---
name: league-trade-evaluator
description: "Invoke before any league tool call to score a proposed trade in the Dynasty of Whiners league (MFL 29557) — market value against league-adjusted value once salary, contract term, cap space and roster legality are priced in. Use for \"is this trade fair\", \"who wins this trade\", \"should I do this deal\", or checking an offer before accepting it. A trade that has already gone through is league-trade-history."
---

# League Trade Evaluator

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

Prices a **proposed** trade. One tool call does the work: `evaluate_trade`
returns two verdicts that are deliberately never merged, and the gap between
them is the whole point.

| | What it is | How much to trust it |
|---|---|---|
| `market` | What a public calculator would say — FantasyCalc blended with FantasyPros superflex ECR | **Direction and size both.** Validated 7 Sep 2026 against a human answer key; it agreed wherever the human had an opinion |
| `leagueAdjusted` | The same trade once salary, contract term, cap space and roster legality are priced in | **Direction only.** The size is systematically overstated — see below |

**Read `divergence` first.** When the two disagree, that sentence is the answer,
and it is the part no external site can compute. It was correct in every case it
fired during validation.

---

## The one rule that matters: never quote the league-adjusted percentage

`leagueAdjusted.edgeVsValueMovedPct` is **not a measurement.** In validation it
returned "clear win" on every single trade tested, at 40–62%, including two the
league manager called dead even. It has never once returned "slight edge".

The cause is structural, not a bug. The price curve is rank-based: a player is
measured against whoever sits at his *salary* rank. Baker Mayfield is around the
4th-highest salary in the league at $61, so he is measured against the
4th-most-valuable player — an expectation of 8,665 against his actual market
value of 3,379, for a surplus of −5,286. Value is steeply convex at the top and
salary is not, so **every expensive contract reads as a landslide.**

So:

- **Say "the contracts favour Pat here."** That is supported.
- **Never say "Pat wins by 61%."** It will be quoted in an argument and it is
  wrong.
- **Show the receipt instead.** "Mayfield is the 4th-priciest contract in the
  league and roughly the 64th most valuable player" is more useful, more
  defensible, and is the actual finding.

The market percentage is fine to quote.

---

## It cannot score a trade that already happened

Every asset is checked against **current** ownership. On an executed trade the
giving side no longer holds what it gave, so all of it fails:

```
"Troy Franklin" is on Gabe's roster, not Straker's.
```

This is correct — the tool prices offers, not history. When someone asks whether
a past trade was good:

1. Say plainly that the evaluator prices proposals, not completed deals.
2. Offer to run it **reversed** — the current holders as the givers — which is
   the same asset comparison with the sign flipped. **Say that you did this**,
   and invert the verdict when reporting.
3. Flag that the league-adjusted half will not invert exactly, because it prices
   contracts against each team's cap position *today*, which is post-trade.

**`league-trade-history` is the skill for this.** It judges completed trades on
what the assets actually did — real points, the player a pick became, dead money
on a cut — rather than re-pricing them against today's board.

## A refusal is the tool working

`ok: false` means it declined to guess, which is the behaviour that makes it
worth trusting. Report the reason plainly; do not retry with the asset dropped.

| Refusal | What it means |
|---|---|
| "is on X's roster, not Y's" | The trade is backwards, or already executed |
| "picks are not tradeable — only …" | Only the upcoming three seasons can be traded |
| "resolves to … currently held by X" | The named owner does not hold that pick |
| "not on X's roster (and may not be the exact MFL spelling)" | **See below** |

**That last message is misleading.** It fires for a cut player exactly as it does
for a typo. Before telling anyone to check their spelling, call
`get_free_agents` — if the player is there, he was released and the trade cannot
be scored at all. Say that instead.

---

## Asking it properly

- **Owners go by first name.** "Straker", "Pat", "Zef".
- **Picks in plain words:** "2027 2nd", or "Mike's 2027 2nd" when the pick did
  not originate with the person trading it. A pick's value follows the *origin*
  team's finish, so naming the origin matters.
- **`teamA` defaults to the caller's own team**, so "what if I send Pearsall for
  Franklin" works without naming yourself.
- Multi-asset sides are fine; give each asset as its own entry.

## Reading the output back to an owner

- **Lead with the answer**, then the reasoning.
- **Never print raw identifiers.** Franchise ids, pick notation and player ids
  are internal plumbing. Say "Zef's 2027 4th", never the code.
- **Always surface `legality`.** A trade that puts someone over the cap or past
  the 18-man active limit cannot be executed, however good it looks. `blocked`
  is not advisory.
- **Report `priceCurve.sampleSize`** if it is far below the league's roster
  count, and treat the verdict as thin if so. A `notes` entry saying the curve
  was built from the two involved rosters means the valuation moved with the
  counterparty rather than measuring the asset — that was a real defect, fixed in
  `tradeval` 0.2.2, and its return would mean the value sources are short.

## What it cannot know, and should say rather than hide

- **Team intent.** A deal can be right for a rebuilder and look bad on raw
  surplus. The tool sees assets, not plans.
- **Why the trade is being offered** — a roster crunch, a bye week, a favour.
- **Conditional picks.** No MFL call represents them; see `league-draft-picks`.
- **News since the values were pulled.** Search when a specific player is named.

When the tool and a person disagree and the reason is one of these, that is worth
saying out loud. It is not the engine being wrong.

> **Editing note — do not "correct" this.** Amounts below ten are written WITHOUT
> a dollar sign. A dollar sign immediately followed by one digit is silently
> replaced at invocation time by a word taken from the skill's arguments, which
> reads as ordinary prose and has rewritten whole price tables unnoticed. Two or
> more digits (`$61`, `$375`) are safe. All figures are US dollars.

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
