---
name: qa-toolbox
description: "Radar de herramientas de QA (adoptar, probar, evaluar, retener) y guía para elegir la herramienta de cada escenario según el peldaño, el artefacto que revisa el humano y el determinismo del ejecutor. Úsala cuando el usuario pregunte \"¿qué herramienta uso para…?\", \"¿Karate o Hurl?\", \"¿cómo pruebo X?\", o cuando qa-test-automation tenga que elegir herramienta para un escenario."
license: MIT
---

# Toolbox de QA

Responde en español y conserva en inglés los términos técnicos habituales.

Elegir herramienta es elegir qué artefacto revisará el humano y qué tan confiable es quien ejecuta. **No se reinventan librerías**: para cada necesidad hay una herramienta madura; el trabajo del agente es elegirla bien y escribir la plomería.

**Analogía:** una caja de herramientas de carpintero. No fabricas un martillo cada vez que clavas; eliges el martillo, el mazo o la pistola de clavos según la madera, y lo que importa es el mueble.

## Criterios de selección

Con agentes escribiendo la plomería, que el humano conozca el lenguaje deja de importar. Importan:

1. **Legibilidad del artefacto que aprueba el humano**: Gherkin y Hurl se leen sin programar; un test en Go no.
2. **Determinismo del ejecutor**: mismo estado, mismo resultado; sin esperas fijas ni dependencias del orden.
3. **Peldaño**: dónde puede correr (ver [../qa-core/referencias/escalera-de-ambientes.md](../qa-core/referencias/escalera-de-ambientes.md)).
4. **Qué necesita**: ¿la imagen?, ¿controlar la red?, ¿el código? (Solo el dev usa herramientas que necesitan el código.)
5. **Que produzca JUnit**: sin reporte trazable, `qa-verify` no puede contar.

## Elección por necesidad

| Necesidad | Herramienta | Peldaño |
|---|---|---|
| Regla de negocio legible por el negocio, con tablas de ejemplos | Gherkin + godog (Go), Cucumber (JVM o JS), behave (Python) | 1 |
| Flujo HTTP de varias peticiones, smoke de staging | Hurl | 1, 3, 4 |
| Dependencias reales desechables (base, cola, cache) | Testcontainers | 1 |
| Fallos de red y de dependencias | Toxiproxy | 1 |
| Terceros: fakes grabados de la realidad, errores provocados | WireMock (grabación y reproducción) | 1 |
| Comportamiento real del tercero | Learning tests (Hurl o el lenguaje del harness) contra el sandbox | 2 |
| Compatibilidad entre servicios propios | Pact (modos A, B o D) | 2 |
| Entradas que nadie escribiría, desde el OpenAPI | Schemathesis | 1, ritmo completo |
| UI, SDK de navegador, walking skeleton con consumidor web | Playwright | 3, 4 |
| Combinatoria de parámetros | PICT (pairwise) para generar los ejemplos | diseño |
| Mutación al nivel de aceptación | `scripts/mutantes.py` + mutantes semánticos | 1 |
| Integridad y trazabilidad del oráculo | `scripts/sello.py`, `scripts/trazabilidad.py` | todos |
| Mutación al nivel unitario (dev) | Gremlins (Go) | 0 |
| Propiedades e invariantes (dev) | rapid (Go), `go test -fuzz` | 0 |
| Carga | k6 | dedicado |

Recetas de uso en [../test-automation/references/herramientas.md](../qa-test-automation/references/herramientas.md).

## Radar (noviembre de 2026)

Las herramientas cambian rápido: antes de adoptar algo de este radar, verifica su estado actual (versión, mantenimiento, cambios de CLI).

### Adoptar
- **Gherkin** como artefacto de aprobación humana de reglas de negocio.
- **Hurl**: flujos HTTP en texto, independiente del lenguaje, JUnit nativo.
- **Testcontainers** (Go y otros lenguajes): el peldaño 1.
- **WireMock**: fakes de terceros grabados y redactados.
- **rapid** y **`go test -fuzz`** en el lazo interno del dev (Go).

### Probar
- **godog**: el ejecutor de Gherkin en Go; la plomería la escribe el agente.
- **Toxiproxy**: fallos de red en el peldaño 1.
- **Pact Go v2**: entre servicios propios, en el modo A sin broker; D cuando haya permisos.
- **Schemathesis**: fuzzing de contrato en el ritmo completo.
- **Playwright**: walking skeleton con SDK de navegador y UI.
- **k6**: carga, fuera de la suite funcional.
- **Gremlins**: mutación unitaria en Go.

### Evaluar
- **Agentes de Playwright** (planner, generator, healer): útiles para crear y mantener tests de UI, con una regla: el healer solo toca selectores, nunca aserciones.
- **Karate**: alternativa a godog + Hurl si el QA prefiere un único DSL para API, mocks y performance; requiere JVM (Java 21 en su versión 2).
- **Ooze** (mutación en Go): alternativa a Gremlins.

### Retener (no usar en suites nuevas)
- `testing/quick` de Go: congelado; usa rapid.
- Forks sin mantenimiento de go-mutesting.
- **Postman** y similares como **fuente de verdad** de los tests: su formato no se revisa bien en un diff y ata la suite a una GUI. (Exportar una colección a Hurl o usarla para explorar es otra cosa.)
- **Selenium** para suites nuevas: Playwright cubre el caso con mejor determinismo (auto-wait).

## Cuándo no usar una herramienta

- **Toxiproxy en staging compartido**: rompes a otros equipos.
- **Hurl para lógica compleja de preparación**: si un escenario necesita más de tres llamadas de siembra o lógica condicional, la plomería va en el harness o en pasos de godog.
- **Pact contra un tercero**: no ejecutará tu contrato y su sandbox no expone estados. Usa learning tests + WireMock; si publica OpenAPI, el contract testing bidireccional es un complemento.
- **Mocks escritos a mano de un tercero**, sin learning test que los respalde: un mock que solo sabe lo que creías es la causa del caso del token de PayPal.
