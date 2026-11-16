#!/usr/bin/env python3
"""key-discovery.py — the commits and pull requests that name a key.

  key-discovery.py scan --key <K> [--key <K> ...] --repo <clone> [--repo <clone> ...]
                        --scope head|default [--probe] [--no-github]
                        [--exclude <clone> ...] [--owner-of <clone> ...]
                        [--docs-root <dir> [--docs-content <path> ...]]
  key-discovery.py docs-check --docs-root <dir> [--docs-content <path> ...] --base <rev> [--head <rev>]
  key-discovery.py --selftest

scan: in each clone, the non-merge commits on one ref whose message names a key whole -- not
inside a longer key, and not followed or preceded by a letter, a digit, "_" or "-" -- matched
case-insensitively. --scope head scans HEAD; --scope default scans the origin's default branch
(origin/HEAD, else origin/main, else origin/master) and falls back to HEAD. --probe adds, on a
clone where no commit matched, every commit naming a key bare, merge commits included -- reported,
never read. Unless --no-github, where `gh` is installed and logged in to github.com, it also
searches the GitHub pull requests of the clones' owners for the keys, keeps those whose title or
body names a key whole, and lists the commits each merged one landed where its merge commit is on
the scanned ref and brings in no other branch's merges (a release pull request is listed, never
read). Dates are local time. GitHub calls stop after a time budget; a failure there never costs the
commit scan. --exclude names a clone whose repository is never code, such as the specs
repository: every --repo with its origin's slug is left unscanned, and every pull request in a
repository of that name is dropped. --owner-of names a clone that is not scanned but whose GitHub
owner is searched too. Prints one JSON document, indented so a reader can take it line by line;
fetches nothing and writes nothing.

--docs-root names the documentation root -- a site's own directory, or a repository's top level
-- and the repository holding it is read by path, not left out. Its content paths are the root's
own directory where it lies below the top level, and each --docs-content, relative to the top level
and matched as the literal path it is (an absolute one, or one with a ".." segment, is rejected and
listed); the documentation set is those and FAMILY_DOC_PATHS. Every --repo that is that repository,
by its path or by its origin's slug, is read under the set. "scanned" counts the non-merge commits
touching a path outside it, in a walk with the set as exclude pathspecs and --full-history -- a
pathspec alone simplifies history, and a side branch netting to nothing would vanish from the
count. Each commit the scan or the probe matched there, and each a merged pull request there
landed, is then tested on its own, which walks no history and so needs no --full-history: a
merge against its first parent, any other commit against its parent (a root commit against the
empty tree). A commit naming a key that touches nothing outside the set is listed as
documentation only and never found, the probe drops a commit that touches, and a merge that
brought in, nothing outside it, and a merged pull request keeps only the landed commits touching a
path outside it, listing the rest. Where no content path is known, or one is the whole
repository, or --exclude names the repository too, it is left out whole, as --exclude leaves one
out; where no --repo is that repository, its pull requests are dropped by name. A root in no git
work tree changes nothing. docs-check prints, as "outside", the paths
`git diff --name-only <base> <head>` lists outside the same documentation set, and [] where
"docs" is null or its "rule" is "left-out".

Exit 0: it ran -- a clone or a search it could not reach is a field of the result. Exit 2: it
could not run; the cause is on stderr. Python standard library only.
"""

import argparse
import contextlib
import itertools
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

GIT_TIMEOUT = 60
GH_TIMEOUT = 30
SSH_TIMEOUT = 5
BATCH = 6
EDGE_L = r"(^|[^A-Za-z0-9_-])"
EDGE_R = r"([^A-Za-z0-9_-]|$)"
ERE_META = set("\\.[](){}*+?^$|")
PLAIN_HOST_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9.-]*")
OWNER_REPO_RE = re.compile(r"[^/\s]+/[^/\s]+")
FMT = "%H%x1f%cd%x1f%B"
SEARCH_LIMIT = 1000
GH_BUDGET = 300
_now = time.monotonic  # the budget's clock; the selftest replaces it
STATES = {"merged": "MERGED", "open": "OPEN", "closed": "CLOSED"}

# The family's own paths: what the family itself writes into a documentation repository, and the configuration
# and navigation files of the generators its docs signals name.
# Each is matched from the repository's top level: "literal" as the path written, a directory with everything
# below it; "glob" as a pattern whose "*" stops at "/", so "*.md" is the top level's markdown and nothing deeper,
# and whose leading "**/" is any depth, the top level included. A generator's configuration and navigation files
# match at any depth, since a site kept in a subfolder has them there and no profile field records them.
FAMILY_DOC_PATHS = (
    ("literal", ".dev-workflows"),
    ("literal", ".claude"),
    ("literal", "docs"),
    ("literal", ".docstack"),
    ("glob", "*.md"),
    ("glob", "**/_snippets/**"),
    ("glob", "**/mkdocs.yml"),
    ("glob", "**/mkdocs.*.yml"),
    ("glob", "**/docusaurus.config.[jt]s"),
    ("glob", "**/docusaurus.config.[cm]js"),
    ("glob", "**/sidebars.[jt]s"),
    ("glob", "**/sidebars.[cm]js"),
    ("glob", "**/_category_.json"),
    ("glob", "**/_category_.yml"),
    ("glob", "**/antora.yml"),
    ("glob", "**/nav.adoc"),
    ("glob", "**/.pages"),
    ("glob", "**/SUMMARY.md"),
    ("literal", ".vale"),
    ("literal", "_vale"),
    ("literal", "vale.ini"),
    ("literal", ".vale.ini"),
    ("literal", "_vale.ini"),
)


class Unrunnable(Exception):
    """The script could not run; main() prints the message and exits 2."""


class SearchFailed(Exception):
    pass


class RateLimited(SearchFailed):
    pass


# ---- self-test ----

def _git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=selftest", "-c", "user.email=selftest@example.invalid",
                           "-c", "init.defaultBranch=main", *args],
                          cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def _repo(tmp, name, remote=None):
    path = os.path.join(tmp, name)
    os.makedirs(path)
    _git(path, "init", "-q")
    if remote:
        _git(path, "remote", "add", "origin", remote)
    return path


_FILES = itertools.count()


def _commit(repo, message, name=None):
    """Append the message to `name` -- a path, or a tuple of paths, below the repository -- and commit it."""
    names = (name,) if isinstance(name, str) else tuple(name or ("f%d.txt" % next(_FILES),))
    for each in names:
        path = os.path.join(repo, each)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(message + "\n")
        _git(repo, "add", "--", ":(literal)" + each)  # a path such as ":odd/p.md" is a path, never pathspec magic
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def _merge(repo, branch, message):
    _git(repo, "merge", "-q", "--no-ff", "-m", message, branch)
    return _git(repo, "rev-parse", "HEAD")


def _stub(tmp, name, rules):
    """An executable `name` first on PATH that answers from `rules` and logs every argv.

    rules: [(tokens, rc, stdout, stderr)] -- the first rule whose tokens all appear in argv answers.
    """
    bindir = os.path.join(tmp, "bin")
    os.makedirs(bindir, exist_ok=True)
    log = os.path.join(tmp, name + ".log")
    if os.path.exists(log):
        os.remove(log)
    src = ("#!%s\nimport json, sys\nRULES = %r\nLOG = %r\n"
           "with open(LOG, 'a') as fh:\n    fh.write(json.dumps(sys.argv[1:]) + '\\n')\n"
           "for tokens, rc, out, err in RULES:\n"
           "    if all(t in sys.argv[1:] for t in tokens):\n"
           "        sys.stdout.write(out); sys.stderr.write(err); sys.exit(rc)\n"
           "sys.stderr.write('no rule'); sys.exit(1)\n") % (sys.executable, rules, log)
    path = os.path.join(bindir, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(src)
    os.chmod(path, 0o755)
    if not os.environ["PATH"].startswith(bindir + os.pathsep):
        os.environ["PATH"] = bindir + os.pathsep + os.environ["PATH"]
    return log


def _calls(log):
    if not os.path.exists(log):
        return []
    with open(log, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _search_hit(owner_repo, number, title, body="", state="merged"):
    return {"number": number, "title": title, "body": body, "state": state,
            "url": "https://github.com/%s/pull/%d" % (owner_repo, number),
            "repository": {"name": owner_repo.split("/")[1], "nameWithOwner": owner_repo}}


def _gh(tmp, hits=(), views=None, auth=0, search_rc=0, search_err=""):
    views = views or {}
    rules = [(["auth", "status"], auth, "", "" if auth == 0 else "not logged in")]
    for number, view in views.items():
        rules.append((["pr", "view", str(number)], 0, json.dumps(view), ""))
    rules.append((["search", "prs"], search_rc, json.dumps(list(hits)) if search_rc == 0 else "", search_err))
    return _stub(tmp, "gh", rules)


def _no_ssh_alias(tmp):
    return _stub(tmp, "ssh", [(["-G"], 0, "hostname unknown.invalid\n", "")])


def _github_clone(tmp, name="app", owner="acme"):
    return _repo(tmp, name, "git@github.com:%s/%s.git" % (owner, name))


def case_boundary(tmp):
    r = _repo(tmp, "r")
    hits = {_commit(r, m): m for m in ("feat: intake [ACME-7]", "fix: acme-7 lowercase", "ACME-7: at the start",
                                       "body\n\nRefs ACME-7.")}
    misses = [_commit(r, m) for m in ("feat: [ACME-77]", "feat: [ACME-70-01]", "XACME-7", "Merge in feat/ACME-7-x",
                                      "ACME-7_x", "nothing")]
    out = discover(["ACME-7"], [r], "head", github=False)
    found = {c["sha"] for c in out["commits"]}
    assert found == set(hits), (found, hits)
    assert not found & set(misses)
    assert all(c["keys"] == ["ACME-7"] and c["via"] == "message" and c["prs"] == [] for c in out["commits"])
    assert out["repos"][0]["matched"] == 4 and out["repos"][0]["scanned"] == 10, out["repos"]


def case_metacharacters_are_literal(tmp):
    r = _repo(tmp, "r")
    good = _commit(r, "work on W.1 done")
    _commit(r, "work on WX1 done")
    out = discover(["W.1"], [r], "head", github=False)
    assert [c["sha"] for c in out["commits"]] == [good], out["commits"]
    quiet = _repo(tmp, "quiet")
    bare = _commit(quiet, "fooW.1bar")
    _commit(quiet, "fooWX1bar")
    probed = discover(["W.1"], [quiet], "head", probe=True, github=False)["repos"][0]["probe"]
    assert [p["sha"] for p in probed] == [bare], probed


def case_merges_are_not_scanned(tmp):
    r = _repo(tmp, "r")
    _commit(r, "base")
    _git(r, "checkout", "-q", "-b", "topic")
    own = _commit(r, "topic work [ACME-7]")
    _git(r, "checkout", "-q", "main")
    _commit(r, "main moves on")
    merge = _merge(r, "topic", "Merge pull request #3 [ACME-7]")
    out = discover(["ACME-7"], [r], "head", github=False)
    shas = [c["sha"] for c in out["commits"]]
    assert own in shas and merge not in shas, shas


def case_each_commit_names_its_keys(tmp):
    r = _repo(tmp, "r")
    both = _commit(r, "ACME-7 and ACME-8")
    one = _commit(r, "only ACME-8")
    out = discover(["ACME-7", "ACME-8"], [r], "head", github=False)
    keys = {c["sha"]: c["keys"] for c in out["commits"]}
    assert keys == {both: ["ACME-7", "ACME-8"], one: ["ACME-8"]}, keys


def case_probe_only_at_zero_matches(tmp):
    quiet = _repo(tmp, "quiet")
    _commit(quiet, "base")
    _git(quiet, "checkout", "-q", "-b", "feat/ACME-7-intake")
    _commit(quiet, "intake work")
    _git(quiet, "checkout", "-q", "main")
    merge = _merge(quiet, "feat/ACME-7-intake", "Merge branch 'feat/ACME-7-intake'")
    longer = _commit(quiet, "unrelated [ACME-77]")
    loud = _repo(tmp, "loud")
    _commit(loud, "[ACME-7] done")
    _commit(loud, "Merge branch 'feat/ACME-7-x'")
    out = discover(["ACME-7"], [quiet, loud], "head", probe=True, github=False)
    q, l = out["repos"]
    assert q["matched"] == 0 and {p["sha"] for p in q["probe"]} == {merge, longer}, q
    assert all(set(p) == {"sha", "date", "subject"} for p in q["probe"])
    assert l["matched"] == 1 and l["probe"] == [], l
    assert discover(["ACME-7"], [quiet], "head", github=False)["repos"][0]["probe"] == []


def case_scope_default_reads_the_origin_default_branch(tmp):
    r = _repo(tmp, "r")
    landed = _commit(r, "landed [ACME-7]")
    _git(r, "update-ref", "refs/remotes/origin/main", landed)
    _git(r, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    _git(r, "checkout", "-q", "-b", "topic")
    unmerged = _commit(r, "unmerged [ACME-7]")
    head = discover(["ACME-7"], [r], "head", github=False)
    default = discover(["ACME-7"], [r], "default", github=False)
    assert {c["sha"] for c in head["commits"]} == {landed, unmerged}
    assert [c["sha"] for c in default["commits"]] == [landed]
    assert head["repos"][0]["ref"] == "HEAD" and default["repos"][0]["ref"] == "origin/main", default["repos"]
    _git(r, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
    assert discover(["ACME-7"], [r], "default", github=False)["repos"][0]["ref"] == "origin/main"
    _git(r, "update-ref", "-d", "refs/remotes/origin/main")
    _git(r, "update-ref", "refs/remotes/origin/master", landed)
    assert discover(["ACME-7"], [r], "default", github=False)["repos"][0]["ref"] == "origin/master"


def case_scope_default_without_an_origin_falls_back_to_head(tmp):
    r = _repo(tmp, "r")
    sha = _commit(r, "[ACME-7]")
    out = discover(["ACME-7"], [r], "default", github=False)
    assert out["repos"][0]["ref"] == "HEAD (no origin default branch)", out["repos"]
    assert [c["sha"] for c in out["commits"]] == [sha]


def case_a_failing_clone_leaves_the_others(tmp):
    good = _repo(tmp, "good")
    sha = _commit(good, "[ACME-7]")
    empty = _repo(tmp, "empty")
    out = discover(["ACME-7"], [empty, good], "head", github=False)
    bad, ok = out["repos"]
    assert bad["error"] and bad["scanned"] is None and bad["matched"] == 0, bad
    assert ok["error"] is None and [c["sha"] for c in out["commits"]] == [sha]


def case_no_github_runs_no_gh_and_no_ssh(tmp):
    r = _github_clone(tmp)
    _commit(r, "[ACME-7]")
    gh = _gh(tmp)
    ssh = _no_ssh_alias(tmp)
    out = discover(["ACME-7"], [r], "head", github=False)
    assert out["github"]["status"] == "off" and out["github"]["prs"] == []
    assert out["repos"][0]["github"] is None
    assert _calls(gh) == [] and _calls(ssh) == []


def case_which_clones_are_on_github(tmp):
    _no_ssh_alias(tmp)
    ssh = _stub(tmp, "ssh", [(["-G", "github-ig.com"], 0, "user git\nhostname github.com\n", ""),
                             (["-G", "gh443"], 0, "hostname ssh.github.com\n", ""),
                             (["-G"], 0, "hostname ghe.example.com\n", "")])
    _gh(tmp)
    remotes = {
        "scp": ("git@github.com:acme/scp.git", "acme/scp"),
        "https": ("https://github.com/acme/https", "acme/https"),
        "sshurl": ("ssh://git@github.com/acme/sshurl.git/", "acme/sshurl"),
        "alias": ("git@github-ig.com:acme/alias.git", "acme/alias"),
        "port443": ("git@gh443:acme/port443.git", "acme/port443"),
        "ghe": ("git@ghe.example.com:acme/ghe.git", None),
        "httpsalias": ("https://github-ig.com/acme/httpsalias.git", None),
        "nested": ("git@github.com:acme/group/nested.git", None),
        "bitbucket": ("ssh://git@bitbucket.example.com/proj/repo.git", None),
        "option": ("git@-oProxyCommand=x:acme/option.git", None),
    }
    clones = [_repo(tmp, name, url) for name, (url, _) in remotes.items()]
    noremote = _repo(tmp, "noremote")
    out = discover(["ACME-7"], clones + [noremote], "head")
    got = {os.path.basename(r["path"]): r["github"] for r in out["repos"]}
    want = {name: slug for name, (_, slug) in remotes.items()}
    want["noremote"] = None
    assert got == want, got
    asked = [c[1] for c in _calls(ssh)]
    assert "-oProxyCommand=x" not in asked and "github.com" not in asked, asked
    assert not any(a.startswith("-") for a in asked), asked


def case_gh_absent_or_logged_out(tmp):
    r = _github_clone(tmp)
    _commit(r, "[ACME-7]")
    _no_ssh_alias(tmp)
    git = shutil.which("git")
    nogh = os.path.join(tmp, "nogh")
    os.makedirs(nogh)
    os.symlink(git, os.path.join(nogh, "git"))
    saved = os.environ["PATH"]
    os.environ["PATH"] = nogh
    try:
        assert discover(["ACME-7"], [r], "head")["github"]["status"] == "not-installed"
    finally:
        os.environ["PATH"] = saved
    log = _gh(tmp, auth=1)
    out = discover(["ACME-7"], [r], "head")
    assert out["github"]["status"] == "not-authenticated", out["github"]
    assert out["github"]["detail"] == "not logged in", out["github"]
    assert all(c[:2] != ["search", "prs"] for c in _calls(log))
    assert [c["sha"] for c in out["commits"]], "the commit scan still ran"


def case_no_clone_on_github(tmp):
    r = _repo(tmp, "r", "ssh://git@bitbucket.example.com/proj/r.git")
    _commit(r, "[ACME-7]")
    _no_ssh_alias(tmp)
    log = _gh(tmp)
    out = discover(["ACME-7"], [r], "head")
    assert out["github"]["status"] == "no-github-clones" and _calls(log) == []


def case_keys_are_searched_six_at_a_time_in_every_owner(tmp):
    a = _github_clone(tmp, "a", "acme")
    b = _github_clone(tmp, "b", "Other")
    c = _github_clone(tmp, "c", "acme")
    _no_ssh_alias(tmp)
    log = _gh(tmp)
    keys = ["K-%d" % i for i in range(1, 8)]
    out = discover(keys, [a, b, c], "head")
    searches = [x for x in _calls(log) if x[:2] == ["search", "prs"]]
    assert len(searches) == 2 and out["github"]["queries"] == 2, searches
    first, second = searches
    assert first.count("--owner") == 2 and "acme" in first and "Other" in first
    assert first[first.index("--") + 1:] == ['"K-1"', "OR", '"K-2"', "OR", '"K-3"', "OR", '"K-4"', "OR", '"K-5"', "OR", '"K-6"']
    assert second[second.index("--") + 1:] == ['"K-7"']
    assert out["github"]["owners"] == ["acme", "Other"] and out["github"]["status"] == "ok"


def case_a_loose_hit_is_dropped_and_a_body_hit_kept(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _no_ssh_alias(tmp)
    hits = [_search_hit("acme/app", 1, "unrelated", "mentions ACME-70 only"),
            _search_hit("acme/app", 2, "plain title", "Implements acme-7.", state="open"),
            _search_hit("acme/app", 3, "[ACME-7] title", state="closed")]
    views = {2: {"state": "OPEN", "headRefName": "f", "baseRefName": "main", "headRefOid": "0" * 40,
                 "mergeCommit": None, "isCrossRepository": False, "commits": []},
             3: {"state": "CLOSED", "headRefName": "g", "baseRefName": "main", "headRefOid": "1" * 40,
                 "mergeCommit": None, "isCrossRepository": True, "commits": []}}
    _gh(tmp, hits, views)
    out = discover(["ACME-7"], [r], "head")
    prs = {p["number"]: p for p in out["github"]["prs"]}
    assert sorted(prs) == [2, 3] and out["github"]["dropped_loose"] == 1, out["github"]
    assert prs[2]["state"] == "OPEN" and prs[2]["keys"] == ["ACME-7"] and prs[2]["clone"] == r
    assert prs[2]["head_ref"] == "f" and prs[2]["landed_as"] is None and prs[2]["landed"] == []
    assert prs[3]["state"] == "CLOSED" and prs[3]["cross_repository"] is True


def case_a_pr_in_an_uncloned_repository(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _no_ssh_alias(tmp)
    log = _gh(tmp, [_search_hit("acme/elsewhere", 9, "[ACME-7] there")])
    out = discover(["ACME-7"], [r], "head")
    (pr,) = out["github"]["prs"]
    assert pr["clone"] is None and pr["head_ref"] is None and pr["owner"] == "acme" and pr["repo"] == "elsewhere"
    assert all(c[:2] != ["pr", "view"] for c in _calls(log))


def _merged_view(merge, commits=()):
    return {"state": "MERGED", "headRefName": "topic", "baseRefName": "main", "headRefOid": "2" * 40,
            "mergeCommit": {"oid": merge}, "isCrossRepository": False,
            "commits": [{"oid": "3" * 40, "messageHeadline": h} for h in commits]}


def case_a_merge_landing_lists_the_branch_commits(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _git(r, "checkout", "-q", "-b", "topic")
    keyless = _commit(r, "topic one")
    keyed = _commit(r, "topic two [ACME-7]")
    _git(r, "checkout", "-q", "main")
    _commit(r, "main moves on")
    merge = _merge(r, "topic", "Merge pull request #5 from acme/topic")
    _no_ssh_alias(tmp)
    _gh(tmp, [_search_hit("acme/app", 5, "Intake (ACME-7)")], {5: _merged_view(merge, ["topic one", "topic two"])})
    out = discover(["ACME-7"], [r], "head", probe=True)
    (pr,) = out["github"]["prs"]
    assert pr["landed_as"] == "merge" and pr["landed"] == [keyless, keyed] and pr["merge_commit"] == merge, pr
    by = {c["sha"]: c for c in out["commits"]}
    assert by[keyed]["via"] == "message" and by[keyed]["prs"] == [pr["url"]]
    assert by[keyless]["via"] == "pull-request" and by[keyless]["keys"] == ["ACME-7"] and by[keyless]["prs"] == [pr["url"]]
    assert by[keyless]["subject"] == "topic one" and by[keyless]["date"]
    assert out["repos"][0]["matched"] == 1


def case_squash_and_rebase_landings(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    squash = _commit(r, "Intake (#6)")
    one = _commit(r, "rebased one")
    two = _commit(r, "rebased two")
    _no_ssh_alias(tmp)
    hits = [_search_hit("acme/app", 6, "Intake [ACME-7]"), _search_hit("acme/app", 7, "Rebased [ACME-7]")]
    _gh(tmp, hits, {6: _merged_view(squash, ["wip", "more wip"]), 7: _merged_view(two, ["rebased one", "rebased two"])})
    out = discover(["ACME-7"], [r], "head")
    prs = {p["number"]: p for p in out["github"]["prs"]}
    assert prs[6]["landed_as"] == "squash" and prs[6]["landed"] == [squash], prs[6]
    assert prs[7]["landed_as"] == "rebase" and prs[7]["landed"] == [one, two], prs[7]


def case_a_merge_commit_the_clone_lacks(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _no_ssh_alias(tmp)
    _gh(tmp, [_search_hit("acme/app", 8, "[ACME-7]")], {8: _merged_view("4" * 40)})
    out = discover(["ACME-7"], [r], "head")
    (pr,) = out["github"]["prs"]
    assert pr["landed_as"] is None and pr["landed"] == [] and pr["reason"] == "merge commit not in the clone", pr
    assert out["commits"] == []


def case_the_probe_omits_what_a_pull_request_accounts_for(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _git(r, "checkout", "-q", "-b", "feat/ACME-7-intake")
    branch_commit = _commit(r, "intake work")
    _git(r, "checkout", "-q", "main")
    merge = _merge(r, "feat/ACME-7-intake", "Merge pull request #4 from acme/feat/ACME-7-intake")
    other = _commit(r, "see ACME-77")
    _no_ssh_alias(tmp)
    _gh(tmp, [_search_hit("acme/app", 4, "Intake [ACME-7]")], {4: _merged_view(merge, ["intake work"])})
    out = discover(["ACME-7"], [r], "head", probe=True)
    assert [p["sha"] for p in out["repos"][0]["probe"]] == [other], out["repos"][0]["probe"]
    assert [c["sha"] for c in out["commits"]] == [branch_commit]


def case_a_failing_search_is_partial_and_a_rate_limit_stops(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _no_ssh_alias(tmp)
    _gh(tmp, search_rc=1, search_err="HTTP 502: bad gateway")
    keys = ["K-%d" % i for i in range(1, 8)]
    out = discover(keys, [r], "head")
    assert out["github"]["status"] == "partial" and "bad gateway" in out["github"]["detail"], out["github"]
    log = _gh(tmp, search_rc=1, search_err="API rate limit exceeded for user")
    out = discover(keys, [r], "head")
    assert out["github"]["status"] == "rate-limited", out["github"]
    assert len([c for c in _calls(log) if c[:2] == ["search", "prs"]]) == 1


def case_a_failing_view_leaves_the_pr_without_details(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _no_ssh_alias(tmp)
    _gh(tmp, [_search_hit("acme/app", 11, "[ACME-7]")])
    out = discover(["ACME-7"], [r], "head")
    (pr,) = out["github"]["prs"]
    assert pr["head_ref"] is None and pr["landed"] == [] and pr["reason"].startswith("gh pr view failed"), pr
    assert out["github"]["status"] == "ok"


def case_excluded_clones_and_their_prs(tmp):
    app = _github_clone(tmp, "app")
    _commit(app, "[ACME-7] code")
    specs = _repo(tmp, "specs", "git@github.com:acme/specs.git")
    _commit(specs, "ACME-7 Add architecture requirements document")
    specs2 = _repo(tmp, "specs-repo", "https://github.com/acme/specs")
    _commit(specs2, "ACME-7 Add session artifacts")
    docs = _repo(tmp, "docs", "ssh://git@bitbucket.example.com/doc/docs.git")
    _commit(docs, "ACME-7 Document intake")
    _no_ssh_alias(tmp)
    log = _gh(tmp, [_search_hit("acme/specs", 3, "ACME-7 Add ARD"), _search_hit("acme/app", 4, "[ACME-7] code")],
              {4: _merged_view("6" * 40)})
    out = discover(["ACME-7"], [app, specs, specs2, docs], "head", excludes=[specs, docs])
    assert [r["path"] for r in out["repos"]] == [app], out["repos"]
    assert out["excluded"] == ["specs", "docs"], out["excluded"]
    assert {c["repo"] for c in out["commits"]} == {app}
    assert [p["number"] for p in out["github"]["prs"]] == [4], out["github"]["prs"]
    assert all("--owner" in c and "acme" in c for c in _calls(log) if c[:2] == ["search", "prs"])


def case_owner_of_adds_an_owner_and_scans_nothing(tmp):
    app = _github_clone(tmp, "app", "acme")
    fork = _github_clone(tmp, "fork", "someone")
    _commit(fork, "[ACME-7] in the fork")
    _no_ssh_alias(tmp)
    log = _gh(tmp)
    out = discover(["ACME-7"], [app], "head", owners_of=[fork])
    (search,) = [c for c in _calls(log) if c[:2] == ["search", "prs"]]
    assert "someone" in search and "acme" in search, search
    assert out["github"]["owners"] == ["acme", "someone"] and out["commits"] == []
    assert [r["path"] for r in out["repos"]] == [app]


def case_a_separator_inside_a_message(tmp):
    r = _repo(tmp, "r")
    odd = _commit(r, "[ACME-7] odd \x1e record \x1f unit")
    plain = _commit(r, "plain [ACME-7]")
    out = discover(["ACME-7"], [r], "head", github=False)
    assert {c["sha"] for c in out["commits"]} == {odd, plain}, out["commits"]


def case_an_unexpected_error_exits_2(tmp):
    r = _repo(tmp, "r")
    _commit(r, "x")
    saved = globals()["discover"]

    def boom(*args, **kwargs):
        raise RuntimeError("unexpected")
    globals()["discover"] = boom
    try:
        rc, out, err = _main(["scan", "--key", "A-1", "--repo", r, "--scope", "head", "--no-github"])
    finally:
        globals()["discover"] = saved
    assert rc == 2 and out == "" and "RuntimeError" in err and "Traceback" not in err, (rc, err)


def case_rebase_headlines_folded_or_truncated(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    one = _commit(r, "rebased one\nwrapped onto a second line")
    two = _commit(r, "rebased two with a subject long enough that GitHub would cut it short in a headline")
    _no_ssh_alias(tmp)
    view = _merged_view(two, ["rebased one", "rebased two with a subject long enough\u2026"])
    _gh(tmp, [_search_hit("acme/app", 13, "[ACME-7]")], {13: view})
    out = discover(["ACME-7"], [r], "head")
    (pr,) = out["github"]["prs"]
    assert pr["landed_as"] == "rebase" and pr["landed"] == [one, two], pr


def case_loose_hits_count_once_and_failures_survive_a_rate_limit(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _no_ssh_alias(tmp)
    loose = [_search_hit("acme/app", 1, "unrelated", "nothing")]
    log = _gh(tmp, loose)
    keys = ["K-%d" % i for i in range(1, 8)]
    out = discover(keys, [r], "head")
    assert out["github"]["dropped_loose"] == 1, out["github"]
    _stub(tmp, "gh", [(["auth", "status"], 0, "", ""),
                      (["search", "prs", '"K-7"'], 1, "", "API rate limit exceeded"),
                      (["search", "prs"], 1, "", "HTTP 502: bad gateway")])
    out = discover(keys, [r], "head")
    g = out["github"]
    assert g["status"] == "rate-limited" and "rate limit" in g["detail"] and "bad gateway" in g["detail"], g


def case_a_full_page_is_partial(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _no_ssh_alias(tmp)
    hits = [_search_hit("acme/app", 100 + i, "loose %d" % i) for i in range(SEARCH_LIMIT)]
    _gh(tmp, hits)
    out = discover(["ACME-7"], [r], "head")
    g = out["github"]
    assert g["status"] == "partial" and "limit" in g["detail"], g


def case_git_never_fetches_lazily(tmp):
    assert _git_env().get("GIT_NO_LAZY_FETCH") == "1"


def case_a_release_pr_that_lands_other_branches_is_not_read(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _git(r, "checkout", "-q", "-b", "develop")
    _git(r, "checkout", "-q", "-b", "fa")
    other = _commit(r, "[ACME-9] billing rework")
    _git(r, "checkout", "-q", "develop")
    _merge(r, "fa", "Merge feature A")
    _git(r, "checkout", "-q", "main")
    release = _merge(r, "develop", "Merge pull request #20 from acme/develop")
    _no_ssh_alias(tmp)
    _gh(tmp, [_search_hit("acme/app", 20, "Release 2.3", "Includes ACME-7 and ACME-9")], {20: _merged_view(release)})
    out = discover(["ACME-7"], [r], "head")
    (pr,) = out["github"]["prs"]
    assert pr["landed_as"] is None and pr["landed"] == [] and "other branches" in pr["reason"], pr
    assert other not in [c["sha"] for c in out["commits"]]


def case_a_branch_that_merged_its_base_is_still_read(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _git(r, "checkout", "-q", "-b", "topic")
    own = _commit(r, "topic work")
    _git(r, "checkout", "-q", "main")
    _commit(r, "main moves on")
    _git(r, "checkout", "-q", "topic")
    _merge(r, "main", "Merge branch 'main' into topic")
    _git(r, "checkout", "-q", "main")
    merge = _merge(r, "topic", "Merge pull request #22 from acme/topic")
    _no_ssh_alias(tmp)
    _gh(tmp, [_search_hit("acme/app", 22, "[ACME-7] topic")], {22: _merged_view(merge)})
    (pr,) = discover(["ACME-7"], [r], "head")["github"]["prs"]
    assert pr["landed_as"] == "merge" and pr["landed"] == [own], pr


def case_a_merge_commit_off_the_scanned_ref_is_not_read(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _git(r, "checkout", "-q", "-b", "part1")
    _commit(r, "part one")
    _git(r, "checkout", "-q", "-b", "part2")
    two = _commit(r, "part two")
    _git(r, "checkout", "-q", "part1")
    stacked = _merge(r, "part2", "Merge pull request #21 from acme/part2")
    _git(r, "checkout", "-q", "main")
    _no_ssh_alias(tmp)
    _gh(tmp, [_search_hit("acme/app", 21, "[ACME-7] part 2")], {21: _merged_view(stacked)})
    out = discover(["ACME-7"], [r], "head")
    (pr,) = out["github"]["prs"]
    assert pr["landed_as"] is None and pr["reason"] == "merge commit not on HEAD", pr
    assert two not in [c["sha"] for c in out["commits"]]


def case_dates_are_local(tmp):
    r = _repo(tmp, "r")
    saved = {k: os.environ.get(k) for k in ("TZ", "GIT_COMMITTER_DATE")}
    os.environ["GIT_COMMITTER_DATE"] = "2026-10-06T23:30:00-07:00"
    try:
        _commit(r, "[ACME-7] late")
        os.environ.pop("GIT_COMMITTER_DATE")
        os.environ["TZ"] = "UTC"
        (c,) = discover(["ACME-7"], [r], "head", github=False)["commits"]
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    assert c["date"].startswith("2026-10-07T06:30:00"), c["date"]


def case_a_commit_takes_the_keys_of_the_prs_that_landed_it(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _git(r, "checkout", "-q", "-b", "topic")
    own = _commit(r, "[ACME-7] work")
    _git(r, "checkout", "-q", "main")
    merge = _merge(r, "topic", "Merge pull request #23 from acme/topic")
    _no_ssh_alias(tmp)
    _gh(tmp, [_search_hit("acme/app", 23, "[ACME-8] the epic")], {23: _merged_view(merge)})
    out = discover(["ACME-7", "ACME-8"], [r], "head")
    (c,) = [c for c in out["commits"] if c["sha"] == own]
    assert c["keys"] == ["ACME-7", "ACME-8"] and c["via"] == "message", c


def case_an_odd_gh_answer_is_partial_and_the_scan_survives(tmp):
    r = _github_clone(tmp)
    sha = _commit(r, "[ACME-7]")
    _no_ssh_alias(tmp)
    _stub(tmp, "gh", [(["auth", "status"], 0, "", ""), (["search", "prs"], 0, json.dumps([1, None, {"repository": None}]), "")])
    out = discover(["ACME-7"], [r], "head")
    assert out["github"]["status"] == "partial" and out["github"]["detail"], out["github"]
    assert [c["sha"] for c in out["commits"]] == [sha]


def case_a_failed_read_after_the_count_and_a_failed_probe(tmp):
    r = os.path.join(tmp, "r")
    _git(tmp, "init", "-q", "r")
    _commit(r, "base")

    def broken(*_args, **_kwargs):
        raise SearchFailed("git log failed")
    saved = globals()["_log"]
    globals()["_log"] = broken
    try:
        (entry,) = discover(["ACME-7"], [r], "head", github=False)["repos"]
    finally:
        globals()["_log"] = saved
    assert entry["error"] and entry["scanned"] is None, entry
    saved = globals()["probe_clone"]
    globals()["probe_clone"] = broken
    try:
        (entry,) = discover(["ACME-7"], [r], "head", probe=True, github=False)["repos"]
    finally:
        globals()["probe_clone"] = saved
    assert entry["error"] is None and entry["scanned"] == 1 and entry["probe_error"], entry


def case_the_view_budget_runs_out(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _no_ssh_alias(tmp)
    _gh(tmp, [_search_hit("acme/app", 24, "[ACME-7]")], {24: _merged_view("7" * 40)})
    ticks = iter([0, 0])  # the start and the one search are in budget; every view after is past it
    saved = globals()["_now"]
    globals()["_now"] = lambda: next(ticks, 10 ** 6)
    try:
        out = discover(["ACME-7"], [r], "head")
    finally:
        globals()["_now"] = saved
    (pr,) = out["github"]["prs"]
    assert pr["head_ref"] is None and "budget" in pr["reason"] and out["github"]["status"] == "partial", out["github"]


def case_the_budget_bounds_the_searches_too(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _no_ssh_alias(tmp)
    _gh(tmp, [_search_hit("acme/app", 24, "[ACME-7]")], {24: _merged_view("7" * 40)})
    keys = ["ACME-%d" % n for n in range(1, 14)]  # three batches of six
    ticks = iter([0, 0])  # the start and the first batch are in budget; the second batch is not
    saved = globals()["_now"]
    globals()["_now"] = lambda: next(ticks, 10 ** 6)
    try:
        out = discover(keys, [r], "head")
    finally:
        globals()["_now"] = saved
    g = out["github"]
    assert g["queries"] == 1 and g["status"] == "partial" and "2 of 3 not run: ACME-7 OR" in g["detail"], g


def case_an_exclude_that_is_no_repository_top_excludes_nothing(tmp):
    product = _repo(tmp, "product", "git@github.com:acme/product.git")
    sha = _commit(product, "[ACME-7] code")
    os.makedirs(os.path.join(product, "docs"))
    loose = os.path.join(tmp, "notes", "product")
    os.makedirs(loose)
    out = discover(["ACME-7"], [product], "head", github=False, excludes=[os.path.join(product, "docs"), loose])
    assert out["excluded"] == [] and [c["sha"] for c in out["commits"]] == [sha], out


def _main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = main(argv)
        except SystemExit as e:
            rc = e.code
    return rc, out.getvalue(), err.getvalue()


def case_cli(tmp):
    r = _repo(tmp, "r")
    sha = _commit(r, "[ACME-7]")
    rc, out, _ = _main(["scan", "--key", "ACME-7", "--key", "ACME-7", "--repo", r, "--scope", "head", "--no-github"])
    assert rc == 0, rc
    doc = json.loads(out)
    assert doc["keys"] == ["ACME-7"] and doc["scope"] == "head" and [c["sha"] for c in doc["commits"]] == [sha]
    assert set(doc) == {"keys", "scope", "excluded", "repos", "commits", "github", "docs"} and doc["docs"] is None
    assert set(doc["github"]) == {"status", "detail", "owners", "queries", "dropped_loose", "prs"}
    assert set(doc["repos"][0]) == {"path", "ref", "scanned", "matched", "github", "error", "probe", "probe_error",
                                    "docs_rule"}, doc["repos"][0]
    assert out.count("\n") > 10 and max(len(line) for line in out.splitlines()) < 2000, "indented, line-readable JSON"
    rc, out, _ = _main(["scan", "--key", "ACME-7", "--repo", r, "--scope", "head", "--no-github",
                        "--docs-root", r, "--docs-content", "website"])
    assert rc == 0 and set(json.loads(out)["docs"]) == {"root", "top", "repo", "rule", "reason", "content_paths",
                                                        "rejected", "clones", "docs_only"}, out


def case_refusals_exit_2(tmp):
    r = _repo(tmp, "r")
    _commit(r, "x")
    for argv in (["scan", "--repo", r, "--scope", "head"],
                 ["scan", "--key", "A-1", "--scope", "head"],
                 ["scan", "--key", "A-1", "--repo", r],
                 ["scan", "--key", "", "--repo", r, "--scope", "head"],
                 ["scan", "--key", "A 1", "--repo", r, "--scope", "head"],
                 ["scan", "--key", 'A"1', "--repo", r, "--scope", "head"],
                 ["scan", "--key", "A-1", "--repo", r, "--scope", "head", "--exclude", os.path.join(tmp, "missing")],
                 ["scan", "--key", "A-1", "--repo", os.path.join(tmp, "missing"), "--scope", "head"],
                 ["scan", "--key", "A-1", "--repo", r, "--scope", "all"]):
        rc, out, err = _main(argv)
        assert rc == 2 and out == "", (argv, rc, out)
    saved = os.environ["PATH"]
    os.environ["PATH"] = os.path.join(tmp, "empty-path")
    try:
        rc, out, err = _main(["scan", "--key", "A-1", "--repo", r, "--scope", "head", "--no-github"])
    finally:
        os.environ["PATH"] = saved
    assert rc == 2 and "git" in err, (rc, err)


def case_no_credential_reaches_an_argument(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _no_ssh_alias(tmp)
    log = _gh(tmp, [_search_hit("acme/app", 12, "[ACME-7]")], {12: _merged_view("5" * 40)})
    discover(["ACME-7"], [r], "head")
    for argv in _calls(log):
        assert not any(re.search(r"token|gh[pousr]_|github_pat_", a, re.I) for a in argv), argv


# the documentation-holding repository: --docs-root and --docs-content

def _mono(tmp, name="mono", remote=None):
    """A repository holding code and a documentation site in website/."""
    r = _repo(tmp, name, remote)
    _commit(r, "base", ("src/app.py", "website/docs/a.md", "website/mkdocs.yml"))
    return r


def case_docs_second_run(tmp):
    mono = _mono(tmp)
    first = _commit(mono, "ACME-7 Document intake",
                    ("website/docs/intake.md", "website/mkdocs.yml", ".dev-workflows/docs-profile.yml"))
    out = discover(["ACME-7"], [mono], "head", probe=True, github=False, docs_root=os.path.join(mono, "website"))
    docs = out["docs"]
    assert out["commits"] == [], out["commits"]
    assert out["repos"][0]["probe"] == [] and out["repos"][0]["probe_error"] is None, out["repos"]
    assert docs["rule"] == "paths" and docs["reason"] is None and docs["content_paths"] == ["website"], docs
    assert docs["top"] == mono and docs["repo"] == "mono" and docs["clones"] == [mono], docs
    assert [d["sha"] for d in docs["docs_only"]] == [first], docs["docs_only"]
    assert docs["docs_only"][0]["keys"] == ["ACME-7"] and docs["docs_only"][0]["subject"] == "ACME-7 Document intake"
    assert out["excluded"] == [] and out["repos"][0]["docs_rule"] is True, out
    assert out["repos"][0]["scanned"] == 1 and out["repos"][0]["matched"] == 0, out["repos"]


def case_docs_code_and_mixed_commits(tmp):
    mono = _mono(tmp)
    code = _commit(mono, "code only [ACME-7]", "src/a.py")
    mixed = _commit(mono, "mixed [ACME-7]", ("src/b.py", "website/docs/x.md"))
    out = discover(["ACME-7"], [mono], "head", github=False, docs_root=os.path.join(mono, "website"))
    assert {c["sha"]: c["via"] for c in out["commits"]} == {code: "message", mixed: "message"}, out["commits"]
    assert out["docs"]["docs_only"] == [], out["docs"]


def case_docs_side_branch_net_zero(tmp):
    mono = _mono(tmp)
    _git(mono, "checkout", "-q", "-b", "side")
    added = _commit(mono, "add e [ACME-9]", "src/e.py")
    _git(mono, "rm", "-q", "src/e.py")
    _git(mono, "commit", "-q", "-m", "drop e again [ACME-9]")
    dropped = _git(mono, "rev-parse", "HEAD")
    _git(mono, "checkout", "-q", "main")
    _commit(mono, "docs on main", "website/docs/b.md")
    _merge(mono, "side", "Merge side")
    out = discover(["ACME-9"], [mono], "head", github=False, docs_root=os.path.join(mono, "website"))
    assert {c["sha"] for c in out["commits"]} == {added, dropped}, out["commits"]
    assert out["repos"][0]["scanned"] == 3, out["repos"]  # base and both side commits; the docs commit is not one


def case_docs_probe_merges(tmp):
    r = _repo(tmp, "mono")
    root = _commit(r, "start ACME-7x", ("src/app.py", "website/docs/a.md"))
    _git(r, "checkout", "-q", "-b", "feat/ACME-7-x")
    _commit(r, "code on a branch", "src/b.py")
    _git(r, "checkout", "-q", "main")
    code_merge = _merge(r, "feat/ACME-7-x", "Merge feat/ACME-7-x")
    _git(r, "checkout", "-q", "-b", "docs/ACME-7-y")
    _commit(r, "docs on a branch", "website/docs/c.md")
    _git(r, "checkout", "-q", "main")
    _commit(r, "code on main", "src/c.py")
    docs_merge = _merge(r, "docs/ACME-7-y", "Merge docs/ACME-7-y")
    for branch, path in (("o1", "website/docs/o.md"), ("o2", "src/o.py")):
        _git(r, "checkout", "-q", "-b", branch, "main")
        _commit(r, "%s work" % branch, path)
    _git(r, "checkout", "-q", "main")
    _commit(r, "main moves on", "src/m.py")
    _git(r, "merge", "-q", "--no-ff", "-m", "Merge octopus ACME-7-z", "o1", "o2")
    octopus = _git(r, "rev-parse", "HEAD")
    out = discover(["ACME-7"], [r], "head", probe=True, github=False, docs_root=os.path.join(r, "website"))
    (entry,) = out["repos"]
    probed = [p["sha"] for p in entry["probe"]]
    assert entry["matched"] == 0 and entry["error"] is None and entry["probe_error"] is None, entry
    assert code_merge in probed and octopus in probed and root in probed, entry["probe"]
    assert docs_merge not in probed, entry["probe"]


def case_docs_pull_requests(tmp):
    r = _github_clone(tmp)
    _commit(r, "base", ("src/app.py", "handbook/index.md"))
    docs_squash = _commit(r, "Handbook (#31)", "docs/guide.md")
    code_squash = _commit(r, "Intake (#32)", "src/intake.py")
    page = _commit(r, "a page", "handbook/intake.md")
    code = _commit(r, "the code", "src/rebased.py")
    _no_ssh_alias(tmp)
    hits = [_search_hit("acme/app", 31, "[ACME-7] handbook"), _search_hit("acme/app", 32, "[ACME-7] intake"),
            _search_hit("acme/app", 33, "[ACME-7] rebased")]
    _gh(tmp, hits, {31: _merged_view(docs_squash, ["wip"]), 32: _merged_view(code_squash, ["wip"]),
                    33: _merged_view(code, ["a page", "the code"])})
    out = discover(["ACME-7"], [r], "head", probe=True, docs_root=r, docs_content=["handbook"])
    prs = {p["number"]: p for p in out["github"]["prs"]}
    found = {c["sha"]: c for c in out["commits"]}
    assert out["docs"]["rule"] == "paths" and sorted(prs) == [31, 32, 33], (out["docs"], prs)
    assert prs[31]["landed"] == [] and prs[31]["reason"] == "landed documentation only", prs[31]
    assert prs[31]["landed_docs_only"] == [docs_squash] and docs_squash not in found, prs[31]
    assert prs[32]["landed"] == [code_squash] and prs[32]["landed_docs_only"] == [], prs[32]
    assert found[code_squash]["via"] == "pull-request" and found[code_squash]["prs"] == [prs[32]["url"]]
    assert prs[33]["landed_as"] == "rebase" and prs[33]["landed"] == [code], prs[33]
    assert prs[33]["landed_docs_only"] == [page] and prs[33]["reason"] is None, prs[33]
    assert set(found) == {code_squash, code} and found[code]["via"] == "pull-request", found
    assert out["repos"][0]["probe"] == [], out["repos"][0]


def case_docs_markdown_outside_the_set_is_code(tmp):
    mono = _mono(tmp)
    sha = _commit(mono, "[ACME-7] the run command", "plugins/x/commands/run.md")
    out = discover(["ACME-7"], [mono], "head", github=False, docs_root=os.path.join(mono, "website"))
    assert [c["sha"] for c in out["commits"]] == [sha] and out["docs"]["docs_only"] == [], out


def case_docs_no_content_path(tmp):
    site = _github_clone(tmp, "site")
    _commit(site, "[ACME-7] code and pages", ("src/a.py", "docs/a.md"))
    app = _github_clone(tmp, "app")
    _commit(app, "base")
    _no_ssh_alias(tmp)
    _gh(tmp, [_search_hit("acme/site", 3, "ACME-7 Document intake"), _search_hit("acme/app", 4, "[ACME-7] code")],
        {4: _merged_view("6" * 40)})
    out = discover(["ACME-7"], [site, app], "head", docs_root=site)
    docs = out["docs"]
    assert out["excluded"] == ["site"] and docs["rule"] == "left-out" and docs["reason"] == "no content path", out
    assert docs["content_paths"] == [] and docs["clones"] == [] and docs["docs_only"] == [], docs
    assert [r["path"] for r in out["repos"]] == [app] and out["commits"] == [], out
    assert [p["number"] for p in out["github"]["prs"]] == [4], out["github"]["prs"]


def case_docs_second_clone_by_slug(tmp):
    remote = "ssh://git@bitbucket.example.com/acme/product.git"
    first = _repo(tmp, "product", remote)
    _commit(first, "base", ("src/app.py", "website/docs/a.md"))
    second = _repo(tmp, "product-2", remote)
    _commit(second, "base", ("src/app.py", "website/docs/a.md"))
    page = _commit(second, "ACME-7 Document intake", "website/docs/intake.md")
    code = _commit(second, "[ACME-7] intake", "src/intake.py")
    out = discover(["ACME-7"], [second], "head", github=False, docs_root=os.path.join(first, "website"))
    docs = out["docs"]
    assert docs["top"] == first and docs["repo"] == "product" and docs["clones"] == [second], docs
    assert [d["sha"] for d in docs["docs_only"]] == [page] and [c["sha"] for c in out["commits"]] == [code], out
    assert out["repos"][0]["docs_rule"] is True and out["excluded"] == [], out


def case_docs_top_level_markdown(tmp):
    mono = _mono(tmp)
    readme = _commit(mono, "ACME-7 README", "README.md")
    design = _commit(mono, "ACME-7 design notes", "src/notes/DESIGN.md")
    out = discover(["ACME-7"], [mono], "head", github=False, docs_root=os.path.join(mono, "website"))
    assert [d["sha"] for d in out["docs"]["docs_only"]] == [readme], out["docs"]
    assert [c["sha"] for c in out["commits"]] == [design], out["commits"]


def case_docs_content_is_literal(tmp):
    r = _repo(tmp, "r")
    _commit(r, "base", "src/app.py")
    draft = _commit(r, "ACME-7 draft page", "docs site/[draft]/p.md")
    odd = _commit(r, "ACME-7 odd page", ":odd/p.md")
    near = _commit(r, "ACME-7 a near miss", "docs site/d")
    starred = _commit(r, "ACME-7 not under a*", "ab/x.py")
    out = discover(["ACME-7"], [r], "head", github=False, docs_root=r, docs_content=["docs site/[draft]", ":odd", "a*"])
    assert out["docs"]["content_paths"] == ["docs site/[draft]", ":odd", "a*"], out["docs"]
    assert {d["sha"] for d in out["docs"]["docs_only"]} == {draft, odd}, out["docs"]["docs_only"]
    assert {c["sha"] for c in out["commits"]} == {near, starred}, out["commits"]


def case_docs_content_whole_repository(tmp):
    r = _repo(tmp, "mono", "git@example.com:acme/mono.git")
    _commit(r, "[ACME-7] code", "src/a.py")
    for content in (["."], ["./"], [""]):
        out = discover(["ACME-7"], [r], "head", github=False, docs_root=r, docs_content=content)
        docs = out["docs"]
        assert docs["rule"] == "left-out" and docs["reason"] == "the content path is the whole repository", docs
        assert out["excluded"] == ["mono"] and out["repos"] == [] and out["commits"] == [], out


def case_docs_content_rejected(tmp):
    mono = _mono(tmp)
    out = discover(["ACME-7"], [mono], "head", github=False, docs_root=mono,
                   docs_content=["/etc", "a/../b", "website", "./website/"])
    docs = out["docs"]
    assert [x["path"] for x in docs["rejected"]] == ["/etc", "a/../b"], docs["rejected"]
    assert all(set(x) == {"path", "why"} and x["why"] for x in docs["rejected"]), docs["rejected"]
    assert docs["content_paths"] == ["website"] and docs["rule"] == "paths", docs


def case_docs_root_outside_a_repository(tmp):
    r = _repo(tmp, "r")
    _commit(r, "[ACME-7] code")
    plain = os.path.join(tmp, "plain")
    os.makedirs(plain)
    out = discover(["ACME-7"], [r], "head", probe=True, github=False, docs_root=plain, docs_content=["x"])
    assert out["docs"] is None, out["docs"]
    assert out == discover(["ACME-7"], [r], "head", probe=True, github=False)


def case_docs_no_clone_of_it_scanned(tmp):
    site = _github_clone(tmp, "site")
    _commit(site, "base", ("src/a.py", "handbook/a.md"))
    app = _github_clone(tmp, "app")
    _commit(app, "base")
    _no_ssh_alias(tmp)
    _gh(tmp, [_search_hit("acme/site", 3, "ACME-7 Document intake"), _search_hit("acme/app", 4, "[ACME-7] code")],
        {4: _merged_view("6" * 40)})
    out = discover(["ACME-7"], [app], "head", docs_root=site, docs_content=["handbook"])
    assert out["docs"]["rule"] == "paths" and out["docs"]["clones"] == [] and out["excluded"] == [], out
    assert [p["number"] for p in out["github"]["prs"]] == [4], out["github"]["prs"]


def case_docs_excluded_too(tmp):
    remote = "git@example.com:acme/mono.git"
    mono = _mono(tmp, remote=remote)
    _commit(mono, "[ACME-7] code", "src/a.py")
    second = _repo(tmp, "mono-2", remote)
    _commit(second, "base")
    for excludes in ([mono], [second]):  # by the repository's own top level, and by a second clone's origin slug
        out = discover(["ACME-7"], [mono], "head", github=False, excludes=excludes,
                       docs_root=os.path.join(mono, "website"))
        docs = out["docs"]
        assert out["excluded"] == ["mono"] and out["repos"] == [] and out["commits"] == [], (excludes, out)
        assert docs["rule"] == "left-out" and docs["reason"] == "--exclude names it too", (excludes, docs)
        assert docs["clones"] == [] and docs["docs_only"] == [], (excludes, docs)


def case_docs_navigation_at_any_depth(tmp):
    r = _repo(tmp, "mono")
    _commit(r, "base", ("src/app.py", "website/docs/a.md", "website/mkdocs.yml"))
    sidebar = _commit(r, "ACME-7 sidebar entry", "website/sidebars.js")
    config = _commit(r, "ACME-7 navbar link", "website/docusaurus.config.ts")
    component = _commit(r, "ACME-7 sidebar component", "website/src/sidebars.jsx")
    out = discover(["ACME-7"], [r], "head", github=False, docs_root=r,
                   docs_content=["website/docs", "website/mkdocs.yml"])  # a root at the top level, a profile's paths
    docs = out["docs"]
    assert docs["rule"] == "paths" and docs["content_paths"] == ["website/docs", "website/mkdocs.yml"], docs
    assert [d["sha"] for d in docs["docs_only"]] == [config, sidebar], docs["docs_only"]
    assert [c["sha"] for c in out["commits"]] == [component], out["commits"]


def case_docs_check(tmp):
    mono = _mono(tmp)
    base = _git(mono, "rev-parse", "HEAD")
    _git(mono, "checkout", "-q", "-b", "docs/ACME-7-intake")
    _commit(mono, "ACME-7 Document intake", ("website/docs/a.md", "README.md", "assets/shot.png"))
    website = os.path.join(mono, "website")
    rc, out, err = _main(["docs-check", "--docs-root", website, "--base", base])
    assert rc == 0, (rc, err)
    doc = json.loads(out)
    assert set(doc) == {"docs", "base", "head", "outside"} and doc["base"] == base and doc["head"] == "HEAD", doc
    assert doc["outside"] == ["assets/shot.png"], doc
    assert doc["docs"]["rule"] == "paths" and "clones" not in doc["docs"] and "docs_only" not in doc["docs"], doc
    rc, out, _ = _main(["docs-check", "--docs-root", website, "--docs-content", "assets", "--base", base])
    assert rc == 0 and json.loads(out)["outside"] == [], out
    rc, out, _ = _main(["docs-check", "--docs-root", mono, "--base", base, "--head", "HEAD"])
    doc = json.loads(out)
    assert rc == 0 and doc["docs"]["rule"] == "left-out" and doc["outside"] == [], doc
    plain = os.path.join(tmp, "plain")
    os.makedirs(plain)
    rc, out, _ = _main(["docs-check", "--docs-root", plain, "--base", base])
    assert rc == 0 and json.loads(out) == {"docs": None, "base": base, "head": "HEAD", "outside": []}, out
    for argv in (["--base", "no-such-rev"], ["--base=-p"], ["--base", base, "--head=--output=x"]):
        rc, out, err = _main(["docs-check", "--docs-root", website] + argv)
        assert rc == 2 and out == "" and len(err.splitlines()) == 1, (argv, rc, out, err)


def case_docs_content_without_root_is_a_usage_error(tmp):
    r = _repo(tmp, "r")
    _commit(r, "x", "website/a.md")
    scan = ["scan", "--key", "A-1", "--repo", r, "--scope", "head", "--no-github"]
    for extra in (["--docs-content", "x"],
                  ["--docs-root", r, "--docs-root", os.path.join(r, "website")],
                  ["--docs-root", os.path.join(tmp, "missing")]):
        rc, out, err = _main(scan + extra)
        assert rc == 2 and out == "" and len(err.splitlines()) == 1, (extra, rc, out, err)


def selftest():
    os.environ["GIT_CONFIG_GLOBAL"] = os.devnull
    os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
    path = os.environ.get("PATH", "")
    cases = sorted((name, fn) for name, fn in globals().items() if name.startswith("case_"))
    failed = 0
    for name, fn in cases:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = os.path.realpath(tmp)
            os.environ["GIT_CEILING_DIRECTORIES"] = tmp
            os.environ["PATH"] = path
            try:
                fn(tmp)
                print("ok   " + name)
            except Exception as e:  # any exception is that case failing, and it is named
                failed += 1
                print("FAIL %s: %s: %s" % (name, type(e).__name__, e))
    os.environ["PATH"] = path
    print("selftest: %d/%d passed" % (len(cases) - failed, len(cases)))
    return 1 if failed else 0


# ---- implementation ----

def _run(argv, timeout, env=None):
    """(returncode, stdout, stderr); the returncode is None where the program is missing or timed out."""
    try:
        p = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, stdin=subprocess.DEVNULL, env=env)
    except subprocess.TimeoutExpired:
        return None, "", "timed out after %ds" % timeout
    except OSError as e:
        return None, "", e.strerror or str(e)
    return p.returncode, p.stdout, p.stderr


def _last_line(text, fallback):
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    return lines[-1] if lines else fallback


def ere_escape(key):
    return "".join("\\" + ch if ch in ERE_META else ch for ch in key)


def whole_pattern(key):
    return re.compile(EDGE_L + re.escape(key) + EDGE_R, re.IGNORECASE | re.MULTILINE)


def _git_env():
    """The environment every git call runs in: a partial clone never fetches a missing object."""
    env = dict(os.environ)
    env["GIT_NO_LAZY_FETCH"] = "1"
    return env


def _git_in(clone, *args):
    return _run(["git", "-C", clone, *args], GIT_TIMEOUT, _git_env())


def _verified(clone, ref):
    rc, _, _ = _git_in(clone, "rev-parse", "-q", "--verify", ref + "^{commit}")
    return rc == 0


def scan_ref(clone, scope):
    """The ref the scan reads, as reported: "HEAD", "origin/<name>", or HEAD with why."""
    if scope == "head":
        return "HEAD", "HEAD"
    rc, out, _ = _git_in(clone, "symbolic-ref", "-q", "refs/remotes/origin/HEAD")
    target = out.strip() if rc == 0 else ""
    if target.startswith("refs/remotes/") and _verified(clone, target):
        return target, target[len("refs/remotes/"):]
    for name in ("origin/main", "origin/master"):
        if _verified(clone, "refs/remotes/" + name):
            return "refs/remotes/" + name, name
    return "HEAD", "HEAD (no origin default branch)"


def _log(clone, ref, greps, merges):
    argv = ["log", ref, "-z", "--date=iso-strict-local", "--extended-regexp", "--regexp-ignore-case", "--format=" + FMT]
    if not merges:
        argv.append("--no-merges")
    argv += ["--grep=" + g for g in greps]
    rc, out, err = _git_in(clone, *argv, "--")
    if rc != 0:
        raise SearchFailed("git log failed: " + _last_line(err, "exit %s" % rc))
    rows = []
    for record in out.split("\0"):
        parts = record.lstrip("\n").split("\x1f", 2)
        if len(parts) == 3 and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", parts[0]):
            rows.append(tuple(parts))
    return rows


def _subject(body):
    return body.split("\n", 1)[0].strip()


def scan_clone(clone, scope, keys, patterns, pathspecs=()):
    """The repos[] entry for one clone, its key-matched commits, and the key-matched commits it left out as
    documentation only -- none unless the clone is read under the documentation rule, where `pathspecs` is the
    whole tree less the documentation set."""
    entry = {"path": clone, "ref": None, "scanned": None, "matched": 0, "github": None, "error": None, "probe": [],
             "probe_error": None, "docs_rule": bool(pathspecs)}
    commits, docs_only = [], []
    ref, shown = scan_ref(clone, scope)
    entry["ref"] = shown
    try:
        # The count is the one walk under the pathspecs, so it takes --full-history: a pathspec alone simplifies
        # history, and a side branch netting to nothing outside the set would vanish from it. The matched commits
        # are filtered one by one below, which walks no history and so has no simplification to fall into.
        walk = ["--full-history", ref, "--", *pathspecs] if pathspecs else [ref, "--"]
        rc, out, err = _git_in(clone, "rev-list", "--no-merges", "--count", *walk)
        if rc != 0:
            raise SearchFailed("cannot count commits on %s: %s" % (shown, _last_line(err, "exit %s" % rc)))
        entry["scanned"] = int(out.strip())
        for sha, date, body in _log(clone, ref, [EDGE_L + ere_escape(k) + EDGE_R for k in keys], merges=False):
            named = [k for k in keys if patterns[k].search(body)]
            if named:
                commits.append({"repo": clone, "sha": sha, "date": date, "subject": _subject(body),
                                "keys": named, "via": "message", "prs": []})
        if pathspecs:
            outside = _touching_outside(clone, [c["sha"] for c in commits], pathspecs)
            docs_only = [{k: c[k] for k in ("repo", "sha", "date", "subject", "keys")}
                         for c in commits if c["sha"] not in outside]
            commits = [c for c in commits if c["sha"] in outside]
    except SearchFailed as e:
        entry["error"] = str(e)
        entry["scanned"] = None  # a clone with an error was not read, whatever the count said first
        return entry, [], [], ref
    entry["matched"] = len(commits)
    return entry, commits, docs_only, ref


def _touching_outside(clone, shas, pathspecs):
    """The commits among `shas` -- none of them a merge -- that touch a path outside the documentation set.

    One --no-walk call compares each commit with its parent, a root commit with the empty tree, and walks no
    history. No SHA, no call: given none, git would read HEAD instead."""
    if not shas:
        return set()
    rc, out, err = _git_in(clone, "log", "--no-walk=unsorted", "--format=%H", *shas, "--", *pathspecs)
    if rc != 0:
        raise SearchFailed("cannot read which commits touch a path outside the documentation set: "
                           + _last_line(err, "exit %s" % rc))
    return set(out.split())


def probe_clone(clone, ref, keys, accounted, pathspecs=()):
    rows = [row for row in _log(clone, ref, [ere_escape(k) for k in keys], merges=True)
            if (clone, row[0]) not in accounted]
    if pathspecs and rows:
        outside = _brought_in_outside(clone, [row[0] for row in rows], pathspecs)
        rows = [row for row in rows if row[0] in outside]
    return [{"sha": sha, "date": date, "subject": _subject(body)} for sha, date, body in rows]


def _brought_in_outside(clone, shas, pathspecs):
    """The commits among `shas` that brought in a path outside the documentation set: a merge whose diff from its
    first parent touches one -- or that git could not compare, since a merge is never dropped untested -- and each
    other commit _touching_outside keeps. No merge reaches _touching_outside."""
    if not shas:
        return set()
    rc, out, err = _git_in(clone, "rev-list", "--no-walk=unsorted", "--parents", *shas)
    if rc != 0:
        raise SearchFailed("cannot read the parents of the commits to filter: " + _last_line(err, "exit %s" % rc))
    merges, others = [], []
    for line in out.splitlines():
        fields = line.split()
        if fields:
            (merges if len(fields) >= 3 else others).append(fields[0])  # the commit and at least two parents
    outside = _touching_outside(clone, others, pathspecs)
    for sha in merges:
        rc, _, _ = _git_in(clone, "diff", "--quiet", sha + "^1", sha, "--", *pathspecs)
        if rc != 0:
            outside.add(sha)
    return outside


def parse_remote(url):
    """(host, path, is_ssh) of a remote URL, or None."""
    url = url.strip()
    m = re.fullmatch(r"(https?)://(?:[^@/]+@)?([^/:]+)(?::\d+)?/(.+)", url)
    if m:
        return m.group(2), m.group(3), False
    m = re.fullmatch(r"ssh://(?:[^@/]+@)?([^/:]+)(?::\d+)?/(.+)", url)
    if m:
        return m.group(1), m.group(2), True
    m = re.fullmatch(r"(?:[^@/:]+@)?([^/:]+):(?!/)(.+)", url)
    if m:
        return m.group(1), m.group(2), True
    return None


def real_host(host, is_ssh):
    """An SSH host alias resolved through `ssh -G`, as the family's handoff references resolve it."""
    if not is_ssh or host == "github.com" or not PLAIN_HOST_RE.fullmatch(host):
        return host
    rc, out, _ = _run(["ssh", "-G", host], SSH_TIMEOUT)
    if rc == 0:
        for line in out.splitlines():
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[0].lower() == "hostname":
                resolved = parts[1].strip()
                return "github.com" if resolved == "ssh.github.com" else resolved
    return host


def remote_slug(clone):
    """The slug the commands' slug->clone map gives a clone: its origin URL's last path segment."""
    rc, out, _ = _git_in(clone, "remote", "get-url", "origin")
    url = out.strip().rstrip("/") if rc == 0 else ""
    if url.endswith(".git"):
        url = url[:-4]
    slug = re.split(r"[/:]", url)[-1] if url else ""
    return slug or None


def github_slug(clone):
    rc, out, _ = _git_in(clone, "remote", "get-url", "origin")
    if rc != 0:
        return None
    parsed = parse_remote(out)
    if not parsed:
        return None
    host, path, is_ssh = parsed
    if real_host(host, is_ssh) != "github.com":
        return None
    path = path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return path if OWNER_REPO_RE.fullmatch(path) else None


def gh_blocker():
    """(status, detail) where gh cannot search, else (None, None)."""
    if shutil.which("gh") is None:
        return "not-installed", None
    rc, out, err = _run(["gh", "auth", "status", "--hostname", "github.com"], GH_TIMEOUT)
    if rc == 0:
        return None, None
    return "not-authenticated", _last_line(err or out, "exit %s" % rc)


def search(owners, batch):
    argv = ["gh", "search", "prs"]
    for owner in owners:
        argv += ["--owner", owner]
    argv += ["--limit", str(SEARCH_LIMIT), "--json", "number,title,body,state,url,repository", "--"]
    for i, key in enumerate(batch):
        argv += (["OR"] if i else []) + ['"%s"' % key]
    rc, out, err = _run(argv, GH_TIMEOUT)
    if rc != 0:
        reason = _last_line(err or out, "exit %s" % rc)
        if "rate limit" in (err + out).lower():
            raise RateLimited(reason)
        raise SearchFailed(reason)
    try:
        hits = json.loads(out)
    except ValueError:
        raise SearchFailed("gh search printed no JSON")
    if not isinstance(hits, list):
        raise SearchFailed("gh search printed no list")
    return hits


def view(owner_repo, number):
    rc, out, err = _run(["gh", "pr", "view", str(number), "--repo", owner_repo, "--json",
                         "state,headRefName,baseRefName,headRefOid,mergeCommit,isCrossRepository,commits"], GH_TIMEOUT)
    if rc != 0:
        raise SearchFailed("gh pr view failed: " + _last_line(err, "exit %s" % rc))
    try:
        details = json.loads(out)
    except ValueError:
        raise SearchFailed("gh pr view failed: no JSON")
    if not isinstance(details, dict):
        raise SearchFailed("gh pr view failed: no JSON object")
    return details


def landing(clone, merge_oid, pr_commits, ref="HEAD", shown="HEAD"):
    """(landed_as, landed, reason) for a merged pull request's merge commit on the scanned ref."""
    rc, _, _ = _git_in(clone, "cat-file", "-e", merge_oid + "^{commit}")
    if rc != 0:
        return None, [], "merge commit not in the clone"
    rc, _, _ = _git_in(clone, "merge-base", "--is-ancestor", merge_oid, ref)
    if rc != 0:
        return None, [], "merge commit not on %s" % shown
    rc, out, err = _git_in(clone, "rev-list", "--parents", "-n", "1", merge_oid)
    if rc != 0:
        return None, [], "cannot read the merge commit: " + _last_line(err, "exit %s" % rc)
    parents = out.split()[1:]
    if len(parents) >= 2:
        rc, out, err = _git_in(clone, "rev-list", "--merges", "--parents", "%s^1..%s^2" % (merge_oid, merge_oid))
        if rc != 0:
            return None, [], "cannot list the merged commits: " + _last_line(err, "exit %s" % rc)
        for line in out.splitlines():
            for parent in line.split()[2:]:
                inside, _, _ = _git_in(clone, "merge-base", "--is-ancestor", parent, merge_oid + "^1")
                if inside != 0:
                    return None, [], "lands other branches' merges -- read by hand"
        rc, out, err = _git_in(clone, "rev-list", "--reverse", "--no-merges", "%s^1..%s^2" % (merge_oid, merge_oid))
        if rc != 0:
            return None, [], "cannot list the merged commits: " + _last_line(err, "exit %s" % rc)
        return "merge", out.split(), None
    n = len(pr_commits)
    if n > 1:
        rc, out, _ = _git_in(clone, "log", "--first-parent", "-z", "-n", str(n), "--format=%H%x1f%B", merge_oid)
        rows = [r.lstrip("\n").split("\x1f", 1) for r in out.split("\0")] if rc == 0 else []
        rows = [(r[0], r[1].split("\n", 1)[0].strip()) for r in rows if len(r) == 2]
        rows.reverse()
        if len(rows) == n and all(_same_headline(row[1], c.get("messageHeadline") or "") for row, c in zip(rows, pr_commits)):
            return "rebase", [row[0] for row in rows], None
    return "squash", [merge_oid], None


def _same_headline(first_line, headline):
    """GitHub's messageHeadline is a commit's first line, cut short with an ellipsis when it is long."""
    headline = headline.strip()
    if headline.endswith("\u2026"):
        stem = headline[:-1].rstrip()
        return bool(stem) and first_line.startswith(stem)
    return first_line == headline


def _pr_entry(hit, keys):
    owner_repo = hit.get("repository", {}).get("nameWithOwner", "")
    owner, _, repo = owner_repo.partition("/")
    return {"url": hit.get("url"), "owner": owner, "repo": repo, "number": hit.get("number"),
            "title": hit.get("title") or "", "state": STATES.get(str(hit.get("state", "")).lower(), "CLOSED"),
            "keys": keys, "clone": None, "head_ref": None, "base_ref": None, "head_oid": None,
            "merge_commit": None, "cross_repository": None, "landed_as": None, "landed": [], "reason": None,
            "landed_docs_only": []}


def _leave_out_documentation(clone, pr, pathspecs):
    """Move each commit a pull request landed in the documentation-holding repository that touches no path outside
    the documentation set from `landed` to `landed_docs_only`."""
    try:
        outside = _brought_in_outside(clone, pr["landed"], pathspecs)
    except SearchFailed as e:
        pr["landed_as"], pr["landed"], pr["reason"] = None, [], str(e)
        return
    pr["landed_docs_only"] = [sha for sha in pr["landed"] if sha not in outside]
    pr["landed"] = [sha for sha in pr["landed"] if sha in outside]
    if not pr["landed"]:
        pr["reason"] = "landed documentation only"


def github_layer(keys, patterns, clones, slugs, owner_slugs=(), excluded=(), refs=None, ruled=(), pathspecs=()):
    refs = refs or {}
    result = {"status": "ok", "detail": None, "owners": [], "queries": 0, "dropped_loose": 0, "prs": []}
    by_slug = {}
    for clone in clones:
        if slugs.get(clone):
            by_slug.setdefault(slugs[clone].lower(), clone)
    owners = []
    for slug in [slugs.get(clone) for clone in clones] + list(owner_slugs):
        owner = (slug or "").split("/")[0]
        if owner and owner.lower() not in [o.lower() for o in owners]:
            owners.append(owner)
    if not owners:
        result["status"] = "no-github-clones"
        return result
    started = _now()  # the budget covers every GitHub call: the auth check, the searches and the views
    blocker, detail = gh_blocker()
    if blocker:
        result["status"], result["detail"] = blocker, detail
        return result
    result["owners"] = owners
    found, failures, loose = {}, [], set()
    for start in range(0, len(keys), BATCH):
        if _now() - started >= GH_BUDGET:
            left = (len(keys) - start + BATCH - 1) // BATCH
            failures.append("the GitHub time budget (%ds) ran out before every search ran -- %d of %d not run: %s"
                            % (GH_BUDGET, left, (len(keys) + BATCH - 1) // BATCH, " OR ".join(keys[start:])))
            break
        batch = keys[start:start + BATCH]
        result["queries"] += 1
        try:
            hits = search(owners, batch)
        except RateLimited as e:
            failures.append("%s: %s" % (" OR ".join(batch), e))
            result["status"], result["detail"] = "rate-limited", "; ".join(failures)
            break
        except SearchFailed as e:
            failures.append("%s: %s" % (" OR ".join(batch), e))
            continue
        if len(hits) >= SEARCH_LIMIT:
            failures.append("%s: %d hits, the search's limit -- more were not read" % (" OR ".join(batch), len(hits)))
        malformed = 0
        for hit in hits:
            if not isinstance(hit, dict) or not hit.get("url") or not isinstance(hit.get("repository"), dict):
                malformed += 1
                continue
            text = str(hit.get("title") or "") + "\n" + str(hit.get("body") or "")
            named = [k for k in keys if patterns[k].search(text)]
            url = hit.get("url")
            repo = str(hit.get("repository", {}).get("name", "")).lower()
            if repo in excluded:
                continue
            if not named:
                loose.add(url)
            elif url in found:
                found[url]["keys"] = [k for k in keys if k in found[url]["keys"] or k in named]
            elif url:
                found[url] = _pr_entry(hit, named)
        if malformed:
            failures.append("%s: %d results gh printed in a shape it does not use" % (" OR ".join(batch), malformed))
    result["dropped_loose"] = len(loose)
    for pr in found.values():
        clone = by_slug.get(("%s/%s" % (pr["owner"], pr["repo"])).lower())
        pr["clone"] = clone
        if clone is None:
            continue
        if _now() - started >= GH_BUDGET:
            pr["reason"] = "not viewed -- the GitHub time budget ran out"
            if "time budget" not in "; ".join(failures):
                failures.append("the GitHub time budget (%ds) ran out before every pull request was viewed" % GH_BUDGET)
            continue
        try:
            details = view("%s/%s" % (pr["owner"], pr["repo"]), pr["number"])
        except SearchFailed as e:
            pr["reason"] = str(e)
            continue
        merge = (details.get("mergeCommit") or {}).get("oid")
        pr.update({"state": STATES.get(str(details.get("state", "")).lower(), pr["state"]),
                   "head_ref": details.get("headRefName"), "base_ref": details.get("baseRefName"),
                   "head_oid": details.get("headRefOid"), "merge_commit": merge,
                   "cross_repository": details.get("isCrossRepository")})
        if pr["state"] == "MERGED" and merge:
            ref, shown = refs.get(clone, ("HEAD", "HEAD"))
            commits = [c for c in (details.get("commits") or []) if isinstance(c, dict)]
            pr["landed_as"], pr["landed"], pr["reason"] = landing(clone, merge, commits, ref, shown)
            if clone in ruled and pr["landed"]:
                _leave_out_documentation(clone, pr, pathspecs)
    if failures and result["status"] == "ok":
        result["status"], result["detail"] = "partial", "; ".join(failures)
    result["prs"] = list(found.values())
    return result


def _describe(clone, shas):
    rc, out, _ = _git_in(clone, "show", "-s", "--date=iso-strict-local", "--format=%H%x1f%cd%x1f%s", *shas)
    rows = {}
    if rc == 0:
        for line in out.splitlines():
            parts = line.split("\x1f")
            if len(parts) == 3:
                rows[parts[0]] = (parts[1], parts[2])
    return rows


def documentation_set(root, content=()):
    """(docs, pathspecs) for the documentation root `root` and the content paths `content`.

    docs is None where `root` is in no git work tree. pathspecs is None unless docs["rule"] is "paths"; it is then
    the whole tree less the documentation set -- each content path, matched as the literal path it is, and each of
    FAMILY_DOC_PATHS -- every pathspec taken from the repository's top level.
    """
    rc, out, _ = _git_in(root, "rev-parse", "--show-toplevel")
    top = out.rstrip("\n") if rc == 0 else ""
    if not top:
        return None, None
    rc, out, _ = _git_in(root, "rev-parse", "--show-prefix")  # the root relative to the top level, "" at the top
    if rc != 0:
        return None, None
    top = os.path.realpath(top)
    content_paths, rejected = [], []
    below = out.rstrip("\n").rstrip("/")
    if below:
        content_paths.append(below)  # the root's own directory, where it lies below the top level
    for given in content:
        if given.startswith("/"):
            rejected.append({"path": given, "why": "absolute -- a content path is relative to the top level"})
            continue
        path = given
        while path.startswith("./"):
            path = path[2:]
        path = path.rstrip("/") or "."
        if ".." in path.split("/"):
            rejected.append({"path": given, "why": "holds a .. segment"})
            continue
        if path not in content_paths:
            content_paths.append(path)
    if "." in content_paths:
        rule, reason = "left-out", "the content path is the whole repository"
    elif not content_paths:
        rule, reason = "left-out", "no content path"
    else:
        rule, reason = "paths", None
    docs = {"root": root, "top": top, "repo": remote_slug(top) or os.path.basename(top), "rule": rule,
            "reason": reason, "content_paths": content_paths, "rejected": rejected, "clones": [], "docs_only": []}
    if rule != "paths":
        return docs, None
    return docs, ([":(top)"] + [":(exclude,top,literal)" + path for path in content_paths]
                  + [":(exclude,top,%s)%s" % (magic, pattern) for magic, pattern in FAMILY_DOC_PATHS])


def discover(keys, clones, scope, probe=False, github=True, excludes=(), owners_of=(), docs_root=None,
             docs_content=()):
    patterns = {k: whole_pattern(k) for k in keys}
    docs, pathspecs = documentation_set(docs_root, docs_content) if docs_root is not None else (None, None)
    excluded, excluded_paths, lowered = [], set(), set()

    def leave_out(path):
        rc, out, _ = _git_in(path, "rev-parse", "--show-toplevel")
        top = os.path.realpath(out.strip()) if rc == 0 and out.strip() else None
        if top is None or top != os.path.realpath(path):
            return  # only a repository's own top level is a repository to leave out
        excluded_paths.add(top)
        slug = remote_slug(top)
        if slug:
            lowered.add(slug.lower())
        name = slug or os.path.basename(top)
        if name.lower() not in [e.lower() for e in excluded]:
            excluded.append(name)

    for path in excludes:
        leave_out(path)
    docs_slug = ""
    if docs is not None:
        docs_slug = (remote_slug(docs["top"]) or "").lower()
        if docs["rule"] == "paths" and (docs["top"] in excluded_paths or (docs_slug and docs_slug in lowered)):
            docs["rule"], docs["reason"], pathspecs = "left-out", "--exclude names it too", None
        if docs["rule"] == "left-out":
            leave_out(docs["top"])  # left out whole, exactly as an --exclude of its top level
    if excluded_paths:
        clones = [c for c in clones
                  if os.path.realpath(c) not in excluded_paths and (remote_slug(c) or "").lower() not in lowered]
    ruled = set()
    if pathspecs:  # every clone of the documentation-holding repository, by its path or by its origin's slug
        ruled = {c for c in clones
                 if os.path.realpath(c) == docs["top"] or (docs_slug and (remote_slug(c) or "").lower() == docs_slug)}
        docs["clones"] = [c for c in clones if c in ruled]
    repos, commits, docs_only, refs = [], [], [], {}
    for clone in clones:
        entry, found, only, ref = scan_clone(clone, scope, keys, patterns, pathspecs if clone in ruled else ())
        repos.append(entry)
        commits += found
        docs_only += only
        refs[clone] = (ref, entry["ref"])
    if docs is not None:
        docs["docs_only"] = docs_only
    if github:
        slugs = {clone: github_slug(clone) for clone in clones}
        for entry in repos:
            entry["github"] = slugs[entry["path"]]
        dropped = set(lowered)
        if pathspecs and not ruled and docs_slug:
            dropped.add(docs_slug)  # no clone of it is read: its pull requests go by name, as an --exclude's do
        try:
            layer = github_layer(keys, patterns, clones, slugs, [github_slug(c) for c in owners_of], dropped, refs,
                                 ruled, pathspecs or ())
        except Exception as e:  # the GitHub layer is optional: its failure never costs the commit scan
            layer = {"status": "partial", "detail": "the GitHub search failed: %s: %s" % (type(e).__name__, e),
                     "owners": [], "queries": 0, "dropped_loose": 0, "prs": []}
    else:
        layer = {"status": "off", "detail": None, "owners": [], "queries": 0, "dropped_loose": 0, "prs": []}
    index = {(c["repo"], c["sha"]): c for c in commits}
    accounted = set()
    for pr in layer["prs"]:
        if pr["clone"] is None:
            continue
        if pr["merge_commit"]:
            accounted.add((pr["clone"], pr["merge_commit"]))
        missing = [sha for sha in pr["landed"] if (pr["clone"], sha) not in index]
        described = _describe(pr["clone"], missing) if missing else {}
        for sha in pr["landed"]:
            accounted.add((pr["clone"], sha))
            known = index.get((pr["clone"], sha))
            if known is None:
                date, subject = described.get(sha, (None, None))
                known = {"repo": pr["clone"], "sha": sha, "date": date, "subject": subject,
                         "keys": list(pr["keys"]), "via": "pull-request", "prs": []}
                index[(pr["clone"], sha)] = known
                commits.append(known)
            if pr["url"] not in known["prs"]:
                known["prs"].append(pr["url"])
            known["keys"] = [k for k in keys if k in known["keys"] or k in pr["keys"]]
        for sha in pr["landed_docs_only"]:
            accounted.add((pr["clone"], sha))  # filtered out, but still the pull request's: never probed
    if probe:
        for entry in repos:
            if entry["error"] is None and entry["matched"] == 0:
                try:
                    entry["probe"] = probe_clone(entry["path"], refs[entry["path"]][0], keys, accounted,
                                                 pathspecs if entry["path"] in ruled else ())
                except SearchFailed as e:
                    entry["probe_error"] = str(e)  # the scan stands; only the report-only probe failed
    return {"keys": keys, "scope": scope, "excluded": excluded, "repos": repos, "commits": commits, "github": layer,
            "docs": docs}


def docs_check(root, content, base, head="HEAD"):
    """The docs-check document: the paths `git diff <base> <head>` lists outside the documentation set."""
    docs, pathspecs = documentation_set(root, content)
    outside = []
    if pathspecs:
        rc, out, err = _git_in(docs["top"], "diff", "--name-only", "--no-renames", "-z", base, head, "--", *pathspecs)
        if rc != 0:
            raise Unrunnable("git diff %s %s failed: %s" % (base, head, _last_line(err, "exit %s" % rc)))
        outside = [path for path in out.split("\0") if path]
    if docs is not None:
        docs = {k: v for k, v in docs.items() if k not in ("clones", "docs_only")}
    return {"docs": docs, "base": base, "head": head, "outside": outside}


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    parser = argparse.ArgumentParser(prog="key-discovery.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan")
    scan.add_argument("--key", action="append", required=True)
    scan.add_argument("--repo", action="append", required=True)
    scan.add_argument("--scope", choices=("head", "default"), required=True)
    scan.add_argument("--probe", action="store_true")
    scan.add_argument("--no-github", action="store_true")
    scan.add_argument("--exclude", action="append", default=[])
    scan.add_argument("--owner-of", action="append", default=[])
    scan.add_argument("--docs-root", action="append", default=[])
    scan.add_argument("--docs-content", action="append", default=[])
    check = sub.add_parser("docs-check")
    check.add_argument("--docs-root", action="append", required=True)
    check.add_argument("--docs-content", action="append", default=[])
    check.add_argument("--base", required=True)
    check.add_argument("--head", default="HEAD")
    args = parser.parse_args(argv)
    try:
        if args.docs_content and not args.docs_root:
            raise Unrunnable("--docs-content needs --docs-root")
        if len(args.docs_root) > 1:
            raise Unrunnable("--docs-root is given %d times; it takes one directory" % len(args.docs_root))
        docs_root = args.docs_root[0] if args.docs_root else None
        if docs_root is not None and not os.path.isdir(docs_root):
            raise Unrunnable("--docs-root %s is not a directory" % docs_root)
        if args.command == "docs-check":
            for flag, rev in (("--base", args.base), ("--head", args.head)):
                if not rev or rev.startswith("-"):
                    raise Unrunnable("%s %r is empty or starts with '-'" % (flag, rev))
            if shutil.which("git") is None:
                raise Unrunnable("git is not on PATH")
            print(json.dumps(docs_check(docs_root, args.docs_content, args.base, args.head),
                             ensure_ascii=False, indent=1))
            return 0
        keys = []
        for key in args.key:
            if not key or re.search(r'[\s"]', key):
                raise Unrunnable("--key %r is empty or holds whitespace or a quote" % key)
            if key not in keys:
                keys.append(key)
        clones = []
        for repo in args.repo:
            if not os.path.isdir(repo):
                raise Unrunnable("--repo %s is not a directory" % repo)
            path = os.path.realpath(repo)
            if path not in clones:
                clones.append(path)
        for flag, paths in (("--exclude", args.exclude), ("--owner-of", args.owner_of)):
            for path in paths:
                if not os.path.isdir(path):
                    raise Unrunnable("%s %s is not a directory" % (flag, path))
        if shutil.which("git") is None:
            raise Unrunnable("git is not on PATH")
        print(json.dumps(discover(keys, clones, args.scope, args.probe, not args.no_github,
                                  [os.path.realpath(p) for p in args.exclude],
                                  [os.path.realpath(p) for p in args.owner_of],
                                  docs_root, args.docs_content), ensure_ascii=False, indent=1))
    except Unrunnable as e:
        print("key-discovery: %s" % e, file=sys.stderr)
        return 2
    except Exception as e:  # any other failure is the script's, reported in one line -- never a traceback
        print("key-discovery: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
