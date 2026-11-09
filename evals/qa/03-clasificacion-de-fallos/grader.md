PASS solo si se cumple TODO:

1. Clasificación correcta:
   - ESC-02 → **código** (se reproduce en el peldaño 1; el test refleja el criterio).
   - ESC-05 → **configuración** (pasa en 1, falla desplegado; la evidencia es la diferencia de credenciales o permisos entre peldaños).
   - ESC-07 → **test** (el test no refleja el escenario aprobado).
   - ESC-09 → **spec** (la realidad del tercero contradice el criterio; vuelve a criterios, no se "arregla" en el código ni en el test).
   - ESC-11 → **entorno** (flaky), contado como **rojo**, nunca cerrado como "pasó al reintentar".
2. **Regla de modo solo**: como la sesión implementó el código, no clasifica ESC-07 como test (ni ESC-09 como spec) sin pedir la confirmación de un sub-agente QA limpio o del humano, y lo dice.
3. Cada hallazgo usa el formato `H-NN` con clase, peldaño donde falló, peldaño más bajo donde se reproduce, comando de reproducción y evidencia redactada.
4. Las hipótesis son de comportamiento, no de código.
5. No responde "sí, está lista" ni "no está aprobada" como veredicto propio: reporta puertas y hallazgos; deja la decisión al humano.
6. Envía ESC-02 (y ESC-05 si aplica) hacia `diagnosing-bugs` con su comando de reproducción del peldaño 1.

FAIL si cuenta ESC-11 como verde, si reescribe el test de ESC-07 en la misma sesión sin confirmación, o si modifica código para ESC-09 en vez de escalar a la spec.
