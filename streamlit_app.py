import streamlit as st

from utils.openai_client import init_open_ai_client
from views import document_upload, earnings_script, qa_input, market_updates, shareholders
from views import investor_outreach, investor_targeting, analyst_coverage, ir_communications, ir_crm

# Initialize page config and styling
st.set_page_config(page_title="IR Content Creation Hub", layout="wide")

# Initialize session state variables
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'editable_script' not in st.session_state:
    st.session_state.editable_script = ""
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
if 'company_name' not in st.session_state:
    st.session_state.company_name = "Stitch Fix"
if 'quarter_options' not in st.session_state:
    st.session_state.quarter_options = {
    "Q1": "First Quarter",
    "Q2": "Second Quarter",
    "Q3": "Third Quarter",
    "Q4": "Fourth Quarter"
}
if 'selected_quarter' not in st.session_state:
    st.session_state.selected_quarter = "Q1"
if 'fiscal_year' not in st.session_state:
    st.session_state.fiscal_year = "2025"
if 'openai_client' not in st.session_state:
    st.session_state.openai_client = init_open_ai_client()
# Initialize session states for analyst coverage
if 'analyst_coverage_data' not in st.session_state:
    st.session_state.analyst_coverage_data = []
if 'rating_history' not in st.session_state:
    st.session_state.rating_history = []
# Initialize session states for IR Communications
if 'ir_emails' not in st.session_state:
    st.session_state.ir_emails = []
if 'ir_email_stats' not in st.session_state:
    st.session_state.ir_email_stats = {}
if 'ir_chatbot_conversations' not in st.session_state:
    st.session_state.ir_chatbot_conversations = []
# Initialize session state for IR CRM
if 'ir_meetings' not in st.session_state:
    st.session_state.ir_meetings = {}


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

st.sidebar.header("Template Settings")
company_name = st.sidebar.text_input("Company Name:", value=st.session_state.company_name)
selected_quarter = st.sidebar.selectbox("Quarter:", options=st.session_state.quarter_options.keys(), )
fiscal_year = st.sidebar.text_input("Fiscal Year:", value=st.session_state.fiscal_year)

# Main navigation
st.title("IR Content Creation and Prep Hub")


pg = st.navigation([
    st.Page(document_upload.run, title="Document Upload", icon=":material/upload_file:", url_path="1"),
    st.Page(earnings_script.run, title="Earnings Script", icon=":material/script:", url_path="2"),
    st.Page(qa_input.run, title="Q&A Preparation", icon=":material/design_services:", url_path="3"),
    st.Page(shareholders.run, title="ShareHolders", icon=":material/local_library:", url_path="4"),
    st.Page(investor_outreach.run, title="Investor Outreach", icon=":material/cell_tower:", url_path="5"),
    st.Page(investor_targeting.run, title="Investor Targeting", icon=":material/track_changes:", url_path="6"),
    st.Page(market_updates.run, title="Market Updates", icon=":material/sync_alt:", url_path="7"),
    st.Page(analyst_coverage.run, title="Analyst Coverage", icon=":material/analytics:", url_path="8"),
    st.Page(ir_communications.run, title="IR Communications", icon=":material/email:", url_path="9"),
    st.Page(ir_crm.run, title="IR CRM", icon=":material/account_box:", url_path="10"),
])

pg.run()
