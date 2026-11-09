---
name: to-tickets
description: "Splits a plan, a spec or the current conversation into tracer-bullet tickets (vertical slices), each with its blockers declared, and saves them as one file per ticket in the local tracker. Use it only when the user explicitly asks for it."
license: MIT
---

# To Tickets

Respond in the user's language; keep common technical terms in English.

Splits a plan, spec or conversation into **tickets**: **tracer-bullet** vertical slices, each with the tickets that **block** it.

Analogy: a tracer bullet is the round that leaves a visible trail from end to end; each ticket crosses every layer thinly, so you see right away whether the whole path works.

Read `docs/agents/tracker.md` to know where and how to save the tickets. If it does not exist, tell the user to run the `engineering-setup` skill and stop.

## Process

### 1. Gather context

Work with what is already in the conversation. If the user passes a reference (the path of a spec or a ticket), read it in full, including its comments.

### 2. Explore the code (optional)

If you have not explored the code yet, do it to understand its current state. Ticket titles and descriptions use the vocabulary of `GLOSSARY.md` and respect the area's ADRs.

Look for **prefactoring** opportunities that make the implementation easier: "first make the change easy, then make the easy change".

### 3. Design vertical slices

Split the work into tracer-bullet tickets.

<vertical-slice-rules>

- Each slice goes through a narrow but COMPLETE path across every layer (schema, repository, service, handler, tests): vertical, NOT a horizontal slice of a single layer.
- A finished slice can be demonstrated or verified on its own.
- Each slice fits in a single fresh context window.
- Any prefactoring goes first.
- **Walking skeleton first when there is a new third party or external consumer**: ticket `01` is the thinnest slice that crosses the whole path with the real integration (the third party's sandbox, the SDK or the consumer that validates the result), without business logic or cache. It is done when the real consumer accepts what the system produces. If the integration is misunderstood, it fails here, on the first day, and not after building everything on top.

</vertical-slice-rules>

Analogy: the walking skeleton is stringing the first rope of a suspension bridge from bank to bank. It carries no traffic, but it proves both banks can be reached before investing in the deck.

Give each ticket its **blockers**: the tickets that must finish before it can start. A ticket without blockers can start now.

**Wide refactors are the exception.** A **wide refactor** is a mechanical change (renaming a column, changing the type of a shared symbol) whose **blast radius** extends across the whole codebase: a single edit breaks thousands of call sites and no vertical slice can stay green. Do not force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form next to the old one so nothing breaks. Then migrate the call sites in batches according to the blast radius (per package, per service), each batch its own ticket blocked by the expansion, keeping CI green because the old form still exists. Finally contract: delete the old form when no caller remains, in a ticket blocked by every batch. If not even the batches can stay green on their own, keep the sequence but have them share an integration branch and block a final integrate-and-verify ticket; green is only promised there.

Analogy: expand–contract is like replacing a bridge without stopping traffic. You build the new one next to it, divert the lanes one by one and only then demolish the old one.

### 4. Validate with the user

Present the proposal as a numbered list. For each ticket show:

- **Title**: a short, descriptive name
- **Blocked by**: which tickets must finish first (if any)
- **What it delivers**: the end-to-end behavior this ticket makes work

Ask:

- Does the granularity feel right? (too coarse / too fine)
- Are the blockers correct: does each ticket depend only on the ones that really block it?
- Should any ticket be merged or split further?

Iterate until the user approves the split.

### 5. Save the tickets

Write one file per ticket at `<tracker-path>/<feature-slug>/tickets/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first). One ticket per file, never a combined one. If the source was a spec, link it in each ticket. Do not modify the spec or any parent ticket.

<ticket-template>

# <NN>: <Ticket title>

Status: ready-for-agent
Blocked by: <numbers of the tickets that block it, or "None">
Spec: <relative path to spec.md, if it exists>

## What to build

The end-to-end behavior this ticket makes work, from the user's perspective, not a list of layer-by-layer changes.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

If approved QA criteria exist (`.scratch/<feature>/qa/criteria.md`), reference their IDs (`AC-03`) instead of rewriting them: a single source of truth. And if approved scenarios exist (`.scratch/<feature>/qa/scenarios.md`), add below `Spec:` the line `Scenarios: SC-01, SC-04` with the scenarios of those criteria this ticket must turn green: it is the scope of `qa-verify` in the per-slice cadence.

</ticket-template>

Avoid file paths and code snippets: they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose (a state machine, a schema, the shape of a type), include it and say it comes from a prototype, trimmed to what holds the decision.

When done, tell the user which is the **frontier**: the tickets without blockers, where work starts.
