# Modelo de roles del plugin qa

Referencia compartida por todas las skills de `qa`. Define quién escribe qué, quién aprueba y qué información ve cada uno.

**Analogía:** un examen bien hecho. Quien estudia (dev) no redacta las preguntas; quien redacta (QA) no corrige con la respuesta del alumno a la vista; la máquina de lectura óptica (ejecutor determinista) cuenta los aciertos; y el profesor (humano) decide si aprueba. Si una sola persona hace las cuatro cosas, el 10 no significa nada.

## Principio que no cambia en ningún modo

**El agente que implementa nunca escribe ni edita el oráculo.** El oráculo son los criterios de aceptación, los escenarios y los tests de aceptación ejecutables. Da igual si detrás hay una persona o dos: la separación es entre **agentes con contextos distintos**, no entre personas.

Fundamento: un agente que escribe el código y sus propios tests de aceptación comparte con ellos sus suposiciones (anclaje del oráculo). Y un agente presionado por un test en rojo puede hacer trampa: en ImpossibleBench (2025), los modelos de Claude y Qwen3-Coder hicieron más del 79 % de sus trampas modificando tests, mientras que otros modelos prefirieron el *special-casing* (código que reconoce los datos del test y responde lo que el test espera). Los autores recomiendan tests ocultos o de solo lectura, y advierten que el solo lectura **no** elimina el special-casing. Por eso este plugin combina tres defensas: tests de solo lectura y sellados, datos de prueba aleatorios sin marcas reconocibles, y revisión humana del código y de cada re-sellado.

## Roles

| Rol | Quién | Escribe | Nunca |
|---|---|---|---|
| **Dev** | Agente implementador (`tdd`) | Código y sus tests unitarios y de integración (lazo interno) | Editar criterios, escenarios, tests de aceptación ni el sello |
| **QA** | Agente diseñador de pruebas, con contexto limpio | Criterios, escenarios, tests de aceptación, learning tests, mutantes | Leer el cuerpo del código de producción; editar código de producción |
| **Ejecutor** | Runners y los scripts de `scripts/` | Resultados: JUnit, sello, trazabilidad, mutantes | Opinar: solo cuenta |
| **Humano** | El dev (modo solo) o el QA y el dev (modo dúo) | Aprobaciones y decisiones de escalamiento | Delegar la aprobación en un agente |

**El QA no certifica.** Ningún agente declara "aprobado", "listo para producción" ni "certificado". `qa-verify` entrega evidencia y el estado de cada puerta; la decisión es humana.

## Modos de operación

Se declaran en `docs/agentes/qa.md` (`qa-setup`).

**La regla de contaminación** (si una sesión ya vio el código de producción de la feature, no escribe el oráculo) también es de buena fe, como N1: ninguna puerta comprueba qué leyó una sesión. Se declara, no se demuestra.

### Modo solo: el dev diseña las pruebas

Una persona hace de dev y de aprobador de los criterios.

- Los criterios y escenarios los escribe un **sub-agente QA** con contexto limpio, con un brief cerrado: recibe solo el contrato de handoff, nunca el diff ni el código. Si la sesión principal ya implementó código, **no puede** escribir los escenarios ella misma: está contaminada.
- El humano aprueba criterios y escenarios **antes** de que empiece la implementación del ticket.
- Riesgo propio del modo: **sesgo del autor**. La misma persona escribió la spec y aprueba los tests, así que comparte sus puntos ciegos. Mitigaciones **obligatorias** en este modo:
  1. Las técnicas de diseño de `qa-test-design` se aplican completas, sin elegir a mano cuáles saltar: son la lista de verificación que el autor no escribió.
  2. Premortem de criterios en `qa-acceptance-criteria`.
  3. `qa-test-the-tests` es puerta obligatoria del ritmo completo, no opcional.

### Modo dúo: QA aparte

Un QA humano opera el plugin `qa`; el dev opera `ingenieria`.

- La entrada del QA es el **contrato de handoff** (ver [formatos.md](formatos.md)). `qa-test-design` se niega a empezar si falta una pieza obligatoria.
- El dev revisa los escenarios solo para confirmar que son **realizables** (que el sistema expone lo necesario para observarlos), no para recortarlos. Es un "three amigos" asíncrono: negocio (spec), dev y QA miran el mismo escenario antes de construir.
- Riesgo propio del modo: **handoff incompleto**. Sin seams de testabilidad, el QA no puede probar desde fuera los casos difíciles.

## Barrera de información: tres niveles

La barrera entre lo que ve el QA y el código se declara en la configuración, y `qa-verify` informa cuál se usó. Declararla con honestidad es parte del rigor: un N1 que dice ser N3 es peor que un N1 declarado.

| Nivel | Cómo | Qué garantiza |
|---|---|---|
| **N1: convención** | Sub-agente con brief que prohíbe leer el código de producción | Separación de contexto; la lectura de código no queda impedida, solo instruida |
| **N2: directorio aislado** | El QA trabaja en una copia que contiene solo `.scratch/<feature>/`, los contratos de API y la carpeta de aceptación | El código no está disponible en su directorio de trabajo |
| **N3: persona distinta** | Otro humano con su propia sesión y sin acceso al repositorio de código | Separación real de información |

QA en **caja gris**: ve la spec, la arquitectura (qué dependencias hay), los contratos de API y los seams de testabilidad. No ve el cuerpo del código.

## Escalamiento: cuando el dev cree que un test está mal

El dev **nunca** edita un test de aceptación para ponerlo en verde, aunque esté convencido de que el test está mal. Escala:

1. Registra la entrada en `.scratch/<feature>/qa/escalamientos.md` (formato en [formatos.md](formatos.md)) con el escenario, su argumento y la evidencia.
2. Detiene el trabajo de ese escenario, no del ticket entero.
3. El QA (o el humano en modo solo, con el sub-agente QA) resuelve con una de tres decisiones:
   - **Test corregido**: el test no reflejaba el criterio. El QA lo corrige y vuelve a sellar citando el escalamiento (`--motivo "E-03: ..."`).
   - **Spec corregida**: el test refleja la spec, pero la spec estaba mal. Vuelve a `qa-acceptance-criteria` y, si hace falta, a la spec.
   - **Rechazado**: el test es correcto; el código debe cambiar.

Cada corrección de un test queda en el historial del sello con su motivo, que debe citar el `E-NN` o `H-NN` que la originó.

**Lo que el sello garantiza y lo que no.** El sello no impide editar: un agente puede editar un test y volver a sellar. Lo que garantiza es que no puede hacerlo **sin que quede a la vista**: `qa-verify` compara el sello contra el de la rama base y lista cada sellado y re-sellado hecho desde entonces; un re-sellado de un sello que ya existía en la base sin `E-NN`/`H-NN` rompe la puerta, y borrar o recrear el sello también. La decisión sobre esos re-sellados es humana, en la revisión del PR. Impedir la edición según el rol (hooks) es trabajo futuro.

## Mapa de artefactos y permisos

| Artefacto | Ruta por defecto | Escribe | Aprueba |
|---|---|---|---|
| Spec | `.scratch/<feature>/spec.md` | Dev (`to-spec`) | Humano |
| Handoff | `.scratch/<feature>/qa/handoff.md` | Dev | QA (lo acepta o lo devuelve) |
| Criterios | `.scratch/<feature>/qa/criterios.md` | QA | Humano |
| Escenarios | `.scratch/<feature>/qa/escenarios.md` | QA | Humano; el dev confirma realizabilidad |
| Tests de aceptación y scripts de peldaño | `<Aceptación>/<feature>/` y `<Aceptación>/bin/` (ver `docs/agentes/qa.md`) | QA | Humano revisa Gherkin y Hurl, no la plomería |
| Configuración de QA | `docs/agentes/qa.md` | QA o humano, nunca el dev | Humano |
| Sello | `<Aceptación>/<feature>/.qa-sello.json` (cubre criterios, escenarios, tests, scripts de peldaño y la configuración) | QA, vía `scripts/sello.py` | Humano revisa cada re-sellado listado en `qa-verify` |
| Escalamientos | `.scratch/<feature>/qa/escalamientos.md` | Dev abre, QA o humano resuelve | Humano |
| Verificaciones | `.scratch/<feature>/qa/verificaciones/` | Ejecutor y `qa-verify` | — |
| Mutantes | `.scratch/<feature>/qa/mutantes/` | Agente de mutación (`qa-test-the-tests`) | Humano decide sobre los equivalentes |
