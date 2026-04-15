import streamlit as st
import queries

st.title("Manage Repository Sections")

# Create the three tabs
tab1, tab2, tab3 = st.tabs(["Create Section", "Assign Employees", "View Sections"])

# --- TAB 1: CREATE SECTION ---
with tab1:
    st.subheader("Create a New Section")
    sec_name = st.text_input("Section Name (e.g., 'Frontend Team Alpha')")
    repo_url = st.text_input("GitHub Repository URL")
    
    if st.button("Create Section"):
        if sec_name and repo_url:
            try:
                queries.createSectionQuery(repo_url, sec_name)
                st.success(f"Section '{sec_name}' created successfully in the database!")
            except Exception as e:
                st.error(f"Error creating section: {e}")
        else:
            st.error("Please provide both a name and a repository URL.")

# --- TAB 2: ASSIGN EMPLOYEES ---
with tab2:
    st.subheader("Assign Employee to Section")
    
    # Fetch live data to populate dropdown menus
    all_employees = queries.get_all_employees()
    all_sections = queries.get_all_sections()
    
    if not all_sections:
        st.warning("No sections exist yet. Create one first.")
    elif not all_employees:
        st.warning("No employees exist in the database.")
    else:
        # Create dictionaries mapping the friendly labels to the actual database IDs
        emp_options = {f"{e['name']} (ID: {e['id']}) - {e['role']}": e['id'] for e in all_employees}
        sec_options = {f"{s['name']}": s['id'] for s in all_sections}
        
        # Display Dropdowns
        selected_emp_label = st.selectbox("Select Employee", list(emp_options.keys()))
        selected_sec_label = st.selectbox("Select Target Section", list(sec_options.keys()))
        
        if st.button("Assign User"):
            # Get the actual IDs from the dictionaries
            emp_id = emp_options[selected_emp_label]
            sec_id = sec_options[selected_sec_label]
            
            try:
                queries.addUserToSection(emp_id, sec_id)
                st.success(f"Successfully assigned {selected_emp_label.split(' ')[0]} to {selected_sec_label}!")
            except Exception as e:
                # If they try to add someone already in the section, the DB will reject it
                st.error(f"Failed to assign user. They might already be assigned to this section. (Error: {e})")

# --- TAB 3: VIEW & EDIT SECTIONS ---
with tab3:
    st.subheader("Current Sections")
    
    # Fetch all sections from the database
    all_sections = queries.get_all_sections()
    
    if not all_sections:
        st.info("No sections available in the database.")
    else:
        for sec in all_sections:
            # Create an interactive dropdown block for each section
            with st.expander(f"{sec['name']} - {sec['url']}"):
                st.write("**Assigned Members:**")
                
                # Fetch members specifically assigned to this section
                members = queries.get_section_members(sec['id'])
                
                if not members:
                    st.write("No members assigned yet.")
                else:
                    for member in members:
                        col1, col2 = st.columns([3, 1])
                        col1.write(f"- {member['name']} (ID: {member['id']})")
                        
                        # Button to remove a user from this specific section
                        if col2.button("Remove User", key=f"rem_{sec['id']}_{member['id']}"):
                            try:
                                queries.deleteUserSection(member['id'], sec['id'])
                                st.success(f"Removed {member['name']}.")
                                st.rerun() # Instantly refresh UI
                            except Exception as e:
                                st.error(f"Failed to remove user: {e}")
                
                st.divider()
                
                # Button to delete the entire section
                if st.button("Delete Entire Section", key=f"del_sec_{sec['id']}", type="primary"):
                    try:
                        queries.deleteSection(sec['name'], sec['id'])
                        st.success("Section deleted.")
                        st.rerun() # Instantly refresh UI
                    except Exception as e:
                        st.error(f"Failed to delete section: {e}")