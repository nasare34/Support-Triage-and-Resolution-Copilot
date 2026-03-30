#!/bin/bash
set -e

echo "=== AcmeDesk Support Copilot ==="

if [ ! -f "/app/artifacts/cat_pipeline.pkl" ]; then
  echo "Training ML models..."
  python src/train.py
else
  echo "ML artifacts already exist, skipping training."
fi

if [ ! -f "/app/artifacts/kb_index.pkl" ]; then
  echo "Building KB index..."
  python src/rag.py
else
  echo "KB index already exists, skipping ingestion."
fi

echo "Starting API server on port ${PORT}..."
exec uvicorn src.api:app --host 0.0.0.0 --port "${PORT}" --workers 1