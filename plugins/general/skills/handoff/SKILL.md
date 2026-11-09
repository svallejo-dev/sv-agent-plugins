---
name: handoff
description: "Compacts the current conversation into a handoff document so another agent (or a new session) can pick up the work. Use it only when the user explicitly asks for it."
license: MIT
---

Write, in the user's language, a handoff document that summarizes the current conversation so an agent with a clean context can continue the work. Save it in the system's temporary directory (`$TMPDIR`, otherwise `/tmp`; `%TEMP%` on Windows), not in the workspace. Tell the user the exact path.

Suggested structure:

- **Goal**: what is being attempted and why.
- **Status**: what is done, what is half-done, what is missing.
- **Decisions made**: each with a one-line reason.
- **Open and discarded hypotheses**: so the next agent does not repeat paths.
- **Concrete next step**: the first action it should take.
- **Suggested skills**: which marketplace skills the next agent should invoke (for example `diagnosing-bugs`, `tdd`).

Do not duplicate content that already lives in other artifacts (specs, tickets, ADRs, commits, diffs). Reference them by path or URL.

Redact any sensitive information: API keys, passwords, tokens, personal data. Write `<REDACTED>` in its place.

If the user passed arguments, treat them as the description of what the next session will focus on and tailor the document to it.
