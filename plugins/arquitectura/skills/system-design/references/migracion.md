# Patrones de migración

Cómo pasar de un estado actual a uno objetivo sin parar el sistema. Cada paso del camino debe ser desplegable por separado, verificable con una señal concreta y, siempre que se pueda, reversible.

**Puertas**: un paso es una **puerta de dos sentidos** si se puede revertir barato (cambiar una ruta, apagar un flag) y una **puerta de un sentido** si no (borrar datos, publicar un formato que otros ya consumen, cortar un contrato). Las de un sentido van al final del camino, después de que las señales confirmen el éxito, y con un ADR.

| Patrón | Qué es | Analogía | Úsalo cuando | Riesgo y cuidado |
|---|---|---|---|---|
| **Strangler fig** | Una fachada delante del sistema viejo enruta capacidad por capacidad al nuevo, hasta que el viejo se puede apagar | La higuera que crece alrededor del árbol hasta reemplazarlo | Reemplazar un monolito o un servicio legacy por partes | La fachada se vuelve permanente; decide cuándo parar ("lo que queda es suficientemente bueno") |
| **Branch by abstraction** | Introducir una abstracción en el código, implementar lo nuevo detrás y cambiar la implementación sin rama larga | Cambiar el motor con el coche en marcha, pasando por un acople | Reemplazar una librería o un componente interno | La abstracción temporal debe borrarse al final |
| **Expand-contract** (parallel change) | Añadir la forma nueva junto a la vieja, migrar los consumidores, borrar la vieja | Construir el puente nuevo al lado antes de demoler el viejo | Cambios de esquema, de contratos de API o de eventos | Mantener ambas formas tiene coste; la fase "contract" es de un sentido |
| **Transactional outbox / CDC** | Escribir el estado y el evento en la misma transacción local (outbox) o leer el log de la base (CDC) | Un recibo que se imprime con la misma operación que cobra | Publicar eventos de un sistema existente sin dual-write | Orden y duplicados: los consumidores deben ser idempotentes |
| **Dual-write** | Escribir en el almacén viejo y en el nuevo desde la aplicación | Llevar dos libretas a la vez | Casi nunca: solo con reconciliación y si no hay otra opción | Sin transacción común, los dos almacenes divergen; prefiere outbox o CDC |
| **Backfill** | Copiar los datos históricos al almacén nuevo mientras los nuevos llegan por el camino nuevo | Mudar los archivos viejos mientras el correo nuevo ya va a la casa nueva | Cualquier migración de datos | Throttling para no tumbar el origen; idempotente y reanudable |
| **Shadow traffic** (dark launch) | El sistema nuevo recibe una copia del tráfico real y sus respuestas se descartan | Un ensayo general con público real que no ve el escenario | Validar carga y comportamiento sin riesgo para el usuario | Cuidado con efectos laterales (escrituras, cobros, notificaciones): desactívalos en la sombra |
| **Dual-run con comparación** | Viejo y nuevo procesan lo mismo; se comparan los resultados y se registran las diferencias; el viejo sigue siendo la verdad | El sistema viejo hace de oráculo | Migraciones de lógica de negocio (reescrituras entre lenguajes o stacks) | Las diferencias esperadas (formato, orden) deben normalizarse antes de comparar |
| **Canary y despliegue progresivo** | El cambio llega a un porcentaje pequeño, se mide contra el SLO y se amplía o se revierte | Probar la comida con una cucharada antes de servir la olla | Todo cambio con riesgo, incluida la configuración | Elegir bien la población del canary (no solo tráfico interno) |
| **Feature flags** | Activar el camino nuevo por segmento, sin deploy | Un interruptor por habitación | Separar desplegar de liberar; rollback instantáneo | Deuda de flags: cada flag tiene fecha de borrado |
| **Cutover** | El momento en que el nuevo pasa a ser la verdad | Cambiar la dirección en el registro civil | Al final, con criterios de éxito cumplidos y plan de vuelta atrás | Si es de un sentido, ensáyalo y ten runbook |

## Forma de un camino de migración

```markdown
| Paso | Qué cambia | Patrón | Señal de éxito | Puerta | Vuelta atrás |
|---|---|---|---|---|---|
| 1 | Fachada delante del legacy, 100 % al legacy | Strangler | Latencia +<5 ms p99 | Dos sentidos | Quitar la fachada |
| 2 | Capacidad A en el servicio nuevo, en sombra | Shadow + dual-run | <0.1 % de diferencias en 7 días | Dos sentidos | Apagar la sombra |
| 3 | Capacidad A al 5 % → 50 % → 100 % | Canary + flag | SLO intacto | Dos sentidos | Flag al 0 % |
| 4 | Borrar el código y los datos de A en el legacy | Contract | 30 días sin tráfico en la ruta vieja | **Un sentido** | Restaurar desde backup (ADR) |
```
