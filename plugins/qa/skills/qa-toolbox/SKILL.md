---
name: qa-toolbox
description: "QA tools radar (adopt, trial, assess, hold) and a guide to choosing the tool for each scenario by rung, by the artifact the human reviews and by how deterministic the runner is. Use it when the user asks \"which tool do I use for…?\", \"Karate or Hurl?\", \"how do I test X?\", or when qa-test-automation has to choose a tool for a scenario."
license: MIT
---

# QA toolbox

Respond in the user's language; keep common technical terms in English.

Choosing a tool is choosing which artifact the human will review and how reliable the runner is. **Libraries are not reinvented**: for each need there is a mature tool; the agent's job is to choose it well and write the plumbing.

**Analogy:** a carpenter's toolbox. You do not make a hammer every time you drive a nail; you choose the hammer, the mallet or the nail gun depending on the wood, and what matters is the furniture.

## Selection criteria

With agents writing the plumbing, whether the human knows the language stops mattering. What matters:

1. **Readability of the artifact the human approves**: Gherkin and Hurl can be read without programming; a Go test cannot.
2. **Runner determinism**: same state, same result; no fixed waits or order dependencies.
3. **Rung**: where it can run (see [../qa-core/references/environment-ladder.md](../qa-core/references/environment-ladder.md)).
4. **What it needs**: the image? controlling the network? the code? (Only the dev uses tools that need the code.)
5. **That it produces JUnit**: without a traceable report, `qa-verify` cannot count.

## Choice by need

| Need | Tool | Rung |
|---|---|---|
| Business rule readable by the business, with example tables | Gherkin + godog (Go), Cucumber (JVM or JS), behave (Python) | 1 |
| Multi-request HTTP flow, staging smoke test | Hurl | 1, 3, 4 |
| Real, disposable dependencies (database, queue, cache) | Testcontainers | 1 |
| Network and dependency failures | Toxiproxy | 1 |
| Third parties: fakes recorded from reality, triggered errors | WireMock (recording and playback) | 1 |
| The third party's real behavior | Learning tests (Hurl or the harness language) against the sandbox | 2 |
| Compatibility between own services | Pact (modes A, B or D) | 2 |
| Inputs nobody would write, from the OpenAPI | Schemathesis | 1, full cadence |
| UI, browser SDK, walking skeleton with a web consumer | Playwright | 3, 4 |
| Parameter combinatorics | PICT (pairwise) to generate the examples | design |
| Mutation at the acceptance level | `scripts/mutants.py` + semantic mutants | 1 |
| Oracle integrity and traceability | `scripts/seal.py`, `scripts/traceability.py` | all |
| Mutation at the unit level (dev) | Gremlins (Go) | 0 |
| Properties and invariants (dev) | rapid (Go), `go test -fuzz` | 0 |
| Load | k6 | dedicated |

Usage recipes in [../qa-test-automation/references/tools.md](../qa-test-automation/references/tools.md).

## Radar (November 2026)

Tools change fast: before adopting something from this radar, check its current state (version, maintenance, CLI changes).

### Adopt
- **Gherkin** as the artifact for human approval of business rules.
- **Hurl**: HTTP flows in text, language-independent, native JUnit.
- **Testcontainers** (Go and other languages): rung 1.
- **WireMock**: recorded and redacted third-party fakes.
- **rapid** and **`go test -fuzz`** in the dev's inner loop (Go).

### Trial
- **godog**: the Gherkin runner in Go; the agent writes the plumbing.
- **Toxiproxy**: network failures on rung 1.
- **Pact Go v2**: between own services, in mode A without a broker; D when there are permissions.
- **Schemathesis**: contract fuzzing in the full cadence.
- **Playwright**: walking skeleton with a browser SDK, and UI.
- **k6**: load, outside the functional suite.
- **Gremlins**: unit-level mutation in Go.

### Assess
- **Playwright agents** (planner, generator, healer): useful to create and maintain UI tests, with one rule: the healer only touches selectors, never assertions.
- **Karate**: an alternative to godog + Hurl if QA prefers a single DSL for API, mocks and performance; requires the JVM (Java 21 in version 2).
- **Ooze** (mutation in Go): an alternative to Gremlins.

### Hold (do not use in new suites)
- Go's `testing/quick`: frozen; use rapid.
- Unmaintained forks of go-mutesting.
- **Postman** and similar as the **source of truth** for tests: its format does not review well in a diff and ties the suite to a GUI. (Exporting a collection to Hurl or using it to explore is something else.)
- **Selenium** for new suites: Playwright covers the case with better determinism (auto-wait).

## When not to use a tool

- **Toxiproxy in shared staging**: you break other teams.
- **Hurl for complex setup logic**: if a scenario needs more than three seeding calls or conditional logic, the plumbing goes in the harness or in godog steps.
- **Pact against a third party**: it will not run your contract and its sandbox does not expose states. Use learning tests + WireMock; if it publishes an OpenAPI, bi-directional contract testing is a complement.
- **Hand-written mocks of a third party** with no learning test behind them: a mock that only knows what you believed is the cause of the PayPal token case.
