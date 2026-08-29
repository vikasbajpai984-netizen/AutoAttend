import streamlit as st 
from src.database.config import supabase
from src.database.db import enroll_student_to_subject

@st.dialog("Enroll in subject")
def enroll_subject():
    st.write("Enter the subject code")
    join_code = st.text_input("subject code", placeholder="E.g ICS301")
    if st.button("Enroll now", width='stretch', type="primary", icon = "▶️"):
        if join_code :
            res = supabase.table("subjects").select("sub_id", "name", "subject_code").eq("subject_code",join_code).execute()
            if res.data:
                subject = res.data[0]
                student_id = st.session_state.student_data["student_id"]
                check = supabase.table("student_subjects").select("*").eq("sub_id",subject["sub_id"]).eq("student_id", student_id).execute()
            if check.data:
                st.warning("Your are already enrolled in this subject")   
            else:
                enroll_student_to_subject(student_id, subject["sub_id"])
                st.success("You are successfully enrolled in the subject")
                import time 
                time.sleep(1)
                st.rerun()
        else:
            st.warning("Please fill the join code carefully", icon="‼️")
            
            
    
     