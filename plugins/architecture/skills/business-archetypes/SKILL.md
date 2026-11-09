---
name: business-archetypes
description: "Business archetypes for designing without prior metrics (exploratory design, PoC, new product). Each archetype (streaming and media, fintech and payments, ticketing and live events, e-commerce and marketplace, social and messaging, B2B SaaS, IoT and telemetry, mobility and logistics, healthtech, AI platform, internal event platform) gives the dominant forces, shape of the load, invariants, typical subdomains, reference architecture, failure modes and PoC hypotheses. system-design, capacity-estimation, design-stress-test and strategic-design load it; also use it when the user says \"it is like Netflix/Stripe/Uber\" or describes a product without numbers."
license: MIT
---

# Business archetypes

Respond in the user's language; keep common technical terms in English.

When there are no metrics, **the kind of business already says a lot**: a payments system does not tolerate duplicates even with little traffic; a ticket sale receives in one minute what it does not receive in a month; a streaming service is, above all, a bandwidth problem. The archetype replaces measurement as the starting point: it does not give exact numbers, it gives **which forces dominate** and **which questions change the design**.

**Analogy:** a doctor without lab results does not refuse to see the patient. They start from the typical clinical picture (age, symptoms, context), treat with what is reasonable and order the test that removes the most uncertainty. The archetype is the clinical picture.

## How to use it

1. **Identify the archetype** from the product description. If the user says "it is like X", use it as a hint, but confirm the force that matters ("do you mean the scale or the real-time nature?").
2. **Combine when it applies.** Many products are a mix: a streaming platform with subscriptions is streaming + fintech (in the billing part); a health app with telemedicine is healthtech + real-time messaging. Take from each archetype the part that corresponds to each subdomain, and do not apply the strictest one's invariants to the whole system.
3. **Read only the files that apply** in `references/`.
4. **Turn the archetype into inputs for the other skills**:
   - Forces, invariants and questions → `system-design` requirements.
   - Shape of the load and scale scenarios → exploratory mode of `capacity-estimation`.
   - Typical failure modes → seed for `design-stress-test` when there are no incidents of your own.
   - Typical subdomains → first draft for `strategic-design`.
   - PoC hypotheses → experiment plan.
5. **Declare that it is an archetype assumption**, not a measurement, and which measurement will replace it.

| Archetype | File | Force that usually dominates |
|---|---|---|
| Streaming and media (VOD and live) | [streaming-media.md](references/streaming-media.md) | Bandwidth and simultaneous audience peaks |
| Fintech and payments | [fintech-payments.md](references/fintech-payments.md) | Correctness: zero duplicates, auditing, compliance |
| Ticketing, bookings and flash sales | [event-ticketing.md](references/event-ticketing.md) | Contention over scarce inventory at extreme peaks |
| E-commerce and marketplace | [ecommerce-marketplace.md](references/ecommerce-marketplace.md) | Massive catalog reads + a correct checkout |
| Social, feeds and messaging | [social-messaging.md](references/social-messaging.md) | Fan-out, real time and skewed graphs (celebrities) |
| Multi-tenant B2B SaaS | [saas-b2b.md](references/saas-b2b.md) | Isolation between tenants and giant tenants |
| IoT and telemetry | [iot-telemetry.md](references/iot-telemetry.md) | Continuous write ingestion and time series |
| Mobility, logistics and geolocation | [mobility-logistics.md](references/mobility-logistics.md) | Real-time geospatial state and matching |
| Healthtech | [healthtech.md](references/healthtech.md) | Privacy, auditing and integration with clinical third parties |
| AI platform (inference) | [ai-platform.md](references/ai-platform.md) | Expensive, scarce compute (GPU), per-token latency |
| Internal event platform (bus, integration) | [event-platform.md](references/event-platform.md) | Contracts between teams, ordering, delivery and replay |

## If the business fits no archetype

Derive the forces with these questions, which are the ones that tell the archetypes apart:

1. What is worse for the business: wrong data or data that arrives late?
2. Is the load stable, with daily peaks, or with event peaks (×10-×100 in minutes)?
3. Do reads or writes dominate? Are the objects small (records) or large (media, files)?
4. Is there a scarce resource many compete for (inventory, drivers, GPUs)?
5. Are there disproportionate entities (a tenant, a user, a product that concentrates the load)?
6. Which regulation applies (personal data, payments, health, financial sector)?
7. What has to happen in real time (under a second) and what can be deferred?
8. Which third parties does the critical flow depend on?

With the answers, choose the closest archetype for the parts that fit and treat the rest as explicit hypotheses.

## Limits

The public cases cited in each archetype are the "path already walked" by others: use them as a starting point and check the details with `research` before citing them in a document. Their scale is almost never yours.
