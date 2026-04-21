"""Tests for the pre-loaded demo samples (app/samples.py)."""
from app.samples import SAMPLES
from app.schemas import SampleEmail


def test_samples_is_nonempty_list() -> None:
    """SAMPLES must be a non-empty list of SampleEmail objects."""
    assert isinstance(SAMPLES, list)
    assert len(SAMPLES) > 0


def test_each_sample_is_sample_email_instance() -> None:
    """Every item in SAMPLES must be a SampleEmail model instance."""
    for sample in SAMPLES:
        assert isinstance(sample, SampleEmail)


def test_each_sample_has_id() -> None:
    """Every sample must have a non-empty id field."""
    for sample in SAMPLES:
        assert sample.id


def test_each_sample_has_label() -> None:
    """Every sample must have a non-empty label field."""
    for sample in SAMPLES:
        assert sample.label


def test_each_sample_has_subject() -> None:
    """Every sample must have a subject field (may be empty string, but present)."""
    for sample in SAMPLES:
        assert hasattr(sample, "subject")


def test_each_sample_has_body() -> None:
    """Every sample must have a non-empty body field."""
    for sample in SAMPLES:
        assert sample.body
