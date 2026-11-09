# The usage oracle

**Rule:** if the system produces something someone else consumes, the criterion is verified with the real consumer. The shape of the artifact is a complementary criterion, never the only one.

**Analogy:** a hotel. There is a master key, a generic guest key and a room key. The locksmith can check that the key is cut correctly (the shape). Only the door says whether it is the right key (the use). And a room key copied and handed to anyone who asks is a problem even if it opens perfectly.

## Why the shape is not enough

A test that checks the shape is written by someone with the **same belief** as whoever implemented it: if the dev believed that "the token is what the OAuth endpoint returns", the test checks exactly that, and passes. The real consumer does not share your belief: it is an **independent** oracle. It is the same principle that separates the dev agent from the QA agent, applied to the boundary with other systems.

## Reference case: the PayPal token

A BFF requested a token from PayPal's OAuth API, cached it and handed it to whoever asked. Late integration tests showed that the consumer needed **another kind of token**, with a different shape.

What makes the case deceptive:
- The same endpoint (`/v1/oauth2/token`) returns different tokens depending on `response_type`: a server token by default, a browser-safe client token (`response_type=client_token`), or a JWT `id_token` (`response_type=id_token`, optionally with `target_customer_id` for a returning buyer).
- The client token arrives in the **same field** `access_token` as the server token. The schema is identical; the meaning changes.
- An `id_token` with `target_customer_id` is **bound to one customer**: a shared cache that hands it to anyone is a cache-key bug with security impact.

(PayPal details checked against its documentation in November 2026; check them again before using them as fact.)

How each criterion would have caught it:

| Criterion | Does it catch the bug? |
|---|---|
| "The endpoint returns 200 and a non-empty token" | No |
| "The token is a JWT" | Only if someone already knew which shape to expect |
| "The token lets the SDK initialize and complete the checkout in sandbox, for each flow (checkout, save payment method, pay with saved method)" | **Yes, on day 1** |
| "A token handed to one customer is never handed to another customer" | **Yes**: it reveals the cache-key bug |

## Patterns by artifact type

| The system produces… | Consumer | Usage oracle |
|---|---|---|
| Token or credential | SDK, front end, another service | The consumer accepts it for the specific operation, in the specific flow |
| Published event | Subscribers | A test consumer deserializes it with the real subscriber's schema and produces the expected effect |
| Outgoing webhook | Partner | The partner's signature verification (or its validator) accepts it |
| Exported file (CSV, reconciliation) | Accounting system, bank, analyst | The target's importer processes it without errors and the totals match |
| Public API response | Mobile or web clients | Consumer Pact, or the real client in a smoke test |
| Signed URL or link | Browser, CDN | The URL downloads the resource and expires when it should |
| Email or notification | User | The test email provider receives it with working links |

## How it becomes a scenario

The usage oracle usually requires **rung 3** (real consumer with real dependencies) or **rung 2** (consumer contract). See [../../qa-core/references/environment-ladder.md](../../qa-core/references/environment-ladder.md). If the real consumer cannot be brought up on any rung, the scenario stays `blocked-testability` and is explicit debt, not a criterion downgraded to checking the shape.

For third-party integrations, the usage criterion comes with a **walking skeleton** as the first ticket (see `to-tickets`): the thinnest slice that crosses the whole path with the real consumer, before any logic or cache.
