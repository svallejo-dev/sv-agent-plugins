# Plataforma de eventos interna (bus, integración)

**Analogía:** el servicio postal interno de una empresa grande. No produce las cartas, las entrega: su valor está en que lleguen, en orden cuando importa, que se puedan reenviar y que todos entiendan el formato del sobre.

## Fuerzas dominantes

- **Contratos entre equipos**: los eventos son una API pública interna; cambiar su formato rompe a otros.
- **Garantías de entrega y orden**: al menos una vez, orden por clave, replay.
- **Muchos productores y consumidores** con ritmos distintos; el consumidor lento no puede frenar a todos.
- **Operación como producto**: los equipos necesitan autoservicio (crear topics, suscribirse, ver su lag).

## Forma de la carga (sin métricas)

- Fórmula clave: **almacenamiento ≈ eventos/s × tamaño medio × retención × réplicas**.
- La carga sigue a la de los sistemas que la alimentan (picos de negocio), más replays y backfills.
- Escenarios para explorar: 100, 10 000 y 1M eventos por segundo, con retenciones de 1, 7 y 30 días.

## Invariantes y consistencia

- Ningún evento aceptado se pierde (durabilidad antes de confirmar al productor).
- Orden garantizado solo dentro de una clave de partición; nunca global.
- Los consumidores son idempotentes: los duplicados son parte del contrato.
- Compatibilidad de esquemas hacia atrás (y hacia adelante cuando haga falta).

## Subdominios típicos

- **Core** (para la plataforma): entrega confiable, gestión de suscripciones y contratos, autoservicio.
- **Supporting**: registro de esquemas, observabilidad de flujo (lag por consumidor), DLQs y replay.
- **Generic**: el broker en sí (Kafka, un servicio gestionado), autenticación.

## Camino recorrido (verifica antes de citar)

- Kafka, nacido en LinkedIn, como log distribuido particionado.
- Registro de esquemas con reglas de compatibilidad.
- Transactional outbox o CDC para publicar desde los servicios sin dual-write.
- CloudEvents (CNCF) como formato común de sobre de evento.
- Published Language: eventos de negocio, no volcados de tablas.

## Modos de fallo típicos (semilla para el red team)

- Poison message que bloquea una partición (head-of-line).
- Consumidor lento cuyo lag crece hasta superar la retención: pierde eventos.
- Cambio de esquema incompatible que rompe consumidores en producción.
- Hot partition por una clave de partición mal elegida.
- Rebalanceos continuos del grupo de consumidores que detienen el consumo.
- Replay masivo que satura a los consumidores o a sus bases.

## Preguntas que cambian el diseño

- ¿Qué garantías necesita cada flujo (orden, entrega, latencia)? ¿Son iguales para todos?
- ¿Quién es dueño de cada evento y de su esquema?
- ¿Qué retención y qué capacidad de replay se necesita?
- ¿Cuánto autoservicio se da a los equipos y con qué gobierno?

## Hipótesis para un PoC

- Validar la entrega con fallos provocados: consumidor caído, mensaje envenenado, rebalanceo, broker reiniciado.
- Validar la evolución de un esquema con productores y consumidores en versiones distintas.
- Instrumentar: lag por consumidor y partición, eventos en DLQ, tiempo de punta a punta, tasa de reintentos.
