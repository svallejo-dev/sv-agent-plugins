---
name: building-blocks
description: "Reference catalog of distributed-systems building blocks (API, storage, caching, consistency, messaging, scheduling, resilience, scaling, observability, logging, load balancing, DNS, CDN, IDs, counters, blobs, search, service decomposition, requirements) with options, trade-offs and behavior under stress. system-design and design-stress-test load it; also use it for a one-off question about one of those components."
license: MIT
---

# Building blocks

Respond in the user's language; keep common technical terms in English.

Catalog of distributed-systems components. Each block is a file in `references/` with the same structure: when to use it and when not, what to clarify first, options, a trade-offs table, **behavior under stress**, application steps, dos and don'ts, numbers, an interface sketch, related blocks and a deep-dive section.

**Analogy:** it is a workshop's parts store. The designer (`system-design`) decides what to build; here is how each part behaves, including how it breaks.

## How to use it

Read **only** the file of the block whose topic is active; do not load the whole catalog. For a one-off question ("which eviction policy for sessions?"), read the block and answer with its recipe and its trade-offs table. Inside a design, apply its trade-offs step with the contract `Decision | Resolves | Worsens | Change it when…`.

| When the conversation reaches… | File |
|---|---|
| Functional and non-functional requirements, scope, questions to ask | [requirements-scoping.md](references/requirements-scoping.md) |
| Endpoints, request/response, pagination, idempotency, versioning | [api-design.md](references/api-design.md) |
| Monolith vs services, boundaries, gateway/BFF, discovery, mesh, sync vs async | [service-decomposition.md](references/service-decomposition.md) |
| SQL vs NoSQL, data model, indexes, sharding, replication | [data-storage.md](references/data-storage.md) |
| What to cache, eviction, invalidation, stampede, hot keys | [caching.md](references/caching.md) |
| CAP/PACELC, consistency models, quorum, consensus, consistent hashing, sagas | [consistency-coordination.md](references/consistency-coordination.md) |
| Queues vs streams, delivery guarantees, ordering, DLQ, outbox, backpressure | [messaging-streaming.md](references/messaging-streaming.md) |
| Deferred jobs, distributed cron, leasing, priorities, fairness | [task-scheduling.md](references/task-scheduling.md) |
| Timeouts, retries, circuit breakers, bulkheads, degradation, rate limiting | [resilience-failure.md](references/resilience-failure.md) |
| How the system grows ×10/×100, diagnosing the bottleneck | [scaling-evolution.md](references/scaling-evolution.md) |
| Metrics, traces, SLOs, burn rate, alerts, health checks | [observability.md](references/observability.md) |
| High-volume log pipeline, sampling, retention | [distributed-logging.md](references/distributed-logging.md) |
| L4/L7, balancing algorithms, health checks, slow start, draining | [load-balancing.md](references/load-balancing.md) |
| DNS resolution, geo/latency/failover routing, TTL, anycast | [dns.md](references/dns.md) |
| CDN, edge cache, cache key, purge, origin shield | [content-delivery.md](references/content-delivery.md) |
| Unique IDs (UUID/ULID/Snowflake/ticket), clock, ordering | [sequencer.md](references/sequencer.md) |
| Write-heavy counters, HyperLogLog | [sharded-counters.md](references/sharded-counters.md) |
| Large objects, multipart, signed URLs, tiering, erasure coding | [blob-store.md](references/blob-store.md) |
| Full-text search, inverted index, ranking, autocomplete | [distributed-search.md](references/distributed-search.md) |

## Notes on this version

- **Origin**: curated from [proyecto26/system-design-skills](https://github.com/proyecto26/system-design-skills) (MIT, commit `228d57d`).
- **Corrections**: the factual errors found are corrected and marked with `[sv-skills]` (DynamoDB is not leaderless, the HyperLogLog error, UUIDv7 in range-partitioned stores, virtual nodes and hot keys, quorum and linearizability, the cache invalidation race, burn rate, among others).
- **No vendor files**: they were removed because they age fast and several were already wrong. When a step says "read the provider file" or "see *Choosing a provider*", check the specific managed service (limits, quotas, names, prices) with `research` against the current official documentation.
- **Cross-references**: a block in backticks (`caching`) is the file `references/caching.md`. Mentions of `back-of-the-envelope` resolve to `capacity-estimation`, of `system-design` to `system-design` and of `architecture-diagram` to a Mermaid diagram in the design doc.
- **Numbers**: the "Numbers that matter" are starting orders of magnitude. In an existing system, the measured metrics win.
- **Anycast and geo-routing**: `load-balancing` and `content-delivery` refer to each other; the useful detail is in `dns.md`.
- **What this catalog does not cover in depth** (`design-stress-test` and `system-design` provide it): metastable failures, static stability, cell-based architecture and shuffle sharding, hedged requests, deadline propagation, migrations of existing systems.
