from utils.document_processing import estimate_tokens
import streamlit as st
import json
import openai
import httpx
import ssl
import os

def init_open_ai_client():
    api_key = os.getenv('OPENAI_KEY')
    ssl._create_default_https_context = ssl._create_unverified_context
    http_client = httpx.Client(verify=False)
    openai_client = openai.OpenAI(
        api_key=api_key,
        http_client=http_client
    )
    return openai_client

def generate_questions(uploaded_documents):
    openai_client = st.session_state.get('openai_client')
    try:
        summarized_content = ""
        for doc in uploaded_documents.values():
            doc_content = doc['content']
            if 'earnings' in doc['name'].lower():
                sections = doc_content.split('\n\n')
                relevant_sections = []
                for section in sections:
                    if any(keyword in section.lower() for keyword in
                           ['revenue', 'margin', 'guidance', 'strategic', 'operational',
                            'million', 'billion', 'growth', 'client', 'customer']):
                        relevant_sections.append(section)

                doc_summary = '\n'.join(relevant_sections[:10])
                summarized_content += f"\nFrom {doc['name']}:\n{doc_summary}\n"

        if estimate_tokens(summarized_content) > 12000:
            summarized_content = summarized_content[:48000]

        prompt = f"""Based on these earnings call excerpts, generate a comprehensive set of questions.
        Format the response as a JSON object with categories as keys and lists of specific questions as values."""

        response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert financial analyst who understands earnings calls."},
                {"role": "user", "content": prompt + "\n\nReference Content:" + summarized_content}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")
        return {}


def analyze_analyst_questions(uploaded_documents):
    try:
        analyst_questions = {}

        for doc in uploaded_documents.values():
            content = doc['content']
            lines = content.split('\n')

            # Extract fiscal quarter and year info
            fiscal_period = {
                'quarter': None,
                'year': None
            }

            # Try to extract from filename first
            filename = doc['name'].lower()
            if 'q1' in filename or 'q2' in filename or 'q3' in filename or 'q4' in filename:
                for q in ['q1', 'q2', 'q3', 'q4']:
                    if q in filename:
                        fiscal_period['quarter'] = q.upper()
                        break

            # Try to extract year from filename
            import re
            year_match = re.search(r'20\d{2}', filename)
            if year_match:
                fiscal_period['year'] = year_match.group(0)

            # If not found in filename, try content
            if not fiscal_period['quarter'] or not fiscal_period['year']:
                for line in lines[:20]:  # Check first 20 lines
                    if 'fiscal year' in line.lower() or 'fiscal 20' in line.lower():
                        year_match = re.search(r'20\d{2}', line)
                        if year_match:
                            fiscal_period['year'] = year_match.group(0)

                    quarter_map = {
                        'first quarter': 'Q1',
                        'second quarter': 'Q2',
                        'third quarter': 'Q3',
                        'fourth quarter': 'Q4'
                    }
                    for quarter_text, quarter_val in quarter_map.items():
                        if quarter_text in line.lower():
                            fiscal_period['quarter'] = quarter_val
                            break

            fiscal_period_str = f"{fiscal_period['quarter']} FY{fiscal_period['year']}" if fiscal_period['quarter'] and \
                                                                                           fiscal_period[
                                                                                               'year'] else "Quarter Unknown"

            # Find analysts listed at the top of the document
            analyst_mapping = {}
            for line in lines[:20]:
                if 'analyst' in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        name = ' '.join(parts[:-1])
                        analyst_mapping[name.lower()] = {'name': name, 'firm': ''}

            # Process Q&A section
            current_analyst = None
            collecting_question = False
            current_question = []

            for i, line in enumerate(lines):
                if not line.strip():
                    continue

                if any(a.lower() in line.lower() for a in analyst_mapping.keys()):
                    for analyst in analyst_mapping.keys():
                        if analyst.lower() in line.lower():
                            current_analyst = analyst_mapping[analyst]['name']
                            collecting_question = True
                            current_question = []
                            break

                elif collecting_question:
                    if line.startswith('Matt Baer') or line.startswith('David Aufderhaar') or line.startswith(
                            'Operator'):
                        if current_analyst and current_question:
                            question_text = ' '.join(current_question).strip()
                            if current_analyst not in analyst_questions:
                                analyst_questions[current_analyst] = {
                                    'firm': analyst_mapping.get(current_analyst.lower(), {}).get('firm', ''),
                                    'questions': []
                                }
                            analyst_questions[current_analyst]['questions'].append({
                                'question': question_text,
                                'call_date': doc['upload_time'],
                                'source_doc': doc['name'],
                                'fiscal_period': fiscal_period_str,
                            })
                        collecting_question = False
                        current_question = []
                    else:
                        current_question.append(line.strip())

        return analyst_questions

    except Exception as e:
        st.error(f"Error analyzing analyst questions: {str(e)}")
        return {}


def generate_earnings_template(uploaded_documents, company_name, quarter, fiscal_year, context_info=""):
    openai_client = st.session_state.openai_client
    quarter_options = st.session_state.quarter_options
    try:
        recent_calls = []
        other_docs = []
        for doc in uploaded_documents.values():
            if 'earnings' in doc['name'].lower():
                recent_calls.append(doc)
            else:
                other_docs.append(doc)
        recent_calls.sort(key=lambda x: x['upload_time'], reverse=True)

        document_excerpts = []
        if recent_calls:
            main_doc = recent_calls[0]
            document_excerpts.append(
                f"\nMost Recent Earnings Call: {main_doc['name']}\nContent: {main_doc['content'][:10000]}")

            for doc in recent_calls[1:2]:
                document_excerpts.append(f"\nPrior Earnings Call: {doc['name']}\nKey Excerpts: {doc['content'][:5000]}")

        # Simple system prompt without f-string
        system_prompt = f"""You are a financial analyst expert creating a detailed earnings call template.
{context_info}

Please incorporate the provided context into the template, particularly:
- Adjust the overall tone to match the specified tone
- Emphasize the strategic initiatives in the CEO sections
- Include the additional considerations throughout the script where relevant
"""

        # Create the detailed prompt
        detailed_prompt = (
            f"Create an extremely detailed, production-ready earnings call template for {company_name}'s "
            f"{quarter_options[quarter]} Fiscal Year {fiscal_year}. The template must match this exact "
            "level of detail and structure:\n\n"

            "OPERATOR INTRODUCTION:\n"
            f"Good afternoon and thank you for standing by. Welcome to {company_name}'s {quarter_options[quarter]} "
            f"Fiscal Year {fiscal_year} Earnings Conference Call. Today's conference is being recorded. "
            "[Operator Instructions for Q&A format]. I would now like to turn the conference over to "
            "[IR Name], Head of Investor Relations. Please go ahead.\n\n"

            "IR INTRODUCTION:\n"
            "Thank you, Operator, and good afternoon everyone. Thank you for joining us today for "
            f"{company_name}'s {quarter_options[quarter]} Fiscal Year {fiscal_year} earnings call. "
            "With me today are [CEO Name], Chief Executive Officer, and [CFO Name], Chief Financial Officer.\n\n"

            f"We have posted complete {quarter} fiscal {fiscal_year} financial results in our earnings "
            "release on the quarterly results section of our website, [company-website].\n\n"

            "Before we begin, I would like to remind you that we will be making forward-looking statements "
            "on this call which involve risks and uncertainties. Actual results could differ materially "
            "from those contemplated by our forward-looking statements. Reported results should not be "
            "considered as an indication of future performance. Please review our filings with the SEC "
            "for a discussion of the factors that could cause our results to differ.\n\n"

            "Also note that the forward-looking statements on this call are based on information available "
            "to us as of today's date. We disclaim any obligation to update any forward-looking statements "
            "except as required by law.\n\n"

            "During this call, we will discuss certain non-GAAP financial measures. Reconciliations to the "
            "most directly comparable GAAP financial measures are provided in the earnings release on our "
            "Investor Relations website. These non-GAAP measures are not intended to be a substitute for "
            "our GAAP results.\n\n"

            "With that, I'll turn the call over to [CEO Name].\n\n"

            "CEO STRATEGIC OVERVIEW:\n"
            "Thanks [IR Name]. Good afternoon everyone.\n\n"

            f"In {quarter} {fiscal_year}, we continued to execute on our transformation strategy and make "
            "progress strengthening our foundation while reimagining the client experience. Our results "
            "demonstrate the positive impact of these efforts:\n\n"

            "Net revenue was $XXX million\n"
            "We ended the quarter with X.X million active clients\n"
            "Revenue per active client was $XXX\n"
            "Adjusted EBITDA was $XX.X million\n\n"

            "Let me highlight several key developments this quarter:\n\n"

            "[Key Strategic Initiative #1 with metrics]\n"
            "[Key Strategic Initiative #2 with metrics]\n"
            "[Key Strategic Initiative #3 with metrics]\n\n"

            "Now I'll turn it over to [CFO Name] to review our financial results and outlook in detail.\n\n"

            "CFO FINANCIAL REVIEW:\n"
            f"Thanks [CEO Name]. I'll now walk through our {quarter} financial results and provide guidance "
            "for [next quarter] and the full year.\n\n"

            "Q2 Performance:\n\n"

            "Revenue:\n"
            "- Q2 net revenue was $XXX million, [up/down] XX% year-over-year\n"
            "- This [exceeded/met/fell below] our guidance range of $XXX to $XXX million\n"
            "- Key components of revenue performance include:\n"
            "  * [Component 1]: Contributing $XXX million, or XX% of revenue\n"
            "  * [Component 2]: Representing $XXX million, or XX% of revenue\n"
            "  * [Component 3]: Adding $XXX million, or XX% of revenue\n\n"

            "The year-over-year revenue [growth/decline] was driven by:\n"
            "- XX% impact from [primary driver]\n"
            "- XX% effect from [secondary driver]\n"
            "- XX% contribution from [tertiary driver]\n\n"

            "Gross Margin:\n"
            "- Q2 gross margin was XX.X%:\n"
            "  * [Up/down] XX basis points year-over-year\n"
            "  * [Up/down] XX basis points quarter-over-quarter\n"
            "- Key drivers include:\n"
            "  * Product margin improvement of XX basis points\n"
            "  * Transportation efficiency gains of XX basis points\n"
            "  * Inventory management benefits of XX basis points\n"
            "- [Detailed explanation of margin drivers and initiatives]\n\n"

            "Operating Expenses:\n"
            "- Total operating expenses were $XXX million, representing XX% of revenue\n"
            "- This compares to $XXX million, or XX% of revenue, in the prior year\n"
            "- Key components include:\n"
            "  * Marketing expenses of $XXX million, or XX% of revenue\n"
            "  * Technology investments of $XXX million, or XX% of revenue\n"
            "  * G&A expenses of $XXX million, or XX% of revenue\n\n"

            "Balance Sheet Metrics:\n"
            "- Ended Q2 with $XXX million in cash and investments\n"
            "- Generated free cash flow of $XX.X million\n"
            "- Inventory position of $XXX million, down XX% year-over-year\n"
            "- Key working capital metrics:\n"
            "  * Days inventory outstanding: XX days\n"
            "  * Days payable outstanding: XX days\n"
            "  * Days sales outstanding: XX days\n\n"

            "GUIDANCE SECTION:\n"
            "For [Next Quarter]:\n"
            "- Revenue in the range of $XXX million to $XXX million, representing:\n"
            "  * Year-over-year [growth/decline] of XX% to XX%\n"
            "  * Sequential [growth/decline] of XX% to XX%\n"
            "- Adjusted EBITDA between $XX.X million and $XX.X million:\n"
            "  * Representing XX% to XX% of revenue\n"
            "  * Compared to $XX.X million in prior year\n\n"

            f"For Full Year FY{fiscal_year}:\n"
            "- Revenue guidance of $X.XX billion to $X.XX billion:\n"
            "  * Representing XX% to XX% [growth/decline] year-over-year\n"
            "  * [Explanation of any changes to prior guidance]\n"
            "- Adjusted EBITDA guidance of $XXX million to $XXX million:\n"
            "  * Implying margins of XX% to XX%\n"
            "  * [Comparison to prior guidance]\n\n"

            "CEO CLOSING REMARKS:\n"
            "Thank you [CFO Name]. Before we open for questions, I want to emphasize several key points:\n\n"

            "First, [Key Achievement 1]:\n"
            "- Specific impact: [quantified result]\n"
            "- Strategic importance: [explanation]\n"
            "- Future opportunity: [outlook]\n\n"

            "Second, [Key Achievement 2]:\n"
            "- Progress made: [specific metric]\n"
            "- Market positioning: [competitive advantage]\n"
            "- Growth potential: [future opportunity]\n\n"

            "Finally, [Key Achievement 3]:\n"
            "- Results demonstrated: [specific outcome]\n"
            "- Strategic alignment: [connection to goals]\n"
            "- Forward momentum: [next steps]\n\n"

            "We remain [confident/optimistic/focused] on our strategy and execution as we continue to "
            "[company's main strategic objective].\n\n"

            "With that, we'll open the line for questions. Operator, please go ahead.\n\n"

            "Q&A TRANSITION:\n"
            "We will now begin the question-and-answer session. [Operator instructions for asking questions]. "
            "Our first question comes from [Analyst Name] with [Firm Name].\n\n"

            "CLOSING:\n"
            f"Thank you everyone for your questions and ongoing interest in {company_name}. We look forward "
            "to updating you on our continued progress next quarter."
        )

        response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": detailed_prompt + "\n\nReference Documents:" + "\n".join(document_excerpts)}
            ],
            temperature=0.7,
            max_tokens=4000
        )

        generated_template = response.choices[0].message.content

        # Clean up any potential formatting issues
        generated_template = generated_template.replace('```', '').strip()

        return generated_template
    except Exception as e:
        st.error(f"Error generating template: {str(e)}")
        return "Error generating template. Please try again."