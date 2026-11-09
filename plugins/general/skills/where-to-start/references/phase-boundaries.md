# Phase boundaries

Adapted from the *phase boundaries* of mattpocock/skills (MIT), without depending on a specific tool.

A **phase** is a chunk of work within a session: design, implementation, review, QA. It ends when you think "done, this is finished". The **boundary** between two phases is the only place where you decide what to do with the context. Halfway through a phase there is no decision: you continue, or you split what is left among subagents. Compacting halfway through a phase makes the agent lose the thread.

**Analogy:** a shift change in a hospital. If the same doctor stays, nothing is lost. If another one comes in, they get a summary (the handoff), and whatever the summary does not say is lost. The handoff is useful, but it is never free.

## The five options

| Option | What it does | In the tools |
|---|---|---|
| **Continue** | You stay in the session | — |
| **Clear** | Empties the context and starts from scratch | `/clear` in Claude Code; a new conversation in the others |
| **Hand off** | Writes a portable file and starts from it anywhere | The `handoff` skill |
| **Delegate** | Sends the task to its own context and gets a report back | Subagents, where they exist |
| **Compact** | Summarizes this context and continues from the summary | `/compact` in Claude Code and Codex; where it does not exist, `handoff` + a new conversation |

## The tree

Go through it top to bottom at the boundary; the first "yes" wins.

1. **Can you continue?** Yes, if the next phase needs this one as its **primary source** (design → implementation: the implementation wants the literal reasoning, not a summary) or if there is plenty of context left for the next phase. Continuing costs nothing: rule it out before anything else.
2. **Is the context irrelevant to what comes next?** If all the exploration, decisions and dead ends of this session are unnecessary, **clear**. It is the cheapest. The expensive mistake goes the other way: clearing a relevant context loses the **why** of what was built, and rereading the diff does not bring it back.
3. **Do you need to hand off?** Only if you switch **tools** (Claude Code → Codex), **directory or repository**, pass the work to **another person**, or split off a side task you found halfway through a phase. What a handoff buys is portability: if nothing travels, you do not need it.
4. **Can it be done without you?** If the task is so well bounded that it runs without your guidance (an automated review that reads the diff and reports), **delegate** it to a subagent and leave this session intact.
5. **Otherwise, compact.** Relevant context, same tool, same directory and you need to stay in charge: the tree lands here, and it lands here often. Tell the summary what to keep ("we are going to QA this area").

Compacting is the **default, not the first reflex**. It is at the end because the four previous questions are cheaper or more precise. The typical failure of starting here: a new session that is confidently wrong about a decision the summary flattened.

## Primary and secondary source

Every option except **continue** trades a primary source (the session as it happened) for a secondary one (a summary of it):

| Source | Information | Noise | Headroom |
|---|---|---|---|
| Primary (continue) | Complete | A lot | Little |
| Secondary (compact, hand off) | Lossy | Less | A lot |

That is why question 1 comes first: the loss is only paid when staying costs more than it saves.

None of these questions is objective: the same boundary can be resolved differently on two consecutive days. The value lies in asking them **in order** and **at the boundary**, not halfway through the work.
