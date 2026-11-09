---
name: ingenieria-setup
description: "Configura este repo para las skills de ingeniería: dónde viven las specs y tickets locales y dónde vive la documentación de dominio (glosario y ADRs). Ejecútala una vez por repo antes de usar to-spec, to-tickets o code-review. Úsala solo cuando el usuario la pida explícitamente."
license: MIT
---

# Setup

Responde en español y conserva en inglés los términos técnicos habituales.

Deja lista la configuración por repo que asumen las demás skills:

- **Tracker local**: dónde viven specs y tickets (archivos Markdown dentro del repo).
- **Docs de dominio**: dónde viven `GLOSARIO.md` y los ADRs, y las reglas para leerlos.

Es una skill guiada por conversación, no un script determinista. Explora, presenta lo que encontraste, confirma con el usuario y después escribe.

## Proceso

### 1. Explora

Mira el estado actual del repo. Lee lo que exista; no supongas:

- `CLAUDE.md` y `AGENTS.md` en la raíz: ¿existe alguno? ¿Ya tiene una sección `## Skills de agente`?
- `GLOSARIO.md` y `MAPA-GLOSARIO.md` en la raíz, y equivalentes en inglés (`GLOSSARY.md`, `CONTEXT.md`). Si existe uno en inglés, ofrece reutilizarlo tal cual en vez de crear otro.
- `docs/adr/` y cualquier `docs/adr/` dentro de subcarpetas de contexto (`src/*/`, `internal/*/`, `services/*/`).
- `docs/agentes/`: ¿ya existe la salida de una ejecución previa de esta skill?
- `.scratch/`: señal de que la convención de tickets locales ya está en uso. Revisa también `.gitignore` para ver si `.scratch/` está ignorado.
- Señales de monorepo: varios manifiestos de proyecto en subcarpetas (`go.mod`, `package.json`, `composer.json`, `pyproject.toml`), un `go.work` o `pnpm-workspace.yaml`, o carpetas `services/*` con su propio punto de entrada. Si no aparecen, el repo es de un solo contexto, como casi todos.

### 2. Presenta y pregunta

Resume lo que hay y lo que falta. Después recorre las secciones en orden: una sección, una respuesta, la siguiente. Empieza cada sección con la respuesta recomendada para que el usuario pueda aceptarla con una palabra. Salta la sección cuando la exploración ya la resolvió.

**Sección A: Ubicación de specs y tickets.** Recomienda `.scratch/` en la raíz. Acepta otra ruta si el usuario la prefiere (por ejemplo `docs/tickets/`).

**Sección B: ¿Se versionan los tickets?** Pregunta una sola vez:

> ¿Quieres commitear las specs y tickets en git? (recomendado: **sí**, así viajan con el código y sirven de historia)

Si dice que no, añade la carpeta a `.gitignore`.

**Sección C: Docs de dominio.** Por defecto, **un contexto** (`GLOSARIO.md` + `docs/adr/` en la raíz); escríbelo sin preguntar. Ofrece **varios contextos** (un `MAPA-GLOSARIO.md` que apunta a un `GLOSARIO.md` por contexto) solo si la exploración encontró señales de monorepo, y confirma el layout.

### 3. Confirma

Muestra un borrador de:

- El bloque `## Skills de agente` que añadirás a `CLAUDE.md` o `AGENTS.md` (ver paso 4).
- El contenido de `docs/agentes/tracker.md` y `docs/agentes/dominio.md`.

Deja que el usuario lo edite antes de escribir.

### 4. Escribe

**Elige el archivo a editar:**

- Si existe `CLAUDE.md`, edítalo.
- Si no, y existe `AGENTS.md`, edítalo.
- Si no existe ninguno, pregunta cuál crear; no elijas por el usuario.

Nunca crees `AGENTS.md` si ya existe `CLAUDE.md` (ni al revés). Si ya hay un bloque `## Skills de agente`, actualízalo en su sitio en vez de duplicarlo, sin tocar las demás secciones.

El bloque:

```markdown
## Skills de agente

### Tracker

Specs y tickets como archivos Markdown en `<ruta>`. Ver `docs/agentes/tracker.md`.

### Docs de dominio

<"Un contexto" o "Varios contextos">. Ver `docs/agentes/dominio.md`.
```

Después escribe los docs usando como semilla las plantillas de esta carpeta, sustituyendo la ruta elegida:

- [TRACKER-LOCAL.md](./TRACKER-LOCAL.md) → `docs/agentes/tracker.md`
- [DOMINIO.md](./DOMINIO.md) → `docs/agentes/dominio.md`

### 5. Listo

Dile al usuario que la configuración está completa y qué skills leerán estos archivos (`to-spec`, `to-tickets`, `code-review`, `domain-modeling`, `tdd`, `diagnosing-bugs`). Si el repo usa un lenguaje con plugin en el marketplace `sv-agent-plugins` (por ejemplo `go`) y no está instalado, recomiéndalo en una línea. Recuérdale que puede editar `docs/agentes/*.md` a mano; solo hace falta volver a ejecutar esta skill para empezar de cero.
