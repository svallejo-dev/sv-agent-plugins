# GLOSSARY.md format (teaching workspace)

`GLOSSARY.md` is the canonical language of this teaching workspace. Every explanation, exercise and log must respect its terminology. Building it is part of learning: compressing a concept into a precise definition is evidence that the user understands it.

## Structure

```md
# Glossary: {Topic}

{One or two sentences about the topic this glossary covers.}

## Terms

**Goroutine**:
A function that runs concurrently, managed by the Go runtime and not by the operating system.
_Analogy_: an extra waiter the restaurant hires on the spot and lets go when the order is done.
_Avoid_: thread (they are different things)

**Data race**:
Two goroutines access the same variable without synchronization and at least one of them writes.
_Analogy_: two people editing the same spreadsheet cell without seeing each other.
_Avoid_: race condition (broader: not every race condition is a data race)

**Happens-before**:
The relation in Go's memory model that guarantees the effects of one operation are visible to another.
_Analogy_: the "received" stamp that proves the letter arrived before it was answered.
_Avoid_: execution order
```

## Rules

- **Add a term only when the user understands it.** The glossary records compressed knowledge; it is not a dictionary for learning. If the concept was just introduced, wait until the user uses it correctly.
- **Canonical term + analogy.** Each entry carries its precise definition and, under `_Analogy_`, the simile that helped understand it. The definition is what stays; the analogy is the scaffolding.
- **Be opinionated.** When several words name the same concept, pick the best one and list the rest under `_Avoid_`.
- **Short definitions.** One or two sentences. Define what the term IS, not what it does or how it is used.
- **Use glossary terms inside the definitions.** Once a term is in the glossary, use it everywhere, even inside other definitions.
- **Group under subheadings** when natural groups appear. A flat list is enough if the terms are cohesive.
- **Mark ambiguities.** If the field uses a term loosely, write down the resolution: "In this workspace, 'concurrency' never means parallelism."
- **Revise as understanding deepens.** A definition from week one may be wrong in week six. Update it in place; do not leave stale entries.
