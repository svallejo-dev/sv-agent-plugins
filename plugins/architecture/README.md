# architecture

Large-scale systems design of the `sv-agent-plugins` marketplace, built to start from a path already walked: the existing system, a similar documented one or, without metrics, the business archetype. Not having numbers never blocks: you work with order-of-magnitude scenarios and decision thresholds. It designs as a delta (current state → target → migration path), with numbers computed in code and a red team in parallel.

| Skill | What it does |
|---|---|
| `system-design` | Orchestrator in rounds: starting point, requirements as a delta, numbers, 2-3 alternatives, trade-offs with a measurable trigger, red team, migration, rubric. |
| `design-stress-test` | Parallel subagents per attack family (load, dependencies, data, changes, infrastructure, operations, abuse), seeded with real incidents and verified against the config. |
| `capacity-estimation` | A tested calculator (`scripts/capacity.py`): demand, projection from metrics, Little, utilization, fan-out, availability, shards, backlog, burn rate. |
| `strategic-design` | Subdomains, AS-IS and TO-BE context map with named patterns, change coupling from git. |
| `business-archetypes` | 11 business archetypes (streaming, fintech, ticketing, e-commerce, social, B2B SaaS, IoT, mobility, healthtech, AI platform, event platform) for designing without metrics: forces, invariants, subdomains, typical failures and PoC hypotheses. |
| `building-blocks` | A curated catalog of 19 building blocks from proyecto26/system-design-skills, without vendor files and with errors corrected (marked `[sv-skills]`). |

It does more with `general` (research, grilling) and `engineering` (domain-modeling for ADRs and the glossary) installed.

## Installation

See the [repository README](../../README.md#installation) for Claude Code, Codex, GitHub Copilot, Cursor and Windsurf. In short, with Claude Code:

```bash
claude plugin marketplace add svallejo-dev/sv-agent-plugins
claude plugin install architecture@sv-agent-plugins
```

Origin: the building-blocks catalog comes from [proyecto26/system-design-skills](https://github.com/proyecto26/system-design-skills) (MIT). All skills respond in the user's language. MIT license.
