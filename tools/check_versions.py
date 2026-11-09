#!/usr/bin/env python3
"""Fails if a plugin changed relative to the base branch without bumping its version in catalog.json.

Claude Code, Codex and Copilot store each plugin by version number: a change without
a version bump never reaches anyone who already has it installed.

Usage:
  python3 tools/check_versions.py --base origin/main

Compares the working tree (commits and uncommitted changes) against the base.
Exit codes: 0 all in order, 1 some plugins changed without a version bump, 2 error.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = {"plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json"}
# The catalog was called catalogo.json before the repository moved to English; older base refs still have it.
CATALOG_NAMES = ("catalog.json", "catalogo.json")


def _git(*args: str) -> str:
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def _version(v: str) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in v.split("-")[0].split("."))
    except ValueError as e:
        raise RuntimeError(f"non-numeric version: {v}") from e


def _base_catalog(base: str) -> dict:
    for name in CATALOG_NAMES:
        try:
            return json.loads(_git("show", f"{base}:{name}"))
        except RuntimeError:
            continue
    raise RuntimeError(f"no catalog found in {base} ({' or '.join(CATALOG_NAMES)})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", required=True, help="git ref of the base branch, e.g. origin/main")
    a = ap.parse_args(argv)
    try:
        _git("rev-parse", "--verify", f"{a.base}^{{commit}}")
        base_cat = _base_catalog(a.base)
        changed = _git("diff", "--name-only", a.base, "--", "plugins").splitlines()
        changed += _git("ls-files", "--others", "--exclude-standard", "--", "plugins").splitlines()
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    current = {p["name"]: p["version"] for p in json.loads((ROOT / "catalog.json").read_text())["plugins"]}
    before = {p["name"]: p["version"] for p in base_cat["plugins"]}
    problems = []
    for name, version in sorted(current.items()):
        prefix = f"plugins/{name}/"
        files = sorted({f for f in changed if f.startswith(prefix) and f[len(prefix):] not in GENERATED})
        if name not in before:
            print(f"  {name}: new plugin ({version})")
            continue
        try:
            bumped = _version(version) > _version(before[name])
            lowered = _version(version) < _version(before[name])
        except RuntimeError as e:
            print(f"error: {name}: {e}", file=sys.stderr)
            return 2
        if lowered:
            problems.append(f"{name}: the version went down ({before[name]} → {version})")
        elif files and not bumped:
            sample = ", ".join(files[:3]) + (f" and {len(files) - 3} more" if len(files) > 3 else "")
            problems.append(f"{name}: changed ({sample}) but is still at {version}; bump it in catalog.json")
        elif files:
            print(f"  {name}: {before[name]} → {version} ({len(files)} files changed)")
    for name in sorted(set(before) - set(current)):
        print(f"  {name}: removed from the catalog (installed copies stay until the user uninstalls them)")
    if problems:
        print("Plugins with changes and no version bump (nobody would receive the update):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("Versions in order.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
