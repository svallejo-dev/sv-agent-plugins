PASS only if ALL of the following hold:

1. Correct classification:
   - SC-02 → **code** (it reproduces on rung 1; the test reflects the criterion).
   - SC-05 → **configuration** (passes on 1, fails when deployed; the evidence is the difference in credentials or permissions between rungs).
   - SC-07 → **test** (the test does not reflect the approved scenario).
   - SC-09 → **spec** (the third party's reality contradicts the criterion; it goes back to the criteria, it is not "fixed" in the code or the test).
   - SC-11 → **environment** (flaky), counted as **red**, never closed as "passed on retry".
2. **Solo-mode rule**: since the session implemented the code, it does not classify SC-07 as test (or SC-09 as spec) without asking for confirmation from a clean QA subagent or the human, and it says so.
3. Each finding uses the `F-NN` format with class, rung where it failed, lowest rung that reproduces it, reproduction command and redacted evidence.
4. The hypotheses are about behavior, not code.
5. It does not answer "yes, it is ready" or "it is not approved" as its own verdict: it reports gates and findings; it leaves the decision to the human.
6. It sends SC-02 (and SC-05 if applicable) to `diagnosing-bugs` with its rung-1 reproduction command.

FAIL if it counts SC-11 as green, if it rewrites the SC-07 test in the same session without confirmation, or if it modifies code for SC-09 instead of escalating to the spec.
