# Measure before estimating (existing system)

In a system that is already running, the best estimate is a measurement. This guide says **what** to measure; the queries are templates to adapt to the real names of apps, events and attributes.

## What to ask for or look up

| Figure | Why it matters | Watch out for |
|---|---|---|
| Peak throughput per endpoint or operation (last 30-90 days) | Basis of every projection | The average hides the peak; use the maximum of a per-minute series |
| p50 / p95 / p99 per endpoint and per dependency | Little, fan-out, timeouts | The average lies with long tails; never use only `average` |
| Error rate by type (4xx, 5xx, timeouts) | Error budget, retries | Timeouts are often counted separately |
| Utilization: CPU, memory, connection pools, threads/goroutines | Distance to the knee of the curve | Measure at the peak, not on an average day |
| Data size and monthly growth | Storage, need for sharding | Indexes and replicas multiply the size |
| Queue/consumer lag | Backlog, draining | Measure per partition: the aggregate lag hides the hot partition |
| Event calendar (premieres, campaigns) | Real peak factor | Ask the business; it is not in the metrics |

## NRQL templates (New Relic)

Adapt `appName`, transaction names and attributes.

```sql
-- Peak throughput per minute over the last 30 days
SELECT rate(count(*), 1 minute) FROM Transaction
WHERE appName = '<app>' SINCE 30 days ago TIMESERIES 1 hour

-- Percentiles per endpoint
SELECT percentile(duration, 50, 95, 99) FROM Transaction
WHERE appName = '<app>' FACET name SINCE 7 days ago

-- Latency of an external dependency
SELECT percentile(duration, 50, 95, 99), count(*) FROM Span
WHERE appName = '<app>' AND span.kind = 'client' FACET peer.service SINCE 7 days ago

-- Error rate
SELECT percentage(count(*), WHERE error IS true) FROM Transaction
WHERE appName = '<app>' SINCE 7 days ago TIMESERIES
```

For logs (Sumo Logic or another), the pattern is the same: count per minute, keep the maximum, and split by endpoint or operation.

## If there are no metrics

1. Use the access or gateway logs to reconstruct the throughput.
2. If there are no logs either, a controlled load test in a production-like environment (with its runbook and stop criteria).
3. If none of the above is possible, project (projected mode) and mark the estimate as **not validated**, with the plan to measure it.

## Typical mistakes in existing systems

- Projecting with the average and discovering the peak in production.
- Measuring the service and forgetting the dependency: the bottleneck is usually in the database or a third party.
- Measuring in a test environment with small data: the queries that fit in memory there do not fit in production.
- Ignoring the traffic from retries and background jobs, which compete for the same resources.
