# Migration patterns

How to get from a current state to a target one without stopping the system. Each step of the path must be deployable on its own, verifiable with a concrete signal and, whenever possible, reversible.

**Doors**: a step is a **two-way door** if it can be reverted cheaply (changing a route, turning off a flag) and a **one-way door** if not (deleting data, publishing a format others already consume, ending a contract). One-way doors go at the end of the path, after the signals confirm success, and with an ADR.

| Pattern | What it is | Analogy | Use it when | Risk and care |
|---|---|---|---|---|
| **Strangler fig** | A facade in front of the old system routes capability by capability to the new one, until the old one can be turned off | The fig tree that grows around the host tree until it replaces it | Replacing a monolith or a legacy service piece by piece | The facade becomes permanent; decide when to stop ("what is left is good enough") |
| **Branch by abstraction** | Introduce an abstraction in the code, implement the new thing behind it and switch the implementation without a long-lived branch | Changing the engine with the car running, through a coupling | Replacing a library or an internal component | The temporary abstraction must be deleted at the end |
| **Expand-contract** (parallel change) | Add the new form next to the old one, migrate the consumers, delete the old one | Building the new bridge next to the old one before demolishing it | Schema changes, API contract or event changes | Keeping both forms has a cost; the "contract" phase is one-way |
| **Transactional outbox / CDC** | Write the state and the event in the same local transaction (outbox) or read the database log (CDC) | A receipt printed by the same operation that charges | Publishing events from an existing system without dual-write | Ordering and duplicates: consumers must be idempotent |
| **Dual-write** | Write to the old and the new store from the application | Keeping two notebooks at once | Almost never: only with reconciliation and if there is no other option | Without a shared transaction, the two stores diverge; prefer outbox or CDC |
| **Backfill** | Copy the historical data to the new store while new data arrives through the new path | Moving the old files while the new mail already goes to the new house | Any data migration | Throttle it so it does not knock over the source; idempotent and resumable |
| **Shadow traffic** (dark launch) | The new system receives a copy of the real traffic and its responses are discarded | A dress rehearsal with a real audience that does not see the stage | Validating load and behavior with no risk to the user | Beware of side effects (writes, charges, notifications): disable them in the shadow |
| **Dual-run with comparison** | Old and new process the same thing; the results are compared and the differences recorded; the old one is still the truth | The old system acts as the oracle | Migrations of business logic (rewrites across languages or stacks) | Expected differences (format, order) must be normalized before comparing |
| **Canary and progressive rollout** | The change reaches a small percentage, it is measured against the SLO and widened or reverted | Tasting a spoonful before serving the whole pot | Any risky change, configuration included | Choose the canary population well (not just internal traffic) |
| **Feature flags** | Turn on the new path per segment, without a deploy | One switch per room | Separating deploying from releasing; instant rollback | Flag debt: every flag has a deletion date |
| **Cutover** | The moment the new one becomes the truth | Changing your address at the registry office | At the end, with success criteria met and a rollback plan | If it is one-way, rehearse it and have a runbook |

## Shape of a migration path

```markdown
| Step | What changes | Pattern | Success signal | Door | Rollback |
|---|---|---|---|---|---|
| 1 | Facade in front of the legacy, 100 % to the legacy | Strangler | Latency +<5 ms p99 | Two-way | Remove the facade |
| 2 | Capability A in the new service, in shadow | Shadow + dual-run | <0.1 % differences over 7 days | Two-way | Turn off the shadow |
| 3 | Capability A at 5 % → 50 % → 100 % | Canary + flag | SLO intact | Two-way | Flag at 0 % |
| 4 | Delete A's code and data in the legacy | Contract | 30 days with no traffic on the old route | **One-way** | Restore from backup (ADR) |
```
