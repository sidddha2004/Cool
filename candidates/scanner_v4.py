"""Candidate v4: propose two page quads (global-threshold and edge-based) and select by measured boundary support.

Evidence: v1 (Otsu) fails on shadows; v2 (Canny hull) fails on noise/blur; v3 (retuned v2) was worse overall.
The failure sets are complementary, so instead of retuning constants we score each proposed quad by how
consistently its perimeter separates a brighter inside from a darker outside (median over samples, so a
quad that cuts through the page interior or balloons into noisy background scores low).
"""
import cv2
import numpy as np

DEFAULT_CONFIG = {"work_max_side": 500, "epsilon": 0.02, "probe": 5, "samples_per_edge": 40}


def _quad_from_contour(c):
    approx = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
    return approx.reshape(-1, 2).astype(np.float32) if len(approx) == 4 else cv2.boxPoints(cv2.minAreaRect(c))


def _otsu_quad(gray):
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return (_quad_from_contour(max(cnts, key=cv2.contourArea)) if cnts else None), th


def _edge_quad(gray):
    eq = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    edges = cv2.Canny(cv2.GaussianBlur(eq, (5, 5), 0), 30, 90)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return (_quad_from_contour(cv2.convexHull(max(cnts, key=cv2.contourArea))) if cnts else None), edges


def _support(gray, quad, probe, n):
    """Median over perimeter samples of (mean inside - mean outside), sampled along inward/outward normals."""
    q = cv2.convexHull(quad.astype(np.float32)).reshape(-1, 2)
    if len(q) < 3:
        return -1e9
    c = q.mean(0); vals = []
    h, w = gray.shape
    for i in range(len(q)):
        a, b = q[i], q[(i + 1) % len(q)]
        d = b - a; L = np.linalg.norm(d)
        if L < 1e-3: continue
        nrm = np.array([-d[1], d[0]]) / L
        if np.dot(nrm, c - (a + b) / 2) < 0: nrm = -nrm          # point inward
        for t in np.linspace(0.05, 0.95, n):
            p = a + d * t
            pin, pout = p + nrm * probe, p - nrm * probe
            if not (0 <= pout[0] < w and 0 <= pout[1] < h and 0 <= pin[0] < w and 0 <= pin[1] < h):
                continue
            vals.append(float(gray[int(pin[1]), int(pin[0])]) - float(gray[int(pout[1]), int(pout[0])]))
    return float(np.median(vals)) if vals else -1e9


def scan(img, config=None):
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    h, w = img.shape[:2]
    s = cfg["work_max_side"] / max(h, w)
    small = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else img.copy()
    s = small.shape[1] / w
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    smooth = cv2.GaussianBlur(gray, (0, 0), 2.0)
    q1, th = _otsu_quad(gray)
    q2, edges = _edge_quad(gray)
    props = {"otsu": q1, "edge": q2}
    scores = {k: _support(smooth, v, cfg["probe"], cfg["samples_per_edge"]) for k, v in props.items() if v is not None}
    stages = {"gray": gray, "threshold": th, "edges": edges}
    if not scores:
        return {"corners": None, "stages": stages, "info": {"scores": scores}}
    best = max(scores, key=scores.get)
    return {"corners": (props[best] / s).tolist(), "stages": stages, "info": {"scores": scores, "chosen": best}}
