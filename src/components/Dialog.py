import streamlit as st 
from src.database.db import create_subject

@st.dialog("Create new subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the details of new subject")
    sub_id = st.text_input("Subject Code", placeholder="E.g INC201")
    sub_name = st.text_input("Subject Name", placeholder="E.g Python Programming")
    sub_section = st.text_input("Batch Name", placeholder="A")
    
    if st.button("Create Now", type = "primary", width="stretch"):
        if sub_id and sub_name and sub_section:
            try : 
                create_subject(sub_id, sub_name, sub_section, teacher_id)
                st.toast("Subject Created Successfully", icon="✅")
                st.rerun()
            except Exception as e :
                st.error(f"Error {str(e)}")
                
    else :
        st.warning("Please fill all fields")