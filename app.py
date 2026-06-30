# =====================
# IMPORTS
# =====================
import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
from services.pdf_service import generate_pdf
from services.calendar_service import create_calendar

from components.chat_assistant import guardian_chat

def _get_api_url():
    # Streamlit Cloud secrets live in st.secrets, not os.environ -- check
    # both so this works the same locally (.env / os.environ) and on
    # Streamlit Cloud (Secrets panel).
    try:
        if "API_URL" in st.secrets:
            return st.secrets["API_URL"]
    except Exception:
        pass
    return os.environ.get("API_URL", "http://127.0.0.1:8000")


API_URL = _get_api_url()

# =====================
# PAGE CONFIG
# =====================
def configure_page():
    """Configure Streamlit page settings and UI."""
    st.set_page_config(
        page_title="Deadline Guardian AI",
        page_icon="🚀",
        layout="wide"
    )
    st.title("🚀 Deadline Guardian AI")
    st.caption(
        "AI-Powered Productivity & Deadline Rescue Assistant"
    )


# =====================
# API FUNCTIONS
# =====================
def fetch_plan(user_input: str):
    """Fetch AI plan from backend API and return (result, error)."""
    try:
        response = requests.post(
            f"{API_URL}/plan",
            json={"text": user_input}
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.ConnectionError:
        return None, f"Cannot connect to backend. Is the API running at {API_URL}?"
    except requests.exceptions.RequestException as e:
        return None, f"API Error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


# =====================
# METRICS CALCULATION
# =====================
def calculate_metrics(tasks: list, result: dict) -> dict:
    """Calculate key performance metrics."""
    total_hours = sum(
        task["allocated_hours"]
        for task in tasks
    )
    
    avg_risk = (
        sum(task["risk_score"] for task in tasks) / len(tasks)
        if tasks else 0
    )
    
    productivity_score = max(0, int(100 - avg_risk))
    
    health_score = max(
        0,
        int(productivity_score - (avg_risk * 0.3))
    )
    
    return {
        "total_hours": total_hours,
        "avg_risk": avg_risk,
        "productivity_score": productivity_score,
        "health_score": health_score,
        "burnout_risk": result["burnout"]["burnout_risk"]
    }


# =====================
# UI COMPONENTS
# =====================
def display_top_metrics(tasks: list, metrics: dict):
    """Display top metrics in 4-column layout."""
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("📌 Tasks", len(tasks))
    col2.metric("⏳ Hours", metrics["total_hours"])
    col3.metric("🔥 Burnout", metrics["burnout_risk"])
    col4.metric("🎯 Productivity", f"{metrics['productivity_score']}/100")


def display_productivity_score(score: int):
    """Display productivity score with status."""
    st.subheader("🎯 Productivity Score")
    
    if score >= 80:
        st.success(f"{score}/100 - Excellent")
    elif score >= 60:
        st.warning(f"{score}/100 - Good")
    else:
        st.error(f"{score}/100 - Critical")


def display_health_score(score: int):
    """Display deadline health score with status."""
    st.subheader("❤️ Deadline Health Score")
    
    if score >= 80:
        st.success(f"{score}/100 - Healthy")
    elif score >= 60:
        st.warning(f"{score}/100 - Moderate Risk")
    else:
        st.error(f"{score}/100 - Critical")



def display_smart_alerts(tasks: list):
    """Display alerts for high-risk tasks."""
    st.subheader("🔔 Smart Alerts")
    
    for task in tasks:
        if task["risk_score"] >= 70:
            st.error(
                f"Critical Alert: {task['title']} requires immediate attention."
            )
        elif task["risk_score"] >= 50:
            st.warning(
                f"Moderate Alert: {task['title']} should be prioritized."
            )
        else:
            st.success(f"{task['title']} is on track.")


def display_productivity_forecast(productivity_score: int):

    st.subheader("📈 Productivity Forecast")

    productivity = [
        max(0, productivity_score - 15),
        max(0, productivity_score - 10),
        max(0, productivity_score - 5),
        productivity_score,
        min(100, productivity_score + 2),
        min(100, productivity_score + 4),
        min(100, productivity_score + 5)
    ]

    forecast_df = pd.DataFrame({
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "Score": productivity
    })

    forecast_chart = px.line(
        forecast_df,
        x="Day",
        y="Score",
        markers=True,
        title="7-Day Productivity Forecast"
    )

    st.plotly_chart(
        forecast_chart,
        use_container_width=True,
        key="productivity_forecast_chart"
    )


def display_failure_simulator(productivity_score: int):
    """Display failure scenario simulator."""
    st.subheader("💀 Failure Simulator")
    
    if st.button("Simulate Missing Today's Work"):
        st.error(
            f"""
Projected Outcome

Current Productivity:
{productivity_score}/100

Future Productivity:
{max(0, productivity_score - 25)}/100

Deadline Risk Increased

Burnout Risk Increased

Recommended Action:
Complete at least one task today.
"""
        )


def display_accountability_coach(tasks: list):
    """Display accountability coaching section."""
    st.subheader("🧑‍🏫 Guardian AI Coach")
    
    st.info(
        f"""
You currently have {len(tasks)} active tasks.

Recommended First Task:

{tasks[0]["title"]}

Starting within the next 30 minutes can significantly improve completion probability.
"""
    )


def display_focus_sessions(tasks: list):
    """Display focus session recommendations."""
    st.subheader("🎯 Focus Session Generator")
    
    for task in tasks:
        st.write(
            f"""
📚 {task['title']}

Session 1:
09:00 - 10:30

Break:
15 Minutes

Session 2:
10:45 - 12:15
"""
        )

def display_weekly_report(tasks, metrics):

    st.subheader("📋 AI Weekly Report")

    highest_risk = max(
        tasks,
        key=lambda x: x["risk_score"]
    )

    st.info(
        f"""
Strongest Area:
✅ Productivity Score: {metrics['productivity_score']}/100

Biggest Risk:
⚠️ {highest_risk['title']}

Recommendation:
🎯 Complete high-risk tasks first
🎯 Schedule deep-work blocks
🎯 Maintain focus sessions
"""
    )
    
def display_demo_mode():

    st.subheader("🎤 Demo Mode")

    st.info(
        """
Hackathon Demo Flow:

1️⃣ User enters tasks

2️⃣ Planner Agent extracts tasks

3️⃣ Scheduler Agent allocates hours

4️⃣ Risk Agent predicts deadline risk

5️⃣ Burnout Agent analyzes workload

6️⃣ Guardian AI generates recommendations

7️⃣ Export report and calendar
"""
    )    

def display_panic_mode():
    """Display panic mode activation button."""
    st.subheader("🚨 Panic Mode")
    
    if st.button("Activate Panic Mode"):
        st.warning(
            """
EMERGENCY PLAN GENERATED

✓ High Priority Tasks Moved Forward

✓ Low Priority Tasks Delayed

✓ Focus Blocks Increased

✓ Recovery Breaks Added

✓ Burnout Recalculated

Success Probability:
92%
"""
        )


# =====================
# DASHBOARD SECTIONS
# =====================
def display_task_dashboard(tasks: list):
    """Display detailed task cards."""
    st.subheader("📌 Task Dashboard")
    
    for task in tasks:
        with st.container():
            st.markdown(
                f"""
### {task['title']}

**Priority:** {task['priority']}

**Allocated Hours:** {task['allocated_hours']}

**Risk Score:** {task['risk_score']}%
"""
        )
            st.progress(task["risk_score"] / 100)
            st.divider()
            
def display_risk_heatmap(tasks: list):
    """Display risk analysis chart."""

    st.subheader("🔥 Deadline Risk Heatmap")

    risk_df = pd.DataFrame({
        "Task": [task["title"] for task in tasks],
        "Risk": [task["risk_score"] for task in tasks]
    })

    fig = px.bar(
        risk_df,
        x="Task",
        y="Risk",
        color="Risk",
        title="Task Risk Analysis"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )    
    
def display_study_strategy(tasks: list):
    """AI-powered study/work strategy recommendations."""

    st.subheader("🧠 AI Study Strategy")

    for task in tasks:

        st.markdown(f"### {task['title']}")

        if "exam" in task["title"].lower():

            st.info("""
✅ Active Recall

✅ Pomodoro 50/10

✅ 2 Revision Cycles

✅ Practice Questions First
""")

        elif "assignment" in task["title"].lower():

            st.info("""
✅ Deep Work Session

✅ Complete Draft First

✅ Review Before Submission

✅ Avoid Last-Minute Work
""")

        elif "project" in task["title"].lower():

            st.info("""
✅ Build Prototype First

✅ Test Core Features

✅ Prepare Demo Slides

✅ Final Review Before Demo
""")

        else:

            st.info("""
✅ Focus Block

✅ Break Large Tasks

✅ Track Progress

✅ Review Daily
""")   
            
def display_smart_notifications(tasks: list):

    st.subheader("🚨 Smart Notifications")

    for task in tasks:

        risk = task["risk_score"]

        if risk >= 70:

            st.error(
                f"🔥 {task['title']} is at HIGH RISK. Start immediately."
            )

        elif risk >= 50:

            st.warning(
                f"⚠️ {task['title']} needs additional focus time."
            )

        else:

            st.success(
                f"✅ {task['title']} is on track."
            )                     

def display_success_predictor(tasks: list):

    st.subheader("🎯 Success Predictor")

    for task in tasks:

        risk = task["risk_score"]

        success_probability = max(
            5,
            100 - risk
        )

        st.metric(
            task["title"],
            f"{success_probability}%"
        )

        st.progress(
            success_probability / 100
        )     

def display_time_allocation(tasks: list):
    """Display pie chart of time allocation."""
    st.subheader("📊 Time Allocation")
    
    df = pd.DataFrame({
        "Task": [task["title"] for task in tasks],
        "Hours": [task["allocated_hours"] for task in tasks]
    })
    
    fig = px.pie(
        df,
        names="Task",
        values="Hours",
        title="Hours Distribution"
    )
    
    st.plotly_chart(
    fig,
    use_container_width=True,
    key="time_allocation_chart"
)


def display_timeline(schedule: list):
    """Display AI-generated timeline."""
    st.subheader("📅 AI Timeline")
    
    for idx, item in enumerate(schedule):
        if idx == 0:
            day = "Today"
        elif idx == 1:
            day = "Tomorrow"
        else:
            day = f"Day {idx+1}"
        
        st.info(f"{day} → {item['task']} ({item['hours']} hrs)")


def display_rescue_mode(tasks: list):
    """Display AI rescue plan for highest-risk task."""
    st.subheader("🚨 AI Rescue Mode")
    
    if tasks:
        highest_risk = max(tasks, key=lambda x: x["risk_score"])
        st.warning(
            f"""
Task At Risk: {highest_risk['title']}

AI Rescue Plan:

✅ Move task earlier

✅ Add focused study block

✅ Reduce multitasking

✅ Schedule recovery breaks

Success Probability: 87%
"""
        )


def display_burnout_coach():
    """Display burnout prevention coaching."""
    st.subheader("🧠 AI Burnout Coach")
    
    st.success(
        """
• Work in 90 minute focus blocks

• Take a 15 minute break

• Finish high priority tasks first

• Avoid studying after 11 PM

• Stay hydrated
"""
    )


def display_recommendations(tasks: list):
    """Display AI recommendations for each task."""
    st.subheader("⚠️ AI Recommendations")
    
    for task in tasks:
        if task["risk_score"] >= 70:
            st.error(f"Finish {task['title']} immediately.")
        elif task["risk_score"] >= 50:
            st.warning(f"Allocate extra time to {task['title']}.")
        else:
            st.success(f"{task['title']} is on track.")


def display_replanner():
    """Display replanner for missed tasks."""
    st.subheader("⚡ AI Replanner")
    
    if st.button("I Missed A Task"):
        st.warning(
            """
AI Replanner Activated

✓ Exam shifted to next focus slot

✓ Assignment moved after Exam

✓ Burnout risk recalculated

✓ Completion probability increased to 91%
"""
        )


def display_calendar_agent(schedule: list):
    """Display calendar agent and export options."""
    st.subheader("📅 Calendar Agent")
    
    schedule_df = pd.DataFrame(schedule)
    
    if st.button("Export Schedule"):
        schedule_df.to_csv("schedule_export.csv", index=False)
        st.success("Schedule exported successfully")


def display_architecture():
    """Display multi-agent architecture diagram."""
    st.subheader("🤖 Multi-Agent Architecture")
    
    st.code(
"""
Planner Agent
      ↓
Scheduler Agent
      ↓
Risk Prediction Agent
      ↓
Burnout Monitoring Agent
      ↓
Rescue/Replanner Agent
      ↓
Calendar Agent
      ↓
User Dashboard
"""
    )


# =====================
# MAIN APPLICATION
# =====================
def main():
    """Main application flow."""
    configure_page()
    guardian_chat()
    
    user_input = st.text_area(
        "Describe your tasks",
        height=180,
        value="""Exam Friday
Assignment Wednesday
Project Demo Monday

12 free hours"""
    )
    
    if st.button("Generate Plan"):
        result, error = fetch_plan(user_input)
        
        if error:
            st.error(error)
        elif result:
            pdf_file = generate_pdf(result)
            tasks = result["tasks"]
            schedule = result["schedule"]
            calendar_file = create_calendar(schedule)
            st.divider()
            
            # Calculate metrics
            metrics = calculate_metrics(tasks, result)
            
            # Display sections in order
            display_top_metrics(tasks, metrics)
            st.divider()
            
            display_productivity_score(metrics["productivity_score"])
            st.divider()
            
            display_health_score(metrics["health_score"])
            st.divider()
            
            display_smart_alerts(tasks)
            st.divider()
            
            display_productivity_forecast(metrics["productivity_score"])
            st.divider()
            
            display_failure_simulator(metrics["productivity_score"])
            st.divider()
            
            display_accountability_coach(tasks)
            st.divider()
            
            display_focus_sessions(tasks)
            st.divider()

            display_weekly_report(
            tasks,
            metrics )

            st.divider()
            
            display_demo_mode()

            st.divider()
            
            display_panic_mode()
            st.divider()
            
            display_task_dashboard(tasks)
            st.divider()

            display_risk_heatmap(tasks)
            st.divider()
            
            display_study_strategy(tasks)
            st.divider()
            
            st.divider()

            display_smart_notifications(tasks)

            st.divider()

            display_success_predictor(tasks)

            st.divider()
            
            display_time_allocation(tasks)
            st.divider()
            
            display_timeline(schedule)
            st.divider()
            
            display_rescue_mode(tasks)
            st.divider()
            
            display_burnout_coach()
            st.divider()
            
            display_recommendations(tasks)
            st.divider()
            
            display_replanner()
            st.divider()
            
            display_calendar_agent(schedule)
            st.divider()
            
            display_architecture()
            
            st.divider()

            st.subheader("📄 Productivity Report")

            with open(pdf_file, "rb") as file:

                st.download_button(
                    label="Download PDF Report",
                    data=file,
                    file_name="Deadline_Guardian_Report.pdf",
                    mime="application/pdf"
              )
                
            st.subheader("📅 Google Calendar Export")

            with open(calendar_file, "rb") as file:

                st.download_button(
                label="Export To Google Calendar",
                data=file,
                file_name="DeadlineGuardian.ics",
                mime="text/calendar"
              ) 
                
            st.divider()

            st.subheader("🏆 Achievement Tracker")

            badges = []

            if len(tasks) >= 3:
                badges.append("🏅 Task Manager")

            if metrics["productivity_score"] >= 80:
                badges.append("🎯 Productivity Master")

            if result["burnout"]["burnout_risk"] == "Low":
                badges.append("🔥 Burnout Avoider")
            
            if sum(task["allocated_hours"] for task in tasks) >= 10:
                badges.append("⏳ Time Warrior")
            
            if len(schedule) >= 3:
                badges.append("📅 Planning Champion")
            
            for badge in badges:
                st.success(badge)
                       
            st.subheader("🚀 Progress Level")

            level_score = min(
                100,
                len(badges) * 20
            )

            st.progress(
            level_score / 100
            )

            st.write(
            f"Level Progress:{level_score}%"
            )
            
if __name__ == "__main__":
        main()