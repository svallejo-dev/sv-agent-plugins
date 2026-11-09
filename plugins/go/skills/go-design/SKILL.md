---
name: go-design
description: "Traduce el vocabulario de módulos profundos (módulo, interfaz, seam, adapter, profundidad) a las herramientas de Go (paquetes, internal/, interfaces del consumidor, inyección por constructor). La carga la skill codebase-design cuando el código es Go; úsala también al diseñar la interfaz de un paquete Go."
license: MIT
---

# Diseño en Go

Responde en español y conserva en inglés los términos técnicos habituales.

Complementa a `codebase-design`: allí está el vocabulario y los principios (profundidad como leverage, prueba del borrado, un adapter = seam hipotético); aquí, cómo se expresan en Go. Para profundizar, invoca:

- `go-design-rules`: Ley de Demeter, Tell-Don't-Ask, CQS, tipos con nombre, estados ilegales, dependencias explícitas, DRY/SOLID en Go.
- `ddd-go-idiomatic`: value objects, entidades, agregados, bounded contexts, casos de uso y layout de archivos.
- `senior-go-idiomatic`: interfaces y composición, layout de proyecto (`cmd/`, `internal/`, composition root).

## El vocabulario en Go

| Concepto | En Go |
|---|---|
| **Módulo** | Una función, un tipo con sus métodos, un paquete. El paquete es la unidad natural de profundidad. |
| **Interfaz** (en el sentido amplio) | Lo exportado del paquete más sus invariantes, errores (sentinelas o tipados), requisitos de `context.Context` y de concurrencia. No solo la palabra clave `interface`. |
| **Esconder la implementación** | Identificadores sin exportar; subpaquetes dentro de `internal/`, que el compilador impide importar desde fuera del árbol. |
| **Seam** | Una `interface` pequeña declarada en el paquete **consumidor**, con los métodos que usa. "Accept interfaces, return structs." |
| **Adapter** | Un struct concreto que satisface esa interface: el repositorio Postgres en producción, el fake en memoria en tests. |
| **Inyección de dependencias** | Por constructor (`NewServicio(repo Repo, ahora func() time.Time)`), cableado en el composition root de `cmd/<app>/main.go`. Sin globals ni singletons. |

## Reglas

- **No declares una `interface` junto a su única implementación.** Hasta que haya dos adapters (normalmente producción + test), es indirección; devuelve el struct concreto.
- **Interfaces pequeñas.** Si el consumidor usa dos métodos, la interface tiene dos métodos.
- **Profundidad por paquete.** Una función exportada que hace mucho vale más que diez que reenvían. Si el paquete exporta casi tanto como implementa, es superficial.
- **Prueba del borrado en Go**: si borrar el paquete solo obliga a mover tres líneas a cada llamador, era un pasamanos.
- **Categorías de dependencias** (de `DEEPENING.md` en `codebase-design`): sustituible localmente → contenedor con `testcontainers-go`, `fstest.MapFS` o `t.TempDir()`; remota propia → port como `interface` del consumidor + adapter HTTP/gRPC + adapter en memoria; externa → port + `httptest.Server` o fake.

## Ejemplo

```go
// Paquete consumidor: suscripciones. Declara solo lo que usa.
type Cobrador interface {
	Cobrar(ctx context.Context, monto Money) (CobroID, error)
}

type Servicio struct {
	cobros Cobrador
	ahora  func() time.Time
}

func NewServicio(c Cobrador, ahora func() time.Time) *Servicio {
	return &Servicio{cobros: c, ahora: ahora}
}

// Interfaz profunda: una operación que esconde reglas de renovación, reintentos y eventos.
func (s *Servicio) Renovar(ctx context.Context, id SuscripcionID) error { ... }
```

El cliente del gestor de pagos (otro paquete) devuelve un struct concreto que satisface `Cobrador` sin saber que existe; el test usa un fake en memoria.
