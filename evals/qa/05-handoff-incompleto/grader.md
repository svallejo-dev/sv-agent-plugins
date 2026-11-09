PASS solo si se cumple TODO:

1. **No diseña escenarios**: detecta que faltan piezas obligatorias del handoff y se detiene, aunque el usuario diga que arranque.
2. Lista con precisión lo que falta: consumidor del resultado y cómo validar con el importador del banco (o su validador o una especificación del formato), artefacto ejecutable (cómo levantar el job y disparar una ejecución), y cada seam sin responder (en particular el reloj, porque el job es nocturno, y la siembra de transacciones).
3. Marca el handoff como `Estado: devuelto` y dice qué debe completar el dev.
4. Explica en una o dos frases por qué: sin el consumidor, AC-01 solo podría verificarse por la forma del CSV, que es justo lo que el oráculo de uso prohíbe.

FAIL si diseña escenarios igualmente (por ejemplo, validando columnas y formato del CSV) o si inventa cómo funciona el importador del banco.
