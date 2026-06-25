def calculate_risk(tasks):

    results = []

    for task in tasks:

        allocated_hours = task.get(
            "allocated_hours",
            0
        )

        if allocated_hours < 2:
            risk_score = 90

        elif allocated_hours < 4:
            risk_score = 70

        elif allocated_hours < 6:
            risk_score = 50

        else:
            risk_score = 20

        task["risk_score"] = risk_score

        results.append(task)

    return results