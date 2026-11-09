# Catalog of semantic mutants

Business-level mutants: mistakes a dev or an agent really make. Choose by risk according to the feature's criteria; there is no need to use every category.

| Category | Mutation | Which scenario should detect it |
|---|---|---|
| **Boundary** | `<` for `<=`, `5` for `6`, `>=` for `>` in a business rule | Boundary values (technique A) |
| **Condition** | Invert a condition, remove an `else` branch, short-circuit a validation (early `return nil`) | Invalid partitions, decision tables |
| **Missing validation** | Remove the check of a mandatory field, a format or a range | Invalid partitions |
| **Authorization** | Remove the check that the resource belongs to the actor (IDOR) | Error guessing: horizontal authorization |
| **Idempotency** | Ignore the idempotency key, or use it without storing the result | Idempotency (technique D) |
| **Cache key** | Remove a dimension from the cache key (customer, domain, intent) | Third parties: cache; two customers never receive the same value |
| **TTL** | Ignore `expires_in`, or a TTL longer than the third party's | Time: expiration just before and after |
| **Third-party variant** | Request another variant (a different `response_type`), or another API version | Usage oracle and walking skeleton |
| **Swallowed error** | Turn a dependency error into an empty success, or into a 200 with a default body | Dependency failures (technique D) |
| **Retry** | Remove the retry, retry non-idempotent operations, or retry without backoff or limit | Dependency failures: 5xx, timeout after execution |
| **Timeout** | Remove the timeout of an outgoing call, or raise it above the budget | Latency with Toxiproxy |
| **State transition** | Allow an invalid transition (refunding a pending payment), or skip a state | State transitions (technique B) |
| **Concurrency** | Remove a lock, a transaction or a `SELECT … FOR UPDATE`; read then write without version control | Concurrency: last seat, double charge |
| **Serialization** | Rename a field of the response or the event, change its type, omit it when empty | Contract (Pact), usage oracle |
| **Ordering** | Change the order of a listing or of two effects (notify before persisting) | Scenarios that check order or the state after an intermediate failure |
| **Sensitive data** | Include a token or a personal data item in an error message or a log | Error guessing: sensitive data |
| **Default value** | Change a default (currency, country, time zone) | Partitions of the omitted parameter |

## How to choose

1. For each critical-priority criterion, at least one mutant that violates it.
2. For each third-party integration, at least one **variant**, one **cache key** (if there is a cache) and one **swallowed error** mutant.
3. Fill up to 5-10 with the highest-risk categories for the business archetype.

## The token case as a mutant

In the PayPal case, the mutant "request the token without `response_type=client_token`" is exactly the real bug. A suite that lets it survive has no scenario with the SDK as the usage oracle, however many tests it has. And the mutant "cache key without the customer" survives if no scenario requests tokens for two different customers.
