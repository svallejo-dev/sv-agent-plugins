# Catálogo de simplificaciones de criterio

Cada entrada tiene un antes, un después y su **límite**: cuándo no aplicarla. Si la skill `senior-go-idiomatic` está disponible, ella es la dueña de los criterios de estilo; este catálogo es la versión operativa para simplificar.

## 1. Comentarios

Un nombre bien elegido ya dice **qué** hace el código; el comentario explica **por qué**.

```go
// Antes
// ---------- Helpers ----------

// getUser gets the user
func getUser(id string) (*User, error) {
	// call the repository
	u, err := repo.Find(id)
	// if err != nil { log.Println(err) }
	return u, err
}

// Después
func getUser(id string) (*User, error) {
	return repo.Find(id)
}
```

- Se van: banners, narración (`// call the repository`), código comentado, comentarios que repiten el nombre.
- Los identificadores **exportados** conservan su doc comment, de una línea, empezando por el nombre: `// FindActive devuelve…`.
- Se quedan: el **porqué** (restricción externa, workaround con enlace al issue, invariante no obvio), `//go:` y `//nolint` con motivo, y los `TODO` con dueño o issue.

**Límite:** si no sabes si un comentario explica un porqué real, déjalo y pregúntalo en el informe.

## 2. Ruido local

```go
// Antes
func esMayor(edad int) bool {
	resultado := false
	if edad >= 18 {
		resultado = true
	} else {
		resultado = false
	}
	return resultado
}

// Después
func esMayor(edad int) bool {
	return edad >= 18
}
```

```go
// Antes
if err != nil {
	return err
} else {
	procesar(x)
}

// Después
if err != nil {
	return err
}
procesar(x)
```

- Variables que se usan una vez y no aportan un nombre útil, asignaciones que se pisan, conversiones a un tipo que ya tiene el valor.

**Límite:** una variable intermedia con buen nombre que explica un cálculo **sí** aporta: no la inlinees. Que sea más corto no basta; tiene que leerse mejor.

## 3. Anidamiento

```go
// Antes
func Procesar(p *Pedido) error {
	if p != nil {
		if p.Valido() {
			if len(p.Items) > 0 {
				return guardar(p)
			}
			return ErrSinItems
		}
		return ErrInvalido
	}
	return ErrNil
}

// Después
func Procesar(p *Pedido) error {
	if p == nil {
		return ErrNil
	}
	if !p.Valido() {
		return ErrInvalido
	}
	if len(p.Items) == 0 {
		return ErrSinItems
	}
	return guardar(p)
}
```

- Guard clauses: el camino feliz queda a la izquierda, sin indentar.
- Cadenas de `if x == a … else if x == b` sobre el mismo valor pasan a `switch`.

**Límite:** al invertir condiciones, cuidado con `NaN`, punteros nil dentro de la condición y evaluación en cortocircuito con efectos. Los tests deben cubrir cada rama; si no, deja el anidamiento.

## 4. Errores

```go
// Antes
u, err := repo.Find(ctx, id)
if err != nil {
	log.Printf("error buscando usuario: %v", err)
	return nil, errors.New(fmt.Sprintf("find user: %v", err))
}

// Después
u, err := repo.Find(ctx, id)
if err != nil {
	return nil, fmt.Errorf("buscar usuario %s: %w", id, err)
}
```

- Se envuelve con `%w` (para que `errors.Is` y `errors.As` sigan funcionando) y contexto una vez por capa.
- Sin "log and return": o se maneja (y se registra) o se devuelve, no las dos cosas.

**Límite:** **no cambies el texto** de un error que otros pueden comparar (errores centinela, mensajes que llegan a clientes de la API) ni pases de `%v` a `%w` en una frontera donde exponer el error interno sea un problema. Es un cambio de comportamiento: proponlo, no lo hagas.

## 5. Código muerto no exportado

- Funciones, tipos, constantes y campos no exportados sin uso; parámetros que ninguna implementación usa en funciones no exportadas.
- Confírmalo con herramientas: el compilador para imports y variables, `staticcheck -checks U1000` para lo no usado, y búsqueda de usos por reflexión, templates o `//go:linkname`.

**Límite:** nada exportado (puede usarlo otro módulo) ni nada referenciado por nombre desde fuera del código Go (configuración, reflexión, generadores).

## 6. Duplicación local

```go
// Antes: el mismo bloque en tres handlers
if r.Header.Get("X-Tenant") == "" {
	http.Error(w, "falta tenant", http.StatusBadRequest)
	return
}

// Después
tenant, ok := tenantDe(w, r)
if !ok {
	return
}
```

- Se extrae a una función no exportada del **mismo paquete** cuando la lógica es la misma y cambia por las mismas razones.

**Límite:** dos bloques que se parecen pero cambian por razones distintas no son duplicación (es acoplamiento accidental). Ante la duda, regla de tres: hasta la tercera repetición no se extrae.

## Lo que ya hacen las herramientas (no lo hagas a mano)

`gofmt -s`, `goimports` y los modernizadores de `go fix` cubren: `interface{}` → `any`, bucles de búsqueda → `slices.Contains`/`slices.Index`, cálculos de mínimo y máximo → `min`/`max`, `for i := 0; i < n; i++` → `for i := range n`, copias de mapas → `maps.Copy`, helpers de puntero → `new(expr)`, `errors.As` con variable → `errors.AsType`, y más. Ejecuta la herramienta en vez de reescribirlo: el resultado es determinista y respeta la versión de Go del módulo.
