"""Agentic-workflow tests: decisions derive from measured evidence; gates and limits hold."""
import time
from pathlib import Path

import pytest
from coolguard import controller, paths, tools


def _analysis(cat, mode, pass_rate=0.3, area=0.6, cov=0.5):
    return {"n_failed": 5, "categories": [{"category": cat, "n_failed": 5, "n": 12, "pass_rate": pass_rate,
            "levels_failing": [1, 2], "dominant_mode": mode, "median_area_ratio": area,
            "median_threshold_page_coverage": cov, "examples": [f"{cat}-L1-s0"]}]}


def _confirmed(cat):
    st = controller.LoopState(trace_id="t", started=time.time()); st.targeted.add(cat); return st


def test_distinct_failure_signatures_yield_different_justified_actions():
    under = controller.decide(_analysis("shadow", "under_detection"), _confirmed("shadow"))
    over = controller.decide(_analysis("noise", "over_detection", area=2.0, cov=None), _confirmed("noise"))
    none = controller.decide(_analysis("blur", "no_detection", area=None, cov=None), _confirmed("blur"))
    assert under["args"]["stage"] == "threshold" and over["args"]["stage"] == "edges" and none["action"] == "inspect_stage"
    assert under["action"] != none["action"] and under["rationale"] != over["rationale"]
    assert "%" in under["rationale"] and under["evidence"]["median_area_ratio"] == 0.6   # cites measured value


def test_first_step_confirms_failure_on_fresh_seeds():
    d = controller.decide(_analysis("shadow", "under_detection"), controller.LoopState(trace_id="t"))
    assert d["action"] == "generate_targeted_cases" and d["args"]["categories"] == ["shadow"]


def test_no_failures_moves_to_benchmarking_and_limits_stop_loop():
    ok = controller.decide({"n_failed": 0, "categories": []}, controller.LoopState(trace_id="t"))
    assert ok["action"] == "benchmark_and_report"
    st = controller.LoopState(trace_id="t", iteration=controller.MAX_ITERATIONS)
    stop = controller.decide(_analysis("shadow", "under_detection"), st)
    assert stop["action"] == "stop_for_human" and stop["requires_human"]
    old = controller.LoopState(trace_id="t", started=time.time() - controller.MAX_TOTAL_SECONDS - 5)
    assert controller.decide(_analysis("shadow", "under_detection"), old)["action"] == "stop_for_human"


def test_failed_candidate_cannot_be_reported_successful():
    for verdict in ("REJECT", "PARTIAL"):
        v = {"verdict": verdict, "evidence": {}, "regressions": ["x"], "unresolved_cases": ["y"]}
        assert controller.decide_after_candidate(v)["action"] != "preserve_for_review"
    acc = controller.decide_after_candidate({"verdict": "ACCEPT", "evidence": {}})
    assert acc["action"] == "preserve_for_review" and acc["requires_human"]


@pytest.fixture
def broken_candidates():
    made = []
    def mk(name, src):
        p = paths.CANDIDATES / name; p.write_text(src); made.append(p); return f"candidates/{name}"
    yield mk
    for p in made: p.unlink(missing_ok=True)


def test_regressing_or_crashing_candidate_is_rejected_end_to_end(broken_candidates):
    tools.generate_visual_test_cases("unit-gate", ["clean", "shadow"], [0, 1])
    base = tools.run_visual_regression_suite("candidates/scanner_v1.py", "artifacts/corpora/unit-gate")
    assert base["by_category"]["clean"] == 1.0
    crash = broken_candidates("_t_crash.py", "def scan(img, config=None):\n    raise RuntimeError('boom')\n")
    v = tools.verify_candidate_fix(crash, base["experiment_id"], "artifacts/corpora/unit-gate")
    assert v["verdict"] == "REJECT" and not v["acceptance_passed"] and len(v["regressions"]) >= 1
    none = broken_candidates("_t_none.py", "def scan(img, config=None):\n    return {'corners': None, 'stages': {}}\n")
    v = tools.verify_candidate_fix(none, base["experiment_id"], "artifacts/corpora/unit-gate")
    assert v["verdict"] == "REJECT" and v["next_action"]["action"] == "reject_candidate"


def test_timeout_is_infrastructure_not_experiment_failure(broken_candidates):
    tools.generate_visual_test_cases("unit-to", ["clean"], [0])
    slow = broken_candidates("_t_slow.py", "import time\ndef scan(img, config=None):\n    time.sleep(30)\n")
    r = tools.run_visual_regression_suite(slow, "artifacts/corpora/unit-to", timeout_s=3)
    assert r["ok"] is False and r["error"]["type"] == "infrastructure"


def test_path_traversal_and_bad_inputs_rejected():
    for bad in ("../x.py", "C:/Windows/system32/calc.py", "candidates/../src/coolguard/tools.py"):
        r = tools.run_visual_regression_suite(bad, "artifacts/corpora/unit-gate")
        assert r["ok"] is False and r["error"]["type"] == "path_not_allowed"
    assert tools.generate_visual_test_cases("x y!")["error"]["type"] == "validation"
    assert tools.generate_visual_test_cases("big", seeds=list(range(30)))["error"]["type"] == "validation"


def test_unreadable_image_is_reported(tmp_path):
    tools.generate_visual_test_cases("unit-corrupt", ["clean"], [0])
    d = paths.CORPORA / "unit-corrupt"
    (d / "images" / "clean-L0-s0.png").write_bytes(b"not a png")
    r = tools.run_visual_regression_suite("candidates/scanner_v1.py", "artifacts/corpora/unit-corrupt")
    assert r["ok"] and r["passed"] == 0 and r["failed_case_ids"] == ["clean-L0-s0"]


def test_remote_blocked_without_config():
    if (paths.ROOT / "config" / "remote.json").exists():
        pytest.skip("remote configured")
    r = tools.run_cool_graviton_benchmark("candidates/scanner_v1.py", "artifacts/corpora/unit-gate")
    assert r["status"] == "BLOCKED" and r["verified_on_graviton"] is False and r["ok"] is False


def test_trace_and_experiment_ids_cannot_traverse(tmp_path):
    from coolguard import experiments
    for bad in ("../../escape", str(tmp_path / "pwned"), "a/b", "x" * 200, ""):
        with pytest.raises(ValueError):
            experiments.trace(bad, "x")
        with pytest.raises(ValueError):
            experiments.read_trace(bad)
        with pytest.raises(ValueError):
            experiments.load(bad)
    assert not (tmp_path / "pwned.jsonl").exists()


def test_worker_env_is_allowlist_and_candidate_cannot_forge_report(monkeypatch, broken_candidates):
    from coolguard import runner
    monkeypatch.setenv("OPENAI_API_KEY", "sk-secret"); monkeypatch.setenv("MY_SECRET", "s")
    env = runner.safe_env()
    assert "OPENAI_API_KEY" not in env and "MY_SECRET" not in env and env["OPENCV_IO_MAX_IMAGE_PIXELS"]
    tools.generate_visual_test_cases("unit-forge", ["clean"], [0])
    forge = broken_candidates("_t_forge.py", "import sys\nprint('{\"results\": [{\"accepted\": true}]}')\n"
                              "def scan(img, config=None):\n    return {'corners': None, 'stages': {}}\n")
    r = tools.run_visual_regression_suite(forge, "artifacts/corpora/unit-forge")
    assert r["ok"] and r["passed"] == 0         # stdout noise ignored; scored independently


def test_benchmark_runs_real_pipeline_and_compares_like_for_like():
    tools.generate_visual_test_cases("unit-bench", ["clean", "rotation"], [0], [0])
    a = tools.benchmark_vision_pipeline("candidates/scanner_v1.py", "artifacts/corpora/unit-bench", warmup=2, repeats=3)
    b = tools.benchmark_vision_pipeline("candidates/scanner_v1.py", "artifacts/corpora/unit-bench", warmup=2, repeats=3)
    assert a["ok"] and a["measurements"]["latency_ms"]["median"] > 0 and a["correctness"]["n"] == 2
    assert "LOCAL" in a["note"] and a["measurements"]["peak_memory_mb"] > 0
    cmp_ = tools.compare_implementations(a["experiment_id"], b["experiment_id"])
    assert cmp_["like_for_like"] is True             # identical code, deterministic outputs
    c = tools.benchmark_vision_pipeline("candidates/scanner_v1.py", "artifacts/corpora/unit-bench", warmup=2, repeats=4)
    assert tools.compare_implementations(a["experiment_id"], c["experiment_id"])["like_for_like"] is False  # repeats differ
    assert tools.benchmark_vision_pipeline("candidates/scanner_v1.py", "artifacts/corpora/unit-bench", repeats=9999)["ok"] is False
