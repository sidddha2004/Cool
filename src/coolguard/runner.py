"""Runs the worker in a subprocess with a timeout; builds structured experiment records.

Process separation + timeout + env allow-list is NOT a sandbox: candidate code runs as the current OS user
and is treated as trusted-but-buggy code (see docs/security.md).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

from . import experiments, paths, runtime

DEFAULT_TIMEOUT_S = 120
MAX_TIMEOUT_S = 600


class InfrastructureError(RuntimeError):
    """Worker could not run (timeout, crash, bad candidate import). Distinct from a failing experiment."""


def safe_env() -> dict:
    """Allow-list environment for candidate code (a deny-list leaks unknown secrets). NOT a sandbox."""
    keep = ("PATH", "SYSTEMROOT", "SYSTEMDRIVE", "TEMP", "TMP", "HOME", "USERPROFILE", "LANG", "LC_ALL")
    env = {k: v for k, v in os.environ.items() if k.upper() in keep or k.startswith("COOLGUARD_")}
    env["PYTHONPATH"] = str(paths.ROOT / "src")
    env["OPENCV_IO_MAX_IMAGE_PIXELS"] = str(16_000_000)
    return env


def run_worker(cmd: list, timeout_s: int) -> dict:
    """Run the worker; its JSON report goes to a file (not stdout, which candidate code can write to)."""
    with tempfile.TemporaryDirectory() as td:
        rpt = Path(td) / "report.json"
        try:
            p = subprocess.run(cmd + ["--report", str(rpt)], capture_output=True, text=True, timeout=timeout_s,
                               env=safe_env(), cwd=str(paths.ROOT))
        except subprocess.TimeoutExpired:
            raise InfrastructureError(f"worker exceeded timeout of {timeout_s}s (killed)")
        if p.returncode != 0 or not rpt.exists():
            raise InfrastructureError(f"worker exited {p.returncode}: [untrusted worker stderr] {p.stderr[-400:]}")
        if rpt.stat().st_size > 50_000_000:
            raise InfrastructureError("worker report too large")
        return json.loads(rpt.read_text())


def summarize(results: list[dict]) -> dict:
    by = defaultdict(lambda: [0, 0])
    for r in results:
        by[r["category"]][0] += 1
        by[r["category"]][1] += int(bool(r.get("accepted")))
    n = len(results)
    ok = sum(int(bool(r.get("accepted"))) for r in results)
    reasons = defaultdict(int)
    for r in results:
        for fr in r.get("failure_reasons", []):
            reasons[fr] += 1
    return {"n": n, "passed": ok, "pass_rate": ok / n if n else None,
            "by_category": {k: {"n": v[0], "passed": v[1], "pass_rate": v[1] / v[0]} for k, v in sorted(by.items())},
            "failure_reasons": dict(reasons),
            "failed_case_ids": [r["case_id"] for r in results if not r.get("accepted")]}


def run_suite(candidate, corpus, label="suite", case_ids=None, config=None, timeout_s=DEFAULT_TIMEOUT_S,
              trace_id=None, save_stages="failures") -> dict:
    paths.ensure_dirs()
    cand = paths.resolve_inside(candidate, paths.CANDIDATES)
    corp = paths.resolve_inside(corpus, paths.CORPORA)
    timeout_s = max(1, min(int(timeout_s), MAX_TIMEOUT_S))
    eid = experiments.new_id(label)
    out = paths.EXPERIMENTS / f"{eid}.artifacts"
    cmd = [sys.executable, "-m", "coolguard.worker", "--candidate", str(cand), "--corpus", str(corp),
           "--out", str(out), "--config", json.dumps(config or {}), "--save-stages", save_stages]
    if case_ids:
        cmd += ["--cases", ",".join(case_ids)]
    rep = run_worker(cmd, timeout_s)
    rec = {
        "experiment_id": eid, "kind": "visual_regression", "trace_id": trace_id,
        "code_revision": rep["candidate_sha256"], "candidate": str(cand.relative_to(paths.ROOT)),
        "dataset_id": json.loads((corp / "manifest.json").read_text())["generator_version"] + ":" + corp.name,
        "configuration_hash": experiments.config_hash(rep["config"]), "configuration": rep["config"],
        "runtime": runtime.probe(),
        "command": " ".join(cmd),
        "results": rep["results"], "summary": summarize(rep["results"]),
        "artifact_dir": str(out),
        "execution": {"status": "completed"},
    }
    rec["correctness"] = {"evaluated": True, "acceptance_passed": rec["summary"]["passed"] == rec["summary"]["n"],
                          "metrics": {"pass_rate": rec["summary"]["pass_rate"]}}
    lat = sorted(r["latency_ms"] for r in rep["results"] if "latency_ms" in r)
    rec["measurements"] = {"latency_ms_median": lat[len(lat) // 2] if lat else None,
                           "note": "single-pass latency; use benchmark for steady state"}
    experiments.save(rec)
    return rec
