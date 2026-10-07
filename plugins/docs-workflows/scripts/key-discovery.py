#!/usr/bin/env python3
"""key-discovery.py — the commits and pull requests that name a key.

  key-discovery.py scan --key <K> [--key <K> ...] --repo <clone> [--repo <clone> ...]
                        --scope head|default [--probe] [--no-github]
                        [--exclude <clone> ...] [--owner-of <clone> ...]
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
commit scan. --exclude names a clone whose repository is never code -- a specs or a docs
repository: every --repo with its origin's slug is left unscanned, and every pull request in a
repository of that name is dropped. --owner-of names a clone that is not scanned but whose GitHub
owner is searched too. Prints one JSON document, indented so a reader can take it line by line;
fetches nothing and writes nothing.

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
STATES = {"merged": "MERGED", "open": "OPEN", "closed": "CLOSED"}


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
    name = name or "f%d.txt" % next(_FILES)
    with open(os.path.join(repo, name), "a", encoding="utf-8") as fh:
        fh.write(message + "\n")
    _git(repo, "add", name)
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


def case_the_view_budget_runs_out(tmp):
    r = _github_clone(tmp)
    _commit(r, "base")
    _no_ssh_alias(tmp)
    _gh(tmp, [_search_hit("acme/app", 24, "[ACME-7]")], {24: _merged_view("7" * 40)})
    saved = globals()["GH_BUDGET"]
    globals()["GH_BUDGET"] = 0
    try:
        out = discover(["ACME-7"], [r], "head")
    finally:
        globals()["GH_BUDGET"] = saved
    (pr,) = out["github"]["prs"]
    assert pr["head_ref"] is None and "budget" in pr["reason"] and out["github"]["status"] == "partial", out["github"]


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
    assert set(doc) == {"keys", "scope", "excluded", "repos", "commits", "github"}
    assert set(doc["github"]) == {"status", "detail", "owners", "queries", "dropped_loose", "prs"}
    assert out.count("\n") > 10 and max(len(line) for line in out.splitlines()) < 2000, "indented, line-readable JSON"


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


def scan_clone(clone, scope, keys, patterns):
    """The repos[] entry for one clone and its key-matched commits."""
    entry = {"path": clone, "ref": None, "scanned": None, "matched": 0, "github": None, "error": None, "probe": []}
    commits = []
    ref, shown = scan_ref(clone, scope)
    entry["ref"] = shown
    try:
        rc, out, err = _git_in(clone, "rev-list", "--no-merges", "--count", ref, "--")
        if rc != 0:
            raise SearchFailed("cannot count commits on %s: %s" % (shown, _last_line(err, "exit %s" % rc)))
        entry["scanned"] = int(out.strip())
        for sha, date, body in _log(clone, ref, [EDGE_L + ere_escape(k) + EDGE_R for k in keys], merges=False):
            named = [k for k in keys if patterns[k].search(body)]
            if named:
                commits.append({"repo": clone, "sha": sha, "date": date, "subject": _subject(body),
                                "keys": named, "via": "message", "prs": []})
    except SearchFailed as e:
        entry["error"] = str(e)
        return entry, [], ref
    entry["matched"] = len(commits)
    return entry, commits, ref


def probe_clone(clone, ref, keys, accounted):
    rows = _log(clone, ref, [ere_escape(k) for k in keys], merges=True)
    return [{"sha": sha, "date": date, "subject": _subject(body)} for sha, date, body in rows
            if (clone, sha) not in accounted]


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
            "merge_commit": None, "cross_repository": None, "landed_as": None, "landed": [], "reason": None}


def github_layer(keys, patterns, clones, slugs, owner_slugs=(), excluded=(), refs=None):
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
    blocker, detail = gh_blocker()
    if blocker:
        result["status"], result["detail"] = blocker, detail
        return result
    result["owners"] = owners
    found, failures, loose = {}, [], set()
    for start in range(0, len(keys), BATCH):
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
    started = time.monotonic()
    for pr in found.values():
        clone = by_slug.get(("%s/%s" % (pr["owner"], pr["repo"])).lower())
        pr["clone"] = clone
        if clone is None:
            continue
        if time.monotonic() - started >= GH_BUDGET:
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


def discover(keys, clones, scope, probe=False, github=True, excludes=(), owners_of=()):
    patterns = {k: whole_pattern(k) for k in keys}
    excluded, excluded_paths, lowered = [], set(), set()
    for path in excludes:
        rc, out, _ = _git_in(path, "rev-parse", "--show-toplevel")
        top = os.path.realpath(out.strip()) if rc == 0 and out.strip() else None
        if top is None or top != os.path.realpath(path):
            continue  # only a repository's own top level is a repository to leave out
        excluded_paths.add(top)
        slug = remote_slug(top)
        if slug:
            lowered.add(slug.lower())
        name = slug or os.path.basename(top)
        if name.lower() not in [e.lower() for e in excluded]:
            excluded.append(name)
    if excludes:
        clones = [c for c in clones
                  if os.path.realpath(c) not in excluded_paths and (remote_slug(c) or "").lower() not in lowered]
    repos, commits, refs = [], [], {}
    for clone in clones:
        entry, found, ref = scan_clone(clone, scope, keys, patterns)
        repos.append(entry)
        commits += found
        refs[clone] = (ref, entry["ref"])
    if github:
        slugs = {clone: github_slug(clone) for clone in clones}
        for entry in repos:
            entry["github"] = slugs[entry["path"]]
        try:
            layer = github_layer(keys, patterns, clones, slugs, [github_slug(c) for c in owners_of], lowered, refs)
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
    if probe:
        for entry in repos:
            if entry["error"] is None and entry["matched"] == 0:
                try:
                    entry["probe"] = probe_clone(entry["path"], refs[entry["path"]][0], keys, accounted)
                except SearchFailed as e:
                    entry["error"] = "probe: %s" % e
    return {"keys": keys, "scope": scope, "excluded": excluded, "repos": repos, "commits": commits, "github": layer}


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
    args = parser.parse_args(argv)
    try:
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
                                  [os.path.realpath(p) for p in args.owner_of]), ensure_ascii=False, indent=1))
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
