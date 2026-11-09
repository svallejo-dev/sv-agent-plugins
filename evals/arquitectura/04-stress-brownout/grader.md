PASS solo si se cumple TODO:
1. Calcula la amplificación de reintentos: con 3 reintentos (4 intentos) en tres capas, un fallo en la base puede generar hasta 4 × 4 × 4 = 64 llamadas por request de usuario.
2. Detecta que los timeouts no están anidados de forma coherente con el presupuesto (el de arriba debería ser mayor que la suma de lo que espera abajo, o mejor, propagarse un deadline) y que el cliente móvil probablemente abandona antes.
3. Analiza el brownout (la base se pone lenta sin caerse): los pools y la concurrencia crecen, el autoscaling por CPU no reacciona porque los hilos esperan I/O, y añadir instancias aumenta la carga sobre la base.
4. Nombra el riesgo de fallo metaestable (el sistema queda saturado por los reintentos aunque la causa desaparezca) y cómo romper el bucle (retry budget, reintentar en una sola capa, load shedding, circuit breaker).
5. Incluye la detección: qué alertas sobre síntomas del usuario saltarían y cuánto tardarían.
6. Presenta una matriz de riesgos priorizada con estado y mitigación.

FAIL si solo recomienda "añadir circuit breakers" sin cuantificar la amplificación ni analizar el brownout.
