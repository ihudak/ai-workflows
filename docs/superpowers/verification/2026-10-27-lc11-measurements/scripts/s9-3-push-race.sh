#!/usr/bin/env bash
# Scenario 9.3 — the push race: B pushes between A's replay and A's push; a bounded re-fetch + re-replay.
# Order: replay -> move (update-ref --stdin transaction) -> push; up to MAX attempts.
. "$(dirname "$0")/lib.sh"; . "$(dirname "$0")/lib9.sh"
git --version
NB=1
bpush() {  # B lands another session commit on origin
  local w=$1; NB=$((NB+1)); git -C "$w/B" pull -q --no-rebase origin main 2>/dev/null
  printf -- '- b%s entry\n' $NB >> "$w/B/$FB"; rec "$w/B" $((NB+1)) "2026-10-27T1$NB:00:00Z" "b${NB}b${NB}b${NB}b${NB}" "scan-b$NB:p1" "b$NB" open; rebuild "$w/B" >/dev/null
  git -C "$w/B" add -A; git -C "$w/B" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/b$NB)"; git -C "$w/B" push -q origin main; }
ms() { echo $(( ($(date +%s%N) - $1) / 1000000 )); }
settle_cf() {  # settle_cf <workdir> <max attempts> <races: attempts in which B pushes just before A's push>
  local w=$1 max=$2 races=$3 a=$1/A k=0 t0 res tip
  while [ $k -lt "$max" ]; do
    k=$((k+1)); t0=$(date +%s%N)
    git -C "$a" fetch -q origin
    python3 -I "$ROOT/push_scope.py" "$a" main refs/remotes/origin/main >/dev/null || { echo "attempt $k: push-scope fails -> today's lines"; return 1; }
    res=$(replay9 "$a"); tip=$(printf '%s' "$res" | tipof)
    [ -z "$tip" ] && { echo "attempt $k: replay refused $res -> today's lines"; return 1; }
    if [ "$tip" != "$(git -C "$a" rev-parse main)" ]; then
      python3 -I "$ROOT/move.py" "$a" main "$(git -C "$a" rev-parse main)" "$tip" txn >/dev/null || { echo "attempt $k: move refused -> nothing pushed; today's lines"; return 1; }
    fi
    local t1; t1=$(ms "$t0")
    [ "$k" -le "$races" ] && bpush "$w"
    local p; p=$(git -C "$a" push --porcelain origin main 2>&1);
    if printf '%s' "$p" | grep -q $'^\t\|^ \t\|^\*'; then :; fi
    if printf '%s\n' "$p" | grep -q '^!'; then
      echo "attempt $k: $(printf '%s\n' "$p" | grep '^!' | cut -f3) — fetch+push-scope+replay+move ${t1} ms, total $(ms "$t0") ms (replay: $res)"
    else
      echo "attempt $k: pushed $(printf '%s\n' "$p" | grep 'refs/heads/main' | cut -f3) — fetch+push-scope+replay+move ${t1} ms, total $(ms "$t0") ms (replay: $res)"; return 0
    fi
  done
  echo "gave up after $max attempts -> today's lines (local main stays moved onto the last replay)"; return 1
}
content() {  # origin's content and what local would still push
  local w=$1 T; T=$(mktemp -d "$ROOT/work/chk.XXXX"); git -C "$w/origin.git" archive main | tar -x -C "$T"
  echo "   origin feedback.md entries: $(grep -c entry "$T/$FB") lines, duplicates: $(grep entry "$T/$FB" | sort | uniq -d | wc -l)"
  cp "$T/$REG/register.json" "$T/c.json"; $RB "$T" "$SLUG" >/dev/null
  echo "   origin register.json == rebuild(runs): $(cmp -s "$T/c.json" "$T/$REG/register.json" && echo yes || echo NO)"
  rm -rf "$T"
  git -C "$w/A" fetch -q origin; echo "   local vs origin: $(git -C "$w/A" status -sb | head -1)"; }

say "R1 — B races A twice; the third attempt pushes (max 3); the user's dirty files in place throughout"
W=$ROOT/work/s93-r1; NB=1; mk9 "$W"; dirty9 "$W/A"; userbytes "$W/A" > "$W/ub0"; git -C "$W/A" status --porcelain > "$W/st0"
settle_cf "$W" 3 2
content "$W"
userbytes "$W/A" > "$W/ub1"; git -C "$W/A" status --porcelain > "$W/st1"
echo "   user files' bytes unchanged: $(cmp -s "$W/ub0" "$W/ub1" && echo yes || echo NO); status letters unchanged: $(cmp -s "$W/st0" "$W/st1" && echo yes || echo NO)"

say "R2 — B races A on all three attempts: the run gives up"
W=$ROOT/work/s93-r2; NB=1; mk9 "$W"; dirty9 "$W/A"
settle_cf "$W" 3 3
content "$W"
echo "-- the next run's settle (no race):"; settle_cf "$W" 3 0; content "$W"

say "R0 — no race: one attempt"
W=$ROOT/work/s93-r0; NB=1; mk9 "$W"; dirty9 "$W/A"
settle_cf "$W" 3 0; content "$W"
