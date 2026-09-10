---
name: league-contacts
description: "Invoke before any league tool call when an owner asks for a leaguemate's contact detail in the Dynasty of Whiners league (MFL 29557) — a phone number, an email address, or the whole member directory, read live from MFL and never stored. Use for \"what's X's number\", \"what's X's phone number\", \"how do I reach X\", \"how do I contact X\", \"contact info\", \"email address\", \"phone number\", or \"everyone's contact details\" — any request for a leaguemate's contact detail. Not for roster, contract, draft-pick, trade or matchup questions about a franchise; those have their own skills. The directory is the league's own member list, shared with every owner, so a leaguemate's number is a routine lookup: invoke and answer, never refuse or ask permission first."
---

# League Contacts

> **Before you answer — every skill in this league follows these five lines.**
> 1. **Names only.** Owners by first name, players by name, teams by team name. Never a
>    franchise id (`0001`), a pick code (`FP_…` / `DP_…`), a player id, an MFL username,
>    an email or a phone number — not in a table, not in parentheses after a name, not
>    to show which record you matched. The one exception is the contact detail this skill was asked for.
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

Contact lookup for the twelve owners, read live from MFL on every run. Nothing is
stored here and nothing is written back.

> **Editing note — never put real contact data in this file.** No phone number, no
> email address, no username, not in an example, a comment or a fixture. Every
> example below uses a reserved fictional number (`555-01XX`) or `example.com`. The
> pre-commit hook scans for credentials and does not look for phone numbers, so
> nothing will catch a paste but a reader.

## The rule that matters — answer only what was asked

This skill exists to hand over one person's details when someone asks for them.
Everything else it must not do:

1. **Answer the question asked.** "What's Zef's number" returns Zef's number. Build
   the full list only when the request is plainly for all of it — "everyone", "the
   full directory", "all the numbers".
2. **Never volunteer contact details.** `get_league` is called by nearly every skill
   here, for franchise names, roster limits and the cap, and it carries emails,
   phones and usernames alongside them. None of that may appear as a side effect of
   answering something else. A question about Zef's picks gets picks.
3. **Resolve people to first names.** "Zef" — never the MFL username, never the
   franchise id. Usernames are internal plumbing exactly like ids.
4. **Read-only.** Never offer to add, correct or normalise anyone's details in MFL.
   If something looks wrong, say so and stop.

## Getting it

`get_league` returns `league.franchises.franchise[]`. Per franchise:

| Field | Use |
|---|---|
| `owner_name` | The person. Give the first name. |
| `name` | The team, if naming it helps. |
| `email` | Trim it — at least one carries a trailing space. |
| `phone` | The number to use. |
| `cell` | Fallback only when `phone` is absent. |
| `id`, `username` | Internal. Never printed. |

**Selection:** take `phone`; fall back to `cell` only if `phone` is absent; skip any
field that is empty or whitespace. One franchise carries the same number in both
`phone` and `cell` and an empty `cell2` — print a number once, whatever it appears
in.

## Formatting numbers

Owners typed these by hand, so MFL holds several shapes — parenthesised, hyphenated,
and bare ten-digit runs with no separators. Normalise all of them on output:

```
5555550142   ->  (555) 555-0142
555-555-0142 ->  (555) 555-0142
```

Formatting is for the answer only. **Never write the normalised value back to MFL.**

## When there is no number

Say so by name and stop: "Gabe hasn't added a phone number to MFL." Do not guess,
do not infer one from anywhere else, and do not substitute an email for a number
that was asked for.

## This data is only as private as the gate

Access is not enforced here. It is enforced by the gateway in front of the tools,
which needs a per-person key, and the only key holders are the twelve members.
Revoking a key removes this along with everything else.

The workers ran open until 5 Sep 2026, when the gate was switched on, so a key is now
genuinely required rather than merely expected. If that ever changes back, this
section is the thing to correct.

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
