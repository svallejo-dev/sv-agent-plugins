# Design doc template

Write it in the team's language. Remove the sections that do not apply instead of leaving them empty. If the repo already has an RFC or design doc template, use theirs and make sure it covers these sections.

~~~markdown
# Design: <system or change>

**Status:** draft | in review | approved · **Goal:** production | exploratory | PoC · **Authors:** … · **Date:** …

## 1. Context and starting point
What exists today (or which similar system was taken as a reference, with links, or which business archetype and with which forces and invariants), what hurts and why change now.

```mermaid
flowchart LR
  %% AS-IS
```

## 2. Requirements (as a delta)
- **Functional:** …
- **Non-functional:** latency, availability, consistency, scale, cost.
- **Constraints:** compliance, contracts, teams, stack.
- **Out of scope:** …

## 3. Numbers
| Figure | Value or scenario | Source (measured / reference / archetype / assumption) | Decision it enables |
|---|---|---|---|

Decision thresholds: the value at which each scale-dependent decision changes.

## 4. Alternatives considered
For each one: diagram, central idea, why yes and why not. Include the minimal-change one.

## 5. Proposed design
```mermaid
flowchart LR
  %% TO-BE
```
Interfaces (request, response, keys, idempotency) and data model with its owner.

## 6. Decisions and trade-offs
| Decision | Resolves | Worsens | Change it when… |
|---|---|---|---|

## 7. Boundaries and relationships
Context map with the pattern of each relationship (if applicable).

## 8. Failures and degradation
The red team's risk matrix: risk, detection, mitigation, status.

## 9. Operations
SLOs, alerts, dashboards, runbooks, spare capacity.

## 10. Migration path (or experiment plan if it is a PoC)
| Step | What changes | Pattern | Success signal | Door | Rollback |
|---|---|---|---|---|---|

In a PoC: | Hypothesis | Minimal scope | Instrumentation | Success | Abandonment | and the list of deliberate debt.

## 11. Evolution
What breaks first at ×10 and what would be done then.

## 12. Topics, open questions and accepted risks

### Topic register

| Topic | Status | Decision or pending question | Basis |
|---|---|---|---|
| | open / closed / deferred | | measurement / reference / archetype / assumption |

A topic closed on an assumption can be reopened: note which signal would reopen it. Deferred topics carry the condition for resuming them.

### Accepted risks

| Risk | Why it is accepted | How it is detected if it happens |
|---|---|---|

### Validation before sharing
- [ ] The starting point (AS-IS, reference or archetype) is described and every number has a source
- [ ] There are at least two alternatives, one of them the minimal change
- [ ] Every decision has a measurable trigger
- [ ] The red team is done and every risk has detection
- [ ] The migration path marks the one-way doors
- [ ] The rubric is scored and the weakest dimension is named
- [ ] No open topics are left without an owner or a date, or they are declared deferred
~~~
