# Checklist de integración con terceros

Los terceros son la fuente más cara de defectos que nadie vio venir: su comportamiento real no está en tu código ni en tu cabeza, está en su sistema. Un fake o un mock solo sabe lo que **tú creías**. Esta checklist convierte cada creencia sobre el tercero en una pregunta explícita, y cada respuesta en un escenario.

**Analogía:** antes de mudarte a otro país no basta con saber que "tienen enchufes". Preguntas qué voltaje, qué forma de clavija y si cambia entre el baño y la cocina. El adaptador que compraste por intuición es el bug.

## 1. Variantes: ¿el tercero devuelve cosas distintas según parámetros o flujo?

- ¿El mismo endpoint devuelve **tipos distintos** según un parámetro (`response_type`, `intent`, `grant_type`, versión de API, país)?
- ¿Dos variantes comparten **el mismo campo o el mismo esquema** con significado distinto? (La trampa más peligrosa: la validación de forma pasa.)
- ¿Qué variante necesita **cada flujo** de la feature? Construye la tabla de decisión **flujo × variante** (técnicas, familia B). Una celda que nadie sabe llenar es una pregunta para la spec.

## 2. Caché: ¿de qué depende lo que guardas?

Para todo lo que se cachea de un tercero:
- ¿El valor depende del **cliente**, del **dominio**, del **intent**, del **país**, de la **sesión**? Todo eso forma parte de la **clave de caché**. Si la clave es más pobre que la dependencia real, la caché entrega a uno lo que era de otro.
- ¿Qué **TTL**? ¿Viene del tercero (`expires_in`) con margen, o es un número fijo inventado?
- ¿Qué pasa si el tercero **revoca** antes del TTL?
- Escenarios obligatorios: dos clientes distintos piden en secuencia y **nunca** reciben el mismo valor personal; el valor expirado no se entrega.

## 3. Ciclo de vida

- Emisión, renovación, expiración, revocación. ¿Quién renueva, cuándo y qué pasa durante la renovación (thundering herd)?

## 4. Errores del tercero

- **Catálogo**: ¿qué errores documenta (códigos, cuerpos)? Cada uno que la feature debe manejar es un escenario con un fake que lo devuelve.
- **Errores no documentados**: 5xx genéricos, HTML en vez de JSON, cuerpos vacíos.
- **Límites de tasa**: valores del sandbox y de producción (suelen diferir), cabeceras de `Retry-After`.

## 5. Efectos y entregas

- ¿La operación es **idempotente** del lado del tercero? ¿Acepta una clave de idempotencia?
- **Timeout tras ejecución**: ¿qué pasa si el tercero hizo el cargo y la respuesta se perdió?
- **Webhooks y callbacks**: ¿pueden llegar duplicados, desordenados, tarde o nunca? ¿Se verifica la firma? ¿Hay reconciliación?

## 6. Sandbox frente a producción

- ¿Qué se comporta distinto en el sandbox (datos de prueba, límites, errores que no se pueden provocar)?
- Todo lo que el sandbox no reproduce queda como **riesgo explícito** del informe de verificación, no como cubierto.

## 7. Versiones

- ¿Qué versión de API se usa? ¿Hay fecha de deprecación? ¿Hay versiones de SDK (v5 frente a v6) que cambian el tipo de token esperado?

## De la checklist a los escenarios

Cada respuesta produce escenarios en tres peldaños:

| Qué | Peldaño | Para qué |
|---|---|---|
| **Learning tests** contra el sandbox, uno por suposición | 2 | Confirmar que el tercero se comporta como creemos. Sus respuestas se graban con WireMock y alimentan los fakes |
| Escenarios con **fakes derivados de los learning tests** | 1 | Errores, timeouts, variantes, concurrencia: todo lo que el sandbox no deja provocar |
| **Walking skeleton** con el consumidor real | 3 | El recorrido más delgado de punta a punta: prueba que el camino entero funciona antes de construir lógica encima |

**Walking skeleton** (Alistair Cockburn; Freeman y Pryce en *Growing Object-Oriented Software, Guided by Tests*): una implementación mínima que atraviesa todas las capas y todas las integraciones reales, sin lógica de negocio. Su valor es que **falla el día 1** si la integración es imposible o está mal entendida. Debe ser el primer ticket (ver `to-tickets`) y el primer escenario.

**Learning tests** (Jim Newkirk; popularizados en *Clean Code*, capítulo 8): tests que escribes contra la API de un tercero para aprender cómo se comporta, antes de construir encima. Son baratos, documentan las suposiciones y avisan si el tercero cambia en una versión nueva.
