import os
import sys
import logging
import pathlib
import pickle
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

ROOT = pathlib.Path(__file__).parent.parent
ARTIFACTS_DIR = pathlib.Path(os.getenv("ARTIFACTS_DIR", str(ROOT / "artifacts")))
KB_INDEX_PATH = ARTIFACTS_DIR / "kb_index.pkl"
CAT_PIPELINE_PATH = ARTIFACTS_DIR / "cat_pipeline.pkl"
PRI_PIPELINE_PATH = ARTIFACTS_DIR / "pri_pipeline.pkl"
CAT_ENCODER_PATH = ARTIFACTS_DIR / "cat_encoder.pkl"
PRI_ENCODER_PATH = ARTIFACTS_DIR / "pri_encoder.pkl"

sys.path.insert(0, str(ROOT / "src"))

_artifacts = {}


def load_artifacts():
    global _artifacts
    if _artifacts:
        return _artifacts

    logger.info("Loading ML artifacts...")
    from rag import KBRetriever

    with open(CAT_PIPELINE_PATH, "rb") as f:
        _artifacts["cat_pipeline"] = pickle.load(f)
    with open(PRI_PIPELINE_PATH, "rb") as f:
        _artifacts["pri_pipeline"] = pickle.load(f)
    with open(CAT_ENCODER_PATH, "rb") as f:
        _artifacts["cat_encoder"] = pickle.load(f)
    with open(PRI_ENCODER_PATH, "rb") as f:
        _artifacts["pri_encoder"] = pickle.load(f)

    if KB_INDEX_PATH.exists():
        _artifacts["retriever"] = KBRetriever.load(KB_INDEX_PATH)
    else:
        logger.warning("KB index not found, building from scratch...")
        _artifacts["retriever"] = KBRetriever()
        _artifacts["retriever"].save(KB_INDEX_PATH)

    logger.info("All artifacts loaded successfully")
    return _artifacts


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        load_artifacts()
    except Exception as e:
        logger.error(f"Startup failed: {e}")
    yield


app = FastAPI(
    title="AcmeDesk Support Copilot API",
    description="Triage + RAG-powered support response generation",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Request and Response Models ---

class TriageRequest(BaseModel):
    subject: str
    body: str


class ConfidenceScore(BaseModel):
    category: float
    priority: float


class TriageResponse(BaseModel):
    category: str
    priority: str
    confidence: ConfidenceScore


class AnswerRequest(BaseModel):
    subject: str
    body: str
    user_question: Optional[str] = None


class Citation(BaseModel):
    doc: str
    chunk_id: str
    snippet: str


class AnswerResponse(BaseModel):
    triage: TriageResponse
    draft_reply: str
    internal_next_steps: List[str]
    citations: List[Citation]


class HealthResponse(BaseModel):
    status: str
    artifacts_loaded: bool
    kb_loaded: bool


# --- Helper ---

def run_triage(subject: str, body: str) -> TriageResponse:
    arts = load_artifacts()
    text = f"{subject} {body}"

    cat_proba = arts["cat_pipeline"].predict_proba([text])[0]
    pri_proba = arts["pri_pipeline"].predict_proba([text])[0]

    cat_idx = cat_proba.argmax()
    pri_idx = pri_proba.argmax()

    return TriageResponse(
        category=arts["cat_encoder"].classes_[cat_idx],
        priority=arts["pri_encoder"].classes_[pri_idx],
        confidence=ConfidenceScore(
            category=round(float(cat_proba[cat_idx]), 4),
            priority=round(float(pri_proba[pri_idx]), 4),
        ),
    )


# --- Endpoints ---

@app.get("/health", response_model=HealthResponse)
def health():
    arts_ok = bool(_artifacts.get("cat_pipeline"))
    kb_ok = bool(_artifacts.get("retriever"))
    return HealthResponse(
        status="healthy" if (arts_ok and kb_ok) else "degraded",
        artifacts_loaded=arts_ok,
        kb_loaded=kb_ok,
    )


@app.post("/triage", response_model=TriageResponse)
def triage(req: TriageRequest):
    logger.info(f"Triage request: subject='{req.subject[:50]}'")
    try:
        return run_triage(req.subject, req.body)
    except Exception as e:
        logger.exception("Triage error")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/answer", response_model=AnswerResponse)
def answer(req: AnswerRequest):
    logger.info(f"Answer request: subject='{req.subject[:50]}'")
    try:
        from llm import generate_response

        arts = load_artifacts()
        triage_result = run_triage(req.subject, req.body)

        query = f"{req.subject} {req.body}"
        if req.user_question:
            query += f" {req.user_question}"

        chunks = arts["retriever"].retrieve(
            query,
            top_k=5,
            category=triage_result.category,
            priority=triage_result.priority,
        )

        needs_human_review = (
            triage_result.confidence.category < 0.40
            or triage_result.confidence.priority < 0.40
        )

        llm_result = generate_response(
            subject=req.subject,
            body=req.body,
            category=triage_result.category,
            priority=triage_result.priority,
            kb_chunks=chunks,
            user_question=req.user_question,
        )

        citations = []
        for c in llm_result.get("citations", []):
            citations.append(Citation(
                doc=c.get("doc", ""),
                chunk_id=c.get("chunk_id", ""),
                snippet=c.get("snippet", "")[:200],
            ))

        internal_steps = llm_result.get("internal_next_steps", [])
        if needs_human_review:
            internal_steps.append(
                "Low model confidence — route to human agent for verification"
            )

        return AnswerResponse(
            triage=triage_result,
            draft_reply=llm_result.get("draft_reply", ""),
            internal_next_steps=internal_steps,
            citations=citations,
        )

    except Exception as e:
        logger.exception("Answer error")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )