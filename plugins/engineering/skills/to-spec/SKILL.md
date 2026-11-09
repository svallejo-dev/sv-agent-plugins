---
name: to-spec
description: "Turns the current conversation into a spec (PRD) and saves it to the local tracker, without an interview, only synthesizing what was already discussed. Use it only when the user explicitly asks for it."
license: MIT
---

Respond in the user's language; keep common technical terms in English.

This skill takes the conversation's context and what you know about the code and produces a spec. Do NOT interview the user: synthesize what you already know. (If understanding is missing, the previous step was `grilling` or `grill-with-docs`.)

Read `docs/agents/tracker.md` to know where to save the spec. If it does not exist, tell the user to run the `engineering-setup` skill and stop.

## Process

1. Explore the repo to understand the current state of the code, if you have not already. Use the vocabulary of `GLOSSARY.md` throughout the spec and respect the ADRs of the area you are going to touch.

2. Sketch the **seams** at which you will test the feature. Prefer existing seams over new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams the better: ideally one. (Seam: the point where you can observe or change behavior without editing that point; usually a module's public interface or an HTTP endpoint.)

   Confirm with the user that those seams match what they expect.

3. Write the spec with the template below and save it to `<tracker-path>/<feature-slug>/spec.md` with the line `Status: ready-for-agent`.

<spec-template>

# <Feature title>

Status: ready-for-agent

## Problem

The problem the user faces, from their perspective.

## Solution

The solution to the problem, from the user's perspective.

## User stories

A LONG, numbered list of user stories, in this format:

1. As a <actor>, I want <capability>, so that <benefit>

<story-example>
1. As a streaming service customer, I want to see which devices I have registered, so that I can free one up when I reach the limit
</story-example>

The list must be very extensive and cover every aspect of the feature.

## Implementation decisions

A list of the implementation decisions made. It may include:

- The modules (packages, services) that are built or modified
- The interfaces of those modules that change
- Technical clarifications from the developer
- Architecture decisions
- Schema changes
- API contracts
- Concrete interactions between services

Do NOT include file paths or code snippets: they go stale very fast.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose (a state machine, a schema, the shape of a type), include it inside the corresponding decision and say it comes from a prototype. Trim it to what holds the decision, not to a working demo.

## Consumers of the result

Who consumes what this feature produces (a token, an event, a file, an API response) and how that consumer validates that it works for them. It is the **usage oracle**: if someone else consumes the result, the real consumer decides whether it works, not the shape of the artifact.

| Consumer | What it consumes | How it validates that it works for them |
|---|---|---|

If a third party returns different variants depending on parameters or flow (token types, API versions), note here which variant each flow needs, or leave it as an open question.

## Testability

The seams the system exposes so it can be tested from the outside. Answer each one: available, no, or not applicable.

- Data seeding through an API or a setup endpoint in non-production environments
- Controllable clock (expirations, time windows)
- Dependencies configurable by variable (for fakes and network failures)
- Test data isolation (tenant or test accounts) and cleanup
- Accessible observability: trace-id or correlation-id in responses and logs

A missing seam does not block the spec, but it leaves scenarios that cannot be tested: it is explicit debt.

## Testing decisions

A list of the testing decisions made. Include:

- What makes a good test (external behavior only, not implementation details)
- Which modules are tested and at which seam
- Prior art (similar tests that already exist in the code)

## Out of scope

What is left out of this spec.

## Notes

Any other notes about the feature.

</spec-template>

4. If the repo uses the `qa` plugin (`docs/agents/qa.md` exists), also write the **handoff contract** at `<tracker-path>/<feature-slug>/qa/handoff.md`, with `Status: draft` and these sections: 1. Surface (API contract or list of endpoints and events with their shape), 2. Consumers of the result (the spec's table), 3. Dependencies (own or third party, sandbox, official documentation), 4. Executable artifact (how to build the image or start the service; URLs per environment, no secrets), 5. Testability seams (the spec's, each one available, no or not applicable, and how it is used), 6. Constraints. Whatever you do not know, leave as `pending` and say so: QA will return an incomplete handoff.

5. Tell the user where the spec was saved and that the natural next step is the `to-tickets` skill with that path; if you wrote the handoff, that QA's next step is `qa-acceptance-criteria` and then `qa-test-design`, before the tickets if they want the `Scenarios:` line in each ticket.
