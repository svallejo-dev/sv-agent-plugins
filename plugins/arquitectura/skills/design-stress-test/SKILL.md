---
name: design-stress-test
description: "Red team de un diseño o de un sistema existente. Lanza sub-agentes en paralelo, cada uno con una familia de ataques (carga, dependencias, datos, cambios, infraestructura, operación, abuso), sembrados con los incidentes reales del sistema y verificados contra su código y configuración; devuelve una matriz de riesgos con modo de fallo, detección y mitigación. Úsala cuando el usuario pida \"stress-test\", \"red team\", \"¿qué puede fallar?\", \"pre-mortem\", \"¿esto aguanta?\" o una revisión de resiliencia."
license: MIT
---

# Design stress test

Responde en español y conserva en inglés los términos técnicos habituales.

Ataca un diseño (o un sistema que ya corre) para encontrar cómo falla **antes** de que falle en producción. Cada familia de ataques la trabaja un sub-agente distinto, en paralelo y con contexto limpio, para que ninguno se ancle en la narrativa optimista del diseño.

**Analogía:** es el túnel de viento. El ala se ve bien en el plano; el túnel dice a qué velocidad vibra, dónde se rompe y si el piloto se entera antes de que pase.

## 1. Reúne el objetivo y su historia

- **El diseño**: design doc, RFC, diagrama o la conversación actual. Si el objetivo es un sistema existente, su arquitectura actual.
- **El sistema real**, si existe: el código y la configuración (timeouts, reintentos, tamaños de pool, límites de colas, health checks, réplicas), los dashboards y las alertas.
- **La historia**: postmortems, incidentes, runbooks, resultados de load tests. **Un ataque que ya ocurrió vale más que uno imaginado**: cada incidente pasado se convierte en un escenario a re-ejecutar contra el diseño nuevo ("¿esto habría evitado el incidente de X?").
- **Los objetivos**: SLOs, RPO/RTO, presupuesto de latencia, qué degradación es aceptable para el negocio.

Si falta la historia o los objetivos, pregúntalos una vez; si no existen, sigue y márcalo en el informe. **Sin historia propia** (diseño exploratorio, PoC, producto nuevo), siembra los ataques con los modos de fallo típicos del arquetipo de negocio (`business-archetypes`): son los incidentes que otros ya sufrieron en ese dominio. Sin objetivos formales, usa los invariantes del arquetipo como criterio de impacto (un cobro duplicado o una sobreventa son críticos aunque no haya SLO escrito).

## 2. Elige las familias de ataque

Las familias y sus ataques están en [references/catalogo-ataques.md](references/catalogo-ataques.md). Selecciona las que aplican al objetivo; por defecto, todas las de carga, dependencias, datos y cambios, más las de infraestructura si hay requisitos de disponibilidad, más abuso si hay superficie pública.

Para el detalle mecánico de un componente concreto (cómo se comporta una cache, una cola o un balanceador bajo estrés), invoca `building-blocks` y extrae la sección "Behavior under stress" del bloque correspondiente para pasarla al sub-agente.

## 3. Lanza un sub-agente por familia, en paralelo

Lanza todas las llamadas juntas, cada una con contexto limpio. Cada sub-agente recibe:

- El diseño (o la arquitectura actual) y los objetivos.
- Su familia de ataques del catálogo, pegada completa.
- Las secciones "Behavior under stress" relevantes de `building-blocks`.
- Los incidentes pasados que caen en su familia.
- Acceso de lectura al repositorio, si existe, con el encargo de **verificar en el código y la configuración** cada suposición ("el diseño dice timeout de 2 s; ¿lo dice la config?").

> **Portabilidad:** si tu herramienta no tiene sub-agentes, ejecuta cada encargo en una conversación nueva con solo su brief, o en secuencia en esta sesión, y declara en el resultado que no hubo aislamiento de contexto.

Encargo para cada sub-agente:

"Eres un ingeniero de confiabilidad buscando cómo falla este sistema en la familia <familia>. Para cada ataque aplicable, escribe un escenario concreto y responde: (1) **disparador**; (2) **propagación**: la cadena de efectos, capa por capa, incluido si el sistema puede quedar atrapado en un estado degradado aunque el disparador desaparezca; (3) **detección**: qué métrica o alerta se dispara y cuánto tarda, o 'nadie se entera'; (4) **impacto**: usuarios afectados, datos en riesgo, SLO consumido; (5) **estado actual**: mitigado / parcial / sin mitigar, con la evidencia (archivo:línea de config o código, o sección del diseño); (6) **mitigación** propuesta, distinguiendo prevención, contención y recuperación, con su coste. Descarta los ataques que no aplican en una línea. No inventes valores de configuración: si no puedes verificarlos, dilo. Responde en español, menos de 700 palabras."

## 4. Agrega en una matriz de riesgos

Ordena los hallazgos por **severidad** (impacto × probabilidad, con probabilidad alta si ya ocurrió antes) y deduplica los que comparten causa raíz: varios ataques que terminan en "el pool de conexiones a la base se agota" son un solo riesgo con varios disparadores.

```markdown
## Stress test: <sistema>

**Objetivo:** <diseño o sistema> · **SLOs:** <…> · **Historia usada:** <incidentes>

| # | Riesgo (causa raíz) | Disparadores | Detección | Impacto | Estado | Mitigación | Coste |
|---|---|---|---|---|---|---|---|
| 1 | … | … | alerta X en ~N min / nadie | … | sin mitigar | … | … |

### Riesgos sistémicos
<los que cruzan familias: fallos correlacionados, bucles de reintentos, estados metaestables>

### Puntos ciegos
<lo que no se pudo verificar: config sin acceso, métricas que no existen>

### Siguiente experimento
<el load test, game day o chaos experiment que más incertidumbre quitaría>
```

## 5. Cierra el ciclo

- Los riesgos que cambian el diseño vuelven a `system-design` como restricciones nuevas.
- Las mitigaciones difíciles de revertir con un trade-off real se registran como ADR con `domain-modeling`.
- Los riesgos de detección ("nadie se entera") se traducen en SLIs y alertas concretas.
- Si una mitigación depende de números (pool, timeouts, réplicas, margen), calcúlalos con `capacity-estimation`.
