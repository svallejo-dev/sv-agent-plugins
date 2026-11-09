# Tests buenos y malos (Go)

## Tests buenos

**Estilo integración**: testean a través de interfaces reales, no de mocks de partes internas.

```go
// BIEN: testea comportamiento observable
func TestCheckout_ConCarritoValido_Confirma(t *testing.T) {
	cart := checkout.NewCart()
	cart.Add(producto)

	got, err := checkout.Pay(ctx, cart, medioDePago)
	if err != nil {
		t.Fatalf("Pay() error = %v", err)
	}
	if got.Status != checkout.StatusConfirmed {
		t.Errorf("Status = %q, want %q", got.Status, checkout.StatusConfirmed)
	}
}
```

Características:

- Testea el comportamiento que le importa al llamador
- Usa solo la API exportada (idealmente desde `package checkout_test`)
- Sobrevive a refactors internos
- Describe QUÉ, no CÓMO
- Una aserción lógica por test (o por caso de la tabla)

**Table-driven**: varios casos en el mismo seam, cada uno con su nombre.

```go
func TestPrecioFinal(t *testing.T) {
	tests := []struct {
		name  string
		items []Item
		cupon string
		want  Money
	}{
		{name: "sin cupón suma los items", items: []Item{{Price: 10}, {Price: 5}}, want: 15},
		{name: "cupón del 10 por ciento", items: []Item{{Price: 100}}, cupon: "DIEZ", want: 90},
		{name: "carrito vacío cuesta cero", want: 0},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := PrecioFinal(tt.items, tt.cupon); got != tt.want {
				t.Errorf("PrecioFinal() = %v, want %v", got, tt.want)
			}
		})
	}
}
```

Para structs grandes, compara con `cmp.Diff(want, got)` (`github.com/google/go-cmp`) e imprime el diff en el error. Para salidas largas (JSON, plantillas), usa archivos golden en `testdata/` revisados a mano.

**Handlers HTTP**: testea el `http.Handler` con `httptest`, no las funciones internas.

```go
func TestListarDispositivos_DevuelveLosDelCliente(t *testing.T) {
	srv := httptest.NewServer(api.NewRouter(fakeRepoConDosDispositivos()))
	defer srv.Close()

	resp, err := http.Get(srv.URL + "/clientes/42/dispositivos")
	if err != nil {
		t.Fatal(err)
	}
	if resp.StatusCode != http.StatusOK {
		t.Fatalf("status = %d, want 200", resp.StatusCode)
	}
	// decodifica y compara contra un literal esperado
}
```

## Tests malos

**Tests de detalles de implementación**: acoplados a la estructura interna.

```go
// MAL: testea detalles de implementación
func TestCheckout_LlamaAPaymentProcess(t *testing.T) {
	mockPay := mocks.NewMockPaymentService(ctrl)
	mockPay.EXPECT().Process(gomock.Any(), cart.Total()).Times(1)
	checkout.Pay(ctx, cart, mockPay)
}
```

Señales de alarma:

- Mockear colaboradores internos (tipos de tu propio paquete)
- Testear funciones no exportadas desde `package foo` solo para llegar a ellas
- Asertar número u orden de llamadas
- El test se rompe al refactorizar sin cambio de comportamiento
- El nombre del test describe CÓMO en vez de QUÉ
- Verificar por fuera en vez de por la interfaz

```go
// MAL: se salta la interfaz para verificar
func TestCrearCliente_GuardaEnDB(t *testing.T) {
	svc.CrearCliente(ctx, "Alice")
	var n int
	db.QueryRow("SELECT count(*) FROM clientes WHERE nombre = $1", "Alice").Scan(&n)
	if n != 1 { t.Fatal("no se guardó") }
}

// BIEN: verifica por la interfaz
func TestCrearCliente_QuedaRecuperable(t *testing.T) {
	c, err := svc.CrearCliente(ctx, "Alice")
	if err != nil { t.Fatal(err) }
	got, err := svc.ObtenerCliente(ctx, c.ID)
	if err != nil { t.Fatal(err) }
	if got.Nombre != "Alice" { t.Errorf("Nombre = %q, want %q", got.Nombre, "Alice") }
}
```

**Tests tautológicos**: el valor esperado repite la implementación, así que el test pasa por construcción.

```go
// MAL: el esperado se recalcula igual que en el código
func TestTotal(t *testing.T) {
	items := []Item{{Price: 10}, {Price: 5}}
	var want Money
	for _, i := range items { want += i.Price }
	if got := Total(items); got != want { t.Errorf(...) }
}

// BIEN: el esperado es un literal independiente
func TestTotal(t *testing.T) {
	if got := Total([]Item{{Price: 10}, {Price: 5}}); got != 15 {
		t.Errorf("Total() = %v, want 15", got)
	}
}
```
