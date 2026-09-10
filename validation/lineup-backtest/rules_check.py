"""Step 3 — does the rules-derived 2025 lineup shape differ from the 2026 block?

WHEN THIS WAS WRITTEN, get_league(season=2025) failed, and that was recorded
as an upstream limitation: MFL rejects a prior season for TYPE=league. THAT
DIAGNOSIS WAS WRONG. The cause was the APIKEY being sent on a prior-season
league call; myfantasyleague 0.6.4 fixed it by dropping the key for that one
case. Confirmed working 9 Sep 2026 PT: the call returns real 2025 settings
through the gateway.

So a stronger check is now possible -- read the 2025 starters block directly
and compare it against BOTH the rules-derived shape and 2026, which would test
the league-rules digest instead of trusting it. This script has not been
rewritten to do that, and still derives 2025 from prose. Source for 2025: league-rules SKILL.md, which states the structure
with no year tag --
    "Roster structure: 10 starters, 8 bench, 6 taxi, 4 IR. Starters resolve to
     1 QB, 2 RB, 3 WR, 1 TE, 2 FLEX, 1 SUPERFLEX."
FLEX is RB/WR/TE; SUPERFLEX additionally allows QB.
"""
import json, os
D = os.path.dirname(os.path.abspath(__file__))

BASE = {"QB": 1, "RB": 2, "WR": 3, "TE": 1}
FLEX, SUPERFLEX = 2, 1
FLEX_OK = {"RB", "WR", "TE"}
SF_OK = {"QB", "RB", "WR", "TE"}

derived = {}
for pos, lo in BASE.items():
    hi = lo + (FLEX if pos in FLEX_OK else 0) + (SUPERFLEX if pos in SF_OK else 0)
    derived[pos] = (lo, hi)
total = sum(BASE.values()) + FLEX + SUPERFLEX

lg = json.loads(json.load(open(os.path.join(D, "league.json"), encoding="utf-8"))
                ["result"]["content"][0]["text"])["league"]
block = {}
for p in lg["starters"]["position"]:
    lo, hi = p["limit"].split("-")
    block[p["name"]] = (int(lo), int(hi))
block_count = int(lg["starters"]["count"])

print("  rules-derived (2025 source)   vs   deployed block (2026)")
same = True
for pos in ("QB", "RB", "WR", "TE"):
    d, b = derived[pos], block[pos]
    mark = "same" if d == b else "*** DIFFERS ***"
    if d != b: same = False
    print(f"    {pos}  {d[0]}-{d[1]:<3}                        {b[0]}-{b[1]:<3}    {mark}")
print(f"    count {total:<25} {block_count:<7} {'same' if total == block_count else '*** DIFFERS ***'}")
if total != block_count: same = False
print()
print("  VERDICT:", "requirements did NOT differ between 2025 and 2026 —"
      " the original gate run stands and the caveat is void." if same
      else "requirements DIFFER — the gate must be re-run.")
