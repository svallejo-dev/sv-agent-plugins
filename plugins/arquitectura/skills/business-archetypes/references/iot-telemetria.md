# IoT y telemetría

**Analogía:** una red de pluviómetros. Miles de aparatos envían una medición pequeña cada pocos segundos, sin parar; casi nadie mira cada dato, pero todos quieren las tendencias y las alarmas.

## Fuerzas dominantes

- **Ingesta continua de escrituras pequeñas**: el volumen de escritura domina sobre la lectura.
- **Series temporales**: los datos se consultan por rango de tiempo y se agregan; los recientes valen más que los viejos.
- **Dispositivos poco fiables**: conectividad intermitente, relojes desfasados, firmware antiguo.
- **Comandos hacia los dispositivos** (configuración, actualizaciones) con entrega garantizada.

## Forma de la carga (sin métricas)

- Fórmula clave: **escrituras/s ≈ dispositivos × frecuencia de envío**; bytes ≈ eso × tamaño del mensaje.
- Picos de reconexión: tras un corte, todos los dispositivos envían su backlog a la vez.
- Escenarios para explorar: 1k, 100k y 10M dispositivos, enviando cada 1, 10 y 60 segundos.

## Invariantes y consistencia

- Las mediciones pueden llegar tarde, duplicadas y fuera de orden: el sistema debe ordenar por el timestamp del evento (con cuidado con relojes desfasados) y deduplicar.
- Alarmas críticas con latencia acotada.
- Retención por niveles: datos crudos poco tiempo, agregados mucho tiempo (downsampling).

## Subdominios típicos

- **Core**: el análisis y las alarmas que dan valor (mantenimiento predictivo, monitoreo).
- **Supporting**: registro y aprovisionamiento de dispositivos, gestión de firmware, dashboards.
- **Generic**: broker de mensajería (MQTT), almacenamiento de series temporales, identidad de dispositivos.

## Camino recorrido (verifica antes de citar)

- MQTT como protocolo ligero de publicación y suscripción para dispositivos.
- Bases de series temporales con downsampling y retención por niveles.
- Procesamiento en el edge para filtrar y agregar antes de enviar.

## Modos de fallo típicos (semilla para el red team)

- Reconexión masiva tras un corte: backlog de todos los dispositivos a la vez.
- Un dispositivo defectuoso que envía a 100× su frecuencia.
- Relojes desfasados que ensucian las series y disparan alarmas falsas.
- El almacenamiento crece sin downsampling ni retención.
- Una actualización de firmware que deja inutilizada una flota.

## Preguntas que cambian el diseño

- ¿Cuántos dispositivos y con qué frecuencia? ¿Cuánto tiempo pueden estar desconectados?
- ¿Qué decisiones deben tomarse en tiempo real y cuáles sobre agregados?
- ¿Cuánto tiempo se guarda el dato crudo?
- ¿Los dispositivos pueden recibir comandos? ¿Con qué garantía?

## Hipótesis para un PoC

- Validar la ingesta con un simulador de dispositivos que incluya desconexiones, duplicados y desorden.
- Validar el costo de almacenamiento por dispositivo y mes con la retención propuesta.
- Instrumentar: mensajes por segundo por dispositivo, lag de ingesta, eventos fuera de orden, dispositivos silenciosos.
