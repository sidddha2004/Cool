"""Workspace layout and path-safety helpers (allow-listed roots only)."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(os.environ.get("COOLGUARD_ROOT", Path(__file__).resolve().parents[2])).resolve()
ARTIFACTS = ROOT / "artifacts"
CANDIDATES = ROOT / "candidates"
CORPORA = ARTIFACTS / "corpora"
EXPERIMENTS = ARTIFACTS / "experiments"
TRACES = ARTIFACTS / "traces"
FAILURES = ARTIFACTS / "failures"


class PathNotAllowed(ValueError):
    pass


def resolve_inside(path: str | os.PathLike, *roots: Path) -> Path:
    """Resolve `path` and require it to live inside one of `roots` (blocks traversal/symlink escape)."""
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    p = p.resolve()
    for r in roots:
        try:
            p.relative_to(r.resolve())
            return p
        except ValueError:
            continue
    raise PathNotAllowed(f"{p} is outside allowed roots: {[str(r) for r in roots]}")


def ensure_dirs() -> None:
    for d in (CORPORA, EXPERIMENTS, TRACES, FAILURES):
        d.mkdir(parents=True, exist_ok=True)
