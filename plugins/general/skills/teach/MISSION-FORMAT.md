# MISSION.md format

`MISSION.md` lives at the workspace root. It captures the _reason_ the user is learning the topic. Every teaching decision (what to teach next, which resources to show, which exercises to design) must be traceable back to this document.

## Template

```md
# Mission: {Topic}

## Why
{1-3 sentences. The concrete real-world goal the user is pursuing. What changes in their life or work once they have this skill? Avoid abstract framings like "understand X"; look for the underlying outcome.}

## Success looks like
- {Something specific and observable the user will be able to do}
- {Another specific thing}
- {…}

## Constraints
- {Time, budget, prior commitments, learning preferences, whatever narrows the approach}

## Out of scope
- {Adjacent topics the user does not want to pursue right now, to protect the zone of proximal development}
```

## Rules

- **One mission per workspace.** If the user wants to learn two unrelated things, those are two workspaces.
- **Concrete before abstract.** "Design the devices service in Go with safe concurrency before Q1" beats "learn concurrency". "Defend chapter 3 of the thesis" beats "know neuropsychology".
- **Push back against vagueness.** If the user cannot say why, interview them before writing anything. A bad mission is worse than none.
- **Revise when reality changes.** Missions change. When the goal moves, update the file; do not leave an old mission guiding future sessions.
- **Brief.** If `MISSION.md` takes more than a screen, it is no longer a compass but a plan.
