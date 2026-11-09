# Técnicas de diseño de pruebas

Cada sección se pega completa al sub-agente de su familia. Son las técnicas de caja negra del programa ISTQB (Foundation y Test Analyst) más las de fallo y entorno que exige un sistema distribuido. Todas sirven para lo mismo: **elegir de forma sistemática qué probar**, para que la cobertura no dependa de la intuición del día.

---

## Familia A: particiones de equivalencia y valores límite

### Particiones de equivalencia

**Qué es:** dividir cada entrada (y cada salida) en clases que el sistema debería tratar igual. Un valor representativo por clase basta; probar diez valores de la misma clase no añade información.

**Analogía:** para comprobar si una máquina de café acepta monedas no pruebas todas las monedas de 500; pruebas una de 500, una de 1000, una extranjera y una ficha falsa.

**Cómo derivarlas:**
1. Para cada entrada del criterio, lista las clases **válidas** y las **inválidas** (tipo equivocado, vacío, ausente, fuera de rango, formato inválido).
2. Haz lo mismo con las **salidas**: cada respuesta distinta (201, 409, 422…) es una clase que necesita al menos un escenario que la produzca.
3. Un escenario por clase válida; las válidas se pueden combinar en un mismo escenario. **Las inválidas, una por escenario**: si mezclas dos inválidas, un rechazo no te dice cuál de las dos lo causó (enmascaramiento).

### Valores límite

**Qué es:** los defectos se concentran en los bordes de las particiones (`<` en vez de `<=`, errores por uno).

**Cómo derivarlos:** para cada frontera ordenada, prueba el valor justo en el límite y el inmediatamente fuera. En la variante de **tres valores** (recomendada para límites de negocio críticos), también el inmediatamente dentro.

Ejemplo, máximo 5 dispositivos por cliente:

```gherkin
Esquema del escenario: ESC-04 registrar con <actuales> dispositivos ya registrados
  Dado un cliente con <actuales> dispositivos registrados
  Cuando registra un nuevo dispositivo
  Entonces la respuesta es <estado>
  Y el cliente queda con <final> dispositivos
  Ejemplos:
    | actuales | estado | final |
    | 0        | 201    | 1     |
    | 4        | 201    | 5     |
    | 5        | 409    | 5     |
```

Fíjate en la segunda aserción: el 409 solo no basta; el oráculo verifica también que **no se creó** el sexto.

**Límites que se olvidan:** cadenas vacías y de longitud máxima, listas vacías y de un elemento, cero y negativos, la primera y la última página de una paginación, montos con la máxima precisión decimal, fechas en cambio de mes o de año, el último segundo antes de una expiración.

**Errores comunes:** probar solo el valor dentro; probar límites que la spec no define (pregunta antes de inventar uno); olvidar los límites de las salidas.

---

## Familia B: tablas de decisión, transición de estados y combinatoria

### Tablas de decisión

**Qué es:** cuando el resultado depende de la **combinación** de varias condiciones, una tabla con una columna por regla hace visible cada combinación, incluidas las que nadie especificó.

**Cómo:** lista las condiciones (filas de arriba) y las acciones (filas de abajo); enumera las combinaciones; colapsa las que dan igual con "—"; **cada columna es un escenario**. Una columna cuya acción nadie sabe es una **pregunta para la spec**: ese es el valor principal de la técnica.

| Condición / acción | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Comprador nuevo | S | S | N | N |
| Quiere guardar el método | N | S | — | — |
| Tiene método guardado | — | — | S | N |
| **Token a entregar** | client_token | id_token | id_token + customer | ¿? |

R4 (comprador recurrente sin método guardado) es una pregunta abierta, no un escenario que se inventa.

### Transición de estados

**Qué es:** cuando el sistema tiene estados con nombre (pedido, pago, suscripción, sesión), los defectos viven en las transiciones: las válidas que fallan y, sobre todo, las inválidas que el sistema acepta.

**Cómo:**
1. Dibuja (o pide) la máquina de estados: estados, eventos y transiciones válidas.
2. **Cobertura mínima:** cada transición válida al menos una vez (cobertura 0-switch).
3. **Transiciones inválidas:** para cada estado, cada evento que no debería aceptarse en él (reembolsar un pago pendiente, cancelar uno ya cancelado). Una por escenario.
4. **Secuencias críticas:** las de ida y vuelta (pausar → reanudar → pausar) y las que repiten un evento (doble captura).

Si nadie puede dibujar la máquina, **es un hallazgo de spec**.

### Combinatoria (pairwise)

**Cuándo:** muchos parámetros independientes con varios valores cada uno (país × moneda × método × dispositivo). Probar todas las combinaciones es inviable; la mayoría de los defectos combinatorios aparecen con la interacción de **dos** parámetros.

**Cómo:** genera un conjunto que cubra cada par de valores al menos una vez con una herramienta (PICT de Microsoft, o la librería equivalente del lenguaje); no lo hagas a mano. Agrega aparte las combinaciones de riesgo conocido. Pairwise **no** reemplaza a la tabla de decisión cuando las condiciones no son independientes.

---

## Familia C: integración con terceros y oráculo de uso

Usa completa la checklist de [terceros.md](terceros.md) y la regla de [oraculo-de-uso.md](../../qa-acceptance-criteria/references/oraculo-de-uso.md). En resumen:

1. Por cada artefacto que el sistema produce para otro: un escenario con el **consumidor real** como oráculo (normalmente peldaño 3) y, si existe contrato, uno de contrato (peldaño 2).
2. Por cada tercero: la tabla de decisión **flujo × variante** de lo que el tercero devuelve, la **clave de caché** de todo lo que se cachea y el **catálogo de errores** del tercero.
3. **Learning tests** contra el sandbox (peldaño 2) para cada suposición sobre el tercero que algún escenario usa. Para servicios propios, un escenario de contrato Pact; para terceros, nunca Pact como puerta.
4. El **walking skeleton** como primer escenario.

---

## Familia D: fallos y entorno

Estos escenarios casi siempre van en **peldaño 1**, porque requieren controlar el entorno (Toxiproxy, fakes, reloj). Para cada dependencia del handoff:

| Fallo | Escenario | Oráculo |
|---|---|---|
| Latencia alta (por encima del timeout) | Toxiproxy `latency` | El sistema corta en su timeout y responde un error limpio; no se cuelga |
| Conexión rechazada o cortada | Proxy deshabilitado, o toxic `reset_peer` / `timeout` | Error limpio; se recupera cuando vuelve |
| Respuesta 5xx o 429 | Fake del tercero | Reintento con backoff dentro del presupuesto; 429 respeta `Retry-After` |
| Respuesta lenta a medias | Toxiproxy `slicer` o `limit_data` | No se procesa una respuesta truncada como válida |
| **Timeout después de que el tercero ejecutó** | Fake que ejecuta y luego tarda | Reintentar no duplica el efecto (idempotencia) |
| Respuesta inesperada pero válida | Fake con una variante real no contemplada | Se rechaza o se maneja de forma explícita; nunca se interpreta mal en silencio |

Además:
- **Idempotencia** como relación metamórfica: aplicar dos veces la misma petición con la misma clave produce el mismo resultado y un solo efecto.
- **Concurrencia**: dos peticiones simultáneas sobre el mismo recurso (el último cupo, el mismo pago). El oráculo es el invariante (no hay sobreventa, no hay doble cobro), no la respuesta individual.
- **Tiempo**: expiraciones justo antes y justo después del límite; requiere reloj controlable (seam del handoff).
- **Datos**: el recurso que otro proceso borró a mitad del flujo, el registro con campos opcionales ausentes, caracteres no ASCII.
- Si hay arquetipo de negocio, cada **modo de fallo típico** del arquetipo es un candidato a escenario.

---

## Familia E: error guessing, abuso y seguridad básica

**Error guessing** es la técnica basada en experiencia: probar donde los sistemas suelen fallar. Es legítima siempre que sea **sistemática**: una checklist, no la inspiración del momento.

Checklist mínima:
- **Autorización horizontal**: el cliente A pide, modifica o borra un recurso del cliente B cambiando el ID (IDOR).
- **Autorización vertical**: un usuario sin rol de administrador llama un endpoint de administración.
- **Entradas hostiles**: cadenas muy largas, caracteres de control, inyección en campos que terminan en consultas o en logs, JSON con campos extra o duplicados, tipos cambiados.
- **Reenvío y repetición**: el mismo request reenviado; el webhook duplicado; el token reutilizado tras expirar.
- **Datos sensibles**: tokens, secretos o datos personales en respuestas de error, logs o mensajes que no deberían contenerlos.
- **Abuso de volumen**: sin límite de tasa en un endpoint costoso o enumerable.
- **Incidentes previos**: cada incidente pasado del sistema es un escenario de regresión.

El fuzzing de contrato a partir del OpenAPI (Schemathesis) complementa esta familia en el ritmo completo: genera miles de entradas inesperadas que ningún humano escribiría.
