from database import SessionLocal
from models import Task


def create_task(
    title,
    deadline,
    priority,
    allocated_hours,
    risk_score
):
    db = SessionLocal()

    task = Task(
        title=title,
        deadline=deadline,
        priority=priority,
        allocated_hours=allocated_hours,
        risk_score=risk_score
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    db.close()

    return task