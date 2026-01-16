import pandas as pd
import numpy as np
import os
from datetime import datetime

# Paths
apple_hr_path = "applewatchhrv/heart_rate_data.csv"
apple_sleep_path = "applewatchhrv/sleep_data.csv"
output_path = "pilot_clean.csv"

def process_apple_data():
    print("🚀 Starting Apple Watch Data Aggregation...")
    
    # 1. Load Data
    hr_df = pd.read_csv(apple_hr_path)
    sleep_df = pd.read_csv(apple_sleep_path)
    
    # 2. Process Sleep Data
    sleep_df['Start Time'] = pd.to_datetime(sleep_df['Start Time'])
    sleep_df['End Time'] = pd.to_datetime(sleep_df['End Time'])
    sleep_df['Duration'] = (sleep_df['End Time'] - sleep_df['Start Time']).dt.total_seconds() / 3600
    sleep_df['Date'] = sleep_df['Start Time'].dt.date
    
    # Aggregating daily sleep
    daily_sleep = sleep_df.groupby('Date').agg(
        Total_Sleep=('Duration', 'sum'),
        Deep_Sleep=('Duration', lambda x: x[sleep_df.loc[x.index, 'Category'] == 'Deep'].sum()),
        REM_Sleep=('Duration', lambda x: x[sleep_df.loc[x.index, 'Category'] == 'REM'].sum()),
        Light_Sleep=('Duration', lambda x: x[sleep_df.loc[x.index, 'Category'].isin(['Light/Core', 'Core'])].sum())
    ).reset_index()
    
    # Calculate Quality of Sleep (0-10 scale)
    # Target: 20% REM, 20% Deep as "Perfect"
    def calculate_quality(row):
        total = row['Total_Sleep']
        if total == 0: return 5
        recovery_sleep = row['Deep_Sleep'] + row['REM_Sleep']
        quality = (recovery_sleep / total) * 20 # 50% recovery sleep = 10/10
        return min(round(max(quality, 4), 1), 10)

    daily_sleep['Quality of Sleep'] = daily_sleep.apply(calculate_quality, axis=1)
    
    # 3. Process Heart Rate Data
    hr_df['Timestamp'] = pd.to_datetime(hr_df['Timestamp'])
    hr_df['Date'] = hr_df['Timestamp'].dt.date
    hr_df['Hour'] = hr_df['Timestamp'].dt.hour
    
    # Calculate Resting HR (avg between 12 AM and 6 AM)
    resting_hr = hr_df[(hr_df['Hour'] >= 0) & (hr_df['Hour'] <= 6)].groupby('Date')['Heart Rate'].mean().reset_index()
    resting_hr.columns = ['Date', 'Heart Rate']
    
    # 4. Merge
    final_apple = pd.merge(daily_sleep, resting_hr, on='Date', how='inner')
    
    # 5. Map to Unified Schema
    # Gender, Age, Occupation, Sleep Duration, Quality of Sleep, Physical Activity Level, Stress Level, BMI Category, Blood Pressure, Heart Rate, Daily Steps, Sleep Disorder, health_state
    
    pilot_rows = []
    for _, row in final_apple.iterrows():
        total_sleep = round(row['Total_Sleep'], 1)
        hr = int(row['Heart Rate'])
        
        # Heuristic for Stress (inverted relationship with sleep and HR)
        stress = 7 if total_sleep < 6 else (4 if hr < 65 else 5)
        
        # Health State Logic
        if total_sleep < 6 or stress > 7:
            state = "Under-Recovered"
        elif total_sleep > 7.5 and stress < 5:
            state = "Optimal"
        else:
            state = "Balanced"
            
        pilot_rows.append({
            "Gender": "Male", # Default for this subject
            "Age": 30,
            "Occupation": "Engineer",
            "Sleep Duration": total_sleep,
            "Quality of Sleep": int(row['Quality of Sleep']),
            "Physical Activity Level": 60,
            "Stress Level": stress,
            "BMI Category": "Normal",
            "Blood Pressure": "120/80",
            "Heart Rate": hr,
            "Daily Steps": 8000,
            "Sleep Disorder": "None",
            "health_state": state,
            "Source": "AppleWatch-Raw"
        })
    
    apple_processed_df = pd.DataFrame(pilot_rows)
    
    # 6. Append to existing pilot_clean.csv
    if os.path.exists(output_path):
        existing_df = pd.read_csv(output_path)
        # Ensure Source column exists in existing
        if 'Source' not in existing_df.columns:
            existing_df['Source'] = "WHOOP-Study"
        
        combined_df = pd.concat([existing_df, apple_processed_df], ignore_index=True)
        combined_df.to_csv(output_path, index=False)
        print(f"✅ Success! Appended {len(apple_processed_df)} Apple Watch rows to {output_path}")
    else:
        apple_processed_df.to_csv(output_path, index=False)
        print(f"✅ Created {output_path} with {len(apple_processed_df)} Apple Watch rows.")

if __name__ == "__main__":
    process_apple_data()
