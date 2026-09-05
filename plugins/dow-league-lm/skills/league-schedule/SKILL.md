---
name: league-schedule
description: "Build or correct the annual regular-season schedule for the Dynasty of Whiners league (MFL 29557) — computes the three tiers from prior-season results, generates a validated 14-week schedule, and produces the MFL import block. Use for \"make the schedule\", \"schedule for next season\", rivalry weeks, or scheduling tiers."
---

# League Schedule

Fourteen weeks, twelve teams. This replaces steps 4–10 of the constitution's LM
procedure — the external Streamlit generator, the CSV export, the manual
team-number assignment, and the "big ass random numbers" duplicate checksum.

Paul Gaffney has built this by hand since 2024 and it takes him hours. He knows
this tool exists. Treat his judgement as the reference, not this file.

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
`build_schedule.py` prints the schedule, the eight checks, and the MFL block, and
asserts both rematch teams are Tier 1 — the assertion that would have caught the
2026 error.

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

### The eight checks — all must pass

    84 games, 14 weeks x 6
    round robin: all 66 pairings exactly once
    rivalry weeks all within-tier
    doubled pairings are exactly the within-tier pairings
    no back-to-back around a rivalry week
    every team plays 14 games
    week 1 carries both rematches
    home/away balanced 7H/7A for all 12

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

**Ship exactly one import file.** Several near-identical candidates next to an
irreversible paste-and-save button is how the wrong one gets used.

## Never automate these

- **Writing to MFL.** `League > Setup > Fantasy Schedule Setup`, format
  `week,away,home`, zero-padded, 84 rows. **Saving overwrites the entire
  schedule with no undo.** Always save the existing contents to a file first,
  and let a human paste.
- **Writing to the league gSheet.** It also holds member phone numbers and email
  addresses. The LM procedure duplicates a proposal tab rather than overwriting;
  follow that, by hand.
- Build before the NFL releases its regular-season schedule, to prevent bye-week
  manipulation.

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
