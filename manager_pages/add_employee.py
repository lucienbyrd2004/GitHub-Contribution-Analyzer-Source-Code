import streamlit as st
import queries

st.title("Add New Employee")
st.write("Create a new employee and generate their login credentials.")

with st.form("add_user_form"):
    st.subheader("Employee Details")
    name = st.text_input("Full Name")
    github = st.text_input("GitHub Username")
    role = st.selectbox("Company Role", ["developer", "manager", "hr", "intern"])
    
    st.divider()
    
    st.subheader("Login Credentials")
    username = st.text_input("System Username")
    password = st.text_input("System Password", type="password")
    
    submitted = st.form_submit_button("Create Employee")
    
    if submitted:
        if name and github and username and password:
            try:
                # Calls the database function to insert into Users and Login tables
                success = queries.createUserQuery(name, github, role, username, password)
                if success:
                    st.success(f"Successfully created account for {name}!")
                else:
                    st.error("Failed to create user.")
            except Exception as e:
                # Catches errors like duplicate usernames if you set that rule in SQL
                st.error(f"Database error: {e}")
        else:
            st.error("Please fill out all fields before submitting.")