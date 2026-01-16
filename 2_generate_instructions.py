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
        "Should I drink more water?"
    ]

    for i, row in df.iterrows():
        # Pick a diverse instruction
        raw_instr = instructions_diversity[i % len(instructions_diversity)]
        instruction = raw_instr.replace("{Occupation}", str(row['Occupation'])).replace("{Sleep Disorder}", str(row['Sleep Disorder']))
        
        # Construct INPUT (ALL COLUMNS)
        user_input = "\n".join([f"{col}: {row[col]}" for col in df.columns])
        
        # Construct OUTPUT (Hyper-Personalized & Natural Tone)
        state = row['health_state']
        occ = str(row['Occupation'])
        dis = str(row['Sleep Disorder'])
        age = row['Age']
        hr = row['Heart Rate']
        steps = row['Daily Steps']
        quality = row['Quality of Sleep']
        stress = row['Stress Level']
        sleep_dur = row['Sleep Duration']
        
        low_instr = instruction.lower()
        greeting = random.choice(["Hey!", "Hello!", "Hi!", "Listen:"])
        
        # --- Time Heuristics & Proactive Logic ---
        # Directive advice based on biometrics
        bedtime = "9:30 PM" if stress > 7 or state == "Under-Recovered" else "10:45 PM"
        stop_work = "5:00 PM" if stress > 8 else "6:30 PM"
        nap_time = "1:45 PM" if sleep_dur < 6.5 else "None"

        if "when" in low_instr:
            if "rest" in low_instr or "stop" in low_instr:
                if state == "Under-Recovered":
                    output = f"{greeting} Right now. For a {occ} with {sleep_dur}h sleep, you're redlining. Stop work at **{stop_work}** and hit the bed by **{bedtime}**."
                else:
                    output = f"{greeting} You can push until **{stop_work}**, but then shift into recovery mode to stay Optimal."
            elif "sleep" in low_instr:
                output = f"{greeting} Your target bedtime is **{bedtime}**. You need this tonight to recover from your {occ} shift."
            elif "nap" in low_instr:
                output = f"{greeting} Take a 20-min nap at **{nap_time}** if you feel a dip. No longer than that."
        
        elif "age" in low_instr:
            if age > 50:
                output = f"{greeting} At {age}, your recovery window is different. With your {stress}/10 stress, sleep is paramount. Aim for bed by **{bedtime}** to keep your HR stable ({hr} bpm)."
            else:
                output = f"{greeting} You're {age}, but don't over-rely on your resilience. Your {sleep_dur}h sleep data says you need a reset at **{bedtime}**."
        
        elif "dizzy" in low_instr:
            output = f"{greeting} Stop working **now**. Your BP ({row['Blood Pressure']}) and stress suggest you need 500ml of water and 10 mins of rest immediately."

        elif "healthy" in low_instr:
            output = f"{greeting} To stay healthy as a {occ}, you need a ritual: Bedtime at **{bedtime}**, work ends at **{stop_work}**, and keep your steps above 6k. This is your protocol for today."

        elif "workout" in low_instr or "run" in low_instr:
            if state == "Optimal":
                output = f"{greeting} Green light! Plan a 45-min session starting around **5.30 PM**. Your biometrics are perfect for it."
            else:
                output = f"{greeting} Not today. Your body is under-recovered. Instead, do light stretching at **8.00 PM** and prioritize sleep."

        elif "tired" in low_instr:
            output = f"{greeting} I see it in your HR ({hr} bpm). You are depleted. Clear your schedule by **{stop_work}** and rest."

        else: # Default Analysis
            if state == "Under-Recovered":
                output = f"{greeting} You're in a depletion phase. Prioritize an early bedtime at **{bedtime}** above all else."
            else:
                output = f"{greeting} You're looking steady. Aim for bed by **{bedtime}** to stay in the Optimal zone."

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
