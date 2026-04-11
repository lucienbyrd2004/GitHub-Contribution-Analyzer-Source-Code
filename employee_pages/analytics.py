import streamlit as st
import queries
import plots

st.title("Section Analytics")
st.write("Run analytical tools on your assigned repositories.")

# Security check to ensure the user is actually logged in
if "user_info" not in st.session_state or not st.session_state.user_info:
    st.warning("Please log in to view this page.")
    st.stop()

user = st.session_state.user_info
user_id = user["id"]

try:
    # 1. Fetch live assigned sections from the database
    assigned_sections = queries.get_employee_sections(user_id)
    
    if not assigned_sections:
        st.warning("You must be assigned to a section to view analytics here. Check with your manager.")
    else:
        # 2. Build the dynamic dropdowns
        sec_options = {sec["name"]: sec["url"] for sec in assigned_sections}
        selected_sec_name = st.selectbox("Select a Section:", list(sec_options.keys()))
        repo_url = sec_options[selected_sec_name]
        
        st.write(f"**Target Repository:** [{repo_url}]({repo_url})")
        
        tool_choice = st.selectbox(
            "Choose an Analytical Tool:",
            [
                "Activity Histograms (Time/Day)",
                "Word Cloud (Commit Messages)",
                "Top Users Bar Chart (Repo)",
                "Sentiment Scatter Plot",
                "Machine Learning: Decision Tree"  # <-- ADD THIS LINE
            ]
        )

        # 3. Generate the graphs!
        if st.button("Generate Analysis"):
            github_username = user.get("github", "")
            
            # Group tools that require a personal GitHub username
            user_specific_tools = [
                "Activity Histograms (Time/Day)", 
                "Word Cloud (Commit Messages)", 
                "Sentiment Scatter Plot",
                "Machine Learning: Decision Tree"
            ]
            
            # Prevent crashing if the user forgot to add their GitHub username to their profile
            if tool_choice in user_specific_tools and not github_username:
                 st.error("Missing GitHub Username! Please go to your Dashboard and update your profile first.")
            else:
                with st.spinner(f"Generating {tool_choice}..."):
                    try:
                        # Route the request to the correct plots.py function
                        if tool_choice == "Activity Histograms (Time/Day)":
                            fig = plots.generate_histogram(github_username)
                            st.pyplot(fig)
                            
                        elif tool_choice == "Word Cloud (Commit Messages)":
                            fig = plots.generate_wordcloud(github_username)
                            st.pyplot(fig)
                            
                        elif tool_choice == "Sentiment Scatter Plot":
                            fig = plots.generate_sentiment_scatter(github_username)
                            st.pyplot(fig)
                            
                        elif tool_choice == "Top Users Bar Chart (Repo)":
                            # This one uses the Repo URL, not the individual user!
                            fig = plots.generate_top_users_barchart(repo_url)
                            st.pyplot(fig)
                            
                        elif tool_choice == "Machine Learning: Decision Tree":
                            fig = plots.generate_decision_tree(github_username)
                            st.pyplot(fig)
                            
                    except Exception as e:
                        st.error(f"Error generating plot: {e}")
                
except Exception as e:
    st.error(f"Failed to load analytics: {e}")