"""Remote execution on a pre-launched COOL Graviton instance (SSH to a fixed, allow-listed procedure).

This module NEVER launches or subscribes to anything and never forwards caller-supplied shell text.
If remote configuration or connectivity is missing it returns status BLOCKED with the exact reason.
A local fallback is never presented as Graviton evidence.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tarfile
import time
from pathlib import Path

from . import experiments, paths

CONFIG = paths.ROOT / "config" / "remote.json"     # git-ignored; see config/remote.example.json
_HOST_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,252}$")
_USER_RE = re.compile(r"^[a-z_][a-z0-9_-]{0,31}$")
_VENV_RE = re.compile(r"^/opt/cool/venvs/python_3\.\d+$")


def _blocked(reason: str, needs: str) -> dict:
    return {"status": "BLOCKED", "reason": reason, "needs": needs, "verified_on_graviton": False,
            "note": "No remote measurement was made. Local results must not be presented as COOL/Graviton evidence."}


def load_config() -> dict | None:
    if not CONFIG.exists():
        return None
    cfg = json.loads(CONFIG.read_text())
    if not _HOST_RE.match(cfg.get("host", "")) or not _USER_RE.match(cfg.get("user", "")):
        raise ValueError("config/remote.json: invalid host or user")
    if not _VENV_RE.match(cfg.get("cool_venv", "/opt/cool/venvs/python_3.12")):
        raise ValueError("config/remote.json: cool_venv must match /opt/cool/venvs/python_3.X")
    return cfg


def _bundle(candidate: Path, corpus: Path, candidate_name: str, threads: int, dst: Path) -> Path:
    tgz = dst / "bundle.tgz"
    with tarfile.open(tgz, "w:gz") as t:
        for f in (paths.ROOT / "src" / "coolguard").glob("*.py"):
            t.add(f, f"src/coolguard/{f.name}")
        t.add(candidate, f"candidates/{candidate_name}")
        t.add(corpus, "corpus")
    return tgz


BUDGET_FILE = paths.ARTIFACTS / "remote_budget.json"
MAX_BUDGET_RUNS = 3


def _runs_used() -> int:
    return json.loads(BUDGET_FILE.read_text())["runs"] if BUDGET_FILE.exists() else 0


def run_cool_graviton_benchmark(candidate: str, corpus: str, repeats: int = 30, threads: int = 4) -> dict:
    cfg = load_config()
    if cfg is None:
        return _blocked("config/remote.json not found (no COOL Graviton instance configured)",
                        "Subscribe to the COOL AMI, launch an instance yourself (docs/deployment.md), then create config/remote.json")
    if _runs_used() >= MAX_BUDGET_RUNS:
        return {"status": "BLOCKED", "reason": f"remote benchmark budget of {MAX_BUDGET_RUNS} runs reached "
                f"(delete {BUDGET_FILE.name} to reset after human approval)", "needs": "human approval", "verified_on_graviton": False}
    if not (shutil.which("ssh") and shutil.which("scp")):
        return _blocked("ssh/scp not available on this machine", "install an OpenSSH client")
    if not (1 <= repeats <= 200 and 1 <= threads <= 64):
        raise ValueError("repeats must be 1..200 and threads 1..64")
    cand = paths.resolve_inside(candidate, paths.CANDIDATES)
    corp = paths.resolve_inside(corpus, paths.CORPORA)
    BUDGET_FILE.write_text(json.dumps({"runs": _runs_used() + 1}))     # counted before launch: failed runs still cost
    eid = experiments.new_id("remote")
    work = paths.EXPERIMENTS / f"{eid}.artifacts"
    work.mkdir(parents=True, exist_ok=True)
    (work / "candidate.txt").write_text(cand.name)
    (work / "threads.txt").write_text(str(threads))
    _bundle(cand, corp, cand.name, threads, work)
    target = f"{cfg['user']}@{cfg['host']}"
    jobdir = f"coolguard_job/{eid}"
    ssh = ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=15"]
    scp = ["scp", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=15"]
    if cfg.get("key_file"):
        ssh += ["-i", cfg["key_file"]]; scp += ["-i", cfg["key_file"]]
    steps = [
        ssh + [target, f"mkdir -p {jobdir}"],
        scp + [str(work / "bundle.tgz"), str(work / "candidate.txt"), str(work / "threads.txt"),
               str(paths.ROOT / "scripts" / "remote_bench.sh"), f"{target}:{jobdir}/"],
        ssh + [target, f"timeout 1500 bash {jobdir}/remote_bench.sh {jobdir} {cfg.get('cool_venv', '/opt/cool/venvs/python_3.12')} {int(repeats)}"],
        scp + ["-r", f"{target}:{jobdir}/out", str(work / "remote_out")],
    ]
    log = []
    for cmd in steps:
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        except subprocess.TimeoutExpired:
            return {"status": "FAILED", "kind": "infrastructure", "reason": "remote step timed out", "experiment_id": eid, "log": log}
        log.append({"cmd": cmd[0] + " ...", "rc": p.returncode, "stderr_tail": p.stderr[-300:]})
        if p.returncode != 0:
            return {"status": "FAILED", "kind": "infrastructure", "reason": f"{cmd[0]} exited {p.returncode}",
                    "experiment_id": eid, "log": log, "verified_on_graviton": False}
    return summarize_remote(work / "remote_out", eid, cand, corp, repeats, threads, cfg)


def summarize_remote(out: Path, eid: str, cand: Path, corp: Path, repeats: int, threads: int, cfg: dict) -> dict:
    inst = json.loads((out / "instance.json").read_text())
    probes = {n: json.loads((out / f"probe_{n}.json").read_text()) for n in ("baseline", "cool")}
    runs = {n: [json.loads(p.read_text()) for p in sorted(out.glob(f"bench_{n}_*.json"))] for n in ("baseline", "cool")}
    cool_ok = bool(probes["cool"]["cool"]["verified"]) and inst["uname_m"] == "aarch64" and \
        probes["cool"]["opencv_module_path"] != probes["baseline"]["opencv_module_path"]
    def med(rs): return sorted(r["latency_ms"]["median"] for r in rs)[len(rs) // 2]
    table = {n: {"median_ms_per_run": [r["latency_ms"]["median"] for r in rs], "p95_ms_per_run": [r["latency_ms"]["p95"] for r in rs],
                 "throughput_per_run": [r["throughput_img_per_s"] for r in rs], "cpu_percent": [r["cpu_percent_of_one_core"] for r in rs],
                 "peak_mb": [r["peak_memory_mb"] for r in rs], "checksums": [r["output_checksum"] for r in rs],
                 "accepted": [r["correctness"] for r in rs]} for n, rs in runs.items()}
    same_out = len({c for n in table for c in table[n]["checksums"]}) == 1
    rec = {"experiment_id": eid, "kind": "remote_benchmark", "code_revision": runs["cool"][0]["candidate_sha256"],
           "candidate": str(cand.relative_to(paths.ROOT)), "dataset_id": corp.name,
           "environment": "aws-graviton-remote", "instance": inst, "runtime_baseline": probes["baseline"],
           "runtime_cool": probes["cool"], "workload": {"repeats": repeats, "threads": threads},
           "results": table,
           "speedup_median_cool_vs_baseline": med(runs["baseline"]) / med(runs["cool"]),
           "outputs_identical_across_runtimes": same_out,
           "verified_cool_on_graviton": cool_ok,
           "raw_dir": str(out), "execution": {"status": "completed"},
           "limitations": ["speedup is for this pipeline/corpus only; vendor aggregate figures do not transfer",
                           "baseline is pip opencv-python-headless 5.0.0.93 on the same instance; COOL build may be a different OpenCV minor version"]}
    experiments.save(rec)
    return {"status": "COMPLETED", **{k: rec[k] for k in ("experiment_id", "verified_cool_on_graviton", "speedup_median_cool_vs_baseline",
                                                          "outputs_identical_across_runtimes")}, "record": rec}
