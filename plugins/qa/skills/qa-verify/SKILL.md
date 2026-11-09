---
name: qa-verify
description: "Ejecuta la verificación de una feature por ritmo (por rebanada, completo o post-deploy) con los scripts declarados, pasa por puertas deterministas (sello contra la rama base, caja negra, ejecución fresca, trazabilidad, estabilidad, contratos, mutantes), clasifica cada fallo (código, configuración, spec, test o entorno), lo baja de peldaño y emite hallazgos con evidencia. Nunca certifica: entrega evidencia para que decida un humano. Úsala cuando el usuario pida \"verificar\", \"correr las pruebas de aceptación\", \"QA de la feature\", \"¿está listo?\", o al cerrar un ticket o antes de un PR."
license: MIT
---

# Verificación

Responde en español y conserva en inglés los términos técnicos habituales.

Ejecuta, mide y reporta. Esta skill no escribe tests ni código y no decide si algo está listo: produce la evidencia con la que un humano decide. Su valor está en ser **difícil de complacer**: los comandos están fijados y sellados, las puertas son scripts, cada ejecución usa reportes nuevos y un verde que no se puede trazar hasta un criterio no cuenta.

**Analogía:** el árbitro con VAR. No juega ni elige qué jugadas revisar según le convenga: aplica el reglamento a lo que muestran las cámaras, y el resultado lo firma otro.

Lee primero [../qa-core/referencias/modelo-de-roles.md](../qa-core/referencias/modelo-de-roles.md), [../qa-core/referencias/escalera-de-ambientes.md](../qa-core/referencias/escalera-de-ambientes.md) y [../qa-core/referencias/formatos.md](../qa-core/referencias/formatos.md) (secciones 5 y 7).

## 0. Precondiciones y reglas

- Lee `docs/agentes/qa.md`. Si no existe, pide ejecutar la skill `qa-setup` y para.
- Ejecuta los scripts desde la raíz del repositorio. `<qa-core>` es la carpeta de la skill `qa-core`, hermana de esta; `<Aceptación>`, `<Reportes>` y la rama base salen de `docs/agentes/qa.md`.
- Determina el **ritmo**:
  - `por-rebanada`: los escenarios del ticket (su línea `Escenarios:`), en los peldaños disponibles. Es una comprobación de avance, no una puerta para el PR.
  - `completo`: todos los escenarios, peldaños 1, 2 y 3 si existe, más contratos, fuzzing y mutantes. Es la puerta antes del PR.
  - `post-deploy`: los escenarios con el peldaño 4 en su columna.
  Si el usuario no lo dice: por-rebanada al cerrar un ticket, completo antes de un PR.
- **No modifiques nada** bajo `<Aceptación>/`, `.scratch/<feature>/qa/` (salvo el informe), `docs/agentes/qa.md` ni el código de producción. Si algo necesita cambiar, es un hallazgo.
- **Ejecuta los scripts de peldaño exactamente como están declarados**: sin filtrar escenarios, sin añadir flags, sin cambiar timeouts. Si un script no sirve, es un hallazgo de clase entorno, no un permiso para improvisar otro.
- **Regla de clasificación en modo solo**: si esta sesión implementó código de la feature, no puede clasificar un fallo como `test` o `spec` por sí sola; ese juicio lo confirma un sub-agente QA de contexto limpio o el humano. Quien escribió el código tiende a culpar al test.

## 1. Puertas

Recorre todas las puertas del ritmo y repórtalas todas; solo G1 en rojo detiene las demás.

**G1 · Sello íntegro contra la rama base** (todos los ritmos):

```bash
python3 <qa-core>/scripts/sello.py verificar --sello <Aceptación>/<feature>/.qa-sello.json --base <rama base> \
  --requiere .scratch/<feature>/qa/criterios.md .scratch/<feature>/qa/escenarios.md docs/agentes/qa.md \
  <Aceptación>/<feature> <Aceptación>/bin
```

Rompe si cambió cualquier archivo sellado, si hay enlaces simbólicos, si falta una ruta requerida, o si desde la base el sello se borró, se recreó o se re-selló sin citar `E-NN`/`H-NN`. **Copia siempre al informe la lista de sellados y re-sellados desde la base**, aunque la puerta esté en verde: revisarlos es trabajo del humano en el PR. Si G1 falla, detente: con el oráculo alterado, nada de lo demás significa algo.

**G2 · Caja negra** (todos): la comprobación de `docs/agentes/qa.md`. Falla si algún test importa código de producción **o si la comprobación misma no se pudo ejecutar**.

**G3 · Ejecución fresca** (todos): para cada peldaño del ritmo marcado como disponible:

```bash
export QA_REPORTES=<Reportes>/<feature>/<fecha>-<ritmo>-p<N>; rm -rf "$QA_REPORTES"; mkdir -p "$QA_REPORTES"
INICIO=$(date +%s); <script del peldaño N> <feature>; echo "exit $?"
```

Falla si el script no termina, termina en rojo o no deja JUnit en `$QA_REPORTES`. Nunca reutilices reportes de otra ejecución o de otra feature.

**G4 · Trazabilidad** (todos):

```bash
python3 <qa-core>/scripts/trazabilidad.py --criterios .scratch/<feature>/qa/criterios.md \
  --escenarios .scratch/<feature>/qa/escenarios.md --fuentes <Aceptación>/<feature> \
  --junit <los XML de los QA_REPORTES de esta verificación> --desde <INICIO de la primera corrida> \
  --peldanos <los disponibles del ritmo> [--ids <Escenarios: del ticket, en por-rebanada>]
```

Falla con cualquier hueco: criterio sin escenario ejecutable, escenario sin implementar, no ejecutado, saltado, rojo, huérfano, caso con varios IDs, reporte anterior a la corrida o **criterio sin evidencia en el alcance** (sus escenarios están solo en peldaños no disponibles: ese criterio queda sin verificar y así se reporta, nunca como verde). Un alcance vacío es error.

**G5 · Estabilidad** (completo y post-deploy): ejecuta **otra vez el script completo** del peldaño 1 (o del 4 en post-deploy), con un `QA_REPORTES` nuevo, y compara escenario por escenario. Un escenario cuyo resultado cambia entre corridas es **flaky** y cuenta como rojo: un verde intermitente no es verde. (No se reejecutan escenarios sueltos: eso exigiría filtrar.)

**G6 · Contratos y fakes** (completo): el peldaño 2. Falla si la verificación Pact o algún learning test está en rojo, si un contrato no tiene verificación verde en los últimos 30 días o desde el último cambio del proveedor, o si un fake de `fakes/GRABACION.md` tiene más de 30 días o es anterior al último cambio conocido del tercero.

**G7 · Fuzzing de contrato** (completo, si hay OpenAPI): Schemathesis contra el peldaño 1. Falla con 5xx o respuestas fuera del esquema.

**G8 · Mutantes** (completo): el último informe de `qa-test-the-tests`. Compara su huella con la actual (`python3 <qa-core>/scripts/mutantes.py huella`): si el HEAD o los cambios difieren, el informe es de otro código y la puerta falla. También falla si no existe (obligatorio en modo solo) o si hay sobrevivientes sin cerrar ni justificar.

**G9 · Señales de special-casing** (completo; aviso, no puerta): busca en el diff de producción referencias a la carpeta de aceptación, a IDs `ESC-`, a variables `QA_` o a valores literales de los datos de prueba. Cada coincidencia va al informe para revisión humana. No lo detecta todo: es una ayuda para la revisión de código, no un sustituto.

Un peldaño marcado `no disponible` no es un fallo de ejecución, pero sus escenarios van a "No ejecutado y por qué" y los criterios que dependen solo de él dejan G4 en rojo.

## 2. Clasifica cada fallo y bájalo de peldaño

Cada escenario rojo o flaky se convierte en un hallazgo con una **clase**. La clase decide quién actúa; clasificar mal manda el arreglo a la persona equivocada (y "arreglar el test" cuando el defecto es del código es exactamente la trampa que este plugin existe para impedir).

Procedimiento completo en [references/clasificacion-y-push-down.md](references/clasificacion-y-push-down.md). En resumen:

| Clase | Significado | Va a |
|---|---|---|
| **código** | El test refleja el criterio, el sistema no lo cumple y se reproduce en el peldaño 1 (también un flaky que se reproduce en el peldaño 1: suele ser una carrera) | Dev, como entrada de `diagnosing-bugs` |
| **configuración** | Falla en 3 o 4 pero no en 1: depende de configuración, despliegue, secretos o red | Dev o plataforma |
| **spec** | El test refleja la spec, pero la spec contradice la realidad (un tercero, un consumidor) o es ambigua | Humano dueño de la spec → `qa-acceptance-criteria` |
| **test** | El test no refleja el criterio aprobado | QA: corrige y re-sella citando el hallazgo |
| **entorno** | Intermitente solo en ambientes compartidos y estable en el peldaño 1; ambiente caído | Registro y deuda; nunca se cierra como "pasó al reintentar" |
| **indeterminada** | Las preguntas del procedimiento no alcanzan para decidir | Humano |

**Baja de peldaño** (push the test down) antes de entregar un hallazgo: reproduce el fallo en el peldaño más bajo que puedas. Desde el peldaño 1 hacia abajo (integración y unitario) baja el dev, con `diagnosing-bugs`: el QA no ve el código.

## 3. Escribe el informe

Escribe `.scratch/<feature>/qa/verificaciones/<fecha>-<ritmo>.md` con el formato de la sección 7 de formatos.md:

1. Encabezado: modo, barrera de información **real** (la declarada), huella (`mutantes.py huella`) y carpetas de reportes de esta verificación.
2. Tabla de puertas con la salida resumida de cada script.
3. **Sellados y re-sellados desde la rama base**, con su motivo.
4. Estado por criterio.
5. Hallazgos (formato de la sección 5), ordenados por severidad.
6. **No ejecutado y por qué**: peldaños no disponibles, escenarios bloqueados por testabilidad, criterios sin evidencia en el alcance, riesgos que el sandbox no reproduce, señales de G9.

Redacta secretos en toda la evidencia (`<REDACTED>`).

## 4. Entrega

- Muestra al usuario las puertas, los re-sellados desde la base y los hallazgos blocker y major. Nada más arriba.
- **Nunca** escribas "aprobado", "listo", "certificado" ni "puede ir a producción". Si todas las puertas están en verde, dilo así: "todas las puertas del ritmo <ritmo> en verde; queda por decidir: <lo no ejecutado y los re-sellados a revisar>".
- Hallazgos de clase código o configuración: ofrece pasarlos a `diagnosing-bugs`, con el comando de reproducción como feedback loop.
- Hallazgos de clase spec: vuelven a `qa-acceptance-criteria`.
- Hallazgos de clase test: los corrige el rol QA y vuelve a sellar con `--motivo "H-NN: …"`.
