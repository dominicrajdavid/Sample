import streamlit as st
import pandas as pd
import io
import time
from groq import Groq

# --- INITIAL CONFIGURATION ---
st.set_page_config(page_title="Gen AI Intelligence Studio", layout="wide", initial_sidebar_state="expanded")

# Initialize Session States for ROI Tracker
if 'total_hours_saved' not in st.session_state:
    st.session_state.total_hours_saved = 0.0
if 'tasks_completed' not in st.session_state:
    st.session_state.tasks_completed = 0

# --- STYLING (Rich UI/UX) ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5em;
        background-color: #0f172a; color: white; font-weight: bold;
        transition: all 0.3s; border: none;
    }
    .stButton>button:hover {
        background-color: #2563eb; transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }
    [data-testid="stMetricValue"] { font-size: 28px; color: #2563eb; }
    .agent-card {
        border-radius: 12px; border: 1px solid #e2e8f0;
        padding: 20px; background: white; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CORE LOGIC ---
def call_llm(system_prompt, user_content, api_key):
    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
            temperature=0.1,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: Please verify your API Key. Details: {str(e)}"

def update_metrics(hours):
    st.session_state.total_hours_saved += hours
    st.session_state.tasks_completed += 1

# --- SIDEBAR (ROI & SETTINGS) ---
with st.sidebar:
    st.title("🛡️ Studio Control")
    api_key = st.text_input("Enter Groq API Key", type="password", help="Get yours at console.groq.com")
    st.divider()
    
    st.subheader("📈 Project Impact")
    st.metric("Total Hours Reclaimed", f"{st.session_state.total_hours_saved} hrs")
    st.metric("Manual Tasks Offloaded", st.session_state.tasks_completed)
    # Average Senior QA Rate: $65/hr
    savings = int(st.session_state.total_hours_saved * 65)
    st.metric("Estimated Cost Savings", f"${savings:,}")
    
    if st.button("Reset Session Metrics"):
        st.session_state.total_hours_saved = 0.0
        st.session_state.tasks_completed = 0
        st.rerun()

# --- MAIN DASHBOARD ---
st.title("⚡ Gen AI Intelligence Studio")
st.markdown("##### *Unified Quality Intelligence Orchestration*")

# Agent Definitions with "Manual Effort" weights
agents = [
    {"name": "Requirement Analysis", "icon": "📝", "weight": 2.0, "desc": "PRD to Gherkin & User Stories."},
    {"name": "Test Case Gen", "icon": "📊", "weight": 2.5, "desc": "Structured suites with Excel export."},
    {"name": "Selenium to Playwright", "icon": "🔄", "weight": 4.5, "desc": "Legacy script migration agent."},
    {"name": "Root Cause Analysis", "icon": "🕵️", "weight": 1.5, "desc": "Log failure & defect diagnosis."},
    {"name": "Impact Analysis", "icon": "🎯", "weight": 3.0, "desc": "Regression scope optimizer."},
    {"name": "Unit Test Creator", "icon": "💻", "weight": 1.5, "desc": "Auto-generate PyTest/Jest suites."}
]

# Display Grid
cols = st.columns(3)
for i, agent in enumerate(agents):
    with cols[i % 3]:
        st.markdown(f"""<div class='agent-card'><h3>{agent['icon']} {agent['name']}</h3><p>{agent['desc']}</p></div>""", unsafe_allow_html=True)
        if st.button(f"Activate {agent['name']}", key=f"btn_{i}"):
            st.session_state.active_agent = agent
            st.rerun()

st.divider()

# --- EXECUTION ENGINE ---
if 'active_agent' in st.session_state:
    agent = st.session_state.active_agent
    st.header(f"{agent['icon']} {agent['name']} Workspace")
    
    if not api_key:
        st.error("🔑 API Key required in the sidebar to run agents.")
    else:
        # Dynamic Input Fields based on Agent
        if agent['name'] == "Requirement Analysis":
            u_input = st.text_area("Paste Requirements/PRD:", height=250)
            sys_p = "Convert requirements into User Stories and Gherkin scenarios."
        elif agent['name'] == "Test Case Gen":
            u_input = st.text_area("Paste Scenarios:")
            sys_p = "Generate a structured test case table in CSV format."
        elif agent['name'] == "Selenium to Playwright":
            u_input = st.text_area("Paste Selenium Code:", height=250)
            sys_p = "Refactor Selenium code to Playwright Async Python. Return only code."
        elif agent['name'] == "Root Cause Analysis":
            u_input = st.text_area("Paste Stack Trace / Logs:")
            sys_p = "Identify if the failure is Code, Data, or Environment. Provide a fix."
        elif agent['name'] == "Impact Analysis":
            v1 = st.text_input("Original Requirement:")
            v2 = st.text_input("New Requirement:")
            u_input = f"Old: {v1}\nNew: {v2}"
            sys_p = "Analyze changes and suggest the minimum regression test scope."
        elif agent['name'] == "Unit Test Creator":
            u_input = st.text_area("Paste Function/Code:")
            sys_p = "Write comprehensive unit tests using PyTest."

        if st.button(f"🚀 Execute {agent['name']}"):
            with st.spinner("Agent is processing..."):
                start_time = time.time()
                result = call_llm(sys_p, u_input, api_key)
                duration = time.time() - start_time
                
                st.subheader("Agent Output")
                st.markdown(result)
                update_metrics(agent['weight'])
                st.toast(f"Execution successful! Saved ~{agent['weight']} hours.", icon="✅")