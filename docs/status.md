# Definition-of-done status (2026-10-14)

VERIFIED = executed with recorded evidence. Evidence paths are relative to the repo.

## Core application
| item | status | evidence |
|---|---|---|
| Real OpenCV 5 workload | VERIFIED (local) | `candidates/scanner_v*.py`; OpenCV 5.0.0 (`inspect_vision_environment`) |
| Processes actual images | VERIFIED | `artifacts/corpora/*/images` (synthetic PNGs) |
| Independent ground truth | VERIFIED | `synthetic.py` (homography corners), `metrics.py`, oracle test `tests/test_metrics.py::test_oracle_always_accepted` |
| Deterministic reproduction | VERIFIED | `tests/test_synthetic.py::test_deterministic`; failure bundles `deterministic=True` |
| Real-photo validation | NOT IMPLEMENTED | no licensed real dataset was added |

## MCP / agent
| item | status | evidence |
|---|---|---|
| Real MCP server (stdio) | VERIFIED | `tests/test_mcp.py` (official client lists 10 tools, calls them) |
| Claude Code can invoke it | IMPLEMENTED, NOT VERIFIED | `.mcp.json` present; server is *Pending approval* in `claude mcp list` (needs user approval) |
| Evidence changes next action | VERIFIED | `tests/test_agent.py` (distinct signatures → distinct actions); trace `artifacts/traces/*.jsonl` |
| Iterative workflow | VERIFIED | `artifacts/last_loop_output.txt` (REJECT, REJECT, PARTIAL×3, ACCEPT) |
| Iteration/resource limits | VERIFIED (unit) | `controller.py` limits + tests; remote budget persisted in `artifacts/remote_budget.json` |
| Failed candidates never "successful" | VERIFIED | `test_failed_candidate_cannot_be_reported_successful`, crash/none-detection candidates → REJECT |

## COOL / AWS
| item | status |
|---|---|
| COOL distribution identified | Secondary sources only (see official_sources.md); official pages returned 403 to our fetch |
| Marketplace subscription / AWS credentials | BLOCKED - none present (`aws` CLI absent, no credentials); we must not subscribe/launch without authorisation |
| Core workload executed through COOL on Arm | **BLOCKED / NOT VERIFIED** |
| Remote runner + ABBA benchmark script | IMPLEMENTED, NOT VERIFIED (never executed against a real host; `remote.py` + `scripts/remote_bench.sh`) |
| Cost / cleanup | documented in `docs/deployment.md`; no resources were created |

## Tests (executed 2026-10-14)
`python -m pytest -q` → 30 passed. Skipped/blocked: all cloud integration tests (no environment).

## Highest-impact unfinished task
Run `scripts/run_agent_loop.py` outputs on a human-launched COOL Graviton instance and record the baseline-vs-COOL table.
