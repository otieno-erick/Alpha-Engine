# Alpha Engine

## Purpose
A desktop app that uses an LLM to generate hypotheses and expressions for WorldQuant BRAIN, simulates them, reads the results, repairs failures, and hands the user only alphas with zero failed checks. The user confirms every submission.

## 0. Instructions to the AI building this (read first, every session)

1. Work in phases (Section 3). Do not start a phase until the previous phase's done gate passes.
2. Every requirement has an ID and an acceptance test. A requirement is not done until its test exists and passes.
3. At the end of every session, update `TRACEABILITY.md` (Section 8): requirement ID, file(s), test name, status. Start every session by reading it.
4. Never skip a requirement because it looks minor. If a requirement is unclear, add it to `OPEN_QUESTIONS.md` and ask.
5. Rules (thresholds, matrices, limits) live in data files (`rules/*.yaml`), never hard-coded in logic.
6. Never invent API endpoints or thresholds. Verify against the live BRAIN documentation and API responses. Record the source and verified date for every rule.

## 1. Global requirements

| ID | Requirement | Acceptance test |
|---|---|---|
| G-01 | No Node.js at build time or run time. | CI build log and the installed app contain no Node process or `node_modules`. |
| G-02 | Closing the app window ends every backend, worker and child process. | After exit, no app process remains (checked on Windows, macOS, Linux), including after a forced crash. |
| G-03 | Rules are data files with `id`, `value`, `source`, `last_verified`. | Changing a threshold in YAML changes scorer output with no code change. |
| G-04 | Nothing is submitted without an explicit user click on a confirm button. | Automated test: no code path calls the submit endpoint without a confirmation token. |
| G-05 | API keys and BRAIN credentials are stored in the OS keychain, never in plain text or logs. | Grep of data directory and logs finds no secrets. |
| G-06 | Every simulation request passes the hash cache check first. | Duplicate config is never sent; cached result is returned and counted as "saved". |
| G-07 | Quota guard: no task may send a simulation when remaining quota is zero or below the reserve. | Test with mocked quota = 0 sends nothing. |
| G-08 | Every alpha ID is shown wherever the alpha appears and links to the detail popup. | UI test on every list view. |
| G-09 | Stop All button stops every task within 10 seconds. | Test with 3 running tasks. |
| G-10 | All user-visible actions that spend quota or change state are written to an audit log. | Audit log contains entries for sim batches, confirmations, setting changes. |

## 2. Tech stack (fixed)

| Piece | Choice |
|---|---|
| Engine | Python + FastAPI |
| UI | Server-rendered pages, HTMX + Alpine.js, Tailwind via its standalone binary |
| Charts | Vendored JS chart library committed to the repo (no package manager) |
| Window | pywebview (OS native web view), backend runs inside the same process |
| Storage | SQLite; secrets in the OS keychain |
| Bundling | PyInstaller or Nuitka, one self-contained app |
| Installers | GitHub Actions matrix: Windows `.exe`, macOS `.dmg`, Linux AppImage + `.deb` |
| Phone | Mobile-friendly page served by the desktop app; token protected; off by default |

## 3. Phases and done gates

| Phase | Contents | Done gate |
|---|---|---|
| 1 | Packaging skeleton (K), client + auth (A), sync (S), hash cache (H), scheduler + quota (T, Q) | A "hello" installer builds for all OSes, installs on a clean machine, opens, signs in, syncs, and exits cleanly. |
| 2 | Rules registry (R), validator (V), scorer (C), diagnoser (D) | Scorer reproduces known results: sub-universe example 1.17 vs 1.18 fails; IS Ladder 30% turnover discount applied. |
| 3 | LLM hub (L), creation loop (M) | End-to-end run: dataset in, hypotheses, expressions, simulation, read, repair, a zero-fail alpha or a logged stop. |
| 4 | Alpha popup (AP), Alphas (AL), Portfolio (PF), Submission Planner (J) | User can confirm and submit a zero-fail alpha with a description. |
| 5 | Evolution Lab (E), Template Lab (P), Correlation Breaker (B), Sampler (X) | Each tool creates tagged tasks that flow into the Planner. |
| 6 | Extras (F), mobile page (MB), auto-update, hardening | All acceptance tests pass on all three OSes. |

## 4. Core services

### A. Client and auth
| ID | Requirement | Acceptance test |
|---|---|---|
| A-01 | Authenticate with BRAIN, including the biometrics (persona) fallback. | Mock 401 with `WWW-Authenticate: persona` triggers the biometrics prompt and completes. |
| A-02 | Detect session expiry and re-authenticate before long runs. | Expired-session mock causes re-auth, not silent failures. |
| A-03 | Simulate, poll with `Retry-After`, fetch recordsets (pnl, sharpe, turnover, yearly-stats, etc.) with pagination. | Test against recorded responses returns parsed `{schema, records}`. |
| A-04 | Read `X-Ratelimit-Remaining` and store it as the authoritative quota. | Quota shown in the UI matches the header. |
| A-05 | Multi-simulation batching within platform limits; region, delay, language, instrument must match inside a batch. | Mixed-setting batch is split automatically. |
| A-06 | Region-agnostic fix: when region is ALL, set type `REGION_AGNOSTIC` and lookback 0. | Request payload inspected in test. |
| A-07 | Header display: BRAIN session time left, simulations left today, quota reset countdown. | UI test with mocked values. |

### S. Sync
| ID | Requirement | Acceptance test |
|---|---|---|
| S-01 | One-click Sync pulls all regions available to the user, operators, data fields, submitted alphas and unsubmitted alphas. | Local DB row counts match the API counts. |
| S-02 | Sync stores each field's category, coverage, type (matrix/vector), region, delay, universe. | Field records contain all attributes. |
| S-03 | Sync is incremental and resumable. | Interrupt mid-sync, rerun, no duplicates. |
| S-04 | App loads from the local cache instantly. | Cold start renders Alphas tab without network. |

### H. Hash cache
| ID | Requirement | Acceptance test |
|---|---|---|
| H-01 | Hash covers the full config: expression, region, universe, delay, neutralization, truncation, decay, test period, and all other settings. | Changing any single setting changes the hash. |
| H-02 | On a hit, return the stored alpha ID and result; do not simulate. | Counter of "quota saved" increments. |
| H-03 | Pruning policy (default 90 days) is configurable. | Old rows removed on schedule. |
| H-04 | Cache also covers children of multi-sim batches before they are sent. | Batch with duplicates sends only new items. |

### T. Task scheduler
| ID | Requirement | Acceptance test |
|---|---|---|
| T-01 | One scheduler for all task sources, sharing the 10 concurrent slots. | Two tasks never exceed 10 slots combined. |
| T-02 | Every task is named and tagged by origin: `LLM`, `Evolution`, `PowerPool`, `ATOM`, `Template`, `Sampler`, `CorrBreaker`. | Tasks tab shows the tag for each. |
| T-03 | Per-task core allocation (for example 4 + 4 + 2). | Allocation respected and adjustable while running. |
| T-04 | Tasks tab shows status, slots in use, waiting count, stop button per task. | UI test. |
| T-05 | Priorities and per-source quota budget (percent of daily quota). | A source at its budget stops sending. |
| T-06 | Tasks survive app restart as resumable or cleanly cancelled. | Restart test. |

### Q. Quota
| ID | Requirement | Acceptance test |
|---|---|---|
| Q-01 | Maintain a reserve that tasks cannot spend. | Reserve is never crossed. |
| Q-02 | Show quota used per task source today. | Matches ledger. |

## 5. Intelligence layer

### R. Rules registry
| ID | Requirement | Acceptance test |
|---|---|---|
| R-01 | Store thresholds by tier (user/consultant), delay (D0/D1), region overrides, universe overrides. | Lookup function returns correct values for each combination. |
| R-02 | Store the neutralization matrix by dataset category, Power Pool criteria, HTVR classes, Genius level limits, quota map. | Each table loadable and unit-tested. |
| R-03 | Every rule has source and last-verified date; stale rules (older than 90 days) are flagged. | Flag appears in the UI. |
| R-04 | Conflicting values must be resolved before release (see Section 9). | `OPEN_QUESTIONS.md` has no unresolved conflict at release. |

### V. Pre-simulation validator
| ID | Requirement | Acceptance test |
|---|---|---|
| V-01 | Syntax check of Fast Expression. | Invalid expressions are rejected locally. |
| V-02 | Reject vector fields used without a `vec_` operator. | Test expression rejected. |
| V-03 | Enforce parameter grid (5, 10, 21, 63, 121, 252) unless user overrides. | Off-grid window flagged. |
| V-04 | Power Pool constraints: operators ≤ 8 (excluding backfills), unique fields ≤ 3. | Counts match the rules. |
| V-05 | Reject fields the user has no access to. | Uses synced access data. |
| V-06 | Reject duplicates via hash cache. | See H-02. |

### C. Scorer
| ID | Requirement | Acceptance test |
|---|---|---|
| C-01 | Compute every submission check locally from simulation results. | Matches platform results on recorded samples. |
| C-02 | Report margin for each check, not only pass/fail. | Sub-universe example shows 1.17 vs 1.18 cutoff, margin -0.01. |
| C-03 | Sub-universe formula and flat-ratio universes. | Unit tests for TOP and non-TOP universes. |
| C-04 | IS Ladder: iterate 2 to 10 years, PASS/FAIL thresholds, 0.85 discount when turnover below 30%. | Table-driven tests. |
| C-05 | Fitness formula with the 12.5% turnover floor. | Test cases 1.37 and 1.73 from the reference posts. |
| C-06 | Weight check: concentration and sparsity modes reported separately. | Test with each failure mode. |
| C-07 | Regional extras (CHN, ASI, GLB, JPN etc.) from rules registry. | One test per region. |
| C-08 | An alpha is "clean" only when every applicable check passes. | Flag used by the Planner. |

### D. Failure diagnoser
| ID | Requirement | Acceptance test |
|---|---|---|
| D-01 | Reads failures in the platform's cascade order and returns the first failing check as the action item. | Test with multiple failures. |
| D-02 | Maps each failure to a repair instruction (cheapest first: weight/coverage, turnover under 30%, IS Ladder, Sharpe, correlation). | Mapping table tested. |
| D-03 | Correlation failures trigger a structural change (dataset, region, delta), not tuning. | Repair type recorded. |
| D-04 | Retry budget per lineage; on exhaustion, mark abandoned with reason. | Budget test. |

## 6. LLM and creation loop

### L. LLM hub
| ID | Requirement | Acceptance test |
|---|---|---|
| L-01 | Providers tab: cards for Google AI Studio, Groq, Cerebras, OpenRouter, NVIDIA NIM, Mistral, GitHub Models, Hugging Face (free), plus OpenAI and Anthropic Claude (bring your own key, billed to user). | UI shows all cards with key status. |
| L-02 | Clicking a card opens the add-key popup and a button opens the provider's key page in the browser. | Test opens the right URL per provider. |
| L-03 | Tabs: Providers, Keys, Models, Budget, Prompts, Assistant. | All tabs present. |
| L-04 | Model setup popup: searchable model list, requests per minute, requests per day, reset timezone, max prompt tokens. | Values saved and enforced. |
| L-05 | Router stops each key at its limits and fails over to the next provider automatically. | Simulated limit hit switches provider with no failed request. |
| L-06 | Paid keys require a daily request cap set by the user. | Cap enforced. |
| L-07 | Budget tab shows usage per key, model and day. | Matches ledger. |
| L-08 | Prompts are versioned; each generated alpha records the prompt version. | Version stored on lineage. |
| L-09 | LLM output is parsed strictly (structured format); malformed output is retried or discarded. | Malformed sample handled. |

### M. Creation loop
| ID | Requirement | Acceptance test |
|---|---|---|
| M-01 | User selects datasets, or the agent selects them from user filters (coverage, value score, crowdedness, category, region, delay, universe). | Both modes produce a dataset list. |
| M-02 | For each dataset, the LLM generates several hypotheses, each with a one-sentence economic rationale. Prompt includes field cards. | Hypotheses stored with dataset and prompt version. |
| M-03 | Each hypothesis becomes one or more expressions, with neutralization chosen from the matrix. | Expression records link to hypothesis. |
| M-04 | One LLM call produces many expressions (batching) to respect free-tier limits. | Call count per N expressions is low. |
| M-05 | Pipeline order: validate, hash check, simulate, score, diagnose, repair, repeat. | Integration test over a mocked BRAIN. |
| M-06 | Repair prompts include the exact failure, margin and instruction. | Prompt log inspected. |
| M-07 | Stops when a clean alpha is found, retry budget is exhausted, or quota budget for the task is reached. | Each stop reason logged. |
| M-08 | Field profiler runs the six probe expressions on unknown fields and stores a field card. | Field card created. |
| M-09 | Generation favors datasets and regions where the user's submitted pool is thin. | Test with a skewed pool. |
| M-10 | Lineage store records parent, settings, results, failure reason, prompt version for every alpha. | Query returns the full chain. |
| M-11 | Overfitting guards: Test Period check, cross-universe check, simplicity limit. | Guard flags are recorded. |

## 7. Workbench tabs and tools

### J. Submission Planner
| ID | Requirement | Acceptance test |
|---|---|---|
| J-01 | Collects candidates from all task sources and checks them. | Candidates from two sources appear. |
| J-02 | Accepts only alphas with zero failed checks; others are dropped or returned to repair with a reason. | Alpha with one fail is excluded. |
| J-03 | Runs the platform's own `check_submission` before listing an alpha as ready. | Mock check failure removes the alpha. |
| J-04 | Confirmation panel shows the full checklist, correlations and a description editor. | UI test. |
| J-05 | Description editor: LLM drafts Idea, Data rationale, Operator rationale; confirm stays disabled until length requirement (100+ characters for Power Pool) is met. | Short description blocks confirm. |
| J-06 | Submission happens only on user click; respects daily and monthly limits (for example D0 5/month). | Limit test. |
| J-07 | Notifications when an alpha becomes ready to confirm. | Desktop notification fires. |

### AP. Alpha detail popup
| ID | Requirement | Acceptance test |
|---|---|---|
| AP-01 | Clicking any alpha opens a popup with ID, expression, settings, dataset, hypothesis, lineage. | UI test. |
| AP-02 | PnL chart, yearly stats, IS summary. | Data loaded from recordsets. |
| AP-03 | Every check with its margin. | Matches scorer output. |
| AP-04 | Manual buttons: Check Prod Correlation and Check Self Correlation. One request at a time; last result cached with timestamp. | Rapid clicks send one request. |
| AP-05 | Open in BRAIN button opens the alpha on the BRAIN website. | URL test. |
| AP-06 | Notes and tags editable. | Persisted. |
| AP-07 | "Explain failure" button sends context to the LLM and shows a repair plan. | Returns a plan for a failed alpha. |

### AL. Alphas tab
| ID | Requirement | Acceptance test |
|---|---|---|
| AL-01 | Lists submitted and unsubmitted alphas with IDs. | Counts match Sync. |
| AL-02 | Auto-classification by region, delay, turnover band, Sharpe tier, dataset, status, and the failing check that blocks it. | Filters work on each. |
| AL-03 | Sort and filter; bulk select to send to Evolution Lab or Planner. | Selection flows to target. |

### PF. Portfolio tab
| ID | Requirement | Acceptance test |
|---|---|---|
| PF-01 | Shows submitted pool with performance and correlation info. | Data matches API. |
| PF-02 | Pool diversity map by dataset and region, with gaps highlighted. | Gap detection test. |
| PF-03 | Post-submission health monitor flags degrading alphas. | Test with a degrading series. |

### E. Evolution Lab
| ID | Requirement | Acceptance test |
|---|---|---|
| E-01 | Manual seed selection from submitted or unsubmitted alphas via checkboxes. | Selected seeds are used. |
| E-02 | Auto-select mode picks best performers using user filters, with diversity and correlation filters so near-copies are not repeated. | Test with clustered alphas selects spread seeds. |
| E-03 | Mutations: swap operator, swap field, swap dataset, tweak parameters (on grid). | Each mutation type tested. |
| E-04 | LLM-assisted mutation with a user instruction (for example "make it orthogonal with a Fast D1 news field"). | Instruction appears in the prompt. |
| E-05 | Mutants pass the validator and hash cache before simulation. | Duplicate mutant not sent. |

### P. Template Lab
| ID | Requirement | Acceptance test |
|---|---|---|
| P-01 | User can add multiple templates with placeholders such as `{field}`, `{window}`, `{group}`. | Two templates saved. |
| P-02 | Expansion across chosen fields, windows and groups, with a preview count before running. | Count matches product of inputs. |
| P-03 | Expanded items go through the validator and cache. | Invalid combos removed. |

### B. Correlation Breaker
| ID | Requirement | Acceptance test |
|---|---|---|
| B-01 | For a correlation-failed alpha, test structured variations: RAM neutralization, `trade_when` trigger, Fast D1 delta, dataset or region change. | Variants created per type. |
| B-02 | Applies the 10% Sharpe escape clause check. | Test with 3.18 vs 3.50 example. |
| B-03 | Does not add noise to reduce correlation. | No noise-based variants exist. |
| B-04 | Respects correlation rate limits. | One check at a time. |

### X. Setting Sampler
| ID | Requirement | Acceptance test |
|---|---|---|
| X-01 | Generates a grid of neutralization, decay, truncation and other settings. | Grid size shown before running. |
| X-02 | Defaults come from the dataset category matrix. | Defaults verified. |

### Other tabs
| ID | Requirement | Acceptance test |
|---|---|---|
| W-01 | Dashboard: quota, session, running work, close-to-submittable list. | UI test. |
| W-02 | Tasks tab (see T). | See T. |
| W-03 | Data Explorer view of synced datasets and fields with filters and field cards. | Filters work. |

## 8. Packaging, platforms, extras

### K. Packaging
| ID | Requirement | Acceptance test |
|---|---|---|
| K-01 | GitHub Actions builds Windows `.exe` installer, macOS `.dmg`, Linux AppImage and `.deb` on every release tag. | Release page has all artifacts. |
| K-02 | The installer contains every dependency; first launch needs no manual installs. | Test on clean VMs. |
| K-03 | App exit ends all processes (see G-02). | Process list check. |
| K-04 | Auto-update checks GitHub Releases. | Update test from an older build. |
| K-05 | Unsigned-build warnings documented in the README. | README section exists. |
| K-06 | Diagnostics bundle with secrets removed. | Bundle contains no keys. |
| K-07 | Backup and restore of local data. | Restore reproduces state. |

### MB. Mobile page
| ID | Requirement | Acceptance test |
|---|---|---|
| MB-01 | Optional mobile-friendly page for monitoring and confirming; off by default; token required. | Access without token is denied. |
| MB-02 | Credentials and LLM keys never leave the desktop. | Network inspection shows none. |

### F. Extras
| ID | Requirement | Acceptance test |
|---|---|---|
| F-01 | Failure analytics by dataset, region, test. | Charts render from data. |
| F-02 | Scheduled overnight runs with morning summary. | Scheduled task runs. |
| F-03 | Dry-run mode using cached data, no quota spent. | Quota unchanged after run. |
| F-04 | Audit log viewer. | See G-10. |

## 9. Open items to resolve before release (verify against live BRAIN docs)

1. Consultant D1 Sharpe threshold appears as both 1.58 and 1.59 in the source summaries.
2. Max weight appears as 10% (submission check) and under 8% (USA, OS-side). Decide which the scorer enforces and where.
3. Confirm every API endpoint and recordset name from live responses.
4. Confirm correlation endpoint rate limits.
5. Confirm Power Pool theme rules and graduated quota.
6. The source summaries are secondary; every number in `rules/*.yaml` needs a primary-source check.

## 10. Out of scope for version 1

Native phone app, running the engine on a phone, Pyramids and Competitions tabs, SuperAlpha construction.

## 11. TRACEABILITY.md template

| Requirement ID | Module / file(s) | Test name | Status (todo / in progress / passing) | Last updated |
|---|---|---|---|---|
| G-01 | | | todo | |
| (one row per requirement above) | | | | |

