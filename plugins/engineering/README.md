# engineering

Language-agnostic engineering workflow of the `sv-agent-plugins` marketplace: `engineering-setup`, `grill-with-docs`, `domain-modeling`, `to-spec`, `to-tickets`, `tdd`, `diagnosing-bugs`, `codebase-design`, `code-review`, `git-commit` and `create-pr`.

- Language-specific work comes from the language plugins (`go`, ...) through the role skills `<language>-review`, `<language>-testing`, `<language>-debugging` and `<language>-design`. If there is no plugin for a language, the skills carry on with their generic rules.
- `grill-with-docs` uses `grilling`: install the `general` plugin too.
- Run the `engineering-setup` skill once per repo.

Based on [mattpocock/skills](https://github.com/mattpocock/skills) (MIT) and on the author's own skills `git-commit`, `create-pr` and `review-pr`.

## Installation

See the [repository README](../../README.md#installation) for Claude Code, Codex, GitHub Copilot, Cursor and Windsurf. In short, with Claude Code:

```bash
claude plugin marketplace add svallejo-dev/sv-agent-plugins
claude plugin install engineering@sv-agent-plugins
```

All skills respond in the user's language. MIT license.
