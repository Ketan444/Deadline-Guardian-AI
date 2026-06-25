from ics import Calendar, Event


def create_calendar(schedule):

    cal = Calendar()

    for item in schedule:

        event = Event()

        event.name = item["task"]

        event.begin = item["date"]

        event.description = (
            f"Allocated Hours: {item['hours']}"
        )

        cal.events.add(event)

    file_name = "deadline_schedule.ics"

    with open(file_name, "w") as f:
        f.writelines(cal)

    return file_name