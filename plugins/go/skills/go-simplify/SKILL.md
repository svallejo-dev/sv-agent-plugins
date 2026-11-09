---
name: go-simplify
description: "Simplifies Go code without changing its behavior: removes noise, narrating comments, dead code, nesting and old idioms, first with deterministic tools (gofmt -s, goimports, go fix with the Go 1.26 modernizers, staticcheck S1) and then with a catalog of judgment simplifications, with green tests before and after each step. Use it when the user asks to simplify, clean up, polish, modernize or remove noise from Go code, \"/simplify\" in Go, or \"make it more idiomatic without changing what it does\"."
license: MIT
---

# Simplifying Go

Respond in the user's language; keep common technical terms in English.

Simplifying is **removing without changing what the code does**. The result reads faster, has fewer branches and less noise, and behaves exactly the same: same outputs, same errors, same API, same effects and in the same order.

**Analogy:** a copy editor, not a co-author. They cut the extra word, join the sentence split in three and remove the footnote that repeats the text, but they do not change the book's argument. If improving it requires changing the argument, that is another job (`codebase-design` or a ticket), not a simplification.

## Non-negotiable rules

1. **Identical behavior.** The exported API does not change (names, signatures, types, struct tags), nor the error text (someone may compare it), nor log and metric names, nor the order of effects, nor the concurrency semantics.
2. **A safety net before cutting.** Without build, `go vet` and tests green before starting, nothing is simplified. Without tests covering the touched code, only the changes the tools guarantee are applied (mechanical layer).
3. **Small, verified changes.** One category at a time, tests after each. If something turns red, that category is reverted; the test is not "fixed".
4. **Not touched:** generated code (`// Code generated ... DO NOT EDIT.`), `vendor/`, `testdata/`, and, if the repo uses the `qa` plugin, the sealed acceptance folder.
5. **Simplifying is not removing defenses.** A validation, error handling or timeout that looks redundant is asked about before deleting it.

The style criteria (comments, names, errors, idioms) belong to `senior-go-idiomatic`: this skill applies them, it does not redefine them. If it is available, load it; if not, use the catalog in [references/catalog.md](references/catalog.md).

## 1. Scope

- **By default, what changed**: the `.go` files of the diff against the base branch, plus what is uncommitted.
  ```bash
  git diff --name-only "$(git merge-base HEAD origin/main)" -- '*.go'; git diff --name-only -- '*.go'
  ```
- **If the user names files or packages**, those.
- **The whole repository only if they explicitly ask.** A huge simplification diff cannot be reviewed, and what is not reviewed is not safe.

Filter out generated files: `grep -L '^// Code generated .* DO NOT EDIT\.$'`. Note the affected packages: they are the ones that get built and tested at each step.

## 2. Baseline

```bash
go build ./... && go vet <packages> && go test -count=1 <packages>
```

Add `-race` if the touched code uses goroutines or shared state. Save the result (packages and number of tests): it is the baseline the end is compared against.

- If something is red, **stop**: report what fails and do not simplify until the user decides.
- If a file in scope has no tests exercising its functions (`go test -cover` shows it per package), mark it **"no safety net"**: only the mechanical layer goes into it.

## 3. Mechanical layer (deterministic)

Tools that guarantee safe changes. Apply them in this order, with tests after each one:

| Step | Command | What it does |
|---|---|---|
| a | `gofmt -s -w <files>` | Formatting and syntactic simplifications (composite literals, ranges, slices) |
| b | `goimports -w <files>` (if installed) | Sorts and cleans up imports |
| c | `go fix -diff <packages>` and then `go fix <packages>` | The Go 1.26 modernizers: `any`, `min`/`max`, `slices`/`maps`, ranges over integers, `new(expr)`, `errors.AsType` and more. It only proposes what the `go.mod` version allows. Repeat until there are no changes: one fix enables another |
| d | `staticcheck -checks 'S1*' <packages>` (if installed) | The S1 family of simplifications: return a boolean expression directly, `fmt.Errorf` instead of `errors.New(fmt.Sprintf(...))`, `append` instead of copy loops… Apply them by hand |
| e | `golangci-lint run <packages>` (if the repo has a configuration) | What the team already decided to require |

If `go fix` proposes something that changes behavior in your case (for example, in a file with build tags), disable that specific analyzer (`go fix -<analyzer>=false`) and say so in the report.

## 4. Judgment layer

Only in files with a safety net. Go through the catalog by category, in this order (from lowest to highest risk), with tests after each one:

1. **Comments**: narration, banners, commented-out code, comments that repeat the name; docs of exported identifiers that do not start with the identifier.
2. **Local noise**: variables used once without contributing a name, redundant assignments, unnecessary conversions, `else` after `return`.
3. **Nesting**: guard clauses and early return, merged conditions, `switch` instead of `if` chains.
4. **Errors**: context with `%w` once per layer, no "log and return", no wrapping the same message twice.
5. **Unexported dead code**: unused functions, types, constants and parameters (confirm it with the compiler or `staticcheck -checks U1000`, not by eye).
6. **Local duplication**: the same logic repeated within the scope, extracted into an unexported function in the same package.

Before-and-after examples, and the limits of each category, in [references/catalog.md](references/catalog.md).

**Out of scope** (propose it, do not do it): changing the exported API, moving code between packages, introducing or removing exported interfaces, performance changes without a benchmark, design refactors. That goes to `codebase-design` or to a ticket.

## 5. Final verification

```bash
gofmt -l <files>            # must print nothing
go build ./... && go vet <packages> && go test -count=1 <packages>   # same as the baseline
```

The number of tests must be the same as in the baseline: if it went down, something was deleted. If the `go-review` skill exists, give it the diff for an independent review; if not, reread the whole diff looking for behavior changes.

## 6. Report

- Baseline and final verification (packages, tests, `-race` yes or no).
- Changes per layer and per category, with `file:line` for the relevant ones.
- **What was not touched and why**: files without a safety net, out-of-scope proposals, disabled analyzers, defenses that looked redundant and remain as a question.
- Proposed commits: one for the mechanical layer and one per judgment category. Do not commit unless the user asks; if they ask and the `git-commit` skill exists, use it.
