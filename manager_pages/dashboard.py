import streamlit as st
import pandas as pd
import queries

st.title("Manager Dashboard")

# Display a welcome message using the session state created in main.py
if "user_info" in st.session_state and st.session_state.user_info:
    st.write(f"Welcome back, **{st.session_state.user_info['name']}**!")

st.header("Company Statistics")

try:
    # 1. Fetch live data from the database via queries.py!
    all_employees = queries.get_all_employees()
    
    if not all_employees:
        st.info("No employees found in the database. Add some via the terminal or database directly!")
    else:
        # 2. Calculate dynamic metrics
        total = len(all_employees)
        managers = sum(1 for e in all_employees if e["role"] == "manager")
        developers = sum(1 for e in all_employees if e["role"] == "developer")
        
        # 3. Display Metric Cards
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Employees", total)
        col2.metric("Managers", managers)
        col3.metric("Developers", developers)
        
        st.divider()
        
        # 4. Display a searchable, sortable table of all employees
        st.subheader("Employee Directory")
        
        # Convert the list of dictionaries to a pandas DataFrame for a clean Streamlit table
        df = pd.DataFrame(all_employees)
        
        # Rename columns to look professional
        df = df.rename(columns={"id": "User ID", "name": "Name", "role": "Role"})
        
        # Capitalize the roles (e.g., 'manager' -> 'Manager')
        df['Role'] = df['Role'].str.title()
        
        # Display the dataframe
        st.dataframe(df, use_container_width=True, hide_index=True)
        
except Exception as e:
    st.error(f"Failed to load dashboard data: {e}")
    st.info("Make sure your database is running and connector.py has the right credentials.")

st.divider()

st.header("Quick Actions")
if st.button("Refresh Data"):
    st.rerun()