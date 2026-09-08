#!/usr/bin/env python3
"""
Compute the three scheduling tiers from prior-season MFL data.

    python3 compute_tiers.py --data prior-season.json > season-YYYY.json

This is the step that has gone wrong before, twice over, so it does the
arithmetic explicitly and shows its work rather than leaving it to judgement.

TWO TRAPS, both real:

1. TIER 1 IS BY PLAYOFF FINISH, NOT BY SCORING. It is the four teams who played
   in the final two playoff games -- the championship and the 3rd place game.
   The 2026 schedule was built by ranking everyone 1-4 on points instead, which
   put Straker in Tier 1 and Gabe in Tier 2, and had to be redone.

2. MFL'S STANDINGS `pf` IS NOT REGULAR-SEASON POINTS. It covers every scoring
   week, not the 14 that count -- non-playoff teams play consolation games, so
   ALL twelve franchises carry scores in weeks 15+. In 2025 every franchise's
   `avgpf` was exactly `pf / 18`. Subtract weeks 15 onward before ranking.
   In 2025 this did not change tier membership, but Ryan scored 484.76 points
   after week 14 on a 2-12 team -- in a year where that sits near the Tier 2/3
   boundary it flips someone.

INPUT (prior-season.json), all of it pullable from the MFL tools:

  {
    "season": 2025,
    "final_two_games": [["0003","0010"], ["0002","0009"]],   # week 17 matchups
    "franchises": {
      "0001": {"pf_total": 2341.18, "post_week14": [162.68,125.88,133.08,75.44]},
      ...
    },
    "names": {"0001": "Straker", ...}
  }

  final_two_games: get_weekly_results(season=N-1, week=17).weeklyResults.matchup
                   -- that array holds exactly the championship and 3rd place game.
  pf_total:        get_standings(season=N-1) -> franchise.pf
  post_week14:     get_weekly_results(season=N-1, week=15..18), each team's score.
                   Pull weeks until one returns nothing; do not assume four.
"""
import argparse, json, sys


def compute(data):
    fr = data["franchises"]
    names = data.get("names", {})
    nm = lambda t: names.get(t, t)

    tier1 = [t for game in data["final_two_games"] for t in game]
    if len(tier1) != 4 or len(set(tier1)) != 4:
        sys.exit(f"final_two_games must name 4 distinct franchises, got {tier1}")

    reg = {}
    for t, v in fr.items():
        post = sum(v.get("post_week14", []))
        reg[t] = round(v["pf_total"] - post, 2)

    rest = sorted((t for t in fr if t not in tier1), key=lambda t: -reg[t])
    if len(rest) != 8:
        sys.exit(f"expected 8 non-Tier-1 franchises, got {len(rest)}")
    tier2, tier3 = rest[:4], rest[4:]

    margin = reg[tier2[-1]] - reg[tier3[0]]
    return {
        "tiers": {"T1": tier1, "T2": tier2, "T3": tier3},
        "rematches": data["final_two_games"],
        "names": names,
        # Keyed by franchise id, for build_schedule.py's opponent-strength
        # report. `_working.regular_season_pf` below is the same numbers keyed by
        # NAME, for a human reading the working -- not safe to consume.
        "prior_pf": {t: reg[t] for t in fr},
        "_working": {
            "regular_season_pf": {nm(t): reg[t] for t in
                                  sorted(fr, key=lambda x: -reg[x])},
            "tier2_tier3_margin": round(margin, 2),
            "note": ("Tier 1 is the four teams in the final two playoff games, by "
                     "finish and not by points. Tiers 2 and 3 rank the other eight "
                     "on regular-season points only, with weeks 15+ subtracted."),
        },
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--season", type=int)
    a = ap.parse_args()
    d = json.load(open(a.data))
    out = compute(d)
    if a.season:
        out = {"season": a.season, **out}
    w = out["_working"]
    print(f"# Tier 1 (final two playoff games): "
          f"{', '.join(out['names'].get(t,t) for t in out['tiers']['T1'])}", file=sys.stderr)
    print(f"# Tier 2/Tier 3 margin: {w['tier2_tier3_margin']} points", file=sys.stderr)
    if w["tier2_tier3_margin"] < 50:
        print("# ^ TIGHT. Re-check that weeks 15+ were fully subtracted.", file=sys.stderr)
    print(json.dumps(out, indent=2))
