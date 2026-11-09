#!/usr/bin/env bash
# Conecta un único archivo de reglas personales (~/.agents/AGENTS.md por defecto) con el
# archivo de instrucciones globales de cada herramienta, para que todas carguen las mismas
# reglas en cualquier proyecto.
#
#   Claude Code  ~/.claude/CLAUDE.md                          (se añade la línea @<fuente>)
#   Codex        ~/.codex/AGENTS.md                            (enlace simbólico)
#   Copilot CLI  ~/.copilot/copilot-instructions.md            (enlace simbólico)
#   Windsurf     ~/.codeium/windsurf/memories/global_rules.md  (enlace simbólico; máximo 6 000 caracteres)
#   Cursor       sin archivo: se pega en Settings → Rules → User Rules (el script lo indica)
#
# Uso:
#   tools/instalar-reglas-globales.sh [--fuente RUTA] [--herramientas claude,codex,copilot,windsurf]
#                                     [--force] [--dry-run]
#
# Si la fuente no existe, se crea a partir de plantillas/reglas-globales.md para que la edites.
# Nunca reemplaza un archivo de instrucciones existente sin --force; con --force deja una copia .bak.

set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FUENTE="$HOME/.agents/AGENTS.md"
HERRAMIENTAS="claude,codex,copilot,windsurf"
FORCE=0 DRY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --fuente) FUENTE="${2:-}"; shift 2 ;;
    --herramientas) HERRAMIENTAS="${2:-}"; shift 2 ;;
    --force) FORCE=1; shift ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "opción desconocida: $1" >&2; exit 2 ;;
  esac
done

hacer() { if [[ $DRY -eq 1 ]]; then echo "  (dry-run) $*"; else "$@"; fi; }

if [[ ! -f "$FUENTE" ]]; then
  echo "Creando $FUENTE desde la plantilla: edítala con tus reglas."
  hacer mkdir -p "$(dirname "$FUENTE")"
  hacer cp "$RAIZ/plantillas/reglas-globales.md" "$FUENTE"
fi

enlazar() {  # $1 = destino
  local destino="$1"
  if [[ -L "$destino" && "$(readlink "$destino")" == "$FUENTE" ]]; then
    echo "  ya enlazado: $destino"; return
  fi
  if [[ -e "$destino" || -L "$destino" ]]; then
    if [[ $FORCE -eq 0 ]]; then
      echo "  OMITIDO: $destino ya existe y no es un enlace a la fuente. Une su contenido con $FUENTE y vuelve a ejecutar con --force."
      return
    fi
    hacer mv "$destino" "$destino.bak"
    echo "  copia de seguridad: $destino.bak"
  fi
  hacer mkdir -p "$(dirname "$destino")"
  hacer ln -s "$FUENTE" "$destino"
  echo "  enlazado: $destino → $FUENTE"
}

IFS=',' read -r -a LISTA <<< "$HERRAMIENTAS"
for h in "${LISTA[@]}"; do
  case "$h" in
    claude)
      echo "Claude Code"
      destino="$HOME/.claude/CLAUDE.md"; linea="@$FUENTE"
      if [[ -f "$destino" ]] && grep -qxF "$linea" "$destino"; then
        echo "  ya importa la fuente: $destino"
      else
        hacer mkdir -p "$(dirname "$destino")"
        if [[ $DRY -eq 1 ]]; then echo "  (dry-run) añadir '$linea' a $destino"; else printf '%s\n' "$linea" >> "$destino"; fi
        echo "  importado en: $destino"
      fi ;;
    codex)    echo "Codex";       enlazar "$HOME/.codex/AGENTS.md" ;;
    copilot)  echo "Copilot CLI"; enlazar "$HOME/.copilot/copilot-instructions.md" ;;
    windsurf)
      echo "Windsurf"
      if [[ -f "$FUENTE" ]] && [[ $(wc -m < "$FUENTE") -gt 6000 ]]; then
        echo "  AVISO: la fuente supera los 6 000 caracteres que admite Windsurf para reglas globales; recórtala o Windsurf la truncará."
      fi
      enlazar "$HOME/.codeium/windsurf/memories/global_rules.md" ;;
    cursor) ;;  # sin archivo global: se informa al final
    *) echo "herramienta desconocida: $h (claude, codex, copilot, windsurf, cursor)" >&2; exit 2 ;;
  esac
done

echo "Cursor: no usa un archivo global; copia el contenido de $FUENTE en Settings → Rules → User Rules."
echo "Abre una sesión nueva en cada herramienta para que cargue las reglas."
