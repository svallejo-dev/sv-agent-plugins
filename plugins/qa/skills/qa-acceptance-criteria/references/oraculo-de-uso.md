# El oráculo de uso

**Regla:** si el sistema produce algo que otro consume, el criterio se verifica con el consumidor real. La forma del artefacto es un criterio complementario, nunca el único.

**Analogía:** un hotel. Hay llave maestra, llave genérica de huésped y llave de habitación. El cerrajero puede verificar que la llave está bien cortada (la forma). Solo la puerta dice si es la llave correcta (el uso). Y una llave de habitación copiada y entregada a cualquiera que la pida es un problema aunque abra perfectamente.

## Por qué la forma no basta

Un test que verifica la forma lo escribe alguien con la **misma creencia** que quien implementó: si el dev creía que "el token es lo que devuelve el endpoint de OAuth", el test verifica justo eso, y pasa. El consumidor real no comparte tu creencia: es un oráculo **independiente**. Es el mismo principio que separa al agente dev del agente QA, aplicado a la frontera con otros sistemas.

## Caso de referencia: el token de PayPal

Un BFF pedía un token a la API de OAuth de PayPal, lo guardaba en caché y lo entregaba a quien lo pidiera. Las pruebas de integración tardías mostraron que el consumidor necesitaba **otro tipo de token**, de morfología distinta.

Lo que hace engañoso el caso:
- El mismo endpoint (`/v1/oauth2/token`) devuelve tokens distintos según `response_type`: un token de servidor por defecto, un client token seguro para el navegador (`response_type=client_token`), o un `id_token` JWT (`response_type=id_token`, opcionalmente con `target_customer_id` para un comprador recurrente).
- El client token llega en el **mismo campo** `access_token` que el token de servidor. El esquema es idéntico; cambia el significado.
- Un `id_token` con `target_customer_id` está **atado a un cliente**: una caché compartida que lo entrega a cualquiera es un error de clave de caché con impacto de seguridad.

(Detalles de PayPal verificados en su documentación en noviembre de 2026; vuelve a verificarlos antes de usarlos como hecho.)

Cómo lo habría detectado cada criterio:

| Criterio | ¿Detecta el bug? |
|---|---|
| "El endpoint devuelve 200 y un token no vacío" | No |
| "El token es un JWT" | Solo si alguien ya sabía qué forma esperar |
| "El token permite al SDK inicializarse y completar el checkout en sandbox, para cada flujo (checkout, guardar método, pago con método guardado)" | **Sí, el día 1** |
| "El token entregado a un cliente nunca se entrega a otro cliente" | **Sí**: revela el error de clave de caché |

## Patrones por tipo de artefacto

| El sistema produce… | Consumidor | Oráculo de uso |
|---|---|---|
| Token o credencial | SDK, front, otro servicio | El consumidor lo acepta para la operación concreta, en el flujo concreto |
| Evento publicado | Suscriptores | Un consumidor de prueba lo deserializa con el esquema del suscriptor real y produce el efecto esperado |
| Webhook saliente | Partner | La verificación de firma del partner (o su validador) lo acepta |
| Archivo exportado (CSV, conciliación) | Sistema contable, banco, analista | El importador del destino lo procesa sin errores y cuadran los totales |
| Respuesta de API pública | Clientes móviles o web | Pact del consumidor, o el cliente real en un test de humo |
| URL firmada o enlace | Navegador, CDN | La URL descarga el recurso y expira cuando debe |
| Correo o notificación | Usuario | El proveedor de correo de prueba lo recibe con enlaces que funcionan |

## Cómo se convierte en escenario

El oráculo de uso suele exigir el **peldaño 3** (consumidor real con dependencias reales) o el **peldaño 2** (contrato del consumidor). Ver [../../qa-core/referencias/escalera-de-ambientes.md](../../qa-core/referencias/escalera-de-ambientes.md). Si el consumidor real no se puede levantar en ningún peldaño, el escenario queda `bloqueado-testabilidad` y es deuda explícita, no un criterio que se rebaja a verificar la forma.

Para integraciones con terceros, el criterio de uso se acompaña de un **walking skeleton** como primer ticket (ver `to-tickets`): la rebanada más delgada que atraviesa el camino completo con el consumidor real, antes de cualquier lógica o caché.
