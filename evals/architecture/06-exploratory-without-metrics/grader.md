PASS only if ALL of the following hold:
1. It does not get blocked by the lack of metrics or demand numbers before moving on: it treats the case as an exploratory design and says so.
2. It identifies the archetypes (ticketing with flash sales + payments) and from them the forces: extreme peaks when sales open, contention over seats, bots, and payment correctness.
3. It designs the invariants first: no overselling (allocation with strong consistency), holds with expiration, payment and ticket tied together, idempotency in the charge.
4. It works the scale as order-of-magnitude scenarios and computed decision thresholds (for example, how many simultaneous buyers direct allocation on the database supports before a waiting room is needed), not as invented figures presented as facts.
5. It asks the questions that change the design (numbered seats vs general admission, hold duration, tolerance for a waiting queue, anti-bot policy, payment processor and PCI scope).
6. It proposes a PoC plan: hypotheses ordered by risk (no overselling under concurrency, integration with the processor), minimal scope, what to instrument and success and abandonment criteria.
7. It recommends a simple architecture for the likely scenario (modular monolith, relational database) with measurable triggers to evolve.

FAIL if it refuses to design without data, if it invents metrics and presents them as real, or if it proposes a hyperscale architecture without justifying it with a scenario.
