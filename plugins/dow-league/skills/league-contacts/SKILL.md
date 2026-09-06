---
name: league-contacts
description: "Reach a Dynasty of Whiners league member (MFL 29557) — a phone number, an email address, or the whole member directory, read live from MFL and never stored. Use for \"what's X's number\", \"how do I reach X\", \"contact info\", \"email address\", \"phone number\", or \"everyone's contact details\". Not for roster, contract, draft-pick or matchup questions about a franchise."
---

# League Contacts

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

Worth knowing while answering: at the time of writing the backend workers still run
`GATE_MODE=off`, and the flip to `internal` has not happened yet.

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
