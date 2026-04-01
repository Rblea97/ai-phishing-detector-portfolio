"""
Download the SpamAssassin public corpus and write data/emails.csv.

Sources
-------
- easy_ham : legitimate emails (Apache 2.0 / public domain)
- spam     : spam emails used as phishing proxy (documented in data/README.md)

Usage
-----
    uv run python scripts/download_data.py

Output: backend/data/emails.csv  (~3,000 rows, ~500KB)
"""
from __future__ import annotations

import csv
import email as email_lib
import io
import sys
import tarfile
import urllib.request
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

_CORPUS = [
    (
        "https://spamassassin.apache.org/old/publiccorpus/20030228_easy_ham.tar.bz2",
        "legitimate",
    ),
    (
        "https://spamassassin.apache.org/old/publiccorpus/20030228_spam.tar.bz2",
        "phishing",
    ),
]


def _parse(raw: bytes) -> tuple[str, str]:
    msg = email_lib.message_from_bytes(raw)
    subject = str(msg.get("Subject") or "")
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    body = payload.decode("utf-8", errors="replace")
                    break
    else:
        payload = msg.get_payload(decode=True)
        if isinstance(payload, bytes):
            body = payload.decode("utf-8", errors="replace")
    return subject.strip(), body.strip()


def _fetch(url: str, label: str) -> list[dict[str, str]]:
    print(f"Downloading {url} ...", flush=True)
    with urllib.request.urlopen(url) as resp:  # noqa: S310
        data = resp.read()
    rows: list[dict[str, str]] = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:bz2") as tar:
        for member in tar.getmembers():
            if not member.isfile() or member.name.endswith("cmds"):
                continue
            fh = tar.extractfile(member)
            if fh is None:
                continue
            subject, body = _parse(fh.read())
            if not body:
                continue
            rows.append(
                {
                    "id": "",
                    "label": label,
                    "source": "spamassassin",
                    "subject": subject,
                    "sender": "",
                    "body": body[:2000],
                    "urls": "",
                    "notes": "",
                }
            )
    print(f"  {len(rows):,} {label} rows", flush=True)
    return rows


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    rows: list[dict[str, str]] = []
    for url, label in _CORPUS:
        rows.extend(_fetch(url, label))

    out = DATA_DIR / "emails.csv"
    fieldnames = ["id", "label", "source", "subject", "sender", "body", "urls", "notes"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    phishing = sum(1 for r in rows if r["label"] == "phishing")
    legit = sum(1 for r in rows if r["label"] == "legitimate")
    print(f"\nWrote {len(rows):,} rows -> {out}")
    print(f"  legitimate : {legit:,}")
    print(f"  phishing   : {phishing:,}")


if __name__ == "__main__":
    main()
    sys.exit(0)
