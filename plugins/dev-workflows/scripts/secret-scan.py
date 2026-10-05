#!/usr/bin/env python3
"""secret-scan.py — flag possible secrets in the lines a code commit is about to add.

Called by references/code-handoff.md §2.2 just before §2.3's commit.
Python standard library only. Two modes:

  secret-scan.py --repo <top-level>               the staged diff (the `add -A` path)
  secret-scan.py --repo <top-level> -- <path> …   those paths against HEAD (carve-out 1)

It reads only the lines the diff adds, plus the names of the files it adds or
changes, so a secret already in the history is not this commit's to report.
Each hit prints as `path:line  rule  preview`. The preview never carries the
value: a token's first four characters (its public format prefix) and its
length, and for a password or a URL's credentials the length alone.
Placeholders, environment-variable references and lines carrying an allowlist
marker (`gitleaks:allow`, `pragma: allowlist secret`) are dismissed and counted.

Exit 0: no hit. Exit 1: hits. Exit 2: the scan could not run (git failed, bad
arguments, any unexpected error) -- never 1, which a caller reads as hits. `--selftest` builds its fixtures in a temporary repository at run
time, so no token-shaped literal sits in this file for a host's push
protection to trip on.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time

# --- content rules: (name, compiled regex, index of the group holding the value) ---
# Group 0 is the whole match. A rule whose value is its own match uses 0.
CONTENT_RULES = [
    ("private-key", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----"), 0),
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA|AGPA|AIDA|AROA|ANPA|ANVA|AIPA)[A-Z0-9]{16}\b"), 0),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})"), 0),
    ("gitlab-token", re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}"), 0),
    ("slack-token", re.compile(r"\bxox[abprse]-[A-Za-z0-9-]{10,}"), 0),
    ("slack-webhook", re.compile(r"https://hooks\.slack\.com/services/T[A-Za-z0-9]+/B[A-Za-z0-9]+/[A-Za-z0-9]+"), 0),
    ("stripe-key", re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{16,}"), 0),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}"), 0),
    ("npm-token", re.compile(r"\bnpm_[A-Za-z0-9]{36}\b"), 0),
    ("llm-api-key", re.compile(r"\bsk-(?:ant-(?:api|admin)\d{2}-|proj-)[A-Za-z0-9_-]{20,}|\bsk-[A-Za-z0-9]{48}\b"), 0),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), 0),
    ("url-credentials", re.compile(r"\b[A-Za-z][A-Za-z0-9+.-]*://[^\s/:@'\"]+:([^\s/@'\"]+)@[^\s/'\"]+"), 1),
]

# A credential-named key assigned a literal. Quoted values anywhere; unquoted
# values only in config-shaped files, where code expressions do not occur.
_SENTINEL = (r"(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?key|private[_-]?key|"
             r"signing[_-]?key|auth[_-]?token|access[_-]?token|client[_-]?secret|"
             r"shared[_-]?secret|hmac[_-]?(?:key|secret)|_?authtoken)")
# The lookbehind, not \b, starts a key only at a token's beginning: \b also fires
# between "." and a letter, and a long dotted or base64url line then re-scans from
# every one of them (measured: 52 s on 40 KB, against 3 ms this way). The optional
# group takes a type annotation between the key and the operator -- `api_key: str`,
# `val apiKey: String`, `var apiKey string` -- led by a colon or by whitespace, so a
# longer key such as `password_hint` is never read as `password` plus a type.
_TYPE = (r"(?:\s*:\s*|\s+)&?(?:'[a-z_]+\s+)?[A-Za-z_][\w.<>?\[\]]{0,40}"
         r"(?:\s*\|\s*[A-Za-z_][\w.<>?\[\]]{0,40}){0,3}")  # str | None, &'static str
ASSIGN_QUOTED = re.compile(r"(?i)(?<![\w.-])[\w.-]*" + _SENTINEL + r"[\"']?(?:" + _TYPE + r")?"
                           r"\s*(?::=|=>|[:=])\s*[\"']([^\"'\s]{8,})[\"']")
# Admits a YAML or compose list marker (`- POSTGRES_PASSWORD=…`), a scoped key as `.npmrc`
# writes one (`//registry.example/:_authToken=…`) and a trailing comment.
ASSIGN_BARE = re.compile(r"(?i)^\s*(?:-\s+)?(?:export\s+)?(?://\S*:)?[\w.-]*" + _SENTINEL +
                         r"[\"']?\s*[:=]\s*([^\s\"'#;,]{8,})\s*(?:#.*)?$")
CONFIG_EXT = (".env", ".properties", ".ini", ".cfg", ".conf", ".toml", ".yaml", ".yml", ".npmrc", ".pypirc")

ALLOW_MARKERS = ("gitleaks:allow", "pragma: allowlist secret")
PLACEHOLDER_WORDS = ("example", "sample", "dummy", "fake", "placeholder", "changeme", "change_me",
                     "redacted", "your_", "your-", "<", "xxxx", "****", "todo", "insert", "replace")
PLACEHOLDER_EXACT = {"password", "passwd", "pass", "pwd", "secret", "token", "none", "null", "test",
                     "true", "false", "user", "username"}

ENV_FILE_OK_SUFFIX = (".example", ".sample", ".template", ".dist", ".defaults")
KEYSTORE_EXT = (".p12", ".pfx", ".jks", ".keystore", ".kdbx", ".ppk")
KEY_FILE_NAMES = {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519", ".netrc", ".git-credentials"}


def is_placeholder(value):
    v = value.strip().strip("\"'")
    low = v.lower()
    if low in PLACEHOLDER_EXACT:
        return True
    if any(w in low for w in PLACEHOLDER_WORDS):
        return True
    if re.fullmatch(r"\$\{[^}]*\}|\$[A-Za-z_][A-Za-z0-9_]*|%[A-Za-z_][A-Za-z0-9_]*%|\{\{.*\}\}", v):
        return True  # an environment or template reference, not a literal
    if v.startswith(("ENC(", "vault:", "arn:", "http://", "https://")):
        return True
    if len(set(v)) <= 2:  # ******** / xxxxxxxx / 00000000
        return True
    if re.fullmatch(r"[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+|[A-Z]+", v):  # an env-var name, e.g. DB_PASSWORD
        return True
    if re.fullmatch(r"[a-z0-9._-]+", v) and not re.search(r"\d", v):  # an identifier or slug
        return True
    return False


# A token's first characters are its published format prefix (AKIA, ghp_, eyJh) and
# give nothing away; a password's are a quarter of it or more, so it shows none.
UNPREFIXED = ("secret-assignment", "url-credentials")
TOKEN_PLACEHOLDER = ("example", "sample", "dummy", "fake", "placeholder", "xxxx", "redacted")


def mask(value, rule=""):
    if rule in UNPREFIXED:
        return "(%d chars)" % len(value)
    return value[:4] + "...(%d chars)" % len(value)


def assignment(path, text):
    m = ASSIGN_QUOTED.search(text)
    config_shaped = path.lower().endswith(CONFIG_EXT) or os.path.basename(path).lower().startswith(".env")
    if not m and config_shaped:
        m = ASSIGN_BARE.search(text)
    return m


def key_file_reason(path):
    base = os.path.basename(path)
    low = base.lower()
    if low == ".env" or (low.startswith(".env.") and not low.endswith(ENV_FILE_OK_SUFFIX)):
        return "an environment file"
    if low.endswith(KEYSTORE_EXT):
        return "a keystore"
    if low in KEY_FILE_NAMES:
        return "a credentials file"
    return None


def unquote_c(path):
    """Undo git's C-style quoting of a diff header path ("a\\tb" -> a<TAB>b)."""
    if not (path.startswith('"') and path.endswith('"')):
        return path
    raw = path[1:-1].encode("utf-8", "surrogateescape")
    escapes = {ord("n"): 10, ord("t"): 9, ord('"'): 34, ord("\\"): 92, ord("a"): 7,
               ord("b"): 8, ord("f"): 12, ord("r"): 13, ord("v"): 11}
    out, i = bytearray(), 0
    while i < len(raw):
        c = raw[i]
        if c == 0x5C and i + 1 < len(raw):
            n = raw[i + 1]
            if 0x30 <= n <= 0x37:
                out.append(int(raw[i + 1:i + 4], 8))
                i += 4
                continue
            out.append(escapes.get(n, n))
            i += 2
            continue
        out.append(c)
        i += 1
    return out.decode("utf-8", "replace")


def count(dismissed, key):
    dismissed[key] = dismissed.get(key, 0) + 1


def scan_line(path, lineno, text, hits, dismissed):
    if any(m in text for m in ALLOW_MARKERS):
        if any(rx.search(text) for _, rx, _ in CONTENT_RULES) or assignment(path, text):
            count(dismissed, "allowlisted")
        return
    reported = False
    for name, rx, grp in CONTENT_RULES:
        for m in rx.finditer(text):
            value = m.group(grp)
            if name == "url-credentials":
                if is_placeholder(value):
                    count(dismissed, name)
                    continue
            elif name != "private-key" and any(w in value.lower() for w in TOKEN_PLACEHOLDER):
                count(dismissed, name)  # e.g. the documentation key AKIAIOSFODNN7EXAMPLE
                continue
            preview = m.group(0) if name == "private-key" else mask(value, name)
            hits.append({"path": path, "line": lineno, "rule": name, "preview": preview})
            reported = True
    if reported:
        return  # a dismissed match must not hide a real password beside it
    m = assignment(path, text)
    if m:
        value = m.group(1)
        if is_placeholder(value):
            count(dismissed, "secret-assignment")
        else:
            hits.append({"path": path, "line": lineno, "rule": "secret-assignment",
                         "preview": mask(value, "secret-assignment")})


def git(repo, *args):
    # The hunk counter below depends on the diff's shape, which these settings in a
    # user's config would change: merged hunks, and blank context lines printed empty.
    r = subprocess.run(["git", "-C", repo, "-c", "core.quotePath=false", "-c", "diff.interHunkContext=0",
                        "-c", "diff.suppressBlankEmpty=false", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace").strip().splitlines()
        raise RuntimeError("git %s failed: %s" % (args[0], err[0] if err else "exit %d" % r.returncode))
    return r.stdout


def scan(repo, paths):
    if paths:
        head = subprocess.run(["git", "-C", repo, "rev-parse", "-q", "--verify", "HEAD"],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        base = head.stdout.decode().strip() if head.returncode == 0 else \
            git(repo, "hash-object", "-t", "tree", "/dev/null").decode().strip()
        spec = ["--"] + [":(literal)" + p for p in paths]
        diff_args = ["diff", base]
    else:
        spec = []
        diff_args = ["diff", "--cached"]
    # Explicit prefixes: diff.noprefix or diff.mnemonicPrefix in the user's config would
    # otherwise change what a header's path starts with.
    common = ["--no-color", "--no-ext-diff", "-M", "--diff-filter=ACMRT", "--no-textconv",
              "--src-prefix=a/", "--dst-prefix=b/"]
    names = git(repo, *diff_args, *common, "--name-only", "-z", *spec).decode("utf-8", "replace")
    files = [n for n in names.split("\0") if n]
    hits, dismissed = [], {}
    for f in files:
        reason = key_file_reason(f)
        if reason:
            hits.append({"path": f, "line": None, "rule": "key-file", "preview": "(%s)" % reason})
    out = git(repo, *diff_args, *common, "-U0", *spec).decode("utf-8", "replace")
    # Inside a hunk, lines are counted off its header, never parsed as headers: an
    # added line whose text begins "++ " reads "+++ " in the diff.
    path, lineno, old_left, new_left = None, 0, 0, 0
    for raw in out.split("\n"):
        if raw.startswith("diff --git "):
            old_left = new_left = 0  # a new file: whatever the last hunk left uncounted ends here
            path = None
            continue
        if old_left > 0 or new_left > 0:
            if raw.startswith("+"):
                if path:
                    scan_line(path, lineno, raw[1:], hits, dismissed)
                lineno += 1
                new_left -= 1
            elif raw.startswith("-"):
                old_left -= 1
            elif raw.startswith(" "):
                lineno += 1
                old_left -= 1
                new_left -= 1
            continue  # "\ No newline at end of file" counts toward neither side
        if raw.startswith("+++ "):
            # git appends a tab to a header whose path holds a space.
            target = raw[4:].rstrip("\t")
            path = None if target == "/dev/null" else unquote_c(target)
            if path and path.startswith("b/"):
                path = path[2:]
            continue
        m = re.match(r"@@ -\d+(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", raw)
        if m:
            old_left = int(m.group(1)) if m.group(1) is not None else 1
            lineno = int(m.group(2))
            new_left = int(m.group(3)) if m.group(3) is not None else 1
    return {"hits": hits, "dismissed": dismissed, "files": len(files)}


def render(result):
    n, d = len(result["hits"]), sum(result["dismissed"].values())
    lines = ["secret-scan: %d possible secret(s) in %d file(s) scanned; %d dismissed%s" % (
        n, result["files"], d,
        " (" + ", ".join("%s %d" % kv for kv in sorted(result["dismissed"].items())) + ")" if d else "")]
    for h in result["hits"]:
        where = h["path"] if h["line"] is None else "%s:%d" % (h["path"], h["line"])
        lines.append("%s  %s  %s" % (where, h["rule"], h["preview"]))
    return "\n".join(lines)


def selftest():
    """Assert every rule fires, every dismissal holds, and both modes read the right diff."""
    q = '"'
    gh = "gh" + "p_" + "A1b2C3d4" * 5  # 40 chars after the prefix
    aws = "AK" + "IA" + "Q7W3E5R7T9Y1U3I5"
    jwt = "ey" + "JhbGciOiJIUzI1NiJ9" + ".ey" + "JzdWIiOiIxMjM0NTY3ODkwIn0" + "." + "dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
    pem = "-----BEGIN " + "RSA PRIVATE KEY-----"
    at = "@"  # a credentialed URL, split so the literal never sits in this file whole
    npm_auth = "//registry.npmjs.org/:_auth" + "Token=" + "-".join(["0f3c2a1e", "4b5d", "4c6e", "8f7a", "9b0c1d2e3f4a"])
    files = {
        "app/config.py": "API_KEY = %s%s%s\nTOKEN = %s%s%s\n" % (q, aws, q, q, gh, q),
        "app/auth.js": "const t = '%s';\n" % jwt,
        "keys/server.pem": pem + "\nMIIE\n",
        "db.yaml": "password: s3cr3tPassw0rd\nurl: postgres://admin:Hunter22x" + at + "db:5432/x\n",
        "ok.py": ("password = os.environ[%sDB_PASSWORD%s]\nclient_secret = %s<your-secret>%s\n"
                  "api_key = %schangeme-please%s\nfield_password = %suser-password-input%s\n"
                  "url = %shttps://user:password" + at + "host/x%s\nAWS = %s%s%s  # gitleaks:allow\n") % (
                      q, q, q, q, q, q, q, q, q, q, q, aws, q),
        ".env": "SOME_FLAG=1\n",
        ".env.example": "API_KEY=<set me>\n",
        "store/release.jks": "binary-ish\n",
        "dir with space/creds.py": "secret = %sQ9z!xV2#mL7p%s\n" % (q, q),
        # Review round 1: a short password, typed declarations, .npmrc's scoped key, an
        # added line reading "++ ", a documentation key, a key that only starts like a
        # sentinel, an allowlisted assignment and a literal that starts with "$".
        "dsn.py": "DSN = 'postgres://admin:h4x0" + at + "db/x'\n",
        "typed.py": "api_key: str = %sZx9QwErTy123AbCd%s\n" % (q, q),
        "typed.kt": "val apiKey: String = %sZx9QwErTy123AbCd%s\n" % (q, q),
        "typed.ts": "const password: string = %sZx9QwErTy123AbCd%s;\n" % (q, q),
        "typed.go": "var apiKey string = %sZx9QwErTy123AbCd%s\n" % (q, q),
        ".npmrc": npm_auth + "\n",
        "hijack.yaml": "++ /dev/null\npassword: Zx9Qw!Er7Ty\n",
        "more_ok.py": ("AWS_DOC = %sAKIAIOSFODNN7" + "EXAMPLE%s\npassword_hint = %sMyHint123%s\n"
                       "secret = %sQ9z!xV2#mL7pZ%s  # gitleaks:allow\n") % (q, q, q, q, q, q),
        "dollar.py": "admin_password = %s$uperS3cret!%s\n" % (q, q),
        # Review round 2: a dismissed match beside a real password, a union type, a Rust
        # reference, a YAML comment, a compose list entry, an all-caps password.
        "beside.py": ("password = %sHunter22xyz%s  # format: https://user:pass" + at + "host\n"
                      "DB_URL = %spostgres://user:changeme" + at + "localhost/db%s; DB_PASSWORD = %sHunter22xyz%s\n") % (
                          q, q, q, q, q, q),
        "union.py": "password: str | None = %sZx9QwErTy123AbCd%s\n" % (q, q),
        "lib.rs": "let api_key: &'static str = %sZx9QwErTy123AbCd%s;\n" % (q, q),
        "prod.yaml": "password: s3cr3tPassw0rd  # prod\n",
        "docker-compose.yml": "    - POSTGRES_PASSWORD=supersecret1\n",
        "caps.py": "password = %sHUNTER22XYZ%s\n" % (q, q),
    }
    expect = {
        ("app/config.py", 1, "aws-access-key-id"), ("app/config.py", 2, "github-token"),
        ("app/auth.js", 1, "jwt"),
        ("keys/server.pem", 1, "private-key"), ("db.yaml", 1, "secret-assignment"),
        ("db.yaml", 2, "url-credentials"), (".env", None, "key-file"),
        ("store/release.jks", None, "key-file"), ("dir with space/creds.py", 1, "secret-assignment"),
        ("dsn.py", 1, "url-credentials"), ("typed.py", 1, "secret-assignment"),
        ("typed.kt", 1, "secret-assignment"), ("typed.ts", 1, "secret-assignment"),
        ("typed.go", 1, "secret-assignment"), (".npmrc", 1, "secret-assignment"),
        ("hijack.yaml", 2, "secret-assignment"), ("dollar.py", 1, "secret-assignment"),
        ("beside.py", 1, "secret-assignment"), ("beside.py", 2, "secret-assignment"),
        ("union.py", 1, "secret-assignment"), ("lib.rs", 1, "secret-assignment"),
        ("prod.yaml", 1, "secret-assignment"), ("docker-compose.yml", 1, "secret-assignment"),
        ("caps.py", 1, "secret-assignment"),
    }
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        def run(*a):
            subprocess.run(["git", "-C", tmp, *a], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        run("init", "-q")
        run("config", "user.email", "t@example.invalid")
        run("config", "user.name", "t")
        for rel, body in files.items():
            p = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as fh:
                fh.write(body)
        run("add", "-A")
        # 1. staged mode on an unborn branch: everything is added.
        r = scan(tmp, [])
        got = {(h["path"], h["line"], h["rule"]) for h in r["hits"]}
        for e in sorted(expect - got, key=str):
            failures.append("staged: missed %s" % (e,))
        for g in sorted(got - expect, key=str):
            failures.append("staged: unexpected %s" % (g,))
        printed = render(r) + json.dumps(r)
        for secret in (gh, aws, jwt, "s3cr3tPassw0rd", "Hunter22x", "Q9z!xV2#mL7p", "h4x0",
                       "Zx9Q", "0f3c", "$upe"):
            if secret in printed:
                failures.append("staged: a value printed unmasked (%s)" % mask(secret))
        if r["dismissed"].get("aws-access-key-id") != 1:
            failures.append("staged: documentation key not dismissed (%r)" % r["dismissed"])
        if r["dismissed"].get("allowlisted") != 2:
            failures.append("staged: allowlist marker not counted (%r)" % r["dismissed"])
        if r["dismissed"].get("secret-assignment", 0) < 3:
            failures.append("staged: placeholders not dismissed (%r)" % r["dismissed"])
        # 2. a pre-existing secret is not reported again; only added lines are read.
        run("commit", "-q", "-m", "base")
        with open(os.path.join(tmp, "app/config.py"), "a") as fh:
            fh.write("DEBUG = True\n")
        run("add", "-A")
        r = scan(tmp, [])
        if r["hits"]:
            failures.append("staged: re-reported history %r" % r["hits"])
        # 3. pathspec mode reads the named paths against HEAD and nothing else.
        with open(os.path.join(tmp, "new.py"), "w") as fh:
            fh.write("access_token = %sZx9!Qw8@Er7#%s\n" % (q, q))
        with open(os.path.join(tmp, "other.py"), "w") as fh:
            fh.write("secret = %sNotMine!123%s\n" % (q, q))
        run("add", "-N", "--", "new.py")
        r = scan(tmp, ["new.py"])
        got = {(h["path"], h["line"], h["rule"]) for h in r["hits"]}
        if got != {("new.py", 1, "secret-assignment")}:
            failures.append("paths: got %r" % sorted(got, key=str))
        # 4. a diff reshaped by the user's config still maps each line to its own file,
        #    and a symlink replaced by a file is read.
        run("config", "diff.interHunkContext", "10")
        run("config", "diff.suppressBlankEmpty", "true")
        body = "".join("x%d = 1\n\n" % i for i in range(3))  # two changes close enough to merge
        with open(os.path.join(tmp, "ctx.py"), "w") as fh:
            fh.write(body)
        os.symlink("ctx.py", os.path.join(tmp, "link.yaml"))
        run("add", "-A")
        run("commit", "-q", "-m", "ctx")
        with open(os.path.join(tmp, "ctx.py"), "w") as fh:
            fh.write("a = 1\n" + body + "b = 2\n")
        with open(os.path.join(tmp, "moved.py"), "w") as fh:
            fh.write("secret = %sQ9z!xV2#mL7pY%s\n" % (q, q))
        os.remove(os.path.join(tmp, "link.yaml"))
        with open(os.path.join(tmp, "link.yaml"), "w") as fh:
            fh.write("password: Zx9Qw!Er7Ty\n")
        run("add", "-A")
        r = scan(tmp, [])
        got = {(h["path"], h["line"], h["rule"]) for h in r["hits"]}
        if got != {("moved.py", 1, "secret-assignment"), ("link.yaml", 1, "secret-assignment")}:
            failures.append("reshaped diff: got %r" % sorted(got, key=str))
        # 5. a long dotted or base64url line scans in linear time.
        with open(os.path.join(tmp, "long.js"), "w") as fh:
            fh.write("a." * 10000 + "\n")  # 20 KB: 3 ms linear, about 13 s the quadratic way
        run("add", "-N", "--", "long.js")
        started = time.time()
        scan(tmp, ["long.js"])
        if time.time() - started > 2:
            failures.append("long line: %.1f s, expected well under one" % (time.time() - started))
    if failures:
        print("secret-scan selftest: FAIL")
        for f in failures:
            print("  " + f)
        return 1
    print("secret-scan selftest: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Flag possible secrets in the lines a commit adds.")
    ap.add_argument("--repo", help="the repository's top level")
    ap.add_argument("--json", action="store_true", help="print the result as JSON")
    ap.add_argument("--selftest", action="store_true", help="run the built-in fixtures and exit")
    ap.add_argument("paths", nargs="*", help="after --: scan these paths against HEAD instead of the index")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except AttributeError:
        pass
    if a.selftest:
        return selftest()
    if not a.repo:
        print("secret-scan: --repo is required", file=sys.stderr)
        return 2
    try:
        result = scan(a.repo, a.paths)
        print(json.dumps(result, indent=2) if a.json else render(result))
    except Exception as e:  # anything unexpected is "not run", never "hits"
        print("secret-scan: not run (%s: %s)" % (type(e).__name__, e), file=sys.stderr)
        return 2
    return 1 if result["hits"] else 0


if __name__ == "__main__":
    sys.exit(main())
