#!/usr/bin/env bash
# Loop de reproducción con humano en el loop (HITL).
# Copia este archivo, edita los pasos de abajo y ejecútalo.
# El agente ejecuta el script; el usuario sigue las instrucciones en su terminal.
#
# Uso:
#   bash hitl-loop.template.sh
#
# Dos helpers:
#   step "<instrucción>"          → muestra la instrucción y espera Enter
#   capture VAR "<pregunta>"      → muestra la pregunta y guarda la respuesta en VAR
#
# Al final, los valores capturados se imprimen como CLAVE=VALOR para que el agente los lea.
#
# `capture` imprime su valor en la terminal, donde lo lee el agente, así que
# captura observaciones y deja el inicio de sesión al usuario como un `step`.

set -euo pipefail

step() {
  printf '\n>>> %s\n' "$1"
  read -r -p "    [Enter cuando termines] " _
}

capture() {
  local var="$1" question="$2" answer
  printf '\n>>> %s\n' "$question"
  read -r -p "    > " answer
  printf -v "$var" '%s' "$answer"
}

# --- edita debajo --------------------------------------------------------

step "Abre la app en http://localhost:8080 e inicia sesión."

capture FALLO "Pulsa el botón 'Exportar'. ¿Dio error? (s/n)"

capture MENSAJE "Pega el mensaje de error (o 'ninguno'):"

# --- edita encima --------------------------------------------------------

printf '\n--- Capturado ---\n'
printf 'FALLO=%s\n' "$FALLO"
printf 'MENSAJE=%s\n' "$MENSAJE"
