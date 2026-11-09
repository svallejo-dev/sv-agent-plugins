# Harness structure and data rules

## A feature's folder

```
<Acceptance>/
├── go.mod                its own module (Go): the compiler prevents importing production internal/
├── bin/                  rung scripts (contract in qa-setup), sealed in every feature
└── <feature>/
    ├── .qa-seal.json     integrity seal (do not edit by hand)
    ├── README.md         which seams it uses; how it runs
    ├── features/         Gherkin: what the human reads
    ├── http/             Hurl: SC-NN-<slug>.hurl
    ├── steps/            step plumbing (AI-generated)
    ├── harness/          rung-1 startup: image, Testcontainers, Toxiproxy, WireMock
    ├── pages/            minimal walking-skeleton consumers (written by QA)
    ├── learning/         learning tests against third-party sandboxes
    ├── fakes/            recorded and redacted WireMock mappings + RECORDING.md with dates
    └── data/             test data generators (never real data)
```

The rung-4 smoke scenarios are the same files, with `1, 4` in their Rung column; there is no separate folder with duplicated IDs. Pact contracts live in the repo's `contracts/`, outside this folder (see pact-modes.md).

Everything in `<feature>/` and `bin/` is sealed, with no exceptions: the seal does not ignore `node_modules`, `__pycache__` or anything similar, and it breaks on any symbolic link. **Nothing is written inside at run time**: reports, logs, caches, Playwright's `test-results/`, `__pycache__` (use `PYTHONDONTWRITEBYTECODE=1`) and new recordings go to `$QA_REPORTS` or to a temporary folder. If a run modifies the folder, the seal breaks and the verification cannot tell a run apart from cheating.

## Test data

| Rule | Why |
|---|---|
| Each scenario creates its own data through the API or the seeding seam | No hidden dependencies between scenarios or on their order |
| Random values per run, **without recognizable prefixes or patterns** | It can run in parallel and repeat without cleanup, and production code cannot recognize the test's data to answer what it expects (special-casing) |
| Never seed by writing directly into the service's database | It would skip the system's rules and the scenario would test an impossible state |
| In staging, only test accounts or tenants, and cleanup at the end | Do not dirty a shared environment; do not touch other people's data |
| Never real personal data; card data only from the provider's test set | Compliance (PCI, privacy) |

If the system offers no seeding seam, the scenario is `blocked-testability`. It is not "fixed" by seeding directly into the database.

## Verifiable black box

The "no production imports" rule is checked, not trusted:

- Go: the acceptance folder is **its own module**, so importing production `internal/` does not even compile. On top of that, the check in `docs/agents/qa.md` (`go list -deps -test ./...` inside the acceptance module, with no trace of the production module). `-test` is essential: godog suites live in `_test.go` files.
- Other languages: the equivalent with the dependency analyzer, or a `grep` of the production import paths.
- A check that **fails to run** (for example `go list` with an error and empty output) does not count as passed: verify its exit code.

`qa-verify` runs this check as a gate.

## The service as an artifact

On rung 1, the service is built once as an image (`docker build`) and the harness starts it. Testing the image and not the code:
- tests what gets deployed (configuration via variables, binary, system dependencies);
- keeps the information barrier: QA needs the image and the handoff, not the code repository.
