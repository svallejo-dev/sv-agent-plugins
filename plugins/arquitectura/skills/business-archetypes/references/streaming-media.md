# Streaming y media (VOD y en vivo)

**Analogía:** una red de distribución de agua. El problema no es fabricar el agua (el contenido), es llevarla a millones de grifos a la vez sin que baje la presión.

## Fuerzas dominantes

- **Ancho de banda** por encima de todo: el sistema mueve bytes, no transacciones.
- **Lectura masiva y repetitiva**: el mismo contenido lo ven muchos; la cache en el edge es la arquitectura.
- **En vivo**: audiencia simultánea con picos al inicio de un evento (partido, estreno) y tolerancia mínima a la latencia.
- La experiencia se mide en arranque de reproducción, rebuffering y calidad, no en latencia de API.

## Forma de la carga (sin métricas)

- VOD: ola diaria (prime time) con picos ×2-3 sobre el promedio y estrenos que concentran audiencia.
- En vivo: rampa brusca en los minutos previos al evento; el "thundering herd" de login, autorización y manifiesto al mismo tiempo.
- Fórmula clave: **egreso ≈ espectadores concurrentes × bitrate medio**. Un stream HD es del orden de unos pocos Mbps; por eso miles de concurrentes ya son Gbps y millones son Tbps (verifica bitrates reales del códec y la escalera de calidades).
- Escenarios para explorar: 1k, 100k y 10M concurrentes. El primero cabe en un CDN comercial sin pensarlo; el último exige acuerdos con CDNs múltiples o red propia.

## Invariantes y consistencia

- Derechos y geobloqueo (qué puede ver quién y dónde): debe ser correcto, pero puede cachearse con TTL corto.
- Estado de reproducción ("seguir viendo"): eventual está bien.
- Entitlement de pago: correcto al autorizar, tolerante a segundos de retraso.

## Subdominios típicos

- **Core**: experiencia de reproducción (ABR, arranque rápido), recomendación y descubrimiento, gestión de derechos.
- **Supporting**: catálogo y metadatos, perfiles, ingesta y transcodificación.
- **Generic**: CDN, DRM, pagos, autenticación.

## Camino recorrido (verifica antes de citar)

- Streaming con bitrate adaptativo (HLS/DASH): el cliente cambia de calidad según su red.
- CDN propio dentro de los ISPs (Netflix Open Connect) a escala muy grande; CDNs comerciales y multi-CDN antes de eso.
- Chaos engineering nació en este dominio (Netflix, Chaos Monkey).

## Modos de fallo típicos (semilla para el red team)

- Thundering herd al inicio de un evento en vivo sobre auth, entitlement y manifiestos.
- Cache fría en el edge tras una purga o un contenido nuevo muy popular: el origen recibe todo.
- Caída o degradación de un CDN sin estrategia multi-CDN.
- DRM o licencias como dependencia síncrona del arranque.
- Costes de egreso que crecen más rápido que los ingresos.

## Preguntas que cambian el diseño

- ¿VOD, en vivo o ambos? ¿Qué latencia de en vivo se tolera (segundos vs decenas de segundos)?
- ¿Cuántos espectadores simultáneos en el peor evento imaginable?
- ¿Qué parte de la cadena es propia (ingesta, transcodificación) y cuál comprada?
- ¿Hay requisitos de DRM o geobloqueo por contrato con los dueños del contenido?

## Hipótesis para un PoC

- Validar primero el tiempo de arranque y el rebuffering con un CDN comercial y ABR estándar; casi nunca hace falta construir distribución propia en un PoC.
- Instrumentar desde el día uno: tiempo hasta el primer frame, ratio de rebuffering, bitrate medio servido, hit ratio del CDN, egreso por espectador.
- Simular el arranque de un evento en vivo (rampa de logins y manifiestos) antes de prometer escala.
