"""COOLGuard MCP server (stdio). Exposes ten allow-listed tools; no shell, no arbitrary file access.

Candidate code may only be loaded from candidates/, corpora only from artifacts/corpora/ (see paths.py).
"""
from __future__ import annotations

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from . import tools

mcp = MCPServer(
    "coolguard",
    instructions=(
        "COOLGuard: evidence-driven visual debugging for OpenCV 5 document-scanner pipelines. Typical loop: "
        "inspect_vision_environment -> generate_visual_test_cases -> run_visual_regression_suite -> "
        "analyze_visual_failures (returns the next action chosen from measured evidence) -> edit a candidate under "
        "candidates/ -> verify_candidate_fix -> benchmark_vision_pipeline / run_cool_graviton_benchmark. "
        "Pass one trace_id through the loop to get an auditable decision trace. Never claim COOL/Graviton results "
        "unless run_cool_graviton_benchmark returned status COMPLETED with verified_cool_on_graviton=true."
    ),
)

_RO = ToolAnnotations(readOnlyHint=True)
_WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False)
_REMOTE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True)


@mcp.tool(annotations=_RO)
def inspect_vision_environment() -> dict:
    """Report Python/OpenCV versions, module path, platform/arch, available ops and whether COOL is verifiably active."""
    return tools.inspect_vision_environment()


@mcp.tool(annotations=_RO)
def analyze_vision_pipeline(candidate: str) -> dict:
    """Static inspection of a candidate under candidates/: OpenCV calls and pipeline stages with file:line."""
    return tools.analyze_vision_pipeline(candidate)


@mcp.tool(annotations=_WRITE)
def generate_visual_test_cases(name: str, categories: list[str] | None = None, seeds: list[int] | None = None,
                               levels: list[int] | None = None, width: int = 640, height: int = 480,
                               params: list[float] | None = None) -> dict:
    """Generate a deterministic corpus with independent ground truth into artifacts/corpora/<name> (size-limited)."""
    return tools.generate_visual_test_cases(name, categories, seeds, levels, width, height, params)


@mcp.tool(annotations=_WRITE)
def run_visual_regression_suite(candidate: str, corpus: str, case_ids: list[str] | None = None,
                                config: dict | None = None, timeout_s: int = 120, trace_id: str | None = None) -> dict:
    """Run a candidate scanner on a corpus in an isolated worker process and score against ground truth."""
    return tools.run_visual_regression_suite(candidate, corpus, case_ids, config, timeout_s, trace_id)


@mcp.tool(annotations=_WRITE)
def analyze_visual_failures(experiment_id: str, trace_id: str | None = None) -> dict:
    """Group failures by condition/mode from measured results + stage images; returns the policy's next action."""
    return tools.analyze_visual_failures(experiment_id, trace_id)


@mcp.tool(annotations=_WRITE)
def reproduce_visual_failure(candidate: str, corpus: str, case_id: str, experiment_id: str | None = None,
                             sweep_params: list[float] | None = None, seed: int = 0) -> dict:
    """Save a failing case as a self-contained bundle and confirm it reproduces; optional severity sweep for failure onset."""
    return tools.reproduce_visual_failure(candidate, corpus, case_id, experiment_id, sweep_params, seed)


@mcp.tool(annotations=_WRITE)
def benchmark_vision_pipeline(candidate: str, corpus: str, warmup: int = 3, repeats: int = 30,
                              threads: int | None = None, trace_id: str | None = None) -> dict:
    """Steady-state local benchmark (median/p95/throughput/CPU/memory) with raw data and correctness check."""
    return tools.benchmark_vision_pipeline(candidate, corpus, warmup, repeats, threads, trace_id)


@mcp.tool(annotations=_REMOTE)
def run_cool_graviton_benchmark(candidate: str, corpus: str, repeats: int = 30, threads: int = 4,
                                runs_used: int = 0) -> dict:
    """Run baseline-vs-COOL benchmark on a human-launched COOL Graviton instance. Returns BLOCKED if unavailable. Billable: needs human approval."""
    return tools.run_cool_graviton_benchmark(candidate, corpus, repeats, threads)


@mcp.tool(annotations=_RO)
def compare_implementations(experiment_a: str, experiment_b: str) -> dict:
    """Compare two saved experiments (same kind); refuses attribution when conditions differ."""
    return tools.compare_implementations(experiment_a, experiment_b)


@mcp.tool(annotations=_WRITE)
def verify_candidate_fix(candidate: str, baseline_experiment_id: str, corpus: str,
                         extra_corpora: list[str] | None = None, extra_baselines: list[str] | None = None,
                         trace_id: str | None = None) -> dict:
    """Run the candidate on the primary corpus and every extra corpus (each needs a baseline experiment id in extra_baselines, aligned). Verdict ACCEPT / PARTIAL / REJECT (any regression => REJECT)."""
    return tools.verify_candidate_fix(candidate, baseline_experiment_id, corpus, extra_corpora, extra_baselines, trace_id)


def main() -> None:
    mcp.run("stdio")


if __name__ == "__main__":
    main()
