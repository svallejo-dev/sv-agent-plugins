# Caso 05: handoff incompleto

## Preparación del repo de prueba

- `docs/agentes/qa.md`: modo dúo.
- `.scratch/exportacion/spec.md`: un job nocturno exporta las transacciones del día a un CSV que el sistema contable del banco importa.
- `.scratch/exportacion/qa/criterios.md` aprobado, con `AC-01: el archivo del día lo procesa el importador del banco sin errores y los totales cuadran`.
- `.scratch/exportacion/qa/handoff.md` con la superficie descrita, pero **sin** la sección de consumidores (no dice cómo se obtiene o simula el importador del banco), **sin** artefacto ejecutable y con los seams sin responder.

## Instrucción al agente (QA)

"Diseña los escenarios de la exportación; el dev dice que el handoff ya está, que arranques."
