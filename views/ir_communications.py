import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import random

def run():
    company_name = {} if 'company_name' not in st.session_state else st.session_state['company_name']
    selected_quarter = {} if 'selected_quarter' not in st.session_state else st.session_state['selected_quarter']
    fiscal_year = {} if 'fiscal_year' not in st.session_state else st.session_state['fiscal_year']

    st.header(f"Shareholder Communications - {company_name}")

    # Initialize session states for IR communications
    if 'ir_emails' not in st.session_state:
        # Sample email data for demonstration
        st.session_state.ir_emails = generate_sample_emails()

    # Initialize email stats with default values
    if 'ir_email_stats' not in st.session_state:
        st.session_state.ir_email_stats = {
            'total_received': 0,
            'total_responded': 0,
            'avg_response_time': 0,
            'by_category': {},
            'by_sender_type': {}
        }

    # Make sure we have emails before updating stats
    if st.session_state.ir_emails:
        # Update stats
        update_email_stats()

    if 'ir_chatbot_conversations' not in st.session_state:
        st.session_state.ir_chatbot_conversations = []

    # Ensure current_response exists in session state
    if 'current_response' not in st.session_state:
        st.session_state.current_response = ""

    # Create tabs
    tab1, tab2 = st.tabs(["IR Inbox Manager", "IR Chat Bot"])

    # Tab 1: IR Inbox Manager
    with tab1:
        st.subheader("IR Email Management")

        try:
            # Email stats dashboard
            display_email_stats()

            # Email list/inbox view
            st.markdown("---")
            st.subheader("Inbox")

            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_status = st.selectbox(
                    "Status",
                    options=["All", "Unread", "Read", "Responded", "Flagged"],
                    index=0
                )

            with col2:
                filter_category = st.selectbox(
                    "Category",
                    options=["All", "Question", "Request", "Feedback", "Complaint", "Other"],
                    index=0
                )

            with col3:
                filter_time = st.selectbox(
                    "Time Period",
                    options=["All Time", "Today", "This Week", "This Month"],
                    index=0
                )

            # Apply filters to emails
            filtered_emails = filter_emails(
                st.session_state.ir_emails, 
                status=filter_status,
                category=filter_category,
                time_period=filter_time
            )

            # Display email list
            if filtered_emails:
                display_email_list(filtered_emails)
            else:
                st.info("No emails match the selected filters.")

            # Email compose section
            st.markdown("---")
            st.subheader("Compose New Email")

            with st.form("compose_email"):
                recipient = st.text_input("To")
                subject = st.text_input("Subject")
                message = st.text_area("Message", height=200)

                col1, col2 = st.columns([1, 5])
                with col1:
                    submitted = st.form_submit_button("Send Email")

                if submitted and recipient and subject and message:
                    # In a real app, this would send the email
                    st.success(f"Email sent to {recipient}")

                    # Add to sent items
                    sent_email = {
                        'id': f"email_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        'sender': f"ir@{company_name.lower().replace(' ', '')}.com",
                        'recipient': recipient,
                        'subject': subject,
                        'body': message,
                        'timestamp': datetime.now(),
                        'read': True,
                        'responded': True,
                        'category': 'Outgoing',
                        'sender_type': 'IR Team',
                        'flagged': False,
                        'response_time': 0
                    }

                    # In a real application, you'd probably store sent emails separately
                    # st.session_state.ir_emails.append(sent_email)
        except Exception as e:
            st.error(f"There was an error displaying the IR Inbox. Please refresh the page.")
            st.write("If the problem persists, please contact support.")

    # Tab 2: IR Chat Bot
    with tab2:
        st.subheader("IR Chat Bot")

        # Placeholder for now
        st.info("IR Chat Bot functionality is coming soon. This feature will provide an automated way for shareholders to get answers to common questions.")

        # Sample UI mockup
        st.markdown("### Chat Bot Configuration")

        st.toggle("Enable Chat Bot on Company Website", value=False)

        with st.expander("Configure Bot Knowledge Base"):
            st.write("Select documents and information to include in the chat bot's knowledge base:")

            st.checkbox("Company Financial Reports", value=True)
            st.checkbox("Earnings Call Transcripts", value=True)
            st.checkbox("Press Releases", value=True)
            st.checkbox("Investor Presentations", value=True)
            st.checkbox("SEC Filings", value=True)
            st.checkbox("FAQ Database", value=True)

            st.button("Update Knowledge Base")

        with st.expander("Bot Personality Settings"):
            st.slider("Formality Level", 1, 5, 3)
            st.slider("Detail Level", 1, 5, 3)
            st.radio("Bot Tone", ["Professional", "Friendly", "Balanced"])

        st.markdown("### Chat Bot Preview")

        st.markdown("""
        ```
        [Bot]: Welcome to the IR chat assistant for XYZ Corp. How can I help you today?

        [User]: What was your revenue last quarter?

        [Bot]: In Q2 FY2025, XYZ Corp reported revenue of $245.3 million, 
               a 12.5% increase compared to the same quarter last year. 
               Would you like more details about our financial performance?
        ```
        """)


def generate_sample_emails():
    """Generate sample email data for demonstration purposes"""
    sample_emails = []

    try:
        # Common IR email subjects and senders
        subjects = [
            "Question about quarterly dividend",
            "Investor seeking information on recent acquisition",
            "Request for annual report",
            "Query about voting rights",
            "Feedback on investor presentation",
            "Question about stock split",
            "Inquiry about executive compensation",
            "Request for investor call",
            "Question about ESG initiatives",
            "Shareholder resolution proposal"
        ]

        senders = [
            {"email": "john.investor@example.com", "name": "John Smith", "type": "Retail Investor"},
            {"email": "sarah.analyst@bigbank.com", "name": "Sarah Johnson", "type": "Analyst"},
            {"email": "michael.fund@capitalgroup.com", "name": "Michael Chen", "type": "Institutional Investor"},
            {"email": "emma.advisory@proxyservice.com", "name": "Emma Davis", "type": "Proxy Advisory"},
            {"email": "david.reporter@financenews.com", "name": "David Williams", "type": "Media"}
        ]

        # Generate 20 sample emails
        now = datetime.now()

        for i in range(20):
            # Randomly select attributes
            sender = random.choice(senders)
            subject = random.choice(subjects)

            # Randomize time within the last 30 days
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            timestamp = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

            # Randomize other properties
            is_read = random.random() > 0.3  # 70% chance of being read
            is_responded = is_read and random.random() > 0.4  # 60% chance of being responded if read
            is_flagged = random.random() > 0.8  # 20% chance of being flagged

            # Response time (if responded)
            response_time = None
            if is_responded:
                response_hours = random.randint(1, 48)  # Response within 1-48 hours
                response_time = response_hours

            # Categories
            categories = ["Question", "Request", "Feedback", "Complaint", "Other"]
            category = random.choice(categories)

            # Create email object
            email = {
                'id': f"email_{i}",
                'sender_email': sender["email"],
                'sender_name': sender["name"],
                'sender_type': sender["type"],
                'subject': subject,
                'body': f"This is a sample email body for the subject: {subject}. It's coming from {sender['name']} who is a {sender['type']}.",
                'timestamp': timestamp,
                'read': is_read,
                'responded': is_responded,
                'category': category,
                'flagged': is_flagged,
                'response_time': response_time
            }

            sample_emails.append(email)
    except Exception:
        # If there's an error with sample generation, create a basic email
        sample_emails = [{
            'id': "email_sample",
            'sender_email': "sample@example.com",
            'sender_name': "Sample User",
            'sender_type': "Investor",
            'subject': "Sample Email",
            'body': "This is a sample email to demonstrate the UI.",
            'timestamp': datetime.now(),
            'read': False,
            'responded': False,
            'category': "Question",
            'flagged': False,
            'response_time': None
        }]

    return sample_emails


def update_email_stats():
    """Update email statistics based on current emails"""
    # Initialize default stats
    default_stats = {
        'total_received': 0,
        'total_responded': 0,
        'avg_response_time': 0,
        'by_category': {},
        'by_sender_type': {}
    }

    # If ir_email_stats doesn't exist, create it with defaults
    if 'ir_email_stats' not in st.session_state:
        st.session_state.ir_email_stats = default_stats.copy()

    # Check if emails exist
    if 'ir_emails' not in st.session_state or not st.session_state.ir_emails:
        st.session_state.ir_email_stats = default_stats.copy()
        return

    try:
        emails = st.session_state.ir_emails

        # Basic stats
        total_received = len(emails)
        total_responded = sum(1 for email in emails if email.get('responded', False))

        # Calculate average response time
        response_times = [email.get('response_time') for email in emails 
                         if email.get('response_time') is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Stats by category
        categories = {}
        for email in emails:
            category = email.get('category', 'Other')
            if category not in categories:
                categories[category] = 0
            categories[category] += 1

        # Stats by sender type
        sender_types = {}
        for email in emails:
            sender_type = email.get('sender_type', 'Other')
            if sender_type not in sender_types:
                sender_types[sender_type] = 0
            sender_types[sender_type] += 1

        # Update stats in session state
        st.session_state.ir_email_stats = {
            'total_received': total_received,
            'total_responded': total_responded,
            'avg_response_time': avg_response_time,
            'by_category': categories,
            'by_sender_type': sender_types
        }
    except Exception:
        # If there's an error, use default values
        st.session_state.ir_email_stats = default_stats.copy()


def display_email_stats():
    """Display IR email statistics dashboard"""
    # Check if stats exist and create default if not
    if 'ir_email_stats' not in st.session_state or not st.session_state.ir_email_stats:
        st.session_state.ir_email_stats = {
            'total_received': 0,
            'total_responded': 0,
            'avg_response_time': 0,
            'by_category': {},
            'by_sender_type': {}
        }

    stats = st.session_state.ir_email_stats

    # Main metrics with error handling
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_received = stats.get('total_received', 0)
        st.metric("Total Emails", total_received)

    with col2:
        total_received = stats.get('total_received', 0)
        total_responded = stats.get('total_responded', 0)
        response_rate = (total_responded / total_received * 100) if total_received > 0 else 0
        st.metric("Response Rate", f"{response_rate:.1f}%")

    with col3:
        avg_time = stats.get('avg_response_time', 0)
        st.metric("Avg Response Time", f"{avg_time:.1f} hours")

    with col4:
        if 'ir_emails' in st.session_state:
            unread_count = sum(1 for email in st.session_state.ir_emails if not email.get('read', False))
        else:
            unread_count = 0
        st.metric("Unread Emails", unread_count)


def filter_emails(emails, status="All", category="All", time_period="All Time"):
    """Filter emails based on specified criteria"""
    try:
        if not emails:
            return []

        filtered = emails.copy()

        # Apply status filter
        if status != "All":
            if status == "Unread":
                filtered = [e for e in filtered if not e.get('read', False)]
            elif status == "Read":
                filtered = [e for e in filtered if e.get('read', False) and not e.get('responded', False)]
            elif status == "Responded":
                filtered = [e for e in filtered if e.get('responded', False)]
            elif status == "Flagged":
                filtered = [e for e in filtered if e.get('flagged', False)]

        # Apply category filter
        if category != "All":
            filtered = [e for e in filtered if e.get('category', '') == category]

        # Apply time period filter
        now = datetime.now()
        if time_period != "All Time":
            if time_period == "Today":
                today = now.date()
                filtered = [e for e in filtered if 'timestamp' in e and e['timestamp'].date() == today]
            elif time_period == "This Week":
                week_start = (now - timedelta(days=now.weekday())).date()
                filtered = [e for e in filtered if 'timestamp' in e and e['timestamp'].date() >= week_start]
            elif time_period == "This Month":
                month_start = datetime(now.year, now.month, 1).date()
                filtered = [e for e in filtered if 'timestamp' in e and e['timestamp'].date() >= month_start]

        return filtered
    except Exception:
        # If filtering fails, return empty list
        return []


def display_email_list(emails):
    """Display a list of emails with detail view"""
    try:
        # Display emails in a table format
        if not emails:
            st.info("No emails to display.")
            return

        email_df = pd.DataFrame([
            {
                'id': email['id'],
                'Sender': f"{email.get('sender_name', 'Unknown')} ({email.get('sender_type', 'Unknown')})",
                'Subject': email.get('subject', 'No Subject'),
                'Date': email['timestamp'].strftime("%b %d, %Y") if 'timestamp' in email else "Unknown",
                'Status': "Responded" if email.get('responded', False) else ("Read" if email.get('read', False) else "Unread")
            } for email in emails
        ])

        if not email_df.empty:
            # Show email list with selection
            st.dataframe(
                email_df[['Sender', 'Subject', 'Date', 'Status']],
                use_container_width=True,
                hide_index=True
            )

            # Display selected email
            st.markdown("### Email Viewer")

            # Check if there are any emails to select
            if emails:
                email_options = [email['id'] for email in emails]
                format_options = {x: next((f"{email.get('subject', 'Email')} - {email.get('sender_name', 'Unknown')}" 
                                for email in emails if email['id'] == x), "") for x in email_options}

                selected_email_id = st.selectbox(
                    "Select an email to view:",
                    options=email_options,
                    format_func=lambda x: format_options[x]
                )

                if selected_email_id:
                    selected_email = next((email for email in emails if email['id'] == selected_email_id), None)

                    if selected_email:
                        # Mark as read if it wasn't already
                        if not selected_email.get('read', False):
                            for email in st.session_state.ir_emails:
                                if email['id'] == selected_email_id:
                                    email['read'] = True

                        # Display email details
                        st.markdown(f"**From:** {selected_email.get('sender_name', 'Unknown')} ({selected_email.get('sender_email', 'Unknown')})")
                        st.markdown(f"**Type:** {selected_email.get('sender_type', 'Unknown')}")
                        st.markdown(f"**Subject:** {selected_email.get('subject', 'No Subject')}")

                        # Safely format timestamp
                        if 'timestamp' in selected_email:
                            time_str = selected_email['timestamp'].strftime('%B %d, %Y at %I:%M %p')
                        else:
                            time_str = "Unknown time"
                        st.markdown(f"**Received:** {time_str}")

                        # Display email body in a container
                        st.markdown("**Message:**")
                        st.markdown(f"""
                        <div style="border: 1px solid #ddd; padding: 15px; border-radius: 5px; background-color: white;">
                            {selected_email.get('body', 'No message content')}
                        </div>
                        """, unsafe_allow_html=True)

                        # Email actions
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            if st.button("Flag/Unflag", key=f"flag_{selected_email_id}"):
                                # Toggle flag status
                                for email in st.session_state.ir_emails:
                                    if email['id'] == selected_email_id:
                                        email['flagged'] = not email.get('flagged', False)
                                        flag_status = "flagged" if email['flagged'] else "unflagged"
                                        st.success(f"Email {flag_status}")

                        # Response section
                        if not selected_email.get('responded', False):
                            st.markdown("### Compose Response")

                            # Generate AI response button
                            if st.button("Generate AI Response"):
                                with st.spinner("Generating optimized response..."):
                                    time.sleep(2)  # Simulate AI processing

                                    # Sample AI-generated response
                                    ai_response = f"""
                                    Dear {selected_email.get('sender_name', 'Investor')},

                                    Thank you for your inquiry about {selected_email.get('subject', 'your question')}.

                                    [AI-generated response would appear here based on the email content and context]

                                    Please let me know if you have any further questions.

                                    Best regards,
                                    IR Team
                                    """

                                    st.session_state.current_response = ai_response

                            # Response editing area
                            response_text = st.text_area(
                                "Edit Response",
                                value=st.session_state.get('current_response', ''),
                                height=200
                            )

                            if st.button("Send Response"):
                                if response_text:
                                    # In a real app, this would send the email

                                    # Mark as responded
                                    for email in st.session_state.ir_emails:
                                        if email['id'] == selected_email_id:
                                            email['responded'] = True
                                            if 'timestamp' in email:
                                                email['response_time'] = (datetime.now() - email['timestamp']).total_seconds() / 3600  # hours
                                            else:
                                                email['response_time'] = 0

                                    # Update stats
                                    update_email_stats()

                                    st.success("Response sent successfully!")
                                    st.session_state.current_response = ""  # Clear current response
                                else:
                                    st.error("Please enter a response message")
                        else:
                            st.info("This email has already been responded to.")
            else:
                st.info("No emails to display.")
        else:
            st.info("No emails to display.")
    except Exception as e:
        st.error("An error occurred while displaying emails. Please refresh the page.")