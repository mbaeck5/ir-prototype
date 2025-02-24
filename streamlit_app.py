import streamlit as st
import pandas as pd
from datetime import datetime
import json
import io
import PyPDF2
from docx import Document
import openai
import httpx
import ssl
import os

API_KEY = os.environ("OPENAI_KEY")

# Initialize page config and styling
st.set_page_config(page_title="Earnings Call Template Generator", layout="wide")

# Add PEAK6 styling
st.markdown("""
    <style>
    .stButton > button {
        color: white;
        background-color: #0365A3;
        border: none;
    }
    .stProgress > div > div > div {
        background-color: #0365A3;
    }
    div[data-baseweb="tab"] > div {
        color: #0365A3;
    }
    div[data-baseweb="tab"][aria-selected="true"] > div {
        color: #0365A3;
        border-bottom-color: #0365A3;
    }
    </style>
""", unsafe_allow_html=True)

# Add PEAK6 logo
st.markdown("""
    <div style="position: fixed; top: 1rem; left: 1rem; z-index: 999; background-color: white; padding: 10px; border-radius: 4px;">
        <img src="https://peak6.com/wp-content/themes/peak6/img/peak6-logo.svg" width="120">
    </div>
    <br><br>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'editable_script' not in st.session_state:
    st.session_state.editable_script = ""
if 'selected_tile' not in st.session_state:
    st.session_state.selected_tile = "Document Upload"
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}
if 'questions' not in st.session_state:
    st.session_state.questions = {}
if 'shareholders_data' not in st.session_state:
    st.session_state.shareholders_data = {}
if 'investor_outreach_data' not in st.session_state:
    st.session_state.investor_outreach_data = {}
if 'investor_targeting_data' not in st.session_state:
    st.session_state.investor_targeting_data = {}
if 'market_updates_data' not in st.session_state:
    st.session_state.market_updates_data = {}
if 'weekly_overview' not in st.session_state:
    st.session_state.weekly_overview = {}
if 'company_highlights' not in st.session_state:
    st.session_state.company_highlights = {}
if 'performance_data' not in st.session_state:
    st.session_state.performance_data = {}
if 'weekly_summaries' not in st.session_state:
    st.session_state.weekly_summaries = {}

# Initialize OpenAI client
ssl._create_default_https_context = ssl._create_unverified_context
http_client = httpx.Client(verify=False)
openai_client = openai.OpenAI(
    api_key=API_KEY,
    # Replace with your actual API key
    http_client=http_client
)


# Utility functions
def estimate_tokens(text):
    return len(text) // 4


def extract_text_from_pdf(file_bytes):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"


def extract_text_from_docx(file_bytes):
    try:
        doc = Document(io.BytesIO(file_bytes))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return f"Error extracting DOCX text: {str(e)}"


def generate_questions(uploaded_documents):
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


# Sidebar configuration
st.sidebar.header("Template Settings")
company_name = st.sidebar.text_input("Company Name:", "Stitch Fix")
quarter_options = {
    "Q1": "First Quarter",
    "Q2": "Second Quarter",
    "Q3": "Third Quarter",
    "Q4": "Fourth Quarter"
}
selected_quarter = st.sidebar.selectbox("Quarter:", list(quarter_options.keys()))
fiscal_year = st.sidebar.text_input("Fiscal Year:", "2025")

# Main navigation
st.title("IR Content Creation and Prep Hub")

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    if st.button("Document Upload", use_container_width=True):
        st.session_state.selected_tile = "Document Upload"

with col2:
    if st.button("Earnings Call Script", use_container_width=True):
        st.session_state.selected_tile = "Earnings Call Script"

with col3:
    if st.button("Q&A Prep", use_container_width=True):
        st.session_state.selected_tile = "Q&A Prep"

with col4:
    if st.button("Shareholders", use_container_width=True):
        st.session_state.selected_tile = "Shareholders"

with col5:
    if st.button("Investor Outreach", use_container_width=True):
        st.session_state.selected_tile = "Investor Outreach"

with col6:
    if st.button("Investor Targeting", use_container_width=True):
        st.session_state.selected_tile = "Investor Targeting"

with col7:
    if st.button("Market Updates", use_container_width=True):
        st.session_state.selected_tile = "Market Updates"

st.markdown("---")

# Document Upload Section
if st.session_state.selected_tile == "Document Upload":
    st.header(f"Document Upload and Analysis - {company_name} {selected_quarter} FY{fiscal_year}")

    uploaded_files = st.file_uploader(
        "Upload earnings calls, competitor analysis, or other relevant documents",
        accept_multiple_files=True,
        type=['pdf', 'docx', 'txt']
    )

    if uploaded_files:
        for file in uploaded_files:
            file_key = f"{file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            if file_key not in st.session_state.uploaded_files:
                file_bytes = file.read()
                file_type = file.name.split('.')[-1].lower()

                if file_type == 'pdf':
                    text_content = extract_text_from_pdf(file_bytes)
                elif file_type == 'docx':
                    text_content = extract_text_from_docx(file_bytes)
                elif file_type == 'txt':
                    text_content = file_bytes.decode('utf-8')
                else:
                    text_content = "Unsupported file type"

                st.session_state.uploaded_files[file_key] = {
                    'name': file.name,
                    'content': text_content,
                    'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                st.success(f"Successfully uploaded: {file.name}")

    # Display uploaded documents
    if st.session_state.uploaded_files:
        st.subheader("Uploaded Documents")
        for file_key, file_data in st.session_state.uploaded_files.items():
            st.write(f"📄 {file_data['name']} - Uploaded at {file_data['upload_time']}")
            if st.button(f"View Content", key=f"view_{file_key}"):
                st.text_area("Document Content", file_data['content'], height=300)

# Earnings Call Script Section
elif st.session_state.selected_tile == "Earnings Call Script":
    st.header(f"Earnings Call Script - {company_name} {selected_quarter} FY{fiscal_year}")

    # Create tabs within the Earnings Call Script section
    tab0, tab1, tab2, tab3 = st.tabs(["Script Context", "Template Generation", "Q&A Input", "Live Transcript"])

    # Script Context Tab
    with tab0:
        st.subheader("Script Context")
        st.write(
            "Please add specific details and commentary on the quarter that you would like considered in this quarters script")

        # Initialize session state for context if not exists
        if 'script_context' not in st.session_state:
            st.session_state.script_context = {
                'tone': '',
                'initiatives': '',
                'considerations': ''
            }

        # Tone Section
        st.markdown("### Tone")
        st.session_state.script_context['tone'] = st.text_area(
            "What tone should the script convey? (e.g., optimistic, cautious, focused on execution, etc.)",
            value=st.session_state.script_context.get('tone', ''),
            height=100,
            key="tone_input"
        )

        # Strategic Initiatives Section
        st.markdown("### Strategic Initiatives to Highlight")
        st.session_state.script_context['initiatives'] = st.text_area(
            "What key strategic initiatives or accomplishments should be emphasized?",
            value=st.session_state.script_context.get('initiatives', ''),
            height=150,
            key="initiatives_input"
        )

        # Additional Considerations Section
        st.markdown("### Additional Considerations")
        st.session_state.script_context['considerations'] = st.text_area(
            "Any other specific points, metrics, or context to include?",
            value=st.session_state.script_context.get('considerations', ''),
            height=150,
            key="considerations_input"
        )

        if st.button("Save Context"):
            st.success("Context saved successfully! You can now proceed to Template Generation.")

    # Template Generation Tab
    with tab1:
        st.subheader("Generate Template")
        if st.session_state.uploaded_files:
            if st.button("Generate Earnings Call Template", key="generate_template"):
                with st.spinner(f"Analyzing documents and generating template for {company_name}..."):
                    # Include script context in the template generation
                    context_info = ""
                    if hasattr(st.session_state, 'script_context'):
                        context_info = f"""
                        Script Context:
                        Tone: {st.session_state.script_context.get('tone', '')}
                        Strategic Initiatives: {st.session_state.script_context.get('initiatives', '')}
                        Additional Considerations: {st.session_state.script_context.get('considerations', '')}
                        """

                    generated_template = generate_earnings_template(
                        uploaded_documents=st.session_state.uploaded_files,
                        company_name=company_name,
                        quarter=selected_quarter,
                        fiscal_year=fiscal_year,
                        context_info=context_info
                    )
                    st.session_state.editable_script = generated_template
                    st.success("Template generated successfully!")

            st.markdown("---")

            st.subheader("Edit Template")
            edited_script = st.text_area(
                "Edit Script Template:",
                value=st.session_state.editable_script if st.session_state.editable_script else "Generate a template or start editing here...",
                height=600,
                key="script_editor"
            )

            if st.button("Save Changes"):
                st.session_state.editable_script = edited_script
                st.success("Changes saved!")
        else:
            st.warning("Please upload documents in the Document Upload tab first")

    # Q&A Input Tab
    with tab2:
        st.subheader("Q&A Management")
        if st.session_state.uploaded_files:
            if st.button("Generate Questions"):
                with st.spinner("Analyzing documents and generating questions..."):
                    generated_questions = generate_questions(st.session_state.uploaded_files)
                    st.session_state.questions = generated_questions
                    st.success("Questions generated successfully!")

                    # Display questions and answers if available
                    if generated_questions:
                        for category, questions in generated_questions.items():
                            st.write(f"**{category}**")
                            for question in questions:
                                st.write(f"- {question}")
        else:
            st.warning("Please upload documents in the Document Upload tab first")

    # Live Transcript Tab
    with tab3:
        st.subheader("Live Transcript")
        if st.session_state.editable_script:
            st.markdown(st.session_state.editable_script)
            if st.button("Export Transcript"):
                st.download_button(
                    label="Download Transcript",
                    data=st.session_state.editable_script,
                    file_name=f"{company_name}_{selected_quarter}_FY{fiscal_year}_transcript_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )
        else:
            st.info("Generate a template first to view the live transcript")

# Q&A Prep section
elif st.session_state.selected_tile == "Q&A Prep":
    st.header(f"Q&A Preparation - {company_name} {selected_quarter} FY{fiscal_year}")

    # Create tabs for different Q&A prep views
    qa_tab1, qa_tab2, qa_tab3 = st.tabs(["Analysts", "Buy-Side", "Full Q&A Prep"])

    # Analysts Tab
    # Inside your Q&A Prep section, update the Analysts tab:
    with qa_tab1:
        st.subheader("Covering Analysts & Historical Questions")

        if st.session_state.uploaded_files:
            col1, col2 = st.columns([2, 1])

            with col1:
                if st.button("Analyze Historical Questions"):
                    with st.spinner("Analyzing previous earnings calls for analyst questions..."):
                        analyst_questions = analyze_analyst_questions(st.session_state.uploaded_files)
                        st.session_state.analyst_questions = analyst_questions

                        if analyst_questions:
                            st.success(f"Found {len(analyst_questions)} analysts with historical questions")
                        else:
                            st.warning(
                                "No analyst questions found. Please ensure the uploaded documents include earnings call transcripts with Q&A sections.")

            with col2:
                st.info(f"📊 Analyzing transcripts for analyst participation and question patterns")

            # Display analyst questions if available
            # Inside your Q&A Prep section, in the Analysts tab:
            if hasattr(st.session_state, 'analyst_questions') and st.session_state.analyst_questions:
                for analyst, data in st.session_state.analyst_questions.items():
                    with st.expander(f"📝 {analyst} ({data['firm']}) - {len(data['questions'])} questions"):
                        # Group questions by fiscal period
                        questions_by_period = {}
                        for q in data['questions']:
                            period = q['fiscal_period']
                            if period not in questions_by_period:
                                questions_by_period[period] = []
                            questions_by_period[period].append(q)

                        # Display questions grouped by fiscal period
                        for period, questions in sorted(questions_by_period.items(), reverse=True):
                            st.markdown(f"**{period}**")
                            for q in questions:
                                st.markdown(f"""
                                🔹 **Question:**  
                                {q['question']}
                                """)
                            st.markdown("---")

                # Add summary statistics
                total_questions = sum(len(data['questions']) for data in st.session_state.analyst_questions.values())
                st.sidebar.markdown("### Analysis Summary")
                st.sidebar.markdown(f"- Total Analysts: {len(st.session_state.analyst_questions)}")
                st.sidebar.markdown(f"- Total Questions: {total_questions}")
                st.sidebar.markdown(
                    f"- Avg Questions/Analyst: {total_questions / len(st.session_state.analyst_questions):.1f}")
        else:
            st.warning("Please upload earnings call transcripts in the Document Upload tab first")

    # Buy-Side Tab
    with qa_tab2:
        st.subheader("Buy-Side Question Preparation")
        st.info("This section will help prepare for potential buy-side questions. Feature coming soon.")

        # Placeholder for future buy-side functionality
        st.markdown("""
        Future features will include:
        - Common buy-side focus areas
        - Institutional holder analysis
        - Investment thesis tracking
        - Recent investor feedback
        """)

    # Full Q&A Prep Tab
    with qa_tab3:
        st.subheader("Comprehensive Q&A Preparation")
        st.info(
            "This section will combine sell-side and buy-side preparation into a complete Q&A guide. Feature coming soon.")

        # Placeholder for future comprehensive Q&A prep
        st.markdown("""
        Future features will include:
        - Question categorization
        - Topic prediction
        - Answer templates
        - Risk area identification
        - Preparation checklist
        """)
# Shareholders section
elif st.session_state.selected_tile == "Shareholders":
    st.header(f"Shareholders - {company_name}")

    # Create tabs for Shareholders section
    sh_tab1, sh_tab2, sh_tab3 = st.tabs(["Ownership Analysis", "Voting Rights", "Shareholder Communications"])

    with sh_tab1:
        st.subheader("Ownership Analysis")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Institutional Ownership", "72.3%", "1.2%")
            st.metric("Insider Ownership", "5.8%", "-0.3%")

        with col2:
            st.metric("Active Shareholders", "487", "15")
            st.metric("New Institutional Buyers", "24", "8")

    with sh_tab2:
        st.subheader("Voting Rights Management")
        st.info("Track and manage shareholder voting rights and proxy matters")

    with sh_tab3:
        st.subheader("Shareholder Communications")
        st.info("Manage and track shareholder communications and engagement")

# Investor Outreach section
elif st.session_state.selected_tile == "Investor Outreach":
    st.header(f"Investor Outreach - {company_name}")

    # Create tabs for Investor Outreach section
    io_tab1, io_tab2, io_tab3 = st.tabs(["Meeting Tracker", "Conference Calendar", "Feedback Management"])

    with io_tab1:
        st.subheader("Meeting Tracker")
        st.info("Track and manage investor meetings and engagements")

        # Add meeting input form
        with st.expander("Add New Meeting"):
            col1, col2 = st.columns(2)
            with col1:
                st.date_input("Meeting Date")
                st.text_input("Investor Name")
                st.text_input("Contact Person")
            with col2:
                st.selectbox("Meeting Type", ["One-on-One", "Group Meeting", "Conference", "Site Visit"])
                st.text_area("Meeting Notes")

    with io_tab2:
        st.subheader("Conference Calendar")
        st.info("Manage upcoming conference participation and scheduling")

    with io_tab3:
        st.subheader("Feedback Management")
        st.info("Track and analyze investor feedback and sentiment")

# Investor Targeting section
elif st.session_state.selected_tile == "Investor Targeting":
    st.header(f"Investor Targeting - {company_name}")

    # Create tabs for Investor Targeting section
    it_tab1, it_tab2, it_tab3 = st.tabs(["Target List", "Peer Analysis", "Investment Style"])

    with it_tab1:
        st.subheader("Target Investor List")
        st.info("Identify and track potential investors based on investment criteria")

        # Add targeting criteria
        with st.expander("Targeting Criteria"):
            col1, col2 = st.columns(2)
            with col1:
                st.slider("AUM Range ($B)", 0.0, 100.0, (1.0, 50.0))
                st.multiselect("Investment Style", ["Growth", "Value", "GARP", "Index", "Hedge Fund"])
            with col2:
                st.multiselect("Geographic Focus", ["North America", "Europe", "Asia", "Global"])
                st.multiselect("Sector Focus", ["Technology", "Consumer", "Industrial", "Healthcare"])

    with it_tab2:
        st.subheader("Peer Analysis")
        st.info("Analyze peer company ownership and targeting opportunities")

    with it_tab3:
        st.subheader("Investment Style Analysis")
        st.info("Analyze investment styles and preferences of potential investors")

# Market Updates section
elif st.session_state.selected_tile == "Market Updates":
    st.header(f"Market Updates - {company_name}")

    # Create tabs for Market Updates section - adding Peers as first tab
    mu_tab0, mu_tab1, mu_tab2, mu_tab3 = st.tabs(["Peers", "Market News", "Peer Updates", "Industry Analysis"])

    # Peers Tab
    with mu_tab0:
        st.subheader("Peer Analysis")

        # Add peer generation controls
        with st.expander("Peer Selection Criteria", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                market_cap_range = st.slider(
                    "Market Cap Range ($B)",
                    min_value=0.0,
                    max_value=100.0,
                    value=(1.0, 50.0),
                    key="peer_market_cap"
                )
                industry_options = ["Technology", "Consumer Discretionary", "Retail", "E-commerce", "Fashion"]
                selected_industries = st.multiselect(
                    "Industry Focus",
                    industry_options,
                    default=["Retail", "E-commerce"],
                    key="peer_industries"
                )

            with col2:
                min_shared_analysts = st.slider(
                    "Minimum Shared Analysts",
                    min_value=0,
                    max_value=20,
                    value=3,
                    key="min_analysts"
                )
                min_shared_investors = st.slider(
                    "Minimum Shared Investors",
                    min_value=0,
                    max_value=50,
                    value=5,
                    key="min_investors"
                )

        # Button to generate peers
        if st.button("Generate Peer Set", key="generate_peers"):
            with st.spinner("Analyzing peer companies..."):
                prompt = f"""Based on the following criteria, generate a detailed analysis of 5-7 public company peers for {company_name}:
                - Market Cap Range: ${market_cap_range[0]}B to ${market_cap_range[1]}B
                - Industries: {', '.join(selected_industries)}
                - Minimum shared analysts: {min_shared_analysts}
                - Minimum shared investors: {min_shared_investors}

                Return the analysis in this exact JSON format:
                {{
                    "peers": [
                        {{
                            "name": "Company Name",
                            "ticker": "TICK",
                            "market_cap": "$XXB",
                            "industry": "Primary Industry",
                            "shared_analysts": X,
                            "shared_investors": X,
                            "business_model_similarities": "Description...",
                            "competitive_positioning": "Analysis..."
                        }}
                    ]
                }}"""

                try:
                    response = openai_client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[
                            {"role": "system",
                             "content": "You are a financial analyst expert. Always return data in the exact JSON format specified."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        response_format={"type": "json_object"}
                    )

                    peers_data = json.loads(response.choices[0].message.content)

                    if 'peers' not in peers_data:
                        st.error("Invalid response format from AI. Please try again.")
                    else:
                        st.session_state.peers_data = peers_data

                        # Display peer analysis results
                        st.subheader("Generated Peer Set")

                        # Create metrics summary
                        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                        with metrics_col1:
                            st.metric("Total Peers", len(peers_data['peers']))
                        with metrics_col2:
                            avg_market_cap = sum(float(peer['market_cap'].replace('$', '').replace('B', ''))
                                                 for peer in peers_data['peers']) / len(peers_data['peers'])
                            st.metric("Average Peer Market Cap", f"${avg_market_cap:.1f}B")
                        with metrics_col3:
                            total_shared_investors = sum(peer['shared_investors'] for peer in peers_data['peers'])
                            st.metric("Total Shared Investors", total_shared_investors)

                        # Display detailed peer information
                        for peer in peers_data['peers']:
                            with st.expander(f"{peer['name']} ({peer['ticker']})"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Market Cap:** {peer['market_cap']}")
                                    st.markdown(f"**Industry:** {peer['industry']}")
                                    st.markdown(f"**Shared Analysts:** {peer['shared_analysts']}")
                                with col2:
                                    st.markdown(f"**Shared Investors:** {peer['shared_investors']}")
                                    st.markdown("**Business Model Similarities:**")
                                    st.markdown(peer['business_model_similarities'])

                                st.markdown("**Competitive Positioning:**")
                                st.markdown(peer['competitive_positioning'])

                except Exception as e:
                    st.error(f"Error generating peer analysis: {str(e)}")
                    st.error("Raw response: " + str(response.choices[0].message.content))

        # Show previously generated peers if they exist
        elif 'peers_data' in st.session_state and 'peers' in st.session_state.peers_data:
            st.subheader("Current Peer Set")

            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            with metrics_col1:
                st.metric("Total Peers", len(st.session_state.peers_data['peers']))
            with metrics_col2:
                avg_market_cap = sum(float(peer['market_cap'].replace('$', '').replace('B', ''))
                                     for peer in st.session_state.peers_data['peers']) / len(
                    st.session_state.peers_data['peers'])
                st.metric("Average Peer Market Cap", f"${avg_market_cap:.1f}B")
            with metrics_col3:
                total_shared_investors = sum(peer['shared_investors'] for peer in st.session_state.peers_data['peers'])
                st.metric("Total Shared Investors", total_shared_investors)

            for peer in st.session_state.peers_data['peers']:
                with st.expander(f"{peer['name']} ({peer['ticker']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Market Cap:** {peer['market_cap']}")
                        st.markdown(f"**Industry:** {peer['industry']}")
                        st.markdown(f"**Shared Analysts:** {peer['shared_analysts']}")
                    with col2:
                        st.markdown(f"**Shared Investors:** {peer['shared_investors']}")
                        st.markdown("**Business Model Similarities:**")
                        st.markdown(peer['business_model_similarities'])

                    st.markdown("**Competitive Positioning:**")
                    st.markdown(peer['competitive_positioning'])

    # Market News Tab
    with mu_tab1:
        st.subheader("Market News")

        # Create tabs for different news categories
        news_tab1, news_tab2, news_tab3, news_tab4 = st.tabs(
            ["Executive Summary", "Company News", "Peer News", "Industry News"])

        # Executive Summary tab
        with news_tab1:
            st.subheader("Executive Summary")

            # Add date selector and generate button
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_date = st.date_input(
                    "Select Week",
                    datetime.now().date(),
                    key="summary_date"
                )
            with col2:
                if st.button("Generate New Summary"):
                    try:
                        # Generate a comprehensive weekly summary using GPT-4
                        summary_prompt = f"""Create a comprehensive weekly market summary for {company_name} for the week ending {selected_date}.
                        Include:
                        1. Key company events and announcements
                        2. Notable peer activities and their implications
                        3. Major industry developments
                        4. Stock performance analysis (company and peers)

                        Format the response as JSON:
                        {{
                            "date": "YYYY-MM-DD",
                            "company_events": ["event1", "event2"],
                            "peer_events": ["event1", "event2"],
                            "industry_events": ["event1", "event2"],
                            "performance_data": {{
                                "company": {{"1w": -2.3, "6m": 15.4, "52w": 28.7}},
                                "peer_avg": {{"1w": -1.8, "6m": 12.1, "52w": 22.3}}
                            }}
                        }}"""

                        response = openai_client.chat.completions.create(
                            model="gpt-4-turbo-preview",
                            messages=[
                                {"role": "system",
                                 "content": "You are an IR professional creating executive summaries."},
                                {"role": "user", "content": summary_prompt}
                            ],
                            temperature=0.7,
                            response_format={"type": "json_object"}
                        )

                        new_summary = json.loads(response.choices[0].message.content)
                        if 'weekly_summaries' not in st.session_state:
                            st.session_state.weekly_summaries = {}
                        st.session_state.weekly_summaries[selected_date.strftime('%Y-%m-%d')] = new_summary
                        st.success("New summary generated!")
                    except Exception as e:
                        st.error(f"Error generating weekly summary: {str(e)}")

            # Display the summary if available
            selected_summary_date = selected_date.strftime('%Y-%m-%d')
            if 'weekly_summaries' in st.session_state and selected_summary_date in st.session_state.weekly_summaries:
                summary = st.session_state.weekly_summaries[selected_summary_date]

                # Create three columns for performance metrics
                met_col1, met_col2, met_col3 = st.columns(3)

                with met_col1:
                    st.metric(
                        label="1-Week Performance",
                        value=f"{summary['performance_data']['company']['1w']}%",
                        delta=f"{summary['performance_data']['company']['1w'] - summary['performance_data']['peer_avg']['1w']:.1f}% vs peers"
                    )

                with met_col2:
                    st.metric(
                        label="6-Month Performance",
                        value=f"{summary['performance_data']['company']['6m']}%",
                        delta=f"{summary['performance_data']['company']['6m'] - summary['performance_data']['peer_avg']['6m']:.1f}% vs peers"
                    )

                with met_col3:
                    st.metric(
                        label="52-Week Performance",
                        value=f"{summary['performance_data']['company']['52w']}%",
                        delta=f"{summary['performance_data']['company']['52w'] - summary['performance_data']['peer_avg']['52w']:.1f}% vs peers"
                    )

                # Display events in expandable sections
                with st.expander("Company Events", expanded=True):
                    for event in summary['company_events']:
                        st.markdown(f"• {event}")

                with st.expander("Peer Activities", expanded=True):
                    for event in summary['peer_events']:
                        st.markdown(f"• {event}")

                with st.expander("Industry Developments", expanded=True):
                    for event in summary['industry_events']:
                        st.markdown(f"• {event}")

                # Export options
                st.subheader("Export Options")
                exp_col1, exp_col2 = st.columns(2)

                with exp_col1:
                    if st.button("📧 Export as Email"):
                        company_events = "\n".join(['• ' + event for event in summary['company_events']])
                        peer_events = "\n".join(['• ' + event for event in summary['peer_events']])
                        industry_events = "\n".join(['• ' + event for event in summary['industry_events']])

                        email_text = f"""Weekly Market Summary for {company_name}
                            Week Ending: {selected_date}
        
                            COMPANY EVENTS:
                            {company_events}
        
                            PEER ACTIVITIES:
                            {peer_events}
        
                            INDUSTRY DEVELOPMENTS:
                            {industry_events}
        
                            PERFORMANCE METRICS:
                            • 1-Week: {summary['performance_data']['company']['1w']}% (Peer avg: {summary['performance_data']['peer_avg']['1w']}%)
                            • 6-Month: {summary['performance_data']['company']['6m']}% (Peer avg: {summary['performance_data']['peer_avg']['6m']}%)
                            • 52-Week: {summary['performance_data']['company']['52w']}% (Peer avg: {summary['performance_data']['peer_avg']['52w']}%)"""

                        st.code(email_text, language="text")
                        st.info("Email text copied to clipboard!")

                with exp_col2:
                    if st.button("📥 Download Summary"):
                        # Create download link
                        company_events = "\n".join(['- ' + event for event in summary['company_events']])
                        peer_events = "\n".join(['- ' + event for event in summary['peer_events']])
                        industry_events = "\n".join(['- ' + event for event in summary['industry_events']])

                        download_str = f"""# Weekly Market Summary - {company_name}
                        Week Ending: {selected_date}

                        ## Performance Metrics
                        - 1-Week: {summary['performance_data']['company']['1w']}% (vs peer avg: {summary['performance_data']['peer_avg']['1w']}%)
                        - 6-Month: {summary['performance_data']['company']['6m']}% (vs peer avg: {summary['performance_data']['peer_avg']['6m']}%)
                        - 52-Week: {summary['performance_data']['company']['52w']}% (vs peer avg: {summary['performance_data']['peer_avg']['52w']}%)

                        ## Company Events
                        {company_events}

                        ## Peer Activities
                        {peer_events}

                        ## Industry Developments
                        {industry_events}"""
                        st.download_button(
                            label="Download as Text",
                            data=download_str,
                            file_name=f"market_summary_{selected_date}.txt",
                            mime="text/plain"
                        )
            else:
                st.info("No summary available for selected week. Click 'Generate New Summary' to create one.")

        # Company News tab
        with news_tab2:
            st.subheader(f"{company_name} News")

            # Generate company-specific news using AI
            try:
                company_prompt = f"""Generate 5 recent, realistic market news items for {company_name}. 
                Include varied news types (earnings, operations, strategy, market performance, analyst coverage).
                Format exactly as JSON:
                {{
                    "news_items": [
                        {{
                            "headline": "Title of the news item",
                            "date": "YYYY-MM-DD",
                            "summary": "2-3 sentence summary of the news",
                            "source": "Name of news source",
                            "link": "https://example.com/news",
                            "category": "News category (e.g., Earnings, Strategy, etc.)"
                        }}
                    ]
                }}"""

                response = openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are a financial news analyst providing market updates."},
                        {"role": "user", "content": company_prompt}
                    ],
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )

                company_news = json.loads(response.choices[0].message.content)

                # Display company news
                for news in company_news['news_items']:
                    with st.container():
                        st.markdown(f"### {news['headline']}")
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"*{news['date']}* - {news['source']}")
                            st.markdown(news['summary'])
                        with col2:
                            st.markdown(f"**Category:** {news['category']}")
                            st.markdown(f"[Read More]({news['link']})")
                        st.markdown("---")

            except Exception as e:
                st.error(f"Error generating company news: {str(e)}")

        # Peer News tab
        with news_tab3:
            st.subheader("Peer Company News")

            # Check if peers have been generated
            if 'peers_data' in st.session_state and 'peers' in st.session_state.peers_data:
                peers = st.session_state.peers_data['peers']

                # Create a multiselect to filter which peers to show news for
                selected_peers = st.multiselect(
                    "Select peers to show news for:",
                    options=[f"{peer['name']} ({peer['ticker']})" for peer in peers],
                    default=[f"{peer['name']} ({peer['ticker']})" for peer in peers[:3]]
                )

                if selected_peers:
                    try:
                        peers_prompt = f"""Generate 2 recent, realistic market news items for each of these companies: {', '.join(selected_peers)}.
                        Format exactly as JSON:
                        {{
                            "news_items": [
                                {{
                                    "company": "Company Name (TICK)",
                                    "headline": "Title",
                                    "date": "YYYY-MM-DD",
                                    "summary": "2-3 sentence summary",
                                    "source": "Source Name",
                                    "link": "https://example.com"
                                }}
                            ]
                        }}"""

                        response = openai_client.chat.completions.create(
                            model="gpt-4-turbo-preview",
                            messages=[
                                {"role": "system",
                                 "content": "You are a financial news analyst providing market updates."},
                                {"role": "user", "content": peers_prompt}
                            ],
                            temperature=0.7,
                            response_format={"type": "json_object"}
                        )

                        peer_news = json.loads(response.choices[0].message.content)

                        for news in peer_news['news_items']:
                            with st.container():
                                st.markdown(f"## {news['company']}")
                                st.markdown(f"### {news['headline']}")
                                st.markdown(f"*{news['date']}* - {news['source']}")
                                st.markdown(news['summary'])
                                st.markdown(f"[Read More]({news['link']})")
                                st.markdown("---")

                    except Exception as e:
                        st.error(f"Error generating peer news: {str(e)}")
            else:
                st.info("Please generate peer companies in the Peers tab first.")

        # Industry News tab
        with news_tab4:
            st.subheader("Industry News")

            # Get industries either from peer selection or default set
            if 'peer_industries' in st.session_state:
                industries = st.session_state.peer_industries
            else:
                industries = ["Retail", "E-commerce"]  # Default industries

            try:
                industry_prompt = f"""Generate 3 recent, realistic market news items for these industries: {', '.join(industries)}.
                Include major trends, market shifts, and regulatory updates.
                Format exactly as JSON:
                {{
                    "news_items": [
                        {{
                            "industry": "Industry Name",
                            "headline": "Title",
                            "date": "YYYY-MM-DD",
                            "summary": "2-3 sentence summary",
                            "source": "Source Name",
                            "link": "https://example.com",
                            "impact": "Brief description of industry impact"
                        }}
                    ]
                }}"""

                response = openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are a financial news analyst providing market updates."},
                        {"role": "user", "content": industry_prompt}
                    ],
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )

                industry_news = json.loads(response.choices[0].message.content)

                # Group news by industry
                news_by_industry = {}
                for news in industry_news['news_items']:
                    if news['industry'] not in news_by_industry:
                        news_by_industry[news['industry']] = []
                    news_by_industry[news['industry']].append(news)

                # Display news grouped by industry
                for industry, news_items in news_by_industry.items():
                    st.markdown(f"## {industry}")
                    for news in news_items:
                        with st.container():
                            st.markdown(f"### {news['headline']}")
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"*{news['date']}* - {news['source']}")
                                st.markdown(news['summary'])
                            with col2:
                                st.markdown("**Industry Impact:**")
                                st.markdown(news['impact'])
                            st.markdown(f"[Read More]({news['link']})")
                            st.markdown("---")

            except Exception as e:
                st.error(f"Error generating industry news: {str(e)}")