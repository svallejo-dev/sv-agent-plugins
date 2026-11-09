# ADR format

ADRs (Architecture Decision Records) live in `docs/adr/` with sequential numbering: `0001-slug.md`, `0002-slug.md`, etc.

Create `docs/adr/` lazily: only when the first ADR is needed.

## Template

```md
# {Short title of the decision}

{1-3 sentences: the context, what we decided and why.}
```

That is all. An ADR can be a single paragraph. The value is in recording _that_ a decision was made and _why_, not in filling sections.

## Optional sections

Include them only when they add real value. Most ADRs do not need them.

- **Status** in frontmatter (`proposed | accepted | deprecated | superseded by ADR-NNNN`): useful when decisions are revisited.
- **Options considered**: only when the rejected alternatives are worth remembering.
- **Consequences**: only when there are non-obvious downstream effects.

## Numbering

Find the highest number in `docs/adr/` and add one.

## When to offer an ADR

All three conditions must hold:

1. **Hard to reverse**: changing your mind later has a real cost.
2. **Surprising without context**: a future reader will look at the code and think "why on earth did they do it this way?".
3. **The result of a real trade-off**: there were genuine alternatives and one was chosen for concrete reasons.

If a decision is easy to reverse, skip it: it just gets reverted. If it is not surprising, nobody will ask. If there was no real alternative, there is nothing to record beyond "we did the obvious thing".

### What qualifies

- **Shape of the architecture.** "We use a monorepo." "The write model is event-sourced and the read model is projected into Postgres."
- **Integration patterns between contexts.** "Subscriptions and Billing communicate through domain events, not synchronous HTTP."
- **Technologies with lock-in.** Database, message bus, auth provider, deployment platform. Not every library: only the ones that would take a quarter to replace.
- **Boundary and scope decisions.** "Customer data belongs to the Customers context; the others only reference it by ID." Explicit "no"s are worth as much as "yes"es.
- **Deliberate deviations from the obvious path.** "We use hand-written SQL instead of an ORM because X." Anything a reasonable reader would assume the other way round. It stops the next engineer from "fixing" something that was intentional.
- **Constraints the code does not show.** "We cannot use provider X because of PCI requirements." "The response must take under 200 ms because of the partner contract."
- **Rejected alternatives when the rejection is not obvious.** If gRPC was considered and REST was chosen for subtle reasons, record it; otherwise someone will propose gRPC again in six months.
