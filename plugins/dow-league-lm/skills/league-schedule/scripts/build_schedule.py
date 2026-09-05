#!/usr/bin/env python3
"""
Dynasty of Whiners — annual regular-season schedule generator.

Builds a complete, validated 14-week schedule from the three tiers plus the two
previous-season rematches, and prints the MFL import block.

    python3 build_schedule.py --config season.json [--seed 7]

It replaces steps 4-10 of the constitution's LM procedure: the external Streamlit
generator, the CSV export, the manual team-number assignment, and the "big ass
random numbers" duplicate checksum.

WHAT IT DOES NOT DO: touch MFL. It prints text. A human pastes it, after saving
the existing schedule, because the MFL import overwrites everything with no undo.

--------------------------------------------------------------------------------
THE STRUCTURE, which is not obvious from the constitution and was confirmed by
auditing a schedule Paul built by hand:

  14 weeks = an 11-week full round robin  +  3 rivalry weeks (4, 8, 12).

  * The round robin occupies weeks 1,2,3,5,6,7,9,10,11,13,14 and contains all 66
    pairings exactly once.
  * Each tier has FOUR teams, and a four-team round robin is exactly THREE rounds
    -- which is why there are exactly three rivalry weeks. Each tier plays itself
    across weeks 4, 8 and 12.
  * So every team plays its three tier-mates twice and everyone else once.
  * The week 1 rematches are NOT extra games. They are round-robin games whose
    position is pinned. Both rematch pairs are Tier 1 by construction (the four
    teams in the final two playoff games ARE Tier 1), so each meets again in a
    rivalry week like any other tier pair.

TWO FREE LEVERS the manual process never used:

  1. Which round of a tier's mini round robin lands in which rivalry week is
     unconstrained -- 3! per tier, three tiers, 216 orderings, all equally legal.
     They differ only in how far apart a pair's two meetings fall. We test all of
     them and keep the best-spaced legal one.
  2. Home/away orientation is entirely free: every constraint depends only on the
     unordered pair. And perfect balance always EXISTS -- all twelve teams play 14
     games, so the graph has all-even degrees and admits an orientation with 7
     home games everywhere. We reach it by flipping augmenting paths.
--------------------------------------------------------------------------------
"""
import argparse, itertools, json, random, sys
from collections import Counter, defaultdict, deque

ROUND_ROBIN_WEEKS = [1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14]
RIVALRY_WEEKS = [4, 8, 12]
pair = lambda a, b: tuple(sorted((a, b)))


# ---------------------------------------------------------------- round robin
def circle_round_robin(teams, rng):
    """Standard circle method. 12 teams -> 11 rounds of 6, every pair once."""
    t = list(teams)
    rng.shuffle(t)
    fixed, rot = t[0], t[1:]
    rounds = []
    for _ in range(len(t) - 1):
        ring = [fixed] + rot
        half = len(ring) // 2
        rounds.append([(ring[i], ring[-1 - i]) for i in range(half)])
        rot = [rot[-1]] + rot[:-1]
    rng.shuffle(rounds)
    for r in rounds:
        rng.shuffle(r)
    return rounds


def label_with_rematches(rounds, rematches, owners, rng):
    """
    The constitution's step 5, done properly: generate the round robin over
    ANONYMOUS slots, then name the rematch participants onto whichever slots
    happen to meet in round 1. That gets the week-1 constraint for free instead
    of searching for it.
    """
    slot_pairs = rounds[0]
    (a1, b1), (a2, b2) = rematches
    (s1, s2), (s3, s4) = slot_pairs[0], slot_pairs[1]
    mapping = {s1: a1, s2: b1, s3: a2, s4: b2}
    rest_slots = [s for r in rounds[0] for s in r if s not in mapping]
    rest_owners = [o for o in owners if o not in mapping.values()]
    rng.shuffle(rest_owners)
    mapping.update(dict(zip(rest_slots, rest_owners)))
    return [[(mapping[x], mapping[y]) for x, y in rnd] for rnd in rounds]


def tier_rounds(four):
    """The three rounds of a four-team round robin."""
    a, b, c, d = four
    return [[(a, b), (c, d)], [(a, c), (b, d)], [(a, d), (b, c)]]


# ------------------------------------------------------------------ assembly
def assemble(rr_rounds, tiers, rng):
    """Place the round robin, then search all 216 rivalry orderings."""
    weeks = {w: rr_rounds[i] for i, w in enumerate(ROUND_ROBIN_WEEKS)}
    rr_week = {pair(*m): w for w, ms in weeks.items() for m in ms}

    best = None
    for perm in itertools.product(itertools.permutations(range(3)), repeat=3):
        riv = {}
        for i, w in enumerate(RIVALRY_WEEKS):
            games = []
            for ti, four in enumerate(tiers.values()):
                games += tier_rounds(four)[perm[ti][i]]
            riv[w] = games
        # hard rule: a rivalry matchup must not repeat in the adjacent week
        if any(pair(*m) in {pair(*x) for x in weeks.get(w + d, [])}
               for w in RIVALRY_WEEKS for m in riv[w] for d in (-1, 1)):
            continue
        gaps = [abs(w - rr_week[pair(*m)]) for w in RIVALRY_WEEKS for m in riv[w]]
        score = (min(gaps), -sum(1 for g in gaps if g <= 2), sum(gaps) / len(gaps))
        if best is None or score > best[0]:
            best = (score, riv)
    if best is None:
        return None
    full = dict(weeks)
    full.update(best[1])
    return {w: full[w] for w in sorted(full)}


# ------------------------------------------------------------- home / away
def balance_home_away(sched, teams):
    """
    Flip orientations until every team has exactly 7 home games. Cannot break any
    other constraint: they all depend on the unordered pair. Guaranteed to
    terminate because a perfect orientation provably exists (all degrees even).
    """
    target = len(sched) // 2
    orient = {(w, i): m for w, ms in sched.items() for i, m in enumerate(ms)}
    flips = 0
    while True:
        home = Counter(h for _, h in orient.values())
        deficit = [t for t in teams if home[t] < target]
        if not deficit:
            break
        adj = defaultdict(list)
        for eid, (a, h) in orient.items():
            adj[a].append((h, eid))
        src = deficit[0]
        prev, q, tgt = {src: None}, deque([src]), None
        while q:
            u = q.popleft()
            if u != src and home[u] > target:
                tgt = u
                break
            for v, eid in adj[u]:
                if v not in prev:
                    prev[v] = (u, eid)
                    q.append(v)
        if tgt is None:
            raise RuntimeError("no augmenting path -- schedule is not connected")
        cur = tgt
        while prev[cur] is not None:
            u, eid = prev[cur]
            a, h = orient[eid]
            orient[eid] = (h, a)
            flips += 1
            cur = u
    return {w: [orient[(w, i)] for i in range(len(ms))] for w, ms in sched.items()}, flips


# -------------------------------------------------------------- validation
def validate(sched, tiers, rematches, teams):
    tier_of = {t: name for name, four in tiers.items() for t in four}
    rr = [pair(*m) for w, ms in sched.items() if w not in RIVALRY_WEEKS for m in ms]
    counts = Counter(pair(*m) for ms in sched.values() for m in ms)
    doubled = {p for p, n in counts.items() if n == 2}
    within = {pair(a, b) for four in tiers.values()
              for i, a in enumerate(four) for b in four[i + 1:]}
    home = Counter(h for ms in sched.values() for _, h in ms)
    away = Counter(a for ms in sched.values() for a, _ in ms)
    n = len(teams)
    checks = [
        (f"{n // 2 * 14} games, 14 weeks x {n // 2}",
         sum(len(v) for v in sched.values()) == n // 2 * 14),
        (f"round robin: all {n * (n - 1) // 2} pairings exactly once",
         len(rr) == n * (n - 1) // 2 == len(set(rr))),
        ("rivalry weeks all within-tier",
         all(tier_of[a] == tier_of[b] for w in RIVALRY_WEEKS for a, b in sched[w])),
        ("doubled pairings are exactly the within-tier pairings", doubled == within),
        ("no back-to-back around a rivalry week",
         not any(pair(*m) in {pair(*x) for x in sched.get(w + d, [])}
                 for w in RIVALRY_WEEKS for m in sched[w] for d in (-1, 1))),
        ("every team plays 14 games", all(home[t] + away[t] == 14 for t in teams)),
        ("week 1 carries both rematches",
         {pair(*m) for m in sched[1]} >= {pair(*r) for r in rematches}),
        (f"home/away balanced {14 // 2}H/{14 // 2}A for all {n}",
         all(home[t] == 7 for t in teams)),
    ]
    return checks


# -------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="JSON: tiers, rematches, names")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--attempts", type=int, default=400)
    args = ap.parse_args()
    cfg = json.load(open(args.config))
    tiers = {k: list(v) for k, v in cfg["tiers"].items()}
    rematches = [tuple(r) for r in cfg["rematches"]]
    names = cfg.get("names", {})
    teams = [t for four in tiers.values() for t in four]

    assert len(teams) == 12 and len(set(teams)) == 12, "need 12 distinct franchises"
    tier_of = {t: k for k, four in tiers.items() for t in four}
    for a, b in rematches:
        assert tier_of[a] == tier_of[b] == "T1", \
            f"both rematch teams must be Tier 1 -- got {a}({tier_of[a]}) v {b}({tier_of[b]})"

    seed = args.seed if args.seed is not None else random.randrange(10 ** 6)
    rng = random.Random(seed)

    for attempt in range(args.attempts):
        rounds = circle_round_robin(range(12), rng)
        named = label_with_rematches(rounds, rematches, teams, rng)
        sched = assemble(named, tiers, rng)
        if sched is None:
            continue                      # no legal rivalry ordering; reshuffle
        sched, flips = balance_home_away(sched, teams)
        checks = validate(sched, tiers, rematches, teams)
        if all(ok for _, ok in checks):
            break
    else:
        sys.exit(f"no valid schedule in {args.attempts} attempts (seed {seed})")

    nm = lambda t: names.get(t, t)
    print(f"# seed {seed} · attempt {attempt + 1} · {flips} orientation flips\n")
    for w in sorted(sched):
        tag = "   [RIVALRY WEEK]" if w in RIVALRY_WEEKS else ""
        print(f"WEEK {w}{tag}")
        for a, h in sched[w]:
            t = f"  ({tier_of[a]})" if w in RIVALRY_WEEKS else ""
            print(f"   {nm(a):<9} at {nm(h):<9}{t}")
        print()
    print("CHECKS")
    for label, ok in validate(sched, tiers, rematches, teams):
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    print("\nMFL IMPORT BLOCK  (League > Setup > Fantasy Schedule Setup)")
    print("!! Saving OVERWRITES the entire schedule and there is no undo.")
    print("!! Copy the existing contents of that box to a file first.\n")
    for w in sorted(sched):
        for a, h in sched[w]:
            print(f"{w:02d},{a},{h}")


if __name__ == "__main__":
    main()
