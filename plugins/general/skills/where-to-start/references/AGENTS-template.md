# Rules for agents

This repository uses the plugins from [sv-agent-plugins](https://github.com/svallejo-dev/sv-agent-plugins). Skills are named here by their bare name (`tdd`); in Claude Code they carry the plugin prefix (`engineering:tdd`, `qa:qa-verify`).

## Language

Respond in the user's language; keep common technical terms in English. Explain new concepts with their canonical name and an analogy.

## Where to start

If it is not clear what to do, use the `where-to-start` skill. Before stating what a skill does, read its `SKILL.md`.

Once per repo: `engineering-setup` and, if there is QA, `qa-setup`. Their decisions live in `docs/agents/`; read them before working.

## Workflows

- **Feature**: `grill-with-docs` → `to-spec` → (QA: `qa-acceptance-criteria` → `qa-test-design` → `qa-test-automation`) → `to-tickets` → per ticket `tdd` + per-slice `qa-verify` → `go-simplify` → `code-review` → `qa-test-the-tests` + full `qa-verify` → `git-commit` → `create-pr`.
- **Bug**: `diagnosing-bugs`. First a command that reproduces the failure red; then the fix, with a regression test.
- **System or migration**: `system-design` (with `capacity-estimation`, `design-stress-test` and `strategic-design`) → `to-spec`.
- **PoC**: `system-design` in PoC mode → build hypothesis by hypothesis from the experiment plan (no `to-spec` or `to-tickets`) → a verdict with a measurement per hypothesis → `system-design` in production mode.
- **Third-party integration**: the spec declares the consumers of the result; the first ticket is the walking skeleton with the real consumer; learning tests against the sandbox before writing fakes.

## Rules

### Work and traceability

- Specs and tickets live in the tracker from `docs/agents/tracker.md` (by default `.scratch/<feature>/`). A ticket is blocked while its `Blocked by:` line lists open tickets.
- Domain terms are those in `GLOSSARY.md`; hard-to-reverse decisions go as an ADR in `docs/adr/`.
- Do not commit, push, merge or do anything irreversible unless the user asks. Never: secrets in commits, `--no-verify`, force-pushing to shared branches, merging PRs.

### Development

- `tdd` is the dev's inner loop: one behavior per cycle, a red test before the code, at the agreed seam.
- `code-review` delivers findings with severity; **it never approves**.
- Language-specific work comes from the `<language>-review`, `<language>-testing`, `<language>-debugging` and `<language>-design` skills.
- In Go: idioms and comments according to `senior-go-idiomatic`; `go-simplify` before the PR, without changing behavior or the exported API.

### QA (if the repo uses `qa`)

- **The implementing agent never writes or edits the oracle**: criteria, scenarios, acceptance tests, rung scripts, `docs/agents/qa.md` or the seal. If an acceptance test looks wrong, record an escalation in `.scratch/<feature>/qa/escalations.md` and move on to another scenario.
- **No agent certifies.** `qa-verify` delivers gates and findings; a ticket is not done while its scenarios are not green with the seal intact, and the decision to ship is human.
- A skipped, unexecuted or intermittent test is not a green test.
- Random, unmarked test data; production code never recognizes the tests' data, IDs (`SC-NN`) or paths.
- If another system consumes what you produce (a token, an event, a file), it is verified with that real consumer, not with the shape of the artifact.

### Architecture (if the repo uses `architecture`)

- Design as a delta: current state → target → migration. Not having metrics never blocks: work with order-of-magnitude scenarios and the business archetype.
- Every decision carries `Decision | Resolves | Worsens | Change it when…`, with a measurable trigger.
- Numbers are computed with `capacity-estimation` (in code), not from memory.

## When a phase ends

Before clearing or compacting the context, go through the questions in the "When a phase ends" section of `where-to-start`: continue, clear, hand off (`handoff`), delegate or compact, in that order.
