# Evals del plugin arquitectura

Casos para la prueba de concepto. Cada caso tiene un `prompt.md` (lo que recibe el agente) y un `grader.md` (criterios PASS/FAIL que aplica un juez).

## Método (tomado de proyecto26/system-design-skills, adaptado)

1. **Calibra al juez** antes de nada: dale una respuesta fuerte y una deliberadamente mala para un mismo caso. Si no las separa con claridad, el juez no sirve.
2. **Con y sin skills**: ejecuta cada caso con el plugin `arquitectura` instalado y sin él (baseline), con el mismo modelo.
3. **n = 3** ejecuciones por configuración; reporta media y desviación, no un solo resultado.
4. **Comprueba la composición**: que las skills se invocaron de verdad (por ejemplo, que la capacidad salió del script y no de cabeza).
5. Reporta también dónde ganó el baseline. Un eval que siempre da la razón a las skills no mide nada.

| Caso | Qué mide |
|---|---|
| 01 trampa de sobre-descomposición | YAGNI: no proponer microservicios + Kafka a una escala diminuta |
| 02 migración de legacy | Paso 0, diseño como delta, camino de migración con puertas, legacy como oráculo |
| 03 capacidad medida | Cálculo correcto desde métricas (Little, utilización), con el script |
| 04 brownout de dependencia | Amplificación de reintentos, agotamiento de pools, estado metaestable, detección |
| 05 integración con partner legacy | Diseño estratégico: ACL vs Conformist, Published Language, transición |
| 06 exploratorio sin métricas | Diseñar sin datos desde el arquetipo: invariantes primero, escenarios y umbrales, plan de PoC |
