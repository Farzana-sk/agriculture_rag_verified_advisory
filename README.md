# Voice-Based Multilingual Agricultural Advisory System

Grounded agricultural extension using Retrieval-Augmented Generation and post-generation answer verification (`τ ≥ 0.6`).

Farmers can ask in Telugu, Hindi, or English by voice or text. The system retrieves Package of Practices (PoP) evidence from ChromaDB, generates an answer with a Groq LLM (`openai/gpt-oss-20b`, Groq's replacement after `llama-3.1-8b-instant` was retired), then **releases the answer only if cosine similarity between the answer and retrieved context is at least 0.60**.

## Pipeline

1. Speech-to-text (Groq Whisper) and language detection
2. Query embedding (`all-MiniLM-L6-v2`)
3. ChromaDB retrieval from official PoP PDFs
4. Groq LLM generation (context-only; `openai/gpt-oss-20b`)
5. Cosine similarity verification (`τ = 0.6`)
6. Text-to-speech of the verified (or refused) answer

## Project layout

- `src/` FastAPI backend, RAG, verification, STT/TTS
- `frontend/` React UI (trust score, sources, voice)
- `data/raw_pdfs/` knowledge-base PDFs only
- `data/test_questions.csv` evaluation set

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Put your Groq key in `.env`. Copy these files into `data/raw_pdfs/`:

- `pop_HF.pdf`
- `pop_veg_culti (1).pdf`

Do **not** ingest IEEE papers or `Project_Abstract.pdf`.

```bash
python src/ingest.py
python src/test_retrieval.py
python src/generate_answer.py --text "What are the recommended cotton varieties?"
python run_api.py
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173

## Evaluation

```bash
python src/evaluate_verifier.py
```

Results are written to `data/evaluation_results.csv`.

## Team

Vasireddy Venkatadri Institute of Technology (VVIT), CSM, AIM-C10  
Guide: Mr. Merigala Kishore Babu

| Roll | Name |
| --- | --- |
| 24BQ5A6114 | Shaik Farzana |
| 24BQ5A6116 | Thummalagunta Sumanth |
| 23BQ1A61F6 | Pratikantam Veda Priyanka |
| 23BQ1A61B6 | Ravela Rupesh |
