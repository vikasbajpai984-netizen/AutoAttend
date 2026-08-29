import streamlit as st
from PIL import Image

@st.dialog("Capture or Upload Photo")
def Add_photos_dialog():
    st.write("Add Classroom Photos to take attendace")
    
    if 'photo_tab' not in st.session_state:
        st.session_state.photo_tab = 'camera' 
    t1, t2 = st.columns(2)
    with t1:
        type_cam = 'primary' if st.session_state.photo_tab == 'camera' else 'tertiary'
        if st.button("camera", type = type_cam, key = "camera_dialog", width = "stretch"):
            st.session_state.photo_tab = 'camera'

    with t2:
        type_up = 'primary' if st.session_state.photo_tab == 'camera' else 'tertiary'
        if st.button("Upload photos", type = type_up, key = "upload_dialog", width = "stretch"):
            st.session_state.photo_tab = 'Upload'
    
    if st.session_state.photo_tab == 'camera':
        cam_photo = st.camera_input("Take Snapshot", key = "cam_dialog")
        if cam_photo:
            st.session_state.attendance_images.append(Image.open(cam_photo))
            st.toast("Photo Captured")
            st.rerun()
            
    if st.session_state.photo_tab == 'Upload':
        uploaded_files = st.file_uploader("Choose image files", type = ["jpg", "png", "jpeg"], accept_multiple_files=True, key = "dialog_upload")
        if uploaded_files:
            for f in uploaded_files:
                st.session_state.attendance_images.append(Image.open(f))
            st.toast("Photo Uploaded Successfully!")
            st.rerun()
            
    st.divider()
    
    if st.button("Done", type = "primary", width="stretch"):
        st.rerun()
    