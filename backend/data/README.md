# Training Data

## Schema

| Field | Type | Required | Description |
|---|---|---|---|
| `label` | `phishing` \| `legitimate` \| `ambiguous` | yes | Ground-truth classification |
| `source` | string | yes | Origin of the sample (e.g. `synthetic`, `spamassassin`) |
| `subject` | string | no | Email subject line |
| `sender` | string | no | Sender address |
| `body` | string | yes | Plain-text email body (non-empty) |
| `urls` | pipe-separated string | no | URLs extracted from the email (e.g. `http://a.example\|http://b.example`) |
| `notes` | string | no | Human-readable annotation for explainability |

All fields are loaded and validated by `app/dataset.py`. Invalid labels or empty bodies raise `ValidationError` immediately.

## Files

### `demo_emails.csv` (in-repo)

12 hand-crafted synthetic rows covering the full label space:

| Label | Count | Examples |
|---|---|---|
| `phishing` | 6 | Credential urgency, spear phishing, BEC, package scam, brand impersonation, payroll |
| `legitimate` | 4 | HR open enrollment, IT password notice, standup notes, expense approval |
| `ambiguous` | 2 | DocuSign notification, IT compliance request |

**Safety:** All sender addresses and URLs use IANA-reserved domains (`.example`, `.test`) that will never resolve. No real credentials, malware, or weaponized payloads.

### Adding a larger public dataset

Download and preprocess the [SpamAssassin Public Corpus](https://spamassassin.apache.org/old/publiccorpus/) into the same CSV format, then load it alongside or instead of `demo_emails.csv`:

```python
from pathlib import Path
from app.dataset import load_dataset

records = load_dataset(Path("data/spamassassin_processed.csv"))
```

The `download_data.py` script (added in a later batch) automates this step.
Place processed CSVs in `data/` — they are gitignored if prefixed with `raw_` or placed in `data/raw/`.

## Provenance

| File | Source | License | Notes |
|---|---|---|---|
| `demo_emails.csv` | Hand-crafted by project author | Original work | Synthetic only; `.example`/`.test` domains |
