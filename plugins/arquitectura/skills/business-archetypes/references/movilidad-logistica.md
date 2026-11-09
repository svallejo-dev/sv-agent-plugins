# Movilidad, logística y geolocalización

**Analogía:** una central de taxis con un mapa vivo. Las fichas (conductores, paquetes) se mueven todo el tiempo y la central debe emparejar cada pedido con la ficha correcta en segundos.

## Fuerzas dominantes

- **Estado geoespacial en tiempo real**: ubicaciones que cambian cada pocos segundos.
- **Matching** entre oferta y demanda (conductor-pasajero, repartidor-pedido) con restricciones de distancia y tiempo.
- **Recurso escaso disputado**: dos pedidos no pueden asignarse al mismo conductor a la vez.
- Demanda muy variable por zona y hora (lluvia, eventos, horas pico).

## Forma de la carga (sin métricas)

- Fórmula clave: **actualizaciones de ubicación/s ≈ agentes activos ÷ intervalo de envío**.
- Concentración geográfica: los puntos calientes de la ciudad concentran la carga.
- Escenarios para explorar: 1k, 100k y 1M agentes activos enviando ubicación cada 4-5 segundos.

## Invariantes y consistencia

- Un agente se asigna a un solo pedido a la vez (consistencia en la asignación).
- Las ubicaciones pueden ser eventuales y aproximadas; la última posición conocida vale más que el historial.
- Precios dinámicos coherentes durante la cotización y el viaje.

## Subdominios típicos

- **Core**: matching y despacho, pricing dinámico, estimación de tiempos de llegada.
- **Supporting**: gestión de viajes o envíos, perfiles de agentes, soporte.
- **Generic**: mapas y rutas (a menudo comprado), pagos, notificaciones.

## Camino recorrido (verifica antes de citar)

- Índices geoespaciales jerárquicos: geohash, S2 (Google) y H3 (índice hexagonal de Uber).
- Estado de ubicación en memoria particionado por celda geográfica.
- Pricing dinámico por zona según la relación oferta/demanda.

## Modos de fallo típicos (semilla para el red team)

- Celda caliente (un estadio al terminar un evento) que concentra la carga en una partición.
- Doble asignación de un agente por una carrera en el matching.
- Proveedor de mapas o rutas lento o con cuota agotada.
- Clientes móviles con mala señal que reintentan en ráfaga.
- Pérdida del estado en memoria de una partición geográfica.

## Preguntas que cambian el diseño

- ¿Cuántos agentes activos en la hora pico y con qué frecuencia envían ubicación?
- ¿Qué tan rápido debe resolverse un matching?
- ¿Mapas y rutas propios o de un proveedor? ¿Con qué cuotas?
- ¿El negocio es por ciudad (particionable) o necesita vista global?

## Hipótesis para un PoC

- Validar el matching con una simulación de agentes y pedidos en una ciudad, con zonas calientes.
- Validar el costo y las cuotas del proveedor de mapas al volumen esperado.
- Instrumentar: tiempo de matching, asignaciones conflictivas, frescura de la ubicación, carga por celda.
