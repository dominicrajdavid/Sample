import streamlit as st
import pandas as pd
from groq import Groq
from datetime import datetime

# --- 1. GLOBAL COMMAND CENTER THEME ---
st.set_page_config(page_title="Quality Intelligence Studio", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    .stApp { background: radial-gradient(circle at top right, #1e293b, #0f172a); color: #f8fafc; }
    
    .studio-title { font-family: 'Orbitron', sans-serif; color: #ffffff; letter-spacing: 5px; text-align: center; margin-top: 50px; margin-bottom: 30px; }
    
    .login-box { 
        max-width: 700px; margin: 0 auto; padding: 50px; 
        background: rgba(255, 255, 255, 0.02); backdrop-filter: blur(15px);
        border-radius: 30px; border: 1px solid rgba(56, 189, 248, 0.2);
    }

    .kpi-card { background: rgba(255, 255, 255, 0.03); border-radius: 20px; padding: 25px; text-align: center; border: 1px solid rgba(255,255,255,0.1); }
    .kpi-value { font-family: 'Orbitron', sans-serif; font-size: 32px; color: #38bdf8; }
    
    .stButton>button { border-radius: 12px; font-weight: 600; transition: 0.3s; height: 50px; }
    .console-box { background: #0b1120; border-radius: 15px; padding: 25px; border-left: 4px solid #38bdf8; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SESSION STATE ---
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'total_hours' not in st.session_state: st.session_state.total_hours = 40.5

st.markdown("<h1 class='studio-title'>QUALITY INTELLIGENCE STUDIO</h1>", unsafe_allow_html=True)

# --- 3. INNOVATIVE LOGIN INTERFACE ---
if not st.session_state.authenticated:
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8; font-size:14px; letter-spacing:2px;'>ENTERPRISE ACCESS PROTOCOL</p>", unsafe_allow_html=True)
    
    user_name = st.text_input("NAME", placeholder="Enter Operator Name...")
    api_key = st.text_input("ENTER ENTERPRISE API KEY", type="password", placeholder="gsk_...")
    st.markdown("<div style='text-align:right;'><a href='https://console.groq.com/keys' target='_blank' style='color:#38bdf8; font-size:12px; text-decoration:none;'>Get API Key →</a></div>", unsafe_allow_html=True)
    
    col_reset, col_spacer, col_enter = st.columns([0.25, 0.5, 0.25])
    with col_reset:
        if st.button("🗑️ RESET"): st.rerun()
    with col_enter:
        if st.button("✅ ENTER"):
            if api_key.startswith("gsk_") and user_name:
                st.session_state.operator = user_name
                st.session_state.saved_key = api_key
                st.session_state.authenticated = True
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. MAIN COMMAND CENTER ---
else:
    # KPI Metrics Board
    k1, k2, k3 = st.columns(3)
    with k1: st.markdown(f"<div class='kpi-card'><div style='color:#94a3b8; font-size:12px;'>TOIL SAVED</div><div class='kpi-value'>{st.session_state.total_hours} HRS</div></div>", unsafe_allow_html=True)
    with k2: st.markdown(f"<div class='kpi-card'><div style='color:#94a3b8; font-size:12px;'>AI ACCELERATION</div><div class='kpi-value'>12.5X</div></div>", unsafe_allow_html=True)
    with k3: st.markdown(f"<div class='kpi-card'><div style='color:#94a3b8; font-size:12px;'>RISK COVERAGE</div><div class='kpi-value'>98.4%</div></div>", unsafe_allow_html=True)

    # Agent Strip
    agents = [
        {"name": "Requirement Analysis", "icon": "📝", "hr": 2.0},
        {"name": "Test Case Gen", "icon": "📊", "hr": 2.5},
        {"name": "Data Factory", "icon": "📁", "hr": 1.5},
        {"name": "Defect Prediction", "icon": "⚠️", "hr": 3.0},
        {"name": "Automation Migration", "icon": "🔄", "hr": 4.5},
        {"name": "BA Documentation", "icon": "📄", "hr": 5.0}
    ]
    st.markdown("<br>", unsafe_allow_html=True)
    grid = st.columns(6)
    for i, a in enumerate(agents):
        if grid[i].button(f"{a['icon']} {a['name']}"):
            st.session_state.active_agent = a

    # Workspace Section
    if 'active_agent' in st.session_state:
        agent = st.session_state.active_agent
        st.markdown(f"### 📡 Active Mode: {agent['name']}")
        c_in, c_ctrl = st.columns([0.75, 0.25])
        with c_in: prompt = st.text_area("Input Stream:", height=150)
        with c_ctrl:
            if st.button("⚡ EXECUTE"):
                try:
                    client = Groq(api_key=st.session_state.saved_key)
                    resp = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": f"QA Expert. Output direct records for {agent['name']}."}, {"role": "user", "content": prompt}]
                    )
                    # Prepare meta-stamped output
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    meta_header = f"**OPERATOR:** {st.session_state.operator.upper()} | **TIMESTAMP:** {timestamp}\n\n---\n"
                    st.session_state.last_out = meta_header + resp.choices[0].message.content
                    st.session_state.total_hours += agent['hr']
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")

    # Output Console with Traceability
    if 'last_out' in st.session_state:
        st.markdown("---")
        h_l, h_r = st.columns([0.8, 0.2])
        with h_l: st.markdown("### 📋 Strategic Traceability Output")
        with h_r: st.download_button("📥 EXPORT REPORT", data=st.session_state.last_out, file_name=f"Studio_Report_{st.session_state.operator}.md")
        st.markdown(f"<div class='console-box'>{st.session_state.last_out}</div>", unsafe_allow_html=True)
