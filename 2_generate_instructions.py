import pandas as pd
import json
import random

# Define paths
clean_data_path = "pilot_clean.csv"
instructions_path = "pilot_instructions.jsonl"

def generate_instructions():
    df = pd.read_csv(clean_data_path)
    
    instructions = []
    
    instructions_diversity = [
        "Analyze my health data and provide insights.",
        "How long should I sleep tonight based on my data?",
        "Why is my recovery score low?",
        "Can I handle a hard workout today?",
        "When should I take my next nap?",
        "How does my stress affect my sleep target?",
        "Best time for coffee today given my recovery?",
        "How can I lower my stress levels today?",
        "Should I focus on cardio or weights today?",
        "Is my heart rate normal for my activity level?",
        "How do my daily steps impact my recovery?",
        "Suggest a running goal for this week.",
        "How does my job as a {Occupation} impact my health?",
        "How to manage my {Sleep Disorder} better?",
        "How does my age affect me?",
        "I feel dizzy, what should I do?",
        "When can I rest?",
        "When today should I stop working?",
        "What is the best way for me to be healthy?",
        "I feel very tired today. Help!",
        "Should I drink more water?",
        "What is my recovery protocol for tonight?",
        "How is my heart rate looking compared to my stress?",
        "Give me a 3nd step for my health today.",
        "How to improve my sleep quality tonight?",
        "My stress is high, give me an immediate action.",
        "What’s the impact of my steps on my longevity?",
        "Is my BMI category affecting my recovery speed?",
        "How does being a {Occupation} change my hydration needs?",
        "What's the best time for my high-focus work?",
        "Explain my health state in one sentence.",
        "Should I take a rest day or push through?",
        "How to prepare for a better morning tomorrow?",
        "What does my heart rate say about my fitness?",
        "Give me a tip for managing work stress as a {Occupation}.",
        "How to offset late-night work stress?",
        "What's my move-to-sleep ratio looking like?",
        "Should I prioritize steps or sleep tonight?",
        "How does my gender impact my recovery baseline?",
        "What is my 'Red Zone' warning today?",
        "How to stay in the 'Optimal' zone all week?",
        "Give me a directive for my afternoon energy slump.",
        "How is my Deep Sleep impacting my focus?",
        "Is my REM sleep sufficient for recovery?",
        "What's the relationship between my blood pressure and stress?",
        "How to optimize my routine for better HRV?",
        "Should I fast or eat normally today based on recovery?",
        "Give me a quick win for my health right now.",
        "How to stop feeling drained as a {Occupation}?",
        "What is the most important metric I should watch today?"
    ]

    for i, row in df.iterrows():
        # Source detection
        source = row.get('Source', 'WHOOP-Study')
        
        # Pick a diverse instruction
        raw_instr = instructions_diversity[i % len(instructions_diversity)]
        instruction = raw_instr.replace("{Occupation}", str(row['Occupation'])).replace("{Sleep Disorder}", str(row['Sleep Disorder']))
        
        # Construct INPUT (ALL COLUMNS)
        user_input = "\n".join([f"{col}: {row[col]}" for col in df.columns])
        
        # Extract Variables
        state = row['health_state']
        occ = str(row['Occupation'])
        age = row['Age']
        hr = row['Heart Rate']
        stress = row['Stress Level']
        sleep_dur = row['Sleep Duration']
        
        # Source-Specific Enrichment (Deep/REM sleep if available)
        deep = row.get('Deep_Sleep', None)
        rem = row.get('REM_Sleep', None)
        
        low_instr = instruction.lower()
        greeting = random.choice(["Hey!", "Hello!", "Hi!", "Listen:"])
        
        # --- Time Heuristics ---
        bedtime = "9:30 PM" if stress > 7 or state == "Under-Recovered" else "10:45 PM"
        stop_work = "5:00 PM" if stress > 8 else "6:30 PM"
        nap_time = "1:45 PM" if sleep_dur < 6.5 else "None"

        # --- Base Prompt Logic (Proactive & Directive) ---
        if source == "AppleWatch-Raw":
            prefix = f"{greeting} Looking at your Apple Watch sensors,"
        else:
            prefix = f"{greeting} Based on your profile and metrics,"

        if "when" in low_instr or "time" in low_instr:
            if "rest" in low_instr or "stop" in low_instr:
                output = f"{prefix} you should wind down by **{stop_work}**. Your {state} state suggests recovery is your top priority right now."
            elif "sleep" in low_instr or "bed" in low_instr:
                output = f"{prefix} your target bedtime is **{bedtime}**. You need to BANK some sleep tonight after your {occ} shift."
            elif "nap" in low_instr:
                output = f"{prefix} a 20-min nap at **{nap_time}** is your best bet to reset your focus today."
            else:
                output = f"{prefix} the best time for high-focus tasks is 10:00 AM, but wind down by **{stop_work}**."

        elif "healthy" in low_instr or "improving" in low_instr or "quality" in low_instr:
            if not pd.isna(deep) and not pd.isna(rem):
                output = f"{prefix} maintaining your **Deep Sleep** ({deep:.1f}h) and **REM** ({rem:.1f}h) ratios is key. To keep this quality, work ends at **{stop_work}** and lights out by **{bedtime}**."
            else:
                output = f"{prefix} for a {occ} your age, the best play is earlier sleep. Bed by **{bedtime}** and keep your daily steps above 6,000."

        elif "workout" in low_instr or "run" in low_instr or "push" in low_instr or "weights" in low_instr:
            if state == "Optimal":
                output = f"{prefix} your biometrics are primed! Hit a session at **5:30 PM**. Your HR ({hr} bpm) shows great readiness."
            else:
                output = f"{prefix} I'd advise against a heavy session. Your recovery is lagging. Instead, prioritize hitting the hay by **{bedtime}**."

        elif "tired" in low_instr or "exhausted" in low_instr or "stress" in low_instr or "immediate" in low_instr:
            output = f"{prefix} I see the depletion. Your HR is {hr} and stress is high. My clear instruction: stop all high-focus tasks by **{stop_work}**."

        elif "bmi" in low_instr or "weight" in low_instr or "gender" in low_instr:
            output = f"{prefix} the data for a {row['Gender']} with your profile suggests a baseline HR of {hr}. Consistency with a **{bedtime}** bedtime will stabilize your recovery cycle."

        elif "heart" in low_instr or "hrv" in low_instr or "blood" in low_instr:
            output = f"{prefix} your HR ({hr} bpm) and BP ({row['Blood Pressure']}) indicate you're in the {state} zone. Keep it stable by winding down at **{stop_work}**."

        elif "steps" in low_instr or "activity" in low_instr:
            output = f"{prefix} you've hit {row['Daily Steps']:,} steps. To optimize that activity, you need to be in bed by **{bedtime}** for cell repair."

        else: # Default/Category logic
            if state == "Under-Recovered":
                output = f"{prefix} you are currently redlining. For a {occ}, this burnout risk is real. Bed by **{bedtime}** is your medicine."
            else:
                output = f"{prefix} you are in a solid, stable zone. Keep this momentum by hitting your **{bedtime}** sleep target tonight."

        # Create JSONL entry
        entry = {
            "instruction": instruction,
            "input": user_input,
            "output": output
        }
        instructions.append(entry)
        
    # Save as JSONL
    with open(instructions_path, "w") as f:
        for entry in instructions:
            f.write(json.dumps(entry) + "\n")
            
    print(f"Generated {len(instructions)} instruction pairs in {instructions_path}")

if __name__ == "__main__":
    generate_instructions()
