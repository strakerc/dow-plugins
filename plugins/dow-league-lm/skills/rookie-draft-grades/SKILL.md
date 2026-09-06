---
name: rookie-draft-grades
description: "Produce the annual humorous rookie draft grades writeup for the dynasty league and post it to Discord #draft. Use when asked to grade, recap, or write up the rookie draft."
---

Annual writeup grading every team's rookie draft, posted to the league's Discord `#draft` channel. Funny, with real analysis underneath.

## Before anything else

**Read `claude/rookie-draft-grades-method.md` in the Dynasty Football League project.** It has the franchise map, the exact tool calls, the value methodology, last year's grades, and the known traps. This skill is the guardrails; that doc is the procedure. Read it *before* pulling data, not after drafting.

## Two rules that are not negotiable

### 1. Never post without an explicit go-ahead

Deliver the writeup as a file, split into its final Discord messages with the cut points visible, so the review sees exactly what would be posted. Volunteer what is uncertain — judgment calls, thin claims, anything a leaguemate could argue with — rather than waiting to be asked. Expect several revision rounds; the 2026 post took about seven. "Looks good" is not permission to post. Wait for an instruction to post.

This review is where the worst errors get caught, **after** automated verification has already passed. In 2026 a single challenge ("Kyler is on MIN now") surfaced three separate errors, one of them a false premise sitting under the post's headline claim.

### 2. Pull the current depth chart for any claim that references one

Trigger phrases: "the starter", "the backup", "RB2", "behind X", "wide open backfield", "thin depth chart", "walking into a role", "QB3". If the claim depends on who else is on that roster, check who else is on that roster — at the time of writing, from a live source.

It fails in both directions. In 2026: Carson Beck was written as backing up a quarterback who had been released; Mike Washington Jr. was written as walking into an open backfield that belonged to Ashton Jeanty. **The second kind is more dangerous** — a sentence claiming a job is open does not look unverified, but it is a claim about every player on that roster.

Never substitute a ranking API's `team` field, `draft_team`, training-camp-era reporting, or your own recollection of the offseason for the actual chart.

Neither rule bends for time pressure. Nothing about this post is urgent.

## Shape of the work

1. Pull the draft from MFL — draft results, league (franchise ID → team → owner), players
2. Gather values from three sources: FantasyPros (`position=OP` is what makes it superflex), FantasyCalc, and KTC (manual screenshot — scraping KTC is expressly forbidden)
3. Re-rank each source across **only the drafted players**, then average. One figure in the deliverable, never two numbers separated by a slash
4. Verify every role claim; pull depth charts (rule 2); check who got waived at cutdowns — that news is the best material and appears in no ranking feed
5. Write it — teams ordered by first pick selected, bolded team name as header, numbered list of picks in order, grade A+ through F for every team including any that made no picks
6. **Review gate** (rule 1)
7. Post to `#draft` — split under 2000 characters at team boundaries, posted sequentially, order matters

## If the post fails

**The post is the delivery mechanism, not the deliverable.** The writeup is the work; `#draft` is only where it lands.

If `send_message` errors — permissions, a disabled flag, an outage — say plainly that posting failed and what the error said, then **output the complete writeup in the response**, split at the same cut points, ready to paste by hand. Never end a run with the writeup stranded inside a failed tool call. This is written twice a year over several revision rounds; a regenerated one is a different post, not a recovered one.

**Do not retry.** A silent retry is how `#draft` ends up with the same message twice. If the sequence failed part-way, say which messages landed and output only the ones that did not — pasting the whole writeup on top of a partial post duplicates what already went out.

If `send_message` comes back as `Unknown tool` rather than failing, that is a key problem and not a bug in this skill: the Discord tools reach through the same gateway as everything else and need an `lm` key. Say so, and hand over the text.

## Tone

Funny with real analysis underneath. Mean is fine; humour matters more than ruthlessness. Every joke should sit on a real number or a real news item. Do not explain league or format context back to the audience — they know what superflex is; jokes that *use* the format are good, explainers are not. Grade the commissioner honestly, including onto the worst-reaches list when that is where the numbers put him.

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
