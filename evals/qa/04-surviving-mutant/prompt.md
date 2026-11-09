# Case 04: a mutant that survives

## Test repo setup

The token BFF from case 01, already fixed: it requests the right variant per flow and caches with the key `(flow, buyer)`. The acceptance suite has SDK scenarios per flow and expiration scenarios, but **none** requests tokens for two different buyers.

`docs/agents/qa.md` with the suite command for mutants (rung 1) and a timeout.

## Instruction to the agent

"Check whether our acceptance suite has teeth before the PR."
