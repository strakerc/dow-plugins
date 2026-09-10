# Test plan — the regression gate for every skill

Written 9 Sep 2026 PT. Runs before `/code-review` on every change, and again
after every push, because here **pushing to `main` is the deployment**: the
marketplace delivers any changed file under `plugins/` to every installed
owner on their next sync, with no version bump and no undo short of deleting
the file.

One command, two modes:

```bash
python3 validation/regress.py               # free: seconds, no model
```

```bash
python3 validation/regress.py --evals       # + the skill evals, gate set
```

```bash
python3 validation/regress.py --post-push   # after the push: everything, against what shipped
```

The order of a change is: edit → `regress.py` (free) → `/code-review` →
`regress.py --evals` if anything under `plugins/` changed → for each failure,
fix one thing, review the fix, `--evals` again (only the affected cases rerun)
→ push → `--post-push`. Review comes before the model on purpose: it is
cheaper, and a finding fixed there is an eval failure never paid for.
`regress.py` exits 3 and says so when `plugins/` has changed and the evals
were not run, so "the gate passed" cannot be said about a run that never
asked the model anything.

**Nothing is retested that already passed.** The runner keeps a ledger in
`.git/dow-evals-ledger.json` with, per case, the last result, the model, and
two fingerprints: the skill directories the case covers plus every skill's
name and description (the routing surface, since a description edit elsewhere
can change which skill fires), and the case's own files, the mock files for the tools its last run
actually called (none for a no-connector case), the mock server and the
grading functions' source. A case is rerun only when it is new, failed, or one of those changed.
Each transcript starts with a metadata line naming its case, model and
fingerprints, which is what a regrade trusts. `--all` forces a case; `--post-push` forces everything;
`run_headless.py --ledger` shows the state. A grader-only correction does not
need the model at all: `run_headless.py --regrade <results dir>` rescores the
saved transcript and updates the ledger.

**The push is blocked when the gate fails.** `.githooks/pre-push` (installed
by the same `core.hooksPath` command as the other hooks) runs
`regress.py --pre-push` once per distinct commit being pushed: the free
stages always, and the gate evals when `plugins/` differs from what the
remote already has — through the same ledger, so a push straight after a
green `--evals` run costs nothing. A CLI that is not logged in blocks the
push as well: a suite that could not run is not a suite that passed.

**Every skill must have an eval.** Each case's `prompt.md` carries a
`skills:` line naming the skills it covers, and `audit.py` check 7 fails
whenever a `SKILL.md` on disk is not named by at least one case tagged `gate`.
A new skill therefore cannot be pushed without one.

## What can go wrong, and which stage catches it

The deliverable is prose that loads inside other people's Claude accounts,
plus four scripts that owners may or may not have. Four things break:

| Failure | Example that has actually happened | Stage |
|---|---|---|
| An invariant | a `$5` token rewritten into a word at load time; `league-rules` shipping without the connector footer; a broken manifest | **static** |
| Script arithmetic | `contractStatus` read as a length; "Short-Term Ext." read as a plain short-term (found by this plan, 9 Sep 2026 PT) | **scripts** |
| The lineup chooser | a lineup that is not legal, or not optimal | **backtest** |
| The prose itself | a skill that answers from memory when the connector is missing; a percentage quoted that the skill says never to quote; a phone number surfacing from a picks question | **evals** |

The first three are deterministic and free. The fourth needs a model in the
loop, costs money, and is the only one that tests what an owner actually
experiences.

## Stage 1 — static (free)

`validation/audit.py`: the seven invariants over the whole tracked tree — the
canonical footer in every `SKILL.md`, no `$` + single digit, every `*.json`
parses, no contact data anywhere, no build droppings, stated counts match
reality, every skill named by a `gate` eval case, and every skill opening with
the canonical "Before you answer" block. Every check carries a control that
must fail.

`claude plugin validate` on the marketplace manifest and both plugin
manifests.

## Stage 2 — scripts (free)

`validation/script_tests.py`: 29 unit tests, synthetic fixtures built in code,
each named for the promise in the skill text it pins.

| Script | Pinned |
|---|---|
| `contract_options.py` | years remaining from `contractStatus`; decision due only in the final year; IR at 25% cap / 100% cut on a **Long-Term** player; rookie year-1 free cut; 25% on FA and rookie year 2; the +5 / +10 ladder; the short-term dead end; the rules worked example (10 → 15 → 25 then 30); the tag menu under both MFL spellings; both extension spellings return to the normal menu; rookie extension bumps by round; cap space net of adjustments and the loud reminder without them; taxi at 100%; the franchise filter |
| `pick_ledger.py` | 144 reconciles; a missing and a duplicated pick each flip the integrity line; an acquired pick is listed under the holder, attributed to the origin, and marked gone for the origin; slot projection is reverse standings with PF as tiebreak; the three-year window; the conditional reminder |
| `compute_tiers.py` | Tier 1 by playoff finish even for the lowest scorer; Tiers 2/3 on `pf` minus weeks 15+; refuses fewer than four distinct finalists; the tight-margin warning |
| `build_schedule.py` | eight checks pass and the block has 84 rows with 7 home games each; a seed reproduces the schedule; a rematch outside Tier 1 is refused; comparing against itself reads all-zero and says why; a truncated comparison is refused; no `prior_pf` skips the report |

## Stage 3 — backtest (free, needs local fixtures)

`validation/lineup-backtest/`: 36 real 2025 lineups through the stated
method with perfect foresight, the hard gates asserted, then a million random
lineups per franchise that must not beat the enumeration and five mutations
that must each be refused. The fixtures are raw MFL payloads and one of them
carries every owner's phone and email, so they are never committed; the stage
reports **SKIP** loudly when they are absent.

## Stage 4 — evals-lint (free)

`run_headless.py --selftest`: every case and mock loads, every grader type is
seen passing and failing on a canned transcript, every regex compiles, every
skill named in a grader exists, the mock gateway answers a real MCP handshake
and reports `Unknown tool` the way the real one does.

## Stage 5 — the skill evals (costs money)

Thirty-one cases under `validation/evals/`, in the layout `claude plugin eval`
documents: `<case>/prompt.md`, `<case>/graders/*.md`, `mocks/dow/<tool>.md`.
They are run today by `validation/evals/run_headless.py`, which drives
`claude -p` with the plugin loaded from the working tree and a synthetic
gateway as the only MCP server. See `validation/evals/README.md` for the
mechanics and the synthetic league.

**Gate set** (`--evals`, 22 cases, tagged `gate`): at least one behavioural
case for every skill, the footer, and every case where a wrong answer costs
the league something. This is what the pre-push hook runs.
**Full set** (`--full`, all 31): everything below.
**The matrix: models × efforts.** Every run, including the push hook's,
covers the models in `--models` (default `haiku,sonnet,opus`) under every
effort in `--efforts` (default `low,high`), one ledger entry per case per
combination. **Every combination gates.** A case passes only when it passes
under all of them; a failure under one is a failure of the case, and the fix
is verified under all, because a fix changes the case's fingerprint and makes
every entry stale. Those are Straker's standing rules (10 Sep 2026 PT):
"treat a failure in a single model as a failure in all" and "the matrix just
needs to test low and high, always, not one or the other." Effort is a real
variable: the same prose passed 22/22 on Sonnet at default effort and 17/22
at low. Medium is not run: low and high bracket it. `claude-fable-5-1` joins
the models when the weekly window allows. `--models ''` and `--efforts ''`
run `--model` at `--effort` alone.
The ledger also records the exact model id behind each alias; a run resolves
each alias with one tiny call first, so when `sonnet` starts pointing at a
newer model the old passes read as stale and rerun.

### Coverage by skill

| Skill | Cases | What is asserted |
|---|---|---|
| all thirteen (the footer) | `no-connector-roster` ⚑, `no-connector-picks` ⚑, `no-connector-contracts` | With no MCP server at all: names the connector, gives the fix, invents nothing |
| `league-rules` | `rules-dead-money` ⚑, `rules-rookie-scale` ⚑, `rules-short-term-price` ⚑ (the dollar-digit canary), `rules-cap-ir` ⚑, `rules-tag-consecutive`, `rules-ir-exempt`, `rules-shortened-season` | The digest's numbers survive loading; the undefined 1–5 game band is called undefined |
| `league-contracts` | `contracts-expiring` ⚑ | Expiring players named, the short-term dead end shown, release free, no ids |
| `league-draft-picks` | `picks-holdings` ⚑ | Origin named for an acquired pick, no `FP_` codes, the conditional raised |
| `league-franchise-tags` | `tags-price-brandt` ⚑ | The positional floor binds (24 over a personal 23), the binding branch is named and flagged as unusual, the five contracts behind the average are shown with owners, eligibility confirmed |
| `league-contacts` | `contacts-no-leak` ⚑, `contacts-number` ⚑, `contacts-none` | A picks question prints no phone/email/username; a number question prints one normalised number and nothing else; no number means say so |
| `league-matchups` | `matchups-lookup`, `matchups-no-schedule` ⚑ | Read from MFL; an empty season means "nothing loaded", no generation, no Bash |
| `league-trade-evaluator` | `trade-no-percentage` ⚑, `trade-executed` | The league-adjusted percentage never appears; legality is a hard stop; a completed trade is refused and the refusal explained |
| `league-lineup` | `lineup-two-tables` ⚑, `lineup-no-write` ⚑, `trigger-lineup-not-values` | Projections called with the week; scores not used; two labelled lineups; IR and taxi never started; no projection named by name; lock time in Pacific; nothing submitted |
| `league-player-values` | `values-unpriced` ⚑ | A missing price is reported as missing, never as low |
| `league-trade-history` | `history-timestamps` ⚑ | Pacific dates with the zone; no codes; no winner declared off a few weeks; a one-sided trade flagged |
| `league-schedule` | `schedule-2026-done` ⚑, `schedule-tier-rule` ⚑, `schedule-no-mfl-write` ⚑ | 2026 is settled; tiers by playoff finish and regular-season points; never writes to MFL |
| `rookie-draft-grades` | `rookie-grades-review-gate` ⚑ | `send_message` is never called; nothing claims to have posted |
| `fa-auction-grades` | `fa-grades-review-gate` ⚑ | same |
| routing | `lm-matchups-not-schedule`, `contacts-no-leak`, `trigger-lineup-not-values` | The right skill fires and the wrong one does not |

⚑ = gate set. The franchise-tag case prices from the synthetic salaries, not
the real 2024–2026 ones; the skill's own "Verification" section remains the
back-test against real history, by hand.

### Graders

**Shared graders run on every mocked case** without being written into it:
no player ids, no franchise ids, no pick codes, no MFL usernames, no email
addresses, no phone numbers. Nine skills state that rule in their own words
and four do not, so the runner tests the behaviour for all of them. The two
documented exceptions are honoured: a case covering `league-contacts` may
print the contact detail asked for, and one covering `league-schedule` may
print franchise ids in the MFL import block.

Free graders do the high-stakes work: `regex` (`contains`, `not_contains`,
`count:N`) for identifiers, phone shapes, forbidden percentages and required
numbers; `tool_used` with `min`/`max` and an `input_match` regex for "called
projections with a week", "never called `send_message`", "the contacts skill
did not fire". `llm` graders (a second Sonnet call, answered as JSON) judge
only what a regex cannot: that two lineups are separately labelled, that a refusal was
explained. A case passes when every grader passes on every run.

## Cost and time

Free stages: about 10 seconds, or 3 minutes with the back-test's adversarial
run. Evals: `sonnet` under test and `sonnet` judging. Measured 9 Sep 2026 PT
with a `haiku` judge at 10 to 40 cents and 10 to 130 seconds a case, so the
22-case gate set was about four dollars in fifteen minutes; a `sonnet` judge
adds roughly two dollars to that and was chosen because the `haiku` judge
returned no verdict on three answers. Usage comes off the claude.ai Max plan the CLI is logged in with -- Straker's
preference, and no API key is involved. Verified 9 Sep 2026 PT against the
claude.ai usage page: two full gate runs and a review left the weekly window at
54% with the plan's usage credits at $0.00, and the console credit balance was
not touched. The dollar figures here are the runner's API-equivalent estimates,
useful for comparing cases, not charges. `haiku` under
test was tried the same day: 6 cents a case, and it failed to invoke a skill
that `sonnet` invoked on the same prompt, which reads as a skill regression
that is not one. Owners use the stronger model, so the cheaper one is not a
valid proxy. `--runs 2` doubles the cost and is worth it when a case looks
flaky. Every run has a per-run budget ceiling (`--max-budget`, default one
dollar).

## What is unverified as of 9 Sep 2026 PT — read before trusting a green

1. **No eval case has been run through a model yet.** The `claude` CLI on
   this machine is not logged in (`claude auth status` → `loggedIn: false`);
   the desktop app authenticates its own sessions through a channel the CLI
   does not share. Log in once from a real terminal:

   ```bash
   claude auth login
   ```

   The runner detects the not-logged-in reply and exits 2, and `regress.py`
   reports the evals as FAIL rather than skipped. Until the first real run,
   expect grader calibration: a strict regex or an over-specific rubric will
   fail a correct answer. Read the transcript in `validation/evals/results/`,
   and change the grader, not the skill, unless the skill is actually wrong.
2. **`claude plugin eval` is early access and not enabled for this
   account.** The cases use its layout so `regress.py --official` can hand
   them over unchanged, but that path has never been watched succeeding, and
   whether its mock framework serves a plugin that declares no MCP server of
   its own is unknown. It reports SKIP with the reason when the gate is closed.
3. **The headless environment is not claude.ai.** Owners use the plugin in a
   chat client with the connector attached; the evals use Claude Code with a
   mock server named `dow`. Tool names differ in prefix (graders match the
   bare name), the global `~/.claude/CLAUDE.md` loads into every run, and
   permission handling is the CLI's. A pass here is strong evidence, not proof,
   that the same prose behaves in a chat.

## Adding a case, and the rule for a new skill

Copy a neighbouring case directory. The prompt is the whole conversation;
say "I'm Ada" when the answer depends on whose team it is. List the skills
the case covers in `skills:`. Prefer a regex or `tool_used` grader wherever
one can express the rule; give an `llm` grader one criterion, not a
checklist. Tag it `gate` if it is the skill's one required case or a wrong
answer costs the league something; `full` otherwise. Never put a real name,
number, address or payload anywhere under `validation/evals/`; the synthetic
league is in `validation/evals/README.md`. `run_headless.py --selftest` must
stay clean.

**A new skill ships with at least one `gate` case that names it.** Check 7 of
`audit.py` fails until it exists, and the pre-push hook runs the audit, so the
skill cannot reach an owner untested. Write the case against the traps the
skill's own text documents — that is where the last three skills' bugs were.
