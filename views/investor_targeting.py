import streamlit as st


def run():
    company_name = {} if 'company_name' not in st.session_state else st.session_state['company_name']
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