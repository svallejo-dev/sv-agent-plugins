---
name: handoff
description: "Compacta la conversación actual en un documento de traspaso para que otro agente (o una sesión nueva) retome el trabajo. Úsala solo cuando el usuario la pida explícitamente."
license: MIT
---

Escribe en español un documento de traspaso que resuma la conversación actual para que un agente con contexto limpio pueda continuar el trabajo. Guárdalo en el directorio temporal del sistema (`$TMPDIR`, si no `/tmp`; `%TEMP%` en Windows), no en el workspace. Dile al usuario la ruta exacta.

Estructura sugerida:

- **Objetivo**: qué se intenta lograr y por qué.
- **Estado**: qué está hecho, qué está a medias, qué falta.
- **Decisiones tomadas**: con la razón en una línea cada una.
- **Hipótesis abiertas y descartadas**: para que el siguiente agente no repita caminos.
- **Siguiente paso concreto**: la primera acción que debería hacer.
- **Skills sugeridas**: qué skills del marketplace debería invocar el siguiente agente (por ejemplo `diagnosing-bugs`, `tdd`).

No dupliques contenido que ya vive en otros artefactos (specs, tickets, ADRs, commits, diffs). Referéncialos por ruta o URL.

Redacta cualquier información sensible: API keys, contraseñas, tokens, datos personales. Escribe `<REDACTED>` en su lugar.

Si el usuario pasó argumentos, trátalos como la descripción de en qué se centrará la siguiente sesión y adapta el documento a ello.
