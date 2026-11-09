---
name: go-review
description: "Go-specific review rules for the .go files of a diff or a PR (Go correctness, idioms, the house layout and DDD). The code-review skill loads it for its Go reviewer; also use it when the user asks to review only Go code."
license: MIT
---

# Go review

Respond in the user's language; keep common technical terms in English.

Rules for the Go reviewer. They apply **only to the `.go` files** and **on top of** the cross-cutting rubric of `code-review`: do not repeat the cross-cutting concerns (security, tests, compatibility, size) unless the problem is a mechanism specific to Go. Each finding carries a severity (blocker / major / minor / nit), `path:line`, why and a concrete fix.

`<SHA>` is the reviewed commit: `HEAD` in a local diff, or a PR's `headRefOid` (read after `git fetch <remote> "pull/<n>/head"`, never from the working tree).

## Who owns each rule

Each rule has an owning skill in this plugin; this skill only points to them. For the full rule and its reasoning, invoke the owner.

| Area | Owner |
|---|---|
| Bounded-context layout, one use case per file, use-case shape, ports, placement of infrastructure | `ddd-go-idiomatic` |
| Design principles: Law of Demeter, Tell-Don't-Ask, CQS, named types, illegal states, explicit dependencies | `go-design-rules` |
| Comment policy, idioms, errors, concurrency, I/O, testing, tooling | `senior-go-idiomatic` |

If a DDD or OOP principle clashes with Go idioms, Go idioms win: one interface per struct, a `mapper/` package, getters/setters or folders per layer are findings even if they "follow DDD".

## Step 1: does the repo adopt the house rules?

The layout and comment rules are a team's conventions, not universal Go. Check adoption at `<SHA>`:

```bash
git cat-file -e "<SHA>:.claude/skills/ddd-go-idiomatic/SKILL.md" 2>/dev/null && echo adopted
for f in AGENTS.md CLAUDE.md .claude/CLAUDE.md; do
  git show "<SHA>:$f" 2>/dev/null | grep -Eiq 'ddd-go-idiomatic|one use case per file' && echo "adopted via $f"
done
```

(Without a local clone, read the same paths with `gh api "repos/<owner>/<repo>/contents/<path>?ref=<SHA>"`; a 404 means it does not exist.)

- **Adopted** → layout violations are **major** and comment-policy violations **minor**, citing the owning skill.
- **Not adopted** → report them as **minor** or **nit** "house style suggestions", grouped, and never let them drive a request-changes verdict. Follow the patterns the repo already uses instead of imposing new ones.

## Step 2: quick detection

```bash
files=$(git diff --name-only <base>...<SHA> | grep '\.go$')   # in a PR: gh pr diff <n> --name-only | grep '\.go$'
# catch-all file names
printf '%s\n' "$files" | grep -E '(^|/)(service|services|usecase|usecases|use_cases|application|app|manager|helpers|utils|common)\.go$'
# catch-all types added
git diff <base>...<SHA> -- $files | grep -E '^\+type ([A-Za-z]*(Service|UseCase|Manager)) struct'
# several exported methods with ctx on the same receiver (more than one use case per file?)
for f in $(printf '%s\n' "$files" | grep -v '_test\.go$'); do
  c=$(git show "<SHA>:$f" 2>/dev/null | grep -cE '^func \([a-z]+ \*?[A-Z][A-Za-z0-9_]*\) [A-Z][A-Za-z0-9_]*\(ctx context\.Context')
  [ "${c:-0}" -gt 1 ] && echo "$f: $c exported methods with ctx"
done
# comment banners added
git diff <base>...<SHA> -- $files | grep -nE '^\+[[:space:]]*// ?[-=]{4,}'
```

Each match is a candidate: confirm it by reading the file. Adapters (stores, repositories) legitimately implement several methods of a port; a composition root (`cmd/<app>/main.go`, `internal/handlers/handlers.go`) legitimately wires many routes.

## Step 3: Go correctness (any repo)

General Go bugs, with severity according to their impact (owner: `senior-go-idiomatic`):

- **Errors**: swallowed (`_ = f()`), compared with `==` instead of `errors.Is/As`, or returned without context at a package boundary (wrap with `fmt.Errorf("operation: %w", err)`). A typed nil returned as `error`.
- **`context.Context`**: not the first parameter or not propagated in calls with I/O; stored in a struct; `context.Background()` halfway through a chain.
- **Goroutines**: without a clear end (no `ctx.Done()`, close channel, `WaitGroup` or `errgroup`); `time.After` inside loops.
- **Concurrency**: data races, concurrent map writes, a `sync.Mutex` copied by value.
- **Slices and loops**: `append` sharing the backing array; mutating the `range` copy instead of `xs[i]`.
- **Interfaces**: declared next to their only implementation without a real seam, or wide when the consumer uses one or two methods (move them to the consumer and trim them).
- **Global state**: mutable package-level state, `init()` with side effects, hidden singletons.
- **`panic`** as control flow outside `main` or initialization.
- **Packages** `util`, `common`, `helpers`: each function goes to the package of the concept it serves.

## Step 4: domain modeling (if the change touches a domain package)

Owner: `ddd-go-idiomatic`. Look for value objects that can be built without validation, entities with setters instead of intention-revealing methods, aggregates referenced by pointer instead of by ID, domain packages that import `database/sql`, `net/http` or `encoding/json`, and driver errors (`sql.ErrNoRows`) leaking out of the repository. Severity according to impact; a leaked infrastructure import in a repo that adopted the house rules is major.

## What is not reported

What `gofmt`, `go vet` and the repo's configured `golangci-lint` already guarantee.
