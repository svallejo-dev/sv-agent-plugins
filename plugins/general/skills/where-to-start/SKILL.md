---
name: where-to-start
description: "Router for the sv-agent-plugins plugins: says which skill or workflow fits the situation (new idea, bug, system design, third-party integration, QA, PR, learning something) and what to do when a phase ends. Use it when the user does not know where to start, asks \"which skill do I use?\", \"what is the workflow?\" or asks to put an AGENTS.md with these plugins' rules into their repo."
license: MIT
---

# Where do I start?

Respond in the user's language; keep common technical terms in English.

Nobody remembers every skill, so ask here. This skill is a map: it says which path to take, it does not do the work.

**Analogy:** the map of a subway station. It does not take you anywhere; it tells you which line to take, where to change and at which station to get off.

**Before stating what a skill does or recommending skipping a step, read its `SKILL.md`**: the summaries on this page are for orientation, not the source of truth. Recommend only skills that are installed; if one is not, say which plugin brings it (`general`, `engineering`, `qa`, `architecture`, `go`).

## 1. Place the situation

If the situation is unclear, ask one or two questions: is there a repository? is it something new, something broken or something to improve? is there a third party or money involved?

| Situation | Start with | Continue with |
|---|---|---|
| New idea or feature, inside a repo | `grill-with-docs` | The main workflow (section 2) |
| Idea, plan or document without a repo | `grilling` | `to-spec` if it is going to be built |
| Designing or changing a system (scale, persistence, resilience, migration) | `system-design` | `capacity-estimation`, `design-stress-test`, `strategic-design`; then `to-spec` |
| Exploratory design without metrics | `system-design` in exploratory mode | `business-archetypes` to start from the kind of business that consumes it |
| Building a PoC | `system-design` in PoC mode | Build hypothesis by hypothesis from the experiment plan, without `to-spec` or `to-tickets` (section 2) |
| Integrating with a third party (payments, partner, SDK) | `to-spec` with the consumers section | `qa-test-design` (third-party checklist) and a walking skeleton as the first ticket |
| Something is broken or fails intermittently | `diagnosing-bugs` | If it comes from QA, with the reproduction command of finding `F-NN` |
| Reviewing a change or a PR | `code-review` | It never approves: it delivers findings |
| Dirty, noisy or outdated Go code | `go-simplify` | `go-review` to review the result |
| Designing the shape of a module or an interface | `codebase-design` | `go-design` if it is Go |
| The domain language is confusing, or a decision must be recorded | `domain-modeling` | ADR in `docs/adr/` |
| Are the tests any good? | `qa-test-the-tests` | `qa-verify` |
| Which testing tool do I use? | `qa-toolbox` | `qa-test-automation` |
| Researching a topic with primary sources | `research` | Take the result to `grill-with-docs` |
| Learning a concept over several sessions | `teach` | — |
| Switching tools or directories, or handing the work to someone else | `handoff` | — |
| Writing or improving a skill, a prompt or an AGENTS.md | `writing-for-agents` | — |

**Preconditions**, once per repo: `engineering-setup` (tracker, glossary, ADRs) and, if there is QA, `qa-setup`.

## 2. The main workflow: from idea to delivery

1. **Sharpen the idea**: `grill-with-docs`. If the idea is a system, go through `system-design` first.
2. **Specify**: `to-spec`. If there is QA, it also writes the handoff contract.
3. **QA, before implementing** (recommended if there are third parties, money or customer data):
   `qa-acceptance-criteria` → `qa-test-design` → `qa-test-automation`. The implementing agent never writes or edits these tests.
4. **Split into tickets**: `to-tickets`. If there is a new third party or external consumer, the first ticket is the walking skeleton.
5. **For each ticket**: `tdd` as the inner loop (with `go-testing` if it is Go) and `codebase-design` if a module must be designed. When closing the ticket: `qa-verify` per slice.
6. **Before the PR**: `go-simplify` (if it is Go) → `code-review` → `qa-test-the-tests` and full `qa-verify` → `git-commit` → `create-pr`.

Without separate QA, skip step 3 and the `qa-verify` steps: the risk is that the same agent that implements decides what "it works" means.

**For a PoC the workflow is different, and shorter:** `system-design` in PoC mode leaves the experiment plan (hypotheses, minimal scope, what to measure, success and abandonment criteria), and that plan is the spec. Build one hypothesis at a time with `tdd` only on the invariants, and close each one with its verdict and the measurement that backs it. No `to-spec`, no `to-tickets` and no full QA. When done, go back to `system-design` in production mode with the PoC as the existing system.

## 3. When a phase ends: continue, clear, hand off, delegate or compact

A **phase** is a chunk of work within a session: the design conversation, the implementation, the review. This decision is made **at the boundary** between two phases, not halfway through one. Go through the questions in order; the first "yes" decides. Details in [references/phase-boundaries.md](references/phase-boundaries.md).

1. **Can you continue in this session?** Yes, if the next phase needs this conversation as is (design → implementation) and there is plenty of context left. Continuing costs nothing and loses nothing.
2. **Is what happened in this session irrelevant to what comes next?** Then clear the context (`/clear` in Claude Code; in other tools, a new conversation).
3. **Are you switching tools, directories or people?** Then `handoff`.
4. **Can the task be done without you, well bounded?** Then delegate it to a subagent and leave this session intact.
5. **Otherwise, compact** (`/compact` where it exists; otherwise, `handoff` and a new conversation) saying what the summary must keep.

## 4. Putting the rules in the repository

If the user asks to put these plugins' rules into their repo:

1. Copy [references/AGENTS-template.md](references/AGENTS-template.md) to `AGENTS.md` at the repository root. If it already exists, add the template as a section and delete nothing.
2. Remove the sections for plugins that are not installed and adjust the paths if `docs/agents/` says otherwise.
3. Codex, Copilot, Cursor and Windsurf read `AGENTS.md` directly. Claude Code, in its recent versions, loads it only if the project does **not** have a `CLAUDE.md`. So: if a `CLAUDE.md` already exists, add an `@AGENTS.md` line to it; if it does not exist, create one with that single line, which works the same in old and new versions and duplicates nothing.
4. Show them the result and do not commit unless they ask.
