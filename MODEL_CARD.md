# Model Card — AcmeDesk Triage Models
## Demo Video
[Watch the full demo on Google Drive](https://drive.google.com/file/d/1vmq3ylRsUP8zdJqpeIZvJIIc6ch6BMyD/view?usp=sharing)
## Model Overview
Two scikit-learn pipelines trained on AcmeDesk synthetic support ticket data:
- **Category model**: predicts 9-class ticket category
- **Priority model**: predicts 3-class priority (P0/P1/P2)

Both use: TfidfVectorizer(ngram_range=(1,2), max_features=15000) + LogisticRegression(class_weight='balanced')

## Training Data
| Property | Value |
|----------|-------|
| Source | Synthetic AcmeDesk dataset (tickets_train.csv) |
| Size | ~280 labeled tickets |
| Labels | 9 categories × 3 priorities |
| Text fields | subject + body concatenated |

## Assumptions
1. Ticket text is in English
2. Subject + body together contain sufficient signal for classification
3. The 9 category labels are exhaustive for the use case
4. Priority label definitions match DATA_DICTIONARY.md

## Limitations
1. Small training set — ~280 examples is marginal for 9-class classification
2. No semantic understanding — TF-IDF treats text as bag-of-words
3. English only — multilingual tickets will produce unreliable outputs
4. Domain drift — accuracy declines if ticket topics shift without retraining
5. No account-level signals — plan tier and history are not used

## Risks and Failure Modes

| Failure | Likelihood | Impact | Mitigation |
|---------|------------|--------|------------|
| P0 predicted as P2 | Low-Medium | HIGH | Monitor P0 recall, use confidence threshold |
| Ambiguous tickets misclassified | Medium | Medium | Show top-2 predictions to agent |
| High confidence wrong prediction | Low | Medium | Requires retraining with feedback loop |

## Intended Use
- In scope: automated first-pass triage for routing and response generation
- Out of scope: final escalation decisions without human oversight

## Recommendations
- Retrain monthly with new labeled tickets
- Implement agent feedback loop for new training data
- Review all P0/P1 predictions weekly
- Route tickets below 0.40 confidence to human agent
```

---

Your project is now complete. Here is your full file structure:
```
support_copilot/
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
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-entrypoint.sh
├── docker-compose.yml
├── README.md
├── ARCHITECTURE.md
└── MODEL_CARD.md