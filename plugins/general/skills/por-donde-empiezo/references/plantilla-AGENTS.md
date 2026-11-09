# Reglas para agentes

Este repositorio usa los plugins de [sv-agent-plugins](https://github.com/svallejo-dev/sv-agent-plugins). Las skills se nombran aquí por su nombre a secas (`tdd`); en Claude Code llevan el prefijo del plugin (`ingenieria:tdd`, `qa:qa-verify`).

## Idioma

Responde en español y conserva en inglés los términos técnicos habituales. Explica los conceptos nuevos con su nombre canónico y una analogía.

## Por dónde empezar

Si no está claro qué hacer, usa la skill `por-donde-empiezo`. Antes de afirmar qué hace una skill, lee su `SKILL.md`.

Una vez por repo: `ingenieria-setup` y, si hay QA, `qa-setup`. Sus decisiones viven en `docs/agentes/`; léelas antes de trabajar.

## Flujos

- **Feature**: `grill-with-docs` → `to-spec` → (QA: `qa-acceptance-criteria` → `qa-test-design` → `qa-test-automation`) → `to-tickets` → por ticket `tdd` + `qa-verify` por rebanada → `go-simplify` → `code-review` → `qa-test-the-tests` + `qa-verify` completo → `git-commit` → `create-pr`.
- **Bug**: `diagnosing-bugs`. Primero un comando que reproduzca el fallo en rojo; después el arreglo, con un test de regresión.
- **Sistema o migración**: `system-design` (con `capacity-estimation`, `design-stress-test` y `strategic-design`) → `to-spec`.
- **PoC**: `system-design` en modo PoC → construir hipótesis por hipótesis desde el plan del experimento (sin `to-spec` ni `to-tickets`) → veredicto con medición por hipótesis → `system-design` en modo producción.
- **Integración con un tercero**: la spec declara los consumidores del resultado; el primer ticket es el walking skeleton con el consumidor real; learning tests contra el sandbox antes de escribir fakes.

## Reglas

### Trabajo y trazabilidad

- Specs y tickets viven en el tracker de `docs/agentes/tracker.md` (por defecto `.scratch/<feature>/`). Un ticket está bloqueado mientras su línea `Bloqueado por:` tenga tickets abiertos.
- Los términos del dominio son los de `GLOSARIO.md`; las decisiones difíciles de revertir van como ADR en `docs/adr/`.
- No hagas commit, push, merge ni nada irreversible sin que el usuario lo pida. Nunca: secretos en commits, `--no-verify`, force-push a ramas compartidas, merge de PRs.

### Desarrollo

- `tdd` es el lazo interno del dev: un comportamiento por ciclo, test en rojo antes del código, en el seam acordado.
- `code-review` entrega hallazgos con severidad; **nunca aprueba**.
- Lo específico de cada lenguaje lo aportan las skills `<lenguaje>-review`, `<lenguaje>-testing`, `<lenguaje>-debugging` y `<lenguaje>-design`.
- En Go: idiomas y comentarios según `senior-go-idiomatic`; `go-simplify` antes del PR, sin cambiar comportamiento ni API exportada.

### QA (si el repo usa `qa`)

- **El agente que implementa nunca escribe ni edita el oráculo**: criterios, escenarios, tests de aceptación, scripts de peldaño, `docs/agentes/qa.md` ni el sello. Si un test de aceptación parece incorrecto, registra un escalamiento en `.scratch/<feature>/qa/escalamientos.md` y sigue con otro escenario.
- **Ningún agente certifica.** `qa-verify` entrega puertas y hallazgos; un ticket no está terminado mientras sus escenarios no estén en verde con el sello íntegro, y la decisión de entregar es humana.
- Un test saltado, no ejecutado o intermitente no es un test en verde.
- Datos de prueba aleatorios y sin marcas; el código de producción nunca reconoce datos, IDs (`ESC-NN`) ni rutas de los tests.
- Si otro sistema consume lo que produces (un token, un evento, un archivo), se verifica con ese consumidor real, no con la forma del artefacto.

### Arquitectura (si el repo usa `arquitectura`)

- Se diseña como delta: estado actual → objetivo → migración. No tener métricas nunca bloquea: se trabaja con escenarios por orden de magnitud y el arquetipo del negocio.
- Toda decisión lleva `Decisión | Resuelve | Empeora | Cámbiala cuando…`, con un disparador medible.
- Los números se calculan con `capacity-estimation` (en código), no de memoria.

## Al terminar una fase

Antes de limpiar o compactar el contexto, recorre las preguntas de la sección "Al terminar una fase" de `por-donde-empiezo`: seguir, limpiar, traspasar (`handoff`), delegar o compactar, en ese orden.
