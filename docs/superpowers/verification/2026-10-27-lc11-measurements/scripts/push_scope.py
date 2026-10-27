#!/usr/bin/env python3
"""specs-repo-git §4 step 5's push-scope test, as written: oldest first, each commit the push would
publish (rev-list --reverse refs/heads/<branch> --not <base>) must be a non-merge commit whose every
path is an ARTIFACT path (§2.1). Prints one line per commit and exits 0 (all the run's own) or 1."""
import re, subprocess, sys

ARTIFACT = [
    r"^(specs|specifications|vis)/.+/dev-workflows/",
    r"^documentation/[^/]+/dev-workflows/",
    r"^dev-workflows-feedback/",
    r"^dev-workflows-cost/",
    r"^security/[^/]+/(runs/|scans/|dev-workflows/|register\.(json|md)$)",
    r"^(specs|specifications|vis)/.+/(implementation|follow-ups|pr-draft|[^/]+-implementation-gaps|_security)\.md$",
]
EXCLUDED = (r"^(specs|specifications|vis)/(.+/)?(brd|grounding|interview|design|attachments|revisions"
            r"|bundle-[0-9]{8}|customer-sent-[0-9]{8}|Doc screenshots)/")


def git(repo, *a):
    return subprocess.run(["git", "-C", repo, *a], stdout=subprocess.PIPE, check=True).stdout.decode()


def artifact(p):
    return any(re.search(x, p) for x in ARTIFACT) and not re.search(EXCLUDED, p)


repo, branch, base = sys.argv[1], sys.argv[2], sys.argv[3]
shas = git(repo, "rev-list", "--reverse", "refs/heads/" + branch, "--not", base).split()
ok = True
for s in shas:
    parents = git(repo, "rev-list", "--parents", "-n", "1", s).split()
    paths = [p for p in git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", "--root", "--no-renames", s).split("\0") if p]
    bad = [p for p in paths if not artifact(p)]
    verdict = "session" if len(parents) <= 2 and not bad else ("merge" if len(parents) > 2 else "NOT-session: " + ", ".join(bad))
    print("%s %s  %s" % (s[:7], git(repo, "log", "-1", "--format=%s", s).strip(), verdict))
    if verdict != "session":
        ok = False
        break
print("push-scope:", "PASS (every commit is the run's own) -> rebase allowed" if ok else "FAIL -> no rebase; today's lines")
sys.exit(0 if ok else 1)
