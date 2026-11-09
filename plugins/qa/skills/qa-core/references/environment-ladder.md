# Environment ladder and execution cadences

Shared reference. It answers two questions: **where** each scenario runs and **when** each group runs.

**Analogy:** building a car.
- The **crash lab** (hermetic environment) repeats the same impact a thousand times while controlling every variable.
- The **road test** (staging) is real, but you cannot ask a pedestrian to cross when you need one.
- The **fleet telemetry** (production) sees what really happens.

Nobody validates airbags on a public road, and nobody signs off the car just because it passed the lab.

## Black box is not the same as a deployed environment

They are independent axes:
- **Black box** is an **information** boundary: QA does not read the code.
- **Environment** is a **place of execution**.

QA tests black-box against the **PR image** brought up on rung 1 without seeing a line of code. It does not need a shared staging to avoid seeing the code.

## The rungs

One acceptance suite, parameterized by `base_url` and environment variables, climbs the ladder. The test artifact does not know where it runs.

| Rung | Where | What is tested there | Who runs it | Blocks? |
|---|---|---|---|---|
| **0. Inner loop** | Dev's machine | Dev's unit and integration tests (`tdd`) | Dev | Its own cycle; not QA's |
| **1. Hermetic** | Local or CI: service image + dependencies with Testcontainers + Toxiproxy + third-party fakes | Complete acceptance scenarios, **all** edge cases of state, time, failure and concurrency | QA | **Yes**: it is the main gate |
| **2. Contract** | Local, on demand or CI | Pact between own services (provider verification) and learning tests against third-party sandboxes | Dev (Pact consumer tests, with their code) and QA (learning tests, verification) | Yes, in the full cadence |
| **3. Isolated integrated** | Ephemeral environment per PR, header-based routing over staging, or a local stack pointing to real sandboxes | Walking skeleton with the real consumer; journeys with real dependencies | QA | Yes, if the platform offers it |
| **4. Shared staging** | After the deploy | Smoke and a regression subset of the critical paths; real configuration, auth and network | QA | No: it alerts |
| **5. Production** | Canary, flags, synthetic monitoring | 3 to 5 critical journeys as synthetic checks; canary metrics | SRE or platform | Rollback |

## Rule for assigning a scenario to a rung

**Assign each scenario to the lowest rung where (a) the behavior is observable and (b) the oracle is reliable.** Move it up only if the behavior depends on something the lower rung does not reproduce.

| If the scenario depends on… | Rung | Why not lower |
|---|---|---|
| Business logic, validations, boundaries, states | 1 | — |
| Time (expirations, windows, TTL) | 1, with a controllable clock | Staging does not let you move the clock forward |
| Dependency failures (timeouts, 5xx, dropped connection, partial response) | 1, with Toxiproxy or fakes | In shared staging you would break other teams |
| Concurrency and race conditions | 1 | Requires controlling the interleaving |
| Compatibility between own services | 2 (Pact) | — |
| Real behavior of a third party (what it returns, in what shape) | 2 (learning tests) | The fake only knows what you believed |
| The real consumer accepting what you produce (SDK, front end, partner) | 3 (walking skeleton) | Only the real consumer is a usage oracle |
| Configuration, secrets, permissions, DNS, auth between services | 3 or 4 | They only exist when deployed |
| Real volume, performance | Dedicated load tests (k6), outside the functional suite | — |

If a scenario needs a testability seam that does not exist (no way to seed data or control the clock), **do not move it up a rung to dodge the gap**: mark it `blocked-testability` and record it as debt. Moving it to staging turns it into a test that cannot fail for the right reason.

## The cadences

| Cadence | When | What runs | Target duration |
|---|---|---|---|
| **Continuous** | On each dev cycle | Rung 0 | Seconds |
| **Per slice** | When closing a ticket | The ticket's scenarios on rung 1 + seal + traceability | Minutes |
| **Full** | Before PR, merge or release (or nightly) | All of rung 1 twice (stability) + rung 2 + rung 3 if it exists + Schemathesis + mutant sampling | Tens of minutes without mutants; with mutants, (baseline + 5-10 mutants) × (build + suite): it can exceed an hour. Declare the budget in `docs/agents/qa.md` and, if it does not fit before the PR, run the mutants nightly and require the report for the diff before merging |
| **Post-deploy** | After deploying to staging | Rung 4: the scenarios that include 4 in their Rung column (smoke and critical regression, with the same ID as on rung 1) | Minutes |
| **Production** | Continuous | Rung 5: synthetics | — |

**Why acceptance tests do not run in the continuous cadence:** during implementation almost all of them are red by design. Running them on every cycle is slow and increases the dev agent's pressure on the oracle, which is exactly what we want to avoid. The dev works with their inner loop and looks at the acceptance tests per slice (double-loop TDD: Freeman and Pryce).

## The rungs your platform gives you

Before configuring, map which rungs the internal platform offers (ephemeral environments, test scopes, canary, synthetics) and which must be built. A rung that does not exist is declared "not available" in `docs/agents/qa.md`; the scenarios assigned to it are reported as not executed, never as green. And if a criterion only has scenarios on unavailable rungs, `traceability.py` marks it "no evidence in scope": the gate stays red and the report explains why. That is intentional: the walking skeleton of the PayPal case cannot come out green because nobody ran it.
