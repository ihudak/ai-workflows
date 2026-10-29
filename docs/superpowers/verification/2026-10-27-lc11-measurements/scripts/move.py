#!/usr/bin/env python3
"""Move a checked-out branch from <old> to <tip>, one of several ways (scenario 9).
  move.py <repo> <branch> <old> <tip> <a|b|txn>
  a   : read-tree -m -u <old> <tip>, then update-ref refs/heads/<branch> <tip> <old>
  b   : update-ref refs/heads/<branch> <tip> <old>, then read-tree -m -u <old> <tip>;
        where read-tree refuses, update-ref refs/heads/<branch> <old> <tip> puts the branch back
  txn : update-ref --stdin transaction: start; update <branch> <tip> <old>; prepare (the ref is now
        locked and its old value checked) -> read-tree -m -u <old> <tip> -> commit, or abort where it refused
MOVE_DURING=<shell command> runs between the two steps (a concurrent process in the window).
Prints one JSON line: {"moved": bool, "steps": [...]}; exit 0 when moved."""
import json, os, subprocess, sys

repo, branch, old, tip, how = sys.argv[1:6]
ref = "refs/heads/" + branch
steps = []


def git(*a):
    r = subprocess.run(["git", "-C", repo, *a], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    steps.append({"cmd": "git " + " ".join(a), "exit": r.returncode, "err": r.stderr.strip().split("\n")[0] if r.returncode else ""})
    return r.returncode == 0


def during():
    cmd = os.environ.get("MOVE_DURING")
    if cmd:
        r = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        steps.append({"during": cmd.split("&&")[-2].strip()[:60], "exit": r.returncode, "out": [l for l in r.stdout.strip().split("\n") if "lock" in l or "committed" in l][:2]})


moved = False
if how == "a":
    if git("read-tree", "-m", "-u", old, tip):
        during()
        moved = git("update-ref", "-m", "settle: replayed onto origin", ref, tip, old)
elif how == "b":
    if git("update-ref", "-m", "settle: replayed onto origin", ref, tip, old):
        during()
        moved = git("read-tree", "-m", "-u", old, tip)
        if not moved:
            git("update-ref", "-m", "settle: put back", ref, old, tip)
elif how == "txn":
    p = subprocess.Popen(["git", "-C", repo, "update-ref", "-m", "settle: replayed onto origin", "--stdin"],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    p.stdin.write("start\n"); p.stdin.flush()
    a = p.stdout.readline().strip()
    p.stdin.write("update %s %s %s\nprepare\n" % (ref, tip, old)); p.stdin.flush()
    b = p.stdout.readline().strip()
    steps.append({"txn": [a, b]})
    if b == "prepare: ok":
        during()
        ok = git("read-tree", "-m", "-u", old, tip)
        p.stdin.write("commit\n" if ok else "abort\n"); p.stdin.flush()
        c = p.stdout.readline().strip()
        steps.append({"txn": c})
        moved = ok and c == "commit: ok"
    p.stdin.close(); p.wait()
    err = p.stderr.read().strip()
    if err:
        steps.append({"txn-stderr": err.split("\n")[0]})
print(json.dumps({"moved": moved, "steps": steps}))
sys.exit(0 if moved else 1)
