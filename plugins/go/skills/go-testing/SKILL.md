---
name: go-testing
description: "Idiomas, ejemplos y herramientas de testing en Go (table-driven tests, paquetes _test, fakes, httptest, testcontainers, golden files, -race). La carga la skill tdd cuando el código es Go; úsala también cuando el usuario pregunte cómo testear algo en Go."
license: MIT
---

# Testing en Go

Responde en español y conserva en inglés los términos técnicos habituales.

Complementa a `tdd`: allí están las reglas del ciclo red → green, los seams y los anti-patrones; aquí, cómo se ve eso en Go. Para temas avanzados (TestMain, testcontainers, `testing/synctest`, fuzzing, benchmarks) invoca `senior-go-idiomatic` y lee su `references/testing-advanced.md`.

## Forma de los tests

- Testea desde fuera del paquete cuando sea posible (`package foo_test`), usando solo lo exportado.
- **Table-driven tests** con `t.Run` cuando varios casos comparten el mismo seam; cada caso con un nombre que describe el comportamiento.
- Nombres `TestQué_Contexto_Resultado` (`TestCheckout_ConCarritoValido_Confirma`).
- Valores esperados literales; para structs grandes compara con `cmp.Diff(want, got)` (`github.com/google/go-cmp`); para salidas largas, archivos golden en `testdata/` revisados a mano.
- `t.Fatalf` cuando no tiene sentido seguir (error de setup); `t.Errorf` para seguir reportando.
- `t.Parallel()` en tests independientes; `t.Cleanup` para liberar recursos; `t.TempDir()` para el filesystem.

Ejemplos completos en [tests.md](tests.md).

## Seams típicos en Go

- La API exportada de un paquete.
- Un `http.Handler`, testeado con `httptest.NewRecorder` o `httptest.NewServer`.
- Una interface pequeña definida por el consumidor.

## Dobles de test

Preferencias, en orden: dependencia real (base de datos o cola en contenedor con `testcontainers-go`) → fake escrito a mano en memoria → `httptest.Server` que imita a un tercero → mock generado (`gomock`, `mockery`) solo para APIs externas difíciles, asertando resultados y no llamadas. Inyecta el tiempo como dependencia (`func() time.Time` o un reloj). Detalle y ejemplos en [mocking.md](mocking.md).

## Comandos

```bash
go test ./...                              # todo
go test -run 'TestCheckout/ConCupon' ./internal/checkout/   # un test o subtest
go test -count=1 ./...                     # sin caché de resultados
go test -race ./...                        # detector de data races; siempre que haya goroutines
go test -cover ./...                       # cobertura (orientativa, no un objetivo)
```

En el ciclo red → green, mira fallar el test con `-run <Nombre>` antes de escribir el código, y corre con `-race` cuando el código toque goroutines o estado compartido.
