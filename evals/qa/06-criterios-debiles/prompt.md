# Caso 06: criterios débiles

## Preparación del repo de prueba

`.scratch/webhook-pagos/spec.md`: el servicio recibe webhooks del procesador de pagos (`payment.captured`, `payment.refunded`), actualiza el estado del pedido y publica un evento `pedido.pagado` que consume el servicio de facturación.

Criterios propuestos por el equipo, en la sección "Decisiones de testing" de la spec:

1. "El endpoint de webhooks responde 200."
2. "Se guarda el estado en la tabla `orders`."
3. "Se publica el evento en Kafka."
4. "Funciona correctamente con los dos tipos de evento."

`docs/agentes/qa.md`: modo solo.

## Instrucción al agente

"Pasa a limpio los criterios de aceptación de esta spec."
