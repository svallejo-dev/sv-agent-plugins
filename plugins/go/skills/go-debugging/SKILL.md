---
name: go-debugging
description: "Comandos y herramientas de Go para cada técnica de diagnóstico (aislar un test, repetir, -race, fuzzing, git bisect run, Delve, slog, benchmarks, benchstat, pprof, trace). La carga la skill diagnosing-bugs cuando el código es Go; úsala también cuando el usuario depure algo en Go."
license: MIT
---

# Debugging en Go

Responde en español y conserva en inglés los términos técnicos habituales.

Complementa a `diagnosing-bugs`: allí está la disciplina (loop que se pone rojo, minimizar, hipótesis falsables, instrumentar, regresión, limpieza); aquí, el comando de Go para cada técnica.

## Fase 1: construir el loop

| Técnica | En Go |
|---|---|
| Test que falla aislado | `go test -run 'TestX/subcaso' -count=1 ./ruta/...` |
| Script HTTP | `curl` contra el servicio levantado con `go run ./cmd/<app>` |
| Replay de una traza | Guarda el payload en `testdata/` y pásalo por el handler con `httptest` |
| Harness desechable | Un `_test.go` temporal que construye el subsistema mínimo con fakes |
| Fuzz | `go test -fuzz=FuzzX -fuzztime=60s ./ruta/` (el corpus que falla queda en `testdata/fuzz/`) |
| Bisección | `git bisect start <malo> <bueno> && git bisect run go test -run TestX -count=1 ./ruta/...` |
| Diferencial | Mismo input al servicio legacy y al nuevo; compara las respuestas con `cmp.Diff` o `diff` |

**Hacerlo tight:** `-run` para acotar, `-count=1` para saltar la caché, fija el tiempo inyectando un reloj, fija la semilla (`rand.New(rand.NewPCG(seed, seed))` con `math/rand/v2`), aísla el filesystem con `t.TempDir()`.

**Bugs no deterministas:** `-count=100`, `-race`, `-cpu=1,4,8`, `-parallel=16`, y `GOMAXPROCS` variable. Para lógica con tiempo y goroutines, `testing/synctest` hace determinista la planificación.

## Fase 4: instrumentar

- **Debugger**: Delve. `dlv test ./ruta -- -test.run TestX` o `dlv debug ./cmd/<app>`; `break archivo.go:42`, `continue`, `print var`, `goroutines`.
- **Logs etiquetados**: `slog.Debug("[DEBUG-a4f2] estado", "id", id)`; al final, `grep -rn "DEBUG-a4f2" .` debe quedar vacío.
- **Goroutines colgadas**: `curl localhost:6060/debug/pprof/goroutine?debug=2` si el servicio expone `net/http/pprof`, o `SIGQUIT` para volcar los stacks.

## Rama de rendimiento

```bash
go test -bench=BenchmarkX -benchmem -count=10 ./ruta/ > antes.txt
# aplica el cambio
go test -bench=BenchmarkX -benchmem -count=10 ./ruta/ > despues.txt
benchstat antes.txt despues.txt                       # diferencia con significancia estadística
go test -bench=BenchmarkX -cpuprofile=cpu.out ./ruta/ && go tool pprof -http=:8081 cpu.out
go test -bench=BenchmarkX -memprofile=mem.out ./ruta/ # también -mutexprofile, -blockprofile
go test -trace=trace.out -run TestX ./ruta/ && go tool trace trace.out
```

En producción, compara percentiles (p50/p95/p99) en el APM antes y después; el promedio esconde la cola. Para escape analysis y presión del GC: `go build -gcflags=-m` y `GODEBUG=gctrace=1`; detalle en `references/memory-pointers.md` de `senior-go-idiomatic`.
