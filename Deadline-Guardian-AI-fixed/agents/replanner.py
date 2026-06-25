def replan_task(
    task_name,
    old_time,
    new_time
):

    return {
        "task": task_name,
        "old_time": old_time,
        "new_time": new_time,
        "message": f"{task_name} moved from {old_time} to {new_time}"
    }