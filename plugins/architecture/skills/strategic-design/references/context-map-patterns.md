# Context map patterns

The relationship patterns between contexts from Domain-Driven Design (Evans, _Domain-Driven Design_, 2003; Vernon, _Implementing Domain-Driven Design_, 2013). Each relationship has an **upstream** (the one that publishes or provides) and a **downstream** (the one that consumes and depends).

| Pattern | What it is | Analogy | Use it when | Risk |
|---|---|---|---|---|
| **Partnership** | Two teams coordinate their changes and deliver together; shared success or failure. | Two partners who co-sign every decision. | Two contexts tightly coupled by a common goal and teams that talk daily. | It becomes a permanent mutual dependency; it does not scale to many teams. |
| **Shared Kernel** | A small subset of the model (types, a library) shared and co-managed. | A party wall between two houses. | Concepts that are truly identical on both sides and coordinated teams. | It grows into a shared monolith; any change needs both. Keep it tiny. |
| **Customer-Supplier** | The downstream (customer) negotiates its needs and the upstream (supplier) plans for them. | A supplier serving the orders of an important customer. | The upstream has incentives to serve the downstream (same company, aligned priorities). | If the upstream does not deliver, the downstream is blocked. Agree on contracts and contract tests. |
| **Conformist** | The downstream adopts the upstream's model as is, without translating. | Using the bank's form even if you do not like it. | The upstream is not going to change for you and its model is acceptable. | The foreign model leaks into your domain; if it is bad, it contaminates you. |
| **Anticorruption Layer (ACL)** | The downstream translates the upstream's model into its own in an isolated layer. | A translator at the border who stops the foreign language from entering the country. | The upstream is legacy, a third party or has a model you do not want to inherit; integrations with external providers; migrations. | The cost of maintaining the translation; it can hide business logic if neglected. |
| **Open Host Service (OHS)** | The upstream offers an API or protocol designed for many consumers. | A public service office with a standard counter. | An upstream with several consumers that cannot negotiate with each one. | If the API is poor, every consumer suffers it; it needs versioning. |
| **Published Language (PL)** | A documented exchange language (event schemas, a standard format). It usually goes with OHS. | The official language of documents between countries. | Domain events between contexts, integrations with industry standards. | Evolving it requires backward compatibility and schema governance. |
| **Separate Ways** | The contexts do not integrate; each solves its own problem. | Two neighbors who decide to share nothing. | The cost of integrating exceeds the benefit. | Duplicated data and logic. |
| **Big Ball of Mud** | It is not a pattern to choose: it is acknowledging an area without clear boundaries. | The storage room where everything is mixed up. | To honestly **name** a legacy area on the AS-IS map. | Put an ACL around it and do not let the mess spread. |

## Frequent combinations

- **OHS + PL in the upstream, ACL in each downstream**: the healthy shape of an event bus with many consumers. The upstream publishes versioned events; each consumer translates into its own model.
- **ACL + strangler fig** to get out of a legacy: the ACL protects the new model while the strangler moves capabilities from the old system to the new one.
- **Conformist towards a generic**: with a standard authentication or payments provider, it is sometimes reasonable to conform to its model in a thin adapter, instead of a full ACL.

## Signs of a sick map

- Two contexts write the same tables: the boundary is fictitious.
- A "common service" or a "shared database" everyone touches: an uncontrolled Shared Kernel.
- Events with the producer's internal model (every column of the table) instead of business facts: a Published Language is missing.
- A business change requires deploying several services at once: the boundary cuts through an invariant or an area that changes together.
- A team depends on another for almost everything and has no aligned incentives: Customer-Supplier without a contract, which in practice is Conformist.
