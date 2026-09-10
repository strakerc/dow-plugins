---
name: league-franchise-tags
description: "Invoke before any league tool call for franchise-tag questions in the Dynasty of Whiners league (MFL 29557) — positional floors from last season's top-5 salaries, per-player tag prices, eligibility, and an auditable breakdown to check against the gSheet. Use for \"what would it cost to tag X\", \"is he eligible for the tag\", \"what's the tag price\", \"franchise tag values\", or tagging decisions."
---

# Franchise tag values — Seattle/Pgh Dynasty League

> **Before you answer — every skill in this league follows these five lines.**
> 1. **Names only.** Owners by first name, players by name, teams by team name. Never a
>    franchise id (`0001`), a pick code (`FP_…` / `DP_…`), a player id, an MFL username,
>    an email or a phone number — not in a table, not in parentheses after a name, not
>    to show which record you matched.
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
>    email → `league-contacts`.

Computes the annual franchise tag prices for MFL league `29557`. Output is built to be
**audited against Straker's gSheet tag tab**, not trusted blindly — always show the five
contracts behind each average, with player names and owners, so a mismatch can be traced
to a specific row.

Scope: tag arithmetic only. General rules lookups belong to `league-rules`; this is the
first slice of the planned `league-contracts` skill, and cut / extension / dead-money
math is not here yet.

> **Editing hazard — never write a bare single-digit dollar amount in this file.**
> A literal dollar-sign-then-5 token is destroyed by argument substitution when the skill
> is invoked with arguments: it is replaced by a word from the invocation string, so the
> central rule renders as "add 2026" instead of "add five dollars". Observed live,
> Sep 2026. Amounts of two or more digits like $54 are unaffected, and the file on disk is
> fine — the corruption happens at load time only, which is why it is invisible when
> editing. **Write single-digit amounts as bare numbers with the unit in words**
> (`plus 5 dollars`, `+5`), as done throughout. All figures here are US dollars.

## The rule

A tagged player's price is the **greater** of two branches:

1. **Positional floor** — `ceil(average of the top 5 salaries at that position last season) + 5`
2. **Personal floor** — `the player's own previous salary + 5`

In practice branch 2 usually wins for genuinely expensive players. All three tags applied
in 2025 were branch-2 outcomes (McCaffrey $74→$79, Davante Adams $71→$76, Mayfield
$56→$61). Branch 1 is the backstop that stops a cheap contract being tagged cheaply, and
it has **never actually set a price in league history** — so the first year it does,
flag that explicitly rather than quoting it as routine.

### Settled interpretations — confirmed by Straker, Sep 2026

| Question | Answer |
|---|---|
| Do **IR** players count toward the top 5? | **Yes.** Salary is salary regardless of slot. In 2026 this moved QB $48→$54 and WR $54→$59 |
| Do **taxi** players count? | **Yes**, same reasoning. Has never bound — taxi salaries are far too low |
| Do **franchise-tagged** contracts count? | **Yes.** This matters enormously — see the ratchet below |
| Which snapshot is "last season"? | End-of-season (week 22) rosters, **union** players dropped mid-season |
| Rounding | **Ceiling the average, then add 5 dollars.** `ceil(48.2) = 49`, then 49 + 5 = $54 — not 48 + 5 = $53 |

Rounding *order* does not matter — `ceil(x) + 5 == ceil(x + 5)` for integer offsets — but
rounding *mode* does. Round-to-nearest would have given QB $53 and WR $58 in 2026.

### The tag price feeds itself

Because tagged contracts count, **a tag inflates next year's floor at that position.** In
2026 the top salary at QB, RB and WR was in every case a player franchised in 2025 —
Mayfield $61, McCaffrey $79, Adams $76. Each was priced off the personal branch, then
became a top-5 input lifting the floor for everyone else. The 2025 RB top five contains
*two* tagged contracts, Barkley $75 and Henry $73, at #1 and #3.

This is a real ratchet, not a rounding artifact: positions where nobody tags expensively
stay cheap, and a position where someone tags a star gets more expensive to tag the
following year. Surface it whenever someone asks why a floor moved.

## Eligibility gates — check before quoting a price

A price is meaningless if the player cannot be tagged. The gSheet states three exclusions
directly, and this is the cleanest statement of the rule anywhere:

> 1. Players that were franchised the previous season
> 2. Players that are currently under contract
> 3. Players that have been franchised more than twice by the same owner

Note the exact wording on #3 — **"more than twice"**, so a second tag by the same owner is
legal and a third is not. Plus, from the constitution:

- **One active tag per team.** A trade creating a second forces a conversion.
- A player on a **short-term** contract before the tag cannot take another short-term
  afterward — only long-term or an extension.
- A tag **freezes contract progression**: a player tagged after year 1 of a short-term can
  later be signed off the *pre-tag* salary. Do not compound the tag price into future-year
  estimates.

MFL does not track tag history. Reconstruct it by scanning past `get_rosters` snapshots
for `contractInfo` of `Franchise` or `Franchise Tag` — MFL has used both strings.

## Data recipe

All calls go to the MyFantasyLeague worker, league `29557`.

1. **`get_rosters` with `season=<last season>`** — the week-22 snapshot, with `salary`,
   `status` (ROSTER / TAXI_SQUAD / INJURED_RESERVE), `contractInfo`, `contractStatus` and
   `drafted` intact. This is the base pool.
2. **`get_salary_adjustments` with `season=<last season>`** — the audit trail for players
   dropped mid-season, who are missing from the week-22 snapshot. Each `description`
   parses as `Dropped <Name> <TEAM> <POS> (Salary: $N, Type of Contract: X, Year: N,
   Signed Through: YYYY)`. Union these in, keeping the **highest** salary if a player
   appears in both (dropped by one team, re-signed by another).
3. **`get_players` with an explicit ID list** — resolve positions. Never omit `players`;
   the full export is megabytes.
4. Group by position, sort by salary descending, take the top 5, average, ceil, add 5.
   The position is the one `get_players` returned for that id and nothing else — a
   name that sounds like a receiver is not a receiver, and a contract at the wrong
   position is out however high its salary. Carry the position into the table so a
   misfiled row is visible.

### Timing: not a constraint, if you use the right source

The pinned LM note says *"don't let people start dropping players before you compute the
franchise tags."* That warning is real **only against current-year rosters**, which is how
this was done by hand for years — one early drop destroys the inputs.

Against last season's frozen week-22 snapshot the hazard cannot occur, and the salary
adjustments recover the drops the snapshot misses. **So run it whenever you like, before
or after cuts.** Do not silently fall back to `get_rosters` with no season — that
reintroduces the exact flaw.

Related trap: MFL's live feed **blanks `contractInfo`, `contractYear`, `contractStatus`
and `salary` the moment a player is cut.** Historical questions need the season snapshot.

### Do not skip position resolution with a salary threshold unless you verify it

Resolving every rostered player is ~300 IDs. Filtering to salaries of 20 dollars and up
first is much cheaper and safe in practice, **but you must then assert that the
5th-highest salary at every position exceeds the threshold.** If any position's cut lands
at or below it, widen the threshold and re-resolve. In 2026 the cuts were QB $41 / RB $54
/ WR $36 / TE $28 — ample headroom, but not guaranteed in a future year, especially at TE.

## Output format

Two blocks. The summary is what gets copied into the gSheet; the breakdown is what makes
it auditable.

```
Pos   Top-5 salaries              Average   Tag floor
QB    61,49,45,45,41                 48.2         $54
RB    79,75,66,59,54                 66.6         $72
WR    76,58,51,45,36                 53.2         $59
TE    55,34,32,31,28                 36.0         $41
```

Then, per position, the five contracts with **player name, salary, owner, contract type,
and an IR/taxi marker**, plus the next player outside the cut. The owner is the
first name of the person whose roster holds the contract, from `get_league`'s
`owner_name` for that franchise — one row reads "Owen Frost — $30 — Bram", never a
franchise id. The near-miss matters: it
shows how much headroom the number has, and it is where a gSheet disagreement usually
resolves.

When asked about a specific player, give `MAX(floor, his salary + 5)`, say **which branch
bound**, and state each eligibility gate with its evidence: his contract's final year
from the current roster (a tag is for the season after it ends), and that no snapshot
pulled shows a `Franchise` or `Franchise Tag` contract on him. If tag history further
back was not checked, say so in one line rather than leaving the gate half-answered.

When asked for more than one year, show both breakdowns and **name the contracts that
entered and left the top 5.** That is the actual explanation for the change, and it is
what someone wants when they ask why a number moved.

## Verification

Three fixtures, all reproduced from MFL data independently of the gSheet. Any change to
this skill should still reproduce all of them.

**2026 floors** — QB $54, RB $72, WR $59, TE $41. Matches the gSheet's 2026 row four for
four.

**2025 RB floor** — from the 2024 week-22 snapshot: Barkley $75, McCaffrey $74 (IR),
Henry $73, Mixon $68, Kamara $65. Sum 355, average exactly 71.0, ceil 71, plus 5 = **$76**.
Matches the gSheet. Note the average landing on a whole number — a case where the
rounding mode happens not to matter.

**2025 tags applied** — McCaffrey $79, Davante Adams $76, Mayfield $61 all reproduce from
the personal branch off their 2024 salaries ($74 / $71 / $56).

**Sanity-check a new number against the historical series** before reporting it.
These are the real league's past floors and they are never the answer to a
question — every price is computed from the data pulled in this run, and quoting
a figure from this table instead (a `$59` for WR, say) is the exact failure the
footer forbids:

| Year | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| QB | $31 | $35 | $40 | $41 | $45 | $51 | $55 | $54 |
| RB | $91 | $90 | $98 | $101 | $96 | $71 | $76 | $72 |
| WR | $72 | $75 | $78 | $77 | $77 | $64 | $66 | $59 |
| TE | $32 | $27 | $33 | $29 | $33 | $40 | $40 | $41 |

These are **not monotonic** — RB fell $96→$71 and WR $77→$64 between 2023 and 2024, a
league-wide repricing rather than a calculation change. So a large move is not by itself
evidence of a bug; trace it to the specific contracts that entered or left the top 5.

## Other traps

- **Stale IR flags.** MFL carries IR designations across seasons. Irrelevant to the tag
  arithmetic (IR salaries count in full here) but do not let a stale flag leak into cap
  commentary alongside the tag price.
- **Never quote a player ID from memory.** Resolve every ID through `get_players`.
- **Never print an id in the answer** — no player ids, no franchise ids. Owners go
  by first name and players by name; "Elliot Brandt (WR, DEN), salary $18" is the
  whole identification. The first eval run of this skill (9 Sep 2026 PT) produced a
  correct price with `id 10003` beside the name, because this rule was stated in
  every other skill and not here.
- **Salary adjustment rows are load-bearing.** They are the only surviving record of a
  mid-season drop's salary and an input to the next year's averages. If asked about
  clearing them during the annual cleanup, say so.
- State the source season and the pull date inline with the numbers.

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
