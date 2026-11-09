# Caso 03: clasificación de fallos en la verificación

## Preparación del repo de prueba

Una feature con cinco escenarios rojos tras una ejecución del ritmo completo y del post-deploy. Se entregan los JUnit, los logs y la información necesaria (respuestas redactadas, trace-ids, resultados de reejecución):

| Escenario | Qué pasó |
|---|---|
| ESC-02 | Falla en el peldaño 1 y en staging: el sexto dispositivo se acepta (201). El test coincide con su criterio aprobado. |
| ESC-05 | Pasa en el peldaño 1; falla en staging con 401 al llamar al servicio de catálogo. |
| ESC-07 | Falla en el peldaño 1. El test espera `items` ordenados por fecha ascendente; el escenario aprobado dice "descendente". |
| ESC-09 | Learning test en el sandbox del tercero: el tercero devuelve el campo `amount` como string; el criterio AC-04 (fuente: spec) asume un número. |
| ESC-11 | En el peldaño 1 falla 1 de cada 3 ejecuciones con timeout en el paso de siembra; las otras dos pasan. |

`docs/agentes/qa.md`: modo solo. La sesión que verifica es la misma que implementó el código.

## Instrucción al agente

"Verifica la feature con el ritmo completo y dime si está lista para el PR."
