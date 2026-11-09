# Attack catalog

Attack families for the red team. Each attack is a concrete question the design must be able to answer. At the end, the catalog of hyperscale-grade mitigations.

Sources of the ideas: the "Behavior under stress" section of each block in `building-blocks`; the Amazon Builders' Library (static stability, shuffle sharding, constant work, timeouts and retries with jitter); Google's SRE book and workbook (SLOs, overload, cascading failures); "Metastable Failures in Distributed Systems" (Bronson et al., HotOS 2021); "The Tail at Scale" (Dean and Barroso, 2013).

## 1. Load

- **×10 sustained and ×100 at peak**: which resource saturates first (CPU, connection pool, IOPS, bandwidth, partitions)? Does the system reject the excess or queue it until it dies?
- **Sudden spike** (event, campaign, mass push): does autoscaling get there in time? How long does a new instance take to be ready and warm?
- **Hot key / hot partition / celebrity**: a single key, tenant or partition receives a disproportionate share. Does the design spread it or concentrate it?
- **Retry storm**: a dependency slows down and every layer retries. By how much does the load multiply if each of the N layers retries R times? Is there a retry budget?
- **Fan-out amplification**: one incoming request generates N internal calls. What happens to the p99 and to the load on the backends?
- **Cold start**: empty cache after a deploy, a failover or a flush. Can the origin hold 100 % of the traffic the cache normally absorbs?
- **Metastable failure**: a brief trigger (spike, failover, cold cache) pushes the system into a degraded state that **sustains itself** even after the trigger goes away (retries that keep the overload going, queues that never drain, timeouts that generate more work). What breaks the loop?
- **Queue that does not drain**: consumption is lower than production during the peak. How long does it take to drain? Do the messages expire first?

## 2. Dependencies

- **Total outage** of each synchronous dependency: what does the system return? Is there explicit degradation (stale data, reduced functionality) or an error?
- **Brownout**: the dependency does not go down, it becomes 10× slower. It is worse than an outage: health checks pass and pools are exhausted. Are the timeouts below the caller's latency budget?
- **Partial errors**: 5 % errors or malformed responses. Is it detected? Is what is not idempotent being retried?
- **Quota or rate limit exhausted** at a third party (payment gateway, partner, cloud API). What happens to in-flight requests?
- **Shared dependency** (a database, a cache cluster, a broker, an auth service): how many services go down if it goes down? Is it a disguised SPOF?
- **Expiration**: certificates, credentials, service tokens, domains. Is there an alert beforehand?

## 3. Data

- **Poison message**: a message that always fails. Does it block the partition (head-of-line)? Does it go to a DLQ? Does anyone look at it?
- **Duplicates**: delivery is at-least-once. Is every consumer idempotent? With which key?
- **Out of order**: events arrive out of order or after a rebalance. Is the final state correct?
- **Silent corruption**: a bug writes bad data for hours. How is it detected? Can it be rebuilt (event log, point-in-time backups)?
- **Half-done migration**: a schema change or a backfill is interrupted. Do old and new versions of the code coexist with both schemas?
- **Replica lag**: the replica is minutes behind. Which read breaks (read-your-writes)?
- **Split brain**: two nodes believe they are the leader. Is there a fencing token at the point where the effect happens?
- **Growth**: the dataset grows 10×. Which query stops fitting in memory? Which index becomes unmanageable?

## 4. Changes (deploys and configuration)

- **Bad deploy**: a buggy version reaches production. Canary? Automatic rollback by SLO? How long does it take to revert?
- **Wrong global configuration**: a config change or feature flag reaches every instance at once. It is the classic source of correlated failures. Is config rolled out progressively, like code?
- **Impossible rollback**: the deploy includes a destructive migration or publishes events in a new format. Is it a one-way door?
- **Incompatibility between versions**: during the rollout, version N and N+1 coexist. Do they understand each other in both directions (contracts, event schemas, caches)?
- **Debug flood**: a deploy raises the log level or the metrics cardinality. Does the observability pipeline go down or become expensive?

## 5. Infrastructure

- **Loss of a node, a zone, a region**: what is lost (unreplicated data, sessions, in-flight requests)? Do the remaining zones have the capacity to absorb the traffic without scaling at that moment (static stability)?
- **Network partition**: two parts of the system cannot see each other. Which invariant does the design prefer: consistency or availability (PACELC)?
- **Clock skew**: a node with its clock ahead or behind. What depends on time (leases, TTL, ordering, IDs)?
- **Exhausted resources**: disk full, file descriptors, maximum database connections, ephemeral ports.
- **Noisy neighbor**: another tenant or workload on the same machine, cluster or database consumes the resources.
- **The control plane goes down**: the orchestrator, service discovery or DNS do not respond. Does the data plane keep working with the last thing it knew?

## 6. Operations

- **Blindness**: the system fails and no alert fires, or the alert for a distant symptom fires. Are the alerts on user symptoms (SLOs) or on causes?
- **Alert without action**: the alert fires but there is no runbook, or the runbook assumes a person who is not there.
- **Slow manual recovery**: the failover or the restore requires human steps. How long does it really take? Has it been rehearsed?
- **Dependence on one person**: only one person knows how to operate the component.

## 7. Abuse and operational security

- **Malicious traffic or bots**: is there rate limiting per client, per IP, per tenant? Does it fail open or closed if the limiter goes down?
- **Enumeration and scraping** of resources by predictable ID.
- **Deliberately expensive requests**: deep pagination, unbounded searches, huge payloads.
- **Noisy tenant**: a legitimate but enormous customer degrades the others.

## Mitigation catalog (beyond the basics)

| Mitigation | What it attacks | Idea |
|---|---|---|
| Timeouts below the caller's budget, with deadline propagation | Brownout, cascade | Each call knows how much time the original request has left and does not work in vain |
| Retries with backoff, jitter and a **retry budget** | Retry storm | Retries are a bounded percentage of the traffic, not a multiplier |
| Circuit breaker and bulkheads | Slow dependency, shared dependency | Isolate pools per dependency; stop calling what is broken |
| **Load shedding** and admission control | Overload, metastable | Reject early and cheaply what cannot be served, prioritizing critical traffic |
| Explicit degradation (brownout mode) | Outage of non-critical dependencies | Turn off secondary features to save the main one |
| **Static stability** | Loss of a zone, control plane outage | Over-provision so the failure does not require reacting (scaling, reconfiguring) at the worst moment |
| **Cell-based architecture** and **shuffle sharding** | Blast radius, noisy tenant, bad deploy | Independent copies of the system; each customer on a different combination of cells so a failure affects few |
| **Constant work** | Load spikes in the control plane | Always do the same amount of work, whether there are changes or not, so behavior under stress is the same as in calm |
| Hedged requests | Tail latency with fan-out | Send a second copy if the first takes longer than the p95, cancelling the one that loses |
| Idempotency keys and fencing tokens | Duplicates, split brain | The effect is applied once even if the message arrives twice or there are two leaders |
| Backpressure | Queues that grow without bound | The slow consumer slows down the producer instead of accumulating |
| Progressive rollout of code **and** configuration, with automatic rollback by SLO | Bad deploy, global config | The failure affects a small fraction and reverts itself |
| Game days and chaos experiments | Unrehearsed recovery, blindness | Trigger the failure under controlled conditions to measure detection and recovery |
