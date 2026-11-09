---
name: diagnosing-bugs
description: "Ciclo de diagnóstico para bugs difíciles y regresiones de rendimiento, en cualquier lenguaje. Úsala cuando el usuario diga \"diagnostica\", \"debug this\", \"depura\" o reporte algo roto, que lanza error, falla, da resultados distintos o va lento."
license: MIT
---

# Diagnóstico de bugs

Responde en español y conserva en inglés los términos técnicos habituales.

Una disciplina para bugs difíciles. Sáltate fases solo con una justificación explícita.

Al explorar el código, lee `GLOSARIO.md` (si existe) para tener un modelo mental claro de los módulos implicados, y revisa los ADRs del área.

## Lenguaje

Esta skill es agnóstica al lenguaje. Identifica el lenguaje del código implicado por las extensiones de sus archivos (`.go` → `go`, `.php` → `php`, `.ts`/`.tsx` → `typescript`, `.py` → `python`). Si entre tus skills disponibles existe `<lenguaje>-debugging`, cárgala (en Claude Code, con la herramienta Skill; en otras herramientas, mencionándola por su nombre o leyendo su SKILL.md) al empezar la Fase 1: aporta los comandos concretos para cada técnica (ejecutar un solo test, repetirlo, fuzzing, race detector, debugger, profiler, benchmarks). Si no existe, sigue solo con esta skill y dilo en una línea.

## Redacta

Esta skill te hace mostrar comandos, salidas y artefactos capturados. **Redacta antes todo secreto**: escribe `<REDACTED>` en su lugar. Construye los loops leyendo credenciales de variables de entorno, para que el secreto se quede en el entorno y no en lo que muestras. Los artefactos capturados llevan headers de auth: cita solo las líneas con señal.

Si la salida redactada no basta para diagnosticar, dilo y pregunta al usuario.

## Fase 0: Escucha las sospechas del usuario

Si el usuario llega con una hipótesis ("creo que es el cache"), anótala tal cual como candidata para la Fase 3 y agradécela, pero no la investigues todavía. Explícale en una línea por qué primero va el loop: sin una señal que se ponga roja, no hay forma de saber si la sospecha es cierta.

Analogía: un médico escucha lo que el paciente cree que tiene, pero no receta hasta tener el resultado del análisis.

## Fase 1: Construye un feedback loop

**Esta es la skill.** Lo demás es mecánico. Si tienes una señal de pasa/falla **tight** para el bug (una que se pone **roja** en _este_ bug), vas a encontrar la causa: bisección, prueba de hipótesis e instrumentación solo la consumen. Si no la tienes, ninguna cantidad de leer código te salvará.

Dedica un esfuerzo desproporcionado aquí. **Sé agresivo. Sé creativo. No te rindas.**

### Formas de construirlo, más o menos en este orden

1. **Test que falla** en el seam que alcance el bug: unitario, de integración o e2e, ejecutado de forma aislada.
2. **Script curl / HTTP** contra un servidor de desarrollo levantado.
3. **Invocación CLI** con una entrada fija, comparando stdout con una salida buena conocida.
4. **Replay de una traza capturada.** Guarda en disco una petición, payload o evento real (de logs, de Kafka, de un HAR) y reprodúcelo por el código en aislamiento.
5. **Harness desechable.** Levanta un subconjunto mínimo del sistema (un servicio, dependencias falsas) que ejercite el camino del bug con una sola llamada.
6. **Fuzz / propiedad.** Si el bug es "a veces da mal resultado", usa el fuzzer del lenguaje o 1000 entradas aleatorias y busca el modo de fallo.
7. **Harness de bisección.** Si el bug apareció entre dos estados conocidos (commit, dataset, versión), automatiza "arranca en el estado X, comprueba, repite" para usar `git bisect run <comando-del-loop>`.
8. **Loop diferencial.** Pasa la misma entrada por la versión vieja y la nueva (o dos configuraciones) y compara salidas. Ideal en migraciones entre stacks (por ejemplo, un servicio legacy frente a su reescritura): el legacy es el oráculo.
9. **Script bash con humano en el loop.** Último recurso. Si una persona tiene que hacer clic o mirar un dashboard, guíala con `scripts/hitl-loop.template.sh` para que el loop siga siendo estructurado. Lo capturado vuelve a ti.

Construye el loop correcto y el bug está arreglado al 90 %.

**Si llegas con un hallazgo de `qa-verify` (H-NN):** su comando de reproducción en el peldaño hermético ya es un loop. Úsalo como punto de partida y bájalo: primero a un test de integración, después a uno unitario, hasta el seam más bajo que se ponga rojo. Cada bajada reduce el área donde puede estar el defecto.

### Ajusta el loop

Trata el loop como un producto. Cuando tengas _un_ loop, hazlo **tight**:

- ¿Puede ir más rápido? (Cachea el setup, salta inicializaciones que no aplican, ejecuta solo el test que importa.)
- ¿Puede dar una señal más nítida? (Aserta el síntoma concreto, no "no se cayó".)
- ¿Puede ser más determinista? (Fija el tiempo, la semilla aleatoria, aísla el filesystem en un directorio temporal, congela la red.)

Un loop de 30 segundos e intermitente casi no vale; uno de 2 segundos y determinista es tight, un superpoder de depuración.

### Bugs no deterministas

El objetivo no es una reproducción limpia sino una **tasa de reproducción más alta**. Repite el disparador 100 veces, paraleliza, activa el detector de data races si el lenguaje lo tiene, añade carga, estrecha ventanas de tiempo, inyecta pausas. Un bug que falla el 50 % de las veces se puede depurar; uno del 1 % no, así que sube la tasa hasta que se pueda.

### Cuando de verdad no puedes construir un loop

Para y dilo explícitamente. Lista lo que intentaste. Pide al usuario: (a) acceso al entorno que lo reproduce, (b) un artefacto capturado y redactado (dump de logs, consulta NRQL o de Sumo Logic con su resultado, trazas, HAR, grabación con timestamps), o (c) permiso para añadir instrumentación temporal en producción. **No** pases a hipótesis sin loop.

### Criterio de cierre: un loop tight que se pone rojo

La Fase 1 termina cuando puedes nombrar **un comando** (un script, una invocación de test, un curl) que **ya ejecutaste al menos una vez** (muestra la invocación y su salida, redactada) y que es:

- [ ] **Capaz de ponerse rojo**: recorre el camino real del bug y aserta el **síntoma exacto del usuario**, así que puede ponerse rojo con este bug y verde cuando se arregle. No "corre sin error": tiene que poder _atrapar este bug_.
- [ ] **Determinista**: mismo veredicto en cada ejecución (en bugs intermitentes, una tasa de reproducción alta y fijada).
- [ ] **Rápido**: segundos, no minutos.
- [ ] **Ejecutable por el agente**: puedes correrlo sin supervisión; un humano solo vía `scripts/hitl-loop.template.sh`.

Si te pillas leyendo código para armar una teoría antes de que exista ese comando, **para: saltar directo a una hipótesis es justo el fallo que esta skill previene.** Sin comando capaz de ponerse rojo, no hay Fase 2.

## Fase 2: Reproduce y minimiza

Corre el loop. Míralo ponerse rojo cuando aparece el bug.

Confirma:

- [ ] El loop produce el modo de fallo que describió el **usuario**, no otro fallo cercano. Bug equivocado = arreglo equivocado.
- [ ] El fallo se reproduce en varias ejecuciones (o, si es no determinista, con una tasa suficiente para depurar).
- [ ] Capturaste el síntoma exacto (mensaje de error, salida incorrecta, tiempo) para verificar después que el arreglo lo resuelve.

### Minimiza

Cuando esté rojo, reduce la reproducción al **escenario más pequeño que sigue en rojo**. Quita entradas, llamadores, configuración, datos y pasos **uno a uno**, corriendo el loop tras cada corte, y quédate solo con lo que sostiene el fallo.

Por qué: una reproducción mínima reduce el espacio de hipótesis en la Fase 3 y se convierte en el test de regresión limpio de la Fase 5.

Termina cuando **cada elemento restante sostiene el fallo**: quitar cualquiera pone el loop en verde.

No sigas hasta haber reproducido **y** minimizado.

## Fase 3: Hipótesis

Genera **de 3 a 5 hipótesis ordenadas** antes de probar ninguna (incluye las sospechas de la Fase 0). Generar una sola ancla en la primera idea plausible.

Cada hipótesis debe ser **falsable**: enuncia la predicción que hace.

> Formato: "Si la causa es <X>, entonces <cambiar Y> hará desaparecer el bug / <cambiar Z> lo empeorará."

Si no puedes enunciar la predicción, la hipótesis es una corazonada: descártala o afínala.

**Muestra la lista ordenada al usuario antes de probar** y pregúntale cuál reordenaría y por qué. Suele tener conocimiento del dominio que la reordena al instante ("ayer desplegamos un cambio en la 3") o sabe cuáles ya descartó. Es un checkpoint barato que ahorra mucho tiempo. No te bloquees: si el usuario no está, sigue con tu orden.

## Fase 4: Instrumenta

Cada sonda corresponde a una predicción concreta de la Fase 3. **Cambia una variable a la vez.**

Preferencia de herramientas:

1. **Debugger** o REPL, si el entorno lo permite. Un breakpoint vale más que diez logs.
2. **Logs dirigidos** en las fronteras que distinguen hipótesis.
3. Nunca "loguear todo y hacer grep".

**Etiqueta cada log de depuración** con un prefijo único, por ejemplo `[DEBUG-a4f2]`. La limpieza final se vuelve un solo grep. Los logs sin etiqueta sobreviven; los etiquetados mueren.

**Rama de rendimiento.** En regresiones de rendimiento, los logs suelen ser la herramienta equivocada. Primero establece una línea base: un benchmark repetido varias veces y comparado estadísticamente, y un perfil (CPU, memoria, contención). En producción, apóyate en el APM (New Relic u otro) mirando percentiles (p50/p95/p99), no el promedio. Después biseca. Primero medir, después arreglar.

## Fase 5: Arreglo y test de regresión

Escribe el test de regresión **antes del arreglo**, pero solo si hay un **seam correcto** para él.

Un seam correcto es uno donde el test ejercita el **patrón real del bug** tal como ocurre en el punto de llamada. Si el único seam disponible es demasiado superficial (un test con un solo llamador cuando el bug necesita varios, un unitario que no puede replicar la cadena que lo disparó), un test ahí da falsa confianza.

**Si no existe un seam correcto, eso mismo es un hallazgo.** Anótalo: la arquitectura impide fijar el bug. Recomiéndale al usuario `codebase-design` para tratarlo.

Si existe un seam correcto:

1. Convierte la reproducción mínima en un test que falla en ese seam.
2. Míralo fallar. Si forzaste el rojo mutando código o un fixture, haz `diff` contra una copia limpia para probar que la mutación se aplicó antes de fiarte.
3. Aplica el arreglo.
4. Míralo pasar.
5. Vuelve a correr el loop de la Fase 1 contra el escenario original (sin minimizar).

## Fase 6: Limpieza

Obligatorio antes de dar por terminado:

- [ ] La reproducción original ya no reproduce (vuelve a correr el loop de la Fase 1).
- [ ] El test de regresión pasa (o la ausencia de seam está documentada).
- [ ] Toda la instrumentación `[DEBUG-...]` eliminada (`grep -rn "DEBUG-a4f2"`).
- [ ] Prototipos desechables borrados (o movidos a un lugar de depuración claramente marcado).
- [ ] La hipótesis que resultó correcta queda escrita en el mensaje del commit o del PR, para que el siguiente que depure aprenda.
