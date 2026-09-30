#!/usr/bin/env bash
# Fires after every Bash tool call. Detects test suite commands, parses results, notifies.
# Always exits 0 — must never block Claude.

# Guard: if python3 is not available, skip silently
command -v python3 &>/dev/null || exit 0

input=$(cat)

command=$(echo "$input" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    # Claude Code's PostToolUse payload nests these under tool_input / tool_response.
    # Fall back to top-level keys for older versions or non-standard runners.
    cmd = (d.get('tool_input') or {}).get('command', '') or d.get('command', '')
    print(cmd)
except Exception:
    print('')
" 2>/dev/null) || true

output=$(echo "$input" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    out = (d.get('tool_response') or {}).get('output', '') or d.get('output', '')
    print(out)
except Exception:
    print('')
" 2>/dev/null) || true

# Exit early if this wasn't a test command.
# A wrapper needs its own alternation: these are substrings, and "mvnw test"
# does not contain "mvn test" any more than "gradlew test" contains "gradle
# test" — which is why that one was already spelled out. Maven's was not, so
# the ./mvnw test most Maven projects actually run never notified.
if ! echo "$command" | grep -qE '(mvnw test|mvn test|gradlew test|gradle test|npm test|yarn test|pytest|make test)'; then
    exit 0
fi

# Parse result using python3 (portable — no grep -P)
# $output is piped via stdin to avoid ARG_MAX limits on large test outputs.
# The parser program therefore CANNOT come from a here-document on the same
# command: a here-document and a pipe compete for fd 0 and the here-document
# wins, so `python3 -` would read the program and the parser would see no
# output at all. Capture the program first, pass it with -c, leave fd 0 to the
# pipe. Under -c, sys.argv[1] is still the first argument after the program.
parser=$(cat <<'PYEOF'
import sys, re

cmd = sys.argv[1] if len(sys.argv) > 1 else ""
out = sys.stdin.read()

# first() and sumall() return None, never "0", where the pattern did not match
# at all — a count the parser could not read must never be notified as a
# measured one. Every runner behind "npm test" that is not jest prints no
# "Tests:" line, and a green Gradle run prints no "N tests completed" line, so
# a zero default put a genuinely red suite on screen as "0 failed", which reads
# exactly like a green one. counts() turns a set of lookups into the numbers to
# report, or into None where every one of them missed: a miss beside a hit IS a
# real zero, because a runner omits the clause for a zero from a summary it did
# print, but a miss beside nothing at all is no measurement.
def first(pattern, text):
    m = re.findall(pattern, text)
    return m[-1] if m else None

def sumall(pattern, text):
    vals = [int(x) for x in re.findall(pattern, text) if x.isdigit()]
    return str(sum(vals)) if vals else None

def counts(*found):
    if all(v is None for v in found):
        return None
    return ["0" if v is None else v for v in found]

if "mvn" in cmd:
    # Surefire prints a "Tests run:" line per test class AND a summary line per
    # module under "Results:". A per-class line continues past "Skipped: N" with
    # a time/class suffix (TestSetStats.getTestSetSummary always appends the
    # elapsed time and " -- in <class>"); a summary line ends at "Skipped: N",
    # or at ", Flakes: N" where any test flaked — RunStatistics.getSummary()
    # appends that one suffix and only when flakes > 0. Matching both endings at
    # end of line sums modules without counting every class a second time. Where
    # nothing matches that anchored form, fall back to the unanchored counts.
    rows = re.findall(
        r"Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: \d+"
        r"(?:, Flakes: \d+)?[ \t]*\r?$",
        out, re.M)
    if rows:
        c = [str(sum(int(r[i]) for r in rows)) for i in range(3)]
    else:
        c = counts(sumall(r"Tests run: (\d+)", out),
                   sumall(r"Failures: (\d+)", out),
                   sumall(r"Errors: (\d+)", out))
    line = f"{c[0]} run, {c[1]} failed, {c[2]} errors" if c else None
elif "gradlew" in cmd or "gradle" in cmd:
    # A multi-project build prints ONE summary per subproject, so these are sums,
    # not first(). first() returns m[-1] -- the LAST match -- which reported only
    # the final subproject's numbers and silently dropped a failing earlier one:
    # a red build could be notified as green. The failed count is read out of each
    # matched line's own trailing clauses rather than by a bare ", N failed" scan,
    # so a stray clause elsewhere in the log is not summed into the total. A green
    # Gradle run prints no summary line at all, so no match means no measurement
    # (None), exactly as before.
    _g = re.findall(r"(\d+) tests? completed((?:, \d+ (?:failed|skipped))*)", out)
    _done = str(sum(int(n) for n, _ in _g)) if _g else None
    _failed = (str(sum(int(n) for _, tail in _g
                       for n in re.findall(r", (\d+) failed", tail))) if _g else None)
    c = counts(_done, _failed)
    line = f"{c[0]} completed, {c[1]} failed" if c else None
elif "pytest" in cmd:
    c = counts(first(r"(\d+) passed", out),
               first(r"(\d+) failed", out))
    line = f"{c[0]} passed, {c[1]} failed" if c else None
elif "npm" in cmd or "yarn" in cmd:
    c = counts(first(r"Tests:.*?(\d+) passed", out),
               first(r"Tests:.*?(\d+) failed", out))
    line = f"{c[0]} passed, {c[1]} failed" if c else None
else:
    line = None

# One disposition for "this run produced no count I can read", shared by an
# unrecognised command and by a recognised one whose output nothing matched.
print(line or "tests completed")
PYEOF
)

summary=$(printf '%s' "$output" | python3 -c "$parser" "$command" 2>/dev/null) || true

[[ -z "$summary" ]] && summary="tests completed"
message="Test run: $summary"

# Notify using platform-appropriate method
if [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e "display notification \"$message\" with title \"Claude Code\"" 2>/dev/null || true
elif grep -qi microsoft /proc/version 2>/dev/null; then
    wsl-notify-send --category "Claude Code" "$message" 2>/dev/null || \
    powershell.exe -Command \
      "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; \$n = New-Object System.Windows.Forms.NotifyIcon; \$n.Icon = [System.Drawing.SystemIcons]::Information; \$n.Visible = \$true; \$n.ShowBalloonTip(3000, 'Claude Code', '$message', [System.Windows.Forms.ToolTipIcon]::None); Start-Sleep -Milliseconds 3500; \$n.Dispose()" 2>/dev/null || \
    echo -e '\a'
else
    notify-send "Claude Code" "$message" 2>/dev/null || echo -e '\a'
fi

exit 0
