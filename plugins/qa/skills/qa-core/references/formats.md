# QA artifact formats

Shared reference. The scripts in `scripts/` read the criteria and scenario formats, so **the parts marked "parseable" are not optional**: a mistyped ID breaks traceability.

They all live in `<Tracker>/<feature>/qa/` (`.scratch/` by default; the `Tracker:` key in `docs/agents/qa.md` wins). This document and the skills write `.scratch/` for brevity.

## Identifiers

| Prefix | What it identifies | Example |
|---|---|---|
| `AC-NN` | Acceptance criterion | `AC-03` |
| `SC-NN` | Scenario | `SC-12` |
| `F-NN` | Finding | `F-04` |
| `E-NN` | Escalation | `E-02` |
| `M-NN` | Mutant | `M-07` |

At least two digits (`AC-1` is invalid and the scripts reject it), numbered per feature, and a discarded ID is never reused: it is marked `discarded`.

## 1. Handoff contract (`handoff.md`)

The dev writes it; QA accepts it or returns it. `qa-test-design` refuses to start if a mandatory piece is missing.

```markdown
# Handoff: <feature>

Status: draft | accepted | returned
Spec: ../spec.md

## 1. Surface (mandatory)
API contract: <path to OpenAPI / AsyncAPI / proto> or, if none exists, the list of endpoints and events with their shape.

## 2. Consumers of the result (mandatory)
| Consumer | What it consumes | How it validates that it works for them (usage oracle) |
|---|---|---|

## 3. Dependencies (mandatory)
| Dependency | Own / third party | Sandbox or test environment | Official documentation |
|---|---|---|---|

## 4. Executable artifact (mandatory: at least one)
- Image or start command: <how to bring the service up and with which variables>
- URLs per environment: <dev, staging…> (no secrets)

## 5. Testability seams (mandatory to answer each one)
| Seam | Status | How it is used |
|---|---|---|
| Data seeding through an API or a non-production setup endpoint | available / no / not applicable | |
| Controllable clock | | |
| Dependencies configurable by variable (for fakes and Toxiproxy) | | |
| Data isolation (tenant or test accounts) and cleanup | | |
| Accessible observability (trace-id or correlation-id in responses and logs) | | |

## 6. Constraints
PCI, real data forbidden, sandbox rate limits, environment usage windows.
```

A seam with status `no` does not block the handoff: it produces `blocked-testability` scenarios and an explicit debt.

## 2. Acceptance criteria (`criteria.md`) — parseable

```markdown
# Acceptance criteria: <feature>

Status: draft | approved
Mode: solo | duo
Spec: ../spec.md

## AC-01: <short title in business language>
- Behavior: <what is observed from the outside, in one sentence; no implementation details>
- Oracle: <who or what decides it holds; if someone else consumes the result, the consumer>
- Source: <spec section or story; "inferred" if it is not in the spec, and then it needs confirmation>
- Type: functional | failure | security | contract | performance
- Priority: critical | high | medium
- Status: discarded        (only if discarded; with the reason on the next line)
```

**Parseable:** each criterion starts with an `## AC-NN:` heading (level 2 or 3). The scripts recognize criteria only by that heading (those inside code blocks do not count). A criterion with the line `- Status: discarded` stops requiring scenarios, and no active scenario may reference it.

## 3. Scenarios (`scenarios.md`) — parseable

```markdown
# Scenarios: <feature>

Status: draft | approved
Criteria: ./criteria.md

| ID | Criterion | Technique | Rung | Scenario | Oracle | Status |
|---|---|---|---|---|---|---|
| SC-01 | AC-01 | boundaries | 1, 4 | Given a customer with 4 devices, when they register one, then 201 | response + listing | active |
| SC-02 | AC-01, AC-04 | decision table | 3 | … | SDK initialized in sandbox | active |
| SC-03 | AC-02 | dependency failure | 1 | … | … | blocked-testability |
| SC-04 | AC-02 | boundaries | 1 | … (pruned by risk: covered by SC-01) | … | discarded |
```

**Parseable:**
- The table header must have the columns `ID`, `Criterion`, `Rung` and `Status` (in any order; there may be more columns).
- `Criterion` accepts several IDs separated by commas.
- `Rung` is one or more numbers on the ladder (1 to 5), separated by commas: `1, 4` means the same scenario runs on the hermetic rung and as a smoke test in staging, with the same ID.
- `Status`: `active`, `blocked-testability` or `discarded`. Scenarios pruned by risk go in the same table as `discarded`, with the reason in the Scenario column.
- There may be several tables (for example one per criterion); every table with an `ID` column is read as a scenario table and must follow this format.
- To write `|` inside a cell, escape it: `\|`.

Below the table, the detail of each scenario that needs it (exact data, steps, why that rung), under an `### SC-NN` heading.

## 4. Traceability convention in executable tests — parseable

Each acceptance test carries the ID of **a single** scenario **in the name that appears in the JUnit report**. A JUnit case with two IDs is a gap: one test, one scenario. In the sources, the ID only counts if it is in the **test title** or in the **file name**; a comment saying "covers SC-03" implements nothing.

| Tool | Where the ID goes |
|---|---|
| Gherkin (godog, Cucumber, Karate) | In the title: `Scenario: SC-04 device limit` (in an outline, each row inherits the ID) |
| Hurl | In the file name: `SC-07-idempotency.hurl` |
| Playwright | In the test title: `test('SC-09 SDK initializes with the token', …)` |
| Go (`testing`) | In the subtest: `t.Run("SC-11 provider timeout", …)` (in the JUnit report it shows as `SC-11_provider…`; the script recognizes it) |

A test without an ID is a test nobody can trace back to a criterion: `scripts/traceability.py` reports it.

## 5. Finding

Issued by `qa-verify`. It goes in the verification report and, if its class is code or configuration, it is also passed to the dev.

```markdown
### F-03: <symptom in one sentence>
- Scenario: SC-07 · Criterion: AC-02 · Severity: blocker | major | minor
- Class: code | configuration | spec | test | environment | undetermined (see qa-verify)
- Failed at rung: 4 · Lowest rung that reproduces it: 1
- Reproduction: `<exact command>`
- Expected: <…>
- Observed: <…>
- Evidence: <redacted request and response, trace-id, relevant log lines>
- Behavior hypothesis: <optional; about the observable behavior, never about code QA did not see>
- Status: open | in-progress | resolved | discarded
```

## 6. Escalation (`escalations.md`)

```markdown
## E-02: SC-05 seems to contradict the spec
- Date: 2026-11-08 · Opened by: dev · Scenario: SC-05 · Criterion: AC-03
- Argument: <why the dev believes the test is wrong>
- Evidence: <spec §, third-party response, official doc>
- Decision: pending | test-fixed | spec-fixed | rejected
- Resolved by: <QA or human> · Reason: <…>
```

This file does not prove who decided: anyone can write "Resolved by: human". The real attribution is the commit authorship and the PR review, where `qa-verify` lists every reseal since the base branch.

## 7. Verification report (`verifications/<date>-<cadence>.md`)

```markdown
# Verification: <feature> · cadence <per-slice | full | post-deploy> · <date>

Mode: solo | duo · Barrier: N1 | N2 | N3 · Fingerprint: HEAD <sha> + changes <sha> · Run: <Reports>/<feature>/<id>/

## Gates
| Gate | Status | Evidence |
|---|---|---|
| Seal intact | ok / broken | seal.py output |
| Traceability complete | ok / gaps | traceability.py output |
| Scenarios of the cadence green | N/M | JUnit reports |
| … | | |

## Criteria
| Criterion | Scenarios | Status |
|---|---|---|

## Findings
<F-NN…>

## Not executed and why
<rungs not available, blocked by testability>
```

The report does **not** contain the word "approved" or equivalents. It ends with the gates and what is missing; the human decides.
