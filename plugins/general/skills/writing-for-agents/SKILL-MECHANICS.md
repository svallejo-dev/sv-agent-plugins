# Skill mechanics

The skill-specific branch of [writing-for-agents](SKILL.md): what changes when the document is a skill (frontmatter, invocation choice and router skills). Everything else about how to write it is the universal reference in `SKILL.md`.

## Invocation

Two options, which trade the two loads:

- A **model-invoked** skill keeps its `description`, so the agent can fire it on its own and other skills can reach it. You can still type its name: model invocation always _includes_ the user's reach; a description only adds discovery by the agent, it never takes away the human's. The description is the skill's main context pointer and it is forced to be always loaded: permanent context load in exchange for discoverability. A model-invoked skill whose content is all reference also works as a home for shared reference: another skill can invoke it, so the reference several skills need lives in one place. Mechanics: write a description for the model with the triggering branches (the pointer rules of `SKILL.md` apply in full).
- A **user-invoked** skill takes the description out of the agent's reach: only the human typing its name can invoke it, and no other skill can. Zero context load, but it spends cognitive load: you are the index that must remember it exists. Mechanics: in Claude Code, `disable-model-invocation: true`; in Codex, `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. The `description` becomes for humans: a one-line summary, with no trigger lists. (In this repository the standard frontmatter does not allow tool-specific fields, so user-only skills say "Use it only when the user explicitly asks for it" in their description and carry `agents/openai.yaml`.)

Choose model invocation only when the agent must reach the skill on its own, or another skill must. If it is only fired by hand, make it user-invoked and do not pay context load.

Shared reference that two user-invoked skills need cannot live in either of them: without a description, neither can fire the other. Move it to a plain file outside the skill system: external reference any skill can point to.

## Plugins and portability

Inside a Claude Code plugin, skills get a namespace (`engineering:tdd`). The other tools (Codex, Copilot, Cursor, Windsurf) install skills into flat folders and invoke them by their bare name. For a skill to work in all of them:

- Give it a **unique, specific name** (`qa-verify`, not `verify`; `go-testing`, not `testing`): in a flat folder two skills with the same name clash.
- When a skill invokes another, use the **bare name** (`tdd`, `grilling`), not `plugin:skill`.
- Follow the Agent Skills standard in the frontmatter: only `name` (equal to the folder), `description` (quoted if it contains `: `), and the optional `license`, `compatibility`, `metadata` and `allowed-tools`. Tool-specific fields, such as `disable-model-invocation`, make the standard's validator reject it.
- If several skills share references or scripts, put them in a sibling base skill (`qa-core`) and link it with relative paths (`../qa-core/...`), not in plugin folders that a loose-skills installation does not copy.

## Splitting by invocation

The cut by invocation (the cut by sequence is in `SKILL.md`): split off a model-invoked skill when you have a distinct leading word that must fire it on its own (a word you really use in your prompts), or another skill needs to reach it. You pay context load for the new always-loaded description, so that independent reach has to be worth it.

## Router skills

When user-invoked skills multiply beyond what you can remember, that accumulated cognitive load is cured with a **router skill**: a user-invoked skill that names the others and when to reach for each, so the human has a single skill to remember instead of many. It can only suggest, never fire them: user-invoked skills have no description, so nothing but the human can reach them.
