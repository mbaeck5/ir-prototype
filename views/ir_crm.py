import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import random

def run():
    company_name = {} if 'company_name' not in st.session_state else st.session_state['company_name']

    st.header(f"IR CRM - {company_name}")

    # Initialize session state variables
    if 'ir_meetings' not in st.session_state:
        st.session_state.ir_meetings = generate_sample_data()

    # Create tabs
    tab1, tab2 = st.tabs(["Meetings", "Contacts"])

    # Tab 1: Meetings
    with tab1:
        st.subheader("Meeting Management")

        meeting_tabs = st.tabs(["Meeting List", "Add Meeting"])

        # Meeting List Tab
        with meeting_tabs[0]:
            meetings = st.session_state.ir_meetings.get('meetings', [])

            if meetings:
                # Create a dataframe for display
                meetings_df = pd.DataFrame([
                    {
                        'Date': m.get('date', ''),
                        'Title': m.get('title', ''),
                        'Firm': m.get('firm', ''),
                        'Attendees': ', '.join(m.get('attendees', [])),
                        'Type': m.get('type', ''),
                        'Follow-up': 'Yes' if m.get('follow_up', False) else 'No'
                    } for m in meetings
                ])

                st.dataframe(meetings_df, use_container_width=True, hide_index=True)

                # Meeting details
                selected_meeting = st.selectbox(
                    "Select meeting to view details:",
                    options=range(len(meetings)),
                    format_func=lambda i: f"{meetings[i].get('date', '')} - {meetings[i].get('title', '')}"
                )

                meeting = meetings[selected_meeting]

                st.markdown("### Meeting Details")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Title:** {meeting.get('title', '')}")
                    st.markdown(f"**Date:** {meeting.get('date', '')}")
                    st.markdown(f"**Firm:** {meeting.get('firm', '')}")

                with col2:
                    st.markdown(f"**Type:** {meeting.get('type', '')}")
                    st.markdown(f"**Attendees:** {', '.join(meeting.get('attendees', []))}")
                    st.markdown(f"**Follow-up Required:** {'Yes' if meeting.get('follow_up', False) else 'No'}")

                st.markdown("**Notes:**")
                st.markdown(meeting.get('notes', 'No notes available.'))

                if meeting.get('questions'):
                    st.markdown("**Questions Discussed:**")
                    for q in meeting.get('questions', []):
                        st.markdown(f"- {q}")
            else:
                st.info("No meetings recorded. Add your first meeting using the 'Add Meeting' tab.")

        # Add Meeting Tab
        with meeting_tabs[1]:
            with st.form("add_meeting_form"):
                st.markdown("### Add New Meeting")

                col1, col2 = st.columns(2)

                with col1:
                    title = st.text_input("Meeting Title")
                    date = st.date_input("Meeting Date", value=datetime.now())
                    firm = st.text_input("Firm Name")

                with col2:
                    meeting_type = st.selectbox(
                        "Meeting Type",
                        options=["1:1 Meeting", "Group Meeting", "Conference", "NDR", "Other"]
                    )
                    attendees = st.text_input("Attendees (comma separated)")
                    follow_up = st.checkbox("Follow-up Required")

                notes = st.text_area("Meeting Notes")
                questions = st.text_area("Questions Discussed (one per line)")

                submitted = st.form_submit_button("Save Meeting")

                if submitted:
                    # Process inputs
                    attendees_list = [a.strip() for a in attendees.split(',') if a.strip()]
                    questions_list = [q.strip() for q in questions.split('\n') if q.strip()]

                    # Create new meeting
                    new_meeting = {
                        'id': str(uuid.uuid4()),
                        'title': title,
                        'date': date.strftime('%Y-%m-%d'),
                        'firm': firm,
                        'type': meeting_type,
                        'attendees': attendees_list,
                        'notes': notes,
                        'questions': questions_list,
                        'follow_up': follow_up,
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    # Add to session state
                    if 'meetings' not in st.session_state.ir_meetings:
                        st.session_state.ir_meetings['meetings'] = []

                    st.session_state.ir_meetings['meetings'].append(new_meeting)
                    st.success("Meeting added successfully!")

    # Tab 2: Contacts
    with tab2:
        st.subheader("Contact Management")

        contact_tabs = st.tabs(["Contact List", "Add Contact"])

        # Contact List Tab
        with contact_tabs[0]:
            contacts = st.session_state.ir_meetings.get('contacts', [])

            if contacts:
                # Create a dataframe for display
                contacts_df = pd.DataFrame([
                    {
                        'Name': c.get('name', ''),
                        'Title': c.get('title', ''),
                        'Firm': c.get('firm', ''),
                        'Email': c.get('email', ''),
                        'Phone': c.get('phone', '')
                    } for c in contacts
                ])

                st.dataframe(contacts_df, use_container_width=True, hide_index=True)

                # Contact details
                selected_contact = st.selectbox(
                    "Select contact to view details:",
                    options=range(len(contacts)),
                    format_func=lambda i: f"{contacts[i].get('name', '')} - {contacts[i].get('firm', '')}"
                )

                contact = contacts[selected_contact]

                st.markdown("### Contact Details")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Name:** {contact.get('name', '')}")
                    st.markdown(f"**Title:** {contact.get('title', '')}")
                    st.markdown(f"**Firm:** {contact.get('firm', '')}")

                with col2:
                    st.markdown(f"**Email:** {contact.get('email', '')}")
                    st.markdown(f"**Phone:** {contact.get('phone', '')}")
                    st.markdown(f"**Focus:** {', '.join(contact.get('focus', []))}")

                st.markdown("**Notes:**")
                st.markdown(contact.get('notes', 'No notes available.'))
            else:
                st.info("No contacts recorded. Add your first contact using the 'Add Contact' tab.")

        # Add Contact Tab
        with contact_tabs[1]:
            with st.form("add_contact_form"):
                st.markdown("### Add New Contact")

                col1, col2 = st.columns(2)

                with col1:
                    name = st.text_input("Name")
                    title = st.text_input("Title")
                    firm = st.text_input("Firm")

                with col2:
                    email = st.text_input("Email")
                    phone = st.text_input("Phone")
                    focus = st.text_input("Focus Areas (comma separated)")

                notes = st.text_area("Notes")

                submitted = st.form_submit_button("Save Contact")

                if submitted:
                    # Process inputs
                    focus_list = [f.strip() for f in focus.split(',') if f.strip()]

                    # Create new contact
                    new_contact = {
                        'id': str(uuid.uuid4()),
                        'name': name,
                        'title': title,
                        'firm': firm,
                        'email': email,
                        'phone': phone,
                        'focus': focus_list,
                        'notes': notes,
                        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    # Add to session state
                    if 'contacts' not in st.session_state.ir_meetings:
                        st.session_state.ir_meetings['contacts'] = []

                    st.session_state.ir_meetings['contacts'].append(new_contact)
                    st.success("Contact added successfully!")


def generate_sample_data():
    """Generate sample data for demonstration"""
    # Sample meetings
    meetings = [
        {
            'id': '1',
            'title': 'Quarterly Update',
            'date': '2024-02-15',
            'firm': 'Capital Investments',
            'type': '1:1 Meeting',
            'attendees': ['John Smith', 'Sarah Johnson'],
            'notes': 'Discussed Q4 results and 2024 outlook. They were particularly interested in our margin expansion initiatives.',
            'questions': [
                'What are your capital allocation priorities?',
                'How do you view the competitive landscape?'
            ],
            'follow_up': True
        },
        {
            'id': '2',
            'title': 'ESG Strategy Overview',
            'date': '2024-01-20',
            'firm': 'Green Horizons Fund',
            'type': 'Group Meeting',
            'attendees': ['Michael Chen', 'Emma Davis'],
            'notes': 'Presented our ESG roadmap and sustainability goals. Positive reception to our carbon reduction targets.',
            'questions': [
                'What metrics are you using to track progress?',
                'How are you integrating ESG into executive compensation?'
            ],
            'follow_up': False
        },
        {
            'id': '3',
            'title': 'Investor Conference Presentation',
            'date': '2023-11-08',
            'firm': 'Multiple Firms',
            'type': 'Conference',
            'attendees': ['Various Investors'],
            'notes': 'Presented at the annual Tech Investors Conference. Good engagement during Q&A session.',
            'questions': [
                'How is AI being integrated into your products?',
                'What are your international expansion plans?'
            ],
            'follow_up': True
        }
    ]

    # Sample contacts
    contacts = [
        {
            'id': '1',
            'name': 'John Smith',
            'title': 'Portfolio Manager',
            'firm': 'Capital Investments',
            'email': 'john.smith@capital.example.com',
            'phone': '(555) 123-4567',
            'focus': ['Technology', 'Growth'],
            'notes': 'Long-term investor, holds 2% of our outstanding shares.'
        },
        {
            'id': '2',
            'name': 'Sarah Johnson',
            'title': 'Senior Analyst',
            'firm': 'Capital Investments',
            'email': 'sarah.johnson@capital.example.com',
            'phone': '(555) 123-4568',
            'focus': ['Technology', 'SaaS'],
            'notes': 'Technical background, asks detailed product questions.'
        },
        {
            'id': '3',
            'name': 'Michael Chen',
            'title': 'ESG Director',
            'firm': 'Green Horizons Fund',
            'email': 'mchen@greenhorizons.example.com',
            'phone': '(555) 987-6543',
            'focus': ['ESG', 'Sustainability'],
            'notes': 'Very focused on climate initiatives and diversity metrics.'
        },
        {
            'id': '4',
            'name': 'Emma Davis',
            'title': 'Analyst',
            'firm': 'Green Horizons Fund',
            'email': 'edavis@greenhorizons.example.com',
            'phone': '(555) 987-6544',
            'focus': ['ESG', 'Governance'],
            'notes': 'New to covering our company as of Q4 2023.'
        }
    ]

    return {
        'meetings': meetings,
        'contacts': contacts
    }