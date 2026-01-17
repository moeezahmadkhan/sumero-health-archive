def sleep_decisions(health_state: str) -> dict:
    """
    Decides strict bedtimes and work cutoffs based on Health State.
    """
    if health_state == "Sleep_Deprived":
        return {
            "recommended_bedtime": "21:00", # 9 PM
            "work_cutoff_time": "17:00"     # 5 PM
        }
    elif health_state == "Under_Recovered":
        return {
            "recommended_bedtime": "21:45", # 9:45 PM
            "work_cutoff_time": "18:00"     # 6 PM
        }
    else:
        return {
            "recommended_bedtime": "22:30", # 10:30 PM
            "work_cutoff_time": "19:00"     # 7 PM
        }
