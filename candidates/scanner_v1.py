"""Candidate v1: the straightforward document scanner an AI assistant typically writes first.

gray -> blur -> global Otsu threshold -> largest external contour -> 4-point polygon.
Written BEFORE any failure analysis; it is the baseline under test, not tuned to the corpus.
"""
import cv2
import numpy as np

DEFAULT_CONFIG = {"work_max_side": 500, "blur": 5, "epsilon": 0.02}


def scan(img, config=None):
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    h, w = img.shape[:2]
    s = cfg["work_max_side"] / max(h, w)
    small = cv2.resize(img, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else img.copy()
    s = small.shape[1] / w
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (cfg["blur"], cfg["blur"]), 0)
    _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    stages = {"gray": gray, "threshold": th}
    cnts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return {"corners": None, "stages": stages}
    c = max(cnts, key=cv2.contourArea)
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, cfg["epsilon"] * peri, True)
    quad = approx.reshape(-1, 2) if len(approx) == 4 else cv2.boxPoints(cv2.minAreaRect(c))
    return {"corners": (np.asarray(quad, np.float32) / s).tolist(), "stages": stages}
