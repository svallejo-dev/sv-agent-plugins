# Cross-cutting rubric

What applies to any change in any language. Go through each changed file with these dimensions and record each finding with a single severity. A specific language's idioms do not go here: that language's plugin reviews them.

## Dimensions

### 1. Correctness and edge cases
- Does the code do what the change's intent says?
- Boundaries: empty input, null, zero, negatives, single-element lists, overflow, off-by-one, ordering, time zones, unicode.
- Failure paths: if a network or database call fails halfway, is the state still consistent?
- Idempotency and retries where the flow needs them.

### 2. Security
- Injection (SQL, NoSQL, shell, LDAP): input concatenated instead of parameters.
- Authentication and authorization: is the permission checked in the right place? IDOR? Is access decided with data the client sends?
- Secrets in the code or in logs: **blocker**, and never quote the value.
- External input (HTTP, queues, files) validated and bounded; size limits when reading; safe deserialization.
- Cryptography: secure randomness for tokens, constant-time comparison, no broken algorithms.
- Personal data: it does not appear in logs, metrics or error messages.

### 3. Tests
- New or changed behavior has tests, including the failure path and the boundaries.
- The tests are deterministic (no sleeps, uncontrolled clock or network).
- A test that passes really exercises the new code; it is not tautological (the expected value is not recomputed the way the code does it).

### 4. Error handling
- Errors are propagated with context instead of being swallowed or logged and ignored.
- Expected errors (not found) are distinguished from unexpected ones.
- No abrupt process exits in normal flows; resources are released on error paths.

### 5. API and backward compatibility
- Changes to public signatures, endpoints, schemas, serialized formats, events, environment variables.
- Incompatible changes (renamed or removed fields, changed types, defaults, status codes): versioned, deprecated or migrated? Who depends on the current behavior today?

### 6. Performance and concurrency
- N+1 queries, avoidable O(n²), allocations on hot paths, missing pagination.
- Unsynchronized shared state, deadlocks, concurrent tasks with no way to end, locks held during I/O.
- Timeouts on every network call.

### 7. Size and readability
- Is it small and focused enough to review rigorously? Does it mix concerns?
- Clear names, faithful to the vocabulary of `GLOSSARY.md`, cohesive functions, no dead or commented-out code.
- Files named after what they do. Catch-all files (`utils`, `helpers`, `common`, `manager`) make navigation harder in any language; their severity depends on the repo's rules.
- Comments that narrate the obvious, or banners, add noise (minor or nit).

### 8. Documentation and migrations
- Behavior changes reflected in README, docs, CHANGELOG, API documentation.
- Database migrations: reversible? Do they lock large tables? Compatible with the version still deployed during the rollout (expand–contract)?
- New flags and configuration documented.

### 9. Observability
- Logs at the right level, with context, without secrets, without spam on hot paths.
- Metrics or traces on the new paths that matter operationally.
- Actionable error messages for whoever operates the system.

## Design smells (Fowler, _Refactoring_ ch. 3)

They are always judgment, never a hard violation: label them "possible <smell>" and give them minor unless they cause a bug. A documented repo standard that backs the pattern suppresses them. Each one reads *what it is* → *how to fix it*.

- **Mysterious name**: the name does not reveal what it does or holds. → rename it; if no honest name comes out, the design is murky.
- **Duplicated code**: the same shape of logic in more than one hunk or file of the change. → extract the common shape.
- **Feature Envy**: a function uses another module's data more than its own. → move it next to the data it envies.
- **Data Clumps**: the same fields or parameters always travel together. → group them into a type.
- **Primitive obsession**: a string or number playing a domain concept. → give it its own type.
- **Repeated switches**: the same `switch` or `if` cascade on the same type in several places. → polymorphism or a shared table.
- **Shotgun surgery**: one logical change forces edits in many scattered files. → bring together what changes together.
- **Divergent change**: a module is edited for several unrelated reasons. → split it.
- **Speculative generality**: abstractions, parameters or hooks for needs nobody asked for. → delete it until the need appears.
- **Message chains**: long navigation `a.b().c().d()`. → hide it behind an operation of the first object.
- **Middle man**: a module that almost only delegates. → call the target directly.
- **Refused bequest** (only in languages with inheritance): a subclass ignores or overrides almost everything it inherits. → composition.

## Severity

Exactly one per finding:

- **blocker**: cannot be merged like this; it breaks correctness, security or a public contract, loses data or introduces a race.
- **major**: must be fixed before merging; a real bug in a plausible case, missing tests for new logic, bad error handling, or the violation of a rule the repo itself adopted.
- **minor**: worth fixing, with no immediate risk; clarity, an unlikely edge case, confusing names, style suggestions the repo did not adopt.
- **nit**: optional preference. Label it so the author knows they can ignore it.

## Output format

```markdown
## Review: <title of the change or the PR>

**Verdict:** request changes | comment | looks ready · **Intent:** <one line>
**Summary:** <2-3 lines: what it does well, what is missing, blast radius>
**Count:** Cross-cutting 0B/1M/2m/0n · Go 0B/0M/1m/1n · Spec 0B/1M/0m/0n

### Cross-cutting
- **major** `path/file.ext:LINE`: <what is wrong and why>. **Fix:** <concrete change>

### <Language>
- **minor** `path/file.ext:LINE`: … **Fix:** …

### Spec
- **major** <requirement quoted from the spec>: … **Fix:** …

### The good
- <one or two things the change does well>

### Not covered
- <languages without an idiomatic reviewer, or "there is no spec">
```

Omit empty sections.
