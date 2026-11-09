---
name: codebase-design
description: "Shared, language-agnostic vocabulary for designing deep modules. Use it when the user wants to design or improve the interface of a module, package or type, find deepening opportunities, decide where a seam goes, make the code more testable or easier for agents to navigate, or when another skill needs this vocabulary."
license: MIT
---

# Codebase design

Respond in the user's language; keep common technical terms in English. The first time you use a glossary term in a conversation, accompany it with its analogy.

## Language

This skill is language-agnostic. Identify the language of the code by its file extensions (`.go` → `go`, `.php` → `php`, `.ts`/`.tsx` → `typescript`, `.py` → `python`). If `<language>-design` exists among your available skills, load it (in Claude Code, with the Skill tool; in other tools, by mentioning its name or reading its SKILL.md): it translates this vocabulary into the language's tools (how the implementation is hidden, where interfaces are declared, how dependencies are injected) and its rules take precedence over the generic examples here. If it does not exist, carry on with this skill alone.

Design **deep modules**: a lot of behavior behind a small interface, placed at a clean seam and testable through that interface. Use this language and these principles wherever code is designed or restructured. The goal is leverage for callers, locality for maintainers and testability for everyone.

## Glossary

Use these terms exactly: do not replace them with "component", "service", "API" or "boundary". Consistent language is the goal.

**Module**: anything with an interface and an implementation. Scale-agnostic on purpose: a function, a class or type with its methods, a package, a service. _Avoid_: unit, component, service.
Analogy: a box with a plug on the outside and circuits on the inside.

**Interface**: everything a caller must know to use the module correctly: the type signature, but also invariants, ordering constraints, error modes, required configuration and performance characteristics. _Avoid_: API, signature (too narrow: they only cover the type surface). Note: it is not just the `interface` keyword of some languages.
Analogy: the appliance's complete user manual, not just the shape of the plug.

**Implementation**: what is inside the module, its code. Distinct from **adapter**: something can be a small adapter with a large implementation (a Postgres repository) or a large adapter with a small implementation (an in-memory fake). Say "adapter" when the topic is the seam; "implementation" otherwise.

**Depth**: leverage at the interface. How much behavior a caller (or a test) can exercise per unit of interface it has to learn. A module is **deep** when there is a lot of behavior behind a small interface, and **shallow** when the interface is almost as complex as the implementation.
Analogy: a light switch is deep (one button, the whole electrical installation behind it); a panel with one switch per wire is shallow.

**Seam** _(Michael Feathers)_: a place where you can alter behavior without editing that place; the _location_ where a module's interface lives. Where to put the seam is a design decision in its own right, distinct from what goes behind it. _Avoid_: boundary (overloaded by DDD's bounded context).
Analogy: the seam of a garment, where you can unpick and replace a piece without touching the rest.

**Adapter**: something concrete that satisfies an interface at a seam. It describes a _role_ (which slot it fills), not a substance (what it has inside).
Analogy: a travel plug adapter: the role is to fit, what is inside does not matter.

**Leverage**: what callers get from depth. More capability per unit of interface learned. One implementation pays off across N calls and M tests.

**Locality**: what maintainers get from depth. Changes, bugs, knowledge and verification concentrate in one place instead of spreading across callers. Fix it once and it is fixed everywhere.

## Deep vs shallow

**Deep module** = small interface + a lot of implementation:

```
┌──────────────────────┐
│  Small interface     │  ← Few public operations, simple parameters
├──────────────────────┤
│                      │
│ Deep implementation  │  ← Complex logic hidden
│                      │
└──────────────────────┘
```

**Shallow module** = large interface + little implementation (avoid it):

```
┌──────────────────────────────────┐
│       Large interface            │  ← Many functions, complex parameters
├──────────────────────────────────┤
│  Thin implementation             │  ← Just forwards
└──────────────────────────────────┘
```

When designing an interface, ask yourself:

- Can I reduce the number of public operations?
- Can I simplify the parameters?
- Can I hide more complexity inside?

## Principles

- **Depth is a property of the interface, not of the implementation.** A deep module can be made inside of small, replaceable pieces; they are just not part of the interface. A module can have **internal seams** (private, used by its own tests) in addition to the **external seam** of its interface.
- **The deletion test.** Imagine deleting the module. If the complexity disappears, it was a pass-through. If the complexity reappears in N callers, it earned its place.
- **The interface is the test surface.** Callers and tests cross the same seam. If you want to test _beyond_ the interface, the module probably has the wrong shape.
- **One adapter means a hypothetical seam. Two adapters mean a real one.** Do not introduce a seam (or an abstract interface) if nothing varies across it.

## Designing for testability

Good interfaces make testing natural:

1. **Accept dependencies, do not create them.**

   ```text
   // Testable
   processOrder(order, charger)

   // Hard to test
   processOrder(order):
       charger = newPaymentGatewayClient(env("KEY"))
       ...
   ```

2. **Return results, do not produce side effects.**

   ```text
   // Testable
   calculateDiscount(cart) -> Discount

   // Hard to test
   applyDiscount(cart):
       cart.total -= discount     // mutates the argument
   ```

3. **Small surface.** Fewer public operations = fewer tests needed. Fewer parameters = simpler test setup.

4. **Consumer-side interfaces.** Declare the interface where it is used, with the minimal operations that consumer needs.

## Relationships

- A **module** has exactly one **interface** (the surface it presents to callers and tests).
- **Depth** is a property of a **module**, measured against its **interface**.
- A **seam** is where a **module**'s **interface** lives.
- An **adapter** sits at a **seam** and satisfies the **interface**.
- **Depth** produces **leverage** for callers and **locality** for maintainers.

## Rejected approaches

- **Depth as the ratio of implementation lines to interface lines** (Ousterhout): it rewards inflating the implementation. Here we use depth as leverage.
- **"Interface" as a language's `interface` keyword or a class's public methods**: too narrow; here the interface includes everything the caller must know.
- **"Boundary"**: overloaded by DDD's bounded context. Say **seam** or **interface**.

## Going deeper

- **Deepening a group of modules according to their dependencies**: see [DEEPENING.md](DEEPENING.md) (dependency categories, seam discipline and testing that replaces instead of stacking).
- **Exploring alternative interfaces**: see [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md) (parallel subagents that design the interface in radically different ways to compare them).
