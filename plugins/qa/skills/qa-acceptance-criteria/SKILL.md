---
name: qa-acceptance-criteria
description: "Convierte una spec o un ticket en criterios de aceptación verificables desde fuera, cada uno con su oráculo; aplica la regla del oráculo de uso (si otro consume el resultado, el consumidor decide), hace explícitos los criterios implícitos y corre un premortem de criterios. Úsala cuando el usuario pida \"criterios de aceptación\", \"acceptance criteria\", \"definition of done de la feature\", o antes de diseñar escenarios de QA."
license: MIT
---

# Criterios de aceptación

Responde en español y conserva en inglés los términos técnicos habituales.

Un criterio de aceptación es una afirmación sobre el comportamiento **observable desde fuera** que, si es falsa, la feature no sirve. Es la primera pieza del oráculo: si el criterio es débil, todo lo que se construya encima (escenarios, tests, verificación) hereda esa debilidad, con todos los tests en verde.

**Analogía:** el criterio es la pregunta del examen. Si la pregunta es "¿el alumno escribió algo?", aprueba todo el mundo. Si es "¿la respuesta abre la puerta correcta?", solo aprueba quien entendió.

Lee primero [../qa-core/referencias/modelo-de-roles.md](../qa-core/referencias/modelo-de-roles.md) y el formato en [../qa-core/referencias/formatos.md](../qa-core/referencias/formatos.md) (sección 2).

## 0. Precondiciones

- Lee `docs/agentes/qa.md`. Si no existe, dile al usuario que ejecute la skill `qa-setup` y para.
- Lee la spec completa (`.scratch/<feature>/spec.md`) y, si existe, `.scratch/<feature>/qa/handoff.md`. La sección "Consumidores del resultado" del handoff es la entrada más importante de esta skill.
- **Regla de contaminación.** Si en esta sesión se leyó o escribió código de producción de la feature, **no escribas los criterios aquí**: lanza un sub-agente con contexto limpio y el brief de abajo para los pasos 1 a 4. El que conoce la implementación ya no puede imaginar cómo falla. Los pasos 5 (premortem) y 6 (aprobación) los hace siempre la sesión principal: un sub-agente no puede lanzar otros sub-agentes ni hablar con el humano. La regla es de buena fe: ninguna puerta comprueba qué leyó la sesión.

Brief del sub-agente:

"Eres el QA de la feature <feature>. Tu trabajo es escribir criterios de aceptación verificables desde fuera. Lee SOLO estos archivos: <spec>, <handoff si existe>, <contratos de API>, y las referencias del plugin qa que te paso. No leas código de producción ni el diff, ni pidas verlo. Sigue los pasos 1 a 4 de la skill qa-acceptance-criteria y devuelve el contenido completo de criterios.md en estado borrador, más la lista de preguntas abiertas y de criterios inferidos."

## 1. Extrae los candidatos

Recorre la spec en este orden y anota un candidato por comportamiento:

1. **Historias de usuario**: cada una produce al menos un criterio del camino feliz.
2. **Decisiones de implementación** que tengan efecto observable (un límite, un código de error, un orden, un tiempo de expiración).
3. **Fuera de alcance**: produce criterios negativos ("no se permite…", "no se expone…") cuando la frontera importa.
4. **Consumidores del resultado** (handoff): cada consumidor produce un criterio con su oráculo de uso (paso 3).

## 2. Haz cada criterio verificable

Cada criterio pasa estas seis pruebas. Si no pasa una, reescríbelo o divídelo:

| Prueba | Mal | Bien |
|---|---|---|
| **Observable desde fuera** | "Se guarda en la tabla devices" | "El dispositivo aparece en el listado del cliente" |
| **Un solo comportamiento** | "Registra, valida y notifica" | Tres criterios |
| **Datos concretos** | "Respeta el límite" | "Con 5 dispositivos registrados, un sexto se rechaza con 409" |
| **Oráculo nombrado** | "Funciona correctamente" | "Oráculo: el listado devuelve 5 elementos y la respuesta es 409" |
| **Independiente de la implementación** | "Usa la caché de Redis" | "Una segunda petición en menos de 1 s devuelve el mismo token" |
| **Fuente trazable** | — | "Fuente: historia 4" o "inferido" |

Un criterio "inferido" (no está en la spec) es válido, pero **requiere la confirmación explícita** del humano: puede ser un requisito que nadie escribió o un invento tuyo.

## 3. Aplica la regla del oráculo de uso

**Si el sistema produce algo que otro consume (un token, un evento, un archivo, un webhook, un correo), el criterio se verifica con el consumidor real, no con la forma del artefacto.**

- Mal: "El endpoint devuelve un token no vacío".
- Bien: "El token devuelto permite al SDK de pagos inicializarse y completar un checkout en sandbox".

La forma (que sea un JWT, que tenga tal campo) puede ser un criterio adicional, nunca el único. Es la regla que más bugs caros evita y la que más se olvida. Casos y patrones en [references/oraculo-de-uso.md](references/oraculo-de-uso.md).

Si el handoff no dice quién consume un resultado, **pregúntalo**: es una pieza obligatoria del contrato.

## 4. Haz explícitos los criterios implícitos

Las specs casi nunca escriben estas propiedades, y son las que fallan en producción. Para cada una, decide con el humano si aplica; si aplica, es un criterio con `Fuente: inferido`:

- **Idempotencia**: ¿repetir la misma petición produce el mismo efecto una sola vez?
- **Autorización**: ¿un actor puede ver o modificar recursos de otro?
- **Fallo de dependencias**: ¿qué ve el usuario si una dependencia tarda, falla o responde a medias?
- **Límites**: valores mínimos, máximos, vacíos, tamaños, cantidades.
- **Concurrencia**: dos peticiones simultáneas sobre el mismo recurso.
- **Tiempo**: expiraciones, ventanas, zonas horarias, relojes desfasados.
- **Variantes de terceros**: si un tercero devuelve cosas distintas según parámetros o flujo, ¿qué variante necesita cada flujo? (ver la checklist de terceros de `qa-test-design`).
- **Datos sensibles**: qué no debe aparecer en respuestas, logs ni errores.

Si la feature encaja en un arquetipo de `business-archetypes` y ese plugin está disponible, usa sus invariantes y modos de fallo típicos como fuente adicional.

## 5. Premortem de criterios

Obligatorio en modo solo; recomendado en modo dúo.

Pregunta: **"Seis meses después, esta feature falló en producción y todos los criterios estaban en verde. ¿Por qué?"**

Lanza 3 sub-agentes en paralelo, cada uno con la spec, los criterios en borrador y un ángulo distinto:
1. El usuario final y el negocio.
2. Los consumidores e integraciones con terceros.
3. La operación: fallos, datos, tiempo, despliegue.

> **Portabilidad:** si tu herramienta no tiene sub-agentes, sigue [../qa-core/referencias/portabilidad.md](../qa-core/referencias/portabilidad.md) y decláralo en el artefacto.

Encargo: "Escribe 3 historias concretas de cómo esta feature falló en producción aunque todos estos criterios pasaban. Para cada historia: qué pasó, qué criterio faltaba o qué oráculo era débil, y el criterio que lo habría detectado. Menos de 400 palabras. Responde en español."

Cada historia termina en un criterio nuevo, un oráculo reforzado o un descarte justificado. Los varios agentes dan diversidad de hipótesis; el beneficio medido del premortem (menos exceso de confianza) solo aparece si **el humano lee las historias y decide**.

## 6. Escribe y pide aprobación

- Escribe `.scratch/<feature>/qa/criterios.md` con el formato de [../qa-core/referencias/formatos.md](../qa-core/referencias/formatos.md), `Estado: borrador`.
- Presenta al humano, en este orden:
  1. Las **preguntas abiertas**: ambigüedades de la spec que bloquean un criterio.
  2. Los criterios **inferidos** que necesitan confirmación.
  3. Los criterios con **oráculo de uso**.
  4. El resto, agrupado por historia.
- Itera hasta que el humano apruebe. Solo él cambia la línea a `Estado: aprobado`. **Nunca te auto-apruebes**, ni siquiera si el humano dice "lo que tú digas": en ese caso, señala los tres criterios de mayor riesgo y pide confirmación de esos.

Siguiente paso: `qa-test-design`.
