from .health_states import determine_health_state
from .heuristics.recovery import recovery_decisions
from .heuristics.sleep import sleep_decisions
from .phrasing import generate_briefing

def run_engine(inputs: dict) -> dict:
    """
    The Brain: Orchestrates the flow from Input -> State -> Decisions.
    Deterministic. No AI.
    """
    
    # 1. Determine Core State
    state = determine_health_state(
        sleep_hours=inputs["sleep_hours"],
        stress_level=inputs["stress_level"],
        resting_hr=inputs["resting_hr"],
        bp_str=inputs.get("blood_pressure", "120/80")
    )
    
    # 2. Run Heuristic Modules
    recovery_out = recovery_decisions(
        health_state=state, 
        stress_level=inputs["stress_level"],
        resting_hr=inputs["resting_hr"],
        bp_str=inputs.get("blood_pressure", "120/80")
    )
    sleep_out = sleep_decisions(state)
    
    # 3. Generate Deterministic Briefing
    briefing = generate_briefing(
        state=state,
        reason_codes=recovery_out['reason_codes'],
        workout_allowed=recovery_out['workout_allowed']
    )
    
    # 4. Construct Final Decision Object (Schema Compliant)
    decision = {
        "health_state": state,
        **recovery_out,
        **sleep_out,
        "briefing": briefing,
        "hydration_target_liters": 2.5 if state == "Unknown" else 3.0
    }
    
    return decision
