# Social, feeds y mensajería

**Analogía:** una plaza con altavoces. La mayoría habla con unos pocos vecinos, pero algunos tienen un altavoz que llega a millones, y eso cambia todo el sistema de sonido.

## Fuerzas dominantes

- **Fan-out**: un mensaje o publicación se entrega a muchos destinatarios.
- **Grafo sesgado**: unos pocos usuarios (celebrities, grupos enormes) concentran seguidores y tráfico.
- **Tiempo real**: chat, presencia, notificaciones push; conexiones persistentes (WebSockets).
- Volumen de escritura alto (mensajes, likes, eventos) y almacenamiento que crece sin parar.

## Forma de la carga (sin métricas)

- Lecturas de feed muy superiores a las publicaciones; picos por eventos culturales o deportivos.
- Conexiones concurrentes persistentes como recurso propio (memoria por conexión, balanceo de conexiones largas).
- Escenarios para explorar: 10k, 1M y 100M usuarios activos diarios, con un usuario de 10M seguidores en el escenario medio.

## Invariantes y consistencia

- Mensajes de un chat en orden dentro de la conversación; entrega al menos una vez con deduplicación en el cliente.
- Read-your-writes para el autor (ve su propia publicación al instante); eventual para los demás.
- Contadores (likes, vistas) aproximados y eventuales.
- Privacidad y bloqueos: deben aplicarse correctamente aunque el resto sea eventual.

## Subdominios típicos

- **Core**: grafo social, ranking del feed, entrega de mensajes en tiempo real.
- **Supporting**: perfiles, media, moderación de contenido, búsqueda.
- **Generic**: push notifications, almacenamiento de objetos, autenticación.

## Camino recorrido (verifica antes de citar)

- Fan-out on write para la mayoría y fan-out on read para cuentas con muchos seguidores (modelo híbrido de Twitter).
- Caches de grafo a gran escala (TAO de Facebook).
- Migraciones de almacenamiento de mensajes por problemas de latencia de cola (Discord, de Cassandra a ScyllaDB).
- Mensajería con Erlang/BEAM y muchas conexiones por servidor (WhatsApp).

## Modos de fallo típicos (semilla para el red team)

- Una celebrity publica: el fan-out on write genera millones de escrituras de golpe.
- Hot partition en el almacén de mensajes de un grupo enorme.
- Reconexión masiva de WebSockets tras un deploy o una caída (thundering herd).
- Contadores con escrituras concentradas en una sola fila.
- Moderación lenta que deja contenido dañino visible.

## Preguntas que cambian el diseño

- ¿Feed cronológico o rankeado? ¿Chat 1 a 1, grupos, o canales masivos?
- ¿Qué tamaño máximo tiene un grupo o cuántos seguidores puede tener una cuenta?
- ¿Cuánto historial se guarda y por cuánto tiempo?
- ¿Qué latencia de entrega se considera "tiempo real" para el producto?

## Hipótesis para un PoC

- Validar el modelo de fan-out con una distribución sesgada sintética (unos pocos usuarios con muchos seguidores), no con una uniforme.
- Validar la reconexión masiva de clientes en tiempo real.
- Instrumentar: latencia de entrega de punta a punta, conexiones por nodo, tamaño de las colas de fan-out, mensajes duplicados en cliente.
