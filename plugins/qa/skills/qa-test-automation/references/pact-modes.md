# Contracts: Pact between own services, learning tests for third parties

Pact is **consumer-driven** contract testing:
1. The consumer writes a test against a Pact mock declaring what it asks for and what it expects; Pact generates a JSON **contract file**.
2. The provider replays that contract against its real implementation, preparing each state with *state handlers*; if something the consumer uses changed, it fails.

**Analogy:** a lease. Signed and kept in a drawer (mode A) it is still valid, but only if someone reads it when there is a dispute. Registered with a notary (mode D, with a broker), anyone can look it up before acting.

## Who does what

- The **consumer tests** use the consumer's real client, which is production code. That is why they belong to the **dev** and live with the consumer's code, **not** in the acceptance folder (which is black box and sealed).
- The generated **contract files** go to the repo's `contracts/`, outside what is sealed.
- The **provider verification** is rung 2: its script runs it, and the result (date, provider version) stays in that run's reports, not inside the contract.

## Modes for services you control

It does not need CI or a broker to work: the contract is a file and the verification is a command. What changes between modes is **which guarantee you get and who has to remember to run it**.

| Mode | How | When | What you lose |
|---|---|---|---|
| **A. Local with files** | The consumer test writes `contracts/*.json`; the provider is verified while running on rung 1, with state handlers that seed through its seams | You control both sides or can bring the provider up | `can-i-deploy` and the version history; drift is only detected when someone runs the verification |
| **B. Against a deployed environment** | The verification points to the provider's URL in dev or staging | You cannot bring the provider up | No state control: only stateless interactions or ones with known seeded data; less stable |
| **D. CI with a broker** | Contracts published to a Pact Broker; `can-i-deploy` before deploying | There are permissions and both teams adopt it | — |

### Without CI: how to keep it alive

Without CI, Pact goes from being a **gate** to being a **check someone has to remember to run**. So that it does not rot silently:
1. The verification is part of the rung-2 script.
2. `qa-verify` runs it in the **full cadence** and reports it as a gate.
3. `qa-verify` flags as a risk a contract whose last green verification is older than 30 days or predates the provider's last change.

## Third parties: do not use Pact as if it were a gate

With a third party (payment gateway, partner), provider verification is not viable: it will not run your contract and its sandbox does not expose *provider states*. Pact's own documentation advises against using it for APIs you do not control. Instead:

1. **Learning tests** against the sandbox (rung 2): each assumption about the third party is a test that runs in the full cadence and warns if the third party changes.
2. **WireMock** records those responses as fakes for rung 1.
3. If the third party publishes an **OpenAPI**, bi-directional contract testing (comparing what you consume against its OpenAPI; PactFlow offers it, paid) is an additional option, not a substitute for the learning tests.

## Recipes (Pact Go v2)

Signatures change between versions; confirm them in the documentation of the installed version. Pact Go v2 needs Pact's native library.

Consumer (written by the dev, next to the consumer's code):

```go
mock, err := consumer.NewV4Pact(consumer.MockHTTPProviderConfig{
    Consumer: "checkout-front", Provider: "payments-bff", PactDir: "../contracts",
})
if err != nil { t.Fatal(err) }
err = mock.AddInteraction().
    Given("a new buyer exists").
    UponReceiving("a token request for checkout").
    WithRequest("POST", "/tokens", func(b *consumer.V4RequestBuilder) {
        b.JSONBody(map[string]any{"flow": "checkout"})
    }).
    WillRespondWith(200, func(b *consumer.V4ResponseBuilder) {
        b.JSONBody(matchers.Map{
            "type":  matchers.S("client_token"),
            "token": matchers.Regex("eyJhbGciOi.e30.x", `^[\w-]+\.[\w-]+\.[\w-]*$`),
        })
    }).
    ExecuteTest(t, func(cfg consumer.MockServerConfig) error {
        return checkoutClient(fmt.Sprintf("http://%s:%d", cfg.Host, cfg.Port)).RequestToken("checkout")
    })
```

Provider (rung 2):

```go
err := provider.NewVerifier().VerifyProvider(t, provider.VerifyRequest{
    ProviderBaseURL: os.Getenv("BASE_URL"),
    PactFiles:       []string{"../contracts/checkout-front-payments-bff.json"},
    StateHandlers: models.StateHandlers{
        "a new buyer exists": func(setup bool, s models.ProviderState) (models.ProviderStateResponse, error) {
            return nil, seedNewBuyer(setup) // through the seeding seam, not by touching the database
        },
    },
})
```

**The detail that matters:** the contract must come from what the **real consumer needs** (the SDK documentation, the front-end code), not from what the provider returns today. A contract copied from the provider's current response certifies the bug.
