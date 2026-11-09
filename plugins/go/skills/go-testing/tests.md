# Good and bad tests (Go)

## Good tests

**Integration style**: they test through real interfaces, not through mocks of internal parts.

```go
// GOOD: tests observable behavior
func TestCheckout_WithValidCart_Confirms(t *testing.T) {
	cart := checkout.NewCart()
	cart.Add(product)

	got, err := checkout.Pay(ctx, cart, paymentMethod)
	if err != nil {
		t.Fatalf("Pay() error = %v", err)
	}
	if got.Status != checkout.StatusConfirmed {
		t.Errorf("Status = %q, want %q", got.Status, checkout.StatusConfirmed)
	}
}
```

Characteristics:

- Tests the behavior the caller cares about
- Uses only the exported API (ideally from `package checkout_test`)
- Survives internal refactors
- Describes WHAT, not HOW
- One logical assertion per test (or per table case)

**Table-driven**: several cases at the same seam, each with its own name.

```go
func TestFinalPrice(t *testing.T) {
	tests := []struct {
		name   string
		items  []Item
		coupon string
		want   Money
	}{
		{name: "without a coupon it adds up the items", items: []Item{{Price: 10}, {Price: 5}}, want: 15},
		{name: "10 percent coupon", items: []Item{{Price: 100}}, coupon: "TEN", want: 90},
		{name: "an empty cart costs zero", want: 0},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := FinalPrice(tt.items, tt.coupon); got != tt.want {
				t.Errorf("FinalPrice() = %v, want %v", got, tt.want)
			}
		})
	}
}
```

For large structs, compare with `cmp.Diff(want, got)` (`github.com/google/go-cmp`) and print the diff in the error. For long outputs (JSON, templates), use golden files in `testdata/` reviewed by hand.

**HTTP handlers**: test the `http.Handler` with `httptest`, not the internal functions.

```go
func TestListDevices_ReturnsTheCustomersDevices(t *testing.T) {
	srv := httptest.NewServer(api.NewRouter(fakeRepoWithTwoDevices()))
	defer srv.Close()

	resp, err := http.Get(srv.URL + "/customers/42/devices")
	if err != nil {
		t.Fatal(err)
	}
	if resp.StatusCode != http.StatusOK {
		t.Fatalf("status = %d, want 200", resp.StatusCode)
	}
	// decode and compare against an expected literal
}
```

## Bad tests

**Implementation-detail tests**: coupled to the internal structure.

```go
// BAD: tests implementation details
func TestCheckout_CallsPaymentProcess(t *testing.T) {
	mockPay := mocks.NewMockPaymentService(ctrl)
	mockPay.EXPECT().Process(gomock.Any(), cart.Total()).Times(1)
	checkout.Pay(ctx, cart, mockPay)
}
```

Red flags:

- Mocking internal collaborators (types of your own package)
- Testing unexported functions from `package foo` just to reach them
- Asserting the number or order of calls
- The test breaks on a refactor with no behavior change
- The test name describes HOW instead of WHAT
- Verifying from the outside instead of through the interface

```go
// BAD: bypasses the interface to verify
func TestCreateCustomer_SavesToDB(t *testing.T) {
	svc.CreateCustomer(ctx, "Alice")
	var n int
	db.QueryRow("SELECT count(*) FROM customers WHERE name = $1", "Alice").Scan(&n)
	if n != 1 { t.Fatal("not saved") }
}

// GOOD: verifies through the interface
func TestCreateCustomer_IsRetrievable(t *testing.T) {
	c, err := svc.CreateCustomer(ctx, "Alice")
	if err != nil { t.Fatal(err) }
	got, err := svc.GetCustomer(ctx, c.ID)
	if err != nil { t.Fatal(err) }
	if got.Name != "Alice" { t.Errorf("Name = %q, want %q", got.Name, "Alice") }
}
```

**Tautological tests**: the expected value repeats the implementation, so the test passes by construction.

```go
// BAD: the expected value is recomputed the same way as in the code
func TestTotal(t *testing.T) {
	items := []Item{{Price: 10}, {Price: 5}}
	var want Money
	for _, i := range items { want += i.Price }
	if got := Total(items); got != want { t.Errorf(...) }
}

// GOOD: the expected value is an independent literal
func TestTotal(t *testing.T) {
	if got := Total([]Item{{Price: 10}, {Price: 5}}); got != 15 {
		t.Errorf("Total() = %v, want 15", got)
	}
}
```
