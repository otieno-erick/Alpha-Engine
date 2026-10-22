| Requirement ID | Module / file(s) | Test name | Status (todo / in progress / passing) | Last updated |
|---|---|---|---|---|
| G-03 | app/services/rules.py, rules/phase1_baseline.yaml | test_rules_loader_loads_yaml | passing | 2026-10-22 |
| G-04 | app/services/submission.py | test_submission_requires_explicit_confirmation | passing | 2026-10-22 |
| G-06 | app/services/hash_cache.py | test_hash_cache_detects_duplicate_config | passing | 2026-10-22 |
| G-07 | app/services/quota.py | test_quota_guard_blocks_zero_remaining | passing | 2026-10-22 |
| G-10 | app/services/audit.py | test_audit_log_records_user_actions | passing | 2026-10-22 |
| A-01 | app/services/auth.py | test_persona_fallback_is_detected | passing | 2026-10-22 |
| A-03 | app/services/client.py | test_client_parses_recordset_payload | passing | 2026-10-22 |
| A-04 | app/services/quota.py | test_quota_reads_x_ratelimit_remaining | passing | 2026-10-22 |
| A-05 | app/services/batch.py | test_batch_splitter_keeps_like_configurations_together | passing | 2026-10-22 |
| H-01 | app/services/hash_cache.py | test_hash_changes_when_any_setting_changes | passing | 2026-10-22 |
| H-02 | app/services/hash_cache.py | test_duplicate_config_returns_cached_result | passing | 2026-10-22 |
| T-01 | app/services/scheduler.py | test_scheduler_uses_shared_slot_limit | passing | 2026-10-22 |
| T-05 | app/services/scheduler.py | test_scheduler_enforces_source_budget | passing | 2026-10-22 |
| Q-01 | app/services/quota.py | test_quota_guard_respects_reserve | passing | 2026-10-22 |
| R-01 | app/services/rules.py, rules/phase2_rules.yaml | test_rules_lookup_reads_phase2_values | passing | 2026-10-22 |
| V-01 | app/services/validator.py | test_validator_rejects_vector_field_without_vec_operator | passing | 2026-10-22 |
| V-03 | app/services/validator.py | test_validator_rejects_off_grid_window | passing | 2026-10-22 |
| C-01 | app/services/scorer.py | test_scorer_reports_margin_for_sub_universe_example | passing | 2026-10-22 |
| C-04 | app/services/scorer.py | test_scorer_applies_is_ladder_discount_for_low_turnover | passing | 2026-10-22 |
| D-01 | app/services/diagnoser.py | test_diagnoser_returns_first_failure_and_repair_instruction | passing | 2026-10-22 |
| L-05 | app/services/llm_hub.py | test_router_uses_fallback_when_primary_is_exhausted | passing | 2026-10-22 |
| M-05 | app/services/pipeline.py | test_pipeline_order_for_clean_alpha | passing | 2026-10-22 |
| J-02 | app/services/submission.py | test_submission_rejects_failed_alpha | passing | 2026-10-22 |
| AP-01 | app/services/submission.py | test_alpha_detail_exposes_core_fields | passing | 2026-10-22 |
| E-01 | app/services/evolution.py | test_seed_selection_and_mutation_generation | in progress | 2026-10-22 |
| E-02 | app/services/evolution.py | test_evolution_filter_keeps_only_valid_mutants | in progress | 2026-10-22 |
| E-03 | app/services/evolution.py | test_evolution_run_builds_candidate_pool | in progress | 2026-10-22 |
| K-01 | pyproject.toml | passing | 2026-10-22 |
| S-04 | app/main.py | pending | todo | |
| A-02 | app/services/auth.py | pending | todo | |
| A-06 | app/services/client.py | pending | todo | |
| A-07 | app/templates/index.html | pending | todo | |
| G-01 | package config | pending | todo | |
| G-02 | app/main.py | pending | todo | |
| G-05 | app/services/secret_store.py | pending | todo | |
| G-08 | app/templates/index.html | pending | todo | |
| G-09 | app/services/scheduler.py | pending | todo | |
| C-02 | app/services/scorer.py | pending | todo | |
| D-02 | app/services/diagnoser.py | pending | todo | |
| L-01 | app/templates/ | pending | todo | |
