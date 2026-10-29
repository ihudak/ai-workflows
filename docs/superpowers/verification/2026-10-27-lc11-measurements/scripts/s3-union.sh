#!/usr/bin/env bash
# Scenario 3 — append-type session files under a rebase, with and without §8's info/attributes block.
. "$(dirname "$0")/lib.sh"
git --version

# append-only session commit (no register, no resume.md): isolates the union question
appendc() {
  local repo=$1 tag=$2
  printf '\n## 2026-10-27 %s run\n- api: %s on feat/%s\n' "$tag" "$tag" "$tag" >> "$repo/$IMPL"
  printf -- '- %s entry\n' "$tag" >> "$repo/$FB"
  printf -- '- [ ] %s item\n' "$tag" >> "$repo/$FUP"
  git -C "$repo" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/$tag)" -- "$IMPL" "$FB" "$FUP"
}
reject_and_fetch() {  # A's push rejected because B pushed first; then fetch
  run git -C "$1/A" push --porcelain origin main
  run git -C "$1/A" fetch -q origin
  run git -C "$1/A" log --oneline --graph --all
}
show() { for f in "$@"; do echo "---- $f"; cat -A "$1/../A/$f" 2>/dev/null | sed 's/\$$//' ; done; }
showA() { local w=$1; shift; for f in "$@"; do echo "---- A:$f"; cat "$w/A/$f"; done; }

say "3a — attributes installed in A; A two append commits, B one; rebase"
W=$ROOT/work/s3a; setup_repos "$W"; install_attrs "$W/A"
appendc "$W/A" a1; appendc "$W/A" a2
appendc "$W/B" b1; git -C "$W/B" push -q origin main
reject_and_fetch "$W"
run git -C "$W/A" check-attr merge -- "$IMPL" "$FB" "$FUP" "$RESUME" "$REG/register.json" "$REG/runs/x.json"
run git -C "$W/A" rebase origin/main
run git -C "$W/A" log --oneline --graph
showA "$W" "$IMPL" "$FB" "$FUP"
run git -C "$W/A" push --porcelain origin main

say "3b — the same without the attributes (the rationale's conflict)"
W=$ROOT/work/s3b; setup_repos "$W"
appendc "$W/A" a1; appendc "$W/A" a2
appendc "$W/B" b1; git -C "$W/B" push -q origin main
reject_and_fetch "$W"
run git -C "$W/A" rebase origin/main
run git -C "$W/A" status --short
showA "$W" "$IMPL" "$FUP"
run git -C "$W/A" rebase --abort
run git -C "$W/A" status --short

say "3c — both appended the identical line (attributes installed)"
W=$ROOT/work/s3c; setup_repos "$W"; install_attrs "$W/A"
for c in A B; do printf -- '- same entry\n' >> "$W/$c/$FB"; git -C "$W/$c" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/same)" -- "$FB"; done
git -C "$W/B" push -q origin main
reject_and_fetch "$W"
run git -C "$W/A" rebase origin/main
run git -C "$W/A" log --oneline
showA "$W" "$FB"
echo "(and identical line + a distinct line after it on A's side)"
W=$ROOT/work/s3c2; setup_repos "$W"; install_attrs "$W/A"
printf -- '- same entry\n' >> "$W/B/$FB"; git -C "$W/B" commit -q -m "B" -- "$FB"; git -C "$W/B" push -q origin main
printf -- '- same entry\n- A only\n' >> "$W/A/$FB"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a)" -- "$FB"
git -C "$W/A" fetch -q origin
run git -C "$W/A" rebase origin/main
showA "$W" "$FB"

say "3d — B ticks a follow-up line mid-file / at the end; A appends (attributes installed)"
W=$ROOT/work/s3d1; setup_repos "$W"; install_attrs "$W/A"
sed -i 's/- \[ \] base item 1/- [x] base item 1/' "$W/B/$FUP"; git -C "$W/B" commit -q -m "B ticks item 1" -- "$FUP"; git -C "$W/B" push -q origin main
appendc "$W/A" a1; git -C "$W/A" fetch -q origin
echo "(d1: B ticks line 1 of 2, A appends after line 2 — non-adjacent)"
run git -C "$W/A" rebase origin/main
showA "$W" "$FUP"
W=$ROOT/work/s3d2; setup_repos "$W"; install_attrs "$W/A"
sed -i 's/- \[ \] base item 2/- [x] base item 2/' "$W/B/$FUP"; git -C "$W/B" commit -q -m "B ticks item 2 (last line)" -- "$FUP"; git -C "$W/B" push -q origin main
appendc "$W/A" a1; git -C "$W/A" fetch -q origin
echo "(d2: B ticks the LAST line, A appends right after it — adjacent hunks)"
run git -C "$W/A" rebase origin/main
showA "$W" "$FUP"
echo "(d2 without attributes, for contrast)"
W=$ROOT/work/s3d3; setup_repos "$W"
sed -i 's/- \[ \] base item 2/- [x] base item 2/' "$W/B/$FUP"; git -C "$W/B" commit -q -m "B ticks item 2 (last line)" -- "$FUP"; git -C "$W/B" push -q origin main
appendc "$W/A" a1; git -C "$W/A" fetch -q origin
run git -C "$W/A" rebase origin/main
run git -C "$W/A" diff --name-only --diff-filter=U
run git -C "$W/A" rebase --abort

say "3e — both sides edited the same mid-file line of implementation.md differently (attributes installed)"
W=$ROOT/work/s3e; setup_repos "$W"; install_attrs "$W/A"
sed -i 's/abc1234 on feat\/a/abc1234 on feat\/a (merged by B)/' "$W/B/$IMPL"; git -C "$W/B" commit -q -m "B edits" -- "$IMPL"; git -C "$W/B" push -q origin main
sed -i 's/abc1234 on feat\/a/def5678 on feat\/a (A rewrote)/' "$W/A/$IMPL"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a)" -- "$IMPL"
git -C "$W/A" fetch -q origin
run git -C "$W/A" rebase origin/main
showA "$W" "$IMPL"

say "3f — add/add: both created the same new implementation.md (attributes installed)"
W=$ROOT/work/s3f; setup_repos "$W"; install_attrs "$W/A"
E=$PRD/EPIC-A-1-1-y/implementation.md
for c in A B; do mkdir -p "$W/$c/$(dirname "$E")"; printf '# Implementation record\n\n## 2026-10-27 %s run\n- api: %s\n' "$c" "$c" > "$W/$c/$E"; git -C "$W/$c" add -- "$E"; git -C "$W/$c" commit -q -m "PRD-A-1-1 Add dev-workflows session artifacts ($c)" -- "$E"; done
git -C "$W/B" push -q origin main; git -C "$W/A" fetch -q origin
run git -C "$W/A" rebase origin/main
showA "$W" "$E"

say "3g — modify/delete on a union path (cost-emission §9: a pending cost file relocated and deleted by one side, appended by the other)"
W=$ROOT/work/s3g; setup_repos "$W"
P=dev-workflows-cost/pending-s1.md
mkdir -p "$W/seed/dev-workflows-cost"; printf '# pending\n- 1\n' > "$W/seed/$P"; git -C "$W/seed" add -A; git -C "$W/seed" commit -q -m pending; git -C "$W/seed" push -q origin main
git -C "$W/A" pull -q --no-rebase origin main; git -C "$W/B" pull -q --no-rebase origin main; install_attrs "$W/A"
git -C "$W/B" rm -q -- "$P"; git -C "$W/B" commit -q -m "B relocates pending" ; git -C "$W/B" push -q origin main
printf -- '- 2\n' >> "$W/A/$P"; git -C "$W/A" commit -q -m "NOISSUE Add dev-workflows session artifacts (/a)" -- "$P"
git -C "$W/A" fetch -q origin
run git -C "$W/A" rebase origin/main
run git -C "$W/A" status --short
run git -C "$W/A" rebase --abort

say "3h — the overwritten shape (resume.md, -merge) changed by both: plain rebase vs rebase -X theirs"
W=$ROOT/work/s3h; setup_repos "$W"; install_attrs "$W/A"
printf 'last: B\nnext: /ready B\n' > "$W/B/$RESUME"; git -C "$W/B" commit -q -m B -- "$RESUME"; git -C "$W/B" push -q origin main
printf 'last: A\nnext: /implement A\n' > "$W/A/$RESUME"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a)" -- "$RESUME"
git -C "$W/A" fetch -q origin
run git -C "$W/A" rebase origin/main
run git -C "$W/A" status --short
echo "---- A:$RESUME during the stop"; cat "$W/A/$RESUME"
run git -C "$W/A" rebase --abort
run git -C "$W/A" rebase -X theirs origin/main
echo "---- A:$RESUME after rebase -X theirs"; cat "$W/A/$RESUME"
run git -C "$W/A" log --oneline -3
echo "(-X theirs on a text conflict outside every attribute — e.g. a same-named runs/ record — silently keeps A's side; see s4)"

say "3i — the block passed for this one command only (git -c core.attributesFile=<block>), nothing written to info/attributes"
W=$ROOT/work/s3i; setup_repos "$W"
sed -n '/^# BEGIN workflows-core/,/^# END workflows-core/p' "$ROOT/work/s3a/A/.git/info/attributes" > "$W/block.attributes"
appendc "$W/A" a1; appendc "$W/B" b1; git -C "$W/B" push -q origin main; git -C "$W/A" fetch -q origin
run git -C "$W/A" check-attr merge -- "$IMPL"
run git -C "$W/A" -c core.attributesFile="$W/block.attributes" check-attr merge -- "$IMPL" "$RESUME" "$REG/register.json"
run git -C "$W/A" -c core.attributesFile="$W/block.attributes" rebase origin/main
showA "$W" "$FB"
echo "info/attributes in A: $(cat "$W/A/.git/info/attributes" 2>/dev/null | grep -c . ) non-empty lines"
echo "(and the autostash re-apply under the same -c: a dirty feedback.md over B's append)"
W=$ROOT/work/s3i2; setup_repos "$W"; cp "$ROOT/work/s3i/block.attributes" "$W/"
printf -- '- [ ] a1 item\n' >> "$W/A/$FUP"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a1)" -- "$FUP"
appendc "$W/B" b1; git -C "$W/B" push -q origin main; git -C "$W/A" fetch -q origin
printf -- '- concurrent, uncommitted\n' >> "$W/A/$FB"
run git -C "$W/A" -c core.attributesFile="$W/block.attributes" rebase --autostash origin/main
run git -C "$W/A" status --short

say "3i3 — the -c must ride on every call: a stop (register), then --continue WITHOUT the -c, with a later pick on a union file"
W=$ROOT/work/s3i3; setup_repos "$W"; cp "$ROOT/work/s3i/block.attributes" "$W/"
rec "$W/A" 2 2026-10-27T02:00:00Z a1a1a1a1 s-a1:p a1 open; rebuild "$W/A" >/dev/null
git -C "$W/A" add -A -- "$REG"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a1: register only)" -- "$REG"
printf -- '- a2\n' >> "$W/A/$FB"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a2: feedback only)" -- "$FB"
rec "$W/B" 2 2026-10-27T02:00:00Z b1b1b1b1 s-b1:p b1 open; rebuild "$W/B" >/dev/null; printf -- '- b1\n' >> "$W/B/$FB"
git -C "$W/B" add -A -- "$REG" "$FB"; git -C "$W/B" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/b1)" -- "$REG" "$FB"
git -C "$W/B" push -q origin main; git -C "$W/A" fetch -q origin
run git -C "$W/A" -c core.attributesFile="$W/block.attributes" rebase origin/main
python3 -I "$ROOT/rebuild.py" "$W/A" "$SLUG" >/dev/null; git -C "$W/A" add -- "$REG/register.json" "$REG/register.md"
echo "(continue without the -c)"
run git -C "$W/A" rebase --continue
run git -C "$W/A" diff --name-only --diff-filter=U
run git -C "$W/A" rebase --abort
echo "(the same, continue WITH the -c)"
run git -C "$W/A" -c core.attributesFile="$W/block.attributes" rebase origin/main
python3 -I "$ROOT/rebuild.py" "$W/A" "$SLUG" >/dev/null; git -C "$W/A" add -- "$REG/register.json" "$REG/register.md"
run git -C "$W/A" -c core.attributesFile="$W/block.attributes" rebase --continue
showA "$W" "$FB"
