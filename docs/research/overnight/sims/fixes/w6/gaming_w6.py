"""w6-fix-counters: sims/gaming/gaming_sim.py plus two adaptive gamers that target the counter alternatives.

  C3t  teach_match   "teach me <part>" (no "just show me"), never reads, picks the option that repeats the point the
                     teach_point just showed; never writes an explain-back (moves to the next part). Targets counters that
                     only look at "just show me".
  C3x  show_paste    as C3 ("just show me" + match), but at an explain-back or extend pastes the shown point back
                     (literal labeller ticks every point; skeptical ticks none). Targets counters that exempt open answers.
L1c  check_once    one real check (all four points, real effort) on the first verify task, then "the link is broken"
                     on every later one. Targets report rules that lift the cap after one real check.
Everything else (strategies, effort, truth model, labellers, metrics, CLI) is gaming_sim.py unchanged: course_run is
rebuilt from its own source with the two strategies added (asserts every anchor is found once).
    PYTHONPATH=<code copy> python gaming_w6.py --code <copy> --data /tmp/claude-1000/... --only C3t,C3x --out x.json
"""
import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gaming"))
import gaming_sim as G  # noqa: E402

src = inspect.getsource(G.course_run)
EDITS = [
    ('"C3": "just_show_me"}', '"C3": "just_show_me", "C3x": "just_show_me"}'),
    ('            elif strategy == "C3":\n                from edux.plan import option_form',
     '            elif strategy in ("C3", "C3t", "C3x"):\n                from edux.plan import option_form'),
    ('        elif strategy == "C3":   # never explains',
     '''        elif strategy == "C3t" or (strategy == "C3x" and step["move"] not in ("explain_back", "extend")):
            L = sim.learner   # no explain-back: next part (C3x: a reteach restarts with "just show me")
            if strategy == "C3x":
                st.say("just show me", "ask_topic", {"choice": "just_show_me"}, node_ids=[part])
                continue
            st.counts["dodged"] += 1
            queue = queue[1:] + queue[:1]
            current = queue[0]
            st.say(f"Teach me {current}", "ask_topic", node_ids=[current])
        elif strategy == "C3x":   # pastes the shown point(s) back; once secure, next part
            L = sim.learner
            if st.counts[f"pasted_{part}"] >= 2 or L.level(L.part_p(st.sid, part, iso(st.t))) == "secure":
                queue = queue[1:] + queue[:1]
                current = queue[0]
                st.say("just show me", "ask_topic", {"choice": "just_show_me"}, node_ids=[current])
                continue
            st.counts[f"pasted_{part}"] += 1
            st.say("<the shown point pasted back>", "explain_copy",
                   answer={"part_id": part, "type": atype, "points_met": letters if st.labeller == "literal" else []})
        elif strategy == "C3":   # never explains'''),
]
for old, new in EDITS:
    assert src.count(old) == 1, old
    src = src.replace(old, new)
ns = vars(G)
exec(compile(src, G.__file__ + ":course_run_w6", "exec"), ns)

lsrc = inspect.getsource(G.literacy_run)
LEDITS = [
    ("""            elif strategy == "L1":
                st.say("the link is broken\"""",
     """            elif strategy == "L1c" and not st.counts["did_check"]:
                st.counts["did_check"] = 1
                st.say("I checked the source ...", "verify_real",
                       answer={"part_id": "ail_verify", "type": "ail_task", "points_met": list("abcd")})
            elif strategy in ("L1", "L1c"):
                st.say("the link is broken\""""),
]
for old, new in LEDITS:
    assert lsrc.count(old) == 1, old
    lsrc = lsrc.replace(old, new)
lsrc = lsrc.replace('("L1", "L1d", "L2", "L3", "L4")', '("L1", "L1c", "L1d", "L2", "L3", "L4")')
exec(compile(lsrc, G.__file__ + ":literacy_run_w6", "exec"), ns)

if __name__ == "__main__":
    G.main()
