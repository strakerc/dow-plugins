#!/usr/bin/env python3
"""The regression gate for dow-plugins. Run it before /code-review, and again
against the installed copy after a push.

    python3 validation/regress.py              # free stages: seconds, no model
    python3 validation/regress.py --evals      # + the skill evals tagged gate
    python3 validation/regress.py --evals --full
    python3 validation/regress.py --official   # try `claude plugin eval` instead of the shim

STAGES, in order. Each prints PASS, FAIL or SKIP with a reason; a SKIP is
printed loudly because a check that did not run is not a check that passed.

  1 static     validation/audit.py (the seven invariants, whole tree) and
               `claude plugin validate` on the marketplace and both manifests
  2 scripts    validation/script_tests.py -- the four skill scripts on
               synthetic fixtures
  3 backtest   validation/lineup-backtest/, when its fixtures are on disk
               (they are never committed; SKIP otherwise, and say so)
  4 evals-lint validation/evals/run_headless.py --selftest -- every case and
               mock loads, every grader type seen failing, the mock gateway
               answers a handshake. No model.
  5 evals      the skill evals through headless Claude Code. Uses the plan's
               usage window, and minutes; only with --evals. `gate` tag by default, --full for
               everything; only cases not already passed against the current
               files, --all to force.

  --post-push  the after-deployment run. Pushing to main IS the deployment
               here, so what shipped is origin/main: this fetches, refuses
               unless plugins/ in the working tree is byte-identical to
               origin/main, then runs every eval case. A pass then describes
               the files owners are actually receiving, not a local draft.

  --pre-push   what .githooks/pre-push runs, once per commit being pushed: the
               free stages, then the gate evals if plugins/ differs from what
               the remote has. The runner keeps a per-case ledger in
               .git/dow-evals-ledger.json: a case's pass stays valid while the
               skills it covers, its own files and the shared mocks are
               unchanged, and only new, failed or stale cases are run. So the
               usual order (regress, /code-review, regress --evals, fix, rerun
               the failures, push) pays for each case once, and the push after
               a local merge pays nothing. --evals --all forces every case.

EXIT CODES
  0  every required stage ran and passed
  1  a stage failed
  2  the evals could not run (CLI not logged in, model unreachable)
  3  incomplete: plugins/ has changed against origin/main and --evals was
     not given. The free stages passed, but the gate for a skill change is
     the evals, and this exit stops "regress.py passed" from being said
     about a run that never asked the model anything.

Why the gate is an exit code and not a note: every bug this project has
shipped came from a check that reported clean while never running.
"""
import argparse, os, re, shutil, subprocess, sys, tempfile, time, types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
# `claude plugin validate` prints symbols a Windows console cannot encode, and a
# crash while echoing a tool's output would look exactly like that tool failing.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PY = sys.executable
CLAUDE = shutil.which("claude") or str(Path.home() / ".local" / "bin" / "claude")
EARLY_ACCESS = re.compile(r"^`plugin eval` is currently in early access\s*$", re.M)

results = []   # (stage, status, detail)


def say(stage, status, detail=""):
    results.append((stage, status, detail))
    flag = {"PASS": "PASS", "FAIL": "FAIL", "SKIP": "SKIP  <-- did not run",
            "WARN": "WARN  <-- reported, not gating"}[status]
    print(f"\n[{flag}] {stage}" + (f": {detail}" if detail else ""))


def print_summary(label):
    print("\n" + "=" * 64)
    for stage, status, detail in results:
        print(f"  {status:<4}  {stage:<22} {detail}")
    print(f"\nRESULT: {label}")


def run(cmd, timeout=3600, **kw):
    """Run a child and always return an object with returncode/stdout/stderr.

    A launcher that cannot start (an npm `claude.cmd` shim on Windows is not a
    program CreateProcess can run) or a hang must read as a failed stage, not
    a traceback out of a git hook.
    """
    print(f"$ {' '.join(str(c) for c in cmd)}")
    t0 = time.time()
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    try:
        p = subprocess.run(cmd, text=True, encoding="utf-8", errors="replace", env=env,
                           stdin=subprocess.DEVNULL, capture_output=kw.pop("capture", False),
                           timeout=timeout, **kw)
    except OSError as e:
        p = types.SimpleNamespace(returncode=127, stdout="", stderr=f"could not start {cmd[0]}: {e}")
        print(p.stderr)
    except subprocess.TimeoutExpired:
        p = types.SimpleNamespace(returncode=124, stdout="", stderr=f"timed out after {timeout}s")
        print(p.stderr)
    p.seconds = round(time.time() - t0, 1)
    return p


def git(*a):
    p = subprocess.run(["git", *a], capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout.strip()


# ------------------------------------------------------------------ stages
def stage_static():
    p = run([PY, "validation/audit.py"])
    ok = p.returncode == 0
    for target in (".", "plugins/dow-league", "plugins/dow-league-lm"):
        q = run([CLAUDE, "plugin", "validate", target], capture=True, timeout=300)
        print((q.stdout or "").strip()[-400:])
        if q.returncode != 0:
            ok = False
            print((q.stderr or "").strip()[-400:])
    say("static", "PASS" if ok else "FAIL", "audit.py and plugin validate")


def stage_scripts():
    p = run([PY, "validation/script_tests.py"], capture=True)
    tail = (p.stderr or p.stdout).strip().splitlines()[-3:]
    print("\n".join(tail))
    say("scripts", "PASS" if p.returncode == 0 else "FAIL", " / ".join(tail[-1:]))


def stage_backtest():
    d = ROOT / "validation" / "lineup-backtest"
    if not (d / "league.json").is_file():
        say("backtest", "SKIP", "fixtures absent -- see validation/lineup-backtest/README.md to regenerate")
        return
    ok = True
    # Exit codes AND the scripts' own verdict lines: both scripts exited 0 on a
    # gate failure until 9 Sep 2026 PT, and the stage read that as a pass.
    verdicts = {"backtest.py": "ALL HARD GATES PASS", "adversarial.py": "ALL ADVERSARIAL CHECKS PASS"}
    for script, verdict in verdicts.items():
        p = run([PY, script], cwd=d, capture=True)
        print("\n".join((p.stdout or "").strip().splitlines()[-4:]))
        if p.returncode != 0 or verdict not in (p.stdout or ""):
            ok = False
            print(f"  {script}: exit {p.returncode}, verdict line {'present' if verdict in (p.stdout or '') else 'MISSING'}")
    say("backtest", "PASS" if ok else "FAIL", "league-lineup back-test and adversarial run")


def stage_evals_lint():
    p = run([PY, "validation/evals/run_headless.py", "--selftest"])
    say("evals-lint", "PASS" if p.returncode == 0 else "FAIL", "cases, graders, mocks, mock gateway")


# ------------------------------------------------------- change detection
def plugins_changed():
    """Has this branch touched plugins/ since it left origin/main? Advisory,
    for the INCOMPLETE exit: merge-base isolates this branch's own work.
    (The hook asks a different question -- will the push change the remote's
    plugins/ -- and diffs the remote tip directly; see pre_push.)"""
    try:
        rc, base = git("merge-base", "HEAD", "origin/main")
        if rc != 0:
            return None
        _, diff = git("diff", "--name-only", base, "--", "plugins/")
        _, wt = git("status", "--porcelain", "--", "plugins/")
        return bool(diff.strip() or wt.strip())
    except Exception:
        return None


def working_plugins_tree():
    """Tree hash of plugins/ as it sits in the working tree, or None if dirty.
    The evals run against the working tree, so a pass can only be recorded
    for a tree that git can name."""
    rc, dirty = git("status", "--porcelain", "--", "plugins/")
    if rc != 0 or dirty:
        return None
    rc, tree = git("rev-parse", "HEAD:plugins")
    return tree if rc == 0 else None


# ---------------------------------------------------------------- evals
def stage_evals(args):
    cmd = [PY, "validation/evals/run_headless.py", "--model", args.model,
           "--judge-model", args.judge_model, "--runs", str(args.runs),
           "--parallel", str(args.parallel)]
    if not args.full:
        cmd += ["--tag", "gate"]
    if args.case:
        cmd += ["--case", args.case]
    if args.all:
        cmd.append("--all")
    p = run(cmd, timeout=6 * 3600)
    if p.returncode == 2:
        say("evals", "FAIL", "model unreachable -- `claude auth login` in a real terminal, then re-run")
        return 2
    say(f"evals[{args.model}]" if args.models else "evals", "PASS" if p.returncode == 0 else "FAIL",
        "headless skill evals, " + ("all cases" if args.full else "gate tag")
        + (", forced" if args.all else ", stale and failed only"))
    return p.returncode


def stage_official(args):
    """Hand the same cases to `claude plugin eval`. UNVERIFIED: that command was
    early access and closed for this account when this was written, so this
    path has never been watched succeeding. It assembles a temp copy of each
    plugin with validation/evals/<plugin>/ as its evals/ directory and the
    shared mocks alongside, runs the command, and reports what it said."""
    ok, any_ran = True, False
    for plugin in ("dow-league", "dow-league-lm"):
        src = ROOT / "validation" / "evals" / plugin
        if not src.is_dir():
            continue
        tmp = Path(tempfile.mkdtemp(prefix=f"dow-official-{plugin}-"))
        shutil.copytree(ROOT / "plugins" / plugin, tmp / "plugin")
        shutil.copytree(src, tmp / "plugin" / "evals")
        shutil.copytree(ROOT / "validation" / "evals" / "mocks", tmp / "plugin" / "evals" / "mocks")
        out = ROOT / "validation" / "evals" / "results" / f"official-{plugin}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        cmd = [CLAUDE, "plugin", "eval", str(tmp / "plugin"), "--no-publish", "--ablation", "none",
               "--runs", str(args.runs), "--json", str(out), "--allow-tools", "mcp__*", "Bash(python3 *)"]
        if not args.full:
            cmd += ["--tag", "gate"]
        if args.case:
            cmd += ["--case", args.case]
        p = run(cmd, capture=True, timeout=6 * 3600)
        text = (p.stdout or "") + (p.stderr or "")
        print(text.strip()[-1500:])
        shutil.rmtree(tmp, ignore_errors=True)
        # The gate message exactly, and a non-zero exit with it: a substring
        # alone would let any error that mentions early access read as SKIP.
        if p.returncode != 0 and EARLY_ACCESS.search(text):
            say(f"official:{plugin}", "SKIP", "`claude plugin eval` is early access and not enabled for this account")
            continue
        any_ran = True
        ok &= p.returncode == 0
        say(f"official:{plugin}", "PASS" if p.returncode == 0 else "FAIL",
            f"exit {p.returncode}, results in {out.relative_to(ROOT)}")
    return 0 if (ok and any_ran) else (1 if any_ran else 3)


# ---------------------------------------------------------------- modes
def free_stages(args):
    for name, fn in (("static", stage_static), ("scripts", stage_scripts),
                     ("backtest", stage_backtest), ("evals-lint", stage_evals_lint)):
        if name == "backtest" and args.skip_backtest:
            say("backtest", "SKIP", "--skip-backtest")
            continue
        fn()


def pre_push(args, local_sha, base_sha):
    """The hook's entry point, once per commit being pushed. Free stages, then
    the gate evals when plugins/ differs from what the remote has. The runner's
    ledger skips every case already passed against the current files, so a
    push straight after a green `--evals` run costs nothing."""
    free_stages(args)
    if any(st == "FAIL" for _, st, _ in results):
        return 1
    rc, pushed_tree = git("rev-parse", f"{local_sha}:plugins")
    if rc != 0:
        say("evals", "FAIL", f"cannot read plugins/ at {local_sha[:12]}")
        return 1
    if base_sha:
        rc, diff = git("diff", "--name-only", base_sha, local_sha, "--", "plugins/")
        changed = rc != 0 or bool(diff)
    else:
        changed = True
    if not changed:
        say("evals", "PASS", "not required: plugins/ is identical to what the remote already has")
        return 0
    wt = working_plugins_tree()
    if wt != pushed_tree:
        say("evals", "FAIL", "the working tree's plugins/ is not the plugins/ being pushed "
                             "(dirty, or a different branch is checked out) -- the evals would test the wrong files. "
                             "Check out the commit being pushed and run `python3 validation/regress.py --evals` first")
        return 1
    # The ledger fingerprints the WORKING TREE of validation/evals, which never
    # ships, so an uncommitted grader is a local matter -- but a pass recorded
    # against a file that is in no commit cannot be reproduced later. Warn,
    # never refuse (review finding, 9 Sep 2026 PT).
    rc, dirty = git("status", "--porcelain", "--", "validation/evals")
    if rc == 0 and dirty.strip():
        print("note: validation/evals has uncommitted changes; a recorded pass may rest on files "
              "that are in no commit:\n" + "\n".join("      " + l for l in dirty.splitlines()[:12]))
    args.full = False
    return stage_evals(args)


def post_push_guard():
    f = run(["git", "fetch", "origin", "main"], capture=True, timeout=300)
    d = run(["git", "diff", "--stat", "origin/main", "--", "plugins/"], capture=True, timeout=120)
    if f.returncode != 0 or d.returncode != 0:
        say("post-push", "FAIL", "could not compare against origin/main")
        return False
    if (d.stdout or "").strip():
        print(d.stdout)
        say("post-push", "FAIL", "plugins/ differs from origin/main -- this tree is not what shipped")
        return False
    say("post-push", "PASS", "plugins/ is byte-identical to origin/main; testing what shipped")
    return True


def main():
    ap = argparse.ArgumentParser(description="dow-plugins regression gate")
    ap.add_argument("--evals", action="store_true", help="run the skill evals (costs money)")
    ap.add_argument("--full", action="store_true", help="all eval cases, not only the gate tag")
    ap.add_argument("--all", action="store_true", help="rerun cases that already passed against the current files")
    ap.add_argument("--official", action="store_true", help="use `claude plugin eval` for the evals")
    ap.add_argument("--case", help="glob on eval case names")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--parallel", type=int, default=6, help="eval cases run at once")
    ap.add_argument("--model", default="sonnet", help="the model the push gate is judged on")
    ap.add_argument("--models", help="comma list, e.g. haiku,sonnet,opus,claude-fable-5-1: run the selected cases "
                                     "under each; only --model's result gates, the rest are reported")
    ap.add_argument("--judge-model", default="sonnet")
    ap.add_argument("--skip-backtest", action="store_true")
    ap.add_argument("--only", choices=["static", "scripts", "backtest", "evals-lint", "evals"])
    ap.add_argument("--post-push", action="store_true",
                    help="after a push: require plugins/ == origin/main, then run every eval")
    ap.add_argument("--pre-push", nargs=2, metavar=("LOCAL_SHA", "BASE_SHA"),
                    help="the hook's mode: free stages, then gate evals if plugins/ changed vs BASE")
    args = ap.parse_args()
    if args.post_push and args.only:
        ap.error("--post-push runs every stage and every eval; it cannot be combined with --only")

    print(f"dow-plugins regression gate -- {ROOT}")
    if args.pre_push:
        rc = pre_push(args, *args.pre_push)
        print_summary(("PASS" if rc == 0 else "FAIL") + " (pre-push)")
        return rc

    if args.post_push:
        args.evals, args.full, args.all = True, True, True
        if not post_push_guard():
            print_summary("FAIL (post-push)")
            return 1

    def run_evals():
        if args.official:
            return stage_official(args)
        if not args.models:
            return stage_evals(args)
        # The matrix: every model in the list, one ledger entry per model. Only
        # the gate model's result decides the exit code; the others are shown
        # in the summary so a routing miss on a cheaper model is seen, not
        # blocking. Straker, 9 Sep 2026 PT: the plan has the bandwidth.
        gate_model, rc_gate = args.model, 0
        try:
            for m in [x.strip() for x in args.models.split(",") if x.strip()]:
                args.model = m
                rc = stage_evals(args)
                if m == gate_model:
                    rc_gate = rc
                elif results:
                    # WARN, never FAIL: the pass/fail decision below counts only
                    # FAIL rows, so a cheaper model's miss is shown, not blocking
                    # (review finding, 9 Sep 2026 PT).
                    det = results[-1][2]
                    results[-1] = (f"evals[{m}]", "PASS" if rc == 0 else "WARN", det + " (reported, not gating)")
        finally:
            args.model = gate_model
        return rc_gate
    rc_evals = None
    if args.only == "evals":
        rc_evals = run_evals()
    elif args.only:
        {"static": stage_static, "scripts": stage_scripts,
         "backtest": stage_backtest, "evals-lint": stage_evals_lint}[args.only]()
    else:
        free_stages(args)
        if args.evals or args.official:
            rc_evals = run_evals()

    failed = [s for s, st, _ in results if st == "FAIL"]
    if failed:
        print_summary(f"FAIL ({', '.join(failed)})")
        return 2 if rc_evals == 2 else 1

    if rc_evals is None and not args.only:
        changed = plugins_changed()
        if changed:
            print_summary("INCOMPLETE")
            print("plugins/ has changed against origin/main, so the skill evals are required\n"
                  "before /code-review and the push:\n"
                  "    python3 validation/regress.py --evals")
            return 3
        note = " (could not compare against origin/main)" if changed is None else ""
        print_summary(f"free stages pass; evals not requested and plugins/ is unchanged{note}")
        return 0
    if rc_evals == 3:
        print_summary("INCOMPLETE")
        print("The official runner did not run; use --evals for the shim.")
        return 3
    print_summary("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
