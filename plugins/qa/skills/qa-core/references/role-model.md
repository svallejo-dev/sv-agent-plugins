# Role model of the qa plugin

Reference shared by every skill in `qa`. It defines who writes what, who approves and what information each one sees.

**Analogy:** a well-run exam. The one who studies (dev) does not write the questions; the one who writes them (QA) does not grade with the student's answer in view; the optical reader (deterministic executor) counts the correct answers; and the teacher (human) decides whether it is a pass. If one person does all four, a perfect score means nothing.

## The principle that does not change in any mode

**The implementing agent never writes or edits the oracle.** The oracle is the acceptance criteria, the scenarios and the executable acceptance tests. It does not matter whether there are one or two people behind it: the separation is between **agents with different contexts**, not between people.

Rationale: an agent that writes the code and its own acceptance tests shares its assumptions with them (oracle anchoring). And an agent under pressure from a red test can cheat: in ImpossibleBench (2025), the Claude and Qwen3-Coder models made over 79 % of their cheats by modifying tests, while other models preferred *special-casing* (code that recognizes the test data and answers what the test expects). The authors recommend hidden or read-only tests, and warn that read-only does **not** eliminate special-casing. That is why this plugin combines three defenses: read-only, sealed tests; random test data without recognizable markers; and human review of the code and of every reseal.

## Roles

| Role | Who | Writes | Never |
|---|---|---|---|
| **Dev** | Implementing agent (`tdd`) | Code and its unit and integration tests (inner loop) | Edit criteria, scenarios, acceptance tests or the seal |
| **QA** | Test-design agent, with a clean context | Criteria, scenarios, acceptance tests, learning tests, mutants | Read the body of the production code; edit production code |
| **Executor** | Runners and the scripts in `scripts/` | Results: JUnit, seal, traceability, mutants | Give opinions: it only counts |
| **Human** | The dev (solo mode) or QA and the dev (duo mode) | Approvals and escalation decisions | Delegate approval to an agent |

**QA does not certify.** No agent declares "approved", "ready for production" or "certified". `qa-verify` delivers evidence and the status of each gate; the decision is human.

## Operating modes

Declared in `docs/agents/qa.md` (`qa-setup`).

**The contamination rule** (if a session has already seen the feature's production code, it does not write the oracle) is also good faith, like N1: no gate checks what a session read. It is declared, not proven.

### Solo mode: the dev designs the tests

One person acts as dev and as approver of the criteria.

- A **QA subagent** with a clean context writes the criteria and scenarios, with a closed brief: it receives only the handoff contract, never the diff or the code. If the main session has already implemented code, it **cannot** write the scenarios itself: it is contaminated.
- The human approves criteria and scenarios **before** the ticket's implementation starts.
- The mode's own risk: **author bias**. The same person wrote the spec and approves the tests, so they share its blind spots. **Mandatory** mitigations in this mode:
  1. The design techniques of `qa-test-design` are applied in full, without hand-picking which to skip: they are the checklist the author did not write.
  2. Criteria premortem in `qa-acceptance-criteria`.
  3. `qa-test-the-tests` is a mandatory gate of the full cadence, not optional.

### Duo mode: separate QA

A human QA runs the `qa` plugin; the dev runs `engineering`.

- QA's input is the **handoff contract** (see [formats.md](formats.md)). `qa-test-design` refuses to start if a mandatory piece is missing.
- The dev reviews the scenarios only to confirm they are **feasible** (that the system exposes what is needed to observe them), not to cut them. It is an asynchronous "three amigos": business (spec), dev and QA look at the same scenario before building.
- The mode's own risk: **incomplete handoff**. Without testability seams, QA cannot test the hard cases from the outside.

## Information barrier: three levels

The barrier between what QA sees and the code is declared in the configuration, and `qa-verify` reports which one was used. Declaring it honestly is part of the rigor: an N1 that claims to be N3 is worse than a declared N1.

| Level | How | What it guarantees |
|---|---|---|
| **N1: convention** | Subagent with a brief that forbids reading the production code | Context separation; reading code is not prevented, only instructed |
| **N2: isolated directory** | QA works in a copy that contains only `.scratch/<feature>/`, the API contracts and the acceptance folder | The code is not available in its working directory |
| **N3: different person** | Another human with their own session and no access to the code repository | Real information separation |

QA in **gray box**: sees the spec, the architecture (which dependencies exist), the API contracts and the testability seams. It does not see the body of the code.

## Escalation: when the dev believes a test is wrong

The dev **never** edits an acceptance test to make it green, even when convinced the test is wrong. They escalate:

1. Record the entry in `.scratch/<feature>/qa/escalations.md` (format in [formats.md](formats.md)) with the scenario, the argument and the evidence.
2. Stop work on that scenario, not on the whole ticket.
3. QA (or the human in solo mode, with the QA subagent) resolves with one of three decisions:
   - **Test fixed**: the test did not reflect the criterion. QA fixes it and reseals citing the escalation (`--reason "E-03: ..."`).
   - **Spec fixed**: the test reflects the spec, but the spec was wrong. Go back to `qa-acceptance-criteria` and, if needed, to the spec.
   - **Rejected**: the test is correct; the code must change.

Every test fix stays in the seal history with its reason, which must cite the `E-NN` or `F-NN` that caused it.

**What the seal guarantees and what it does not.** The seal does not prevent editing: an agent can edit a test and reseal. What it guarantees is that it cannot do so **without it showing**: `qa-verify` compares the seal against the one on the base branch and lists every seal and reseal made since then; a reseal of a seal that already existed on the base without `E-NN`/`F-NN` breaks the gate, and so does deleting or recreating the seal. The decision about those reseals is human, in the PR review. Preventing edits by role (hooks) is future work.

## Map of artifacts and permissions

| Artifact | Default path | Writes | Approves |
|---|---|---|---|
| Spec | `.scratch/<feature>/spec.md` | Dev (`to-spec`) | Human |
| Handoff | `.scratch/<feature>/qa/handoff.md` | Dev | QA (accepts or returns it) |
| Criteria | `.scratch/<feature>/qa/criteria.md` | QA | Human |
| Scenarios | `.scratch/<feature>/qa/scenarios.md` | QA | Human; the dev confirms feasibility |
| Acceptance tests and rung scripts | `<Acceptance>/<feature>/` and `<Acceptance>/bin/` (see `docs/agents/qa.md`) | QA | Human reviews Gherkin and Hurl, not the plumbing |
| QA configuration | `docs/agents/qa.md` | QA or human, never the dev | Human |
| Seal | `<Acceptance>/<feature>/.qa-seal.json` (covers criteria, scenarios, tests, rung scripts and the configuration) | QA, via `scripts/seal.py` | Human reviews every reseal listed by `qa-verify` |
| Escalations | `.scratch/<feature>/qa/escalations.md` | Dev opens, QA or human resolves | Human |
| Verifications | `.scratch/<feature>/qa/verifications/` | Executor and `qa-verify` | — |
| Mutants | `.scratch/<feature>/qa/mutants/` | Mutation agent (`qa-test-the-tests`) | Human decides on the equivalent ones |
