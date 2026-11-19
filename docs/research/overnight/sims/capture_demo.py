"""Capture real eduX outputs for the demo storyboard (w1-07), offline, through the service layer.

Run from the worktree root:
    EDUX_DATA_DIR=/tmp/claude-1000/edux-demo-capture PYTHONPATH=. /home/vishnu/edux26/.venv/bin/python \
        docs/research/overnight/sims/capture_demo.py docs/research/overnight/sims/demo-captures

It loads example-mini into a fresh data folder, seeds the three demo students, then for each student:
  1. tutor_turn on the same question ("How do I calculate price elasticity of demand?")
  2. answers the MCQ it gets (wrong letter first, to show the misconception path), then the next one right
  3. records the target part's p_now / level before and after (what the learner model did)
  4. get_my_progress
plus a "just show me" turn for demo-showme and a minimal-profile comparison for demo-weak.
Timing per call is recorded. No AI model is called: the 'chatbot' labels are hard-coded here.
"""
from __future__ import annotations

import json
import os
import socket
import sys
import time
from pathlib import Path

assert os.environ.get("EDUX_DATA_DIR", "").startswith("/tmp/claude-1000/"), "use a temporary EDUX_DATA_DIR"

# Prove no network is used: any socket connect raises.
_real_connect = socket.socket.connect
NET_ATTEMPTS: list[str] = []
def _no_net(self, addr):  # noqa: E302
    NET_ATTEMPTS.append(repr(addr))
    raise OSError("network disabled by capture_demo.py")
socket.socket.connect = _no_net  # type: ignore[assignment]

from edux import cli, demo, learner, service  # noqa: E402

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "demo-captures")
OUT.mkdir(parents=True, exist_ok=True)
Q = "How do I calculate price elasticity of demand?"
LABELS = {"question_depth": "mechanism", "engagement": "active"}
TIMINGS: list[dict] = []


def dump(name: str, obj) -> None:
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def turn(sid: str, label: str, **kw) -> dict:
    t0 = time.perf_counter()
    out = service.tutor_turn(learner.get_student(sid), client="claude", **kw)
    ms = (time.perf_counter() - t0) * 1000
    TIMINGS.append({"student": sid, "call": label, "ms": round(ms, 1), "chars": len(json.dumps(out))})
    return out


def mcq_map(sid: str) -> dict:
    row = learner._conn().execute("SELECT plan_json FROM issued_plan WHERE student_id = ?", (sid,)).fetchone()
    return (json.loads(row[0]).get("mcq") or {}) if row else {}


def pick(sid: str, right: bool) -> tuple[str | None, str | None, str | None]:
    m = mcq_map(sid)
    for k, o in sorted((m.get("options") or {}).items()):
        if (o["id"] == "correct") == right and o["id"] != "extra":
            return k, o["id"], m.get("part_id")
    return None, None, m.get("part_id")


def snapshot(sid: str, parts: list[str]) -> dict:
    out = {}
    for p in parts:
        if p:
            v = learner.part_p(sid, p)
            out[p] = {"p_now": round(v, 3), "level": learner.level(v)}
    act = learner._conn().execute(
        "SELECT misconception_id, active FROM student_misconception WHERE student_id = ?", (sid,)).fetchall()
    out["misconceptions_active"] = sorted(r[0] for r in act if r[1])
    return out


def progress(sid: str) -> dict:
    t0 = time.perf_counter()
    out = service.my_progress(learner.get_student(sid))
    TIMINGS.append({"student": sid, "call": "get_my_progress", "ms": round((time.perf_counter() - t0) * 1000, 1),
                    "chars": len(json.dumps(out))})
    return out


def cli_state(sid: str, name: str) -> None:
    """What `python -m edux.cli state --student <sid>` prints: the on-screen view of the learner model."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cli.cmd_state(sid)
    (OUT / name).write_text(buf.getvalue())


def main() -> None:
    assert cli.cmd_load(Path("coursepacks/example-mini")) in (0, None)
    seeded = demo.seed(reset=True)
    roles = seeded["roles"]
    dump("00_seed_roles.json", {"course": seeded["course"], "roles": roles, "warnings": seeded["warnings"],
                                "students": list(seeded["students"])})   # keys deliberately not saved
    target = roles["target"]
    watch = [target, roles["prereq"], roles["anchor"]]

    summary = {}
    for sid in demo.STUDENTS:
        log = {"student": sid}
        log["before"] = snapshot(sid, watch)
        cli_state(sid, f"{sid}_state_before.txt")
        first = turn(sid, "same question", message=Q, this_message=LABELS)
        log["1_same_question"] = first
        letter, opt, part = pick(sid, right=False)
        log["mcq_map_after_turn1"] = mcq_map(sid)
        if letter:
            time.sleep(1.1)
            second = turn(sid, "wrong letter", message=letter, this_message=LABELS,
                          answer={"part_id": part, "type": "mcq", "choice": letter})
            log["2_wrong_letter"] = {"letter": letter, "option_id": opt, "part_id": part, "result": second}
            log["after_wrong"] = snapshot(sid, watch + [part])
            letter2, opt2, part2 = pick(sid, right=True)
            if letter2:
                time.sleep(1.1)
                third = turn(sid, "right letter", message=letter2, this_message=LABELS,
                             answer={"part_id": part2, "type": "mcq", "choice": letter2})
                log["3_right_letter"] = {"letter": letter2, "option_id": opt2, "part_id": part2, "result": third}
                log["after_right"] = snapshot(sid, watch + [part, part2])
        cli_state(sid, f"{sid}_state_after.txt")
        log["progress"] = progress(sid)
        dump(f"{sid}.json", log)
        summary[sid] = {
            "turn1_moves": [(s["move"], s.get("data", {}).get("purpose")) for s in first.get("plan", [])],
            "turn2_moves": [(s["move"], s.get("data", {}).get("purpose")) for s in
                            log.get("2_wrong_letter", {}).get("result", {}).get("plan", [])],
            "turn3_moves": [(s["move"], s.get("data", {}).get("purpose")) for s in
                            log.get("3_right_letter", {}).get("result", {}).get("plan", [])],
            "before": log["before"], "after_wrong": log.get("after_wrong"), "after_right": log.get("after_right"),
        }

    # Re-seed so the extras start from the seeded state
    demo.seed(reset=True)
    extras = {}
    time.sleep(1.1)
    extras["showme_just_show_me"] = turn("demo-showme", "just show me", message="Just show me how to calculate PED",
                                         this_message={**LABELS, "choice": "just_show_me", "engagement": "passive"})
    time.sleep(1.1)
    extras["showme_review_prompt"] = turn("demo-showme", "quiz me on what's due", message="Quiz me on what's due",
                                          this_message=LABELS)
    learner.set_profile("demo-weak", "minimal")
    extras["weak_minimal_profile"] = turn("demo-weak", "same question, minimal profile", message=Q, this_message=LABELS)
    learner.set_profile("demo-weak", None)
    time.sleep(1.1)
    extras["secure_conflict_flagged"] = turn("demo-secure", "chatbot self-corrects",
                                             message="Wait, you said earlier PED uses the new price?",
                                             node_ids=[target], this_message={**LABELS, "conflict_flagged": True})
    extras["bad_label_refused"] = turn("demo-secure", "bad label", message=Q,
                                       this_message={"question_depth": "deep", "engagement": "active"})
    dump("extras.json", extras)

    # Variants: other first messages on fresh seeds, looking for a three-way difference.
    variants = {}
    for msg in ("Quiz me on what's due.", "How do I interpret PED values?", "What should I work on next?"):
        demo.seed(reset=True)
        variants[msg] = {}
        for sid in demo.STUDENTS:
            out = turn(sid, f"variant: {msg}", message=msg, this_message=LABELS)
            variants[msg][sid] = out
    dump("variants.json", variants)
    print("VARIANTS")
    for msg, by in variants.items():
        for sid, out in by.items():
            print(f"  {msg!r:40} {sid:12}", [(s["move"], s["part_id"], s.get("data", {}).get("purpose"),
                                               s.get("data", {}).get("mode")) for s in out.get("plan", [])])

    dump("summary.json", {"question": Q, "roles": roles, "students": summary, "timings_ms": TIMINGS,
                          "network_connect_attempts": NET_ATTEMPTS})
    print(json.dumps(summary, indent=1))
    print("network attempts:", NET_ATTEMPTS)
    print("timings:", [(t["student"], t["call"], t["ms"], t["chars"]) for t in TIMINGS])


if __name__ == "__main__":
    main()
