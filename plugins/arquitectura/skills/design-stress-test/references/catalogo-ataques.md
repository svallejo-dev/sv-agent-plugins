# Catálogo de ataques

Familias de ataques para el red team. Cada ataque es una pregunta concreta que el diseño debe poder responder. Al final, el catálogo de mitigaciones de nivel hiperescala.

Fuentes de las ideas: la sección "Behavior under stress" de cada bloque en `building-blocks`; el Amazon Builders' Library (estabilidad estática, shuffle sharding, trabajo constante, timeouts y reintentos con jitter); el libro y el workbook de SRE de Google (SLOs, sobrecarga, fallos en cascada); "Metastable Failures in Distributed Systems" (Bronson et al., HotOS 2021); "The Tail at Scale" (Dean y Barroso, 2013).

## 1. Carga

- **×10 sostenido y ×100 en pico**: ¿qué recurso se satura primero (CPU, pool de conexiones, IOPS, ancho de banda, particiones)? ¿El sistema rechaza el exceso o lo encola hasta morir?
- **Pico súbito** (evento, campaña, push masivo): ¿el autoscaling llega a tiempo? ¿Cuánto tarda una instancia nueva en estar lista y caliente?
- **Hot key / hot partition / celebrity**: una sola key, tenant o partición recibe una fracción desproporcionada. ¿El diseño lo reparte o lo concentra?
- **Retry storm**: una dependencia se pone lenta y cada capa reintenta. ¿Por cuánto se multiplica la carga si cada una de las N capas reintenta R veces? ¿Hay retry budget?
- **Amplificación por fan-out**: un request de entrada genera N llamadas internas. ¿Qué pasa con el p99 y con la carga en los backends?
- **Arranque en frío**: cache vacía tras un deploy, un failover o un flush. ¿El origen aguanta el 100 % del tráfico que normalmente absorbe la cache?
- **Fallo metaestable**: un disparador breve (pico, failover, cache fría) empuja al sistema a un estado degradado que **se sostiene solo** aunque el disparador desaparezca (reintentos que mantienen la sobrecarga, colas que nunca drenan, timeouts que generan más trabajo). ¿Qué rompe el bucle?
- **Cola que no drena**: el consumo es menor que la producción durante el pico. ¿Cuánto tarda en drenar? ¿Los mensajes caducan antes?

## 2. Dependencias

- **Caída total** de cada dependencia síncrona: ¿qué devuelve el sistema? ¿Hay degradación explícita (datos viejos, funcionalidad reducida) o error?
- **Brownout**: la dependencia no cae, se pone 10× más lenta. Es peor que la caída: los health checks pasan y los pools se agotan. ¿Los timeouts están por debajo del presupuesto de latencia del caller?
- **Errores parciales**: 5 % de errores o respuestas malformadas. ¿Se detecta? ¿Se reintenta lo que no es idempotente?
- **Cuota o rate limit agotado** en un tercero (pasarela de pagos, partner, API de nube). ¿Qué pasa con los requests en vuelo?
- **Dependencia compartida** (una base, un cluster de cache, un broker, un servicio de auth): ¿cuántos servicios caen si cae ella? ¿Es un SPOF disfrazado?
- **Expiración**: certificados, credenciales, tokens de servicio, dominios. ¿Hay alerta antes?

## 3. Datos

- **Poison message**: un mensaje que siempre falla. ¿Bloquea la partición (head-of-line)? ¿Va a una DLQ? ¿Alguien la mira?
- **Duplicados**: la entrega es at-least-once. ¿Cada consumidor es idempotente? ¿Con qué key?
- **Desorden**: los eventos llegan fuera de orden o tras un rebalanceo. ¿El estado final es correcto?
- **Corrupción silenciosa**: un bug escribe datos mal durante horas. ¿Cómo se detecta? ¿Se puede reconstruir (event log, backups con punto en el tiempo)?
- **Migración a medias**: un cambio de esquema o un backfill queda interrumpido. ¿Conviven versiones viejas y nuevas del código con ambos esquemas?
- **Replica lag**: la réplica va minutos atrás. ¿Qué lectura se rompe (read-your-writes)?
- **Split brain**: dos nodos creen ser líder. ¿Hay fencing token en el punto donde se produce el efecto?
- **Crecimiento**: el dataset crece 10×. ¿Qué consulta deja de caber en memoria? ¿Qué índice se vuelve inmanejable?

## 4. Cambios (deploys y configuración)

- **Deploy malo**: una versión con bug llega a producción. ¿Canary? ¿Rollback automático por SLO? ¿Cuánto tarda en revertir?
- **Configuración global errónea**: un cambio de config o feature flag llega a todas las instancias a la vez. Es la fuente clásica de fallos correlacionados. ¿Se despliega la config de forma progresiva, como el código?
- **Rollback imposible**: el deploy incluye una migración destructiva o publica eventos en un formato nuevo. ¿Es una puerta de un solo sentido?
- **Incompatibilidad entre versiones**: durante el rollout conviven la versión N y la N+1. ¿Se entienden en ambos sentidos (contratos, esquemas de eventos, caches)?
- **Debug flood**: un deploy sube el nivel de log o la cardinalidad de métricas. ¿El pipeline de observabilidad se cae o encarece?

## 5. Infraestructura

- **Pérdida de un nodo, de una zona, de una región**: ¿qué se pierde (datos no replicados, sesiones, requests en vuelo)? ¿El resto de zonas tiene capacidad para absorber el tráfico sin escalar en ese momento (estabilidad estática)?
- **Partición de red**: dos partes del sistema no se ven. ¿Qué invariante prefiere el diseño: consistencia o disponibilidad (PACELC)?
- **Desfase de reloj**: un nodo con el reloj adelantado o atrasado. ¿Qué depende del tiempo (leases, TTL, ordenamiento, IDs)?
- **Recursos agotados**: disco lleno, file descriptors, conexiones máximas de la base, puertos efímeros.
- **Vecino ruidoso**: otro tenant o workload en la misma máquina, cluster o base consume los recursos.
- **El plano de control cae**: el orquestador, el service discovery o el DNS no responden. ¿El plano de datos sigue funcionando con lo último que sabía?

## 6. Operación

- **Ceguera**: el sistema falla y ninguna alerta salta, o salta la de un síntoma lejano. ¿Las alertas están sobre síntomas del usuario (SLOs) o sobre causas?
- **Alerta sin acción**: la alerta salta pero no hay runbook, o el runbook asume a una persona que no está.
- **Recuperación manual lenta**: el failover o el restore requiere pasos humanos. ¿Cuánto tarda de verdad? ¿Se ha ensayado?
- **Dependencia de una persona**: solo una persona sabe operar el componente.

## 7. Abuso y seguridad operativa

- **Tráfico malicioso o bots**: ¿hay rate limiting por cliente, por IP, por tenant? ¿Falla abierto o cerrado si el limitador cae?
- **Enumeración y scraping** de recursos por ID predecible.
- **Requests caros a propósito**: paginación profunda, búsquedas sin límite, payloads enormes.
- **Tenant ruidoso**: un cliente legítimo pero enorme degrada a los demás.

## Catálogo de mitigaciones (más allá de lo básico)

| Mitigación | Qué ataca | Idea |
|---|---|---|
| Timeouts por debajo del presupuesto del caller, con propagación de deadline | Brownout, cascada | Cada llamada sabe cuánto tiempo le queda al request original y no trabaja en balde |
| Reintentos con backoff, jitter y **retry budget** | Retry storm | Los reintentos son un porcentaje acotado del tráfico, no un multiplicador |
| Circuit breaker y bulkheads | Dependencia lenta, dependencia compartida | Aislar pools por dependencia; dejar de llamar a lo que está roto |
| **Load shedding** y admission control | Sobrecarga, metaestable | Rechazar pronto y barato lo que no se puede servir, priorizando el tráfico crítico |
| Degradación explícita (brownout mode) | Caída de dependencias no críticas | Apagar features secundarias para salvar la principal |
| **Estabilidad estática** | Pérdida de zona, caída del plano de control | Sobreaprovisionar para que el fallo no requiera reaccionar (escalar, reconfigurar) en el peor momento |
| **Arquitectura por celdas** y **shuffle sharding** | Blast radius, tenant ruidoso, deploy malo | Copias independientes del sistema; cada cliente en una combinación distinta de celdas para que un fallo afecte a pocos |
| **Trabajo constante** | Picos de carga en el plano de control | Hacer siempre la misma cantidad de trabajo, haya cambios o no, para que el comportamiento bajo estrés sea el mismo que en calma |
| Hedged requests | Latencia de cola con fan-out | Enviar una segunda copia si la primera tarda más que el p95, cancelando la que pierda |
| Idempotency keys y fencing tokens | Duplicados, split brain | El efecto se aplica una vez aunque el mensaje llegue dos veces o haya dos líderes |
| Backpressure | Colas que crecen sin límite | El consumidor lento frena al productor en vez de acumular |
| Despliegue progresivo de código **y** configuración, con rollback automático por SLO | Deploy malo, config global | El fallo afecta a una fracción pequeña y se revierte solo |
| Game days y chaos experiments | Recuperación no ensayada, ceguera | Provocar el fallo en condiciones controladas para medir detección y recuperación |
