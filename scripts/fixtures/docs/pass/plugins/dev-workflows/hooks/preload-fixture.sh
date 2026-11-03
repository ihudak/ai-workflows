#!/usr/bin/env bash
# Fixture stand-in for a keyed preload hook (check 24): prints the specs-context line on
# `/fixture-keyed <address>`, its key test a deliberate superset of the key grammar, and
# nothing on free text.
command -v python3 >/dev/null 2>&1 || exit 0
prompt=$(python3 -c "
import sys, json
try:
    print(json.load(sys.stdin).get('prompt') or '')
except Exception:
    print('')
" 2>/dev/null) || true
if [[ "$prompt" =~ ^/fixture-keyed[[:space:]]+[A-Z][A-Z0-9_-]*-[0-9] ]]; then
    echo "=== Auto-injected project context (specs workflow) ==="
fi
exit 0
