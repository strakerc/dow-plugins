#!/usr/bin/env python3
"""Phase 5 back-test harness for league-lineup.

Implements the skill's stated method exactly, with ACTUAL 2025 points as the
ranking input (perfect foresight -- an upper bound on the chooser, not a
forecast). Checks the hard gates.
"""
import json, os, sys, itertools
from collections import Counter

D = os.path.dirname(os.path.abspath(__file__))
def load(name):
    return json.loads(json.load(open(os.path.join(D, name), encoding="utf-8"))
                      ["result"]["content"][0]["text"])

# ---- slots, from get_league (2026 config; season=2025 is broken upstream) ----
lg = load("league.json")["league"]
SLOTS = {p["name"]: p["limit"] for p in lg["starters"]["position"]}
COUNT = int(lg["starters"]["count"])
RANGES = {}
for pos, lim in SLOTS.items():
    lo, hi = lim.split("-") if "-" in lim else (lim, lim)
    RANGES[pos] = (int(lo), int(hi))
PARTIAL_OK = lg.get("partialLineupAllowed") == "YES"

# ---- player metadata ----
pl = load("players.json")["players"]["player"]
POS = {p["id"]: p.get("position") for p in pl}
NAME = {p["id"]: p.get("name") for p in pl}

# ---- rosters as they were in 2025 ----
ros = load("rosters2025.json")["rosters"]["franchise"]
FR_NAME = {}
lgf = {f["id"]: f.get("name") for f in lg["franchises"]["franchise"]}

def startable(fr):
    """Only status ROSTER. Never IR, never taxi."""
    return [p["id"] for p in fr["player"] if p.get("status") == "ROSTER"]

def legal_splits():
    """Every position-count combination that fills exactly COUNT legally."""
    out = []
    for q in range(RANGES["QB"][0], RANGES["QB"][1] + 1):
        for r in range(RANGES["RB"][0], RANGES["RB"][1] + 1):
            for w in range(RANGES["WR"][0], RANGES["WR"][1] + 1):
                for t in range(RANGES["TE"][0], RANGES["TE"][1] + 1):
                    if q + r + w + t == COUNT:
                        out.append({"QB": q, "RB": r, "WR": w, "TE": t})
    return out

SPLITS = legal_splits()

def optimise(pool_ids, pts):
    """Highest-scoring legal COUNT. Optimal: within a position you always take
    the top-N, so enumerating legal position splits is exhaustive."""
    by_pos = {}
    for pid in pool_ids:
        by_pos.setdefault(POS.get(pid), []).append(pid)
    for k in by_pos:
        by_pos[k].sort(key=lambda i: -pts.get(i, 0.0))
    best = None
    for sp in SPLITS:
        if any(len(by_pos.get(p, [])) < n for p, n in sp.items()):
            continue
        picked = [i for p, n in sp.items() for i in by_pos[p][:n]]
        total = sum(pts.get(i, 0.0) for i in picked)
        if best is None or total > best[0]:
            best = (total, picked, sp)
    return best

print(f"slots {SLOTS} count {COUNT} partialLineupAllowed={'YES' if PARTIAL_OK else 'NO'}")
print(f"legal position splits: {len(SPLITS)}\n")

gate_fail = []
rows = []
for week in (3, 8, 13):
    sc = load(f"scores_w{week}.json")["playerScores"]["playerScore"]
    pts = {}
    for s in sc:
        try: pts[s["id"]] = float(s.get("score") or 0)
        except (TypeError, ValueError): pts[s["id"]] = 0.0
    for fr in ros:
        fid = fr["id"]; owner = lgf.get(fid, fid)
        pool = startable(fr)
        unresolved = [i for i in pool if POS.get(i) is None]
        noscore = [i for i in pool if i not in pts]
        best = optimise(pool, pts)
        if best is None:
            gate_fail.append(f"week {week} {owner}: NO LEGAL LINEUP from {len(pool)} startable")
            continue
        total, picked, sp = best
        # ---- gates ----
        if len(picked) != COUNT:
            gate_fail.append(f"week {week} {owner}: {len(picked)} starters, need {COUNT}")
        if len(set(picked)) != len(picked):
            gate_fail.append(f"week {week} {owner}: a player used twice")
        cnt = Counter(POS.get(i) for i in picked)
        for p, (lo, hi) in RANGES.items():
            if not (lo <= cnt.get(p, 0) <= hi):
                gate_fail.append(f"week {week} {owner}: {p}={cnt.get(p,0)} outside {lo}-{hi}")
        for i in picked:
            if i not in pool:
                gate_fail.append(f"week {week} {owner}: bench/IR player started")
        rows.append(dict(week=week, owner=owner, total=round(total, 2), split=sp,
                         pool=len(pool), unresolved=len(unresolved), noscore=len(noscore)))

for week in (3, 8, 13):
    wk = [r for r in rows if r["week"] == week]
    print(f"--- week {week} ---")
    for r in sorted(wk, key=lambda x: -x["total"]):
        sp = r["split"]
        print(f"  {r['owner'][:22]:<22} {r['total']:>7.2f}  "
              f"QB{sp['QB']} RB{sp['RB']} WR{sp['WR']} TE{sp['TE']}  "
              f"pool {r['pool']:>2}  unresolved {r['unresolved']}  no-score {r['noscore']}")
    print()

print("=" * 62)
print(f"lineups built: {len(rows)} (12 franchises x 3 weeks = 36 expected)")
print(f"GATE failures: {len(gate_fail)}")
for g in gate_fail:
    print("  FAIL", g)
if not gate_fail and len(rows) == 36:
    print("\nALL HARD GATES PASS")
else:
    # Exit non-zero, so a runner that only reads the exit code sees the
    # failure. Until 9 Sep 2026 PT this script exited 0 either way, and
    # validation/regress.py read that as a pass.
    sys.exit(1)
