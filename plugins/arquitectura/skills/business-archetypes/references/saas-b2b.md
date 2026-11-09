# SaaS B2B multi-tenant

**Analogía:** un edificio de oficinas compartido. Cada empresa tiene su espacio, pero comparten ascensores, electricidad y portería; una empresa que crece mucho no puede dejar sin ascensor a las demás.

## Fuerzas dominantes

- **Aislamiento entre tenants**: de datos (seguridad), de rendimiento (vecino ruidoso) y de fallos (blast radius).
- **Distribución de tamaños muy sesgada**: muchos clientes pequeños y unos pocos enormes que generan la mayor parte del ingreso y de la carga.
- **Personalización y configuración** por tenant sin bifurcar el código.
- **Requisitos empresariales**: SSO, auditoría, residencia de datos, SLAs contractuales.

## Forma de la carga (sin métricas)

- Horario laboral de los clientes (picos por zona horaria) y procesos batch (importaciones, reportes, integraciones).
- Un tenant grande puede generar más carga que miles de pequeños juntos.
- Escenarios para explorar: 100, 10 000 y 1M tenants, con un tenant que es 1 000 veces el promedio.

## Invariantes y consistencia

- **Ningún tenant ve datos de otro**: es el invariante más importante; el tenant_id en cada consulta, con defensa en profundidad (row-level security, scoping obligatorio en la capa de datos).
- Límites y cuotas por tenant aplicados de forma consistente.
- Auditoría de acciones por usuario y tenant.

## Subdominios típicos

- **Core**: la funcionalidad del producto (lo que el cliente compra).
- **Supporting**: gestión de tenants y configuración, facturación por uso, integraciones, reportes.
- **Generic**: identidad y SSO, notificaciones, pagos.

## Camino recorrido (verifica antes de citar)

- Modelos de aislamiento silo (recursos dedicados por tenant), pool (todo compartido) y bridge (mixto), según la guía de SaaS de AWS.
- Arquitectura multi-tenant dirigida por metadatos (Salesforce).
- Sharding por tenant y migración a Vitess a gran escala (Slack).
- Celdas para limitar el blast radius de un tenant o de un deploy.

## Modos de fallo típicos (semilla para el red team)

- Fuga de datos entre tenants por una consulta sin filtro de tenant.
- Vecino ruidoso: un tenant con una importación masiva degrada a todos.
- Migración de esquema que tarda horas en la base del tenant más grande.
- Un tenant enorme que ya no cabe en el shard compartido.
- Un deploy malo que afecta a todos los clientes a la vez.

## Preguntas que cambian el diseño

- ¿Qué aislamiento exigen los clientes grandes (base dedicada, región dedicada, cifrado con su propia llave)?
- ¿Cómo se factura: por asiento, por uso, por plan?
- ¿Qué tan distinta es la configuración entre tenants?
- ¿Hay requisitos de residencia de datos por país?

## Hipótesis para un PoC

- Validar el aislamiento de datos con tests que intentan acceder a otro tenant.
- Validar cuotas y rate limits por tenant con un tenant sintético enorme.
- Instrumentar todo por tenant desde el día uno (latencia, errores, consumo): sin eso no se puede detectar el vecino ruidoso ni facturar por uso.
