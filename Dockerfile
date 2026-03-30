FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY kb_docs/ ./kb_docs/
COPY tickets_train.csv tickets_test.csv eval_questions.jsonl ./

RUN mkdir -p artifacts reports

COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

ENV PORT=8000
ENV ARTIFACTS_DIR=/app/artifacts
ENV KB_DIR=/app/kb_docs

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]