import pandas as pd
import os

# Define paths
raw_data_path = "Sleep_health_and_lifestyle_dataset.csv"
clean_data_path = "pilot_clean.csv"

def process_data():
    if not os.path.exists(raw_data_path):
        print(f"Error: {raw_data_path} not found.")
        return

    # Load data
    df = pd.read_csv(raw_data_path)

    # STEP 1 — Keep All Relevant Columns
    cols_to_keep = [
        "Gender", "Age", "Occupation", "Sleep Duration", "Quality of Sleep",
        "Physical Activity Level", "Stress Level", "BMI Category", "Blood Pressure",
        "Heart Rate", "Daily Steps", "Sleep Disorder"
    ]
    df = df[cols_to_keep]

    # STEP 2 — Add Enhanced Health State Column
    def assign_health_state(row):
        sleep = row["Sleep Duration"]
        stress = row["Stress Level"]
        disorder = str(row["Sleep Disorder"])
        
        if sleep <= 6.1 or (disorder != "nan" and disorder != "None"):
            return "Under-Recovered"
        elif sleep >= 7.0 and stress <= 6:
            return "Optimal"
        else:
            return "Balanced"

    df["health_state"] = df.apply(assign_health_state, axis=1)

    # STEP 3 — Use Complete Dataset
    print(f"Dataset Size: {len(df)}")
    print("Health State Distribution:")
    print(df["health_state"].value_counts())

    # Save complete cleaned data
    df.to_csv(clean_data_path, index=False)
    print(f"\nSaved {len(df)} rows to {clean_data_path}")

if __name__ == "__main__":
    process_data()
