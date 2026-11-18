"""eduX unit economics on the Microsoft 365 Education + Copilot Studio route (w5-08u).

What the school pays per student per year = eduX licence + Microsoft Copilot Credits.
A first-principles model: no eduX code is imported, nothing is fetched. Run:

    python3 docs/research/overnight/sims/economics/unit_model.py

It writes results.md and results.json next to this file.

Labels: [w..] = a finding id in docs/research/overnight/findings.csv with its verifier mark;
"our choice" = a number we picked; "our estimate" = derived by this script.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent

# --- verified rates (findings.csv) --------------------------------------------------------
GBP_PER_CREDIT_PAYG = 0.0075          # [w3-08m-07 ✓] US$0.01, Azure GBP list
PACK_GBP, PACK_CREDITS = 153.80, 25_000   # [w3-08m-07 ✓] per month, no rollover (business plan §3)
PREPURCHASE_DISCOUNT = 0.20           # [w3-08m-07 ✓] "saves up to 20%": upper bound
CREDITS_PER_TOOL_CALL = 5             # [w3-08m-06 ✓] MCP tool invocation in the estimator
CREDITS_GENERATIVE = 2                # [w3-08m-05 ~] generative answer on the billing page
# A message to the eduX agent with no tool call may still bill a generative answer (2) or nothing (0):
# the estimator and the billing page read differently [w3-08m-05 ~, w3-08m-06 ✓]. Modelled as {0, 2}.
NON_CALL_CREDITS = (0, 2)

# --- eduX price (our choice; business plan §3) -------------------------------------------
PRICE_DEPT, PRICE_TRUST, MIN_DEPT = 5.0, 3.0, 100.0

# --- comparators ---------------------------------------------------------------------------
SPARX_PER_PUPIL = (1.80, 2.80)        # [w2-08-06 ✓] our estimate on an assumed trust headcount
CENTURY_ESSEX_INC_VAT_3Y = 68_850     # [w2-08-07 ✓] FE, English/maths/science, headcount not published
SENECA_SCHOOL_SYNC = 646              # [w1-08-07 ✓] per school per year ex VAT, >600 pupils
KHANMIGO_USD_YEAR = 44                # [w2-08-12 ✓] learner price, US; no UK offer
ICT_PER_PUPIL = 128                   # [w1-08-05 ✓] LA-maintained secondary ICT learning resources

# --- usage grid (our choice) ---------------------------------------------------------------
MSGS_PER_WEEK = (5, 10, 20, 40)
WEEKS = (20, 30, 38)
CREDITS_PER_CALLED_MSG = (5, 7, 12)   # 5 = one call; 7 = call + generative answer; 12 = two calls + gen.
WEEKS_PER_MONTH = 52 / 12


def cost_per_student(msgs_week: float, weeks: float, credits_per_msg: float, gbp_per_credit: float,
                     licence: float = PRICE_DEPT, licensed_share: float = 0.0) -> dict:
    """School cost per student per year. licensed_share: students whose credits are exempt IF the
    M365 Copilot licensed-user exemption applies to students (unclear, w3-08m-05 ~)."""
    credits = msgs_week * weeks * credits_per_msg * (1 - licensed_share)
    ms = credits * gbp_per_credit
    total = licence + ms
    return {"credits": credits, "microsoft": ms, "edux": licence, "total": total,
            "ms_share": ms / total if total else 0.0, "ms_over_edux": ms / licence if licence else float("inf")}


def pack_price(utilisation: float) -> float:
    """Effective £ per credit used from a monthly pack at a given fill (credits don't roll over)."""
    return PACK_GBP / (PACK_CREDITS * utilisation)


# --- the move structure (05d point-by-point loop, 05e research turns) ---------------------
# Every student message to the eduX agent costs one tutor_turn on the 05e branch ("Call tutor_turn at the
# start of every reply ... research questions about the world too"). The plan never needs a call without a
# student message: teach_point and its check go out in the same reply (plan.teach returns both; MAX_STEPS 3).
def message_mix(k: float = 3, p: float = 0.3, q: float = 1.0, research_share: float = 0.10,
                off_share: float = 0.10, tool_extra: float = 0.03, retry: float = 0.03) -> dict:
    """Messages per 100 student messages, by type. Per part (05d): one opening request, one intuition MCQ
    answer, k check answers, p*k re-check answers after a reteach (reteach_limit = 1), one explain-back
    answer, and q questions asked instead of answering (answer_brief + reask). k = points per part
    (settings points.warn_min..warn_max = 2..4). p, q and the shares are our choice."""
    per_part = {"opening": 1, "intuition_answer": 1, "check_answer": k, "recheck_answer": p * k,
                "explain_back_answer": 1, "midloop_question": q}
    loop_total = sum(per_part.values())
    loop_share = 1 - research_share - off_share
    mix = {t: 100 * loop_share * n / loop_total for t, n in per_part.items()}
    mix["research"] = 100 * research_share
    mix["off_course"] = 100 * off_share
    return {"mix": mix, "per_part": per_part, "msgs_per_part": loop_total,
            "extra_calls": 100 * tool_extra,   # get_my_progress / update_my_profile, each 5 credits
            "retry_calls": 100 * retry}        # {"ok": false} -> fix the field and call again


def options(m: dict) -> dict:
    """Calls avoided per 100 messages for each design option, and which messages lose their call."""
    mix = m["mix"]
    mcq_answers = mix["check_answer"] + mix["recheck_answer"]
    interrupt = mix["midloop_question"] / (mcq_answers + mix["midloop_question"])
    return {
        "A. no call on off-course turns (chit-chat, thanks)": {
            "skip_msgs": mix["off_course"], "evidence_lost": "session timing events only; no scored evidence",
            "fidelity_risk": "low"},
        "A+. also no call on research turns (main-branch 'about the course' wording)": {
            "skip_msgs": mix["off_course"] + mix["research"],
            "evidence_lost": "every Ask item and the Verify tasks: all AI-literacy evidence (05e)",
            "fidelity_risk": "fatal to the AI-literacy claim"},
        "B. no call on mid-loop questions (chatbot answers briefly, re-asks the pending question)": {
            "skip_msgs": mix["midloop_question"],
            "evidence_lost": "question_depth/engagement labels on those messages (trends); fatigue and stuck "
                             "checks run one turn later",
            "fidelity_risk": "low-medium"},
        "C. pre-branched plan: next step for each MCQ letter returned in advance (lookahead 1)": {
            # the intuition answer always leads to teaching (05d C.1), so its branch is free; on checks every
            # second consecutive MCQ answer is carried in the next call, unless a question breaks the run
            "skip_msgs": mix["intuition_answer"] + 0.5 * mcq_answers * (1 - interrupt),
            "evidence_lost": "none lost; scored one turn later. The answer key and both branches reach the "
                             "chatbot before the student answers",
            "fidelity_risk": "medium (integrity; fatigue/stuck one turn late; result ~2x larger)"},
        "C3. session plan every 3 MCQ answers (lookahead 2; 4 leaves)": {
            "skip_msgs": mix["intuition_answer"] + (2 / 3) * mcq_answers * (1 - interrupt) ** 2,
            "evidence_lost": "as C, up to two turns late; reteach choice made from a stale model",
            "fidelity_risk": "medium-high"},
        "D. fewer calls during explanation steps": {
            "skip_msgs": 0.0,
            "evidence_lost": "-", "fidelity_risk": "-"},
        "E. cut schema retries from 3% to 1% (simpler labels, examples in tool text)": {
            "skip_msgs": 0.0, "skip_calls": m["retry_calls"] - 1.0,
            "evidence_lost": "none", "fidelity_risk": "none"},
    }


def credits_per_100(m: dict, skip_msgs: float, non_call: float, skip_calls: float = 0.0,
                    per_call: float = CREDITS_PER_TOOL_CALL) -> float:
    """Credits per 100 student messages: called messages at per_call, uncalled at non_call (0 or 2),
    plus progress/profile calls and retries at 5 each."""
    called = 100 - skip_msgs
    extra = m["extra_calls"] + m["retry_calls"] - skip_calls
    return called * per_call + skip_msgs * non_call + extra * CREDITS_PER_TOOL_CALL


def main() -> None:
    out: dict = {}
    md: list[str] = ["# eduX unit model: results (w5-08u)", "",
                     "Generated by `unit_model.py`. All usage numbers are **our choice**; rates are cited by "
                     "finding id. School cost = eduX licence + Microsoft Copilot Credits, per student per year, "
                     "ex VAT, list prices.", ""]

    # 1. grid
    md += ["## 1. School cost per student per year (PAYG £0.0075/credit, £5 licence)", "",
           "| msgs/week | weeks | credits/msg | credits/yr | Microsoft £ | total £ | Microsoft share | MS ÷ eduX |",
           "|---|---|---|---|---|---|---|---|"]
    grid = []
    for mw, wk, cpm in itertools.product(MSGS_PER_WEEK, WEEKS, CREDITS_PER_CALLED_MSG):
        r = cost_per_student(mw, wk, cpm, GBP_PER_CREDIT_PAYG)
        grid.append({"msgs_week": mw, "weeks": wk, "credits_per_msg": cpm, **r})
        if wk == 30 or (mw == 20 and cpm == 5):
            md.append(f"| {mw} | {wk} | {cpm} | {r['credits']:,.0f} | {r['microsoft']:.2f} | {r['total']:.2f} | "
                      f"{r['ms_share']:.0%} | {r['ms_over_edux']:.1f}x |")
    out["grid"] = grid
    central = cost_per_student(20, 30, 5, GBP_PER_CREDIT_PAYG)
    out["central"] = central
    md += ["", f"Central (20 msgs/week × 30 weeks × 5 credits): Microsoft £{central['microsoft']:.2f}, total "
           f"£{central['total']:.2f}, Microsoft {central['ms_share']:.0%} of spend, "
           f"{central['ms_over_edux']:.1f}× eduX. Full grid (incl. 20 and 38 weeks) in results.json.", ""]

    # 2. break-evens
    per_call = CREDITS_PER_TOOL_CALL * GBP_PER_CREDIT_PAYG
    be = {
        "gbp_per_call": per_call,
        "calls_where_ms_equals_licence_5": PRICE_DEPT / per_call,
        "calls_where_ms_equals_licence_3": PRICE_TRUST / per_call,
        "calls_for_total_le_sparx_high_with_free_licence": SPARX_PER_PUPIL[1] / per_call,
        "calls_for_total_le_sparx_high_with_3_licence": max(0.0, SPARX_PER_PUPIL[1] - PRICE_TRUST) / per_call,
    }
    budgets = {}
    for b in (10, 15, 20, 30):
        budgets[b] = {lic: max(0.0, b - lic) / per_call for lic in (0, 3, 5)}
    be["max_calls_per_year_for_total_budget"] = budgets
    out["break_even"] = be
    md += ["## 2. Break-even and price points (5 credits/call, PAYG)", "",
           f"- One call costs the school £{per_call:.4f}.",
           f"- Microsoft's take equals the £5 licence at {be['calls_where_ms_equals_licence_5']:.0f} calls a "
           f"year ({be['calls_where_ms_equals_licence_5'] / 30:.1f} a week over 30 weeks); the £3 trust tier at "
           f"{be['calls_where_ms_equals_licence_3']:.0f} ({be['calls_where_ms_equals_licence_3'] / 30:.1f} a week).",
           f"- To keep the whole bill at or under Sparx's top estimate (£2.80) **with eduX free**, a student could "
           f"make only {be['calls_for_total_le_sparx_high_with_free_licence']:.0f} calls a year "
           f"({be['calls_for_total_le_sparx_high_with_free_licence'] / 30:.1f} a week). At the £3 trust tier, none: "
           f"£3 alone is above £2.80.", "",
           "Max calls per student per year that fit a total budget (our choice of budgets):", "",
           "| total budget £/student/yr | eduX free | eduX £3 | eduX £5 | at £5: per week over 30 weeks |",
           "|---|---|---|---|---|"]
    for b, row in budgets.items():
        md.append(f"| {b} | {row[0]:.0f} | {row[3]:.0f} | {row[5]:.0f} | {row[5] / 30:.1f} |")
    md.append("")

    # 3. credit price: PAYG vs pre-purchase vs pack, and pack fill
    months_central = 30 / WEEKS_PER_MONTH
    cred_month_central = central["credits"] / months_central
    pack = {
        "payg": GBP_PER_CREDIT_PAYG,
        "prepurchase_best": GBP_PER_CREDIT_PAYG * (1 - PREPURCHASE_DISCOUNT),
        "pack_full": pack_price(1.0),
        "pack_breakeven_fill_vs_payg": PACK_GBP / (PACK_CREDITS * GBP_PER_CREDIT_PAYG),
        "active_months_central": months_central,
        "credits_per_student_month_central": cred_month_central,
        "students_to_fill_one_pack_central": PACK_CREDITS / cred_month_central,
        "students_to_reach_pack_breakeven": PACK_GBP / GBP_PER_CREDIT_PAYG / cred_month_central,
        "central_ms_cost_by_price": {},
    }
    for name, price in (("PAYG", GBP_PER_CREDIT_PAYG), ("pre-purchase −20% (best case)", pack["prepurchase_best"]),
                        ("pack 100% used", pack_price(1.0)), ("pack 82% used", pack_price(0.82)),
                        ("pack 60% used", pack_price(0.6)), ("pack 40% used", pack_price(0.4))):
        pack["central_ms_cost_by_price"][name] = {"gbp_per_credit": price, "ms_per_student": central["credits"] * price}
    out["credit_price"] = pack
    md += ["## 3. Credit price: pay-as-you-go, pre-purchase, packs", "",
           "| credit source | £/credit | Microsoft £/student/yr (central usage) |", "|---|---|---|"]
    for name, v in pack["central_ms_cost_by_price"].items():
        md.append(f"| {name} | {v['gbp_per_credit']:.5f} | {v['ms_per_student']:.2f} |")
    md += ["", f"- A pack beats PAYG only when at least {pack['pack_breakeven_fill_vs_payg']:.0%} of it is used.",
           f"- Central usage spread over {months_central:.1f} active months is {cred_month_central:.0f} credits per "
           f"student-month: about {pack['students_to_fill_one_pack_central']:.0f} students fill one 25k pack, and "
           f"{pack['students_to_reach_pack_breakeven']:.0f} reach its break-even. Use is seasonal (holidays, exam "
           "leave), so a trust needs a margin above that; the pool is shared with other agents.",
           "- Best credible price cut is about 20% (pre-purchase, 'up to'). No education discount was found "
           "(business plan §3). Credit price is not the lever; call count is.", ""]

    # 4. licensed vs unlicensed
    lic = {}
    for L in (0.0, 0.1, 0.25, 0.5, 1.0):
        lic[L] = cost_per_student(20, 30, 5, GBP_PER_CREDIT_PAYG, licensed_share=L)["total"]
    out["licensed_share_total"] = lic
    md += ["## 4. Licensed vs unlicensed students (IF the exemption covers students: unclear, w3-08m-05 ~)", "",
           "| share of students with an M365 Copilot licence | total £/student/yr (central, £5) |", "|---|---|"]
    md += [f"| {L:.0%} | {v:.2f} |" for L, v in lic.items()]
    md += ["", "The licence itself is not in findings.csv with a verified UK education price (the ~US$18/month "
           "figure is unverified, wave 2), so this table shows credits avoided, not money saved. Don't say a "
           "licensed student costs nothing.", ""]

    # 5. comparators
    century_year_inc = CENTURY_ESSEX_INC_VAT_3Y / 3
    comp = {
        "sparx_per_pupil": SPARX_PER_PUPIL,
        "century_essex_per_year_inc_vat": century_year_inc,
        "century_essex_per_year_ex_vat_at_20pc": century_year_inc / 1.2,
        "seneca_school_sync_per_school": SENECA_SCHOOL_SYNC,
        "seneca_per_pupil_at_600_or_more": SENECA_SCHOOL_SYNC / 600,
        "khanmigo_gbp_at_azure_rate": KHANMIGO_USD_YEAR * 0.75,
        "edux_central_total_share_of_ict_per_pupil": central["total"] / ICT_PER_PUPIL,
        "edux_central_vs_sparx_high": central["total"] / SPARX_PER_PUPIL[1],
    }
    out["comparators"] = comp
    md += ["## 5. Against what schools pay", "",
           "| product | per pupil per year | basis |", "|---|---|---|",
           f"| Sparx Maths (Dixons) | £{SPARX_PER_PUPIL[0]:.2f}–{SPARX_PER_PUPIL[1]:.2f} | w2-08-06 ✓; our estimate on an assumed headcount |",
           f"| Seneca School Sync | ≤ £{comp['seneca_per_pupil_at_600_or_more']:.2f} | w1-08-07 ✓; £646 per school, schools over 600 pupils |",
           f"| CENTURY (Essex FE) | not computable | w2-08-07 ✓; £{century_year_inc:,.0f}/yr inc VAT (≈£{comp['century_essex_per_year_ex_vat_at_20pc']:,.0f} ex VAT at 20%), learner count not published |",
           f"| Khanmigo (US learner price) | ≈ £{comp['khanmigo_gbp_at_azure_rate']:.0f} | w2-08-12 ✓; US$44 at Azure's 0.75 rate (our arithmetic); no UK offer |",
           f"| Microsoft Study and Learn | £0 extra | w3-08m-04 ✓; included, preselected for K-12 learners |",
           f"| **eduX on Copilot Studio, central** | **£{central['total']:.2f}** (£5 + £{central['microsoft']:.2f}) | this model |",
           f"| eduX, low (10 msgs/wk × 30) | £{cost_per_student(10, 30, 5, GBP_PER_CREDIT_PAYG)['total']:.2f} | this model |",
           "", f"eduX central is {comp['edux_central_vs_sparx_high']:.0f}× Sparx's top estimate and "
           f"{comp['edux_central_total_share_of_ict_per_pupil']:.0%} of what an LA-maintained secondary spends per "
           "pupil on ICT learning resources in a year (£128, w1-08-05 ✓; all pupils, not sixth-formers).", ""]

    # 6. design options
    m = message_mix()
    opts = options(m)
    base_credits = credits_per_100(m, 0, 0)
    out["message_mix"] = m
    rows = []
    md += ["## 6. Cutting calls: design options (per 100 student messages, our-choice mix)", "",
           f"Mix per part (05d): {', '.join(f'{k} {v:g}' for k, v in m['per_part'].items())} = "
           f"{m['msgs_per_part']:.1f} messages per part (k = 3 points, 30% wrong on first check, 1 question "
           "mid-loop: our choice). 10% research, 10% off-course, 3 progress/profile calls and 3 retries per "
           f"100 (our choice). Baseline (05e: call on every reply): {base_credits:.0f} credits per 100 messages.", "",
           "| option | messages without a call | credits/100 (uncalled = 0) | saving | credits/100 (uncalled = 2) | saving | evidence lost | fidelity risk |",
           "|---|---|---|---|---|---|---|---|"]
    for name, o in opts.items():
        c0 = credits_per_100(m, o["skip_msgs"], 0, o.get("skip_calls", 0.0))
        c2 = credits_per_100(m, o["skip_msgs"], 2, o.get("skip_calls", 0.0))
        rows.append({"option": name, **o, "credits_0": c0, "credits_2": c2,
                     "saving_0": 1 - c0 / base_credits, "saving_2": 1 - c2 / base_credits})
        md.append(f"| {name} | {o['skip_msgs']:.1f} | {c0:.0f} | {1 - c0 / base_credits:.0%} | {c2:.0f} | "
                  f"{1 - c2 / base_credits:.0%} | {o['evidence_lost']} | {o['fidelity_risk']} |")
    combo_skip = (opts["A. no call on off-course turns (chit-chat, thanks)"]["skip_msgs"]
                  + opts["B. no call on mid-loop questions (chatbot answers briefly, re-asks the pending question)"]["skip_msgs"]
                  + opts["C. pre-branched plan: next step for each MCQ letter returned in advance (lookahead 1)"]["skip_msgs"])
    for label, skip in (("A+B+E (no integrity cost)", opts["A. no call on off-course turns (chit-chat, thanks)"]["skip_msgs"]
                         + opts["B. no call on mid-loop questions (chatbot answers briefly, re-asks the pending question)"]["skip_msgs"]),
                        ("A+B+C+E", combo_skip)):
        c0 = credits_per_100(m, skip, 0, 2.0)
        c2 = credits_per_100(m, skip, 2, 2.0)
        rows.append({"option": label, "skip_msgs": skip, "credits_0": c0, "credits_2": c2,
                     "saving_0": 1 - c0 / base_credits, "saving_2": 1 - c2 / base_credits})
        md.append(f"| **{label}** | {skip:.1f} | {c0:.0f} | {1 - c0 / base_credits:.0%} | {c2:.0f} | "
                  f"{1 - c2 / base_credits:.0%} | see rows | see rows |")
    out["options"] = rows

    # what the options do to the central £ figure (20 messages/week x 30 weeks)
    md += ["", "Central £/student/yr after each package (20 msgs/week × 30 weeks, PAYG, £5 licence):", "",
           "| package | Microsoft £ (uncalled = 0) | total £ | Microsoft £ (uncalled = 2) | total £ |", "|---|---|---|---|---|"]
    msgs_year = 20 * 30
    pkg = {}
    for r in [{"option": "baseline (05e)", "credits_0": base_credits, "credits_2": base_credits}] + rows[-2:]:
        ms0 = msgs_year / 100 * r["credits_0"] * GBP_PER_CREDIT_PAYG
        ms2 = msgs_year / 100 * r["credits_2"] * GBP_PER_CREDIT_PAYG
        pkg[r["option"]] = {"ms_0": ms0, "ms_2": ms2}
        md.append(f"| {r['option']} | {ms0:.2f} | {ms0 + 5:.2f} | {ms2:.2f} | {ms2 + 5:.2f} |")
    out["packages_central"] = pkg
    md += ["", "Note: the baseline here (" f"{base_credits:.0f} credits per 100 messages) is above the business plan's "
           "flat 5 because it counts progress/profile calls and retries; the plan's £22.50 is 5 credits × 600.", ""]

    # 7. sensitivity of option C and B to the mix
    sens = []
    md += ["## 7. Sensitivity of the saving to the move mix (uncalled = 2 credits)", "",
           "| points/part k | wrong rate p | mid-loop q | research | off-course | A+B+E | A+B+C+E |", "|---|---|---|---|---|---|---|"]
    for k, p, q, rs, off in [(2, 0.3, 1, .1, .1), (4, 0.3, 1, .1, .1), (3, 0.1, 0.5, .1, .05), (3, 0.5, 2, .1, .1),
                             (3, 0.3, 1, .25, .1), (3, 0.3, 1, .05, .25), (3, 0.3, 3, .1, .1)]:
        mm = message_mix(k, p, q, rs, off)
        oo = options(mm)
        b = credits_per_100(mm, 0, 0)
        ab = oo["A. no call on off-course turns (chit-chat, thanks)"]["skip_msgs"] + \
            oo["B. no call on mid-loop questions (chatbot answers briefly, re-asks the pending question)"]["skip_msgs"]
        abc = ab + oo["C. pre-branched plan: next step for each MCQ letter returned in advance (lookahead 1)"]["skip_msgs"]
        s1 = 1 - credits_per_100(mm, ab, 2, 2.0) / b
        s2 = 1 - credits_per_100(mm, abc, 2, 2.0) / b
        sens.append({"k": k, "p": p, "q": q, "research": rs, "off": off, "AB_E": s1, "ABC_E": s2})
        md.append(f"| {k} | {p} | {q} | {rs:.0%} | {off:.0%} | {s1:.0%} | {s2:.0%} |")
    out["sensitivity"] = sens
    md += ["", "## 8. Per-class cap (central, PAYG)", ""]
    for n in (10, 20, 30):
        md.append(f"- Class of {n}: {n * cred_month_central:,.0f} credits a month over {months_central:.1f} active "
                  f"months, about £{n * cred_month_central * GBP_PER_CREDIT_PAYG:.0f} a month "
                  f"(business plan's 10-month spread: £{n * central['credits'] / 10 * GBP_PER_CREDIT_PAYG:.0f}).")
    md.append("")

    (OUT / "results.json").write_text(json.dumps(out, indent=1, default=str))
    (OUT / "results.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
