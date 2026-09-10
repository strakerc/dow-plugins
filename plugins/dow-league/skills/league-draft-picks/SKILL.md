---
name: league-draft-picks
description: "Invoke before any league tool call for draft-pick questions in the Dynasty of Whiners league (MFL 29557) — who holds which future picks, where each is likely to slot, and the outstanding conditional picks that MFL cannot represent. Use for \"what draft picks does X have\", \"what picks does X have\", \"who owns my 2028 1st\", \"is anyone owed a pick\", or any count of picks. The raw picks payload is franchise ids and pick codes an owner cannot read; this skill resolves them to names and adds the conditional obligation MFL does not show. Not for what a pick pays on a rookie contract (league-rules)."
---

# League Draft Picks

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

Picks are currency here. This skill answers who holds what, roughly where each
will land, and — the part no API can tell you — what is still **owed**.

**What a pick pays on a rookie contract, and for how long, is `league-rules`** —
the rookie scale lives there and nowhere else. Invoke it for that question; this
skill holds no prices, and answering from NFL contract knowledge is wrong here.

**Always re-derive from live MFL.** `future-draft-picks.md` is a dated snapshot
and goes stale on the next trade. Checking it against live data on 4 Sep 2026
found a pick had already moved since the 29 Aug snapshot.

---

**Answers are written for owners: names only.** If a franchise id such as `0002`
or a pick code such as `FP_0002_2027_2` appears anywhere in your reply — even in
parentheses after a team name — you have made an error. Say "Bram" or "Bram's
Whiners"; the id is how the payload is keyed, not part of the name. Three eval
runs on 9 Sep 2026 PT put it after the team name anyway.

## Three things that trip people

**1. The franchise id in a pick's name is its ORIGIN, not its holder.**
`FP_0002_2027_2` is Pat's 2027 2nd wherever it currently sits. Notation is
`FP_{origin}_{year}_{round}`.

**2. A pick's value follows the origin team's finish, not the holder's.**
Draft order is reverse regular-season standings, so how good a pick is depends
entirely on how the team it came from does in the season *before* the draft.
Early in a season the prior year is a weak anchor — say so rather than implying
precision.

**3. `DP_` is a different notation from `FP_`, and it is zero-based.**
`DP_{round}_{pick}` appears in trade records for current-year rookie picks, and
both numbers start at zero — `DP_1_3` is round 2, pick 4, not round 1, pick 3.
`FP_{origin}_{year}_{round}` uses real round numbers; do not read the two the
same way. Confirm any `DP_` reference against `get_draft_results` for that
season before naming a slot: an off-by-one here produces a plausible pick with
no error anywhere. Found 7 Sep 2026, when `DP_1_3` in a 2026 trade was reported
as 1.03 and was actually 2.04.

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
  to an owner.** That includes the line that says whose team you are looking at: write the owner's
  name or the team name, never "franchise 0001". Four of twenty-two answers on the first
  eval run (9 Sep 2026 PT) put the id in exactly that opening line.
- **Do not narrate which franchise record you matched, or how.** The owner knows
  who they are. Open with the answer itself; the team name may appear, the id
  never does. Telling the rule as "never print the id" did not stop it (two more
  answers on 9 Sep 2026 PT opened with the id): the id appears because the answer
  was showing its lookup, so do not show the lookup.

- **Never quote the script's raw output either.** `own gone: [4]` is a column
  name, not English — write "his own 2027 4th is gone". The ledger prints for a
  developer; you are writing for an owner.
- **Every pick count ends with one line that begins "Conditional obligations:"** —
  the outstanding one from the section above with who owes whom, or "none affecting
  <owner>" after checking the gSheet language and the one-sided trades. The line is
  not optional and it is not a preamble: MFL cannot show these, so an answer
  without it is silently incomplete. Raise it especially before any trade
  involving that year and round; an obligation recorded backwards is worse than
  none.
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
