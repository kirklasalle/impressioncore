"""Phase-0 gate probe (v2).

For each configured entrypoint, using the official MCP client over stdio:
  1. initialize (records protocol version + server name)
  2. tools/list
  3. one safe positive tools/call (if configured)
  4. a negative call to a nonexistent tool -> MUST come back isError=true (no false success)

Server stderr goes to tests/logs/<label>.log. Exception groups are unwrapped.
Usage: python tests/probe_v2.py [label ...]
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parent.parent
PY = os.environ.get("PROBE_PY", sys.executable)
HERE = Path(__file__).resolve().parent
LOGS = HERE / "logs"
LOGS.mkdir(exist_ok=True)

TARGETS = {
    "goliath":    ("goliath/server.py",          "goliath_get_swarm_state", {}),
    "ids":        ("ids/server_ai_enhanced.py",  None, None),
    "eds":        ("eds/server_enhanced.py",     None, None),
    "ipa":        ("ipa/server_ultimate.py",     "ipa_research_capabilities", {}),
    "vrgc":       ("vrgc/server_enhanced.py",    None, None),
    "dpa":        ("dpa/server.py",              "get_intent", {"text": "remind me to call mom tomorrow"}),
    "web-search": ("web-search/server.py",       "get_search_suggestions", {"query": "mcp"}),
    "loc":        ("loc/server.py",              None, None),
}


def flatten(e):
    if isinstance(e, BaseExceptionGroup):
        out = []
        for sub in e.exceptions:
            out.extend(flatten(sub))
        return out
    return [e]


async def probe(label, script, tool, args, timeout=90):
    rec = {"server": label, "script": script}
    target_path = ROOT / script
    params = StdioServerParameters(
        command=PY,
        args=[str(target_path)],
        cwd=str(target_path.parent),
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"},
    )
    t0 = time.time()
    errlog = open(LOGS / f"{label}.log", "w", encoding="utf-8", errors="replace")
    try:
        async with asyncio.timeout(timeout):
            async with stdio_client(params, errlog=errlog) as (r, w):
                async with ClientSession(r, w) as s:
                    init = await s.initialize()
                    rec["init_s"] = round(time.time() - t0, 2)
                    rec["protocol"] = init.protocolVersion
                    rec["server_name"] = init.serverInfo.name
                    tl = await s.list_tools()
                    rec["tools"] = len(tl.tools)
                    rec["tool_names"] = [t.name for t in tl.tools]
                    if tool:
                        res = await s.call_tool(tool, args)
                        txt = " ".join(getattr(c, "text", "") for c in res.content)
                        rec["call"] = tool
                        rec["call_isError"] = res.isError
                        rec["call_excerpt"] = txt[:240].replace("\n", " ")
                    neg = await s.call_tool("__nonexistent_tool__", {})
                    rec["negative_isError"] = neg.isError
                    rec["status"] = "OK" if neg.isError else "FALSE_SUCCESS"
    except BaseException as e:  # noqa: BLE001 - probe must record everything
        subs = flatten(e)
        rec["status"] = "FAIL"
        rec["error"] = " | ".join(f"{type(x).__name__}: {str(x)[:200]}" for x in subs)
    finally:
        errlog.close()
    rec["elapsed_s"] = round(time.time() - t0, 2)
    return rec


async def main():
    labels = sys.argv[1:] or list(TARGETS)
    results = []
    for label in labels:
        script, tool, args = TARGETS[label]
        r = await probe(label, script, tool, args)
        results.append(r)
        print(json.dumps({k: v for k, v in r.items() if k != "tool_names"}), flush=True)
    (HERE / "probe_v2_results.json").write_text(json.dumps(results, indent=2))
    ok = sum(r["status"] == "OK" for r in results)
    print(f"GATE: {ok}/{len(results)} OK")


if __name__ == "__main__":
    asyncio.run(main())
