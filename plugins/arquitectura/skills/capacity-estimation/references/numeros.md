# Números de referencia

Órdenes de magnitud para estimar sin buscar. Recuerda la magnitud, no los decimales: lo que cambia una arquitectura es la razón entre componentes. En un sistema existente, estos números solo sirven para detectar que una medición es sospechosa; manda la medición.

Base: el cheat sheet de [proyecto26/system-design-skills](https://github.com/proyecto26/system-design-skills) (MIT), con las cifras de throughput corregidas.

## Tiempo y volumen

- Un día ≈ 86 400 s ≈ 10⁵ s. Un mes ≈ 2.6 × 10⁶ s.
- 1 req/s sostenido ≈ 86 000 al día ≈ 2.6 M al mes.
- 2¹⁰ ≈ mil (KB), 2²⁰ ≈ millón (MB), 2³⁰ ≈ mil millones (GB), 2⁴⁰ (TB), 2⁵⁰ (PB). La memoria es base 2; el almacenamiento y la red se venden en base 10.

## Latencias (orden de magnitud)

| Operación | ≈ Tiempo |
|---|---:|
| Referencia a caché L1 | ~1 ns |
| Referencia a memoria principal | ~100 ns |
| Comprimir 1 KB | ~1-3 µs |
| Leer 1 MB secuencial de memoria | ~3-10 µs |
| Lectura aleatoria en SSD | ~16-100 µs |
| Leer 1 MB secuencial de SSD | ~50-200 µs |
| Ida y vuelta dentro del mismo datacenter | ~0.5 ms |
| Ida y vuelta entre zonas de una región | ~1-2 ms |
| Seek de disco giratorio | ~2-10 ms |
| Ida y vuelta entre continentes | ~70-150 ms |

Consecuencias: la memoria es ~100× más rápida que la red interna; las llamadas entre regiones cuestan del orden de 100 ms, así que el tráfico conversacional va dentro de una región.

## Throughput por nodo (puntos de partida, no promesas)

| Componente | ≈ Operaciones/s por nodo | Notas |
|---|---:|---|
| RDBMS (Postgres/MySQL) en lecturas puntuales indexadas | ~10k (hardware moderno, datos en memoria) | ~1k es un suelo conservador; scans, joins y escrituras con muchos índices pueden quedar 10× por debajo. Valida con benchmark o medición. |
| RDBMS en escrituras transaccionales | ~1k-10k | Depende de fsync, índices, contención en filas calientes. |
| Key-value distribuido por partición | ~1k-10k | Los servicios gestionados publican límites por partición: verifícalos con `research`. |
| Cache en memoria (Redis/Memcached) | ~100k-1M | Ejecución de comandos por shard en un solo hilo en Redis. |
| Broker de streaming por partición | ~1-10 MB/s | Mide en bytes, no en mensajes. |
| Servicio HTTP con lógica simple, por núcleo | ~1k-10k | Muy dependiente del lenguaje y de la serialización. |

## Disponibilidad

| Disponibilidad | Caída por año | Caída por mes (30 días) |
|---:|---|---|
| 99 % | ~3.65 días | ~7.2 h |
| 99.9 % | ~8.76 h | ~43 min |
| 99.95 % | ~4.4 h | ~22 min |
| 99.99 % | ~53 min | ~4.3 min |
| 99.999 % | ~5.3 min | ~26 s |

Cada nueve adicional cuesta de forma no lineal (redundancia, failover automático, multi-región). Ata el objetivo al requisito, no a la ambición.

## Factores de pico

- Tráfico de consumo diario: pico ≈ 2-3× el promedio.
- Eventos (lanzamientos, partidos en vivo, campañas, quincenas en pagos): 10× o más, a veces en minutos. Pregunta por el calendario de eventos.
- Reintentos durante un incidente: pueden multiplicar la carga por (1 + reintentos) en cada capa que reintenta.
