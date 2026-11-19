"""Plan A turns and their variants. Labels are what a chatbot with web search OFF would send, per
text/tools/tutor_turn.md and the server instructions on the 05e branch. 'pick' names the option id whose
letter the student chooses (the driver looks the letter up in the stored map, as a viewer would read it off screen)."""

SURF = {"question_depth": "surface", "engagement": "active"}
MECH = {"question_depth": "mechanism", "engagement": "active"}

T1 = {"shot": "4a", "message": "what's happening with inflation?",
      "labels": {**SURF, "request_type": "research", "question_features": ["concept"], "web_access": False,
                 "asks_recent": False}}
T2 = {"shot": "4b", "message": "What happened to UK CPI inflation in 2025, and why? Please give me sources I can check.",
      "labels": {**MECH, "request_type": "research",
                 "question_features": ["concept", "context", "asks_sources", "asks_reasoning"],
                 "web_access": False, "asks_recent": False}}
T3 = {"shot": "4c", "message": "That ONS link doesn't work.",
      "labels": {**SURF, "request_type": "research", "source_conflict": True, "question_features": ["context"],
                 "web_access": False}}
T4_M2 = {"shot": "4c'", "answer": {"part_id": "ail_how_fabrication", "type": "mcq", "pick": "ail_how_fabrication_m2"},
         "labels": {**SURF, "request_type": "other"}}
T4_RIGHT = {"shot": "4c'", "answer": {"part_id": "ail_how_fabrication", "type": "mcq", "pick": "correct"},
            "labels": {**SURF, "request_type": "other"}}
PROGRESS = {"shot": "4d", "tool": "get_my_progress"}
OK = {"message": "ok", "labels": {"question_depth": "surface", "engagement": "passive", "request_type": "other"}}
PED = {"shot": "5", "message": "How do I calculate price elasticity of demand?",
       "labels": {**MECH, "request_type": "concept"}}


def with_labels(turn, **labels):
    return {**turn, "labels": {**turn["labels"], **labels}}


# Wording that resolves to no course part on example-mini (see probe_resolve.py): no "give", "link", "ONS", "first",
# "cost", "change" in the literacy lines, so no course focus is set and nothing course-related follows the check.
T2C = {**T2, "message": "What was UK CPI inflation in 2025, and why? Sources please."}
T2C_CAND = {**T2, "message": "What was UK CPI inflation in 2025, and why did it change? Sources please."}
T3C = {"shot": "4c", "message": "I clicked it and the page doesn't exist.",
       "labels": {**SURF, "request_type": "other", "source_conflict": True}}

STORY = [T1, T2, T3, T4_M2, PROGRESS]
CLEAN = [T1, T2C, T3C, T4_M2, PROGRESS]

SCENARIOS = {
    "as_written": {"about": "Plan A as written in demo-plan.md, check-script labels on the dead-link turn (research, [context])",
                   "turns": STORY, "dump_instructions_as": "as_written"},
    "clean": {"about": "Plan A with focus-safe wording and the dead-link turn labelled request_type other",
              "turns": CLEAN},
    "clean_candidates": {"about": "clean, but 4b worded so it matches two topics as candidates (brings the ONS trusted source)",
                         "turns": [T1, T2C_CAND, T3C, T4_M2, PROGRESS]},
    "clean_right_pick": {"about": "clean, student picks the correct option", "turns": [T1, T2C, T3C, T4_RIGHT, PROGRESS]},
    "clean_conflict_research": {"about": "clean wording but the dead-link turn labelled research with no features",
                                "turns": [T1, T2C, {**T3C, "labels": {**SURF, "request_type": "research", "source_conflict": True,
                                                                       "question_features": [], "web_access": False}}, T4_M2, PROGRESS]},
    "as_written_conflict_other": {"about": "as written wording ('That ONS link doesn't work.') but labelled other",
                                  "turns": [T1, T2, {**T3, "labels": {**SURF, "request_type": "other", "source_conflict": True}}, T4_M2, PROGRESS]},
    "recent_t1": {"about": "the chatbot honestly labels 'what's happening with inflation?' asks_recent (search off)",
                  "turns": [with_labels(T1, asks_recent=True), T2C, T3C, T4_M2, PROGRESS]},
    "recent_t2": {"about": "the chatbot labels the 2025 question asks_recent (search off)",
                  "turns": [T1, with_labels(T2C, asks_recent=True), T3C, T4_M2, PROGRESS]},
    "one_feature_rewrite": {"about": "the student does exactly what the Ask task says: adds only a place and time period",
                            "turns": [T1, {**T2C, "message": "What was UK inflation in 2025?",
                                           "labels": {**SURF, "request_type": "research", "question_features": ["concept", "context"],
                                                      "web_access": False, "asks_recent": False}}, T3C, T4_M2, PROGRESS]},
    "three_feature_rewrite": {"about": "rewrite with idea + place/time + sources but no 'why'",
                              "turns": [T1, {**T2C, "message": "What was UK CPI inflation in 2025? Sources please.",
                                             "labels": {**SURF, "request_type": "research",
                                                        "question_features": ["concept", "context", "asks_sources"],
                                                        "web_access": False, "asks_recent": False}}, T3C, T4_M2, PROGRESS]},
    "conflict_as_verify_answer": {"about": "chatbot also sends the dead-link line as the verify task's answer (opened it; says it didn't match)",
                                  "turns": [T1, T2C, {**T3C, "answer": {"part_id": "ail_verify", "type": "ail_task", "points_met": ["a", "d"]}},
                                            T4_M2, PROGRESS]},
    "no_source_conflict_label": {"about": "chatbot forgets source_conflict on the dead-link message",
                                 "turns": [T1, T2C, {**T3C, "labels": {**SURF, "request_type": "other"}}, PROGRESS]},
    "petrol": {"about": "petrol/PED-linked questions so the pack's trusted ONS source reaches the plan",
               "turns": [{**T1, "message": "how much does petrol cost?"},
                         {**T2, "message": "How did UK petrol prices change in 2025, and how did demand respond? Give sources and explain why."},
                         T3C, T4_M2, PROGRESS]},
    "search_on": {"about": "web search left ON (web_access true) for the whole episode",
                  "turns": [with_labels(T1, web_access=True), with_labels(T2C, web_access=True), T3C, T4_M2, PROGRESS]},
    "after_m2_ok": {"about": "clean, then the student says 'ok' twice (does the waiting verify task come back / score 0?)",
                    "turns": [T1, T2C, T3C, T4_M2, OK, OK, PROGRESS]},
    "retake_same_session": {"about": "a second take without reset, in the same session",
                            "turns": [T1, T2C, T3C, T4_M2, T1, T2C, T3C, PROGRESS]},
    "then_ped": {"about": "clean, then the PED question (expo order: literacy first, then PED)",
                 "turns": [T1, T2C, T3C, T4_M2, PED, PROGRESS]},
    "as_written_then_ped": {"about": "as written, then the PED question", "turns": [T1, T2, T3, T4_M2, PED, PROGRESS]},
    "skip_4b": {"about": "fallback: cut 4b, dead link straight after the Ask task", "turns": [T1, T3C, T4_M2, PROGRESS]},
}

# ---- wave-2 storyboard (demo-plan.md as edited after wave 2: mismatched source, never m2) ----
T4_M1 = {**T4_M2, "answer": {"part_id": "ail_how_fabrication", "type": "mcq", "pick": "ail_how_fabrication_m1"}}
T1R = {**T1, "message": "tell me about inflation"}
T2R = {**T2, "message": "What was UK CPI inflation in 2022, and why did it change? Sources please."}
T3R = {"shot": "4c", "message": "That page doesn't say that.", "labels": {**SURF, "request_type": "other", "source_conflict": True}}
T3R_ANS = {**T3R, "answer": {"part_id": "ail_verify", "type": "ail_task", "points_met": ["a", "c", "d"]}}
T3_NOW = {"shot": "4c", "message": "That ONS page doesn't give that figure.",
          "labels": {**SURF, "request_type": "other", "source_conflict": True}}
SCENARIOS.update({
    "plan_now": {"about": "demo-plan.md's current lines (4c 'That ONS page doesn't give that figure.'), pick m1, labelled other",
                 "turns": [T1, T2, T3_NOW, T4_M1, PROGRESS]},
    "recommended": {"about": "recommended takes: timeless vague 4a, 2022 question that brings the ONS source, mismatch line that is also the verify answer (a,c,d), pick m1",
                    "turns": [T1R, T2R, T3R_ANS, T4_M1, PROGRESS]},
    "recommended_no_verify_answer": {"about": "recommended, but the chatbot does not send the mismatch line as the verify answer",
                                     "turns": [T1R, T2R, T3R, T4_M1, PROGRESS]},
    "recommended_right": {"about": "recommended, with the right pick (the alternative ending)",
                          "turns": [T1R, T2R, T3R_ANS, T4_RIGHT, PROGRESS]},
    "clean_m1": {"about": "clean (dead page), pick m1 instead of m2", "turns": [T1, T2C, T3C, T4_M1, PROGRESS]},
})

# ---- after review: 4a wording and label, and a 4c line that states what the page says ----
T1P = {**T1, "message": "what was inflation like?"}
T3S = {"shot": "4c", "message": "I opened it and the page says 9.1%, not 11.1%.",
       "labels": {**SURF, "request_type": "other", "source_conflict": True}}
SCENARIOS.update({
    "final": {"about": "final shot list: past-tense vague 4a, 2022 4b, 4c states what the page says (verify answer a,c,d), pick m1",
              "turns": [T1P, T2R, {**T3S, "answer": {"part_id": "ail_verify", "type": "ail_task", "points_met": ["a", "c", "d"]}}, T4_M1, PROGRESS]},
    "final_ticks_ad": {"about": "final, but the chatbot ticks only a,d on the 4c verify answer",
                       "turns": [T1P, T2R, {**T3S, "answer": {"part_id": "ail_verify", "type": "ail_task", "points_met": ["a", "d"]}}, T4_M1, PROGRESS]},
    "t1_concept": {"about": "4a 'tell me about inflation' labelled request_type concept (course question), not research",
                   "turns": [{**T1R, "labels": {**SURF, "request_type": "concept"}}, T2R, T3R, T4_M1, PROGRESS]},
    "t1p_concept": {"about": "4a 'what was inflation like?' labelled concept",
                    "turns": [{**T1P, "labels": {**SURF, "request_type": "concept"}}, T2R, T3S, T4_M1, PROGRESS]},
})
