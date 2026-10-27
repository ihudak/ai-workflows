#!/usr/bin/env python3
"""A checkout-free alternative to an in-checkout rebase (scenarios 8 and 9).
  replay.py <repo> <branch> <onto> <rebuild-cmd...>
Replays `rev-list --reverse <branch> --not <onto>` onto <onto> with `git merge-tree --write-tree
--merge-base=<parent>`, settling a conflict confined to security/<slug>/register.{json,md} by a rebuild run
in a temporary directory over the merged tree's security/<slug>/, and builds each commit with commit-tree
(author and message kept). A commit whose replayed tree equals its new parent's is dropped (listed in
"dropped"). It never touches the checkout, the index or any ref; prints {"tip": ...} or {"refused": ...}.
Environment:
  REPLAY_ATTRS=<file>  pass the §8 block as `-c core.attributesFile=<file>` to every git call
  REPLAY_X=theirs      merge-tree -X theirs (keeps the replayed commit's version of an overwritten shape
                       whole); then every register whose files both sides changed is rebuilt regardless.
  REPLAY_X=scoped      no -X; a conflict on an overwritten shape (resume.md under dev-workflows/, pr-draft.md)
                       takes the replayed commit's version of that path alone; any other conflict still refuses."""
import json, os, re, shutil, subprocess, sys, tempfile

repo, branch, onto = sys.argv[1], sys.argv[2], sys.argv[3]
rebuild_cmd = sys.argv[4:]
REGFILE = re.compile(r"^security/([^/]+)/register\.(json|md)$")
PRE = ["-c", "core.attributesFile=" + os.environ["REPLAY_ATTRS"]] if os.environ.get("REPLAY_ATTRS") else []
SCOPED = os.environ.get("REPLAY_X") == "scoped"
X = ["-X", os.environ["REPLAY_X"]] if os.environ.get("REPLAY_X") and not SCOPED else []
OVERWRITTEN = re.compile(r"(^|/)dev-workflows/resume\.md$|(^|/)pr-draft\.md$")


def git(*a, env=None, data=None, check=True):
    r = subprocess.run(["git", "-C", repo, *PRE, *a], input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=dict(os.environ, **env) if env else None)
    if check and r.returncode != 0:
        print(json.dumps({"refused": "git %s failed: %s" % (a[0], r.stderr.decode().strip())})); sys.exit(1)
    return r


def out(*a, **k):
    return git(*a, **k).stdout.decode().strip()


def names(a, b):
    return set(p for p in out("diff", "--name-only", "--no-renames", a, b).split("\n") if p)


base = out("rev-parse", onto)
commits = out("rev-list", "--reverse", "refs/heads/" + branch, "--not", onto).split()
dropped = []
for c in commits:
    parent = out("rev-parse", c + "^")
    r = git("merge-tree", "--write-tree", "--name-only", "--no-messages", *X, "--merge-base=" + parent, base, c, check=False)
    lines = r.stdout.decode().split("\n")
    tree, conflicted = lines[0], [l for l in lines[1:] if l]
    if r.returncode not in (0, 1):
        print(json.dumps({"refused": "merge-tree could not run on %s: %s" % (c[:7], r.stderr.decode().strip())})); sys.exit(1)
    slugs, take = set(), []
    for p in conflicted:
        m = REGFILE.match(p)
        if SCOPED and OVERWRITTEN.search(p) and git("cat-file", "-e", "%s:%s" % (c, p), check=False).returncode == 0:
            take.append(p)
            continue
        if not m:
            print(json.dumps({"refused": "conflict in %s replaying %s" % (p, c[:7])})); sys.exit(1)
        slugs.add(m.group(1))
    if X:  # -X settles the registers silently: rebuild every one both sides changed
        for p in names(parent, c) & names(parent, base):
            m = REGFILE.match(p)
            if m:
                slugs.add(m.group(1))
    if slugs or take:
        tmp = tempfile.mkdtemp()
        try:
            env = {"GIT_INDEX_FILE": os.path.join(tmp, "index")}
            git("read-tree", tree, env=env)
            for p in take:  # the replayed commit's own version, whole
                git("update-index", "--cacheinfo", "100644,%s,%s" % (out("rev-parse", "%s:%s" % (c, p)), p), env=env)
            for s in sorted(slugs):
                arch = git("archive", tree, "security/" + s).stdout
                subprocess.run(["tar", "-x", "-C", tmp], input=arch, check=True)
                rb = subprocess.run(rebuild_cmd + [tmp, s], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if rb.returncode != 0:
                    print(json.dumps({"refused": "rebuild failed: %s" % rb.stderr.decode().strip()[-200:]})); sys.exit(1)
                for f in ("register.json", "register.md"):
                    blob = out("hash-object", "-w", os.path.join(tmp, "security", s, f))
                    git("update-index", "--cacheinfo", "100644,%s,security/%s/%s" % (blob, s, f), env=env)
            tree = out("write-tree", env=env)
        finally:
            shutil.rmtree(tmp)
    fmt = out("log", "-1", "--format=%an%x00%ae%x00%aI%x00%B", c).split("\0", 3)
    if out("rev-parse", base + "^{tree}") == tree:
        dropped.append(c[:7])  # already there: dropped, as rebase drops a commit that becomes empty
        continue
    env = {"GIT_AUTHOR_NAME": fmt[0], "GIT_AUTHOR_EMAIL": fmt[1], "GIT_AUTHOR_DATE": fmt[2]}
    base = out("commit-tree", tree, "-p", base, "-F", "-", env=env, data=fmt[3].encode())
print(json.dumps({"tip": base, "replayed": len(commits), "dropped": dropped}))
