#!/usr/bin/env python3
"""Integrity seal for the oracle (criteria, scenarios, acceptance tests and QA configuration).

Records the SHA-256 hash of every file under the sealed paths and detects any
modification, deletion, new file or symbolic link. With --base it also compares
against the seal on the base branch (git) and lists EVERY reseal made since then, so
that a human reviews it: an agent can edit and reseal, but it cannot do so without
it showing up in the verification.

What this script does NOT do: prevent editing, or know who resealed (--author is
declarative). Real attribution is git authorship and the PR review.

Usage:
  seal.py seal    --seal PATH [--root DIR] --reason TEXT [--author X] PATH...
  seal.py reseal  --seal PATH [--root DIR] --reason TEXT [--author X] [PATH...]
  seal.py verify  --seal PATH [--root DIR] [--base REF] [--require PATH...] [--json]
  seal.py history --seal PATH

Exit codes: 0 intact / operation done, 1 seal broken, 2 usage error.
Standard library only (plus git for --base).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

VERSION = 2
IGNORED = {".DS_Store"}
RE_REFERENCE = re.compile(r"(?<![A-Za-z0-9])[EF]-\d{2,}(?!\d)")


class UsageError(Exception):
    pass


def _hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def _rel(p: Path, root: Path) -> str:
    return Path(os.path.abspath(p)).relative_to(Path(os.path.abspath(root))).as_posix()


def _walk(base: Path):
    """Walks without following symbolic links; returns (files, links)."""
    files, links = [], []
    for dirpath, dirnames, filenames in os.walk(base, followlinks=False):
        for d in list(dirnames):
            if os.path.islink(os.path.join(dirpath, d)):
                links.append(Path(dirpath) / d)
                dirnames.remove(d)
        for f in filenames:
            p = Path(dirpath) / f
            (links if p.is_symlink() else files).append(p)
    return sorted(files), sorted(links)


def collect(paths: list[str], root: Path, seal_path: Path) -> tuple[dict[str, str], list[str]]:
    """({relative_path: sha256}, [symbolic links that cannot be sealed])."""
    files: dict[str, str] = {}
    links: list[str] = []
    seal_abs = os.path.abspath(seal_path)
    root_abs = Path(os.path.abspath(root))
    for r in paths:
        base = root / r
        if not base.exists() and not base.is_symlink():
            raise UsageError(f"the path to seal does not exist: {r}")
        try:
            Path(os.path.abspath(base)).relative_to(root_abs)
        except ValueError as e:
            raise UsageError(f"the path {r} is outside the root {root}") from e
        if base.is_symlink():
            links.append(_rel(base, root))
            continue
        if base.is_file():
            candidates, found_links = [base], []
        else:
            candidates, found_links = _walk(base)
        links.extend(_rel(p, root) for p in found_links)
        for p in candidates:
            if p.name in IGNORED or os.path.abspath(p) == seal_abs or p.name.endswith(".qa-seal.json.tmp"):
                continue
            files[_rel(p, root)] = _hash(p)
    return dict(sorted(files.items())), sorted(set(links))


def _digest(files: dict[str, str]) -> str:
    h = hashlib.sha256()
    for path, sha in files.items():
        h.update(f"{path}\0{sha}\n".encode())
    return h.hexdigest()


def _validate(data: dict, origin: str) -> dict:
    if data.get("version") != VERSION:
        raise UsageError(f"unsupported seal version in {origin}: {data.get('version')}")
    return data


def _read(seal_path: Path) -> dict:
    if not seal_path.exists():
        raise UsageError(f"the seal {seal_path} does not exist")
    return _validate(json.loads(seal_path.read_text(encoding="utf-8")), str(seal_path))


def _read_base(seal_path: Path, root: Path, ref: str) -> dict | None:
    rel = _rel(seal_path, root)
    r = subprocess.run(["git", "-C", str(root), "show", f"{ref}:{rel}"], capture_output=True, text=True)
    if r.returncode != 0:
        check = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", ref], capture_output=True, text=True)
        if check.returncode != 0:
            raise UsageError(f"the base ref '{ref}' does not exist")
        return None  # the seal did not exist on the base: new feature
    return _validate(json.loads(r.stdout), f"{ref}:{rel}")


def _write(seal_path: Path, data: dict) -> None:
    seal_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = seal_path.with_name(seal_path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, seal_path)


def _entry(action: str, reason: str, author: str, files: dict[str, str]) -> dict:
    return {
        "date": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "action": action,
        "reason": reason,
        "author": author,
        "n_files": len(files),
        "digest": _digest(files),
    }


def _normalize(paths: list[str]) -> list[str]:
    return sorted({Path(r).as_posix().rstrip("/") for r in paths})


def seal(seal_path: Path, root: Path, paths: list[str], reason: str, author: str) -> dict:
    if seal_path.exists():
        raise UsageError("the seal already exists; to change it use 'reseal' with a reason")
    if not paths:
        raise UsageError("give at least one path to seal")
    if not reason.strip():
        raise UsageError("the reason is required")
    norm = _normalize(paths)
    files, links = collect(norm, root, seal_path)
    if links:
        raise UsageError(f"there are symbolic links, which cannot be sealed: {', '.join(links)}")
    if not files:
        raise UsageError("there are no files to seal in the given paths")
    data = {"version": VERSION, "paths": norm, "files": files,
            "history": [_entry("seal", reason, author, files)]}
    _write(seal_path, data)
    return data


def compare(data: dict, current: dict[str, str]) -> dict[str, list[str]]:
    sealed = data["files"]
    return {
        "modified": sorted(r for r in sealed if r in current and current[r] != sealed[r]),
        "deleted": sorted(r for r in sealed if r not in current),
        "new": sorted(r for r in current if r not in sealed),
    }


def _covered(path: str, paths: list[str]) -> bool:
    path = Path(path).as_posix().rstrip("/")
    return any(path == r or path.startswith(r + "/") for r in paths)


def verify(seal_path: Path, root: Path, base: str | None = None, required: list[str] | None = None) -> dict:
    """Returns a report with 'intact' and every cause of breakage."""
    report: dict = {"intact": True, "modified": [], "deleted": [], "new": [], "links": [],
                    "missing_paths": [], "required_not_sealed": [], "base": base,
                    "reseals_since_base": [], "base_problems": []}
    base_data = _read_base(seal_path, root, base) if base else None
    if not seal_path.exists():
        if base and base_data is not None:
            report["intact"] = False
            report["base_problems"].append("the seal existed on the base and was deleted")
            return report
        raise UsageError(f"the seal {seal_path} does not exist")
    data = _read(seal_path)
    existing = [r for r in data["paths"] if (root / r).exists() or (root / r).is_symlink()]
    report["missing_paths"] = [r for r in data["paths"] if r not in existing]
    current, links = collect(existing, root, seal_path) if existing else ({}, [])
    report.update(compare(data, current))
    report["links"] = links
    report["required_not_sealed"] = [r for r in (required or []) if not _covered(r, data["paths"])]
    if base:
        hist, hist_base = data["history"], (base_data or {}).get("history", [])
        if hist[:len(hist_base)] != hist_base:
            report["base_problems"].append("the seal history was rewritten relative to the base")
            new_entries = hist
        else:
            new_entries = hist[len(hist_base):]
        report["reseals_since_base"] = new_entries
        if base_data is not None:
            for e in new_entries:
                if e.get("action") == "reseal" and not RE_REFERENCE.search(e.get("reason", "")):
                    report["base_problems"].append(
                        f"reseal on {e.get('date')} without a reference to an escalation or finding (E-NN / F-NN)")
    report["intact"] = not any(report[k] for k in ("modified", "deleted", "new", "links",
                                                   "missing_paths", "required_not_sealed", "base_problems"))
    return report


def reseal(seal_path: Path, root: Path, paths: list[str], reason: str, author: str) -> tuple[dict, dict]:
    if not reason.strip():
        raise UsageError("a reason is required to reseal (cite the escalation E-NN or the finding F-NN)")
    data = _read(seal_path)
    norm = _normalize(data["paths"] + paths)
    files, links = collect([r for r in norm if (root / r).exists()], root, seal_path)
    if links:
        raise UsageError(f"there are symbolic links, which cannot be sealed: {', '.join(links)}")
    changes = compare(data, files)
    entry = _entry("reseal", reason, author, files)
    entry["changes"] = changes
    data["paths"], data["files"] = norm, files
    data["history"].append(entry)
    _write(seal_path, data)
    return data, changes


def _print(report: dict) -> None:
    labels = [("modified", "MODIFIED"), ("deleted", "DELETED"), ("new", "NEW, NOT SEALED"),
              ("links", "SYMBOLIC LINK (cannot be sealed)"), ("missing_paths", "SEALED PATH MISSING"),
              ("required_not_sealed", "REQUIRED AND NOT SEALED"), ("base_problems", "BASE")]
    for key, label in labels:
        for r in report.get(key, []):
            print(f"  {label}: {r}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Integrity seal for the QA oracle")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("seal", "reseal", "verify", "history"):
        p = sub.add_parser(name)
        p.add_argument("--seal", required=True, type=Path)
        p.add_argument("--root", type=Path, default=Path("."))
        if name in ("seal", "reseal"):
            p.add_argument("--reason", required=True)
            p.add_argument("--author", default=os.environ.get("USER", "unknown"),
                           help="declarative: real attribution is git authorship")
            p.add_argument("paths", nargs="*")
        if name == "verify":
            p.add_argument("--base", help="git ref of the base branch (e.g. origin/main)")
            p.add_argument("--require", nargs="*", default=[], help="paths that must be sealed")
            p.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "seal":
            data = seal(a.seal, a.root, a.paths, a.reason, a.author)
            print(f"Seal created: {len(data['files'])} files in {', '.join(data['paths'])}")
            return 0
        if a.cmd == "reseal":
            data, changes = reseal(a.seal, a.root, a.paths, a.reason, a.author)
            print(f"Seal updated ({len(data['files'])} files). Reason: {a.reason}")
            for key, label in (("modified", "changed"), ("deleted", "removed"), ("new", "added")):
                for r in changes[key]:
                    print(f"  {label}: {r}")
            return 0
        if a.cmd == "verify":
            rep = verify(a.seal, a.root, a.base, a.require)
            if a.json:
                print(json.dumps(rep, ensure_ascii=False, indent=2))
            else:
                if rep["intact"]:
                    print("Seal intact.")
                else:
                    print("SEAL BROKEN:")
                    _print(rep)
                if a.base:
                    print(f"\nSeals and reseals since {a.base} (human review required): "
                          f"{len(rep['reseals_since_base'])}")
                    for e in rep["reseals_since_base"]:
                        print(f"  {e['date']}  {e['action']:<7} {e['n_files']:>4} files  {e['reason']}")
            return 0 if rep["intact"] else 1
        if a.cmd == "history":
            for e in _read(a.seal)["history"]:
                print(f"{e['date']}  {e['action']:<7} {e['n_files']:>4} files  {e['author']}: {e['reason']}")
            return 0
    except (UsageError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
