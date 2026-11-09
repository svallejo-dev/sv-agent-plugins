# Fronteras de fase

Adaptado de las *phase boundaries* de mattpocock/skills (MIT), sin depender de una herramienta concreta.

Una **fase** es un trozo de trabajo dentro de una sesión: el diseño, la implementación, la revisión, el QA. Termina cuando piensas "listo, esto ya está". La **frontera** entre dos fases es el único lugar donde se decide qué hacer con el contexto. A mitad de una fase no hay decisión: se sigue, o se reparte lo que queda entre sub-agentes. Compactar a mitad de una fase hace que el agente pierda el hilo.

**Analogía:** cambiar de turno en un hospital. Si el mismo médico sigue, no se pierde nada. Si entra otro, recibe un resumen (el traspaso), y lo que el resumen no dice, se pierde. El traspaso es útil, pero nunca es gratis.

## Las cinco opciones

| Opción | Qué hace | En las herramientas |
|---|---|---|
| **Seguir** | Te quedas en la sesión | — |
| **Limpiar** | Vacía el contexto y empieza de cero | `/clear` en Claude Code; conversación nueva en las demás |
| **Traspasar** | Escribe un archivo portable y arranca con él donde sea | La skill `handoff` |
| **Delegar** | Manda la tarea a su propio contexto y recibe un informe | Sub-agentes, donde existan |
| **Compactar** | Resume este contexto y sigue con el resumen | `/compact` en Claude Code y Codex; donde no exista, `handoff` + conversación nueva |

## El árbol

Recórrelo de arriba abajo en la frontera; el primer "sí" gana.

1. **¿Puedes seguir?** Sí, si la siguiente fase necesita esta como **fuente primaria** (diseño → implementación: la implementación quiere el razonamiento literal, no un resumen) o si queda contexto de sobra para la fase siguiente. Seguir no cuesta nada: descártalo antes que todo lo demás.
2. **¿El contexto es irrelevante para lo que sigue?** Si toda la exploración, las decisiones y los callejones sin salida de esta sesión sobran, **limpia**. Es lo más barato. El error caro va en la otra dirección: limpiar un contexto relevante pierde el **porqué** de lo construido, y releer el diff no lo devuelve.
3. **¿Necesitas traspasar?** Solo si cambias de **herramienta** (Claude Code → Codex), de **directorio o repositorio**, pasas el trabajo a **otra persona**, o separas una tarea lateral que encontraste a mitad de fase. Lo que compra el traspaso es portabilidad: si nada viaja, no lo necesitas.
4. **¿Se puede hacer sin ti?** Si la tarea está tan acotada que corre sin que la guíes (una revisión automática que lee el diff y reporta), **delégala** a un sub-agente y deja esta sesión intacta.
5. **Si no, compacta.** Contexto relevante, misma herramienta, mismo directorio y necesitas seguir al mando: aquí cae el árbol, y cae a menudo. Dile al resumen qué conservar ("vamos a hacer QA de esta zona").

Compactar es el **valor por defecto, no el primer reflejo**. Está al final porque las cuatro preguntas anteriores son más baratas o más precisas. El fallo típico de empezar por aquí: una sesión nueva que se equivoca con mucha seguridad sobre una decisión que el resumen aplanó.

## Fuente primaria y secundaria

Toda opción salvo **seguir** cambia una fuente primaria (la sesión tal como ocurrió) por una secundaria (un resumen de ella):

| Fuente | Información | Ruido | Margen |
|---|---|---|---|
| Primaria (seguir) | Completa | Mucho | Poco |
| Secundaria (compactar, traspasar) | Con pérdida | Menos | Mucho |

Por eso la pregunta 1 va primero: la pérdida solo se paga cuando quedarse cuesta más de lo que ahorra.

Ninguna de estas preguntas es objetiva: la misma frontera puede resolverse distinto dos días seguidos. El valor está en hacerlas **en orden** y **en la frontera**, no a mitad del trabajo.
