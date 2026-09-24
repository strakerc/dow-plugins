---
name: league-cut-audit
description: "Invoke before any league tool call when a league manager asks to audit cuts of players on guaranteed contracts in the Dynasty of Whiners league (MFL 29557) — reads every salary adjustment, pairs MFL's automatic 25% row with the LM's 75% row, lists each cut whose LM entry is missing or the wrong amount, checks #general for the 24-hour report, and hands the LM the entries to make by hand. Use for \"audit the cuts\", \"any cuts missing dead money\", \"who cut a guaranteed contract\", \"did anyone report their cut\", \"missing salary adjustments\", \"check the salary adjustments\", \"dead money audit\", or \"did I enter the 75%\". Never writes to MFL. What a cut would cost one owner, or his cap space, is league-contracts."
---

# League Cut Audit

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

The Constitution: cuts of players on **guaranteed contracts** must be reported to
the LMs so the guaranteed money is charged, because MFL charges only 25% on its
own. This skill is the LMs' audit of that. It answers two questions for every
guaranteed cut — **is the full charge entered, and was the cut reported in
time** — and gives the LM the exact entries still to make.

**Nothing here writes to MFL.** No league tool can add, change or remove a salary
adjustment. If the LM asks you to enter one, say so in the first line, then give
the entries: the LM makes them by hand in MFL's commissioner tools, under Salary
Adjustments. Never say an adjustment was added.

The rules behind the numbers — the percentages, the 24-hour window, the extra
year for an unreported cut and when it applies — belong to `league-rules`. The
reconciliation below is the mechanics of checking them, not a second copy.

## Calls

1. `get_league` — franchise ids to owner first names and team names.
2. `get_salary_adjustments` for the current season.
3. `get_salary_adjustments` with `season` set to the **previous** season: its
   cuts are paired the same way, and it feeds the carry-forward check below.
4. Discord, for the report check, only when there is a guaranteed cut dated this
   season (see below):
   `list_guilds`, then `list_channels` for the league's server, then
   `get_messages` on **#general** with `limit` 100. It returns newest first; call
   it again with `before` set to the oldest message id you have until the oldest
   message is earlier than the earliest guaranteed cut you are checking. Stop
   there: an older page cannot hold a report of a later cut.

## Reading the rows

**MFL's own row** — one per drop that still owes money, written the moment the
player is dropped:

> `Dropped <Last>, <First> <NFL team> <pos> (Salary: <S>, Type of Contract: <T>, Year: <Y>, Signed Through: <YYYY>)`

Its `amount` is 25% of the salary. Write the player as First Last. The
`timestamp` is Unix seconds; convert it to Pacific.

**Which season a row belongs to — by its date, not by the list it is in.** A
season's list also holds rows carried over from earlier seasons, under their
original ids and dates (the 2026 list holds 2025 cuts still being charged). A
row belongs to season S when it is dated from 1 February of S to 31 January of
S+1, Pacific. "This season's cuts" means rows dated in this season; the rest of
the current list is carried over and is checked only by the carry-forward check.

**The LM's row** — every row that does not start with `Dropped`. Its text is
typed by hand and follows no format: "For Kmet through 2026", "For troy Franklin
through 2026; reported within 24h", "For OBJ cut unreported, so through 2026".
A last name only, a nickname, lower case: all seen. So **the name is the weakest
part of the match**, and the amount is the strongest.

**Which cuts are guaranteed.** Every contract type except **Free Agent** and
**Rookie**. MFL spells the guaranteed ones several ways, some with a trailing
space: `Short-Term`, `Short-Term Ext.`, `Short-Term (Extension)`, `Short-Term
Extension`, `Long-Term`, `Franchise Tag`. Treat every variant as guaranteed. A
Free Agent or Rookie row's 25% is its whole charge: it needs no LM row and is not
listed as a finding.

**Drops with no MFL row owed nothing.** Measured 24 Sep 2026 PT against every
drop of the 2026 cut deadline on three teams: each one without a row was a
contract that had already ended or a rookie between years 1 and 2, both free. So
the adjustments list is the complete record of the cuts that cost money, and the
transactions feed is not needed.

## Pairing each guaranteed cut with its LM row

For each guaranteed MFL row, the LM row that completes it has, in order of
weight:

1. the **same franchise**,
2. an amount of **three times the MFL row's** — the remaining 75% — to the cent,
3. a **later timestamp**,
4. the player's name in some form, if it is there at all.

Match on 1 to 3 and treat 4 as confirmation. Each LM row completes one cut at
most. Pair every guaranteed cut before classifying any of them: a row taken by
one cut cannot explain another. Then every guaranteed cut lands in one of these:

| Outcome | What it means | What to tell the LM |
|---|---|---|
| **Complete** | A row matches 1 to 3 | Nothing to do; count it |
| **Wrong amount** | A row names the player, same franchise, but its amount is not 3× | The amount entered, the amount owed, and the difference to add or remove |
| **Possible partial entry** | No row matches, but the same team has an LM row dated after the cut that completes nothing else | That row's amount, the amount owed, and the difference; the LM confirms it is this cut's |
| **Missing** | No row matches, and no unpaired LM row on that team could be it | Enter 75% of the salary, and say through which season |
| **Ambiguous** | Two cuts on one team at the same salary, and the LM rows do not name them apart | List both; the LM says which row is which |

An LM row that completes no cut is **not** an error: LMs enter other
adjustments too. List those once, briefly, under "other adjustments", with no
verdict.

## Every remaining year

A guaranteed cut costs 100% of **every** remaining season through `Signed
Through`, and one extra season if it went unreported (see below). The rows carry
it: a cut's two rows reappear in each later season's list under the **same row
ids** (measured 24 Sep 2026 PT, a 2025 cut signed through 2026 appears in both
seasons' lists). Whether MFL or an LM carries them forward was not observed, so
check the result, not the mechanism:

- **Carry-forward check.** Every guaranteed cut in the previous season's list
  whose `Signed Through` is this season or later, or whose LM row says
  "through" this season or later, must appear in this season's list with **both**
  rows. Match on the row id first. One missing is a finding: "carry into
  <season>", with the amount.
- **Last season's cuts** are paired exactly like this season's, from the
  previous season's list. A gap there is still a finding — report it under
  "Last season", with the amount, and leave to the LM whether a closed season
  is corrected.
- **This season's cuts** with `Signed Through` beyond this season: say through
  which season the charge runs, so the LM knows the rows must still be there
  next year. There is no next season's list to check yet — say so, do not guess.

## Was it reported?

The window is 24 hours from the drop (`league-rules` holds the rule). Reports go
to **#general**. For each guaranteed cut this season, look at the #general
messages from the drop time to 24 hours after it for one that names the player —
last name, first name or an obvious nickname — or clearly announces that team's
cut. The LM ruled on 24 Sep 2026 PT that an LM's own message about the drop,
inside the window, counts as the report. Whoever posted it, name the channel and
the Pacific time and how far into the window it came; **never print a Discord
username**.

- **Reported:** say where and when.
- **No report found in the window:** say so plainly. Under the rule an unreported
  cut carries one extra season at 100%, so the LM row's "through" year should be
  one past `Signed Through`. **The rule's reach is stated two ways — say both,
  pick neither.** `league-rules` limits it to "in-season" cuts and defines that
  as after roster decisions are due and before the FA draft; yet on 17 Sep 2026
  PT the LMs applied the extra year to a cut made after the FA draft, until the
  report was found. If the cut falls outside the digest's window, give both
  readings. The LM makes the call — present it as the finding, not as a penalty
  already decided.
- **The LM row already records it** ("reported within 24h", "unreported"): quote
  it. If the Discord evidence disagrees with the row, say so; that disagreement
  is the most useful thing this check can find.
- **Discord unreachable** (the tools are missing, or the channel will not load):
  say the report check did not run. Never mark a cut reported or unreported
  without having read the window.

Only this season's cuts get the Discord check — dated in this season, by the
rule above, not merely present in this season's list. A prior season's report
history is too deep to page back to and was settled when it happened.

## The answer

Lead with the work the LM has to do. If there is none, one line saying so, with
the count: "All 5 guaranteed cuts this season are fully charged and were
reported."

1. **Entries to make**, one table: Team (owner) | Player | Contract | Cut (PT) |
   Charged now | Enter | Through. Money as plain numbers with two decimals.
   Missing rows, wrong amounts, possible partial entries and carry-forward
   gaps all go here; last season's gaps go in a second table under "Last
   season".
2. **Reporting**, one line per guaranteed cut this season: reported where and
   when, or no report found and what that means for the "through" year.
3. **Complete**, one line: how many guaranteed cuts matched, by name.
4. Free Agent and Rookie cuts: one line with the count, no table. Other
   adjustments: one line each.

If the LM asked for the entries to be made, the no-write sentence comes first.

## Traps

- **Never sum a franchise's rows and call the total the dead money** without
  pairing first. A lone 25% row makes the total look like a quarter of the real
  charge, and that understated number is exactly the finding.
- **A nickname is not a mismatch.** An LM row with the right team and three times
  the amount completes the cut even if its text names nobody you recognise.
- **A wrong amount is not a missing row.** Report what was entered and the
  difference; telling the LM to enter the full 75% again would double-charge.
  That holds when the short row names nobody too: an unpaired LM row on the same
  team is a possible partial entry until the LM says otherwise.
- **Being in this season's list does not make a cut this season's.** Date it.
- **Never re-derive the unreported rule from memory.** `league-rules` has it,
  with its window; quote it.

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
