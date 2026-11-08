#!/usr/bin/env python3
"""specs-git.py — the deterministic git primitives of workflows-core:specs-repo-git and
workflows-core:phase-handoff, one implementation every command reaches through those references.

The rules are the references'; this script is their plumbing, and a change to either is a change to
both. It loads session-branch.py as a module, so the §2.1 classifier, the §4 step 5 push-scope walk,
§8.1's mode and the git helper exist once. Python standard library only.

  specs-git.py --specs <root> status
  specs-git.py --specs <root> branch-merged --ref <ref> --default-ref <ref>
  specs-git.py --specs <root> branch-key --branch <name> [--key <K>]...
  specs-git.py --specs <root> push-scope --branch <name> [--session-default-ref <ref>]
  specs-git.py --specs <root> mode --default <name>
  specs-git.py owner-repo --repo <path> [--no-alias]
  specs-git.py --selftest

<root> is the specs repository's top level. Nothing here writes the working tree, the index or a
ref. Output is one JSON object on stdout. Exit 0: it ran, whatever it found. Exit 2: it could not
run (usage, not a repository's top level, a ref that does not resolve, an unexpected git failure,
any other exception), printing one "specs-git: not run (...)" line on stderr; the caller reports it
and the run continues.
"""

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SPECS_REPO_GIT = os.path.join(HERE, "..", "references", "specs-repo-git.md")


def _load_session_branch():
    spec = importlib.util.spec_from_file_location("session_branch", os.path.join(HERE, "session-branch.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sb = _load_session_branch()
NotRun = sb.NotRun


def status(root):
    """specs-repo-git §2.1 staging steps 1-2: every path git status reports, sorted into the ARTIFACT
    paths the terminal commit may stage and every OTHER path. Read with -z, whose records are never
    quoted; a rename or copy record carries its original path as a second field, consumed with it."""
    fields = sb.git(root, "status", "--porcelain", "-z", "--untracked-files=all").stdout.decode(
        "utf-8", "surrogateescape").split("\0")
    artifact, other = set(), set()
    i = 0
    while i < len(fields):
        record = fields[i]
        i += 1
        if not record:
            continue
        path = record[3:]
        if "R" in record[:2] or "C" in record[:2]:
            i += 1  # the original path, which is no record of its own
        (artifact if sb.classify(path) else other).add(path)
    return {"artifact": sorted(artifact), "other": sorted(other)}


class Parser(argparse.ArgumentParser):
    """A usage error is one "not run" line, as every exit 2 is."""

    def error(self, message):
        print("specs-git: not run (%s)" % message, file=sys.stderr)
        sys.exit(2)


def main():
    ap = Parser(description="The deterministic git primitives of specs-repo-git and phase-handoff.")
    ap.add_argument("--specs", help="the specs repository's top level")
    ap.add_argument("--selftest", action="store_true", help="run the built-in fixtures and exit")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except AttributeError:
        pass
    if a.selftest:
        return selftest()
    if not a.cmd:
        print("specs-git: not run (a subcommand is required)", file=sys.stderr)
        return 2
    try:
        if not a.specs:
            raise NotRun("--specs is required")
        top = sb.text(sb.git(a.specs, "rev-parse", "--show-toplevel"))
        if os.path.realpath(top) != os.path.realpath(a.specs):
            raise NotRun("%s is not its repository's top level (%s)" % (a.specs, top))
        result = dispatch(a)
    except (NotRun, OSError) as e:
        print("specs-git: not run (%s)" % " ".join(str(e).split()), file=sys.stderr)
        return 2
    except Exception as e:  # anything unexpected is "not run" on one line, never a traceback
        print("specs-git: not run (%s: %s)" % (type(e).__name__, " ".join(str(e).split())), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


def dispatch(a):
    if a.cmd == "status":
        return status(a.specs)
    raise NotRun("unknown subcommand %s" % a.cmd)


def selftest():
    """Every rule this script carries, on repositories built at run time."""
    failures = []
    count = [0]
    me = os.path.abspath(__file__)
    os.environ["GIT_CONFIG_GLOBAL"] = os.devnull
    os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
    os.environ.pop("GIT_USER_INITIALS", None)

    def check(ok, what):
        count[0] += 1
        if not ok:
            failures.append(what)

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

    def cli(*args, env=None):
        r = subprocess.run([sys.executable, me, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=dict(os.environ, **(env or {})))
        out = r.stdout.decode("utf-8", "replace")
        try:
            got = json.loads(out) if out.strip() else {}
        except ValueError:
            got = {"_stdout": out}
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
        check("dev-workflows-cost/x.md" not in got["artifact"] + got["other"],
              "status: a rename's original path is no record of its own (%r)" % got)
        check(set(got["other"]) == {frames, shot, prd, threat}, "status: the other list (%r)" % got)
        check(got["artifact"] == sorted(got["artifact"]) and got["other"] == sorted(got["other"]),
              "status: both lists sorted (%r)" % got)
        got = cli("--specs", r.path, "status")
        check(got["_rc"] == 0 and set(got.get("artifact", [])) == {resume, follow, reg, "dev-workflows-cost/y.md"},
              "status: the CLI prints the same object (%r)" % got)
        got = cli("--specs", os.path.join(r.path, "specifications"), "status")
        check(one_not_run_line(got) and "_stdout" not in got and "artifact" not in got,
              "a subdirectory is not the top level: exit 2, one line, no JSON (%r)" % got)
        plain = os.path.join(tmp, "plain")
        os.makedirs(plain)
        got = cli("--specs", plain, "status")
        check(one_not_run_line(got), "a directory that is no repository: exit 2, one line (%r)" % got)
        got = cli("status")
        check(one_not_run_line(got), "no --specs: exit 2, one line (%r)" % got)
        got = cli("--specs", r.path, "no-such-subcommand")
        check(one_not_run_line(got), "an unknown subcommand: exit 2, one line (%r)" % got)

    def scenarios():
        with tempfile.TemporaryDirectory() as tmp:
            scenarios_status(tmp)

    try:
        scenarios()
    except Exception as e:  # a scenario that crashes must not hide the failures before it
        failures.append("selftest crashed: %s: %s" % (type(e).__name__, str(e).strip()[:500]))

    if failures:
        print("specs-git selftest: FAIL")
        for f in failures:
            print("  " + f)
        return 1
    print("specs-git selftest: PASS (%d checks)" % count[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
