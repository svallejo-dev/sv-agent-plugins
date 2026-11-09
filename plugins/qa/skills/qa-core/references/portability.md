# Portability across tools

The skills in this repository follow the Agent Skills standard (`SKILL.md`) and work in Claude Code, OpenAI Codex, GitHub Copilot, Cursor and Windsurf. Some instructions depend on capabilities that each tool offers differently. This page says how to fulfil them in each one and what to do if a capability does not exist.

**General rule:** if your tool does not offer a capability, do not simulate it silently. Apply the alternative below and **declare it** in the artifact you produce (report, criteria, scenarios): honesty about isolation is part of the rigor.

## Subagents with a clean context

Several skills ask you to launch subagents in parallel (design techniques, premortem, reviewers, red team) or to delegate to a "clean" subagent that has not seen the code.

| If your tool… | Do this |
|---|---|
| Has subagents (in Claude Code, the Agent tool; in others, their subagent or custom-agent mechanism) | Launch them as the skill says, with the exact brief and only the material indicated |
| Has no subagents, but you can open a new conversation | Run each assignment in a new conversation, pasting only the brief and the material indicated; bring the output back |
| Has neither | Run the assignments one after another in the same session and **declare** "no context isolation" in the artifact. In QA solo mode, this lowers the information barrier to N1 at most |

## Questions to the user

If your tool has a multiple-choice question mechanism (in Claude Code, AskUserQuestion), use it. If not, ask in text, numbering the options, and wait for the answer.

## Loading another skill

When a skill says "invoke the `X` skill" or "load `X`":
- In Claude Code, with the Skill tool. If the plugin is installed as a plugin, its name appears with a namespace: `qa:qa-verify`, `engineering:tdd`.
- In the other tools, mention it by name (`qa-verify`, `tdd`) or read its `SKILL.md` in the sibling folder.

If the skill is not installed, carry on without it and say so in one line, as each skill indicates.

## Running scripts

The scripts need a tool that can run commands in a terminal (all the ones listed can, with the user's permission). If the session cannot run commands, the skill cannot go through the deterministic gates: say so and do not declare any gate as passed.
