import streamlit as st 
from src.components.Footer import footer_dashboard
from src.components.enroll_in_subject_dialog import enroll_subject
from src.database.db import unenroll_student_to_subject
from src.components.Header_home import Header_dashboard
from src.ui.base_style import style_background_home , base_style_layout, style_background_dashboard
import numpy as np
from PIL import Image
from src.pipelines.facepipeline import predict_attendence, get_face_embeddings, train_classifier
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance
from src.pipelines.voicepipeline import get_voice_embeddings
from src.database.config import supabase
from src.components.subject_card import subject_card




def student__dashboard():
    student_data = st.session_state.student_data
    student_id = student_data["student_id"]
    col1,col2 = st.columns(2,vertical_alignment="center",gap="xxlarge")
    with col1:
        Header_dashboard()
    with col2:
        st.subheader(f"""Welcome, {student_data["name"]}!""")
        if st.button("Logout",type="secondary",icon="↩️", key ="back_to_home" ,shortcut="control+backspace"):
            st.session_state["is_logged_in"] = False       
            del st.session_state.student_data 
            st.rerun()
            
        st.space()
    c1, c2 = st.columns(2)
    with c1:
        st.header("Your enrolled subjects")
    with c2:
        if st.button("Enroll in subject", type="primary", width='stretch', key = "enroll to subject"):
            enroll_subject()
    st.divider()    
    with st.spinner("Loading your subjects ⏳..."):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)
        print(logs)
    stats_map = {}
    for log in logs:
        sid = log["sub_id"]
        if sid not in stats_map:
            stats_map[sid] = {"Total":0,"Attended":0}
        stats_map[sid]["Total"] += 1 
        if log.get('is_present'):
            stats_map[sid]["Attended"] +=1
            
    cols = st.columns(2)
    for i , sub_node in enumerate(subjects):
        sub = sub_node["subjects"]  
        sid = sub["sub_id"]  
        
        stats = stats_map.get(sid, {"Total":0,"Attended":0})
        def unenroll_button():
            if st.button ("Unenroll from this course" , type = "tertiary", icon=":material/delete_forever:", key = f" {i}unenroll this course"):
                unenroll_student_to_subject(student_id, sid)
                st.toast(f"You unenrolled from {sub["name"]} successfully")
                st.rerun()
        
        with cols[i%2]:
           
            subject_card(
                name = sub["name"],
                code = sub["subject_code"],
                section = sub["section"],
                stats = [
                    ('📆', 'Total', stats['Total']),
                    ('☑️', 'Attended', stats['Attended'])
                ],
                
                footer_callback=unenroll_button
            )
            
    footer_dashboard()

def Student_Dashboard():
    style_background_dashboard()
    base_style_layout()
    
    

    if "student_data" in st.session_state:
        student__dashboard()
        return
        
        
        
        
    col1,col2 = st.columns(2,vertical_alignment="center",gap="xxlarge")
    with col1:
        Header_dashboard()
    with col2:
        st.button("Back To Home",type="secondary",icon="↩️", key ="back_to_home" ,on_click=lambda : st.session_state.update({'login_type':None}), shortcut="control+backspace")
        
    st.header("Login Using Face-Id",text_alignment="center")
    st.space()
    st.space()
    show_registration = False
    photo_source = st.camera_input("Position Your Face in the center")
    if photo_source :
        img = np.array(Image.open(photo_source))
        with st.spinner("Scanning..."):
            detected , all_ids , num_faces = predict_attendence(img) 
           
            if num_faces == 0 :
                st.warning("Face Not Found")
            elif num_faces > 1:
                st.warning("Multiple Faces Found")
            else:
               
                if detected :
                    
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students() 
                    student = next((s for s in all_students if s["student_id"] == student_id),None)
                    
                    if student :
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = "student"
                        st.session_state.student_data = student
                        st.toast(f"Welcome Back {student["name"]}")
                        import time
                        time.sleep(1)
                        st.rerun()
                    
                    
                    
                    
                else:
                        st.info("Face not recognized! You might be a new student.")
                        show_registration = True
                
    if show_registration:
                with st.container(border=True):
                    st.header("Register new profile")
                    new_name = st.text_input("Enter your name", placeholder="E.g Vikas Bajpai")
                    st.subheader("optional : Voice Enrollment")
                    st.info("Enroll your voice for voice only attendance")
                    audio_data = None
                    try:
                        audio_data = st.audio_input("Record a short phrase like I am present, My name is Vikas")
                        
                    except Exception as e :
                        st.error(f"Audio data failed!{e}")
                        
                    if st.button("Create Account", type = "primary"):
                        if new_name:
                            with st.spinner("Creating Profile..."):
                                img = np.array(Image.open(photo_source))
                                encodings = get_face_embeddings(img)
                                if encodings:
                                    face_embd = encodings[0].tolist()
                                    voice_embd = None
                                    if audio_data:
                                        voice_embd = get_voice_embeddings(audio_data.getvalue())
                                        
                                    response_data = create_student(new_name, face_embeddings=face_embd, voice_embeddings=voice_embd)
                                    
                                    if response_data:
                                        train_classifier()
                                        st.session_state.is_logged_in = True
                                        st.session_state.user_role = "student"
                                        st.session_state.student_data = response_data
                                        st.toast(f"Profile created, Hi {new_name}")
                                        import time
                                        time.sleep(1)
                                        st.rerun()
                                else:
                                    st.error("Couldn't capture your facial features")    
                        else:
                            st.warning("Please Enter name")
    footer_dashboard()
    
    