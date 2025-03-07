import streamlit as st
import pandas as pd
from datetime import datetime

def run():
    company_name = {} if 'company_name' not in st.session_state else st.session_state['company_name']
    selected_quarter = {} if 'selected_quarter' not in st.session_state else st.session_state['selected_quarter']
    fiscal_year = {} if 'fiscal_year' not in st.session_state else st.session_state['fiscal_year']

    st.header(f"Analyst Coverage - {company_name} {selected_quarter} FY{fiscal_year}")

    # Initialize session state for analyst coverage if not exists
    if 'analyst_coverage_data' not in st.session_state:
        st.session_state.analyst_coverage_data = []

    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Analyst Directory", "Rating History", "Price Targets"])

    # Tab 1: Analyst Directory
    with tab1:
        st.subheader("Analyst Directory")

        # Form to add new analyst
        with st.form("add_analyst"):
            col1, col2 = st.columns(2)

            with col1:
                analyst_name = st.text_input("Analyst Name")
                firm_name = st.text_input("Firm Name")
                email = st.text_input("Email")

            with col2:
                phone = st.text_input("Phone")
                current_rating = st.selectbox(
                    "Current Rating", 
                    ["Buy", "Overweight", "Hold", "Underweight", "Sell", "Not Rated"]
                )
                price_target = st.number_input("Price Target ($)", min_value=0.0, step=0.5)

            notes = st.text_area("Notes")

            submit_button = st.form_submit_button("Add Analyst")
            if submit_button and analyst_name and firm_name:
                # Create a unique ID for the analyst
                analyst_id = f"{analyst_name}_{firm_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

                new_analyst = {
                    "id": analyst_id,
                    "name": analyst_name,
                    "firm": firm_name,
                    "email": email,
                    "phone": phone,
                    "current_rating": current_rating,
                    "price_target": price_target,
                    "notes": notes,
                    "last_updated": datetime.now().strftime("%Y-%m-%d")
                }

                st.session_state.analyst_coverage_data.append(new_analyst)
                st.success(f"Added analyst: {analyst_name} from {firm_name}")

        # Display existing analysts
        if st.session_state.analyst_coverage_data:
            st.markdown("### Current Analyst Coverage")

            # Convert to DataFrame for display
            analysts_df = pd.DataFrame(st.session_state.analyst_coverage_data)
            display_cols = ["name", "firm", "current_rating", "price_target", "last_updated"]

            if not analysts_df.empty:
                st.dataframe(
                    analysts_df[display_cols],
                    use_container_width=True,
                    hide_index=True
                )

                # Allow user to select an analyst to view or edit
                selected_analyst_idx = st.selectbox(
                    "Select analyst to view/edit details:",
                    options=range(len(st.session_state.analyst_coverage_data)),
                    format_func=lambda i: f"{st.session_state.analyst_coverage_data[i]['name']} ({st.session_state.analyst_coverage_data[i]['firm']})"
                )

                # Show analyst details
                selected_analyst = st.session_state.analyst_coverage_data[selected_analyst_idx]

                with st.expander("Analyst Details", expanded=True):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Name:** {selected_analyst['name']}")
                        st.write(f"**Firm:** {selected_analyst['firm']}")
                        st.write(f"**Email:** {selected_analyst['email']}")
                        st.write(f"**Phone:** {selected_analyst['phone']}")

                    with col2:
                        st.write(f"**Current Rating:** {selected_analyst['current_rating']}")
                        st.write(f"**Price Target:** ${selected_analyst['price_target']}")
                        st.write(f"**Last Updated:** {selected_analyst['last_updated']}")

                    st.write(f"**Notes:**")
                    st.write(selected_analyst['notes'])

                    # Delete button
                    if st.button("Delete Analyst"):
                        st.session_state.analyst_coverage_data.pop(selected_analyst_idx)
                        st.success(f"Deleted analyst: {selected_analyst['name']}")
                        st.rerun()
        else:
            st.info("No analyst coverage data added yet. Use the form above to add analysts.")

    # Tab 2: Rating History
    with tab2:
        st.subheader("Rating History")

        # Initialize rating history if not exists
        if 'rating_history' not in st.session_state:
            st.session_state.rating_history = []

        # Form to add a rating change
        with st.form("add_rating_change"):
            col1, col2 = st.columns(2)

            # Get list of analysts
            analyst_options = []
            if st.session_state.analyst_coverage_data:
                analyst_options = [(a["id"], f"{a['name']} ({a['firm']})") for a in st.session_state.analyst_coverage_data]

            with col1:
                selected_analyst_id = st.selectbox(
                    "Select Analyst",
                    options=[a[0] for a in analyst_options],
                    format_func=lambda x: next((a[1] for a in analyst_options if a[0] == x), ""),
                    disabled=not analyst_options
                ) if analyst_options else None

                change_date = st.date_input("Date of Change")

            with col2:
                previous_rating = st.selectbox(
                    "Previous Rating", 
                    ["Buy", "Overweight", "Hold", "Underweight", "Sell", "Not Rated", "Initiated"]
                )

                new_rating = st.selectbox(
                    "New Rating", 
                    ["Buy", "Overweight", "Hold", "Underweight", "Sell", "Not Rated", "Dropped"]
                )

            col1, col2 = st.columns(2)
            with col1:
                previous_target = st.number_input("Previous Price Target ($)", min_value=0.0, step=0.5)
            with col2:
                new_target = st.number_input("New Price Target ($)", min_value=0.0, step=0.5)

            notes = st.text_area("Notes on Rating Change")

            submit_button = st.form_submit_button("Add Rating Change")
            if submit_button and selected_analyst_id:
                # Find analyst name and firm
                analyst_info = next((a for a in st.session_state.analyst_coverage_data if a["id"] == selected_analyst_id), None)

                if analyst_info:
                    new_rating_change = {
                        "id": f"rating_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "analyst_id": selected_analyst_id,
                        "analyst_name": analyst_info["name"],
                        "firm": analyst_info["firm"],
                        "change_date": change_date.strftime("%Y-%m-%d"),
                        "previous_rating": previous_rating,
                        "new_rating": new_rating,
                        "previous_target": previous_target,
                        "new_target": new_target,
                        "notes": notes
                    }

                    st.session_state.rating_history.append(new_rating_change)

                    # Update the analyst's current rating and price target
                    for analyst in st.session_state.analyst_coverage_data:
                        if analyst["id"] == selected_analyst_id:
                            analyst["current_rating"] = new_rating
                            analyst["price_target"] = new_target
                            analyst["last_updated"] = change_date.strftime("%Y-%m-%d")

                    st.success(f"Added rating change for {analyst_info['name']}")

        # Display rating history
        if st.session_state.rating_history:
            st.markdown("### Rating Change History")

            # Convert to DataFrame for display
            history_df = pd.DataFrame(st.session_state.rating_history)
            display_cols = ["change_date", "analyst_name", "firm", "previous_rating", "new_rating", "previous_target", "new_target"]

            # Sort by date (newest first)
            history_df = history_df.sort_values(by="change_date", ascending=False)

            st.dataframe(
                history_df[display_cols],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No rating history data yet. Use the form above to add rating changes.")

    # Tab 3: Price Targets
    with tab3:
        st.subheader("Price Target Trends")

        # Display price target statistics
        if st.session_state.analyst_coverage_data:
            analysts_df = pd.DataFrame(st.session_state.analyst_coverage_data)

            if not analysts_df.empty and "price_target" in analysts_df.columns:
                # Calculate statistics
                avg_price_target = analysts_df["price_target"].mean()
                median_price_target = analysts_df["price_target"].median()
                min_price_target = analysts_df["price_target"].min()
                max_price_target = analysts_df["price_target"].max()

                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Average Target", f"${avg_price_target:.2f}")
                col2.metric("Median Target", f"${median_price_target:.2f}")
                col3.metric("Low Target", f"${min_price_target:.2f}")
                col4.metric("High Target", f"${max_price_target:.2f}")

                # Count ratings by category
                if "current_rating" in analysts_df.columns:
                    rating_counts = analysts_df["current_rating"].value_counts()

                    st.markdown("### Rating Distribution")

                    # Create rating chart
                    rating_data = {
                        "Buy/Overweight": rating_counts.get("Buy", 0) + rating_counts.get("Overweight", 0),
                        "Hold": rating_counts.get("Hold", 0),
                        "Sell/Underweight": rating_counts.get("Sell", 0) + rating_counts.get("Underweight", 0),
                        "Not Rated": rating_counts.get("Not Rated", 0)
                    }

                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Buy/Overweight", rating_data["Buy/Overweight"])
                    col2.metric("Hold", rating_data["Hold"])
                    col3.metric("Sell/Underweight", rating_data["Sell/Underweight"])
                    col4.metric("Not Rated", rating_data["Not Rated"])

                    # Display firms with highest and lowest price targets
                    st.markdown("### Highest & Lowest Price Targets")

                    if len(analysts_df) >= 1:
                        highest_target = analysts_df.loc[analysts_df["price_target"].idxmax()]
                        st.write(f"**Highest:** ${highest_target['price_target']:.2f} - {highest_target['name']} ({highest_target['firm']}) - {highest_target['current_rating']}")

                    if len(analysts_df) >= 2:
                        lowest_target = analysts_df.loc[analysts_df["price_target"].idxmin()]
                        st.write(f"**Lowest:** ${lowest_target['price_target']:.2f} - {lowest_target['name']} ({lowest_target['firm']}) - {lowest_target['current_rating']}")

                    # CSV export option
                    if st.button("Export Analyst Coverage to CSV"):
                        csv_data = analysts_df.to_csv(index=False).encode('utf-8')

                        st.download_button(
                            label="Download CSV",
                            data=csv_data,
                            file_name=f"{company_name}_analyst_coverage_{datetime.now().strftime('%Y%m%d')}.csv",
                            mime="text/csv"
                        )
        else:
            st.info("No analyst coverage data available yet. Add analysts in the Analyst Directory tab.")