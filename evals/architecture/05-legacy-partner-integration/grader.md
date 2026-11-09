PASS only if ALL of the following hold:
1. It identifies the relationship with the partner as an upstream that will not adapt to us and explicitly chooses between Anticorruption Layer and Conformist, with a justification (the expected recommendation is an ACL that translates the partner's IDs, states and events into the own model).
2. It proposes a stable own model (subscription states, IDs) independent of both versions of the partner, so that the legacy system and the new API coexist per country behind the same ACL.
3. It handles the unreliable callback: idempotency, periodic reconciliation with the partner and divergence detection.
4. It defines the transition path per country (flags or per-country routing, coexistence, cutover criterion) and marks the one-way doors.
5. It classifies the domain (partner integration management as supporting or authentication as generic, not as core) and derives from it how much to invest.
6. It delivers the context map with the pattern of each relationship.

FAIL if it couples the internal model to the partner's states or IDs, or if it proposes keeping two independent integrations without a common layer.
