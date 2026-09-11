---
name: league-schedule
description: "Invoke before any league tool call when the league manager asks to make, build, rebuild or correct the regular-season schedule for the Dynasty of Whiners league (MFL 29557) — computes the three tiers from prior-season results, generates a validated 14-week schedule, and produces the MFL import block. Use for \"make the schedule\", \"make our 2026 schedule\", \"build the 2027 schedule\", \"schedule for next season\", \"rebuild the schedule\", \"import it into MFL\", rivalry weeks, or the MFL import block. The league's format is fixed and known here, so do not ask what kind of schedule first. Reading a schedule or the tiers back is league-matchups."
---

# League Schedule

> **Before you answer — every skill in this league follows these five lines.**
> 1. **Names only.** Owners by first name, players by name, teams by team name. Never a
>    franchise id (`0001`), a pick code (`FP_…` / `DP_…`), a player id, an MFL username,
>    an email or a phone number — not in a table, not in parentheses after a name, not
>    to show which record you matched. The one exception is the MFL import block, which is machine input.
> 2. **Every time is Pacific, with the zone written** (PT).
> 3. **If the data has nothing for something the owner asked about, say so by name.**
>    Never fill the gap from memory, and never treat a missing value as a low one.
> 4. **Lead with the answer.** Do not narrate the lookups. The league tools are called
>    directly, like any other tool, never through a shell, a script or a file search.
> 5. **Wrong skill? Hand off, do not improvise.** If the question belongs to another
>    skill in this league, invoke that one now: rules and prices → `league-rules`,
>    contract options → `league-contracts`, picks → `league-draft-picks`, tag prices →
>    `league-franchise-tags`, who plays whom and the tiers → `league-matchups`, player
>    worth → `league-player-values`, a proposed trade → `league-trade-evaluator`, a
>    completed trade → `league-trade-history`, lineups → `league-lineup`, phone or
>    email → `league-contacts`, who has a player or how bad his injury is →
>    `league-player-status`.

Fourteen weeks, twelve teams. This replaces steps 4–10 of the constitution's LM
procedure — the external Streamlit generator, the CSV export, the manual
team-number assignment, and the "big ass random numbers" duplicate checksum.

Paul Gaffney has built this by hand since 2024 and it takes him hours. He knows
this tool exists. Treat his judgement as the reference, not this file.

**If the request includes importing, saving or loading the schedule into MFL, say
in the first reply that nothing here writes to MFL** -- saving overwrites the whole
schedule with no undo, so a human saves the existing contents and pastes the
block -- and say it whether or not the schedule can be built yet. Declining the
build because the prior season is unfinished does not excuse the import half of
the question (Sonnet at low effort left it unanswered, 10 Sep 2026 PT).

**2026 is done.** The season was rebuilt on the corrected tiering and imported
7 Sep 2026 PT. If you are asked to build 2026, you are being asked to redo settled
work — read the live schedule out of MFL first.

## Structure — the part the constitution does not spell out

    14 weeks = an 11-week full round robin + 3 rivalry weeks (4, 8, 12)

- The round robin occupies weeks **1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14** and
  contains all 66 pairings exactly once.
- Each tier holds four teams, and a four-team round robin is exactly three
  rounds — which is why there are exactly three rivalry weeks. **Each tier plays
  itself across weeks 4, 8 and 12.**
- So every team plays its three tier-mates twice and everyone else once.
- **The week 1 rematches are not extra games.** They are round-robin games whose
  position is pinned. Both rematch pairs are Tier 1 by construction, so each
  meets again in a rivalry week like any other tier pair.

*Confirmed by auditing a schedule Paul built by hand, not just inferred.*

## The tiers — where this goes wrong

1. **Tier 1: the four teams that played in the final two playoff games** — the
   championship and the 3rd place game. **By playoff finish, NOT by scoring.**
2. **Tier 2:** the four highest of the remaining eight by prior-season
   **regular season** points.
3. **Tier 3:** the other four.

**Two traps, both of which have actually bitten:**

- The constitution used to state the rule two ways, and the wrong version —
  "ranked 1 to 4 in scoring" — produced the 2026 schedule, putting Straker in
  Tier 1 and Gabe in Tier 2. Fixed in the constitution 4 Sep 2026. If you ever
  read a scoring-rank version of this rule again, it is wrong.
- **MFL's standings `pf` is not regular-season points.** It covers every scoring
  week — non-playoff teams play consolation games, so all twelve carry scores in
  weeks 15+. In 2025 every franchise's `avgpf` was exactly `pf / 18`. Subtract
  weeks 15 onward before ranking. Pull weeks until one returns nothing; do not
  assume four.

## Data to gather

All via the league connector, for season **N−1**:

| Need | Call |
|---|---|
| The final two games | `get_weekly_results(season=N-1, week=17)` — the `matchup` array holds exactly the championship and 3rd place game |
| Points for | `get_standings(season=N-1)` → `franchise.pf` |
| Post-week-14 scores | `get_weekly_results(season=N-1, week=15,16,17,18…)` |

Those weekly pulls are large for played weeks (full lineups). Extract only each
franchise's `score` and discard the rest.

## Run it

If `scripts/compute_tiers.py` and `scripts/build_schedule.py` are present:

```
python3 scripts/compute_tiers.py --data prior-YYYY.json --season YYYY > season-YYYY.json
python3 scripts/build_schedule.py --config season-YYYY.json [--seed N]
```

`compute_tiers.py` shows its working and warns when the Tier 2/3 margin is tight.
`build_schedule.py` prints the schedule, the eight checks, **the opponent-strength
report**, and the MFL block, and asserts both rematch teams are Tier 1 — the
assertion that would have caught the 2026 error.

Pass `--compare <saved-import-block>` to get the per-owner opponent-strength
delta against the schedule currently live. `compute_tiers.py` emits the `prior_pf`
the report needs; without it the report says so and skips rather than guessing.

### The algorithm, if the scripts are absent

1. Circle-method round robin over twelve **anonymous** slots → 11 rounds.
2. **Name the rematch participants onto whichever slots meet in round 1**, then
   assign the other eight owners at random. This is the constitution's step 5 and
   it gets the week-1 constraint for free instead of searching for it.
3. Place the 11 rounds into the round-robin weeks.
4. Rivalry weeks: each tier's three-round mini robin across weeks 4, 8, 12.
   **Which round lands in which week is free — 3! per tier, 216 combinations,
   all equally legal.** Reject any with a pairing repeating in an adjacent week;
   score the rest on how far apart each pair's two meetings fall; keep the best.
5. **Balance home/away.** Orientation cannot break any other constraint — they
   all depend on the unordered pair — and perfect balance always exists, because
   all twelve teams play 14 games, so the graph has even degrees and admits a
   7-home orientation. Reach it by flipping directed augmenting paths from a
   home-deficit team to a home-surplus team.
6. Validate. If anything fails, reshuffle and retry.
7. **Compute the opponent-strength disclosure** — method below. It is part of the
   output, not an optional extra, and this prose path is the one most likely to
   skip it.

### The eight checks — all must pass

    84 games, 14 weeks x 6
    round robin: all 66 pairings exactly once
    rivalry weeks all within-tier
    doubled pairings are exactly the within-tier pairings
    no back-to-back around a rivalry week
    every team plays 14 games
    week 1 carries both rematches
    home/away balanced 7H/7A for all 12

### The opponent-strength report — not a ninth check

**A schedule change is never competitively neutral.** Report the per-owner
opponent-strength delta before importing, and name any owner who gains or loses
materially — especially if that owner is the person running this.

The eight checks verify that a schedule is *structurally* valid. Fairness is not a
structural property and they cannot see it. The 2026 correction passed all eight
and still moved one owner's average opponent down 76 points a game and another's
up 76, with everyone else inside two points. Nothing was looking.

There is no pass/fail line here on purpose. There is no correct spread, and a
threshold would either block a legitimate correction or lend false authority to
whatever it let through. It is a disclosure: publish it, name who moved, and let
the league weigh it.

**A delta of zero across the board is the normal result of a rebuild**, not a
broken report. Each team plays the other eleven once and its three tier-mates
twice, so the opponent set is fixed by the tiering alone — only a *tier* change
can move these numbers. Which is exactly why a tier correction is the case that
needs disclosing.

**Computing it without the script.** List each team's fourteen opponents from the
schedule you just built — the other eleven once, its three tier-mates twice.
Average those opponents' prior-season **regular-season** points: `pf` minus weeks
15 onward, the same figure the tiers were ranked on, not raw `pf`. Do the same for
the schedule being replaced, using the same prior-season numbers, and subtract.
Report by owner name, sorted by size of change, and name anyone moving about 25
points a game or more.

Two ways to get this wrong, both of which produce a confident wrong table: using
raw `pf` instead of regular-season points, and averaging over an incomplete
opponent list. If you cannot list fourteen opponents for every team on both
schedules, say the delta cannot be computed rather than reporting a partial one.

## Correcting an existing schedule

Read the live one back first: `get_weekly_results` on a **future** week returns
scheduled matchups with no scores and no lineups — a few hundred bytes. Fourteen
calls reconstruct the whole thing.

If only the tiers were wrong, the fix is usually tiny. Tiers that differ by a
swap of two teams change only the three rivalry weeks, and a four-team round
robin is isomorphic under relabelling — so exchanging those two teams in weeks
4, 8 and 12 corrects it and leaves eleven weeks untouched. Always check whether
the minimal fix works before regenerating from scratch; it preserves Paul's work
and gives a far shorter diff to review.

## Delivering it

**Produce a review sheet, not just the import block.** Paul reviews by reading
matchups, not by parsing `04,0003,0002`. Mark what changed and leave the rest
quiet — his job is spotting differences, not re-deriving 84 rows. An HTML page
or PDF with changed rows shaded works well; a spreadsheet with the schedule, the
changes, the tiers and the import block on separate sheets lets him paste into a
duplicated tab himself.

**If you cannot produce a file, put the review sheet and the import block inline in
the answer.** Never end on a promise to create something; an answer that stops at
"let me create an artifact" delivers nothing (seen 10 Sep 2026 PT).

**Ship exactly one import file.** Several near-identical candidates next to an
irreversible paste-and-save button is how the wrong one gets used.

**Ship the opponent-strength delta with it**, in the review sheet, not buried in
console output. It is the one number in the package that a leaguemate would want
to see before the import rather than after.

## Never automate these

- **Writing to MFL.** `League > Setup > Fantasy Schedule Setup`, format
  `week,away,home`, zero-padded, 84 rows. **Saving overwrites the entire
  schedule with no undo.** Always save the existing contents to a file first,
  and let a human paste.
- **Writing to the league gSheet.** It also holds member phone numbers and email
  addresses. The LM procedure duplicates a proposal tab rather than overwriting;
  follow that, by hand.
- Build **before** the NFL releases its regular-season schedule, to prevent bye-week
  manipulation. That is a reason to build early, never a reason to wait: nothing
  in this procedure needs the NFL schedule.

## Open question for Paul

Whether he cares **which round of a tier's mini robin lands in which rivalry
week**. The optimiser picks purely on spacing and will happily move the title
rematch. If he places it deliberately, that is an unwritten rule and belongs
here — ask before assuming the checks are the whole specification.

---

## If the league tools aren't there

If `get_rosters`, `get_future_draft_picks` and the other league tools are
missing, **the connector is not set up.** This plugin ships no credentials and no
league data — the skills are instructions, and every fact comes from tools.

Say so plainly, and give the fix:

> Ask Straker for your personal Dynasty of Whiners connector URL, then add it at
> **claude.ai → Customize → Connectors**. It is one paste. It has to be a
> personal Claude account — Team and Enterprise accounts can't add their own
> connectors, and the option simply won't appear.

If the tools exist but return a 401, the key is wrong or has been revoked; the
response carries a `help` field saying what to do. Same fix: ask Straker.

**Never answer from memory, from the examples in this file, or from general NFL
knowledge when the tools are unavailable.** There is no league data without the
connector, and a plausible-looking answer is worse than no answer.

---

## Identifiers in the output

- **Keep internal identifiers out of the prose.** Franchise ids belong in the
  MFL import block and nowhere else — that block is machine input and must keep
  them. Everywhere a human reads, use owner names: "Straker at Pat in week 6",
  never `0001` v `0002`.
