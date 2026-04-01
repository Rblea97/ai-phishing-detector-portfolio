"""Tests for the ML inference layer (app/ml.py)."""

from app.ml import analyze, load_pipeline, score_to_risk_level
from app.schemas import Feature, MLResult

# ── score_to_risk_level ───────────────────────────────────────────────────────


def test_score_high_threshold() -> None:
    assert score_to_risk_level(0.75) == "high"
    assert score_to_risk_level(1.0) == "high"


def test_score_medium_threshold() -> None:
    assert score_to_risk_level(0.4) == "medium"
    assert score_to_risk_level(0.74) == "medium"


def test_score_low_threshold() -> None:
    assert score_to_risk_level(0.0) == "low"
    assert score_to_risk_level(0.39) == "low"


# ── load_pipeline ─────────────────────────────────────────────────────────────


def test_load_pipeline_returns_pipeline() -> None:
    """load_pipeline() should return the sklearn Pipeline object."""
    pipeline = load_pipeline()
    # Duck-type check: sklearn Pipeline has predict_proba
    assert hasattr(pipeline, "predict_proba")
    assert hasattr(pipeline, "named_steps")


def test_load_pipeline_is_cached() -> None:
    """Calling load_pipeline() twice returns the same object (cached)."""
    p1 = load_pipeline()
    p2 = load_pipeline()
    assert p1 is p2


# ── analyze ───────────────────────────────────────────────────────────────────


def test_analyze_returns_ml_result() -> None:
    result = analyze(subject="Verify your account", body="Click here to confirm.")
    assert isinstance(result, MLResult)
    assert 0.0 <= result.score <= 1.0
    assert result.risk_level in ("high", "medium", "low")
    assert isinstance(result.top_features, list)


def test_analyze_phishing_email_scores_high() -> None:
    result = analyze(
        subject="URGENT: Verify your PayPal account immediately",
        body=(
            "Your account has been suspended. Click the link below to verify "
            "your credentials and restore access. Failure to act within 24 hours "
            "will result in permanent suspension. http://paypal-verify.example/login"
        ),
    )
    assert result.score >= 0.5


def test_analyze_legitimate_email_scores_low() -> None:
    result = analyze(
        subject="Team standup notes — Monday",
        body=(
            "Hi everyone, here are the notes from today's standup. "
            "Alice is working on the auth refactor. Bob will finish the "
            "dashboard PR by Wednesday. Next standup is Thursday at 10am."
        ),
    )
    assert result.score < 0.5


def test_analyze_top_features_not_empty() -> None:
    result = analyze(subject="Verify your account", body="Click here to confirm.")
    assert len(result.top_features) > 0


def test_analyze_top_features_are_features() -> None:
    result = analyze(subject="Test", body="Hello world.")
    for f in result.top_features:
        assert isinstance(f, Feature)
        assert isinstance(f.token, str)
        assert isinstance(f.weight, float)


def test_analyze_top_features_limited_to_10() -> None:
    result = analyze(subject="Verify your account", body="Click here to confirm.")
    assert len(result.top_features) <= 10


def test_analyze_features_sorted_descending_by_weight() -> None:
    result = analyze(subject="Verify your account", body="Click here to confirm.")
    weights = [f.weight for f in result.top_features]
    assert weights == sorted(weights, reverse=True)
