---
name: qa-acceptance-criteria
description: "Turns a spec or a ticket into acceptance criteria verifiable from the outside, each with its oracle; applies the usage-oracle rule (if someone else consumes the result, the consumer decides), makes implicit criteria explicit and runs a criteria premortem. Use it when the user asks for \"acceptance criteria\", \"definition of done for the feature\", or before designing QA scenarios."
license: MIT
---

# Acceptance criteria

Respond in the user's language; keep common technical terms in English.

An acceptance criterion is a statement about behavior **observable from the outside** that, if false, means the feature is useless. It is the first piece of the oracle: if the criterion is weak, everything built on top of it (scenarios, tests, verification) inherits that weakness, with every test green.

**Analogy:** the criterion is the exam question. If the question is "did the student write something?", everybody passes. If it is "does the answer open the right door?", only those who understood pass.

First read [../qa-core/references/role-model.md](../qa-core/references/role-model.md) and the format in [../qa-core/references/formats.md](../qa-core/references/formats.md) (section 2).

## 0. Preconditions

- Read `docs/agents/qa.md`. If it does not exist, tell the user to run the `qa-setup` skill and stop.
- Read the whole spec (`.scratch/<feature>/spec.md`) and, if it exists, `.scratch/<feature>/qa/handoff.md`. The handoff's "Consumers of the result" section is this skill's most important input.
- **Contamination rule.** If this session read or wrote the feature's production code, **do not write the criteria here**: launch a subagent with a clean context and the brief below for steps 1 to 4. Whoever knows the implementation can no longer imagine how it fails. Steps 5 (premortem) and 6 (approval) are always done by the main session: a subagent cannot launch other subagents or talk to the human. The rule is good faith: no gate checks what the session read.

Subagent brief:

"You are QA for the feature <feature>. Your job is to write acceptance criteria verifiable from the outside. Read ONLY these files: <spec>, <handoff if it exists>, <API contracts>, and the qa plugin references I give you. Do not read production code or the diff, and do not ask to see them. Follow steps 1 to 4 of the qa-acceptance-criteria skill and return the full content of criteria.md in draft status, plus the list of open questions and of inferred criteria."

## 1. Extract the candidates

Go through the spec in this order and note one candidate per behavior:

1. **User stories**: each one produces at least one happy-path criterion.
2. **Implementation decisions** with an observable effect (a limit, an error code, an order, an expiration time).
3. **Out of scope**: produces negative criteria ("it is not allowed to…", "it does not expose…") when the boundary matters.
4. **Consumers of the result** (handoff): each consumer produces a criterion with its usage oracle (step 3).

## 2. Make each criterion verifiable

Each criterion passes these six tests. If it fails one, rewrite it or split it:

| Test | Bad | Good |
|---|---|---|
| **Observable from the outside** | "It is stored in the devices table" | "The device appears in the customer's listing" |
| **A single behavior** | "Registers, validates and notifies" | Three criteria |
| **Concrete data** | "Respects the limit" | "With 5 devices registered, a sixth is rejected with 409" |
| **Named oracle** | "Works correctly" | "Oracle: the listing returns 5 items and the response is 409" |
| **Independent of the implementation** | "Uses the Redis cache" | "A second request in under 1 s returns the same token" |
| **Traceable source** | — | "Source: story 4" or "inferred" |

An "inferred" criterion (not in the spec) is valid, but it **requires the human's explicit confirmation**: it may be a requirement nobody wrote down or an invention of yours.

## 3. Apply the usage-oracle rule

**If the system produces something someone else consumes (a token, an event, a file, a webhook, an email), the criterion is verified with the real consumer, not with the shape of the artifact.**

- Bad: "The endpoint returns a non-empty token".
- Good: "The returned token lets the payments SDK initialize and complete a checkout in sandbox".

The shape (that it is a JWT, that it has some field) may be an additional criterion, never the only one. It is the rule that prevents the most expensive bugs and the one most often forgotten. Cases and patterns in [references/usage-oracle.md](references/usage-oracle.md).

If the handoff does not say who consumes a result, **ask**: it is a mandatory piece of the contract.

## 4. Make implicit criteria explicit

Specs almost never write down these properties, and they are the ones that fail in production. For each one, decide with the human whether it applies; if it does, it is a criterion with `Source: inferred`:

- **Idempotency**: does repeating the same request produce the same effect only once?
- **Authorization**: can an actor see or modify another actor's resources?
- **Dependency failure**: what does the user see if a dependency is slow, fails or answers partially?
- **Boundaries**: minimum, maximum and empty values, sizes, quantities.
- **Concurrency**: two simultaneous requests on the same resource.
- **Time**: expirations, windows, time zones, skewed clocks.
- **Third-party variants**: if a third party returns different things depending on parameters or flow, which variant does each flow need? (see the third-party checklist in `qa-test-design`).
- **Sensitive data**: what must not appear in responses, logs or errors.

If the feature fits an archetype in `business-archetypes` and that plugin is available, use its invariants and typical failure modes as an additional source.

## 5. Criteria premortem

Mandatory in solo mode; recommended in duo mode.

Question: **"Six months later, this feature failed in production and every criterion was green. Why?"**

Launch 3 subagents in parallel, each with the spec, the draft criteria and a different angle:
1. The end user and the business.
2. The consumers and third-party integrations.
3. Operations: failures, data, time, deployment.

> **Portability:** if your tool has no subagents, follow [../qa-core/references/portability.md](../qa-core/references/portability.md) and declare it in the artifact.

Assignment: "Write 3 concrete stories of how this feature failed in production even though all these criteria passed. For each story: what happened, which criterion was missing or which oracle was weak, and the criterion that would have caught it. Under 400 words. Respond in the user's language."

Each story ends in a new criterion, a strengthened oracle or a justified discard. The several agents give diversity of hypotheses; the measured benefit of the premortem (less overconfidence) only appears if **the human reads the stories and decides**.

## 6. Write and ask for approval

- Write `.scratch/<feature>/qa/criteria.md` in the format of [../qa-core/references/formats.md](../qa-core/references/formats.md), `Status: draft`.
- Present to the human, in this order:
  1. The **open questions**: spec ambiguities that block a criterion.
  2. The **inferred** criteria that need confirmation.
  3. The criteria with a **usage oracle**.
  4. The rest, grouped by story.
- Iterate until the human approves. Only they change the line to `Status: approved`. **Never approve yourself**, not even if the human says "whatever you say": in that case, point out the three highest-risk criteria and ask for confirmation of those.

Next step: `qa-test-design`.
