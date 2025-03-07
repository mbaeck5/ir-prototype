from datetime import datetime

import streamlit as st

from utils.openai_client import generate_earnings_template, generate_questions


def run():
    company_name = {} if 'company_name' not in st.session_state else st.session_state['company_name']
    selected_quarter = {} if 'selected_quarter' not in st.session_state else st.session_state['selected_quarter']
    fiscal_year = {} if 'fiscal_year' not in st.session_state else st.session_state['fiscal_year']

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