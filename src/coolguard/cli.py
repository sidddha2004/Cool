"""Command-line interface over the same tool functions the MCP server exposes."""
from __future__ import annotations

import argparse
import json
import sys

from . import runtime, tools


def _print(obj) -> int:
    print(json.dumps(obj, indent=1, default=str))
    return 0 if not isinstance(obj, dict) or obj.get("ok", True) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="coolguard")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe", help="print runtime probe JSON (used on remote hosts)")
    sub.add_parser("env")
    p = sub.add_parser("gen"); p.add_argument("name"); p.add_argument("--categories", default=""); p.add_argument("--seeds", default="0,1,2,3")
    p = sub.add_parser("run"); p.add_argument("--candidate", required=True); p.add_argument("--corpus", required=True)
    p.add_argument("--cases", default=""); p.add_argument("--trace", default=None)
    p = sub.add_parser("analyze"); p.add_argument("experiment"); p.add_argument("--trace", default=None)
    p = sub.add_parser("verify"); p.add_argument("--candidate", required=True); p.add_argument("--baseline", required=True)
    p.add_argument("--corpus", required=True); p.add_argument("--extra", default=""); p.add_argument("--extra-baselines", default=""); p.add_argument("--trace", default=None)
    p = sub.add_parser("bench"); p.add_argument("--candidate", required=True); p.add_argument("--corpus", required=True)
    p.add_argument("--repeats", type=int, default=30); p.add_argument("--threads", type=int, default=None)
    p = sub.add_parser("compare"); p.add_argument("a"); p.add_argument("b")
    p = sub.add_parser("repro"); p.add_argument("--candidate", required=True); p.add_argument("--corpus", required=True)
    p.add_argument("--case", required=True)
    p = sub.add_parser("remote"); p.add_argument("--candidate", required=True); p.add_argument("--corpus", required=True)
    p.add_argument("--repeats", type=int, default=30); p.add_argument("--threads", type=int, default=4)
    a = ap.parse_args(argv)
    split = lambda s: [x for x in s.split(",") if x] or None
    if a.cmd == "probe":
        print(json.dumps(runtime.probe())); return 0
    if a.cmd == "env":
        return _print(tools.inspect_vision_environment())
    if a.cmd == "gen":
        return _print(tools.generate_visual_test_cases(a.name, split(a.categories), [int(x) for x in a.seeds.split(",")]))
    if a.cmd == "run":
        return _print(tools.run_visual_regression_suite(a.candidate, a.corpus, split(a.cases), trace_id=a.trace))
    if a.cmd == "analyze":
        return _print(tools.analyze_visual_failures(a.experiment, a.trace))
    if a.cmd == "verify":
        return _print(tools.verify_candidate_fix(a.candidate, a.baseline, a.corpus, split(a.extra), split(a.extra_baselines), a.trace))
    if a.cmd == "bench":
        return _print(tools.benchmark_vision_pipeline(a.candidate, a.corpus, repeats=a.repeats, threads=a.threads))
    if a.cmd == "compare":
        return _print(tools.compare_implementations(a.a, a.b))
    if a.cmd == "repro":
        return _print(tools.reproduce_visual_failure(a.candidate, a.corpus, a.case))
    if a.cmd == "remote":
        return _print(tools.run_cool_graviton_benchmark(a.candidate, a.corpus, a.repeats, a.threads))
    return 2


if __name__ == "__main__":
    sys.exit(main())
