import streamlit as st
import queries
import plots  # We are finally hooking into your visualization file!

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
        st.warning("You must be assigned to a section to view analytics here. Use the Public Tools instead.")
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
                "Contribution Line Charts (Repo)",
                "Top Users Bar Chart (Repo)"
            ]
        )

        # 3. Generate the graphs!
        if st.button("Generate Analysis"):
            st.success(f"Running '{tool_choice}' for {selected_sec_name}...")
            
            if tool_choice == "Activity Histograms (Time/Day)":
                try:
                    # Your current git_parser expects a GitHub username. 
                    # Let's pull the logged-in employee's GitHub username from session state!
                    github_username = user.get("github", "")
                    
                    if not github_username:
                        st.error("Missing GitHub Username! Please go to your Dashboard and update your profile first.")
                    else:
                        with st.spinner(f"Fetching commit history for '{github_username}'..."):
                            # Call the function from plots.py
                            fig = plots.generate_histogram(github_username)
                            
                            # Streamlit function to draw the matplotlib figure
                            st.pyplot(fig)
                            
                except Exception as e:
                    st.error(f"Error generating plot: {e}")
                    
            else:
                st.info(f"The visualization logic for '{tool_choice}' needs to be built in plots.py next!")
                
except Exception as e:
    st.error(f"Failed to load analytics: {e}")