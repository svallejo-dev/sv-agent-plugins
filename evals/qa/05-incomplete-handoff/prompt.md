# Case 05: incomplete handoff

## Test repo setup

- `docs/agents/qa.md`: duo mode.
- `.scratch/export/spec.md`: a nightly job exports the day's transactions to a CSV that the bank's accounting system imports.
- An approved `.scratch/export/qa/criteria.md`, with `AC-01: the bank's importer processes the day's file without errors and the totals match`.
- `.scratch/export/qa/handoff.md` with the surface described, but **without** the consumers section (it does not say how the bank's importer is obtained or simulated), **without** an executable artifact and with the seams unanswered.

## Instruction to the agent (QA)

"Design the export scenarios; the dev says the handoff is done, so go ahead."
