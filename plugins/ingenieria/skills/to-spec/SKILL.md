---
name: to-spec
description: "Convierte la conversación actual en una spec (PRD) y la guarda en el tracker local, sin entrevista, solo sintetizando lo ya discutido. Úsala solo cuando el usuario la pida explícitamente."
license: MIT
---

Responde en español y conserva en inglés los términos técnicos habituales.

Esta skill toma el contexto de la conversación y lo que sabes del código y produce una spec. NO entrevistes al usuario: sintetiza lo que ya sabes. (Si falta entendimiento, el paso anterior era `grilling` o `grill-with-docs`.)

Lee `docs/agentes/tracker.md` para saber dónde guardar la spec. Si no existe, dile al usuario que ejecute la skill `ingenieria-setup` y para.

## Proceso

1. Explora el repo para entender el estado actual del código, si aún no lo hiciste. Usa el vocabulario de `GLOSARIO.md` en toda la spec y respeta los ADRs del área que vas a tocar.

2. Esboza los **seams** en los que vas a testear la feature. Prefiere seams existentes a nuevos. Usa el seam más alto posible. Si hacen falta seams nuevos, propónlos en el punto más alto que puedas. Cuantos menos seams, mejor: lo ideal es uno. (Seam: el punto donde puedes observar o cambiar el comportamiento sin editar ese punto; suele ser la interfaz pública de un módulo o un endpoint HTTP.)

   Confirma con el usuario que esos seams coinciden con lo que espera.

3. Escribe la spec con la plantilla de abajo y guárdala en `<ruta-del-tracker>/<feature-slug>/spec.md` con la línea `Estado: listo-para-agente`.

<plantilla-spec>

# <Título de la feature>

Estado: listo-para-agente

## Problema

El problema que enfrenta el usuario, desde su perspectiva.

## Solución

La solución al problema, desde la perspectiva del usuario.

## Historias de usuario

Una lista LARGA y numerada de historias de usuario, con este formato:

1. Como <actor>, quiero <funcionalidad>, para <beneficio>

<ejemplo-historia>
1. Como cliente de Claro Video, quiero ver qué dispositivos tengo registrados, para poder liberar uno cuando llegue al límite
</ejemplo-historia>

La lista debe ser muy extensa y cubrir todos los aspectos de la feature.

## Decisiones de implementación

Lista de decisiones de implementación tomadas. Puede incluir:

- Los módulos (paquetes, servicios) que se construyen o modifican
- Las interfaces de esos módulos que cambian
- Aclaraciones técnicas del desarrollador
- Decisiones de arquitectura
- Cambios de esquema
- Contratos de API
- Interacciones concretas entre servicios

NO incluyas rutas de archivos ni fragmentos de código: se desactualizan muy rápido.

Excepción: si un prototipo produjo un fragmento que codifica una decisión con más precisión que la prosa (máquina de estados, esquema, forma de un tipo), inclúyelo dentro de la decisión correspondiente e indica que viene de un prototipo. Recórtalo a lo que contiene la decisión, no a una demo funcional.

## Consumidores del resultado

Quién consume lo que esta feature produce (un token, un evento, un archivo, una respuesta de API) y cómo valida ese consumidor que le sirve. Es el **oráculo de uso**: si otro consume el resultado, el consumidor real decide si funciona, no la forma del artefacto.

| Consumidor | Qué consume | Cómo valida que le sirve |
|---|---|---|

Si un tercero devuelve variantes distintas según parámetros o flujo (tipos de token, versiones de API), anota aquí qué variante necesita cada flujo, o déjalo como pregunta abierta.

## Testabilidad

Los seams que el sistema expone para que se pueda probar desde fuera. Responde cada uno: disponible, no, o no aplica.

- Siembra de datos por API o endpoint de setup en ambientes no productivos
- Reloj controlable (expiraciones, ventanas de tiempo)
- Dependencias configurables por variable (para fakes y fallos de red)
- Aislamiento de datos de prueba (tenant o cuentas de prueba) y limpieza
- Observabilidad accesible: trace-id o correlation-id en respuestas y logs

Un seam que falta no bloquea la spec, pero deja escenarios sin poder probarse: es deuda explícita.

## Decisiones de testing

Lista de decisiones de testing tomadas. Incluye:

- Qué hace bueno a un test (solo comportamiento externo, no detalles de implementación)
- Qué módulos se testean y en qué seam
- Antecedentes (tests parecidos que ya existan en el código)

## Fuera de alcance

Lo que queda fuera de esta spec.

## Notas

Cualquier otra nota sobre la feature.

</plantilla-spec>

4. Si el repo usa el plugin `qa` (existe `docs/agentes/qa.md`), escribe también el **contrato de handoff** en `<ruta-del-tracker>/<feature-slug>/qa/handoff.md`, con `Estado: borrador` y estas secciones: 1. Superficie (contrato de API o lista de endpoints y eventos con su forma), 2. Consumidores del resultado (la tabla de la spec), 3. Dependencias (propia o tercero, sandbox, documentación oficial), 4. Artefacto ejecutable (cómo construir la imagen o arrancar el servicio; URLs por ambiente, sin secretos), 5. Seams de testabilidad (los de la spec, cada uno disponible, no o no aplica, y cómo se usa), 6. Restricciones. Lo que no sepas, déjalo como `pendiente` y dilo: el QA devolverá un handoff incompleto.

5. Dile al usuario dónde quedó la spec y que el siguiente paso natural es la skill `to-tickets` con esa ruta; si escribiste el handoff, que el siguiente paso de QA es `qa-acceptance-criteria` y luego `qa-test-design`, antes de los tickets si quiere la línea `Escenarios:` en cada ticket.
