# Pull requests de GitHub

Cómo obtener un PR para revisarlo y, solo si se pide, publicar la revisión. La publicación es un paso aparte y explícito porque un comentario de revisión es público y notifica al autor.

## Entorno

```bash
gh auth status                 # ¿instalado y con sesión?
gh api user --jq .login        # el usuario actual, necesario para publicar
```

Sin `gh` (sin shell o sin sesión), pide al usuario que pegue el diff o la descripción del PR y revisa lo que te dé; menciona `gh auth login` si quiere el flujo completo. Con una URL de PR, pasa `--repo <owner>/<repo>` a cada llamada de `gh`; con un número suelto, `gh` usa el repo actual (en un fork puede necesitar `--repo <padre>`).

## Obtener el PR

```bash
gh pr view <n> --json number,url,title,body,author,isDraft,baseRefName,headRefName,headRefOid,isCrossRepository,additions,deletions,files
gh pr diff <n>                 # léelo entero; en PRs grandes empieza con --name-only
gh pr checks <n>
```

El working tree local casi nunca es el head del PR (otra rama, cambios sin commitear), así que nunca leas de ahí los archivos del PR. Cuando el diff no dé suficiente contexto, lee archivos en el commit head del PR:

```bash
git fetch <remote> "pull/<n>/head"        # actualiza solo FETCH_HEAD; no hace checkout
git show "<headRefOid>:ruta/al/archivo"
# sin clon local:
gh api "repos/<owner>/<repo>/contents/ruta/al/archivo?ref=<headRefOid>" -H "Accept: application/vnd.github.raw"
```

Para compilar o testear el PR, usa un worktree desechable en vez de `gh pr checkout`, que cambiaría la rama del usuario:

```bash
wt=$(mktemp -d "${TMPDIR:-/tmp}/pr-review.XXXXXX")
git worktree add --detach "$wt" "<headRefOid>"
# ... ejecuta los tests dentro de "$wt" ...
git worktree remove --force "$wt"
```

Para pasar a un revisor de lenguaje solo sus archivos: `gh pr diff <n> --name-only | grep -E '\.go$'` y después `git diff <base>...<headRefOid> -- <archivos>` tras el fetch.

## Publicar

Solo cuando el usuario pida explícitamente publicar, postear o comentar en el PR.

- **Evento**: si el autor del PR es el usuario actual, usa `--comment` (GitHub rechaza "request changes" en tu propio PR). Si no, `--request-changes` cuando haya algún blocker o major, y `--comment` en el resto.
- **Nunca apruebes**, aunque te lo pidan.
- Escribe los payloads en archivos temporales fuera del repo para que no se commiteen por accidente.

```bash
body=$(mktemp "${TMPDIR:-/tmp}/review.XXXXXX")
# escribe el markdown de la revisión en "$body"
gh pr review <n> --comment --body-file "$body"      # o --request-changes
rm -f "$body"
```

Los comentarios en línea van por la API de reviews en una sola petición. Cada `line` debe caer dentro de un hunk del diff en el lado `RIGHT` (nuevo), o GitHub responde 422; lo demás va en el cuerpo del resumen.

```bash
payload=$(mktemp "${TMPDIR:-/tmp}/review-json.XXXXXX")
cat > "$payload" <<'JSON'
{
  "commit_id": "<headRefOid>",
  "body": "Resumen de la revisión. Ver comentarios en línea.",
  "event": "COMMENT",
  "comments": [
    { "path": "internal/user/register_user.go", "line": 42, "side": "RIGHT",
      "body": "major: se descarta el error; envuélvelo: `return fmt.Errorf(\"find user %d: %w\", id, err)`" }
  ]
}
JSON
gh api --method POST "repos/<owner>/<repo>/pulls/<n>/reviews" --input "$payload"
rm -f "$payload"
```

`event` es `COMMENT` o `REQUEST_CHANGES`, con la misma regla. Informa la URL de la revisión.
