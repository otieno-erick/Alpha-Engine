# Alpha Engine

Alpha Engine is a desktop-first research application that uses an LLM to generate hypotheses and expressions for WorldQuant BRAIN, validates and scores them, repairs failures, and only presents clean alphas for explicit human confirmation before submission.

This repository starts with the initial project structure and the required specification artifacts for the build plan described in the project brief.

## Current status

This is the initial repository scaffold for the first phase of the product lifecycle. It establishes:

- a Python + FastAPI application shell
- a rules directory that keeps policy values in YAML
- a testing baseline
- traceability and open-question tracking files

## Repository structure

```text
.
├── README.md
├── OPEN_QUESTIONS.md
├── TRACEABILITY.md
├── pyproject.toml
├── .gitignore
├── rules/
│   └── engine_rules.yaml
├── src/
│   └── alpha_engine/
│       ├── __init__.py
│       ├── __main__.py
│       └── app.py
├── tests/
│   └── test_app.py
└── docs/
    └── architecture.md
```

## Stack

- Engine: Python + FastAPI
- UI shell: pywebview-compatible app architecture
- Storage: SQLite
- Secrets: OS keychain
- Bundling: PyInstaller or Nuitka target
- No Node.js at build time or runtime

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
python -m alpha_engine
```

The app exposes a health endpoint at:

```text
http://127.0.0.1:8080/health
```

## Notes

This scaffold intentionally keeps the implementation minimal while matching the product specification: rules are stored as data files, the app is Python-based, and the project includes explicit traceability and open-item tracking.
