---
name: code-review
description: "Revisa cambios de código en cualquier lenguaje, sea un diff local desde un punto fijo (commit, rama, tag) o un pull request de GitHub (número, URL o rama), con revisores en paralelo (Transversal, uno por lenguaje vía los plugins de lenguaje, y Spec) y hallazgos con severidad. Publica en GitHub solo si se pide y nunca aprueba. Triggers: \"code review\", \"revisa desde main\", \"revisa esta rama\", \"revisa este PR\", \"review PR #123\", \"revisión de PR\"."
license: MIT
---

# Code review

Responde en español y conserva en inglés los términos técnicos habituales. Si el PR está escrito en otro idioma, escribe la revisión en ese idioma.

Revisa un cambio con tres tipos de revisor que corren como **sub-agentes en paralelo**, cada uno con contexto limpio, para que no se contaminen:

- **Transversal**: lo que vale en cualquier lenguaje (corrección, seguridad, tests, errores, compatibilidad, rendimiento, tamaño, migraciones, observabilidad, smells de diseño). Reglas en [TRANSVERSAL.md](TRANSVERSAL.md).
- **Lenguaje**: uno por cada lenguaje del cambio que tenga plugin instalado. Idiomas, trampas y convenciones propias de ese lenguaje.
- **Spec**: ¿el código hace lo que pedía la spec, el ticket o el issue?

Analogía: es la inspección de un edificio. El inspector general revisa estructura y salidas de emergencia en cualquier obra; el gasista solo entra si hay gas; y el cliente comprueba si es la casa que encargó. Si los juntas en una sola voz, el hallazgo más ruidoso tapa a los demás.

## 1. Fija la unidad de revisión

- **Diff local**: el usuario da un punto fijo (SHA, rama, tag, `main`, `HEAD~5`). Si no lo dio, pregúntalo. Captura una vez `git diff <punto-fijo>...HEAD` (tres puntos, contra el merge-base) y `git log <punto-fijo>..HEAD --oneline`. Confirma que el punto resuelve (`git rev-parse <punto-fijo>`) y que el diff no está vacío: una referencia mala debe fallar aquí, no dentro de los sub-agentes. El commit revisado es `HEAD`.
- **Pull request**: el usuario da número, URL o rama. Sigue [PR-GITHUB.md](PR-GITHUB.md) § Obtener el PR. El commit revisado es el `headRefOid` del PR; nunca leas archivos del working tree local.

## 2. Intención, alcance y tamaño

Antes de juzgar código, fija:

- **Intención**: qué problema resuelve (título, descripción, ticket o issue enlazado, mensajes de commit). Código correcto que no cumple la intención sigue estando mal.
- **Alcance**: módulos y consumidores tocados; cualquier cambio de contrato público.
- **Tamaño**: si es demasiado grande para revisarlo con rigor o mezcla asuntos (refactor + feature + fix + formateo masivo), pedir que se divida es el hallazgo más valioso y va primero, con los cortes propuestos. Una revisión superficial de un cambio enorme es peor que pedir dividirlo.

## 3. Identifica la spec

Busca la spec de origen en este orden:

1. La descripción del PR y el issue o ticket que enlaza.
2. Referencias en los commits (`#123`, `TBRFRE-1758`, rutas de tickets), resolviéndolas según `docs/agentes/tracker.md` si existe.
3. Una ruta que el usuario pasó como argumento.
4. Un `spec.md` o ticket en `.scratch/` (o la ruta configurada), `docs/` o `specs/` que coincida con la rama o la feature.

Si no hay nada, pregunta. Si el usuario confirma que no hay spec, el revisor de Spec se salta y el informe lo dice.

## 4. Identifica los estándares del repo

Busca todos los archivos que documentan cómo se escribe el código: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`, ADRs y configuración de linters. Sepáralos en dos grupos: los que valen para todo el repo (van al revisor Transversal) y los de un lenguaje concreto, como `.golangci.yml` o `.eslintrc` (van al revisor de ese lenguaje).

**Precedencia**: estándar documentado del repo > reglas del plugin de lenguaje > [TRANSVERSAL.md](TRANSVERSAL.md). Lo que ya garantiza el tooling (formatters, linters configurados, CI) no se reporta.

## 5. Detecta los lenguajes y carga sus reglas

Lista los archivos cambiados y agrúpalos por lenguaje según la extensión: `.go` → `go`, `.php` → `php`, `.ts`/`.tsx`/`.js` → `typescript`, `.py` → `python`, `.sql` → `sql`, `.java` → `java`, `.kt` → `kotlin`.

Para cada lenguaje, comprueba si entre tus skills disponibles existe `<lenguaje>-review`:

- **Existe**: cárgala ahora (en Claude Code, con la herramienta Skill; en otras herramientas, mencionándola por su nombre o leyendo su SKILL.md). Su contenido son las reglas que pegarás en el prompt del revisor de ese lenguaje (el sub-agente no puede cargarlas por sí mismo). Si esa skill apunta a otras skills del mismo plugin para profundizar, cárgalas también y resume lo pertinente.
- **No existe**: no hay revisor de ese lenguaje. Anótalo para el informe ("sin revisor idiomático para `.py`; solo revisión transversal") y no improvises reglas idiomáticas.

Los archivos sin lenguaje de programación (YAML, Markdown, JSON, Dockerfile) solo pasan por el revisor Transversal.

## 6. Lanza los revisores en paralelo

Lanza todas las llamadas juntas, en primer plano, y agrega lo que devuelvan. Cada sub-agente recibe cómo obtener el diff, la lista de commits, el commit revisado y, para un PR, cómo leer archivos en ese commit (ver [PR-GITHUB.md](PR-GITHUB.md)).

**Transversal**: el diff completo, los estándares del repo que valen para todo, y el contenido completo de [TRANSVERSAL.md](TRANSVERSAL.md) pegado tal cual. Encargo: "Recorre cada archivo cambiado con las dimensiones de la rúbrica y los smells de diseño. No reportes idiomas de un lenguaje concreto; eso lo cubre otro revisor. Cada hallazgo: severidad, `ruta:línea`, por qué es un problema y un arreglo concreto. Un estándar documentado del repo prevalece sobre la rúbrica. Menos de 500 palabras."

**Un revisor por lenguaje con reglas**: solo los archivos de ese lenguaje, las reglas cargadas en el paso 5 y los estándares del repo de ese lenguaje. Encargo: "Revisa solo los archivos `<extensiones>` con estas reglas de `<lenguaje>`. No repitas lo transversal (seguridad, tests, compatibilidad, tamaño) salvo cuando el problema sea un mecanismo propio del lenguaje. Cada hallazgo: severidad, `ruta:línea`, por qué y arreglo concreto. Menos de 400 palabras."

**Spec**: el diff y la spec (ruta o contenido). Encargo: "Informa: (a) requisitos que la spec pedía y faltan o están a medias; (b) comportamiento que nadie pidió (scope creep); (c) requisitos que parecen implementados pero cuya implementación parece incorrecta. Cita la línea de la spec en cada hallazgo y dale severidad. Menos de 400 palabras."

Si no hay spec, sáltate ese sub-agente.

> **Portabilidad:** si tu herramienta no tiene sub-agentes, ejecuta cada encargo en una conversación nueva con solo su brief, o en secuencia en esta sesión, y declara en el resultado que no hubo aislamiento de contexto.

## 7. Agrega

Usa el formato de salida de [TRANSVERSAL.md](TRANSVERSAL.md) § Formato de salida, con una sección por revisor (`### Transversal`, `### Go`, `### Spec`…). Dentro de cada sección ordena de más a menos severo. **No** mezcles ni reordenes entre secciones: están separadas a propósito para que una no tape a otra.

Si dos revisores marcan la misma línea por la misma causa, conserva el hallazgo en la sección del lenguaje y menciónalo en una línea en la otra.

El **veredicto** es global: algún blocker o major en cualquier sección → pedir cambios; solo minor o nit → comentar; nada → "parece listo", y la aprobación queda en manos de una persona. Añade una línea con el conteo por sección y severidad, y una o dos cosas que el cambio hace bien.

Si la unidad era un PR, ofrece publicar la revisión.

## 8. Publica en GitHub (solo si se pide)

Solo cuando el usuario pida explícitamente publicar, postear o comentar en el PR. Sigue [PR-GITHUB.md](PR-GITHUB.md) § Publicar.

## Guardarraíles

- **Nunca apruebes** un PR (`--approve`, `event: APPROVE`), aunque te lo pidan: la aprobación es una firma humana; dile al usuario que apruebe en GitHub.
- **Nunca reproduzcas un secreto** encontrado en el diff: describe el patrón y la ubicación y márcalo blocker.
- **Solo revisión**: sin push, merge, cierre, labels ni edición del PR, y sin checkout en el working tree del usuario.
