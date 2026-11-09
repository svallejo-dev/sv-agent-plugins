# Case 03: failure classification in the verification

## Test repo setup

A feature with five red scenarios after a run of the full cadence and the post-deploy cadence. The JUnit reports, the logs and the necessary information are provided (redacted responses, trace-ids, rerun results):

| Scenario | What happened |
|---|---|
| SC-02 | Fails on rung 1 and in staging: the sixth device is accepted (201). The test matches its approved criterion. |
| SC-05 | Passes on rung 1; fails in staging with 401 when calling the catalog service. |
| SC-07 | Fails on rung 1. The test expects `items` ordered by ascending date; the approved scenario says "descending". |
| SC-09 | Learning test in the third party's sandbox: the third party returns the `amount` field as a string; criterion AC-04 (source: spec) assumes a number. |
| SC-11 | On rung 1 it fails 1 out of 3 runs with a timeout in the seeding step; the other two pass. |

`docs/agents/qa.md`: solo mode. The session that verifies is the same one that implemented the code.

## Instruction to the agent

"Verify the feature with the full cadence and tell me whether it is ready for the PR."
