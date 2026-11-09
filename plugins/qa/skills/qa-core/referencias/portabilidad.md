# Portabilidad entre herramientas

Las skills de este repositorio siguen el estándar Agent Skills (`SKILL.md`) y funcionan en Claude Code, OpenAI Codex, GitHub Copilot, Cursor y Windsurf. Algunas instrucciones dependen de capacidades que cada herramienta ofrece de forma distinta. Esta página dice cómo cumplirlas en cada una y qué hacer si una capacidad no existe.

**Regla general:** si tu herramienta no ofrece una capacidad, no la simules en silencio. Aplica la alternativa de abajo y **decláralo** en el artefacto que produzcas (informe, criterios, escenarios): la honestidad sobre el aislamiento es parte del rigor.

## Sub-agentes con contexto limpio

Varias skills piden lanzar sub-agentes en paralelo (técnicas de diseño, premortem, revisores, red team) o delegar en un sub-agente "limpio" que no vio el código.

| Si tu herramienta… | Haz esto |
|---|---|
| Tiene sub-agentes (en Claude Code, la herramienta Agent; en otras, su mecanismo de sub-agentes o agentes personalizados) | Lánzalos como dice la skill, con el brief exacto y solo el material indicado |
| No tiene sub-agentes, pero puedes abrir una conversación nueva | Ejecuta cada encargo en una conversación nueva, pegando solo el brief y el material indicado; trae de vuelta la salida |
| No tiene ninguna de las dos | Ejecuta los encargos uno tras otro en la misma sesión y **declara** "sin aislamiento de contexto" en el artefacto. En el modo solo de QA, esto baja la barrera de información a N1 como máximo |

## Preguntas al usuario

Si tu herramienta tiene un mecanismo de preguntas con opciones (en Claude Code, AskUserQuestion), úsalo. Si no, pregunta en texto, numerando las opciones, y espera la respuesta.

## Cargar otra skill

Cuando una skill dice "invoca la skill `X`" o "carga `X`":
- En Claude Code, con la herramienta Skill. Si el plugin está instalado como plugin, su nombre aparece con espacio de nombres: `qa:qa-verify`, `ingenieria:tdd`.
- En las demás herramientas, menciónala por su nombre (`qa-verify`, `tdd`) o lee su `SKILL.md` en la carpeta hermana.

Si la skill no está instalada, sigue sin ella y dilo en una línea, como indica cada skill.

## Ejecutar scripts

Los scripts necesitan una herramienta que pueda ejecutar comandos en una terminal (todas las mencionadas pueden, con permiso del usuario). Si la sesión no puede ejecutar comandos, la skill no puede pasar por las puertas deterministas: dilo y no declares ninguna puerta como superada.
