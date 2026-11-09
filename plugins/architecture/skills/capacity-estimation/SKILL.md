---
name: capacity-estimation
description: "Capacity estimation with numbers computed in code, not in prose. It starts from measured metrics when the system exists, or from order-of-magnitude scenarios and decision thresholds when there are no metrics (exploratory design, PoC), leaning on the business archetype. Covers QPS, storage, bandwidth, Little's law, utilization and queues, fan-out and tail latency, composed availability, shards, backlog and burn rate. Use it when a decision depends on scale (\"will it hold?\", \"how many instances?\", \"do we need to shard?\", \"capacity planning\", \"back-of-the-envelope\")."
license: MIT
---

# Capacity estimation

Respond in the user's language; keep common technical terms in English.

Turns "a lot of traffic" into numbers that **decide** the design. The numbers are computed with `scripts/capacity.py`, never in your head: the model is good at reasoning and bad at multiplying, and a confidently invented figure is the most expensive failure in this domain.

**Analogy:** it is the architect's structural calculator. The bridge drawing may be beautiful, but if nobody computed the load, it is an illustration, not a design.

## 1. Choose the mode according to the starting point

- **Measured** (existing system, the default when there are metrics): start from the real traffic and percentiles in the APM. Ask for or look up: peak throughput (not average), p50/p95/p99 per endpoint or dependency, CPU, memory and pool utilization, current data size and its growth. The starting queries are in [references/measurement.md](references/measurement.md).
- **Exploratory** (no system and no metrics: exploratory design, PoC, new product): **the lack of numbers does not block**. Take the shape of the load from the business archetype (`business-archetypes`) and:
  1. Define three **order-of-magnitude scenarios** (for example 10k, 1M and 100M daily active users, or 1k, 100k and 10M devices) with `scenarios`.
  2. For each decision that depends on scale, compute the **threshold** beyond which it stops working with `threshold` ("a primary of ~5k writes/s holds up to ~N daily active users with this pattern").
  3. Ask the business which scenario it expects to be in at 12-18 months; design for that one and check what breaks at the next.
  4. Mark each factor (actions per user, sizes, peaks) as an archetype assumption and say how it will be measured in the PoC or in production.
- **Projected** (a new feature on a system with business data, or calibrated with a similar published system): start from demand assumptions (active users, actions per user, read/write ratio, sizes, retention) and cite the source of the calibration.
- **Mixed** (the most common): one part measured (the current traffic) and another projected (the new feature or the growth).

Write each assumption with its source: "measured in NR, peak of the last 30 days", "archetype assumption (ticketing: ×100 at the sales opening)", "taken from case X", "assumption, no data". An assumption without a source is marked as such.

## 2. Compute only what can change a decision

Before each calculation, name the decision that depends on it ("if peak writes go beyond ~5k/s, a single primary is not enough"). If no possible result changes the decision, do not compute it.

| Question | Subcommand |
|---|---|
| How much demand will there be? | `demand` (projected), `measured` (growth over the real numbers) or `scenarios` (several orders of magnitude) |
| Up to what scale does this option work? | `threshold` |
| How many connections, goroutines or workers do I need? | `little` |
| At what utilization does latency start to explode? How many servers to keep the queue low? | `utilization` |
| What happens to latency if a request touches N backends? | `fanout` |
| What availability does this chain of dependencies give? | `availability` |
| Do we need to shard? How many nodes? | `shards` |
| How long does a backed-up queue take to drain? | `backlog` |
| How fast is the error budget exhausted? | `burn` |

```bash
python3 <this skill's directory>/scripts/capacity.py <subcommand> --help
python3 <this skill's directory>/scripts/capacity.py little --rps 1200 --latency-ms 180 --utilization 0.7
```

The output is JSON with inputs, result and formula. Show the user the invocation and the result; do not rewrite the numbers by hand.

## 3. Interpret with the right concepts

- **Peak, not average.** Size on the measured peak (or average × a declared factor). In event-driven systems (premieres, matches, campaigns), the factor can be 10× or more; ask about it.
- **Little's law** (`L = λ · W`): concurrency is throughput × latency. Use the latency of the percentile you do not want to queue (p99 for pools towards dependencies). If the dependency slows down, concurrency rises proportionally: that is how pools get exhausted.
- **Utilization and queues**: response time grows as `1/(1−ρ)`. At 50 % the response is 2× the service time; at 90 %, 10×. Above ~70-80 % small spikes produce long queues. The headroom is not waste: it is what absorbs the variance. (The formula is M/M/1, indicative.)
- **Fan-out and tail latency** ("The Tail at Scale", Dean and Barroso): with 100 backends, if each one answers above its p99 1 % of the time, 63 % of requests see at least one slow response. The backends' p99 becomes the aggregate's p50.
- **Composed availability**: in series it multiplies (each synchronous dependency subtracts). Parallel adds nines **only if the failures are independent**; the same zone, the same deploy or the same configuration correlate them.
- **Shards on the hottest key**: if the distribution is skewed, a calculation on the average lies.
- **Burn rate**: a burn of 14.4× exhausts the monthly budget in ~2 days; it is the typical threshold for an urgent page.

Reference orders of magnitude (latencies, throughput per node, nines) are in [references/numbers.md](references/numbers.md). They are starting points: if there is a measurement, the measurement wins.

## 4. Delivery

A table with: assumption or measurement (with its source), calculation (subcommand), result and **the decision it enables or rules out**. In exploratory mode, the scenarios table and the thresholds of each decision, plus the list of measurements that will replace the assumptions. Close with the number that has the most uncertainty and how to reduce it (a load test, a specific APM query, a benchmark).

If the estimation is done inside a design (`system-design`), the table goes into the numbers section of the design doc.
