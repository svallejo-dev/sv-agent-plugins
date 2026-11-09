---
name: research
description: "Investiga una pregunta contra fuentes primarias de alta confianza y deja los hallazgos en un archivo Markdown del repo. Úsala cuando el usuario quiera investigar un tema, reunir datos de documentación o de una API, o delegar lectura a un agente en segundo plano."
license: MIT
---

Lanza un **agente en segundo plano** para hacer la investigación, así sigues trabajando mientras lee. Inícialo con contexto limpio.

> **Portabilidad:** si tu herramienta no tiene sub-agentes, ejecuta cada encargo en una conversación nueva con solo su brief, o en secuencia en esta sesión, y declara en el resultado que no hubo aislamiento de contexto.

Su encargo:

1. Investigar la pregunta contra **fuentes primarias** (documentación oficial, código fuente, especificaciones, RFCs, APIs de primera mano, el `go doc` del paquete), no resúmenes de terceros. Seguir cada afirmación hasta la fuente que la posee.
2. Escribir los hallazgos en español, en un único archivo Markdown, citando la fuente de cada afirmación con enlace. Marcar explícitamente lo que no pudo verificar.
3. Guardarlo donde el repo ya guarde notas de este tipo, siguiendo la convención existente. Si no hay ninguna, usar `docs/investigaciones/<slug>.md` y decir dónde quedó.

Cuando el agente termine, resume al usuario en 3-5 líneas lo que encontró y dale la ruta del archivo.
