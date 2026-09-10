---
name: league-rules
description: "Invoke for any question about how the Dynasty of Whiners dynasty league (MyFantasyLeague 29557) works — salary cap, contracts, dead money, taxi and IR eligibility, trades, deadlines, penalties, playoffs and draft order. Use for \"can I do this\", \"what does that cost\", \"what does pick 1.05 pay\", \"rookie contract\", \"rookie salary\", \"contract prices\", \"is he IR eligible\", \"what's the deadline\", \"how much dead money\", \"what happens to our league if\", or \"under our league rules\" — any question about the rules. Answers come from the digest here, not from memory of other leagues."
---

# League Rules

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

A digest of Constitution 2.0 for the Dynasty of Whiners (MFL league `29557`).
**The Google Doc is the source of truth; this is a working reference.** If a
question turns on exact wording, say so and point at the constitution.

Format: **12 teams, dynasty, salary cap, superflex, half-PPR.** Don't explain the
format back to the reader — everyone here already knows it.

**Rules carry year tags**, e.g. `[2026]`, marking when they passed. Some have
future effective dates; check them before quoting a price for a later season.

**If you ever find a rule stated two different ways, say so rather than picking
one.** The scheduling tier rule was stated twice, differently, until 4 Sep 2026,
and the wrong version shipped an entire season's schedule before anyone noticed.

> **Editing note — do not "correct" this.** Amounts below ten are written WITHOUT
> a dollar sign, and money tables carry the unit in the column header. A dollar
> sign immediately followed by one digit is silently replaced, at invocation
> time, with a word taken from the arguments the skill was called with — the
> digit picks which word. It reads as ordinary prose, which is why it went
> unnoticed until 4 Sep 2026, by which point it had rewritten the rookie salary
> scale and the payout table into nonsense. Two or more digits (`$25`, `$375`)
> are safe and keep their sign. **All figures are US dollars.** This paragraph is for whoever edits this file, not an instruction for
> answering an owner; the source repository documents the behaviour.

---

## Salary cap

- **Cap $375** `[2025]`. History: $400 → $370 (2021 expansion) → $375.
- Counts: all active contracts, all taxi at **100%**, and **25%** of IR.
- Over the cap is allowed only until the Roster Submission Deadline. After that,
  at or under **at all times**.
- Minimum salary is **1**, so free cap space must always be ≥ open roster spots.
- **Cap floor $300** `[2026]`, after the FA draft, held until the first game.
  For the floor, **IR counts 100%** and dead money counts too. Missing it
  triggers tanking penalties.

**The IR asymmetry catches people:** 25% against the cap, 100% against the floor.
Cutting an IR player also costs 100% of the remaining contract, not 25% — the cap
relief does not follow him out the door.

Effective cap = $375 − salary adjustments (dead money). Never quote cap space
without checking `get_salary_adjustments`. `get_league`'s
`bbidAvailableBalance` already accounts for it.

**How dead money is actually recorded, which breaks naive reconciliation.** MFL
writes an automatic adjustment of **25%** of salary the moment a player is
dropped, and an LM adds the remaining **75%** by hand as a *second* row. The two
together make the 100% the constitution requires. So one cut appears as two
entries, and a cut the LM has not finished processing shows only a quarter of its
real charge. Sum every row for a franchise, and flag a lone 25% row as "LM entry
still outstanding" rather than quoting the smaller number as fact.

---

## Contracts

Every rostered player is on exactly one of these. Prices are dollars over the
player's previous salary.

| Type | Term | Price |
|---|---|---|
| **Short-term** | 1 year | +5 over previous salary |
| **Short-term extension** | 2 years | yr 1 +10 over previous, yr 2 +5 more |
| **Long-term** | 3 years | +10 over previous, **flat** all three years |
| **Rookie** | 2 years | by draft slot, see below |
| **Free Agent** | 1 year | auction/waiver price, expires end of season |
| **Franchise tag** | 1 year | see below |

`[2026, effective 2028]` A short-term extension signed 2028 or later has year 2
at **+10**, not +5 — so the first year anyone actually pays it is **2030**.

*Worked example:* drafted at 10 → short-term 15 → extension 25 then 30.
Would be 35 in year 4 if the short-term was signed 2028 or later.

After a short-term contract's first season the player must be released, tagged,
or given the two-year extension. After an extension completes, the normal options
resume.

**Back-tested and confirmed 4 Sep 2026.** Across the 2025→2026 offseason, all
twelve players re-signed by two franchises landed at exactly these prices —
short-terms at previous +5 for one year, long-terms at previous +10 expiring in
the third year. This arithmetic is verified against real signings, not assumed.

### Rookie contracts — 2 years, and they guarantee taxi eligibility

| Picks | Salary ($) |
|---|---|
| 1.01–1.03 | 12 |
| 1.04–1.09 | 10 |
| 1.10–1.12 | 8 |
| 2.01–2.03 | 6 |
| 2.04–2.09 | 5 |
| 2.10–2.12 | 4 |
| 3.01–3.06 | 3 |
| 3.07–3.12 | 2 |
| Round 4 | 1 |

`[2026, effective 2028]` Optional **one-year rookie extension** after a rookie
deal expires: 1st round +5, 2nd +4, 3rd +3, 4th +2. Available regardless of
NFL years or taxi eligibility, and it does not block a short-term the year after.

### Franchise tag

- **One per team per season.**
- Price: the **greater** of (5 over the average of the top 5 at that position
  last season, rounded up) or (5 over the player's previous salary).
- Only **after a contract has expired** — never mid-multi-year deal.
- Max **twice by the same owner**, and **never two years running**.
- Freezes contract progression: a player tagged after year 1 can later be signed
  short-term or long-term off the **pre-tag** salary.
- Convertible mid-year to a valid short-term, extension, or long-term,
  retroactive to the start of the year. A player who was on a short-term before
  the tag cannot get another short-term — only long-term or the extension.

---

## Cutting players and dead money

- Cutting a contracted player: **100% of the remaining contract** becomes dead
  money. **Exception: a player who formally retires carries none.**
- **Free Agent and Rookie contracts: 25%**, for the rest of that year only.
- **A rookie cut between years 1 and 2 of a rookie deal carries no penalty.**
- **An expired contract is not a cut.** Walking away from a player whose deal has
  ended costs nothing, so never quote a cut cost against a player whose decision
  is due this offseason — his choices are release at no charge, re-sign, or tag.
- **Dead money cannot be traded.** It stays with the original team even if that
  same team re-signs the player.
- `[2027]` The league year starts at the contract signing deadline.
- **Unreported** in-season cut of a non-rookie contracted player: 100% of salary
  for **one extra year** beyond the contract. "In-season" here means any moment
  after roster decisions are due, before the FA draft.
- Reporting window for cutting a non-rookie contracted player: **24 hours** `[2023]`.
- **The Balaji Rule™** `[2023]`: 5 minutes to report a transaction made in error.

---

## Taxi squad and IR

**Taxi — 6 spots** `[2025, was 5]`

- **Rookies and sophomores only** — first two NFL years. A 2026 draftee stays
  eligible through 2027.
- Taxi players **cannot start**; promote first, clearing a roster spot.
- After promotion, a player may return to taxi after **7 days**.
- **100% of salary counts against the cap.**

**IR — 4 spots.** Eligible: on real-life IR, or carrying **Out** or **Doubtful**.
Not eligible: suspended (unless also on real IR), and contract holdouts.

### Which NFL statuses actually qualify — check before pricing a stash

| Status | Eligible? | Note |
|---|---|---|
| Injured Reserve | **Yes** | including IR-with-return |
| Out / Doubtful | **Yes** | the weekly designation |
| Reserve/Left Squad | **No** | not an injury status at all |
| Commissioner's Exempt | **No** | conduct, not injury |
| Suspended | **No** | unless also on real IR |
| PUP / NFI | **Check** | only if it carries Out/Doubtful |

**Why this matters more than it looks.** A player who is unavailable but *not*
IR-eligible eats a **full active roster spot** for zero production, which inverts
the whole logic of a cheap stash. MFL enforces eligibility automatically, so the
failure mode isn't an illegal roster — it's discovering he can't be IR'd *after*
you've bought him and used the spot.

**Roster minimums** `[2026]`, after the FA draft: **2 QB, 3 RB, 4 WR, 2 TE**.
Taxi and IR count toward them.

Roster structure: 10 starters, 8 bench, 6 taxi, 4 IR. Starters resolve to
1 QB, 2 RB, 3 WR, 1 TE, 2 FLEX, 1 SUPERFLEX.

---

## Trades

- Contracts and salaries transfer **as-is**.
- **Both teams must be under the cap after the trade.** Players may be dropped as
  part of a trade to make room.
- **One active franchise tag per team** — a trade giving you two forces a
  conversion.
- **Dead money cannot be traded.**
- **Picks for the upcoming three seasons only** `[2022]`. In the 2026 offseason
  that means 2027, 2028 and 2029.
- LM-reviewable and vetoable — reserved for collusion or clearly abnormal
  behaviour such as giving assets away for nothing, **not** for a subjectively
  lopsided deal. A vetoing LM may transfer a 4th-round pick as compensation.

**The thing owners underweight:** an incoming above-market contract is a
liability regardless of the player's external trade value, because salary
transfers as-is and cutting costs 100% of the remainder. Always recompute both
sides' cap space and open roster spots before judging an offer.

**Conditional legs are invisible to MFL** — if terms include a pick identified
later, nothing in the system records it; see `league-draft-picks`. And the
gSheet's Trade History has at least one row with its two sides reversed, so never
read who owes whom off the sheet alone.

---

## Deadlines and penalties

Annual order: rule votes → **rookie draft** (after the NFL draft, ideally
July/August) → **roster submission deadline** → **owner-executed cuts** →
**FA auction** (mid-to-late August).

- **Roster submission:** usually midnight PT the Saturday before the FA draft.
  `[2025]` **$25/day** late fee.
- **Cuts:** by midnight the following day. **Do not cut early** — it influences
  other owners' contract decisions. `[2025]` **$25/day, stacking** with the above.
- Dues unpaid by kickoff of game 1: **$25/week** to a discretionary league fund.

**Rookie draft** `[2026]`: 4 rounds, reverse order of previous standings, async,
**24-hour pick clock**. Miss it and your pick auto-trades one-for-one with the
next pick (2.01 becomes 2.02). It can cascade. Flag extenuating circumstances in
advance.

**FA auction:** capital = cap space remaining after all contracts, rookie deals
and dead money. By the end, every team must be **at or under the cap**, meet the
**roster minimums** `[2026]`, and clear the **$300 floor** `[2026]`. `[2025]` **No
taxi or IR changes during the draft** — it corrupts MFL's projections, and LMs
audit before and after.

**Mid-season:** all free agents lock **1PM ET Sunday**; blind bids process
Wednesday afternoon; then continuous FCFS. Dropped players go to **waivers**, not
FCFS, minimum 24h. Waivers process Wednesday evening, Saturday morning, and
Sunday around noon ET. No spending limit beyond staying under the cap after each
signing — and you may **not** bid above your cap space intending to drop
afterwards; drops must come first.

**Consequence worth stating:** unspent auction capital is in-season buying power.
Leaving the auction with money is a position, not a failure.

---

## Standings, playoffs, draft order

- 14-week regular season, **top 6** make the playoffs, no divisions.
- Tiebreaker throughout: **total points for**.
- Week 15: seeds 1–2 bye, 3v6, 4v5. Week 16: no reseeding (MFL limitation) —
  seed 1 vs winner of 4/5, seed 2 vs winner of 3/6. Week 17: championship and a
  3rd place game, which pays.

**Scheduling tiers** — which four teams are Tier 1 and how Tiers 2 and 3 split —
are not restated here. For "how are the tiers decided" or a team's tier, invoke
`league-matchups`; to build a season, `league-schedule`. Never answer the tier
rule from memory: the wrong version once shipped a whole season.

**Next year's rookie draft order:** non-playoff teams in reverse regular-season
standings (H2H record, then points for — lowest points picks first among equal
records); playoff teams by finish. **Exception:** first-round playoff losers take
**#7** (lower seed) and **#8** (higher seed).

**Scoring:** passing TD 4, 25 yds 1, INT −1; rushing TD 6, 10 yds 1; receiving
TD 6, 10 yds 1, **reception 0.5**; 40+ yard TD bonus 1; fumble −1 and fumble lost
−1; 2PC 2; `[2026]` all other TDs 6.

**Tanking** — triggered by fielding an incomplete roster, starting inactive
players, or `[2026]` missing the cap floor. Penalties: docked draft
compensation (moved last in a round, or losing your latest pick; floor
violations can apply across several rounds), applied only to a team's **own**
picks. Match outcomes can be reversed where a winning lineup was available, with
2+ LMs agreeing. `[2025]` Precedent for not setting a roster: lose your latest
pick next year, stacking, at most one warning per owner per year — and LMs
retroactively correct the lineup so points-for stays accurate, which can flip a
game.

---

## Dues and payouts

`[2025]` **$200/season escalating $50/year**, so 2026 is **$250**.
`[2026]` At 12 teams that is **3,000 dollars**:

| Line | Amount ($) |
|---|---|
| MFL platform | −70 with the early-bird discount, −90 without |
| Most points | 250 |
| Rolling repeat-winner pot | 250 |
| 3rd place | 500 |
| 2nd place | 750 |
| **1st place** | **1,180** (1,160 without the discount) |

The rolling pot held **$925** entering 2026. Pat is treasurer.

---

## Rule changes

Explicitly **not a democracy** — a coregency of three equal LMs (Straker, Mike,
Pat). `[2025]` Every proposal gets a **minimum 14-day** public comment and vote in
Discord. A majority of players (**≥7**) settles it; absent a majority the LMs
vote. One active vote at a time is recommended. Passed changes go into the
constitution with a `[YEAR]` tag.

---

## Known open item

**Shortened season, 1–5 games played: the constitution says `<rules TBD>`.**
0 games = dues refunded and all contracts freeze. 6+ but short of a full season =
that year only, winners and draft order from a stack rank by total points for.
The 1–5 band is genuinely undefined — say so rather than reasoning by analogy.

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
