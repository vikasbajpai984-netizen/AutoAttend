import streamlit as st 
from src.pipelines.voicepipeline import process_bulk_audio
from src.database.config import supabase
from datetime import datetime
import pandas as pd
from src.components.attendance_result_dialog import show_attendance_result
@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):
    st.write("Record audio of students saying I am present")
    audio_data = None
    audio_data = st.audio_input("Record classroom audio")
    
    if st.button("Analyze Audio", width='stretch', type = 'primary'):
        with st.spinner("System is recognizing the Voice..."):
            enrolled_res = supabase.table("student_subjects").select("*, students(*)").eq('sub_id', selected_subject_id).execute()
            enrolled_students = enrolled_res.data
        
            
            if  not enrolled_students :
                st.warning("No Student in this course")
                return
            candidate_dict = {
                s['students']['student_id'] : s['students']['voice_embeddings']
                for s in enrolled_students if s['students'].get('voice_embeddings')
            }
            
            if not candidate_dict :
                st.error("No enrolled student has resistered voice profiles ❌ ")  
                st.rerun()  
            audio_bytes = audio_data.getvalue()
            
            detected_score = process_bulk_audio(audio_bytes, candidate_dict)
            
            results, attendance_to_log = [],[]
            current_timestampz = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            for node in enrolled_students:
                student = node['students']
                score = detected_score.get(student['student_id'], 0.0)
                is_present = bool(score>0)
                
                results.append({
                    "Name":student["name"],
                    "Id":student["student_id"],
                    "Source":score if is_present else "-",
                    "Status":"✅ Present" if is_present else "❌ Absent"
                    
                })
                attendance_to_log.append({
                    "timestamps" : current_timestampz,
                    "student_id" : student["student_id"],
                    "sub_id" : selected_subject_id,
                    "is_present" : bool(is_present)
                })
        
            
            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)
    if st.session_state.get('voice_attendance_results'):
        st.divider()
        df_defaults, logs = st.session_state.voice_attendance_results
        show_attendance_result(df_defaults, logs)

