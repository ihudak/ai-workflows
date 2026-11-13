# specs_git_selftest.py — specs-git.py's selftest.
#
# specs-git.py --selftest executes this file in that script's own namespace, so every name here that this file does
# not define is the script's. It is never imported, because the tests read and patch the script through globals() and
# read its source through __file__. It lives outside the plugin so that it is not shipped to users.

# Run on its own, this file has no script around it: _run_selftest is a name only specs-git.py defines. (__name__
# cannot tell the two apart, since in the script's namespace it is "__main__" too.)
if "_run_selftest" not in globals():
    raise SystemExit("specs_git_selftest.py: not run (it runs only inside specs-git.py: "
                     "python3 plugins/workflows-core/scripts/specs-git.py --selftest)")

import contextlib
import tempfile

SPECS_REPO_GIT = os.path.join(HERE, "..", "references", "specs-repo-git.md")
ADDRESSING = os.path.join(HERE, "..", "references", "addressing.md")
SESSION_HYGIENE = os.path.join(HERE, "..", "references", "session-hygiene.md")


def selftest(groups=None):
    """Every rule this script carries, on repositories built at run time: every group where groups is None, else
    only the named groups, in the selftest's own order."""
    # Before anything runs: CI reads only the exit status, so a partial run there is refused; and a run that
    # scenarios_selftest started (SPECS_GIT_SELFTEST_NESTED) fails where it would run group selftest, which would start
    # runs of its own, so a break in group selection fails that group instead of recursing.
    if groups is not None and os.environ.get("GITHUB_ACTIONS") == "true":
        print("specs-git: not run (--group is refused in CI, where GITHUB_ACTIONS is true: a partial run is never "
              "evidence that the selftest passes)", file=sys.stderr)
        return 2
    if os.environ.get("SPECS_GIT_SELFTEST_NESTED") == "1" and (groups is None or "selftest" in groups):
        print("specs-git selftest: FAIL (nested)")
        print("  s_nested: a nested run was asked for every group, or for group selftest")
        return 1
    failures = []
    count = [0]
    me = os.path.abspath(__file__)
    os.environ["GIT_CONFIG_GLOBAL"] = os.devnull
    os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
    os.environ.pop("GIT_USER_INITIALS", None)
    os.environ.pop("CLAUDE_CODE_SESSION_ID", None)

    def check(ok, what):
        count[0] += 1
        if not ok:
            failures.append(what)

    def utc_day():
        """The UTC date _today() gives now: every expected <YYYY-MM-DD> is read when the line it checks is rendered,
        never fixed at the selftest's start, so a run across 00:00 UTC compares each date with its own render's."""
        return _today()

    def local_day():
        """The local date `date +%Y-%m-%d` gives now, as _record_refusal writes it: read when the record is checked."""
        return time.strftime("%Y-%m-%d")

    def dated(call):
        """<call>()'s result, with the dates a line or record it wrote can carry: the UTC dates (utc_day) and the local
        dates (local_day) read just before the call and just after it -- one each, or two where the call crossed
        midnight. A check accepts either, so no crossing, before the call or during it, fails one."""
        utc, local = utc_day(), local_day()
        got = call()
        return got, sorted({utc, utc_day()}), sorted({local, local_day()})

    class Repo:
        def __init__(self, path):
            self.path = path

        def git(self, *args, check=True, env=None):
            r = subprocess.run(["git", "-C", self.path, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env=dict(os.environ, **(env or {})))
            if check and r.returncode != 0:
                raise AssertionError("git %s: %s" % (" ".join(args), r.stderr.decode("utf-8", "replace")))
            return r.stdout.decode("utf-8", "surrogateescape").strip()

        def write(self, rel, body):
            full = os.path.join(self.path, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8", newline="") as fh:
                fh.write(body)

        def commit_all(self, message):
            self.git("add", "-A")
            self.git("commit", "-q", "-m", message)
            return self.git("rev-parse", "HEAD")

    def new_repo(base, name="repo"):
        path = os.path.join(base, name)
        os.makedirs(path)
        r = Repo(path)
        r.git("init", "-q", "-b", "main")
        r.git("config", "user.email", "t@example.invalid")
        r.git("config", "user.name", "t")
        r.git("config", "commit.gpgsign", "false")
        r.write("README.md", "specs\n")
        r.commit_all("init")
        return r

    def cli(*args, env=None, stdin=None, cwd=None, script=None):
        return parsed(subprocess.run([sys.executable, script or me, *args], stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, input=stdin, cwd=cwd, env=dict(os.environ, **(env or {}))))

    def shell(line, env):
        """A next.run (or on_timeout) line as the skill runs it: verbatim, in a Bash call of its own."""
        return parsed(subprocess.run(["bash", "-c", line], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     env=dict(os.environ, **env)))

    def parsed(r):
        out = r.stdout.decode("utf-8", "replace")
        try:
            got = json.loads(out) if out.strip() else {}
        except ValueError:
            got = {"_stdout": out}
        got["_raw"] = r.stdout
        got["_rc"] = r.returncode
        got["_err"] = r.stderr.decode("utf-8", "replace")
        return got

    def one_not_run_line(got):
        lines = got.get("_err", "").splitlines()
        return got.get("_rc") == 2 and len(lines) == 1 and lines[0].startswith("specs-git: not run (")

    def scenarios_status(tmp):
        r = new_repo(tmp, "status")
        resume = "specifications/PRD-ACME-1-zahlungsauslösung/dev-workflows/resume.md"
        follow = "specifications/PRD-ACME-2-a b/follow-ups.md"
        frames = "specifications/PRD-ACME-3/design/frame-set/index.md"
        shot = "specifications/PRD-ACME-3/Doc screenshots/a.png"
        prd = "specifications/PRD-ACME-3/prd.md"
        reg = "security/web/register.json"
        threat = "security/web/threat-model.md"
        for p in (resume, follow, frames, shot, prd, reg, threat):
            r.write(p, "x\n")
        r.write("dev-workflows-cost/x.md", "cost\n")
        r.git("add", "dev-workflows-cost/x.md")
        r.git("commit", "-q", "-m", "cost")
        r.git("mv", "dev-workflows-cost/x.md", "dev-workflows-cost/y.md")
        got = status(r.path)
        check(set(got["artifact"]) == {resume, follow, reg, "dev-workflows-cost/y.md"},
              "status: the artifact list (%r)" % got)
        check(not any(p.endswith("/x.md") for p in got["artifact"] + got["other"]),
              "status: a rename's original path is no record of its own (%r)" % got)
        check(set(got["other"]) == {frames, shot, prd, threat}, "status: the other list (%r)" % got)
        check(got["artifact"] == sorted(got["artifact"]) and got["other"] == sorted(got["other"]),
              "status: both lists sorted (%r)" % got)
        got = cli("--specs", r.path, "status")
        check(got["_rc"] == 0 and set(got.get("artifact", [])) == {resume, follow, reg, "dev-workflows-cost/y.md"},
              "status: the CLI prints the same object (%r)" % got)
        check(resume.encode("utf-8") in got["_raw"],
              "status: a non-ASCII path is printed as git gave it, never as a \\u escape (%r)" % got["_raw"][:300])
        got = cli("--specs", os.path.join(r.path, "specifications"), "status")
        check(one_not_run_line(got) and "_stdout" not in got and "artifact" not in got,
              "a subdirectory is not the top level: exit 2, one line, no JSON (%r)" % got)
        plain = os.path.join(tmp, "plain")
        os.makedirs(plain)
        got = cli("--specs", plain, "status")
        check(one_not_run_line(got), "a directory that is no repository: exit 2, one line (%r)" % got)
        got = cli("status")
        check(one_not_run_line(got), "no --specs: exit 2, one line (%r)" % got)
        lone = os.path.join(tmp, "lone")
        os.makedirs(lone)
        shutil.copy(me, os.path.join(lone, "specs-git.py"))
        rr = subprocess.run([sys.executable, os.path.join(lone, "specs-git.py"), "--specs", r.path, "status"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        err = rr.stderr.decode("utf-8", "replace").splitlines()
        check(rr.returncode == 2 and len(err) == 1 and err[0].startswith("specs-git: not run ("),
              "a missing session-branch.py exits 2 with one line, no traceback (%r)" % rr.stderr)
        got = cli("--specs", r.path, "no-such-subcommand")
        check(one_not_run_line(got), "an unknown subcommand: exit 2, one line (%r)" % got)

    def lines30(changes=None):
        rows = ["line %02d\n" % n for n in range(1, 31)]
        for n, body in (changes or {}).items():
            rows[n - 1] = body
        return "".join(rows)

    def scenarios_branch_merged(tmp):
        def case(name):
            r = new_repo(tmp, "merged-" + name)
            r.write("f.txt", lines30())
            r.commit_all("thirty lines")
            return r

        r = case("ff")
        r.git("switch", "-q", "-c", "prd/A-1-x")
        r.write("a.md", "a\n")
        r.commit_all("a")
        r.git("switch", "-q", "main")
        r.git("merge", "-q", "--ff-only", "prd/A-1-x")
        check(branch_merged(r.path, "prd/A-1-x", "main") == {"merged": True, "test": 1},
              "branch-merged: a fast-forward is test 1")

        r = case("rebase")
        r.git("switch", "-q", "-c", "prd/A-2-x")
        r.write("a.md", "a\n")
        c1 = r.commit_all("a")
        r.write("b.md", "b\n")
        c2 = r.commit_all("b")
        r.git("switch", "-q", "main")
        r.write("other.md", "o\n")
        r.commit_all("other")
        r.git("cherry-pick", c1, c2)
        check(branch_merged(r.path, "prd/A-2-x", "main") == {"merged": True, "test": 2},
              "branch-merged: a rebase merge is test 2 (%r)" % branch_merged(r.path, "prd/A-2-x", "main"))

        r = case("evil-merge")
        r.git("switch", "-q", "-c", "side")
        r.write("s.md", "s\n")
        s1 = r.commit_all("side")
        r.git("switch", "-q", "main")
        r.git("switch", "-q", "-c", "prd/A-3-x")
        r.git("merge", "-q", "--no-ff", "--no-commit", "side")
        r.write("extra.md", "the branch's own change, inside the merge commit\n")
        r.git("add", "extra.md")
        r.git("commit", "-q", "-m", "merge side, with a change of its own")
        r.git("switch", "-q", "main")
        r.git("cherry-pick", s1)
        got = branch_merged(r.path, "prd/A-3-x", "main")
        check(got == {"merged": False, "test": None},
              "branch-merged: a change of its own inside a merge commit is not merged by test 2 (%r)" % got)

        r = case("squash")
        r.git("switch", "-q", "-c", "prd/A-4-x")
        r.write("a.md", "a\n")
        r.commit_all("a")
        r.write("b.md", "b\n")
        r.commit_all("b")
        r.git("switch", "-q", "main")
        r.git("merge", "-q", "--squash", "prd/A-4-x")
        r.git("commit", "-q", "-m", "squash")
        r.write("specifications/PRD-A-4-x/dev-workflows/resume.md", "dirty\n")
        check(branch_merged(r.path, "prd/A-4-x", "main") == {"merged": True, "test": 3},
              "branch-merged: a squash merge is test 3, with a dirty session file in the tree (GIT-B2) (%r)"
              % branch_merged(r.path, "prd/A-4-x", "main"))

        r = case("drift")
        r.git("switch", "-q", "-c", "prd/A-5-x")
        r.write("f.txt", lines30({10: "branch line 10\n"}))
        r.commit_all("line 10")
        r.git("switch", "-q", "main")
        r.write("f.txt", lines30({12: "main line 12\n"}))
        r.commit_all("line 12")
        check(branch_merged(r.path, "prd/A-5-x", "main") == {"merged": False, "test": None},
              "branch-merged: before its squash the drifted branch is unmerged")
        r.git("merge", "-q", "--squash", "prd/A-5-x")
        r.git("commit", "-q", "-m", "squash line 10")
        got = branch_merged(r.path, "prd/A-5-x", "main")
        check(got == {"merged": True, "test": 4}, "branch-merged: GIT-B1's drifted squash is test 4 (%r)" % got)

        r = case("empty")
        r.git("switch", "-q", "-c", "prd/A-6-x")
        check(branch_merged(r.path, "prd/A-6-x", "main") == {"merged": True, "test": 1},
              "branch-merged: a branch with no commit of its own is test 1")
        r.git("commit", "-q", "--allow-empty", "-m", "nothing")
        r.git("switch", "-q", "main")
        got = branch_merged(r.path, "prd/A-6-x", "main")
        check(got == {"merged": False, "test": None}, "branch-merged: an empty change is never merged by 3 or 4 (%r)" % got)

        r = case("open")
        r.git("switch", "-q", "-c", "prd/A-7-x")
        r.write("a.md", "a\n")
        r.commit_all("a")
        r.git("switch", "-q", "main")
        check(branch_merged(r.path, "prd/A-7-x", "main") == {"merged": False, "test": None},
              "branch-merged: open work is unmerged")
        got = cli("--specs", r.path, "branch-merged", "--ref", "prd/A-7-x", "--default-ref", "main")
        check(got["_rc"] == 0 and got.get("merged") is False and "test" in got, "branch-merged: the CLI (%r)" % got)
        r.write("specifications/x.md", "x\n")
        got = cli("--specs", os.path.join(r.path, "specifications"), "branch-merged", "--ref", "prd/A-7-x", "--default-ref", "main")
        check(got["_rc"] == 0 and got.get("merged") is False,
              "branch-merged: runs where $SPECS_PATH is below the top level, as §3.5 does under misrooted (%r)" % got)
        got = cli("--specs", r.path, "branch-merged", "--ref", "prd/no-such", "--default-ref", "main")
        check(one_not_run_line(got), "branch-merged: a ref that does not resolve exits 2 (%r)" % got)

    def scenarios_branch_key(tmp):
        cases = [
            ("spec/PRODUCT-1234-2fa-rollout", ["PRODUCT-1234"], "PRODUCT-1234"),
            ("spec/PRODUCT-1234-2fa-rollout", ["PRODUCT-1234", "PRODUCT-1234-2"], "PRODUCT-1234"),
            ("spec/ACME-77-01-checkout", ["ACME-77", "ACME-77-01"], "ACME-77-01"),
            ("ard/EPIC-008-01_slug", ["EPIC-008-01"], "EPIC-008-01"),
            ("prd/ACME-7", ["ACME-7"], "ACME-7"),
            ("prd/ACME-77-x", ["ACME-7"], None),
            ("prd/ACME-7-x", [], None),
        ]
        for branch, keys, want in cases:
            got = branch_key(branch, keys)
            check(got["plugin_branch"] is True and got["key"] == want,
                  "branch-key: %s with %r resolves to %r (%r)" % (branch, keys, want, got))
        got = branch_key("kb/harvest-2026-11-08", ["ACME-7"])
        check(got == {"plugin_branch": True, "prefix": "kb", "key": None}, "branch-key: a kb/ branch holds no key (%r)" % got)
        got = branch_key("feature/ACME-7-x", ["ACME-7"])
        check(got == {"plugin_branch": False, "prefix": None, "key": None},
              "branch-key: a branch outside the prefixes is no plugin branch (%r)" % got)
        with open(SPECS_REPO_GIT, encoding="utf-8") as fh:
            m = re.search(r"its name matches `\^\(([a-z|]+)\)/`", fh.read())
        check(m is not None and tuple(m.group(1).split("|")) == PREFIXES,
              "branch-key: PREFIXES is specs-repo-git §2.2's alternation (%r)" % (m and m.group(1)))
        r = new_repo(tmp, "branch-key")
        got = cli("--specs", r.path, "branch-key", "--branch", "spec/ACME-77-01-x", "--key", "ACME-77", "--key", "ACME-77-01")
        check(got["_rc"] == 0 and got.get("key") == "ACME-77-01", "branch-key: the CLI (%r)" % got)
        sub_dir = os.path.join(r.path, "specifications")
        os.makedirs(sub_dir)
        got = cli("--specs", sub_dir, "branch-key", "--branch", "spec/ACME-77-01-x", "--key", "ACME-77-01")
        check(got["_rc"] == 0 and got.get("key") == "ACME-77-01",
              "branch-key: runs where $SPECS_PATH is below the top level (%r)" % got)
        got = cli("--specs", r.path, "branch-key", "--branch", "spec/ACME-77-01-x")
        check(got["_rc"] == 0 and got.get("key") is None, "branch-key: no --key is a keyless run (%r)" % got)

    def with_origin(tmp, name):
        bare = os.path.join(tmp, name + ".git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
        r = new_repo(tmp, name)
        r.git("remote", "add", "origin", bare)
        r.git("push", "-q", "-u", "origin", "main")
        return r

    def scenarios_push_scope(tmp):
        session_file = "specifications/PRD-A-1-x/dev-workflows/resume.md"
        r = with_origin(tmp, "scope-plugin")
        r.git("switch", "-q", "-c", "prd/A-1-x")
        r.write("specifications/PRD-A-1-x/prd.md", "prd\n")
        r.commit_all("deliverable")
        r.git("push", "-q", "-u", "origin", "prd/A-1-x")
        r.write(session_file, "resume\n")
        c = r.commit_all("session")
        got = push_scope(r.path, "prd/A-1-x")
        check(got == {"base": "refs/remotes/origin/prd/A-1-x", "commits": [c], "in_scope": True, "failed": None},
              "push-scope: one session-file commit past the pushed branch (%r)" % got)
        r.write("specifications/PRD-A-1-x/prd.md", "changed\n")
        bad = r.commit_all("deliverable again")
        got = push_scope(r.path, "prd/A-1-x")
        check(got["in_scope"] is False and got["failed"] == {"sha": bad, "reason": "paths",
              "path": "specifications/PRD-A-1-x/prd.md"}, "push-scope: a deliverable path fails (%r)" % got)

        r = with_origin(tmp, "scope-merge")
        r.git("switch", "-q", "-c", "prd/A-2-x")
        r.git("push", "-q", "-u", "origin", "prd/A-2-x")
        r.git("switch", "-q", "-c", "side")
        r.write("specifications/PRD-A-2-x/dev-workflows/resume.md", "r\n")
        r.commit_all("session on side")
        r.git("switch", "-q", "prd/A-2-x")
        r.git("merge", "-q", "--no-ff", "-m", "merge side", "side")
        merge = r.git("rev-parse", "HEAD")
        got = push_scope(r.path, "prd/A-2-x")
        check(got["in_scope"] is False and got["failed"] == {"sha": merge, "reason": "merge", "path": None},
              "push-scope: a merge commit fails (%r)" % got)

        r = with_origin(tmp, "scope-new")
        r.git("switch", "-q", "-c", "prd/A-3-x")
        r.write("specifications/PRD-A-3-x/dev-workflows/resume.md", "r\n")
        c = r.commit_all("session")
        got = push_scope(r.path, "prd/A-3-x")
        check(got == {"base": None, "commits": [c], "in_scope": True, "failed": None},
              "push-scope: a branch never pushed is walked over --remotes=origin (%r)" % got)

        r = with_origin(tmp, "scope-session")
        r.git("switch", "-q", "-c", "session/ab")
        r.write("specifications/PRD-A-4-x/dev-workflows/resume.md", "1\n")
        r.commit_all("session 1")
        r.git("push", "-q", "-u", "origin", "session/ab")
        r.git("switch", "-q", "main")
        r.write("main.md", "m\n")
        r.commit_all("main moves")
        r.git("push", "-q", "origin", "main")
        r.git("switch", "-q", "session/ab")
        r.git("merge", "-q", "--no-ff", "-m", "NOISSUE Merge main into session/ab", "main")
        r.write("specifications/PRD-A-4-x/dev-workflows/resume.md", "2\n")
        r.commit_all("session 2")
        got = push_scope(r.path, "session/ab", session_default_ref="origin/main")
        check(got["in_scope"] is True and got["base"] == "refs/remotes/origin/session/ab" and len(got["commits"]) == 2,
              "push-scope: the session branch admits its merge of the default branch (%r)" % got)
        r.write("specifications/PRD-A-4-x/prd.md", "p\n")
        r.commit_all("a deliverable on the session branch")
        r.git("push", "-q", "origin", "session/ab")
        r.write("specifications/PRD-A-4-x/dev-workflows/resume.md", "3\n")
        r.commit_all("session 3")
        got = push_scope(r.path, "session/ab", session_default_ref="origin/main")
        newest_merge = r.git("rev-list", "--merges", "-n", "1", "refs/heads/session/ab")
        check(got["in_scope"] is False and got["failed"] == {"sha": newest_merge, "reason": "branch-path",
              "path": "specifications/PRD-A-4-x/prd.md"},
              "push-scope: the session branch's whole change must name session files only (%r)" % got)
        got = cli("--specs", r.path, "push-scope", "--branch", "session/ab", "--session-default-ref", "origin/main")
        check(got["_rc"] == 0 and got.get("in_scope") is False, "push-scope: the CLI (%r)" % got)

        r = with_origin(tmp, "scope-session-2")
        r.git("switch", "-q", "-c", "session/cd")
        r.write("specifications/PRD-A-5-x/prd.md", "p\n")
        bad = r.commit_all("a deliverable, unpushed")
        got = push_scope(r.path, "session/cd", session_default_ref="origin/main")
        check(got["base"] is None and got["failed"] == {"sha": bad, "reason": "paths", "path": "specifications/PRD-A-5-x/prd.md"},
              "push-scope: a never-pushed session branch walks --remotes=origin and fails a deliverable commit (%r)" % got)
        r.git("switch", "-q", "--orphan", "session/ef")
        r.write("specifications/PRD-A-6-x/dev-workflows/resume.md", "r\n")
        r.git("add", "specifications/PRD-A-6-x/dev-workflows/resume.md")
        r.git("commit", "-q", "-m", "a root commit")
        root = r.git("rev-parse", "HEAD")
        got = push_scope(r.path, "session/ef", session_default_ref="origin/main")
        check(got["failed"] == {"sha": root, "reason": "merge", "path": None}, "push-scope: a root commit fails as merge (%r)" % got)

        r = with_origin(tmp, "scope-session-3")
        r.git("switch", "-q", "-c", "session/gh")
        r.write("specifications/PRD-A-7-x/prd.md", "p\n")
        r.commit_all("a deliverable")
        r.git("push", "-q", "-u", "origin", "session/gh")
        r.write("specifications/PRD-A-7-x/dev-workflows/resume.md", "r\n")
        r.commit_all("session")
        got = push_scope(r.path, "session/gh", session_default_ref="origin/main")
        check(got["failed"] == {"sha": None, "reason": "branch-path", "path": "specifications/PRD-A-7-x/prd.md"},
              "push-scope: branch-path with no merge commit names sha null (%r)" % got)
        got = cli("--specs", r.path, "push-scope", "--branch", "no-such")
        check(one_not_run_line(got), "push-scope: a branch that does not exist exits 2 (%r)" % got)

    def scenarios_owner_repo(tmp):
        conf = os.path.join(tmp, "ssh_config")
        with open(conf, "w", encoding="utf-8") as fh:
            fh.write("Host github-ig.com\n  HostName github.com\n")
        cases = [
            ("git@github.com:acme/docs.git", True, "acme/docs"),
            ("https://github.com/acme/docs", True, "acme/docs"),
            ("ssh://git@git.example.com:2222/team/docs.git", True, "git.example.com/team/docs"),
            ("https://git.example.com/team/docs/", True, "git.example.com/team/docs"),
            ("git@github-ig.com:acme/repo.git", False, "github-ig.com/acme/repo"),
            ("https://github.com/", True, None),
        ]
        if shutil.which("ssh"):
            cases.append(("git@github-ig.com:acme/repo.git", True, "acme/repo"))
        for url, alias, want in cases:
            got = owner_repo(url, resolve_alias=alias, ssh_config=conf)
            check(got["owner_repo"] == want and "url" not in got,
                  "owner-repo: %s (alias %s) gives %r (%r)" % (url, alias, want, got))
        for url, name in [("https://bitbucket.example.com/scm/proj/docs.git", "bitbucket.example.com/scm/proj/docs"),
                          ("https://gitlab.example.com/group/sub/docs.git", "gitlab.example.com/group/sub/docs"),
                          ("/srv/git/docs.git", "//srv/git/docs"),
                          ("git@github.com:acme/docs.git", "acme/docs"),
                          ("https://github.com/", None)]:
            got = owner_repo(url, resolve_alias=False)
            check(got["name"] == name, "owner-repo: %s's unvalidated derivation, the <docs-repo-slug> source, is %r (%r)"
                  % (url, name, got))
        r = new_repo(tmp, "owner-none")
        got = cli("owner-repo", "--repo", r.path)
        check(got["_rc"] == 0 and all(got.get(k) is None for k in ("host", "slug", "name", "owner_repo")),
              "owner-repo: a repository with no origin gives nulls (%r)" % got)
        r.git("remote", "add", "origin", "https://x-access-token:ghp_FAKE0123@github.com/acme/docs.git")
        got = cli("owner-repo", "--repo", r.path, "--no-alias")
        check(got["_rc"] == 0 and got.get("owner_repo") == "acme/docs", "owner-repo: the CLI (%r)" % got)
        check(b"ghp_FAKE0123" not in got["_raw"] and b"x-access-token" not in got["_raw"],
              "owner-repo: a credential in the remote URL is never printed (%r)" % got["_raw"])
        plain = os.path.join(tmp, "plain-owner")
        os.makedirs(plain)
        got = cli("owner-repo", "--repo", plain)
        check(one_not_run_line(got), "owner-repo: a path that is no repository exits 2 (%r)" % got)

    def scenarios_mode(tmp):
        r = new_repo(tmp, "mode")
        got = cli("--specs", r.path, "mode", "--default", "main")
        check(got["_rc"] == 0 and got.get("mode") == "off" and got.get("source") is None, "mode: off by default (%r)" % got)
        r.git("config", "workflows.sessionBranch", "true")
        got = cli("--specs", r.path, "mode", "--default", "main", env={"GIT_USER_INITIALS": "ab"})
        check(got["_rc"] == 0 and got.get("mode") in ("on", "unsupported") and got.get("source") == "config"
              and got.get("branch") == "session/ab", "mode: the opt-in key turns it on (%r)" % got)

        # Session-branch mode in start and end (specs-repo-git §8). Each world turns the mode on with
        # workflows.sessionBranch and names its identity with GIT_USER_INITIALS=ab, unless a case says otherwise.
        _, lines = _flow()
        g = globals()
        S = "session/ab"
        SB = os.path.join(HERE, "session-branch.py")
        FEED = "specifications/PRD-ACME-1-x/dev-workflows/feedback/"
        A, A_FEED = "prd/ACME-2-a", "specifications/PRD-ACME-2-a/dev-workflows/feedback/"
        B = "prd/B-2-y"
        SUBJECT = "NOISSUE Add dev-workflows session artifacts (/feedback)"

        def mode_world(name, initials="ab", on=True):
            r, env = world(tmp, name)
            if on:
                r.git("config", "workflows.sessionBranch", "true")
            if initials:
                env["GIT_USER_INITIALS"] = initials
            return r, env

        def run_start(env, *args):
            return cli("--specs", env["SPECS_PATH"], "start", "--command", "/feedback", *args, env=env)

        def end_of(env, *args):
            return run_end(env, "/feedback", *args)

        def ref(r, name):
            return r.git("rev-parse", "--verify", "-q", "refs/heads/" + name, check=False) or None

        def sb_cli(r, env, *args):
            """session-branch.py run as a command runs it, to build a world's overlay."""
            subprocess.run([sys.executable, SB, "--specs", r.path, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=dict(os.environ, **env), check=True)

        def untracked(r, path):
            return "?? " + path in r.git("status", "--porcelain", "--untracked-files=all")

        def overlay(r, branch=S):
            """The session paths where <branch> differs from HEAD, and whether the working tree holds <branch>'s version
            of each, or none where <branch> lacks it: specs-repo-git §8.3's overlay in place."""
            if ref(r, branch) is None:
                return [], False
            paths = [p for p in r.git("diff", "--name-only", "HEAD", branch).splitlines() if sb.classify(p)]
            ok = True
            for p in paths:
                want = subprocess.run(["git", "-C", r.path, "show", "%s:%s" % (branch, p)], stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL)
                full, have = os.path.join(r.path, p), None
                if os.path.isfile(full):
                    with open(full, "rb") as fh:
                        have = fh.read()
                ok = ok and have == (want.stdout if want.returncode == 0 else None)
            return paths, ok

        def checked_out(r, branch=S):
            """The worktree path git names for the checkout holding <branch>, as session-branch.py's refusal names it."""
            where = None
            for line in r.git("worktree", "list", "--porcelain").splitlines():
                if line.startswith("worktree "):
                    where = line[len("worktree "):]
                elif line == "branch refs/heads/" + branch:
                    return where
            return None

        def not_run(where):
            return ("Specs preflight: session-branch.py could not run (session-branch: not run (%s is checked out at %s; "
                    "switch that checkout back to the default branch))" % (S, where))

        def pushed_session(sha7, n, f):
            return ("Specs repo: committed %s (%s) on session/ab — pushed; %d session file(s) not on main yet: merge its "
                    "pull request, or open one with gh pr create --head session/ab --base main"
                    % (sha7, "1 file" if n == 1 else "%d files" % n, f))

        def left(branch):
            return ("Specs preflight: left %s for main, since no key of this run names it — the branch and its pull "
                    "request are as they were" % branch)

        def wrapped_world(name):
            """w.md tracked on main as v0 and on B as vB; session/ab holds v1, the overlay over B: git refuses B's
            switch to main over that working copy unless it is lifted first."""
            r, env = mode_world(name)
            w = FEED + "w.md"
            r.write(w, "v0\n")
            r.commit_all("NOISSUE v0")
            r.git("push", "-q", "origin", "main")
            r.write(w, "v1\n")
            sb_cli(r, env, "commit", "--branch", S, "--default-ref", "origin/main", "--message", "NOISSUE w")
            sb_cli(r, env, "lift", "--branch", S)
            r.git("switch", "-q", "-c", B)
            r.write(w, "vB\n")
            r.commit_all("NOISSUE vB")
            r.git("push", "-q", "-u", "origin", B)
            sb_cli(r, env, "put-back", "--branch", S, "--default-ref", "origin/main")
            return r, env, w

        def read(r, path):
            with open(os.path.join(r.path, path), encoding="utf-8") as fh:
                return fh.read()

        # m_created
        r, env = mode_world("m-created")
        main = head(r)
        got = run_start(env)
        want = "Specs preflight: created local session/ab at %s; no session file to commit yet" % main[:7]
        check(got["_rc"] == 0 and got.get("mode") == "on" and got.get("session_branch") == S and got.get("error") is None
              and got.get("print") == [env_line(r.path), want] and ref(r, S) == main and got.get("next") is None,
              "m_created: a clean main creates session/ab at its base and says so, nothing to commit (%r)" % got)
        r, env = mode_world("m-created-dirty")
        main = head(r)
        r.write(FEED + "c.md", "c\n")
        got = run_start(env)
        tip = ref(r, S) or ""
        want = "Specs preflight: created local session/ab at %s, and committed %s on it" % (main[:7], tip[:7])
        check(got.get("print") == [env_line(r.path), want] and r.git("rev-parse", tip + "~1", check=False) == main
              and r.git("log", "-1", "--format=%s", tip, check=False) == SUBJECT,
              "m_created: a dirty session file committed on the new session branch, never on HEAD (%r)" % got)
        paths, ok = overlay(r)
        check(on_origin(r, S) == tip and head(r) == main and on_origin(r) == main and paths == [FEED + "c.md"] and ok,
              "m_created: the session branch pushed, main untouched, the overlay in place after start (%r)" % paths)

        # m_created_by_lift: the catch-up's lift finds l.md unpreserved, and its commit creates session/ab -- a creation
        # by §8.3's call, not the flush's, so it is carried (across a --rerun too) to end's line
        r, env = mode_world("m-created-by-lift")
        other = clone(r, "m-created-by-lift-other")
        other.write("notes.md", "n\n")
        other.commit_all("notes")
        other.git("push", "-q", "origin", "main")
        main = head(r)
        r.write(FEED + "l.md", "l\n")
        got = run_start(env)
        check(got.get("print") == [env_line(r.path)] and head(r) == on_origin(r) and on_origin(r, S) == ref(r, S)
              and (record(env, "/feedback") or {}).get("session_branch_created") == main[:7],
              "m_created_by_lift: no pre.created line, the creation saved for end (%r)" % got)
        got = run_start(env, "--rerun")
        check((record(env, "/feedback") or {}).get("session_branch_created") == main[:7], "m_created_by_lift: --rerun carries it")
        r.write(FEED + "l2.md", "l2\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        check(got.get("print") == [pushed_session(tip[:7], 1, 2) + "; this run created local session/ab at " + main[:7]],
              "m_created_by_lift: end's line appends it (%r)" % got)

        # m_land_merged: in the mode the session files never commit on HEAD (§8.2), so no stay is kept and no landing
        # runs: G1 on a merged plugin branch prints the plain block, records no stay, and end commits on session/ab and
        # pushes, as the mode does
        r, env = mode_world("m-land-merged")
        M = "prd/M-1-x"
        r.git("switch", "-q", "-c", M)
        r.write("specifications/PRD-M-1-x/prd.md", "m\n")
        r.commit_all("M-1 work")
        r.git("push", "-q", "-u", "origin", M)
        other = clone(r, "m-land-merged-other")
        other.git("merge", "-q", "--ff-only", "origin/" + M)
        other.git("push", "-q", "origin", "main")
        r.write("notes.md", "n\n")
        r.write(FEED + "d.md", "d\n")
        h = head(r)
        plain = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 1, "<path list>": "notes.md"})
        got = run_start(env)
        check(got.get("print") == [env_line(r.path), plain] and got.get("branch") == M
              and (record(env, "/feedback") or {}).get("stay") is None,
              "m_land_merged: the mode's G1 is the plain block, and no stay is recorded (%r)" % got)
        got = end_of(env)
        tip = ref(r, S) or ""
        check(got.get("row") == "pushed-session" and got.get("print") == [
                  pushed_session(tip[:7], 1, 1) + "; this run created local session/ab at " + h[:7], plain]
              and on_origin(r, S) == tip and head(r) == h and r.git("symbolic-ref", "--short", "HEAD") == M,
              "m_land_merged: end commits on session/ab and pushes, HEAD unmoved (%r)" % got)

        # m_no_stay: G1 on a branch no key of the run names, in the mode -- whose commit takes every session file the
        # overlay holds, keeping no snapshot apart (specs-repo-git §3.5) -- keeps no stay and takes no snapshot, so no
        # object is written for the session file in the working tree
        r, env = mode_world("m-no-stay")
        other_key(r)
        r.write("notes.md", "n\n")
        mine = FEED + "m.md"
        r.write(mine, "m-no-stay\n")
        plain = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 1, "<path list>": "notes.md"})
        got = run_start(env, "--key", "ACME-1")
        rec = record(env, "/feedback") or {}
        unstored = subprocess.run(["git", "-C", r.path, "cat-file", "-e", r.git("hash-object", "--", mine)],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0
        check(got.get("print") == [env_line(r.path), plain] and got.get("mode") == "on"
              and "stay" in got and got["stay"] is None and "start_dirty" in got and got["start_dirty"] is None
              and rec.get("stay") is None and rec.get("start_dirty") is None and unstored,
              "m_no_stay: the plain block, no stay, no snapshot, no object written (%r)" % got)

        # m_end_pushed
        r, env = mode_world("m-end-pushed")
        run_start(env)
        r.write(FEED + "e.md", "e\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        check(got["_rc"] == 0 and got.get("row") == "pushed-session" and got.get("print") == [pushed_session(tip[:7], 1, 1)]
              and got.get("branch") == S and got.get("pushed") is True and got.get("next") is None
              and on_origin(r, S) == tip and r.git("log", "-1", "--format=%s", tip) == SUBJECT
              and record(env, "/feedback") is None,
              "m_end_pushed: committed on session/ab and pushed, <F> counted against main (%r)" % got)
        r.write(FEED + "e2.md", "e2\n")
        got = end_of(env, "--session-branch-created", "abc1234")
        tip = ref(r, S) or ""
        check(got.get("print") == [pushed_session(tip[:7], 1, 2) + "; this run created local session/ab at abc1234"],
              "m_end_pushed: --session-branch-created appends the created clause (%r)" % got)
        got = end_of(env)
        check(got.get("row") == "nothing" and got.get("print") == ["Specs repo: no session artifacts to commit"]
              and ref(r, S) == tip, "m_end_pushed: commit's committed null is nothing to commit, nothing pushed (%r)" % got)
        r, env = mode_world("m-no-remote")
        r.git("remote", "remove", "origin")
        r.write(FEED + "n.md", "n\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        check(got.get("print") == ["Specs repo: committed %s (1 file) on session/ab — not pushed: this specs repo has no "
                                   "origin remote; this run created local session/ab at %s" % (tip[:7], head(r)[:7])],
              "m_end_pushed: a not-pushed row names the session branch (%r)" % got)
        r, env = mode_world("m-end-created")
        main = head(r)
        r.write(FEED + "e.md", "e\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        check(got.get("print") == [pushed_session(tip[:7], 1, 1) + "; this run created local session/ab at " + main[:7]],
              "m_end_pushed: a session branch end's own commit created is appended as created (%r)" % got)

        # m_no_identity
        r, env = mode_world("m-no-identity", initials=None)
        r.write(RESUME, "r\n")
        got = end_of(env)
        want = ("Specs repo: NOT COMMITTED — session-branch mode is on and no identity names its branch; set "
                "GIT_USER_INITIALS (or git config user.initials), and the next run commits these files")
        check(got["_rc"] == 0 and got.get("row") == "no-identity" and got.get("print") == [want] and untracked(r, RESUME)
              and not r.git("for-each-ref", "refs/heads/session"), "m_no_identity: end commits nothing (%r)" % got)
        r.git("switch", "-q", "-c", B)
        r.write("specifications/PRD-B-2-y/prd.md", "b\n")
        r.git("add", "specifications/PRD-B-2-y/prd.md")
        r.git("commit", "-q", "-m", "B-2 Add the PRD")
        r.git("push", "-q", "-u", "origin", B)
        got = run_start(env)
        placed = os.path.join(r.path, r.git("rev-parse", "--git-path", "session-branch-placed.json"))
        check(got.get("mode") == "on" and got.get("session_branch") is None and got.get("print") == [env_line(r.path), left(B)]
              and got.get("branch") == "main" and untracked(r, RESUME) and not r.git("for-each-ref", "refs/heads/session")
              and not os.path.exists(placed),
              "m_no_identity: start's B4 switches unwrapped, the session file carried, nothing lifted (%r)" % got)

        # m_not_run
        r, env = mode_world("m-not-run")
        r.git("branch", S, "main")
        r.git("worktree", "add", "-q", os.path.join(tmp, "m-not-run-wt"), S)
        where = checked_out(r)
        r.write(RESUME, "r\n")
        got = run_start(env)
        check(got["_rc"] == 0 and got.get("error") is None and where
              and got.get("print") == [env_line(r.path), not_run(where), not_run(where)] and untracked(r, RESUME),
              "m_not_run: the flush's commit and the closing put-back each report it, and the run goes on (%r)" % got)
        got = end_of(env)
        want = ("Specs repo: NOT COMMITTED — session-branch.py could not run (session-branch: not run (%s is checked out "
                "at %s; switch that checkout back to the default branch)); the files stay in your working tree, and the "
                "next run commits them" % (S, where))
        check(got.get("row") == "session-not-run" and got.get("print") == [want] and untracked(r, RESUME),
              "m_not_run: end's session-not-run row names the checkout (%r)" % got)
        # the flush's commit could not run, yet what an earlier run left on the session branch is still pushed (§4 step 5)
        wt = Repo(os.path.join(tmp, "m-not-run-wt"))
        wt.write(FEED + "w.md", "w\n")
        wt.commit_all(SUBJECT)
        got = run_start(env)
        check(got.get("print") == [env_line(r.path), not_run(where), not_run(where)] and on_origin(r, S) == ref(r, S),
              "m_not_run: the session branch's own commits pushed all the same (%r)" % got)

        # m_g2
        found = ("⚠ SPECS REPO — ON A BRANCH THIS PLUGIN DID NOT CREATE\n\n"
                 "Found:    %s is on branch `%s`, which is neither the default\n"
                 "          branch (`main`) nor a plugin branch (idea/ prd/ ard/ spec/\n"
                 "          epics/ design/ ready/ brd/ frames/ kb/ conformance/).\n")
        def g2_session(path, branch):
            return (found % (path, branch)
                    + "Not done: the preflight did not switch away from it — the plugin manages only branches it created. "
                      "This run's artifacts WILL be committed on session/ab, the session branch this specs repository uses "
                      "because its default branch takes no push, and not on %s.\n"
                      "Fix:\n"
                      "If ignored: nothing changes for the artifacts, and nothing is to be run for them: they reach main "
                      "through session/ab's pull request."
                    % branch)

        def g2_no_identity(path, branch):
            return (found % (path, branch)
                    + "Not done: the preflight did not switch away from it — the plugin manages only branches it created. "
                      "Session-branch mode is on and no identity names its branch, so this run's artifacts will NOT be "
                      "committed until one is set.\n"
                      "Fix:\n"
                      "If ignored: the artifacts stay in your working tree, and the first run after you set "
                      "GIT_USER_INITIALS, or git -C \"%s\" config user.initials, to your initials commits them." % path)

        r, env = mode_world("m-g2")
        r.git("switch", "-q", "-c", "feature/x")
        got = run_start(env)
        want = g2_session(r.path, "feature/x")
        check(got.get("print") == [env_line(r.path), want] and got.get("guard") == "G2",
              "m_g2: on another branch, G2's session-branch lines (%r)" % got)
        r.git("switch", "-q", "-c", S, "main")
        got = run_start(env)
        want = (found % (r.path, S)
                + "Not done: the preflight did not switch away from it. It is this specs repository's session branch, "
                  "which the plugin commits to only while nothing stands on it, so this run's artifacts will NOT be "
                  "committed.\n"
                  "Fix:      git -C \"%s\" switch main\n"
                  "If ignored: the artifacts stay in your working tree, and the first run after you switch back commits "
                  "them." % r.path)
        check(got.get("print") == [env_line(r.path), want, not_run(checked_out(r))] and got.get("guard") == "G2",
              "m_g2: on session/ab itself its own variant, then the closing put-back's refusal (%r)" % got)
        r, env = mode_world("m-g2-no-identity", initials=None)
        r.git("switch", "-q", "-c", "feature/x")
        got = run_start(env)
        check(got.get("print") == [env_line(r.path), g2_no_identity(r.path, "feature/x")] and got.get("guard") == "G2"
              and got.get("session_branch") is None, "m_g2: with no identity, its no-identity variant (%r)" % got)
        # §5's precedence: a direct /implement run from inside the specs repository takes the mode's variants
        for initials, block in (("ab", g2_session), (None, g2_no_identity)):
            r, env = mode_world("m-g2-implement-%s" % (initials or "none"), initials=initials)
            r.git("switch", "-q", "-c", "feature/x")
            got = cli("--specs", r.path, "start", "--command", "/implement", env=env, cwd=r.path)
            check(got.get("print") == [env_line(r.path), block(r.path, "feature/x")] and got.get("guard") == "G2",
                  "m_g2: a direct /implement run in the mode takes the mode's variant, identity %r (%r)" % (initials, got))

        # m_unsupported
        r, env = mode_world("m-unsupported")
        fake = os.path.join(tmp, "m-unsupported-bin")
        os.makedirs(fake)
        with open(os.path.join(fake, "git"), "w", encoding="utf-8") as fh:
            fh.write('#!/bin/sh\nfor x in "$@"; do\n  if [ "$x" = merge-tree ]; then\n'
                     '    echo "usage: git merge-tree <base-tree> <branch1> <branch2>" >&2\n    exit 129\n  fi\ndone\n'
                     'exec "%s" "$@"\n' % shutil.which("git"))
        os.chmod(os.path.join(fake, "git"), 0o755)
        env["PATH"] = fake + os.pathsep + os.environ.get("PATH", "")
        r.write(FEED + "u.md", "u\n")
        got = run_start(env)
        check(got.get("mode") == "unsupported" and got.get("session_branch") is None and got.get("print") == [env_line(r.path)]
              and r.git("log", "-1", "--format=%s") == SUBJECT and on_origin(r) == head(r)
              and not r.git("for-each-ref", "refs/heads/session"),
              "m_unsupported: start runs as with the mode off, its flush committing on main (%r)" % got)
        r.write(FEED + "u2.md", "u2\n")
        got = end_of(env)
        want = ("Specs repo: committed %s (1 file) on main — pushed straight to main, and no pull request was opened: this "
                "plugin lands its session files there without review; to land them through a pull request of your own "
                "instead, turn on session-branch mode (§8) with git -C \"%s\" config workflows.sessionBranch true — where a "
                "container mounts this repository's .git/config read-only, run it on the host; "
                "session-branch mode is on for this clone, but this git's merge-tree cannot merge without a checkout (it "
                "needs --write-tree and -X), so these files stay on main until git is upgraded" % (head(r)[:7], r.path))
        check(got.get("row") == "pushed-default" and got.get("print") == [want],
              "m_unsupported: end's line ends with the unsupported clause (%r)" % got)
        r.git("checkout", "-q", "--detach")
        r.write(FEED + "u3.md", "u3\n")
        got = end_of(env)
        check(got.get("row") == "blocked" and (got.get("print") or [""])[0] == "Specs repo: NOT COMMITTED — see the notice below",
              "m_unsupported: no unsupported clause on a detached HEAD, which names no branch (%r)" % got)
        run_start(env)
        got = end_of(env)
        check(got.get("row") == "blocked" and (record(env, "/feedback") is None)
              and (got.get("print") or [""])[0] == "Specs repo: NOT COMMITTED — see the notice below",
              "m_unsupported: nor on the blocked flag start recorded in that mode (%r)" % got)

        # m_wrapped_b4
        r, env, w = wrapped_world("m-wrapped-b4")
        before = overlay(r)
        got = run_start(env)
        paths, ok = overlay(r)
        check(before == ([w], True) and read(r, w) == "v1\n", "m_wrapped_b4: the overlay holds w.md over B (%r)" % (before,))
        check(got.get("print") == [env_line(r.path), left(B)] and got.get("error") is None and got.get("branch") == "main"
              and got.get("b4_left") == B and paths == [w] and ok and read(r, w) == "v1\n" and on_origin(r, S) == ref(r, S),
              "m_wrapped_b4: B4 switches inside lift and put-back, the overlay back over main (%r)" % got)
        # the re-run's switch back is wrapped the same way: B's version of w.md differs from main's
        got = run_start(env, "--rerun", "--key", "B-2")
        paths, ok = overlay(r)
        check(got.get("print") == [env_line(r.path)] and got.get("branch") == B and got.get("b4_left") is None
              and paths == [w] and ok and read(r, w) == "v1\n",
              "m_wrapped_b4: the re-run's switch back inside lift and put-back, the overlay over B again (%r)" % got)

        # m_wrapped_catch_up: origin's main changed follow-ups.md, which the overlay holds, so git refuses the pull over
        # it unless it is lifted first -- start's §3.4 catch-up, and end's §4 step 2 for a run whose preflight never ran
        fu = "specifications/PRD-ACME-1-x/follow-ups.md"
        for kind in ("start", "end"):
            r, env = mode_world("m-catch-up-" + kind)
            r.write(fu, "- [ ] a\n")
            r.commit_all("NOISSUE a")
            r.git("push", "-q", "origin", "main")
            r.write(fu, "- [ ] a\n- [ ] b\n")
            sb_cli(r, env, "commit", "--branch", S, "--default-ref", "origin/main", "--message", "NOISSUE b")
            o = clone(r, "m-catch-up-%s-other" % kind)
            o.write(fu, "- [ ] a\n- [ ] c\n")
            o.commit_all("NOISSUE c")
            o.git("push", "-q", "origin", "main")
            if kind == "start":
                got = run_start(env)
                want, overlaid = [env_line(r.path)], [fu]
            else:  # e.md is not on the session branch yet, so the lift's commit carries it before the pull (§8.3)
                r.git("fetch", "-q", "origin")
                r.write(FEED + "e.md", "e\n")
                got = end_of(env)
                carried = r.git("log", "-1", "--format=%H", S, "--", FEED + "e.md")
                want, overlaid = [pushed_session(carried[:7], 1, 2)], [FEED + "e.md", fu]
                check(r.git("log", "-1", "--format=%s", carried) == SUBJECT and carried != ref(r, S),
                      "m_wrapped_catch_up: end's run commit is the lift's, step 4's message, below put-back's merge")
            paths, ok = overlay(r)
            check(got.get("print") == want and head(r) == on_origin(r) and read(r, fu) == "- [ ] a\n- [ ] b\n- [ ] c\n"
                  and paths == overlaid and ok and on_origin(r, S) == ref(r, S),
                  "m_wrapped_catch_up: %s's pull inside lift and put-back, origin's change merged into the session "
                  "branch and back over the checkout, which then pushes it (%r)" % (kind, got))

        # m_sync_conflict: origin's main changed implementation.md's header while the session branch edited its entry,
        # so §8.2 step 3 refuses that merge; end says so, and <F> counts what the session branch's pull request shows
        im = "specifications/PRD-ACME-1-x/implementation.md"
        entry = "## 2026-01-01 — /implement\n\n%s\n"
        r, env = mode_world("m-sync-conflict")
        r.write(im, "# Implementation\n\n" + entry % "x")
        r.commit_all("NOISSUE x")
        r.git("push", "-q", "origin", "main")
        r.write(im, "# Implementation\n\n" + entry % "y")
        sb_cli(r, env, "commit", "--branch", S, "--default-ref", "origin/main", "--message", "NOISSUE y")
        o = clone(r, "m-sync-conflict-other")
        o.write(im, "# Implementation log\n\n" + entry % "x")
        o.write("notes.md", "n\n")
        o.commit_all("NOISSUE header, and notes")
        o.git("push", "-q", "origin", "main")
        r.git("fetch", "-q", "origin")
        r.write(FEED + "e.md", "e\n")
        got = end_of(env)
        carried = r.git("log", "-1", "--format=%H", S, "--", FEED + "e.md")
        check(got.get("print") == [pushed_session(carried[:7], 1, 2) + "; merging main into session/ab left " + im
                                   + " unsettled — settle them in its pull request"] and on_origin(r, S) == ref(r, S),
              "m_sync_conflict: the conflict appended, <F> the session files the three-dot diff lists (%r)" % got)

        # m_end_commit_not_run (in process): the lift's commit carried e.md, then step 4's commit could not run
        r, env = mode_world("m-end-commit-not-run")
        other = clone(r, "m-end-commit-not-run-other")
        other.write("notes.md", "n\n")
        other.commit_all("notes")
        other.git("push", "-q", "origin", "main")
        r.git("fetch", "-q", "origin")
        r.write(FEED + "e.md", "e\n")
        main = head(r)
        real_commit, made = sb.commit, []

        def second_fails(*args):
            made.append(args)
            if len(made) > 1:
                raise NotRun("boom")
            return real_commit(*args)

        sb.commit = second_fails
        try:
            with in_env(env):
                got = end(r.path, "/feedback")
        finally:
            sb.commit = real_commit
        carried = r.git("log", "-1", "--format=%H", S, "--", FEED + "e.md")
        check(got.get("print") == ["Specs repo: session-branch.py could not run (session-branch: not run (boom))",
                                   pushed_session(carried[:7], 1, 1) + "; this run created local session/ab at " + main[:7]]
              and got.get("row") == "pushed-session"
              and on_origin(r, S) == ref(r, S) and len(made) == 2,
              "m_end_commit_not_run: reported, and the lift's commit is the run's, pushed (%r)" % got)

        # m_branch_path: another clone pushed a deliverable on session/ab; its merge makes the session branch's whole
        # change name a path that is no session file, so §8.4's push-scope fails with branch-path (§6's session form)
        r, env = mode_world("m-branch-path")
        o = clone(r, "m-branch-path-other")
        o.git("switch", "-q", "-c", S)
        o.write("specifications/PRD-ACME-3-z/prd.md", "z\n")
        o.commit_all("ACME-3 Add the PRD, on the session branch")
        o.git("push", "-q", "origin", S)
        main = head(r)
        r.write(FEED + "b1.md", "b1\n")
        got = run_start(env)
        b1 = r.git("log", "-1", "--format=%H", S, "--", FEED + "b1.md")
        merge = r.git("rev-list", "--merges", "-n", "1", S)
        check(got.get("print") == [env_line(r.path), "Specs preflight: created local session/ab at %s, and committed %s on it"
                                   % (main[:7], b1[:7])] and on_origin(r, S) == ref(o, S) and merge,
              "m_branch_path: the flush merges origin's copy and pushes nothing (%r)" % got)
        r.write(FEED + "b2.md", "b2\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        want = ("Specs repo: committed %s (1 file) on session/ab — not pushed: its pull request would also change "
                "specifications/PRD-ACME-3-z/prd.md, which is not one of this plugin's session files, and the branch's newest "
                "merge commit is %s NOISSUE Merge origin/session/ab into session/ab; push session/ab once that change is "
                "ready to go, and the artifacts go with it" % (tip[:7], merge[:7]))
        check(got.get("row") == "scope" and got.get("print") == [want] and got.get("error") is None
              and on_origin(r, S) == ref(o, S) and record(env, "/feedback") is None,
              "m_branch_path: end's push-scope row in its session-branch form, the record removed (%r)" % got)

        # m_end_resume (in process): a kill while §8.2's commit runs; end --resume finds what landed and pushes it
        real_commit = sb.commit

        def killed(*args):
            real_commit(*args)
            raise KeyboardInterrupt

        for name, existing in (("m-end-resume", False), ("m-end-resume-existing", True)):
            r, env = mode_world(name)
            if existing:
                r.git("branch", S, "main")
            main = head(r)
            r.write(FEED + "k.md", "k\n")
            sb.commit = killed
            try:
                with in_env(env):
                    try:
                        end(r.path, "/feedback")
                    except KeyboardInterrupt:
                        pass
            finally:
                sb.commit = real_commit
            pending = (record(env, "/feedback") or {}).get("end_commit") or {}
            check(pending == {"branch": S, "base": main if existing else None, "session": {}},
                  "m_end_resume: the pending end_commit saved before the commit (%s: %r)" % (name, pending))
            got = end_of(env, "--resume")
            carried = r.git("log", "-1", "--format=%H", S, "--", FEED + "k.md")
            want = pushed_session(carried[:7], 1, 1) + ("" if existing else "; this run created local session/ab at "
                                                        + main[:7])
            check(got.get("print") == [want] and got.get("record") == "found" and on_origin(r, S) == ref(r, S)
                  and record(env, "/feedback") is None,
                  "m_end_resume: --resume pushes the commit the kill left unnamed (%s: %r)" % (name, got))

        # m_blocked: both blocked rows carry the created clause, the one session-branch append §6 gives them
        blocked = "Specs repo: NOT COMMITTED — see the notice below; this run created local session/ab at abc1234"
        r, env = mode_world("m-blocked")
        r.git("checkout", "-q", "--detach")
        r.write(RESUME, "r\n")
        got = end_of(env, "--session-branch-created", "abc1234")
        check(got.get("row") == "blocked" and len(got.get("print") or []) == 2 and got["print"][0] == blocked
              and got["print"][1].startswith("⚠ SPECS REPO — THIS RUN'S ARTIFACTS WILL NOT BE COMMITTED"),
              "m_blocked: G0's state at end, the created clause appended (%r)" % got)
        got = run_start(env)
        block = (got.get("print") or ["", ""])[1]
        got = end_of(env, "--session-branch-created", "abc1234")
        check(got.get("row") == "blocked" and got.get("print") == [blocked, block],
              "m_blocked: the blocked flag start recorded, the created clause appended (%r)" % got)
        os.remove(os.path.join(r.path, RESUME))
        got = end_of(env, "--session-branch-created", "abc1234")
        check(got.get("row") == "nothing" and got.get("print") == [
            "Specs repo: no session artifacts to commit; this run created local session/ab at abc1234"],
              "m_blocked: the detached HEAD's nothing row takes the created clause too (%r)" % got)

        # m_not_finished (in process): §1 rule 5's line takes none of a row's appends, and a G2 block still follows it
        real_check = g["push_check"]

        def broken(*args, **kwargs):
            raise RuntimeError("boom")

        stop = ("Specs repo: NOT FINISHED — the terminal step stopped early (RuntimeError: boom); what it committed or "
                "pushed is as it left it, and the next run's preflight flushes the rest")
        r, env = mode_world("m-not-finished")
        r.git("switch", "-q", "-c", "feature/x")
        block = (run_start(env).get("print") or ["", ""])[1]
        r.write(FEED + "n.md", "n\n")
        r2, env2 = mode_world("m-not-finished-unsupported", on=False)
        seed(env2, "/feedback", mode="unsupported", session_branch_created="abc1234")
        r2.write(RESUME, "r\n")
        g["push_check"] = broken
        try:
            with in_env(env):
                got = end(r.path, "/feedback", session_branch_created="abc1234")
            with in_env(env2):
                got2 = end(r2.path, "/feedback")
        finally:
            g["push_check"] = real_check
        check(got.get("print") == [stop, block] and got.get("error") == "RuntimeError: boom"
              and block == g2_session(r.path, "feature/x"),
              "m_not_finished: no created clause, and the G2 block start saved after the line (%r)" % got)
        check(got2.get("print") == [stop], "m_not_finished: no unsupported clause either (%r)" % got2)
        # a resumed record holding a G1 block, stopped before its push step: the line, then the block, in the
        # not-committed form §5 gives the NOT FINISHED line
        r, env = mode_world("m-not-finished-resume", on=False)
        g1_block = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 1, "<path list>": ["notes.md", "notes.md"]})
        rows = g1_block.split("\n")
        at = {x: next(k for k, row in enumerate(rows) if row.startswith(x)) for x in ("Not done:", "Fix:", "If ignored:")}
        g1_stopped = "\n".join(rows[:at["Not done:"]] + ["Not done: " + lines.T["g1.not_done.uncommitted"]]
                               + rows[at["Fix:"]:at["If ignored:"]] + ["If ignored: " + lines.T["g1.if_ignored.uncommitted"]])
        seed(env, "/feedback", default=None, guard="G1", guard_block=g1_block, guard_paths=["notes.md"],
             end_commit={"sha7": "abc1234", "files": 1, "branch": "main", "paths": [RESUME], "hook_paths": []})
        real_default = g["resolve_default"]
        g["resolve_default"] = broken
        try:
            with in_env(env):
                got = end(r.path, "/feedback", resume=True)
        finally:
            g["resolve_default"] = real_default
        check(got.get("print") == [stop, g1_stopped] and got.get("record") == "found",
              "m_not_finished: end --resume's stop before its push step still repeats the block (%r)" % got)
        r, env = mode_world("m-not-finished-replay")
        seed(env, "/feedback", guard="G2", guard_block="the G2 block")
        got = cli("--specs", r.path, "replay", "--for", "end", "--command", "/feedback", "--branch", "main", env=env)
        check(got.get("_rc") == 0 and got.get("error") and len(got.get("print") or []) == 2
              and got["print"][0].startswith("Specs repo: NOT FINISHED — ") and got["print"][1] == "the G2 block",
              "m_not_finished: replay --for end's stop is followed by the block too (%r)" % got)

        # m_misrooted: §8.1 is never resolved under misrooted, so nothing of the mode runs
        r, env = mode_world("m-misrooted")
        os.makedirs(os.path.join(r.path, "specs"))
        got = cli("--specs", os.path.join(r.path, "specs"), "start", "--command", "/feedback", env=env)
        check(got.get("specs_git") == "misrooted" and got.get("mode") is None and got.get("session_branch") is None
              and len(got.get("print") or []) == 2 and not r.git("for-each-ref", "refs/heads/session"),
              "m_misrooted: no mode, no session branch, no session-branch line (%r)" % got)

        # m_budget_overlay (m9): a catch-up to make and a settle push, at --budget 0, against one call on a copy
        r, env = mode_world("m-budget")
        r.git("switch", "-q", "-c", A, "main")
        r.git("push", "-q", "-u", "origin", A)
        r.write(A_FEED + "f.md", "f\n")
        r.commit_all("NOISSUE f")
        r.git("switch", "-q", "main")
        o_path = FEED + "o.md"
        r.write(o_path, "o\n")
        sb_cli(r, env, "commit", "--branch", S, "--default-ref", "origin/main", "--message", "NOISSUE o")
        other = clone(r, "m-budget-other")
        other.write("notes.md", "n\n")
        other.commit_all("notes")
        other.git("push", "-q", "origin", "main")
        c_bare, c_path = os.path.join(tmp, "m-budget-copy.git"), os.path.join(tmp, "m-budget-copy")
        shutil.copytree(r.bare, c_bare, symlinks=True)
        shutil.copytree(r.path, c_path, symlinks=True)
        copy = Repo(c_path)
        copy.bare = c_bare
        copy.git("remote", "set-url", "origin", c_bare)
        c_env = dict(env, HOME=os.path.join(tmp, "home-m-budget-copy"), CLAUDE_CODE_SESSION_ID="m-budget-copy",
                     SPECS_PATH=c_path)
        os.makedirs(c_env["HOME"])

        def stamp():
            st = os.stat(os.path.join(r.path, o_path))
            return st.st_ino, st.st_mtime_ns

        untouched = stamp()
        calls = [run_start(env, "--budget", "0")]
        check(stamp() == untouched, "m_budget_overlay: the call that stopped before the catch-up lifted nothing")
        states = [overlay(r)]
        while (calls[-1].get("next") or {}).get("run") and len(calls) < 8:
            calls.append(shell(calls[-1]["next"]["run"], env))
            states.append(overlay(r))
        resume0 = " ".join(["python3", shlex.quote(me), "--specs", shlex.quote(r.path), "start", "--command", "/feedback",
                            "--budget", "0", "--started", calls[0].get("started") or "", "--resume"])
        check(len(calls) == 3 and all(c["_rc"] == 0 and c.get("error") is None for c in calls)
              and all(c["next"] == {"run": resume0, "timeout_ms": 600000, "on_timeout": None} for c in calls[:-1])
              and calls[-1].get("next") is None and on_origin(r) == head(r) and on_origin(r, A) == ref(r, A)
              and on_origin(r, S) == ref(r, S),
              "m_budget_overlay: a stop before the catch-up's lift, one before the settle push, then the end (%r)"
              % [c.get("print") for c in calls])
        check(states == [([o_path], True)] * 3,
              "m_budget_overlay: at every call's return no lift stands without its put-back (%r)" % states)
        one = run_start(c_env)
        stitched = [p for c in calls for p in c.get("print") or []]

        def trees(repo):
            return repo.git("for-each-ref", "--format=%(refname) %(tree)", "refs/heads")

        check(one.get("next") is None and [p.replace(c_path, r.path) for p in one.get("print") or []]
              == [p.replace(env_line(r.path), env_line(c_path).replace(c_path, r.path)) for p in stitched]
              and trees(copy) == trees(r) and read(copy, o_path) == read(r, o_path)
              and all(on_origin(copy, b) == on_origin(r, b) for b in ("main", A))
              and (record(c_env, "/feedback") or {}).get("stage") == (record(env, "/feedback") or {}).get("stage") == "done",
              "m_budget_overlay: following next ends as one call would (%r, %r)" % (one.get("print"), stitched))

        # m_no_replay: no replay is handed out in session-branch mode
        r, env = mode_world("m-no-replay")
        r.git("switch", "-q", "-c", A, "main")
        r.git("push", "-q", "-u", "origin", A)
        o = clone(r, "m-no-replay-other")
        o.git("switch", "-q", A)
        o.write(A_FEED + "o.md", "o\n")
        o.commit_all("NOISSUE o")
        o.git("push", "-q", "origin", A)
        r.write(A_FEED + "r.md", "r\n")
        r.commit_all("NOISSUE r")
        r.git("switch", "-q", "main")
        r.git("branch", S, "main")
        got = run_start(env)
        rec = record(env, "/feedback") or {}
        p = r.path
        want = ("Specs preflight: %s — push REJECTED: origin's %s has commits this one lacks, and the run could not take "
                "them in: session-branch mode is on, which replays nothing; run python3 \"%s\" --specs \"%s\" lift --branch "
                "session/ab, then git -C \"%s\" switch %s, git -C \"%s\" pull --rebase --no-autostash origin %s and git -C "
                "\"%s\" push origin %s, then switch back to main, then python3 \"%s\" --specs \"%s\" put-back --branch "
                "session/ab --default-ref origin/main" % (A, A, SB, p, p, A, p, A, p, A, SB, p))
        check(got.get("print") == [env_line(p), want] and got.get("next") is None and rec.get("pending") == []
              and rec.get("stage") == "done" and on_origin(r, A) == head(o),
              "m_no_replay: a settle push rejected in the mode names no replay, its remedy wrapped (%r)" % got)
        r, env = mode_world("m-session-rejected")
        run_start(env)
        o = clone(r, "m-session-rejected-other")
        o.git("config", "workflows.sessionBranch", "true")
        o.write(FEED + "o.md", "o\n")
        sb_cli(o, env, "commit", "--branch", S, "--default-ref", "origin/main", "--message", "NOISSUE o")
        o.git("push", "-q", "origin", S)
        r.write(FEED + "r.md", "r\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        want = ("Specs repo: committed %s (1 file) on session/ab — push REJECTED: origin's session/ab has commits this clone "
                "lacks, pushed from another clone under the same identity; a later run takes them in and pushes" % tip[:7])
        check(got.get("row") == "rejected" and got.get("print") == [want] and got.get("next") is None
              and got.get("pushed") is False and on_origin(r, S) == ref(o, S) and record(env, "/feedback") is None,
              "m_no_replay: end's session push rejected is its own row, no replay named (%r)" % got)
        # m_second_fetch: the next start fetches origin's copy (§8.1), merges it in and pushes, as the row said
        got = run_start(env)
        tip = ref(r, S) or ""
        check(got.get("print") == [env_line(r.path)] and on_origin(r, S) == tip and tip != ref(o, S)
              and subprocess.run(["git", "-C", r.path, "merge-base", "--is-ancestor", ref(o, S), tip]).returncode == 0
              and r.git("rev-parse", "refs/remotes/origin/" + S) == tip,
              "m_second_fetch: origin's session/ab fetched, taken in and pushed (%r)" % got)

        # m_remote_deleted: a session branch origin deleted (its pull request merged) is pushed again (§8.4)
        r, env = mode_world("m-remote-deleted")
        r.write(FEED + "d.md", "d\n")
        run_start(env)
        subprocess.run(["git", "-C", r.bare, "branch", "-q", "-D", S], check=True)
        r.write(FEED + "d2.md", "d2\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        check(got.get("row") == "pushed-session" and got.get("print") == [pushed_session(tip[:7], 1, 2)]
              and on_origin(r, S) == tip, "m_remote_deleted: the push recreates it (%r)" % got)

        # m_include_ahead: commits origin refused left on main go to the session branch, and end names them
        r, env = mode_world("m-include-ahead", on=False)
        r.write(FEED + "s.md", "s\n")
        r.commit_all(SUBJECT)
        refused_at = os.path.join(r.path, ".git", "workflows", "push-refused", "main")
        os.makedirs(os.path.dirname(refused_at))
        with open(refused_at, "w", encoding="utf-8") as fh:
            fh.write("2026-11-01\n")
        main, base = head(r), r.git("rev-parse", "origin/main")
        got = run_start(env)
        tip = ref(r, S) or ""
        want = "Specs preflight: created local session/ab at %s, and committed %s on it" % (base[:7], tip[:7])
        check(got.get("mode") == "on" and got.get("print") == [env_line(r.path), want]
              and r.git("show", "%s:%s" % (tip, FEED + "s.md"), check=False) == "s" and on_origin(r, S) == tip
              and head(r) == main, "m_include_ahead: the flush takes the stranded commit's file (%r)" % got)
        r.write(FEED + "e.md", "e\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        want = (pushed_session(tip[:7], 1, 2) + "; your local main still holds 1 commit(s) origin refused, whose files are "
                "on session/ab now — to drop them, standing on main, run python3 \"%s\" --specs \"%s\" lift --branch "
                "session/ab && git -C \"%s\" reset --keep origin/main && python3 \"%s\" --specs \"%s\" put-back --branch "
                "session/ab --default-ref origin/main" % (SB, r.path, r.path, SB, r.path))
        check(got.get("print") == [want], "m_include_ahead: end's line names the stranded commit (%r)" % got)

        # m_mode_on: a default-branch push origin refused outside the mode turns the mode on, and says so
        mode_on = ("from the next run on, session files go to %s, a branch of your own whose pull request lands them "
                   "(session-branch mode), and these commits' files go there too")
        r, env = mode_world("m-mode-on", on=False)
        hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 1\n")
        r.write(RESUME, "r\n")
        got = end_of(env)
        want = ("Specs repo: committed %s (1 file) on main — push REFUSED by origin (pre-receive hook declined): a rule "
                "there takes no push of main, so this is recorded and no later run pushes it; " % head(r)[:7]
                + mode_on % "session/ab")
        check(got.get("row") == "push-refused" and got.get("print") == [want],
              "m_mode_on: end's refused default branch names the mode it turns on (%r)" % got)
        got = cli("--specs", r.path, "mode", "--default", "main", env=env)
        check(got.get("mode") == "on" and got.get("source") == "refused", "m_mode_on: the record turns it on (%r)" % got)
        r, env = mode_world("m-mode-on-start", initials=None, on=False)
        hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 1\n")
        r.write(RESUME, "r\n")
        got = run_start(env)
        want = ("Specs preflight: main not pushed — origin refused it (pre-receive hook declined), and this is recorded so "
                "no later run pushes it; " + mode_on % "a session branch of your own, once GIT_USER_INITIALS names it")
        check(got.get("print") == [env_line(r.path), want],
              "m_mode_on: the flush's refused default branch, with no identity (%r)" % got)

        # m_skipped (in process): a second unpreserved skips the move, which its step reports as a refused one
        real_lift, real_put_back, puts = sb.lift, sb.put_back, []

        def stuck(root, branch):
            return {"lifted": [], "unpreserved": [FEED + "x.md"]}

        def counted(root, branch, default_ref):
            puts.append(branch)
            return real_put_back(root, branch, default_ref)

        why = "lift found %sx.md not yet on session/ab" % FEED
        r, env = mode_world("m-skipped")
        r.git("branch", S, "main")
        other = clone(r, "m-skipped-other")
        other.write("notes.md", "n\n")
        other.commit_all("notes")
        other.git("push", "-q", "origin", "main")
        h = head(r)
        sb.lift, sb.put_back = stuck, counted
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            sb.lift, sb.put_back = real_lift, real_put_back
        check(got.get("print") == [env_line(r.path), "Specs preflight: could not fast-forward main (%s); the run goes on from "
                                   "it as it stands" % why] and head(r) == h and puts == [S] and got.get("error") is None,
              "m_skipped: the catch-up skipped and reported, nothing put back but the closing put-back (%r, %r)" % (got, puts))
        r, env, w = wrapped_world("m-skipped-b4")
        del puts[:]
        sb.lift, sb.put_back = stuck, counted
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            sb.lift, sb.put_back = real_lift, real_put_back
        stop = ("Specs preflight: stopped early (git switch main: %s) — what it did is above, and the next run's preflight "
                "goes on from where this one stands" % why)
        check(got.get("print") == [env_line(r.path), stop] and got.get("error") == "git switch main: " + why
              and got.get("branch") == B
              and puts == [S], "m_skipped: B4's skipped switch stops the call, the closing put-back run (%r, %r)" % (got, puts))

        # m_canned: the renderer over canned sb.commit results and facts
        base = {"specs": "/s", "default": "main", "default_ref": "origin/main", "session_branch": S, "branch": S}
        sync = {"conflict": ["a.md", "b.md", "c.md"],
                "conflicts": [{"path": "a.md", "source": "origin/main"}, {"path": "c.md", "source": "origin/session/ab"},
                              {"path": "b.md", "source": "origin/main"}]}
        origin_clause = ("; origin's copy of session/ab, pushed from another clone, was not merged in: on c.md one clone "
                         "changed what the other clone's copy still holds unchanged (an entry edited or removed, the header "
                         "edited, the file deleted) — make the two copies agree, by making the same change on the clone that "
                         "still holds it (standing on main there; a pending cost file the other relocated is relocated there "
                         "too, never deleted by hand) or by undoing it on the other; the next run on the clone you changed "
                         "commits it, and once that is pushed, a later run here merges and pushes")
        unsettled = ("; %s and session/ab's version of it each hold a change the other lacks, so it was left out of this "
                     "commit and is as it was in your working tree — git -C \"/s\" show session/ab:%s shows the branch's "
                     "version")
        want = ("; this run created local session/ab at 1234567"
                "; merging main into session/ab left a.md, b.md unsettled — settle them in its pull request"
                + origin_clause
                + unsettled % ("x.md", "x.md") + unsettled % ("y.md", "y.md")
                + "; once a copy left out is the branch's version with your own entries added after it, in the line "
                  "endings your checkout gives the file, the next run commits it, and an edit or removal of an entry the "
                  "branch your specs checkout stands on holds can then be made again; until then lift will not discard it, "
                  "so each move of the specs checkout is skipped"
                + "; your local main still holds 2 commit(s) origin refused, whose files are on session/ab now — to drop "
                  "them, standing on main, run python3 \"%s\" --specs \"/s\" lift --branch session/ab && git -C \"/s\" "
                  "reset --keep origin/main && python3 \"%s\" --specs \"/s\" put-back --branch session/ab --default-ref "
                  "origin/main" % (SB, SB))
        got = _appends(lines, dict(base, created="1234567", sync=sync, unsettled=["x.md", "y.md"], stranded=2))
        check(got == want, "m_canned: created, sync.conflict from each source, unsettled and stranded, in §6's order (%r)" % got)
        got = _appends(lines, dict(base, sync={"error": "merge-tree: boom"}))
        check(got == "; the merge of main into session/ab could not run (merge-tree: boom), and the next run tries again",
              "m_canned: sync.error (%r)" % got)
        got = _appends(lines, dict(base, session_branch=None, branch="main", mode="unsupported", created="1234567"))
        check(got == ("; session-branch mode is on for this clone, but this git's merge-tree cannot merge without a "
                      "checkout (it needs --write-tree and -X), so these files stay on main until git is upgraded"),
              "m_canned: unsupported, and no created clause without a session branch (%r)" % got)
        row = dict(base, sha7="abc1234", files=2)
        rejected = ("Specs repo: committed abc1234 (2 files) on session/ab — push REJECTED: origin's session/ab has commits "
                    "this clone lacks, pushed from another clone under the same identity")
        got = [_row_line(lines, "rejected", dict(row, sync=s)) for s in (None, {"conflicts": sync["conflicts"][:1]}, sync)]
        check(got == [rejected + "; a later run takes them in and pushes"] * 2
              + [rejected + ", which a later run takes in only once the two clones' copies agree, as this line says"],
              "m_canned: the session branch's push-rejected row, with its conflict ending where origin's copy was not "
              "merged (%r)" % got)
        check(lines.preflight_form(_row_line(lines, "rejected", dict(row, sha7="-", files=0))).startswith(
            "Specs preflight: session/ab — push REJECTED: "), "m_canned: its Specs preflight: form")
        rec_s = "/s/.git/workflows/push-refused/session/ab"
        key_s = "branch.session/ab.workflowsPushRefused"
        refused = ("Specs repo: committed abc1234 (2 files) on session/ab — push REFUSED by origin (hook declined): a rule "
                   "there takes no push of session/ab, so this is recorded and no later run pushes it; once origin takes "
                   "pushes to session/ab, ")
        before = ("Specs repo: committed abc1234 (2 files) on session/ab — not pushed: origin refused pushes to session/ab "
                  "on 2026-11-01 (%s), and every commit since stays on local session/ab; once origin takes pushes to "
                  "session/ab, ")
        for name, facts, want in (
                ("push refused, file", dict(row, reason="hook declined", record=rec_s, record_kind="file"),
                 refused + "rm \"%s\"" % rec_s),
                ("push refused, config key", dict(row, reason="hook declined", record=key_s, record_kind="config"),
                 refused + "git -C \"/s\" config --unset " + key_s),
                ("refused before, file", dict(row, date="2026-11-01", record=rec_s, record_kind="file"),
                 before % rec_s + "rm \"%s\"" % rec_s),
                ("refused before, config key", dict(row, date="2026-11-01", record=key_s, record_kind="config"),
                 before % key_s + "git -C \"/s\" config --unset " + key_s)):
            got = _row_line(lines, "refused-before" if "before" in name else "push-refused", facts)
            check(got == want, "m_canned: the session branch's refused remedy, %s (%r)" % (name, got))
        on_main = {"sha7": "abc1234", "files": 2, "branch": "main", "default": "main", "specs": "/s",
                   "reason": "hook declined", "record": "/r", "record_kind": "file", "mode_on": True}
        main_refused = ("Specs repo: committed abc1234 (2 files) on main — push REFUSED by origin (hook declined): a rule "
                        "there takes no push of main, so this is recorded and no later run pushes it; ")
        for identity, named in (("ab", "session/ab"), (None, "a session branch of your own, once GIT_USER_INITIALS names it")):
            for kind, record_ in (("file", "/r"), ("config", "branch.main.workflowsPushRefused")):
                got = _row_line(lines, "push-refused", dict(on_main, identity=identity, record=record_, record_kind=kind))
                check(got == main_refused + mode_on % named,
                      "m_canned: app.mode-on, identity %r, a %s record (%r)" % (identity, kind, got))
        got = _row_line(lines, "push-refused", dict(on_main, record=None, record_kind=None, record_error="e", identity="ab"))
        check(got == ("Specs repo: committed abc1234 (2 files) on main — push REFUSED by origin (hook declined): a rule "
                      "there takes no push of main, but this could not be recorded (e, the configuration write's), so a "
                      "later run pushes main again"), "m_canned: an unrecorded refusal turns nothing on (%r)" % got)
        p_ = {"reason": "hook declined", "recorded": "file", "record": "/r", "record_error": None}
        got = [_refused_line(lines, "/s", "main", "main", p_, {"mode_on": True, "identity": "ab"}),
               _refused_line(lines, "/s", S, "main", dict(p_, record=rec_s), {"session_branch": S})]
        check(got == ["Specs preflight: main not pushed — origin refused it (hook declined), and this is recorded so no "
                      "later run pushes it; " + mode_on % "session/ab",
                      "Specs preflight: session/ab not pushed — origin refused it (hook declined), and this is recorded so "
                      "no later run pushes it; once origin takes pushes to session/ab, rm \"%s\"" % rec_s],
              "m_canned: the Specs preflight: refused forms take the same remedies (%r)" % got)
        moved = {"moved": True, "pushed": False, "attempts": 1, "replayed": ["a" * 40], "dropped": [], "tip": "b" * 40,
                 "porcelain": None, "moves": [], "upstream_error": None, "refused": None}
        got = _replay_line(lines, {"row": "moved", "why": "refused", "reason": None}, moved,
                           dict(on_main, standing="main", register_rebuild=False, error=None, preflight=False,
                                identity="ab"))
        check(got == ("Specs repo: committed bbbbbbb (2 files) on main — origin's main had moved on, so the run replayed "
                      "its 1 commit(s) onto it and moved main there, but push REFUSED by origin (hook declined): a rule "
                      "there takes no push of main, so this is recorded and no later run pushes it; " + mode_on % "session/ab"),
              "m_canned: the replay's refused form on the default branch says the mode turns on (%r)" % got)
        got = _row_line(lines, "pushed-session", dict(row, files=1, F=3))
        check(got == pushed_session("abc1234", 1, 3), "m_canned: pushed-session (%r)" % got)
        bp = ("Specs repo: committed abc1234 (2 files) on session/ab — not pushed: its pull request would also change "
              "specifications/PRD-A-1-x/prd.md, which is not one of this plugin's session files%s; push session/ab once that "
              "change is ready to go, and the artifacts go with it")
        failed = {"sha": "c" * 40, "reason": "branch-path", "path": "specifications/PRD-A-1-x/prd.md"}
        got = [_row_line(lines, "scope", dict(row, scope={"failed": failed}, subject="NOISSUE Merge main into session/ab")),
               _row_line(lines, "scope", dict(row, scope={"failed": dict(failed, sha=None)}, subject=None))]
        check(got == [bp % ", and the branch's newest merge commit is ccccccc NOISSUE Merge main into session/ab", bp % ""],
              "m_canned: push-scope's branch-path form, with a merge commit and with none (%r)" % got)
        got = [_session_rejected_preflight(lines, S, "main", s) for s in (None, {"conflicts": sync["conflicts"][:1]}, sync)]
        plain = ("Specs preflight: session/ab — push REJECTED: origin's session/ab has commits this clone lacks, pushed from "
                 "another clone under the same identity")
        check(got == [plain + "; a later run takes them in and pushes"] * 2
              + [plain + ", which a later run takes in only once the two clones' copies agree, as this line says" + origin_clause],
              "m_canned: the flush's session rejection, its conflict ending followed by the clause it points at (%r)" % got)

    def scenarios_state(tmp):
        state = _load_module("specs_git_state")
        home = os.path.join(tmp, "home")
        os.makedirs(home)
        keep = {k: os.environ.get(k) for k in ("HOME", "CLAUDE_CODE_SESSION_ID")}

        def env(session="s1"):
            os.environ["HOME"] = home
            if session is None:
                os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
            else:
                os.environ["CLAUDE_CODE_SESSION_ID"] = session
            return {"HOME": home, "CLAUDE_CODE_SESSION_ID": session} if session else {"HOME": home}

        def raises(exc, fn, *args, **kw):
            try:
                fn(*args, **kw)
            except exc:
                return True
            except Exception:
                return False
            return False

        def tree(base):
            return sorted(os.path.relpath(os.path.join(d, f), base) for d, _, fs in os.walk(base) for f in fs)

        def clean_env(session):
            e = dict(os.environ)
            e["HOME"] = home
            e.pop("CLAUDE_CODE_SESSION_ID", None)
            if session:
                e["CLAUDE_CODE_SESSION_ID"] = session
            return e

        try:
            # s_session_id
            os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
            check(raises(state.NoSession, state.session_id), "s_session_id: unset raises NoSession")
            for bad in ("", "../x", "-x", "a b"):
                os.environ["CLAUDE_CODE_SESSION_ID"] = bad
                check(raises(state.NoSession, state.session_id), "s_session_id: %r raises NoSession" % bad)
            os.environ["CLAUDE_CODE_SESSION_ID"] = "abc\n"
            check(raises(state.NoSession, state.session_id), "s_session_id: a trailing newline raises NoSession")
            os.environ["CLAUDE_CODE_SESSION_ID"] = "ab-12_x.y"
            check(state.session_id() == "ab-12_x.y", "s_session_id: a good id is returned")

            # s_path
            env()
            want = os.path.join(home, ".claude", "dev-workflows", "specs-git", "s1", "create-ard.json")
            check(state.path("s1", "/create-ard") == want, "s_path: the record's home (%r)" % state.path("s1", "/create-ard"))
            check(raises(ValueError, state.path, "s1", "create-ard"), "s_path: a command without its slash is a ValueError")
            check(raises(ValueError, state.path, "s1", "/idea\n"), "s_path: a trailing newline is a ValueError")
            check(raises(ValueError, state.path, "s1", "/Create"), "s_path: an upper-case command is a ValueError")

            # s_roundtrip
            env()
            rec = state.new("/create-ard", started_by_script=False, specs="/x/specs")
            rec["declined"] = ["specifications/PRD-A-1 x/prd.md", "specifikationen/zahlungsauslösung.md"]
            state.save("s1", "/create-ard", rec)
            got = state.load("s1", "/create-ard")
            check(got == rec and got["updated"] and got["started"], "s_roundtrip: save then load returns the record (%r)" % got)
            check(state.FIELDS["declined"] == [] and got["version"] == 1, "s_roundtrip: FIELDS is not mutated by new()")
            check(os.listdir(os.path.join(home, ".claude", "dev-workflows", "specs-git", "s1")) == ["create-ard.json"],
                  "s_roundtrip: no file but create-ard.json is left")
            before = open(state.path("s1", "/create-ard"), encoding="utf-8").read()
            bad = dict(rec, bogus=1)
            check(raises(ValueError, state.save, "s1", "/create-ard", bad)
                  and open(state.path("s1", "/create-ard"), encoding="utf-8").read() == before,
                  "s_roundtrip: an unknown key raises before the file changes")
            check(raises(ValueError, state.new, "/create-ard", bogus=1), "s_roundtrip: new() refuses an unknown key")
            check(oct(os.stat(os.path.dirname(state.path("s1", "/create-ard"))).st_mode & 0o777) == "0o700",
                  "s_roundtrip: the session directory is private")

            # s_unparsable
            with open(state.path("s1", "/create-ard"), "w", encoding="utf-8") as fh:
                fh.write("{")
            check(state.load("s1", "/create-ard") is None, "s_unparsable: a file holding { loads as None")
            with open(state.path("s1", "/create-ard"), "w", encoding="utf-8") as fh:
                json.dump(dict(rec, version=2), fh)
            check(state.load("s1", "/create-ard") is None, "s_unparsable: another version loads as None")

            # s_fields: the stay with its kind, the run's snapshot, the open run and protects; merged_stay no field
            check({"stay", "start_dirty", "midrun", "protects"} <= set(state.FIELDS)
                  and "merged_stay" not in state.FIELDS and state.FIELDS.get("stay", 0) is None
                  and state.FIELDS.get("start_dirty", 0) is None and state.FIELDS.get("midrun", 0) is None
                  and state.FIELDS.get("protects") is True,
                  "s_fields: stay, start_dirty, midrun null and protects true in FIELDS, merged_stay not (%r)"
                  % sorted(state.FIELDS))

            # s_legacy_merged_stay: a record an earlier version wrote, holding merged_stay, loads with it as a stay of
            # kind and flag merged, every new field defaulted, and saves; one whose merged_stay is null, and one holding
            # none of those fields, load with each new field at its default, stay null and present
            NEW = ("stay", "start_dirty", "midrun", "protects")
            want = {"branch": "prd/A-1-x", "kind": "merged", "reason": "g1", "merged": True, "command": None}
            for case, extra, stay in (("merged_stay set", {"merged_stay": {"branch": "prd/A-1-x", "reason": "g1"}},
                                       want),
                                      ("merged_stay null", {"merged_stay": None}, None),
                                      ("no new field", {}, None)):
                legacy = {k: v for k, v in state.new("/specify", specs="/x/specs").items() if k not in NEW}
                legacy.update(extra)
                with open(state.path("s1", "/specify"), "w", encoding="utf-8") as fh:
                    json.dump(legacy, fh)
                got = state.load("s1", "/specify") or {}
                check(all(k in got for k in NEW) and got.get("stay") == stay and got.get("start_dirty") is None
                      and got.get("midrun") is None and got.get("protects") is True and "merged_stay" not in got
                      and got.get("specs") == "/x/specs",
                      "s_legacy_merged_stay: %s loads with stay %r and every new field at its default (%r)"
                      % (case, stay, got))
                check(not raises(Exception, state.save, "s1", "/specify", got)
                      and (state.load("s1", "/specify") or {}).get("stay") == stay,
                      "s_legacy_merged_stay: %s, the loaded record saves (%r)" % (case, state.load("s1", "/specify")))
            state.remove("s1", "/specify")

            # s_keys
            for sess, cmd in (("s1", "/specify"), ("s1", "/feedback"), ("s2", "/specify")):
                state.save(sess, cmd, state.new(cmd, session=sess, specs="%s%s" % (sess, cmd)))
            check(all(state.load(sess, cmd)["specs"] == "%s%s" % (sess, cmd)
                      for sess, cmd in (("s1", "/specify"), ("s1", "/feedback"), ("s2", "/specify"))),
                  "s_keys: each (session, command) loads back its own")

            # s_remove
            check(state.remove("s2", "/specify") is True and state.remove("s2", "/specify") is False,
                  "s_remove: True, then False")
            check(state.load("s2", "/specify") is None and not os.path.exists(os.path.dirname(state.path("s2", "/specify"))),
                  "s_remove: load then None, and s2/ is gone with its last record")
            check(os.path.isdir(os.path.dirname(state.path("s1", "/specify"))), "s_remove: s1/ stays while it holds records")

            # s_prune
            def touch(sess, cmd, days):
                state.save(sess, cmd, state.new(cmd, session=sess))
                t = time.time() - days * 86400
                os.utime(state.path(sess, cmd), (t, t))

            touch("old", "/specify", 8)
            touch("young", "/specify", 6)
            touch("cur", "/specify", 8)
            gone = state.prune("cur")
            check(gone == [state.path("old", "/specify")] and not os.path.exists(os.path.dirname(gone[0])),
                  "s_prune: an 8-day-old record in another session goes with its directory (%r)" % gone)
            check(os.path.exists(state.path("young", "/specify")) and os.path.exists(state.path("cur", "/specify")),
                  "s_prune: a 6-day-old record and the current session's own stay")

            # s_resumable
            rec = state.new("/specify", stage="settle", args={"keys": ["A-1"]})
            rec["updated"] = state._now()
            check(state.resumable(rec, {"keys": ["A-1"]}) is True, "s_resumable: a fresh record at settle with the same args")
            check(state.resumable(dict(rec, stage="done"), {"keys": ["A-1"]}) is False, "s_resumable: stage done")
            check(state.resumable(rec, {"keys": ["A-2"]}) is False, "s_resumable: other args")
            old = time.strftime(state.STAMP, time.gmtime(time.time() - 20 * 60))
            check(state.resumable(dict(rec, updated=old), {"keys": ["A-1"]}) is False, "s_resumable: twenty minutes old")
            check(state.resumable(dict(rec, updated=""), {"keys": ["A-1"]}) is False, "s_resumable: no timestamp")
            check(state.resumable(dict(rec, updated=None), {"keys": ["A-1"]}) is False, "s_resumable: a null timestamp")
            check(state.saved_within(rec) is True and state.saved_within(dict(rec, updated=old)) is False
                  and state.saved_within(dict(rec, updated=old), minutes=30) is True
                  and state.saved_within(dict(rec, updated=None)) is False and state.saved_within({}) is False,
                  "s_resumable: saved_within is the 15-minute window resumable applies")

            # s_declined_cli
            shutil.rmtree(os.path.join(home, ".claude"))
            first = "specifications/PRD-A-1 x/prd.md"
            got = cli("declined", "--command", "/create-ard", "--path", first, "--path", "a.md", env=clean_env("s1"))
            rec = state.load("s1", "/create-ard")
            check(got["_rc"] == 0 and got.get("record") == "created" and got.get("recorded") == [first, "a.md"]
                  and rec and rec["declined"] == [first, "a.md"] and rec["started_by_script"] is False,
                  "s_declined_cli: no record yet creates one (%r)" % got)
            got = cli("declined", "--command", "/create-ard", "--path", "a.md", "--path", "b.md", env=clean_env("s1"))
            rec = state.load("s1", "/create-ard")
            check(got.get("record") == "found" and got.get("recorded") == ["a.md", "b.md"]
                  and rec["declined"] == [first, "a.md", "b.md"],
                  "s_declined_cli: a second call adds b.md only (%r)" % got)
            snapshot = open(state.path("s1", "/create-ard"), encoding="utf-8").read()
            got = cli("declined", "--command", "/idea", "--path", "z.md", env=clean_env("s1"))
            check(got["_rc"] == 0 and open(state.path("s1", "/create-ard"), encoding="utf-8").read() == snapshot
                  and state.load("s1", "/idea")["declined"] == ["z.md"],
                  "s_declined_cli: another command's call leaves /create-ard's record unchanged (%r)" % got)

            # s_declined_no_session
            shutil.rmtree(os.path.join(home, ".claude"))
            env(None)
            got = cli("declined", "--command", "/idea", "--path", "a.md", env={"HOME": home})
            env()
            check(one_not_run_line(got) and not os.path.exists(os.path.join(home, ".claude")),
                  "s_declined_no_session: exit 2, one line, nothing written (%r)" % got)

            # s_usage_prefix
            got = cli("declined", "--path", "a.md", env=clean_env("s1"))
            check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: "),
                  "s_usage_prefix: a usage error says usage (%r)" % got)
            got = cli("declined", "--command", "/idea", env=clean_env("s1"))
            check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: ")
                  and not os.path.exists(state.path("s1", "/idea")),
                  "s_usage_prefix: no --path is a usage error, nothing written (%r)" % got)
            got = cli("declined", "--command", "idea", "--path", "a.md", env=clean_env("s1"))
            check(one_not_run_line(got), "s_usage_prefix: a command without its slash exits 2 with one line (%r)" % got)

            # s_outside_repo
            r = new_repo(tmp, "state-outside")
            r.write("dirty.md", "x\n")
            before = r.git("status", "--porcelain")
            got = cli("declined", "--command", "/idea", "--path", "a.md", env=clean_env("s1"), cwd=r.path)
            check(got["_rc"] == 0 and r.git("status", "--porcelain") == before,
                  "s_outside_repo: declined from inside a repository leaves its status unchanged (%r)" % got)

            def case(name, fn):  # one case that crashes must not hide the others
                try:
                    fn()
                except Exception as e:
                    check(False, "%s crashed: %s: %s" % (name, type(e).__name__, str(e).strip()[:300]))

            def opened(started, session="s7"):
                rec = state.new("/specify", session=session)
                rec["started"] = started
                state.save(session, "/specify", rec)
                return rec

            # s_save_at: save, load and remove each take a record file of their own (at), <name>.json untouched
            def s_save_at():
                env()
                main_rec = state.new("/specify", session="s5")
                state.save("s5", "/specify", main_rec)
                main_path = state.path("s5", "/specify")
                before = open(main_path, "rb").read()
                at = os.path.join(os.path.dirname(main_path), "specify.20261110T100000Z.json")
                parked = state.new("/specify", session="s5", parked=True)
                parked["started"] = "2026-11-10T10:00:00Z"
                state.save("s5", "/specify", parked, at=at)
                check(state.load("s5", "/specify", at=at) == parked and open(main_path, "rb").read() == before
                      and state.load("s5", "/specify") == main_rec,
                      "s_save_at: save(at=) writes that file and load(at=) reads it, <name>.json untouched")
                check(state.remove("s5", "/specify", at=at) is True and not os.path.exists(at)
                      and open(main_path, "rb").read() == before and state.remove("s5", "/specify", at=at) is False,
                      "s_save_at: remove(at=) removes that file alone, then False")

            case("s_save_at", s_save_at)

            # s_others: every record of the session's directory not of this command, by its file's name -- parked
            # ones of other commands included -- oldest started first; a temporary file, another name, one that cannot
            # be read and one another version wrote are left out; mine() lists the command's own
            def s_others():
                env()
                sdir = os.path.dirname(state.path("s6", "/specify"))

                def put(command, started, name=None, **f):
                    rec = state.new(command, session="s6", **f)
                    rec["started"] = started
                    state.save("s6", command, rec, at=None if name is None else os.path.join(sdir, name))
                    return rec

                put("/specify", "2026-11-10T10:00:02Z")
                put("/specify", "2026-11-10T10:00:01Z", "specify.20261110T100001Z.json", parked=True)
                put("/feedback", "2026-11-10T10:00:03Z")
                put("/create-ard", "2026-11-10T10:00:00Z", "create-ard.20261110T100000Z.json", parked=True)
                for name, body in ((".tmp-x.json", "{}"), ("notes.txt", "x"), ("bad.json", "{"),
                                   ("old.json", json.dumps({"version": 0, "command": "/old", "started": "2026-11-10T09:00:00Z"}))):
                    with open(os.path.join(sdir, name), "w", encoding="utf-8") as fh:
                        fh.write(body)
                got = [(rec["command"], rec["started"]) for rec in state.others("s6", "/specify")]
                check(got == [("/create-ard", "2026-11-10T10:00:00Z"), ("/feedback", "2026-11-10T10:00:03Z")],
                      "s_others: the other commands' records, a parked one among them, oldest first (%r)" % got)
                got = [os.path.basename(f) for f, _rec in state.mine("s6", "/specify")]
                check(got == ["specify.20261110T100001Z.json", "specify.json"],
                      "s_others: mine() lists the command's own, parked and not, oldest first (%r)" % got)

            case("s_others", s_others)

            # s_park_unpark: park moves <name>.json aside under its started stamp, marked parked, its updated kept --
            # -2 where the name is taken; unpark restores the newest parked one with protects false where keep holds,
            # drops it otherwise, and never takes a record not marked parked (N3)
            def s_park_unpark():
                env()
                sdir = os.path.dirname(state.path("s7", "/specify"))

                a = opened("2026-11-10T10:00:01Z")
                pa = state.park("s7", "/specify")
                got = state.load("s7", "/specify", at=pa) or {}
                check(pa == os.path.join(sdir, "specify.20261110T100001Z.json") and not os.path.exists(state.path("s7", "/specify"))
                      and got.get("parked") is True and got.get("protects") is False and got.get("updated") == a["updated"]
                      and got.get("started") == a["started"],
                      "s_park_unpark: parked under its stamp, marked parked and protects false, updated kept (%r, %r)"
                      % (pa, got))
                opened("2026-11-10T10:00:02Z")
                state.park("s7", "/specify")
                opened("2026-11-10T10:00:03Z")
                state.park("s7", "/specify")
                check(state.park("s7", "/specify") is None, "s_park_unpark: nothing at <name>.json parks nothing")
                derived = state.new("/specify", session="s7", started_by_script=False)
                derived["started"] = "2026-11-10T10:00:09Z"
                dpath = os.path.join(sdir, "specify.20261110T100009Z.json")
                state.save("s7", "/specify", derived, at=dpath)
                dbytes = open(dpath, "rb").read()
                seen = []
                got1 = state.unpark("s7", "/specify", lambda rec: seen.append(rec["started"]) or True)
                restored = state.load("s7", "/specify") or {}
                check(got1 == "restored" and seen == ["2026-11-10T10:00:03Z"] and restored.get("started") == "2026-11-10T10:00:03Z"
                      and restored.get("protects") is False and restored.get("parked") is False
                      and not os.path.exists(os.path.join(sdir, "specify.20261110T100003Z.json")),
                      "s_park_unpark: the newest parked one restored, protects false (%r, %r)" % (got1, restored))
                state.remove("s7", "/specify")
                got2 = state.unpark("s7", "/specify", lambda rec: False)
                check(got2 == "dropped" and state.load("s7", "/specify") is None
                      and not os.path.exists(os.path.join(sdir, "specify.20261110T100002Z.json")),
                      "s_park_unpark: where keep fails, the newest is dropped, nothing restored (%r)" % got2)
                got3 = state.unpark("s7", "/specify", lambda rec: True)
                got4 = state.unpark("s7", "/specify", lambda rec: True)
                check(got3 == "restored" and (state.load("s7", "/specify") or {}).get("started") == "2026-11-10T10:00:01Z"
                      and got4 is None and open(dpath, "rb").read() == dbytes,
                      "s_park_unpark: three parks unpark newest first, and a record not marked parked is never taken "
                      "(%r, %r)" % (got3, got4))
                opened("2026-11-10T10:00:05Z", "s7b")
                first = state.park("s7b", "/specify")
                opened("2026-11-10T10:00:05Z", "s7b")
                second = state.park("s7b", "/specify")
                check(first.endswith("specify.20261110T100005Z.json") and second.endswith("specify.20261110T100005Z-2.json"),
                      "s_park_unpark: a taken name takes -2 before .json (%r, %r)" % (first, second))

            case("s_park_unpark", s_park_unpark)

            # s_find: <name>.json where its started is the stamp; else <name>.<stamp>.json by name; else that derived
            # path with None -- never <name>.json for another run
            def s_find():
                env()
                sdir = os.path.dirname(state.path("s8", "/specify"))
                main_rec = opened("2026-11-10T11:00:00Z", "s8")
                p2 = os.path.join(sdir, "specify.20261110T100000Z.json")
                other = state.new("/specify", session="s8", parked=True)
                other["started"] = "2026-11-10T10:00:00Z"
                state.save("s8", "/specify", other, at=p2)
                got = [state.find("s8", "/specify", "2026-11-10T11:00:00Z"), state.find("s8", "/specify", "2026-11-10T10:00:00Z"),
                       state.find("s8", "/specify", "2026-11-10T09:00:00Z")]
                check(got == [(state.path("s8", "/specify"), main_rec), (p2, other),
                              (os.path.join(sdir, "specify.20261110T090000Z.json"), None)],
                      "s_find: the main record by its started, a parked one by name, else the derived path (%r)" % (got,))
                check(raises(ValueError, state.find, "s8", "/specify", "yesterday"), "s_find: a bad stamp is a ValueError")

            case("s_find", s_find)

            # s_find_before: any stamp a run's starts returned names its record -- its started, or one its
            # started_before lists -- the newest started where two list it; never another run's <name>.json
            def s_find_before():
                env()
                sdir = os.path.dirname(state.path("s9", "/specify"))

                def put(started, before, name=None, **f):
                    rec = state.new("/specify", session="s9", started_before=list(before), **f)
                    rec["started"] = started
                    at = None if name is None else os.path.join(sdir, name)
                    state.save("s9", "/specify", rec, at=at)
                    return at or state.path("s9", "/specify"), rec

                main = put("2026-11-10T12:00:00Z", ["2026-11-10T11:00:00Z"])
                n1 = put("2026-11-10T10:30:00Z", ["2026-11-10T10:00:00Z"], "specify.20261110T103000Z.json", parked=True)
                n2 = put("2026-11-10T10:40:00Z", ["2026-11-10T10:00:00Z"], "specify.20261110T104000Z.json", parked=True)
                got = [state.find("s9", "/specify", s) for s in ("2026-11-10T11:00:00Z", "2026-11-10T12:00:00Z",
                                                                 "2026-11-10T10:00:00Z", "2026-11-10T10:30:00Z")]
                check(got == [main, main, n2, n1],
                      "s_find_before: <name>.json by a stamp its started_before lists, the newest of two listing one, "
                      "a parked one by its started (%r)" % ([g[0] for g in got],))
                put("2026-11-10T13:00:00Z", [])  # another run's <name>.json, listing no stamp
                got = state.find("s9", "/specify", "2026-11-10T11:00:00Z")
                check(got == (os.path.join(sdir, "specify.20261110T110000Z.json"), None),
                      "s_find_before: another run's <name>.json is never named (%r)" % (got,))

            case("s_find_before", s_find_before)

            # s_left_behind: a re-run cut off between its save and its removal of the parked file it re-ran from leaves
            # that file behind; no reader lists it -- mine, others, unpark, find -- and the save or the removal of the
            # record that lists its started removes it
            def s_left_behind():
                env()
                sdir = os.path.dirname(state.path("s10", "/specify"))
                x, y = "2026-11-10T10:00:00Z", "2026-11-10T10:05:00Z"
                p_path = os.path.join(sdir, "specify.20261110T100000Z.json")
                n_path = os.path.join(sdir, "specify.20261110T100500Z.json")

                def lay():  # both files as the cut-off leaves them, written with no save's clean-up
                    p = state.new("/specify", session="s10", parked=True, protects=False)
                    n = state.new("/specify", session="s10", parked=True, protects=False, started_before=[x])
                    state._write(p_path, dict(p, started=x, updated=x))
                    state._write(n_path, dict(n, started=y, updated=y))
                    return dict(n, started=y)

                lay()
                mine = [os.path.basename(f) for f, _rec in state.mine("s10", "/specify")]
                others = [rec["started"] for rec in state.others("s10", "/feedback")]
                check(mine == ["specify.20261110T100500Z.json"] and others == [y]
                      and state.find("s10", "/specify", x)[0] == n_path,
                      "s_left_behind: the file left behind is listed by neither mine nor others, and its stamp names "
                      "the re-run's record (%r, %r)" % (mine, others))
                first = state.unpark("s10", "/specify", lambda rec: True)
                second = state.unpark("s10", "/specify", lambda rec: True)
                check(first == "restored" and (state.load("s10", "/specify") or {}).get("started") == y
                      and second is None and os.path.exists(p_path),
                      "s_left_behind: unpark restores the re-run's record, never the file it left behind (%r, %r)"
                      % (first, second))
                state.remove("s10", "/specify")
                check(not os.path.exists(p_path) and not os.path.exists(state.path("s10", "/specify")),
                      "s_left_behind: removing the record that lists it removes the file left behind (%r)"
                      % (os.listdir(sdir) if os.path.isdir(sdir) else None))
                n = lay()
                state.save("s10", "/specify", n, at=n_path)
                check(not os.path.exists(p_path) and os.path.exists(n_path),
                      "s_left_behind: the next save of the record that lists it removes the file left behind")
                state.remove("s10", "/specify", at=n_path)
                # another run's record saved over the one that lists the stamp takes the file left behind with it --
                # one whose started falls in the same second, which no stamp tells apart, among them -- and never a
                # third run's live record: a parked one, and the record it writes
                lay()
                state.unpark("s10", "/specify", lambda rec: True)  # the re-run's record to <name>.json, no clean-up
                d_path = os.path.join(sdir, "specify.20261110T100700Z.json")
                d = state.new("/specify", session="s10", parked=True, protects=False)
                state._write(d_path, dict(d, started="2026-11-10T10:07:00Z", updated="2026-11-10T10:07:00Z"))
                c = state.new("/specify", session="s10")
                c["started"] = y
                state.save("s10", "/specify", c)
                check(not os.path.exists(p_path) and os.path.exists(d_path)
                      and (state.load("s10", "/specify") or {}).get("started_before") == [],
                      "s_left_behind: a save of another run's record over the one that lists it removes the file left "
                      "behind, a third run's parked record and its own kept (%r)" % sorted(os.listdir(sdir)))
                state.remove("s10", "/specify")
                state.remove("s10", "/specify", at=d_path)

            case("s_left_behind", s_left_behind)

            # s_lazy_import
            lone = os.path.join(tmp, "lazy")
            os.makedirs(lone)
            shutil.copy(me, os.path.join(lone, "specs-git.py"))
            shutil.copy(os.path.join(HERE, "session-branch.py"), os.path.join(lone, "session-branch.py"))
            got = cli("--specs", r.path, "status", script=os.path.join(lone, "specs-git.py"), env=clean_env("s1"))
            check(got["_rc"] == 0 and "artifact" in got, "s_lazy_import: status runs without the new modules (%r)" % got)
            got = cli("declined", "--command", "/idea", "--path", "a.md", script=os.path.join(lone, "specs-git.py"),
                      env=clean_env("s1"))
            check(one_not_run_line(got) and "specs_git_state" in got["_err"],
                  "s_lazy_import: declined without its module exits 2 with one line (%r)" % got)
            shutil.copy(os.path.join(HERE, "specs_git_state.py"), os.path.join(lone, "specs_git_state.py"))
            got = cli("--specs", r.path, "status", script=os.path.join(lone, "specs-git.py"), env=clean_env("s1"))
            check(got["_rc"] == 0 and "artifact" in got, "s_lazy_import: status runs without the lines module (%r)" % got)
            got = cli("declined", "--command", "/idea", "--path", "a.md", script=os.path.join(lone, "specs-git.py"),
                      env=clean_env("s1"))
            check(one_not_run_line(got) and "specs_git_lines" in got["_err"],
                  "s_lazy_import: declined without the lines module exits 2 with one line naming it (%r)" % got)
        finally:
            for k, v in keep.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def scenarios_lines(tmp):
        _, lines = _flow()
        T = lines.T
        with open(SPECS_REPO_GIT, encoding="utf-8") as fh:
            srg = fh.read()
        with open(ADDRESSING, encoding="utf-8") as fh:
            addressing = fh.read()
        with open(SESSION_HYGIENE, encoding="utf-8") as fh:
            hygiene = fh.read()

        span = lines.placeholder

        def raises_naming(name, fn, *args):
            try:
                fn(*args)
            except ValueError as e:
                return name in str(e)
            return False

        # l_pins
        got = lines.pins(srg, addressing, hygiene)
        check(got == [], "l_pins: every template is found in its source (%r)" % got)

        # l_pins_bite
        row = "Specs repo: no session artifacts to commit"
        got = lines.pins(srg.replace(row, "Specs repo: no session artefacts to commit"), addressing, hygiene)
        check(srg.count(row) == 1 and len(got) == 1 and got[0].startswith("row.nothing:"),
              "l_pins_bite: one word of the Nothing to commit row changed fails row.nothing alone (%r)" % got)
        got = lines.pins(srg.replace("could not delete merged", "could not remove merged"), addressing, hygiene)
        check(len(got) == 1 and got[0].startswith("pre.delete-failed:"),
              "l_pins_bite: a word of a wording Task 3 wrote fails its template (%r)" % got)
        blocks = lines.section5_blocks(srg)
        got = lines.pins(srg.replace(blocks[1], blocks[1].replace("          artifact area:", "         artifact area:")),
                         addressing, hygiene)
        check(len(got) == 1 and got[0].startswith("g1:"), "l_pins_bite: a §5 block is compared line for line (%r)" % got)
        got = lines.pins(srg, addressing.replace("the plugin moves nothing.]`", "the plugin moves nothing at all.]`"), hygiene)
        check(got and all(f.startswith(("root.left-behind:", "root.left-behind.close:")) for f in got),
              "l_pins_bite: an addressing §3 template is pinned to addressing.md (%r)" % got)

        # l_pins_all: pins() skips no template: every one but the three blocks is found in its source, the landing's
        # rows among them, and one gone from SRG is reported
        got = lines.pins(srg, addressing, hygiene)
        check(got == [], "l_pins_all: every template is found in its source (%r)" % got)
        there = T.get("row.there", "")
        moved = srg.replace(there, there.replace("nothing to commit", "nothing to land"))
        got = lines.pins(moved, addressing, hygiene) if there else []
        check(there and srg.count(there) == 1 and [f.split(":", 1)[0] for f in got] == ["row.there"],
              "l_pins_all: a landing row missing from SRG is reported (%r)" % got)

        # l_ids
        ids = ["g0", "g1", "g2", "g1.merged.fix", "g1.merged.if_ignored", "fix.make-default"]
        ids += ["g2.%s.%s" % (v, part) for v in ("session", "self", "no-identity", "implement")
                for part in ("not_done", "fix", "if_ignored")]
        # the pins table's ids (the landing, held commits and the run typed mid-run)
        pinned = ["g1.landing.not_done", "g1.landing.if_ignored", "g1.midrun.if_ignored", "g2.midrun.if_ignored",
                  "pre.stay.midrun", "pre.held.landed", "pre.held.failed", "pre.held.stuck", "pre.held.changed",
                  "app.landed", "app.landed.unlisted", "app.held.stuck", "row.held", "row.held-stuck", "row.there",
                  "row.here", "row.midrun-kept", "pre.here.finished", "g1.landing.not_done.unlanded",
                  "g1.not_done.uncommitted"]
        pinned += ["reason.land." + r for r in ("dropped", "edited", "forms", "deleted", "folder-gone", "register",
                                                "moved", "checked-out", "no-preflight", "no-snapshot", "unfinished")]
        ids += pinned
        ids += ["row.remote-deleted.default-tail", "row.scope.merge", "row.scope.no-file", "row.scope.hook", "row.scope.branch-path",
                "row.moved.refused", "row.session-rejected", "row.session-rejected.conflict-ending"]
        ids += ["app." + a for a in (
            "hook-line", "record-key", "record-unset", "unrecorded", "register-clause", "register-move", "upstream-error",
            "register-move.run", "register-move.remote", "why.failed.none",
            "why.later-refused", "why.moved-on", "why.failed", "why.stopped", "session.created", "session.conflict-default",
            "session.conflict-origin", "session.sync-error", "session.unsettled", "session.unsettled.close",
            "session.stranded", "session.unsupported", "why.checkout-moved",
            "session.refused-remedy", "mode-on", "mode-on.no-identity", "declined")]
        ids += ["reason." + r for r in (
            "conflict", "register-rebuild", "register-rebuild.failed", "would-overwrite", "cannot-replay", "in-progress", "locked", "push-scope",
            "checked-out", "fetch-failed", "branch-moved", "cannot-move", "checkout-moved", "not-run", "timed-out",
            "session-mode")]
        ids += ["remedy.rejected", "remedy.not-standing", "remedy.checked-out", "remedy.session-wrap"]
        ids += ["pre." + p for p in (
            "nonrepo", "below-top", "pull-failed", "leave-failed", "merged-unknown", "status-failed", "scope-failed",
            "merged-flush", "refused", "refused.unrecorded", "created.empty",
            "created.committed", "deleted", "delete-failed", "advisory-D", "advisory-D.rm", "pushed-left", "b2-config",
            "b2-squash", "b4", "b4.count", "stay", "stay.unlisted", "rerun-failed", "rerun-stay", "session-not-run",
            "stopped")]
        ids += ["end.stopped", "end.session-not-run", "text.push-capped", "text.pull-capped", "text.lift-unpreserved", "text.offline", "root.one-line",
                "root.stray", "root.two-readings",
                "root.left-behind", "root.left-behind.nested", "root.left-behind.dir", "root.left-behind.close", "env.changed"]
        missing = [i for i in ids if i not in T]
        check(not missing, "l_ids: every id the interface names is a template (missing %r)" % missing)
        check(len(lines.ROWS) == 29 and lines.ROWS[0] == "pushed-plugin"
              and lines.ROWS[-7:] == ("misrooted", "held", "held-stuck", "midrun-kept", "there", "here", "silent")
              and all(("row." + r in T) == (r != "silent") for r in lines.ROWS),
              "l_ids: 29 rows in §6's order, each a row.<id> template but silent (%r)" % (lines.ROWS,))
        check(all("\n" not in t for k, t in T.items() if k not in lines.BLOCKS),
              "l_ids: every template but the three blocks is one line")
        # The landing's refusal codes, read through globals() so that a missing constant fails its check rather than
        # crashing the selftest: each maps to its reason.land.* clause -- locked to reason.locked, which P15 reuses as
        # it stands -- and every code own_change and the landing write is mapped. The coverage half is approximate, a
        # tripwire: it finds the codes by regex over the three functions' source, so a refactor that builds the
        # refusal another way fails it spuriously, and it cannot see _land_change's dynamic why["reason"] (move_branch
        # and _ref_refusal's, all mapped or retried: checked-out, checkout-moved, branch-moved, locked).
        land_reasons, permanent = globals().get("LAND_REASONS"), globals().get("LAND_PERMANENT")
        mapped = land_reasons if isinstance(land_reasons, dict) else {}
        check(mapped and all(v in T and (v.startswith("reason.land.") or (k, v) == ("locked", "reason.locked"))
                             for k, v in mapped.items()),
              "l_ids: every code of LAND_REASONS maps to a reason.land.* template, locked to reason.locked (%r)"
              % (land_reasons,))
        def defined(path, name):
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            start = text.find("\ndef %s(" % name)
            end = text.find("\ndef ", start + 1)
            return "" if start < 0 else text[start:end if end > 0 else len(text)]

        sb_source = defined(SB_SCRIPT, "own_change")
        own_codes = set(re.findall(r'refused\[p\] = \("([a-z-]+)"', sb_source))
        land_source = "".join(defined(os.path.abspath(__file__), f) for f in ("_land_change", "_here_move", "_land"))
        land_codes = set(re.findall(r'(?:refused\s*=\s*(?:entry\["refused"\] or )?|refused=|"refused": )'
                                    r'\{"reason": "([a-z-]+)"', land_source))
        check(own_codes == {"deleted", "folder-gone", "edited", "forms", "dropped", "register-rebuild"}
              and land_codes == {"checked-out", "moved", "locked", "unfinished"}
              and own_codes | land_codes <= set(mapped) and permanent == own_codes,
              "l_ids: LAND_REASONS maps every refusal code own_change and the landing write, and LAND_PERMANENT is "
              "own_change's (%r, %r, %r)" % (sorted(own_codes), sorted(land_codes), permanent))

        # l_constants: the stay's kinds in the order of the alternation that names them, its reasons, and the path
        # <specs-git.py's path> takes
        kinds, reasons, script = (globals().get(n) for n in ("STAY_KINDS", "STAY_REASONS", "SG_SCRIPT"))
        alternations = []
        for tid in ("g1.landing.not_done", "g1.landing.not_done.unlanded", "app.landed", "row.held", "row.held-stuck"):
            try:
                alternations.append(lines._alternatives(lines.placeholder(tid, "<which no key")[1:-1]))
            except (KeyError, ValueError):
                alternations.append(None)
        check(kinds == ("unkeyed", "merged", "mid-run")
              and all(a is not None and len(a) == len(kinds) and "no key" in a[kinds.index("unkeyed")]
                      and "is merged" in a[kinds.index("merged")] and "was open" in a[kinds.index("mid-run")]
                      for a in alternations),
              "l_constants: STAY_KINDS is the order of the <which no key ...> alternation in each template (%r, %r)"
              % (kinds, alternations))
        check(reasons == ("g1", "unlisted", "refused", "stopped", "mid-run")
              and isinstance(script, str) and os.path.isabs(script) and os.path.basename(script) == "specs-git.py"
              and os.path.isfile(script) and os.path.samefile(script, os.path.abspath(__file__)),
              "l_constants: STAY_REASONS gains mid-run last, and SG_SCRIPT is this script's path (%r, %r)"
              % (reasons, script))

        # l_g1_not_done: the plain G1 block's Not done part opens P30's sentence
        rows = T["g1"].split("\n")
        i = next(k for k, row in enumerate(rows) if row.startswith("Not done:"))
        j = i + 1
        while j < len(rows) and rows[j].startswith(" "):
            j += 1
        part = " ".join(" ".join([rows[i][len("Not done:"):]] + rows[i + 1:j]).split())
        check(part.startswith("the preflight did not switch branches, and did not commit or push these files."),
              "l_g1_not_done: the plain G1 block's Not done opens with the files the block lists, true beside the held "
              "stage's commits (%r)" % part[:120])

        # l_g1_end: the forms of G1 the run's end repeats (§5), by whether it committed the run's whole change: with no
        # stay, the plain block, or, where nothing of the run's was committed, the not-committed form -- its Not done
        # and If ignored -- its Fix the plain block's; with a stay, the landing form, or its not-landed Not done; under a run
        # typed mid-run, the mid-run form, whose Not done each outcome picks the same way
        landing = globals().get("_g1_landing")
        S, paths = "/s", ["notes.md"]
        plain = lines.fill("g1", {"<SPECS_PATH>": S, "<N>": 1, "<path list>": ["notes.md", "notes.md"]})

        def parts(block):
            """label -> the part's text, unwrapped (a Not done, Fix or If ignored part of a §5 block)."""
            rows, out, label = block.split("\n"), {}, None
            for row in rows:
                hit = next((x for x in ("Not done:", "Fix:", "If ignored:") if row.startswith(x)), None)
                if hit:
                    label, out[hit] = hit, row[len(hit):].strip()
                elif label and row.startswith(" "):
                    out[label] += " " + row.strip()
                else:
                    label = None
            return out

        unkeyed = {"branch": "prd/B-2-y", "kind": "unkeyed", "reason": "g1", "merged": False, "command": None}
        midrun = {"command": "/specify", "started": "2026-11-10T10:00:00Z", "branch": "prd/B-2-y"}
        stay_m = dict(unkeyed, kind="mid-run", command="/specify")
        kinds = lines.placeholder("g1.landing.not_done", "<which no key")
        v = {"<default>": "main", "<branch>": "prd/B-2-y", "<command>": "/specify"}
        try:
            got = {name: parts(landing(lines, plain, "prd/B-2-y", "main", S, paths, stay, mid, committed))
                   for name, stay, mid, committed in (("plain", None, None, True), ("none", None, None, False),
                                                      ("whole", unkeyed, None, True), ("held", unkeyed, None, False),
                                                      ("m-plain", None, midrun, True), ("m-none", None, midrun, False),
                                                      ("m-whole", stay_m, midrun, True), ("m-held", stay_m, midrun, False))}
        except Exception as e:
            got = {"error": "%s: %s" % (type(e).__name__, e)}
        p0 = parts(plain)
        uncommitted = T.get("g1.not_done.uncommitted", "")
        ignored = T.get("g1.if_ignored.uncommitted", "")
        check(got.get("plain") == p0 and got.get("none", {}).get("Not done:") == uncommitted
              and got["none"]["Fix:"] == p0["Fix:"] and got["none"]["If ignored:"] == ignored
              and "WILL still be committed" not in uncommitted and "WILL still be committed" in p0["Not done:"]
              and "the Specs repo: line above this notice says what came of them" in uncommitted
              and "committed alongside them" in p0["If ignored:"] and "committed alongside" not in ignored
              and "the Specs repo: line above this notice says what came of this run's artifacts" in ignored,
              "l_g1_end: no stay -- the plain block where the end committed; where it did not, the not-committed form, "
              "its Not done and If ignored, the Fix the plain block's (%r)" % got)
        check(got.get("whole", {}).get("Not done:") == lines.fill("g1.landing.not_done.landed", dict(v, **{kinds: 0}))
              and got.get("held", {}).get("Not done:") == lines.fill("g1.landing.not_done.unlanded",
                                                                     dict(v, **{kinds: 0}))
              and got["held"]["If ignored:"] == T["g1.landing.if_ignored"] == got["whole"]["If ignored:"],
              "l_g1_end: a stay -- the landing form, its Not done the landed one after a whole landing and the "
              "not-landed one after any other outcome (%r)" % got)
        # M4: after the commit, the landed Not done says the artifacts were committed, never that they WILL be, and
        # names the run's Specs repo: line, which §6 prints above the repeated block
        landed_nd = (got.get("whole") or {}).get("Not done:") or ""
        check("WILL" not in landed_nd and "were committed at the end of the run on main" in landed_nd
              and landed_nd.endswith("the Specs repo: line above this notice names that commit.")
              and "WILL be committed" in T["g1.landing.not_done"],
              "l_g1_end: M4 -- the landed form promises nothing more after the commit (%r)" % landed_nd)
        midrun_ignored = lines.fill("g1.midrun.if_ignored", v)
        check(got.get("m-plain", {}).get("Not done:") == p0["Not done:"]
              and got.get("m-none", {}).get("Not done:") == uncommitted
              and got.get("m-whole", {}).get("Not done:") == lines.fill("g1.landing.not_done.landed",
                                                                        dict(v, **{kinds: 2}))
              and got.get("m-held", {}).get("Not done:") == lines.fill("g1.landing.not_done.unlanded",
                                                                       dict(v, **{kinds: 2}))
              and all(got.get(k, {}).get("Fix:") == "" and got[k].get("If ignored:") == midrun_ignored
                      for k in ("m-plain", "m-none", "m-whole", "m-held")),
              "l_g1_end: under a run typed mid-run, the mid-run form, its Not done by the same outcomes, a mid-run row "
              "that committed nothing taking the not-committed one (%r)" % got)
        check(raises_naming("no Not done: part", landing, lines, "the G1 block", "b", "main", S, paths, None, None, False),
              "l_g1_end: a block with no Not done part is refused, never rendered unchanged")

        # l_fill_basic
        check(lines.fill("row.nothing", {}) == "Specs repo: no session artifacts to commit", "l_fill_basic: row.nothing")
        check(raises_naming("<reason>", lines.fill, "row.failed", {"<sha7>": "abc1234", "<N>": 2, "<branch>": "main"}),
              "l_fill_basic: a missing value raises ValueError naming its placeholder")
        check(raises_naming("<N>", lines.fill, "row.pushed-plugin", {"<sha7>": "abc1234", "<branch>": "main"}),
              "l_fill_basic: a missing file count raises ValueError naming <N>")
        check(raises_naming("<branch>", lines.fill, "row.failed", {"<sha7>": "a", "<N>": 2, "<branch>": None, "<reason>": "r"}),
              "l_fill_basic: a None value outside an optional segment raises")
        check(raises_naming("repeats a clause", lines.fill, "root.left-behind", {}),
              "l_fill_basic: the left-behind line is never filled whole")

        # l_fill_list
        got = lines.fill("row.scope", {"<sha7>": ["1111111", "2222222"], "<N>": 1, "<branch>": "main",
                                       "<subject>": "Add notes", "<path>": "notes.md"})
        check(got.startswith("Specs repo: committed 1111111 (1 file) on main — ")
              and "the oldest 2222222 Add notes, which carries notes.md;" in got,
              "l_fill_list: the push-scope row's two <sha7>s, in order (%r)" % got)

        # l_fill_optional
        base = {"<sha7>": "abc1234", "<N>": 3, "<branch>": "main", "<K>": 2}
        got = lines.fill("row.replayed", dict(base, **{"<D>": None}))
        check(got.endswith("replayed its 2 commit(s) onto it"), "l_fill_optional: replayed with no <D> (%r)" % got)
        got = lines.fill("row.replayed", dict(base, **{"<D>": "1"}))
        check(got.endswith("onto it, 1 of them already there and dropped"), "l_fill_optional: replayed with <D> (%r)" % got)
        got = lines.fill("row.moved", dict(base, **{"<why>": "the push FAILED (x)"}))
        check("onto it and moved main there, but the push FAILED (x); the commits are on local main" in got and "[" not in got,
              "l_fill_optional: moved with neither optional clause (%r)" % got)
        got = lines.fill("row.moved", dict(base, **{"<why>": "w", "<D>": "1", "<the register clause>": "RC"}))
        check("onto it, 1 of them already there and dropped; RC and moved main there, but w;" in got,
              "l_fill_optional: moved with both optional clauses (%r)" % got)
        got = lines.fill("row.scope.hook", dict(base, **{"<path>": "a.md", "<M-1>": None}))
        check("a pre-commit hook added a.md to this commit" in got, "l_fill_optional: the hook row with one path (%r)" % got)
        got = lines.fill("row.scope.hook", dict(base, **{"<path>": "a.md", "<M-1>": "2"}))
        check("a pre-commit hook added a.md, and 2 more to this commit" in got,
              "l_fill_optional: the hook row with three paths (%r)" % got)
        got = lines.fill("reason.would-overwrite", {"<path>": "a.md", "<M>": None, "<branch>": "main"})
        check(got.startswith("moving the checkout would write over a.md, which you changed"),
              "l_fill_optional: would-overwrite with <M> None (%r)" % got)
        got = lines.fill("reason.would-overwrite", {"<path>": "a.md", "<M>": "2", "<branch>": "main"})
        check(got.startswith("moving the checkout would write over a.md and 2 more, which you changed"),
              "l_fill_optional: would-overwrite with <M> 2 (%r)" % got)
        one = {"<value>": "/r/specifications", span("root.one-line", "<is itself"): 0, "<the value the walk found>": "/r",
               span("root.one-line", "<the value the walk found |"): 0, "<that repository's top level>": None}
        got = lines.fill("root.one-line", one)
        check(got.endswith("Set SPECS_PATH to /r where it is set, and re-run.") and "which is itself a specifications/ directory —" in got,
              "l_fill_optional: the one-line form without its unsupported-layout segment (%r)" % got)
        got = lines.fill("root.one-line", dict(one, **{"<the value the walk found>": "/r/specs",
                                                       "<that repository's top level>": "/r"}))
        check(got.endswith("and re-run. /r/specs is not the top level of its repository (/r), and a specs tree inside a larger "
                           "repository is unsupported: this plugin switches branches and commits in that repository."),
              "l_fill_optional: the one-line form with its unsupported-layout segment (%r)" % got)
        got = lines.fill("root.one-line", dict(one, **{span("root.one-line", "<the value the walk found |"): 1}))
        check("Set SPECS_PATH to the directory that holds specifications/ where it is set" in got,
              "l_fill_optional: the one-line form naming no value (%r)" % got)
        stray = {"<value>": "/r", span("root.stray", "<the top level"): 0, "<subdirectory>": ["PRD-S-9-x"],
                 "<that repository's top level>": None}
        got = lines.fill("root.stray", stray)
        check(got.endswith("reported here instead.") and "not the top level" not in got,
              "l_fill_optional: the stray form drops its inner segment with no top level (%r)" % got)
        got = lines.fill("root.stray", dict(stray, **{"<value>": "/r/specs", span("root.stray", "<the top level"): 1,
                                                      "<that repository's top level>": "/r"}))
        check(got.endswith("instead. /r/specs is not the top level of its repository (/r), and a specs tree inside a larger "
                           "repository is unsupported: this plugin switches branches and commits in that repository.")
              and "SPECS_PATH is /r/specs, which holds /r/specs/specifications/, and holds" in got,
              "l_fill_optional: the stray form keeps its inner segment where its values are given (%r)" % got)

        # l_fill_list_marker
        got = lines.fill("app.session.conflict-default", {"<path>": ["a.md", "b c.md"], "<identity>": "ab", "<default>": "main"})
        check(got == "; merging main into session/ab left a.md, b c.md unsettled — settle them in its pull request",
              "l_fill_list_marker: <path>[, …] takes the whole list (%r)" % got)
        got = lines.fill("app.hook-line", {"<path>": ["a.md"], "<sha7>": "abc1234"})
        check(got == "Specs repo: a.md is now committed in abc1234, put there by a pre-commit hook, and not pushed",
              "l_fill_list_marker: a one-item list (%r)" % got)
        got = "".join(lines.fill("app.session.unsettled", {"<path>": p, "<identity>": "ab", "<SPECS_PATH>": "/s"})
                      for p in ("a.md", "b c.md")) + lines.fill("app.session.unsettled.close", {})
        check(got.count("so it was left out of this commit") == 2 and "show session/ab:a.md shows" in got
              and "show session/ab:b c.md shows" in got and got.endswith("each move of the specs checkout is skipped")
              and got.count("once a copy left out is the branch's version") == 1,
              "l_fill_list_marker: unsettled once per path, each with its own show, the close once (%r)" % got)

        # l_fill_root_lists
        two = ["PRD-S-9-x", "EPIC-S-9-01-y"]
        got = lines.fill("root.stray", dict(stray, **{"<subdirectory>": two}))
        check(got.count("PRD-S-9-x, EPIC-S-9-01-y") == 2 and "…" not in got and "[" not in got,
              "l_fill_root_lists: the stray form names both subdirectories in each of its two places (%r)" % got)
        got = lines.fill("root.stray", stray)
        check(got.count("PRD-S-9-x") == 2 and ", EPIC" not in got and "folder(s) PRD-S-9-x outside" in got,
              "l_fill_root_lists: with one name, it alone (%r)" % got)
        got = lines.left_behind({"<value>": "/s/specs", "<the value the walk found>": "/s"}, ["PRD-A-2-y", "PRD-A-3-z"],
                                ["dev-workflows-cost", "documentation/guide/dev-workflows"], False)
        want = ("Misrooted runs left: /s/specs/specifications/ (PRD-A-2-y, PRD-A-3-z), which belongs in /s/specifications/, "
                "and which the first run after SPECS_PATH is fixed searches for keys and commits bookkeeping from, in the wrong "
                "place, unless it is moved first; /s/specs/dev-workflows-cost/, which belongs at /s/dev-workflows-cost/; "
                "/s/specs/documentation/guide/dev-workflows/, which belongs at /s/documentation/guide/dev-workflows/, which the "
                "first run after SPECS_PATH is fixed commits there in the wrong place unless it is moved first. Move them "
                "yourself, commit the move, then re-run — the plugin moves nothing.")
        check(got == want, "l_fill_root_lists: the left-behind line, two folders and two directories (%r)" % got)
        got = lines.left_behind({"<value>": "/m", "<the value the walk found>": None}, None,
                                ["dev-workflows-feedback", "dev-workflows-cost"], True)
        want = ("If /m is a specs tree under another name, misrooted runs left: /m/dev-workflows-feedback/, which belongs at "
                "the same path at the specs repository's top level; /m/dev-workflows-cost/, which belongs at the same path at "
                "the specs repository's top level. Move them yourself, commit the move, then re-run — the plugin moves nothing.")
        check(got == want, "l_fill_root_lists: the two-readings opening, with no value the walk found (%r)" % got)
        check(lines.left_behind({"<value>": "/m", "<the value the walk found>": None}, None, [], False) is None
              and lines.left_behind({"<value>": "/m", "<the value the walk found>": None}, [], [], False) is None,
              "l_fill_root_lists: nothing left, no line, an empty folder list included")
        got = lines.left_behind({"<value>": "/m", "<the value the walk found>": None}, [], ["dev-workflows-cost"], False)
        check(got == "Misrooted runs left: /m/dev-workflows-cost/, which belongs at the same path at the specs repository's "
              "top level. Move them yourself, commit the move, then re-run — the plugin moves nothing.",
              "l_fill_root_lists: an empty folder list is no nested clause, never () (%r)" % got)

        # l_fill_alternation
        got = lines.fill("pre.stay", {"<branch>": "prd/A-1-x", "<default>": "main", span("pre.stay", "<switched"): 1})
        check(got.endswith("(it would have switched to main, as no key of this run names it)"),
              "l_fill_alternation: the stay line's second alternative, <default> filled (%r)" % got)
        got = lines.fill("pre.stay", {"<branch>": "prd/A-1-x", "<default>": "main", span("pre.stay", "<switched"): 0})
        check(got.endswith("(it would have switched to main and deleted it, as it is merged)"),
              "l_fill_alternation: the stay line's first alternative (%r)" % got)
        got = lines.fill("root.one-line", dict(one, **{span("root.one-line", "<is itself"): 2, "<key>": "A-1"}))
        check("which is itself a specs folder, asserting key A-1 — every folder" in got,
              "l_fill_alternation: the signal alternation's third alternative fills <key> (%r)" % got)
        check(raises_naming("no alternative 4", lines.fill, "root.one-line", dict(one, **{span("root.one-line", "<is itself"): 4})),
              "l_fill_alternation: an alternative that does not exist raises")
        got = lines.fill("root.one-line", dict(one, **{"<the value the walk found>": "/walk/value"}))
        check("Set SPECS_PATH to /walk/value where it is set" in got and "the value the walk found" not in got,
              "l_fill_alternation: int 0 on the value-to-set alternation renders the walk's value (%r)" % got)
        check(raises_naming("<the value the walk found>", lines.fill, "root.one-line",
                            dict(one, **{"<the value the walk found>": None})),
              "l_fill_alternation: an alternative naming a placeholder with no value raises naming it")
        walk_alt = span("root.one-line", "<the value the walk found |")
        check(raises_naming("is an alternation", lines.fill, "root.one-line", dict(one, **{walk_alt: "/r"})),
              "l_fill_alternation: a string for an alternation raises")
        check(raises_naming("is an alternation", lines.fill, "pre.stay",
                            {"<branch>": "b", "<default>": "main", span("pre.stay", "<switched"): True}),
              "l_fill_alternation: a bool for an alternation raises")
        check(raises_naming("beginning", span, "root.one-line", "<the value the walk found"),
              "l_fill_alternation: placeholder() refuses a prefix two placeholders share")
        check(span("root.one-line", "<key>") == "<key>" and span("pre.stay", "<default>") == "<default>"
              and span("root.two-readings", "<the parent of") == "<the parent of <value>>",
              "l_fill_alternation: placeholder() finds a placeholder inside an alternation's alternatives")
        check(raises_naming("has 0", span, "pre.stay", "<nothing>"), "l_fill_alternation: placeholder() refuses a key it lacks")

        # l_fill_count
        got1 = lines.fill("row.pushed-plugin", {"<sha7>": "abc1234", "<N>": 1, "<branch>": "prd/A-1-x"})
        got2 = lines.fill("row.pushed-plugin", {"<sha7>": "abc1234", "<N>": 2, "<branch>": "prd/A-1-x"})
        check(got1 == "Specs repo: committed abc1234 (1 file) on prd/A-1-x — pushed"
              and got2 == "Specs repo: committed abc1234 (2 files) on prd/A-1-x — pushed",
              "l_fill_count: singular at one (%r, %r)" % (got1, got2))

        # l_fill_landing: the landing's lines, filled -- the stay's alternation by kind, a held row's reason clause, the
        # stuck lines' two commands quoted whole, and the two new file counts singular at one
        def fill_landing():
            kind = span("app.landed", "<which no key")
            got = [lines.fill("app.landed", {"<branch>": "prd/B-2-y", "<default>": "main", "<command>": "/specify",
                                             kind: k}) for k in range(3)]
            tail = (", so its files were committed on main without leaving prd/B-2-y, and taken out of your working "
                    "tree there")
            check(got == ["; this run's preflight stayed on prd/B-2-y, which no key of this run names" + tail,
                          "; this run's preflight stayed on prd/B-2-y, which is merged into main" + tail,
                          "; this run's preflight stayed on prd/B-2-y, where /specify's run in this session was open "
                          "when this run started" + tail],
                  "l_fill_landing: app.landed by the stay's kind, <default> and <command> filled inside it (%r)" % got)
            clause = lines.fill("reason.land.checked-out", {"<path>": "/w2", "<default>": "main",
                                                            span("reason.land.checked-out", "<the push of"): 0,
                                                            "<reason>": "…"})
            got = lines.fill("row.held", {"<branch>": "prd/B-2-y", "<default>": "main", "<reason clause>": clause,
                                          span("row.held", "<which no key"): 0, span("row.held", "<held for"): 0})
            check(got.endswith(" without leaving it: another worktree, /w2, has main checked out, and the push of the "
                               "commit by refspec failed (…); they stay in your working tree, held for main, and the "
                               "next run tries again")
                  and got.startswith("Specs repo: NOT COMMITTED — this run's preflight stayed on prd/B-2-y, which "
                                     "no key"),
                  "l_fill_landing: row.held with reason.land.checked-out's failed push (%r)" % got)
            dropped = lines.fill("reason.land.dropped", {"<path>": "specifications/PRD-A-1-x/follow-ups.md",
                                                         "<onto>": "main"})
            S, tool = "/s p", "/plugins/workflows-core/scripts/specs-git.py"
            stuck = {"<branch>": "prd/B-2-y", "<default>": "main", "<reason clause>": dropped, "<SPECS_PATH>": S,
                     "<sha7>": "abc1234", "<specs-git.py's path>": tool, "<default-ref>": "origin/main",
                     "<path>": ["specifications/PRD-A-1-x/follow-ups.md"]}
            want = ["git -C \"%s\" show abc1234" % S,
                    "python3 \"%s\" --specs \"%s\" land --default-ref origin/main --drop-held abc1234" % (tool, S)]
            for tid, values in (("row.held-stuck", dict(stuck, **{span("row.held-stuck", "<which no key"): 1})),
                                ("app.held.stuck", stuck), ("pre.held.stuck", stuck)):
                got = lines.fill(tid, values)
                check(all(("'%s'" % w) in got and shlex.split(w) for w in want)
                      and got.endswith("'%s'" % want[1]) and dropped in got and "<" not in got,
                      "l_fill_landing: %s names both commands, each quoted whole (%r)" % (tid, got))
            # 4(c): the clause naming a stopped run's ends names that run's key set where it holds one, and drops it
            # where it holds none
            got = lines.fill("row.here", {"<sha7>": "abc1234", "<N>": 1, "<branch>": "main", "<command>": "/specify",
                                          "<keys>": "ACME-1", span("row.here", "<the next push"): 0})
            check(got.startswith("Specs repo: committed abc1234 (1 file) on main — not pushed yet: /specify's run")
                  and got.endswith("; the next push of main this plugin makes, by that run or a later one, carries it, "
                                   "and that run's files are as they were in your working tree; if you stopped that run, /clear, typing /specify again with ACME-1, or HEAD leaving the branch ends it")
                  and "so this run committed what changed since it started" in got and "only its own" not in got,
                  "l_fill_landing: row.here singular at one, its first alternative (%r)" % got)
            got = lines.fill("pre.held.landed", {"<sha7>": "abc1234", "<N>": 1, "<default>": "main",
                                                 "<branch>": "prd/B-2-y"})
            check(got.startswith("Specs preflight: committed abc1234 (1 file) on main: the session files an "
                                 "earlier run"),
                  "l_fill_landing: pre.held.landed singular at one (%r)" % got)
            # the held lines' tail: the next run's retry, or, where session-branch mode takes the files, what it does
            refused = lines.fill("reason.land.checked-out", {"<path>": "/w2", "<default>": "main", "<the refusal>": "x",
                                                             span("reason.land.checked-out", "<the push of"): 4})
            mode_tail = ("and the next run, in session-branch mode, drops this hold and commits them as that mode "
                         "commits session files")
            got = lines.fill("row.held", {"<branch>": "prd/B-2-y", "<default>": "main", "<reason clause>": refused,
                                          span("row.held", "<which no key"): 0, span("row.held", "<held for"): 1})
            check(got.endswith(", so from the next run session-branch mode takes these files; they stay in your "
                               "working tree, " + mode_tail) and "tries again" not in got,
                  "l_fill_landing: row.held's mode tail where session-branch mode takes the files (%r)" % got)
            got = [lines.fill("pre.held.failed", {"<default>": "main", "<reason clause>": refused,
                                                  span("pre.held.failed", "<and the next run tries"): k})
                   for k in (0, 1)]
            check(got[0].endswith("); they stay in your working tree, and the next run tries again")
                  and got[1].endswith("); they stay in your working tree, " + mode_tail),
                  "l_fill_landing: pre.held.failed's two tails (%r)" % got)
            # G1's end forms after a landing that did not land the run's whole change: the not-landed Not done promises
            # nothing, by kind, and names the run's Specs repo: outcome line -- printed above the repeated block -- by
            # what it is, not as "the line above", which in the block is its Found line; the landing, merged and
            # mid-run If ignored lines claim nothing about where this run's artifacts went
            unl = span("g1.landing.not_done.unlanded", "<which no key")
            got = [lines.fill("g1.landing.not_done.unlanded", {"<branch>": "prd/B-2-y", "<default>": "main",
                                                               "<command>": "/specify", unl: k}) for k in range(3)]
            head_ = ("the preflight did not switch branches, and did not commit or push these files. Those files are "
                     "yours, and switching branches would carry them along. This run's own artifacts were to be "
                     "committed at the end of the run on main, not on prd/B-2-y, ")
            tail_ = ", and your checkout is not moved; the Specs repo: line above this notice says what came of them."
            check(got == [head_ + w + tail_ for w in ("which no key of this run names", "which is merged into main",
                                                      "where /specify's run in this session was open when this run "
                                                      "started")]
                  and not any("WILL" in x or "the line above says" in x for x in got),
                  "l_fill_landing: g1.landing.not_done.unlanded by kind, promising nothing, naming the Specs repo: "
                  "line (%r)" % got)
            # G2's mid-run If ignored names the run's Specs repo: line by what it is -- true at the start, where no
            # outcome line is printed yet, and at the end, where it stands above the block -- never "the line above"
            got = lines.fill("g2.midrun.if_ignored", {"<command>": "/specify", "<branch>": "prd/B-2-y", "<keys>": None})
            check(got == "nothing is to be run here while /specify's run in this session is open on prd/B-2-y: let it "
                         "finish, or end it, first — if you stopped that run, /clear, typing /specify again, or HEAD leaving the branch ends it; this run's Specs repo: line, at its end, says what came of its "
                         "artifacts." and "line above" not in got,
                  "l_fill_landing: g2.midrun.if_ignored names the run's Specs repo: line (%r)" % got)
            neutral = [T[k] for k in ("g1.landing.if_ignored", "g1.merged.if_ignored", "g1.midrun.if_ignored")]
            check(all("nothing of this run's is committed with them" in x.lower() for x in neutral)
                  and not any("reach <default>" in x or "committed without them" in x for x in neutral),
                  "l_fill_landing: the landing, merged and mid-run If ignored lines are true whatever the outcome")
            got = [lines.fill("pre.here.finished", {"<branch>": "main", "<sha7>": "abc1234", "<N>": n}) for n in (1, 2)]
            check(got == ["Specs preflight: finished the commit an earlier run was making on main when it was cut off: "
                          "abc1234 (%s), that run's own session files, committed apart from another run's" % c
                          for c in ("1 file", "2 files")],
                  "l_fill_landing: pre.here.finished, singular at one (%r)" % got)
            got = lines.fill("row.midrun-kept", {"<command>": "/specify", "<branch>": "main", "<keys>": "ACME-1",
                                                 "<reason clause>": lines.fill("reason.land.unfinished",
                                                                               {"<branch>": "main"})})
            check(got == "Specs repo: NOT COMMITTED — /specify's run in this session is still open on main, and this "
                         "run's own changes could not be committed apart from that run's: main moved on without the "
                         "commit this run was making on it when it was cut off, so that commit was dropped unfinished; "
                         "they stay in your working tree, and that run's terminal commit takes them with its own; "
                         "if you stopped that run, /clear, typing /specify again with ACME-1, or HEAD leaving the branch ends it, and a later run's commit takes them",
                  "l_fill_landing: the mid-run row with reason.land.unfinished (%r)" % got)
            # a run typed mid-run whose start took no snapshot -- status could not run, or the start was cut off before
            # taking one -- commits nothing while the open run stands: its clause holds for both causes, so it names
            # neither a preflight that never ran nor a status that failed
            got = lines.fill("row.midrun-kept", {"<command>": "/specify", "<branch>": "prd/B-2-y",
                                                 "<keys>": "ACME-1-01 and ACME-1",
                                                 "<reason clause>": lines.fill("reason.land.no-snapshot", {})})
            check(got == "Specs repo: NOT COMMITTED — /specify's run in this session is still open on prd/B-2-y, and "
                         "this run's own changes could not be committed apart from that run's: this run's start took no "
                         "snapshot of the session files then uncommitted, so nothing tells its files from that run's; "
                         "they stay in your working tree, and that run's terminal commit takes them with its own; "
                         "if you stopped that run, /clear, typing /specify again with ACME-1-01 and ACME-1, or HEAD leaving the branch ends it, and a later run's commit takes them"
                  and "preflight" not in T["reason.land.no-snapshot"],
                  "l_fill_landing: the mid-run row with reason.land.no-snapshot, true for both causes (%r)" % got)
            # a landing that found an index.lock at its start holds the change for reason locked, a cause that passes:
            # the held row with reason.locked, its retry tail
            got = lines.fill("row.held", {"<branch>": "prd/B-2-y", "<default>": "main",
                                          "<reason clause>": lines.fill("reason.locked", {"<path>": ".git/index.lock"}),
                                          span("row.held", "<which no key"): 0, span("row.held", "<held for"): 0})
            check(got == "Specs repo: NOT COMMITTED — this run's preflight stayed on prd/B-2-y, which no key of this run "
                         "names, and its files could not be committed on main without leaving it: .git/index.lock is "
                         "held by another git process, or was left by one that died, and this plugin never deletes a "
                         "lock; they stay in your working tree, held for main, and the next run tries again",
                  "l_fill_landing: the held row with reason.locked, an index.lock at the landing's start (%r)" % got)

        try:
            if not all(t in T for t in pinned):
                raise ValueError("the pins table's templates are not all in T")
            fill_landing()
        except ValueError as e:  # a template that lost a placeholder the check names fails here, not the run
            check(False, "l_fill_landing: %s" % e)

        # l_literal_bracket
        got = lines.fill("app.register-move", {"<from>": "7", "<to>": "9", "<origin>": "a", "<whose number>": "the local number"})
        check(got == "[SEC#7] → [SEC#9] (a, the local number)", "l_literal_bracket: [SEC# stays literal (%r)" % got)

        # l_preflight_form
        failed = lines.fill("row.failed", {"<sha7>": "abc1234", "<N>": 2, "<branch>": "main", "<reason>": T["text.push-capped"]})
        got = lines.preflight_form(failed)
        check(got == "Specs preflight: main — push FAILED (the push did not finish within 60 s); the commit is local and a later "
              "run retries it", "l_preflight_form: the push FAILED row (%r)" % got)
        got = lines.preflight_form(lines.fill("row.locked", {}))
        check(got.startswith("Specs preflight: skipped — another session holds the repo"), "l_preflight_form: Locked (%r)" % got)
        got = lines.preflight_form(lines.fill("row.commit-failed", {"<the first line of git's error or the hook's output>": "e"}))
        check(got.startswith("Specs preflight: NOT COMMITTED — the commit failed (e)"), "l_preflight_form: Commit failed (%r)" % got)
        got = lines.preflight_form(lines.fill("row.pushed-plugin", {"<sha7>": "abc1234", "<N>": 1, "<branch>": "prd/A-1-x"}))
        check(got == "Specs preflight: prd/A-1-x — pushed", "l_preflight_form: a singular count (%r)" % got)

        # l_artifacts
        base_dir = "specifications/PRD-A-1-x/"
        check(lines.artifacts([base_dir + "prd.md"]) == base_dir + "prd.md", "l_artifacts: one path")
        check(lines.artifacts([base_dir + "prd.md", base_dir + "a b.md"]) == base_dir + "prd.md, " + base_dir + "a b.md",
              "l_artifacts: two paths, a space kept")
        three = [base_dir + "prd.md", base_dir + "ard.md", base_dir + "x.md"]
        check(lines.artifacts(three) == ", ".join(three), "l_artifacts: three paths")
        four = three + [base_dir + "revisions/prd-1.md"]
        check(lines.artifacts(four) == "4 files under specifications/PRD-A-1-x", "l_artifacts: four in one folder (%r)"
              % lines.artifacts(four))
        spread = three + ["specifications/PRD-A-2-y/defects.md"]
        check(lines.artifacts(spread) == "4 files under specifications", "l_artifacts: four spanning specifications/ (%r)"
              % lines.artifacts(spread))

        # l_fix_lines: every §5 Fix part, rendered with its values, is commands only -- no #, no quote left open: this
        # static check is what guards a paste into an interactive zsh, which does not read # as a comment unless
        # interactivecomments is set -- and runs whole in bash and, where it is on PATH, in zsh, against a git that
        # only logs its arguments, making exactly the git calls it shows. zsh -c is not interactive, so it reads # as a
        # comment whatever INTERACTIVE_COMMENTS says: that run checks the part's syntax and quoting in zsh, never how a
        # # reads there
        shim = os.path.join(tmp, "l-fix-shim")
        os.makedirs(shim)
        log = os.path.join(tmp, "l-fix-calls")
        with open(os.path.join(shim, "git"), "w", encoding="utf-8") as fh:
            fh.write("#!/bin/sh\nfor a in \"$@\"; do printf '%s|' \"$a\"; done >> \"$GIT_CALLS\"\necho >> \"$GIT_CALLS\"\n")
        os.chmod(os.path.join(shim, "git"), 0o755)
        S, paths = os.path.join(tmp, "a specs repo"), ["my notes.md", "n.md"]
        plain = lines.fill("g1", {"<SPECS_PATH>": S, "<N>": 2,
                                  "<path list>": [", ".join(paths), " ".join(shlex.quote(p) for p in paths)]})
        blocks = [("g0", lines.fill("g0", {"<SPECS_PATH>": S, "<sha7>": "abc1234", "<YYYY-MM-DD>": "2026-11-10",
                                           "<branch>": "main"}), ["switch|-c|rescue/2026-11-10|"]),
                  ("g1", plain, ["status|", "add|my notes.md|n.md|", "commit|"]),
                  ("g2", _g2_block(lines, S, "feature/x", "main"), ["switch|main|"]),
                  ("g2.implement", _g2_block(lines, S, "feature/x", "main", "implement"), []),
                  ("g2.session", _g2_block(lines, S, "feature/x", "main", "session", {"<identity>": "ab"}), []),
                  ("g2.self", _g2_block(lines, S, "session/ab", "main", "self", {"<identity>": "ab"}), ["switch|main|"]),
                  ("g2.no-identity", _g2_block(lines, S, "feature/x", "main", "no-identity"), [])]
        landing = globals().get("_g1_landing")  # G1's landing forms (§5): the plain Fix, or merged's switch first
        check(landing is not None, "l_fix_lines: _g1_landing renders G1's landing forms")
        if landing is not None:
            unkeyed = {"branch": "prd/B-2-y", "kind": "unkeyed", "reason": "g1", "merged": False, "command": None}
            merged = {"branch": "prd/A-1-x", "kind": "merged", "reason": "g1", "merged": True, "command": None}
            blocks += [("g1.landing", landing(lines, plain, "prd/B-2-y", "main", S, paths, unkeyed, None),
                        ["status|", "add|my notes.md|n.md|", "commit|"]),
                       ("g1.landing.merged", landing(lines, plain, "prd/A-1-x", "main", S, paths, merged, None),
                        ["switch|main|", "add|my notes.md|n.md|", "commit|"])]
        for name, block, want in blocks:
            rows = block.split("\n")
            i = next((k for k, row in enumerate(rows) if row.startswith("Fix:")), None)
            part = []
            for row in rows[i:] if i is not None else []:
                if part and not row.startswith(" "):
                    break
                part.append(row[len("Fix:"):].strip() if not part else row.strip())
            balanced = True
            for row in part:
                try:
                    shlex.split(row)
                except ValueError:
                    balanced = False
            check(i is not None and not any("#" in row for row in part) and balanced,
                  "l_fix_lines: %s's Fix part is commands only -- no #, which zsh's interactive shell does not read as a "
                  "comment, and no quote left open (%r)" % (name, part))
            for shell in [["bash", "-c"]] + ([["zsh", "-c"]] if shutil.which("zsh") else []):
                if os.path.exists(log):
                    os.remove(log)
                ran = subprocess.run(shell + ["\n".join(part)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     env=dict(os.environ, PATH=shim + os.pathsep + os.environ.get("PATH", ""),
                                              GIT_CALLS=log))
                calls = open(log, encoding="utf-8").read().splitlines() if os.path.exists(log) else []
                check(i is not None and ran.returncode == 0 and calls == ["-C|%s|%s" % (S, w) for w in want],
                      "l_fix_lines: %s's Fix part runs whole through %s -c, making its git calls (rc %s, %r, %r)"
                      % (name, shell[0], ran.returncode, calls, ran.stderr.decode("utf-8", "replace")[:200]))

    def scenarios_gate(tmp):
        with open(SESSION_HYGIENE, encoding="utf-8") as fh:
            hygiene = fh.read()
        with open(ADDRESSING, encoding="utf-8") as fh:
            addressing = fh.read()
        section7 = hygiene[hygiene.index("\n## 7. "):]
        after = section7[section7.index("**The line.**"):]
        block = after[after.index("```bash\n") + len("```bash\n"):after.index("\n```", after.index("```bash\n"))]

        def carrier(path, key, kind="prd", quote=""):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("---\nkind: %s%s%s\nkey: %s%s%s\n---\n\n# x\n" % (quote, kind, quote, quote, key, quote))

        real = os.path.realpath
        inside = ("every folder lives under $SPECS_PATH/specifications/, so this run would look for and create folders "
                  "in the wrong place; it wrote nothing under that path, and its cost and feedback are reported here "
                  "instead.")
        unsupported = ("is not the top level of its repository (%s), and a specs tree inside a larger repository is "
                       "unsupported: this plugin switches branches and commits in that repository.")
        close = " Move them yourself, commit the move, then re-run — the plugin moves nothing."

        def nonrepo(value, which):
            return ("Specs preflight: SPECS_PATH is %s, which %s — nothing this run writes there is committed or handed "
                    "off; set SPECS_PATH to your specs repository's top level, where it is set, and re-run." % (value, which))

        # g_sh7_pinned
        check(SH7_LINE == block, "g_sh7_pinned: SH7_LINE is session-hygiene §7's fenced block (%r)" % block)

        # g_env_line_equal
        r = new_repo(tmp, "env repo")
        r.git("remote", "add", "origin", "git@github.com:acme/specs.git")
        link = os.path.join(tmp, "env-link")
        os.symlink(r.path, link)
        keep = {k: os.environ.get(k) for k in ("SPECS_PATH", "REPOS_PATH")}
        cwd = os.getcwd()
        try:
            os.chdir(tmp)
            for repos in (None, "/workspace/repos dir"):
                if repos is None:
                    os.environ.pop("REPOS_PATH", None)
                else:
                    os.environ["REPOS_PATH"] = repos
                for value in ("", r.path + "/", link, "env repo", os.path.join(tmp, "no-such"), r.path):
                    env = dict(os.environ)
                    env.pop("SPECS_PATH", None)
                    if value:
                        env["SPECS_PATH"] = value
                    want = subprocess.run(["bash", "-c", block], env=env, stdout=subprocess.PIPE).stdout.decode("utf-8")
                    got = env_line(value)
                    check(got + "\n" == want, "g_env_line_equal: SPECS_PATH %r, REPOS_PATH %r (%r, %r)" % (value, repos, got, want))
            os.environ["SPECS_PATH"] = "/somewhere/else"
            check(env_line("").startswith("Environment: SPECS_PATH=unset (origin none), "),
                  "g_env_line_equal: an empty value is unset whatever the environment holds (%r)" % env_line(""))
            check(env_line("env repo") == "Environment: SPECS_PATH=%s (origin git@github.com:acme/specs.git), REPOS_PATH=%s"
                  % (real(r.path), os.environ.get("REPOS_PATH", "unset")),
                  "g_env_line_equal: a relative path is its real path, with its origin (%r)" % env_line("env repo"))
        finally:
            os.chdir(cwd)
            for k, v in keep.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

        # g_unset
        got = gate("")
        check(got == {"state": "unset", "top": None, "git_dir": None, "misrooted": False, "lines": []},
              "g_unset: unset is silent (%r)" % got)
        check(gate("", notices=False) == {"state": "unset", "top": None, "git_dir": None},
              "g_unset: notices off returns state, top and git_dir alone (%r)" % gate("", notices=False))

        # g_file
        f = os.path.join(tmp, "a-file")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write("x\n")
        got = gate(f)
        check(got["state"] == "not-a-repo" and got["lines"] == [nonrepo(f, "is not a directory")] and not got["misrooted"],
              "g_file: a regular file is not a directory (%r)" % got)
        missing = os.path.join(tmp, "no such dir")
        got = gate(missing)
        check(got["state"] == "not-a-repo" and got["lines"] == [nonrepo(missing, "is not a directory")],
              "g_file: a path that does not exist is not a directory (%r)" % got)

        # g_plain_dir
        plain = os.path.join(tmp, "gate-plain")
        os.makedirs(plain)
        got = gate(plain)
        check(got["state"] == "not-a-repo" and got["lines"] == [nonrepo(plain, "is not in a git repository")]
              and got["misrooted"] is False and got["top"] is None and got["git_dir"] is None,
              "g_plain_dir: a directory in no repository, no signal (%r)" % got)

        # g_mounted_specifications
        m = os.path.join(tmp, "mount-a", "specifications")
        carrier(os.path.join(m, "PRD-A-1-x", "prd.md"), "A-1")
        stop = ("SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, which is itself a specifications/ directory — %s Set "
                "SPECS_PATH to the directory that holds specifications/ where it is set, and re-run." % (m, inside))
        got = gate(m)
        check(got["state"] == "not-a-repo" and got["misrooted"] is True
              and got["lines"] == [nonrepo(m, "is not in a git repository") + " " + stop],
              "g_mounted_specifications: the notice, then on the same line the one-line stop (%r)" % got)
        got = specs_root_check(m)
        check(got["signal"] == "a-ef" and got["form"] == "one-line" and got["value"] is None and got["subdirs"] == [],
              "g_mounted_specifications: signal a-ef, the one-line form, no value (%r)" % got)
        os.makedirs(os.path.join(m, "specifications", "PRD-A-2-y"))
        os.makedirs(os.path.join(m, "dev-workflows-cost"))
        got = gate(m)
        behind = ("Misrooted runs left: %s/specifications/ (PRD-A-2-y), which belongs in the specs repository's "
                  "specifications/, and which the first run after SPECS_PATH is fixed searches for keys and commits "
                  "bookkeeping from, in the wrong place, unless it is moved first; %s/dev-workflows-cost/, which belongs "
                  "at the same path at the specs repository's top level.%s" % (m, m, close))
        check(got["misrooted"] is True and got["lines"] == [nonrepo(m, "is not in a git repository") + " " + stop, behind],
              "g_mounted_specifications: the left-behind line after it, on its own (%r)" % got)

        # g_mounted_other_name
        t = os.path.join(tmp, "mount-b", "tree")
        carrier(os.path.join(t, "PRD-A-1-x", "ard.md"), "A-1", kind="ard")
        carrier(os.path.join(t, "PRD-A-1-x", "prd.md"), "A-1", quote='"')
        stop = ("SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, which holds the specs folder PRD-A-1-x directly, and nothing on "
                "disk says whether %s is a specs tree under another name or a specs root. If it is a specs tree under "
                "another name, its folders belong in a directory named specifications/, and SPECS_PATH names that "
                "directory's parent: set SPECS_PATH to the parent of the specifications/ directory %s is a mount of, and "
                "mount that parent whole rather than the tree alone, where it is set. If it is a specs root, move "
                "PRD-A-1-x and every other specs folder beside it into %s/specifications/ yourself and commit the move, "
                "and make %s the top level of a git repository, which it is not. Then re-run — the plugin moves nothing. "
                "This run wrote nothing under that path, and its cost and feedback are reported here instead."
                % (t, t, t, t, t))
        got = gate(t)
        check(got["state"] == "not-a-repo" and got["misrooted"] is True
              and got["lines"] == [nonrepo(t, "is not in a git repository") + " " + stop],
              "g_mounted_other_name: the notice, then on the same line the two-readings stop (%r)" % got)
        parent = os.path.dirname(t)
        check(not any(("SPECS_PATH to %s" % p) in line for line in got["lines"] for p in (parent, real(parent)))
              and not any("the directory that holds specifications/" in line for line in got["lines"]),
              "g_mounted_other_name: no line names a value addressing §3 rules out (%r)" % got)
        got = specs_root_check(t)
        check(got["signal"] == "b-sub" and got["form"] == "two-readings" and got["value"] is None
              and got["subdirs"] == ["PRD-A-1-x"], "g_mounted_other_name: b-sub, two readings (%r)" % got)
        cur = os.path.join(tmp, "mount-b", "cur")
        os.symlink(os.path.join(t, "PRD-A-1-x"), cur)
        got = specs_root_check(cur)
        check(got["signal"] == "b-self" and got["form"] == "one-line"
              and "which is itself a specs folder, asserting key A-1 —" in got["lines"][0],
              "g_mounted_other_name: a link is judged by the folder it reaches, by its physical name (%r)" % got)
        named = os.path.join(tmp, "mount-b", "notes")
        carrier(os.path.join(named, "prd.md"), "A-1")
        alias = os.path.join(tmp, "mount-b", "PRD-A-1-alias")
        os.symlink(named, alias)
        check(specs_root_check(alias)["signal"] is None,
              "g_mounted_other_name: a link's own name never passes the prefix test for it (%r)" % specs_root_check(alias))
        inv = os.path.join(tmp, "mount-c", "other")
        carrier(os.path.join(inv, "BRD-B-1-x", "coverage-ledger.md"), "B-1", kind="coverage-ledger")
        carrier(os.path.join(inv, "BRD-B-1-x", "brd", "brd-inventory.md"), "B-1", kind="brd")
        got = specs_root_check(inv)
        check(got["signal"] == "b-sub" and got["subdirs"] == ["BRD-B-1-x"],
              "g_mounted_other_name: a root BRD folder's carrier is its brd/brd-inventory.md (%r)" % got)

        # g_inside_tree
        r = new_repo(tmp, "inside")
        carrier(os.path.join(r.path, "specifications", "PRD-A-1-x", "prd.md"), "A-1")
        r.commit_all("a folder")
        spec_dir = os.path.join(r.path, "specifications")
        got = gate(spec_dir)
        stop = ("SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, which is itself a specifications/ directory — %s Set SPECS_PATH "
                "to %s where it is set, and re-run." % (spec_dir, inside, real(r.path)))
        check(got["state"] == "pass" and got["misrooted"] is True and got["lines"] == [stop]
              and real(got["top"]) == real(r.path) and real(got["git_dir"]) == real(os.path.join(r.path, ".git")),
              "g_inside_tree: <repo>/specifications names <repo> (%r)" % got)
        check(specs_root_check(spec_dir)["signal"] == "a-prefix" and specs_root_check(spec_dir)["value"] == real(r.path),
              "g_inside_tree: signal a-prefix, value <repo> (%r)" % specs_root_check(spec_dir))
        folder = os.path.join(spec_dir, "PRD-A-1-x")
        got = gate(folder)
        check(specs_root_check(folder)["signal"] == "a-prefix" and got["misrooted"] is True
              and got["lines"] == [stop.replace(spec_dir + ", which is itself a specifications/ directory",
                                                folder + ", which is inside the specifications/ directory")],
              "g_inside_tree: a folder inside the tree is the same signal (%r)" % got)
        via = os.path.join(tmp, "inside-link")
        os.symlink(folder, via)
        got = specs_root_check(via)
        check(got["signal"] == "a-prefix" and got["value"] == real(r.path)
              and got["lines"][0].endswith("Set SPECS_PATH to %s where it is set, and re-run." % real(r.path)),
              "g_inside_tree: the walk starts from the physical path, so a link to a folder names <repo> (%r)" % got)
        os.makedirs(os.path.join(spec_dir, "specifications", "PRD-A-2-y"))
        os.makedirs(os.path.join(spec_dir, "dev-workflows-cost"))
        got = gate(spec_dir)
        check(got["misrooted"] is True and got["lines"] == [stop, (
            "Misrooted runs left: %s/specifications/ (PRD-A-2-y), which belongs in %s/specifications/, and which the first "
            "run after SPECS_PATH is fixed searches for keys and commits bookkeeping from, in the wrong place, unless it is "
            "moved first; %s/dev-workflows-cost/, which belongs at %s/dev-workflows-cost/.%s"
            % (spec_dir, real(r.path), spec_dir, real(r.path), close))],
              "g_inside_tree: what an earlier run left in <repo>/specifications belongs under the value the walk found (%r)"
              % got)

        # g_below_top
        r = new_repo(tmp, "below")
        carrier(os.path.join(r.path, "specs", "specifications", "PRD-A-1-x", "prd.md"), "A-1")
        r.commit_all("a nested tree")
        specs = os.path.join(r.path, "specs")
        got = gate(specs)
        check(got["state"] == "pass" and got["misrooted"] is True and got["lines"] == [
            "Specs preflight: SPECS_PATH is %s, below the top level of its repository (%s) — a specs tree inside a larger "
            "repository is unsupported, because this plugin switches branches and commits in the repository SPECS_PATH "
            "belongs to, so this run switches and commits nothing there; set SPECS_PATH to a dedicated specs "
            "repository's top level." % (specs, got["top"])] and real(got["top"]) == real(r.path),
              "g_below_top: one line from pre.below-top naming <repo> (%r)" % got)
        nested = os.path.join(specs, "specifications")
        got = gate(nested)
        want = ("SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, which is itself a specifications/ directory — %s Set SPECS_PATH "
                "to %s where it is set, and re-run. %s %s" % (nested, inside, real(specs), real(specs),
                                                              unsupported % real(r.path)))
        check(got["misrooted"] is True and got["lines"] == [want] and specs_root_check(nested)["signal"] == "a-ef",
              "g_below_top: the inside-tree notice skips the below-top one, the unsupported clause carried (%r)" % got)

        # g_stray
        r = new_repo(tmp, "stray")
        carrier(os.path.join(r.path, "specifications", "PRD-A-1-x", "prd.md"), "A-1")
        carrier(os.path.join(r.path, "PRD-S-9-x", "prd.md"), "S-9")
        r.write("dev-workflows-cost/c.md", "cost\n")
        got = gate(r.path)
        check(got["state"] == "pass" and got["misrooted"] is True and got["lines"] == [
            "SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, the top level of its repository, and holds the specs folder(s) "
            "PRD-S-9-x outside %s/specifications/, where every folder lives. SPECS_PATH names the right directory; move "
            "PRD-S-9-x into %s/specifications/ yourself, commit the move, then re-run — the plugin moves nothing. This run "
            "wrote nothing under %s, and its cost and feedback are reported here instead." % ((r.path,) * 4)],
              "g_stray: the stray-folder form, no left-behind line (%r)" % got)
        carrier(os.path.join(r.path, "EPIC-S-9-01-y", "epic.md"), "S-9-01", kind="epic")
        got = specs_root_check(r.path)
        check(got["form"] == "stray" and got["subdirs"] == ["EPIC-S-9-01-y", "PRD-S-9-x"]
              and got["lines"][0].count("EPIC-S-9-01-y, PRD-S-9-x") == 2 and len(got["lines"]) == 1,
              "g_stray: the loop finished, every stray named in byte-wise order (%r)" % got)
        r = new_repo(tmp, "stray-below")
        carrier(os.path.join(r.path, "specs", "specifications", "PRD-A-1-x", "prd.md"), "A-1")
        carrier(os.path.join(r.path, "specs", "PRD-S-9-x", "prd.md"), "S-9")
        specs = os.path.join(r.path, "specs")
        got = gate(specs)
        check(got["misrooted"] is True and len(got["lines"]) == 1
              and got["lines"][0].startswith("SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, which holds %s/specifications/, "
                                             "and holds the specs folder(s) PRD-S-9-x outside" % (specs, specs))
              and got["lines"][0].endswith("reported here instead. %s %s" % (specs, unsupported % real(r.path))),
              "g_stray: below the top level, which holds specifications/, the unsupported clause (%r)" % got)

        # g_two_readings
        r = new_repo(tmp, "two")
        carrier(os.path.join(r.path, "specs", "PRD-A-1-x", "prd.md"), "A-1")
        specs = os.path.join(r.path, "specs")
        top = real(r.path)
        stop = ("SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, which holds the specs folder PRD-A-1-x directly, and nothing on "
                "disk says whether %s is a specs tree under another name or a specs root. If it is a specs tree under "
                "another name, its folders belong in a directory named specifications/, and SPECS_PATH names that "
                "directory's parent: move them into %s/specifications/ yourself, commit the move, and set SPECS_PATH to "
                "%s, where it is set. If it is a specs root, move PRD-A-1-x and every other specs folder beside it into "
                "%s/specifications/ yourself and commit the move; %s %s Then re-run — the plugin moves nothing. This run "
                "wrote nothing under that path, and its cost and feedback are reported here instead."
                % (specs, specs, top, top, specs, specs, unsupported % top))
        got = gate(specs)
        check(got["state"] == "pass" and got["misrooted"] is True and got["lines"] == [stop],
              "g_two_readings: the two-readings form with the unsupported-layout clause (%r)" % got)
        via = os.path.join(tmp, "two-link")
        os.symlink(specs, via)
        got = specs_root_check(via)
        check(got["form"] == "two-readings" and "move them into %s/specifications/ yourself, commit the move, and set "
              "SPECS_PATH to %s, where it is set." % (top, top) in got["lines"][0],
              "g_two_readings: the parent the first reading names is the physical one (%r)" % got)
        os.makedirs(os.path.join(specs, "dev-workflows-feedback"))
        os.makedirs(os.path.join(specs, "documentation", "guide", "dev-workflows"))
        got = gate(specs)
        check(got["lines"][1:] == [
            "If %s is a specs tree under another name, misrooted runs left: %s/dev-workflows-feedback/, which belongs at "
            "the same path at the specs repository's top level; %s/documentation/guide/dev-workflows/, which belongs at "
            "the same path at the specs repository's top level, which the first run after SPECS_PATH is fixed commits "
            "there in the wrong place unless it is moved first.%s" % (specs, specs, specs, close)],
              "g_two_readings: the left-behind line, under the first reading (%r)" % got)

        # g_correct_root
        r = new_repo(tmp, "correct")
        carrier(os.path.join(r.path, "specifications", "PRD-A-1-x", "prd.md"), "A-1")
        carrier(os.path.join(r.path, "templates", "prd.md"), "A-1")
        carrier(os.path.join(r.path, "README.md"), "A-1")
        os.symlink(os.path.join("specifications", "PRD-A-1-x"), os.path.join(r.path, "PRD-A-1-x"))
        os.symlink(os.path.join("specifications", "PRD-A-1-x"), os.path.join(r.path, "current"))
        got = gate(r.path)
        check(got["state"] == "pass" and got["lines"] == [] and got["misrooted"] is False and specs_root_check(r.path)
              == {"signal": None, "form": None, "value": None, "subdirs": [], "lines": []},
              "g_correct_root: templates/, README.md and a link into the tree are no signal (%r)" % got)
        got = gate(r.path, notices=False)
        check(sorted(got) == ["git_dir", "state", "top"] and got["state"] == "pass",
              "g_correct_root: notices off returns state, top and git_dir alone (%r)" % got)
        r = new_repo(os.path.join(tmp, "clone"), "specifications")
        carrier(os.path.join(r.path, "specifications", "PRD-A-1-x", "prd.md"), "A-1")
        got = gate(r.path)
        check(got["state"] == "pass" and got["lines"] == [] and specs_root_check(r.path)["signal"] is None,
              "g_correct_root: a repository cloned into a directory named specifications is a root (%r)" % got)
        loose = os.path.join(tmp, "mount-d", "loose")
        os.makedirs(os.path.join(loose, "PRD-A-3-z"))
        with open(os.path.join(loose, "PRD-A-3-z", "notes.md"), "w", encoding="utf-8") as fh:
            fh.write("# Notes\n\n---\nkind: prd\nkey: A-3\n---\n")
        with open(os.path.join(loose, "PRD-A-3-z", "open.md"), "w", encoding="utf-8") as fh:
            fh.write("---\nkind: prd\nkey: A-3\n")
        check(specs_root_check(loose)["signal"] is None,
              "g_correct_root: frontmatter is only what opens a file and closes, never a rule further down (%r)"
              % specs_root_check(loose))

        # g_reserved
        para = addressing[addressing.index("**Reserved subdirectory names are not folder kinds.**"):]
        para = para[para.index("never resolved by one —"):para.index("None matches")]
        raw = re.findall(r"`([^`/][^`]*)/`", para)
        names = [n.replace("<YYYYMMDD>", "20261109") for n in raw]
        check(len(names) == 10 and all(RESERVED.match(n) for n in names),
              "g_reserved: RESERVED matches every name of addressing §2's list (%r)" % names)
        check(not any(RESERVED.match(n) for n in ("brd2", "xbrd", "bundle-2026", "bundle-202611090", "PRD-A-1-x",
                                                  "Doc screenshots/", "design ")),
              "g_reserved: RESERVED matches whole names only")
        mine = re.search(r"\(\?:(.+)\)", RESERVED.pattern).group(1).split("|")
        check(sorted(mine) == sorted(n.replace("<YYYYMMDD>", "[0-9]{8}") for n in raw),
              "g_reserved: RESERVED holds addressing §2's names and no other (%r, %r)" % (mine, raw))
        theirs = re.search(r"\(\.\+/\)\?\((.+)\)/$", sb.EXCLUDED).group(1).split("|")
        check(sorted(theirs) == sorted(n for n in mine if n != "dev-workflows") and "dev-workflows" in mine,
              "g_reserved: session-branch.py's EXCLUDED holds the same names but dev-workflows (%r, %r)" % (mine, theirs))

        # g_read_only (skipped as root, for whom no mode bit refuses a write)
        if not (hasattr(os, "geteuid") and os.geteuid() == 0):
            r = new_repo(tmp, "read-only")
            git_dir = os.path.join(r.path, ".git")
            os.chmod(git_dir, 0o555)
            try:
                got = gate(r.path)
                check(got["state"] == "read-only" and got["lines"] == [] and got["misrooted"] is False,
                      "g_read_only: a git directory with no write bit (%r)" % got)
            finally:
                os.chmod(git_dir, 0o755)

        # g_cli
        for value in (m, t, "", spec_dir):
            got = cli("--specs", value, "specs-root-check")
            raw = {k: v for k, v in got.items() if not k.startswith("_")}
            check(got["_rc"] == 0 and raw == specs_root_check(value), "g_cli: %r prints the function's object (%r)" % (value, got))
        got = cli("--specs", f, "specs-root-check")
        check(got["_rc"] == 0 and got.get("signal") is None, "g_cli: a file is passed through unchecked (%r)" % got)
        got = cli("specs-root-check")
        check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: "),
              "g_cli: no --specs at all is a usage error (%r)" % got)

    # The run worlds scenarios_end and scenarios_replay share.
    PRD = "specifications/PRD-ACME-1-x/prd.md"
    RESUME = "specifications/PRD-ACME-1-x/dev-workflows/resume.md"
    PLUGIN = "prd/ACME-1-x"

    @contextlib.contextmanager
    def in_env(env):
        keep = {k: os.environ.get(k) for k in env}
        os.environ.update(env)
        try:
            yield
        finally:
            for k, v in keep.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def world(tmp, name):
        """A bare origin; a clone with the PRD committed and pushed on main; the environment of a run of session
        <name>: HOME under tmp, the session variable, SPECS_PATH naming the clone."""
        bare = os.path.join(tmp, name + ".git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
        r = new_repo(tmp, name)
        r.write(PRD, "---\nkind: prd\nkey: ACME-1\n---\n\n# PRD\n")
        r.commit_all("ACME-1 Add the PRD")
        r.git("remote", "add", "origin", bare)
        r.git("push", "-q", "-u", "origin", "main")
        r.bare = bare
        home = os.path.join(tmp, "home-" + name)
        os.makedirs(home)
        return r, {"HOME": home, "CLAUDE_CODE_SESSION_ID": name, "SPECS_PATH": r.path}

    def other_key(r, name="prd/B-2-y"):
        """A plugin branch no key of the run names, with one commit of its own, pushed with -u, HEAD left on it."""
        r.git("switch", "-q", "-c", name)
        r.write("specifications/PRD-B-2-y/prd.md", "---\nkind: prd\nkey: B-2\n---\n")
        r.commit_all("B-2 Add the PRD")
        r.git("push", "-q", "-u", "origin", name)

    def seed(env, command, **fields):
        """A record as start saves one, its env_line from env_line(<the clone>)."""
        state = _flow()[0]
        specs = fields.pop("specs", env["SPECS_PATH"])
        rec = dict(specs=specs, env_line=env_line(specs), gate="pass", top=os.path.realpath(specs), default="main",
                   default_ref="origin/main", remote="origin", mode="off", branch="main", stage="done",
                   args={"specs": specs, "keys": [], "commit_key": None, "register_rebuild": None})
        rec.update(fields)
        with in_env(env):
            session = env["CLAUDE_CODE_SESSION_ID"]
            state.save(session, command, state.new(command, session=session, **rec))

    def record(env, command):
        with in_env(env):
            return _flow()[0].load(env["CLAUDE_CODE_SESSION_ID"], command)

    def run_end(env, command, *args, specs=None, stdin=b""):
        return cli("--specs", env["SPECS_PATH"] if specs is None else specs, "end", "--command", command, *args,
                   env=env, stdin=stdin)

    def on_origin(r, branch="main"):
        p = subprocess.run(["git", "-C", r.bare, "rev-parse", "--verify", "-q", "refs/heads/" + branch],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        return p.stdout.decode().strip() or None

    def clone(r, name):
        """Another clone of <r>'s origin, beside <r>."""
        path = os.path.join(os.path.dirname(r.path), name)
        subprocess.run(["git", "clone", "-q", r.bare, path], check=True, stderr=subprocess.DEVNULL)
        o = Repo(path)
        o.git("config", "user.email", "o@example.invalid")
        o.git("config", "user.name", "o")
        o.git("config", "commit.gpgsign", "false")
        return o

    def hook(path, body):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("#!/bin/sh\n" + body)
        os.chmod(path, 0o755)

    def head(r):
        return r.git("rev-parse", "HEAD")

    def scenarios_end(tmp):
        state, lines = _flow()
        T = lines.T
        g = globals()
        MIS = ("Specs repo: NOT COMMITTED — SPECS_PATH is misplaced, or the run's environment no longer matches the one "
               "it recorded; see the notice below")
        BLOCKED = "Specs repo: NOT COMMITTED — see the notice below"
        NOTHING = "Specs repo: no session artifacts to commit"
        FIELDS = {"print", "line", "row", "sha7", "files", "branch", "pushed", "next", "record", "error"}

        def files(n):
            return "1 file" if n == 1 else "%d files" % n

        def pushed_default(sha7, specs, n=1):
            return ("Specs repo: committed %s (%s) on main — pushed straight to main, and no pull request was opened: this "
                    "plugin lands its session files there without review; to land them through a pull request of your own "
                    "instead, turn on session-branch mode (§8) with git -C \"%s\" config workflows.sessionBranch true — where a "
                    "container mounts this repository's .git/config read-only, run it on the host" % (sha7, files(n), specs))

        def refused_tail(branch, specs, record_text, clear, day):
            return ("to land the commits on local %s, put them on a branch of their own and open a pull request from it — "
                    "git -C \"%s\" branch --no-track session-files-%s %s && git -C \"%s\" push -u origin session-files-%s — then, "
                    "standing on %s, git -C \"%s\" reset --keep origin/%s; once origin takes pushes to %s again, %s"
                    % (branch, specs, day, branch, specs, day, branch, specs, branch, branch, clear))

        def appended(paths_text):
            return "; the deliverable at %s remains uncommitted, as you asked" % paths_text

        def plugin_world(name, pushed=True):
            r, env = world(tmp, name)
            r.git("switch", "-q", "-c", PLUGIN)
            if pushed:
                r.git("push", "-q", "-u", "origin", PLUGIN)
            return r, env

        # e_nothing
        r, env = world(tmp, "e-nothing")
        seed(env, "/create-ard")
        got = run_end(env, "/create-ard")
        check(got["_rc"] == 0 and got.get("row") == "nothing" and got.get("print") == [NOTHING] and got.get("line") == NOTHING
              and got.get("record") == "found" and got.get("pushed") is False and got.get("sha7") is None
              and got.get("next") is None and got.get("error") is None and record(env, "/create-ard") is None,
              "e_nothing: a clean tree is nothing to commit, the record removed (%r)" % got)
        check({k for k in got if not k.startswith("_")} == FIELDS, "e_nothing: the full field set (%r)" % sorted(got))

        # e_pushed_default
        r, env = world(tmp, "e-pushed-default")
        seed(env, "/create-ard")
        r.write(RESUME, "resume\n")
        got = run_end(env, "/create-ard", "--commit-key", "ACME-1")
        h = head(r)
        want = pushed_default(h[:7], r.path)
        check(got["_rc"] == 0 and got.get("row") == "pushed-default" and got.get("print") == [want] and got.get("line") == want
              and got.get("sha7") == h[:7] and got.get("files") == 1 and got.get("branch") == "main"
              and got.get("pushed") is True and record(env, "/create-ard") is None,
              "e_pushed_default: committed, pushed straight to main, (1 file) (%r)" % got)
        check(r.git("log", "-1", "--format=%s") == "ACME-1 Add dev-workflows session artifacts (/create-ard)"
              and "Co-Authored-By" not in r.git("log", "-1", "--format=%B"),
              "e_pushed_default: the subject carries the key and no trailer (%r)" % r.git("log", "-1", "--format=%B"))
        check(on_origin(r) == h and r.git("status", "--porcelain") == "", "e_pushed_default: origin/main holds it, the tree clean")
        r.write(RESUME, "resume 2\n")
        seed(env, "/create-ard")
        got = run_end(env, "/create-ard")
        check(got.get("row") == "pushed-default"
              and r.git("log", "-1", "--format=%s") == "NOISSUE Add dev-workflows session artifacts (/create-ard)",
              "e_pushed_default: no --commit-key opens the subject NOISSUE (%r)" % got)

        # e_pushed_plugin
        r, env = plugin_world("e-pushed-plugin")
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "resume\n")
        got = run_end(env, "/create-prd", "--commit-key", "ACME-1")
        h = head(r)
        check(got.get("row") == "pushed-plugin" and got.get("print") == ["Specs repo: committed %s (1 file) on %s — pushed"
                                                                          % (h[:7], PLUGIN)]
              and on_origin(r, PLUGIN) == h and got.get("branch") == PLUGIN, "e_pushed_plugin (%r)" % got)
        r, env = plugin_world("e-pushed-plugin-no-upstream", pushed=False)
        r.git("push", "-q", "origin", PLUGIN)
        r.write(RESUME, "resume\n")
        got = run_end(env, "/create-prd")
        check(got.get("row") == "pushed-plugin" and on_origin(r, PLUGIN) == head(r)
              and r.git("config", "--get", "branch.%s.merge" % PLUGIN, check=False) == "refs/heads/" + PLUGIN,
              "e_pushed_plugin: a branch pushed with no upstream is pushed with -u (%r)" % got)

        # e_not_ours
        r, env = world(tmp, "e-not-ours")
        r.git("switch", "-q", "-c", "feature/x")
        block = lines.fill("g2", {"<SPECS_PATH>": r.path, "<branch>": "feature/x", "<default>": "main"})
        seed(env, "/specify", guard="G2", guard_block=block, branch="feature/x")
        r.write(RESUME, "r\n")
        got = run_end(env, "/specify")
        h = head(r)
        want = ("Specs repo: committed %s (1 file) on feature/x — not pushed: this plugin pushes only the default branch and "
                "the branches it creates, so feature/x is yours to push; the artifacts reach the maintainer when you push or "
                "merge it" % h[:7])
        check(got.get("row") == "not-ours" and got.get("print") == [want, block] and on_origin(r, "feature/x") is None,
              "e_not_ours: the row, then G2's block verbatim (%r)" % got)

        # e_no_remote
        r, env = world(tmp, "e-no-remote")
        r.git("remote", "remove", "origin")
        r.write(RESUME, "r\n")
        got = run_end(env, "/feedback")
        check(got.get("record") == "missing" and got.get("row") == "no-remote" and got.get("print") == [
            "Specs repo: committed %s (1 file) on main — not pushed: this specs repo has no origin remote" % head(r)[:7]],
              "e_no_remote (%r)" % got)

        # e_elsewhere
        r, env = world(tmp, "e-elsewhere")
        r.git("config", "branch.main.pushRemote", "fork")
        for remote in ("fork", "upstream"):
            if remote == "upstream":
                r.git("config", "--unset", "branch.main.pushRemote")
                r.git("config", "remote.pushDefault", "upstream")
            seed(env, "/feedback")
            r.write(RESUME, "r %s\n" % remote)
            got = run_end(env, "/feedback")
            want = ("Specs repo: committed %s (1 file) on main — not pushed: your git configuration pushes main to %s, not "
                    "to origin, which is the remote this plugin reads; push it where it belongs yourself" % (head(r)[:7], remote))
            check(got.get("row") == "elsewhere" and got.get("print") == [want] and on_origin(r) != head(r),
                  "e_elsewhere: %s (%r)" % (remote, got))

        # e_remote_deleted
        r, env = plugin_world("e-remote-deleted")
        subprocess.run(["git", "-C", r.bare, "update-ref", "-d", "refs/heads/" + PLUGIN], check=True)
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-prd")
        want = ("Specs repo: committed %s (1 file) on %s — not pushed: origin has no %s any more, so it was renamed or "
                "deleted there, and this step does not recreate it; the commit stays on local %s"
                % (head(r)[:7], PLUGIN, PLUGIN, PLUGIN))
        check(got.get("row") == "remote-deleted" and got.get("print") == [want] and on_origin(r, PLUGIN) is None,
              "e_remote_deleted: a plugin branch origin deleted (%r)" % got)
        r, env = world(tmp, "e-remote-deleted-default")
        subprocess.run(["git", "-C", r.bare, "update-ref", "-d", "refs/heads/main"], check=True)
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard")
        want = ("Specs repo: committed %s (1 file) on main — not pushed: origin has no main any more, so it was renamed or "
                "deleted there, and this step does not recreate it; the commit stays on local main; if origin renamed it, "
                "git -C \"%s\" remote set-head origin --auto names the new one" % (head(r)[:7], r.path))
        check(got.get("row") == "remote-deleted" and got.get("print") == [want] and on_origin(r) is None,
              "e_remote_deleted: the default branch's form, with its set-head tail (%r)" % got)

        # e_origin_lacks
        r, env = plugin_world("e-origin-lacks", pushed=False)
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-prd")
        want = ("Specs repo: committed %s (1 file) on %s — not pushed: origin has no %s, and this plugin puts a branch of "
                "its own there only by handing off its deliverable; the commit stays on local %s until a later handoff of "
                "%s pushes the branch, or you run git -C \"%s\" push -u origin %s"
                % (head(r)[:7], PLUGIN, PLUGIN, PLUGIN, PLUGIN, r.path, PLUGIN))
        check(got.get("row") == "origin-lacks" and got.get("print") == [want] and on_origin(r, PLUGIN) is None,
              "e_origin_lacks (%r)" % got)

        # e_refused_before
        r, env = plugin_world("e-refused-before")
        pushed_tip = head(r)
        rec_file = os.path.join(r.path, ".git", "workflows", "push-refused", "prd", "ACME-1-x")
        os.makedirs(os.path.dirname(rec_file))

        def refused_before(sha7, date, record_text, clear, day):
            return ("Specs repo: committed %s (1 file) on %s — not pushed: origin refused pushes to %s on %s (%s), and every "
                    "commit since stays on local %s; " % (sha7, PLUGIN, PLUGIN, date, record_text, PLUGIN)
                    + refused_tail(PLUGIN, r.path, record_text, clear, day))

        for body, date in (("2026-11-01\n", "2026-11-01"), ("", "an earlier run")):
            with open(rec_file, "w", encoding="utf-8") as fh:
                fh.write(body)
            seed(env, "/create-prd", branch=PLUGIN)
            r.write(RESUME, "r %s\n" % date)
            got, days, _ = dated(lambda: run_end(env, "/create-prd"))
            check(got.get("row") == "refused-before"
                  and any(got.get("print") == [refused_before(head(r)[:7], date, rec_file, "rm \"%s\"" % rec_file, d)]
                          for d in days)
                  and on_origin(r, PLUGIN) == pushed_tip,
                  "e_refused_before: the record file holding %r names %s and its path (%r)" % (body, date, got))
        os.remove(rec_file)
        key = "branch.%s.workflowsPushRefused" % PLUGIN
        r.git("config", key, "2026-11-02")
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r config\n")
        got, days, _ = dated(lambda: run_end(env, "/create-prd"))
        check(got.get("row") == "refused-before" and any(got.get("print") == [refused_before(
            head(r)[:7], "2026-11-02", key, "git -C \"%s\" config --unset %s" % (r.path, key), d)] for d in days)
              and "rm \"" not in got["line"],
              "e_refused_before: the configuration-key form names the key and its config --unset (%r)" % got)

        # e_push_refused
        r, env = plugin_world("e-push-refused")
        hook(os.path.join(r.bare, "hooks", "pre-receive"), "echo refused by policy >&2\nexit 1\n")
        rec_file = os.path.join(r.path, ".git", "workflows", "push-refused", "prd", "ACME-1-x")
        opening = ("Specs repo: committed %s (1 file) on %s — push REFUSED by origin (pre-receive hook declined): a rule "
                   "there takes no push of %s, ")
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r\n")
        got, days, ldays = dated(lambda: run_end(env, "/create-prd"))
        want = [[opening % (head(r)[:7], PLUGIN, PLUGIN) + "so this is recorded and no later run pushes it; "
                 + refused_tail(PLUGIN, r.path, rec_file, "rm \"%s\"" % rec_file, d)] for d in days]
        check(got.get("row") == "push-refused" and got.get("print") in want and got.get("pushed") is False
              and os.path.isfile(rec_file) and open(rec_file, encoding="utf-8").read() in [d + "\n" for d in ldays],
              "e_push_refused: refused, the record file written under the common git directory with today's date (%r)" % got)
        shutil.rmtree(os.path.join(r.path, ".git", "workflows"))
        with open(os.path.join(r.path, ".git", "workflows"), "w", encoding="utf-8") as fh:
            fh.write("a file where the record's directory would go\n")
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r2\n")
        got, days, ldays = dated(lambda: run_end(env, "/create-prd"))
        want = [[opening % (head(r)[:7], PLUGIN, PLUGIN) + "so this is recorded and no later run pushes it; "
                 + refused_tail(PLUGIN, r.path, key, "git -C \"%s\" config --unset %s" % (r.path, key), d)] for d in days]
        check(got.get("row") == "push-refused" and got.get("print") in want and r.git("config", "--get", key) in ldays,
              "e_push_refused: the file cannot be written, so the configuration key is (%r)" % got)
        r.git("config", "--unset", key)
        lock = os.path.join(r.path, ".git", "config.lock")
        open(lock, "w").close()
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r3\n")
        got = run_end(env, "/create-prd")
        os.remove(lock)
        line = got.get("line") or ""
        check(got.get("row") == "push-refused" and line.startswith(opening % (head(r)[:7], PLUGIN, PLUGIN)
                                                                     + "but this could not be recorded (")
              and line.endswith(", the configuration write's), so a later run pushes %s again" % PLUGIN)
              and "to land the commits" not in line and "rm \"" not in line
              and r.git("config", "--get", key, check=False) == "",
              "e_push_refused: neither can be written, so the row says so and names no remedy (%r)" % got)

        # e_scope
        r, env = world(tmp, "e-scope")
        r.write("notes.md", "n\n")
        user = r.commit_all("Add notes")
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard")
        want = ("Specs repo: committed %s (1 file) on main — not pushed: the push would also publish commits that are not "
                "this plugin's session-file commits, the oldest %s Add notes, which carries notes.md; push main once they "
                "are ready to go, and the artifacts go with them" % (head(r)[:7], user[:7]))
        check(got.get("row") == "scope" and got.get("print") == [want] and on_origin(r) != head(r),
              "e_scope: the user's unpushed commit, its sha7, subject and path (%r)" % got)
        r, env = world(tmp, "e-scope-merge")
        r.git("switch", "-q", "-c", "side")
        r.write("specifications/PRD-ACME-1-x/dev-workflows/feedback/x.md", "f\n")
        r.commit_all("side feedback")
        r.git("switch", "-q", "main")
        r.git("merge", "-q", "--no-ff", "-m", "Merge side", "side")
        merge = head(r)
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard")
        check(got.get("row") == "scope" and got.get("line") == (
            "Specs repo: committed %s (1 file) on main — not pushed: the push would also publish commits that are not this "
            "plugin's session-file commits, the oldest %s Merge side, which is a merge commit; push main once they are "
            "ready to go, and the artifacts go with them" % (head(r)[:7], merge[:7])),
              "e_scope: a merge commit (%r)" % got)
        generating = ("echo gen > generated.txt\necho g2 > gen2.txt\ngit add generated.txt gen2.txt\n")

        def hook_row(sha7):
            # git lists a commit's paths in byte order, gen2.txt before generated.txt, and the first is the one named
            return ("Specs repo: committed %s (3 files) on main — not pushed: a pre-commit hook added gen2.txt, and 1 more "
                    "to this commit, so it carries more than this plugin's session files; check what the hook added before "
                    "you push main" % sha7)

        def hook_line(sha7):
            return "Specs repo: generated.txt is now committed in %s, put there by a pre-commit hook, and not pushed" % sha7

        r, env = world(tmp, "e-scope-hook")
        hook(os.path.join(r.path, ".git", "hooks", "pre-commit"), generating)
        r.write("generated.txt", "mine\n")
        block = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 1, "<path list>": "generated.txt"})
        seed(env, "/specify", guard="G1", guard_block=block, guard_paths=["generated.txt"])
        r.write(RESUME, "r\n")
        got = run_end(env, "/specify")
        h = head(r)
        check(got.get("row") == "scope" and got.get("print") == [hook_row(h[:7]), block, hook_line(h[:7])]
              and on_origin(r) != h, "e_scope: the hook variant, the block, then the hook line (%r)" % got)
        check(r.git("status", "--porcelain") == "",
              "e_scope: the index is brought back in step with HEAD after the hook (%r)" % r.git("status", "--porcelain"))
        r, env = world(tmp, "e-scope-hook-declined")
        hook(os.path.join(r.path, ".git", "hooks", "pre-commit"), generating)
        r.write(RESUME, "r\n")
        got = run_end(env, "/specify", "--declined", "generated.txt")
        h = head(r)
        check(got.get("row") == "scope" and got.get("print") == [hook_row(h[:7]), hook_line(h[:7])],
              "e_scope: a hook path the declined paths name gets the hook line, and no append now it is committed (%r)" % got)
        r, env = world(tmp, "e-scope-hook-plain")
        hook(os.path.join(r.path, ".git", "hooks", "pre-commit"), generating)
        r.write(RESUME, "r\n")
        got = run_end(env, "/specify")
        check(got.get("row") == "scope" and got.get("print") == [hook_row(head(r)[:7])],
              "e_scope: no hook line where neither the block nor the declined paths name a hook path (%r)" % got)

        # e_push_failed
        r, env = world(tmp, "e-push-failed")
        missing = os.path.join(tmp, "e-push-failed-missing.git")
        r.git("remote", "set-url", "origin", missing)
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard")
        want = ("Specs repo: committed %s (1 file) on main — push FAILED (fatal: '%s' does not appear to be a git "
                "repository); the commit is local and a later run retries it" % (head(r)[:7], missing))
        check(got.get("row") == "failed" and got.get("print") == [want] and got.get("pushed") is False,
              "e_push_failed: git's reason (%r)" % got)

        # e_locked
        r, env = world(tmp, "e-locked")
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        h = head(r)
        lock = os.path.join(r.path, ".git", "index.lock")
        open(lock, "w").close()
        got = run_end(env, "/create-ard")
        staged = r.git("diff", "--cached", "--name-only")
        os.remove(lock)
        check(got.get("row") == "locked" and got.get("print") == [
            "Specs repo: skipped — another session holds the repo (index.lock); the next run picks the artifacts up"]
              and staged == "" and head(r) == h, "e_locked: nothing staged, nothing committed (%r)" % got)

        # e_commit_failed
        r, env = world(tmp, "e-commit-failed")
        hook(os.path.join(r.path, ".git", "hooks", "pre-commit"), "echo hook says no >&2\nexit 1\n")
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        h = head(r)
        got = run_end(env, "/create-ard")
        check(got.get("row") == "commit-failed" and got.get("print") == [
            "Specs repo: NOT COMMITTED — the commit failed (hook says no); the artifacts stay staged, and a later run commits "
            "them once git accepts the commit (a merge concluded, a hook satisfied)"]
              and head(r) == h and r.git("diff", "--cached", "--name-only") == RESUME,
              "e_commit_failed: the hook's output, the session file still staged (%r)" % got)

        # e_blocked
        r, env = world(tmp, "e-blocked")
        h = head(r)
        r.git("switch", "-q", "--detach")

        def g0_on(r, h, days):
            """G0's block as end renders it, one per day of <days> (dated)."""
            return [lines.fill("g0", {"<SPECS_PATH>": r.path, "<sha7>": h[:7], "<YYYY-MM-DD>": d, "<branch>": "main"})
                    for d in days]
        g0 = g0_on(r, h, [utc_day()])[0]  # seeded: end prints the block the record holds, never one it renders
        seed(env, "/specify", specs_git="blocked", guard="G0", guard_block=g0, branch=None)
        r.write(RESUME, "r\n")
        got = run_end(env, "/specify")
        check(got.get("row") == "blocked" and got.get("print") == [BLOCKED, g0] and head(r) == h
              and record(env, "/specify") is None, "e_blocked: a record carrying blocked repeats G0's block (%r)" % got)
        got, days, _ = dated(lambda: run_end(env, "/specify", "--no-preflight"))
        check(got.get("record") == "missing" and got.get("row") == "blocked"
              and got.get("print") in [[BLOCKED, b] for b in g0_on(r, h, days)]
              and head(r) == h and "?? " + RESUME in r.git("status", "--porcelain", "--untracked-files=all"),
              "e_blocked: no record, a detached HEAD and something to stage prints G0's block the first time (%r)" % got)
        os.remove(os.path.join(r.path, RESUME))
        got = run_end(env, "/specify", "--no-preflight")
        check(got.get("row") == "nothing" and got.get("print") == [NOTHING], "e_blocked: nothing to stage is nothing (%r)" % got)

        # e_declined_blocked: §6's declined append on both blocked rows, before G0's block
        r, env = world(tmp, "e-declined-blocked")
        h = head(r)
        r.git("switch", "-q", "--detach")
        ard = "specifications/PRD-ACME-1-x/ard.md"
        r.write(ard, "ard\n")
        r.write(RESUME, "r\n")
        g0 = g0_on(r, h, [utc_day()])[0]
        seed(env, "/specify", specs_git="blocked", guard="G0", guard_block=g0, branch=None, declined=[ard])
        got = run_end(env, "/specify")
        check(got.get("row") == "blocked" and got.get("print") == [BLOCKED + appended(ard), g0] and head(r) == h
              and record(env, "/specify") is None,
              "e_declined_blocked: a record carrying blocked names the declined path, then G0's block (%r)" % got)
        got, days, _ = dated(lambda: run_end(env, "/specify", "--no-preflight", "--declined", ard))
        check(got.get("record") == "missing" and got.get("row") == "blocked"
              and got.get("print") in [[BLOCKED + appended(ard), b] for b in g0_on(r, h, days)] and head(r) == h,
              "e_declined_blocked: on a detached HEAD with no preflight, the --declined path, then G0's block (%r)" % got)
        # ... and only where --specs still names the repository the start checked (§6): the review's two reproductions,
        # --specs "" from a cwd that is no repository and from another repository holding the path dirty, and --specs
        # naming that other repository -- each the blocked line and G0's block, exit 0, no append
        nowhere = os.path.join(tmp, "e-declined-blocked-nowhere")
        os.makedirs(nowhere)
        other = new_repo(tmp, "e-declined-blocked-other")
        other.write(ard, "theirs\n")
        for label, specs, cwd in (("--specs \"\" from no repository", "", nowhere),
                                  ("--specs \"\" from another repository", "", other.path),
                                  ("--specs naming another repository", other.path, None)):
            seed(env, "/specify", specs_git="blocked", guard="G0", guard_block=g0, branch=None, declined=[ard])
            got = cli("--specs", specs, "end", "--command", "/specify", env=env, cwd=cwd)
            check(got["_rc"] == 0 and got.get("row") == "blocked" and got.get("print") == [BLOCKED, g0]
                  and record(env, "/specify") is None,
                  "e_declined_blocked: %s, the blocked line and G0's block alone (%r)" % (label, got))

        # e_declined_misrooted: the misrooted row takes no declined append, and runs no git status in the wrong path
        r, env = world(tmp, "e-declined-misrooted")
        wrong = os.path.join(tmp, "e-declined-misrooted-wrong")
        os.makedirs(wrong)
        notice = ["SPECS_PATH_INSIDE_TREE: the notice the run's start printed"]
        seed(env, "/specify", specs_git="misrooted", misrooted_notice=notice, declined=[PRD], specs=wrong)
        got = run_end(env, "/specify", specs=wrong)
        check(got["_rc"] == 0 and got.get("row") == "misrooted" and got.get("print") == [MIS] + notice
              and record(env, "/specify") is None,
              "e_declined_misrooted: the row and its notice alone, though git status cannot run there (%r)" % got)

        # e_misrooted
        r, env = world(tmp, "e-misrooted")
        notice = ["SPECS_PATH_INSIDE_TREE: the notice the run's start printed", "Misrooted runs left: what it left"]
        seed(env, "/specify", specs_git="misrooted", misrooted_notice=notice)
        r.write(RESUME, "r\n")
        h = head(r)
        got = run_end(env, "/specify")
        check(got.get("row") == "misrooted" and got.get("print") == [MIS] + notice and head(r) == h
              and record(env, "/specify") is None, "e_misrooted: the record's notice, verbatim (%r)" % got)
        changed = ("Environment changed: started in SPECS_PATH=/a (origin none), REPOS_PATH=unset, now SPECS_PATH=/b "
                   "(origin none), REPOS_PATH=unset — nothing more is committed, handed off or recorded here, and what this "
                   "run already wrote stays where it is. Re-run in the container the run started in.")
        got = run_end(env, "/specify", "--no-preflight", "--misrooted-stdin", stdin=(changed + "\n").encode("utf-8"))
        check(got.get("record") == "missing" and got.get("row") == "misrooted" and got.get("print") == [MIS, changed]
              and head(r) == h, "e_misrooted: --misrooted-stdin's notice, verbatim (%r)" % got)
        got = run_end(env, "/specify", "--no-preflight", "--misrooted-stdin", stdin=b"")
        check(got.get("row") == "misrooted" and got.get("print") == [MIS] and head(r) == h,
              "e_misrooted: empty stdin is the row and nothing after it (%r)" % got)

        # e_env_changed
        r, env = world(tmp, "e-env-changed")
        recorded = env_line(r.path)
        r.write(RESUME, "r\n")
        h = head(r)

        def env_changed(now):
            return ("Environment changed: started in %s, now %s — nothing more is committed, handed off or recorded here, "
                    "and what this run already wrote stays where it is. Re-run in the container the run started in."
                    % (recorded[len("Environment: "):], now[len("Environment: "):]))

        seed(env, "/create-ard")
        got = run_end(env, "/create-ard", specs="")
        check(got.get("record") == "found" and got.get("row") == "misrooted"
              and got.get("print") == [MIS, env_changed(env_line(""))] and head(r) == h,
              "e_env_changed: --specs \"\" against a recorded path (%r)" % got)
        other = new_repo(tmp, "e-env-other")
        seed(env, "/create-ard")
        got = run_end(env, "/create-ard", specs=other.path)
        check(got.get("row") == "misrooted" and got.get("print") == [MIS, env_changed(env_line(other.path))]
              and head(r) == h and other.git("log", "--format=%s") == "init",
              "e_env_changed: another repository (%r)" % got)
        seed(env, "/create-ard", env_line=recorded.partition("), REPOS_PATH=")[0] + "), REPOS_PATH=/repos/elsewhere")
        got = run_end(env, "/create-ard")
        check(got.get("record") == "found" and got.get("row") == "pushed-default" and on_origin(r) == head(r) != h,
              "e_env_changed: a line differing only in its REPOS_PATH half commits (%r)" % got)

        # e_d3_below_top
        r, env = world(tmp, "e-d3")
        r.write("specs/specifications/PRD-ACME-1-x/prd.md", "---\nkind: prd\nkey: ACME-1\n---\n")
        r.commit_all("a nested specs tree")
        r.write("specs/specifications/PRD-ACME-1-x/dev-workflows/resume.md", "r\n")
        h = head(r)
        specs = os.path.join(r.path, "specs")
        got = run_end(env, "/create-ard", "--no-preflight", specs=specs)
        want = ("Specs preflight: SPECS_PATH is %s, below the top level of its repository (%s) — a specs tree inside a "
                "larger repository is unsupported, because this plugin switches branches and commits in the repository "
                "SPECS_PATH belongs to, so this run switches and commits nothing there; set SPECS_PATH to a dedicated "
                "specs repository's top level." % (specs, r.git("rev-parse", "--show-toplevel")))
        check(got.get("record") == "missing" and got.get("row") == "misrooted" and got.get("print") == [MIS, want]
              and head(r) == h, "e_d3_below_top: the below-top-level notice, nothing committed (%r)" % got)

        # e_declined_only
        r, env = world(tmp, "e-declined-only")
        ard = "specifications/PRD-ACME-1-x/ard.md"
        got = cli("declined", "--command", "/create-ard", "--path", ard, env=env)
        r.write(ard, "ard\n")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard")
        check(got.get("record") == "declined-only" and got.get("row") == "pushed-default"
              and got.get("line") == pushed_default(head(r)[:7], r.path) + appended(ard)
              and on_origin(r) == head(r) and record(env, "/create-ard") is None,
              "e_declined_only: the no-preflight path, the commit made, the declined append (%r)" % got)

        # e_silent
        plain = os.path.join(tmp, "e-silent-plain")
        os.makedirs(plain)
        env = {"HOME": os.path.join(tmp, "home-e-silent"), "CLAUDE_CODE_SESSION_ID": "e-silent", "SPECS_PATH": plain}
        os.makedirs(env["HOME"])
        got = run_end(env, "/feedback")
        check(got["_rc"] == 0 and got.get("row") == "silent" and got.get("print") == [] and got.get("line") is None
              and got.get("record") == "missing", "e_silent: no repository and no flag prints nothing (%r)" % got)

        # e_declined
        r, env = world(tmp, "e-declined")
        r.git("rm", "-q", PRD)
        r.git("commit", "-q", "-m", "drop the PRD")
        r.git("push", "-q", "origin", "main")
        ab = "specifications/PRD-ACME-1-x/a b.md"
        r.write(PRD, "prd\n")
        r.write(ab, "ab\n")
        seed(env, "/create-prd", declined=[PRD, ab])
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-prd")
        check((got.get("line") or "").endswith(appended("%s, %s" % (PRD, ab))),
              "e_declined: both declined paths, in the record's order (%r)" % got)
        r.git("add", PRD)
        r.git("commit", "-q", "-m", "ACME-1 the PRD, committed by hand")
        seed(env, "/create-prd", declined=[PRD, ab])
        r.write(RESUME, "r2\n")
        got = run_end(env, "/create-prd")
        check((got.get("line") or "").endswith(appended(ab)), "e_declined: only what is still uncommitted (%r)" % got)
        four = [ab, "specifications/PRD-ACME-1-x/c.md", "specifications/PRD-ACME-1-x/zahlungsauslösung.md",
                "specifications/PRD-ACME-1-x/d e.md"]
        for p in four[1:]:
            r.write(p, "x\n")
        seed(env, "/create-prd", declined=four)
        r.write(RESUME, "r3\n")
        got = run_end(env, "/create-prd")
        check((got.get("line") or "").endswith(appended("4 files under specifications/PRD-ACME-1-x")),
              "e_declined: four paths in one folder (%r)" % got)
        r, env = world(tmp, "e-declined-flag")
        r.git("rm", "-q", PRD)
        r.git("commit", "-q", "-m", "drop the PRD")
        r.git("push", "-q", "origin", "main")
        r.write(PRD, "prd\n")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-prd", "--declined", PRD)
        check(got.get("record") == "missing" and got.get("line") == pushed_default(head(r)[:7], r.path) + appended(PRD),
              "e_declined: no record and --declined (%r)" % got)

        # e_two_sessions
        r, env = world(tmp, "e-two")
        e1, e2 = dict(env, CLAUDE_CODE_SESSION_ID="s1"), dict(env, CLAUDE_CODE_SESSION_ID="s2")
        seed(e1, "/specify", specs_git="misrooted", misrooted_notice=["s1's notice"])
        r.write("notes.md", "n\n")
        block = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 1, "<path list>": "notes.md"})
        seed(e2, "/specify", guard="G1", guard_block=block, guard_paths=["notes.md"])
        with in_env(e1):
            s1_file = state.path("s1", "/specify")
        before = open(s1_file, encoding="utf-8").read()
        r.write(RESUME, "r\n")
        got = run_end(e2, "/specify")
        check(got.get("row") == "pushed-default" and got.get("print") == [pushed_default(head(r)[:7], r.path), block]
              and open(s1_file, encoding="utf-8").read() == before and record(e2, "/specify") is None,
              "e_two_sessions: s2 commits with its own block; s1's record untouched (%r)" % got)

        # e_stale_no_preflight (P37): a record a start of the script made, at <command>.json, is ignored and never
        # written or removed by an end with no start and no --started -- it may be another run's -- the commit made, and
        # the end's own record, kept at a derived path, removed
        r, env = world(tmp, "e-stale")
        seed(env, "/create-ard", specs_git="misrooted", misrooted_notice=["a stale run's notice"])
        sdir = os.path.join(env["HOME"], ".claude", "dev-workflows", "specs-git", env["CLAUDE_CODE_SESSION_ID"])
        stale = open(os.path.join(sdir, "create-ard.json"), "rb").read()
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard", "--no-preflight")
        check(got.get("record") == "ignored" and got.get("row") == "pushed-default" and on_origin(r) == head(r)
              and open(os.path.join(sdir, "create-ard.json"), "rb").read() == stale
              and sorted(os.listdir(sdir)) == ["create-ard.json"] and "a stale run's notice" not in got.get("print", []),
              "e_stale_no_preflight: the stale record ignored and left byte for byte, the commit made, the end's own "
              "record removed (%r)" % got)

        # e_missing_record
        r, env = world(tmp, "e-missing")
        r.write(RESUME, "r\n")
        got = run_end(env, "/feedback")
        check(got.get("record") == "missing" and got.get("row") == "pushed-default" and on_origin(r) == head(r)
              and record(env, "/feedback") is None, "e_missing_record: run as the no-preflight path (%r)" % got)

        # e_catch_up
        r, env = world(tmp, "e-catch-up")
        o = clone(r, "e-catch-up-other")
        o.write("other.md", "o\n")
        theirs = o.commit_all("NOISSUE another clone's change")
        o.git("push", "-q", "origin", "main")
        r.git("fetch", "-q", "origin")
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard")
        check(got.get("row") == "pushed-default" and r.git("rev-parse", "HEAD~1") == theirs and on_origin(r) == head(r)
              and got.get("print") == [pushed_default(head(r)[:7], r.path)],
              "e_catch_up: main fast-forwarded before the commit, the push lands (%r)" % got)
        o.git("pull", "-q", "--ff-only", "origin", "main")
        o.write("other2.md", "o\n")
        o.commit_all("NOISSUE another")
        o.git("push", "-q", "origin", "main")
        r.git("fetch", "-q", "origin")
        missing = os.path.join(tmp, "e-catch-up-missing.git")
        r.git("remote", "set-url", "origin", missing)
        seed(env, "/create-ard")
        r.write(RESUME, "r2\n")
        got = run_end(env, "/create-ard")
        check(got.get("row") == "failed" and len(got.get("print", [])) == 2 and got["print"][0] == (
            "Specs preflight: could not fast-forward main (fatal: '%s' does not appear to be a git repository); the run "
            "goes on from it as it stands" % missing) and got["print"][1] == got.get("line"),
              "e_catch_up: a failed catch-up prints its line before the outcome line (%r)" % got)

        # e_nonff
        r, env = world(tmp, "e-nonff")
        seed(env, "/create-ard")
        o = clone(r, "e-nonff-other")
        o.write("other.md", "o\n")
        o.commit_all("NOISSUE another clone's change")
        o.git("push", "-q", "origin", "main")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard")
        h = head(r)
        nxt = got.get("next") or {}
        rec = record(env, "/create-ard") or {}
        check(got["_rc"] == 0 and got.get("row") is None and got.get("print") == [] and got.get("line") is None
              and nxt.get("run", "").startswith("python3 ")
              and " --specs %s replay --for end --command /create-ard --branch main" % r.path in nxt.get("run", "")
              and "--set-upstream" not in nxt.get("run", "") and nxt.get("timeout_ms") == 420000
              and nxt.get("on_timeout") == nxt.get("run", "") + " --timed-out" and got.get("sha7") == h[:7],
              "e_nonff: next names the replay, in a call of its own (%r)" % got)
        check(rec.get("stage") == "end-replay" and (rec.get("end_commit") or {}).get("sha7") == h[:7]
              and rec["end_commit"].get("branch") == "main" and rec["end_commit"].get("files") == 1
              and rec["end_commit"].get("paths") == [RESUME] and rec["end_commit"].get("hook_paths") == [],
              "e_nonff: the record holds end_commit at stage end-replay (%r)" % rec)
        r, env = plugin_world("e-nonff-upstream", pushed=False)
        r.git("push", "-q", "origin", PLUGIN)
        o = clone(r, "e-nonff-upstream-other")
        o.git("switch", "-q", PLUGIN)
        o.write("specifications/PRD-ACME-1-x/dev-workflows/feedback/o.md", "o\n")
        o.commit_all("NOISSUE another clone's feedback")
        o.git("push", "-q", "origin", PLUGIN)
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-prd")
        check((got.get("next") or {}).get("run", "").endswith(" --branch %s --set-upstream" % PLUGIN),
              "e_nonff: --set-upstream where the push carried -u (%r)" % got)

        # e_resume
        r, env = world(tmp, "e-resume")
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        real_check = g["push_check"]

        def killed(*args, **kw):
            raise KeyboardInterrupt

        stopped = False
        g["push_check"] = killed
        try:
            with in_env(env):
                end(r.path, "/create-ard")
        except KeyboardInterrupt:
            stopped = True
        finally:
            g["push_check"] = real_check
        h = head(r)
        count = r.git("rev-list", "--count", "HEAD")
        rec = record(env, "/create-ard") or {}
        check(stopped and (rec.get("end_commit") or {}).get("sha7") == h[:7] and on_origin(r) != h,
              "e_resume: stopped right after its commit, which the record holds (%r)" % rec)
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and got.get("sha7") == h[:7] and got.get("print") == [pushed_default(h[:7], r.path)]
              and r.git("rev-list", "--count", "HEAD") == count and on_origin(r) == h and record(env, "/create-ard") is None,
              "e_resume: the commit is not made again, the push lands (%r)" % got)
        r, env = world(tmp, "e-resume-after-push")
        subprocess.run(["git", "-C", r.bare, "config", "core.logAllRefUpdates", "true"], check=True)
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        real_push = g["push"]

        def push_then_killed(*args, **kw):
            real_push(*args, **kw)
            raise KeyboardInterrupt

        def updates():
            p = subprocess.run(["git", "-C", r.bare, "reflog", "show", "refs/heads/main"], stdout=subprocess.PIPE)
            return len(p.stdout.decode().splitlines())

        stopped = False
        g["push"] = push_then_killed
        try:
            with in_env(env):
                end(r.path, "/create-ard")
        except KeyboardInterrupt:
            stopped = True
        finally:
            g["push"] = real_push
        h = head(r)
        landed = updates()
        check(stopped and on_origin(r) == h and landed == 1, "e_resume_after_push: stopped right after its push landed")
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and got.get("sha7") == h[:7] and got.get("pushed") is True
              and updates() == landed and on_origin(r) == h and record(env, "/create-ard") is None,
              "e_resume_after_push: [up to date] reads as pushed, nothing pushed twice (%r)" % got)
        r.write(RESUME, "r stale\n")
        seed(env, "/create-ard", end_commit={"sha7": "0000000", "files": 1, "branch": "main", "paths": [RESUME],
                                             "hook_paths": []}, stage="end")
        with in_env(env):
            rec = state.load(env["CLAUDE_CODE_SESSION_ID"], "/create-ard")
            rec["updated"] = time.strftime(state.STAMP, time.gmtime(time.time() - 20 * 60))
            with open(state.path(env["CLAUDE_CODE_SESSION_ID"], "/create-ard"), "w", encoding="utf-8") as fh:
                json.dump(rec, fh)
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and got.get("sha7") == head(r)[:7] != "0000000"
              and on_origin(r) == head(r), "e_resume: an end_commit saved 20 minutes ago runs from step 1 (%r)" % got)

        # e_exit2
        r, env = world(tmp, "e-exit2")
        r.write(RESUME, "r\n")

        def snapshot():
            return (r.git("status", "--porcelain"), head(r), r.git("for-each-ref"),
                    subprocess.run(["git", "-C", r.bare, "for-each-ref"], stdout=subprocess.PIPE).stdout)

        before = snapshot()
        got = cli("--specs", r.path, "end", "--command", "/create-ard",
                  env={k: v for k, v in env.items() if k != "CLAUDE_CODE_SESSION_ID"}, stdin=b"")
        check(one_not_run_line(got) and snapshot() == before and not os.path.exists(os.path.join(env["HOME"], ".claude")),
              "e_exit2: no session variable, exit 2, one line, nothing changed (%r)" % got)
        for args, what in (((r.path, "/create-ard", "--commit-key", "acme-1"), "a lower-case key"),
                           ((r.path, "/create-ard", "--commit-key", "ACME-1\n"), "a key with a newline"),
                           ((r.path, "create-ard"), "a command without its slash"),
                           ((r.path, "/create-ard", "--session-branch-created", "xyz"), "a creation that is no sha")):
            got = cli("--specs", args[0], "end", "--command", *args[1:], env=env, stdin=b"")
            check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: ") and snapshot() == before,
                  "e_exit2: %s is a usage exit 2 (%r)" % (what, got))
        got = cli("end", "--command", "/create-ard", env=env, stdin=b"")
        check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: "),
              "e_exit2: no --specs at all is a usage error (%r)" % got)
        lone = os.path.join(tmp, "e-exit2-lone")
        os.makedirs(lone)
        shutil.copy(me, os.path.join(lone, "specs-git.py"))
        shutil.copy(os.path.join(HERE, "session-branch.py"), os.path.join(lone, "session-branch.py"))
        got = cli("--specs", r.path, "end", "--command", "/create-ard", env=env, stdin=b"",
                  script=os.path.join(lone, "specs-git.py"))
        check(one_not_run_line(got) and "specs_git_state" in got["_err"] and snapshot() == before,
              "e_exit2: end without its modules exits 2 with one line naming the missing one (%r)" % got)
        real_catch_up = g["catch_up"]

        def unreadable(*args, **kw):
            raise NotRun("a read failed")

        raised = False
        g["catch_up"] = unreadable
        try:
            with in_env(env):
                end(r.path, "/create-ard")
        except NotRun:
            raised = True
        finally:
            g["catch_up"] = real_catch_up
        check(raised and snapshot() == before, "e_exit2: a failure before the first repository write raises, so exit 2")

        # e_error_after_write
        r, env = world(tmp, "e-error")
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")

        def boom(*args, **kw):
            raise RuntimeError("boom")

        g["push_check"] = boom
        try:
            with in_env(env):
                got = end(r.path, "/create-ard")
        finally:
            g["push_check"] = real_check
        want = ("Specs repo: NOT FINISHED — the terminal step stopped early (RuntimeError: boom); what it committed or pushed "
                "is as it left it, and the next run's preflight flushes the rest")
        check(got.get("error") == "RuntimeError: boom" and got.get("line") == want and got.get("print") == [want]
              and got.get("sha7") == head(r)[:7] and set(got) == FIELDS
              and r.git("log", "-1", "--format=%s") == "NOISSUE Add dev-workflows session artifacts (/create-ard)",
              "e_error_after_write: exit-0 result, error set, the commit made, the stopped line (%r)" % got)
        check(((record(env, "/create-ard") or {}).get("end_commit") or {}).get("sha7") == head(r)[:7],
              "e_error_after_write: the record stays, its end_commit for --resume (%r)" % record(env, "/create-ard"))

        # e_kill_in_push: a signal during the push, which sb.git_bounded turns into NotRun, keeps the record
        r, env = world(tmp, "e-kill-in-push")
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        real_bounded = sb.git_bounded

        def signalled_push(root, seconds, *args):
            if args and args[0] == "push":
                raise NotRun("git push ended by signal 15")
            return real_bounded(root, seconds, *args)

        sb.git_bounded = signalled_push
        try:
            with in_env(env):
                got = end(r.path, "/create-ard")
        finally:
            sb.git_bounded = real_bounded
        h = head(r)
        count = r.git("rev-list", "--count", "HEAD")
        check(got.get("error") == "git push ended by signal 15" and got.get("sha7") == h[:7] and on_origin(r) != h
              and ((record(env, "/create-ard") or {}).get("end_commit") or {}).get("sha7") == h[:7],
              "e_kill_in_push: end.stopped, the commit made and unpushed, the record kept (%r)" % got)
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and got.get("sha7") == h[:7] and got.get("print") == [pushed_default(h[:7], r.path)]
              and r.git("rev-list", "--count", "HEAD") == count and on_origin(r) == h and record(env, "/create-ard") is None,
              "e_kill_in_push: --resume pushes the first call's commit, nothing committed twice (%r)" % got)

        # e_kill_after_commit: no record, a kill between the commit and the save that names it
        r, env = world(tmp, "e-kill-after-commit")
        ard = "specifications/PRD-ACME-1-x/ard.md"
        r.write(ard, "ard\n")
        r.write(RESUME, "r\n")
        base = head(r)
        real_commit = g["commit_session_files"]

        def commit_then_killed(*args, **kw):
            real_commit(*args, **kw)
            raise KeyboardInterrupt

        stopped = False
        g["commit_session_files"] = commit_then_killed
        try:
            with in_env(env):
                end(r.path, "/create-ard", commit_key="ACME-1", register_rebuild="/x/register.py",
                    session_branch_created="abc1234", declined=[ard])
        except KeyboardInterrupt:
            stopped = True
        finally:
            g["commit_session_files"] = real_commit
        h = head(r)
        rec = record(env, "/create-ard") or {}
        pending = rec.get("end_commit") or {}
        check(stopped and h != base and rec.get("stage") == "end" and rec.get("started_by_script") is False
              and rec.get("declined") == [ard] and rec.get("commit_key") == "ACME-1"
              and rec.get("register_rebuild") == "/x/register.py" and rec.get("session_branch_created") == "abc1234"
              and "sha7" not in pending and pending.get("base") == base and pending.get("branch") == "main"
              and pending.get("staged") == {RESUME: r.git("rev-parse", "HEAD:" + RESUME)},
              "e_kill_after_commit: the record saved at the boundary, the commit about to be made in it (%r)" % rec)
        count = r.git("rev-list", "--count", "HEAD")
        got = run_end(env, "/create-ard", "--commit-key", "ACME-1", "--declined", ard, "--resume")
        check(got.get("row") == "pushed-default" and got.get("sha7") == h[:7]
              and got.get("line") == pushed_default(h[:7], r.path) + appended(ard)
              and r.git("rev-list", "--count", "HEAD") == count and on_origin(r) == h and record(env, "/create-ard") is None,
              "e_kill_after_commit: --resume finds the commit where it landed and pushes it (%r)" % got)
        r.write(RESUME, "r2\n")
        base = head(r)
        seed(env, "/create-ard", stage="end",
             end_commit={"branch": "main", "base": base, "staged": {RESUME: r.git("hash-object", RESUME)}})
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and r.git("rev-parse", "HEAD~1") == base and on_origin(r) == head(r),
              "e_kill_after_commit: a pending commit that was never made runs from step 1 (%r)" % got)
        base = head(r)
        r.write(RESUME, "r3\n")
        seed(env, "/create-ard", stage="end",
             end_commit={"branch": "main", "base": base, "staged": {RESUME: r.git("hash-object", RESUME)}})
        r.write("notes.md", "n\n")
        r.git("add", "notes.md")
        r.git("commit", "-q", "-m", "Add notes")
        user = head(r)
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "scope" and r.git("rev-parse", "HEAD~1") == user and got.get("sha7") == head(r)[:7],
              "e_kill_after_commit: a tip on the base that carries none of the staged paths is not the run's (%r)" % got)
        r, env = world(tmp, "e-kill-after-commit-same-path")
        r.write(RESUME, "mine\n")
        base = head(r)
        seed(env, "/create-ard", stage="end",
             end_commit={"branch": "main", "base": base, "staged": {RESUME: r.git("hash-object", RESUME)}})
        r.write(RESUME, "theirs\n")
        r.git("add", RESUME)
        r.git("commit", "-q", "-m", "a commit of the user's on the same path")
        user = head(r)
        r.write(RESUME, "mine\n")
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and r.git("rev-parse", "HEAD~1") == user and got.get("sha7") == head(r)[:7]
              and got.get("sha7") != user[:7] and on_origin(r) == head(r),
              "e_kill_after_commit: a tip on the base touching a staged path with other content is not the run's (%r)" % got)
        r, env = world(tmp, "e-kill-after-commit-removal")
        old = "specifications/PRD-ACME-1-x/dev-workflows/feedback/old.md"
        r.write(old, "old\n")
        r.commit_all("NOISSUE an earlier run's feedback")
        r.git("push", "-q", "origin", "main")
        os.remove(os.path.join(r.path, old))
        r.write(RESUME, "r\n")
        stopped = False
        g["commit_session_files"] = commit_then_killed
        try:
            with in_env(env):
                end(r.path, "/create-ard")
        except KeyboardInterrupt:
            stopped = True
        finally:
            g["commit_session_files"] = real_commit
        h = head(r)
        count = r.git("rev-list", "--count", "HEAD")
        pending = (record(env, "/create-ard") or {}).get("end_commit") or {}
        check(stopped and pending.get("staged") == {old: None, RESUME: r.git("rev-parse", "HEAD:" + RESUME)},
              "e_kill_after_commit: a staged removal is saved as no blob (%r)" % pending)
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and got.get("sha7") == h[:7] and got.get("files") == 2
              and r.git("rev-list", "--count", "HEAD") == count and on_origin(r) == h,
              "e_kill_after_commit: a removal matches the path's absence at the tip (%r)" % got)
        r.write(old, "old again\n")
        r.commit_all("NOISSUE the feedback again")
        r.git("push", "-q", "origin", "main")
        base = head(r)
        r.write(RESUME, "y\n")
        seed(env, "/create-ard", stage="end", end_commit={"branch": "main", "base": base,
                                                          "staged": {old: None, RESUME: r.git("hash-object", RESUME)}})
        r.git("add", RESUME)
        r.git("commit", "-q", "-m", "a commit of the user's with the same blob, the removed path kept")
        user = head(r)
        os.remove(os.path.join(r.path, old))
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and r.git("rev-parse", "HEAD~1") == user and got.get("sha7") == head(r)[:7]
              and got.get("sha7") != user[:7], "e_kill_after_commit: a tip still holding a removed path is not the run's (%r)" % got)
        r, env = world(tmp, "e-kill-after-commit-msg")
        hook(os.path.join(r.path, ".git", "hooks", "commit-msg"), "printf '\\nChange-Id: I0123456789\\n' >> \"$1\"\n")
        r.write(RESUME, "r\n")
        stopped = False
        g["commit_session_files"] = commit_then_killed
        try:
            with in_env(env):
                end(r.path, "/create-ard")
        except KeyboardInterrupt:
            stopped = True
        finally:
            g["commit_session_files"] = real_commit
        h = head(r)
        count = r.git("rev-list", "--count", "HEAD")
        check(stopped and r.git("log", "-1", "--format=%B").endswith("Change-Id: I0123456789") and on_origin(r) != h,
              "e_kill_after_commit: a commit-msg hook rewrote the message of the commit the kill followed")
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and got.get("sha7") == h[:7] and got.get("print") == [pushed_default(h[:7], r.path)]
              and r.git("rev-list", "--count", "HEAD") == count and on_origin(r) == h and record(env, "/create-ard") is None,
              "e_kill_after_commit: a rewritten message still resumes that commit, nothing committed twice (%r)" % got)

        # e_d3_signal
        r, env = world(tmp, "e-d3-signal")
        r.write(RESUME, "r\n")
        h = head(r)
        spec_dir = os.path.join(r.path, "specifications")
        got = run_end(env, "/create-ard", "--no-preflight", specs=spec_dir)
        stop = ("SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, which is itself a specifications/ directory — every folder "
                "lives under $SPECS_PATH/specifications/, so this run would look for and create folders in the wrong "
                "place; it wrote nothing under that path, and its cost and feedback are reported here instead. Set "
                "SPECS_PATH to %s where it is set, and re-run." % (spec_dir, os.path.realpath(r.path)))
        check(got.get("record") == "missing" and got.get("row") == "misrooted" and got.get("print") == [MIS, stop]
              and head(r) == h, "e_d3_signal: specs-root-check's one-line stop, nothing committed (%r)" % got)

        # e_g0_found: a record with no flag, HEAD detached since its start
        r, env = world(tmp, "e-g0-found")
        seed(env, "/specify")
        h = head(r)
        r.git("switch", "-q", "--detach")
        r.write(RESUME, "r\n")
        got, days, _ = dated(lambda: run_end(env, "/specify"))
        check(got.get("record") == "found" and got.get("row") == "blocked"
              and got.get("print") in [[BLOCKED, b] for b in g0_on(r, h, days)]
              and head(r) == h and record(env, "/specify") is None,
              "e_g0_found: a found record on a detached HEAD prints G0's block, nothing committed (%r)" % got)

        # e_resolve_default
        r, env = world(tmp, "e-resolve")
        check(resolve_default(r.path, False) == {"default": "main", "default_ref": "origin/main", "remote": "origin",
                                                 "offline": False}, "e_resolve_default: no origin/HEAD falls back to main")
        r.git("branch", "trunk")
        r.git("push", "-q", "origin", "trunk")
        r.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
        check(resolve_default(r.path, True) == {"default": "trunk", "default_ref": "origin/trunk", "remote": "origin",
                                                "offline": False}, "e_resolve_default: origin/HEAD names it, fetched")
        r.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/renamed")
        check(resolve_default(r.path, False)["default"] == "main",
              "e_resolve_default: origin/HEAD naming a ref that does not exist falls back")
        r.git("remote", "set-url", "origin", os.path.join(tmp, "e-resolve-missing.git"))
        check(resolve_default(r.path, True)["offline"] is True, "e_resolve_default: a failed fetch is offline")
        loc = new_repo(tmp, "e-resolve-local")
        check(resolve_default(loc.path, True) == {"default": "main", "default_ref": "refs/heads/main", "remote": "none",
                                                  "offline": False}, "e_resolve_default: no remote, the local ref, no fetch")
        loc.git("branch", "-m", "main", "master")
        check(resolve_default(loc.path, False)["default"] == "master", "e_resolve_default: then master")
        loc.git("branch", "-m", "master", "work")
        check(resolve_default(loc.path, False)["default"] == "work", "e_resolve_default: then the current branch")

        # e_key_grammar
        with open(ADDRESSING, encoding="utf-8") as fh:
            addressing = fh.read()
        section1 = addressing[addressing.index("## 1. Key grammar"):]
        fence = section1[section1.index("```\n") + 4:section1.index("\n```", section1.index("```\n") + 4)]
        check(fence == r"^[A-Z][A-Z0-9_]*(-\d+)+$" and "^" + KEY_RE.pattern.replace("[0-9]", r"\d") + "$" == fence,
              "e_key_grammar: KEY_RE is addressing §1's grammar, \\d spelt [0-9] (%r)" % fence)
        check(all(KEY_RE.fullmatch(k) for k in ("ACME-1", "ACME-90-01", "A_B2-7-1"))
              and not any(KEY_RE.fullmatch(k) for k in ("acme-1", "ACME", "ACME-1\n", "ACME-١", "ACME-1-")),
              "e_key_grammar: whole keys only, ASCII digits only")

        # e_push_status: push() over canned --porcelain output, for the statuses no local origin gives
        r, env = world(tmp, "e-push-status")
        rec_file = os.path.join(r.path, ".git", "workflows", "push-refused", "main")
        real_bounded = sb.git_bounded

        def canned(status_line, rc=1):
            out = ("To origin\n%s\nDone\n" % status_line) if status_line else ""
            return lambda root, seconds, *args: subprocess.CompletedProcess(["git"] + list(args), rc, out.encode(), b"")

        try:
            for reason in TRANSIENT:
                sb.git_bounded = canned("!\trefs/heads/main:refs/heads/main\t[remote rejected] (%s x)" % reason)
                got = push(r.path, "main", False)
                check(got["outcome"] == "failed" and got["reason"] == "[remote rejected] (%s x)" % reason
                      and got["recorded"] is None and not os.path.exists(rec_file),
                      "e_push_status: %r is a failed push, never a refusal (%r)" % (reason, got))
            sb.git_bounded = canned(None, 124)
            got = push(r.path, "main", False)
            check(got["outcome"] == "failed" and got["reason"] == T["text.push-capped"], "e_push_status: capped (%r)" % got)
            sb.git_bounded = canned("+\trefs/heads/main:refs/heads/main\taaaaaaa...bbbbbbb (forced update)", 0)
            check(push(r.path, "main", False)["outcome"] == "pushed", "e_push_status: + is pushed")
            sb.git_bounded = canned("!\trefs/heads/main:refs/heads/main\t[remote failure] (remote failed to report status)")
            got = push(r.path, "main", False)
            check(got["outcome"] == "failed" and got["reason"] == "[remote failure] (remote failed to report status)",
                  "e_push_status: another status is a failed push (%r)" % got)
            sb.git_bounded = canned("!\trefs/heads/main:refs/heads/main\t[remote rejected] (push declined due to "
                                    "repository rule violations)")
            got, _, ldays = dated(lambda: push(r.path, "main", False))
            check(got == {"outcome": "refused", "reason": "push declined due to repository rule violations",
                          "recorded": "file", "record": rec_file, "record_error": None}
                  and open(rec_file, encoding="utf-8").read() in [d + "\n" for d in ldays],
                  "e_push_status: a host's refusal is recorded (%r)" % got)
        finally:
            sb.git_bounded = real_bounded

        # e_canned: the rows whose facts no repository here produces
        base = {"sha7": "abc1234", "files": 2, "branch": "main", "default": "main", "specs": "/s"}
        got = _row_line(lines, "push-refused", dict(base, reason="r", record_kind="config",
                                                    record="branch.main.workflowsPushRefused"))
        check(got.endswith("once origin takes pushes to main again, git -C \"/s\" config --unset branch.main."
                           "workflowsPushRefused") and "so this is recorded" in got,
              "e_canned: push refused, recorded in the configuration key (%r)" % got)
        got = _row_line(lines, "push-refused", dict(base, reason="r", record_kind=None, record_error="e"))
        check(got == "Specs repo: committed abc1234 (2 files) on main — push REFUSED by origin (r): a rule there takes no "
              "push of main, but this could not be recorded (e, the configuration write's), so a later run pushes main again",
              "e_canned: push refused and unrecorded (%r)" % got)
        got = _row_line(lines, "failed", dict(base, reason=T["text.push-capped"]))
        check(got == "Specs repo: committed abc1234 (2 files) on main — push FAILED (the push did not finish within 60 s); "
              "the commit is local and a later run retries it", "e_canned: a capped push (%r)" % got)
        got = _row_line(lines, "scope", dict(base, subject="s", scope={"failed": {"sha": "f" * 40, "reason": "paths",
                                                                                   "path": None}}))
        check("the oldest fffffff s, which changes no file;" in got, "e_canned: a commit that changes no file (%r)" % got)
        got = _row_line(lines, "scope", dict(base, hook=["a.md"], scope={"failed": {"sha": "abc1234" + "0" * 33,
                                                                                     "reason": "paths", "path": "a.md"}}))
        check("a pre-commit hook added a.md to this commit" in got, "e_canned: the hook variant with one path (%r)" % got)

        # §4 step 1's landing at the run's end (STAY-2; S1, S2): each case a start, then an end, on world with
        # other_key -- HEAD on prd/B-2-y, which no key of the run (ACME-1) names -- and, unless a case says otherwise,
        # notes.md, which is not the plugin's, dirty, so G1 fires and the preflight stays (an unkeyed stay); the run's
        # own session file is written after the start. Each expected line is rendered from the pins, never by the code
        # under test.
        LB = "prd/B-2-y"
        SUBJECT = "%s Add dev-workflows session artifacts (%s)"
        FB = "specifications/PRD-ACME-1-x/dev-workflows/feedback/f.md"
        LEFT = "specifications/PRD-ACME-1-x/dev-workflows/feedback/left.md"
        FUP = "specifications/PRD-ACME-1-x/follow-ups.md"
        COST = "specifications/PRD-ACME-1-x/dev-workflows/cost/abcd1234.md"
        COST_BODY = "# Cost\n\n## 2026-11-10T10:00:00Z — /specify — draft\n\nbody\n"
        ENTRY = "## 2026-11-10 — /feedback — note\n\n%s\n"
        AX = "prd/A-1-x"
        KINDS = lines.placeholder("g1.landing.not_done", "<which no key")
        LANDED = lines.placeholder("app.landed", "<which no key")
        HELD_KIND = lines.placeholder("row.held", "<which no key")
        HELD_TAIL = lines.placeholder("row.held", "<held for")
        STUCK_KIND = lines.placeholder("row.held-stuck", "<which no key")
        CHECKED = lines.placeholder("reason.land.checked-out", "<the push of")
        UNKEYED = {"branch": LB, "kind": "unkeyed", "reason": "g1", "merged": False, "command": None}

        def case(name, fn):
            try:
                fn()
            except Exception as e:  # one case that crashes must not hide the others
                check(False, "%s crashed: %s: %s" % (name, type(e).__name__, str(e).strip()[:400]))

        def start_of(env, *args):
            return cli("--specs", env["SPECS_PATH"], "start", "--command", "/feedback", "--key", "ACME-1", *args, env=env)

        def lworld(name, notes=True, extra=()):
            """world, <extra> ((path, body) pairs) committed on main and pushed, then other_key; notes.md dirty where
            <notes>."""
            r, env = world(tmp, name)
            for p, body in extra:
                r.write(p, body)
            if extra:
                r.commit_all("ACME-1 Add more")
                r.git("push", "-q", "origin", "main")
            other_key(r, LB)
            if notes:
                r.write("notes.md", "n\n")
            return r, env

        def ref(r, name):
            return r.git("rev-parse", "--verify", "-q", name, check=False) or None

        def main_of(r):
            return ref(r, "refs/heads/main")

        def read(r, path):
            full = os.path.join(r.path, path)
            if not os.path.isfile(full):
                return None
            with open(full, encoding="utf-8", newline="") as fh:
                return fh.read()

        def gone(r, path):
            return not os.path.lexists(os.path.join(r.path, path))

        def changed(r, rev):
            return sorted(x for x in r.git("diff-tree", "--no-commit-id", "--name-only", "-r", rev).split("\n") if x)

        def show(r, rev, path):
            return r.git("show", "%s:%s" % (rev, path), check=False)

        def held(r):
            return held_entries(r.path)

        def held_refs(r):
            return r.git("for-each-ref", "--format=%(refname)", HELD_REF).split()

        def on_lb(r):
            return r.git("symbolic-ref", "--short", "HEAD") == LB

        def reflog_landed(r):
            return [x for x in r.git("reflog", "--format=%gs", "refs/heads/main").split("\n") if x.startswith("specs-git: landed")]

        def landed(r, n, branch=LB, kind="unkeyed", sha7=None, row=None):
            """The row the landing's commit takes on main -- pushed-default unless <row> gives another line's opening
            -- then app.landed for a stay of <kind> on <branch>."""
            line = row if row is not None else pushed_default(sha7 or (main_of(r) or "")[:7], r.path, n)
            return line + lines.fill("app.landed", {"<branch>": branch, "<default>": "main", LANDED: STAY_KINDS.index(kind)})

        def g1_plain(r):
            return lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 1, "<path list>": ["notes.md", "notes.md"]})

        def g1_form(r, not_done=None, if_ignored=None):
            """G1's block for notes.md: the plain block, its Not done and If ignored parts replaced, each on one line."""
            rows = g1_plain(r).split("\n")
            at = {x: next(k for k, row in enumerate(rows) if row.startswith(x)) for x in ("Not done:", "Fix:", "If ignored:")}
            nd = rows[at["Not done:"]:at["Fix:"]] if not_done is None else ["Not done: " + not_done]
            ig = rows[at["If ignored:"]:] if if_ignored is None else ["If ignored: " + if_ignored]
            return "\n".join(rows[:at["Not done:"]] + nd + rows[at["Fix:"]:at["If ignored:"]] + ig)

        def g1_land(r, unlanded=False, branch=LB, whole=False):
            """G1's landing form for an unkeyed stay on <branch>: as the start prints it, or as the end repeats it --
            <whole>, after a landing that landed the run's whole change (M4: its landed Not done), or <unlanded>."""
            tid = ("g1.landing.not_done.unlanded" if unlanded else "g1.landing.not_done.landed" if whole
                   else "g1.landing.not_done")
            return g1_form(r, lines.fill(tid, {"<default>": "main", "<branch>": branch, KINDS: 0}), T["g1.landing.if_ignored"])

        def stuck_cmds(r, sha7, default_ref="origin/main"):
            return ("'git -C \"%s\" show %s'" % (r.path, sha7),
                    "'python3 \"%s\" --specs \"%s\" land --default-ref %s --drop-held %s'" % (me, r.path, default_ref, sha7))

        def worktree_on_main(r, name):
            path = os.path.join(tmp, name)
            r.git("worktree", "add", "-q", path, "main")
            return Repo(path)

        def ahead_on_origin(r, name):
            """origin's main one commit ahead of r's: another clone's commit, which r fetches at its start."""
            o = clone(r, name)
            o.write("specifications/PRD-ACME-1-x/notes-other.md", "o\n")
            o.commit_all("ACME-1 Other work")
            o.git("push", "-q", "origin", "main")

        def e_land_g1():
            """Path 1, G1: the run's own file lands on main, the checkout unmoved, the branch and its origin copy unmoved,
            the file lifted, notes.md left dirty."""
            r, env = lworld("e-land-g1")
            br, up = ref(r, "refs/heads/" + LB), on_origin(r, LB)
            first = start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            tip = main_of(r)
            check(first.get("stay") == UNKEYED and got["_rc"] == 0 and got.get("row") == "pushed-default"
                  and got.get("print") == [landed(r, 1), g1_land(r, whole=True)] and got.get("branch") == "main"
                  and got.get("sha7") == tip[:7] and got.get("pushed") is True and on_origin(r) == tip
                  and changed(r, tip) == [FB] and r.git("log", "-1", "--format=%s", tip) == SUBJECT % ("NOISSUE", "/feedback")
                  and ref(r, "refs/heads/" + LB) == br and on_origin(r, LB) == up and on_lb(r)
                  and gone(r, FB) and r.git("status", "--porcelain") == "?? notes.md" and record(env, "/feedback") is None
                  and held(r) == [] and reflog_landed(r) == ["specs-git: landed " + tip[:7]],
                  "e_land_g1: landed on main, alternative 0, then G1's landing form; the checkout and the branch unmoved, "
                  "the file lifted (%r)" % got)

        def e_land_refused():
            """Path 2, a switch git refused: an index.lock at the start makes B4's switch fail; the end lands."""
            r, env = lworld("e-land-refused", notes=False)
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            try:
                first = start_of(env)
            finally:
                os.remove(lock)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(first.get("stay") == dict(UNKEYED, reason="refused") and got.get("row") == "pushed-default"
                  and got.get("print") == [landed(r, 1)] and changed(r, main_of(r)) == [FB] and gone(r, FB) and on_lb(r),
                  "e_land_refused: the refused switch's stay lands at the end (%r, %r)" % (first.get("stay"), got))

        def e_land_unlisted():
            """Path 3: status could not run at the start, so no snapshot: a leftover dirty before the start lands with the
            run's own file, and the line says so."""
            r, env = lworld("e-land-unlisted", notes=False)
            r.write(LEFT, ENTRY % "left")
            real = g["status"]

            def broken(root):
                raise NotRun("git status: fatal: index file corrupt")

            g["status"] = broken
            try:
                with in_env(env):
                    first = start(r.path, "/feedback", ("ACME-1",))
            finally:
                g["status"] = real
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(first.get("stay") == dict(UNKEYED, reason="unlisted") and first.get("start_dirty") is None
                  and got.get("row") == "pushed-default"
                  and got.get("print") == [landed(r, 2) + lines.fill("app.landed.unlisted", {"<branch>": LB})]
                  and changed(r, main_of(r)) == sorted([FB, LEFT]) and gone(r, FB) and gone(r, LEFT),
                  "e_land_unlisted: the leftover lands too, and app.landed.unlisted says so (%r)" % got)

        def e_land_stopped():
            """Path 4: the preflight stopped early before B4's switch."""
            r, env = lworld("e-land-stopped", notes=False)
            real = g["_disposition"]
            g["_disposition"] = boom
            try:
                with in_env(env):
                    first = start(r.path, "/feedback", ("ACME-1",))
            finally:
                g["_disposition"] = real
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(first.get("error") == "RuntimeError: boom" and first.get("stay") == dict(UNKEYED, reason="stopped")
                  and got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1)] and gone(r, FB),
                  "e_land_stopped: the early stop's stay lands (%r)" % got)

        def e_land_budget():
            """Path 5: start --budget 0 stopped at its budget, its next never made, so the record holds no stay; end asks
            for one (_unfinished_stay) and lands. And once HEAD has moved to another branch, none is asked for."""
            r, env = lworld("e-land-budget", notes=False)
            first = start_of(env, "--budget", "0")
            rec = record(env, "/feedback") or {}
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check((first.get("next") or {}).get("run") and rec.get("stage") in START_STAGES and rec.get("stay") is None
                  and got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1, LB, "unkeyed")]
                  and changed(r, main_of(r)) == [FB] and gone(r, FB) and on_lb(r),
                  "e_land_budget: the unfinished start's branch takes the landing (%r, %r)" % (rec.get("stage"), got))
            r, env = lworld("e-land-budget-moved", notes=False)
            start_of(env, "--budget", "0")
            old = main_of(r)
            r.git("switch", "-q", "-c", "prd/B-2-z")
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(got.get("branch") == "prd/B-2-z" and main_of(r) == old and changed(r, "HEAD") == [FB]
                  and "stayed on" not in (got.get("line") or ""),
                  "e_land_budget_moved: HEAD on a branch the start never stood on: end commits there (%r)" % got)

        def e_land_legacy():
            """P12: a 1.82.0 record -- merged_stay, no start_dirty -- on a merged branch lands against HEAD, every session
            file dirty going with the run's, and no unlisted clause, since no status failure is recorded."""
            r, env = world(tmp, "e-land-legacy")
            r.git("switch", "-q", "-c", AX)
            r.write("specifications/PRD-A-1-x/prd.md", "x\n")
            r.commit_all("A-1 work")
            r.git("push", "-q", "-u", "origin", AX)
            o = clone(r, "e-land-legacy-other")
            o.git("merge", "-q", "--ff-only", "origin/" + AX)
            o.git("push", "-q", "origin", "main")
            r.git("fetch", "-q", "origin")
            seed(env, "/feedback", branch=AX)
            with in_env(env):
                path = state.path("e-land-legacy", "/feedback")
            with open(path, encoding="utf-8") as fh:
                rec = json.load(fh)
            for k in ("stay", "start_dirty", "midrun", "protects"):
                rec.pop(k, None)
            rec["merged_stay"] = {"branch": AX, "reason": "g1"}
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(rec, fh)
            r.write(LEFT, ENTRY % "left")
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 2, AX, "merged")]
                  and changed(r, main_of(r)) == sorted([FB, LEFT]) and gone(r, FB) and gone(r, LEFT)
                  and r.git("symbolic-ref", "--short", "HEAD") == AX,
                  "e_land_legacy: the legacy stay lands against HEAD, no unlisted clause (%r)" % got)

        def e_land_merged():
            """S2: G1 on a fast-forward-merged branch lands (alternative 1), the file lifted, the branch still merged;
            with notes.md cleaned, the next start leaves the branch and deletes it -- which a file left in the working
            tree at a path main now holds would make git refuse."""
            r, env = world(tmp, "e-land-merged")
            r.git("switch", "-q", "-c", AX)
            r.write("specifications/PRD-A-1-x/prd.md", "x\n")
            r.commit_all("A-1 work")
            r.git("push", "-q", "-u", "origin", AX)
            o = clone(r, "e-land-merged-other")
            o.git("merge", "-q", "--ff-only", "origin/" + AX)
            o.git("push", "-q", "origin", "main")
            r.write("notes.md", "n\n")
            first = start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            v = {"<default>": "main", "<branch>": AX, KINDS: 1}
            merged_form = g1_form(r, lines.fill("g1.landing.not_done.landed", v),
                                  lines.fill("g1.merged.if_ignored", v)).split("\n")
            fix = lines.fill("g1.merged.fix", {"<SPECS_PATH>": r.path, "<default>": "main", "<path list>": "notes.md"})
            k = next(i for i, row in enumerate(merged_form) if row.startswith("Fix:"))
            j = next(i for i, row in enumerate(merged_form) if row.startswith("If ignored:"))
            merged_form = "\n".join(merged_form[:k] + ["Fix:      " + fix] + merged_form[j:])
            check(first.get("stay") == dict(UNKEYED, branch=AX, kind="merged", merged=True)
                  and got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1, AX, "merged"), merged_form]
                  and gone(r, FB) and branch_merged(r.path, "HEAD", "origin/main")["merged"]
                  and r.git("symbolic-ref", "--short", "HEAD") == AX,
                  "e_land_merged: alternative 1, lifted, the branch still merged (%r)" % got)
            os.remove(os.path.join(r.path, "notes.md"))
            got = start_of(env)
            check("Specs preflight: deleted merged prd/A-1-x" in (got.get("print") or [])
                  and got.get("branch") == "main" and ref(r, "refs/heads/" + AX) is None,
                  "e_land_merged: the next start leaves and deletes the merged branch (%r)" % got)

        def e_land_leftover_kept():
            """S1: a session file dirty before the start is not the run's: only the run's file reaches main, and the
            leftover is as it was."""
            r, env = lworld("e-land-leftover-kept")
            r.write(LEFT, ENTRY % "left")
            start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(got.get("print") == [landed(r, 1), g1_land(r, whole=True)] and changed(r, main_of(r)) == [FB]
                  and show(r, "main", LEFT) == "" and read(r, LEFT) == ENTRY % "left" and gone(r, FB),
                  "e_land_leftover_kept: the leftover stays out of main, unchanged (%r)" % got)

        def e_land_leftover_shared():
            """The run appends to the leftover's own block file: only the appended entry reaches main, and the working
            copy is the leftover's version after the lift."""
            r, env = lworld("e-land-leftover-shared")
            left = "## 2026-11-09 — /specify — left\n\nleft\n"
            mine = "## 2026-11-10 — /feedback — mine\n\nmine\n"
            r.write(FB, left)
            start_of(env)
            r.write(FB, left + mine)
            got = run_end(env, "/feedback")
            on_main = show(r, "main", FB)
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1), g1_land(r, whole=True)]
                  and "mine" in on_main and "left" not in on_main and read(r, FB) == left,
                  "e_land_leftover_shared: the run's entry alone on main, the leftover's version left (%r, %r)"
                  % (got, on_main))

        def e_land_commit_key():
            """The re-test: an unkeyed stay whose branch the end's --commit-key names is the run's own -- dropped, and the
            end commits on it, with the plain block; and, for a run typed mid-run, an unmerged mid-run stay is dropped
            the same way, nothing landing on main."""
            r, env = lworld("e-land-commit-key")
            first = start_of(env)
            old, up = main_of(r), on_origin(r)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback", "--commit-key", "B-2")
            h = head(r)
            check(first.get("stay") == UNKEYED and got.get("row") == "pushed-plugin"
                  and got.get("print") == ["Specs repo: committed %s (1 file) on %s — pushed" % (h[:7], LB), g1_plain(r)]
                  and on_origin(r, LB) == h and changed(r, h) == [FB] and main_of(r) == old and on_origin(r) == up
                  and r.git("log", "-1", "--format=%s", h) == SUBJECT % ("B-2", "/feedback"),
                  "e_land_commit_key: the stay dropped, committed on the branch, the plain block (%r)" % got)
            r, env = lworld("e-land-commit-key-midrun", notes=False)
            old, up = main_of(r), on_origin(r)
            midrun = {"command": "/specify", "started": "2026-11-10T10:00:00Z", "branch": LB}
            seed(env, "/feedback", branch=LB, keys=["ACME-1"], start_dirty={}, midrun=midrun,
                 stay={"branch": LB, "kind": "mid-run", "reason": "mid-run", "merged": False, "command": "/specify"})
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback", "--commit-key", "B-2")
            check(got.get("error") is None and main_of(r) == old and on_origin(r) == up and on_lb(r)
                  and changed(r, "HEAD") == [FB] and "stayed on" not in (got.get("line") or ""),
                  "e_land_commit_key_midrun: the mid-run stay dropped, nothing landed on main (%r)" % got)

        def e_land_moved():
            """HEAD moved to a new branch before the end: no stay stands there, so end commits where HEAD stands, with G1's
            plain block."""
            r, env = lworld("e-land-moved")
            start_of(env)
            old = main_of(r)
            r.git("switch", "-q", "-c", "prd/B-2-z")
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(got.get("branch") == "prd/B-2-z" and got.get("sha7") == head(r)[:7] and changed(r, "HEAD") == [FB]
                  and main_of(r) == old and (got.get("print") or [""])[-1] == g1_plain(r)
                  and "stayed on" not in (got.get("line") or ""),
                  "e_land_moved: committed on the branch HEAD moved to, the plain block (%r)" % got)

        def e_land_checked_out_pushed():
            """C2: another worktree has main checked out, behind origin's: the landing builds on origin/main and pushes by
            refspec -- pushed-default at once -- leaving local main and that worktree as they were."""
            r, env = lworld("e-land-co-pushed")
            w2 = worktree_on_main(r, "e-land-co-pushed-w2")
            ahead_on_origin(r, "e-land-co-pushed-other")
            start_of(env)
            local = main_of(r)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            up = on_origin(r) or ""
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1, sha7=up[:7]), g1_land(r, whole=True)]
                  and got.get("pushed") is True and changed(r, up) == [FB] and main_of(r) == local
                  and w2.git("status", "--porcelain") == "" and gone(r, FB) and held(r) == [],
                  "e_land_checked_out_pushed: pushed by refspec, local main and w2 untouched (%r)" % got)

        def e_land_held():
            """A cause that passes: w2 has main checked out and origin cannot be reached, so the refspec push fails and
            the change is held -- the held row, alternative 0, the checked-out clause with the push's reason, ending
            that the next run tries again; the files stay; one held entry."""
            r, env = lworld("e-land-held")
            w2 = worktree_on_main(r, "e-land-held-w2")
            start_of(env)
            os.rename(r.bare, r.bare + ".gone")  # origin unreachable, its URL -- and so the Environment: line -- as it was
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            entries = held(r)
            refused = entries[0]["refused"] if len(entries) == 1 else {}
            detail = refused.get("detail") or {}
            clause = lines.fill("reason.land.checked-out", {"<path>": refused.get("path"), "<default>": "main", CHECKED: 0,
                                                            "<reason>": detail.get("text")})
            want = lines.fill("row.held", {"<branch>": LB, "<default>": "main", HELD_KIND: 0, HELD_TAIL: 0,
                                           "<reason clause>": clause})
            check(got.get("row") == "held" and got.get("print") == [want, g1_land(r, unlanded=True)]
                  and refused.get("reason") == "checked-out" and refused.get("permanent") is False
                  and detail.get("outcome") == "failed" and os.path.samefile(refused.get("path"), w2.path)
                  and want.endswith("held for main, and the next run tries again")
                  and read(r, FB) == ENTRY % "mine" and main_of(r) == old and got.get("sha7") is None,
                  "e_land_held: the held row, the files kept, one held entry (%r, %r)" % (got, entries))

        def e_land_checked_out_no_origin():
            """A cause that will not pass: w2 has main checked out and there is no origin, so nowhere to push: the held,
            stuck row, the no-origin alternative, its two commands quoted whole."""
            r, env = lworld("e-land-co-none")
            w2 = worktree_on_main(r, "e-land-co-none-w2")
            r.git("remote", "remove", "origin")
            start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            entries = held(r)
            sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
            clause = lines.fill("reason.land.checked-out", {"<path>": entries[0]["refused"]["path"] if entries else None,
                                                            "<default>": "main", CHECKED: 1})
            want = lines.fill("row.held-stuck", {"<branch>": LB, "<default>": "main", STUCK_KIND: 0, "<reason clause>": clause,
                                                 "<SPECS_PATH>": r.path, "<sha7>": sha7, "<specs-git.py's path>": me,
                                                 "<default-ref>": "refs/heads/main"})
            cmds = stuck_cmds(r, sha7, "refs/heads/main")
            check(got.get("row") == "held-stuck" and got.get("print") == [want, g1_land(r, unlanded=True)]
                  and "there is no origin to push the commit to" in want and all(c in want for c in cmds)
                  and entries[0]["refused"]["permanent"] is True and read(r, FB) == ENTRY % "mine"
                  and w2.git("status", "--porcelain") == "",
                  "e_land_checked_out_no_origin: held stuck, nowhere to push, both commands (%r)" % got)

        def e_land_stuck():
            """The run's only change edits an entry main holds: refused edited, held stuck, nothing committed."""
            r, env = lworld("e-land-stuck", extra=[(COST, COST_BODY)])
            start_of(env)
            old = main_of(r)
            r.write(COST, COST_BODY.replace("body", "edited"))
            got = run_end(env, "/feedback")
            entries = held(r)
            sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
            want = lines.fill("row.held-stuck", {"<branch>": LB, "<default>": "main", STUCK_KIND: 0,
                                                 "<reason clause>": lines.fill("reason.land.edited", {"<path>": COST}),
                                                 "<SPECS_PATH>": r.path, "<sha7>": sha7, "<specs-git.py's path>": me,
                                                 "<default-ref>": "origin/main"})
            check(got.get("row") == "held-stuck" and got.get("print") == [want, g1_land(r, unlanded=True)]
                  and all(c in want for c in stuck_cmds(r, sha7)) and main_of(r) == old
                  and read(r, COST) == COST_BODY.replace("body", "edited"),
                  "e_land_stuck: held stuck, reason edited, both commands quoted whole (%r)" % got)

        def e_land_partial():
            """P29: that edit beside a feedback file: the feedback file lands, the cost file is held alone -- the
            landing's row with app.landed, then app.held.stuck naming it -- and the not-landed form."""
            r, env = lworld("e-land-partial", extra=[(COST, COST_BODY)])
            start_of(env)
            r.write(COST, COST_BODY.replace("body", "edited"))
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            entries = held(r)
            sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
            stuck = lines.fill("app.held.stuck", {"<path>": [COST], "<reason clause>": lines.fill("reason.land.edited",
                                                                                                {"<path>": COST}),
                                                  "<SPECS_PATH>": r.path, "<sha7>": sha7, "<default>": "main",
                                                  "<specs-git.py's path>": me, "<default-ref>": "origin/main"})
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1) + stuck, g1_land(r, unlanded=True)]
                  and changed(r, main_of(r)) == [FB] and gone(r, FB) and read(r, COST) == COST_BODY.replace("body", "edited")
                  and len(entries) == 1 and list(entries[0]["paths"]) == [COST],
                  "e_land_partial: the feedback file landed, the cost file held alone (%r)" % got)

        def e_land_there():
            """P26: the run's change is already on main: the there row, the file taken out, main unmoved."""
            r, env = lworld("e-land-there", notes=False)
            r.git("switch", "-q", "main")
            r.write(FB, ENTRY % "mine")
            r.commit_all("NOISSUE Add dev-workflows session artifacts (/feedback)")
            r.git("push", "-q", "origin", "main")
            r.git("switch", "-q", LB)
            r.write("notes.md", "n\n")
            start_of(env)
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(got.get("row") == "there"
                  and got.get("print") == [lines.fill("row.there", {"<default>": "main", "<branch>": LB}),
                                           g1_land(r, unlanded=True)]
                  and main_of(r) == old and gone(r, FB) and held(r) == [],
                  "e_land_there: the there row, lifted, main unmoved (%r)" % got)

        def e_land_kill():
            """A kill during the lift: main moved, the files dirty, end_commit's landing saved; end --resume lifts them
            and pushes, the same commit, main moved once."""
            r, env = lworld("e-land-kill")
            start_of(env)
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            real = g["_lift"]

            def lift_killed(*args, **kw):
                raise KeyboardInterrupt

            g["_lift"] = lift_killed
            killed = False
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                killed = True
            finally:
                g["_lift"] = real
            tip = main_of(r)
            rec = record(env, "/feedback") or {}
            landing = (rec.get("end_commit") or {}).get("landing") or {}
            check(killed and tip != old and read(r, FB) == ENTRY % "mine" and landing.get("tip") == tip
                  and len(held(r)) == 1,
                  "e_land_kill: main moved, the file dirty, the landing saved (%r)" % rec.get("end_commit"))
            got = run_end(env, "/feedback", "--resume")
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1), g1_land(r, whole=True)]
                  and got.get("sha7") == tip[:7] and main_of(r) == tip and on_origin(r) == tip and gone(r, FB)
                  and held(r) == [] and reflog_landed(r) == ["specs-git: landed " + tip[:7]]
                  and record(env, "/feedback") is None,
                  "e_land_kill: end --resume lifts and pushes the same commit, main moved once (%r)" % got)

        def e_land_kill_resumed():
            """A kill during the lift, resumed, where part of the change was held alone (the paths split off it found
            again by its c1: the row keeps app.held.stuck and the not-landed form), and where the change was pushed by
            refspec (its move verified on origin's main after a fetch: the pushed-default row at once)."""
            r, env = lworld("e-land-kill-stuck", extra=[(COST, COST_BODY)])
            start_of(env)
            r.write(COST, COST_BODY.replace("body", "edited"))
            r.write(FB, ENTRY % "mine")
            real = g["_lift"]

            def lift_killed(*args, **kw):
                raise KeyboardInterrupt

            g["_lift"] = lift_killed
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                pass
            finally:
                g["_lift"] = real
            got = run_end(env, "/feedback", "--resume")
            entries = held(r)
            sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
            stuck = lines.fill("app.held.stuck", {"<path>": [COST], "<reason clause>": lines.fill("reason.land.edited",
                                                                                                {"<path>": COST}),
                                                  "<SPECS_PATH>": r.path, "<sha7>": sha7, "<default>": "main",
                                                  "<specs-git.py's path>": me, "<default-ref>": "origin/main"})
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1) + stuck, g1_land(r, unlanded=True)]
                  and gone(r, FB) and len(entries) == 1 and list(entries[0]["paths"]) == [COST],
                  "e_land_kill_stuck: resumed, the path held alone still named (%r)" % got)
            r, env = lworld("e-land-kill-refspec")
            w2 = worktree_on_main(r, "e-land-kill-refspec-w2")
            start_of(env)
            local = main_of(r)
            r.write(FB, ENTRY % "mine")
            g["_lift"] = lift_killed
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                pass
            finally:
                g["_lift"] = real
            up = on_origin(r) or ""
            r.git("update-ref", "-d", "refs/remotes/origin/main")  # the fetch the verification makes brings it back
            got = run_end(env, "/feedback", "--resume")
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1, sha7=up[:7]), g1_land(r, whole=True)]
                  and got.get("pushed") is True and changed(r, up) == [FB] and on_origin(r) == up
                  and main_of(r) == local and gone(r, FB) and held(r) == [] and w2.git("status", "--porcelain") == "",
                  "e_land_kill_refspec: resumed, the refspec push verified on origin's main, its row at once (%r)" % got)

        def e_land_kill_register():
            """A landing whose register rebuild renumbered a record, cut off during the lift after its move: end --resume
            reads the moves from the journal, and its line carries the register clause the uninterrupted end prints."""
            canned = {"before_remote": {"web": {"o1": 1}}, "before_run": {"web": {"o2": 3}},
                      "after": {"web": {"o1": 2, "o2": 1}}}
            moves = sb._moves([canned])
            clause = "; ".join(
                lines.fill("app.register-clause", {"<slug>": slug, "<move>": [
                    lines.fill("app.register-move", {"<from>": m["from"], "<to>": m["to"], "<origin>": m["origin"],
                                                     "<whose number>": T["app.register-move." + m["side"]]})
                    for m in moves if m["slug"] == slug]})
                for slug in sorted({m["slug"] for m in moves}, key=[m["slug"] for m in moves].index))
            real_own, real_lift = sb.own_change, g["_lift"]

            def own_renumbering(*args, **kw):
                return dict(real_own(*args, **kw), numbers=canned)

            def lift_killed(*args, **kw):
                raise KeyboardInterrupt

            shown = {}
            for name, kill in (("e-land-register-whole", False), ("e-land-kill-register", True)):
                r, env = lworld(name)
                start_of(env)
                r.write(FB, ENTRY % "mine")
                sb.own_change = own_renumbering
                if kill:
                    g["_lift"] = lift_killed
                try:
                    with in_env(env):
                        got = end(r.path, "/feedback")
                except KeyboardInterrupt:
                    got = None
                finally:
                    sb.own_change, g["_lift"] = real_own, real_lift
                if kill:
                    rec = record(env, "/feedback") or {}
                    journal = ((rec.get("end_commit") or {}).get("landing") or {}).get("moves")
                    got = run_end(env, "/feedback", "--resume")
                    check(journal == moves and moves,
                          "e_land_kill_register: the journal saved through on_move carries the moves (%r)" % journal)
                shown[name] = (got or {}).get("print"), landed(r, 1) + "; " + clause, g1_land(r, whole=True)
            whole, killed = shown["e-land-register-whole"], shown["e-land-kill-register"]
            check(whole[0] == [whole[1], whole[2]] and killed[0] == [killed[1], killed[2]],
                  "e_land_kill_register: the resumed line carries the register clause the uninterrupted end prints "
                  "(%r)" % (shown,))

        def set_mode(env, mode):
            """The record's mode, as start records it: unsupported on a git whose merge-tree cannot merge without a
            checkout, with session-branch mode opted in."""
            with in_env(env):
                rec = state.load(env["CLAUDE_CODE_SESSION_ID"], "/feedback")
                rec["mode"] = mode
                state.save(env["CLAUDE_CODE_SESSION_ID"], "/feedback", rec)

        def e_land_unsupported():
            """I1, §6: in unsupported mode, the held, held-stuck and there rows -- none of which commits the files this
            run -- take no unsupported clause; the nothing row, which §6 does not except, keeps it."""
            unsupported = lines.fill("app.session.unsupported", {"<branch>": LB})
            # held: an index.lock at the landing's start
            r, env = lworld("e-land-unsup-held")
            start_of(env)
            set_mode(env, "unsupported")
            r.write(FB, ENTRY % "mine")
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            try:
                got = run_end(env, "/feedback")
            finally:
                os.remove(lock)
            want = lines.fill("row.held", {"<branch>": LB, "<default>": "main", HELD_KIND: 0, HELD_TAIL: 0,
                                           "<reason clause>": lines.fill("reason.locked", {"<path>": ".git/index.lock"})})
            check(got.get("row") == "held" and got.get("print") == [want, g1_land(r, unlanded=True)],
                  "e_land_unsupported: the held row takes no unsupported clause (%r)" % got)
            # held, stuck: an entry main holds, edited
            r, env = lworld("e-land-unsup-stuck", extra=[(COST, COST_BODY)])
            start_of(env)
            set_mode(env, "unsupported")
            r.write(COST, COST_BODY.replace("body", "edited"))
            got = run_end(env, "/feedback")
            entries = held(r)
            sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
            want = lines.fill("row.held-stuck", {"<branch>": LB, "<default>": "main", STUCK_KIND: 0,
                                                 "<reason clause>": lines.fill("reason.land.edited", {"<path>": COST}),
                                                 "<SPECS_PATH>": r.path, "<sha7>": sha7, "<specs-git.py's path>": me,
                                                 "<default-ref>": "origin/main"})
            check(got.get("row") == "held-stuck" and got.get("print") == [want, g1_land(r, unlanded=True)],
                  "e_land_unsupported: the held, stuck row takes no unsupported clause (%r)" % got)
            # there: the run's change already on main
            r, env = lworld("e-land-unsup-there", notes=False)
            r.git("switch", "-q", "main")
            r.write(FB, ENTRY % "mine")
            r.commit_all("NOISSUE Add dev-workflows session artifacts (/feedback)")
            r.git("push", "-q", "origin", "main")
            r.git("switch", "-q", LB)
            r.write("notes.md", "n\n")
            start_of(env)
            set_mode(env, "unsupported")
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(got.get("row") == "there"
                  and got.get("print") == [lines.fill("row.there", {"<default>": "main", "<branch>": LB}),
                                           g1_land(r, unlanded=True)],
                  "e_land_unsupported: the there row takes no unsupported clause (%r)" % got)
            # nothing: §6 does not except it, so the clause stands
            r, env = lworld("e-land-unsup-nothing")
            start_of(env)
            set_mode(env, "unsupported")
            got = run_end(env, "/feedback")
            check(got.get("row") == "nothing" and got.get("print") == [T["row.nothing"] + unsupported,
                                                                     g1_land(r, unlanded=True)],
                  "e_land_unsupported: the nothing row keeps the unsupported clause (%r)" % got)

        def e_land_resume_moved():
            """I2: a landing cut off before its move, then HEAD switched off the stayed branch: end --resume drops the
            journal entry -- nothing moved, the file still in the working tree -- and goes on as an end whose HEAD
            moved, committing where HEAD stands: on main (pushed), and on a third branch (not on origin)."""
            for to in ("main", "prd/B-2-z"):
                r, env = lworld("e-land-resume-moved-" + to.replace("/", "-"))
                start_of(env)
                r.write(FB, ENTRY % "mine")
                real = g["land"]

                def land_killed(*args, **kw):
                    inner = kw["on_move"]

                    def on_move(pending):
                        inner(pending)
                        raise KeyboardInterrupt
                    kw["on_move"] = on_move
                    return real(*args, **kw)

                g["land"] = land_killed
                try:
                    with in_env(env):
                        end(r.path, "/feedback")
                except KeyboardInterrupt:
                    pass
                finally:
                    g["land"] = real
                old = main_of(r)
                r.git("switch", "-q", *(["main"] if to == "main" else ["-c", to]))
                got = run_end(env, "/feedback", "--resume")
                h = head(r)
                if to == "main":
                    row = pushed_default(h[:7], r.path)
                    ok = got.get("row") == "pushed-default" and on_origin(r) == h and r.git("rev-parse", h + "^") == old
                else:
                    row = lines.fill("row.origin-lacks", {"<sha7>": h[:7], "<N>": 1, "<branch>": to, "<SPECS_PATH>": r.path})
                    ok = got.get("row") == "origin-lacks" and main_of(r) == old
                check(ok and got.get("print") == [row, g1_plain(r)] and changed(r, h) == [FB]
                      and r.git("symbolic-ref", "--short", "HEAD") == to and held(r) == [] and held_refs(r) == []
                      and r.git("status", "--porcelain") == "?? notes.md" and record(env, "/feedback") is None,
                      "e_land_resume_moved: HEAD on %s, the journal dropped, committed where HEAD stands (%r)" % (to, got))
            # no row is ever filled from a status the landing's end has none for (a raw template id)
            run = {"state": state, "lines": lines, "specs": tmp, "session": "x", "command": "/feedback", "record": "found",
                   "wrote": True, "pre": [], "commit": None}
            try:
                _landing_end(run, {}, {"default": "main", "default_ref": "origin/main"}, UNKEYED,
                             {"status": "kept", "held_landed": [], "stuck": None}, {"declined": [], "guard_block": None,
                                                                                   "guard_paths": []})
                raised = None
            except NotRun as e:
                raised = str(e)
            check(raised and "kept" in raised,
                  "e_land_resume_moved: a status with no landing row raises, never prints its id (%r)" % raised)

        def e_land_origin_lacks_default():
            """I3: origin exists but has no main yet (t_merged_unknown's world): G1 keeps an unkeyed stay, and the
            landing builds on local main, as (2) gives it; the push follows push_check's row for main -- none where main
            tracks nothing (push-scope finds every other commit on origin's prd/B-2-y, so the push creates origin's
            main), remote-deleted where main tracks an origin/main origin no longer has."""
            for name, tracks in (("e-land-no-origin-main", False), ("e-land-no-origin-main-tracked", True)):
                bare = os.path.join(tmp, name + ".git")
                subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
                r = new_repo(tmp, name)
                r.write(PRD, "---\nkind: prd\nkey: ACME-1\n---\n\n# PRD\n")
                r.commit_all("ACME-1 Add the PRD")
                r.git("remote", "add", "origin", bare)
                r.bare = bare
                if tracks:
                    r.git("config", "branch.main.remote", "origin")
                    r.git("config", "branch.main.merge", "refs/heads/main")
                env = {"HOME": os.path.join(tmp, "home-" + name), "CLAUDE_CODE_SESSION_ID": name, "SPECS_PATH": r.path}
                os.makedirs(env["HOME"])
                other_key(r, LB)
                r.write("notes.md", "n\n")
                local = main_of(r)
                first = start_of(env)
                r.write(FB, ENTRY % "mine")
                got = run_end(env, "/feedback")
                tip = main_of(r) or ""
                if tracks:
                    row = (lines.fill("row.remote-deleted", {"<sha7>": tip[:7], "<N>": 1, "<branch>": "main",
                                                             "<SPECS_PATH>": r.path})
                           + lines.fill("row.remote-deleted.default-tail", {"<SPECS_PATH>": r.path}))
                    want = ("remote-deleted", landed(r, 1, row=row), None)
                else:
                    want = ("pushed-default", landed(r, 1), tip)
                check(first.get("stay") == UNKEYED and first.get("default_ref") == "origin/main"
                      and (got.get("row"), got.get("line"), on_origin(r)) == want and got.get("error") is None
                      and tip != local and r.git("rev-parse", tip + "^") == local and changed(r, tip) == [FB]
                      and gone(r, FB) and on_lb(r) and (got.get("print") or [""])[-1] == g1_land(r, whole=True),
                      "%s: landed on local main, its row from push_check (%r)" % (name.replace("-", "_").replace(
                          "e_land_no_origin_main", "e_land_origin_lacks_default"), got))

        def e_land_origin_lacks_checked_out():
            """New Important 1 (round 2): origin has no main, w2 has main checked out, and local main holds a private
            commit of the user's: the landing never builds on local main for a refspec push, which would publish that
            commit unmeasured -- the change is held stuck (checked-out, origin has no main), nothing pushed, origin and
            both branches as they were."""
            name = "e-land-no-origin-main-co"
            bare = os.path.join(tmp, name + ".git")
            subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
            r = new_repo(tmp, name)
            r.write(PRD, "---\nkind: prd\nkey: ACME-1\n---\n\n# PRD\n")
            r.commit_all("ACME-1 Add the PRD")
            r.git("remote", "add", "origin", bare)
            r.bare = bare
            env = {"HOME": os.path.join(tmp, "home-" + name), "CLAUDE_CODE_SESSION_ID": name, "SPECS_PATH": r.path}
            os.makedirs(env["HOME"])
            other_key(r, LB)
            r.git("switch", "-q", "main")
            r.write("private.txt", "my private notes\n")
            r.commit_all("my private notes")
            r.git("switch", "-q", LB)
            r.write("notes.md", "n\n")
            w2 = worktree_on_main(r, name + "-w2")
            local = main_of(r)
            bare_refs = subprocess.run(["git", "--git-dir", bare, "for-each-ref"], stdout=subprocess.PIPE).stdout
            first = start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            entries = held(r)
            origin_unchanged = subprocess.run(["git", "--git-dir", bare, "for-each-ref"],
                                              stdout=subprocess.PIPE).stdout == bare_refs
            check(got.get("row") == "held-stuck" and origin_unchanged and len(entries) == 1 and main_of(r) == local,
                  "e_land_origin_lacks_checked_out: held stuck, nothing pushed -- origin's refs unchanged, local main "
                  "unmoved -- and one held entry (row %r, origin unchanged %r, %d held, %r)"
                  % (got.get("row"), origin_unchanged, len(entries), got.get("print")))
            if len(entries) == 1:  # the line and the entry, worded from the one entry that stands
                refused, sha7 = entries[0]["refused"], entries[0]["c2"][:7]
                clause = lines.fill("reason.land.checked-out", {"<path>": refused.get("path"), "<default>": "main",
                                                                CHECKED: 3})
                want = lines.fill("row.held-stuck", {"<branch>": LB, "<default>": "main", STUCK_KIND: 0,
                                                     "<reason clause>": clause, "<SPECS_PATH>": r.path, "<sha7>": sha7,
                                                     "<specs-git.py's path>": me, "<default-ref>": "origin/main"})
                check(first.get("stay") == UNKEYED and first.get("default_ref") == "origin/main"
                      and got.get("print") == [want, g1_land(r, unlanded=True)]
                      and clause.endswith("and origin has no main") and refused.get("permanent") is True
                      and (refused.get("detail") or {}).get("outcome") == "origin-lacks"
                      and os.path.samefile(refused.get("path"), w2.path)
                      and read(r, FB) == ENTRY % "mine" and w2.git("status", "--porcelain") == "",
                      "e_land_origin_lacks_checked_out: the held-stuck line, origin has no main, the entry permanent, "
                      "the file kept (%r)" % got)

        def e_land_held_mode_takes():
            """row.held's session-branch tail (checked-out's alternatives 4 and 5, mode_takes): w2 has main checked out,
            and origin refuses the refspec push, which is then recorded -- or a refusal was recorded already, after the
            start -- so the next run, in session-branch mode, drops the hold and commits the files as that mode does."""
            for name, alt in (("e-land-held-refused", 4), ("e-land-held-refused-before", 5)):
                r, env = lworld(name)
                worktree_on_main(r, name + "-w2")
                start_of(env)
                if alt == 4:
                    with open(os.path.join(r.bare, "hooks", "pre-receive"), "w", encoding="utf-8") as fh:
                        fh.write("#!/bin/sh\nwhile read old new ref; do [ \"$ref\" = refs/heads/main ] && exit 1; done\n"
                                 "exit 0\n")
                    os.chmod(os.path.join(r.bare, "hooks", "pre-receive"), 0o755)
                else:
                    path = os.path.join(r.path, ".git", "workflows", "push-refused", "main")
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write("2026-11-01\n")
                old = main_of(r)
                r.write(FB, ENTRY % "mine")
                got = run_end(env, "/feedback")
                entries = held(r)
                refused = entries[0]["refused"] if len(entries) == 1 else {}
                detail = refused.get("detail") or {}
                v = {"<path>": refused.get("path"), "<default>": "main", CHECKED: alt}
                v.update({"<the refusal>": detail.get("text")} if alt == 4 else
                         {"<date>": detail.get("date"), "<record>": detail.get("record")})
                want = lines.fill("row.held", {"<branch>": LB, "<default>": "main", HELD_KIND: 0, HELD_TAIL: 1,
                                               "<reason clause>": lines.fill("reason.land.checked-out", v)})
                check(got.get("row") == "held" and got.get("print") == [want, g1_land(r, unlanded=True)]
                      and detail.get("outcome") == ("refused" if alt == 4 else "refused-before") and detail.get("record")
                      and refused.get("permanent") is False and main_of(r) == old and read(r, FB) == ENTRY % "mine"
                      and want.endswith("and the next run, in session-branch mode, drops this hold and commits them as "
                                        "that mode commits session files"),
                      "e_land_held_mode_takes: alternative %d, the session-branch tail (%r, %r)" % (alt, got, entries))

        def e_land_kill_before_move():
            """A kill in on_move -- the journal written, nothing moved: end --resume lands the change once, then lifts
            it, the held record emptied."""
            r, env = lworld("e-land-kill-before")
            start_of(env)
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            real = g["land"]

            def land_killed(*args, **kw):
                inner = kw["on_move"]

                def on_move(pending):
                    inner(pending)
                    raise KeyboardInterrupt
                kw["on_move"] = on_move
                return real(*args, **kw)

            g["land"] = land_killed
            killed = False
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                killed = True
            finally:
                g["land"] = real
            rec = record(env, "/feedback") or {}
            check(killed and main_of(r) == old and read(r, FB) == ENTRY % "mine"
                  and ((rec.get("end_commit") or {}).get("landing") or {}).get("tip") and len(held(r)) == 1,
                  "e_land_kill_before_move: the journal written and saved, nothing moved (%r)" % rec.get("end_commit"))
            got = run_end(env, "/feedback", "--resume")
            tip = main_of(r)
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1), g1_land(r, whole=True)]
                  and tip != old and r.git("rev-parse", tip + "^") == old and changed(r, tip) == [FB]
                  and on_origin(r) == tip and gone(r, FB) and held(r) == [] and len(reflog_landed(r)) == 1,
                  "e_land_kill_before_move: end --resume lands once, then lifts (%r)" % got)

        def e_land_push_rows():
            """Steps 5-7 for the landing's commit on main: offline (failed), no origin (no-remote), and a local main
            holding the user's own unpushed commit (scope), each followed by app.landed."""
            r, env = lworld("e-land-offline")
            start_of(env)
            missing = r.bare
            os.rename(r.bare, r.bare + ".gone")  # origin unreachable, the Environment: line as it was
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            tip = main_of(r)
            want = ("Specs repo: committed %s (1 file) on main — push FAILED (fatal: '%s' does not appear to be a git "
                    "repository); the commit is local and a later run retries it" % (tip[:7], missing))
            check(got.get("row") == "failed" and got.get("print") == [landed(r, 1, row=want), g1_land(r, whole=True)]
                  and changed(r, tip) == [FB] and gone(r, FB),
                  "e_land_offline: committed on main, push FAILED naming main (%r)" % got)
            r, env = lworld("e-land-no-origin")
            r.git("remote", "remove", "origin")
            start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            tip = main_of(r)
            want = "Specs repo: committed %s (1 file) on main — not pushed: this specs repo has no origin remote" % tip[:7]
            check(got.get("row") == "no-remote" and got.get("print") == [landed(r, 1, row=want), g1_land(r, whole=True)]
                  and changed(r, tip) == [FB] and gone(r, FB),
                  "e_land_no_origin: committed on main, no-remote (%r)" % got)
            r, env = lworld("e-land-scope", notes=False)
            r.git("switch", "-q", "main")
            r.write(PRD, "---\nkind: prd\nkey: ACME-1\n---\n\n# PRD, edited\n")
            mine = r.commit_all("ACME-1 my edit")
            r.git("switch", "-q", LB)
            r.write("notes.md", "n\n")
            start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            tip = main_of(r)
            want = lines.fill("row.scope", {"<sha7>": [tip[:7], mine[:7]], "<N>": 1, "<branch>": "main",
                                            "<subject>": "ACME-1 my edit", "<path>": PRD})
            check(got.get("row") == "scope" and got.get("print") == [landed(r, 1, row=want), g1_land(r, whole=True)]
                  and r.git("rev-parse", tip + "^") == mine and on_origin(r) != tip,
                  "e_land_scope: the scope row names the user's commit (%r)" % got)

        def e_land_nonff():
            """origin's main moved after the start: the push is rejected and next names the replay of main; following it
            replays the landing's commit onto origin's -- main moved by update-ref, HEAD still on the stayed branch --
            the replayed row ending with app.landed."""
            r, env = lworld("e-land-nonff")
            start_of(env)
            ahead_on_origin(r, "e-land-nonff-other")
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            run = (got.get("next") or {}).get("run") or ""
            check(got.get("row") is None and " replay --for end --command /feedback --branch main" in run,
                  "e_land_nonff: next names the replay of main (%r)" % got)
            got = shell(run, env) if run else {}
            tip = main_of(r)
            want = ("Specs repo: committed %s (1 file) on main — pushed after a replay: origin's main had moved on, so "
                    "the run replayed its 1 commit(s) onto it" % tip[:7])
            check(got.get("row") == "replayed" and got.get("print") == [landed(r, 1, row=want), g1_land(r, whole=True)]
                  and on_origin(r) == tip and changed(r, tip) == [FB] and on_lb(r) and gone(r, FB)
                  and record(env, "/feedback") is None,
                  "e_land_nonff: replayed and pushed, main moved by update-ref, HEAD on the stayed branch (%r)" % got)

        def e_land_declined():
            """A declined path: the landing's row, app.landed, then the declined append last."""
            r, env = lworld("e-land-declined")
            start_of(env)
            ard = "specifications/PRD-ACME-1-x/ard.md"
            r.write(ard, "a\n")
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback", "--declined", ard)
            check(got.get("print") == [landed(r, 1) + "; the deliverable at %s remains uncommitted, as you asked" % ard,
                                       g1_land(r, whole=True)] and read(r, ard) == "a\n",
                  "e_land_declined: app.landed, then the declined append (%r)" % got)

        def e_land_locked():
            """end --resume of a landing journal with an index.lock standing: Locked, nothing landed or lifted, the
            journal left for a later call."""
            r, env = lworld("e-land-locked")
            start_of(env)
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            real = g["land"]

            def land_killed(*args, **kw):
                inner = kw["on_move"]

                def on_move(pending):
                    inner(pending)
                    raise KeyboardInterrupt
                kw["on_move"] = on_move
                return real(*args, **kw)

            g["land"] = land_killed
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                pass
            finally:
                g["land"] = real
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            try:
                got = run_end(env, "/feedback", "--resume")
            finally:
                os.remove(lock)
            entries = held(r)
            check(got.get("row") == "locked" and got.get("print") == [T["row.locked"], g1_land(r, unlanded=True)]
                  and main_of(r) == old and read(r, FB) == ENTRY % "mine" and len(entries) == 1
                  and entries[0].get("tip") and entries[0]["refused"] is None,
                  "e_land_locked: Locked, nothing landed, the journal kept (%r)" % got)
            # and where the move is verified -- a kill during the lift -- nothing is lifted under the lock either
            r, env = lworld("e-land-locked-lift")
            start_of(env)
            r.write(FB, ENTRY % "mine")
            real = g["_lift"]

            def lift_killed(*args, **kw):
                raise KeyboardInterrupt

            g["_lift"] = lift_killed
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                pass
            finally:
                g["_lift"] = real
            tip = main_of(r)
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            try:
                got = run_end(env, "/feedback", "--resume")
            finally:
                os.remove(lock)
            entries = held(r)
            check(got.get("row") == "locked" and got.get("print") == [T["row.locked"], g1_land(r, unlanded=True)]
                  and main_of(r) == tip and read(r, FB) == ENTRY % "mine" and len(entries) == 1
                  and entries[0].get("tip") == tip,
                  "e_land_locked: a verified journal is not lifted under the lock either (%r)" % got)

        def e_land_locked_held():
            """An index.lock at the end of a stayed run: the change held for that cause (row.held with reason.locked), one
            transient held entry, nothing committed or lifted; once the lock is gone, the held stage's primitive lands
            it on main and lifts it."""
            r, env = lworld("e-land-locked-held")
            start_of(env)
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            try:
                got = run_end(env, "/feedback")
            finally:
                os.remove(lock)
            entries = held(r)
            want = lines.fill("row.held", {"<branch>": LB, "<default>": "main", HELD_KIND: 0, HELD_TAIL: 0,
                                           "<reason clause>": lines.fill("reason.locked", {"<path>": ".git/index.lock"})})
            check(got.get("row") == "held" and got.get("print") == [want, g1_land(r, unlanded=True)]
                  and len(entries) == 1 and entries[0]["refused"] == {"reason": "locked", "path": ".git/index.lock",
                                                                      "detail": None, "permanent": False}
                  and list(entries[0]["paths"]) == [FB] and main_of(r) == old and read(r, FB) == ENTRY % "mine",
                  "e_land_locked_held: held for the lock, one transient entry, nothing committed (%r, %r)"
                  % (got, entries))
            # the flush half (Task 6): the lock stands again when the next start's held stage runs, so its retry fails
            # on the lock itself -- pre.held.failed with reason.locked, the entry kept, nothing lifted -- and the process
            # holding it finishes just after that stage; the flush, on prd/B-2-y now named by its key B-2 and notes.md
            # clean, then commits the run's other file and leaves the held one out. Once the lock is gone, the next
            # start's held stage lands it on main.
            os.remove(os.path.join(r.path, "notes.md"))
            r.write(LEFT, ENTRY % "left")
            open(lock, "w").close()
            real = g["_held_stage"]

            def held_then_unlocked(run):
                try:
                    return real(run)
                finally:
                    os.remove(lock)

            g["_held_stage"] = held_then_unlocked
            try:
                with in_env(env):
                    got = start(r.path, "/feedback", ("B-2",))
            finally:
                g["_held_stage"] = real
                if os.path.lexists(lock):
                    os.remove(lock)
            h = head(r)
            failed = lines.fill("pre.held.failed", {"<default>": "main", FAILED_TAIL: 0, "<reason clause>": lines.fill(
                "reason.locked", {"<path>": ".git/index.lock"})})
            check(failed in (got.get("print") or []) and changed(r, h) == [LEFT] and on_lb(r) and main_of(r) == old
                  and read(r, FB) == ENTRY % "mine" and [list(e["paths"]) for e in held(r)] == [[FB]],
                  "e_land_locked_held: the retry fails on the lock, and the flush commits the run's other file and leaves "
                  "the held one out (%r, %r)" % (got, r.git("status", "--porcelain", "--untracked-files=all")))
            got = start_with(env, "B-2")
            check(changed(r, main_of(r)) == [FB] and gone(r, FB) and held(r) == [] and main_of(r) != old
                  and lines.fill("pre.held.landed", {"<sha7>": main_of(r)[:7], "<N>": 1, "<default>": "main",
                                                     "<branch>": LB}) in (got.get("print") or []),
                  "e_land_locked_held: once the lock is gone, the held stage lands it on main (%r)" % got)

        def e_land_mode():
            """Session-branch mode: a stay is never kept there, and a record holding one is not landed: the mode's own
            commit on session/ab, main unmoved."""
            r, env = lworld("e-land-mode", notes=False)
            r.git("config", "workflows.sessionBranch", "true")
            env = dict(env, GIT_USER_INITIALS="ab")
            seed(env, "/feedback", branch=LB, keys=["ACME-1"], mode="on", session_branch="session/ab", start_dirty={},
                 stay=dict(UNKEYED, reason="stopped"))
            old, up = main_of(r), on_origin(r)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(got.get("row") == "pushed-session" and got.get("branch") == "session/ab" and main_of(r) == old
                  and on_origin(r) == up and on_lb(r) and "stayed on" not in (got.get("line") or ""),
                  "e_land_mode: the mode's outcome, nothing landed (%r)" % got)

        def e_land_hand_edit():
            """N4: prd/B-2-y's follow-ups.md holds a line main lacks; the user ticks it mid-run and the run appends one
            and writes a feedback file: the feedback file lands, follow-ups.md is held alone (dropped), its working copy
            keeping the tick and the new line, main's unchanged; with follow-ups.md the run's only change, held stuck."""
            for name, also in (("e-land-hand-edit", True), ("e-land-hand-edit-only", False)):
                r, env = lworld(name, notes=False, extra=[(FUP, "- [ ] a\n")])
                r.write(FUP, "- [ ] a\n- [ ] b\n")
                r.commit_all("B-2 a follow-up")
                r.write("notes.md", "n\n")
                start_of(env)
                ticked = "- [ ] a\n- [x] b\n- [ ] n\n"
                r.write(FUP, ticked)
                if also:
                    r.write(FB, ENTRY % "mine")
                got = run_end(env, "/feedback")
                entries = held(r)
                sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
                clause = lines.fill("reason.land.dropped", {"<path>": FUP, "<onto>": "main"})
                if also:
                    stuck = lines.fill("app.held.stuck", {"<path>": [FUP], "<reason clause>": clause, "<SPECS_PATH>": r.path,
                                                          "<sha7>": sha7, "<default>": "main",
                                                          "<specs-git.py's path>": me, "<default-ref>": "origin/main"})
                    ok = (got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1) + stuck,
                                                                                     g1_land(r, unlanded=True)]
                          and changed(r, main_of(r)) == [FB])
                else:
                    want = lines.fill("row.held-stuck", {"<branch>": LB, "<default>": "main", STUCK_KIND: 0,
                                                         "<reason clause>": clause, "<SPECS_PATH>": r.path, "<sha7>": sha7,
                                                         "<specs-git.py's path>": me, "<default-ref>": "origin/main"})
                    ok = got.get("row") == "held-stuck" and got.get("print") == [want, g1_land(r, unlanded=True)]
                check(ok and read(r, FUP) == ticked and show(r, "main", FUP) == "- [ ] a",
                      "%s: follow-ups.md held alone (dropped), the tick kept, main's unchanged (%r)"
                      % (name.replace("-", "_"), got))

        def e_land_register():
            """C: _push_step's rendering of a landing whose rebuild renumbered a record: the register clause after
            app.landed."""
            r, env = world(tmp, "e-land-register")
            r.write(RESUME, "r\n")
            tip = r.commit_all(SUBJECT % ("NOISSUE", "/feedback"))
            move = {"slug": "acme", "origin": "a1b2c3d", "side": "run", "from": 3, "to": 4}
            rec = {"stay": UNKEYED, "default": "main", "default_ref": "origin/main", "specs": r.path, "reported": [],
                   "mode": "off"}
            commit = {"sha7": tip[:7], "files": 1, "branch": "main", "paths": [RESUME], "hook_paths": [],
                      "landing": {"moves": [move], "stuck": None}}
            run = {"state": state, "lines": lines, "specs": r.path, "session": "e-land-register", "command": "/feedback",
                   "record": "found", "wrote": True, "pre": [], "commit": None}
            with in_env(env):
                got = _push_step(run, rec, commit, "main", {"declined": [], "guard_block": None, "guard_paths": []})
            clause = lines.fill("app.register-clause", {"<slug>": "acme", "<move>": [lines.fill("app.register-move", {
                "<from>": 3, "<to>": 4, "<origin>": "a1b2c3d", "<whose number>": T["app.register-move.run"]})]})
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1) + "; " + clause],
                  "e_land_register: the register clause after app.landed (%r)" % got)

        def e_land_not_finished():
            """An end that stops early inside the landing: the NOT FINISHED line, then G1's landing form with its
            not-landed Not done (§5); the record kept."""
            r, env = lworld("e-land-not-finished")
            start_of(env)
            r.write(FB, ENTRY % "mine")
            real = g["land"]
            g["land"] = boom
            try:
                with in_env(env):
                    got = end(r.path, "/feedback")
            finally:
                g["land"] = real
            stop = lines.fill("end.stopped", {"<the error>": "RuntimeError: boom"})
            check(got.get("print") == [stop, g1_land(r, unlanded=True)] and record(env, "/feedback") is not None,
                  "e_land_not_finished: NOT FINISHED, then the not-landed form (%r)" % got)

        def e_g1_uncommitted():
            """No stay: the plain block after an end that committed nothing of the run's -- Locked, Commit failed, and the
            NOT FINISHED line -- takes the not-committed form, its Not done and If ignored; after a commit, the plain
            block as it was."""
            uncommitted = T["g1.not_done.uncommitted"]
            for name in ("locked", "commit-failed", "stopped"):
                r, env = world(tmp, "e-g1-uncommitted-" + name)
                r.write("notes.md", "n\n")
                seed(env, "/specify", guard="G1", guard_block=g1_plain(r), guard_paths=["notes.md"])
                r.write(RESUME, "r\n")
                lock = os.path.join(r.path, ".git", "index.lock")
                if name == "locked":
                    open(lock, "w").close()
                    try:
                        got = run_end(env, "/specify")
                    finally:
                        os.remove(lock)
                    row = T["row.locked"]
                elif name == "commit-failed":
                    hook(os.path.join(r.path, ".git", "hooks", "pre-commit"), "echo hook says no >&2\nexit 1\n")
                    got = run_end(env, "/specify")
                    row = lines.fill("row.commit-failed", {"<the first line of git's error or the hook's output>":
                                                           "hook says no"})
                else:
                    real = g["commit_session_files"]

                    def write_then_boom(root, message, on_write=None, on_staged=None, exclude=()):
                        on_write()
                        raise RuntimeError("boom")

                    g["commit_session_files"] = write_then_boom
                    try:
                        with in_env(env):
                            got = end(r.path, "/specify")
                    finally:
                        g["commit_session_files"] = real
                    row = lines.fill("end.stopped", {"<the error>": "RuntimeError: boom"})
                shown = (got.get("print") or ["", ""])
                check(shown == [row, g1_form(r, uncommitted, T["g1.if_ignored.uncommitted"])]
                      and "WILL still be committed" not in shown[-1] and "committed alongside" not in shown[-1],
                      "e_g1_uncommitted: after %s, the not-committed Not done (%r)" % (name, got))

        # Task 6: §3.2's held stage at the start, <default>'s push before the guards, and the held files every flush and
        # end's commit leave out (exclude). A transient held entry is made as e_land_held makes one -- w2 has main checked
        # out and origin cannot be reached, so the refspec push fails -- and a permanent one as e_land_stuck does, an edited
        # cost entry main holds. origin is made unreachable by moving the bare repository aside, never by changing its URL,
        # which the Environment: line carries.
        FAILED_TAIL = lines.placeholder("pre.held.failed", "<and the next run")
        FUPS = ("- [ ] a\n", "- [ ] b\n", "- [ ] c\n", "- [ ] d\n")

        def offline(r):
            os.rename(r.bare, r.bare + ".gone")

        def online(r):
            os.rename(r.bare + ".gone", r.bare)

        def start_with(env, *keys, extra=()):
            """A start of /feedback with the key set <keys> (start_of's is ACME-1's), <extra> after them."""
            return cli("--specs", env["SPECS_PATH"], "start", "--command", "/feedback",
                       *[x for k in keys for x in ("--key", k)], *extra, env=env)

        def held_transient(name, files=None, extra=()):
            """lworld, then a stayed run (unkeyed, G1) whose end holds <files> (default FB) for a cause that passes: w2 has
            main checked out and origin is unreachable. Returns r, env and w2; origin is left unreachable."""
            r, env = lworld(name, extra=extra)
            w2 = worktree_on_main(r, name + "-w2")
            start_of(env)
            offline(r)
            for p, body in files or [(FB, ENTRY % "mine")]:
                r.write(p, body)
            run_end(env, "/feedback")
            return r, env, w2

        def held_permanent(name):
            """lworld with a cost file main holds, then a stayed run whose only change edits its entry: held, stuck."""
            r, env = lworld(name, extra=[(COST, COST_BODY)])
            start_of(env)
            r.write(COST, COST_BODY.replace("body", "edited"))
            run_end(env, "/feedback")
            return r, env

        def pushed_left(n=1):
            return lines.fill("pre.pushed-left", {"<N>": n, "<branch>": "main"})

        def held_landed(sha, n=1, branch=LB):
            return lines.fill("pre.held.landed", {"<sha7>": sha[:7], "<N>": n, "<default>": "main", "<branch>": branch})

        def stuck_line(r, sha7):
            return lines.fill("pre.held.stuck", {"<default>": "main", "<SPECS_PATH>": r.path, "<sha7>": sha7,
                                                 "<reason clause>": lines.fill("reason.land.edited", {"<path>": COST}),
                                                 "<specs-git.py's path>": me, "<default-ref>": "origin/main"})

        def commit_on_main(r, path, body):
            """A session-file commit on local main, unpushed, made by switching there and back: notes.md, untracked,
            rides both switches and is left out of the commit. Returns it."""
            back = r.git("symbolic-ref", "--short", "HEAD")
            r.git("switch", "-q", "main")
            r.write(path, body)
            r.git("add", "--", path)
            r.git("commit", "-q", "-m", SUBJECT % ("NOISSUE", "/feedback"))
            sha = head(r)
            r.git("switch", "-q", back)
            return sha

        def t_held_retry():
            """A transient entry whose cause is gone (w2 removed, origin reachable), notes.md still dirty: the next
            start's held stage lands it on main before G1's block -- pre.held.landed, then pre.pushed-left for the
            commit local main now holds -- the file lifted, the entry and its ref gone; G1's Not done opens that the
            preflight did not commit or push these files (P30), true beside a commit and push of main."""
            r, env, w2 = held_transient("t-held-retry")
            entries = held(r)
            r.git("worktree", "remove", "--force", w2.path)
            online(r)
            old = main_of(r)
            got = start_of(env)
            tip = main_of(r)
            block = g1_land(r)
            check(len(entries) == 1 and got.get("print") == [env_line(r.path), held_landed(tip), pushed_left(), block]
                  and "Not done: the preflight did not switch branches, and did not commit or push these files." in block
                  and tip != old and r.git("rev-parse", tip + "^") == old and changed(r, tip) == [FB]
                  and on_origin(r) == tip and gone(r, FB) and held(r) == [] and held_refs(r) == [] and on_lb(r),
                  "t_held_retry: landed on main before G1's block, main pushed, lifted, the entry gone (%r)" % got)

        def t_held_retry_fails():
            """w2 still has main checked out and origin is still unreachable: pre.held.failed, reason.land.checked-out
            naming main and the push's reason, before G1's block; the entry kept, main unmoved."""
            r, env, w2 = held_transient("t-held-retry-fails")
            old = main_of(r)
            got = start_of(env)
            entries = held(r)
            refused = entries[0]["refused"] if len(entries) == 1 else {}
            detail = refused.get("detail") or {}
            clause = lines.fill("reason.land.checked-out", {"<path>": refused.get("path"), "<default>": "main",
                                                            CHECKED: 0, "<reason>": detail.get("text")})
            want = lines.fill("pre.held.failed", {"<default>": "main", "<reason clause>": clause, FAILED_TAIL: 0})
            check(got.get("print") == [env_line(r.path), want, g1_land(r)] and refused.get("reason") == "checked-out"
                  and os.path.samefile(refused.get("path"), w2.path) and detail.get("outcome") == "failed"
                  and "has main checked out" in want and want.endswith("and the next run tries again")
                  and main_of(r) == old and read(r, FB) == ENTRY % "mine",
                  "t_held_retry_fails: pre.held.failed naming main before G1's block, the entry kept (%r)" % got)

        def t_held_stuck_reported():
            """Review Focus 3: a permanent entry prints pre.held.stuck on this start and the next, each before G1's
            block; a later stayed run's own file still lands at its end, the stuck file left as it stands."""
            r, env = held_permanent("t-held-stuck")
            entries = held(r)
            sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
            want = [env_line(r.path), stuck_line(r, sha7), g1_land(r)]
            first = start_of(env)
            second = start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            tip = main_of(r)
            check(first.get("print") == want and second.get("print") == want
                  and all(c in want[1] for c in stuck_cmds(r, sha7)) and want[1].endswith(stuck_cmds(r, sha7)[1])
                  and got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1), g1_land(r, whole=True)]
                  and changed(r, tip) == [FB] and gone(r, FB) and read(r, COST) == COST_BODY.replace("body", "edited")
                  and [e["c2"] for e in held(r)] == [entries[0]["c2"]],
                  "t_held_stuck_reported: the stuck line on every start, the next run's own file landed (%r, %r, %r)"
                  % (first, second, got))

        def t_held_flush_excludes():
            """A failing entry, notes.md clean, HEAD on prd/B-2-y with the key set {B-2} (B3): the flush commits the run's
            other dirty file on the branch and leaves the held one out."""
            r, env, w2 = held_transient("t-held-flush")
            os.remove(os.path.join(r.path, "notes.md"))
            r.write(LEFT, ENTRY % "left")
            start_with(env, "B-2")
            h = head(r)
            check(changed(r, h) == [LEFT] and r.git("log", "-1", "--format=%s", h) == SUBJECT % ("NOISSUE", "/feedback")
                  and on_lb(r) and read(r, FB) == ENTRY % "mine" and [list(e["paths"]) for e in held(r)] == [[FB]],
                  "t_held_flush_excludes: the flush commits LEFT alone, FB held (%r)"
                  % r.git("status", "--porcelain", "--untracked-files=all"))

        def t_held_changed():
            """P8: an entry holding FB and LEFT, FB edited since, the retry failing: the held stage rebuilds the entry
            without FB -- its ref naming a commit with c1's version of FB, which lacks it -- the flush commits FB as it
            stands on HEAD and prints pre.held.changed after the commit; a later retry lands LEFT alone."""
            r, env, w2 = held_transient("t-held-changed", files=[(FB, ENTRY % "mine"), (LEFT, ENTRY % "left")])
            before = held(r)
            os.remove(os.path.join(r.path, "notes.md"))
            r.write(FB, ENTRY % "edited")
            got = start_with(env, "B-2")
            h = head(r)
            entries = held(r)
            c2 = entries[0]["c2"] if len(entries) == 1 else None
            printed = got.get("print") or []
            line = lines.fill("pre.held.changed", {"<path>": FB, "<default>": "main"})
            failed = [k for k, x in enumerate(printed) if x.startswith("Specs preflight: could not commit the session")]
            check(len(before) == 1 and sorted(before[0]["paths"]) == [FB, LEFT] and line in printed
                  and failed and failed[0] < printed.index(line) and changed(r, h) == [FB]
                  and show(r, h, FB) == (ENTRY % "edited").rstrip("\n") and on_lb(r)
                  and c2 and list(entries[0]["paths"]) == [LEFT] and show(r, c2, FB) == ""
                  and show(r, c2, LEFT) == (ENTRY % "left").rstrip("\n") and held_refs(r) == [HELD_REF + c2],
                  "t_held_changed: FB committed on HEAD with pre.held.changed, the entry rebuilt without it (%r, %r)"
                  % (got, entries))
            r.git("worktree", "remove", "--force", w2.path)
            online(r)
            start_with(env, "B-2")
            check(changed(r, main_of(r)) == [LEFT] and held(r) == [] and gone(r, LEFT),
                  "t_held_changed: a later retry lands LEFT alone (%r)" % changed(r, main_of(r)))

        def t_held_on_default():
            """P9: an entry held for an index.lock, then HEAD switched to main with the held file: the next start drops
            the entry and its ref silently, and the flush commits the file on main."""
            r, env = lworld("t-held-default")
            start_of(env)
            r.write(FB, ENTRY % "mine")
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            try:
                run_end(env, "/feedback")
            finally:
                os.remove(lock)
            entries = held(r)
            os.remove(os.path.join(r.path, "notes.md"))
            r.git("switch", "-q", "main")
            got = start_of(env)
            tip = main_of(r)
            check(len(entries) == 1 and got.get("print") == [env_line(r.path)] and held(r) == [] and held_refs(r) == []
                  and changed(r, tip) == [FB] and on_origin(r) == tip and r.git("status", "--porcelain") == "",
                  "t_held_on_default: dropped silently, the flush commits the file on main (%r)" % got)

        def e_end_on_default_drops():
            """P9 at the end: a held entry (the stuck cost edit), then B4's switch to main and the run's own file: end
            drops the entry and its ref and commits the held file with the rest on main."""
            r, env = held_permanent("e-end-default")
            entries = held(r)
            sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
            os.remove(os.path.join(r.path, "notes.md"))
            first = start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            tip = main_of(r)
            check(first.get("print") == [env_line(r.path), stuck_line(r, sha7),
                                         lines.fill("pre.b4", {"<branch>": LB, "<default>": "main"})]
                  and got.get("print") == [pushed_default(tip[:7], r.path, 2)] and changed(r, tip) == sorted([COST, FB])
                  and held(r) == [] and held_refs(r) == [] and r.git("status", "--porcelain") == "",
                  "e_end_on_default_drops: the entry dropped, its file committed with the run's on main (%r, %r)"
                  % (first, got))

        def e_end_excludes_held():
            """§4 step 2: HEAD on prd/B-2-y, which the run's key B-2 names (B3), a held entry standing, and notes.md still
            dirty, so G1 ends the preflight before any flush: end's commit takes the run's own file and leaves the held one
            out."""
            r, env = held_permanent("e-end-excludes")
            start_with(env, "B-2")
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            h = head(r)
            check(got.get("branch") == LB and changed(r, h) == [FB] and on_lb(r)
                  and read(r, COST) == COST_BODY.replace("body", "edited") and len(held(r)) == 1,
                  "e_end_excludes_held: end commits FB on the branch, the held cost edit left out (%r)" % got)

        def e_land_resume_dropped_excludes():
            """end --resume drops an unverified landing journal with HEAD off the stay's branch (§4 step 1): the stuck
            half split off before the cut-off keeps its entry, and step 4's commit, on the branch HEAD moved to, leaves its
            file out."""
            r, env = lworld("e-land-resume-drop", extra=[(COST, COST_BODY)])
            start_of(env)
            old = main_of(r)
            r.write(COST, COST_BODY.replace("body", "edited"))
            r.write(FB, ENTRY % "mine")
            real = g["land"]

            def land_killed(*args, **kw):
                inner = kw["on_move"]

                def on_move(pending):
                    inner(pending)
                    raise KeyboardInterrupt
                kw["on_move"] = on_move
                return real(*args, **kw)

            g["land"] = land_killed
            killed = False
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                killed = True
            finally:
                g["land"] = real
            before = sorted(tuple(sorted(e["paths"])) for e in held(r))
            r.git("switch", "-q", "-c", "prd/ACME-1-z")
            got = run_end(env, "/feedback", "--resume")
            h = head(r)
            check(killed and before == [(COST,), (FB,)] and main_of(r) == old and changed(r, h) == [FB]
                  and r.git("symbolic-ref", "--short", "HEAD") == "prd/ACME-1-z"
                  and read(r, COST) == COST_BODY.replace("body", "edited") and [list(e["paths"]) for e in held(r)] == [[COST]],
                  "e_land_resume_dropped_excludes: the journal dropped, FB committed where HEAD stands, the stuck cost edit "
                  "left out (%r, %r)" % (before, got))

        def kill_lift(r, env):
            """end of a stayed run cut off during the landing's lift: main moved, the files dirty, the journal kept."""
            real = g["_lift"]

            def lift_killed(*args, **kw):
                raise KeyboardInterrupt

            g["_lift"] = lift_killed
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                return True
            finally:
                g["_lift"] = real
            return False

        def kill_before_move(r, env):
            """end of a stayed run cut off just after its landing's journal was written, before main moved."""
            real = g["land"]

            def land_killed(*args, **kw):
                inner = kw["on_move"]

                def on_move(pending):
                    inner(pending)
                    raise KeyboardInterrupt
                kw["on_move"] = on_move
                return real(*args, **kw)

            g["land"] = land_killed
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                return True
            finally:
                g["land"] = real
            return False

        def forget(env):
            """The run's record removed: a new session, which no end --resume reaches."""
            with in_env(env):
                state.remove(env["CLAUDE_CODE_SESSION_ID"], "/feedback")

        def t_held_journal():
            """e_land_kill's world -- main moved, the lift cut off -- and the record then removed: the next start's held
            stage finds the move verified and lifts the files, main unmoved by it, the held record empty; then main's
            push, before G1's block."""
            r, env = lworld("t-held-journal")
            start_of(env)
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            killed = kill_lift(r, env)
            tip = main_of(r)
            forget(env)
            got = start_of(env)
            check(killed and tip != old and got.get("print") == [env_line(r.path), pushed_left(), g1_land(r)]
                  and main_of(r) == tip and on_origin(r) == tip and gone(r, FB) and held(r) == [] and held_refs(r) == []
                  and len(reflog_landed(r)) == 1,
                  "t_held_journal: the verified journal lifted, main unmoved, the record empty (%r)" % got)

        def t_held_journal_before_move():
            """F2: e_land_kill_before_move's world -- the journal written, main still at its old -- the record then
            removed, no --resume: the next start's held stage lands the change again, main moved once and holding it,
            and lifts the files only after; never a bare lift."""
            r, env = lworld("t-held-journal-before")
            start_of(env)
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            killed = kill_before_move(r, env)
            journal = held(r)
            forget(env)
            got = start_of(env)
            tip = main_of(r)
            check(killed and main_of(r) != old and len(journal) == 1 and journal[0]["refused"] is None
                  and got.get("print") == [env_line(r.path), held_landed(tip), pushed_left(), g1_land(r)]
                  and r.git("rev-parse", tip + "^") == old and changed(r, tip) == [FB] and len(reflog_landed(r)) == 1
                  and on_origin(r) == tip and gone(r, FB) and held(r) == [] and held_refs(r) == [],
                  "t_held_journal_before_move: landed again, main moved once, then lifted (%r)" % got)

        def t_held_then_own_across_start():
            """m2: a transient entry on follow-ups.md whose run had the file dirty at its own start (its c1 holds b); the
            next run's held stage lands the entry and lifts the file to that c1, updating the run's snapshot; the run
            then appends a line, and its end lands only that line, nothing refused, the file left at the entry's c1."""
            a, b, c, d = FUPS
            r, env = lworld("t-held-own", extra=[(FUP, a)])
            w2 = worktree_on_main(r, "t-held-own-w2")
            r.write(FUP, a + b)
            start_of(env)
            offline(r)
            r.write(FUP, a + b + c)
            first = run_end(env, "/feedback")
            entries = held(r)
            r.git("worktree", "remove", "--force", w2.path)
            online(r)
            started = start_of(env)
            mid = read(r, FUP)
            landed_held = main_of(r)
            r.write(FUP, a + b + d)
            got = run_end(env, "/feedback")
            check(first.get("row") == "held" and len(entries) == 1 and mid == a + b
                  and started.get("print") == [env_line(r.path), held_landed(landed_held), pushed_left(), g1_land(r)]
                  and got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1), g1_land(r, whole=True)]
                  and show(r, "main", FUP) == (a + c + d).rstrip("\n") and read(r, FUP) == a + b and held(r) == [],
                  "t_held_then_own_across_start: the end lands d alone, the file left at a+b (%r, %r, %r)"
                  % (started, got, read(r, FUP)))

        def e_land_held_landed_at_end():
            """Minor 11: a transient entry on follow-ups.md, retried in vain at start; the run appends to the file; the
            cause gone before its end: the end lands the entry first -- pre.held.landed before the row -- then the run's
            own line, both on main, the file lifted back to HEAD's version."""
            a, b, c, _d = FUPS
            r, env = lworld("e-land-held-end", extra=[(FUP, a)])
            w2 = worktree_on_main(r, "e-land-held-end-w2")
            start_of(env)
            offline(r)
            r.write(FUP, a + b)
            run_end(env, "/feedback")
            entries = held(r)
            started = start_of(env)
            r.write(FUP, a + b + c)
            r.git("worktree", "remove", "--force", w2.path)
            online(r)
            got = run_end(env, "/feedback")
            tip = main_of(r)
            first = r.git("rev-parse", tip + "^")
            check(len(entries) == 1 and any(x.startswith("Specs preflight: could not commit the session files")
                                            for x in started.get("print") or [])
                  and got.get("print") == [held_landed(first), landed(r, 1), g1_land(r, whole=True)]
                  and show(r, "main", FUP) == (a + b + c).rstrip("\n") and show(r, first, FUP) == (a + b).rstrip("\n")
                  and read(r, FUP) == a and held(r) == [] and on_origin(r) == tip,
                  "e_land_held_landed_at_end: pre.held.landed before the row, both on main (%r)" % got)

        def t_held_mode():
            """P9: in session-branch mode the held stage drops every held entry and its ref."""
            r, env, _w2 = held_transient("t-held-mode")
            entries = held(r)
            r.git("config", "workflows.sessionBranch", "true")
            got = start_of(env)
            check(len(entries) == 1 and got.get("mode") == "on" and held(r) == [] and held_refs(r) == []
                  and read(r, FB) == ENTRY % "mine",
                  "t_held_mode: the entry and its ref dropped, the file left (%r)" % got)

        def t_held_misrooted():
            """P9: under misrooted (SPECS_PATH below the repository's top) the held stage never runs: the entry and its
            ref kept, though its cause is gone (w2 removed, origin reachable), so a held stage would have landed it."""
            r, env, w2 = held_transient("t-held-misrooted")
            r.git("worktree", "remove", "--force", w2.path)
            online(r)
            entries, refs = held(r), held_refs(r)
            below = os.path.join(r.path, "specs")
            os.makedirs(below)
            got = cli("--specs", below, "start", "--command", "/feedback", "--key", "ACME-1", env=env)
            check(len(entries) == 1 and got.get("specs_git") == "misrooted" and held(r) == entries
                  and held_refs(r) == refs and refs,
                  "t_held_misrooted: nothing done under misrooted (%r)" % got)

        def t_default_push_g1():
            """P21: G1 firing on prd/B-2-y, local main one session-file commit ahead of origin's: the held stage pushes
            main, pre.pushed-left naming it, before G1's block. In session-branch mode, no such push; with HEAD on main,
            none from this stage (and G1 ends the preflight before the flush's)."""
            r, env = lworld("t-default-push")
            tip = commit_on_main(r, FB, ENTRY % "landed")
            got = start_of(env)
            check(got.get("print") == [env_line(r.path), pushed_left(), g1_land(r)] and on_origin(r) == tip
                  and main_of(r) == tip and on_lb(r),
                  "t_default_push_g1: main pushed before G1's block (%r)" % got)
            r, env = lworld("t-default-push-mode")
            old = on_origin(r)
            commit_on_main(r, FB, ENTRY % "landed")
            r.git("config", "workflows.sessionBranch", "true")
            got = start_of(env)
            check(got.get("mode") == "on" and pushed_left() not in (got.get("print") or []) and on_origin(r) == old,
                  "t_default_push_g1: in session-branch mode, no push of main (%r)" % got)
            r, env = lworld("t-default-push-main")
            old = on_origin(r)
            r.git("switch", "-q", "main")
            commit_on_main(r, FB, ENTRY % "landed")
            got = start_of(env)
            check(got.get("print") == [env_line(r.path), g1_plain(r)] and on_origin(r) == old,
                  "t_default_push_g1: HEAD on main, G1 firing: no push from this stage (%r)" % got)

        def t_default_push_nonff():
            """origin's main moved on: the held stage's push is rejected, and next names replay --for start --branch
            main; following it replays the commit onto origin's main, moving refs/heads/main by update-ref with HEAD on
            prd/B-2-y, pushes, and names start --resume, which goes on at the guards: G1's block, once."""
            r, env = lworld("t-default-nonff")
            mine = commit_on_main(r, FB, ENTRY % "landed")
            ahead_on_origin(r, "t-default-nonff-o")
            theirs = on_origin(r)
            got = start_of(env)
            nxt = (got.get("next") or {}).get("run") or ""
            stage = (record(env, "/feedback") or {}).get("stage")
            replayed = shell(nxt, env) if nxt else {}
            again = (replayed.get("next") or {}).get("run") or ""
            stage2 = (record(env, "/feedback") or {}).get("stage")
            resumed = shell(again, env) if again else {}
            tip = main_of(r)
            shown = (replayed.get("print") or [""])[0]
            check(" replay --for start --command /feedback --branch main" in nxt and stage == "held"
                  and got.get("print") == [env_line(r.path)] and stage2 == "guards"
                  and again.endswith("--resume") and " start --command /feedback " in again
                  and shown.startswith("Specs preflight: main — pushed after a replay")
                  and tip != mine and r.git("rev-parse", tip + "^") == theirs and on_origin(r) == tip
                  and changed(r, tip) == [FB] and on_lb(r)
                  and resumed.get("print") == [g1_land(r)] and resumed.get("next") is None,
                  "t_default_push_nonff: replayed by update-ref, pushed, then the guards (%r, %r, %r)"
                  % (got, replayed, resumed))

        def e_land_unpushed_retry():
            """e_land_offline's world -- the landing committed on main, its push failed -- origin reachable again and G1
            still firing: the next start's held stage pushes main, before G1's block."""
            r, env = lworld("e-land-unpushed")
            start_of(env)
            offline(r)
            r.write(FB, ENTRY % "mine")
            first = run_end(env, "/feedback")
            tip = main_of(r)
            online(r)
            got = start_of(env)
            check(first.get("row") == "failed" and got.get("print") == [env_line(r.path), pushed_left(), g1_land(r)]
                  and on_origin(r) == tip,
                  "e_land_unpushed_retry: main pushed by the held stage while G1 fires (%r)" % got)

        def t_held_resume():
            """P28: two transient entries on two paths, w2 still on main and origin reachable, --budget 0: the fetch takes
            the first call's one unit, so it stops at stage held before the first entry's push; the next call lands
            the first entry and stops before the second's; the third lands the second, and G1's block follows, once.
            Each stop's next is start --resume, the record at held."""
            r, env, w2 = held_transient("t-held-resume")
            start_of(env)
            r.write(LEFT, ENTRY % "left")
            run_end(env, "/feedback")
            entries = held(r)
            online(r)
            calls, stages = [start_of(env, "--budget", "0")], []
            while (calls[-1].get("next") or {}).get("run") and len(calls) < 8:
                stages.append((record(env, "/feedback") or {}).get("stage"))
                calls.append(shell(calls[-1]["next"]["run"], env))
            tip = on_origin(r)
            first = r.git("rev-parse", tip + "^")
            check(len(entries) == 2 and len(calls) == 3 and stages == ["held", "held"]
                  and all(c["next"]["run"].endswith("--budget 0 --started %s --resume" % calls[0].get("started"))
                          for c in calls[:2])
                  and [c.get("print") for c in calls] == [[env_line(r.path)], [held_landed(first)],
                                                          [held_landed(tip), g1_land(r)]]
                  and calls[-1].get("next") is None and sorted(changed(r, tip) + changed(r, first)) == sorted([FB, LEFT])
                  and gone(r, FB) and gone(r, LEFT) and held(r) == [] and held_refs(r) == [],
                  "t_held_resume: one entry per call, G1's block once (%r)" % [c.get("print") for c in calls])

        def t_held_locked():
            """The held stage under an index.lock (specs-repo-git §3.2): a transient entry, its cause gone (w2 removed,
            origin reachable), and a lock standing at the next start: it lands nothing and lifts nothing -- pre.held.failed
            with reason.locked naming the lock, before G1's block; main unmoved, the file as it was, the record and the
            ref kept. Once the lock is gone, the next start lands the entry."""
            r, env, w2 = held_transient("t-held-locked")
            entries, refs = held(r), held_refs(r)
            r.git("worktree", "remove", "--force", w2.path)
            online(r)
            old = main_of(r)
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            try:
                got = start_of(env)
            finally:
                os.remove(lock)
            failed = lines.fill("pre.held.failed", {"<default>": "main", FAILED_TAIL: 0, "<reason clause>": lines.fill(
                "reason.locked", {"<path>": ".git/index.lock"})})
            check(len(entries) == 1 and got.get("print") == [env_line(r.path), failed, g1_land(r)] and main_of(r) == old
                  and on_origin(r) == old and read(r, FB) == ENTRY % "mine" and held(r) == entries
                  and held_refs(r) == refs,
                  "t_held_locked: nothing landed or lifted under the lock, the entry kept (%r)" % got)
            got = start_of(env)
            tip = main_of(r)
            check(got.get("print") == [env_line(r.path), held_landed(tip), pushed_left(), g1_land(r)]
                  and changed(r, tip) == [FB] and gone(r, FB) and held(r) == [] and held_refs(r) == [],
                  "t_held_locked: once the lock is gone, the next start lands it (%r)" % got)

        def t_held_locked_stuck():
            """Under an index.lock, retry_held reports a permanent entry stuck, as ever, and keeps it: a stuck entry's
            line promises no landing, so the lock changes nothing it says."""
            r, env = held_permanent("t-held-locked-stuck")
            entries = held(r)
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            try:
                got = retry_held(r.path, "main", "origin/main")
            finally:
                os.remove(lock)
            check(len(entries) == 1 and [x["sha"] for x in got["stuck"]] == [entries[0]["c2"]] and got["failed"] == []
                  and got["stuck"][0]["refused"]["reason"] == "edited" and held(r) == entries,
                  "t_held_locked_stuck: the permanent entry reported stuck and kept (%r)" % got)

        def held_locked(name, files=None):
            """lworld, then a stayed run (unkeyed, G1) whose end found an index.lock: <files> (default FB) held for that
            cause, which passes. The lock is gone again on return."""
            r, env = lworld(name)
            start_of(env)
            for p, body in files or [(FB, ENTRY % "mine")]:
                r.write(p, body)
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            try:
                run_end(env, "/feedback")
            finally:
                os.remove(lock)
            return r, env

        def start_lock_held(r, env, keys):
            """A start of /feedback with the key set <keys>, in process, an index.lock standing through its held stage and
            gone just after it -- the process holding it finishing between that stage and the flush."""
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            real = g["_held_stage"]

            def held_then_unlocked(run):
                try:
                    return real(run)
                finally:
                    if os.path.lexists(lock):
                        os.remove(lock)

            g["_held_stage"] = held_then_unlocked
            try:
                with in_env(env):
                    return start(r.path, "/feedback", tuple(keys))
            finally:
                g["_held_stage"] = real
                if os.path.lexists(lock):
                    os.remove(lock)

        def t_held_locked_default():
            """I1: with HEAD on main, an index.lock at the held stage does not keep the entries: each is dropped with its
            ref, silently, as without the lock (a drop touches no index); once the lock is gone the flush commits the
            files on main."""
            r, env = held_locked("t-held-locked-default")
            entries = held(r)
            os.remove(os.path.join(r.path, "notes.md"))
            r.git("switch", "-q", "main")
            got = start_lock_held(r, env, ("ACME-1",))
            tip = main_of(r)
            check(len(entries) == 1 and got.get("print") == [env_line(r.path)] and held(r) == [] and held_refs(r) == []
                  and changed(r, tip) == [FB] and on_origin(r) == tip and r.git("status", "--porcelain") == "",
                  "t_held_locked_default: dropped under the lock, the flush commits the file on main (%r)" % got)

        def t_held_locked_mode():
            """I1: in session-branch mode, an index.lock at the held stage does not keep the entries: each is dropped with
            its ref, no held line printed; once the lock is gone, the flush's §8.2 commit takes the file onto the session
            branch."""
            r, env = held_locked("t-held-locked-mode")
            entries = held(r)
            os.remove(os.path.join(r.path, "notes.md"))
            r.git("config", "workflows.sessionBranch", "true")
            env = dict(env, GIT_USER_INITIALS="ab")
            got = start_lock_held(r, env, ("ACME-1",))
            printed = got.get("print") or []
            check(len(entries) == 1 and got.get("mode") == "on" and held(r) == [] and held_refs(r) == []
                  and not any("an earlier run held" in x for x in printed)
                  and show(r, "session/ab", FB) == (ENTRY % "mine").rstrip("\n"),
                  "t_held_locked_mode: dropped under the lock, the session branch takes the file (%r)" % got)

        def t_held_resume_failed():
            """I2: two transient entries on two paths, both failing (w2 on main, origin unreachable), --budget 0: each
            call tries one entry, the resumed stage keeping, and not printing again, the one an earlier call of this start
            tried; the chain reaches the second and ends, each failed line printed once, then G1's block."""
            r, env, _w2 = held_transient("t-held-resume-failed")
            start_of(env)
            r.write(LEFT, ENTRY % "left")
            run_end(env, "/feedback")
            entries = held(r)
            calls = [start_of(env, "--budget", "0")]
            while (calls[-1].get("next") or {}).get("run") and len(calls) < 8:
                calls.append(shell(calls[-1]["next"]["run"], env))
            after = held(r)

            def failed(e):
                detail = e["refused"].get("detail") or {}
                clause = lines.fill("reason.land.checked-out", {"<path>": e["refused"]["path"], "<default>": "main",
                                                                CHECKED: 0, "<reason>": detail.get("text")})
                return lines.fill("pre.held.failed", {"<default>": "main", "<reason clause>": clause, FAILED_TAIL: 0})

            want = ([[env_line(r.path)], [failed(after[0])], [failed(after[1]), g1_land(r)]]
                    if len(after) == 2 else None)
            check(len(entries) == 2 and [list(e["paths"]) for e in after] == [[FB], [LEFT]] and len(calls) == 3
                  and [c.get("print") for c in calls] == want and calls[-1].get("next") is None
                  and (record(env, "/feedback") or {}).get("held_attempted") == [],
                  "t_held_resume_failed: one entry per call, each failed line once, the chain ends (%r)"
                  % [c.get("print") for c in calls])

        def t_held_locked_journal():
            """Minor 2: e_land_kill's world (main moved, the lift cut off), the record removed, then an index.lock at the
            next start's held stage: the journal's move is verified from the local refs, so it prints nothing, its lift
            waiting; the flush, the lock gone, commits the run's other file and leaves the journal's out; the next start
            lifts it."""
            r, env = lworld("t-held-locked-journal")
            start_of(env)
            r.write(FB, ENTRY % "mine")
            killed = kill_lift(r, env)
            tip = main_of(r)
            forget(env)
            os.remove(os.path.join(r.path, "notes.md"))
            r.write(LEFT, ENTRY % "left")
            got = start_lock_held(r, env, ("B-2",))
            h = head(r)
            journal = held(r)
            check(killed and got.get("print") == [env_line(r.path), pushed_left()] and changed(r, h) == [LEFT] and on_lb(r)
                  and read(r, FB) == ENTRY % "mine" and len(journal) == 1 and journal[0]["refused"] is None
                  and main_of(r) == tip and on_origin(r) == tip,
                  "t_held_locked_journal: no line under the lock, the lift waits, the flush leaves FB out (%r)" % got)
            start_with(env, "B-2")
            check(gone(r, FB) and held(r) == [] and main_of(r) == tip,
                  "t_held_locked_journal: once the lock is gone, the next start lifts it (%r)" % held(r))

        def t_held_locked_changed():
            """Minor 1: an entry holding FB and LEFT, FB edited since, an index.lock at the held stage and gone by the
            flush: the held stage rebuilds nothing under the lock; the flush commits FB as it stands, prints
            pre.held.changed, and rebuilds the entry without it once that commit is made."""
            r, env = held_locked("t-held-locked-changed", files=[(FB, ENTRY % "mine"), (LEFT, ENTRY % "left")])
            before = held(r)
            os.remove(os.path.join(r.path, "notes.md"))
            r.write(FB, ENTRY % "edited")
            got = start_lock_held(r, env, ("B-2",))
            h = head(r)
            entries = held(r)
            c2 = entries[0]["c2"] if len(entries) == 1 else None
            check(len(before) == 1 and sorted(before[0]["paths"]) == [FB, LEFT]
                  and lines.fill("pre.held.changed", {"<path>": FB, "<default>": "main"}) in (got.get("print") or [])
                  and changed(r, h) == [FB] and c2 and c2 != before[0]["c2"] and list(entries[0]["paths"]) == [LEFT]
                  and show(r, c2, FB) == "" and read(r, LEFT) == ENTRY % "left",
                  "t_held_locked_changed: FB committed, the entry rebuilt after the commit (%r, %r)" % (got, entries))

        def e_end_changed_resume():
            """The end killed just after its commit, which took a held file changed since it was held (§4 step 2):
            end_commit saved the path before the commit, so end --resume prints pre.held.changed for it, once, and
            rebuilds the entry without it. An entry holding FB and LEFT, failing at the start (w2 on main, origin
            unreachable); the start's G1 ends the preflight on prd/B-2-y, named by the run's key B-2, so no flush runs;
            FB is edited after the start."""
            r, env, _w2 = held_transient("e-end-changed-resume", files=[(FB, ENTRY % "mine"), (LEFT, ENTRY % "left")])
            before = held(r)
            start_with(env, "B-2")
            r.write(FB, ENTRY % "edited")
            real = g["commit_session_files"]

            def commit_then_killed(*args, **kw):
                real(*args, **kw)
                raise KeyboardInterrupt

            g["commit_session_files"] = commit_then_killed
            killed = False
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                killed = True
            finally:
                g["commit_session_files"] = real
            h = head(r)
            pending = (record(env, "/feedback") or {}).get("end_commit") or {}
            got = run_end(env, "/feedback", "--resume")
            line = lines.fill("pre.held.changed", {"<path>": FB, "<default>": "main"})
            entries = held(r)
            c2 = entries[0]["c2"] if len(entries) == 1 else None
            check(killed and len(before) == 1 and sorted(before[0]["paths"]) == [FB, LEFT] and changed(r, h) == [FB]
                  and on_lb(r) and pending.get("held_changed") == [FB] and (got.get("print") or []).count(line) == 1
                  and got.get("sha7") == h[:7] and c2 and list(entries[0]["paths"]) == [LEFT] and show(r, c2, FB) == ""
                  and read(r, LEFT) == ENTRY % "left",
                  "e_end_changed_resume: the resume prints the line once and rebuilds the entry (%r, %r, %r)"
                  % (pending, got, entries))

        COST2 = ("# Cost\n\n## 2026-11-09T10:00:00Z — /specify — draft\n\nfirst\n\n"
                 "## 2026-11-10T10:00:00Z — /specify — draft\n\nbody\n")
        MORE = "\n## 2026-11-11T10:00:00Z — /specify — draft\n\nmore\n"

        def t_held_resume_stuck():
            """N1: a stuck entry S (an edited cost entry main holds), then a later run's append T to that file, started
            from S's version and held for a cause that passes (w2 on main, origin unreachable); origin back, --budget 0.
            The first call prints S's stuck line and stops before T's push; the resumed stage keeps S, which holds
            nothing back, and lands T by refspec -- never reporting it stuck or held behind S -- then G1's block."""
            r, env = lworld("t-held-resume-stuck", extra=[(COST, COST2)])
            worktree_on_main(r, "t-held-resume-stuck-w2")
            start_of(env)
            r.write(COST, COST2.replace("first", "edited"))
            run_end(env, "/feedback")
            start_of(env)
            r.write(COST, COST2.replace("first", "edited") + MORE)
            offline(r)
            run_end(env, "/feedback")
            online(r)
            entries = held(r)
            calls = [start_of(env, "--budget", "0")]
            while (calls[-1].get("next") or {}).get("run") and len(calls) < 8:
                calls.append(shell(calls[-1]["next"]["run"], env))
            tip = on_origin(r)
            s_c2 = entries[0]["c2"] if len(entries) == 2 else "?"
            check(len(entries) == 2 and entries[0]["refused"]["permanent"] is True
                  and entries[1]["refused"]["permanent"] is False
                  and [c.get("print") for c in calls] == [[env_line(r.path), stuck_line(r, s_c2[:7])],
                                                          [held_landed(tip), g1_land(r)]]
                  and calls[-1].get("next") is None and [e["c2"] for e in held(r)] == [s_c2]
                  and r.git("--git-dir", r.bare, "show", "main:" + COST).endswith("more")
                  and read(r, COST) == COST2.replace("first", "edited"),
                  "t_held_resume_stuck: T lands on the resume, S kept and holding nothing back (%r, %r)"
                  % ([c.get("print") for c in calls], held(r)))

        def changed_world(name):
            """held_transient with FB and LEFT (origin left unreachable), a start keyed B-2 on prd/B-2-y whose G1 ends the
            preflight before any flush, then FB edited: the end's commit takes FB as it stands (§4 step 2)."""
            r, env, _w2 = held_transient(name, files=[(FB, ENTRY % "mine"), (LEFT, ENTRY % "left")])
            start_with(env, "B-2")
            r.write(FB, ENTRY % "edited")
            return r, env

        def killed_at(env, name, call):
            """<call>() in process, g[<name>] raising KeyboardInterrupt on entry; True where it was killed."""
            real = g[name]

            def kill(*_a, **_kw):
                raise KeyboardInterrupt

            g[name] = kill
            try:
                with in_env(env):
                    call()
            except KeyboardInterrupt:
                return True
            finally:
                g[name] = real
            return False

        def rebuilt_to_left(r):
            entries = held(r)
            return (len(entries) == 1 and list(entries[0]["paths"]) == [LEFT]
                    and show(r, entries[0]["c2"], FB) == "" and read(r, LEFT) == ENTRY % "left")

        def e_end_changed_resume_push():
            """N2 (a): the end killed during its push step -- after its commit, its pre.held.changed line and its
            rebuild -- then end --resume: the line printed once (the killed call's output was never returned), the entry
            rebuilt without FB."""
            r, env = changed_world("e-end-changed-push")
            killed = killed_at(env, "_push_step", lambda: end(r.path, "/feedback"))
            pending = (record(env, "/feedback") or {}).get("end_commit") or {}
            got = run_end(env, "/feedback", "--resume")
            line = lines.fill("pre.held.changed", {"<path>": FB, "<default>": "main"})
            check(killed and pending.get("held_changed") == [FB] and pending.get("sha7")
                  and (got.get("print") or []).count(line) == 1 and got.get("sha7") == pending.get("sha7")
                  and rebuilt_to_left(r),
                  "e_end_changed_resume_push: the resume prints the line once, the entry rebuilt (%r, %r)" % (pending, got))

        def e_end_changed_resume_twice():
            """N2 (b): the end killed after its commit, then the first end --resume killed as it enters _held_committed
            (before its rebuild): the second resume prints the line once and rebuilds the entry."""
            r, env = changed_world("e-end-changed-twice")
            real = g["commit_session_files"]

            def commit_then_killed(*args, **kw):
                real(*args, **kw)
                raise KeyboardInterrupt

            g["commit_session_files"] = commit_then_killed
            first = False
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                first = True
            finally:
                g["commit_session_files"] = real
            second = killed_at(env, "_held_committed", lambda: end(r.path, "/feedback", resume=True))
            mid = [list(e["paths"]) for e in held(r)]
            pending = (record(env, "/feedback") or {}).get("end_commit") or {}
            got = run_end(env, "/feedback", "--resume")
            line = lines.fill("pre.held.changed", {"<path>": FB, "<default>": "main"})
            check(first and second and sorted(mid[0]) == [FB, LEFT] and pending.get("held_changed") == [FB]
                  and (got.get("print") or []).count(line) == 1 and rebuilt_to_left(r),
                  "e_end_changed_resume_twice: the second resume prints the line once and rebuilds (%r, %r, %r)"
                  % (mid, pending, got))

        def e_end_changed_shown():
            """N2's guard: the end's push rejected (origin's prd/B-2-y moved on), so its output -- carrying
            pre.held.changed -- names the replay and the record stays; end_commit marks the line shown, and an end
            --resume then rebuilds without printing it again."""
            r, env = changed_world("e-end-changed-shown")
            online(r)
            o = clone(r, "e-end-changed-shown-o")
            o.git("switch", "-q", LB)
            o.write("specifications/PRD-B-2-y/notes-o.md", "o\n")
            o.commit_all("B-2 Other work")
            o.git("push", "-q", "origin", LB)
            first = run_end(env, "/feedback")
            line = lines.fill("pre.held.changed", {"<path>": FB, "<default>": "main"})
            pending = (record(env, "/feedback") or {}).get("end_commit") or {}
            got = run_end(env, "/feedback", "--resume")
            check(" replay --for end " in ((first.get("next") or {}).get("run") or "")
                  and (first.get("print") or []).count(line) == 1 and pending.get("held_changed_shown") is True
                  and line not in (got.get("print") or []) and rebuilt_to_left(r),
                  "e_end_changed_shown: shown once, a later resume does not repeat it (%r, %r, %r)" % (first, pending, got))

        def t_held_resume_rebuilt():
            """The re-review's out-of-scope case, ruled in: an entry E (FB and LEFT) settled as failed on one call of a
            start, then FB edited before the next, so P8 rebuilds E under a new c2: the resumed stage still counts it as
            tried -- not retried, its failed line not printed again -- and goes on to the next entry F. --budget 0, w2
            on main, origin unreachable."""
            third = "specifications/PRD-ACME-1-x/dev-workflows/feedback/third.md"
            r, env, _w2 = held_transient("t-held-resume-rebuilt", files=[(FB, ENTRY % "mine"), (LEFT, ENTRY % "left")])
            start_of(env)
            r.write(third, ENTRY % "third")
            run_end(env, "/feedback")
            before = held(r)
            calls = [start_of(env, "--budget", "0")]
            calls.append(shell(calls[-1]["next"]["run"], env) if (calls[-1].get("next") or {}).get("run") else {})
            r.write(FB, ENTRY % "edited")
            calls.append(shell(calls[-1]["next"]["run"], env) if (calls[-1].get("next") or {}).get("run") else {})
            after = held(r)

            def failed(e):
                detail = e["refused"].get("detail") or {}
                clause = lines.fill("reason.land.checked-out", {"<path>": e["refused"]["path"], "<default>": "main",
                                                                CHECKED: 0, "<reason>": detail.get("text")})
                return lines.fill("pre.held.failed", {"<default>": "main", "<reason clause>": clause, FAILED_TAIL: 0})

            want = ([[env_line(r.path)], [failed(after[0])], [failed(after[1]), g1_land(r)]]
                    if len(after) == 2 else None)
            check(len(before) == 2 and sorted(before[0]["paths"]) == [FB, LEFT] and list(before[1]["paths"]) == [third]
                  and len(after) == 2 and list(after[0]["paths"]) == [LEFT] and after[0]["c2"] != before[0]["c2"]
                  and [c.get("print") for c in calls] == want and calls[-1].get("next") is None
                  and (record(env, "/feedback") or {}).get("held_attempted") == [],
                  "t_held_resume_rebuilt: the rebuilt entry not retried, its line not printed again (%r, %r)"
                  % ([c.get("print") for c in calls], after))

        def e_end_changed_signal():
            """M1 (the re-review's rv_sig): a SIGTERM inside the end's capped push -- git_bounded raising NotRun("git push
            ended by signal 15") -- takes end's error return, an output the harness that sent the signal has set aside:
            the record does not mark pre.held.changed shown, and the end --resume the skill then makes prints it once."""
            r, env = changed_world("e-end-changed-signal")
            real = g["push"]

            def ended(*_a, **_kw):
                raise NotRun("git push ended by signal 15")

            g["push"] = ended
            try:
                with in_env(env):
                    first = end(r.path, "/feedback")
            finally:
                g["push"] = real
            pending = (record(env, "/feedback") or {}).get("end_commit") or {}
            got = run_end(env, "/feedback", "--resume")
            line = lines.fill("pre.held.changed", {"<path>": FB, "<default>": "main"})
            check(first.get("error") == "git push ended by signal 15" and pending.get("held_changed") == [FB]
                  and not pending.get("held_changed_shown") and (got.get("print") or []).count(line) == 1
                  and rebuilt_to_left(r),
                  "e_end_changed_signal: a signal's stop marks nothing shown; the resume prints the line once (%r, %r, %r)"
                  % (first, pending, got))

        def t_held_here_finished():
            """A here journal cut off before its update-ref (P2), HEAD on main: the next start's held stage runs the here
            form again and prints pre.here.finished -- its <branch> and <N> from retry_held's finished entry -- before
            G1's block."""
            r, env = world(tmp, "t-held-here")
            r.write("notes.md", "n\n")
            r.write(FB, ENTRY % "mine")
            old = main_of(r)

            def kill(_pending):
                raise KeyboardInterrupt

            killed = False
            try:
                land(r.path, "main", "main", "origin/main", SUBJECT % ("NOISSUE", "/feedback"), {}, here=True,
                     on_move=kill)
            except KeyboardInterrupt:
                killed = True
            journal = held(r)
            got = start_of(env)
            tip = main_of(r)
            want = lines.fill("pre.here.finished", {"<branch>": "main", "<sha7>": tip[:7], "<N>": 1})
            check(killed and len(journal) == 1 and journal[0]["here"] is True and journal[0]["tip"]
                  and got.get("print") == [env_line(r.path), want, g1_plain(r)]
                  and tip != old and r.git("rev-parse", tip + "^") == old and changed(r, tip) == [FB]
                  and r.git("status", "--porcelain") == "?? notes.md" and held(r) == [] and held_refs(r) == [],
                  "t_held_here_finished: the here form run again, its line before G1's block (%r)" % got)

        for name, fn in (("e_land_g1", e_land_g1), ("e_land_refused", e_land_refused),
                         ("e_land_unlisted", e_land_unlisted), ("e_land_stopped", e_land_stopped),
                         ("e_land_budget", e_land_budget), ("e_land_legacy", e_land_legacy),
                         ("e_land_merged", e_land_merged), ("e_land_leftover_kept", e_land_leftover_kept),
                         ("e_land_leftover_shared", e_land_leftover_shared), ("e_land_commit_key", e_land_commit_key),
                         ("e_land_moved", e_land_moved), ("e_land_checked_out_pushed", e_land_checked_out_pushed),
                         ("e_land_held", e_land_held), ("e_land_checked_out_no_origin", e_land_checked_out_no_origin),
                         ("e_land_stuck", e_land_stuck), ("e_land_partial", e_land_partial),
                         ("e_land_there", e_land_there), ("e_land_kill", e_land_kill),
                         ("e_land_kill_resumed", e_land_kill_resumed),
                         ("e_land_kill_register", e_land_kill_register),
                         ("e_land_kill_before_move", e_land_kill_before_move),
                         ("e_land_unsupported", e_land_unsupported), ("e_land_resume_moved", e_land_resume_moved),
                         ("e_land_held_mode_takes", e_land_held_mode_takes),
                         ("e_land_origin_lacks_checked_out", e_land_origin_lacks_checked_out),
                         ("e_land_origin_lacks_default", e_land_origin_lacks_default), ("e_land_push_rows", e_land_push_rows),
                         ("e_land_nonff", e_land_nonff), ("e_land_declined", e_land_declined),
                         ("e_land_locked", e_land_locked), ("e_land_locked_held", e_land_locked_held),
                         ("e_land_mode", e_land_mode), ("e_land_hand_edit", e_land_hand_edit),
                         ("e_land_register", e_land_register), ("e_land_not_finished", e_land_not_finished),
                         ("e_g1_uncommitted", e_g1_uncommitted),
                         ("t_held_retry", t_held_retry), ("t_held_retry_fails", t_held_retry_fails),
                         ("t_held_stuck_reported", t_held_stuck_reported), ("t_held_flush_excludes", t_held_flush_excludes),
                         ("t_held_changed", t_held_changed), ("t_held_on_default", t_held_on_default),
                         ("e_end_on_default_drops", e_end_on_default_drops), ("e_end_excludes_held", e_end_excludes_held),
                         ("e_land_resume_dropped_excludes", e_land_resume_dropped_excludes),
                         ("t_held_journal", t_held_journal), ("t_held_journal_before_move", t_held_journal_before_move),
                         ("t_held_then_own_across_start", t_held_then_own_across_start),
                         ("e_land_held_landed_at_end", e_land_held_landed_at_end), ("t_held_mode", t_held_mode),
                         ("t_held_misrooted", t_held_misrooted), ("t_default_push_g1", t_default_push_g1),
                         ("t_default_push_nonff", t_default_push_nonff), ("e_land_unpushed_retry", e_land_unpushed_retry),
                         ("t_held_resume", t_held_resume), ("t_held_here_finished", t_held_here_finished),
                         ("t_held_locked", t_held_locked), ("t_held_locked_stuck", t_held_locked_stuck),
                         ("t_held_locked_default", t_held_locked_default), ("t_held_locked_mode", t_held_locked_mode),
                         ("t_held_resume_failed", t_held_resume_failed), ("t_held_locked_journal", t_held_locked_journal),
                         ("t_held_locked_changed", t_held_locked_changed),
                         ("e_end_changed_resume", e_end_changed_resume), ("t_held_resume_stuck", t_held_resume_stuck),
                         ("e_end_changed_resume_push", e_end_changed_resume_push),
                         ("e_end_changed_resume_twice", e_end_changed_resume_twice),
                         ("e_end_changed_shown", e_end_changed_shown), ("t_held_resume_rebuilt", t_held_resume_rebuilt),
                         ("e_end_changed_signal", e_end_changed_signal)):
            case(name, fn)

    def scenarios_land(tmp):
        """specs-repo-git §4 step 1's landing: land, the held record, retry_held, and the land and snapshot subcommands.
        In process where a fault is injected, else as the CLI runs."""
        LB = "prd/B-2-y"
        FUP = "specifications/PRD-ACME-1-x/follow-ups.md"
        FB = "specifications/PRD-ACME-1-x/dev-workflows/feedback/f.md"
        FB2 = "specifications/PRD-ACME-1-x/dev-workflows/feedback/g.md"
        COST = "specifications/PRD-ACME-1-x/dev-workflows/cost/abcd1234.md"
        COST_BODY = "# Cost\n\n## 2026-11-10T10:00:00Z — /specify — draft\n\nbody\n"
        EDITED = COST_BODY.replace("body", "edited")
        ENTRY = "## 2026-11-10 — /feedback — note\n\n%s\n"
        HELD = "refs/workflows/held/"
        MSG = session_subject(None, "/feedback")
        PENDING = {"c1", "c2", "old", "tip", "onto", "paths", "remote_only", "here", "index_before", "moves", "kept"}
        CLI_FIELDS = {"status", "sha7", "files", "paths", "lifted", "default", "pushed", "reason", "detail", "path", "permanent",
                      "stuck", "kept", "error"}

        def case(name, fn):
            try:
                fn()
            except Exception as e:  # one case that crashes must not hide the others
                check(False, "%s crashed: %s: %s" % (name, type(e).__name__, str(e).strip()[:400]))

        def no_origin(r):
            r.git("remote", "remove", "origin")

        def lworld(name, follow="- [ ] a\n", extra=(), stay=True):
            """world, with follow-ups.md and <extra> ((path, body) pairs) committed on main and pushed; then, where
            <stay>, other_key."""
            r, r.env = world(tmp, name)
            r.write(FUP, follow)
            for p, body in extra:
                r.write(p, body)
            r.commit_all("ACME-1 Add the follow-ups")
            r.git("push", "-q", "origin", "main")
            if stay:
                other_key(r)
            return r

        def ref(r, name):
            return r.git("rev-parse", "--verify", "-q", name, check=False) or None

        def main_of(r):
            return ref(r, "refs/heads/main")

        def held(r):
            return held_entries(r.path)

        def held_refs(r):
            return r.git("for-each-ref", "--format=%(refname)", HELD).split()

        def show(r, rev, path):
            return r.git("show", "%s:%s" % (rev, path), check=False)

        def changed(r, rev):
            return sorted(x for x in r.git("diff-tree", "--no-commit-id", "--name-only", "-r", rev).split("\n") if x)

        def porcelain(r):
            return r.git("status", "--porcelain", "--untracked-files=all")

        def read(r, path):
            full = os.path.join(r.path, path)
            if not os.path.isfile(full):
                return None
            with open(full, encoding="utf-8", newline="") as fh:
                return fh.read()

        def do_land(r, branch=LB, snap=None, default_ref="origin/main", **kw):
            return land(r.path, branch, "main", default_ref, MSG, snap, **kw)

        def worktree(r, name, branch="main"):
            path = os.path.join(tmp, name)
            r.git("worktree", "add", "-q", path, branch)
            return Repo(path)

        def same_path(a, b):
            return a is not None and b is not None and os.path.realpath(a) == os.path.realpath(b)

        @contextlib.contextmanager
        def patched(name, fake):
            real = getattr(sb, name)
            setattr(sb, name, fake)
            try:
                yield real
            finally:
                setattr(sb, name, real)

        def locked_move(calls=None):
            """move_branch answering locked, as a lock left by a git that died would make it: a transient cause."""
            def fake(*_args, **_kw):
                if calls is not None:
                    calls.append(1)
                return {"reason": "locked", "path": ".git/refs/heads/main.lock"}
            return fake

        def kill(_pending):
            raise OSError("killed")

        def stopped(fn):
            try:
                fn()
            except LandStopped as e:
                return e
            return None

        def l_land_unkeyed():
            r = lworld("l-unkeyed")
            old, br, hd = main_of(r), ref(r, "refs/heads/" + LB), ref(r, "HEAD")
            r.write(FB, ENTRY % "mine")
            r.write(FUP, "- [ ] a\n- [ ] b\n")
            got = do_land(r)
            tip = main_of(r)
            check(got["status"] == "landed" and got["sha"] == tip and got["files"] == 2 and got["paths"] == [FB, FUP]
                  and got["pushed"] is False and got["onto"] == "main" and got["refused"] is None and got["stuck"] is None
                  and got["held_landed"] == [] and got["moves"] == [],
                  "l_land_unkeyed: landed on main (%r)" % got)
            check(tip != old and r.git("rev-parse", tip + "^") == old and changed(r, tip) == [FB, FUP]
                  and show(r, tip, FUP) == "- [ ] a\n- [ ] b"
                  and r.git("reflog", "-1", "--format=%gs", "refs/heads/main") == "specs-git: landed " + tip[:7],
                  "l_land_unkeyed: one commit on the old main naming exactly the two paths, its reflog the landing's")
            check(ref(r, "refs/heads/" + LB) == br and ref(r, "HEAD") == hd and r.git("symbolic-ref", "--short", "HEAD") == LB,
                  "l_land_unkeyed: the stayed branch and HEAD unmoved")
            check(porcelain(r) == "" and sorted(got["lifted"]) == [FB, FUP],
                  "l_land_unkeyed: both paths lifted, the checkout clean (%r, %r)" % (porcelain(r), got["lifted"]))
            check(held(r) == [] and held_refs(r) == [], "l_land_unkeyed: no journal entry left")

        def l_land_snapshot():
            r = lworld("l-snapshot")
            r.write(FUP, "- [ ] a\n- [ ] s\n")  # S: another run's line, dirty when this run started
            snap = snapshot(r.path)
            check(snap == {FUP: r.git("hash-object", FUP)}, "l_land_snapshot: the snapshot names S's blob (%r)" % snap)
            r.write(FUP, "- [ ] a\n- [ ] s\n- [ ] mine\n")
            got = do_land(r, snap=snap)
            check(got["status"] == "landed" and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] mine"
                  and read(r, FUP) == "- [ ] a\n- [ ] s\n" and got["lifted"] == [FUP],
                  "l_land_snapshot: main's commit adds only the run's line, the working copy S after the lift (%r, %r)"
                  % (got, show(r, main_of(r), FUP)))

        def l_land_snapshot_deleted():
            r = lworld("l-snapshot-deleted", extra=[(RESUME, "r\n")])
            os.remove(os.path.join(r.path, RESUME))
            snap = snapshot(r.path)
            r.write(FB, ENTRY % "mine")
            got = do_land(r, snap=snap)
            tip = main_of(r)
            check(snap == {RESUME: None} and got["status"] == "landed" and changed(r, tip) == [FB]
                  and show(r, tip, RESUME) == "r" and read(r, RESUME) is None and read(r, FB) is None,
                  "l_land_snapshot_deleted: a deletion standing at the start is not the run's: it neither lands nor is "
                  "put back (%r, %r)" % (snap, got))

        def l_land_no_snapshot():
            r = lworld("l-no-snapshot")
            r.write(FUP, "- [ ] a\n- [ ] s\n")
            r.write(FB, ENTRY % "mine")
            got = do_land(r)
            tip = main_of(r)
            check(got["status"] == "landed" and changed(r, tip) == [FB, FUP] and show(r, tip, FUP) == "- [ ] a\n- [ ] s"
                  and porcelain(r) == "",
                  "l_land_no_snapshot: with no snapshot every dirty session file lands, the leftover included (%r)" % got)

        def l_land_behind():
            r = lworld("l-behind")
            o = clone(r, "l-behind-other")
            o.write("specifications/PRD-ACME-1-x/notes.md", "n\n")
            o.commit_all("ACME-1 Add notes")
            o.git("push", "-q", "origin", "main")
            r.git("fetch", "-q", "origin")
            local, up = main_of(r), ref(r, "refs/remotes/origin/main")
            r.write(FB, ENTRY % "mine")
            got = do_land(r)
            tip = main_of(r)
            check(local != up and got["status"] == "landed" and got["sha"] == tip and r.git("rev-parse", tip + "^") == up
                  and got["pushed"] is False,
                  "l_land_behind: built on origin/main, local main fast-forwarded to it (%r)" % got)

        def l_land_absent():
            r = lworld("l-absent")
            r.git("branch", "-q", "-D", "main")
            up = ref(r, "refs/remotes/origin/main")
            r.write(FB, ENTRY % "mine")
            got = do_land(r)
            check(got["status"] == "landed" and main_of(r) == got["sha"] and r.git("rev-parse", got["sha"] + "^") == up,
                  "l_land_absent: no local main: created at the landed commit, on origin/main (%r)" % got)

        def l_land_behind_checked_out():
            r = lworld("l-behind-co")
            o = clone(r, "l-behind-co-other")
            o.write("specifications/PRD-ACME-1-x/notes.md", "n\n")
            o.commit_all("ACME-1 Add notes")
            o.git("push", "-q", "origin", "main")
            r.git("fetch", "-q", "origin")
            w2 = worktree(r, "l-behind-co-w2")
            local, up = main_of(r), ref(r, "refs/remotes/origin/main")
            check(w2.git("status", "--porcelain") == "" and w2.git("diff", "--cached") == "",
                  "l_land_behind_checked_out: w2 clean before")
            r.write(FB, ENTRY % "mine")
            got = do_land(r)
            check(got["status"] == "landed" and got["pushed"] is True and on_origin(r) == got["sha"]
                  and r.git("rev-parse", got["sha"] + "^") == up and main_of(r) == local and local != up,
                  "l_land_behind_checked_out: pushed by refspec on origin/main, local main unmoved (%r)" % got)
            check(w2.git("status", "--porcelain") == "" and w2.git("diff", "--cached") == "" and porcelain(r) == ""
                  and held(r) == [] and held_refs(r) == [],
                  "l_land_behind_checked_out: w2 as it was, no staged reversal (%r, %r)"
                  % (w2.git("status", "--porcelain"), w2.git("diff", "--cached")))

        def l_land_checked_out_no_push():
            def refused_before(r):
                path = os.path.join(r.path, ".git", "workflows", "push-refused", "main")
                os.makedirs(os.path.dirname(path))
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write("2026-11-01\n")
            for name, setup, ref_name, detail, permanent in (
                    ("l-co-no-remote", no_origin, "refs/heads/main", "no-remote", True),
                    ("l-co-offline", lambda r: r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git")),
                     "origin/main", "failed", False),
                    ("l-co-refused", refused_before, "origin/main", "refused-before", False)):
                r = lworld(name)
                w2 = worktree(r, name + "-w2")
                setup(r)
                local, up = main_of(r), on_origin(r)
                r.write(FB, ENTRY % "mine")
                got = do_land(r, default_ref=ref_name)
                entries = held(r)
                refused = got.get("refused") or {}
                check(got["status"] == "held" and refused.get("reason") == "checked-out"
                      and (refused.get("detail") or {}).get("outcome") == detail
                      and refused.get("permanent") is permanent and same_path(refused.get("path"), w2.path)
                      and got["pushed"] is False and main_of(r) == local and on_origin(r) == up
                      and "?? " + FB in porcelain(r) and len(entries) == 1 and entries[0]["refused"] == refused
                      and entries[0]["tip"] is None and held_refs(r) == [HELD + entries[0]["c2"]] and got["sha"] == entries[0]["c2"],
                      "l_land_checked_out_no_push: %s held, %s, local main unmoved, the file dirty (%r, %r)"
                      % (name, detail, got, entries))

        def l_land_diverged():
            r = lworld("l-diverged")
            r.git("switch", "-q", "main")
            r.write("notes.md", "the user's\n")
            user = r.commit_all("the user's own commit")
            r.git("switch", "-q", LB)
            r.write(FB, ENTRY % "mine")
            got = do_land(r)
            check(got["status"] == "landed" and r.git("rev-parse", got["sha"] + "^") == user and main_of(r) == got["sha"],
                  "l_land_diverged: landed on top of the user's unpushed commit (%r)" % got)

        def l_land_nothing():
            r = lworld("l-nothing")
            old = main_of(r)
            got = do_land(r)
            check(got["status"] == "nothing" and got["sha"] is None and main_of(r) == old and held(r) == [],
                  "l_land_nothing: nothing dirty, nothing landed (%r)" % got)

        def main_gains(r, body):
            r.git("switch", "-q", "main")
            r.write(FUP, body)
            r.commit_all("ACME-1 follow-ups on main")
            r.git("push", "-q", "origin", "main")
            r.git("switch", "-q", LB)

        def l_land_there():
            r = lworld("l-there")
            main_gains(r, "- [ ] a\n- [ ] b\n")
            old = main_of(r)
            r.write(FUP, "- [ ] a\n- [ ] b\n")
            got = do_land(r)
            check(got["status"] == "there" and got["sha"] is None and main_of(r) == old and got["lifted"] == [FUP]
                  and porcelain(r) == "" and held(r) == [],
                  "l_land_there: the run's line already on main: no commit, the file lifted (%r)" % got)

        def l_land_there_refused():
            r = lworld("l-there-refused", extra=[(COST, COST_BODY)])
            main_gains(r, "- [ ] a\n- [ ] b\n")
            old = main_of(r)
            r.write(FUP, "- [ ] a\n- [ ] b\n")
            r.write(COST, EDITED)
            got = do_land(r)
            entries = held(r)
            stuck = got.get("stuck") or {}
            check(got["status"] == "held" and main_of(r) == old and got["lifted"] == [FUP] and read(r, FUP) == "- [ ] a\n"
                  and read(r, COST) == EDITED and stuck.get("paths") == [COST] and got["refused"] == stuck.get("refused")
                  and (got["refused"] or {}).get("reason") == "edited" and (got["refused"] or {}).get("permanent") is True
                  and len(entries) == 1 and list(entries[0]["paths"]) == [COST],
                  "l_land_there_refused: no commit, the path already there lifted, the other held, permanent (%r, %r)"
                  % (got, entries))

        def l_land_hook():
            r = lworld("l-hook")
            hook(os.path.join(r.path, ".git", "hooks", "pre-commit"), "exit 1\n")
            r.write(FB, ENTRY % "mine")
            got = do_land(r)
            check(got["status"] == "landed" and main_of(r) == got["sha"], "l_land_hook: no pre-commit hook runs (%r)" % got)

        def l_land_on_move():
            r = lworld("l-on-move")
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            seen = []

            def on_move(pending):
                seen.append((dict(pending), main_of(r), [dict(e) for e in held(r)]))
            got = do_land(r, on_move=on_move)
            p, at, entries = seen[0] if seen else ({}, None, [])
            check(len(seen) == 1 and set(p) == PENDING and at == old and p.get("old") == old and p.get("tip") == got["sha"]
                  and p.get("here") is False and p.get("remote_only") is False and p.get("onto") == "main"
                  and p.get("moves") == [] and p.get("kept") == [] and len(entries) == 1
                  and entries[0]["refused"] is None
                  and entries[0]["tip"] == got["sha"]
                  and entries[0]["c2"] == p.get("c2") and held(r) == [] and held_refs(r) == [],
                  "l_land_on_move: called before the move, the journal entry written; none left after (%r)" % (seen,))

        def l_land_partial():
            r = lworld("l-partial", extra=[(COST, COST_BODY)])
            r.write(COST, EDITED)
            r.write(FB, ENTRY % "mine")
            got = do_land(r)
            entries = held(r)
            stuck = got.get("stuck") or {}
            check(got["status"] == "landed" and changed(r, main_of(r)) == [FB] and stuck.get("paths") == [COST]
                  and (stuck.get("refused") or {}).get("reason") == "edited"
                  and (stuck.get("refused") or {}).get("permanent") is True
                  and len(entries) == 1 and list(entries[0]["paths"]) == [COST] and entries[0]["c2"] == stuck.get("sha")
                  and entries[0]["refused"] == stuck.get("refused")
                  and changed(r, entries[0]["c2"]) == [COST] and r.git("rev-parse", entries[0]["c2"] + "^") == entries[0]["c1"]
                  and read(r, COST) == EDITED and read(r, FB) is None and got["lifted"] == [FB],
                  "l_land_partial: the feedback file lands, the cost file held alone, permanent, unlifted (%r, %r)"
                  % (got, entries))
            r = lworld("l-partial-alone", extra=[(COST, COST_BODY)])
            old = main_of(r)
            r.write(COST, EDITED)
            got = do_land(r)
            check(got["status"] == "held" and (got["refused"] or {}).get("permanent") is True and main_of(r) == old
                  and len(held(r)) == 1 and read(r, COST) == EDITED,
                  "l_land_partial: the cost file alone is held, permanent (%r)" % got)

        def l_land_locked():
            r = lworld("l-locked")
            r.write(FB, ENTRY % "mine")
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            refs = r.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads", "refs/remotes")
            try:
                got = do_land(r)
            finally:
                os.remove(lock)
            entries = held(r)
            refused = got["refused"] or {}
            check(got["status"] == "held" and refused == {"reason": "locked", "path": ".git/index.lock", "detail": None,
                                                           "permanent": False}
                  and r.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads", "refs/remotes") == refs
                  and len(entries) == 1 and entries[0]["refused"] == refused and entries[0]["c2"] == got["sha"]
                  and entries[0]["tip"] is None and list(entries[0]["paths"]) == [FB]
                  and held_refs(r) == [HELD + got["sha"]] and got["lifted"] == [] and read(r, FB) == ENTRY % "mine",
                  "l_land_locked: an index.lock at the landing's start holds the change for that cause, transient: "
                  "no branch moved, nothing lifted (%r)" % got)
            # the here form (HEAD on main) holds nothing: locked, nothing moved (specs-repo-git §4 step 1)
            r = lworld("l-locked-here", stay=False)
            r.write(FB, ENTRY % "mine")
            open(lock.replace("l-locked", "l-locked-here"), "w").close()
            try:
                got = do_land(r, branch="main")
            finally:
                os.remove(lock.replace("l-locked", "l-locked-here"))
            check(got["status"] == "locked" and (got["refused"] or {}).get("reason") == "locked" and held(r) == []
                  and held_refs(r) == [] and read(r, FB) == ENTRY % "mine",
                  "l_land_locked: in the here form, locked, nothing held (%r)" % got)
            # a resumed journal (end --resume) is left as it stands for a later call: locked, nothing moved or held anew
            r = lworld("l-locked-resume")
            r.write(FB, ENTRY % "mine")
            e = stopped(lambda: do_land(r, on_move=kill))
            before, old = held(r), main_of(r)
            path = os.path.join(r.path, ".git", "index.lock")
            open(path, "w").close()
            try:
                got = do_land(r, resume=e.pending) if e and e.pending else {}
            finally:
                os.remove(path)
            check(got.get("status") == "locked" and held(r) == before and len(before) == 1 and before[0]["tip"]
                  and before[0]["refused"] is None and main_of(r) == old and read(r, FB) == ENTRY % "mine",
                  "l_land_locked: a resumed journal under the lock is left for a later call (%r)" % got)

        def l_land_resume_on_default():
            """A landing's journal is never finished by the here form: resumed with HEAD on <default>, land refuses
            before any write, the journal and main as they were."""
            r = lworld("l-resume-on-default")
            r.write(FB, ENTRY % "mine")
            e = stopped(lambda: do_land(r, on_move=kill))
            before, old = held(r), main_of(r)
            r.git("switch", "-q", "main")
            try:
                do_land(r, branch="main", resume=e.pending if e else None)
                said = None
            except NotRun as x:
                said = str(x)
            check(said and "is not finished with HEAD on main" in said and held(r) == before and len(before) == 1
                  and main_of(r) == old and read(r, FB) == ENTRY % "mine",
                  "l_land_resume_on_default: refused, nothing done (%r)" % said)

        def l_land_old_git():
            fake = os.path.join(tmp, "l-old-git-bin")
            os.makedirs(fake)
            with open(os.path.join(fake, "git"), "w") as fh:
                fh.write('#!/bin/sh\nfor x in "$@"; do\n  if [ "$x" = merge-tree ]; then\n    cat <<\'EOF\'\n'
                         "usage: git merge-tree [--write-tree] [<options>] <branch1> <branch2>\n\n"
                         "    --write-tree          do a real merge instead of a trivial merge\n"
                         "    -X, --strategy-option <option=value>\nEOF\n    exit 129\n  fi\ndone\n"
                         "exec %s \"$@\"\n" % shlex.quote(shutil.which("git")))
            os.chmod(os.path.join(fake, "git"), 0o755)
            plain = lworld("l-old-git-plain")
            plain.write(FB, ENTRY % "mine")
            plain.write(FUP, "- [ ] a\n- [ ] b\n")
            want = do_land(plain)
            r = lworld("l-old-git")
            r.write(FB, ENTRY % "mine")
            r.write(FUP, "- [ ] a\n- [ ] b\n")
            with in_env({"PATH": fake + os.pathsep + os.environ.get("PATH", "")}):
                shim = sb.replay_ok(r.path)
                got = do_land(r)
            check(shim is False and got["status"] == want["status"] == "landed" and got["paths"] == want["paths"]
                  and r.git("rev-parse", got["sha"] + "^{tree}") == plain.git("rev-parse", want["sha"] + "^{tree}")
                  and porcelain(r) == "",
                  "l_land_old_git: under a git without merge-tree --merge-base, the same landing (%r, %r, %r)"
                  % (shim, got, want))

        def l_land_moved():
            for n, status in ((2, "held"), (1, "landed")):
                r = lworld("l-moved-%d" % n)
                old = main_of(r)
                r.write(FB, ENTRY % "mine")
                calls = []
                real = sb.move_branch

                def fake(*args, **kw):
                    calls.append(1)
                    return {"reason": "branch-moved", "path": None} if len(calls) <= n else real(*args, **kw)
                with patched("move_branch", fake):
                    got = do_land(r)
                if n == 2:
                    entries = held(r)
                    check(got["status"] == "held" and got["refused"] == {"reason": "moved", "path": None,
                                                                         "detail": "branch-moved", "permanent": False}
                          and len(calls) == 2 and main_of(r) == old and len(entries) == 1
                          and entries[0]["refused"] == got["refused"] and read(r, FB) == ENTRY % "mine",
                          "l_land_moved: refused twice, held, moved, transient (%r)" % got)
                else:
                    check(got["status"] == "landed" and len(calls) == 2 and main_of(r) == got["sha"] and held(r) == [],
                          "l_land_moved: refused once, landed on the second try (%r)" % got)

        def l_held_chain():
            r = lworld("l-held-chain")
            w2 = worktree(r, "l-held-chain-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            first = do_land(r)
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            second = do_land(r, snap=snap)
            entries = held(r)
            check(first["status"] == "held" and ((first["refused"] or {}).get("detail") or {}).get("outcome") == "failed"
                  and second["status"] == "held" and len(entries) == 2 and second["refused"] == entries[0]["refused"]
                  and snap == {FUP: entries[0]["paths"][FUP]} and entries[1]["c2"] == second["sha"],
                  "l_held_chain: the second landing held behind the first (%r, %r, %r)" % (first, second, entries))
            r.git("worktree", "remove", "--force", w2.path)
            r.git("remote", "set-url", "origin", r.bare)
            got = retry_held(r.path, "main", "origin/main")
            check(show(r, main_of(r), FUP) == "- [ ] a\n- [ ] l1\n- [ ] l2" and len(got["landed"]) == 2
                  and [x["branch"] for x in got["landed"]] == [LB, LB] and read(r, FUP) == "- [ ] a\n"
                  and porcelain(r) == "" and held(r) == [] and held_refs(r) == [],
                  "l_held_chain: both landed in order, each line once, the working copy HEAD's (%r, %r)"
                  % (got, show(r, main_of(r), FUP)))

        def l_held_unrelated():
            r = lworld("l-held-unrelated", extra=[(COST, COST_BODY)])
            r.write(COST, EDITED)
            got = do_land(r)
            check(got["status"] == "held" and got["refused"]["permanent"] is True, "l_held_unrelated: a permanent entry")
            snap = snapshot(r.path)
            r.write(FB, ENTRY % "b")
            got = do_land(r, snap=snap)
            check(got["status"] == "landed" and changed(r, main_of(r)) == [FB] and len(held(r)) == 1,
                  "l_held_unrelated: a permanent entry on A holds back no landing on B (%r)" % got)
            r = lworld("l-held-unrelated-2")
            r.write(FUP, "- [ ] a\n- [ ] x\n")
            with patched("move_branch", locked_move()):
                got = do_land(r)
            check(got["status"] == "held" and got["refused"] == {"reason": "locked", "path": ".git/refs/heads/main.lock",
                                                                 "detail": None, "permanent": False},
                  "l_held_unrelated: a transient entry (%r)" % got)
            snap = snapshot(r.path)
            r.write(FB, ENTRY % "b")
            got = do_land(r, snap=snap)
            check(got["status"] == "landed" and changed(r, main_of(r)) == [FB] and len(held(r)) == 1
                  and got["held_landed"] == [],
                  "l_held_unrelated: a transient entry on A holds back no landing on B (%r)" % got)
            old = main_of(r)
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] x\n- [ ] y\n")
            calls = []
            with patched("move_branch", locked_move(calls)):
                got = do_land(r, snap=snap)
            entries = held(r)
            check(got["status"] == "held" and got["refused"] == entries[0]["refused"] and len(calls) == 1
                  and main_of(r) == old and len(entries) == 2 and entries[1]["c2"] == got["sha"],
                  "l_held_unrelated: a transient entry on A holds a landing on A behind it, unattempted (%r, %r)"
                  % (got, calls))

        def l_held_then_own():
            r = lworld("l-held-then-own")
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            with patched("move_branch", locked_move()):
                do_land(r)
            entry = held(r)[0]
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            got = do_land(r, snap=snap)
            check(snap == {FUP: entry["paths"][FUP]} and got["status"] == "landed" and len(got["held_landed"]) == 1
                  and got["held_landed"][0]["branch"] == LB and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] l1\n- [ ] l2"
                  and read(r, FUP) == "- [ ] a\n" and porcelain(r) == "" and held(r) == [] and held_refs(r) == [],
                  "l_held_then_own: the held entry lands first, then the run's own, the file lifted to the entry's c1 "
                  "(%r, %r)" % (got, read(r, FUP)))

        def l_held_then_own_there():
            # as l_held_then_own, but main already holds the run's own line: the own change is there, never journalled,
            # so no carry reaches it, and only the walk-back through the held entry lifts the file to HEAD's version
            r = lworld("l-held-then-own-there")
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            with patched("move_branch", locked_move()):
                do_land(r)
            snap = snapshot(r.path)
            o = clone(r, "l-held-then-own-there-other")
            o.write(FUP, "- [ ] a\n- [ ] l2\n")
            o.commit_all("ACME-1 l2")
            o.git("push", "-q", "origin", "main")
            r.git("fetch", "-q", "origin")
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            got = do_land(r, snap=snap)
            check(got["status"] == "there" and len(got["held_landed"]) == 1 and read(r, FUP) == "- [ ] a\n"
                  and porcelain(r) == "" and held(r) == [],
                  "l_held_then_own_there: the entry lands, the own change is there, the file lifted to HEAD's (%r, %r)"
                  % (got, read(r, FUP)))

        def l_retry_local_only():
            r = lworld("l-retry-local")
            worktree(r, "l-retry-local-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            do_land(r)
            r.git("remote", "set-url", "origin", r.bare)
            up = on_origin(r)
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            got = do_land(r, snap=snap, retry_remote=False)
            check(got["status"] == "held" and on_origin(r) == up and len(held(r)) == 2 and got["held_landed"] == [],
                  "l_retry_local_only: retry_remote=False leaves the entry, the own change held behind it (%r)" % got)
            got = do_land(r, snap=snap)
            o = subprocess.run(["git", "-C", r.bare, "show", "main:" + FUP], stdout=subprocess.PIPE).stdout.decode()
            # the run's own change is the second entry's: it lands as that entry, the own change then there, or -- both
            # commits made in one second, so one c2 -- as the own change itself
            check(got["held_landed"] and got["held_landed"][0]["branch"] == LB and o == "- [ ] a\n- [ ] l1\n- [ ] l2\n"
                  and got["status"] in ("there", "landed") and held(r) == [] and held_refs(r) == []
                  and read(r, FUP) == "- [ ] a\n",
                  "l_retry_local_only: with the default the entries are pushed by refspec (%r, %r)" % (got, o))

        def l_retry_budget():
            r = lworld("l-retry-budget")
            worktree(r, "l-retry-budget-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FB, ENTRY % "one")
            do_land(r)
            snap = snapshot(r.path)
            r.write(FB2, ENTRY % "two")
            do_land(r, snap=snap)
            r.git("remote", "set-url", "origin", r.bare)
            calls = []

            def budget(cost):
                calls.append(cost)
                if len(calls) == 2:
                    raise _Stop()
            raised = False
            try:
                retry_held(r.path, "main", "origin/main", check=budget)
            except _Stop:
                raised = True
            entries = held(r)
            tip = on_origin(r)
            check(raised and calls == [PUSH_COST, PUSH_COST] and len(entries) == 1 and list(entries[0]["paths"]) == [FB2]
                  and show(r, tip, FB) != "" and show(r, tip, FB2) == "" and read(r, FB) is None
                  and read(r, FB2) == ENTRY % "two",
                  "l_retry_budget: the first landed, the second kept, _Stop propagated (%r, %r, %r)" % (raised, calls, entries))

        def first_move_only(calls):
            """move_branch real for its first call, locked after it: the held entry lands, the run's own stays held."""
            real = sb.move_branch

            def fake(*args, **kw):
                calls.append(1)
                return real(*args, **kw) if len(calls) == 1 else locked_move()(*args, **kw)
            return fake

        def stopped_chain(name):
            """E1 and E2 held, chained on follow-ups.md (E2 started from E1's version); a _Stop lands E1 alone."""
            r = lworld(name)
            worktree(r, name + "-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            do_land(r)
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            do_land(r, snap=snap)
            second = held(r)[1]
            r.git("remote", "set-url", "origin", r.bare)
            calls = []

            def budget(cost):
                calls.append(cost)
                if len(calls) == 2:
                    raise _Stop()
            try:
                retry_held(r.path, "main", "origin/main", check=budget)
            except _Stop:
                pass
            return r, second

        def l_chain_partly_stopped():
            r, second = stopped_chain("l-chain-stopped")
            left = held(r)
            check(len(left) == 1 and left[0]["c2"] == second["c2"]
                  and left[0].get("lift") == {FUP: r.git("rev-parse", "HEAD:" + FUP)}
                  and read(r, FUP) == "- [ ] a\n- [ ] l1\n- [ ] l2\n",
                  "l_chain_partly_stopped: E1 landed, E2 kept with its lift where the chain began (%r)" % left)
            got = retry_held(r.path, "main", "origin/main")
            o = subprocess.run(["git", "-C", r.bare, "show", "main:" + FUP], stdout=subprocess.PIPE).stdout.decode()
            check(len(got["landed"]) == 1 and o == "- [ ] a\n- [ ] l1\n- [ ] l2\n" and read(r, FUP) == "- [ ] a\n"
                  and porcelain(r) == "" and held(r) == [],
                  "l_chain_partly_stopped: E2 lands later, the working copy back where the chain began, no E1 line "
                  "(%r, %r)" % (got, read(r, FUP)))

        def l_chain_lift_pruned():
            # an override whose blob git no longer holds (an entry held past gc's pruning): the lift falls back to c1
            r, second = stopped_chain("l-chain-pruned")
            missing = "0" * 39 + "1"
            g["_held_put"](r.path, dict(held(r)[0], lift={FUP: missing}))
            got = retry_held(r.path, "main", "origin/main")
            check(len(got["landed"]) == 1 and read(r, FUP) == "- [ ] a\n- [ ] l1\n" and held(r) == []
                  and got["landed"][0]["lifted"] == [{"path": FUP, "blob": r.git("rev-parse", second["c1"] + ":" + FUP)}],
                  "l_chain_lift_pruned: a missing override blob falls back to the entry's c1 (%r)" % got)

        def l_chain_partly_own():
            # E1 lands in land's step 3; the run's own change, started from E1's version, then stays held
            r = lworld("l-chain-own")
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            with patched("move_branch", locked_move()):
                do_land(r)
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            calls = []
            with patched("move_branch", first_move_only(calls)):
                got = do_land(r, snap=snap)
            left = held(r)
            check(len(got["held_landed"]) == 1 and got["status"] == "held" and len(calls) == 2 and len(left) == 1
                  and left[0]["c2"] == got["sha"] and left[0].get("lift") == {FUP: r.git("rev-parse", "HEAD:" + FUP)}
                  and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] l1",
                  "l_chain_partly_own: E1 landed, the own change held with its lift where the chain began (%r, %r)"
                  % (got, left))
            got = retry_held(r.path, "main", "origin/main")
            check(len(got["landed"]) == 1 and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] l1\n- [ ] l2"
                  and read(r, FUP) == "- [ ] a\n" and porcelain(r) == "" and held(r) == [],
                  "l_chain_partly_own: it lands later, the working copy back where the chain began, no E1 line (%r, %r)"
                  % (got, read(r, FUP)))

        def l_chain_delete_behind_whole():
            # P1 (final re-review 2): a whole file uncommitted at the run's start is never part of a landing's change, so
            # a deletion of one held behind a whole-file edit chains nothing: E1 resume.md v0 -> v1 stays held, the
            # run's deletion is left out (kept), main keeps v0; the held stage then finds E1's file changed since it was
            # held and drops E1 (P8), the deletion left in the working tree for a later commit on the branch
            r = lworld("l-chain-delete", extra=[(RESUME, "v0\n")])
            r.write(RESUME, "v1\n")
            with patched("move_branch", locked_move()):
                do_land(r)
            snap = snapshot(r.path)
            os.remove(os.path.join(r.path, RESUME))
            calls = []
            with patched("move_branch", first_move_only(calls)):
                got = do_land(r, snap=snap)
            left = held(r)
            check(got["status"] == "nothing" and got["kept"] == [RESUME] and len(left) == 1
                  and show(r, main_of(r), RESUME) == "v0",
                  "l_chain_delete_behind_whole: the deletion left out of the change, E1 still held (%r, %r)" % (got, left))
            got = retry_held(r.path, "main", "origin/main")
            check(got["landed"] == [] and got["dropped"] == 1 and held(r) == [] and show(r, main_of(r), RESUME) == "v0"
                  and read(r, RESUME) is None,
                  "l_chain_delete_behind_whole: E1 dropped, its file changed since it was held; the deletion left in the "
                  "working tree (%r, %r)" % (got, read(r, RESUME)))

        def l_cli_detail():
            r = lworld("l-cli-detail")
            worktree(r, "l-cli-detail-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FB, ENTRY % "mine")
            got = cli("--specs", r.path, "land", "--branch", LB, "--default-ref", "origin/main", "--command", "/feedback",
                      env=r.env)
            detail = got.get("detail") or {}
            check(got["_rc"] == 0 and got.get("status") == "held" and got.get("reason") == "checked-out"
                  and isinstance(detail, dict) and set(detail) == set(CHECKED_OUT_DETAIL)
                  and detail["outcome"] == "failed" and "nowhere.git" in (detail["text"] or "")
                  and got.get("permanent") is False,
                  "l_cli_detail: a checked-out hold prints its detail whole: the refspec push's outcome and reason (%r)"
                  % got)

        def l_checked_out_detail():
            """Each alternative of reason.land.checked-out, worded from a real refusal of the landing's remote path:
            the detail the held record keeps, mapped by checked_out_values, filled whole."""
            _, lines = _flow()
            nowhere = os.path.join(tmp, "nowhere.git")

            def moved_on(r):  # another clone pushes to origin's main; this clone does not fetch it
                other = r.path + "-other"
                subprocess.run(["git", "clone", "-q", r.bare, other], check=True)
                o = Repo(other)
                o.git("config", "user.email", "t@example.invalid")
                o.git("config", "user.name", "t")
                o.git("config", "commit.gpgsign", "false")
                o.git("switch", "-q", "main")
                o.write("notes.md", "a teammate's\n")
                o.commit_all("a teammate's commit")
                o.git("push", "-q", "origin", "main")

            def refused_before(r):
                path = os.path.join(r.path, ".git", "workflows", "push-refused", "main")
                os.makedirs(os.path.dirname(path))
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write("2026-11-01\n")

            def record_of(r):
                return os.path.join(r.path, ".git", "workflows", "push-refused", "main")

            cases = (
                ("l-cod-failed", lambda r: r.git("remote", "set-url", "origin", nowhere), "origin/main",
                 lambda r, d: d["outcome"] == "failed" and d["text"].startswith("fatal:") and "nowhere.git" in d["text"]
                 and d["remote"] is None and d["record"] is None and d["date"] is None,
                 lambda r, d: "and the push of the commit by refspec failed (%s)" % d["text"]),
                ("l-cod-rejected", moved_on, "origin/main",
                 lambda r, d: d["outcome"] == "rejected" and d["text"].startswith("[rejected]"),
                 lambda r, d: "and the push of the commit by refspec failed (%s)" % d["text"]),
                ("l-cod-no-remote", no_origin, "refs/heads/main",
                 lambda r, d: d == dict(dict.fromkeys(CHECKED_OUT_DETAIL), outcome="no-remote"),
                 lambda r, d: "and there is no origin to push the commit to"),
                ("l-cod-elsewhere", lambda r: r.git("config", "remote.pushDefault", "fork"), "origin/main",
                 lambda r, d: d == dict(dict.fromkeys(CHECKED_OUT_DETAIL), outcome="elsewhere", remote="fork"),
                 lambda r, d: "and your git configuration pushes main to fork, not to origin"),
                ("l-cod-remote-deleted",
                 lambda r: subprocess.run(["git", "-C", r.bare, "update-ref", "-d", "refs/heads/main"], check=True),
                 "origin/main",
                 lambda r, d: d == dict(dict.fromkeys(CHECKED_OUT_DETAIL), outcome="remote-deleted"),
                 lambda r, d: "and origin has no main"),
                # (3): no <default-ref> to build on -- never built on local main -- held as origin has no main
                # origin no longer has main, and the clone's tracking ref is pruned (fetch --prune)
                ("l-cod-origin-lacks",
                 lambda r: (subprocess.run(["git", "-C", r.bare, "update-ref", "-d", "refs/heads/main"], check=True),
                            r.git("fetch", "-q", "--prune", "origin")),
                 "origin/main",
                 lambda r, d: d == dict(dict.fromkeys(CHECKED_OUT_DETAIL), outcome="origin-lacks"),
                 lambda r, d: "and origin has no main"),
                ("l-cod-refused", lambda r: hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 1\n"), "origin/main",
                 lambda r, d: d["outcome"] == "refused" and d["text"] == "pre-receive hook declined"
                 and same_path(d["record"], record_of(r)) and d["date"] is None and d["record_error"] is None,
                 lambda r, d: "and origin refuses pushes to main (pre-receive hook declined), so from the next run "
                              "session-branch mode takes these files"),
            )
            rendered, takes = [], {}
            for name, setup, default_ref, holds, want in cases:
                r = lworld(name)
                w2 = worktree(r, name + "-w2")
                setup(r)
                r.write(FB, ENTRY % "mine")
                got = do_land(r, default_ref=default_ref)
                refused = got.get("refused") or {}
                d = refused.get("detail") or {}
                entries = held(r)
                try:
                    ok = isinstance(d, dict) and set(d) == set(CHECKED_OUT_DETAIL) and holds(r, d)
                except (KeyError, TypeError, AttributeError):
                    ok = False
                values = checked_out_values(lines, d)
                try:
                    line = lines.fill("reason.land.checked-out", dict(values or {}, **{"<path>": refused.get("path"),
                                                                                     "<default>": "main"}))
                except ValueError as e:
                    line = "fill: %s" % e
                rendered.append(line)
                check(got["status"] == "held" and refused.get("reason") == "checked-out" and ok
                      and len(entries) == 1 and entries[0]["refused"] == refused
                      and line == "another worktree, %s, has main checked out, %s" % (refused.get("path"), want(r, d)),
                      "l_checked_out_detail: %s's detail kept in the held record, and its clause worded whole (%r, %r)"
                      % (name, d, line))
                check(same_path(refused.get("path"), w2.path), "l_checked_out_detail: %s names the worktree" % name)
                takes[name] = mode_takes(refused)
            check(not any("failed (failed)" in x or "()" in x for x in rendered),
                  "l_checked_out_detail: no clause reads failed (failed) or an empty () (%r)" % rendered)
            def clause(refused):
                values = checked_out_values(lines, refused.get("detail"))
                try:
                    return lines.fill("reason.land.checked-out", dict(values or {}, **{"<path>": refused.get("path"),
                                                                                     "<default>": "main"}))
                except ValueError as e:
                    return "fill: %s" % e

            # refused-before, a record another session wrote mid-run: worded as row.refused-before words it
            r = lworld("l-cod-refused-before")
            w2 = worktree(r, "l-cod-refused-before-w2")
            r.write(FB, ENTRY % "mine")
            snap = snapshot(r.path)  # the run's start
            refused_before(r)        # mid-run
            r.write(FB2, ENTRY % "mine too")
            got = do_land(r, snap=snap)
            refused = got.get("refused") or {}
            d = refused.get("detail") or {}
            line = clause(refused)
            check(d == dict(dict.fromkeys(CHECKED_OUT_DETAIL), outcome="refused-before", date="2026-11-01",
                            record=record_of(r)) and held(r)[0]["refused"] == refused and refused.get("permanent") is False
                  and line == "another worktree, %s, has main checked out, and origin refused pushes to main on "
                              "2026-11-01 (%s), so from the next run session-branch mode takes these files"
                              % (refused.get("path"), record_of(r))
                  and same_path(refused.get("path"), w2.path) and sb.mode(r.path, "main")["mode"] == "on",
                  "l_checked_out_detail: refused-before, its record written mid-run, worded whole from the record's "
                  "date and path; the mode it names is on (%r, %r)" % (d, line))
            rendered.append(line)
            takes["l-cod-refused-before"] = mode_takes(refused)

            # refused, its record writable neither way: the unrecorded form, naming the configuration write's error
            r = lworld("l-cod-unrecorded")
            w2 = worktree(r, "l-cod-unrecorded-w2")
            hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 1\n")
            os.makedirs(os.path.join(r.path, ".git", "workflows"), exist_ok=True)
            with open(os.path.join(r.path, ".git", "workflows", "push-refused"), "w", encoding="utf-8") as fh:
                fh.write("a file where the record's directory would go\n")
            lock = os.path.join(r.path, ".git", "config.lock")
            with open(lock, "w", encoding="utf-8") as fh:
                fh.write("")
            r.write(FB, ENTRY % "mine")
            try:
                got = do_land(r)
            finally:
                os.remove(lock)
            refused = got.get("refused") or {}
            d = refused.get("detail") or {}
            line = clause(refused)
            error = d.get("record_error") or ""
            check(set(d) == set(CHECKED_OUT_DETAIL) and d["outcome"] == "refused"
                  and d["text"] == "pre-receive hook declined" and d["record"] is None and "config" in error
                  and held(r)[0]["refused"] == refused
                  and line == "another worktree, %s, has main checked out, and origin refuses pushes to main "
                              "(pre-receive hook declined), but this could not be recorded (%s, the configuration "
                              "write's), so a later run pushes main again" % (refused.get("path"), error)
                  and sb.refusal_record(r.path, "main") is None and sb.mode(r.path, "main")["mode"] == "off",
                  "l_checked_out_detail: refused with its record unwritable, worded in the unrecorded form, naming the "
                  "configuration write's error; no record, the mode off (%r, %r)" % (d, line))
            rendered.append(line)
            takes["l-cod-unrecorded"] = mode_takes(refused)
            check(takes == {"l-cod-failed": False, "l-cod-rejected": False, "l-cod-no-remote": False,
                            "l-cod-elsewhere": False, "l-cod-remote-deleted": False, "l-cod-origin-lacks": False,
                            "l-cod-refused": True,
                            "l-cod-refused-before": True, "l-cod-unrecorded": False}
                  and mode_takes(None) is False and mode_takes({"reason": "moved", "detail": "branch-moved"}) is False,
                  "l_checked_out_detail: mode_takes is true exactly where a record turns session-branch mode on, so the "
                  "held lines take their mode tail (%r)" % takes)
            check(not any("failed (failed)" in x or "()" in x or "None" in x for x in rendered[-2:]),
                  "l_checked_out_detail: neither new form reads an empty () or None (%r)" % rendered[-2:])

            # every detail _land_change can produce: from each push outcome _push_detail meets, each row _row_detail
            # meets, origin-lacks (no <default-ref> to build on, specs-repo-git §4 step 1 (3)), and None (held with no
            # push tried); checked_out_values and the fill never raise
            pushes = [{"outcome": o, "reason": why, "record": rec, "record_error": err}
                      for o, why in (("failed", "fatal: x"), ("failed", None), ("rejected", "[rejected] (fetch first)"),
                                     ("rejected", None))
                      for rec, err in ((None, None),)]
            pushes += [{"outcome": "refused", "reason": why, "record": rec, "record_error": err}
                       for why in ("hook declined", "", None)
                       for rec, err in (("/s/.git/workflows/push-refused/main", None),
                                        ("branch.main.workflowsPushRefused", None), (None, "error: could not lock"))]
            rows = [{"row": "no-remote"}, {"row": "elsewhere", "remote": "fork"}, {"row": "remote-deleted"}]
            rows += [{"row": "refused-before", "record": rec, "date": date}
                     for rec, date in (("/s/.git/workflows/push-refused/main", "2026-11-01"),
                                       ("/s/.git/workflows/push-refused/main", "an earlier run"),
                                       ("branch.main.workflowsPushRefused", "2026-11-01"))]
            details = ([_push_detail(x) for x in pushes] + [_row_detail(x) for x in rows]
                       + [_checked_out_detail("origin-lacks"), None])
            problems = []
            for detail in details:
                try:
                    values = checked_out_values(lines, detail)
                    if values is None:
                        if detail is not None:
                            problems.append("no values for %r" % (detail,))
                        continue
                    line = lines.fill("reason.land.checked-out", dict(values, **{"<path>": "/w2", "<default>": "main"}))
                    if "()" in line or "None" in line:
                        problems.append(line)
                except Exception as e:  # any raise is the failure this check is for
                    problems.append("%r raised %s: %s" % (detail, type(e).__name__, e))
            check(problems == [] and len(details) == 21,
                  "l_checked_out_detail: every detail _land_change can produce maps and fills without raising (%r)"
                  % problems)
            # a push that gave no reason takes the words a status line with none gives (specs-repo-git §6)
            got = _push_detail({"outcome": "failed", "reason": None, "record": None})
            check(got["text"] == lines.T["app.why.failed.none"] and checked_out_values(lines, None) is None
                  and checked_out_values(lines, "failed") is None,
                  "l_checked_out_detail: a failed push with no reason reads no status line; no detail object, no values "
                  "(%r)" % got)

        def l_cli_local_retries():
            """Minor 5: the CLI's landing retries earlier held entries locally only, as end's does (§4 step 1): one that
            would need the refspec push stays held, and holds back the run's change on its path."""
            r = lworld("l-cli-local")
            worktree(r, "l-cli-local-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            first = do_land(r)
            r.git("remote", "set-url", "origin", r.bare)  # the refspec push would go through now
            snap_file = os.path.join(tmp, "l-cli-local.snap.json")
            with open(snap_file, "w", encoding="utf-8") as fh:
                json.dump(snapshot(r.path), fh)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            up, local = on_origin(r), main_of(r)
            got = cli("--specs", r.path, "land", "--branch", LB, "--default-ref", "origin/main", "--command", "/feedback",
                      "--snapshot", snap_file, env=r.env)
            detail = got.get("detail") or {}
            check(first["status"] == "held" and got["_rc"] == 0 and got.get("status") == "held"
                  and got.get("reason") == "checked-out" and detail.get("outcome") == "failed"
                  and got.get("pushed") is False and on_origin(r) == up and main_of(r) == local and len(held(r)) == 2,
                  "l_cli_local_retries: the earlier entry stays held, not pushed by refspec, and holds the run's change "
                  "back (%r)" % got)

        def l_here_resume_unfinished():
            """Minor 6: an end --resume whose here-form journal is at neither its tip nor its old commit keeps the change
            with a reason of its own, unfinished, never moved."""
            r = here_world("l-here-unfinished")
            e = stopped(lambda: here_land(r, on_move=kill))
            r.git("commit", "-q", "--allow-empty", "-m", "elsewhere")
            got = here_land(r, resume=e.pending if e else None) if e else {}
            refused = got.get("refused") or {}
            _, lines = _flow()
            clause = lines.fill(LAND_REASONS.get(refused.get("reason"), "reason.land.moved"), {"<branch>": "main",
                                                                                              "<default>": "main"})
            check(got.get("status") == "kept" and refused.get("reason") == "unfinished" and held(r) == []
                  and held_refs(r) == [] and read(r, FUP) == "- [ ] a\n- [ ] mine\n" and read(r, FB) == ENTRY % "mine"
                  and clause == ("main moved on without the commit this run was making on it when it was cut off, "
                                 "so that commit was dropped unfinished")
                  and refused.get("permanent") is True,
                  "l_here_resume_unfinished: kept as unfinished, nothing held, the files as they stand (%r, %r)"
                  % (got, clause))

        def l_split_collision():
            # review exp2: P8 rebuilds a transient entry, then every path left is refused, in one retry_held call; the
            # split's stuck commit is the rebuilt entry's own commit (same tree, parent, message and, pinned, dates)
            r = lworld("l-split-collision", extra=[(RESUME, "v0\n")])
            os.remove(os.path.join(r.path, RESUME))
            r.write(FB, ENTRY % "mine")
            with patched("move_branch", locked_move()):
                do_land(r)
            r.write(FB, ENTRY % "edited")  # P8: the feedback file leaves the entry
            w = worktree(r, "l-split-collision-w2")
            w.write(RESUME, "v9\n")
            w.git("commit", "-q", "-am", "ACME-1 resume.md changed on main")  # the deletion is now refused, deleted
            r.git("worktree", "remove", "--force", w.path)
            with in_env({"GIT_COMMITTER_DATE": "1793700000 +0000", "GIT_AUTHOR_DATE": "1793700000 +0000"}):
                got = retry_held(r.path, "main", "origin/main")
            entries, sha = held(r), ((got["stuck"] or [{}])[0]).get("sha")
            check(len(got["stuck"]) == 1 and got["stuck"][0]["refused"]["reason"] == "deleted" and len(entries) == 1
                  and entries[0]["c2"] == sha and list(entries[0]["paths"]) == [RESUME]
                  and entries[0]["refused"]["permanent"] is True and held_refs(r) == [HELD + sha]
                  and read(r, RESUME) is None and read(r, FB) == ENTRY % "edited",
                  "l_split_collision: the stuck entry reported stands in the record with its ref (%r, %r)"
                  % (got, entries))

        def chain_committed(name, held_own):
            # review exp4: a held entry's version the user then commits on the stayed branch; a later run starts from
            # HEAD's version, with no snapshot of the path, so it does not start from the held entry
            r = lworld(name)
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            with patched("move_branch", locked_move()):
                do_land(r)
            r.git("commit", "-q", "-am", "B-2 the user commits follow-ups.md as it stands")
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            if held_own:
                with patched("move_branch", locked_move()):
                    do_land(r, snap=snap)
                after = held(r)  # land's P8 has dropped the committed entry: the own change is held alone
                return r, (snap, after), retry_held(r.path, "main", "origin/main")
            return r, snap, do_land(r, snap=snap)

        def l_chain_committed_land():
            r, snap, got = chain_committed("l-chain-committed-land", False)
            check(snap == {} and got["status"] == "landed" and got["held_landed"] == []
                  and read(r, FUP) == "- [ ] a\n- [ ] l1\n" and r.git("diff", "HEAD", "--", FUP) == ""
                  and porcelain(r) == "" and held(r) == [] and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] l2",
                  "l_chain_committed_land: P8 drops the committed entry in land's step 3 as retry_held does: main "
                  "holds the later change alone, the working copy HEAD's (%r, %r, %r)"
                  % (got, read(r, FUP), show(r, main_of(r), FUP)))

        def l_chain_committed_retry():
            r, (snap, after), got = chain_committed("l-chain-committed-retry", True)
            check(snap == {} and len(after) == 1 and list(after[0]["paths"]) == [FUP]
                  and r.git("rev-parse", after[0]["c1"] + "^") == r.git("rev-parse", "HEAD")
                  and len(got["landed"]) == 1 and got["dropped"] == 0 and read(r, FUP) == "- [ ] a\n- [ ] l1\n"
                  and r.git("diff", "HEAD", "--", FUP) == "" and porcelain(r) == "" and held(r) == []
                  and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] l2",
                  "l_chain_committed_retry: land's P8 drops the committed entry, the later change is held alone and "
                  "retry_held lands it alone, the working copy HEAD's (%r, %r, %r, %r)"
                  % (after, got, read(r, FUP), show(r, main_of(r), FUP)))

        def l_land_pending_own():
            # review exp3: a held entry lands in step 3, then the run's own change fails before its journal
            r = lworld("l-pending-own")
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            with patched("move_branch", locked_move()):
                do_land(r)
            first = held(r)[0]
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            real, calls = sb.own_change, []

            def fail_second(*args, **kw):
                calls.append(1)
                if len(calls) == 2:
                    raise OSError("git failed in the run's own change")
                return real(*args, **kw)
            with patched("own_change", fail_second):
                e = stopped(lambda: do_land(r, snap=snap))
            entries = held(r)
            check(e is not None and e.pending is None and len(entries) == 1 and entries[0]["c2"] == first["c2"]
                  and entries[0]["refused"] is None and entries[0]["tip"] == main_of(r),
                  "l_land_pending_own: LandStopped carries no held entry's pending; that journal stays in its record "
                  "(%r, %r)" % (e and e.pending, entries))

        def l_land_resume_chain():
            # review exp6: the run is killed after its move, before its lift; another run's change, started from its
            # version, is held; end --resume lands that entry in step 3 and lifts the chain from the resumed change
            r = lworld("l-resume-chain")
            r.write(FUP, "- [ ] a\n- [ ] own\n")

            def no_lift(*_args):
                raise OSError("killed before the lift")
            with patched("write_from", no_lift):
                e = stopped(lambda: do_land(r))
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] own\n- [ ] other\n")
            with patched("move_branch", locked_move()):
                do_land(r, snap=snap)
            got = do_land(r, resume=e.pending if e else None)
            check(e is not None and got["status"] == "landed" and len(got["held_landed"]) == 1 and got["lifted"] == [FUP]
                  and read(r, FUP) == "- [ ] a\n" and porcelain(r) == "" and held(r) == []
                  and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] own\n- [ ] other",
                  "l_land_resume_chain: the resumed change is the oldest of the chain it starts, the file lifted to "
                  "HEAD's (%r, %r)" % (got, read(r, FUP)))

        def l_retry_held_blocked():
            # a blocked entry's failed row, and its record, carry the refusal of the entry it waits for
            r = lworld("l-retry-blocked")
            worktree(r, "l-retry-blocked-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            do_land(r)
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            do_land(r, snap=snap)
            stale = {"reason": "locked", "path": ".git/refs/heads/main.lock", "detail": None, "permanent": False}
            g["_held_put"](r.path, dict(held(r)[1], refused=stale))
            got = retry_held(r.path, "main", "origin/main")
            first, second = held(r)
            check([x["refused"] for x in got["failed"]] == [first["refused"], first["refused"]]
                  and first["refused"]["reason"] == "checked-out" and second["refused"] == first["refused"],
                  "l_retry_held_blocked: the blocked entry reports, and records, the refusal it waits on (%r, %r)"
                  % (got["failed"], held(r)))

        def l_cli_retry_partial():
            # land --retry-held stopped by an error after a landing reports that landing before the error
            r = lworld("l-retry-partial")
            r.write(FB, ENTRY % "one")
            with patched("move_branch", locked_move()):
                do_land(r)
            snap = snapshot(r.path)
            r.write(FB2, ENTRY % "two")
            with patched("move_branch", locked_move()):
                do_land(r, snap=snap)
            real, calls = sb.own_change, []

            def fail_second(*args, **kw):
                calls.append(1)
                if len(calls) == 2:
                    raise OSError("git failed in the second entry")
                return real(*args, **kw)
            args = argparse.Namespace(specs=r.path, default_ref="origin/main", retry_held=True, drop_held=None,
                                      branch=None, command=None, commit_key=None, snapshot=None, here=False,
                                      open_run=False, register_rebuild=None)
            with patched("own_change", fail_second):
                got = land_cli(args)
            check("git failed in the second entry" in (got.get("error") or "") and len(got["landed"]) == 1
                  and got["landed"][0]["paths"] == [FB] and got["landed"][0]["sha"] == main_of(r)
                  and got["landed"][0]["lifted"] == [] and got["failed"] == [] and got["stuck"] == [],
                  "l_cli_retry_partial: the landing made before the error is reported with it (%r)" % got)

        def l_retry_held_edited():
            r = lworld("l-retry-edited")
            worktree(r, "l-retry-edited-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FUP, "- [ ] a\n- [ ] x\n")
            r.write(FB, ENTRY % "mine")
            do_land(r)
            first = held(r)[0]
            r.write(FB, ENTRY % "edited")
            got = retry_held(r.path, "main", "origin/main", retry_remote=False)
            entries = held(r)
            check(sorted(first["paths"]) == [FB, FUP] and len(entries) == 1 and list(entries[0]["paths"]) == [FUP]
                  and entries[0]["c2"] != first["c2"] and held_refs(r) == [HELD + entries[0]["c2"]]
                  and changed(r, entries[0]["c2"]) == [FUP] and read(r, FB) == ENTRY % "edited"
                  and got["dropped"] == 0 and len(got["failed"]) == 1,
                  "l_retry_held_edited: a held file edited since leaves the entry, rebuilt without it (%r, %r)"
                  % (got, entries))
            r.write(FUP, "- [ ] a\n- [ ] x\n- [ ] edited\n")
            got = retry_held(r.path, "main", "origin/main", retry_remote=False)
            check(got["dropped"] == 1 and held(r) == [] and held_refs(r) == [] and read(r, FB) == ENTRY % "edited"
                  and read(r, FUP) == "- [ ] a\n- [ ] x\n- [ ] edited\n",
                  "l_retry_held_edited: an entry left with no file is dropped, the files untouched (%r)" % got)

        def l_retry_held_on_default():
            r = lworld("l-retry-default")
            r.write(FB, ENTRY % "mine")
            with patched("move_branch", locked_move()):
                do_land(r)
            old = main_of(r)
            r.git("switch", "-q", "main")
            got = retry_held(r.path, "main", "origin/main")
            check(got["dropped"] == 1 and got["landed"] == [] and held(r) == [] and held_refs(r) == []
                  and read(r, FB) == ENTRY % "mine" and main_of(r) == old,
                  "l_retry_held_on_default: HEAD on main drops the entry, its file left (%r)" % got)

        def l_retry_held_journal():
            r = lworld("l-retry-journal")
            r.write(FB, ENTRY % "mine")

            def no_lift(*_args):
                raise OSError("killed before the lift")
            with patched("write_from", no_lift):
                e = stopped(lambda: do_land(r))
            tip = main_of(r)
            entries = held(r)
            check(e is not None and (e.pending or {}).get("tip") == tip and len(entries) == 1
                  and entries[0]["refused"] is None and entries[0]["tip"] == tip and read(r, FB) == ENTRY % "mine",
                  "l_retry_held_journal: a kill after the move leaves the journal entry (%r)" % entries)
            got = retry_held(r.path, "main", "origin/main")
            check(got["finished"] == [{"sha": tip, "here": False, "files": 1, "branch": "prd/B-2-y",
                                       "lifted": [{"path": FB, "blob": None}]}]
                  and main_of(r) == tip and read(r, FB) is None and held(r) == [] and held_refs(r) == [],
                  "l_retry_held_journal: main holds the tip: lifted only (%r)" % got)

        def l_retry_held_journal_before_move():
            r = lworld("l-retry-before-move")
            old = main_of(r)
            r.write(FUP, "- [ ] a\n- [ ] b\n")
            e = stopped(lambda: do_land(r, on_move=kill))
            entries = held(r)
            check(e is not None and main_of(r) == old and len(entries) == 1 and entries[0]["refused"] is None
                  and entries[0]["tip"] == (e.pending or {}).get("tip") and read(r, FUP) == "- [ ] a\n- [ ] b\n",
                  "l_retry_held_journal_before_move: a kill before the move leaves main at old (%r)" % entries)
            got = retry_held(r.path, "main", "origin/main")
            check(r.git("rev-list", "--count", old + "..main") == "1" and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] b"
                  and read(r, FUP) == "- [ ] a\n" and len(got["landed"]) == 1 and held(r) == [],
                  "l_retry_held_journal_before_move: landed again, main moved once, lifted after (%r)" % got)

        def l_held_rebuild():
            r = lworld("l-held-rebuild")
            r.write(FUP, "- [ ] a\n- [ ] x\n")
            r.write(FB, ENTRY % "mine")
            with patched("move_branch", locked_move()):
                do_land(r)
            entry = dict(held(r)[0], lift={FUP: r.git("rev-parse", "HEAD:" + FUP), FB: None})
            g["_held_put"](r.path, entry)  # a lift override on each path, as a partly landed chain leaves one
            new = held_rebuild(r.path, entry, [FB])
            check(new is not None and list(new["paths"]) == [FUP] and new["c2"] != entry["c2"] and held(r) == [new]
                  and held_refs(r) == [HELD + new["c2"]] and changed(r, new["c2"]) == [FUP]
                  and r.git("rev-parse", new["c2"] + "^") == entry["c1"] and read(r, FB) == ENTRY % "mine"
                  and new.get("lift") == {FUP: entry["lift"][FUP]},
                  "l_held_rebuild: rebuilt without the path, its lift override with it (%r)" % new)
            gone = held_rebuild(r.path, new, [FUP])
            check(gone is None and held(r) == [] and held_refs(r) == [] and read(r, FUP) == "- [ ] a\n- [ ] x\n",
                  "l_held_rebuild: an entry left with no file is dropped")

        def l_held_drop():
            r = lworld("l-held-drop")
            r.write(FB, ENTRY % "mine")
            with patched("move_branch", locked_move()):
                do_land(r)
            sha7 = held(r)[0]["c2"][:7]
            got = cli("--specs", r.path, "land", "--default-ref", "origin/main", "--drop-held", sha7, env=r.env)
            check(got["_rc"] == 0 and {k for k in got if not k.startswith("_")} == {"dropped", "sha7", "error"}
                  and got.get("dropped") is True and got.get("sha7") == sha7 and held(r) == [] and held_refs(r) == []
                  and read(r, FB) == ENTRY % "mine",
                  "l_held_drop: --drop-held removes the entry and its ref, the file untouched (%r)" % got)
            got = cli("--specs", r.path, "land", "--default-ref", "origin/main", "--drop-held", sha7, env=r.env)
            check(got["_rc"] == 0 and got.get("dropped") is False, "l_held_drop: a second drop finds none (%r)" % got)

        def l_held_orphan_refs():
            r = lworld("l-orphans")
            w2 = worktree(r, "l-orphans-w2")
            base, tree = r.git("rev-parse", "main"), r.git("rev-parse", "main^{tree}")

            def commit_at(seconds_ago, message):
                stamp = "%d +0000" % (time.time() - seconds_ago)
                return r.git("commit-tree", tree, "-p", base, "-m", message,
                             env={"GIT_COMMITTER_DATE": stamp, "GIT_AUTHOR_DATE": stamp})
            listed, old, young, late = (commit_at(7200, "listed"), commit_at(7200, "old"), commit_at(60, "young"),
                                        commit_at(7200, "late"))
            entry = {"c1": base, "c2": listed, "old": None, "tip": None, "onto": "main", "branch": "main",
                     "remote_only": False, "kind": None, "merged": None, "command": "/feedback",
                     "refused": {"reason": "locked", "path": None, "detail": None, "permanent": False},
                     "date": "2026-11-10", "paths": {}, "here": False, "index_before": None}
            g["_held_put"](w2.path, entry)
            for c in (old, young):
                r.git("update-ref", HELD + c, c)
            check(sorted(held_refs(r)) == sorted(HELD + c for c in (listed, old, young)) and held(w2) == [entry]
                  and held(r) == [], "l_held_orphan_refs: three refs, one listed by w2's record")
            r.git("switch", "-q", "--detach")
            retry_held(r.path, "main", "origin/main")
            check(sorted(held_refs(r)) == sorted(HELD + c for c in (listed, old, young)),
                  "l_held_orphan_refs: on a detached HEAD nothing is done, the orphan sweep included (P9) (%r)"
                  % held_refs(r))
            r.git("switch", "-q", LB)
            real, made = g["_read_held"], []

            def racing(path):
                if not made:  # another worktree writes a held ref while this sweep reads the records
                    made.append(r.git("update-ref", HELD + late, late))
                return real(path)
            g["_read_held"] = racing
            try:
                retry_held(r.path, "main", "origin/main")
            finally:
                g["_read_held"] = real
            check(sorted(held_refs(r)) == sorted(HELD + c for c in (listed, young, late)),
                  "l_held_orphan_refs: the unlisted ref over an hour old removed; w2's, one younger than an hour, and one "
                  "written while the records were read, all kept (%r)" % held_refs(r))

        def here_world(name, extra=()):
            r = lworld(name, extra=extra, stay=False)
            r.write(FUP, "- [ ] a\n- [ ] mine\n")
            r.write(FB, ENTRY % "mine")
            return r

        def lock_after_move(r):
            real = sb.git

            def fake(root, *args, **kw):
                out = real(root, *args, **kw)
                if args and args[0] == "update-ref" and "refs/heads/main" in args:
                    open(os.path.join(r.path, ".git", "index.lock"), "w").close()
                return out
            return fake

        def here_land(r, snap=None, **kw):
            return land(r.path, "main", "main", "origin/main", MSG, snap, **kw)

        def l_land_here():
            r = lworld("l-here", stay=False)
            r.write(FUP, "- [ ] a\n- [ ] s\n")
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] s\n- [ ] mine\n")
            r.write(FB, ENTRY % "mine")
            old = main_of(r)
            mtimes = [os.stat(os.path.join(r.path, p)).st_mtime_ns for p in (FUP, FB)]
            got = here_land(r, snap)
            tip = main_of(r)
            diff = [x for x in r.git("diff", "HEAD", "--", FUP).splitlines()
                    if x.startswith(("+", "-")) and not x.startswith(("+++", "---"))]
            check(got["status"] == "landed" and got["sha"] == tip and r.git("rev-parse", tip + "^") == old
                  and changed(r, tip) == [FB, FUP] and show(r, tip, FUP) == "- [ ] a\n- [ ] mine" and got["onto"] == "main"
                  and got["lifted"] == [] and got["pushed"] is False,
                  "l_land_here: main advanced by one commit holding only the run's own (%r)" % got)
            check(r.git("diff", "--cached") == "" and diff == ["+- [ ] s"]
                  and [os.stat(os.path.join(r.path, p)).st_mtime_ns for p in (FUP, FB)] == mtimes
                  and held(r) == [] and held_refs(r) == [],
                  "l_land_here: the index restored, S's line alone left, no file written, no journal (%r, %r)"
                  % (r.git("diff", "--cached"), diff))

        def l_land_here_refused():
            r = lworld("l-here-refused", extra=[(COST, COST_BODY)], stay=False)
            old = main_of(r)
            r.write(COST, EDITED)
            r.write(FB, ENTRY % "mine")
            got = here_land(r)
            check(got["status"] == "kept" and (got["refused"] or {}).get("reason") == "edited" and main_of(r) == old
                  and held(r) == [] and held_refs(r) == [] and read(r, COST) == EDITED,
                  "l_land_here_refused: a refusal keeps the whole change, nothing moved, no journal (%r)" % got)

        def l_land_here_recheck_and_retry():
            r = here_world("l-here-recheck")
            old = main_of(r)
            index_fup = r.git("rev-parse", ":" + FUP)
            with patched("git", lock_after_move(r)):
                e = stopped(lambda: here_land(r))
            tip = main_of(r)
            entries = held(r)
            check(e is not None and (e.pending or {}).get("here") is True and (e.pending or {}).get("tip") == tip
                  and str(e).startswith("main moved to %s, but .git/index.lock stands" % tip[:7])
                  and tip != old and len(entries) == 1 and entries[0]["here"] is True and entries[0]["refused"] is None
                  and entries[0]["index_before"] == {FB: None, FUP: index_fup},
                  "l_land_here_recheck: a lock after the move raises with pending.here, the journal kept (%r)" % entries)
            os.remove(os.path.join(r.path, ".git", "index.lock"))
            check(r.git("diff", "--cached") != "", "l_retry_held_here: the index still on the old tip before")
            got = retry_held(r.path, "main", "origin/main")
            check(got["finished"] == [{"sha": tip, "here": True, "files": 2, "branch": "main", "lifted": []}]
                  and r.git("diff", "--cached") == ""
                  and main_of(r) == tip and held(r) == [] and held_refs(r) == [],
                  "l_retry_held_here: the index restored from index_before, a new file included (%r)" % got)
            # the user stages follow-ups.md after the kill: that path's index entry is theirs and stays (exp5)
            r = here_world("l-here-recheck-staged")
            with patched("git", lock_after_move(r)):
                stopped(lambda: here_land(r))
            os.remove(os.path.join(r.path, ".git", "index.lock"))
            r.write(FUP, "- [ ] a\n- [ ] mine\n- [ ] staged by the user\n")
            r.git("add", FUP)
            staged = r.git("rev-parse", ":" + FUP)
            got = retry_held(r.path, "main", "origin/main")
            check(len(got["finished"]) == 1 and r.git("rev-parse", ":" + FUP) == staged
                  and r.git("diff", "--cached", "--name-only") == FUP and held(r) == [],
                  "l_retry_held_here_staged: a path the user staged after the kill stays as they staged it, the rest "
                  "restored "
                  "(%r, %r)" % (got, r.git("diff", "--cached", "--name-only")))

        def l_retry_held_here_old():
            r = here_world("l-here-old")
            old = main_of(r)
            e = stopped(lambda: here_land(r, on_move=kill))
            check(e is not None and main_of(r) == old and held(r)[0]["here"] is True,
                  "l_retry_held_here_old: a kill before the move")
            got = retry_held(r.path, "main", "origin/main")
            check(r.git("rev-list", "--count", old + "..main") == "1" and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] mine"
                  and r.git("diff", "--cached") == "" and len(got["finished"]) == 1 and held(r) == [],
                  "l_retry_held_here_old: the here form again, one commit (%r)" % got)

        def l_retry_held_here_elsewhere():
            r = here_world("l-here-elsewhere")
            stopped(lambda: here_land(r, on_move=kill))
            r.git("commit", "-q", "--allow-empty", "-m", "elsewhere")
            got = retry_held(r.path, "main", "origin/main")
            check(got["dropped"] == 1 and got["finished"] == [] and held(r) == [] and held_refs(r) == []
                  and read(r, FUP) == "- [ ] a\n- [ ] mine\n" and read(r, FB) == ENTRY % "mine",
                  "l_retry_held_here_elsewhere: main at neither: dropped, the files untouched (%r)" % got)

        def l_retry_held_here_ancestor():
            r = here_world("l-here-ancestor")
            with patched("git", lock_after_move(r)):
                stopped(lambda: here_land(r))
            tip = main_of(r)
            os.remove(os.path.join(r.path, ".git", "index.lock"))
            r.write("notes.md", "n\n")
            r.git("add", "notes.md")
            r.git("commit", "-q", "-m", "on top", "--", "notes.md")
            check(main_of(r) != tip and r.git("rev-parse", "main^") == tip
                  and r.git("diff", "--cached") != "", "l_retry_held_here_ancestor: main one commit past the tip")
            got = retry_held(r.path, "main", "origin/main")
            check(len(got["finished"]) == 1 and got["dropped"] == 0 and r.git("diff", "--cached") == "" and held(r) == [],
                  "l_retry_held_here_ancestor: the tip an ancestor: the index restored, finished (%r)" % got)

        def l_land_resume():
            r = lworld("l-resume")
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            e = stopped(lambda: do_land(r, on_move=kill))
            r.write(FB2, ENTRY % "after")  # written after the kill: no part of the pending change
            got = do_land(r, resume=e.pending if e else None)
            check(e is not None and got["status"] == "landed" and got["held_landed"] == [] and held(r) == []
                  and held_refs(r) == [] and r.git("rev-list", "--count", old + "..main") == "1"
                  and changed(r, main_of(r)) == [FB] and read(r, FB) is None and read(r, FB2) == ENTRY % "after",
                  "l_land_resume: the pending landed again, alone, its journal entry never a held one (%r)" % got)

        def l_land_register():
            r = lworld("l-register")
            r.write(FB, ENTRY % "mine")
            canned = {"before_remote": {"web": {"o1": 1}}, "before_run": {"web": {"o2": 3}},
                      "after": {"web": {"o1": 2, "o2": 1}}}
            real = sb.own_change

            def fake(*args, **kw):
                return dict(real(*args, **kw), numbers=canned)
            with patched("own_change", fake):
                got = do_land(r)
            check(got["status"] == "landed" and got["moves"] and got["moves"] == sb._moves([canned]),
                  "l_land_register: moves as sb._moves gives them (%r)" % got)

        def l_cli_land():
            r = lworld("l-cli")
            r.write(FB, ENTRY % "mine")
            base = ("--specs", r.path, "land", "--branch", LB, "--default-ref", "origin/main", "--command", "/feedback")
            got = cli(*base, env=r.env)
            check(got["_rc"] == 0 and {k for k in got if not k.startswith("_")} == CLI_FIELDS
                  and got.get("status") == "landed" and got.get("sha7") == main_of(r)[:7] and got.get("files") == 1
                  and got.get("paths") == [FB] and got.get("lifted") == [FB] and got.get("default") == "main"
                  and got.get("pushed") is False and got.get("error") is None and got.get("reason") is None
                  and r.git("log", "-1", "--format=%s", "main") == "NOISSUE Add dev-workflows session artifacts (/feedback)",
                  "l_cli_land: landed, the session subject (%r)" % got)
            r.write(FB2, ENTRY % "two")
            got = cli(*base, "--commit-key", "ACME-1", env=r.env)
            check(got.get("status") == "landed"
                  and r.git("log", "-1", "--format=%s", "main") == "ACME-1 Add dev-workflows session artifacts (/feedback)",
                  "l_cli_land: --commit-key opens the subject (%r)" % got)
            r.write(FUP, "- [ ] a\n- [ ] s\n")
            snap = {k: v for k, v in cli("--specs", r.path, "snapshot", env=r.env).items() if not k.startswith("_")}
            check(snap == {FUP: r.git("hash-object", FUP)}, "l_cli_land: snapshot prints the map --snapshot takes (%r)" % snap)
            path = os.path.join(tmp, "l-cli-snapshot.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(snap, fh)
            r.write(FUP, "- [ ] a\n- [ ] s\n- [ ] one\n")
            got = cli(*base, "--snapshot", path, env=r.env)
            check(got.get("status") == "landed" and show(r, "main", FUP) == "- [ ] a\n- [ ] one"
                  and read(r, FUP) == "- [ ] a\n- [ ] s\n", "l_cli_land: --snapshot <file> honoured (%r)" % got)
            r.write(FUP, "- [ ] a\n- [ ] s\n- [ ] two\n")
            got = cli(*base, "--snapshot", "-", stdin=json.dumps(snap).encode(), env=r.env)
            check(got.get("status") == "landed" and show(r, "main", FUP) == "- [ ] a\n- [ ] one\n- [ ] two"
                  and read(r, FUP) == "- [ ] a\n- [ ] s\n", "l_cli_land: --snapshot - honoured (%r)" % got)
            h = here_world("l-cli-here")
            old = main_of(h)
            got = cli("--specs", h.path, "land", "--branch", "main", "--default-ref", "origin/main", "--command",
                      "/feedback", "--here", env=h.env)
            check(got.get("status") == "landed" and got.get("sha7") == main_of(h)[:7]
                  and h.git("rev-parse", "main^") == old and h.git("diff", "--cached") == "" and got.get("lifted") == [],
                  "l_cli_land: --here on main (%r)" % got)
            got = cli("--specs", r.path, "land", "--default-ref", "origin/main", "--retry-held", env=r.env)
            check(got["_rc"] == 0 and {k for k in got if not k.startswith("_")} == {"landed", "finished", "failed", "stuck",
                                                                                     "dropped", "error"},
                  "l_cli_land: --retry-held prints its object (%r)" % got)

        def l_cli_start_dirty():
            """§4 step 1 (1)'s guard by hand (specs-repo-git §4 step 1's *By hand*): land --snapshot leaves the
            overwritten snapshot paths out of the change, in the landing and the here form, and prints them as kept; an
            appended file's added entries still travel; the flag the pass before this one added is gone."""
            got = {}
            for form in ("stay", "here"):
                r = lworld("l-cli-start-dirty-" + form, stay=form == "stay")
                r.write(RESUME, "v1\n")
                r.write(FUP, "- [ ] a\n- [ ] open's\n")
                snap = {k: v for k, v in cli("--specs", r.path, "snapshot", env=r.env).items() if not k.startswith("_")}
                r.write(RESUME, "v2\n")
                r.write(FUP, "- [ ] a\n- [ ] open's\n- [ ] open's later\n")
                r.write(FB, ENTRY % "mine")
                args = ["--specs", r.path, "land", "--branch", LB if form == "stay" else "main", "--default-ref",
                        "origin/main", "--command", "/feedback", "--snapshot", "-"]
                out = cli(*(args + (["--here"] if form == "here" else [])), stdin=json.dumps(snap).encode(), env=r.env)
                c = main_of(r)
                got[form] = (out.get("status"), out.get("kept"), sorted(out.get("paths") or []), read(r, RESUME),
                             "open's later" in show(r, c, FUP))
            r = lworld("l-cli-start-dirty-usage")
            bare = cli("--specs", r.path, "land", "--branch", LB, "--default-ref", "origin/main", "--command",
                       "/feedback", "--open-run", env=r.env)
            check(got == {f: ("landed", [RESUME], sorted([FB, FUP]), "v2\n", True) for f in ("stay", "here")}
                  and one_not_run_line(bare) and "unrecognized arguments: --open-run" in bare["_err"],
                  "l_cli_start_dirty: the start-dirty resume pointer kept out and printed as kept, the follow-up line "
                  "landed, with no flag; --open-run no longer exists (%r, %r)" % (got, bare.get("_err")))

        def l_cli_exit2():
            r = lworld("l-cli-exit2")
            r.write(FB, ENTRY % "mine")
            with patched("move_branch", locked_move()):
                do_land(r)
            r.write(FB2, ENTRY % "two")
            nowhere = os.path.join(tmp, "l-cli-exit2-nowhere")
            os.makedirs(nowhere)

            def state_of():
                with open(held_path(r.path), encoding="utf-8") as fh:
                    return r.git("for-each-ref"), porcelain(r), fh.read()
            before = state_of()
            tail = ("--command", "/feedback")
            for what, args in (
                    ("--branch naming a branch HEAD is not on",
                     ("--specs", r.path, "land", "--branch", "main", "--default-ref", "origin/main") + tail),
                    ("a --default-ref that does not resolve",
                     ("--specs", r.path, "land", "--branch", LB, "--default-ref", "origin/nowhere") + tail),
                    ("--commit-key acme-1",
                     ("--specs", r.path, "land", "--branch", LB, "--default-ref", "origin/main", "--commit-key", "acme-1")
                     + tail),
                    ("no repository", ("--specs", nowhere, "land", "--branch", LB, "--default-ref", "origin/main") + tail),
                    ("--specs below the top level",
                     ("--specs", os.path.join(r.path, "specifications"), "land", "--branch", LB, "--default-ref",
                      "origin/main") + tail)):
                got = cli(*args, env=r.env)
                check(one_not_run_line(got) and "_stdout" not in got and not got["_raw"].strip() and state_of() == before,
                      "l_cli_exit2: %s exits 2 with one line, nothing changed (%r)" % (what, got))

        def l_sb_reused():
            with open(me, encoding="utf-8") as fh:
                src = fh.read()
            found = re.findall(r"^def (own_change|tree_with|commit_tree|move_branch|replay_commits)\b", src, re.M)
            check(found == [], "l_sb_reused: specs-git.py imports session-branch.py's functions, defining none (%r)" % found)

        g = globals()
        for name, fn in sorted(locals().items()):
            if name.startswith("l_") and callable(fn):
                case(name, fn)

    def scenarios_replay(tmp):
        state, lines = _flow()
        FEED = "specifications/PRD-ACME-1-x/dev-workflows/feedback/"
        REG = "security/web/register.json"
        END_FIELDS = {"print", "line", "row", "sha7", "files", "branch", "pushed", "next", "record", "error"}
        TIMED = ("session-branch.py did not finish within 420 s, so %s may already stand on the replay (git -C \"%s\" log "
                 "-1 %s shows it); the next run whose preflight gets past its guards retries the push where it stands on "
                 "%s or %s is a plugin branch")

        def plain(specs, branch):
            return 'run git -C "%s" pull --rebase --no-autostash origin %s, then git -C "%s" push origin %s' % (
                specs, branch, specs, branch)

        def rejected(opening, branch, clause, remedy):
            return ("%s — push REJECTED: origin's %s has commits this one lacks, and the run could not take them in: %s%s"
                    % (opening, branch, clause, "; " + remedy if remedy else ""))

        def committed(sha7, branch, n=1):
            return "Specs repo: committed %s (%s) on %s" % (sha7, "1 file" if n == 1 else "%d files" % n, branch)

        def replayed(opening, branch, k, tail=""):
            return ("%s — pushed after a replay: origin's %s had moved on, so the run replayed its %d commit(s) onto it%s"
                    % (opening, branch, k, tail))

        def refused_tail(branch, specs, record_path, day):
            return ("to land the commits on local %s, put them on a branch of their own and open a pull request from it — "
                    "git -C \"%s\" branch --no-track session-files-%s %s && git -C \"%s\" push -u origin session-files-%s — then, "
                    "standing on %s, git -C \"%s\" reset --keep origin/%s; once origin takes pushes to %s again, rm \"%s\""
                    % (branch, specs, day, branch, specs, day, branch, specs, branch, branch, record_path))

        def other_pushes(r, name, path, body="o\n", branch="main"):
            o = clone(r, name)
            if branch != "main":
                o.git("switch", "-q", branch)
            o.write(path, body)
            o.commit_all("NOISSUE another clone's session file")
            o.git("push", "-q", "origin", branch)
            return o

        def ended(r, env, command="/create-ard"):
            """end on a push origin rejects as non-fast-forward: the next it hands the run."""
            got = run_end(env, command)
            nxt = got.get("next") or {}
            check(got["_rc"] == 0 and " replay --for end --command %s --branch " % command in nxt.get("run", ""),
                  "%s: end hands the rejected push to the replay (%r)" % (os.path.basename(r.path), got))
            return nxt if nxt.get("run") else {"run": "false", "on_timeout": "false"}

        def origin_files(r, branch, prefix):
            p = subprocess.run(["git", "-C", r.bare, "ls-tree", "-r", "--name-only", branch, "--", prefix],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            return set(p.stdout.decode().split())

        def replay_cli(env, for_, command, branch, *more, specs=None):
            return cli("--specs", specs or env["SPECS_PATH"], "replay", "--for", for_, "--command", command,
                       "--branch", branch, *more, env=env)

        def resume_line(specs, command, *args):
            return " ".join(["python3", shlex.quote(me), "--specs", shlex.quote(specs), "start", "--command", command]
                            + list(args) + ["--resume"])

        def replay_line(specs, command, branch, *more):
            return " ".join(["python3", shlex.quote(me), "--specs", shlex.quote(specs), "replay", "--for", "start",
                             "--command", command, "--branch", branch] + list(more))

        def own_started(env, command):
            """The started of <command>'s record, which every next a replay --for start returns names it by, whatever
            --started the call was given (none, in these cases)."""
            return (record(env, command) or {}).get("started") or ""

        # r_replayed
        r, env = world(tmp, "r-replayed")
        seed(env, "/create-ard")
        o = other_pushes(r, "r-replayed-other", FEED + "y.md")
        r.write(FEED + "x.md", "x\n")
        nxt = ended(r, env)
        mine = head(r)
        got = shell(nxt["run"], env)
        h = head(r)
        want = replayed(committed(h[:7], "main"), "main", 1)
        check(got["_rc"] == 0 and got.get("row") == "replayed" and got.get("print") == [want] and got.get("line") == want
              and got.get("sha7") == h[:7] and got.get("files") == 1 and got.get("branch") == "main"
              and got.get("pushed") is True and got.get("record") == "found" and got.get("next") is None
              and got.get("error") is None and {k for k in got if not k.startswith("_")} == END_FIELDS,
              "r_replayed: next.run prints end's object, the replayed and pushed row (%r)" % got)
        check(h != mine and r.git("rev-parse", "HEAD~1") == head(o) and on_origin(r) == h
              and origin_files(r, "main", FEED) == {FEED + "x.md", FEED + "y.md"} and record(env, "/create-ard") is None,
              "r_replayed: origin/main holds both files, the record removed")

        # r_appends: the declined append and the repeated guard block, as end renders them
        r, env = world(tmp, "r-appends")
        seed(env, "/create-ard", declined=["notes.md"], guard_block="BLOCK")
        r.write("notes.md", "n\n")
        other_pushes(r, "r-appends-other", FEED + "y.md")
        r.write(FEED + "x.md", "x\n")
        got = shell(ended(r, env)["run"], env)
        want = (replayed(committed(head(r)[:7], "main"), "main", 1)
                + "; the deliverable at notes.md remains uncommitted, as you asked")
        check(got.get("row") == "replayed" and got.get("print") == [want, "BLOCK"] and got.get("line") == want
              and record(env, "/create-ard") is None, "r_appends: every append end gives (%r)" % got)

        # r_dropped
        r, env = world(tmp, "r-dropped")
        seed(env, "/create-ard")
        o = other_pushes(r, "r-dropped-other", FEED + "x.md", "x\n")
        r.write(FEED + "x.md", "x\n")
        got = shell(ended(r, env)["run"], env)
        theirs = head(o)
        want = ("%s — not pushed, and nothing is left to push: origin's main had moved on and already holds every change "
                "main carries, so main now stands on it" % committed(theirs[:7], "main"))
        check(got.get("row") == "already-there" and got.get("print") == [want] and got.get("sha7") == theirs[:7]
              and got.get("pushed") is False and head(r) == theirs and record(env, "/create-ard") is None,
              "r_dropped: the same change on origin is already there, main moved onto it (%r)" % got)
        r, env = world(tmp, "r-dropped-one")
        seed(env, "/create-ard")
        r.write(FEED + "z.md", "z\n")
        r.commit_all("NOISSUE an earlier run's feedback")
        o = other_pushes(r, "r-dropped-one-other", FEED + "x.md", "x\n")
        r.write(FEED + "x.md", "x\n")
        got = shell(ended(r, env)["run"], env)
        h = head(r)
        want = replayed(committed(h[:7], "main"), "main", 2, ", 1 of them already there and dropped")
        check(got.get("row") == "replayed" and got.get("print") == [want] and on_origin(r) == h
              and r.git("rev-parse", "HEAD~1") == head(o), "r_dropped: one of two commits already there, the <D> clause (%r)" % got)

        # r_register_rebuild
        for name, rebuild, clause in (
                ("r-register", None, "both sides changed the security register security/web/, which only a rebuild "
                                     "settles, and this command hands the run no register.py to rebuild it"),
                ("r-register-failed", "fails", "both sides changed the security register security/web/, which only a "
                                               "rebuild settles, and that rebuild failed")):
            r, env = world(tmp, name)
            r.write(REG, '{"findings": []}\n')
            r.commit_all("NOISSUE the register")
            r.git("push", "-q", "origin", "main")
            if rebuild:
                rebuild = os.path.join(tmp, name + "-rebuild.py")
                with open(rebuild, "w", encoding="utf-8") as fh:
                    fh.write("import sys\nsys.exit(1)\n")
            seed(env, "/scan", register_rebuild=rebuild)
            other_pushes(r, name + "-other", REG, '{"findings": ["o"]}\n')
            r.write(REG, '{"findings": ["r"]}\n')
            nxt = ended(r, env, "/scan")
            mine = head(r)
            got = shell(nxt["run"], env)
            want = rejected(committed(mine[:7], "main"), "main", clause, plain(r.path, "main"))
            check(got.get("row") == "rejected" and got.get("print") == [want] and got.get("sha7") == mine[:7]
                  and got.get("pushed") is False and head(r) == mine and on_origin(r) != mine and record(env, "/scan") is None,
                  "r_register_rebuild: %s — push rejected, nothing moved (%r)" % (name, got))

        # r_checked_out: the branch checked out in a second worktree
        r, env = world(tmp, "r-checked-out")
        seed(env, "/create-ard")
        other_pushes(r, "r-checked-out-other", FEED + "y.md")
        r.write(FEED + "x.md", "x\n")
        nxt = ended(r, env)
        mine = head(r)
        r.git("worktree", "add", "-q", "-f", os.path.join(tmp, "r-checked-out-wt"), "main")
        wt = [w for w in sb.checked_out_at(r.path, "main") if os.path.realpath(w) != os.path.realpath(r.path)]
        got = shell(nxt["run"], env)
        want = rejected(committed(mine[:7], "main"), "main", "another worktree, %s, has main checked out" % wt[0],
                        plain(wt[0], "main"))
        check(len(wt) == 1 and got.get("row") == "rejected" and got.get("print") == [want]
              and "switch" not in got.get("line", "switch") and head(r) == mine,
              "r_checked_out: the remedy runs in that worktree, no switch (%r)" % got)
        r, env = world(tmp, "r-checked-out-queued")
        W, W_FEED = "prd/ACME-4-w", "specifications/PRD-ACME-4-w/dev-workflows/feedback/"
        r.git("switch", "-q", "-c", W)
        r.git("push", "-q", "-u", "origin", W)
        other_pushes(r, "r-checked-out-queued-other", W_FEED + "o.md", branch=W)
        r.write(W_FEED + "w.md", "w\n")
        r.commit_all("NOISSUE w")
        r.git("switch", "-q", "main")
        r.git("worktree", "add", "-q", os.path.join(tmp, "r-checked-out-queued-wt"), W)
        wt = sb.checked_out_at(r.path, W)
        seed(env, "/specify", stage="settle-done", pending=[{"branch": W, "set_upstream": False, "standing": "main"}])
        got = replay_cli(env, "start", "/specify", W)
        want = rejected("Specs preflight: " + W, W, "another worktree, %s, has %s checked out" % (wt[0], W), plain(wt[0], W))
        check(len(wt) == 1 and got["_rc"] == 0 and got.get("print") == [want] and "switch" not in got["print"][0],
              "r_checked_out: on a branch the run is not standing on, still the worktree's remedy (%r)" % got)

        # r_timed_out
        r, env = world(tmp, "r-timed-out")
        seed(env, "/create-ard")
        other_pushes(r, "r-timed-out-other", FEED + "y.md")
        r.write(FEED + "x.md", "x\n")
        nxt = ended(r, env)
        mine = head(r)
        got = shell(nxt["on_timeout"], env)
        want = rejected(committed(mine[:7], "main"), "main", TIMED % ("main", r.path, "main", "main", "main"),
                        plain(r.path, "main"))
        check(got["_rc"] == 0 and got.get("row") == "rejected" and got.get("print") == [want] and head(r) == mine
              and on_origin(r) != mine and record(env, "/create-ard") is None,
              "r_timed_out: the 420 s clause, nothing replayed, the record removed (%r)" % got)

        # r_not_run: session-branch.py's replay exits 2 with nothing printed
        r, env = world(tmp, "r-not-run")
        GONE = "prd/ACME-9-gone"
        seed(env, "/create-ard", stage="end-replay", end_commit={"sha7": "abc1234", "files": 2, "branch": GONE,
                                                                 "paths": [], "hook_paths": []})
        got = replay_cli(env, "end", "/create-ard", GONE)
        want = rejected(committed("abc1234", GONE, 2), GONE,
                        "session-branch.py could not run (session-branch: not run (no such branch: %s))" % GONE,
                        plain(r.path, GONE))
        check(got["_rc"] == 0 and got.get("row") == "rejected" and got.get("print") == [want]
              and record(env, "/create-ard") is None, "r_not_run: the could-not-run clause (%r)" % got)

        # r_refused_form: the replay moved the branch and origin refused its push
        r, env = world(tmp, "r-refused")
        r.git("switch", "-q", "-c", PLUGIN)
        r.git("push", "-q", "-u", "origin", PLUGIN)
        seed(env, "/create-prd", branch=PLUGIN)
        other_pushes(r, "r-refused-other", FEED + "y.md", branch=PLUGIN)
        hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 1\n")
        r.write(FEED + "x.md", "x\n")
        nxt = ended(r, env, "/create-prd")
        got, days, ldays = dated(lambda: shell(nxt["run"], env))
        h = head(r)
        rec_file = os.path.join(r.path, ".git", "workflows", "push-refused", PLUGIN)
        want = [["%s — origin's %s had moved on, so the run replayed its 1 commit(s) onto it and moved %s there, but push "
                 "REFUSED by origin (pre-receive hook declined): a rule there takes no push of %s, so this is recorded and "
                 "no later run pushes it; %s" % (committed(h[:7], PLUGIN), PLUGIN, PLUGIN, PLUGIN,
                                                  refused_tail(PLUGIN, r.path, rec_file, d))] for d in days]
        check(got.get("row") == "moved" and got.get("print") in want and got.get("pushed") is False
              and on_origin(r, PLUGIN) != h and record(env, "/create-prd") is None,
              "r_refused_form: moved, not pushed, in its refused form (%r)" % got)
        check(os.path.isfile(rec_file) and open(rec_file, encoding="utf-8").read() in [d + "\n" for d in ldays],
              "r_refused_form: the push-refusal record written as step 6 writes it")

        # r_start_current: the current branch's replay in §3.4's flush
        r, env = world(tmp, "r-start-current")
        other_pushes(r, "r-start-current-other", FEED + "y.md")
        r.write(FEED + "x.md", "x\n")
        r.commit_all("NOISSUE Add dev-workflows session artifacts (/specify)")
        args = {"specs": r.path, "keys": ["ACME-1", "ACME-1-01"], "commit_key": "ACME-1", "register_rebuild": None}
        seed(env, "/specify", stage="flush", args=args)
        got = replay_cli(env, "start", "/specify", "main")
        h = head(r)
        resume = resume_line(r.path, "/specify", "--key", "ACME-1", "--key", "ACME-1-01", "--commit-key", "ACME-1",
                             "--started", own_started(env, "/specify"))
        check(got["_rc"] == 0 and {k for k in got if not k.startswith("_")} == {"print", "next", "error"}
              and got.get("print") == [replayed("Specs preflight: main", "main", 1)] and got.get("error") is None
              and got.get("next") == {"run": resume, "timeout_ms": 600000, "on_timeout": None} and on_origin(r) == h,
              "r_start_current: the Specs preflight: form, next names start --resume with the start call's args (%r)" % got)
        check((record(env, "/specify") or {}).get("stage") == "settle",
              "r_start_current: the replay advances the record to the settle loop (%r)" % record(env, "/specify"))
        r, env = world(tmp, "r-start-current-timed-out")
        seed(env, "/specify", stage="flush")
        got = replay_cli(env, "start", "/specify", "main", "--timed-out")
        want = rejected("Specs preflight: main", "main", TIMED % ("main", r.path, "main", "main", "main"),
                        plain(r.path, "main"))
        check(got.get("print") == [want]
              and (got.get("next") or {}).get("run") == resume_line(r.path, "/specify", "--started",
                                                                    own_started(env, "/specify")),
              "r_start_current: rejected on the branch the run stands on, the remedy names no switch (%r)" % got)
        r, env = world(tmp, "r-start-current-timed-out-moved")
        seed(env, "/specify", stage="flush")
        r.git("switch", "-q", "-c", "elsewhere")
        got = replay_cli(env, "start", "/specify", "main", "--timed-out")
        want = rejected("Specs preflight: main", "main", TIMED % ("main", r.path, "main", "main", "main"),
                        plain(r.path, "main"))
        check(got["_rc"] == 0 and got.get("error") is None and got.get("print") == [want]
              and (got.get("next") or {}).get("run") == resume_line(r.path, "/specify", "--started",
                                                                    own_started(env, "/specify"))
              and (record(env, "/specify") or {}).get("stage") == "settle",
              "r_start_current: --timed-out after another session switched the checkout off the branch still prints the "
              "420 s row and goes on to settle (%r)" % got)

        # r_start_queued: two replays the settle loop queued, each naming the next
        r, env = world(tmp, "r-start-queued")
        Y, Z = "prd/ACME-2-y", "prd/ACME-3-z"
        RES_Y, Z_FEED = "specifications/PRD-ACME-2-y/dev-workflows/resume.md", "specifications/PRD-ACME-3-z/dev-workflows/feedback/"
        r.git("switch", "-q", "-c", Y)
        r.write(RES_Y, "r\n")
        r.commit_all("NOISSUE resume")
        r.git("push", "-q", "-u", "origin", Y)
        r.git("switch", "-q", "-c", Z, "main")
        r.git("push", "-q", "-u", "origin", Z)
        o = clone(r, "r-start-queued-other")
        o.git("switch", "-q", Y)
        o.git("rm", "-q", RES_Y)
        o.git("commit", "-q", "-m", "NOISSUE drop the resume pointer")
        o.git("push", "-q", "origin", Y)
        o.git("switch", "-q", Z)
        o.write(Z_FEED + "o.md", "o\n")
        o.commit_all("NOISSUE o")
        o.git("push", "-q", "origin", Z)
        r.git("switch", "-q", Y)
        r.write(RES_Y, "r2\n")
        r.commit_all("NOISSUE resume again")
        mine_y = head(r)
        r.git("switch", "-q", Z)
        r.write(Z_FEED + "z.md", "z\n")
        r.commit_all("NOISSUE z")
        r.git("switch", "-q", "main")
        pending = [{"branch": Y, "set_upstream": False, "standing": "main"},
                   {"branch": Z, "set_upstream": False, "standing": "main"}]
        seed(env, "/specify", stage="settle-done", pending=pending)
        got = replay_cli(env, "start", "/specify", Y)
        p = r.path
        want = rejected("Specs preflight: " + Y, Y,
                        "both sides changed %s, or the folder holding it, and the run cannot settle it" % RES_Y,
                        'run git -C "%s" switch %s, git -C "%s" pull --rebase --no-autostash origin %s and git -C "%s" push '
                        'origin %s, then switch back to main' % (p, Y, p, Y, p, Y))
        nz = replay_line(p, "/specify", Z, "--started", own_started(env, "/specify"))
        check(got["_rc"] == 0 and got.get("print") == [want] and got.get("error") is None
              and got.get("next") == {"run": nz, "timeout_ms": 420000, "on_timeout": nz + " --timed-out"}
              and r.git("rev-parse", Y) == mine_y and r.git("symbolic-ref", "--short", "HEAD") == "main",
              "r_start_queued: the first replay switches first and back to main after, next names the second (%r)" % got)
        rec = record(env, "/specify") or {}
        check(rec.get("stage") == "settle-done" and rec.get("pending") == pending[1:],
              "r_start_queued: the first branch dropped from pending (%r)" % rec)
        got = shell(nz, env)
        z = r.git("rev-parse", Z)
        check(got["_rc"] == 0 and got.get("print") == [replayed("Specs preflight: " + Z, Z, 1)]
              and got.get("next") == {"run": resume_line(p, "/specify", "--started", own_started(env, "/specify")),
                                      "timeout_ms": 600000, "on_timeout": None}
              and on_origin(r, Z) == z and r.git("rev-parse", Z + "~1") == head(o)
              and r.git("symbolic-ref", "--short", "HEAD") == "main",
              "r_start_queued: the last replay names start --resume, HEAD still on main (%r)" % got)
        rec = record(env, "/specify") or {}
        check(rec.get("stage") == "disposition" and rec.get("pending") == [],
              "r_start_queued: nothing left pending, the record on to §3.5 (%r)" % rec)
        r, env = world(tmp, "r-start-queued-upstream")
        seed(env, "/specify", stage="settle-done", pending=[{"branch": Y, "set_upstream": False, "standing": "main"},
                                                           {"branch": Z, "set_upstream": True, "standing": "main"}])
        got = replay_cli(env, "start", "/specify", Y, "--timed-out")
        check((got.get("next") or {}).get("run") == replay_line(r.path, "/specify", Z, "--set-upstream", "--started",
                                                                own_started(env, "/specify")),
              "r_start_queued: the next replay carries --set-upstream where its queue entry does (%r)" % got)

        # r_start_refused: a queued branch's replay moved it, and origin refused the push
        r, env = world(tmp, "r-start-refused")
        V, V_FEED = "prd/ACME-5-v", "specifications/PRD-ACME-5-v/dev-workflows/feedback/"
        r.git("switch", "-q", "-c", V)
        r.git("push", "-q", "-u", "origin", V)
        o = other_pushes(r, "r-start-refused-other", V_FEED + "o.md", branch=V)
        r.write(V_FEED + "v.md", "v\n")
        r.commit_all("NOISSUE v")
        r.git("switch", "-q", "main")
        hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 1\n")
        seed(env, "/specify", stage="settle-done", pending=[{"branch": V, "set_upstream": False, "standing": "main"}])
        got, days, ldays = dated(lambda: replay_cli(env, "start", "/specify", V))
        rec_file = os.path.join(r.path, ".git", "workflows", "push-refused", V)
        want = [["Specs preflight: %s — origin's %s had moved on, so the run replayed its 1 commit(s) onto it and moved %s "
                 "there, but push REFUSED by origin (pre-receive hook declined): a rule there takes no push of %s, so this "
                 "is recorded and no later run pushes it; %s" % (V, V, V, V, refused_tail(V, r.path, rec_file, d))]
                for d in days]
        check(got["_rc"] == 0 and got.get("print") in want and got.get("error") is None
              and (got.get("next") or {}).get("run") == resume_line(r.path, "/specify", "--started",
                                                                    own_started(env, "/specify"))
              and r.git("rev-parse", V + "~1") == head(o) and on_origin(r, V) == head(o)
              and r.git("symbolic-ref", "--short", "HEAD") == "main",
              "r_start_refused: moved, not pushed, its refused form in Specs preflight: form (%r)" % got)
        check(os.path.isfile(rec_file) and open(rec_file, encoding="utf-8").read() in [d + "\n" for d in ldays]
              and (record(env, "/specify") or {}).get("stage") == "disposition",
              "r_start_refused: the push-refusal record written, the record on to §3.5")

        # r_exit2: nothing found, nothing done
        r, env = world(tmp, "r-exit2")
        got = replay_cli(env, "end", "/create-ard", "main")
        check(one_not_run_line(got) and "_stdout" not in got, "r_exit2: no record is exit 2, one line (%r)" % got)
        seed(env, "/create-ard", stage="end-replay", end_commit={"sha7": head(r)[:7], "files": 1, "branch": "main",
                                                                 "paths": [], "hook_paths": []})
        got = cli("--specs", r.path, "replay", "--for", "end", "--command", "/create-ard", "--branch", "main",
                  env={k: v for k, v in env.items() if k != "CLAUDE_CODE_SESSION_ID"})
        check(one_not_run_line(got), "r_exit2: no session variable is exit 2 (%r)" % got)
        got = replay_cli(env, "end", "/create-ard", "main", specs=os.path.join(r.path, "specifications"))
        check(one_not_run_line(got), "r_exit2: --specs below the top level is exit 2 (%r)" % got)
        for more, what in ((("--for", "middle"), "an unknown --for"), (("--command", "create-ard"), "a command without its slash")):
            args = {"--for": "end", "--command": "/create-ard"}
            args.update(dict(zip(more[::2], more[1::2])))
            got = cli("--specs", r.path, "replay", "--for", args["--for"], "--command", args["--command"], "--branch",
                      "main", env=env)
            check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: "),
                  "r_exit2: %s is a usage exit 2 (%r)" % (what, got))
        check(((record(env, "/create-ard") or {}).get("end_commit") or {}).get("sha7") == head(r)[:7],
              "r_exit2: the record untouched by every exit 2")

        # r_found: once the record is found, never an exit 2
        r, env = world(tmp, "r-found")
        o = other_pushes(r, "r-found-other", FEED + "y.md")
        base = head(r)
        r.write(FEED + "x.md", "x\n")
        r.commit_all("NOISSUE Add dev-workflows session artifacts (/create-ard)")
        mine = head(r)
        for stage, pending_commit in (("end", {"branch": "main", "base": base, "staged": {FEED + "x.md": "0" * 40}}),
                                      ("end-replay", {"branch": "main", "base": base, "staged": {FEED + "x.md": "0" * 40}}),
                                      ("end", {"sha7": mine[:7], "files": 1, "branch": "main", "paths": [], "hook_paths": []})):
            seed(env, "/create-ard", stage=stage, end_commit=pending_commit)
            got = replay_cli(env, "end", "/create-ard", "main")
            line = got.get("line") or ""
            check(got["_rc"] == 0 and got.get("row") is None and got.get("sha7") is None and "end --resume" in (got.get("error") or "")
                  and got.get("print") == [line] and got.get("record") == "found"
                  and line.startswith("Specs repo: NOT FINISHED — the terminal step stopped early (")
                  and head(r) == mine and on_origin(r) == head(o)
                  and (record(env, "/create-ard") or {}).get("end_commit") == pending_commit,
                  "r_found: end_commit %r at stage %s is no replay's: refused plainly, nothing replayed, no row, the record "
                  "kept for end --resume (%r)" % (pending_commit, stage, got))
        seed(env, "/specify", stage="done")
        got = replay_cli(env, "start", "/specify", "main")
        check(got["_rc"] == 0 and got.get("error") and got.get("next") is None
              and (got.get("print") or [""])[0].startswith("Specs preflight: stopped early (")
              and (record(env, "/specify") or {}).get("stage") == "done",
              "r_found: a start record with no replay pending is refused plainly, the record kept (%r)" % got)
        seed(env, "/specify", stage="settle-done", pending=[{"branch": Z, "set_upstream": False, "standing": "main"}])
        got = replay_cli(env, "start", "/specify", Y)
        check(got["_rc"] == 0 and got.get("error") and (record(env, "/specify") or {}).get("pending") == [
            {"branch": Z, "set_upstream": False, "standing": "main"}],
              "r_found: a branch the record did not queue is refused plainly (%r)" % got)
        seed(env, "/specify", stage="flush")
        got = replay_cli(env, "start", "/specify", Y)
        check(got["_rc"] == 0 and "holds no replay of %s" % Y in (got.get("error") or "") and got.get("next") is None
              and (record(env, "/specify") or {}).get("stage") == "flush" and head(r) == mine,
              "r_found: at flush, a branch HEAD does not stand on is refused plainly, the record kept (%r)" % got)

        # r_canned: classify_replay and the renderer over results no repository here produces
        tip = "b" * 40
        moved = {"moved": True, "pushed": False, "attempts": 1, "replayed": ["a" * 40], "dropped": [], "tip": tip,
                 "porcelain": None, "moves": [], "upstream_error": None, "refused": None}
        rej = "!\trefs/heads/main:refs/heads/main\t[rejected] (fetch first)"
        declined = "!\t%s:refs/heads/main\t[remote rejected] (pre-receive hook declined)" % tip
        locked = "!\t%s:refs/heads/main\t[remote rejected] (failed to lock refs/heads/main)" % tip
        failure = "!\t%s:refs/heads/main\t[remote failure] (remote failed to report status)" % tip
        cm = {"reason": "checkout-moved", "path": None}
        for args, want in (
                ((None, None, False, True), ("rejected", None, "timed-out")),
                ((None, "e", False, False), ("rejected", None, "not-run")),
                ((dict(moved, pushed=True), None, False, False), ("replayed", None, None)),
                ((dict(moved, pushed=True), "e", True, False), ("replayed", None, None)),
                ((dict(moved, moved=False, replayed=[], tip=None, refused={"reason": "conflict", "path": "a"}), None, False,
                  False), ("rejected", None, "conflict")),
                ((dict(moved, replayed=[], dropped=["c" * 40]), None, False, False), ("already-there", None, None)),
                ((dict(moved, moved=False, replayed=[]), None, False, False), ("already-there", None, None)),
                ((dict(moved, porcelain=rej, refused=cm), "e", True, False), ("moved", "stopped", None)),
                ((dict(moved, porcelain=rej, refused=cm), None, False, False), ("moved", "later-refused", "checkout-moved")),
                ((dict(moved, attempts=3, porcelain=rej), None, False, False), ("moved", "moved-on", None)),
                ((dict(moved, porcelain=declined), None, False, False), ("moved", "refused", None)),
                ((dict(moved, porcelain=locked), None, False, False), ("moved", "failed", None)),
                ((dict(moved, porcelain=failure), None, False, False), ("moved", "failed", None)),
                ((moved, None, False, False), ("moved", "failed", None))):
            got = classify_replay(*args)
            check(got == dict(zip(("row", "why", "reason"), want)),
                  "r_canned: classify_replay(%r) is %r (%r)" % (args, want, got))

        f = {"sha7": "abc1234", "files": 2, "branch": "main", "specs": "/s", "default": "main", "standing": "main",
             "register_rebuild": False, "error": None, "preflight": False}

        def render(result, error=None, partial=False, timed_out=False, **facts):
            return _replay_line(lines, classify_replay(result, error, partial, timed_out), result,
                                dict(f, error=error, **facts))

        opening = committed("bbbbbbb", "main", 2) + " — origin's main had moved on, so the run replayed its 1 commit(s) onto it and moved main there, but "
        closing = "; the commits are on local main, and a later run retries the push"
        for result, error, partial, why, what in (
                (dict(moved, porcelain=rej, refused=cm), None, False,
                 "a later attempt could not take origin's newer commits in: the checkout switched to or from main while "
                 "the run was moving it — another session's preflight or handoff, say — so main was not moved again; the "
                 "next run that commits session files on main settles the push itself", "later refused, checkout-moved"),
                (dict(moved, attempts=3, porcelain=rej), None, False, "origin's main moved on again during each of its 3 "
                                                                       "attempts", "moved on"),
                (dict(moved, porcelain=failure), None, False,
                 "the push FAILED ([remote failure] (remote failed to report status))", "failed with a status line"),
                (moved, None, False, "the push FAILED (no status line)", "failed with none"),
                (dict(moved, porcelain=rej), "session-branch: not run (OSError: [Errno 28] No space left on device)", True,
                 "session-branch.py stopped (session-branch: not run (OSError: [Errno 28] No space left on device))",
                 "stopped")):
            got = render(result, error, partial)
            check(got == opening + why + closing, "r_canned: moved, not pushed — %s (%r)" % (what, got))
        pf = dict(branch="prd/A-1-x", standing="prd/A-1-x", reason="pre-receive hook declined")
        got, days, _ = dated(lambda: render(dict(moved, porcelain=declined.replace("main", "prd/A-1-x")), record="/r",
                                            record_kind="file", record_error=None, **pf))
        check(got in [("%s — origin's prd/A-1-x had moved on, so the run replayed its 1 commit(s) onto it and moved "
                       "prd/A-1-x there, but push REFUSED by origin (pre-receive hook declined): a rule there takes no push "
                       "of prd/A-1-x, so this is recorded and no later run pushes it; %s"
                       % (committed("bbbbbbb", "prd/A-1-x", 2), refused_tail("prd/A-1-x", "/s", "/r", d))) for d in days],
              "r_canned: the refused form, recorded (%r)" % got)
        got = render(dict(moved, porcelain=declined), record=None, record_kind=None, record_error="e",
                     reason="pre-receive hook declined")
        check(got == ("%s — origin's main had moved on, so the run replayed its 1 commit(s) onto it and moved main there, "
                      "but push REFUSED by origin (pre-receive hook declined): a rule there takes no push of main, but this "
                      "could not be recorded (e, the configuration write's), so a later run pushes main again"
                      % committed("bbbbbbb", "main", 2)), "r_canned: the refused form, unrecorded (%r)" % got)
        got, days, _ = dated(lambda: render(dict(moved, porcelain=declined.replace("main", "prd/A-1-x")), preflight=True,
                                            sha7=None, files=None, record="/r", record_kind="file", record_error=None, **pf))
        check(got in [("Specs preflight: prd/A-1-x — origin's prd/A-1-x had moved on, so the run replayed its 1 commit(s) "
                       "onto it and moved prd/A-1-x there, but push REFUSED by origin (pre-receive hook declined): a rule "
                       "there takes no push of prd/A-1-x, so this is recorded and no later run pushes it; %s"
                       % refused_tail("prd/A-1-x", "/s", "/r", d)) for d in days],
              "r_canned: the refused form in its Specs preflight: form, recorded (%r)" % got)
        got = render(dict(moved, porcelain=declined), preflight=True, sha7=None, files=None, record=None, record_kind=None,
                     record_error="e", reason="pre-receive hook declined")
        check(got == ("Specs preflight: main — origin's main had moved on, so the run replayed its 1 commit(s) onto it and "
                      "moved main there, but push REFUSED by origin (pre-receive hook declined): a rule there takes no push "
                      "of main, but this could not be recorded (e, the configuration write's), so a later run pushes main "
                      "again"), "r_canned: the refused form in its Specs preflight: form, unrecorded (%r)" % got)
        moves = [{"slug": "api", "origin": "f-9", "side": "run", "from": 2, "to": 5},
                 {"slug": "web", "origin": "f-1", "side": "remote", "from": 3, "to": 4},
                 {"slug": "web", "origin": "f-2", "side": "run", "from": 4, "to": 3}]
        got = render(dict(moved, pushed=True, moves=moves, upstream_error="error: could not lock config file"))
        check(got == replayed(committed("bbbbbbb", "main", 2), "main", 1,
                              "; the rebuild of security/api/ renumbered [SEC#2] → [SEC#5] (f-9, the local number), and "
                              "the next run that records in that register lists the lines that cite an old number; the "
                              "rebuild of security/web/ renumbered [SEC#3] → [SEC#4] (f-1, origin's number), [SEC#4] → "
                              "[SEC#3] (f-2, the local number), and the next run that records in that register lists the "
                              "lines that cite an old number; its upstream could not be set (error: could not lock config "
                              "file)"), "r_canned: the register clause per slug, run and remote moves, upstream_error (%r)" % got)
        got = render(dict(moved, replayed=[], dropped=["c" * 40], moves=moves[:1]))
        check(got.endswith("so main now stands on it; the rebuild of security/api/ renumbered [SEC#2] → [SEC#5] (f-9, "
                           "the local number), and the next run that records in that register lists the lines that cite "
                           "an old number"), "r_canned: already there with its register clause (%r)" % got)
        got = render(dict(moved, pushed=True, replayed=["a" * 40], dropped=["c" * 40, "d" * 40]))
        check(got == replayed(committed("bbbbbbb", "main", 2), "main", 3, ", 2 of them already there and dropped"),
              "r_canned: <K> counts replayed and dropped, <D> the dropped (%r)" % got)
        got = render(dict(moved, pushed=True), "session-branch: not run (OSError: [Errno 28] No space left on device)", True)
        check(got == replayed(committed("bbbbbbb", "main", 2), "main", 1),
              "r_canned: a Partial whose pushed is true is replayed and pushed (%r)" % got)
        nothing = dict(moved, moved=False, replayed=[], tip=None)
        for refused, clause, what in (
                ({"reason": "would-overwrite", "path": "a.md", "paths": ["a.md"]},
                 "moving the checkout would write over a.md, which you changed, left untracked or ignore — once that is "
                 "clear, the next run that commits session files on main settles the push itself", "would-overwrite, one path"),
                ({"reason": "would-overwrite", "path": "a.md", "paths": ["a.md", "b.md", "c.md"]},
                 "moving the checkout would write over a.md and 2 more, which you changed, left untracked or ignore — once "
                 "that is clear, the next run that commits session files on main settles the push itself",
                 "would-overwrite, three paths"),
                ({"reason": "push-scope", "path": "abcdef1234567890"},
                 "the push would now also publish abcdef1, which is not one of this plugin's session-file commits", "push-scope"),
                ({"reason": "in-progress", "path": ".git/MERGE_HEAD"},
                 "a rebase, merge, cherry-pick or revert, or an unresolved conflict, is in progress in the checkout "
                 "(.git/MERGE_HEAD)", "in-progress"),
                ({"reason": "locked", "path": ".git/index.lock"}, ".git/index.lock is held by another git process, or was "
                 "left by one that died, and this plugin never deletes a lock", "locked"),
                ({"reason": "cannot-replay", "path": None}, "this git cannot replay without a checkout (its merge-tree "
                 "needs --write-tree and --merge-base, git 2.40 or later)", "cannot-replay"),
                ({"reason": "fetch-failed", "path": None}, "fetching origin's main failed", "fetch-failed"),
                ({"reason": "branch-moved", "path": None}, "main moved while the run was replaying it", "branch-moved"),
                ({"reason": "cannot-move", "path": None}, "git could not move the checkout onto the replay (a folder it "
                 "cannot write, say), and nothing moved", "cannot-move")):
            got = render(dict(nothing, refused=refused))
            check(got == rejected(committed("abc1234", "main", 2), "main", clause, plain("/s", "main")),
                  "r_canned: push rejected — %s (%r)" % (what, got))
        got = render(dict(nothing, refused={"reason": "register-rebuild", "path": "security/web/"}), register_rebuild=True)
        check("the security register security/web/, which only a rebuild settles, and that rebuild failed; run git" in got,
              "r_canned: register-rebuild where the call carried a rebuild (%r)" % got)
        got = render(None, "session-branch: not run (no such branch: main)")
        check(got == rejected(committed("abc1234", "main", 2), "main", "session-branch.py could not run (session-branch: "
                              "not run (no such branch: main))", plain("/s", "main")),
              "r_canned: an exit 2 with nothing on stdout (%r)" % got)
        cm_clause = ("the checkout switched to or from main while the run was moving it — another session's preflight or "
                     "handoff, say — so main was not moved; the next run that commits session files on main settles the "
                     "push itself")
        got = render(dict(nothing, refused=cm))
        check(got == rejected(committed("abc1234", "main", 2), "main", cm_clause, None),
              "r_canned: checkout-moved ends at its reason clause, no remedy (%r)" % got)
        got = render(dict(nothing, refused=cm), preflight=True, standing="prd/A-1-x", sha7=None, files=None)
        check(got == rejected("Specs preflight: main", "main", cm_clause, None),
              "r_canned: checkout-moved names no remedy on a branch the run is not standing on either (%r)" % got)
        got = render(dict(nothing, refused={"reason": "fetch-failed", "path": None}), preflight=True, branch="prd/A-1-x",
                     standing="main", sha7=None, files=None)
        check(got == rejected("Specs preflight: prd/A-1-x", "prd/A-1-x", "fetching origin's prd/A-1-x failed",
                              'run git -C "/s" switch prd/A-1-x, git -C "/s" pull --rebase --no-autostash origin prd/A-1-x '
                              'and git -C "/s" push origin prd/A-1-x, then switch back to main'),
              "r_canned: a branch the run is not standing on, switched to first and back after (%r)" % got)
        got = render(dict(moved, attempts=2, porcelain=rej), preflight=True, sha7=None, files=None)
        check(got == "Specs preflight: main — origin's main had moved on, so the run replayed its 1 commit(s) onto it and "
                     "moved main there, but origin's main moved on again during each of its 2 attempts" + closing,
              "r_canned: moved, not pushed, in its Specs preflight: form (%r)" % got)

        # r_in_process: session-branch.py's replay in process, its exits read as its main() prints them
        real_replay = sb.replay

        def raising(e):
            def replay(*args, **kw):
                raise e
            return replay

        try:
            sb.replay = raising(sb.Partial("OSError: [Errno 28] No space left on device", dict(moved, pushed=True)))
            got = _run_replay("/x", "main", None, False, False)
            check(got == (dict(moved, pushed=True), "session-branch: not run (OSError: [Errno 28] No space left on device)",
                          True), "r_in_process: a Partial is its result, its stderr line and partial (%r)" % (got,))
            sb.replay = raising(sb.Partial("git push ended by signal 15", dict(moved, pushed=True)))
            try:
                got = _run_replay("/x", "main", None, False, False)
            except _Ended as e:
                got = ("ended", e.signum)
            check(got == ("ended", 15), "r_in_process: a Partial a signal ended is no outcome: _Ended (%r)" % (got,))
            sb.replay = raising(NotRun("no such branch:\n  main"))
            got = _run_replay("/x", "main", None, False, False)
            check(got == (None, "session-branch: not run (no such branch: main)", False),
                  "r_in_process: a NotRun is nothing printed and its one stderr line (%r)" % (got,))
            sb.replay = raising(RuntimeError("boom"))
            got = _run_replay("/x", "main", None, False, False)
            check(got == (None, "session-branch: not run (RuntimeError: boom)", False),
                  "r_in_process: any other exception as main() prints it (%r)" % (got,))
            sb.replay = raising(AssertionError("called"))
            check(_run_replay("/x", "main", None, False, True) == (None, None, False),
                  "r_in_process: --timed-out runs no replay")
        finally:
            sb.replay = real_replay

        # r_signalled: a replay a signal ended -- the harness's, at its 420 s -- is no outcome: nothing is printed or
        # recorded, the process ends by that signal, and the --timed-out call that follows finds the record intact
        def caused(e, cause):
            e.__cause__ = cause
            return e

        def record_bytes(env, command):
            with in_env(env):
                try:
                    with open(state.path(env["CLAUDE_CODE_SESSION_ID"], command), "rb") as fh:
                        return fh.read()
                except OSError:
                    return None

        class Exited(BaseException):
            pass

        def exits(signum):
            raise Exited(signum)

        endings = (("git_bounded's NotRun", NotRun("git fetch ended by signal 15"), 15),
                   ("replay's NotRun from _Signalled", caused(NotRun("ended by signal 15"), sb._Signalled(15)), 15),
                   ("a Partial from git_bounded's NotRun", caused(sb.Partial("git push ended by signal 15",
                                                                             dict(moved, pushed=False)),
                                                                  NotRun("git push ended by signal 15")), 15),
                   ("a Partial from _Signalled", caused(sb.Partial("ended by signal 1", dict(moved, pushed=True)),
                                                        sb._Signalled(1)), 1))
        g = globals()
        real_exit = g["_exit_by"]
        g["_exit_by"] = exits
        try:
            for k, (what, ending, signum) in enumerate(endings):
                for for_, command, fields in (
                        ("end", "/create-ard", {"stage": "end-replay"}),
                        ("start", "/specify", {"stage": "flush", "args": {"specs": None, "keys": ["ACME-1"],
                                                                          "commit_key": None, "register_rebuild": None}})):
                    r, env = world(tmp, "r-signalled-%d-%s" % (k, for_))
                    fields = dict(fields, end_commit={"sha7": head(r)[:7], "files": 1, "branch": "main", "paths": [],
                                                      "hook_paths": []})
                    if for_ == "start":
                        fields["args"] = dict(fields["args"], specs=r.path)
                    seed(env, command, **fields)
                    before, h = record_bytes(env, command), head(r)
                    sb.replay = raising(ending)
                    got = None
                    try:
                        with in_env(env):
                            replay(r.path, for_, command, "main")
                    except Exited as e:
                        got = e.args[0]
                    finally:
                        sb.replay = real_replay
                    check(got == signum and record_bytes(env, command) == before and head(r) == h,
                          "r_signalled: %s, --for %s — ends by signal %d, the record as it stood (%r)"
                          % (what, for_, signum, got))
                    if k:
                        continue
                    got = replay_cli(env, for_, command, "main", "--timed-out")
                    timed = TIMED % ("main", r.path, "main", "main", "main")
                    if for_ == "end":
                        check(got.get("row") == "rejected" and got.get("print") == [rejected(committed(h[:7], "main"),
                              "main", timed, plain(r.path, "main"))] and record_bytes(env, command) is None,
                              "r_signalled: then --timed-out prints the 420 s row and removes the record (%r)" % got)
                    else:
                        check(got.get("print") == [rejected("Specs preflight: main", "main", timed, plain(r.path, "main"))]
                              and (got.get("next") or {}).get("run") == resume_line(r.path, "/specify", "--key", "ACME-1",
                                                                                    "--started", own_started(env, command))
                              and (record(env, command) or {}).get("stage") == "settle",
                              "r_signalled: then --timed-out prints the 420 s row, the record on to settle (%r)" % got)
        finally:
            g["_exit_by"] = real_exit
            sb.replay = real_replay
        r, env = world(tmp, "r-signalled-pin")
        sb._pending.append(signal.SIGTERM)
        try:
            sb.git_bounded(r.path, 5, "status")
            pinned = None
        except NotRun as e:
            pinned = _signal_of(e)
        finally:
            del sb._pending[:]
        check(pinned == signal.SIGTERM, "r_signalled: _signal_of reads git_bounded's own words for the signal (%r)" % pinned)
        check(_signal_of(caused(NotRun("stopped"), sb._Signalled(2))) == 2
              and _signal_of(caused(sb.Partial("stopped", {}), sb._Signalled(1))) == 1,
              "r_signalled: a _Signalled cause is read by its type, whatever the words")
        check(_signal_of(NotRun("git fetch --no-tags: error: ended by signal 15")) is None
              and _signal_of(RuntimeError("ended by signal 15")) is None and _signal_of(NotRun("no such branch: x")) is None,
              "r_signalled: an error that only mentions the words is an outcome")

        # r_signalled_child: a real SIGTERM inside the replay's fetch, in a child process
        r, env = world(tmp, "r-signalled-child")
        marker = os.path.join(tmp, "r-signalled-child.fetching")
        r.git("config", "protocol.ext.allow", "always")
        r.git("remote", "set-url", "origin", "ext::sh -c touch%% %s;sleep%% 60" % marker)
        seed(env, "/create-ard", stage="end-replay", end_commit={"sha7": head(r)[:7], "files": 1, "branch": "main",
                                                                 "paths": [], "hook_paths": []})
        before = record_bytes(env, "/create-ard")
        p = subprocess.Popen([sys.executable, me, "--specs", r.path, "replay", "--for", "end", "--command", "/create-ard",
                              "--branch", "main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=dict(os.environ, **env))
        deadline = time.monotonic() + 30
        while not os.path.exists(marker) and p.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        reached = os.path.exists(marker)
        p.send_signal(signal.SIGTERM)
        try:
            out, err = p.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            p.kill()
            out, err = p.communicate()
        check(reached and p.returncode == -signal.SIGTERM and out == b"" and err == b""
              and record_bytes(env, "/create-ard") == before,
              "r_signalled_child: SIGTERM during the fetch ends the call by it, nothing printed, the record intact "
              "(reached %r, rc %r, out %r, err %r)" % (reached, p.returncode, out[:200], err[:300]))

    def scenarios_start(tmp):
        state, lines = _flow()
        T = lines.T
        g = globals()
        FEED = "specifications/PRD-ACME-1-x/dev-workflows/feedback/"
        SPEC = "spec/ACME-1-01-x"
        SUBJECT = "%s Add dev-workflows session artifacts (%s)"
        FIELDS = {"print", "next", "specs_git", "gate", "default", "default_ref", "remote", "offline", "offline_clause",
                  "session_branch", "mode", "guard", "branch", "b2_left", "b4_left", "stay", "start_dirty", "midrun",
                  "started", "replaced", "error"}
        STAY = lines.placeholder("pre.stay", "<switched")

        def run_start(env, command, *args, specs=None, cwd=None):
            return cli("--specs", env["SPECS_PATH"] if specs is None else specs, "start", "--command", command, *args,
                       env=env, cwd=cwd)

        def fields(got):
            return {k for k in got if not k.startswith("_")} == FIELDS

        def follow(got, env):
            """got, then each call the one before it names as next, run as the skill runs it, until one names none."""
            seen = [got]
            while (seen[-1].get("next") or {}).get("run") and len(seen) < 12:
                seen.append(shell(seen[-1]["next"]["run"], env))
            return seen

        def resume_line(specs, command, *args):
            return " ".join(["python3", shlex.quote(me), "--specs", shlex.quote(specs), "start", "--command", command]
                            + list(args) + ["--resume"])

        def subject(r):
            return r.git("log", "-1", "--format=%s")

        def rev(r, branch):
            return r.git("rev-parse", "--verify", "-q", "refs/heads/" + branch, check=False) or None

        def ff_merged(r, name, branch, path):
            """<branch>, cut from r's main with one commit adding <path> and pushed with -u, fast-forward-merged into
            origin's main by another clone; r is left on <branch>, its own main behind origin's."""
            r.git("switch", "-q", "-c", branch, "main")
            r.write(path, "x\n")
            r.commit_all("work on " + branch)
            r.git("push", "-q", "-u", "origin", branch)
            o = clone(r, name)
            o.git("merge", "-q", "--ff-only", "origin/" + branch)
            o.git("push", "-q", "origin", "main")
            return o

        def squash_merged(r, name, branch, path):
            """<branch>, cut from r's main with one commit adding <path>, never pushed; another clone lands the same
            change on origin's main as a commit of its own."""
            r.git("switch", "-q", "-c", branch, "main")
            r.write(path, "s\n")
            r.commit_all("work on " + branch)
            o = clone(r, name)
            o.write(path, "s\n")
            o.commit_all("work on %s, squashed" % branch)
            o.git("push", "-q", "origin", "main")
            return o

        def session_commit(r, branch, prd, command="/feedback", name="f.md"):
            """A session-file commit on <branch>, unpushed."""
            r.git("switch", "-q", branch)
            r.write("specifications/%s/dev-workflows/feedback/%s" % (prd, name), name + "\n")
            r.commit_all(SUBJECT % ("NOISSUE", command))

        def refusal_file(r, branch):
            path = os.path.join(r.path, ".git", "workflows", "push-refused", branch)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("2026-11-01\n")
            return path

        def updates(r, branch):
            """How many times origin's <branch> was written (the bare's reflog, core.logAllRefUpdates on)."""
            p = subprocess.run(["git", "-C", r.bare, "reflog", "show", "refs/heads/" + branch], stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL)
            return len(p.stdout.decode().splitlines())

        def pushed_default(sha7, specs):
            return ("Specs repo: committed %s (1 file) on main — pushed straight to main, and no pull request was opened: "
                    "this plugin lands its session files there without review; to land them through a pull request of your "
                    "own instead, turn on session-branch mode (§8) with git -C \"%s\" config workflows.sessionBranch true — where a "
                    "container mounts this repository's .git/config read-only, run it on the host" % (sha7, specs))

        # The landing's pieces (specs-repo-git §4 step 1, §6): the row a landing's commit on main takes once pushed with
        # app.landed, G1's plain block, its §5 forms, and the stay the record holds.
        KINDS = lines.placeholder("g1.landing.not_done", "<which no key")
        LANDED = lines.placeholder("app.landed", "<which no key")

        def lacks_row(r, branch):
            """origin-lacks' line for HEAD's one-file commit on <branch>, a plugin branch origin does not have."""
            return lines.fill("row.origin-lacks", {"<sha7>": head(r)[:7], "<N>": 1, "<branch>": branch,
                                                   "<SPECS_PATH>": r.path})

        def plugin_row(r, branch):
            return "Specs repo: committed %s (1 file) on %s — pushed" % (head(r)[:7], branch)

        def landed_row(r, n, branch, kind="merged"):
            """pushed-default's line for the landing's commit, main's tip, of <n> files, then app.landed for a stay of
            <kind> (STAY_KINDS) on <branch>."""
            sha7 = (r.git("rev-parse", "--verify", "-q", "refs/heads/main", check=False) or "")[:7]
            return (pushed_default(sha7, r.path).replace("(1 file)", "(1 file)" if n == 1 else "(%d files)" % n)
                    + lines.fill("app.landed", {"<branch>": branch, "<default>": "main", LANDED: STAY_KINDS.index(kind)}))

        def g1_plain(r, paths):
            return lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": len(paths),
                                     "<path list>": [", ".join(paths), " ".join(shlex.quote(p) for p in paths)]})

        def g1_form(r, paths, not_done, fix, if_ignored):
            """G1's block for <paths> in one of §5's forms, rendered from the pins and never by the code it checks: the
            plain block's header and Found part, then <not_done>, <fix> (None: the plain block's Fix part) and
            <if_ignored>, each on its one line after its label's padding."""
            rows = g1_plain(r, paths).split("\n")
            at = {label: next(k for k, row in enumerate(rows) if row.startswith(label))
                  for label in ("Not done:", "Fix:", "If ignored:")}
            fixed = rows[at["Fix:"]:at["If ignored:"]] if fix is None else [("Fix:      " + fix).rstrip()]
            return "\n".join(rows[:at["Not done:"]] + ["Not done: " + not_done] + fixed + ["If ignored: " + if_ignored])

        def merged_fix(r, paths):
            return lines.fill("g1.merged.fix", {"<SPECS_PATH>": r.path, "<default>": "main",
                                                "<path list>": " ".join(shlex.quote(p) for p in paths)})

        def g1_landing(r, paths, branch, kind):
            """G1's landing form (§5) at the start, for a stay of <kind> (STAY_KINDS) on <branch>: merged's Fix and If
            ignored where the stay's merged flag is set -- here, kind merged -- else the plain Fix and
            g1.landing.if_ignored."""
            v = {"<default>": "main", "<branch>": branch, KINDS: STAY_KINDS.index(kind)}
            if kind == "merged":
                return g1_form(r, paths, lines.fill("g1.landing.not_done", v), merged_fix(r, paths),
                               lines.fill("g1.merged.if_ignored", v))
            return g1_form(r, paths, lines.fill("g1.landing.not_done", v), None, T["g1.landing.if_ignored"])

        def g1_unlanded(r, paths, branch, kind):
            """G1's landing form as end repeats it after a landing that did not land the run's whole change (§5): its
            Not done g1.landing.not_done.unlanded, its Fix and If ignored the landing form's."""
            v = {"<default>": "main", "<branch>": branch, KINDS: STAY_KINDS.index(kind)}
            whole = g1_landing(r, paths, branch, kind).split("\n")
            k = next(i for i, row in enumerate(whole) if row.startswith("Not done:"))
            return "\n".join(whole[:k] + ["Not done: " + lines.fill("g1.landing.not_done.unlanded", v)] + whole[k + 1:])

        def g1_landed(r, paths, branch, kind):
            """G1's landing form as end repeats it after a landing that landed the run's whole change (§5, M4): its Not
            done g1.landing.not_done.landed, its Fix and If ignored the landing form's."""
            v = {"<default>": "main", "<branch>": branch, KINDS: STAY_KINDS.index(kind)}
            whole = g1_landing(r, paths, branch, kind).split("\n")
            k = next(i for i, row in enumerate(whole) if row.startswith("Not done:"))
            return "\n".join(whole[:k] + ["Not done: " + lines.fill("g1.landing.not_done.landed", v)] + whole[k + 1:])

        def stayed(branch, reason, kind="merged", merged=True):
            return {"branch": branch, "kind": kind, "reason": reason, "merged": merged, "command": None}

        def stay_of(env, command="/feedback"):
            return (record(env, command) or {}).get("stay")

        def untracked(r, path):
            return "?? " + path in r.git("status", "--porcelain", "--untracked-files=all")

        # t_stay_keys_none (in process, first, since the key list it pins is B3's and B4's too, which every start
        # below reads): with no commit key, and an extra key that is None, nothing None reaches branch_key; a key
        # given beside them still resolves the branch
        B = "prd/B-2-y"
        rec = state.new("/feedback", session="t-stay-keys-none", default="main", mode="off", keys=["ACME-1"])
        try:
            kind_of = g["_stay_kind"]
            got = [kind_of(rec, B, False), kind_of(rec, B, False, extra_keys=(None,)),
                   kind_of(rec, B, False, extra_keys=("B-2",)), kind_of(dict(rec, commit_key="B-2"), B, False),
                   kind_of(rec, B, True), kind_of(rec, "main", True), kind_of(rec, "feature/x", False),
                   kind_of(dict(rec, mode="on"), B, True), kind_of(dict(rec, specs_git="misrooted"), B, True),
                   kind_of(rec, None, True)]
        except Exception as e:
            got = "%s: %s" % (type(e).__name__, e)
        check(got == ["unkeyed", "unkeyed", None, None, "merged", None, None, None, None, None],
              "t_stay_keys_none: _stay_kind's kinds, and no None reaching branch_key (%r)" % (got,))

        # t_clean
        r, env = world(tmp, "t-clean")
        got = run_start(env, "/feedback")
        line = env_line(r.path)
        check(got["_rc"] == 0 and fields(got) and got.get("print") == [line] and got.get("specs_git") is None
              and got.get("gate") == "pass" and got.get("default") == "main" and got.get("default_ref") == "origin/main"
              and got.get("remote") == "origin" and got.get("offline") is False and got.get("offline_clause") is None
              and got.get("branch") == "main" and got.get("guard") is None and got.get("next") is None
              and got.get("mode") == "off" and got.get("replaced") is None and got.get("error") is None,
              "t_clean: the Environment line alone, on main, nothing to do (%r)" % got)
        rec = record(env, "/feedback") or {}
        check(rec.get("stage") == "done" and rec.get("env_line") == line and rec.get("branch") == "main"
              and rec.get("args") == {"specs": r.path, "keys": [], "commit_key": None, "register_rebuild": None},
              "t_clean: the record saved at stage done, with the call's arguments (%r)" % rec)

        # t_unset
        got = run_start(env, "/feedback", specs="")
        check(got["_rc"] == 0 and fields(got) and got.get("print") == [env_line("")] and "SPECS_PATH=unset" in got["print"][0]
              and got.get("gate") == "unset" and got.get("default") is None and got.get("branch") is None
              and got.get("next") is None and got.get("error") is None,
              "t_unset: the Environment line naming SPECS_PATH=unset, nothing else (%r)" % got)
        check((record(env, "/feedback") or {}).get("stage") == "done", "t_unset: a record saved")

        # t_misrooted
        r, env = world(tmp, "t-misrooted")
        r.write("specs/specifications/PRD-A-1-x/prd.md", "---\nkind: prd\nkey: A-1\n---\n")
        r.commit_all("a specs tree inside a larger repository")
        r.git("push", "-q", "origin", "main")
        ff_merged(r, "t-misrooted-other", "prd/A-1-x", "specs/specifications/PRD-A-1-x/ard.md")
        mine = "specs/specifications/PRD-A-1-x/dev-workflows/resume.md"
        r.write(mine, "r\n")
        specs = os.path.join(r.path, "specs")
        below = lines.fill("pre.below-top", {"<value>": specs, "<top>": r.git("rev-parse", "--show-toplevel")})
        h = head(r)
        got = run_start(env, "/feedback", specs=specs)
        want = lines.fill("pre.stay", {"<branch>": "prd/A-1-x", "<default>": "main", STAY: 0})
        check(got.get("print") == [env_line(specs), below, want] and got.get("specs_git") == "misrooted"
              and got.get("branch") == "prd/A-1-x" and head(r) == h
              and "?? " + mine in r.git("status", "--porcelain", "--untracked-files=all"),
              "t_misrooted: the below-top notice and pre.stay's merged variant, no switch, nothing committed (%r)" % got)
        check((record(env, "/feedback") or {}).get("misrooted_notice") == [below],
              "t_misrooted: the notice saved for end to repeat")
        r.git("switch", "-q", "-c", "prd/B-2-y", "main")
        r.write("specs/specifications/PRD-B-2-y/prd.md", "b\n")
        r.commit_all("B-2 Add the PRD")
        h = head(r)
        got = run_start(env, "/feedback", "--key", "A-1", specs=specs)
        want = lines.fill("pre.stay", {"<branch>": "prd/B-2-y", "<default>": "main", STAY: 1})
        check(got.get("print") == [env_line(specs), below, want] and got.get("branch") == "prd/B-2-y" and head(r) == h,
              "t_misrooted: an unmerged branch no key names gets the unkeyed variant (%r)" % got)

        # t_offline
        r, env = world(tmp, "t-offline")
        r.git("remote", "set-url", "origin", os.path.join(tmp, "t-offline-gone.git"))
        got = run_start(env, "/feedback")
        check(got["_rc"] == 0 and got.get("offline") is True
              and got.get("offline_clause") == "offline — ancestry checked against the last-fetched ref"
              and got.get("print") == [env_line(r.path)] and got.get("default_ref") == "origin/main"
              and got.get("error") is None, "t_offline: carried, not printed (%r)" % got)

        # t_g0
        r, env = world(tmp, "t-g0")
        r.git("switch", "-q", "--detach", "HEAD")
        r.write(RESUME, "r\n")
        h = head(r)
        got, days, _ = dated(lambda: run_start(env, "/feedback"))
        blocks = [lines.fill("g0", {"<SPECS_PATH>": r.path, "<sha7>": h[:7], "<YYYY-MM-DD>": d, "<branch>": "main"})
                  for d in days]
        block = next((b for b in blocks if got.get("print") == [env_line(r.path), b]), blocks[-1])
        check(got.get("print") == [env_line(r.path), block] and got.get("specs_git") == "blocked" and got.get("guard") == "G0"
              and got.get("branch") is None and head(r) == h,
              "t_g0: a detached HEAD prints G0's block and sets blocked (%r)" % got)
        rec = record(env, "/feedback") or {}
        check(rec.get("guard_block") == block and rec.get("stage") == "done", "t_g0: the block saved for end (%r)" % rec)

        # t_g1: a plugin branch cut at main's tip holds nothing of its own, so branch-merged reads it merged and G1 takes
        # its landing form (§5), merged's alternative; t_land_merged_b3_g1 below has the plain block on an unmerged branch
        r, env = world(tmp, "t-g1")
        r.git("switch", "-q", "-c", "prd/ACME-9-q")
        r.write("notes.md", "n\n")
        r.write("my notes.md", "m\n")
        r.write(RESUME, "r\n")
        h = head(r)
        got = run_start(env, "/feedback")
        block = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 2,
                                  "<path list>": ["my notes.md, notes.md", "'my notes.md' notes.md"]})
        shown = (got.get("print") or ["", ""])[-1]
        check(got.get("print") == [env_line(r.path),
                                   g1_landing(r, ["my notes.md", "notes.md"], "prd/ACME-9-q", "merged")]
              and block == g1_plain(r, ["my notes.md", "notes.md"]) and got.get("guard") == "G1"
              and got.get("specs_git") is None and got.get("branch") == "prd/ACME-9-q" and head(r) == h
              and "?? " + RESUME in r.git("status", "--porcelain", "--untracked-files=all")
              and "artifact area: my notes.md, notes.md\n" in shown and "add 'my notes.md' notes.md &&" in shown,
              "t_g1: the block lists the paths, comma-separated, then shell-quoted; no flush, no switch (%r)" % got)
        rec = record(env, "/feedback") or {}
        check(rec.get("guard_paths") == ["my notes.md", "notes.md"] and rec.get("guard_block") == block
              and rec.get("stay") == stayed("prd/ACME-9-q", "g1"),
              "t_g1: the paths saved as guard_paths, the plain block saved, the stay recorded (%r)" % rec)

        # t_g2, t_g2_implement
        r, env = world(tmp, "t-g2")
        r.git("switch", "-q", "-c", "feature/x")
        plain = lines.fill("g2", {"<SPECS_PATH>": r.path, "<branch>": "feature/x", "<default>": "main"})
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), plain] and got.get("guard") == "G2" and got.get("branch") == "feature/x",
              "t_g2: G2's block naming main (%r)" % got)
        run_end(env, "/feedback")  # its run ended, so /implement's below is not typed mid-run (§3.5)
        implement = (
            "⚠ SPECS REPO — ON A BRANCH THIS PLUGIN DID NOT CREATE\n\n"
            "Found:    %s is on branch `feature/x`, which is neither the default\n"
            "          branch (`main`) nor a plugin branch (idea/ prd/ ard/ spec/\n"
            "          epics/ design/ ready/ brd/ frames/ kb/ conformance/).\n"
            "Not done: the preflight did not switch away from it — the plugin manages only branches it created. This run "
            "changes code here, so its artifacts WILL be committed on the branch it cuts for that, or, if it stops first, on "
            "the branch it then stands on — feature/x, or main after a fresh start — and not pushed unless that branch is "
            "main or its name carries one of this plugin's prefixes.\n"
            "Fix:\n"
            "If ignored: nothing is to be run here: the artifacts stay on that branch until it is pushed or merged, and "
            "reach the maintainer then." % r.path)
        got = run_start(env, "/implement", cwd=os.path.join(r.path, "specifications"))
        check(got.get("print") == [env_line(r.path), implement] and got.get("guard") == "G2",
              "t_g2_implement: /implement from inside the specs work tree gets the direct-run lines (%r)" % got)
        got = run_start(env, "/implement", cwd=tmp)
        check(got.get("print") == [env_line(r.path), plain], "t_g2_implement: /implement run from elsewhere gets the plain block")

        # t_catch_up
        r, env = world(tmp, "t-catch-up")
        o = clone(r, "t-catch-up-other")
        o.write(FEED + "o.md", "o\n")
        o.commit_all(SUBJECT % ("NOISSUE", "/feedback"))
        o.git("push", "-q", "origin", "main")
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path)] and head(r) == head(o) and got.get("branch") == "main",
              "t_catch_up: fast-forwarded silently (%r)" % got)

        # t_catch_up_failed: origin unreachable once the fetch has run
        r, env = world(tmp, "t-catch-up-failed")
        o = clone(r, "t-catch-up-failed-other")
        o.write(FEED + "o.md", "o\n")
        o.commit_all(SUBJECT % ("NOISSUE", "/feedback"))
        o.git("push", "-q", "origin", "main")
        h, line = head(r), env_line(r.path)
        real_resolve = g["resolve_default"]

        def then_gone(root, fetch):  # once the fetch has run: the snapshot's read before it fetches nothing
            out = real_resolve(root, fetch)
            if fetch:
                sb.git(root, "remote", "set-url", "origin", os.path.join(tmp, "t-catch-up-failed-gone.git"))
            return out

        g["resolve_default"] = then_gone
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["resolve_default"] = real_resolve
        shown = got.get("print") or []
        check(len(shown) == 2 and shown[0] == line and shown[1].startswith("Specs preflight: could not fast-forward main (")
              and shown[1].endswith("); the run goes on from it as it stands") and head(r) == h and got.get("error") is None,
              "t_catch_up_failed: pre.pull-failed, the run going on from main as it stands (%r)" % got)

        # t_flush
        r, env = world(tmp, "t-flush")
        r.write(RESUME, "r\n")
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path)] and subject(r) == SUBJECT % ("NOISSUE", "/feedback")
              and "Co-Authored-By" not in r.git("log", "-1", "--format=%B") and on_origin(r) == head(r)
              and r.git("status", "--porcelain") == "", "t_flush: committed and pushed, silent (%r)" % got)
        r.write(RESUME, "r2\n")
        got = run_start(env, "/feedback", "--commit-key", "ACME-1")
        check(got.get("print") == [env_line(r.path)] and subject(r) == SUBJECT % ("ACME-1", "/feedback")
              and on_origin(r) == head(r), "t_flush: --commit-key opens the subject (%r)" % got)

        # t_flush_locked
        r, env = world(tmp, "t-flush-locked")
        r.write(RESUME, "r\n")
        h = head(r)
        lock = os.path.join(r.path, ".git", "index.lock")
        open(lock, "w").close()
        got = run_start(env, "/feedback")
        os.remove(lock)
        check(got.get("print") == [env_line(r.path), "Specs preflight: skipped — another session holds the repo "
                                   "(index.lock); the next run picks the artifacts up"] and head(r) == h,
              "t_flush_locked: the Locked row in its Specs preflight: form (%r)" % got)

        # t_flush_locked_b4: a Locked flush leaves the session file dirty, and B4's switch, refused under the index.lock,
        # stops the call with rule 5's line
        r, env = world(tmp, "t-flush-locked-b4")
        r.git("switch", "-q", "-c", "prd/ACME-9-q")
        r.write("specifications/PRD-ACME-9-q/prd.md", "q\n")
        r.commit_all("ACME-9 Add the PRD")
        r.write(RESUME, "r\n")
        lock = os.path.join(r.path, ".git", "index.lock")
        open(lock, "w").close()
        got = run_start(env, "/feedback")
        os.remove(lock)
        shown = got.get("print") or []
        check(got["_rc"] == 0 and len(shown) == 3 and shown[1] == "Specs preflight: skipped — another session holds the "
              "repo (index.lock); the next run picks the artifacts up"
              and shown[2].startswith("Specs preflight: stopped early (git switch main: fatal: Unable to create '")
              and shown[2].endswith(" — what it did is above, and the next run's preflight goes on from where this one "
                                    "stands") and (got.get("error") or "").startswith("git switch main: ")
              and got.get("branch") == "prd/ACME-9-q" and (record(env, "/feedback") or {}).get("stage") == "disposition",
              "t_flush_locked_b4: B4's refused switch ends the call on pre.stopped, nothing moved (%r)" % got)

        # t_flush_commit_failed
        r, env = world(tmp, "t-flush-commit-failed")
        hook(os.path.join(r.path, ".git", "hooks", "pre-commit"), "echo hook says no >&2\nexit 1\n")
        r.write(RESUME, "r\n")
        h = head(r)
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), "Specs preflight: NOT COMMITTED — the commit failed (hook says no); the "
                                   "artifacts stay staged, and a later run commits them once git accepts the commit (a "
                                   "merge concluded, a hook satisfied)"] and head(r) == h,
              "t_flush_commit_failed: the Commit failed row in its Specs preflight: form (%r)" % got)

        # t_flush_refused: origin's pre-receive hook refuses the flush's push, on a plugin branch the run stays on
        r, env = world(tmp, "t-flush-refused")
        r.git("switch", "-q", "-c", PLUGIN)
        r.write("specifications/PRD-ACME-1-x/ard.md", "a\n")
        r.commit_all("ACME-1 Add the ARD")
        r.git("push", "-q", "-u", "origin", PLUGIN)
        hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 1\n")
        r.write(RESUME, "r\n")
        got, days, _ = dated(lambda: run_start(env, "/feedback", "--key", "ACME-1"))
        p, rec_file = r.path, os.path.join(r.path, ".git", "workflows", "push-refused", PLUGIN)
        want = [[env_line(p), "Specs preflight: %s not pushed — origin refused it (pre-receive hook declined), and this is "
                 "recorded so no later run pushes it; to land the commits on local %s, put them on a branch of their own and "
                 "open a pull request from it — git -C \"%s\" branch --no-track session-files-%s %s && git -C \"%s\" push -u origin "
                 "session-files-%s — then, standing on %s, git -C \"%s\" reset --keep origin/%s; once origin takes pushes "
                 "to %s again, rm \"%s\"" % (PLUGIN, PLUGIN, p, d, PLUGIN, p, d, PLUGIN, p, PLUGIN, PLUGIN, rec_file)]
                for d in days]
        check(got.get("print") in want and os.path.isfile(rec_file) and on_origin(r, PLUGIN) != head(r)
              and got.get("branch") == PLUGIN, "t_flush_refused: the refusal in its Specs preflight: form, recorded (%r)" % got)

        # t_session_files_always: the refusal's remedy makes session-files-<date> with branch --no-track (specs-repo-git
        # §6), so a user's branch.autoSetupMerge=always writes no upstream: run as printed -- its branch and push, joined
        # by && -- with that setting and .git/config held locked, as a hardened container's read-only one fails a write,
        # it makes the branch at PLUGIN's tip and pushes it, exit 0. A plain `git branch` there makes the branch, fails on
        # the tracking write and exits 1, and the && never pushes.
        sfa = re.search(r'(git -C "[^"]+" branch (?:--no-track )?(session-files-[0-9-]+) \S+ && git -C "[^"]+" push -u origin '
                        r'session-files-[0-9-]+)', (got.get("print") or [""])[-1])
        hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 0\n")
        r.git("config", "branch.autoSetupMerge", "always")
        sfa_lock = os.path.join(r.path, ".git", "config.lock")
        open(sfa_lock, "w").close()
        try:
            sfa_rc = shell(sfa.group(1), env)["_rc"] if sfa else None
        finally:
            os.remove(sfa_lock)
        check(sfa is not None and sfa_rc == 0 and on_origin(r, sfa.group(2)) == r.git("rev-parse", PLUGIN)
              and rev(r, sfa.group(2)) == r.git("rev-parse", PLUGIN),
              "t_session_files_always: the remedy, run with branch.autoSetupMerge=always and .git/config locked, makes "
              "and pushes the branch (%r, rc %r)" % (sfa.group(1) if sfa else None, sfa_rc))

        # t_flush_failed: origin unreachable once the fetch has run, so the flush's push fails
        r, env = world(tmp, "t-flush-failed")
        r.write(RESUME, "r\n")
        line = env_line(r.path)

        def then_gone_too(root, fetch):
            out = real_resolve(root, fetch)
            if fetch:
                sb.git(root, "remote", "set-url", "origin", os.path.join(tmp, "t-flush-failed-gone.git"))
            return out

        g["resolve_default"] = then_gone_too
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["resolve_default"] = real_resolve
        shown = got.get("print") or []
        check(len(shown) == 2 and shown[0] == line and shown[1].startswith("Specs preflight: main — push FAILED (fatal: ")
              and shown[1].endswith("); the commit is local and a later run retries it")
              and subject(r) == SUBJECT % ("NOISSUE", "/feedback") and got.get("error") is None,
              "t_flush_failed: push FAILED in its Specs preflight: form, git's reason (%r)" % got)

        # t_preflight_forms (canned): the unrecorded refusal, and a push the cap ended
        got = _refused_line(lines, "/s", PLUGIN, "main", {"reason": "a rule", "recorded": None, "record": None,
                                                          "record_error": "error: could not lock config file"})
        check(got == "Specs preflight: %s not pushed — origin refused it (a rule), and this could not be recorded (error: "
                     "could not lock config file), so a later run pushes it again" % PLUGIN,
              "t_preflight_forms: the unrecorded refusal names no remedy (%r)" % got)
        got = lines.preflight_form(_row_line(lines, "failed", {"sha7": "-", "files": 0, "branch": "main",
                                                               "reason": T["text.push-capped"]}))
        check(got == "Specs preflight: main — push FAILED (the push did not finish within 60 s); the commit is local and a "
                     "later run retries it", "t_preflight_forms: a capped push's reason (%r)" % got)

        # t_retry
        r, env = world(tmp, "t-retry")
        r.write(RESUME, "r\n")
        r.commit_all(SUBJECT % ("NOISSUE", "/specify"))
        h = head(r)
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path)] and on_origin(r) == h and head(r) == h,
              "t_retry: an earlier run's unpushed session commit pushed, silent (%r)" % got)

        # t_merged_leave
        A = "prd/A-1-x"
        RES_A = "specifications/PRD-A-1-x/dev-workflows/resume.md"
        r, env = world(tmp, "t-merged-leave")
        ff_merged(r, "t-merged-leave-other", A, "specifications/PRD-A-1-x/prd.md")
        r.write(RES_A, "r\n")
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), "Specs preflight: deleted merged prd/A-1-x"]
              and got.get("branch") == "main" and got.get("b2_left") == A and rev(r, A) is None
              and subject(r) == SUBJECT % ("NOISSUE", "/feedback") and on_origin(r) == head(r)
              and r.git("show", "--name-only", "--format=", "HEAD") == RES_A,
              "t_merged_leave: switched to main, the branch deleted, the flush on main (%r)" % got)
        r, env = world(tmp, "t-merged-leave-refused")
        r.write(RES_A, "main's\n")
        r.commit_all("NOISSUE a resume pointer on main")
        r.git("push", "-q", "origin", "main")
        r.git("switch", "-q", "-c", A)
        r.write(RES_A, "the branch's\n")
        r.commit_all("A-1 work")
        r.git("push", "-q", "-u", "origin", A)
        o = clone(r, "t-merged-leave-refused-other")
        o.git("merge", "-q", "--ff-only", "origin/" + A)
        o.git("push", "-q", "origin", "main")
        o.git("push", "-q", "origin", "--delete", A)
        r.write(RES_A, "dirty\n")
        got = run_start(env, "/feedback", "--key", "A-1")
        shown = got.get("print") or []
        flushed = lines.fill("pre.merged-flush", {"<branch>": A, "<sha7>": head(r)[:7], "<default>": "main",
                                                  "<SPECS_PATH>": r.path})
        check(len(shown) == 3 and shown[0] == env_line(r.path)
              and shown[1].startswith("Specs preflight: could not switch from merged prd/A-1-x to main (error: ")
              and shown[2] == flushed and got.get("branch") == A and got.get("b2_left") is None
              and subject(r) == SUBJECT % ("NOISSUE", "/feedback") and on_origin(r, A) is None,
              "t_merged_leave: a refused switch is reported, the flush on the branch, the cherry-pick line (%r)" % got)

        # t_merged_leave_kept (in process): the leave's pull fails, so -d keeps the branch; the settle loop, which skips the
        # branch the leave reported, does not report it again
        r, env = world(tmp, "t-merged-leave-kept")
        ff_merged(r, "t-merged-leave-kept-other", A, "specifications/PRD-A-1-x/prd.md")
        r.git("update-ref", "-d", "refs/remotes/origin/" + A)
        r.write(RES_A, "r\n")

        def then_unreachable(root, fetch):
            out = real_resolve(root, fetch)
            if fetch:
                sb.git(root, "remote", "set-url", "origin", os.path.join(tmp, "t-merged-leave-kept-gone.git"))
            return out

        g["resolve_default"] = then_unreachable
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["resolve_default"] = real_resolve
        shown = got.get("print") or []
        check(len(shown) == 4 and shown[1].startswith("Specs preflight: could not fast-forward main (")
              and shown[2].startswith("Specs preflight: could not delete merged prd/A-1-x (error: ")
              and shown[3].startswith("Specs preflight: main — push FAILED (") and got.get("b2_left") == A
              and rev(r, A) is not None and got.get("branch") == "main",
              "t_merged_leave_kept: the leave's reports once, the settle loop skipping the branch it reported (%r)" % got)
        got = run_start(env, "/feedback", "--rerun")
        shown = got.get("print") or []
        check(got["_rc"] == 0 and len(shown) == 2 and shown[1].startswith("Specs preflight: main — push FAILED (")
              and not any(A in line for line in shown) and (record(env, "/feedback") or {}).get("b2_left") == A,
              "t_merged_leave_kept: --rerun carries b2_left, so its settle loop skips that branch too (%r)" % got)

        # t_merged_unknown: an origin that holds no default branch yet, so branch-merged cannot answer anywhere
        bare = os.path.join(tmp, "t-merged-unknown.git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
        r = new_repo(tmp, "t-merged-unknown")
        r.git("remote", "add", "origin", bare)
        env = {"HOME": os.path.join(tmp, "home-t-merged-unknown"), "CLAUDE_CODE_SESSION_ID": "t-merged-unknown",
               "SPECS_PATH": r.path}
        os.makedirs(env["HOME"])
        r.git("branch", "prd/ACME-2-y")
        r.git("switch", "-q", "-c", PLUGIN)
        r.write("specifications/PRD-ACME-1-x/prd.md", "p\n")
        r.commit_all("ACME-1 Add the PRD")
        r.write(RESUME, "r\n")

        def unknown(branch):
            return ("Specs preflight: could not tell whether %s is merged (specs-git: not run (origin/main does not "
                    "resolve to a commit)), so it reads unmerged" % branch)

        # The leave asks HEAD, the settle loop its branch, B2's row HEAD again: one report for a branch in a run.
        got = run_start(env, "/feedback", "--key", "ACME-1")
        check(got["_rc"] == 0 and got.get("print") == [env_line(r.path), unknown(PLUGIN), unknown("prd/ACME-2-y")]
              and got.get("branch") == PLUGIN and rev(r, "prd/ACME-2-y") is not None and got.get("error") is None
              and subject(r) == SUBJECT % ("NOISSUE", "/feedback")
              and (record(env, "/feedback") or {}).get("reported") == ["pre.merged-unknown " + PLUGIN,
                                                                       "pre.merged-unknown prd/ACME-2-y"],
              "t_merged_unknown: the leave's and the settle loop's asks report, B2's repeats none, all read unmerged "
              "(%r)" % got)
        got = run_start(env, "/feedback", "--key", "ACME-1")
        check(got.get("print") == [env_line(r.path), unknown("prd/ACME-2-y"), unknown(PLUGIN)]
              and got.get("branch") == PLUGIN, "t_merged_unknown: on a clean tree, the settle loop's and B2's (%r)" % got)
        # --budget 0: an ask made just before a stop is not reported again by the resume that asks it again. Four calls:
        # the fetch's, the held stage's push of main -- whose commits origin, holding no main, lacks, so it is measured
        # and its budget checked (§3.2), then refused silently by push-scope (README.md is no session file) -- the
        # flush's and the settle loop's.
        calls = [run_start(env, "/feedback", "--key", "ACME-1", "--budget", "0")]
        while (calls[-1].get("next") or {}).get("run") and len(calls) < 8:
            calls.append(shell(calls[-1]["next"]["run"], env))
        stitched = [p for c in calls for p in c.get("print") or []]
        check(len(calls) == 4 and stitched == [env_line(r.path), unknown("prd/ACME-2-y"), unknown(PLUGIN)]
              and calls[-1].get("next") is None and (record(env, "/feedback") or {}).get("stage") == "done",
              "t_merged_unknown: at --budget 0 each report once across the calls (%r)" % stitched)
        got = run_start(env, "/feedback", "--rerun", "--key", "ACME-1")
        check(got.get("print") == [env_line(r.path)], "t_merged_unknown: a --rerun carries the reports, so prints none (%r)" % got)

        # t_status_failed (in process): status cannot run -- one report, G1 finds nothing, the flush stages nothing
        r, env = world(tmp, "t-status-failed")
        r.write(RESUME, "r\n")
        r.write("notes.md", "n\n")
        h = head(r)
        real_status = g["status"]

        def broken_status(root):
            raise NotRun("git status: fatal: index file corrupt")

        g["status"] = broken_status
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["status"] = real_status
        check(got.get("print") == [env_line(r.path), "Specs preflight: could not list the uncommitted paths (specs-git: not "
                                   "run (git status: fatal: index file corrupt)), so nothing is staged"]
              and got.get("error") is None and got.get("guard") is None and head(r) == h
              and (record(env, "/feedback") or {}).get("stage") == "done",
              "t_status_failed: reported once, nothing staged, the preflight going on to the end (%r)" % got)

        # t_status_failed_stay (in process): with the dirty set unknown, B2 on a merged plugin branch stays and says so
        r, env = world(tmp, "t-status-failed-stay")
        ff_merged(r, "t-status-failed-stay-other", A, "specifications/PRD-A-1-x/prd.md")
        r.write(RES_A, "r\n")
        g["status"] = broken_status
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["status"] = real_status
        stay = lines.placeholder("pre.stay.unlisted", "<switched")
        check(got.get("print") == [env_line(r.path), "Specs preflight: could not list the uncommitted paths (specs-git: not "
                                   "run (git status: fatal: index file corrupt)), so nothing is staged",
                                   "Specs preflight: staying on prd/A-1-x — the uncommitted paths could not be listed, so no "
                                   "branch is switched (it would have switched to main and deleted it, as it is merged)"]
              and lines.fill("pre.stay.unlisted", {"<branch>": A, "<default>": "main", stay: 0}) == got["print"][2]
              and got.get("branch") == A and rev(r, A) is not None and got.get("b2_left") is None
              and got.get("error") is None, "t_status_failed_stay: B2 stays and reports, nothing switched (%r)" % got)

        # t_status_failed_stay_b4 (in process): with the dirty set unknown, B4 on an unmerged plugin branch no key names
        # stays and says so
        r, env = world(tmp, "t-status-failed-stay-b4")
        r.git("switch", "-q", "-c", SPEC)
        r.write("specifications/PRD-ACME-1-x/EPIC-ACME-1-01-x/specification.md", "s\n")
        r.commit_all("ACME-1-01 Add the specification")
        g["status"] = broken_status
        try:
            with in_env(env):
                got = start(r.path, "/document", ("ACME-2",))
        finally:
            g["status"] = real_status
        check(got.get("print") == [env_line(r.path), "Specs preflight: could not list the uncommitted paths (specs-git: not "
                                   "run (git status: fatal: index file corrupt)), so nothing is staged",
                                   "Specs preflight: staying on spec/ACME-1-01-x — the uncommitted paths could not be listed, "
                                   "so no branch is switched (it would have switched to main, as no key of this run names it)"]
              and lines.fill("pre.stay.unlisted", {"<branch>": SPEC, "<default>": "main", stay: 1}) == got["print"][2]
              and got.get("branch") == SPEC and got.get("b4_left") is None and got.get("error") is None,
              "t_status_failed_stay_b4: B4 stays and reports, nothing switched (%r)" % got)

        # t_rerun_unlisted (in process for the failing call): a start whose B4 leaves a branch, a --rerun whose status
        # fails, then a --rerun whose keys name the branch -- the switch back is left undone, as B2 and B4 are
        r, env = world(tmp, "t-rerun-unlisted")
        r.git("switch", "-q", "-c", SPEC)
        r.write("specifications/PRD-ACME-1-x/EPIC-ACME-1-01-x/specification.md", "s\n")
        r.commit_all("ACME-1-01 Add the specification")
        got = run_start(env, "/document", "--key", "ACME-2")
        check(got.get("branch") == "main" and got.get("b4_left") == SPEC, "t_rerun_unlisted: B4 leaves the branch (%r)" % got)
        g["status"] = broken_status
        try:
            with in_env(env):
                got = start(r.path, "/document", ("ACME-2",), rerun=True)
        finally:
            g["status"] = real_status
        check(got.get("print") == [env_line(r.path), "Specs preflight: could not list the uncommitted paths (specs-git: not "
                                   "run (git status: fatal: index file corrupt)), so nothing is staged"]
              and got.get("branch") == "main" and got.get("b4_left") == SPEC
              and "pre.status-failed" in ((record(env, "/document") or {}).get("reported") or []),
              "t_rerun_unlisted: the re-run's status fails, its report recorded (%r)" % got)
        got = run_start(env, "/document", "--rerun", "--key", "ACME-2", "--key", "ACME-1-01")
        check(got.get("print") == [env_line(r.path), "Specs preflight: staying on main — the uncommitted paths could not be "
                                   "listed, so no branch is switched (it would have switched back to spec/ACME-1-01-x, as a "
                                   "key of this run names it)"]
              and lines.fill("pre.rerun-stay", {"<current>": "main", "<branch>": SPEC}) == got["print"][1]
              and got.get("branch") == "main" and r.git("symbolic-ref", "--short", "HEAD") == "main"
              and got.get("b4_left") == SPEC and got.get("error") is None,
              "t_rerun_unlisted: no switch back after the run's status failure (%r)" % got)

        # t_flush_order (in process): the dirty flush tests step 5's conditions in order, push-scope last, so a branch
        # origin lacks stops silently before push-scope is measured
        r, env = world(tmp, "t-flush-order")
        r.git("switch", "-q", "-c", PLUGIN)
        r.write("specifications/PRD-ACME-1-x/ard.md", "a\n")
        r.commit_all("ACME-1 Add the ARD")
        r.write(RESUME, "r\n")
        real_scope = g["push_scope"]
        measured = []

        def watched_scope(root, branch, session_default_ref=None):
            measured.append(branch)
            raise NotRun("git rev-list: fatal: bad object")

        g["push_scope"] = watched_scope
        try:
            with in_env(env):
                got = start(r.path, "/feedback", ("ACME-1",))
        finally:
            g["push_scope"] = real_scope
        check(got.get("print") == [env_line(r.path)] and measured == [] and subject(r) == SUBJECT % ("NOISSUE", "/feedback")
              and on_origin(r, PLUGIN) is None and got.get("error") is None,
              "t_flush_order: origin-lacks stops the push before push-scope is measured, silently (%r, %r)" % (got, measured))

        # t_scope_failed (in process): push-scope cannot run for two branches -- each reported once, neither pushed,
        # B4 naming no count
        r, env = world(tmp, "t-scope-failed")
        Q, P2 = "prd/ACME-9-q", "prd/ACME-3-p"
        r.git("switch", "-q", "-c", P2, "main")
        r.git("push", "-q", "-u", "origin", P2)
        session_commit(r, P2, "PRD-ACME-3-p")
        r.git("switch", "-q", "-c", Q, "main")
        r.write("specifications/PRD-ACME-9-q/prd.md", "q\n")
        r.commit_all("ACME-9 Add the PRD")
        real_scope = g["push_scope"]

        def broken_scope(root, branch, session_default_ref=None):
            if branch in (Q, P2):
                raise NotRun("git rev-list: fatal: bad object")
            return real_scope(root, branch, session_default_ref)

        def scope_failed(branch):
            return ("Specs preflight: could not measure what a push of %s would publish (specs-git: not run (git rev-list: "
                    "fatal: bad object)), so %s is not pushed" % (branch, branch))

        g["push_scope"] = broken_scope
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["push_scope"] = real_scope
        check(got.get("print") == [env_line(r.path), scope_failed(Q), scope_failed(P2),
                                   lines.fill("pre.b4", {"<branch>": Q, "<default>": "main"})]
              and got.get("error") is None and on_origin(r, P2) != rev(r, P2) and got.get("branch") == "main",
              "t_scope_failed: the retry's and the loop's reports, nothing pushed, B4 with no count (%r)" % got)

        # t_settle
        r, env = world(tmp, "t-settle")
        F, P, S = "prd/ACME-2-f", "prd/ACME-3-p", "prd/ACME-4-s"
        ff_merged(r, "t-settle-f", F, "specifications/PRD-ACME-2-f/prd.md")
        squash_merged(r, "t-settle-s", S, "specifications/PRD-ACME-4-s/prd.md")
        s_record = refusal_file(r, S)
        r.git("switch", "-q", "-c", P, "main")
        r.git("push", "-q", "-u", "origin", P)
        session_commit(r, P, "PRD-ACME-3-p")
        r.git("switch", "-q", "main")
        got = run_start(env, "/feedback")
        advisory = lines.fill("pre.advisory-D", {"<branch>": S, "<default>": "main", "<SPECS_PATH>": r.path})
        check(got.get("print") == [env_line(r.path), "Specs preflight: deleted merged prd/ACME-2-f",
                                   "Specs preflight: pushed 1 session-file commit(s) left on prd/ACME-3-p", advisory,
                                   'rm -f "%s"' % s_record]
              and rev(r, F) is None and rev(r, S) is not None and on_origin(r, P) == rev(r, P),
              "t_settle: deleted merged, pushed left, the -D advisory with its rm (%r)" % got)
        check((record(env, "/feedback") or {}).get("advised_D") == [S], "t_settle: the advisory recorded")
        got = run_start(env, "/feedback", "--rerun")
        check(got.get("print") == [env_line(r.path)] and (record(env, "/feedback") or {}).get("advised_D") == [S],
              "t_settle: the -D advisory is not given again after start --rerun (%r)" % got)

        # t_settle_delete_failed: a branch merged by ancestry -d can see, but checked out in another worktree
        r, env = world(tmp, "t-settle-delete-failed")
        ff_merged(r, "t-settle-delete-failed-other", F, "specifications/PRD-ACME-2-f/prd.md")
        r.git("switch", "-q", "main")
        elsewhere = os.path.join(tmp, "t-settle-delete-failed-wt")
        r.git("worktree", "add", "-q", elsewhere, F)
        got = run_start(env, "/feedback")
        shown = got.get("print") or []
        check(len(shown) == 2 and shown[1].startswith("Specs preflight: could not delete merged %s (error: " % F)
              and rev(r, F) is not None, "t_settle_delete_failed: -d's refusal, never -D (%r)" % got)

        # t_refusal_record_removed: B2's file record, and the settle loop's configuration-key record
        r, env = world(tmp, "t-refusal-removed")
        K = "prd/K-2-k"
        ff_merged(r, "t-refusal-removed-other", A, "specifications/PRD-A-1-x/prd.md")
        r.git("branch", K)
        a_record = refusal_file(r, A)
        r.git("config", "branch.%s.workflowsPushRefused" % K, "2026-11-01")
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), "Specs preflight: deleted merged prd/K-2-k",
                                   "Specs preflight: deleted merged prd/A-1-x"]
              and not os.path.exists(a_record) and got.get("branch") == "main"
              and r.git("config", "--get", "branch.%s.workflowsPushRefused" % K, check=False) == "",
              "t_refusal_record_removed: each deleted branch's push-refusal record goes with it (%r)" % got)

        # t_b2
        r, env = world(tmp, "t-b2")
        B = "prd/ACME-5-a"
        ff_merged(r, "t-b2-other", B, "specifications/PRD-ACME-5-a/prd.md")
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), "Specs preflight: deleted merged prd/ACME-5-a"]
              and got.get("branch") == "main" and got.get("b2_left") == B and rev(r, B) is None
              and head(r) == on_origin(r), "t_b2: switched, pulled, deleted (%r)" % got)
        r, env = world(tmp, "t-b2-squash")
        Q = "prd/ACME-6-q"
        squash_merged(r, "t-b2-squash-other", Q, "specifications/PRD-ACME-6-q/prd.md")
        q_record = refusal_file(r, Q)
        got = run_start(env, "/feedback")
        shown = got.get("print") or []
        squash = lines.fill("pre.b2-squash", {"<branch>": Q, "<default>": "main", "<SPECS_PATH>": r.path})
        check(len(shown) == 4 and shown[1].startswith("Specs preflight: could not delete merged prd/ACME-6-q (error: ")
              and shown[2] == squash and shown[3] == 'rm -f "%s"' % q_record and got.get("branch") == "main"
              and got.get("b2_left") == Q and rev(r, Q) is not None and os.path.exists(q_record),
              "t_b2: a squash-merged branch is kept, -d's refusal and the -D line after it (%r)" % got)
        check((record(env, "/feedback") or {}).get("advised_D") == [Q], "t_b2: the -D line recorded once for the run")

        # t_b2_config (in process): the branch's configuration left behind where .git/config cannot be written
        r, env = world(tmp, "t-b2-config")
        ff_merged(r, "t-b2-config-other", B, "specifications/PRD-ACME-5-a/prd.md")
        real_config = sb.config

        def stuck(root, key, as_bool=False):
            return "refs/heads/" + B if key == "branch.%s.merge" % B else real_config(root, key, as_bool)

        sb.config = stuck
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            sb.config = real_config
        check(got.get("print") == [env_line(r.path), "Specs preflight: deleted merged prd/ACME-5-a",
                                   lines.fill("pre.b2-config", {"<branch>": B, "<SPECS_PATH>": r.path})],
              "t_b2_config: the configuration line after the deletion (%r)" % got)

        # t_b3_b4, t_rerun
        r, env = world(tmp, "t-b3-b4")
        r.git("switch", "-q", "-c", SPEC)
        r.write("specifications/PRD-ACME-1-x/EPIC-ACME-1-01-x/specification.md", "s\n")
        r.commit_all("ACME-1-01 Add the specification")
        got = run_start(env, "/document", "--key", "ACME-1-01", "--key", "ACME-1")
        check(got.get("print") == [env_line(r.path)] and got.get("branch") == SPEC and got.get("b4_left") is None,
              "t_b3_b4: a branch a key of the run names stays (%r)" % got)
        # each later run in a session of its own: in this one the first run, open on SPEC, would keep its branch from a
        # run of its command typed with another key set (specs-repo-git §3.5, M1)
        env = dict(env, CLAUDE_CODE_SESSION_ID="t-b3-b4-2")
        got = run_start(env, "/document", "--key", "ACME-2")
        b4 = (lines.fill("pre.b4", {"<branch>": SPEC, "<default>": "main"}) + lines.fill("pre.b4.count", {"<N>": 1}))
        check(got.get("print") == [env_line(r.path), b4] and got.get("branch") == "main" and got.get("b4_left") == SPEC,
              "t_b3_b4: no key names it, so B4 leaves it, with its count (%r)" % got)
        got = run_start(env, "/document", "--rerun", "--key", "ACME-2", "--key", "ACME-1-01")
        check(got.get("print") == [env_line(r.path)] and got.get("branch") == SPEC and got.get("b4_left") is None
              and got.get("replaced") is None, "t_rerun: back on the branch B4 left (%r)" % got)
        env = dict(env, CLAUDE_CODE_SESSION_ID="t-b3-b4-3")
        got = run_start(env, "/document", "--key", "ACME-2")
        r.git("branch", "-D", SPEC)
        got = run_start(env, "/document", "--rerun", "--key", "ACME-2", "--key", "ACME-1-01")
        shown = got.get("print") or []
        check(len(shown) == 2 and shown[1].startswith("Specs preflight: could not switch back to %s (" % SPEC)
              and shown[1].endswith("); this run goes on from main") and got.get("branch") == "main",
              "t_rerun: a branch deleted meanwhile gives pre.rerun-failed (%r)" % got)

        # t_b4_pull_capped (in process): B4's pull ended by the cap prints its failure line, then B4's report
        r, env = world(tmp, "t-b4-pull-capped")
        r.git("switch", "-q", "-c", SPEC)
        r.write("specifications/PRD-ACME-1-x/EPIC-ACME-1-01-x/specification.md", "s\n")
        r.commit_all("ACME-1-01 Add the specification")
        r.git("push", "-q", "-u", "origin", SPEC)
        real_bounded = sb.git_bounded

        def capped_pull(root, seconds, *args):
            if args and args[0] == "pull":
                return subprocess.CompletedProcess(["git"] + list(args), 124, b"", b"")
            return real_bounded(root, seconds, *args)

        sb.git_bounded = capped_pull
        try:
            with in_env(env):
                got = start(r.path, "/document", ("ACME-2",))
        finally:
            sb.git_bounded = real_bounded
        check(got.get("print") == [env_line(r.path), "Specs preflight: could not fast-forward main (the pull did not finish "
                                   "within 60 s); the run goes on from it as it stands",
                                   lines.fill("pre.b4", {"<branch>": SPEC, "<default>": "main"})]
              and got.get("branch") == "main", "t_b4_pull_capped: the capped pull's words, then B4's report (%r)" % got)

        # t_b4_no_remote: with no origin, <default-ref> is refs/heads/main, so B4 switches and pulls nothing
        r = new_repo(tmp, "t-b4-no-remote")
        env = {"HOME": os.path.join(tmp, "home-t-b4-no-remote"), "CLAUDE_CODE_SESSION_ID": "t-b4-no-remote",
               "SPECS_PATH": r.path}
        os.makedirs(env["HOME"])
        r.git("switch", "-q", "-c", "prd/ACME-9-q")
        r.write("specifications/PRD-ACME-9-q/prd.md", "q\n")
        r.commit_all("ACME-9 Add the PRD")
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), lines.fill("pre.b4", {"<branch>": "prd/ACME-9-q", "<default>": "main"})
                                   + lines.fill("pre.b4.count", {"<N>": 2})]
              and got.get("default_ref") == "refs/heads/main" and got.get("remote") == "none" and got.get("branch") == "main",
              "t_b4_no_remote: no pull and no pull-failed line where there is no origin (%r)" % got)

        # t_b4_no_local_default: no local main, B4 makes it at origin/main by update-ref (specs-repo-git §3.5) and
        # switches. (a) .git/config held locked, as a hardened container's read-only one fails a write: no upstream is
        # set, and the checkout moves whole -- git's own --guess would have written the upstream as it switched, failed
        # there, and left the index and files on main's tree with HEAD on the branch, exit 1, which read as a switch
        # refused with nothing moved. (b) .git/config writable: main tracks origin/main.
        for nld_label, nld_locked in (("locked", True), ("writable", False)):
            r, env = world(tmp, "t-b4-nld-" + nld_label)
            other_key(r)
            r.git("branch", "-q", "-D", "main")
            nld_lock = os.path.join(r.path, ".git", "config.lock")
            if nld_locked:
                open(nld_lock, "w").close()
            try:
                got = run_start(env, "/feedback")
            finally:
                if os.path.exists(nld_lock):
                    os.remove(nld_lock)
            nld_head = r.git("symbolic-ref", "-q", "--short", "HEAD", check=False)
            nld_status = r.git("status", "--porcelain", "--untracked-files=all")
            nld_upstream = r.git("config", "--get", "branch.main.merge", check=False)
            check(got.get("branch") == "main" and nld_head == "main" and nld_status == ""
                  and rev(r, "main") == r.git("rev-parse", "origin/main")
                  and got.get("print") == [env_line(r.path), lines.fill("pre.b4", {"<branch>": "prd/B-2-y", "<default>": "main"})]
                  and nld_upstream == ("" if nld_locked else "refs/heads/main"),
                  "t_b4_no_local_default (%s): main made at origin/main, %s, and the checkout moved whole (%r, head %r, "
                  "status %r, upstream %r)" % (nld_label, "no upstream" if nld_locked else "tracking origin/main", got, nld_head,
                                                   nld_status, nld_upstream))

        # t_rerun_no_guess: the re-run's switch back takes --no-guess (specs-repo-git §3.5), so a branch B4 left that
        # was deleted locally since is not made again from origin's copy -- git's --guess would write its upstream as it
        # switched -- and the re-run goes on from where it stands, pre.rerun-failed printed
        r, env = world(tmp, "t-rerun-no-guess")
        r.git("switch", "-q", "-c", SPEC)
        r.write("specifications/PRD-ACME-1-x/EPIC-ACME-1-01-x/specification.md", "s\n")
        r.commit_all("ACME-1-01 Add the specification")
        r.git("push", "-q", "-u", "origin", SPEC)
        got = run_start(env, "/document", "--key", "ACME-2")
        r.git("branch", "-q", "-D", SPEC)
        got = run_start(env, "/document", "--rerun", "--key", "ACME-2", "--key", "ACME-1-01")
        shown = got.get("print") or []
        check(len(shown) == 2 and shown[1].startswith("Specs preflight: could not switch back to %s (" % SPEC)
              and got.get("branch") == "main" and rev(r, SPEC) is None,
              "t_rerun_no_guess: no switch back makes the deleted branch again from origin's copy (%r)" % got)

        # t_fix_no_local_default: a Fix line that switches to main, where no local main exists (specs-repo-git §5 part
        # 3), makes it first: G2's plain block and G1's on a merged branch, each run as pasted with .git/config held
        # locked, as a hardened container's read-only one fails a write, move the checkout whole onto main, exit 0. A
        # bare `switch main` there takes git's --guess, whose upstream write fails after the index and the files moved:
        # HEAD left where it was, exit 1. The end repeats G2's block with its Fix judged again, and with a local main
        # the Fix is the plain switch. With .git/config writable the line sets main's upstream to origin/main, as git's
        # guess did. Run again after git refused its switch -- an untracked file in the way, then moved -- the same line
        # switches whole, its first command's `already exists` stopping nothing.
        def fix_of(block):
            return next((row[len("Fix:"):].strip() for row in block.split("\n") if row.startswith("Fix:")), "")

        def run_locked(r, line, env):
            lock = os.path.join(r.path, ".git", "config.lock")
            open(lock, "w").close()
            try:
                return shell(line, dict(env, GIT_EDITOR="printf 'NOISSUE notes\\n' >"))["_rc"]
            finally:
                os.remove(lock)

        r, env = world(tmp, "t-fix-nld-g2")
        r.git("switch", "-q", "-c", "feature/x")
        r.write("feature.md", "f\n")
        r.commit_all("NOISSUE feature")
        r.git("branch", "-q", "-D", "main")
        got = run_start(env, "/feedback")
        fix = fix_of((got.get("print") or [""])[-1])
        end = run_end(env, "/feedback")
        end_fix = fix_of((end.get("print") or [""])[-1])
        rc = run_locked(r, fix, env)
        fnld_head = r.git("symbolic-ref", "-q", "--short", "HEAD", check=False)
        fnld_status = r.git("status", "--porcelain", "--untracked-files=no")
        check(got.get("guard") == "G2" and rc == 0 and fnld_head == "main" and fnld_status == ""
              and rev(r, "main") == r.git("rev-parse", "origin/main") and end_fix == fix,
              "t_fix_no_local_default (g2): the Fix, run with .git/config locked, moves the checkout whole onto main, "
              "and the end repeats it (%r, rc %r, head %r, status %r, end %r)" % (fix, rc, fnld_head, fnld_status, end_fix))
        r, env = world(tmp, "t-fix-nld-g2-local")
        r.git("switch", "-q", "-c", "feature/x")
        got = run_start(env, "/feedback")
        check(fix_of((got.get("print") or [""])[-1]) == 'git -C "%s" switch main' % r.path,
              "t_fix_no_local_default (g2, local main): the plain switch (%r)" % got)

        r, env = world(tmp, "t-fix-nld-g2-writable")
        r.git("switch", "-q", "-c", "feature/x")
        r.write("feature.md", "f\n")
        r.commit_all("NOISSUE feature")
        r.git("branch", "-q", "-D", "main")
        got = run_start(env, "/feedback")
        fix = fix_of((got.get("print") or [""])[-1])
        run_end(env, "/feedback")
        rc = shell(fix, env)["_rc"]
        fnld_head = r.git("symbolic-ref", "-q", "--short", "HEAD", check=False)
        fnld_up = (r.git("config", "--get", "branch.main.remote", check=False),
                   r.git("config", "--get", "branch.main.merge", check=False))
        check(rc == 0 and fnld_head == "main" and fnld_up == ("origin", "refs/heads/main"),
              "t_fix_no_local_default (g2, writable): the Fix sets main's upstream to origin/main (%r, rc %r, head %r, "
              "upstream %r)" % (fix, rc, fnld_head, fnld_up))

        r, env = world(tmp, "t-fix-nld-g2-again")
        r.git("switch", "-q", "-c", "feature/x")
        r.git("rm", "-q", PRD)
        r.commit_all("NOISSUE drop the PRD")
        r.git("branch", "-q", "-D", "main")
        got = run_start(env, "/feedback")
        fix = fix_of((got.get("print") or [""])[-1])
        run_end(env, "/feedback")
        r.write(PRD, "mine\n")
        rc1 = run_locked(r, fix, env)
        head1 = r.git("symbolic-ref", "-q", "--short", "HEAD", check=False)
        with open(os.path.join(r.path, PRD), encoding="utf-8") as fh:
            kept = fh.read()
        os.rename(os.path.join(r.path, PRD), os.path.join(r.path, "mine.md"))
        rc2 = run_locked(r, fix, env)
        head2 = r.git("symbolic-ref", "-q", "--short", "HEAD", check=False)
        fnld_status = r.git("status", "--porcelain", "--untracked-files=no")
        check(got.get("guard") == "G2" and rc1 != 0 and head1 == "feature/x" and kept == "mine\n" and rc2 == 0
              and head2 == "main" and fnld_status == "" and rev(r, "main") == r.git("rev-parse", "origin/main"),
              "t_fix_no_local_default (g2, run again): refused over the file in the way, nothing moved; once it is moved, "
              "the same line switches whole (%r, rc %r then %r, head %r then %r, status %r)"
              % (fix, rc1, rc2, head1, head2, fnld_status))

        r, env = world(tmp, "t-fix-nld-g1")
        ff_merged(r, "t-fix-nld-g1-other", A, "specifications/PRD-A-1-x/prd.md")
        r.git("branch", "-q", "-D", "main")
        r.write("notes.md", "n\n")
        got = run_start(env, "/feedback", "--key", "A-1")
        fix = fix_of((got.get("print") or [""])[-1])
        rc = run_locked(r, fix, env)
        fnld_head = r.git("symbolic-ref", "-q", "--short", "HEAD", check=False)
        fnld_status = r.git("status", "--porcelain", "--untracked-files=no")
        check(got.get("guard") == "G1" and rc == 0 and fnld_head == "main" and fnld_status == ""
              and r.git("log", "-1", "--format=%s") == "NOISSUE notes" and r.git("show", "HEAD:notes.md") == "n",
              "t_fix_no_local_default (g1 merged): the Fix, run with .git/config locked, switches to main whole and "
              "commits notes.md there (%r, rc %r, head %r, status %r)" % (fix, rc, fnld_head, fnld_status))

        # t_rerun_blocked: a run --rerun carries blocked into prints the re-run's own block and keeps G0's for end. G0's
        # date is one of the days dated() reads just before and just after the call that rendered it, never one fixed at
        # this scenario's start, so a run across 00:00 UTC passes: t_rerun_blocked_midnight runs the case with the clock
        # start reads crossing midnight between this scenario's start and the render, and
        # t_rerun_blocked_midnight_during with it crossing during the call, after the render (injected, in process; no
        # sleeping)
        def rerun_blocked(label, name, first):
            r, env = world(tmp, name)
            r.git("switch", "-q", "--detach", "HEAD")
            h = head(r)
            got, days, _ = dated(lambda: first(env, "/specify"))
            blocks = [lines.fill("g0", {"<SPECS_PATH>": r.path, "<sha7>": h[:7], "<YYYY-MM-DD>": d, "<branch>": "main"})
                      for d in days]
            g0 = next((b for b in blocks if got.get("print") == [env_line(r.path), b]), blocks[-1])
            check(got.get("print") == [env_line(r.path), g0] and got.get("specs_git") == "blocked",
                  "%s: G0 first (%r)" % (label, got))
            r.git("switch", "-q", "-c", "feature/x")
            got = run_start(env, "/specify", "--rerun")
            g2 = lines.fill("g2", {"<SPECS_PATH>": r.path, "<branch>": "feature/x", "<default>": "main"})
            rec = record(env, "/specify") or {}
            check(got.get("print") == [env_line(r.path), g2] and got.get("specs_git") == "blocked"
                  and got.get("guard") == "G0" and rec.get("guard_block") == g0 and rec.get("guard_paths") == [],
                  "%s: the re-run's G2 printed, G0's fields kept (%r, %r)" % (label, got, rec))
            r.write(RESUME, "r\n")
            got = run_end(env, "/specify")
            check(got.get("row") == "blocked" and got.get("print") == ["Specs repo: NOT COMMITTED — see the notice below", g0]
                  and head(r) == h, "%s: end prints G0's block with the blocked row (%r)" % (label, got))
            return g0
        rerun_blocked("t_rerun_blocked", "t-rerun-blocked", run_start)

        def start_past_midnight(env, command):
            with in_env(env):
                return start(env["SPECS_PATH"], command)
        real_today = g["_today"]
        tomorrow = time.strftime("%Y-%m-%d", time.gmtime(time.time() + 86400))
        g["_today"] = lambda: tomorrow  # the clock _today reads has crossed 00:00 UTC since this scenario started
        try:
            rerun_blocked("t_rerun_blocked_midnight", "t-rerun-blocked-midnight", start_past_midnight)
        finally:
            g["_today"] = real_today
        # ... and with the clock crossing midnight during the call, after the render: G0 carries the day before
        before = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400))  # a day distinct from tomorrow's
        day = [before]

        def start_then_midnight(env, command):
            got = start_past_midnight(env, command)
            day[0] = tomorrow  # 00:00 UTC passes as start returns, after it rendered G0
            return got
        g["_today"] = lambda: day[0]
        try:
            g0 = rerun_blocked("t_rerun_blocked_midnight_during", "t-rerun-blocked-midnight-during", start_then_midnight)
        finally:
            g["_today"] = real_today
        check(day[0] == tomorrow and before in g0 and tomorrow not in g0,
              "t_rerun_blocked_midnight_during: G0 rendered on the day before the crossing, and checked as such (%r)" % g0)

        # t_rerun_no_record
        r, env = world(tmp, "t-rerun-no-record")
        got = run_start(env, "/release-notes", "--rerun")
        check(got.get("print") == [env_line(r.path)] and got.get("replaced") is None
              and (record(env, "/release-notes") or {}).get("stage") == "done",
              "t_rerun_no_record: a fresh start (%r)" % got)

        # t_rerun_resume
        r, env = world(tmp, "t-rerun-resume")
        subprocess.run(["git", "-C", r.bare, "config", "core.logAllRefUpdates", "true"], check=True)
        r.git("switch", "-q", "-c", SPEC)
        r.write("specifications/PRD-ACME-1-x/EPIC-ACME-1-01-x/specification.md", "s\n")
        r.commit_all("ACME-1-01 Add the specification")
        got = run_start(env, "/document", "--key", "ACME-2")
        check(got.get("b4_left") == SPEC, "t_rerun_resume: the first start's B4 (%r)" % got)
        others = ("prd/ACME-3-a", "prd/ACME-4-b")
        for b in others:
            r.git("switch", "-q", "-c", b, "main")
            r.git("push", "-q", "-u", "origin", b)
            session_commit(r, b, "PRD-" + b[4:], "/document")
        r.git("switch", "-q", "main")

        def back():
            return r.git("reflog", "show", "HEAD").count("moving from main to " + SPEC)

        moved = back()
        got = run_start(env, "/document", "--rerun", "--key", "ACME-2", "--key", "ACME-1-01", "--budget", "0")
        want = resume_line(r.path, "/document", "--key", "ACME-2", "--key", "ACME-1-01", "--budget", "0", "--started",
                           got.get("started") or "")
        check(got.get("next") == {"run": want, "timeout_ms": 600000, "on_timeout": None}
              and (record(env, "/document") or {}).get("args", {}).get("keys") == ["ACME-2", "ACME-1-01"]
              and got.get("branch") == SPEC, "t_rerun_resume: next repeats the rerun's own keys, in order (%r)" % got)
        chain = follow(got, env)
        check(len(chain) > 2 and all(c["_rc"] == 0 and fields(c) and c.get("replaced") is None for c in chain[1:])
              and chain[-1].get("next") is None and chain[-1].get("branch") == SPEC
              and (record(env, "/document") or {}).get("stage") == "done",
              "t_rerun_resume: following next continues the same record to done (%r)" % chain[-1])
        check(back() == moved + 1 and all(on_origin(r, b) == rev(r, b) and updates(r, b) == 2 for b in others),
              "t_rerun_resume: the switch back made once, each branch pushed once (%d, %r)"
              % (back() - moved, [updates(r, b) for b in others]))
        seed(env, "/document", stage="settle", settle_todo=None,
             args={"specs": r.path, "keys": ["ACME-2", "ACME-1-01"], "commit_key": None, "register_rebuild": None})
        got = run_start(env, "/document", "--key", "ACME-2", "--resume")
        check((got.get("print") or [None])[0] == env_line(r.path) and got.get("replaced") is not None,
              "t_rerun_resume: the first start's keys fail resumable, and the call runs fresh (%r)" % got)

        # t_nonff_order
        r, env = world(tmp, "t-nonff-order")
        Z = "prd/Z-9-z"
        r.git("switch", "-q", "-c", Z)
        r.write("specifications/PRD-Z-9-z/prd.md", "z\n")
        r.commit_all("Z-9 Add the PRD")
        r.git("push", "-q", "origin", Z)
        r.git("switch", "-q", "main")
        o = clone(r, "t-nonff-order-other")
        o.git("merge", "-q", "--ff-only", "origin/" + Z)
        o.git("push", "-q", "origin", "main")
        o.git("push", "-q", "origin", "--delete", Z)
        r.git("update-ref", "-d", "refs/remotes/origin/" + Z)
        session_commit(r, "main", "PRD-ACME-1-x", name="s1.md")
        r.write(FEED + "s2.md", "s2\n")
        got = run_start(env, "/feedback")
        nxt = got.get("next") or {}
        check(got.get("print") == [env_line(r.path)] and " replay --for start --command /feedback --branch main" in nxt.get("run", "")
              and nxt.get("timeout_ms") == 420000 and rev(r, Z) is not None,
              "t_nonff_order: the current branch's rejected push hands its replay over first, no settle line (%r)" % got)
        chain = follow(got, env)
        shown = [c.get("print") for c in chain[1:]]
        check(len(chain) == 3 and shown[0] and shown[0][0].startswith("Specs preflight: main — pushed after a replay")
              and chain[1].get("next", {}).get("run") == resume_line(r.path, "/feedback", "--started",
                                                                     chain[0].get("started") or "")
              and shown[1] == ["Specs preflight: deleted merged prd/Z-9-z"] and chain[2].get("next") is None
              and (record(env, "/feedback") or {}).get("stage") == "done" and rev(r, Z) is None,
              "t_nonff_order: the replay's line, then the settle line, across the calls (%r)" % shown)
        landed = subprocess.run(["git", "-C", r.bare, "ls-tree", "-r", "--name-only", "main"], stdout=subprocess.PIPE).stdout.decode()
        check(all(p in landed for p in ("specifications/PRD-Z-9-z/prd.md", FEED + "s1.md", FEED + "s2.md")),
              "t_nonff_order: origin's main holds both changes (%r)" % landed)

        # t_replay_stopped: a replay that stops prints pre.stopped and names no next, and the chain ends there
        r, env = world(tmp, "t-replay-stopped")
        o = clone(r, "t-replay-stopped-other")
        o.write(FEED + "o.md", "o\n")
        o.commit_all(SUBJECT % ("NOISSUE", "/specify"))
        o.git("push", "-q", "origin", "main")
        session_commit(r, "main", "PRD-ACME-1-x", name="s1.md")
        got = run_start(env, "/feedback")
        r.git("switch", "-q", "-c", "elsewhere")  # another session moves the checkout before the replay runs
        chain = follow(got, env)
        last = chain[-1]
        check(len(chain) == 2 and last.get("next") is None and last.get("error")
              and (last.get("print") or [""])[0].startswith("Specs preflight: stopped early (")
              and (record(env, "/feedback") or {}).get("stage") == "flush",
              "t_replay_stopped: the chain ends on the replay's pre.stopped, the record as it stood (%r)" % last)

        # t_settle_queue
        r, env = world(tmp, "t-settle-queue")
        Y, X, W = "prd/ACME-2-y", "prd/ACME-3-x", "prd/ACME-9-w"
        for b in (Y, X):
            r.git("switch", "-q", "-c", b, "main")
            r.git("push", "-q", "-u", "origin", b)
        o = clone(r, "t-settle-queue-other")
        for b in (Y, X):
            o.git("switch", "-q", b)
            o.write("specifications/PRD-%s/dev-workflows/feedback/o.md" % b[4:], "o\n")
            o.commit_all(SUBJECT % ("NOISSUE", "/specify"))
            o.git("push", "-q", "origin", b)
            session_commit(r, b, "PRD-" + b[4:])
        r.git("switch", "-q", "-c", W, "main")
        r.write("specifications/PRD-ACME-9-w/prd.md", "w\n")
        r.commit_all("ACME-9 Add the PRD")
        r.git("push", "-q", "-u", "origin", W)
        # At --budget 0 each start call makes one unit of capped calls, so the two rejections queue across calls, and
        # the start --resume the last replay names repeats the budget the record holds.
        calls = [run_start(env, "/feedback", "--budget", "0")]
        while ((calls[-1].get("next") or {}).get("run") and " replay --for start " not in calls[-1]["next"]["run"]
               and len(calls) < 8):
            calls.append(shell(calls[-1]["next"]["run"], env))
        rec = record(env, "/feedback") or {}
        resume0 = resume_line(r.path, "/feedback", "--budget", "0", "--started", calls[0].get("started") or "")
        check(len(calls) == 3 and all(c["next"]["run"] == resume0 for c in calls[:-1])
              and [p for c in calls for p in c.get("print") or []] == [env_line(r.path)]
              and calls[-1]["next"]["run"].endswith("replay --for start --command /feedback --branch %s --started %s"
                                                    % (Y, calls[0].get("started")))
              and rec.get("stage") == "settle-done" and rec.get("budget") == 0
              and rec.get("pending") == [{"branch": Y, "set_upstream": False, "standing": W},
                                         {"branch": X, "set_upstream": False, "standing": W}],
              "t_settle_queue: both rejections queued, the first replay named (%r, %r)" % (calls[-1], rec))
        chain = follow(calls[-1], env)
        shown = [c.get("print") for c in chain[1:]]
        b4 = lines.fill("pre.b4", {"<branch>": W, "<default>": "main"})
        check(len(chain) == 4 and shown[0][0].startswith("Specs preflight: %s — pushed after a replay" % Y)
              and shown[1][0].startswith("Specs preflight: %s — pushed after a replay" % X)
              and chain[2].get("next") == {"run": resume0, "timeout_ms": 600000, "on_timeout": None} and shown[2] == [b4]
              and on_origin(r, Y) == rev(r, Y) and on_origin(r, X) == rev(r, X) and chain[3].get("branch") == "main"
              and chain[3].get("next") is None,
              "t_settle_queue: the two replays in order, the last naming start --resume with the run's --budget 0, "
              "which runs §3.5 (%r)" % shown)

        # t_budget_resume: --budget 0, followed to its end, against one call with the default budget on a copy
        r, env = world(tmp, "t-budget")
        subprocess.run(["git", "-C", r.bare, "config", "core.logAllRefUpdates", "true"], check=True)
        branches = ("prd/ACME-2-a", "prd/ACME-3-b", "prd/ACME-4-c")
        for b in branches:
            r.git("switch", "-q", "-c", b, "main")
            r.git("push", "-q", "-u", "origin", b)
            session_commit(r, b, "PRD-" + b[4:])
        r.git("switch", "-q", "main")
        c_bare, c_path = os.path.join(tmp, "t-budget-copy.git"), os.path.join(tmp, "t-budget-copy")
        shutil.copytree(r.bare, c_bare, symlinks=True)
        shutil.copytree(r.path, c_path, symlinks=True)
        copy = Repo(c_path)
        copy.bare = c_bare
        copy.git("remote", "set-url", "origin", c_bare)
        c_env = {"HOME": os.path.join(tmp, "home-t-budget-copy"), "CLAUDE_CODE_SESSION_ID": "t-budget-copy",
                 "SPECS_PATH": c_path}
        os.makedirs(c_env["HOME"])
        got = run_start(env, "/feedback", "--budget", "0")
        calls, landed = [got], [sum(on_origin(r, b) == rev(r, b) for b in branches)]
        while (calls[-1].get("next") or {}).get("run") and len(calls) < 8:
            calls.append(shell(calls[-1]["next"]["run"], env))
            landed.append(sum(on_origin(r, b) == rev(r, b) for b in branches))
        check(len(calls) == 4 and landed == [0, 1, 2, 3] and all(c["_rc"] == 0 and fields(c) for c in calls)
              and all(c["next"] == {"run": resume_line(r.path, "/feedback", "--budget", "0", "--started",
                                                       got.get("started") or ""), "timeout_ms": 600000,
                                    "on_timeout": None} for c in calls[:-1]) and calls[-1].get("next") is None,
              "t_budget_resume: each call one push, each naming start --resume, to the end (%r)" % landed)
        check(all(updates(r, b) == 2 for b in branches), "t_budget_resume: every branch pushed exactly once")
        one = run_start(c_env, "/feedback")
        stitched = [p for c in calls for p in c.get("print") or []]
        check(one.get("next") is None and [p.replace(c_path, r.path) for p in one.get("print") or []]
              == [p.replace(env_line(r.path), env_line(c_path).replace(c_path, r.path)) for p in stitched]
              and all(on_origin(copy, b) == on_origin(r, b) for b in branches + ("main",))
              and copy.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads")
              == r.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads")
              and {k: v for k, v in (record(c_env, "/feedback") or {}).items() if k in ("stage", "branch", "pending")}
              == {k: v for k, v in (record(env, "/feedback") or {}).items() if k in ("stage", "branch", "pending")},
              "t_budget_resume: the same final state as one call with the default budget (%r)" % one)

        # t_replaced
        r, env = world(tmp, "t-replaced")
        seed(env, "/create-ard", specs_git="misrooted", misrooted_notice=["stale"], guard="G1", guard_block="stale block",
             guard_paths=["n.md"], declined=["d.md"], advised_D=["prd/X-1-x"], b4_left="prd/Y-1-y", stage="settle")
        old = record(env, "/create-ard") or {}
        got = run_start(env, "/create-ard")
        rec = record(env, "/create-ard") or {}
        check(got.get("replaced") == {"command": "/create-ard", "started": old.get("started"), "parked": False}
              and got.get("specs_git") is None and got.get("print") == [env_line(r.path)],
              "t_replaced: the stale record reported as replaced, not parked (%r)" % got)
        check(all(rec.get(k) == state.FIELDS[k] for k in ("specs_git", "misrooted_notice", "guard", "guard_block",
                                                          "guard_paths", "declined", "advised_D", "b4_left")),
              "t_replaced: the new record holds no flag of the old one (%r)" % rec)

        # t_two_commands: /feedback is typed mid-run on main while /specify's run stands open there (§3.5), so a
        # session file written before /feedback's start would be the open run's: /feedback writes its own after its
        # start, and its end commits that alone by the here form, unpushed, its G1 block in the mid-run form;
        # /specify's end then repeats its own block and pushes both
        r, env = world(tmp, "t-two-commands")
        r.write("notes.md", "n\n")
        got = run_start(env, "/specify")
        block_s = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 1, "<path list>": ["notes.md", "notes.md"]})
        check(got.get("print") == [env_line(r.path), block_s], "t_two_commands: /specify's block (%r)" % got)
        spec_rec = record(env, "/specify")
        up = on_origin(r)
        r.write(RESUME, "specify's\n")  # /specify's file in progress, dirty before /feedback's start
        r.write("notes2.md", "n2\n")
        got = run_start(env, "/feedback")
        block_f = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 2,
                                    "<path list>": ["notes.md, notes2.md", "notes.md notes2.md"]})
        rows = block_f.split("\n")
        at = {x: next(k for k, row in enumerate(rows) if row.startswith(x)) for x in ("Fix:", "If ignored:")}
        midrun_f = "\n".join(rows[:at["Fix:"]] + ["Fix:", "If ignored: " + lines.fill("g1.midrun.if_ignored",
                                                                                   {"<command>": "/specify"})])
        check(got.get("print") == [env_line(r.path), midrun_f]
              and (got.get("midrun") or {}).get("command") == "/specify",
              "t_two_commands: /feedback, typed mid-run, prints its block in the mid-run form (%r)" % got)
        r.write(FEED + "f.md", "f\n")
        got = run_end(env, "/feedback")
        here = lines.fill("row.here", {"<sha7>": head(r)[:7], "<N>": 1, "<branch>": "main", "<command>": "/specify",
                                       lines.placeholder("row.here", "<the next push"): 0})
        mine = head(r)
        check(got.get("row") == "here" and got.get("print") == [here, midrun_f] and on_origin(r) == up
              and r.git("show", "--name-only", "--format=", "HEAD") == FEED + "f.md"
              and record(env, "/feedback") is None and record(env, "/specify") == spec_rec
              and "?? " + RESUME in r.git("status", "--porcelain", "--untracked-files=all"),
              "t_two_commands: /feedback's end commits its own file by the here form, unpushed, and repeats its "
              "block in the mid-run form; /specify's file and record untouched (%r)" % got)
        got = run_end(env, "/specify")
        check(got.get("print") == [pushed_default(head(r)[:7], r.path), block_s] and on_origin(r) == head(r)
              and r.git("rev-parse", "HEAD^") == mine and r.git("show", "--name-only", "--format=", "HEAD") == RESUME
              and record(env, "/specify") is None,
              "t_two_commands: /specify's end commits its own file and pushes both, repeating the block its own start "
              "saved (%r)" % got)

        # t_prune
        r, env = world(tmp, "t-prune")
        with in_env(env):
            for session, command, days in (("old-session", "/specify", 8), ("new-session", "/specify", 6),
                                           ("t-prune", "/create-ard", 8)):
                state.save(session, command, state.new(command, session=session))
                stamp = time.time() - days * 86400
                os.utime(state.path(session, command), (stamp, stamp))
        run_start(env, "/feedback")
        with in_env(env):
            kept = [os.path.exists(state.path(s, c)) for s, c in (("old-session", "/specify"), ("new-session", "/specify"),
                                                                  ("t-prune", "/create-ard"), ("t-prune", "/feedback"))]
            gone_dir = not os.path.exists(os.path.join(state.root(), "old-session"))
        check(kept == [False, True, True, True] and gone_dir,
              "t_prune: another session's record 8 days old gone, 6 days kept, this session's kept (%r)" % kept)

        # t_resume_stale
        r, env = world(tmp, "t-resume-stale")
        seed(env, "/create-ard", specs_git="misrooted", misrooted_notice=["Specs preflight: a stale notice"], stage="done")
        real_save = state.save

        def interrupted(*args, **kw):
            raise KeyboardInterrupt

        stopped = False
        state.save = interrupted
        try:
            with in_env(env):
                start(r.path, "/create-ard")
        except KeyboardInterrupt:
            stopped = True
        finally:
            state.save = real_save
        check(stopped and (record(env, "/create-ard") or {}).get("specs_git") == "misrooted",
              "t_resume_stale: a start stopped before its first write leaves the stale record")
        got = run_start(env, "/create-ard", "--resume")
        check(got.get("print") == [env_line(r.path)] and got.get("specs_git") is None and got.get("replaced") is not None,
              "t_resume_stale: a stale record at done is no resume; a fresh preflight (%r)" % got)

        def aged(minutes):
            with in_env(env):
                rec = state.load(env["CLAUDE_CODE_SESSION_ID"], "/create-ard")
                rec["updated"] = time.strftime(state.STAMP, time.gmtime(time.time() - minutes * 60))
                with open(state.path(env["CLAUDE_CODE_SESSION_ID"], "/create-ard"), "w", encoding="utf-8") as fh:
                    json.dump(rec, fh)

        seed(env, "/create-ard", specs_git="misrooted", misrooted_notice=["Specs preflight: a stale notice"], stage="settle",
             settle_todo=None)
        aged(20)
        got = run_start(env, "/create-ard", "--resume")
        check(got.get("print") == [env_line(r.path)] and got.get("specs_git") is None,
              "t_resume_stale: a record saved 20 minutes ago is no resume either (%r)" % got)
        L = "prd/ACME-7-l"
        r.git("switch", "-q", "-c", L, "main")
        r.git("push", "-q", "-u", "origin", L)
        session_commit(r, L, "PRD-ACME-7-l")
        r.git("switch", "-q", "main")
        seed(env, "/create-ard", stage="settle", settle_todo=None)
        # the resume a next names, by the record's started: one given no --started meets a record not marked
        # call_returned false as a plain start does
        got = run_start(env, "/create-ard", "--resume", "--started", (record(env, "/create-ard") or {}).get("started"))
        check(got.get("print") == ["Specs preflight: pushed 1 session-file commit(s) left on %s" % L]
              and got.get("replaced") is None and fields(got) and on_origin(r, L) == rev(r, L)
              and (record(env, "/create-ard") or {}).get("stage") == "done",
              "t_resume_stale: a record at settle saved now, the same arguments, continues from settle (%r)" % got)

        # t_exit2_nothing_done
        r, env = world(tmp, "t-exit2")
        r.write(RESUME, "r\n")

        def snapshot():
            return (r.git("status", "--porcelain"), head(r), r.git("branch", "--list"), r.git("for-each-ref"),
                    subprocess.run(["git", "-C", r.bare, "for-each-ref"], stdout=subprocess.PIPE).stdout)

        before = snapshot()
        claude = os.path.join(env["HOME"], ".claude")
        got = cli("--specs", r.path, "start", "--command", "/feedback",
                  env={k: v for k, v in env.items() if k != "CLAUDE_CODE_SESSION_ID"})
        check(one_not_run_line(got) and snapshot() == before and not os.path.exists(claude),
              "t_exit2_nothing_done: no session variable, exit 2, one line, nothing done (%r)" % got)
        for args, what in ((("--key", "bad"), "a key off the grammar"), (("--commit-key", "acme-1"), "a lower-case key"),
                           (("--key", "ACME-1\n"), "a key with a newline"), (("--budget", "-1"), "a negative budget"),
                           (("--budget", "soon"), "a budget that is no number")):
            got = run_start(env, "/feedback", *args)
            check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: ") and snapshot() == before
                  and not os.path.exists(claude), "t_exit2_nothing_done: %s is a usage exit 2 (%r)" % (what, got))
        got = cli("--specs", r.path, "start", "--command", "feedback", env=env)
        check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: ") and not os.path.exists(claude),
              "t_exit2_nothing_done: a command without its slash (%r)" % got)
        got = cli("start", "--command", "/feedback", env=env)
        check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: "),
              "t_exit2_nothing_done: no --specs at all is a usage error (%r)" % got)

        # t_error_after_write
        r, env = world(tmp, "t-error")
        r.write(RESUME, "r\n")
        real_settle = g["_settle"]

        def boom(*args, **kw):
            raise RuntimeError("boom")

        g["_settle"] = boom
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["_settle"] = real_settle
        stop = ("Specs preflight: stopped early (RuntimeError: boom) — what it did is above, and the next run's preflight "
                "goes on from where this one stands")
        check(got.get("error") == "RuntimeError: boom" and got.get("print") == [env_line(r.path), stop] and set(got) == FIELDS
              and subject(r) == SUBJECT % ("NOISSUE", "/feedback") and on_origin(r) == head(r)
              and (record(env, "/feedback") or {}).get("stage") == "settle",
              "t_error_after_write: exit-0 result, error set, the commit pushed, the record saved (%r)" % got)

        # The landing on a merged plugin branch (S2, §4 step 1): a merged branch the preflight stayed on takes the
        # landing as every stay does -- the run's own session files committed on main, the checkout unmoved, the files
        # lifted -- where an earlier version held them uncommitted. A is fast-forward-merged into origin's main;
        # notes.md is not the plugin's, so G1 fires; RES_A, dirty before the start, is not the run's (S1), so FEED_A,
        # written after it, is the run's own change.
        def merged_world(name):
            r, env = world(tmp, name)
            ff_merged(r, name + "-other", A, "specifications/PRD-A-1-x/prd.md")
            r.write("notes.md", "n\n")
            r.write(RES_A, "r\n")
            return r, env

        def refused_world(name):
            """A merged into origin's main by fast-forward and deleted there, r's main behind it; RES_A differs between
            r's main and A and is dirty, so git refuses the merged-branch leave's switch (t_merged_leave)."""
            r, env = world(tmp, name)
            r.write(RES_A, "main's\n")
            r.commit_all("NOISSUE a resume pointer on main")
            r.git("push", "-q", "origin", "main")
            r.git("switch", "-q", "-c", A)
            r.write(RES_A, "the branch's\n")
            r.commit_all("A-1 work")
            r.git("push", "-q", "-u", "origin", A)
            o = clone(r, name + "-other")
            o.git("merge", "-q", "--ff-only", "origin/" + A)
            o.git("push", "-q", "origin", "main")
            o.git("push", "-q", "origin", "--delete", A)
            r.write(RES_A, "dirty\n")
            return r, env

        FEED_A = "specifications/PRD-A-1-x/dev-workflows/feedback/f.md"

        def gone(r, path):
            return not os.path.lexists(os.path.join(r.path, path))

        def landed_on_main(r, paths):
            """main's tip is the landing's one commit, naming exactly <paths>, and origin's main holds it."""
            tip = rev(r, "main")
            return (tip is not None and on_origin(r) == tip
                    and sorted(r.git("show", "--name-only", "--format=", tip).split()) == sorted(paths))

        # t_land_merged_g1: start prints G1's landing form, merged's alternative, and records the stay; end lands the run's
        # own file on main -- alternative 1 -- and repeats the landing form whole; HEAD and the branch unmoved, the
        # branch still merged, the file lifted, the leftover as it was
        r, env = merged_world("t-land-merged-g1")
        h = head(r)
        landing = g1_landing(r, ["notes.md"], A, "merged")
        got = run_start(env, "/feedback")
        rec = record(env, "/feedback") or {}
        check(got.get("print") == [env_line(r.path), landing] and got.get("guard") == "G1" and got.get("branch") == A
              and fields(got) and got.get("stay") == stayed(A, "g1")
              and rec.get("stay") == stayed(A, "g1") and rec.get("guard_block") == g1_plain(r, ["notes.md"])
              and "WILL be committed at the end of the run on main, not on prd/A-1-x, which is merged into main" in landing
              and "WILL still be committed" not in landing,
              "t_land_merged_g1: G1's landing form printed, the stay recorded, the plain block saved (%r)" % got)
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got["_rc"] == 0 and got.get("row") == "pushed-default"
              and got.get("print") == [landed_row(r, 1, A), g1_landed(r, ["notes.md"], A, "merged")]
              and got.get("line") == landed_row(r, 1, A) and got.get("sha7") == (rev(r, "main") or "")[:7]
              and got.get("pushed") is True and got.get("branch") == "main" and landed_on_main(r, [FEED_A])
              and head(r) == h and rev(r, A) == h and r.git("symbolic-ref", "--short", "HEAD") == A
              and gone(r, FEED_A) and untracked(r, RES_A) and branch_merged(r.path, "HEAD", "origin/main")["merged"]
              and record(env, "/feedback") is None,
              "t_land_merged_g1: end lands the run's file on main, the checkout unmoved, the landing form whole (%r)" % got)

        # t_land_merged_next_run: notes.md cleaned, the next run's preflight leaves the merged branch before its flush
        # (§3.4) and lands the leftover on main, pushed
        os.remove(os.path.join(r.path, "notes.md"))
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), "Specs preflight: deleted merged prd/A-1-x"] and got.get("branch") == "main"
              and rev(r, A) is None and subject(r) == SUBJECT % ("NOISSUE", "/feedback") and on_origin(r) == head(r)
              and r.git("show", "--name-only", "--format=", "HEAD") == RES_A and stay_of(env) is None,
              "t_land_merged_next_run: the next run leaves the branch and commits the files on main (%r)" % got)

        # t_land_merged_fix_line: the review's sequence -- G1's merged-branch Fix line run whole, as printed, through
        # bash -c (its commit's message typed in the editor) after the end landed the run's file: the user's files
        # committed on main, off the merged branch; the next run commits the leftover on main and deletes the branch
        r, env = merged_world("t-land-merged-fix")
        shown = (run_start(env, "/feedback").get("print") or [""])[-1]
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and shown == g1_landing(r, ["notes.md"], A, "merged")
              and got.get("print") == [landed_row(r, 1, A), g1_landed(r, ["notes.md"], A, "merged")] and gone(r, FEED_A),
              "t_land_merged_fix_line: the landing form, merged's alternative, then end lands (%r)" % got)
        fix = next((x for x in shown.split("\n") if x.startswith("Fix:")), "Fix:")
        editor = os.path.join(tmp, "t-land-merged-fix-editor.sh")  # the commit's message, as a user types it in the editor
        with open(editor, "w", encoding="utf-8") as fh:
            fh.write("#!/bin/sh\necho 'my notes' > \"$1\"\n")
        os.chmod(editor, 0o755)
        ran = subprocess.run(["bash", "-c", fix[len("Fix:"):].strip()], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=dict(os.environ, GIT_EDITOR=editor))
        got = run_start(env, "/feedback")
        check(ran.returncode == 0 and got.get("print") == [env_line(r.path), "Specs preflight: deleted merged prd/A-1-x"]
              and got.get("branch") == "main" and rev(r, A) is None and subject(r) == SUBJECT % ("NOISSUE", "/feedback")
              and r.git("show", "--name-only", "--format=", "HEAD") == RES_A
              and r.git("log", "-1", "--format=%s", "HEAD~1") == "my notes" and r.git("status", "--porcelain") == "",
              "t_land_merged_fix_line: the files reach main, the merged branch deleted (%r)" % got)

        # t_land_merged_committed_on_branch: the plain G1 fix instead, a commit on the merged branch after the end
        # landed, which makes it read unmerged: the next run's flush commits the leftover on it, and B4 then leaves it
        r, env = merged_world("t-land-merged-on-branch")
        run_start(env, "/feedback")
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and landed_on_main(r, [FEED_A]),
              "t_land_merged_committed_on_branch: the end lands (%r)" % got)
        r.git("add", "notes.md")
        r.git("commit", "-q", "-m", "my notes")
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), lines.fill("pre.b4", {"<branch>": A, "<default>": "main"})
                                   + lines.fill("pre.b4.count", {"<N>": 2})]
              and got.get("branch") == "main" and r.git("log", "-1", "--format=%s", A) == SUBJECT % ("NOISSUE", "/feedback")
              and r.git("log", "-1", "--format=%s", A + "~1") == "my notes" and stay_of(env) is None,
              "t_land_merged_committed_on_branch: the leftover committed on the branch, B4's line naming both commits "
              "(%r)" % got)

        # t_land_merged_status_failed (in process): status cannot run at start, so B2 stays (pre.stay.unlisted), the stay
        # is recorded and no snapshot is taken; end, whose status runs, lands against HEAD -- the leftover with the rest
        # -- and says so (app.landed.unlisted); no block, since no guard fired
        r, env = merged_world("t-land-merged-status")
        h = head(r)
        g["status"] = broken_status
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["status"] = real_status
        check(got.get("branch") == A and got.get("guard") is None and got.get("error") is None
              and stay_of(env) == stayed(A, "unlisted") and got.get("start_dirty") is None,
              "t_land_merged_status_failed: B2 stays, the stay recorded, no snapshot (%r)" % got)
        got = run_end(env, "/feedback")
        unlisted = lines.fill("app.landed.unlisted", {"<branch>": A})
        check(got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A) + unlisted]
              and head(r) == h and landed_on_main(r, [RES_A]) and gone(r, RES_A),
              "t_land_merged_status_failed: end lands the leftover too, and says so (%r)" % got)

        # t_land_merged_leave_refused: git refuses the merged-branch leave's switch, so the flush commits on the branch
        # with the cherry-pick line; a session file written after it is the run's, and lands on main
        r, env = refused_world("t-land-merged-refused")
        got = run_start(env, "/feedback", "--key", "A-1")
        shown = got.get("print") or []
        flushed = head(r)
        check(len(shown) == 3 and shown[1].startswith("Specs preflight: could not switch from merged prd/A-1-x to main (")
              and shown[2] == lines.fill("pre.merged-flush", {"<branch>": A, "<sha7>": flushed[:7], "<default>": "main",
                                                              "<SPECS_PATH>": r.path})
              and got.get("branch") == A and stay_of(env) == stayed(A, "refused"),
              "t_land_merged_leave_refused: the flush on the branch, the cherry-pick line, the stay recorded (%r)" % got)
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A)] and head(r) == flushed
              and landed_on_main(r, [FEED_A]) and gone(r, FEED_A),
              "t_land_merged_leave_refused: a session file written after the start lands on main (%r)" % got)
        # with no key naming it, B4 leaves the branch the flush made unmerged, and that clears the stay
        r, env = refused_world("t-land-merged-refused-b4")
        got = run_start(env, "/feedback")
        check(got.get("branch") == "main" and got.get("b4_left") == A and stay_of(env) is None,
              "t_land_merged_leave_refused: a start that leaves the branch clears the stay (%r)" % got)

        # t_land_merged_resume: --budget 0 splits that start across calls; the stay one call records stands through the
        # next
        r, env = world(tmp, "t-land-merged-resume")
        B = "spec/B-1-y"
        r.git("switch", "-q", "-c", B)
        r.git("push", "-q", "-u", "origin", B)
        session_commit(r, B, "PRD-B-1-y")
        r.git("switch", "-q", "main")
        r.write(RES_A, "main's\n")
        r.commit_all("NOISSUE a resume pointer on main")
        r.git("push", "-q", "origin", "main")
        r.git("switch", "-q", "-c", A)
        r.write(RES_A, "the branch's\n")
        r.commit_all("A-1 work")
        r.git("push", "-q", "-u", "origin", A)
        o = clone(r, "t-land-merged-resume-other")
        o.git("merge", "-q", "--ff-only", "origin/" + A)
        o.git("push", "-q", "origin", "main")
        o.git("push", "-q", "origin", "--delete", A)
        r.write(RES_A, "dirty\n")
        calls = follow(run_start(env, "/feedback", "--key", "A-1", "--budget", "0"), env)
        shown = [line for c in calls for line in (c.get("print") or [])]
        check(len(calls) == 3 and calls[-1].get("next") is None and calls[-1].get("branch") == A
              and "Specs preflight: pushed 1 session-file commit(s) left on spec/B-1-y" in shown
              and stay_of(env) == stayed(A, "refused"),
              "t_land_merged_resume: the stay recorded in one call stands through the resume after it (%r)" % shown)
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A)]
              and landed_on_main(r, [FEED_A]),
              "t_land_merged_resume: end lands on the stay the split start recorded (%r)" % got)

        # t_land_merged_rerun_clears: a --rerun's preflight derives its own stay; leaving the merged branch, it keeps
        # none
        r, env = merged_world("t-land-merged-rerun")
        run_start(env, "/feedback")
        os.remove(os.path.join(r.path, "notes.md"))
        got = run_start(env, "/feedback", "--rerun")
        check(got.get("branch") == "main" and got.get("b2_left") == A and stay_of(env) is None,
              "t_land_merged_rerun_clears: the re-run leaves the branch and clears the stay (%r)" % got)
        got = run_end(env, "/feedback")
        check(got.get("row") == "nothing", "t_land_merged_rerun_clears: end goes on as before (%r)" % got)

        # t_land_merged_rerun_stopped (in process for the re-run): a re-run's preflight derives its own stay -- G1 gone,
        # it stops early on the merged branch, so the stay is its own, stopped, and end lands with no notice
        r, env = merged_world("t-land-merged-rerun-stopped")
        run_start(env, "/feedback")
        os.remove(os.path.join(r.path, "notes.md"))
        real_flush = g["_flush"]
        g["_flush"] = boom
        try:
            with in_env(env):
                got = start(r.path, "/feedback", rerun=True)
        finally:
            g["_flush"] = real_flush
        check(got.get("error") == "RuntimeError: boom" and got.get("stay") == stayed(A, "stopped")
              and stay_of(env) == stayed(A, "stopped") and (record(env, "/feedback") or {}).get("guard") is None,
              "t_land_merged_rerun_stopped: the re-run's own reason (%r)" % got)
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A)]
              and landed_on_main(r, [FEED_A]) and untracked(r, RES_A),
              "t_land_merged_rerun_stopped: the end lands the run's file, and no notice (%r)" % got)

        # t_land_merged_rerun_b3: the user commits on the branch in the middle of the run, so it reads unmerged, and a
        # re-run keyed to it stays by B3: no stay, and end commits on the branch
        r, env = merged_world("t-land-merged-rerun-b3")
        run_start(env, "/feedback", "--key", "A-1")
        r.git("add", "notes.md")
        r.git("commit", "-q", "-m", "my notes")
        got = run_start(env, "/feedback", "--rerun", "--key", "A-1")
        check(got.get("branch") == A and got.get("stay") is None and stay_of(env) is None,
              "t_land_merged_rerun_b3: the re-run on B3 keeps no stay (%r)" % got)
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        mine = r.git("rev-list", "-1", "--grep=^my notes$", "HEAD")
        want = lines.fill("row.scope", {"<sha7>": [head(r)[:7], mine[:7]], "<N>": 1, "<branch>": A,
                                        "<subject>": "my notes", "<path>": "notes.md"})
        check(got.get("row") == "scope" and got.get("print") == [want] and got.get("branch") == A and mine
              and on_origin(r, A) != head(r) and not untracked(r, FEED_A),
              "t_land_merged_rerun_b3: end commits on the branch, not pushed past the user's commit (%r)" % got)

        # t_land_merged_b3_g1: an unmerged branch a key of the run names (B3), with G1: the plain block, no stay, and end
        # commits on it as before
        r, env = world(tmp, "t-land-merged-b3")
        r.git("switch", "-q", "-c", PLUGIN)
        r.write("specifications/PRD-ACME-1-x/ard.md", "a\n")
        r.commit_all("ACME-1 Add the ARD")
        r.write("notes.md", "n\n")
        r.write(RESUME, "r\n")
        plain = g1_plain(r, ["notes.md"])
        got = run_start(env, "/feedback", "--key", "ACME-1")
        check(got.get("print") == [env_line(r.path), plain] and got.get("branch") == PLUGIN and stay_of(env) is None,
              "t_land_merged_b3_g1: G1's plain block, no stay (%r)" % got)
        got = run_end(env, "/feedback", "--commit-key", "ACME-1")
        check(got.get("row") == "origin-lacks" and got.get("print") == [lacks_row(r, PLUGIN), plain]
              and got.get("branch") == PLUGIN and got.get("sha7") == head(r)[:7]
              and subject(r) == SUBJECT % ("ACME-1", "/feedback") and r.git("show", "--name-only", "--format=", "HEAD") == RESUME,
              "t_land_merged_b3_g1: end commits on the branch as before (%r)" % got)

        # t_land_merged_moved: HEAD moved off the merged branch before end (a new plugin branch, as a handoff cuts one):
        # end commits there as before, and repeats G1's plain block, since the commit runs
        r, env = merged_world("t-land-merged-moved")
        run_start(env, "/feedback")
        r.git("switch", "-q", "-c", "prd/A-1-y")
        got = run_end(env, "/feedback")
        check(got.get("row") == "origin-lacks" and got.get("branch") == "prd/A-1-y"
              and got.get("print") == [lacks_row(r, "prd/A-1-y"), g1_plain(r, ["notes.md"])] and got.get("sha7") == head(r)[:7]
              and r.git("show", "--name-only", "--format=", "HEAD") == RES_A and not untracked(r, RES_A),
              "t_land_merged_moved: end commits where HEAD now stands, with G1's plain block (%r)" % got)

        # t_land_merged_stopped (in process): the preflight stops early on the merged branch before its switch; it asks
        # branch-merged then, and the stay is recorded; end lands what the run wrote after it
        r, env = world(tmp, "t-land-merged-stopped")
        ff_merged(r, "t-land-merged-stopped-other", A, "specifications/PRD-A-1-x/prd.md")
        g["_settle"] = boom
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["_settle"] = real_settle
        check(got.get("error") == "RuntimeError: boom" and got.get("branch") == A
              and stay_of(env) == stayed(A, "stopped"),
              "t_land_merged_stopped: the stop on the merged branch records the stay (%r)" % got)
        r.write(RES_A, "r\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A)]
              and landed_on_main(r, [RES_A]) and gone(r, RES_A),
              "t_land_merged_stopped: end lands (%r)" % got)

        # t_land_merged_budget: a start that returned at its budget on the merged branch, whose next the run never
        # made, reached neither G1's nor B2's test; end asks branch-merged HEAD itself (§4 step 1) and lands
        r, env = world(tmp, "t-land-merged-budget")
        ff_merged(r, "t-land-merged-budget-other", A, "specifications/PRD-A-1-x/prd.md")
        h = head(r)
        got = run_start(env, "/feedback", "--budget", "0")
        rec = record(env, "/feedback") or {}
        check((got.get("next") or {}).get("run") and rec.get("stage") in START_STAGES and rec.get("branch") == A
              and stay_of(env) is None,
              "t_land_merged_budget: the start stopped at its budget on the branch, no stay (%r)" % rec)
        r.write(RES_A, "r\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A)] and gone(r, RES_A)
              and landed_on_main(r, [RES_A]) and head(r) == h and r.git("symbolic-ref", "--short", "HEAD") == A
              and record(env, "/feedback") is None,
              "t_land_merged_budget: end lands on the branch the start did not leave (%r)" % got)

        # t_land_merged_budget_moved: the same stop, then HEAD on a branch the start never stood on (as a handoff cuts
        # one, at the merged tip): no stay is asked for, and end commits where HEAD stands, as before
        r, env = world(tmp, "t-land-merged-budget-moved")
        ff_merged(r, "t-land-merged-budget-moved-other", A, "specifications/PRD-A-1-x/prd.md")
        run_start(env, "/feedback", "--budget", "0")
        r.git("switch", "-q", "-c", "prd/A-1-y")
        r.write(RES_A, "r\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "origin-lacks" and got.get("print") == [lacks_row(r, "prd/A-1-y")]
              and got.get("branch") == "prd/A-1-y" and got.get("sha7") == head(r)[:7] and not untracked(r, RES_A),
              "t_land_merged_budget_moved: end commits on the branch HEAD moved to (%r)" % got)

        # t_land_merged_budget_done: a record whose start finished holds no stay on a branch it did not leave, so end
        # asks nothing and commits there, as before -- the ask is for an unfinished start alone; an unfinished start on
        # a branch now unmerged that a key of the run names (B3's) holds none either, and end commits there
        r, env = world(tmp, "t-land-merged-budget-done")
        ff_merged(r, "t-land-merged-budget-done-other", A, "specifications/PRD-A-1-x/prd.md")
        r.git("fetch", "-q", "origin")
        seed(env, "/feedback", branch=A)
        r.write(RES_A, "r\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-plugin" and got.get("print") == [plugin_row(r, A)] and got.get("branch") == A
              and got.get("sha7") == head(r)[:7] and on_origin(r, A) == head(r) and not untracked(r, RES_A),
              "t_land_merged_budget_done: a finished start's record, end commits (%r)" % got)
        seed(env, "/feedback", branch=A, stage="settle", keys=["A-1"])
        r.write(RES_A, "r2\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-plugin" and got.get("print") == [plugin_row(r, A)] and got.get("branch") == A
              and got.get("sha7") == head(r)[:7] and on_origin(r, A) == head(r),
              "t_land_merged_budget_done: an unfinished start on an unmerged branch a key names, end commits (%r)" % got)

        # t_land_merged_nothing: the stay recorded and nothing of the run's dirty at end: step 3's nothing to commit
        # line stands, then the landing form with its not-landed Not done
        r, env = merged_world("t-land-merged-nothing")
        run_start(env, "/feedback")
        os.remove(os.path.join(r.path, RES_A))
        got = run_end(env, "/feedback")
        check(got.get("row") == "nothing" and got.get("print") == ["Specs repo: no session artifacts to commit",
                                                                  g1_unlanded(r, ["notes.md"], A, "merged")],
              "t_land_merged_nothing: nothing to stage, nothing to commit, the not-landed form (%r)" % got)

        # t_land_merged_declined: a recorded declined path is named on the row, after app.landed, before G1's block
        r, env = merged_world("t-land-merged-declined")
        run_start(env, "/feedback")
        ARD_A = "specifications/PRD-A-1-x/ard.md"
        r.write(ARD_A, "a\n")
        r.write(FEED_A, "f\n")
        got = cli("declined", "--command", "/feedback", "--path", ARD_A, env=env)
        check(got["_rc"] == 0, "t_land_merged_declined: the declined call ran (%r)" % got)
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default"
              and got.get("print") == [landed_row(r, 1, A) + "; the deliverable at %s remains uncommitted, as you asked"
                                       % ARD_A, g1_landed(r, ["notes.md"], A, "merged")]
              and untracked(r, ARD_A) and untracked(r, RES_A) and landed_on_main(r, [FEED_A]),
              "t_land_merged_declined: the row takes the declined append after app.landed (%r)" % got)

        # t_land_merged_g1_unknown: G1 on a plugin branch whose merge cannot be told (an origin with no default branch
        # yet, as in t_merged_unknown): the report once, beside G1's plain block; no stay, none on --rerun; end commits
        # as before
        bare = os.path.join(tmp, "t-land-merged-unknown.git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
        r = new_repo(tmp, "t-land-merged-unknown")
        r.git("remote", "add", "origin", bare)
        env = {"HOME": os.path.join(tmp, "home-t-land-merged-unknown"), "CLAUDE_CODE_SESSION_ID": "t-land-merged-unknown",
               "SPECS_PATH": r.path}
        os.makedirs(env["HOME"])
        r.git("switch", "-q", "-c", PLUGIN)
        r.write("specifications/PRD-ACME-1-x/prd.md", "p\n")
        r.commit_all("ACME-1 Add the PRD")
        r.write("notes.md", "n\n")
        r.write(RESUME, "r\n")
        plain = g1_plain(r, ["notes.md"])
        got = run_start(env, "/feedback", "--key", "ACME-1")
        check(got.get("print") == [env_line(r.path), unknown(PLUGIN), plain] and stay_of(env) is None
              and (record(env, "/feedback") or {}).get("reported") == ["pre.merged-unknown " + PLUGIN],
              "t_land_merged_g1_unknown: the report once, G1's plain block, no stay (%r)" % got)
        got = run_start(env, "/feedback", "--rerun", "--key", "ACME-1")
        check(got.get("print") == [env_line(r.path), plain] and stay_of(env) is None,
              "t_land_merged_g1_unknown: a --rerun reports nothing again, and keeps no stay (%r)" % got)
        got = run_end(env, "/feedback", "--commit-key", "ACME-1")
        check(got.get("row") == "origin-lacks" and got.get("print") == [lacks_row(r, PLUGIN), plain]
              and got.get("sha7") == head(r)[:7] and r.git("show", "--name-only", "--format=", "HEAD") == RESUME,
              "t_land_merged_g1_unknown: end commits on the branch as before (%r)" % got)

        # t_land_merged_refused_kill (in process): a kill right after the flush commits on the branch whose leave git
        # refused -- the commit that makes the branch read unmerged -- finds the stay already saved, and end lands
        r, env = refused_world("t-land-merged-kill")
        real_commit = g["commit_session_files"]

        def commit_then_kill(*args, **kw):
            real_commit(*args, **kw)
            raise KeyboardInterrupt

        g["commit_session_files"] = commit_then_kill
        killed = False
        try:
            with in_env(env):
                start(r.path, "/feedback", ("A-1",))
        except KeyboardInterrupt:
            killed = True
        finally:
            g["commit_session_files"] = real_commit
        check(killed and subject(r) == SUBJECT % ("NOISSUE", "/feedback") and stay_of(env) == stayed(A, "refused"),
              "t_land_merged_refused_kill: the stay saved before the flush commits (%r)" % record(env, "/feedback"))
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A)]
              and landed_on_main(r, [FEED_A]) and gone(r, FEED_A),
              "t_land_merged_refused_kill: end lands on the saved stay (%r)" % got)

        # t_land_merged_g1_kill (in process): a kill right after G1's stay is saved finds G1's block saved beside it, so
        # end's landing repeats that block, in the landing form
        r, env = merged_world("t-land-merged-g1-kill")
        real_stay = g["_stay"]

        def stay_then_kill(*args, **kw):
            real_stay(*args, **kw)
            raise KeyboardInterrupt

        g["_stay"] = stay_then_kill
        killed = False
        try:
            with in_env(env):
                start(r.path, "/feedback")
        except KeyboardInterrupt:
            killed = True
        finally:
            g["_stay"] = real_stay
        rec = record(env, "/feedback") or {}
        check(killed and rec.get("stay") == stayed(A, "g1") and rec.get("guard") == "G1"
              and rec.get("guard_block") == g1_plain(r, ["notes.md"]) and rec.get("guard_paths") == ["notes.md"],
              "t_land_merged_g1_kill: the stay saved with G1's block (%r)" % rec)
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default"
              and got.get("print") == [landed_row(r, 1, A), g1_landed(r, ["notes.md"], A, "merged")],
              "t_land_merged_g1_kill: end's landing, then the notice in the landing form (%r)" % got)

        # The run's snapshot (specs-repo-git §7): the session files dirty when a fresh start that is not a --rerun took
        # it, each kept as a blob, narrowed as each call returns to the paths still dirty.
        B = "prd/B-2-y"
        S_FILE = "specifications/PRD-ACME-1-x/dev-workflows/feedback/s.md"

        def blob(r, path):
            """The blob id of <path>'s working copy, as git would store it; nothing written."""
            return r.git("hash-object", "--", path)

        def stored(r, sha):
            return subprocess.run(["git", "-C", r.path, "cat-file", "-e", sha], stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL).returncode == 0

        # t_snap_g1: G1 ends the preflight on a branch no key names; the snapshot names the dirty session file, with a
        # blob the object store holds, and not notes.md, which is not the plugin's
        r, env = world(tmp, "t-snap-g1")
        other_key(r)
        r.write("notes.md", "n\n")
        r.write(S_FILE, "t-snap-g1\n")
        got = run_start(env, "/feedback", "--key", "ACME-1")
        want = blob(r, S_FILE)
        check(got.get("guard") == "G1" and got.get("start_dirty") == {S_FILE: want}
              and (record(env, "/feedback") or {}).get("start_dirty") == {S_FILE: want} and stored(r, want),
              "t_snap_g1: the snapshot names the session file, its blob written (%r)" % got)

        # t_snap_narrowed: on main, the dirty session file the flush commits leaves the snapshot as the call returns
        r, env = world(tmp, "t-snap-narrowed")
        r.write(S_FILE, "t-snap-narrowed\n")
        got = run_start(env, "/feedback")
        check(got.get("start_dirty") == {} and (record(env, "/feedback") or {}).get("start_dirty") == {}
              and subject(r) == SUBJECT % ("NOISSUE", "/feedback")
              and r.git("show", "--name-only", "--format=", "HEAD") == S_FILE,
              "t_snap_narrowed: the flushed session file narrowed out of the snapshot (%r)" % got)

        # t_snap_misrooted: SPECS_PATH below the top level -- no snapshot, and no object written for the session file
        r, env = world(tmp, "t-snap-misrooted")
        nested = "specs/" + S_FILE
        r.write(nested, "t-snap-misrooted\n")
        got = run_start(env, "/feedback", specs=os.path.join(r.path, "specs"))
        check(got.get("specs_git") == "misrooted" and "start_dirty" in got and got["start_dirty"] is None
              and (record(env, "/feedback") or {}).get("start_dirty") is None and not stored(r, blob(r, nested)),
              "t_snap_misrooted: no snapshot, no object written (%r)" % got)

        # t_snap_status_failed (in process): status cannot run, so no snapshot is taken, and its report, once, is in
        # the record's reported -- which end's line reads (§4 step 1)
        r, env = world(tmp, "t-snap-status")
        r.write(S_FILE, "t-snap-status\n")
        g["status"] = broken_status
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["status"] = real_status
        reports = [x for x in got.get("print") or [] if x.startswith("Specs preflight: could not list the uncommitted")]
        check(got.get("error") is None and "start_dirty" in got and got["start_dirty"] is None and len(reports) == 1
              and (record(env, "/feedback") or {}).get("start_dirty") is None
              and "pre.status-failed" in ((record(env, "/feedback") or {}).get("reported") or [])
              and not stored(r, blob(r, S_FILE)),
              "t_snap_status_failed: no snapshot, pre.status-failed reported once and recorded (%r)" % got)

        # t_snap_rerun: a leftover dirty before the run's first start (G1 keeps every preflight from its flush), a
        # session file the run writes after it, then start --rerun: the snapshot is the first start's, the new file not
        # in it; with the leftover gone, the next --rerun narrows it to nothing
        r, env = world(tmp, "t-snap-rerun")
        LEFT, NEW = FEED + "left.md", FEED + "new.md"
        r.write("notes.md", "n\n")
        r.write(LEFT, "t-snap-rerun leftover\n")
        first = run_start(env, "/feedback")
        r.write(NEW, "t-snap-rerun new\n")
        got = run_start(env, "/feedback", "--rerun")
        want = {LEFT: blob(r, LEFT)}
        check(first.get("start_dirty") == want and got.get("start_dirty") == want
              and (record(env, "/feedback") or {}).get("start_dirty") == want,
              "t_snap_rerun: the re-run carries the first start's snapshot, and only that (%r)" % got)
        os.remove(os.path.join(r.path, LEFT))
        got = run_start(env, "/feedback", "--rerun")
        check(got.get("start_dirty") == {} and (record(env, "/feedback") or {}).get("start_dirty") == {},
              "t_snap_rerun: a re-run only narrows the snapshot it carries (%r)" % got)

        # Every stay kept in the record (specs-repo-git §4 step 1): the branch, its kind, its merged flag, its reason.
        # t_stay_g1_unkeyed: G1 on a branch no key of the run names -- the landing form, unkeyed's alternative, with the
        # plain Fix; the plain block saved for end
        r, env = world(tmp, "t-stay-g1-unkeyed")
        other_key(r)
        r.write("notes.md", "n\n")
        got = run_start(env, "/feedback", "--key", "ACME-1")
        rec = record(env, "/feedback") or {}
        want = stayed(B, "g1", kind="unkeyed", merged=False)
        shown = (got.get("print") or [""])[-1]
        check(got.get("print") == [env_line(r.path), g1_landing(r, ["notes.md"], B, "unkeyed")]
              and got.get("stay") == want and rec.get("stay") == want
              and rec.get("guard_block") == g1_plain(r, ["notes.md"])
              and "on main, not on prd/B-2-y, which no key of this run names" in shown
              and "Fix:      git -C \"%s\" status\n" % r.path in shown,
              "t_stay_g1_unkeyed: G1's landing form, the stay kept, the plain block saved (%r)" % got)

        # t_stay_g1_keyed: a key of the run names the branch -- the plain block, its reworded Not done, no stay
        r, env = world(tmp, "t-stay-g1-keyed")
        other_key(r)
        r.write("notes.md", "n\n")
        got = run_start(env, "/feedback", "--key", "B-2")
        check(got.get("print") == [env_line(r.path), g1_plain(r, ["notes.md"])] and "stay" in got and got["stay"] is None
              and stay_of(env) is None and "did not commit or push" in (got.get("print") or [""])[-1],
              "t_stay_g1_keyed: G1's plain block, no stay (%r)" % got)

        # t_stay_g1_commit_key: the start's commit key names the branch -- no stay
        r, env = world(tmp, "t-stay-g1-commit-key")
        other_key(r)
        r.write("notes.md", "n\n")
        got = run_start(env, "/feedback", "--commit-key", "B-2")
        check(got.get("print") == [env_line(r.path), g1_plain(r, ["notes.md"])] and "stay" in got and got["stay"] is None
              and stay_of(env) is None, "t_stay_g1_commit_key: no stay (%r)" % got)

        # t_stay_g1_merged: G1 on a fast-forward-merged branch a key of the run names -- merged wins: the landing form,
        # merged's alternative, its Fix and If ignored; kind and flag merged
        r, env = world(tmp, "t-stay-g1-merged")
        ff_merged(r, "t-stay-g1-merged-other", A, "specifications/PRD-A-1-x/prd.md")
        r.write("notes.md", "n\n")
        got = run_start(env, "/feedback", "--key", "A-1")
        shown = (got.get("print") or [""])[-1]
        check(got.get("print") == [env_line(r.path), g1_landing(r, ["notes.md"], A, "merged")]
              and got.get("stay") == stayed(A, "g1") and stay_of(env) == stayed(A, "g1")
              and "which is merged into main" in shown and "Fix:      git -C \"%s\" switch main && " % r.path in shown,
              "t_stay_g1_merged: the landing form, merged's alternative (%r)" % got)

        # t_stay_unlisted_b4 (in process): status cannot run, so B4 stays and says so, and keeps the branch as a stay
        r, env = world(tmp, "t-stay-unlisted-b4")
        other_key(r)
        g["status"] = broken_status
        try:
            with in_env(env):
                got = start(r.path, "/feedback", ("ACME-1",))
        finally:
            g["status"] = real_status
        unlisted = lines.fill("pre.stay.unlisted", {"<branch>": B, "<default>": "main",
                                                    lines.placeholder("pre.stay.unlisted", "<switched"): 1})
        want = stayed(B, "unlisted", kind="unkeyed", merged=False)
        check((got.get("print") or [""])[-1] == unlisted and got.get("branch") == B and got.get("error") is None
              and got.get("stay") == want and stay_of(env) == want,
              "t_stay_unlisted_b4: pre.stay.unlisted's B4 alternative, the stay kept (%r)" % got)

        # t_stay_b4_refused: an index.lock -- the flush is Locked, git refuses B4's switch, and the preflight stops,
        # the stay kept before it does
        r, env = world(tmp, "t-stay-b4-refused")
        other_key(r)
        r.write(S_FILE, "t-stay-b4-refused\n")
        lock = os.path.join(r.path, ".git", "index.lock")
        open(lock, "w").close()
        try:
            got = run_start(env, "/feedback", "--key", "ACME-1")
        finally:
            os.remove(lock)
        shown = got.get("print") or [""]
        want = stayed(B, "refused", kind="unkeyed", merged=False)
        check(lines.preflight_form(T["row.locked"]) in shown and str(got.get("error")).startswith("git switch main: ")
              and shown[-1] == lines.fill("pre.stopped", {"<the error>": got.get("error")}) and got.get("branch") == B
              and got.get("stay") == want and stay_of(env) == want,
              "t_stay_b4_refused: Locked, B4's switch refused, pre.stopped, the stay kept (%r)" % got)

        # t_stay_stopped (in process): the preflight stops before B4's switch; the early stop's ask keeps the stay
        r, env = world(tmp, "t-stay-stopped")
        other_key(r)
        real_disposition = g["_disposition"]
        g["_disposition"] = boom
        try:
            with in_env(env):
                got = start(r.path, "/feedback", ("ACME-1",))
        finally:
            g["_disposition"] = real_disposition
        want = stayed(B, "stopped", kind="unkeyed", merged=False)
        check(got.get("error") == "RuntimeError: boom" and got.get("branch") == B and got.get("stay") == want
              and stay_of(env) == want, "t_stay_stopped: the early stop keeps the stay (%r)" % got)

        # t_stay_cleared: a --rerun whose merged-branch leave git refuses keeps a stay, its flush then commits on the
        # branch, and B4 leaves it: the switch that leaves the branch clears the stay
        r, env = refused_world("t-stay-cleared")
        r.write("notes.md", "n\n")
        first = run_start(env, "/feedback")
        os.remove(os.path.join(r.path, "notes.md"))
        got = run_start(env, "/feedback", "--rerun")
        shown = got.get("print") or []
        check(first.get("stay") == stayed(A, "g1")
              and any(x.startswith("Specs preflight: could not switch from merged prd/A-1-x to main (") for x in shown)
              and got.get("branch") == "main" and got.get("b4_left") == A and "stay" in got and got["stay"] is None
              and stay_of(env) is None,
              "t_stay_cleared: the re-run's B4 leaves the branch, and the stay it kept goes with it (%r)" % got)

        # t_start_json: every call's JSON -- a fresh start, a --rerun, a split start and its resumes, SPECS_PATH unset,
        # an early stop -- holds stay, start_dirty, midrun and started, and no merged_stay; started is the record's
        r, env = world(tmp, "t-start-json")
        r.git("switch", "-q", "-c", "spec/B-1-y")
        r.git("push", "-q", "-u", "origin", "spec/B-1-y")
        session_commit(r, "spec/B-1-y", "PRD-B-1-y")  # an unpushed commit the settle loop pushes: --budget 0 splits
        r.git("switch", "-q", "main")
        chain = follow(run_start(env, "/feedback", "--budget", "0"), env)
        started = (record(env, "/feedback") or {}).get("started")
        calls = chain + [run_start(env, "/feedback"), run_start(env, "/feedback", "--rerun"),
                         run_start(env, "/feedback", specs="")]
        real_disposition = g["_disposition"]
        g["_disposition"] = boom
        try:
            with in_env(env):
                calls.append(start(r.path, "/feedback"))
        finally:
            g["_disposition"] = real_disposition
        check(len(chain) > 1 and all(fields(c) and "merged_stay" not in c for c in calls)
              and all(c.get("started") == started for c in chain) and started
              and calls[-1].get("started") == (record(env, "/feedback") or {}).get("started"),
              "t_start_json: stay, start_dirty, midrun and started on every call (%r)" % [sorted(c) for c in calls])

        # t_snap_rerun_unset: a --rerun with SPECS_PATH unset, run from inside another repository, whose status would
        # list none of the run's paths: the gate did not pass, so the carried snapshot is left as it was
        r, env = world(tmp, "t-snap-rerun-unset")
        LEFT = FEED + "left.md"
        r.write("notes.md", "n\n")
        r.write(LEFT, "t-snap-rerun-unset leftover\n")
        first = run_start(env, "/feedback")
        elsewhere = new_repo(tmp, "t-snap-rerun-unset-elsewhere")
        got = run_start(env, "/feedback", "--rerun", specs="", cwd=elsewhere.path)
        want = {LEFT: blob(r, LEFT)}
        check(first.get("start_dirty") == want and got.get("gate") == "unset" and got.get("start_dirty") == want
              and (record(env, "/feedback") or {}).get("start_dirty") == want,
              "t_snap_rerun_unset: the carried snapshot is not narrowed against another repository (%r)" % got)

        # t_stay_b4_commit_key: only the start's commit key names the branch -- B3, as the run key set's own: no B4
        # switch, and no stay
        r, env = world(tmp, "t-stay-b4-commit-key")
        other_key(r)
        h = head(r)
        got = run_start(env, "/feedback", "--commit-key", "B-2")
        check(got.get("branch") == B and got.get("b4_left") is None and head(r) == h
              and r.git("symbolic-ref", "--short", "HEAD") == B and "stay" in got and got["stay"] is None
              and stay_of(env) is None and got.get("print") == [env_line(r.path)],
              "t_stay_b4_commit_key: the commit key names the branch, so B4 does not leave it (%r)" % got)

        # t_rerun_commit_key: a start whose B4 leaves the branch, then a --rerun whose commit key alone names it -- the
        # run's own, as B3 reads it: the re-run switches back, and B3 keeps it there
        r, env = world(tmp, "t-rerun-commit-key")
        other_key(r)
        first = run_start(env, "/feedback", "--key", "ACME-1")
        got = run_start(env, "/feedback", "--rerun", "--key", "ACME-1", "--commit-key", "B-2")
        check(first.get("branch") == "main" and first.get("b4_left") == B
              and got.get("branch") == B and got.get("b4_left") is None
              and r.git("symbolic-ref", "--short", "HEAD") == B and got.get("print") == [env_line(r.path)]
              and stay_of(env) is None,
              "t_rerun_commit_key: the re-run switches back to the branch its commit key names (%r)" % got)

        # t_snap_bug (in process): a coding error inside the snapshot -- an injected TypeError -- reaches the start's
        # error and pre.stopped, never hidden as a snapshot that could not be taken
        r, env = world(tmp, "t-snap-bug")
        r.write(S_FILE, "t-snap-bug\n")
        real_snapshot = g["snapshot"]

        def snapshot_bug(root):
            raise TypeError("a bug in the snapshot")

        g["snapshot"] = snapshot_bug
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["snapshot"] = real_snapshot
        check(got.get("error") == "TypeError: a bug in the snapshot"
              and (got.get("print") or [""])[-1] == lines.fill("pre.stopped", {"<the error>": got.get("error")}),
              "t_snap_bug: the TypeError surfaces as the start's error (%r)" % got)

    def scenarios_midrun(tmp):
        """specs-repo-git §3.5's run typed mid-run (MIDRUN-B4), §4 step 1's here form, and the record's identity
        (D-park, P19, P35, P36). Each case builds its own world -- a bare origin, a clone with the PRD on main and
        pushed, HEAD's reflog aged so no move of the setup falls after a start -- and runs one session's commands on it.
        Every expected line is rendered from the pins, never by the code under test."""
        state, lines = _flow()
        T = lines.T
        g = globals()
        SPEC = "spec/ACME-1-01-x"
        LB = "prd/B-2-y"
        FUP = "specifications/PRD-ACME-1-x/follow-ups.md"
        FB = "specifications/PRD-ACME-1-x/dev-workflows/feedback/f.md"
        DELIV = "specifications/PRD-B-2-y/specification.md"
        SUBJECT = "%s Add dev-workflows session artifacts (%s)"
        HERE_ALT = lines.placeholder("row.here", "<the next push")
        LANDED = lines.placeholder("app.landed", "<which no key")
        STAY_ALT = lines.placeholder("pre.stay.midrun", "<switched")
        KINDS = lines.placeholder("g1.landing.not_done", "<which no key")
        MID = STAY_KINDS.index("mid-run")
        STAMP_FMT = "%Y-%m-%dT%H:%M:%SZ"

        def case(name, fn):
            try:
                fn()
            except Exception as e:  # one case that crashes must not hide the others
                check(False, "%s crashed: %s: %s" % (name, type(e).__name__, str(e).strip()[:400]))

        def age(r, seconds=3600):
            """Every entry of HEAD's reflog moved <seconds> back: none of the moves made so far falls after a start
            made from here on."""
            path = os.path.join(r.path, ".git", "logs", "HEAD")
            if not os.path.exists(path):
                return
            out = []
            with open(path, encoding="utf-8", errors="surrogateescape") as fh:
                for line in fh.read().splitlines():
                    meta, tab, msg = line.partition("\t")
                    f = meta.split(" ")
                    f[-2] = str(int(f[-2]) - seconds)
                    out.append(" ".join(f) + tab + msg)
            with open(path, "w", encoding="utf-8", errors="surrogateescape") as fh:
                fh.write("\n".join(out) + "\n")

        def mworld(name, follow=None, branch=None):
            """world; <follow> committed on main as follow-ups.md and pushed, where given; then, where <branch> is
            given, that branch cut from main with one commit of its own, pushed with -u, HEAD left on it; the reflog
            aged."""
            r, env = world(tmp, name)
            if follow is not None:
                r.write(FUP, follow)
                r.commit_all("ACME-1 Add the follow-ups")
                r.git("push", "-q", "origin", "main")
            if branch is not None:
                r.git("switch", "-q", "-c", branch)
                r.write("specifications/%s.md" % branch.replace("/", "-"), "work\n")
                r.commit_all("Work on " + branch)
                r.git("push", "-q", "-u", "origin", branch)
            age(r)
            return r, env

        def start_(env, command, *args, specs=None):
            return cli("--specs", env["SPECS_PATH"] if specs is None else specs, "start", "--command", command, *args,
                       env=env)

        def declined_(env, command, *args):
            return cli("declined", "--command", command, *args, env=env)

        def rev(r, ref):
            return r.git("rev-parse", "--verify", "-q", ref, check=False) or None

        def on(r):
            return r.git("symbolic-ref", "--short", "-q", "HEAD", check=False)

        def read(r, path):
            full = os.path.join(r.path, path)
            if not os.path.isfile(full):
                return None
            with open(full, encoding="utf-8", newline="") as fh:
                return fh.read()

        def append(r, path, text):
            r.write(path, (read(r, path) or "") + text)

        def gone(r, path):
            return not os.path.lexists(os.path.join(r.path, path))

        def changed(r, ref):
            return sorted(x for x in r.git("diff-tree", "--no-commit-id", "--name-only", "-r", ref).split("\n") if x)

        def show(r, ref, path):
            return r.git("show", "%s:%s" % (ref, path), check=False)

        def cached(r):
            return r.git("diff", "--cached", "--name-only")

        def added(r, path):
            """The lines `git diff HEAD -- <path>` adds."""
            return [x[1:] for x in r.git("diff", "HEAD", "--", path).split("\n") if x.startswith("+") and not x.startswith("+++")]

        def file_of(env, command, name=None):
            with in_env(env):
                main = state.path(env["CLAUDE_CODE_SESSION_ID"], command)
            return main if name is None else os.path.join(os.path.dirname(main), name)

        def raw(env, command, name=None):
            path = file_of(env, command, name)
            return open(path, "rb").read() if os.path.exists(path) else None

        def stamp_of(started):
            return started.replace("-", "").replace(":", "")

        def backdate(env, command, seconds=120):
            """The record of <command>'s run started <seconds> earlier, as a start that ran then would have saved it:
            two runs of one command then hold two started stamps. Its new started."""
            with in_env(env):
                session = env["CLAUDE_CODE_SESSION_ID"]
                rec = state.load(session, command)
                rec["started"] = time.strftime(STAMP_FMT, time.gmtime(time.time() - seconds))
                state.save(session, command, rec)
            return rec["started"]

        def drop(env, command):
            """The record of <command>'s run removed, as prune or a /clear would leave an abandoned run's."""
            with in_env(env):
                state.remove(env["CLAUDE_CODE_SESSION_ID"], command)

        def pushed_default(sha7, specs, n=1):
            return lines.fill("row.pushed-default", {"<sha7>": sha7, "<N>": n, "<default>": "main", "<SPECS_PATH>": specs})

        def here_row(sha7, n, branch, command="/specify", alt=0, keys=None):
            """The here row, <keys> the open run's key set as the clause naming its ends names it (4(c)), None for
            none."""
            return lines.fill("row.here", {"<sha7>": sha7, "<N>": n, "<branch>": branch, "<command>": command,
                                           "<keys>": keys, HERE_ALT: alt})

        def landed_app(branch, command="/specify"):
            return lines.fill("app.landed", {"<branch>": branch, "<default>": "main", "<command>": command, LANDED: MID})

        def kept_row(branch, clause, command="/specify", keys=None):
            return lines.fill("row.midrun-kept", {"<command>": command, "<keys>": keys, "<branch>": branch,
                                                  "<reason clause>": clause})

        def stay_line(branch, command="/specify", merged=False):
            return lines.fill("pre.stay.midrun", {"<branch>": branch, "<default>": "main", "<command>": command,
                                                  STAY_ALT: 0 if merged else 1})

        def parts(block, **texts):
            """<block> with each part a keyword names -- not_done, fix, if_ignored -- replaced by its text on one line
            after its label's padding, the part's continuation lines dropped; an empty text leaves the label alone."""
            labels = {"not_done": "Not done:", "fix": "Fix:", "if_ignored": "If ignored:"}
            rows = block.split("\n")
            for key, text in texts.items():
                label = labels[key]
                i = next(k for k, row in enumerate(rows) if row.startswith(label))
                j = i + 1
                while j < len(rows) and rows[j].startswith(" "):
                    j += 1
                pad = label + " " * (len(re.match(re.escape(label) + " *", rows[i]).group(0)) - len(label))
                rows = rows[:i] + [(pad + text).rstrip()] + rows[j:]
            return "\n".join(rows)

        def g1_of(r, paths):
            return lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": len(paths),
                                     "<path list>": [", ".join(paths), " ".join(shlex.quote(p) for p in paths)]})

        def g1_midrun(r, paths, not_done=None, command="/specify", keys=None):
            """G1's mid-run form (§5): <not_done> in place of the plain Not done where given, an empty Fix, and
            g1.midrun.if_ignored, <keys> the open run's key set (4(c))."""
            texts = {"fix": "", "if_ignored": lines.fill("g1.midrun.if_ignored", {"<command>": command,
                                                                                   "<keys>": keys})}
            if not_done is not None:
                texts["not_done"] = not_done
            return parts(g1_of(r, paths), **texts)

        def landing_nd(branch, unlanded=False, command="/specify", whole=False):
            """The landing Not done: the start's, or, as the end repeats it, <whole> (landed) or <unlanded> (M4)."""
            tid = ("g1.landing.not_done.unlanded" if unlanded else "g1.landing.not_done.landed" if whole
                   else "g1.landing.not_done")
            return lines.fill(tid, {"<default>": "main", "<branch>": branch, "<command>": command, KINDS: MID})

        def g2_midrun(r, branch, command="/specify", keys=None):
            plain = lines.fill("g2", {"<SPECS_PATH>": r.path, "<branch>": branch, "<default>": "main"})
            return parts(plain, fix="", if_ignored=lines.fill("g2.midrun.if_ignored",
                                                              {"<command>": command, "<keys>": keys,
                                                               "<branch>": branch}))

        def no_git(block):
            return "git -C" not in block and "switch" not in block.split("Fix:")[1]

        def held(r):
            return held_entries(r.path)

        def opened_on(env, branch, command="/specify", **fields):
            """A record of <command>'s run open on <branch>, as its start saves one (seed)."""
            seed(env, command, branch=branch, **fields)
            return record(env, command)

        # t_midrun_keyless, t_midrun_keyed_other (MIDRUN-B4, Review Focus 1)
        def t_midrun_keyless(name, cmd, args):
            r, env = mworld(name, branch=SPEC)
            s = start_(env, "/specify", "--key", "ACME-1-01", "--key", "ACME-1")
            r.write(FUP, "- [ ] specify's\n")  # in progress, new on the branch, absent from main
            spec_tip, main_old = rev(r, SPEC), rev(r, "main")
            f = start_(env, cmd, *args)
            check(s.get("branch") == SPEC and s.get("midrun") is None
                  and f.get("print") == [env_line(r.path), stay_line(SPEC)] and on(r) == SPEC and rev(r, SPEC) == spec_tip
                  and f.get("midrun") == {"command": "/specify", "started": s.get("started"), "branch": SPEC,
                                         "keys": ["ACME-1-01", "ACME-1"]}
                  and f.get("stay") == {"branch": SPEC, "kind": "mid-run", "reason": "mid-run", "merged": False,
                                        "command": "/specify"},
                  "%s: no commit on the branch, HEAD unmoved, pre.stay.midrun naming /specify, a mid-run stay (%r)"
                  % (name, f))
            r.write(FB, "## 2026-11-10 — %s — note\n\nmine\n" % cmd)
            append(r, FUP, "- [ ] mine\n")
            e = run_end(env, cmd)
            m = rev(r, "main")
            check(e.get("row") == "pushed-default" and e.get("print") == [pushed_default(m[:7], r.path, 2) + landed_app(SPEC)]
                  and r.git("rev-parse", m + "^") == main_old and changed(r, m) == sorted([FB, FUP])
                  and show(r, m, FUP) == "- [ ] mine" and read(r, FUP) == "- [ ] specify's\n" and gone(r, FB)
                  and rev(r, SPEC) == spec_tip and on(r) == SPEC and on_origin(r) == m,
                  "%s: main holds the run's file and its line alone, app.landed's mid-run alternative; the working copy "
                  "is /specify's again (%r)" % (name, e))
            e = run_end(env, "/specify")
            h = rev(r, SPEC)
            check(e.get("row") == "pushed-plugin" and r.git("rev-parse", h + "^") == spec_tip and changed(r, h) == [FUP]
                  and show(r, h, FUP) == "- [ ] specify's" and on_origin(r, SPEC) == h,
                  "%s: /specify's end commits its line on the branch, pushed (%r)" % (name, e))

        case("t_midrun_keyless", lambda: t_midrun_keyless("t-midrun-keyless", "/feedback", []))
        case("t_midrun_keyed_other", lambda: t_midrun_keyless("t-midrun-keyed-other", "/create-ard", ["--key", "ACME-2"]))

        # t_midrun_default (P2, P20): the here form on main, unpushed; then the open run's end pushes both
        def t_midrun_default():
            r, env = mworld("t-midrun-default", follow="- [ ] a\n")
            up = on_origin(r)
            start_(env, "/specify", "--key", "ACME-1")
            append(r, FUP, "- [ ] specify's\n")
            f = start_(env, "/feedback")
            old = head(r)
            check(f.get("print") == [env_line(r.path)] and (f.get("midrun") or {}).get("branch") == "main"
                  and f.get("stay") is None and head(r) == old,
                  "t_midrun_default: typed mid-run on main, nothing printed, nothing kept (%r)" % f)
            append(r, FUP, "- [ ] feedback's\n")
            r.write(FB, "fb\n")
            e = run_end(env, "/feedback")
            h = head(r)
            check(e.get("row") == "here" and e.get("print") == [here_row(h[:7], 2, "main", keys="ACME-1")] and e.get("pushed") is False
                  and on_origin(r) == up and r.git("rev-parse", "HEAD^") == old and changed(r, h) == sorted([FB, FUP])
                  and show(r, h, FUP) == "- [ ] a\n- [ ] feedback's" and cached(r) == ""
                  and added(r, FUP) == ["- [ ] specify's"] and record(env, "/feedback") is None,
                  "t_midrun_default: one commit on main holding /feedback's line and file alone, unpushed, the index "
                  "in step, /specify's line still dirty (%r)" % e)
            e = run_end(env, "/specify")
            check(e.get("row") == "pushed-default" and on_origin(r) == head(r) and r.git("rev-parse", "HEAD^") == h
                  and read(r, FUP) == show(r, "HEAD", FUP) + "\n" and r.git("status", "--porcelain") == "",
                  "t_midrun_default: /specify's end commits its line and pushes both (%r)" % e)

        case("t_midrun_default", t_midrun_default)

        # t_midrun_b3: the here form on a branch a key of the typed run names (B3): unpushed, the open run's file
        # intact; the open run's end pushes both
        def t_midrun_b3():
            r, env = mworld("t-midrun-b3", branch=SPEC)
            start_(env, "/specify", "--key", "ACME-1-01")
            r.write(FUP, "- [ ] specify's\n")
            up, old = on_origin(r, SPEC), head(r)
            f = start_(env, "/feedback", "--key", "ACME-1")
            r.write(FB, "fb\n")
            e = run_end(env, "/feedback")
            h = head(r)
            check(f.get("print") == [env_line(r.path)] and f.get("stay") is None and e.get("row") == "here"
                  and e.get("print") == [here_row(h[:7], 1, SPEC, keys="ACME-1-01")] and on_origin(r, SPEC) == up
                  and r.git("rev-parse", "HEAD^") == old and changed(r, h) == [FB] and read(r, FUP) == "- [ ] specify's\n"
                  and cached(r) == "",
                  "t_midrun_b3: the here form on the keyed branch, its first alternative, unpushed, /specify's file "
                  "intact (%r)" % e)
            e = run_end(env, "/specify")
            check(e.get("row") == "pushed-plugin" and on_origin(r, SPEC) == head(r) and r.git("rev-parse", "HEAD^") == h,
                  "t_midrun_b3: /specify's end pushes both (%r)" % e)

        case("t_midrun_b3", t_midrun_b3)

        # t_midrun_g2 (F5): on feature/x, G2's block in its mid-run form at the start and as end repeats it; the here
        # form's row in its second alternative
        def t_midrun_g2():
            r, env = mworld("t-midrun-g2")
            r.git("switch", "-q", "-c", "feature/x")
            age(r)
            start_(env, "/specify")
            f = start_(env, "/feedback")
            block = g2_midrun(r, "feature/x")
            r.write(FB, "fb\n")
            e = run_end(env, "/feedback")
            h = head(r)
            check(f.get("print") == [env_line(r.path), block] and no_git(block) and f.get("guard") == "G2"
                  and e.get("row") == "here" and e.get("print") == [here_row(h[:7], 1, "feature/x", alt=1), block],
                  "t_midrun_g2: G2's mid-run form, its Fix empty, at the start and at the end; the here row's second "
                  "alternative (%r, %r)" % (f, e))

        case("t_midrun_g2", t_midrun_g2)

        # t_midrun_catch_up (P20): an open run on main behind origin/main -- the typed run's start makes no pull and
        # no retry of HEAD's push, its end no pull; the here form commits on the commit the open run stood on
        def t_midrun_catch_up():
            r, env = mworld("t-midrun-catch-up")
            start_(env, "/specify")
            old = head(r)
            o = clone(r, "t-midrun-catch-up-other")
            o.write("specifications/PRD-ACME-1-x/notes-other.md", "o\n")
            o.commit_all("ACME-1 Other work")
            o.git("push", "-q", "origin", "main")
            f = start_(env, "/feedback")
            r.write(FB, "fb\n")
            e = run_end(env, "/feedback")
            check(f.get("print") == [env_line(r.path)] and e.get("row") == "here"
                  and r.git("rev-parse", "HEAD^") == old and gone(r, "specifications/PRD-ACME-1-x/notes-other.md"),
                  "t_midrun_catch_up: no pull at the start or the end (%r, %r)" % (f, e))
            r, env = mworld("t-midrun-push-retry")
            start_(env, "/specify")
            r.write(FB, "left\n")
            r.commit_all(SUBJECT % ("NOISSUE", "/feedback"))  # a session-file commit left unpushed on main
            up = on_origin(r)
            f = start_(env, "/feedback")
            check(on_origin(r) == up and f.get("print") == [env_line(r.path)],
                  "t_midrun_catch_up: no retry of HEAD's push under the open run (%r)" % f)

        case("t_midrun_catch_up", t_midrun_catch_up)

        # t_midrun_g1 (N2): the open run's deliverable dirty on prd/B-2-y, which no key of the typed run names -- G1's
        # mid-run form with the landing Not done, its Fix empty, nothing to run; the end lands. On main, no stay: the
        # plain Not done
        def t_midrun_g1():
            r, env = mworld("t-midrun-g1", branch=LB)
            start_(env, "/specify", "--key", "B-2")
            r.write(DELIV, "draft\n")
            f = start_(env, "/feedback")
            block = g1_midrun(r, [DELIV], landing_nd(LB), keys="B-2")
            r.write(FB, "fb\n")
            e = run_end(env, "/feedback")
            m = rev(r, "main")
            check(f.get("print") == [env_line(r.path), block] and no_git(block)
                  and (f.get("stay") or {}).get("kind") == "mid-run" and e.get("row") == "pushed-default"
                  and e.get("print") == [pushed_default(m[:7], r.path) + landed_app(LB),
                                         g1_midrun(r, [DELIV], landing_nd(LB, whole=True), keys="B-2")] and changed(r, m) == [FB],
                  "t_midrun_g1: G1's mid-run landing form at the start and the end, the end landed, its Not done the "
                  "landed one (%r, %r)" % (f, e))
            r, env = mworld("t-midrun-g1-main")
            start_(env, "/specify")
            r.write(DELIV, "draft\n")
            f = start_(env, "/feedback")
            block = g1_midrun(r, [DELIV])
            r.write(FB, "fb\n")
            e = run_end(env, "/feedback")
            check(f.get("print") == [env_line(r.path), block] and no_git(block) and f.get("stay") is None
                  and e.get("print") == [here_row(head(r)[:7], 1, "main"), block],
                  "t_midrun_g1: on main, the plain Not done, the empty Fix, the mid-run If ignored (%r, %r)" % (f, e))

        case("t_midrun_g1", t_midrun_g1)

        # t_stay_merged_midrun (N2): an open run on a merged branch -- a mid-run stay with its merged flag set, G1's
        # Fix empty and its If ignored the mid-run one, no switch
        def t_stay_merged_midrun():
            r, env = mworld("t-stay-merged-midrun")
            r.git("switch", "-q", "-c", "prd/C-3-z")
            r.write("specifications/PRD-C-3-z/prd.md", "c\n")
            r.commit_all("C-3 Add the PRD")
            r.git("push", "-q", "-u", "origin", "prd/C-3-z")
            o = clone(r, "t-stay-merged-midrun-other")
            o.git("merge", "-q", "--ff-only", "origin/prd/C-3-z")
            o.git("push", "-q", "origin", "main")
            age(r)
            r.write("notes.md", "n\n")
            start_(env, "/specify")
            f = start_(env, "/feedback")
            block = g1_midrun(r, ["notes.md"], landing_nd("prd/C-3-z"))
            check(f.get("stay") == {"branch": "prd/C-3-z", "kind": "mid-run", "reason": "g1", "merged": True,
                                    "command": "/specify"}
                  and f.get("print") == [env_line(r.path), block] and no_git(block) and on(r) == "prd/C-3-z",
                  "t_stay_merged_midrun: kind mid-run, merged, the mid-run form whatever the flag (%r)" % f)

        case("t_stay_merged_midrun", t_stay_merged_midrun)

        # The here form cut off (M1): its journals -- the held record's entry and the state record's end_commit.here --
        # are written before HEAD's branch moves, so end --resume, or the next preflight's held stage, finishes it.
        class Killed(BaseException):
            """A kill: no handler of an outcome takes it, so the call ends where it stands, as a SIGKILL would."""

        def midrun_main(name):
            """/specify open on main with a follow-ups line in progress; /feedback typed mid-run, which writes its own
            file and line."""
            r, env = mworld(name, follow="- [ ] a\n")
            start_(env, "/specify", "--key", "ACME-1")
            append(r, FUP, "- [ ] specify's\n")
            start_(env, "/feedback")
            append(r, FUP, "- [ ] feedback's\n")
            r.write(FB, "fb\n")
            return r, env

        def end_in_process(env, *args, **kw):
            with in_env(env):
                return end(env["SPECS_PATH"], "/feedback", *args, **kw)

        def git_hook(after=None, before=None):
            """sb.git wrapped: <before>(args) runs before, and <after>(args) after, each call whose args open
            update-ref -m "specs-git: landed ..." -- the here form's move of HEAD's branch."""
            real = sb.git

            def wrapped(root, *args, **kw):
                move = args[:2] == ("update-ref", "-m") and str(args[2]).startswith("specs-git: landed")
                if move and before:
                    before(args)
                got = real(root, *args, **kw)
                if move and after:
                    after(args)
                return got
            return real, wrapped

        def e_midrun_here_kill():
            r, env = midrun_main("e-midrun-here-kill")
            old = head(r)
            real = g["_restore_index"]

            def killed(root, entry):
                raise RuntimeError("killed in the restore step")

            g["_restore_index"] = killed
            try:
                got = end_in_process(env)
            finally:
                g["_restore_index"] = real
            rec = record(env, "/feedback") or {}
            journal = (rec.get("end_commit") or {}).get("here") or {}
            check("killed in the restore step" in (got.get("error") or "") and head(r) != old
                  and journal.get("tip") == head(r) and journal.get("old") == old
                  and sorted(cached(r).split()) == sorted([FB, FUP])
                  and [e.get("here") and e.get("tip") for e in held(r)] == [head(r)],
                  "e_midrun_here_kill: error set, the index showing the reversal, end_commit.here and the held record "
                  "holding the journal (%r, %r)" % (got, rec.get("end_commit")))
            e = run_end(env, "/feedback", "--resume")
            check(e.get("row") == "here" and e.get("print") == [here_row(head(r)[:7], 2, "main", keys="ACME-1")] and cached(r) == ""
                  and held(r) == [] and record(env, "/feedback") is None and r.git("rev-parse", "HEAD^") == old,
                  "e_midrun_here_kill: end --resume restores the index, the here row, the journal gone (%r)" % e)

        def e_midrun_here_kill_moved():
            """A kill just after the move: the journals were written before it, so the resume finds them."""
            r, env = midrun_main("e-midrun-here-kill-moved")
            old = head(r)

            def kill(args):
                raise Killed()

            real, wrapped = git_hook(after=kill)
            sb.git = wrapped
            try:
                try:
                    end_in_process(env)
                except Killed:
                    pass
            finally:
                sb.git = real
            moved = head(r)
            e = run_end(env, "/feedback", "--resume")
            check(moved != old and e.get("row") == "here" and e.get("print") == [here_row(moved[:7], 2, "main", keys="ACME-1")]
                  and cached(r) == "" and held(r) == [] and head(r) == moved,
                  "e_midrun_here_kill_moved: a kill right after the move is finished by end --resume (%r)" % e)

        def e_midrun_here_lock():
            r, env = midrun_main("e-midrun-here-lock")
            lock = os.path.join(r.path, ".git", "index.lock")

            def appear(args):
                open(lock, "w").close()

            real, wrapped = git_hook(after=appear)
            sb.git = wrapped
            try:
                got = end_in_process(env)
            finally:
                sb.git = real
            journal = ((record(env, "/feedback") or {}).get("end_commit") or {}).get("here") or {}
            check(got.get("error") and journal.get("tip") == head(r) and sorted(cached(r).split()) == sorted([FB, FUP]),
                  "e_midrun_here_lock: an index.lock between the two steps stops it, the journals kept (%r)" % got)
            os.remove(lock)
            e = run_end(env, "/feedback", "--resume")
            check(e.get("row") == "here" and cached(r) == "" and held(r) == [],
                  "e_midrun_here_lock: finished by end --resume once the lock is gone (%r)" % e)

        def e_midrun_here_no_resume():
            r, env = midrun_main("e-midrun-here-no-resume")
            real = g["_restore_index"]
            g["_restore_index"] = lambda root, entry: (_ for _ in ()).throw(RuntimeError("killed"))
            try:
                end_in_process(env)
            finally:
                g["_restore_index"] = real
            tip = head(r)
            env2 = dict(env, CLAUDE_CODE_SESSION_ID="e-midrun-here-no-resume-2")
            got = start_(env2, "/create-ard")
            want = lines.fill("pre.here.finished", {"<branch>": "main", "<sha7>": tip[:7], "<N>": 2})
            check(want in (got.get("print") or []) and cached(r) == "" and held(r) == []
                  and tip in r.git("rev-list", "HEAD").split(),
                  "e_midrun_here_no_resume: a new session's start finishes the restore (%r)" % got)

        case("e_midrun_here_kill", e_midrun_here_kill)
        case("e_midrun_here_kill_moved", e_midrun_here_kill_moved)
        case("e_midrun_here_lock", e_midrun_here_lock)
        case("e_midrun_here_no_resume", e_midrun_here_no_resume)

        def journal_cut(name):
            """midrun_main, then /feedback's end cut off after its journals and before the move."""
            r, env = midrun_main(name)

            def kill(args):
                raise Killed()

            real, wrapped = git_hook(before=kill)
            sb.git = wrapped
            try:
                try:
                    end_in_process(env)
                except Killed:
                    pass
            finally:
                sb.git = real
            return r, env

        def e_midrun_here_resume_elsewhere():
            """end --resume with HEAD on another branch than the journal's drops the journal entry itself, then goes on
            from step 1: HEAD back on the journal's branch, a start commits nothing again there."""
            r, env = journal_cut("e-midrun-resume-elsewhere")
            old = head(r)
            check(len(held(r)) == 1 and held(r)[0].get("here"), "e_midrun_here_resume_elsewhere: the journal stands")
            r.git("switch", "-q", "-c", "other")
            e = run_end(env, "/feedback", "--resume")
            r.git("switch", "-q", "main")
            env2 = dict(env, CLAUDE_CODE_SESSION_ID="e-midrun-resume-elsewhere-2")
            s = start_(env2, "/create-ard")
            check(e.get("branch") == "other" and held(r) == [] and head(r) == old
                  and not any("finished the commit" in x for x in s.get("print") or []),
                  "e_midrun_here_resume_elsewhere: the journal dropped, no second commit on main (%r, %r)" % (e, s))

        def e_midrun_here_unfinished():
            """end --resume with HEAD on the journal's branch, which moved on without the commit: the open run still
            standing, the mid-run row with the unfinished clause; where it no longer stands, from step 1."""
            other = "specifications/PRD-ACME-1-x/dev-workflows/feedback/other.md"
            r, env = journal_cut("e-midrun-unfinished")
            r.write(other, "o\n")  # main moves on: another session's commit of its own file
            r.git("add", other)
            r.git("commit", "-q", "-m", SUBJECT % ("NOISSUE", "/other"))
            moved = head(r)
            e = run_end(env, "/feedback", "--resume")
            check(e.get("row") == "midrun-kept" and e.get("print") == [kept_row("main", lines.fill(
                      "reason.land.unfinished", {"<branch>": "main"}), keys="ACME-1")] and head(r) == moved and held(r) == []
                  and record(env, "/feedback") is None,
                  "e_midrun_here_unfinished: the mid-run row with reason.land.unfinished, nothing committed (%r)" % e)
            r, env = journal_cut("e-midrun-unfinished-ended")
            r.write(other, "o\n")
            r.git("add", other)
            r.git("commit", "-q", "-m", SUBJECT % ("NOISSUE", "/other"))
            moved = head(r)
            drop(env, "/specify")
            e = run_end(env, "/feedback", "--resume")
            check(e.get("row") == "pushed-default" and r.git("rev-parse", "HEAD^") == moved and on_origin(r) == head(r)
                  and changed(r, "HEAD") == sorted([FB, FUP]) and "still open" not in (e.get("line") or ""),
                  "e_midrun_here_unfinished: the open run ended, the end goes on from step 1 (%r)" % e)

        def t_midrun_here_journal_ancestor():
            """N4: the restore cut off; the open run's end then commits on top; end --resume finds the journalled tip
            an ancestor of HEAD's branch, restores what is still the old tip's, and commits nothing again."""
            r, env = midrun_main("t-midrun-here-ancestor")
            real = g["_restore_index"]
            g["_restore_index"] = lambda root, entry: (_ for _ in ()).throw(RuntimeError("killed"))
            try:
                end_in_process(env)
            finally:
                g["_restore_index"] = real
            tip = head(r)
            run_end(env, "/specify")
            above = head(r)
            e = run_end(env, "/feedback", "--resume")
            check(above != tip and tip in r.git("rev-list", above).split()
                  and head(r) == above and held(r) == [] and cached(r) == "" and record(env, "/feedback") is None
                  and e.get("error") is None,
                  "t_midrun_here_journal_ancestor: the journal finished on an ancestor, nothing committed again (%r)" % e)

        case("e_midrun_here_resume_elsewhere", e_midrun_here_resume_elsewhere)
        case("e_midrun_here_unfinished", e_midrun_here_unfinished)
        case("t_midrun_here_journal_ancestor", t_midrun_here_journal_ancestor)

        # e_no_start_midrun (N3, Review Focus 4): an end with no start of its own while /specify is open on its branch
        # writes nothing -- kinds missing, ignored and declined-only
        def e_no_start_midrun():
            r, env = mworld("e-no-start-midrun", branch=SPEC)
            start_(env, "/specify", "--key", "ACME-1-01")
            r.write(FUP, "- [ ] specify's\n")
            spec_raw, spec_tip, main_tip = raw(env, "/specify"), rev(r, SPEC), rev(r, "main")
            want = kept_row(SPEC, T["reason.land.no-preflight"], keys="ACME-1-01")
            got = run_end(env, "/feedback", "--no-preflight")
            check(got.get("record") == "missing" and got.get("row") == "midrun-kept" and got.get("print") == [want]
                  and rev(r, SPEC) == spec_tip and rev(r, "main") == main_tip and raw(env, "/specify") == spec_raw
                  and raw(env, "/feedback") is None and read(r, FUP) == "- [ ] specify's\n",
                  "e_no_start_midrun: kind missing -- the mid-run row with no-preflight, nothing written (%r)" % got)
            declined_(env, "/feedback", "--path", "x.md")
            fb_raw = raw(env, "/feedback")
            got = run_end(env, "/feedback", "--no-preflight")
            got2 = run_end(env, "/feedback")
            check(got.get("record") == "ignored" and got.get("print") == [want] and got2.get("record") == "declined-only"
                  and got2.get("print") == [want] and raw(env, "/feedback") == fb_raw and rev(r, SPEC) == spec_tip
                  and raw(env, "/specify") == spec_raw,
                  "e_no_start_midrun: kinds ignored and declined-only alike, nothing removed (%r, %r)" % (got, got2))

        def e_no_preflight_open():
            """P5: /specify's own end with --no-preflight while its start's record is open: nothing committed, the
            record untouched."""
            r, env = mworld("e-no-preflight-open")
            start_(env, "/specify")
            r.write(FB, "fb\n")
            spec_raw, old = raw(env, "/specify"), head(r)
            got = run_end(env, "/specify", "--no-preflight")
            check(got.get("row") == "midrun-kept" and got.get("print") == [kept_row("main", T["reason.land.no-preflight"])]
                  and head(r) == old and raw(env, "/specify") == spec_raw,
                  "e_no_preflight_open: the mid-run row, nothing committed, the record untouched (%r)" % got)

        case("e_no_start_midrun", e_no_start_midrun)
        case("e_no_preflight_open", e_no_preflight_open)

        # t_midrun_not_open: each condition of the open-run test broken in turn, and the typed run switches as before
        # (B4); then a record each condition passes, the run typed mid-run
        def t_midrun_not_open():
            r, env = mworld("t-midrun-not-open", branch=LB)
            eight = time.strftime(STAMP_FMT, time.gmtime(time.time() - 8 * 86400))
            for label, fields in (("open", {}), ("end_commit", {"end_commit": {"branch": LB}}), ("stage end", {"stage": "end"}),
                                  ("declined only", {"started_by_script": False}), ("misrooted", {"specs_git": "misrooted"}),
                                  ("another top", {"top": "/elsewhere"}), ("protects false", {"protects": False}),
                                  ("8 days", {"started": eight}),
                                  ("another branch", {"branch": "prd/C-3-z", "keys": ["C-3"]})):
                r.git("switch", "-q", LB)
                started = fields.pop("started", None)
                age(r, 9 * 86400 if started else 3600)  # no move of the earlier cases inside an 8-day-old run's window
                drop(env, "/feedback")
                seed(env, "/specify", **dict({"branch": LB, "keys": ["B-2"]}, **fields))
                if started:
                    with in_env(env):
                        rec = state.load(env["CLAUDE_CODE_SESSION_ID"], "/specify")
                        rec["started"] = started
                        state.save(env["CLAUDE_CODE_SESSION_ID"], "/specify", rec)
                got = start_(env, "/feedback")
                if label == "open":
                    check(got.get("midrun") and on(r) == LB and stay_line(LB) in (got.get("print") or []),
                          "t_midrun_not_open: the open record holds the run on its branch (%r)" % got)
                else:
                    check(got.get("midrun") is None and on(r) == "main" and got.get("b4_left") == LB,
                          "t_midrun_not_open: %s -- not open, B4 switches as before (%r)" % (label, got))

        def t_midrun_keyset():
            """The open record's branch is main, its keys naming HEAD's: open."""
            r, env = mworld("t-midrun-keyset", branch=LB)
            seed(env, "/specify", branch="main", keys=["B-2"])
            got = start_(env, "/feedback")
            check(got.get("midrun") and on(r) == LB and stay_line(LB) in (got.get("print") or []),
                  "t_midrun_keyset: a key of the open run names HEAD's branch (%r)" % got)

        case("t_midrun_not_open", t_midrun_not_open)
        case("t_midrun_keyset", t_midrun_keyset)

        # HEAD's reflog (§3.5): a leave of HEAD's branch since the open run's start ends it, even where HEAD returned;
        # one before it, a move to HEAD's branch itself, and the open run's own handoff onto its branch do not; with
        # no reflog, the protection holds while HEAD stands on the branch
        def reflog_case(name, between, before=None, keys=("B-2",), on_branch=LB, open_branch=None):
            r, env = mworld(name, branch=LB)
            if before:
                before(r)
                age(r)
            seed(env, "/specify", branch=open_branch or on_branch, keys=list(keys))
            between(r)
            return r, start_(env, "/feedback")

        def away_and_back(r):
            r.git("switch", "-q", "main")
            r.git("switch", "-q", LB)

        def t_midrun_reflog():
            r, got = reflog_case("t-midrun-left-returned", away_and_back)
            check(got.get("midrun") is None and on(r) == "main",
                  "t_midrun_left_returned: away and back since the start -- not mid-run (%r)" % got)
            r, got = reflog_case("t-midrun-left-before", lambda r: None, before=away_and_back)
            check(got.get("midrun") and on(r) == LB,
                  "t_midrun_left_before: away and back before the start -- still mid-run (%r)" % got)
            r, got = reflog_case("t-midrun-noop-move", lambda r: r.git("switch", "-q", LB))
            check(got.get("midrun") and on(r) == LB, "t_midrun_noop_move: a move to the branch itself (%r)" % got)

            def gone_reflog(r):
                away_and_back(r)
                os.remove(os.path.join(r.path, ".git", "logs", "HEAD"))

            r, got = reflog_case("t-midrun-reflog-none", gone_reflog)
            check(got.get("midrun") and on(r) == LB,
                  "t_midrun_reflog_none: no reflog -- mid-run while HEAD stands on the branch (%r)" % got)
            def handoff(r):  # the open run's own handoff onto its branch, which then carries a commit of its own
                r.git("switch", "-q", "-c", "prd/B-2-z")
                r.write("specifications/PRD-B-2-y/prd-z.md", "z\n")
                r.commit_all("B-2 the handoff's deliverable")

            r, got = reflog_case("t-midrun-handoff-open", handoff, before=lambda r: r.git("switch", "-q", "main"),
                                 on_branch="main")
            check(got.get("midrun") and on(r) == "prd/B-2-z" and stay_line("prd/B-2-z") in (got.get("print") or []),
                  "t_midrun_handoff_open: the open run's handoff onto its own branch -- still mid-run (%r)" % got)

        case("t_midrun_reflog", t_midrun_reflog)

        # e_midrun_open_ended (P36, F4): the open run stops standing without committing the typed run's file -- HEAD
        # leaves main and returns, or its record removed as an abandoned run's -- and the typed run's end commits its
        # own change by the here form and pushes it, with no mid-run wording
        def e_midrun_open_ended():
            for name, ends in (("e-midrun-ended-left", lambda r, env: (r.git("switch", "-q", "-c", "tmp"),
                                                                       r.git("switch", "-q", "main"))),
                               ("e-midrun-ended-dropped", lambda r, env: drop(env, "/specify"))):
                r, env = midrun_main(name)
                old = head(r)
                ends(r, env)
                e = run_end(env, "/feedback")
                h = head(r)
                check(e.get("row") == "pushed-default" and e.get("print") == [pushed_default(h[:7], r.path, 2)]
                      and on_origin(r) == h and r.git("rev-parse", "HEAD^") == old and changed(r, h) == sorted([FB, FUP])
                      and show(r, h, FUP) == "- [ ] a\n- [ ] feedback's" and added(r, FUP) == ["- [ ] specify's"],
                      "%s: only /feedback's change, pushed, no mid-run wording (%r)" % (name, e))

        case("e_midrun_open_ended", e_midrun_open_ended)

        # t_midrun_ends_*: the protection's ends (S3) -- HEAD on another branch, /clear's new session id, the open
        # run's own end; its age is t_midrun_not_open's
        def t_midrun_ends():
            r, env = mworld("t-midrun-ends-head-left", branch=LB)
            start_(env, "/specify", "--key", "B-2")
            r.git("switch", "-q", "main")
            got = start_(env, "/feedback")
            check(got.get("midrun") is None, "t_midrun_ends_head_left: HEAD on another branch (%r)" % got)
            r, env = mworld("t-midrun-ends-clear", branch=LB)
            start_(env, "/specify", "--key", "B-2")
            got = start_(dict(env, CLAUDE_CODE_SESSION_ID="t-midrun-ends-clear-2"), "/feedback")
            check(got.get("midrun") is None and on(r) == "main", "t_midrun_ends_clear: a new session id (%r)" % got)
            r, env = mworld("t-midrun-ends-end", branch=LB)
            start_(env, "/specify", "--key", "B-2")
            run_end(env, "/specify")
            got = start_(env, "/feedback")
            check(got.get("midrun") is None and on(r) == "main", "t_midrun_ends_end: the open run's end (%r)" % got)

        case("t_midrun_ends", t_midrun_ends)

        # N17, conditional (§4 step 1 (1)): a run typed mid-run whose start took no snapshot -- status could not run,
        # or the start was cut off before taking one -- commits nothing while the open run stands, by the landing or
        # the here form alike; once it no longer stands, the change is taken against HEAD
        def no_snapshot(name, cause, where):
            """/specify open -- on LB (a mid-run stay for the typed run) or on main (the here form) -- with a follow-ups
            line in progress; /feedback typed mid-run with no snapshot, for <cause>; it writes its own file."""
            if where == "lb":
                r, env = mworld(name, branch=LB)
                start_(env, "/specify", "--key", "B-2")
            else:
                r, env = mworld(name, follow="- [ ] a\n")
                start_(env, "/specify", "--key", "ACME-1")
            append(r, FUP, "- [ ] specify's\n")
            with in_env(env):
                if cause == "status":
                    real = g["status"]

                    def broken(root):
                        raise NotRun("git status: fatal: index file corrupt")

                    g["status"] = broken
                    try:
                        first = start(r.path, "/feedback")
                    finally:
                        g["status"] = real
                else:
                    real = g["_take_snapshot"]

                    def cut(run):
                        raise Killed()

                    g["_take_snapshot"] = cut
                    try:
                        try:
                            start(r.path, "/feedback")
                        except Killed:
                            pass
                    finally:
                        g["_take_snapshot"] = real
                    first = state.load(env["CLAUDE_CODE_SESSION_ID"], "/feedback") or {}
            r.write(FB, "fb\n")
            return r, env, first

        def e_midrun_no_snapshot():
            for cause, where in (("status", "lb"), ("cut", "main"), ("status", "main"), ("cut", "lb")):
                name = "e-midrun-no-snapshot-%s-%s" % (cause, where)
                r, env, first = no_snapshot(name, cause, where)
                branch = LB if where == "lb" else "main"
                old_main, old_head = rev(r, "main"), head(r)
                e = run_end(env, "/feedback")
                check(first.get("start_dirty") is None and (first.get("midrun") or {}).get("command") == "/specify"
                      and e.get("row") == "midrun-kept"
                      and e.get("print") == [kept_row(branch, T["reason.land.no-snapshot"], keys="B-2" if where == "lb" else "ACME-1")]
                      and rev(r, "main") == old_main and head(r) == old_head and "- [ ] specify's" in read(r, FUP)
                      and not gone(r, FB) and r.git("status", "--porcelain", "--", FUP) != "",
                      "%s: nothing committed while the open run stands, the open run's file still dirty (%r)" % (name, e))
            for cause, where, ends in (("status", "lb", "dropped"), ("cut", "main", "left")):
                name = "e-midrun-no-snapshot-ended-%s-%s" % (cause, where)
                r, env, first = no_snapshot(name, cause, where)
                if ends == "dropped":
                    drop(env, "/specify")
                else:
                    r.git("switch", "-q", "-c", "tmp")
                    r.git("switch", "-q", "main")
                e = run_end(env, "/feedback")
                m = rev(r, "main")
                check(e.get("row") == "pushed-default" and on_origin(r) == m and changed(r, m) == sorted([FB, FUP])
                      and "still open" not in (e.get("line") or ""),
                      "%s: the open run no longer stands -- the change taken against HEAD, every session file with it "
                      "(%r)" % (name, e))

        case("e_midrun_no_snapshot", e_midrun_no_snapshot)

        # The here form refused (P2): while the open run stands, nothing committed or held, the mid-run row naming the
        # refused path, G1's block in its not-committed mid-run form; once it no longer stands, steps 2-4
        def kept_world(name):
            """/specify open on main with its follow-ups line in progress and notes.md (not the plugin's) dirty; /feedback
            typed mid-run ticks /specify's line -- a line of its snapshot HEAD lacks, gone from its copy: dropped."""
            r, env = mworld(name, follow="- [ ] a\n")
            start_(env, "/specify", "--key", "ACME-1")
            append(r, FUP, "- [ ] s\n")
            r.write("notes.md", "n\n")
            start_(env, "/feedback")
            r.write(FUP, "- [ ] a\n- [x] s\n- [ ] f\n")
            r.write(FB, "fb\n")
            return r, env

        def e_midrun_kept():
            r, env = kept_world("e-midrun-kept")
            old = head(r)
            e = run_end(env, "/feedback")
            clause = lines.fill("reason.land.dropped", {"<path>": FUP, "<onto>": "main"})
            block = g1_midrun(r, ["notes.md"], T["g1.not_done.uncommitted"], keys="ACME-1")
            check(e.get("row") == "midrun-kept" and e.get("print") == [kept_row("main", clause, keys="ACME-1"), block]
                  and head(r) == old and held(r) == [] and "WILL" not in block.split("Fix:")[0],
                  "e_midrun_kept: the mid-run row with the refused path's clause, nothing committed or held, the "
                  "not-committed mid-run form (%r)" % e)
            r, env = kept_world("e-midrun-kept-ended")
            old = head(r)
            drop(env, "/specify")
            e = run_end(env, "/feedback")
            check(e.get("row") == "pushed-default" and r.git("rev-parse", "HEAD^") == old and on_origin(r) == head(r)
                  and changed(r, "HEAD") == sorted([FB, FUP]),
                  "e_midrun_kept: once the open run no longer stands, steps 2-4 commit on HEAD's branch (%r)" % e)

        case("e_midrun_kept", e_midrun_kept)

        # A mid-run stay whose landing did not land the run's whole change: G1's mid-run form with the not-landed Not
        # done -- nothing, held (an index.lock), held stuck, there, and landed with a path held alone
        def e_midrun_unlanded():
            def setup(name, extra=None):
                r, env = mworld(name, branch=LB)
                if extra:
                    extra(r)
                    age(r)
                start_(env, "/specify", "--key", "B-2")
                r.write(DELIV, "draft\n")
                start_(env, "/feedback")
                return r, env

            def lb_follow(r):  # LB's follow-ups.md holds a line main lacks
                r.write(FUP, "- [ ] b\n")
                r.commit_all("B-2 a follow-up")
                r.git("push", "-q", "origin", LB)

            for name, act, row in (("nothing", lambda r: None, "nothing"),
                                   ("held", lambda r: (r.write(FB, "fb\n"),
                                                       open(os.path.join(r.path, ".git", "index.lock"), "w").close()),
                                    "held"),
                                   ("stuck", lambda r: r.write(FUP, "- [x] b\n"), "held-stuck"),
                                   ("partial", lambda r: (r.write(FUP, "- [x] b\n"), r.write(FB, "fb\n")),
                                    "pushed-default")):
                r, env = setup("e-midrun-unlanded-" + name, lb_follow if name in ("stuck", "partial") else None)
                act(r)
                e = run_end(env, "/feedback")
                lock = os.path.join(r.path, ".git", "index.lock")
                if os.path.exists(lock):
                    os.remove(lock)
                block = g1_midrun(r, [DELIV], landing_nd(LB, True), keys="B-2")
                check(e.get("row") == row and (e.get("print") or [None])[-1] == block,
                      "e_midrun_unlanded: after %s, the mid-run form with the not-landed Not done (%r)" % (name, e))
            r, env = setup("e-midrun-unlanded-there")
            o = clone(r, "e-midrun-unlanded-there-other")
            o.write(FB, "fb\n")
            o.commit_all("ACME-1 the same file")
            o.git("push", "-q", "origin", "main")
            r.git("fetch", "-q", "origin")
            r.write(FB, "fb\n")
            e = run_end(env, "/feedback")
            check(e.get("row") == "there" and (e.get("print") or [None])[-1] == g1_midrun(r, [DELIV], landing_nd(LB, True), keys="B-2"),
                  "e_midrun_unlanded: after there, the mid-run form with the not-landed Not done (%r)" % e)

        case("e_midrun_unlanded", e_midrun_unlanded)

        # The same command typed twice, keyless (D-park, P4, P19, P35, N1, N3): a restart (M1), parked, never typed mid-run;
        # each run's end reads and writes its own record by --started, in either order
        def t_midrun_same_command():
            r, env = mworld("t-midrun-same-command")
            r.write("notes.md", "n\n")
            start_(env, "/specify", "--commit-key", "ACME-1")
            declined_(env, "/specify", "--path", "notes.md")
            first = backdate(env, "/specify")
            b = start_(env, "/specify")
            check((b.get("replaced") or {}).get("parked") is True and b.get("midrun") is None
                  and not any("is still open on it" in x for x in b.get("print") or [])
                  and os.path.exists(file_of(env, "/specify", "specify.%s.json" % stamp_of(first))),
                  "t_midrun_same_command: the second start parks the first, and is not typed mid-run (%r)" % b)
            e = run_end(env, "/specify", "--started", b.get("started"))
            restored = record(env, "/specify") or {}
            check(e.get("error") is None and restored.get("started") == first and restored.get("protects") is False
                  and restored.get("parked") is False,
                  "t_midrun_same_command: the second's end restores the first, protects false (%r)" % restored)
            f = start_(env, "/feedback")
            check(f.get("midrun") is None,
                  "t_midrun_ends_command_again: once its command's start ran again, the first run protects nothing "
                  "(%r)" % f)
            run_end(env, "/feedback")
            r.write(FB, "fb\n")
            e = run_end(env, "/specify", "--started", first)
            block = g1_of(r, ["notes.md"])
            check(e.get("record") == "found" and e.get("row") == "pushed-default"
                  and e.get("print") == [pushed_default(head(r)[:7], r.path)
                                         + lines.fill("app.declined", {"<path>": "notes.md"}), block]
                  and r.git("log", "-1", "--format=%s") == SUBJECT % ("ACME-1", "/specify")
                  and record(env, "/specify") is None,
                  "t_midrun_same_command: the first run's end finds its own record: its block, its declined append, "
                  "its commit key (%r)" % e)

        def t_started_not_found():
            """P35, F7: a third start replaced the restored record; the first run's declined --started and end --started
            take the first run's derived path, never <command>.json, and its end sees the third run open (P5)."""
            r, env = mworld("t-started-not-found")
            start_(env, "/specify")
            first = backdate(env, "/specify", 240)
            b = start_(env, "/specify")
            run_end(env, "/specify", "--started", b.get("started"))
            third = start_(env, "/specify")
            check((third.get("replaced") or {}).get("parked") is False,
                  "t_started_not_found: the restored record is replaced, not parked (%r)" % third.get("replaced"))
            third_raw = raw(env, "/specify")
            r.write(FB, "fb\n")
            old = head(r)
            got = declined_(env, "/specify", "--started", first, "--path", "x.md")
            derived = file_of(env, "/specify", "specify.%s.json" % stamp_of(first))
            drec = json.load(open(derived, encoding="utf-8")) if os.path.exists(derived) else {}
            e = run_end(env, "/specify", "--started", first)
            check(got.get("record") == "created" and drec.get("declined") == ["x.md"] and drec.get("started") == first
                  and drec.get("parked") is False and e.get("record") == "declined-only" and e.get("row") == "midrun-kept"
                  and e.get("print") == [kept_row("main", T["reason.land.no-preflight"])] and head(r) == old
                  and raw(env, "/specify") == third_raw and os.path.exists(derived),
                  "t_started_not_found: both calls on the derived path, the third's record byte for byte, nothing "
                  "committed (%r, %r)" % (got, e))

        def t_park_out_of_order(landing):
            """N1: the second run abandoned with a G1 block and a declined path of its own; the first run's declined
            --started and end --started end on its own parked record, which is removed; <command>.json, the second's,
            byte for byte. <landing>: the first run's start stayed on prd/B-2-y (G1, unkeyed), so its end lands through
            on_move."""
            name = "t-park-out-of-order" + ("-landing" if landing else "")
            r, env = mworld(name, branch=LB if landing else None)
            if landing:
                r.write("notes.md", "n\n")
            s1 = start_(env, "/specify")
            first = backdate(env, "/specify")
            r.write("notes.md", "n\n")
            start_(env, "/specify")
            declined_(env, "/specify", "--path", "notes.md")
            second_raw = raw(env, "/specify")
            r.write("x.md", "x\n")
            declined_(env, "/specify", "--started", first, "--path", "x.md")
            r.write(FB, "fb\n")
            parked_file = file_of(env, "/specify", "specify.%s.json" % stamp_of(first))
            e = run_end(env, "/specify", "--started", first)
            m = rev(r, "main")
            line = (e.get("line") or "")
            ok = (e.get("record") == "found" and e.get("error") is None and raw(env, "/specify") == second_raw
                  and not os.path.exists(parked_file) and line.endswith(lines.fill("app.declined", {"<path>": "x.md"}))
                  and changed(r, m) == [FB] and on_origin(r) == m)
            if landing:
                ok = ok and (s1.get("stay") or {}).get("kind") == "unkeyed" and on(r) == LB and gone(r, FB)
            check(ok, "%s: the first run ends on its own parked record, the second's byte for byte (%r)" % (name, e))

        def t_park_stack():
            """Three runs of one command: each end restores the newest parked, newest first."""
            r, env = mworld("t-park-stack")
            start_(env, "/specify")
            a = backdate(env, "/specify", 240)
            start_(env, "/specify")
            b = backdate(env, "/specify", 120)
            c = start_(env, "/specify").get("started")
            run_end(env, "/specify", "--started", c)
            got_b = (record(env, "/specify") or {}).get("started")
            run_end(env, "/specify", "--started", b)
            got_a = (record(env, "/specify") or {}).get("started")
            e = run_end(env, "/specify", "--started", a)
            check(got_b == b and got_a == a and e.get("record") == "found" and record(env, "/specify") is None,
                  "t_park_stack: restored newest first (%r, %r)" % (got_b, got_a))

        def t_park_dropped():
            """HEAD left the parked record's branch and returned since its start: the nested end drops it."""
            r, env = mworld("t-park-dropped", branch=LB)
            start_(env, "/specify", "--key", "B-2")
            first = backdate(env, "/specify")
            b = start_(env, "/specify", "--key", "B-2")
            r.git("switch", "-q", "main")
            r.git("switch", "-q", LB)
            run_end(env, "/specify", "--started", b.get("started"))
            check(record(env, "/specify") is None
                  and not os.path.exists(file_of(env, "/specify", "specify.%s.json" % stamp_of(first))),
                  "t_park_dropped: a leave of its branch since its start drops the parked record")

        def t_park_misrooted_stop():
            """The second run's end on a misrooted path, before any gate: the parked record restored, read in its own
            repository (its top)."""
            r, env = mworld("t-park-misrooted-stop")
            start_(env, "/specify")
            first = backdate(env, "/specify")
            b = start_(env, "/specify")
            elsewhere = os.path.join(tmp, "t-park-misrooted-elsewhere")
            os.makedirs(elsewhere)
            e = run_end(env, "/specify", "--started", b.get("started"), specs=elsewhere)
            restored = record(env, "/specify") or {}
            check(e.get("row") == "misrooted" and restored.get("started") == first and restored.get("protects") is False,
                  "t_park_misrooted_stop: the misrooted end restores the parked record (%r, %r)" % (e.get("row"), restored))

        def t_derived_not_parked():
            """N3: a declined --started with no start makes a record at a derived path, never marked parked: a nested
            run's unpark leaves it as it was, though its stamp is newer than the parked record's."""
            r, env = mworld("t-derived-not-parked")
            start_(env, "/specify")
            first = backdate(env, "/specify", 240)
            later = time.strftime(STAMP_FMT, time.gmtime(time.time() - 120))
            declined_(env, "/specify", "--started", later, "--path", "y.md")
            derived_raw = raw(env, "/specify", "specify.%s.json" % stamp_of(later))
            b = start_(env, "/specify")
            run_end(env, "/specify", "--started", b.get("started"))
            check(derived_raw is not None and raw(env, "/specify", "specify.%s.json" % stamp_of(later)) == derived_raw
                  and (record(env, "/specify") or {}).get("started") == first,
                  "t_derived_not_parked: the derived record untouched, the parked one restored")

        case("t_midrun_same_command", t_midrun_same_command)
        case("t_started_not_found", t_started_not_found)
        case("t_park_out_of_order", lambda: t_park_out_of_order(False))
        case("t_park_out_of_order_landing", lambda: t_park_out_of_order(True))
        case("t_park_stack", t_park_stack)
        case("t_park_dropped", t_park_dropped)
        case("t_park_misrooted_stop", t_park_misrooted_stop)
        case("t_derived_not_parked", t_derived_not_parked)

        def t_park_abandoned_middle():
            """M3: three keyless runs of one command -- each a restart (M1) -- the middle one abandoned; the third's end
            restores the middle one. The oldest stays parked, marked protects: false since the second start parked it,
            so it makes no later run of another command a run typed mid-run."""
            r, env = mworld("t-park-abandoned-middle")
            start_(env, "/specify")
            a = backdate(env, "/specify", 240)
            start_(env, "/specify")
            backdate(env, "/specify", 120)
            c = start_(env, "/specify").get("started")
            run_end(env, "/specify", "--started", c)
            oldest = json.load(open(file_of(env, "/specify", "specify.%s.json" % stamp_of(a)), encoding="utf-8"))
            f = start_(env, "/feedback")
            check(oldest.get("parked") is True and oldest.get("protects") is False and f.get("midrun") is None,
                  "t_park_abandoned_middle: the oldest parked record protects nothing (%r, %r)" % (oldest.get("protects"), f))

        case("t_park_abandoned_middle", t_park_abandoned_middle)

        def follow(got, env):
            """<got>, then each call the one before it names as next, run as the skill runs it, until one names none."""
            seen = [got]
            while (seen[-1].get("next") or {}).get("run") and len(seen) < 12:
                seen.append(shell(seen[-1]["next"]["run"], env))
            return seen

        def ahead(r, name):
            """origin's main one commit ahead of r's: another clone's commit, which r fetches at its next start."""
            o = clone(r, name)
            o.write("specifications/PRD-ACME-1-x/notes-other.md", "o\n")
            o.commit_all("ACME-1 Other work")
            o.git("push", "-q", "origin", "main")
            return o.git("rev-parse", "HEAD")

        # I1: a re-run is a run typed mid-run only where its first start was one -- it carries that start's open run
        # and tests it again, and never takes one that started since
        def t_midrun_rerun():
            r, env = mworld("t-midrun-rerun-later", branch=LB)
            first = start_(env, "/document", "--key", "ACME-1")
            start_(env, "/specify", "--key", "ACME-1")
            r.write(FUP, "- [ ] specify's\n")
            again = start_(env, "/document", "--key", "ACME-1", "--key", "B-2", "--rerun")
            r.write(FB, "fb\n")
            e = run_end(env, "/document")
            line = e.get("line") or ""
            check(first.get("b4_left") == LB and again.get("midrun") is None and again.get("b4_left") is None
                  and on(r) == LB and e.get("row") == "pushed-plugin" and "still open" not in line
                  and "was open" not in line,
                  "t_midrun_rerun: a re-run under a run started since its first start switches back as any B4 re-run, "
                  "and its end has no mid-run wording (%r, %r)" % (again, e))
            for name, ended in (("t-midrun-rerun-standing", False), ("t-midrun-rerun-ended", True)):
                r, env = mworld(name)
                start_(env, "/specify", "--key", "ACME-1")
                f = start_(env, "/document", "--key", "ACME-1")
                if ended:
                    run_end(env, "/specify")
                again = start_(env, "/document", "--key", "ACME-1", "--key", "B-2", "--rerun")
                r.write(FB, "fb\n")
                e = run_end(env, "/document")
                ok = (f.get("midrun") or {}).get("command") == "/specify" and on(r) == "main"
                if ended:
                    ok = ok and again.get("midrun") is None and e.get("row") == "pushed-default"
                else:
                    ok = ok and again.get("midrun") == f.get("midrun") and e.get("row") == "here"
                check(ok, "t_midrun_rerun: %s -- the re-run tests its first start's open run again (%r, %r)"
                      % (name, again, e))

        case("t_midrun_rerun", t_midrun_rerun)

        # M1, as SRG §4 step 1's here form words it: the typed run's own handoff moved HEAD off the branch it started
        # on, onto one a key of the open run names too; the here form does not run, and steps 2-4 commit every session
        # file uncommitted there, the open run's line among them
        def t_midrun_handoff_moved():
            r, env = mworld("t-midrun-handoff-moved", follow="- [ ] a\n")
            start_(env, "/specify", "--key", "ACME-1")
            append(r, FUP, "- [ ] specify's\n")
            c = start_(env, "/create-ard", "--key", "ACME-1")
            r.git("switch", "-q", "-c", "ard/ACME-1-x")
            r.write(FB, "ard's\n")
            e = run_end(env, "/create-ard", "--commit-key", "ACME-1")
            h = head(r)
            check((c.get("midrun") or {}).get("command") == "/specify" and e.get("row") == "origin-lacks"
                  and e.get("branch") == "ard/ACME-1-x" and changed(r, h) == sorted([FB, FUP])
                  and "- [ ] specify's" in show(r, h, FUP),
                  "t_midrun_handoff_moved: HEAD moved by the run's own handoff -- steps 2-4, as worded (%r)" % e)

        case("t_midrun_handoff_moved", t_midrun_handoff_moved)

        # M2: a parked run's re-run reads and writes its own record by --started: its new record parked under a stamp
        # of its own, the old parked file removed, every next repeating --started; the second run's <command>.json
        # byte for byte as before; its end then ends on its own record
        def t_park_rerun():
            r, env = mworld("t-park-rerun")
            start_(env, "/document", "--key", "ACME-1")
            a = backdate(env, "/document", 240)
            start_(env, "/document", "--key", "ACME-1")
            b = backdate(env, "/document", 120)
            declined_(env, "/document", "--started", b, "--path", "notes.md")
            b_raw = raw(env, "/document")
            ahead(r, "t-park-rerun-other")  # a catch-up for the re-run's flush: a second unit, past --budget 0
            calls = follow(start_(env, "/document", "--key", "ACME-1", "--key", "B-2", "--rerun", "--started", a,
                                  "--budget", "0"), env)
            new = calls[-1].get("started")
            new_file = file_of(env, "/document", "document.%s.json" % stamp_of(new or a))
            nrec = json.load(open(new_file, encoding="utf-8")) if os.path.exists(new_file) else {}
            nexts = [c["next"]["run"] for c in calls if (c.get("next") or {}).get("run")]
            check(len(calls) > 1 and all("--started " + new in x for x in nexts) and new != a
                  and raw(env, "/document") == b_raw and nrec.get("parked") is True and nrec.get("protects") is False
                  and "notes.md" not in (nrec.get("declined") or [])
                  and not os.path.exists(file_of(env, "/document", "document.%s.json" % stamp_of(a))),
                  "t_park_rerun: the re-run's record parked under its own stamp, every next carrying --started, "
                  "<command>.json byte for byte (%r)" % [(c.get("started"), c.get("next")) for c in calls])
            r.write(FB, "fb\n")
            e = run_end(env, "/document", "--started", new)
            check(e.get("record") == "found" and e.get("error") is None and raw(env, "/document") == b_raw
                  and not os.path.exists(new_file),
                  "t_park_rerun: its end ends on its own record, the second run's untouched (%r)" % e)

        case("t_park_rerun", t_park_rerun)

        # A re-run the harness stops before its JSON: the run knows only the stamp of the start before it, which the
        # re-run's record keeps in started_before, so the start --resume --started <that stamp> the skill makes goes on
        # with the re-run's record -- no fresh record beside it; for a parked run's re-run, the second run's
        # <command>.json byte for byte as it was
        RERUN_KEYS = ("--key", "ACME-1", "--key", "B-2")

        def rec_of(env, command, name=None):
            path = file_of(env, command, name)
            return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}

        def names_of(env, command):
            sdir = os.path.dirname(file_of(env, command))
            prefix = command.lstrip("/")
            return sorted(n for n in os.listdir(sdir) if n.startswith(prefix + ".")) if os.path.isdir(sdir) else []

        def t_rerun_stopped():
            r, env = mworld("t-rerun-stopped")
            start_(env, "/document", "--key", "ACME-1")
            a = backdate(env, "/document", 240)
            ahead(r, "t-rerun-stopped-other")  # a catch-up for the re-run's flush: a second unit, past --budget 0
            stopped = start_(env, "/document", *RERUN_KEYS, "--rerun", "--started", a, "--budget", "0")
            saved = rec_of(env, "/document")  # what the harness's stop leaves: the re-run's record, its JSON unseen
            # the skill's remake: the same call again with --resume added (When the JSON names next)
            calls = follow(start_(env, "/document", *RERUN_KEYS, "--rerun", "--resume", "--started", a), env)
            done = rec_of(env, "/document")
            check((stopped.get("next") or {}).get("run") and saved.get("stage") in START_STAGES
                  and saved.get("started") not in (None, a) and saved.get("started_before") == [a]
                  and calls[0].get("started") == saved.get("started") and calls[-1].get("error") is None
                  and done.get("stage") == "done" and done.get("started") == saved.get("started")
                  and names_of(env, "/document") == ["document.json"],
                  "t_rerun_stopped: start --resume --started <the earlier stamp> goes on with the re-run's record, "
                  "<command>.json the one record (%r, %r)" % (names_of(env, "/document"),
                                                              [(c.get("started"), c.get("error")) for c in calls]))

        case("t_rerun_stopped", t_rerun_stopped)

        def t_rerun_stopped_parked():
            r, env = mworld("t-rerun-stopped-parked")
            start_(env, "/document", "--key", "ACME-1")
            a = backdate(env, "/document", 240)
            start_(env, "/document", "--key", "ACME-1")
            backdate(env, "/document", 120)
            b_raw = raw(env, "/document")
            ahead(r, "t-rerun-stopped-parked-other")
            stopped = start_(env, "/document", *RERUN_KEYS, "--rerun", "--started", a, "--budget", "0")
            after_stop = names_of(env, "/document")
            calls = follow(start_(env, "/document", *RERUN_KEYS, "--resume", "--started", a), env)
            new = calls[0].get("started") or a
            nrec = rec_of(env, "/document", "document.%s.json" % stamp_of(new))
            check((stopped.get("next") or {}).get("run") and new != a and raw(env, "/document") == b_raw
                  and after_stop == names_of(env, "/document") == sorted(["document.json", "document.%s.json" % stamp_of(new)])
                  and calls[-1].get("error") is None and nrec.get("stage") == "done"
                  and nrec.get("started_before") == [a] and nrec.get("parked") is True,
                  "t_rerun_stopped_parked: the parked run's re-run goes on from the earlier stamp on its own record, "
                  "the second run's <command>.json byte for byte (%r, %r)"
                  % (after_stop, [(c.get("started"), c.get("error")) for c in calls]))

        case("t_rerun_stopped_parked", t_rerun_stopped_parked)

        # The cut-off: the parked run's re-run saved its new record and was stopped before removing the file it re-ran
        # from. That stamp names the new record; the file left behind is listed to no open-run test and restored by
        # no end; the end that removes the record listing it removes it too
        def t_rerun_cut_off():
            r, env = mworld("t-rerun-cut-off")
            start_(env, "/document", "--key", "ACME-1")
            a = backdate(env, "/document", 240)
            start_(env, "/document", "--key", "ACME-1")
            b = backdate(env, "/document", 120)
            old_name = "document.%s.json" % stamp_of(a)
            old_raw = raw(env, "/document", old_name)
            calls = follow(start_(env, "/document", *RERUN_KEYS, "--rerun", "--started", a), env)
            new = calls[0].get("started") or a
            with open(file_of(env, "/document", old_name), "wb") as fh:  # the old file, as the cut-off leaves it
                fh.write(old_raw or b"")
            with in_env(env):
                session = env["CLAUDE_CODE_SESSION_ID"]
                found = state.find(session, "/document", a)[0]
                listed = [rec.get("started") for rec in state.others(session, "/feedback")]
            r.write(FB, "fb\n")
            e_b = run_end(env, "/document", "--started", b)
            restored = rec_of(env, "/document")
            e_a = run_end(env, "/document", "--started", a)
            check(old_raw is not None and new != a
                  and found == file_of(env, "/document", "document.%s.json" % stamp_of(new)) and a not in listed
                  and e_b.get("error") is None and restored.get("started") == new
                  and e_a.get("record") == "found" and e_a.get("error") is None and names_of(env, "/document") == [],
                  "t_rerun_cut_off: the earlier stamp names the re-run's record, the file left behind is never listed, "
                  "restored or left after the end (%r, %r, %r)" % (listed, restored.get("started"), names_of(env, "/document")))

        case("t_rerun_cut_off", t_rerun_cut_off)

        # The old stamp at the end: after a completed re-run, the stamp of the start before it still names the run's
        # record -- for declined and for end -- and so does it after a start --resume --started that starts afresh
        def t_rerun_old_stamp_end():
            r, env = mworld("t-rerun-old-stamp")
            start_(env, "/document", "--key", "ACME-1")
            a = backdate(env, "/document", 240)
            calls = follow(start_(env, "/document", *RERUN_KEYS, "--rerun", "--started", a), env)
            d = declined_(env, "/document", "--started", a, "--path", "notes.md")
            rec = rec_of(env, "/document")
            r.write(FB, "fb\n")
            e = run_end(env, "/document", "--started", a)
            check(calls[-1].get("started") not in (None, a) and d.get("record") == "found"
                  and rec.get("declined") == ["notes.md"] and e.get("record") == "found" and e.get("error") is None
                  and names_of(env, "/document") == [],
                  "t_rerun_old_stamp_end: declined and end by the earlier stamp reach the re-run's record (%r, %r, %r)"
                  % (d, e.get("record"), names_of(env, "/document")))
            r2, env2 = mworld("t-resume-fresh-old-stamp")
            start_(env2, "/document", "--key", "ACME-1")
            a2 = backdate(env2, "/document", 240)
            fresh = start_(env2, "/document", "--key", "ACME-1", "--resume", "--started", a2)  # at done: it starts afresh
            r2.write(FB, "fb\n")
            e2 = run_end(env2, "/document", "--started", a2)
            check(fresh.get("started") not in (None, a2) and fresh.get("replaced") is None
                  and e2.get("record") == "found" and e2.get("error") is None and names_of(env2, "/document") == [],
                  "t_rerun_old_stamp_end: after a start --resume --started that starts afresh, setting nothing aside, "
                  "the earlier stamp still names the run's record (%r, %r, %r)"
                  % (fresh.get("started"), fresh.get("replaced"), e2.get("record")))

        case("t_rerun_old_stamp_end", t_rerun_old_stamp_end)

        # A re-run of the open run leaves it standing: it takes over that run's record, whose started_before keeps the
        # stamp a run typed under it recorded (midrun), so that run's end still finds it open and commits its own change
        # by the here form, unpushed
        def t_midrun_open_rerun():
            r, env = mworld("t-midrun-open-rerun")
            up = on_origin(r)
            start_(env, "/document", "--key", "ACME-1")
            a = backdate(env, "/document", 240)
            f = start_(env, "/feedback")
            calls = follow(start_(env, "/document", *RERUN_KEYS, "--rerun", "--started", a), env)
            r.write(FB, "fb\n")
            e = run_end(env, "/feedback")
            check((f.get("midrun") or {}).get("started") == a and calls[-1].get("error") is None
                  and calls[0].get("started") not in (None, a) and e.get("row") == "here" and e.get("pushed") is False
                  and on_origin(r) == up,
                  "t_midrun_open_rerun: after the open run's re-run, the run typed under it still reads it as standing "
                  "-- the here row, nothing pushed (%r)" % e)

        case("t_midrun_open_rerun", t_midrun_open_rerun)

        # A continuation of the open run that starts afresh leaves it standing where it takes its record over: named by
        # --started, or, named by none, a record marked call_returned false, as the harness's stop of the run's start
        # leaves it -- started_before then lists the stamp the run typed under it
        # holds. Named by none and finding a record whose start returned, it sets that record aside, and the run typed
        # under it commits its own change and pushes it. The take-over deletes nothing of another run: a parked record of
        # an earlier run of the command stays byte for byte
        def t_midrun_open_resume():
            got, kept = {}, {}
            for name, named, returned in (("named", True, True), ("own", False, False), ("returned", False, True),
                                          ("other-args", False, False)):
                r, env = mworld("t-midrun-open-resume-" + name)
                up = on_origin(r)
                parked_raw = None
                if name == "own":  # an earlier run of the command, open, which the run's start parks
                    start_(env, "/document", "--key", "ACME-1")
                    backdate(env, "/document", 360)
                start_(env, "/document", "--key", "ACME-1")
                a = backdate(env, "/document", 240)
                if not returned:  # the harness stopped this start before it returned its JSON
                    with in_env(env):
                        session = env["CLAUDE_CODE_SESSION_ID"]
                        rec = state.load(session, "/document")
                        rec["call_returned"] = False
                        state.save(session, "/document", rec)
                if name == "own":
                    parked = [n for n in names_of(env, "/document") if n != "document.json"]
                    parked_raw = raw(env, "/document", parked[0]) if len(parked) == 1 else None
                f = start_(env, "/feedback")
                # other arguments with the same key set: a restart (M1), which ends the first run's protection
                keys = ("--key", "ACME-1") + (("--commit-key", "ACME-1") if name == "other-args" else ())
                again = start_(env, "/document", *keys, "--resume", *(("--started", a) if named else ()))
                taken = rec_of(env, "/document")
                if name == "own":
                    kept["parked"] = parked_raw is not None and raw(env, "/document", parked[0]) == parked_raw
                    kept["before"], kept["a"] = taken.get("started_before"), a
                r.write(FB, "fb\n")
                e = run_end(env, "/feedback")
                got[name] = ((f.get("midrun") or {}).get("started") == a, again.get("started") != a,
                             (again.get("replaced") or {}).get("started"), e.get("row"), e.get("pushed"),
                             on_origin(r) == up)
                if name in ("returned", "other-args"):
                    got[name + "-a"] = a
            standing = (True, True, None, "here", False, True)
            check(got.get("named") == standing and got.get("own") == standing
                  and all(got.get(n, ())[:3] == (True, True, got.get(n + "-a")) and got[n][4] is True
                          and got[n][5] is False for n in ("returned", "other-args")),
                  "t_midrun_open_resume: a fresh continuation leaves the open run standing where it names its record by "
                  "--started or finds its own stopped start's (the here row, nothing pushed); finding a record whose "
                  "start returned, or a stopped one made with other arguments, it sets it aside, and the run typed "
                  "under it pushes (%r)" % got)
            check(kept.get("parked") is True and kept.get("before") == [kept.get("a")],
                  "t_midrun_open_resume: taking over its stopped start's record deletes nothing of another run -- the "
                  "earlier run's parked record byte for byte (%r)" % kept)

        case("t_midrun_open_resume", t_midrun_open_resume)

        # call_returned: a plain start writes it false at its first save and true as it returns, so one killed anywhere
        # in its stages leaves it false; the continuation given no --started that remakes it goes on with that record,
        # marked so already, leaves it false where it is killed in turn, and true once it returns
        def t_call_returned_mark():
            r, env = mworld("t-call-returned")
            ahead(r, "t-call-returned-other")  # a second unit, so --budget 0 stops the first call with a next
            first = start_(env, "/document", "--key", "ACME-1", "--budget", "0")
            after_first = rec_of(env, "/document").get("call_returned")
            real = g["_start_stages"]

            def killed(_run):
                raise Killed()

            marks = []
            for resume in (False, True):  # a fresh plain start, then the continuation that remakes it
                g["_start_stages"] = killed
                try:
                    with in_env(env):
                        start(env["SPECS_PATH"], "/document", ["ACME-1"], resume=resume)
                except Killed:
                    pass
                finally:
                    g["_start_stages"] = real
                rec = rec_of(env, "/document")
                marks.append((rec.get("stage"), rec.get("call_returned"), rec.get("started")))
            again = start_(env, "/document", "--key", "ACME-1", "--resume")
            back = rec_of(env, "/document").get("call_returned")
            check((first.get("next") or {}).get("run") and after_first is True
                  and marks[0][0] in START_STAGES and marks[0][1] is False
                  and marks[1][0] in START_STAGES and marks[1][1] is False and marks[1][2] == marks[0][2]
                  and again.get("error") is None and again.get("started") == marks[0][2] and back is True,
                  "t_call_returned_mark: true once a call returns; false where a plain start, then the continuation "
                  "that goes on with its record, is killed in its stages; true once that continuation returns "
                  "(%r, %r, %r)" % (after_first, marks, back))

        case("t_call_returned_mark", t_call_returned_mark)

        # call_returned and a named call: a call given --started, or a re-run, belongs to a run that holds the record's
        # stamp already, so it never writes the mark false -- killed in its stages after a stage's save, a continuation
        # that goes on leaves the record as the start that returned the stamp left it, true, and a fresh named
        # continuation or a re-run leaves its new record true. So another run's continuation given no --started, with the same arguments and
        # past 15 minutes, parks that record, an open run's, rather than taking it up as its own stopped start's
        def t_call_returned_named():
            r, env = mworld("t-call-returned-named")
            ahead(r, "t-call-returned-named-other")  # a second unit, so --budget 0 stops the first call with a next
            first = start_(env, "/document", "--key", "ACME-1", "--budget", "0")
            a = first.get("started")
            real = g["_start_stages"]

            def killed(run):  # stopped inside its stages, after the first stage's save
                g["_advance"](run, run["rec"].get("stage") or "fetch")
                raise Killed()

            def kill(**kw):
                g["_start_stages"] = killed
                try:
                    with in_env(env):
                        start(env["SPECS_PATH"], "/document", ["ACME-1"], **kw)
                except Killed:
                    pass
                finally:
                    g["_start_stages"] = real
                rec = rec_of(env, "/document")
                return rec.get("stage"), rec.get("call_returned")

            def aged():  # the record saved 20 minutes ago: past resumable's 15
                path = file_of(env, "/document")
                rec = json.load(open(path, encoding="utf-8"))
                rec["updated"] = time.strftime(STAMP_FMT, time.gmtime(time.time() - 1200))
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(rec, fh)
                return rec.get("started")

            went_on = kill(resume=True, started=a)  # within 15 minutes: it goes on with the record
            aged()
            other = start_(env, "/document", "--key", "ACME-1", "--resume")  # another run's remake, named by none
            c = aged()
            fresh = kill(resume=True, started=c)  # past 15 minutes: a fresh named continuation, its record taken over
            rerun = kill(rerun=True)  # a re-run, given no --started: its record new
            check(went_on[0] in START_STAGES and [went_on[1], fresh[1], rerun[1]] == [True, True, True],
                  "t_call_returned_named: a named continuation, a fresh named one and a re-run, each killed in its "
                  "stages, leave the mark true (%r, %r, %r)" % (went_on, fresh, rerun))
            check(other.get("error") is None and (other.get("replaced") or {}).get("started") == a
                  and (other.get("replaced") or {}).get("parked") is True,
                  "t_call_returned_named: the record a killed named call left is parked by another run's unnamed "
                  "continuation, never taken up as its own (%r)" % other.get("replaced"))

        case("t_call_returned_named", t_call_returned_named)

        # call_returned on the error path: a call whose stages raise returns its JSON, the record's stamp in it, even
        # where _close raises too -- the mark is saved true apart from _close
        def t_call_returned_error():
            r, env = mworld("t-call-returned-error")
            real_stages, real_head = g["_start_stages"], g["_head_branch"]

            def no_head(_specs):
                raise RuntimeError("no HEAD to read")

            def broken(_run):  # the stages raise, and from here on HEAD cannot be read, so _close raises as well
                g["_head_branch"] = no_head
                raise RuntimeError("the stages failed")

            g["_start_stages"] = broken
            try:
                with in_env(env):
                    got = start(env["SPECS_PATH"], "/document", ["ACME-1"])
            finally:
                g["_start_stages"], g["_head_branch"] = real_stages, real_head
            rec = rec_of(env, "/document")
            check("the stages failed" in (got.get("error") or "") and got.get("started") == rec.get("started")
                  and rec.get("call_returned") is True,
                  "t_call_returned_error: a call whose stages and whose _close both raise still returns its JSON, its "
                  "stamp in it, and leaves the mark true (%r, %r)" % (got.get("error"), rec.get("call_returned")))

        case("t_call_returned_error", t_call_returned_error)

        # A continuation given no --started meets another run's record -- marked call_returned true, at a start stage,
        # made with the same arguments and saved within 15 minutes, which resumable alone would let it go on with -- as a
        # plain start does: it parks that open run's record and starts afresh. The other run's next, made as given, still
        # goes on with its own record, this run's record untouched
        def t_resume_unnamed_other_run():
            r, env = mworld("t-resume-unnamed-other-run")
            ahead(r, "t-resume-unnamed-other-run-other")  # a second unit, so --budget 0 stops the first call with a next
            first = start_(env, "/document", "--key", "ACME-1", "--budget", "0")
            a, nxt = first.get("started"), (first.get("next") or {}).get("run") or ""
            before = rec_of(env, "/document")
            while time.strftime(STAMP_FMT, time.gmtime()) <= (a or ""):  # this run's own stamp a later second, so its
                time.sleep(0.05)  # record and the other run's never share one
            other = start_(env, "/document", "--key", "ACME-1", "--resume")  # this run's remake, named by none
            mine = raw(env, "/document")
            parked = [n for n in names_of(env, "/document") if n != "document.json"]
            theirs = shell(nxt, env) if nxt else {}
            got = (before.get("stage") in START_STAGES, before.get("call_returned"),
                   (other.get("print") or [None])[0] == env_line(r.path), other.get("error"), other.get("replaced"),
                   other.get("started") not in (None, a), parked)
            check(got == (True, True, True, None, {"command": "/document", "started": a, "parked": True}, True,
                          ["document.%s.json" % stamp_of(a or "")]),
                  "t_resume_unnamed_other_run: a continuation given no --started meets another run's record marked true "
                  "as a plain start does -- it parks it and starts afresh (%r)" % (got,))
            check(theirs.get("error") is None and theirs.get("started") == a and raw(env, "/document") == mine,
                  "t_resume_unnamed_other_run: the other run's next, by its --started, goes on with its own record, "
                  "this run's untouched (%r)" % ({k: theirs.get(k) for k in ("started", "replaced", "error")},))

        case("t_resume_unnamed_other_run", t_resume_unnamed_other_run)

        # A start that returned a start --resume next, made past resumable's 15 minutes -- a replay that hung to its
        # timeout, then another call: the next names the record by --started, so the resume, starting afresh, takes the
        # record over (started_before, replaced null) rather than setting it aside, and a run typed under it still reads
        # it as standing -- the here row, nothing pushed
        def t_midrun_open_next_aged():
            r, env = mworld("t-midrun-open-next-aged")
            ahead(r, "t-midrun-open-next-aged-other")  # a unit of capped calls, so --budget 0 stops with a next
            first = start_(env, "/document", "--key", "ACME-1", "--budget", "0")
            a, nxt = first.get("started"), (first.get("next") or {}).get("run") or ""
            path = file_of(env, "/document")
            rec = json.load(open(path, encoding="utf-8"))
            rec["updated"] = time.strftime(STAMP_FMT, time.gmtime(time.time() - 1200))  # past resumable's 15 minutes
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(rec, fh)
            f = start_(env, "/feedback")
            up = on_origin(r)
            while time.strftime(STAMP_FMT, time.gmtime()) <= (a or ""):  # the take-over's own stamp a later second, so
                time.sleep(0.05)  # only started_before, never a shared stamp, can name it by <a>
            again = shell(nxt, env) if nxt else {}
            taken = rec_of(env, "/document")
            chain = follow(again, env)
            r.write(FB, "fb\n")
            e = run_end(env, "/feedback")
            got = (" start --command /document " in nxt and nxt.endswith(" --resume"), rec.get("stage") in START_STAGES,
                   (f.get("midrun") or {}).get("started") == a, "replaced" in again, again.get("replaced"),
                   again.get("started") not in (None, a), taken.get("started_before") == [a], chain[-1].get("error"),
                   e.get("row"), e.get("pushed"), on_origin(r) == up)
            check(got == (True, True, True, True, None, True, True, None, "here", False, True),
                  "t_midrun_open_next_aged: the next, made past 15 minutes, takes its record over -- started_before "
                  "[the first start's stamp], replaced null -- and the run typed under it still reads it as standing "
                  "(%r, %r)" % (got, nxt))

        case("t_midrun_open_next_aged", t_midrun_open_next_aged)

        # The file a cut-off re-run leaves behind outlives no save over the record that lists its stamp: the second
        # run's end restores the re-run's record (unpark, no clean-up), a third plain start of the command saves its own
        # record over it -- not an open run, protects false -- and the file left behind goes with it, so the third
        # run's end restores nothing
        def t_rerun_cut_off_overwritten():
            r, env = mworld("t-rerun-cut-off-over")
            start_(env, "/document", "--key", "ACME-1")
            a = backdate(env, "/document", 360)
            start_(env, "/document", "--key", "ACME-1")
            b = backdate(env, "/document", 240)
            old_name = "document.%s.json" % stamp_of(a)
            old_raw = raw(env, "/document", old_name)
            follow(start_(env, "/document", *RERUN_KEYS, "--rerun", "--started", a), env)
            with open(file_of(env, "/document", old_name), "wb") as fh:  # the old file, as the cut-off leaves it
                fh.write(old_raw or b"")
            r.write(FB, "fb\n")
            run_end(env, "/document", "--started", b)  # unpark: the re-run's record back to <command>.json
            restored = rec_of(env, "/document")
            third = start_(env, "/document", "--key", "ACME-1")
            after_third = names_of(env, "/document")
            e = run_end(env, "/document", "--started", third.get("started") or "")
            check(old_raw is not None and restored.get("started_before") == [a] and restored.get("protects") is False
                  and (third.get("replaced") or {}).get("parked") is False and old_name not in after_third
                  and after_third == ["document.json"] and e.get("error") is None and names_of(env, "/document") == [],
                  "t_rerun_cut_off_overwritten: the third start's save over the re-run's record takes the file left "
                  "behind with it, and its end restores nothing (%r, %r)" % (after_third, names_of(env, "/document")))

        case("t_rerun_cut_off_overwritten", t_rerun_cut_off_overwritten)

        # N2: every start-side next repeats --started -- the flush's replay and the resume after it, the held stage's
        # replay of <default>, and the settle loop's queued replay -- so a parked run's re-run never touches the second
        # run's <command>.json and ends at done on its own record
        def t_park_rerun_replays():
            def chain(name, setup, keys=("--key", "ACME-1")):
                r, env = mworld(name, branch=LB if name.endswith("held") else None)
                start_(env, "/document", *keys)
                a = backdate(env, "/document", 240)
                start_(env, "/document", *keys)
                backdate(env, "/document", 120)
                b_raw = raw(env, "/document")
                setup(r, name)
                calls = follow(start_(env, "/document", *keys, "--rerun", "--started", a), env)
                new = calls[0].get("started") or a
                nexts = [c["next"]["run"] for c in calls if (c.get("next") or {}).get("run")]
                path = file_of(env, "/document", "document.%s.json" % stamp_of(new))
                rec = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
                return r, nexts, new, rec, raw(env, "/document") == b_raw, calls

            def local_commit(r, branch, path):  # an unpushed session-file commit on <branch>, HEAD left where it was
                here = on(r)
                if branch != here:
                    r.git("switch", "-q", branch)
                r.write(path, "local\n")
                r.commit_all(SUBJECT % ("NOISSUE", "/feedback"))
                if branch != here:
                    r.git("switch", "-q", here)

            def flush(r, name):  # main diverged from origin's: the flush's push is rejected
                local_commit(r, "main", "specifications/PRD-ACME-1-x/dev-workflows/feedback/local.md")
                ahead(r, name + "-other")

            def held(r, name):  # HEAD on prd/B-2-y, main diverged from origin's: the held stage's push of main
                local_commit(r, "main", "specifications/PRD-ACME-1-x/dev-workflows/feedback/local.md")
                ahead(r, name + "-other")

            def settle(r, name):  # another plugin branch diverged from its origin copy: the settle loop queues it
                r.git("branch", "prd/C-3-z", "main")
                r.git("push", "-q", "-u", "origin", "prd/C-3-z")
                o = clone(r, name + "-other")
                o.git("switch", "-q", "prd/C-3-z")
                o.write("specifications/PRD-C-3-z/o.md", "o\n")
                o.commit_all(SUBJECT % ("NOISSUE", "/other"))
                o.git("push", "-q", "origin", "prd/C-3-z")
                local_commit(r, "prd/C-3-z", "specifications/PRD-C-3-z/dev-workflows/feedback/l.md")

            for name, setup, keys, want in (
                    ("t-park-rerun-flush", flush, ("--key", "ACME-1"), "replay --for start --command /document --branch main"),
                    ("t-park-rerun-held", held, ("--key", "B-2"), "replay --for start --command /document --branch main"),
                    ("t-park-rerun-settle", settle, ("--key", "ACME-1"),
                     "replay --for start --command /document --branch prd/C-3-z")):
                r, nexts, new, rec, b_same, calls = chain(name, setup, keys)
                check(len(nexts) >= 2 and any(want in x for x in nexts) and any("--resume" in x for x in nexts)
                      and all(("--started " + new) in x for x in nexts) and b_same and rec.get("stage") == "done"
                      and calls[-1].get("error") is None,
                      "t_park_rerun_replays: %s -- each next repeats --started, the chain ends at done on the re-run's "
                      "own record, the second's untouched (%r)" % (name, nexts))

        case("t_park_rerun_replays", t_park_rerun_replays)

        # N1: a re-run that finds no record of its own -- its parked record dropped at the second run's end -- reads
        # the open runs as a first start does, and takes no snapshot, as no re-run does
        def t_midrun_rerun_no_record():
            r, env = mworld("t-midrun-rerun-no-record")
            start_(env, "/document", "--key", "ACME-1")
            a = backdate(env, "/document", 240)
            start_(env, "/document", "--key", "ACME-9")
            b = backdate(env, "/document", 120)
            r.git("switch", "-q", "-c", "prd/ACME-9-x")  # the second run's own handoff
            run_end(env, "/document", "--started", b)
            age(r)  # the handoff before the third run's start, as a run typed a moment later finds it
            dropped = not os.path.exists(file_of(env, "/document", "document.%s.json" % stamp_of(a)))
            c = start_(env, "/specify", "--key", "ACME-9")
            again = start_(env, "/document", "--key", "ACME-1", "--key", "B-2", "--rerun", "--started", a)
            check(dropped and (again.get("midrun") or {}).get("started") == c.get("started")
                  and again.get("start_dirty") is None,
                  "t_midrun_rerun_no_record: no record of its own, so the open runs read as a first start reads them, "
                  "no snapshot taken (%r)" % again)

        case("t_midrun_rerun_no_record", t_midrun_rerun_no_record)

        # A start --resume that runs fresh -- its record past resumable's 15 minutes -- takes over its own record, which
        # the next names by --started, and never parks it: the record is the same run's
        def t_resume_stale_no_park():
            r, env = mworld("t-resume-stale-no-park")
            ahead(r, "t-resume-stale-no-park-other")
            first = start_(env, "/specify", "--budget", "0")
            path = file_of(env, "/specify")
            rec = json.load(open(path, encoding="utf-8"))
            rec["updated"] = time.strftime(STAMP_FMT, time.gmtime(time.time() - 1200))
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(rec, fh)
            got = shell(first["next"]["run"], env) if (first.get("next") or {}).get("run") else {}
            sdir = os.path.dirname(path)
            taken = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
            check(rec.get("stage") in START_STAGES and "replaced" in got and got.get("replaced") is None
                  and taken.get("started_before") == [first.get("started")]
                  and sorted(os.listdir(sdir)) == ["specify.json"],
                  "t_resume_stale_no_park: a resume run fresh takes over its own record, parking none (%r, %r)"
                  % (got.get("replaced"), taken.get("started_before")))

        case("t_resume_stale_no_park", t_resume_stale_no_park)

        # M3, R1: on a branch a key names, the here form's refused clause names HEAD's branch in <default>
        def e_midrun_kept_b3():
            r, env = mworld("e-midrun-kept-b3", branch=SPEC)
            # a block-shaped file, which goes with the run's change (§4 step 1 (1)); an overwritten one already
            # uncommitted at the start would be left out by the guard, never refused
            resume = "specifications/PRD-ACME-1-x/dev-workflows/feedback/r.md"
            r.write(resume, "r1\n")
            r.commit_all("ACME-1-01 resume")
            r.git("push", "-q", "origin", SPEC)
            age(r)
            start_(env, "/specify", "--key", "ACME-1-01")
            r.write(resume, "r2, in progress\n")
            start_(env, "/feedback", "--key", "ACME-1")
            os.remove(os.path.join(r.path, resume))
            old = head(r)
            e = run_end(env, "/feedback")
            clause = lines.fill("reason.land.deleted", {"<path>": resume, "<default>": SPEC})
            check(e.get("row") == "midrun-kept" and e.get("print") == [kept_row(SPEC, clause, keys="ACME-1-01")] and head(r) == old,
                  "e_midrun_kept_b3: the refused clause names HEAD's branch (%r)" % e)

        case("e_midrun_kept_b3", e_midrun_kept_b3)

        # M3, R5: once the open run no longer stands, steps 2-4 catch up on main before they commit, so the push goes
        # with no replay
        def e_midrun_kept_ended_catch_up():
            r, env = mworld("e-midrun-kept-ended-catch-up", follow="- [ ] a\n")
            start_(env, "/specify", "--key", "ACME-1")
            append(r, FUP, "- [ ] s\n")
            up = ahead(r, "e-midrun-kept-ended-catch-up-other")
            start_(env, "/feedback")
            r.write(FUP, "- [ ] a\n- [x] s\n- [ ] f\n")
            r.write(FB, "fb\n")
            drop(env, "/specify")
            e = run_end(env, "/feedback")
            check(e.get("row") == "pushed-default" and e.get("next") is None and r.git("rev-parse", "HEAD^") == up
                  and on_origin(r) == head(r),
                  "e_midrun_kept_ended_catch_up: the catch-up, then the push, no replay (%r)" % e)

        case("e_midrun_kept_ended_catch_up", e_midrun_kept_ended_catch_up)

        # M3, R2: an end --no-preflight whose --started names the run's own open <command>.json excludes it from P5's
        # test, and commits
        def e_no_preflight_named():
            r, env = mworld("e-no-preflight-named")
            s0 = start_(env, "/specify")
            r.write(FB, "fb\n")
            e = run_end(env, "/specify", "--no-preflight", "--started", s0.get("started"))
            check(e.get("record") == "ignored" and e.get("row") == "pushed-default" and on_origin(r) == head(r),
                  "e_no_preflight_named: the record --started names is no open run beside itself (%r)" % e)

        case("e_no_preflight_named", e_no_preflight_named)

        # t_midrun_abandoned (Review Focus 5): /specify open on prd/B-2-y, never ended; three commands after it each
        # stay, name it, and land their own file
        def t_midrun_abandoned():
            r, env = mworld("t-midrun-abandoned", branch=LB)
            start_(env, "/specify", "--key", "B-2")
            r.write(FUP, "- [ ] specify's\n")
            for k, cmd in enumerate(("/feedback", "/create-ard", "/idea")):
                got = start_(env, cmd)
                path = "specifications/PRD-ACME-1-x/dev-workflows/feedback/f%d.md" % k
                r.write(path, "f\n")
                e = run_end(env, cmd)
                m = rev(r, "main")
                check(stay_line(LB) in (got.get("print") or []) and on(r) == LB
                      and e.get("print") == [pushed_default(m[:7], r.path) + landed_app(LB)] and changed(r, m) == [path]
                      and read(r, FUP) == "- [ ] specify's\n",
                      "t_midrun_abandoned: %s stays naming /specify and lands its own file (%r)" % (cmd, e))

        case("t_midrun_abandoned", t_midrun_abandoned)

        # t_midrun_misrooted (P14): misrooted and an open run -- the misrooted line alone
        def t_midrun_misrooted():
            r, env = mworld("t-midrun-misrooted", branch=LB)
            seed(env, "/specify", branch=LB, keys=["B-2"])
            sub = os.path.join(r.path, "sub")
            os.makedirs(sub)
            got = start_(env, "/feedback", specs=sub)
            stay = lines.fill("pre.stay", {"<branch>": LB, "<default>": "main",
                                           lines.placeholder("pre.stay", "<switched"): 1})
            check(got.get("specs_git") == "misrooted" and got.get("midrun") and stay in (got.get("print") or [])
                  and not any("is still open on it" in x for x in got.get("print") or []) and on(r) == LB,
                  "t_midrun_misrooted: one stay line, the misrooted one (%r)" % got)

        case("t_midrun_misrooted", t_midrun_misrooted)

        # t_midrun_mode: B4 under a run typed mid-run in session-branch mode -- the mid-run stay line, no switch; the
        # mode's commit carrying the open run's in-progress file, as the spec's non-goal says
        def t_midrun_mode():
            r, env = mworld("t-midrun-mode", branch=LB)
            r.git("config", "workflows.sessionBranch", "true")
            env = dict(env, GIT_USER_INITIALS="ab")
            start_(env, "/specify", "--key", "B-2")
            r.write(FUP, "- [ ] specify's\n")
            got = start_(env, "/feedback")
            r.write(FB, "fb\n")
            e = run_end(env, "/feedback")
            check(stay_line(LB) in (got.get("print") or []) and on(r) == LB and got.get("stay") is None
                  and e.get("row") == "pushed-session"
                  and FUP in r.git("diff", "--name-only", "main", "refs/heads/session/ab").split(),
                  "t_midrun_mode: no switch, the mode's commit carrying the open run's file (%r, %r)" % (got, e))

        case("t_midrun_mode", t_midrun_mode)

        def t_midrun_mode_catch_up():
            """In session-branch mode, the typed run's end makes no catch-up while the open run stands on main."""
            r, env = mworld("t-midrun-mode-catch-up")
            r.git("config", "workflows.sessionBranch", "true")
            env = dict(env, GIT_USER_INITIALS="ab")
            start_(env, "/specify")
            old = head(r)
            o = clone(r, "t-midrun-mode-catch-up-other")
            o.write("specifications/PRD-ACME-1-x/notes-other.md", "o\n")
            o.commit_all("ACME-1 Other work")
            o.git("push", "-q", "origin", "main")
            f = start_(env, "/feedback")
            r.write(FB, "fb\n")
            e = run_end(env, "/feedback")
            check(f.get("midrun") and head(r) == old and e.get("row") == "pushed-session",
                  "t_midrun_mode_catch_up: no pull at the start or the end in the mode (%r)" % e)

        case("t_midrun_mode_catch_up", t_midrun_mode_catch_up)

        def t_park_replay():
            """P19: the first run's end, on its parked record, hands a rejected push to the replay, whose next repeats
            --started: the replay ends on that record, <command>.json untouched."""
            r, env = mworld("t-park-replay")
            start_(env, "/specify")
            first = backdate(env, "/specify")
            start_(env, "/specify")
            second_raw = raw(env, "/specify")
            o = clone(r, "t-park-replay-other")
            o.write("specifications/PRD-ACME-1-x/dev-workflows/feedback/o.md", "o\n")
            o.commit_all(SUBJECT % ("NOISSUE", "/other"))
            o.git("push", "-q", "origin", "main")
            r.write(FB, "fb\n")
            e = run_end(env, "/specify", "--started", first)
            nxt = (e.get("next") or {}).get("run") or ""
            rp = shell(nxt, env) if nxt else {}
            parked_file = file_of(env, "/specify", "specify.%s.json" % stamp_of(first))
            check(("--started " + first) in nxt and rp.get("row") == "replayed" and not os.path.exists(parked_file)
                  and raw(env, "/specify") == second_raw and on_origin(r) == head(r),
                  "t_park_replay: the replay names --started and ends on the parked record (%r, %r)" % (e, rp))

        case("t_park_replay", t_park_replay)

        def t_started_missing_end():
            """P35: an end --started whose stamp names no record (kind missing) saves at the run's derived path, its
            started the stamp -- here kept at stage end-replay by a rejected push -- and the replay its next names ends
            there."""
            r, env = mworld("t-started-missing-end")
            o = clone(r, "t-started-missing-end-other")
            o.write("specifications/PRD-ACME-1-x/dev-workflows/feedback/o.md", "o\n")
            o.commit_all(SUBJECT % ("NOISSUE", "/other"))
            o.git("push", "-q", "origin", "main")
            r.write(FB, "fb\n")
            stamp = "2026-11-10T10:00:00Z"
            e = run_end(env, "/feedback", "--started", stamp)
            derived = file_of(env, "/feedback", "specify.json").replace("specify.json", "feedback.%s.json" % stamp_of(stamp))
            drec = json.load(open(derived, encoding="utf-8")) if os.path.exists(derived) else {}
            rp = shell((e.get("next") or {}).get("run") or "true", env)
            check(e.get("record") == "missing" and drec.get("started") == stamp and drec.get("stage") == "end-replay"
                  and raw(env, "/feedback") is None and rp.get("row") == "replayed" and not os.path.exists(derived),
                  "t_started_missing_end: saved and removed at the derived path, its started the stamp (%r, %r)"
                  % (e, drec))

        case("t_started_missing_end", t_started_missing_end)

        # I2 (final review): for a run typed mid-run, an overwritten file the open run had uncommitted when the typed
        # run started stays out of the typed run's change -- neither landed, lifted nor committed there -- however the
        # open run rewrites it before that end, and the line leaves it for a later commit (app.start-dirty-kept); an
        # appended file's entries added since the start still travel. Both forms: the landing (a mid-run stay) and the
        # here form
        RES = "specifications/PRD-ACME-1-x/dev-workflows/resume.md"
        COST = "specifications/PRD-ACME-1-x/dev-workflows/cost/s.md"
        CENTRY = "## 2026-11-12T10:0%d:00Z — /specify — p%d\n\nentry %d\n"
        COST1 = "# cost\n\n" + CENTRY % (0, 1, 1)

        def kept_app(paths, branch):
            """app.start-dirty-kept (P2): the paths the guard left out, left for a later commit on <branch>."""
            return lines.fill("app.start-dirty-kept", {"<path>": paths, "<branch>": branch})

        def t_midrun_open_writes(here):
            name = "t-midrun-open-writes-" + ("here" if here else "stay")
            r, env = mworld(name, branch=None if here else SPEC)
            s = start_(env, "/specify", "--key", "ACME-1" if here else "ACME-1-01")
            r.write(RES, "resume v1\n")
            r.write(COST, COST1)
            up, base = on_origin(r), head(r)
            f = start_(env, "/feedback")
            r.write(RES, "resume v2\n")  # the open run goes on after /feedback's start: a rewrite, and an entry appended
            append(r, COST, "\n" + CENTRY % (5, 2, 2))
            r.write(FB, "## 2026-11-12 — /feedback — note\n\nmine\n")
            e = run_end(env, "/feedback")
            c = head(r) if here else rev(r, "main")
            line = e.get("line") or ""
            ok = (sorted(f.get("start_dirty") or {}) == sorted([COST, RES]) and changed(r, c) == sorted([COST, FB])
                  and read(r, RES) == "resume v2\n" and "entry 2" in show(r, c, COST)
                  and "entry 1" not in show(r, c, COST) and line.endswith(kept_app([RES], "main" if here else SPEC))
                  and cached(r) == "")
            if here:
                ok = (ok and e.get("row") == "here" and e.get("pushed") is False and on_origin(r) == up
                      and line == here_row(c[:7], 2, "main", keys="ACME-1") + kept_app([RES], "main"))
            else:
                ok = (ok and e.get("row") == "pushed-default" and on(r) == SPEC and rev(r, SPEC) == base
                      and line == pushed_default(c[:7], r.path, 2) + landed_app(SPEC) + kept_app([RES], SPEC)
                      and on_origin(r) == c and read(r, COST) == COST1)
            check(ok, "%s: the open run's rewritten resume pointer stays out of the change, its newer version in the "
                      "working tree, the line naming it; its appended cost entry travels (%r, %r)" % (name, f, e))
            e = run_end(env, "/specify", "--started", s.get("started"))
            h = head(r)
            check(e.get("error") is None and RES in changed(r, h) and show(r, h, RES) == "resume v2",
                  "%s: the open run's own end commits its resume pointer as it stands (%r)" % (name, e))

        case("t_midrun_open_writes_stay", lambda: t_midrun_open_writes(False))
        case("t_midrun_open_writes_here", lambda: t_midrun_open_writes(True))

        # M1 (the user's decision, 2026-11-12): the same command typed again with another run key set keeps the first
        # run protected -- its record parked, still protecting, and read as the open run -- so the second run commits
        # none of the first run's files and switches nothing; the two end in either order, each by its own record
        def t_same_command_other_key(order):
            name = "t-same-command-other-key-" + order
            r, env = mworld(name, branch=SPEC)
            s = start_(env, "/specify", "--key", "ACME-1-01")
            r.write(COST, COST1)  # the first run's file, in progress
            first = backdate(env, "/specify")
            tip, up = rev(r, SPEC), on_origin(r, SPEC)
            b = start_(env, "/specify", "--key", "B-2")
            parked = rec_of(env, "/specify", "specify.%s.json" % stamp_of(first))
            check(s.get("midrun") is None and b.get("print") == [env_line(r.path), stay_line(SPEC)] and on(r) == SPEC
                  and rev(r, SPEC) == tip and on_origin(r, SPEC) == up
                  and b.get("midrun") == {"command": "/specify", "started": first, "branch": SPEC, "keys": ["ACME-1-01"]}
                  and (b.get("replaced") or {}).get("parked") is True and parked.get("protects") is True
                  and (b.get("stay") or {}).get("kind") == "mid-run" and read(r, COST) == COST1,
                  "%s: the second start stays, commits none of the first run's file, parks its record still protecting "
                  "and reads it as its open run (%r, %r)" % (name, b, parked))
            r.write(FB, "## 2026-11-12 — /specify — note\n\nmine\n")
            second, m0 = b.get("started"), rev(r, "main")
            got = {}
            for who in (("second", "first") if order == "second-first" else ("first", "second")):
                got[who] = run_end(env, "/specify", "--started", second if who == "second" else first)
                if who == "second" and order == "second-first":
                    got["restored"] = rec_of(env, "/specify")
            m, h = rev(r, "main"), rev(r, SPEC)
            ok = (all(got[w].get("error") is None and got[w].get("record") == "found" for w in ("first", "second"))
                  and [n for n in names_of(env, "/specify") if n != "specify.json"] == [] and rec_of(env, "/specify") == {}
                  and on(r) == SPEC)
            if order == "second-first":
                ok = (ok and got["second"].get("row") == "pushed-default" and changed(r, m) == [FB]
                      and got["restored"].get("started") == first and got["restored"].get("protects") is True
                      and got["first"].get("row") == "pushed-plugin" and changed(r, h) == [COST] and on_origin(r, SPEC) == h)
            else:
                ok = (ok and got["first"].get("row") == "pushed-plugin" and changed(r, h) == sorted([COST, FB])
                      and got["second"].get("row") == "nothing" and m == m0)
            check(ok, "%s: each end finds its own record; the first's commits its file on its own branch (%r)"
                  % (name, got))

        case("t_same_command_other_key_second_first", lambda: t_same_command_other_key("second-first"))
        case("t_same_command_other_key_first_second", lambda: t_same_command_other_key("first-second"))

        # M1: the same run key set, in any order, or either start keyless, is a restart -- the first run's record parked
        # protecting nothing, and the second run not typed under it; the second run's own record protects the branch
        def t_same_command_restart():
            got = {}
            for name, k1, k2, branch in (("same-key", ("--key", "ACME-1-01", "--key", "ACME-1"),
                                          ("--key", "ACME-1", "--key", "ACME-1-01"), SPEC),
                                         ("keyless-second", ("--key", "ACME-1"), (), None),
                                         ("keyless-first", (), ("--key", "B-2"), None)):
                r, env = mworld("t-same-command-restart-" + name, branch=branch)
                start_(env, "/specify", *k1)
                first = backdate(env, "/specify")
                b = start_(env, "/specify", *k2)
                parked = rec_of(env, "/specify", "specify.%s.json" % stamp_of(first))
                f = start_(env, "/feedback")
                got[name] = (b.get("midrun"), (b.get("replaced") or {}).get("parked"), parked.get("protects"),
                             (f.get("midrun") or {}).get("started") == b.get("started"))
            check(got == {n: (None, True, False, True) for n in ("same-key", "keyless-second", "keyless-first")},
                  "t_same_command_restart: a restart parks the first run's record protecting nothing, and a later "
                  "command is typed under the second run alone (%r)" % got)

        case("t_same_command_restart", t_same_command_restart)

        # M1: a retype of a run whose record is parked already -- K1 open, K2 typed with another key set, then K1's key
        # set typed again -- ends K1's protection, its parked record marked so in place; K2 stays protected and is the
        # open run the third start is typed under
        def t_same_command_restarts_parked():
            r, env = mworld("t-same-command-restarts-parked")
            start_(env, "/specify", "--key", "ACME-1")
            k1 = backdate(env, "/specify", 240)
            start_(env, "/specify", "--key", "B-2")
            k2 = backdate(env, "/specify", 120)
            c = start_(env, "/specify", "--key", "ACME-1")
            p1 = rec_of(env, "/specify", "specify.%s.json" % stamp_of(k1))
            p2 = rec_of(env, "/specify", "specify.%s.json" % stamp_of(k2))
            check(p1.get("parked") is True and p1.get("protects") is False and p2.get("parked") is True
                  and p2.get("protects") is True and (c.get("midrun") or {}).get("started") == k2,
                  "t_same_command_restarts_parked: K1's parked record protects nothing once K1 is typed again; K2 "
                  "stays protecting and is the third run's open run (%r, %r, %r)" % (p1.get("protects"),
                                                                                     p2.get("protects"), c.get("midrun")))

        case("t_same_command_restarts_parked", t_same_command_restarts_parked)

        # P37 (M2): an end with no start and no --started never writes or removes a record a start made at
        # <command>.json -- another run's -- on the misrooted path, the silent one or the ordinary one, which commits;
        # it keeps its own at a derived path and removes it, and the first run's end still finds its record
        def t_no_start_end_beside():
            got = {}
            for path in ("misrooted", "silent", "ordinary"):
                name = "t-no-start-beside-" + path
                r, env = mworld(name)
                s = start_(env, "/specify", "--key", "ACME-1")
                before = raw(env, "/specify")
                if path == "misrooted":
                    e = run_end(env, "/specify", "--no-preflight", "--misrooted-stdin", stdin=b"a notice\n")
                elif path == "silent":
                    e = run_end(env, "/specify", "--no-preflight", specs=os.path.join(tmp, name + "-nowhere"))
                else:  # HEAD left main and came back since the first run's start: that run is open no longer
                    r.git("switch", "-q", "-c", "feature/x")
                    r.git("switch", "-q", "main")
                    r.write(FB, "fb\n")
                    e = run_end(env, "/specify", "--no-preflight")
                after, left = raw(env, "/specify"), [n for n in names_of(env, "/specify") if n != "specify.json"]
                then = run_end(env, "/specify", "--started", s.get("started"))
                got[path] = (e.get("row"), e.get("record"), before is not None and after == before, left,
                             then.get("record"), then.get("error"))
            check(got == {"misrooted": ("misrooted", "ignored", True, [], "found", None),
                          "silent": ("silent", "ignored", True, [], "found", None),
                          "ordinary": ("pushed-default", "ignored", True, [], "found", None)},
                  "t_no_start_end_beside: the first run's record byte for byte, no file of the end's left, and the "
                  "first run's end finds its own (%r)" % got)

        case("t_no_start_end_beside", t_no_start_end_beside)

        # The unnamed-resume edge (final review, Declined to judge): a record an end restores from parked is marked
        # call_returned true -- its start, stopped by the harness, was overtaken by the later start that parked it -- so
        # another run's continuation given no --started, made with the same arguments within 15 minutes, meets it as a
        # plain start does, never going on with the dead run's record
        def t_resume_unnamed_restored():
            r, env = mworld("t-resume-unnamed-restored")
            start_(env, "/specify", "--key", "ACME-1")
            a = backdate(env, "/specify", 240)
            with in_env(env):  # the harness stopped that start mid-preflight: its record marked false, at a start stage
                session = env["CLAUDE_CODE_SESSION_ID"]
                rec = state.load(session, "/specify")
                rec.update(call_returned=False, stage="flush")
                state.save(session, "/specify", rec)
            b = start_(env, "/specify", "--key", "ACME-1")
            run_end(env, "/specify", "--started", b.get("started"))
            restored = rec_of(env, "/specify")
            c = start_(env, "/specify", "--key", "ACME-1", "--resume")
            mine = rec_of(env, "/specify")
            check(restored.get("started") == a and restored.get("call_returned") is True and c.get("error") is None
                  and c.get("started") not in (None, a) and (c.get("replaced") or {}).get("started") == a
                  and mine.get("started_before") == [] and mine.get("protects") is True,
                  "t_resume_unnamed_restored: the restored record marked returned; the continuation starts afresh and "
                  "sets it aside (%r, %r, %r)" % ({k: restored.get(k) for k in ("started", "call_returned")},
                                                  {k: c.get(k) for k in ("started", "replaced", "error")},
                                                  {k: mine.get(k) for k in ("started_before", "protects")}))

        case("t_resume_unnamed_restored", t_resume_unnamed_restored)

        # N1 (final re-review; ruling (a), then P1's): §4 step 1 (1)'s guard is on whatever stands at a run's end. The re-review's s3: K1 open on SPEC with its resume pointer in progress; K2 typed
        # with another key set, a mid-run stay under K1; K1's key set typed again, a restart, under K2, so K1's parked
        # record protects nothing; the restart rewrites the pointer. In either end order the middle run, K2, leaves the
        # pointer out and the working copy keeps v2: its line names the restart's command where the restart still
        # stands, and leaves the pointer for a later commit on SPEC where none does. The restart, typed under K2, leaves
        # its own rewrite out too -- the rule's cost -- so v2 stays uncommitted on SPEC, for the branch's next commit
        def t_guard_s3(order):
            name = "t-guard-s3-" + order
            r, env = mworld(name, branch=SPEC)
            start_(env, "/specify", "--key", "ACME-1-01")
            r.write(RES, "resume v1\n")
            backdate(env, "/specify", 240)
            start_(env, "/specify", "--key", "B-2")
            k2 = backdate(env, "/specify", 120)
            r.write(FB, "## 2026-11-12 — /specify — note\n\nB-2's\n")  # K2's own file, before the restart starts
            c = start_(env, "/specify", "--key", "ACME-1-01")
            r.write(RES, "resume v2\n")
            main0 = rev(r, "main")
            ends = ("middle", "restart") if order == "middle-first" else ("restart", "middle")
            got = {}
            for who in ends:
                got[who] = run_end(env, "/specify", "--started", k2 if who == "middle" else c.get("started"))
                got[who + "-wc"] = read(r, RES)
            m = rev(r, "main")
            middle, restart = got["middle"].get("line") or "", got["restart"].get("line") or ""
            named = kept_app([RES], SPEC)
            ok = (c.get("midrun", {}).get("started") == k2 and got["middle-wc"] == got["restart-wc"] == "resume v2\n"
                  and got["middle"].get("record") == got["restart"].get("record") == "found"
                  and got["middle"].get("row") == "pushed-default" and m != main0 and changed(r, m) == [FB]
                  and middle.endswith(landed_app(SPEC) + named) and got["restart"].get("row") == "nothing"
                  and show(r, SPEC, RES) == "" and on(r) == SPEC
                  and RES in r.git("status", "--porcelain", "--untracked-files=all"))
            want_restart = T["row.nothing"] + kept_app([RES], SPEC)
            check(ok and restart == want_restart,
                  "%s: the middle run leaves the restarted run's pointer out in either end order, the working copy at "
                  "v2, and the restart, typed under it, leaves its own rewrite out too (%r)" % (name, got))

        case("t_guard_s3_middle_first", lambda: t_guard_s3("middle-first"))
        case("t_guard_s3_restart_first", lambda: t_guard_s3("restart-first"))

        # N1, ruling (a): a run typed mid-run whose open run has ended before its end -- here, an abandoned run's record
        # dropped, as prune or a /clear leaves it -- still leaves a snapshot path of an overwritten class out of its
        # change, in the landing and in the here form, and leaves it for a later commit on its branch
        def t_guard_open_run_ended():
            got = {}
            for form in ("stay", "here"):
                r, env = mworld("t-guard-ended-" + form, branch=SPEC if form == "stay" else None)
                start_(env, "/specify", "--key", "ACME-1-01" if form == "stay" else "ACME-1")
                r.write(RES, "resume v1\n")
                f = start_(env, "/feedback")
                r.write(RES, "resume v2\n")
                r.write(FB, "## 2026-11-12 — /feedback — note\n\nmine\n")
                drop(env, "/specify")
                e = run_end(env, "/feedback")
                branch = SPEC if form == "stay" else "main"
                c = rev(r, "main")
                got[form] = (bool(f.get("midrun")), e.get("row"), changed(r, c), read(r, RES),
                             (e.get("line") or "").endswith(kept_app([RES], branch)))
            check(got == {"stay": (True, "pushed-default", [FB], "resume v2\n", True),
                          "here": (True, "pushed-default", [FB], "resume v2\n", True)},
                  "t_guard_open_run_ended: the pointer left out though the open run has ended, left for a later commit "
                  "on the branch (%r)" % got)

        case("t_guard_open_run_ended", t_guard_open_run_ended)

        # P1 (final re-review 2; the coordinator's ruling): the guard is on for every landing and here form, typed
        # mid-run or not. The re-review's s4: on SPEC, the resume pointer uncommitted and README.md edited (G1), an
        # untyped /feedback holding a stay; /specify typed under it rewrites the pointer. In either end order neither
        # run lands or commits the pointer, and the working copy keeps v2
        def t_guard_s4(order):
            name = "t-guard-s4-" + order
            r, env = mworld(name, branch=SPEC)
            r.write(RES, "resume v1\n")
            append(r, "README.md", "stray\n")
            f = start_(env, "/feedback")
            r.write(FB, "## 2026-11-12 — /feedback — note\n\nmine\n")
            s = start_(env, "/specify", "--key", "ACME-1-01")
            r.write(RES, "resume v2\n")
            main0 = rev(r, "main")
            ends = ("/specify", "/feedback") if order == "later-first" else ("/feedback", "/specify")
            got = {}
            for cmd in ends:
                got[cmd] = run_end(env, cmd, "--started", (s if cmd == "/specify" else f).get("started"))
                got[cmd + "-wc"] = read(r, RES)
            m = rev(r, "main")
            fb_line, sp_line = got["/feedback"].get("line") or "", got["/specify"].get("line") or ""
            ok = (f.get("midrun") is None and (f.get("stay") or {}).get("reason") == "g1"
                  and (s.get("midrun") or {}).get("command") == "/feedback"
                  and got["/feedback-wc"] == got["/specify-wc"] == "resume v2\n"
                  and got["/feedback"].get("row") == "pushed-default" and m != main0 and changed(r, m) == [FB]
                  and fb_line.endswith(kept_app([RES], SPEC)) and got["/specify"].get("row") == "nothing"
                  and sp_line == T["row.nothing"] + kept_app([RES], SPEC)
                  and show(r, SPEC, RES) == "" and RES in r.git("status", "--porcelain", "--untracked-files=all"))
            check(ok, "%s: neither the untyped stayed run nor the run typed under it takes the pointer, in this end "
                      "order; the working copy at v2 (%r)" % (name, got))

        case("t_guard_s4_later_first", lambda: t_guard_s4("later-first"))
        case("t_guard_s4_untyped_first", lambda: t_guard_s4("untyped-first"))

        # P1: an untyped stayed run alone -- no run open beside it -- rewriting an overwritten file already uncommitted
        # at its start: the landing leaves it out, in the working tree for a later commit on the branch, the rule's cost
        def t_guard_untyped_alone():
            r, env = mworld("t-guard-untyped-alone", branch=SPEC)
            r.write(RES, "resume v1\n")
            append(r, "README.md", "stray\n")
            f = start_(env, "/feedback")
            r.write(RES, "resume v2\n")
            r.write(FB, "## 2026-11-12 — /feedback — note\n\nmine\n")
            e = run_end(env, "/feedback")
            m = rev(r, "main")
            check(f.get("midrun") is None and (f.get("stay") or {}).get("kind") == "unkeyed"
                  and e.get("row") == "pushed-default" and changed(r, m) == [FB] and read(r, RES) == "resume v2\n"
                  and (e.get("line") or "").endswith(kept_app([RES], SPEC)) and show(r, m, RES) == "",
                  "t_guard_untyped_alone: the run's own rewrite of the start-dirty pointer left out of its landing (%r)"
                  % e)

        case("t_guard_untyped_alone", t_guard_untyped_alone)

        # P3: a here form whose open run has ended pushes, origin rejects it, and the replay's row carries the guard's
        # append (the re-review's s4.sh C reject)
        def t_guard_here_replay():
            r, env = mworld("t-guard-here-replay", follow="- [ ] a\n")
            start_(env, "/specify", "--key", "ACME-1")
            r.write(RES, "resume v1\n")
            f = start_(env, "/feedback")
            r.write(RES, "resume v2\n")
            r.write(FB, "## 2026-11-12 — /feedback — note\n\nmine\n")
            drop(env, "/specify")
            ahead(r, "t-guard-here-replay-other")
            calls = follow(run_end(env, "/feedback"), env)
            last = calls[-1]
            line = last.get("line") or ""
            check(len(calls) == 2 and (calls[0].get("next") or {}).get("run") and last.get("row") == "replayed"
                  and line.endswith(kept_app([RES], "main")) and read(r, RES) == "resume v2\n"
                  and RES not in changed(r, head(r)),
                  "t_guard_here_replay: the replayed here-form row names the pointer left out (%r)" % (calls,))

        case("t_guard_here_replay", t_guard_here_replay)

        # k_started: --started on end, declined and replay -- a stamp is required to be one; a rejected push's next
        # repeats it
        def k_started():
            kenv = {"HOME": os.path.join(tmp, "home-k-started"), "CLAUDE_CODE_SESSION_ID": "k-started"}
            got = cli("--specs", tmp, "end", "--command", "/feedback", "--started", "yesterday", env=kenv)
            got2 = cli("declined", "--command", "/feedback", "--started", "x", "--path", "a.md", env=kenv)
            got3 = cli("--specs", new_repo(tmp, "k-started").path, "replay", "--for", "end", "--command", "/feedback",
                       "--branch", "main", "--started", "x", env=kenv)
            nxt = _replay_next("/s", "/feedback", "main", False, started="2026-11-10T10:00:00Z")
            check(one_not_run_line(got) and "--started" in got["_err"] and one_not_run_line(got2)
                  and one_not_run_line(got3) and "--started" in got3["_err"]
                  and nxt["run"].endswith("--branch main --started 2026-11-10T10:00:00Z")
                  and nxt["on_timeout"].endswith("--started 2026-11-10T10:00:00Z --timed-out"),
                  "k_started: a bad stamp is a usage error on all three; the replay's next repeats --started (%r, %r)"
                  % (got, nxt))

        case("k_started", k_started)

    def scenarios_skill(tmp):
        """The specs-git skill's text, held to the CLI it drives, to the loader that routes to it and to the run-key-set
        file both name; and the session variable, never written with a $ where checks 5 and 9 would read it as one."""
        def read(*parts):
            try:
                with open(os.path.join(HERE, "..", *parts), encoding="utf-8") as fh:
                    return fh.read()
            except OSError:  # a missing file fails the checks that read it, never the whole selftest
                return ""

        skill = read("skills", "specs-git", "SKILL.md")
        loader = read("skills", "reference", "SKILL.md")
        option = re.compile(r"(?<![\w-])--[a-z][a-z0-9-]*")

        def accepted(*sub):
            """The options `specs-git.py [<sub>] --help` lists, as a user meets the parser."""
            got = cli(*(sub + ("--help",)))
            return got["_rc"], got.get("_stdout", ""), set(option.findall(got.get("_stdout", "")))

        rc, top_help, top = accepted()
        listed = re.search(r"\{([a-z,-]+)\}", top_help)
        subcommands = set(listed.group(1).split(",")) if listed else set()
        subs = {s: accepted(s)[2] for s in ("start", "end", "declined", "land", "snapshot")}

        # The one option the skill names that is no option of this script: /docs-brand's, where it says that run calls
        # none of this.
        other = "started `--inline`"
        # Where a bullet of *The call* names its option: start, end or both; or end, and a start that carries one of two
        # options -- --started's place, since start refuses it on a call carrying neither --rerun nor --resume
        place = re.compile(r"(start and end|start|end)|end, and start with `(--[a-z][a-z0-9-]*)` or `(--[a-z][a-z0-9-]*)`")
        land_call = re.compile(r'specs-git\.py" --specs "\$\{SPECS_PATH-\}" land ([^`]*)`')
        stamp = "2026-11-10T10:00:00Z"

        def start_usage(*args):
            """Whether start refuses <args> as a usage error -- read before the session id, so nothing is written."""
            got = cli("--specs", "", "start", "--command", "/k-skill", *args, env={"HOME": os.path.join(tmp, "home-k-skill")})
            return got["_rc"] == 2 and got["_err"].startswith("specs-git: not run (usage:")

        started_alone = start_usage("--started", stamp)
        started_with = {q for q in ("--rerun", "--resume") if not start_usage(q, "--started", stamp)}

        def skill_problems(text):
            problems = []
            if text.count(other) != 1:
                problems.append("the skill names /docs-brand's --inline %d time(s), not once" % text.count(other))
            union = top.union(*subs.values())
            for o in sorted(set(option.findall(text.replace(other, ""))) - union):
                problems.append("%s is no option of specs-git.py, or of its start, end, declined, land or snapshot" % o)
            bullets = re.findall(r"^- `(--[a-z][a-z0-9-]*)[^`]*` \(([^)]*)\)", text, re.M)
            for o, where in bullets:
                m = place.fullmatch(where)
                if m is None:
                    problems.append("%s is named for %r, no place this check reads" % (o, where))
                    continue
                for s in m.group(1).split(" and ") if m.group(1) else ("end", "start"):
                    if o not in subs[s]:
                        problems.append("%s, named for %s, is no option of %s" % (o, s, s))
                if o == "--started" and m.group(1) and "start" in m.group(1).split(" and ") and started_alone:
                    problems.append("--started is named for a start carrying neither --rerun nor --resume, a usage error")
                for q in (m.group(2), m.group(3)):
                    if q and q not in (started_with if o == "--started" else subs["start"]):
                        problems.append("%s, named for a start with %s, which start does not take with it" % (o, q))
            if not any(o == "--started" and "end" in where for o, where in bullets):
                problems.append("The call names --started for no end call")
            declined_calls = re.findall(r'specs-git\.py" declined ([^`]*)`', text)
            for call in declined_calls:
                for o in sorted(set(option.findall(call)) - subs["declined"]):
                    problems.append("%s, in the declined call, is no option of declined" % o)
            if not any("--started" in option.findall(call) for call in declined_calls):
                problems.append("the declined call names no --started")
            land_calls = land_call.findall(text)
            if len(land_calls) != 1:
                problems.append("the skill names the land call %d time(s), not once" % len(land_calls))
            for call in land_calls:
                for o in sorted(set(option.findall(call)) - subs["land"] - top):
                    problems.append("%s, in the land call, is no option of land" % o)
            return problems

        # k_skill_options
        got = skill_problems(skill)
        check(rc == 0 and {"start", "end", "declined", "land", "snapshot"} <= subcommands and "--specs" in top
              and all("--command" in subs[s] for s in ("start", "end", "declined", "land"))
              and all("--resume" in subs[s] for s in ("start", "end")) and "--started" in subs["declined"]
              and started_alone and started_with == {"--rerun", "--resume"}
              and got == [], "k_skill_options: every option the skill names is the CLI's, where it names it (%r, %r)"
              % (sorted(subcommands), got))
        bites = ((skill + "\n`--no-such-option`\n", "--no-such-option is no option"),
                 (skill.replace("- `--no-preflight` (end)", "- `--no-preflight` (start)"), "--no-preflight, named for start"),
                 (skill.replace(other, "started `--inline-x`"), "--inline"),
                 (skill.replace(" --path '<path>'`", " --paths '<path>'`"), "--paths, in the declined call"),
                 (skill.replace("- `--started <stamp>` (end, and start with", "- `--started <stamp>` (start and end, and start with"),
                  "--started is named for 'start and end, and start"),
                 (skill.replace("- `--started <stamp>` (end, and start with `--rerun` or `--resume`)",
                                "- `--started <stamp>` (start and end)"), "--started is named for a start carrying neither"),
                 (skill.replace("(end, and start with `--rerun` or `--resume`)", "(end, and start with `--rerun` or `--budget`)"),
                  "--started, named for a start with --budget"),
                 (skill.replace("declined --command /<name> --started <stamp> --path", "declined --command /<name> --path"),
                  "the declined call names no --started"),
                 (skill.replace(" land --branch <branch> --default-ref", " land --key <branch> --default-ref"),
                  "--key, in the land call, is no option of land"))
        for text, want in bites:
            got = skill_problems(text)
            check(text != skill and any(want in p for p in got),
                  "k_skill_options: a skill naming the wrong option fails (%s: %r)" % (want, got))

        # k_skill_fields: every JSON field the skill names is one the script returns
        _, flow_lines = _flow()
        start_keys = set(_start_result({"print": [], "rec": {}, "lines": flow_lines}, None, None, None))
        end_keys = set(_end_result())
        next_keys = set(_replay_next("/s", "/feedback", "main", False)) & set(_resume_next("/feedback", {}))

        def field_problems(text):
            problems = []
            sections = {s.split("\n", 1)[0]: s for s in text.split("\n## ")}
            listed = re.search(r"results from the last `start` JSON(.*?)wherever your command's text reads them",
                               sections.get("Start", ""), re.S)
            if listed is None:
                problems.append("the Start section lists no field it reads")
            named = set(re.findall(r"`([a-z_][a-z0-9_]*)`", re.sub(r"\([^)]*\)", "", listed.group(1) if listed else "")))
            named |= set(re.findall(r"A `([a-z_][a-z0-9_]*)` field", sections.get("Start", "")))
            for f in sorted(named - start_keys):
                problems.append("Start reads %s, which start's JSON does not hold" % f)
            shared = set(re.findall(r"JSON's `([a-z_][a-z0-9_]*)`|JSON (?:names|with) `([a-z_][a-z0-9_]*)`", text))
            for f in sorted({f for pair in shared for f in pair if f} - (start_keys & end_keys)):
                problems.append("the skill reads %s, which start's and end's JSON do not both hold" % f)
            for f in sorted(set(re.findall(r"`next\.([a-z_][a-z0-9_]*)`", text)) - next_keys):
                problems.append("next.%s is no key of the next a replay or a resume returns" % f)
            return problems

        got = field_problems(skill)
        listed = re.search(r"results from the last `start` JSON(.*?)wherever your command's text reads them", skill, re.S)
        check(listed is not None and "`stay`" in listed.group(1) and "stay" in start_keys
              and "`merged_stay`" not in skill and "merged_stay" not in start_keys
              and "`stay` field" in skill.split("## Where the script cannot start", 1)[-1],
              "k_skill_fields: Start names stay, which an end run by hand reads (§3.3), and merged_stay nowhere")
        check(got == [] and {"print", "error", "next", "specs_git", "b2_left", "replaced"} <= start_keys
              and {"run", "timeout_ms", "on_timeout"} == next_keys,
              "k_skill_fields: every JSON field the skill names is the script's (%r)" % got)
        for old, new, want in (("`b2_left`", "`b2_lefts`", "Start reads b2_lefts"),
                               ("A `replaced` field", "A `replacement` field", "Start reads replacement"),
                               ("`next.timeout_ms`", "`next.timeout`", "next.timeout is no key"),
                               ("JSON with `error` set", "JSON with `failure` set", "reads failure")):
            got = field_problems(skill.replace(old, new))
            check(skill.count(old) >= 1 and any(want in p for p in got),
                  "k_skill_fields: a renamed field fails (%s: %r)" % (want, got))

        # k_skill_fallback: where the end cannot start and the script ran the start, the stay, the snapshot and the open
        # run come from the last start JSON, and the landing or the here form is the land call specs-repo-git §4 step 1's
        # *By hand* paragraph names -- its options, and --snapshot - only where start_dirty holds a snapshot, as land
        # refuses a null one -- that paragraph alone saying what its status leads to, so the skill restates no status
        srg = read("references", "specs-repo-git.md")
        statuses = ("landed", "there", "nothing", "held", "kept", "locked")
        null_snap = cli("--specs", new_repo(tmp, "k-skill-land").path, "land", "--branch", "main", "--default-ref",
                        "refs/heads/main", "--command", "/specify", "--snapshot", "-", stdin=b"null")

        def by_hand(ref):
            """specs-repo-git §4 step 1's *By hand* paragraph, the one that names land; "" where none stands."""
            try:
                step1 = ref[ref.index("\n## 4. "):ref.index("\n### 4.1")].split("\n2. **Enumerate and stage**", 1)[0]
            except ValueError:
                return ""
            return next((p for p in step1.split("\n\n") if p.lstrip().startswith("**By hand**, the landing is one call")), "")

        # The clauses the fallback must keep word for word: where it makes no land call (SRG §4 step 1 (1)), which
        # branch and default ref the call names, where land's own failure goes, and the export The call opens with
        fallback_pins = (
            ("save where its (1) says neither the landing nor the here form commits anything",
             "the fallback makes the land call where §4 step 1 (1) says neither form commits"),
            ("`<branch>` the branch HEAD stands on", "the fallback's <branch> is not the branch HEAD stands on"),
            ("`<default_ref>` your last `start` call's `default_ref` field",
             "the fallback's <default_ref> is not start's default_ref field"),
            ("in place of this section's own exit-2 rule",
             "the fallback sends no land exit 2 or error to the *By hand* paragraph"),
            ("`export SPECS_PATH='<the value>';`", "the land call does not open with The call's export"))
        START_LAST = "the first call's, or that of the last `start --rerun` or `start --resume` made since"
        LAND_FAILS = ("exits 2 on a line that does not begin `specs-git: not run (usage:`", "has `error` set",
                      "whatever it left in the held record — a held entry, or the journal of a move it began — stays "
                      "there", "`Specs repo: NOT FINISHED` line")

        def fallback_problems(text, ref):
            sections = {s.split("\n", 1)[0]: s for s in text.split("\n## ")}
            fallback = sections.get("Where the script cannot start", "")
            listed = re.search(r"results from the last `start` JSON(.*?)wherever your command's text reads them",
                               sections.get("Start", ""), re.S)
            problems = ["the skill names merged_stay"] if "merged_stay" in text else []
            problems += ["the fallback names no `%s`" % f for f in ("stay", "start_dirty", "midrun")
                         if "`%s`" % f not in fallback]
            problems += ["Start lists no `%s`" % f for f in ("stay", "start_dirty", "midrun", "started")
                         if "`%s`" % f not in (listed.group(1) if listed else "")]
            read_fields = {f for pair in re.findall(r"`([a-z_][a-z0-9_]*)` field|call's `([a-z_][a-z0-9_]*)`", fallback)
                           for f in pair if f}
            problems += ["the fallback reads %s, which start's JSON does not hold" % f for f in sorted(read_fields - start_keys)]
            if len(land_call.findall(fallback)) != 1:
                problems.append("the fallback names the land call %d time(s), not once" % len(land_call.findall(fallback)))
            if "`--snapshot -` where `start_dirty` is not null" not in fallback:
                problems.append("the fallback passes --snapshot - without testing start_dirty for null")
            para = by_hand(ref)
            if not para:
                problems.append("specs-repo-git §4 step 1 has no *By hand* paragraph naming land")
            want, named = set(option.findall(para.split("It prints", 1)[0])), set(option.findall(fallback))
            problems += ["the fallback names %s, which §4 step 1's *By hand* call does not" % o for o in sorted(named - want)]
            problems += ["the fallback names no %s, which §4 step 1's *By hand* call does" % o for o in sorted(want - named)]
            if "§4 step 1's *By hand* paragraph" not in fallback:
                problems.append("the fallback does not send the land call's status to §4 step 1's *By hand* paragraph")
            problems += ["the fallback restates the status %s, the *By hand* paragraph's" % s for s in statuses
                         if "`%s`" % s in fallback]
            if re.search(r"\bpush", fallback):
                problems.append("the fallback names a push, which only the *By hand* paragraph may say, by status")
            problems += [said for pin, said in fallback_pins if pin not in fallback]
            if START_LAST not in sections.get("Start", ""):
                problems.append("Start's last start JSON leaves out a start --rerun's")
            tos = [re.search(r"timeout of ([0-9]+) ms", s) for s in (sections.get("The call", ""), fallback)]
            if not all(tos) or tos[0].group(1) != tos[1].group(1):
                problems.append("the land call's timeout is not The call's")
            if not all(s in para for s in LAND_FAILS):
                problems.append("§4 step 1's *By hand* paragraph says nothing of the land call's exit 2 or error")
            return problems

        got = fallback_problems(skill, srg)
        check(got == [] and all("`%s`" % s in by_hand(srg) for s in statuses)
              and one_not_run_line(null_snap) and "usage:" not in null_snap["_err"],
              "k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names "
              "land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot (%r, %r)" % (got, null_snap))
        for old, new, want, ref in (
                ("call's `midrun` field", "call's `mid_run` field", "the fallback names no `midrun`", srg),
                (", `midrun` and `started` — ", " and `midrun` — ", "Start lists no `started`", srg),
                ("the stay §4 step 1 reads is your last `start` call's `stay` field",
                 "the stay §4 step 1 reads is your last `start` call's `merged_stay` field", "names merged_stay", srg),
                ("`--snapshot -` where `start_dirty` is not null", "`--snapshot -`", "without testing start_dirty", srg),
                (", and `--here` for the here form", "", "names no --here", srg),
                ("§4 step 1's *By hand* paragraph", "§4 step 5", "does not send the land call's status", srg),
                ("says its `status` leads to", "says its `status` leads to, `landed` the commit's row",
                 "restates the status landed", srg),
                (None, None, "names --here, which §4 step 1's *By hand* call does not",
                 srg.replace(", and `--here` for the here form below", "")),
                ("says its `status` leads to", "says its `status` leads to, a push included", "names a push", srg),
                ("save where its (1) says neither the landing nor the here form commits anything, ", "",
                 "where §4 step 1 (1) says neither form commits", srg),
                ("`<branch>` the branch HEAD stands on", "`<branch>` the branch your `stay` names",
                 "is not the branch HEAD stands on", srg),
                ("your last `start` call's `default_ref` field", "your last `start` call's `default` field",
                 "is not start's default_ref field", srg),
                ("in place of this section's own exit-2 rule", "", "sends no land exit 2 or error", srg),
                ("`export SPECS_PATH='<the value>';` where", "where", "does not open with The call's export", srg),
                ("a timeout of 600000 ms, opened", "a timeout of 120000 ms, opened", "timeout is not The call's", srg),
                (START_LAST, "the first call's, or the last `start --resume` a `next` led to",
                 "leaves out a start --rerun's", srg),
                (None, None, "says nothing of the land call's exit 2 or error",
                 srg.replace("`Specs repo: NOT FINISHED` line, `<the error>`", "outcome line, `<the error>`")),
                (None, None, "says nothing of the land call's exit 2 or error",
                 srg.replace("whatever it left in the held record — a held entry, or the journal of a move it began — "
                             "stays there", "what it held or journalled stays in the held record"))):
            got = fallback_problems(skill.replace(old, new) if old else skill, ref)
            check((old is None or skill.count(old) >= 1) and any(want in p for p in got),
                  "k_skill_fallback: a fallback off its rule fails (%s: %r)" % (want, got))

        # k_loader_routes
        para = next((p for p in loader.split("\n\n") if "workflows-core:specs-git" in p), "")
        front = loader.split("---", 2)[1] if loader.startswith("---") else ""
        tools = re.search(r"^allowed-tools:(.*)$", front, re.M)
        check(all(s in para for s in ('Skill(skill: "workflows-core:specs-git", args: "start")', 'args: "end"',
                                      'args: "specs-repo-git specs-preflight"', 'args: "specs-repo-git commit-artifacts"'))
              and tools is not None and "Skill" in [t.strip() for t in tools.group(1).split(",")],
              "k_loader_routes: the loader routes both requests to the skill and may call it (%r)"
              % (tools.group(0) if tools else None))

        # k_key_set_file
        rel = "skills/specs-git/run-key-set.md"
        named = "${CLAUDE_PLUGIN_ROOT}/" + rel
        check(os.path.isfile(os.path.join(HERE, "..", rel)) and named in skill and named in loader,
              "k_key_set_file: %s exists, and the skill and the loader both name it" % rel)

        # k_key_set_quotes: run-key-set.md quotes specs-repo-git word for word -- each of its quotations found,
        # whitespace-collapsed, in §3 up to §3.3, and each paragraph of §3.2 from *Run key set* to its end equal to one of
        # them -- so a word changed on either side fails, and so does a sentence or a paragraph §3.2 gains there
        key_set = read("skills", "specs-git", "run-key-set.md")

        def key_set_problems(text, ref):
            try:
                s3 = ref[ref.index("\n## 3. "):ref.index("\n### 3.3")]
                s32 = ref[ref.index("\n### 3.2"):ref.index("\n### 3.3")]
            except ValueError:
                return ["specs-repo-git has no §3, §3.2 or §3.3 heading"]
            quotes = [" ".join(re.sub(r"(?m)^> ?", "", p).split()) for p in text.split("\n\n") if p.startswith(">")]
            paras = s32.split("\n\n")
            first = next((k for k, p in enumerate(paras) if p.lstrip().startswith("**Run key set:**")), None)
            problems = [] if quotes else ["run-key-set.md quotes nothing"]
            if first is None:
                problems.append("§3.2 has no *Run key set* paragraph")
            whole = " ".join(s3.split())
            problems += ["run-key-set.md's quotation %d is not in specs-repo-git §3 (%s…)" % (k + 1, q[:60])
                         for k, q in enumerate(quotes) if q not in whole]
            for p in paras[first:] if first is not None else []:
                c = " ".join(p.split())
                if c and c not in quotes:
                    problems.append("specs-repo-git §3.2's paragraph %s… is not quoted whole in run-key-set.md" % c[:60])
            return problems

        got = key_set_problems(key_set, srg)
        check(got == [] and key_set.count("\n> ") >= 6,
              "k_key_set_quotes: run-key-set.md quotes §3.2 from *Run key set* on, and §3's sentence, word for word (%r)" % got)
        word, said = "contributes **both**", "contributes **each**"
        tail = "`NOISSUE`.\n\n### 3.3"
        for label, text, ref, want in (
                ("a word of the file", key_set.replace(word, said), srg, "quotation 1 is not in"),
                ("the same word of §3.2", key_set, srg.replace(word, said), "quotation 1 is not in"),
                ("a word of §3's sentence", key_set, srg.replace("and resolves afterwards", "and resolves later"),
                 "quotation 6 is not in"),
                ("a sentence §3.2 gains", key_set, srg.replace(tail, "`NOISSUE`. One sentence more.\n\n### 3.3"),
                 "is not quoted whole")):
            got = key_set_problems(text, ref)
            check(key_set.count(word) == 1 and srg.count(word) == 1 and srg.count(tail) == 1
                  and srg.count("and resolves afterwards") == 1 and any(want in p for p in got),
                  "k_key_set_quotes: %s changed fails (%r)" % (label, got))

        # k_branch_check_midrun (P23, M6): branch-check's two mid-run stops -- It does not's (no switch) and It does's
        # (no merge) -- prose a run follows and no template of the script's, each held verbatim in phase-handoff §6.1's
        # bullet and in the part file generated from it, naming no git command: check-branch-check reads which commands
        # request branch-check, never the stop's wording
        handoff = read("references", "phase-handoff.md")
        part_file = read("reference-parts", "phase-handoff", "branch-check.md")
        midrun_stops = {
            "It does not": ("<finding> — <command>'s run in this session is still open on <branch>, so no switch is "
                            "named here: finish or end that run first, then re-run; if you stopped that run, /clear, "
                            "typing <command> again[ with <keys>], or HEAD leaving the branch ends it."),
            "It does": ("<finding> — <command>'s run in this session is still open on <branch>, so no merge is named "
                        "here: finish or end that run first, then re-run; if you stopped that run, /clear, typing "
                        "<command> again[ with <keys>], or HEAD leaving the branch ends it."),
        }

        def midrun_problems(ref, part):
            try:
                s61 = ref[ref.index("\n### 6.1 "):ref.index("\n### 6.2 ")]
            except ValueError:
                return ["phase-handoff has no §6.1 or §6.2 heading"]
            bullets = {}
            for line in s61.split("\n"):
                m = re.match(r"- \*\*(It does not|It does)\*\*", line)
                if m:
                    bullets[m.group(1)] = line
            problems = []
            for label, stop in sorted(midrun_stops.items()):
                if stop not in bullets.get(label, ""):
                    problems.append("phase-handoff §6.1's *%s* bullet does not hold its mid-run stop verbatim" % label)
                if stop not in part:
                    problems.append("branch-check.md does not hold the *%s* mid-run stop verbatim" % label)
                if "git" in stop or re.search(r"\b(?:switch|merge)\s+(?:<|-|to\b|into\b)", stop):
                    problems.append("the *%s* mid-run stop names a git command" % label)
            return problems

        got = midrun_problems(handoff, part_file)
        check(got == [], "k_branch_check_midrun: both mid-run stops are in their §6.1 bullets and the part file, "
                         "naming no git command (%r)" % got)
        for label, stop in sorted(midrun_stops.items()):
            got = midrun_problems(handoff.replace(stop, ""), part_file)
            check(handoff.count(stop) == 1
                  and got == ["phase-handoff §6.1's *%s* bullet does not hold its mid-run stop verbatim" % label],
                  "k_branch_check_midrun: the *%s* stop dropped from §6.1 fails (%r)" % (label, got))

        # k_no_dollar_session: the directories check-docs.sh's checks 5 and 9 read a $NAME in, of every plugin
        session_var = "CLAUDE_CODE_SESSION_ID"
        written = ("$" + session_var, "${" + session_var)

        def dollar_session(plugins):
            found, scanned = [], set()
            for plugin in sorted(os.listdir(plugins)):
                for d in ("commands", "agents", "references", "hooks", "skills"):
                    for dirpath, _, files in os.walk(os.path.join(plugins, plugin, d)):
                        for name in sorted(files):
                            full = os.path.join(dirpath, name)
                            try:
                                with open(full, encoding="utf-8") as fh:
                                    text = fh.read()
                            except (OSError, UnicodeDecodeError):
                                continue
                            scanned.add(os.path.realpath(full))
                            if any(w in text for w in written):
                                found.append(os.path.relpath(full, plugins))
            return found, scanned

        found, scanned = dollar_session(os.path.join(HERE, "..", ".."))
        check(found == [] and os.path.realpath(SPECS_REPO_GIT) in scanned,
              "k_no_dollar_session: no plugin file checks 5 and 9 read names the session variable after a $ (%r)" % found)
        fake = os.path.join(tmp, "k-dollar", "plugins")
        for rel, body in (("x/hooks/a.sh", "echo " + written[0] + "\n"), ("x/skills/s/SKILL.md", written[1] + "}\n"),
                          ("x/references/plain.md", session_var + "\n"), ("x/scripts/b.py", written[0] + "\n")):
            os.makedirs(os.path.dirname(os.path.join(fake, rel)), exist_ok=True)
            with open(os.path.join(fake, rel), "w", encoding="utf-8") as fh:
                fh.write(body)
        found, _ = dollar_session(fake)
        check(sorted(found) == ["x/hooks/a.sh", "x/skills/s/SKILL.md"],
              "k_no_dollar_session: both written forms found, the plain name and a scripts/ file not (%r)" % found)

    def scenarios_selftest(tmp):
        """The selftest's own command line: one group alone, the partial line, the refusals, and the file's absence."""
        ALL = ("status, branch_merged, branch_key, push_scope, owner_repo, mode, state, lines, gate, end, land, replay, "
               "start, midrun, skill, selftest")
        # Every run started here is marked nested, so a break in group selection fails rather than recursing, and
        # every run but s_group_refused_in_ci's has GITHUB_ACTIONS empty, outside CI's refusal of --group, so this
        # group passes in CI too.
        nested = {"SPECS_GIT_SELFTEST_NESTED": "1", "GITHUB_ACTIONS": ""}
        got = cli("--selftest", "--group", "branch_key", cwd=tmp, env=nested)
        check(got["_rc"] == 0 and re.fullmatch(r"specs-git selftest: PASS \([1-9][0-9]* checks; partial: branch_key\)",
                                               (got.get("_stdout", "").strip().splitlines() or [""])[-1]) is not None,
              "s_group_alone: one group runs alone and says so (%r)" % got)
        got = cli("--selftest", "--group", "owner_repo", "--group", "branch_key", cwd=tmp, env=nested)
        check(got["_rc"] == 0 and got.get("_stdout", "").strip().endswith("partial: branch_key, owner_repo)"),
              "s_group_order: groups run and are named in the selftest's order (%r)" % got)
        got = cli("--selftest", "--group", "nope", env=nested)
        check(one_not_run_line(got)
              and got["_err"].strip() == "specs-git: not run (usage: --group takes one of: %s)" % ALL,
              "s_group_unknown: an unknown group is a usage error naming every group (%r)" % got)
        got = cli("--group", "status", env=nested)
        check(one_not_run_line(got) and "usage: --group needs --selftest" in got["_err"],
              "s_group_without_selftest: --group alone is a usage error (%r)" % got)
        got = cli("--selftest", "--group", "branch_key", env=dict(nested, GITHUB_ACTIONS="true"))
        check(got["_rc"] == 2 and got["_raw"] == b""
              and got["_err"] == ("specs-git: not run (--group is refused in CI, where GITHUB_ACTIONS is true: a partial "
                                  "run is never evidence that the selftest passes)\n"),
              "s_group_refused_in_ci: a run with --group is refused in CI, in one line (%r)" % got)
        got = cli("--selftest", "--group", "selftest", env=nested)
        check(got["_rc"] == 1 and got.get("_stdout", "").splitlines() == [
                  "specs-git selftest: FAIL (nested)",
                  "  s_nested: a nested run was asked for every group, or for group selftest"],
              "s_nested_refused: a nested run of group selftest fails rather than recursing (%r)" % got)
        lone =os.path.join(tmp, "s-lone", "plugins", "workflows-core")
        os.makedirs(lone)
        shutil.copytree(HERE, os.path.join(lone, "scripts"))
        got = cli("--selftest", script=os.path.join(lone, "scripts", "specs-git.py"), env=nested)
        check(one_not_run_line(got)
              and got["_err"].startswith("specs-git: not run (the selftest is not shipped with the plugin"),
              "s_selftest_not_shipped: a tree without the selftest file says so in one line (%r)" % got)
        unread = os.path.join(tmp, "s-unread")
        shutil.copytree(HERE, os.path.join(unread, "plugins", "workflows-core", "scripts"))
        at = os.path.join(unread, "scripts", "selftests", "specs_git_selftest.py")
        os.makedirs(at)  # a directory where the file belongs, which no one can read as a file, root included
        try:
            open(at, encoding="utf-8").close()
            why = None
        except OSError as e:
            why = e.strerror
        got = cli("--selftest", script=os.path.join(unread, "plugins", "workflows-core", "scripts", "specs-git.py"),
                  env=nested)
        check(one_not_run_line(got) and why is not None
              and got["_err"].strip() == "specs-git: not run (the selftest could not be read: %s: %s)"
              % (os.path.normpath(at), why),
              "s_selftest_unreadable: a selftest path that cannot be read says why in one line (%r, %r)" % (why, got))
        clash = os.path.join(tmp, "s-clash")
        shutil.copytree(HERE, os.path.join(clash, "plugins", "workflows-core", "scripts"))
        os.makedirs(os.path.join(clash, "scripts", "selftests"))
        with open(os.path.join(clash, "scripts", "selftests", "specs_git_selftest.py"), "w", encoding="utf-8") as fh:
            fh.write("HERE = 1\n\n\ndef selftest(groups=None):\n    print(\"specs-git selftest: PASS (0 checks)\")\n"
                     "    return 0\n")
        got = cli("--selftest", script=os.path.join(clash, "plugins", "workflows-core", "scripts", "specs-git.py"),
                  env=nested)
        check(one_not_run_line(got) and got["_raw"] == b""
              and got["_err"] == "specs-git: not run (the selftest file redefines a name of the script: HERE)\n",
              "s_selftest_redefines: a selftest file that rebinds a name of the script is not run (%r)" % got)
        got = cli(script=os.path.normpath(SELFTEST_FILE), env=nested)
        check(got["_rc"] == 1 and got["_raw"] == b""
              and got["_err"] == ("specs_git_selftest.py: not run (it runs only inside specs-git.py: "
                                  "python3 plugins/workflows-core/scripts/specs-git.py --selftest)\n"),
              "s_file_run_directly: the selftest file run on its own names the command that runs it (%r)" % got)
        ci =os.path.join(HERE, "..", "..", "..", ".github", "workflows", "validate-catalog.yml")
        with open(ci, encoding="utf-8") as fh:
            runs = [line.strip() for line in fh if line.strip().startswith("run:") and "specs-git.py" in line]
        check(runs == ["run: python3 plugins/workflows-core/scripts/specs-git.py --selftest"],
              "s_ci_runs_all: CI runs the whole selftest, with no --group (%r)" % runs)

    # The groups, in run order: --selftest --group <name> runs only the named ones, still in this order.
    GROUPS = (("status", scenarios_status), ("branch_merged", scenarios_branch_merged),
              ("branch_key", scenarios_branch_key), ("push_scope", scenarios_push_scope),
              ("owner_repo", scenarios_owner_repo), ("mode", scenarios_mode), ("state", scenarios_state),
              ("lines", scenarios_lines), ("gate", scenarios_gate), ("end", scenarios_end), ("land", scenarios_land),
              ("replay", scenarios_replay), ("start", scenarios_start), ("midrun", scenarios_midrun),
              ("skill", scenarios_skill), ("selftest", scenarios_selftest))
    names = [name for name, _ in GROUPS]
    if groups is not None and any(g not in names for g in groups):
        print("specs-git: not run (usage: --group takes one of: %s)" % ", ".join(names), file=sys.stderr)
        return 2
    partial = None if groups is None else ", ".join(name for name in names if name in groups)

    def scenarios():
        with tempfile.TemporaryDirectory() as tmp:
            for name, run in GROUPS:
                if groups is None or name in groups:
                    run(tmp)

    try:
        scenarios()
    except Exception as e:  # a scenario that crashes must not hide the failures before it
        failures.append("selftest crashed: %s: %s" % (type(e).__name__, str(e).strip()[:500]))

    if failures:
        print("specs-git selftest: FAIL" if partial is None else "specs-git selftest: FAIL (partial: %s)" % partial)
        for f in failures:
            print("  " + f)
        return 1
    if partial is None:
        print("specs-git selftest: PASS (%d checks)" % count[0])
    else:
        print("specs-git selftest: PASS (%d checks; partial: %s)" % (count[0], partial))
    return 0
