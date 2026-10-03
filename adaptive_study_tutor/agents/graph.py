from typing import TypedDict, Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from agents.planner import plan_user_intent
from agents.explainer import explain_topic
from agents.quiz_master import create_quiz_session
from agents.evaluator import evaluate_quiz_answers
from agents.revision_planner import generate_revision_plan
from tools.progress_tools import get_student_progress, get_weak_topics


class TutorState(TypedDict):
    student: str
    topic: str
    difficulty: str
    query: str
    intent: str
    explanation_result: Optional[Dict[str, Any]]
    quiz_data: Optional[Dict[str, Any]]
    student_answers: Optional[Dict[int, str]]
    evaluation_result: Optional[Dict[str, Any]]
    revision_result: Optional[Dict[str, Any]]
    progress_result: Optional[Dict[str, Any]]
    exam_date: str
    available_hours: float
    retry_count: int


# --- Node Functions ---

def planner_node(state: TutorState) -> Dict[str, Any]:
    """Node that analyzes student query to determine workflow intent."""
    query = state.get("query", "")
    plan = plan_user_intent(query)
    intent = state.get("intent") or plan["intent"]
    topic = state.get("topic") or plan["topic"] or "General Science"
    return {"intent": intent, "topic": topic}


def explainer_node(state: TutorState) -> Dict[str, Any]:
    """Node that generates concept explanations via RAG and web search."""
    topic = state.get("topic", "General Topic")
    query = state.get("query", topic)
    result = explain_topic(topic=topic, query=query)
    return {"explanation_result": result}


def quiz_master_node(state: TutorState) -> Dict[str, Any]:
    """Node that creates structured quiz questions."""
    topic = state.get("topic", "General Knowledge")
    difficulty = state.get("difficulty", "Medium")
    quiz = create_quiz_session(topic=topic, difficulty=difficulty, count=5)
    return {"quiz_data": quiz}


def evaluator_node(state: TutorState) -> Dict[str, Any]:
    """Node that evaluates quiz submission and saves score to SQLite."""
    student = state.get("student", "Student")
    topic = state.get("topic", "Quiz")
    quiz_data = state.get("quiz_data", {})
    questions = quiz_data.get("questions", []) if quiz_data else []
    student_answers = state.get("student_answers", {})
    
    result = evaluate_quiz_answers(
        student=student,
        topic=topic,
        questions=questions,
        student_answers=student_answers
    )
    return {"evaluation_result": result}


def revision_planner_node(state: TutorState) -> Dict[str, Any]:
    """Node that builds personalized revision schedule based on weak topics."""
    student = state.get("student", "Student")
    exam_date = state.get("exam_date", "In 7 Days")
    available_hours = state.get("available_hours", 2.0)
    result = generate_revision_plan(student=student, exam_date=exam_date, available_hours=available_hours)
    return {"revision_result": result}


def progress_node(state: TutorState) -> Dict[str, Any]:
    """Node that retrieves student progress history and weak topics."""
    student = state.get("student", "Student")
    history = get_student_progress(student)
    weak_topics = get_weak_topics(student)
    return {
        "progress_result": {
            "history": history,
            "weak_topics": weak_topics
        }
    }


# --- Conditional Routing ---

def route_intent(state: TutorState) -> str:
    """Routes execution from Planner to the designated handler node."""
    intent = state.get("intent", "EXPLAIN").upper()
    if intent == "QUIZ":
        return "quiz_master"
    elif intent == "EVALUATE":
        return "evaluator"
    elif intent in ["REVIEW", "PROGRESS"]:
        return "progress"
    elif intent in ["REVISION", "PLAN"]:
        return "revision_planner"
    else:
        return "explainer"


# --- Graph Construction ---

def build_tutor_graph():
    """Builds and compiles the LangGraph workflow."""
    workflow = StateGraph(TutorState)

    # Add Nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("explainer", explainer_node)
    workflow.add_node("quiz_master", quiz_master_node)
    workflow.add_node("evaluator", evaluator_node)
    workflow.add_node("revision_planner", revision_planner_node)
    workflow.add_node("progress", progress_node)

    # Set Entry Point
    workflow.set_entry_point("planner")

    # Add Conditional Edges from Planner
    workflow.add_conditional_edges(
        "planner",
        route_intent,
        {
            "explainer": "explainer",
            "quiz_master": "quiz_master",
            "evaluator": "evaluator",
            "revision_planner": "revision_planner",
            "progress": "progress"
        }
    )

    # Connect Node Endpoints
    workflow.add_edge("explainer", END)
    workflow.add_edge("quiz_master", END)
    workflow.add_edge("evaluator", END)
    workflow.add_edge("revision_planner", END)
    workflow.add_edge("progress", END)

    return workflow.compile()


# Single graph instance export
tutor_graph = build_tutor_graph()
