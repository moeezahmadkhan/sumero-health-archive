def determine_health_state(sleep_hours: float, stress_level: int, resting_hr: int, bp_str: str = "120/80") -> str:
    """
    Medical-Grade Calibration: Incorporates Sleep, Stress, HR, and BP.
    
    Rules:
    - Sleep < 6h -> "Sleep_Deprived"
    - Sleep < 7h OR Stress >= 7 -> "Under_Recovered"
    - HR > 80 BPM (Elevated Resting) -> "Under_Recovered"
    - BP > 135/88 (Hypertension Proxy) -> "Under_Recovered"
    - Otherwise -> "Well_Recovered"
    """
    # Parse Blood Pressure
    try:
        sys_bp, dia_bp = map(int, bp_str.split('/'))
    except:
        sys_bp, dia_bp = 120, 80 # Default fallback
        
    if sleep_hours < 6.0:
        return "Sleep_Deprived"
    
    # Check physiological strain markers
    is_strained = (
        sleep_hours < 7.0 or 
        stress_level >= 7 or 
        resting_hr > 80 or 
        sys_bp > 135 or 
        dia_bp > 88
    )
    
    if is_strained:
        return "Under_Recovered"
    
    return "Well_Recovered"
