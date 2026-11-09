# qa

QA domain of the `sv-agent-plugins` marketplace: it separates whoever builds from whoever tests, so no agent certifies itself. The dev implements with `engineering`; QA designs and automates the oracle with this plugin; deterministic scripts count; the human decides.

## Principles

1. **The implementing agent never writes or edits the oracle** (criteria, scenarios, acceptance tests). If it believes a test is wrong, it escalates.
2. **QA does not certify.** `verify` delivers gates and evidence; the decision is human.
3. **Usage oracle**: if someone else consumes what you produce, the consumer decides whether it works, not the shape of the artifact.
4. **Black box is information, not a place**: QA tests the PR image in a hermetic environment without seeing the code.
5. **If nobody reads the code, the tests get tested**: integrity seal, traceability, determinism and bug injection.

## Flow

```
to-spec ─► handoff ─► acceptance-criteria ─► test-design ─► test-automation ─► (dev: tdd)
                                      │ premortem           │ 5 techniques    │ learning tests        │ acceptance tests
                                      ▼                     ▼ in parallel     ▼ correct red           ▼ read-only
                                  human approval        design seal        tests seal             verify ─► findings
                                                                                                    │   (code → diagnosing-bugs)
                                                                                    test-the-tests ◄┘   (spec → acceptance-criteria)
```

## Skills

| Skill | Invocation | What it does |
|---|---|---|
| `qa-setup` | user | Mode (solo or duo), information barrier, available rungs with their command, Pact mode. Writes `docs/agents/qa.md`. |
| `qa-acceptance-criteria` | model | Criteria verifiable from the outside with their oracle; usage oracle; implicit criteria; criteria premortem with 3 subagents. |
| `qa-test-design` | model | Requires the handoff contract; 5 parallel subagents per family of ISTQB and failure techniques; assigns the rung; traces and seals. |
| `qa-test-automation` | model | Harness per rung, learning tests first, scenarios with existing tools; red for the right reason, determinism and traceability before sealing. |
| `qa-verify` | model | Deterministic gates per cadence; failure classification (code, configuration, spec, test, environment); push-down; a report without "approved". |
| `qa-test-the-tests` | model | Semantic mutants on the diff in temporary worktrees; survivors are concrete gaps in the scenarios. |
| `qa-toolbox` | model | Tools radar and a guide to choosing by need and rung. |
| `qa-core` | model | Shared base: references and scripts. **Always install it** next to the others: they all link to it as a sibling folder. |

## Scripts (in `skills/qa-core/scripts/`, Python standard library, with tests)

| Script | What it does |
|---|---|
| `scripts/seal.py` | Hashes the whole oracle (criteria, scenarios, tests, rung scripts, configuration); detects changes and symbolic links; against the base branch it lists every reseal and breaks if the seal was deleted, recreated or resealed without citing `E-NN`/`F-NN`. |
| `scripts/traceability.py` | Chain criterion → scenario → test → result from Markdown, sources and the JUnit reports of a single run; skipped, not executed, a stale report, a case with several IDs or a criterion with no evidence in scope are not green. |
| `scripts/mutants.py` | Mutant patches in temporary worktrees, with a mandatory baseline run, a code fingerprint, forbidden paths and a process group; it counts as detected only if a scenario fails. |

Tests: `python3 -m unittest discover -s skills/qa-core/scripts/tests`.

## Shared references (in `skills/qa-core/references/`)

- `references/role-model.md`: roles, solo and duo modes, information barrier N1-N3, escalation, permissions per artifact.
- `references/environment-ladder.md`: rungs 0 to 5, assignment rule, cadences.
- `references/formats.md`: handoff, criteria, scenarios, ID convention in JUnit, findings, escalations, report.
- `references/portability.md`: how subagents, questions and skill loading are handled in each tool, and what to declare if a capability is missing.

## What this plugin does not guarantee (yet)

- **The information barrier is by convention at N1**, and so is the contamination rule: no gate checks what a session read. For a real guarantee, N2 or N3.
- **The seal detects, it does not prevent, and it does not attribute.** An agent can edit a test and reseal. What it cannot do is that without it showing: `verify` compares against the base branch and lists every reseal for the human PR review. Who did it is said by git, not by the seal. Preventing it by role (hooks) is phase 2.
- **Special-casing** (code that recognizes the test's data) is not detected with certainty by any script. Random, unmarked data, the G9 warning in `verify` and code review mitigate it.
- **Coverage depends on scenario design.** The tools execute; the techniques and the human decide what gets tested.

## Dependencies

It works on its own. It does more with `engineering` (spec, tickets with a walking skeleton, `tdd` as the inner loop, `diagnosing-bugs` for findings), `architecture` (failure modes per archetype) and a language plugin (`go-testing` for the Go plumbing).

## Installation

See the [repository README](../../README.md#installation) for Claude Code, Codex, GitHub Copilot, Cursor and Windsurf. In short, with Claude Code:

```bash
claude plugin marketplace add svallejo-dev/sv-agent-plugins
claude plugin install qa@sv-agent-plugins
```

Then, in each repo, run the `qa-setup` skill.

All skills respond in the user's language. MIT license.
