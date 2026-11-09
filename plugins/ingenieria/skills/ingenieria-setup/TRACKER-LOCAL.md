# Tracker: Markdown local

Las specs y los tickets de este repo viven como archivos Markdown en `.scratch/`.

## Convenciones

- Una feature por carpeta: `.scratch/<feature-slug>/`.
- La spec es `.scratch/<feature-slug>/spec.md`.
- Los tickets de implementación son un archivo por ticket en `.scratch/<feature-slug>/tickets/<NN>-<slug>.md`, numerados desde `01`. Nunca un único archivo con todos los tickets.
- El estado va en una línea `Estado:` cerca del inicio de cada archivo. Valores: `listo-para-agente`, `listo-para-humano`, `en-curso`, `hecho`, `descartado`.
- Las dependencias van en una línea `Bloqueado por:` con los números de los tickets que lo bloquean, o `Ninguno`.
- Los comentarios y la historia se añaden al final bajo un encabezado `## Comentarios`, con fecha.

## Cuando una skill diga "publica en el tracker"

Crea el archivo dentro de `.scratch/<feature-slug>/`, creando la carpeta si hace falta.

## Cuando una skill diga "trae el ticket"

Lee el archivo en la ruta indicada. Normalmente el usuario pasa la ruta o el número del ticket.

## Frontera de trabajo

Un ticket está **desbloqueado** cuando todos los que aparecen en `Bloqueado por:` están en `hecho`. La frontera son los tickets desbloqueados que no están en `en-curso` ni `hecho`; gana el número más bajo. Al empezar uno, cambia su estado a `en-curso` y guarda antes de trabajar.
