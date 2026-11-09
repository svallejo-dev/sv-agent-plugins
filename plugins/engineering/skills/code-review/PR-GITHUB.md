# GitHub pull requests

How to fetch a PR to review it and, only if asked, post the review. Posting is a separate, explicit step because a review comment is public and notifies the author.

## Environment

```bash
gh auth status                 # installed and signed in?
gh api user --jq .login        # the current user, needed to post
```

Without `gh` (no shell or no session), ask the user to paste the diff or the PR description and review what they give you; mention `gh auth login` if they want the full flow. With a PR URL, pass `--repo <owner>/<repo>` to every `gh` call; with a bare number, `gh` uses the current repo (in a fork it may need `--repo <parent>`).

## Fetching the PR

```bash
gh pr view <n> --json number,url,title,body,author,isDraft,baseRefName,headRefName,headRefOid,isCrossRepository,additions,deletions,files
gh pr diff <n>                 # read it in full; on large PRs start with --name-only
gh pr checks <n>
```

The local working tree is almost never the PR's head (another branch, uncommitted changes), so never read the PR's files from there. When the diff does not give enough context, read files at the PR's head commit:

```bash
git fetch <remote> "pull/<n>/head"        # only updates FETCH_HEAD; does not check out
git show "<headRefOid>:path/to/file"
# without a local clone:
gh api "repos/<owner>/<repo>/contents/path/to/file?ref=<headRefOid>" -H "Accept: application/vnd.github.raw"
```

To build or test the PR, use a throwaway worktree instead of `gh pr checkout`, which would change the user's branch:

```bash
wt=$(mktemp -d "${TMPDIR:-/tmp}/pr-review.XXXXXX")
git worktree add --detach "$wt" "<headRefOid>"
# ... run the tests inside "$wt" ...
git worktree remove --force "$wt"
```

To give a language reviewer only its files: `gh pr diff <n> --name-only | grep -E '\.go$'` and then `git diff <base>...<headRefOid> -- <files>` after the fetch.

## Posting

Only when the user explicitly asks to publish, post or comment on the PR.

- **Event**: if the PR author is the current user, use `--comment` (GitHub rejects "request changes" on your own PR). Otherwise, `--request-changes` when there is any blocker or major, and `--comment` for the rest.
- **Never approve**, even if asked.
- Write the payloads to temporary files outside the repo so they are not committed by accident.

```bash
body=$(mktemp "${TMPDIR:-/tmp}/review.XXXXXX")
# write the review's markdown into "$body"
gh pr review <n> --comment --body-file "$body"      # or --request-changes
rm -f "$body"
```

Inline comments go through the reviews API in a single request. Each `line` must fall inside a diff hunk on the `RIGHT` (new) side, or GitHub answers 422; everything else goes in the summary body.

```bash
payload=$(mktemp "${TMPDIR:-/tmp}/review-json.XXXXXX")
cat > "$payload" <<'JSON'
{
  "commit_id": "<headRefOid>",
  "body": "Review summary. See inline comments.",
  "event": "COMMENT",
  "comments": [
    { "path": "internal/user/register_user.go", "line": 42, "side": "RIGHT",
      "body": "major: the error is discarded; wrap it: `return fmt.Errorf(\"find user %d: %w\", id, err)`" }
  ]
}
JSON
gh api --method POST "repos/<owner>/<repo>/pulls/<n>/reviews" --input "$payload"
rm -f "$payload"
```

`event` is `COMMENT` or `REQUEST_CHANGES`, with the same rule. Report the review's URL.
