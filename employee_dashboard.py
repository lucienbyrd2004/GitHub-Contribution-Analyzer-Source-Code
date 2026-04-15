# import streamlit
import streamlit as st

# title of app
st.title("company employee system")

# short description
st.write("employee management dashboard")

# session storage

# store employees if not created yet
if "employees" not in st.session_state:
    st.session_state.employees = [
        {"name": "jabril", "id": "100", "role": "manager"},
        {"name": "Debbie", "id": "200", "role": "developer"},
        {"name": "Sabir", "id": "300", "role": "hr"}
    ]

# store logged in user
if "user" not in st.session_state:
    st.session_state.user = None


# validation functions

# check name
def validate_name(name):
    return name.strip() != ""

# check id
def validate_id(emp_id):
    return emp_id.isdigit()

# check role
def validate_role(role):
    roles = ["manager", "developer", "hr", "intern"]
    return role in roles


# login function

# find employee by id
def login_user(emp_id):

    for emp in st.session_state.employees:
        if emp["id"] == emp_id:
            return emp

    return None


# login page

if st.session_state.user is None:

    st.header("login")

    emp_id = st.text_input("enter employee id")

    # login button
    if st.button("login"):

        user = login_user(emp_id)

        if user:
            st.session_state.user = user
            st.success("login successful")
            st.rerun()

        else:
            st.error("employee not found")


# dashboard section

else:

    user = st.session_state.user

    st.write("logged in as:", user["name"])

    # logout button
    if st.button("logout"):
        st.session_state.user = None
        st.rerun()


    # employee dashboard

    if user["role"] != "manager":

        st.header("employee dashboard")

        st.subheader("edit your info")

        new_name = st.text_input("change name", value=user["name"])
        new_id = st.text_input("change id", value=user["id"])

        # update button
        if st.button("update info"):

            if not validate_name(new_name):
                st.error("name cannot be empty")

            elif not validate_id(new_id):
                st.error("id must be numbers")

            else:
                user["name"] = new_name
                user["id"] = new_id

                st.success("info updated")


    # manager dashboard

    if user["role"] == "manager":

        st.header("manager dashboard")

        # statistics section

        st.subheader("employee statistics")

        total = len(st.session_state.employees)

        managers = sum(1 for e in st.session_state.employees if e["role"] == "manager")
        developers = sum(1 for e in st.session_state.employees if e["role"] == "developer")
        hr = sum(1 for e in st.session_state.employees if e["role"] == "hr")
        interns = sum(1 for e in st.session_state.employees if e["role"] == "intern")

        # display stats
        st.write("total employees:", total)
        st.write("managers:", managers)
        st.write("developers:", developers)
        st.write("hr:", hr)
        st.write("interns:", interns)


        # add employee

        st.subheader("add employee")

        name = st.text_input("employee name")
        emp_id = st.text_input("employee id")

        role = st.selectbox(
            "role",
            ["manager", "developer", "hr", "intern"]
        )

        if st.button("add employee"):

            if not validate_name(name):
                st.error("name cannot be empty")

            elif not validate_id(emp_id):
                st.error("id must be numbers")

            else:

                st.session_state.employees.append({
                    "name": name,
                    "id": emp_id,
                    "role": role
                })

                st.success("employee added")


        # search and filter

        st.subheader("search employees")

        search_name = st.text_input("search by name")

        role_filter = st.selectbox(
            "filter by role",
            ["all", "manager", "developer", "hr", "intern"]
        )


        # filter employees
        filtered_employees = st.session_state.employees

        # apply name search
        if search_name:
            filtered_employees = [
                e for e in filtered_employees
                if search_name.lower() in e["name"].lower()
            ]

        # apply role filter
        if role_filter != "all":
            filtered_employees = [
                e for e in filtered_employees
                if e["role"] == role_filter
            ]


        # employee list

        st.subheader("employee list")

        for i, emp in enumerate(filtered_employees):

            with st.expander(f"{emp['name']} (id: {emp['id']})"):

                st.write("role:", emp["role"])

                # edit employee
                new_name = st.text_input(
                    "edit name",
                    value=emp["name"],
                    key=f"name{i}"
                )

                new_id = st.text_input(
                    "edit id",
                    value=emp["id"],
                    key=f"id{i}"
                )

                new_role = st.selectbox(
                    "edit role",
                    ["manager", "developer", "hr", "intern"],
                    index=["manager","developer","hr","intern"].index(emp["role"]),
                    key=f"role{i}"
                )

                # update button
                if st.button("update employee", key=f"update{i}"):

                    if validate_name(new_name) and validate_id(new_id):

                        emp["name"] = new_name
                        emp["id"] = new_id
                        emp["role"] = new_role

                        st.success("employee updated")

                # delete button
                if st.button("delete employee", key=f"delete{i}"):

                    st.session_state.employees.remove(emp)
                    st.rerun()