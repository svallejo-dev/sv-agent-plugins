---
name: grill-with-docs
description: "Relentless questioning to sharpen a plan or design that, along the way, writes the domain glossary and the ADRs. Use it only when the user explicitly asks for it."
license: MIT
---

Respond in the user's language; keep common technical terms in English.

Load two skills (in Claude Code, with the Skill tool; in other tools, by mentioning their names): first `grilling` (`general` plugin) and then `domain-modeling`. Follow both at once for the whole session: `grilling` sets the pace of the rounds and `domain-modeling` decides when to update `GLOSSARY.md` and when to offer an ADR.
