#!/usr/bin/env python3
"""Adversarial checks on the back-test harness.

Two questions the clean run cannot answer:
  A. Is the "optimum" actually optimal, or just what my enumeration found?
  B. Do the gates fire at all, or are they decorative?
"""
import json, os, random, itertools
from collections import Counter

D = os.path.dirname(os.path.abspath(__file__))
def load(n):
    return json.loads(json.load(open(os.path.join(D, n), encoding="utf-8"))
                      ["result"]["content"][0]["text"])

lg = load("league.json")["league"]
COUNT = int(lg["starters"]["count"])
RANGES = {}
for p in lg["starters"]["position"]:
    lo, hi = p["limit"].split("-")
    RANGES[p["name"]] = (int(lo), int(hi))
POS = {p["id"]: p.get("position") for p in load("players.json")["players"]["player"]}
ros = load("rosters2025.json")["rosters"]["franchise"]

SPLITS = [{"QB": q, "RB": r, "WR": w, "TE": t}
          for q in range(*(RANGES["QB"][0], RANGES["QB"][1] + 1))
          for r in range(*(RANGES["RB"][0], RANGES["RB"][1] + 1))
          for w in range(*(RANGES["WR"][0], RANGES["WR"][1] + 1))
          for t in range(*(RANGES["TE"][0], RANGES["TE"][1] + 1))
          if q + r + w + t == COUNT]

def optimise(pool, pts):
    by = {}
    for i in pool: by.setdefault(POS.get(i), []).append(i)
    for k in by: by[k].sort(key=lambda i: -pts.get(i, 0.0))
    best = None
    for sp in SPLITS:
        if any(len(by.get(p, [])) < n for p, n in sp.items()): continue
        pick = [i for p, n in sp.items() for i in by[p][:n]]
        tot = sum(pts.get(i, 0.0) for i in pick)
        if best is None or tot > best[0]: best = (tot, pick)
    return best

def is_legal(pick, pool):
    if len(pick) != COUNT: return "wrong count"
    if len(set(pick)) != len(pick): return "duplicate player"
    if any(i not in pool for i in pick): return "player not in startable pool"
    c = Counter(POS.get(i) for i in pick)
    for p, (lo, hi) in RANGES.items():
        if not (lo <= c.get(p, 0) <= hi): return f"{p} count {c.get(p,0)} outside {lo}-{hi}"
    return None

sc = load("scores_w3.json")["playerScores"]["playerScore"]
pts = {}
for s in sc:
    try: pts[s["id"]] = float(s.get("score") or 0)
    except (TypeError, ValueError): pts[s["id"]] = 0.0

print("=== A. is the optimum actually optimal? ===")
print("    1,000,000 random legal lineups per franchise vs the enumerated optimum\n")
rng = random.Random(7)
beaten = 0
for fr in ros:
    pool = [p["id"] for p in fr["player"] if p.get("status") == "ROSTER"]
    opt, pick = optimise(pool, pts)
    by = {}
    for i in pool: by.setdefault(POS.get(i), []).append(i)
    best_rand = 0.0
    for _ in range(1_000_000 // len(ros)):
        sp = rng.choice(SPLITS)
        if any(len(by.get(p, [])) < n for p, n in sp.items()): continue
        cand = [i for p, n in sp.items() for i in rng.sample(by[p], n)]
        t = sum(pts.get(i, 0.0) for i in cand)
        if t > best_rand: best_rand = t
    flag = "  *** RANDOM BEAT THE OPTIMUM ***" if best_rand > opt + 1e-9 else ""
    if best_rand > opt + 1e-9: beaten += 1
    print(f"    {fr['id']}  optimum {opt:7.2f}   best of random {best_rand:7.2f}{flag}")
print(f"\n    franchises where random beat the enumeration: {beaten} (want 0)\n")

print("=== B. do the gates fire? mutation tests ===")
fr = ros[0]
pool = [p["id"] for p in fr["player"] if p.get("status") == "ROSTER"]
ir = [p["id"] for p in fr["player"] if p.get("status") == "INJURED_RESERVE"]
taxi = [p["id"] for p in fr["player"] if p.get("status") == "TAXI_SQUAD"]
_, good = optimise(pool, pts)
print(f"    baseline legal lineup            -> {is_legal(good, pool) or 'LEGAL (correct)'}")
print(f"    drop one starter (9 players)     -> {is_legal(good[:-1], pool) or 'LEGAL -- GATE FAILED'}")
dup = good[:-1] + [good[0]]
print(f"    duplicate a player               -> {is_legal(dup, pool) or 'LEGAL -- GATE FAILED'}")
if ir:
    swapped = good[:-1] + [ir[0]]
    print(f"    start an IR player               -> {is_legal(swapped, pool) or 'LEGAL -- GATE FAILED'}")
if taxi:
    swapped = good[:-1] + [taxi[0]]
    print(f"    start a taxi-squad player        -> {is_legal(swapped, pool) or 'LEGAL -- GATE FAILED'}")
qbs = [i for i in pool if POS.get(i) == "QB"]
if len(qbs) >= 3:
    nonqb = [i for i in good if POS.get(i) != "QB"]
    over = [i for i in good if POS.get(i) == "QB"] + qbs[:3]
    over = list(dict.fromkeys(over))[:3] + nonqb[:7]
    print(f"    three QBs (max is 2)             -> {is_legal(over, pool) or 'LEGAL -- GATE FAILED'}")
else:
    print(f"    three QBs                        -> skipped, only {len(qbs)} QBs rostered")

print("\n=== C. a starved pool must yield NO lineup, not an illegal one ===")
starved = [i for i in pool if POS.get(i) != "TE"][:12]
r = optimise(starved, pts)
if r is None:
    print("    zero TEs available -> optimise() returned None (correct: no legal lineup exists)")
else:
    print(f"    zero TEs available -> returned a lineup: {is_legal(r[1], starved) or 'LEGAL -- WRONG'}")
