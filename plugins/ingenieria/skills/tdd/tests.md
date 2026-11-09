# Tests buenos y malos

Ejemplos en pseudocódigo. Para la forma idiomática en un lenguaje concreto, usa la skill `<lenguaje>-testing` si está disponible.

## Tests buenos

**Estilo integración**: testean a través de interfaces reales, no de mocks de partes internas.

```text
// BIEN: testea comportamiento observable
test "el cliente puede pagar con un carrito válido":
    carrito = nuevoCarrito()
    carrito.agregar(producto)
    resultado = pagar(carrito, medioDePago)
    esperar resultado.estado == CONFIRMADO
```

Características:

- Testea el comportamiento que le importa al llamador
- Usa solo la API pública
- Sobrevive a refactors internos
- Describe QUÉ, no CÓMO
- Una aserción lógica por test (o por caso)

**Casos en tabla**: varios casos en el mismo seam, cada uno con su nombre, cuando comparten la misma forma.

```text
casos:
    "sin cupón suma los items"     items=[10, 5]   cupón=—        esperado=15
    "cupón del 10 por ciento"      items=[100]     cupón="DIEZ"   esperado=90
    "carrito vacío cuesta cero"    items=[]        cupón=—        esperado=0
para cada caso:
    esperar precioFinal(caso.items, caso.cupón) == caso.esperado
```

## Tests malos

**Tests de detalles de implementación**: acoplados a la estructura interna.

```text
// MAL: testea detalles de implementación
test "pagar llama a servicioDePagos.procesar":
    mockPagos = mock(servicioDePagos)
    pagar(carrito, mockPagos)
    esperar mockPagos.procesar fue llamado 1 vez con carrito.total
```

Señales de alarma:

- Mockear colaboradores internos
- Testear funciones privadas
- Asertar número u orden de llamadas
- El test se rompe al refactorizar sin cambio de comportamiento
- El nombre del test describe CÓMO en vez de QUÉ
- Verificar por fuera en vez de por la interfaz

```text
// MAL: se salta la interfaz para verificar
test "crearCliente guarda en la base":
    crearCliente("Alice")
    fila = db.consultar("SELECT * FROM clientes WHERE nombre = 'Alice'")
    esperar fila existe

// BIEN: verifica por la interfaz
test "crearCliente deja al cliente recuperable":
    c = crearCliente("Alice")
    esperar obtenerCliente(c.id).nombre == "Alice"
```

**Tests tautológicos**: el valor esperado repite la implementación, así que el test pasa por construcción.

```text
// MAL: el esperado se recalcula igual que en el código
test "total suma los items":
    items = [10, 5]
    esperado = suma(items)
    esperar total(items) == esperado

// BIEN: el esperado es un literal independiente
test "total suma los items":
    esperar total([10, 5]) == 15
```
