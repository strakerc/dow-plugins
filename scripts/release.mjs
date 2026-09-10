#!/usr/bin/env node
/**
 * release.mjs — the intentional publish for dow-plugins.
 *
 * PROJECT COPY. Canonical location once the repo has it: dow-plugins/scripts/release.mjs
 * Two copies drift. Change both in the same sitting; the repo wins on disagreement.
 *
 * WHY THIS EXISTS
 * ---------------
 * WRITTEN on the belief that `version` in plugin.json gates delivery. It does not.
 * Measured 9 Sep 2026 PT: a marketplace sync delivered a skill added under
 * plugins/ with NO version bump on either manifest, into a live account.
 * Delivery follows the FILE CHANGE. Pushing to main is the publish; this
 * script is not.
 *
 * Two purposes survive the correction. It reports what has shipped since the
 * last release tag, the only record of what owners actually received; and it
 * moves both manifests and the CHANGELOG together, so the version string stays
 * an honest label for a release even though it does not gate one.
 *
 * Do not restore the old claim. It is why league-lineup was believed to be held
 * back while it was already live in an account.
 *
 *   node release.mjs                 # report: current versions + what is unreleased
 *   node release.mjs 0.2.0           # dry run for that version
 *   node release.mjs 0.2.0 --commit  # write the files
 *
 * Writes files only. It does not git commit, tag or push — those stay a human act,
 * because "what shipped" should be reviewable before it is irreversible.
 */

import { readFileSync, writeFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { execSync } from "node:child_process";

const ROOT = process.env.DOW_PLUGINS_ROOT || process.cwd();
const PLUGINS = ["dow-league", "dow-league-lm"];
const SEMVER = /^\d+\.\d+\.\d+$/;
// Present once the staleness check ships; absent until then. Both cases are fine.
const STAMP = /^\*Plugin version .+\.\*$/m;

const [, , versionArg, ...flags] = process.argv;
const commit = flags.includes("--commit");

function fail(msg) { console.error(`\n  FAILED: ${msg}\n`); process.exit(1); }

function manifestPath(p) {
  const a = join(ROOT, "plugins", p, ".claude-plugin", "plugin.json");
  if (existsSync(a)) return a;
  fail(`no plugin.json for ${p} under ${ROOT}. Run from the repo root or set DOW_PLUGINS_ROOT.`);
}

function skillFiles(p) {
  const dir = join(ROOT, "plugins", p, "skills");
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .map((d) => join(dir, d, "SKILL.md"))
    .filter((f) => existsSync(f) && statSync(f).isFile());
}

// ---------------------------------------------------------------- read state
const state = PLUGINS.map((p) => {
  const mf = manifestPath(p);
  const json = JSON.parse(readFileSync(mf, "utf8"));
  return { plugin: p, manifestPath: mf, json, current: json.version, skills: skillFiles(p) };
});

console.log(`\n  dow-plugins release — root ${resolve(ROOT)}\n`);
for (const s of state) {
  const stamped = s.skills.filter((f) => STAMP.test(readFileSync(f, "utf8"))).length;
  console.log(`  ${s.plugin.padEnd(15)} plugin.json ${String(s.current).padEnd(8)} ` +
              `${s.skills.length} skills, ${stamped} stamped`);
}

// ------------------------------------------------- what is waiting to ship
// "Is a release pending?" should be answerable mechanically, not from memory.
function unreleased() {
  const git = (cmd) => execSync(cmd, { cwd: ROOT, stdio: ["ignore", "pipe", "ignore"] }).toString().trim();
  let tag;
  try { tag = git(`git describe --tags --abbrev=0 --match "v*"`); }
  catch { return { tag: null, commits: null }; }
  try {
    const out = git(`git log ${tag}..HEAD --oneline -- plugins/`);
    return { tag, commits: out ? out.split("\n") : [] };
  } catch { return { tag, commits: null }; }
}

const u = unreleased();
if (u.commits === null) {
  console.log(`\n  No release tag found (or not a git repo) — cannot tell what is unreleased.`);
  console.log(`  After the first release, tag it \`v<version>\` so this works from then on.`);
} else if (u.commits.length === 0) {
  console.log(`\n  Nothing unreleased. No plugin change since ${u.tag}.`);
} else {
  console.log(`\n  UNTAGGED — ${u.commits.length} commit(s) touching plugins/ since ${u.tag}:\n`);
  for (const c of u.commits.slice(0, 15)) console.log(`    ${c}`);
  if (u.commits.length > 15) console.log(`    … and ${u.commits.length - 15} more`);
  console.log(`\n  These are LIVE. Measured 9 Sep 2026 PT: a marketplace sync delivers a changed file under plugins/ to every installed owner, with no version bump required. UNTAGGED means no release tag records them -- not that they are unshipped.`);
}

const currents = [...new Set(state.map((s) => s.current))];
if (currents.length > 1) {
  console.log(`\n  NOTE: the two plugins are on different versions (${currents.join(", ")}).`);
  console.log(`  That is legal but it means nobody can state "the" version. This run aligns them.`);
}

if (!versionArg) {
  console.log(`\n  No version given — nothing written.`);
  if (u.commits && u.commits.length) console.log(`  To publish the above:  node release.mjs <version> --commit`);
  console.log("");
  process.exit(0);
}
if (!SEMVER.test(versionArg)) fail(`"${versionArg}" is not x.y.z`);

// Refuse to go backwards or sideways. Neither guard is about delivery -- the push
// already delivered. They protect the version string's job as a LABEL: if two
// different sets of files ever ship as 0.2.0, no one can say afterwards which one
// a given owner received.
const cmp = (a, b) => {
  const [A, B] = [a, b].map((v) => v.split(".").map(Number));
  for (let i = 0; i < 3; i++) if (A[i] !== B[i]) return A[i] - B[i];
  return 0;
};
for (const s of state) {
  if (cmp(versionArg, s.current) === 0) fail(`${s.plugin} is already ${versionArg}. Reusing a version string makes it a dishonest label: two different sets of files ship under one name, and nothing can then say which one an owner has.`);
  if (cmp(versionArg, s.current) < 0) fail(`${versionArg} is lower than ${s.plugin}'s ${s.current}. Going backwards makes the version string unreadable as history -- the files still ship either way.`);
}

// ---------------------------------------------------------------- plan edits
const edits = [];
for (const s of state) {
  const raw = readFileSync(s.manifestPath, "utf8");
  if (!raw.includes(`"version"`)) fail(`${s.plugin}'s plugin.json has no version field. Add one before releasing.`);
  // Textual replace, not JSON.stringify — preserves the file's own formatting.
  const next = raw.replace(/("version"\s*:\s*")[^"]+(")/, `$1${versionArg}$2`);
  if (next === raw) fail(`could not rewrite the version in ${s.manifestPath}`);
  edits.push({ file: s.manifestPath, next, what: `plugin.json ${s.current} -> ${versionArg}` });

  for (const f of s.skills) {
    const txt = readFileSync(f, "utf8");
    if (!STAMP.test(txt)) continue;           // not stamped yet — that is fine
    const line = `*Plugin version ${versionArg}.*`;
    const out = txt.replace(STAMP, line);
    if (out !== txt) edits.push({ file: f, next: out, what: `stamp -> ${versionArg}` });
  }
}

const CHANGELOG = join(ROOT, "CHANGELOG.md");
const today = new Intl.DateTimeFormat("en-CA", {
  timeZone: "America/Los_Angeles", year: "numeric", month: "2-digit", day: "2-digit",
}).format(new Date());                          // Pacific, per the project date rule
const entry = `## ${versionArg} — ${today} PT\n\n- _describe what shipped_\n\n`;
edits.push({
  file: CHANGELOG,
  next: existsSync(CHANGELOG)
    ? readFileSync(CHANGELOG, "utf8").replace(/^(# .*\n\n)?/, (m) => (m || "# Changelog\n\n") + entry)
    : `# Changelog\n\n${entry}`,
  what: existsSync(CHANGELOG) ? `prepend ${versionArg}` : `create with ${versionArg}`,
});

console.log(`\n  ${commit ? "WRITING" : "DRY RUN"} — ${edits.length} file(s)\n`);
for (const e of edits) console.log(`    ${e.what.padEnd(28)} ${e.file.replace(ROOT, ".")}`);

if (!commit) {
  console.log(`\n  Nothing written. Re-run with --commit.\n`);
  process.exit(0);
}
for (const e of edits) writeFileSync(e.file, e.next);

console.log(`
  Written. Now, by hand and in this order:

    1. Fill in the CHANGELOG entry. A version with no record of what it contains
       is a number nobody trusts.
    2. git add -A && git commit -m "release ${versionArg}"
    3. git tag v${versionArg} && git push && git push --tags
    4. Confirm a real client picks it up before telling anyone it is out.
       Reading the repo back proves the push, not the delivery.
`);
