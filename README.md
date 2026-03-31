# AcmeDesk Support Triage + Resolution Copilot

A production-ready AI system that:
1. Triages support tickets (category + priority) using a traditional ML model
2. Generates grounded responses via RAG over a knowledge base
3. Integrates triage output into RAG retrieval
4. Exposes a FastAPI service with `/triage`, `/answer`, and `/health` endpoints

---

## Quick Start

### Option A — Docker Compose (recommended)
```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY

docker compose up --build
```

API available at: http://localhost:8000
Docs at: http://localhost:8000/docs

The four main URLs are:

http://0.0.0.0:8000 (I didn't create a homapage hence the reason for seeing the blank page or {"detail":"Not Found"} on the http://0.0.0.0:8000.
To work or see the api just use http://0.0.0.0:8000/docs.

The four main URL are;

1. http://0.0.0.0:8000/docs
2. GET  http://0.0.0.0:8000/health
3. POST http://0.0.0.0:8000/triage
4. POST http://0.0.0.0:8000/answer


### Option B — Local Python
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant-...

python src/train.py
python src/rag.py
uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | — | Anthropic API key |
| `PORT` | No | `8000` | API server port |
| `ARTIFACTS_DIR` | No | `./artifacts` | Path to trained model artifacts |
| `KB_DIR` | No | `./kb_docs` | Path to KB markdown documents |
| `LOG_LEVEL` | No | `info` | Logging level |

---

## API Reference

### `GET /health`
Returns service status.

### `POST /triage`
Predict category and priority for a ticket.

**Request:**
```json
{
  "subject": "Cannot login after password reset",
  "body": "MFA code keeps getting rejected"
}
```

**Response:**
```json
{
  "category": "Authentication & Access",
  "priority": "P1",
  "confidence": {"category": 0.82, "priority": 0.74}
}
```

### `POST /answer`
Full copilot — triage + RAG reply + citations.

**Request:**
```json
{
  "subject": "API rate limit 429",
  "body": "We keep hitting 429 errors after only a few requests",
  "user_question": "What should we do?"
}
```

**Response:**
```json
{
  "triage": {"category": "Integrations & API", "priority": "P1", "confidence": {}},
  "draft_reply": "Thank you for reaching out...",
  "internal_next_steps": ["Confirm token scopes", "Check request volume"],
  "citations": [{"doc": "api_rate_limits", "chunk_id": "api_rate_limits::0", "snippet": "60 requests/minute..."}]
}
```

---

## Running Tests
```bash
pytest tests/ -v
```

---

## Running RAG Evaluation
```bash
python src/eval_rag.py
```

Outputs `reports/rag_eval.md` and `reports/rag_eval.json`.

---

## Project Structure
```
.
├── src/
│   ├── train.py
│   ├── predict.py
│   ├── rag.py
│   ├── llm.py
│   ├── api.py
│   └── eval_rag.py
├── tests/
│   └── test_core.py
├── kb_docs/
├── artifacts/
├── reports/
├── tickets_train.csv
├── tickets_test.csv
├── eval_questions.jsonl
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
└── MODEL_CARD.md
```
