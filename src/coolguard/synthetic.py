"""Deterministic synthetic document-scene generator with independent ground truth.

Ground truth is the corner quadrilateral produced by the *known* homography used to
place a flat page into the scene. The detector under test never contributes to it.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path

import cv2
import numpy as np

GENERATOR_VERSION = "1.0"
PAGE_W, PAGE_H = 400, 560           # canonical flat page (portrait)
MAX_CASES = 400
MAX_DIM = 2048
MAX_SEEDS = 20

# category -> level parameter lists (index = severity level)
CATEGORIES: dict[str, list[float]] = {
    "clean": [0.0],
    "rotation": [10.0, 25.0, 40.0],                 # degrees
    "perspective": [0.06, 0.12, 0.18],              # corner jitter, fraction of scene size
    "illumination": [0.6, 0.4, 0.25],               # brightness factor at dark side of gradient
    "shadow": [0.7, 0.5, 0.35],                     # brightness factor inside shadow
    "blur": [1.5, 3.0, 5.0],                        # gaussian sigma px
    "noise": [8.0, 18.0, 30.0],                     # gaussian sigma gray levels
    "lowres": [0.75, 0.5, 0.35],                    # scale factor
    "jpeg": [40, 20, 8],                            # quality
    "lowcontrast": [0.5, 0.3, 0.15],                # paper/background contrast retention
}


@dataclass
class CaseSpec:
    case_id: str
    category: str
    level: int
    seed: int
    width: int
    height: int
    param: float
    corners: list            # ground-truth quad TL,TR,BR,BL in scene px, float
    homography: list         # page->scene 3x3
    generator_version: str = GENERATOR_VERSION
    image: str = ""
    page: str = ""


def _make_page(rng: np.random.Generator) -> np.ndarray:
    """Flat page: off-white paper with text-like dark blocks and a figure."""
    page = np.full((PAGE_H, PAGE_W, 3), 238, np.uint8)
    y = 40
    while y < PAGE_H - 40:
        x = 30
        while x < PAGE_W - 40:
            w = int(rng.integers(15, 70))
            if x + w > PAGE_W - 30:
                break
            cv2.rectangle(page, (x, y), (x + w, y + 7), (55, 55, 60), -1)
            x += w + int(rng.integers(6, 14))
        y += int(rng.integers(16, 24))
    cx, cy = int(rng.integers(120, 280)), int(rng.integers(200, 360))
    cv2.circle(page, (cx, cy), int(rng.integers(30, 60)), (90, 70, 60), -1)
    cv2.rectangle(page, (0, 0), (PAGE_W - 1, PAGE_H - 1), (200, 200, 200), 2)
    return page


def _background(rng: np.random.Generator, w: int, h: int, level: float) -> np.ndarray:
    base = rng.integers(70, 110)
    bg = np.full((h, w, 3), base, np.float32)
    bg += rng.normal(0, 4, (h, w, 1)).astype(np.float32)
    yy = np.linspace(-10, 10, h, dtype=np.float32)[:, None, None]
    bg += yy
    bg *= np.array([0.9, 1.0, 1.1], np.float32)[None, None, :] if rng.random() < 0.5 else 1.0
    return np.clip(bg, 0, 255)


def _quad(rng: np.random.Generator, w: int, h: int, category: str, p: float) -> np.ndarray:
    """Target quad (TL,TR,BR,BL) in scene coords; margins keep it fully inside the frame."""
    cx, cy = w / 2, h / 2
    pw, ph = w * 0.42, h * 0.78        # half-ish extents
    pts = np.array([[-pw / 2, -ph / 2], [pw / 2, -ph / 2], [pw / 2, ph / 2], [-pw / 2, ph / 2]], np.float64)
    angle = rng.uniform(-4, 4)
    if category == "rotation":
        angle = p * rng.choice([-1, 1])
    a = math.radians(angle)
    R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
    pts = pts @ R.T
    jit = 0.02 if category != "perspective" else p
    pts += rng.uniform(-jit, jit, pts.shape) * np.array([w, h])
    pts += [cx, cy]
    m = 8
    pts[:, 0] = np.clip(pts[:, 0], m, w - m)
    pts[:, 1] = np.clip(pts[:, 1], m, h - m)
    return pts.astype(np.float32)


def render_case(category: str, level: int, seed: int, width: int = 640, height: int = 480, param: float | None = None):
    """Return (scene_bgr, flat_page_bgr, CaseSpec-without-paths)."""
    if category not in CATEGORIES:
        raise ValueError(f"unknown category {category!r}; valid: {sorted(CATEGORIES)}")
    if not (0 <= level < len(CATEGORIES[category])):
        raise ValueError(f"level {level} out of range for {category}")
    if not (64 <= width <= MAX_DIM and 64 <= height <= MAX_DIM):
        raise ValueError(f"image dimensions must be within 64..{MAX_DIM}")
    p = CATEGORIES[category][level] if param is None else float(param)
    rng = np.random.default_rng([seed, level, sorted(CATEGORIES).index(category)])
    page = _make_page(rng)
    bg = _background(rng, width, height, p)
    quad = _quad(rng, width, height, category, p)
    src = np.array([[0, 0], [PAGE_W - 1, 0], [PAGE_W - 1, PAGE_H - 1], [0, PAGE_H - 1]], np.float32)
    H = cv2.getPerspectiveTransform(src, quad)
    pg = page.astype(np.float32)
    if category == "lowcontrast":
        # pull paper towards background brightness: contrast retained = p
        bgm = float(bg.mean())
        pg = bgm + (pg - bgm) * p
    warped = cv2.warpPerspective(pg, H, (width, height), flags=cv2.INTER_LINEAR)
    mask = cv2.warpPerspective(np.full((PAGE_H, PAGE_W), 255, np.uint8), H, (width, height))
    mask = cv2.GaussianBlur(mask, (0, 0), 0.8).astype(np.float32)[..., None] / 255.0
    scene = bg * (1 - mask) + warped * mask

    xs = np.linspace(0, 1, width, dtype=np.float32)[None, :, None]
    if category == "illumination":
        scene *= p + (1 - p) * (1 - xs)               # 1.0 at left, p at right
    elif category == "shadow":
        # soft-edged diagonal shadow cast across the page (covers a part of it)
        ang = rng.uniform(0, math.pi)
        yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
        d = (xx - width / 2) * math.cos(ang) + (yy - height / 2) * math.sin(ang)
        off = rng.uniform(-0.1, 0.1) * width
        s = 1 / (1 + np.exp(-(d - off) / 6.0))
        scene *= (1 - s * (1 - p))[..., None]
    scene = np.clip(scene, 0, 255)

    if category == "blur":
        scene = cv2.GaussianBlur(scene, (0, 0), p)
    if category == "noise":
        scene = scene + rng.normal(0, p, scene.shape).astype(np.float32)
    scene = np.clip(scene, 0, 255).astype(np.uint8)
    gt = quad.copy()
    if category == "lowres":
        nw, nh = int(width * p), int(height * p)
        scene = cv2.resize(scene, (nw, nh), interpolation=cv2.INTER_AREA)
        gt = gt * p
    if category == "jpeg":
        ok, enc = cv2.imencode(".jpg", scene, [cv2.IMWRITE_JPEG_QUALITY, int(p)])
        scene = cv2.imdecode(enc, cv2.IMREAD_COLOR)
    h2, w2 = scene.shape[:2]
    spec = CaseSpec(
        case_id=f"{category}-L{level}-s{seed}", category=category, level=level, seed=seed,
        width=w2, height=h2, param=float(p), corners=gt.astype(float).tolist(),
        homography=H.astype(float).tolist(),
    )
    return scene, page, spec


def generate_corpus(out_dir: Path, categories: list[str] | None = None, seeds: list[int] | None = None,
                    levels: list[int] | None = None, width: int = 640, height: int = 480,
                    params: list[float] | None = None) -> dict:
    """Write PNG images + manifest.json. Enforces corpus-size limits."""
    cats = categories or list(CATEGORIES)
    seeds = seeds if seeds is not None else [0, 1, 2]
    if len(seeds) > MAX_SEEDS:
        raise ValueError(f"at most {MAX_SEEDS} seeds")
    plan = []          # (category, level, seed, param-override)
    for c in cats:
        if c not in CATEGORIES:
            raise ValueError(f"unknown category {c!r}; valid: {sorted(CATEGORIES)}")
        for lv in (levels if levels is not None else range(len(CATEGORIES[c]))):
            if params is None and lv < len(CATEGORIES[c]):
                plan += [(c, lv, s, None) for s in seeds]
        if params is not None:      # severity sweep: explicit continuous parameter values (level index 0 is used as rng stream)
            plan += [(c, 0, s, pv) for s in seeds for pv in params]
    if len(plan) > MAX_CASES:
        raise ValueError(f"corpus would have {len(plan)} cases; limit is {MAX_CASES}")
    out_dir = Path(out_dir)
    (out_dir / "images").mkdir(parents=True, exist_ok=True)
    (out_dir / "pages").mkdir(parents=True, exist_ok=True)
    cases = []
    for c, lv, s, pv in plan:
        scene, page, spec = render_case(c, lv, s, width, height, param=pv)
        if pv is not None:
            spec.case_id = f"{c}-P{pv:g}-s{s}"
        spec.image = f"images/{spec.case_id}.png"
        spec.page = f"pages/{spec.case_id}.png"
        cv2.imwrite(str(out_dir / spec.image), scene)
        cv2.imwrite(str(out_dir / spec.page), page)
        cases.append(asdict(spec))
    manifest = {"generator_version": GENERATOR_VERSION, "page_size": [PAGE_W, PAGE_H],
                "scene_size": [width, height], "n_cases": len(cases), "cases": cases}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=1))
    return manifest
