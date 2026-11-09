# Punto de partida

El paso 0 del diseño. Su objetivo es que nadie diseñe sobre una hoja en blanco: siempre hay algo de lo que partir, sea un edificio habitado, un vecino que ya construyó algo parecido o, como mínimo, el tipo de edificio que se quiere construir. **No tener métricas nunca bloquea el diseño.**

## Caso 1: sistema existente

### Inventario del AS-IS

Completa lo que puedas leyendo; pregunta solo lo que no está escrito en ninguna parte.

| Área | Qué capturar | Dónde buscar |
|---|---|---|
| Topología | Servicios, bases, caches, colas, terceros; quién llama a quién (síncrono o asíncrono) | Código, manifiestos de despliegue, diagramas existentes, APM (service map) |
| Flujos críticos | Los 2-4 caminos que más importan al negocio, de punta a punta | Conversación, RFCs, producto |
| Datos | Qué servicio escribe cada tabla/topic, volumen, crecimiento, retención | Código, migraciones, métricas de la base |
| Números medidos | Throughput pico, p50/p95/p99, errores, utilización, lag | APM y logs (ver `capacity-estimation`) |
| Objetivos | SLOs vigentes o implícitos, RPO/RTO, presupuesto de latencia | Docs de operación, contratos |
| Historia | Incidentes y postmortems del último año, load tests, cuellos de botella conocidos | Postmortems, runbooks, tickets |
| Deuda | Lo que el equipo sabe que está mal y por qué no se ha arreglado | Conversación, ADRs, TODOs |
| Restricciones | Compliance (PCI, datos personales), contratos con partners, stack obligado, presupuesto | Conversación, legal, contratos |
| Equipos | Quién es dueño de cada parte y quién tiene capacidad | Conversación, CODEOWNERS |
| Decisiones previas | Por qué se hizo así (ADRs, RFCs); qué se intentó y se descartó | Docs, historia del repo |

### Resultado

- Un diagrama Mermaid del AS-IS (simple, honesto, aunque sea feo).
- La tabla de números medidos con su fuente.
- La lista de dolores: qué duele hoy, medido si es posible ("p99 de 2 s en el checkout los días de campaña").
- Los huecos: qué no se sabe y cómo averiguarlo.

Un AS-IS que solo existe en la cabeza de alguien es el primer riesgo del proyecto: escribirlo ya es valor.

## Caso 2: camino similar

Cuando no hay sistema propio, el punto de partida es lo que otros ya resolvieron.

1. Con `research`, busca dos o tres sistemas parecidos con documentación primaria: blogs de ingeniería de la empresa que lo construyó, papers, charlas con slides, design docs públicos. Prioriza fuentes que cuenten **por qué** decidieron, no solo qué.
2. Para cada uno, extrae: escala declarada, restricciones, decisiones clave, lo que cambiaron con el tiempo y por qué.
3. Compara con tu caso: qué fuerzas compartes y cuáles no. Lo que para ellos era necesario a su escala puede ser sobreingeniería a la tuya.
4. Cita cada fuente. Un "así lo hace Netflix" sin enlace no vale como argumento.

## Caso 3: arquetipo de negocio (sin sistema ni métricas)

Es el caso normal de un diseño exploratorio o un PoC, y es un punto de partida válido, no un último recurso.

1. Identifica el arquetipo con `business-archetypes` a partir de la descripción del producto. Si mezcla varios, asigna cada uno a su subdominio.
2. Extrae del arquetipo: fuerzas dominantes, invariantes, forma de la carga, subdominios típicos, modos de fallo y las preguntas que cambian el diseño.
3. Haz esas preguntas al usuario en la primera ronda; son las que sustituyen a las métricas.
4. Combina con el caso 2 cuando haya sistemas similares documentados.
5. Registra cada supuesto que viene del arquetipo como tal ("supuesto de arquetipo: picos de ×100 en la apertura de ventas") y la medición que lo reemplazará (en el PoC o en producción).

### Resultado

- Una tabla de fuerzas: qué manda en este negocio y por qué.
- Los invariantes que no admiten error.
- Tres escenarios de escala por orden de magnitud (ver `capacity-estimation`, modo exploratorio).
- La lista de supuestos con la medición que los validará.

## Señales de que el paso 0 está incompleto

- Las alternativas propuestas no mencionan ninguna pieza del sistema actual.
- Los números son todos supuestos aunque el sistema existe y tiene APM.
- No hay métricas y tampoco se identificó el arquetipo de negocio: se está diseñando un sistema genérico que no existe.
- El diseño resuelve problemas que nadie reportó y no toca los dolores medidos.
- Nadie sabe quién es dueño de los datos que el diseño mueve.
