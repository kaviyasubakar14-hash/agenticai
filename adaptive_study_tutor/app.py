import streamlit as st
import pandas as pd
from config import check_api_keys, DB_PATH
from tools.progress_tools import init_db, get_student_progress, get_weak_topics
from agents.graph import tutor_graph

# Page Configuration
st.set_page_config(
    page_title="Adaptive Study Tutor",
    page_icon="🎓",
    layout="wide"
)

# Auto-initialize database
init_db(DB_PATH)

# Check API Keys
api_status = check_api_keys()

# Custom CSS styling for cards
st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.5rem; }
    .stCard { background-color: #F8FAFC; padding: 1.2rem; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 1rem; }
    .metric-card { background: #EFF6FF; border-left: 4px solid #3B82F6; padding: 1rem; border-radius: 6px; }
    .weak-card { background: #FEF2F2; border-left: 4px solid #EF4444; padding: 1rem; border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🎓 Adaptive Study Tutor</h1>", unsafe_allow_html=True)

if not api_status["google"]:
    st.warning("⚠️ **Google API Key not detected.** Set `GOOGLE_API_KEY` in `.env` to enable full Gemini AI features. System is operating with standard local fallback responses.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Student Preferences")
    student_name = st.text_input("Student Name", value="Alex")
    subject = st.selectbox("Subject", ["Physics / Science", "Computer Science", "General Studies"])
    
    default_topics = {
        "Physics / Science": ["Newton's third law", "Photosynthesis"],
        "Computer Science": ["Java Inheritance", "Data Structures", "Arrays", "Trees"],
        "General Studies": ["General Science"]
    }
    
    topic = st.selectbox("Select Topic", default_topics.get(subject, ["General Topic"]))
    custom_topic = st.text_input("Or enter custom topic", value="")
    active_topic = custom_topic.strip() if custom_topic.strip() else topic
    
    difficulty = st.radio("Difficulty Level", ["Easy", "Medium", "Hard"], index=1)
    
    st.divider()
    nav_option = st.radio(
        "Navigation",
        ["📚 Ask Tutor", "📝 Take Quiz", "📊 My Progress", "🎯 Weak Topics", "📅 Revision Plan"]
    )

# --- 1. ASK TUTOR SECTION ---
if nav_option == "📚 Ask Tutor":
    st.subheader("📚 Learn & Ask Tutor")
    st.caption("Ask syllabus questions or request topic explanations.")
    
    sample_queries = [
        f"Explain {active_topic} with an example.",
        "Explain Newton's third law with an example.",
        "Explain inheritance in Java simply.",
        "What is photosynthesis?"
    ]
    
    st.write("**Quick Sample Prompts:**")
    cols = st.columns(len(sample_queries))
    selected_prompt = None
    for idx, prompt_text in enumerate(sample_queries):
        if cols[idx].button(prompt_text, key=f"btn_{idx}"):
            selected_prompt = prompt_text

    user_query = st.text_area(
        "Your Question:",
        value=selected_prompt if selected_prompt else f"Explain {active_topic} with an example.",
        height=100
    )
    
    if st.button("🚀 Ask Tutor", type="primary"):
        with st.spinner("Retrieving syllabus notes and preparing explanation..."):
            initial_state = {
                "student": student_name,
                "topic": active_topic,
                "difficulty": difficulty,
                "query": user_query,
                "intent": "EXPLAIN"
            }
            final_state = tutor_graph.invoke(initial_state)
            exp_res = final_state.get("explanation_result", {})
            
            st.markdown(exp_res.get("explanation", "No explanation generated."))
            
            if exp_res.get("sources"):
                st.info("📌 **Sources Used:** " + ", ".join(exp_res["sources"]))

# --- 2. TAKE QUIZ SECTION ---
elif nav_option == "📝 Take Quiz":
    st.subheader(f"📝 Quiz: {active_topic}")
    st.caption(f"Difficulty: {difficulty} | Student: {student_name}")
    
    if "quiz_session" not in st.session_state or st.session_state.get("quiz_topic") != active_topic:
        if st.button("🎯 Generate New Quiz", type="primary"):
            with st.spinner("Generating quiz questions..."):
                state = tutor_graph.invoke({
                    "student": student_name,
                    "topic": active_topic,
                    "difficulty": difficulty,
                    "query": f"Quiz me on {active_topic}",
                    "intent": "QUIZ"
                })
                st.session_state["quiz_session"] = state.get("quiz_data", {})
                st.session_state["quiz_topic"] = active_topic
                st.session_state["submitted"] = False
    
    quiz_data = st.session_state.get("quiz_session")
    if quiz_data and quiz_data.get("questions"):
        questions = quiz_data["questions"]
        student_answers = {}
        
        st.write("---")
        with st.form("quiz_form"):
            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}: {q.get('question')}**")
                options = q.get("options", {})
                opt_labels = [f"{k}. {v}" for k, v in options.items()]
                choice = st.radio("Select answer:", opt_labels, key=f"q_{q.get('id')}", index=None)
                student_answers[q.get("id")] = choice[0] if choice else ""
                st.write("")
                
            submitted = st.form_submit_button("Submit Quiz Answers", type="primary")
            
        if submitted:
            with st.spinner("Grading quiz and updating progress..."):
                eval_state = tutor_graph.invoke({
                    "student": student_name,
                    "topic": active_topic,
                    "quiz_data": quiz_data,
                    "student_answers": student_answers,
                    "intent": "EVALUATE"
                })
                res = eval_state.get("evaluation_result", {})
                
                st.balloons() if res.get("percentage", 0) >= 60 else None
                
                st.markdown(f"### Score: {res.get('score')}/{res.get('total')} ({res.get('percentage')}%)")
                st.info(res.get("feedback"))
                
                for r in res.get("question_results", []):
                    icon = "✅" if r["is_correct"] else "❌"
                    st.write(f"{icon} **Q{r['id']}:** {r['question']}")
                    st.write(f"- Your Answer: `{r['student_answer']}` | Correct: `{r['correct_answer']}`")
                    st.caption(f"Explanation: {r['explanation']}")
                    st.write("---")
    else:
        st.info("Click 'Generate New Quiz' above to start your practice test.")

# --- 3. MY PROGRESS SECTION ---
elif nav_option == "📊 My Progress":
    st.subheader(f"📊 Progress History for {student_name}")
    records = get_student_progress(student_name)
    
    if records:
        df = pd.DataFrame(records)
        df_display = df[["topic", "score", "total", "percentage", "timestamp"]].rename(columns={
            "topic": "Topic", "score": "Score", "total": "Total",
            "percentage": "Percentage (%)", "timestamp": "Date/Time"
        })
        st.dataframe(df_display, use_container_width=True)
        st.line_chart(df.set_index("timestamp")["percentage"])
    else:
        st.info("No quiz attempts recorded yet. Take a quiz to start tracking progress!")

# --- 4. WEAK TOPICS SECTION ---
elif nav_option == "🎯 Weak Topics":
    st.subheader(f"🎯 Weak Topic Analysis for {student_name}")
    weak_topics = get_weak_topics(student_name)
    
    if weak_topics:
        st.write("Topics where your average score is below **60%**:")
        for w in weak_topics:
            st.markdown(f"""
                <div class='weak-card'>
                    <h4>📌 {w['topic']}</h4>
                    <p><b>Attempts:</b> {w['attempts']} | <b>Average Score:</b> {w['avg_score']}% | <b>Status:</b> ⚠️ {w['status']}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.success("🎉 No weak topics detected! Your average score across all attempted topics is 60% or higher.")

# --- 5. REVISION PLAN SECTION ---
elif nav_option == "📅 Revision Plan":
    st.subheader("📅 Personalized Revision Schedule")
    
    col1, col2 = st.columns(2)
    with col1:
        exam_target = st.text_input("Target Exam Date / Timeframe", value="In 7 Days")
    with col2:
        study_hours = st.number_input("Available Study Hours per Day", min_value=0.5, max_value=12.0, value=2.0, step=0.5)
        
    if st.button("✨ Generate Revision Plan", type="primary"):
        with st.spinner("Building custom revision plan based on weak topics..."):
            rev_state = tutor_graph.invoke({
                "student": student_name,
                "exam_date": exam_target,
                "available_hours": study_hours,
                "intent": "REVISION"
            })
            plan_res = rev_state.get("revision_result", {})
            st.markdown(plan_res.get("plan", "No plan created."))
