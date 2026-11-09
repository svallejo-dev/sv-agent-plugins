---
name: to-tickets
description: "Divide un plan, una spec o la conversación actual en tickets tracer-bullet (rebanadas verticales), cada uno con sus bloqueos declarados, y los guarda como un archivo por ticket en el tracker local. Úsala solo cuando el usuario la pida explícitamente."
license: MIT
---

# To Tickets

Responde en español y conserva en inglés los términos técnicos habituales.

Divide un plan, spec o conversación en **tickets**: rebanadas verticales tipo **tracer bullet**, cada una con los tickets que la **bloquean**.

Analogía: una tracer bullet es la bala trazadora que deja una estela visible de punta a punta; cada ticket atraviesa todas las capas de forma fina, para ver enseguida si el camino entero funciona.

Lee `docs/agentes/tracker.md` para saber dónde y cómo guardar los tickets. Si no existe, dile al usuario que ejecute la skill `ingenieria-setup` y para.

## Proceso

### 1. Reúne contexto

Trabaja con lo que ya está en la conversación. Si el usuario pasa una referencia (la ruta de una spec o de un ticket), léela completa, incluidos sus comentarios.

### 2. Explora el código (opcional)

Si aún no exploraste el código, hazlo para entender su estado actual. Los títulos y descripciones de los tickets usan el vocabulario de `GLOSARIO.md` y respetan los ADRs del área.

Busca oportunidades de **prefactoring** que hagan más fácil la implementación: "primero haz fácil el cambio, después haz el cambio fácil".

### 3. Diseña rebanadas verticales

Divide el trabajo en tickets tracer bullet.

<reglas-rebanada-vertical>

- Cada rebanada recorre un camino estrecho pero COMPLETO por todas las capas (esquema, repositorio, servicio, handler, tests): vertical, NO una rebanada horizontal de una sola capa.
- Una rebanada terminada se puede demostrar o verificar por sí sola.
- Cada rebanada cabe en una sola ventana de contexto fresca.
- Cualquier prefactoring va primero.
- **Walking skeleton primero cuando hay un tercero o un consumidor externo nuevo**: el ticket `01` es la rebanada más delgada que atraviesa el camino completo con la integración real (el sandbox del tercero, el SDK o el consumidor que valida el resultado), sin lógica de negocio ni caché. Se termina cuando el consumidor real acepta lo que el sistema produce. Si la integración está mal entendida, falla aquí, el primer día, y no después de construir todo encima.

</reglas-rebanada-vertical>

Analogía: el walking skeleton es tender primero la cuerda de un puente colgante de orilla a orilla. No soporta tráfico, pero demuestra que las dos orillas se alcanzan antes de invertir en el tablero.

Dale a cada ticket sus **bloqueos**: los tickets que deben terminar antes de que pueda empezar. Un ticket sin bloqueos puede empezar ya.

**Los refactors anchos son la excepción.** Un **refactor ancho** es un cambio mecánico (renombrar una columna, cambiar el tipo de un símbolo compartido) cuyo **radio de impacto** se extiende por todo el código: una sola edición rompe miles de llamadas y ninguna rebanada vertical puede quedar en verde. No lo fuerces en un tracer bullet; secuéncialo como **expand–contract**. Primero expande: añade la forma nueva junto a la vieja para que nada se rompa. Después migra las llamadas por lotes según el radio de impacto (por paquete, por servicio), cada lote su propio ticket bloqueado por la expansión, manteniendo CI en verde porque la forma vieja sigue existiendo. Por último contrae: borra la forma vieja cuando no quede ningún llamador, en un ticket bloqueado por todos los lotes. Si ni siquiera los lotes pueden quedar en verde solos, mantén la secuencia pero que compartan una rama de integración y bloqueen un ticket final de integrar y verificar; el verde solo se promete ahí.

Analogía: expand–contract es como cambiar un puente sin cortar el tráfico. Construyes el nuevo al lado, desvías los carriles uno a uno y solo entonces demueles el viejo.

### 4. Valida con el usuario

Presenta la propuesta como lista numerada. Para cada ticket muestra:

- **Título**: nombre corto y descriptivo
- **Bloqueado por**: qué tickets deben terminar antes (si alguno)
- **Qué entrega**: el comportamiento de punta a punta que este ticket hace funcionar

Pregunta:

- ¿La granularidad se siente bien? (demasiado gruesa / demasiado fina)
- ¿Los bloqueos son correctos: cada ticket depende solo de los que de verdad lo bloquean?
- ¿Algún ticket debería fusionarse o dividirse más?

Itera hasta que el usuario apruebe la división.

### 5. Guarda los tickets

Escribe un archivo por ticket en `<ruta-del-tracker>/<feature-slug>/tickets/<NN>-<slug>.md`, numerados desde `01` en orden de dependencias (los que bloquean primero). Un ticket por archivo, nunca uno combinado. Si la fuente fue una spec, enlázala en cada ticket. No modifiques la spec ni ningún ticket padre.

<plantilla-ticket>

# <NN>: <Título del ticket>

Estado: listo-para-agente
Bloqueado por: <números de los tickets que lo bloquean, o "Ninguno">
Spec: <ruta relativa a spec.md, si existe>

## Qué construir

El comportamiento de punta a punta que este ticket hace funcionar, desde la perspectiva del usuario, no una lista de cambios capa por capa.

## Criterios de aceptación

- [ ] Criterio 1
- [ ] Criterio 2

Si existen criterios de QA aprobados (`.scratch/<feature>/qa/criterios.md`), referencia sus IDs (`AC-03`) en vez de reescribirlos: una sola fuente de verdad. Y si existen escenarios aprobados (`.scratch/<feature>/qa/escenarios.md`), añade debajo de `Spec:` la línea `Escenarios: ESC-01, ESC-04` con los escenarios de esos criterios que este ticket debe poner en verde: es el alcance de `qa-verify` en el ritmo por rebanada.

</plantilla-ticket>

Evita rutas de archivos y fragmentos de código: se desactualizan rápido. Excepción: si un prototipo produjo un fragmento que codifica una decisión con más precisión que la prosa (máquina de estados, esquema, forma de un tipo), inclúyelo e indica que viene de un prototipo, recortado a lo que contiene la decisión.

Al terminar, dile al usuario cuál es la **frontera**: los tickets sin bloqueos, por donde se empieza.
