def _matches_condition(value, condition):
    op, thr = condition["operator"], condition["threshold"]

    if op == ">":  return value > thr
    if op == ">=": return value >= thr
    if op == "<":  return value < thr
    if op == "<=": return value <= thr
    if op == "==": return value == thr

    raise ValueError(f"Unknown operator: {op}")
    
    
def _matches_entry(row, entry):
    for param, condition in entry["conditions"].items():
        if not _matches_condition(getattr(row, param), condition):
            return False
    return True

def classify_area(row, active_catalogue):
    if not row.hazard:
        return "Area 1 (known safe)"

    for entry in active_catalogue:
        if _matches_entry(row, entry):
            return "Area 2 (known unsafe - documented trigger)"

    return "Area 3 (unknown unsafe - undiscovered trigger)"

