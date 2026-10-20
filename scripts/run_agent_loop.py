"""End-to-end evidence-driven debugging loop (real execution; nothing is scripted to succeed).

What is automatic: every measurement, every policy decision (controller.decide), every verdict.
What is NOT automatic: authoring candidates. candidates/scanner_v2..v7.py were written by the coding assistant
(Claude Code) in response to the evidence printed by the previous step; this script replays their verification
in order. If a verdict is REJECT/PARTIAL the script moves to the next candidate; it stops at ACCEPT (preserved
for human review) or when the policy's limits are hit. Output: artifacts/traces/<trace_id>.jsonl + report.

Usage: python scripts/run_agent_loop.py [--fresh]
"""
from __future__ import annotations

import json
import shutil
import sys
import time

from coolguard import controller, experiments, paths, tools

CANDIDATE_QUEUE = [f"candidates/scanner_v{i}.py" for i in range(2, 8)]
BASELINE = "candidates/scanner_v1.py"
REQUIRED = ["dev", "targeted-shadow", "heldout"]       # regression suite; 'final' is reserved for the last check


def say(msg: str) -> None:
    print(msg, flush=True)


def must(res: dict) -> dict:
    if not res.get("ok", True):
        raise SystemExit(f"tool failed: {json.dumps(res['error'])}")
    return res


def main() -> int:
    if "--fresh" in sys.argv:
        for d in (paths.EXPERIMENTS, paths.TRACES, paths.FAILURES):
            shutil.rmtree(d, ignore_errors=True)
    paths.ensure_dirs()
    trace = experiments.new_id("loop")
    experiments.trace(trace, "start", note="evidence-driven loop; candidates authored by the coding assistant", baseline=BASELINE)
    state = controller.LoopState(trace_id=trace, started=time.time())

    env = must(tools.inspect_vision_environment())["environment"]
    experiments.trace(trace, "environment_inspected", opencv=env["opencv_version"], arch=env["architecture"],
                      cool_verified=env["cool"]["verified"], module=env["opencv_module_path"])
    say(f"[env] OpenCV {env['opencv_version']} on {env['architecture']}, COOL verified: {env['cool']['verified']}")

    must(tools.generate_visual_test_cases("dev", seeds=[0, 1, 2, 3]))
    must(tools.generate_visual_test_cases("heldout", seeds=list(range(100, 106))))
    must(tools.generate_visual_test_cases("final", seeds=list(range(200, 206))))

    # 1. baseline workload
    base = must(tools.run_visual_regression_suite(BASELINE, "artifacts/corpora/dev", trace_id=trace))
    say(f"[baseline v1/dev] {base['passed']}/{base['n']}  weakest: "
        f"{sorted(base['by_category'].items(), key=lambda kv: kv[1])[:3]}")
    baselines = {"dev": base["experiment_id"]}

    # 2. evidence -> next action (policy), repeated until the policy asks for the coding assistant's change
    exp_id, n_decisions = base["experiment_id"], 0
    repro_corpus, repro_baseline = "artifacts/corpora/dev", base
    while True:
        an = must(tools.analyze_visual_failures(exp_id, trace))
        dec = an["next_action"]
        n_decisions += 1
        ev = dec["evidence"]
        say(f"[decision {n_decisions}] {dec['action']} | evidence: {ev.get('category')} pass={ev.get('pass_rate')} "
            f"mode={ev.get('dominant_mode')} area_ratio={ev.get('median_area_ratio')}\n    why: {dec['rationale']}")
        if dec["action"] == "generate_targeted_cases":
            a = dec["args"]
            gen = must(tools.generate_visual_test_cases(f"targeted-{a['categories'][0]}", a["categories"], a["seeds"]))
            r = must(tools.run_visual_regression_suite(BASELINE, gen["corpus"], trace_id=trace))
            say(f"    executed: {gen['n_cases']} targeted cases; v1 passes {r['passed']}/{r['n']} -> "
                f"{'failure generalises' if r['passed'] < r['n'] else 'failure NOT reproduced on fresh seeds'}")
            baselines[f"targeted-{a['categories'][0]}"] = r["experiment_id"]
            experiments.trace(trace, "targeted_result", corpus=gen["corpus"], experiment_id=r["experiment_id"],
                              passed=r["passed"], n=r["n"], confirms=r["passed"] < r["n"])
            exp_id = r["experiment_id"]
            repro_corpus, repro_baseline = gen["corpus"], r
            if r["passed"] == r["n"]:
                say("    policy would stop: failure did not generalise"); return 1
            continue
        if dec["action"] in ("inspect_stage_then_propose_change", "inspect_stage"):
            ids = repro_baseline["failed_case_ids"]
            cid = next((c for c in dec["args"].get("cases", []) if c in ids), ids[0])
            rep = must(tools.reproduce_visual_failure(BASELINE, repro_corpus, cid, repro_baseline["experiment_id"]))
            say(f"    executed: failure bundle {rep['bundle_dir']} (reproduced={rep['reproduced_failure']}, deterministic={rep['deterministic']})")
            experiments.trace(trace, "failure_reproduced", bundle=rep["bundle_dir"], reproduced=rep["reproduced_failure"],
                              deterministic=rep["deterministic"], inspect_stage=dec["args"].get("stage"))
            break
        say(f"    policy returned {dec['action']}; stopping"); return 1

    # required baselines for every regression corpus
    for c in REQUIRED:
        if c not in baselines:
            baselines[c] = must(tools.run_visual_regression_suite(BASELINE, f"artifacts/corpora/{c}", trace_id=trace))["experiment_id"]
    say("[baselines] " + ", ".join(f"{k}={v}" for k, v in baselines.items()))

    # 3. candidates (authored by the coding assistant) are verified; verdicts drive what happens next
    accepted = None
    for cand in CANDIDATE_QUEUE:
        if state.iteration >= controller.MAX_ITERATIONS + 2:
            say("iteration limit reached; human approval required"); break
        extras = [c for c in REQUIRED[1:]]
        v = must(tools.verify_candidate_fix(cand, baselines["dev"], "artifacts/corpora/dev",
                                            [f"artifacts/corpora/{c}" for c in extras], [baselines[c] for c in extras], trace))
        nxt = v["next_action"]
        controller.log_decision(state, nxt, v["experiments"][0])
        pc = ", ".join(f"{x['corpus']} {x['passed']}/{x['n']}" for x in v["per_corpus"])
        say(f"[verify {cand.split('/')[-1]}] {v['verdict']}  ({pc})  regressions={len(v['regressions'])} "
            f"cats={v['evidence']['regressed_categories']}\n    next: {nxt['action']} - {nxt['rationale']}")
        if v["verdict"] == "ACCEPT":
            accepted = cand
            break

    if not accepted:
        say("no candidate accepted; preserve evidence and hand back to the developer"); return 1

    # 4. final check on the corpus never used while iterating
    fin_base = must(tools.run_visual_regression_suite(BASELINE, "artifacts/corpora/final", trace_id=trace))
    fin = must(tools.run_visual_regression_suite(accepted, "artifacts/corpora/final", trace_id=trace))
    cmp_ = must(tools.compare_implementations(fin_base["experiment_id"], fin["experiment_id"]))
    say(f"[final corpus, unseen during iteration] baseline {fin_base['passed']}/{fin_base['n']} -> {accepted.split('/')[-1]} "
        f"{fin['passed']}/{fin['n']}; fixed={len(cmp_['fixed'])} regressions={len(cmp_['regressions'])}")
    experiments.trace(trace, "final_check", baseline=fin_base["experiment_id"], candidate=fin["experiment_id"],
                      passed=fin["passed"], n=fin["n"], regressions=cmp_["regressions"], fixed=len(cmp_["fixed"]),
                      human_review_required=True)

    # 5. local benchmark (like-for-like: same corpus, params, machine)
    b1 = must(tools.benchmark_vision_pipeline(BASELINE, "artifacts/corpora/final", repeats=10, trace_id=trace))
    b2 = must(tools.benchmark_vision_pipeline(accepted, "artifacts/corpora/final", repeats=10, trace_id=trace))
    cb = must(tools.compare_implementations(b1["experiment_id"], b2["experiment_id"]))
    say(f"[local bench] v1 median {cb['median_ms']['a']:.2f} ms vs {accepted.split('/')[-1]} {cb['median_ms']['b']:.2f} ms "
        f"(ratio {cb['median_ms']['b_over_a']:.2f}); like_for_like={cb['like_for_like']} caveats={cb['caveats']}")
    experiments.trace(trace, "local_benchmark", a=b1["experiment_id"], b=b2["experiment_id"], comparison=cb)

    remote = tools.run_cool_graviton_benchmark(accepted, "artifacts/corpora/final")
    say(f"[cool/graviton] status={remote.get('status')} verified_on_graviton={remote.get('verified_on_graviton')} "
        f"reason={remote.get('reason')}")
    experiments.trace(trace, "remote_benchmark", **{k: remote.get(k) for k in ("status", "reason", "needs", "verified_on_graviton")})

    say(f"\nTRACE: artifacts/traces/{trace}.jsonl\nCandidate preserved for HUMAN REVIEW (nothing committed or deployed): {accepted}")
    (paths.ARTIFACTS / "last_trace_id.txt").write_text(trace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
