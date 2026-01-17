def recovery_decisions(health_state: str, stress_level: int, resting_hr: int, bp_str: str) -> dict:
    """
    Decides workout permissions and nap protocols.
    Captures specific physiological reasons for the state.
    """
    reasons = []
    
    # Parse BP for reason capturing
    try:
        sys_bp, dia_bp = map(int, bp_str.split('/'))
    except:
        sys_bp, dia_bp = 120, 80

    if health_state == "Sleep_Deprived":
        return {
            "workout_allowed": False,
            "nap_recommended": True,
            "priority_focus": "sleep",
            "reason_codes": ["LOW_SLEEP"]
        }
    
    elif health_state == "Under_Recovered":
        if stress_level >= 7: reasons.append("HIGH_STRESS")
        if resting_hr > 80: reasons.append("HIGH_HR")
        if sys_bp > 135 or dia_bp > 88: reasons.append("HIGH_BP")
        if not reasons: reasons.append("LOW_SLEEP") # Fallback
        
        return {
            "workout_allowed": False,
            "nap_recommended": stress_level > 5 or sys_bp > 130,
            "priority_focus": "recovery",
            "reason_codes": reasons
        }
        
    else:
        # Well Recovered
        return {
            "workout_allowed": True,
            "nap_recommended": False,
            "priority_focus": "activity",
            "reason_codes": ["GOOD_RECOVERY"]
        }
