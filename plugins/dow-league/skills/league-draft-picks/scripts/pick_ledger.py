#!/usr/bin/env python3
"""
Dynasty of Whiners — draft pick ledger.

    python3 pick_ledger.py --picks picks.json [--standings standings.json] \
                          [--names names.json] [--owner 0001]

Turns `get_future_draft_picks` into a readable ledger: who holds what, which
picks were acquired or sent, and -- with prior-season standings -- where each
pick is likely to slot.

THE NOTATION TRAP
  A pick is `FP_{origin}_{year}_{round}`. The franchise id in that string is the
  pick's ORIGIN, not its current holder. `FP_0002_2027_2` is Pat's 2027 2nd
  wherever it now sits.

SLOT PROJECTION
  Draft order is REVERSE regular-season standings, so a pick's worth depends
  entirely on how its ORIGIN team finishes the season before the draft -- not on
  who holds it. Early in a season the prior year is a weak anchor; the output
  says so rather than implying precision.

WHAT THIS CANNOT SEE
  Conditional picks. MFL has no representation for one: when a trade with a
  conditional leg executes, only the identified assets move, and the obligation
  exists solely in the gSheet text and two owners' memories. See the conditional
  section of the skill -- the ledger prints a standing reminder.
"""
import argparse, json, sys
from collections import defaultdict

TRADEABLE_YEARS_AHEAD = 3
ROUNDS = 4

def load_picks(raw):
    fr = raw.get("futureDraftPicks", {}).get("franchise", raw)
    if isinstance(fr, dict): fr = [fr]
    held = defaultdict(list)
    for f in fr:
        p = f.get("futureDraftPick", [])
        if isinstance(p, dict): p = [p]
        for pk in p:
            held[f["id"]].append((int(pk["year"]), int(pk["round"]), pk["originalPickFor"]))
    return held

def project_slots(standings_raw):
    """Reverse standings -> slot 1..12. Worst record picks first; PF breaks ties."""
    if not standings_raw: return {}, None
    fr = standings_raw.get("leagueStandings", {}).get("franchise", standings_raw)
    if isinstance(fr, dict): fr = [fr]
    rows = [{"id": f["id"], "w": float(f.get("h2hw") or 0), "pf": float(f.get("pf") or 0)}
            for f in fr]
    rows.sort(key=lambda r: (r["w"], r["pf"]))
    return ({r["id"]: i + 1 for i, r in enumerate(rows)},
            "prior regular-season standings (reverse order; PF breaks ties)")

def tier(slot):
    if slot is None: return "unknown"
    return "early" if slot <= 4 else "mid" if slot <= 8 else "late"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--picks", required=True)
    ap.add_argument("--standings")
    ap.add_argument("--names")
    ap.add_argument("--owner")
    ap.add_argument("--season", type=int)
    a = ap.parse_args()

    held = load_picks(json.load(open(a.picks)))
    slots, basis = project_slots(json.load(open(a.standings)) if a.standings else None)
    names = json.load(open(a.names)) if a.names else {}
    nm = lambda f: names.get(f, f)

    years = sorted({y for v in held.values() for y, _, _ in v})
    season = a.season or (min(years) - 1 if years else None)

    # completeness: every franchise's own slate should exist somewhere
    all_picks = {(y, r, o) for v in held.values() for (y, r, o) in v}
    expected = {(y, r, f) for y in years for r in range(1, ROUNDS + 1) for f in held}
    missing, extra = expected - all_picks, all_picks - expected
    dupes = len([1 for v in held.values() for _ in v]) - len(all_picks)

    print(f"PICK LEDGER · years {years[0]}-{years[-1]} · {len(all_picks)} picks")
    if basis: print(f"slot projection from {basis}")
    print(f"integrity: {'OK' if not (missing or extra or dupes) else 'PROBLEM'}"
          f"  missing={len(missing)} unexpected={len(extra)} duplicated={dupes}")
    if season:
        ok = [season + i for i in range(1, TRADEABLE_YEARS_AHEAD + 1)]
        print(f"tradeable years from the {season} offseason: {ok}")
        bad = [y for y in years if y not in ok]
        if bad: print(f"  !! picks present for untradeable years: {bad}")
    print()

    targets = [a.owner] if a.owner else sorted(held, key=lambda f: -len(held[f]))
    for f in targets:
        picks = sorted(held[f])
        own = sum(1 for _, _, o in picks if o == f)
        print(f"{nm(f)} ({f}) · holds {len(picks)} · own {own} · acquired {len(picks)-own}")
        by_year = defaultdict(list)
        for y, r, o in picks: by_year[y].append((r, o))
        for y in sorted(by_year):
            bits = []
            for r, o in sorted(by_year[y]):
                s = slots.get(o)
                lbl = f"{r}"
                if o != f: lbl += f" ({nm(o)})"
                if s: lbl += f" ~{tier(s)}"
                bits.append(lbl)
            gone = [r for r in range(1, ROUNDS + 1) if (r, f) not in by_year[y]]
            g = f"   own gone: {gone}" if gone else ""
            print(f"   {y}: " + ", ".join(bits) + g)
        print()

    print("REMINDERS")
    print("  * The id in FP_xxxx_YYYY_R is the pick's ORIGIN, not its holder.")
    print("  * Slot follows the ORIGIN team's finish, not the holder's.")
    print("  * Conditional picks are INVISIBLE here -- MFL cannot represent them.")
    print("    Check the gSheet Trade History for relative-slot language")
    print("    (latest / earliest / highest / lowest / better of / worse of),")
    print("    and look for one-sided trades, which are how they settle.")

if __name__ == "__main__":
    main()
