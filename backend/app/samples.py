"""
Pre-loaded demo email samples served by GET /api/samples.

Samples are loaded from data/demo_emails.csv at import time and cached.
To add or edit samples, update the CSV — no code change needed.
"""
from pathlib import Path

from app.dataset import load_dataset
from app.schemas import SampleEmail

_DEMO_CSV = Path(__file__).parent.parent / "data" / "demo_emails.csv"


def _load() -> list[SampleEmail]:
    records = load_dataset(_DEMO_CSV)
    return [
        SampleEmail(
            id=r.id or r.label.value,
            label=r.label.value,
            subject=r.subject,
            body=r.body,
        )
        for r in records
    ]


SAMPLES: list[SampleEmail] = _load()
