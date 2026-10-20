"""Vision execution worker. Runs a candidate scanner over a corpus in a SEPARATE PROCESS.

Entry point: python -m coolguard.worker --candidate X.py --corpus DIR --out DIR [--cases id,id] [--config JSON]
Prints one JSON document on stdout. The parent enforces the wall-clock timeout.
NOTE: process separation + timeout is NOT a security sandbox (see docs/security.md).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
import traceback
from pathlib import Path

import cv2
import numpy as np

from . import metrics


def load_candidate(path: Path):
    spec = importlib.util.spec_from_file_location("coolguard_candidate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not callable(getattr(mod, "scan", None)):
        raise AttributeError("candidate must define scan(img, config=None) -> {'corners':..., 'stages':{...}}")
    return mod


def run(candidate: Path, corpus: Path, out: Path, case_ids=None, config=None, save_stages="failures") -> dict:
    mod = load_candidate(candidate)
    cfg = {**getattr(mod, "DEFAULT_CONFIG", {}), **(config or {})}
    manifest = json.loads((corpus / "manifest.json").read_text())
    cases = [c for c in manifest["cases"] if not case_ids or c["case_id"] in case_ids]
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for c in cases:
        r = {"case_id": c["case_id"], "category": c["category"], "level": c["level"], "seed": c["seed"]}
        img = cv2.imread(str(corpus / c["image"]), cv2.IMREAD_COLOR)
        page = cv2.imread(str(corpus / c["page"]), cv2.IMREAD_COLOR)
        if img is None or page is None:
            r.update(status="infrastructure_error", error="could not load case images")
            results.append(r); continue
        t0 = time.perf_counter()
        try:
            res = mod.scan(img, cfg)
            dt = (time.perf_counter() - t0) * 1000
            det = None if res.get("corners") is None else np.asarray(res["corners"], np.float32)
            ev = metrics.evaluate_case(img, page, np.asarray(c["corners"], np.float32), det)
            r.update(status="ok", latency_ms=dt, detected_corners=None if det is None else det.tolist(), **ev)
            if save_stages == "all" or (save_stages == "failures" and not ev["accepted"]):
                d = out / "stages" / c["case_id"]; d.mkdir(parents=True, exist_ok=True)
                for name, im in res.get("stages", {}).items():
                    cv2.imwrite(str(d / f"{name}.png"), im)
                vis = img.copy()
                cv2.polylines(vis, [np.asarray(c["corners"], np.int32)], True, (0, 200, 0), 2)
                if det is not None:
                    cv2.polylines(vis, [det.astype(np.int32)], True, (0, 0, 255), 2)
                cv2.imwrite(str(d / "overlay_gt_green_det_red.png"), vis)
                r["artifact_dir"] = str(d)
        except Exception as e:  # candidate defect, reported as an experiment failure (not infra)
            r.update(status="candidate_exception", error=f"{type(e).__name__}: {e}",
                     traceback=traceback.format_exc(limit=3), accepted=False, failure_reasons=["exception"])
        results.append(r)
    return {"candidate": str(candidate), "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
            "config": cfg, "results": results}


def bench(candidate: Path, corpus: Path, case_ids=None, config=None, warmup=3, repeats=30, threads=None) -> dict:
    """Steady-state benchmark of the real scan() over corpus images. Raw per-run latencies are preserved."""
    import psutil
    mod = load_candidate(candidate)
    cfg = {**getattr(mod, "DEFAULT_CONFIG", {}), **(config or {})}
    if threads is not None:
        cv2.setNumThreads(int(threads))
    manifest = json.loads((corpus / "manifest.json").read_text())
    cases = [c for c in manifest["cases"] if not case_ids or c["case_id"] in case_ids]
    imgs = [(c, cv2.imread(str(corpus / c["image"]), cv2.IMREAD_COLOR), cv2.imread(str(corpus / c["page"]))) for c in cases]
    proc = psutil.Process()
    # untimed correctness pass (evaluation work must not pollute timing/CPU/throughput)
    acc, corners = 0, []
    for c, im, pg in imgs:
        res = mod.scan(im, cfg)
        det = None if res.get("corners") is None else np.asarray(res["corners"], np.float32)
        acc += int(metrics.evaluate_case(im, pg, np.asarray(c["corners"], np.float32), det)["accepted"])
        corners.append(None if det is None else np.round(det, 3).tolist())
    for i in range(warmup):                      # warm-up cycles through the images
        mod.scan(imgs[i % len(imgs)][1], cfg)
    raw = []
    peak = [proc.memory_info().rss]
    cpu0 = proc.cpu_times(); w0 = time.perf_counter()
    for rep in range(repeats):
        for c, im, pg in imgs:
            t0 = time.perf_counter_ns()
            mod.scan(im, cfg)
            raw.append((time.perf_counter_ns() - t0) / 1e6)
        peak.append(proc.memory_info().rss)
    wall = time.perf_counter() - w0; cpu1 = proc.cpu_times()
    srt = sorted(raw); n = len(srt)
    try:
        import resource                         # Linux/macOS: true process peak (KB on Linux)
        peak_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        peak_src = "ru_maxrss"
    except ImportError:                         # Windows: peak working set
        peak_mb = (getattr(proc.memory_info(), "peak_wset", None) or max(peak)) / 1e6
        peak_src = "peak_wset"
    return {"candidate": str(candidate), "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(), "config": cfg,
            "n_images": len(imgs), "warmup": warmup, "repeats": repeats, "threads": cv2.getNumThreads(),
            "latency_ms": {"median": srt[n // 2], "p95": srt[min(n - 1, int(0.95 * n))], "mean": sum(srt) / n,
                           "min": srt[0], "max": srt[-1]},
            "throughput_img_per_s": n / wall, "wall_s": wall,
            "cpu_percent_of_one_core": 100 * ((cpu1.user - cpu0.user) + (cpu1.system - cpu0.system)) / wall,
            "peak_memory_mb": peak_mb, "peak_memory_source": peak_src,
            "peak_memory_note": "whole worker process (Python+numpy+images), not OpenCV-only",
            "output_checksum": hashlib.sha256(json.dumps(corners).encode()).hexdigest()[:16], "detected_corners": corners,
            "correctness": {"accepted": acc, "n": len(imgs)}, "raw_latency_ms": raw,
            "clock": "time.perf_counter_ns (monotonic)"}


def _emit(a, obj):
    if a.report:
        Path(a.report).write_text(json.dumps(obj))
    else:
        sys.stdout.write(json.dumps(obj))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True); ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--cases", default="")
    ap.add_argument("--config", default="{}"); ap.add_argument("--save-stages", default="failures")
    ap.add_argument("--mode", default="suite"); ap.add_argument("--report", default=""); ap.add_argument("--warmup", type=int, default=3)
    ap.add_argument("--repeats", type=int, default=30); ap.add_argument("--threads", type=int, default=None)
    a = ap.parse_args(argv)
    cv2.setRNGSeed(0)
    ids = set(filter(None, a.cases.split(","))) or None
    if a.mode == "bench":
        _emit(a, bench(Path(a.candidate), Path(a.corpus), ids, json.loads(a.config), a.warmup, a.repeats, a.threads))
        return
    rep = run(Path(a.candidate), Path(a.corpus), Path(a.out), ids, json.loads(a.config), a.save_stages)
    _emit(a, rep)


if __name__ == "__main__":
    main()
