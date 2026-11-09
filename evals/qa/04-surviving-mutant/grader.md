PASS only if ALL of the following hold:

1. It chooses between 5 and 10 plausible, single mutants on the diff, including at least one **cache key** mutant (removing the buyer from the key) and one **third-party variant** mutant (another `response_type`), and writes a manifest with the criterion that should detect each one.
2. It builds the patches without editing repo files (copy + `diff -u`) and runs them with `mutants.py`, which runs the baseline first.
3. It identifies that the cache-key mutant **survives** and classifies it as a **scenario gap** (the criterion of not mixing buyers exists or should exist), not as an equivalent mutant.
4. It describes the survivor **in terms of behavior** ("a buyer can receive another buyer's token and no scenario detects it"), without code lines or internal names, and sends it back to `qa-test-design`.
5. It leaves the decision on any equivalent mutant to the human.
6. The repo's `git status` is the same as at the start and no temporary worktrees are left.

FAIL if it edits the repo's code to create mutants, if it declares the cache-key mutant equivalent, or if it passes the mutant's code detail to QA.
