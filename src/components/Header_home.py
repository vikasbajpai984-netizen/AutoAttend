import streamlit as st 

def header_home():
    logo_url="https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center; margin-bottom:30px; margin-top:30px ;">
            <img src='{logo_url}' style='height: 100px;'/>
            <h1 style='text-align:center ; color:#E0E3FF;'>AUTO <br/> ATTEND</h1>
        </div>
            
                  """,unsafe_allow_html=True)
    
def Header_dashboard():
    logo_url="https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown(f"""
        <div style="display:flex;align-items:left;justify-content:left; gap:15px;">
            <img src='{logo_url}' style='height: 80px';/>
            <h2 style='text-align:center ; color:#5865F2;'>AUTO <br/>  ATTEND</h2>
        </div>
            
                  """,unsafe_allow_html=True)    
    
    