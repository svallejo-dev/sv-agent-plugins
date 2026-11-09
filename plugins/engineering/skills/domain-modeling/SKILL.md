---
name: domain-modeling
description: "Builds and sharpens a project's domain model. Use it when the terminology of the code or the business is being discussed, when writing or editing a GLOSSARY.md, or when recording or editing an ADR."
license: MIT
---

# Domain modeling

Respond in the user's language; keep common technical terms in English.

Actively build and sharpen the domain model while designing: challenge terms, invent edge scenarios and write down the glossary and the decisions as soon as they crystallize. (Merely _reading_ `GLOSSARY.md` to use its vocabulary is not this skill; that is a one-line habit any skill has. This skill is for when the model changes.)

Analogy: the glossary is the house dictionary and the ADRs are the minutes of the meetings where something hard to undo was decided.

## File structure

If `docs/agents/domain.md` exists (written by `engineering-setup`), follow its paths. If not, use this default layout. Most repos have a single context:

```
/
├── GLOSSARY.md
├── docs/
│   └── adr/
│       ├── 0001-device-events-via-kafka.md
│       └── 0002-postgres-for-the-write-model.md
└── src/
```

If there is a `GLOSSARY-MAP.md` at the root, the repo has several contexts and the map says where each one lives:

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

Create the files lazily: only when you have something to write. If there is no `GLOSSARY.md`, create it when the first term is resolved. If there is no `docs/adr/`, create it when the first ADR is needed.

## During the session

### Check against the glossary

When the user uses a term that clashes with the language of `GLOSSARY.md`, flag it right away: "Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term: "You say 'account': do you mean the Customer or the User? They are different things."

### Discuss concrete scenarios

When domain relationships come up, test them with specific scenarios. Invent scenarios that explore edge cases and force precision about the boundaries between concepts.

### Cross-check with the code

When the user states how something works, check whether the code agrees. If you find a contradiction, show it: "Your code cancels whole Subscriptions, but you just said partial cancellation is possible. Which is right?"

### Update GLOSSARY.md on the spot

When a term is resolved, update `GLOSSARY.md` right there, without batching changes. Use the format in [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).

`GLOSSARY.md` contains no implementation details. It is not a spec, a draft or a log of technical decisions: it is a glossary and nothing else.

### Offer ADRs sparingly

Offer to create an ADR only when all three conditions hold:

1. **Hard to reverse**: changing your mind later has a real cost.
2. **Surprising without context**: a future reader will wonder "why did they do it this way?".
3. **The result of a real trade-off**: there were genuine alternatives and one was chosen for concrete reasons.

If any of the three is missing, there is no ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).
