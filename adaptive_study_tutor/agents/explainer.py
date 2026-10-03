from typing import Dict, Any
from rag.retriever import retrieve_syllabus_context
from tools.web_search import search_tavily
from langchain_google_genai import ChatGoogleGenerativeAI
from config import GOOGLE_API_KEY, DEFAULT_MODEL


def explain_topic(topic: str, query: str = "") -> Dict[str, Any]:
    """
    Generates a structured, easy-to-understand explanation for a topic using
    RAG (local syllabus notes) first, falling back to Tavily web search if needed.
    """
    search_query = query if query else topic
    rag_result = retrieve_syllabus_context(search_query)

    syllabus_context = ""
    web_context = ""
    sources_used = []

    if rag_result["found"]:
        syllabus_context = rag_result["context"]
        sources_used.extend([f"Syllabus File: {s}" for s in rag_result["sources"]])

    # If RAG context is missing or brief, run Tavily search for supplementary info
    if not syllabus_context or len(syllabus_context) < 100:
        web_res = search_tavily(search_query)
        if web_res["success"]:
            web_context = web_res["summary"]
            sources_used.append("Supplementary Web Source (Tavily)")

    # Prepare LLM explanation prompt
    if GOOGLE_API_KEY and GOOGLE_API_KEY != "your_google_api_key_here":
        try:
            llm = ChatGoogleGenerativeAI(
                model=DEFAULT_MODEL,
                google_api_key=GOOGLE_API_KEY,
                temperature=0.2
            )
            
            prompt = f"""You are a helpful and clear AI tutor for school and college students.
Explain the topic: "{search_query}"

Context available:
--- SYLLABUS NOTES ---
{syllabus_context if syllabus_context else 'No direct syllabus match found.'}

--- SUPPLEMENTARY WEB CONTEXT ---
{web_context if web_context else 'Not required/used.'}

Please structure your explanation as follows:
### 📌 Concept Explanation
(Simple, clear explanation suitable for a student)

### 💡 Real-World Example
(A concrete, practical example demonstrating the concept)

### ⭐ Important Key Points
(Bullet points of key formulas, rules, or takeaways)

### 📚 Reference Sources
(Specify clearly whether "Syllabus Source" or "Supplementary Web Source" was used)
"""
            response = llm.invoke(prompt)
            explanation_text = response.content.strip()

        except Exception as e:
            explanation_text = f"Error generating explanation: {e}\n\n" + _format_raw_fallback(topic, syllabus_context, web_context)
    else:
        explanation_text = _format_raw_fallback(topic, syllabus_context, web_context)

    return {
        "topic": topic,
        "explanation": explanation_text,
        "sources": sources_used,
        "used_rag": bool(syllabus_context),
        "used_web": bool(web_context)
    }


def _format_raw_fallback(topic: str, syllabus: str, web: str) -> str:
    """Fallback text structure when LLM is unavailable."""
    content = syllabus if syllabus else web
    if not content:
        content = f"{topic} is an important academic topic. Review your textbooks and practice questions."

    return f"""### 📌 Concept Explanation
{content}

### 💡 Real-World Example
Consider practical scenarios where {topic} applies in real life.

### ⭐ Important Key Points
- Core definitions and principles
- Practical application rules

### 📚 Reference Sources
{"Syllabus Source" if syllabus else "General Knowledge / Web Source"}
"""
