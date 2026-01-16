import streamlit as st
import pandas as pd
import random
import time

# --- Page Config ---
st.set_page_config(page_title="Sumero Health AI", page_icon="🛡️", layout="wide")

# --- Custom Styling ---
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #3e4150;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data():
    # Ensure pilot_clean.csv exists
    return pd.read_csv("pilot_clean.csv")

df = load_data()

# --- Sidebar: User Selection ---
st.sidebar.title("👤 Health Profile")
user_id = st.sidebar.select_slider("Select Profile Index", options=range(len(df)), value=0)
current_data = df.iloc[user_id]

st.sidebar.markdown(f"**Occupation:** {current_data['Occupation']}")
st.sidebar.markdown(f"**Age:** {current_data['Age']}")
st.sidebar.markdown(f"**Sleep Disorder:** {current_data['Sleep Disorder']}")

st.sidebar.markdown("---")
st.sidebar.info("This AI coach uses your Age, Occupation, and Biometrics to provide hyper-personalized advice.")

# --- Main Dashboard ---
st.title("🛡️ Sumero Health Intelligence")
st.subheader(f"Status for {current_data['Occupation']} (Age: {current_data['Age']})")

# Proactive Coach Briefing
with st.expander("🚀 Daily Coach Briefing (Read First)", expanded=True):
    state = current_data['health_state']
    stress = current_data['Stress Level']
    sleep_dur = current_data['Sleep Duration']
    
    # Specific timing heuristics
    bedtime = "9:30 PM" if stress > 7 or state == "Under-Recovered" else "10:45 PM"
    stop_work = "5:00 PM" if stress > 8 else "6:30 PM"
    
    if state == "Under-Recovered":
        st.error(f"**Coaching Alert:** You are running in the red. For a {current_data['Occupation']}, this burnout risk is high. **Plan:** Finish work by {stop_work}, no high-intensity training, and lights out at **{bedtime}** sharp.")
    elif state == "Optimal":
        st.success(f"**Performance Window:** You are primed for elite output. **Goal:** High-intensity session at 5:30 PM. Bedtime at {bedtime} to maintain this streak.")
    else:
        st.warning(f"**Stability Note:** You're balanced. Focus on consistency. Aim for bed by {bedtime} to nudge into 'Optimal' tomorrow.")

# Top Metrics Row
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("State", current_data['health_state'])
m2.metric("Sleep", f"{current_data['Sleep Duration']}h")
m3.metric("Quality", f"{current_data['Quality of Sleep']}/10")
m4.metric("Stress", f"{current_data['Stress Level']}/10")
m5.metric("Heart Rate", f"{current_data['Heart Rate']} bpm")
m6.metric("BP", current_data['Blood Pressure'])

# Secondary Metrics Row
s1, s2, s3, s4 = st.columns(4)
s1.metric("BMI", current_data['BMI Category'])
s2.metric("Daily Steps", f"{current_data['Daily Steps']:,}")
s3.metric("Activity Level", current_data['Physical Activity Level'])
s4.metric("Gender", current_data['Gender'])

# --- Chat Interface ---
st.markdown("---")
st.subheader("💬 Health AI Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Proactive first message
    st.session_state.messages.append({"role": "assistant", "content": f"Hey! I've analyzed your {current_data['Occupation']} data. Ready to optimize your day? Ask me 'When can I rest?' or 'What's my plan today?'"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about recovery, sleep, or training..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Logic mirroring 2_generate_instructions.py
        state = current_data['health_state']
        occ = str(current_data['Occupation'])
        dis = str(current_data['Sleep Disorder'])
        age = current_data['Age']
        hr = current_data['Heart Rate']
        bp = current_data['Blood Pressure']
        stress = current_data['Stress Level']
        sleep_dur = current_data['Sleep Duration']
        low_p = prompt.lower()
        
        greeting = random.choice(["Hey!", "Hello!", "Hi there!", "Listen:"])
        
        # Heuristics for times
        bedtime = "9:15 PM" if stress > 7 or state == "Under-Recovered" else "10:30 PM"
        stop_work = "4:45 PM" if stress > 8 else "6:00 PM"
        nap_time = "1:30 PM" if sleep_dur < 6.5 else "None"

        # --- Proactive & Time-Specific Handlers ---
        if any(x in low_p for x in ["when", "rest", "stop", "time"]):
            if "sleep" in low_p or "bed" in low_p:
                res = f"{greeting} Your optimal bedtime tonight is **{bedtime}**. You only got {sleep_dur}h last night, so your body needs this extra window for recovery."
            elif "nap" in low_p:
                if state == "Under-Recovered":
                    res = f"{greeting} I'd recommend a 20-min power nap at **{nap_time}**. Don't sleep longer or you'll be groggy."
                else:
                    res = f"{greeting} You're fresh enough that a nap isn't necessary. Better to save that sleep pressure for tonight's rest."
            else:
                if state == "Under-Recovered":
                    res = f"{greeting} Right now. Since you're a {occ}, you need to wind down. I suggest finishing all high-stress work by **{stop_work}** today."
                else:
                    res = f"{greeting} You can push until **{stop_work}**, but then it's time to shift into recovery mode."

        elif any(x in low_p for x in ["age", "health", "how to"]):
            res = f"{greeting} To stay healthy as a {age}-year-old {occ}, consistency is your best friend. My plan for you: work ends by {stop_work}, lights out at **{bedtime}**, and hit your {current_data['Daily Steps']} steps early."

        elif any(x in low_p for x in ["dizzy", "unwell", "sick"]):
            res = f"{greeting} Stop what you're doing. Your BP ({bp}) and {stress}/10 stress say you're redlining. Drink 500ml of water and sit down for 10 minutes **now**."

        elif any(x in low_p for x in ["run", "running", "jog", "workout", "gym"]):
            if state == "Optimal":
                res = f"{greeting} You're ready! Start your session at **5:30 PM**. Your HR ({hr}) and Quality are elite. Aim for a 45-min workout."
            else:
                res = f"{greeting} I'd advise against a heavy session. Instead, do 15 mins of light stretching at **8:00 PM** to prepare for that **{bedtime}** bedtime."

        elif any(x in low_p for x in ["tired", "exhausted", "sleepy"]):
            res = f"{greeting} The numbers show it—HR is {hr} and you're under-recovered. My clear instruction: Stop all high-focus tasks by **{stop_work}**."

        elif any(x in low_p for x in ["water", "hydration", "drink"]):
            res = f"{greeting} Hydration is critical. Aim for 3 liters today. Have 500ml **right now** to help lower that {stress}/10 stress level."

        else: # Default/General
            if state == "Optimal":
                res = f"{greeting} You're in a high-performance window. Enjoy your energy but aim for bed by **{bedtime}** to keep the streak alive."
            elif state == "Under-Recovered":
                res = f"{greeting} You're running in the red. For a {occ}, this is a burnout zone. Prioritize rest at **{bedtime}** above all else."
            else:
                res = f"{greeting} You're steady. Keep your {occ} work balanced and aim for the **{bedtime}** sleep target."

        # Simulate streaming
        full_p = ""
        for chunk in res.split():
            full_p += chunk + " "
            time.sleep(0.04)
            message_placeholder.markdown(full_p + "▌")
        message_placeholder.markdown(full_p)
        st.session_state.messages.append({"role": "assistant", "content": full_p})
