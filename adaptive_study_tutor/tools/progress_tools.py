import sqlite3
from typing import List, Dict, Any
from config import DB_PATH, DB_DIR


def init_db(db_path=DB_PATH):
    """Creates the SQLite database and progress table if it does not exist."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student TEXT NOT NULL,
            topic TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percentage REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_progress(student: str, topic: str, score: int, total: int, db_path=DB_PATH) -> bool:
    """Saves quiz progress for a student into SQLite."""
    init_db(db_path)
    percentage = round((score / total) * 100, 2) if total > 0 else 0.0
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO progress (student, topic, score, total, percentage) VALUES (?, ?, ?, ?, ?)",
            (student.strip(), topic.strip(), score, total, percentage)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Database error saving progress: {e}")
        return False


def get_student_progress(student: str, db_path=DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves all quiz attempts for a specific student."""
    init_db(db_path)
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, student, topic, score, total, percentage, timestamp FROM progress WHERE student = ? ORDER BY timestamp DESC",
            (student.strip(),)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Database error reading progress: {e}")
        return []


def get_weak_topics(student: str, db_path=DB_PATH) -> List[Dict[str, Any]]:
    """
    Reads previous quiz scores and returns topics with average score < 60%.
    Weak topic rule: average score < 60%.
    """
    init_db(db_path)
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT topic, 
                   COUNT(id) as attempts, 
                   AVG(percentage) as avg_score 
            FROM progress 
            WHERE student = ? 
            GROUP BY topic
        """, (student.strip(),))
        rows = cursor.fetchall()
        conn.close()

        weak_topics = []
        for row in rows:
            avg_score = round(row["avg_score"], 1)
            status = "Needs Practice" if avg_score < 60.0 else "Good"
            if avg_score < 60.0:
                weak_topics.append({
                    "topic": row["topic"],
                    "attempts": row["attempts"],
                    "avg_score": avg_score,
                    "status": status
                })
        return weak_topics
    except Exception as e:
        print(f"Database error reading weak topics: {e}")
        return []
