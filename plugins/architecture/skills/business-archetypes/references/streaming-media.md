# Streaming and media (VOD and live)

**Analogy:** a water distribution network. The problem is not producing the water (the content), it is getting it to millions of taps at once without the pressure dropping.

## Dominant forces

- **Bandwidth** above all: the system moves bytes, not transactions.
- **Massive, repetitive reads**: many people watch the same content; the edge cache is the architecture.
- **Live**: simultaneous audience with peaks at the start of an event (match, premiere) and minimal tolerance for latency.
- The experience is measured in playback start, rebuffering and quality, not in API latency.

## Shape of the load (without metrics)

- VOD: a daily wave (prime time) with ×2-3 peaks over the average and premieres that concentrate the audience.
- Live: a sharp ramp in the minutes before the event; the "thundering herd" of login, authorization and manifest at the same time.
- Key formula: **egress ≈ concurrent viewers × average bitrate**. An HD stream is on the order of a few Mbps; that is why thousands of concurrent viewers are already Gbps and millions are Tbps (check the codec's real bitrates and the quality ladder).
- Scenarios to explore: 1k, 100k and 10M concurrent viewers. The first fits in a commercial CDN without thinking about it; the last one demands agreements with multiple CDNs or an own network.

## Invariants and consistency

- Rights and geo-blocking (what who can watch and where): it must be correct, but it can be cached with a short TTL.
- Playback state ("continue watching"): eventual is fine.
- Payment entitlement: correct at authorization, tolerant of seconds of delay.

## Typical subdomains

- **Core**: playback experience (ABR, fast start), recommendation and discovery, rights management.
- **Supporting**: catalog and metadata, profiles, ingestion and transcoding.
- **Generic**: CDN, DRM, payments, authentication.

## Path already walked (check before citing)

- Adaptive bitrate streaming (HLS/DASH): the client changes quality according to its network.
- An own CDN inside the ISPs (Netflix Open Connect) at very large scale; commercial CDNs and multi-CDN before that.
- Chaos engineering was born in this domain (Netflix, Chaos Monkey).

## Typical failure modes (seed for the red team)

- Thundering herd at the start of a live event on auth, entitlement and manifests.
- Cold edge cache after a purge or a very popular new title: the origin receives everything.
- Outage or degradation of a CDN without a multi-CDN strategy.
- DRM or licenses as a synchronous dependency of playback start.
- Egress costs growing faster than revenue.

## Questions that change the design

- VOD, live or both? What live latency is tolerated (seconds vs tens of seconds)?
- How many simultaneous viewers at the worst imaginable event?
- Which part of the chain is your own (ingestion, transcoding) and which is bought?
- Are there DRM or geo-blocking requirements by contract with the content owners?

## Hypotheses for a PoC

- First validate start time and rebuffering with a commercial CDN and standard ABR; an own distribution network is almost never needed in a PoC.
- Instrument from day one: time to first frame, rebuffering ratio, average bitrate served, CDN hit ratio, egress per viewer.
- Simulate the start of a live event (a ramp of logins and manifests) before promising scale.
