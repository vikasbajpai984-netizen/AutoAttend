import streamlit as st 
from src.components.Footer import footer_dashboard
from src.components.Header_home import Header_dashboard
from src.ui.base_style import style_background_home , base_style_layout, style_background_dashboard
from src.database.db import check_teacher_existance, create_teacher, teacher_login, get_teacher_subject, get_attendance_for_teacher
from src.components.Dialog import create_subject_dialog
from src.components.subject_card import subject_card
from src.components.share_subject import share_subject
from src.components.Add_photos_dialog import Add_photos_dialog
import numpy as np
from src.pipelines.facepipeline import predict_attendence
from src.database.config import supabase
from datetime import datetime
import pandas as pd
from src.components.attendance_result_dialog import attendance_result_dialog
from src.components.voice_attendance_dialog import voice_attendance_dialog
def Teacher_Dashboard():
    
    style_background_dashboard()
    base_style_layout()
    
    if 'teacher_data' in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in  st.session_state or st.session_state.teacher_login_type == "login":
        teacher_dashboard_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_dashboard_resister()
        
               
def teacher_dashboard():
    teacher_data = st.session_state.teacher_data 
    col1,col2 = st.columns(2,vertical_alignment="center",gap="xxlarge")
    with col1:
        Header_dashboard()
    with col2:
        st.subheader(f"""Welcome, {teacher_data["name"]}!""")
        if st.button("Logout",type="secondary",icon="↩️", key ="back_to_home" ,shortcut="control+backspace"):
            st.session_state["is_logged_in"] = False       
            del st.session_state.teacher_data 
            st.rerun()
            
        st.space()
        
        
    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = "Take_Attendance"
    tab1, tab2, tab3 = st.columns(3)
    
    with tab1:
        type1= "primary" if st.session_state.current_teacher_tab=="Take_Attendance" else "tertiary"
        if st.button("Take Attendance", width = "stretch", icon=":material/ar_on_you:", type=type1):
            st.session_state.current_teacher_tab = "Take_Attendance"
            st.rerun()
    with tab2:
        type2= "primary" if st.session_state.current_teacher_tab=="Manage_Subjects" else "tertiary"
        if st.button("Manage Subjects", width = "stretch", icon=":material/book_ribbon:", type=type2 ):
            st.session_state.current_teacher_tab = "Manage_Subjects"
            st.rerun()
    with tab3:
        type3= "primary" if st.session_state.current_teacher_tab=="Attendance_Records" else "tertiary"
        if st.button("Attendance Records", width = 'stretch', icon=":material/cards_stack:", type=type3):
            st.session_state.current_teacher_tab = "Attendance_Records"
            st.rerun()
    
    st.divider()
    
    if st.session_state.current_teacher_tab == 'Take_Attendance':
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == 'Manage_Subjects':
        teacher_tab_Manage_Subjects()
    if st.session_state.current_teacher_tab == 'Attendance_Records':
        teacher_tab_Attendance_Records()
        
    footer_dashboard() 


def teacher_tab_take_attendance():
    
    teacher_id = st.session_state.teacher_data["teacher_id"]
    st.header("Take Ai attendance")
    if "attendance_images" not in st.session_state:
        st.session_state.attendance_images = []
    
    subjects = get_teacher_subject(teacher_id)
    if not subjects:
        st.warning("You haven't created any subject yet!\nPlease create the subject first")  
        return

    subject_options = {f"{s['name']} - {s['subject_code']}" : s['sub_id'] for s in subjects}
    col1, col2 = st.columns([3,1], vertical_alignment='bottom')
    with col1 :
        selected_subject_label = st.selectbox('Select Subject', options = list(subject_options.keys()))
    with col2:
        if st.button('Add Photos', type = 'primary', icon = ":material/monochrome_photos:", key = "add"):
            Add_photos_dialog()
        
    selected_subject_id = subject_options[selected_subject_label]
    st.divider()
    
    if st.session_state.attendance_images:
        st.header("Added Photos")
        gallery_cols = st.columns(4)
        for indx , img in enumerate(st.session_state.attendance_images):
            with gallery_cols[indx%4]:
                st.image(img, width = 'stretch', caption = f"Photo {indx + 1}")
    col1, col2, col3 = st.columns(3)
    has_photos = bool(st.session_state.attendance_images)
    with col1 :
        if st.button("Clear Photos", width = 'stretch', type = "tertiary", icon = ":material/delete:", disabled=not has_photos) :
            st.session_state.attendance_images = []  
            st.rerun()
    
    with col2 :
        
        if st.button("Run Face Analysis", width = 'stretch', type = "secondary", icon = ":material/analytics:", disabled= not has_photos) :
            with st.spinner("Deep scanning..."):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendence(img_np)
                    
                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)
                            
                            all_detected_ids.setdefault(student_id,[]).append(f"Photo {idx+1}")  
                
                enrolled_res = supabase.table("student_subjects").select("*, students(*)").eq('sub_id', selected_subject_id).execute()
                enrolled_students = enrolled_res.data
                if  not enrolled_students :
                    st.warning("No Student in this course")
                else :
                    
                    results, attendance_to_log = [],[]
                    current_timestampz = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    for node in enrolled_students:
                        student = node['students']
                        source = all_detected_ids.get(int(student['student_id']), [])
                        is_present = len(source)>0
                        
                        results.append({
                            "Name":student["name"],
                            "Id":student["student_id"],
                            "Source":",".join(source) if is_present else "-",
                            "Status":"✅ Present" if is_present else "❌ Absent"
                            
                        })
                        attendance_to_log.append({
                            "timestamps" : current_timestampz,
                            "student_id" : student["student_id"],
                            "sub_id" : selected_subject_id,
                            "is_present" : bool(is_present)
                        })
                
                attendance_result_dialog(pd.DataFrame(results), attendance_to_log)
    
    with col3 :
        if st.button('Use Voice Attendance', type = "primary", width = 'stretch', icon = ':material/mic:'):
            voice_attendance_dialog(selected_subject_id)
        
        
        
        
        
        
        
        
        
            
def teacher_tab_Manage_Subjects():
    teacher_id = st.session_state.teacher_data["teacher_id"]
    col1, col2 = st.columns(2)
    with col1:
        st.header("Manage Subjects")
    with col2:
        if st.button("Create new subject", width = 'stretch'):
            create_subject_dialog(teacher_id)  

    # listing all subjects 

    subjects = get_teacher_subject(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("👥", "Students", sub["total_students"]),
                ("📚", "Classes", sub ["total_classes"])
            ]
            def share_btn():
                if st.button(f"Share Code: {sub["name"]}", key = f"Share Code: {sub["subject_code"]}", icon = ":material/share:"):
                    share_subject(sub["name"], sub["subject_code"])
                    st.space()
            subject_card (
                name = sub["name"],
                code = sub["subject_code"],
                section = sub["section"],
                stats = stats,
                footer_callback = share_btn
            )
    else :
        st.info("NO SUBJECT FOUND. CREATE A NEW ONE ABOVE")            
        
    
    
def teacher_tab_Attendance_Records():
    st.header("Attendance Records")
    teacher_id = st.session_state.teacher_data['teacher_id']
    
    records = get_attendance_for_teacher(teacher_id)

    if not records :
        return
    
    data = []  
    for r in records:
        
        ts = r.get('timestamps')
        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Time":datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M%p") if ts else "N.A",
            "Subject": r['subjects']['name'],
            "Subject Code": r['subjects']['subject_code'],
            "is_present":bool(r.get('is_present', False))
        })
    df = pd.DataFrame(data)
    
    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code' ])
        .agg(
            present_count = ('is_present', 'sum'),
            Total_count = ('is_present', 'count')
        ).reset_index()
        
    )
    summary['Attendance States'] = (
        "✅ " + summary['present_count'].astype(str) + " /" + summary['present_count'].astype(str)+' Students'
    )
   
    display_df = ( summary.sort_values(by='ts_group', ascending = False)
                 [['Time', 'Subject', 'Subject Code', 'Attendance States' ]]
                 )
    st.dataframe(display_df, width = 'stretch', hide_index=True)
    
    
def login_teacher(username, password):
    if not username or not password:
        return False
    teacher = teacher_login(username, password)
    
    if teacher:
        st.session_state.user_role = "teacher"
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    
    
    return False
    
    
    
def register_teacher(teacher_username, teacher_name, teacher_password, teacher_password_confirm):
    if not teacher_username or not teacher_name or not teacher_password or not teacher_password_confirm:
        return False, "All fields are required!"
    if check_teacher_existance(teacher_username):
        return False, "Username already taken!"
    if teacher_password != teacher_password_confirm:
        return False, "Password does not match!"
    try:   
        create_teacher(teacher_username, teacher_password, teacher_name)
        return True , "Successfully Registered, Login Now!"
    except Exception as  e:
        return False,f"Uexpected error:{e}"
    
    
    
def teacher_dashboard_login():
    col1,col2 = st.columns(2,vertical_alignment="center",gap="xxlarge")
    with col1:
        Header_dashboard()
    with col2:
        st.button("Back To Home",type="secondary",icon="↩️", key ="back_to_home" ,on_click=lambda : st.session_state.update({'login_type':None}), shortcut="control+backspace")
    st.header("Login as teacher",text_alignment="left")
    st.space()
    teacher_username = st.text_input("Enter your username",placeholder="vikas bajpai")
    teacher_password = st.text_input("Enter your password",placeholder="********",type="password")
    st.divider()
    c1,c2 = st.columns(2,vertical_alignment="center",gap="xxlarge")
    with c1:
         if st.button("Login",type="secondary", icon=":material/passkey:",key = "login_button", shortcut="control+enter",  width="stretch") :
            if login_teacher(teacher_username, teacher_password):
                st.toast("Welcome back!", icon="👋") 
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid Username or Password")
    with c2:
       if  st.button("Register instead",type="primary", icon=":material/passkey:",key = "register_button", width="stretch") :
           st.session_state.teacher_login_type = "register"
           st.rerun()
    st.space()   
    footer_dashboard() 
    
    
def teacher_dashboard_resister():
    col1,col2 = st.columns(2,vertical_alignment="center",gap="xxlarge")
    with col1:
        Header_dashboard()
    with col2:
        st.button("Back To Home",type="secondary",icon="↩️", key ="backtohome",on_click=lambda : st.session_state.update({'login_type':None}), shortcut="control+backspace")
    st.header("Register as teacher")
    st.space()
    teacher_username = st.text_input("Enter your username",placeholder="vikasbajpai")
    teacher_name = st.text_input("Enter your name",placeholder="Vikas Bajpai")
    teacher_password = st.text_input("Enter your password",placeholder="********",type="password")
    teacher_password_confirm = st.text_input("Confirm your password",placeholder="********",type="password")
    st.divider()
    c1,c2 = st.columns(2,vertical_alignment="center",gap="xxlarge")
    with c1:
        if st.button("Register now",type="secondary", icon=":material/passkey:",key = "register_now_button", shortcut="control+enter",  width="stretch"):
            success , message = register_teacher(teacher_username, teacher_name, teacher_password, teacher_password_confirm)
            if success :
                st.success(message)
                import time 
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else :
                st.error(message)
    with c2:
        if st.button("Login instead",type="primary", icon=":material/passkey:",key = "login_instead_button", width="stretch"):
            st.session_state.teacher_login_type = "login"
            st.rerun()
    st.space()   
    footer_dashboard() 
    
    
      