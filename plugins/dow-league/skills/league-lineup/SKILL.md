---
name: league-lineup
description: "Set a weekly lineup in the Dynasty of Whiners league (MFL 29557) — the highest-projected legal ten from a franchise's own roster, and separately what changes once the specific opponent that week is priced in. Use for \"set my lineup\", \"who should I start\", \"start or sit\", \"lineup for week N\", \"should I start X over Y\", or \"optimize my lineup\"."
---

# League Lineup

Two lineups, never merged: **the highest-projected legal ten**, and **what changes
once you look at who you are playing**. The first is arithmetic. The second is a
judgement about variance, and it is the part no public tool does.

> Straker's standing instruction, verbatim: *"They are allowed to be separate!"*
> Show what the raw measure says, then show the override, and let the owner
> decide. Never collapse the two into one recommendation, and never quietly drop a
> candidate because this skill dislikes it.

---

## The projection source, and the one field that matters

`get_projections` is the only forward-looking source in this stack. Two things it
is **not**, and reaching for either is the likeliest way this skill ships
confidently wrong:

- `get_player_scores` is points **already scored**. Authoritative, and useless for
  a lineup — it exists only after the games.
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
return a legal full lineup and say that it is legal.**

### 2. The pool

`get_rosters`, then **filter on `status`** — only `ROSTER` is startable. Never
`INJURED_RESERVE`, never `TAXI_SQUAD`.

Resolve every id through `get_players`. **An id you did not resolve is unexamined,
not known.** Here that means starting somebody who was traded away.

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

### 3. The objective optimum

Fill the highest-projected legal ten. No judgement, no correlation, no filtering.
**Its own labelled table**, with each player's projection shown.

### 4. Predict the opponent

`get_matchups` gives the opposing franchise for that week. Run step 3's optimiser
on their roster.

**Say that it is a prediction.** The entire correlation layer is conditional on
it. **Weight it by certainty:** a manager's only startable quarterback is
near-certain; their fifth receiver is a coin flip. Lean on the confident parts and
say which parts are not.

### 5. The correlation layer

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

**It breaks ties. It does not overturn material gaps.** Moving a player two or
more projected points behind is rationalising, not strategy — if you do it anyway,
say plainly what is being given up.

### 6. Risk flags — the shortlist, not the roster

For the recommended ten plus close alternatives only: injury and practice reports,
snap and touch share, depth-chart and quarterback changes, game total.

**One clause after the name, never a paragraph**, and only where it could change
the decision. A resolved minor injury gets four words or nothing. Do the research
up front with the flags ready — do not go looking mid-decision.

**Never treat variance as a reason to avoid.** A wide spread among sources means
"go look into this", not "fade this". That misread has already cost this league a
draft pick.

### 7. Say when it locks

MFL locks each player at their own kickoff, not at a single weekly deadline. Name
the **earliest-starting recommended player and their kickoff, in Pacific with the
zone labelled.**

---

## Must not

- **No writes to MFL.** A human enters the lineup.
- **No full recommended lineup for another franchise.** Predicting the opponent's
  starters is in scope; producing their lineup for them is not.
- **Never surface a franchise id, player id, MFL username, email or phone number**
  as a side effect. Owners go by first name.
- **Never present the correlation-adjusted lineup alone.** Both tables, labelled.
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
