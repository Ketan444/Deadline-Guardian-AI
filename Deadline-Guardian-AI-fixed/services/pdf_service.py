from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(result):

    pdf_path = "productivity_report.pdf"

    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "Deadline Guardian AI Report",
            styles["Title"]
        )
    )

    content.append(
        Spacer(1, 20)
    )

    for task in result["tasks"]:

        content.append(
            Paragraph(
                f"""
Task: {task['title']}
<br/>
Priority: {task['priority']}
<br/>
Hours: {task['allocated_hours']}
<br/>
Risk: {task['risk_score']}%
                """,
                styles["BodyText"]
            )
        )

        content.append(
            Spacer(1, 10)
        )

    content.append(
        Paragraph(
            f"""
Burnout Risk:
{result['burnout']['burnout_risk']}
            """,
            styles["Heading2"]
        )
    )

    doc.build(content)

    return pdf_path