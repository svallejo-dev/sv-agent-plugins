---
name: qa-test-the-tests
description: "Tests the acceptance suite by injecting plausible bugs (mutants) into the diff's code, in temporary worktrees that never touch the repo, and reports which bugs survive; each survivor is a concrete gap in the scenarios. Use it when the user asks \"are the tests any good?\", \"does the suite have teeth?\", asks for \"mutation testing\", \"bug injection\" or \"testing the tests\", and as a gate of the full cadence (mandatory in solo mode)."
license: MIT
---

# Testing the tests

Respond in the user's language; keep common technical terms in English.

If nobody reads the code and nobody reads the tests line by line, how do you know a green suite means anything? By injecting known bugs and checking that the suite detects them. Each bug that survives is a **concrete** gap in the scenarios, with a name and a face, not an abstract coverage metric.

**Analogy:** calibrating a scale with reference weights. If you put a 1 kg weight on it and it reads 0, the scale is useless, even if it has always read "fine".

**Rationale:** mutant detection is associated with real-fault detection more than code coverage is (Just et al., 2014); the correlation exists but is weaker when suite size is controlled for (Papadakis et al., 2018). That is why the value here is not a percentage, but each concrete survivor. Google applies it to the diff, with few mutants per change shown in code review; Meta (ACH) uses LLMs to generate plausible mutants and the tests that kill them. This skill applies the same idea at the **acceptance** level: semantic, plausible mutants chosen by risk, not thousands of syntactic mutations.

## 0. Preconditions

- Run the scripts from the repository root. `<qa-core>` is the folder of the `qa-core` skill, a sibling of this one; `<Acceptance>` and `<Reports>` come from `docs/agents/qa.md`.
- `docs/agents/qa.md` declares the **suite command for mutants**, the cleanup, the timeout, the budget and the forbidden paths. If not, ask to complete it (`qa-setup`). The command follows the rung-script contract: it builds the image **from the current directory** with `$QA_IMAGE_TAG` and writes the JUnit report to `$QA_REPORTS`. If it does not rebuild the image from the worktree, every mutant "survives" without being tested.
- **Cost**: (baseline + N mutants) × (build + suite). With 5-10 mutants it can exceed an hour. If it does not fit the budget before the PR, run it nightly; the report is valid for the fingerprint of the code evaluated.
- The feature is implemented and the suite is green on rung 1. The script checks it (baseline run) and aborts if not: with a red baseline the results mean nothing.
- The seal is intact (`seal.py verify`).

## 1. Role separation

The **mutation agent** is a distinct adversarial role:
- It **sees the code** (it needs it to inject bugs), but it **does not edit** tests or code in the repo: its changes only exist as patches that the script applies in temporary worktrees.
- It **reports survivors in terms of behavior**, not code: "the system accepts a sixth device and no scenario detects it", not "I changed `<` to `<=` on line 40". That way QA can add scenarios without seeing the code, and the information barrier holds.

Launch it as a subagent with a clean context if the current session is QA's (so it is not exposed to the code) or the dev's (so it does not pick mutants it knows its suite detects).

> **Portability:** if your tool has no subagents, follow [../qa-core/references/portability.md](../qa-core/references/portability.md) and declare it in the artifact.

## 2. Choose the mutants

1. Scope: the feature diff's production files (`git diff <base>...HEAD --stat`).
2. Choose **between 5 and 10 mutants**, prioritized by risk: the rules of critical criteria, third-party integrations, caching, idempotency, boundaries. Use the catalog in [references/mutant-catalog.md](references/mutant-catalog.md).
3. Each mutant meets four conditions:
   - **Plausible**: a mistake a person or an agent could really make.
   - **Single**: one behavior change per mutant.
   - **Observable**: it changes something a criterion demands. If you believe it changes no observable behavior, it is a candidate **equivalent**: do not run it, but **list it in the manifest** as "discarded as equivalent" with your justification. The human confirms it, not you.
   - **Production code only**: it never touches tests, the acceptance folder, the tracker, the QA configuration or the rung scripts. The script rejects patches that touch the forbidden paths.

## 3. Write the patches

One file per mutant in `.scratch/<feature>/qa/mutants/<date>/M-NN-<slug>.patch`, built against the current state of the working tree:

```bash
cp <file> /tmp/mutant/<file>            # copy
# edit the copy with the mutant's change
diff -u --label a/<file> --label b/<file> <file> /tmp/mutant/<file> > M-NN-<slug>.patch
```

**Never edit the repo's file** to produce the patch. Next to the patches, a `manifest.md`:

| ID | File | Category | Behavior it changes | Criterion that should detect it | Status |
|---|---|---|---|---|---|

Status: `to run` or `discarded as equivalent: <justification>`.

## 4. Run

```bash
python3 <qa-core>/scripts/mutants.py run --cmd "<suite command from qa.md>" \
  --timeout <timeout> --cleanup "<cleanup from qa.md>" --forbidden <forbidden paths from qa.md> \
  --output .scratch/<feature>/qa/mutants/<date>/results.json \
  .scratch/<feature>/qa/mutants/<date>/M-*.patch
```

The script records the code's **fingerprint** (HEAD and the hash of uncommitted changes), first runs the baseline without mutants (if it does not pass, or leaves no JUnit report with scenarios, it aborts), and for each patch creates a temporary worktree with the current state, applies the patch, runs the suite in its own process group (on a timeout it also kills the child processes) and removes the worktree whatever happens. The repository is not touched. There is no option to skip the baseline.

## 5. Analyze

| Result | What it means | Action |
|---|---|---|
| **detected** | The suite ended red and at least one `SC-NN` scenario failed | Check that the red scenarios include one from the criterion the manifest expected; if only another one fell, note it: the expected criterion may have a gap |
| **survived** | The suite passed with the bug inside | Triage (below) |
| **harness-error** | Red without any failed scenario: it did not compile, the harness did not start | It does not count as detected. Redo the mutant (one that does not compile is not plausible) or fix the harness |
| **timeout** | The suite did not finish | Investigate: a mutant that hangs the system may be a real, uncovered robustness bug; it never counts as detected |
| **not-applicable** | Badly built patch | Redo it |
| **rejected** | The patch touches forbidden paths | Redo it on production code |

Triage of each survivor:
1. **Equivalent**: the change alters no observable behavior. Justify it in writing; **the human decides**, not the mutation agent.
2. **Scenario gap**: the criterion exists but no scenario observes that behavior. Pass QA the description **in terms of behavior**; `qa-test-design` adds the scenario and the approval and seal cycle repeats.
3. **Criterion gap**: no criterion demands that behavior. Go back to `qa-acceptance-criteria`: either a criterion is missing, or the behavior does not matter (and then the mutant is equivalent for the business).

## 6. Report

Write `.scratch/<feature>/qa/mutants/<date>.md` with:
- the **fingerprint** from `results.json` (a report is valid only for that fingerprint; if the code changes, `qa-verify` asks for a new one in the full cadence);
- the ones discarded as equivalent, for the human to confirm;
- the results table;
- each survivor with its triage and its decision.

`qa-verify` uses it as gate G8.

## Complement in the inner loop

For the dev's unit tests there are mechanical mutation tools (in Go, Gremlins). They are useful in the dev's full cadence, but they answer another question: whether the **unit** tests detect syntactic mutations. They do not replace this skill, which measures the **business** oracle.
