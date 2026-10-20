"""Failure analysis from MEASURED results and saved intermediate stages.

Reports observed patterns and correlations. It deliberately does not assert root causes:
`hypotheses` are labelled as such and name the evidence that supports them.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from statistics import median

import cv2
import numpy as np

from . import metrics


def _area(q) -> float:
    return float(cv2.contourArea(np.asarray(q, np.float32)))


def _stage_coverage(artifact_dir: str | None, gt, shape) -> float | None:
    """Fraction of the ground-truth page polygon that is 'on' in the saved threshold/closed stage image."""
    if not artifact_dir:
        return None
    for name in ("threshold", "closed"):
        p = Path(artifact_dir) / f"{name}.png"
        if p.exists():
            st = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
            st = cv2.resize(st, (shape[1], shape[0]), interpolation=cv2.INTER_NEAREST)
            mask = np.zeros(shape[:2], np.uint8)
            cv2.fillConvexPoly(mask, np.asarray(gt, np.int32), 255)
            return float((st[mask > 0] > 0).mean()) if name == "threshold" else None
    return None


def analyze(record: dict, corpus_manifest: dict | None = None) -> dict:
    gt_by_id = {c["case_id"]: c for c in (corpus_manifest or {}).get("cases", [])}
    fails = [r for r in record["results"] if not r.get("accepted")]
    per_cat = defaultdict(list)
    for r in fails:
        c = gt_by_id.get(r["case_id"])
        sig = {"case_id": r["case_id"], "level": r["level"], "reasons": r.get("failure_reasons", []),
               "iou": r.get("iou"), "corner_err": r.get("corner_err")}
        if r.get("detected_corners") is not None and c:
            ratio = _area(r["detected_corners"]) / max(_area(c["corners"]), 1.0)
            sig["area_ratio"] = ratio
            sig["mode"] = "under_detection" if ratio < 0.85 else "over_detection" if ratio > 1.15 else "misaligned"
            sig["page_coverage_in_threshold_stage"] = _stage_coverage(r.get("artifact_dir"), c["corners"], (c["height"], c["width"]))
        elif r.get("status") == "candidate_exception":
            sig["mode"] = "exception"
        else:
            sig["mode"] = "no_detection"
        per_cat[r["category"]].append(sig)

    summ = record["summary"]["by_category"]
    categories = []
    for cat, sigs in per_cat.items():
        modes = defaultdict(int)
        for s in sigs:
            modes[s["mode"]] += 1
        dom = max(modes, key=modes.get)
        lv = sorted({s["level"] for s in sigs})
        cov = [s["page_coverage_in_threshold_stage"] for s in sigs if s.get("page_coverage_in_threshold_stage") is not None]
        ar = [s["area_ratio"] for s in sigs if "area_ratio" in s]
        categories.append({
            "category": cat, "n_failed": len(sigs), "n": summ[cat]["n"], "pass_rate": summ[cat]["pass_rate"],
            "levels_failing": lv, "dominant_mode": dom, "mode_counts": dict(modes),
            "median_area_ratio": median(ar) if ar else None,
            "median_threshold_page_coverage": median(cov) if cov else None,
            "median_iou": median([s["iou"] for s in sigs if s["iou"] is not None] or [0.0]),
            "examples": [s["case_id"] for s in sigs[:3]],
        })
    categories.sort(key=lambda c: (c["pass_rate"], -c["n_failed"]))
    hyps = []
    for c in categories:
        if c["dominant_mode"] == "under_detection" and (c["median_threshold_page_coverage"] or 1) < 0.85:
            hyps.append({"category": c["category"], "hypothesis": "binarisation stage loses part of the page "
                         "(only %.0f%% of the true page area is foreground in the threshold stage); suspect brightness-"
                         "dependent thresholding" % (100 * c["median_threshold_page_coverage"]),
                         "status": "unverified-hypothesis", "evidence": "threshold stage images + area ratio"})
        elif c["dominant_mode"] == "over_detection":
            hyps.append({"category": c["category"], "hypothesis": "detected region extends beyond the page "
                         "(median area ratio %.2f); suspect background/noise structures joined to the page" % c["median_area_ratio"],
                         "status": "unverified-hypothesis", "evidence": "area ratio"})
    return {"experiment_id": record["experiment_id"], "n_failed": len(fails), "categories": categories,
            "hypotheses": hyps,
            "note": "Patterns are measured correlations with the corpus generator's conditions, not proven root causes."}
