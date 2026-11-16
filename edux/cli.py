"""Command line: python -m edux.cli load | add-student | log | state | rebuild | serve | seed-demo."""

from __future__ import annotations

import argparse
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
            ts: str | None = None) -> int:
    """Record one exchange by hand and apply it straight away."""
    try:
        event_id = learner.record_exchange(student, nodes, depth, engagement, offloading, support, choice,
                                           misconceptions, ts=ts, client="cli", apply="now")
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    print(f"logged exchange {event_id}")
    return 0


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


def cmd_serve(host: str | None = None, port: int | None = None) -> int:
    """Start the MCP server."""
    raise NotImplementedError


def cmd_seed_demo() -> int:
    """Create the demo students by replaying scripted events."""
    raise NotImplementedError


def _list(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and run a command."""
    parser = argparse.ArgumentParser(prog="python -m edux.cli")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("load", help="load a course pack into content.db")
    p.add_argument("pack", type=Path)
    p = sub.add_parser("add-student", help="create a student and print their key")
    p.add_argument("--name", required=True)
    p.add_argument("--course", required=True)
    p.add_argument("--profile", help="context profile (default from context.toml)")
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
    p = sub.add_parser("state", help="show a student's parts")
    p.add_argument("--student", required=True)
    p.add_argument("--node", help="only parts under this node")
    p.add_argument("--at", help="ISO timestamp to read decay at (default: now)")
    p = sub.add_parser("rebuild", help="replay events into derived state")
    p.add_argument("--student")
    args = parser.parse_args(argv)

    if args.command == "load":
        code = cmd_load(args.pack)
    elif args.command == "add-student":
        code = cmd_add_student(args.name, args.course, args.profile)
    elif args.command == "log":
        code = cmd_log(args.student, args.nodes, args.depth, args.engagement, args.offloading, args.support,
                       args.choice, args.misconceptions, args.ts)
    elif args.command == "state":
        code = cmd_state(args.student, args.node, args.at)
    else:
        code = cmd_rebuild(args.student)
    sys.exit(code)


if __name__ == "__main__":
    main()
