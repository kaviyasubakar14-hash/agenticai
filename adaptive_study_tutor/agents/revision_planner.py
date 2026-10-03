from typing import Dict, Any, List
from tools.progress_tools import get_weak_topics
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY, DEFAULT_MODEL


def generate_revision_plan(
    student: str,
    exam_date: str = "In 7 Days",
    available_hours: float = 2.0
) -> Dict[str, Any]:
    """
    Retrieves weak topics for student from SQLite and builds a structured,
    day-by-day revision plan tailored to the student's exam date and daily study hours.
    """
    weak_topics_list = get_weak_topics(student)
    weak_topic_names = [t["topic"] for t in weak_topics_list]

    if not weak_topic_names:
        topics_str = "General Revision (All recent subjects: Newton's Laws, Photosynthesis, Java Inheritance, Data Structures)"
    else:
        topics_str = ", ".join(weak_topic_names)

    if GOOGLE_API_KEY and GOOGLE_API_KEY != "your_google_api_key_here":
        try:
            llm = ChatGoogleGenerativeAI(
                model=DEFAULT_MODEL,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.3
            )
            prompt = f"""You are an expert academic study planner.
Create a personalized revision timetable for student '{student}'.

Inputs:
- Weak Topics requiring focus: {topics_str}
- Target Exam Date/Timeframe: {exam_date}
- Available Study Time per Day: {available_hours} hours

Requirements:
- Create a realistic 3-day to 5-day daily plan.
- Include topic review, practice quiz, and quick breaks.
- Format with clear Markdown headings for Day 1, Day 2, etc.
- Keep the plan realistic, actionable, and concise.
"""
            res = llm.invoke(prompt)
            plan_text = res.content.strip()

        except Exception as e:
            plan_text = _fallback_revision_plan(student, weak_topic_names, exam_date, available_hours)
    else:
        plan_text = _fallback_revision_plan(student, weak_topic_names, exam_date, available_hours)

    return {
        "student": student,
        "exam_date": exam_date,
        "available_hours": available_hours,
        "weak_topics": weak_topic_names,
        "plan": plan_text
    }


def _fallback_revision_plan(student: str, weak_topics: List[str], exam_date: str, hours: float) -> str:
    """Fallback revision schedule generator."""
    focus = weak_topics[0] if weak_topics else "Newton's Laws & Data Structures"
    sec_focus = weak_topics[1] if len(weak_topics) > 1 else "Java Inheritance & Photosynthesis"

    half = hours / 2

    return f"""### 📅 Personalized Revision Plan for {student}
**Exam Target:** {exam_date} | **Daily Study Budget:** {hours} Hours/Day

#### 🔹 Day 1: Priority Focus
- **{focus}** — Concept Review ({half} hours)
- **Practice Quiz & Flashcards** ({half} hours)

#### 🔹 Day 2: Secondary Focus & Application
- **{sec_focus}** — Concept Review ({half} hours)
- **Solving Sample Questions** ({half} hours)

#### 🔹 Day 3: Weak Topic Review & Mock Test
- **Weak Topics Deep Dive** — Re-read syllabus notes ({half} hours)
- **Full Retake Practice Quiz** ({half} hours)
"""
