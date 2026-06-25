from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)

    deadline = Column(String, nullable=False)

    priority = Column(String, default="Medium")

    estimated_hours = Column(Float, default=0)

    allocated_hours = Column(Float, default=0)

    risk_score = Column(Float, default=0)

    status = Column(String, default="Pending")

    created_at = Column(DateTime, default=datetime.utcnow)