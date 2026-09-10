# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this repository is

A **Claude plugin marketplace**, not an application. `.claude-plugin/marketplace.json`
lists two plugins under `plugins/`; people add this repo's URL in Claude and install
from it, so every commit here loads as instructions inside other owners' accounts.

The deliverable is almost entirely **prose**: thirteen `SKILL.md` files. The four Python
scripts are optional accelerators — each skill states what to do when its script is
absent, because an account-saved copy of a skill ships without `scripts/`. Keep that
fallback accurate whenever a script changes.

**Owner-facing setup lives in `SETUP.md`, and only there.** `README.md` points at
it and carries no steps of its own. The eleven people installing this are not
developers and will read exactly one page; two pages means one of them is stale
and it is always the one being read. Do not re-add install steps to `README.md`.

**This repo is the source of truth for skill text and scripts.** Copies saved to
anyone's Claude account are dead ends: no scripts, and they drift. Straker's own
account copies were deleted 6 Sep 2026. Edit here, never there.

There is no build and no dependency manifest. The test suite is `validation/`,
described in `validation/TEST-PLAN.md`; nothing under it ships. The runtimes are
`python3` for the four skill scripts and the tests, the `claude` CLI for the skill
evals, and `node` for `scripts/release.mjs`, which is the release tool, not part
of the deliverable.

Owners read the output in a chat window, mid-trade. Not developers. That shapes the
conventions below.

**All dates in this project are Pacific, and every timestamp carries its zone.**
This is the rule at the top of `START-HERE.md` and it applies here too. Evening work
otherwise reads a day ahead in the doc that describes it and a day behind in the
commit that lands it, which is how a correct set of dates got "corrected" once
already.

## Commands

```bash
git config core.hooksPath .githooks    # once per clone — all three hooks: commit gate and push gate
```

```bash
.githooks/pre-commit                   # run the staged-file gate by hand
```

```bash
python3 validation/regress.py          # the regression gate: before /code-review, every change
```

```bash
python3 validation/regress.py --evals  # required when anything under plugins/ changed; costs money
```

```bash
python3 validation/regress.py --post-push   # after the push: every eval, against what shipped
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

## Hard invariants (the git hooks enforce all seven)

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
5. **Every `SKILL.md` carries the connector footer verbatim, and opens with the
   canonical "Before you answer" block verbatim.** The texts are
   `.githooks/skill-footer.md` and `.githooks/skill-header.md` — copy them, don't
   retype them. Sections *after* the footer are fine (`league-schedule` adds one);
   paraphrase is not; the header allows one appended exception sentence
   (`league-contacts`, `league-schedule`). The hook checks the footer on commit,
   `audit.py` check 8 checks the header, and the pre-push gate runs the audit.
   `league-rules` shipped without the footer for a while and nothing noticed,
   because the rule was prose. The header exists because small models at low
   effort follow five lines at the top and ignore the same rule deep in the prose
   (measured 10 Sep 2026 PT).
6. **No phone numbers or email addresses in added lines, or in the commit message.**
   `get_league` returns both for all twelve owners; `league-contacts` reads them at
   run time and the repo stores none. This is the one invariant whose breach cannot
   be undone — the remote
   is public, so a number is published the moment it lands, and `git revert` does not
   unpublish it. The check covers ten-digit North American numbers in any of the
   formats owners actually typed into MFL, bare or separated by spaces, dots,
   hyphens or parentheses, plus standard email addresses.

   **Examples must use exempt values, and the exemption is by value, not by file.**
   Safe: the reserved fictional range — any area code, exchange `555`, line number
   `01XX` — and the `example.com`, `example.org`, `example.net` domains. Nothing else
   is safe, including in a comment. Describe the shape instead of writing one down.

7. **Every skill has an eval, and the gate passes before a push.** Each case under
   `validation/evals/` lists the skills it covers in a `skills:` line, and every
   `SKILL.md` must be named by at least one case tagged `gate`
   (`validation/audit.py`, check 7 — a new skill fails the audit until its eval
   exists). `.githooks/pre-push` runs `validation/regress.py --pre-push`: the free
   stages always, and the gate evals whenever `plugins/` differs from what the
   remote has — only the cases the runner's ledger does not already hold a pass
   for against the current files. **A push is refused when the gate fails or
   cannot run** — a CLI that is not logged in blocks the push, because a suite
   that never ran is not a suite that passed. `git push --no-verify` bypasses it;
   say so when you use it.

The commit hooks scan **added lines only** (and the message itself) — a rule that
re-flags existing content trains everyone to use `--no-verify`. The pre-push hook is
the exception, on purpose: it runs the whole gate, because the push is the release.

**Invariant 3 needs an interpreter** (it is section 4 in the hook). The JSON check
wants a working `python3`, `python` or `node`. When no candidate qualifies the check
is skipped rather than failed, so a machine without an interpreter can still commit,
but the hook prints a `note: ... was NOT checked`
line naming each unchecked file. If you see that note, the manifest was not verified.

## The two-plugin split

`dow-league` is for all twelve owners; `dow-league-lm` is the LM add-on and depends on
it (the LM skills lean on `league-rules`). The line is deliberate:

- **Anything that produces an artifact of record is LM-only.** Members *read* the
  schedule back from MFL via `league-matchups`; generation lives in the LM-only
  `league-schedule`. If members could generate schedules, twelve people would hold
  twelve plausible schedules, none of them the one MFL is playing.
- **Anything that posts to Discord is LM-only**, partly so nine extra copies of those
  descriptions don't fire on ordinary draft questions.

When adding a skill, decide which package it belongs to on that rule, mirror the
new skill in the owning plugin's `README.md` table, and **write at least one gate
eval case for it** under `validation/evals/<plugin>/` with the skill in its
`skills:` line — `validation/audit.py` fails until it exists, and the pre-push hook
runs the audit. Open the new skill with `.githooks/skill-header.md` and end it with
`.githooks/skill-footer.md`, both verbatim. `validation/evals/README.md` has the
case format and the synthetic league to write it against.

## How skills get their facts

Every fact comes from MyFantasyLeague (league `29557`) through a per-owner connector
that each person adds to their own account. The plugin carries no key and no data —
**without a key it is inert**, which is the intended security model, not a bug. The
gateway began *enforcing* that on 5 Sep 2026; the workers ran open before then, so
anything written earlier described the intent rather than the behaviour.

Common tools: `get_rosters`, `get_future_draft_picks`, `get_salary_adjustments`,
`get_standings`, `get_weekly_results`, `get_transactions`, `get_players`,
`get_matchups`, `get_league`, `get_assets`, `get_draft_results`.

Key consequences that shape the prose:

- A tool the owner's key cannot reach reports as `Unknown tool`, not a permission
  error — so "missing tool" means a key problem, not a broken skill.
- Every `SKILL.md` ends with the same **"If the league tools aren't there"** footer:
  the connector-setup instructions, the 401 case, and a ban on answering from memory
  or from examples in the file. Copy `.githooks/skill-footer.md` into any new skill —
  it is the canonical copy, and the hook checks staged skills against it.
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
| Contact details — phone, email, the member directory | `league-contacts` (read-only) |
| Scoring a proposed trade, market vs league-adjusted | `league-trade-evaluator` |
| What a player is worth here, and whether his contract is an asset or a drag | `league-player-values` |
| How a completed trade has aged, and who is ahead now | `league-trade-history` |
| Who to start this week, and what the opponent changes | `league-lineup` |

Duplicating a price table across skills is how the two skills drift apart. Cross-
reference instead, as they currently do.

## Conventions the skills share

- **Never surface internal identifiers in an answer** — franchise ids (`0001`), pick
  notation (`FP_0012_2027_4`), player ids (`15742`). Resolve them to names first. The
  one exception is the MFL schedule import block, which is machine input.
- **Never surface emails, phone numbers, or MFL usernames.** `get_league` carries all
  three for all twelve owners, and every member-facing skill calls it.
  `league-contacts` is the sole exception, and only when contact details are what was
  asked for.
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

**The gate, in order, for every change.** Free checks first, review second, the
model last — each step is cheaper than the one after it and catches what the next
one would otherwise pay to find. Straker set this order on 9 Sep 2026 PT.

1. `python3 validation/regress.py` — free: the seven invariants, the script
   tests, the lineup back-test, the eval lint. Seconds.
2. `/code-review` — before any eval run, including a rerun. A review finding
   fixed here is an eval failure that never has to be paid for.
3. `python3 validation/regress.py --evals` if anything under `plugins/` changed.
   The runner keeps a per-case ledger in `.git/` and **runs only cases that are
   new, failed, or stale** (their skill files, any skill's description, their
   case or mock files, or the grading code changed since the pass). Already-passed cases are not rerun: "we don't need to retest what we
   already tested." `--all` forces everything; `--post-push` always does.
   Every run covers `haiku`, `sonnet` and `opus` at low **and** high effort
   (`--models`, `--efforts`), because owners may be on any of them, and
   **every combination gates: a case passes only when it passes under all, a
   failure under one is a failure of the case, and the fix is verified under
   all** (a fix changes the fingerprint, so every entry reruns). Standing
   rules, both Straker's, 10 Sep 2026 PT.
4. **A failure means fix, review, rerun the failures.** Read the transcript in
   `validation/evals/results/`, decide whether the skill or the grader is
   wrong, fix that one thing, run `/code-review` on the fix, then
   `regress.py --evals` again — which by construction reruns only the cases the
   fix touched. A grader-only fix needs no model run at all:
   `run_headless.py --regrade <results dir>` rescores the saved transcript.
5. Push. The pre-push hook (invariant 7) runs the same ledger check, so a push
   straight after a green step 3 pays nothing.
6. `python3 validation/regress.py --post-push` — every case, forced, against
   what actually shipped.

The plan and the per-skill coverage are in `validation/TEST-PLAN.md`. The evals
are the only stage that reads the prose the way an owner's Claude does, so **a
prose-only edit to a `SKILL.md` is exactly what they exist for** — the code-review
skip list for docs-only changes does not apply to them. `regress.py` exits 3 when
`plugins/` has changed and the evals were not run; that is "incomplete", not
"passed".

**Cost.** `sonnet` under test and `sonnet` judging, Straker's call: 15 to 50
cents a case, so a full gate run is about six dollars and a rerun of two failures
under a dollar. Usage comes off the claude.ai Max plan (his preference; no API
key). Verified 9 Sep 2026 PT: two full gate runs plus a review left the weekly
window at 54% and the plan's usage credits at $0.00; the console credit balance
is not involved. The dollar figures are API-equivalent estimates, not charges. `haiku` under test was tried and rejected: it failed to invoke
a skill that `sonnet` invoked on the same prompt. The first full run happened
9 Sep 2026 PT (17 of 22; the five failures were two runner bugs, two over-strict
graders, and one real prose gap in `league-franchise-tags`). `claude plugin eval`
is still early access and closed for this account; `regress.py --official`
reports SKIP.

**Research first, then write.** Every number in a skill came from a live MFL call or a
back-test, not from memory.

The `league-lineup` back-test is committed and runnable at
`validation/lineup-backtest/` — scripts only; its fixtures are raw MFL payloads
and one of them carries every owner's phone and email, so `*.json` is blocked
there. The skill evals under `validation/evals/` run against a **synthetic**
league (owners Ada through Lior, reserved 555-01XX numbers, `example.com`); a real
name, number or payload never belongs there either. Only `plugins/` reaches an
installed owner, so nothing under `validation/` ships.

**Back-test against a decision that already happened.** A skill run on an open question
produces a plausible answer nobody can check. `league-contracts` was validated by
re-deriving all twelve 2025→2026 re-signings and matching price and term. That is the
only cheap way to catch confident-and-wrong.

**Design the test so one thing explains a failure.** The first IR cut-cost probe used a
Free Agent, whose dead-money rate is 25% either way — it could not distinguish a bug
from correct behaviour. Re-run on a Long-Term player, it passed.

## Branching

**The branching workflow is not defined here.** Branch naming, when to branch, what
to do with a dirty tree, and how a change lands are machine-wide defaults
(`~/.claude/project-defaults.md`). Restating them in this file only overrides them
with a staler copy — project instructions win on conflict, so a duplicate here wins
by accident rather than on merit.

What is specific to this repo is what a branch is protecting you from:

- **`main` is the publish channel.** A change to files under `plugins/<name>/` reaches
  every installed owner on the next marketplace sync (see Publishing below), so
  landing on `main` *is* the release. That makes the merge the deliberate act — not
  the commit, and not the push of a task branch.
- **There is no CI here**, and no second reviewer, so a PR on this repo runs no checks
  and gates nothing. Prefer the local merge the global defaults describe unless a PR
  is asked for.
- Work that never touches `plugins/` — this file, `README.md`, `scripts/release.mjs` —
  publishes nothing when it lands. Branch anyway; just don't treat the merge as a
  release.

## Publishing

**Committing IS publishing, measured 9 Sep 2026 PT.** An earlier version of this
section said the opposite — that `version` in `plugin.json` gates delivery and a
commit at an unchanged version reaches nobody. That was taken from the plugin docs
and never observed. It is wrong, and it was wrong in this file for one morning.

What was actually watched: the marketplace synced 62df110 → 03ae6e9; `dow-league`,
whose files changed in between, showed **updated "now"**; `dow-league-lm`, whose
files did not, stayed at 14h. A new claude.ai chat then loaded `league-lineup` —
a skill added in that range with **no version bump on either manifest**.

So delivery follows **file changes under `plugins/<name>/`**, on sync. Treat every
push to `main` as reaching everyone who has installed, immediately.

Two things follow. **A skill is live the moment it is pushed** — "committed
deliberately unreleased" is not a state this marketplace has, and `league-lineup`
was delivered while its work order still called it unreleased. And **deleting a
skill file and pushing removes it from installs**, which is the only lever for
pulling something back.

What `version` does instead is unmeasured. Do not write another claim about it
here without watching it.

```bash
node scripts/release.mjs                 # report: versions, and what is unreleased
```

```bash
node scripts/release.mjs 0.3.0 --commit  # bump both manifests and prepend a CHANGELOG entry
```

Run it with no version first: it lists every commit touching `plugins/` since the last
`v*` tag, which is the mechanical answer to "is a release pending?". It refuses a
re-release of the current version, a lower version and a non-semver string, and it
writes files only — the commit, the annotated `v<version>` tag and the push stay a
human act. What it cannot tell you is whether something is undelivered: pushing to
`main` already delivered it, tag or no tag.

Push to `main`. Installed owners pick it up on their next update. A plugin installed or
updated **mid-session does not appear until a new session**, because skills resolve at
task start — start a new task rather than uninstalling and reinstalling.

**Verify a push by reading the file back from `raw.githubusercontent.com`, and read it
twice.** That CDN serves a stale copy for a few minutes, which on 6 Sep 2026 produced a
confident report that a landed change had not landed. A second fetch with a different
query string returns the new content.

`__pycache__/` and `*.pyc` do not belong here — check `git ls-files | grep pycache` and
add a `.gitignore` if any are tracked.
