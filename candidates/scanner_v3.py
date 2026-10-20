"""Candidate v3: v2's edge-based page localisation, made noise/blur-aware.

Evidence (experiments for v2): v2 fixed shadow/lowcontrast/illumination but regressed noise and blur.
Stage images showed Canny firing on sensor noise / smeared edges with fixed thresholds.
Change: estimate noise (MAD of Laplacian) -> scale blur kernel; derive Canny thresholds from the gradient-magnitude
distribution instead of constants; close with a kernel scaled to the working size.
"""
import cv2
import numpy as np

DEFAULT_CONFIG = {"work_max_side": 500, "epsilon": 0.02, "clahe_clip": 2.0, "canny_hi_pct": 92.0, "canny_ratio": 0.4,
                  "noise_blur_gain": 0.25, "close": 7}


def scan(img, config=None):
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    h, w = img.shape[:2]
    s = cfg["work_max_side"] / max(h, w)
    small = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else img.copy()
    s = small.shape[1] / w
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_32F)
    noise_sigma = float(np.median(np.abs(lap - np.median(lap))) / 0.6745 / 2.5)   # rough Gaussian-noise estimate
    sigma = 1.0 + cfg["noise_blur_gain"] * noise_sigma
    pre = cv2.GaussianBlur(gray, (0, 0), sigma)
    eq = cv2.createCLAHE(clipLimit=cfg["clahe_clip"], tileGridSize=(8, 8)).apply(pre)
    blur = cv2.GaussianBlur(eq, (0, 0), 1.0)
    gx = cv2.Sobel(blur, cv2.CV_32F, 1, 0); gy = cv2.Sobel(blur, cv2.CV_32F, 0, 1)
    mag = cv2.magnitude(gx, gy) / 4.0                                  # Canny uses un-normalised sobel; /4 ~ per-pixel grad
    hi = float(np.percentile(mag, cfg["canny_hi_pct"]))
    edges = cv2.Canny(blur, max(5.0, hi * cfg["canny_ratio"]), max(10.0, hi))
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((cfg["close"], cfg["close"]), np.uint8))
    stages = {"gray": gray, "clahe": eq, "edges": edges, "closed": closed}
    cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return {"corners": None, "stages": stages, "info": {"noise_sigma": noise_sigma}}
    c = cv2.convexHull(max(cnts, key=cv2.contourArea))
    approx = cv2.approxPolyDP(c, cfg["epsilon"] * cv2.arcLength(c, True), True)
    quad = approx.reshape(-1, 2) if len(approx) == 4 else cv2.boxPoints(cv2.minAreaRect(c))
    return {"corners": (np.asarray(quad, np.float32) / s).tolist(), "stages": stages, "info": {"noise_sigma": noise_sigma}}
