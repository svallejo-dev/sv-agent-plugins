---
name: code-review
description: "Reviews code changes in any language, either a local diff from a fixed point (commit, branch, tag) or a GitHub pull request (number, URL or branch), with parallel reviewers (Cross-cutting, one per language via the language plugins, and Spec) and findings with severity. Posts to GitHub only if asked and never approves. Triggers: \"code review\", \"review since main\", \"review this branch\", \"review this PR\", \"review PR #123\", \"PR review\"."
license: MIT
---

# Code review

Respond in the user's language; keep common technical terms in English. If the PR is written in another language, write the review in that language.

Reviews a change with three kinds of reviewer that run as **parallel subagents**, each with a clean context, so they do not contaminate each other:

- **Cross-cutting**: what holds in any language (correctness, security, tests, errors, compatibility, performance, size, migrations, observability, design smells). Rules in [CROSS-CUTTING.md](CROSS-CUTTING.md).
- **Language**: one for each language in the change that has a plugin installed. That language's own idioms, traps and conventions.
- **Spec**: does the code do what the spec, the ticket or the issue asked for?

Analogy: it is a building inspection. The general inspector checks the structure and the emergency exits on any site; the gas fitter only comes in if there is gas; and the client checks whether it is the house they ordered. If you merge them into a single voice, the loudest finding drowns out the others.

## 1. Pin the unit of review

- **Local diff**: the user gives a fixed point (SHA, branch, tag, `main`, `HEAD~5`). If they did not, ask. Capture `git diff <fixed-point>...HEAD` once (three dots, against the merge base) and `git log <fixed-point>..HEAD --oneline`. Confirm that the point resolves (`git rev-parse <fixed-point>`) and that the diff is not empty: a bad ref must fail here, not inside the subagents. The reviewed commit is `HEAD`.
- **Pull request**: the user gives a number, URL or branch. Follow [PR-GITHUB.md](PR-GITHUB.md) § Fetching the PR. The reviewed commit is the PR's `headRefOid`; never read files from the local working tree.

## 2. Intent, scope and size

Before judging code, pin down:

- **Intent**: which problem it solves (title, description, linked ticket or issue, commit messages). Correct code that does not meet the intent is still wrong.
- **Scope**: modules and consumers touched; any change to a public contract.
- **Size**: if it is too large to review rigorously or mixes concerns (refactor + feature + fix + mass formatting), asking for a split is the most valuable finding and goes first, with the proposed cuts. A shallow review of a huge change is worse than asking to split it.

## 3. Identify the spec

Look for the source spec in this order:

1. The PR description and the issue or ticket it links.
2. References in the commits (`#123`, `PROJ-1758`, ticket paths), resolving them according to `docs/agents/tracker.md` if it exists.
3. A path the user passed as an argument.
4. A `spec.md` or ticket in `.scratch/` (or the configured path), `docs/` or `specs/` that matches the branch or the feature.

If there is nothing, ask. If the user confirms there is no spec, the Spec reviewer is skipped and the report says so.

## 4. Identify the repo's standards

Look for every file that documents how code is written: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`, ADRs and linter configuration. Split them into two groups: those that apply to the whole repo (they go to the Cross-cutting reviewer) and those for a specific language, such as `.golangci.yml` or `.eslintrc` (they go to that language's reviewer).

**Precedence**: the repo's documented standard > the language plugin's rules > [CROSS-CUTTING.md](CROSS-CUTTING.md). What tooling already guarantees (formatters, configured linters, CI) is not reported.

## 5. Detect the languages and load their rules

List the changed files and group them by language according to their extension: `.go` → `go`, `.php` → `php`, `.ts`/`.tsx`/`.js` → `typescript`, `.py` → `python`, `.sql` → `sql`, `.java` → `java`, `.kt` → `kotlin`.

For each language, check whether `<language>-review` exists among your available skills:

- **It exists**: load it now (in Claude Code, with the Skill tool; in other tools, by mentioning its name or reading its SKILL.md). Its content is the rules you will paste into that language reviewer's prompt (the subagent cannot load them on its own). If that skill points to other skills of the same plugin for depth, load them too and summarize what is relevant.
- **It does not exist**: there is no reviewer for that language. Note it for the report ("no idiomatic reviewer for `.py`; cross-cutting review only") and do not improvise idiomatic rules.

Files without a programming language (YAML, Markdown, JSON, Dockerfile) only go through the Cross-cutting reviewer.

## 6. Launch the reviewers in parallel

Launch all the calls together, in the foreground, and aggregate what they return. Each subagent receives how to get the diff, the commit list, the reviewed commit and, for a PR, how to read files at that commit (see [PR-GITHUB.md](PR-GITHUB.md)).

**Cross-cutting**: the full diff, the repo's standards that apply to everything, and the full content of [CROSS-CUTTING.md](CROSS-CUTTING.md) pasted as is. Assignment: "Go through each changed file with the rubric's dimensions and the design smells. Do not report idioms of a specific language; another reviewer covers that. Each finding: severity, `path:line`, why it is a problem and a concrete fix. A documented repo standard takes precedence over the rubric. Under 500 words."

**One reviewer per language with rules**: only that language's files, the rules loaded in step 5 and the repo's standards for that language. Assignment: "Review only the `<extensions>` files with these `<language>` rules. Do not repeat the cross-cutting concerns (security, tests, compatibility, size) unless the problem is a mechanism specific to the language. Each finding: severity, `path:line`, why and a concrete fix. Under 400 words."

**Spec**: the diff and the spec (path or content). Assignment: "Report: (a) requirements the spec asked for that are missing or half-done; (b) behavior nobody asked for (scope creep); (c) requirements that seem implemented but whose implementation looks wrong. Quote the spec line in each finding and give it a severity. Under 400 words."

If there is no spec, skip that subagent.

> **Portability:** if your tool has no subagents, run each assignment in a new conversation with only its brief, or in sequence in this session, and declare in the result that there was no context isolation.

## 7. Aggregate

Use the output format of [CROSS-CUTTING.md](CROSS-CUTTING.md) § Output format, with one section per reviewer (`### Cross-cutting`, `### Go`, `### Spec`…). Within each section, order from most to least severe. Do **not** mix or reorder across sections: they are separate on purpose so one does not drown out another.

If two reviewers flag the same line for the same cause, keep the finding in the language section and mention it in one line in the other.

The **verdict** is global: any blocker or major in any section → request changes; only minor or nit → comment; nothing → "looks ready", and approval stays in a person's hands. Add a line with the count per section and severity, and one or two things the change does well.

If the unit was a PR, offer to post the review.

## 8. Post to GitHub (only if asked)

Only when the user explicitly asks to publish, post or comment on the PR. Follow [PR-GITHUB.md](PR-GITHUB.md) § Posting.

## Guardrails

- **Never approve** a PR (`--approve`, `event: APPROVE`), even if asked: approval is a human signature; tell the user to approve on GitHub.
- **Never reproduce a secret** found in the diff: describe the pattern and the location and mark it blocker.
- **Review only**: no push, merge, close, labels or PR edits, and no checkout in the user's working tree.
