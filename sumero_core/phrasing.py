from typing import List

# Industry Standard: Human-Reviewed Controlled Phrases
REASON_MAP = {
    "LOW_SLEEP": "Your sleep duration fell below clinical recovery thresholds.",
    "HIGH_STRESS": "Significant daytime stress levels are impacting your nervous system's ability to recover.",
    "HIGH_HR": "Elevated resting heart rate detected, indicating physiological strain or fatigue.",
    "HIGH_BP": "Blood pressure readings are outside optimal ranges, suggesting systemic load.",
    "GOOD_RECOVERY": "Consistent sleep and low stress are maintaining your physiological capacity.",
    "STABLE_BASELINE": "Your current metrics align with your standard activity-to-rest ratio."
}

STATE_TITLES = {
    "Sleep_Deprived": "🔴 CRITICAL RECOVERY DEFICIT",
    "Under_Recovered": "🟡 MODERATE STRAIN WARNING",
    "Well_Recovered": "🟢 OPTIMAL READINESS"
}

STATE_SUMMARY = {
    "Sleep_Deprived": "Your body has not completed a full repair cycle. Avoid all physiological load.",
    "Under_Recovered": "Recovery is incomplete. Prioritize stability and avoid max-effort tasks.",
    "Well_Recovered": "Your system is ready for standard or high-intensity activity."
}

def generate_briefing(state: str, reason_codes: List[str], workout_allowed: bool) -> str:
    """
    Deterministic Phrasing Engine. 
    Constructs a human-readable briefing based strictly on Heuristic decisions.
    """
    title = STATE_TITLES.get(state, "Health Status Update")
    summary = STATE_SUMMARY.get(state, "No specific guidance available.")
    
    reasons = "\n".join([f"- {REASON_MAP.get(code, 'Metric variation detected.')}" for code in reason_codes])
    
    workout_advice = "✅ Workout Allowed: Prioritize moderate intensity." if workout_allowed else "🛑 No Workout: Physical load should be minimized."
    
    briefing = f"""
{title}
{summary}

Analysis:
{reasons}

Directives:
{workout_advice}
    """.strip()
    
    return briefing
