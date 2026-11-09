# Fallback PR body

Use it only when the repo has no PR template and its recent PRs show no structure worth copying. Write it in the repo's language: in a repo written in another language, translate the headings (Summary, Why, What changed, Evidence, Merge danger, Issues) into that language.

## Template

~~~markdown
## Summary

<!-- One or two lines: what this PR does. Below, the smallest visual that makes the change clear (see visuals.md). -->

## Why

<!-- The problem it solves, the issue or ticket that asked for it, design decisions made. -->

## What changed

-

## Evidence

- **Before:** <failing test / output / screenshot>
  **After:** <passing test / output / screenshot>

```bash
# commands the reviewer can paste to verify it
```

## Merge danger

- **Door:** <one-way or two-way>
- **Blast radius:** <one word> · <possible consequences>
- **Migrations / flags:**
- **Rollback:**

## Issues

Closes #
~~~

Remove the sections that do not apply (nothing to link → no Issues section) instead of leaving them empty.

## How to fill each section

With `BASE_REF` defined as in SKILL.md (the fetched base, for example `origin/main`):

| Section | Source | Command |
|---|---|---|
| Summary | A synthesis of the commits, not a dump, plus a visual | `git log "$BASE_REF"..HEAD --format=%s` |
| Why | Commit bodies plus the linked issue, ticket or spec | `git log "$BASE_REF"..HEAD --format=%b` |
| What changed | One bullet per relevant change | `git log "$BASE_REF"..HEAD --format='- %s'` |
| Evidence | Real tests or commands on what was touched, with their output before and after | `git diff "$BASE_REF"...HEAD --stat` |
| Merge danger | Files touched, migrations, flags, contract changes | `git diff "$BASE_REF"...HEAD` |
| Issues | `Closes`/`Refs` footers of the commits | `git log "$BASE_REF"..HEAD --format=%b \| grep -iE '(closes\|fixes\|refs) #'` |

Two dots for the log (the branch's commits), three dots for the diff (against the merge base, so unrelated changes that reached the base do not show up).

## Guide

- **Evidence**: screenshots are best when the change is visual and the environment allows it. Next, execution evidence: the exact test that used to fail and now passes, console output, a metrics query before and after. "How to test" means commands that can be pasted, not "try the app".
- **Door**: you can come back through a two-way door; through a one-way door, you cannot. A PR that is cheap to revert is low risk. Destructive or hard-to-revert actions (migrations that delete data, partner contracts, events already published) are one-way doors. Analogy: a two-way door is moving furniture; a one-way door is knocking down a wall.
- **Blast radius**: the change's potential reach. Consider broken consumers, API contracts, events, performance, per-country configuration, feature flags.
- **Rollback**: if there are no migrations or flags, say so; the rollback is usually "revert the merge commit", unless a data migration makes it unsafe, and then explain it.
- Never include secrets, tokens or `.env` content.

## Example

Branch `feat/auth-refresh`, commits `feat(auth): add token refresh endpoint` and `test(auth): cover refresh happy path`.

**Title:** `feat(auth): add token refresh endpoint`

~~~markdown
## Summary

Adds `POST /auth/refresh` so clients can renew the access token without logging in again.

```text
Handler.Refresh
  sessions.FindByRefreshToken
  tokens.Issue
```

## Why

Sessions expired after an hour without warning and users were sent back to login mid-flow. Design agreed in #142.

## What changed

- New refresh endpoint on the existing `sessions` table
- Tests for the happy path and for an expired refresh token

## Evidence

- **Before:** `POST /auth/refresh` → 404
  **After:** `POST /auth/refresh` → 200 with a new access token

```bash
go test ./internal/auth/...
curl -sS -X POST localhost:8080/auth/refresh -H 'Authorization: Bearer <refresh-token>'
```

## Merge danger

- **Door:** two-way.
- **Blast radius:** contained · only `internal/auth`; if the refresh fails, clients go back to login.
- **Migrations / flags:** none.
- **Rollback:** revert the merge commit.

## Issues

Closes #142
~~~
