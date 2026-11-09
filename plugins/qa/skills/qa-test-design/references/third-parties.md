# Third-party integration checklist

Third parties are the most expensive source of defects nobody saw coming: their real behavior is not in your code or in your head, it is in their system. A fake or a mock only knows what **you believed**. This checklist turns each belief about the third party into an explicit question, and each answer into a scenario.

**Analogy:** before moving to another country it is not enough to know that "they have power sockets". You ask which voltage, which plug shape and whether it changes between the bathroom and the kitchen. The adapter you bought on intuition is the bug.

## 1. Variants: does the third party return different things depending on parameters or flow?

- Does the same endpoint return **different types** depending on a parameter (`response_type`, `intent`, `grant_type`, API version, country)?
- Do two variants share **the same field or the same schema** with a different meaning? (The most dangerous trap: shape validation passes.)
- Which variant does **each flow** of the feature need? Build the **flow × variant** decision table (techniques, family B). A cell nobody knows how to fill is a question for the spec.

## 2. Cache: what does what you store depend on?

For everything cached from a third party:
- Does the value depend on the **customer**, the **domain**, the **intent**, the **country**, the **session**? All of that is part of the **cache key**. If the key is poorer than the real dependency, the cache hands one party what belonged to another.
- Which **TTL**? Does it come from the third party (`expires_in`) with a margin, or is it a fixed, invented number?
- What happens if the third party **revokes** before the TTL?
- Mandatory scenarios: two different customers request in sequence and **never** receive the same personal value; an expired value is not handed out.

## 3. Lifecycle

- Issuance, renewal, expiration, revocation. Who renews, when, and what happens during renewal (thundering herd)?

## 4. Third-party errors

- **Catalog**: which errors does it document (codes, bodies)? Each one the feature must handle is a scenario with a fake that returns it.
- **Undocumented errors**: generic 5xx, HTML instead of JSON, empty bodies.
- **Rate limits**: sandbox and production values (they usually differ), `Retry-After` headers.

## 5. Effects and deliveries

- Is the operation **idempotent** on the third party's side? Does it accept an idempotency key?
- **Timeout after execution**: what happens if the third party made the charge and the response was lost?
- **Webhooks and callbacks**: can they arrive duplicated, out of order, late or never? Is the signature verified? Is there reconciliation?

## 6. Sandbox versus production

- What behaves differently in the sandbox (test data, limits, errors that cannot be triggered)?
- Everything the sandbox does not reproduce stays as an **explicit risk** in the verification report, not as covered.

## 7. Versions

- Which API version is used? Is there a deprecation date? Are there SDK versions (v5 versus v6) that change the expected token type?

## From the checklist to the scenarios

Each answer produces scenarios on three rungs:

| What | Rung | What for |
|---|---|---|
| **Learning tests** against the sandbox, one per assumption | 2 | Confirm the third party behaves as we believe. Their responses are recorded with WireMock and feed the fakes |
| Scenarios with **fakes derived from the learning tests** | 1 | Errors, timeouts, variants, concurrency: everything the sandbox does not let you trigger |
| **Walking skeleton** with the real consumer | 3 | The thinnest end-to-end path: proves the whole path works before building logic on top |

**Walking skeleton** (Alistair Cockburn; Freeman and Pryce in *Growing Object-Oriented Software, Guided by Tests*): a minimal implementation that crosses every layer and every real integration, without business logic. Its value is that it **fails on day 1** if the integration is impossible or misunderstood. It must be the first ticket (see `to-tickets`) and the first scenario.

**Learning tests** (Jim Newkirk; popularized in *Clean Code*, chapter 8): tests you write against a third party's API to learn how it behaves, before building on top. They are cheap, document the assumptions and warn you if the third party changes in a new version.
