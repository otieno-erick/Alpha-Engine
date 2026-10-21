# Alpha Engine initial scaffold

This file records the open questions that must be resolved against live BRAIN documentation before release.

## Open items

1. Consultant D1 Sharpe threshold appears as both 1.58 and 1.59 in source summaries.
2. Max weight appears as 10% in the submission check and under 8% in the USA OS-side rule. Decide which the scorer enforces and where.
3. Confirm every API endpoint and recordset name from live responses.
4. Confirm correlation endpoint rate limits.
5. Confirm Power Pool theme rules and graduated quota.
6. The source summaries are secondary; every number in `rules/*.yaml` needs a primary-source check.

## Notes

This project is intentionally scaffolded with a minimal working base and does not claim production compliance with the full specification yet. Each requirement should be implemented, tested, and then marked in `TRACEABILITY.md`.
