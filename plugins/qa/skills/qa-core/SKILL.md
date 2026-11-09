---
name: qa-core
description: "Base compartida del dominio QA: modelo de roles (dev, QA, ejecutor, humano), escalera de ambientes, formatos de criterios, escenarios y hallazgos, y los scripts deterministas (sello de integridad, trazabilidad, mutantes). Úsala cuando otra skill qa-* la referencie, o cuando el usuario pregunte cómo funciona el modelo de QA, qué garantiza el sello o cómo se trazan criterios a tests."
license: MIT
---

# QA: base compartida

Responde en español y conserva en inglés los términos técnicos habituales.

Esta skill no ejecuta un flujo: es la referencia y las herramientas que comparten todas las skills `qa-*`. Las demás skills apuntan aquí con rutas relativas (`../qa-core/...`), así que **debe estar instalada junto a ellas**, como carpeta hermana, en cualquier herramienta.

**Analogía:** es el reglamento y la mesa de control de un partido. Los jugadores (las demás skills) juegan; el reglamento dice qué vale y la mesa cuenta.

## Referencias

| Archivo | Qué contiene |
|---|---|
| [referencias/modelo-de-roles.md](referencias/modelo-de-roles.md) | Quién escribe qué y quién aprueba; modos solo y dúo; barrera de información N1-N3; escalamiento; qué garantiza el sello y qué no |
| [referencias/escalera-de-ambientes.md](referencias/escalera-de-ambientes.md) | Peldaños 0 a 5, regla de asignación de escenarios, ritmos de ejecución |
| [referencias/formatos.md](referencias/formatos.md) | Handoff, criterios, escenarios (formato parseable), convención de IDs en JUnit, hallazgos, escalamientos, informe de verificación |
| [referencias/portabilidad.md](referencias/portabilidad.md) | Cómo se ejecutan las instrucciones de sub-agentes, preguntas al usuario y carga de skills en cada herramienta (Claude Code, Codex, Copilot, Cursor, Windsurf) |

## Scripts

Python 3.10+ y solo la biblioteca estándar (más `git` para el sello contra la rama base y los mutantes). Se ejecutan desde la raíz del repositorio bajo prueba; `<qa-core>` es la ruta de esta carpeta.

| Script | Qué hace |
|---|---|
| `scripts/sello.py` | Hash de todo el oráculo; detecta cambios, enlaces simbólicos y re-sellados desde la rama base |
| `scripts/trazabilidad.py` | Cadena criterio → escenario → test → resultado; saltado, no ejecutado o reporte viejo no son verdes |
| `scripts/mutantes.py` | Mutantes en worktrees temporales; solo cuenta como detectado si falla un escenario |

Tests: `python3 -m unittest discover -s <qa-core>/scripts/tests`.
