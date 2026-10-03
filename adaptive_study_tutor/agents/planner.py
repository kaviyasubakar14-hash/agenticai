import re
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY, DEFAULT_MODEL


def plan_user_intent(query: str) -> Dict[str, Any]:
    """
    Analyzes user input to determine intent: EXPLAIN, QUIZ, REVIEW, or REVISION.
    Extracts topic or timeframe parameters if present.
    """
    q_lower = query.lower().strip()

    # Fast rule-based matching for quick response
    if any(k in q_lower for k in ["quiz", "test me", "question"]):
        intent = "QUIZ"
    elif any(k in q_lower for k in ["weak", "progress", "score", "performance", "my progress"]):
        intent = "REVIEW"
    elif any(k in q_lower for k in ["revision", "schedule", "plan", "timetable", "exam"]):
        intent = "REVISION"
    else:
        intent = "EXPLAIN"

    # Use LLM for refined topic extraction if API key available
    if GOOGLE_API_KEY and GOOGLE_API_KEY != "your_google_api_key_here":
        try:
            llm = ChatGoogleGenerativeAI(
                model=DEFAULT_MODEL,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.0
            )
            prompt = f"""Analyze this student request: "{query}"

Classify into one of these intents:
- EXPLAIN (asking for explanation of a concept/topic)
- QUIZ (asking for a quiz or practice questions)
- REVIEW (asking about progress, performance, or weak topics)
- REVISION (asking for a revision plan or study schedule)

Extract the main topic if specified.

Reply in format:
INTENT: <INTENT>
TOPIC: <TOPIC_NAME or None>
"""
            res = llm.invoke(prompt).content.strip()
            lines = res.split("\n")
            extracted_intent = intent
            topic = ""
            for line in lines:
                if line.startswith("INTENT:"):
                    extracted_intent = line.replace("INTENT:", "").strip().upper()
                elif line.startswith("TOPIC:"):
                    topic = line.replace("TOPIC:", "").strip()
            
            if extracted_intent in ["EXPLAIN", "QUIZ", "REVIEW", "REVISION"]:
                intent = extracted_intent
                
            return {"intent": intent, "topic": topic if topic and topic != "None" else query}
        except Exception as e:
            print(f"Planner LLM fallback: {e}")

    return {"intent": intent, "topic": query}
