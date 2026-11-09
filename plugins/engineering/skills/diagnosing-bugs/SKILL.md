---
name: diagnosing-bugs
description: "Diagnosis cycle for hard bugs and performance regressions, in any language. Use it when the user says \"diagnose\", \"debug this\" or reports something broken, throwing errors, failing, giving inconsistent results or running slow."
license: MIT
---

# Diagnosing bugs

Respond in the user's language; keep common technical terms in English.

A discipline for hard bugs. Skip phases only with an explicit justification.

When exploring the code, read `GLOSSARY.md` (if it exists) to have a clear mental model of the modules involved, and check the area's ADRs.

## Language

This skill is language-agnostic. Identify the language of the code involved by its file extensions (`.go` → `go`, `.php` → `php`, `.ts`/`.tsx` → `typescript`, `.py` → `python`). If `<language>-debugging` exists among your available skills, load it (in Claude Code, with the Skill tool; in other tools, by mentioning its name or reading its SKILL.md) when starting Phase 1: it brings the concrete commands for each technique (run a single test, repeat it, fuzzing, race detector, debugger, profiler, benchmarks). If it does not exist, carry on with this skill alone and say so in one line.

## Redact

This skill makes you show commands, outputs and captured artifacts. **Redact every secret first**: write `<REDACTED>` in its place. Build the loops reading credentials from environment variables, so the secret stays in the environment and not in what you show. Captured artifacts carry auth headers: quote only the lines with signal.

If the redacted output is not enough to diagnose, say so and ask the user.

## Phase 0: Listen to the user's suspicions

If the user arrives with a hypothesis ("I think it's the cache"), write it down as is as a candidate for Phase 3 and thank them, but do not investigate it yet. Explain in one line why the loop comes first: without a signal that turns red, there is no way to know whether the suspicion is true.

Analogy: a doctor listens to what the patient thinks they have, but does not prescribe until the test results are in.

## Phase 1: Build a feedback loop

**This is the skill.** Everything else is mechanical. If you have a **tight** pass/fail signal for the bug (one that turns **red** on _this_ bug), you will find the cause: bisection, hypothesis testing and instrumentation only consume it. If you do not have it, no amount of reading code will save you.

Spend a disproportionate effort here. **Be aggressive. Be creative. Do not give up.**

### Ways to build it, roughly in this order

1. **Failing test** at the seam that reaches the bug: unit, integration or e2e, run in isolation.
2. **curl / HTTP script** against a running development server.
3. **CLI invocation** with a fixed input, comparing stdout with a known-good output.
4. **Replay of a captured trace.** Save a real request, payload or event to disk (from logs, from Kafka, from a HAR) and replay it through the code in isolation.
5. **Throwaway harness.** Bring up a minimal subset of the system (one service, fake dependencies) that exercises the bug's path with a single call.
6. **Fuzz / property.** If the bug is "sometimes it gives a wrong result", use the language's fuzzer or 1000 random inputs and look for the failure mode.
7. **Bisection harness.** If the bug appeared between two known states (commit, dataset, version), automate "start in state X, check, repeat" so you can use `git bisect run <loop-command>`.
8. **Differential loop.** Feed the same input through the old and the new version (or two configurations) and compare outputs. Ideal for migrations between stacks (for example, a legacy service against its rewrite): the legacy one is the oracle.
9. **Bash script with a human in the loop.** Last resort. If a person has to click or look at a dashboard, guide them with `scripts/hitl-loop.template.sh` so the loop stays structured. What is captured comes back to you.

Build the right loop and the bug is 90 % fixed.

**If you arrive with a `qa-verify` finding (F-NN):** its reproduction command on the hermetic rung is already a loop. Use it as the starting point and push it down: first to an integration test, then to a unit test, down to the lowest seam that turns red. Each step down shrinks the area where the defect can be.

### Tune the loop

Treat the loop as a product. Once you have _a_ loop, make it **tight**:

- Can it go faster? (Cache the setup, skip initializations that do not apply, run only the test that matters.)
- Can it give a sharper signal? (Assert the concrete symptom, not "it did not crash".)
- Can it be more deterministic? (Pin the time and the random seed, isolate the file system in a temporary directory, freeze the network.)

A 30-second, intermittent loop is barely worth anything; a 2-second, deterministic one is tight, a debugging superpower.

### Non-deterministic bugs

The goal is not a clean reproduction but a **higher reproduction rate**. Repeat the trigger 100 times, parallelize, turn on the data race detector if the language has one, add load, narrow time windows, inject pauses. A bug that fails 50 % of the time can be debugged; one at 1 % cannot, so raise the rate until it can.

### When you really cannot build a loop

Stop and say so explicitly. List what you tried. Ask the user for: (a) access to the environment that reproduces it, (b) a captured and redacted artifact (log dump, an NRQL or Sumo Logic query with its result, traces, HAR, a recording with timestamps), or (c) permission to add temporary instrumentation in production. Do **not** move on to hypotheses without a loop.

### Exit criterion: a tight loop that turns red

Phase 1 ends when you can name **one command** (a script, a test invocation, a curl) that **you have already run at least once** (show the invocation and its output, redacted) and that is:

- [ ] **Able to turn red**: it goes through the bug's real path and asserts the **user's exact symptom**, so it can turn red with this bug and green when it is fixed. Not "runs without error": it has to be able to _catch this bug_.
- [ ] **Deterministic**: the same verdict on every run (for intermittent bugs, a high, pinned reproduction rate).
- [ ] **Fast**: seconds, not minutes.
- [ ] **Runnable by the agent**: you can run it unsupervised; a human only via `scripts/hitl-loop.template.sh`.

If you catch yourself reading code to build a theory before that command exists, **stop: jumping straight to a hypothesis is exactly the failure this skill prevents.** Without a command able to turn red, there is no Phase 2.

## Phase 2: Reproduce and minimize

Run the loop. Watch it turn red when the bug appears.

Confirm:

- [ ] The loop produces the failure mode the **user** described, not another nearby failure. Wrong bug = wrong fix.
- [ ] The failure reproduces across several runs (or, if non-deterministic, at a rate high enough to debug).
- [ ] You captured the exact symptom (error message, wrong output, timing) to verify later that the fix resolves it.

### Minimize

Once it is red, reduce the reproduction to the **smallest scenario that is still red**. Remove inputs, callers, configuration, data and steps **one by one**, running the loop after each cut, and keep only what sustains the failure.

Why: a minimal reproduction shrinks the hypothesis space in Phase 3 and becomes the clean regression test of Phase 5.

You are done when **every remaining element sustains the failure**: removing any of them turns the loop green.

Do not continue until you have reproduced **and** minimized.

## Phase 3: Hypotheses

Generate **3 to 5 ranked hypotheses** before testing any of them (include the suspicions from Phase 0). Generating only one anchors you on the first plausible idea.

Each hypothesis must be **falsifiable**: state the prediction it makes.

> Format: "If the cause is <X>, then <changing Y> will make the bug disappear / <changing Z> will make it worse."

If you cannot state the prediction, the hypothesis is a hunch: discard it or sharpen it.

**Show the ranked list to the user before testing** and ask which they would reorder and why. They often have domain knowledge that reorders it instantly ("yesterday we deployed a change to number 3") or know which ones they already ruled out. It is a cheap checkpoint that saves a lot of time. Do not block: if the user is not there, carry on with your order.

## Phase 4: Instrument

Each probe corresponds to a concrete prediction from Phase 3. **Change one variable at a time.**

Tool preference:

1. **Debugger** or REPL, if the environment allows it. One breakpoint is worth ten logs.
2. **Targeted logs** at the boundaries that distinguish hypotheses.
3. Never "log everything and grep".

**Tag each debug log** with a unique prefix, for example `[DEBUG-a4f2]`. The final cleanup becomes a single grep. Untagged logs survive; tagged ones die.

**Performance branch.** For performance regressions, logs are usually the wrong tool. First establish a baseline: a benchmark repeated several times and compared statistically, and a profile (CPU, memory, contention). In production, rely on the APM (New Relic or another) looking at percentiles (p50/p95/p99), not the average. Then bisect. Measure first, fix afterwards.

## Phase 5: Fix and regression test

Write the regression test **before the fix**, but only if there is a **correct seam** for it.

A correct seam is one where the test exercises the **real pattern of the bug** as it happens at the call site. If the only seam available is too shallow (a test with a single caller when the bug needs several, a unit test that cannot replicate the chain that triggered it), a test there gives false confidence.

**If no correct seam exists, that itself is a finding.** Note it: the architecture prevents pinning the bug down. Recommend `codebase-design` to the user to address it.

If a correct seam exists:

1. Turn the minimal reproduction into a failing test at that seam.
2. Watch it fail. If you forced the red by mutating code or a fixture, `diff` against a clean copy to prove the mutation was applied before trusting it.
3. Apply the fix.
4. Watch it pass.
5. Rerun the Phase 1 loop against the original (unminimized) scenario.

## Phase 6: Cleanup

Mandatory before calling it done:

- [ ] The original reproduction no longer reproduces (rerun the Phase 1 loop).
- [ ] The regression test passes (or the lack of a seam is documented).
- [ ] All `[DEBUG-...]` instrumentation removed (`grep -rn "DEBUG-a4f2"`).
- [ ] Throwaway prototypes deleted (or moved to a clearly marked debugging location).
- [ ] The hypothesis that turned out to be right is written in the commit or PR message, so the next person who debugs learns from it.
