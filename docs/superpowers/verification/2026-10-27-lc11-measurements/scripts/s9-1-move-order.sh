#!/usr/bin/env bash
# Scenario 9.1 — moving the checkout after the replay: which order is safe.
. "$(dirname "$0")/lib.sh"; . "$(dirname "$0")/lib9.sh"
git --version
# Expected after a correct move: HEAD=main=TIP; index≠HEAD exactly on the user's staged paths
# (notes/staged-new.md, prd.md, design-notes.md); worktree≠index exactly on team.md, prd.md, design-notes.md.

domove() {  # domove <strategy> <repo>
  local how=$1 a=$2
  case $how in
    a|b|txn) python3 -I "$ROOT/move.py" "$a" main "$OLD" "$TIP" "$how";;
    switchC) run git -C "$a" switch -C main "$TIP";;
    checkoutB) run git -C "$a" checkout -B main "$TIP";;
    resetkeep) run git -C "$a" reset --keep "$TIP";;
    mergeff) run git -C "$a" merge --ff-only "$TIP";;
    pullff) run git -C "$a" push --porcelain origin "$TIP:refs/heads/main" >/dev/null; run git -C "$a" fetch -q origin; run git -C "$a" pull --ff-only --no-rebase origin main;;
  esac
}
onecase() {  # onecase <strategy> <case>
  local how=$1 kase=$2; local W=$ROOT/work/s91-$how-$kase
  case $kase in
    dirty) mk9 "$W"; dirty9 "$W/A";;
    collide) mk9 "$W" deliv; dirty9 "$W/A";;
    untracked) mk9 "$W" newfile; dirty9 "$W/A"; printf 'mine\n' > "$W/A/notes/new.md";;
    concurrent) mk9 "$W"; dirty9 "$W/A";;
    window-pathspec|window-index) mk9 "$W"; dirty9 "$W/A";;
  esac
  OLD=$(git -C "$W/A" rev-parse main); TIP=$(replay9 "$W/A" | tipof); X=
  if [ $kase = concurrent ]; then
    printf -- '- [ ] other session\n' >> "$W/A/$FUP"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/other)" -- "$FUP"; X=$(git -C "$W/A" rev-parse HEAD)
  fi
  local A=$W/A
  if [ $kase = window-pathspec ]; then
    export MOVE_DURING="printf -- '- [ ] window\n' >> '$A/$FUP' && git -C '$A' commit -q -m 'PRD-A-1 Add dev-workflows session artifacts (/window)' -- '$FUP' && echo committed"
  elif [ $kase = window-index ]; then
    export MOVE_DURING="git -C '$A' commit -q -m 'a plain index commit by another process' && echo committed"
  else unset MOVE_DURING; fi
  snap "$A" > "$W/before.snap"; userbytes "$A" > "$W/before.ub"
  echo; echo "== $how / $kase"
  domove "$how" "$A"
  unset MOVE_DURING
  state "$A"
  snap "$A" > "$W/after.snap"; userbytes "$A" > "$W/after.ub"
  echo "   user files' bytes unchanged: $(cmp -s "$W/before.ub" "$W/after.ub" && echo yes || echo NO)"
  echo "   whole snapshot (HEAD, index, every file, stash) unchanged: $(cmp -s "$W/before.snap" "$W/after.snap" && echo yes || echo no)"
  [ -n "$X" ] && echo "   X (the concurrent commit) on a branch: $(git -C "$A" branch --contains "$X" 2>/dev/null | wc -l)"
  [ "${kase#window}" != "$kase" ] && echo "   newest commit on main: $(git -C "$A" log -1 --format='%h %s' main) — parent $(lab "$A" main^)"
  return 0
}
for how in a b txn switchC checkoutB resetkeep mergeff pullff; do
  say "strategy $how"
  for kase in dirty collide untracked concurrent; do onecase $how $kase; done
  case $how in a|b|txn) onecase $how window-pathspec; onecase $how window-index;; esac
done

say "txn — the driver goes away between prepare and commit (stdin closes): are the locks released, is the ref unchanged?"
W=$ROOT/work/s91-txn-eof; mk9 "$W"; OLD=$(git -C "$W/A" rev-parse main); TIP=$(replay9 "$W/A" | tipof)
python3 - "$W/A" "$OLD" "$TIP" <<'PY'
import subprocess, sys, os
repo, old, tip = sys.argv[1:4]
p = subprocess.Popen(["git", "-C", repo, "update-ref", "--stdin"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
p.stdin.write("start\nupdate refs/heads/main %s %s\nprepare\n" % (tip, old)); p.stdin.flush()
print("  ", p.stdout.readline().strip(), "/", p.stdout.readline().strip())
print("   while prepared: HEAD.lock %s, main.lock %s" % (os.path.exists(repo + "/.git/HEAD.lock"), os.path.exists(repo + "/.git/refs/heads/main.lock")))
p.stdin.close(); rc = p.wait()
print("   after stdin closed: update-ref exit %d, stderr %r" % (rc, p.stderr.read().strip()))
print("   HEAD.lock %s, main.lock %s" % (os.path.exists(repo + "/.git/HEAD.lock"), os.path.exists(repo + "/.git/refs/heads/main.lock")))
PY
echo "   main is OLD? $([ "$(git -C "$W/A" rev-parse main)" = "$OLD" ] && echo yes || echo no)"

say "txn — index.lock held by another process when the move runs"
W=$ROOT/work/s91-txn-indexlock; mk9 "$W"; dirty9 "$W/A"; OLD=$(git -C "$W/A" rev-parse main); TIP=$(replay9 "$W/A" | tipof)
snap "$W/A" > "$W/before.snap"; touch "$W/A/.git/index.lock"
python3 -I "$ROOT/move.py" "$W/A" main "$OLD" "$TIP" txn | sed "s#$ROOT#\$M#g"
rm -f "$W/A/.git/index.lock"; snap "$W/A" > "$W/after.snap"; cmpsnap "$W/before.snap" "$W/after.snap"
echo "   main is OLD? $([ "$(git -C "$W/A" rev-parse main)" = "$OLD" ] && echo yes || echo no); reflog entries for main: $(git -C "$W/A" reflog refs/heads/main | wc -l)"
