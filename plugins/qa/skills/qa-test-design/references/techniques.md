# Test design techniques

Each section is pasted in full to the subagent of its family. They are the black-box techniques of the ISTQB syllabus (Foundation and Test Analyst) plus the failure and environment ones a distributed system demands. They all serve the same purpose: **choosing systematically what to test**, so coverage does not depend on the day's intuition.

---

## Family A: equivalence partitions and boundary values

### Equivalence partitions

**What it is:** splitting each input (and each output) into classes the system should treat the same way. One representative value per class is enough; testing ten values of the same class adds no information.

**Analogy:** to check whether a coffee machine accepts coins you do not try every 50-cent coin; you try one 50-cent coin, one 1-euro coin, a foreign coin and a fake token.

**How to derive them:**
1. For each input of the criterion, list the **valid** and **invalid** classes (wrong type, empty, missing, out of range, invalid format).
2. Do the same with the **outputs**: each distinct response (201, 409, 422…) is a class that needs at least one scenario that produces it.
3. One scenario per valid class; valid classes can be combined in the same scenario. **Invalid classes, one per scenario**: if you mix two invalid ones, a rejection does not tell you which of the two caused it (masking).

### Boundary values

**What it is:** defects concentrate at the edges of partitions (`<` instead of `<=`, off-by-one errors).

**How to derive them:** for each ordered boundary, test the value right at the limit and the one immediately outside. In the **three-value** variant (recommended for critical business limits), also the one immediately inside.

Example, maximum 5 devices per customer:

```gherkin
Scenario Outline: SC-04 register with <current> devices already registered
  Given a customer with <current> registered devices
  When they register a new device
  Then the response is <status>
  And the customer ends up with <final> devices
  Examples:
    | current | status | final |
    | 0       | 201    | 1     |
    | 4       | 201    | 5     |
    | 5       | 409    | 5     |
```

Note the second assertion: the 409 alone is not enough; the oracle also checks that the sixth **was not created**.

**Boundaries people forget:** empty strings and maximum-length strings, empty and single-element lists, zero and negatives, the first and last page of a pagination, amounts with the maximum decimal precision, dates at a month or year change, the last second before an expiration.

**Common mistakes:** testing only the value inside; testing limits the spec does not define (ask before inventing one); forgetting the limits of the outputs.

---

## Family B: decision tables, state transitions and combinatorics

### Decision tables

**What it is:** when the result depends on the **combination** of several conditions, a table with one column per rule makes every combination visible, including the ones nobody specified.

**How:** list the conditions (top rows) and the actions (bottom rows); enumerate the combinations; collapse the ones that do not matter with "—"; **each column is a scenario**. A column whose action nobody knows is a **question for the spec**: that is the main value of the technique.

| Condition / action | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| New buyer | Y | Y | N | N |
| Wants to save the payment method | N | Y | — | — |
| Has a saved payment method | — | — | Y | N |
| **Token to hand over** | client_token | id_token | id_token + customer | ? |

R4 (returning buyer without a saved method) is an open question, not a scenario to invent.

### State transitions

**What it is:** when the system has named states (order, payment, subscription, session), defects live in the transitions: the valid ones that fail and, above all, the invalid ones the system accepts.

**How:**
1. Draw (or ask for) the state machine: states, events and valid transitions.
2. **Minimum coverage:** each valid transition at least once (0-switch coverage).
3. **Invalid transitions:** for each state, each event that should not be accepted in it (refunding a pending payment, cancelling one already cancelled). One per scenario.
4. **Critical sequences:** round trips (pause → resume → pause) and those that repeat an event (double capture).

If nobody can draw the machine, **that is a spec finding**.

### Combinatorics (pairwise)

**When:** many independent parameters with several values each (country × currency × method × device). Testing every combination is unfeasible; most combinatorial defects appear with the interaction of **two** parameters.

**How:** generate a set that covers every pair of values at least once with a tool (Microsoft's PICT, or the equivalent library in your language); do not do it by hand. Add combinations of known risk separately. Pairwise does **not** replace the decision table when the conditions are not independent.

---

## Family C: third-party integration and usage oracle

Use the checklist in [third-parties.md](third-parties.md) in full and the rule in [usage-oracle.md](../../qa-acceptance-criteria/references/usage-oracle.md). In short:

1. For each artifact the system produces for someone else: a scenario with the **real consumer** as the oracle (usually rung 3) and, if there is a contract, a contract scenario (rung 2).
2. For each third party: the **flow × variant** decision table of what the third party returns, the **cache key** of everything that is cached and the third party's **error catalog**.
3. **Learning tests** against the sandbox (rung 2) for each assumption about the third party that some scenario uses. For own services, a Pact contract scenario; for third parties, never Pact as a gate.
4. The **walking skeleton** as the first scenario.

---

## Family D: failures and environment

These scenarios almost always go on **rung 1**, because they require controlling the environment (Toxiproxy, fakes, clock). For each dependency in the handoff:

| Failure | Scenario | Oracle |
|---|---|---|
| High latency (above the timeout) | Toxiproxy `latency` | The system cuts off at its timeout and answers with a clean error; it does not hang |
| Connection refused or dropped | Proxy disabled, or toxic `reset_peer` / `timeout` | Clean error; it recovers when the dependency comes back |
| 5xx or 429 response | Third-party fake | Retry with backoff within the budget; 429 honors `Retry-After` |
| Slow, partial response | Toxiproxy `slicer` or `limit_data` | A truncated response is not processed as valid |
| **Timeout after the third party executed** | Fake that executes and then delays | Retrying does not duplicate the effect (idempotency) |
| Unexpected but valid response | Fake with a real variant nobody considered | It is rejected or handled explicitly; it is never silently misread |

Also:
- **Idempotency** as a metamorphic relation: applying the same request twice with the same key produces the same result and a single effect.
- **Concurrency**: two simultaneous requests on the same resource (the last seat, the same payment). The oracle is the invariant (no overselling, no double charge), not the individual response.
- **Time**: expirations just before and just after the limit; requires a controllable clock (handoff seam).
- **Data**: the resource another process deleted halfway through the flow, the record with optional fields missing, non-ASCII characters.
- If there is a business archetype, each of the archetype's **typical failure modes** is a candidate scenario.

---

## Family E: error guessing, abuse and basic security

**Error guessing** is the experience-based technique: testing where systems usually fail. It is legitimate as long as it is **systematic**: a checklist, not the inspiration of the moment.

Minimum checklist:
- **Horizontal authorization**: customer A reads, modifies or deletes a resource of customer B by changing the ID (IDOR).
- **Vertical authorization**: a user without the admin role calls an admin endpoint.
- **Hostile inputs**: very long strings, control characters, injection into fields that end up in queries or logs, JSON with extra or duplicate fields, changed types.
- **Resending and replay**: the same request sent again; the duplicate webhook; the token reused after it expired.
- **Sensitive data**: tokens, secrets or personal data in error responses, logs or messages that should not contain them.
- **Volume abuse**: no rate limit on an expensive or enumerable endpoint.
- **Previous incidents**: every past incident of the system is a regression scenario.

Contract fuzzing from the OpenAPI (Schemathesis) complements this family in the full cadence: it generates thousands of unexpected inputs no human would write.
