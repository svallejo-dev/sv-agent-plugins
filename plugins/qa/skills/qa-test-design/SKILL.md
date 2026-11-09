---
name: qa-test-design
description: "Diseña los escenarios de prueba de una feature a partir de criterios aprobados y del contrato de handoff, con sub-agentes en paralelo por técnica (particiones y límites, tablas de decisión y estados, terceros y oráculo de uso, fallos y entorno, error guessing y abuso); asigna cada escenario a un peldaño y lo traza a sus criterios. Úsala cuando el usuario pida \"diseñar pruebas\", \"escenarios de prueba\", \"casos de prueba\", \"test cases\", \"plan de pruebas\" o después de aprobar criterios con qa-acceptance-criteria."
license: MIT
---

# Diseño de escenarios

Responde en español y conserva en inglés los términos técnicos habituales.

Convierte criterios aprobados en escenarios concretos: datos exactos, acción, resultado esperado y oráculo, cada uno en el peldaño donde puede fallar por la razón correcta. Esta es la capa más barata para detectar defectos de spec: un escenario se escribe en minutos y puede revelar que nadie sabe qué debe pasar.

**Analogía:** un inspector de puentes no prueba "si el puente aguanta". Prueba la carga máxima, la carga justo por encima, el viento lateral, el tráfico detenido en la mitad y un camión frenando de golpe. Cada técnica es una forma sistemática de elegir qué cargas probar sin depender de la intuición del día.

Lee primero [../qa-core/referencias/modelo-de-roles.md](../qa-core/referencias/modelo-de-roles.md), [../qa-core/referencias/escalera-de-ambientes.md](../qa-core/referencias/escalera-de-ambientes.md) y [../qa-core/referencias/formatos.md](../qa-core/referencias/formatos.md).

## 0. Precondiciones: si falta algo, para

1. `docs/agentes/qa.md` existe. Si no, pide ejecutar la skill `qa-setup` y para.
2. `.scratch/<feature>/qa/criterios.md` tiene `Estado: aprobado`. Si está en borrador, para: los escenarios se diseñan contra criterios aprobados, no contra borradores.
3. **Contrato de handoff** (`.scratch/<feature>/qa/handoff.md`) con las piezas obligatorias: superficie, consumidores, dependencias y artefacto ejecutable, y cada seam de testabilidad respondido. Si falta una pieza obligatoria, **no diseñes**: lista lo que falta, marca el handoff como `Estado: devuelto` y dile al usuario qué debe completar el dev. En modo solo, el humano completa el handoff antes de seguir.
4. **Regla de contaminación**: igual que en `qa-acceptance-criteria`. Si esta sesión vio código de producción de la feature, todo el diseño se hace en los sub-agentes del paso 1, y la consolidación (paso 2) se delega a otro sub-agente limpio que recibe solo sus salidas; la sesión principal ejecuta el script, presenta y sella.

## 1. Sub-agentes en paralelo, uno por familia de técnicas

Lanza los cinco sub-agentes juntos, cada uno con contexto limpio. Cada sub-agente recibe: los criterios aprobados, el handoff, los contratos de API, la escalera de ambientes y **su** sección de técnicas pegada completa desde [references/tecnicas.md](references/tecnicas.md). Ninguno recibe código de producción.

> **Portabilidad:** si tu herramienta no tiene sub-agentes, sigue [../qa-core/referencias/portabilidad.md](../qa-core/referencias/portabilidad.md) y decláralo en el artefacto.

| Sub-agente | Técnicas | Material adicional |
|---|---|---|
| A | Particiones de equivalencia y valores límite | — |
| B | Tablas de decisión, transición de estados, combinatoria (pairwise) | — |
| C | Integración con terceros y oráculo de uso | [references/terceros.md](references/terceros.md) completa; [../acceptance-criteria/references/oraculo-de-uso.md](../qa-acceptance-criteria/references/oraculo-de-uso.md) |
| D | Fallos y entorno: dependencias, tiempo, concurrencia, idempotencia, datos | Los modos de fallo del arquetipo (`business-archetypes`) si aplica y está disponible |
| E | Error guessing, abuso y seguridad básica | Incidentes previos del sistema, si existen |

Encargo para cada uno:

"Eres QA de la feature <feature>. Aplica SOLO tu familia de técnicas (<familia>) a estos criterios aprobados. No leas código de producción. Para cada escenario devuelve una fila: criterio(s) AC-NN, técnica, peldaño propuesto (con la regla de asignación de la escalera: el más bajo donde el comportamiento es observable y el oráculo es confiable), escenario en forma Dado/Cuando/Entonces con datos concretos, oráculo y, si necesita un seam de testabilidad, cuál. Si un criterio es ambiguo para tu técnica, no lo resuelvas inventando: anótalo como pregunta. Si encuentras un comportamiento que ningún criterio cubre, repórtalo como criterio faltante, no como escenario huérfano. Responde en español, como tabla más una lista de preguntas y criterios faltantes."

**Por qué en paralelo y separados:** un solo agente que aplica todas las técnicas tiende a quedarse con las primeras ideas y a recortar las demás. Cada técnica en su propio contexto produce los casos que esa técnica, y solo esa, encuentra.

## 2. Consolida

1. **Criterios faltantes y preguntas** primero: si algún sub-agente encontró un comportamiento sin criterio o una ambigüedad, eso vuelve a `qa-acceptance-criteria` antes de seguir. Un escenario sin criterio no se agrega por la puerta de atrás.
2. **Deduplica**: dos escenarios con el mismo comportamiento y datos equivalentes son uno. Conserva la técnica que lo justifica mejor.
3. **Agrupa** como esquema de escenario (tabla de ejemplos) los casos que solo varían en datos: es más legible y cada fila sigue contando.
4. **Asigna IDs** `ESC-NN` y el peldaño con la regla de asignación. No subas un escenario de peldaño para esquivar un seam faltante: márcalo `bloqueado-testabilidad`. Los escenarios que además sirven de smoke en staging llevan `1, 4` en la columna Peldaño, con el mismo ID.
5. **Walking skeleton**: si hay un tercero o un consumidor externo nuevo, el primer escenario (`ESC-01` cuando sea posible) es el recorrido más delgado de punta a punta con el consumidor real, en peldaño 3. Ver [references/terceros.md](references/terceros.md).
6. **Poda por riesgo, no por cansancio**: si el conjunto es demasiado grande, conserva siempre los escenarios de criterios de prioridad crítica, todos los límites y todas las transiciones inválidas de estado. Lo que se poda queda en la misma tabla con `Estado: descartado` y el motivo; no desaparece en silencio.

## 3. Comprueba la cobertura con el script

Escribe `.scratch/<feature>/qa/escenarios.md` con el formato de [../qa-core/referencias/formatos.md](../qa-core/referencias/formatos.md) y ejecuta:

```bash
python3 <qa-core>/scripts/trazabilidad.py \
  --criterios .scratch/<feature>/qa/criterios.md \
  --escenarios .scratch/<feature>/qa/escenarios.md
```

`<qa-core>` es la carpeta de la skill `qa-core`, hermana de esta. El resultado debe salir sin huecos: cada criterio con al menos un escenario ejecutable. Un criterio cubierto solo por escenarios bloqueados **es un hueco**, no una cobertura.

## 4. Revisión y aprobación

Presenta al humano:
1. Preguntas abiertas y criterios faltantes (si quedaron).
2. **Deuda de testabilidad**: escenarios bloqueados y qué seam los desbloquea.
3. Walking skeleton y escenarios de oráculo de uso.
4. La tabla completa, agrupada por criterio.

- **Modo dúo**: el dev revisa solo la **realizabilidad** (¿el sistema expone lo necesario para observarlo?). Puede pedir aclaraciones, no recortar escenarios.
- **Aprobación**: solo el humano cambia a `Estado: aprobado`. Nunca te auto-apruebes.

## 5. Sella el diseño

Con el diseño aprobado, sella criterios, escenarios y la configuración de QA, para que ningún agente los cambie sin dejar rastro (desde la raíz del repo; `<Aceptación>` sale de `docs/agentes/qa.md`):

```bash
python3 <qa-core>/scripts/sello.py sellar --sello <Aceptación>/<feature>/.qa-sello.json \
  --motivo "diseño aprobado" .scratch/<feature>/qa/criterios.md .scratch/<feature>/qa/escenarios.md \
  docs/agentes/qa.md
```

Si el diseño cambia más adelante (un hallazgo de spec, un mutante sobreviviente), se re-sella con `resellar` y un motivo que cite el `E-NN` o `H-NN`. Siguiente paso: `qa-test-automation`.
