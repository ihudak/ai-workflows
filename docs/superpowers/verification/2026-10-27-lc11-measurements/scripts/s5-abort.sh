#!/usr/bin/env bash
# Scenario 5 — abort cleanliness: the decided path's abort after a register stop was already settled.
. "$(dirname "$0")/lib.sh"
git --version
# A: commit a1 (register run + append files), commit a2 (resume.md overwrite); B: register run + resume.md + a new file.
mk() {
  local w=$1; setup_repos "$w"; install_attrs "$w/A"
  printf -- '- a1 entry\n' >> "$w/A/$FB"; rec "$w/A" 2 2026-10-27T02:00:00Z a1a1a1a1 scan-a1:p1 "a1" open; rebuild "$w/A" >/dev/null
  git -C "$w/A" add -A -- "$FB" "$REG"; git -C "$w/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a1)" -- "$FB" "$REG"
  printf 'last: a2\n' > "$w/A/$RESUME"; git -C "$w/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a2)" -- "$RESUME"
  printf -- '- b1 entry\n' >> "$w/B/$FB"; printf 'last: b1\n' > "$w/B/$RESUME"; rec "$w/B" 2 2026-10-27T02:00:00Z b1b1b1b1 scan-b1:p1 "b1" open; rebuild "$w/B" >/dev/null
  printf 'B wrote this\n' > "$w/B/notes/new.md"
  git -C "$w/B" add -A; git -C "$w/B" commit -q -m "PRD-A-1 B: session files + notes/new.md"; git -C "$w/B" push -q origin main
  git -C "$w/A" fetch -q origin
}
mtimes() { (cd "$1" && git ls-files -z | xargs -0 stat -c '%n %y'); }

say "5a — clean checkout: stop 1 (register) settled by rebuild, stop 2 (resume.md) aborts"
W=$ROOT/work/s5a; mk "$W"
snap "$W/A" > "$W/before.snap"; mtimes "$W/A" > "$W/before.mt"
git -C "$W/A" reflog > "$W/reflog.before"; git -C "$W/A" reflog refs/heads/main > "$W/breflog.before"
sleep 1.1
settle "$W/A"
snap "$W/A" > "$W/after.snap"; mtimes "$W/A" > "$W/after.mt"
cmpsnap "$W/before.snap" "$W/after.snap"
echo "-- files whose mtime changed (content identical):"; diff "$W/before.mt" "$W/after.mt" | grep '^>' | sed 's/^> /   /'
echo "-- notes/new.md (B's, added during the rebase) present after abort? $(test -e "$W/A/notes/new.md" && echo yes || echo no)"
echo "-- HEAD reflog, new entries:"; git -C "$W/A" reflog | head -n $(( $(git -C "$W/A" reflog | wc -l) - $(wc -l < "$W/reflog.before") ))
echo "-- branch reflog changed? $(git -C "$W/A" reflog refs/heads/main | diff -q - "$W/breflog.before" >/dev/null && echo no || echo yes)"
echo "-- ORIG_HEAD == HEAD? $([ "$(git -C "$W/A" rev-parse ORIG_HEAD)" = "$(git -C "$W/A" rev-parse HEAD)" ] && echo yes || echo no)"
echo "-- leftovers in .git:"; ls "$W/A/.git" | grep -iE 'rebase|AUTO_MERGE|MERGE_|REBASE_HEAD|CHERRY' || echo "   none"
run git -C "$W/A" status
run git -C "$W/A" stash list

say "5b — the same with the user's dirty files and --autostash"
W=$ROOT/work/s5b; mk "$W"
printf 'user edit\n' >> "$W/A/$NOTE"; printf 'staged\n' >> "$W/A/$DELIV"; git -C "$W/A" add -- "$DELIV"; printf 'u\n' > "$W/A/notes/u.txt"
snap "$W/A" > "$W/before.snap"
settle "$W/A" --autostash
snap "$W/A" > "$W/after.snap"; cmpsnap "$W/before.snap" "$W/after.snap"

say "5c — rerere.enabled=true (a common user setting): what the stops and the abort leave in rr-cache"
W=$ROOT/work/s5c; mk "$W"; git -C "$W/A" config rerere.enabled true
settle "$W/A"
echo "-- rr-cache entries after abort: $(ls "$W/A/.git/rr-cache" 2>/dev/null | wc -l)"; ls -R "$W/A/.git/rr-cache" 2>/dev/null | head
