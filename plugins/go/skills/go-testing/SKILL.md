---
name: go-testing
description: "Go testing idioms, examples and tools (table-driven tests, _test packages, fakes, httptest, testcontainers, golden files, -race). The tdd skill loads it when the code is Go; also use it when the user asks how to test something in Go."
license: MIT
---

# Testing in Go

Respond in the user's language; keep common technical terms in English.

Complements `tdd`: that skill holds the rules of the red → green cycle, the seams and the anti-patterns; this one, what that looks like in Go. For advanced topics (TestMain, testcontainers, `testing/synctest`, fuzzing, benchmarks) invoke `senior-go-idiomatic` and read its `references/testing-advanced.md`.

## Shape of the tests

- Test from outside the package when possible (`package foo_test`), using only what is exported.
- **Table-driven tests** with `t.Run` when several cases share the same seam; each case with a name that describes the behavior.
- Names `TestWhat_Context_Result` (`TestCheckout_WithValidCart_Confirms`).
- Literal expected values; for large structs compare with `cmp.Diff(want, got)` (`github.com/google/go-cmp`); for long outputs, golden files in `testdata/` reviewed by hand.
- `t.Fatalf` when it makes no sense to continue (setup error); `t.Errorf` to keep reporting.
- `t.Parallel()` in independent tests; `t.Cleanup` to release resources; `t.TempDir()` for the file system.

Full examples in [tests.md](tests.md).

## Typical seams in Go

- A package's exported API.
- An `http.Handler`, tested with `httptest.NewRecorder` or `httptest.NewServer`.
- A small interface defined by the consumer.

## Test doubles

Preferences, in order: real dependency (database or queue in a container with `testcontainers-go`) → hand-written in-memory fake → `httptest.Server` imitating a third party → generated mock (`gomock`, `mockery`) only for hard external APIs, asserting results and not calls. Inject time as a dependency (`func() time.Time` or a clock). Details and examples in [mocking.md](mocking.md).

## Commands

```bash
go test ./...                              # everything
go test -run 'TestCheckout/WithCoupon' ./internal/checkout/   # one test or subtest
go test -count=1 ./...                     # without the results cache
go test -race ./...                        # data race detector; whenever there are goroutines
go test -cover ./...                       # coverage (indicative, not a target)
```

In the red → green cycle, watch the test fail with `-run <Name>` before writing the code, and run with `-race` when the code touches goroutines or shared state.
