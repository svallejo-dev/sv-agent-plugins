# Evals del plugin qa

Casos para medir si el plugin cambia el comportamiento del agente donde importa: oráculos independientes, resistencia a la trampa y clasificación honesta. Cada caso tiene un `prompt.md` (lo que recibe el agente, con los archivos que debe crear en un repo de prueba) y un `grader.md` (criterios PASS/FAIL para un juez).

## Método

1. **Calibra al juez**: para cada caso, dale una respuesta fuerte y una deliberadamente mala. Si no las separa, el juez no sirve.
2. **Con y sin plugin**: el mismo modelo, con `qa` (y `ingenieria`) instalados y sin ellos.
3. **n = 3** por configuración; reporta media y dispersión.
4. **Comprueba la composición**: que las skills se invocaron (sub-agentes lanzados, scripts ejecutados, archivos con el formato parseable). Un resultado correcto obtenido sin el proceso no cuenta como éxito del plugin.
5. **Reporta dónde gana el baseline.** Un eval que siempre favorece al plugin no mide nada.

| Caso | Qué mide |
|---|---|
| 01 token: variante del tercero | El caso real del BFF de PayPal: ¿el diseño de escenarios descubre la variante equivocada y la clave de caché antes de implementar? |
| 02 tentación de editar un test | Con un test de aceptación sellado en rojo que parece incorrecto, ¿el agente dev escala en vez de editarlo? |
| 03 clasificación de fallos | ¿`verify` clasifica bien código, configuración, spec, test y entorno, y no cierra un flaky como verde? |
| 04 mutante sobreviviente | ¿El triage describe el hueco en términos de comportamiento y lo devuelve a diseño, sin filtrar el código al QA? |
| 05 handoff incompleto | ¿`test-design` se niega a diseñar e identifica qué falta, en vez de inventar? |
| 06 criterios débiles | ¿`acceptance-criteria` reescribe criterios de forma en criterios de uso y hace explícitos los implícitos? |

El caso 01 es el más importante: si el plugin no detecta ahí el bug que motivó su diseño, no sirve todavía.
