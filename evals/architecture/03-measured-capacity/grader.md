PASS only if ALL of the following hold:
1. It applies Little's law: today, at p50, 800 × 0.12 ≈ 96 concurrent connections and at p99 up to 800 × 1.4 = 1,120; in the campaign, 2,400 × 0.12 ≈ 288 and 2,400 × 1.4 = 3,360. It compares them with the total capacity of 400 connections (4 × 100).
2. It concludes that with tail latencies (or with a gateway brownout) the pool is exhausted, and that the p50 is not enough to size it.
3. It computes with the skill's script (or shows the calculations in a verifiable way), not with figures asserted without calculation.
4. It proposes concrete changes: a timeout below the budget, a dedicated bulkhead, a circuit breaker, a concurrency limit or load shedding, decoupling with a queue if the flow allows it, and checking the gateway's rate limits with the provider.
5. It points out the main uncertainty (for example, the gateway's behavior at 3× or its rate limit) and how to reduce it (a load test with the gateway in sandbox, an agreement with the provider).

FAIL if it answers "yes, it holds" using only the p50 or the average throughput.
