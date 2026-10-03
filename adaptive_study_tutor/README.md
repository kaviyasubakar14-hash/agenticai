# 🎓 Adaptive Study Tutor

An AI-powered adaptive study tutor for school and college students. The application explains syllabus concepts using local RAG notes and supplementary web search, generates custom quizzes, grades student responses, automatically tracks weak topics in SQLite, and builds personalized revision schedules.

---

## ✨ Features

- **📚 Learn & Ask Tutor**: Get clear explanations with real-world examples and key bullet points using local RAG syllabus documents.
- **📝 Practice Quizzes**: Generate topic-specific multiple-choice quizzes with difficulty customization (Easy, Medium, Hard).
- **📊 Progress Tracking**: Auto-saves quiz scores into an SQLite database (`progress.db`) and visualizes performance history over time.
- **🎯 Weak Topic Identification**: Identifies topics with an average score below 60% and highlights them for targeted practice.
- **📅 Custom Revision Schedule**: Generates day-by-day study plans taking exam dates and daily available study hours into account.

---

## 🛠️ Technology Stack

- **Python**: 3.11+
- **Frontend**: Streamlit
- **Agent Orchestration**: LangGraph
- **LLM Engine**: Google Gemini (`langchain-google-genai`)
- **Web Search**: Tavily API (`tavily-python`)
- **Database**: Built-in Python `sqlite3`
- **Document Ingestion**: PyPDF & raw text chunking

---

## 📁 Project Structure

```text
adaptive_study_tutor/
│
├── app.py                   # Streamlit Frontend UI
├── config.py                # Environment & path configuration
├── requirements.txt         # Project dependencies
├── .env.example             # Template for API keys
├── README.md                # Project documentation
│
├── agents/                  # LangGraph nodes & graph workflow
│   ├── graph.py             # StateGraph definition & compilation
│   ├── planner.py           # Intent analysis
│   ├── explainer.py         # RAG & LLM explanation generator
│   ├── quiz_master.py       # Quiz generator node
│   ├── evaluator.py         # Answer grading & database saver
│   └── revision_planner.py  # Revision schedule generator
│
├── tools/                   # Helper functions
│   ├── quiz_tools.py        # MCQ question generator
│   ├── progress_tools.py    # SQLite database CRUD operations
│   └── web_search.py        # Tavily web search helper
│
├── rag/                     # Retrieval-Augmented Generation
│   ├── loader.py            # PDF/TXT syllabus loader & chunker
│   └── retriever.py         # Keyword & term overlap retriever
│
├── database/                # SQLite storage
│   └── progress.db          # Auto-created progress database
│
└── data/
    └── syllabus/            # Syllabus files & sample notes
        └── sample_notes.txt
```

---

## 🚀 Quick Start Guide

### 1. Installation
Clone or navigate to the project directory and install required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```
Inside `.env`:
```env
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### 3. Run the Application
Launch the Streamlit web interface:
```bash
streamlit run app.py
```

---

## 💡 Example Queries Supported

- *"Explain Newton's third law with an example."*
- *"Explain inheritance in Java."*
- *"What is photosynthesis?"*
- *"Quiz me on photosynthesis."*
- *"Give me a quiz on data structures."*
- *"What topics am I weak in?"*
- *"Make me a revision plan for my exam next week."*
