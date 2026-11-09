---
name: research
description: "Researches a question against high-confidence primary sources and leaves the findings in a Markdown file in the repo. Use it when the user wants to research a topic, gather facts from documentation or an API, or delegate reading to a background agent."
license: MIT
---

Respond in the user's language; keep common technical terms in English.

Launch a **background agent** to do the research, so you keep working while it reads. Start it with a clean context.

> **Portability:** if your tool has no subagents, run each assignment in a new conversation with only its brief, or in sequence in this session, and declare in the result that there was no context isolation.

Its assignment:

1. Research the question against **primary sources** (official documentation, source code, specifications, RFCs, first-hand APIs, the package's `go doc`), not third-party summaries. Follow each claim to the source that owns it.
2. Write the findings in the user's language, in a single Markdown file, citing the source of each claim with a link. Explicitly mark what it could not verify.
3. Save it wherever the repo already keeps notes of this kind, following the existing convention. If there is none, use `docs/research/<slug>.md` and say where it went.

When the agent finishes, summarize what it found for the user in 3-5 lines and give them the file path.
