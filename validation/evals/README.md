# Skill evals

Thirty-one cases that exercise the thirteen skills end to end — prompt in,
tool calls out, answer graded — with no key, no network and no real league
data. Every skill is named in the `skills:` line of at least one case tagged
`gate`; `validation/audit.py` check 7 enforces that, so a new skill needs a
case before it can be pushed.
`validation/TEST-PLAN.md` says what each case asserts and why; this page is
the mechanics.

## Layout

```
mocks/dow/<tool>.md            the synthetic gateway, shared by every case
dow-league/<case>/             cases run with the member plugin loaded
dow-league-lm/<case>/          cases run with BOTH plugins loaded
  prompt.md                    front matter (name, tags, skills, max_turns) + the prompt
  graders/<name>.md            one grader each: regex | tool_used | tool_order | llm
  mocks/dow/<tool>.md          optional: overrides one tool for this case only
mock_mcp_server.py             an MCP server over stdio that serves the mocks
run_headless.py                loads the cases, drives `claude -p`, grades
results/                       transcripts and aggregate JSON; ignored by git
```

This is the layout `claude plugin eval` documents, so the same files serve
that command when it is enabled (`regress.py --official`).

## Running

```bash
python3 validation/evals/run_headless.py --selftest     # no model
```

```bash
python3 validation/evals/run_headless.py --tag gate     # the pre-push set
```

```bash
python3 validation/evals/run_headless.py --case 'rules-*' --runs 2 --verbose
```

```bash
python3 validation/evals/run_headless.py --ledger --tag gate  # what has passed against the current files
```

```bash
python3 validation/evals/run_headless.py --regrade 20260909-213359 --case picks-holdings  # rescore a saved transcript
```

`validation/regress.py --evals` covers each model in its `--models` (default
`haiku,sonnet,opus`) under each effort in `--efforts` (default `low,high`),
every combination gating except the `--report-models` (default `haiku`,
whose failures print as NOTE), by calling this runner once per combination; run
directly, this runner covers the one `--model` at the one `--effort` given. A run skips every case whose recorded pass is still valid: the skills it
covers, every skill's name and description, its own files, the mock files for
the tools its last run called, the mock server and the grading code all
unchanged, and the same model.
`--all` forces. The ledger lives in `.git/dow-evals-ledger.json`. A grader
change is settled with `--regrade` against the transcript already paid for;
only a skill or mock change needs the model again, and only for the cases
that cover it. Every transcript begins with a `dow-meta` line naming its
case, model and fingerprints.

Six shared graders run on every mocked case automatically -- no player ids,
franchise ids, pick codes, usernames, emails or phone numbers in the answer --
with the documented exceptions for `league-contacts` (contact details) and
`league-schedule` (the import block). See `IMPLICIT_GRADERS` in the runner.

Each run starts Claude Code headless in an empty temp directory with the
plugin loaded via `--plugin-dir` from the working tree, `--strict-mcp-config`
so the mock gateway is the only MCP server, and `WebFetch`, `WebSearch`,
`Write` and `Edit` disallowed. Cases tagged `no-connector` get no MCP server
at all. The `claude` CLI must be logged in; the runner exits 2 and says so
when it is not.

## The synthetic league

Twelve franchises `0001`–`0012`, owners **Ada, Bram, Cleo, Dev, Esme, Finn,
Gus, Hana, Ivo, Juno, Kit, Lior**. "I'm Ada" in a prompt means franchise
`0001`. Contact fields use only the reserved fictional range (`206 555-01XX`)
and `example.com`; usernames are `<name>_wh`. Cleo has no number on file. Dev's
email carries the trailing space the contacts skill warns about.

Ada's roster is built to trip the traps the skills document: a plain
Short-Term expiring (Marcus Hale, the dead end), a Long-Term expiring (Elliot
Brandt), a Long-Term on IR (Silas Orr, projected well enough to tempt a start),
a rookie on taxi (Rowan Pike), a rookie in year 2 (Cyrus Bell), a player with no
projection row (Harlan Voss), one projected exactly zero (Luca Ferro), and one
the value board cannot price (Wren Castillo). Bram holds Ada's 2028 1st; Ada
holds Cleo's 2027 3rd. Ada plays Bram in weeks 3 and 8 (a round-robin week and a rivalry week; the schedule is a legal 14-week build). Ada carries $16 of
dead money in two rows. One trade on 31 Jul 2026 at 19:08 PT (1 Aug UTC) --
Kai Mercer and Ada's 2028 1st for Ravi Dunn and a `DP_` pick, and the rosters
reflect it -- plus one one-sided trade from Cleo. Ten-digit epochs read as phone
numbers to the contact check, so every timestamp here is an epoch in the
reserved shape (digits 1XX 555 01XX).

Everything above is invented. Real player names, real owner names beyond the
first names already in the skills, real numbers, real payloads: none of it
belongs here, and the pre-commit hook and `audit.py` scan for the contact
shapes by value.

## Mock files

```
---
description: shown to the model as the tool's description
---
{"json": "returned verbatim as the tool result"}
```

`{{input.week}}` in a body is replaced with that argument from the call. A
tool with no file answers `Unknown tool`, as the real gateway does for a tool
the key cannot reach. Later directories override earlier ones file by file,
which is how a case replaces one tool of the shared set.

## Graders

```
---
type: regex
pattern: '\b[FD]P_\d'
match: not_contains          # contains | not_contains | count:N
flags: i                     # optional
---
```

```
---
type: tool_used
tool: get_projections        # bare name matches any server prefix
input_match: '"week":\s*"?3' # optional regex over the JSON input
min: 1
max: 3                       # optional; min 0 max 0 = must not be called
---
```

```
---
type: llm
criteria: "One criterion, stated as what a passing answer does."
---
Optional rubric body for the judge.
```

Every grader must be seen failing before it is trusted; `--selftest` does that
for each type on a canned transcript, and a new grader shape needs a new
control there.
