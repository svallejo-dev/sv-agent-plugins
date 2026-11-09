---
name: capacity-estimation
description: "Estimación de capacidad con números calculados en código, no en prosa. Parte de métricas medidas cuando el sistema existe, o de escenarios por orden de magnitud y umbrales de decisión cuando no hay métricas (diseño exploratorio, PoC), apoyándose en el arquetipo de negocio. Cubre QPS, almacenamiento, ancho de banda, ley de Little, utilización y colas, fan-out y latencia de cola, disponibilidad compuesta, shards, backlog y burn rate. Úsala cuando una decisión dependa de la escala (\"¿aguanta?\", \"¿cuántas instancias?\", \"¿hace falta shardear?\", \"capacity planning\", \"back-of-the-envelope\")."
license: MIT
---

# Estimación de capacidad

Responde en español y conserva en inglés los términos técnicos habituales.

Convierte "mucho tráfico" en números que **deciden** el diseño. Los números se calculan con `scripts/capacidad.py`, nunca de cabeza: el modelo es bueno razonando y malo multiplicando, y una cifra inventada con seguridad es el fallo más caro de este dominio.

**Analogía:** es la calculadora estructural del arquitecto. El dibujo del puente puede ser precioso, pero si nadie calculó la carga, es una ilustración, no un diseño.

## 1. Elige el modo según el punto de partida

- **Medido** (sistema existente, el caso por defecto si hay métricas): parte del tráfico y los percentiles reales del APM. Pide o consulta: pico de throughput (no promedio), p50/p95/p99 por endpoint o dependencia, utilización de CPU, memoria y pools, tamaño de datos actual y su crecimiento. Las consultas de partida están en [references/medicion.md](references/medicion.md).
- **Exploratorio** (sin sistema ni métricas: diseño exploratorio, PoC, producto nuevo): **la falta de números no bloquea**. Toma la forma de la carga del arquetipo de negocio (`business-archetypes`) y:
  1. Define tres **escenarios por orden de magnitud** (por ejemplo 10k, 1M y 100M usuarios activos diarios, o 1k, 100k y 10M dispositivos) con `escenarios`.
  2. Para cada decisión que depende de la escala, calcula el **umbral** a partir del cual deja de servir con `umbral` ("un primario de ~5k escrituras/s aguanta hasta ~N usuarios activos diarios con este patrón").
  3. Pregunta al negocio en qué escenario espera estar a 12-18 meses; diseña para ese y verifica qué se rompe en el siguiente.
  4. Marca cada factor (acciones por usuario, tamaños, picos) como supuesto de arquetipo y di cómo se medirá en el PoC o en producción.
- **Proyectado** (feature nueva sobre un sistema con datos de negocio, o calibrado con un sistema parecido publicado): parte de supuestos de demanda (usuarios activos, acciones por usuario, ratio lectura/escritura, tamaños, retención) y cita la fuente de la calibración.
- **Mixto** (lo más común): una parte medida (el tráfico actual) y otra proyectada (la feature nueva o el crecimiento).

Escribe cada supuesto con su fuente: "medido en NR, pico de los últimos 30 días", "supuesto de arquetipo (ticketing: ×100 en la apertura)", "tomado del caso X", "supuesto, sin dato". Un supuesto sin fuente se marca como tal.

## 2. Calcula solo lo que puede cambiar una decisión

Antes de cada cálculo, nombra la decisión que depende de él ("si la escritura pico pasa de ~5k/s, un solo primario no basta"). Si ningún resultado posible cambia la decisión, no lo calcules.

| Pregunta | Subcomando |
|---|---|
| ¿Cuánta demanda habrá? | `demanda` (proyectado), `medido` (crecimiento sobre lo real) o `escenarios` (varios órdenes de magnitud) |
| ¿Hasta qué escala sirve esta opción? | `umbral` |
| ¿Cuántas conexiones, goroutines o workers necesito? | `little` |
| ¿A qué utilización empieza a explotar la latencia? ¿Cuántos servidores para mantener la cola baja? | `utilizacion` |
| ¿Qué pasa con la latencia si un request toca N backends? | `fanout` |
| ¿Qué disponibilidad da esta cadena de dependencias? | `disponibilidad` |
| ¿Hace falta shardear? ¿Cuántos nodos? | `shards` |
| ¿Cuánto tarda en drenar una cola atrasada? | `backlog` |
| ¿Qué tan rápido se agota el presupuesto de error? | `burn` |

```bash
python3 <directorio de esta skill>/scripts/capacidad.py <subcomando> --help
python3 <directorio de esta skill>/scripts/capacidad.py little --rps 1200 --latencia-ms 180 --utilizacion 0.7
```

La salida es JSON con entradas, resultado y fórmula. Muestra al usuario la invocación y el resultado; no reescribas los números a mano.

## 3. Interpreta con los conceptos correctos

- **Pico, no promedio.** Dimensiona sobre el pico medido (o promedio × factor declarado). En sistemas con eventos (estrenos, partidos, campañas), el factor puede ser 10× o más; pregúntalo.
- **Ley de Little** (`L = λ · W`): la concurrencia es throughput × latencia. Usa la latencia del percentil que no quieres que encole (p99 para pools hacia dependencias). Si la dependencia se pone lenta, la concurrencia sube en proporción: así se agotan los pools.
- **Utilización y colas**: el tiempo de respuesta crece como `1/(1−ρ)`. A 50 % la respuesta es 2× el servicio; a 90 %, 10×. Por encima de ~70-80 % pequeños picos producen colas largas. El margen no es desperdicio: es lo que absorbe la varianza. (La fórmula es M/M/1, orientativa.)
- **Fan-out y cola de latencia** ("The Tail at Scale", Dean y Barroso): con 100 backends, si cada uno responde por encima de su p99 el 1 % de las veces, el 63 % de los requests ven al menos una respuesta lenta. El p99 de los backends se vuelve el p50 del agregado.
- **Disponibilidad compuesta**: en serie se multiplica (cada dependencia síncrona resta). El paralelo suma nueves **solo si los fallos son independientes**; misma zona, mismo deploy o misma configuración los correlacionan.
- **Shards sobre la key más caliente**: si la distribución está sesgada, el cálculo con el promedio miente.
- **Burn rate**: un burn de 14.4× agota el presupuesto mensual en ~2 días; es el umbral típico de página urgente.

Los órdenes de magnitud de referencia (latencias, throughput por nodo, nueves) están en [references/numeros.md](references/numeros.md). Son puntos de partida: si hay medición, manda la medición.

## 4. Entrega

Una tabla con: supuesto o medición (con fuente), cálculo (subcomando), resultado y **decisión que habilita o descarta**. En modo exploratorio, la tabla de escenarios y los umbrales de cada decisión, más la lista de mediciones que reemplazarán a los supuestos. Cierra con el número que más incertidumbre tiene y cómo reducirla (un load test, una consulta concreta al APM, un benchmark).

Si la estimación se hace dentro de un diseño (`system-design`), la tabla va a la sección de números del design doc.
