<!-- Origin: proyecto26/system-design-skills (MIT), skills/resilience-failure, commit 228d57d. Curated for sv-skills: no vendor files or diagrams; corrections marked with [sv-skills]. -->

# Resilience & Failure

Design the system so that when a part breaks — and it will — the failure is
contained and the user still gets a useful (if degraded) answer instead of an
error page or a cascading outage. Getting this wrong is the difference between a
slow dependency and a total meltdown: the most common amplifier of an outage is
the system's own reaction to it (retry storms, health-check stampedes).

## When to reach for this
Any design with a remote dependency, a shared resource, or an SLA. Reach here to
find single points of failure, decide what each call does when its dependency is
slow or down, protect a service from being overwhelmed (rate limiting), and plan
how a recovered service comes back without being crushed by the backlog.

## When NOT to
Don't wrap a single in-process function or a best-effort batch job in circuit
breakers and bulkheads — that's machinery for cross-process/cross-network calls
(YAGNI). Don't add retries to a non-idempotent write without an idempotency key
first (→ `api-design`) — you'll duplicate side effects. The cheapest design that
meets the availability target wins; chasing an extra nine you don't need costs
real complexity (→ `back-of-the-envelope` for what a nine actually buys).

## Clarify first
- **Availability target** — how many nines, and is it per-request or per-feature? (→ `back-of-the-envelope`.)
- **Blast radius** — if this dependency dies, must the whole request fail, or can the feature degrade or hide?
- **Idempotency** — is the operation safe to retry? If not, what makes it safe (key, dedup)? (→ `api-design`.)
- **Latency budget** — how long may a call wait before a timeout is better than waiting? (→ `back-of-the-envelope`.)
- **Limit dimension & policy** — rate-limit per user / IP / API key / tenant? Hard (reject) or soft (queue/shape)? Burst tolerated?

## The options
Layered defenses; most real designs combine several.

- **Timeout** — bound every remote call. Use *everywhere*; an unbounded wait is
  the root of most cascades.
- **Retry with backoff + jitter** — re-attempt transient failures with growing,
  randomized delays. Use for idempotent calls against blips; never naked retries.
- **Circuit breaker** — stop calling a dependency that's failing; fail fast and
  probe to recover. Use when a downstream is down or slow and retries would pile on.
- **Bulkhead** — isolate resources (thread pools, connection pools, queues) per
  dependency. Use so one slow dependency can't exhaust capacity shared by others.
- **Graceful degradation** — fall back to a cached/stale value, partial result,
  default, or hidden feature. Use when a usable-but-worse answer beats an error.
- **Rate limiting / load shedding** — cap inbound work; reject or shape excess.
  Use to protect a service from overload, abuse, or a stampeding caller.
- **Redundancy / failover** — run N>1 of every component; promote a standby on
  failure. Use to remove SPOFs. (Health checks/LB failover live in `load-balancing`.)

Rate-limiting algorithms (token bucket, leaky bucket, fixed/sliding window) and
the circuit-breaker state machine are detailed in `references/deep-dive.md`.

## Trade-offs

| Option | What it solves | What it worsens | Change it when |
|---|---|---|---|
| Timeout | Bounds blocked threads; stops one slow call hanging the caller | Too tight → false failures; too loose → cascades | Tune to the dependency's p99, not a guess |
| Retry + backoff + jitter | Rides out transient blips | Multiplies load; duplicates non-idempotent writes | Add jitter + cap attempts + budget; require idempotency |
| Circuit breaker | Fails fast, gives a sick dependency room to recover | Adds state/tuning; can trip on a blip and over-shed | Flapping → tune thresholds / half-open probe rate |
| Bulkhead | Contains one failure to its own pool | Lower peak utilization; more pools to size | One noisy dependency starves others |
| Graceful degradation | Keeps the user served when a dependency dies | Serves stale/partial; more code paths to test | Correctness must be exact → fail closed instead |
| Rate limiting | Protects the service; bounds cost/abuse | Rejects legitimate bursts; needs shared state at scale | Limits too strict (valid drops) or too loose (overload) |
| Redundancy / failover | Removes SPOFs; survives node/region loss | Cost, replication lag, failover consistency risk | Failover drops un-replicated writes → `consistency-coordination` |

## Behavior under stress
This block exists to stop the system from amplifying its own outage.

- **Retry storm:** a dependency slows, every caller retries, retries pile on the
  retries of callers upstream, and load multiplies geometrically. *Mitigate:*
  exponential backoff with **jitter**, a per-request **retry budget** (cap total
  attempts), and a circuit breaker so a dead dependency isn't retried at all.
- **Thundering herd on recovery:** a service comes back and every queued client
  and expired cache entry hits it at once, knocking it over again. *Mitigate:*
  half-open circuit breakers that admit a trickle, jittered client reconnect,
  request coalescing, and slow-start ramp. (Cache-expiry stampede is `caching`.)
- **Health-check stampede / accidental DDoS:** aggressive health checks or
  load-balancer probes hammer a recovering instance. *Mitigate:* gentle probe
  intervals, fail-fast readiness, and draining. (Probe mechanics → `load-balancing`.)
- **Timeout-less cascade:** one slow dependency holds threads until the pool is
  exhausted, and the caller now looks "down" to *its* callers. *Mitigate:*
  timeouts + bulkheads everywhere.
- **Rate-limiter as SPOF:** a shared counter store (e.g. Redis) for limits goes
  down. *Mitigate:* fail-open (allow on limiter error) for availability, or
  fail-closed for protection — decide deliberately.

**Monitor:** error rate and p99 per dependency, retry counts, circuit-breaker
state transitions, pool saturation/queue depth, rate-limit rejection rate, and
"time to first success" after a recovery.

## How to apply
1. **Clarify the inputs** — pin the availability target, blast radius per
   dependency, idempotency, latency budget, and the rate-limit dimension/policy
   (the "Clarify first" list). No defense is chosen before these are answers.
2. **Pick the defenses** — walk the trade-off table per dependency, not globally.
   Every remote call gets a *timeout*; add retry+jitter only where idempotent; add
   a *circuit breaker* where a sick downstream would pile on; *bulkhead* shared
   pools; choose *degrade* vs *fail closed* by whether a stale answer is acceptable.
3. **Set the key knobs** — timeout = the dependency's measured p99; retry cap
   (often 2–3) plus a per-request budget and jitter; breaker open/half-open
   thresholds; bulkhead pool sizes; limiter rate/burst and fail-open-vs-closed.
4. **Stress-test the design** — replay each amplifier from "Behavior under stress"
   (retry storm, recovery herd, health-check stampede, timeout-less cascade,
   limiter-as-SPOF) and confirm a mitigation is in place for each.
5. **Size with numbers** — compute composed availability along the request path
   (series multiplies, parallel adds nines) and confirm the target is met without
   over-provisioning. (→ `back-of-the-envelope`.)
   if the user named a cloud (see "Choosing a provider").
7. **Show the trade-off in the answer** — give a `Decision | Solves | Worsens |
   Change it when…` table with one row per choice you made here (e.g. the
   option, its store, its failure policy); the last column is a concrete trigger
   (a number or observable signal). Then name what breaks first.

## Dos and don'ts
**Do**
- Bound every remote call with a timeout tuned to the dependency's p99.
- Add jitter and a retry budget so re-attempts can't multiply into a storm.
- Make a degraded response explicit (`stale: true`) instead of a silent lie.
- Decide fail-open vs fail-closed deliberately for limiters and breakers.
- Stress-test against the amplifiers before calling the design resilient.

**Don't**
- Retry a non-idempotent write without an idempotency key (→ `api-design`).
- Wrap in-process calls in breakers/bulkheads — that's cross-network machinery.
- Chase an extra nine the SLA doesn't require; redundancy cost is non-linear.
- Let a shared limiter or counter store become an unguarded single point of failure.
- Hammer a recovering instance with aggressive health checks or full reconnects.

## Numbers that matter
Tie timeouts to the dependency's measured **p99**, not a round guess. Cap retries
(often 2–3) and apply a budget so total attempts can't explode. Each extra
"nine" of availability costs disproportionately more redundancy — know what a
nine actually buys before targeting it. Composed availability matters: components
in series multiply (two 99.9% deps in a request path ≈ 99.8%), redundant
components in parallel add nines. For all of these — latency tables, the nines
table, series/parallel availability math — see `back-of-the-envelope`.

## Interface sketch
Two contracts are load-bearing here.

- **Degraded response:** make "I'm degraded" explicit, not a silent lie. Return
  the fallback plus a signal, e.g. `{ "data": [...], "stale": true, "source":
  "cache", "as_of": "2026-05-29T10:00Z" }` so callers and clients can react.
- **Rate-limit response:** reject with HTTP `429 Too Many Requests` and standard
  headers — `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `Retry-After`
  (seconds) so a well-behaved client backs off instead of retrying into the wall.

## Related building blocks
- `messaging-streaming` — *pairs with* this: a queue absorbs a write spike and a dead-letter queue contains poison messages; *owned-concept lives in* it for delivery guarantees and DLQ mechanics.
- `load-balancing` — *depends on* it for health checks and LB-level failover routing; pair its probes with the redundancy here to remove SPOFs.
- `consistency-coordination` — *owned-concept lives in* it: the consistency consequences of failover (un-replicated writes lost, quorum under partition) are decided there.
- `api-design` — *depends on* its idempotency-key contract before any retry of a write is safe.
- `caching` — *pairs with* graceful degradation as a fallback source; *owned-concept lives in* it for the cache-expiry stampede (vs. the recovery herd here).
- `system-design` — *feeds into* the orchestrator; this block is its step-5 failure-mode check.

## Deep dive: Resilience & failure deep-dive

Mechanics that don't belong in the lean SKILL.md. Read when designing the
resilience layer in detail.

## Timeouts (the foundation)

An unbounded wait is the seed of most cascades: a thread blocked on a slow
dependency is a thread that can't serve anyone else, and pool exhaustion turns
"one slow dependency" into "the whole service is down."

- Set the timeout from the dependency's **measured p99**, not a round number.
  Too tight manufactures failures out of normal tail latency; too loose lets a
  sick dependency hold resources.
- **Budget end-to-end, not per-hop.** If the user-facing SLA is 1 s and a request
  fans out A→B→C, the inner timeouts must sum to less than the outer one, or the
  outer caller times out while inner work keeps running (wasted, and still
  holding resources). Propagate a deadline down the call chain.
- Distinguish **connect** vs **read** timeouts; a connect timeout should be short.

## Retries: backoff, jitter, budgets

Naked immediate retries are the classic outage amplifier — they hit a struggling
dependency hardest exactly when it's weakest, and synchronized retries arrive in
lockstep waves.

- **Exponential backoff:** delay = `base * 2^attempt`, capped at a max. Spreads
  attempts out over time.
- **Jitter** is the part people skip and the part that matters. Without it, all
  clients that failed at the same instant retry at the same instant — a
  synchronized herd. Use *full jitter*: `sleep = random(0, base * 2^attempt)`.
  This decorrelates clients and flattens the retry spike.
- **Retry budget:** cap retries as a fraction of total requests (e.g. retries may
  be at most 10% of traffic). A per-call attempt cap (2–3) isn't enough on its
  own — under a broad outage, even "3 attempts each" across all callers is a 3–4×
  load multiplier. The budget bounds the *aggregate*.
- **Only retry idempotent operations**, or operations carrying an idempotency key
  so the server dedups duplicates. Retrying a non-idempotent write (charge card,
  send message) double-applies the side effect. The key contract is owned by
  `api-design`.
- **Retry only retryable errors:** timeouts, 503, connection resets. Never retry
  a 400/422 (the request is wrong; retrying just wastes capacity).

## Circuit breaker (state machine)

A breaker stops calling a dependency that's clearly failing, so callers fail fast
(freeing threads) and the dependency gets breathing room to recover.

States:
- **Closed** — calls flow normally; the breaker counts failures (rolling window
  or consecutive-failure threshold).
- **Open** — failure threshold tripped; calls are rejected *immediately* (fail
  fast) without touching the dependency, for a cool-down period. This is what
  prevents the retry pile-on against a dead dependency.
- **Half-open** — after the cool-down, admit a *small* number of trial calls. If
  they succeed, close; if they fail, re-open. Half-open is the herd guard: it
  lets a trickle through instead of the full backlog the instant the dependency
  looks alive.

Tuning: a too-sensitive breaker trips on a transient blip and over-sheds; a
too-lax one lets the cascade start before it opens. Track state transitions —
frequent flapping means the thresholds or half-open probe rate need tuning.
Combine with a fallback: when the breaker is open, serve the degraded response.

## Bulkheads

Named after a ship's watertight compartments: partition resources so a flood in
one section doesn't sink the vessel. Give each downstream dependency its **own**
thread pool / connection pool / concurrency limit. Then a dependency that goes
slow can only exhaust *its* pool — calls to healthy dependencies keep flowing.
The cost is lower peak utilization (you can't share the slack) and more pools to
size. Size each pool to that dependency's concurrency × latency, with headroom.

## Graceful degradation patterns

Pick the fallback per feature; the goal is a useful answer, not a perfect one:
- **Stale cache:** serve the last-known-good value (mark it stale — see the
  response contract in SKILL.md). Best when slightly old data is fine.
- **Default / static value:** a sensible constant (e.g. "trending" list when the
  personalized recommender is down).
- **Partial result:** return what succeeded, omit what failed, tell the client.
- **Hide the feature:** drop the non-essential widget rather than fail the page.
- **Fail closed (deliberately):** for money/auth/safety, an error is correct —
  never serve a degraded *wrong* answer where correctness is the point.

Degradation must be tested like any other path; untested fallbacks fail when
finally exercised, in the middle of the incident.

## Rate-limiting algorithms

The job: count work per key (user / IP / API key / tenant / global) and reject or
shape what exceeds the limit. Counters live in a fast shared store (e.g. Redis
`INCR`/`EXPIRE`), not a disk DB.

- **Token bucket** — a bucket of capacity `B` refills at `R` tokens/sec; each
  request spends one; empty ⇒ reject. **Allows bursts** up to `B` then settles to
  `R`. Memory-efficient, the common default (Amazon, Stripe). Two knobs (size,
  rate) can be fiddly to tune.
- **Leaky bucket** — a FIFO queue drained at a fixed rate; full ⇒ drop. Produces a
  **smooth, constant outflow** (good when a downstream needs steady input), but a
  burst fills the queue with old requests and delays fresh ones.
- **Fixed window counter** — one counter per clock window (per minute); simple and
  cheap, but a burst straddling the window boundary can admit up to **2×** the
  limit.
- **Sliding window log** — store a timestamp per request, count those inside the
  rolling window. **Exact**, but memory-heavy (stores rejected requests too).
- **Sliding window counter** — weight the previous window's count by the overlap
  fraction. Smooths the boundary spike of fixed-window at a fraction of the log's
  memory; an approximation (Cloudflare reports ~0.003% error). Good default for
  distributed limiting.

**Distributed rate limiting** has two hazards:
- **Race condition:** read-then-increment from concurrent requests under-counts.
  Fix with an atomic op — a Redis Lua script or sorted-set operation — not a
  read-modify-write with a lock (locks kill throughput).
- **Synchronization:** with multiple limiter nodes, a centralized store (Redis)
  beats sticky sessions, which don't rebalance. For multi-region, sync counters
  eventually-consistent and accept slight over-admission, or shard limits per
  region.

**Hard vs soft:** hard limiting never exceeds the threshold; soft tolerates brief
overage. **On reject:** return `429` with `Retry-After`; optionally enqueue the
work for later instead of dropping it (e.g. non-urgent jobs).

## SPOF analysis and failover

Walk every component and ask: *if this single box vanishes, does the system
stop?* Each "yes" is a SPOF to remove with redundancy.

- **Active-passive (failover):** one node serves; a standby takes over on
  heartbeat loss. Cold standby = slower recovery; hot standby = faster, costlier.
  Risk: writes not yet replicated to the standby are **lost** on promotion.
- **Active-active:** all nodes serve and share load; losing one sheds its share.
  Needs the routing layer (DNS/LB) or app to know all nodes, and conflict handling
  if both accept writes.
- **Multi-region:** survives a whole-datacenter loss; geo-route normally, redirect
  all traffic to a healthy region on outage. Cross-region replication is
  asynchronous, so failover trades some recent writes for availability.

The **consistency** consequences of any failover (what's lost, quorum behavior
under a partition, single-writer guarantees) are owned by
`consistency-coordination` — decide *consistency-first* (reject writes without
quorum) vs *availability-first* (accept locally, reconcile later) there.

## Common mistakes

- Retries with no jitter, no budget, no idempotency — the textbook amplifier.
- No timeout, or a timeout looser than the caller's own deadline.
- A circuit breaker with no fallback — you fail fast into an error instead of a
  degraded answer.
- One shared thread pool for all dependencies (no bulkhead) — one slow one takes
  everything.
- Treating the rate-limiter store as infallible — decide fail-open vs fail-closed.
- Untested degradation paths that only run during the incident they were meant to
  survive.
