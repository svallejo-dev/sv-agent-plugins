---
name: qa-setup
description: "Sets up the qa plugin in a repo: mode (solo or duo), information barrier, where the acceptance tests live, which rungs of the ladder exist and which script runs each one, the black-box check and the mutant budget. Writes docs/agents/qa.md. Use it only when the user explicitly asks for it."
license: MIT
---

# QA setup

Respond in the user's language; keep common technical terms in English.

Writes `docs/agents/qa.md`, the configuration every skill in `qa` reads. Without that file, the others stop and ask to run the `qa-setup` skill.

**Why the configuration pins commands, and why it is sealed:** `qa-verify` runs exactly the scripts declared here; it does not improvise them. An agent that decides on the spot how to run the suite can, with no bad intent, pick the command that gives green (a subset, an excluded tag). That is why the commands live in scripts inside the acceptance folder, and both those scripts and this file sit under each feature's seal: changing them is changing the oracle, and it shows.

## Process

1. Read `docs/agents/tracker.md` (from `engineering-setup`) to know where the specs live. If it does not exist, the default tracker is `.scratch/`; say so in one line.
2. Explore the repo: acceptance test folders, `Dockerfile`, `docker-compose`, Makefile, OpenAPI or AsyncAPI contracts, `.feature` and `.hurl` files, Playwright configuration. Propose values from what you find.
3. Ask, in a single round, what you cannot deduce. Use your tool's multiple-choice question mechanism if it has one (AskUserQuestion in Claude Code); if not, ask in text and number the options:
   - **Mode**: `solo` or `duo`. See [../qa-core/references/role-model.md](../qa-core/references/role-model.md).
   - **Information barrier**: N1, N2 or N3. Recommend N2 if the mode is solo and the work is critical.
   - **Available rungs**. See [../qa-core/references/environment-ladder.md](../qa-core/references/environment-ladder.md). A rung the platform does not offer is marked `not available`, never omitted.
   - **Base branch** the seal is compared against (usually `origin/main`).
   - **Time budget** for mutants.
4. Write the file from the template. No secrets in it: credentials are referenced by environment variable name.
5. Add the reports folder to `.gitignore`. Create the acceptance folder with a one-line `README.md`: its content is sealed and the dev escalates instead of editing.
6. Tell the user the next step: `qa-acceptance-criteria` on the feature's spec.

## Contract of the rung scripts

Each rung runs with a script in `<Acceptance>/bin/` (for example `rung-1.sh <feature>`). If they do not exist yet, `qa-test-automation` creates them in its step 1. Every rung script:

- exits 0 only if everything is green;
- writes its JUnit reports **only** to the directory it receives in `$QA_REPORTS` (empty and owned by that run; `qa-verify` creates it);
- writes nothing inside `<Acceptance>/` (it would break the seal);
- if it builds the service image, it does so from the current directory and with the tag `$QA_IMAGE_TAG` if defined (`qa-test-the-tests` uses it so mutant images do not mix with the real one);
- accepts no arguments that filter scenarios.

## Template for `docs/agents/qa.md`

```markdown
# QA configuration

Mode: solo | duo
Barrier: N1 | N2 | N3
Base branch: origin/main
Tracker: .scratch/
Acceptance: acceptance/            # one subfolder per feature + bin/ with the rung scripts
Seal: acceptance/<feature>/.qa-seal.json
Reports: acceptance-reports/       # outside acceptance/; ignored by git; one subfolder per feature and run

## Rungs

| Rung | Available | Script | Variables |
|---|---|---|---|
| 1 hermetic | yes | `acceptance/bin/rung-1.sh <feature>` | the harness sets BASE_URL |
| 2 contract | yes | `acceptance/bin/rung-2.sh <feature>` | sandbox URLs, credentials by variable name |
| 3 isolated integrated | not available | — | — |
| 4 staging | yes | `acceptance/bin/rung-4.sh <feature>` | STAGING_URL |
| 5 production | not available | — | — |

## Black box

Acceptance tests in Go live in **their own module** (`acceptance/go.mod`): the compiler prevents importing `internal/` packages from another module.
Check (must print nothing, with exit 0 from `go list`):
`cd acceptance && go list -deps -test ./... > /tmp/deps.txt && ! grep -E '^<production-module>(/|$)' /tmp/deps.txt`

## Artifact build

Service image: `docker build -t ${QA_IMAGE_TAG:-<service>:qa} .`

## Contracts

| Dependency | Type | How it is verified |
|---|---|---|
| <own service> | Pact mode A, B or D | … |
| <third party> | learning tests + WireMock | … |

## Mutants

Suite command: `acceptance/bin/rung-1.sh <feature>`
Cleanup after each mutant: `docker rmi -f $QA_IMAGE_TAG`
Timeout per mutant (s): 900
Total budget: <minutes>; if it does not fit before the PR, it runs nightly
Forbidden paths for mutants: acceptance/ .scratch/ docs/agents/
```

For repos that are not Go, the black-box check uses the language's dependency analyzer, or a `grep` of the production import paths with the exit code checked. A check that fails to run does **not** count as passed.
