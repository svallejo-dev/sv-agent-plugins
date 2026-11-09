# Cuándo usar dobles de test

Ejemplos en pseudocódigo. Para las herramientas y la forma idiomática en un lenguaje concreto, usa la skill `<lenguaje>-testing` si está disponible.

Usa dobles solo en las **fronteras del sistema**:

- APIs externas (pasarelas de pago, partners, proveedores de auth)
- Bases de datos (a veces; prefiere una base real de test)
- Tiempo y aleatoriedad
- Sistema de archivos (a veces; un directorio temporal suele bastar)

No uses dobles para:

- Tus propios módulos
- Colaboradores internos
- Nada que controles

Analogía: un doble es un actor de reparto que sustituye a alguien que no puedes traer al set (el banco, el partner). A tus propios actores los dejas actuar.

## Preferencias

1. **Dependencia real antes que doble.** Para bases de datos, colas o caches, usa una instancia real de test (un contenedor o la de CI). Un doble de base de datos testea tu suposición sobre la base, no la base.
2. **Fakes escritos a mano antes que mocks generados.** Un fake en memoria que implementa la interfaz da tests que se leen como el uso real. Los mocks generados, solo para APIs externas difíciles de simular, y aun así asertando resultados, no llamadas.
3. **Servidor HTTP falso para APIs externas.** Levanta un servidor local que responde como el partner y apunta el cliente a su URL: testeas el cliente real, el parseo y los errores.

## Diseñar para poder sustituir

**1. Inyecta dependencias**

```text
// Fácil de sustituir
procesarPago(orden, cobrador):
    return cobrador.cobrar(orden.total)

// Difícil de sustituir
procesarPago(orden):
    cliente = nuevoClienteGestorPagos(env("GESTOR_PAGOS_KEY"))
    return cliente.cobrar(orden.total)
```

**2. Interfaces pequeñas definidas por quien las usa**

Declara la interfaz donde se consume, con solo las operaciones que ese consumidor necesita, no junto a la implementación con todo lo que ofrece.

**3. Operaciones específicas antes que un fetcher genérico**

```text
// BIEN: cada operación se sustituye por separado
interfaz ClientePartner:
    obtenerUsuario(id) -> Usuario
    listarSuscripciones(usuarioId) -> [Suscripcion]
    crearSuscripcion(datos) -> Suscripcion

// MAL: el doble necesita lógica condicional dentro
interfaz ClientePartner:
    hacer(método, ruta, cuerpo) -> bytes
```

Con operaciones específicas, cada doble devuelve una forma concreta, no hay lógica condicional en el setup, se ve qué operaciones usa cada test y hay tipado por operación.

**4. El tiempo también se inyecta**

Pasa un reloj (o una función que devuelve "ahora") como dependencia. En producción es el reloj del sistema; en el test, una fecha fija.
