#!/usr/bin/env python3
"""promotion-signals.py — the deterministic half of the promote-decisions command.

  promotion-signals.py --specs <root> --ref <ref> [--layout vi|prd] --signals [--reconsider]
  promotion-signals.py --specs <root> --ref <ref> --arch <root> --arch-ref <ref> [--specs-name <name>] --reconcile
  promotion-signals.py --specs <root> --mark <plan.json> [--check]
  promotion-signals.py --selftest

--signals: for every record under <specs>/architecture/decisions/ at <ref>, its own counts, the feature
folders outside its own that link to it, the deviations recorded against it there, the records of
other groups it superseded, its promotion keys, and whether it is a candidate; and, for each
organisation artifact the team side names in a deviation, every place that names it.
--reconcile: the promotion keys each record should carry, given the `Origin: team decisions …` lines
of the ADRs at <arch-ref> (only the lines naming <specs-name>, when it is given), the records marked
proposed whose ADR is on no such line, and the proposed ADRs that propose to supersede another.
--mark: writes or clears the promotion keys of the named records in the working tree, preserving
every other byte, and writes nothing else; with --check it validates the plan and writes nothing.

The record format is the plugin's architecture-kb reference; the keys and their lifecycle are its
architecture-promotion reference. Parsing is architecture-harvest.py's, loaded from beside this file,
so the two never disagree about a record. Python standard library only.

Exit 0: it ran — problems are listed in the JSON. Exit 2: it could not run.
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


def _harvest():
    spec = importlib.util.spec_from_file_location("architecture_harvest",
                                                  os.path.join(HERE, "architecture-harvest.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


H = _harvest()
Abort = H.Abort

DECISIONS = H.KB + "/decisions/"
KEYS = ("promotion", "promoted_to", "promotion_note")
VALUES = ("proposed", "accepted", "rejected", "declined", "covered")
NEEDS_ADR = ("proposed", "accepted", "rejected", "covered")
NEEDS_NOTE = ("declined",)
ART_ID = r"(?:[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+|\d{3,}-[a-z][a-z0-9]*(?:-[a-z0-9]+)*)"  # ADR-0004, STD-API-001, 0005-use-outbox
RECORD_ID_FULL = re.compile("^%s$" % H.RECORD_ID)
PROMOTED_TO_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")  # an ADR's or standard's id, or its file stem
RECORD_IDS = re.compile(r"(?<![\w-])(%s)(?![\w-])" % H.RECORD_ID)
LINK_RE = re.compile(r"\]\(<?([^)\s>]*?)architecture/decisions/(%s)\.md>?\)" % H.RECORD_ID)
ART_LINK_RE = re.compile(r"\[(%s|%s)(?![\w-])[^\]]*\]\(" % (H.RECORD_ID, ART_ID))
DEVIATION_RE = re.compile(r"^\s*[-*]\s*Architecture deviation:\s*\[(%s|%s)(?![\w-])[^\]]*\]\(" % (H.RECORD_ID, ART_ID))
OPEN_Q_RE = re.compile(r"^##\s+(?:\d+\.\s*)?Open questions\s*$", re.I)
ITEM_RE = re.compile(r"^\s*[-*]\s")
KEY_LINE_RE = re.compile(r"^([A-Za-z_][\w-]*):")
ADR_DIRS = ("decisions/", "adr/", "adrs/", "docs/adr/", "docs/adrs/", "docs/decisions/", "docs/architecture/decisions/")
ORIGIN_RE = re.compile(r"^\s*Origin:\s*team decisions\s+(.*)$")
SUPERSEDE_RE = re.compile(r"^\s*Proposes to supersede:\s*([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)")
STATUS_HEADING_RE = re.compile(r"^#{2,3}\s+Status\s*$", re.I)
STATUS_LINE_RE = re.compile(r"^\s*(?:[-*]\s+)?(?:#{2,3}\s+)?Status\s*:\s*([A-Za-z]+)", re.I)
EMPHASIS_RE = re.compile(r"[*_`]")
STATUS_MAP = {"accepted": "accepted", "approved": "accepted", "deprecated": "accepted", "superseded": "accepted",
              "proposed": "proposed", "draft": "proposed", "rejected": "rejected", "withdrawn": "rejected"}
RANK = {"accepted": 0, "proposed": 1, "rejected": 2}  # a live ADR before a rejected one: that one is history


def folder_of(path, layout):
    """The feature folder a path belongs to: specifications/<group>/, or (prd) the deepest PRD- folder."""
    parts = path.split("/")
    if len(parts) < 3 or parts[0] != "specifications":
        return None
    if layout == "prd":
        idx = [i for i, p in enumerate(parts[:-1]) if p.startswith("PRD-")]
        if idx:
            return "/".join(parts[:idx[-1] + 1]) + "/"
    return "/".join(parts[:2]) + "/"


def is_ard(path, layout):
    base = path.rsplit("/", 1)[-1]
    return bool((H.PRD_ARD_RE if layout == "prd" else H.VI_ARD_RE).match(base))


def items_under(body, heading):
    count, on = 0, False
    for ln in body:
        if ln.startswith("## "):
            on = ln[3:].strip() == heading
            continue
        if on and ln.startswith("- ["):
            count += 1
    return count


def open_questions(lines):
    on = False
    for i, ln in enumerate(lines, 1):
        if H.TOP_HEADING_RE.match(ln):
            on = bool(OPEN_Q_RE.match(ln))
            continue
        if on and ITEM_RE.match(ln):
            yield i, ln


def load_records(root, sha, files):
    recs = {}
    for p in files:
        rest = p[len(DECISIONS):]
        if not p.startswith(DECISIONS) or not p.endswith(".md") or "/" in rest:
            continue
        fm, body = H.split_frontmatter(H.read(root, sha, p))
        _, b = H.fm_blocks(fm)
        rid = H.fm_scalar(b, "id") or rest[:-3]
        recs[rid] = {
            "id": rid, "path": p,
            "title": H.fm_scalar(b, "title", strip_comment=False) or rid,
            "status": H.fm_scalar(b, "status") or "accepted",
            "scope": H.fm_scalar(b, "scope") or "vi",
            "group": H.fm_scalar(b, "vi") or H.fm_scalar(b, "prd") or "",
            "source": H.fm_scalar(b, "source") or "",
            "superseded_by": H.fm_scalar(b, "superseded_by"),
            "components": len(H.fm_list(b, "components")),
            "applied_in": items_under(body, "Applied in"),
            "deviated_in": items_under(body, "Deviated in"),
            "promotion": H.fm_scalar(b, "promotion"),
            "promoted_to": H.fm_scalar(b, "promoted_to"),
            "promotion_note": H.fm_scalar(b, "promotion_note", strip_comment=False),
        }
    return recs


def _note(aid, entry, recs, own, elsewhere, artifacts):
    if aid in recs:
        if entry["folder"] != own[aid]:
            elsewhere[aid].append(entry)
    elif not RECORD_ID_FULL.match(aid):
        artifacts.setdefault(aid, []).append(entry)


def signals(root, ref, layout="vi", reconsider=False):
    sha = H.resolve(root, ref)
    files = H.list_files(root, sha)
    recs = load_records(root, sha, files)
    own = {rid: folder_of(r["source"], layout) for rid, r in recs.items()}
    cited = {rid: set() for rid in recs}
    elsewhere = {rid: [] for rid in recs}
    artifacts = {}
    for p in sorted(files):
        if not p.endswith(".md") or p.startswith(H.KB + "/") or H.excluded(p):
            continue
        here = folder_of(p, layout)
        lines = H.read(root, sha, p).split("\n")
        for i, ln in enumerate(lines, 1):
            for m in LINK_RE.finditer(ln):
                rid = m.group(2)
                if rid in recs and here and here != own[rid]:
                    cited[rid].add(here)
            m = DEVIATION_RE.match(ln)
            if m:
                _note(m.group(1), {"file": p, "line": i, "kind": "design-deviation", "folder": here},
                      recs, own, elsewhere, artifacts)
        if is_ard(p, layout):
            for i, ln in open_questions(lines):
                for aid in sorted(set(ART_LINK_RE.findall(ln))):
                    _note(aid, {"file": p, "line": i, "kind": "ard-open-question", "folder": here},
                          recs, own, elsewhere, artifacts)
    records = []
    for rid in sorted(recs, key=H.natural):
        r = recs[rid]
        candidate = r["status"] == "accepted" and (
            r["promotion"] is None or (reconsider and r["promotion"] in ("declined", "rejected")))
        records.append({
            "id": rid, "title": r["title"], "status": r["status"], "scope": r["scope"], "group": r["group"],
            "source": r["source"], "components": r["components"], "applied_in": r["applied_in"],
            "deviated_in": r["deviated_in"], "cited_by": sorted(cited[rid]),
            "deviated_elsewhere": elsewhere[rid],
            "superseded_others": sorted((x for x, o in recs.items()
                                         if o["superseded_by"] == rid and o["group"] != r["group"]), key=H.natural),
            "promotion": r["promotion"], "promoted_to": r["promoted_to"], "promotion_note": r["promotion_note"],
            "candidate": candidate})
    arts = [{"id": a, "friction": e, "folders": sorted({x["folder"] for x in e if x["folder"]})}
            for a, e in sorted(artifacts.items(), key=lambda kv: H.natural(kv[0]))]
    return {"sha": sha, "layout": layout, "records": records, "artifacts": arts,
            "candidates": sum(1 for r in records if r["candidate"])}


def _status_word(text):
    m = re.match(r"\s*([A-Za-z]+)", EMPHASIS_RE.sub("", text).lstrip("-* "))
    return m.group(1).lower() if m else "unknown"


def adr_status(blocks, body):
    """An ADR's status word: frontmatter `status:`, else the first line under a `## Status` heading, else a
    `Status:` label near the top (`## Status: X`, `**Status:** X`, `- **Status**: X`), emphasis ignored."""
    s = H.fm_scalar(blocks, "status")
    if s:
        return _status_word(s)
    for i, ln in enumerate(body):
        if STATUS_HEADING_RE.match(ln):
            for nxt in body[i + 1:]:
                if nxt.strip():
                    return _status_word(nxt)
    for ln in body[:30]:
        m = STATUS_LINE_RE.match(EMPHASIS_RE.sub("", ln))
        if m:
            return m.group(1).lower()
    return "unknown"


def artifact_id(blocks, base):
    """An ADR's id: its frontmatter `id:`, else its file stem's leading `<letters>-<digits>`, else the stem."""
    m = re.match(r"([A-Za-z]+-\d+)", base)
    return H.fm_scalar(blocks, "id") or (m.group(1) if m else base[:-3])


def reconcile(specs, ref, arch, arch_ref, specs_name=None):
    sha = H.resolve(specs, ref)
    recs = load_records(specs, sha, H.list_files(specs, sha))
    asha = H.resolve(arch, arch_ref)
    adrs, named, problems, superseding = [], {}, [], []
    for p in sorted(H.list_files(arch, asha)):
        base = p.rsplit("/", 1)[-1]
        if (not p.endswith(".md") or base.lower() in ("readme.md", "index.md")
                or not any(p.startswith(d) for d in ADR_DIRS)):
            continue
        fm, body = H.split_frontmatter(H.read(arch, asha, p))
        _, b = H.fm_blocks(fm)
        origin, supersedes = [], None
        for ln in body:
            m = ORIGIN_RE.match(ln)
            if m and not origin:  # the first Origin line that names this specs repository
                ids, _, rest = m.group(1).partition(" — ")
                if specs_name is None or (rest.split() or [""])[0].strip(".,;:") == specs_name:
                    origin = RECORD_IDS.findall(ids)
            m = SUPERSEDE_RE.match(ln)
            if m and supersedes is None:
                supersedes = m.group(1)
        if not origin and not supersedes:
            continue
        aid = artifact_id(b, base)
        if not PROMOTED_TO_RE.fullmatch(aid):
            problems.append(H.problem("invalid-id", p, 0, "its id %r is no artifact id (letters, digits, . _ -), so "
                                      "it names nothing for this command" % aid))
            continue
        status = adr_status(b, body)
        if status not in STATUS_MAP:
            problems.append(H.problem("unknown-status", p, 0, "status %r is none of %s, so the records it names "
                                      "keep their keys" % (status, ", ".join(sorted(STATUS_MAP)))))
        if supersedes and STATUS_MAP.get(status) == "proposed":
            superseding.append({"adr": supersedes, "by": aid})
        if not origin:
            continue
        adrs.append({"id": aid, "file": p, "status": status, "origin": origin})
        for rid in origin:
            named.setdefault(rid, []).append((aid, status, p))
    changes, unresolved = [], []
    for rid in sorted(recs, key=H.natural):
        r = recs[rid]
        cur = {k: r[k] for k in KEYS if r[k] is not None}
        hits = named.get(rid)
        if not hits:
            if r["promotion"] == "proposed":
                if isinstance(r["promoted_to"], str) and PROMOTED_TO_RE.fullmatch(r["promoted_to"]):
                    unresolved.append({"id": rid, "promoted_to": r["promoted_to"]})
                else:
                    problems.append(H.problem("invalid-key", r["path"], 0, "promoted_to %r is no artifact id"
                                              % r["promoted_to"]))
            continue
        known = [h for h in hits if h[1] in STATUS_MAP]
        if not known:
            continue
        live = [h for h in known if STATUS_MAP[h[1]] != "rejected"]
        if len(live) > 1:
            problems.append(H.problem("multiple-origins", r["path"], 0, "named by the Origin lines of %s"
                                      % ", ".join(h[0] for h in live)))
        best = min(RANK[STATUS_MAP[h[1]]] for h in known)
        aid, status, _ = max((h for h in known if RANK[STATUS_MAP[h[1]]] == best), key=lambda h: H.natural(h[0]))
        want = {"promotion": STATUS_MAP[status], "promoted_to": aid}
        if want["promotion"] == "rejected":
            want["promotion_note"] = (r["promotion_note"] if r["promotion"] == "rejected" and r["promotion_note"]
                                      else "%s was %s" % (aid, status))
        if want != cur:
            changes.append({"id": rid, "from": cur, "to": want})
    for rid in sorted(named, key=H.natural):
        if rid not in recs:
            problems.append(H.problem("unknown-record", named[rid][0][2], 0,
                                      "its Origin line names %s, which is no record" % rid))
    return {"sha": sha, "arch_sha": asha, "adrs": adrs, "changes": changes, "unresolved": unresolved,
            "superseding": superseding, "problems": problems}


def check_keys(rid, keys):
    if not isinstance(keys, dict) or set(keys) - set(KEYS):
        raise Abort("%s: keys must be an object of %s" % (rid, ", ".join(KEYS)))
    v = keys.get("promotion")
    if v not in VALUES:
        raise Abort("%s: promotion must be one of %s" % (rid, ", ".join(VALUES)))
    adr = keys.get("promoted_to")
    if v in NEEDS_ADR and not (isinstance(adr, str) and PROMOTED_TO_RE.fullmatch(adr)):
        raise Abort("%s: promotion %s needs promoted_to, an artifact id" % (rid, v))
    if v not in NEEDS_ADR and adr is not None:
        raise Abort("%s: promotion %s takes no promoted_to" % (rid, v))
    note = keys.get("promotion_note")
    if v in NEEDS_NOTE and not (isinstance(note, str) and note.strip()):
        raise Abort("%s: promotion %s needs a promotion_note" % (rid, v))
    if note is not None and (not isinstance(note, str) or "\n" in note):
        raise Abort("%s: promotion_note is one line" % rid)


def rewrite(text, keys, rid):
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise Abort("%s has no frontmatter" % rid)
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise Abort("%s has an unterminated frontmatter" % rid)
    kept, cur = [], None
    for ln in lines[1:end]:
        m = KEY_LINE_RE.match(ln)
        if m:
            cur = m.group(1)
        if cur not in KEYS:
            kept.append(ln)
    if keys is not None:
        kept.append("promotion: " + keys["promotion"])
        if keys.get("promoted_to"):
            kept.append("promoted_to: " + keys["promoted_to"])
        if keys.get("promotion_note"):
            kept.append("promotion_note: " + H.q(keys["promotion_note"]))
    return "\n".join([lines[0]] + kept + lines[end:])


def mark(root, plan_path, check=False):
    H.resolve(root, "HEAD")  # the specs repository's top level, or Abort
    with open(plan_path, encoding="utf-8") as fh:
        plan = json.load(fh)
    marks = plan.get("marks") if isinstance(plan, dict) else None
    if not isinstance(marks, dict):
        raise Abort('the plan holds no "marks" object')
    base = os.path.realpath(os.path.join(root, H.KB, "decisions"))
    staged = []
    for rid in sorted(marks, key=H.natural):
        keys = marks[rid]
        if not RECORD_ID_FULL.fullmatch(rid):
            raise Abort("%r is not a record id" % rid)
        path = os.path.join(root, DECISIONS + rid + ".md")
        if not os.path.realpath(path).startswith(base + os.sep) or not os.path.isfile(path):
            raise Abort("no record %s in the working tree" % rid)
        if keys is not None:
            check_keys(rid, keys)
        with open(path, encoding="utf-8", newline="") as fh:
            old = fh.read()
        staged.append((path, DECISIONS + rid + ".md", old, rewrite(old, keys, rid)))
    if check:
        return {"written": [], "would_write": [rel for _, rel, old, new in staged if new != old]}
    written = []
    for path, rel, old, new in staged:  # every entry validated before the first write
        if new != old:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new)
            written.append(rel)
    return {"written": written}


# --- selftest ----------------------------------------------------------------------------

def selftest():
    """Every rule of the promotion keys and signals, on fixtures built at run time."""
    failures = []
    me = os.path.abspath(__file__)

    def check(ok, what):
        if not ok:
            failures.append(what)

    def git(tmp, *args):
        subprocess.run(["git", "-C", tmp, *args], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def init(tmp):
        git(tmp, "init", "-q")
        for k, v in (("user.email", "t@example.invalid"), ("user.name", "t"), ("commit.gpgsign", "false")):
            git(tmp, "config", k, v)

    def commit(tmp, files, message):
        for rel, body in files.items():
            path = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(body)
        git(tmp, "add", "-A")
        git(tmp, "commit", "-q", "-m", message)

    def snapshot(tmp, message):
        git(tmp, "add", "-A")
        git(tmp, "commit", "-q", "--allow-empty", "-m", message)

    def text(path):
        with open(path, encoding="utf-8", newline="") as fh:
            return fh.read()

    def cli(*args):
        return subprocess.run([sys.executable, me, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def run_mark(tmp, marks, *extra):
        fd, plan = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump({"marks": marks}, fh)
        try:
            return cli("--specs", tmp, "--mark", plan, *extra)
        finally:
            os.remove(plan)

    def ad(n, title, extra=""):
        return ("### [AD#%d]: %s\n\n**Binds:** the %s path.\n\n**Prevents:** divergence.\n\n**Rule:** %s holds.\n\n"
                "**Alternatives:** option B — lost on cost.\n\n%s") % (n, title, title.lower(), title, extra)

    def ard(title, decisions, open_questions="None.\n", fm=""):
        return ("---\ntitle: %s — ARD\n%s---\n\n# %s — ARD\n\n## Context\n\nWhy.\n\n## Architecture decisions\n\n%s\n"
                "## Open questions\n\n%s") % (title, fm, title, "\n".join(decisions), open_questions)

    adr4 = "[ADR-0004 RabbitMQ as the standard message broker](https://example.invalid/ADR-0004.md)"

    def rec(rid, title, depth):
        return "[%s %s](%sarchitecture/decisions/%s.md)" % (rid, title, "../" * depth, rid)

    # ---- the vi layout ---------------------------------------------------------------
    orders, billing, search = ("specifications/ACME-1-orders/", "specifications/ACME-7-billing/",
                               "specifications/ACME-9-search/")
    outbox = "Orders publish events through an outbox"
    with tempfile.TemporaryDirectory() as tmp:
        init(tmp)
        commit(tmp, {
            orders + "ACME-1_ARD.md": ard("Orders", [ad(1, outbox), ad(2, "Shared cache")],
                                          fm="components:\n  - id: orders\n  - id: shop\n"),
            orders + "ACME-2-checkout/design.md": ("# Design\n\nUses [AD#1].\n\n## ARD deviations\n\n"
                                                   "- ARD deviation: [AD#2] — caches per pod — latency — flag: architect\n"),
            orders + "notes.md": "Our own: %s.\n" % rec("ACME-1-AD1", outbox, 2),
            billing + "ACME-7_ARD.md": ard("Billing", [
                ad(1, "Billing writes through the outbox",
                   "**Supersedes:** [ACME-1-AD2 Shared cache](../../architecture/decisions/ACME-1-AD2.md) — one cache.\n\n"),
                ad(2, "Billing ledger"), ad(3, "Billing retries")],
                open_questions="- [ ] Departs from %s — billing uses Kafka.\n- [ ] Departs from %s — refunds skip it.\n"
                "- [ ] See [2-phase commit](https://example.invalid/2pc), [12-factor config](https://example.invalid/12f), "
                "[3-tier layout](https://example.invalid/3t) and [2024-05-01 sync notes](https://example.invalid/n).\n"
                % (adr4, rec("ACME-1-AD1", outbox, 2))),
            search + "ACME-9-ui/design.md": (
                "# Design\n\nFollows %s.\n\n## Risks & mitigations\n\n"
                "- Architecture deviation: %s — uses Kafka — throughput — flag: architect\n"
                "- Architecture deviation: %s — local cache — latency — flag: architect\n"
                "- Architecture deviation: radar: Kafka not listed — adopted — throughput — flag: architect\n"
                "- Architecture deviation: [0005-use-outbox](https://example.invalid/0005-use-outbox.md) — polls — cost — flag: architect\n"
                % (rec("ACME-1-AD1", outbox, 3), adr4, rec("ACME-1-AD2", "Shared cache", 3))),
            search + "revisions/old.md": "Old: %s.\n" % rec("ACME-1-AD1", outbox, 3),
        }, "fixtures")
        H.harvest(tmp, "HEAD", "vi", write=True)
        snapshot(tmp, "harvest")

        try:
            s = signals(tmp, "HEAD")
        except Exception as e:  # a stub, or a crash, is one failure, never a traceback
            s = {"records": [], "artifacts": [], "candidates": None}
            check(False, "--signals runs: %s" % e)
        by = {r["id"]: r for r in s["records"]}
        a1, a2, b1 = by.get("ACME-1-AD1", {}), by.get("ACME-1-AD2", {}), by.get("ACME-7-AD1", {})
        check(a1.get("applied_in") == 1 and a1.get("deviated_in") == 0 and a1.get("components") == 2,
              "a record's own counts: %s" % a1)
        check(a1.get("cited_by") == [billing, search], "cited_by: other folders only, revisions/ excluded: %s"
              % a1.get("cited_by"))
        check([e["kind"] for e in a1.get("deviated_elsewhere", [])] == ["ard-open-question"],
              "a record named in another VI's ARD open question")
        check(a2.get("status") == "superseded" and a2.get("candidate") is False and a2.get("deviated_in") == 1
              and [e["kind"] for e in a2.get("deviated_elsewhere", [])] == ["design-deviation"],
              "a superseded record: deviated in its own folder and elsewhere: %s" % a2)
        check(b1.get("superseded_others") == ["ACME-1-AD2"] and b1.get("candidate") is True,
              "a cross-VI Supersedes: %s" % b1)
        arts = {x["id"]: x for x in s["artifacts"]}
        check(set(arts) == {"ADR-0004", "0005-use-outbox"}
              and [e["kind"] for e in arts["ADR-0004"]["friction"]] == ["ard-open-question", "design-deviation"]
              and arts["ADR-0004"]["folders"] == [billing, search]
              and [e["kind"] for e in arts["0005-use-outbox"]["friction"]] == ["design-deviation"],
              "ADR friction from an ARD and a design, a numbered ADR stem included; a radar line and link text that "
              "only starts with a number name no artifact: %s" % arts)
        check(s["candidates"] == 4, "the live records without keys are the candidates: %s" % s["candidates"])

        # ---- --mark ------------------------------------------------------------------
        path2 = os.path.join(tmp, DECISIONS + "ACME-7-AD2.md")
        path3 = os.path.join(tmp, DECISIONS + "ACME-7-AD3.md")
        before2, before3 = text(path2), text(path3)
        r = run_mark(tmp, {"ACME-7-AD2": {"promotion": "declined", "promotion_note": "billing-only ledger"}})
        after2 = text(path2)
        added = 'promotion: declined\npromotion_note: "billing-only ledger"\n'
        check(r.returncode == 0 and added in after2 and after2.replace(added, "", 1) == before2,
              "--mark adds exactly the keys and preserves every other byte: rc=%d %s" % (r.returncode, r.stderr[-300:]))
        snapshot(tmp, "mark")
        again = H.harvest(tmp, "HEAD", "vi", write=False)
        check("ACME-7-AD2" in again["unchanged"] and not again["files"],
              "a re-harvest keeps the keys and writes nothing: %s" % again["files"])
        try:
            d = {x["id"]: x for x in signals(tmp, "HEAD")["records"]}
            dr = {x["id"]: x for x in signals(tmp, "HEAD", reconsider=True)["records"]}
            check(d["ACME-7-AD2"]["candidate"] is False and d["ACME-7-AD2"]["promotion"] == "declined"
                  and d["ACME-7-AD2"]["promotion_note"] == "billing-only ledger", "a declined record is not a candidate")
            check(dr["ACME-7-AD2"]["candidate"] is True, "--reconsider proposes a declined record again")
        except Exception as e:
            check(False, "--signals after --mark: %s" % e)

        for bad, why in (({"ACME-7-AD3": {"promotion": "maybe"}}, "an unknown promotion value"),
                         ({"ACME-7-AD3": {"promotion": "proposed"}}, "proposed without promoted_to"),
                         ({"ACME-7-AD3": {"promotion": "declined"}}, "declined without a note"),
                         ({"ACME-7-AD3": {"promotion": "declined", "promotion_note": "x", "promoted_to": "ADR-1"}},
                          "declined with an ADR"),
                         ({"ACME-7-AD3": {"promotion": "declined", "promotion_note": "two\nlines"}}, "a two-line note"),
                         ({"../../x-AD1": {"promotion": "declined", "promotion_note": "x"}}, "a path, not a record id"),
                         ({"ACME-404-AD1": {"promotion": "declined", "promotion_note": "x"}}, "a record not in the tree"),
                         ({"ACME-7-AD3": {"promotion": "declined", "promotion_note": "x", "owner": "me"}}, "an unknown key"),
                         ({"ACME-7-AD2": None, "ACME-7-AD3": {"promotion": "maybe"}}, "a plan with one bad entry")):
            r = run_mark(tmp, bad)
            check(r.returncode == 2, "--mark refuses %s (rc=%d)" % (why, r.returncode))
        check(text(path2) == after2 and text(path3) == before3, "a refused plan writes nothing, not even its valid entries")

        r = run_mark(tmp, {"ACME-7-AD3": {"promotion": "proposed", "promoted_to": "ADR-0009"}}, "--check")
        check(r.returncode == 0 and text(path3) == before3
              and json.loads(r.stdout.decode("utf-8") or "{}").get("would_write") == [DECISIONS + "ACME-7-AD3.md"],
              "--mark --check validates and writes nothing: rc=%d %s" % (r.returncode, r.stdout[-200:]))
        check(run_mark(tmp, {"ACME-7-AD3": {"promotion": "maybe"}}, "--check").returncode == 2, "--mark --check refuses a bad plan")
        check(cli("--specs", tmp, "--ref", "HEAD", "--signals", "--check").returncode == 2, "--check goes only with --mark")
        r = run_mark(tmp, {"ACME-7-AD3": {"promotion": "covered", "promoted_to": "0005-use-outbox"}}, "--check")
        check(r.returncode == 0, "an ADR id need not be upper-case: a numbered file stem is one")
        check(run_mark(tmp, {"ACME-7-AD3": {"promotion": "covered", "promoted_to": "$(id)"}}, "--check").returncode == 2,
              "an id holding shell syntax is refused")
        check(run_mark(tmp, {"ACME-7-AD3": {"promotion": "covered", "promoted_to": "ADR-0004\n"}}, "--check").returncode == 2,
              "an id with a trailing newline is refused")
        r = run_mark(tmp, {"ACME-7-AD3": {"promotion": "proposed", "promoted_to": "ADR-0009"}})
        check(r.returncode == 0 and "promoted_to: ADR-0009" in text(path3), "--mark proposed with its ADR")
        snapshot(tmp, "mark AD3")

        # ---- the status forms an ADR is written in ---------------------------------------
        for body, want in (("---\nstatus: Accepted   # a comment\n---\n# X\n", "accepted"),
                           ("# X\n\n## Status\n\n**Accepted**\n", "accepted"),
                           ("# X\n\n## Status\n\n_Superseded_ by ADR-0009\n", "superseded"),
                           ("# X\n\n## Status: Rejected\n", "rejected"),
                           ("# X\n\n**Status:** Accepted\n", "accepted"),
                           ("# X\n\n- **Status**: Draft\n", "draft"),
                           ("# X\n\nStatus: Proposed\n", "proposed"),
                           ("# X\n\nNo status anywhere.\n", "unknown")):
            fm, bd = H.split_frontmatter(body)
            got = adr_status(H.fm_blocks(fm)[1], bd)
            check(got == want, "ADR status %r read as %r, not %r" % (body[:30], got, want))

        # ---- --reconcile ---------------------------------------------------------------
        with tempfile.TemporaryDirectory() as arch:
            init(arch)
            commit(arch, {
                "decisions/README.md": "# ADRs\n\nOrigin: team decisions ACME-7-AD3 — prose, not an ADR.\n",
                "decisions/ADR-0001-outbox.md": ("---\nid: ADR-0001\ntitle: Outbox\nstatus: accepted\n---\n"
                                                 "# ADR-0001: Outbox\n\n## Context\n\n"
                                                 "Origin: team decisions ACME-1-AD1 — specs ACME-55-AD9 mirror\n"),
                "decisions/ADR-0002-billing-ledger.md": ("# ADR-0002: Billing ledger\n\n## Status\n\n**Rejected**\n\n"
                                                         "## Context\n\nOrigin: team decisions ACME-7-AD2, ACME-99-AD1 — specs\n"),
                "decisions/ADR-0003-retries.md": ("---\nid: ADR-0003\nstatus: proposed   # proposed | accepted\n---\n"
                                                  "## Context\n\nOrigin: team decisions ACME-7-AD1 — specs.\n"),
                "standards/STD-API-001.md": "Origin: team decisions ACME-1-AD2 — not under an ADR folder.\n",
                "decisions/ADR-0006-retries-again.md": ("# ADR-0006: Retries\n\n**Status:** Rejected\n\n## Context\n\n"
                                                        "Origin: team decisions ACME-7-AD1 — specs\n"),
                "decisions/ADR-0008-outbox-twice.md": ("# ADR-0008: Outbox again\n\n## Status: Proposed\n\n## Context\n\n"
                                                       "Origin: team decisions ACME-1-AD1 — specs\n"),
                "decisions/ADR-0010-theirs.md": ("---\nid: ADR-0010\nstatus: accepted\n---\n## Context\n\n"
                                                 "Origin: team decisions ACME-404-AD1 — other-specs\n"),
                "decisions/ADR-0011-pondering.md": ("---\nid: ADR-0011\nstatus: pondering\n---\n## Context\n\n"
                                                    "Origin: team decisions ACME-1-AD2 — specs\n"),
                "decisions/ADR-0012-kafka.md": ("---\nid: ADR-0012\nstatus: proposed\n---\n## Context\n\n"
                                                "Proposes to supersede: ADR-0004.\n\nTwo VIs depart from it.\n"),
                "decisions/ADR-0013-shared.md": ("---\nid: ADR-0013\nstatus: rejected\n---\n## Context\n\n"
                                                 "Origin: team decisions ACME-404-AD1 — other-specs\n"
                                                 "Origin: team decisions ACME-1-AD1 — specs\n"),
                "decisions/ADR-0014-musing.md": ("---\nid: ADR-0014\nstatus: musing\n---\n## Context\n\n"
                                                 "Proposes to supersede: ADR-0005\n"),
                "decisions/ADR-0060-spaced.md": ("---\nid: ADR 0060\nstatus: accepted\n---\n## Context\n\n"
                                                 "Origin: team decisions ACME-1-AD2 — specs\n"),
            }, "adrs")
            try:
                rc = reconcile(tmp, "HEAD", arch, "HEAD", specs_name="specs")
            except Exception as e:
                rc = {"changes": [], "unresolved": [], "problems": [], "adrs": [], "superseding": []}
                check(False, "--reconcile runs: %s" % e)
            ch = {c["id"]: c["to"] for c in rc["changes"]}
            check(ch.get("ACME-1-AD1") == {"promotion": "accepted", "promoted_to": "ADR-0001"},
                  "an accepted ADR; a key-shaped word after the dash is not an id: %s" % ch.get("ACME-1-AD1"))
            check(ch.get("ACME-7-AD2") == {"promotion": "rejected", "promoted_to": "ADR-0002",
                                           "promotion_note": "ADR-0002 was rejected"},
                  "a rejected ADR, its status from a Status heading, its id from the file name: %s" % ch.get("ACME-7-AD2"))
            check(ch.get("ACME-7-AD1") == {"promotion": "proposed", "promoted_to": "ADR-0003"},
                  "a proposed ADR, its status comment stripped: %s" % ch.get("ACME-7-AD1"))
            check("ACME-1-AD2" not in ch, "an Origin line outside an ADR folder, or an ADR whose status is unreadable, changes nothing")
            check(rc["unresolved"] == [{"id": "ACME-7-AD3", "promoted_to": "ADR-0009"}],
                  "a proposed record whose ADR is on no Origin line: %s" % rc["unresolved"])
            check(sorted(p["kind"] for p in rc["problems"]) == ["invalid-id", "multiple-origins", "unknown-record",
                                                                "unknown-status", "unknown-status"]
                  and all(not a["file"].endswith("README.md") for a in rc["adrs"]),
                  "a README is not an ADR; an unknown record, two live ADRs for one record, an unreadable status "
                  "are problems; a rejected ADR beside a live one and another specs repository's line are not: %s"
                  % rc["problems"])
            check(rc.get("superseding") == [{"adr": "ADR-0004", "by": "ADR-0012"}],
                  "a proposed ADR that proposes to supersede another is listed, a trailing full stop dropped: %s"
                  % rc.get("superseding"))
            origins = {a["id"]: a["origin"] for a in rc["adrs"]}
            check(origins.get("ADR-0013") == ["ACME-1-AD1"] and origins.get("ADR-0003") == ["ACME-7-AD1"]
                  and "ADR 0060" not in origins,
                  "the Origin line naming this specs repository is read, wherever it stands and whatever ends it; "
                  "an ADR whose id is no id names nothing: %s" % origins)
            rel3 = DECISIONS + "ACME-7-AD3.md"
            commit(tmp, {rel3: text(path3).replace("promoted_to: ADR-0009", "promoted_to: $(id)")}, "hand edit")
            try:
                bad = reconcile(tmp, "HEAD", arch, "HEAD", specs_name="specs")
            except Exception as e:
                bad = {"unresolved": None, "problems": []}
                check(False, "--reconcile on a hand-edited key runs: %s" % e)
            check(bad["unresolved"] == [] and "invalid-key" in [p["kind"] for p in bad["problems"]],
                  "a hand-edited promoted_to that is no id is a problem, never a search term: %s" % bad["problems"])

        # ---- the CLI -------------------------------------------------------------------
        check(cli("--signals").returncode == 2, "--specs is required")
        check(cli("--specs", tmp, "--signals").returncode == 2, "--signals needs --ref")
        check(cli("--specs", tmp, "--ref", "no-such-ref", "--signals").returncode == 2, "an unknown ref cannot run")
        check(cli("--specs", tmp, "--ref", "HEAD", "--signals", "--mark", "x.json").returncode == 2, "one mode at a time")
        ok = cli("--specs", tmp, "--ref", "HEAD", "--signals")
        check(ok.returncode == 0 and json.loads(ok.stdout.decode("utf-8")).get("candidates") is not None,
              "--signals prints JSON")

    # ---- the prd layout ----------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        init(tmp)
        shop, pay = "specifications/PRD-ACME-90-shop/", "specifications/PRD-ACME-91-pay/"
        slice_ = "specifications/BRD-ACME-80-retail/PRD-ACME-81-loyalty/"
        one_db = "Shop uses one database"
        commit(tmp, {
            shop + "prd.md": "---\nkey: ACME-90\n---\n# Shop\n",
            shop + "ard.md": ard("Shop", [ad(1, one_db)], fm="key: ACME-90\nkind: ard\ncomponents:\n  - id: shop\n"),
            shop + "EPIC-ACME-90-01-cart/design.md": "Per %s.\n" % rec("ACME-90-AD1", one_db, 3),
            pay + "design.md": "Per %s.\n" % rec("ACME-90-AD1", one_db, 2),
            slice_ + "design.md": "Per %s.\n" % rec("ACME-90-AD1", one_db, 3),
        }, "prd fixtures")
        H.harvest(tmp, "HEAD", "prd", write=True)
        snapshot(tmp, "harvest")
        try:
            r = {x["id"]: x for x in signals(tmp, "HEAD", "prd")["records"]}.get("ACME-90-AD1", {})
        except Exception as e:
            r = {}
            check(False, "--signals --layout prd runs: %s" % e)
        check(r.get("group") == "ACME-90" and r.get("cited_by") == [slice_, pay],
              "prd: the deepest PRD- folder groups a citation; an Epic of the same PRD is its own: %s" % r.get("cited_by"))

    if failures:
        print("promotion-signals selftest: FAIL")
        for f in failures:
            print("  " + f)
        return 1
    print("promotion-signals selftest: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Promotion signals, reconciliation and keys for the team knowledge base.")
    ap.add_argument("--specs", help="the specs repository's top level")
    ap.add_argument("--ref", help="the specs ref to read: its default branch, or a commit")
    ap.add_argument("--layout", choices=sorted(H.GROUP), default="vi", help="vi (<KEY>_ARD.md) or prd (ard.md)")
    ap.add_argument("--signals", action="store_true", help="print every record's signals")
    ap.add_argument("--reconsider", action="store_true", help="count declined and rejected records as candidates")
    ap.add_argument("--reconcile", action="store_true", help="print the key changes the architecture repository implies")
    ap.add_argument("--arch", help="the architecture repository's top level")
    ap.add_argument("--arch-ref", help="the architecture ref to read: its default branch")
    ap.add_argument("--mark", metavar="PLAN", help="write the promotion keys a plan file names")
    ap.add_argument("--check", action="store_true", help="with --mark: validate the plan and write nothing")
    ap.add_argument("--specs-name", help="with --reconcile: count only the Origin lines naming this specs repository")
    ap.add_argument("--selftest", action="store_true", help="run the built-in fixtures and exit")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except AttributeError:
        pass
    if a.selftest:
        return selftest()
    modes = [m for m in ("signals", "reconcile", "mark") if getattr(a, m)]
    if len(modes) != 1 or not a.specs or (a.check and not a.mark):
        print("promotion-signals: give --specs and exactly one of --signals, --reconcile, --mark "
              "(--check only with --mark)", file=sys.stderr)
        return 2
    try:
        if a.signals:
            if not a.ref:
                raise Abort("--signals needs --ref")
            out = signals(a.specs, a.ref, a.layout, a.reconsider)
        elif a.reconcile:
            if not (a.ref and a.arch and a.arch_ref):
                raise Abort("--reconcile needs --ref, --arch and --arch-ref")
            out = reconcile(a.specs, a.ref, a.arch, a.arch_ref, a.specs_name)
        else:
            out = mark(a.specs, a.mark, a.check)
    except Exception as e:  # anything unexpected is "could not run", never a partial result
        print("promotion-signals: not run (%s: %s)" % (type(e).__name__, e), file=sys.stderr)
        return 2
    print(json.dumps(out, indent=2))  # ASCII-escaped: valid JSON on any stdout encoding
    return 0


if __name__ == "__main__":
    sys.exit(main())
