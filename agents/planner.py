import re


def extract_tasks(user_input):

    tasks = []

    lines = user_input.split("\n")

    available_hours = 8

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if "hour" in line.lower():

            nums = re.findall(r"\d+", line)

            if nums:
                available_hours = int(nums[0])

        elif "exam" in line.lower():

            tasks.append(
                {
                    "title": "Exam Preparation",
                    "deadline": "Friday",
                    "priority": "High"
                }
            )

        elif "assignment" in line.lower():

            tasks.append(
                {
                    "title": "Assignment",
                    "deadline": "Wednesday",
                    "priority": "Medium"
                }
            )

        elif "project" in line.lower():

            tasks.append(
                {
                    "title": "Project Demo",
                    "deadline": "Monday",
                    "priority": "Medium"
                }
            )

    return {
        "tasks": tasks,
        "available_hours": available_hours
    }