import sys
import json
import pathlib
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from rag import KBRetriever

EVAL_PATH = ROOT / "eval_questions.jsonl"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

TOP_K = 5


def load_eval(path):
    items = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def stem(doc_name):
    return doc_name.replace(".md", "")


def evaluate():
    logger.info("Loading KB retriever...")
    index_path = ROOT / "artifacts" / "kb_index.pkl"
    if index_path.exists():
        retriever = KBRetriever.load(index_path)
    else:
        retriever = KBRetriever()

    logger.info("Loading eval questions...")
    eval_items = load_eval(EVAL_PATH)
    logger.info(f"Evaluating {len(eval_items)} questions...")

    results = []
    recall_scores = []
    mrr_scores = []
    coverage_scores = []

    for item in eval_items:
        qid = item["id"]
        subject = item["ticket_subject"]
        body = item["ticket_body"]
        user_q = item.get("user_question", "")
        expected_docs = [stem(d) for d in item.get("expected_docs", [])]
        notes = item.get("notes", "")

        query = f"{subject} {body} {user_q}"
        retrieved = retriever.retrieve(query, top_k=TOP_K)
        retrieved_docs = [r["doc"] for r in retrieved]

        hits = [d for d in expected_docs if d in retrieved_docs]
        recall = len(hits) / max(len(expected_docs), 1)

        mrr = 0.0
        for rank, doc in enumerate(retrieved_docs, 1):
            if doc in expected_docs:
                mrr = 1.0 / rank
                break

        coverage = 1.0 if any(d in retrieved_docs for d in expected_docs) else 0.0

        recall_scores.append(recall)
        mrr_scores.append(mrr)
        coverage_scores.append(coverage)

        results.append({
            "id": qid,
            "subject": subject,
            "expected_docs": expected_docs,
            "retrieved_docs": retrieved_docs,
            "recall_at_k": round(recall, 3),
            "mrr": round(mrr, 3),
            "coverage": coverage,
            "hit_docs": hits,
            "missed_docs": [d for d in expected_docs if d not in retrieved_docs],
            "notes": notes,
        })

    avg_recall = sum(recall_scores) / len(recall_scores)
    avg_mrr = sum(mrr_scores) / len(mrr_scores)
    avg_coverage = sum(coverage_scores) / len(coverage_scores)

    failures = [r for r in results if r["recall_at_k"] < 0.5]
    perfect = [r for r in results if r["recall_at_k"] == 1.0]

    summary = {
        "n_questions": len(eval_items),
        "top_k": TOP_K,
        "avg_recall_at_k": round(avg_recall, 4),
        "avg_mrr": round(avg_mrr, 4),
        "avg_coverage": round(avg_coverage, 4),
        "n_perfect_recall": len(perfect),
        "n_failures": len(failures),
        "per_question": results,
    }

    with open(REPORTS_DIR / "rag_eval.json", "w") as f:
        json.dump(summary, f, indent=2)

    md_lines = [
        "# RAG Evaluation Report\n",
        "## Summary\n",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Questions evaluated | {len(eval_items)} |",
        f"| Top-K | {TOP_K} |",
        f"| Avg Recall@{TOP_K} | {avg_recall:.3f} |",
        f"| Avg MRR | {avg_mrr:.3f} |",
        f"| Avg Coverage | {avg_coverage:.3f} |",
        f"| Perfect recall | {len(perfect)} / {len(eval_items)} |",
        f"| Failures (recall < 0.5) | {len(failures)} / {len(eval_items)} |",
        "",
        "## Metrics Explanation\n",
        "- **Recall@K**: fraction of expected KB docs found in top-K results.",
        "- **MRR**: reciprocal rank of the first expected doc. Higher = relevant docs ranked earlier.",
        "- **Coverage**: did at least one expected doc appear in top-K results.",
        "",
        "## Per-Question Results\n",
        "| ID | Subject | Recall@K | MRR | Coverage | Missed Docs |",
        "|----|---------|----------|-----|----------|-------------|",
    ]

    for r in results:
        missed = ", ".join(r["missed_docs"]) or "—"
        md_lines.append(
            f"| {r['id']} | {r['subject'][:45]} | {r['recall_at_k']} | "
            f"{r['mrr']} | {int(r['coverage'])} | {missed} |"
        )

    md_lines += [
        "",
        "## Failure Analysis\n",
    ]

    if failures:
        md_lines.append("### Common failure patterns\n")
        for r in failures:
            md_lines.append(f"**{r['id']}** — *{r['subject']}*")
            md_lines.append(f"- Expected: {r['expected_docs']}")
            md_lines.append(f"- Retrieved: {r['retrieved_docs']}")
            md_lines.append(f"- Missed: {r['missed_docs']}")
            md_lines.append("")

        md_lines += [
            "### Root causes\n",
            "1. **Vocabulary mismatch**: informal query language does not overlap with KB terminology.",
            "2. **Multi-doc queries**: some questions expect 5+ docs but top-K may not capture all.",
            "3. **Short KB docs**: sparse TF-IDF targets. Semantic embeddings would improve this.",
        ]
    else:
        md_lines.append("No significant failures detected.\n")

    md_lines += [
        "",
        "## Improvement Roadmap\n",
        "- Replace TF-IDF with dense embeddings (sentence-transformers) for semantic similarity",
        "- Add BM25 hybrid retrieval for vocabulary-exact matches",
        "- Query expansion using LLM rephrasing before retrieval",
        "- Re-rank retrieved chunks with a cross-encoder",
    ]

    with open(REPORTS_DIR / "rag_eval.md", "w") as f:
        f.write("\n".join(md_lines))

    logger.info(f"RAG eval complete. Recall@{TOP_K}={avg_recall:.3f}, MRR={avg_mrr:.3f}")
    logger.info(f"Reports saved to reports/rag_eval.json and reports/rag_eval.md")


if __name__ == "__main__":
    evaluate()