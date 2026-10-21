# Alpha Engine

Alpha Engine is a desktop-first research application that uses an LLM to generate hypotheses and expressions for WorldQuant BRAIN, validates and scores them, repairs failures, and only presents clean alphas for explicit human confirmation before submission.

This repository starts with the initial project structure and the required specification artifacts for the build plan described in the project brief.

## Current status

This repository contains the baseline scaffold and the Phase 1 shell for the product lifecycle. It establishes:

- a Python + FastAPI application shell
- a rules directory that keeps policy values in YAML
- a testing baseline
- traceability and open-question tracking files
- the Phase 1 service contracts for auth, sync, hash cache, scheduler, and quota enforcement

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
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py
│       ├── auth.py
│       ├── hash_cache.py
│       ├── phase1.py
│       ├── quota.py
│       ├── scheduler.py
│       └── sync.py
├── tests/
│   └── test_app.py
│   └── test_phase1_core.py
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

## Phase 1 service shell

The project now includes a minimal Phase 1 implementation shell for:

- auth state and session handling
- sync status and metadata tracking
- hash cache behavior and duplicate detection
- scheduler slots and task naming
- quota reserve and source-budget accounting

These are intentionally minimal service contracts and should be expanded as requirements are implemented.

## Notes

This scaffold intentionally keeps the implementation minimal while matching the product specification: rules are stored as data files, the app is Python-based, and the project includes explicit traceability and open-item tracking.
