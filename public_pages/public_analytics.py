import streamlit as st
import git_parser
import plots

st.title("Public GitHub Analytics")
st.write("Access analytical tools without an assigned section.")

# Use a single input for either a username or a full repository URL
target_input = st.text_input("Enter a Public GitHub Repository URL or Username:")

tool_choice = st.selectbox(
    "Choose an Analytical Tool:",
    [
        "Activity Histograms (Time/Day)",
        "Word Cloud (Commit Messages)",
        "Top Users Bar Chart (Repo)",
        "Sentiment Scatter Plot",
        "Machine Learning: Decision Tree"
    ]
)

if st.button("Generate Analysis"):
    if not target_input:
        st.error("Please enter a valid GitHub URL or Username.")
    else:
        with st.spinner(f"Fetching data for '{target_input}'..."):
            try:
                # 1. Figure out if they typed a URL or just a username
                username = target_input.strip()
                repo_url = target_input.strip()

                # If they pasted a full URL, parse it to extract the username
                if "github.com" in target_input:
                    url_type, owner, repo = git_parser.parse_github_url(target_input)
                    username = owner 
                    
                # 2. Route the request to the correct plots.py function
                if tool_choice == "Activity Histograms (Time/Day)":
                    fig = plots.generate_histogram(username)
                    st.pyplot(fig)
                    
                elif tool_choice == "Word Cloud (Commit Messages)":
                    fig = plots.generate_wordcloud(username)
                    st.pyplot(fig)
                    
                elif tool_choice == "Sentiment Scatter Plot":
                    fig = plots.generate_sentiment_scatter(username)
                    st.pyplot(fig)
                    
                elif tool_choice == "Top Users Bar Chart (Repo)":
                    # This specific tool requires a full repository URL
                    if "github.com" not in repo_url or len(repo_url.split('/')) < 4:
                        st.error("The Bar Chart requires a full repository URL (e.g., https://github.com/user/repo).")
                    else:
                        fig = plots.generate_top_users_barchart(repo_url)
                        st.pyplot(fig)

                        # ... other elif blocks ...
                elif tool_choice == "Machine Learning: Decision Tree":
                    fig = plots.generate_decision_tree(username)
                    st.pyplot(fig)
                        
            except ValueError as ve:
                # This catches the errors we set up in plots.py (like "No recent activity found")
                st.error(f"Data Error: {ve}")
            except Exception as e:
                st.error(f"Failed to generate plot: {e}")