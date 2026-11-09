# sv-agent-plugins

[![validar](https://github.com/svallejo-dev/sv-agent-plugins/actions/workflows/validar.yml/badge.svg)](https://github.com/svallejo-dev/sv-agent-plugins/actions/workflows/validar.yml)

**Español** · [English](#english)

Plugins de ingeniería para agentes de código, en español, que funcionan en **Claude Code, OpenAI Codex, GitHub Copilot, Cursor y Windsurf**. Están construidos sobre dos estándares abiertos: [Agent Skills](https://agentskills.io) (cada skill es una carpeta con un `SKILL.md`) y [Agent Plugins](https://agent-plugins.org) (empaquetado). Además incluyen los manifiestos propios de cada herramienta.

| Plugin | Para qué | Skills |
|---|---|---|
| [`general`](plugins/general) | Por dónde empezar, interrogar planes, enseñar con analogías, escribir para agentes, traspasos e investigación | `por-donde-empiezo` `grilling` `teach` `writing-for-agents` `handoff` `research` |
| [`ingenieria`](plugins/ingenieria) | Flujo de ingeniería agnóstico al lenguaje: spec, tickets, TDD, diagnóstico, diseño, code review, commits y PRs | `ingenieria-setup` `grill-with-docs` `domain-modeling` `to-spec` `to-tickets` `tdd` `diagnosing-bugs` `codebase-design` `code-review` `git-commit` `create-pr` |
| [`qa`](plugins/qa) | QA separado del dev: el agente que implementa nunca escribe el oráculo y ningún agente certifica | `qa-setup` `qa-acceptance-criteria` `qa-test-design` `qa-test-automation` `qa-verify` `qa-test-the-tests` `qa-toolbox` `qa-core` |
| [`arquitectura`](plugins/arquitectura) | System design a gran escala partiendo de lo que existe, con capacidad calculada y red team | `system-design` `design-stress-test` `capacity-estimation` `strategic-design` `business-archetypes` `building-blocks` |
| [`go`](plugins/go) | Go idiomático, reglas de diseño, DDD en Go, simplificación sin cambiar comportamiento y las skills de rol del contrato de lenguajes | `senior-go-idiomatic` `go-design-rules` `ddd-go-idiomatic` `go-simplify` `go-review` `go-testing` `go-debugging` `go-design` |

## Compatibilidad

| Herramienta | Cómo se instala | Estado |
|---|---|---|
| **Claude Code** | Marketplace de plugins (`.claude-plugin/`) | Verificado: Claude Code 2.1.319 instala los 5 plugins y las 39 skills |
| **OpenAI Codex** | Marketplace de plugins (`.agents/plugins/`, `plugin.json` de Agent Plugins) | Verificado: codex-cli 0.167.0 instala los 5 plugins y las 39 skills |
| **GitHub Copilot** (CLI y VS Code) | Marketplace de plugins (`.github/plugin/`, `plugin.json` de Agent Plugins) | Verificado: Copilot CLI 1.0.107 instala los 5 plugins y las 39 skills |
| **Cursor** | Plugin (`.cursor-plugin/`, Agent Plugins) o carpeta de skills | Según su documentación; no probado en Cursor |
| **Windsurf** | Carpeta de skills con `install.sh` (Windsurf no tiene sistema de plugins) | Instalador probado; no probado dentro de Windsurf |
| Otras herramientas compatibles con Agent Skills | `install.sh --dest <carpeta>` | — |

## Instalación

Cada herramienta tiene dos formas: **todos los plugins de una vez** o **solo los que elijas**. Los nombres de los plugins son `general`, `ingenieria`, `qa`, `arquitectura` y `go`. Después de instalar, abre una sesión nueva para que la herramienta cargue las skills.

### Claude Code

Todos los plugins:

```bash
claude plugin marketplace add svallejo-dev/sv-agent-plugins; for p in general ingenieria qa arquitectura go; do claude plugin install "$p@sv-agent-plugins"; done
```

Solo algunos:

```bash
claude plugin marketplace add svallejo-dev/sv-agent-plugins
claude plugin install qa@sv-agent-plugins
```

Dentro de una sesión: `/plugin marketplace add svallejo-dev/sv-agent-plugins` y luego `/plugin install <plugin>@sv-agent-plugins` por cada plugin (o elígelos en el menú de `/plugin`). En Claude Code las skills llevan el nombre del plugin como prefijo: `qa:qa-verify`, `ingenieria:tdd`.

### OpenAI Codex

Todos los plugins:

```bash
codex plugin marketplace add svallejo-dev/sv-agent-plugins; for p in general ingenieria qa arquitectura go; do codex plugin add "$p@sv-agent-plugins"; done
```

Solo algunos:

```bash
codex plugin marketplace add svallejo-dev/sv-agent-plugins
codex plugin add qa@sv-agent-plugins
```

También puedes instalarlos desde el navegador de plugins de la app o de la CLI (`/plugins`).

### GitHub Copilot

CLI, todos los plugins:

```bash
copilot plugin marketplace add svallejo-dev/sv-agent-plugins; for p in general ingenieria qa arquitectura go; do copilot plugin install "$p@sv-agent-plugins"; done
```

CLI, solo algunos:

```bash
copilot plugin marketplace add svallejo-dev/sv-agent-plugins
copilot plugin install qa@sv-agent-plugins
```

En VS Code, añade el repositorio como marketplace de agent plugins en la configuración de Copilot Chat y búscalo con `@agentPlugins` en la vista de Extensiones.

Solo las skills, en un repositorio concreto (las copia a `<repo>/.github/skills/`):

```bash
./install.sh --tool copilot --project-dir <repo>                       # todas
./install.sh --tool copilot --project-dir <repo> --plugins qa          # algunas
```

### Cursor

Desde un clon de este repositorio:

```bash
git clone https://github.com/svallejo-dev/sv-agent-plugins && cd sv-agent-plugins
```

Todos los plugins, como plugins locales (después recarga la ventana):

```bash
mkdir -p ~/.cursor/plugins/local; for p in general ingenieria qa arquitectura go; do ln -sfn "$PWD/plugins/$p" ~/.cursor/plugins/local/$p; done
```

Solo algunos: `ln -sfn "$PWD/plugins/qa" ~/.cursor/plugins/local/qa`.

Solo las skills (también sirve para `cursor-agent` en terminal, que hoy no registra las skills de los plugins):

```bash
./install.sh --tool cursor --scope user                 # todas
./install.sh --tool cursor --scope user --plugins qa    # algunas
```

Para un equipo: importa este repositorio en el panel de plugins del equipo; Cursor lee `.cursor-plugin/marketplace.json` y muestra los cinco plugins.

### Windsurf

Windsurf no tiene sistema de plugins: lee skills de `.windsurf/skills/` (proyecto) y `~/.codeium/windsurf/skills/` (usuario).

```bash
git clone https://github.com/svallejo-dev/sv-agent-plugins && cd sv-agent-plugins
./install.sh --tool windsurf --scope user                          # todos los plugins
./install.sh --tool windsurf --scope user --plugins qa,ingenieria  # algunos
```

### Todas las herramientas a la vez (solo skills)

Si usas varias herramientas en la misma máquina, desde el clon:

```bash
for t in claude codex cursor windsurf; do ./install.sh --tool "$t" --scope user --link; done
```

`--link` crea enlaces simbólicos al clon, así un `git pull` actualiza todas las herramientas a la vez. Si en Claude Code, Codex o Copilot ya instalaste los plugins por marketplace, no instales además sus skills sueltas: tendrías cada skill dos veces.

### `install.sh`

```
./install.sh --tool <claude|codex|copilot|cursor|windsurf> [--scope user|project] [--plugins a,b] [--project-dir DIR] [--link] [--force] [--dry-run]
./install.sh --dest <carpeta-de-skills> [--plugins a,b]
```

- Sin `--plugins`, instala **todos** los plugins.
- Copia por defecto; `--link` crea enlaces simbólicos para recibir actualizaciones con `git pull`.
- Nunca sobrescribe una skill ajena sin `--force`; `--dry-run` muestra qué instalaría.
- Instala siempre el plugin completo: algunas skills dependen de una hermana (todas las `qa-*` usan `qa-core`).

## Actualizar

Cuando el repositorio publica cambios, cada plugin sube de versión; sin eso, ninguna herramienta los detecta.

```bash
# Claude Code (después, abre una sesión nueva)
claude plugin marketplace update sv-agent-plugins; for p in general ingenieria qa arquitectura go; do claude plugin update "$p@sv-agent-plugins"; done
# OpenAI Codex
codex plugin marketplace upgrade sv-agent-plugins
# GitHub Copilot CLI
copilot plugin marketplace update sv-agent-plugins; for p in general ingenieria qa arquitectura go; do copilot plugin update "$p@sv-agent-plugins"; done
# Cursor, Windsurf o install.sh con --link: basta con actualizar el clon
git -C <ruta-del-clon> pull
# install.sh sin --link: actualiza el clon y vuelve a ejecutar el mismo install.sh
```

## Usar las reglas en tu proyecto

La skill `por-donde-empiezo` tiene una plantilla de `AGENTS.md` con las reglas y los flujos de estos plugins. Pídele "deja las reglas de estos plugins en el repo" y la copia a tu `AGENTS.md`, quitando los plugins que no uses. Codex, Copilot, Cursor y Windsurf leen `AGENTS.md` directamente. Claude Code, en sus versiones recientes, también lo carga, pero solo cuando el proyecto no tiene `CLAUDE.md`; por eso la skill deja en `CLAUDE.md` una línea `@AGENTS.md`, que lo importa en cualquier caso. La plantilla está en [plugins/general/skills/por-donde-empiezo/references/plantilla-AGENTS.md](plugins/general/skills/por-donde-empiezo/references/plantilla-AGENTS.md).

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
- Flujo típico con QA separado: `to-spec` → `qa-acceptance-criteria` → `qa-test-design` → `qa-test-automation` → `to-tickets` → `tdd` por ticket → `qa-verify` → `go-simplify` → `code-review` → `qa-test-the-tests` → `create-pr`. Si no sabes por dónde empezar: `por-donde-empiezo`.

## Portabilidad: decisiones de diseño

- **Nombres únicos.** Codex, Copilot, Cursor y Windsurf instalan las skills en carpetas planas, sin el espacio de nombres del plugin. Por eso las skills genéricas llevan prefijo (`qa-verify`, `go-testing`, `ingenieria-setup`), y las referencias entre skills usan el nombre a secas.
- **Frontmatter estándar.** Solo `name`, `description` y `license`, validados con el validador de referencia de Agent Skills. Las skills que en Claude Code eran solo para el usuario lo dicen ahora en su descripción, porque `disable-model-invocation` no es parte del estándar.
- **Autocontenidas.** Lo compartido vive en una skill hermana (`qa-core`), no en carpetas del plugin que una instalación de skills sueltas no copiaría.
- **Instrucciones neutras.** Donde una skill usa sub-agentes, preguntas al usuario o carga de otras skills, dice qué hacer si la herramienta no lo ofrece ([portabilidad](plugins/qa/skills/qa-core/referencias/portabilidad.md)).
- **Una sola fuente de manifiestos.** `catalogo.json` → `python3 tools/build_manifests.py` genera los 24 manifiestos de Claude Code, Codex, Copilot y Cursor; la CI falla si se desincronizan.

## Contribuir

Las reglas completas están en [AGENTS.md](AGENTS.md). Lo esencial:

1. Las skills cumplen el [estándar Agent Skills](https://agentskills.io/specification): `pip install skills-ref && agentskills validate plugins/<plugin>/skills/<skill>`.
2. **Todo cambio en un plugin sube su versión en `catalogo.json`**; después `python3 tools/build_manifests.py`. Sin subir la versión, quien ya lo instaló nunca recibe el cambio.
3. Para probar sin instalar: `claude --plugin-dir ./plugins/<plugin>`.
4. La CI (`.github/workflows/validar.yml`) comprueba manifiestos, versiones, skills, tests de scripts, `claude plugin validate` y el instalador.

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
| `general` | Where to start (a router over all plugins plus an AGENTS.md template), plan grilling, teaching with analogies, writing for agents, session handoffs, research with primary sources |
| `ingenieria` | Language-agnostic engineering flow: specs, tickets, TDD, debugging, module design, code review, commits, PRs |
| `qa` | QA separated from development: the implementing agent never writes the oracle and no agent certifies; integrity seal, traceability and mutation scripts with tests |
| `arquitectura` | Large-scale system design starting from what exists, with computed capacity estimates and a parallel red team |
| `go` | Idiomatic Go, design rules, DDD in Go, behavior-preserving simplification (`go-simplify`), and the language-role skills used by `ingenieria` |

### Install

All plugins at once (plugin names: `general`, `ingenieria`, `qa`, `arquitectura`, `go`):

```bash
# Claude Code
claude plugin marketplace add svallejo-dev/sv-agent-plugins; for p in general ingenieria qa arquitectura go; do claude plugin install "$p@sv-agent-plugins"; done
# OpenAI Codex
codex plugin marketplace add svallejo-dev/sv-agent-plugins; for p in general ingenieria qa arquitectura go; do codex plugin add "$p@sv-agent-plugins"; done
# GitHub Copilot CLI
copilot plugin marketplace add svallejo-dev/sv-agent-plugins; for p in general ingenieria qa arquitectura go; do copilot plugin install "$p@sv-agent-plugins"; done
# Cursor (from a clone of this repo; then reload the window)
mkdir -p ~/.cursor/plugins/local; for p in general ingenieria qa arquitectura go; do ln -sfn "$PWD/plugins/$p" ~/.cursor/plugins/local/$p; done
# Windsurf (from a clone; no plugin system, skills only)
./install.sh --tool windsurf --scope user
```

A single plugin:

| Tool | Command |
|---|---|
| Claude Code | `claude plugin marketplace add svallejo-dev/sv-agent-plugins` then `claude plugin install qa@sv-agent-plugins` |
| OpenAI Codex | `codex plugin marketplace add svallejo-dev/sv-agent-plugins` then `codex plugin add qa@sv-agent-plugins` |
| GitHub Copilot CLI | `copilot plugin marketplace add svallejo-dev/sv-agent-plugins` then `copilot plugin install qa@sv-agent-plugins` |
| Cursor | `ln -sfn "$PWD/plugins/qa" ~/.cursor/plugins/local/qa`, or `./install.sh --tool cursor --scope user --plugins qa` |
| Windsurf | `./install.sh --tool windsurf --scope user --plugins qa` (skills go to `~/.codeium/windsurf/skills/`) |

Claude Code, Codex and Copilot CLI installs were verified end to end (5 plugins, 39 skills). Cursor and Windsurf follow their documented formats; the installer is tested, but not inside those editors.

To update, run `claude plugin marketplace update sv-agent-plugins` and `claude plugin update <plugin>@sv-agent-plugins` (or the equivalent in each tool); every published change bumps the plugin version.

Always install whole plugins: some skills depend on a sibling skill (all `qa-*` skills use `qa-core`). MIT licensed; see [Origin](#origen-y-licencias) for third-party attributions.
