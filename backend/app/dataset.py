"""
Dataset schema and loader for phishing email classification.

Schema fields
-------------
label   : "phishing" | "legitimate" | "ambiguous"
source  : origin of the sample (e.g. "synthetic", "spamassassin")
subject : email subject line (may be empty)
sender  : sender address (may be empty)
body    : plain-text email body (required, non-empty)
urls    : list of URLs extracted from the email (pipe-separated in CSV)
notes   : human-readable annotation for explainability demos (may be empty)

CSV format
----------
Pipe-separated URLs within a single quoted cell:
  "http://evil.example|http://track.example"

Loading a larger public dataset
---------------------------------
Pass any file path (or file-like object) to load_dataset():
  records = load_dataset(Path("data/spamassassin_processed.csv"))

The schema is enforced via Pydantic — rows with invalid labels or empty
bodies raise ValidationError immediately so bad data never reaches the model.
"""
from __future__ import annotations

import csv
from enum import StrEnum
from pathlib import Path
from typing import IO

from pydantic import BaseModel, Field


class Label(StrEnum):
    PHISHING = "phishing"
    LEGITIMATE = "legitimate"
    AMBIGUOUS = "ambiguous"


class EmailRecord(BaseModel):
    id: str = ""
    label: Label
    source: str = Field(min_length=1)
    subject: str = ""
    sender: str = ""
    body: str = Field(min_length=1)
    urls: list[str] = Field(default_factory=list)
    notes: str = ""


def load_dataset(path: Path | str | IO[str]) -> list[EmailRecord]:
    """
    Load and validate a CSV dataset of labeled emails.

    Parameters
    ----------
    path:
        File path (str or Path) or any file-like object with a ``read`` method.
        Expected columns: label, source, subject, sender, body, urls, notes.

    Returns
    -------
    list[EmailRecord]
        Validated records. Raises FileNotFoundError or ValidationError on bad input.
    """
    if isinstance(path, (str, Path)):
        resolved = Path(path)
        if not resolved.exists():
            raise FileNotFoundError(f"Dataset not found: {resolved}")
        fh: IO[str] = open(resolved, newline="", encoding="utf-8")
        close_after = True
    else:
        fh = path
        close_after = False

    try:
        reader = csv.DictReader(fh)
        records: list[EmailRecord] = []
        for row in reader:
            urls_raw = (row.get("urls") or "").strip()
            urls = [u.strip() for u in urls_raw.split("|") if u.strip()]
            records.append(
                EmailRecord.model_validate(
                    {
                        "id": row.get("id", ""),
                        "label": row["label"],
                        "source": row.get("source", ""),
                        "subject": row.get("subject", ""),
                        "sender": row.get("sender", ""),
                        "body": row.get("body", ""),
                        "urls": urls,
                        "notes": row.get("notes", ""),
                    }
                )
            )
    finally:
        if close_after:
            fh.close()

    return records
