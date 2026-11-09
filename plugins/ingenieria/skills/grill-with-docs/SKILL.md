---
name: grill-with-docs
description: "Interrogatorio sin tregua para afinar un plan o diseño que, sobre la marcha, escribe el glosario del dominio y los ADRs. Úsala solo cuando el usuario la pida explícitamente."
license: MIT
---

Carga dos skills (en Claude Code, con la herramienta Skill; en otras herramientas, mencionándolas por su nombre): primero `grilling` (plugin `general`) y después `domain-modeling`. Sigue ambas a la vez durante toda la sesión: `grilling` marca el ritmo de las rondas y `domain-modeling` decide cuándo actualizar `GLOSARIO.md` y cuándo ofrecer un ADR.
