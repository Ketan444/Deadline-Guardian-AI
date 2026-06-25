from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from database import engine, SessionLocal
from models import Base, Task

from agents.gemini_agent import run_agent
from agents.scheduler import generate_schedule
from agents.burnout_detector import detect_burnout

app = FastAPI(title="Deadline Guardian AI")

Base.metadata.create_all(bind=engine)


class UserInput(BaseModel):
    text: str


class ChatRequest(BaseModel):
    question: str


@app.get("/")
def home():
    return {"message": "Deadline Guardian AI Running"}


def _current_state() -> dict:
    """Reads pending tasks back out of the database and builds the same
    tasks/schedule/burnout shape the UI already expects, now backed by
    real agent-driven data instead of the old keyword-matching pipeline.
    """
    db = SessionLocal()
    tasks = db.query(Task).filter(Task.status != "Done").all()
    task_list = [
        {
            "title": t.title,
            "deadline": t.deadline,
            "priority": t.priority,
            "allocated_hours": t.allocated_hours or 0,
            "risk_score": t.risk_score or 0,
        }
        for t in tasks
    ]
    db.close()

    schedule = generate_schedule(task_list)
    total_hours = sum(t["allocated_hours"] for t in task_list) or 1
    burnout = detect_burnout(len(task_list), total_hours)

    return {"tasks": task_list, "schedule": schedule, "burnout": burnout}


@app.post("/plan")
def create_plan(user_input: UserInput):
    if not user_input.text.strip():
        raise HTTPException(status_code=400, detail="Input cannot be empty.")

    try:
        agent_reply = run_agent(user_input.text)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {exc}")

    state = _current_state()
    state["agent_reply"] = agent_reply
    return state


@app.post("/chat")
def chat_agent(data: ChatRequest):
    if not data.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        answer = run_agent(data.question)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {exc}")

    return {"answer": answer}
