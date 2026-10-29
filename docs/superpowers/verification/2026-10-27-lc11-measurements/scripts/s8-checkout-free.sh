#!/usr/bin/env bash
# Scenario 8 (beyond the brief's list) — the same settlement without an in-checkout rebase:
# replay.py builds the rebased commits with merge-tree/commit-tree, then ONE `git reset --keep <tip>`
# moves the checkout. Measured on the dirty states of scenario 1.
. "$(dirname "$0")/lib.sh"
git --version
RB="python3 -I $ROOT/rebuild.py"
mk() {  # A: a1 (register + feedback + implementation); B: b1 (same), plus extras
  local w=$1; shift; setup_repos "$w"; install_attrs "$w/A"
  for c in A B; do local t; t=$(echo $c | tr AB ab)1
    printf -- '- %s entry\n' $t >> "$w/$c/$FB"; printf '\n## %s run\n' $t >> "$w/$c/$IMPL"
    rec "$w/$c" 2 2026-10-27T02:00:00Z "${t}${t}${t}${t}" "scan-$t:p1" "$t" open; rebuild "$w/$c" >/dev/null
    git -C "$w/$c" add -A -- "$FB" "$IMPL" "$REG"; git -C "$w/$c" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/$t)" -- "$FB" "$IMPL" "$REG"; done
  for x in "$@"; do case $x in
    deliv) sed -i 's/Goal: base./Goal: B changed it./' "$w/B/$DELIV"; git -C "$w/B" commit -q -am "B edits the PRD";;
    newfile) printf 'B\n' > "$w/B/notes/new.md"; git -C "$w/B" add notes/new.md; git -C "$w/B" commit -q -m "B adds notes/new.md";;
    resume) printf 'last: a\n' > "$w/A/$RESUME"; git -C "$w/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a2)" -- "$RESUME"
            printf 'last: b\n' > "$w/B/$RESUME"; git -C "$w/B" commit -q -m "B resume" -- "$RESUME";;
  esac; done
  git -C "$w/B" push -q origin main; git -C "$w/A" fetch -q origin
}
dirty() { local a=$1
  printf 'user edit, unstaged\n' >> "$a/$NOTE"; printf 'scratch\n' > "$a/notes/scratch.txt"
  printf 'user edit, staged\n' >> "$a/$DELIV"; git -C "$a" add -- "$DELIV"; printf 'unstaged on top\n' >> "$a/$DELIV"
  printf 'new staged\n' > "$a/notes/staged-new.md"; git -C "$a" add -- notes/staged-new.md
  printf 'new staged\n' > "$a/$PRD/design-notes.md"; git -C "$a" add -- "$PRD/design-notes.md"; printf 'unstaged on top\n' >> "$a/$PRD/design-notes.md"; }
MOVE=${MOVE:-switch}   # how the checkout is moved: switch (git switch -C main <tip>), keep (reset --keep), readtree (read-tree -m -u + update-ref)
move() { local a=$1 tip=$2
  case $MOVE in
    keep) run git -C "$a" reset --keep "$tip";;
    switch) run git -C "$a" switch -C main "$tip";;
    readtree) run git -C "$a" read-tree -m -u HEAD "$tip" && run git -C "$a" update-ref -m "settle: replayed onto origin/main" refs/heads/main "$tip" "$(git -C "$a" rev-parse HEAD)";;
  esac; }
go() {  # replay, then move the checkout once
  local a=$1; local t0 t1 res tip
  t0=$(date +%s%N); res=$(python3 -I "$ROOT/replay.py" "$a" main origin/main $RB); t1=$(date +%s%N)
  echo "replay.py: $res  ($(( (t1-t0)/1000000 )) ms; checkout untouched so far)"
  tip=$(printf '%s' "$res" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("tip",""))')
  [ -z "$tip" ] && { echo "=> refused before touching anything; print today's lines"; return 1; }
  t0=$(date +%s%N); move "$a" "$tip"; local rc=$?; t1=$(date +%s%N); echo "(move by $MOVE: $(( (t1-t0)/1000000 )) ms)"
  [ $rc -ne 0 ] && { echo "=> the checkout refused the move; nothing changed; print today's lines"; return 1; }
  run git -C "$a" push --porcelain origin main
}

say "8a — the user's dirty files (MM, AM, staged new, unstaged, untracked), none touched by B; register conflict settled off-checkout"
W=$ROOT/work/s8a; mk "$W"; dirty "$W/A"
snap "$W/A" > "$W/before.snap"; run git -C "$W/A" status --short
go "$W/A"
snap "$W/A" > "$W/after.snap"; run git -C "$W/A" status --short
cmpsnap <(grep -v '^HEAD' "$W/before.snap" | grep -v 'feedback.md$\|implementation.md$\|register\.\(json\|md\)$\|runs/') <(grep -v '^HEAD' "$W/after.snap" | grep -v 'feedback.md$\|implementation.md$\|register\.\(json\|md\)$\|runs/')
python3 -I "$ROOT/push_scope.py" "$W/A" main refs/remotes/origin/main >/dev/null; echo "-- origin/main now: $(git -C "$W/origin.git" log --oneline main | tr '\n' '|')"
echo "-- register at origin == rebuild? $(T=$(mktemp -d); git -C "$W/origin.git" archive main security | tar -x -C "$T"; cp "$T/$REG/register.json" "$T/c"; $RB "$T" "$SLUG" >/dev/null; cmp -s "$T/c" "$T/$REG/register.json" && echo yes || echo no; rm -rf "$T")"
cat "$W/A/$FB"

say "8b — a dirty file B also changed (prd.md): the move refuses, nothing changes"
W=$ROOT/work/s8b; mk "$W" deliv; dirty "$W/A"
snap "$W/A" > "$W/before.snap"; go "$W/A"; snap "$W/A" > "$W/after.snap"; cmpsnap "$W/before.snap" "$W/after.snap"

say "8c — an untracked file where B adds one"
W=$ROOT/work/s8c; mk "$W" newfile; dirty "$W/A"; printf 'mine\n' > "$W/A/notes/new.md"
snap "$W/A" > "$W/before.snap"; go "$W/A"; snap "$W/A" > "$W/after.snap"; cmpsnap "$W/before.snap" "$W/after.snap"

say "8d — another conflict (resume.md): refused before the checkout is touched"
W=$ROOT/work/s8d; mk "$W" resume; dirty "$W/A"
snap "$W/A" > "$W/before.snap"; go "$W/A"; snap "$W/A" > "$W/after.snap"; cmpsnap "$W/before.snap" "$W/after.snap"

if [ "$MOVE" = switch ]; then
say "8e — a commit lands on main (another session) between the replay and the move"
W=$ROOT/work/s8e; mk "$W"; OLD=$(git -C "$W/A" rev-parse main)
TIP=$(python3 -I "$ROOT/replay.py" "$W/A" main origin/main $RB | python3 -c 'import json,sys;print(json.load(sys.stdin)["tip"])')
printf -- '- other session\n' >> "$W/A/$FUP"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/other)" -- "$FUP"; X=$(git -C "$W/A" rev-parse HEAD)
echo "(i) git switch -C main <tip>:"; run git -C "$W/A" switch -C main "$TIP"
echo "   the other session's commit on a branch now? $(git -C "$W/A" branch --contains "$X" | wc -l)"
W=$ROOT/work/s8e2; mk "$W"; OLD=$(git -C "$W/A" rev-parse main)
TIP=$(python3 -I "$ROOT/replay.py" "$W/A" main origin/main $RB | python3 -c 'import json,sys;print(json.load(sys.stdin)["tip"])')
printf -- '- other session\n' >> "$W/A/$FUP"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/other)" -- "$FUP"
snap "$W/A" > "$W/before.snap"
echo "(ii) compare-and-swap first: update-ref main <tip> <old>, then read-tree -m -u <old> <tip>:"
run git -C "$W/A" update-ref -m "settle" refs/heads/main "$TIP" "$OLD"
snap "$W/A" > "$W/after.snap"; cmpsnap "$W/before.snap" "$W/after.snap"
fi
