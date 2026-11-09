# AI platform (inference)

**Analogy:** a restaurant with a few very expensive star chefs. Each dish takes time to prepare, chefs cannot be hired on the spot, and the art is in batching orders so no chef sits idle without making anyone wait too long.

## Dominant forces

- **Expensive, scarce compute**: GPUs (or accelerators) are the limiting resource and the largest cost; they do not scale in seconds.
- **Latency in two parts**: time to first token and tokens per second afterwards; responses are streamed.
- **Long requests of very variable size** (input context, output length).
- **Cost per token** as a business metric.

## Shape of the load (without metrics)

- Throughput is measured in **tokens per second**, not requests per second; two requests can differ by orders of magnitude.
- Long-lived connections (streaming for seconds or minutes).
- Peaks from launches and from customers running batches.
- Scenarios to explore: 10, 1,000 and 100,000 concurrent requests, with contexts of 1k, 10k and 100k tokens.

## Invariants and consistency

- Per-customer limits on requests and on tokens per minute, applied consistently.
- Exact usage-based billing (input and output tokens).
- Data isolation between customers (prompts and responses), with explicit retention policies.

## Typical subdomains

- **Core**: model serving (batching, GPU scheduling, routing between models), quality and evaluation.
- **Supporting**: key and quota management, usage-based billing, usage observability, prompt caching.
- **Generic**: authentication, payments, storage.

## Path already walked (check before citing)

- Continuous batching and KV cache memory management (vLLM, PagedAttention) to increase throughput per GPU.
- Rate limiting by requests and tokens per minute, as model providers' APIs do.
- Prompt caching to reuse long prefixes.
- Streaming responses with Server-Sent Events.

## Typical failure modes (seed for the red team)

- A saturated GPU queue: time to first token shoots up for everyone.
- A customer with huge-context requests hoarding the capacity (noisy neighbor).
- Streaming connections cut by proxies or load balancers with short timeouts.
- Client retries on 429 or 529 errors that worsen the overload.
- Lack of capacity in a region with no way to scale quickly.

## Questions that change the design

- Own models or a provider's? One or several?
- What time to first token does the product need?
- Interactive use, batch or both? Can the queues be separated?
- What retention and privacy requirements apply to the prompts?

## Hypotheses for a PoC

- Validate latency and cost per request with the real distribution of context sizes, not with a fixed size.
- Validate behavior against the provider's limits (429) with backoff and queues.
- Instrument: time to first token, tokens per second, tokens per request (input and output), cost per request, 429 rate.
