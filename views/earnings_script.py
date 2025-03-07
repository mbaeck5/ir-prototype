from datetime import datetime

import streamlit as st
import pandas as pd

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
            "Please add specific details and commentary on the quarter that you would like considered in this quarter's script")

        # Initialize session state for context if not exists
        if 'script_context' not in st.session_state:
            st.session_state.script_context = {
                'tone': '',
                'initiatives': '',
                'considerations': ''
            }

        # Initialize disclosure metrics if not exists
        if 'disclosure_metrics' not in st.session_state:
            st.session_state.disclosure_metrics = []

        # Initialize financial disclosures if not exists
        if 'financial_disclosures' not in st.session_state:
            st.session_state.financial_disclosures = {
                'financial_highlights': [],
                'non_gaap_metrics': [],
                'cfo_metrics': [],
                'guidance': []
            }

        # Use columns for better layout organization
        col1, col2 = st.columns(2)

        # Left column - Narrative context
        with col1:
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

        # Right column - Metrics and disclosures
        with col2:
            # Disclosure Metrics Section
            st.markdown("### Disclosure Metrics")
            st.write("Add specific metrics that should be included in the script")

            # Form for adding new disclosure metrics
            with st.form(key="add_disclosure_metric"):
                metric_name = st.text_input("Metric Name (e.g., Active Users, Retention Rate)")
                metric_value = st.text_input("Metric Value")
                metric_context = st.text_input("Context (e.g., 10% increase YoY)")

                submit_button = st.form_submit_button(label="Add Metric")
                if submit_button and metric_name:
                    new_metric = {
                        "name": metric_name,
                        "value": metric_value,
                        "context": metric_context,
                        "id": len(st.session_state.disclosure_metrics)
                    }
                    st.session_state.disclosure_metrics.append(new_metric)
                    st.success(f"Added metric: {metric_name}")

            # Display existing disclosure metrics
            if st.session_state.disclosure_metrics:
                st.markdown("#### Current Disclosure Metrics")

                metrics_df = pd.DataFrame(st.session_state.disclosure_metrics)
                if not metrics_df.empty:
                    # Display the dataframe
                    st.dataframe(
                        metrics_df[["name", "value", "context"]], 
                        use_container_width=True,
                        hide_index=True
                    )

                # Option to remove metrics
                if st.session_state.disclosure_metrics:
                    metric_to_remove = st.selectbox(
                        "Select metric to remove:",
                        options=range(len(st.session_state.disclosure_metrics)),
                        format_func=lambda i: st.session_state.disclosure_metrics[i]["name"]
                    )

                    if st.button("Remove Selected Metric"):
                        del st.session_state.disclosure_metrics[metric_to_remove]
                        st.success("Metric removed successfully!")
                        st.rerun()

        # Financial Disclosures Section - Full width
        st.markdown("---")
        st.markdown("### Financial Disclosures")
        st.write("Add specific financial metrics that will be highlighted in the script")

        # Create tabs for different financial disclosure categories
        fin_tab1, fin_tab2, fin_tab3, fin_tab4 = st.tabs([
            "Financial Highlights", 
            "Non-GAAP Metrics", 
            "CFO Metrics", 
            "Guidance"
        ])

        # Tab 1: Financial Highlights
        with fin_tab1:
            handle_financial_section(
                "financial_highlights", 
                "Financial Highlights", 
                "Add key financial highlights like revenue, growth rates, etc."
            )

        # Tab 2: Non-GAAP Metrics
        with fin_tab2:
            handle_financial_section(
                "non_gaap_metrics", 
                "Non-GAAP Metrics", 
                "Add non-GAAP metrics like adjusted EBITDA, free cash flow, etc."
            )

        # Tab 3: CFO Metrics
        with fin_tab3:
            handle_financial_section(
                "cfo_metrics",
                "CFO Metrics",
                "Add metrics typically presented by the CFO such as operating expenses, margins, etc."
            )

        # Tab 4: Guidance
        with fin_tab4:
            handle_financial_section(
                "guidance",
                "Guidance",
                "Add forward-looking guidance metrics for future periods"
            )

        # Save button for all context
        st.markdown("---")
        if st.button("Save All Context", key="save_all_context"):
            st.success("All context and metrics saved successfully! You can now proceed to Template Generation.")

    # Template Generation Tab
    with tab1:
        st.subheader("Generate Template")
        if st.session_state.uploaded_files:
            if st.button("Generate Earnings Call Template", key="generate_template"):
                with st.spinner(f"Analyzing documents and generating template for {company_name}..."):
                    # Include script context and metrics in the template generation
                    context_info = ""
                    if hasattr(st.session_state, 'script_context'):
                        context_info = f"""
                        Script Context:
                        Tone: {st.session_state.script_context.get('tone', '')}
                        Strategic Initiatives: {st.session_state.script_context.get('initiatives', '')}
                        Additional Considerations: {st.session_state.script_context.get('considerations', '')}
                        """

                    # Add disclosure metrics
                    if hasattr(st.session_state, 'disclosure_metrics') and st.session_state.disclosure_metrics:
                        context_info += "\n\nDisclosure Metrics:\n"
                        for metric in st.session_state.disclosure_metrics:
                            context_info += f"- {metric['name']}: {metric['value']} ({metric['context']})\n"

                    # Add financial disclosures
                    if hasattr(st.session_state, 'financial_disclosures'):
                        context_info += "\n\nFinancial Disclosures:\n"

                        # Financial Highlights
                        if st.session_state.financial_disclosures.get('financial_highlights'):
                            context_info += "\nFinancial Highlights:\n"
                            for metric in st.session_state.financial_disclosures['financial_highlights']:
                                context_info += f"- {metric['name']}: {metric['value']} ({metric['context']})\n"

                        # Non-GAAP Metrics
                        if st.session_state.financial_disclosures.get('non_gaap_metrics'):
                            context_info += "\nNon-GAAP Metrics:\n"
                            for metric in st.session_state.financial_disclosures['non_gaap_metrics']:
                                context_info += f"- {metric['name']}: {metric['value']} ({metric['context']})\n"

                        # CFO Metrics
                        if st.session_state.financial_disclosures.get('cfo_metrics'):
                            context_info += "\nCFO Metrics:\n"
                            for metric in st.session_state.financial_disclosures['cfo_metrics']:
                                context_info += f"- {metric['name']}: {metric['value']} ({metric['context']})\n"

                        # Guidance
                        if st.session_state.financial_disclosures.get('guidance'):
                            context_info += "\nGuidance:\n"
                            for metric in st.session_state.financial_disclosures['guidance']:
                                context_info += f"- {metric['name']}: {metric['value']} ({metric['context']})\n"

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


def handle_financial_section(section_key, section_title, description):
    """Helper function to handle each financial disclosure section"""
    st.subheader(section_title)
    st.write(description)

    # Form for adding new financial metrics
    with st.form(key=f"add_{section_key}_metric"):
        metric_name = st.text_input("Metric Name", key=f"{section_key}_name")
        metric_value = st.text_input("Metric Value", key=f"{section_key}_value")
        metric_context = st.text_input("Context (e.g., YoY change, significance)", key=f"{section_key}_context")

        submit_button = st.form_submit_button(label="Add Metric")
        if submit_button and metric_name:
            if section_key not in st.session_state.financial_disclosures:
                st.session_state.financial_disclosures[section_key] = []

            new_metric = {
                "name": metric_name,
                "value": metric_value,
                "context": metric_context,
                "id": len(st.session_state.financial_disclosures[section_key])
            }
            st.session_state.financial_disclosures[section_key].append(new_metric)
            st.success(f"Added {section_title} metric: {metric_name}")

    # Display existing metrics for this section
    if section_key in st.session_state.financial_disclosures and st.session_state.financial_disclosures[section_key]:
        st.markdown(f"#### Current {section_title}")

        metrics_df = pd.DataFrame(st.session_state.financial_disclosures[section_key])
        if not metrics_df.empty:
            # Display the dataframe
            st.dataframe(
                metrics_df[["name", "value", "context"]], 
                use_container_width=True,
                hide_index=True
            )

        # Option to remove metrics
        if st.session_state.financial_disclosures[section_key]:
            metric_to_remove = st.selectbox(
                "Select metric to remove:",
                options=range(len(st.session_state.financial_disclosures[section_key])),
                format_func=lambda i: st.session_state.financial_disclosures[section_key][i]["name"],
                key=f"select_{section_key}"
            )

            if st.button("Remove Selected Metric", key=f"remove_{section_key}"):
                del st.session_state.financial_disclosures[section_key][metric_to_remove]
                st.success("Metric removed successfully!")
                st.rerun()