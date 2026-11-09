# go

Dominio Go del marketplace `sv-agent-plugins`.

- **Profundidad**: `senior-go-idiomatic`, `go-design-rules`, `ddd-go-idiomatic`.
- **Roles para el plugin `ingenieria`**: `go-review` (lo carga `code-review`), `go-testing` (`tdd`), `go-debugging` (`diagnosing-bugs`) y `go-design` (`codebase-design`). Ver el [contrato de lenguajes](../../docs/CONTRATO-LENGUAJES.md).

Funciona solo, pero rinde más con `ingenieria` instalado.

## Instalación

Ver el [README del repositorio](../../README.md#instalación) para Claude Code, Codex, GitHub Copilot, Cursor y Windsurf. En resumen, con Claude Code:

```bash
claude plugin marketplace add svallejo-dev/sv-agent-plugins
claude plugin install go@sv-agent-plugins
```


Todas las skills responden en español y conservan en inglés los términos técnicos habituales. Licencia MIT.
