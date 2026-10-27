# lib9.sh — helpers for the s9 follow-up measurements (sourced after lib.sh).
RB="python3 -I $ROOT/rebuild.py"
BLOCK=$ROOT/block.attributes   # §8's block, passed per command with -c core.attributesFile; never written into a clone
cat > "$BLOCK" <<'EOF'
# BEGIN workflows-core session-branch: written by session-branch.py, do not edit
**/dev-workflows/** merge=union
dev-workflows-feedback/** merge=union
dev-workflows-cost/** merge=union
**/implementation.md merge=union
**/follow-ups.md merge=union
**/_security.md merge=union
**/*-implementation-gaps.md merge=union
**/dev-workflows/resume.md -merge
**/pr-draft.md -merge
security/*/register.json -merge
security/*/register.md -merge
# END workflows-core session-branch
EOF
export REPLAY_ATTRS=$BLOCK

# A: a1 (register + feedback + implementation); B: b1 (the same) and extras; B pushes; A fetches.
mk9() {
  local w=$1; shift; setup_repos "$w"
  for c in A B; do local t; t=$(echo $c | tr AB ab)1
    printf -- '- %s entry\n' $t >> "$w/$c/$FB"; printf '\n## %s run\n' $t >> "$w/$c/$IMPL"
    rec "$w/$c" 2 2026-10-27T02:00:00Z "${t}${t}${t}${t}" "scan-$t:p1" "$t" open; rebuild "$w/$c" >/dev/null
    git -C "$w/$c" add -A -- "$FB" "$IMPL" "$REG"; git -C "$w/$c" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/$t)" -- "$FB" "$IMPL" "$REG"; done
  for x in "$@"; do case $x in
    deliv) sed -i 's/Goal: base./Goal: B changed it./' "$w/B/$DELIV"; git -C "$w/B" commit -q -am "B edits the PRD";;
    newfile) printf 'B\n' > "$w/B/notes/new.md"; git -C "$w/B" add notes/new.md; git -C "$w/B" commit -q -m "B adds notes/new.md";;
  esac; done
  git -C "$w/B" push -q origin main; git -C "$w/A" fetch -q origin
}
USERFILES="$NOTE notes/scratch.txt $DELIV notes/staged-new.md $PRD/design-notes.md"
dirty9() { local a=$1
  printf 'user edit, unstaged\n' >> "$a/$NOTE"; printf 'scratch\n' > "$a/notes/scratch.txt"
  printf 'user edit, staged\n' >> "$a/$DELIV"; git -C "$a" add -- "$DELIV"; printf 'unstaged on top\n' >> "$a/$DELIV"
  printf 'new staged\n' > "$a/notes/staged-new.md"; git -C "$a" add -- notes/staged-new.md
  printf 'new staged\n' > "$a/$PRD/design-notes.md"; git -C "$a" add -- "$PRD/design-notes.md"; printf 'unstaged on top\n' >> "$a/$PRD/design-notes.md"; }
userbytes() { (cd "$1" && for f in $USERFILES notes/new.md; do [ -e "$f" ] && sha256sum "$f"; done); }
replay9() { python3 -I "$ROOT/replay.py" "$1" main origin/main $RB; }
tipof() { python3 -c 'import json,sys;print(json.load(sys.stdin).get("tip",""))'; }
lab() { local s; s=$(git -C "$1" rev-parse "$2" 2>/dev/null); case $s in "$OLD") echo OLD;; "$TIP") echo TIP;; "${X:-none}") echo X;; *) echo "${s:0:7}";; esac; }
# state <repo>: HEAD/branch labels, status letters, and the two consistency tests
state() { local a=$1
  echo "   HEAD=$(lab "$a" HEAD) main=$(lab "$a" refs/heads/main) on=$(git -C "$a" symbolic-ref -q --short HEAD || echo DETACHED)"
  echo "   status: $(git -C "$a" status --porcelain=v1 --untracked-files=all | tr '\n' ';')"
  local staged unstaged
  staged=$(git -C "$a" diff --cached --name-only | sort | tr '\n' ' ')
  unstaged=$(git -C "$a" diff --name-only | sort | tr '\n' ' ')
  echo "   index≠HEAD on: ${staged:-nothing}"
  echo "   worktree≠index on: ${unstaged:-nothing}"
}
