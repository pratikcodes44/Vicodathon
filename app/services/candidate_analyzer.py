"""
Candidate Evidence Analyzer service.
"""

def get_eligible_curriculum_days(candidate_profile: dict) -> list[int]:
    """
    Takes a CandidateProfile dictionary and returns a list of eligible curriculum days.
    
    A day is only eligible if it exists in the missions array, passed is true,
    and skipped is false. Missing days or omitted boolean fields are treated
    as unknown and excluded.
    """
    eligible_days = []
    missions = candidate_profile.get("missions", [])
    
    for mission in missions:
        passed = mission.get("passed")
        skipped = mission.get("skipped", False)
        day = mission.get("day")
        
        # Strict rule: passed MUST be True, and skipped MUST be False.
        if passed is True and skipped is False and day is not None:
            eligible_days.append(day)
            
    return sorted(list(set(eligible_days)))
