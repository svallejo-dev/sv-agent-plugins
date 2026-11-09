# Internal event platform (bus, integration)

**Analogy:** the internal mail service of a large company. It does not produce the letters, it delivers them: its value is that they arrive, in order when it matters, that they can be resent and that everyone understands the envelope format.

## Dominant forces

- **Contracts between teams**: events are an internal public API; changing their format breaks others.
- **Delivery and ordering guarantees**: at least once, order per key, replay.
- **Many producers and consumers** at different paces; the slow consumer cannot hold back everyone.
- **Operations as a product**: teams need self-service (create topics, subscribe, see their lag).

## Shape of the load (without metrics)

- Key formula: **storage ≈ events/s × average size × retention × replicas**.
- The load follows that of the systems that feed it (business peaks), plus replays and backfills.
- Scenarios to explore: 100, 10,000 and 1M events per second, with retentions of 1, 7 and 30 days.

## Invariants and consistency

- No accepted event is lost (durability before acknowledging the producer).
- Order guaranteed only within a partition key; never globally.
- Consumers are idempotent: duplicates are part of the contract.
- Backward schema compatibility (and forward when needed).

## Typical subdomains

- **Core** (for the platform): reliable delivery, subscription and contract management, self-service.
- **Supporting**: schema registry, flow observability (lag per consumer), DLQs and replay.
- **Generic**: the broker itself (Kafka, a managed service), authentication.

## Path already walked (check before citing)

- Kafka, born at LinkedIn, as a partitioned distributed log.
- A schema registry with compatibility rules.
- Transactional outbox or CDC to publish from the services without dual-write.
- CloudEvents (CNCF) as a common event envelope format.
- Published Language: business events, not table dumps.

## Typical failure modes (seed for the red team)

- A poison message blocking a partition (head-of-line).
- A slow consumer whose lag grows beyond the retention: it loses events.
- An incompatible schema change that breaks consumers in production.
- A hot partition from a badly chosen partition key.
- Continuous rebalances of the consumer group that stop consumption.
- A massive replay that saturates the consumers or their databases.

## Questions that change the design

- Which guarantees does each flow need (ordering, delivery, latency)? Are they the same for all?
- Who owns each event and its schema?
- Which retention and which replay capacity are needed?
- How much self-service is given to the teams, and with what governance?

## Hypotheses for a PoC

- Validate delivery with triggered failures: consumer down, poison message, rebalance, broker restarted.
- Validate the evolution of a schema with producers and consumers on different versions.
- Instrument: lag per consumer and partition, events in the DLQ, end-to-end time, retry rate.
