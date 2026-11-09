<!-- Origen: proyecto26/system-design-skills (MIT), skills/caching, commit 228d57d. Curado para sv-skills: sin archivos de proveedor ni diagramas; correcciones marcadas con [sv-skills]. -->

# Caching

Put a copy of hot data closer to the reader so most requests skip the slow path.
Caching is the highest-leverage move for read-heavy systems — and the easiest to
get subtly wrong, because a cache adds a second source of truth that can serve
stale or wrong data, and can *amplify* an outage when it misbehaves.

## When to reach for this
Reads dominate (a high read:write ratio from `back-of-the-envelope`); the same
data is read repeatedly; the datastore is the read bottleneck; or recomputation
is expensive. A cache buys read latency and offloads the origin.

## When NOT to
Write-heavy or read-once data (low hit rate — pure overhead). Data that must be
exactly current with zero staleness (a cache is a stale copy by nature; when
strict freshness is required, go to the source or use `consistency-coordination`). Don't
add a cache before a number shows reads are the problem (YAGNI) — it's a new
failure mode and a second thing to operate.

## Clarify first
- **Read:write ratio and hit rate** — is the working set cacheable? (→ `back-of-the-envelope`, 80/20.)
- **Staleness tolerance** — seconds? minutes? must reads see their own writes?
- **Working-set size** — does the hot set fit in RAM across cache nodes?
- **Consistency on write** — can the cache briefly disagree with the store?
- **Eviction trigger** — what's the access pattern (recency? frequency? time-bound?).

## The options

**Where to cache** (often layered): client/browser → CDN edge (→ `content-delivery`)
→ application/in-process → distributed cache (Redis/Memcached) → database buffer
pool. This skill focuses on the application and distributed layers.

**Read strategy**
- **Cache-aside (lazy):** app checks cache, on miss reads the store and populates.
  Use when reads are unpredictable; the default for most systems.
- **Read-through:** the cache library fetches from the store on miss. Use to keep
  app code simple and caching policy centralized.

**Write strategy**
- **Write-through:** write cache and store synchronously. Use when reads right
  after writes must be fresh and slower writes are acceptable.
- **Write-back (write-behind):** write cache now, flush to store async. Use for
  write-heavy/bursty paths that tolerate a small loss window.
- **Write-around:** write only the store; let the cache fill on read. Use when
  written data is rarely re-read soon (avoids cache churn).

**Eviction policy**
- **LRU** for recency-skewed access (most common); **LFU** for stable popularity;
  **TTL** to bound staleness; **FIFO** rarely. Match the policy to the pattern.

## Trade-offs

| Option | What it solves | What it worsens | Change it when |
|---|---|---|---|
| Cache-aside | Simple, resilient (cache down ⇒ just slower) | First read per key is a miss; risk of stale after writes | Misses are too costly → read-through + warming |
| Read-through | Centralized, clean app code | Couples app to cache lib; cold-start misses | Custom per-key load logic is needed |
| Write-through | Fresh reads after write | Slower writes; writes cached data that may never be read | Writes dominate and aren't re-read → write-around/back |
| Write-back | Fast, absorbs write bursts | Data loss window on crash; complex | Durability of recent writes is required |
| Write-around | No churn from write-only data | Recently written keys miss on first read | That data IS read right after write → write-through |
| TTL eviction | Bounds staleness automatically | Mass expiry can stampede the origin | Add jitter / soft-TTL refresh |

## Behavior under stress
A cache that misbehaves doesn't just stop helping — it can take down the origin.

- **Thundering herd / stampede:** a hot key expires (or the cache restarts) and
  thousands of concurrent misses hit the store at once. *Mitigate:* per-key locks
  / request coalescing (single-flight), early/probabilistic refresh, TTL jitter.
- **Cache penetration:** requests for keys that don't exist bypass the cache every
  time (often malicious). *Mitigate:* cache the negative result (short TTL), or a
  Bloom filter in front.
- **Hot key:** one key (a celebrity, a viral item) exceeds a single node's
  throughput. *Mitigate:* replicate the key across nodes, add a local/L1 tier, or
  shard the value.
- **Eviction storm / cold cache:** after a flush or deploy, hit rate craters and
  the origin sees full load. *Mitigate:* warm critical keys; ramp traffic.
- **Stale-after-write:** the store changed but the cache didn't. *Mitigate:*
  invalidate on write, or write-through, or short TTL — pick per staleness budget.

**Monitor:** hit rate, p99 latency, eviction rate, key distribution (hot spots),
and origin QPS during cache restarts.

## How to apply
1. **Clarify the inputs** — confirm the read:write ratio, staleness budget, and
   hot-set size (see *Clarify first*). If no number yet shows reads are the
   bottleneck, stop — a cache is not needed yet (→ `back-of-the-envelope`).
2. **Pick the strategies from the trade-off table** — choose a read strategy
   (cache-aside is the default), a write strategy keyed to the staleness budget,
   and an eviction policy matched to the access pattern.
3. **Set the key knobs** — define the key naming scheme, TTL (with jitter), and the
   per-key-family invalidation event. Decide negative-caching and single-flight up
   front, not after the first incident.
4. **Stress-test the choice** — walk each failure in *Behavior under stress*
   (stampede, penetration, hot key, cold cache, stale-after-write) and confirm a
   mitigation is in place for the ones the traffic profile can trigger.
5. **Size it with numbers** — fit the hot set in RAM across nodes, sanity-check the
   target hit rate (90%+), and confirm the node count covers peak QPS (→ *Numbers
   that matter*).
   if the user named a cloud (see *Choosing a provider*).
7. **Show the trade-off in the answer** — give a `Decision | Solves | Worsens |
   Change it when…` table with one row per choice you made here (e.g. the
   option, its store, its failure policy); the last column is a concrete trigger
   (a number or observable signal). Then name what breaks first.

## Dos and don'ts
**Do**
- Default to cache-aside; it stays correct (just slower) when the cache is down.
- Set a TTL on every entry and add jitter so keys don't expire in lockstep.
- Add single-flight / request coalescing for hot keys *before* launch.
- Invalidate on write (or write-through, or short TTL) to a stated staleness budget.
- Size the cache to the hot set and alert on hit rate, evictions, and origin QPS.

**Don't**
- Don't add a cache before a number proves reads are the bottleneck (YAGNI).
- Don't cache data that must be exactly current — go to the source instead.
- Don't let a mass-expiry or cold start dump full load on the origin (warm, ramp).
- Don't ignore non-existent-key floods — cache negatives or front with a Bloom filter.
- Don't reuse a key across schema versions — bump the version (`...:v2`) instead.

## Numbers that matter
A cache node serves ~**100k–1M QPS**, far above an RDBMS (~1k). Memory access is
~100 ns vs ms-scale disk — the reason caching wins. Size the cache to the hot set
(~20% of data ≈ 80% of reads). Target hit rates are usually 90%+; below that,
question whether the data is cacheable. → `back-of-the-envelope`.

## Interface sketch
A cache entry is a contract: a **key** (stable, namespaced, e.g.
`user:123:profile`), a **value** (serialized; watch size), and a **TTL**. Decide
the **invalidation event** per key family (on write? on TTL? on version bump?).
Versioned keys (`...:v2`) make invalidation a write of a new key instead of a
delete race.

## Related building blocks
- `content-delivery` — *pairs with* this as the edge layer above it; CDN/edge caching for static and media (that concept lives there).
- `data-storage` — *depends on* this as the origin a cache protects; its read replicas are an *alternative to* caching reads, and cache-node sharding mirrors its partitioning. (Consistent-hashing theory is *owned by* `consistency-coordination`.)
- `consistency-coordination` — *pairs with* this when staleness is unacceptable and read-your-writes or stronger guarantees are required.
- `back-of-the-envelope` — *feeds into* this skill: it supplies the read ratio and hot-set size that justify a cache.
- `resilience-failure` — *pairs with* this; rate limiting and circuit breakers (*owned* there) help contain the retry storms a misbehaving cache can trigger.
- `system-design` — *owned-concept lives in* the orchestrator: the reasoning loop, the trade-off method, and the ten failure modes.

## Deep dive: Caching deep-dive

Mechanics that don't belong in the lean SKILL.md. Read when designing the cache
layer in detail.

## Invalidation patterns (the hard part)

"There are only two hard things in CS: cache invalidation and naming things."
Pick the pattern that matches the staleness budget:

- **Invalidate-on-write (delete):** on update, delete the cache key; next read
  repopulates. Simple, but there's a race — a concurrent read can repopulate the
  *old* value between the store write and the delete. [sv-skills: corrected] Ordering the delete after the commit does **not** close it: a reader that missed before the write can still set the old value after the delete. Close it with leases (the cache hands a token on miss and rejects sets whose token was invalidated, as in Facebook's memcache), a versioned compare-and-set, or a delayed second delete; keep a short TTL as the backstop.
- **Update-on-write (write-through):** keep cache and store in lockstep. No stale
  window, slower writes.
- **TTL expiry:** let entries die after N seconds. Bounds staleness without
  tracking writes. Add **jitter** so keys written together don't expire together
  (mass-expiry stampede).
- **Versioned keys:** embed a version in the key (`user:123:v7`). A write bumps
  the version, so readers naturally fetch a fresh key and old keys age out. Turns
  invalidation into a write, sidestepping delete races. Costs key churn.

For read-your-writes: write-through the writer's own keys, or pin the writer to
read from the store for a short window. → `consistency-coordination`.

## Single-flight (request coalescing)

On a miss for a hot key, only let **one** request recompute/fetch; others wait for
that result. Prevents the thundering herd. Implement with a per-key lock/mutex
(in-process) or a distributed lock (e.g. Redis `SETNX` with a short TTL). Pair
with **probabilistic early refresh**: refresh a key *before* its TTL with a
probability that rises as expiry approaches, so it's renewed by one request
during normal traffic instead of expiring under load.

## Tiered caching (L1 + L2)

- **L1 — local/in-process** (per app instance): nanosecond access, no network
  hop, but small and per-instance (so N copies, weaker consistency).
- **L2 — distributed** (Redis/Memcached): shared across instances, larger, one
  network hop.

Read L1 → L2 → origin. L1 absorbs hot keys (mitigating the hot-key problem) at
the cost of cross-instance staleness. Use short L1 TTLs.

## Sharding a distributed cache

Spreading keys across cache nodes needs a mapping that survives node
add/remove without remapping everything:

- **Modulo hashing** (`hash(key) % N`) remaps almost all keys when N changes →
  mass miss storm. Avoid for elastic fleets.
- **Consistent hashing** moves only `~K/N` keys when a node joins/leaves. The
  standard choice. Use virtual nodes to even out load. Full mechanics in
  `consistency-coordination`.

## Redis vs Memcached (when it matters)

- **Memcached:** multithreaded, pure in-memory key/value, simple, great for
  straightforward string/object caching with high throughput. No persistence, no
  rich types.
- **Redis:** single-threaded command execution per shard (I/O threads exist since Redis 6), rich data structures (sorted sets,
  hashes, streams), optional persistence (RDB/AOF), replication, pub/sub, Lua,
  cluster mode. Choose it when you need more than get/set (rate-limit counters,
  leaderboards via sorted sets, locks, queues).

Rule of thumb: Memcached for a plain LRU object cache at scale; Redis when the
cache also does data-structure work or needs persistence/replication.

## Write-back durability

Write-back buffers writes in the cache and flushes asynchronously. The risk is the
**loss window**: a crash before flush loses recent writes. Bound it with a short
flush interval, a replicated/persistent cache (Redis AOF), or by only using
write-back for data that can be regenerated. Never write-back the system of record
for money or anything requiring durability — that's `consistency-coordination`
and `data-storage` territory.

## Common mistakes

- Caching without measuring the hit rate (a sub-50% hit rate cache is often net
  negative).
- One giant TTL for everything → synchronized mass expiry.
- Deleting on write without ordering → repopulating stale values.
- Treating the cache as durable storage.
- Ignoring the cold-start problem on deploy/restart (warm critical keys).
