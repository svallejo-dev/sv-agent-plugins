# Exploratory design and PoC

When there is neither a system nor metrics, the design does not stop: it changes question. Instead of "which is the right architecture for this load?", ask **"which architecture stays reasonable across the whole range of plausible loads, and what must be learned first?"**.

**Analogy:** an explorer without a map does not stand still. They use the compass (the business archetype), advance over terrain that lets them turn back and note in their notebook what they learn, to draw the map later.

## Exploratory design

1. **Archetype as the starting point.** With `business-archetypes`, identify the kind of business and extract forces, invariants, subdomains and failure modes. If the product mixes archetypes, assign each one to its subdomain.
2. **Scenarios, not numbers.** Define three order-of-magnitude scenarios (small, medium, large) with `capacity-estimation` in exploratory mode. Design for the scenario the business considers likely at 12-18 months and check what breaks at the next one.
3. **Decision thresholds.** For each decision that depends on scale, compute the value at which it stops working ("a single primary works up to about X daily active users with this pattern"). That threshold goes into the "change it when…" column.
4. **Invariants before scale.** Business rules that admit no error (no overselling, no double charging, no mixing tenant data) are designed right from the start even if the load is small; scale can be gained later, correctness almost never.
5. **Two-way doors.** Prefer decisions that are cheap to reverse. One-way ones (the data model of the invariants, public contracts, a provider with lock-in) are flagged and taken with more evidence.

## PoC

A PoC exists to **reduce the most expensive uncertainty**, not to prove that something works in the happy case.

### Experiment plan

| Element | What it contains |
|---|---|
| **Hypotheses** | Falsifiable statements, ordered by risk × cost of being wrong ("the gateway supports 50 authorizations/s in sandbox with p99 < 2 s") |
| **Minimal scope** | Just enough to test each hypothesis; everything else is simulated, stubbed or bought |
| **Instrumentation** | The metrics that will replace the archetype's assumptions, active from day one |
| **Success criterion** | The measurable result that confirms the hypothesis |
| **Abandonment criterion** | The result that refutes it and what would be done then (change approach, change provider, cancel) |
| **Deliberate debt** | What is left out on purpose (high availability, multi-region, automation) and the condition for resuming it |

### Rules

- Attack first the hypothesis that, if false, invalidates the project (integration with a third party, an invariant under concurrency, unit cost).
- Test the failures, not just the happy path: timeouts, duplicates, concurrency on the same resource.
- Realistic distributions: skewed data and load (hot keys, giant users) instead of uniform ones.
- Instrument even if the PoC is small: the goal is to turn assumptions into measurements.
- At the end, write what was learned and which design assumptions change; that feeds the production version.

### From the plan to the code

The experiment plan **is the PoC's spec**. There is no need to run it through `to-spec` or split it with `to-tickets`: those skills are meant for production features and here they would duplicate the plan with a template that does not fit.

1. Build **one hypothesis at a time**, in the plan's order (the most expensive to get wrong first). If there is a third party, the first one is the walking skeleton against its sandbox.
2. Use `tdd` only for the core of invariants (no double charging, no overselling); the rest can be throwaway code.
3. Close each hypothesis with a **verdict** (confirmed, refuted or inconclusive), the measurement that backs it and what changes in the design. Record it in the plan section of the design doc, or in `results.md` next to it.
4. If a hypothesis is refuted, apply its abandonment criterion before moving on to the next one: the others may no longer matter.

`to-spec` only adds value if the PoC is built over several sessions or by someone else, to write down the implementation decisions (stack, data model); as a complement to the plan, not a substitute. To hand the work over, `handoff`.

### From PoC to production

When the PoC ends, go back to `system-design` in production mode with a **new starting point**: the PoC is now an existing system with its own metrics. The archetype assumptions that were measured are replaced by their real values; the ones that were not stay marked as assumptions.
