# E-commerce y marketplace

**Analogía:** un centro comercial. Mucha gente mira escaparates (catálogo) y una fracción entra a pagar en caja (checkout). Las dos zonas necesitan cosas muy distintas.

## Fuerzas dominantes

- **Catálogo de lectura masiva**: búsqueda, navegación y detalle de producto dominan el tráfico.
- **Checkout correcto**: carrito, inventario, precio, pago y orden deben ser consistentes.
- **Picos por campañas** (Black Friday, Hot Sale, quincenas).
- En marketplace, **dos lados** (compradores y vendedores) con necesidades distintas y una fracción de vendedores gigantes.

## Forma de la carga (sin métricas)

- Ratio de lectura a escritura muy alto en catálogo; escritura concentrada en carrito y órdenes.
- Campañas con picos de ×5-×20 y productos en oferta que concentran el tráfico (hot items).
- Escenarios para explorar: 10, 1 000 y 100 000 órdenes por minuto en el pico de campaña.

## Invariantes y consistencia

- No vender lo que no hay en stock (o, si se acepta la sobreventa, que sea una decisión de negocio explícita con compensación).
- El precio cobrado es el precio mostrado y confirmado.
- La orden, el pago y la reserva de inventario se coordinan (saga u orquestación), con compensaciones.
- Catálogo y búsqueda: eventual está bien (segundos o minutos de retraso).

## Subdominios típicos

- **Core**: búsqueda y descubrimiento, pricing y promociones, experiencia de checkout; en marketplace, matching y confianza entre partes.
- **Supporting**: catálogo, inventario, órdenes, gestión de vendedores, logística y envíos.
- **Generic**: pagos, notificaciones, autenticación, fraude (a menudo comprado).

## Camino recorrido (verifica antes de citar)

- Monolito modular a gran escala (Shopify) como alternativa a microservicios prematuros.
- El paper de Dynamo (Amazon, 2007) nació de la disponibilidad del carrito de compras.
- Búsqueda en un índice dedicado alimentado por eventos del catálogo.

## Modos de fallo típicos (semilla para el red team)

- Hot item de una campaña: la fila de inventario de un producto se convierte en cuello de botella.
- Búsqueda caída o lenta: el tráfico se desvía a la base transaccional.
- Saga a medias: pago cobrado sin orden creada, o inventario reservado sin pago.
- Cache de precios desactualizada durante un cambio de promoción.
- Un vendedor gigante que sube un catálogo masivo y degrada a los demás.

## Preguntas que cambian el diseño

- ¿Inventario propio, de vendedores o ambos? ¿Se tolera sobreventa con compensación?
- ¿Qué tan dinámicos son los precios y promociones?
- ¿Cuál es el calendario de campañas y su magnitud esperada?
- ¿Hay vendedores con volúmenes desproporcionados?

## Hipótesis para un PoC

- Validar el flujo de checkout de punta a punta con compensaciones (fallos provocados en pago e inventario).
- Validar que catálogo y búsqueda se desacoplan de la base transaccional.
- Instrumentar: conversión por paso del funnel, latencia de búsqueda, órdenes en estados intermedios, conflictos de inventario.
