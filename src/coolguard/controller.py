"""Transparent, deterministic next-action policy driven by measured evidence, plus bounded-loop limits.

`decide()` is a pure function of (analysis, state). Different measured failure signatures give different
actions; every decision carries the evidence it used so the trace is auditable. No LLM call is involved
in this policy: the coding assistant executes the actions and edits code.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from . import experiments

# Loop limits (human approval is required beyond these)
MAX_ITERATIONS = 6
MAX_GENERATED_CASES = 400
MAX_TOTAL_SECONDS = 1800
MAX_REMOTE_BENCHMARKS = 3        # billable runs per session without fresh human approval

STAGE_FOR_MODE = {"under_detection": "threshold", "over_detection": "edges", "misaligned": "closed"}


@dataclass
class LoopState:
    trace_id: str
    iteration: int = 0
    generated_cases: int = 0
    started: float = 0.0
    remote_runs: int = 0
    targeted: set = field(default_factory=set)       # categories already probed with fresh seeds


def _d(action, args, rationale, evidence, requires_human):
    return {"action": action, "args": args, "rationale": rationale, "evidence": evidence,
            "requires_human": requires_human}


def decide(analysis: dict, state: LoopState, now: float | None = None) -> dict:
    """Return {action, args, rationale, evidence, requires_human}. Logs nothing; caller traces it."""
    now = now if now is not None else time.time()
    if state.iteration >= MAX_ITERATIONS:
        return _d("stop_for_human", {}, f"iteration limit {MAX_ITERATIONS} reached", {"iteration": state.iteration}, True)
    if state.started and now - state.started > MAX_TOTAL_SECONDS:
        return _d("stop_for_human", {}, f"time limit {MAX_TOTAL_SECONDS}s exceeded", {}, True)
    if analysis["n_failed"] == 0:
        return _d("benchmark_and_report", {},
                  "no failing cases on the suite; correctness criteria met, proceed to held-out verification / "
                  "benchmarking", {"n_failed": 0}, False)

    worst = analysis["categories"][0]
    ev = {k: worst[k] for k in ("category", "pass_rate", "n_failed", "n", "dominant_mode", "median_area_ratio",
                                "median_threshold_page_coverage", "levels_failing")}
    # 1) confirm that the failure generalises before spending effort on it
    if worst["category"] not in state.targeted and state.generated_cases + 24 <= MAX_GENERATED_CASES:
        return _d("generate_targeted_cases",
                  {"categories": [worst["category"]], "seeds": [300, 301, 302, 303], "reason": "confirm"},
                  f"'{worst['category']}' has the lowest pass rate ({worst['pass_rate']:.0%}); confirm on fresh seeds "
                  "before attributing the failure to the pipeline", ev, False)
    # 2) choose an investigation that depends on the measured failure signature
    mode = worst["dominant_mode"]
    if mode == "exception":
        return _d("fix_candidate_exception", {},
                  "candidate raised exceptions on these cases; see traceback in the case results", ev, False)
    if mode == "no_detection":
        return _d("inspect_stage", {"stage": "gray", "cases": worst["examples"]},
                  "pipeline returned no quad; inspect the earliest stage for blank/saturated output", ev, False)
    stage = STAGE_FOR_MODE.get(mode, "closed")
    if mode == "under_detection":
        why = (f"detected area is {worst['median_area_ratio']:.0%} of the true page; inspect the {stage} stage to see "
               "which page regions are lost, then change the binarisation/segmentation step")
    elif mode == "over_detection":
        why = (f"detected area is {worst['median_area_ratio']:.0%} of the true page (region leaks into background); "
               f"inspect the {stage} stage for structures joined to the page; consider noise-robust edge handling")
    else:
        why = "region has plausible area but misaligned corners; inspect corner refinement / approxPolyDP epsilon"
    return _d("inspect_stage_then_propose_change", {"stage": stage, "cases": worst["examples"], "mode": mode}, why, ev, False)


def decide_after_candidate(verification: dict) -> dict:
    """Post-verification decision: preserve for human review, revise (with evidence), or reject."""
    v = verification["verdict"]
    if v == "ACCEPT":
        return _d("preserve_for_review", {},
                  "no regressions and all target failures fixed; preserved for human review "
                  "(automated pass != production-ready)", verification["evidence"], True)
    if v == "PARTIAL":
        return _d("revise_candidate", {"unresolved": verification["unresolved_cases"][:5]},
                  "no regressions but target failures remain; investigate unresolved cases", verification["evidence"], False)
    return _d("reject_candidate", {"regressed": verification["regressions"][:5]},
              "candidate breaks cases that the baseline passed (or crashed); reject and revise using the regressed "
              "categories as evidence", verification["evidence"], False)


def log_decision(state: LoopState, decision: dict, based_on: str) -> dict:
    state.iteration += 1
    if decision["action"] == "generate_targeted_cases":
        state.targeted.update(decision["args"]["categories"])
        state.generated_cases += 24
    return experiments.trace(state.trace_id, "decision", based_on_experiment=based_on,
                             iteration=state.iteration, **decision)
