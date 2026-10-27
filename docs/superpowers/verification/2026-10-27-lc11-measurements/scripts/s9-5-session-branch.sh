#!/usr/bin/env bash
# Scenario 9.5 — session-branch mode: the session files never land on, or push, the default branch.
# Runs the real session-branch.py (read from /workspace/ai-workflows, never modified) against a scratch clone.
. "$(dirname "$0")/lib.sh"
git --version
SB=/workspace/ai-workflows/plugins/workflows-core/scripts/session-branch.py
export GIT_USER_INITIALS=ab
W=$ROOT/work/s95; setup_repos "$W"; A=$W/A
git -C "$A" config workflows.sessionBranch true
say "mode"
run python3 -I "$SB" --specs "$A" mode --default main
say "a run's session files, committed in the mode (commit-artifacts' §8.2 call); B pushes main meanwhile"
printf -- '- a1 entry\n' >> "$A/$FB"; printf '\n## a1 run\n' >> "$A/$IMPL"
printf -- '- b1 entry\n' >> "$W/B/$FB"; git -C "$W/B" commit -q -am b1; git -C "$W/B" push -q origin main
run git -C "$A" fetch -q origin
run python3 -I "$SB" --specs "$A" commit --branch session/ab --default-ref origin/main --message "PRD-A-1 Add dev-workflows session artifacts (/a1)" --include-ahead
echo "-- local main: $(git -C "$A" rev-parse --short main); commits on main that origin/main lacks: $(git -C "$A" rev-list --count main --not origin/main)"
run git -C "$A" log --oneline --graph session/ab
echo "-- §8.4: the push names the session branch, never main:"
run git -C "$A" push --porcelain -u origin session/ab
echo "-- main is behind origin/main only (a fast-forward for §3.4's catch-up, never a rejection):"
run git -C "$A" status -sb
