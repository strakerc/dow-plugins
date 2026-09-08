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

# Opponent-strength swing worth naming out loud, in points per game. NOT a
# pass/fail threshold -- see opponent_strength() for why there cannot be one.
MATERIAL_SOS_DELTA = 25.0


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


# ------------------------------------------------------ opponent strength
# The eight checks verify that a schedule is STRUCTURALLY valid. They say nothing
# about whether it is competitively neutral, and nothing was looking at that. The
# 2026 correction passed all eight and still moved one owner's average opponent
# down 76 points a game and another's up 76, with everyone else inside +/-2.
#
# So this is a DISCLOSURE, not a check. There is deliberately no pass/fail
# threshold: there is no correct spread, and a threshold would either block a
# legitimate correction or lend false authority to whatever it let through.
def opponent_strength(sched, prior_pf, teams):
    """Mean prior-season regular-season PF of each team's 14 opponents."""
    opps = defaultdict(list)
    for ms in sched.values():
        for a, h in ms:
            opps[a].append(h)
            opps[h].append(a)
    return {t: sum(prior_pf[o] for o in opps[t]) / len(opps[t])
            for t in teams if opps[t]}


def load_import_block(path):
    """Parse a saved MFL import block -- `week,away,home` rows, as printed below.

    Deliberately lenient about comments and blank lines so a file saved straight
    out of MFL's setup box, or one of this script's own outputs, both work.
    """
    sched = defaultdict(list)
    for raw in open(path):
        parts = [p.strip() for p in raw.strip().split(",")]
        if len(parts) != 3 or not parts[0].isdigit():
            continue
        sched[int(parts[0])].append((parts[1], parts[2]))
    return dict(sched)


def compare_problems(old, teams, prior_pf, nm):
    """Reasons a compared schedule cannot yield an honest delta. Empty == usable.

    Checked BEFORE any arithmetic: opponent_strength indexes prior_pf directly,
    so an unknown franchise in the compared file is a KeyError that would abort
    the run and take the import block with it.
    """
    out = []
    want = len(teams) // 2 * 14
    games = sum(len(v) for v in old.values())
    if games != want:
        out.append(f"parsed as {games} games, expected {want}")
    named = {t for ms in old.values() for m in ms for t in m}
    unknown = sorted(named - set(prior_pf))
    if unknown:
        # nm() resolves an id to an owner name; this file's rule is that ids stay
        # inside the MFL import block. An id with no name is a corrupt row and the
        # raw token is the only identifying thing left to print.
        out.append("names franchises with no prior_pf: " +
                   ", ".join(nm(t) for t in unknown))
    opps = Counter()
    for ms in old.values():
        for a, h in ms:
            opps[a] += 1
            opps[h] += 1
    wrong = sorted(t for t in teams if opps[t] != 14)
    if wrong:
        out.append(f"does not give 14 opponents to {len(wrong)} of {len(teams)} teams")
    return out


def print_after_only(after, teams, nm):
    print(f"  {'Owner':<12}{'avg opp':>9}")
    for t in sorted(teams, key=lambda x: -after[x]):
        print(f"  {nm(t):<12}{after[t]:>9.0f}")


def print_opponent_strength(sched, prior_pf, teams, nm, compare_path=None):
    print("\nOPPONENT STRENGTH  (avg opponent prior-season regular-season PF, 14 games)")
    if not prior_pf:
        print("  SKIPPED: the config has no `prior_pf`. compute_tiers.py emits it --")
        print("  regenerate season-YYYY.json to get this report.")
        return
    missing = sorted(t for t in teams if t not in prior_pf)
    if missing:
        print("  SKIPPED: `prior_pf` is missing " +
              ", ".join(nm(t) for t in missing) + ".")
        print("  A mean over some opponents is not a strength of schedule.")
        return

    after = opponent_strength(sched, prior_pf, teams)
    print("  A disclosure, not a check -- there is no correct spread.")

    if compare_path is None:
        print_after_only(after, teams, nm)
        print("  Pass --compare <import-block-file> to see the change against an "
              "existing schedule.")
        return

    old = load_import_block(compare_path)
    problems = compare_problems(old, teams, prior_pf, nm)
    if problems:
        # Refuse the delta rather than computing one from a partial opponent set.
        # A truncated file yields deltas of tens of points that are pure artifact
        # and are formatted exactly like real ones -- including the flag telling
        # someone to report them to the league. Same reasoning as the partial
        # prior_pf path above: a mean over some opponents is not a strength of
        # schedule, and a caution above a confident table does not survive being
        # read out loud.
        for p in problems:
            print(f"  CANNOT COMPARE: {compare_path} {p}.")
        print("  Delta suppressed. Showing this schedule only.")
        print_after_only(after, teams, nm)
        return

    before = opponent_strength(old, prior_pf, teams)
    print(f"  {'Owner':<12}{'before':>9}{'after':>9}{'change':>9}")
    rows = [(t, before[t], after[t]) for t in teams]
    rows.sort(key=lambda r: -abs(r[2] - r[1]))
    for t, b, a in rows:
        d = a - b
        flag = "   <-- report this to the league" if abs(d) >= MATERIAL_SOS_DELTA else ""
        print(f"  {nm(t):<12}{b:>9.0f}{a:>9.0f}{d:>+9.0f}{flag}")

    # A team's 14 opponents are all eleven others once plus its three tier-mates
    # again, so the opponent SET is fixed by the tiering alone -- reshuffling the
    # weeks cannot change it. All-zero is the expected result of a regeneration
    # that keeps the tiers, not a broken report. Say so, or it reads as one.
    if all(abs(a - b) < 0.005 for _, b, a in rows):
        print("  All zero, which is correct: both schedules use the same tiers.")
        print("  Every team plays the other eleven once and its three tier-mates")
        print("  twice, so only a TIER change can move these numbers.")


# -------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="JSON: tiers, rematches, names")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--attempts", type=int, default=400)
    ap.add_argument("--compare", metavar="FILE",
                    help="an existing MFL import block; adds a per-owner "
                         "opponent-strength delta to the report")
    args = ap.parse_args()
    cfg = json.load(open(args.config))
    tiers = {k: list(v) for k, v in cfg["tiers"].items()}
    rematches = [tuple(r) for r in cfg["rematches"]]
    names = cfg.get("names", {})
    prior_pf = cfg.get("prior_pf", {})
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
    print_opponent_strength(sched, prior_pf, teams, nm, args.compare)
    print("\nMFL IMPORT BLOCK  (League > Setup > Fantasy Schedule Setup)")
    print("!! Saving OVERWRITES the entire schedule and there is no undo.")
    print("!! Copy the existing contents of that box to a file first.\n")
    for w in sorted(sched):
        for a, h in sched[w]:
            print(f"{w:02d},{a},{h}")


if __name__ == "__main__":
    main()
