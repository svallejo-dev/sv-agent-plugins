---
name: go-simplify
description: "Simplifica código Go sin cambiar su comportamiento: quita ruido, comentarios que narran, código muerto, anidamiento y modismos viejos, primero con herramientas deterministas (gofmt -s, goimports, go fix con los modernizadores de Go 1.26, staticcheck S1) y después con un catálogo de simplificaciones de criterio, con tests en verde antes y después de cada paso. Úsala cuando el usuario pida simplificar, limpiar, pulir, modernizar o quitar ruido de código Go, \"/simplify\" en Go, o \"déjalo más idiomático sin cambiar lo que hace\"."
license: MIT
---

# Simplificar Go

Responde en español y conserva en inglés los términos técnicos habituales.

Simplificar es **quitar sin cambiar lo que el código hace**. El resultado se lee más rápido, tiene menos ramas y menos ruido, y se comporta exactamente igual: mismas salidas, mismos errores, misma API, mismos efectos y en el mismo orden.

**Analogía:** un corrector de estilo, no un coautor. Corta la palabra que sobra, junta la frase partida en tres y quita la nota al pie que repite el texto, pero no cambia el argumento del libro. Si para mejorar hay que cambiar el argumento, eso es otro trabajo (`codebase-design` o un ticket), no una simplificación.

## Reglas que no se negocian

1. **Comportamiento idéntico.** No cambia la API exportada (nombres, firmas, tipos, tags de struct), ni el texto de los errores (alguien puede compararlos), ni los nombres de logs y métricas, ni el orden de los efectos, ni la semántica de concurrencia.
2. **Red antes de cortar.** Sin build, `go vet` y tests en verde antes de empezar, no se simplifica nada. Sin tests que cubran el código tocado, solo se aplican los cambios que las herramientas garantizan (capa mecánica).
3. **Cambios pequeños y verificados.** Una categoría a la vez, tests después de cada una. Si algo se pone rojo, se revierte esa categoría; no se "arregla" el test.
4. **No se toca:** código generado (`// Code generated ... DO NOT EDIT.`), `vendor/`, `testdata/`, y, si el repo usa el plugin `qa`, la carpeta de aceptación sellada.
5. **Simplificar no es quitar defensas.** Una validación, un manejo de error o un timeout que parece redundante se pregunta antes de borrarlo.

Los criterios de estilo (comentarios, nombres, errores, idiomas) son de `senior-go-idiomatic`: esta skill los aplica, no los redefine. Si está disponible, cárgala; si no, usa el catálogo de [references/catalogo.md](references/catalogo.md).

## 1. Alcance

- **Por defecto, lo que cambió**: los `.go` del diff contra la rama base, más lo no commiteado.
  ```bash
  git diff --name-only "$(git merge-base HEAD origin/main)" -- '*.go'; git diff --name-only -- '*.go'
  ```
- **Si el usuario nombra archivos o paquetes**, esos.
- **Todo el repositorio solo si lo pide explícitamente.** Un diff de simplificación enorme no se puede revisar, y lo que no se revisa no es seguro.

Filtra los archivos generados: `grep -L '^// Code generated .* DO NOT EDIT\.$'`. Anota los paquetes afectados: son los que se compilan y prueban en cada paso.

## 2. Línea base

```bash
go build ./... && go vet <paquetes> && go test -count=1 <paquetes>
```

Añade `-race` si el código tocado usa goroutines o estado compartido. Guarda el resultado (paquetes y número de tests): es la línea base contra la que se compara al final.

- Si algo está rojo, **para**: reporta qué falla y no simplifiques hasta que el usuario decida.
- Si un archivo del alcance no tiene tests que ejerciten sus funciones (`go test -cover` lo indica por paquete), márcalo **"sin red"**: en él solo entra la capa mecánica.

## 3. Capa mecánica (determinista)

Herramientas que garantizan cambios seguros. Aplícalas en este orden, con tests después de cada una:

| Paso | Comando | Qué hace |
|---|---|---|
| a | `gofmt -s -w <archivos>` | Formato y simplificaciones sintácticas (literales compuestos, rangos, slices) |
| b | `goimports -w <archivos>` (si está instalado) | Ordena y depura imports |
| c | `go fix -diff <paquetes>` y luego `go fix <paquetes>` | Los modernizadores de Go 1.26: `any`, `min`/`max`, `slices`/`maps`, rangos sobre enteros, `new(expr)`, `errors.AsType` y más. Solo propone lo que permite la versión de `go.mod`. Repite hasta que no haya cambios: un arreglo habilita otro |
| d | `staticcheck -checks 'S1*' <paquetes>` (si está instalado) | Simplificaciones de la familia S1: devolver directamente una expresión booleana, `fmt.Errorf` en vez de `errors.New(fmt.Sprintf(...))`, `append` en vez de bucles de copia… Aplícalas a mano |
| e | `golangci-lint run <paquetes>` (si el repo tiene configuración) | Lo que el equipo ya decidió exigir |

Si `go fix` propone algo que cambia el comportamiento en tu caso (por ejemplo, en un archivo con build tags), desactiva ese analizador concreto (`go fix -<analizador>=false`) y dilo en el informe.

## 4. Capa de criterio

Solo en archivos con red de tests. Recorre el catálogo por categorías, en este orden (de menor a mayor riesgo), con tests después de cada una:

1. **Comentarios**: narración, banners, código comentado, comentarios que repiten el nombre; docs de exportados que no empiezan con el identificador.
2. **Ruido local**: variables usadas una sola vez sin aportar nombre, asignaciones redundantes, conversiones innecesarias, `else` después de `return`.
3. **Anidamiento**: guard clauses y early return, condiciones fusionadas, `switch` en vez de cadenas de `if`.
4. **Errores**: contexto con `%w` una sola vez por capa, sin "log and return", sin envolver dos veces el mismo mensaje.
5. **Código muerto no exportado**: funciones, tipos, constantes y parámetros sin uso (confírmalo con el compilador o `staticcheck -checks U1000`, no a ojo).
6. **Duplicación local**: la misma lógica repetida dentro del alcance, extraída a una función no exportada en el mismo paquete.

Ejemplos de antes y después, y los límites de cada categoría, en [references/catalogo.md](references/catalogo.md).

**Fuera de alcance** (proponlo, no lo hagas): cambiar la API exportada, mover código entre paquetes, introducir o quitar interfaces exportadas, cambios por rendimiento sin benchmark, refactors de diseño. Eso va a `codebase-design` o a un ticket.

## 5. Verificación final

```bash
gofmt -l <archivos>            # debe salir vacío
go build ./... && go vet <paquetes> && go test -count=1 <paquetes>   # igual que la línea base
```

El número de tests debe ser el mismo que en la línea base: si bajó, algo se borró. Si existe la skill `go-review`, pásale el diff para una revisión independiente; si no, relee el diff completo buscando cambios de comportamiento.

## 6. Informe

- Línea base y verificación final (paquetes, tests, `-race` sí o no).
- Cambios por capa y por categoría, con `archivo:línea` de los relevantes.
- **Lo que no se tocó y por qué**: archivos sin red, propuestas fuera de alcance, analizadores desactivados, defensas que parecían redundantes y quedan como pregunta.
- Propuesta de commits: uno para la capa mecánica y uno por categoría de criterio. No hagas commit salvo que el usuario lo pida; si lo pide y existe la skill `git-commit`, úsala.
