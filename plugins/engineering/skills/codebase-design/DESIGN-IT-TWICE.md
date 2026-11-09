# Design it twice

When the user wants to explore alternative interfaces for a deepening candidate, use this parallel-subagent pattern. Based on "Design It Twice" (Ousterhout): your first idea is rarely the best.

Use the vocabulary of [SKILL.md](SKILL.md): **module**, **interface**, **seam**, **adapter**, **leverage**.

## Process

### 1. Frame the problem space

Before launching subagents, write for the user an explanation of the chosen candidate's problem space:

- The constraints any new interface must meet
- The dependencies it would rely on and which category each falls into (see [DEEPENING.md](DEEPENING.md))
- An illustrative code sketch in the project's language to ground the constraints (not a proposal, just a way to make them concrete)

Show it to the user and move straight on to step 2. The user reads and thinks while the subagents work in parallel.

### 2. Launch the subagents

Launch 3 or more subagents in parallel, each with a clean context. Each must produce a **radically different** interface for the deepened module.

> **Portability:** if your tool has no subagents, run each assignment in a new conversation with only its brief, or in sequence in this session, and declare in the result that there was no context isolation.

Give each subagent its own technical brief (file paths, coupling details, dependency category according to [DEEPENING.md](DEEPENING.md), what sits behind the seam). The brief is independent of the explanation of step 1. Give each one a different design constraint:

- Agent 1: "Minimize the interface: between 1 and 3 entry points at most. Maximize the leverage per entry point."
- Agent 2: "Maximize flexibility: support many use cases and extension."
- Agent 3: "Optimize for the most common caller: make the default case trivial."
- Agent 4 (if applicable): "Design with ports & adapters for the dependencies that cross the seam."

Include in the brief the vocabulary of [SKILL.md](SKILL.md) and that of `GLOSSARY.md`, so each subagent names things consistently with the architecture language and with the domain's. Ask for the code to be idiomatic in the project's language; if you loaded `<language>-design`, include its rules in the brief.

Each subagent delivers:

1. Interface (types, functions, methods, parameters, plus invariants, ordering and error modes)
2. Usage example from a caller
3. What the implementation hides behind the seam
4. Dependency and adapter strategy (see [DEEPENING.md](DEEPENING.md))
5. Trade-offs: where the leverage is high and where it is poor

### 3. Present and compare

Present the designs one by one so the user can take them in, then compare them in prose. Contrast them by **depth** (leverage at the interface), **locality** (where changes concentrate) and **seam location**.

After comparing, give your recommendation: which design you believe is the strongest and why. If elements of several designs combine well, propose a hybrid. Be opinionated: the user wants a firm reading, not a menu.
