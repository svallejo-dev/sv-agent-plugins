PASS solo si se cumple TODO:
1. No se bloquea por la falta de métricas ni exige números antes de avanzar: trata el caso como diseño exploratorio y lo dice.
2. Identifica los arquetipos (ticketing con ventas flash + pagos) y de ahí las fuerzas: picos extremos en la apertura de ventas, contención sobre asientos, bots, y la corrección del pago.
3. Diseña primero los invariantes: no sobrevender (asignación con consistencia fuerte), holds con expiración, pago y ticket atados, idempotencia en el cobro.
4. Trabaja la escala como escenarios por orden de magnitud y umbrales de decisión calculados (por ejemplo, cuántos compradores simultáneos soporta la asignación directa sobre la base antes de necesitar una sala de espera), no como cifras inventadas presentadas como hechos.
5. Hace las preguntas que cambian el diseño (asientos numerados vs cupos, duración del hold, tolerancia a una cola de espera, política antibots, procesador de pagos y alcance PCI).
6. Propone un plan de PoC: hipótesis ordenadas por riesgo (no sobreventa bajo concurrencia, integración con el procesador), alcance mínimo, qué instrumentar y criterios de éxito y abandono.
7. Recomienda una arquitectura simple para el escenario probable (monolito modular, base relacional) con disparadores medibles para evolucionar.

FAIL si se niega a diseñar sin datos, si inventa métricas presentándolas como reales, o si propone una arquitectura de hiperescala sin justificarla con un escenario.
