# Reference numbers

Orders of magnitude for estimating without looking things up. Remember the magnitude, not the decimals: what changes an architecture is the ratio between components. In an existing system, these numbers only help to spot a suspicious measurement; the measurement wins.

Basis: the cheat sheet of [proyecto26/system-design-skills](https://github.com/proyecto26/system-design-skills) (MIT), with the throughput figures corrected.

## Time and volume

- One day ≈ 86,400 s ≈ 10⁵ s. One month ≈ 2.6 × 10⁶ s.
- 1 req/s sustained ≈ 86,000 per day ≈ 2.6 M per month.
- 2¹⁰ ≈ thousand (KB), 2²⁰ ≈ million (MB), 2³⁰ ≈ billion (GB), 2⁴⁰ (TB), 2⁵⁰ (PB). Memory is base 2; storage and network are sold in base 10.

## Latencies (order of magnitude)

| Operation | ≈ Time |
|---|---:|
| L1 cache reference | ~1 ns |
| Main memory reference | ~100 ns |
| Compress 1 KB | ~1-3 µs |
| Read 1 MB sequentially from memory | ~3-10 µs |
| Random read on SSD | ~16-100 µs |
| Read 1 MB sequentially from SSD | ~50-200 µs |
| Round trip within the same datacenter | ~0.5 ms |
| Round trip between zones of a region | ~1-2 ms |
| Spinning disk seek | ~2-10 ms |
| Round trip between continents | ~70-150 ms |

Consequences: memory is ~100× faster than the internal network; calls between regions cost on the order of 100 ms, so chatty traffic stays within a region.

## Throughput per node (starting points, not promises)

| Component | ≈ Operations/s per node | Notes |
|---|---:|---|
| RDBMS (Postgres/MySQL) on indexed point reads | ~10k (modern hardware, data in memory) | ~1k is a conservative floor; scans, joins and writes with many indexes can be 10× lower. Validate with a benchmark or a measurement. |
| RDBMS on transactional writes | ~1k-10k | Depends on fsync, indexes, contention on hot rows. |
| Distributed key-value per partition | ~1k-10k | Managed services publish per-partition limits: check them with `research`. |
| In-memory cache (Redis/Memcached) | ~100k-1M | Command execution per shard on a single thread in Redis. |
| Streaming broker per partition | ~1-10 MB/s | Measure in bytes, not in messages. |
| HTTP service with simple logic, per core | ~1k-10k | Highly dependent on the language and the serialization. |

## Availability

| Availability | Downtime per year | Downtime per month (30 days) |
|---:|---|---|
| 99 % | ~3.65 days | ~7.2 h |
| 99.9 % | ~8.76 h | ~43 min |
| 99.95 % | ~4.4 h | ~22 min |
| 99.99 % | ~53 min | ~4.3 min |
| 99.999 % | ~5.3 min | ~26 s |

Each additional nine costs non-linearly (redundancy, automatic failover, multi-region). Tie the target to the requirement, not to ambition.

## Peak factors

- Daily consumer traffic: peak ≈ 2-3× the average.
- Events (launches, live matches, campaigns, paydays in payments): 10× or more, sometimes within minutes. Ask about the event calendar.
- Retries during an incident: they can multiply the load by (1 + retries) at each layer that retries.
