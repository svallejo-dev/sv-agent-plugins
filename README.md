# sv-agent-plugins

[![validate](https://github.com/svallejo-dev/sv-agent-plugins/actions/workflows/validate.yml/badge.svg)](https://github.com/svallejo-dev/sv-agent-plugins/actions/workflows/validate.yml)

Engineering plugins for coding agents that work in **Claude Code, OpenAI Codex, GitHub Copilot, Cursor and Windsurf**. They are built on two open standards: [Agent Skills](https://agentskills.io) (each skill is a folder with a `SKILL.md`) and [Agent Plugins](https://agent-plugins.org) (packaging), plus each tool's native manifests.

The skills are written in English and **answer in the user's language**: ask in Spanish, get the answer in Spanish.

| Plugin | What it is for | Skills |
|---|---|---|
| [`general`](plugins/general) | Where to start, grilling a plan, teaching with analogies, writing for agents, handoffs and research | `where-to-start` `grilling` `teach` `writing-for-agents` `handoff` `research` |
| [`engineering`](plugins/engineering) | Language-agnostic engineering workflow: spec, tickets, TDD, diagnosis, design, code review, commits and PRs | `engineering-setup` `grill-with-docs` `domain-modeling` `to-spec` `to-tickets` `tdd` `diagnosing-bugs` `codebase-design` `code-review` `git-commit` `create-pr` |
| [`qa`](plugins/qa) | QA separated from dev: the implementing agent never writes the oracle and no agent certifies | `qa-setup` `qa-acceptance-criteria` `qa-test-design` `qa-test-automation` `qa-verify` `qa-test-the-tests` `qa-toolbox` `qa-core` |
| [`architecture`](plugins/architecture) | Large-scale system design starting from what exists, with computed capacity and a red team | `system-design` `design-stress-test` `capacity-estimation` `strategic-design` `business-archetypes` `building-blocks` |
| [`go`](plugins/go) | Idiomatic Go, design rules, DDD in Go, behavior-preserving simplification and the role skills of the language contract | `senior-go-idiomatic` `go-design-rules` `ddd-go-idiomatic` `go-simplify` `go-review` `go-testing` `go-debugging` `go-design` |

## Compatibility

| Tool | How it installs | Status |
|---|---|---|
| **Claude Code** | Plugin marketplace (`.claude-plugin/`) | Verified: Claude Code installs the 5 plugins and 39 skills |
| **OpenAI Codex** | Plugin marketplace (`.agents/plugins/`, Agent Plugins `plugin.json`) | Verified: codex-cli installs the 5 plugins and 39 skills |
| **GitHub Copilot** (CLI and VS Code) | Plugin marketplace (`.github/plugin/`, Agent Plugins `plugin.json`) | Verified: Copilot CLI installs the 5 plugins and 39 skills |
| **Cursor** | Plugin (`.cursor-plugin/`, Agent Plugins) or skills folder | Per its documentation; not tested inside Cursor |
| **Windsurf** | Skills folder with `install.sh` (Windsurf has no plugin system) | Installer tested; not tested inside Windsurf |
| Other tools compatible with Agent Skills | `install.sh --dest <folder>` | — |

## Installation

Each tool has two ways: **all the plugins at once** or **only the ones you choose**. The plugin names are `general`, `engineering`, `qa`, `architecture` and `go`. After installing, open a new session so the tool loads the skills.

### Claude Code

All the plugins:

```bash
claude plugin marketplace add svallejo-dev/sv-agent-plugins; for p in general engineering qa architecture go; do claude plugin install "$p@sv-agent-plugins"; done
```

Only some:

```bash
claude plugin marketplace add svallejo-dev/sv-agent-plugins
claude plugin install qa@sv-agent-plugins
```

Inside a session: `/plugin marketplace add svallejo-dev/sv-agent-plugins` and then `/plugin install <plugin>@sv-agent-plugins` for each plugin (or pick them in the `/plugin` menu). In Claude Code skills carry the plugin name as a prefix: `qa:qa-verify`, `engineering:tdd`.

### OpenAI Codex

All the plugins:

```bash
codex plugin marketplace add svallejo-dev/sv-agent-plugins; for p in general engineering qa architecture go; do codex plugin add "$p@sv-agent-plugins"; done
```

Only some:

```bash
codex plugin marketplace add svallejo-dev/sv-agent-plugins
codex plugin add qa@sv-agent-plugins
```

You can also install them from the plugin browser in the app or the CLI (`/plugins`).

### GitHub Copilot

CLI, all the plugins:

```bash
copilot plugin marketplace add svallejo-dev/sv-agent-plugins; for p in general engineering qa architecture go; do copilot plugin install "$p@sv-agent-plugins"; done
```

CLI, only some:

```bash
copilot plugin marketplace add svallejo-dev/sv-agent-plugins
copilot plugin install qa@sv-agent-plugins
```

In VS Code, add the repository as an agent plugins marketplace in the Copilot Chat settings and search for it with `@agentPlugins` in the Extensions view.

Only the skills, in a specific repository (it copies them to `<repo>/.github/skills/`):

```bash
./install.sh --tool copilot --project-dir <repo>                       # all
./install.sh --tool copilot --project-dir <repo> --plugins qa          # some
```

### Cursor

From a clone of this repository:

```bash
git clone https://github.com/svallejo-dev/sv-agent-plugins && cd sv-agent-plugins
```

All the plugins, as local plugins (then reload the window):

```bash
mkdir -p ~/.cursor/plugins/local; for p in general engineering qa architecture go; do ln -sfn "$PWD/plugins/$p" ~/.cursor/plugins/local/$p; done
```

Only some: `ln -sfn "$PWD/plugins/qa" ~/.cursor/plugins/local/qa`.

Only the skills (it also works for `cursor-agent` in the terminal, which today does not register plugin skills):

```bash
./install.sh --tool cursor --scope user                 # all
./install.sh --tool cursor --scope user --plugins qa    # some
```

For a team: import this repository in the team's plugin panel; Cursor reads `.cursor-plugin/marketplace.json` and shows the five plugins.

### Windsurf

Windsurf has no plugin system: it reads skills from `.windsurf/skills/` (project) and `~/.codeium/windsurf/skills/` (user).

```bash
git clone https://github.com/svallejo-dev/sv-agent-plugins && cd sv-agent-plugins
./install.sh --tool windsurf --scope user                           # all the plugins
./install.sh --tool windsurf --scope user --plugins qa,engineering  # some
```

### Every tool at once (skills only)

If you use several tools on the same machine, from the clone:

```bash
for t in claude codex cursor windsurf; do ./install.sh --tool "$t" --scope user --link; done
```

`--link` creates symbolic links to the clone, so a `git pull` updates every tool at once. If you already installed the plugins through the marketplace in Claude Code, Codex or Copilot, do not also install their loose skills: you would have every skill twice.

### `install.sh`

```
./install.sh --tool <claude|codex|copilot|cursor|windsurf> [--scope user|project] [--plugins a,b] [--project-dir DIR] [--link] [--force] [--dry-run]
./install.sh --dest <skills-folder> [--plugins a,b]
```

- Without `--plugins`, it installs **all** the plugins.
- It copies by default; `--link` creates symbolic links to receive updates with `git pull`.
- It never overwrites a skill it did not install without `--force`; `--dry-run` shows what it would install.
- Always install the whole plugin: some skills depend on a sibling (every `qa-*` uses `qa-core`).

## Updating

When the repository publishes changes, each plugin's version goes up; without that, no tool detects them.

```bash
# Claude Code (then open a new session)
claude plugin marketplace update sv-agent-plugins; for p in general engineering qa architecture go; do claude plugin update "$p@sv-agent-plugins"; done
# OpenAI Codex
codex plugin marketplace upgrade sv-agent-plugins
# GitHub Copilot CLI
copilot plugin marketplace update sv-agent-plugins; for p in general engineering qa architecture go; do copilot plugin update "$p@sv-agent-plugins"; done
# Cursor, Windsurf or install.sh with --link: updating the clone is enough
git -C <clone-path> pull
# install.sh without --link: update the clone and run the same install.sh again
```

### Migrating from the Spanish plugin names

Until November 2026 the plugins were written in Spanish and two of them had Spanish names: `ingenieria` (now `engineering`) and `arquitectura` (now `architecture`); the skills `por-donde-empiezo` and `ingenieria-setup` are now `where-to-start` and `engineering-setup`. A renamed plugin is a new plugin for the tools, so uninstall the old ones and install the new ones:

```bash
# Claude Code
claude plugin marketplace update sv-agent-plugins
claude plugin uninstall ingenieria@sv-agent-plugins; claude plugin uninstall arquitectura@sv-agent-plugins
claude plugin install engineering@sv-agent-plugins; claude plugin install architecture@sv-agent-plugins
for p in general qa go; do claude plugin update "$p@sv-agent-plugins"; done
# Codex and Copilot: the same with `codex plugin remove`/`codex plugin add` and `copilot plugin uninstall`/`copilot plugin install`
# install.sh: delete the old folders (ingenieria-setup, por-donde-empiezo) from the skills folder and run install.sh again
```

Repositories that already use the plugins keep working, but the files the skills write changed names: `docs/agentes/` → `docs/agents/`, `GLOSARIO.md` → `GLOSSARY.md`, and the QA artifacts (`criterios.md` → `criteria.md`, `escenarios.md` → `scenarios.md`, `ESC-NN` → `SC-NN`, `H-NN` → `F-NN`, `.qa-sello.json` → `.qa-seal.json`). Rename them, or rerun `engineering-setup` and `qa-setup`. Existing seals must be recreated with `seal.py seal`: the seal format changed version.

## Using the rules in your project

The `where-to-start` skill has an `AGENTS.md` template with these plugins' rules and workflows. Ask it to "put these plugins' rules in the repo" and it copies them into your `AGENTS.md`, removing the plugins you do not use. Codex, Copilot, Cursor and Windsurf read `AGENTS.md` directly. Claude Code, in its recent versions, also loads it, but only when the project has no `CLAUDE.md`; that is why the skill puts an `@AGENTS.md` line in `CLAUDE.md`, which imports it in every case. The template is at [plugins/general/skills/where-to-start/references/AGENTS-template.md](plugins/general/skills/where-to-start/references/AGENTS-template.md).

## Global behavior rules

Skills load on demand; **behavior** rules (how you want the agent to treat you in any project) go in each tool's personal instructions file, which is always loaded. [templates/global-rules.md](templates/global-rules.md) is a starting point: grounded disagreement that always comes with alternatives, evidence instead of adjectives, flagging language that leaves the door open ("I think", "it seems to me"), no flattery.

A single source (`~/.agents/AGENTS.md`) connected to every tool:

```bash
tools/install-global-rules.sh                # creates the source from the template if missing and connects it
"${EDITOR:-nano}" ~/.agents/AGENTS.md        # adjust it to your taste; the changes reach every tool
```

| Tool | Global file | How the script connects it |
|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` | Adds an `@` line with the source's absolute path |
| Codex | `~/.codex/AGENTS.md` | Symbolic link |
| Copilot CLI | `~/.copilot/copilot-instructions.md` | Symbolic link |
| Windsurf | `~/.codeium/windsurf/memories/global_rules.md` | Symbolic link (Windsurf accepts up to 6,000 characters) |
| Cursor | Settings → Rules → User Rules | Manual: paste the content |

It does not replace an instructions file you already have: it warns you so you can merge its content into the source and run it again with `--force`, which leaves a `.bak` copy. `--dry-run` shows what it would do.

## How they work together

```
          general  ◄──── grilling, research
           ▲     ▲
  architecture ──┼──► domain-modeling (ADRs, glossary)
                 │
          engineering ──── tdd, diagnosing-bugs, codebase-design, code-review
            ▲    │         detect the language and load <language>-<role>
  qa ───────┘    ▼
  (oracle)     go  (php)  (typescript) ...    language plugins
```

- Each plugin works on its own; together they do more. If a skill another one recommends is not installed, it carries on without it and says so.
- Language plugins implement the `<language>-review`, `<language>-testing`, `<language>-debugging` and `<language>-design` skills ([contract](docs/LANGUAGE-CONTRACT.md)).
- Typical workflow with separate QA: `to-spec` → `qa-acceptance-criteria` → `qa-test-design` → `qa-test-automation` → `to-tickets` → `tdd` per ticket → `qa-verify` → `go-simplify` → `code-review` → `qa-test-the-tests` → `create-pr`. If you do not know where to start: `where-to-start`.

## Portability: design decisions

- **Unique names.** Codex, Copilot, Cursor and Windsurf install skills into flat folders, without the plugin's namespace. That is why generic skills carry a prefix (`qa-verify`, `go-testing`, `engineering-setup`), and references between skills use the bare name.
- **Standard frontmatter.** Only `name`, `description` and `license`, validated with the Agent Skills reference validator. Skills meant only for the user say so in their description, because `disable-model-invocation` is not part of the standard; Codex gets `agents/openai.yaml`.
- **Self-contained.** What is shared lives in a sibling skill (`qa-core`), not in plugin folders a loose-skills installation would not copy.
- **Neutral instructions.** Where a skill uses subagents, questions to the user or loading other skills, it says what to do if the tool does not offer that ([portability](plugins/qa/skills/qa-core/references/portability.md)).
- **A single source of manifests.** `catalog.json` → `python3 tools/build_manifests.py` generates the 24 manifests for Claude Code, Codex, Copilot and Cursor; CI fails if they drift.

## Contributing

The full rules are in [AGENTS.md](AGENTS.md). The essentials:

1. Skills follow the [Agent Skills standard](https://agentskills.io/specification): `pip install skills-ref && agentskills validate plugins/<plugin>/skills/<skill>`.
2. **Every change to a plugin bumps its version in `catalog.json`**; then `python3 tools/build_manifests.py`. Without the version bump, whoever already installed it never receives the change.
3. To try it without installing: `claude --plugin-dir ./plugins/<plugin>`.
4. CI (`.github/workflows/validate.yml`) checks manifests, versions, skills, script tests, `claude plugin validate` and the installer.

## Origin and licenses

- `general` and most of `engineering` are adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT), with tickets as local Markdown and pedagogical analogies.
- The `building-blocks` catalog comes from [proyecto26/system-design-skills](https://github.com/proyecto26/system-design-skills) (MIT), curated and corrected.
- `qa`, `go`, the rest of `architecture`, `git-commit` and `create-pr` are original.

MIT license ([LICENSE](LICENSE)).
