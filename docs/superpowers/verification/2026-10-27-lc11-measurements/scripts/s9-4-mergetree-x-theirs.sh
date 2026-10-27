#!/usr/bin/env bash
# Scenario 9.4 — merge-tree -X theirs for the overwritten shapes, the block passed with -c core.attributesFile.
. "$(dirname "$0")/lib.sh"; . "$(dirname "$0")/lib9.sh"
git --version
W=$ROOT/work/s94; setup_repos "$W"; R=$W/seed
PD=$PRD/pr-draft.md; RUNX=$REG/runs/0009-20261027T090000Z-samename.json
printf 'draft: base\n' > "$R/$PD"; git -C "$R" add -A; git -C "$R" commit -q -m "base pr-draft"; P=$(git -C "$R" rev-parse HEAD)
side() {  # side <tag>: overwrite resume.md, pr-draft.md; append feedback; a run record + rebuild; a same-named runs/ record
  local t=$1
  printf 'last: %s\n' $t > "$R/$RESUME"; printf 'draft: %s\n' $t > "$R/$PD"; printf -- '- %s entry\n' $t >> "$R/$FB"
  rec "$R" 2 2026-10-27T02:00:00Z "${t}1${t}1${t}1${t}1" "scan-$t:p1" "$t" open
  [ "${2:-}" = norunx ] || printf '{\n  "seq": 9,\n  "at": "2026-10-27T09:00:00Z",\n  "findings": [{"origin": "x:%s", "title": "%s", "status": "open"}]\n}\n' $t $t > "$R/$RUNX"
  rebuild "$R" >/dev/null; git -C "$R" add -A; git -C "$R" commit -q -m "$t"; }
git -C "$R" switch -q -c onto "$P"; side b; ONTO=$(git -C "$R" rev-parse HEAD)
git -C "$R" switch -q -c replayed "$P"; side a; C=$(git -C "$R" rev-parse HEAD)
echo "parent P=${P:0:7}  onto (B's side, merge-tree's branch1 = ours) ${ONTO:0:7}  replayed commit (A's, branch2 = theirs) ${C:0:7}"
show() { local t=$1
  for f in "$RESUME" "$PD" "$REG/register.json" "$REG/register.md" "$FB" "$RUNX"; do
    case $f in *register.json) echo "   $f: runs $(git -C "$R" show "$t:$f" | python3 -c 'import json,sys
try: print([r[-13:-5] for r in json.load(sys.stdin)["runs"]])
except Exception as e: print("unparseable:", type(e).__name__)')";;
      *register.md) echo "   $f: $(git -C "$R" show "$t:$f" | grep -c '^| \[SEC') finding rows";;
      *.json) echo "   $f: $(git -C "$R" show "$t:$f" | grep -o '"x:[ab]"\|<<<<<<<\|>>>>>>>' | tr '\n' ' ')";;
      *) echo "   $f: $(git -C "$R" show "$t:$f" | tr '\n' '|')";;
    esac; done; }
mt() { echo; echo "\$ git $* "; local o; o=$(git -C "$R" "$@" 2>&1); echo "[exit $?]"; echo "$o" | sed 's/^/   /'; TREE=$(echo "$o" | head -1); }

say "no -X, block passed: which paths conflict"
mt -c core.attributesFile="$BLOCK" merge-tree --write-tree --name-only --merge-base="$P" "$ONTO" "$C"
say "-X theirs, block passed"
mt -c core.attributesFile="$BLOCK" merge-tree --write-tree --name-only -X theirs --merge-base="$P" "$ONTO" "$C"; show "$TREE"
say "-X ours, block passed (orientation check)"
mt -c core.attributesFile="$BLOCK" merge-tree --write-tree --name-only -X ours --merge-base="$P" "$ONTO" "$C"; show "$TREE"
say "-X theirs WITHOUT the block"
mt merge-tree --write-tree --name-only -X theirs --merge-base="$P" "$ONTO" "$C"; show "$TREE"

say "modify/delete under -X theirs (B deleted a pending cost file A appended to)"
git -C "$R" switch -q -c md "$P"; mkdir -p "$R/dev-workflows-cost"; printf -- '- 1\n' > "$R/dev-workflows-cost/pending-s1.md"; git -C "$R" add -A; git -C "$R" commit -q -m pending; P2=$(git -C "$R" rev-parse HEAD)
git -C "$R" rm -q dev-workflows-cost/pending-s1.md; git -C "$R" commit -q -m "B relocates"; O2=$(git -C "$R" rev-parse HEAD)
git -C "$R" switch -q -c md2 "$P2"; printf -- '- 2\n' >> "$R/dev-workflows-cost/pending-s1.md"; git -C "$R" commit -q -am "A appends"; C2=$(git -C "$R" rev-parse HEAD)
mt -c core.attributesFile="$BLOCK" merge-tree --write-tree --name-only -X theirs --merge-base="$P2" "$O2" "$C2"

say "replay.py with REPLAY_X=theirs (no same-named record this time): overwritten shapes kept whole, registers rebuilt"
git -C "$R" switch -q -c onto3 "$P"; side b norunx; git -C "$R" update-ref refs/remotes/origin/main HEAD
git -C "$R" switch -q -c replayed3 "$P"; side a norunx
REPLAY_X=theirs run python3 -I "$ROOT/replay.py" "$R" replayed3 origin/main $RB
T=$(REPLAY_X=theirs python3 -I "$ROOT/replay.py" "$R" replayed3 origin/main $RB | tipof); show "$T" 2>&1 | grep -v samename
X=$(mktemp -d "$ROOT/work/chk.XXXX"); git -C "$R" archive "$T" security | tar -x -C "$X"; cp "$X/$REG/register.json" "$X/c"; $RB "$X" "$SLUG" >/dev/null
echo "   register.json == rebuild(runs) at the replayed tip: $(cmp -s "$X/c" "$X/$REG/register.json" && echo yes || echo NO)"; rm -rf "$X"
echo "(REPLAY_X=scoped: take the replayed version of resume.md / pr-draft.md only; everything else as without -X)"
REPLAY_X=scoped run python3 -I "$ROOT/replay.py" "$R" replayed3 origin/main $RB
T=$(REPLAY_X=scoped python3 -I "$ROOT/replay.py" "$R" replayed3 origin/main $RB | tipof); show "$T" 2>&1 | grep -v samename
echo "(REPLAY_X=scoped on the first pair, which also holds the same-named runs/ record: still refused)"
git -C "$R" update-ref refs/remotes/origin/main "$ONTO"; git -C "$R" branch -f replayed1 "$C"
REPLAY_X=scoped run python3 -I "$ROOT/replay.py" "$R" replayed1 origin/main $RB
echo "(and without REPLAY_X: the overwritten shapes refuse the replay)"
git -C "$R" update-ref refs/remotes/origin/main onto3
run python3 -I "$ROOT/replay.py" "$R" replayed3 origin/main $RB
