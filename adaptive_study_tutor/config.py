import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "progress.db"
SYLLABUS_DIR = BASE_DIR / "data" / "syllabus"

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# LLM Model Config
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def check_api_keys():
    """Returns a dict indicating presence of required API keys."""
    return {
        "google": bool(GOOGLE_API_KEY and GOOGLE_API_KEY != "your_google_api_key_here"),
        "tavily": bool(TAVILY_API_KEY and TAVILY_API_KEY != "your_tavily_api_key_here"),
    }
