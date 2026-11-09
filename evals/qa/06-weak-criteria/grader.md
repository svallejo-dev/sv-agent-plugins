PASS only if ALL of the following hold:

1. It rewrites the four criteria so they are observable from the outside, a single behavior each, with concrete data and a named oracle:
   - number 2 stops talking about the table (order status queried through the API);
   - number 3 becomes a usage oracle (the billing consumer deserializes the event with its schema and processes it), not "it is published";
   - number 4 is split per event type and state transition.
2. It makes explicit, with `Source: inferred` and asking for confirmation, at least: **idempotency** (a duplicate webhook does not produce two events or two transitions), **ordering** (refunded before captured), **signature verification** (an unsigned or badly signed webhook is rejected) and **invalid transitions**.
3. It runs the criteria premortem (mandatory in solo mode) with parallel subagents and shows how each story changes or adds a criterion.
4. It uses the parseable `## AC-NN:` format with Behavior, Oracle, Source, Type and Priority, in `Status: draft`, and asks for human approval.

FAIL if it keeps implementation criteria ("it is saved in the table", "it is published to Kafka") as the only criteria, if it omits the webhook's idempotency or if it approves itself.
