"""Integration: spawn the real MCP server over stdio and call tools through the official client."""
import asyncio
import json
import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"inspect_vision_environment", "analyze_vision_pipeline", "generate_visual_test_cases",
            "run_visual_regression_suite", "analyze_visual_failures", "reproduce_visual_failure",
            "benchmark_vision_pipeline", "run_cool_graviton_benchmark", "compare_implementations", "verify_candidate_fix"}


def _payload(res):
    if getattr(res, "structuredContent", None):
        sc = res.structuredContent
        return sc.get("result", sc) if isinstance(sc, dict) and set(sc) == {"result"} else sc
    return json.loads(res.content[0].text)


async def _session(fn):
    params = StdioServerParameters(command=sys.executable, args=["-m", "coolguard.mcp_server"],
                                   env={"PYTHONPATH": str(ROOT / "src"), "COOLGUARD_ROOT": str(ROOT)})
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            return await fn(s)


def test_tools_registered_with_schemas():
    async def go(s):
        return (await s.list_tools()).tools
    tl = asyncio.run(_session(go))
    assert {t.name for t in tl} == EXPECTED
    assert all(t.input_schema.get("type") == "object" and t.description for t in tl)


def test_end_to_end_and_structured_errors():
    async def go(s):
        env = _payload(await s.call_tool("inspect_vision_environment", {}))
        bad = _payload(await s.call_tool("run_visual_regression_suite", {"candidate": "../../etc/passwd", "corpus": "artifacts/corpora/x"}))
        gen = _payload(await s.call_tool("generate_visual_test_cases", {"name": "mcp-test", "categories": ["clean", "shadow"], "seeds": [0]}))
        run = _payload(await s.call_tool("run_visual_regression_suite", {"candidate": "candidates/scanner_v1.py", "corpus": "artifacts/corpora/mcp-test"}))
        remote = _payload(await s.call_tool("run_cool_graviton_benchmark", {"candidate": "candidates/scanner_v1.py", "corpus": "artifacts/corpora/mcp-test"}))
        return env, bad, gen, run, remote
    env, bad, gen, run, remote = asyncio.run(_session(go))
    assert env["environment"]["opencv_is_v5"] is True
    assert bad["ok"] is False and bad["error"]["type"] == "path_not_allowed"
    assert gen["n_cases"] == 4
    assert run["n"] == 4 and run["by_category"]["clean"] == 1.0
    # without config/remote.json the cloud tool must be explicit about being blocked, never fabricate results
    if not (ROOT / "config" / "remote.json").exists():
        assert remote["ok"] is False and remote["status"] == "BLOCKED" and remote["verified_on_graviton"] is False
