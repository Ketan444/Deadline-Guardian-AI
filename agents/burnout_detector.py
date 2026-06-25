def detect_burnout(
    total_tasks,
    available_hours
):

    if available_hours <= 0:

        return {
            "burnout_risk": "High"
        }

    ratio = total_tasks / available_hours

    if ratio > 1:

        risk = "High"

    elif ratio > 0.5:

        risk = "Medium"

    else:

        risk = "Low"

    return {
        "burnout_risk": risk
    }