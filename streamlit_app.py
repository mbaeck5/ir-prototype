import streamlit as st
from datetime import datetime
import json
import io
import PyPDF2
from docx import Document
import openai
import httpx
import ssl
import os

API_KEY = os.getenv("OPENAI_KEY")
# PEAK6 styling
st.set_page_config(page_title="Earnings Call Template Generator", layout="wide")

# Add styling
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

# Initialize session state
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'editable_script' not in st.session_state:
    st.session_state.editable_script = ""
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}

# Disable SSL verification for OpenAI calls
ssl._create_default_https_context = ssl._create_unverified_context

# Initialize OpenAI client
http_client = httpx.Client(verify=False)
openai_client = openai.OpenAI(
    api_key=API_KEY,
    http_client=http_client
)

# Define variables at the top level so they're accessible everywhere
if 'company_name' not in st.session_state:
    st.session_state.company_name = "Stitch Fix"
if 'selected_quarter' not in st.session_state:
    st.session_state.selected_quarter = "Q1"
if 'fiscal_year' not in st.session_state:
    st.session_state.fiscal_year = "2025"

# Add sidebar navigation
selected_view = st.sidebar.radio("Select View", ["Template Settings", "Transcript and Q&A"])

# Debug display - you can remove these later
st.sidebar.write("Current Settings:")
st.sidebar.write(f"Company: {st.session_state.company_name}")
st.sidebar.write(f"Quarter: {st.session_state.selected_quarter}")
st.sidebar.write(f"Year: {st.session_state.fiscal_year}")

quarter_options = {
    "Q1": "First Quarter",
    "Q2": "Second Quarter",
    "Q3": "Third Quarter",
    "Q4": "Fourth Quarter"
}

# Show Template Settings view
if selected_view == "Template Settings":
    st.title("Template Settings")

    # Template Settings form
    with st.form("template_settings"):
        company_name = st.text_input("Company Name:", value=st.session_state.company_name)
        selected_quarter = st.selectbox("Quarter:", list(quarter_options.keys()),
                                        index=list(quarter_options.keys()).index(st.session_state.selected_quarter))
        fiscal_year = st.text_input("Fiscal Year:", value=st.session_state.fiscal_year)

        if st.form_submit_button("Save Settings"):
            st.session_state.company_name = company_name
            st.session_state.selected_quarter = selected_quarter
            st.session_state.fiscal_year = fiscal_year
            st.success("Settings saved!")

# Only show the main content when "Transcript and Q&A" is selected
if selected_view == "Transcript and Q&A":

    def estimate_tokens(text):
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4


    def generate_earnings_template(uploaded_documents, company_name, quarter, fiscal_year):
        try:
            # Process documents as before
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
                    document_excerpts.append(
                        f"\nPrior Earnings Call: {doc['name']}\nKey Excerpts: {doc['content'][:5000]}")

            detailed_prompt = f"""
            Create an extremely detailed, production-ready earnings call template for {st.session_state.company_name}'s {quarter_options[quarter]} Fiscal Year {st.session_state.fiscal_year}. 
            The template must match this exact level of detail and structure:

            OPERATOR INTRODUCTION:
            Must use exact language like this:
            "Good afternoon and thank you for standing by. Welcome to {st.session_state.company_name}'s {quarter_options[quarter]} Fiscal Year {st.session_state.fiscal_year} Earnings Conference Call. Today's conference is being recorded. [Operator Instructions for Q&A format]. I would now like to turn the conference over to [IR Name], Head of Investor Relations. Please go ahead."

            IR INTRODUCTION:
            Must follow this exact structure and detail:
            "Thank you, Operator, and good afternoon everyone. Thank you for joining us today for {st.session_state.company_name}'s {quarter_options[quarter]} Fiscal Year {st.session_state.fiscal_year} earnings call. With me today are [CEO Name], Chief Executive Officer, and [CFO Name], Chief Financial Officer.

            We have posted complete [quarter] fiscal {st.session_state.fiscal_year} financial results in our earnings release on the quarterly results section of our website, [company-website].

            Before we begin, I would like to remind you that we will be making forward-looking statements on this call which involve risks and uncertainties. Actual results could differ materially from those contemplated by our forward-looking statements. Please review our filings with the SEC for a discussion of the factors that could cause our results to differ.

            Also note that the forward-looking statements on this call are based on information available to us as of today's date. We disclaim any obligation to update any forward-looking statements except as required by law.

            During this call, we will discuss certain non-GAAP financial measures. Reconciliations to the most directly comparable GAAP financial measures are provided in the earnings release on our Investor Relations website. These non-GAAP measures are not intended to be a substitute for our GAAP results.

            With that, I'll turn the call over to [CEO Name]."

            CEO STRATEGIC OVERVIEW:
            Must use this exact framework:
            "Thanks [IR Name]. Good afternoon everyone.

            In {quarter} {st.session_state.fiscal_year}, we continued to execute on our transformation strategy and make progress strengthening our foundation while reimagining the client experience. Our results demonstrate the positive impact of these efforts:

            Net revenue was $XXX million
            We ended the quarter with X.X million active clients
            Revenue per active client was $XXX
            Adjusted EBITDA was $XX.X million

            Let me highlight several key developments this quarter:

            [Key Strategic Initiative #1 with metrics]
            [Key Strategic Initiative #2 with metrics]
            [Key Strategic Initiative #3 with metrics]

            Now I'll turn it over to [CFO Name] to review our financial results and outlook in detail."

            CFO FINANCIAL REVIEW:
            [Detailed financial review section with metrics]

            GUIDANCE SECTION:
            [Detailed guidance section with ranges]

            CEO CLOSING REMARKS:
            [Strategic closing remarks]

            Q&A TRANSITION:
            "We will now begin the question-and-answer session. [Operator instructions]. Our first question comes from [Analyst Name] with [Firm Name]."

            CLOSING:
            "Thank you everyone for your questions and ongoing interest in {st.session_state.company_name}. We look forward to updating you on our continued progress next quarter."
            """

            system_prompt = f"""You are a financial analyst expert creating a detailed earnings call template for {st.session_state.company_name}. 
            Create a comprehensive, word-for-word template following the exact structure and detail level shown in the prompt. 
            The template should require only the insertion of specific metrics and company details to be ready for use."""

            response = openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",
                     "content": detailed_prompt + "\n\nReference Documents:" + "\n".join(document_excerpts)}
                ],
                temperature=0.7,
                max_tokens=4000
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating template: {str(e)}"


    def generate_questions(uploaded_documents):
        try:
            # First, get a summary of the documents
            summarized_content = ""
            for doc in uploaded_documents.values():
                doc_content = doc['content']
                if 'earnings' in doc['name'].lower():
                    # If it's an earnings call, extract key sections
                    sections = doc_content.split('\n\n')
                    relevant_sections = []
                    for section in sections:
                        if any(keyword in section.lower() for keyword in
                               ['revenue', 'margin', 'guidance', 'strategic', 'operational',
                                'million', 'billion', 'growth', 'client', 'customer']):
                            relevant_sections.append(section)

                    # Take only the most relevant parts
                    doc_summary = '\n'.join(relevant_sections[:10])  # Limit to top 10 sections
                    summarized_content += f"\nFrom {doc['name']}:\n{doc_summary}\n"

            # Check token count and truncate if necessary
            if estimate_tokens(summarized_content) > 12000:  # Leave room for prompt
                summarized_content = summarized_content[:48000]  # ~12000 tokens

            prompt = f"""Based on these earnings call excerpts, generate a comprehensive set of questions that need to be answered to create a complete earnings call transcript. 

    The questions should:
    1. Cover all key metrics and performance indicators mentioned
    2. Include strategic initiatives and their progress
    3. Address forward-looking guidance
    4. Cover operational metrics and business drivers
    5. Include questions about specific programs or features mentioned

    Focus on these categories:
    - Financial Performance (revenue, margins, EBITDA, etc.)
    - Operational Metrics (clients, engagement, etc.)
    - Strategic Initiatives (products, features, etc.)
    - Forward Looking Guidance

    Format the response as a JSON object with these exact categories as keys and lists of specific questions as values.
    Only include questions that can be answered based on the provided content."""

            response = openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system",
                     "content": "You are an expert financial analyst who understands earnings calls."},
                    {"role": "user", "content": prompt + "\n\nReference Content:" + summarized_content}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Error generating questions: {str(e)}")
            return {}


    def auto_populate_answer(question, documents, context=""):
        try:
            # Find relevant sections from documents
            relevant_content = ""
            for doc in documents.values():
                # Split into paragraphs
                paragraphs = doc['content'].split('\n\n')

                # Find relevant paragraphs
                question_keywords = set(question.lower().split())
                for paragraph in paragraphs:
                    # If paragraph contains any question keywords, include it
                    if any(keyword in paragraph.lower() for keyword in question_keywords):
                        relevant_content += paragraph + "\n\n"
                        if len(relevant_content) > 6000:  # Limit content size
                            break

            # If we found no relevant content, take some recent content
            if not relevant_content and documents:
                recent_doc = list(documents.values())[0]
                relevant_content = recent_doc['content'][:6000]

            prompt = f"""Based on these earnings call excerpts, provide a specific answer to this question: "{question}"

    The answer should:
    1. Be specific and include exact metrics where available
    2. Match the style and tone of an earnings call
    3. Be concise but complete
    4. Only include information supported by the documents

    Context: {context}"""

            response = openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system",
                     "content": "You are an expert financial analyst providing precise answers based on earnings call transcripts."},
                    {"role": "user", "content": prompt + "\n\nReference Content:" + relevant_content}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating answer: {str(e)}"


    def generate_complete_transcript(template, answers):
        try:
            # First, let's organize the answers by topic
            organized_answers = {
                "financial_results": [],
                "operational_metrics": [],
                "strategic_updates": [],
                "guidance": []
            }

            for question_key, answer_data in answers.items():
                section = question_key.split('_')[0]  # Get the section from the question key
                if "Financial" in section:
                    organized_answers["financial_results"].append(answer_data['answer'])
                elif "Operational" in section:
                    organized_answers["operational_metrics"].append(answer_data['answer'])
                elif "Strategic" in section:
                    organized_answers["strategic_updates"].append(answer_data['answer'])
                elif "Forward" in section:
                    organized_answers["guidance"].append(answer_data['answer'])

            prompt = f"""Using this earnings call template and the organized answers from the Q&A, 
            create a complete, natural-sounding earnings call transcript. 

            Template:
            {template}

            Financial Results Information:
            {' '.join(organized_answers["financial_results"])}

            Operational Metrics Information:
            {' '.join(organized_answers["operational_metrics"])}

            Strategic Updates Information:
            {' '.join(organized_answers["strategic_updates"])}

            Guidance Information:
            {' '.join(organized_answers["guidance"])}

            Please create a complete transcript that:
            1. Follows the template structure
            2. Incorporates all the specific metrics and information from the Q&A answers
            3. Maintains a natural conversational flow
            4. Includes proper transitions between sections
            5. Sounds authentic to an earnings call
            """

            response = openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system",
                     "content": "You are an expert in creating earnings call transcripts that sound natural and professional."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating complete transcript: {str(e)}"


    # Function to extract text from PDF
    def extract_text_from_pdf(file_bytes):
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error extracting PDF text: {str(e)}"


    # Function to extract text from DOCX
    def extract_text_from_docx(file_bytes):
        try:
            doc = Document(io.BytesIO(file_bytes))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            return f"Error extracting DOCX text: {str(e)}"


    # Function to save answers to a JSON file
    def save_answers():
        with open('earnings_call_answers.json', 'w') as f:
            json.dump(st.session_state.answers, f)


    # Function to load answers from JSON file
    def load_answers():
        try:
            with open('earnings_call_answers.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}


    # Create main tabs
    tab_upload, tab_script, tab_qa, tab_transcript = st.tabs(
        ["Document Upload", "Earnings Call Script", "Q&A Input", "Live Transcript"])

    # Document Upload tab
    with tab_upload:
        st.header(
            f"Document Upload and Analysis - {st.session_state.company_name} {st.session_state.selected_quarter} FY{st.session_state.fiscal_year}")

        upload_col, analyze_col = st.columns([2, 1])

        with upload_col:
            # File uploader
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

            # Document viewing
            if st.session_state.uploaded_files:
                st.subheader("View Uploaded Documents")
                selected_doc = st.selectbox(
                    "Select a document to view:",
                    options=list(st.session_state.uploaded_files.keys()),
                    format_func=lambda x: st.session_state.uploaded_files[x]['name']
                )

                if selected_doc:
                    doc = st.session_state.uploaded_files[selected_doc]
                    st.text_area("Document Content", doc['content'], height=300)

                    # Search functionality
                    search_query = st.text_input("Search within document:")
                    if search_query:
                        lines = doc['content'].split('\n')
                        for i, line in enumerate(lines):
                            if search_query.lower() in line.lower():
                                st.write(f"Line {i + 1}: {line}")

        with analyze_col:
            st.subheader("Generate Template")
            st.write(f"Selected Company: {st.session_state.company_name}")
            st.write(f"Period: {quarter_options[st.session_state.selected_quarter]} FY{st.session_state.fiscal_year}")

            if st.button("Generate Earnings Call Template"):
                if st.session_state.uploaded_files:
                    with st.spinner(
                            f"Analyzing documents and generating template for {st.session_state.company_name}..."):
                        generated_template = generate_earnings_template(
                            st.session_state.uploaded_files,
                            st.session_state.company_name,
                            st.session_state.selected_quarter,
                            st.session_state.fiscal_year
                        )
                        st.session_state.editable_script = generated_template
                        st.success("Template generated! View it in the Earnings Call Script tab.")
                else:
                    st.warning("Please upload documents first.")

            st.markdown("---")
            st.write("Template will be generated based on:")
            st.write("- Company's typical metrics")
            st.write("- Historical language patterns")
            st.write("- Standard structure")
            st.write("- Characteristic explanations")

    # Earnings Call Script tab
    with tab_script:
        st.header(
            f"Earnings Call Script Template - {st.session_state.company_name} {st.session_state.selected_quarter} FY{st.session_state.fiscal_year}")

        if not st.session_state.editable_script:
            st.info(
                "Upload documents and click 'Generate Earnings Call Template' in the Document Upload tab to create a template, or edit the default template below.")

        # Create an editable text area for the script
        edited_script = st.text_area(
            "Edit Script Template:",
            value=st.session_state.editable_script,
            height=800,
            key="script_editor"
        )

        # Save edited script back to session state
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Save Script Changes"):
                st.session_state.editable_script = edited_script
                st.success("Script changes saved!")

    # Q&A Input tab
    with tab_qa:
        st.header(
            f"Q&A Input - {st.session_state.company_name} {st.session_state.selected_quarter} FY{st.session_state.fiscal_year}")

        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("Generate Questions from Documents"):
                if st.session_state.uploaded_files:
                    with st.spinner("Analyzing documents and generating questions..."):
                        generated_questions = generate_questions(st.session_state.uploaded_files)
                        st.session_state.questions = generated_questions
                        st.success("Questions generated successfully!")
                else:
                    st.warning("Please upload documents first.")

        with col2:
            if st.button("Auto-Populate All Answers"):
                if hasattr(st.session_state, 'questions'):
                    with st.spinner("Generating answers..."):
                        for section, section_questions in st.session_state.questions.items():
                            for q in section_questions:
                                question_key = f"{section}_{q}"
                                if question_key not in st.session_state.answers:
                                    answer = auto_populate_answer(q, st.session_state.uploaded_files)
                                    st.session_state.answers[question_key] = {
                                        'answer': answer,
                                        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'user': 'AI Assistant'
                                    }
                        st.success("Answers generated successfully!")
                else:
                    st.warning("Please generate questions first.")

        # Display questions and answers
        if hasattr(st.session_state, 'questions'):
            for section, section_questions in st.session_state.questions.items():
                st.subheader(section)
                for q in section_questions:
                    question_key = f"{section}_{q}"
                    st.write(f"**{q}**")

                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        answer = st.text_area(
                            "Answer:",
                            value=st.session_state.answers.get(question_key, {}).get('answer', ''),
                            key=f"input_{question_key}",
                            height=100
                        )

                        if answer:
                            st.session_state.answers[question_key] = {
                                'answer': answer,
                                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'user': st.session_state.get('user', 'Anonymous')
                            }

                    with col2:
                        if st.button("Auto-Populate", key=f"auto_{question_key}"):
                            answer = auto_populate_answer(q, st.session_state.uploaded_files)
                            st.session_state.answers[question_key] = {
                                'answer': answer,
                                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'user': 'AI Assistant'
                            }

                    with col3:
                        if question_key in st.session_state.answers:
                            st.write("Last updated:", st.session_state.answers[question_key]['last_updated'])
                            st.write("Updated by:", st.session_state.answers[question_key]['user'])

                    st.markdown("---")

    # Live Transcript tab
    with tab_transcript:
        st.header(
            f"Live Earnings Call Transcript - {st.session_state.company_name} {st.session_state.selected_quarter} FY{st.session_state.fiscal_year}")

        if st.session_state.editable_script:
            st.markdown(st.session_state.editable_script)
        else:
            st.info("Generate a template in the Document Upload tab or create one in the Earnings Call Script tab.")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Refresh Transcript"):
                st.session_state.transcript = st.session_state.editable_script
                st.success("Transcript updated!")

        with col2:
            if st.button("Export Transcript"):
                st.download_button(
                    label="Download Transcript",
                    data=st.session_state.editable_script,
                    file_name=f"{st.session_state.company_name}_{st.session_state.selected_quarter}_FY{st.session_state.fiscal_year}_transcript_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )