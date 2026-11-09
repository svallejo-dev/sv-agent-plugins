PASS solo si se cumple TODO:

1. **Orden del proceso**: escribe los criterios antes que los escenarios (o se niega a diseñar escenarios sin criterios aprobados y los genera primero) y no se auto-aprueba: pide la aprobación humana.
2. **Oráculo de uso**: al menos un criterio se verifica con el SDK web del procesador aceptando el token para un flujo concreto, no solo con la forma de la respuesta (200, token no vacío o JWT).
3. **Variante por flujo**: identifica que cada historia necesita un tipo de token distinto (checkout → client token; guardar método → id_token; pago con método guardado → id_token con `target_customer_id`) y que la spec pide un único token sin `response_type`. Lo presenta como **hallazgo o pregunta de spec** (tabla de decisión flujo × variante o equivalente), no como un detalle a resolver en la implementación.
4. **Clave de caché**: detecta que un token atado a un comprador no puede servirse desde una caché compartida, y propone un escenario donde dos compradores distintos nunca reciben el mismo token personal.
5. **Seguridad**: señala que el token de servidor no debe llegar al navegador.
6. **Peldaños**: el escenario del SDK queda en el peldaño 3 (walking skeleton con el consumidor real, servido por el harness del QA) y propone learning tests contra el sandbox en el peldaño 2, grabados con WireMock, antes de construir fakes; no usa Pact contra el procesador.
7. **Composición**: usa sub-agentes en paralelo por técnica y el formato parseable (`AC-NN`, tabla de escenarios con ID, Criterio, Peldaño, Estado), y ejecuta `trazabilidad.py`.

FAIL si:
- los escenarios verifican solo la forma de la respuesta (código 200, token presente, formato JWT) sin el consumidor real;
- trata la caché compartida como correcta;
- resuelve la ambigüedad inventando una variante sin preguntar.

Calibración: la respuesta mala de referencia escribe escenarios del tipo "POST /pagos/token devuelve 200 y un token no vacío", "una segunda llamada devuelve el mismo token desde la caché" y "si el procesador falla, devuelve 502". Debe dar FAIL.
