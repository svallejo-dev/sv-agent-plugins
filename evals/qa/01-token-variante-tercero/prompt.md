# Caso 01: token de un tercero con variantes

## Preparación del repo de prueba

`docs/agentes/qa.md`: modo solo, barrera N1, peldaños 1, 2 y 3 disponibles (con comandos ficticios), el procesador de pagos como tercero (learning tests + WireMock).

`.scratch/token-pagos/spec.md`:

> **Problema.** El front de checkout necesita autenticarse con el procesador de pagos para mostrar sus botones de pago y permitir guardar métodos de pago.
>
> **Solución.** Un BFF expone `POST /pagos/token`. Llama al endpoint OAuth del procesador (`/v1/oauth2/token`, `grant_type=client_credentials`), guarda el token en caché hasta que expire y lo devuelve a quien lo pida.
>
> **Historias.** 1. Como comprador, quiero ver los botones de pago en el checkout. 2. Como comprador, quiero guardar mi método de pago para la próxima compra. 3. Como comprador recurrente, quiero pagar con mi método guardado.
>
> **Decisiones.** El token se cachea en Redis con TTL igual a `expires_in`. El BFF no conoce al comprador: solo entrega el token.

`.scratch/token-pagos/qa/handoff.md` completo: superficie (`POST /pagos/token` → `{ "token": string }`), consumidor (el SDK web del procesador, inicializado en el front), dependencia (procesador de pagos, con sandbox y enlace a su documentación), artefacto (imagen Docker del BFF) y seams (siembra: no aplica; reloj: disponible; dependencias configurables: sí; aislamiento: cuentas de sandbox; observabilidad: trace-id).

`docs/procesador-oauth.md`, un resumen de la documentación del procesador (paráfrasis, no copia):

> El endpoint `/v1/oauth2/token` emite distintos tipos de token según el parámetro `response_type`. Sin él, emite un token de servidor para llamadas server-to-server; no debe exponerse al navegador. Con `response_type=client_token` emite un token seguro para el navegador, que el SDK web usa para inicializarse; llega también en el campo `access_token`. Con `response_type=id_token` emite un JWT de identidad que el SDK necesita para guardar métodos de pago; si además se envía `target_customer_id`, el token queda atado a ese comprador y permite pagar con sus métodos guardados.

## Instrucción al agente

"Diseña las pruebas de aceptación de la feature token-pagos. Los criterios todavía no están escritos."
