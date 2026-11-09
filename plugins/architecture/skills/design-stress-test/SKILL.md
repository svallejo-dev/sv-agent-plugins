---
name: design-stress-test
description: "Red team for a design or an existing system. It launches parallel subagents, each with an attack family (load, dependencies, data, changes, infrastructure, operations, abuse), seeded with the system's real incidents and verified against its code and configuration; it returns a risk matrix with failure mode, detection and mitigation. Use it when the user asks for a \"stress test\", \"red team\", \"what can go wrong?\", \"pre-mortem\", \"will this hold?\" or a resilience review."
license: MIT
---

# Design stress test

Respond in the user's language; keep common technical terms in English.

Attacks a design (or a system that is already running) to find how it fails **before** it fails in production. Each attack family is worked by a different subagent, in parallel and with a clean context, so none of them anchors on the design's optimistic narrative.

**Analogy:** it is the wind tunnel. The wing looks fine on the drawing; the tunnel tells you at what speed it vibrates, where it breaks and whether the pilot finds out before it happens.

## 1. Gather the target and its history

- **The design**: design doc, RFC, diagram or the current conversation. If the target is an existing system, its current architecture.
- **The real system**, if it exists: the code and the configuration (timeouts, retries, pool sizes, queue limits, health checks, replicas), the dashboards and the alerts.
- **The history**: postmortems, incidents, runbooks, load test results. **An attack that already happened is worth more than an imagined one**: each past incident becomes a scenario to replay against the new design ("would this have prevented incident X?").
- **The objectives**: SLOs, RPO/RTO, latency budget, which degradation is acceptable for the business.

If the history or the objectives are missing, ask for them once; if they do not exist, carry on and flag it in the report. **Without a history of your own** (exploratory design, PoC, new product), seed the attacks with the typical failure modes of the business archetype (`business-archetypes`): they are the incidents others already suffered in that domain. Without formal objectives, use the archetype's invariants as the impact criterion (a duplicate charge or an oversale is critical even if there is no written SLO).

## 2. Choose the attack families

The families and their attacks are in [references/attack-catalog.md](references/attack-catalog.md). Select the ones that apply to the target; by default, all of load, dependencies, data and changes, plus infrastructure if there are availability requirements, plus abuse if there is a public surface.

For the mechanical detail of a specific component (how a cache, a queue or a load balancer behaves under stress), invoke `building-blocks` and extract the "Behavior under stress" section of the corresponding block to pass it to the subagent.

## 3. Launch one subagent per family, in parallel

Launch all the calls together, each with a clean context. Each subagent receives:

- The design (or the current architecture) and the objectives.
- Its attack family from the catalog, pasted in full.
- The relevant "Behavior under stress" sections from `building-blocks`.
- The past incidents that fall into its family.
- Read access to the repository, if it exists, with the assignment to **verify in the code and the configuration** each assumption ("the design says a 2 s timeout; does the config say so?").

> **Portability:** if your tool has no subagents, run each assignment in a new conversation with only its brief, or in sequence in this session, and declare in the result that there was no context isolation.

Assignment for each subagent:

"You are a reliability engineer looking for how this system fails in the <family> family. For each applicable attack, write a concrete scenario and answer: (1) **trigger**; (2) **propagation**: the chain of effects, layer by layer, including whether the system can get stuck in a degraded state even after the trigger goes away; (3) **detection**: which metric or alert fires and how long it takes, or 'nobody notices'; (4) **impact**: affected users, data at risk, SLO consumed; (5) **current status**: mitigated / partial / unmitigated, with the evidence (file:line of config or code, or section of the design); (6) proposed **mitigation**, distinguishing prevention, containment and recovery, with its cost. Discard the attacks that do not apply in one line. Do not invent configuration values: if you cannot verify them, say so. Respond in the user's language, in under 700 words."

## 4. Aggregate into a risk matrix

Order the findings by **severity** (impact × probability, with high probability if it already happened before) and deduplicate the ones that share a root cause: several attacks that end in "the database connection pool is exhausted" are a single risk with several triggers.

```markdown
## Stress test: <system>

**Target:** <design or system> · **SLOs:** <…> · **History used:** <incidents>

| # | Risk (root cause) | Triggers | Detection | Impact | Status | Mitigation | Cost |
|---|---|---|---|---|---|---|---|
| 1 | … | … | alert X in ~N min / nobody | … | unmitigated | … | … |

### Systemic risks
<the ones that cross families: correlated failures, retry loops, metastable states>

### Blind spots
<what could not be verified: config without access, metrics that do not exist>

### Next experiment
<the load test, game day or chaos experiment that would remove the most uncertainty>
```

## 5. Close the loop

- Risks that change the design go back to `system-design` as new constraints.
- Mitigations that are hard to reverse and have a real trade-off are recorded as an ADR with `domain-modeling`.
- Detection risks ("nobody notices") are translated into concrete SLIs and alerts.
- If a mitigation depends on numbers (pool, timeouts, replicas, headroom), compute them with `capacity-estimation`.
