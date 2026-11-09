# RESOURCES.md format

`RESOURCES.md` is the curated set of trustworthy sources for the topic. The knowledge in the explanations comes from here, not from parametric guesses. The wisdom comes from the communities listed here.

## Structure

```md
# Resources: {Topic}

## Knowledge

- [Book: _Concurrency in Go_, by Katherine Cox-Buday](https://example.com)
  Reference text on goroutines, channels and patterns. Use it for: pipelines, cancellation, fan-out/fan-in.
- [Official doc: "The Go Memory Model"](https://go.dev/ref/mem)
  Canonical definition of happens-before in Go. Use it for: data races, synchronization.

## Wisdom (communities)

- [Gophers Slack, #performance channel](https://example.com)
  Active, moderated community. Use it for: reviewing concurrency designs and pprof profiles.
- Local: the city's Go meetup
  Use it for: in-person feedback on talks or designs.
```

## Rules

- **High trust only.** Prefer primary sources, recognized experts, peer-reviewed work and well-moderated communities. If a resource is marketing dressed up as education, leave it out.
- **Annotate each entry.** A bare link is useless in three months. Add one line: what it covers and when to use it.
- **Group into Knowledge / Wisdom.** It mirrors the philosophy of [SKILL.md](./SKILL.md). A resource can be in only one group.
- **Make the gaps visible.** If no good resource exists for an area the mission needs, add a `## Gaps` section with what is missing. It guides future searches.
- **Prune ruthlessly.** A resource that turned out wrong, shallow or off-mission is removed, not buried. Five good sources are better than thirty mediocre ones.
- **Record community preferences.** If the user decided not to join communities, write it down so future sessions do not insist.
