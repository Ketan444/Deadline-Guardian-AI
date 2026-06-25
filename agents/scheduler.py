from datetime import datetime, timedelta

WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}

PRIORITY_RANK = {"High": 0, "Medium": 1, "Low": 2}


def _parse_deadline(deadline_str, today=None):
    """Best-effort parse of a deadline string into an actual date.

    Handles explicit dates and weekday names ("Friday" -> the next
    occurrence of that weekday, treating today's own weekday as today).
    Falls back to one week out if the text can't be parsed at all, so a
    messy deadline still gets scheduled instead of silently disappearing.
    """
    today = today or datetime.now().date()
    if not deadline_str:
        return today + timedelta(days=7)

    text = deadline_str.strip().lower()

    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    for fmt in ("%B %d", "%b %d"):
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.date().replace(year=today.year)
        except ValueError:
            continue

    for name, idx in WEEKDAYS.items():
        if name in text:
            days_ahead = (idx - today.weekday()) % 7
            return today + timedelta(days=days_ahead)

    return today + timedelta(days=7)


def allocate_hours(tasks, available_hours):
    if not tasks:
        return []

    total_tasks = len(tasks)
    hours_per_task = round(available_hours / total_tasks, 2)

    for task in tasks:
        task["allocated_hours"] = hours_per_task

    return tasks


def generate_schedule(tasks):
    """Lays tasks out on real calendar days. A task is never scheduled
    after its own deadline -- tasks with closer deadlines and higher
    priority get earlier slots, and if there isn't enough runway before
    a deadline, the task is scheduled on the deadline day itself rather
    than silently slipping past it.
    """
    if not tasks:
        return []

    today = datetime.now().date()

    enriched = []
    for task in tasks:
        deadline_date = _parse_deadline(task.get("deadline"), today)
        priority_rank = PRIORITY_RANK.get(task.get("priority"), 1)
        enriched.append((deadline_date, priority_rank, task))

    enriched.sort(key=lambda t: (t[0], t[1]))

    schedule = []
    cursor = today
    for deadline_date, _priority_rank, task in enriched:
        scheduled_date = min(cursor, deadline_date)

        schedule.append(
            {
                "task": task["title"],
                "date": scheduled_date.strftime("%Y-%m-%d"),
                "hours": task.get("allocated_hours", 0),
            }
        )

        cursor = max(cursor, scheduled_date) + timedelta(days=1)

    return schedule