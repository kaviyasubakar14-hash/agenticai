import json
import re
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY, DEFAULT_MODEL


def generate_quiz(topic: str, difficulty: str = "Medium", number_of_questions: int = 5) -> Dict[str, Any]:
    """
    Generates a structured quiz with multiple-choice questions for a given topic and difficulty.
    """
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
        return _get_fallback_quiz(topic, difficulty, number_of_questions)

    try:
        llm = ChatGoogleGenerativeAI(
            model=DEFAULT_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.3
        )
        
        prompt = f"""You are an expert quiz generator. Generate a quiz on the topic '{topic}' with difficulty '{difficulty}'.
Create exactly {number_of_questions} multiple-choice questions.

Output ONLY valid JSON matching this exact format:
{{
  "topic": "{topic}",
  "difficulty": "{difficulty}",
  "questions": [
    {{
      "id": 1,
      "question": "Question text here?",
      "options": {{
        "A": "Option A text",
        "B": "Option B text",
        "C": "Option C text",
        "D": "Option D text"
      }},
      "answer": "A",
      "explanation": "Short explanation why A is correct."
    }}
  ]
}}

Do not include markdown code blocks or additional conversational text.
"""
        response = llm.invoke(prompt)
        text = response.content.strip()
        
        # Clean JSON formatting if enclosed in markdown ```json ... ```
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            text = json_match.group(0)
            
        data = json.loads(text)
        return data

    except Exception as e:
        print(f"Error generating quiz with Gemini: {e}")
        return _get_fallback_quiz(topic, difficulty, number_of_questions)


def _get_fallback_quiz(topic: str, difficulty: str, count: int) -> Dict[str, Any]:
    """Provides structured fallback quiz questions if API is unavailable."""
    sample_questions = [
        {
            "id": 1,
            "question": f"What is the primary core concept behind {topic}?",
            "options": {
                "A": "Fundamental principles and underlying laws",
                "B": "Arbitrary assumptions without empirical proof",
                "C": "Purely static non-interactive variables",
                "D": "None of the above"
            },
            "answer": "A",
            "explanation": f"Understanding core principles is key to mastering {topic}."
        },
        {
            "id": 2,
            "question": f"Which of the following best demonstrates {topic} in practice?",
            "options": {
                "A": "Standard real-world physical or logical application",
                "B": "Complex random behavior",
                "C": "Ignoring system bounds",
                "D": "System shutdown"
            },
            "answer": "A",
            "explanation": "Real-world application demonstrates operational behavior."
        },
        {
            "id": 3,
            "question": f"In a standard evaluation of {topic}, which factor is most critical?",
            "options": {
                "A": "Correct boundary condition handling",
                "B": "Ignoring error margins",
                "C": "Skipping validation steps",
                "D": "Using hardcoded constants"
            },
            "answer": "A",
            "explanation": "Boundary condition handling ensures system stability."
        },
        {
            "id": 4,
            "question": f"What is a common misconception regarding {topic}?",
            "options": {
                "A": "That it operates in isolation without external factors",
                "B": "That it can be represented logically",
                "C": "That it has practical uses",
                "D": "That students can learn it"
            },
            "answer": "A",
            "explanation": "Most concepts depend on broader system context."
        },
        {
            "id": 5,
            "question": f"How can a student best review and master {topic}?",
            "options": {
                "A": "By solving practice problems and reviewing weak areas",
                "B": "By memorizing terms without understanding",
                "C": "By skipping revision sessions",
                "D": "By reading once without practice"
            },
            "answer": "A",
            "explanation": "Active recall and targeted practice yield optimal retention."
        }
    ]
    
    return {
        "topic": topic,
        "difficulty": difficulty,
        "questions": sample_questions[:count]
    }
