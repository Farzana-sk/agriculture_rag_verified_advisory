import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

DATA_DIR = ROOT_DIR / "data"
RAW_PDF_DIR = DATA_DIR / "raw_pdfs"
CHROMA_DB_DIR = str(ROOT_DIR / "chroma_db")
SQLITE_PATH = DATA_DIR / "advisory.db"
TEST_QUESTIONS_CSV = DATA_DIR / "test_questions.csv"
EVAL_RESULTS_CSV = DATA_DIR / "evaluation_results.csv"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = os.getenv("GROQ_LLM_MODEL", "openai/gpt-oss-20b")
STT_MODEL = os.getenv("GROQ_STT_MODEL", "whisper-large-v3-turbo")
TAU_THRESHOLD = float(os.getenv("TAU_THRESHOLD", "0.60"))
RETRIEVE_K = int(os.getenv("RETRIEVE_K", "5"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

SKIP_PDF_SUBSTRINGS = (
    "test_questions",
    "project_abstract",
    "reference",
    "context-aware",
    "collini",
)

SAFE_REFUSAL = (
    "Insufficient information in the agricultural knowledge base. "
    "Official Package of Practices documents do not support a verified "
    "recommendation for this query."
)


def require_groq_key() -> str:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found. Add it to the .env file.")
    return GROQ_API_KEY
