# Case 01: a third-party token with variants

## Test repo setup

`docs/agents/qa.md`: solo mode, barrier N1, rungs 1, 2 and 3 available (with fictitious commands), the payment processor as a third party (learning tests + WireMock).

`.scratch/payment-token/spec.md`:

> **Problem.** The checkout front end needs to authenticate with the payment processor to show its payment buttons and allow saving payment methods.
>
> **Solution.** A BFF exposes `POST /payments/token`. It calls the processor's OAuth endpoint (`/v1/oauth2/token`, `grant_type=client_credentials`), caches the token until it expires and returns it to whoever asks.
>
> **Stories.** 1. As a buyer, I want to see the payment buttons at checkout. 2. As a buyer, I want to save my payment method for the next purchase. 3. As a returning buyer, I want to pay with my saved method.
>
> **Decisions.** The token is cached in Redis with a TTL equal to `expires_in`. The BFF does not know the buyer: it only hands out the token.

A complete `.scratch/payment-token/qa/handoff.md`: surface (`POST /payments/token` → `{ "token": string }`), consumer (the processor's web SDK, initialized in the front end), dependency (payment processor, with a sandbox and a link to its documentation), artifact (the BFF's Docker image) and seams (seeding: not applicable; clock: available; configurable dependencies: yes; isolation: sandbox accounts; observability: trace-id).

`docs/processor-oauth.md`, a summary of the processor's documentation (a paraphrase, not a copy):

> The `/v1/oauth2/token` endpoint issues different token types depending on the `response_type` parameter. Without it, it issues a server token for server-to-server calls; it must not be exposed to the browser. With `response_type=client_token` it issues a browser-safe token, which the web SDK uses to initialize; it also arrives in the `access_token` field. With `response_type=id_token` it issues an identity JWT the SDK needs to save payment methods; if `target_customer_id` is also sent, the token is bound to that buyer and allows paying with their saved methods.

## Instruction to the agent

"Design the acceptance tests for the payment-token feature. The criteria are not written yet."
