#!/usr/bin/env bash
# Instala las skills de uno o varios plugins en la carpeta de skills de una herramienta.
# Es la vía para Windsurf (que no tiene sistema de plugins) y la alternativa para
# cualquier herramienta compatible con el estándar Agent Skills.
#
# Uso:
#   ./install.sh --tool <claude|codex|copilot|cursor|windsurf> [--scope user|project]
#                [--plugins qa,ingenieria,...] [--project-dir DIR] [--link] [--force] [--dry-run]
#   ./install.sh --dest <carpeta-de-skills> [--plugins ...] [--link] [--force] [--dry-run]
#
# Por defecto instala todos los plugins, copia (no enlaza) y en el alcance "project"
# usa el directorio actual. Nunca sobrescribe una skill ajena sin --force.

set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL="" SCOPE="project" PLUGINS="" DEST="" PROJECT_DIR="$PWD" LINK=0 FORCE=0 DRY=0

uso() { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }
error() { echo "error: $*" >&2; exit 2; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tool) TOOL="${2:-}"; shift 2 ;;
    --scope) SCOPE="${2:-}"; shift 2 ;;
    --plugins) PLUGINS="${2:-}"; shift 2 ;;
    --dest) DEST="${2:-}"; shift 2 ;;
    --project-dir) PROJECT_DIR="${2:-}"; shift 2 ;;
    --link) LINK=1; shift ;;
    --force) FORCE=1; shift ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) uso 0 ;;
    *) echo "opción desconocida: $1" >&2; uso 2 ;;
  esac
done

if [[ -z "$DEST" ]]; then
  [[ -n "$TOOL" ]] || error "indica --tool o --dest"
  [[ "$SCOPE" == "user" || "$SCOPE" == "project" ]] || error "--scope debe ser user o project"
  case "$TOOL:$SCOPE" in
    claude:project)   DEST="$PROJECT_DIR/.claude/skills" ;;
    claude:user)      DEST="$HOME/.claude/skills" ;;
    codex:project)    DEST="$PROJECT_DIR/.agents/skills" ;;
    codex:user)       DEST="$HOME/.agents/skills" ;;
    copilot:project)  DEST="$PROJECT_DIR/.github/skills" ;;
    copilot:user)     error "para Copilot a nivel de usuario instala como plugin: copilot plugin install <plugin>@sv-agent-plugins" ;;
    cursor:project)   DEST="$PROJECT_DIR/.cursor/skills" ;;
    cursor:user)      DEST="$HOME/.cursor/skills" ;;
    windsurf:project) DEST="$PROJECT_DIR/.windsurf/skills" ;;
    windsurf:user)    DEST="$HOME/.codeium/windsurf/skills" ;;
    *) error "herramienta no soportada: $TOOL (usa --dest para otra carpeta de skills)" ;;
  esac
fi

DISPONIBLES=$(cd "$RAIZ/plugins" && ls -d */ | tr -d '/')
if [[ -z "$PLUGINS" ]]; then PLUGINS=$(echo "$DISPONIBLES" | tr '\n' ','); fi

IFS=',' read -r -a LISTA <<< "$PLUGINS"
SKILLS=()
for p in "${LISTA[@]}"; do
  [[ -z "$p" ]] && continue
  [[ -d "$RAIZ/plugins/$p/skills" ]] || error "plugin desconocido: $p (disponibles: $(echo $DISPONIBLES))"
  for s in "$RAIZ/plugins/$p/skills"/*/; do
    [[ -f "$s/SKILL.md" ]] && SKILLS+=("${s%/}")
  done
done
[[ ${#SKILLS[@]} -gt 0 ]] || error "no hay skills que instalar"

# Comprobación previa: no pisar skills ajenas
for s in "${SKILLS[@]}"; do
  nombre=$(basename "$s"); destino="$DEST/$nombre"
  if [[ -e "$destino" && $FORCE -eq 0 ]]; then
    if [[ ! -f "$destino/.sv-agent-plugins" && ! -L "$destino" ]]; then
      error "ya existe $destino y no la instaló este repositorio; usa --force para reemplazarla"
    fi
  fi
done

echo "Instalando ${#SKILLS[@]} skills en $DEST ($([[ $LINK -eq 1 ]] && echo enlaces || echo copias))"
[[ $DRY -eq 1 ]] && { for s in "${SKILLS[@]}"; do echo "  $(basename "$s")"; done; echo "(dry-run: no se escribió nada)"; exit 0; }

mkdir -p "$DEST"
for s in "${SKILLS[@]}"; do
  nombre=$(basename "$s"); destino="$DEST/$nombre"
  rm -rf "$destino"
  if [[ $LINK -eq 1 ]]; then
    ln -s "$s" "$destino"
  else
    cp -R "$s" "$destino"
    find "$destino" -name '__pycache__' -prune -exec rm -rf {} +
    echo "instalado desde $RAIZ" > "$destino/.sv-agent-plugins"
  fi
  echo "  $nombre"
done
echo "Listo. Reinicia la herramienta o abre una sesión nueva para que detecte las skills."
