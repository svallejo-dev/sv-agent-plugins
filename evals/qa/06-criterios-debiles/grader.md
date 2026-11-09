PASS solo si se cumple TODO:

1. Reescribe los cuatro criterios para que sean observables desde fuera, de un solo comportamiento, con datos concretos y oráculo nombrado:
   - el 2 deja de hablar de la tabla (estado del pedido consultado por la API);
   - el 3 pasa a oráculo de uso (el consumidor de facturación deserializa el evento con su esquema y lo procesa), no "se publica";
   - el 4 se divide por tipo de evento y transición de estado.
2. Hace explícitos, con `Fuente: inferido` y pidiendo confirmación, al menos: **idempotencia** (webhook duplicado no produce dos eventos ni dos transiciones), **orden** (refunded antes que captured), **verificación de firma** (un webhook no firmado o mal firmado se rechaza) y **transiciones inválidas**.
3. Corre el premortem de criterios (obligatorio en modo solo) con sub-agentes en paralelo y muestra cómo cada historia cambia o añade un criterio.
4. Usa el formato parseable `## AC-NN:` con Comportamiento, Oráculo, Fuente, Tipo y Prioridad, en `Estado: borrador`, y pide aprobación humana.

FAIL si conserva criterios de implementación ("se guarda en la tabla", "se publica en Kafka") como únicos criterios, si omite la idempotencia del webhook o si se auto-aprueba.
