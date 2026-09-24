# Dynasty of Whiners — LM add-on

**Requires `dow-league`. Install that first.** These skills lean on the contract
and cap rules in `league-rules`; installed alone this package degrades quietly
rather than erroring, which is the worst failure mode available.

| Skill | What it does |
|---|---|
| `league-schedule` | Computes the three tiers from prior-season results, generates a validated 14-week schedule, produces the MFL import block |
| `rookie-draft-grades` | The annual humorous rookie draft writeup |
| `fa-auction-grades` | The post-auction money report |
| `league-cut-audit` | Pairs MFL's automatic 25% row for each cut of a guaranteed contract with the LM's 75% row, checks #general for the 24-hour report, and lists the entries still to make by hand |

## Why these are separate

**Anything that produces an artifact of record is LM-only.** If members held a
generative schedule skill, every member could produce a plausible schedule that
is not the one in MFL — silently, confidently, and differently from each other.
Members read the schedule back from MFL instead (`league-matchups`), so a
re-roll propagates automatically and there is nothing to invalidate.

The cut audit is LM-only because it reads Discord through LM-only tools and
its output is a list of entries to make in the league's cap ledger.

The grades skills are LM-only for a duller reason: they post to Discord, and
nine extra people carrying their descriptions makes those skills fire on
ordinary draft questions.

## Both writeup skills have a hard review gate

Nothing posts without an explicit go-ahead. That gate has caught a factually
wrong headline joke, a bad valuation, and a self-contradicting ranking claim.
It is not a formality and nothing about these posts is urgent.

## `league-schedule` needs prior-season data

It reads `get_weekly_results` for the season before the one being scheduled —
week 17 identifies the final two playoff games (which set Tier 1), and weeks 15+
give the consolation points to subtract from MFL's `pf`. Every key reaches it:
lineups are visible league-wide in this league, so `get_weekly_results` is on
the owner surface with no season restriction (dowgateway 1.6.8).
