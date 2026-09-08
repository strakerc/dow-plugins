---
name: league-matchups
description: "Look up the Dynasty of Whiners regular-season schedule (MFL 29557) — who a franchise plays in a given week, which scheduling tier a team is in and why, and strength of schedule. Use for \"who do I play\", \"when do I play X\", \"what tier am I in\", or \"who has the easiest schedule\"."
---

# League Matchups

Read-only schedule lookup. **MFL is the schedule; this skill reports it.**

> **Never generate a schedule to answer a lookup.** Generation lives in
> `league-schedule`, which is LM-only, and it produces the artifact of record.
> If two people generate schedules they get two different valid answers, and
> neither is the one the league is playing. If MFL has no schedule loaded for
> the season yet, say exactly that. Do not fill the gap with a plausible one.

## Getting it

`get_matchups` returns pairings by week — no lineups, no scores. Pass `week` for
one week, omit it for the season.

That narrowness is deliberate. `get_weekly_results` also contains the schedule,
but it carries every franchise's starting lineup, bench, per-player scores and
computed optimal lineup, so it is not on the member surface. If `get_matchups`
is unavailable, say the schedule tool is not reachable — do not reach for
weekly results instead.

## The three tiers, and why anyone asks

The regular season is built from a tiering of the previous season:

- **Tier 1 — the four teams who played in the final two playoff games**, the
  championship and the third-place game. **By playoff finish, not by scoring.**
  This is the part people get wrong; getting it wrong once rebuilt a whole
  season's schedule.
- **Tier 2** — the next four by regular-season points for.
- **Tier 3** — the bottom four by regular-season points for.

Tier 1 plays a harder schedule; Tier 3 an easier one. That is the point of the
system, so "why do I play them twice" usually has a real answer.

**Regular-season points for is not MFL's `pf`.** That field covers every scoring
week, and non-playoff teams keep playing consolation games, so all twelve
franchises carry points from weeks 15 on. Subtract those before ranking anyone,
and say you did.

**2026 note.** The schedule was rebuilt on 8 Sep 2026 PT after the original was
built on a superseded reading of the tiering rule. Straker moved from Tier 1 to
Tier 2 and Gabe from Tier 2 to Tier 1; Tier 3 was unchanged. Weeks 4, 8 and 12
differ from what owners saw before that date. If someone's memory of their
schedule disagrees with MFL, this is why — MFL is right.

## Answering well

- **Lead with the matchup**, then the context. "Week 6 you're at Pat."
- **Name the tier and the reason** when tiers come up — "Tier 1, because you
  were in the third-place game" is an answer; "Tier 1" is a label.
- **Strength of schedule is a comparison**, so state what you compared: opponent
  tiers, or opponents' prior-season regular-season points, and which.
- If the season's schedule is not in MFL yet, say so plainly and stop.
- Don't explain the format back to the reader.

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
