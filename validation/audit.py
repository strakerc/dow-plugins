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

def report(name, bad, control_ok):
    global checks
    checks += 1
    status = "PASS" if not bad else "FAIL"
    ctl = "control ok" if control_ok else "*** CONTROL FAILED - CHECK IS INERT ***"
    print(f"  {status}  {name}  [{ctl}]")
    for b in bad:
        print(f"          {b}")
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
PHONE = re.compile(r"(?<!\d)(\(?\d{3}\)?[\s.\-]?)\d{3}[\s.\-]?\d{4}(?!\d)")
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
ctl_num = "1" * 10                      # ten digits, phone-shaped, nobody's
ctl_reserved = "412" + "555" + "0100"   # the reserved range, must be EXEMPT
ctl_addr = "a" + "@" + "b.co"           # address-shaped, not an exempt domain
ctl_phone = bool(PHONE.search(ctl_num)) and RESERVED.match(ctl_reserved) is not None
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

print()
print(f"{checks - len(fails)}/{checks} checks passed over {len(FILES)} tracked files")
sys.exit(1 if fails else 0)
