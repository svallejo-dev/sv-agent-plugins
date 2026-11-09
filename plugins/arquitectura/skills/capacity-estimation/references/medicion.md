# Medir antes de estimar (sistema existente)

En un sistema que ya corre, la mejor estimación es una medición. Esta guía dice **qué** medir; las consultas son plantillas que hay que adaptar a los nombres reales de apps, eventos y atributos.

## Qué pedir o consultar

| Dato | Por qué importa | Cuidado con |
|---|---|---|
| Throughput pico por endpoint u operación (últimos 30-90 días) | Base de toda proyección | El promedio esconde el pico; usa el máximo de una serie por minuto |
| p50 / p95 / p99 por endpoint y por dependencia | Little, fan-out, timeouts | El promedio miente con colas largas; nunca uses solo `average` |
| Tasa de errores por tipo (4xx, 5xx, timeouts) | Presupuesto de error, reintentos | Los timeouts suelen contarse aparte |
| Utilización: CPU, memoria, pools de conexiones, hilos/goroutines | Distancia al codo de la curva | Mide en el pico, no en el día medio |
| Tamaño de datos y crecimiento mensual | Almacenamiento, necesidad de sharding | Índices y réplicas multiplican el tamaño |
| Lag de colas/consumidores | Backlog, drenaje | Mide por partición: el lag agregado esconde la partición caliente |
| Calendario de eventos (estrenos, campañas) | Factor de pico real | Pregunta a negocio; no está en las métricas |

## Plantillas NRQL (New Relic)

Adapta `appName`, nombres de transacciones y atributos.

```sql
-- Throughput pico por minuto en los últimos 30 días
SELECT rate(count(*), 1 minute) FROM Transaction
WHERE appName = '<app>' SINCE 30 days ago TIMESERIES 1 hour

-- Percentiles por endpoint
SELECT percentile(duration, 50, 95, 99) FROM Transaction
WHERE appName = '<app>' FACET name SINCE 7 days ago

-- Latencia de una dependencia externa
SELECT percentile(duration, 50, 95, 99), count(*) FROM Span
WHERE appName = '<app>' AND span.kind = 'client' FACET peer.service SINCE 7 days ago

-- Tasa de errores
SELECT percentage(count(*), WHERE error IS true) FROM Transaction
WHERE appName = '<app>' SINCE 7 days ago TIMESERIES
```

Para logs (Sumo Logic u otro), el patrón es el mismo: contar por minuto, quedarse con el máximo, y separar por endpoint u operación.

## Si no hay métricas

1. Usa los logs de acceso o del gateway para reconstruir el throughput.
2. Si tampoco hay logs, un load test controlado en un entorno parecido a producción (con su runbook y criterios de parada).
3. Si nada de lo anterior es posible, proyecta (modo proyectado) y marca la estimación como **no validada**, con el plan para medirla.

## Errores típicos en sistemas existentes

- Proyectar con el promedio y descubrir el pico en producción.
- Medir el servicio y olvidar la dependencia: el cuello de botella suele estar en la base de datos o en un tercero.
- Medir en un entorno de pruebas con datos pequeños: las consultas que caben en memoria allí no caben en producción.
- Ignorar el tráfico de reintentos y de jobs en segundo plano, que compiten por los mismos recursos.
