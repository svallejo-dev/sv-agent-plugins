---
name: por-donde-empiezo
description: "Enrutador de los plugins de sv-agent-plugins: dice qué skill o flujo encaja con la situación (idea nueva, bug, diseño de sistema, integración con un tercero, QA, PR, aprender algo) y qué hacer al terminar una fase. Úsala cuando el usuario no sepa por dónde empezar, pregunte \"¿qué skill uso?\", \"¿cuál es el flujo?\" o pida dejar en su repo un AGENTS.md con las reglas de estos plugins."
license: MIT
---

# ¿Por dónde empiezo?

Responde en español y conserva en inglés los términos técnicos habituales.

Nadie recuerda todas las skills, así que pregunta aquí. Esta skill es un mapa: dice qué camino tomar, no hace el trabajo.

**Analogía:** el mapa de una estación de metro. No te lleva; te dice qué línea tomar, dónde transbordar y en qué estación bajarte.

**Antes de afirmar qué hace una skill o recomendar saltarse un paso, lee su `SKILL.md`**: los resúmenes de esta página son para orientarse, no la fuente de verdad. Recomienda solo skills que estén instaladas; si una no lo está, di qué plugin la trae (`general`, `ingenieria`, `qa`, `arquitectura`, `go`).

## 1. Ubica la situación

Si la situación no está clara, haz una o dos preguntas: ¿hay un repositorio?, ¿es algo nuevo, algo roto o algo que mejorar?, ¿hay un tercero o dinero de por medio?

| Situación | Empieza con | Sigue con |
|---|---|---|
| Idea o feature nueva, dentro de un repo | `grill-with-docs` | El flujo principal (sección 2) |
| Idea, plan o documento sin repo | `grilling` | `to-spec` si se va a construir |
| Diseñar o cambiar un sistema (escala, persistencia, resiliencia, migración) | `system-design` | `capacity-estimation`, `design-stress-test`, `strategic-design`; luego `to-spec` |
| Diseño exploratorio sin métricas | `system-design` en modo exploratorio | `business-archetypes` para partir del tipo de negocio que lo consume |
| Construir un PoC | `system-design` en modo PoC | Construir hipótesis por hipótesis desde el plan del experimento, sin `to-spec` ni `to-tickets` (sección 2) |
| Integrar con un tercero (pagos, partner, SDK) | `to-spec` con la sección de consumidores | `qa-test-design` (checklist de terceros) y walking skeleton como primer ticket |
| Algo está roto o falla a ratos | `diagnosing-bugs` | Si viene de QA, con el comando de reproducción del hallazgo `H-NN` |
| Revisar un cambio o un PR | `code-review` | Nunca aprueba: entrega hallazgos |
| Código Go sucio, ruidoso o anticuado | `go-simplify` | `go-review` para revisar el resultado |
| Diseñar la forma de un módulo o una interfaz | `codebase-design` | `go-design` si es Go |
| El lenguaje del dominio es confuso, o hay que registrar una decisión | `domain-modeling` | ADR en `docs/adr/` |
| ¿Los tests sirven de algo? | `qa-test-the-tests` | `qa-verify` |
| ¿Qué herramienta de pruebas uso? | `qa-toolbox` | `qa-test-automation` |
| Investigar un tema con fuentes primarias | `research` | Llevar el resultado a `grill-with-docs` |
| Aprender un concepto en varias sesiones | `teach` | — |
| Cambiar de herramienta, de directorio o pasar el trabajo a otra persona | `handoff` | — |
| Escribir o mejorar una skill, un prompt o un AGENTS.md | `writing-for-agents` | — |

**Precondiciones**, una vez por repo: `ingenieria-setup` (tracker, glosario, ADRs) y, si hay QA, `qa-setup`.

## 2. El flujo principal: de la idea a la entrega

1. **Afilar la idea**: `grill-with-docs`. Si la idea es un sistema, pasa antes por `system-design`.
2. **Especificar**: `to-spec`. Si hay QA, también escribe el contrato de handoff.
3. **QA, antes de implementar** (recomendado si hay terceros, dinero o datos de clientes):
   `qa-acceptance-criteria` → `qa-test-design` → `qa-test-automation`. El agente que implementa nunca escribe ni edita estos tests.
4. **Partir en tickets**: `to-tickets`. Si hay un tercero o un consumidor externo nuevo, el primer ticket es el walking skeleton.
5. **Por cada ticket**: `tdd` como lazo interno (con `go-testing` si es Go) y `codebase-design` si hay que diseñar un módulo. Al cerrar el ticket: `qa-verify` por rebanada.
6. **Antes del PR**: `go-simplify` (si es Go) → `code-review` → `qa-test-the-tests` y `qa-verify` completo → `git-commit` → `create-pr`.

Sin QA separado, salta el paso 3 y los `qa-verify`: el riesgo es que el mismo agente que implementa decide qué significa "funciona".

**Para un PoC el flujo es otro, más corto:** `system-design` en modo PoC deja el plan del experimento (hipótesis, alcance mínimo, qué medir, criterios de éxito y de abandono), y ese plan es la spec. Se construye una hipótesis a la vez con `tdd` solo en los invariantes, y cada una se cierra con su veredicto y la medición que lo respalda. Sin `to-spec`, sin `to-tickets` y sin QA completo. Al terminar, se vuelve a `system-design` en modo producción con el PoC como sistema existente.

## 3. Al terminar una fase: seguir, limpiar, traspasar, delegar o compactar

Una **fase** es un trozo de trabajo dentro de una sesión: la conversación de diseño, la implementación, la revisión. Esta decisión se toma **en la frontera** entre dos fases, no a mitad de una. Recorre las preguntas en orden; la primera respuesta "sí" decide. El detalle está en [references/fronteras-de-fase.md](references/fronteras-de-fase.md).

1. **¿Puedes seguir en esta sesión?** Sí, si la siguiente fase necesita esta conversación tal cual (diseño → implementación) y queda contexto de sobra. Seguir no cuesta nada y no pierde nada.
2. **¿Lo de esta sesión es irrelevante para lo que sigue?** Entonces limpia el contexto (`/clear` en Claude Code; en otras herramientas, una conversación nueva).
3. **¿Cambias de herramienta, de directorio o de persona?** Entonces `handoff`.
4. **¿La tarea se puede hacer sin ti, bien acotada?** Entonces delégala a un sub-agente y deja esta sesión intacta.
5. **Si no, compacta** (`/compact` donde exista; si no, `handoff` y conversación nueva) indicando qué debe conservar el resumen.

## 4. Dejar las reglas en el repositorio

Si el usuario pide dejar en su repo las reglas de estos plugins:

1. Copia [references/plantilla-AGENTS.md](references/plantilla-AGENTS.md) a `AGENTS.md` en la raíz del repositorio. Si ya existe, añade la plantilla como una sección y no borres nada.
2. Quita las secciones de los plugins que no estén instalados y ajusta las rutas si `docs/agentes/` dice otra cosa.
3. Codex, Copilot, Cursor y Windsurf leen `AGENTS.md` directamente. Claude Code, en sus versiones recientes, lo carga solo si el proyecto **no** tiene `CLAUDE.md`. Por eso: si ya existe un `CLAUDE.md`, añádele una línea `@AGENTS.md`; si no existe, crea uno con esa sola línea, que funciona igual en versiones antiguas y nuevas y no duplica nada.
4. Enséñale el resultado y no hagas commit salvo que lo pida.
