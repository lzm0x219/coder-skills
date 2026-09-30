#!/usr/bin/env bash
# Usage: bash hitl-loop.sh "exact symptom" "step 1" ["step 2" ...]
# Prompts for an observation only. Never put passwords, tokens, or private data in arguments.
set -euo pipefail

if (( $# < 2 )); then
  printf 'Usage: bash %s "exact symptom" "step 1" ["step 2" ...]\n' "$0" >&2
  exit 2
fi

symptom=$1
shift
printf 'Symptom to check: %s\n' "$symptom"
step_number=0
for instruction in "$@"; do
  step_number=$((step_number + 1))
  printf '\nStep %s: %s\n' "$step_number" "$instruction"
  printf 'Press Enter after completing this step: '
  IFS= read -r _ || exit 2
done

while :; do
  printf '\nDid the exact symptom occur? [y/n/u for unknown]: '
  IFS= read -r answer || exit 2
  case "$answer" in
    y|Y) verdict=RED; status=1; break ;;
    n|N) verdict=GREEN; status=0; break ;;
    u|U) verdict=UNKNOWN; status=3; break ;;
    *) printf 'Enter y, n, or u.\n' >&2 ;;
  esac
done

printf 'Optional redacted observation (no secrets or personal data): '
IFS= read -r observation || exit 2
printf 'REPRO_VERDICT=%s\n' "$verdict"
printf 'REPRO_NOTE=%s\n' "$observation"
exit "$status"
