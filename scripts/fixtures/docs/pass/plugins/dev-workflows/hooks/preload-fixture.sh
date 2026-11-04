#!/usr/bin/env bash
# Fixture stand-in for a keyed preload hook (check 24): prints the specs-context line on
# `/fixture-keyed <address>`, its key test a deliberate superset of the key grammar, and
# nothing on free text. Leading flags are skipped first, a bare --enforce-model together with
# the token after it, so an address behind a run flag is read as one.
command -v python3 >/dev/null 2>&1 || exit 0
prompt=$(python3 -c "
import sys, json
try:
    print(json.load(sys.stdin).get('prompt') or '')
except Exception:
    print('')
" 2>/dev/null) || true
[[ "$prompt" =~ ^/fixture-keyed([[:space:]]+|$) ]] || exit 0
args="${prompt:${#BASH_REMATCH[0]}}"
while :; do
    args="${args#"${args%%[![:space:]]*}"}"
    if [[ "$args" =~ ^--enforce-model[[:space:]]+[^[:space:]]+ || "$args" =~ ^-[^[:space:]]* ]]; then
        args="${args:${#BASH_REMATCH[0]}}"
    else
        break
    fi
done
if [[ "$args" =~ ^[A-Z][A-Z0-9_-]*-[0-9] ]]; then
    echo "=== Auto-injected project context (specs workflow) ==="
fi
exit 0
