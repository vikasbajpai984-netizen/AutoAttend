import streamlit as st

from src.screens.Home_Page import Home_Page
from src.screens.Student_Dashboard import Student_Dashboard
from src.screens.Teacher_Dashboard import Teacher_Dashboard

def main():
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None
     
    match st.session_state['login_type']:
        case 'Teacher':
            Teacher_Dashboard()
        case 'Student':
            Student_Dashboard()
        case None:
            Home_Page()
            
main()