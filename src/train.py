import json
import pickle
import pathlib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import f1_score, recall_score, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder

ROOT = pathlib.Path(__file__).parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"
REPORTS_DIR = ROOT / "reports"
ARTIFACTS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


def load_data(path):
    df = pd.read_csv(path)
    df["text"] = df["subject"].fillna("") + " " + df["body"].fillna("")
    return df


def make_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=15000,
            sublinear_tf=True,
            min_df=2,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            C=1.0,
            class_weight="balanced",
            solver="lbfgs",
        )),
    ])


def train():
    print("Loading training data...")
    df = load_data(ROOT / "tickets_train.csv")
    X = df["text"].values
    y_cat = df["category_label"].values
    y_pri = df["priority_label"].values

    cat_encoder = LabelEncoder()
    pri_encoder = LabelEncoder()
    y_cat_enc = cat_encoder.fit_transform(y_cat)
    y_pri_enc = pri_encoder.fit_transform(y_pri)

    cat_pipeline = make_pipeline()
    pri_pipeline = make_pipeline()

    print("Training category model...")
    cat_pipeline.fit(X, y_cat_enc)

    print("Training priority model...")
    pri_pipeline.fit(X, y_pri_enc)

    print("Evaluating...")
    cat_pred = cat_encoder.inverse_transform(cat_pipeline.predict(X))
    pri_pred = pri_encoder.inverse_transform(pri_pipeline.predict(X))

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cat_cv = cross_val_score(make_pipeline(), X, y_cat, cv=cv, scoring="f1_macro")
    pri_cv = cross_val_score(make_pipeline(), X, y_pri, cv=cv, scoring="f1_macro")

    cat_f1 = f1_score(y_cat, cat_pred, average="macro")
    pri_f1 = f1_score(y_pri, pri_pred, average="macro")
    pri_recall = recall_score(y_pri, pri_pred, average="macro")

    cat_cm = confusion_matrix(y_cat, cat_pred, labels=cat_encoder.classes_.tolist()).tolist()
    pri_cm = confusion_matrix(y_pri, pri_pred, labels=pri_encoder.classes_.tolist()).tolist()

    metrics = {
        "category": {
            "macro_f1_train": round(cat_f1, 4),
            "macro_f1_cv_mean": round(float(cat_cv.mean()), 4),
            "macro_f1_cv_std": round(float(cat_cv.std()), 4),
            "classes": cat_encoder.classes_.tolist(),
            "confusion_matrix": cat_cm,
        },
        "priority": {
            "macro_f1_train": round(pri_f1, 4),
            "macro_f1_cv_mean": round(float(pri_cv.mean()), 4),
            "macro_f1_cv_std": round(float(pri_cv.std()), 4),
            "macro_recall_train": round(pri_recall, 4),
            "classes": pri_encoder.classes_.tolist(),
            "confusion_matrix": pri_cm,
        },
    }

    with open(REPORTS_DIR / "ml_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print("Metrics saved to reports/ml_metrics.json")

    with open(ARTIFACTS_DIR / "cat_pipeline.pkl", "wb") as f:
        pickle.dump(cat_pipeline, f)
    with open(ARTIFACTS_DIR / "pri_pipeline.pkl", "wb") as f:
        pickle.dump(pri_pipeline, f)
    with open(ARTIFACTS_DIR / "cat_encoder.pkl", "wb") as f:
        pickle.dump(cat_encoder, f)
    with open(ARTIFACTS_DIR / "pri_encoder.pkl", "wb") as f:
        pickle.dump(pri_encoder, f)

    print("Artifacts saved to artifacts/")
    print(f"Category macro F1 (CV): {cat_cv.mean():.3f} ± {cat_cv.std():.3f}")
    print(f"Priority macro F1 (CV): {pri_cv.mean():.3f} ± {pri_cv.std():.3f}")
    print(f"Priority macro recall: {pri_recall:.3f}")


if __name__ == "__main__":
    train()