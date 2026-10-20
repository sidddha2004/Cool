"""Controlled local benchmark (runs the real scan() in the isolated worker) and result comparison."""
from __future__ import annotations

import json
import os
import subprocess
import sys

from . import experiments, paths, runtime
from . import runner

MAX_CORNER_DELTA_PX = 0.5   # bit-level float differences between builds are expected; geometry must agree
MAX_REPEATS = 200
MAX_TIMEOUT_S = 900


def run_benchmark(candidate: str, corpus: str, warmup: int = 3, repeats: int = 30, threads: int | None = None,
                  case_ids: list[str] | None = None, label: str = "bench", timeout_s: int = 600,
                  trace_id: str | None = None) -> dict:
    paths.ensure_dirs()
    cand = paths.resolve_inside(candidate, paths.CANDIDATES)
    corp = paths.resolve_inside(corpus, paths.CORPORA)
    if not (1 <= repeats <= MAX_REPEATS and 0 <= warmup <= 50):
        raise ValueError(f"repeats must be 1..{MAX_REPEATS}, warmup 0..50")
    cmd = [sys.executable, "-m", "coolguard.worker", "--mode", "bench", "--candidate", str(cand), "--corpus", str(corp),
           "--out", str(paths.EXPERIMENTS), "--warmup", str(warmup), "--repeats", str(repeats)]
    if threads:
        cmd += ["--threads", str(int(threads))]
    if case_ids:
        cmd += ["--cases", ",".join(case_ids)]
    b = runner.run_worker(cmd, min(timeout_s, MAX_TIMEOUT_S))
    rec = {"experiment_id": experiments.new_id(label), "kind": "benchmark", "trace_id": trace_id,
           "code_revision": b["candidate_sha256"], "candidate": str(cand.relative_to(paths.ROOT)),
           "dataset_id": corp.name, "configuration_hash": experiments.config_hash(b["config"]),
           "runtime": runtime.probe(), "command": " ".join(cmd), "environment": "local-developer-workstation",
           "workload": {k: b[k] for k in ("n_images", "warmup", "repeats", "threads", "config")},
           "measurements": {"latency_ms": b["latency_ms"], "throughput_img_per_s": b["throughput_img_per_s"],
                            "cpu_percent_of_one_core": b["cpu_percent_of_one_core"], "peak_memory_mb": b["peak_memory_mb"],
                            "raw_latency_ms": b["raw_latency_ms"], "clock": b["clock"]},
           "output_checksum": b["output_checksum"], "detected_corners": b["detected_corners"], "correctness": {"evaluated": True, **b["correctness"],
                                                                    "acceptance_passed": b["correctness"]["accepted"] == b["correctness"]["n"]},
           "execution": {"status": "completed"}}
    experiments.save(rec)
    return rec


def _max_corner_delta(a: dict, b: dict):
    ca, cb = a.get("detected_corners"), b.get("detected_corners")
    if not ca or not cb or len(ca) != len(cb):
        return None
    d = 0.0
    for x, y in zip(ca, cb):
        if (x is None) != (y is None):
            return float("inf")
        if x is not None:
            d = max(d, max(abs(p - q) for u, v in zip(x, y) for p, q in zip(u, v)))
    return d


def compare_benchmarks(a: dict, b: dict) -> dict:
    """Compare two benchmark records; refuses to attribute differences when conditions differ."""
    problems = []
    for k in ("n_images", "warmup", "repeats", "threads"):
        if a["workload"][k] != b["workload"][k]:
            problems.append(f"workload.{k} differs ({a['workload'][k]} vs {b['workload'][k]})")
    if a["dataset_id"] != b["dataset_id"]:
        problems.append("different datasets")
    delta = _max_corner_delta(a, b)
    if delta is None or delta > MAX_CORNER_DELTA_PX:
        problems.append(f"outputs differ (max corner delta {delta} px > {MAX_CORNER_DELTA_PX}): not like-for-like; see correctness")
    ra, rb = a["runtime"], b["runtime"]
    if ra["architecture"] != rb["architecture"] or a.get("environment") != b.get("environment"):
        problems.append("different architecture/environment: differences are not attributable to the library alone")
    ma, mb = a["measurements"], b["measurements"]
    med = (ma["latency_ms"]["median"], mb["latency_ms"]["median"])
    return {"a": a["experiment_id"], "b": b["experiment_id"], "like_for_like": not problems, "caveats": problems,
            "median_ms": {"a": med[0], "b": med[1], "b_over_a": med[1] / med[0]},
            "p95_ms": {"a": ma["latency_ms"]["p95"], "b": mb["latency_ms"]["p95"]},
            "throughput": {"a": ma["throughput_img_per_s"], "b": mb["throughput_img_per_s"]},
            "correctness": {"a": a["correctness"], "b": b["correctness"]}}
