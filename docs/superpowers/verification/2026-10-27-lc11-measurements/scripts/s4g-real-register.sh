#!/usr/bin/env bash
# Scenario 4g — the same stop, settled by the REAL `register.py rebuild` on genuine run records.
. "$(dirname "$0")/lib.sh"
git --version
REGPY=/workspace/ai-workflows/plugins/security-workflows/scripts/register.py
RR="python3 -I $ROOT/real_register.py"
W=$ROOT/work/s4g; setup_repos "$W"
C1=$($RR code "$W"); echo "code repo $W/code at $C1"
$RR scan "$W/seed" "$W/code" s0 v3:p0 src/b.py 1 2026-10-16T08:00:00Z
git -C "$W/seed" add -A -- security/code; git -C "$W/seed" commit -q -m "NOISSUE base register"; git -C "$W/seed" push -q origin main
for c in A B; do git -C "$W/$c" pull -q --no-rebase origin main; done
install_attrs "$W/A"
say "A records scan sA (not pushed); B records scan sB and pushes first"
$RR scan "$W/A" "$W/code" sA v3:pa src/a.py 10 2026-10-16T09:00:00Z
git -C "$W/A" add -A -- security/code; git -C "$W/A" commit -q -m "NOISSUE Add dev-workflows session artifacts (/security-workflows:scan)" -- security/code
$RR scan "$W/B" "$W/code" sB v3:pb src/a.py 30 2026-10-16T09:05:00Z
git -C "$W/B" add -A -- security/code; git -C "$W/B" commit -q -m "NOISSUE Add dev-workflows session artifacts (/security-workflows:scan)" -- security/code
git -C "$W/B" push -q origin main
run git -C "$W/A" push --porcelain origin main
run git -C "$W/A" fetch -q origin
run python3 -I "$ROOT/push_scope.py" "$W/A" main refs/remotes/origin/main
say "rebase; at the stop, the real rebuild"
run git -C "$W/A" rebase origin/main
run git -C "$W/A" status --short
echo "runs/ in the worktree at the stop:"; ls "$W/A/security/code/runs"
echo "scans/ in the worktree at the stop:"; ls "$W/A/security/code/scans"
run python3 -I "$REGPY" rebuild --specs "$W/A" --slug code
run git -C "$W/A" add -- security/code/register.json security/code/register.md
run git -C "$W/A" rebase --continue
run git -C "$W/A" push --porcelain origin main
say "is the pushed register exactly what a rebuild of the pushed records gives?"
T=$(mktemp -d "$ROOT/work/chk.XXXX"); git -C "$W/origin.git" archive main security/code | tar -x -C "$T"
cp "$T/security/code/register.json" "$T/c.json"; cp "$T/security/code/register.md" "$T/c.md"
python3 -I "$REGPY" rebuild --specs "$T" --slug code >/dev/null
cmp "$T/c.json" "$T/security/code/register.json" && cmp "$T/c.md" "$T/security/code/register.md" && echo "YES: register.json and register.md == rebuild(runs/, scans/) at origin/main"
grep -E '^\| \[SEC#' "$T/security/code/register.md" | cut -c1-120
rm -rf "$T"
