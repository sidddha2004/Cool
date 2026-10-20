# Architecture (only implemented components are drawn as solid)

```
 Developer ── Claude Code ──(MCP stdio)──► coolguard.mcp_server ──► tools.py (structured errors)
                 │  edits candidates/*.py                              │
                 ▼                                                     ├─ synthetic.py     corpus + ground truth
        candidates/scanner_vN.py                                       ├─ runner.py        subprocess worker (timeout, env allow-list)
                 ▲                                                     │     └─ worker.py  runs scan() -> metrics.py (independent scoring)
                 │ trusted code (NOT sandboxed)                        ├─ failure_analysis.py  patterns from results + stage images
                                                                       ├─ controller.py    deterministic next-action policy + limits
                                                                       ├─ verify.py        ACCEPT / PARTIAL / REJECT, repro bundles
                                                                       ├─ benchmark.py     local benchmark, like-for-like compare
                                                                       └─ remote.py  ·····► SSH ····► [Graviton + COOL AMI]  (NOT VERIFIED:
                                                                                              human-launched; no instance exists)
 artifacts/: corpora/ experiments/*.json traces/*.jsonl failures/ report/
```

Trust boundaries: (1) Claude Code ↔ MCP server (tool allow-list, path checks); (2) MCP server ↔ worker process (timeout,
env allow-list, report via file; *not* a sandbox); (3) workstation ↔ remote instance (fixed command set; candidate runs with
instance privileges).

## Agent decision flow (`controller.py`, evidence in every trace event)
```
run suite ─► analyze_visual_failures (per-category pass rate, failure mode: under/over-detection/misaligned/none/exception,
                │                     area ratio, stage coverage)
                ▼
          decide(): 0 failures ─────────► benchmark_and_report
                    worst category not yet confirmed ─► generate_targeted_cases (fresh seeds 300+)
                    under_detection ─► inspect threshold stage;  over_detection ─► inspect edges stage;
                    no_detection ─► inspect gray stage;  exception ─► fix candidate;  limits hit ─► stop_for_human
                ▼
   coding assistant edits a candidate ─► verify_candidate_fix on dev + targeted + heldout, each vs its own baseline
                ▼
   REJECT (any regression/exception) ─► revise using regressed categories   PARTIAL ─► revise on unresolved cases
   ACCEPT ─► preserve_for_review (requires_human=True)
```
Limits: 6 iterations, 400 generated cases, 1800 s, 3 remote runs. The policy is deterministic; it never writes code.
Experiment record schema: `experiment_id, kind, code_revision (sha256), dataset_id, configuration_hash, runtime, command,
results, summary, correctness, measurements, execution` (see `runner.run_suite`).
