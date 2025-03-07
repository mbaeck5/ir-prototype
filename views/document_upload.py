# views/document_upload.py
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import uuid
from utils.document_processing import extract_text_from_pdf, extract_text_from_docx

def run():
    company_name = {} if 'company_name' not in st.session_state else st.session_state['company_name']
    selected_quarter = {} if 'selected_quarter' not in st.session_state else st.session_state['selected_quarter']
    fiscal_year = {} if 'fiscal_year' not in st.session_state else st.session_state['fiscal_year']

    st.header(f"Setup / Quarterly Context - {company_name} {selected_quarter} FY{fiscal_year}")

    # Initialize session state variables for each tab
    if 'quarterly_context' not in st.session_state:
        st.session_state.quarterly_context = {
            "key_highlights": "",
            "business_challenges": "",
            "product_updates": "",
            "financial_metrics": "",
            "outlook": ""
        }

    if 'recommended_themes' not in st.session_state:
        st.session_state.recommended_themes = [
            {"id": "theme1", "title": "Revenue Growth Acceleration", "description": "Focus on how strategic initiatives are accelerating revenue growth across key markets.", "selected": False},
            {"id": "theme2", "title": "Operational Efficiency", "description": "Highlight cost-saving measures and operational improvements driving margin expansion.", "selected": False},
            {"id": "theme3", "title": "Innovation Pipeline", "description": "Showcase new product developments and R&D investments positioning the company for future growth.", "selected": False},
            {"id": "theme4", "title": "Market Share Gains", "description": "Emphasize competitive advantages leading to market share gains in core segments.", "selected": False},
            {"id": "theme5", "title": "Digital Transformation", "description": "Detail progress on digital initiatives enhancing customer experience and internal processes.", "selected": False}
        ]

    if 'document_categories' not in st.session_state:
        st.session_state.document_categories = {
            "financial_info": {},
            "company_materials": {},
            "past_earnings": {},
            "competitor_info": {},
            "market_research": {}
        }

    if 'calendar_events' not in st.session_state:
        st.session_state.calendar_events = []

    if 'calendar_date_range' not in st.session_state:
        # Default to current quarter
        current_month = datetime.now().month
        current_year = datetime.now().year
        quarter_start_month = ((current_month - 1) // 3) * 3 + 1
        st.session_state.calendar_date_range = {
            "start_date": datetime(current_year, quarter_start_month, 1),
            "end_date": datetime(current_year, quarter_start_month, 1) + timedelta(days=90)
        }

    # Create tabs for the different sections
    tab1, tab2, tab3 = st.tabs(["Quarterly Content", "Document Upload", "IR Calendar"])

    # Tab 1: Quarterly Content
    with tab1:
        st.subheader("Key Quarterly Context")

        # Text input fields for quarterly context
        st.session_state.quarterly_context["key_highlights"] = st.text_area(
            "Key Areas to Highlight This Quarter",
            value=st.session_state.quarterly_context["key_highlights"],
            height=100,
            help="What are the most important achievements or metrics to emphasize?"
        )

        st.session_state.quarterly_context["business_challenges"] = st.text_area(
            "Business Challenges to Address",
            value=st.session_state.quarterly_context["business_challenges"],
            height=100,
            help="What challenges or headwinds should be acknowledged and addressed?"
        )

        st.session_state.quarterly_context["product_updates"] = st.text_area(
            "Product or Service Updates",
            value=st.session_state.quarterly_context["product_updates"],
            height=100,
            help="What product launches, updates, or milestones occurred this quarter?"
        )

        st.session_state.quarterly_context["financial_metrics"] = st.text_area(
            "Key Financial Metrics",
            value=st.session_state.quarterly_context["financial_metrics"],
            height=100,
            help="What financial metrics should be emphasized in the earnings call?"
        )

        st.session_state.quarterly_context["outlook"] = st.text_area(
            "Forward-Looking Guidance/Outlook",
            value=st.session_state.quarterly_context["outlook"],
            height=100,
            help="What guidance or outlook should be communicated for future quarters?"
        )

        # Save button for quarterly context
        if st.button("Save Quarterly Context"):
            st.success("Quarterly context saved successfully!")

        # AI Recommended Themes Section
        st.markdown("---")
        st.subheader("AI Recommended Themes")
        st.write("Based on insights from past quarters, competitor earnings calls, analyst questions, and market news, the following themes are recommended for this quarter's earnings presentation:")

        # Display recommended themes with checkboxes
        for i, theme in enumerate(st.session_state.recommended_themes):
            col1, col2 = st.columns([1, 10])
            with col1:
                theme["selected"] = st.checkbox("", value=theme["selected"], key=f"theme_{i}")
            with col2:
                st.markdown(f"**{theme['title']}**")
                st.write(theme["description"])
            st.markdown("---")

        # Apply selected themes button
        if st.button("Apply Selected Themes"):
            selected_themes = [theme for theme in st.session_state.recommended_themes if theme["selected"]]
            if selected_themes:
                st.success(f"Applied {len(selected_themes)} themes to your quarterly materials!")
            else:
                st.warning("No themes selected. Please select at least one theme.")

    # Tab 2: Document Upload
    with tab2:
        st.subheader("Document Upload by Category")

        # Create a tab for each document category
        doc_tabs = st.tabs(["Financial Info", "Company Materials", "Past Earnings", "Competitor Info", "Market Research"])

        # Financial Info tab
        with doc_tabs[0]:
            st.write("Upload financial statements, reports, and other financial data")
            financial_files = st.file_uploader(
                "Upload financial documents",
                accept_multiple_files=True,
                type=['pdf', 'docx', 'txt', 'xlsx', 'csv'],
                key="financial_uploader"
            )

            process_uploaded_files(financial_files, "financial_info")
            display_category_documents("financial_info")

        # Company Materials tab
        with doc_tabs[1]:
            st.write("Upload company presentations, press releases, and other materials")
            company_files = st.file_uploader(
                "Upload company materials",
                accept_multiple_files=True,
                type=['pdf', 'docx', 'txt', 'pptx'],
                key="company_uploader"
            )

            process_uploaded_files(company_files, "company_materials")
            display_category_documents("company_materials")

        # Past Earnings tab
        with doc_tabs[2]:
            st.write("Upload previous earnings call transcripts, presentations, and Q&A sessions")
            earnings_files = st.file_uploader(
                "Upload past earnings materials",
                accept_multiple_files=True,
                type=['pdf', 'docx', 'txt'],
                key="earnings_uploader"
            )

            process_uploaded_files(earnings_files, "past_earnings")
            display_category_documents("past_earnings")

        # Competitor Info tab
        with doc_tabs[3]:
            st.write("Upload competitor earnings transcripts, analysis, and benchmark data")
            competitor_files = st.file_uploader(
                "Upload competitor information",
                accept_multiple_files=True,
                type=['pdf', 'docx', 'txt', 'xlsx', 'csv'],
                key="competitor_uploader"
            )

            process_uploaded_files(competitor_files, "competitor_info")
            display_category_documents("competitor_info")

        # Market Research tab
        with doc_tabs[4]:
            st.write("Upload market reports, industry analysis, and research")
            market_files = st.file_uploader(
                "Upload market research",
                accept_multiple_files=True,
                type=['pdf', 'docx', 'txt'],
                key="market_uploader"
            )

            process_uploaded_files(market_files, "market_research")
            display_category_documents("market_research")

    # Tab 3: IR Calendar
    with tab3:
        st.subheader("IR Event Calendar")

        # Date range selection for calendar
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=st.session_state.calendar_date_range["start_date"],
                key="calendar_start_date"
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=st.session_state.calendar_date_range["end_date"],
                key="calendar_end_date"
            )

        # Update date range in session state
        if start_date and end_date:
            if start_date > end_date:
                st.error("Error: End date must fall after start date.")
            else:
                st.session_state.calendar_date_range["start_date"] = datetime.combine(start_date, datetime.min.time())
                st.session_state.calendar_date_range["end_date"] = datetime.combine(end_date, datetime.min.time())

        # Event creation form
        st.markdown("---")
        st.subheader("Add New Event")

        event_types = [
            "Company Earnings Call",
            "Competitor Earnings Call",
            "Non-Deal Roadshow (NDR)",
            "Investor Conference",
            "Board Meeting",
            "Industry Event",
            "Other"
        ]

        col1, col2 = st.columns(2)
        with col1:
            event_title = st.text_input("Event Title", key="event_title")
            event_date = st.date_input("Event Date", key="event_date")
            event_type = st.selectbox("Event Type", options=event_types, key="event_type")

        with col2:
            event_description = st.text_area("Event Description", height=100, key="event_description")
            event_time = st.time_input("Event Time", key="event_time")
            event_location = st.text_input("Location/Link", key="event_location")

        if st.button("Add Event to Calendar"):
            if event_title and event_date:
                event_id = str(uuid.uuid4())
                new_event = {
                    "id": event_id,
                    "title": event_title,
                    "date": event_date,
                    "time": event_time,
                    "type": event_type,
                    "description": event_description,
                    "location": event_location
                }
                st.session_state.calendar_events.append(new_event)
                st.success(f"Added event: {event_title}")
            else:
                st.error("Event title and date are required.")

        # Display calendar
        st.markdown("---")
        st.subheader("IR Calendar")

        # Convert events to dataframe for display
        if st.session_state.calendar_events:
            events_df = pd.DataFrame(st.session_state.calendar_events)

            # Filter events by date range
            start_date_naive = st.session_state.calendar_date_range["start_date"].date()
            end_date_naive = st.session_state.calendar_date_range["end_date"].date()

            filtered_events = events_df[
                (events_df["date"] >= start_date_naive) &
                (events_df["date"] <= end_date_naive)
            ]

            if not filtered_events.empty:
                # Sort events by date
                filtered_events = filtered_events.sort_values(by="date")

                # Display events in a table
                st.dataframe(
                    filtered_events[["title", "date", "time", "type", "location"]],
                    use_container_width=True,
                    hide_index=True
                )

                # Add ability to view and delete events
                selected_event_id = st.selectbox(
                    "Select event to view details or delete:",
                    options=filtered_events["id"].tolist(),
                    format_func=lambda x: filtered_events[filtered_events["id"] == x]["title"].iloc[0]
                )

                if selected_event_id:
                    selected_event = next((e for e in st.session_state.calendar_events if e["id"] == selected_event_id), None)
                    if selected_event:
                        st.markdown("---")
                        st.subheader("Event Details")
                        st.write(f"**Title:** {selected_event['title']}")
                        st.write(f"**Date & Time:** {selected_event['date']} at {selected_event['time']}")
                        st.write(f"**Type:** {selected_event['type']}")
                        st.write(f"**Location:** {selected_event['location']}")
                        st.write(f"**Description:** {selected_event['description']}")

                        if st.button("Delete Event"):
                            st.session_state.calendar_events = [e for e in st.session_state.calendar_events if e["id"] != selected_event_id]
                            st.success(f"Deleted event: {selected_event['title']}")
                            st.rerun()
            else:
                st.info(f"No events scheduled between {start_date_naive} and {end_date_naive}.")
        else:
            st.info("No events have been added to the calendar yet.")

        # Calendar view (simplified monthly view)
        st.markdown("---")
        st.subheader("Monthly Calendar View")

        if st.session_state.calendar_events:
            # Get the selected month and year
            selected_month = st.selectbox(
                "Select Month",
                options=range(1, 13),
                format_func=lambda m: datetime(2000, m, 1).strftime("%B"),
                index=datetime.now().month - 1
            )

            selected_year = st.selectbox(
                "Select Year",
                options=range(datetime.now().year - 1, datetime.now().year + 3),
                index=1  # Default to current year
            )

            # Filter events for the selected month and year
            month_events = [
                e for e in st.session_state.calendar_events
                if e["date"].month == selected_month and e["date"].year == selected_year
            ]

            # Create a calendar view
            if month_events:
                # Group events by date
                events_by_date = {}
                for event in month_events:
                    date_str = event["date"].strftime("%Y-%m-%d")
                    if date_str not in events_by_date:
                        events_by_date[date_str] = []
                    events_by_date[date_str].append(event)

                # Create a visual calendar
                first_day = datetime(selected_year, selected_month, 1)
                last_day = (datetime(selected_year, selected_month + 1, 1) if selected_month < 12 else datetime(selected_year + 1, 1, 1)) - timedelta(days=1)

                # Get first weekday (0 is Monday, 6 is Sunday)
                first_weekday = first_day.weekday()

                # Create calendar grid
                calendar_days = []
                # Add empty cells for days before the first of the month
                for _ in range(first_weekday):
                    calendar_days.append(None)

                # Add all days in the month
                for day in range(1, last_day.day + 1):
                    date_obj = datetime(selected_year, selected_month, day)
                    date_str = date_obj.strftime("%Y-%m-%d")
                    day_events = events_by_date.get(date_str, [])
                    calendar_days.append((day, day_events))

                # Render calendar as a 7-column grid
                st.write(f"### {first_day.strftime('%B %Y')}")
                weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                cols = st.columns(7)

                # Write weekday headers
                for i, col in enumerate(cols):
                    col.markdown(f"**{weekdays[i]}**", unsafe_allow_html=True)

                # Write calendar days
                for i in range(0, len(calendar_days), 7):
                    week_days = calendar_days[i:i+7]
                    cols = st.columns(7)

                    for j, day_data in enumerate(week_days):
                        if day_data is None:
                            cols[j].write("")
                        else:
                            day, events = day_data
                            if events:
                                cols[j].markdown(f"**{day}** 📅", unsafe_allow_html=True)
                                event_list = "<ul style='font-size: 0.8em; padding-left: 15px;'>"
                                for event in events:
                                    event_list += f"<li>{event['title']}</li>"
                                event_list += "</ul>"
                                cols[j].markdown(event_list, unsafe_allow_html=True)
                            else:
                                cols[j].write(str(day))
            else:
                st.info(f"No events scheduled for {datetime(selected_year, selected_month, 1).strftime('%B %Y')}.")
        else:
            st.info("No events have been added to the calendar yet.")


def process_uploaded_files(uploaded_files, category_key):
    """Process and store uploaded files by category"""
    if uploaded_files:
        for file in uploaded_files:
            file_key = f"{file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            if file_key not in st.session_state.document_categories[category_key]:
                file_bytes = file.read()
                file_type = file.name.split('.')[-1].lower()

                if file_type == 'pdf':
                    text_content = extract_text_from_pdf(file_bytes)
                elif file_type == 'docx':
                    text_content = extract_text_from_docx(file_bytes)
                elif file_type == 'txt':
                    text_content = file_bytes.decode('utf-8')
                else:
                    text_content = f"File uploaded: {file.name} (Content extraction not supported for {file_type} files)"

                st.session_state.document_categories[category_key][file_key] = {
                    'name': file.name,
                    'content': text_content,
                    'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                st.success(f"Successfully uploaded: {file.name}")


def display_category_documents(category_key):
    """Display documents for a specific category"""
    category_files = st.session_state.document_categories.get(category_key, {})
    if category_files:
        st.write(f"**Uploaded {category_key.replace('_', ' ').title()} Documents ({len(category_files)})**")

        for file_key, file_data in category_files.items():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"📄 {file_data['name']}")
            with col2:
                st.write(f"Uploaded: {file_data['upload_time']}")
            with col3:
                view_button = st.button(f"View", key=f"view_{file_key}")
                delete_button = st.button(f"Delete", key=f"delete_{file_key}")

            if view_button:
                with st.expander(f"Content of {file_data['name']}", expanded=True):
                    st.text_area("Document Content", file_data['content'], height=300, key=f"content_{file_key}")

            if delete_button:
                del st.session_state.document_categories[category_key][file_key]
                st.success(f"Deleted: {file_data['name']}")
                st.rerun()

            st.markdown("---")
    else:
        st.info(f"No {category_key.replace('_', ' ')} documents uploaded yet.")