# COOLGuard

Evidence-driven visual debugging for AI-generated OpenCV 5 code, delivered as an MCP server for Claude Code.

AI assistants write computer-vision code quickly, and visual defects survive ordinary tests. COOLGuard runs the
real pipeline on a deterministic corpus with **independent ground truth**, reports *where* it fails, picks the
next investigation **from the measured evidence**, gates candidate fixes on **regression protection**, and (when a
COOL Graviton instance is provided) benchmarks baseline vs COOL on Arm.

> **Status (checked 2026-10-14).** Local workflow: implemented and tested. **COOL on AWS Graviton: NOT verified** -
> no AWS access or Marketplace subscription exists in this workspace; the tool returns `BLOCKED`. See
> [docs/status.md](docs/status.md) for the full verified / unverified table.

## What it does (demonstrated run)

`python scripts/run_agent_loop.py --fresh` (output saved in `artifacts/last_loop_output.txt`):

| step | evidence → action |
|---|---|
| baseline scanner v1 on `dev` | 99/112; weakest `shadow` 42% (under-detection, ~62-67% of true page area) |
| policy | confirm on fresh seeds → v1 passes only 5/12 (failure generalises) |
| policy | inspect threshold stage → failure bundle saved & reproduced deterministically |
| candidate v2 (edge-based) | **REJECT** - fixes shadow but regresses 27 baseline-passing blur/noise cases |
| candidate v3 | **REJECT** - 48 regressions |
| candidates v4-v6 | **PARTIAL** - no regressions, failures remain (each step motivated by the previous failures) |
| candidate v7 | **ACCEPT** → preserved for human review |
| unseen `final` corpus | v1 151/168 → v7 168/168, 0 regressions |
| local benchmark | v7 is ~4x slower than v1 per image (correctness costs latency); outputs differ so it is flagged *not like-for-like* |
| COOL/Graviton | `BLOCKED` - no remote configured |

Candidates v2-v7 are written by the coding assistant between steps; the *policy* (`controller.py`) selects actions and
verdicts are computed, not scripted. The trace is `artifacts/traces/<id>.jsonl`; `scripts/make_report.py` renders
`artifacts/report/index.html`.

## Install

Python 3.10-3.13 (tested on 3.13, Windows x86-64; Linux/Arm is untested locally).

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"      # Linux/macOS: .venv/bin/python
```

Pinned: `opencv-python-headless==5.0.0.93`, `mcp>=2.3,<3` (the 2.x SDK renamed `FastMCP` → `MCPServer`).

## Claude Code configuration

`.mcp.json` (included) registers a stdio server. Project-scoped servers need your approval: run `claude` in this
directory and approve `coolguard` (or `claude mcp list` shows it as *Pending approval*). On Linux/macOS change the command
to `.venv/bin/python`. The server was verified with the official MCP client over stdio (`tests/test_mcp.py`); we have **not**
recorded an interactive Claude Code session invoking it.

Tools: `inspect_vision_environment`, `analyze_vision_pipeline`, `generate_visual_test_cases`,
`run_visual_regression_suite`, `analyze_visual_failures`, `reproduce_visual_failure`, `benchmark_vision_pipeline`,
`run_cool_graviton_benchmark`, `compare_implementations`, `verify_candidate_fix`. Pass one `trace_id` through a loop.

## Quick start

```bash
export PYTHONPATH=src
python -m coolguard.cli env
python -m coolguard.cli gen dev --seeds 0,1,2,3
python -m coolguard.cli run --candidate candidates/scanner_v1.py --corpus artifacts/corpora/dev
python -m coolguard.cli analyze <experiment_id>
python scripts/run_agent_loop.py --fresh && python scripts/make_report.py
python -m pytest -q          # 30 tests
```

## Remote COOL benchmark (needs a human-launched instance)

See [docs/deployment.md](docs/deployment.md). Without `config/remote.json` the tool returns `status: BLOCKED` and no numbers.

## Limitations

Synthetic data only; one page per frame; no real-photo validation; `dev` and `heldout` corpora were used while developing
candidates (only `final` was untouched); candidate code is executed as trusted code (not sandboxed). Details:
[docs/evaluation.md](docs/evaluation.md), [docs/security.md](docs/security.md).
