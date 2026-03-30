import pickle
import pathlib
import pandas as pd

ROOT = pathlib.Path(__file__).parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def load_artifacts():
    with open(ARTIFACTS_DIR / "cat_pipeline.pkl", "rb") as f:
        cat_pipeline = pickle.load(f)
    with open(ARTIFACTS_DIR / "pri_pipeline.pkl", "rb") as f:
        pri_pipeline = pickle.load(f)
    with open(ARTIFACTS_DIR / "cat_encoder.pkl", "rb") as f:
        cat_encoder = pickle.load(f)
    with open(ARTIFACTS_DIR / "pri_encoder.pkl", "rb") as f:
        pri_encoder = pickle.load(f)
    return cat_pipeline, pri_pipeline, cat_encoder, pri_encoder


def predict_ticket(subject, body, cat_pipeline, pri_pipeline, cat_encoder, pri_encoder):
    text = f"{subject} {body}"

    cat_proba = cat_pipeline.predict_proba([text])[0]
    pri_proba = pri_pipeline.predict_proba([text])[0]

    cat_idx = cat_proba.argmax()
    pri_idx = pri_proba.argmax()

    return {
        "category": cat_encoder.classes_[cat_idx],
        "priority": pri_encoder.classes_[pri_idx],
        "confidence": {
            "category": round(float(cat_proba[cat_idx]), 4),
            "priority": round(float(pri_proba[pri_idx]), 4),
        },
    }


def main():
    print("Loading artifacts...")
    cat_pipeline, pri_pipeline, cat_encoder, pri_encoder = load_artifacts()

    print("Loading test data...")
    df = pd.read_csv(ROOT / "tickets_test.csv")
    df["text"] = df["subject"].fillna("") + " " + df["body"].fillna("")

    cat_proba = cat_pipeline.predict_proba(df["text"].values)
    pri_proba = pri_pipeline.predict_proba(df["text"].values)

    df["predicted_category"] = cat_encoder.inverse_transform(cat_proba.argmax(axis=1))
    df["predicted_priority"] = pri_encoder.inverse_transform(pri_proba.argmax(axis=1))
    df["category_confidence"] = cat_proba.max(axis=1).round(4)
    df["priority_confidence"] = pri_proba.max(axis=1).round(4)

    out_cols = [
        "ticket_id", "subject",
        "predicted_category", "category_confidence",
        "predicted_priority", "priority_confidence",
    ]

    out_path = REPORTS_DIR / "test_predictions.csv"
    df[out_cols].to_csv(out_path, index=False)

    print(f"Predictions saved to {out_path}")
    print(df[out_cols].head(10).to_string())


if __name__ == "__main__":
    main()