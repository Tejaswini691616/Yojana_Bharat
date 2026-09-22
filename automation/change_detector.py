# PATH: GovScheme/automation/change_detector.py
"""
NEW / UPDATED / UNCHANGED detection (spec section 24).
Compares an incoming candidate scheme record against what's already
stored in the `schemes` table.
"""
from models.db import query_one

TRACKED_FIELDS = ["scheme_name", "category", "eligibility", "min_age", "max_age",
                   "income_limit", "caste_requirement"]


def detect_change(candidate: dict) -> dict:
    """
    candidate: dict with at least scheme_id + TRACKED_FIELDS
    Returns: {"change_type": "NEW"|"UPDATED"|"UNCHANGED",
              "old_value": str|None, "new_value": str|None}
    """
    existing = query_one("SELECT * FROM schemes WHERE scheme_id = ?", (candidate["scheme_id"],))
    if existing is None:
        return {"change_type": "NEW", "old_value": None, "new_value": str(candidate)}

    diffs = []
    for field in TRACKED_FIELDS:
        old_v = existing.get(field)
        new_v = candidate.get(field)
        if new_v is not None and str(old_v).strip() != str(new_v).strip():
            diffs.append(f"{field}: '{old_v}' -> '{new_v}'")

    if diffs:
        return {"change_type": "UPDATED", "old_value": str(existing), "new_value": "; ".join(diffs)}
    return {"change_type": "UNCHANGED", "old_value": None, "new_value": None}
