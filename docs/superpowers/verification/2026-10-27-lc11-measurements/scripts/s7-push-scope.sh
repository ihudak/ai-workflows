#!/usr/bin/env bash
# Scenario 7 — push-scope's precondition: a non-session commit among A's unpushed ones skips the rebase.
. "$(dirname "$0")/lib.sh"
git --version
mk() { local w=$1; setup_repos "$w"; install_attrs "$w/A"
  printf -- '- b1\n' >> "$w/B/$FB"; git -C "$w/B" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/b1)" -- "$FB"; git -C "$w/B" push -q origin main; }

say "7a — A: session commit, a hand commit of the deliverable, session commit; B pushed first"
W=$ROOT/work/s7a; mk "$W"
printf -- '- a1\n' >> "$W/A/$FB"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a1)" -- "$FB"
printf 'Goal: edited by hand.\n' >> "$W/A/$DELIV"; git -C "$W/A" commit -q -m "PRD-A-1 tweak the goal" -- "$DELIV"
printf -- '- a2\n' >> "$W/A/$FB"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a2)" -- "$FB"
echo "(push-scope's base before the fetch — what the rejected push measured)"
run git -C "$W/A" log --oneline origin/main..main
run python3 -I "$ROOT/push_scope.py" "$W/A" main refs/remotes/origin/main
run git -C "$W/A" push --porcelain origin main
run git -C "$W/A" fetch -q origin
echo "(after the fetch: the same commits — B's are on origin/main, not on main)"
run git -C "$W/A" log --oneline origin/main..main
run python3 -I "$ROOT/push_scope.py" "$W/A" main refs/remotes/origin/main
echo "=> the rule skips the rebase and prints today's lines; nothing in the checkout moved:"
run git -C "$W/A" status -sb

say "7b — a local merge commit among A's unpushed commits"
W=$ROOT/work/s7b; mk "$W"
git -C "$W/A" switch -q -c side; printf -- '- side\n' >> "$W/A/$FUP"; git -C "$W/A" commit -q -m "side" -- "$FUP"; git -C "$W/A" switch -q main
printf -- '- a1\n' >> "$W/A/$FB"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a1)" -- "$FB"
git -C "$W/A" merge -q --no-ff -m "merge side" side
git -C "$W/A" fetch -q origin
run git -C "$W/A" log --oneline --graph origin/main..main
run python3 -I "$ROOT/push_scope.py" "$W/A" main refs/remotes/origin/main
echo "(note: rev-list --reverse lists the side commit before the merge; a session-only side branch passes until the merge itself)"

say "7c — every commit the run's own: the rule rebases; afterwards the set to publish is A's rebased commits alone"
W=$ROOT/work/s7c; mk "$W"
printf -- '- a1\n' >> "$W/A/$FB"; git -C "$W/A" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/a1)" -- "$FB"
git -C "$W/A" fetch -q origin
run python3 -I "$ROOT/push_scope.py" "$W/A" main refs/remotes/origin/main
run git -C "$W/A" rebase origin/main
run python3 -I "$ROOT/push_scope.py" "$W/A" main refs/remotes/origin/main

say "7d — B pushes again between A's fetch+rebase and A's push: the second push is rejected too"
printf -- '- b2\n' >> "$W/B/$FB"; git -C "$W/B" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/b2)" -- "$FB"; git -C "$W/B" push -q origin main
run git -C "$W/A" push --porcelain origin main
