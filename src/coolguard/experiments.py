"""Experiment records and the auditable decision trace (append-only JSONL)."""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from pathlib import Path

import re

from . import paths

_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,80}$")


def _check_id(x: str) -> str:
    if not isinstance(x, str) or not _ID_RE.match(x):
        raise ValueError("id must match [A-Za-z0-9_-]{1,80}")
    return x


def new_id(prefix: str = "exp") -> str:
    return f"{prefix}-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"


def config_hash(cfg: dict) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16]


def save(record: dict) -> Path:
    paths.ensure_dirs()
    p = paths.EXPERIMENTS / f"{record['experiment_id']}.json"
    p.write_text(json.dumps(record, indent=1))
    return p


def load(experiment_id: str) -> dict:
    return json.loads((paths.EXPERIMENTS / f"{_check_id(experiment_id)}.json").read_text())


def list_ids() -> list[str]:
    return sorted(p.stem for p in paths.EXPERIMENTS.glob("*.json"))


def trace(trace_id: str, step: str, **fields) -> dict:
    """Append one decision-trace event. Fields should include inputs, evidence, action, rationale."""
    _check_id(trace_id)
    paths.ensure_dirs()
    ev = {"ts": time.time(), "trace_id": trace_id, "step": step, **fields}
    with open(paths.TRACES / f"{trace_id}.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(ev) + "\n")
    return ev


def read_trace(trace_id: str) -> list[dict]:
    p = paths.TRACES / f"{_check_id(trace_id)}.jsonl"
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []
