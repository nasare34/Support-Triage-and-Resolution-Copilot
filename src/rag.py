import pickle
import pathlib
from typing import List, Dict, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = pathlib.Path(__file__).parent.parent
KB_DIR = ROOT / "kb_docs"
ARTIFACTS_DIR = ROOT / "artifacts"

CATEGORY_DOC_HINTS: Dict[str, List[str]] = {
    "Billing & Payments": ["billing", "refund", "invoice", "vat", "proration"],
    "Authentication & Access": ["auth", "mfa", "password", "sso", "saml", "lockout"],
    "Integrations & API": ["api", "webhook", "zapier", "slack", "token"],
    "Data Export & Reporting": ["export", "csv", "audit", "report", "dashboard"],
    "Performance & Reliability": ["performance", "latency", "incident", "status"],
    "Security & Compliance": ["security", "gdpr", "encryption", "ip_allowlist"],
    "Account & Subscription": ["account", "cancel", "ownership", "upgrade"],
    "Bugs & Errors": ["bugs", "attachment", "notification"],
    "Feature Request": ["feature_requests"],
}


def chunk_document(doc_name: str, content: str, chunk_size: int = 400) -> List[Dict]:
    lines = content.strip().split("\n")
    chunks = []
    current = []
    current_len = 0
    chunk_idx = 0

    for line in lines:
        current.append(line)
        current_len += len(line)
        if current_len >= chunk_size:
            chunk_text = "\n".join(current).strip()
            if chunk_text:
                chunks.append({
                    "chunk_id": f"{doc_name}::{chunk_idx}",
                    "doc": doc_name,
                    "text": chunk_text,
                })
                chunk_idx += 1
            current = current[-3:]
            current_len = sum(len(l) for l in current)

    if current:
        chunk_text = "\n".join(current).strip()
        if chunk_text:
            chunks.append({
                "chunk_id": f"{doc_name}::{chunk_idx}",
                "doc": doc_name,
                "text": chunk_text,
            })

    return chunks


def ingest_kb(kb_dir: pathlib.Path = KB_DIR) -> List[Dict]:
    all_chunks = []
    for md_file in sorted(kb_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        doc_name = md_file.stem
        chunks = chunk_document(doc_name, content)
        all_chunks.extend(chunks)
    return all_chunks


class KBRetriever:
    def __init__(self, chunks: Optional[List[Dict]] = None):
        if chunks is None:
            chunks = ingest_kb()
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=10000,
            sublinear_tf=True,
        )
        texts = [c["text"] for c in chunks]
        self.chunk_vectors = self.vectorizer.fit_transform(texts)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> List[Dict]:
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.chunk_vectors)[0]

        if category and category in CATEGORY_DOC_HINTS:
            keywords = CATEGORY_DOC_HINTS[category]
            for i, chunk in enumerate(self.chunks):
                if any(kw in chunk["doc"].lower() for kw in keywords):
                    scores[i] *= 1.3

        if priority == "P0":
            for i, chunk in enumerate(self.chunks):
                if "incident" in chunk["doc"].lower() or "status" in chunk["doc"].lower():
                    scores[i] *= 1.2

        top_indices = scores.argsort()[::-1][:top_k]
        results = []
        for idx in top_indices:
            if scores[idx] > 0.01:
                chunk = self.chunks[idx].copy()
                chunk["score"] = round(float(scores[idx]), 4)
                results.append(chunk)

        return results

    def save(self, path: pathlib.Path = ARTIFACTS_DIR / "kb_index.pkl"):
        path.parent.mkdir(exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({
                "chunks": self.chunks,
                "vectorizer": self.vectorizer,
                "chunk_vectors": self.chunk_vectors,
            }, f)

    @classmethod
    def load(cls, path: pathlib.Path = ARTIFACTS_DIR / "kb_index.pkl") -> "KBRetriever":
        with open(path, "rb") as f:
            data = pickle.load(f)
        obj = cls.__new__(cls)
        obj.chunks = data["chunks"]
        obj.vectorizer = data["vectorizer"]
        obj.chunk_vectors = data["chunk_vectors"]
        return obj


if __name__ == "__main__":
    print("Ingesting KB docs...")
    retriever = KBRetriever()
    print(f"Indexed {len(retriever.chunks)} chunks from {len(list(KB_DIR.glob('*.md')))} docs")
    retriever.save()
    print("Index saved to artifacts/kb_index.pkl")

    results = retriever.retrieve("rate limit 429 error", category="Integrations & API")
    print("\nTest query: 'rate limit 429 error'")
    for r in results[:3]:
        print(f"  [{r['score']:.3f}] {r['doc']}")