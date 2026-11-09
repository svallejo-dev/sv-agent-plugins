# ingenieria

Flujo de ingeniería agnóstico al lenguaje del marketplace `sv-agent-plugins`: `ingenieria-setup`, `grill-with-docs`, `domain-modeling`, `to-spec`, `to-tickets`, `tdd`, `diagnosing-bugs`, `codebase-design`, `code-review`, `git-commit` y `create-pr`.

- Lo específico de cada lenguaje lo aportan los plugins de lenguaje (`go`, ...) a través de las skills de rol `<lenguaje>-review`, `<lenguaje>-testing`, `<lenguaje>-debugging` y `<lenguaje>-design`. Si no hay plugin para un lenguaje, las skills siguen con sus reglas genéricas.
- `grill-with-docs` usa `grilling`: instala también el plugin `general`.
- Ejecuta la skill `ingenieria-setup` una vez por repo.

Basado en [mattpocock/skills](https://github.com/mattpocock/skills) (MIT) y en las skills propias `git-commit`, `create-pr` y `review-pr`.

## Instalación

Ver el [README del repositorio](../../README.md#instalación) para Claude Code, Codex, GitHub Copilot, Cursor y Windsurf. En resumen, con Claude Code:

```bash
claude plugin marketplace add svallejo-dev/sv-agent-plugins
claude plugin install ingenieria@sv-agent-plugins
```


Todas las skills responden en español y conservan en inglés los términos técnicos habituales. Licencia MIT.
