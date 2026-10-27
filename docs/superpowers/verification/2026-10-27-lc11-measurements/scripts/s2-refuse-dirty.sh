#!/usr/bin/env bash
# Scenario 2 — rebase with no autostash on a dirty checkout: what git refuses, and what it leaves.
. "$(dirname "$0")/lib.sh"
git --version
mk() {  # A: one append-only session commit (union in A); B: one, pushed; plus B's optional newfile
  local w=$1; setup_repos "$w"; install_attrs "$w/A"
  printf -- '- a1 entry\n' >> "$w/A/$FB"; git -C "$w/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a1)" -- "$FB"
  printf -- '- b1 entry\n' >> "$w/B/$FB"; git -C "$w/B" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/b1)" -- "$FB"
  [ "${2:-}" = newfile ] && { printf 'B wrote this\n' > "$w/B/notes/new.md"; git -C "$w/B" add notes/new.md; git -C "$w/B" commit -q -m "B adds notes/new.md"; }
  git -C "$w/B" push -q origin main; git -C "$w/A" fetch -q origin
}
try() {  # try <label> <repo> <git args...> : snapshot, run, snapshot, compare (HEAD included: a refusal must not move it)
  local w=$1; shift
  snap "$w/A" > "$w/b.snap"; run git -C "$w/A" "$@"; snap "$w/A" > "$w/a.snap"; cmpsnap "$w/b.snap" "$w/a.snap"
}

say "2a — untracked files only (none at a path the rebase writes)"
W=$ROOT/work/s2a; mk "$W"; printf 'x\n' > "$W/A/notes/scratch.txt"; mkdir -p "$W/A/drafts"; printf 'd\n' > "$W/A/drafts/d.md"
run git -C "$W/A" rebase origin/main; run git -C "$W/A" status --short

say "2b — a tracked file modified (unstaged), which the rebase does not touch"
W=$ROOT/work/s2b; mk "$W"; printf 'user edit\n' >> "$W/A/$NOTE"
try "$W" rebase origin/main
try "$W" pull --rebase origin main

say "2c — a staged change only, which the rebase does not touch"
W=$ROOT/work/s2c; mk "$W"; printf 'user edit\n' >> "$W/A/$DELIV"; git -C "$W/A" add -- "$DELIV"
try "$W" rebase origin/main
try "$W" pull --rebase origin main

say "2d — staged + unstaged + untracked together"
W=$ROOT/work/s2d; mk "$W"; printf 'user edit\n' >> "$W/A/$NOTE"; printf 's\n' >> "$W/A/$DELIV"; git -C "$W/A" add -- "$DELIV"; printf 'u\n' > "$W/A/notes/u.txt"
try "$W" rebase origin/main

say "2e — an untracked file where the incoming commits add one (no autostash): fails at checkout"
W=$ROOT/work/s2e; mk "$W" newfile; printf 'user untracked\n' > "$W/A/notes/new.md"
try "$W" rebase origin/main

say "2f — the pre-check a refuse-when-dirty rule would run before rebasing (porcelain, tracked only), on 2a/2b/2c/2d's trees"
for c in s2a s2b s2c s2d; do
  echo "$c: '$(git -C "$ROOT/work/$c/A" status --porcelain -z --untracked-files=no | tr '\0' ' ')'  diff-index: $(git -C "$ROOT/work/$c/A" diff-index --quiet HEAD -- && echo clean || echo dirty)"
done
