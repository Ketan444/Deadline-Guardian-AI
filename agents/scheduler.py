from datetime import datetime, timedelta


def allocate_hours(tasks, available_hours):

    if not tasks:
        return []

    total_tasks = len(tasks)

    hours_per_task = round(
        available_hours / total_tasks,
        2
    )

    for task in tasks:

        task["allocated_hours"] = (
            hours_per_task
        )

    return tasks


def generate_schedule(tasks):

    schedule = []

    current_date = datetime.now()

    for task in tasks:

        schedule.append(
            {
                "task": task["title"],
                "date": current_date.strftime(
                    "%Y-%m-%d"
                ),
                "hours": task.get(
                    "allocated_hours",
                    0
                )
            }
        )

        current_date += timedelta(
            days=1
        )

    return schedule