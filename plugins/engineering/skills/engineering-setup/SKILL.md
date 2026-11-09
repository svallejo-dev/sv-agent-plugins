---
name: engineering-setup
description: "Sets this repo up for the engineering skills: where the local specs and tickets live and where the domain documentation (glossary and ADRs) lives. Run it once per repo before using to-spec, to-tickets or code-review. Use it only when the user explicitly asks for it."
license: MIT
---

# Setup

Respond in the user's language; keep common technical terms in English.

Prepares the per-repo configuration the other skills assume:

- **Local tracker**: where specs and tickets live (Markdown files inside the repo).
- **Domain docs**: where `GLOSSARY.md` and the ADRs live, and the rules for reading them.

It is a conversation-driven skill, not a deterministic script. Explore, present what you found, confirm with the user and then write.

## Process

### 1. Explore

Look at the current state of the repo. Read what exists; do not assume:

- `CLAUDE.md` and `AGENTS.md` at the root: does either exist? Does it already have an `## Agent skills` section?
- `GLOSSARY.md` and `GLOSSARY-MAP.md` at the root, and equivalents under other names (`CONTEXT.md`, or a glossary in another language such as `GLOSARIO.md`). If one exists, offer to reuse it as is instead of creating another.
- `docs/adr/` and any `docs/adr/` inside context subfolders (`src/*/`, `internal/*/`, `services/*/`).
- `docs/agents/`: does the output of a previous run of this skill already exist?
- `.scratch/`: a sign that the local-ticket convention is already in use. Also check `.gitignore` to see whether `.scratch/` is ignored.
- Monorepo signals: several project manifests in subfolders (`go.mod`, `package.json`, `composer.json`, `pyproject.toml`), a `go.work` or `pnpm-workspace.yaml`, or `services/*` folders with their own entry point. If none appear, the repo has a single context, like almost all of them.

### 2. Present and ask

Summarize what is there and what is missing. Then go through the sections in order: one section, one answer, the next. Start each section with the recommended answer so the user can accept it with one word. Skip a section when the exploration already settled it.

**Section A: Location of specs and tickets.** Recommend `.scratch/` at the root. Accept another path if the user prefers it (for example `docs/tickets/`).

**Section B: Are the tickets versioned?** Ask only once:

> Do you want to commit the specs and tickets to git? (recommended: **yes**, so they travel with the code and serve as history)

If they say no, add the folder to `.gitignore`.

**Section C: Domain docs.** By default, **one context** (`GLOSSARY.md` + `docs/adr/` at the root); write it without asking. Offer **several contexts** (a `GLOSSARY-MAP.md` that points to one `GLOSSARY.md` per context) only if the exploration found monorepo signals, and confirm the layout.

### 3. Confirm

Show a draft of:

- The `## Agent skills` block you will add to `CLAUDE.md` or `AGENTS.md` (see step 4).
- The content of `docs/agents/tracker.md` and `docs/agents/domain.md`.

Let the user edit it before writing.

### 4. Write

**Choose the file to edit:**

- If `CLAUDE.md` exists, edit it.
- If not, and `AGENTS.md` exists, edit it.
- If neither exists, ask which one to create; do not choose for the user.

Never create `AGENTS.md` if `CLAUDE.md` already exists (or the other way round). If there is already an `## Agent skills` block, update it in place instead of duplicating it, without touching the other sections.

The block:

```markdown
## Agent skills

### Tracker

Specs and tickets as Markdown files in `<path>`. See `docs/agents/tracker.md`.

### Domain docs

<"One context" or "Several contexts">. See `docs/agents/domain.md`.
```

Then write the docs using the templates in this folder as seeds, substituting the chosen path:

- [LOCAL-TRACKER.md](./LOCAL-TRACKER.md) → `docs/agents/tracker.md`
- [DOMAIN.md](./DOMAIN.md) → `docs/agents/domain.md`

### 5. Done

Tell the user the configuration is complete and which skills will read these files (`to-spec`, `to-tickets`, `code-review`, `domain-modeling`, `tdd`, `diagnosing-bugs`). If the repo uses a language with a plugin in the `sv-agent-plugins` marketplace (for example `go`) and it is not installed, recommend it in one line. Remind them they can edit `docs/agents/*.md` by hand; they only need to run this skill again to start from scratch.
