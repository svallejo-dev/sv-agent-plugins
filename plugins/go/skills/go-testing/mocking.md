# When to use test doubles (Go)

Use doubles only at the **system's boundaries**:

- External APIs (payment gateways, partners, auth providers)
- Databases (sometimes; prefer a real test database)
- Time and randomness
- File system (sometimes; `fstest.MapFS` or `t.TempDir()` are usually enough)

Do not use doubles for:

- Your own types or packages
- Internal collaborators
- Anything you control

Analogy: a double is a stand-in actor replacing someone you cannot bring to the set (the bank, the partner). You let your own actors act.

## Preferences in Go

1. **Real database before a double.** For Postgres or MySQL, use a test database (a container with `testcontainers-go` or a CI instance). The same for Redis or Kafka. A database double tests your assumption about the database, not the database.
2. **Hand-written fakes before generated mocks.** An in-memory fake that implements the interface (a `map` protected by a `sync.Mutex`) gives tests that read like real usage. Generated mocks (`gomock`, `mockery`) only for external APIs that are hard to simulate, and even then asserting results, not calls.
3. **`httptest.Server` for external HTTP APIs.** Start a server that answers like the partner and point the client at its URL. You test the real HTTP client, the parsing and the errors.

## Designing for substitution

At the boundaries, design interfaces that are easy to substitute:

**1. Inject dependencies**

Pass external dependencies in instead of creating them inside:

```go
// Easy to substitute
func ProcessPayment(ctx context.Context, o Order, charges Charger) error {
	return charges.Charge(ctx, o.Total)
}

// Hard to substitute
func ProcessPayment(ctx context.Context, o Order) error {
	client := paymentgateway.NewClient(os.Getenv("PAYMENT_GATEWAY_KEY"))
	return client.Charge(ctx, o.Total)
}
```

**2. Small interfaces defined by the consumer**

"Accept interfaces, return structs." Define the interface in the package that uses it, with only the methods it needs, not in the package that implements it:

```go
// In the subscriptions package, not in the payment gateway client
type Charger interface {
	Charge(ctx context.Context, amount Money) (ChargeID, error)
}
```

**3. Specific methods before a generic fetcher**

Create one method per external operation instead of a generic one with conditional logic:

```go
// GOOD: each method is substituted separately
type PartnerClient interface {
	GetUser(ctx context.Context, id string) (User, error)
	ListSubscriptions(ctx context.Context, userID string) ([]Subscription, error)
	CreateSubscription(ctx context.Context, s NewSubscription) (Subscription, error)
}

// BAD: the double needs conditional logic inside
type PartnerClient interface {
	Do(ctx context.Context, method, path string, body any) ([]byte, error)
}
```

With specific methods:
- Each double returns a concrete shape
- There is no conditional logic in the test setup
- You can see which operations each test uses
- There is typing per operation

**4. Time is injected too**

```go
type Clock func() time.Time

func NewService(repo Repo, now Clock) *Service { ... }

// In production: NewService(repo, time.Now)
// In the test:   NewService(repo, func() time.Time { return fixedDate })
```
