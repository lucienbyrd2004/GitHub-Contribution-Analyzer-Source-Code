import streamlit as st
import queries  # Now seamlessly connected to your database!

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="GitHub Contribution Analyzer", page_icon="📊", layout="wide")

# --- INITIALIZE SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# --- LOGIN & LOGOUT LOGIC ---
def login(username, password):
    # Call the database to verify credentials
    user_data = queries.verify_login(username, password)
    
    if user_data:
        st.session_state.logged_in = True
        st.session_state.user_role = user_data["role"]
        st.session_state.user_info = user_data
        return True
    return False

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_info = None

# --- DEFINE PAGES ---
# Login Page definition
def login_page():
    st.title("System Login")
    st.write("Welcome to the GitHub Contribution Analyzer.")
    
    # Updated to capture actual DB credentials
    username = st.text_input("Enter Username:")
    password = st.text_input("Enter Password:", type="password")
    
    if st.button("Login"):
        if login(username, password):
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password.")
            
    st.divider()
    st.write("Not an employee? You can still use the public analytics tools via the sidebar.")

# Define Streamlit Pages mapped to your file structure
login_view = st.Page(login_page, title="Login", icon="🔑")

# Public Pages
public_analytics = st.Page("public_pages/public_analytics.py", title="Public Analytics", icon="📈")

# Manager Pages
manager_dashboard = st.Page("manager_pages/dashboard.py", title="Manager Dashboard", icon="🏢")
manager_sections = st.Page("manager_pages/section_manage.py", title="Manage Sections", icon="📁")
manager_add_emp = st.Page("manager_pages/add_employee.py", title="Add Employees", icon="➕")


# Employee Pages
employee_dashboard = st.Page("employee_pages/dashboard.py", title="My Dashboard", icon="👤")
employee_analytics = st.Page("employee_pages/analytics.py", title="Section Analytics", icon="📊")

# --- ROUTING LOGIC ---
# Determine which pages to show based on login status and role
if not st.session_state.logged_in:
    # General User / Not Logged In
    pg = st.navigation({
        "Authentication": [login_view],
        "Public Tools": [public_analytics]
    })
else:
    # Route based on the role retrieved from the database
    if st.session_state.user_role == "manager":
        pg = st.navigation({
            "Manager Portal": [manager_dashboard, manager_sections, manager_add_emp],
            "Public Tools": [public_analytics]
        })
    else: 
        # Employee / Developer / HR / Intern
        pg = st.navigation({
            "Employee Portal": [employee_dashboard, employee_analytics],
            "Public Tools": [public_analytics]
        })

# --- RENDER APP ---
# Show logout button in sidebar if logged in
if st.session_state.logged_in:
    with st.sidebar:
        st.write(f"Logged in as: **{st.session_state.user_info['name']}**")
        if st.button("Logout"):
            logout()
            st.rerun()

# Run the navigation page
pg.run()