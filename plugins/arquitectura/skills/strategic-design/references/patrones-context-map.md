# Patrones del mapa de contextos

Los patrones de relación entre contextos de Domain-Driven Design (Evans, _Domain-Driven Design_, 2003; Vernon, _Implementing Domain-Driven Design_, 2013). Cada relación tiene un **upstream** (el que publica o provee) y un **downstream** (el que consume y depende).

| Patrón | Qué es | Analogía | Úsalo cuando | Riesgo |
|---|---|---|---|---|
| **Partnership** | Dos equipos coordinan sus cambios y entregan juntos; éxito o fracaso compartido. | Dos socios que firman juntos cada decisión. | Dos contextos muy acoplados por un objetivo común y equipos que se hablan a diario. | Se vuelve una dependencia mutua permanente; no escala a muchos equipos. |
| **Shared Kernel** | Un subconjunto pequeño del modelo (tipos, una librería) compartido y cogestionado. | Una pared medianera entre dos casas. | Conceptos realmente idénticos en ambos lados y equipos coordinados. | Crece hasta ser un monolito compartido; cualquier cambio necesita a los dos. Mantenlo diminuto. |
| **Customer-Supplier** | El downstream (cliente) negocia sus necesidades y el upstream (proveedor) las planifica. | Un proveedor que atiende pedidos de un cliente importante. | El upstream tiene incentivos para atender al downstream (misma empresa, prioridades alineadas). | Si el upstream no cumple, el downstream queda bloqueado. Acuerda contratos y tests de contrato. |
| **Conformist** | El downstream adopta el modelo del upstream tal cual, sin traducir. | Usar el formulario del banco aunque no te guste. | El upstream no va a cambiar por ti y su modelo es aceptable. | El modelo ajeno se filtra en tu dominio; si es malo, te contamina. |
| **Anticorruption Layer (ACL)** | El downstream traduce el modelo del upstream al suyo en una capa aislada. | Un traductor en la frontera que impide que el idioma extranjero entre al país. | El upstream es legacy, de un tercero o con un modelo que no quieres heredar; integraciones con proveedores externos; migraciones. | Coste de mantener la traducción; puede esconder lógica de negocio si se descuida. |
| **Open Host Service (OHS)** | El upstream ofrece una API o protocolo pensado para muchos consumidores. | Una oficina de atención al público con ventanilla estándar. | Un upstream con varios consumidores que no puede negociar con cada uno. | Si la API es pobre, todos los consumidores la sufren; necesita versionado. |
| **Published Language (PL)** | Un lenguaje de intercambio documentado (esquemas de eventos, un formato estándar). Suele ir con OHS. | El idioma oficial de los documentos entre países. | Eventos de dominio entre contextos, integraciones con estándares de la industria. | Evolucionarlo exige compatibilidad hacia atrás y gobierno de esquemas. |
| **Separate Ways** | Los contextos no se integran; cada uno resuelve lo suyo. | Dos vecinos que deciden no compartir nada. | El coste de integrar supera el beneficio. | Duplicación de datos y lógica. |
| **Big Ball of Mud** | No es un patrón a elegir: es reconocer una zona sin fronteras claras. | El trastero donde todo está mezclado. | Para **nombrar** honestamente un legacy en el mapa AS-IS. | Ponle una ACL alrededor y no dejes que el desorden se extienda. |

## Combinaciones frecuentes

- **OHS + PL en el upstream, ACL en cada downstream**: la forma sana de un bus de eventos con muchos consumidores. El upstream publica eventos versionados; cada consumidor traduce a su modelo.
- **ACL + strangler fig** para salir de un legacy: la ACL protege el modelo nuevo mientras el strangler va moviendo capacidades del sistema viejo al nuevo.
- **Conformist frente a un generic**: con un proveedor de autenticación o de pagos estándar, a veces es razonable conformarse con su modelo en un adaptador fino, en vez de una ACL completa.

## Señales de un mapa enfermo

- Dos contextos escriben las mismas tablas: la frontera es ficticia.
- Un "servicio común" o una "base compartida" que todos tocan: Shared Kernel descontrolado.
- Eventos con el modelo interno del productor (todas las columnas de la tabla) en vez de hechos de negocio: falta un Published Language.
- Un cambio de negocio exige desplegar varios servicios a la vez: la frontera corta un invariante o un área que cambia junta.
- Un equipo depende de otro para casi todo y no tiene incentivos alineados: Customer-Supplier sin contrato, que en la práctica es Conformist.
