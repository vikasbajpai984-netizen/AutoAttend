import streamlit as st 

def footer_home():
    logo_url="https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown(f"""
        <div style="margin-top: 2rem ;display: flex; gap: 6px; justify-content: center; items-align: center; color:#E0E3FF", font-size: 2rem>
            <p> Created by Vikas Bajpai</p>
        </div>
            
                  """,unsafe_allow_html=True)

def footer_dashboard():
    logo_url="https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown(f"""
        <div style="margin-top: 2rem ;display: flex; gap: 6px; justify-content: center; items-align: center; color:black", font-size: 2rem>
            <p> Created by Vikas Bajpai</p>
        </div>
            
                  """,unsafe_allow_html=True)    