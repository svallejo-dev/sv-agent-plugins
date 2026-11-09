# Plantilla de design doc

Escríbelo en el idioma del equipo. Quita las secciones que no apliquen en vez de dejarlas vacías. Si el repo ya tiene una plantilla de RFC o design doc, usa la suya y asegúrate de que cubre estas secciones.

~~~markdown
# Diseño: <sistema o cambio>

**Estado:** borrador | en revisión | aprobado · **Objetivo:** producción | exploratorio | PoC · **Autores:** … · **Fecha:** …

## 1. Contexto y punto de partida
Qué existe hoy (o qué sistema similar se tomó como referencia, con enlaces, o qué arquetipo de negocio y con qué fuerzas e invariantes), qué duele y por qué cambiar ahora.

```mermaid
flowchart LR
  %% AS-IS
```

## 2. Requisitos (como delta)
- **Funcionales:** …
- **No funcionales:** latencia, disponibilidad, consistencia, escala, coste.
- **Restricciones:** compliance, contratos, equipos, stack.
- **Fuera de alcance:** …

## 3. Números
| Dato | Valor o escenario | Fuente (medido / referencia / arquetipo / supuesto) | Decisión que habilita |
|---|---|---|---|

Umbrales de decisión: a partir de qué valor cambia cada decisión dependiente de la escala.

## 4. Alternativas consideradas
Para cada una: diagrama, idea central, por qué sí y por qué no. Incluye la de cambio mínimo.

## 5. Diseño propuesto
```mermaid
flowchart LR
  %% TO-BE
```
Interfaces (request, response, keys, idempotencia) y modelo de datos con su dueño.

## 6. Decisiones y trade-offs
| Decisión | Resuelve | Empeora | Cámbiala cuando… |
|---|---|---|---|

## 7. Fronteras y relaciones
Mapa de contextos con el patrón de cada relación (si aplica).

## 8. Fallos y degradación
Matriz de riesgos del red team: riesgo, detección, mitigación, estado.

## 9. Operación
SLOs, alertas, dashboards, runbooks, capacidad de reserva.

## 10. Camino de migración (o plan del experimento si es un PoC)
| Paso | Qué cambia | Patrón | Señal de éxito | Puerta | Vuelta atrás |
|---|---|---|---|---|---|

En un PoC: | Hipótesis | Alcance mínimo | Instrumentación | Éxito | Abandono | y la lista de deuda deliberada.

## 11. Evolución
Qué se rompe primero a ×10 y qué se haría entonces.

## 12. Temas, preguntas abiertas y riesgos aceptados

### Registro de temas

| Tema | Estado | Decisión o pregunta pendiente | Base |
|---|---|---|---|
| | abierto / cerrado / aplazado | | medición / referencia / arquetipo / supuesto |

Un tema cerrado sobre un supuesto puede reabrirse: anota qué señal lo reabriría. Los aplazados llevan la condición para retomarlos.

### Riesgos aceptados

| Riesgo | Por qué se acepta | Cómo se detecta si ocurre |
|---|---|---|

### Validación antes de compartir
- [ ] El punto de partida (AS-IS, referencia o arquetipo) está descrito y cada número tiene fuente
- [ ] Hay al menos dos alternativas, una de cambio mínimo
- [ ] Cada decisión tiene disparador medible
- [ ] El red team está hecho y cada riesgo tiene detección
- [ ] El camino de migración marca las puertas de un sentido
- [ ] La rúbrica está puntuada y la dimensión más débil, nombrada
- [ ] No quedan temas abiertos sin dueño ni fecha, o están declarados como aplazados
~~~
