import streamlit as st 
from src.components.Header_home import Header_teacher_dashboard
from src.ui.base_style import style_background_home , base_style_layout, style_background_dashboard
def Teacher_Dashboard():
    Header_teacher_dashboard()
    style_background_dashboard()
    base_style_layout()
    st.header("Teacher Dashboard")
    