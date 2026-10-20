"""Candidate v2 (proposed fix for v1's shadow failures, see artifacts/traces).

Hypothesis from v1 stage images: a single global Otsu threshold removes the shadowed part of the page.
Change: locate the page by its *edges* (local gradient) instead of by absolute brightness:
CLAHE -> blur -> Canny -> close -> external contours -> convex hull of the largest -> 4-point polygon.
"""
import cv2
import numpy as np

DEFAULT_CONFIG = {"work_max_side": 500, "blur": 5, "canny_lo": 30, "canny_hi": 90, "close": 7, "epsilon": 0.02,
                  "clahe_clip": 2.0}


def scan(img, config=None):
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    h, w = img.shape[:2]
    s = cfg["work_max_side"] / max(h, w)
    small = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else img.copy()
    s = small.shape[1] / w
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    eq = cv2.createCLAHE(clipLimit=cfg["clahe_clip"], tileGridSize=(8, 8)).apply(gray)
    blur = cv2.GaussianBlur(eq, (cfg["blur"], cfg["blur"]), 0)
    edges = cv2.Canny(blur, cfg["canny_lo"], cfg["canny_hi"])
    k = np.ones((cfg["close"], cfg["close"]), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, k)
    stages = {"gray": gray, "clahe": eq, "edges": edges, "closed": closed}
    cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return {"corners": None, "stages": stages}
    c = cv2.convexHull(max(cnts, key=cv2.contourArea))
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, cfg["epsilon"] * peri, True)
    quad = approx.reshape(-1, 2) if len(approx) == 4 else cv2.boxPoints(cv2.minAreaRect(c))
    return {"corners": (np.asarray(quad, np.float32) / s).tolist(), "stages": stages}
