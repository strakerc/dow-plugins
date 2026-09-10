# league-lineup back-test

The evidence that `league-lineup` picks legal, optimal lineups. Not shipped to
anyone: only `plugins/` reaches an installed owner, so everything under
`validation/` stays here.

CLAUDE.md says to back-test a skill against a decision that already happened.
This is that, made runnable.

## The fixtures are not in this repo, deliberately

Every script reads JSON files that must sit beside it, and **none of them are
committed** — `.gitignore` blocks `*.json` in this directory.

`league.json` is the reason. It is a raw `get_league` payload, which carries every
owner's phone number, email address and MFL username. This repository is public.
A number is published the moment it lands and `git revert` does not unpublish it,
so the fixtures live on disk and nowhere else.

The other files carry no contact data, but they are league data, which invariant 4
keeps out of the repo regardless.

## Regenerating them

Six connector calls. **Save each raw tool response exactly as returned** — the
scripts read `["result"]["content"][0]["text"]` and then parse that string, so
they expect the whole MCP envelope, not the payload alone.

| File | Call |
|---|---|
| `league.json` | `get_league` |
| `players.json` | `get_players` with the id list from the rosters below |
| `rosters2025.json` | `get_rosters` with `season=2025` |
| `scores_w3.json`, `scores_w8.json`, `scores_w13.json` | `get_player_scores`, `season=2025`, `week=3` / `8` / `13` |
| `match_w3.json`, `match_w8.json`, `match_w13.json` | `get_matchups`, `season=2025`, `week=3` / `8` / `13` |

Weeks 3, 8 and 13 are early, middle and late in a 14-week regular season. Nothing
else is special about them; change them if you have a reason.

## The scripts

```bash
python3 backtest.py
```

Runs the skill's stated method over 12 franchises × 3 weeks, using **actual 2025
points** as the ranking input. That is perfect foresight and deliberately so: it
measures the chooser, not a forecast. It builds each optimum and asserts the hard
gates — exactly ten starters, no duplicate, nobody from IR or the taxi squad, and
every position inside its limit. Expect 36 lineups, zero gate failures, the
line `ALL HARD GATES PASS`, and exit code 0. Any failure exits 1 -- until
9 Sep 2026 PT the script exited 0 either way, and `validation/regress.py` read
that as a pass.

```bash
python3 adversarial.py
```

Two questions the clean run cannot answer.

**Is the optimum actually optimal, or just what the enumeration found?** It throws
a million random legal lineups at each franchise and checks none beats the
enumerated answer. Want zero.

**Do the gates fire, or are they decorative?** It mutates a known-good lineup —
drops a starter, duplicates a player, starts someone from IR, starts a taxi-squad
player, plays three quarterbacks — and each must be refused. A gate never watched
failing is not a gate. It also starves a pool of tight ends and requires that the
optimiser return *nothing* rather than something illegal. A clean run ends with
`ALL ADVERSARIAL CHECKS PASS` and exit code 0; any failure is listed and exits 1.

```bash
python3 rules_check.py
```

Checks whether the 2025 lineup shape differed from 2026, since the back-test uses
2025 rosters against the 2026 starters block. Read its docstring: its original
premise was wrong, and a stronger version of the check is now possible.

## What is still unverified

The **presentation** layer. These scripts prove the lineup is legal and optimal;
nothing here checks that the output obeys the skill's own rules — two separately
labelled tables never merged, the opponent stated as a prediction, no franchise
ids, player ids, usernames, emails or phone numbers, and a lock time in Pacific.

That needs a model executing the skill and someone reading what comes out. The
eval case `validation/evals/dow-league/lineup-two-tables` now asserts exactly
those rules against the synthetic league; as of 9 Sep 2026 PT it has not been run
either — see "What is unverified" in `validation/TEST-PLAN.md`.
