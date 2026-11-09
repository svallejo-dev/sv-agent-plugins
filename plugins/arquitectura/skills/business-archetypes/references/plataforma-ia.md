# Plataforma de IA (inferencia)

**Analogía:** un restaurante con pocos chefs estrella carísimos. Cada plato tarda en prepararse, los chefs no se pueden contratar al instante, y el arte está en agrupar pedidos para que ningún chef quede ocioso sin hacer esperar demasiado a nadie.

## Fuerzas dominantes

- **Cómputo caro y escaso**: las GPUs (o aceleradores) son el recurso limitante y el mayor costo; no escalan en segundos.
- **Latencia en dos partes**: tiempo hasta el primer token y tokens por segundo después; las respuestas se transmiten en streaming.
- **Requests largos y de tamaño muy variable** (contexto de entrada, longitud de salida).
- **Costo por token** como métrica de negocio.

## Forma de la carga (sin métricas)

- El throughput se mide en **tokens por segundo**, no en requests por segundo; dos requests pueden diferir en órdenes de magnitud.
- Conexiones de larga duración (streaming durante segundos o minutos).
- Picos por lanzamientos y por clientes que ejecutan lotes.
- Escenarios para explorar: 10, 1 000 y 100 000 requests concurrentes, con contextos de 1k, 10k y 100k tokens.

## Invariantes y consistencia

- Límites por cliente en requests y en tokens por minuto, aplicados de forma consistente.
- Facturación por uso exacta (tokens de entrada y salida).
- Aislamiento de datos entre clientes (prompts y respuestas), con políticas de retención explícitas.

## Subdominios típicos

- **Core**: serving de modelos (batching, scheduling de GPUs, enrutamiento entre modelos), calidad y evaluación.
- **Supporting**: gestión de claves y cuotas, facturación por uso, observabilidad de uso, caching de prompts.
- **Generic**: autenticación, pagos, almacenamiento.

## Camino recorrido (verifica antes de citar)

- Batching continuo y gestión de memoria del KV cache (vLLM, PagedAttention) para aumentar el throughput por GPU.
- Rate limiting por requests y tokens por minuto, como hacen las APIs de proveedores de modelos.
- Caching de prompts para reutilizar prefijos largos.
- Streaming de respuestas con Server-Sent Events.

## Modos de fallo típicos (semilla para el red team)

- Cola de GPUs saturada: el tiempo hasta el primer token se dispara para todos.
- Un cliente con requests de contexto enorme acapara la capacidad (vecino ruidoso).
- Conexiones de streaming cortadas por proxies o balanceadores con timeouts cortos.
- Reintentos de clientes ante errores 429 o 529 que agravan la sobrecarga.
- Falta de capacidad en una región sin posibilidad de escalar rápido.

## Preguntas que cambian el diseño

- ¿Modelos propios o de un proveedor? ¿Uno o varios?
- ¿Qué latencia hasta el primer token necesita el producto?
- ¿Uso interactivo, por lotes o ambos? ¿Se pueden separar las colas?
- ¿Qué requisitos de retención y privacidad de los prompts hay?

## Hipótesis para un PoC

- Validar latencia y costo por request con la distribución real de tamaños de contexto, no con un tamaño fijo.
- Validar el comportamiento ante límites del proveedor (429) con backoff y colas.
- Instrumentar: tiempo hasta el primer token, tokens por segundo, tokens por request (entrada y salida), costo por request, tasa de 429.
