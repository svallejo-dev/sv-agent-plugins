# Good and bad tests

Examples in pseudocode. For the idiomatic form in a specific language, use the `<language>-testing` skill if available.

## Good tests

**Integration style**: they test through real interfaces, not through mocks of internal parts.

```text
// GOOD: tests observable behavior
test "the customer can pay with a valid cart":
    cart = newCart()
    cart.add(product)
    result = pay(cart, paymentMethod)
    expect result.status == CONFIRMED
```

Characteristics:

- Tests the behavior the caller cares about
- Uses only the public API
- Survives internal refactors
- Describes WHAT, not HOW
- One logical assertion per test (or per case)

**Table cases**: several cases at the same seam, each with its own name, when they share the same shape.

```text
cases:
    "without a coupon it adds up the items"   items=[10, 5]   coupon=—       expected=15
    "10 percent coupon"                       items=[100]     coupon="TEN"   expected=90
    "an empty cart costs zero"                items=[]        coupon=—       expected=0
for each case:
    expect finalPrice(case.items, case.coupon) == case.expected
```

## Bad tests

**Implementation-detail tests**: coupled to the internal structure.

```text
// BAD: tests implementation details
test "pay calls paymentService.process":
    paymentMock = mock(paymentService)
    pay(cart, paymentMock)
    expect paymentMock.process was called 1 time with cart.total
```

Red flags:

- Mocking internal collaborators
- Testing private functions
- Asserting the number or order of calls
- The test breaks on a refactor with no behavior change
- The test name describes HOW instead of WHAT
- Verifying from the outside instead of through the interface

```text
// BAD: bypasses the interface to verify
test "createCustomer saves to the database":
    createCustomer("Alice")
    row = db.query("SELECT * FROM customers WHERE name = 'Alice'")
    expect row exists

// GOOD: verifies through the interface
test "createCustomer leaves the customer retrievable":
    c = createCustomer("Alice")
    expect getCustomer(c.id).name == "Alice"
```

**Tautological tests**: the expected value repeats the implementation, so the test passes by construction.

```text
// BAD: the expected value is recomputed the same way as in the code
test "total adds up the items":
    items = [10, 5]
    expected = sum(items)
    expect total(items) == expected

// GOOD: the expected value is an independent literal
test "total adds up the items":
    expect total([10, 5]) == 15
```
