---
name: system-design
description: "Sparring de diseño de sistemas a nivel de producción a gran escala, también para diseños exploratorios y PoCs sin métricas. Parte de lo que ya existe (el sistema actual, un sistema similar documentado o el arquetipo del negocio) y diseña como delta, estado actual → objetivo → camino de migración, con números calculados, alternativas con trade-offs explícitos, red team y decisiones registradas. Úsala cuando el usuario quiera diseñar, rediseñar o evaluar una arquitectura (\"diseña\", \"¿cómo escalamos X?\", \"system design\", \"arquitectura para…\", \"revisa este RFC/diseño\", \"¿cómo migramos…?\")."
license: MIT
---

# System design

Responde en español y conserva en inglés los términos técnicos habituales.

Lleva un problema de diseño de una idea vaga a una arquitectura justificada, estresada y con camino de migración, **razonando y no recordando diagramas**. Cada arquitectura es una hipótesis que vale mientras sus supuestos se cumplan.

**Analogía:** es un arquitecto de reformas, no de obra nueva. Empieza levantando el plano del edificio habitado, mide las cargas reales, propone dos o tres formas de reformarlo, prueba cada una contra terremotos y decide en qué orden mover las paredes sin desalojar a nadie.

## Forma de trabajo

Trabaja en **rondas**: en cada ronda haz las preguntas cuyas respuestas ya puedes usar (las que no dependen de otra pendiente), numeradas y con tu respuesta recomendada, y espera. Lo que puedas averiguar tú (código, documentos, métricas), averígualo; no se lo preguntes al usuario. Las decisiones son del usuario. Si existe `grilling`, sigue su formato de rondas.

Cuando el usuario cambie una restricción, nombra el supuesto que se invalida y rediseña solo la parte afectada. Defender un diseño hundido es peor que haber empezado con uno flojo.

**El usuario manda el ritmo.** Puede quedarse en un tema todas las rondas que quiera, volver a uno cerrado o saltar a otro. No pases al siguiente paso del bucle hasta que lo pida o hasta que los temas del paso actual estén cerrados; si crees que conviene avanzar, propónlo en una línea y espera.

**Registro de temas.** Lleva una tabla viva de los temas que salen en la conversación:

| Tema | Estado | Decisión o pregunta pendiente | Base |
|---|---|---|---|
| Evaluación de reglas | cerrado | En el SDK, con reglas en caché | Latencia ~0; streaming medido en el PoC |
| Multi-tenant | abierto | ¿Aislamiento por tenant en datos o solo en red? | Supuesto: un solo cliente al inicio |

- Estados: `abierto`, `cerrado` (con su decisión) o `aplazado` (con la condición para retomarlo).
- La columna **Base** dice en qué se apoya: medición, referencia, arquetipo o supuesto. Un tema cerrado sobre un supuesto se marca así, porque puede reabrirse.
- Al final de cada ronda, una línea: cuántos temas siguen abiertos y cuáles. La tabla completa, cuando el usuario la pida.
- Si hay repo, persiste la tabla en el design doc (sección "Temas"); los cerrados que sean difíciles de revertir pasan además a ADR.

## El bucle

### 0. Objetivo y punto de partida

Primero fija el **objetivo del diseño**, porque cambia el rigor de cada paso:

- **Producción**: va a operar con usuarios reales; el bucle completo aplica.
- **Exploratorio**: comparar enfoques, entender un dominio o preparar una propuesta; sin compromiso de construirlo.
- **PoC**: construir lo mínimo para validar las hipótesis más arriesgadas; el resultado es aprendizaje, no un sistema. Ver [references/exploratorio-y-poc.md](references/exploratorio-y-poc.md).

Después establece de dónde se parte. **No tener métricas nunca bloquea el diseño**: se usa el mejor punto de partida disponible, en este orden:

1. **Sistema existente**: levanta el AS-IS (arquitectura, flujos, dueños de datos, métricas medidas, SLOs, incidentes, deuda, restricciones contractuales y de equipo). Lee lo que haya: código, ADRs, RFCs, design docs, dashboards, postmortems.
2. **Camino similar**: si no hay sistema propio, busca con `research` dos o tres sistemas parecidos documentados por quien ya los resolvió (blogs de ingeniería, papers, charlas). Extrae sus fuerzas y decisiones, y marca qué es distinto en tu caso: su escala no es tu escala, su equipo no es tu equipo.
3. **Arquetipo de negocio**: si no hay sistema ni métricas (lo normal en un diseño exploratorio o un PoC), identifica el tipo de negocio (streaming, fintech, ticketing, e-commerce, social, SaaS B2B, IoT, movilidad, healthtech, plataforma de IA, plataforma de eventos) con `business-archetypes`. El arquetipo aporta las fuerzas dominantes, los invariantes, la forma de la carga, los subdominios típicos, los modos de fallo y las preguntas que cambian el diseño. Se combina con el camino similar cuando lo hay.

   **Si diseñas una API, una plataforma o un componente que usan otros**, el arquetipo es el del **negocio que lo consume**, no el de la API. Una API de feature flags para una fintech hereda auditoría y control estricto de cambios; para un e-commerce, picos de campaña y despliegues frecuentes. Lo propio de la API (cómo resuelven otros el mismo problema técnico) sale del camino similar. Si hay varios consumidores, cada arquetipo aporta sus requisitos y el diseño cubre su unión o elige uno de forma explícita.

El protocolo completo está en [references/punto-de-partida.md](references/punto-de-partida.md). Completa este paso cuando puedas describir el punto de partida (AS-IS, referencia o arquetipo) en un diagrama o una tabla de fuerzas, con los huecos explícitos.

### 1. Requisitos como delta

Funcionales, no funcionales y **fuera de alcance**, expresados como cambio respecto al punto de partida ("hoy X; necesitamos Y"). Incluye los requisitos que no se ven en un enunciado: restricciones de compliance (PCI, datos personales), contratos con terceros, calendario de eventos, equipos disponibles, presupuesto. Para el catálogo de preguntas, invoca `building-blocks` y lee su bloque `requirements-scoping`.

### 2. Números

Invoca `capacity-estimation`. En un sistema existente, mide antes de estimar. Sin métricas, trabaja con **escenarios por orden de magnitud** derivados del arquetipo y calcula los **umbrales** en los que cada decisión cambia: el diseño no necesita saber si habrá 1 000 o 100 000 usuarios, necesita saber a partir de cuántos deja de servir. Cada número lleva su fuente (medido, referencia, arquetipo o supuesto) y la decisión que habilita.

### 3. Alternativas

Propón **dos o tres** diseños que respondan de forma distinta a la tensión principal (por ejemplo, síncrono vs basado en eventos, compartir la base vs separar datos, extender el sistema actual vs reemplazar una parte). Uno de ellos debe ser **el cambio mínimo sobre lo existente**. Incluye para cada uno un diagrama en Mermaid y su boceto de interfaz (request, response, key primaria, paginación, idempotencia).

Para cada componente, invoca `building-blocks` y lee el bloque que corresponde en lugar de reconstruir su receta de memoria. Si la discusión es sobre fronteras entre contextos o servicios, invoca `strategic-design`.

### 4. Trade-offs y decisión

Para cada decisión importante responde las tres preguntas: **qué resuelve**, **qué empeora** y **qué te haría cambiarla**. Ver el contrato de respuesta abajo. Compara las alternativas en esos términos y recomienda una, con firmeza.

### 5. Red team

Invoca `design-stress-test` sobre la alternativa elegida (y sobre el sistema actual, si el objetivo es justificar el cambio). Los riesgos que cambian el diseño vuelven al paso 3 o 4.

### 6. Camino de migración o plan del experimento

En un PoC, este paso es el **plan del experimento**: hipótesis ordenadas por riesgo, lo mínimo que hay que construir para validar cada una, qué se instrumenta desde el día uno, criterios de éxito y de abandono, y qué se difiere a propósito (ver [references/exploratorio-y-poc.md](references/exploratorio-y-poc.md)). En un diseño exploratorio, basta con nombrar el primer paso y las puertas de un sentido que habría en el camino.

En un sistema existente, diseña cómo se pasa del estado actual al objetivo sin parar el sistema: pasos ordenados, cada uno desplegable y verificable, con el patrón que usa (strangler fig, expand-contract, outbox, shadow traffic, dual-run con comparación, canary), su criterio de éxito y si es **reversible** (puerta de dos sentidos) o no (puerta de un sentido). Los patrones están en [references/migracion.md](references/migracion.md).

### 7. Iterar y cerrar

Profundiza en el componente más frágil. Antes de cerrar, haz un **barrido de cobertura** con la tabla de `building-blocks`: cada bloque plausible se abre o se descarta explícitamente con una línea. Puntúa el diseño con [references/rubrica.md](references/rubrica.md) y nombra la dimensión más débil.

## Contrato de respuesta

Cada propuesta de diseño (primera o revisada) incluye, en la respuesta misma:

- **Tabla de decisiones**, al menos tres filas en un diseño completo:

  | Decisión | Resuelve | Empeora | Cámbiala cuando… |
  |---|---|---|---|

  La última columna es un disparador concreto, un número o una señal observable ("escrituras > 5k/s sostenidas en el primario", "un segundo equipo necesita desplegar por separado"), nunca "si hace falta".
- **Línea de punto débil**: lo que se rompe primero cuando crecen la carga o los requisitos, y el movimiento que harías entonces.
- En un sistema existente, el **delta**: qué cambia respecto al AS-IS y qué se queda igual.

Una lista de pros y contras, o trade-offs para una sola decisión, no cumple el contrato.

## Persistir

- **Design doc** con [references/plantilla-design-doc.md](references/plantilla-design-doc.md), en la ruta que use el repo (si no hay convención, `docs/design/<sistema>.md`; pregunta si dudas). Las discusiones se quedan en la conversación; al documento van los resultados.
- **ADRs** para las decisiones difíciles de revertir, sorprendentes y con trade-off real, usando `domain-modeling`.
- **Términos del dominio** nuevos al glosario, con `domain-modeling`.

## Guardarraíles

- Aclara antes de diseñar y cuantifica antes de elegir: con mediciones si existen, con escenarios y umbrales si no. La falta de métricas se declara, no se esconde ni bloquea.
- Justifica cada componente con las tres preguntas; "es el estándar de la industria" no es una justificación.
- Conoce cómo se comporta cada bloque bajo estrés, no solo su nombre.
- La opción más barata que cumple las restricciones suele ganar: monolito modular antes que microservicios, base relacional antes que sharding, hasta que un número lo fuerce.
- Los límites de servicios gestionados (cuotas, tamaños, precios) se verifican con `research` en el momento; la memoria del modelo los tiene desactualizados.
- Ningún diseño es perfecto: cierra siempre con el punto débil y lo que harías con un orden de magnitud más.
