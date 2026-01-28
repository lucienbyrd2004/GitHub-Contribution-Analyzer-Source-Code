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

#basic page configuration function 
st.set_page_config(
    page_title="Manager dashboard",
    page_icon="🧊",
    layout="wide",
)
st.title("Manager dashboard")

#side bar option menu 
with st.sidebar:
    selected=option_menu(
        menu_title="git operations",
        options=["Create New Section","Edit Section","list all sections","Edit user Info","Analyze repo"],
        icons=["Activity","house-heart-fill","calendar2-heart-fill","6-square-fill","align-bottom","alexa"],
        menu_icon="cake",
        default_index=0
        
    )
    
