# Architecture Document

## System Overview
```
User / Agent
     │
     ▼
┌─────────────────────────────────────┐
│         FastAPI Service             │
│                                     │
│  POST /triage     POST /answer      │
│       │                │            │
│       ▼                ▼            │
│  Triage Model     Triage Model      │
│  (TF-IDF + LR)    (same)           │
│                        │            │
│                   category+priority │
│                        ▼            │
│                  KB Retriever       │
│                  (TF-IDF +          │
│                  category boost +   │
│                  P0 escalation)     │
│                        │            │
│                   top-5 chunks      │
│                        ▼            │
│                  LLM (Groq /        │
│                  Llama-3.3-70b)     │
│                  + injection        │
│                    defense          │
│                        │            │
│               draft_reply +         │
│               citations +           │
│               internal_next_steps   │
└─────────────────────────────────────┘
```

## Component Details

### 1. Triage Model
- TF-IDF (bigrams, 15k features) + Logistic Regression
- Two separate models: category (9-class) and priority (3-class)
- `class_weight='balanced'` ensures rare P0 tickets are not missed
- Outputs confidence scores used for human-review routing

### 2. KB Retriever
- In-memory TF-IDF matrix — no external vector DB required
- Sliding window chunking per KB doc with 3-line overlap
- Cosine similarity retrieval with category and priority boosting

### 3. Triage × RAG Integration
| Signal | Effect |
|--------|--------|
| category | Matching docs get ×1.3 score boost |
| priority P0 | Incident/status docs get ×1.2 boost |
| confidence < 0.40 | Routes to human agent |

### 4. LLM Layer
- Model: `llama-3.3-70b-versatile` via Groq API
- Prompt injection defense: regex pre-filter on user input + sanitizer on KB chunks
- Output: structured JSON parsed from LLM response
- API key configured via `GROQ_API_KEY` environment variable

### 5. FastAPI Service
- Endpoints: GET /health, POST /triage, POST /answer
- Config via environment variables
- Structured logging at INFO level
- Dockerized with volume persistence

## Key Tradeoffs

| Decision | Chosen | Alternative | Why |
|----------|--------|-------------|-----|
| Vector store | In-memory TF-IDF | ChromaDB / Pinecone | No external dependency |
| Classifier | Logistic Regression | Fine-tuned BERT | Fast, interpretable, robust on small data |
| LLM | Groq (Llama-3.3-70b) | Anthropic Claude / OpenAI GPT-4 | Fast inference, generous free tier, OpenAI-compatible API |

## Productionization Plan

### Monitoring
- Log all requests with ticket_id, triage result, confidence, and latency
- Alert on LLM API errors and injection detection spikes
- Track RAG Recall@K via agent feedback

### Cost Controls
- Cache LLM responses for duplicate tickets
- Use a smaller Groq-hosted model (e.g. `llama-3.1-8b-instant`) for low-priority P2 tickets
- Batch ML inference for bulk processing

### Security
- Store `GROQ_API_KEY` in a secrets manager (e.g. AWS Secrets Manager, HashiCorp Vault)
- Rate-limit the /answer endpoint
- Audit log all injection detections
- Never log full ticket bodies (PII risk)

### Scaling
- ML inference is stateless — scale horizontally
- KB index fits in memory — replicate per pod
- Use async task queue for /answer at high volume