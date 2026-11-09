# Social, feeds and messaging

**Analogy:** a town square with loudspeakers. Most people talk to a few neighbors, but some have a loudspeaker that reaches millions, and that changes the whole sound system.

## Dominant forces

- **Fan-out**: a message or post is delivered to many recipients.
- **Skewed graph**: a few users (celebrities, huge groups) concentrate followers and traffic.
- **Real time**: chat, presence, push notifications; persistent connections (WebSockets).
- High write volume (messages, likes, events) and storage that grows without stopping.

## Shape of the load (without metrics)

- Feed reads far above posts; peaks from cultural or sporting events.
- Persistent concurrent connections as a resource in their own right (memory per connection, balancing long-lived connections).
- Scenarios to explore: 10k, 1M and 100M daily active users, with a user with 10M followers in the medium scenario.

## Invariants and consistency

- Messages in a chat in order within the conversation; at-least-once delivery with deduplication on the client.
- Read-your-writes for the author (they see their own post instantly); eventual for the others.
- Counters (likes, views) approximate and eventual.
- Privacy and blocks: they must be applied correctly even if the rest is eventual.

## Typical subdomains

- **Core**: social graph, feed ranking, real-time message delivery.
- **Supporting**: profiles, media, content moderation, search.
- **Generic**: push notifications, object storage, authentication.

## Path already walked (check before citing)

- Fan-out on write for most accounts and fan-out on read for accounts with many followers (Twitter's hybrid model).
- Graph caches at large scale (Facebook's TAO).
- Message storage migrations due to tail latency problems (Discord, from Cassandra to ScyllaDB).
- Messaging with Erlang/BEAM and many connections per server (WhatsApp).

## Typical failure modes (seed for the red team)

- A celebrity posts: fan-out on write generates millions of writes at once.
- A hot partition in a huge group's message store.
- Mass WebSocket reconnection after a deploy or an outage (thundering herd).
- Counters with writes concentrated on a single row.
- Slow moderation that leaves harmful content visible.

## Questions that change the design

- Chronological or ranked feed? 1-to-1 chat, groups, or massive channels?
- What is the maximum size of a group or how many followers can an account have?
- How much history is kept and for how long?
- What delivery latency counts as "real time" for the product?

## Hypotheses for a PoC

- Validate the fan-out model with a synthetic skewed distribution (a few users with many followers), not a uniform one.
- Validate the mass reconnection of real-time clients.
- Instrument: end-to-end delivery latency, connections per node, size of the fan-out queues, duplicate messages on the client.
