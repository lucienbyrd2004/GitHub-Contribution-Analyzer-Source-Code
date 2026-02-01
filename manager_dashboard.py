"""
first test for github-contribution-analyzer manager login home page

installation needed:
pip install streamlit
pip install streamlit-option-menu
"""

#libraries and modules used

import streamlit as st 
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu

#page configuration function 
st.set_page_config(
    page_title="Manager dashboard",
    page_icon="🧊",
    layout="wide",
)
st.title("Manager dashboard")

#page list section
pages = [
    st.Page("manager_pages/pg_analyze_repo.py", title="Analyze repository", icon=None),
    st.Page("manager_pages/pg_create_new_section.py", title="Create a new section", icon=None),
    st.Page("manager_pages/pg_list_sections.py", title="List all Sections", icon=None),
    st.Page("manager_pages/pg_edit_section.py", title="Edit section", icon=None),
    st.Page("manager_pages/pg_edit_user_info.py", title="Edit user info", icon=None),
]

pg = st.navigation(pages, position="sidebar", expanded= True)
pg.run()

    
