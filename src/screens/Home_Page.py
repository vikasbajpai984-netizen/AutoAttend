import streamlit as st 
from src.components.Header_home import header_home
from src.ui.base_style import style_background_home , base_style_layout, style_background_dashboard
from src.components.Footer import footer_home


def Home_Page():
    header_home()
    style_background_home()
    base_style_layout()
    style_background_dashboard()

   
    col1,col2 = st.columns(2,gap="large")
    with col1:
        st.header("I'am Teacher")
        st.image("https://i.ibb.co/CsmQQV6X/mascot-teacher.png",width=145)
        if st.button("Login as Teacher",type="primary",icon="↗️"):
            st.session_state['login_type'] = 'Teacher'
            st.rerun()
    with col2:
        st.header("I'am Student")
        st.image("https://i.ibb.co/844D9Lrt/mascot-student.png",width=120)
        if st.button("Login as student",type="primary", icon="↗️"):
            st.session_state['login_type'] = 'Student'
            st.rerun()
                    
    footer_home()