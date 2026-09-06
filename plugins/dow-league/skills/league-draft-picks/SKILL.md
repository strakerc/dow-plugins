---
name: league-draft-picks
description: "Track draft pick ownership for the Dynasty of Whiners league (MFL 29557) — who holds which future picks, where each is likely to slot, and outstanding conditional picks that MFL cannot represent. Use for \"who owns my 2028 1st\", \"what picks does X have\", or \"is anyone owed a pick\"."
---

# League Draft Picks

Picks are currency here. This skill answers who holds what, roughly where each
will land, and — the part no API can tell you — what is still **owed**.

**Always re-derive from live MFL.** `future-draft-picks.md` is a dated snapshot
and goes stale on the next trade. Checking it against live data on 4 Sep 2026
found a pick had already moved since the 29 Aug snapshot.

---

## Two things that trip people

**1. The franchise id in a pick's name is its ORIGIN, not its holder.**
`FP_0002_2027_2` is Pat's 2027 2nd wherever it currently sits. Notation is
`FP_{origin}_{year}_{round}`.

**2. A pick's value follows the origin team's finish, not the holder's.**
Draft order is reverse regular-season standings, so how good a pick is depends
entirely on how the team it came from does in the season *before* the draft.
Early in a season the prior year is a weak anchor — say so rather than implying
precision.

**Only the upcoming three seasons are tradeable.** In the 2026 offseason
that is 2027, 2028 and 2029.

---

## Conditional picks — the part MFL cannot see

**When a trade includes a conditional leg, MFL records only the identified
assets.** The obligation exists solely in the league gSheet's Trade History text
and in two owners' memories. It is absent from `get_future_draft_picks`,
`get_assets`, and the trade record itself.

A real case: a conditional agreed 10 Oct 2025 settled on 31 Dec 2025 as a
*separate, one-sided* trade 82 days later, with nothing linking the two. If
nobody remembers, nothing in the system ever asks.

**The detection heuristic: a trade where one side gives up nothing is almost
always a conditional settling.** In `get_transactions(transaction_type="TRADE")`
that shows as an empty `franchise1_gave_up` or `franchise2_gave_up`. It is the
only machine-readable signal available.

### The vocabulary — settled 5 Sep 2026

These words have league meanings. Draft order is reverse standings, so a pick
from a team that finished *well* lands late in its round and is worth less.

| Word | Selects | Position in the round | Origin team finished |
|---|---|---|---|
| **earliest**, **best** | the better pick | first | worse |
| **latest**, **worst**, **lowest** | the poorer pick | last | better |

**"highest" is NOT settled — do not infer it.** Obligation #1 was written as
"highest at end of season" and the pick that actually conveyed matched no reading
of it: not the earliest slot, not the latest, not the best-finishing origin. Its
meaning is genuinely unknown, so symmetry with the table above is a guess. If a
row says "highest", ask the two owners rather than resolving it yourself.

**Scan the gSheet Trade History on relative-slot language, not the word
"conditional"** — the outstanding one below is labelled only "Latest". Match on:
`latest · earliest · highest · lowest · better of · worse of · contingent · swap`.

**Never trust the sheet's column order.** It is hand-entered free text with no
validation, and at least one row has the two sides reversed — which is how this
very obligation got recorded backwards for a while. Before writing down who owes
whom, reconcile the row against `get_transactions` for that season: match the
player counts, the player names, and above all the picks. A team can never give
up a pick that is not on its own side, so a pick with origin X appearing in the
record means X's column is the one that gave it.

### Outstanding as of 4 Sep 2026

**Pat owes Zef a 2027 3rd — the "Latest 27'3rd". Not conveyed.**

- **"Latest" means the WORST pick of that round.** Settled by Straker, 5 Sep 2026.
  This is no longer an open question: do not present it as ambiguous, and do not
  offer the reading that Zef gets the better pick.
- Draft order is reverse standings, so the latest 3rd is the one whose **origin
  team finished best**. Pat holds two 2027 3rds — his own and Paul's — and which
  of them is "latest" is decided by the **2026** season, not 2025. It is not
  knowable until the regular season ends in week 14.
- Check window **mid-Dec 2026 → mid-Jan 2027** (precedent: the previous
  conditional settled 31 Dec). **Hard backstop: before the 2027 rookie draft**,
  likely early August. Once the pick is used it is unfixable.
- To check whether it has settled: does Zef hold any 2027 round-3 pick that did
  not originate with him?

Full history, the corrected trade record, and the resolved case are in
`conditional-picks.md`.

**A caution on reconstruction.** `get_draft_results` comments name a pick's
*origin* franchise and do not reliably list every hop — a pick that passed
through three teams showed one line. Use `get_transactions` with the right
season instead.

---

## Data recipe

| Need | Call |
|---|---|
| Who holds what | `get_future_draft_picks` — smallest, cleanest |
| Picks plus rostered players | `get_assets` — for building a trade *(LM-only on the gateway)* |
| Slot projection | `get_standings(season=N-1)` |
| Settlement evidence | `get_transactions(transaction_type="TRADE", season=YYYY)` |
| Resolving player ids in a trade record | `get_players(players="id,id,id")` — always pass ids |

## Run it

If `scripts/pick_ledger.py` is present alongside this file:

```
python3 scripts/pick_ledger.py --picks picks.json \
        [--standings standings.json] [--names names.json] \
        [--owner 0001] [--season YYYY]
```

Feed it the raw `get_future_draft_picks` payload. It prints holdings by year with
acquired picks attributed to their origin, flags each franchise's own missing
picks, projects early/mid/late from prior standings, and runs an integrity check
— 12 franchises × 3 years × 4 rounds should reconcile to 144 picks with none
missing, unexpected or duplicated. **A failing integrity line means the data
moved or the year window shifted, not that the tool is broken.**

**The script does not ship with the account-saved copy of this skill** — only
this file does. Where it is absent, do the same work directly: group the
`get_future_draft_picks` payload by holder, mark any pick whose origin differs
from its holder as acquired, list each franchise's own missing picks, and count
the total against 144. The integrity count is the part worth not skipping.

Raise the conditional above every time picks are counted, because the ledger by
construction cannot see it.

---

## Answering well

- **Lead with the answer, then the caveat.** "Paul holds five 2027 picks
  including Gabe's 1st — but Gabe's slot depends on how Gabe finishes."
- **Name the origin owner** whenever a pick is not the holder's own. "Pat's 2027
  2nd" is meaningful in a way "a 2027 2nd" is not.
- **Give the slot as a tier with its basis**, never a precise pick number.
- **Never put internal identifiers in the answer.** Franchise ids (`0012`), pick
  notation (`FP_0012_2027_4`) and player ids (`15742`) are how the API talks, not
  how the league talks. Resolve every one to a name before you write: "Blake has
  Zef's 2027 4th", never "Blake holds `FP_0012_2027_4`". **The notation section
  above exists so you read the data correctly — it is not vocabulary to hand back
  to an owner.**

- **Never quote the script's raw output either.** `own gone: [4]` is a column
  name, not English — write "his own 2027 4th is gone". The ledger prints for a
  developer; you are writing for an owner.
- **Raise an outstanding conditional whenever picks are being counted**, and
  especially before any trade involving that year and round. Say which side owes
  — an obligation recorded backwards is worse than none.
- Don't explain the format back to the reader.

## Worth proposing to the league

When a trade includes a conditional, the Trade History row should state: the
owing team, the exact set the condition selects from, the tiebreak, and the
settlement deadline. One sentence at trade time prevents an argument a year
later, when the only two people who know no longer agree.

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
