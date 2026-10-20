"""Candidate verification, experiment comparison and failure reproduction."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from . import experiments, paths, runner, synthetic


def _by_id(rec):
    return {r["case_id"]: r for r in rec["results"]}


def compare(a: dict, b: dict) -> dict:
    """Compare two saved visual-regression experiments (a = baseline, b = candidate)."""
    limits = []
    if a.get("dataset_id") != b.get("dataset_id"):
        limits.append(f"different datasets ({a.get('dataset_id')} vs {b.get('dataset_id')}): only overlapping case ids compared")
    ra, rb = a["runtime"], b["runtime"]
    comparable_perf = all(ra[k] == rb[k] for k in ("architecture", "opencv_version", "opencv_module_path", "platform"))
    if not comparable_perf:
        limits.append("runtimes differ (arch/OpenCV build/platform): latency differences are NOT attributable to the code change")
    A, B = _by_id(a), _by_id(b)
    common = sorted(set(A) & set(B))
    if not common:
        return {"comparable": False, "reason": "no overlapping case ids", "limitations": limits}
    fixed = [c for c in common if not A[c].get("accepted") and B[c].get("accepted")]
    regress = [c for c in common if A[c].get("accepted") and not B[c].get("accepted")]
    still = [c for c in common if not A[c].get("accepted") and not B[c].get("accepted")]
    cats: dict = {}
    for c in common:
        d = cats.setdefault(A[c]["category"], {"baseline": 0, "candidate": 0, "n": 0})
        d["n"] += 1
        d["baseline"] += int(bool(A[c].get("accepted")))
        d["candidate"] += int(bool(B[c].get("accepted")))
    la = sorted(A[c]["latency_ms"] for c in common if "latency_ms" in A[c])
    lb = sorted(B[c]["latency_ms"] for c in common if "latency_ms" in B[c])
    perf = {"baseline_median_ms": la[len(la) // 2] if la else None,
            "candidate_median_ms": lb[len(lb) // 2] if lb else None,
            "caveat": "single-pass latency including first-call effects; use benchmark_vision_pipeline for steady state",
            "attributable": comparable_perf}
    return {"comparable": True, "n_common": len(common), "fixed": fixed, "regressions": regress,
            "still_failing": still, "by_category": cats, "performance": perf, "limitations": limits,
            "baseline": a["experiment_id"], "candidate": b["experiment_id"]}


def verify_candidate(candidate: str, baseline_experiment_id: str, corpus: str, trace_id: str | None = None,
                     extra_corpora: list[str] | None = None, extra_baselines: list[str] | None = None,
                     timeout_s: int = 120) -> dict:
    """Run the candidate over the primary corpus AND every extra corpus, comparing each against its baseline run.

    ACCEPT  : zero regressions on every corpus, every case passes, no exceptions.
    PARTIAL : zero regressions, but some cases still fail.
    REJECT  : any regression vs the baseline, any exception, or an infrastructure failure (never reported as success).
    Each extra corpus needs a baseline experiment (extra_baselines aligned with extra_corpora)."""
    extra_corpora = list(extra_corpora or [])
    extra_baselines = list(extra_baselines or [])
    if len(extra_corpora) != len(extra_baselines):
        raise ValueError("extra_baselines must be aligned with extra_corpora (one baseline experiment per corpus)")
    pairs = [(corpus, baseline_experiment_id)] + list(zip(extra_corpora, extra_baselines))
    recs, cmps = [], []
    try:
        for c, b in pairs:
            rec = runner.run_suite(candidate, c, label="verify", trace_id=trace_id, timeout_s=timeout_s)
            recs.append(rec)
            cmps.append(compare(experiments.load(b), rec))
    except runner.InfrastructureError as e:
        return {"verdict": "REJECT", "acceptance_passed": False, "infrastructure_error": str(e), "regressions": [],
                "unresolved_cases": [], "evidence": {"error": str(e)}, "experiments": [r["experiment_id"] for r in recs]}
    exceptions = [r["case_id"] for rec in recs for r in rec["results"] if r.get("status") == "candidate_exception"]
    regress = [c for cm in cmps if cm["comparable"] for c in cm["regressions"]]
    unresolved = [r["case_id"] for rec in recs for r in rec["results"] if not r.get("accepted")]
    fixed = [c for cm in cmps if cm["comparable"] for c in cm["fixed"]]
    if regress or exceptions or not all(cm["comparable"] for cm in cmps):
        verdict = "REJECT"
    elif unresolved:
        verdict = "PARTIAL"
    else:
        verdict = "ACCEPT"
    per_corpus = [{"corpus": Path(c).name, "baseline": b, "candidate_experiment": r["experiment_id"],
                   "pass_rate_baseline": experiments.load(b)["summary"]["pass_rate"],
                   "pass_rate_candidate": r["summary"]["pass_rate"], "passed": r["summary"]["passed"], "n": r["summary"]["n"]}
                  for (c, b), r in zip(pairs, recs)]
    out = {"verdict": verdict, "acceptance_passed": verdict == "ACCEPT", "regressions": regress,
           "exceptions": exceptions, "unresolved_cases": unresolved, "fixed_cases": fixed,
           "comparison": cmps[0], "per_corpus": per_corpus, "experiments": [r["experiment_id"] for r in recs],
           "evidence": {"n_fixed": len(fixed), "n_regressed": len(regress),
                        "regressed_categories": sorted({c.split("-")[0] for c in regress}),
                        "n_unresolved": len(unresolved), "per_corpus": per_corpus}}
    if trace_id:
        experiments.trace(trace_id, "candidate_verified", candidate=candidate, baseline=baseline_experiment_id,
                          experiments=out["experiments"], verdict=verdict, evidence=out["evidence"])
    return out


def reproduce_failure(candidate: str, corpus: str, case_id: str, experiment_id: str | None = None) -> dict:
    """Save a self-contained failure bundle and confirm that re-running reproduces the same failure."""
    corp = paths.resolve_inside(corpus, paths.CORPORA)
    man = json.loads((corp / "manifest.json").read_text())
    spec = next((c for c in man["cases"] if c["case_id"] == case_id), None)
    if spec is None:
        raise ValueError(f"case {case_id!r} not in corpus {corp.name}")
    r1 = runner.run_suite(candidate, corp, label="repro1", case_ids=[case_id], save_stages="all")
    r2 = runner.run_suite(candidate, corp, label="repro2", case_ids=[case_id], save_stages="none")
    a, b = r1["results"][0], r2["results"][0]
    fails = not a.get("accepted")
    same = (a.get("detected_corners") == b.get("detected_corners")) and (a.get("accepted") == b.get("accepted"))
    dst = paths.FAILURES / f"{case_id}-{r1['experiment_id']}"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy(corp / spec["image"], dst / "input.png")
    shutil.copy(corp / spec["page"], dst / "ground_truth_flat_page.png")
    art = Path(r1["artifact_dir"]) / "stages" / case_id
    if art.exists():
        shutil.copytree(art, dst / "stages", dirs_exist_ok=True)
    bundle = {"case": spec, "expected": {"corners": spec["corners"], "criteria": "see coolguard.metrics"},
              "actual": {k: a.get(k) for k in ("detected_corners", "iou", "corner_err", "ncc", "failure_reasons", "accepted")},
              "candidate": r1["candidate"], "candidate_sha256": r1["code_revision"], "runtime": r1["runtime"],
              "source_experiment": experiment_id, "repro_experiments": [r1["experiment_id"], r2["experiment_id"]],
              "reproduce_command": f"python -m coolguard.cli run --candidate {r1['candidate']} --corpus {corp} --cases {case_id}",
              "reproduced_failure": fails, "deterministic_across_two_runs": same}
    (dst / "failure.json").write_text(json.dumps(bundle, indent=1))
    return {"bundle_dir": str(dst), "reproduced_failure": fails, "deterministic": same, "actual": bundle["actual"]}


def severity_sweep(candidate: str, category: str, seed: int, params: list[float]) -> dict:
    """Locate where a category starts to fail by running one batch over explicit severity values.

    Reports pass/fail per parameter at the supplied grid resolution. This is a failure-ONSET estimate,
    not a formally minimal failing case."""
    out_dir = paths.CORPORA / f"sweep-{category}-s{seed}"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    synthetic.generate_corpus(out_dir, categories=[category], seeds=[seed], params=params)
    rec = runner.run_suite(candidate, out_dir, label="sweep")
    rows = sorted((float(r["case_id"].split("-P")[1].split("-s")[0]), bool(r.get("accepted")), r.get("iou"))
                  for r in rec["results"])
    return {"experiment_id": rec["experiment_id"], "category": category, "seed": seed,
            "points": [{"param": p, "accepted": ok, "iou": i} for p, ok, i in rows],
            "note": "onset resolution limited to the supplied grid; see synthetic.CATEGORIES for severity direction"}
