---
name: league-lineup
description: "Invoke before any league tool call to set a weekly lineup in the Dynasty of Whiners league (MFL 29557) — the highest-projected legal ten from a franchise's own roster, and separately what changes once the specific opponent that week is priced in. Use for \"set my lineup\", \"set my week N lineup\", \"who should I start\", \"start or sit\", \"lineup for week N\", \"should I start X over Y\", or \"optimize my lineup\". Never submits a lineup to MFL."
---

# League Lineup

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
>    email → `league-contacts`, who has a player or how bad his injury is →
>    `league-player-status`.

Two lineups, never merged: **the highest-projected legal ten**, and **what changes
once you look at who you are playing**. The first is arithmetic. The second is a
judgement about variance, and it is the part no public tool does.

> Straker's standing instruction, verbatim: *"They are allowed to be separate!"*
> Show what the raw measure says, then show the override, and let the owner
> decide. Never collapse the two into one recommendation, and never quietly drop a
> candidate because this skill dislikes it.

Beside them sits a short third section, **form and matchup** (step 7): what each
player has actually scored here, and how the defence he faces has treated his
position. It is context the owner weighs. It never moves a number in either
lineup.

---

## The projection source, and the one field that matters

`get_projections` is the only forward-looking source in this stack. Two things it
is **not**, and reaching for either is the likeliest way this skill ships
confidently wrong:

- `get_player_scores` is points **already scored**. Authoritative, and **never
  the ranking input** — a lineup ranked on last month is a lineup for last
  month. Step 7 reads it as context beside the projection, and nowhere else.
- `get_dynasty_rankings`, `get_rookie_rankings` and `get_player_values` are
  **dynasty asset values**. A player can be a top-fifteen dynasty asset and the
  wrong week-9 start.

### Calling it

**One call: `position="ALL"`, with an explicit `week`.** All four lineup positions
are needed every run, and the upstream rate-limits — four scoped calls cost four
times the pressure for the same data.

**`week` is required and there is no default, deliberately.** Omitting it upstream
returns the season-long total with nothing in the payload marking it as such.
**Assert the echoed `week` matches what you asked for** before using a single
number. It comes back as a string.

If a call returns a rate-limit error, wait and retry — it clears in about a
minute. Do not treat it as a dead source and do not substitute another one.

### 🔑 `points_half` is at the TOP LEVEL of each player row

The tool returns a trimmed, **flat** shape. Each player is:

```json
{"mflid": 16211, "name": "Puka Nacua", "position_id": "WR",
 "team_id": "LAR", "points_half": 16.8}
```

**Read `points_half`, not `stats.points_half`.** Upstream nests it under `stats`;
this tool flattens it. Reading the nested path returns `undefined` on every row,
which presents as "no projections available" rather than as an error — a whole
lineup silently unscored.

`points_half` is the half-PPR figure, which is this league's scoring. The
untrimmed payload carries `points` and `points_ppr` beside it; reading either is a
quiet, uniform bias across every recommendation this skill would ever make.

Pass `full: true` only if a stat beyond the projection is genuinely needed. It is
about four times the size.

---

## The method, in order

### 1. Slots from live data, every run

Read the `starters` block from `get_league`. **Do not hardcode any of it** — the
league has changed its lineup shape before.

`partialLineupAllowed` matters as much as the counts: when it is `NO`, an
under-filled lineup is a rules problem and not merely a scoring one. **Always
return a legal full lineup and say that it is legal** — or, when the roster
cannot field one, say that instead (step 4).

### 2. The pool

`get_rosters`, then **filter on `status`** — only `ROSTER` is startable. Never
`INJURED_RESERVE`, never `TAXI_SQUAD`.

Every roster row carries the player's name, position and NFL team. **A row
that arrives without a name is unexamined, not known**: look that id up with
`get_players`, and if it returns nothing, say a roster slot could not be
identified rather than starting it. Here that means starting somebody who was
traded away.

**Build the pool as one line per roster player — name, status, projection or
NONE — before writing anything.** That list is your working, not the answer: the
answer shows the tables and the "left out and why" line, and every NONE appears
there by name as having no projection.

**The roster is the list of players; the projection payload is only numbers.**
Build the pool from `get_rosters`, then attach projections to it — never the
other way round. A run that starts from the projection rows never
sees the player who has no row, which is exactly the player this section says to
name. That is how Harlan Voss went missing in two of three eval runs on 9 Sep
2026 PT, in answers that otherwise followed every rule.

**Join projections to the roster on `mflid`, never on name.** Every projection row
carries MyFantasyLeague's own player id; non-null values are unique. Name matching
is the standard failure mode for this kind of join and this payload removes the
need for it.

Two cases that look alike and are not:

- **A roster player with no matching row in the payload has no projection.** Say
  so by name and leave him out of the optimum. Silently dropping him is how a
  startable player goes missing; inventing a number is worse.
- **A player present with `points_half` of zero is projected zero.** That is data,
  not absence. Rows are not filtered server-side precisely so these stay
  distinguishable.

### 3. The lineups already submitted

`get_weekly_results` with the same `week` and no `season` returns every
franchise's block for that week. Before the games it is the lineups as
submitted: `starters` is a comma-separated list of player ids with a trailing
comma, `nonstarters` the bench, and the scores are blank. Lineups are visible
league-wide in this league, on the site and here, so the opponent's block is a
page every owner can already see.

- Find the owner's block: the entry whose `id` is the owner's franchise. **If
  it has a `starters` field, the lineup is submitted. Write it out as its own
  labelled list, by name, before the optimum.** Every id in it is already in
  step 2's pool, named there, so nothing needs a lookup. An id in `starters`
  that is not on the roster is a player moved since the lineup was set: name
  him and say the slot is empty until it is refilled.
- **Only a block with no `starters` field, or an empty one, means not
  submitted yet** — not an empty lineup, not an error. Check the field before
  writing that sentence: one run (sonnet, low effort, 13 Sep 2026 PT) called a
  submitted lineup "not entered" with all ten ids sitting in the payload, and
  narrated the franchise id while doing it. The list above is how that answer
  cannot happen — it exists, or the field is absent or empty.
- A `comments` field is an owner's note to themselves. Any `optimal` or
  `shouldStart` MFL adds once games score is hindsight from actual points. None
  of that is data for any table; leave it out.
- If the tool is not on the connector at all, the connector predates it. Say the
  submitted lineup could not be read from MFL, and give the two tables from the
  tools that did answer. Never guess what was submitted, and a plan the owner
  then types into chat is their word, compared as such, not MFL's.

The owner's `matchup` entry also names the opponent: the other franchise in it.
Keep that block; step 5 reads it.

### 4. The objective optimum

Fill the highest-projected legal ten. No judgement, no correlation, no filtering.
**Its own labelled table**, with each player's projection shown.

How: within a position the best choice is always its top projections, so try
every way of splitting the ten across positions that the limits allow, fill
each split from the top down, and keep the highest total. That is exhaustive,
not a heuristic — it rebuilt all 36 real 2025 lineups (twelve teams, weeks 3, 8
and 13), and a million random legal lineups per team never beat it
(`validation/lineup-backtest/`).

**Check the ten before you show it**, against the payloads you already hold:

1. **Exactly the `count`** from step 1's `starters` block. Not nine, not eleven.
2. **Every position inside its `limit`.** The ten biggest projections ignore
   the limits, so they always total at least as much as the legal answer. A
   higher total than the method gives is a warning, not a better lineup.
3. **Every player is in step 2's pool** — this owner's roster, status `ROSTER`.
   The projection payload lists the whole league; a name in it is not a player
   on this roster.
4. **Nobody twice.**
5. **Add the total again from the table's own numbers** and print it under the
   table.

If a line fails, fix the ten and check again; never show a table that failed
one. Then say it is legal, as step 1 requires.

**If no split meets every limit from the pool** — the only tight end on injured
reserve, say — there is no legal ten. Say so, name the position that is short
and anyone at it on injured reserve or the taxi squad, and show no optimum table.

The back-test proves the method, not the model carrying it out: on 13 Sep 2026
PT haiku started a player off another team's roster in one run, and added a
correct ten up 5.6 points wrong in another.

**Close the table with one line naming every startable player left out and why**
— no projection row, projected zero, position full. That line is where a player
with no projection gets named; without it he goes missing silently, which is
exactly what happened in one of two eval runs on 9 Sep 2026 PT.

**Then set it against what is submitted.** Name every difference player for
player with the projection gap, in one line each: "Luca Ferro is in for Wren
Castillo, 0.0 against 5.5". Say when the submitted lineup already is the optimum.
When nothing is submitted, say so and give the ten as the lineup to enter.

### 5. The opponent: read, or predict

The opponent is the other franchise in the owner's `matchup` entry from step 3.
`get_matchups` is the fallback for when weekly results could not be read. Their
roster is already in the `get_rosters` payload, which returns every franchise
with names on the rows, so nothing needs a lookup.

**If their block in step 3 has `starters`, that is their lineup, not a
prediction.** Use it, say it was read from MFL, and note that any player whose
game has not kicked off can still be swapped. Do not run the optimiser on their
roster and present that instead of what they submitted.

**Only when they have not submitted, predict.** Run step 4's optimiser on their
roster and **say that it is a prediction.** The entire correlation layer is
conditional on it. **Weight it by certainty:** a manager's only startable
quarterback is near-certain; their fifth receiver is a coin flip. Lean on the
confident parts and say which parts are not.

### 6. The correlation layer

Five relationships. They differ in strength **and in direction**, and direction is
the half that gets dropped.

| Relationship | Effect | Margin | Strength |
|---|---|---|---|
| **Your pass-catcher, their QB** | The same play pays both, and the receiver gains more per catch | **Compresses** | **Strongest.** The canonical play |
| **Your RB, their RB, same backfield** | Touches you take are touches they do not get | **Widens** | **Strong.** A direct block |
| **Your pass-catcher, their pass-catcher, same team** | Two effects at once: a good team day lifts both, a finite target pool sets them against each other | **Widens** as their player's target share rises; near neutral for their third receiver | Moderate. Do not overstate it |
| **Any other same-team pair** | A finite team scoring pool — your running back and their tight end, say | **Widens**, weakly | Weak. Name it; do not act on it alone |
| **Same game, different teams** | A shootout lifts both; a defensive game sinks both | **Compresses** | Weak. A variance note, nothing more |

**Read Margin against the favourite/underdog line below, never on its own.**
Strength says how far a pairing moves the spread of outcomes. It does not say
whether you want that. Compressing the margin is what a favourite wants and
exactly what an underdog must avoid — and the strongest row in this table is a
compressor, so reading only the Strength column gets the magnitude right and the
sign backwards.

The fourth row is a catch-all and it is load-bearing. The others name specific
pairings; a real matchup does not. Your running back and their tight end on the
same NFL team is not row 1, 2, 3 or 5 — row 5 is scoped to *different* teams —
and an earlier version of this table said nothing whatever about that case while
both players were near-certain starters. When a pair fits no row above it, the
default is the fourth: weakly widening, worth naming, never decisive.

**Correlation is a variance tool, not a points tool.** Compare the two projected
totals first and **state which side of the line this matchup is on before
recommending any swap**:

- **A clear favourite should reduce variance** and take known usage.
- **A clear underdog should take ceiling and leverage.**
- **A close projection is still a side.** Name the marginal favourite by the
  number, then use the table as the tiebreaker below — “coin flip” alone names
  no side (sonnet at high effort, 14 Sep 2026 PT).

**It breaks ties. It does not overturn material gaps.** Moving a player two or
more projected points behind is rationalising, not strategy — if you do it anyway,
say plainly what is being given up.

**End the opponent section with its own verdict, in one line:** what changes
from the objective ten once this opponent is priced in, or "no change to the
ten". A swap the optimum already made is not this layer's verdict; agreeing with
the first table is still a conclusion, so write it. On 13 Sep 2026 PT opus at
low effort noted that step 4's swap "happens to" suit the matchup and never
said whether anything changed, which is the two lineups merged by omission.

### 7. Form and matchup — named beside the projection, never added to it

> Straker, 21 Sep 2026 PT: a receiver who would not normally start, facing one
> of the worst pass defences in the league — "that is at least worth
> acknowledging and considering in the lineup recommendation."

**The projection already prices both.** FantasyPros builds the opponent and
recent usage into `points_half`, so "a few points for the matchup" counts the
matchup twice. Neither table changes here. What this step adds is what sits
behind the numbers, from payloads and never from a defence's reputation.

**The defence each player faces — every startable player in step 2's pool.**

1. His opponent: find his `team` in `get_nfl_schedule` (the same call step 9
   reads; make it once). The other side of that game is who he faces. No game
   that week is a bye; say so.
2. `get_points_allowed`, no arguments: the opponent's row, then the player's
   own position in it — `per_game`, `rank`, and the team's `games`. **Rank 1
   allows the fewest; the highest rank is the softest matchup.** It is scored
   under this league's rules and it is per position, so it can tell a defence
   that is soft against tight ends from one that is soft against receivers.
   Lead with it.
3. The second read, already in the schedule payload: the opponent's
   `passDefenseRank` for a quarterback, receiver or tight end, `rushDefenseRank`
   for a running back. 1 is the stingiest. These rank a whole unit and cannot
   separate a receiver from a tight end, which is why they come second.

Say how much football a rank rests on: "30th of 32 against receivers, on two
games". `through_week` and `games` are in the payload; early in a season every
rank is a small sample, and the week in progress is never in it. A blank rank,
a `gamesUnavailable` note, or `get_points_allowed` missing from the connector
(it predates the tool) means that source could not be read: say so, use the
other, and if both are gone say the matchup could not be read. Nothing about a
defence comes from memory.

**Season form — the ten, plus any left-out player who projects no worse than
three points below the lowest projection in the ten.** `get_player_scores`
twice, with `players` set to those ids comma-separated: `week="AVG"` and
`week="YTD"`. AVG is YTD divided by the weeks he has a score for — a week he
played and scored nothing counts, a week he sat out does not (measured 21 Sep
2026 PT). So YTD divided by AVG is how many games the average rests on; say it
when it is one or two. An id with no row, or an average of zero, has not
scored this season: say "no points yet this season" and divide nothing. Do not
build form from single weeks: a week that comes back 0 for every player was not read (measured 21 Sep
2026 PT), and it is not a scoreless week.

**What gets written: one clause after the name, only where it is notable.**

- The opponent is in the softest or the stingiest quarter of `ranked_teams`
  for his position — of 32, ranks 25 and up, or 8 and down.
- His season average is four or more points away from this week's projection,
  either way.

Everyone else gets nothing; twenty clauses of "average matchup" bury the two
that matter. Those two thresholds only choose what earns a clause, and the
quarter-of-the-table gap below only chooses what gets offered. All three are
judgement, not back-tested (21 Sep 2026 PT), and none of them decides a start.

**What it may change is what step 6 may change: ties, not material gaps.**

- A left-out player **within two points** of a starter he could legally
  replace, whose matchup is the better of the two by a quarter of the table
  or more (8 ranks of 32), is a swap candidate. Name him, the starter, both
  ranks and the projection given up. The owner decides.
- **Further back than that, he is still named** — "Teo Alvarez faces the
  softest defence against receivers in the league, on two games, but projects
  3.4 behind Owen Frost: worth knowing, not enough to start him." A soft
  matchup the owner never hears about is this skill quietly dropping a
  candidate.
- A player projected zero or with no projection is not a matchup candidate.
  No defence is soft enough to help a player who is not expected to play.
- Form far from the projection is "go look" — a role change, a return from
  injury, one huge game — not a verdict in either direction (step 8's rule
  about variance applies here unchanged).

**Its own labelled section, after the opponent section, ending in one line:**
the swap candidate it raises with the points given up, or "no change to the
ten". Never folded into the first table, and never a third lineup.

### 8. Risk flags — the shortlist, not the roster

For the recommended ten plus close alternatives only: injury and practice reports,
snap and touch share, depth-chart and quarterback changes, game total.

**One clause after the name, never a paragraph**, and only where it could change
the decision. A resolved minor injury gets four words or nothing. Do the research
up front with the flags ready — do not go looking mid-decision.

**Never treat variance as a reason to avoid.** A wide spread among sources means
"go look into this", not "fade this". That misread has already cost this league a
draft pick.

### 9. Say when it locks

`get_nfl_schedule` with the same `week` is the kickoff source. Each game carries
`kickoff` in Unix seconds and `gameSecondsRemaining` (3600 before kickoff, 0 at
final); each side's `id` is the same code as `team` on a roster row, which is
the join. Convert every kickoff to Pacific and write the zone -- with the analysis tool or a shell one-liner, never arithmetic in your head (the timestamps rule in league-trade-history; a head conversion has put a July trade in March).

MFL locks each player at their own kickoff, not at a single weekly deadline.
**Join every one of the recommended ten to his game by `team`, and put all
ten in the answer with team name and kickoff before you name the earliest** —
never scan the schedule for teams you remember (opus at low effort said nobody
played Thursday while two of the ten did, 14 Sep 2026 PT).
Name the **earliest-starting recommended players and their kickoff, in Pacific
with the zone labelled** — a Thursday game locks two starters days before the
rest. A player whose game has already started is locked; say so instead of
recommending a swap that cannot be made.

**A kickoff time comes from that payload or it is not stated.** If the tool is
not on the connector, say the lock time could not be determined from the data
and stop there; an estimated "~1:00 PM PT" is a fabricated deadline (10 Sep
2026 PT), and haiku wrote one against this very sentence on 13 Sep 2026 PT
because nothing gave it a real time. Now something does.

---

## Must not

- **No writes to MFL.** A human enters the lineup. A request to submit is
  still a request for the lineup: read the data, give both tables, then say
  the entry is theirs to make. Declining before reading anything answers
  nothing (sonnet at low effort did exactly that, 13 Sep 2026 PT).
- **No full recommended lineup for another franchise.** Reading back what the
  opponent has submitted is in scope, and so is predicting their starters;
  producing their lineup for them is not.
- **Never surface a franchise id, player id, MFL username, email or phone number**
  as a side effect. Owners go by first name — including the line that says whose
  lineup this is, and the line that says a lineup is on file: the owner's name or
  the team name, and **not the word "franchise" at all**, because the word
  invites the number after it. Four of twenty-two answers on the first eval run
  (9 Sep 2026 PT) put the id right there, and on 14 Sep 2026 PT it came back in
  parentheses after a correctly named owner, twice in one answer, both times
  straight after that word.
- **Do not narrate which franchise record you matched, or how.** The owner knows
  who they are. Open with the answer itself; the team name may appear, the id
  never does. Telling the rule as "never print the id" did not stop it (two more
  answers on 9 Sep 2026 PT opened with the id): the id appears because the answer
  was showing its lookup, so do not show the lookup.
- **Never present the correlation-adjusted lineup alone.** Both tables, labelled.
- **Never add points to a projection for form or matchup, and never rank on
  past scores.** The projection already carries both; step 7 names them.
- **Never explain the format back.** The audience knows what superflex is.
- **One blended figure, never two separated by a slash**, where a projection has
  more than one source. Per-source detail on request, out of the default output.

## Where this stops

| Question | Skill |
|---|---|
| What is this player worth as an asset | `league-player-values` |
| Is this proposed trade fair | `league-trade-evaluator` |
| Who do I play in week N, and what tier am I | `league-matchups` |
| Can I do this under the rules | `league-rules` |

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
