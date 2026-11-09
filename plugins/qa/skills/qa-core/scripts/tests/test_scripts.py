"""Tests for the qa plugin scripts. Run: python3 -m unittest discover -s scripts/tests"""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mutants  # noqa: E402
import seal  # noqa: E402
import traceability  # noqa: E402


def _quiet(fn, *args):
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
        code = fn(*args)
    return code, out.getvalue(), err.getvalue()


def _git_init(d: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main", str(d)], check=True)
    for k, v in (("user.email", "t@t"), ("user.name", "t"), ("commit.gpgsign", "false")):
        subprocess.run(["git", "-C", str(d), "config", k, v], check=True)


def _commit(d: Path, msg: str = "c") -> None:
    subprocess.run(["git", "-C", str(d), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(d), "commit", "-qm", msg], check=True)


# ---------------------------------------------------------------- seal

class TestSeal(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "acceptance/feat").mkdir(parents=True)
        (self.root / "acceptance/feat/SC-01-register.hurl").write_text("GET {{base_url}}/x\nHTTP 200\n")
        (self.root / "acceptance/feat/limits.feature").write_text("Scenario: SC-02 limit\n")
        (self.root / "docs/agents").mkdir(parents=True)
        (self.root / "docs/agents/qa.md").write_text("command: make r1\n")
        self.seal = self.root / "acceptance/feat/.qa-seal.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _seal(self):
        return seal.seal(self.seal, self.root, ["acceptance/feat", "docs/agents/qa.md"], "design approved", "qa")

    def test_seal_and_verify_intact(self):
        data = self._seal()
        self.assertTrue(seal.verify(self.seal, self.root)["intact"])
        self.assertEqual(len(data["files"]), 3)
        self.assertNotIn("acceptance/feat/.qa-seal.json", data["files"], "the seal does not seal itself")

    def test_detects_modification_deletion_and_new_file(self):
        self._seal()
        (self.root / "acceptance/feat/SC-01-register.hurl").write_text("GET {{base_url}}/x\nHTTP 404\n")
        (self.root / "acceptance/feat/limits.feature").unlink()
        (self.root / "acceptance/feat/SC-09-new.hurl").write_text("x")
        rep = seal.verify(self.seal, self.root)
        self.assertFalse(rep["intact"])
        self.assertEqual(rep["modified"], ["acceptance/feat/SC-01-register.hurl"])
        self.assertEqual(rep["deleted"], ["acceptance/feat/limits.feature"])
        self.assertEqual(rep["new"], ["acceptance/feat/SC-09-new.hurl"])

    def test_changing_the_configured_command_breaks_the_seal(self):
        self._seal()
        (self.root / "docs/agents/qa.md").write_text("command: make r1 TAGS=~@slow\n")
        self.assertEqual(seal.verify(self.seal, self.root)["modified"], ["docs/agents/qa.md"])

    def test_node_modules_and_pycache_are_not_ignored(self):
        self._seal()
        (self.root / "acceptance/feat/node_modules/@playwright/test").mkdir(parents=True)
        (self.root / "acceptance/feat/node_modules/@playwright/test/index.js").write_text("cheat")
        self.assertFalse(seal.verify(self.seal, self.root)["intact"])

    def test_symbolic_link_breaks_the_seal(self):
        self._seal()
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "steps.go").write_text("x")
        os.symlink(outside, self.root / "acceptance/feat/steps")
        rep = seal.verify(self.seal, self.root)
        self.assertFalse(rep["intact"])
        self.assertEqual(rep["links"], ["acceptance/feat/steps"])
        with self.assertRaises(seal.UsageError):
            seal.reseal(self.seal, self.root, [], "F-01: x", "qa")

    def test_required_paths_must_be_sealed(self):
        seal.seal(self.seal, self.root, ["acceptance/feat"], "design", "qa")
        rep = seal.verify(self.seal, self.root, required=["docs/agents/qa.md", "acceptance/feat/limits.feature"])
        self.assertEqual(rep["required_not_sealed"], ["docs/agents/qa.md"])
        self.assertFalse(rep["intact"])

    def test_no_double_seal_and_no_seal_without_reason(self):
        with self.assertRaises(seal.UsageError):
            seal.seal(self.seal, self.root, ["acceptance/feat"], "  ", "qa")
        self._seal()
        with self.assertRaises(seal.UsageError):
            seal.seal(self.seal, self.root, ["acceptance/feat"], "again", "qa")

    def test_reseal_requires_reason_and_keeps_history(self):
        self._seal()
        (self.root / "acceptance/feat/SC-01-register.hurl").write_text("change")
        with self.assertRaises(seal.UsageError):
            seal.reseal(self.seal, self.root, [], "", "qa")
        data, changes = seal.reseal(self.seal, self.root, [], "E-02: test fixed", "qa")
        self.assertEqual(changes["modified"], ["acceptance/feat/SC-01-register.hurl"])
        self.assertEqual([e["action"] for e in data["history"]], ["seal", "reseal"])
        self.assertTrue(seal.verify(self.seal, self.root)["intact"])

    def test_path_outside_the_root_is_an_error(self):
        with self.assertRaises(seal.UsageError):
            seal.seal(self.seal, self.root, ["../"], "x", "qa")

    def test_cli_exit_codes(self):
        base = ["--seal", str(self.seal), "--root", str(self.root)]
        self.assertEqual(_quiet(seal.main, ["verify", *base])[0], 2, "no seal is a usage error")
        self.assertEqual(_quiet(seal.main, ["seal", *base, "--reason", "initial", "acceptance/feat"])[0], 0)
        self.assertEqual(_quiet(seal.main, ["verify", *base])[0], 0)
        (self.root / "acceptance/feat/limits.feature").write_text("edited by the dev")
        code, out, _ = _quiet(seal.main, ["verify", *base])
        self.assertEqual(code, 1)
        self.assertIn("SEAL BROKEN", out)


class TestSealAgainstBase(unittest.TestCase):
    """The agent that edits and reseals does not go unnoticed."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        _git_init(self.root)
        (self.root / "acceptance/feat").mkdir(parents=True)
        (self.root / "acceptance/feat/SC-01.hurl").write_text("HTTP 409\n")
        self.seal = self.root / "acceptance/feat/.qa-seal.json"
        seal.seal(self.seal, self.root, ["acceptance/feat"], "design approved", "qa")
        _commit(self.root, "base")
        subprocess.run(["git", "-C", str(self.root), "checkout", "-qb", "feature"], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_reseal_without_reference_breaks_against_base(self):
        (self.root / "acceptance/feat/SC-01.hurl").write_text("HTTP 422\n")
        seal.reseal(self.seal, self.root, [], "tweak", "dev")
        self.assertTrue(seal.verify(self.seal, self.root)["intact"], "without a base, the reseal passes…")
        rep = seal.verify(self.seal, self.root, base="main")
        self.assertFalse(rep["intact"], "…but against the base it shows")
        self.assertEqual(len(rep["reseals_since_base"]), 1)

    def test_reseal_with_reference_is_listed_for_review(self):
        (self.root / "acceptance/feat/SC-01.hurl").write_text("HTTP 422\n")
        seal.reseal(self.seal, self.root, [], "E-03: the criterion changed", "qa")
        rep = seal.verify(self.seal, self.root, base="main")
        self.assertTrue(rep["intact"])
        self.assertEqual(rep["reseals_since_base"][0]["reason"], "E-03: the criterion changed")

    def test_deleting_and_recreating_the_seal_is_detected(self):
        self.seal.unlink()
        (self.root / "acceptance/feat/SC-01.hurl").write_text("HTTP 422\n")
        seal.seal(self.seal, self.root, ["acceptance/feat"], "new", "dev")
        rep = seal.verify(self.seal, self.root, base="main")
        self.assertFalse(rep["intact"])
        self.assertIn("seal history was rewritten", " ".join(rep["base_problems"]))

    def test_deleting_the_seal_is_detected(self):
        self.seal.unlink()
        rep = seal.verify(self.seal, self.root, base="main")
        self.assertFalse(rep["intact"])

    def test_new_feature_without_seal_on_base(self):
        other = self.root / "acceptance/new/.qa-seal.json"
        (self.root / "acceptance/new").mkdir()
        (self.root / "acceptance/new/SC-01.hurl").write_text("x")
        seal.seal(other, self.root, ["acceptance/new"], "design", "qa")
        rep = seal.verify(other, self.root, base="main")
        self.assertTrue(rep["intact"])
        self.assertEqual(len(rep["reseals_since_base"]), 1, "everything is listed for human review")

    def test_missing_base_is_an_error(self):
        with self.assertRaises(seal.UsageError):
            seal.verify(self.seal, self.root, base="does-not-exist")


# ---------------------------------------------------------------- traceability

CRITERIA = textwrap.dedent("""\
    # Criteria
    Status: approved

    ## AC-01: register device
    - Oracle: listing

    ## AC-02: device limit
    - Oracle: 409

    ### AC-03: token works for the SDK
    - Oracle: SDK initialized

    ## AC-04: old idea
    - Status: discarded

    ```markdown
    ## AC-99: example inside a code block, does not count
    ```
    """)

SCENARIOS = textwrap.dedent("""\
    # Scenarios

    | ID | Criterion | Technique | Rung | Scenario | Oracle | Status |
    |---|---|---|---|---|---|---|
    | SC-01 | AC-01 | partitions | 1 | register | listing | active |
    | SC-02 | AC-02 | boundaries | 1, 4 | fifth | 409 \\| listing | active |
    | SC-03 | AC-02, AC-01 | boundaries | 1 | fourth | 201 | active |
    | SC-04 | AC-03 | walking skeleton | 3 | sdk | sdk ok | active |
    | SC-05 | AC-02 | failure | 1 | timeout | 503 | blocked-testability |
    | SC-06 | AC-01 | x | 1 | old | x | discarded |
    | SC-07 | AC-04 | x | 1 | pruned by risk | x | discarded |

    ### SC-02
    Detail with an SC-99 mentioned in prose, which must not be parsed as a row.
    """)


def _junit(cases: list[tuple[str, str]]) -> str:
    parts = ['<?xml version="1.0"?><testsuites><testsuite name="s">']
    for name, res in cases:
        child = {"failed": "<failure message='x'/>", "skipped": "<skipped/>", "error": "<error/>"}.get(res, "")
        parts.append(f'<testcase classname="acceptance" name="{name}">{child}</testcase>')
    parts.append("</testsuite></testsuites>")
    return "".join(parts)


GREEN_R1 = [("SC-01 register", "passed"), ("SC-02 fifth #1", "passed"),
            ("SC-02 fifth #2", "passed"), ("SC-03 fourth", "passed")]


class TestTraceability(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        (self.d / "criteria.md").write_text(CRITERIA)
        (self.d / "scenarios.md").write_text(SCENARIOS)
        self.src = self.d / "acceptance"
        self.src.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *extra):
        return _quiet(traceability.main, ["--criteria", str(self.d / "criteria.md"),
                                          "--scenarios", str(self.d / "scenarios.md"), "--json", *extra])

    def _rep(self, cases, name="r.xml"):
        rep = self.d / name
        rep.write_text(_junit(cases))
        return rep

    def test_basic_parsing(self):
        self.assertEqual(traceability.read_criteria(CRITERIA), (["AC-01", "AC-02", "AC-03"], ["AC-04"]))
        sc = traceability.read_scenarios(SCENARIOS)
        self.assertEqual([s.id for s in sc], [f"SC-0{i}" for i in range(1, 8)])
        self.assertEqual(sc[1].rungs, [1, 4])
        self.assertEqual(sc[2].criteria, ["AC-02", "AC-01"])

    def test_declaration_only_is_complete(self):
        code, out, _ = self._run()
        self.assertEqual(code, 0, out)
        self.assertTrue(any("SC-05" in w for w in json.loads(out)["warnings"]))

    def test_criterion_without_scenario_and_missing_reference(self):
        (self.d / "criteria.md").write_text(CRITERIA + "\n## AC-05: new\n")
        (self.d / "scenarios.md").write_text(SCENARIOS.replace("| SC-01 | AC-01 |", "| SC-01 | AC-01, AC-09 |"))
        code, out, _ = self._run()
        gaps = json.loads(out)["gaps"]
        self.assertEqual(code, 1)
        self.assertIn("AC-05 has no scenario", gaps)
        self.assertTrue(any("AC-09" in g for g in gaps))

    def test_active_scenario_on_discarded_criterion(self):
        (self.d / "scenarios.md").write_text(SCENARIOS.replace("| x | 1 | pruned by risk | x | discarded |",
                                                               "| x | 1 | pruned by risk | x | active |"))
        code, out, _ = self._run()
        self.assertEqual(code, 1)
        self.assertTrue(any("AC-04, which is discarded" in g for g in json.loads(out)["gaps"]))

    def test_criterion_with_only_blocked_scenarios_has_no_coverage(self):
        sc = SCENARIOS.replace("| 3 | sdk | sdk ok | active |", "| 3 | sdk | sdk ok | blocked-testability |")
        (self.d / "scenarios.md").write_text(sc)
        code, out, _ = self._run()
        self.assertEqual(code, 1)
        self.assertTrue(any("AC-03 only has scenarios blocked" in g for g in json.loads(out)["gaps"]))

    def test_sources_only_count_titles_and_names(self):
        (self.src / "SC-01-register.hurl").write_text("x")
        (self.src / "limits.feature").write_text(
            "Scenario: SC-02 fifth\nScenario: SC-77 invented\n# this step also covers SC-03\n")
        (self.src / "helper.go").write_text("// covers SC-03\nfunc x() {}\n")
        (self.src / "mapping.json").write_text('{"SC-03": true}')
        code, out, _ = self._run("--sources", str(self.src), "--rungs", "1")
        gaps = json.loads(out)["gaps"]
        self.assertEqual(code, 1)
        self.assertTrue(any(g.startswith("SC-03") and "is not implemented" in g for g in gaps),
                        "a comment or a JSON file does not implement a scenario")
        self.assertTrue(any(g.startswith("SC-77") for g in gaps))
        self.assertFalse(any(g.startswith("SC-04") for g in gaps), "SC-04 is rung 3, out of scope")

    def test_sources_go_playwright_and_localized_gherkin(self):
        (self.src / "a_test.go").write_text('t.Run("SC-01 register", func(t *testing.T) {})\n')
        (self.src / "b.spec.ts").write_text("test('SC-02 fifth', async () => {})\ntest.describe('SC-03 fourth', () => {})\n")
        (self.src / "c.feature").write_text("# language: es\nEscenario: SC-04 sdk\n")
        self.assertEqual(set(traceability.scan_sources([self.src])), {"SC-01", "SC-02", "SC-03", "SC-04"})

    def test_junit_all_green_on_rung_1(self):
        (self.d / "scenarios.md").write_text(SCENARIOS.replace("| SC-04 | AC-03 | walking skeleton | 3 |",
                                                               "| SC-04 | AC-03 | walking skeleton | 1, 3 |"))
        rep = self._rep(GREEN_R1 + [("SC-04 sdk", "passed")])
        code, out, _ = self._run("--junit", str(rep), "--rungs", "1")
        self.assertEqual(code, 0, out)

    def test_criterion_whose_scenarios_are_on_another_rung_is_not_green(self):
        """The PayPal case: if rung 3 does not run, the walking skeleton cannot come out green."""
        rep = self._rep(GREEN_R1)
        code, out, _ = self._run("--junit", str(rep), "--rungs", "1")
        self.assertEqual(code, 1)
        self.assertTrue(any(g.startswith("AC-03 has no evidence in scope") for g in json.loads(out)["gaps"]))

    def test_empty_scope_is_an_error(self):
        rep = self._rep(GREEN_R1)
        self.assertEqual(self._run("--junit", str(rep), "--rungs", "5")[0], 2)
        self.assertEqual(self._run("--junit")[0], 2, "--junit without reports is an error")

    def test_junit_skipped_failed_and_not_run_are_not_green(self):
        rep = self._rep([("SC-01 register", "skipped"), ("SC-02 fifth #1", "passed"),
                         ("SC-02 fifth #2", "failed"), ("TestWithoutID", "passed")])
        code, out, _ = self._run("--junit", str(rep), "--rungs", "1")
        r = json.loads(out)
        self.assertEqual(code, 1)
        self.assertTrue(any("SC-01 was skipped" in g for g in r["gaps"]))
        self.assertTrue(any("SC-02 failed" in g for g in r["gaps"]), "a single red outline row is enough")
        self.assertTrue(any("SC-03 does not appear" in g for g in r["gaps"]))
        self.assertTrue(any("TestWithoutID" in w for w in r["warnings"]))

    def test_one_case_cannot_cover_several_scenarios(self):
        rep = self._rep([("smoke SC-01 SC-02 SC-03", "passed")])
        code, out, _ = self._run("--junit", str(rep), "--ids", "SC-01,SC-02,SC-03")
        r = json.loads(out)
        self.assertEqual(code, 1)
        self.assertTrue(any("several scenario IDs" in g for g in r["gaps"]))
        self.assertTrue(any("SC-01 does not appear" in g for g in r["gaps"]))

    def test_go_names_with_underscore(self):
        rep = self._rep([("TestAcceptance/SC-01_register", "passed"), ("TestAcceptance/SC-02_fifth", "passed"),
                         ("TestAcceptance/SC-03_fourth", "passed")])
        results, without_id, _ = traceability.read_junit([rep])
        self.assertEqual(set(results), {"SC-01", "SC-02", "SC-03"})
        self.assertEqual(without_id, [])

    def test_sc_01_is_not_confused_with_sc_010(self):
        rep = self._rep([("SC-010 something", "passed")])
        results, _, _ = traceability.read_junit([rep])
        self.assertNotIn("SC-01", results)

    def test_report_older_than_the_run_is_rejected(self):
        rep = self._rep(GREEN_R1)
        old = time.time() - 3600
        os.utime(rep, (old, old))
        self.assertEqual(self._run("--junit", str(rep), "--rungs", "1", "--since", str(time.time() - 60))[0], 2)

    def test_per_slice_cadence_with_ids(self):
        rep = self._rep([("SC-02 fifth", "passed"), ("SC-03 fourth", "passed")])
        code, out, _ = self._run("--junit", str(rep), "--ids", "SC-02,SC-03")
        self.assertEqual(code, 0, out)
        crit = [c["criterion"] for c in json.loads(out)["coverage"]]
        self.assertEqual(crit, ["AC-01", "AC-02"], "only the criteria of those scenarios")
        self.assertEqual(self._run("--junit", str(rep), "--ids", "SC-42")[0], 2)

    def test_expect_red_before_implementing(self):
        rep = self._rep([("SC-01 register", "failed"), ("SC-02 fifth", "failed"), ("SC-03 fourth", "passed")])
        code, out, _ = self._run("--junit", str(rep), "--rungs", "1", "--expect-red")
        r = json.loads(out)
        self.assertEqual(code, 0, out)
        self.assertTrue(any("SC-03 is GREEN before implementing" in w for w in r["warnings"]))
        rep2 = self._rep([("SC-01 register", "failed")], "r2.xml")
        self.assertEqual(self._run("--junit", str(rep2), "--rungs", "1", "--expect-red")[0], 1,
                         "anything not executed is still a gap even when red is expected")

    def test_invalid_formats_are_errors(self):
        bad = [
            SCENARIOS.replace("| SC-01 | AC-01 | partitions | 1 |", "| SC-1 | AC-01 | partitions | 1 |"),
            SCENARIOS.replace("| SC-01 | AC-01 | partitions | 1 |", "| SC-01 | AC-1 | partitions | 1 |"),
            SCENARIOS.replace("| SC-01 | AC-01 | partitions | 1 |", "| SC-01 | AC-01 | partitions | 9 |"),
            SCENARIOS.replace("| active |\n| SC-02", "| green |\n| SC-02"),
            SCENARIOS.replace("| SC-03 | AC-02, AC-01 |", "| SC-03 | none |"),
            SCENARIOS.replace("| SC-03 |", "| SC-02 |"),
            SCENARIOS.replace("| Rung |", "| Level |"),
        ]
        for text in bad:
            (self.d / "scenarios.md").write_text(text)
            self.assertEqual(self._run()[0], 2, text[:300])
        (self.d / "scenarios.md").write_text(SCENARIOS)
        for crit in ("# nothing", "## AC-1: short\n"):
            (self.d / "criteria.md").write_text(crit)
            self.assertEqual(self._run()[0], 2, crit)

    def test_plural_headers(self):
        text = SCENARIOS.replace("| ID | Criterion | Technique | Rung |", "| ID | Criteria | Technique | Rungs |")
        self.assertEqual(len(traceability.read_scenarios(text)), 7)


# ---------------------------------------------------------------- mutants

CHECK = textwrap.dedent("""\
    import os, sys
    from app import limit
    ok = limit(4) and not limit(5)
    rep = os.environ.get("QA_REPORTS")
    if rep:
        failure = "" if ok else "<failure message='limit'/>"
        open(os.path.join(rep, "r.xml"), "w").write(
            f'<testsuite><testcase name="SC-01 limit">{failure}</testcase></testsuite>')
    sys.exit(0 if ok else 1)
    """)


def _repo(dir_: Path) -> Path:
    _git_init(dir_)
    (dir_ / "app.py").write_text("def limit(n):\n    return n < 5\n")
    (dir_ / "check.py").write_text(CHECK)
    (dir_ / "acceptance").mkdir()
    (dir_ / "acceptance/SC-01.txt").write_text("oracle")
    (dir_ / ".gitignore").write_text("ignored.txt\n")
    _commit(dir_, "init")
    return dir_


def _patch(repo: Path, new: str, file: str = "app.py") -> str:
    """Builds the patch the way the skill says: diff -u of the current file against an edited copy."""
    with tempfile.TemporaryDirectory() as t:
        copy = Path(t) / Path(file).name
        copy.write_text(new)
        r = subprocess.run(["diff", "-u", "--label", f"a/{file}", "--label", f"b/{file}",
                            str(repo / file), str(copy)], capture_output=True, text=True)
    assert r.returncode == 1, r.stderr
    return r.stdout


class TestMutants(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = _repo(Path(self.tmp.name) / "repo")
        self.patches = Path(self.tmp.name) / "patches"
        self.patches.mkdir()
        self.cmd = f"{sys.executable} check.py"

    def tearDown(self):
        self.tmp.cleanup()

    def _status(self):
        return subprocess.run(["git", "-C", str(self.repo), "status", "--porcelain"],
                              capture_output=True, text=True).stdout

    def _p(self, name, content):
        p = self.patches / name
        p.write_text(content)
        return p

    def test_results_without_touching_the_repo(self):
        self._p("M-01-limit.patch", _patch(self.repo, "def limit(n):\n    return n <= 5\n"))
        self._p("M-02-equivalent.patch", _patch(self.repo, "def limit(n):\n    return not n >= 5\n"))
        self._p("M-03-broken.patch", "diff --git a/none.py b/none.py\n--- a/none.py\n+++ b/none.py\n@@ -1 +1 @@\n-x\n+y\n")
        self._p("M-04-does-not-compile.patch", _patch(self.repo, "def limit(n):\n    return n <\n"))
        self._p("M-05-oracle.patch", _patch(self.repo, "another oracle\n", "acceptance/SC-01.txt"))
        before, content = self._status(), (self.repo / "app.py").read_text()
        r = mutants.run(self.repo, self.cmd, sorted(self.patches.iterdir()), timeout=60,
                        forbidden=["acceptance"])
        res = {m["patch"]: m["result"] for m in r["mutants"]}
        self.assertEqual(res, {"M-01-limit.patch": "detected", "M-02-equivalent.patch": "survived",
                               "M-03-broken.patch": "not-applicable", "M-04-does-not-compile.patch": "harness-error",
                               "M-05-oracle.patch": "rejected"})
        detected = next(m for m in r["mutants"] if m["patch"] == "M-01-limit.patch")
        self.assertEqual(detected["red_scenarios"], ["SC-01"])
        self.assertEqual(self._status(), before)
        self.assertEqual((self.repo / "app.py").read_text(), content)
        wts = subprocess.run(["git", "-C", str(self.repo), "worktree", "list"], capture_output=True, text=True).stdout
        self.assertEqual(len(wts.strip().splitlines()), 1, "no temporary worktrees may be left behind")
        self.assertEqual(r["fingerprint"], mutants.fingerprint(self.repo))

    def test_uses_uncommitted_changes_and_untracked_files(self):
        (self.repo / "app.py").write_text("def limit(n):\n    return n < 5  # edited without commit\n")
        (self.repo / "extra.py").write_text("VALUE = 1\n")
        (self.repo / "check.py").write_text("import extra\n" + CHECK)
        p = self._p("M-01.patch", _patch(self.repo, "def limit(n):\n    return n <= 5  # edited without commit\n"))
        r = mutants.run(self.repo, self.cmd, [p], timeout=60)
        self.assertEqual(r["baseline"]["status"], "pass")
        self.assertEqual(r["mutants"][0]["result"], "detected")

    def test_nested_repository_does_not_break(self):
        _git_init(self.repo / "nested")
        p = self._p("M-01.patch", _patch(self.repo, "def limit(n):\n    return n <= 5\n"))
        r = mutants.run(self.repo, self.cmd, [p], timeout=60)
        self.assertEqual(r["mutants"][0]["result"], "detected")

    def test_fingerprint_changes_with_the_code(self):
        f1 = mutants.fingerprint(self.repo)
        (self.repo / "app.py").write_text("def limit(n):\n    return n < 6\n")
        self.assertNotEqual(f1["changes"], mutants.fingerprint(self.repo)["changes"])
        self.assertEqual(f1["head"], mutants.fingerprint(self.repo)["head"])

    def test_red_baseline_or_no_reports_aborts(self):
        p = self._p("M-01.patch", "x")
        (self.repo / "app.py").write_text("def limit(n):\n    return True\n")
        with self.assertRaises(mutants.MutationError):
            mutants.run(self.repo, self.cmd, [p], timeout=60)
        (self.repo / "app.py").write_text("def limit(n):\n    return n < 5\n")
        with self.assertRaises(mutants.MutationError):
            mutants.run(self.repo, f"{sys.executable} -c 'pass'", [p], timeout=60)

    def test_timeout_kills_the_group_and_does_not_count_as_detected(self):
        marker = Path(self.tmp.name) / "orphan.txt"
        cmd = f"(sleep 6; touch {marker}) & sleep 30"
        r = mutants.run_command(cmd, self.repo, 2, {})
        self.assertEqual(r["status"], "timeout")
        time.sleep(6)
        self.assertFalse(marker.exists(), "the orphan process should have died with the group")

    def test_background_grandchild_does_not_cause_false_timeout(self):
        r = mutants.run_command("(sleep 20 &) ; exit 1", self.repo, 10, {})
        self.assertEqual(r["status"], "fail")
        self.assertLess(r["seconds"], 5)

    def test_cli_exit_code_1_with_survivors(self):
        p = self._p("M-02.patch", _patch(self.repo, "def limit(n):\n    return not n >= 5\n"))
        code, out, _ = _quiet(mutants.main, ["run", "--cmd", self.cmd, "--repo", str(self.repo),
                                             "--timeout", "60", str(p)])
        self.assertEqual(code, 1)
        self.assertIn("Detected: 0/1", out)


if __name__ == "__main__":
    unittest.main()
