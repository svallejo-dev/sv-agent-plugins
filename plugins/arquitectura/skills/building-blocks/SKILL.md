---
name: building-blocks
description: "Catálogo de referencia de bloques de construcción de sistemas distribuidos (API, almacenamiento, caching, consistencia, mensajería, scheduling, resiliencia, escalado, observabilidad, logging, balanceo, DNS, CDN, IDs, contadores, blobs, búsqueda, descomposición de servicios, requisitos) con opciones, trade-offs y comportamiento bajo estrés. Lo cargan system-design y design-stress-test; úsalo también para una pregunta puntual sobre uno de esos componentes."
license: MIT
---

# Bloques de construcción

Responde en español y conserva en inglés los términos técnicos habituales.

Catálogo de componentes de sistemas distribuidos. Cada bloque es un archivo en `references/` con la misma estructura: cuándo usarlo y cuándo no, qué aclarar antes, opciones, tabla de trade-offs, **comportamiento bajo estrés**, pasos de aplicación, dos y don'ts, números, boceto de interfaz, bloques relacionados y una sección de profundidad.

**Analogía:** es el almacén de piezas de un taller. El diseñador (`system-design`) decide qué construir; aquí está cómo se comporta cada pieza, incluido cómo se rompe.

## Cómo usarlo

Lee **solo** el archivo del bloque cuyo tema está activo; no cargues el catálogo entero. Para una pregunta puntual ("¿qué política de eviction para sesiones?"), lee el bloque y responde con su receta y su tabla de trade-offs. Dentro de un diseño, aplica su paso de trade-offs con el contrato `Decisión | Resuelve | Empeora | Cámbiala cuando…`.

| Cuando la conversación llega a… | Archivo |
|---|---|
| Requisitos funcionales, no funcionales, alcance, preguntas que hacer | [requirements-scoping.md](references/requirements-scoping.md) |
| Endpoints, request/response, paginación, idempotencia, versionado | [api-design.md](references/api-design.md) |
| Monolito vs servicios, fronteras, gateway/BFF, discovery, mesh, sync vs async | [service-decomposition.md](references/service-decomposition.md) |
| SQL vs NoSQL, modelo de datos, índices, sharding, replicación | [data-storage.md](references/data-storage.md) |
| Qué cachear, eviction, invalidación, stampede, hot keys | [caching.md](references/caching.md) |
| CAP/PACELC, modelos de consistencia, quorum, consenso, consistent hashing, sagas | [consistency-coordination.md](references/consistency-coordination.md) |
| Colas vs streams, garantías de entrega, orden, DLQ, outbox, backpressure | [messaging-streaming.md](references/messaging-streaming.md) |
| Jobs diferidos, cron distribuido, leasing, prioridades, fairness | [task-scheduling.md](references/task-scheduling.md) |
| Timeouts, reintentos, circuit breakers, bulkheads, degradación, rate limiting | [resilience-failure.md](references/resilience-failure.md) |
| Cómo crece el sistema ×10/×100, diagnóstico del cuello de botella | [scaling-evolution.md](references/scaling-evolution.md) |
| Métricas, trazas, SLOs, burn rate, alertas, health checks | [observability.md](references/observability.md) |
| Pipeline de logs a gran volumen, sampling, retención | [distributed-logging.md](references/distributed-logging.md) |
| L4/L7, algoritmos de balanceo, health checks, slow start, draining | [load-balancing.md](references/load-balancing.md) |
| Resolución DNS, routing geo/latencia/failover, TTL, anycast | [dns.md](references/dns.md) |
| CDN, cache en el edge, cache key, purga, origin shield | [content-delivery.md](references/content-delivery.md) |
| IDs únicos (UUID/ULID/Snowflake/ticket), reloj, orden | [sequencer.md](references/sequencer.md) |
| Contadores con muchas escrituras, HyperLogLog | [sharded-counters.md](references/sharded-counters.md) |
| Objetos grandes, multipart, URLs firmadas, tiering, erasure coding | [blob-store.md](references/blob-store.md) |
| Búsqueda full-text, índice invertido, ranking, autocomplete | [distributed-search.md](references/distributed-search.md) |

## Notas de esta versión

- **Origen**: curado de [proyecto26/system-design-skills](https://github.com/proyecto26/system-design-skills) (MIT, commit `228d57d`). El texto está en inglés, como el original.
- **Correcciones**: los errores factuales detectados están corregidos y marcados con `[sv-skills]` (DynamoDB no es leaderless, error de HyperLogLog, UUIDv7 en stores por rango, virtual nodes y hot keys, quorum y linealizabilidad, carrera de invalidación en cache, burn rate, entre otros).
- **Sin archivos de proveedor**: se quitaron porque envejecen rápido y varios ya estaban mal. Cuando un paso diga "read the provider file" o "see *Choosing a provider*", verifica el servicio gestionado concreto (límites, cuotas, nombres, precios) con `research` contra la documentación oficial actual.
- **Referencias cruzadas**: un bloque entre backticks (`caching`) es el archivo `references/caching.md`. Las menciones a `back-of-the-envelope` se resuelven con `capacity-estimation`, a `system-design` con `system-design` y a `architecture-diagram` con un diagrama Mermaid en el design doc.
- **Números**: los "Numbers that matter" son órdenes de magnitud de partida. En un sistema existente mandan las métricas medidas.
- **Anycast y geo-routing**: `load-balancing` y `content-delivery` se remiten mutuamente; el detalle útil está en `dns.md`.
- **Lo que este catálogo no cubre a fondo** (lo aportan `design-stress-test` y `system-design`): fallos metaestables, estabilidad estática, arquitectura por celdas y shuffle sharding, hedged requests, propagación de deadlines, migraciones de sistemas existentes.
