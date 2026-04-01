"""
Tests for the dataset schema and loader.
All tests use only synthetic data — no real credentials, domains, or PII.
"""
import io
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.dataset import EmailRecord, Label, load_dataset

DEMO_CSV = Path(__file__).parent.parent / "data" / "demo_emails.csv"


# ── Schema unit tests ─────────────────────────────────────────────────────────


def test_email_record_valid_phishing() -> None:
    record = EmailRecord(
        label=Label.PHISHING,
        source="synthetic",
        subject="Verify your account",
        sender="security@bank-verify.example",
        body="Click here to verify: http://bank-verify.example/reset",
        urls=["http://bank-verify.example/reset"],
        notes="Credential harvesting attempt",
    )
    assert record.label == Label.PHISHING
    assert len(record.urls) == 1


def test_email_record_valid_legitimate() -> None:
    record = EmailRecord(
        label=Label.LEGITIMATE,
        source="synthetic",
        body="Please join us for the all-hands meeting on Friday.",
    )
    assert record.label == Label.LEGITIMATE
    assert record.subject == ""
    assert record.sender == ""
    assert record.urls == []
    assert record.notes == ""


def test_email_record_valid_ambiguous() -> None:
    record = EmailRecord(
        label=Label.AMBIGUOUS,
        source="synthetic",
        body="Your document is ready for signature.",
        notes="Could be legitimate DocuSign or spoofed",
    )
    assert record.label == Label.AMBIGUOUS


def test_email_record_invalid_label_raises() -> None:
    with pytest.raises(ValidationError):
        EmailRecord(label="spam", source="synthetic", body="Some body")  # type: ignore[arg-type]


def test_email_record_empty_body_raises() -> None:
    with pytest.raises(ValidationError):
        EmailRecord(label=Label.PHISHING, source="synthetic", body="")


def test_email_record_empty_source_raises() -> None:
    with pytest.raises(ValidationError):
        EmailRecord(label=Label.PHISHING, source="", body="Some body content")


def test_email_record_urls_default_to_empty_list() -> None:
    record = EmailRecord(label=Label.LEGITIMATE, source="synthetic", body="Hello team.")
    assert record.urls == []


# ── Loader tests ──────────────────────────────────────────────────────────────


def test_load_dataset_returns_list_of_records() -> None:
    records = load_dataset(DEMO_CSV)
    assert isinstance(records, list)
    assert len(records) > 0
    assert all(isinstance(r, EmailRecord) for r in records)


def test_demo_dataset_has_all_label_types() -> None:
    records = load_dataset(DEMO_CSV)
    labels = {r.label for r in records}
    assert Label.PHISHING in labels
    assert Label.LEGITIMATE in labels
    assert Label.AMBIGUOUS in labels


def test_demo_dataset_all_bodies_non_empty() -> None:
    records = load_dataset(DEMO_CSV)
    assert all(r.body.strip() for r in records), "Every record must have a non-empty body"


def test_demo_dataset_all_sources_non_empty() -> None:
    records = load_dataset(DEMO_CSV)
    assert all(r.source.strip() for r in records), "Every record must have a non-empty source"


def test_load_dataset_parses_urls_from_pipe_separated() -> None:
    """Loader must split pipe-separated URLs into a list."""
    csv_content = (
        "label,source,subject,sender,body,urls,notes\n"
        "phishing,synthetic,Test,sender@example.test,"
        "Click here,http://a.example|http://b.example,test\n"
    )
    tmp = io.StringIO(csv_content)
    records = load_dataset(tmp)
    assert records[0].urls == ["http://a.example", "http://b.example"]


def test_load_dataset_handles_empty_urls_field() -> None:
    csv_content = (
        "label,source,subject,sender,body,urls,notes\n"
        "legitimate,synthetic,Hi,sender@co.example,Normal email,,no urls\n"
    )
    tmp = io.StringIO(csv_content)
    records = load_dataset(tmp)
    assert records[0].urls == []


def test_load_dataset_invalid_label_raises() -> None:
    csv_content = (
        "label,source,subject,sender,body,urls,notes\n"
        "malware,synthetic,Test,s@example.test,Body content,,\n"
    )
    tmp = io.StringIO(csv_content)
    with pytest.raises(ValidationError):
        load_dataset(tmp)


def test_load_dataset_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_dataset(Path("/nonexistent/path/emails.csv"))
