# Fintech y pagos

**Analogía:** una bóveda con libro contable. Entra poca gente comparada con un centro comercial, pero cada movimiento debe quedar anotado una sola vez, cuadrar al final del día y poder auditarse años después.

## Fuerzas dominantes

- **Corrección por encima de la latencia**: un cobro duplicado o perdido es peor que un cobro lento.
- **Auditoría y trazabilidad**: cada cambio de saldo debe poder explicarse.
- **Compliance**: PCI DSS si se tocan datos de tarjeta, regulación financiera local, prevención de fraude y lavado.
- **Terceros en el camino crítico**: pasarelas, adquirentes, bancos, redes de tarjetas, con su latencia y su poca fiabilidad.

## Forma de la carga (sin métricas)

- Volumen modesto en comparación con otros arquetipos, pero con picos en días de pago (quincenas, fin de mes), campañas y renovaciones masivas de suscripciones.
- Las renovaciones y cobros programados concentran carga en horas fijas si no se reparten.
- Escenarios para explorar: 1, 100 y 10 000 transacciones por segundo. Casi todo producto nuevo vive en el primero durante mucho tiempo; el diseño debe ser correcto ahí antes de ser escalable.

## Invariantes y consistencia

- **Libro mayor de doble entrada** (double-entry ledger): cada movimiento tiene contrapartida; los saldos se derivan de los asientos, no se sobrescriben.
- **Efecto exactamente una vez** sobre una entrega al menos una vez: **idempotency keys** en cada operación que mueve dinero.
- Consistencia fuerte para saldos y estados de pago; eventual aceptable para reportes.
- **Reconciliación** diaria con los terceros: el estado propio y el del adquirente se comparan y las diferencias se investigan.
- Estados de pago como máquina de estados explícita (pendiente, autorizado, capturado, fallido, reembolsado), con transiciones válidas definidas.

## Subdominios típicos

- **Core**: el producto financiero (crédito, wallet, suscripciones, scoring), ledger, riesgo y fraude.
- **Supporting**: reconciliación, conciliación contable, notificaciones transaccionales.
- **Generic**: pasarela o procesador, KYC, tokenización de tarjetas.

## Camino recorrido (verifica antes de citar)

- Idempotency keys en la API de pagos (popularizadas por Stripe).
- Tokenización para sacar los datos de tarjeta del propio sistema y reducir el alcance de PCI DSS.
- Outbox para publicar eventos de pago sin dual-write.

## Modos de fallo típicos (semilla para el red team)

- Timeout con la pasarela después de que el cobro se ejecutó: ¿reintento = doble cobro?
- Webhook o callback duplicado, desordenado o perdido.
- Divergencia silenciosa entre el estado propio y el del procesador.
- Reintentos de renovaciones masivas que golpean al procesador y disparan su rate limit.
- Fraude o abuso explotando un endpoint sin límites.
- **Variante equivocada de credencial del tercero**: el mismo endpoint de OAuth del procesador devuelve tipos de token distintos según parámetros (token de servidor, client token para el navegador, `id_token` atado a un cliente), a veces en el mismo campo. Pedir la variante equivocada pasa cualquier validación de forma; cachear un token atado a un cliente en una caché compartida lo entrega a otro. Se detecta con el consumidor real como oráculo (walking skeleton) y con la clave de caché explícita.

## Preguntas que cambian el diseño

- ¿Se tocan datos de tarjeta o se delega todo en un procesador con tokenización?
- ¿Quién es la fuente de verdad del estado de un pago: nosotros o el procesador?
- ¿Qué pasa con un pago cuyo resultado es desconocido (timeout)?
- ¿Qué regulación y qué auditoría aplican en cada país?

## Hipótesis para un PoC

- Validar la máquina de estados y la idempotencia contra el sandbox del procesador, incluidos timeouts y webhooks duplicados provocados a propósito.
- Instrumentar: pagos por estado, tiempo en estado pendiente, diferencias de reconciliación, tasa de reintentos.
- No dejar para después la reconciliación: es lo primero que falla en producción y lo más caro de añadir tarde.
