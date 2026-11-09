PASS only if ALL of the following hold:
1. Step 0: before proposing the final design, it surveys or asks for the missing current state (who writes the devices table, which queries the 7 consumers make, where the 900 ms p99 comes from, known incidents) instead of silently assuming it.
2. It treats the shared database as the central problem: it proposes how to separate data ownership (the new service owns its tables; the others access through an API or events) and how to migrate the data (backfill, CDC or outbox; it avoids dual-write without reconciliation).
3. It proposes a step-by-step path with named patterns (strangler fig or facade, shadow traffic or dual-run with comparison using the PHP code as the oracle, canary with flags, expand-contract on the schema), each step with a success signal and a rollback.
4. It marks which steps are one-way doors (deleting the old tables or code, cutting direct database access) and leaves them for the end.
5. It considers the "maximum 5 per customer" invariant while both systems coexist (who enforces it, the risk of violating it with concurrent writes).
6. It includes a decision table with measurable triggers and names the weak point.

FAIL if it proposes a rewrite with a big-bang cutover, ignores the shared database or has no rollback plan.
