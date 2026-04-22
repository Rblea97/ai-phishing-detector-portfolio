# Model Card — TF-IDF + Logistic Regression Phishing Classifier

Follows the [Hugging Face Model Card](https://huggingface.co/docs/hub/model-cards) format, aligned with NIST AI RMF (NIST AI 100-1) documentation guidance.

---

## Model Details

| Field | Value |
|---|---|
| **Model type** | Text classification (binary: phishing / legitimate) |
| **Architecture** | scikit-learn Pipeline: TF-IDF Vectorizer → Logistic Regression |
| **Task** | Phishing email detection |
| **Language** | English (monolingual) |
| **Artifact** | `backend/model/pipeline.joblib` |
| **Framework** | scikit-learn 1.x |
| **Training date** | 2026-03 |
| **Author** | Richard Blea |
| **Use case** | Defensive portfolio demonstration; SOC Tier 1 email triage support |

---

## Intended Use

### Primary use

Classify submitted email text (subject + body) as phishing or legitimate and return an interpretable confidence score with the top contributing tokens for analyst review.

Designed for:
- Portfolio demonstration to security engineering hiring managers
- Educational showcase of explainable ML in a defensive security context
- Supporting manual SOC analyst triage — the model aids human decisions, it does not replace them

### Out-of-scope uses

| Use | Reason out of scope |
|---|---|
| Automated block decisions without analyst review | False positives exist; automated blocking would suppress legitimate email |
| Production enterprise email gateway | Model trained on SpamAssassin corpus (2002–2005 era data); real-world corpora drift fast |
| Detection of image-based or attachment-based phishing | Detector is text-only; no OCR, no file analysis |
| Multi-language phishing detection | Training data is English-only; other-language inputs will produce unreliable scores |
| Adversarial robustness testing | Model not hardened against deliberate evasion; see Known Limitations |
| Offensive phishing generation | Strictly out of scope — no generation endpoints exist |

---

## Training Data

| Dataset | Size | Labels | License | Era |
|---|---|---|---|---|
| SpamAssassin public corpus | ~80,000 emails (post-processing) | phishing / legitimate | Apache 2.0 | 2002–2005 |
| Hand-crafted synthetic samples | 12 emails | phishing / legitimate / ambiguous | Original work | 2026 |

**Preprocessing:**
- Rows labelled `ambiguous` are excluded from training (retained for demo samples only)
- Subject and body concatenated as `f"{subject}\n\n{body}"`
- No deduplication beyond what SpamAssassin provides
- No PII scrubbing (SpamAssassin corpus is public; synthetic samples use `.example` domains)

**Train / test split:** 80/20 stratified random split (`random_state=42`).

**Class distribution (training set, ~63,960 emails):**
- Legitimate: approximately 60–65% of corpus
- Phishing: approximately 35–40% of corpus
- `class_weight="balanced"` corrects for any remaining imbalance during training

---

## Evaluation Metrics

Evaluated on a held-out test set of 595 emails (20% stratified split):

| Class | Precision | Recall | F1-Score |
|---|---|---|---|
| Legitimate | 98.81% | 99.80% | 99.30% |
| Phishing | 98.88% | 93.62% | 96.17% |
| **Overall accuracy** | | | **98.82%** |
| **False Positive Rate** | | | **~0.20%** |
| **AUC-ROC** | | | ~0.99 (estimated) |

**Key metric discussion:**

- **False Positive Rate (~0.20%)** — approximately 1 in 500 legitimate emails is incorrectly flagged. In a 100-email/day SOC queue this translates to roughly one false-positive alert per week — a manageable analyst burden.
- **Phishing Recall (93.62%)** — the model misses ~6.4% of phishing emails. In a layered defence, missed detections are caught by the LLM layer or header analysis. This is why a dual-layer architecture is used rather than relying on ML alone.
- **Precision (98.88% for phishing)** — when the model says phishing, it is almost always right, supporting high analyst confidence in positive verdicts.

---

## Model Architecture Details

```
TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 2),     # unigrams + bigrams
    sublinear_tf=True,       # log(1 + tf) dampens high-frequency term dominance
    stop_words="english"     # removes stopwords before vectorisation
)

LogisticRegression(
    C=1.0,                   # inverse regularisation strength (standard default)
    class_weight="balanced", # weights inversely proportional to class frequency
    max_iter=1000,
    random_state=42,
    solver="lbfgs"           # scikit-learn default for small-to-medium problems
)
```

**Why Logistic Regression over alternatives:**

| Alternative | Reason not selected |
|---|---|
| Naive Bayes | Assumes conditional independence of features — invalid for phishing where "click here" + "verify account" co-occurrence is the signal. F1 on phishing class is −4.1 pp vs. LR. |
| Random Forest | Competitive accuracy but feature importance is aggregated across trees, making per-prediction explanation harder to surface in a UI |
| BERT / transformer | Highest accuracy ceiling but ~100× inference latency, requires GPU for production, and outputs opaque embeddings that resist the "which token caused this?" explainability requirement |
| SVM (linear kernel) | Similar interpretability to LR; LR chosen for simpler probability calibration and faster inference |

---

## Known Limitations

### Data limitations

1. **Corpus age:** SpamAssassin corpus data dates from 2002–2005. Phishing language has evolved significantly — brand impersonation (Microsoft, PayPal, DocuSign) and BEC vocabulary may be under-represented. The synthetic samples fill some modern gaps.

2. **English-only:** All training data is English. Non-English phishing will produce arbitrary scores.

3. **Text-only:** The model sees only subject and body text. Image-based phishing (embedded screenshots of credential forms), QR code phishing ("quishing"), and attachment-based delivery (T1566.001) are invisible to this classifier.

4. **Header-blind at training time:** SPF/DKIM/DMARC signals are handled by the separate header analysis layer, not incorporated into the ML model's features.

### Adversarial limitations

5. **LLM-generated phishing text:** Large language models produce grammatically flawless phishing emails that defeat traditional grammar/spelling heuristics — a category of signal this model may partially rely on. An adversary using Claude/GPT-4 to craft phishing text will see reduced detection rates. This is the most significant current limitation.

6. **Token obfuscation:** Inserting invisible Unicode characters, zero-width spaces, or homoglyph substitutions into key phishing tokens (e.g., `vеrify` with a Cyrillic `е`) bypasses TF-IDF feature matching for those tokens.

7. **Evasion via synonyms:** Replacing flagged tokens ("click here" → "follow this link") reduces the TF-IDF weight of known signals.

8. **No adversarial training:** The model was not hardened against deliberate evasion. Adversarial robustness would require generating perturbed examples and retraining.

### Operational limitations

9. **No confidence calibration audit:** Probability scores are used directly from Logistic Regression's softmax output. Platt scaling or isotonic regression calibration has not been applied to verify that `score=0.7` actually corresponds to 70% real-world prevalence.

10. **Static model:** The model is retrained manually (one-time script). It does not learn from analyst feedback or adapt to new phishing campaigns without full retraining.

---

## Fairness and Safety Notes

- **No demographic attributes in training data.** The SpamAssassin corpus contains raw email text with no demographic labels. No fairness analysis was performed on demographic subgroups.
- **Defensive use constraint.** The system prompt for the LLM layer explicitly prohibits Claude from generating phishing content. No generation endpoint exists in the API.
- **Synthetic demo data.** All demo samples use IANA-reserved `.example` and `.test` domains that cannot resolve, preventing any accidental live phishing simulation.
- **No PII retention.** Submitted emails are analysed in memory and not stored. No database or persistent storage layer exists.

---

## Environmental Impact

- **Training:** ~30 seconds on a single CPU core; negligible energy cost
- **Inference:** ~1ms per email on CPU (no GPU required)
- **Model size:** ~500KB serialized artifact

---

## Citation and Provenance

SpamAssassin Public Corpus: https://spamassassin.apache.org/old/publiccorpus/  
License: Apache 2.0  
No modifications to corpus content were made beyond CSV reformatting and label standardisation.
