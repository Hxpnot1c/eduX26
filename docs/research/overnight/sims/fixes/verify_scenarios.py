"""Scenarios for the w4-fix-verify scoring fix: the wave-3 demo-05e scenarios plus the cases this fix targets.
Run with PYTHONPATH including ../demo-05e (for scenarios.py)."""
from scenarios import SCENARIOS as BASE, T1, T1P, T2C, T2R, T3C, T3S, T4_M1, T4_M2, OK, PROGRESS, SURF

SCENARIOS = {k: BASE[k] for k in ("clean", "conflict_as_verify_answer", "final", "final_ticks_ad",
                                  "recommended_no_verify_answer", "after_m2_ok", "no_source_conflict_label",
                                  "skip_4b", "clean_m1")}

VERIFY = lambda pts: {"part_id": "ail_verify", "type": "ail_task", "points_met": pts}
MATCHED = {"shot": "4c", "message": "I opened the ONS page, published by the ONS in Jan 2023: it says 9.1% too, so it matches.",
           "labels": {**SURF, "request_type": "other"}}
SCENARIOS.update({
    # dead page reported as the answer (a,d), then the student moves on twice: the w3 "0.30 -> 0.14" path
    "dead_ad_then_ok": {"about": "dead page answered with a,d, then 'ok' twice",
                        "turns": [T1, T2C, {**T3C, "answer": VERIFY(["a", "d"])}, T4_M2, OK, OK, PROGRESS]},
    # dead page reported with source_conflict but no answer, then moves on: the open task was scored 0 on the branch
    "dead_noanswer_then_ok": {"about": "dead page with source_conflict, no verify answer sent, then 'ok' twice",
                              "turns": [T1, T2C, T3C, T4_M2, OK, OK, PROGRESS]},
    # mismatch with all four ticks, for 3-vs-4 comparison against `final` (a,c,d)
    "final_ticks_abcd": {"about": "final, 4c ticked a,b,c,d", "turns": [T1P, T2R, {**T3S, "answer": VERIFY(["a", "b", "c", "d"])}, T4_M1, PROGRESS]},
    # an ordinary matching check (no conflict): 3 ticks vs 4 ticks
    "matched_abc_d": {"about": "page matches; answer a,b,c,d (no source_conflict)", "turns": [T1P, T2R, {**MATCHED, "answer": VERIFY(["a", "b", "c", "d"])}, PROGRESS]},
    "matched_acd": {"about": "page matches; answer a,c,d (restating-style: no publisher/date)", "turns": [T1P, T2R, {**MATCHED, "answer": VERIFY(["a", "c", "d"])}, PROGRESS]},
    # the verify task is ignored entirely (re-asked once, then ignored again)
    "verify_ignored": {"about": "verify task set, then the student says 'ok' three times",
                       "turns": [T1P, T2R, OK, OK, OK, PROGRESS]},
})

# a found problem sent as ail_unprompted (lower slip): must not make Verify secure in one message
UNP_A = {"part_id": "ail_verify", "type": "ail_unprompted", "points_met": ["a"]}
T3_DEAD_UNP = {**T3C, "answer": UNP_A}
SCENARIOS.update({
    "unprompted_dead_task_open": {"about": "verify task open; dead page sent as ail_unprompted ticked a only",
                                  "turns": [T1P, T2R, T3_DEAD_UNP, PROGRESS]},
    "unprompted_dead_no_task": {"about": "no verify task open (Ask task); dead page sent as ail_unprompted ticked a only",
                                "turns": [T1, T3_DEAD_UNP, PROGRESS]},
    "retake_same_session": BASE["retake_same_session"],
})
