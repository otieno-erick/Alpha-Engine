1| | Requirement ID | Module / file(s) | Test name | Status (todo / in progress / passing) | Last updated |
2| |---|---|---|---|---|
3| | G-01 | app/services/runtime_security.py | test_global_runtime_has_no_node_modules | passing | 2026-11-01 |
4| | G-02 | app/services/runtime_security.py | test_global_runtime_stops_all_processes | passing | 2026-11-01 |
5| | G-03 | app/services/rules.py, rules/phase1_baseline.yaml | test_rules_loader_loads_yaml | todo | 2026-11-01 |
6| | G-04 | app/services/submission.py | test_submission_requires_explicit_confirmation | passing | 2026-10-22 |
7| | G-05 | app/services/secret_store.py | test_secret_store_uses_keychain_not_plaintext | passing | 2026-11-01 |
8| | G-06 | app/services/hash_cache.py | test_hash_cache_detects_duplicate_config | todo | 2026-11-01 |
9| | G-07 | app/services/quota.py | test_quota_guard_blocks_zero_remaining | passing | 2026-10-22 |
10| | G-08 | app/services/submission.py | test_alpha_id_renders_as_detail_link | passing | 2026-11-01 |
11| | G-09 | app/services/scheduler.py | test_scheduler_stop_all_stops_running_tasks | passing | 2026-11-01 |
12| | G-10 | app/services/audit.py | test_audit_log_records_user_actions | passing | 2026-10-22 |
13| | A-01 | app/services/auth.py | test_persona_fallback_is_detected | passing | 2026-10-22 |
14| | A-02 | app/services/auth.py | test_persona_fallback_is_detected | passing | 2026-11-01 |
15| | A-03 | app/services/client.py | test_client_parses_recordset_payload | passing | 2026-10-22 |
16| | A-04 | app/services/quota.py | test_quota_reads_x_ratelimit_remaining | passing | 2026-10-22 |
17| | A-05 | app/services/batch.py | test_batch_splitter_keeps_like_configurations_together | todo | 2026-11-01 |
18| | A-06 | app/services/client.py | test_client_normalizes_region_agnostic_payload | passing | 2026-11-01 |
19| | A-07 | app/templates/index.html | UI header displays session/quota values | passing | 2026-11-01 |
20| | S-01 | app/db.py, app/main.py | test_app_loads_cached_alphas_offline | todo | 2026-11-01 |
21| | S-02 | app/db.py, app/main.py | test_app_loads_cached_alphas_offline | todo | 2026-11-01 |
22| | S-03 | app/db.py, app/main.py | test_app_loads_cached_alphas_offline | todo | 2026-11-01 |
23| | S-04 | app/db.py, app/main.py | test_app_loads_cached_alphas_offline | passing | 2026-11-01 |
24| | H-01 | app/services/hash_cache.py | test_hash_changes_when_any_setting_changes | passing | 2026-10-22 |
25| | H-02 | app/services/hash_cache.py | test_duplicate_config_returns_cached_result | passing | 2026-10-22 |
26| | H-03 | app/services/hash_cache.py | test_hash_cache_prunes_old_entries_by_default_window | todo | 2026-11-01 |
27| | H-04 | app/services/hash_cache.py | test_hash_cache_covers_child_batch_items_before_send | todo | 2026-11-01 |
28| | T-01 | app/services/scheduler.py | test_scheduler_uses_shared_slot_limit | passing | 2026-10-22 |
29| | T-02 | app/services/scheduler.py | test_scheduler_tags_tasks_by_origin | todo | 2026-11-01 |
30| | T-03 | app/services/scheduler.py | test_scheduler_respects_per_task_slot_allocation | todo | 2026-11-01 |
31| | T-04 | app/templates/tasks.html, app/services/scheduler.py | test_tasks_tab_shows_status_slots_and_stop_controls | todo | 2026-11-01 |
32| | T-05 | app/services/scheduler.py | test_scheduler_enforces_source_budget | passing | 2026-10-22 |
33| | Q-01 | app/services/quota.py | test_quota_guard_respects_reserve | passing | 2026-10-22 |
34| | Q-02 | app/services/quota.py | test_quota_usage_is_shown_by_source_today | todo | 2026-11-01 |
35| | R-01 | app/services/rules.py, rules/phase2_rules.yaml | test_rules_lookup_reads_phase2_values | passing | 2026-10-22 |
36| | R-02 | app/services/rules.py, rules/phase2_rules.yaml | test_rules_loader_loads_neutralization_matrix | todo | 2026-11-01 |
37| | R-03 | app/services/rules.py, rules/phase2_rules.yaml | test_rules_flags_stale_rule_sets | todo | 2026-11-01 |
38| | R-04 | app/services/rules.py, rules/phase2_rules.yaml | test_rules_reject_unresolved_conflicts | todo | 2026-11-01 |
39| | V-01 | app/services/validator.py | test_validator_rejects_vector_field_without_vec_operator | passing | 2026-10-22 |
40| | V-02 | app/services/validator.py | test_validator_rejects_vector_field_without_vec_operator | todo | 2026-11-01 |
41| | V-03 | app/services/validator.py | test_validator_rejects_off_grid_window | passing | 2026-10-22 |
42| | V-04 | app/services/validator.py | test_validator_enforces_power_pool_limits | todo | 2026-11-01 |
43| | V-05 | app/services/validator.py | test_validator_rejects_unavailable_fields | todo | 2026-11-01 |
44| | V-06 | app/services/validator.py | test_validator_rejects_duplicate_in_hash_cache | todo | 2026-11-01 |
45| | C-01 | app/services/scorer.py | test_scorer_reports_margin_for_sub_universe_example | passing | 2026-10-22 |
46| | C-02 | app/services/scorer.py | test_scorer_reports_margin_for_sub_universe_example | passing | 2026-11-01 |
47| | C-03 | app/services/scorer.py | test_scorer_handles_top_and_flat_ratio_universes | todo | 2026-11-01 |
48| | C-04 | app/services/scorer.py | test_scorer_applies_is_ladder_discount_for_low_turnover | passing | 2026-10-22 |
49| | C-05 | app/services/scorer.py | test_scorer_uses_12_5_percent_turnover_floor | todo | 2026-11-01 |
50| | C-06 | app/services/scorer.py | test_scorer_reports_weight_failures_separately | todo | 2026-11-01 |
51| | C-07 | app/services/scorer.py | test_scorer_applies_regional_extras_from_rules | todo | 2026-11-01 |
52| | C-08 | app/services/scorer.py | test_scorer_flags_alpha_clean_only_when_all_checks_pass | todo | 2026-11-01 |
53| | D-01 | app/services/diagnoser.py | test_diagnoser_returns_first_failure_and_repair_instruction | passing | 2026-10-22 |
54| | D-02 | app/services/diagnoser.py | test_diagnoser_maps_correlation_and_weight_failures_to_repair_instructions | passing | 2026-11-01 |
55| | D-03 | app/services/diagnoser.py | test_diagnoser_uses_structural_repair_for_correlation_failures | todo | 2026-11-01 |
56| | D-04 | app/services/diagnoser.py | test_diagnoser_exhausts_retry_budget_and_marks_abandoned | todo | 2026-11-01 |
57| | L-01 | app/templates/index.html, app/services/llm_hub.py | test_provider_catalog_includes_all_required_cards | passing | 2026-11-01 |
58| | L-02 | app/services/llm_hub.py | test_provider_key_popup_opens_correct_url | todo | 2026-11-01 |
59| | L-03 | app/services/llm_hub.py, app/templates/index.html | test_llm_tabs_include_providers_keys_models_budget_prompts_assistant | todo | 2026-11-01 |
60| | L-04 | app/services/llm_hub.py | test_model_setup_popup_keeps_values_and_limits | todo | 2026-11-01 |
61| | L-05 | app/services/llm_hub.py | test_router_uses_fallback_when_primary_is_exhausted | passing | 2026-11-01 |
62| | L-06 | app/services/llm_hub.py | test_budget_ledger_summarizes_requests_by_provider_model_and_day | passing | 2026-11-01 |
63| | L-07 | app/services/llm_hub.py | test_budget_ledger_summarizes_requests_by_provider_model_and_day | passing | 2026-11-01 |
64| | L-08 | app/services/llm_hub.py | test_prompt_versioner_tracks_alpha_prompt_versions | passing | 2026-11-01 |
65| | L-09 | app/services/llm_hub.py | test_structured_output_parser_rejects_malformed_json | passing | 2026-11-01 |
66| | M-01 | app/services/pipeline.py | test_creation_loop_selects_datasets_and_generates_hypotheses | passing | 2026-11-01 |
67| | M-02 | app/services/pipeline.py | test_creation_loop_selects_datasets_and_generates_hypotheses | passing | 2026-11-01 |
68| | M-03 | app/services/pipeline.py | test_creation_loop_generates_expressions_and_runs_pipeline | passing | 2026-11-01 |
69| | M-04 | app/services/pipeline.py | test_creation_loop_generates_expressions_and_runs_pipeline | passing | 2026-11-01 |
70| | M-05 | app/services/pipeline.py | test_creation_loop_generates_expressions_and_runs_pipeline | passing | 2026-11-01 |
71| | M-06 | app/services/pipeline.py | test_creation_loop_repair_prompts_and_lineage_are_recorded | passing | 2026-11-01 |
72| | M-07 | app/services/pipeline.py | test_creation_loop_generates_expressions_and_runs_pipeline | passing | 2026-11-01 |
73| | M-08 | app/services/pipeline.py | test_field_profiler_and_overfitting_guard_are_available | passing | 2026-11-01 |
74| | M-09 | app/services/pipeline.py | test_creation_loop_selects_datasets_and_generates_hypotheses | passing | 2026-11-01 |
75| | M-10 | app/services/pipeline.py | test_creation_loop_repair_prompts_and_lineage_are_recorded | passing | 2026-11-01 |
76| | M-11 | app/services/pipeline.py | test_field_profiler_and_overfitting_guard_are_available | passing | 2026-11-01 |
77| | J-01 | app/services/submission.py | test_submission_requires_explicit_confirmation | passing | 2026-11-01 |
78| | J-02 | app/services/submission.py | test_submission_rejects_failed_alpha | passing | 2026-10-22 |
79| | J-03 | app/services/submission.py | test_submission_rejects_failed_alpha | passing | 2026-11-01 |
80| | J-04 | app/services/submission.py | test_alpha_detail_exposes_core_fields | passing | 2026-11-01 |
81| | J-05 | app/services/submission.py | test_alpha_detail_exposes_core_fields | passing | 2026-11-01 |
82| | J-06 | app/services/submission.py | test_submission_requires_explicit_confirmation | passing | 2026-11-01 |
83| | J-07 | app/services/submission.py | test_submission_requires_explicit_confirmation | passing | 2026-11-01 |
84| | AP-01 | app/services/submission.py | test_alpha_detail_exposes_core_fields | passing | 2026-10-22 |
85| | AP-02 | app/services/submission.py | test_alpha_detail_exposes_core_fields | passing | 2026-11-01 |
86| | AP-03 | app/services/submission.py | test_alpha_detail_exposes_core_fields | passing | 2026-11-01 |
87| | AP-04 | app/services/submission.py | test_alpha_id_renders_as_detail_link | passing | 2026-11-01 |
88| | AP-05 | app/services/submission.py | test_alpha_id_renders_as_detail_link | passing | 2026-11-01 |
89| | AP-06 | app/services/submission.py | test_alpha_detail_exposes_core_fields | passing | 2026-11-01 |
90| | AP-07 | app/services/submission.py | test_alpha_detail_exposes_core_fields | passing | 2026-11-01 |
91| | AL-01 | app/services/submission.py | test_alpha_list_counts_submitted_and_unsubmitted | todo | 2026-11-01 |
92| | AL-02 | app/services/submission.py | test_alpha_list_auto_classifies_and_filters | todo | 2026-11-01 |
93| | AL-03 | app/services/submission.py | test_alpha_list_bulk_select_routes_to_target | todo | 2026-11-01 |
94| | E-01 | app/services/evolution.py | test_seed_selection_and_mutation_generation | passing | 2026-10-22 |
95| | E-02 | app/services/evolution.py | test_evolution_filter_keeps_only_valid_mutants | passing | 2026-10-22 |
96| | E-03 | app/services/evolution.py | test_evolution_run_builds_candidate_pool | passing | 2026-10-22 |
97| | E-04 | app/services/evolution.py | test_llm_mutation_includes_user_instruction | todo | 2026-11-01 |
98| | E-05 | app/services/evolution.py | test_mutants_pass_validator_and_hash_cache_before_simulation | todo | 2026-11-01 |
99| | P-01 | app/services/template_lab.py | test_template_lab_expands_and_counts_preview | passing | 2026-10-22 |
100| | P-02 | app/services/template_lab.py | test_template_lab_expands_across_fields_windows_and_groups | todo | 2026-11-01 |
101| | P-03 | app/services/template_lab.py | test_template_lab_rejects_invalid_expansions_after_validation | todo | 2026-11-01 |
102| | B-01 | app/services/correlation_breaker.py | test_correlation_breaker_generates_structured_variants | passing | 2026-10-22 |
103| | B-02 | app/services/correlation_breaker.py | test_correlation_breaker_applies_sharpe_escape_clause | todo | 2026-11-01 |
104| | B-03 | app/services/correlation_breaker.py | test_correlation_breaker_avoids_noise_based_variants | todo | 2026-11-01 |
105| | B-04 | app/services/correlation_breaker.py | test_correlation_breaker_respects_rate_limits | todo | 2026-11-01 |
106| | X-01 | app/services/sampler.py | test_sampler_builds_setting_grid_for_defaults | passing | 2026-10-22 |
107| | X-02 | app/services/sampler.py | test_sampler_uses_dataset_category_default_matrix | todo | 2026-11-01 |
108| | W-01 | app/templates/index.html, app/services/dashboard.py | test_dashboard_shows_quota_session_running_work_and_submit_ready_list | todo | 2026-11-01 |
109| | W-02 | app/templates/index.html, app/services/tasks.py | test_tasks_tab_matches_scheduler_requirements | todo | 2026-11-01 |
110| | W-03 | app/templates/index.html, app/services/data_explorer.py | test_data_explorer_filters_fields_and_field_cards | todo | 2026-11-01 |
111| | MB-01 | app/services/phase6.py | test_mobile_page_requires_token_when_enabled | passing | 2026-11-01 |
112| | MB-02 | app/services/phase6.py | test_mobile_page_keeps_credentials_and_llm_keys_off_device | todo | 2026-11-01 |
113| | F-01 | app/services/phase6.py | test_failure_analytics_grouped_by_dataset_region_and_test | todo | 2026-11-01 |
114| | F-02 | app/services/phase6.py | test_scheduled_overnight_runs_create_morning_summary | todo | 2026-11-01 |
115| | F-03 | app/services/phase6.py | test_dry_run_mode_uses_cached_data_without_quota_spend | todo | 2026-11-01 |
116| | F-04 | app/services/phase6.py | test_audit_viewer_filters_and_summarizes_events | passing | 2026-11-01 |
117| | K-01 | .github/workflows/release.yml, pyproject.toml | test_release_builds_artifacts_for_windows_macos_linux | passing | 2026-10-22 |
118| | K-02 | .github/workflows/release.yml, pyproject.toml | test_installer_runs_without_manual_setup_on_clean_vm | todo | 2026-11-01 |
119| | K-03 | .github/workflows/release.yml, app/services/runtime_security.py | test_app_exit_ends_all_processes_on_all_platforms | todo | 2026-11-01 |
120| | K-04 | app/services/auto_update.py | test_auto_update_checks_github_releases | todo | 2026-11-01 |
121| | K-05 | README.md | test_readme_documents_unsigned_build_warning | todo | 2026-11-01 |
122| | K-06 | app/services/diagnostics.py | test_diagnostics_bundle_removes_secrets | todo | 2026-11-01 |
123| | K-07 | app/services/backup_restore.py | test_backup_restore_reproduces_local_data_state | todo | 2026-11-01 |
124| 
125| | RESOLVED-RULE-01 | rules/*.yaml, app/services/rules.py | test_platform_rule_takes_precedence_over_local_mismatch | todo | 2026-11-01 |
126| | RESOLVED-RULE-02 | rules/*.yaml, app/services/rules.py | test_local_platform_mismatch_is_logged | todo | 2026-11-01 |
127| | RESOLVED-RULE-03 | rules/*.yaml, app/services/scorer.py | test_consultant_d1_sharpe_threshold_uses_1_58 | todo | 2026-11-01 |
128| | RESOLVED-RULE-04 | rules/*.yaml, app/services/scorer.py | test_is_ladder_d1_fail_threshold_uses_1_59 | todo | 2026-11-01 |
129| | RESOLVED-RULE-05 | rules/*.yaml, app/services/scorer.py | test_max_weight_fails_above_10_percent | todo | 2026-11-01 |
130| | RESOLVED-RULE-06 | rules/*.yaml, app/services/scorer.py | test_max_weight_warns_between_8_and_10_percent | todo | 2026-11-01 |
131| |
132| | NOTE: last_verified remains empty for all resolved rules until the live account check is complete. |
133| 