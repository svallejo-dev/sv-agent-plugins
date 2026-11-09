# Learning log format

Learning logs live in `./logs/` with sequential numbering: `0001-slug.md`, `0002-slug.md`, etc. Create the folder lazily: only when the first log is written.

They are the teaching equivalent of ADRs: they capture non-obvious lessons, key insights and declared prior knowledge that will guide future sessions. They are used to work out the zone of proximal development.

## Template

```md
# {Short title of what was learned or established}

{1-3 sentences: what was learned (or which prior knowledge was established) and why it matters for future sessions.}
```

That is the whole format. A log can be a single paragraph. The value is in recording _that_ this is already known and _why_ it changes what gets taught next.

## Optional sections

Include them only when they add real value.

- **Status** in frontmatter (`active | superseded by LL-NNNN`): useful when an earlier understanding turns out wrong and is replaced.
- **Evidence**: how the user demonstrated the understanding (a question answered, an exercise completed, prior experience cited).
- **Implications**: what it unlocks or rules out for future sessions, when that is not obvious.

## Numbering

Find the highest number in `./logs/` and add one.

## When to write a log

Write one when any of these conditions holds:

1. **The user demonstrated real understanding of something non-trivial**: not just exposure, but evidence they can use the concept correctly. It sets a new floor for what gets taught next.
2. **The user declared prior knowledge**: "I already know X". Record it so it is not taught again, along with the declared _depth_.
3. **A misconception was corrected**: the user believed something wrong and now sees why. These are very valuable: they predict future stumbles on related topics.
4. **The mission changed because of what was learned**: the user discovered they cared about something else. Link to `MISSION.md` and update it.

### What does not qualify

- Material that was only covered. Covering is not learning. Wait for the evidence.
- What is already in `GLOSSARY.md` as a definition. Do not duplicate.
- Per-session activity logs. Learning logs are not a diary: they are insights that decide.

## Superseding

When a later log contradicts an earlier one (the user's understanding deepened or was corrected), mark the old one with `Status: superseded by LL-NNNN` instead of deleting it. The history of how the understanding evolved is a useful signal in itself.
