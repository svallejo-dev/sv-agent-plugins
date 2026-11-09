# Domain docs

How the engineering skills should consume this repo's domain documentation when exploring the code.

## Before exploring, read this

- **`GLOSSARY.md`** at the root, or
- **`GLOSSARY-MAP.md`** at the root if it exists: it points to one `GLOSSARY.md` per context. Read the ones relevant to the topic.
- **`docs/adr/`**: read the ADRs that touch the area you are going to work on. In repos with several contexts, also check `docs/adr/` inside each context.

If any of these files does not exist, **carry on silently**. Do not flag its absence or suggest creating it upfront. The `domain-modeling` skill (via `grill-with-docs`) creates them when a term or a decision is actually resolved.

## Structure

One context (most repos):

```
/
├── GLOSSARY.md
├── docs/adr/
└── src/
```

Several contexts (there is a `GLOSSARY-MAP.md` at the root):

```
/
├── GLOSSARY-MAP.md
├── docs/adr/                          ← system-wide decisions
└── src/
    ├── subscriptions/
    │   ├── GLOSSARY.md
    │   └── docs/adr/                  ← the context's decisions
    └── billing/
        ├── GLOSSARY.md
        └── docs/adr/
```

## Use the glossary's vocabulary

When your output names a domain concept (a ticket title, a refactor proposal, a hypothesis, a test name), use the term as `GLOSSARY.md` defines it. Do not drift to synonyms the glossary marks as `_Avoid_`.

If the concept you need is not in the glossary, that is a signal: either you are inventing language the project does not use (reconsider it) or there is a real gap (note it for `domain-modeling`).

## Flag conflicts with ADRs

If your output contradicts an existing ADR, say so explicitly instead of ignoring it:

> _Contradicts ADR-0007 (device events via Kafka), but it is worth reopening because…_
