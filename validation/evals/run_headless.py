#!/usr/bin/env python3
"""Run the skill evals through headless Claude Code, and grade the transcripts.

    python3 validation/evals/run_headless.py --selftest          # no model, seconds
    python3 validation/evals/run_headless.py --tag gate           # the pre-push set
    python3 validation/evals/run_headless.py                      # everything
    python3 validation/evals/run_headless.py --case 'rules-*' --runs 2

WHY THIS FILE EXISTS

`claude plugin eval` is the tool this suite is written for, and the case files
under this directory use its layout: <case>/prompt.md, <case>/graders/*.md,
mocks/<server>/<tool>.md. On 9 Sep 2026 PT that command was early access and
switched off for this account, so nothing here could be run through it. This
runner reads the same files and drives `claude -p` directly instead, with the
plugin loaded from the working tree and a mock gateway as the only MCP server.
When the official command opens up, `validation/regress.py --official` hands it
the same cases; this file is the bridge, not a competing format.

WHAT A RUN IS

For each case: start Claude headless in an empty temp directory, with
`--plugin-dir` pointing at a copy of the plugin(s) inside that directory, `--strict-mcp-config`
so the only tool server is validation/evals/mock_mcp_server.py, WebFetch and
WebSearch disallowed (file writes are allowed: they land in the empty temp
directory, and a skill script needs a saved payload), every tool listed from
the first turn (ENABLE_TOOL_SEARCH=false: claude.ai does not defer a
connector's tools, and a deferred list confused haiku), and the case prompt as
the whole conversation. Cases
tagged `no-connector` get no MCP server at all, which is how the "connector is
not set up" behaviour is exercised. The stream-json transcript is saved, then
every grader in the case scores it.

GRADERS (frontmatter `type:`), the ones plugin eval documents that matter here:

    regex       pattern, flags, match: contains | not_contains | count:N
    tool_used   tool, input_match (regex over the JSON input), min, max
    tool_order  before, after
    llm         criteria in the frontmatter, rubric in the body; judged by a
                second headless call (Sonnet by default), answered as JSON

Tool names match on the bare name too: `get_projections` matches
`mcp__dow__get_projections` here and `mcp__plugin_dow-league_dow__...` there.

A case passes a run when every grader passes; a case passes when every run
passes. Exit 1 on any failure, 2 if the model could not be reached at all --
a suite that cannot run must not look like a suite that passed.

REAL DATA NEVER ENTERS. The mock gateway serves synthetic files, the run
directory is empty, and the transcripts land in results/, which is ignored by
git. Do not point --mcp-config at the real connector from here.
"""
import argparse, fnmatch, hashlib, json, os, re, shutil, subprocess, sys, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PLUGINS = ROOT / "plugins"
SERVER = "dow"
SUITES = {"dow-league": ["dow-league"],
          "dow-league-lm": ["dow-league", "dow-league-lm"]}
KNOWN_GRADERS = {"regex", "tool_used", "tool_order", "llm"}
# Nothing that reaches outward: no web, no sub-agents, and none of the desktop
# app's publishing tools -- haiku called Artifact from a schedule case and got
# as far as the "publish to claude.ai" prompt (10 Sep 2026 PT). File writes
# are fine: they land in the empty temp cwd.
DISALLOWED = ["WebFetch", "WebSearch", "NotebookEdit", "Agent", "Artifact", "SendUserFile",
              "Workflow", "PushNotification"]

# --------------------------------------------------------------- loading
sys.path.insert(0, str(HERE))
from mock_mcp_server import frontmatter, load_tools, parse_mock  # the one parser


class JudgeUnreachable(Exception):
    """The judge model could not be reached. Not a grader verdict: the run
    must end on the unreachable path, never as an ordinary FAIL."""


# The CLI's own short replies when no model was reached. Deliberately narrow:
# a real answer about a 401 says "authentication" and must be graded.
LOGIN_RE = re.compile(r"not logged in|please run /login|invalid api key", re.I)


def load_cases(only_suite=None):
    cases = []
    for suite, plugins in SUITES.items():
        if only_suite and suite != only_suite:
            continue
        sdir = HERE / suite
        if not sdir.is_dir():
            continue
        for cdir in sorted(p for p in sdir.iterdir() if p.is_dir()):
            pm = cdir / "prompt.md"
            if not pm.is_file():
                continue
            meta, body = frontmatter(pm.read_text(encoding="utf-8"))
            graders = []
            for g in sorted((cdir / "graders").glob("*.md")):
                gm, gb = frontmatter(g.read_text(encoding="utf-8"))
                gm["_name"], gm["_body"] = g.stem, gb.strip()
                graders.append(gm)
            tags = meta.get("tags") or []
            skills_covered = meta.get("skills")
            if not isinstance(tags, list):
                tags = ["<unparsed>"]           # frontmatter() left a string: surfaced by selftest
            if skills_covered is not None and not isinstance(skills_covered, list):
                skills_covered = ["<unparsed>"]
            cases.append({
                "suite": suite, "plugins": plugins, "dir": cdir,
                "name": f"{suite}/{cdir.name}", "title": meta.get("name", cdir.name),
                "tags": tags, "skills": skills_covered,
                "prompt": body.strip(), "graders": graders,
                "max_turns": int(meta.get("max_turns", 12)),
                "runs": int(meta.get("runs", 1)),
                "model": meta.get("model"),
                "mocks": "no-connector" not in tags,
            })
    return cases


# --------------------------------------------------------------- transcript
def parse_stream(lines):
    """stream-json -> {"tools": [(name, input)], "last": str, "cost": float, ...}"""
    tools, texts, result, model_id = [], [], {}, None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            m = json.loads(line)
        except Exception:
            continue
        if m.get("type") == "system" and m.get("subtype") == "init" and m.get("model"):
            model_id = m["model"]           # the alias resolved, e.g. claude-sonnet-5
        if m.get("type") == "assistant":
            for b in (m.get("message") or {}).get("content") or []:
                if b.get("type") == "tool_use":
                    tools.append((b.get("name", ""), b.get("input") or {}))
                elif b.get("type") == "text":
                    texts.append(b.get("text", ""))
        elif m.get("type") == "result":
            result = m
    last = result.get("result") if isinstance(result.get("result"), str) else ""
    if not last and texts:
        last = texts[-1]
    return {"tools": tools, "last": last or "", "all_text": "\n".join(texts), "model_id": model_id,
            "cost": float(result.get("total_cost_usd") or 0),
            "turns": result.get("num_turns"), "subtype": result.get("subtype"),
            "is_error": bool(result.get("is_error")), "raw_result": result}


def tool_matches(want, name):
    if not want:
        return False
    if name == want:
        return True
    bare = name.rsplit("__", 1)[-1]
    if bare == want:
        return True
    if want.endswith("*"):
        return name.startswith(want[:-1]) or bare.startswith(want[:-1])
    return False


# --------------------------------------------------------------- graders
def grade_regex(g, t):
    flags = re.I if "i" in str(g.get("flags", "")) else 0
    flags |= re.S if "s" in str(g.get("flags", "")) else 0
    target = t["all_text"] if g.get("target") == "all_text" else t["last"]
    pat = re.compile(str(g["pattern"]), flags)
    hits = pat.findall(target)
    mode = str(g.get("match", "contains"))
    if mode == "contains":
        ok = bool(hits)
    elif mode == "not_contains":
        ok = not hits
    elif mode.startswith("count:"):
        ok = len(hits) == int(mode.split(":", 1)[1])
    else:
        raise ValueError(f"unknown match mode {mode!r}")
    ev = f"{len(hits)} match(es) for /{g['pattern']}/ ({mode})"
    if hits and mode == "not_contains":
        ev += ": " + ", ".join(repr(h if isinstance(h, str) else h[0])[:40] for h in hits[:3])
    return ok, ev


def grade_tool_used(g, t):
    im = re.compile(str(g["input_match"]), re.S) if g.get("input_match") else None
    n = 0
    for name, inp in t["tools"]:
        if tool_matches(str(g["tool"]), name):
            if im is None or im.search(json.dumps(inp)):
                n += 1
    lo, hi = int(g.get("min", 1)), g.get("max")
    ok = n >= lo and (hi is None or n <= int(hi))
    return ok, f"{g['tool']} called {n}x (want {lo}..{hi if hi is not None else 'inf'})"


def grade_tool_order(g, t):
    names = [n for n, _ in t["tools"]]
    first = next((i for i, n in enumerate(names) if tool_matches(str(g["before"]), n)), None)
    last = next((i for i, n in enumerate(names) if tool_matches(str(g["after"]), n)), None)
    ok = first is not None and last is not None and first < last
    return ok, f"{g['before']} at {first}, {g['after']} at {last}"


JUDGE_SCHEMA = {"type": "object", "required": ["pass", "reason"],
                "properties": {"pass": {"type": "boolean"}, "reason": {"type": "string"}},
                "additionalProperties": False}


def grade_llm(g, t, judge_model, claude):
    rubric = g.get("_body") or ""
    prompt = (
        "You are grading one answer produced by a fantasy-football league assistant. "
        "Judge ONLY the criteria below; do not reward or penalise anything else. "
        "Answer with a JSON object {\"pass\": true|false, \"reason\": \"...\"} and nothing else.\n\n"
        f"CRITERIA: {g.get('criteria', '')}\n\n"
        + (f"RUBRIC:\n{rubric}\n\n" if rubric else "")
        + "ANSWER UNDER TEST:\n<<<\n" + t["last"][:12000] + "\n>>>\n"
    )
    # --max-turns 3, not 1: with a single turn the judge sometimes ends it
    # without the structured answer (subtype error_max_turns, result None) and
    # the case fails with "judge gave no verdict" -- seen three times on the
    # first gate run, 9 Sep 2026 PT. No tools are available, so extra turns
    # cost nothing unless the model needs them.
    cmd = [claude, "-p", "--model", judge_model, "--output-format", "json",
           "--json-schema", json.dumps(JUDGE_SCHEMA), "--strict-mcp-config",
           "--tools", "", "--max-turns", "3", "--no-session-persistence"]
    verdict, evidence = None, ""
    # Two attempts. A verdict is taken from the structured output, else from
    # JSON in the result text, else from a bare `"pass": true|false` in it.
    # Unreachability is decided from the envelope (exit code, empty output, a
    # short login/auth reply) -- never from a regex over the judge's prose,
    # which legitimately mentions authentication when grading footer answers.
    for _ in range(2):
        try:
            p = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                               encoding="utf-8", timeout=180)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise JudgeUnreachable(f"judge could not run: {e}")
        out, result_text = {}, ""
        try:
            out = json.loads(p.stdout)
            verdict = out.get("structured_output")
            result_text = out.get("result") or ""
        except Exception:
            result_text = p.stdout or ""
        if not isinstance(verdict, dict) or "pass" not in verdict:
            verdict = None
            try:
                verdict = json.loads(result_text)
            except Exception:
                m = re.search(r'"pass"\s*:\s*(true|false)', result_text, re.I)
                if m:
                    r = re.search(r'"reason"\s*:\s*"((?:[^"\\]|\\.)*)"', result_text, re.S)
                    verdict = {"pass": m.group(1).lower() == "true",
                               "reason": (r.group(1) if r else result_text.strip())[:300]}
        if isinstance(verdict, dict) and "pass" in verdict:
            break
        evidence = f"subtype={out.get('subtype')} rc={p.returncode} result={result_text.strip()[:160]!r}"
        if (p.returncode != 0 and not p.stdout) or \
           (not out.get("structured_output") and len(result_text) < 300 and LOGIN_RE.search(result_text)):
            raise JudgeUnreachable(evidence)
    if not isinstance(verdict, dict) or "pass" not in verdict:
        return False, f"judge gave no verdict twice: {evidence}"
    return bool(verdict["pass"]), str(verdict.get("reason", ""))[:300]


# Conventions every skill shares (CLAUDE.md, "Conventions the skills share"):
# no internal identifiers, no contact data, in any answer. Nine of the thirteen
# skills say so in their own words and four say nothing, so the rule is tested
# here for every mocked case rather than trusted to each skill's prose. A case
# may still carry its own copy; that is harmless. Exemptions are the documented
# ones: league-contacts hands over the contact detail asked for, and the MFL
# import block from league-schedule is franchise ids by design.
IMPLICIT_GRADERS = [
    {"_name": "shared:no-player-ids", "type": "regex", "pattern": r"\b[1-5]000\d\b", "match": "not_contains"},
    {"_name": "shared:no-franchise-ids", "type": "regex", "pattern": r"\b00(0[1-9]|1[0-2])\b",
     "match": "not_contains", "_unless": {"league-schedule"}},
    {"_name": "shared:no-pick-codes", "type": "regex", "pattern": r"\b[FD]P_\d", "match": "not_contains"},
    {"_name": "shared:no-username", "type": "regex", "pattern": r"\b[a-z]+_wh\b", "match": "not_contains"},
    {"_name": "shared:no-email", "type": "regex", "pattern": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
     "match": "not_contains", "_unless": {"league-contacts"}},
    {"_name": "shared:no-phone", "type": "regex", "pattern": r"\(?\d{3}\)?[\s.-]?555[\s.-]?01\d\d",
     "match": "not_contains", "_unless": {"league-contacts"}},
]


def graders_for(case):
    """The case's own graders plus the shared ones that apply to it."""
    out = list(case["graders"])
    if not case["mocks"]:
        return out                     # no data was ever shown, nothing to leak
    covered = set(case["skills"] or [])
    for g in IMPLICIT_GRADERS:
        if not (g.get("_unless", set()) & covered):
            out.append(dict(g, _body=""))
    return out


def grade(case, t, judge_model, claude):
    out = []
    for g in graders_for(case):
        kind = g.get("type")
        try:
            if kind == "regex":
                ok, ev = grade_regex(g, t)
            elif kind == "tool_used":
                ok, ev = grade_tool_used(g, t)
            elif kind == "tool_order":
                ok, ev = grade_tool_order(g, t)
            elif kind == "llm":
                ok, ev = grade_llm(g, t, judge_model, claude)
            else:
                ok, ev = False, f"unknown grader type {kind!r}"
        except JudgeUnreachable:
            raise
        except Exception as e:  # a grader that crashes is a failed grader
            ok, ev = False, f"grader error: {e}"
        out.append({"name": g["_name"], "type": kind, "passed": ok, "evidence": ev})
    return out


def print_result(mark, name, detail, gs, verbose):
    print(f"  {mark:<7} {name}  {detail}")
    for g in gs:
        if not g["passed"] or verbose:
            print(f"          {'ok ' if g['passed'] else 'BAD'} {g['name']} [{g['type']}] {g['evidence']}")


# --------------------------------------------------------------- running
def find_claude():
    c = shutil.which("claude")
    if not c:
        for cand in (Path.home() / ".local" / "bin" / "claude.exe",
                     Path.home() / ".local" / "bin" / "claude"):
            if cand.exists():
                return str(cand)
    return c


def mcp_config(case, tmp):
    dirs = [str(HERE / "mocks")]
    if (case["dir"] / "mocks").is_dir():
        dirs.append(str(case["dir"] / "mocks"))
    cfg = {"mcpServers": {SERVER: {
        "command": sys.executable,
        "args": [str(HERE / "mock_mcp_server.py"), "--server", SERVER, "--mocks", *dirs]}}}
    p = Path(tmp) / "mcp.json"
    p.write_text(json.dumps(cfg), encoding="utf-8")
    return str(p)


def run_case_once(case, args, claude, results_dir, run_no):
    tmp = tempfile.mkdtemp(prefix="dow-eval-")
    model = case["model"] or args.model
    cmd = [claude, "-p", "--output-format", "stream-json", "--verbose",
           "--max-turns", str(case["max_turns"]), "--no-session-persistence",
           "--model", model, "--disallowedTools", *DISALLOWED]
    if args.effort:
        cmd += ["--effort", args.effort]
    # The plugin is loaded from a COPY inside the temp directory, never from
    # the repo: file writes are allowed, a skill may tell the model to run a
    # script next to itself, and a payload written into plugins/ would dirty
    # the tree and move the fingerprints mid-run (review finding, 10 Sep 2026
    # PT). The copy is a few dozen small files.
    copy_error = None
    for pl in case["plugins"]:
        dst = Path(tmp) / "plugins" / pl
        try:
            shutil.copytree(PLUGINS / pl, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        except (OSError, shutil.Error) as e:
            copy_error = f"could not copy plugin {pl}: {e}"      # nothing ran; the suite stops
            break
        cmd += ["--plugin-dir", str(dst)]
    allowed = ["Skill", "Read", "Write", "Edit", "Glob", "Grep", "Bash(python3 *)", "Bash(python *)",
               "Bash(ls *)", "Bash(cat *)"]
    if case["mocks"]:
        cmd += ["--mcp-config", mcp_config(case, tmp), "--strict-mcp-config"]
        allowed.append(f"mcp__{SERVER}__*")
    else:
        cmd += ["--strict-mcp-config"]
    cmd += ["--allowedTools", *allowed]
    if args.max_budget:
        cmd += ["--max-budget-usd", str(args.max_budget)]
    # The transcript says what produced it: which case, which model, the
    # skills fingerprint the model saw and the tools it called. A regrade
    # reads these back instead of guessing from the file name or trusting the
    # operator. Written after the run, once the tool list is known.
    meta = {"type": "dow-meta", "case": case["name"], "model": model, "effort": args.effort,
            "skills_fp": skills_fp(case), "when": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    t0 = time.time()
    timed_out = False
    try:
        if copy_error:
            raise PluginCopyError(copy_error)
        # claude.ai lists a connector's tools directly. The CLI defers MCP
        # tools behind ToolSearch by default, and haiku at low effort then
        # "loaded" them and reported the connector down, or reached for
        # PowerShell (six transcripts, 10 Sep 2026 PT). `false` is the CLI's
        # standard mode: every tool in the prompt from the first turn.
        env = dict(os.environ, ENABLE_TOOL_SEARCH="false")
        p = subprocess.run(cmd, input=case["prompt"], capture_output=True, text=True,
                           encoding="utf-8", cwd=tmp, timeout=args.timeout, env=env)
        lines, stderr, rc = p.stdout.splitlines(), p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        lines, stderr, rc = (e.stdout or "").splitlines(), f"TIMEOUT after {args.timeout}s", -1
        timed_out = True
    except PluginCopyError as e:
        # The plugin never reached the temp dir: nothing ran, and the suite
        # stops (every case needs the copy), with the OS error as the reason.
        lines, stderr, rc = [], str(e), 126
    except OSError as e:
        # An npm `claude.cmd` shim, or no claude at all: nothing ran.
        lines, stderr, rc = [], f"could not start {cmd[0]}: {e}", 127
    shutil.rmtree(tmp, ignore_errors=True)
    t = parse_stream(lines)
    meta["tools"], meta["model_id"] = bare_tools(t["tools"]), t["model_id"]
    slug = case["name"].replace("/", "__")
    (results_dir / f"{slug}.run{run_no}.jsonl").write_text(
        json.dumps(meta) + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    t["seconds"] = round(time.time() - t0, 1)
    t["rc"], t["stderr"], t["timed_out"], t["model"] = rc, stderr[-2000:], timed_out, model
    return t


class PluginCopyError(Exception):
    """The plugin could not be copied into the run's temp directory."""


def unreachable(t):
    """True when the model was never reached: a launcher that could not start,
    a plugin that could not be copied, a run that produced nothing, or the
    CLI's short "not logged in" reply.
    Decided from the envelope, not from words in a real answer -- a correct
    footer answer says "authentication" and must be graded, not aborted. A
    timeout after real work is graded and labelled, never called unreachable."""
    if t.get("rc") in (126, 127):
        return True
    last = t.get("last") or ""
    if not t["tools"] and len(last) < 300 and LOGIN_RE.search(last):
        return True
    return t.get("rc", 0) != 0 and not t["tools"] and not last and not t.get("timed_out")


# --------------------------------------------------------------- ledger
# What has already been tested, and against which files. A case's pass stays
# valid while the skills it covers, every skill's routing surface, its own
# files, the mocks it saw and the grading engine are unchanged; a rerun then
# touches only cases that are new, failed, or stale. Straker's rule, 9 Sep
# 2026 PT: "we don't need to retest what we already tested". Lives in .git/,
# so it never ships and never commits.
def git_dir():
    try:
        p = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, text=True,
                           cwd=ROOT, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if p.returncode != 0:
        return None
    g = Path(p.stdout.strip())
    # git answers relative to ROOT ('.git'); resolve it there, not to whatever
    # directory this process was started from.
    return g if g.is_absolute() else ROOT / g


def ledger_path():
    g = git_dir()
    return (g / "dow-evals-ledger.json") if g else None


def ledger_key(case, model, effort=None):
    """One entry per case per model (per effort, when one is set). Keyed by
    case alone, the models overwrote each other and every matrix run reran
    everything (found 10 Sep 2026 PT, before the first matrix run)."""
    return f"{case['name']}@{model}" + (f"@{effort}" if effort else "")


def _migrate(led):
    for k in [k for k in led if "@" not in k]:
        e = led.pop(k)
        if e.get("model"):
            led.setdefault(f"{k}@{e['model']}", e)
    return led


def read_ledger():
    p = ledger_path()
    if p and p.is_file():
        try:
            led = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"warning: {p} did not parse ({e}); treating every case as new", file=sys.stderr)
            return {}
        # Entries written before the key carried the model: rekey them once.
        return _migrate(led)
    return {}


def write_ledger(led):
    """Atomic: a kill mid-write must not leave half a file, because a ledger
    that fails to parse reads as "nothing has ever passed" and the next run
    pays for everything again."""
    p = ledger_path()
    if p:
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(led, indent=1, sort_keys=True), encoding="utf-8")
        os.replace(tmp, p)


_LEDGER_LOCK = threading.Lock()   # parallel cases in one process record one at a time


def record_now(case, passed, model, results_dir, skills_fp_value=None, tools=None,
               effort=None, model_id=None):
    """Read-modify-write one entry. Two runners can be alive at once (a rerun
    loop and a regrade, 9 Sep 2026 PT), and a process that held the ledger in
    memory for its whole run wrote back over the other's entries."""
    with _LEDGER_LOCK:
        led = read_ledger()
        record(led, case, passed, model, results_dir, skills_fp_value, tools, effort, model_id)
        write_ledger(led)


def _hash_paths(paths, extra=b""):
    h = hashlib.sha1(extra)
    for base in paths:
        base = Path(base)
        if not base.exists():
            continue
        files = [base] if base.is_file() else sorted(q for q in base.rglob("*") if q.is_file())
        for q in files:
            if "results" in q.parts or "__pycache__" in q.parts:
                continue
            h.update(str(q.relative_to(ROOT)).encode("utf-8"))
            # Line endings are not content: git re-checks files out with CRLF
            # on this machine, and that turned every recorded pass stale once
            # (10 Sep 2026 PT).
            h.update(q.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:12]


def routing_surface():
    """Every skill's name and description: what decides which skill fires."""
    parts = []
    for p in sorted(PLUGINS.glob("*/skills/*/SKILL.md")):
        meta, _ = frontmatter(p.read_text(encoding="utf-8"))
        parts.append(f"{p.parent.name}|{meta.get('name', '')}|{meta.get('description', '')}")
    return "\n".join(parts).encode("utf-8")


def skills_fp(case):
    """Hash of the SKILL directories this case covers, plus every skill's
    routing surface (a description edit elsewhere can change which skill
    fires). A footer-only case (skills: []) depends on every skill's footer,
    so it hashes all of them."""
    dirs = []
    for s in case["skills"] or []:
        dirs += list(PLUGINS.glob(f"*/skills/{s}"))
    if not dirs:
        dirs = list(PLUGINS.glob("*/skills"))
    return _hash_paths(dirs, extra=routing_surface())


def grader_engine():
    """Source of the grading functions and the shared graders: a fix to how
    answers are scored must make recorded passes stale (review finding, 9 Sep
    2026 PT), while an edit to a help text or the ledger printing must not."""
    import inspect
    src = "".join(inspect.getsource(f) for f in
                  (grade_regex, grade_tool_used, grade_tool_order, grade_llm, graders_for, grade))
    return (src + repr(IMPLICIT_GRADERS)).encode("utf-8")


def bare_tools(tools):
    """Sorted bare names of the gateway tools a transcript called."""
    return sorted({n.rsplit("__", 1)[-1] for n, _ in tools if n.startswith("mcp__")})


def evals_fp(case, tools=None):
    """Hash of the case's own files, the grading engine, and -- for a mocked
    case -- the mock server plus the mock files for the tools the run actually
    called (`tools`; every mock when that is unknown). Editing one mock then
    invalidates only the cases that read it, not every mocked case (review
    finding, 9 Sep 2026 PT: a players-table edit had made all 19 stale)."""
    paths = [case["dir"]]
    if case["mocks"]:
        paths.append(HERE / "mock_mcp_server.py")
        if tools is None:
            paths.append(HERE / "mocks")
        else:
            paths += [HERE / "mocks" / SERVER / f"{t}.md" for t in tools]
    return _hash_paths(paths, extra=grader_engine())


def ledger_status(case, led, model, effort=None, model_id=None):
    """'current' (a pass recorded against exactly these files, this model and,
    when known, this resolved model id), 'failed', 'stale' (files or the
    model behind the alias changed since), or 'new'."""
    e = led.get(ledger_key(case, model, effort))
    if not e:
        return "new"
    if e.get("skills_fp") != skills_fp(case) or e.get("evals_fp") != evals_fp(case, e.get("tools")):
        return "stale"
    if model_id and e.get("model_id") and e["model_id"] != model_id:
        return "stale"                    # the alias now points at a newer model
    return "current" if e.get("passed") else "failed"


def record(led, case, passed, model, results_dir, skills_fp_value=None, tools=None,
           effort=None, model_id=None):
    led[ledger_key(case, model, effort)] = {
        "passed": bool(passed), "model": model, "model_id": model_id, "effort": effort,
        "when": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "skills_fp": skills_fp_value or skills_fp(case),
        "evals_fp": evals_fp(case, tools), "tools": tools,   # None = unknown: every mock counts
        "results": str(results_dir.name)}


def resolve_model_id(claude, model, effort=None):
    """What an alias like `sonnet` points at right now, from one tiny call.
    Used before a run so a recorded pass on an older model reads as stale
    (review finding, 10 Sep 2026 PT: the id was recorded but never compared)."""
    cmd = [claude, "-p", "--model", model, "--output-format", "json", "--max-turns", "1",
           "--tools", "", "--strict-mcp-config", "--no-session-persistence"]
    if effort:
        cmd += ["--effort", effort]
    try:
        p = subprocess.run(cmd, input="Reply with the single word ok.", capture_output=True,
                           text=True, encoding="utf-8", timeout=120)
        out = json.loads(p.stdout)
        usage = out.get("modelUsage") or {}
        return next(iter(usage)) if usage else None
    except Exception:
        return None


def transcript_meta(path):
    """The dow-meta line a transcript starts with, or {} for one written
    before that line existed."""
    with open(path, encoding="utf-8") as f:
        first = f.readline()
    try:
        m = json.loads(first)
        return m if m.get("type") == "dow-meta" else {}
    except Exception:
        return {}


def regrade(args):
    """Grade saved transcripts again without calling the model under test.
    Free graders cost nothing; llm graders cost one judge call each. For
    settling a grader change against an answer already paid for, and for
    salvaging a run whose console output was lost. Cases whose ledger entry
    is already current are skipped unless --all."""
    claude = find_claude()
    src = Path(args.regrade)
    if not src.is_dir():
        src = HERE / "results" / args.regrade
    if not src.is_dir():
        print(f"no results directory {args.regrade}", file=sys.stderr)
        return 1
    cases = {c["name"]: c for c in load_cases()}
    led = read_ledger()
    report, any_fail, n = [], False, 0
    for f in sorted(src.glob("*.run*.jsonl")):
        meta = transcript_meta(f)
        name = meta.get("case") or f.name.split(".run")[0].replace("__", "/", 1)
        c = cases.get(name)
        if not c:
            print(f"  skip {f.name}: no such case now ({name})")
            continue
        if args.case and not (fnmatch.fnmatch(c["dir"].name, args.case) or fnmatch.fnmatch(name, args.case)):
            continue
        model = meta.get("model") or args.model
        effort = meta.get("effort")
        if not args.all and ledger_status(c, led, model, effort) == "current":
            print(f"  current {name}  (already passed against these files; not regraded)")
            continue
        t = parse_stream(f.read_text(encoding="utf-8").splitlines())
        try:
            gs = grade(c, t, args.judge_model, claude)
        except JudgeUnreachable as e:
            print(f"  {name}: JUDGE UNREACHABLE -- {e}")
            return 2
        ok = all(g["passed"] for g in gs)
        any_fail |= not ok
        n += 1
        print_result("PASS" if ok else "FAIL", name, f"(regraded from {f.name}, {model})", gs, args.verbose)
        report.append({"case": name, "passed": ok, "runs": [{"run": 1, "passed": ok, "graders": gs,
                                                             "regraded_from": f.name}]})
        # The transcript was produced against the skills as they were when it
        # ran (its own meta line says which); a regrade refreshes only the
        # grader side, so the current evals fingerprint is recorded.
        sfp = meta.get("skills_fp") or led.get(ledger_key(c, model, effort), {}).get("skills_fp")
        if sfp:
            record_now(c, ok, model, src, sfp, tools=bare_tools(t["tools"]), effort=effort,
                       model_id=meta.get("model_id") or t["model_id"])
        else:
            print("          (not recorded: this transcript predates the meta line and has no ledger entry; "
                  "run the case instead)")
    (src / "regrade-result.json").write_text(json.dumps({"schemaVersion": "dow-headless-1",
                                                         "regraded": src.name, "cases": report}, indent=2),
                                             encoding="utf-8")
    print(f"\n{sum(1 for r in report if r['passed'])}/{n} cases passed on regrade")
    return 1 if any_fail else 0


def print_ledger(args):
    led = read_ledger()
    cases = load_cases(args.suite)
    if args.tag:
        cases = [c for c in cases if any(tg in c["tags"] for tg in args.tag)]
    models = [x.strip() for x in (args.models or args.model).split(",") if x.strip()] or [args.model]
    counts = {}
    for m in models:
        for c in cases:
            st = ledger_status(c, led, m, args.effort)
            counts[st] = counts.get(st, 0) + 1
            e = led.get(ledger_key(c, m, args.effort), {})
            print(f"  {st:<8} {m:<8} {c['name']:<44} {e.get('when', '')[:19]} {e.get('model_id') or ''}")
    print("\n" + ", ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    return 0


def main_run(args):
    claude = find_claude()
    if not claude:
        print("claude CLI not found on PATH", file=sys.stderr)
        return 2
    cases = load_cases(args.suite)
    if args.tag:
        cases = [c for c in cases if any(tg in c["tags"] for tg in args.tag)]
    if args.case:
        cases = [c for c in cases if fnmatch.fnmatch(c["dir"].name, args.case)
                 or fnmatch.fnmatch(c["name"], args.case)]
    if not cases:
        print("no cases selected", file=sys.stderr)
        return 1
    led = read_ledger()
    if not args.all:
        ids = {}
        for m in {c["model"] or args.model for c in cases}:
            ids[m] = resolve_model_id(claude, m, args.effort)
            print(f"  {m} resolves to {ids[m] or 'unknown'}")
        status = {c["name"]: ledger_status(c, led, c["model"] or args.model, args.effort,
                                           ids.get(c["model"] or args.model)) for c in cases}
        current = [c for c in cases if status[c["name"]] == "current"]
        cases = [c for c in cases if status[c["name"]] != "current"]
        for c in current:
            e = led[ledger_key(c, c["model"] or args.model, args.effort)]
            print(f"  current  {c['name']}  (passed {e['when'][:19]} on {e.get('model_id') or e['model']}; not rerun)")
        if not cases:
            print("\nnothing to run: every selected case has a recorded pass against the current files")
            return 0
        print(f"{len(cases)} case(s) to run: " +
              ", ".join(f"{c['dir'].name} ({status[c['name']]})" for c in cases))
    # Local time with its numeric offset appended, per the project rule that
    # every timestamp carries its zone (no example here: a stamp's last ten
    # digits read as a phone number to the contact check, and it was right).
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d-%H%M%S%z")
    results_dir = HERE / "results" / stamp
    results_dir.mkdir(parents=True, exist_ok=True)
    print(f"{len(cases)} case(s), model {args.model}, judge {args.judge_model}, "
          f"runs {args.runs} -> {results_dir.relative_to(ROOT)}")

    # Cases are independent -- own process, own mock server, own temp dir --
    # so they run in a pool. Straker, 9 Sep 2026 PT: sequential was too slow
    # to iterate on. A model-unreachable result stops new cases from starting;
    # cases already in flight finish and are graded.
    print_lock = threading.Lock()
    stop = threading.Event()
    state = {"cost": 0.0, "dead": 0, "judge_dead": 0}

    def run_case(c):
        if stop.is_set():
            return None
        runs = []
        for r in range(1, max(args.runs, c["runs"]) + 1):
            if stop.is_set():
                break
            t = run_case_once(c, args, claude, results_dir, r)
            state["cost"] += t["cost"]
            if unreachable(t):
                state["dead"] += 1
                stop.set()
                runs.append({"run": r, "unreachable": True, "graders": [],
                             "passed": False, "note": (t["last"] or t["stderr"])[:300]})
                with print_lock:
                    print(f"  {c['name']} run {r}: MODEL UNREACHABLE -- {(t['last'] or t['stderr'])[:120]!r}")
                break
            try:
                gs = grade(c, t, args.judge_model, claude)
                state["judge_dead"] = 0
            except JudgeUnreachable as e:
                # One judge failure is this run's failure, with the evidence.
                # Two in a row is the judge being down: stop spending.
                state["judge_dead"] += 1
                gs = [{"name": "judge", "type": "llm", "passed": False, "evidence": f"judge unreachable: {e}"}]
                if state["judge_dead"] >= 2:
                    state["dead"] += 1
                    stop.set()
                    runs.append({"run": r, "unreachable": True, "graders": gs, "passed": False,
                                 "note": f"judge unreachable twice: {e}"})
                    with print_lock:
                        print(f"  {c['name']} run {r}: JUDGE UNREACHABLE twice -- {str(e)[:120]!r}")
                    break
            ok = all(g["passed"] for g in gs) and not t["timed_out"]
            runs.append({"run": r, "passed": ok, "graders": gs, "cost": t["cost"], "model": t["model"],
                         "turns": t["turns"], "seconds": t["seconds"], "timed_out": t["timed_out"],
                         "tools": [n for n, _ in t["tools"]], "subtype": t["subtype"]})
            mark = "TIMEOUT" if t["timed_out"] else "PASS" if ok else "FAIL"
            with print_lock:
                print_result(mark, f"{c['name']} run {r}",
                             f"({t['seconds']}s, {t['turns']} turns, ${t['cost']:.3f})", gs, args.verbose)
                sys.stdout.flush()
        passed = bool(runs) and all(r["passed"] for r in runs)
        entry = {"case": c["name"], "title": c["title"], "tags": c["tags"], "passed": passed, "runs": runs}
        if runs and not any(r.get("unreachable") for r in runs):
            record_now(c, passed, c["model"] or args.model, results_dir,
                       tools=bare_tools(t["tools"]), effort=args.effort,
                       model_id=t["model_id"])         # per case: a killed run keeps its passes
        return entry

    with ThreadPoolExecutor(max_workers=max(1, args.parallel)) as pool:
        report = [e for e in pool.map(run_case, cases) if e is not None]
    total_cost, dead = state["cost"], state["dead"]
    any_fail = any(not e["passed"] for e in report)

    n_pass = sum(1 for r in report if r["passed"])
    summary = {"schemaVersion": "dow-headless-1", "when": stamp, "model": args.model,
               "judge": args.judge_model, "cases": report,
               "aggregates": {"passed": n_pass, "total": len(report),
                              "totalCostUsd": round(total_cost, 4),
                              "unreachable": dead}}
    (results_dir / "aggregate-result.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n{n_pass}/{len(report)} cases passed, ${total_cost:.2f}, results in {results_dir.relative_to(ROOT)}")
    if dead:
        print("MODEL UNREACHABLE: the suite did not run. Nothing above is a pass.\n"
              "  The note on the run says why. Not logged in:  claude auth login  (from a real terminal)")
        return 2
    return 1 if any_fail else 0


# --------------------------------------------------------------- self-test
def selftest():
    """No model. Prove the machinery: every grader type caught failing, every
    case and mock loadable, the mock server answering tools/list."""
    fails = []
    def check(name, ok, detail=""):
        print(f"  {'ok ' if ok else 'BAD'} {name}{('  ' + detail) if detail else ''}")
        if not ok:
            fails.append(name)

    # graders, positive AND negative -- a grader never seen failing is decoration
    t = parse_stream([
        json.dumps({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": "dow-league:league-rules"}},
            {"type": "tool_use", "name": "mcp__dow__get_league", "input": {}},
            {"type": "tool_use", "name": "mcp__dow__get_projections", "input": {"week": 3}}]}}),
        json.dumps({"type": "result", "subtype": "success", "result": "Week 6 you're at Bram. Cap is $375.",
                    "total_cost_usd": 0.01, "num_turns": 2}),
    ])
    check("parse_stream tools", [n for n, _ in t["tools"]] == ["Skill", "mcp__dow__get_league", "mcp__dow__get_projections"])
    check("regex contains +", grade_regex({"pattern": r"\$375", "match": "contains"}, t)[0])
    check("regex contains -", not grade_regex({"pattern": r"\$400", "match": "contains"}, t)[0])
    check("regex not_contains +", grade_regex({"pattern": r"FP_\d", "match": "not_contains"}, t)[0])
    check("regex not_contains -", not grade_regex({"pattern": r"Bram", "match": "not_contains"}, t)[0])
    check("regex count", grade_regex({"pattern": r"\bBram\b", "match": "count:1"}, t)[0])
    check("tool_used bare name +", grade_tool_used({"tool": "get_league"}, t)[0])
    check("tool_used prefixed +", grade_tool_used({"tool": "mcp__dow__get_league"}, t)[0])
    check("tool_used max 0 -", not grade_tool_used({"tool": "get_league", "min": 0, "max": 0}, t)[0])
    check("tool_used absent max 0 +", grade_tool_used({"tool": "send_message", "min": 0, "max": 0}, t)[0])
    check("tool_used input_match +", grade_tool_used({"tool": "Skill", "input_match": r'"skill":\s*"(?:[\w-]+:)?league-rules"'}, t)[0])
    check("tool_used input_match -", not grade_tool_used({"tool": "Skill", "input_match": r'league-lineup'}, t)[0])
    check("tool_used week arg +", grade_tool_used({"tool": "get_projections", "input_match": r'"week":\s*\d'}, t)[0])
    check("tool_order +", grade_tool_order({"before": "get_league", "after": "get_projections"}, t)[0])
    check("tool_order -", not grade_tool_order({"before": "get_projections", "after": "get_league"}, t)[0])
    check("unreachable detects login prompt", unreachable(parse_stream([
        json.dumps({"type": "result", "subtype": "success", "result": "Not logged in. Please run /login"})])))
    check("unreachable false on a real answer", not unreachable(t))
    check("unreachable true when the launcher failed", unreachable(dict(t, rc=127, tools=[], last="")))
    check("timeout after a tool call is not unreachable",
          not unreachable(dict(t, rc=-1, last="", timed_out=True)))
    footer = ("The league tools are not available: if they exist but return a 401 the authentication key "
              "is wrong. Ask Straker for your connector URL and add it at claude.ai > Customize > Connectors. "
              "Team accounts cannot add connectors; a personal account is needed.")
    check("a correct footer answer mentioning authentication is NOT unreachable",
          not unreachable(dict(t, rc=0, tools=[], last=footer)))
    check("a dow-meta line is ignored by parse_stream",
          parse_stream([json.dumps({"type": "dow-meta", "case": "x"})])["tools"] == [])
    all_cases = load_cases()
    mocked = next(c for c in all_cases if c["mocks"] and "league-contacts" not in (c["skills"] or []))
    contacts = next(c for c in all_cases if "league-contacts" in (c["skills"] or []))
    bare = next(c for c in all_cases if not c["mocks"])
    names = {g["_name"] for g in graders_for(mocked)}
    check("shared graders attach to a mocked case", {"shared:no-player-ids", "shared:no-phone"} <= names)
    check("shared no-phone waived for a contacts case",
          "shared:no-phone" not in {g["_name"] for g in graders_for(contacts)})
    check("no shared graders on a no-connector case",
          not any(g["_name"].startswith("shared:") for g in graders_for(bare)))
    leak = parse_stream([json.dumps({"type": "result", "subtype": "success", "result": "Brandt (id 10003) at $18"})])
    check("shared no-player-ids catches an id",
          not grade_regex(next(g for g in IMPLICIT_GRADERS if g["_name"] == "shared:no-player-ids"), leak)[0])
    check("ledger path is under the repo", str(ledger_path()).startswith(str(ROOT)))
    fp_a = evals_fp(mocked, ["get_league"])
    fp_b = evals_fp(mocked, ["get_league", "get_rosters"])
    check("evals fingerprint depends on the tools a run called", fp_a != fp_b and fp_a == evals_fp(mocked, ["get_league"]))
    check("bare_tools strips the server prefix",
          bare_tools([("mcp__dow__get_league", {}), ("Skill", {}), ("mcp__dow__get_league", {})]) == ["get_league"])
    check("routing surface names every skill",
          routing_surface().count(b"|") >= 2 * len(list(PLUGINS.glob("*/skills/*/SKILL.md"))))

    # the one parser: coercion, CSV lists, and a list that will not parse
    fm, body = frontmatter('---\ntags: ["gate", "mocked"]\nskills: league-rules, league-lineup\n'
                           'max_turns: 8\ntext: false\nname: "Quoted"\n---\nbody here')
    check("frontmatter JSON list", fm.get("tags") == ["gate", "mocked"])
    check("frontmatter CSV list", fm.get("skills") == ["league-rules", "league-lineup"])
    check("frontmatter int / bool / quoted", (fm.get("max_turns"), fm.get("text"), fm.get("name")) == (8, False, "Quoted"))
    check("frontmatter body", body.strip() == "body here")
    bad, _ = frontmatter("---\ntags: ['gate']\n---\nx")
    check("frontmatter single-quoted list stays a string (surfaced, not swallowed)", isinstance(bad.get("tags"), str))

    # cases: every prompt loads, every grader is a known type, every regex compiles,
    # every skill named in an input_match exists on disk
    cases = load_cases()
    check("cases found", len(cases) > 0, f"{len(cases)}")
    skills = {p.parent.name for p in PLUGINS.glob("*/skills/*/SKILL.md")}
    for c in cases:
        probs = []
        if not c["prompt"]:
            probs.append("empty prompt")
        if not c["graders"]:
            probs.append("no graders")
        for g in c["graders"]:
            if g.get("type") not in KNOWN_GRADERS:
                probs.append(f"{g['_name']}: unknown type {g.get('type')!r}")
            for key in ("pattern", "input_match"):
                if g.get(key) is not None:
                    try:
                        re.compile(str(g[key]))
                    except re.error as e:
                        probs.append(f"{g['_name']}: bad regex {key}: {e}")
                    # A generator once wrote `\b` as a literal backspace; the
                    # pattern compiled, matched nothing, and the case failed on
                    # a correct answer (9 Sep 2026 PT).
                    if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", str(g[key])):
                        probs.append(f"{g['_name']}: {key} contains a control character (a `\\b` written as backspace?)")
            if g.get("type") == "regex" and not g.get("pattern"):
                probs.append(f"{g['_name']}: regex without pattern")
            if g.get("type") == "tool_used" and not g.get("tool"):
                probs.append(f"{g['_name']}: tool_used without tool")
            if g.get("type") == "llm" and not g.get("criteria"):
                probs.append(f"{g['_name']}: llm without criteria")
            im = str(g.get("input_match") or "")
            for s in re.findall(r"league-[a-z-]+|rookie-draft-grades|fa-auction-grades", im):
                if s not in skills:
                    probs.append(f"{g['_name']}: names unknown skill {s}")
        if "gate" not in c["tags"] and "full" not in c["tags"]:
            probs.append("tagged neither gate nor full")
        if c["skills"] is None:
            probs.append("no `skills:` line in prompt.md (list the skills this case covers; [] for a footer-only case)")
        if "<unparsed>" in c["tags"] or "<unparsed>" in (c["skills"] or []):
            probs.append("tags: or skills: is not a list -- use JSON double quotes, or a bare comma list")
        for s in c["skills"] or []:
            if s not in skills:
                probs.append(f"skills: names unknown skill {s}")
        check(f"case {c['name']}", not probs, "; ".join(probs))

    # coverage: every skill on disk has a case, and a GATE case, that lists it.
    # This is the rule "a new skill needs an eval"; validation/audit.py check 7
    # enforces the same thing on the tracked tree and the pre-push hook runs it.
    for s in sorted(skills):
        covering = [c for c in cases if s in (c["skills"] or [])]
        gate = [c for c in covering if "gate" in c["tags"]]
        check(f"skill {s} has a gate case", bool(gate),
              ", ".join(c["dir"].name for c in gate) if gate else
              (f"only: {', '.join(c['dir'].name for c in covering)}" if covering else "NO CASE AT ALL"))

    # mocks: shared and per-case files parse; JSON bodies are JSON
    shared = load_tools(SERVER, [str(HERE / "mocks")])
    check("shared mocks present", len(shared) >= 8, ", ".join(sorted(shared)))
    for path in list((HERE / "mocks").rglob("*.md")) + list(HERE.glob("*/*/mocks/**/*.md")):
        meta, body = parse_mock(path)
        if path.name.startswith("_"):
            continue
        ok = True
        if not meta.get("text"):
            try:
                json.loads(body)
            except Exception as e:
                ok = False
        check(f"mock {path.relative_to(HERE)}", ok, "" if ok else "body is not JSON (set `text: true` if that is intended)")

    # the server answers a real handshake with the shared set. All three requests
    # go in at once and communicate() has a timeout, so a server that dies before
    # answering is a BAD line, not a hang inside a git hook.
    p = subprocess.Popen([sys.executable, str(HERE / "mock_mcp_server.py"), "--server", SERVER,
                          "--mocks", str(HERE / "mocks")],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    reqs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "no_such_tool", "arguments": {}}}]
    try:
        out, err = p.communicate("".join(json.dumps(r) + "\n" for r in reqs).encode(), timeout=30)
        replies = {}
        for line in out.decode("utf-8", "replace").splitlines():
            if line.strip():
                m = json.loads(line)
                replies[m.get("id")] = m
    except subprocess.TimeoutExpired:
        p.kill()
        replies, err = {}, b"timeout"
    init, lst, unk = replies.get(1, {}), replies.get(2, {}), replies.get(3, {})
    names = {x["name"] for x in lst.get("result", {}).get("tools", [])}
    check("mock server initialize", "result" in init, "" if "result" in init else err.decode("utf-8", "replace")[-200:])
    check("mock server tools/list matches files", names == set(shared))
    check("mock server unknown tool says so",
          bool(unk) and "Unknown tool" in unk["result"]["content"][0]["text"] and unk["result"]["isError"])

    # the ledger's state machine, on a dict: new -> current -> stale / failed
    probe = cases[0]
    led = {}
    check("ledger: unknown case is new", ledger_status(probe, led, "sonnet") == "new")
    record(led, probe, True, "sonnet", Path("x"), model_id="claude-sonnet-5")
    check("ledger: recorded pass is current", ledger_status(probe, led, "sonnet") == "current")
    check("ledger: other model is new, not overwritten", ledger_status(probe, led, "haiku") == "new")
    record(led, probe, False, "haiku", Path("x"))
    check("ledger: haiku fail leaves sonnet current",
          ledger_status(probe, led, "haiku") == "failed" and ledger_status(probe, led, "sonnet") == "current")
    check("ledger: alias moved to a newer model is stale",
          ledger_status(probe, led, "sonnet", model_id="claude-sonnet-6") == "stale")
    led[ledger_key(probe, "sonnet")]["evals_fp"] = "changed"
    check("ledger: changed case files are stale", ledger_status(probe, led, "sonnet") == "stale")
    record(led, probe, True, "sonnet", Path("x"))
    led[ledger_key(probe, "sonnet")]["skills_fp"] = "changed"
    check("ledger: changed skill files are stale", ledger_status(probe, led, "sonnet") == "stale")
    record(led, probe, False, "sonnet", Path("x"))
    check("ledger: recorded fail is failed", ledger_status(probe, led, "sonnet") == "failed")
    check("ledger: effort is part of the key", ledger_key(probe, "sonnet", "high") != ledger_key(probe, "sonnet"))
    old = {probe["name"]: {"passed": True, "model": "sonnet"}}
    import json as _j, tempfile as _t
    check("ledger: case-only keys are rekeyed on read",
          "@sonnet" in next(iter(_migrate(old))))
    check("ledger: skills fingerprint is not empty", len(skills_fp(probe)) == 12)

    # the CLI is here (running it is a separate question, answered by a real run)
    check("claude CLI found", bool(find_claude()), find_claude() or "")

    print(f"\nselftest: {len(fails)} problem(s)")
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--selftest", action="store_true", help="no model; check graders, cases, mocks, server")
    ap.add_argument("--suite", choices=list(SUITES), help="one plugin's cases only")
    ap.add_argument("--tag", nargs="*", help="only cases carrying any of these tags")
    ap.add_argument("--case", help="glob on the case directory name")
    ap.add_argument("--runs", type=int, default=1, help="repetitions per case (max with the case's own)")
    ap.add_argument("--model", default="sonnet",
                    help="model under test. haiku was tried 9 Sep 2026 PT: 6c a case against sonnet's 10c, "
                         "and it failed to trigger a skill that sonnet triggered -- a false failure, not a saving")
    ap.add_argument("--judge-model", default="sonnet",
                    help="the grader for llm criteria. Straker: Sonnet everywhere (9 Sep 2026 PT); "
                         "haiku judged for cents less and returned no verdict on three answers")
    ap.add_argument("--timeout", type=int, default=600, help="seconds per run")
    ap.add_argument("--max-budget", type=float, default=1.0, help="USD ceiling per run (0 = none)")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--effort", help="effort level passed to claude -p; part of the ledger key when set")
    ap.add_argument("--models", help="for --ledger only: comma list of models to show (default --model)")
    ap.add_argument("--parallel", type=int, default=6,
                    help="cases run at once; each is its own claude process and mock server (default 6)")
    ap.add_argument("--regrade", metavar="RESULTS_DIR",
                    help="grade the transcripts in a results directory again; no model-under-test calls")
    ap.add_argument("--all", action="store_true",
                    help="run every selected case, including ones with a current recorded pass")
    ap.add_argument("--ledger", action="store_true", help="show each case's recorded status and exit")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.ledger:
        sys.exit(print_ledger(args))
    if args.regrade:
        sys.exit(regrade(args))
    sys.exit(main_run(args))


if __name__ == "__main__":
    # Evidence strings and CLI output carry characters a Windows console
    # cannot encode; a crash while printing would read as a failed run.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    main()
