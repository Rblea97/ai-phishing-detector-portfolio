"""
ML inference layer.

Loads the trained TF-IDF + Logistic Regression pipeline from
model/pipeline.joblib and exposes a single ``analyze()`` function used by
the FastAPI route.  The pipeline is loaded once at first call and cached for
the lifetime of the process.
"""
from __future__ import annotations

import functools
from pathlib import Path

import joblib
import numpy as np
from sklearn.pipeline import Pipeline

from app.schemas import Feature, MLResult

_MODEL_PATH = Path(__file__).parent.parent / "model" / "pipeline.joblib"

# Score thresholds for risk bucketing
_HIGH_THRESHOLD = 0.75
_MEDIUM_THRESHOLD = 0.40


def score_to_risk_level(score: float) -> str:
    """Map a phishing probability to a human-readable risk tier."""
    if score >= _HIGH_THRESHOLD:
        return "high"
    if score >= _MEDIUM_THRESHOLD:
        return "medium"
    return "low"


@functools.lru_cache(maxsize=1)
def load_pipeline() -> Pipeline:
    """Load and cache the sklearn Pipeline from disk."""
    return joblib.load(_MODEL_PATH)


def analyze(*, subject: str, body: str, top_n: int = 10) -> MLResult:
    """
    Run the ML pipeline on one email and return a structured result.

    Parameters
    ----------
    subject:
        Email subject line.
    body:
        Plain-text email body.
    top_n:
        Maximum number of top contributing TF-IDF tokens to return.

    Returns
    -------
    MLResult
        Phishing probability score, risk level, and top weighted features.
    """
    pipeline = load_pipeline()
    text = f"{subject}\n\n{body}"

    # Probability of the positive (phishing) class
    proba: np.ndarray = pipeline.predict_proba([text])[0]
    score = float(proba[1])

    # Extract feature contributions from the LR coefficients × TF-IDF weights
    tfidf = pipeline.named_steps["tfidf"]
    clf = pipeline.named_steps["clf"]

    tf_matrix = tfidf.transform([text])  # sparse (1, n_features)
    # coef_ shape: (1, n_features) for binary classification
    coef = clf.coef_[0]
    contributions: np.ndarray = tf_matrix.toarray()[0] * coef

    # Sort descending by contribution magnitude (positive = phishing signal)
    feature_names: list[str] = tfidf.get_feature_names_out().tolist()
    top_indices = np.argsort(contributions)[::-1][:top_n]

    features = [
        Feature(token=feature_names[i], weight=round(float(contributions[i]), 4))
        for i in top_indices
        if contributions[i] > 0
    ]

    return MLResult(
        score=round(score, 4),
        risk_level=score_to_risk_level(score),
        top_features=features,
    )
