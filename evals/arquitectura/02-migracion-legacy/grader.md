PASS solo si se cumple TODO:
1. Paso 0: antes de proponer el diseño final, levanta o pide el estado actual que falta (quién escribe la tabla de dispositivos, qué consultas hacen los 7 consumidores, de dónde viene el p99 de 900 ms, incidentes conocidos) en lugar de asumirlo en silencio.
2. Trata la base compartida como el problema central: propone cómo separar la propiedad de los datos (el servicio nuevo es dueño de sus tablas; los demás acceden por API o eventos) y cómo migrarlos (backfill, CDC u outbox; evita el dual-write sin reconciliación).
3. Propone un camino paso a paso con patrones nombrados (strangler fig o fachada, shadow traffic o dual-run con comparación usando el PHP como oráculo, canary con flags, expand-contract en el esquema), cada paso con señal de éxito y vuelta atrás.
4. Marca qué pasos son puertas de un sentido (borrar las tablas o el código viejo, cortar el acceso directo a la base) y los deja al final.
5. Considera el invariante "máximo 5 por cliente" durante la convivencia de ambos sistemas (quién lo aplica, riesgo de violarlo con escrituras concurrentes).
6. Incluye tabla de decisiones con disparadores medibles y nombra el punto débil.

FAIL si propone una reescritura con big-bang cutover, ignora la base compartida o no tiene plan de vuelta atrás.
