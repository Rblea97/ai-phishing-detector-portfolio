# Resume Bullets — AI Phishing Detector

Pick 3–4 of these depending on what the job description emphasizes. Never use all 5.
Tailor by swapping in exact language from the posting where it maps to what you actually built.

---

- Built a blue team email threat detection system using Python, ML (TF-IDF + Logistic Regression), and Claude LLM; achieved 98.82% accuracy and 96.17% F1 on the phishing class across 595 held-out emails with a ~0.20% false positive rate

- Mapped threat detection logic to MITRE ATT&CK T1566 (Phishing); system extracts Indicators of Compromise (IOCs) including malicious URLs, urgency language, and impersonation patterns from email content

- Implemented Explainable AI (XAI) layer providing SOC analysts with per-prediction feature weights and LLM-generated risk reasoning to support alert triage and escalation decisions

- Engineered CI/CD pipeline with SAST (CodeQL), automated test suite (62 pytest / 16 Vitest), Dependabot dependency management, and zero-downtime deployment — DevSecOps practices from day one

- Selected Logistic Regression over Naive Bayes (+4.1 F1 pp on attack class) based on coefficient-based explainability requirements for SOC analyst workflows; documented model decision rationale in project README

---

## Resume Project Header

**AI Phishing Detector** | Python, FastAPI, React, scikit-learn, Claude API | [GitHub](https://github.com/Rblea97/ai-phishing-detector-portfolio) | [Live Demo](https://phishing-detector-ui-s3bf.onrender.com)

---

## Which Bullets to Use By Role

| Target Role | Prioritize |
|---|---|
| SOC Analyst Tier 1 | Bullets 1, 2, 3 — threat detection, IOCs, triage |
| DevSecOps / Security Engineer | Bullets 1, 4, 5 — accuracy, CI/CD, model decision |
| GRC / Risk Analyst | Bullets 2, 3 — MITRE ATT&CK mapping, explainability |
| Threat Intelligence | Bullets 2, 3 — IOCs, reasoning output |
