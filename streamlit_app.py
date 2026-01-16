import streamlit as st
import pandas as pd
import random
import time
import os
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Page Config ---
st.set_page_config(page_title="Sumero Health AI", page_icon="🛡️", layout="wide")

# --- Custom Styling ---
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 10px; border-radius: 10px; border: 1px solid #3e4150; }
    .stButton>button { background-color: #ff4b4b; color: white; }
    .code-block { background-color: #262730; color: #ffffff; padding: 15px; border-radius: 5px; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- LLM Backend Logic ---
class HybridBackend:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        
    def get_context(self, data):
        """Converts patient data into a markdown table for the LLM."""
        return f"""
### PATIENT CONTEXT (CURRENT STATE)
| Metric | Value |
| :--- | :--- |
| **Occupation** | {data['Occupation']} |
| **Age** | {data['Age']} |
| **Health State** | {data['health_state']} |
| **Stress Level** | {data['Stress Level']}/10 |
| **Sleep Duration** | {data['Sleep Duration']}h |
| **Recovery Deep/REM** | {data.get('Deep_Sleep', 'N/A')}h / {data.get('REM_Sleep', 'N/A')}h |
| **Heart Rate** | {data['Heart Rate']} bpm |
| **Steps Today** | {data['Daily Steps']} |
"""

    def generate_heuristic(self, prompt, data):
        """Old stable heuristic logic (Fallback)."""
        low_p = prompt.lower()
        state = data['health_state']
        bedtime = "9:15 PM" if data['Stress Level'] > 7 or state == "Under-Recovered" else "10:30 PM"
        if any(x in low_p for x in ["when", "sleep", "bed"]):
            return f"Heuristic Analysis (Local): Your optimal bedtime tonight is **{bedtime}**."
        return f"Heuristic Analysis: You are in a {state} zone. Prioritize bed by {bedtime}."

    def generate_ollama(self, prompt, data):
        """Local Ollama Inference with better error handling."""
        sys_prompt = f"You are Sumero Health AI, a proactive health coach. Use this patient context to give a 1-2 sentence directive answer:\n{self.get_context(data)}"
        try:
            res = requests.post(f"{self.ollama_url}/api/chat", 
                json={
                    "model": self.ollama_model,
                    "messages": [
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                }, timeout=15)
            
            resp_json = res.json()
            if 'error' in resp_json:
                return f"⚠️ Ollama Error: {resp_json['error']}. (Try: 'ollama pull {self.ollama_model}')"
            
            if 'message' in resp_json:
                return resp_json['message']['content']
            
            return f"⚠️ Unexpected Ollama Response: {resp_json}"
            
        except requests.exceptions.ConnectionError:
            return f"⚠️ Connection Error: Could not reach Ollama at {self.ollama_url}. Is it running?"
        except Exception as e:
            return f"⚠️ Ollama Exception: {e}"

    def generate_openai(self, prompt, data):
        """Cloud OpenAI Inference."""
        if not self.openai_key: return "⚠️ OpenAI API key missing in .env"
        client = OpenAI(api_key=self.openai_key)
        sys_prompt = f"You are Sumero Health AI. Be proactive and directive. Use context:\n{self.get_context(data)}"
        try:
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"⚠️ OpenAI Error: {e}"

# --- Data Loading ---
@st.cache_data
def load_data():
    return pd.read_csv("pilot_clean.csv")

df = load_data()
backend = HybridBackend()

# --- Sidebar ---
st.sidebar.title("👤 Health Intelligence")
user_id = st.sidebar.select_slider("Select Patient Index", options=range(len(df)), value=58)
current_data = df.iloc[user_id]

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Model Configuration")
model_type = st.sidebar.radio("Select Intelligence Layer", 
    ["Heuristic (Stable)", "Ollama (Local LLM)", "OpenAI (Cloud LLM)"])

if model_type == "Ollama (Local LLM)":
    if st.sidebar.button("🔍 Check Ollama Status"):
        try:
            res = requests.get(f"{backend.ollama_url}/api/tags")
            models = [m['name'] for m in res.json().get('models', [])]
            if backend.ollama_model in [m.split(':')[0] for m in models] or backend.ollama_model in models:
                st.sidebar.success(f"✅ Ollama Connected: '{backend.ollama_model}' found.")
            else:
                st.sidebar.warning(f"⚠️ '{backend.ollama_model}' not found in local tags. Run 'ollama pull {backend.ollama_model}'")
        except:
            st.sidebar.error("❌ Ollama Offline. Ensure it is running on port 11434.")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Occupation:** {current_data['Occupation']}")
st.sidebar.markdown(f"**Source:** `{current_data.get('Source', 'WHOOP-Study')}`")

# --- Dashboard ---
st.title("🛡️ Sumero Health Intelligence")
st.subheader(f"Directives for {current_data['Occupation']} (Age: {current_data['Age']})")

# Top Metrics Row
cols = st.columns(6)
metrics = [
    ("State", current_data['health_state']),
    ("Sleep", f"{current_data['Sleep Duration']}h"),
    ("Quality", f"{current_data['Quality of Sleep']}/10"),
    ("Stress", f"{current_data['Stress Level']}/10"),
    ("HR", f"{current_data['Heart Rate']} bpm"),
    ("Steps", f"{current_data['Daily Steps']:,}")
]
for i, (label, val) in enumerate(metrics):
    cols[i].metric(label, val)

# --- Chat Interface ---
st.markdown("---")
st.subheader("💬 Health AI Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": f"Hey! I've analyzed your {current_data['Occupation']} data using the {model_type} layer. What's our plan?"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about recovery protocol, sleep shifts, or workout readiness..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        if model_type == "Heuristic (Stable)":
            res = backend.generate_heuristic(prompt, current_data)
        elif model_type == "Ollama (Local LLM)":
            res = backend.generate_ollama(prompt, current_data)
        else:
            res = backend.generate_openai(prompt, current_data)

        # Simulate streaming for all
        full_p = ""
        for chunk in res.split():
            full_p += chunk + " "
            time.sleep(0.04)
            message_placeholder.markdown(full_p + "▌")
        message_placeholder.markdown(full_p)
        st.session_state.messages.append({"role": "assistant", "content": full_p})
