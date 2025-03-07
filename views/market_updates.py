import streamlit as st
import json
from datetime import datetime

def run():
    company_name = {} if 'company_name' not in st.session_state else st.session_state['company_name']
    openai_client = st.session_state['openai_client']
    st.header(f"Market Updates - {company_name}")

    # Create tabs for Market Updates section - adding Peers as first tab
    mu_tab0, mu_tab1, mu_tab2, mu_tab3 = st.tabs(["Peers", "Market News", "Peer Updates", "Industry Analysis"])

    # Peers Tab
    with mu_tab0:
        st.subheader("Peer Analysis")

        # Add peer generation controls
        with st.expander("Peer Selection Criteria", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                market_cap_range = st.slider(
                    "Market Cap Range ($B)",
                    min_value=0.0,
                    max_value=100.0,
                    value=(1.0, 50.0),
                    key="peer_market_cap"
                )
                industry_options = ["Technology", "Consumer Discretionary", "Retail", "E-commerce", "Fashion"]
                selected_industries = st.multiselect(
                    "Industry Focus",
                    industry_options,
                    default=["Retail", "E-commerce"],
                    key="peer_industries"
                )

            with col2:
                min_shared_analysts = st.slider(
                    "Minimum Shared Analysts",
                    min_value=0,
                    max_value=20,
                    value=3,
                    key="min_analysts"
                )
                min_shared_investors = st.slider(
                    "Minimum Shared Investors",
                    min_value=0,
                    max_value=50,
                    value=5,
                    key="min_investors"
                )

        # Button to generate peers
        if st.button("Generate Peer Set", key="generate_peers"):
            with st.spinner("Analyzing peer companies..."):
                prompt = f"""Based on the following criteria, generate a detailed analysis of 5-7 public company peers for {company_name}:
                - Market Cap Range: ${market_cap_range[0]}B to ${market_cap_range[1]}B
                - Industries: {', '.join(selected_industries)}
                - Minimum shared analysts: {min_shared_analysts}
                - Minimum shared investors: {min_shared_investors}

                Return the analysis in this exact JSON format:
                {{
                    "peers": [
                        {{
                            "name": "Company Name",
                            "ticker": "TICK",
                            "market_cap": "$XXB",
                            "industry": "Primary Industry",
                            "shared_analysts": X,
                            "shared_investors": X,
                            "business_model_similarities": "Description...",
                            "competitive_positioning": "Analysis..."
                        }}
                    ]
                }}"""

                try:
                    response = openai_client.chat.completions.create(
                        model="gpt-4-turbo-preview",
                        messages=[
                            {"role": "system",
                             "content": "You are a financial analyst expert. Always return data in the exact JSON format specified."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        response_format={"type": "json_object"}
                    )

                    peers_data = json.loads(response.choices[0].message.content)

                    if 'peers' not in peers_data:
                        st.error("Invalid response format from AI. Please try again.")
                    else:
                        st.session_state.peers_data = peers_data

                        # Display peer analysis results
                        st.subheader("Generated Peer Set")

                        # Create metrics summary
                        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                        with metrics_col1:
                            st.metric("Total Peers", len(peers_data['peers']))
                        with metrics_col2:
                            avg_market_cap = sum(float(peer['market_cap'].replace('$', '').replace('B', ''))
                                                 for peer in peers_data['peers']) / len(peers_data['peers'])
                            st.metric("Average Peer Market Cap", f"${avg_market_cap:.1f}B")
                        with metrics_col3:
                            total_shared_investors = sum(peer['shared_investors'] for peer in peers_data['peers'])
                            st.metric("Total Shared Investors", total_shared_investors)

                        # Display detailed peer information
                        for peer in peers_data['peers']:
                            with st.expander(f"{peer['name']} ({peer['ticker']})"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Market Cap:** {peer['market_cap']}")
                                    st.markdown(f"**Industry:** {peer['industry']}")
                                    st.markdown(f"**Shared Analysts:** {peer['shared_analysts']}")
                                with col2:
                                    st.markdown(f"**Shared Investors:** {peer['shared_investors']}")
                                    st.markdown("**Business Model Similarities:**")
                                    st.markdown(peer['business_model_similarities'])

                                st.markdown("**Competitive Positioning:**")
                                st.markdown(peer['competitive_positioning'])

                except Exception as e:
                    st.error(f"Error generating peer analysis: {str(e)}")
                    st.error("Raw response: " + str(response.choices[0].message.content))

        # Show previously generated peers if they exist
        elif 'peers_data' in st.session_state and 'peers' in st.session_state.peers_data:
            st.subheader("Current Peer Set")

            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
            with metrics_col1:
                st.metric("Total Peers", len(st.session_state.peers_data['peers']))
            with metrics_col2:
                avg_market_cap = sum(float(peer['market_cap'].replace('$', '').replace('B', ''))
                                     for peer in st.session_state.peers_data['peers']) / len(
                    st.session_state.peers_data['peers'])
                st.metric("Average Peer Market Cap", f"${avg_market_cap:.1f}B")
            with metrics_col3:
                total_shared_investors = sum(peer['shared_investors'] for peer in st.session_state.peers_data['peers'])
                st.metric("Total Shared Investors", total_shared_investors)

            for peer in st.session_state.peers_data['peers']:
                with st.expander(f"{peer['name']} ({peer['ticker']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Market Cap:** {peer['market_cap']}")
                        st.markdown(f"**Industry:** {peer['industry']}")
                        st.markdown(f"**Shared Analysts:** {peer['shared_analysts']}")
                    with col2:
                        st.markdown(f"**Shared Investors:** {peer['shared_investors']}")
                        st.markdown("**Business Model Similarities:**")
                        st.markdown(peer['business_model_similarities'])

                    st.markdown("**Competitive Positioning:**")
                    st.markdown(peer['competitive_positioning'])

    # Market News Tab
    with mu_tab1:
        st.subheader("Market News")

        # Create tabs for different news categories
        news_tab1, news_tab2, news_tab3, news_tab4 = st.tabs(
            ["Executive Summary", "Company News", "Peer News", "Industry News"])

        # Executive Summary tab
        with news_tab1:
            st.subheader("Executive Summary")

            # Add date selector and generate button
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_date = st.date_input(
                    "Select Week",
                    datetime.now().date(),
                    key="summary_date"
                )
            with col2:
                if st.button("Generate New Summary"):
                    try:
                        # Generate a comprehensive weekly summary using GPT-4
                        summary_prompt = f"""Create a comprehensive weekly market summary for {company_name} for the week ending {selected_date}.
                        Include:
                        1. Key company events and announcements
                        2. Notable peer activities and their implications
                        3. Major industry developments
                        4. Stock performance analysis (company and peers)

                        Format the response as JSON:
                        {{
                            "date": "YYYY-MM-DD",
                            "company_events": ["event1", "event2"],
                            "peer_events": ["event1", "event2"],
                            "industry_events": ["event1", "event2"],
                            "performance_data": {{
                                "company": {{"1w": -2.3, "6m": 15.4, "52w": 28.7}},
                                "peer_avg": {{"1w": -1.8, "6m": 12.1, "52w": 22.3}}
                            }}
                        }}"""

                        response = openai_client.chat.completions.create(
                            model="gpt-4-turbo-preview",
                            messages=[
                                {"role": "system",
                                 "content": "You are an IR professional creating executive summaries."},
                                {"role": "user", "content": summary_prompt}
                            ],
                            temperature=0.7,
                            response_format={"type": "json_object"}
                        )

                        new_summary = json.loads(response.choices[0].message.content)
                        if 'weekly_summaries' not in st.session_state:
                            st.session_state.weekly_summaries = {}
                        st.session_state.weekly_summaries[selected_date.strftime('%Y-%m-%d')] = new_summary
                        st.success("New summary generated!")
                    except Exception as e:
                        st.error(f"Error generating weekly summary: {str(e)}")

            # Display the summary if available
            selected_summary_date = selected_date.strftime('%Y-%m-%d')
            if 'weekly_summaries' in st.session_state and selected_summary_date in st.session_state.weekly_summaries:
                summary = st.session_state.weekly_summaries[selected_summary_date]

                # Create three columns for performance metrics
                met_col1, met_col2, met_col3 = st.columns(3)

                with met_col1:
                    st.metric(
                        label="1-Week Performance",
                        value=f"{summary['performance_data']['company']['1w']}%",
                        delta=f"{summary['performance_data']['company']['1w'] - summary['performance_data']['peer_avg']['1w']:.1f}% vs peers"
                    )

                with met_col2:
                    st.metric(
                        label="6-Month Performance",
                        value=f"{summary['performance_data']['company']['6m']}%",
                        delta=f"{summary['performance_data']['company']['6m'] - summary['performance_data']['peer_avg']['6m']:.1f}% vs peers"
                    )

                with met_col3:
                    st.metric(
                        label="52-Week Performance",
                        value=f"{summary['performance_data']['company']['52w']}%",
                        delta=f"{summary['performance_data']['company']['52w'] - summary['performance_data']['peer_avg']['52w']:.1f}% vs peers"
                    )

                # Display events in expandable sections
                with st.expander("Company Events", expanded=True):
                    for event in summary['company_events']:
                        st.markdown(f"• {event}")

                with st.expander("Peer Activities", expanded=True):
                    for event in summary['peer_events']:
                        st.markdown(f"• {event}")

                with st.expander("Industry Developments", expanded=True):
                    for event in summary['industry_events']:
                        st.markdown(f"• {event}")

                # Export options
                st.subheader("Export Options")
                exp_col1, exp_col2 = st.columns(2)

                with exp_col1:
                    if st.button("📧 Export as Email"):
                        company_events = "\n".join(['• ' + event for event in summary['company_events']])
                        peer_events = "\n".join(['• ' + event for event in summary['peer_events']])
                        industry_events = "\n".join(['• ' + event for event in summary['industry_events']])

                        email_text = f"""Weekly Market Summary for {company_name}
                            Week Ending: {selected_date}

                            COMPANY EVENTS:
                            {company_events}

                            PEER ACTIVITIES:
                            {peer_events}

                            INDUSTRY DEVELOPMENTS:
                            {industry_events}

                            PERFORMANCE METRICS:
                            • 1-Week: {summary['performance_data']['company']['1w']}% (Peer avg: {summary['performance_data']['peer_avg']['1w']}%)
                            • 6-Month: {summary['performance_data']['company']['6m']}% (Peer avg: {summary['performance_data']['peer_avg']['6m']}%)
                            • 52-Week: {summary['performance_data']['company']['52w']}% (Peer avg: {summary['performance_data']['peer_avg']['52w']}%)"""

                        st.code(email_text, language="text")
                        st.info("Email text copied to clipboard!")

                with exp_col2:
                    if st.button("📥 Download Summary"):
                        # Create download link
                        company_events = "\n".join(['- ' + event for event in summary['company_events']])
                        peer_events = "\n".join(['- ' + event for event in summary['peer_events']])
                        industry_events = "\n".join(['- ' + event for event in summary['industry_events']])

                        download_str = f"""# Weekly Market Summary - {company_name}
                        Week Ending: {selected_date}

                        ## Performance Metrics
                        - 1-Week: {summary['performance_data']['company']['1w']}% (vs peer avg: {summary['performance_data']['peer_avg']['1w']}%)
                        - 6-Month: {summary['performance_data']['company']['6m']}% (vs peer avg: {summary['performance_data']['peer_avg']['6m']}%)
                        - 52-Week: {summary['performance_data']['company']['52w']}% (vs peer avg: {summary['performance_data']['peer_avg']['52w']}%)

                        ## Company Events
                        {company_events}

                        ## Peer Activities
                        {peer_events}

                        ## Industry Developments
                        {industry_events}"""
                        st.download_button(
                            label="Download as Text",
                            data=download_str,
                            file_name=f"market_summary_{selected_date}.txt",
                            mime="text/plain"
                        )
            else:
                st.info("No summary available for selected week. Click 'Generate New Summary' to create one.")

        # Company News tab
        with news_tab2:
            st.subheader(f"{company_name} News")

            # Generate company-specific news using AI
            try:
                company_prompt = f"""Generate 5 recent, realistic market news items for {company_name}.
                Include varied news types (earnings, operations, strategy, market performance, analyst coverage).
                Format exactly as JSON:
                {{
                    "news_items": [
                        {{
                            "headline": "Title of the news item",
                            "date": "YYYY-MM-DD",
                            "summary": "2-3 sentence summary of the news",
                            "source": "Name of news source",
                            "link": "https://example.com/news",
                            "category": "News category (e.g., Earnings, Strategy, etc.)"
                        }}
                    ]
                }}"""

                response = openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are a financial news analyst providing market updates."},
                        {"role": "user", "content": company_prompt}
                    ],
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )

                company_news = json.loads(response.choices[0].message.content)

                # Display company news
                for news in company_news['news_items']:
                    with st.container():
                        st.markdown(f"### {news['headline']}")
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"*{news['date']}* - {news['source']}")
                            st.markdown(news['summary'])
                        with col2:
                            st.markdown(f"**Category:** {news['category']}")
                            st.markdown(f"[Read More]({news['link']})")
                        st.markdown("---")

            except Exception as e:
                st.error(f"Error generating company news: {str(e)}")

        # Peer News tab
        with news_tab3:
            st.subheader("Peer Company News")

            # Check if peers have been generated
            if 'peers_data' in st.session_state and 'peers' in st.session_state.peers_data:
                peers = st.session_state.peers_data['peers']

                # Create a multiselect to filter which peers to show news for
                selected_peers = st.multiselect(
                    "Select peers to show news for:",
                    options=[f"{peer['name']} ({peer['ticker']})" for peer in peers],
                    default=[f"{peer['name']} ({peer['ticker']})" for peer in peers[:3]]
                )

                if selected_peers:
                    try:
                        peers_prompt = f"""Generate 2 recent, realistic market news items for each of these companies: {', '.join(selected_peers)}.
                        Format exactly as JSON:
                        {{
                            "news_items": [
                                {{
                                    "company": "Company Name (TICK)",
                                    "headline": "Title",
                                    "date": "YYYY-MM-DD",
                                    "summary": "2-3 sentence summary",
                                    "source": "Source Name",
                                    "link": "https://example.com"
                                }}
                            ]
                        }}"""

                        response = openai_client.chat.completions.create(
                            model="gpt-4-turbo-preview",
                            messages=[
                                {"role": "system",
                                 "content": "You are a financial news analyst providing market updates."},
                                {"role": "user", "content": peers_prompt}
                            ],
                            temperature=0.7,
                            response_format={"type": "json_object"}
                        )

                        peer_news = json.loads(response.choices[0].message.content)

                        for news in peer_news['news_items']:
                            with st.container():
                                st.markdown(f"## {news['company']}")
                                st.markdown(f"### {news['headline']}")
                                st.markdown(f"*{news['date']}* - {news['source']}")
                                st.markdown(news['summary'])
                                st.markdown(f"[Read More]({news['link']})")
                                st.markdown("---")

                    except Exception as e:
                        st.error(f"Error generating peer news: {str(e)}")
            else:
                st.info("Please generate peer companies in the Peers tab first.")

        # Industry News tab
        with news_tab4:
            st.subheader("Industry News")

            # Get industries either from peer selection or default set
            if 'peer_industries' in st.session_state:
                industries = st.session_state.peer_industries
            else:
                industries = ["Retail", "E-commerce"]  # Default industries

            try:
                industry_prompt = f"""Generate 3 recent, realistic market news items for these industries: {', '.join(industries)}.
                Include major trends, market shifts, and regulatory updates.
                Format exactly as JSON:
                {{
                    "news_items": [
                        {{
                            "industry": "Industry Name",
                            "headline": "Title",
                            "date": "YYYY-MM-DD",
                            "summary": "2-3 sentence summary",
                            "source": "Source Name",
                            "link": "https://example.com",
                            "impact": "Brief description of industry impact"
                        }}
                    ]
                }}"""

                response = openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are a financial news analyst providing market updates."},
                        {"role": "user", "content": industry_prompt}
                    ],
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )

                industry_news = json.loads(response.choices[0].message.content)

                # Group news by industry
                news_by_industry = {}
                for news in industry_news['news_items']:
                    if news['industry'] not in news_by_industry:
                        news_by_industry[news['industry']] = []
                    news_by_industry[news['industry']].append(news)

                # Display news grouped by industry
                for industry, news_items in news_by_industry.items():
                    st.markdown(f"## {industry}")
                    for news in news_items:
                        with st.container():
                            st.markdown(f"### {news['headline']}")
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"*{news['date']}* - {news['source']}")
                                st.markdown(news['summary'])
                            with col2:
                                st.markdown("**Industry Impact:**")
                                st.markdown(news['impact'])
                            st.markdown(f"[Read More]({news['link']})")
                            st.markdown("---")

            except Exception as e:
                st.error(f"Error generating industry news: {str(e)}")