#!/usr/bin/env bash
# Self-test of the status line's plan usage (workflows-core's statusline-command.sh),
# the opt-in WORKFLOWS_STATUSLINE_PLAN_USAGE=1 line drawn from a cached reply of the
# account's usage endpoint.
#
# Each case renders the shipped script with a HOME of its own that holds only the cache
# and a fresh fetch-attempt stamp, so no case reads a credential or reaches the network:
# the script fetches at most once every five minutes, timed by that stamp. It lives
# outside the plugin, so it never ships in a user's plugin cache. Needs bash, jq and
# python3 (to age a file portably).
#
# Usage: bash scripts/selftests/statusline_selftest.sh   — exit 0 when every case passes.
set -u

here=$(cd "$(dirname "$0")" && pwd)
SCRIPT="$here/../../plugins/workflows-core/scripts/statusline-command.sh"
[ -f "$SCRIPT" ] || { echo "statusline selftest: no script at $SCRIPT" >&2; exit 2; }
for tool in jq python3; do
  command -v "$tool" >/dev/null 2>&1 || { echo "statusline selftest: needs $tool" >&2; exit 2; }
done

work=$(mktemp -d "${TMPDIR:-/tmp}/statusline-selftest.XXXXXX")
trap 'rm -rf "$work"' EXIT
esc=$(printf '\033')
pass=0
fail=0

# The fields the script reads, in the shapes one account's reply carried on
# 2026-11-14: the plan's Fable limit only in `limits`, as a weekly_scoped entry.
cat > "$work/account.json" <<'JSON'
{
  "five_hour": null,
  "seven_day": {"utilization": 35.0, "resets_at": "2026-11-16T14:59:59.794445+00:00"},
  "seven_day_opus": null,
  "seven_day_sonnet": null,
  "some_internal_name": null,
  "extra_usage": {"is_enabled": false, "monthly_limit": null, "used_credits": null},
  "limits": [
    {"kind": "weekly_all", "group": "weekly", "percent": 35,
     "resets_at": "2026-11-16T14:59:59.794445+00:00", "scope": null, "is_active": true},
    {"kind": "weekly_scoped", "group": "weekly", "percent": 25,
     "resets_at": "2026-11-16T14:59:59.794629+00:00",
     "scope": {"model": {"id": null, "display_name": "Fable"}, "surface": null}, "is_active": false}
  ]
}
JSON
jq '. + {seven_day_fable: {utilization: 40.0, resets_at: "2026-11-16T14:59:59+00:00"}}' \
  "$work/account.json" > "$work/both.json"
jq '.limits += [{"kind":"weekly_scoped","percent":5,"scope":"weird"},
                {"kind":"weekly_scoped","percent":7,"scope":{"model":null,"surface":"cowork"}},
                {"kind":"session_scoped","percent":9,"scope":{"model":{"display_name":"Opus"}}},
                "junk"]' "$work/account.json" > "$work/odd.json"
jq '.limits = "notalist"' "$work/account.json" > "$work/notlist.json"
jq '.extra_usage = {"is_enabled":true,"monthly_limit":100000,"used_credits":42554,
                    "utilization":null,"currency":"USD","decimal_places":2}' \
  "$work/account.json" > "$work/budget.json"

PLAIN='{"session_id":"selftest","model":{"display_name":"Opus"},"workspace":{"current_dir":"/nonexistent"}}'
WITH7D='{"session_id":"selftest","model":{"display_name":"Opus"},"workspace":{"current_dir":"/nonexistent"},"rate_limits":{"seven_day":{"used_percentage":35,"resets_at":1794841199}}}'

# render <cache> <stdin-json> [age-seconds]: OUT = the last line, colours stripped; ERR = stderr
render() {
  local h
  h=$(mktemp -d "$work/home.XXXXXX")
  mkdir -p "$h/.claude/dev-workflows"
  cp "$1" "$h/.claude/dev-workflows/plan-usage.json"
  touch "$h/.claude/dev-workflows/plan-usage.attempt"
  if [ -n "${3:-}" ]; then
    python3 -c 'import os, sys, time; t = time.time() - int(sys.argv[2]); os.utime(sys.argv[1], (t, t))' \
      "$h/.claude/dev-workflows/plan-usage.json" "$3"
  fi
  OUT=$(printf '%s' "$2" | env -u CLAUDE_CONFIG_DIR HOME="$h" WORKFLOWS_STATUSLINE_PLAN_USAGE=1 \
        bash "$SCRIPT" 2>"$h/stderr" | sed "s/${esc}\[[0-9;]*m//g" | tail -n 1)
  ERR=$(cat "$h/stderr")
  rm -rf "$h"
}

check() { # check <name> <command over $OUT and $ERR>
  if eval "$2"; then
    pass=$((pass + 1)); echo "ok   $1"
  else
    fail=$((fail + 1)); echo "FAIL $1"; echo "     line:   $OUT"
    [ -n "$ERR" ] && echo "     stderr: $(printf '%s' "$ERR" | head -c 300)"
  fi
}
has() { printf '%s' "$OUT" | grep -qE "$1"; }
count() { printf '%s' "$OUT" | grep -oE "$1" | wc -l | tr -d ' '; }

# A bare 7d bar: "7d" not preceded by a dash, so 7d-fable is not one.
BARE7D='(^|[^-])7d [^ ]+ [0-9]+%'

render "$work/account.json" "$PLAIN"
check "a cached reply renders with nothing on stderr (GNU stat reads -f as file-system status)" '[ -z "$ERR" ]'
check "the weekly window is drawn"                         'has "(^|[^-])7d [^ ]+ 35%"'
check "a limit listed only in limits is drawn as 7d-fable" 'has "7d-fable [^ ]+ 25%"'
check "its reset is drawn"                                 'has "7d-fable [^|]*resets"'

render "$work/account.json" "$WITH7D"
check "a 7d window Claude Code passed is not drawn twice"  '[ "$(count "$BARE7D")" = 1 ]'
check "7d-fable is drawn beside it"                        'has "7d-fable"'

render "$work/both.json" "$PLAIN"
check "a window sent in both forms is drawn once"          '[ "$(count "7d-fable")" = 1 ]'
check "the seven_day_* field is the one drawn"             'has "7d-fable [^ ]+ 40%"'

render "$work/odd.json" "$PLAIN"
check "malformed limits entries put nothing on stderr"     '[ -z "$ERR" ]'
check "malformed limits entries leave the rest drawn"      'has "7d-fable" && has "$BARE7D"'
check "an unknown kind or a scope with no model is not drawn" '! has "cowork|weird|-opus"'

render "$work/notlist.json" "$PLAIN"
check "limits that is no list leaves the rest drawn"       'has "$BARE7D"'

render "$work/budget.json" "$PLAIN"
check "a monthly budget draws its usage bar"               'has "usage [^ ]+ 43% [$]425[.]54 / [$]1000[.]00 monthly"'

render "$work/account.json" "$PLAIN" 4000
check "a cache over an hour old is not drawn"              '! has "7d"'

echo "statusline selftest: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
