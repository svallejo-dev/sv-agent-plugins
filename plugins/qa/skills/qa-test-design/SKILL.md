---
name: qa-test-design
description: "Designs a feature's test scenarios from approved criteria and the handoff contract, with parallel subagents per technique (partitions and boundaries, decision tables and states, third parties and usage oracle, failures and environment, error guessing and abuse); assigns each scenario to a rung and traces it to its criteria. Use it when the user asks to \"design tests\", for \"test scenarios\", \"test cases\", a \"test plan\", or after approving criteria with qa-acceptance-criteria."
license: MIT
---

# Scenario design

Respond in the user's language; keep common technical terms in English.

Turns approved criteria into concrete scenarios: exact data, action, expected result and oracle, each on the rung where it can fail for the right reason. This is the cheapest layer for finding spec defects: a scenario is written in minutes and can reveal that nobody knows what should happen.

**Analogy:** a bridge inspector does not test "whether the bridge holds". They test the maximum load, the load just above it, crosswind, traffic stopped in the middle and a truck braking hard. Each technique is a systematic way to choose which loads to test without relying on the day's intuition.

First read [../qa-core/references/role-model.md](../qa-core/references/role-model.md), [../qa-core/references/environment-ladder.md](../qa-core/references/environment-ladder.md) and [../qa-core/references/formats.md](../qa-core/references/formats.md).

## 0. Preconditions: if something is missing, stop

1. `docs/agents/qa.md` exists. If not, ask to run the `qa-setup` skill and stop.
2. `.scratch/<feature>/qa/criteria.md` has `Status: approved`. If it is a draft, stop: scenarios are designed against approved criteria, not drafts.
3. **Handoff contract** (`.scratch/<feature>/qa/handoff.md`) with the mandatory pieces: surface, consumers, dependencies and executable artifact, and every testability seam answered. If a mandatory piece is missing, **do not design**: list what is missing, mark the handoff `Status: returned` and tell the user what the dev must complete. In solo mode, the human completes the handoff before continuing.
4. **Contamination rule**: same as in `qa-acceptance-criteria`. If this session saw the feature's production code, all the design happens in the subagents of step 1, and the consolidation (step 2) is delegated to another clean subagent that receives only their outputs; the main session runs the script, presents and seals.

## 1. Parallel subagents, one per family of techniques

Launch the five subagents together, each with a clean context. Each subagent receives: the approved criteria, the handoff, the API contracts, the environment ladder and **its** techniques section pasted in full from [references/techniques.md](references/techniques.md). None receives production code.

> **Portability:** if your tool has no subagents, follow [../qa-core/references/portability.md](../qa-core/references/portability.md) and declare it in the artifact.

| Subagent | Techniques | Additional material |
|---|---|---|
| A | Equivalence partitions and boundary values | — |
| B | Decision tables, state transitions, combinatorics (pairwise) | — |
| C | Third-party integration and usage oracle | [references/third-parties.md](references/third-parties.md) in full; [../qa-acceptance-criteria/references/usage-oracle.md](../qa-acceptance-criteria/references/usage-oracle.md) |
| D | Failures and environment: dependencies, time, concurrency, idempotency, data | The archetype's failure modes (`business-archetypes`) if it applies and is available |
| E | Error guessing, abuse and basic security | The system's previous incidents, if any |

Assignment for each one:

"You are QA for the feature <feature>. Apply ONLY your family of techniques (<family>) to these approved criteria. Do not read production code. For each scenario return one row: criterion(s) AC-NN, technique, proposed rung (with the ladder's assignment rule: the lowest where the behavior is observable and the oracle is reliable), scenario in Given/When/Then form with concrete data, oracle and, if it needs a testability seam, which one. If a criterion is ambiguous for your technique, do not resolve it by inventing: note it as a question. If you find a behavior no criterion covers, report it as a missing criterion, not as an orphan scenario. Respond in the user's language, as a table plus a list of questions and missing criteria."

**Why in parallel and separately:** a single agent applying every technique tends to stick with its first ideas and cut the rest. Each technique in its own context produces the cases that this technique, and only this one, finds.

## 2. Consolidate

1. **Missing criteria and questions** first: if any subagent found a behavior without a criterion or an ambiguity, it goes back to `qa-acceptance-criteria` before continuing. A scenario without a criterion is not added through the back door.
2. **Deduplicate**: two scenarios with the same behavior and equivalent data are one. Keep the technique that justifies it best.
3. **Group** as a scenario outline (table of examples) the cases that only vary in data: it is more readable and each row still counts.
4. **Assign IDs** `SC-NN` and the rung with the assignment rule. Do not move a scenario up a rung to dodge a missing seam: mark it `blocked-testability`. Scenarios that also serve as a smoke test in staging carry `1, 4` in the Rung column, with the same ID.
5. **Walking skeleton**: if there is a new third party or external consumer, the first scenario (`SC-01` when possible) is the thinnest end-to-end path with the real consumer, on rung 3. See [references/third-parties.md](references/third-parties.md).
6. **Prune by risk, not by fatigue**: if the set is too large, always keep the scenarios of critical-priority criteria, all the boundaries and all the invalid state transitions. What gets pruned stays in the same table with `Status: discarded` and the reason; it does not disappear silently.

## 3. Check coverage with the script

Write `.scratch/<feature>/qa/scenarios.md` in the format of [../qa-core/references/formats.md](../qa-core/references/formats.md) and run:

```bash
python3 <qa-core>/scripts/traceability.py \
  --criteria .scratch/<feature>/qa/criteria.md \
  --scenarios .scratch/<feature>/qa/scenarios.md
```

`<qa-core>` is the folder of the `qa-core` skill, a sibling of this one. The result must come out without gaps: every criterion with at least one executable scenario. A criterion covered only by blocked scenarios **is a gap**, not coverage.

## 4. Review and approval

Present to the human:
1. Open questions and missing criteria (if any remain).
2. **Testability debt**: blocked scenarios and which seam unblocks them.
3. Walking skeleton and usage-oracle scenarios.
4. The full table, grouped by criterion.

- **Duo mode**: the dev reviews only **feasibility** (does the system expose what is needed to observe it?). They can ask for clarification, not cut scenarios.
- **Approval**: only the human changes it to `Status: approved`. Never approve yourself.

## 5. Seal the design

With the design approved, seal the criteria, the scenarios and the QA configuration, so no agent changes them without leaving a trace (from the repo root; `<Acceptance>` comes from `docs/agents/qa.md`):

```bash
python3 <qa-core>/scripts/seal.py seal --seal <Acceptance>/<feature>/.qa-seal.json \
  --reason "design approved" .scratch/<feature>/qa/criteria.md .scratch/<feature>/qa/scenarios.md \
  docs/agents/qa.md
```

If the design changes later (a spec finding, a surviving mutant), reseal with `reseal` and a reason that cites the `E-NN` or `F-NN`. Next step: `qa-test-automation`.
