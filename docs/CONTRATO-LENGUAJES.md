# Contrato entre `ingenieria` y los plugins de lenguaje

Las skills de `ingenieria` son agnósticas al lenguaje. Cuando necesitan conocimiento de un lenguaje concreto, lo piden a un **plugin de lenguaje** a través de skills con **nombre de rol fijo**. Es el patrón ports & adapters aplicado a skills: `ingenieria` define el port (el rol y lo que se espera de él) y cada plugin de lenguaje es un adapter.

Analogía: es un enchufe estándar. El electrodoméstico (`ingenieria`) no sabe qué central eléctrica hay detrás; solo sabe que si la toma existe, tiene corriente.

## Roles

| Rol | Lo invoca | Debe aportar |
|---|---|---|
| `<lenguaje>-review` | `code-review` | Reglas de revisión solo para los archivos de ese lenguaje, con severidad, sin repetir la rúbrica transversal. Se pegan en el prompt del sub-agente revisor de ese lenguaje. |
| `<lenguaje>-testing` | `tdd` | Forma idiomática de los tests, seams típicos, dobles de test preferidos y comandos (ejecutar un test, repetir, race detector, cobertura). |
| `<lenguaje>-debugging` | `diagnosing-bugs` | El comando concreto para cada técnica del loop (aislar, repetir, fuzz, bisect, diferencial), debugger, logs etiquetados, benchmarks y profiling. |
| `<lenguaje>-design` | `codebase-design` | Cómo se expresan módulo, interfaz, seam, adapter e inyección de dependencias con las herramientas del lenguaje. |

Un plugin de lenguaje puede implementar solo algunos roles. Si falta uno, la skill agnóstica sigue con sus reglas genéricas y lo dice en una línea.

## Reglas para que el contrato funcione

1. **El nombre del plugin es el identificador del lenguaje** (`go`, `php`, `typescript`, `python`, `sql`) y **cada skill de rol se llama `<lenguaje>-<rol>`** (`go-review`). Así el nombre es único en las herramientas sin espacios de nombres (Codex, Copilot, Cursor, Windsurf), y `go-review` existe exactamente cuando el plugin `go` está instalado. En Claude Code aparece como `go:go-review`.
2. **Las skills de rol son invocadas por el modelo**: su descripción es lo que permite que otra skill las encuentre. El frontmatter cumple el estándar Agent Skills (solo `name`, `description` y los campos opcionales del estándar).
3. **La descripción empieza diciendo qué lenguaje y qué rol cubre** y nombra la skill de `ingenieria` que la carga.
4. **Una skill de rol complementa, no repite.** No copia la disciplina de la skill agnóstica (el ciclo de TDD, las fases del diagnóstico, la rúbrica transversal); solo aporta lo propio del lenguaje.
5. **Las skills de profundidad del lenguaje son dueñas de sus reglas** (en `go`: `senior-go-idiomatic`, `go-design-rules`, `ddd-go-idiomatic`). La skill de rol apunta a ellas en vez de duplicarlas.

## Detección del lenguaje

Las skills agnósticas mapean extensiones a identificadores. Si añades un lenguaje cuya extensión no aparece aquí, añádela también en el paso 5 de `code-review` y en la sección "Lenguaje" de `tdd`, `diagnosing-bugs` y `codebase-design`.

| Extensiones | Identificador |
|---|---|
| `.go` | `go` |
| `.php` | `php` |
| `.ts`, `.tsx`, `.js` | `typescript` |
| `.py` | `python` |
| `.sql` | `sql` |
| `.java` | `java` |
| `.kt` | `kotlin` |

## Cómo añadir un lenguaje (ejemplo: PHP)

```
plugins/php/
├── LICENSE
├── README.md
└── skills/
    ├── php-review/SKILL.md         # name: php-review
    ├── php-testing/SKILL.md        # name: php-testing
    ├── php-debugging/SKILL.md      # name: php-debugging
    └── php-design/SKILL.md         # name: php-design
```

Después añade el plugin a `catalogo.json` y ejecuta `python3 tools/build_manifests.py`: genera los manifiestos de Claude Code, Codex, Copilot y Cursor. Valida con `agentskills validate plugins/php/skills/*` y `claude plugin validate plugins/php`. No hace falta tocar el plugin `ingenieria`.
