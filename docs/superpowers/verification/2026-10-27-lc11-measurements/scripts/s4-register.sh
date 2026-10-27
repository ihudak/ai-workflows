#!/usr/bin/env bash
# Scenario 4 — a rebase stopping on register.json / register.md, settled by a rebuild mid-rebase.
. "$(dirname "$0")/lib.sh"
git --version

# session commit without resume.md (resume.md is measured separately in 4b)
sess() {  # sess <repo> <tag> <seq> <hash8> [resume]
  local repo=$1 tag=$2 seq=$3 h=$4 resume=${5:-}
  printf '\n## 2026-10-27 %s run\n- api: %s\n' "$tag" "$h" >> "$repo/$IMPL"
  printf -- '- %s entry\n' "$tag" >> "$repo/$FB"
  local paths=("$IMPL" "$FB" "$REG")
  if [ -n "$resume" ]; then printf 'last: %s\n' "$tag" > "$repo/$RESUME"; paths+=("$RESUME"); fi
  rec "$repo" "$seq" "2026-10-27T0$seq:00:00Z" "$h" "scan-$tag:p1" "$tag finding" open
  rebuild "$repo" >/dev/null
  git -C "$repo" add -A -- "${paths[@]}"
  git -C "$repo" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/$tag)" -- "${paths[@]}"
}
check_register() {  # is the committed register what a rebuild of the committed runs/ gives?
  local repo=$1 t; t=$(mktemp -d "$ROOT/work/chk.XXXX")
  git -C "$repo" archive HEAD security | tar -x -C "$t"
  cp "$t/$REG/register.json" "$t/committed.json"; cp "$t/$REG/register.md" "$t/committed.md"
  python3 -I "$ROOT/rebuild.py" "$t" "$SLUG" >/dev/null
  if cmp -s "$t/committed.json" "$t/$REG/register.json" && cmp -s "$t/committed.md" "$t/$REG/register.md"; then
    echo "register at HEAD == rebuild(runs at HEAD): YES"
  else echo "register at HEAD == rebuild(runs at HEAD): NO"; diff "$t/committed.json" "$t/$REG/register.json"; fi
  echo "runs at HEAD: $(git -C "$repo" ls-tree --name-only HEAD "$REG/runs/" | xargs -n1 basename | tr '\n' ' ')"
  rm -rf "$t"
}
# settle, but print what the rebuild sees at each stop
settle_v() {
  local repo=$1; shift
  run git -C "$repo" rebase "$@" origin/main
  while [ -d "$repo/.git/rebase-merge" ]; do
    local un; un=$(git -C "$repo" diff --name-only --diff-filter=U)
    echo "STOP at $(cat "$repo/.git/rebase-merge/msgnum")/$(cat "$repo/.git/rebase-merge/end") ($(git -C "$repo" log -1 --format=%s "$(cat "$repo/.git/rebase-merge/stopped-sha")")) — conflicted: $(echo $un)"
    echo "  runs/ in the worktree at the stop: $(ls "$repo/$REG/runs" | tr '\n' ' ')"
    echo "  register.json at the stop holds runs: $(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["runs"])' "$repo/$REG/register.json")"
    if printf '%s\n' "$un" | grep -qvE '^security/[^/]+/register\.(json|md)$'; then
      echo "  => other conflict: abort"; run git -C "$repo" rebase --abort; return 1; fi
    local t0 t1; t0=$(date +%s%N)
    run python3 -I "$ROOT/rebuild.py" "$repo" "$SLUG"
    run git -C "$repo" add -- "$REG/register.json" "$REG/register.md"
    t1=$(date +%s%N); echo "  rebuild+add took $(( (t1-t0)/1000000 )) ms"
    run git -C "$repo" rebase --continue
  done
}

say "4a — A: two session commits with register runs; B: one, pushed first; attributes installed; settle"
W=$ROOT/work/s4a; setup_repos "$W"; install_attrs "$W/A"
sess "$W/A" a1 2 a1a1a1a1; sess "$W/A" a2 3 a2a2a2a2
sess "$W/B" b1 2 b1b1b1b1; git -C "$W/B" push -q origin main
run git -C "$W/A" push --porcelain origin main
run git -C "$W/A" fetch -q origin
run python3 -I "$ROOT/push_scope.py" "$W/A" main refs/remotes/origin/main
t0=$(date +%s%N); settle_v "$W/A"; t1=$(date +%s%N); echo "whole settle: $(( (t1-t0)/1000000 )) ms"
run git -C "$W/A" log --oneline --graph
check_register "$W/A"
cat "$W/A/$REG/register.md"
run git -C "$W/A" push --porcelain origin main
run git -C "$W/A" status --short

say "4b — the same, but both sides also overwrote resume.md (same PRD): the decided rule aborts"
W=$ROOT/work/s4b; setup_repos "$W"; install_attrs "$W/A"
sess "$W/A" a1 2 a1a1a1a1 resume
sess "$W/B" b1 2 b1b1b1b1 resume; git -C "$W/B" push -q origin main
git -C "$W/A" fetch -q origin
settle_v "$W/A"
run git -C "$W/A" log --oneline -3
echo "(variant: at a stop, take the run's own version of an overwritten shape — in a rebase that is --theirs)"
run git -C "$W/A" rebase origin/main
run git -C "$W/A" checkout --theirs -- "$RESUME"
run git -C "$W/A" add -- "$RESUME"
run python3 -I "$ROOT/rebuild.py" "$W/A" "$SLUG"
run git -C "$W/A" add -- "$REG/register.json" "$REG/register.md"
run git -C "$W/A" rebase --continue
echo "---- resume.md"; cat "$W/A/$RESUME"
check_register "$W/A"

say "4c — runs/ itself conflicts: the same record file name with different content on both sides"
W=$ROOT/work/s4c; setup_repos "$W"; install_attrs "$W/A"
rec "$W/A" 2 2026-10-27T02:00:00Z deadbeef scan-a:p1 "A finding" open; rebuild "$W/A" >/dev/null
git -C "$W/A" add -A -- "$REG"; git -C "$W/A" commit -q -m "NOISSUE Add dev-workflows session artifacts (/scan a)" -- "$REG"
rec "$W/B" 2 2026-10-27T02:00:00Z deadbeef scan-b:p1 "B finding" fixed; rebuild "$W/B" >/dev/null
git -C "$W/B" add -A -- "$REG"; git -C "$W/B" commit -q -m "NOISSUE Add dev-workflows session artifacts (/scan b)" -- "$REG"; git -C "$W/B" push -q origin main
git -C "$W/A" fetch -q origin
run git -C "$W/A" rebase origin/main
run git -C "$W/A" status --short
echo "---- the conflicted record:"; cat "$W/A/$REG/runs/0002-20261027T020000Z-deadbeef.json"
echo "---- what a rebuild does on it:"; run python3 -I "$ROOT/rebuild.py" "$W/A" "$SLUG" | tail -2
run git -C "$W/A" rebase --abort
echo "(same name, identical content on both sides — the realistic case, since <hash8> is the record's own sha256)"
W=$ROOT/work/s4c2; setup_repos "$W"; install_attrs "$W/A"
for c in A B; do rec "$W/$c" 2 2026-10-27T02:00:00Z cafecafe scan-x:p1 "same" open; rebuild "$W/$c" >/dev/null; printf -- '- %s\n' "$c" >> "$W/$c/$FB"
  git -C "$W/$c" add -A -- "$REG" "$FB"; git -C "$W/$c" commit -q -m "NOISSUE Add dev-workflows session artifacts ($c)" -- "$REG" "$FB"; done
git -C "$W/B" push -q origin main; git -C "$W/A" fetch -q origin
run git -C "$W/A" rebase origin/main
run git -C "$W/A" status --short

say "4d — no attributes in A: register.json / register.md merge as text"
W=$ROOT/work/s4d; setup_repos "$W"
sess "$W/A" a1 2 a1a1a1a1
sess "$W/B" b1 2 b1b1b1b1; git -C "$W/B" push -q origin main
git -C "$W/A" fetch -q origin
run git -C "$W/A" rebase origin/main
run git -C "$W/A" diff --name-only --diff-filter=U
echo "---- register.json with markers:"; head -30 "$W/A/$REG/register.json"
run git -C "$W/A" rebase --abort
echo "(a register change on one side far from the other's: B triages the base finding only — a decision record —, A adds a run)"
W=$ROOT/work/s4d2; setup_repos "$W"
# pad the base register with many findings so the two sides' edits are far apart
for i in $(seq 2 12); do rec "$W/seed" "$i" "2026-10-0${i}T00:00:00Z" "$(printf '%08d' $i)" "scan$i:p1" "f$i" open; done 2>/dev/null
rebuild "$W/seed" >/dev/null; git -C "$W/seed" add -A; git -C "$W/seed" commit -q -m pad; git -C "$W/seed" push -q origin main
git -C "$W/A" pull -q --no-rebase origin main; git -C "$W/B" pull -q --no-rebase origin main
sed -i 's/"title": "f5", "status": "open"/"title": "f5", "status": "fixed"/' "$W/B/$REG/runs/0005-20261005T000000Z-00000005.json"   # (hand edit of a record: B's register differs mid-file only)
rebuild "$W/B" >/dev/null; git -C "$W/B" commit -q -am "B mid-file register change"; git -C "$W/B" push -q origin main
rec "$W/A" 13 2026-10-27T13:00:00Z a13a13a1 scan-a:p1 "A finding" open; rebuild "$W/A" >/dev/null
git -C "$W/A" add -A -- "$REG"; git -C "$W/A" commit -q -m "NOISSUE Add dev-workflows session artifacts (/a)" -- "$REG"
git -C "$W/A" fetch -q origin
run git -C "$W/A" rebase origin/main
check_register "$W/A"

say "4e — rebase -X theirs (keeps an overwritten shape whole with no stop): the registers too"
W=$ROOT/work/s4e; setup_repos "$W"; install_attrs "$W/A"
sess "$W/A" a1 2 a1a1a1a1 resume
sess "$W/B" b1 2 b1b1b1b1 resume; git -C "$W/B" push -q origin main
git -C "$W/A" fetch -q origin
run git -C "$W/A" rebase -X theirs origin/main
check_register "$W/A"
echo "---- implementation.md (union still applies under -X theirs?)"; cat "$W/A/$IMPL"

say "4f — timing: A five session commits, B one; settle (attributes installed)"
W=$ROOT/work/s4f; setup_repos "$W"; install_attrs "$W/A"
for i in 1 2 3 4 5; do sess "$W/A" a$i $((i+1)) "a${i}a${i}a${i}a${i}"; done
sess "$W/B" b1 2 b1b1b1b1; git -C "$W/B" push -q origin main
git -C "$W/A" fetch -q origin
t0=$(date +%s%N); settle_v "$W/A" >/dev/null 2>&1; t1=$(date +%s%N)
echo "settle of 5 commits, 5 stops, 5 rebuilds: $(( (t1-t0)/1000000 )) ms"
check_register "$W/A"
