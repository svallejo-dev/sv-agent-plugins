---
name: create-pr
description: "Drafts or opens a GitHub pull request for the current branch, following the repo's template, title style and language; if there are none, it uses a Conventional Commits title and a template with a visual summary, before/after evidence and merge risk. Draft only, no push: \"write a PR description\", \"draft the PR\". It pushes and runs gh pr create only when asked to open it: \"open a PR\", \"make a PR\", \"send this to review\". It commits only the task's files, handles forks and never merges. Without a shell or gh, it drafts the text and the commands."
license: MIT
---

# Create PR

Respond in the user's language; keep common technical terms in English. The PR is written in the language the repo's PRs and commits use.

A pull request must explain itself: the reviewer understands what changed, why, how to verify it and what could break before reading any code. The title says the *what* in one line; the body, the *why* and the *how*, with the shape and language the repo already uses.

## 1. Choose the mode

- **Draft**: "draft the PR", "write the PR description", a pasted diff, or there is no shell or `gh`. Gather context in read-only mode (`git log`, `git diff`) and return the title and the body, plus the commands that would open it. Nothing is committed, pushed or created, because the user asked for text.
- **Open**: "open a PR", "send this to review". Follow the steps below. Stop and ask only when something is genuinely ambiguous: which uncommitted changes belong to the PR, which base it targets, or which remote to push to.

## 2. Preflight

```bash
sh <this skill's directory>/scripts/preflight.sh
```

It is read-only and prints `key=value` lines. The ones that matter here:

| Key | Use |
|---|---|
| `gh_installed=no`, `gh_authenticated=no` | Switch to draft mode and give the `gh auth login` / `gh pr create` commands. |
| `remote`, `push_remote`, `is_fork`, `fork_parent`, `parent_remote`, `base_repo` | Where to push and where to open the PR (step 5). The remote is not always `origin`. |
| `gh_default_branch` / `base_default_branch` | Default base. |
| `on_default_branch`, `ahead`, `staged`, `unstaged`, `untracked` | Branch and commit state (step 3). |
| `open_pr_for_branch` | A PR already exists: update it instead of opening a duplicate. |
| `pr_template`, `contributing`, `commit_convention_config`, `history_style` | Title and body conventions (step 6). |
| `operation_in_progress`, `conflicted` | Stop and tell the user. |

## 3. Get the commits ready

**Base.** The user's explicit target wins; otherwise, the default branch of `base_repo`. Fetch before comparing, so the log and the diff reflect the real remote (a fetch only updates the remote refs):

```bash
git fetch "$BASE_REMOTE" "$BASE"     # BASE_REMOTE: parent_remote in forks, otherwise remote
BASE_REF="$BASE_REMOTE/$BASE"
```

In a fork with no remote pointing to the parent, fetch by URL and use the fetched commit: `git fetch https://github.com/<fork_parent>.git "$BASE"` and then `BASE_REF=FETCH_HEAD`.

**Branch.** A PR needs a head branch distinct from the base. If you are on the default branch, create one with `git switch -c <name>`; your local commits move with it. Name it like the repo's existing branches (`git branch -r`), otherwise `type/short-topic`. Leave the local default branch where it is and mention that it is ahead of the remote; resetting it is the user's decision, because a reset there can discard work.

**Uncommitted changes.** Commit only this task's files with the `git-commit` skill (same rules: stage by path, the repo's message convention, secret scan, no `--no-verify`). Do not touch the user's unrelated changes and list them in the report. If you do not know which changes belong, ask.

## 4. Push

```bash
git push -u "$PUSH_REMOTE" "$BRANCH"
```

`PUSH_REMOTE` is the preflight's `push_remote` (the user's fork in fork workflows). If the branch already exists on the remote and diverged after **your own** rebase, use `git push --force-with-lease`; never a bare `--force`.

## 5. Open (or update) the PR

If `open_pr_for_branch` shows a URL, the push already updated it; report the URL and edit the title or body (`gh pr edit`) only if the user asked.

If not:

```bash
body=$(mktemp "${TMPDIR:-/tmp}/pr-body.XXXXXX")
# write the body (step 6) into "$body"
gh pr create --repo "$BASE_REPO" --base "$BASE" --head "$HEAD" \
  --title "$TITLE" --body-file "$body"
rm -f "$body"
```

- `HEAD` is `<branch>` for a same-repo PR and `<fork-owner>:<branch>` for a fork.
- Add `--draft` when the user said WIP or draft, or you know the work is incomplete or a check fails. Otherwise, open it ready for review.
- Add reviewers, labels or assignees only if the user asks; CODEOWNERS assigns reviewers on its own.

## 6. Title and body

The repo's conventions win:

1. **Repo template**: the preflight's `pr_template` (if it is a directory, pick the one that fits or ask). Keep its headings and checkboxes and fill every section.
2. **Recent PRs**: they show the title style, structure and language: `gh pr list --repo "$BASE_REPO" --state merged --limit 10 --json title,body`. If the default branch's history ends subjects with `(#123)`, PRs are squashed and the title becomes the commit subject, so it must follow the commit convention (commitlint, CONTRIBUTING, `history_style`).
3. **Fallback**: a Conventional Commits title and the template in [references/pr-template.md](references/pr-template.md), which explains how to fill each section from `git log "$BASE_REF"..HEAD` and `git diff "$BASE_REF"...HEAD`. Its **Summary** section uses the menu of visuals in [references/visuals.md](references/visuals.md).

Even when the repo has its own template, if it has a summary or description section, you can support it with a visual from [references/visuals.md](references/visuals.md) when it clarifies the change.

Title: one commit → reuse its subject; several → one line that summarizes the dominant change. Link issues with `Closes #N` or `Refs #N`; if the work comes from the local tracker, link the path of the spec or the ticket (`.scratch/<feature>/...`). If the environment asks for an attribution line at the end of PR descriptions, include it as is. Never paste secrets, tokens or `.env` content into the title or the body.

## 7. Report

The PR's URL, base ← head, draft or ready, and what was left out on purpose (uncommitted files, the local default branch ahead of its remote).

## Guardrails

Hard limits, because their effects reach other people:

- **Never merge**: no `gh pr merge`, no `--auto`. Merging is a human decision.
- **Never force-push to a shared branch**; `--force-with-lease` only on your own branch.
- **Never commit or publish secrets**, neither in commits nor in the PR text.
- **Never skip hooks or signing** (`--no-verify`, `--no-gpg-sign`).
