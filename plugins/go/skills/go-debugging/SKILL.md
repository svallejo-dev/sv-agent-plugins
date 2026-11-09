---
name: go-debugging
description: "Go commands and tools for each diagnosis technique (isolate a test, repeat, -race, fuzzing, git bisect run, Delve, slog, benchmarks, benchstat, pprof, trace). The diagnosing-bugs skill loads it when the code is Go; also use it when the user is debugging something in Go."
license: MIT
---

# Debugging in Go

Respond in the user's language; keep common technical terms in English.

Complements `diagnosing-bugs`: that skill holds the discipline (a loop that turns red, minimize, falsifiable hypotheses, instrument, regression, cleanup); this one, the Go command for each technique.

## Phase 1: build the loop

| Technique | In Go |
|---|---|
| Failing test in isolation | `go test -run 'TestX/subcase' -count=1 ./path/...` |
| HTTP script | `curl` against the service started with `go run ./cmd/<app>` |
| Replay of a trace | Save the payload in `testdata/` and pass it through the handler with `httptest` |
| Throwaway harness | A temporary `_test.go` that builds the minimal subsystem with fakes |
| Fuzz | `go test -fuzz=FuzzX -fuzztime=60s ./path/` (the failing corpus stays in `testdata/fuzz/`) |
| Bisection | `git bisect start <bad> <good> && git bisect run go test -run TestX -count=1 ./path/...` |
| Differential | The same input to the legacy and the new service; compare the responses with `cmp.Diff` or `diff` |

**Making it tight:** `-run` to narrow it, `-count=1` to skip the cache, pin the time by injecting a clock, pin the seed (`rand.New(rand.NewPCG(seed, seed))` with `math/rand/v2`), isolate the file system with `t.TempDir()`.

**Non-deterministic bugs:** `-count=100`, `-race`, `-cpu=1,4,8`, `-parallel=16`, and a varying `GOMAXPROCS`. For logic with time and goroutines, `testing/synctest` makes scheduling deterministic.

## Phase 4: instrument

- **Debugger**: Delve. `dlv test ./path -- -test.run TestX` or `dlv debug ./cmd/<app>`; `break file.go:42`, `continue`, `print var`, `goroutines`.
- **Tagged logs**: `slog.Debug("[DEBUG-a4f2] state", "id", id)`; at the end, `grep -rn "DEBUG-a4f2" .` must come back empty.
- **Hung goroutines**: `curl localhost:6060/debug/pprof/goroutine?debug=2` if the service exposes `net/http/pprof`, or `SIGQUIT` to dump the stacks.

## Performance branch

```bash
go test -bench=BenchmarkX -benchmem -count=10 ./path/ > before.txt
# apply the change
go test -bench=BenchmarkX -benchmem -count=10 ./path/ > after.txt
benchstat before.txt after.txt                        # difference with statistical significance
go test -bench=BenchmarkX -cpuprofile=cpu.out ./path/ && go tool pprof -http=:8081 cpu.out
go test -bench=BenchmarkX -memprofile=mem.out ./path/ # also -mutexprofile, -blockprofile
go test -trace=trace.out -run TestX ./path/ && go tool trace trace.out
```

In production, compare percentiles (p50/p95/p99) in the APM before and after; the average hides the tail. For escape analysis and GC pressure: `go build -gcflags=-m` and `GODEBUG=gctrace=1`; details in `references/memory-pointers.md` of `senior-go-idiomatic`.
