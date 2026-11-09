# Rúbrica de calidad

Puntúa el diseño de 0 a 5 en cada dimensión antes de cerrarlo. Informa el total, la dimensión más débil y qué le falta exactamente a cada dimensión que no llega a 5. Ningún diseño se da por terminado sin nombrar su dimensión más débil.

Basada en la rúbrica de [proyecto26/system-design-skills](https://github.com/proyecto26/system-design-skills) (MIT), adaptada a sistemas existentes.

| Dimensión | 5 significa | Si es baja, invoca |
|---|---|---|
| **Punto de partida** | El AS-IS (o la referencia similar, o el arquetipo de negocio) está descrito: diagrama y números medidos si existe sistema; fuerzas, invariantes y supuestos explícitos si no; los huecos están nombrados | `references/punto-de-partida.md` |
| **Requisitos** | Funcionales, no funcionales y fuera de alcance, como delta, con restricciones de negocio y compliance | `building-blocks` → `requirements-scoping` |
| **Números** | Con sistema: pico, percentiles, crecimiento y capacidad medidos y calculados con fuente. Sin métricas: escenarios por orden de magnitud y umbrales de decisión calculados, con plan para medirlos. Cada número habilita una decisión | `capacity-estimation` |
| **Interfaces y datos** | Request, response, key primaria, paginación, idempotencia y dueño de cada dato son concretos | `building-blocks` → `api-design`, `data-storage` |
| **Trade-offs** | Cada decisión importante tiene resuelve / empeora / cámbiala cuando con disparador medible; hubo alternativas reales | Contrato de respuesta de `system-design` |
| **Fronteras** | Los contextos y sus relaciones tienen patrón y dueño | `strategic-design` |
| **Fallos** | Red team hecho; riesgos con detección, mitigación y estado | `design-stress-test` |
| **Operación** | SLOs, alertas sobre síntomas, runbooks y capacidad de detectar cada fallo relevante | `building-blocks` → `observability` |
| **Migración / experimento** | Con sistema: camino paso a paso, desplegable, verificable, con puertas marcadas y vuelta atrás. En un PoC: hipótesis por riesgo, alcance mínimo, instrumentación, criterios de éxito y abandono, deuda deliberada | `references/migracion.md` |
| **Evolución** | Se sabe qué se rompe a ×10 y qué se haría entonces | `building-blocks` → `scaling-evolution` |

## Diagnóstico rápido

Cuando un diseño "no termina de convencer", recorre estas preguntas en orden; la primera con respuesta "no" dice qué hacer a continuación.

1. ¿Sé de dónde parto (sistema, referencia o arquetipo) y qué duele o qué manda?
2. ¿Sé qué cambia y qué no (requisitos como delta)?
3. ¿Tengo números con fuente (medidos, o escenarios y umbrales) para las decisiones que dependen de la escala?
4. ¿Hubo al menos una alternativa real, incluida la de cambio mínimo?
5. ¿Cada componente tiene sus tres respuestas?
6. ¿Ataqué el diseño y sé cómo me enteraría de cada fallo?
7. ¿Puedo llegar desde el sistema actual sin pararlo? (En un PoC: ¿sé qué hipótesis valido primero y cómo la mido?)
8. ¿Barrí los bloques de construcción y abrí o descarté cada uno con una razón?
