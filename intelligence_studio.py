import streamlit as st
import pandas as pd
import io
import time
from groq import Groq

# --- INITIAL CONFIGURATION ---
st.set_page_config(page_title="Gen AI Intelligence Studio", layout="wide", initial_sidebar_state="expanded")

# Initialize Session States
if 'total_hours_saved' not in st.session_state:
    st.session_state.total_hours_saved = 0.0
if 'tasks_completed' not in st.session_state:
    st.session_state.tasks_completed = 0

# --- RICH UI STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3em;
        background-color: #0f172a; color: white; font-weight: bold;
    }
    .stButton>button:hover { background-color: #2563eb; border: none; }
    .agent-card {
        border-radius: 12px; border: 1px solid #e2e8f0;
        padding: 20px; background: white; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CORE UTILITIES ---
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
        return f"Error: {str(e)}"

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Studio_Report')
    return output.getvalue()

# --- SIDEBAR (ROI TRACKER) ---
with st.sidebar:
    st.title("🛡️ Admin Console")
    api_key = st.text_input("Groq API Key", type="password")
    st.divider()
    st.metric("Total Hours Saved", f"{st.session_state.total_hours_saved} hrs")
    st.metric("Cost Savings", f"${int(st.session_state.total_hours_saved * 65)}")
    if st.button("Reset Metrics"):
        st.session_state.total_hours_saved = 0.0
        st.rerun()

# --- MAIN DASHBOARD ---
st.title("🚀 Gen AI Intelligence Studio")
st.caption("Strategic Automation for PMs & Senior QA Leads")

agents = [
    {"name": "Requirement Analysis", "icon": "📝", "hr": 2.0, "p": "Analyze requirements into a table with columns: ID, User Story, Gherkin Scenario."},
    {"name": "Test Case Gen", "icon": "📊", "hr": 2.5, "p": "Generate test cases as a table: ID, Step, Expected Result, Priority."},
    {"name": "Root Cause Analysis", "icon": "🕵️", "hr": 1.5, "p": "Analyze logs and return a table: Error, Category, Root Cause, Suggested Fix."},
    {"name": "Impact Analysis", "icon": "🎯", "hr": 3.0, "p": "Compare versions and return a table: Change, Impacted Module, Risk Level, Test Action."}
]

cols = st.columns(len(agents))
for i, agent in enumerate(agents):
    with cols[i]:
        st.markdown(f"<div class='agent-card'><h4>{agent['icon']} {agent['name']}</h4></div>", unsafe_allow_html=True)
        if st.button("Select", key=f"sel_{i}"):
            st.session_state.active_agent = agent

st.divider()

# --- DYNAMIC WORKING AREA ---
if 'active_agent' in st.session_state:
    active = st.session_state.active_agent
    st.subheader(f"Working Area: {active['name']}")
    
    user_input = st.text_area("Paste your data here:", height=200)
    
    if st.button(f"🚀 Execute {active['name']}"):
        if not api_key:
            st.error("Please enter an API key in the sidebar.")
        else:
            with st.spinner("Processing..."):
                # Force LLM to output CSV format for parsing
                full_prompt = f"{active['p']} Important: Return ONLY a valid CSV-formatted string with headers. No conversation."
                raw_csv = call_llm(full_prompt, user_input, api_key)
                
                try:
                    df = pd.read_csv(io.StringIO(raw_csv))
                    
                    st.success(f"Analysis Complete! Saved ~{active['hr']} hours.")
                    st.session_state.total_hours_saved += active['hr']
                    
                    # Display table with native Copy-to-Clipboard (Ctrl+C)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Download Excel Option
                    excel_file = to_excel(df)
                    st.download_button(
                        label="📥 Download Results as Excel",
                        data=excel_file,
                        file_name=f"{active['name'].replace(' ', '_')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except:
                    st.error("Format error. Raw output shown below:")
                    st.markdown(raw_csv)
