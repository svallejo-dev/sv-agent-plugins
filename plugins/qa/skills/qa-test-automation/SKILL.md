---
name: qa-test-automation
description: "Implementa como tests ejecutables los escenarios aprobados, con herramientas existentes (Gherkin con godog, Hurl, Testcontainers, Toxiproxy, WireMock, Pact, Schemathesis, Playwright) y la plomería generada por IA; primero los learning tests de terceros, después los escenarios, y comprueba que cada test falla por la razón correcta y es determinista antes de sellar. Úsala cuando el usuario pida \"automatizar las pruebas\", \"implementar los escenarios\", \"tests de aceptación\", \"tests e2e\", \"learning tests\" o después de qa-test-design."
license: MIT
---

# Automatización de pruebas

Responde en español y conserva en inglés los términos técnicos habituales.

Convierte escenarios aprobados en tests que una máquina ejecuta igual mil veces. La plomería (pasos de godog, harness de Testcontainers, fakes) la genera la IA y el humano no la lee línea por línea; por eso esta skill exige **pruebas deterministas sobre los propios tests** antes de sellarlos: que fallen por la razón correcta, que no sean flaky y que no importen código de producción.

**Analogía:** construir el banco de pruebas de un motor. No importa en qué lenguaje se atornilló el banco; importa que mida lo que dice medir, que dé la misma lectura dos veces seguidas y que no esté conectado al motor por un cable que lo haga marcar lo que el motor quiere.

Lee primero [../qa-core/referencias/modelo-de-roles.md](../qa-core/referencias/modelo-de-roles.md), [../qa-core/referencias/escalera-de-ambientes.md](../qa-core/referencias/escalera-de-ambientes.md) y [../qa-core/referencias/formatos.md](../qa-core/referencias/formatos.md) (sección 4, convención de IDs).

## 0. Precondiciones

1. `docs/agentes/qa.md` existe; si no, pide ejecutar la skill `qa-setup` y para. Ejecuta los scripts desde la raíz del repositorio. `<qa-core>` es la carpeta de la skill `qa-core`, hermana de esta; `<Aceptación>` y `<Reportes>` salen de `docs/agentes/qa.md`.
2. `escenarios.md` tiene `Estado: aprobado`.
3. El sello del diseño está íntegro:
   ```bash
   python3 <qa-core>/scripts/sello.py verificar --sello <Aceptación>/<feature>/.qa-sello.json \
     --requiere .scratch/<feature>/qa/criterios.md .scratch/<feature>/qa/escenarios.md docs/agentes/qa.md
   ```
   Si está roto, para: alguien cambió el diseño o la configuración después de aprobarlos.
4. **Regla de contaminación**: los tests de aceptación los escribe el rol QA. Si esta sesión implementó código de la feature, delega la automatización a un sub-agente con contexto limpio; su brief incluye los escenarios, el handoff, los contratos de API, esta skill y la prohibición de leer código de producción. (Es de buena fe; ver modelo-de-roles.)
5. Lenguaje de la plomería: el del repo, salvo que `docs/agentes/qa.md` diga otro. Si existe `<lenguaje>-testing` (por ejemplo `go-testing`), invócala para sus idiomas. Que el humano no domine ese lenguaje no es un problema: no va a leer la plomería, va a leer Gherkin y Hurl.

## 1. Los scripts de peldaño y el harness

Si `docs/agentes/qa.md` dice `por construir` en algún peldaño disponible, crea su script en `<Aceptación>/bin/` cumpliendo el **contrato de los scripts de peldaño** de `qa-setup` (JUnit solo en `$QA_REPORTES`, nada escrito dentro de `<Aceptación>/`, sin argumentos que filtren, imagen con `$QA_IMAGEN_TAG`). Requisitos del harness:

- **Parametrizado por ambiente**: `base_url` y dependencias por variables; ningún valor de ambiente escrito en los tests.
- **Peldaño 1**: levanta la **imagen del servicio** (no el código fuente) con sus dependencias en Testcontainers, cada dependencia detrás de Toxiproxy, y los terceros como fakes WireMock.
- **Caja negra comprobable**: en Go, los tests de aceptación son un módulo propio (`<Aceptación>/go.mod`), así el compilador impide importar paquetes `internal/` de producción.

Recetas en [references/herramientas.md](references/herramientas.md); estructura y reglas de datos en [references/harness.md](references/harness.md).

## 2. Learning tests primero (si hay terceros)

Antes de escribir un solo escenario que dependa de un tercero:

1. Por cada suposición sobre el tercero que usan los escenarios (qué variante devuelve, con qué forma, qué errores), escribe un learning test contra su **sandbox**, en `aprendizaje/`.
2. Ejecútalos. **Si un learning test contradice un escenario o un criterio, para**: es un hallazgo de clase **spec**, no un detalle de implementación. Regístralo y vuelve a `qa-acceptance-criteria`. Así se habría detectado el caso del token de PayPal antes de escribir el BFF.
3. Graba sus respuestas como fakes con el **modo de grabación de WireMock**, **redactando secretos**, y añade a mano las variantes que el sandbox no deja provocar (5xx, 429, timeouts). Los fakes del peldaño 1 nacen de la realidad, no de la creencia.
4. Registra la fecha de grabación de cada fake en `fakes/GRABACION.md`: un fake viejo es sospechoso, y `qa-verify` lo reporta en el ritmo completo.

Pact es para servicios propios, no para terceros: ver [references/pact-modos.md](references/pact-modos.md).

## 3. Implementa los escenarios

Elige la herramienta por escenario con la guía de `qa-toolbox`. Reglas que no se negocian:

1. **Un ID por test, en el título o en el nombre del archivo** (convención de formatos.md). Un test sin ID no existe para la trazabilidad; un test con dos IDs es un hueco.
2. **Caja negra**: los tests hablan con el sistema solo por su superficie pública (HTTP, eventos, UI) y por los seams de testabilidad declarados en el handoff. Ningún import de paquetes de producción.
3. **Datos propios, aleatorios y sin marcas**: cada escenario crea sus datos por la API o por el seam de siembra, con valores generados en cada ejecución y **sin prefijos ni patrones reconocibles** (nada de `qa-`, `test-`, IDs fijos). Unos datos reconocibles permiten que el código de producción los detecte y responda lo que el test espera (special-casing).
4. **Sin esperas fijas**: nada de `sleep`. Sondea con timeout (la opción `retry` de Hurl, `Eventually` en Go, `expect.poll` en Playwright).
5. **El oráculo del escenario, completo**: si el escenario dice "409 y el cliente sigue con 5 dispositivos", el test verifica ambas cosas.
6. **Nada de saltos**: ningún `skip`, `@ignore`, `.only` ni tag que excluya escenarios. Un escenario bloqueado está bloqueado en `escenarios.md`, no saltado en el código.
7. **El consumidor real lo controla el QA**: en el walking skeleton, la página o el cliente mínimo que usa el SDK lo escribe el QA dentro de `<Aceptación>/<feature>/` y lo sirve el harness. Si lo sirviera el servicio bajo prueba, el dev controlaría el oráculo.

## 4. Prueba los tests antes de sellarlos

Ejecuta los scripts de peldaño con un directorio de reportes nuevo para cada corrida:

```bash
export QA_REPORTES=<Reportes>/<feature>/$(date +%Y%m%dT%H%M%S); mkdir -p "$QA_REPORTES"; INICIO=$(date +%s)
<Aceptación>/bin/peldano-1.sh <feature>
```

Tres comprobaciones deterministas. Ninguna es opcional.

**a) Rojo por la razón correcta** (normalmente la feature aún no está implementada):

```bash
python3 <qa-core>/scripts/trazabilidad.py --criterios .scratch/<feature>/qa/criterios.md \
  --escenarios .scratch/<feature>/qa/escenarios.md --fuentes <Aceptación>/<feature> \
  --junit "$QA_REPORTES"/*.xml --desde "$INICIO" --peldanos 1 --esperar-rojo
```

El script exige que cada escenario esté implementado y ejecutado; el rojo es lo esperado y avisa de cada **verde antes de implementar**. Después revisa la causa de cada rojo:

| Resultado | Significado | Acción |
|---|---|---|
| Rojo por aserción de comportamiento (404, 501, valor esperado distinto) | Correcto: el test detecta la ausencia del comportamiento | Ninguna |
| Rojo por error del harness (conexión rechazada, fixture rota, compilación, timeout del setup) | El test no prueba nada todavía | Arregla el harness y repite |
| **Verde antes de implementar** | O el comportamiento ya existía, o **el test es vacuo** (aserción que no puede fallar) | Investiga. Si ya existía, documéntalo en el escenario; si es vacuo, reescríbelo |

**b) Determinismo.** Ejecuta la suite tres veces seguidas sobre el mismo estado, cada vez con un `QA_REPORTES` nuevo. Cualquier escenario cuyo resultado cambie entre corridas es flaky y **no se sella**: arregla la causa (datos compartidos, orden, esperas, reloj).

**c) Caja negra.** Ejecuta la comprobación declarada en `docs/agentes/qa.md` y verifica su código de salida.

## 5. Revisión humana y sello

1. El humano revisa los artefactos **legibles**: los `.feature` y los `.hurl`, contrastándolos con los escenarios. No revisa la plomería; su garantía son las comprobaciones del paso 4.
2. Con la aprobación, amplía el sello a los tests y a los scripts de peldaño:
   ```bash
   python3 <qa-core>/scripts/sello.py resellar --sello <Aceptación>/<feature>/.qa-sello.json \
     --motivo "tests de aceptación implementados y revisados" <Aceptación>/<feature> <Aceptación>/bin
   ```
3. Dile al dev que los tests de aceptación son de **solo lectura** para él: los ejecuta por rebanada y, si cree que uno está mal, escala (`escalamientos.md`), nunca edita.

Siguiente paso: el dev implementa con `tdd`; la verificación se hace con `qa-verify`.
