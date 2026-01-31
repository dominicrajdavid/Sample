import streamlit as st
import pandas as pd
import io
import time
from groq import Groq

# --- CONFIGURATION & ROI STATE ---
st.set_page_config(page_title="Executive QA Intelligence Studio", layout="wide")

if 'total_hours_saved' not in st.session_state:
    st.session_state.total_hours_saved = 0.0

# --- CUSTOM CSS FOR MANAGEMENT UI ---
st.markdown("""
    <style>
    .metric-card { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; }
    .agent-box { border-left: 5px solid #6366f1; padding: 15px; background: #fdfdfd; border-radius: 8px; margin-bottom: 10px; }
    .stButton>button { background-color: #0f172a; color: white; border-radius: 8px; height: 3em; width: 100%; font-weight: bold; }
    .stButton>button:hover { background-color: #2563eb; color: white; }
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
        return f"Error: {str(e)}"

def get_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Executive_Report')
    return output.getvalue()

# --- TOP LEVEL MANAGEMENT DASHBOARD ---
st.title("🛡️ Gen AI Intelligence Studio: Executive View")
st.markdown("##### *Strategic Quality Orchestration & Risk Mitigation*")

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Total ROI (Hours Saved)", f"{st.session_state.total_hours_saved} hrs")
with m2:
    st.metric("Estimated Cost Recovery", f"${int(st.session_state.total_hours_saved * 85)}", delta="Strategic Asset")
with m3:
    st.metric("Release Confidence Score", "94%", delta="2% High")

st.divider()

# --- STRATEGIC AGENT GRID ---
agents = [
    {"name": "Requirement Analysis", "icon": "📝", "hr": 2.0, "desc": "Audit PRDs for clarity and risks."},
    {"name": "Test Case Generator", "icon": "📊", "hr": 2.5, "desc": "Convert stories to executable suites."},
    {"name": "Defect Prediction Risk", "icon": "⚠️", "hr": 3.5, "desc": "AI analysis of high-risk fail zones."},
    {"name": "Impact & Regression", "icon": "🎯", "hr": 3.0, "desc": "Optimize regression scope for speed."},
    {"name": "Root Cause Analysis", "icon": "🕵️", "hr": 1.5, "desc": "Instant failure diagnosis for Sprints."},
    {"name": "Swagger to Code", "icon": "🔗", "hr": 4.0, "desc": "API automation from documentation."}
]

cols = st.columns(3)
for i, agent in enumerate(agents):
    with cols[i % 3]:
        st.markdown(f"<div class='agent-box'><h4>{agent['icon']} {agent['name']}</h4><p style='font-size:0.8em; color:gray;'>{agent['desc']}</p></div>", unsafe_allow_html=True)
        if st.button(f"Activate {agent['name']}", key=f"btn_{i}"):
            st.session_state.active_agent = agent

# --- EXECUTION & EXCEL EXPORT ---
if 'active_agent' in st.session_state:
    active = st.session_state.active_agent
    st.divider()
    st.subheader(f"Working Space: {active['name']}")
    
    api_key = st.sidebar.text_input("Groq API Key", type="password")
    user_input = st.text_area("Input data (Requirements, Logs, or Swagger):", height=200)

    if st.button("🚀 Execute Strategic Analysis"):
        if not api_key:
            st.error("API Key required in the sidebar.")
        else:
            with st.spinner("Analyzing with Gen AI..."):
                # System prompt optimized for structured data extraction
                sys_p = f"You are a Senior Project Manager. Analyze the input for '{active['name']}' and return the results ONLY as a valid CSV-formatted string with headers."
                raw_csv = call_llm(sys_p, user_input, api_key)
                
                try:
                    df = pd.read_csv(io.StringIO(raw_csv))
                    st.success(f"Strategic Analysis Complete. Saved ~{active['hr']} hours of manual review.")
                    st.session_state.total_hours_saved += active['hr']
                    
                    # Searchable Table with native Copy
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Download Button for Excel
                    excel_data = get_excel(df)
                    st.download_button(
                        label="📥 Download Executive Report (Excel)",
                        data=excel_data,
                        file_name=f"{active['name']}_Analysis.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except:
                    st.warning("Could not parse as table. Raw Output:")
                    st.markdown(raw_csv)
