PASS only if ALL of the following hold:

1. **Process order**: it writes the criteria before the scenarios (or refuses to design scenarios without approved criteria and generates them first) and does not approve itself: it asks for human approval.
2. **Usage oracle**: at least one criterion is verified with the processor's web SDK accepting the token for a specific flow, not just with the shape of the response (200, non-empty token or JWT).
3. **Variant per flow**: it identifies that each story needs a different token type (checkout → client token; save method → id_token; pay with a saved method → id_token with `target_customer_id`) and that the spec asks for a single token without `response_type`. It presents this as a **spec finding or question** (a flow × variant decision table or equivalent), not as a detail to resolve during implementation.
4. **Cache key**: it detects that a token bound to a buyer cannot be served from a shared cache, and proposes a scenario where two different buyers never receive the same personal token.
5. **Security**: it points out that the server token must not reach the browser.
6. **Rungs**: the SDK scenario stays on rung 3 (walking skeleton with the real consumer, served by QA's harness) and it proposes learning tests against the sandbox on rung 2, recorded with WireMock, before building fakes; it does not use Pact against the processor.
7. **Composition**: it uses parallel subagents per technique and the parseable format (`AC-NN`, scenario table with ID, Criterion, Rung, Status), and runs `traceability.py`.

FAIL if:
- the scenarios only check the shape of the response (200 status, token present, JWT format) without the real consumer;
- it treats the shared cache as correct;
- it resolves the ambiguity by inventing a variant without asking.

Calibration: the reference bad answer writes scenarios like "POST /payments/token returns 200 and a non-empty token", "a second call returns the same token from the cache" and "if the processor fails, it returns 502". It must get FAIL.
