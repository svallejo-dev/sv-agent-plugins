# Quality rubric

Score the design from 0 to 5 on each dimension before closing it. Report the total, the weakest dimension and exactly what each dimension that does not reach 5 is missing. No design is considered finished without naming its weakest dimension.

Based on the rubric of [proyecto26/system-design-skills](https://github.com/proyecto26/system-design-skills) (MIT), adapted to existing systems.

| Dimension | 5 means | If it is low, invoke |
|---|---|---|
| **Starting point** | The AS-IS (or the similar reference, or the business archetype) is described: diagram and measured numbers if a system exists; explicit forces, invariants and assumptions if not; the gaps are named | `references/starting-point.md` |
| **Requirements** | Functional, non-functional and out of scope, as a delta, with business and compliance constraints | `building-blocks` → `requirements-scoping` |
| **Numbers** | With a system: peak, percentiles, growth and capacity measured and computed with a source. Without metrics: order-of-magnitude scenarios and computed decision thresholds, with a plan to measure them. Every number enables a decision | `capacity-estimation` |
| **Interfaces and data** | Request, response, primary key, pagination, idempotency and the owner of each piece of data are concrete | `building-blocks` → `api-design`, `data-storage` |
| **Trade-offs** | Every important decision has resolves / worsens / change it when with a measurable trigger; there were real alternatives | `system-design` response contract |
| **Boundaries** | The contexts and their relationships have a pattern and an owner | `strategic-design` |
| **Failures** | Red team done; risks with detection, mitigation and status | `design-stress-test` |
| **Operations** | SLOs, symptom-based alerts, runbooks and the ability to detect each relevant failure | `building-blocks` → `observability` |
| **Migration / experiment** | With a system: a step-by-step path, deployable, verifiable, with doors marked and rollback. In a PoC: hypotheses by risk, minimal scope, instrumentation, success and abandonment criteria, deliberate debt | `references/migration.md` |
| **Evolution** | It is known what breaks at ×10 and what would be done then | `building-blocks` → `scaling-evolution` |

## Quick diagnosis

When a design "is not quite convincing", go through these questions in order; the first one answered "no" tells you what to do next.

1. Do I know where I start from (system, reference or archetype) and what hurts or what drives it?
2. Do I know what changes and what does not (requirements as a delta)?
3. Do I have numbers with a source (measured, or scenarios and thresholds) for the decisions that depend on scale?
4. Was there at least one real alternative, including the minimal-change one?
5. Does each component have its three answers?
6. Did I attack the design and do I know how I would find out about each failure?
7. Can I get there from the current system without stopping it? (In a PoC: do I know which hypothesis I validate first and how I measure it?)
8. Did I sweep the building blocks and open or discard each one with a reason?
