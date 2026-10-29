#!/usr/bin/env bash
# Scenario 1 — the user's own dirty files in A's checkout under --autostash, a failed re-apply, and --abort.
. "$(dirname "$0")/lib.sh"
git --version

# One session commit on each side (append files only, union in A); B pushes first.
# B's extra incoming change, if any: deliv (B changed prd.md), newfile (B added notes/new.md), resume (B overwrote resume.md)
mkcase() {
  local w=$1; shift
  setup_repos "$w"; install_attrs "$w/A"
  local resume=0
  for x in "$@"; do [ "$x" = resume ] && resume=1; done
  # A's own session commit
  printf -- '- a1 entry\n' >> "$w/A/$FB"; printf '\n## a1 run\n- api: a1\n' >> "$w/A/$IMPL"
  local pa=("$FB" "$IMPL"); [ $resume = 1 ] && { printf 'last: a1\n' > "$w/A/$RESUME"; pa+=("$RESUME"); }
  git -C "$w/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a1)" -- "${pa[@]}"
  # B
  printf -- '- b1 entry\n' >> "$w/B/$FB"; printf '\n## b1 run\n- api: b1\n' >> "$w/B/$IMPL"
  local pb=("$FB" "$IMPL"); [ $resume = 1 ] && { printf 'last: b1\n' > "$w/B/$RESUME"; pb+=("$RESUME"); }
  git -C "$w/B" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/b1)" -- "${pb[@]}"
  for x in "$@"; do case $x in
    deliv) sed -i 's/Goal: base./Goal: B changed it./' "$w/B/$DELIV"; git -C "$w/B" commit -q -am "PRD-A-1 B edits the PRD (merged PR)";;
    newfile) printf 'B wrote this\n' > "$w/B/notes/new.md"; git -C "$w/B" add notes/new.md; git -C "$w/B" commit -q -m "B adds notes/new.md";;
  esac; done
  git -C "$w/B" push -q origin main
  git -C "$w/A" fetch -q origin
}
# The user's dirty state in A: tracked modified (untouched by incoming), untracked (file + dir),
# staged change, staged new file, partially staged (MM).
dirty() {
  local a=$1
  printf 'user edit, unstaged\n' >> "$a/$NOTE"
  printf 'scratch\n' > "$a/notes/scratch.txt"; mkdir -p "$a/drafts"; printf 'draft\n' > "$a/drafts/d.md"
  printf 'user edit, staged\n' >> "$a/$DELIV"; git -C "$a" add -- "$DELIV"
  printf 'user edit, unstaged on top of the staged one\n' >> "$a/$DELIV"
  printf 'new staged file\n' > "$a/notes/staged-new.md"; git -C "$a" add -- notes/staged-new.md
  printf '\n## user section (staged)\n' >> "$a/$PRD/design-notes.md"; git -C "$a" add -- "$PRD/design-notes.md"
  printf 'and then unstaged on top\n' >> "$a/$PRD/design-notes.md"
}

say "1a — git rebase --autostash origin/main, dirty files none of which the incoming commits touch"
W=$ROOT/work/s1a; mkcase "$W"; dirty "$W/A"
snap "$W/A" > "$W/before.snap"; run git -C "$W/A" status --short
run git -C "$W/A" rebase --autostash origin/main
snap "$W/A" > "$W/after.snap"; run git -C "$W/A" status --short
echo "(HEAD moves by design; compare everything but HEAD)"
cmpsnap <(grep -v '^HEAD' "$W/before.snap" | sed '/implementation.md$/d;/feedback.md$/d') <(grep -v '^HEAD' "$W/after.snap" | sed '/implementation.md$/d;/feedback.md$/d')

say "1b — the same through git pull --rebase --autostash origin main"
W=$ROOT/work/s1b; mkcase "$W"; dirty "$W/A"
snap "$W/A" > "$W/before.snap"
run git -C "$W/A" pull --rebase --autostash origin main
snap "$W/A" > "$W/after.snap"; run git -C "$W/A" status --short
cmpsnap <(grep -v '^HEAD' "$W/before.snap" | sed '/implementation.md$/d;/feedback.md$/d') <(grep -v '^HEAD' "$W/after.snap" | sed '/implementation.md$/d;/feedback.md$/d')

say "1c — rebase.autoStash=true, plain git rebase origin/main"
W=$ROOT/work/s1c; mkcase "$W"; dirty "$W/A"; git -C "$W/A" config rebase.autoStash true
run git -C "$W/A" rebase origin/main
run git -C "$W/A" status --short

say "1d — a dirty file the incoming commits also change (B edited prd.md; the user has prd.md staged+dirty in A)"
W=$ROOT/work/s1d; mkcase "$W" deliv; dirty "$W/A"
snap "$W/A" > "$W/before.snap"
run git -C "$W/A" rebase --autostash origin/main
run git -C "$W/A" status --short
run git -C "$W/A" stash list
echo "---- prd.md after the failed re-apply:"; cat "$W/A/$DELIV"
run git -C "$W/A" log --oneline -3
run git -C "$W/A" stash show --stat stash@{0}
echo "(is the stash complete? apply it on the original HEAD in a scratch worktree)"
run git -C "$W/A" worktree add -q --detach "$W/wt" ORIG_HEAD
run git -C "$W/wt" stash apply --index stash@{0}
run git -C "$W/wt" status --short
run git -C "$W/A" worktree remove --force "$W/wt"

say "1e — a dirty SESSION file the incoming commits also change (feedback.md: union in A) — re-apply honours the attributes?"
W=$ROOT/work/s1e; mkcase "$W"
printf -- '- concurrent session entry, uncommitted\n' >> "$W/A/$FB"
run git -C "$W/A" rebase --autostash origin/main
run git -C "$W/A" status --short; cat "$W/A/$FB"
echo "(and without the attributes: A's own commit touches follow-ups.md only, B appended feedback.md, the dirty copy of feedback.md conflicts)"
W=$ROOT/work/s1e2; setup_repos "$W"
printf -- '- [ ] a1 item\n' >> "$W/A/$FUP"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a1)" -- "$FUP"
printf -- '- b1 entry\n' >> "$W/B/$FB"; git -C "$W/B" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/b1)" -- "$FB"; git -C "$W/B" push -q origin main
git -C "$W/A" fetch -q origin
printf -- '- concurrent session entry, uncommitted\n' >> "$W/A/$FB"
run git -C "$W/A" rebase --autostash origin/main
run git -C "$W/A" status --short
run git -C "$W/A" stash list
cat "$W/A/$FB"

say "1f — the decided path's abort (resume.md conflict = 'any other conflict') with the user's dirty files autostashed"
W=$ROOT/work/s1f; mkcase "$W" resume; dirty "$W/A"
snap "$W/A" > "$W/before.snap"
git -C "$W/A" reflog -n 3 > "$W/reflog-before"
run git -C "$W/A" rebase --autostash origin/main
echo "-- during the stop:"; run git -C "$W/A" status --short; run git -C "$W/A" stash list
echo "   (the user's files during the stop:)"; tail -1 "$W/A/$NOTE"; tail -1 "$W/A/$DELIV"; ls "$W/A/notes"
run git -C "$W/A" rebase --abort
snap "$W/A" > "$W/after.snap"
cmpsnap "$W/before.snap" "$W/after.snap"
echo "-- reflog after abort:"; git -C "$W/A" reflog -n 6
echo "-- branch reflog:"; git -C "$W/A" reflog -n 3 refs/heads/main
echo "-- stash reflog / refs/stash:"; git -C "$W/A" reflog -n 3 refs/stash 2>&1; git -C "$W/A" rev-parse -q --verify refs/stash || echo "no refs/stash"
echo "-- ORIG_HEAD: $(git -C "$W/A" rev-parse ORIG_HEAD)  HEAD: $(git -C "$W/A" rev-parse HEAD)"

say "1g — an untracked file at a path the incoming commits add (B added notes/new.md; A has an untracked notes/new.md)"
W=$ROOT/work/s1g; mkcase "$W" newfile; dirty "$W/A"; printf 'user untracked\n' > "$W/A/notes/new.md"
snap "$W/A" > "$W/before.snap"
run git -C "$W/A" rebase --autostash origin/main
run git -C "$W/A" status --short; run git -C "$W/A" stash list
ls -d "$W/A/.git/rebase-merge" 2>/dev/null && echo "rebase in progress" || echo "no rebase in progress"
snap "$W/A" > "$W/after.snap"; cmpsnap "$W/before.snap" "$W/after.snap"
echo "(and the pull form)"
run git -C "$W/A" pull --rebase --autostash origin main
snap "$W/A" > "$W/after2.snap"; cmpsnap "$W/before.snap" "$W/after2.snap"
