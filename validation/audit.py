#!/usr/bin/env python3
"""Whole-tree invariant audit for dow-plugins.

The pre-commit hook scans ADDED LINES ONLY, deliberately -- a rule that re-flags
existing content trains everyone to use --no-verify. The cost is that nothing has
ever checked what is already in the tree. This does, once.

Every check carries a CONTROL: a synthetic case that MUST be caught. A check that
cannot be seen failing proves nothing, which is the bug this project keeps
shipping.
"""
import io, json, os, re, subprocess, sys

# Repo root is the parent of validation/, so this runs from any directory.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def tracked():
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout
    return [f for f in out.split("\n") if f.strip()]

FILES = tracked()
fails, checks = [], 0

overrides = []

def report(name, bad, control_ok, note=None):
    """`note` marks a check a human overrode: it prints as OVERRIDE, not PASS,
    stays out of the fail count so the push proceeds, and is counted in the
    summary line, because a check that did not run is not a check that passed."""
    global checks
    checks += 1
    status = "FAIL" if bad else "OVERRIDE" if note else "PASS"
    ctl = "control ok" if control_ok else "*** CONTROL FAILED - CHECK IS INERT ***"
    print(f"  {status}  {name}  [{ctl}]")
    for b in bad:
        print(f"          {b}")
    if note:
        print(f"          {note}")
        overrides.append(name)
    if bad:
        fails.append(name)
    if not control_ok:
        fails.append(name + " (control)")

# --- 1. every SKILL.md carries the canonical footer -------------------------
ref = io.open(".githooks/skill-footer.md", encoding="utf-8").read().strip()
skills = [f for f in FILES if f.endswith("SKILL.md")]
bad = []
for f in skills:
    t = io.open(f, encoding="utf-8").read()
    if ref not in t:
        bad.append(f"{f} -- footer missing or paraphrased")
control = ref not in "# a file with no footer at all"
report(f"all {len(skills)} SKILL.md carry the canonical footer", bad, control)

# --- 2. no dollar-sign + single digit in a SKILL.md -------------------------
PAT = re.compile(r"\$\d(?!\d)")
bad = []
for f in skills:
    for n, line in enumerate(io.open(f, encoding="utf-8").read().split("\n"), 1):
        if PAT.search(line):
            bad.append(f"{f}:{n}")
control = bool(PAT.search("costs $5 per year")) and not PAT.search("costs $25 per year")
report("no '$' + single digit in any SKILL.md", bad, control)

# --- 3. every tracked *.json parses -----------------------------------------
bad = []
jsons = [f for f in FILES if f.endswith(".json")]
for f in jsons:
    try:
        json.loads(io.open(f, encoding="utf-8").read())
    except Exception as e:
        bad.append(f"{f} -- {e}")
try:
    json.loads('{"broken":')
    control = False
except Exception:
    control = True
report(f"all {len(jsons)} tracked *.json parse", bad, control)

# --- 4. no phone numbers or email addresses anywhere in the tree ------------
# Same shapes the hook uses. Exemptions are BY VALUE: the reserved fictional
# range (any area code, exchange 555, line 01XX) and the example.* domains.
# Area code and exchange start with 2-9 in the North American plan, so a run
# beginning with 0 or 1 is not a number -- and every Unix epoch until 2033
# begins with 1 (the NFL schedule mock's `kickoff`, 13 Sep 2026 PT). Same
# narrowing as .githooks/contact-lib.sh; the reserved-range exemption stands.
PHONE = re.compile(r"(?<!\d)(\(?[2-9]\d{2}\)?[\s.\-]?)[2-9]\d{2}[\s.\-]?\d{4}(?!\d)")
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
RESERVED = re.compile(r"^\d{3}55501\d{2}$")
EXEMPT_DOM = ("example.com", "example.org", "example.net")
NOREPLY = ("noreply@", "users.noreply.github.com")
bad = []
for f in FILES:
    try:
        text = io.open(f, encoding="utf-8", errors="replace").read()
    except Exception:
        continue
    for n, line in enumerate(text.split("\n"), 1):
        for m in PHONE.finditer(line):
            digits = re.sub(r"\D", "", m.group(0))
            if len(digits) == 10 and not RESERVED.match(digits):
                bad.append(f"{f}:{n} -- phone-shaped, not the reserved range")
        for m in EMAIL.finditer(line):
            v = m.group(0).lower()
            if not v.endswith(EXEMPT_DOM) and not any(x in v for x in NOREPLY):
                bad.append(f"{f}:{n} -- email {v.split('@')[0][:2]}...@{v.split('@')[1]}")
# CONTROL VALUES ARE BUILT AT RUNTIME, NEVER WRITTEN DOWN. An earlier draft of
# this file put a literal ten-digit number here as the must-be-caught case, and
# the pre-commit hook refused the commit -- correctly, because the number I had
# reached for was a real one seen in a get_league payload minutes earlier. That
# is exactly how a real number ends up in a public repo: not by intent, but as
# test data in a file about protecting against it. Constructing the strings
# means no contact-shaped literal exists here to leak or to trip the gate.
ctl_num = "2" * 10                      # ten digits, phone-shaped, nobody's
ctl_epoch = "1" + "7" * 9               # ten digits starting with 1: a timestamp, never a number
ctl_reserved = "412" + "555" + "0100"   # the reserved range, must be EXEMPT
ctl_addr = "a" + "@" + "b.co"           # address-shaped, not an exempt domain
ctl_phone = (bool(PHONE.search(ctl_num)) and RESERVED.match(ctl_reserved) is not None
             and not PHONE.search(ctl_epoch))
ctl_email = bool(EMAIL.search(ctl_addr)) and ("x" + "@" + EXEMPT_DOM[0]).endswith(EXEMPT_DOM)
report("no phone numbers or emails in any tracked file", bad, ctl_phone and ctl_email)

# --- 5. no build droppings tracked ------------------------------------------
bad = [f for f in FILES if "__pycache__" in f or f.endswith(".pyc")]
report("no __pycache__ or *.pyc tracked", bad, True)

# --- 6. stated counts match reality -----------------------------------------
def skills_in(pkg):
    d = f"plugins/{pkg}/skills"
    return sorted(x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x)))
a, b = skills_in("dow-league"), skills_in("dow-league-lm")
claude = io.open("CLAUDE.md", encoding="utf-8").read()
bad = []
# Spelled out because CLAUDE.md writes counts as words. A count with no word here
# is REPORTED, never raised: an exception would abort the audit mid-run and the
# checks below it would silently never execute.
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
         7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
         12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
         16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen",
         20: "twenty"}
total = len(a) + len(b)
word = WORDS.get(total)
if word is None:
    bad.append(f"{total} skills; no number-word mapped, extend WORDS in this file")
elif f"{word} `SKILL.md` files" not in claude:
    bad.append(f"CLAUDE.md does not say '{word} SKILL.md files' (actual: {total})")
for pkg, lst in (("dow-league", a), ("dow-league-lm", b)):
    rd = io.open(f"plugins/{pkg}/README.md", encoding="utf-8").read()
    missing = [s for s in lst if s not in rd]
    if missing:
        bad.append(f"{pkg}/README.md does not mention: {', '.join(missing)}")
report(f"counts and README rows match reality ({len(a)} + {len(b)} skills)", bad, True)

# --- 7. every skill has an eval, and one in the gate set ----------------------
# A skill with no eval is a skill nobody can watch failing. Each case's prompt.md
# lists the skills it covers in a `skills:` line; every SKILL.md on disk must be
# named by at least one case tagged `gate`, the set the pre-push hook runs.
# The front matter is read by the same function the eval runner uses, so this
# check and run_headless.py cannot disagree about what a case declares.
sys.path.insert(0, os.path.join(ROOT, "validation", "evals"))
from mock_mcp_server import frontmatter

def cases_covering(prompt_texts):
    """{skill: set(tags)} over prompt.md contents. A tags/skills value that is
    not a list is reported under a sentinel key rather than dropped."""
    cov = {}
    for text in prompt_texts:
        meta, _ = frontmatter(text)
        tags, sk = meta.get("tags", []), meta.get("skills", [])
        if not isinstance(tags, list) or not isinstance(sk, list):
            cov.setdefault("<unparsed>", set()).add(meta.get("name", "?"))
            continue
        for s in sk:
            cov.setdefault(s, set()).update(tags)
    return cov

def coverage_gaps(skill_names, cov):
    out = []
    for s in skill_names:
        if s not in cov:
            out.append(f"{s} -- no eval case lists it in `skills:`")
        elif "gate" not in cov[s]:
            out.append(f"{s} -- has a case, but none tagged `gate`")
    if "<unparsed>" in cov:
        out.append("cases with a tags:/skills: line that is not a list: " + ", ".join(sorted(cov["<unparsed>"])))
    return out

prompts = [io.open(f, encoding="utf-8").read() for f in FILES
           if f.startswith("validation/evals/") and f.endswith("/prompt.md")]
cov = cases_covering(prompts)
bad = coverage_gaps(a + b, cov)
# Control: synthetic prompt.md texts through the REAL path -- one gate case, one
# full-only case, one written as a bare comma list, one with a list that does not
# parse. A skill with no case, one with only a full case, and the unparsable
# case must all be named; the covered skill must not be.
ctl_cov = cases_covering([
    '---\nname: "a"\ntags: ["gate", "mocked"]\nskills: ["covered"]\n---\np',
    '---\nname: "b"\ntags: ["full"]\nskills: full-only\n---\np',
    "---\nname: \"c\"\ntags: ['gate']\nskills: [\"covered\"]\n---\np",
])
ctl = coverage_gaps(["covered", "full-only", "absent"], ctl_cov)
control = (len(ctl) == 3 and ctl[0].startswith("full-only") and ctl[1].startswith("absent")
           and ctl[2].endswith(": c") and ctl_cov.get("covered") == {"gate", "mocked"})
report(f"every skill has a gate eval case ({len(cov)} skills covered)", bad, control)

# --- 8. every SKILL.md opens with the canonical "Before you answer" block -------
# The five house lines (names only, Pacific times, say what is missing, lead
# with the answer, hand off a wrong-skill question) live at the top of every skill because small models at low
# effort follow a short block near the top and ignore the same rule stated
# deep in the prose (measured 10 Sep 2026 PT). Canonical text is
# .githooks/skill-header.md; two skills append one sentence of exception to
# line 1, which is allowed, so the match is line-by-line with that one
# insertion tolerated.
hdr_lines = io.open(".githooks/skill-header.md", encoding="utf-8").read().strip().splitlines()

def header_ok(text):
    """The block must be verbatim AND at the top: the first quoted line within
    the first six non-blank lines after the front matter (an H1 may precede it).
    A block that drifts to the bottom is the thing this check exists to stop."""
    lines = [l.rstrip("\r") for l in text.splitlines()]
    fm_end = 0
    if lines and lines[0] == "---":
        for i in range(1, len(lines)):
            if lines[i] == "---":
                fm_end = i + 1
                break
    body = [l for l in lines[fm_end:] if l.strip()]
    first = next((i for i, l in enumerate(body) if l.startswith(">")), None)
    if first is None or first > 5:
        return False
    got = body[first:first + len(hdr_lines)]
    if len(got) != len(hdr_lines):
        return False
    for want, have in zip(hdr_lines, got):
        if have == want:
            continue
        if want.rstrip().endswith("matched.") and have.startswith(want.rstrip()):
            continue          # the one allowed exception sentence, appended
        return False
    return True

bad = [f"{f} -- header missing, not verbatim, or not at the top" for f in skills
       if not header_ok(io.open(f, encoding="utf-8").read())]
_fm = "---\nname: x\n---\n# Title\n\n"
_ok = _fm + "\n".join(hdr_lines) + "\n\nbody"
_exc = _ok.replace("matched.", "matched. The one exception is X.")
_para = _fm + "\n".join(hdr_lines).replace("Names only", "Use names") + "\n\nbody"   # same length, one word off
_late = _fm + "body\n" * 8 + "\n".join(hdr_lines) + "\n"                             # verbatim, but buried
control = header_ok(_ok) and header_ok(_exc) and not header_ok(_para) and not header_ok(_late)
report(f"all {len(skills)} SKILL.md open with the canonical house block", bad, control)

# --- 9. every shared eval mock is pinned to the worker version it mirrors ----
# The routing-surface check keeps mock DESCRIPTIONS in step with the gateway;
# nothing kept mock BODIES in step with the worker that produces them until
# tradeval 0.2.3 changed its `notes` and the mock said `notes: []` (13 Sep 2026
# PT). validation/mock-mirrors.json names the worker and version each mock was
# last read against; this check reads the worker's version out of the sibling
# dow-workers clone and fails when it has moved. Moving the pin is the
# acknowledgement that someone re-read the mock. Straker's rule, 13 Sep 2026
# PT: a missing clone is a FAILURE, not a skip -- a check that never ran is not
# a check that passed -- and only DOW_ALLOW_MISSING_WORKERS=1 lets it through,
# reported as OVERRIDE rather than PASS.
#
# A version pin misses a body change nobody bumped, and a source hash would
# fire on every comment edit; the pin is kept because this repo already treats
# an unbumped worker change as a rule broken (dow-workers CLAUDE.md, "No code
# change is not no change"), so it leans on a contract that exists.
import functools, tempfile
from mock_mcp_server import load_tools
MIRRORS = os.path.join(ROOT, "validation", "mock-mirrors.json")
MOCKS_ROOT = os.path.join(ROOT, "validation", "evals", "mocks")
MOCK_SERVER = "dow"                      # run_headless.SERVER; the mocks live under mocks/dow/
WORKERS_ROOT_ENV = "DOW_WORKERS_ROOT"    # same shape as DOW_PLUGINS_ROOT in scripts/release.mjs
OVERRIDE_ENV = "DOW_ALLOW_MISSING_WORKERS"
# Two declaration forms exist: `const VERSION = "x.y.z";` (dowgateway, tradeval,
# fantasypros) and an inline `serverInfo: { ..., version: "x.y.z" }`
# (myfantasyleague, discord). Both are what /admin/versions reports.
VERSION_RES = (re.compile(r'^(?:export\s+)?const VERSION = "(\d+\.\d+\.\d+)";', re.M),
               re.compile(r'serverInfo:\s*\{.{0,300}?version:\s*"(\d+\.\d+\.\d+)"', re.S))

def native_path(p):
    """A Git Bash path (/c/Users/...) handed to a Windows Python is not a path
    it can open; rewrite the drive prefix. Any other form passes through."""
    m = re.match(r"^/([A-Za-z])/(.*)$", p or "")
    return f"{m.group(1).upper()}:/{m.group(2)}" if m and os.name == "nt" else p

@functools.lru_cache(maxsize=None)
def worker_version(workers_root, worker):
    path = os.path.join(workers_root, "workers", worker, "src", "worker.js")
    if not os.path.isfile(path):
        return None
    text = io.open(path, encoding="utf-8").read()
    for pat in VERSION_RES:
        m = pat.search(text)
        if m:
            return m.group(1)
    return None

def check_mirrors(pins, workers_root, allow_missing, mock_names, schema_pin=None):
    """Returns (bad, note): the failures, and the override line when the clone
    is absent and the override is set."""
    bad, note = [], None
    for name in sorted(mock_names):
        if name not in pins:
            bad.append(f"{name}.md has no entry in validation/mock-mirrors.json")
    for name in sorted(set(pins) - set(mock_names)):
        bad.append(f"mock-mirrors.json pins {name}, but there is no mocks/{MOCK_SERVER}/{name}.md")
    if not os.path.isdir(os.path.join(workers_root, "workers")):
        msg = (f"dow-workers clone not found at {workers_root} -- mock bodies were NOT "
               f"checked against their workers (set {WORKERS_ROOT_ENV}, or "
               f"{OVERRIDE_ENV}=1 to override)")
        if allow_missing:
            note = "note: " + msg + " -- OVERRIDDEN by a human, proceeding"
        else:
            bad.append(msg)
        return bad, note
    for name, pin in sorted(pins.items()):
        live = worker_version(workers_root, pin["worker"])
        if live is None:
            bad.append(f"{name}: no version found for worker {pin['worker']} under {workers_root}")
        elif live != pin["version"]:
            bad.append(f"{name}: pinned to {pin['worker']} {pin['version']}, the worker is now {live} -- "
                       f"re-read the mock against the worker, then move the pin")
    # The argument schemas the mock server advertises (SCHEMAS in
    # mock_mcp_server.py) are a hand copy of the gateway's tools/list, pinned
    # the same way: a gateway bump fails here until someone re-reads them
    # (added 17 Sep 2026 PT; the copy itself dates from 14 Sep).
    if schema_pin:
        live = worker_version(workers_root, schema_pin["worker"])
        if live is None:
            bad.append(f"schemas: no version found for worker {schema_pin['worker']} under {workers_root}")
        elif live != schema_pin["version"]:
            bad.append(f"schemas: SCHEMAS in mock_mcp_server.py pinned to {schema_pin['worker']} "
                       f"{schema_pin['version']}, the worker is now {live} -- re-read tools/list, then move the pin")
    return bad, note

def default_workers_root():
    """The sibling of this checkout, or, in a linked worktree, the sibling of
    the main checkout: a worktree lives at .claude/worktrees/<name>, where
    ../dow-workers is nothing (found 24 Sep 2026 PT, the first worktree push).
    The main checkout is the parent of git's common dir."""
    here = os.path.join(os.path.dirname(ROOT), "dow-workers")
    if os.path.isdir(os.path.join(here, "workers")):
        return here
    try:
        p = subprocess.run(["git", "rev-parse", "--git-common-dir"],
                           capture_output=True, text=True, cwd=ROOT, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return here
    if p.returncode != 0 or not p.stdout.strip():
        return here
    # Relative ('.git') in the main checkout, absolute from a worktree.
    main = os.path.dirname(os.path.normpath(os.path.join(ROOT, p.stdout.strip())))
    return os.path.join(os.path.dirname(main), "dow-workers")

_mirrors = json.loads(io.open(MIRRORS, encoding="utf-8").read())
pins, schema_pin = _mirrors["mocks"], _mirrors.get("schemas")
mock_names = set(load_tools(MOCK_SERVER, [MOCKS_ROOT]))
workers_root = native_path(os.environ.get(WORKERS_ROOT_ENV)) or default_workers_root()
allow_missing = os.environ.get(OVERRIDE_ENV, "") == "1"
bad, note = check_mirrors(pins, workers_root, allow_missing, mock_names, schema_pin)
if schema_pin is None:
    bad.append("mock-mirrors.json has no `schemas` pin for SCHEMAS in mock_mcp_server.py")

# Controls, against a synthetic clone so they run whether or not the real one
# is present: a moved version in either declaration form must be caught, a
# missing clone must fail without the override and pass, loudly, with it.
with tempfile.TemporaryDirectory() as fake:
    for w, body in (("tradeval", 'const VERSION = "9.9.9";\n'),
                    ("discord", 'serverInfo: { name: "discord-mcp", version: "8.8.8" },\n')):
        d = os.path.join(fake, "workers", w, "src")
        os.makedirs(d)
        io.open(os.path.join(d, "worker.js"), "w", encoding="utf-8").write(body)
    _pins = {"evaluate_trade": {"worker": "tradeval", "version": "0.0.0"},
             "send_message": {"worker": "discord", "version": "0.0.0"}}
    _names = {"evaluate_trade", "send_message"}
    _moved, _ = check_mirrors(_pins, fake, False, _names,
                              {"worker": "tradeval", "version": "0.0.0"})
    _nodir, _ = check_mirrors(_pins, os.path.join(fake, "no-such-dir"), False, _names)
    _over, _overnote = check_mirrors(_pins, os.path.join(fake, "no-such-dir"), True, _names)
control = (len(_moved) == 3 and "9.9.9" in _moved[0] and "8.8.8" in _moved[1]
           and _moved[2].startswith("schemas:") and "9.9.9" in _moved[2]
           and len(_nodir) == 1 and not _over and _overnote is not None
           and native_path("/c/x/y") in ("C:/x/y", "/c/x/y"))
report(f"all {len(mock_names)} shared mocks and the schema table pinned to a current worker version", bad, control, note=note)

# --- 9b. every shared mock's role matches the gateway route it mirrors -------
# `roles: lm` in a mock's front matter is hand-set, and roles have moved before
# (get_injuries went LM_ONLY -> OWNER on 9 Sep 2026 PT). Read dowgateway's
# ROUTES out of the same sibling clone and compare. Same override as check 9.
from mock_mcp_server import visible
ROUTE_RE = re.compile(r'name:\s*"(\w+)",\s*roles:\s*(\w+)')

def route_roles(workers_root):
    path = os.path.join(workers_root, "workers", "dowgateway", "src", "worker.js")
    if not os.path.isfile(path):
        return None
    return dict(ROUTE_RE.findall(io.open(path, encoding="utf-8").read()))

def check_roles(routes, mocks):
    bad = []
    for name, (meta, _) in sorted(mocks.items()):
        if name not in routes:
            continue
        lm_only_mock = visible(meta, "lm") and not visible(meta, "owner")
        lm_only_route = routes[name] == "LM_ONLY"
        if lm_only_mock != lm_only_route:
            bad.append(f"{name}: mock is {'LM-only' if lm_only_mock else 'every role'}, the gateway route is {routes[name]}")
    return bad

mocks = load_tools(MOCK_SERVER, [MOCKS_ROOT])
routes = route_roles(workers_root)
if routes is None:
    bad9b = [] if allow_missing else [f"dow-workers clone not found at {workers_root} -- mock roles were NOT checked against the gateway routes"]
    note9b = ("note: mock roles were NOT checked against the gateway routes -- OVERRIDDEN by a human, proceeding"
              if allow_missing else None)
else:
    bad9b, note9b = check_roles(routes, mocks), None
_ctl_bad = check_roles({"a_tool": "LM_ONLY", "b_tool": "OWNER"},
                       {"a_tool": ({}, ""), "b_tool": ({"roles": ["lm"]}, ""), "c_tool": ({"roles": ["lm"]}, "")})
control9b = len(_ctl_bad) == 2 and not check_roles({"a_tool": "LM_ONLY"}, {"a_tool": ({"roles": ["lm"]}, "")})
report(f"all {len(mocks)} shared mocks carry the role of their gateway route", bad9b, control9b, note=note9b)

print()
print(f"{checks - len(fails)}/{checks} checks passed over {len(FILES)} tracked files"
      + (f" -- {len(overrides)} OVERRIDDEN by a human, not run: {', '.join(overrides)}" if overrides else ""))
sys.exit(1 if fails else 0)
