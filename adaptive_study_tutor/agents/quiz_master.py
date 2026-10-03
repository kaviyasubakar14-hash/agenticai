from typing import Dict, Any
from tools.quiz_tools import generate_quiz


def create_quiz_session(topic: str, difficulty: str = "Medium", count: int = 5) -> Dict[str, Any]:
    """
    Creates a new quiz session for the given topic and difficulty.
    Answers are contained in the quiz dict but kept hidden in the UI until submission.
    """
    quiz_data = generate_quiz(topic=topic, difficulty=difficulty, number_of_questions=count)
    return {
        "topic": quiz_data.get("topic", topic),
        "difficulty": quiz_data.get("difficulty", difficulty),
        "questions": quiz_data.get("questions", []),
        "status": "ready"
    }
