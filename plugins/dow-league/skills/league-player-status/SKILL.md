---
name: league-player-status
description: "Invoke before any league tool call when an owner asks who has a player, whether he is available, how bad his injury is, or which teammates to go after now that he is hurt, in the Dynasty of Whiners league (MFL 29557) — the owner and roster slot, the injury from MFL's report checked against dated news, and for an injury's fallout his teammates at that position with their points here and who owns each. Use for \"who has X\", \"who owns X\", \"is X available\", \"is X a free agent\", \"how serious is X's injury\", \"is X hurt\", \"how long is X out\", \"what's the latest on X\", \"with X on IR, who should I target\", \"who replaces X\", or \"who steps up with X out\". Finds the owner in one pass, never one franchise at a time, and never calls a player healthy because a report is silent. Not for what he is worth (league-player-values) or whether to start him (league-lineup)."
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
is it. Each has a short answer and one trap. The third follows from the second:
with him out, which teammate steps in, and can I get him.

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

- **Write nothing until you have the answer.** Make the calls, then write once.
  No "found him", no "checking the next team", no line naming the record you
  matched. **Every line written between tool calls appears in the owner's chat**,
  so those lines are part of the answer and carry every rule the answer carries.
  Two measured leaks, both 11 Sep 2026 PT: a "not on this team, continuing"
  line nine times over, each naming the franchise by its id, from an answer
  that went on to name the id in its final text as well; and a "found him"
  line giving his player id and his franchise's id, from a run whose final
  answer was clean, so the whole leak was in the line nobody counts as the
  answer. The second came back later the same day nearly word for word, when
  this file still quoted it with the ids in: a quoted leak is a template.
- **Never walk the league one franchise at a time.** The first of those leaks was
  an answer that called the tools once per team, which is where its nine progress
  lines came from. One pass has nothing to narrate.
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
   **The report is league-wide and carries ids, not names.** Resolve the one
   player asked about and say nothing about the rest: never list, count or quote
   the other entries. An answer that said "the report only lists" and then three
   raw ids leaked all three and answered a question nobody asked (measured
   11 Sep 2026 PT).
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
- **His points say whether he played.** Pull `get_player_scores` for the latest
  week with games in it. A score for him means he was on the field that week, so
  a report dated before that game cannot describe him now, however recent it
  looks. Measured 11 Sep 2026 PT: an answer doubted an owner's "he's on IR"
  because everything it found was dated the day of the game, written before
  kickoff; MFL already had his week-1 score. **A blank score is not a zero**:
  the same day, a receiver inactive for his team's game came back with an empty
  score, and one who played and caught nothing came back 0.00.
- **The owner's word is a report too.** When the owner says he is hurt and the
  news you find is older than his last game, the owner is the newer source.
  Say what you could and could not confirm, with dates, and answer the question
  asked. Do not open by disputing the premise with a story written before the
  game.

---

## Who steps in — his teammates, and whether you can get them

"With X on IR, who should I target", "who replaces him", "which of his team's
receivers are worth a look" — the injury, the depth chart, and the ownership
of every name, all in one answer.

| Step | Call |
|---|---|
| 1 | The injury, exactly as in the section above: `get_injuries`, `get_player_scores`, dated news |
| 2 | `get_player_scores` with his `position` for the latest week with games in it, then `get_players` on every id returned; keep the rows on his NFL team. From week 3 on, add `week=AVG` |
| 3 | `get_rosters` with no `franchise_id`, `get_free_agents` for the position, and `get_league` for the owners — the one pass from "Who has him", covering every teammate you will name |
| 4 | The news, for the depth chart: who takes his snaps, and who the team signed or promoted. Put the month and year in the query |

`get_player_scores` names other skills in its tool description. That line is
about routing a first call; here, call it directly.

- **Availability goes in this answer, never offered as a follow-up.** Every
  teammate named carries his owner's first name and team name, or "free agent".
  Measured 11 Sep 2026 PT: an answer led with a receiver who was already on
  another owner's roster, listed a free agent third without saying he was
  available, and closed by offering to check who owned them. The owner had
  asked who to consider; which of them he can have was the answer.
- **Scores come from this league, not from memory of last season.** Write each
  teammate's points from step 2 next to his name. The same answer ranked the room
  on last season's target counts while MFL already held this season's first
  game, in which that free agent had outscored every teammate.
- **Early in a week, only some teams have played.** At 11 Sep 2026 PT, week 1 had
  scores for four NFL teams only. A teammate with no row may not have played
  yet; say so, or step back a week once one exists. An empty row is not a zero.
- **A teammate on a taxi squad or IR slot is still owned.** Say where he sits.

---

## Answering

- **Lead with the answer, in the order asked.** Two questions in one message get
  two short answers, not one blended paragraph.
- **Who has him:** player (position, NFL team), owner's first name and team name,
  roster slot. One line.
- **The injury:** what it is, how long he is expected out, then the source and its
  date, in that order. One sentence of what it means here only when it changes a
  decision — a lineup (`league-lineup`) or an IR move (`league-rules`).
- **Who steps in:** the injury in one line with its source and date, then one row
  per teammate — his points in the latest week, his owner's first name and team
  name or "free agent", and his role now from the depth-chart news. End by
  naming which of them can be claimed today.
- **Name the source and date inline**, dates in Pacific. An undated injury claim
  cannot be checked against the next report.
- **Never print raw identifiers** — franchise ids, player ids — in the answer or
  in any line written between tool calls.
- **Never describe a franchise you have not named.** Mentioning whose roster he
  is on means `get_league` was called and the owner is named. A label wrapped
  round the id is still the id: "owned by the franchise at team roster slot",
  followed by the id, was a measured leak on an injury question (11 Sep 2026
  PT), where the ownership line was volunteered and the lookup skipped. If the owner was not
  resolved, leave ownership out of the answer.

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
