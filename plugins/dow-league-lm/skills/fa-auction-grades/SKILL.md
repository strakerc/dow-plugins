---
name: fa-auction-grades
description: "Use when writing the humorous post-auction FA money report for Straker's dynasty league — best/worst buys, manager standings, posted to Discord #draft."
---

# FA Auction Writeup

The annual humorous free-agent auction money report for Straker's dynasty league
(MFL league 29557), posted to Discord `#draft`. Two lists — the funniest worst buys
and best buys — plus a manager standings table.

**Read `claude/fa-auction-grades-method.md` in the Dynasty Football League project
before starting.** It carries the full runbook, the three pricing traps with their
fixes, the prior-year baseline, and the exact tool calls. This skill exists to make
sure that doc gets opened; it is not a substitute for it.

Sibling: `rookie-draft-grades` / `claude/rookie-draft-grades-method.md`.

> **Editing note — do not "correct" this.** Small amounts are spelled out ("one
> dollar") rather than written with a dollar sign and a single digit. A dollar
> sign immediately followed by one digit is silently replaced, at invocation
> time, with a word taken from the arguments the skill was called with. Two or
> more digits are safe. Details: the repo README, "A convention that looks
> like a typo and is not".

## ⛔ Two hard rules

**1. Nothing gets posted without Straker's manual review.** Deliver as a file with
per-message character counts, wait, revise, post only on an explicit go-ahead. The
review is load-bearing — it has caught a factually wrong headline joke, a bad
valuation, and a self-contradicting ranking claim.

**2. Any claim that references a depth chart requires pulling the current depth
chart** — every time, at the time of writing, from a live source.

Neither is negotiable on time pressure. Nothing about this post is urgent.

## Skeleton

1. **Ground truth is `get_rosters`**, whose `drafted` field reads `"Auction $78"`.
   Never parse a prose summary table for prices — the project's own auction doc
   undercounts buyers and collapses grouped rows.
2. **Reprice to money actually spent.** FantasyPros' dollars assume a full $375
   roster build; scale total FP-equivalent value up to total spent.
3. **Apply the three traps** (method doc, Step 3): FP's auction board is shallower
   than its ranking board, so a listed price of **one dollar means "no data"** —
   fill those gaps from `player_owned_avg`, floored to one dollar under ~5%
   rostered; FP's superflex QB dollars assume an empty QB slot, so anchor QBs to
   this league's own clearing prices; and any player whose rostership outruns his
   published price is a stale-board candidate needing a depth-chart check.
4. **Mine the contract rules** — for every buy, check whether the buyer already owned
   that player last year (`get_rosters season=YYYY-1`) and what re-signing would have
   cost. This is the single richest joke source in the dataset.
5. **Write**, then check for duplicate joke structures and cross-list claims that
   contradict the rankings. Straker goes on the list when the numbers say so.
6. **Review gate.** Deliver the file. Stop.
7. **Post** to `#draft` (`703738094259666964`), sequentially, 2,000 chars per message.

## Formatting

- Single newline after a standalone bold entry title — Discord already gives a
  fully-bold line its own bottom margin, and a blank line on top of that double-spaces
  the post. Blank lines between entries and body paragraphs only.
- Prefer `## HEADER` over a bold line for section headers.
- Verify spacing with one throwaway message in `#commish-chat` before the real post.
- Single averaged figure when blending sources — never two numbers with a slash.
- Never explain league or format context; the audience is the league.

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
