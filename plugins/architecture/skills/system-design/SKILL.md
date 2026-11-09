---
name: system-design
description: "Production-grade, large-scale system design sparring, also for exploratory designs and PoCs without metrics. It starts from what already exists (the current system, a similar documented system or the business archetype) and designs as a delta, current state → target → migration path, with computed numbers, alternatives with explicit trade-offs, a red team and recorded decisions. Use it when the user wants to design, redesign or evaluate an architecture (\"design\", \"how do we scale X?\", \"system design\", \"architecture for…\", \"review this RFC/design\", \"how do we migrate…?\")."
license: MIT
---

# System design

Respond in the user's language; keep common technical terms in English.

Takes a design problem from a vague idea to a justified, stress-tested architecture with a migration path, **by reasoning, not by recalling diagrams**. Every architecture is a hypothesis that holds while its assumptions hold.

**Analogy:** it is a renovation architect, not a new-build one. They start by surveying the plan of the occupied building, measure the real loads, propose two or three ways to renovate it, test each one against earthquakes and decide in which order to move the walls without evicting anyone.

## Way of working

Work in **rounds**: in each round ask the questions whose answers you can already use (the ones that do not depend on another pending one), numbered and with your recommended answer, and wait. Whatever you can find out yourself (code, documents, metrics), find it out; do not ask the user. Decisions belong to the user. If `grilling` exists, follow its round format.

When the user changes a constraint, name the assumption that is invalidated and redesign only the affected part. Defending a sunk design is worse than having started with a weak one.

**The user sets the pace.** They can stay on a topic for as many rounds as they want, go back to a closed one or jump to another. Do not move on to the next step of the loop until they ask or until the current step's topics are closed; if you believe it is worth moving on, propose it in one line and wait.

**Topic register.** Keep a living table of the topics that come up in the conversation:

| Topic | Status | Decision or pending question | Basis |
|---|---|---|---|
| Rule evaluation | closed | In the SDK, with cached rules | Latency ~0; streaming measured in the PoC |
| Multi-tenant | open | Per-tenant isolation in data or only in network? | Assumption: a single customer at first |

- Statuses: `open`, `closed` (with its decision) or `deferred` (with the condition for resuming it).
- The **Basis** column says what it rests on: measurement, reference, archetype or assumption. A topic closed on an assumption is marked as such, because it can be reopened.
- At the end of each round, one line: how many topics are still open and which ones. The full table, when the user asks for it.
- If there is a repo, persist the table in the design doc ("Topics" section); closed topics that are hard to reverse also become ADRs.

## The loop

### 0. Goal and starting point

First pin down the **goal of the design**, because it changes the rigor of each step:

- **Production**: it will run with real users; the full loop applies.
- **Exploratory**: comparing approaches, understanding a domain or preparing a proposal; no commitment to build it.
- **PoC**: building the minimum to validate the riskiest hypotheses; the result is learning, not a system. See [references/exploratory-and-poc.md](references/exploratory-and-poc.md).

Then establish where you start from. **Not having metrics never blocks the design**: use the best available starting point, in this order:

1. **Existing system**: survey the AS-IS (architecture, flows, data owners, measured metrics, SLOs, incidents, debt, contractual and team constraints). Read whatever exists: code, ADRs, RFCs, design docs, dashboards, postmortems.
2. **Similar path**: if there is no system of your own, use `research` to find two or three similar systems documented by those who already solved them (engineering blogs, papers, talks). Extract their forces and decisions, and mark what is different in your case: their scale is not your scale, their team is not your team.
3. **Business archetype**: if there is neither a system nor metrics (normal in an exploratory design or a PoC), identify the kind of business (streaming, fintech, ticketing, e-commerce, social, B2B SaaS, IoT, mobility, healthtech, AI platform, event platform) with `business-archetypes`. The archetype brings the dominant forces, the invariants, the shape of the load, the typical subdomains, the failure modes and the questions that change the design. It is combined with the similar path when there is one.

   **If you are designing an API, a platform or a component others use**, the archetype is that of the **business that consumes it**, not that of the API. A feature-flags API for a fintech inherits auditing and strict change control; for an e-commerce, campaign peaks and frequent deployments. What is specific to the API (how others solve the same technical problem) comes from the similar path. If there are several consumers, each archetype brings its requirements and the design covers their union or chooses one explicitly.

The full protocol is in [references/starting-point.md](references/starting-point.md). This step is complete when you can describe the starting point (AS-IS, reference or archetype) in a diagram or a table of forces, with the gaps made explicit.

### 1. Requirements as a delta

Functional, non-functional and **out of scope**, expressed as a change relative to the starting point ("today X; we need Y"). Include the requirements that do not show in a problem statement: compliance constraints (PCI, personal data), contracts with third parties, event calendars, available teams, budget. For the question catalog, invoke `building-blocks` and read its `requirements-scoping` block.

### 2. Numbers

Invoke `capacity-estimation`. In an existing system, measure before estimating. Without metrics, work with **order-of-magnitude scenarios** derived from the archetype and compute the **thresholds** at which each decision changes: the design does not need to know whether there will be 1,000 or 100,000 users, it needs to know from how many it stops working. Each number carries its source (measured, reference, archetype or assumption) and the decision it enables.

### 3. Alternatives

Propose **two or three** designs that answer the main tension differently (for example, synchronous vs event-based, sharing the database vs separating data, extending the current system vs replacing a part). One of them must be **the minimal change over what exists**. Include for each one a Mermaid diagram and its interface sketch (request, response, primary key, pagination, idempotency).

For each component, invoke `building-blocks` and read the corresponding block instead of rebuilding its recipe from memory. If the discussion is about boundaries between contexts or services, invoke `strategic-design`.

### 4. Trade-offs and decision

For each important decision answer the three questions: **what it resolves**, **what it worsens** and **what would make you change it**. See the response contract below. Compare the alternatives in those terms and recommend one, firmly.

### 5. Red team

Invoke `design-stress-test` on the chosen alternative (and on the current system, if the goal is to justify the change). Risks that change the design go back to step 3 or 4.

### 6. Migration path or experiment plan

In a PoC, this step is the **experiment plan**: hypotheses ordered by risk, the minimum that must be built to validate each one, what is instrumented from day one, success and abandonment criteria, and what is deferred on purpose (see [references/exploratory-and-poc.md](references/exploratory-and-poc.md)). In an exploratory design, it is enough to name the first step and the one-way doors there would be along the way.

In an existing system, design how to get from the current state to the target without stopping the system: ordered steps, each deployable and verifiable, with the pattern it uses (strangler fig, expand-contract, outbox, shadow traffic, dual-run with comparison, canary), its success criterion and whether it is **reversible** (two-way door) or not (one-way door). The patterns are in [references/migration.md](references/migration.md).

### 7. Iterate and close

Go deeper into the most fragile component. Before closing, do a **coverage sweep** with the `building-blocks` table: each plausible block is opened or explicitly discarded with one line. Score the design with [references/rubric.md](references/rubric.md) and name the weakest dimension.

## Response contract

Every design proposal (first or revised) includes, in the response itself:

- **Decision table**, at least three rows in a complete design:

  | Decision | Resolves | Worsens | Change it when… |
  |---|---|---|---|

  The last column is a concrete trigger, a number or an observable signal ("writes > 5k/s sustained on the primary", "a second team needs to deploy separately"), never "if needed".
- **Weak-point line**: what breaks first when the load or the requirements grow, and the move you would make then.
- In an existing system, the **delta**: what changes relative to the AS-IS and what stays the same.

A list of pros and cons, or trade-offs for a single decision, does not meet the contract.

## Persist

- **Design doc** with [references/design-doc-template.md](references/design-doc-template.md), at the path the repo uses (if there is no convention, `docs/design/<system>.md`; ask if in doubt). Discussions stay in the conversation; results go into the document.
- **ADRs** for decisions that are hard to reverse, surprising and with a real trade-off, using `domain-modeling`.
- New **domain terms** go to the glossary, with `domain-modeling`.

## Guardrails

- Clarify before designing and quantify before choosing: with measurements if they exist, with scenarios and thresholds if not. The lack of metrics is declared, not hidden, and it does not block.
- Justify each component with the three questions; "it is the industry standard" is not a justification.
- Know how each block behaves under stress, not just its name.
- The cheapest option that meets the constraints usually wins: a modular monolith before microservices, a relational database before sharding, until a number forces it.
- The limits of managed services (quotas, sizes, prices) are checked with `research` at the time; the model's memory has them out of date.
- No design is perfect: always close with the weak point and what you would do with an order of magnitude more.
