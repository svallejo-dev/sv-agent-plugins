<!-- Origen: proyecto26/system-design-skills (MIT), skills/blob-store, commit 228d57d. Curado para sv-skills: sin archivos de proveedor ni diagramas; correcciones marcadas con [sv-skills]. -->

# Blob store

Store large, immutable, unstructured objects — images, video, backups, model
weights, document blobs — in a flat namespace keyed by a string, replicated for
durability and served by direct download. Getting it wrong means stuffing
multi-megabyte blobs into a row-oriented database (where they bloat the working
set, wreck cache locality, and cap throughput) or hand-rolling a file server that
loses data on the first disk failure.

## When to reach for this
Objects are large (KB to GB), written once and read many times, and you only ever
fetch them whole by key — never query *inside* them. Photo/video stores, user
uploads, backups, data-lake/ML datasets, static-site assets, log archives. The
access pattern is `PUT key → GET key`, durability matters, and the total volume is
too large or too cold to sit in a primary database.

## When NOT to
Small structured records you query, filter, sort, or join — that is `data-storage`.
Data that needs transactions, secondary indexes, or partial updates (blobs are
replace-whole, not edit-in-place). Low-latency reads of tiny values (a KV cache or
`caching` wins). A few files on one box that never grow — the local filesystem is
fine; a blob store is operational overhead you do not need yet (YAGNI). Naming
"object storage" for a workload that is really a database is failure mode #2.

## Clarify first
- **Object size distribution** — average and p99 size? (Decides chunking, multipart
  thresholds, and whether reads stream or buffer.) → `back-of-the-envelope`.
- **Read:write ratio and access recency** — write-once/read-many? How fast does data
  go cold? (Drives tiering and CDN fronting.)
- **Durability and availability target** — how many nines of durability? Can a read
  briefly fail or must it always succeed? (Replication vs erasure coding, multi-region.)
- **Access control** — public, private, or time-limited per-object grants? (Signed URLs.)
- **Mutability and history** — do objects change? Must old versions be retained
  (compliance, undo)? (Versioning + lifecycle.)
- **Egress profile** — who reads, from where, how often? (CDN offload, egress cost.)

## The options
**Durability scheme** (how many copies, what shape)
- **N-way replication** — store N full copies on different nodes/racks/AZs. Use when
  objects are small, hot, and latency matters; simplest to reason about.
- **Erasure coding (EC)** — split an object into *k* data + *m* parity shards; any *k*
  reconstruct it. Use for large/cold data at scale — same durability as replication
  at ~1.4x overhead instead of 3x. (Mechanics in `references/deep-dive.md`.)

**Storage tier** (price/latency/retrieval trade)
- **Hot/standard** — millisecond reads, highest $/GB. Use for actively served objects.
- **Cool/infrequent** — cheaper storage, retrieval fee/slightly higher latency. Use
  for backups and data read a few times a month.
- **Archive/cold** — cheapest storage, minutes-to-hours retrieval. Use for compliance
  retention and rarely-touched data; never for anything on a request path.

**Upload path**
- **Single PUT** — one request. Use for small objects (under the multipart threshold).
- **Multipart / resumable** — split into parts, upload in parallel, retry per-part,
  commit on completion. Use for large objects and flaky networks; the default above
  the threshold.

**Mutation model**
- **Immutable + versioning** — each write is a new version; deletes are tombstones.
  Use when history, undo, or accidental-overwrite protection matters.
- **Overwrite-in-place (last-writer-wins)** — simplest; no history. Use when only the
  latest object matters and storage of old copies is waste.

## Trade-offs

| Option | What it solves | What it worsens | Change it when |
|---|---|---|---|
| N-way replication | Simple, fast reads, fast rebuild | 3x+ storage cost | Data is large/cold and cost dominates → erasure coding |
| Erasure coding | Same durability at ~1.4x storage | CPU + multi-node read on every fetch; slow small-object reads; costly rebuild | Objects are small/hot and latency matters → replication |
| Hot tier | Low-latency serving | Highest $/GB | Data goes cold and is rarely read → cool/archive |
| Archive tier | Cheapest at-rest storage | Minutes–hours to first byte; retrieval fees | Anything ends up on a latency-sensitive path → hot/cool |
| Multipart/resumable upload | Large files survive flaky links; parallel throughput | More client logic; orphaned parts cost money | Objects are small → single PUT |
| Versioning | Undo, history, overwrite protection | Storage grows silently; needs lifecycle expiry | Only latest matters → overwrite, last-writer-wins |
| Signed URLs | Offload transfer off your app; scoped access | Leaked/over-broad URLs; clock-skew expiry bugs | Content is fully public → CDN + public read |

## Behavior under stress
A blob store rarely "falls over" the way a database does, but it amplifies trouble in
specific ways.

- **Hot object / hot prefix:** a viral file or a key scheme where many writes share a
  prefix concentrates load on one partition. *Mitigate:* front hot reads with a CDN
  (`content-delivery`), randomize/hash key prefixes, replicate the hot object.
- **Metadata-index bottleneck:** the index that maps key → shard locations is the real
  SPOF and the throughput ceiling (millions of tiny objects hurt far more than a few
  huge ones). *Mitigate:* shard the index, cache hot lookups, prefer fewer-larger objects.
- **Thundering herd on cold-tier promotion:** a burst of reads for archived data
  triggers slow, expensive bulk retrievals. *Mitigate:* expose retrieval as async, queue
  it (`messaging-streaming`), set expectations on latency.
- **Orphaned multipart uploads:** aborted uploads leave parts that silently accrue cost.
  *Mitigate:* lifecycle rule to abort incomplete uploads after N days.
- **Egress storm / cost blow-up:** a popular object served directly from origin saturates
  bandwidth and runs up egress bills. *Mitigate:* CDN in front; the origin should serve
  cache fills, not end users.
- **Partial failure during write:** a node dies mid-write. *Mitigate:* write is not
  acknowledged until the durability quorum (replicas or EC shards) is met; background
  repair re-replicates under-durable objects.

**Monitor:** request rate and error rate per operation (PUT/GET/DELETE), p99 first-byte
latency, durability/repair queue depth, per-prefix hotness, incomplete-multipart count,
and egress volume + cost.

## How to apply
1. **Clarify the inputs** — pin object size distribution, read:write ratio, durability
   target, access control, and egress profile (see *Clarify first*). If the data is
   really small structured records you query, stop — use `data-storage`.
2. **Pick from the trade-off table** — choose a durability scheme (replication for
   small/hot, erasure coding for large/cold), a default tier, an upload path keyed to
   size, and a mutation model keyed to whether history matters.
3. **Set the key knobs** — design the key/prefix scheme to avoid hotspots, set the
   multipart threshold and part size, define lifecycle rules (tier transitions, version
   expiry, abort-incomplete-uploads), and decide signed-URL TTLs.
4. **Stress-test the choice** — walk each item in *Behavior under stress* (hot object,
   metadata bottleneck, cold-retrieval herd, orphaned parts, egress storm) and confirm a
   mitigation exists for the ones this traffic can trigger.
5. **Size it with numbers** — total storage with replication/EC overhead, object count
   (metadata-index load), peak PUT/GET QPS, and monthly egress. → *Numbers that matter*.
   user named a cloud (see *Choosing a provider*).
7. **Show the trade-off in the answer** — give a `Decision | Solves | Worsens |
   Change it when…` table with one row per choice you made here (e.g. the
   option, its store, its failure policy); the last column is a concrete trigger
   (a number or observable signal). Then name what breaks first.

## Dos and don'ts
**Do**
- Keep the blob in the store and a *pointer* (key + metadata) in the database — never the
  bytes in a row.
- Treat objects as immutable; version instead of editing in place when history matters.
- Front public/hot reads with a CDN so the origin serves fills, not end users.
- Use multipart/resumable upload above the size threshold, and abort incomplete uploads via lifecycle.
- Design key prefixes to spread load; hash or shuffle high-cardinality prefixes.
- Set lifecycle rules to move cold data down tiers and expire old versions automatically.

**Don't**
- Don't store large blobs in a relational/NoSQL row — it wrecks the working set and throughput.
- Don't put archive tiers on a read path; minutes-to-hours retrieval will time out requests.
- Don't serve a popular object directly from origin without a CDN (egress blowup).
- Don't hand out broad or long-lived signed URLs; scope them tight and short.
- Don't assume erasure coding is free — it adds CPU, multi-node reads, and expensive rebuilds.
- Don't ignore millions-of-tiny-objects: the metadata index, not the disks, is the ceiling.

## Numbers that matter
The figures that drive the design: total stored bytes × durability overhead (replication
≈ 3x, erasure coding ≈ 1.3–1.5x), object *count* (the metadata index scales with count, not
size), peak upload/download QPS, and monthly egress (often the dominant cost). Object-store
durability targets are commonly quoted around eleven nines; treat that as a design goal set
by the durability scheme, not a given. For the actual storage/bandwidth/QPS arithmetic and
unit conversions, use `back-of-the-envelope` — do not restate its tables here.

## Interface sketch
The contract is small and key-addressed:
```
PUT    /{bucket}/{key}        body=bytes, headers: Content-Type, optional checksum
GET    /{bucket}/{key}        → bytes (supports Range for partial/streamed reads)
DELETE /{bucket}/{key}        → tombstone (new version if versioning on)
HEAD   /{bucket}/{key}        → metadata only (size, etag, version-id)
# multipart: Initiate → UploadPart×N (parallel, retryable) → Complete | Abort
# signed URL: presign(GET|PUT, key, expiry) → time-limited URL the client uses directly
```
The **key** is the whole index (e.g. `userId/2026/photo-uuid.jpg`); choose it for both
access pattern and prefix spread. The **etag/checksum** lets clients verify integrity and
do conditional requests. The database stores this key plus app metadata, not the bytes.

## Related building blocks
- `content-delivery` — *pairs with* this: a CDN fronts the blob origin so repeat reads are
  served from the edge and the store handles only cache fills (edge caching is *owned* there).
- `data-storage` — *alternative to* this for large unstructured objects: store the blob here,
  keep a pointer (key + metadata) in the DB; sharding/indexing the metadata is *owned* there.
- `back-of-the-envelope` — *depends on* this for storage, object-count, QPS, and egress sizing
  (the numbers that pick replication vs EC and a tier live there).
- `messaging-streaming` — *pairs with* this to queue async work like cold-tier retrieval and
  post-upload processing (transcode, thumbnail); delivery guarantees are *owned* there.
- `caching` — *pairs with* this for hot small-object reads and metadata-lookup offload.
- `system-design` — *owned-concept lives in* the orchestrator: the reasoning loop, the
  trade-off method, and the ten failure modes.

## Deep dive: Blob store deep-dive

Mechanics that don't belong in the lean SKILL.md. Read when designing the object
store in detail.

## Anatomy: data plane + metadata index

A blob store is two systems wearing one API:

- **Data plane** — the storage nodes that hold the actual bytes (as full replicas or
  erasure-coded shards) on disks/SSDs across racks/AZs.
- **Metadata index** — the key/value map from `bucket/key` → `{size, etag, version,
  shard/replica locations, tier, ACL}`. This is the brain and the bottleneck.

A GET is: look up the key in the index → resolve locations → stream bytes from the
data plane. The index is consulted on *every* request, so it must be fast, sharded,
and highly available. It scales with **object count**, not total bytes — ten billion
1 KB objects is a far harder index problem than ten thousand 1 GB objects, even though
the second holds more data. Prefer fewer, larger objects; pack tiny objects together
(tar/parquet/log segments) when you control the producer.

## Chunking

Large objects are stored as fixed-size **chunks** (commonly a few MB each):

- **Parallelism** — chunks upload/download/replicate in parallel.
- **Resumability** — a failed transfer retries only the affected chunks.
- **Dedup (optional)** — content-addressed chunks (hash as the chunk id) let identical
  data across objects share storage; great for backups/snapshots, costs a dedup index.
- **Range reads** — a GET with a byte range fetches only the chunks it needs (video
  seeking, partial reads) without pulling the whole object.

The object's metadata holds an ordered chunk manifest; the data plane stores chunks.

## Durability: replication vs erasure coding

**N-way replication.** Keep N identical copies on independent failure domains (different
disks, racks, AZs). A write is acknowledged when a quorum of copies is durable. Reads hit
any copy (fast, single-node). Rebuild after a disk loss is a straight copy. Cost: N× the
bytes (3× is typical for ~11 nines).

**Erasure coding (Reed–Solomon).** Split the object into *k* data shards, compute *m*
parity shards, store all *k+m* on independent domains. Any *k* of the *k+m* shards
reconstruct the object, so it tolerates *m* simultaneous losses.

- Storage overhead = `(k+m)/k`. E.g. (10,4) → 1.4× and survives 4 losses — far cheaper than
  3× replication for comparable durability.
- **Costs:** every read gathers *k* shards from *k* nodes (more network, higher tail latency,
  bad for small/hot objects); writes do parity math (CPU); a single lost shard rebuild reads
  *k* shards to regenerate one (expensive, amplifies on correlated failures).
- **Use it** for large, cold, throughput-oriented data; **replicate** small/hot/latency-
  sensitive data. Many stores replicate hot tiers and EC cold tiers.

**Background repair / anti-entropy.** Storage nodes continuously scrub (checksum) data and
re-replicate or re-encode objects that fall below their target redundancy after failures.
Watch repair-queue depth: a deep queue means under-durable objects are accumulating faster
than the system heals.

## Consistency model

Object stores historically offered read-after-write for new keys but only eventual
consistency for overwrites/deletes; most now provide strong read-after-write for PUT, GET,
and DELETE. Still, *listing* a bucket can lag a just-written object, and cross-region
replication is asynchronous (a region can serve a stale object after failover). Treat
objects as immutable and version them to sidestep overwrite-consistency entirely. CAP/
consistency-model theory lives in `consistency-coordination`.

## Versioning, tombstones, and lifecycle

- **Versioning on** → every PUT to an existing key creates a new immutable version; a DELETE
  writes a **tombstone** (delete marker) rather than erasing data, so deletes are
  recoverable. Reads return the latest non-tombstone version.
- **Lifecycle rules** automate the silent-growth problem: transition objects to cooler tiers
  after N days, expire non-current versions after M days, and **abort incomplete multipart
  uploads** after K days (orphaned parts cost real money). Without these, versioning and
  multipart both leak storage indefinitely.

## Multipart / resumable upload (the protocol)

1. **Initiate** → server returns an `uploadId`.
2. **UploadPart** for each part (typically ≥5 MB except the last), in parallel; each returns
   a part etag. Failed parts retry independently — the win for flaky networks.
3. **Complete** with the ordered list of part etags → server assembles and exposes the
   object atomically (it does not appear until completion).
4. **Abort** discards parts; lifecycle should also reap forgotten uploads.

Resumable-upload variants (e.g. session-URI style) let a client query how many bytes the
server already has and resume from there after a disconnect.

## Signed (presigned) URLs

The app holds the credentials; it signs a URL that grants a single client a scoped,
time-limited operation (GET or PUT a specific key) and hands it over. The client then
transfers bytes *directly* to/from the store, so large transfers never traverse the app
tier. Pitfalls: the signature encodes an expiry — clock skew or too-long TTLs widen the
leak window; a presigned PUT can let a client overwrite a key, so scope to exact key/method
and short expiry; signed URLs are bearer tokens, so anyone with the link has the access
until it expires.

## Key design and hot prefixes

The key *is* the index. Two forces:

- **Access pattern** — encode what you list/fetch by (`userId/album/photo-uuid`).
- **Prefix spread** — request routing/partitioning can key on the prefix, so monotonic or
  shared prefixes (a date prefix, a single hot user) concentrate load on one partition. Add
  a hash/shuffle to the high-order bytes of hot prefixes to spread them. Sharding/
  partitioning theory (incl. consistent hashing) is `data-storage` / `consistency-coordination`.

## Self-hosted internals (open source)

- **Ceph (RADOS)** — CRUSH algorithm maps objects to placement groups → OSDs without a central
  lookup; supports replication and EC pools; S3-compatible via RGW.
- **MinIO** — S3-compatible, simple, EC by default within a node set; good for on-prem S3.
- **SeaweedFS** — optimized for *many small files*: a master tracks volumes, files are packed
  into large volume files to keep the metadata footprint tiny (directly addresses the
  small-object index problem above).

## Common mistakes

- Storing bytes in the database instead of a pointer to the blob.
- One giant object instead of chunks (no parallelism, no resumability, no range reads).
- Erasure coding small/hot objects (latency and rebuild cost dominate).
- No lifecycle rules → versions and orphaned multipart parts grow storage without bound.
- Serving popular objects from origin without a CDN (egress cost + saturation).
- Long-lived, broadly-scoped signed URLs treated as if they were access-controlled.
- Ignoring object *count*: the metadata index, not raw disk, is the scaling ceiling.
