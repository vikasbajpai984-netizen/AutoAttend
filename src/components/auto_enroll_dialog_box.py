import streamlit as st 
from src.database.config import supabase
from src.database.db import enroll_student_to_subject


@st.dialog("Quick Enrollment")
def auto_enroll_dialog(subject_code):
    
    
    student_id = st.session_state.student_data["student_id"]
    res = supabase.table("subjects").select("sub_id , name").eq("subject_code", subject_code).execute()
    
    if not res.data:
        st.error("Subject Not Found")
        if st.button("close"):
            st.query_params.clear()
            st.rerun()
        return
    subject = res.data[0]
    check = supabase.table("student_subjects").select("*").eq("sub_id",subject["sub_id"]).eq("student_id", student_id).execute()
    if check.data:
        st.info("You are already enrolled!")
        if st.button("Got it"):
            st.query_params.clear()
            st.rerun()
        return
    st.markdown(f"Would you like to enroll in **{subject["name"]}** ?")
    c1 , c2 = st.columns(2)
    with c1:
        if st.button("No thanks", key="no",type = "secondary"):
            st.query_params.clear()
            st.rerun()
    with c2:
        if st.button("Yes Enroll Now", type = "primary", width='stretch', key= "enroll"):
            enroll_student_to_subject(student_id, subject["sub_id"])
            st.success("Joined Successfully")
            st.query_params.clear()
            import time 
            time.sleep(2)
            st.rerun()