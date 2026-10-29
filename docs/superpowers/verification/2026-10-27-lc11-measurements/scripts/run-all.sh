#!/usr/bin/env bash
# Re-runs every LC11 measurement from scratch; each writes logs/<script>.log. Scratch repos go to work/.
cd "$(dirname "$0")" || exit 1
rm -rf work logs; mkdir -p work logs
for s in s1-autostash s2-refuse-dirty s3-union s4-register s4g-real-register s5-abort s6-concurrency s7-push-scope; do
  bash "$s.sh" > "logs/$s.log" 2>&1; echo "$s: exit $?"
done
for m in switch readtree keep; do MOVE=$m bash s8-checkout-free.sh > "logs/s8-checkout-free-$m.log" 2>&1; echo "s8-checkout-free ($m): exit $?"; done
for s in s9-1-move-order s9-2-push-vs-move s9-3-push-race s9-4-mergetree-x-theirs s9-5-session-branch; do
  bash "$s.sh" > "logs/$s.log" 2>&1; echo "$s: exit $?"
done
git --version > logs/git-version.txt
