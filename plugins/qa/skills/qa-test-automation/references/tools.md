# Tools: how each one is used

Minimal recipes for the harness and the tests. APIs change between versions: **confirm every signature and every flag against the documentation or the `--help` of the installed version** before trusting a recipe. The selection criteria are in `qa-toolbox`.

## Hurl: HTTP flows in plain text

Language-independent binary. Each file is a sequence of requests with captures and assertions; a human reads it without knowing how to program.

```hurl
# SC-07-idempotency.hurl
# Seeding through the API: a new, unique customer per run
POST {{base_url}}/qa/customers
HTTP 201
[Captures]
customer: jsonpath "$.id"

POST {{base_url}}/customers/{{customer}}/devices
Idempotency-Key: register-{{customer}}
{ "type": "tv" }
HTTP 201
[Captures]
id: jsonpath "$.id"

POST {{base_url}}/customers/{{customer}}/devices
Idempotency-Key: register-{{customer}}
{ "type": "tv" }
HTTP 201
[Asserts]
jsonpath "$.id" == {{id}}

GET {{base_url}}/customers/{{customer}}/devices
HTTP 200
[Asserts]
jsonpath "$.items" count == 1
```

- Run (inside the rung script): `hurl --test --report-junit "$QA_REPORTS/hurl.xml" --variable base_url=$BASE_URL <files>`.
- Polling without `sleep`: the per-request `retry` option (`[Options]` section).
- Shape: `jsonpath "$.token" matches "^[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]+\\.[A-Za-z0-9_-]*$"`.
- The ID goes in the file name.

## Gherkin with godog (Go)

Gherkin is the artifact the human reads; godog connects each step to a Go function. It supports other languages with a `# language: <code>` header (for example `# language: es`).

```gherkin
Feature: Device limit per customer
  Scenario Outline: SC-04 register with <current> devices
    Given a customer with <current> registered devices
    When they register a new device
    Then the response is <status>
    And the customer ends up with <final> devices
    Examples:
      | current | status | final |
      | 4       | 201    | 5     |
      | 5       | 409    | 5     |
```

```go
func InitializeScenario(sc *godog.ScenarioContext) {
    w := &world{api: newHTTPClient(os.Getenv("BASE_URL"))} // per-scenario state
    sc.Step(`^a customer with (\d+) registered devices$`, w.customerWithDevices)
    sc.Step(`^they register a new device$`, w.registersDevice)
    sc.Step(`^the response is (\d+)$`, w.responseIs)
    sc.Step(`^the customer ends up with (\d+) devices$`, w.customerEndsUpWith)
}
```

- The steps speak HTTP to the service; they never import production packages.
- It runs from `go test` with `godog.TestSuite`; the JUnit report comes from its `junit` formatter (for example `Format: "pretty,junit:" + os.Getenv("QA_REPORTS") + "/godog.xml"`; confirm the syntax in your version). The steps live in the acceptance folder's own Go module.
- In other languages, the equivalent is Cucumber (JVM, JS) or behave (Python). Karate is an alternative with its own HTTP DSL.

## Testcontainers: real, disposable dependencies

Starts containers from the test and destroys them at the end. It exists for Go, Java, .NET, Node, Python and others.

```go
pg, err := postgres.Run(ctx, "postgres:16-alpine",
    postgres.WithDatabase("devices"),
    postgres.BasicWaitStrategies())
if err != nil { t.Fatal(err) }
t.Cleanup(func() { _ = testcontainers.TerminateContainer(pg) })
dsn, err := pg.ConnectionString(ctx, "sslmode=disable")
if err != nil { t.Fatal(err) }
```

For rung 1, the **service under test is also a container**, built from its image, on the same Docker network as its dependencies. That way QA tests the artifact that gets deployed, not the source code.

Requirements: Docker available locally and in CI. Pin the image versions; `latest` makes the harness non-deterministic.

## Toxiproxy: network failures on demand

A TCP proxy placed between the service and each dependency. The service is configured to talk to the proxy; the test adds "toxics".

```go
cli := toxiproxy.NewClient(toxiproxyAPI) // the Toxiproxy container's API (port 8474 mapped)
px, err := cli.CreateProxy("postgres", "0.0.0.0:25432", "postgres:5432")
if err != nil { t.Fatal(err) }
// the service under test is configured with the database at <toxiproxy>:25432
if _, err := px.AddToxic("slow", "latency", "downstream", 1.0,
    toxiproxy.Attributes{"latency": 3000}); err != nil { t.Fatal(err) }
t.Cleanup(func() { _ = px.RemoveToxic("slow") })
```

Useful toxics: `latency`, `bandwidth`, `timeout`, `reset_peer`, `slicer`, `limit_data`, `slow_close`. Disabling the proxy simulates the dependency being down.

It is used on rung 1, where you control the whole network. **Not in shared staging.**

## WireMock: third-party fakes recorded from reality

HTTP stub server, as a container (it has a Testcontainers module). Two uses:
- **Recording**: in record mode it proxies to the third party's sandbox while the learning tests run and saves the responses as mappings. **Redact tokens and secrets from the mappings before saving them.**
- **Playback**: on rung 1 it serves those mappings, plus the error and variant ones the sandbox does not let you trigger (5xx, 429, timeouts with `fixedDelayMilliseconds`, truncated responses).

## Pact: contracts between own services

See [pact-modes.md](pact-modes.md): modes A (local files), B (against a deployed environment) and D (CI with a broker). For third parties, learning tests + WireMock.

## Schemathesis: contract fuzzing from OpenAPI

Generates thousands of requests from the OpenAPI and checks that the service does not answer 5xx, that responses match the schema and other properties. It runs in the full cadence against rung 1. Basic: `schemathesis run <openapi> --url $BASE_URL`, with its JUnit report. The CLI changed in v4: confirm the flags with `schemathesis run --help`.

It finds what nobody wrote (odd inputs, extra fields); it does not replace the scenarios, which check business rules.

## Playwright: the real consumer in the browser

For scenarios with a UI and, above all, for the **walking skeleton** with a browser SDK: a minimal page that requests the token from the system under test, initializes the SDK with it and exposes the result reported by **the SDK itself** (its error or ready callback).

```ts
test('SC-01 the payments SDK initializes with the BFF token', async ({ page }) => {
  await page.goto(`${process.env.QA_PAGES_URL}/minimal-checkout.html?bff=${encodeURIComponent(process.env.BASE_URL!)}`);
  await expect(page.getByTestId('sdk-status')).toHaveText('ready', { timeout: 15000 });
});
```

**QA writes the minimal page** inside `<Acceptance>/<feature>/` and the harness serves it (a static server in its own container). If the service under test served it, the dev would control the oracle: they could make it say `ready` every time.

Reports: configure the `junit` reporter with its output file in `$QA_REPORTS` (the `outputFile` option in the config, or the environment variable your version documents; without it, it writes to stdout) and `outputDir` also under `$QA_REPORTS`: by default Playwright writes `test-results/` next to the tests, and that would break the seal.

Playwright's agents (planner, generator, healer) can help create and maintain UI tests, but **the healer may only touch selectors, never assertions**: if it repairs an assertion, it is changing the oracle.

## k6: load

It is not part of the functional suite. It is used for dedicated load tests, in an environment that can take load without affecting other teams.

## gotestsum (Go)

If part of the harness runs with `go test`, `gotestsum --junitfile "$QA_REPORTS/go.xml"` produces the JUnit report. Subtests appear as `TestX/SC-11_timeout…`; `traceability.py` recognizes the ID.
