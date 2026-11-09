---
name: qa-verify
description: "Runs a feature's verification by cadence (per slice, full or post-deploy) with the declared scripts, goes through deterministic gates (seal against the base branch, black box, fresh run, traceability, stability, contracts, mutants), classifies each failure (code, configuration, spec, test or environment), pushes it down the ladder and issues findings with evidence. It never certifies: it delivers evidence for a human to decide. Use it when the user asks to \"verify\", \"run the acceptance tests\", \"QA the feature\", \"is it ready?\", or when closing a ticket or before a PR."
license: MIT
---

# Verification

Respond in the user's language; keep common technical terms in English.

Runs, measures and reports. This skill does not write tests or code and does not decide whether something is ready: it produces the evidence a human decides with. Its value lies in being **hard to please**: the commands are pinned and sealed, the gates are scripts, every run uses new reports and a green that cannot be traced back to a criterion does not count.

**Analogy:** the referee with VAR. They do not play or choose which plays to review as it suits them: they apply the rulebook to what the cameras show, and someone else signs the result.

First read [../qa-core/references/role-model.md](../qa-core/references/role-model.md), [../qa-core/references/environment-ladder.md](../qa-core/references/environment-ladder.md) and [../qa-core/references/formats.md](../qa-core/references/formats.md) (sections 5 and 7).

## 0. Preconditions and rules

- Read `docs/agents/qa.md`. If it does not exist, ask to run the `qa-setup` skill and stop.
- Run the scripts from the repository root. `<qa-core>` is the folder of the `qa-core` skill, a sibling of this one; `<Acceptance>`, `<Reports>` and the base branch come from `docs/agents/qa.md`.
- Determine the **cadence**:
  - `per-slice`: the ticket's scenarios (its `Scenarios:` line), on the available rungs. It is a progress check, not a gate for the PR.
  - `full`: every scenario, rungs 1, 2 and 3 if it exists, plus contracts, fuzzing and mutants. It is the gate before the PR.
  - `post-deploy`: the scenarios with rung 4 in their column.
  If the user does not say: per-slice when closing a ticket, full before a PR.
- **Do not modify anything** under `<Acceptance>/`, `.scratch/<feature>/qa/` (except the report), `docs/agents/qa.md` or the production code. If something needs to change, it is a finding.
- **Run the rung scripts exactly as declared**: no filtering scenarios, no added flags, no changed timeouts. If a script does not work, that is an environment-class finding, not permission to improvise another.
- **Classification rule in solo mode**: if this session implemented code for the feature, it cannot classify a failure as `test` or `spec` on its own; a clean-context QA subagent or the human confirms that judgment. Whoever wrote the code tends to blame the test.

## 1. Gates

Go through every gate of the cadence and report them all; only a red G1 stops the others.

**G1 · Seal intact against the base branch** (every cadence):

```bash
python3 <qa-core>/scripts/seal.py verify --seal <Acceptance>/<feature>/.qa-seal.json --base <base branch> \
  --require .scratch/<feature>/qa/criteria.md .scratch/<feature>/qa/scenarios.md docs/agents/qa.md \
  <Acceptance>/<feature> <Acceptance>/bin
```

It breaks if any sealed file changed, if there are symbolic links, if a required path is missing, or if since the base the seal was deleted, recreated or resealed without citing `E-NN`/`F-NN`. **Always copy into the report the list of seals and reseals since the base**, even when the gate is green: reviewing them is the human's job in the PR. If G1 fails, stop: with the oracle altered, nothing else means anything.

**G2 · Black box** (every cadence): the check in `docs/agents/qa.md`. It fails if any test imports production code **or if the check itself could not run**.

**G3 · Fresh run** (every cadence): for each rung of the cadence marked available:

```bash
export QA_REPORTS=<Reports>/<feature>/<date>-<cadence>-r<N>; rm -rf "$QA_REPORTS"; mkdir -p "$QA_REPORTS"
START=$(date +%s); <rung N script> <feature>; echo "exit $?"
```

It fails if the script does not finish, ends red or leaves no JUnit in `$QA_REPORTS`. Never reuse reports from another run or another feature.

**G4 · Traceability** (every cadence):

```bash
python3 <qa-core>/scripts/traceability.py --criteria .scratch/<feature>/qa/criteria.md \
  --scenarios .scratch/<feature>/qa/scenarios.md --sources <Acceptance>/<feature> \
  --junit <the XML files in this verification's QA_REPORTS> --since <START of the first run> \
  --rungs <the cadence's available rungs> [--ids <the ticket's Scenarios:, in per-slice>]
```

It fails on any gap: a criterion without an executable scenario, a scenario not implemented, not executed, skipped, red or orphaned, a case with several IDs, a report older than the run or a **criterion with no evidence in scope** (its scenarios are only on unavailable rungs: that criterion stays unverified and is reported as such, never as green). An empty scope is an error.

**G5 · Stability** (full and post-deploy): run **the whole script again** for rung 1 (or rung 4 in post-deploy), with a new `QA_REPORTS`, and compare scenario by scenario. A scenario whose result changes between runs is **flaky** and counts as red: an intermittent green is not green. (Single scenarios are not rerun: that would require filtering.)

**G6 · Contracts and fakes** (full): rung 2. It fails if the Pact verification or a learning test is red, if a contract has no green verification in the last 30 days or since the provider's last change, or if a fake in `fakes/RECORDING.md` is more than 30 days old or predates the third party's last known change.

**G7 · Contract fuzzing** (full, if there is an OpenAPI): Schemathesis against rung 1. It fails with 5xx or responses outside the schema.

**G8 · Mutants** (full): the latest `qa-test-the-tests` report. Compare its fingerprint with the current one (`python3 <qa-core>/scripts/mutants.py fingerprint`): if HEAD or the changes differ, the report is about other code and the gate fails. It also fails if the report does not exist (mandatory in solo mode) or if there are survivors neither closed nor justified.

**G9 · Special-casing signals** (full; a warning, not a gate): search the production diff for references to the acceptance folder, to `SC-` IDs, to `QA_` variables or to literal values from the test data. Each match goes into the report for human review. It does not catch everything: it is an aid for code review, not a substitute.

A rung marked `not available` is not a run failure, but its scenarios go to "Not executed and why" and the criteria that depend only on it leave G4 red.

## 2. Classify each failure and push it down the ladder

Each red or flaky scenario becomes a finding with a **class**. The class decides who acts; misclassifying sends the fix to the wrong person (and "fixing the test" when the defect is in the code is exactly the cheat this plugin exists to prevent).

Full procedure in [references/classification-and-push-down.md](references/classification-and-push-down.md). In short:

| Class | Meaning | Goes to |
|---|---|---|
| **code** | The test reflects the criterion, the system does not meet it and it reproduces on rung 1 (also a flaky test that reproduces on rung 1: it is usually a race) | Dev, as input for `diagnosing-bugs` |
| **configuration** | Fails on 3 or 4 but not on 1: depends on configuration, deployment, secrets or network | Dev or platform |
| **spec** | The test reflects the spec, but the spec contradicts reality (a third party, a consumer) or is ambiguous | Human who owns the spec → `qa-acceptance-criteria` |
| **test** | The test does not reflect the approved criterion | QA: fixes it and reseals citing the finding |
| **environment** | Intermittent only in shared environments and stable on rung 1; environment down | Record and debt; never closed as "passed on retry" |
| **undetermined** | The procedure's questions are not enough to decide | Human |

**Push the test down** before handing over a finding: reproduce the failure on the lowest rung you can. From rung 1 downwards (integration and unit), the dev pushes it down, with `diagnosing-bugs`: QA does not see the code.

## 3. Write the report

Write `.scratch/<feature>/qa/verifications/<date>-<cadence>.md` in the format of section 7 of formats.md:

1. Header: mode, **actual** information barrier (the declared one), fingerprint (`mutants.py fingerprint`) and the report folders of this verification.
2. Gates table with the summarized output of each script.
3. **Seals and reseals since the base branch**, with their reason.
4. Status per criterion.
5. Findings (format of section 5), ordered by severity.
6. **Not executed and why**: unavailable rungs, scenarios blocked by testability, criteria with no evidence in scope, risks the sandbox does not reproduce, G9 signals.

Redact secrets in all the evidence (`<REDACTED>`).

## 4. Delivery

- Show the user the gates, the reseals since the base and the blocker and major findings. Nothing else at the top.
- **Never** write "approved", "ready", "certified" or "can go to production". If every gate is green, say exactly that: "every gate of the <cadence> cadence is green; still to decide: <what was not executed and the reseals to review>".
- Code or configuration findings: offer to pass them to `diagnosing-bugs`, with the reproduction command as the feedback loop.
- Spec findings: they go back to `qa-acceptance-criteria`.
- Test findings: the QA role fixes them and reseals with `--reason "F-NN: …"`.
