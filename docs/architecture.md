# Architecture notes

This repository begins with a minimal but realistic Python project layout aligned with the Alpha Engine specification.

## Layers

- `src/alpha_engine/app.py` exposes the FastAPI service and a health endpoint.
- `rules/engine_rules.yaml` keeps configuration values as data instead of hard-coded logic.
- `tests/test_app.py` validates the smoke path required before broader feature work begins.

## Phase 1 intent

The initial scaffold is intentionally minimal and designed to support a clean, testable extension path. It does not yet implement the full BRAIN client, LLM hub, or packaging pipeline; those belong to later phases in the product design document.

The app runs locally on port 8080 by default.
