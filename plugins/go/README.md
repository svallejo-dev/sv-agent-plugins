# go

Go domain of the `sv-agent-plugins` marketplace.

- **Depth**: `senior-go-idiomatic`, `go-design-rules`, `ddd-go-idiomatic`.
- **Simplification**: `go-simplify` cleans up Go code without changing its behavior: first deterministic tools (`gofmt -s`, `goimports`, `go fix` with the Go 1.26 modernizers, `staticcheck` S1) and then a catalog of judgment simplifications (comments, noise, nesting, errors, dead code, duplication), with green tests before and after each step.
- **Roles for the `engineering` plugin**: `go-review` (loaded by `code-review`), `go-testing` (`tdd`), `go-debugging` (`diagnosing-bugs`) and `go-design` (`codebase-design`). See the [language contract](../../docs/LANGUAGE-CONTRACT.md).

It works on its own, but does more with `engineering` installed.

## Installation

See the [repository README](../../README.md#installation) for Claude Code, Codex, GitHub Copilot, Cursor and Windsurf. In short, with Claude Code:

```bash
claude plugin marketplace add svallejo-dev/sv-agent-plugins
claude plugin install go@sv-agent-plugins
```

All skills respond in the user's language. MIT license.
