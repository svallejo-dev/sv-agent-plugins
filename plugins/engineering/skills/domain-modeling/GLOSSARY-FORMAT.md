# GLOSSARY.md format

## Structure

```md
# {Context name}

{One or two sentences: what this context is and why it exists.}

## Language

**Device**:
A physical piece of equipment (Smart TV, phone, set-top box) registered to a Customer.
_Avoid_: terminal, appliance, unit

**Subscription**:
A Customer's right to consume content during a paid period.
_Avoid_: plan, membership

**Customer**:
A person who takes out Subscriptions and registers Devices.
_Avoid_: user, account, subscriber
```

## Rules

- **Be opinionated.** When several words name the same concept, pick the best one and list the others under `_Avoid_`.
- **Short definitions.** One or two sentences at most. Define what the term IS, not what it does.
- **Only terms specific to this context.** General programming concepts (timeouts, error types, utilities) do not go in even if the project uses them a lot. Before adding a term, ask: is it a concept unique to this domain or a general one? Only the former goes in.
- **Group under subheadings** when natural groups appear. If every term belongs to one cohesive area, a flat list is enough.
- **Language.** Write the terms in the language the business uses. If the code uses a different name for the term (for example the business says `Dispositivo` and the code says `Device`), state it in the definition so the mapping is explicit.

## One context or several

**One context (most repos):** a `GLOSSARY.md` at the repo root.

**Several contexts:** a `GLOSSARY-MAP.md` at the root lists the contexts, where they live and how they relate:

```md
# Glossary map

## Contexts

- [Subscriptions](./src/subscriptions/GLOSSARY.md): sign-ups, renewals and cancellations
- [Billing](./src/billing/GLOSSARY.md): charges to payment methods and retries
- [Devices](./src/devices/GLOSSARY.md): registration and per-Customer device limits

## Relationships

- **Subscriptions → Billing**: Subscriptions emits `RenewalRequested`; Billing consumes it to create the charge
- **Billing → Subscriptions**: Billing emits `ChargeDeclined`; Subscriptions suspends after N retries
- **Devices ↔ Subscriptions**: they share `CustomerID`
```

Infer which structure applies:

- If `GLOSSARY-MAP.md` exists, read it to find the contexts.
- If only a `GLOSSARY.md` exists at the root, there is one context.
- If neither exists, create a `GLOSSARY.md` at the root when the first term is resolved.

With several contexts, infer which one the current topic refers to. If it is not clear, ask.
