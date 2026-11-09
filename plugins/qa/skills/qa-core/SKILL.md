---
name: qa-core
description: "Shared base of the QA domain: role model (dev, QA, executor, human), environment ladder, formats for criteria, scenarios and findings, and the deterministic scripts (integrity seal, traceability, mutants). Use it when another qa-* skill references it, or when the user asks how the QA model works, what the seal guarantees or how criteria are traced to tests."
license: MIT
---

# QA: shared base

Respond in the user's language; keep common technical terms in English.

This skill does not run a workflow: it is the reference and the tools that every `qa-*` skill shares. The other skills point here with relative paths (`../qa-core/...`), so **it must be installed next to them**, as a sibling folder, in any tool.

**Analogy:** it is the rulebook and the scorer's table of a match. The players (the other skills) play; the rulebook says what counts and the table keeps the score.

## References

| File | What it contains |
|---|---|
| [references/role-model.md](references/role-model.md) | Who writes what and who approves; solo and duo modes; information barrier N1-N3; escalation; what the seal guarantees and what it does not |
| [references/environment-ladder.md](references/environment-ladder.md) | Rungs 0 to 5, scenario assignment rule, execution cadences |
| [references/formats.md](references/formats.md) | Handoff, criteria, scenarios (parseable format), ID convention in JUnit, findings, escalations, verification report |
| [references/portability.md](references/portability.md) | How the instructions for subagents, questions to the user and skill loading run in each tool (Claude Code, Codex, Copilot, Cursor, Windsurf) |

## Scripts

Python 3.10+ and the standard library only (plus `git` for the seal against the base branch and for mutants). They run from the root of the repository under test; `<qa-core>` is the path of this folder.

| Script | What it does |
|---|---|
| `scripts/seal.py` | Hashes the whole oracle; detects changes, symbolic links and reseals since the base branch |
| `scripts/traceability.py` | Chain criterion → scenario → test → result; skipped, not executed or a stale report are not green |
| `scripts/mutants.py` | Mutants in temporary worktrees; counts as detected only if a scenario fails |

Tests: `python3 -m unittest discover -s <qa-core>/scripts/tests`.
