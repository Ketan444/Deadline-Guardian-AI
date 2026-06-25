import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from database import SessionLocal
from models import Task
from agents.risk_predictor import calculate_risk
from agents.burnout_detector import detect_burnout

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Put your key in .env "
        "(get one at https://aistudio.google.com/app/apikey)."
    )

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.5-flash"

# Higher weight = bigger slice of available time.
PRIORITY_WEIGHTS = {"High": 3, "Medium": 2, "Low": 1}


# ---- Tools the model can call. Plain functions, real DB reads/writes. ----

def add_task(title: str, deadline: str, priority: str = "Medium") -> dict:
    """Adds a new task to the database.

    Args:
        title: Short description of the task.
        deadline: When it's due, e.g. "2026-06-28" or "Friday".
        priority: One of High, Medium, or Low.
    """
    db = SessionLocal()
    task = Task(title=title, deadline=deadline, priority=priority)
    db.add(task)
    db.commit()
    db.refresh(task)
    task_id = task.id
    db.close()
    return {"task_id": task_id, "status": "added"}


def list_tasks() -> dict:
    """Returns every task that isn't done yet, with deadline, priority,
    allocated hours, and risk score. Call this first if the user refers to
    something that might already exist, to avoid duplicates.
    """
    db = SessionLocal()
    tasks = db.query(Task).filter(Task.status != "Done").all()
    result = [
        {
            "id": t.id,
            "title": t.title,
            "deadline": t.deadline,
            "priority": t.priority,
            "allocated_hours": t.allocated_hours,
            "risk_score": t.risk_score,
            "status": t.status,
        }
        for t in tasks
    ]
    db.close()
    return {"tasks": result}


def calculate_time_budget(available_hours: float) -> dict:
    """Splits available hours across all pending tasks, weighted by
    priority, using real division -- and saves the result to each task.
    Call this when the user mentions how much free time they have.

    Args:
        available_hours: Total free hours available before the nearest deadline.
    """
    db = SessionLocal()
    tasks = db.query(Task).filter(Task.status != "Done").all()
    if not tasks:
        db.close()
        return {"schedule": [], "note": "No pending tasks to budget time for."}

    weights = [PRIORITY_WEIGHTS.get(t.priority, 2) for t in tasks]
    total_weight = sum(weights)

    schedule = []
    for task, weight in zip(tasks, weights):
        hours = round(available_hours * weight / total_weight, 2)
        task.allocated_hours = hours
        schedule.append({"task_id": task.id, "title": task.title, "hours": hours})

    db.commit()
    db.close()
    return {"schedule": schedule, "total_allocated": available_hours}


def assess_risk_and_burnout(available_hours: float) -> dict:
    """Calculates deadline risk for each pending task and an overall
    burnout risk for the current workload. Call this after allocating
    time, before summarizing the plan to the user.

    Args:
        available_hours: Total free hours available, used for the burnout ratio.
    """
    db = SessionLocal()
    tasks = db.query(Task).filter(Task.status != "Done").all()

    task_dicts = [{"title": t.title, "allocated_hours": t.allocated_hours or 0} for t in tasks]
    risked = calculate_risk(task_dicts)

    for t, r in zip(tasks, risked):
        t.risk_score = r["risk_score"]
    db.commit()

    burnout = detect_burnout(len(tasks), available_hours if available_hours > 0 else 1)

    result = {
        "tasks": [{"title": t.title, "risk_score": t.risk_score} for t in tasks],
        "burnout": burnout,
    }
    db.close()
    return result


def mark_task_done(task_id: int) -> dict:
    """Marks a task as completed.

    Args:
        task_id: The id of the task to mark done.
    """
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = "Done"
        db.commit()
    db.close()
    return {"task_id": task_id, "status": "done"}


AGENT_TOOLS = [
    add_task,
    list_tasks,
    calculate_time_budget,
    assess_risk_and_burnout,
    mark_task_done,
]

SYSTEM_INSTRUCTION = """You are Guardian AI, a proactive deadline and productivity \
planning agent. When the user describes their tasks, deadlines, or available time:
1. Call list_tasks first to check what already exists, so you don't create duplicates.
2. Break their situation into concrete tasks using add_task, with sensible deadlines \
and a priority (High, Medium, or Low) based on urgency and stakes.
3. If they mention how much free time they have, call calculate_time_budget with that \
number to allocate real hours per task instead of guessing.
4. Call assess_risk_and_burnout to evaluate deadline risk per task and overall burnout \
risk for their current workload.
If the user is just asking a question or wants advice rather than describing new tasks, \
you can call list_tasks to ground your answer in their real workload, then just answer \
directly without necessarily creating anything.
After acting, summarize in plain, encouraging language: the plan, which task is \
riskiest, and the overall burnout outlook. Be concise and practical, not robotic."""


def run_agent(message: str) -> str:
    """Sends a message to Gemini with the agent's tools available, and
    returns its final text reply after any function calls it decided to make.
    """
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=AGENT_TOOLS,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                maximum_remote_calls=8
            ),
        ),
    )
    return response.text
