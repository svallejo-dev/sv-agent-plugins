# Cuándo usar dobles de test (Go)

Usa dobles solo en las **fronteras del sistema**:

- APIs externas (pasarelas de pago, partners, proveedores de auth)
- Bases de datos (a veces; prefiere una base real de test)
- Tiempo y aleatoriedad
- Sistema de archivos (a veces; `fstest.MapFS` o `t.TempDir()` suelen bastar)

No uses dobles para:

- Tus propios tipos o paquetes
- Colaboradores internos
- Nada que controles

Analogía: un doble es un actor de reparto que sustituye a alguien que no puedes traer al set (el banco, el partner). A tus propios actores los dejas actuar.

## Preferencias en Go

1. **Base real antes que doble.** Para Postgres o MySQL, usa una base de test (contenedor con `testcontainers-go` o una instancia de CI). Para Redis o Kafka, igual. Un doble de base de datos testea tu suposición sobre la base, no la base.
2. **Fakes escritos a mano antes que mocks generados.** Un fake en memoria que implementa la interfaz (un `map` protegido con `sync.Mutex`) da tests que leen como el uso real. Los mocks generados (`gomock`, `mockery`) solo para APIs externas difíciles de simular, y aun así asertando resultados, no llamadas.
3. **`httptest.Server` para APIs HTTP externas.** Levanta un servidor que responde como el partner y apunta el cliente a su URL. Testeas el cliente HTTP real, el parseo y los errores.

## Diseñar para poder sustituir

En las fronteras, diseña interfaces fáciles de sustituir:

**1. Inyecta dependencias**

Pasa las dependencias externas en vez de crearlas dentro:

```go
// Fácil de sustituir
func ProcesarPago(ctx context.Context, o Orden, cobros Cobrador) error {
	return cobros.Cobrar(ctx, o.Total)
}

// Difícil de sustituir
func ProcesarPago(ctx context.Context, o Orden) error {
	client := gestorpagos.NewClient(os.Getenv("GESTOR_PAGOS_KEY"))
	return client.Cobrar(ctx, o.Total)
}
```

**2. Interfaces pequeñas definidas por el consumidor**

"Accept interfaces, return structs." Define la interfaz en el paquete que la usa, con solo los métodos que necesita, no en el paquete que la implementa:

```go
// En el paquete suscripciones, no en el cliente del gestor de pagos
type Cobrador interface {
	Cobrar(ctx context.Context, monto Money) (CobroID, error)
}
```

**3. Métodos específicos antes que un fetcher genérico**

Crea un método por operación externa en vez de uno genérico con lógica condicional:

```go
// BIEN: cada método se sustituye por separado
type PartnerClient interface {
	ObtenerUsuario(ctx context.Context, id string) (Usuario, error)
	ListarSuscripciones(ctx context.Context, userID string) ([]Suscripcion, error)
	CrearSuscripcion(ctx context.Context, s NuevaSuscripcion) (Suscripcion, error)
}

// MAL: el doble necesita lógica condicional dentro
type PartnerClient interface {
	Do(ctx context.Context, method, path string, body any) ([]byte, error)
}
```

Con métodos específicos:
- Cada doble devuelve una forma concreta
- No hay lógica condicional en el setup del test
- Se ve qué operaciones usa cada test
- Hay tipado por operación

**4. El tiempo también se inyecta**

```go
type Reloj func() time.Time

func NuevoServicio(repo Repo, ahora Reloj) *Servicio { ... }

// En producción: NuevoServicio(repo, time.Now)
// En el test:   NuevoServicio(repo, func() time.Time { return fechaFija })
```
