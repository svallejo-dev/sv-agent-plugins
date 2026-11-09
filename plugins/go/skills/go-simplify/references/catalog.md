# Catalog of judgment simplifications

Each entry has a before, an after and its **limit**: when not to apply it. If the `senior-go-idiomatic` skill is available, it owns the style criteria; this catalog is the operational version for simplifying.

## 1. Comments

A well-chosen name already says **what** the code does; the comment explains **why**.

```go
// Before
// ---------- Helpers ----------

// getUser gets the user
func getUser(id string) (*User, error) {
	// call the repository
	u, err := repo.Find(id)
	// if err != nil { log.Println(err) }
	return u, err
}

// After
func getUser(id string) (*User, error) {
	return repo.Find(id)
}
```

- Out go: banners, narration (`// call the repository`), commented-out code, comments that repeat the name.
- **Exported** identifiers keep their doc comment, one line, starting with the name: `// FindActive returns…`.
- What stays: the **why** (an external constraint, a workaround with a link to the issue, a non-obvious invariant), `//go:` and `//nolint` with a reason, and `TODO`s with an owner or issue.

**Limit:** if you do not know whether a comment explains a real why, leave it and ask about it in the report.

## 2. Local noise

```go
// Before
func isAdult(age int) bool {
	result := false
	if age >= 18 {
		result = true
	} else {
		result = false
	}
	return result
}

// After
func isAdult(age int) bool {
	return age >= 18
}
```

```go
// Before
if err != nil {
	return err
} else {
	process(x)
}

// After
if err != nil {
	return err
}
process(x)
```

- Variables used once that do not contribute a useful name, assignments that overwrite each other, conversions to a type the value already has.

**Limit:** an intermediate variable with a good name that explains a computation **does** contribute: do not inline it. Being shorter is not enough; it has to read better.

## 3. Nesting

```go
// Before
func Process(o *Order) error {
	if o != nil {
		if o.Valid() {
			if len(o.Items) > 0 {
				return save(o)
			}
			return ErrNoItems
		}
		return ErrInvalid
	}
	return ErrNil
}

// After
func Process(o *Order) error {
	if o == nil {
		return ErrNil
	}
	if !o.Valid() {
		return ErrInvalid
	}
	if len(o.Items) == 0 {
		return ErrNoItems
	}
	return save(o)
}
```

- Guard clauses: the happy path stays on the left, unindented.
- `if x == a … else if x == b` chains on the same value become a `switch`.

**Limit:** when inverting conditions, watch out for `NaN`, nil pointers inside the condition and short-circuit evaluation with side effects. The tests must cover each branch; if not, leave the nesting.

## 4. Errors

```go
// Before
u, err := repo.Find(ctx, id)
if err != nil {
	log.Printf("error finding user: %v", err)
	return nil, errors.New(fmt.Sprintf("find user: %v", err))
}

// After
u, err := repo.Find(ctx, id)
if err != nil {
	return nil, fmt.Errorf("find user %s: %w", id, err)
}
```

- Wrap with `%w` (so `errors.Is` and `errors.As` keep working) and add context once per layer.
- No "log and return": either handle it (and log it) or return it, not both.

**Limit:** **do not change the text** of an error others may compare (sentinel errors, messages that reach API clients) or switch from `%v` to `%w` at a boundary where exposing the internal error is a problem. That is a behavior change: propose it, do not do it.

## 5. Unexported dead code

- Unused unexported functions, types, constants and fields; parameters no implementation uses in unexported functions.
- Confirm it with tools: the compiler for imports and variables, `staticcheck -checks U1000` for what is unused, and a search for uses via reflection, templates or `//go:linkname`.

**Limit:** nothing exported (another module may use it) and nothing referenced by name from outside the Go code (configuration, reflection, generators).

## 6. Local duplication

```go
// Before: the same block in three handlers
if r.Header.Get("X-Tenant") == "" {
	http.Error(w, "missing tenant", http.StatusBadRequest)
	return
}

// After
tenant, ok := tenantFrom(w, r)
if !ok {
	return
}
```

- Extract it into an unexported function of the **same package** when the logic is the same and changes for the same reasons.

**Limit:** two blocks that look alike but change for different reasons are not duplication (that is accidental coupling). When in doubt, rule of three: do not extract until the third repetition.

## What the tools already do (do not do it by hand)

`gofmt -s`, `goimports` and the `go fix` modernizers cover: `interface{}` → `any`, search loops → `slices.Contains`/`slices.Index`, min and max computations → `min`/`max`, `for i := 0; i < n; i++` → `for i := range n`, map copies → `maps.Copy`, pointer helpers → `new(expr)`, `errors.As` with a variable → `errors.AsType`, and more. Run the tool instead of rewriting it: the result is deterministic and respects the module's Go version.
