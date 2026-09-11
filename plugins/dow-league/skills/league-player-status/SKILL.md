---
name: league-player-status
description: "Invoke before any league tool call when an owner asks who has a player, whether a player is available, or how bad a player's injury is in the Dynasty of Whiners league (MFL 29557) — which owner rosters him and in what slot, and his injury status from MFL's report checked against dated news. Use for \"who has X\", \"who owns X\", \"who's got X\", \"is X available\", \"is X a free agent\", \"how serious is X's injury\", \"is X hurt\", \"how long is X out\", \"injury update on X\", or \"what's the latest on X\". Finds the owner in one pass, never one franchise at a time, and never calls a player healthy because a report is silent. Not for what he is worth (league-player-values) or whether to start him (league-lineup)."
---

# League Player Status

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

Two questions an owner asks in one breath, mid-trade: who has him, and how bad
is it. Each has a short answer and one trap.

---

## Who has him — one pass, never twelve

| Step | Call |
|---|---|
| 1 | `get_rosters` with **no** `franchise_id` — every franchise in one payload |
| 2 | `get_players` with **every** rostered id from step 1, in one comma-separated list |
| 3 | Find his name, then `get_league` to turn that franchise into the owner's first name and team name |
| 4 | On no roster at all: `get_free_agents` for his position, the only authority on unowned players |

One `get_players` call covers the whole league: a 300-id list went through in a
single call, measured 11 Sep 2026 PT. Confirm the name you want is in the
response before saying he is on no roster; a lookup that came back short is not
an answer.

- **Never walk the league one franchise at a time.** On 11 Sep 2026 PT an answer
  to "who has Romeo Doubs?" called the tools once per team and wrote a line after
  each one — "No Doubs here (franchise 0004). Continuing." — nine of them before
  the answer. **Every line written between tool calls appears in the owner's
  chat**, so a progress line is part of the answer and carries the same rules:
  no ids, no narration. Make the calls, then write once.
- **MFL writes names "Last, First"**, with suffixes ("Walker III, Kenneth").
  Match on first and last name, ignoring punctuation and suffixes. If two players
  match, tell them apart by position and NFL team, and ask if that does not
  settle it.
- **Say where he sits**, from `status`: active roster, taxi squad, or IR. His
  salary and final contract year fit in one clause; what his contract options
  cost belongs to `league-contracts`.
- **Not on any roster and not in `get_free_agents` either** means the name did
  not match, not that he does not exist. Say which name you searched for.

## How bad is the injury — MFL is the slowest source

1. **`get_injuries`** — one call, league-wide. Find him by id. `status` is
   Questionable, Doubtful, Out, IR, IR-R (designated to return), IR-PUP, IR-NFI,
   Suspended, Holdout or RETIRED; `details` is the body part; `exp_return` is MFL's
   expected return date.
2. **Then search the news, every time**, for the newest dated reports on him.
   Put the injury and the current month and year in the query, not his name
   alone.
3. **Put the two together**: the injury, the expected time out, and the source
   and date of the newest report. Where MFL and the news disagree, the newer
   report leads and the disagreement is stated.

### Traps

- **MFL's injury report lags the news by days.** Measured 11 Sep 2026 PT: A.J.
  Brown's high-ankle sprain was reported on 9 Sep and confirmed by MRI, with at
  least four weeks out, by 11 Sep. MFL's injury report pulled at 07:01 PT on
  11 Sep had no entry for him at all. **No entry in MFL means MFL has not caught
  up, never that he is healthy.**
- **Never call a player healthy, or an injury minor, from silence or from an
  old article.** The same answer said Brown was "not currently injured" on the
  strength of an August thumb story. A report written before his last game
  cannot describe his state after it. If the newest report you can find predates
  his last game, say that and give its date.
- **Search for this week, not for the player.** A search on the name alone
  returns the most-linked story, which is rarely the newest. Put the month and
  year, or the week, in the query, and search again if every result predates
  his last game.
- **Some `exp_return` dates are leftovers.** A date already in the past is a
  stale entry the offseason left behind. A date after the season ends (the report
  uses 15 Feb) means no return date this season, not a date to plan around.
- **`INJURED_RESERVE` on a roster is a league roster slot, not a diagnosis**, and
  offseason IR flags carry over stale. Whether he is eligible for our IR slot is
  `league-rules`.
- **No web search this turn?** Then MFL's report is all there is. Say so, say it
  lags the news, and say no current news was checked. Do not fill the gap from
  memory.

---

## Answering

- **Lead with the answer, in the order asked.** Two questions in one message get
  two short answers, not one blended paragraph.
- **Who has him:** player (position, NFL team), owner's first name and team name,
  roster slot. One line.
- **The injury:** what it is, how long he is expected out, then the source and its
  date, in that order. One sentence of what it means here only when it changes a
  decision — a lineup (`league-lineup`) or an IR move (`league-rules`).
- **Name the source and date inline**, dates in Pacific. An undated injury claim
  cannot be checked against the next report.
- **Never print raw identifiers** — franchise ids, player ids — in the answer or
  in any line written between tool calls.

## Where this stops

| Question | Skill |
|---|---|
| What is he worth, is he a good asset | `league-player-values` |
| Should I start him this week | `league-lineup` |
| Can I put him on IR, what it costs | `league-rules` |
| His contract options and dead money | `league-contracts` |
| Is a trade for him fair | `league-trade-evaluator` |

> **Editing note — do not "correct" this.** Amounts below ten are written WITHOUT
> a dollar sign. A dollar sign immediately followed by one digit is silently
> replaced at invocation time by a word taken from the skill's arguments, which
> reads as ordinary prose and has rewritten whole price tables unnoticed. Two or
> more digits (`$16`, `$375`) are safe. All figures are US dollars.

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
