# Demo script (≤5 min, all live)

1. `python -m coolguard.cli env` - show OpenCV 5.0.0, architecture, `cool.verified: false` (honest local run).
2. In Claude Code (approve the `coolguard` MCP server first): ask "run COOLGuard on candidates/scanner_v1.py with a shadow-focused
   corpus and tell me what to investigate". Show tool calls `generate_visual_test_cases` → `run_visual_regression_suite` →
   `analyze_visual_failures`; read out the measured evidence (shadow pass rate, area ratio) and the chosen next action.
3. Open `artifacts/failures/<case>/stages/` - threshold stage shows the lost shadowed half of the page.
4. Show `verify_candidate_fix` on v2 → REJECT with named regressed categories; then on v7 → ACCEPT (requires human review).
5. `python scripts/run_agent_loop.py --fresh` (≈1 min) then open `artifacts/report/index.html` after `python scripts/make_report.py`.
6. `python -m coolguard.cli remote ...` → show `BLOCKED` (unless a COOL instance has been configured; then show the table).
Say out loud: synthetic data only; dev/heldout were used during development; COOL/Graviton not verified unless step 6 ran.
