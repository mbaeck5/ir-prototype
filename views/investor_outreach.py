import streamlit as st

def run():
    company_name = {} if 'company_name' not in st.session_state else st.session_state['company_name']
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