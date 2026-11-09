---
name: qa-test-automation
description: "Implements the approved scenarios as executable tests, with existing tools (Gherkin with godog, Hurl, Testcontainers, Toxiproxy, WireMock, Pact, Schemathesis, Playwright) and AI-generated plumbing; third-party learning tests first, then the scenarios, and it checks that each test fails for the right reason and is deterministic before sealing. Use it when the user asks to \"automate the tests\", \"implement the scenarios\", for \"acceptance tests\", \"e2e tests\", \"learning tests\" or after qa-test-design."
license: MIT
---

# Test automation

Respond in the user's language; keep common technical terms in English.

Turns approved scenarios into tests a machine runs the same way a thousand times. The AI generates the plumbing (godog steps, Testcontainers harness, fakes) and the human does not read it line by line; that is why this skill demands **deterministic checks on the tests themselves** before sealing them: that they fail for the right reason, that they are not flaky and that they do not import production code.

**Analogy:** building an engine test bench. It does not matter what language the bench was bolted together in; what matters is that it measures what it claims to measure, gives the same reading twice in a row and is not wired to the engine by a cable that makes it read whatever the engine wants.

First read [../qa-core/references/role-model.md](../qa-core/references/role-model.md), [../qa-core/references/environment-ladder.md](../qa-core/references/environment-ladder.md) and [../qa-core/references/formats.md](../qa-core/references/formats.md) (section 4, ID convention).

## 0. Preconditions

1. `docs/agents/qa.md` exists; if not, ask to run the `qa-setup` skill and stop. Run the scripts from the repository root. `<qa-core>` is the folder of the `qa-core` skill, a sibling of this one; `<Acceptance>` and `<Reports>` come from `docs/agents/qa.md`.
2. `scenarios.md` has `Status: approved`.
3. The design seal is intact:
   ```bash
   python3 <qa-core>/scripts/seal.py verify --seal <Acceptance>/<feature>/.qa-seal.json \
     --require .scratch/<feature>/qa/criteria.md .scratch/<feature>/qa/scenarios.md docs/agents/qa.md
   ```
   If it is broken, stop: someone changed the design or the configuration after they were approved.
4. **Contamination rule**: the QA role writes the acceptance tests. If this session implemented code for the feature, delegate the automation to a subagent with a clean context; its brief includes the scenarios, the handoff, the API contracts, this skill and the prohibition on reading production code. (It is good faith; see role-model.)
5. Plumbing language: the repo's, unless `docs/agents/qa.md` says otherwise. If `<language>-testing` exists (for example `go-testing`), invoke it for its idioms. The human not mastering that language is not a problem: they will not read the plumbing, they will read Gherkin and Hurl.

## 1. The rung scripts and the harness

If `docs/agents/qa.md` says `to be built` for an available rung, create its script in `<Acceptance>/bin/` following the **rung script contract** of `qa-setup` (JUnit only in `$QA_REPORTS`, nothing written inside `<Acceptance>/`, no filtering arguments, image tagged `$QA_IMAGE_TAG`). Harness requirements:

- **Parameterized by environment**: `base_url` and dependencies via variables; no environment value written into the tests.
- **Rung 1**: brings up the **service image** (not the source code) with its dependencies in Testcontainers, each dependency behind Toxiproxy, and third parties as WireMock fakes.
- **Verifiable black box**: in Go, the acceptance tests are their own module (`<Acceptance>/go.mod`), so the compiler prevents importing production `internal/` packages.

Recipes in [references/tools.md](references/tools.md); structure and data rules in [references/harness.md](references/harness.md).

## 2. Learning tests first (if there are third parties)

Before writing a single scenario that depends on a third party:

1. For each assumption about the third party the scenarios use (which variant it returns, in which shape, which errors), write a learning test against its **sandbox**, in `learning/`.
2. Run them. **If a learning test contradicts a scenario or a criterion, stop**: it is a **spec**-class finding, not an implementation detail. Record it and go back to `qa-acceptance-criteria`. That is how the PayPal token case would have been caught before writing the BFF.
3. Record their responses as fakes with **WireMock's recording mode**, **redacting secrets**, and add by hand the variants the sandbox does not let you trigger (5xx, 429, timeouts). The rung-1 fakes are born from reality, not from belief.
4. Record the recording date of each fake in `fakes/RECORDING.md`: an old fake is suspicious, and `qa-verify` reports it in the full cadence.

Pact is for own services, not third parties: see [references/pact-modes.md](references/pact-modes.md).

## 3. Implement the scenarios

Choose the tool per scenario with the `qa-toolbox` guide. Non-negotiable rules:

1. **One ID per test, in the title or in the file name** (formats.md convention). A test without an ID does not exist for traceability; a test with two IDs is a gap.
2. **Black box**: the tests talk to the system only through its public surface (HTTP, events, UI) and through the testability seams declared in the handoff. No imports of production packages.
3. **Own, random, unmarked data**: each scenario creates its data through the API or the seeding seam, with values generated on every run and **without recognizable prefixes or patterns** (no `qa-`, `test-`, fixed IDs). Recognizable data lets production code detect it and answer what the test expects (special-casing).
4. **No fixed waits**: no `sleep`. Poll with a timeout (Hurl's `retry` option, `Eventually` in Go, `expect.poll` in Playwright).
5. **The scenario's oracle, complete**: if the scenario says "409 and the customer still has 5 devices", the test checks both.
6. **No skipping**: no `skip`, `@ignore`, `.only` or tag that excludes scenarios. A blocked scenario is blocked in `scenarios.md`, not skipped in the code.
7. **QA controls the real consumer**: in the walking skeleton, the page or minimal client that uses the SDK is written by QA inside `<Acceptance>/<feature>/` and served by the harness. If the service under test served it, the dev would control the oracle.

## 4. Test the tests before sealing them

Run the rung scripts with a new reports directory for each run:

```bash
export QA_REPORTS=<Reports>/<feature>/$(date +%Y%m%dT%H%M%S); mkdir -p "$QA_REPORTS"; START=$(date +%s)
<Acceptance>/bin/rung-1.sh <feature>
```

Three deterministic checks. None is optional.

**a) Red for the right reason** (usually the feature is not implemented yet):

```bash
python3 <qa-core>/scripts/traceability.py --criteria .scratch/<feature>/qa/criteria.md \
  --scenarios .scratch/<feature>/qa/scenarios.md --sources <Acceptance>/<feature> \
  --junit "$QA_REPORTS"/*.xml --since "$START" --rungs 1 --expect-red
```

The script requires every scenario to be implemented and executed; red is expected and it warns about every **green before implementing**. Then review the cause of each red:

| Result | Meaning | Action |
|---|---|---|
| Red from a behavior assertion (404, 501, a different expected value) | Correct: the test detects the absence of the behavior | None |
| Red from a harness error (connection refused, broken fixture, compilation, setup timeout) | The test does not test anything yet | Fix the harness and repeat |
| **Green before implementing** | Either the behavior already existed, or **the test is vacuous** (an assertion that cannot fail) | Investigate. If it already existed, document it in the scenario; if it is vacuous, rewrite it |

**b) Determinism.** Run the suite three times in a row on the same state, each time with a new `QA_REPORTS`. Any scenario whose result changes between runs is flaky and **is not sealed**: fix the cause (shared data, ordering, waits, clock).

**c) Black box.** Run the check declared in `docs/agents/qa.md` and verify its exit code.

## 5. Human review and seal

1. The human reviews the **readable** artifacts: the `.feature` and `.hurl` files, comparing them with the scenarios. They do not review the plumbing; their guarantee is the checks of step 4.
2. With approval, extend the seal to the tests and the rung scripts:
   ```bash
   python3 <qa-core>/scripts/seal.py reseal --seal <Acceptance>/<feature>/.qa-seal.json \
     --reason "acceptance tests implemented and reviewed" <Acceptance>/<feature> <Acceptance>/bin
   ```
3. Tell the dev that the acceptance tests are **read-only** for them: they run them per slice and, if they believe one is wrong, they escalate (`escalations.md`), never edit.

Next step: the dev implements with `tdd`; verification is done with `qa-verify`.
