---
name: create-pr
description: "Redacta o abre un pull request de GitHub para la rama actual, siguiendo la plantilla, el estilo de título y el idioma del repo; si no hay, usa un título Conventional Commits y una plantilla con resumen visual, evidencia antes/después y riesgo de merge. Solo redactar, sin push: \\\"write a PR description\\\", \\\"redacta la descripción del PR\\\", \\\"draft the PR\\\". Hace push y gh pr create solo cuando se pide abrirlo: \\\"open a PR\\\", \\\"abre un PR\\\", \\\"haz un PR\\\", \\\"sube esto a review\\\". Commitea solo los archivos de la tarea, maneja forks y nunca mergea. Sin shell o sin gh, redacta el texto y los comandos."
license: MIT
---

# Create PR

Responde en español y conserva en inglés los términos técnicos habituales. El PR se escribe en el idioma que usan los PRs y commits del repo.

Un pull request debe explicarse solo: quien revisa entiende qué cambió, por qué, cómo verificarlo y qué podría romperse antes de leer código. El título dice el *qué* en una línea; el cuerpo, el *porqué* y el *cómo*, con la forma y el idioma que el repo ya usa.

## 1. Elige el modo

- **Redactar**: "redacta el PR", "write the PR description", un diff pegado, o no hay shell o `gh`. Reúne contexto en modo lectura (`git log`, `git diff`) y devuelve el título y el cuerpo, más los comandos que lo abrirían. No se commitea, no se hace push ni se crea nada, porque el usuario pidió texto.
- **Abrir**: "abre un PR", "open a PR", "sube esto a review". Sigue los pasos de abajo. Para y pregunta solo cuando algo es genuinamente ambiguo: qué cambios sin commitear pertenecen al PR, contra qué base va, o a qué remoto hacer push.

## 2. Preflight

```bash
sh <directorio de esta skill>/scripts/preflight.sh
```

Es de solo lectura e imprime líneas `clave=valor`. Las que importan aquí:

| Clave | Uso |
|---|---|
| `gh_installed=no`, `gh_authenticated=no` | Cambia a modo redactar y da los comandos `gh auth login` / `gh pr create`. |
| `remote`, `push_remote`, `is_fork`, `fork_parent`, `parent_remote`, `base_repo` | Dónde hacer push y dónde abrir el PR (paso 5). El remoto no siempre es `origin`. |
| `gh_default_branch` / `base_default_branch` | Base por defecto. |
| `on_default_branch`, `ahead`, `staged`, `unstaged`, `untracked` | Estado de rama y commits (paso 3). |
| `open_pr_for_branch` | Ya existe un PR: actualízalo en vez de abrir un duplicado. |
| `pr_template`, `contributing`, `commit_convention_config`, `history_style` | Convenciones de título y cuerpo (paso 6). |
| `operation_in_progress`, `conflicted` | Para y avisa al usuario. |

## 3. Deja los commits listos

**Base.** Gana el destino explícito del usuario; si no, la rama por defecto de `base_repo`. Haz fetch antes de comparar, para que el log y el diff reflejen el remoto real (un fetch solo actualiza las referencias remotas):

```bash
git fetch "$BASE_REMOTE" "$BASE"     # BASE_REMOTE: parent_remote en forks, si no remote
BASE_REF="$BASE_REMOTE/$BASE"
```

En un fork sin remoto que apunte al padre, haz fetch por URL y usa el commit traído: `git fetch https://github.com/<fork_parent>.git "$BASE"` y después `BASE_REF=FETCH_HEAD`.

**Rama.** Un PR necesita una rama head distinta de la base. Si estás en la rama por defecto, crea una con `git switch -c <nombre>`; tus commits locales se mueven con ella. Nómbrala como las ramas existentes del repo (`git branch -r`), si no `tipo/tema-corto`. Deja la rama por defecto local donde está y menciona que va adelantada al remoto; resetearla es decisión del usuario, porque un reset ahí puede descartar trabajo.

**Cambios sin commitear.** Commitea solo los archivos de esta tarea con la skill `git-commit` (mismas reglas: stage por ruta, convención de mensajes del repo, escaneo de secretos, sin `--no-verify`). No toques los cambios ajenos del usuario y lístalos en el informe. Si no sabes qué cambios pertenecen, pregunta.

## 4. Push

```bash
git push -u "$PUSH_REMOTE" "$BRANCH"
```

`PUSH_REMOTE` es `push_remote` del preflight (el fork del usuario en flujos con fork). Si la rama ya existe en remoto y divergió tras **tu propio** rebase, usa `git push --force-with-lease`; nunca `--force` a secas.

## 5. Abre (o actualiza) el PR

Si `open_pr_for_branch` muestra una URL, el push ya lo actualizó; informa la URL y edita título o cuerpo (`gh pr edit`) solo si el usuario lo pidió.

Si no:

```bash
body=$(mktemp "${TMPDIR:-/tmp}/pr-body.XXXXXX")
# escribe el cuerpo (paso 6) en "$body"
gh pr create --repo "$BASE_REPO" --base "$BASE" --head "$HEAD" \
  --title "$TITLE" --body-file "$body"
rm -f "$body"
```

- `HEAD` es `<rama>` en un PR del mismo repo y `<owner-del-fork>:<rama>` en un fork.
- Añade `--draft` cuando el usuario dijo WIP o borrador, o sabes que el trabajo está incompleto o falla un check. Si no, ábrelo listo para revisión.
- Añade reviewers, labels o assignees solo si el usuario lo pide; CODEOWNERS asigna reviewers por su cuenta.

## 6. Título y cuerpo

Las convenciones del repo mandan:

1. **Plantilla del repo**: `pr_template` del preflight (si es un directorio, elige la que encaje o pregunta). Conserva sus encabezados y checkboxes y rellena todas las secciones.
2. **PRs recientes**: muestran estilo de título, estructura e idioma: `gh pr list --repo "$BASE_REPO" --state merged --limit 10 --json title,body`. Si la historia de la rama por defecto termina los asuntos con `(#123)`, los PRs se hacen squash y el título se convierte en el asunto del commit, así que debe seguir la convención de commits (commitlint, CONTRIBUTING, `history_style`).
3. **Respaldo**: un título Conventional Commits y la plantilla de [references/pr-template.md](references/pr-template.md), que explica cómo rellenar cada sección a partir de `git log "$BASE_REF"..HEAD` y `git diff "$BASE_REF"...HEAD`. Su sección **Resumen** usa el menú de visuales de [references/visuales.md](references/visuales.md).

Aunque el repo tenga plantilla propia, si tiene una sección de resumen o descripción, puedes apoyarla con un visual de [references/visuales.md](references/visuales.md) cuando aclare el cambio.

Título: un commit → reutiliza su asunto; varios → una línea que resuma el cambio dominante. Enlaza issues con `Closes #N` o `Refs #N`; si el trabajo viene del tracker local, enlaza la ruta de la spec o del ticket (`.scratch/<feature>/...`). Si el entorno pide una línea de atribución al final de las descripciones de PR, inclúyela tal cual. Nunca pegues secretos, tokens ni contenido de `.env` en el título ni en el cuerpo.

## 7. Informe

La URL del PR, base ← head, borrador o listo, y lo que quedó fuera a propósito (archivos sin commitear, la rama por defecto local adelantada a su remoto).

## Guardarraíles

Límites duros, porque sus efectos llegan a otras personas:

- **Nunca mergees**: sin `gh pr merge`, sin `--auto`. Mergear es una decisión humana.
- **Nunca hagas force-push a una rama compartida**; `--force-with-lease` solo en tu propia rama.
- **Nunca commitees ni publiques secretos**, ni en commits ni en el texto del PR.
- **Nunca te saltes hooks ni firma** (`--no-verify`, `--no-gpg-sign`).
