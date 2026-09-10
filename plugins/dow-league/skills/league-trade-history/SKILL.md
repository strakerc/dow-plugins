---
name: league-trade-history
description: "Invoke before any league tool call for questions about completed trades in the Dynasty of Whiners league (MFL 29557) — what trades an owner has made, what moved, what those assets actually did afterwards, and who is ahead now. Use for \"what trades has X made\", \"what trades has X made this season\", \"how did that trade turn out\", \"who won the Worthy trade\", \"has that deal aged well\", or \"was my trade of X for Y a good deal\". The raw transactions payload is ids, pick codes and epoch timestamps; this skill resolves all three."
---

# League Trade History

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

Judges trades that **already happened**, on what the assets actually did.

**This is not the trade evaluator.** `league-trade-evaluator` prices a *proposal*
against a market board, which is why it checks current ownership and refuses on
any completed deal. This skill goes the other way: the trade is done, ownership
has already moved, and the league's own record is better evidence than any
valuation model. Real points under our scoring, the player a pick actually
became, the dead money a cut actually cost.

**It cannot tell you whether a trade was good *at the time*.** Neither value
source retro-prices — FantasyCalc and FantasyPros serve current numbers only, and
KTC scraping is barred by their terms. Anyone who claims a trade-time valuation
here is quoting today's board in a costume. Say so plainly and answer the
question that can be answered.

---

## The two questions, and never merge them

**1. Who is ahead now.** A fact. Points scored, picks used, players cut, dead
money carried, contracts still running.

**2. Whether the decision was defensible.** An argument, and a different one.

**A trade can be correct and still lose.** A back tearing an ACL does not
retroactively make the manager who acquired him wrong; it makes him unlucky.
Grading on outcome alone builds a machine for blaming people for variance, and in
a twelve-person league that people stay in for years, that is a bad thing to
build. Report the first, then argue the second, and label which is which.

State what was knowable at the time when you argue the second one — an injury
that had already happened is evidence against the decision; one that happened
afterwards is not.

---

## The recipe

| Step | Call |
|---|---|
| Find the trades | `get_transactions` with `transaction_type="TRADE"` and a `season` |
| Name the players | `get_players` with the full id list — never skip an id |
| What a pick became | `get_draft_results` with the draft's season — **LM-only, see below** |
| What each player has done since | `get_player_scores` — pull `week=YTD` **and** `week=AVG` |
| Who was cut, and what it cost | `get_salary_adjustments` with the season |
| Is he even still owned | `get_free_agents`, plus current `get_rosters` |
| The contract each side chose afterwards | `get_rosters` with an explicit `season` |

### Reading a trade record

Each row carries `franchise` and `franchise2` with a `..._gave_up` list for each
side. Assets are player ids, or pick codes in **two different notations that do
not read the same way**:

- **`FP_{origin}_{year}_{round}`** — a future pick. The id is the pick's
  **origin**, not its holder. `FP_0002_2027_2` is Pat's 2027 2nd wherever it sits.
  Round numbers here are real round numbers.
- **`DP_{round}_{pick}`** — a pick in that year's own rookie draft, and **both
  numbers start at zero.** Add one to each before naming a slot:
  `DP_0_0` = 1.01, `DP_1_3` = 2.04, `DP_3_11` = 4.12. `DP_1_3` is **not** 1.03, and its year
  is the season the transaction sits in: a `DP_` pick in a 2026 trade is a 2026
  pick, never 2027 -- only `FP_` codes name a later year. Confirm every
  `DP_` against `get_draft_results` before naming a slot out loud: an off-by-one
  produces a completely plausible wrong pick with no error anywhere. This has
  already happened once, on 7 Sep 2026.

### Timestamps

`timestamp` is Unix epoch. **Convert to Pacific and print the zone**, with UTC in
parentheses: `29 Aug 2026, 07:37 PT (14:37 UTC)`. Late-evening trades fall on the
previous day in Pacific, and four of seven in one sample did exactly that — a
date quoted from the UTC conversion will disagree with what the owners remember.

---

## `get_draft_results` is LM-only

It is the cleanest way to say what a pick became, and **members do not have it.**
A tool a key cannot reach reports as `Unknown tool`, not as a permission error, so
this looks like a broken skill when it is a role boundary.

**The fallback, which members do have:** `get_rosters` with the draft's `season`
carries a `drafted` field per player — `1.05 (2025)` for a rookie-draft slot. Scan
the snapshot for the slot you want. It finds anyone still rostered at season's
end and misses anyone cut before it, so say the pick's outcome is best-effort
rather than presenting a gap as "nobody was taken."

---

## Traps

- **A side that gave up nothing is almost always a conditional settling.**
  An empty `franchise1_gave_up` or `franchise2_gave_up` is the only
  machine-readable signal that a conditional exists — one settled 82 days after
  it was agreed, recorded as a separate one-sided trade with nothing linking the
  two. Check `conditional-picks.md` and say the record is incomplete.
- **Conditional legs are invisible.** MFL records only the identified assets, so
  a trade with a conditional attached cannot be judged from the API alone. Flag
  it; do not quietly score the visible half.
- **Contract fields blank the moment a player is dropped.** The live feed empties
  `salary`, `contractInfo` and `contractStatus` on a cut. Anything historical
  needs `get_rosters` with an explicit `season` — the week-22 snapshot keeps them
  intact.
- **`YTD` alone conflates rate with availability.** Nine games at 7.4 and
  eighteen at 6.4 rank backwards on totals. Pull `AVG` too, and say which you are
  quoting.
- **A few weeks is noise.** Say so rather than declaring a winner off four games.
  A dynasty trade is usually not settled inside a season.
- **A future pick that has not been used yet has no outcome.** Its value still
  depends on how the *origin* team finishes. Give a tier and its basis, not a
  verdict.
- **The league gSheet's Trade History is hand-typed and has had a row reversed.**
  It is not evidence. Reconcile any row against `get_transactions` before
  recording who gave what — a team can never give up a pick that is not on its own
  side, so a pick with origin X appearing in the record means X's column is the
  one that gave it.

---

## Answering well

- **Lead with where it stands**, then the argument about the decision.
- **Name what each asset became**, not what it was labelled. "Paul's 2026 2nd"
  means little; "the pick that became Chris Bell" means everything.
- **Never print raw identifiers** — franchise ids, pick codes, player ids. Say
  "Zef's 2027 4th".
- **Quote real production, not estimates**, and say which season and which split.
- **Say when the record is incomplete** rather than scoring around the gap. That
  is the whole difference between this and a guess.
- **Be careful whose trade you are grading.** These are eleven people who read
  each other's writeups. Report the facts flatly; save the sharper edges for
  where the evidence is genuinely one-sided.

## Where this stops

| Question | Skill |
|---|---|
| Is this proposed trade fair | `league-trade-evaluator` |
| What is this player worth now | `league-player-values` |
| Who holds which future pick, and what is owed | `league-draft-picks` |
| What are my options on his contract | `league-contracts` |

> **Editing note — do not "correct" this.** Amounts below ten are written WITHOUT
> a dollar sign. A dollar sign immediately followed by one digit is silently
> replaced at invocation time by a word taken from the skill's arguments, which
> reads as ordinary prose and has rewritten whole price tables unnoticed. Two or
> more digits (`$19`, `$375`) are safe. All figures are US dollars.

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
