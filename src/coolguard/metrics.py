"""Independent evaluation: geometry metrics and acceptance criteria.

This module never imports a candidate scanner; candidates cannot define their own success.
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

# Acceptance criteria (task requirement: a scan is usable if the page can be rectified
# faithfully). Chosen from the task, NOT tuned to a candidate; see docs/evaluation.md.
IOU_MIN = 0.95            # page content displaced by at most ~2-3% of page size -> text stays legible
CORNER_ERR_MAX = 0.01     # mean corner error / image diagonal (~8 px on 640x480)
NCC_RATIO_MIN = 0.0       # DIAGNOSTIC ONLY (not gated): NCC(detected)/NCC(true corners). Text strokes are ~7px tall so
#                           it is too sensitive to ~2px corner error to be a fair gate even on clean images.
# (absolute NCC is NOT gated: with perfect corners it is only 0.53-0.77 on blur/shadow images, so it
#  would fail a perfect detector. Validated by tests/test_metrics.py::test_oracle_always_accepted.)


@dataclass(frozen=True)
class Acceptance:
    iou_min: float = IOU_MIN
    corner_err_max: float = CORNER_ERR_MAX
    ncc_ratio_min: float = NCC_RATIO_MIN


def order_quad(pts: np.ndarray) -> np.ndarray:
    """Order 4 points TL,TR,BR,BL by angle about centroid (robust for convex quads)."""
    pts = np.asarray(pts, np.float32).reshape(4, 2)
    c = pts.mean(0)
    ang = np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0])
    p = pts[np.argsort(ang)]            # clockwise starting from left-ish in image coords
    s = p.sum(1)
    start = int(np.argmin(s))           # TL has min x+y
    return np.roll(p, -start, axis=0)


def polygon_iou(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, np.float32).reshape(-1, 2)
    b = np.asarray(b, np.float32).reshape(-1, 2)
    inter, _ = cv2.intersectConvexConvex(a, b)
    ua = cv2.contourArea(a) + cv2.contourArea(b) - inter
    return float(inter / ua) if ua > 0 else 0.0


def corner_error(det: np.ndarray, gt: np.ndarray, diag: float) -> float:
    d, g = order_quad(det), order_quad(gt)
    return float(np.linalg.norm(d - g, axis=1).mean() / diag)


def rectification_ncc(scene: np.ndarray, det: np.ndarray, page: np.ndarray) -> float:
    """Warp the scene by the detected quad and correlate with the true flat page."""
    h, w = page.shape[:2]
    dst = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], np.float32)
    M = cv2.getPerspectiveTransform(order_quad(det), dst)
    rect = cv2.warpPerspective(scene, M, (w, h))
    a = cv2.cvtColor(rect, cv2.COLOR_BGR2GRAY).astype(np.float32)
    b = cv2.cvtColor(page, cv2.COLOR_BGR2GRAY).astype(np.float32)
    a -= a.mean(); b -= b.mean()
    den = float(np.sqrt((a * a).sum() * (b * b).sum()))
    return float((a * b).sum() / den) if den > 1e-6 else 0.0


def is_valid_quad(q) -> bool:
    if q is None:
        return False
    q = np.asarray(q, np.float32)
    return q.shape == (4, 2) and bool(np.isfinite(q).all()) and cv2.isContourConvex(order_quad(q).reshape(-1, 1, 2)) \
        and cv2.contourArea(q) > 1.0


def evaluate_case(scene, page, gt_corners, detected, acc: Acceptance = Acceptance()) -> dict:
    h, w = scene.shape[:2]
    diag = float(np.hypot(w, h))
    out = {"detected": detected is not None, "iou": 0.0, "corner_err": None, "ncc": None, "ncc_oracle": None, "ncc_ratio": None,
           "accepted": False, "failure_reasons": []}
    if detected is None:
        out["failure_reasons"].append("no_detection")
        return out
    if not is_valid_quad(detected):
        out["failure_reasons"].append("invalid_quad")
        return out
    out["iou"] = polygon_iou(order_quad(detected), order_quad(gt_corners))
    out["corner_err"] = corner_error(detected, gt_corners, diag)
    out["ncc"] = rectification_ncc(scene, detected, page)
    out["ncc_oracle"] = rectification_ncc(scene, gt_corners, page)
    out["ncc_ratio"] = out["ncc"] / out["ncc_oracle"] if out["ncc_oracle"] > 1e-6 else 0.0
    if out["iou"] < acc.iou_min:
        out["failure_reasons"].append("low_iou")
    if out["corner_err"] > acc.corner_err_max:
        out["failure_reasons"].append("corner_error")
    if acc.ncc_ratio_min > 0 and out["ncc_ratio"] < acc.ncc_ratio_min:
        out["failure_reasons"].append("poor_rectification")
    out["accepted"] = not out["failure_reasons"]
    return out
