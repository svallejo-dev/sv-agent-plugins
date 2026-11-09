# Mecánica de skills

La rama específica de skills de [writing-for-agents](SKILL.md): lo que cambia cuando el documento es una skill (frontmatter, elección de invocación y skills router). Todo lo demás sobre cómo escribirla es la referencia universal de `SKILL.md`.

## Invocación

Dos opciones, que intercambian las dos cargas:

- Una skill **invocada por el modelo** conserva su `description`, así el agente puede dispararla por su cuenta y otras skills pueden alcanzarla. Puedes seguir escribiendo su nombre: la invocación por el modelo siempre _incluye_ el alcance del usuario; una descripción solo añade descubrimiento por el agente, nunca quita el del humano. La descripción es el puntero de contexto principal de la skill y está forzada a estar siempre cargada: carga de contexto permanente a cambio de descubribilidad. Una skill invocada por el modelo cuyo contenido es todo referencia también sirve como hogar de referencia compartida: otra skill puede invocarla, así la referencia que necesitan varias skills vive en un solo sitio. Mecánica: omite `disable-model-invocation` y escribe una descripción para el modelo con las ramas de disparo (aplican completas las reglas de punteros de `SKILL.md`).
- Una skill **invocada por el usuario** saca la descripción del alcance del agente: solo el humano que escribe su nombre puede invocarla, y ninguna otra skill puede. Cero carga de contexto, pero gasta carga cognitiva: tú eres el índice que debe recordar que existe. Mecánica: pon `disable-model-invocation: true`; la `description` pasa a ser para humanos: un resumen de una línea, sin listas de disparadores.

Elige invocación por el modelo solo cuando el agente deba alcanzar la skill por su cuenta, u otra skill deba hacerlo. Si solo se dispara a mano, hazla invocada por el usuario y no pagues carga de contexto.

La referencia compartida que necesitan dos skills invocadas por el usuario no puede vivir en ninguna de ellas: sin descripción, ninguna puede disparar a la otra. Llévala a un archivo plano fuera del sistema de skills: referencia externa que cualquier skill puede apuntar.

## Plugins y portabilidad

Dentro de un plugin de Claude Code, las skills quedan con espacio de nombres (`ingenieria:tdd`). Las demás herramientas (Codex, Copilot, Cursor, Windsurf) instalan las skills en carpetas planas y las invocan por su nombre a secas. Para que una skill funcione en todas:

- Dale un **nombre único y específico** (`qa-verify`, no `verify`; `go-testing`, no `testing`): en una carpeta plana dos skills con el mismo nombre chocan.
- Cuando una skill invoque a otra, usa el **nombre a secas** (`tdd`, `grilling`), no `plugin:skill`.
- Cumple el estándar Agent Skills en el frontmatter: solo `name` (igual a la carpeta), `description` (entre comillas si contiene `: `), y los opcionales `license`, `compatibility`, `metadata` y `allowed-tools`. Campos propios de una herramienta, como `disable-model-invocation`, hacen que el validador del estándar la rechace.
- Si varias skills comparten referencias o scripts, ponlos en una skill base hermana (`qa-core`) y enlázala con rutas relativas (`../qa-core/...`), no en carpetas del plugin que una instalación de skills sueltas no copia.

## Dividir por invocación

El corte por invocación (el corte por secuencia está en `SKILL.md`): separa una skill invocada por el modelo cuando tengas una palabra guía distinta que deba dispararla por sí sola (una palabra que de verdad usas en tus prompts), u otra skill necesite alcanzarla. Pagas carga de contexto por la nueva descripción siempre cargada, así que ese alcance independiente tiene que valer la pena.

## Skills router

Cuando las skills invocadas por el usuario se multiplican más allá de lo que puedes recordar, esa carga cognitiva acumulada se cura con una **skill router**: una skill invocada por el usuario que nombra a las demás y cuándo recurrir a cada una, para que el humano tenga una sola skill que recordar en vez de muchas. Solo puede sugerir, nunca dispararlas: las skills invocadas por el usuario no tienen descripción, así que nada salvo el humano puede alcanzarlas.
