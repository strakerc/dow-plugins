#!/usr/bin/env python3
"""Unit tests for the four skill scripts, on synthetic fixtures.

    python3 validation/script_tests.py            # verbose unittest run
    python3 validation/regress.py                 # runs this as one stage

Every fixture is built in code, right here. Nothing is a saved MFL payload:
franchise ids are 0001-0012, owners are one-syllable placeholders, players are
"Player A" and so on. That is deliberate. Invariant 4 keeps league data out of
the repo, and a fixture file that starts synthetic gets "corrected" from a real
payload the first time a test needs one more field. Building them in code keeps
the shape honest (the scripts parse the real envelope) without the content.

Each test pins a behaviour the skill text promises. When one fails, read the
SKILL.md section it names before deciding which side is wrong: the script, the
prose, or the test. Tests are named after the promise, not the function.

The four scripts print for a developer, so most assertions are on stdout text
or the parsed JSON they emit. Runs from any directory; ASCII only, on purpose
(non-ASCII is mangled on the way through some shells here).
"""
import json, os, re, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins" / "dow-league" / "skills"
LM_SKILLS = ROOT / "plugins" / "dow-league-lm" / "skills"
CONTRACTS = SKILLS / "league-contracts" / "scripts" / "contract_options.py"
LEDGER = SKILLS / "league-draft-picks" / "scripts" / "pick_ledger.py"
TIERS = LM_SKILLS / "league-schedule" / "scripts" / "compute_tiers.py"
SCHEDULE = LM_SKILLS / "league-schedule" / "scripts" / "build_schedule.py"

FRANCHISES = ["%04d" % i for i in range(1, 13)]
NAMES = dict(zip(FRANCHISES, ["Ada", "Bram", "Cleo", "Dev", "Esme", "Finn",
                              "Gus", "Hana", "Ivo", "Juno", "Kit", "Lior"]))


def run(script, *args, expect_ok=True):
    """Run a script and return (returncode, stdout, stderr).

    The child is told to write UTF-8. Two scripts print a middle dot, which a
    Windows console encodes as one cp1252 byte; decoding that as UTF-8 here
    made every ledger test error out before it could assert anything.
    """
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run([sys.executable, str(script), *map(str, args)],
                       capture_output=True, text=True, encoding="utf-8", env=env)
    if expect_ok and p.returncode != 0:
        raise AssertionError(f"{script.name} exited {p.returncode}\n{p.stderr}")
    return p.returncode, p.stdout, p.stderr


class Fixture(unittest.TestCase):
    """Base: a temp dir that survives the test method and a JSON writer."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def write(self, name, obj):
        p = self.dir / name
        p.write_text(json.dumps(obj), encoding="utf-8")
        return p


# --------------------------------------------------------------- contracts
def player(pid, salary, info, through, year=1, status="ROSTER", drafted=None):
    p = {"id": str(pid), "salary": str(salary), "contractInfo": info,
         "contractStatus": str(through), "contractYear": str(year),
         "status": status}
    if drafted:
        p["drafted"] = drafted
    return p


def rosters(*players, fid="0001"):
    return {"rosters": {"franchise": [{"id": fid, "player": list(players)}]}}


class ContractOptions(Fixture):
    SEASON = 2027

    def analyse(self, *players, adjustments=None, season=None):
        roster = self.write("roster.json", rosters(*players))
        args = ["--roster", roster, "--season", season or self.SEASON]
        if adjustments is not None:
            adj = self.write("adj.json", {"salaryAdjustments": {"salaryAdjustment": [
                {"franchise_id": "0001", "amount": str(a)} for a in adjustments]}})
            args += ["--adjustments", adj]
        _, out, _ = run(CONTRACTS, *args)
        return json.loads(out)["0001"]

    def by_id(self, result, pid):
        for row in result["decisionsDue"] + result["underContract"]:
            if row["id"] == str(pid):
                return row
        raise AssertionError(f"player {pid} missing from output")

    def option(self, row, name):
        for o in row["options"]:
            if o["option"] == name:
                return o
        raise AssertionError(f"{name!r} not offered; got "
                             f"{[o['option'] for o in row['options']]}")

    # "years remaining = contractStatus - season + 1" -- league-contracts,
    # "The field that misleads everyone".
    def test_contract_status_is_final_year_not_length(self):
        r = self.analyse(player(1, 20, "Long-Term", 2029))
        self.assertEqual(self.by_id(r, 1)["yearsRemaining"], 3)
        r = self.analyse(player(1, 20, "Long-Term", 2027))
        self.assertEqual(self.by_id(r, 1)["yearsRemaining"], 1)

    # "flag every player whose contractStatus equals the season as facing a
    # decision" -- and nobody else.
    def test_decision_due_only_when_contract_ends_this_season(self):
        r = self.analyse(player(1, 20, "Long-Term", 2027),
                         player(2, 20, "Long-Term", 2028))
        self.assertEqual([x["id"] for x in r["decisionsDue"]], ["1"])
        self.assertEqual([x["id"] for x in r["underContract"]], ["2"])

    # The IR asymmetry, tested on a LONG-TERM player as CLAUDE.md insists: a
    # Free Agent would show 25% for both and could not tell a bug from correct
    # behaviour. Cap hit a quarter of salary; cut cost the whole remainder.
    def test_ir_long_term_cap_quarter_cut_full(self):
        r = self.analyse(player(1, 20, "Long-Term", 2028, status="INJURED_RESERVE"))
        row = self.by_id(r, 1)
        self.assertEqual(row["capHit"], 5.0)
        self.assertEqual(row["cutCost"], 40)
        self.assertIn("100%", row["cutNote"])
        self.assertEqual(r["committed"], 5.0)
        # For the floor, IR counts in full.
        self.assertEqual(r["floorCharge"], 20)

    # "A rookie in contract year 1 cuts for nothing."
    def test_rookie_year_one_cuts_free(self):
        r = self.analyse(player(1, 10, "Rookie", 2028, year=1, drafted="1.05 (2026)"))
        self.assertEqual(self.by_id(r, 1)["cutCost"], 0)

    # "Free Agent, or Rookie in year 2: 25%, rest of the current year only."
    def test_rookie_year_two_and_free_agent_cut_at_a_quarter(self):
        r = self.analyse(player(1, 10, "Rookie", 2027, year=2, drafted="1.05 (2026)"),
                         player(2, 8, "Free Agent", 2027))
        self.assertEqual(self.by_id(r, 1)["cutCost"], 3)   # ceil(2.5)
        self.assertEqual(self.by_id(r, 2)["cutCost"], 2)

    # The price ladder: short-term +5 for one year, long-term +10 flat for
    # three, tag reported as the PERSONAL floor only.
    def test_prices_off_an_expiring_normal_contract(self):
        r = self.analyse(player(1, 20, "Long-Term", 2027))
        row = self.by_id(r, 1)
        st, lt, tag = (self.option(row, n) for n in
                       ("Short-term", "Long-term", "Franchise tag"))
        self.assertEqual((st["cost"], st["years"]), (25, 1))
        self.assertEqual((lt["cost"], lt["years"]), (30, 3))
        self.assertEqual(tag["cost"], 25)
        self.assertIn("PERSONAL FLOOR", tag["note"])
        self.assertEqual(self.option(row, "Release")["cost"], 0)

    # "Someone on a plain Short-Term shows the two-year extension, and shows a
    # second short-term explicitly marked NOT LEGAL." No long-term either.
    def test_short_term_dead_end(self):
        r = self.analyse(player(1, 15, "Short-Term", 2027))
        row = self.by_id(r, 1)
        ext = self.option(row, "Short-term extension")
        self.assertEqual((ext["cost"], ext["years"]), (25, 2))
        self.assertIn("30", ext["note"])          # year 2 is +5 more
        again = self.option(row, "Short-term (again)")
        self.assertIsNone(again["cost"])
        self.assertIn("NOT LEGAL", again["note"])
        self.assertNotIn("Long-term", [o["option"] for o in row["options"]])

    # league-rules worked example: drafted at 10 -> short-term 15 -> extension
    # 25 then 30. Two runs, one per step of the ladder.
    def test_rules_worked_example(self):
        r = self.analyse(player(1, 10, "Rookie", 2027, year=2, drafted="1.09 (2025)"))
        self.assertEqual(self.option(self.by_id(r, 1), "Short-term")["cost"], 15)
        r = self.analyse(player(1, 15, "Short-Term", 2028), season=2028)
        ext = self.option(self.by_id(r, 1), "Short-term extension")
        self.assertEqual(ext["cost"], 25)
        self.assertIn("30", ext["note"])

    # After a tag: long-term or the extension; a second tag is never legal two
    # years running; short-term conditional on pre-tag history.
    def test_after_a_franchise_tag(self):
        for spelling in ("Franchise Tag", "Franchise"):
            r = self.analyse(player(1, 61, spelling, 2027))
            row = self.by_id(r, 1)
            self.assertEqual(self.option(row, "Long-term")["cost"], 71)
            self.assertEqual(self.option(row, "Short-term extension")["cost"], 71)
            self.assertIsNone(self.option(row, "Franchise tag (again)")["cost"])
            self.assertIsNone(self.option(row, "Short-term")["cost"])

    # "MFL is inconsistent about Short-Term (Extension) vs Short-Term Ext. --
    # match on a prefix or substring." A completed extension returns to the
    # normal menu; it must NOT be read as a plain short-term, whose menu is the
    # dead end above.
    def test_extension_spellings_return_to_normal_menu(self):
        for spelling in ("Short-Term (Extension)", "Short-Term Ext."):
            r = self.analyse(player(1, 30, spelling, 2027))
            names = [o["option"] for o in self.by_id(r, 1)["options"]]
            self.assertIn("Long-term", names, spelling)
            self.assertIn("Short-term", names, spelling)
            self.assertNotIn("Short-term (again)", names, spelling)

    # Rookie extension [2026, effective 2028]: 1st +5, 2nd +4, 3rd +3, 4th +2.
    def test_rookie_extension_bump_by_round(self):
        for rnd, bump in ((1, 5), (2, 4), (3, 3), (4, 2)):
            r = self.analyse(player(1, 10, "Rookie", 2027, year=2,
                                    drafted=f"{rnd}.03 (2026)"))
            self.assertEqual(self.option(self.by_id(r, 1), "Rookie extension")["cost"],
                             10 + bump, f"round {rnd}")

    # "Run without --adjustments and the output says so and sets
    # adjustmentsSupplied: false." With them, capSpace is net and the two cap
    # figures differ.
    def test_cap_space_net_of_adjustments(self):
        gross = self.analyse(player(1, 20, "Long-Term", 2028))
        self.assertFalse(gross["adjustmentsSupplied"])
        self.assertEqual(gross["capSpace"], gross["capSpaceBeforeAdjustments"])
        self.assertTrue(any("NO SALARY ADJUSTMENTS" in s for s in gross["reminders"]))
        net = self.analyse(player(1, 20, "Long-Term", 2028), adjustments=[5, 7.5])
        self.assertTrue(net["adjustmentsSupplied"])
        self.assertEqual(net["salaryAdjustments"], 12.5)
        self.assertEqual(net["capSpaceBeforeAdjustments"] - net["capSpace"], 12.5)
        self.assertEqual(net["capSpace"], 375 - 12.5 - 20)
        self.assertEqual(net["floorHeadroom"], 20 + 12.5 - 300)

    # Taxi counts 100% against the cap; roster counts split by status.
    def test_roster_counts_and_taxi_at_full(self):
        r = self.analyse(player(1, 20, "Long-Term", 2028),
                         player(2, 6, "Rookie", 2028, status="TAXI_SQUAD"),
                         player(3, 12, "Long-Term", 2028, status="INJURED_RESERVE"))
        self.assertEqual(r["rosterCounts"], {"active": 1, "taxi": 1, "ir": 1})
        self.assertEqual(r["committed"], 20 + 6 + 3)

    def test_franchise_filter_and_bad_id(self):
        roster = self.write("r.json", rosters(player(1, 20, "Long-Term", 2028)))
        _, out, _ = run(CONTRACTS, "--roster", roster, "--season", 2027,
                        "--franchise", "0001")
        self.assertIn("0001", json.loads(out))
        rc, _, err = run(CONTRACTS, "--roster", roster, "--season", 2027,
                         "--franchise", "0099", expect_ok=False)
        self.assertNotEqual(rc, 0)
        self.assertIn("no franchise matched", err)


# ----------------------------------------------------------------- ledger
def full_slate(years=(2027, 2028, 2029)):
    """Every franchise holds its own four picks in every year: 144 picks."""
    return {f: [(y, r, f) for y in years for r in (1, 2, 3, 4)] for f in FRANCHISES}


def picks_payload(held):
    return {"futureDraftPicks": {"franchise": [
        {"id": f, "futureDraftPick": [
            {"year": str(y), "round": str(r), "originalPickFor": o}
            for (y, r, o) in picks]}
        for f, picks in held.items()]}}


class PickLedger(Fixture):
    def ledger(self, held, *extra):
        picks = self.write("picks.json", picks_payload(held))
        names = self.write("names.json", NAMES)
        _, out, _ = run(LEDGER, "--picks", picks, "--names", names, *extra)
        return out

    # "12 franchises x 3 years x 4 rounds must reconcile to 144 picks"
    def test_full_slate_reconciles(self):
        out = self.ledger(full_slate())
        self.assertIn("144 picks", out)
        self.assertIn("integrity: OK  missing=0 unexpected=0 duplicated=0", out)

    # "A failing integrity line means the data moved" -- so it must fail.
    def test_integrity_sees_a_missing_and_a_duplicated_pick(self):
        held = full_slate()
        held["0003"].remove((2028, 2, "0003"))
        self.assertIn("integrity: PROBLEM  missing=1 unexpected=0 duplicated=0",
                      self.ledger(held))
        held = full_slate()
        held["0004"].append((2028, 2, "0004"))
        self.assertIn("integrity: PROBLEM  missing=0 unexpected=0 duplicated=1",
                      self.ledger(held))

    # "The franchise id in a pick's name is its ORIGIN, not its holder."
    # A pick that moved is listed under the holder, attributed to the origin,
    # and the origin's own row says it is gone.
    def test_acquired_pick_attributed_to_origin(self):
        held = full_slate()
        held["0002"].remove((2027, 1, "0002"))
        held["0001"].append((2027, 1, "0002"))
        out = self.ledger(held)
        # The ledger lists holders by pick count, so Ada (13) prints before Bram (11).
        ai, bi = out.index("Ada (0001)"), out.index("Bram (0002)")
        self.assertLess(ai, bi)
        ada = out[ai:bi]
        self.assertIn("holds 13 . own 12 . acquired 1", ada.replace("·", "."))
        self.assertIn("1 (Bram)", ada)
        bram = out[out.index("Bram (0002)"):]
        bram = bram[:bram.index("\n\n")]
        self.assertIn("2027: 2, 3, 4   own gone: [1]", bram)

    # Slot projection: reverse standings, worst record first, PF breaks ties.
    def test_slot_projection_is_reverse_standings(self):
        rows = []
        for i, f in enumerate(FRANCHISES):
            rows.append({"id": f, "h2hw": str(i), "pf": "1500"})
        rows[0]["h2hw"] = rows[1]["h2hw"] = "0"     # tie at the bottom
        rows[0]["pf"], rows[1]["pf"] = "1400", "1300"  # lower PF picks first
        standings = self.write("standings.json", {"leagueStandings": {"franchise": rows}})
        out = self.ledger(full_slate(), "--standings", standings, "--owner", "0002")
        self.assertIn("slot projection from prior regular-season standings", out)
        self.assertRegex(out, r"2027: 1 ~early, 2 ~early")
        out = self.ledger(full_slate(), "--standings", standings, "--owner", "0012")
        self.assertRegex(out, r"2027: 1 ~late")

    # "Only the upcoming three seasons are tradeable."
    def test_tradeable_window_from_season(self):
        out = self.ledger(full_slate(), "--season", 2026)
        self.assertIn("tradeable years from the 2026 offseason: [2027, 2028, 2029]", out)
        out = self.ledger(full_slate(years=(2027, 2028, 2029, 2030)), "--season", 2026)
        self.assertIn("picks present for untradeable years: [2030]", out)

    # The ledger cannot see conditionals, so it must say so every run.
    def test_conditional_reminder_always_printed(self):
        self.assertIn("Conditional picks are INVISIBLE here", self.ledger(full_slate()))


# ------------------------------------------------------------------ tiers
def prior_season(final_two=(("0003", "0010"), ("0002", "0009"))):
    """Twelve franchises with distinct regular-season points, descending by id."""
    fr = {}
    for i, f in enumerate(FRANCHISES):
        fr[f] = {"pf_total": 2400.0 - 60 * i, "post_week14": [100.0, 100.0]}
    return {"season": 2025, "final_two_games": [list(g) for g in final_two],
            "franchises": fr, "names": NAMES}


class ComputeTiers(Fixture):
    def tiers(self, data, *extra, expect_ok=True):
        p = self.write("prior.json", data)
        rc, out, err = run(TIERS, "--data", p, *extra, expect_ok=expect_ok)
        return rc, (json.loads(out) if rc == 0 else None), err

    # "Tier 1: the four teams that played in the final two playoff games -- by
    # playoff finish, NOT by scoring." Make one finalist the lowest scorer.
    def test_tier_one_is_by_playoff_finish_not_points(self):
        d = prior_season()
        d["franchises"]["0010"]["pf_total"] = 900.0
        _, out, _ = self.tiers(d, "--season", 2026)
        self.assertEqual(sorted(out["tiers"]["T1"]), ["0002", "0003", "0009", "0010"])
        self.assertEqual(out["season"], 2026)
        self.assertNotIn("0010", out["tiers"]["T2"] + out["tiers"]["T3"])

    # "MFL's standings pf is not regular-season points ... subtract weeks 15
    # onward before ranking." A team whose raw pf tops the field but whose
    # consolation games supplied it must rank on the net figure.
    def test_tiers_two_and_three_use_regular_season_points(self):
        d = prior_season()
        d["franchises"]["0012"]["pf_total"] = 2500.0       # raw: highest of all
        d["franchises"]["0012"]["post_week14"] = [300.0, 300.0, 300.0]  # net: 1600
        _, out, _ = self.tiers(d)
        self.assertIn("0012", out["tiers"]["T3"])
        self.assertEqual(out["prior_pf"]["0012"], 1600.0)
        self.assertEqual(out["prior_pf"]["0001"], 2200.0)
        self.assertEqual(len(out["tiers"]["T2"]), 4)
        self.assertEqual(len(out["tiers"]["T3"]), 4)
        self.assertEqual(out["rematches"], [["0003", "0010"], ["0002", "0009"]])

    def test_refuses_fewer_than_four_distinct_finalists(self):
        d = prior_season(final_two=(("0003", "0010"), ("0003", "0009")))
        rc, _, err = self.tiers(d, expect_ok=False)
        self.assertNotEqual(rc, 0)
        self.assertIn("must name 4 distinct franchises", err)

    # "warns when the Tier 2/3 margin is tight"
    def test_tight_margin_warning(self):
        d = prior_season()
        for f in FRANCHISES:
            d["franchises"][f]["pf_total"] = 2000.0     # all equal: margin 0
        _, out, err = self.tiers(d)
        self.assertIn("TIGHT", err)
        self.assertEqual(out["_working"]["tier2_tier3_margin"], 0)


# --------------------------------------------------------------- schedule
class BuildSchedule(Fixture):
    def config(self, **over):
        p = self.write("prior.json", prior_season())
        _, out, _ = run(TIERS, "--data", p, "--season", 2026)
        cfg = json.loads(out)
        cfg.update(over)
        return self.write("season.json", cfg)

    def build(self, cfg, *extra, expect_ok=True):
        return run(SCHEDULE, "--config", cfg, *extra, expect_ok=expect_ok)

    @staticmethod
    def import_rows(out):
        return re.findall(r"^\d{2},\d{4},\d{4}$", out, re.M)

    # "It prints eight checks ... A schedule that fails a check is a bug."
    def test_eight_checks_pass_and_block_has_84_rows(self):
        _, out, _ = self.build(self.config(), "--seed", 7)
        self.assertEqual(out.count("[PASS]"), 8)
        self.assertEqual(out.count("[FAIL]"), 0)
        rows = self.import_rows(out)
        self.assertEqual(len(rows), 84)
        weeks = {int(r[:2]) for r in rows}
        self.assertEqual(weeks, set(range(1, 15)))
        # Every franchise appears in the block exactly 14 times, 7 at home.
        for f in FRANCHISES:
            self.assertEqual(sum(r.endswith("," + f) for r in rows), 7, f)
            self.assertEqual(sum(r.split(",")[1] == f for r in rows), 7, f)

    # Same seed, same schedule. This is what makes a generator diff reviewable.
    def test_seed_makes_it_reproducible(self):
        cfg = self.config()
        _, a, _ = self.build(cfg, "--seed", 11)
        _, b, _ = self.build(cfg, "--seed", 11)
        self.assertEqual(self.import_rows(a), self.import_rows(b))
        _, c, _ = self.build(cfg, "--seed", 12)
        self.assertNotEqual(self.import_rows(a), self.import_rows(c))

    # "asserts both week-1 rematch teams are Tier 1 -- the assertion that would
    # have caught the 2026 error."
    def test_rematch_outside_tier_one_is_refused(self):
        cfg = self.config(rematches=[["0003", "0010"], ["0002", "0001"]])
        rc, _, err = self.build(cfg, "--seed", 7, expect_ok=False)
        self.assertNotEqual(rc, 0)
        self.assertIn("both rematch teams must be Tier 1", err)

    # Opponent strength is a disclosure. Comparing a schedule against itself
    # must read all-zero and say why; a truncated file must be refused rather
    # than produce a partial delta.
    def test_compare_against_itself_and_against_a_truncated_block(self):
        cfg = self.config()
        _, out, _ = self.build(cfg, "--seed", 7)
        rows = self.import_rows(out)
        same = self.dir / "live.txt"
        same.write_text("\n".join(rows) + "\n", encoding="utf-8")
        _, out2, _ = self.build(cfg, "--seed", 7, "--compare", same)
        self.assertIn("All zero, which is correct", out2)
        short = self.dir / "short.txt"
        short.write_text("\n".join(rows[:40]) + "\n", encoding="utf-8")
        _, out3, _ = self.build(cfg, "--seed", 7, "--compare", short)
        self.assertIn("CANNOT COMPARE", out3)
        self.assertIn("Delta suppressed", out3)
        self.assertNotIn("report this to the league", out3)

    # Without prior_pf the report says so and skips rather than guessing.
    def test_opponent_strength_skips_without_prior_pf(self):
        cfg = self.config(prior_pf={})
        _, out, _ = self.build(cfg, "--seed", 7)
        self.assertIn("SKIPPED: the config has no `prior_pf`", out)
        self.assertEqual(out.count("[PASS]"), 8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
