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
        """Production-Grade Heuristic Engine - Edge-Optimized Intelligence"""
        low_p = prompt.lower()
        
        # Extract all biometrics
        state = data['health_state']
        occ = str(data['Occupation'])
        age = data['Age']
        hr = data['Heart Rate']
        stress = data['Stress Level']
        sleep_dur = data['Sleep Duration']
        sleep_quality = data['Quality of Sleep']
        steps = data['Daily Steps']
        activity = data['Physical Activity Level']
        bmi = data['BMI Category']
        gender = data['Gender']
        
        # Source-specific metrics
        source = data.get('Source', 'WHOOP-Study')
        deep = data.get('Deep_Sleep', None)
        rem = data.get('REM_Sleep', None)
        
        # Dynamic time calculations
        bedtime = "9:15 PM" if stress > 7 or state == "Under-Recovered" else "10:30 PM"
        stop_work = "4:45 PM" if stress > 8 else "6:00 PM"
        nap_time = "1:30 PM" if sleep_dur < 6.5 else "None recommended"
        workout_time = "5:30 PM" if state == "Optimal" else "Light stretching only"
        
        # Greeting variation
        greetings = ["Hey!", "Listen:", "Here's the plan:", "Quick update:"]
        greeting = random.choice(greetings)
        
        # Source prefix
        if source == "AppleWatch-Raw" and not pd.isna(deep):
            prefix = f"{greeting} Your Apple Watch shows"
        else:
            prefix = f"{greeting} Based on your {occ} profile at age {age},"
        
        # ===== Primary Intent Detection =====
        
        # 1. Sleep & Bedtime Queries
        if any(x in low_p for x in ["sleep", "bed", "bedtime", "rest tonight", "when should i sleep"]):
            if sleep_dur < 6:
                return f"{prefix} you're severely sleep-deprived ({sleep_dur}h). **Critical directive:** Lights out by **{bedtime}** sharp. No exceptions."
            elif not pd.isna(deep) and deep < 1.2:
                return f"{prefix} Deep Sleep is low ({deep:.1f}h). Your brain didn't get enough repair time. Target **{bedtime}** and avoid screens 1hr before."
            else:
                return f"{prefix} aim for **{bedtime}** tonight to maintain your {state} state. Consistency is your superpower."
        
        # 2. Workout & Exercise Queries
        elif any(x in low_p for x in ["workout", "exercise", "gym", "run", "train", "lift"]):
            if state == "Under-Recovered":
                return f"{prefix} your body is redlining (HR: {hr}, Stress: {stress}/10). **No heavy training today.** Do light yoga or skip entirely. Sleep is your priority."
            elif state == "Optimal":
                return f"{prefix} you're primed! Your HR ({hr} bpm) and recovery metrics say 'go hard.' Hit the gym at **{workout_time}**. Target: High intensity."
            else:
                return f"{prefix} you're balanced. Moderate workout is fine (30-40 min cardio). Listen to your body and stop if HR spikes above {hr + 20}."
        
        # 3. Stress & Mental Health
        elif any(x in low_p for x in ["stress", "anxious", "overwhelmed", "burnout", "mental"]):
            if stress > 7:
                return f"{prefix} stress is critically high ({stress}/10). **Immediate protocol:** Stop work by **{stop_work}**, 10-min meditation, and a short walk. Your nervous system needs a reset."
            else:
                return f"{prefix} stress is manageable ({stress}/10). Keep it stable with deep breathing breaks every 2 hours. You're doing well for a {occ}."
        
        # 4. Fatigue & Energy Queries
        elif any(x in low_p for x in ["tired", "exhausted", "drained", "fatigue", "energy", "sleepy"]):
            if sleep_dur < 6.5:
                return f"{prefix} fatigue is expected—you only slept {sleep_dur}h. **Action:** {nap_time} nap (20 min max), water, and finish work by **{stop_work}**."
            elif hr > 80:
                return f"{prefix} elevated resting HR ({hr} bpm) signals stress. Hydrate, take 5-min breaks, and avoid caffeine after 2 PM."
            else:
                return f"{prefix} fatigue might be mental, not physical. Try a 10-min walk or switch tasks. Your biometrics are stable."
        
        # 5. Nap Queries
        elif any(x in low_p for x in ["nap", "power nap", "short sleep"]):
            if sleep_dur < 6.5:
                return f"{prefix} a nap is recommended at **{nap_time}**. Keep it to 20 minutes max to avoid grogginess. Set an alarm."
            else:
                return f"{prefix} you slept {sleep_dur}h—a nap isn't necessary. If you're tired, it's likely mental fatigue. Try movement instead."
        
        # 6. Steps & Activity
        elif any(x in low_p for x in ["steps", "walk", "activity", "move"]):
            if steps < 5000:
                return f"{prefix} you're at {steps:,} steps today. Target: 8,000 minimum for a {occ}. Try a 15-min walk after each meal."
            elif steps > 10000:
                return f"{prefix} great job! {steps:,} steps is excellent. Pair this with quality sleep (**{bedtime}**) for optimal recovery."
            else:
                return f"{prefix} {steps:,} steps is solid. You're on track for baseline health. Keep moving throughout the day."
        
        # 7. Work & Productivity
        elif any(x in low_p for x in ["work", "productivity", "focus", "concentration", "stop working"]):
            if stress > 7:
                return f"{prefix} your stress ({stress}/10) is too high for peak productivity. **Hard stop:** **{stop_work}**. Quality > quantity."
            else:
                return f"{prefix} you can work until **{stop_work}** safely. After that, wind down to protect tomorrow's performance."
        
        # 8. Nutrition & Hydration
        elif any(x in low_p for x in ["eat", "food", "nutrition", "drink", "water", "hydrate"]):
            return f"{prefix} hydration first: aim for 2.5L water today. For a {occ} at {age}, protein-rich meals + veggies are key. Avoid heavy carbs after 7 PM."
        
        # 9. Heart Rate Queries
        elif any(x in low_p for x in ["heart rate", "hr", "pulse", "bpm"]):
            if hr > 75:
                return f"{prefix} resting HR is elevated ({hr} bpm). This signals stress or fatigue. Prioritize rest and avoid stimulants."
            else:
                return f"{prefix} resting HR ({hr} bpm) is healthy. You're in good cardiovascular shape for age {age}."
        
        # 10. Recovery & Health State
        elif any(x in low_p for x in ["recover", "recovery", "health", "state", "status"]):
            if not pd.isna(deep) and not pd.isna(rem):
                return f"{prefix} recovery is nuanced. Deep: {deep:.1f}h, REM: {rem:.1f}h. Both are crucial. Your overall state is **{state}**. Sleep by **{bedtime}** to improve."
            else:
                return f"{prefix} your health state is **{state}**. Key drivers: Sleep ({sleep_dur}h), Stress ({stress}/10), HR ({hr}). Fix sleep first."
        
        # 11. BMI & Weight
        elif any(x in low_p for x in ["weight", "bmi", "body", "fat"]):
            return f"{prefix} BMI category: {bmi}. For a {gender} at {age}, focus on sleep quality and {steps:,}+ daily steps. Weight follows behavior."
        
        # 12. Age-Related Queries
        elif any(x in low_p for x in ["age", "older", "younger", "aging"]):
            return f"{prefix} at age {age}, recovery takes longer. Prioritize sleep (**{bedtime}**) and stress management more than younger peers."
        
        # 13. Occupation-Specific
        elif "job" in low_p or "career" in low_p:
            return f"{prefix} as a {occ}, your main risk is burnout. Your data shows {state}. Protect your calendar: hard stop at **{stop_work}**."
        
        # 14. General "How am I doing?"
        elif any(x in low_p for x in ["how am i", "doing", "status", "overall"]):
            return f"{prefix} you're in a **{state}** zone. Sleep: {sleep_dur}h, Stress: {stress}/10, Steps: {steps:,}. **Top priority:** Bed by **{bedtime}**."
        
        # 15. Default Catch-All
        else:
            if state == "Under-Recovered":
                return f"{prefix} you're currently **Under-Recovered**. For a {occ}, this is a red flag. **Protocol:** Sleep by **{bedtime}**, stop work by **{stop_work}**, and avoid high-intensity activity."
            elif state == "Optimal":
                return f"{prefix} you're crushing it! **Optimal** state at {age} is rare. Maintain with: **{bedtime}** sleep, {steps:,}+ steps, and stress under 5."
            else:
                return f"{prefix} you're **{state}**—solid baseline. Keep the momentum: bed by **{bedtime}**, moderate activity, and monitor stress."

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
