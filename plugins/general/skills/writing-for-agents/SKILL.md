---
name: writing-for-agents
description: "Reference for writing documents an agent consumes. Use it when creating or editing skills or agent system prompts, or when modifying AGENTS.md or CLAUDE.md."
license: MIT
---

Respond in the user's language; keep common technical terms in English.

Reference for writing any document an agent consumes: a skill, an `AGENTS.md` / `CLAUDE.md`, a system prompt, a doc reached through a pointer. The packaging changes; the writing does not. The same levers make each of them predictable: the goal is for the agent to follow the same _process_ on every run, not to produce the same output.

If the document you are writing is a skill, read [SKILL-MECHANICS.md](SKILL-MECHANICS.md) for the frontmatter, the invocation choice and router skills.

## Context pointers

A **context pointer** is a reference that lives in the agent's context, names material that is outside the context and encodes the condition for fetching it. A skill's description is one; a line in `AGENTS.md` that names a doc is the same object. The pointer's _wording_, not its target, decides when the agent reaches the material and how reliably. An essential target behind a badly worded pointer is a variance bug: tune the wording first, and inline the material only if tuning fails.

Analogy: the pointer is the sign on a door. What is inside the room does not matter if the sign does not say when to go in.

A pointer does two jobs: say what the material is and list the **branches** that must trigger the fetch (a branch is a distinct case the document handles, so different runs take different paths). Every word of an always-loaded pointer costs on every turn, so it deserves even harsher pruning than the body:

- **Front-load the leading word**: the pointer is where it does its triggering work.
- **One trigger per branch.** Synonyms that rename the same branch are one branch written twice; collapse them and keep only the genuinely distinct branches.
- **Cut the identity the body already carries.**

## The two loads

Every document and every pointer you add spends one of two budgets:

- **Context load**: the cost of always-loaded material on the agent's window. A line in `AGENTS.md`, a skill's description, everything that is in context every turn, spending tokens and attention whether it fires or not.
- **Cognitive load**: the cost on the human: which documents exist and when to reach for each. The human is the index. It is not a cost to minimize: it is the price of human agency. Spend it where human judgment matters and remove it where it does not.

Material reached only through a pointer escapes the context load at the price of the pointer's own line; material with no pointer at all lives entirely on the cognitive load.

## Information hierarchy

A document is built from two kinds of content: **steps** (the ordered actions the agent takes) and **reference** (definitions, rules, facts consulted on demand). They mix freely: all steps (a recipe), all reference (the rules of a review, this skill) or both. The central decision is which rung of the **information hierarchy** each piece goes on, a ladder ordered by how urgently the agent needs the material:

1. **Step in the file**: the main rung, what the agent does, in order.
2. **Reference in the file**: consulted on demand. It is often a legitimate flat set (all the rules of a review on one rung), and that is fine.
3. **Disclosed reference**: moved to a separate file, reached through a pointer, loaded only when the pointer fires. It ranges from a sibling file in the same folder to fully external reference any document can point to.

If you push down too little, the top bloats; if you push down too much, you hide material the agent does need. That tension is the whole decision.

**Progressive disclosure**: moving down the ladder (out of the main file and behind a pointer) so the top stays readable. It is not mainly a token optimization: it is how the hierarchy is protected. Branching is the cleanest test: keep inline what every branch needs and put behind a pointer what only some reach. When a document has steps, inline reference that should be disclosed buries them and turns attending to them into a coin flip: it is a variance lever, not just a readability one.

**Co-location**: the complement inside the file. The ladder decides _how far_ a piece goes down; co-location decides _what goes next to it_. Keep a concept's definition, rules and caveats under one heading, so reading one part brings its neighbors along. The test: the document should read like documentation written for the agent. (Different from duplication: duplicating repeats one meaning in two places; scattering fragments one meaning across many.)

**Sprawl** is the failure mode: a document that is simply too long, even if every line is alive and unique. Attention dilutes in the excess and every extra line is one more to keep relevant. The cure is the ladder: disclose reference behind pointers and split by branch or by sequence so each path carries only what it needs.

## Steps and completion criteria

Each step ends in a **completion criterion**: the condition that tells the agent the work is done. Two properties make it a lever:

- **Clarity**: can the agent tell done from not done? A vague boundary ("understanding was reached") invites **premature completion**: finishing the step too early, with attention on _having finished_. The visible steps ahead pull; the criterion's clarity resists. Defend yourself in order: **sharpen the boundary first** (local and cheap); only if it is irreducibly fuzzy _and_ you observe the rush, hide the later steps by splitting the sequence. Hiding only works across a real context boundary (a handoff or a subagent; an inline call leaves the later steps in context and clears nothing).
- **Demand**: how much it asks for. "Every modified model accounted for" forces exhaustive work where "produce a list of changes" does not. Demand drives **legwork** (what the agent investigates within the task, latent in the wording instead of written as a step), and it is not tied to steps: "every rule applied" binds a flat body of reference just as "every step done" binds a sequence.

The strongest criteria are verifiable and exhaustive.

## When to split

Splitting a document in two spends one of the two loads, so split only when the cut justifies it:

- **By sequence**: split a series of steps when the later steps tempt the agent to rush the one in front of it. Keeping them out of sight generates more legwork on the current task. Beware the inverse: merging sequences exposes each step to the ones that come after and invites premature completion.
- **By invocation**, specific to skills: see [SKILL-MECHANICS.md](SKILL-MECHANICS.md).

## Leading words

A **leading word** is a compact concept that already lives in the model's pretraining and that the agent thinks with while running the document (_lesson_, _fog of war_, _tracer bullets_). Repeated as a token, never as a phrase, it accumulates a distributed definition and anchors a whole region of behavior with a minimum of tokens, because it recruits priors the model already has. Coining your own words works if you define them clearly, but an invented word recruits no priors: you pay in definition tokens what a pretrained word gives for free. Look for an existing word first.

It anchors twice. In the body, the _execution_: the agent reaches for the same behavior every time the word appears, and within flat reference it focuses attention on a class of things to look for. In a pointer, the _invocation_: when the same word lives in your prompts, your docs and your code, the agent connects that shared language with the material and reaches it more reliably.

Look for opportunities to refactor with leading words. A trio written in three places, a pointer that spends a sentence pointing at an idea: each one asks to collapse into a single token:

- "fast, deterministic, low cost" → _tight_ (a _tight_ loop).
- "a loop you trust" → _red_, which turns a fuzzy gate into an observable binary state (the loop turns _red_ with the bug, or it does not).

You win twice: fewer tokens and a sharper hook for the agent's thinking. Assume every document carries rephrasings that leading words can retire. Go look for them.

Mind the language: the strongest leading words are often the English technical terms the model has seen millions of times (_seam_, _tracer bullet_, _red-green_). In documents written in other languages, keep them in English instead of translating them into a word that recruits no priors.

**Negation** is the failure mode next to this lever: guiding by prohibition puts the forbidden behavior into the context and makes it _more_ available. _Do not think of an elephant_, and there is only elephant; negation is a weak modifier the strongly activated concept overruns, so the prohibition is half-read as an instruction to do it. Write the **positive**: state the target behavior ("write one-line comments") so the forbidden one is never named. A prohibition only earns its place as a hard guardrail you cannot express positively; even then, pair it with the positive target.

## Pruning

- Keep each meaning in a **single source of truth**: one authoritative place, so changing the behavior means editing one place. **Duplication** (the same meaning in more than one place) costs maintenance and tokens and inflates a meaning's importance above its real rung. (It is the accidental inverse of a leading word, which repeats a token on purpose, never the meaning.)
- The **environment** is a source of truth too (`go.mod`, the `Makefile`, configuration files, the directory structure, `--help` output), and a document that repeats it is a **cache**: a copy of a lookup, which only earns its load when the lookup is expensive. Cache what the agent cannot find by looking: the unwritten convention, the reason behind a choice, the trap no configuration admits. Leave one-file or one-command lookups to the environment, where they cannot go stale.
- Check each line's **relevance**: does it still influence what the document does? A line loses relevance if it never influenced anything (mere exposition, or a branch that should be disclosed) or if it went stale when the behavior or the world it describes changed. Short documents are easier to keep relevant. Without pruning discipline, the default fate is **sediment**: stale layers that settle because adding feels safe and removing feels risky.
- Hunt **no-ops** sentence by sentence: an instruction the model already follows by default pays load to say nothing. The test (does it change behavior relative to the default?) is relative to the model, not the reader: two people arguing about whether something is a no-op are arguing about the default, and it is settled by running the document, not by debating. When a sentence fails, delete it entirely instead of trimming words. The test also evaluates leading words: one too weak to beat the default (_be thorough_ when the agent already more or less is) is a no-op, and the fix is a stronger word (_relentless_), not another technique.
