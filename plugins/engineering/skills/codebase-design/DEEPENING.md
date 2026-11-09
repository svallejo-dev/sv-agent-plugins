# Deepening

How to safely deepen a group of shallow modules according to their dependencies. It assumes the vocabulary of [SKILL.md](SKILL.md): **module**, **interface**, **seam**, **adapter**.

## Dependency categories

When evaluating a candidate, classify its dependencies. The category decides how the deepened module is tested through its seam.

### 1. In-process

Pure computation, in-memory state, no I/O. It can always be deepened: merge the modules and test directly through the new interface. No adapter needed.

### 2. Locally substitutable

Dependencies with a local substitute for tests: Postgres or MySQL in a container, Redis or Kafka in a container, an in-memory file system or a temporary directory. It can be deepened if the substitute exists. The deepened module is tested with the substitute running in the suite. The seam is internal; there is no port in the module's external interface.

### 3. Remote but owned (Ports & Adapters)

Your own services on the other side of the network (microservices, internal APIs, queues). Define a **port** (an interface) at the seam. The deep module owns the logic; the transport is injected as an **adapter**. Tests use an in-memory adapter; production uses an HTTP, gRPC or queue adapter.

Shape of the recommendation: _"Define a port at the seam, implement an HTTP adapter for production and an in-memory one for tests, so the logic lives in a single deep module even though it is deployed across the network."_

### 4. Truly external (double)

Third-party services you do not control (payment gateways, partners, identity providers). The deepened module receives the external dependency as an injected port; tests use a fake adapter or a local HTTP server that imitates the third party.

## Seam discipline

- **One adapter means a hypothetical seam. Two adapters mean a real one.** Do not introduce a port unless at least two adapters are justified (usually production + test). A seam with a single adapter is just indirection.
- **Internal vs external seams.** A deep module can have internal seams (private, used by its own tests) in addition to the external seam of its interface. Do not expose internal seams in the interface just because tests use them.

## Testing strategy: replace, do not stack

- Old unit tests on shallow modules become redundant once tests exist at the deepened module's interface; delete them.
- Write new tests at the deepened module's interface. **The interface is the test surface.**
- Tests assert observable results through the interface, not internal state.
- Tests survive internal refactors because they describe behavior, not implementation. If a test has to change when the implementation changes, it is testing beyond the interface.
