#!/usr/bin/env python3
"""Traceability criterion → scenario → executable test → result.

Reads criteria.md and scenarios.md (format in references/formats.md), and optionally
the test sources and the JUnit reports of ONE run. Reports every gap in the chain.
It is the deterministic defense against: the criterion nobody tests, the test that
"passes" because it did not run, the stale or foreign report, and the test that claims
to cover several scenarios at once.

Usage:
  traceability.py --criteria criteria.md --scenarios scenarios.md
                  [--sources DIR ...] [--junit REPORT.xml ...] [--since EPOCH]
                  [--rungs 1,2] [--ids SC-01,SC-04] [--expect-red] [--json]

Strict rules:
  - A skipped or unexecuted scenario does NOT count as green.
  - A JUnit case with more than one scenario ID is a gap: one test, one scenario.
  - With --junit, every criterion in scope needs at least one green scenario executed
    in this run; if all its scenarios are outside the requested rungs, it is a gap
    ("no evidence in scope"), never a green.
  - An empty scope is an error.
  - With --since, a report modified before that timestamp is an error.
  - --expect-red (before implementing): a red scenario is expected and a green one is
    reported for investigation; anything not implemented or not executed is still a gap.

Exit codes: 0 chain complete (and green), 1 gaps or failures, 2 format error.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

ID_AC = r"AC-\d{2,}"
ID_SC = r"SC-\d{2,}"
RE_AC = re.compile(rf"(?<![A-Za-z0-9]){ID_AC}(?!\d)")
RE_SC = re.compile(rf"(?<![A-Za-z0-9]){ID_SC}(?!\d)")
RE_SC_ANY = re.compile(r"(?<![A-Za-z0-9])SC-\d+(?!\d)")
RE_AC_ANY = re.compile(r"(?<![A-Za-z0-9])AC-\d+(?!\d)")
RE_AC_HEADING = re.compile(r"^#{2,3}\s+(AC-\d+)\b(.*)$")
# Test title lines. Gherkin keywords in English and in the Spanish localization (# language: es).
RE_TITLE = re.compile(
    r"(Scenario Outline|Scenario Template|Scenario|Example|Esquema del escenario|Escenario|Ejemplo)\s*:"
    r"|\b(test|it|describe)\s*(\.\w+)?\s*\("
    r"|\bt\.Run\s*\(", re.IGNORECASE)
VALID_STATUSES = {"active", "blocked-testability", "discarded"}
SOURCE_EXTS = {".feature", ".hurl", ".go", ".ts", ".js", ".mjs", ".py", ".java", ".kt", ".http", ".robot"}


class FormatError(Exception):
    pass


@dataclass
class Scenario:
    id: str
    criteria: list[str]
    rungs: list[int]
    status: str
    files: list[str] = field(default_factory=list)
    results: list[str] = field(default_factory=list)  # passed | failed | skipped

    @property
    def result(self) -> str:
        if not self.results:
            return "not-run"
        if "failed" in self.results:
            return "red"
        if "skipped" in self.results:
            return "skipped"
        return "green"


def _without_code_blocks(text: str) -> list[str]:
    lines, inside = [], False
    for line in text.splitlines():
        if line.strip().startswith(("```", "~~~")):
            inside = not inside
            lines.append("")
            continue
        lines.append("" if inside else line)
    return lines


def read_criteria(text: str) -> tuple[list[str], list[str]]:
    """(current criteria, discarded criteria)."""
    current, discarded, active = [], [], None
    seen: list[str] = []
    for n, line in enumerate(_without_code_blocks(text), 1):
        m = RE_AC_HEADING.match(line)
        if m:
            ident = m.group(1)
            if not re.fullmatch(ID_AC, ident):
                raise FormatError(f"line {n}: invalid criterion ID '{ident}' (expected AC-NN, at least two digits)")
            if ident in seen:
                raise FormatError(f"duplicate criterion: {ident}")
            seen.append(ident)
            active = ident
            current.append(ident)
            continue
        if line.startswith("#"):
            active = None
        if active and re.match(r"^\s*-\s*Status\s*:\s*discarded\b", line, re.IGNORECASE):
            current.remove(active)
            discarded.append(active)
            active = None
    if not seen:
        raise FormatError("no criterion found with a '## AC-NN:' heading")
    return current, discarded


def _cells(line: str) -> list[str]:
    s = line.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]


def _normal(c: str) -> str:
    return c.lower().strip()


def _rungs(text: str, n: int, ident: str) -> list[int]:
    parts = [p.strip() for p in re.split(r"[,\s]+", text) if p.strip()]
    if not parts or not all(p.isdigit() and 1 <= int(p) <= 5 for p in parts):
        raise FormatError(f"line {n}: {ident} has an invalid rung '{text}' (1 to 5, several separated by commas)")
    return sorted({int(p) for p in parts})


def read_scenarios(text: str) -> list[Scenario]:
    scenarios: list[Scenario] = []
    columns: dict[str, int] | None = None
    for n, line in enumerate(_without_code_blocks(text), 1):
        if not line.strip().startswith("|"):
            columns = None
            continue
        cells = _cells(line)
        normal = [_normal(c) for c in cells]
        if "id" in normal:
            alias = {"criteria": "criterion", "rungs": "rung"}
            normal = [alias.get(c, c) for c in normal]
            required = {"id", "criterion", "rung", "status"}
            missing = required - set(normal)
            if missing:
                raise FormatError(f"line {n}: the table is missing columns: {', '.join(sorted(missing))}")
            columns = {name: normal.index(name) for name in required}
            continue
        if columns is None or set(line.replace("|", "").strip()) <= set("-: "):
            continue
        if len(cells) <= max(columns.values()):
            raise FormatError(f"line {n}: row with fewer columns than the header")
        ident = cells[columns["id"]]
        if not re.fullmatch(ID_SC, ident):
            raise FormatError(f"line {n}: invalid scenario ID '{ident}' (expected SC-NN, at least two digits)")
        crit_cell = cells[columns["criterion"]]
        criteria = RE_AC_ANY.findall(crit_cell)
        bad = [c for c in criteria if not re.fullmatch(ID_AC, c)]
        if bad or not criteria:
            raise FormatError(f"line {n}: {ident} must reference valid AC-NN criteria (found: '{crit_cell}')")
        status = cells[columns["status"]].lower()
        if status not in VALID_STATUSES:
            raise FormatError(f"line {n}: {ident} has an invalid status '{status}'")
        scenarios.append(Scenario(ident, criteria, _rungs(cells[columns["rung"]], n, ident), status))
    ids = [s.id for s in scenarios]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise FormatError(f"duplicate scenarios: {', '.join(duplicates)}")
    if not scenarios:
        raise FormatError("no scenario table found with columns ID, Criterion, Rung and Status")
    return scenarios


def scan_sources(dirs: list[Path]) -> dict[str, list[str]]:
    """{SC-NN: [files]} looking for the ID in the file name or in test title lines."""
    mentions: dict[str, set[str]] = {}
    for d in dirs:
        if not d.exists():
            raise FormatError(f"the sources directory {d} does not exist")
        files = [d] if d.is_file() else sorted(p for p in d.rglob("*") if p.is_file())
        for p in files:
            if p.suffix.lower() not in SOURCE_EXTS:
                continue
            ids = set(RE_SC_ANY.findall(p.name))
            try:
                for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if RE_TITLE.search(line):
                        ids |= set(RE_SC_ANY.findall(line))
            except OSError:
                continue
            for i in ids:
                mentions.setdefault(i, set()).add(p.as_posix())
    return {k: sorted(v) for k, v in mentions.items()}


def read_junit(paths: list[Path], since: float | None = None) -> tuple[dict[str, list[str]], list[str], list[str]]:
    """({SC-NN: [results]}, [cases without an ID], [cases with several IDs])."""
    if not paths:
        raise FormatError("no JUnit report given (did the run produce no reports?)")
    results: dict[str, list[str]] = {}
    without_id: list[str] = []
    multiple: list[str] = []
    for path in paths:
        if since is not None and path.stat().st_mtime < since:
            raise FormatError(f"the report {path} predates the start of the run: not accepted")
        try:
            tree = ET.parse(path)
        except (ET.ParseError, OSError) as e:
            raise FormatError(f"could not read the JUnit report {path}: {e}") from e
        for case in tree.iter("testcase"):
            name = " ".join(filter(None, (case.get("classname"), case.get("name"), case.get("file"))))
            if case.find("failure") is not None or case.find("error") is not None:
                res = "failed"
            elif case.find("skipped") is not None:
                res = "skipped"
            else:
                res = "passed"
            ids = sorted(set(RE_SC_ANY.findall(name)))
            if not ids:
                without_id.append(name)
            elif len(ids) > 1:
                multiple.append(name)
            else:
                results.setdefault(ids[0], []).append(res)
    return results, without_id, multiple


def analyze(criteria: list[str], scenarios: list[Scenario], rungs: set[int] | None,
            sources: dict[str, list[str]] | None,
            junit: tuple[dict[str, list[str]], list[str], list[str]] | None,
            ids: set[str] | None = None, expect_red: bool = False,
            discarded: list[str] | None = None) -> dict:
    declared = {s.id for s in scenarios}
    gaps: list[str] = []
    warnings: list[str] = []
    discarded = discarded or []

    if ids:
        unknown = sorted(ids - declared)
        if unknown:
            raise FormatError(f"--ids includes undeclared scenarios: {', '.join(unknown)}")

    for s in scenarios:
        for c in s.criteria:
            if c in discarded and s.status != "discarded":
                gaps.append(f"{s.id} is active but references {c}, which is discarded")
            elif c not in criteria and c not in discarded:
                gaps.append(f"{s.id} references {c}, which does not exist in criteria.md")

    live = [s for s in scenarios if s.status != "discarded"]

    def in_filter(s: Scenario) -> bool:
        return (rungs is None or bool(set(s.rungs) & rungs)) and (ids is None or s.id in ids)

    in_scope = [s for s in live if s.status == "active" and in_filter(s)]
    if not in_scope:
        raise FormatError("the scope is empty: no active scenario matches the filters (rungs or IDs)")

    considered = criteria if ids is None else sorted({c for s in in_scope for c in s.criteria if c in criteria})

    for c in considered:
        own = [s for s in live if c in s.criteria]
        if not own:
            gaps.append(f"{c} has no scenario")
        elif all(s.status == "blocked-testability" for s in own):
            gaps.append(f"{c} only has scenarios blocked by testability: no executable coverage")

    for s in live:
        if s.status == "blocked-testability":
            warnings.append(f"{s.id} blocked by testability (open debt)")

    if sources is not None:
        for s in in_scope:
            s.files = sources.get(s.id, [])
            if not s.files:
                gaps.append(f"{s.id} is not implemented in the sources (the ID must be in the test title or the file name)")
        for i in sorted(set(sources) - declared):
            gaps.append(f"{i} appears in {', '.join(sources[i])} but is not declared in scenarios.md")

    if junit is not None:
        results, without_id, multiple = junit
        for s in in_scope:
            s.results = results.get(s.id, [])
            r = s.result
            if r == "not-run":
                gaps.append(f"{s.id} does not appear in any JUnit report: not executed")
            elif r == "skipped":
                gaps.append(f"{s.id} was skipped: it does not count as green")
            elif r == "red" and not expect_red:
                gaps.append(f"{s.id} failed")
            elif r == "green" and expect_red:
                warnings.append(f"{s.id} is GREEN before implementing: either the behavior already existed or the test is vacuous; investigate")
        for i in sorted(set(results) - declared):
            gaps.append(f"{i} was executed but is not declared in scenarios.md")
        for name in multiple:
            gaps.append(f"JUnit case with several scenario IDs (one test, one scenario): {name}")
        for name in without_id:
            warnings.append(f"case without a scenario ID in the JUnit report: {name}")
        if not expect_red:
            for c in considered:
                own = [s for s in live if c in s.criteria and s.status == "active"]
                if own and not any(s in in_scope for s in own):
                    outside = ", ".join(f"{s.id}(r{'/'.join(map(str, s.rungs))})" for s in own)
                    gaps.append(f"{c} has no evidence in scope: its scenarios are on other rungs ({outside})")

    coverage = []
    for c in considered:
        states = []
        for s in (x for x in live if c in x.criteria):
            if s.status == "blocked-testability":
                states.append(f"{s.id}:blocked")
            elif s not in in_scope:
                states.append(f"{s.id}:out-of-scope(r{'/'.join(map(str, s.rungs))})")
            elif junit is not None:
                states.append(f"{s.id}:{s.result}")
            elif sources is not None:
                states.append(f"{s.id}:{'implemented' if s.files else 'not-implemented'}")
            else:
                states.append(f"{s.id}:declared")
        coverage.append({"criterion": c, "scenarios": states})

    return {"complete": not gaps, "gaps": gaps, "warnings": warnings, "coverage": coverage,
            "in_scope": len(in_scope), "declared": len(live), "expect_red": expect_red}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Traceability criterion → scenario → test → result")
    ap.add_argument("--criteria", required=True, type=Path)
    ap.add_argument("--scenarios", required=True, type=Path)
    ap.add_argument("--sources", nargs="*", type=Path)
    ap.add_argument("--junit", nargs="*", type=Path)
    ap.add_argument("--since", type=float, help="epoch of the start of the run; rejects older reports")
    ap.add_argument("--rungs", help="rungs in scope, for example 1,2")
    ap.add_argument("--ids", help="scenarios in scope, for example SC-01,SC-04 (per-slice cadence)")
    ap.add_argument("--expect-red", action="store_true", help="before implementing: red is expected")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        criteria, discarded = read_criteria(a.criteria.read_text(encoding="utf-8"))
        scenarios = read_scenarios(a.scenarios.read_text(encoding="utf-8"))
        rungs = ids = None
        if a.rungs:
            try:
                rungs = {int(x) for x in a.rungs.split(",") if x.strip()}
            except ValueError as e:
                raise FormatError(f"invalid --rungs: {a.rungs}") from e
        if a.ids:
            ids = {x.strip() for x in a.ids.split(",") if x.strip()}
        sources = scan_sources(a.sources) if a.sources else None
        junit = read_junit(a.junit, a.since) if a.junit is not None else None
        r = analyze(criteria, scenarios, rungs, sources, junit, ids, a.expect_red, discarded)
    except (FormatError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        scope = ", ".join(filter(None, [f"rungs {a.rungs}" if a.rungs else "",
                                        f"scenarios {a.ids}" if a.ids else ""])) or "all"
        print(f"Traceability (scope: {scope}): {r['in_scope']} active scenarios in scope out of {r['declared']} current.")
        for c in r["coverage"]:
            print(f"  {c['criterion']}: {', '.join(c['scenarios']) or '—'}")
        if r["gaps"]:
            print(f"\nGAPS ({len(r['gaps'])}):")
            for g in r["gaps"]:
                print(f"  - {g}")
        if r["warnings"]:
            print(f"\nWarnings ({len(r['warnings'])}):")
            for w in r["warnings"]:
                print(f"  - {w}")
        if r["complete"]:
            print("\nChain complete." + (" Red expected before implementing." if a.expect_red else ""))
        else:
            print("\nChain has gaps.")
    return 0 if r["complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
