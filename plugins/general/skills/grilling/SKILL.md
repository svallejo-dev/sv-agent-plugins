---
name: grilling
description: "Questions the user relentlessly about a plan, decision, design or idea until reaching a shared understanding. Use it when the user wants to stress-test their reasoning, asks to \"grill me\", \"question me\", \"challenge me\" or for a \"stress test\" of a plan."
license: MIT
---

Respond in the user's language; keep common technical terms in English.

Question the user relentlessly until you reach a shared understanding. Model the conversation as a **decision tree**: each decision branches into the decisions that depend on it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already resolved: the questions you can ask _now_ without guessing answers you have not heard yet. Ask the whole frontier in one round: number each question and give your recommended answer with a one-line reason. Then wait for the answers before the next round.

Format of a round:

```
❓ **Q1** - **<question title>**: <body, it can span several paragraphs and include options>

➡️ <your recommended answer> (because <one-line reason>)

---

❓ **Q2** - **<question title>**: <body>

➡️ <your recommended answer> (because <reason>)
```

Word each question so that "yes" accepts your recommendation.

Each round of answers changes the tree: resolved decisions push the frontier outwards and unlock the questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another one still open in this round belongs to a _later_ round.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (code, files, tools, git), launch a subagent with a clean context to find it out; do not ask the user for anything you can look up yourself. Do not block: an exploration in progress is an unresolved prerequisite, so only the questions that depend on it wait; ask the rest of the frontier now. _Decisions_ belong to the user: put them to them and wait.

When a question uses a concept the user may not master, name it with its canonical term and add a short analogy in parentheses.

The session ends when the frontier is empty: every branch of the tree visited and nothing silently assumed. Do not act on the result until the user confirms there is a shared understanding.
