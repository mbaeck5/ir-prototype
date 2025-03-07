import streamlit as st

def run():
    company_name = {} if 'company_name' not in st.session_state else st.session_state['company_name']
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