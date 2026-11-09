# Classifying a failure and pushing it down the ladder

A failing test gives you a **symptom**, not a diagnosis. "The limit scenario returned 201" does not say what to change. This procedure turns the symptom into something actionable: **who** must act (the class) and **where** the defect is (the lowest rung where it reproduces).

**Analogy:** an emergency doctor. First they classify (triage) to send the patient to the right specialist; then they order increasingly specific tests (X-ray, then CT scan) until they locate the injury. They do not operate on the symptom.

## Classification tree

Apply the questions in order; the first one answered "yes" decides.

1. **Does the test faithfully reflect the approved scenario and criterion?**
   Compare the test with its row in `scenarios.md` and its criterion. If the test checks something else (different data, a different assertion, a different oracle) → **test**.
   In solo mode, if this session wrote the code, a clean QA subagent or the human gives this answer.

2. **Does it reproduce deterministically?**
   If the scenario alternated results between the G5 runs, it is intermittent. Then:
   - If it is intermittent **on rung 1** (controlled environment), the cause is almost never "the environment": it is usually a **race in the code** or a **non-deterministic harness**. Candidate for **code** (with its pattern as evidence, for `diagnosing-bugs`) or for **test** if the non-determinism is in the harness (shared data, waits, ordering). Continue with questions 3 and 4.
   - If it is stable on rung 1 and intermittent only in shared environments (3 or 4) → **environment**. Record it with its pattern (how many times it failed, at which step) and it stays as debt.
   Either way, an intermittent scenario counts as red, and in a critical scenario its severity is at least major.

3. **Does it reproduce on rung 1?**
   Run the scenario on the hermetic rung.
   - Yes → candidate for **code**; continue with question 4.
   - No (fails on 3 or 4, passes on 1) → **configuration**: the defect lives in what only exists when deployed (variables, secrets, permissions, network, the neighbor's version, migrations). The evidence is the **difference** between rungs: what the environment has that rung 1 does not.

4. **Is the behavior the test demands the right one according to reality?**
   Look for external evidence: the third party's official documentation, a learning test, the real consumer, the business owner's answer.
   - If reality contradicts the spec (the third party does not behave that way, the consumer needs something else) or the spec is ambiguous on this point → **spec**.
   - If not → **code**.

If after the four questions you cannot decide, the class is **undetermined** and the human resolves the finding. Do not force it.

## Pushing the test down

Each step down shrinks the area where the defect can be. The goal is to hand over the finding with **the lowest and fastest reproduction command possible**.

```
rung 4 (staging)          "fails in staging"                   → zone: the whole deployed system
   ↓ reproduce on 1
rung 1 (hermetic)         "fails with the PR image"            → zone: the service and its controlled dependencies
   ↓ the dev reproduces it as an integration test
integration (inner loop)  "the repository fails with Postgres" → zone: one module and its adapter
   ↓ the dev reproduces it as a unit test
unit                      "the limit rule fails"               → zone: one function
```

- **QA pushes it down to rung 1.** Below that you need to see the code; that is the dev's job, with `diagnosing-bugs`, which receives the rung-1 reproduction command as its feedback loop (its Phase 1).
- If a failure does not go below rung 3 or 4, that is already information: the defect is not in the logic, it is in integration or configuration.
- When the finding is closed, the low-level test the dev wrote stays as a **regression** test in their suite; the acceptance scenario remains the business oracle.

## Severity

| Severity | Criterion |
|---|---|
| **blocker** | Violates a critical-priority criterion, an invariant (double charge, data leak, token handed to the wrong customer) or breaks the walking skeleton |
| **major** | Violates a high-priority criterion, or is a flaky test in a critical scenario |
| **minor** | Violates a medium-priority criterion with no risk to data or money |

## What is never done

- Closing a finding because "it passed on retry".
- Classifying as `test` to unblock the cadence without the required confirmation.
- Lowering the severity because the fix is expensive.
- Writing a hypothesis about the **code**: QA did not see it. Hypotheses are about **behavior** ("it looks like the cache does not distinguish between customers", not "the map on line 40 uses a global key").
