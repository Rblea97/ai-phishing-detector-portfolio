"""
Train TF-IDF + Logistic Regression on data/emails.csv.
Saves the fitted pipeline to model/pipeline.joblib.

Usage
-----
    uv run python scripts/train_model.py

The model artifact is committed to the repo so the app never trains at runtime.
Re-run this script if you update emails.csv with a new corpus.
"""
from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

DATA_PATH = Path(__file__).parent.parent / "data" / "emails.csv"
MODEL_DIR = Path(__file__).parent.parent / "model"


def main() -> None:
    if not DATA_PATH.exists():
        print(f"ERROR: {DATA_PATH} not found. Run download_data.py first.")
        sys.exit(1)

    MODEL_DIR.mkdir(exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["body"])
    df = df[df["label"].isin(["phishing", "legitimate"])]  # exclude ambiguous from training
    df["text"] = df["subject"].fillna("") + "\n\n" + df["body"].fillna("")

    X = df["text"].tolist()
    y = (df["label"] == "phishing").astype(int).tolist()

    print(f"Training on {len(X):,} examples ({sum(y):,} phishing, {len(y)-sum(y):,} legitimate)")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words="english",
                sublinear_tf=True,
            ),
        ),
        (
            "clf",
            LogisticRegression(
                C=1.0,
                class_weight="balanced",
                max_iter=1000,
                random_state=42,
            ),
        ),
    ])

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print("\nEvaluation on held-out test set (20%):")
    print(classification_report(y_test, y_pred, target_names=["legitimate", "phishing"]))

    out = MODEL_DIR / "pipeline.joblib"
    joblib.dump(pipeline, out)
    size_kb = out.stat().st_size // 1024
    print(f"Saved {out}  ({size_kb} KB)")


if __name__ == "__main__":
    main()
    sys.exit(0)
