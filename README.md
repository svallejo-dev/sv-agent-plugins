# sv-agent-plugins

[![validar](https://github.com/svallejo-dev/sv-agent-plugins/actions/workflows/validar.yml/badge.svg)](https://github.com/svallejo-dev/sv-agent-plugins/actions/workflows/validar.yml)

**Español** · [English](#english)

Plugins de ingeniería para agentes de código, en español, que funcionan en **Claude Code, OpenAI Codex, GitHub Copilot, Cursor y Windsurf**. Están construidos sobre dos estándares abiertos: [Agent Skills](https://agentskills.io) (cada skill es una carpeta con un `SKILL.md`) y [Agent Plugins](https://agent-plugins.org) (empaquetado). Además incluyen los manifiestos propios de cada herramienta.

| Plugin | Para qué | Skills |
|---|---|---|
| [`general`](plugins/general) | Interrogar planes, enseñar con analogías, escribir para agentes, traspasos e investigación | `grilling` `teach` `writing-for-agents` `handoff` `research` |
| [`ingenieria`](plugins/ingenieria) | Flujo de ingeniería agnóstico al lenguaje: spec, tickets, TDD, diagnóstico, diseño, code review, commits y PRs | `ingenieria-setup` `grill-with-docs` `domain-modeling` `to-spec` `to-tickets` `tdd` `diagnosing-bugs` `codebase-design` `code-review` `git-commit` `create-pr` |
| [`qa`](plugins/qa) | QA separado del dev: el agente que implementa nunca escribe el oráculo y ningún agente certifica | `qa-setup` `qa-acceptance-criteria` `qa-test-design` `qa-test-automation` `qa-verify` `qa-test-the-tests` `qa-toolbox` `qa-core` |
| [`arquitectura`](plugins/arquitectura) | System design a gran escala partiendo de lo que existe, con capacidad calculada y red team | `system-design` `design-stress-test` `capacity-estimation` `strategic-design` `business-archetypes` `building-blocks` |
| [`go`](plugins/go) | Go idiomático, reglas de diseño, DDD en Go y las skills de rol del contrato de lenguajes | `senior-go-idiomatic` `go-design-rules` `ddd-go-idiomatic` `go-review` `go-testing` `go-debugging` `go-design` |

## Compatibilidad

| Herramienta | Cómo se instala | Estado |
|---|---|---|
| **Claude Code** | Marketplace de plugins (`.claude-plugin/`) | Verificado: Claude Code 2.1.319 instala los 5 plugins y las 37 skills |
| **OpenAI Codex** | Marketplace de plugins (`.agents/plugins/`, `plugin.json` de Agent Plugins) | Verificado: codex-cli 0.167.0 instala los 5 plugins y las 37 skills |
| **GitHub Copilot** (CLI y VS Code) | Marketplace de plugins (`.github/plugin/`, `plugin.json` de Agent Plugins) | Verificado: Copilot CLI 1.0.107 instala los 5 plugins y las 37 skills |
| **Cursor** | Plugin (`.cursor-plugin/`, Agent Plugins) o carpeta de skills | Según su documentación; no probado en Cursor |
| **Windsurf** | Carpeta de skills con `install.sh` (Windsurf no tiene sistema de plugins) | Instalador probado; no probado dentro de Windsurf |
| Otras herramientas compatibles con Agent Skills | `install.sh --dest <carpeta>` | — |

## Instalación

### Claude Code

```bash
claude plugin marketplace add svallejo-dev/sv-agent-plugins
claude plugin install qa@sv-agent-plugins          # o general, ingenieria, arquitectura, go
```

Dentro de una sesión: `/plugin marketplace add svallejo-dev/sv-agent-plugins` y `/plugin install qa@sv-agent-plugins`. En Claude Code las skills de un plugin llevan el nombre del plugin como prefijo: `qa:qa-verify`, `ingenieria:tdd`.

### OpenAI Codex

```bash
codex plugin marketplace add svallejo-dev/sv-agent-plugins
codex plugin add qa@sv-agent-plugins
```

También puedes instalar desde el navegador de plugins de la app o de la CLI (`/plugins`).

### GitHub Copilot

CLI:

```bash
copilot plugin marketplace add svallejo-dev/sv-agent-plugins
copilot plugin install qa@sv-agent-plugins
```

En VS Code, añade el repositorio como marketplace de agent plugins en la configuración de Copilot Chat y búscalo con `@agentPlugins` en la vista de Extensiones. Para un solo repositorio sin plugins: `./install.sh --tool copilot --project-dir <repo>` copia las skills a `.github/skills/`.

### Cursor

- **Plugin local**: `ln -s "$PWD/plugins/qa" ~/.cursor/plugins/local/qa` desde un clon de este repositorio, y recarga la ventana.
- **Marketplace de equipo**: importa este repositorio en el panel de plugins de tu equipo; lee `.cursor-plugin/marketplace.json`.
- **Solo skills** (también para `cursor-agent` en terminal, que hoy no registra las skills de los plugins): `./install.sh --tool cursor --scope user --plugins qa`.

### Windsurf

Windsurf lee skills de `.windsurf/skills/` (proyecto) y `~/.codeium/windsurf/skills/` (usuario):

```bash
git clone https://github.com/svallejo-dev/sv-agent-plugins
cd sv-agent-plugins
./install.sh --tool windsurf --scope user --plugins qa,ingenieria
```

### `install.sh`

```
./install.sh --tool <claude|codex|copilot|cursor|windsurf> [--scope user|project] [--plugins a,b] [--project-dir DIR] [--link] [--force] [--dry-run]
./install.sh --dest <carpeta-de-skills> [--plugins a,b]
```

Instala las skills de cada plugin elegido, copia por defecto (`--link` crea enlaces simbólicos para recibir actualizaciones con `git pull`) y nunca sobrescribe una skill ajena sin `--force`. Instala siempre el plugin completo: algunas skills dependen de una hermana (por ejemplo, todas las `qa-*` usan `qa-core`).

## Cómo funcionan juntos

```
          general  ◄──── grilling, research
           ▲     ▲
  arquitectura ──┼──► domain-modeling (ADRs, glosario)
                 │
           ingenieria ──── tdd, diagnosing-bugs, codebase-design, code-review
            ▲    │         detectan el lenguaje y cargan <lenguaje>-<rol>
  qa ───────┘    ▼
  (oráculo)    go  (php)  (typescript) ...    plugins de lenguaje
```

- Cada plugin funciona solo; juntos rinden más. Si una skill que otra recomienda no está instalada, sigue sin ella y lo dice.
- Los plugins de lenguaje implementan las skills `<lenguaje>-review`, `<lenguaje>-testing`, `<lenguaje>-debugging` y `<lenguaje>-design` ([contrato](docs/CONTRATO-LENGUAJES.md)).
- Flujo típico con QA separado: `to-spec` → `qa-acceptance-criteria` → `qa-test-design` → `qa-test-automation` → `to-tickets` → `tdd` por ticket → `qa-verify` → `qa-test-the-tests` → `code-review` → `create-pr`.

## Portabilidad: decisiones de diseño

- **Nombres únicos.** Codex, Copilot, Cursor y Windsurf instalan las skills en carpetas planas, sin el espacio de nombres del plugin. Por eso las skills genéricas llevan prefijo (`qa-verify`, `go-testing`, `ingenieria-setup`), y las referencias entre skills usan el nombre a secas.
- **Frontmatter estándar.** Solo `name`, `description` y `license`, validados con el validador de referencia de Agent Skills. Las skills que en Claude Code eran solo para el usuario lo dicen ahora en su descripción, porque `disable-model-invocation` no es parte del estándar.
- **Autocontenidas.** Lo compartido vive en una skill hermana (`qa-core`), no en carpetas del plugin que una instalación de skills sueltas no copiaría.
- **Instrucciones neutras.** Donde una skill usa sub-agentes, preguntas al usuario o carga de otras skills, dice qué hacer si la herramienta no lo ofrece ([portabilidad](plugins/qa/skills/qa-core/referencias/portabilidad.md)).
- **Una sola fuente de manifiestos.** `catalogo.json` → `python3 tools/build_manifests.py` genera los 24 manifiestos de Claude Code, Codex, Copilot y Cursor; la CI falla si se desincronizan.

## Contribuir

1. Las skills cumplen el [estándar Agent Skills](https://agentskills.io/specification): `pip install skills-ref && agentskills validate plugins/<plugin>/skills/<skill>`.
2. Un plugin nuevo se añade en `catalogo.json`; después `python3 tools/build_manifests.py`.
3. La CI (`.github/workflows/validar.yml`) comprueba manifiestos, skills, tests de scripts, `claude plugin validate` y el instalador.

## Origen y licencias

- `general` y la mayor parte de `ingenieria` están adaptadas de [mattpocock/skills](https://github.com/mattpocock/skills) (MIT): traducidas, con tickets como Markdown local y analogías pedagógicas.
- El catálogo `building-blocks` viene de [proyecto26/system-design-skills](https://github.com/proyecto26/system-design-skills) (MIT), curado y corregido.
- `qa`, `go`, el resto de `arquitectura`, `git-commit` y `create-pr` son propios.

Licencia MIT ([LICENSE](LICENSE)).

---

## English

Engineering plugins for coding agents, **written in Spanish**, that work in **Claude Code, OpenAI Codex, GitHub Copilot, Cursor and Windsurf**. They are built on the open [Agent Skills](https://agentskills.io) standard (each skill is a folder with a `SKILL.md`) and the [Agent Plugins](https://agent-plugins.org) packaging standard, plus each tool's native manifests.

| Plugin | What it does |
|---|---|
| `general` | Plan grilling, teaching with analogies, writing for agents, session handoffs, research with primary sources |
| `ingenieria` | Language-agnostic engineering flow: specs, tickets, TDD, debugging, module design, code review, commits, PRs |
| `qa` | QA separated from development: the implementing agent never writes the oracle and no agent certifies; integrity seal, traceability and mutation scripts with tests |
| `arquitectura` | Large-scale system design starting from what exists, with computed capacity estimates and a parallel red team |
| `go` | Idiomatic Go, design rules, DDD in Go, and the language-role skills used by `ingenieria` |

### Install

| Tool | Command |
|---|---|
| Claude Code | `claude plugin marketplace add svallejo-dev/sv-agent-plugins` then `claude plugin install qa@sv-agent-plugins` |
| OpenAI Codex | `codex plugin marketplace add svallejo-dev/sv-agent-plugins` then `codex plugin add qa@sv-agent-plugins` |
| GitHub Copilot CLI | `copilot plugin marketplace add svallejo-dev/sv-agent-plugins` then `copilot plugin install qa@sv-agent-plugins` |
| Cursor | symlink `plugins/<name>` into `~/.cursor/plugins/local/`, import the repo as a team marketplace, or `./install.sh --tool cursor --scope user` |
| Windsurf | `./install.sh --tool windsurf --scope user --plugins qa` (Windsurf has no plugin system; skills go to `~/.codeium/windsurf/skills/`) |

Claude Code, Codex and Copilot CLI installs were verified end to end (5 plugins, 37 skills). Cursor and Windsurf follow their documented formats; the installer is tested, but not inside those editors.

Always install whole plugins: some skills depend on a sibling skill (all `qa-*` skills use `qa-core`). MIT licensed; see [Origin](#origen-y-licencias) for third-party attributions.
