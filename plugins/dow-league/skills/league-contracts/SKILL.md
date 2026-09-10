---
name: league-contracts
description: "Invoke before any league tool call for contract questions in the Dynasty of Whiners league (MFL 29557) — which players have a decision due, which contracts expire, what each option (short-term, long-term, extension, tag) costs, dead money on a cut, and whether a roster is cap- and roster-legal. Use for \"which of my contracts expire\", \"what are my options on X\", \"what does it cost to keep him\", \"my contract decisions\", \"what's my roster and which contracts are up\", or \"how much dead money if I cut\". The raw roster payload is ids, codes and unpriced options; this skill resolves the names and prices every option."
---

# League Contracts

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

The costs side of contract decisions: what is legal, what it costs, and what the
roster looks like afterwards. **Deterministic** — it reads the constitution's
price tables and the roster, never a valuation.

**Whether a player is *worth* the price is a different question.** That is player
valuation; say so and hand off rather than guessing. This skill answers "what are
my options and what do they cost", which is most of what an owner actually needs
at the deadline.

**Franchise tag pricing lives in `league-franchise-tags`.** This skill reports the
personal floor (previous salary plus 5) and flags that the real price is the
*greater* of that and the positional floor, which needs last season's top-5
salaries by position. Don't compute the positional floor here.

> **Editing note — do not "correct" this.** Amounts below ten are written WITHOUT
> a dollar sign. A dollar sign immediately followed by one digit is silently
> replaced, at invocation time, with a word taken from the arguments the skill
> was called with — the digit picks which word. It reads as ordinary prose, which
> is why it went unnoticed until 4 Sep 2026, by which point it had rewritten this
> file's entire price ladder into nonsense. Two or more digits (`$25`, `$375`)
> are safe and keep their sign. **All figures are US dollars.** This paragraph is for whoever edits this file, not an instruction for
> answering an owner; the source repository documents the behaviour.

---

## The field that misleads everyone

`get_rosters` returns, per player:

| Field | Meaning |
|---|---|
| `salary` | current annual salary |
| `contractInfo` | `Rookie` · `Short-Term` · `Short-Term (Extension)` · `Long-Term` · `Free Agent` · `Franchise` / `Franchise Tag` |
| `contractYear` | which year **of** the deal he is in |
| `contractStatus` | **the FINAL YEAR of the deal — not its length** |
| `status` | `ROSTER` · `TAXI_SQUAD` · `INJURED_RESERVE` |

**`years remaining = contractStatus − season + 1`.** Reading `contractStatus` as a
duration is the single most likely mistake here. **A contract expires after season S
exactly when `contractStatus` equals S.** Nothing else marks expiry — not
`contractYear`, not the contract type, not the salary.

MFL is inconsistent about `Franchise` vs `Franchise Tag`, and about
`Short-Term (Extension)` vs `Short-Term Ext.` — match on a prefix or substring,
never an exact string. Both extension spellings mean the same contract. Test for
`Ext`: testing for `Extension` misses the abbreviated one and reads an *expiring*
extension as a plain short-term, offering a second extension and withholding the
long-term. The script did exactly that until 9 Sep 2026 PT. A player still
inside his extension gets no options either way — only his cut cost.

**`contractYear` does not reliably increment by one.** A short-term extension was
observed going from year 1 to year 3 across a single offseason. Do arithmetic
from `contractStatus` and `salary`; treat `contractYear` as a label.

**Contract data vanishes on a drop.** The live feed blanks `contractInfo`,
`contractYear`, `contractStatus` and `salary` the moment a player is cut. For any
historical question use `get_rosters` with `season=YYYY`, which returns the
week-22 snapshot with everything intact.

---

## Options, once a contract completes

| Current contract | Legal next steps |
|---|---|
| **Rookie**, **Long-Term**, **Short-Term (Extension)**, **Free Agent** | Release · Short-term (+5) · Long-term (+10, flat 3 yrs) · Franchise tag |
| **Short-Term**, after its first season | Release · **two-year extension** (+10, then +5 more: a short-term at 22 extends at 32, then 37) · Franchise tag. **A second short-term is not legal.** |
| **Franchise Tag** | Release · Long-term · Extension. Short-term only if he was *not* on a short-term before the tag. **Never tagged two years running.** |

**The extension's first year is previous + 10, never + 5.** A short-term at 22
extends at 32, then 37; writing 27 is the plain short-term price, which is the one
option a short-term cannot take again.

`[2026, effective 2028]` A short-term extension signed 2028+ has year 2 at +10
rather than +5 — first actually paid in **2030**.

`[2026, effective 2028]` **Rookie extension:** after a rookie deal expires, an
optional one year at 1st round +5, 2nd +4, 3rd +3, 4th +2. Available
regardless of NFL years or taxi eligibility, and it does not block a short-term
the following year. Not available before 2028.

**Back-tested and confirmed 4 Sep 2026.** Across the 2025→2026 offseason, all
twelve players re-signed by two franchises landed at exactly these prices, with
the right terms — short-terms one year at previous +5, long-terms three years at
previous +10, expiring in the third. Every player who actually faced a decision
was flagged as facing one. The pricing model is verified against real signings.

## Dead money on a cut

| Contract | Dead money |
|---|---|
| Non-rookie under contract | **100% of the remaining years.** Cannot be traded |
| Free Agent, or Rookie in year 2 | 25%, for the rest of the current year only |
| **Rookie between years 1 and 2** | **Nothing** |
| Player who formally retires | Nothing |

**An expired contract is not a cut, and costs nothing to walk away from.** Never
quote a cut cost against a player whose decision is due — his options are release
at no charge, re-sign, or tag. Cut cost applies only to players still under
contract for a future year.

Dead money stays with the original team **even if that team re-signs the player**.
`[2025]` An unreported in-season cut of a non-rookie contracted player costs 100%
of salary for one **extra** year beyond the contract. Reporting window is 24
hours.

**How it is recorded, which breaks naive reconciliation.** MFL writes an
automatic adjustment of **25%** of salary the instant a player is dropped; an LM
adds the remaining **75%** by hand as a *second* row. Both together make the
100%. So one cut appears as two entries, and a cut the LM has not finished
processing shows a quarter of its real charge. Sum all rows per franchise, and
flag a lone 25% row as "LM entry still outstanding" rather than quoting it.

## Cap and roster legality

- Cap **$375**. Taxi counts **100%**, IR **25%**.
- Floor **$300** after the FA draft until the first game — and for the floor,
  IR counts **100%** and dead money counts too.
- Effective cap is $375 **minus salary adjustments**. **Always pull
  `get_salary_adjustments` and pass it in.** Without it every cap-space figure is
  gross, and for a team carrying dead money it runs $30 or more too generous.
  `get_league`'s `bbidAvailableBalance` already nets them out.
- Free cap space must always be ≥ open roster spots (minimum salary is 1).
- Slots: 18 active, 6 taxi, 4 IR.
- `[2026]` Roster minimums after the FA draft: **2 QB, 3 RB, 4 WR, 2 TE**, with
  taxi and IR counting.

**Deadlines bite.** Roster submission is `[2025]` **$25/day** late, and the
owner-cuts deadline the following day stacks **another $25/day**. Do not cut
early — it influences other owners' decisions.

---

## Run it

```
python3 scripts/contract_options.py --roster roster.json --season YYYY \
        [--adjustments adjustments.json] [--franchise 0001] [--names names.json]
```

Feed it the raw `get_rosters` payload and the raw `get_salary_adjustments`
payload. It returns, per franchise: cap space net of dead money, committed
salary, floor charge and headroom, roster counts, every player with a decision
due plus each legal option and its price, everyone under contract with their cut
cost, and the reminders above.

**Run without `--adjustments` and the output says so and sets
`adjustmentsSupplied: false`.** Never quote cap space from such a run.

If the script is missing, the tables in this file are the whole specification:
group by franchise, charge taxi at full and IR at a quarter, flag every player
whose `contractStatus` equals the season as facing a decision, price the options
from the tables above, and subtract salary adjustments before stating cap space.

### Sanity checks worth doing on the output

- A rookie in contract year 1 cuts for nothing.
- A contracted player on IR: cap hit a quarter of salary, cut cost the full
  remaining contract. Those two looking inconsistent is correct. **Test this on a
  Long-Term or Short-Term player** — a Free Agent on IR shows 25% for both,
  because the Free Agent dead-money rule is 25% anyway. That is a bad test case,
  not a bug.
- Someone on a plain `Short-Term` shows the two-year extension, and shows a
  second short-term explicitly marked NOT LEGAL.
- `capSpace` and `capSpaceBeforeAdjustments` differ for any team carrying dead
  money. Equal, for such a team, means adjustments were not passed in.

---

## Answering well

- **Lead with the decision, not the table.** "Three players have decisions due;
  Hockenson is the expensive one at 33 short-term or 38 long-term."
- **Give the release consequence alongside every keep price.** For an expiring
  contract that consequence is "free", and saying so is the point.
- **Flag the trap where it applies**, not as a preamble: the short-term dead end,
  the rookie year-1 free cut, the IR asymmetry.
- **State the deadline** whenever the answer is decision-shaped.
- **Never put internal identifiers in the answer.** MFL rosters are keyed by
  player id; an owner does not know or care that Jaylen Warren is `15742`.
  Resolve every id with `get_players` before writing, and if an id will not
  resolve, say the player could not be identified rather than printing the
  number. Same for franchise ids — use the owner's name. That includes the line that says whose team you are looking at: write the owner's
  name or the team name, never "franchise 0001". Four of twenty-two answers on the first
  eval run (9 Sep 2026 PT) put the id in exactly that opening line.
- **Do not narrate which franchise record you matched, or how.** The owner knows
  who they are. Open with the answer itself; the team name may appear, the id
  never does. Telling the rule as "never print the id" did not stop it (two more
  answers on 9 Sep 2026 PT opened with the id): the id appears because the answer
  was showing its lookup, so do not show the lookup.
- **Never quote cap space without adjustments in hand.**
- Don't explain the format back to the reader; everyone here knows it.
- Where a number blends sources, give one figure, not two with a slash.

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
