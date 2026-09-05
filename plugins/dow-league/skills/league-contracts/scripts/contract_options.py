#!/usr/bin/env python3
"""
Dynasty of Whiners — contract options and costs.

    python3 contract_options.py --roster roster.json --season 2027 [--franchise 0001]

For every player on a roster, works out whether a decision is due this offseason,
what the legal options are, and what each one costs. Deterministic: it reads the
constitution's price tables, never a valuation.

INPUT is the raw `get_rosters` payload (or the `franchise` object from it).

WHAT IT DOES NOT DO
  * Say whether a player is WORTH the price. That is a valuation question.
  * Price a franchise tag. The positional floor needs last season's top-5 salaries
    by position -- see the league-franchise-tags skill and franchise-tag-method.md.
    This tool reports the personal floor (previous plus 5) and flags that the real
    price is the GREATER of that and the positional floor.

THE FIELDS, and the one that misleads
  salary          current annual salary
  contractInfo    Rookie | Short-Term | Short-Term (Extension) | Long-Term |
                  Free Agent | Franchise / Franchise Tag  (MFL is inconsistent
                  about the last two spellings)
  contractYear    which year OF the deal the player is in
  contractStatus  *** the FINAL YEAR of the deal, not its length ***
  status          ROSTER | TAXI_SQUAD | INJURED_RESERVE

  years remaining = contractStatus - season + 1
"""
import argparse, json, math, sys
from collections import defaultdict

CAP, FLOOR, MIN_SALARY = 375, 300, 1
ACTIVE_SLOTS, TAXI_SLOTS, IR_SLOTS = 18, 6, 4
ROSTER_MINIMUMS = {"QB": 2, "RB": 3, "WR": 4, "TE": 2}

def norm(ci):
    c = (ci or "").strip().lower()
    if "extension" in c: return "short_ext"
    if c.startswith("short"): return "short"
    if c.startswith("long"): return "long"
    if c.startswith("rookie"): return "rookie"
    if c.startswith("free"): return "fa"
    if c.startswith("franchise"): return "tag"
    return "unknown"

def years_remaining(p, season):
    through = int(p.get("contractStatus") or 0)
    return max(0, through - season + 1) if through else 0

def options_for(p, season):
    """Legal options once this contract has completed, with prices."""
    kind, sal = norm(p.get("contractInfo")), int(p.get("salary") or 0)
    opts = [{"option": "Release", "cost": 0,
             "note": "dead money depends on contract type -- see cut_cost"}]

    tag = {"option": "Franchise tag", "cost": sal + 5, "years": 1,
           "note": "PERSONAL FLOOR ONLY. Real price is the GREATER of this and "
                   "ceil(avg of top 5 salaries at the position last season) plus 5. "
                   "Also gated: max twice by the same owner, never two years "
                   "running, one active tag per team."}

    if kind == "short":
        # After year 1 of a short-term the options NARROW: no second short-term.
        opts += [
            {"option": "Short-term extension", "cost": sal + 10, "years": 2,
             "note": f"year 1 ${sal+10}, year 2 ${sal+15} "
                     f"(year 2 becomes +$10 -> ${sal+20} for short-terms signed 2028+, "
                     f"first paid 2030)"},
            tag,
        ]
        opts.append({"option": "Short-term (again)", "cost": None, "years": None,
                     "note": "NOT LEGAL. After a short-term's first season the only "
                             "choices are release, tag, or the two-year extension."})
    elif kind == "tag":
        opts += [
            {"option": "Long-term", "cost": sal + 10, "years": 3,
             "note": "flat all three years"},
            {"option": "Short-term extension", "cost": sal + 10, "years": 2,
             "note": f"year 1 ${sal+10}, year 2 ${sal+15}"},
        ]
        opts.append({"option": "Short-term", "cost": None, "years": None,
                     "note": "Only if the player was NOT on a short-term before the "
                             "tag. If he was, long-term or extension only."})
        opts.append({"option": "Franchise tag (again)", "cost": None, "years": None,
                     "note": "NOT LEGAL two years running."})
    else:
        # rookie / long / fa / short_ext all return to the normal menu
        opts += [
            {"option": "Short-term", "cost": sal + 5, "years": 1},
            {"option": "Long-term", "cost": sal + 10, "years": 3,
             "note": "flat all three years"},
            tag,
        ]
        if kind == "rookie":
            rd = (p.get("drafted") or "")
            rnd = int(rd[0]) if rd[:1].isdigit() else None
            bump = {1: 5, 2: 4, 3: 3, 4: 2}.get(rnd)
            opts.append({
                "option": "Rookie extension", "cost": (sal + bump) if bump else None,
                "years": 1,
                "note": f"[2026, effective 2028] round {rnd or '?'} +${bump or '?'}. "
                        "Not available before 2028. Does not block a short-term after."})
    return opts

def cut_cost(p, season):
    kind, sal = norm(p.get("contractInfo")), int(p.get("salary") or 0)
    yrs = years_remaining(p, season)
    if kind == "rookie":
        yr = int(p.get("contractYear") or 1)
        if yr == 1:
            return 0, "Rookie cut between years 1 and 2 -- NO penalty."
        return math.ceil(sal * 0.25), "Rookie contract -- 25%, for the rest of this year only."
    if kind == "fa":
        return math.ceil(sal * 0.25), "Free Agent contract -- 25%, rest of this year only."
    return sal * yrs, (f"Non-rookie contract -- 100% of the remaining {yrs} "
                       f"year{'s' if yrs != 1 else ''} as dead money. Cannot be traded.")

def cap_hit(p):
    return int(p.get("salary") or 0) * (0.25 if p.get("status") == "INJURED_RESERVE" else 1)

def analyse(players, season, names=None, adjustments=0.0, adjustments_supplied=False):
    names = names or {}
    nm = lambda p: names.get(p["id"], p["id"])
    committed = sum(cap_hit(p) for p in players)
    floor_charge = sum(int(p.get("salary") or 0) for p in players)
    expiring, under = [], []
    for p in players:
        row = {"id": p["id"], "name": nm(p), "salary": int(p.get("salary") or 0),
               "contract": p.get("contractInfo"), "through": p.get("contractStatus"),
               "status": p.get("status"), "capHit": cap_hit(p),
               "yearsRemaining": years_remaining(p, season)}
        cost, why = cut_cost(p, season)
        row["cutCost"], row["cutNote"] = cost, why
        if row["yearsRemaining"] <= 1:
            row["options"] = options_for(p, season)
            expiring.append(row)
        else:
            under.append(row)
    return {
        "season": season,
        "capSpace": round(CAP - adjustments - committed, 2),
        "capSpaceBeforeAdjustments": round(CAP - committed, 2),
        "salaryAdjustments": round(adjustments, 2),
        "adjustmentsSupplied": adjustments_supplied,
        "committed": round(committed, 2),
        "floorCharge": round(floor_charge + adjustments, 2),
        "floorHeadroom": round(floor_charge + adjustments - FLOOR, 2),
        "rosterCounts": {
            "active": sum(1 for p in players if p.get("status") == "ROSTER"),
            "taxi": sum(1 for p in players if p.get("status") == "TAXI_SQUAD"),
            "ir": sum(1 for p in players if p.get("status") == "INJURED_RESERVE"),
        },
        "decisionsDue": expiring,
        "underContract": under,
        "reminders": [
            "Cap $375; taxi counts 100%, IR 25%. Floor $300 with IR at 100% and dead money included.",
            "Free cap space must always be >= open roster spots (minimum salary is 1).",
            f"Roster minimums after the FA draft: {ROSTER_MINIMUMS} -- taxi and IR count.",
            ("Cap space above is NET of $%.2f in salary adjustments." % adjustments)
            if adjustments_supplied else
            "*** NO SALARY ADJUSTMENTS SUPPLIED -- capSpace may be TOO HIGH. Dead money "
            "lives in get_salary_adjustments; pass it with --adjustments. Note MFL writes "
            "only the automatic 25%% on a drop and the LM adds the remaining 75%% by hand, "
            "so a partially-processed cut understates the true charge. ***",
            "Roster submission deadline is $25/day late, and the cuts deadline the next day stacks another $25/day.",
        ],
    }

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--roster", required=True, help="get_rosters JSON")
    ap.add_argument("--season", type=int, required=True)
    ap.add_argument("--franchise")
    ap.add_argument("--names", help="optional {id: name} JSON")
    ap.add_argument("--adjustments", help="raw get_salary_adjustments JSON -- dead money. "
                                          "Without it capSpace is gross, not net.")
    a = ap.parse_args()
    raw = json.load(open(a.roster))
    fr = raw.get("rosters", {}).get("franchise", raw)
    if isinstance(fr, dict): fr = [fr]
    if a.franchise: fr = [f for f in fr if f.get("id") == a.franchise]
    if not fr: sys.exit("no franchise matched")
    names = json.load(open(a.names)) if a.names else {}

    adj, supplied = {}, False
    if a.adjustments:
        supplied = True
        raw_adj = json.load(open(a.adjustments))
        rows = raw_adj.get("salaryAdjustments", {}).get("salaryAdjustment", raw_adj)
        if isinstance(rows, dict): rows = [rows]
        for r in rows:
            adj[r["franchise_id"]] = adj.get(r["franchise_id"], 0.0) + float(r["amount"])

    out = {f["id"]: analyse(f["player"], a.season, names,
                            adj.get(f["id"], 0.0), supplied) for f in fr}
    print(json.dumps(out, indent=2))
