# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this repository is

A **Claude plugin marketplace**, not an application. `.claude-plugin/marketplace.json`
lists two plugins under `plugins/`; people add this repo's URL in Claude and install
from it, so every commit here loads as instructions inside other owners' accounts.

The deliverable is almost entirely **prose**: eight `SKILL.md` files. The four Python
scripts are optional accelerators — each skill states what to do when its script is
absent, because an account-saved copy of a skill ships without `scripts/`. Keep that
fallback accurate whenever a script changes.

**This repo is the source of truth for skill text and scripts.** Copies saved to
anyone's Claude account are dead ends: no scripts, and they drift. Straker's own
account copies were deleted 6 Sep 2026. Edit here, never there.

There is no build, no dependency manifest, no test suite, and no runtime beyond
`python3` for the scripts.

Owners read the output in a chat window, mid-trade. Not developers. That shapes the
conventions below.

## Commands

```bash
git config core.hooksPath .githooks    # once per clone — the hook is the only gate
```

```bash
.githooks/pre-commit                   # run the gate manually against staged files
```

Scripts take **raw connector payloads saved to JSON files**. None of them touch the
network; you feed them what the MFL tools returned.

```bash
python3 plugins/dow-league/skills/league-contracts/scripts/contract_options.py --roster roster.json --season 2027 --adjustments adjustments.json
```

```bash
python3 plugins/dow-league/skills/league-draft-picks/scripts/pick_ledger.py --picks picks.json --standings standings.json
```

```bash
python3 plugins/dow-league-lm/skills/league-schedule/scripts/compute_tiers.py --data prior-2025.json --season 2026 > season-2026.json
```

```bash
python3 plugins/dow-league-lm/skills/league-schedule/scripts/build_schedule.py --config season-2026.json --seed 7
```

`build_schedule.py` self-validates: it prints eight checks and asserts both week-1
rematch teams are Tier 1. A schedule that fails a check is a bug in the config or the
generator, not a schedule to ship.

`pick_ledger.py` ends with an integrity check: 12 franchises × 3 years × 4 rounds must
reconcile to 144 picks. A failure means the data moved or the year window shifted, not
that the tool is broken.

## Hard invariants (the pre-commit hook enforces all four)

1. **Never add a `.mcp.json`.** A plugin *can* declare its own connector, and the
   connector URL carries a per-owner key. This repo is public. Also blocked: `.env*`,
   key/cert files, `wrangler.toml`, and credential-shaped strings in added lines.
2. **Never write `$` followed by a single digit in a `SKILL.md`.** At skill-load time
   that token is silently replaced by a word from the invocation arguments — it once
   rewrote the rookie salary scale into prose with no error. Write `+5`, or put the
   unit in the table header. `$25` and `$375` are safe. Several skills carry an
   editing note saying this; do not "fix" it.
3. **All `*.json` must parse.** A broken manifest breaks the install for everyone, and
   the failure surfaces in someone else's Claude.
4. No league data, member contact details, or credentials in the repo at all.

The hook scans **added lines only** — one that re-flags existing content trains
everyone to use `--no-verify`.

**Invariant 3 needs an interpreter** (it is section 4 in the hook). The JSON check
wants a working `python3`, `python` or `node`, and the hook probes each candidate
from *both* sides: it must accept valid JSON and reject invalid JSON. One that exits
0 for every input would otherwise be selected and turn the check into a no-op that
still looks active — a worse failure than a false block, because it is silent. When
no candidate qualifies the check is skipped rather than failed, so a machine without
an interpreter can still commit, but the hook prints a `note: ... was NOT checked`
line naming each unchecked file. If you see that note, the manifest was not verified.

The probe exists because Windows ships Microsoft Store stubs at
`WindowsApps\python3.exe` which sit on PATH, answer before anything else, and exit 49
with an install message. Straker's box has run Python 3.13.15 ahead of them since
5 Sep 2026, so invariant 3 is live there. Note the Windows installer creates
`python.exe` but never `python3.exe` — that file is a hand-made copy, and without it
`python3` reaches the stub.

## The two-plugin split

`dow-league` is for all twelve owners; `dow-league-lm` is the LM add-on and depends on
it (the LM skills lean on `league-rules`). The line is deliberate:

- **Anything that produces an artifact of record is LM-only.** Members *read* the
  schedule back from MFL via `league-matchups`; generation lives in the LM-only
  `league-schedule`. If members could generate schedules, twelve people would hold
  twelve plausible schedules, none of them the one MFL is playing.
- **Anything that posts to Discord is LM-only**, partly so nine extra copies of those
  descriptions don't fire on ordinary draft questions.

When adding a skill, decide which package it belongs to on that rule, and mirror the
new skill in the owning plugin's `README.md` table.

## How skills get their facts

Every fact comes from MyFantasyLeague (league `29557`) through a per-owner connector
that each person adds to their own account. The plugin carries no key and no data —
**without a key it is inert**, which is the intended security model, not a bug.

Common tools: `get_rosters`, `get_future_draft_picks`, `get_salary_adjustments`,
`get_standings`, `get_weekly_results`, `get_transactions`, `get_players`,
`get_matchups`, `get_league`, `get_assets`, `get_draft_results`.

Key consequences that shape the prose:

- A tool the owner's key cannot reach reports as `Unknown tool`, not a permission
  error — so "missing tool" means a key problem, not a broken skill.
- Every `SKILL.md` ends with the same **"If the league tools aren't there"** footer:
  the connector-setup instructions, the 401 case, and a ban on answering from memory
  or from examples in the file. Copy it verbatim into any new skill.
- MFL's live feed blanks contract fields the moment a player is dropped, so historical
  questions must use `get_rosters` with an explicit `season` (the week-22 snapshot).
- **Conditional draft picks are invisible to MFL.** They are agreed in Discord and
  recorded as free text in the league gSheet, so no API call will ever surface one.
  `league-draft-picks` carries the outstanding obligation by hand; raise it whenever
  picks are counted.

## Skill boundaries — respect them when editing

| Question | Owning skill |
|---|---|
| Rules, cap, deadlines, penalties | `league-rules` (digest of Constitution 2.0; the Google Doc is source of truth) |
| Decision-due, option prices, dead money, cap/roster legality | `league-contracts` — reports the *personal* tag floor only |
| Positional tag floors from last season's top-5 salaries | `league-franchise-tags` |
| Who holds which future pick, conditional obligations | `league-draft-picks` |
| Reading the schedule back | `league-matchups` (read-only) |
| Generating the schedule | `league-schedule` (LM-only) |

Duplicating a price table across skills is how the two skills drift apart. Cross-
reference instead, as they currently do.

## Conventions the skills share

- **Never surface internal identifiers in an answer** — franchise ids (`0001`), pick
  notation (`FP_0012_2027_4`), player ids (`15742`). Resolve them to names first. The
  one exception is the MFL schedule import block, which is machine input.
- **Never quote a script's raw output as prose.** The scripts print for a developer;
  `own gone: [4]` becomes "his own 2027 4th is gone".
- **Relative-slot vocabulary is settled — do not re-derive it.**

  | Word | Selects | Position in round | Origin team finished |
  |---|---|---|---|
  | earliest, best | the better pick | first | worse |
  | latest, worst, lowest | the poorer pick | last | better |

  **"highest" is NOT settled.** The one obligation written that way conveyed a pick
  matching no reading of it. If a trade record says "highest", ask the two owners.
- Rules carry year tags like `[2026]`, and some have future effective dates. Check the
  tag before quoting a price for a later season.
- If a rule is stated two different ways anywhere, say so rather than picking one — a
  duplicated, contradictory tier rule shipped a whole wrong season's schedule.
- Don't explain the league format back to the reader; everyone here knows it.
- Both writeup skills (`rookie-draft-grades`, `fa-auction-grades`) have a **hard review
  gate**: nothing posts to Discord without an explicit go-ahead, and that gate is
  load-bearing — it has caught factually wrong headline claims.
- **Never automate writes** to MFL's schedule setup (saving overwrites all 84 rows with
  no undo) or to the league gSheet (it holds member phone numbers and emails). KTC
  scraping is forbidden by their ToS; the Google service-account key never ships.

## Validating a change to a skill

**Research first, then write.** Every number in a skill came from a live MFL call or a
back-test, not from memory.

**Back-test against a decision that already happened.** A skill run on an open question
produces a plausible answer nobody can check. `league-contracts` was validated by
re-deriving all twelve 2025→2026 re-signings and matching price and term. That is the
only cheap way to catch confident-and-wrong.

**Design the test so one thing explains a failure.** The first IR cut-cost probe used a
Free Agent, whose dead-money rate is 25% either way — it could not distinguish a bug
from correct behaviour. Re-run on a Long-Term player, it passed.

## Publishing

Push to `main`. Installed owners pick it up on their next update. A plugin installed or
updated **mid-session does not appear until a new session**, because skills resolve at
task start — start a new task rather than uninstalling and reinstalling.

**Verify a push by reading the file back from `raw.githubusercontent.com`, and read it
twice.** That CDN serves a stale copy for a few minutes, which on 6 Sep 2026 produced a
confident report that a landed change had not landed. A second fetch with a different
query string returns the new content.

`__pycache__/` and `*.pyc` do not belong here — check `git ls-files | grep pycache` and
add a `.gitignore` if any are tracked.
