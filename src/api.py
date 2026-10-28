import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel, Field

try:
    from .config import TAU_THRESHOLD
    from .db import init_db, list_advisories
    from .embeddings import get_embedding_model, get_vector_store
    from .language import detect_language
    from .pipeline import run_advisory
    from .stt import transcribe_audio_bytes
    from .tts import synthesize_speech
except ImportError:  # pragma: no cover - script execution support
    from config import TAU_THRESHOLD
    from db import init_db, list_advisories
    from embeddings import get_embedding_model, get_vector_store
    from language import detect_language
    from pipeline import run_advisory
    from stt import transcribe_audio_bytes
    from tts import synthesize_speech

app = FastAPI(
    title="Voice-Based Agricultural Advisory",
    description="RAG + cosine similarity verification (tau >= 0.6)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: str | None = None


class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: str = "en"


@app.on_event("startup")
def startup() -> None:
    init_db()
    get_embedding_model()
    get_vector_store()


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
    <html>
      <body style="font-family: Segoe UI, sans-serif; max-width: 640px; margin: 40px auto;">
        <h1>Agricultural Advisory API is running</h1>
        <p>This port is the backend, not the farmer screen.</p>
        <ul>
          <li><a href="http://localhost:5173">Open farmer UI (localhost:5173)</a></li>
          <li><a href="/docs">Open API docs</a></li>
          <li><a href="/health">Health check</a></li>
        </ul>
      </body>
    </html>
    """


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "tau": TAU_THRESHOLD}


@app.post("/query")
def query(request: QueryRequest) -> dict:
    try:
        return run_advisory(request.text, request.language)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/voice")
async def voice(
    file: UploadFile = File(...),
    language: str | None = Form(default=None),
) -> dict:
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio upload.")
    try:
        transcript = transcribe_audio_bytes(
            audio_bytes,
            file.filename or "question.webm",
            language=language if language in {"en", "hi", "te"} else None,
        )
        question = transcript["text"]
        detected = language or transcript.get("language")
        result = run_advisory(question, detected)
        result["transcript"] = question
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/speak")
def speak(request: SpeakRequest) -> Response:
    audio = synthesize_speech(request.text, request.language or "en")
    return Response(content=audio, media_type="audio/mpeg")


@app.get("/history")
def history(limit: int = 20) -> dict:
    return {"items": list_advisories(limit=limit)}
