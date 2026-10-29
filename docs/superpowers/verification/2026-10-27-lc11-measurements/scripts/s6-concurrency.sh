#!/usr/bin/env bash
# Scenario 6 — another process in A's worktree while the rebase is stopped (simulated in sequence).
. "$(dirname "$0")/lib.sh"
git --version
REGPY=/workspace/ai-workflows/plugins/security-workflows/scripts/register.py
# A: a1 (register + feedback); B: b1 (register + feedback); attributes installed: the stop is on the register only.
mk() {
  local w=$1; setup_repos "$w"; install_attrs "$w/A"
  for c in A B; do
    local t; t=$(echo $c | tr AB ab)1
    printf -- '- %s entry\n' $t >> "$w/$c/$FB"; rec "$w/$c" 2 2026-10-27T02:00:00Z "${t}${t}${t}${t}" "scan-$t:p1" "$t" open; rebuild "$w/$c" >/dev/null
    git -C "$w/$c" add -A -- "$FB" "$REG"; git -C "$w/$c" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/$t)" -- "$FB" "$REG"
  done
  git -C "$w/B" push -q origin main; git -C "$w/A" fetch -q origin
}
stop_on_register() { run git -C "$1/A" rebase "${@:2}" origin/main; }
finish() {  # the run's settle of the register stop: rebuild, add, continue
  run python3 -I "$ROOT/rebuild.py" "$1/A" "$SLUG"; run git -C "$1/A" add -- "$REG/register.json" "$REG/register.md"; run git -C "$1/A" rebase --continue
}

say "6a — what another session sees during the stop (its preflight's G0 test, its catch-up, its switch, its status)"
W=$ROOT/work/s6a; mk "$W"; stop_on_register "$W"
run git -C "$W/A" symbolic-ref -q HEAD
run git -C "$W/A" pull --ff-only --no-rebase origin main
run git -C "$W/A" switch -c spec/x
run git -C "$W/A" status --porcelain -z --untracked-files=all
echo; finish "$W"

say "6b — another process appends to a session file (feedback.md) the run's stop does not involve, then the run continues"
W=$ROOT/work/s6b; mk "$W"; stop_on_register "$W"
printf -- '- concurrent entry written during the stop\n' >> "$W/A/$FB"
finish "$W"
run git -C "$W/A" status --short
run git -C "$W/A" log --oneline -3
run git -C "$W/A" show --stat --format=%s HEAD

say "6c — another process edits a tracked user file, then the run's flow aborts (reset --hard)"
W=$ROOT/work/s6c; mk "$W"; stop_on_register "$W"
printf 'edit saved during the stop\n' >> "$W/A/$NOTE"; printf 'new untracked during the stop\n' > "$W/A/notes/during.txt"
run git -C "$W/A" rebase --abort
echo "-- $NOTE after abort:"; tail -2 "$W/A/$NOTE"
echo "-- notes/during.txt after abort: $(test -e "$W/A/notes/during.txt" && echo present || echo GONE)"

say "6c2 — the same with --autostash, the user's edit already stashed: an editor writes its buffer back during the stop"
W=$ROOT/work/s6c2; mk "$W"; printf 'user edit\n' >> "$W/A/$NOTE"
stop_on_register "$W" --autostash
echo "-- $NOTE during the stop: $(tail -1 "$W/A/$NOTE")"
printf 'user edit\n' >> "$W/A/$NOTE"   # the editor's autosave of its (dirty) buffer
finish "$W"
run git -C "$W/A" status --short; run git -C "$W/A" stash list
echo "-- $NOTE now:"; cat "$W/A/$NOTE"

say "6d — another session commits (its commit-artifacts pathspec commit) during the stop"
W=$ROOT/work/s6d; mk "$W"; stop_on_register "$W"
printf -- '- other session entry\n' >> "$W/A/$FUP"
run git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/other)" -- "$FUP"
run git -C "$W/A" log --oneline -3
echo "(d1: the run then continues)"; finish "$W"
run git -C "$W/A" log --oneline -5
echo "(d2: the run instead aborts)"
W=$ROOT/work/s6d2; mk "$W"; stop_on_register "$W"
printf -- '- other session entry\n' >> "$W/A/$FUP"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/other)" -- "$FUP"; OTHER=$(git -C "$W/A" rev-parse HEAD)
run git -C "$W/A" rebase --abort
run git -C "$W/A" log --oneline -3
echo "-- the other session's commit $OTHER reachable from a branch? $(git -C "$W/A" branch --contains "$OTHER" 2>/dev/null | wc -l) branch(es); in HEAD reflog: $(git -C "$W/A" reflog | grep -c "${OTHER:0:7}")"

say "6e — index.lock held by another process at the moment the run continues, or aborts"
W=$ROOT/work/s6e; mk "$W"; stop_on_register "$W"
python3 -I "$ROOT/rebuild.py" "$W/A" "$SLUG" >/dev/null
touch "$W/A/.git/index.lock"
run git -C "$W/A" add -- "$REG/register.json" "$REG/register.md"
run git -C "$W/A" rebase --continue
run git -C "$W/A" rebase --abort
echo "-- state with the lock still held:"; ls -d "$W/A/.git/rebase-merge" >/dev/null 2>&1 && echo "   rebase still in progress, HEAD $(git -C "$W/A" symbolic-ref -q HEAD || echo DETACHED)"
rm -f "$W/A/.git/index.lock"   # (the other process releases it)
run git -C "$W/A" rebase --abort
echo "(and a lock present at rebase start)"
touch "$W/A/.git/index.lock"; run git -C "$W/A" rebase origin/main; ls -d "$W/A/.git/rebase-merge" 2>/dev/null || echo "   no rebase started"; rm -f "$W/A/.git/index.lock"

say "6f — how long the checkout is in a non-normal state: wall time from rebase start to finish"
for n in 1 3 5; do
  W=$ROOT/work/s6f$n; setup_repos "$W"; install_attrs "$W/A"
  for i in $(seq 1 $n); do printf -- '- a%s\n' $i >> "$W/A/$FB"; rec "$W/A" $((i+1)) "2026-10-27T0$i:00:00Z" "a${i}a${i}a${i}a${i}" "s$i:p" "a$i" open; rebuild "$W/A" >/dev/null
    git -C "$W/A" add -A -- "$FB" "$REG"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a$i)" -- "$FB" "$REG"; done
  printf -- '- b1\n' >> "$W/B/$FB"; rec "$W/B" 2 2026-10-27T00:30:00Z b1b1b1b1 sb:p b1 open; rebuild "$W/B" >/dev/null
  git -C "$W/B" add -A; git -C "$W/B" commit -q -m b1; git -C "$W/B" push -q origin main; git -C "$W/A" fetch -q origin
  t0=$(date +%s%N); settle "$W/A" >/dev/null 2>&1; t1=$(date +%s%N)
  echo "$n commit(s), $n stop(s), simulated rebuild: $(( (t1-t0)/1000000 )) ms"
done
W=$ROOT/work/s6f-clean; setup_repos "$W"; install_attrs "$W/A"
for i in 1 2 3 4 5; do printf -- '- a%s\n' $i >> "$W/A/$FB"; git -C "$W/A" commit -q -m "a$i" -- "$FB"; done
printf -- '- b1\n' >> "$W/B/$FB"; git -C "$W/B" commit -q -am b1; git -C "$W/B" push -q origin main; git -C "$W/A" fetch -q origin
t0=$(date +%s%N); git -C "$W/A" rebase -q origin/main; t1=$(date +%s%N); echo "5 commits, no stop: $(( (t1-t0)/1000000 )) ms"
echo "real register.py rebuild cost (python start + import + replay), on s4g's register if present:"
if [ -d "$ROOT/work/s4g/A/security/code" ]; then
  for i in 1 2 3; do t0=$(date +%s%N); python3 -I "$REGPY" rebuild --specs "$ROOT/work/s4g/A" --slug code >/dev/null; t1=$(date +%s%N); echo "   $(( (t1-t0)/1000000 )) ms ($(ls "$ROOT/work/s4g/A/security/code/runs" | wc -l) records)"; done
fi

say "6b2 — 6b's refused continue, followed by the decided flow's abort: what happens to the concurrent append"
W=$ROOT/work/s6b2; mk "$W"; stop_on_register "$W" >/dev/null 2>&1
printf -- '- concurrent entry written during the stop\n' >> "$W/A/$FB"
finish "$W" >/dev/null 2>&1; echo "continue refused? $(test -d "$W/A/.git/rebase-merge" && echo yes)"
run git -C "$W/A" rebase --abort
echo "-- concurrent entry still in $FB? $(grep -c 'concurrent entry' "$W/A/$FB")"

say "6c3 — --autostash; the user keeps typing during the stop (buffer saved = stashed edit + more); continue refused; abort"
W=$ROOT/work/s6c3; mk "$W"; printf 'user edit\n' >> "$W/A/$NOTE"
stop_on_register "$W" --autostash >/dev/null 2>&1
printf 'user edit\nmore typing during the stop\n' >> "$W/A/$NOTE"
finish "$W" >/dev/null 2>&1; echo "continue refused? $(test -d "$W/A/.git/rebase-merge" && echo yes)"
run git -C "$W/A" rebase --abort
echo "-- $NOTE after abort:"; tail -3 "$W/A/$NOTE"; run git -C "$W/A" stash list

say "6g — hooks: which fire on a pick, on --continue after a settled stop, and after the rebase"
W=$ROOT/work/s6g; mk "$W"
for h in pre-commit commit-msg post-commit pre-rebase post-rewrite post-checkout prepare-commit-msg; do
  printf '#!/bin/sh\necho "%s $*" >> "%s"\n' "$h" "$W/hooks.log" > "$W/A/.git/hooks/$h"; chmod +x "$W/A/.git/hooks/$h"; done
printf -- '- a2\n' >> "$W/A/$FUP"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a2)" -- "$FUP"; : > "$W/hooks.log"
settle "$W/A" >/dev/null 2>&1
echo "-- hooks that ran during settle (commit a1 stops on the register and is continued; a2 picks clean):"; cat "$W/hooks.log"
