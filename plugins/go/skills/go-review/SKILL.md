---
name: go-review
description: "Reglas de revisión específicas de Go para los archivos .go de un diff o un PR (corrección Go, idiomas, layout y DDD de la casa). La carga la skill code-review para su revisor de Go; úsala también cuando el usuario pida revisar solo código Go."
license: MIT
---

# Revisión Go

Responde en español y conserva en inglés los términos técnicos habituales.

Reglas para el revisor de Go. Se aplican **solo a los archivos `.go`** y **encima** de la rúbrica transversal de `code-review`: no repitas lo transversal (seguridad, tests, compatibilidad, tamaño) salvo cuando el problema sea un mecanismo propio de Go. Cada hallazgo lleva severidad (blocker / major / minor / nit), `ruta:línea`, por qué y un arreglo concreto.

`<SHA>` es el commit revisado: `HEAD` en un diff local, o el `headRefOid` de un PR (leído tras `git fetch <remote> "pull/<n>/head"`, nunca del working tree).

## Quién es dueño de cada regla

Cada regla tiene una skill dueña en este plugin; esta skill solo apunta a ellas. Para la regla completa y su razonamiento, invoca la dueña.

| Área | Dueña |
|---|---|
| Layout de bounded contexts, un caso de uso por archivo, forma del caso de uso, ports, ubicación de infraestructura | `ddd-go-idiomatic` |
| Principios de diseño: Ley de Demeter, Tell-Don't-Ask, CQS, tipos con nombre, estados ilegales, dependencias explícitas | `go-design-rules` |
| Política de comentarios, idiomas, errores, concurrencia, I/O, testing, tooling | `senior-go-idiomatic` |

Si un principio de DDD u OOP choca con los idiomas de Go, ganan los idiomas de Go: una interface por struct, un paquete `mapper/`, getters/setters o carpetas por capa son hallazgos aunque "sigan DDD".

## Paso 1: ¿el repo adopta las reglas de la casa?

Las reglas de layout y de comentarios son convenciones de un equipo, no Go universal. Comprueba la adopción en `<SHA>`:

```bash
git cat-file -e "<SHA>:.claude/skills/ddd-go-idiomatic/SKILL.md" 2>/dev/null && echo adoptado
for f in AGENTS.md CLAUDE.md .claude/CLAUDE.md; do
  git show "<SHA>:$f" 2>/dev/null | grep -Eiq 'ddd-go-idiomatic|one use case per file|un caso de uso por archivo' && echo "adoptado vía $f"
done
```

(Sin clon local, lee las mismas rutas con `gh api "repos/<owner>/<repo>/contents/<ruta>?ref=<SHA>"`; un 404 significa que no existe.)

- **Adoptadas** → las violaciones de layout son **major** y las de la política de comentarios **minor**, citando la skill dueña.
- **No adoptadas** → repórtalas como **minor** o **nit** "sugerencias de estilo de la casa", agrupadas, y nunca dejes que motiven un veredicto de pedir cambios. Sigue los patrones que el repo ya usa en vez de imponer nuevos.

## Paso 2: detección rápida

```bash
files=$(git diff --name-only <base>...<SHA> | grep '\.go$')   # en un PR: gh pr diff <n> --name-only | grep '\.go$'
# nombres de archivo cajón de sastre
printf '%s\n' "$files" | grep -E '(^|/)(service|services|usecase|usecases|use_cases|application|app|manager|helpers|utils|common)\.go$'
# tipos cajón de sastre añadidos
git diff <base>...<SHA> -- $files | grep -E '^\+type ([A-Za-z]*(Service|UseCase|Manager)) struct'
# varios métodos exportados con ctx en un mismo receptor (¿más de un caso de uso por archivo?)
for f in $(printf '%s\n' "$files" | grep -v '_test\.go$'); do
  c=$(git show "<SHA>:$f" 2>/dev/null | grep -cE '^func \([a-z]+ \*?[A-Z][A-Za-z0-9_]*\) [A-Z][A-Za-z0-9_]*\(ctx context\.Context')
  [ "${c:-0}" -gt 1 ] && echo "$f: $c métodos exportados con ctx"
done
# banners de comentarios añadidos
git diff <base>...<SHA> -- $files | grep -nE '^\+[[:space:]]*// ?[-=]{4,}'
```

Cada coincidencia es una candidata: confírmala leyendo el archivo. Los adapters (stores, repositorios) implementan legítimamente varios métodos de un port; un composition root (`cmd/<app>/main.go`, `internal/handlers/handlers.go`) cablea legítimamente muchas rutas.

## Paso 3: corrección Go (cualquier repo)

Bugs generales de Go, con severidad según su impacto (dueña: `senior-go-idiomatic`):

- **Errores**: tragados (`_ = f()`), comparados con `==` en vez de `errors.Is/As`, o devueltos sin contexto en una frontera de paquete (envuelve con `fmt.Errorf("operación: %w", err)`). Un nil tipado devuelto como `error`.
- **`context.Context`**: no es el primer parámetro o no se propaga en llamadas con I/O; guardado en un struct; `context.Background()` a mitad de una cadena.
- **Goroutines**: sin un final claro (sin `ctx.Done()`, canal de cierre, `WaitGroup` o `errgroup`); `time.After` dentro de bucles.
- **Concurrencia**: data races, escrituras concurrentes en mapas, un `sync.Mutex` copiado por valor.
- **Slices y bucles**: `append` que comparte el backing array; mutar la copia de `range` en vez de `xs[i]`.
- **Interfaces**: declaradas junto a su única implementación sin seam real, o anchas cuando el consumidor usa uno o dos métodos (muévelas al consumidor y recórtalas).
- **Estado global**: estado mutable a nivel de paquete, `init()` con efectos laterales, singletons ocultos.
- **`panic`** como control de flujo fuera de `main` o de la inicialización.
- **Paquetes** `util`, `common`, `helpers`: cada función va al paquete del concepto que sirve.

## Paso 4: modelado de dominio (si el cambio toca un paquete de dominio)

Dueña: `ddd-go-idiomatic`. Busca value objects que se pueden construir sin validación, entidades con setters en vez de métodos que revelan intención, agregados referenciados por puntero en vez de por ID, paquetes de dominio que importan `database/sql`, `net/http` o `encoding/json`, y errores del driver (`sql.ErrNoRows`) que se escapan del repositorio. Severidad según impacto; un import de infraestructura filtrado en un repo que adoptó las reglas de la casa es major.

## Lo que no se reporta

Lo que garantizan `gofmt`, `go vet` y el `golangci-lint` configurado en el repo.
