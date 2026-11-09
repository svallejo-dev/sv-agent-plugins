# Rules for contributing to sv-agent-plugins

This file is for whoever edits this repository, person or agent. To use the plugins in another project, the AGENTS.md template is at `plugins/general/skills/where-to-start/references/AGENTS-template.md`, and the `where-to-start` skill installs it.

Everything in this repository is written in English: skills, references, scripts, docs and evals. Skills tell the agent to respond in the user's language. Talk to the person editing in their own language.

## Structure

- `plugins/<plugin>/skills/<skill>/SKILL.md`: one folder per skill, with `references/`, `scripts/` or `agents/` if it needs them.
- `catalog.json`: the **single source** of the plugins' names, versions, descriptions and categories.
- Manifests (`plugin.json`, `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.agents/plugins/`, `.github/plugin/`): **generated**. They are not edited by hand; they are regenerated with `python3 tools/build_manifests.py`.
- `install.sh`: installation of loose skills (Windsurf and any skills folder).
- `templates/global-rules.md` and `tools/install-global-rules.sh`: personal behavior rules, connected to each tool's global file. They are not part of any plugin. The template must stay under 6,000 characters (Windsurf's limit).
- `docs/LANGUAGE-CONTRACT.md`: the `<language>-<role>` contract between `engineering` and the language plugins.

## Skill rules

1. **Agent Skills standard.** Frontmatter with only `name` (equal to the folder), `description` in double quotes and `license: MIT`. No tool-specific field (for example, no `disable-model-invocation`).
2. **Unique names across the whole repository**, with a prefix when the name is generic (`qa-verify`, `go-testing`). Codex, Copilot, Cursor and Windsurf install skills into flat folders, without the plugin prefix.
3. **References between skills by bare name** (`tdd`), never `plugin:skill`.
4. **Self-contained.** Shared files live in a sibling skill (such as `qa-core`) and are linked with relative paths (`../qa-core/...`). Never in plugin folders outside `skills/`.
5. **Tool-neutral.** If a skill uses subagents, multiple-choice questions or loads other skills, it says what to do when the tool does not offer that (see `plugins/qa/skills/qa-core/references/portability.md`).
6. **English, answering in the user's language.** Every skill body says "Respond in the user's language; keep common technical terms in English." near the top.
7. **User-only skills**: the description says so ("Use it only when the user explicitly asks for it") and the folder carries `agents/openai.yaml` with `policy.allow_implicit_invocation: false` for Codex. Do not add it to a skill another skill must be able to trigger through its description.
8. Each skill is validated with `agentskills validate plugins/<plugin>/skills/<skill>` (`pip install skills-ref`).

## Versions: no version bump, no update

Claude Code, Codex and Copilot store each plugin by version number. **If you change any file of a plugin and do not bump its version in `catalog.json`, nobody receives the change.** Verified: `claude plugin update` answers "already at the latest version".

- Fix → patch (`0.2.0` → `0.2.1`); new skill or behavior change → minor (`0.3.0`); renaming or removing a skill → minor while we are on `0.x`, and note it in the commit.
- Then: `python3 tools/build_manifests.py`.
- CI checks it with `python3 tools/check_versions.py --base origin/main`.

## Before committing

```bash
python3 tools/build_manifests.py --check
python3 tools/check_versions.py --base origin/main
for d in plugins/*/skills/*/; do agentskills validate "$d"; done
python3 -m unittest discover -s plugins/qa/skills/qa-core/scripts/tests
python3 -m unittest discover -s plugins/architecture/skills/capacity-estimation/scripts -p 'test_*.py'
claude plugin validate .
```

To try a plugin without installing it or bumping its version: `claude --plugin-dir ./plugins/<plugin>`.

## Attribution

`general` and most of `engineering` were adapted from mattpocock/skills, and `building-blocks` from proyecto26/system-design-skills, both MIT-licensed. When adapting third-party content, credit it in the plugin's README and in `LICENSE`.
