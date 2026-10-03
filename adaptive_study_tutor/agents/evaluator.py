from typing import Dict, Any, List
from tools.progress_tools import save_progress


def evaluate_quiz_answers(
    student: str,
    topic: str,
    questions: List[Dict[str, Any]],
    student_answers: Dict[int, str]
) -> Dict[str, Any]:
    """
    Evaluates student answers, calculates score, builds feedback,
    and automatically saves the result into SQLite.
    """
    score = 0
    total = len(questions)
    results = []

    for q in questions:
        q_id = q.get("id")
        correct_ans = str(q.get("answer", "")).strip().upper()
        student_ans = str(student_answers.get(q_id, "")).strip().upper()
        is_correct = (student_ans == correct_ans)

        if is_correct:
            score += 1

        results.append({
            "id": q_id,
            "question": q.get("question"),
            "student_answer": student_ans if student_ans else "Not Answered",
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "explanation": q.get("explanation", "")
        })

    percentage = round((score / total) * 100, 1) if total > 0 else 0.0
    needs_practice = percentage < 60.0

    # Save score to SQLite database
    db_saved = save_progress(student=student, topic=topic, score=score, total=total)

    return {
        "student": student,
        "topic": topic,
        "score": score,
        "total": total,
        "percentage": percentage,
        "needs_practice": needs_practice,
        "question_results": results,
        "saved_to_db": db_saved,
        "feedback": f"Scored {score}/{total} ({percentage}%). " + (
            "Great job! You have a solid grasp of this topic." if percentage >= 60.0
            else "This topic needs further practice and review."
        )
    }
