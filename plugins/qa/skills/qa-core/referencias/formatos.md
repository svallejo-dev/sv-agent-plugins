# Formatos de los artefactos de QA

Referencia compartida. Los formatos de criterios y escenarios los leen los scripts de `scripts/`, así que **sus partes marcadas como "parseable" no son opcionales**: un ID mal escrito rompe la trazabilidad.

Todos viven en `<Tracker>/<feature>/qa/` (`.scratch/` por defecto; la clave `Tracker:` de `docs/agentes/qa.md` manda). En este documento y en las skills se escribe `.scratch/` por brevedad.

## Identificadores

| Prefijo | Qué identifica | Ejemplo |
|---|---|---|
| `AC-NN` | Criterio de aceptación | `AC-03` |
| `ESC-NN` | Escenario | `ESC-12` |
| `H-NN` | Hallazgo | `H-04` |
| `E-NN` | Escalamiento | `E-02` |
| `M-NN` | Mutante | `M-07` |

Dos dígitos mínimo (`AC-1` es inválido y los scripts lo rechazan), numeración por feature, nunca se reutiliza un ID descartado: se marca `descartado`.

## 1. Contrato de handoff (`handoff.md`)

Lo escribe el dev, lo acepta o devuelve el QA. `qa-test-design` se niega a empezar si falta una pieza obligatoria.

```markdown
# Handoff: <feature>

Estado: borrador | aceptado | devuelto
Spec: ../spec.md

## 1. Superficie (obligatorio)
Contrato de API: <ruta a OpenAPI / AsyncAPI / proto> o, si no existe, la lista de endpoints y eventos con su forma.

## 2. Consumidores del resultado (obligatorio)
| Consumidor | Qué consume | Cómo valida que le sirve (oráculo de uso) |
|---|---|---|

## 3. Dependencias (obligatorio)
| Dependencia | Propia / tercero | Sandbox o entorno de prueba | Documentación oficial |
|---|---|---|---|

## 4. Artefacto ejecutable (obligatorio: al menos uno)
- Imagen o comando de arranque: <cómo levantar el servicio y con qué variables>
- URLs por ambiente: <dev, staging…> (sin secretos)

## 5. Seams de testabilidad (obligatorio responder cada uno)
| Seam | Estado | Cómo se usa |
|---|---|---|
| Siembra de datos por API o endpoint de setup no productivo | disponible / no / no aplica | |
| Reloj controlable | | |
| Dependencias configurables por variable (para fakes y Toxiproxy) | | |
| Aislamiento de datos (tenant o cuentas de prueba) y limpieza | | |
| Observabilidad accesible (trace-id o correlation-id en respuestas y logs) | | |

## 6. Restricciones
PCI, datos reales prohibidos, rate limits del sandbox, ventanas de uso de ambientes.
```

Un seam en estado `no` no bloquea el handoff: produce escenarios `bloqueado-testabilidad` y una deuda explícita.

## 2. Criterios de aceptación (`criterios.md`) — parseable

```markdown
# Criterios de aceptación: <feature>

Estado: borrador | aprobado
Modo: solo | duo
Spec: ../spec.md

## AC-01: <título corto en lenguaje de negocio>
- Comportamiento: <qué se observa desde fuera, en una frase; sin detalles de implementación>
- Oráculo: <quién o qué decide que se cumple; si el resultado lo consume otro, el consumidor>
- Fuente: <sección o historia de la spec; "inferido" si no está en la spec, y entonces requiere confirmación>
- Tipo: funcional | fallo | seguridad | contrato | rendimiento
- Prioridad: crítica | alta | media
- Estado: descartado        (solo si se descarta; con el motivo en la línea siguiente)
```

**Parseable:** cada criterio empieza con un encabezado `## AC-NN:` (nivel 2 o 3). Los scripts reconocen los criterios solo por ese encabezado (los que están dentro de bloques de código no cuentan). Un criterio con la línea `- Estado: descartado` deja de exigir escenarios, y ningún escenario activo puede referenciarlo.

## 3. Escenarios (`escenarios.md`) — parseable

```markdown
# Escenarios: <feature>

Estado: borrador | aprobado
Criterios: ./criterios.md

| ID | Criterio | Técnica | Peldaño | Escenario | Oráculo | Estado |
|---|---|---|---|---|---|---|
| ESC-01 | AC-01 | límites | 1, 4 | Dado un cliente con 4 dispositivos, cuando registra uno, entonces 201 | respuesta + listado | activo |
| ESC-02 | AC-01, AC-04 | tabla de decisión | 3 | … | SDK inicializado en sandbox | activo |
| ESC-03 | AC-02 | fallo de dependencia | 1 | … | … | bloqueado-testabilidad |
| ESC-04 | AC-02 | límites | 1 | … (podado por riesgo: cubierto por ESC-01) | … | descartado |
```

**Parseable:**
- La tabla debe tener en su encabezado las columnas `ID`, `Criterio`, `Peldaño` y `Estado` (en cualquier orden; puede haber más columnas).
- `Criterio` admite varios IDs separados por coma.
- `Peldaño` es uno o varios números de la escalera (1 a 5), separados por coma: `1, 4` significa que el mismo escenario corre en el peldaño hermético y como smoke en staging, con el mismo ID.
- `Estado`: `activo`, `bloqueado-testabilidad` o `descartado`. Los podados por riesgo van en la misma tabla como `descartado`, con el motivo en la columna Escenario.
- Puede haber varias tablas (por ejemplo una por criterio); toda tabla con columna `ID` se interpreta como tabla de escenarios y debe cumplir este formato.
- Para escribir `|` dentro de una celda, escápalo: `\|`.

Debajo de la tabla, el detalle de cada escenario que lo necesite (datos exactos, pasos, por qué ese peldaño), con el encabezado `### ESC-NN`.

## 4. Convención de trazabilidad en los tests ejecutables — parseable

Cada test de aceptación lleva el ID de **un solo** escenario **en el nombre que aparece en el reporte JUnit**. Un caso JUnit con dos IDs es un hueco: un test, un escenario. En las fuentes, el ID solo cuenta si está en el **título del test** o en el **nombre del archivo**; un comentario que dice "cubre ESC-03" no implementa nada.

| Herramienta | Dónde va el ID |
|---|---|
| Gherkin (godog, Cucumber, Karate) | En el título: `Escenario: ESC-04 límite de dispositivos` (en un esquema, cada fila hereda el ID) |
| Hurl | En el nombre del archivo: `ESC-07-idempotencia.hurl` |
| Playwright | En el título del test: `test('ESC-09 SDK se inicializa con el token', …)` |
| Go (`testing`) | En el subtest: `t.Run("ESC-11 timeout del proveedor", …)` (en el JUnit aparece como `ESC-11_timeout…`; el script lo reconoce) |

Un test sin ID es un test que nadie puede trazar hasta un criterio: `scripts/trazabilidad.py` lo reporta.

## 5. Hallazgo

Lo emite `qa-verify`. Va en el informe de verificación y, si es de clase código o configuración, también se pasa al dev.

```markdown
### H-03: <síntoma en una frase>
- Escenario: ESC-07 · Criterio: AC-02 · Severidad: blocker | major | minor
- Clase: código | configuración | spec | test | entorno | indeterminada (ver qa-verify)
- Peldaño donde falló: 4 · Peldaño más bajo donde se reproduce: 1
- Reproducción: `<comando exacto>`
- Esperado: <…>
- Observado: <…>
- Evidencia: <request y response redactados, trace-id, líneas de log relevantes>
- Hipótesis de comportamiento: <opcional; sobre el comportamiento observable, nunca sobre el código que el QA no vio>
- Estado: abierto | en-curso | resuelto | descartado
```

## 6. Escalamiento (`escalamientos.md`)

```markdown
## E-02: ESC-05 parece contradecir la spec
- Fecha: 2026-11-08 · Abre: dev · Escenario: ESC-05 · Criterio: AC-03
- Argumento: <por qué el dev cree que el test está mal>
- Evidencia: <spec §, respuesta del tercero, doc oficial>
- Decisión: pendiente | test-corregido | spec-corregida | rechazado
- Resuelve: <QA o humano> · Motivo: <…>
```

Este archivo no prueba quién decidió: cualquiera puede escribir "Resuelve: humano". La atribución real es la autoría del commit y la revisión del PR, donde `qa-verify` lista cada re-sellado desde la rama base.

## 7. Informe de verificación (`verificaciones/<fecha>-<ritmo>.md`)

```markdown
# Verificación: <feature> · ritmo <por-rebanada | completo | post-deploy> · <fecha>

Modo: solo | duo · Barrera: N1 | N2 | N3 · Huella: HEAD <sha> + cambios <sha> · Ejecución: <Reportes>/<feature>/<id>/

## Puertas
| Puerta | Estado | Evidencia |
|---|---|---|
| Sello íntegro | ok / roto | salida de sello.py |
| Trazabilidad completa | ok / huecos | salida de trazabilidad.py |
| Escenarios del ritmo en verde | N/M | reportes JUnit |
| … | | |

## Criterios
| Criterio | Escenarios | Estado |
|---|---|---|

## Hallazgos
<H-NN…>

## No ejecutado y por qué
<peldaños no disponibles, bloqueados por testabilidad>
```

El informe **no** contiene la palabra "aprobado" ni equivalentes. Termina con las puertas y lo que falta; el humano decide.
