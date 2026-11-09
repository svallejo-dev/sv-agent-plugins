# Catálogo de mutantes semánticos

Mutantes de nivel de negocio: errores que un dev o un agente cometen de verdad. Elige por riesgo según los criterios de la feature; no hace falta usar todas las categorías.

| Categoría | Mutación | Qué escenario debería detectarlo |
|---|---|---|
| **Límite** | `<` por `<=`, `5` por `6`, `>=` por `>` en una regla de negocio | Valores límite (técnica A) |
| **Condición** | Invertir una condición, eliminar una rama `else`, cortocircuitar una validación (`return nil` temprano) | Particiones inválidas, tablas de decisión |
| **Validación ausente** | Quitar la comprobación de un campo obligatorio, de un formato o de un rango | Particiones inválidas |
| **Autorización** | Quitar la comprobación de pertenencia del recurso al actor (IDOR) | Error guessing: autorización horizontal |
| **Idempotencia** | Ignorar la clave de idempotencia, o usarla sin guardar el resultado | Idempotencia (técnica D) |
| **Clave de caché** | Quitar de la clave de caché una dimensión (cliente, dominio, intent) | Terceros: caché; dos clientes nunca reciben el mismo valor |
| **TTL** | Ignorar `expires_in`, o un TTL mayor que el del tercero | Tiempo: expiración justo antes y después |
| **Variante del tercero** | Pedir otra variante (`response_type` distinto), u otra versión de API | Oráculo de uso y walking skeleton |
| **Error tragado** | Convertir un error de dependencia en éxito vacío, o en un 200 con cuerpo por defecto | Fallos de dependencias (técnica D) |
| **Reintento** | Quitar el reintento, reintentar operaciones no idempotentes, o sin backoff ni límite | Fallos de dependencias: 5xx, timeout tras ejecución |
| **Timeout** | Quitar el timeout de una llamada saliente, o subirlo por encima del presupuesto | Latencia con Toxiproxy |
| **Transición de estado** | Permitir una transición inválida (reembolsar un pendiente), o saltarse un estado | Transición de estados (técnica B) |
| **Concurrencia** | Quitar un lock, una transacción o un `SELECT … FOR UPDATE`; leer y luego escribir sin control de versión | Concurrencia: último cupo, doble cobro |
| **Serialización** | Renombrar un campo de la respuesta o del evento, cambiar su tipo, omitirlo cuando está vacío | Contrato (Pact), oráculo de uso |
| **Orden** | Cambiar el orden de un listado o de dos efectos (notificar antes de persistir) | Escenarios que verifican orden o el estado tras un fallo intermedio |
| **Datos sensibles** | Incluir un token o un dato personal en un mensaje de error o un log | Error guessing: datos sensibles |
| **Valor por defecto** | Cambiar un default (moneda, país, zona horaria) | Particiones del parámetro omitido |

## Cómo elegir

1. Para cada criterio de prioridad crítica, al menos un mutante que lo viole.
2. Para cada integración con un tercero, al menos uno de **variante**, uno de **clave de caché** (si hay caché) y uno de **error tragado**.
3. Completa hasta 5-10 con las categorías de mayor riesgo para el arquetipo de negocio.

## El caso del token como mutante

En el caso de PayPal, el mutante "pedir el token sin `response_type=client_token`" es justo el bug real. Una suite que lo deja sobrevivir no tiene un escenario con el SDK como oráculo de uso, por muchos tests que tenga. Y el mutante "clave de caché sin el cliente" sobrevive si ningún escenario pide tokens para dos clientes distintos.
