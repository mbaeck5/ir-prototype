import streamlit as st

from utils.openai_client import analyze_analyst_questions


def run():
    company_name = {} if 'company_name' not in st.session_state else st.session_state['company_name']
    selected_quarter = {} if 'selected_quarter' not in st.session_state else st.session_state['selected_quarter']
    fiscal_year = {} if 'fiscal_year' not in st.session_state else st.session_state['fiscal_year']

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