# Starting point

Step 0 of the design. Its goal is that nobody designs on a blank sheet: there is always something to start from, whether an occupied building, a neighbor who already built something similar or, at the very least, the kind of building you want to build. **Not having metrics never blocks the design.**

## Case 1: existing system

### AS-IS inventory

Fill in what you can by reading; ask only about what is not written anywhere.

| Area | What to capture | Where to look |
|---|---|---|
| Topology | Services, databases, caches, queues, third parties; who calls whom (synchronous or asynchronous) | Code, deployment manifests, existing diagrams, APM (service map) |
| Critical flows | The 2-4 paths that matter most to the business, end to end | Conversation, RFCs, product |
| Data | Which service writes each table/topic, volume, growth, retention | Code, migrations, database metrics |
| Measured numbers | Peak throughput, p50/p95/p99, errors, utilization, lag | APM and logs (see `capacity-estimation`) |
| Objectives | Current or implicit SLOs, RPO/RTO, latency budget | Operations docs, contracts |
| History | Incidents and postmortems from the last year, load tests, known bottlenecks | Postmortems, runbooks, tickets |
| Debt | What the team knows is wrong and why it has not been fixed | Conversation, ADRs, TODOs |
| Constraints | Compliance (PCI, personal data), partner contracts, mandated stack, budget | Conversation, legal, contracts |
| Teams | Who owns each part and who has capacity | Conversation, CODEOWNERS |
| Previous decisions | Why it was done this way (ADRs, RFCs); what was tried and discarded | Docs, repo history |

### Result

- A Mermaid diagram of the AS-IS (simple, honest, even if ugly).
- The table of measured numbers with their source.
- The list of pains: what hurts today, measured if possible ("p99 of 2 s at checkout on campaign days").
- The gaps: what is not known and how to find out.

An AS-IS that only exists in someone's head is the project's first risk: writing it down is already value.

## Case 2: similar path

When there is no system of your own, the starting point is what others already solved.

1. With `research`, look for two or three similar systems with primary documentation: engineering blogs of the company that built it, papers, talks with slides, public design docs. Prioritize sources that tell **why** they decided, not just what.
2. For each one, extract: declared scale, constraints, key decisions, what they changed over time and why.
3. Compare with your case: which forces you share and which you do not. What was necessary for them at their scale may be over-engineering at yours.
4. Cite each source. A "that is how Netflix does it" without a link is not an argument.

## Case 3: business archetype (no system or metrics)

It is the normal case for an exploratory design or a PoC, and it is a valid starting point, not a last resort.

1. Identify the archetype with `business-archetypes` from the product description. If it mixes several, assign each one to its subdomain.
2. Extract from the archetype: dominant forces, invariants, shape of the load, typical subdomains, failure modes and the questions that change the design.
3. Ask the user those questions in the first round; they are the ones that stand in for the metrics.
4. Combine with case 2 when there are similar documented systems.
5. Record each assumption that comes from the archetype as such ("archetype assumption: ×100 peaks when sales open") and the measurement that will replace it (in the PoC or in production).

### Result

- A table of forces: what drives this business and why.
- The invariants that admit no error.
- Three order-of-magnitude scale scenarios (see `capacity-estimation`, exploratory mode).
- The list of assumptions with the measurement that will validate them.

## Signs that step 0 is incomplete

- The proposed alternatives do not mention any piece of the current system.
- The numbers are all assumptions even though the system exists and has APM.
- There are no metrics and the business archetype was not identified either: a generic system that does not exist is being designed.
- The design solves problems nobody reported and does not touch the measured pains.
- Nobody knows who owns the data the design moves.
