# Change coupling from git

What changes together belongs together. Git history says what changes together more honestly than a diagram. The technique is known as temporal or change coupling analysis (popularized by Adam Tornhill in _Your Code as a Crime Scene_).

**Analogy:** it is looking at the dirt paths that formed in a park: they show where people really walk, not where the planner drew the sidewalks.

## Pairs of files that change together

From the repo root, last 12 months, ignoring merge commits:

```bash
git log --since="12 months ago" --no-merges --name-only --pretty=format:'--%h' \
| awk '/^--/{ if (n>1 && n<=30) for(i=1;i<=n;i++) for(j=i+1;j<=n;j++) print f[i]" | "f[j]; n=0; next }
       NF{ f[++n]=$0 }
       END{ if (n>1 && n<=30) for(i=1;i<=n;i++) for(j=i+1;j<=n;j++) print f[i]" | "f[j] }' \
| sort | uniq -c | sort -rn | head -30
```

Commits with more than 30 files are ignored because they are usually mass refactors or formatting changes that say nothing about coupling.

## Aggregated by folder or service

To see the coupling between modules or services instead of files, group by folder prefix:

```bash
git log --since="12 months ago" --no-merges --name-only --pretty=format:'--%h' \
| awk -F/ 'function flush(){ if (c<=30) for(i=1;i<=n;i++) for(j=i+1;j<=n;j++) print m[i]" | "m[j]; delete s; n=0; c=0 }
           /^--/{ flush(); next }
           NF>1{ c++; k=$1"/"$2; if(!(k in s)){ s[k]=1; m[++n]=k } }
           END{ flush() }' \
| sort | uniq -c | sort -rn | head -20
```

Adjust the depth (`$1"/"$2`) to the repo's structure (for example `internal/<context>` or `services/<service>`).

## How to read it

- **Pairs inside the same context**: expected; it confirms the boundary.
- **Frequent pairs across different contexts**: a sign that the boundary cuts through something that changes together, or that a Published Language is missing and schema changes propagate.
- **Across repositories**: if two services in different repos frequently need coordinated PRs, the same applies; look for it in the tickets or in the linked PRs.
- Combine it with data ownership and with language: change coupling is only one of the signals, and in a young system it has little history.
