#!/usr/bin/env python3
"""question-registry.py — the registry of one run's questions: what became of each, the account that proves none vanished.

  question-registry.py init         --registry <file>   (stdin {"budget": N, "questions": [Q, ...]})
  question-registry.py add          --registry <file>   (stdin {"questions": [Q, ...]})
  question-registry.py merge        --registry <file> --into <qid> --from <qid>[,<qid>...] --reason <text> [--sitting <n>]
  question-registry.py drop         --registry <file> --qid <qid> --reason <text> [--sitting <n>]
  question-registry.py record       --registry <file> --sitting <n>   (stdin one event E)
  question-registry.py reopen       --registry <file> (--qid <qid> | --follows <decision-id>)
  question-registry.py next         --registry <file> [--limit <N>]
  question-registry.py sitting-list --registry <file> --sitting <n>
  question-registry.py account      --registry <file>
  question-registry.py --selftest

The registry is one JSON file: {"version": 1, "budget": N, "generated": {"V": n, "C": n, "DEF": n},
"questions": {<qid>: {...}}}, the questions in the order they were added. "generated" is counted when a
question enters the file, by the tag it entered with, and no later call rewrites it; the account measures
every question still in the file against it, so a question that leaves the file leaves a gap.

Q = {"qid": ^[A-Za-z0-9/._-]+$, "tag": "V"|"C"|"DEF", "text", "rows": ["[BR#n]"], "findings": ["[CG#n]"|"[DG#n]"],
"strategic": bool, "covers": [qid], "carried": bool, "rank": int, "recommendation": str|null,
"confidence": "high"|"medium"|"low"|null}. Only qid, tag and text are required. A Q may also carry the state
fields of a question a round already wrote -- state (open|merged|dropped|auto|applied|table|answered|deferred),
into, reason, decision, applied_from, answer, proposed, sitting, original_tag -- and they are checked as an
event would be.

E = {"qid", "event": answered|applied|table|deferred|auto|narrowed|proposed|retagged, "decision"?,
"applied_from"?, "answer"?, "reason"?, "text"?, "tag"?}. answered, applied, table, deferred and auto close
the question and record --sitting on it; narrowed sets its text, proposed sets its proposed answer, retagged
changes its tag (the account then counts it retagged out of its first tag and retagged in to the new one);
those three leave it open. A decision id is [VD#n], [CD#n] or <KEY>/[VD#n] with <KEY> matching
^[A-Z][A-Z0-9_]*(-[0-9]+)+$; for tag DEF it is one of confirmed, confirmed-narrowed, not-logged,
noted-in-inventory, sent-on-unreviewed.

reopen --follows X reopens every question whose applied_from is X, then every question whose applied_from is
the decision of one just reopened, and so on; reopen --qid reopens that one question. Either clears its
decision, applied_from, answer, reason, into and sitting and sets it open; prints the reopened qids.
next prints the open, not carried, qids: open strategic first, then by rank, then by qid; default limit is
the budget. sitting-list prints markdown: "### Applied from <decision-id>" groups, "### Merged",
"### Dropped", "### Confirmed in a table", for the questions of that sitting; an empty group is left out.
account prints {"V": {...}, "C": {...}, "DEF": {...}, "closes": bool}, each tag's eleven counts: generated,
retagged_in, merged, dropped, auto, applied, table, answered, deferred, open, retagged_out.

It refuses, and writes nothing, on: an unknown qid; an event on a question that is not open; any event but
proposed on a carried question; answered, applied or table on tag C; applied without applied_from and
decision; answered or table without a decision; auto on a tag other than DEF; deferred on tag DEF with a
decision other than sent-on-unreviewed; retagged without tag and reason, or to the same tag; narrowed
without text; proposed without answer; a merge across tags, into a question that is not open, or of a
carried question; a drop of a carried question; a reopen of a carried question or of one already open; init
over an existing registry; a Q or an event that does not match the shape above.

Exit 0: it ran. Exit 3: it refused the caller's input, which it can rebuild and send once more. Exit 2: the
registry is absent, unreadable or invalid (a state no column holds, a missing field), or cannot be written.
Exit 4: account only -- some tag's generated + retagged_in is not merged + dropped + auto + applied + table +
answered + deferred + open + retagged_out; the account is still printed. A refusal writes nothing, and so
does a failed write; the cause is one line on stderr. No output names a path. Python standard library only.

The registry is written whole to a temporary file beside it, which then replaces it, so a write that fails
part-way leaves the registry as it was and no temporary file behind.
"""

import argparse
import contextlib
import io
import json
import os
import re
import sys
import tempfile

TAGS = ("V", "C", "DEF")
STATES = ("open", "merged", "dropped", "auto", "applied", "table", "answered", "deferred")
CLOSING = ("answered", "applied", "table", "deferred", "auto")
EVENTS = CLOSING + ("narrowed", "proposed", "retagged")
EVENT_KEYS = {"qid", "event", "decision", "applied_from", "answer", "reason", "text", "tag"}
CONFIDENCE = ("high", "medium", "low")
DEF_DECISIONS = ("confirmed", "confirmed-narrowed", "not-logged", "noted-in-inventory", "sent-on-unreviewed")
COLUMNS = ("generated", "retagged_in", "merged", "dropped", "auto", "applied", "table", "answered", "deferred",
           "open", "retagged_out")

QID_RE = re.compile(r"[A-Za-z0-9/._-]+")
ROW_RE = re.compile(r"\[BR#[1-9][0-9]*\]")
FINDING_RE = re.compile(r"\[(?:CG|DG)#[1-9][0-9]*\]")
DECISION_RE = re.compile(r"(?:[A-Z][A-Z0-9_]*(?:-[0-9]+)+/)?\[(?:VD|CD)#[1-9][0-9]*\]")

BLANK = (("qid", None), ("tag", None), ("original_tag", None), ("text", None), ("rows", []), ("findings", []),
         ("strategic", False), ("covers", []), ("carried", False), ("rank", 0), ("recommendation", None),
         ("confidence", None), ("state", "open"), ("into", None), ("reason", None), ("decision", None),
         ("applied_from", None), ("answer", None), ("proposed", None), ("sitting", 0))
FIELDS = tuple(name for name, _ in BLANK)


class Refused(Exception):
    """The registry cannot be read or written by the rule; main() prints the message and exits 2."""


class InputRefused(Refused):
    """The caller's input is not one the rule can apply; main() prints the message and exits 3."""


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _is_text(value):
    return isinstance(value, str) and bool(value.strip())


def _one_line(text):
    return " ".join(str(text).split())


# ---- reading and writing the registry ----

def _read(path):
    try:
        with open(path, encoding="utf-8", newline="") as fh:
            text = fh.read()
    except UnicodeDecodeError:
        raise Refused("the registry is not UTF-8 text")
    except OSError as e:
        raise Refused("cannot read the registry: %s" % (e.strerror or type(e).__name__))
    try:
        return json.loads(text)
    except ValueError:
        raise Refused("the registry is not JSON")


def _write_body(fh, text):
    fh.write(text)


_replace = os.replace


def _write(path, registry):
    """Writes the whole registry to a temporary file in its own directory, then renames it over the registry."""
    text = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
    target = os.path.realpath(path)
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(target), prefix=".question-registry.", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            _write_body(fh, text)
        if os.path.exists(target):
            os.chmod(tmp, os.stat(target).st_mode & 0o777)
        else:
            umask = os.umask(0)
            os.umask(umask)
            os.chmod(tmp, 0o666 & ~umask)
        _replace(tmp, target)
        tmp = None
    except OSError as e:
        raise Refused("cannot write the registry: %s" % (e.strerror or type(e).__name__))
    finally:
        if tmp is not None:
            with contextlib.suppress(OSError):
                os.remove(tmp)


def _check_decision(value, tag, exc, what):
    if not isinstance(value, str):
        raise exc("%s is not a decision id" % what)
    if tag == "DEF":
        if value not in DEF_DECISIONS:
            raise exc("%s %s is not one of %s, which a DEF question takes" % (what, json.dumps(value), ", ".join(DEF_DECISIONS)))
    elif not DECISION_RE.fullmatch(value):
        raise exc("%s %s is not a [VD#n], [CD#n] or <KEY>/[VD#n] decision id" % (what, json.dumps(value)))


def _check_question(raw, exc, stored):
    """The question as the registry holds it, every field present. Raises exc where the shape or the state does not hold."""
    if not isinstance(raw, dict):
        raise exc("a question is not a JSON object")
    qid = raw.get("qid")
    label = "question %s" % json.dumps(qid) if isinstance(qid, str) else "a question"
    unknown = sorted(set(raw) - set(FIELDS))
    if unknown:
        raise exc("%s carries %s, which no question has" % (label, ", ".join(unknown)))
    if stored:
        absent = [name for name in FIELDS if name not in raw]
        if absent:
            raise exc("%s lacks %s" % (label, ", ".join(absent)))
    q = {name: raw[name] if name in raw else (list(default) if isinstance(default, list) else default)
         for name, default in BLANK}
    if not isinstance(qid, str) or not QID_RE.fullmatch(qid):
        raise exc("%s has no qid of letters, digits and / . _ -" % label)
    if q["tag"] not in TAGS:
        raise exc("%s has the tag %s, not one of %s" % (label, json.dumps(q["tag"]), ", ".join(TAGS)))
    if "original_tag" not in raw:
        q["original_tag"] = q["tag"]
    if q["original_tag"] not in TAGS:
        raise exc("%s has the original_tag %s" % (label, json.dumps(q["original_tag"])))
    if not _is_text(q["text"]):
        raise exc("%s has no text" % label)
    for name, pattern in (("rows", ROW_RE), ("findings", FINDING_RE), ("covers", QID_RE)):
        if not isinstance(q[name], list) or not all(isinstance(v, str) and pattern.fullmatch(v) for v in q[name]):
            raise exc("%s has %s that is not a list of well-formed ids" % (label, name))
    for name in ("strategic", "carried"):
        if not isinstance(q[name], bool):
            raise exc("%s has %s that is not true or false" % (label, name))
    if not _is_int(q["rank"]):
        raise exc("%s has a rank that is not a whole number" % label)
    if q["recommendation"] is not None and not isinstance(q["recommendation"], str):
        raise exc("%s has a recommendation that is neither text nor null" % label)
    if q["confidence"] is not None and q["confidence"] not in CONFIDENCE:
        raise exc("%s has a confidence that is not high, medium, low or null" % label)
    if q["state"] not in STATES:
        raise exc("%s has the state %s, which no account column holds" % (label, json.dumps(q["state"])))
    if not _is_int(q["sitting"]) or q["sitting"] < 0:
        raise exc("%s has a sitting that is not a whole number from 0" % label)
    for name in ("into", "reason", "decision", "applied_from", "answer", "proposed"):
        if q[name] is not None and not isinstance(q[name], str):
            raise exc("%s has %s that is neither text nor null" % (label, name))
    _check_state(q, exc, label)
    return q


def _check_state(q, exc, label):
    """The fields a closed question must carry, and the tags that may close this way."""
    state, tag = q["state"], q["tag"]
    if q["decision"] is not None:
        _check_decision(q["decision"], tag, exc, "%s decision" % label)
    if q["applied_from"] is not None and not DECISION_RE.fullmatch(q["applied_from"]):
        raise exc("%s has an applied_from that is not a decision id" % label)
    if state in ("answered", "applied", "table") and tag == "C":
        raise exc("%s is tag C and cannot be %s" % (label, state))
    if state == "auto" and tag != "DEF":
        raise exc("%s is not tag DEF and cannot be auto" % label)
    if state in ("answered", "applied", "table") and q["decision"] is None:
        raise exc("%s is %s without a decision" % (label, state))
    if state == "applied" and q["applied_from"] is None:
        raise exc("%s is applied without an applied_from" % label)
    if state == "merged" and not (isinstance(q["into"], str) and QID_RE.fullmatch(q["into"])):
        raise exc("%s is merged without the qid it merged into" % label)
    if state == "deferred" and tag == "DEF" and q["decision"] not in (None, "sent-on-unreviewed"):
        raise exc("%s is a deferred DEF question with a decision other than sent-on-unreviewed" % label)


def _load(path):
    raw = _read(path)
    if not isinstance(raw, dict) or raw.get("version") != 1:
        raise Refused("the registry is not a version 1 registry")
    if not _is_int(raw.get("budget")) or raw["budget"] < 1:
        raise Refused("the registry has no budget")
    generated = raw.get("generated")
    if not isinstance(generated, dict) or set(generated) != set(TAGS) or not all(
            _is_int(n) and n >= 0 for n in generated.values()):
        raise Refused("the registry's generated counts are not one whole number for each of V, C, DEF")
    if not isinstance(raw.get("questions"), dict):
        raise Refused("the registry holds no questions object")
    questions = {}
    for qid, entry in raw["questions"].items():
        q = _check_question(entry, Refused, True)
        if q["qid"] != qid:
            raise Refused("the registry holds question %s under the key %s" % (json.dumps(q["qid"]), json.dumps(qid)))
        questions[qid] = q
    return {"version": 1, "budget": raw["budget"], "generated": {t: generated[t] for t in TAGS},
            "questions": questions}


def _parse_stdin(text, what):
    try:
        data = json.loads(text)
    except ValueError as e:
        raise InputRefused("standard input is not JSON: %s" % e)
    if not isinstance(data, dict):
        raise InputRefused("standard input is not one JSON object holding %s" % what)
    return data


def _positive(text, what, floor=1):
    try:
        value = int(text)
        if str(value) != str(text).strip().lstrip("+") or value < floor:
            raise ValueError
    except ValueError:
        raise InputRefused("%s takes a whole number from %d" % (what, floor))
    return value


def _add(registry, items):
    """Appends Q objects: each checked, none already held; counts each in generated by the tag it enters with."""
    if not isinstance(items, list):
        raise InputRefused("questions is not a list")
    fresh = {}
    for item in items:
        q = _check_question(item, InputRefused, False)
        if q["qid"] in registry["questions"] or q["qid"] in fresh:
            raise InputRefused("question %s is already in the registry or named twice" % json.dumps(q["qid"]))
        fresh[q["qid"]] = q
    for q in fresh.values():
        registry["questions"][q["qid"]] = q
        registry["generated"][q["original_tag"]] += 1
    return len(fresh)


# ---- the subcommands ----

def init(path, text):
    data = _parse_stdin(text, "budget and questions")
    if set(data) != {"budget", "questions"}:
        raise InputRefused("init takes budget and questions, and nothing else")
    if not _is_int(data["budget"]) or data["budget"] < 1:
        raise InputRefused("the budget is not a whole number from 1")
    if os.path.exists(path):
        raise InputRefused("a registry already exists there; init does not replace one")
    registry = {"version": 1, "budget": data["budget"], "generated": {t: 0 for t in TAGS}, "questions": {}}
    _add(registry, data["questions"])
    _write(path, registry)
    return {"budget": registry["budget"], "questions": len(registry["questions"])}


def add(path, text):
    data = _parse_stdin(text, "questions")
    if set(data) != {"questions"}:
        raise InputRefused("add takes questions, and nothing else")
    registry = _load(path)
    count = _add(registry, data["questions"])
    _write(path, registry)
    return {"added": count}


def _open_question(registry, qid, what):
    q = registry["questions"].get(qid)
    if q is None:
        raise InputRefused("%s %s is not in the registry" % (what, json.dumps(qid)))
    if q["carried"]:
        raise InputRefused("%s %s is carried" % (what, qid))
    if q["state"] != "open":
        raise InputRefused("%s %s is %s, not open" % (what, qid, q["state"]))
    return q


def merge(path, into, froms, reason, sitting):
    if not _is_text(reason):
        raise InputRefused("a merge takes a reason")
    sitting = _positive(sitting, "--sitting", 0)
    sources = froms.split(",")
    if not all(QID_RE.fullmatch(s) for s in sources) or len(set(sources)) != len(sources) or into in sources:
        raise InputRefused("--from takes distinct qids, other than --into, separated by commas")
    registry = _load(path)
    target = _open_question(registry, into, "the question merged into,")
    for qid in sources:
        q = _open_question(registry, qid, "the question merged,")
        if q["tag"] != target["tag"]:
            raise InputRefused("%s is tag %s and %s is tag %s; a merge does not cross tags"
                               % (qid, q["tag"], into, target["tag"]))
    for qid in sources:
        q = registry["questions"][qid]
        q.update(state="merged", into=into, reason=reason, sitting=sitting)
    _write(path, registry)
    return {"merged": sources, "into": into}


def drop(path, qid, reason, sitting):
    if not _is_text(reason):
        raise InputRefused("a drop takes a reason")
    sitting = _positive(sitting, "--sitting", 0)
    registry = _load(path)
    q = _open_question(registry, qid, "the question dropped,")
    q.update(state="dropped", reason=reason, sitting=sitting)
    _write(path, registry)
    return {"dropped": qid}


def _text_field(event, name):
    value = event.get(name)
    if value is not None and not isinstance(value, str):
        raise InputRefused("the event's %s is not text" % name)
    return value


def record(path, text, sitting):
    sitting = _positive(sitting, "--sitting")
    event = _parse_stdin(text, "one event")
    unknown = sorted(set(event) - EVENT_KEYS)
    if unknown:
        raise InputRefused("the event carries %s, which no event has" % ", ".join(unknown))
    kind, qid = event.get("event"), event.get("qid")
    if kind not in EVENTS:
        raise InputRefused("the event %s is not one of %s" % (json.dumps(kind), ", ".join(EVENTS)))
    if not isinstance(qid, str):
        raise InputRefused("the event names no qid")
    registry = _load(path)
    q = registry["questions"].get(qid)
    if q is None:
        raise InputRefused("question %s is not in the registry" % json.dumps(qid))
    if q["state"] != "open":
        raise InputRefused("%s is %s, not open" % (qid, q["state"]))
    if q["carried"] and kind != "proposed":
        raise InputRefused("%s is carried, and a carried question takes only a proposed answer" % qid)
    decision, applied_from = _text_field(event, "decision"), _text_field(event, "applied_from")
    answer, reason, new_text = (_text_field(event, n) for n in ("answer", "reason", "text"))
    if decision is not None:
        _check_decision(decision, q["tag"], InputRefused, "the decision")
    if applied_from is not None and not DECISION_RE.fullmatch(applied_from):
        raise InputRefused("the applied_from %s is not a decision id" % json.dumps(applied_from))
    if kind in ("answered", "applied", "table") and q["tag"] == "C":
        raise InputRefused("%s is tag C, which %s does not close" % (qid, kind))
    if kind == "auto" and q["tag"] != "DEF":
        raise InputRefused("%s is tag %s; only a DEF question closes auto" % (qid, q["tag"]))
    if kind in ("answered", "table", "applied") and decision is None:
        raise InputRefused("%s takes a decision" % kind)
    if kind == "applied" and applied_from is None:
        raise InputRefused("applied takes an applied_from")
    if kind == "deferred" and q["tag"] == "DEF" and decision not in (None, "sent-on-unreviewed"):
        raise InputRefused("a DEF question is deferred only with the decision sent-on-unreviewed")
    if kind in CLOSING:
        q.update(state=kind, decision=decision, applied_from=applied_from if kind == "applied" else None,
                 answer=answer, reason=reason, sitting=sitting)
    elif kind == "narrowed":
        if not _is_text(new_text):
            raise InputRefused("narrowed takes text")
        q["text"] = new_text
    elif kind == "proposed":
        if not _is_text(answer):
            raise InputRefused("proposed takes an answer")
        q["proposed"] = answer
    else:
        new_tag = event.get("tag")
        if new_tag not in TAGS or not _is_text(reason):
            raise InputRefused("retagged takes a tag (V, C or DEF) and a reason")
        if new_tag == q["tag"]:
            raise InputRefused("%s is already tag %s" % (qid, new_tag))
        q.update(tag=new_tag, reason=reason)
    _write(path, registry)
    return {"qid": qid, "state": q["state"], "tag": q["tag"]}


def _reopen_one(q):
    q.update(state="open", into=None, reason=None, decision=None, applied_from=None, answer=None, sitting=0)


def reopen(path, qid, follows):
    registry = _load(path)
    reopened = []
    if qid is not None:
        q = registry["questions"].get(qid)
        if q is None:
            raise InputRefused("question %s is not in the registry" % json.dumps(qid))
        if q["carried"]:
            raise InputRefused("%s is carried, and a carried question is not reopened" % qid)
        if q["state"] == "open":
            raise InputRefused("%s is already open" % qid)
        _reopen_one(q)
        reopened.append(qid)
    else:
        if not DECISION_RE.fullmatch(follows):
            raise InputRefused("--follows takes a decision id")
        pending, seen = [follows], {follows}
        while pending:
            source = pending.pop(0)
            for q in registry["questions"].values():
                if q["applied_from"] == source and q["state"] != "open":
                    freed = q["decision"]
                    _reopen_one(q)
                    reopened.append(q["qid"])
                    if freed is not None and freed not in seen:
                        seen.add(freed)
                        pending.append(freed)
    if reopened:
        _write(path, registry)
    return reopened


def next_qids(path, limit):
    registry = _load(path)
    limit = registry["budget"] if limit is None else _positive(limit, "--limit")
    live = [q for q in registry["questions"].values() if q["state"] == "open" and not q["carried"]]
    live.sort(key=lambda q: (not q["strategic"], q["rank"], q["qid"]))
    return [q["qid"] for q in live[:limit]]


def sitting_list(path, sitting):
    sitting = _positive(sitting, "--sitting")
    mine = [q for q in _load(path)["questions"].values() if q["sitting"] == sitting]
    groups = {}
    for q in mine:
        if q["state"] == "applied":
            groups.setdefault(q["applied_from"], []).append(
                "- %s: %s (%s)" % (q["qid"], _one_line(q["answer"] or ""), _one_line(q["reason"] or "")))
    out = []
    for source, lines in groups.items():
        out += ["### Applied from %s" % source] + lines + [""]
    for state, heading, line in (
            ("merged", "### Merged", lambda q: "- %s merged into %s: %s" % (q["qid"], q["into"], _one_line(q["reason"] or ""))),
            ("dropped", "### Dropped", lambda q: "- %s: %s" % (q["qid"], _one_line(q["reason"] or ""))),
            ("table", "### Confirmed in a table", lambda q: "- %s: %s" % (q["qid"], _one_line(q["answer"] or q["text"])))):
        lines = [line(q) for q in mine if q["state"] == state]
        if lines:
            out += [heading] + lines + [""]
    return "\n".join(out)


def account(path):
    registry = _load(path)
    acct = {t: dict.fromkeys(COLUMNS, 0) for t in TAGS}
    for tag in TAGS:
        acct[tag]["generated"] = registry["generated"][tag]
    for q in registry["questions"].values():
        acct[q["tag"]][q["state"]] += 1
        if q["tag"] != q["original_tag"]:
            acct[q["tag"]]["retagged_in"] += 1
            acct[q["original_tag"]]["retagged_out"] += 1
    short = []
    for tag, c in acct.items():
        if c["generated"] + c["retagged_in"] != sum(c[k] for k in COLUMNS[2:]):
            short.append(tag)
    acct["closes"] = not short
    return acct, short


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    parser = argparse.ArgumentParser(prog="question-registry.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    def command(name, *options):
        p = sub.add_parser(name)
        p.add_argument("--registry", required=True)
        for flag, kw in options:
            p.add_argument(flag, **kw)
        return p

    command("init")
    command("add")
    command("merge", ("--into", {"required": True}), ("--from", {"required": True, "dest": "sources"}),
            ("--reason", {"required": True}), ("--sitting", {"default": "0"}))
    command("drop", ("--qid", {"required": True}), ("--reason", {"required": True}), ("--sitting", {"default": "0"}))
    command("record", ("--sitting", {"required": True}))
    command("next", ("--limit", {"default": None}))
    command("sitting-list", ("--sitting", {"required": True}))
    command("account")
    reopen_p = command("reopen")
    group = reopen_p.add_mutually_exclusive_group(required=True)
    group.add_argument("--qid")
    group.add_argument("--follows")
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:  # a usage error is the caller's input refused; --help is a run
        return 3 if e.code else 0
    try:
        c, path = args.command, args.registry
        if c == "init":
            print(json.dumps(init(path, sys.stdin.read())))
        elif c == "add":
            print(json.dumps(add(path, sys.stdin.read())))
        elif c == "merge":
            print(json.dumps(merge(path, args.into, args.sources, args.reason, args.sitting)))
        elif c == "drop":
            print(json.dumps(drop(path, args.qid, args.reason, args.sitting)))
        elif c == "record":
            print(json.dumps(record(path, sys.stdin.read(), args.sitting)))
        elif c == "reopen":
            print("".join(q + "\n" for q in reopen(path, args.qid, args.follows)), end="")
        elif c == "next":
            print("".join(q + "\n" for q in next_qids(path, args.limit)), end="")
        elif c == "sitting-list":
            print(sitting_list(path, args.sitting), end="")
        else:
            acct, short = account(path)
            print(json.dumps(acct))
            if short:
                print("question-registry: the account does not close for %s" % ", ".join(short), file=sys.stderr)
                return 4
    except InputRefused as e:
        print("question-registry: %s" % e, file=sys.stderr)
        return 3
    except Refused as e:
        print("question-registry: %s" % e, file=sys.stderr)
        return 2
    except (OSError, UnicodeError) as e:
        print("question-registry: %s" % type(e).__name__, file=sys.stderr)
        return 2
    return 0


# ---- self-test ----

def _q(qid, tag="V", **kw):
    q = {"qid": qid, "tag": tag, "text": "Question %s?" % qid}
    q.update(kw)
    return q


def _main_with(argv, stdin=""):
    out, err = io.StringIO(), io.StringIO()
    real = sys.stdin
    sys.stdin = io.StringIO(stdin)
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
    finally:
        sys.stdin = real
    return code, out.getvalue(), err.getvalue()


def _reg(tmp):
    return os.path.join(tmp, "registry.json")


def _run(tmp, command, extra=(), stdin=None):
    """One CLI call against the case's registry: (exit code, standard output, standard error)."""
    if stdin is not None and not isinstance(stdin, str):
        stdin = json.dumps(stdin)
    code, out, err = _main_with([command, "--registry", _reg(tmp)] + list(extra), stdin or "")
    assert tmp not in out + err, "printed a path: %r %r" % (out, err)
    return code, out, err


def _init(tmp, questions, budget=25):
    code, out, err = _run(tmp, "init", stdin={"budget": budget, "questions": questions})
    assert code == 0, (code, out, err)


def _event(tmp, sitting=1, **event):
    return _run(tmp, "record", ["--sitting", str(sitting)], stdin=event)


def _get(tmp):
    with open(_reg(tmp), encoding="utf-8") as fh:
        return fh.read()


def _state(tmp):
    return json.loads(_get(tmp))["questions"]


def _account(tmp):
    code, out, err = _run(tmp, "account")
    return code, json.loads(out), err


def _unchanged(tmp, before, code, want=3):
    assert code == want, "exit %s, wanted %s" % (code, want)
    assert _get(tmp) == before, "the registry changed on a refusal"


def case_init_and_account_closes(tmp):
    _init(tmp, [_q("1/1"), _q("1/2"), _q("1/3"), _q("1/4"), _q("1/5")])
    code, acct, err = _account(tmp)
    assert code == 0 and acct["closes"] is True, (code, acct, err)
    assert acct["V"]["generated"] == 5 and acct["V"]["open"] == 5, acct
    assert set(acct["V"]) == {"generated", "retagged_in", "merged", "dropped", "auto", "applied", "table",
                              "answered", "deferred", "open", "retagged_out"}, acct
    assert acct["C"]["generated"] == 0 and acct["DEF"]["generated"] == 0, acct
    assert set(_state(tmp)) == {"1/1", "1/2", "1/3", "1/4", "1/5"}
    assert all(q["state"] == "open" for q in _state(tmp).values())


def case_init_refuses_existing_registry(tmp):
    _init(tmp, [_q("1/1")])
    before = _get(tmp)
    code, out, err = _run(tmp, "init", stdin={"budget": 10, "questions": [_q("9/9")]})
    _unchanged(tmp, before, code)
    assert err.startswith("question-registry: "), err


def case_init_and_add_refuse_a_malformed_question(tmp):
    bad = [
        _q("a b"), _q("1/1", tag="G"), _q("1/1", text=""), _q("1/1", rows=["BR#1"]), _q("1/1", findings=["[BR#1]"]),
        _q("1/1", rank="1"), _q("1/1", confidence="certain"), _q("1/1", strategic="yes"), _q("1/1", covers=["a b"]),
        _q("1/1", state="gone"), _q("1/1", surprise=1), _q("1/1", state="answered"),
        _q("1/1", tag="C", state="answered", decision="[CD#1]"),
        _q("1/1", tag="V", state="auto"), _q("1/1", state="merged"),
    ]
    for q in bad:
        code, out, err = _run(tmp, "init", stdin={"budget": 5, "questions": [q]})
        assert code == 3 and not os.path.exists(_reg(tmp)), (q, code, err)
    for stdin in ("not json", "[]", '{"budget": 0, "questions": []}', '{"budget": 5}',
                  '{"budget": 5, "questions": [], "x": 1}',
                  json.dumps({"budget": 5, "questions": [_q("1/1"), _q("1/1")]})):
        code, out, err = _run(tmp, "init", stdin=stdin)
        assert code == 3 and not os.path.exists(_reg(tmp)), (stdin, code, err)
    _init(tmp, [_q("1/1")])
    before = _get(tmp)
    code, out, err = _run(tmp, "add", stdin={"questions": [_q("1/1")]})
    _unchanged(tmp, before, code)
    code, out, err = _run(tmp, "add", stdin={"questions": [_q("2/1"), _q("2/1")]})
    _unchanged(tmp, before, code)


def case_add_appends_in_order_and_counts_strategic(tmp):
    _init(tmp, [_q("1/1")])
    code, out, err = _run(tmp, "add", stdin={"questions": [_q("cand/1", strategic=True), _q("2/1", tag="C")]})
    assert code == 0, (code, err)
    assert list(_state(tmp)) == ["1/1", "cand/1", "2/1"]
    code, acct, err = _account(tmp)
    assert code == 0 and acct["V"]["generated"] == 2 and acct["C"]["generated"] == 1 and acct["closes"], acct


def case_merge_records_and_counts(tmp):
    _init(tmp, [_q("1/1"), _q("1/2"), _q("1/3")])
    code, out, err = _run(tmp, "merge", ["--into", "1/1", "--from", "1/2,1/3", "--reason", "same ask", "--sitting", "2"])
    assert code == 0, (code, err)
    st = _state(tmp)
    assert st["1/1"]["state"] == "open"
    for qid in ("1/2", "1/3"):
        assert st[qid]["state"] == "merged" and st[qid]["into"] == "1/1", st[qid]
        assert st[qid]["reason"] == "same ask" and st[qid]["sitting"] == 2, st[qid]
    code, acct, err = _account(tmp)
    assert code == 0 and acct["closes"] is True, acct
    assert acct["V"]["merged"] == 2 and acct["V"]["open"] == 1 and acct["V"]["generated"] == 3, acct


def case_merge_across_tags_refused(tmp):
    _init(tmp, [_q("1/1"), _q("1/2", tag="C"), _q("1/3", carried=True), _q("1/4"), _q("1/5", carried=True)])
    _event(tmp, qid="1/4", event="answered", decision="[VD#1]")
    before = _get(tmp)
    for into, frm in (("1/1", "1/2"), ("1/2", "1/1"), ("1/1", "1/3"), ("1/3", "1/1"), ("1/1", "1/4"),
                      ("1/4", "1/1"), ("1/1", "1/1"), ("1/1", "9/9"), ("9/9", "1/1")):
        code, out, err = _run(tmp, "merge", ["--into", into, "--from", frm, "--reason", "x"])
        _unchanged(tmp, before, code)
    code, out, err = _run(tmp, "merge", ["--into", "1/1", "--from", "", "--reason", "x"])
    _unchanged(tmp, before, code)
    code, out, err = _run(tmp, "merge", ["--into", "1/1", "--from", "1/2", "--reason", " "])
    _unchanged(tmp, before, code)


def case_drop_records_and_refuses(tmp):
    _init(tmp, [_q("1/1"), _q("1/2", carried=True)])
    before = _get(tmp)
    for qid, reason in (("1/2", "x"), ("9/9", "x"), ("1/1", "")):
        code, out, err = _run(tmp, "drop", ["--qid", qid, "--reason", reason])
        _unchanged(tmp, before, code)
    code, out, err = _run(tmp, "drop", ["--qid", "1/1", "--reason", "out of scope", "--sitting", "3"])
    assert code == 0, err
    q = _state(tmp)["1/1"]
    assert (q["state"], q["reason"], q["sitting"]) == ("dropped", "out of scope", 3), q
    code, acct, err = _account(tmp)
    assert code == 0 and acct["V"]["dropped"] == 1 and acct["V"]["open"] == 1 and acct["closes"], acct
    code, out, err = _run(tmp, "drop", ["--qid", "1/1", "--reason", "again"])
    assert code == 3, "a dropped question dropped again"


def case_applied_requires_from_and_decision(tmp):
    _init(tmp, [_q("1/1")])
    before = _get(tmp)
    for ev in ({"qid": "1/1", "event": "applied"},
               {"qid": "1/1", "event": "applied", "decision": "[VD#2]"},
               {"qid": "1/1", "event": "applied", "applied_from": "[VD#1]"}):
        code, out, err = _event(tmp, **ev)
        _unchanged(tmp, before, code)
    code, out, err = _event(tmp, sitting=4, qid="1/1", event="applied", decision="[VD#2]", applied_from="[VD#1]",
                            answer="Yes", reason="follows the earlier answer")
    assert code == 0, (code, err)
    q = _state(tmp)["1/1"]
    assert (q["state"], q["decision"], q["applied_from"], q["answer"], q["sitting"]) == \
        ("applied", "[VD#2]", "[VD#1]", "Yes", 4), q


def case_answered_and_table_require_a_decision(tmp):
    _init(tmp, [_q("1/1"), _q("1/2")])
    before = _get(tmp)
    for event in ("answered", "table"):
        code, out, err = _event(tmp, qid="1/1", event=event)
        _unchanged(tmp, before, code)
    assert _event(tmp, qid="1/1", event="answered", decision="[VD#1]", answer="No")[0] == 0
    assert _event(tmp, qid="1/2", event="table", decision="PRD-7-02/[VD#3]")[0] == 0
    st = _state(tmp)
    assert st["1/1"]["state"] == "answered" and st["1/2"]["state"] == "table", st


def case_applied_on_C_refused(tmp):
    _init(tmp, [_q("1/1", tag="C")])
    before = _get(tmp)
    for ev in ({"event": "applied", "decision": "[CD#2]", "applied_from": "[CD#1]"},
               {"event": "answered", "decision": "[CD#1]"}, {"event": "table", "decision": "[CD#1]"}):
        code, out, err = _event(tmp, qid="1/1", **ev)
        _unchanged(tmp, before, code)
    assert _event(tmp, qid="1/1", event="deferred", decision="[CD#1]")[0] == 0
    assert _state(tmp)["1/1"]["state"] == "deferred"


def case_auto_only_for_DEF(tmp):
    _init(tmp, [_q("1/1"), _q("1/2", tag="C"), _q("1/3", tag="DEF")])
    before = _get(tmp)
    for qid in ("1/1", "1/2"):
        code, out, err = _event(tmp, qid=qid, event="auto", decision="confirmed")
        _unchanged(tmp, before, code)
    assert _event(tmp, qid="1/3", event="auto", decision="confirmed")[0] == 0
    code, acct, err = _account(tmp)
    assert acct["DEF"]["auto"] == 1 and acct["DEF"]["open"] == 0 and acct["closes"], acct


def case_DEF_decisions_use_their_own_vocabulary(tmp):
    _init(tmp, [_q("1/1", tag="DEF"), _q("1/2", tag="DEF"), _q("1/3", tag="DEF"), _q("1/4", tag="DEF")])
    before = _get(tmp)
    for ev in ({"qid": "1/1", "event": "answered", "decision": "[VD#1]"},
               {"qid": "1/1", "event": "answered", "decision": "maybe"},
               {"qid": "1/1", "event": "deferred", "decision": "confirmed"}):
        code, out, err = _event(tmp, **ev)
        _unchanged(tmp, before, code)
    assert _event(tmp, qid="1/1", event="deferred", decision="sent-on-unreviewed")[0] == 0
    assert _event(tmp, qid="1/2", event="answered", decision="confirmed-narrowed")[0] == 0
    assert _event(tmp, qid="1/3", event="table", decision="noted-in-inventory")[0] == 0
    assert _event(tmp, qid="1/4", event="answered", decision="not-logged")[0] == 0


def case_decision_ids_follow_the_grammar(tmp):
    _init(tmp, [_q("1/1")])
    before = _get(tmp)
    for bad in ("VD#1", "[VD#0]", "[VD#01]", "[XD#1]", "key-1-01/[VD#1]", "KEY-1-01/VD#1", "KEY/[VD#1]", " [VD#1]", ""):
        code, out, err = _event(tmp, qid="1/1", event="answered", decision=bad)
        _unchanged(tmp, before, code)
    code, out, err = _event(tmp, qid="1/1", event="applied", decision="[VD#2]", applied_from="nope")
    _unchanged(tmp, before, code)
    assert _event(tmp, qid="1/1", event="answered", decision="KEY-12-03/[VD#10]")[0] == 0


def case_carried_refuses_all_but_proposed(tmp):
    _init(tmp, [_q("1/1", carried=True)])
    before = _get(tmp)
    events = ({"event": "answered", "decision": "[VD#1]"},
              {"event": "applied", "decision": "[VD#2]", "applied_from": "[VD#1]"},
              {"event": "table", "decision": "[VD#1]"}, {"event": "deferred", "decision": "[VD#1]"},
              {"event": "auto", "decision": "confirmed"}, {"event": "narrowed", "text": "Narrower?"},
              {"event": "retagged", "tag": "C", "reason": "x"})
    for ev in events:
        code, out, err = _event(tmp, qid="1/1", **ev)
        _unchanged(tmp, before, code)
    code, out, err = _event(tmp, qid="1/1", event="proposed")
    _unchanged(tmp, before, code)
    code, out, err = _event(tmp, qid="1/1", event="proposed", answer="Probably yes")
    assert code == 0, (code, err)
    q = _state(tmp)["1/1"]
    assert q["state"] == "open" and q["proposed"] == "Probably yes", q
    code, out, err = _run(tmp, "reopen", ["--qid", "1/1"])
    assert code == 3, "reopened a carried question"


def case_events_on_a_closed_or_unknown_question_refused(tmp):
    _init(tmp, [_q("1/1")])
    assert _event(tmp, qid="1/1", event="answered", decision="[VD#1]")[0] == 0
    before = _get(tmp)
    for ev in ({"qid": "1/1", "event": "answered", "decision": "[VD#2]"},
               {"qid": "1/1", "event": "deferred"}, {"qid": "1/1", "event": "proposed", "answer": "x"},
               {"qid": "9/9", "event": "deferred"}, {"qid": "1/1", "event": "settled"},
               {"qid": "1/1", "event": "deferred", "colour": "red"}):
        code, out, err = _event(tmp, **ev)
        _unchanged(tmp, before, code)
    for sitting in ("0", "-1", "x", "1.5"):
        code, out, err = _run(tmp, "record", ["--sitting", sitting], stdin={"qid": "1/1", "event": "deferred"})
        _unchanged(tmp, before, code)
    code, out, err = _run(tmp, "record", ["--sitting", "1"], stdin="{")
    _unchanged(tmp, before, code)


def case_narrowed_sets_text_and_stays_open(tmp):
    _init(tmp, [_q("1/1")])
    before = _get(tmp)
    code, out, err = _event(tmp, qid="1/1", event="narrowed")
    _unchanged(tmp, before, code)
    assert _event(tmp, qid="1/1", event="narrowed", text="Which invoices?")[0] == 0
    q = _state(tmp)["1/1"]
    assert q["text"] == "Which invoices?" and q["state"] == "open", q
    assert _event(tmp, qid="1/1", event="deferred")[0] == 0


def case_reopen_cascades_transitively(tmp):
    _init(tmp, [_q("1/1"), _q("1/2"), _q("1/3"), _q("1/4")])
    assert _event(tmp, qid="1/1", event="answered", decision="[VD#1]", answer="A")[0] == 0
    assert _event(tmp, qid="1/2", event="applied", applied_from="[VD#1]", decision="[VD#2]", answer="B", reason="r")[0] == 0
    assert _event(tmp, qid="1/3", event="applied", applied_from="[VD#2]", decision="[VD#3]", answer="C")[0] == 0
    assert _event(tmp, qid="1/4", event="applied", applied_from="[VD#9]", decision="[VD#4]")[0] == 0
    code, out, err = _run(tmp, "reopen", ["--follows", "[VD#1]"])
    assert code == 0 and out.split() == ["1/2", "1/3"], (code, out, err)
    st = _state(tmp)
    assert st["1/1"]["state"] == "answered" and st["1/4"]["state"] == "applied", st
    for qid in ("1/2", "1/3"):
        q = st[qid]
        assert q["state"] == "open", q
        assert (q["decision"], q["applied_from"], q["answer"], q["reason"], q["sitting"]) == (None, None, None, None, 0), q
    code, acct, err = _account(tmp)
    assert code == 0 and acct["V"]["open"] == 2 and acct["V"]["answered"] == 1 and acct["V"]["applied"] == 1, acct
    code, out, err = _run(tmp, "reopen", ["--follows", "[VD#1]"])
    assert code == 0 and out == "", (code, out, err)
    code, out, err = _run(tmp, "reopen", ["--follows", "not-an-id"])
    assert code == 3


def case_reopen_cascades_cross_brd(tmp):
    _init(tmp, [_q("1/1"), _q("1/2"), _q("1/3")])
    foreign = "PRD-7-02/[VD#4]"
    assert _event(tmp, qid="1/1", event="applied", applied_from=foreign, decision="[VD#5]")[0] == 0
    assert _event(tmp, qid="1/2", event="applied", applied_from="[VD#4]", decision="[VD#6]")[0] == 0
    assert _event(tmp, qid="1/3", event="applied", applied_from="[VD#5]", decision="[VD#7]")[0] == 0
    code, out, err = _run(tmp, "reopen", ["--follows", foreign])
    assert code == 0 and out.split() == ["1/1", "1/3"], (code, out, err)
    assert _state(tmp)["1/2"]["state"] == "applied", "a bare [VD#4] is not the same decision as PRD-7-02/[VD#4]"


def case_reopen_one_question(tmp):
    _init(tmp, [_q("1/1"), _q("1/2"), _q("1/3", carried=True)])
    assert _event(tmp, qid="1/1", event="answered", decision="[VD#1]", answer="A")[0] == 0
    assert _event(tmp, qid="1/2", event="applied", applied_from="[VD#1]", decision="[VD#2]")[0] == 0
    before = _get(tmp)
    for qid in ("1/3", "9/9"):
        code, out, err = _run(tmp, "reopen", ["--qid", qid])
        _unchanged(tmp, before, code)
    code, out, err = _run(tmp, "reopen", ["--qid", "1/1"])
    assert code == 0 and out.split() == ["1/1"], (code, out, err)
    st = _state(tmp)
    assert st["1/1"]["state"] == "open" and st["1/1"]["decision"] is None and st["1/2"]["state"] == "applied", st
    before = _get(tmp)
    code, out, err = _run(tmp, "reopen", ["--qid", "1/1"])
    _unchanged(tmp, before, code)


def case_reopen_needs_exactly_one_selector(tmp):
    _init(tmp, [_q("1/1")])
    code, out, err = _run(tmp, "reopen")
    assert code != 0 and code != 4, code
    code, out, err = _run(tmp, "reopen", ["--qid", "1/1", "--follows", "[VD#1]"])
    assert code != 0 and code != 4, code


def case_retag_moves_counts(tmp):
    _init(tmp, [_q("1/1", tag="C"), _q("1/2", tag="C"), _q("1/3")])
    before = _get(tmp)
    for ev in ({"event": "retagged"}, {"event": "retagged", "tag": "V"}, {"event": "retagged", "reason": "x"},
               {"event": "retagged", "tag": "C", "reason": "x"}, {"event": "retagged", "tag": "G", "reason": "x"}):
        code, out, err = _event(tmp, qid="1/1", **ev)
        _unchanged(tmp, before, code)
    assert _event(tmp, qid="1/1", event="retagged", tag="V", reason="the operator can answer it")[0] == 0
    q = _state(tmp)["1/1"]
    assert (q["tag"], q["original_tag"], q["state"]) == ("V", "C", "open"), q
    code, acct, err = _account(tmp)
    assert code == 0 and acct["closes"] is True, acct
    assert acct["C"]["retagged_out"] == 1 and acct["C"]["generated"] == 2 and acct["C"]["open"] == 1, acct
    assert acct["V"]["retagged_in"] == 1 and acct["V"]["generated"] == 1 and acct["V"]["open"] == 2, acct
    assert _event(tmp, qid="1/1", event="answered", decision="[VD#1]")[0] == 0
    code, acct, err = _account(tmp)
    assert code == 0 and acct["V"]["answered"] == 1 and acct["V"]["open"] == 1 and acct["closes"], acct


def case_next_orders_and_skips(tmp):
    qs = [_q("2/1", rank=3), _q("1/2", rank=1), _q("1/1", rank=1), _q("cand/2", rank=9, strategic=True),
          _q("cand/1", rank=9, strategic=True), _q("3/1", rank=0, carried=True), _q("4/1", rank=0),
          _q("5/1", rank=2), _q("6/1", rank=5, strategic=True)]
    _init(tmp, qs, budget=6)
    assert _event(tmp, qid="4/1", event="deferred")[0] == 0
    code, out, err = _run(tmp, "next")
    assert code == 0 and out.split() == ["6/1", "cand/1", "cand/2", "1/1", "1/2", "5/1"], (code, out)
    code, out, err = _run(tmp, "next", ["--limit", "2"])
    assert out.split() == ["6/1", "cand/1"], out
    code, out, err = _run(tmp, "next", ["--limit", "50"])
    assert out.split() == ["6/1", "cand/1", "cand/2", "1/1", "1/2", "5/1", "2/1"], out
    for bad in ("0", "-1", "x"):
        code, out, err = _run(tmp, "next", ["--limit", bad])
        assert code == 3, (bad, code)


def case_sitting_list_groups_by_source(tmp):
    _init(tmp, [_q("1/1"), _q("1/2"), _q("1/3"), _q("1/4"), _q("1/5"), _q("1/6"), _q("1/7"), _q("1/8")])
    assert _event(tmp, qid="1/1", event="applied", applied_from="[VD#1]", decision="[VD#2]", answer="Yes", reason="same as before")[0] == 0
    assert _event(tmp, qid="1/2", event="applied", applied_from="[VD#1]", decision="[VD#3]", answer="Weekly")[0] == 0
    assert _event(tmp, qid="1/3", event="applied", applied_from="PRD-7-02/[VD#4]", decision="[VD#5]", answer="No")[0] == 0
    assert _event(tmp, qid="1/4", event="table", decision="[VD#6]", answer="Confirmed")[0] == 0
    assert _event(tmp, qid="1/5", event="applied", applied_from="[VD#1]", decision="[VD#7]", answer="Later")[0] == 0
    assert _event(tmp, sitting=2, qid="1/8", event="applied", applied_from="[VD#1]", decision="[VD#8]", answer="x")[0] == 0
    assert _run(tmp, "merge", ["--into", "1/6", "--from", "1/7", "--reason", "duplicate", "--sitting", "1"])[0] == 0
    assert _run(tmp, "drop", ["--qid", "1/6", "--reason", "not needed", "--sitting", "1"])[0] == 0
    # 1/5 belongs to sitting 1 too; move it to sitting 2 by reopening and recording again.
    assert _run(tmp, "reopen", ["--qid", "1/5"])[0] == 0
    assert _event(tmp, sitting=2, qid="1/5", event="applied", applied_from="[VD#1]", decision="[VD#7]", answer="Later")[0] == 0
    code, out, err = _run(tmp, "sitting-list", ["--sitting", "1"])
    assert code == 0, (code, err)
    assert out.count("### Applied from [VD#1]") == 1 and out.count("### Applied from PRD-7-02/[VD#4]") == 1, out
    lines = out.split("\n")
    first = lines.index("### Applied from [VD#1]")
    block = lines[first + 1:first + 3]
    assert block[0].startswith("- 1/1") and "Yes" in block[0] and "same as before" in block[0], block
    assert block[1].startswith("- 1/2") and "Weekly" in block[1], block
    heads = [ln for ln in lines if ln.startswith("### ")]
    assert heads == ["### Applied from [VD#1]", "### Applied from PRD-7-02/[VD#4]", "### Merged", "### Dropped",
                     "### Confirmed in a table"], heads
    merged = out.split("### Merged")[1].split("###")[0]
    dropped = out.split("### Dropped")[1].split("###")[0]
    table = out.split("### Confirmed in a table")[1]
    assert "1/7" in merged and "1/6" in merged and "duplicate" in merged, merged
    assert "1/6" in dropped and "not needed" in dropped, dropped
    assert "1/4" in table, table
    assert "1/5" not in out.split("### Merged")[0] and "1/8" not in out, out
    code, out2, err = _run(tmp, "sitting-list", ["--sitting", "2"])
    assert code == 0 and "1/5" in out2 and "1/8" in out2 and "1/4" not in out2, out2
    code, out3, err = _run(tmp, "sitting-list", ["--sitting", "9"])
    assert code == 0 and out3.strip() == "", out3
    code, out3, err = _run(tmp, "sitting-list", ["--sitting", "0"])
    assert code == 3


def case_account_detects_gap(tmp):
    _init(tmp, [_q("1/1"), _q("1/2"), _q("1/3", tag="C")])
    good = json.loads(_get(tmp))
    # A state value no account column holds: the registry cannot be read.
    bad = json.loads(json.dumps(good))
    bad["questions"]["1/2"]["state"] = "settled"
    with open(_reg(tmp), "w", encoding="utf-8") as fh:
        json.dump(bad, fh)
    code, out, err = _run(tmp, "account")
    assert code == 2 and err.startswith("question-registry: ") and out == "", (code, out, err)
    # A question removed from the file: generated still counts it, no state column does.
    gap = json.loads(json.dumps(good))
    del gap["questions"]["1/2"]
    with open(_reg(tmp), "w", encoding="utf-8") as fh:
        json.dump(gap, fh)
    code, acct, err = _account(tmp)
    assert code == 4 and acct["closes"] is False and acct["V"]["generated"] == 2 and acct["V"]["open"] == 1, (code, acct)
    assert acct["C"]["generated"] == 1 and "V" in err, err
    # A state field removed, a tag outside the three, a file that is not JSON, and an absent file.
    for mutate in (lambda d: d["questions"]["1/1"].pop("state"), lambda d: d["questions"]["1/1"].update(tag="G"),
                   lambda d: d["questions"]["1/1"].update(qid="9/9"), lambda d: d.update(version=2),
                   lambda d: d["generated"].pop("C")):
        broken = json.loads(json.dumps(good))
        mutate(broken)
        with open(_reg(tmp), "w", encoding="utf-8") as fh:
            json.dump(broken, fh)
        assert _run(tmp, "account")[0] == 2
    with open(_reg(tmp), "w", encoding="utf-8") as fh:
        fh.write("{")
    assert _run(tmp, "account")[0] == 2
    os.remove(_reg(tmp))
    code, out, err = _run(tmp, "account")
    assert code == 2 and "cannot read" in err, (code, err)


def case_init_from_existing_states(tmp):
    _init(tmp, [
        _q("1/1", state="answered", decision="[VD#1]", answer="Yes", sitting=1),
        _q("1/2", state="applied", decision="[VD#2]", applied_from="[VD#1]", answer="Yes", sitting=1),
        _q("1/3", state="merged", into="1/4", reason="same", sitting=1),
        _q("1/4"),
        _q("1/5", tag="DEF", state="auto", decision="confirmed", sitting=1),
        _q("1/6", tag="C", state="deferred", decision="[CD#1]"),
        _q("1/7", state="dropped", reason="out", sitting=1),
        _q("1/8", state="table", decision="[VD#3]", sitting=1),
    ])
    code, acct, err = _account(tmp)
    assert code == 0 and acct["closes"] is True, acct
    v = acct["V"]
    assert (v["generated"], v["answered"], v["applied"], v["merged"], v["open"], v["dropped"], v["table"]) == \
        (6, 1, 1, 1, 1, 1, 1), v
    assert acct["DEF"]["auto"] == 1 and acct["C"]["deferred"] == 1, acct
    before = _get(tmp)
    for qid, ev in (("1/1", {"event": "deferred"}), ("1/3", {"event": "answered", "decision": "[VD#9]"}),
                    ("1/5", {"event": "proposed", "answer": "x"}), ("1/7", {"event": "narrowed", "text": "x"})):
        code, out, err = _event(tmp, qid=qid, **ev)
        _unchanged(tmp, before, code)
    code, out, err = _run(tmp, "reopen", ["--follows", "[VD#1]"])
    assert code == 0 and out.split() == ["1/2"], out


def case_atomic_write_leaves_no_temp(tmp):
    names = lambda: sorted(os.listdir(tmp))  # noqa: E731
    code, out, err = _run(tmp, "init", stdin={"budget": 5, "questions": [_q("a b")]})
    assert code == 3 and names() == [], names()
    _init(tmp, [_q("1/1"), _q("1/2")])
    assert names() == ["registry.json"], names()
    os.chmod(_reg(tmp), 0o640)
    before = _get(tmp)
    code, out, err = _event(tmp, qid="9/9", event="deferred")
    _unchanged(tmp, before, code)
    assert names() == ["registry.json"], names()
    assert _event(tmp, qid="1/1", event="deferred")[0] == 0
    assert names() == ["registry.json"], names()
    assert os.stat(_reg(tmp)).st_mode & 0o777 == 0o640, oct(os.stat(_reg(tmp)).st_mode)
    before = _get(tmp)

    def fails_midway(fh, text):
        fh.write(text[: len(text) // 2])
        raise OSError(28, "No space left on device")

    def fails_on_replace(src, dst):
        raise OSError(5, "Input/output error")

    for name, broken in (("_write_body", fails_midway), ("_replace", fails_on_replace)):
        real = globals()[name]
        globals()[name] = broken
        try:
            code, out, err = _event(tmp, qid="1/2", event="deferred")
        finally:
            globals()[name] = real
        assert code == 2 and "cannot write the registry" in err and tmp not in err, (name, code, err)
        assert _get(tmp) == before and names() == ["registry.json"], (name, names())


def selftest():
    cases = sorted((name, fn) for name, fn in globals().items() if name.startswith("case_"))
    failed = 0
    for name, fn in cases:
        with tempfile.TemporaryDirectory() as tmp:
            try:
                fn(os.path.realpath(tmp))
                print("ok   " + name)
            except Exception as e:  # any exception is that case failing, and it is named
                failed += 1
                print("FAIL %s: %s: %s" % (name, type(e).__name__, e))
    print("selftest: %d/%d passed" % (len(cases) - failed, len(cases)))
    return 1 if failed else 0



if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
