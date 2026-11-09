# Contract between `engineering` and the language plugins

The `engineering` skills are language-agnostic. When they need knowledge of a specific language, they ask a **language plugin** for it through skills with a **fixed role name**. It is the ports & adapters pattern applied to skills: `engineering` defines the port (the role and what is expected of it) and each language plugin is an adapter.

Analogy: it is a standard power socket. The appliance (`engineering`) does not know which power plant is behind it; it only knows that if the socket exists, it has power.

## Roles

| Role | Invoked by | Must provide |
|---|---|---|
| `<language>-review` | `code-review` | Review rules only for that language's files, with severity, without repeating the cross-cutting rubric. They are pasted into the prompt of that language's reviewer subagent. |
| `<language>-testing` | `tdd` | Idiomatic test shape, typical seams, preferred test doubles and commands (run a test, repeat, race detector, coverage). |
| `<language>-debugging` | `diagnosing-bugs` | The concrete command for each technique of the loop (isolate, repeat, fuzz, bisect, differential), debugger, tagged logs, benchmarks and profiling. |
| `<language>-design` | `codebase-design` | How module, interface, seam, adapter and dependency injection are expressed with the language's tools. |

A language plugin may implement only some roles. If one is missing, the agnostic skill carries on with its generic rules and says so in one line.

## Rules for the contract to work

1. **The plugin name is the language identifier** (`go`, `php`, `typescript`, `python`, `sql`) and **each role skill is called `<language>-<role>`** (`go-review`). That way the name is unique in tools without namespaces (Codex, Copilot, Cursor, Windsurf), and `go-review` exists exactly when the `go` plugin is installed. In Claude Code it appears as `go:go-review`.
2. **Role skills are model-invoked**: their description is what lets another skill find them. The frontmatter follows the Agent Skills standard (only `name`, `description` and the standard's optional fields).
3. **The description starts by saying which language and which role it covers** and names the `engineering` skill that loads it.
4. **A role skill complements, it does not repeat.** It does not copy the agnostic skill's discipline (the TDD cycle, the diagnosis phases, the cross-cutting rubric); it only brings what is specific to the language.
5. **The language's depth skills own their rules** (in `go`: `senior-go-idiomatic`, `go-design-rules`, `ddd-go-idiomatic`). The role skill points to them instead of duplicating them.

## Language detection

The agnostic skills map extensions to identifiers. If you add a language whose extension does not appear here, also add it in step 5 of `code-review` and in the "Language" section of `tdd`, `diagnosing-bugs` and `codebase-design`.

| Extensions | Identifier |
|---|---|
| `.go` | `go` |
| `.php` | `php` |
| `.ts`, `.tsx`, `.js` | `typescript` |
| `.py` | `python` |
| `.sql` | `sql` |
| `.java` | `java` |
| `.kt` | `kotlin` |

## How to add a language (example: PHP)

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

Then add the plugin to `catalog.json` and run `python3 tools/build_manifests.py`: it generates the manifests for Claude Code, Codex, Copilot and Cursor. Validate with `agentskills validate plugins/php/skills/*` and `claude plugin validate plugins/php`. There is no need to touch the `engineering` plugin.
