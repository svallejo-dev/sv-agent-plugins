# When to use test doubles

Examples in pseudocode. For the tools and the idiomatic form in a specific language, use the `<language>-testing` skill if available.

Use doubles only at the **system's boundaries**:

- External APIs (payment gateways, partners, auth providers)
- Databases (sometimes; prefer a real test database)
- Time and randomness
- File system (sometimes; a temporary directory is usually enough)

Do not use doubles for:

- Your own modules
- Internal collaborators
- Anything you control

Analogy: a double is a stand-in actor replacing someone you cannot bring to the set (the bank, the partner). You let your own actors act.

## Preferences

1. **Real dependency before a double.** For databases, queues or caches, use a real test instance (a container or the CI one). A database double tests your assumption about the database, not the database.
2. **Hand-written fakes before generated mocks.** An in-memory fake that implements the interface gives tests that read like real usage. Generated mocks only for external APIs that are hard to simulate, and even then asserting results, not calls.
3. **Fake HTTP server for external APIs.** Start a local server that answers like the partner and point the client at its URL: you test the real client, the parsing and the errors.

## Designing for substitution

**1. Inject dependencies**

```text
// Easy to substitute
processPayment(order, charger):
    return charger.charge(order.total)

// Hard to substitute
processPayment(order):
    client = newPaymentGatewayClient(env("PAYMENT_GATEWAY_KEY"))
    return client.charge(order.total)
```

**2. Small interfaces defined by whoever uses them**

Declare the interface where it is consumed, with only the operations that consumer needs, not next to the implementation with everything it offers.

**3. Specific operations before a generic fetcher**

```text
// GOOD: each operation is substituted separately
interface PartnerClient:
    getUser(id) -> User
    listSubscriptions(userId) -> [Subscription]
    createSubscription(data) -> Subscription

// BAD: the double needs conditional logic inside
interface PartnerClient:
    do(method, path, body) -> bytes
```

With specific operations, each double returns a concrete shape, there is no conditional logic in the setup, you can see which operations each test uses and there is typing per operation.

**4. Time is injected too**

Pass a clock (or a function that returns "now") as a dependency. In production it is the system clock; in the test, a fixed date.
