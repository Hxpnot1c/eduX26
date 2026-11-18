"""Rehearse the Plan A AI-literacy episode against a copy of the 05e branch, playing the chatbot's side.

    /home/vishnu/edux26/.venv/bin/python run_episode.py --code /tmp/claude-1000/w4-fix-verify/branch --label branch \
        --out captures [--scenario NAME ...] [--port 8765]

For each scenario: a fresh EDUX_DATA_DIR under /tmp/claude-1000/w4-fix-verify/data/, `edux.cli load coursepacks/example-mini`
(the branch reads ingest/ai_literacy/ in with every pack), `seed-demo --reset`, then the branch's own server on
127.0.0.1 (localhost only), driven through the MCP Python client with one session per scenario (as a chatbot
would hold one). Each turn records: the arguments sent (labels a chatbot would send), the full result, the exact
text the chatbot is told (cue + data per step), wall time, the server console line (ms, chars, OVER BUDGET), the
AI-literacy part p_now/levels and held misconceptions before/after, the evidence rows written, and the pending
literacy task / how-AI-works check stored in issued_plan. Never touches the repo or the export: --code must be a copy.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

from verify_scenarios import SCENARIOS

PY = sys.executable
AIL_PARTS = ["ail_ask", "ail_verify", "ail_how_fabrication", "ail_how_confidence", "ail_how_cutoff", "ail_how_agreement"]


def run(code: Path, env: dict, *args: str) -> str:
    out = subprocess.run([PY, "-m", *args], cwd=code, env=env, capture_output=True, text=True)
    if out.returncode:
        raise SystemExit(f"{args} failed:\n{out.stdout}\n{out.stderr}")
    return out.stdout


class Server:
    def __init__(self, code: Path, env: dict, port: int):
        self.lines: list[str] = []
        self.proc = subprocess.Popen([PY, "-m", "edux.cli", "serve", "--host", "127.0.0.1", "--port", str(port)],
                                     cwd=code, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        threading.Thread(target=self._read, daemon=True).start()
        import httpx
        for _ in range(100):
            try:
                httpx.get(f"http://127.0.0.1:{port}/", timeout=0.5)
                return
            except Exception:
                time.sleep(0.1)
        raise SystemExit("server did not start:\n" + "\n".join(self.lines))

    def _read(self):
        for line in self.proc.stdout:
            self.lines.append(line.rstrip())

    def stop(self):
        self.proc.terminate()
        self.proc.wait(5)


def snapshot(learner, graph, context_blocks, student: str) -> dict:
    conn = learner._conn()
    parts = {p: round(learner.part_p(student, p), 3) for p in AIL_PARTS}
    held = [m["id"] for m in context_blocks.held_misconceptions(student, graph.parts_of(learner.AIL_HOW))]
    row = conn.execute("SELECT plan_json FROM issued_plan WHERE student_id = ?", (student,)).fetchone()
    issued = json.loads(row[0]) if row else {}
    return {"p": parts, "levels": {p: learner.level(v) for p, v in parts.items()},
            "how_rollup": round(learner.rollup(student, learner.AIL_HOW), 3),
            "held_ail": held,
            "pending_literacy": issued.get("literacy"),
            "pending_how": {k: v for k, v in (issued.get("how") or {}).items() if k != "step"} or None,
            "mcq_map": {k: o["id"] for k, o in ((issued.get("mcq") or {}).get("options") or {}).items()}}


def told(result: dict) -> list[dict]:
    """What the chatbot is told to do, step by step: move, cue, and the data fields it must use."""
    out = []
    for s in result.get("plan", []):
        d = s.get("data", {})
        keep = {k: d[k] for k in ("skill", "level", "task", "features", "pattern", "purpose", "options", "correct",
                                  "correct_option", "misconceptions", "intuition", "asked", "trusted_sources",
                                  "answer_type", "extra_option", "name", "note") if k in d}
        out.append({"move": s["move"], "part_id": s.get("part_id"), "cue": s.get("cue"), **keep})
    return out


async def scenario(name: str, spec: dict, code: Path, label: str, port: int, out_dir: Path) -> dict:
    data = Path(f"/tmp/claude-1000/w4-fix-verify/data/{label}-{name}")
    shutil.rmtree(data, ignore_errors=True)
    data.mkdir(parents=True)
    env = {**os.environ, "EDUX_DATA_DIR": str(data), "PYTHONPATH": str(code), "PYTHONDONTWRITEBYTECODE": "1"}
    load_out = run(code, env, "edux.cli", "load", "coursepacks/example-mini")
    seed_out = run(code, env, "edux.cli", "seed-demo", "--reset")
    os.environ["EDUX_DATA_DIR"] = str(data)
    for mod in [m for m in sys.modules if m == "edux" or m.startswith("edux.") or m.startswith("ingest")]:
        del sys.modules[mod]
    sys.path.insert(0, str(code))
    from edux import learner, graph, context_blocks  # noqa: E402  (the copy's code, this scenario's data)
    sys.path.pop(0)
    student = spec.get("student", "demo-weak")
    key = learner.get_student(student)["key"]
    server = Server(code, env, port)
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    record = {"scenario": name, "label": label, "about": spec["about"], "student": student,
              "load": load_out.strip().splitlines()[-3:], "turns": []}
    try:
        async with streamablehttp_client(f"http://127.0.0.1:{port}/mcp?key={key}") as (r, w, _), ClientSession(r, w) as s:
            init = await s.initialize()
            record["server_instructions_words"] = len((init.instructions or "").split())
            if name == spec.get("dump_instructions_as", ""):
                (out_dir / "server_instructions.txt").write_text(init.instructions or "")
            for i, t in enumerate(spec["turns"]):
                time.sleep(1.1)   # events are stamped to the second
                before = snapshot(learner, graph, context_blocks, student)
                ev_before = learner._conn().execute("SELECT COALESCE(MAX(id),0) FROM evidence_log").fetchone()[0]
                n_lines = len(server.lines)
                if t.get("tool") == "get_my_progress":
                    args = {}
                    tool = "get_my_progress"
                else:
                    tool = "tutor_turn"
                    args = {"message": t.get("message", ""), "client": "claude", "this_message": t["labels"]}
                    if "node_ids" in t:
                        args["node_ids"] = t["node_ids"]
                    if "answer" in t:
                        a = dict(t["answer"])
                        if "pick" in a:   # the letter of a given option id (or 'correct') in the stored map
                            want = a.pop("pick")
                            found = next((k for k, v in before["mcq_map"].items() if v == want), None)
                            if found is None:   # the check never appeared: the driver can't pick it
                                record["turns"].append({"n": i + 1, "shot": t.get("shot"), "tool": "skipped",
                                                        "moves": None, "note": f"no pending option {want}: the check did not fire",
                                                        "before": before})
                                continue
                            a["choice"] = found
                        args["answer"] = a
                        if tool == "tutor_turn" and a.get("type") == "mcq":
                            args["message"] = a["choice"]
                t0 = time.perf_counter()
                res = await s.call_tool(tool, args)
                wall = (time.perf_counter() - t0) * 1000
                payload = (res.structuredContent or {}).get("result", res.structuredContent) if res.structuredContent \
                    else json.loads(res.content[0].text)
                time.sleep(0.05)
                after = snapshot(learner, graph, context_blocks, student)
                evid = [dict(e) for e in learner._conn().execute(
                    "SELECT part_id, evidence_type, score, point_id FROM evidence_log WHERE student_id = ? AND id > ? ORDER BY id",
                    (student, ev_before))]
                record["turns"].append({
                    "n": i + 1, "shot": t.get("shot"), "tool": tool, "sent": args,
                    "moves": [st["move"] + (":" + st["data"].get("purpose", "") if st["move"] == "ask_mcq" else "")
                              for st in payload.get("plan", [])] if tool == "tutor_turn" else None,
                    "told": told(payload) if tool == "tutor_turn" else None,
                    "result_chars": len(json.dumps(payload, ensure_ascii=False, separators=(",", ":"))),
                    "console": server.lines[n_lines:],
                    "wall_ms": round(wall, 1),
                    "evidence": evid, "before": before, "after": after, "result": payload})
    finally:
        server.stop()
    ms = learner._conn().execute("SELECT tool, ms, result_chars, over_budget FROM call_log WHERE student_id = ?",
                                 (student,)).fetchall()
    record["call_log"] = [dict(m) for m in ms]
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--scenario", nargs="*")
    a = ap.parse_args()
    assert str(a.code.resolve()).startswith("/tmp/claude-1000/w4-fix-verify/"), "run only against a copy"
    a.out.mkdir(parents=True, exist_ok=True)
    for name, spec in SCENARIOS.items():
        if a.scenario and name not in a.scenario:
            continue
        rec = asyncio.run(scenario(name, spec, a.code.resolve(), a.label, a.port, a.out))
        (a.out / f"{a.label}__{name}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False))
        print(f"{a.label} {name}: " + " | ".join(
            f"{t['n']}:{','.join(t['moves']) if t['moves'] is not None else t['tool']}" for t in rec["turns"]))


if __name__ == "__main__":
    main()
