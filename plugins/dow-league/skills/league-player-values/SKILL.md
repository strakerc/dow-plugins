---
name: league-player-values
description: "What a player is worth in the Dynasty of Whiners league (MFL 29557) — market value, what his contract costs against it, and whether that makes him an asset or a liability here. Use for \"what's X worth\", \"is he overpaid\", \"should I keep him at that price\", \"who's the better asset\", or sizing up someone else's roster."
---

# League Player Values

**A player's price is public. What he is worth *here* is not.** Every external
site prices the player; none of them knows he is signed through 2028 at $16, or
that his owner is $14 over the cap and has to move someone.

That gap is this skill. Market value sets the price; the league data decides
whether that price is a bargain or a problem.

---

## The recipe

| Need | Call |
|---|---|
| Market value, by name | `get_player_values` — semicolon-separated, "First Last" or "Last, First" |
| Can't find a name, or want picks | `list_values` — substring search; picks sit under position `PICK` |
| Consensus rank cross-check | `get_dynasty_rankings` — superflex board, pinned server-side |
| Rookies | `get_rookie_rankings` |
| Salary, contract type, contract end year, IR/taxi | `get_rosters` (add `franchise_id` for one team) |
| Whose cap is under pressure | `get_league` → `bbidAvailableBalance`, then `get_salary_adjustments` |
| Actual production under our scoring | `get_player_scores` — **pull `week=AVG` as well as `YTD`** |
| Is he even owned | `get_free_agents` — the only authority on this |

**Report one market figure, not two.** `get_player_values` returns a real value
number; `get_dynasty_rankings` returns a *rank*, which is a different unit and
cannot be averaged into it. Lead with the value. Use the rank as a **cross-check**
— and when the two disagree sharply, say so as a finding rather than splitting
the difference. The properly weighted blend of the two only exists inside
`evaluate_trade`, and only for assets in a specific trade.

## The part no external source has

Once you have the value, the league data is what makes it mean something:

- **What he costs, and for how long.** `contractStatus` is the FINAL year of the
  deal, so years remaining = `contractStatus` − season + 1.
- **Whether the contract can be escaped.** Cutting a non-rookie deal costs 100%
  of the remainder. A rookie deal can be cut between years 1 and 2 for nothing.
  **A cheap long deal and an expensive long deal are opposite things**, and the
  length is what makes each of them so.
- **What his owner can actually do.** Someone against the cap has different
  options than someone with room, and that changes what he can be had for.

**The contract is the asset.** An above-market contract is a liability no matter
how good the player is, and a below-market one is worth more than the name.

---

## Traps, all of which have cost something here

- **Superflex, always.** The gateway pins `get_dynasty_rankings` to the
  superflex board server-side, so the trap cannot be hit through it — but know
  why it exists. Josh Allen is #1 on that board and #21 on the 1QB one. If a rank
  ever looks absurd for a quarterback, that is the tell.
- **FantasyPros dynasty ranks are PPR. This league is half-PPR.** No half-PPR
  dynasty board exists. It slightly overstates high-volume, short-target
  receivers relative to our scoring. Adjust in words, not by inventing a number.
- **A player absent from a source is unpriced, not worthless.** Report him
  separately and say the board could not price him. Chris Brazzell II and Mike
  Washington Jr. are both rostered and both missing from FantasyCalc. **Never let
  a missing price read as a low one.**
- **Confirm both sides can be named before comparing two players.** Truncation
  and tier caps fail silently, so a comparison can quietly become a comparison
  with nothing.
- **`YTD` alone ranks players wrong.** Season totals conflate rate with
  availability. One receiver's 66.5 points was nine games at 7.4; another's 115.1
  was eighteen games at 6.4 — a usage problem with a fix versus a health problem
  without one. **Always pull `AVG` too.**
- **Diagnose *why* a player is cheap before calling him a bargain.** An injury
  has a rehab timeline you can underwrite. A contractual standoff has no timeline
  at all, only a decision that is not yours. Ask what specific event ends the
  unavailability and who controls it — if the answer is "his own choice, which he
  has declined", the low price is not an inefficiency.
- **IR flags carry over between seasons and go stale.** Verify against news
  before treating one as current.
- **Role and depth-chart claims rot faster than any API field.** Nothing in MFL
  knows a player's NFL role. Search news whenever a specific player is named, and
  date-stamp the claim.
- **Contract fields blank out the moment a player is dropped.** For anything
  historical, call `get_rosters` with an explicit `season` — the week-22 snapshot
  keeps salary and contract intact.

---

## Answering well

- **Give the objective answer and your recommendation as two separate things.**
  What the board says, then what you think, each labelled. Do not quietly filter
  a name out of a list because you disagree with its rank — say the rank and then
  say why you would go elsewhere.
- **Wide expert disagreement means "look into this", never "avoid this".**
  A high spread is a signal that consensus is thin, which is where value hides.
  Treating variance as a reason to discount is how a good pick gets talked out of.
- **When someone names a player they already like, that is evidence, not a
  guess.** Give the number and any real concern, then let them decide. Do not
  argue anyone off a named target on a ranking alone.
- **Lead with the answer under time pressure.** A name and a number first,
  reasoning after. Availability or injury risk belongs in one clause beside the
  name, never a paragraph, and only when it could change the decision.
- **State the source and its age inline.** An unattributed number cannot be
  argued with later.
- **Never print raw identifiers** — franchise ids, pick notation, player ids.
  Say "Zef's 2027 4th", never the code.

## Where this stops

| Question | Skill |
|---|---|
| What are my options on his expiring deal, and what does each cost | `league-contracts` |
| What would it cost to tag him | `league-franchise-tags` |
| Is this specific trade fair | `league-trade-evaluator` |
| Who holds which future pick | `league-draft-picks` |

**Do not compute a surplus score here.** `evaluate_trade` produces one, and its
*size* is known to be overstated — it returned "clear win" on every trade in
validation, including deals the league manager called even. Direction is usable,
the magnitude is not, and a single-player version of it would be worse. Describe
the tension in words: what he is worth, what he costs, how long, and whether that
is a problem for his owner.

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
