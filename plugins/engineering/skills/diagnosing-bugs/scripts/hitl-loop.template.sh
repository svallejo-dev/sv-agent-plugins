#!/usr/bin/env bash
# Reproduction loop with a human in the loop (HITL).
# Copy this file, edit the steps below and run it.
# The agent runs the script; the user follows the instructions in their terminal.
#
# Usage:
#   bash hitl-loop.template.sh
#
# Two helpers:
#   step "<instruction>"          → shows the instruction and waits for Enter
#   capture VAR "<question>"      → shows the question and stores the answer in VAR
#
# At the end, the captured values are printed as KEY=VALUE for the agent to read.
#
# `capture` prints its value in the terminal, where the agent reads it, so
# capture observations and leave signing in to the user as a `step`.

set -euo pipefail

step() {
  printf '\n>>> %s\n' "$1"
  read -r -p "    [Enter when you are done] " _
}

capture() {
  local var="$1" question="$2" answer
  printf '\n>>> %s\n' "$question"
  read -r -p "    > " answer
  printf -v "$var" '%s' "$answer"
}

# --- edit below ----------------------------------------------------------

step "Open the app at http://localhost:8080 and sign in."

capture FAILED "Press the 'Export' button. Did it fail? (y/n)"

capture MESSAGE "Paste the error message (or 'none'):"

# --- edit above ----------------------------------------------------------

printf '\n--- Captured ---\n'
printf 'FAILED=%s\n' "$FAILED"
printf 'MESSAGE=%s\n' "$MESSAGE"
