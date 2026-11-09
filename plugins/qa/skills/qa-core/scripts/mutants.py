#!/usr/bin/env python3
"""Runs mutants (bugs injected on purpose) against the acceptance suite.

Each mutant is a patch (unified diff). For each one: creates a temporary git worktree with
the current state of the repository (uncommitted changes and untracked files included),
applies the patch, runs the suite command and decides whether the suite detected it. The
original repository is never modified.

Analogy: calibrating a scale with reference weights. If you put 1 kg on it and it reads 0,
the scale is useless, even if it has always read "fine".

Contract with the suite command (environment variables it receives):
  QA_REPORTS      empty directory, owned by that run, where it MUST write its JUnit reports
  QA_IMAGE_TAG    unique tag for the image it builds from the current directory
  QA_MUTANT       mutant ID ("baseline" in the run without mutants)

A mutant counts as DETECTED only if the command ends red AND at least one JUnit case
with a scenario ID (SC-NN) failed. A red without a failed scenario (does not compile, the
harness does not start, port in use) is "harness-error" and does not count as detected.

Usage:
  mutants.py fingerprint [--repo DIR]
  mutants.py baseline    --cmd "COMMAND" [--repo DIR] [--timeout SEC]
  mutants.py run         --cmd "COMMAND" [--repo DIR] [--timeout SEC] [--output results.json]
                         [--forbidden PATH ...] [--cleanup "COMMAND"] PATCH...

Exit codes: 0 all detected, 1 some mutant not detected (survived, timeout,
harness-error, not-applicable, rejected), 2 error (including a baseline that does not pass).
Standard library and git only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from traceability import FormatError, read_junit  # noqa: E402


class MutationError(Exception):
    pass


def _git(repo: Path, *args: str, check: bool = True, text: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=text)
    if check and r.returncode != 0:
        err = r.stderr if text else r.stderr.decode(errors="replace")
        raise MutationError(f"git {' '.join(args)} failed: {err.strip()}")
    return r


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def untracked(repo: Path) -> list[str]:
    out = _git(repo, "ls-files", "--others", "--exclude-standard", "-z").stdout
    return [p for p in out.split("\0") if p]


def fingerprint(repo: Path) -> dict:
    """Identifies the code under evaluation: HEAD + uncommitted diff + untracked files."""
    if _git(repo, "rev-parse", "--is-inside-work-tree", check=False).returncode != 0:
        raise MutationError(f"{repo} is not a git repository")
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    diff = _git(repo, "diff", "HEAD", "--binary", text=False).stdout
    h = hashlib.sha256(diff)
    for rel in sorted(untracked(repo)):
        p = repo / rel
        h.update(rel.encode())
        if p.is_file():
            h.update(p.read_bytes())
    return {"head": head, "changes": h.hexdigest()}


def snapshot(repo: Path) -> str:
    stash = _git(repo, "stash", "create").stdout.strip()
    return stash or _git(repo, "rev-parse", "HEAD").stdout.strip()


class Worktree:
    """Temporary git worktree that is always removed, whatever happens."""

    def __init__(self, repo: Path, commit: str, extras: list[str]):
        self.repo, self.commit, self.extras = repo, commit, extras
        self.dir: Path | None = None
        self.skipped: list[str] = []

    def __enter__(self) -> "Worktree":
        parent = Path(tempfile.mkdtemp(prefix="qa-mutant-"))
        self.dir = parent / "wt"
        _git(self.repo, "worktree", "add", "--detach", str(self.dir), self.commit)
        for rel in self.extras:
            src, dst = self.repo / rel, self.dir / rel
            if not src.is_file():
                self.skipped.append(rel)  # e.g. a nested repository
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        return self

    def __exit__(self, *exc) -> None:
        if self.dir is not None:
            _git(self.repo, "worktree", "remove", "--force", str(self.dir), check=False)
            shutil.rmtree(self.dir.parent, ignore_errors=True)
            _git(self.repo, "worktree", "prune", check=False)


def run_command(cmd: str, cwd: Path, timeout: int, env_extra: dict[str, str]) -> dict:
    """Runs in its own process group; on timeout kills the whole group."""
    env = {**os.environ, **env_extra}
    with tempfile.TemporaryFile() as out:
        start = time.monotonic()
        proc = subprocess.Popen(cmd, shell=True, cwd=cwd, env=env, stdout=out, stderr=subprocess.STDOUT,
                                start_new_session=True)
        try:
            code = proc.wait(timeout=timeout)
            status = "pass" if code == 0 else "fail"
        except subprocess.TimeoutExpired:
            code, status = None, "timeout"
        finally:
            try:
                os.killpg(proc.pid, signal.SIGKILL)  # cleans up descendants, also after finishing
            except (ProcessLookupError, PermissionError):
                pass
            proc.wait()
        seconds = time.monotonic() - start
        out.seek(0)
        tail = out.read()[-3000:].decode(errors="replace")
    return {"status": status, "code": code, "seconds": round(seconds, 1), "output": tail}


def _red_scenarios(reports: Path) -> tuple[list[str], int]:
    xmls = sorted(reports.rglob("*.xml"))
    if not xmls:
        return [], 0
    try:
        results, _, _ = read_junit(xmls)
    except FormatError:
        return [], 0
    red = sorted(i for i, rs in results.items() if "failed" in rs)
    return red, len(results)


def _execution(repo: Path, commit: str, extras: list[str], cmd: str, timeout: int, ident: str,
               patch: Path | None, cleanup: str | None) -> dict:
    with Worktree(repo, commit, extras) as wt, tempfile.TemporaryDirectory(prefix="qa-reports-") as rep:
        if patch is not None:
            check = _git(wt.dir, "apply", "--check", str(patch), check=False)
            if check.returncode != 0:
                return {"result": "not-applicable", "detail": check.stderr.strip()[-500:]}
            _git(wt.dir, "apply", str(patch))
        env = {"QA_REPORTS": rep, "QA_IMAGE_TAG": f"qa-mut-{ident.lower()}-{os.getpid()}", "QA_MUTANT": ident}
        r = run_command(cmd, wt.dir, timeout, env)
        r["red_scenarios"], r["executed_scenarios"] = _red_scenarios(Path(rep))
        r["skipped"] = wt.skipped
        if cleanup:
            run_command(cleanup, wt.dir, 300, env)
    return r


def _targets(patch: Path) -> list[str]:
    paths = set()
    for line in patch.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(("+++ ", "--- ")):
            path = line[4:].split("\t")[0].strip()
            if path != "/dev/null":
                paths.add(path[2:] if path.startswith(("a/", "b/")) else path)
    return sorted(paths)


def baseline(repo: Path, cmd: str, timeout: int) -> dict:
    commit = snapshot(repo)
    r = _execution(repo, commit, untracked(repo), cmd, timeout, "baseline", None, None)
    r["commit"] = commit
    return r


def run(repo: Path, cmd: str, patches: list[Path], timeout: int, with_baseline: bool = True,
        forbidden: list[str] | None = None, cleanup: str | None = None) -> dict:
    if not patches:
        raise MutationError("give at least one patch")
    for p in patches:
        if not p.is_file():
            raise MutationError(f"the patch {p} does not exist")
    forbidden = [Path(x).as_posix().rstrip("/") for x in (forbidden or [])]
    summary: dict = {"fingerprint": fingerprint(repo), "baseline": None, "mutants": []}
    commit = snapshot(repo)
    extras = untracked(repo)
    if with_baseline:
        b = _execution(repo, commit, extras, cmd, timeout, "baseline", None, cleanup)
        summary["baseline"] = b
        if b["status"] != "pass":
            raise MutationError(f"the suite does not pass without mutants (status: {b['status']}); "
                                f"the results would mean nothing.\n{b['output']}")
        if b["executed_scenarios"] == 0:
            raise MutationError("the baseline run left no JUnit report with SC-NN scenarios in $QA_REPORTS; "
                                "without reports a detected bug cannot be told apart from a broken harness")
    for patch in patches:
        data = patch.read_bytes()
        entry = {"patch": patch.name, "sha256": _sha(data), "targets": _targets(patch)}
        touched = [t for t in entry["targets"] if any(t == p or t.startswith(p + "/") for p in forbidden)]
        if touched:
            entry.update(result="rejected", detail=f"touches forbidden paths (oracle or harness): {', '.join(touched)}")
            summary["mutants"].append(entry)
            continue
        ident = re.sub(r"[^a-z0-9-]", "-", patch.stem.lower())[:40]
        r = _execution(repo, commit, extras, cmd, timeout, ident, patch.resolve(), cleanup)
        if r.get("result") == "not-applicable":
            entry.update(r)
        elif r["status"] == "timeout":
            entry.update(r, result="timeout")
        elif r["status"] == "pass":
            entry.update(r, result="survived")
        elif r["red_scenarios"]:
            entry.update(r, result="detected")
            entry["output"] = ""
        else:
            entry.update(r, result="harness-error")
        summary["mutants"].append(entry)
    return summary


def _table(summary: dict) -> str:
    rows = ["| Patch | Result | Red scenarios | Seconds |", "|---|---|---|---|"]
    for m in summary["mutants"]:
        red = ", ".join(m.get("red_scenarios", [])) or "—"
        rows.append(f"| {m['patch']} | {m['result']} | {red} | {m.get('seconds', '—')} |")
    total = len(summary["mutants"])
    detected = sum(1 for m in summary["mutants"] if m["result"] == "detected")
    rows.append(f"\nDetected: {detected}/{total}")
    rows.append(f"Fingerprint: HEAD {summary['fingerprint']['head'][:12]} · changes {summary['fingerprint']['changes'][:12]}")
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Runs mutants against the acceptance suite")
    sub = ap.add_subparsers(dest="cmd_", required=True)
    h = sub.add_parser("fingerprint")
    h.add_argument("--repo", type=Path, default=Path("."))
    for name in ("baseline", "run"):
        p = sub.add_parser(name)
        p.add_argument("--cmd", required=True, help="suite command; exit 0 = green; writes JUnit to $QA_REPORTS")
        p.add_argument("--repo", type=Path, default=Path("."))
        p.add_argument("--timeout", type=int, default=1800)
        if name == "run":
            p.add_argument("--output", type=Path)
            p.add_argument("--forbidden", nargs="*", default=[], help="paths a mutant may not touch")
            p.add_argument("--cleanup", help="command after each run (e.g. delete the $QA_IMAGE_TAG image)")
            p.add_argument("patches", nargs="+", type=Path)
    a = ap.parse_args(argv)
    repo = a.repo.resolve()
    try:
        if a.cmd_ == "fingerprint":
            print(json.dumps(fingerprint(repo), indent=2))
            return 0
        if a.cmd_ == "baseline":
            b = baseline(repo, a.cmd, a.timeout)
            print(f"Baseline: {b['status']} in {b['seconds']} s; scenarios in JUnit: {b['executed_scenarios']}")
            ok = b["status"] == "pass" and b["executed_scenarios"] > 0
            if not ok:
                print(b["output"])
            return 0 if ok else 2
        summary = run(repo, a.cmd, a.patches, a.timeout, forbidden=a.forbidden, cleanup=a.cleanup)
    except MutationError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(_table(summary))
    return 0 if all(m["result"] == "detected" for m in summary["mutants"]) else 1


if __name__ == "__main__":
    sys.exit(main())
