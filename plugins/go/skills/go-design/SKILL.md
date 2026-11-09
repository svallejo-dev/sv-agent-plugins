---
name: go-design
description: "Translates the deep-module vocabulary (module, interface, seam, adapter, depth) into Go's tools (packages, internal/, consumer-side interfaces, constructor injection). The codebase-design skill loads it when the code is Go; also use it when designing the interface of a Go package."
license: MIT
---

# Design in Go

Respond in the user's language; keep common technical terms in English.

Complements `codebase-design`: that skill holds the vocabulary and the principles (depth as leverage, the deletion test, one adapter = hypothetical seam); this one, how they are expressed in Go. To go deeper, invoke:

- `go-design-rules`: Law of Demeter, Tell-Don't-Ask, CQS, named types, illegal states, explicit dependencies, DRY/SOLID in Go.
- `ddd-go-idiomatic`: value objects, entities, aggregates, bounded contexts, use cases and file layout.
- `senior-go-idiomatic`: interfaces and composition, project layout (`cmd/`, `internal/`, composition root).

## The vocabulary in Go

| Concept | In Go |
|---|---|
| **Module** | A function, a type with its methods, a package. The package is the natural unit of depth. |
| **Interface** (in the broad sense) | What the package exports plus its invariants, errors (sentinel or typed), `context.Context` and concurrency requirements. Not just the `interface` keyword. |
| **Hiding the implementation** | Unexported identifiers; subpackages inside `internal/`, which the compiler prevents importing from outside the tree. |
| **Seam** | A small `interface` declared in the **consumer** package, with the methods it uses. "Accept interfaces, return structs." |
| **Adapter** | A concrete struct that satisfies that interface: the Postgres repository in production, the in-memory fake in tests. |
| **Dependency injection** | Through the constructor (`NewService(repo Repo, now func() time.Time)`), wired in the composition root at `cmd/<app>/main.go`. No globals or singletons. |

## Rules

- **Do not declare an `interface` next to its only implementation.** Until there are two adapters (usually production + test), it is indirection; return the concrete struct.
- **Small interfaces.** If the consumer uses two methods, the interface has two methods.
- **Depth per package.** One exported function that does a lot is worth more than ten that forward. If the package exports almost as much as it implements, it is shallow.
- **The deletion test in Go**: if deleting the package only forces moving three lines into each caller, it was a pass-through.
- **Dependency categories** (from `DEEPENING.md` in `codebase-design`): locally substitutable → a container with `testcontainers-go`, `fstest.MapFS` or `t.TempDir()`; remote but owned → port as a consumer-side `interface` + HTTP/gRPC adapter + in-memory adapter; external → port + `httptest.Server` or a fake.

## Example

```go
// Consumer package: subscriptions. It declares only what it uses.
type Charger interface {
	Charge(ctx context.Context, amount Money) (ChargeID, error)
}

type Service struct {
	charges Charger
	now     func() time.Time
}

func NewService(c Charger, now func() time.Time) *Service {
	return &Service{charges: c, now: now}
}

// Deep interface: one operation that hides renewal rules, retries and events.
func (s *Service) Renew(ctx context.Context, id SubscriptionID) error { ... }
```

The payment gateway client (another package) returns a concrete struct that satisfies `Charger` without knowing it exists; the test uses an in-memory fake.
