#!/usr/bin/env bash
# Scenario 9.2 — push before move vs move before push, when the move is refused (a dirty collision).
. "$(dirname "$0")/lib.sh"; . "$(dirname "$0")/lib9.sh"
git --version
mv_txn() { python3 -I "$ROOT/move.py" "$1" main "$(git -C "$1" rev-parse main)" "$2" txn; }
count() { echo "   $(basename "$2"): $(grep -c -- "$3" "$1/$2") × '$3'"; }
check_content() {  # what origin holds: each entry once, register == rebuild
  local w=$1 T; T=$(mktemp -d "$ROOT/work/chk.XXXX"); git -C "$w/origin.git" archive main | tar -x -C "$T"
  echo "-- origin/main content:"; for e in "a1 entry" "b1 entry" "a2 entry" "b2 entry"; do count "$T" "$FB" "$e"; done
  for e in "## a1 run" "## a2 run"; do count "$T" "$IMPL" "$e"; done
  [ -f "$T/$RESUME" ] && echo "   resume.md: $(tr '\n' ' ' < "$T/$RESUME")"
  cp "$T/$REG/register.json" "$T/c.json"; $RB "$T" "$SLUG" >/dev/null
  echo "   register.json == rebuild(runs): $(cmp -s "$T/c.json" "$T/$REG/register.json" && echo yes || echo NO)  runs: $(ls "$T/$REG/runs" | wc -l)"
  rm -rf "$T"; }
a2commit() {  # the next run's own session commit on local main
  local a=$1; printf -- '- a2 entry\n' >> "$a/$FB"; printf '\n## a2 run\n' >> "$a/$IMPL"
  rec "$a" 3 2026-10-27T03:00:00Z a2a2a2a2 scan-a2:p1 a2 open; rebuild "$a" >/dev/null
  git -C "$a" add -A -- "$FB" "$IMPL" "$REG"; git -C "$a" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a2)" -- "$FB" "$IMPL" "$REG"; }
b2push() {  # B pushes again after A's push
  local w=$1; git -C "$w/B" pull -q --no-rebase origin main 2>/dev/null
  printf -- '- b2 entry\n' >> "$w/B/$FB"; rec "$w/B" 4 2026-10-27T04:00:00Z b2b2b2b2 scan-b2:p1 b2 open; rebuild "$w/B" >/dev/null
  [ "${3:-}" = resume ] && printf 'last: b2\n' > "$w/B/$RESUME"
  git -C "$w/B" add -A; git -C "$w/B" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/b2)"; git -C "$w/B" push -q origin main; }
nextrun_view() {
  local a=$1
  run git -C "$a" fetch -q origin
  run git -C "$a" status -sb
  echo "   §3.4 catch-up test (merge-base --is-ancestor HEAD origin/main): $(git -C "$a" merge-base --is-ancestor HEAD origin/main && echo 'behind -> pull' || echo 'not behind -> no catch-up')"
  run git -C "$a" pull --ff-only --no-rebase origin main
  run python3 -I "$ROOT/push_scope.py" "$a" main refs/remotes/origin/main
  run git -C "$a" cherry -v origin/main main
}

say "P1 — push BEFORE move; the move is refused; origin does not move again before the next run"
W=$ROOT/work/s92-p1; mk9 "$W" deliv; printf 'user edit\n' >> "$W/A/$DELIV"
TIP=$(replay9 "$W/A" | tipof)
run git -C "$W/A" push --porcelain origin "$TIP:refs/heads/main"
mv_txn "$W/A" "$TIP"; echo
echo "-- the next run's view:"; nextrun_view "$W/A"
echo "-- the next run commits its own session files (a2) on local main, its push is rejected, it replays:"
a2commit "$W/A"; run git -C "$W/A" push --porcelain origin main
run python3 -I "$ROOT/replay.py" "$W/A" main origin/main $RB
TIP2=$(replay9 "$W/A" | tipof); run git -C "$W/A" push --porcelain origin "$TIP2:refs/heads/main"; mv_txn "$W/A" "$TIP2"; echo
check_content "$W"
echo "-- the user discards the colliding edit; the run after that replays again:"
git -C "$W/A" restore -- "$DELIV"; git -C "$W/A" fetch -q origin
run python3 -I "$ROOT/replay.py" "$W/A" main origin/main $RB
T3=$(replay9 "$W/A" | tipof); echo "   replay tip == origin/main? $([ "$T3" = "$(git -C "$W/A" rev-parse origin/main)" ] && echo yes || echo no)"
mv_txn "$W/A" "$T3"; echo; run git -C "$W/A" status -sb
echo "-- what local main now holds, and would push next:"; for e in "a1 entry" "a2 entry" "b1 entry"; do count "$W/A" "$FB" "$e"; done
run git -C "$W/A" diff --stat origin/main main
check_content "$W"

say "P2 — push BEFORE move; move refused; B pushes again before the next run (origin moved past the replays)"
W=$ROOT/work/s92-p2; mk9 "$W" deliv; printf 'user edit\n' >> "$W/A/$DELIV"
TIP=$(replay9 "$W/A" | tipof); run git -C "$W/A" push --porcelain origin "$TIP:refs/heads/main" >/dev/null; mv_txn "$W/A" "$TIP" >/dev/null
b2push "$W"
git -C "$W/A" restore -- "$DELIV"; git -C "$W/A" fetch -q origin
echo "-- the next run re-replays local main (its pre-replay a1) onto origin (b1, a1', b2):"
run python3 -I "$ROOT/replay.py" "$W/A" main origin/main $RB
T2=$(replay9 "$W/A" | tipof)
T=$(mktemp -d "$ROOT/work/chk.XXXX"); git -C "$W/A" archive "$T2" | tar -x -C "$T"
echo "-- what that replay would publish:"; for e in "a1 entry" "b1 entry" "b2 entry"; do count "$T" "$FB" "$e"; done; count "$T" "$IMPL" "## a1 run"; rm -rf "$T"
echo "   git diff origin/main <replay tip> --stat:"; git -C "$W/A" diff --stat origin/main "$T2"

say "P2x — the same, with resume.md overwritten by a1 and later by b2, replayed with -X theirs"
W=$ROOT/work/s92-p2x; mk9 "$W" deliv
printf 'last: a1\n' > "$W/A/$RESUME"; git -C "$W/A" commit -q --amend --no-edit -- "$RESUME" "$FB" "$IMPL" "$REG"; printf 'user edit\n' >> "$W/A/$DELIV"
export REPLAY_X=theirs
TIP=$(replay9 "$W/A" | tipof); git -C "$W/A" push -q --porcelain origin "$TIP:refs/heads/main" >/dev/null; mv_txn "$W/A" "$TIP" >/dev/null
b2push "$W" x resume
git -C "$W/A" restore -- "$DELIV"; git -C "$W/A" fetch -q origin
echo "   origin's resume.md: $(git -C "$W/A" show origin/main:"$RESUME")"
T2=$(replay9 "$W/A" | tipof); echo "   re-replay (-X theirs) of the already-published a1 -> resume.md: $(git -C "$W/A" show "$T2:$RESUME")"
unset REPLAY_X

say "M — move BEFORE push: the move is refused, so nothing is pushed"
W=$ROOT/work/s92-m; mk9 "$W" deliv; printf 'user edit\n' >> "$W/A/$DELIV"
OLD=$(git -C "$W/A" rev-parse main); TIP=$(replay9 "$W/A" | tipof)
mv_txn "$W/A" "$TIP" && run git -C "$W/A" push --porcelain origin main || echo "=> move refused: no push; everything as it was"
echo "-- the next run's view:"; nextrun_view "$W/A"
b2push "$W"
echo "-- B pushed again; the user then discards the colliding edit; the next run (a2 too) replays, moves, pushes:"
git -C "$W/A" restore -- "$DELIV"; a2commit "$W/A"; git -C "$W/A" fetch -q origin
run python3 -I "$ROOT/replay.py" "$W/A" main origin/main $RB
TIP=$(replay9 "$W/A" | tipof); mv_txn "$W/A" "$TIP" && echo && run git -C "$W/A" push --porcelain origin main
check_content "$W"
