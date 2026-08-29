import streamlit as st

from src.screens.Home_Page import Home_Page
from src.screens.Student_Dashboard import Student_Dashboard
from src.screens.Teacher_Dashboard import Teacher_Dashboard
from src.components.auto_enroll_dialog_box import auto_enroll_dialog

def main():
    st.set_page_config(
        page_title='Auto Attend - Making Attendance faster using AI',
        page_icon="https://i.ibb.co/YTYGn5qV/logo.png"
    )
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None
    
    match st.session_state['login_type']:
        case 'Teacher':
            Teacher_Dashboard()
        case 'Student':
            Student_Dashboard()
        case None:
            Home_Page()

    join_code = st.query_params.get("join-code") 
    if join_code :
        
        if st.session_state["login_type"]!= 'Student':
            st.session_state['login_type'] = 'Student'
            st.rerun()

        if st.session_state.get("is_logged_in") and st.session_state.get('user_role') == "student":
            auto_enroll_dialog(join_code)
            
            
main()