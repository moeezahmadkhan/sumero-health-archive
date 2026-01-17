import pandas as pd
import sys
import os

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sumero_core.engine import run_engine

def run_simulation():
    # 1. Load Data
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'Sleep_health_and_lifestyle_dataset.csv')
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print("Error: Dataset not found in sumero_core/data/")
        return

    print(f"Loaded {len(df)} users for simulation.")
    print("-" * 40)

    # 2. Iterate and Decide
    results_objects = []
    for _, row in df.iterrows():
        # Map CSV columns to our Engine Input Schema
        inputs = {
            "sleep_hours": float(row['Sleep Duration']),
            "stress_level": int(row['Stress Level']),
            "resting_hr": int(row['Heart Rate']),
            "blood_pressure": str(row['Blood Pressure']),
            "age": int(row['Age']),
            "occupation": str(row['Occupation'])
        }

        # The Brain decides
        decision = run_engine(inputs)
        results_objects.append(decision)

    # 3. Analyze Results
    total = len(results_objects)
    states = [r['health_state'] for r in results_objects]
    counts = pd.Series(states).value_counts()
    
    print("SIMULATION REPORT")
    print("-" * 40)
    print(f"Total Analyzed: {total}")
    print("\nSample Briefings (First 5 Users):")
    for i, res in enumerate(results_objects[:5]):
        print(f"\nUser {i+1} Briefing:\n{res['briefing']}")
        print("-" * 20)

    print("\nTargeted Verification (User 265 - The 'Silent Strain' Case):")
    # Using index 264 for the 265th row (0-indexed)
    print(f"User 265 Briefing:\n{results_objects[264]['briefing']}")
    print("-" * 20)

    print("\nState Distribution:")
    for state, count in counts.items():
        percentage = (count / total) * 100
        print(f"  {state}: {count} ({percentage:.1f}%)")

if __name__ == "__main__":
    run_simulation()
