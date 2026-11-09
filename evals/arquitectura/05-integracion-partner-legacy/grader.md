PASS solo si se cumple TODO:
1. Identifica la relación con el partner como upstream que no va a adaptarse a nosotros y elige explícitamente entre Anticorruption Layer y Conformist, justificando (la recomendación esperada es una ACL que traduzca IDs, estados y eventos del partner al modelo propio).
2. Propone un modelo propio estable (estados de suscripción, IDs) independiente de las dos versiones del partner, de modo que convivan legacy y API nueva por país detrás de la misma ACL.
3. Trata la poca fiabilidad del callback: idempotencia, reconciliación periódica con el partner y detección de divergencias.
4. Define el camino de transición por país (flags o enrutamiento por país, convivencia, criterio de corte) y marca las puertas de un sentido.
5. Clasifica el dominio (la gestión de la integración con partners como supporting o la autenticación como generic, no como core) y deriva de ahí cuánto invertir.
6. Entrega el mapa de contextos con el patrón de cada relación.

FAIL si acopla el modelo interno a los estados o IDs del partner, o si propone mantener dos integraciones independientes sin capa común.
