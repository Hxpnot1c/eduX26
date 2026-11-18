"""Command line: python -m edux.cli load | add-student | set-profile | log | evidence | state | sessions | context | calls | rebuild | serve | seed-demo."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from edux import graph, learner


def cmd_load(pack: Path) -> int:
    """Load a course pack into content.db (delegates to ingest)."""
    from ingest import cli as ingest_cli

    return ingest_cli.cmd_load(pack)


def cmd_rebuild(student: str | None = None) -> int:
    """Rebuild derived state for one student, or all."""
    if student:
        if learner.get_student(student) is None:
            print(f"unknown student {student!r}", file=sys.stderr)
            return 1
        print(f"{student}: replayed {learner.rebuild_state(student)} event(s)")
    else:
        counts = learner.rebuild_all()
        for student_id, n in counts.items():
            print(f"{student_id}: replayed {n} event(s)")
        print(f"rebuilt {len(counts)} student(s)")
    return 0


def cmd_add_student(name: str, course: str, profile: str | None = None) -> int:
    """Create a student and print their key."""
    try:
        created = learner.add_student(name, course, profile)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    print(f"student: {created['id']}")
    print(f"key:     {created['key']}")
    return 0


def cmd_log(student: str, nodes: list[str], depth: str, engagement: str, offloading: bool = False,
            support: str | None = None, choice: str | None = None, misconceptions: list[str] | None = None,
            ts: str | None = None, evidence: list[dict] | None = None) -> int:
    """Record one exchange (and any evidence with it) by hand and apply it straight away."""
    try:
        event_id = learner.record_exchange(student, nodes, depth, engagement, offloading, support, choice,
                                           misconceptions, ts=ts, client="cli", evidence=evidence, apply="now")
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    print(f"logged exchange {event_id}" + (f" with {len(evidence)} evidence item(s)" if evidence else ""))
    return 0


def cmd_evidence(student: str, part: str, evidence_type: str, score: float, ts: str | None = None,
                 misconceptions: list[str] | None = None) -> int:
    """Record evidence with no exchange by hand and apply it straight away."""
    try:
        ids = learner.record_evidence(student, part, evidence_type, score, misconceptions, ts=ts, apply="now")
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    print(f"logged evidence {', '.join(map(str, ids))}")
    return 0


def _priority_lines(student: str, at: str | None) -> list[str]:
    """Upcoming assessments and the top three due reviews by expected marks (priorities). CLI only."""
    lines = [f"assessment {a['id']}: {a['name']} ({a['kind']}) on {a['date']}, {len(a['part_ids'])} parts"
             for a in learner.assessments(student, at)] or ["assessments: none upcoming"]
    chance = learner.move_chance(student, "mcq_check", at)
    valued = sorted(((learner.step_value(student, r["part_id"], chance, at), r["part_id"])
                     for r in learner.due_reviews(student, 10_000, at)), key=lambda v: -v[0]["value"])
    for found, part in valued[:3]:
        why = f" ({learner.reason_text(found['reason'], at)})" if found["reason"] else ""
        lines.append(f"candidate review {part}: value {found['value']:.4f}{why}")
    return lines


def _learning_line(student: str, at: str | None) -> str:
    """The personal learning-rate offset for the current (or next) session: CLI only, never shown to students or
    teachers (personal-learning-rate)."""
    if not learner.personalisation_on():
        return "learning rate: personalisation off"
    session = learner.session_state(student, at)
    found = learner.learning_offset(student, session["session_id"] if session else at)
    return (f"learning rate: offset {found['offset']:+.2f} log-odds (x{found['weight']:.2f} odds) "
            f"from n={found['n']} pieces of evidence")


def cmd_state(student: str, node: str | None = None, at: str | None = None) -> int:
    """Print parts with p_now, level and due date."""
    if learner.get_student(student) is None:
        print(f"unknown student {student!r}", file=sys.stderr)
        return 1
    if node and graph.get_node(node) is None:
        print(f"unknown node {node!r}", file=sys.stderr)
        return 1
    conn = learner._conn()
    states = {r["part_id"]: r for r in conn.execute("SELECT * FROM part_state WHERE student_id = ?", (student,))}
    reviews = {r["part_id"]: r for r in conn.execute("SELECT * FROM review_queue WHERE student_id = ?", (student,))}
    roots = [graph.get_node(node)] if node else graph.topics()

    print(_session_line(learner.session_state(student, at)))
    print(_learning_line(student, at))
    for line in _priority_lines(student, at):
        print(line)
    print(f"{'part':24} {'level':10} {'p_now':>5} {'p_known':>7} {'half-life':>9} {'checks':>6} {'chats':>5}  "
          f"{'last correct':12} review due")
    for root in roots:
        print(f"{root['name']} ({root['level']}): {learner.rollup(student, root['id'], at):.2f}")
        for part in graph.parts_of(root["id"]):
            p = learner.part_p(student, part, at)
            state, review = states.get(part), reviews.get(part)
            if state:
                numbers = (f"{state['p_known']:7.2f} {state['half_life_days']:8.1f}d {state['n_evidence']:6d} "
                           f"{state['exchanges_since_evidence']:5d}  {(state['last_correct'] or '-')[:10]:12}")
            else:
                numbers = f"{'-':>7} {'-':>9} {'-':>6} {'-':>5}  {'-':12}"
            due = f"{review['due'][:16].replace('T', ' ')} ({review['reason']})" if review else "-"
            print(f"  {part:22} {learner.level(p):10} {p:5.2f} {numbers} {due}")
    return 0


def _share(value: float | None) -> str:
    return "-" if value is None else f"{value:.0%}"


def _session_line(session: dict | None) -> str:
    if session is None:
        return "session: none in progress"
    parts = [f"session: started {session['session_id'][:16].replace('T', ' ')}, {session['minutes']:.0f} min",
             f"{session['n_evidence']} evidence"]
    if session["rolling_surprise"] is not None:
        parts.append(f"rolling surprise {session['rolling_surprise']:+.2f}")
    if session["fatigued"]:
        parts.append(f"FATIGUED since minute {session['fatigued_since_minute']:.0f}")
    if session["stuck_parts"]:
        parts.append("stuck on " + ", ".join(p["part_id"] for p in session["stuck_parts"]))
    parts.append(f"just-show-me {_share(session['just_show_me_share'])}, surface {_share(session['surface_share'])}")
    return " | ".join(parts)


def cmd_sessions(student: str) -> int:
    """List a student's sessions with their length, evidence and fatigue onset."""
    if learner.get_student(student) is None:
        print(f"unknown student {student!r}", file=sys.stderr)
        return 1
    print(f"{'started':17} {'minutes':>7} {'exchanges':>9} {'evidence':>8}  fatigue from")
    for s in learner.sessions(student):
        onset = "-" if s["fatigue_onset_minute"] is None else f"minute {s['fatigue_onset_minute']:.0f}"
        print(f"{s['session_id'][:16].replace('T', ' '):17} {s['minutes']:7.0f} {s['n_exchanges']:9d} {s['n_evidence']:8d}  {onset}")
    return 0


def cmd_context(student: str, message: str, nodes: list[str] | None = None) -> int:
    """Print the context blocks for a message as JSON, numbers included (for debugging; reads only, records nothing)."""
    import json

    from edux import service

    found = learner.get_student(student)
    if found is None:
        print(f"unknown student {student!r}", file=sys.stderr)
        return 1
    print(json.dumps(service.learning_context(found, message, nodes), indent=2))
    return 0


def cmd_calls(student: str | None = None, last: int = 20) -> int:
    """Recent tool calls; per tool the median and 90th-percentile server time, the median and largest result
    size and the over-budget count; and the median gap between a student's consecutive calls."""
    from edux import service

    if student and learner.get_student(student) is None:
        print(f"unknown student {student!r}", file=sys.stderr)
        return 1
    stats = service.call_stats(student, last)
    print(f"{'time':23} {'student':12} {'tool':18} {'ms':>7} {'chars':>7}  result")
    for r in stats["recent"]:
        result = ("ok" if r["ok"] else f"error: {r['error']}") + (" OVER BUDGET" if r["over_budget"] else "")
        print(f"{r['ts'][:23].replace('T', ' '):23} {r['student_id'] or '-':12} {r['tool']:18} {r['ms']:7.1f} "
              f"{r['result_chars']:7d}  {result}")
    print()
    print(f"{'tool':18} {'calls':>5} {'median ms':>9} {'p90 ms':>7} {'median chars':>12} {'max chars':>9} {'over budget':>11}")
    for tool, t in stats["tools"].items():
        print(f"{tool:18} {t['calls']:5d} {t['median_ms']:9.1f} {t['p90_ms']:7.1f} {t['median_chars']:12.0f} "
              f"{t['max_chars']:9d} {t['over_budget']:11d}")
    if stats["gaps"]:
        print()
        print(f"{'student':12} median gap between calls")
        for student_id, gap in sorted(stats["gaps"].items()):
            print(f"{student_id:12} {gap:.1f}s")
    return 0


def cmd_set_profile(student: str, profile: str) -> int:
    """Switch a student's context profile ("default" goes back to the default in context.toml)."""
    try:
        learner.set_profile(student, None if profile == "default" else profile)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    print(f"{student}: profile {learner.profile_of(learner.get_student(student))}")
    return 0


def cmd_serve(host: str | None = None, port: int | None = None) -> int:
    """Start the MCP server at http://<host>:<port>/mcp (HOST and PORT from the environment by default)."""
    from edux import server

    host = host or os.environ.get("HOST", "127.0.0.1")
    port = port or int(os.environ.get("PORT", "8000"))
    print(f"serving MCP at http://{host}:{port}/mcp?key=<student key>")
    server.serve(host, port)
    return 0


def cmd_seed_demo(course: str | None = None, reset: bool = False, parts: str | None = None) -> int:
    """Create the three demo students by replaying scripted events; print the roles picked and their keys."""
    from edux import demo

    try:
        result = demo.seed(course, reset, parts)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    print(f"course: {result['course']}")
    for role in demo.ROLES:
        value = result["roles"][role]
        print(f"  {role:14} {', '.join(value) if isinstance(value, list) else value or '-'}")
    for warning in result["warnings"]:
        print(f"warning: {warning}")
    host, port = os.environ.get("HOST", "127.0.0.1"), os.environ.get("PORT", "8000")
    for student_id, key in result["students"].items():
        print(f"{student_id:12} key {key}   http://{host}:{port}/mcp?key={key}")
    return 0


def _list(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def _evidence(value: str) -> dict:
    """part_id:type:score -> an evidence item."""
    try:
        part_id, evidence_type, score = value.split(":")
        return {"part_id": part_id, "type": evidence_type, "score": float(score)}
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected part_id:type:score, got {value!r}") from None


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and run a command."""
    parser = argparse.ArgumentParser(prog="python -m edux.cli", description="Synapse command line: load a course pack, manage students, inspect and rebuild the learner model, run the server.")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("load", help="load a course pack into content.db")
    p.add_argument("pack", type=Path)
    p = sub.add_parser("add-student", help="create a student and print their key")
    p.add_argument("--name", required=True)
    p.add_argument("--course", required=True)
    p.add_argument("--profile", help="context profile (default from context.toml)")
    p = sub.add_parser("set-profile", help="switch a student's context profile")
    p.add_argument("--student", required=True)
    p.add_argument("--profile", required=True, help="a profile in context.toml, or 'default'")
    p = sub.add_parser("log", help="record an exchange by hand")
    p.add_argument("--student", required=True)
    p.add_argument("--nodes", required=True, type=_list, help="comma-separated part or concept ids")
    p.add_argument("--depth", required=True, help="surface / mechanism / transfer")
    p.add_argument("--engagement", required=True, help="passive / active / constructive")
    p.add_argument("--offloading", action="store_true")
    p.add_argument("--support", help="worked_example / hint / explain_back / none")
    p.add_argument("--choice", help="try_first / hint / just_show_me / none")
    p.add_argument("--misconceptions", type=_list, help="comma-separated misconception ids")
    p.add_argument("--ts", help="ISO timestamp (default: now)")
    p.add_argument("--evidence", type=_evidence, action="append",
                   help="part_id:type:score, what the student produced this turn (repeatable)")
    p = sub.add_parser("evidence", help="record evidence by hand, with no exchange")
    p.add_argument("--student", required=True)
    p.add_argument("--part", required=True, help="part or concept id")
    p.add_argument("--type", required=True, help="a key of [bkt.evidence], e.g. explain_back")
    p.add_argument("--score", required=True, type=float, help="0–1")
    p.add_argument("--ts", help="ISO timestamp (default: now)")
    p.add_argument("--misconceptions", type=_list, help="comma-separated misconception ids")
    p = sub.add_parser("state", help="show a student's parts")
    p.add_argument("--student", required=True)
    p.add_argument("--node", help="only parts under this node")
    p.add_argument("--at", help="ISO timestamp to read decay at (default: now)")
    p = sub.add_parser("sessions", help="list a student's sessions")
    p.add_argument("--student", required=True)
    p = sub.add_parser("context", help="print the context blocks for a message (debugging; records nothing)")
    p.add_argument("--student", required=True)
    p.add_argument("--message", required=True)
    p.add_argument("--nodes", type=_list, help="comma-separated part or concept ids")
    p = sub.add_parser("calls", help="tool call timing: recent calls, per-tool median and p90, gaps per student")
    p.add_argument("--student")
    p.add_argument("--last", type=int, default=20, help="recent calls to list (default 20)")
    p = sub.add_parser("rebuild", help="replay events into derived state")
    p.add_argument("--student")
    p = sub.add_parser("seed-demo", help="create the three demo students from scripted events")
    p.add_argument("--course", help="course id (default: the only loaded course)")
    p.add_argument("--reset", action="store_true", help="remove the demo students and their events first")
    p.add_argument("--parts", help="override roles, e.g. target=ped_values,prereq=ped_formula "
                                   "(review_parts and showme_parts take ;-separated ids)")
    p = sub.add_parser("serve", help="start the MCP server")
    p.add_argument("--host", help="default: HOST from the environment, else 127.0.0.1")
    p.add_argument("--port", type=int, help="default: PORT from the environment, else 8000")
    args = parser.parse_args(argv)

    if args.command == "load":
        code = cmd_load(args.pack)
    elif args.command == "add-student":
        code = cmd_add_student(args.name, args.course, args.profile)
    elif args.command == "set-profile":
        code = cmd_set_profile(args.student, args.profile)
    elif args.command == "log":
        code = cmd_log(args.student, args.nodes, args.depth, args.engagement, args.offloading, args.support,
                       args.choice, args.misconceptions, args.ts, args.evidence)
    elif args.command == "evidence":
        code = cmd_evidence(args.student, args.part, args.type, args.score, args.ts, args.misconceptions)
    elif args.command == "state":
        code = cmd_state(args.student, args.node, args.at)
    elif args.command == "sessions":
        code = cmd_sessions(args.student)
    elif args.command == "context":
        code = cmd_context(args.student, args.message, args.nodes)
    elif args.command == "calls":
        code = cmd_calls(args.student, args.last)
    elif args.command == "seed-demo":
        code = cmd_seed_demo(args.course, args.reset, args.parts)
    elif args.command == "serve":
        code = cmd_serve(args.host, args.port)
    else:
        code = cmd_rebuild(args.student)
    sys.exit(code)


if __name__ == "__main__":
    main()
