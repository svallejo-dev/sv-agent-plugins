# Ticketing, reservas y ventas flash

**Analogía:** la apertura de puertas de un concierto. Durante meses nadie llega; en un minuto llega todo el mundo a la vez y solo hay sitio para una fracción.

## Fuerzas dominantes

- **Demanda muy superior a la oferta** en ventanas cortas: el problema no es el promedio, es el minuto de apertura.
- **Contención sobre inventario escaso**: muchos usuarios disputan las mismas filas (asientos, cupos, habitaciones).
- **Justicia percibida y bots**: quién llega primero y quién se queda fuera es un problema de negocio y de reputación.
- La mayor parte del tiempo el sistema está casi ocioso.

## Forma de la carga (sin métricas)

- Pico extremo y predecible (se conoce la hora de apertura), con picos de ×100 o más respecto al día normal.
- Lecturas masivas de disponibilidad y escrituras concentradas en pocas filas calientes.
- Escenarios para explorar: 1k, 100k y 1M usuarios intentando comprar en el mismo minuto, contra un inventario de miles.

## Invariantes y consistencia

- **No sobrevender**: el inventario vendido nunca supera el disponible. Consistencia fuerte en la asignación.
- **Reservas temporales** (holds) con expiración: el asiento se bloquea mientras el usuario paga y se libera si no paga.
- Pago y emisión del ticket atados: no hay ticket sin pago confirmado ni pago sin ticket.

## Subdominios típicos

- **Core**: asignación de inventario y reservas, gestión de la cola de compra, prevención de bots.
- **Supporting**: catálogo de eventos y recintos, mapas de asientos, emisión y validación de tickets.
- **Generic**: pagos, notificaciones, autenticación.

## Camino recorrido (verifica antes de citar)

- Salas de espera virtuales (virtual waiting room) que admiten usuarios a la tienda a un ritmo que el backend soporta.
- Reservas con TTL y liberación automática.
- Fallos públicos de grandes preventas (por ejemplo, la preventa de 2022 de Ticketmaster) como estudio de caso de demanda y bots.

## Modos de fallo típicos (semilla para el red team)

- Todo el tráfico de apertura golpea directamente la base de inventario.
- Hot rows: miles de transacciones bloqueando las mismas filas.
- Holds que no expiran (proceso de limpieza caído): inventario fantasma agotado.
- Bots que acaparan el inventario o saturan la cola.
- La pasarela de pagos se convierte en el cuello de botella en el pico.

## Preguntas que cambian el diseño

- ¿Asientos numerados o cupos generales? (cambia la granularidad de la contención)
- ¿Cuánto dura un hold y qué pasa si el pago llega tarde?
- ¿Es aceptable una cola de espera explícita para el usuario?
- ¿Qué política antibots y de límite por usuario exige el negocio?

## Hipótesis para un PoC

- Validar el invariante de no sobreventa bajo concurrencia real (prueba de carga dirigida a las mismas filas) antes que cualquier otra cosa.
- Validar que la sala de espera protege al backend: admisión controlada y medible.
- Instrumentar: usuarios en cola, tasa de admisión, holds activos y expirados, conflictos de asignación, conversión de hold a pago.
