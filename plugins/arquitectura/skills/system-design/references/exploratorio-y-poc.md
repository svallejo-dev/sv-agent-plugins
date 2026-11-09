# Diseño exploratorio y PoC

Cuando no hay sistema ni métricas, el diseño no se detiene: cambia de pregunta. En vez de "¿cuál es la arquitectura correcta para esta carga?", pregunta **"¿qué arquitectura sigue siendo razonable en todo el rango de cargas plausibles, y qué hay que aprender primero?"**.

**Analogía:** un explorador sin mapa no se queda quieto. Usa la brújula (el arquetipo del negocio), avanza por terreno que permite volver atrás y marca en el cuaderno lo que va aprendiendo para dibujar el mapa después.

## Diseño exploratorio

1. **Arquetipo como punto de partida.** Con `business-archetypes`, identifica el tipo de negocio y extrae fuerzas, invariantes, subdominios y modos de fallo. Si el producto mezcla arquetipos, asigna cada uno a su subdominio.
2. **Escenarios, no números.** Define tres escenarios por orden de magnitud (pequeño, medio, grande) con `capacity-estimation` en modo exploratorio. Diseña para el escenario que el negocio considera probable a 12-18 meses y verifica qué se rompe en el siguiente.
3. **Umbrales de decisión.** Para cada decisión que depende de la escala, calcula a partir de qué valor deja de servir ("un solo primario sirve hasta unos X usuarios activos diarios con este patrón"). Ese umbral va a la columna "cámbiala cuando…".
4. **Invariantes antes que escala.** Las reglas del negocio que no admiten error (no sobrevender, no cobrar dos veces, no mezclar datos de tenants) se diseñan bien desde el principio aunque la carga sea pequeña; la escala se puede ganar después, la corrección casi nunca.
5. **Puertas de dos sentidos.** Prefiere decisiones baratas de revertir. Las de un sentido (modelo de datos de los invariantes, contratos públicos, proveedor con lock-in) se señalan y se toman con más evidencia.

## PoC

Un PoC existe para **reducir la incertidumbre más cara**, no para demostrar que algo funciona en el caso feliz.

### Plan del experimento

| Elemento | Qué contiene |
|---|---|
| **Hipótesis** | Afirmaciones falsables, ordenadas por riesgo × costo de equivocarse ("la pasarela soporta 50 autorizaciones/s en sandbox con p99 < 2 s") |
| **Alcance mínimo** | Lo justo para probar cada hipótesis; todo lo demás se simula, se stubbea o se compra |
| **Instrumentación** | Las métricas que reemplazarán a los supuestos del arquetipo, activas desde el primer día |
| **Criterio de éxito** | El resultado medible que confirma la hipótesis |
| **Criterio de abandono** | El resultado que la refuta y qué se haría entonces (cambiar de enfoque, de proveedor, cancelar) |
| **Deuda deliberada** | Lo que se deja fuera a propósito (alta disponibilidad, multi-región, automatización) y la condición para retomarlo |

### Reglas

- Ataca primero la hipótesis que, si es falsa, invalida el proyecto (integración con un tercero, invariante bajo concurrencia, costo unitario).
- Prueba los fallos, no solo el camino feliz: timeouts, duplicados, concurrencia sobre el mismo recurso.
- Distribuciones realistas: datos y carga sesgados (hot keys, usuarios gigantes) en lugar de uniformes.
- Instrumenta aunque el PoC sea pequeño: el objetivo es convertir supuestos en mediciones.
- Escribe al final qué se aprendió y qué supuestos del diseño cambian; eso alimenta la versión de producción.

### Del plan al código

El plan del experimento **es la spec del PoC**. No hace falta pasarlo por `to-spec` ni partirlo con `to-tickets`: esas skills están pensadas para features de producción y aquí duplicarían el plan con una plantilla que no encaja.

1. Construye **una hipótesis a la vez**, en el orden del plan (la más cara de equivocarse primero). Si hay un tercero, la primera es el walking skeleton contra su sandbox.
2. Usa `tdd` solo para el núcleo de invariantes (no cobrar dos veces, no sobrevender); el resto puede ser código desechable.
3. Cierra cada hipótesis con un **veredicto** (confirmada, refutada o no concluyente), la medición que lo respalda y qué cambia en el diseño. Regístralo en la sección del plan del design doc, o en `resultados.md` junto a él.
4. Si se refuta una hipótesis, aplica su criterio de abandono antes de seguir con la siguiente: puede que las demás ya no importen.

`to-spec` aporta solo si el PoC se construye en varias sesiones o lo construye otra persona, para dejar escritas las decisiones de implementación (stack, modelo de datos); como complemento del plan, no como sustituto. Para traspasar el trabajo, `handoff`.

### Del PoC a producción

Al terminar el PoC, vuelve a `system-design` en modo producción con un **punto de partida nuevo**: el PoC ya es un sistema existente con métricas propias. Los supuestos del arquetipo que se midieron se reemplazan por sus valores reales; los que no, siguen marcados como supuestos.
