# Fintech and payments

**Analogy:** a vault with a ledger. Few people come in compared with a shopping mall, but every movement must be recorded exactly once, balance at the end of the day and be auditable years later.

## Dominant forces

- **Correctness over latency**: a duplicate or lost charge is worse than a slow one.
- **Auditing and traceability**: every balance change must be explainable.
- **Compliance**: PCI DSS if card data is touched, local financial regulation, fraud and money-laundering prevention.
- **Third parties on the critical path**: gateways, acquirers, banks, card networks, with their latency and limited reliability.

## Shape of the load (without metrics)

- Modest volume compared with other archetypes, but with peaks on paydays (mid-month, end of month), campaigns and mass subscription renewals.
- Renewals and scheduled charges concentrate load at fixed hours if they are not spread out.
- Scenarios to explore: 1, 100 and 10,000 transactions per second. Almost every new product lives in the first one for a long time; the design must be correct there before it is scalable.

## Invariants and consistency

- **Double-entry ledger**: every movement has a counterpart; balances are derived from the entries, not overwritten.
- **Exactly-once effect** over at-least-once delivery: **idempotency keys** on every operation that moves money.
- Strong consistency for balances and payment states; eventual is acceptable for reports.
- Daily **reconciliation** with the third parties: your own state and the acquirer's are compared and the differences investigated.
- Payment states as an explicit state machine (pending, authorized, captured, failed, refunded), with defined valid transitions.

## Typical subdomains

- **Core**: the financial product (credit, wallet, subscriptions, scoring), ledger, risk and fraud.
- **Supporting**: reconciliation, accounting reconciliation, transactional notifications.
- **Generic**: gateway or processor, KYC, card tokenization.

## Path already walked (check before citing)

- Idempotency keys in the payments API (popularized by Stripe).
- Tokenization to take card data out of your own system and reduce the PCI DSS scope.
- Outbox to publish payment events without dual-write.

## Typical failure modes (seed for the red team)

- Timeout with the gateway after the charge was executed: retry = double charge?
- Duplicate, out-of-order or lost webhook or callback.
- Silent divergence between your own state and the processor's.
- Retries of mass renewals that hammer the processor and trigger its rate limit.
- Fraud or abuse exploiting an endpoint without limits.
- **Wrong variant of the third party's credential**: the processor's same OAuth endpoint returns different token types depending on parameters (server token, browser client token, `id_token` bound to a customer), sometimes in the same field. Requesting the wrong variant passes any shape validation; caching a customer-bound token in a shared cache hands it to someone else. It is caught with the real consumer as the oracle (walking skeleton) and with an explicit cache key.

## Questions that change the design

- Is card data touched, or is everything delegated to a processor with tokenization?
- Who is the source of truth for a payment's state: us or the processor?
- What happens to a payment whose outcome is unknown (timeout)?
- Which regulation and which auditing apply in each country?

## Hypotheses for a PoC

- Validate the state machine and idempotency against the processor's sandbox, including timeouts and duplicate webhooks triggered on purpose.
- Instrument: payments by state, time in pending state, reconciliation differences, retry rate.
- Do not leave reconciliation for later: it is the first thing to fail in production and the most expensive to add late.
