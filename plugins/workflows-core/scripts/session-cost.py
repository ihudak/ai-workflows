#!/usr/bin/env python3
"""session-cost.py — compute the token-cost delta for one command of this family.

Pure computation, Python standard library only (json, argparse, glob, os,
datetime). Given a chained checkpoint (or none) it reads the current session's
main transcript from a line offset forward plus the session's subagent
transcripts within a timestamp window, accumulates token usage per model
(each API message id once -- see keep_once),
applies a price table (USD per MILLION tokens), and prints a structured JSON
result to stdout. It NEVER writes the specs repo and NEVER writes the checkpoint
back — the caller (references/cost-emission.md) persists ``new_checkpoint``,
except under ``--advance-only``, which writes it itself (run-flags.md ``skip-cost``).

Claude Code stores no dollar figure in the transcript; every assistant message
carries ``.message.usage`` + ``.message.model``, so cost is computed, not read.
"""

import argparse
import datetime
import glob
import json
import os
import sys

TOKEN_KEYS = ("input", "output", "cache_read", "cache_write_5m", "cache_write_1h")


def _num(v):
    """Coerce a token count to a number; None/absent/non-numeric -> 0."""
    return v if isinstance(v, (int, float)) else 0


def _blank():
    return {k: 0 for k in TOKEN_KEYS}


def parse_ts(s):
    """Parse an ISO8601 timestamp to a UTC-aware datetime, or None on failure.

    Handles a trailing 'Z' and over-long fractional seconds without ``re``
    (fromisoformat before 3.11 rejects >6 fractional digits and a 'Z')."""
    if not s or not isinstance(s, str):
        return None
    t = s.strip().replace("Z", "+00:00")
    if "." in t:
        head, frac = t.split(".", 1)
        tz = ""
        for sign in ("+", "-"):
            idx = frac.find(sign)
            if idx != -1:
                tz, frac = frac[idx:], frac[:idx]
                break
        t = head + "." + frac[:6] + tz
    try:
        dt = datetime.datetime.fromisoformat(t)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def iso_z(dt):
    """Format a datetime as ISO8601 UTC with a 'Z' suffix (whole seconds)."""
    return dt.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_scalar(s):
    s = s.strip()
    if s == "" or s.lower() in ("null", "~"):
        return None
    try:
        return float(s) if ("." in s or "e" in s.lower()) else int(s)
    except ValueError:
        return s.strip('"').strip("'")


def load_prices(path):
    """Minimal indentation-based YAML reader for the fixed cost-prices.yaml
    structure (nested mappings, scalar leaves, inline '#' comments). Standard
    library only -- NOT a general YAML parser, but sufficient for the shipped
    price file, so PyYAML is not a dependency."""
    root = {}
    stack = [(-1, root)]
    if not path or not os.path.isfile(path):
        return root
    try:
        fh_prices = open(path, encoding="utf-8", errors="replace")
    except OSError:
        return root
    with fh_prices as fh:
        for raw in fh:
            line = raw.split("#", 1)[0].rstrip()
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip(" "))
            key, _, val = line.strip().partition(":")
            key, val = key.strip(), val.strip()
            while stack and stack[-1][0] >= indent:
                stack.pop()
            parent = stack[-1][1]
            if val == "":
                child = {}
                parent[key] = child
                stack.append((indent, child))
            else:
                parent[key] = _parse_scalar(val)
    return root


def extract_usage(obj):
    """Return (model, usage) for an assistant message with usage, else (None, None)."""
    msg = obj.get("message") if isinstance(obj, dict) else None
    if not isinstance(msg, dict):
        return None, None
    usage = msg.get("usage")
    if not isinstance(usage, dict):
        return None, None
    model = msg.get("model")
    # Coerced to str deliberately: a transcript is not a schema we control, and a
    # non-string model (a number, a dict) used to reach sorted() and acc[] and
    # raise -- a hard failure in a script whose contract is that it never fails.
    if not isinstance(model, str):
        model = "unknown" if model is None else repr(model)
    return (model or "unknown"), usage


def _message_id(obj):
    """The API message id an assistant record belongs to, or None."""
    msg = obj.get("message") if isinstance(obj, dict) else None
    mid = msg.get("id") if isinstance(msg, dict) else None
    return mid if isinstance(mid, str) and mid else None


def keep_once(records, by_id, mid, ts, model, usage):
    """Append (ts, model, usage) unless its message id is already kept.

    One API response is written as several assistant records sharing one message id,
    each repeating the usage: a streaming partial first, the final record later.
    Summing per record counted one call's input and cache reads two to three times.
    A repeated id is folded into the record already kept -- its first timestamp, the
    usage with the most output tokens, which is the final one -- so each call counts
    once. A record with no id is kept as it is."""
    if mid is None:
        records.append((ts, model, usage))
        return
    i = by_id.get(mid)
    if i is None:
        by_id[mid] = len(records)
        records.append((ts, model, usage))
        return
    old_ts, _old_model, old_usage = records[i]
    if _num(usage.get("output_tokens")) >= _num(old_usage.get("output_tokens")):
        records[i] = (old_ts, model, usage)


STANDARD_SPEED = "standard"
GLOBAL_GEO = "global"
# `inference_geo` values that bill at the standard rate with no table lookup:
# the default routing, and the two ways a record says "no residency pinned".
_STANDARD_GEOS = (None, "", GLOBAL_GEO, "not_available")


def variant_key(usage):
    """(speed, geo) for one usage record -- the two facts a transcript records
    that change the RATE rather than the token count.

    `usage.speed` is `standard` or `fast`; `usage.inference_geo` is `global`,
    `us`, or `not_available`. Both fields are absent from older records, and an
    absent field is the standard case, not an unknown one. Any OTHER value is
    kept verbatim rather than folded into the default: a value this function
    does not recognise is one the price table must then answer for, and
    `price_model` reports it unpriced where the table cannot -- folding it to
    `standard` here would price it at a rate nobody confirmed."""
    speed = usage.get("speed")
    if not isinstance(speed, str) or speed in ("", STANDARD_SPEED):
        speed = STANDARD_SPEED
    geo = usage.get("inference_geo")
    if geo in _STANDARD_GEOS or not isinstance(geo, str):
        geo = GLOBAL_GEO
    return speed, geo


def add_usage(acc, model, usage):
    """Accumulate one assistant message's token usage into acc[model].

    Totals land in the five TOKEN_KEYS exactly as before, so every consumer of
    the row format is unaffected. The same increments ALSO land in
    acc[model]["_v"][(speed, geo)], which is what `price_model` prices from:
    fast mode and US-only inference change the rate, not the count, so a model's
    cost is the sum over its variants and cannot be recovered from the totals."""
    m = acc.setdefault(model, _blank())
    inc = _blank()
    inc["input"] = _num(usage.get("input_tokens"))
    inc["output"] = _num(usage.get("output_tokens"))
    inc["cache_read"] = _num(usage.get("cache_read_input_tokens"))
    cc = usage.get("cache_creation")
    if isinstance(cc, dict) and (
        cc.get("ephemeral_5m_input_tokens") is not None
        or cc.get("ephemeral_1h_input_tokens") is not None
    ):
        inc["cache_write_5m"] = _num(cc.get("ephemeral_5m_input_tokens"))
        inc["cache_write_1h"] = _num(cc.get("ephemeral_1h_input_tokens"))
    else:
        # No 5m/1h split available -> price all cache-creation at the 5m rate.
        inc["cache_write_5m"] = _num(usage.get("cache_creation_input_tokens"))
    v = m.setdefault("_v", {}).setdefault(variant_key(usage), _blank())
    for k in TOKEN_KEYS:
        m[k] += inc[k]
        v[k] += inc[k]


MARKER_OPEN = "<command-name>"
MARKER_CLOSE = "</command-name>"
# Claude Code writes a slash-command invocation in one of TWO envelope orders,
# and the difference is not cosmetic -- it decides whether plugin-provided
# commands are visible at all:
#   built-ins        <command-name>/compact</command-name><command-message>...
#   plugin-provided  <command-message>foo:bar</command-message><command-name>/foo:bar</command-name>...
# Verified over every transcript on the machine this was written on: 79 built-in
# invocations, all name-first; every plugin-provided invocation message-first.
# An implementation anchored on <command-name> alone therefore sees ZERO plugin
# commands and the whole feature is inert -- which is exactly how it first
# shipped here. Anchoring on EITHER opener keeps the property that matters (the
# envelope must START the message, so a marker quoted inside prose or a pasted
# file is not an invocation) while admitting both real shapes.
MARKER_MSG = "<command-message>"


# The namespace manifest ships BESIDE this script, and is read with no flag and no
# path assumption. Building the map at runtime would need every sibling plugin's
# commands/ dir, which lives at <cache>/<marketplace>/<plugin>/<version>/ -- a layout
# CLAUDE.md forbids hardcoding. Every plugin of this marketplace is authored in one
# repository, so the namespaces and their command sets are known at authoring time.
DEFAULT_NAMESPACE_MAP = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "command-namespaces.json")


def load_namespace_map(path):
    """Every plugin namespace in this marketplace, mapped to that plugin's OWN
    command names.

    Returns {namespace: frozenset(names)}, or None when nothing usable resolved --
    which disables boundary detection entirely rather than guessing.

    It is a MAP and not a list of namespaces, and that distinction is the whole
    fix. A boundary resolves BOTH halves at once, so a detector that widened the
    accepted namespaces while still holding one plugin's command names would go on
    rejecting `/dev-workflows:vuln` -- reproduced, and measured: the claim then
    swallows the sibling run's segment (9000 tokens claimed where 5000 is correct).

    It is equally NOT read off any plugin's commands/ directory. The run doing the
    reading is routinely a DIFFERENT plugin from the one that ships this script and
    the reference that invokes it, so a ${CLAUDE_PLUGIN_ROOT}/commands path resolves
    to the WRONG plugin's command set -- the reference's own six utility commands
    while the emitting run is a command of a sibling plugin. That was live, and no
    assertion could see it: the path resolved, just to the wrong files.

    The manifest is DERIVED, never hand-maintained: scripts/check-docs.sh asserts it
    equals the tree's per-plugin command inventory, in both directions."""
    if not path or not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            raw = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(raw, dict):
        return None
    # Tolerant by entry, never fatal: a malformed entry drops out and the rest of the
    # map still resolves, exactly as a malformed transcript line does not fail a run.
    ns_map = {}
    for ns, names in raw.items():
        if not isinstance(ns, str) or not ns or not isinstance(names, list):
            continue
        good = frozenset(n for n in names if isinstance(n, str) and n)
        if good:
            ns_map[ns] = good
    return ns_map or None


# `/compact` is Claude Code's own built-in context-compaction operation. It is a
# well-formed envelope by every structural test command_envelope applies below --
# and it is STILL excluded, by NAME, from cutting a window. A cost window exists
# to attribute spend to the thing that CAUSED it; /compact does not start a new
# unit of work, it is housekeeping Claude Code performs on the conversation that
# is ALREADY running, mid-task and often automatic. Cutting there would not
# attribute its own tokens to /compact -- nothing ever claims it, since it has no
# namespace and claimable_command rejects every bare name -- it would sever the
# window of whatever command WAS already open, stranding the rest of THAT
# command's own spend in the remainder instead of in its rightful claim. That is
# the very misattribution section 8.7 exists to prevent, just aimed inward at the
# window's own command instead of outward at a sibling's.
#
# This is a DECISION, not a derivation, and it does not fall out of "any
# well-formed envelope cuts" by itself -- it is the one deliberate exception,
# named here rather than inferred from shape. Bare-vs-namespaced is explicitly
# NOT the test: a bare `/upgrade` built-in DOES cut (see command_envelope), and
# for the opposite reason /compact does not -- /upgrade represents the user
# doing something genuinely separate (a subscription action), /compact does not.
# A held ONE-ELEMENT set, tested by membership, not parsed -- the same
# discipline every other name test in this file uses.
NON_CUTTING_BUILTINS = frozenset({"compact"})


def _skill_invocation(obj, ns_map):
    """The typed-form name if `obj` is an assistant record invoking a command of
    THIS marketplace through the Skill tool, else None.

    WHY THIS SHAPE EXISTS. The `<command-name>` envelope is emitted when the user
    TYPES the slash command. When the model reaches the command through the
    **Skill tool** -- on a prose request, or one command running another -- the
    invocation appears only as an assistant `tool_use` block named `Skill` whose
    `input.skill` is the command -- no user message, no envelope -- so a detector
    reading user messages alone misses the invocation entirely, and section 13.3 hands
    the preceding claim the segment running to the next boundary of any kind, i.e.
    straight through it. Measured on a real session: a typed grill command was followed
    by two prose-invoked runs, neither of which cut the window, and the grill's claim
    absorbed both. Typed-only commands (flagged `disable-model-invocation: true`) changed
    what reaches this path, not the path: a flagged command never runs through the Skill
    tool, and a call the tool refused -- its result an error -- cuts nothing (scan_main
    drops it); a command left unflagged still arrives this way, from a caller or on a
    prose request.

    WHY THIS HALF RESOLVES WHERE command_envelope DOES NOT -- a deliberate
    asymmetry, and the one thing to get right here. command_envelope cuts on ANY
    command, foreign marketplaces included, because a typed name it cannot see is
    swallowed whole into some claim's segment; a user can only type a real command,
    so permissiveness costs nothing there. A Skill call is different in kind:
    commands dispatch NON-command skills constantly -- the model-routing skill and
    the reference loader, several times a run -- and cutting on those would shatter
    one command's window into spurious segments, which is worse than the miss this
    function exists to fix. So a Skill call cuts only where `ns_map` resolves it to
    a real command of this marketplace."""
    if obj.get("type") != "assistant":
        return None
    msg = obj.get("message")
    if not isinstance(msg, dict):
        return None
    for block in (msg.get("content") or []):
        if not isinstance(block, dict) or block.get("type") != "tool_use":
            continue
        if block.get("name") != "Skill":
            continue
        inp = block.get("input")
        if not isinstance(inp, dict):
            continue
        skill = inp.get("skill")
        if claimable_command(skill, ns_map) is not None:
            return skill
    return None


def command_envelope(obj, ns_map=None):
    """The typed command text (e.g. "workflows-core:prompt-grill-me", or the
    bare built-in "upgrade") if obj is a transcript record for ANY well-formed
    slash-command invocation, else None. Decides WHERE TO CUT a window.

    Deliberately independent of any manifest -- a namespace, a bare built-in
    name, or a command from a marketplace this one has never heard of all
    qualify equally. The marketplace-split design spec's section 8.7 (git show
    62e791e8:docs/superpowers/specs/2026-09-02-marketplace-split-design.md;
    removed from the tree 2026-09-23) found
    that resolving THIS question against the manifest was itself the defect: a
    boundary this test cannot see is swallowed whole into whichever claim's
    segment it falls inside (section 13.3 gives a claim the segment up to the
    next boundary OF ANY KIND), and a foreign marketplace's command is exactly
    such an invisible boundary. The manifest still governs the SEPARATE
    question of what a claim may MATCH -- see claimable_command.

    Two disciplines survive the split intact. The marker must START the
    message content: the same `<command-name>` text appears inside quoted file
    content elsewhere in a transcript, and an unanchored search matches that
    too. And exactly one name is excluded, by deliberate decision rather than
    by parsed shape -- see NON_CUTTING_BUILTINS."""
    if not isinstance(obj, dict):
        return None
    if obj.get("type") == "assistant":
        return _skill_invocation(obj, ns_map)
    if obj.get("type") != "user":
        return None
    msg = obj.get("message")
    if not isinstance(msg, dict):
        return None
    content = msg.get("content")
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        text = "".join(
            c.get("text", "") for c in content
            if isinstance(c, dict) and c.get("type") == "text"
        )
    else:
        return None
    text = text.lstrip()
    if not (text.startswith(MARKER_OPEN) or text.startswith(MARKER_MSG)):
        return None
    at = text.find(MARKER_OPEN)
    if at < 0:
        return None
    rest = text[at + len(MARKER_OPEN):]
    end = rest.find(MARKER_CLOSE)
    if end < 0:
        return None
    raw = rest[:end].strip()
    # The leading-slash test and the [1:] that follows it are deliberately
    # coupled: the check rejects a <command-name> whose content is not a slash
    # command, and the offset assumes it passed. Removing the check alone is not
    # independently observable -- [1:] then eats the first real character and the
    # name matches nothing -- so no selftest case asserts it. Keep them together.
    if not raw.startswith("/"):
        return None
    typed = raw[1:].strip()
    if not typed or typed in NON_CUTTING_BUILTINS:
        return None
    return typed


def claimable_command(typed, ns_map):
    """The bare command name if `typed` (command_envelope's return value)
    names a command KNOWN to this marketplace's manifest, else None. Decides
    WHERE A CLAIM MAY MATCH -- unlike command_envelope, a namespace is
    REQUIRED here, and that is a deliberate asymmetry with how a user thinks
    about these commands. Two facts force it. Claude Code's own built-ins are
    always written bare, and several of them -- `/upgrade`, `/feedback`,
    `/statusline` and `/release-notes` -- collide with command names this
    marketplace also ships: accepting a bare name here would let such a
    built-in masquerade as a claimable invocation of ours
    (it still CUTS -- command_envelope does not require a namespace -- only
    claimability is refused here). And a namespace is resolved, never
    discarded: stripping it would read another marketplace's
    `/superpowers:implement` as this family's `/implement`.

    BOTH halves are resolved against a held set, never parsed: `typed` may be
    namespaced (`workflows-core:prompt-grill-me`) or bare (`upgrade`), and only
    the map can say which namespace:name pair is real. A pair outside the map
    -- a bare name, a real namespace paired with a command that plugin does
    not itself ship, or a plugin from another marketplace entirely -- returns
    None, so it never becomes claimable, even where command_envelope already
    let it cut the window."""
    if not typed or not ns_map or ":" not in typed:
        return None
    ns, rest = typed.split(":", 1)
    names = ns_map.get(ns)
    if names and rest in names:
        return rest
    return None


def scan_main(path, line_offset, ns_map, by_id=None):
    """Single pass over main-transcript lines [line_offset, EOF).

    Buffers each usage record with its timestamp instead of accumulating
    immediately, so the window can be cut into segments afterwards without
    re-reading. Returns (new_total_line_count, earliest_ts, boundaries, records)
    where records is a list of (ts, model, usage), one per API message id.
    Pass the same by_id to read_subagents, appending to a list that starts with
    these records, so an id a subagent file repeats is counted once."""
    count = line_offset
    first_ts = None
    boundaries = []
    # A Skill-tool boundary waits on its call's result: a call the tool refused ran nothing
    # (a typed-only command, flagged disable-model-invocation, is refused every time), so an
    # error result drops it. Keyed by the tool_use id the result names.
    by_call = {}
    records = []
    by_id = {} if by_id is None else by_id
    if not path or not os.path.isfile(path):
        return count, first_ts, boundaries, records
    try:
        fh_main = open(path, encoding="utf-8", errors="replace")
    except OSError:
        return count, first_ts, boundaries, records
    with fh_main as fh:
        for i, raw in enumerate(fh):
            count = i + 1
            if i < line_offset:
                continue
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except (ValueError, TypeError):
                continue
            ts = parse_ts(obj.get("timestamp") if isinstance(obj, dict) else None)
            typed = command_envelope(obj, ns_map)
            if typed is not None and ts is not None:
                # The raw stamp is kept, not iso_z's whole-second form: segment
                # edges are compared against record timestamps, and flooring the
                # edge moves up to a second of one run's records into another's.
                # A marker with no usable timestamp is not a boundary -- there is
                # nothing to cut the window at, and iso_z(None) used to raise here
                # and fail a run whose contract is that it never does.
                claim_name = claimable_command(typed, ns_map)
                # `command` is the CLAIMABLE bare name when there is one, because
                # that is exactly what a caller's `--claim` names
                # (cost-emission.md section 13.1's deferred record is always a
                # bare command). A cut that is NOT claimable reports its full
                # typed text instead -- namespaced when it had one, bare
                # otherwise -- which can never collide with a bare claimable
                # name. `claimable` is not merely informational: match_claims
                # trusts it rather than re-deriving it from `command`'s shape.
                boundaries.append(
                    {"command": ("/" + claim_name) if claim_name is not None
                                else ("/" + typed),
                     "claimable": claim_name is not None,
                     "ts": obj.get("timestamp"),
                     "line_offset": i}
                )
                if obj.get("type") == "assistant":
                    for block in (obj.get("message") or {}).get("content") or []:
                        if isinstance(block, dict) and block.get("name") == "Skill" and block.get("id"):
                            by_call[block["id"]] = boundaries[-1]
            elif by_call and isinstance(obj, dict) and obj.get("type") == "user" \
                    and isinstance(obj.get("message"), dict):
                content = obj["message"].get("content")
                for block in content if isinstance(content, list) else []:
                    if isinstance(block, dict) and block.get("type") == "tool_result" \
                            and block.get("is_error") and block.get("tool_use_id") in by_call:
                        boundaries.remove(by_call.pop(block["tool_use_id"]))
            if ts is not None and (first_ts is None or ts < first_ts):
                first_ts = ts
            model, usage = extract_usage(obj)
            if usage is not None:
                keep_once(records, by_id, _message_id(obj), ts, model, usage)
    return count, first_ts, boundaries, records


def read_subagents(subdir, last_dt, now_dt, records, by_id=None):
    """Buffer usage from subagents/agent-*.jsonl entries whose timestamp is in
    (last_dt, now_dt]  (all <= now_dt when last_dt is None), appending
    (ts, model, usage) to records so they are segmented exactly as the main
    transcript's are -- the two must agree at a boundary or a subagent's tokens
    land in both slices or neither. Each API message id counts once (keep_once).

    Returns the earliest in-window entry timestamp, or None."""
    first_ts = None
    by_id = {} if by_id is None else by_id
    if not subdir or not os.path.isdir(subdir):
        return first_ts
    for fp in sorted(glob.glob(os.path.join(subdir, "agent-*.jsonl"))):
        try:
            fh = open(fp, encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                except (ValueError, TypeError):
                    continue
                ts = parse_ts(obj.get("timestamp") if isinstance(obj, dict) else None)
                if ts is None:
                    continue
                if now_dt is not None and ts > now_dt:
                    continue
                if last_dt is not None and ts <= last_dt:
                    continue
                model, usage = extract_usage(obj)
                if usage is not None:
                    keep_once(records, by_id, _message_id(obj), ts, model, usage)
                    if first_ts is None or ts < first_ts:
                        first_ts = ts
    return first_ts


def _rate(rates, key):
    v = rates.get(key)
    return float(v) if isinstance(v, (int, float)) else 0.0


def price_model(model, tok, prices):
    """Return (cost_usd or None, note or None). Rates are USD per MILLION tokens."""
    table = prices.get("models") if isinstance(prices.get("models"), dict) else {}
    rates = table.get(model)
    if not isinstance(rates, dict):
        # Exact miss -> longest table key that is a prefix of the model id
        # (so undated key "claude-sonnet-5" prices "claude-sonnet-5-20250930").
        best = None
        for k, v in table.items():
            if isinstance(v, dict) and isinstance(model, str) and model.startswith(k):
                if best is None or len(k) > len(best):
                    best = k
        rates = table.get(best) if best is not None else None
    if not isinstance(rates, dict):
        return None, "unpriced-model"
    # A token dict built by add_usage carries its (speed, geo) variants; one
    # built by hand (the selftest's, or any caller pricing plain totals) does
    # not, and is the standard/global case by definition.
    variants = tok.get("_v") if isinstance(tok, dict) else None
    if not isinstance(variants, dict) or not variants:
        variants = {(STANDARD_SPEED, GLOBAL_GEO): tok}
    cost = 0.0
    for (speed, geo) in sorted(variants):
        vt = variants[(speed, geo)]
        vrates = rates
        if speed != STANDARD_SPEED:
            # A non-standard speed prices from that model's own sub-block
            # (`fast:`), keyed explicitly like every other rate in the table.
            # No block -> the table cannot price it. Falling back to the
            # standard rates would be a confident figure known to be low by a
            # factor of two, which is worse than a null the run reports.
            vrates = rates.get(speed)
            if not isinstance(vrates, dict):
                return None, "unpriced-speed:" + speed
        mult = 1.0
        if geo != GLOBAL_GEO:
            mult = geo_multiplier(prices, geo)
            if mult is None:
                return None, "unpriced-inference-geo:" + geo
        cost += mult * sum(vt[k] * _rate(vrates, k) for k in TOKEN_KEYS)
    return round(cost / 1_000_000.0, 4), None


def geo_multiplier(prices, geo):
    """The all-categories multiplier for a non-default `inference_geo`, from the
    table's `modifiers.inference_geo` map, or None where the table has none.

    Only reached for a value outside _STANDARD_GEOS, so a price file written
    before this map existed -- a user's $DEV_WORKFLOWS_COST_PRICES override --
    still prices every global record exactly as it did."""
    mods = prices.get("modifiers") if isinstance(prices, dict) else None
    geos = mods.get("inference_geo") if isinstance(mods, dict) else None
    v = geos.get(geo) if isinstance(geos, dict) else None
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def pricing_modifiers(tok):
    """The non-default variants that contributed tokens to this model, as the
    strings the entry's optional `modifiers:` field carries -- so a row whose
    cost per token looks high says why, instead of looking like a bad table."""
    variants = tok.get("_v") if isinstance(tok, dict) else None
    out = set()
    for (speed, geo), vt in (variants or {}).items():
        if not any(vt[k] for k in TOKEN_KEYS):
            continue
        if speed != STANDARD_SPEED:
            out.add("speed:" + speed)
        if geo != GLOBAL_GEO:
            out.add("inference-geo:" + geo)
    return sorted(out)


def read_snapshot_cost(path):
    """Return the latest cost_usd from the statusline snapshot file, or None.

    Accepts a single JSON object or JSONL (last parseable line with cost_usd)."""
    if not path or not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            data = fh.read()
    except OSError:
        return None
    try:
        obj = json.loads(data)
        if isinstance(obj, dict) and isinstance(obj.get("cost_usd"), (int, float)):
            return float(obj["cost_usd"])
    except ValueError:
        pass
    for raw in reversed(data.splitlines()):
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except ValueError:
            continue
        if isinstance(obj, dict) and isinstance(obj.get("cost_usd"), (int, float)):
            return float(obj["cost_usd"])
    return None



# --------------------------------------------------------------------------
# Selftest
#
# The window split (section 13 of cost-emission.md) is the one part of this
# script whose failure is silent: a boundary that is missed or invented still
# produces a plausible number, in the wrong bucket. So the fixture is built to
# DISCRIMINATE, and every row of it exists for a specific broken implementation
# rather than for coverage -- see _st_rows for which defect each row pins.
# Deliberately not recorded here: a count of mutations caught. That number moves
# with the fixture and with the mutation set someone chooses to try, and the last
# one written here was measured against a fixture two rewrites old. Re-derive it
# by mutating a load-bearing line and running --selftest.
# --------------------------------------------------------------------------

SELFTEST_PRICES = """models:
  claude-opus-5:
    input: 5
    output: 25
    cache_read: 0.5
    cache_write_5m: 6.25
    cache_write_1h: 10
default: null
"""


def _st_asst(ts, out):
    rec = {"type": "assistant",
           "message": {"role": "assistant", "model": "claude-opus-5",
                       "usage": {"input_tokens": 0, "output_tokens": out,
                                 "cache_read_input_tokens": 0,
                                 "cache_creation_input_tokens": 0}}}
    if ts:
        rec["timestamp"] = ts
    return rec


def _st_builtin(ts, name):          # built-ins: name-first AND bare
    return {"type": "user", "timestamp": ts,
            "message": {"role": "user", "content":
                        MARKER_OPEN + name + MARKER_CLOSE +
                        "\n  <command-message>x</command-message>"}}


def _st_plugin_cmd(ts, name, as_blocks=False):   # plugin commands: message-first
    body = (MARKER_MSG + name.lstrip("/") + "</command-message>\n"
            + MARKER_OPEN + name + MARKER_CLOSE + "\n<command-args></command-args>")
    content = ([{"type": "text", "text": body}] if as_blocks else body)
    rec = {"type": "user", "message": {"role": "user", "content": content}}
    if ts:
        rec["timestamp"] = ts
    return rec


def _st_rows():
    """A window carrying every trap this splitter has actually fallen into.

    Each row exists for a defect, not for coverage: a MESSAGE-FIRST plugin
    envelope (anchoring on <command-name> alone made the feature inert); a bare
    built-in `/upgrade`, whose name a plugin of this marketplace ships (must
    NEVER become claimable -- and, since section 8.7's split, DOES cut the
    window, proving cut and claimable are independent tests rather than one);
    a `/vuln` boundary between the ceding run and the replaying one (positional
    pairing filed its spend under a PRD phase); a FOREIGN namespace over a
    shared bare name (never claimable, but now cuts too -- the section 8.7
    defect this file exists to fix); `/compact`, the one deliberate exception
    that does NOT cut despite being just as well-formed an envelope as every
    other built-in (see NON_CUTTING_BUILTINS); the SAME command ceding twice (a
    cursor that does not advance pairs both claims to one boundary); SUB-SECOND
    boundary and record stamps (flooring the edge moves records between runs);
    records sitting exactly ON a boundary (edge inclusivity); a usage record
    with no timestamp at all; and TWO PLUGINS' namespaces in one window (a
    single-plugin detector sees only its own, and the ceding command and the
    run that replays it ship from different plugins)."""
    asst, builtin, plugin_cmd = _st_asst, _st_builtin, _st_plugin_cmd

    # The ceding command is namespaced to the plugin that actually ships it, which is
    # NOT the plugin whose command replays it at the end of this window. That is the
    # ordinary post-split shape, and it is the fixture's business to model it: both
    # namespaces must resolve, out of one manifest, for a single boundary list to come
    # back. Keep this name, the manifest built in selftest(), and the replaying
    # `/dev-workflows:implement` below consistent with each other -- a sweep that
    # rewrote this constant alone once left eight assertions failing.
    G = "/workflows-core:prompt-grill-me"
    return [
        asst("2026-09-01T10:00:00.000Z", 1000),          # prior activity
        builtin("2026-09-01T10:00:30.000Z", "/upgrade"),  # BARE, cuts, never claimable
        plugin_cmd("2026-09-01T10:01:00.000Z", "/dev-workflows:vuln"),   # emits no cost
        asst("2026-09-01T10:01:30.000Z", 4000),          # /vuln's spend
        plugin_cmd("2026-09-01T10:02:00.000Z", G),       # cede #1
        asst("2026-09-01T10:02:00.000Z", 500),           # exactly ON the boundary
        asst("2026-09-01T10:02:00.500Z", 500),           # sub-second, inside cede #1
        asst(None, 700),                                 # no timestamp -> remainder
        plugin_cmd("2026-09-01T10:02:30.000Z", "/superpowers:implement"),  # FOREIGN, cuts, never claimable
        {"type": "user", "timestamp": "2026-09-01T10:02:40.000Z",
         "message": {"role": "user", "content": "a doc quoting " + MARKER_OPEN +
                     "/dev-workflows:implement" + MARKER_CLOSE + " inline"}},
        builtin("2026-09-01T10:02:50.000Z", "/compact"),  # the ONE deliberate non-cut
        asst("2026-09-01T10:03:00.200Z", 300),           # still cede #1 (before edge)
        plugin_cmd("2026-09-01T10:03:00.500Z", G),       # cede #2 -- SAME name
        asst("2026-09-01T10:03:00.500Z", 100),           # exactly ON cede #1's END
        asst("2026-09-01T10:03:00.700Z", 800),           # cede #2
        plugin_cmd("2026-09-01T10:04:00.000Z", "/dev-workflows:implement", True),
        asst("2026-09-01T10:04:30.000Z", 3000),          # the replaying run
    ]


def _st_split_rows():
    """The defect the marketplace split introduced, reproduced as a window.

    The deferring command ships from THIS plugin; the `/vuln` that runs between the
    cede and the replay ships from a SIBLING; the replaying `/prompt` is this
    plugin's own. Section 13.3 gives a claim the segment up to the next boundary OF
    ANY KIND, so a detector that cannot see the sibling's boundary hands the claim
    the sibling's 4000 as well: 9000 claimed where 5000 is correct, 800 left in the
    remainder where 4800 is correct. Measured, both before and after.

    It carries BOTH safety rows too, because the widening is what could plausibly
    have broken them: a bare `/upgrade` (a Claude Code built-in whose name a plugin
    of this marketplace also ships) and a `/superpowers:implement` (a real namespace,
    but from another marketplace, over a bare name this one ships). Neither may EVER
    become claimable, and an implementation that widens the accepted NAMESPACES
    without widening the per-namespace NAME sets passes exactly this pair while
    failing the segment numbers above -- which is why the two travel together.
    Section 8.7 changes what these two rows ALSO prove: since neither is
    `/compact`, both are now CUT boundaries too (`command_envelope` never consults
    the manifest), so this fixture is where "cuts, but never claimable" is
    exercised for real -- right after the pair that used to be this file's whole
    answer to them.

    A THIRD degradation has its own row: a map read as one FLAT set of every
    plugin's names, so that `/workflows-core:vuln` -- a real namespace paired
    with another plugin's command -- is accepted AS CLAIMABLE. It still cuts
    the window regardless (`command_envelope` does not care whose command it
    is), so the defect this row now pins is no longer "does it appear in the
    boundary list" -- it always does -- but "is it ever marked `claimable`":
    only a flat-set implementation marks it so, and nothing else here pairs the
    two that way."""
    asst, builtin, plugin_cmd = _st_asst, _st_builtin, _st_plugin_cmd
    return [
        plugin_cmd("2026-09-01T10:00:00.000Z", "/workflows-core:prompt-grill-me"),
        asst("2026-09-01T10:00:30.000Z", 5000),          # the ceded run's own spend
        plugin_cmd("2026-09-01T10:01:00.000Z", "/dev-workflows:vuln"),  # SIBLING
        asst("2026-09-01T10:01:30.000Z", 4000),          # /vuln's spend -- remainder
        builtin("2026-09-01T10:02:00.000Z", "/upgrade"),                # safety; cuts, never claimable
        plugin_cmd("2026-09-01T10:02:10.000Z", "/superpowers:implement"),  # safety; cuts, never claimable
        plugin_cmd("2026-09-01T10:02:30.000Z", "/workflows-core:prompt"),  # replays
        asst("2026-09-01T10:03:00.000Z", 800),           # the replaying run's spend
        # A KNOWN namespace paired with a command belonging to a DIFFERENT plugin. This
        # row pins the `<that plugin's OWN command>` half of the claimability rule:
        # without it, a map read as one FLAT set of every plugin's names -- namespace
        # checked, name checked against the union -- marks it claimable, which nothing
        # else here does. It cuts the window either way (command_envelope does not
        # consult the manifest), so it moves no figure above and is told apart only by
        # its `claimable` flag, never by whether it appears in the boundary list.
        plugin_cmd("2026-09-01T10:03:30.000Z", "/workflows-core:vuln"),
    ]


def _st_crossplugin_rows():
    """A cede replayed by a command from ANOTHER plugin -- the commoner half.

    Before the widening this claim did not resolve at all: the replaying run held
    only its own plugin's set, so the ceding invocation was invisible, the claim came
    back unmatched, and the spend stayed with the replaying run (section 13.4 -- it
    errs safe, but the attribution was lost every time)."""
    asst, plugin_cmd = _st_asst, _st_plugin_cmd
    return [
        plugin_cmd("2026-09-01T10:00:00.000Z", "/workflows-core:prompt-brainstorm"),
        asst("2026-09-01T10:00:30.000Z", 2000),          # the ceded run's own spend
        plugin_cmd("2026-09-01T10:01:00.000Z", "/dev-workflows:implement"),
        asst("2026-09-01T10:01:30.000Z", 1000),          # the replaying run's spend
    ]


def _selftest_body(tmp):
    import subprocess
    import tempfile

    failures = []

    def bad(msg):
        failures.append(msg)
        print("FAIL  " + msg)

    def check(cond, msg):
        print("ok    " + msg) if cond else bad(msg)

    # Prefix shadowing: `claude-opus-5` is a prefix of `claude-opus-5-5`. With both keyed,
    # each id must price at its OWN key (exact match first), and a dated Opus 5.5 id at
    # the longest matching key -- never at Opus 5's rates.
    _pt = {"models": {
        "claude-opus-5": {"input": 5, "output": 25, "cache_read": 0.5,
                          "cache_write_5m": 6.25, "cache_write_1h": 10},
        "claude-opus-5-5": {"input": 4, "output": 20, "cache_read": 0.2,
                            "cache_write_5m": 5, "cache_write_1h": 8}}}
    _tk = {"input": 1_000_000, "output": 0, "cache_read": 1_000_000,
           "cache_write_5m": 0, "cache_write_1h": 0}
    check(price_model("claude-opus-5-5", _tk, _pt) == (4.2, None),
          "claude-opus-5-5 prices at its own key, not the claude-opus-5 prefix")
    check(price_model("claude-opus-5-5-20260901", _tk, _pt) == (4.2, None),
          "a dated Opus 5.5 id prices at the longest matching key")
    check(price_model("claude-opus-5", _tk, _pt) == (5.5, None),
          "claude-opus-5 still prices at its own key")
    # The synthetic table above proves the ENGINE. Nothing proved the SHIPPED table still
    # carries the keys the engine needs -- which is how claude-fable-5-1 went missing while
    # `claude-fable-5` shadowed it and priced 5.1's cache reads 4x high, silently, with no
    # `unpriced-model` note. These pin the shipped file.
    _shipped = load_prices(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "..", "references", "cost-prices.yaml"))
    for _mid, _want in (("claude-opus-5-5", 4.2), ("claude-opus-5", 5.5),
                        ("claude-fable-5-1", 10.25), ("claude-fable-5", 11.0),
                        ("claude-sonnet-5-5", 2.2), ("claude-sonnet-5", 2.2)):
        _got = price_model(_mid, _tk, _shipped)
        check(_got[1] is None and _got[0] is not None and abs(_got[0] - _want) < 1e-9,
              "shipped cost-prices.yaml keys %s at its own rates (1M in + 1M cache read = $%s)"
              % (_mid, _want))
    # The Sonnet pair is the one case a price assertion CANNOT police: 5.5 and 5 bill
    # identically today, so dropping the `claude-sonnet-5-5` key leaves the figure unchanged
    # (longest-prefix falls through) and both checks above still pass. The key exists to
    # survive a future divergence, so it is asserted present by name.
    check("claude-sonnet-5-5" in _shipped.get("models", {}),
          "shipped cost-prices.yaml keys claude-sonnet-5-5 explicitly, not by prefix")

    # Fast mode and data residency change the RATE, not the token count, so they
    # are priced per (speed, geo) variant. The transcript records both on every
    # assistant message; until this existed the engine read neither and a /fast
    # session priced 50% low. Built through add_usage, not by hand, so the path
    # from a usage record to a variant bucket is what is under test.
    def _use(speed=None, geo=None, inp=1_000_000, cr=1_000_000):
        u = {"input_tokens": inp, "output_tokens": 0, "cache_read_input_tokens": cr}
        if speed is not None:
            u["speed"] = speed
        if geo is not None:
            u["inference_geo"] = geo
        return u
    def _cost(model, table, *uses):
        acc = {}
        for u in uses:
            add_usage(acc, model, u)
        return price_model(model, acc[model], table), acc[model]
    _ft = {"models": {"claude-opus-5-5": {
               "input": 4, "output": 20, "cache_read": 0.2,
               "cache_write_5m": 5, "cache_write_1h": 8,
               "fast": {"input": 8, "output": 40, "cache_read": 0.4,
                        "cache_write_5m": 10, "cache_write_1h": 16}},
           "claude-opus-4-7": {"input": 5, "output": 25, "cache_read": 0.5,
                               "cache_write_5m": 6.25, "cache_write_1h": 10}},
           "modifiers": {"inference_geo": {"us": 1.1}}}
    check(_cost("claude-opus-5-5", _ft, _use())[0] == (4.2, None),
          "a record with no speed / geo field prices at the standard rate")
    check(_cost("claude-opus-5-5", _ft, _use("standard", "global"))[0] == (4.2, None),
          "speed=standard + geo=global prices at the standard rate")
    check(_cost("claude-opus-5-5", _ft, _use("standard", "not_available"))[0] == (4.2, None),
          "geo=not_available is the standard case, not an unknown one")
    check(_cost("claude-opus-5-5", _ft, _use("fast"))[0] == (8.4, None),
          "speed=fast prices from the model's fast block ($8 in + $0.40 cache read)")
    check(_cost("claude-opus-5-5", _ft, _use("standard", "us"))[0] == (4.62, None),
          "geo=us applies the 1.1x multiplier to every category")
    check(_cost("claude-opus-5-5", _ft, _use("fast", "us"))[0] == (9.24, None),
          "fast and geo=us stack (1.1 x the fast rates)")
    _mixed, _mtok = _cost("claude-opus-5-5", _ft, _use(), _use("fast"))
    check(_mixed == (12.6, None),
          "one model's standard and fast records are priced separately and summed")
    check(_mtok["input"] == 2_000_000 and _mtok["cache_read"] == 2_000_000,
          "...while the row's token totals stay the plain sum across variants")
    check(_cost("claude-opus-4-7", _ft, _use("fast"))[0] == (None, "unpriced-speed:fast"),
          "fast on a model with no fast block is unpriced, never priced at standard")
    check(_cost("claude-opus-5-5", _ft, _use("standard", "eu"))[0]
          == (None, "unpriced-inference-geo:eu"),
          "a geo the table has no multiplier for is unpriced, never priced at 1.0")
    _legacy = {"models": {"claude-opus-5-5": _ft["models"]["claude-opus-5-5"]}}
    check(_cost("claude-opus-5-5", _legacy, _use("standard", "global"))[0] == (4.2, None),
          "a price file with no modifiers block still prices global records")
    check(_cost("claude-opus-5-5-20260901", _ft, _use("fast"))[0] == (8.4, None),
          "a dated id reaches its prefix key's fast block")
    _pb, _ = price_block({"claude-opus-5-5": _cost("claude-opus-5-5", _ft, _use("fast", "us"))[1]}, _ft)
    check(_pb[0].get("modifiers") == ["inference-geo:us", "speed:fast"],
          "a row priced with modifiers names them")
    _pb2, _ = price_block({"claude-opus-5-5": _cost("claude-opus-5-5", _ft, _use())[1]}, _ft)
    check("modifiers" not in _pb2[0],
          "a standard row carries no modifiers field")
    # ...and the SHIPPED table carries the blocks the engine needs.
    for _mid, _want in (("claude-opus-5-5", 8.4), ("claude-opus-5", 11.0),
                        ("claude-opus-4-8", 11.0)):
        check(_cost(_mid, _shipped, _use("fast"))[0] == (_want, None),
              "shipped cost-prices.yaml prices %s in fast mode (1M in + 1M cache read = $%s)"
              % (_mid, _want))
    # Opus 4.6 accepts speed=fast and bills it at its STANDARD rate (pricing page); a null
    # here would price a real run at $0 and call it unknown.
    check(_cost("claude-opus-4-6", _shipped, _use("fast"))[0] == (5.5, None),
          "shipped cost-prices.yaml prices claude-opus-4-6 fast mode at its standard rate")
    check(price_model("claude-opus-4-5", _tk, _shipped) == (5.5, None),
          "shipped cost-prices.yaml keys claude-opus-4-5 (1M in + 1M cache read = $5.5)")
    check(_cost("claude-opus-5-5", _shipped, _use("standard", "us"))[0] == (4.62, None),
          "shipped cost-prices.yaml carries the 1.1x US-inference multiplier")
    for _mid in ("claude-opus-4-7", "claude-sonnet-5-5"):
        check(_cost(_mid, _shipped, _use("fast"))[0] == (None, "unpriced-speed:fast"),
              "shipped cost-prices.yaml gives %s no fast block (fast mode does not exist there)"
              % _mid)
    for _mid, _want in (("claude-mythos-5-1", 10.25), ("claude-mythos-5", 11.0)):
        _got = price_model(_mid, _tk, _shipped)
        check(_got[1] is None and _got[0] is not None and abs(_got[0] - _want) < 1e-9,
              "shipped cost-prices.yaml keys %s at its own rates (1M in + 1M cache read = $%s)"
              % (_mid, _want))


    # One API response is written as SEVERAL assistant records sharing one message id,
    # each repeating the usage -- a streaming partial first (output_tokens a few, no
    # speed) and the final record later. Summing per record counted one call's input and
    # cache reads two to three times over. Each message id counts once, at its final usage.
    def _rec(mid, ts, out, extra=None):
        u = {"input_tokens": 3, "output_tokens": out, "cache_read_input_tokens": 1000,
             "cache_creation_input_tokens": 500}
        u.update(extra or {})
        return {"type": "assistant", "timestamp": ts,
                "message": {"id": mid, "role": "assistant", "model": "claude-opus-5-5",
                            "usage": u}}
    _dd = os.path.join(tmp, "dedup.jsonl")
    with open(_dd, "w", encoding="utf-8") as fh:
        for r in (_rec("msg_A", "2026-09-01T10:00:01.000Z", 8),
                  _rec("msg_A", "2026-09-01T10:00:02.000Z", 251, {"speed": "standard"}),
                  _rec("msg_A", "2026-09-01T10:00:02.500Z", 251, {"speed": "standard"}),
                  _rec("msg_B", "2026-09-01T10:00:03.000Z", 40),
                  {"type": "assistant", "timestamp": "2026-09-01T10:00:04.000Z",
                   "message": {"role": "assistant", "model": "claude-opus-5-5",
                               "usage": {"input_tokens": 1, "output_tokens": 1}}}):
            fh.write(json.dumps(r) + "\n")
    _, _, _, _drecs = scan_main(_dd, 0, {})
    check(len(_drecs) == 3,
          "scan_main counts each message id once (3 calls, 5 records) -- got %d" % len(_drecs))
    check(sorted(r[2].get("output_tokens") for r in _drecs) == [1, 40, 251],
          "a repeated message id keeps its final usage (251 output tokens, not the partial 8)")
    _ddir = os.path.join(tmp, "dedup-subagents")
    os.makedirs(_ddir)
    with open(os.path.join(_ddir, "agent-x.jsonl"), "w", encoding="utf-8") as fh:
        for r in (_rec("msg_C", "2026-09-01T10:00:05.000Z", 8),
                  _rec("msg_C", "2026-09-01T10:00:06.000Z", 275, {"speed": "standard"})):
            fh.write(json.dumps(r) + "\n")
    _srecs = []
    read_subagents(_ddir, None, None, _srecs)
    check(len(_srecs) == 1 and _srecs[0][2].get("output_tokens") == 275,
          "read_subagents counts a subagent's repeated message id once, at its final usage")
    _msg_a = [r for r in _drecs if r[2].get("output_tokens") == 251]
    check(len(_msg_a) == 1 and _msg_a[0][0] == parse_ts("2026-09-01T10:00:01.000Z"),
          "a repeated message id is placed at its FIRST record's timestamp, where the call began")
    with open(os.path.join(_ddir, "agent-y.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(_rec("msg_D", "2026-09-01T10:00:07.000Z", 90)) + "\n")
    with open(os.path.join(_ddir, "agent-z.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(_rec("msg_D", "2026-09-01T10:00:07.000Z", 90)) + "\n")
    _srecs2 = []
    read_subagents(_ddir, None, None, _srecs2)
    check(len(_srecs2) == 2,
          "a message id two subagent files share (a fork copies its parent's records) counts once")
    # A fork of the MAIN session copies the main transcript's spawning record into its own
    # file, under the same id: one map across both sources counts it once.
    _shared = {}
    _, _, _, _mrecs = scan_main(_dd, 0, {}, by_id=_shared)
    with open(os.path.join(_ddir, "agent-fork.jsonl"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(_rec("msg_B", "2026-09-01T10:00:03.000Z", 40)) + "\n")
    _all = list(_mrecs)
    read_subagents(_ddir, None, None, _all, by_id=_shared)
    check(len(_all) == len(_mrecs) + 2,
          "a main-transcript id a subagent file repeats counts once when the two share one map")

    tpath = os.path.join(tmp, "t.jsonl")
    with open(tpath, "w", encoding="utf-8") as fh:
        for r in _st_rows():
            fh.write(json.dumps(r) + "\n")
    t2path = os.path.join(tmp, "t-split.jsonl")
    with open(t2path, "w", encoding="utf-8") as fh:
        for r in _st_split_rows():
            fh.write(json.dumps(r) + "\n")
    t3path = os.path.join(tmp, "t-crossplugin.jsonl")
    with open(t3path, "w", encoding="utf-8") as fh:
        for r in _st_crossplugin_rows():
            fh.write(json.dumps(r) + "\n")
    ppath = os.path.join(tmp, "prices.yaml")
    with open(ppath, "w", encoding="utf-8") as fh:
        fh.write(SELFTEST_PRICES)
    # The fixture's OWN manifest, never the shipped one: a fixture that read the real
    # map would assert nothing about the map it was written against, and would go red
    # the day a command is renamed. Two namespaces, DISJOINT, allocated exactly as the
    # marketplace allocates them -- the deferring commands ship from the plugin that
    # holds this script, the work commands from a sibling. `prompt` is shipped and is a
    # strict PREFIX of the two deferring commands: a claim matcher using startswith
    # instead of equality mispairs on it. `upgrade` is shipped too, which is what makes
    # the bare-built-in row below a real trap rather than a name nothing knows.
    nspath = os.path.join(tmp, "command-namespaces.json")
    with open(nspath, "w", encoding="utf-8") as fh:
        json.dump({"dev-workflows": ["implement", "specify", "upgrade", "vuln"],
                   "workflows-core": ["feedback", "prompt", "prompt-brainstorm",
                                      "prompt-grill-me"]}, fh, indent=2, sort_keys=True)
    sdir = os.path.join(tmp, "subagents")
    os.makedirs(sdir)
    with open(os.path.join(sdir, "agent-1.jsonl"), "w", encoding="utf-8") as fh:
        for ts, out in (("2026-09-01T10:02:15.000Z", 400),   # inside cede #1
                        ("2026-09-01T10:03:30.000Z", 200),   # inside cede #2
                        ("2026-09-01T09:00:00.000Z", 900),   # BEFORE the window
                        ("2026-09-01T11:00:00.000Z", 600)):  # AFTER the window
            fh.write(json.dumps({"timestamp": ts, "message": {
                "role": "assistant", "model": "claude-opus-5",
                "usage": {"input_tokens": 0, "output_tokens": out,
                          "cache_read_input_tokens": 0,
                          "cache_creation_input_tokens": 0}}}) + "\n")
    snap = os.path.join(tmp, "snap.json")
    with open(snap, "w", encoding="utf-8") as fh:
        json.dump({"ts": "2026-09-01T10:05:00Z", "cost_usd": 9.9}, fh)
    ckpt = os.path.join(tmp, "ck.json")
    with open(ckpt, "w", encoding="utf-8") as fh:
        json.dump({"line_offset": 0, "last_ts": "2026-09-01T09:30:00.000Z",
                   "last_snapshot_cost": 9.0}, fh)

    def run(*extra, **kw):
        cmd = [sys.executable, os.path.abspath(__file__),
               "--transcript", kw.get("transcript", tpath), "--prices", ppath,
               "--now-ts", "2026-09-01T10:05:00.000Z"]
        if kw.get("subagents", True):
            cmd += ["--subagents-dir", kw.get("subagents_dir", sdir)]
        # `namespaces=False` points the flag at a path that does not exist rather than
        # omitting it: omitting it now resolves the SHIPPED manifest beside this script,
        # and a fixture silently measured against real command names proves nothing.
        cmd += ["--namespaces", nspath if kw.get("namespaces", True)
                else os.path.join(tmp, "no-such-manifest.json")]
        cmd += ["--snapshot", snap, "--checkpoint", ckpt] + list(extra)
        out = subprocess.run(cmd, capture_output=True, text=True)
        if out.returncode != 0:
            bad("run failed: " + " ".join(extra) + " -> " + out.stderr.strip()[:200])
            return None
        return json.loads(out.stdout)

    def tokens(block):
        return sum(m["input_tokens"] + m["output_tokens"] + m["cache_read_tokens"]
                   + m["cache_write_tokens"] for m in block)

    # main() must hand scan_main and read_subagents the SAME map; the unit check above
    # passes one by hand, so only a run through the CLI shows main() doing it. A fork
    # file repeating a main-transcript id adds nothing, while its own new id still counts.
    _fork_only = os.path.join(tmp, "fork-only-subagents")
    os.makedirs(_fork_only)
    with open(os.path.join(_fork_only, "agent-fork.jsonl"), "w", encoding="utf-8") as fh:
        for r in (_rec("msg_B", "2026-09-01T10:00:03.000Z", 40),
                  _rec("msg_E", "2026-09-01T10:00:08.000Z", 7)):
            fh.write(json.dumps(r) + "\n")
    _solo = run(transcript=_dd, subagents=False)
    _forked = run(transcript=_dd, subagents_dir=_fork_only)
    check(_solo is not None and _forked is not None
          and tokens(_forked["models"]) - tokens(_solo["models"]) == 3 + 7 + 1000 + 500,
          "through the CLI, a main-transcript id a subagent file repeats counts once")

    whole = run()
    if whole is None:
        print("SELFTEST FAIL"); return 1
    boundaries = whole["command_boundaries"]
    names = [b["command"] for b in boundaries]
    claimable_names = [b["command"] for b in boundaries if b["claimable"]]
    # Section 8.7's fix: cutting no longer needs the manifest, so /upgrade and
    # /superpowers:implement now cut too -- they just never appear in the
    # CLAIMABLE view, which is the one the four un-split assertions below used
    # to be written against wholesale.
    check(claimable_names == ["/vuln", "/prompt-grill-me", "/prompt-grill-me", "/implement"],
          "the CLAIMABLE boundaries are exactly the four plugin invocations "
          "this marketplace's own manifest resolves, in order (got %r)"
          % (claimable_names,))
    check("/upgrade" in names and not boundaries[names.index("/upgrade")]["claimable"],
          "a BARE built-in now cuts the window (section 8.7), even though a "
          "plugin of this marketplace ships that name -- but it is never "
          "marked claimable")
    check("/compact" not in names,
          "/compact is not a boundary at all -- the one deliberate exception "
          "to 'every well-formed envelope cuts' (NON_CUTTING_BUILTINS)")
    check(names.count("/implement") == 1,
          "a FOREIGN namespace (/superpowers:implement) is never resolved down "
          "to this marketplace's bare /implement")
    check("/superpowers:implement" in names
          and not boundaries[names.index("/superpowers:implement")]["claimable"],
          "...and it appears in the boundary list under its own full text, "
          "cutting the window (section 8.7) without ever being claimable")
    check(len(names) == 6,
          "a marker quoted mid-message is still not a boundary (anchored "
          "match) -- 6 cuts total, up from 4 before the split added /upgrade "
          "and /superpowers:implement as non-claimable cuts")
    check([b["line_offset"] for b in boundaries] == [1, 2, 4, 8, 12, 15],
          "each boundary reports the transcript line it was found on")
    check(whole["namespaces"] == ["dev-workflows", "workflows-core"],
          "the accepted CLAIM namespaces come from the manifest -- EVERY "
          "plugin of this marketplace, not the one plugin that happens to be "
          "reading -- and cutting needs no namespace list at all")
    check(tokens(whole["models"]) == 11500,
          "unclaimed, the window is 11500 tok (out-of-window subagents "
          "excluded) -- unaffected by which envelopes cut, since nothing is "
          "claimed")
    check(abs(whole["cost_computed_usd"] - 0.2875) < 1e-9,
          "...priced at $0.2875")
    check(whole["cost_statusline_usd"] == 0.9,
          "with no claim the statusline delta is reported")

    two = run("--claim", "/prompt-grill-me", "--claim", "/prompt-grill-me")
    if two is None:
        print("SELFTEST FAIL"); return 1
    check(len(two["claims"]) == 2 and two["unmatched_claims"] == [],
          "two cedes of the SAME command match two DIFFERENT boundaries")
    c1, c2 = (two["claims"] + [None, None])[:2]
    # Cede #1's segment now ends at 10:02:30 -- the FOREIGN /superpowers:implement,
    # the next envelope of ANY kind -- not at 10:03:00.500 (cede #2's own start),
    # which is what it swallowed before section 8.7's fix (was $0.0425 / 1700 tok /
    # 60s; a foreign command's spend in between was silently folded into it). Cede
    # #2 is untouched: nothing new cuts between its own start and the replay.
    check(c1 and abs(c1["cost_computed_usd"] - 0.035) < 1e-9,
          "cede #1's segment now ends at the next envelope of ANY kind (the "
          "foreign /superpowers:implement, $0.035) rather than running all "
          "the way to cede #2 -- and still resolves by NAME, not position, "
          "so it is not /vuln's segment either")
    check(c2 and abs(c2["cost_computed_usd"] - 0.0275) < 1e-9,
          "cede #2 gets its own segment ($0.0275) -- unaffected, since nothing "
          "newly cuts between its start and the replay")
    check(c1 and tokens(c1["models"]) == 1400 and c2 and tokens(c2["models"]) == 1100,
          "a segment is half-open [start, end): a record exactly ON a boundary "
          "opens the new segment and does not also close the old one, and a "
          "sub-second record before the edge stays where it ran -- cede #1 is "
          "1400 tok now (500+500+400 subagent), down from 1700, because the "
          "foreign command's cut moves the 300-tok record after it into the "
          "remainder instead of into this claim")
    check(c1 and c1["duration_s"] == 30 and c2 and c2["duration_s"] == 59,
          "each claim's duration spans its own segment, not the whole window "
          "-- cede #1 is 30s now (10:02:00 to the foreign cut at 10:02:30), "
          "down from 60s")
    check(tokens(two["models"]) + tokens(c1["models"]) + tokens(c2["models"])
          == tokens(whole["models"]),
          "claims + remainder are token-exact against the unsplit window")
    check(two["cost_statusline_usd"] is None,
          "a claimed window reports no statusline delta (option B cannot split)")

    pre = run("--claim", "/prompt")
    check(pre is not None and pre["unmatched_claims"] == ["/prompt"]
          and pre["claims"] == [],
          "/prompt does not match /prompt-grill-me (equality, not prefix)")

    miss = run("--claim", "/prompt-brainstorm")
    check(miss is not None and miss["unmatched_claims"] == ["/prompt-brainstorm"]
          and miss["claims"] == [],
          "a claim with no matching boundary is reported, never guessed onto one")
    check(miss is not None and tokens(miss["models"]) == tokens(whole["models"]),
          "an unmatched claim carves out nothing -- no spend is lost")

    nosub = run("--claim", "/prompt-grill-me", subagents=False)
    # Same cut (foreign /superpowers:implement at 10:02:30) as the `two` test's cede
    # #1, minus the subagent's 400: 500+500=1000 tok, $0.025 -- down from $0.0325
    # (1300 tok), which is what this segment wrongly ran to (10:03:00.500) before
    # the foreign command was a cut at all.
    check(nosub is not None and abs(nosub["claims"][0]["cost_computed_usd"] - 0.025) < 1e-9,
          "subagent spend lands in the segment it ran in, not elsewhere -- and "
          "the claim itself is correctly shortened by the foreign command's "
          "new cut, from $0.0325 to $0.025")

    bare = run(namespaces=False)
    # command_envelope never consults ns_map -- cutting is structural, so all 6
    # envelopes (everything but /compact) still cut with no manifest resolved at
    # all. claimable_command DOES require ns_map, so every one of them comes back
    # unclaimable: nothing is guessed onto a match, but the window is still
    # segmented correctly if a caller ever claims against it.
    check(bare is not None and len(bare["command_boundaries"]) == 6
          and all(not b["claimable"] for b in bare["command_boundaries"]),
          "with no manifest resolved, cuts still apply structurally (6, same "
          "as with the manifest) but NOTHING is claimable -- nothing "
          "claimable is guessed, which is what 'nothing is guessed' now means")
    check(bare is not None and bare["namespaces"] == [],
          "with no manifest resolved, there is no namespace to claim against")
    check(bare is not None and tokens(bare["models"]) == tokens(whole["models"]),
          "boundary detection never changes the cost figure")

    # ---------------------------------------------------------- the split cases
    # Their own transcripts, and no subagent dir: the shared subagent entries sit at
    # timestamps inside these windows too, and would silently move the token figures
    # these cases exist to pin.
    seg = run("--claim", "/prompt-grill-me", transcript=t2path, subagents=False)
    seg_boundaries = seg["command_boundaries"] if seg else []
    segn = [b["command"] for b in seg_boundaries]
    seg_claimable = {b["command"]: b["claimable"] for b in seg_boundaries}
    check(segn == ["/prompt-grill-me", "/vuln", "/upgrade", "/superpowers:implement",
                   "/prompt", "/workflows-core:vuln"],
          "every well-formed envelope cuts now, whatever its namespace or "
          "claimability (got %r)" % (segn,))
    check(segn.count("/vuln") == 1,
          "a command resolves CLAIMABLE against ITS OWN plugin's names: "
          "/workflows-core:vuln pairs a real namespace with a real command of "
          "the marketplace that is not that namespace's, and is reported "
          "under its own full text rather than colliding with the bare /vuln")
    check(seg_claimable.get("/workflows-core:vuln") is False,
          "...and it cuts the window regardless (command_envelope does not "
          "consult the manifest) but is never claimable -- a map read as one "
          "FLAT set of every plugin's names would mark it claimable, which is "
          "what this pins now that structural cutting no longer depends on "
          "manifest resolution at all")
    check(seg is not None and seg["unmatched_claims"] == [] and len(seg["claims"]) == 1
          and tokens(seg["claims"][0]["models"]) == 5000,
          "the claim gets 5000 -- its own segment, ending at the SIBLING's boundary, "
          "not the 9000 that swallows the sibling's run as well")
    check(seg is not None and tokens(seg["models"]) == 4800,
          "the remainder keeps /vuln's 4000 and the replaying run's 800 (4800), "
          "not the 800 a swallowed sibling segment leaves behind")
    check(seg_claimable.get("/upgrade") is False,
          "a BARE built-in whose name a plugin of this marketplace ships now "
          "cuts the window (section 8.7's fix) but widening the namespaces "
          "accepted for CLAIMING never admits it")
    check(seg_claimable.get("/superpowers:implement") is False,
          "a FOREIGN marketplace's command now cuts the window too (section "
          "8.7's fix) but is never admitted as claimable")
    check("/implement" not in segn,
          "...and it is reported under its own full namespaced text, never "
          "stripped down to a bare /implement this marketplace's claims "
          "could match")

    xp = run("--claim", "/prompt-brainstorm", transcript=t3path, subagents=False)
    check(xp is not None and xp["unmatched_claims"] == [] and len(xp["claims"]) == 1
          and tokens(xp["claims"][0]["models"]) == 2000,
          "a claim whose ceding run ships from a DIFFERENT plugin than the run "
          "replaying it matches (2000)")
    check(xp is not None and tokens(xp["models"]) == 1000,
          "...and that replaying run keeps exactly its own 1000")

    # --advance-only writes exactly the checkpoint a full run reports, prices nothing,
    # and prints one line. A run skipped with --skip-costs must leave the next
    # measured command's window starting where a measured run would have.
    full = run()
    ck_adv = os.path.join(tmp, "ck-adv.json")
    with open(ckpt, encoding="utf-8") as src, open(ck_adv, "w", encoding="utf-8") as dst:
        dst.write(src.read())
    adv = subprocess.run(
        [sys.executable, os.path.abspath(__file__), "--transcript", tpath,
         "--subagents-dir", sdir, "--snapshot", snap, "--checkpoint", ck_adv,
         "--now-ts", "2026-09-01T10:05:00.000Z", "--advance-only"],
        capture_output=True, text=True)
    check(adv.returncode == 0 and adv.stdout.strip().startswith("checkpoint advanced:")
          and len(adv.stdout.strip().splitlines()) == 1,
          "--advance-only exits 0 and prints one line, with no --prices")
    with open(ck_adv, encoding="utf-8") as fh:
        written = json.load(fh)
    check(full is not None and written == full["new_checkpoint"],
          "--advance-only writes the same checkpoint a full run reports")
    noc = subprocess.run(
        [sys.executable, os.path.abspath(__file__), "--transcript", tpath, "--advance-only"],
        capture_output=True, text=True)
    check(noc.returncode != 0, "--advance-only without --checkpoint is refused")

    # Skill-tool boundary detection. A command the model runs -- on a prose request, or
    # from another command -- reaches the family through the Skill tool and leaves no
    # <command-name> envelope, so reading user messages alone let the preceding claim run
    # straight through the invocation.
    _ns = {"product-workflows": {"update-prd"}, "workflows-core": {"prompt"}}
    def _sk(skill):
        return {"type": "assistant", "timestamp": "2026-09-01T10:00:00.000Z",
                "message": {"content": [{"type": "tool_use", "name": "Skill",
                                         "input": {"skill": skill}}]}}
    check(command_envelope(_sk("product-workflows:update-prd"), _ns)
          == "product-workflows:update-prd",
          "a Skill-tool invocation of a known command CUTS the window")
    check(command_envelope(_sk("workflows-core:model-routing"), _ns) is None,
          "a Skill-tool invocation of a NON-command skill does not cut")
    check(command_envelope(_sk("superpowers:brainstorming"), _ns) is None,
          "a Skill-tool invocation of another marketplace's skill does not cut")
    check(command_envelope(_sk("update-prd"), _ns) is None,
          "a bare (un-namespaced) Skill name does not cut")
    check(command_envelope({"type": "assistant", "message": {"content": [
              {"type": "tool_use", "name": "Bash", "input": {"command": "x"}}]}},
              _ns) is None,
          "a non-Skill tool_use does not cut")
    # The asymmetry is the point: the typed half stays permissive (it cuts on a
    # foreign marketplace's command too), the Skill half resolves. Asserting both
    # keeps a later reader from "harmonising" them and reintroducing one of the
    # two defects -- a swallowed boundary, or a shattered window.
    check(command_envelope({"type": "user", "message": {"content":
              "<command-name>/superpowers:implement</command-name>"}}, _ns)
          == "superpowers:implement",
          "the TYPED half still cuts on a foreign command (deliberately permissive)")
    check(command_envelope({"type": "user", "message": {"content":
              "<command-name>/product-workflows:update-prd</command-name>"}}, _ns)
          == "product-workflows:update-prd",
          "the typed shape still resolves after the Skill shape was added")
    # A Skill call the tool refused ran nothing -- a typed-only command (flagged
    # disable-model-invocation) is refused whenever the model reaches for it -- so it cuts
    # nothing: scan_main drops the boundary once the call's tool_result comes back an error.
    def _scan(result):
        path = os.path.join(tmp, "skill-refused.jsonl")
        sk = _sk("product-workflows:update-prd")
        sk["message"]["content"][0]["id"] = "toolu_x"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(sk) + "\n")
            fh.write(json.dumps({"type": "user", "timestamp": "2026-09-01T10:00:01.000Z",
                                 "message": {"content": [dict(result, type="tool_result",
                                                              tool_use_id="toolu_x")]}}) + "\n")
        return scan_main(path, 0, _ns)[2]
    check(_scan({"is_error": True, "content": "cannot be used with Skill tool"}) == [],
          "a Skill call the tool refused does not cut")
    check(len(_scan({"content": "Launching skill: product-workflows:update-prd"})) == 1,
          "a Skill call that ran still cuts")

    if failures:
        print("SELFTEST FAIL (%d)" % len(failures))
        return 1
    print("SELFTEST PASS")
    return 0



def selftest():
    """Run the selftest in a fresh temporary directory and always remove it.

    The body returns early on several failures; the temporary tree it writes
    (transcripts, a price table, a fake plugin root) is removed on every path,
    so repeated runs leave nothing behind -- on a developer machine or a CI
    runner that is reused."""
    import shutil
    import tempfile
    tmp = tempfile.mkdtemp(prefix="session-cost-selftest-")
    try:
        return _selftest_body(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def match_claims(claim_names, boundaries):
    """Pair each claimed command name with the boundary it actually ran at.

    Matching is BY NAME, scanning forward, never by position. A window routinely
    contains boundaries no claim corresponds to -- `/vuln`, `/upgrade`,
    `/statusline`, `/docs-profile`, `/docs-serve`, `/harvest-decisions` and the two guideline
    reviewers emit no cost entry at all, and any run the user interrupted leaves a boundary behind too.
    Pairing the k-th claim with the k-th boundary therefore skews the moment one
    of those sits in the window, and files one command's spend under another
    command's lifecycle labels.

    Returns (matched, unmatched). Each matched entry carries the half-open
    segment [start, end) that belongs to that claim; end is None for the final
    segment, meaning "to the end of the window".

    A candidate boundary must be `claimable` -- `boundaries` now also holds
    CUT-only entries (command_envelope's, never resolved against the
    manifest), and those must never be mistaken for a match even where their
    `command` text happens to coincide with a claim name. The segment's END,
    below, deliberately does NOT carry the same restriction: it is the very
    next boundary of ANY kind, claimable or not -- a foreign or otherwise
    non-claimable command genuinely closes the window it interrupts."""
    matched, unmatched = [], []
    cursor = 0
    for name in claim_names:
        hit = None
        for i in range(cursor, len(boundaries)):
            if boundaries[i].get("claimable") and boundaries[i]["command"] == name:
                hit = i
                break
        if hit is None:
            unmatched.append(name)
            continue
        cursor = hit + 1
        start = parse_ts(boundaries[hit]["ts"])
        end = parse_ts(boundaries[hit + 1]["ts"]) if hit + 1 < len(boundaries) else None
        matched.append({"command": name, "ts": boundaries[hit]["ts"],
                        "start": start, "end": end})
    return matched, unmatched


def price_block(acc, prices):
    """Turn one accumulator into the models array + total, per section 6."""
    models = []
    total = 0.0
    for model in sorted(acc):
        tok = acc[model]
        cost_usd, note = price_model(model, tok, prices)
        if cost_usd is not None:
            total += cost_usd
        entry = {
            "model": model,
            "cost_usd": cost_usd,
            "input_tokens": tok["input"],
            "output_tokens": tok["output"],
            "cache_read_tokens": tok["cache_read"],
            "cache_write_tokens": tok["cache_write_5m"] + tok["cache_write_1h"],
        }
        if note:
            entry["note"] = note
        mods = pricing_modifiers(tok)
        if mods:
            entry["modifiers"] = mods
        models.append(entry)
    return models, round(total, 4)


def main():
    ap = argparse.ArgumentParser(
        description="Compute a session-cost delta for one command of this family.")
    ap.add_argument("--transcript", default="")
    ap.add_argument("--subagents-dir", default="")
    ap.add_argument("--prices", default="")
    ap.add_argument("--checkpoint", default="")
    ap.add_argument("--snapshot", default="")
    ap.add_argument("--now-ts", default="")
    ap.add_argument("--namespaces", default=DEFAULT_NAMESPACE_MAP,
                    help="The command-namespace manifest boundaries are resolved "
                         "against. Defaults to command-namespaces.json beside this "
                         "script, which is the only correct answer at a call site: a "
                         "caller-supplied plugin path names whichever plugin READ the "
                         "reference, not the one that ran. Point it elsewhere only to "
                         "test; where it resolves to nothing, no boundary is reported.")
    ap.add_argument("--claim", action="append", default=[], metavar="/COMMAND",
                    help="A deferred run to carve out of this window, oldest "
                         "first (cost-emission.md section 13). Repeatable. Each "
                         "is matched to a boundary BY NAME; the remainder stays "
                         "with this run.")
    ap.add_argument("--advance-only", action="store_true",
                    help="Write new_checkpoint to --checkpoint and exit, pricing "
                         "nothing: the --skip-costs path (run-flags.md skip-cost). "
                         "Keeps the next measured command's window correct.")
    ap.add_argument("--selftest", action="store_true",
                    help="Run the built-in fixture checks and exit.")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    # --transcript and --prices are declared optional only so --selftest can run
    # without them; for a real measurement they stay mandatory.
    required = ("transcript", "checkpoint") if args.advance_only else ("transcript", "prices")
    missing = [f for f in required if not getattr(args, f)]
    if missing:
        ap.error("the following arguments are required: "
                 + ", ".join("--" + m for m in missing))
    # A path that is merely absent or unreadable would otherwise price the run at
    # $0 and exit clean -- a plausible-but-wrong figure, which is worse than a
    # loud failure. Note this is a check on the ARGUMENT, not on the contract that
    # a malformed LINE never fails the run; that still holds.
    if not os.path.isfile(args.transcript):
        ap.error("--transcript is not a readable file: %s" % args.transcript)

    now_dt = parse_ts(args.now_ts) or datetime.datetime.now(datetime.timezone.utc)

    checkpoint = {"line_offset": 0, "last_ts": None, "last_snapshot_cost": None}
    if args.checkpoint and os.path.isfile(args.checkpoint):
        try:
            with open(args.checkpoint, encoding="utf-8", errors="replace") as fh:
                loaded = json.load(fh)
            if isinstance(loaded, dict):
                for k in checkpoint:
                    if k in loaded:
                        checkpoint[k] = loaded[k]
        except (ValueError, OSError):
            pass
    line_offset = checkpoint["line_offset"] if isinstance(checkpoint["line_offset"], int) else 0
    last_dt = parse_ts(checkpoint["last_ts"])

    ns_map = load_namespace_map(args.namespaces)

    records = []
    # One map across the main transcript and every subagent file: a fork copies its
    # parent's records under the same ids. `records` is empty when main_records is
    # appended below, so the map's indices stay valid in it.
    by_id = {}
    new_line_offset, main_first_ts, boundaries, main_records = scan_main(
        args.transcript, line_offset, ns_map, by_id=by_id
    )
    current_snapshot = read_snapshot_cost(args.snapshot)
    baseline_snapshot = checkpoint["last_snapshot_cost"]
    new_last_snapshot_cost = (
        current_snapshot if isinstance(current_snapshot, (int, float)) else baseline_snapshot
    )
    new_checkpoint = {
        "line_offset": new_line_offset,
        "last_ts": iso_z(now_dt),
        "last_snapshot_cost": new_last_snapshot_cost,
    }
    # --advance-only needs nothing past the checkpoint: return before the
    # subagent read, the claim match and any pricing.
    if args.advance_only:
        tmp_ck = args.checkpoint + ".tmp"
        os.makedirs(os.path.dirname(os.path.abspath(args.checkpoint)), exist_ok=True)
        with open(tmp_ck, "w", encoding="utf-8") as fh:
            json.dump(new_checkpoint, fh)
        os.replace(tmp_ck, args.checkpoint)
        print("checkpoint advanced: line_offset=%s last_ts=%s"
              % (new_checkpoint["line_offset"], new_checkpoint["last_ts"]))
        return

    prices = load_prices(args.prices) if args.prices else {"models": {}}
    records.extend(main_records)
    sub_first_ts = read_subagents(args.subagents_dir, last_dt, now_dt, records, by_id=by_id)

    matched, unmatched = match_claims(args.claim, boundaries)

    notes = []
    if args.claim and ns_map is None:
        notes.append("no command-namespace manifest resolved at %r: no "
                     "invocation can be claimed (window cuts still apply "
                     "structurally, independent of any manifest)" % (args.namespaces,))
    elif args.claim and not any(b.get("claimable") for b in boundaries):
        notes.append("no claimable command boundary found in this window "
                     "(namespaces known: %s)" % (", ".join(sorted(ns_map)),))

    # Partition every buffered record into exactly one bucket: a claimed segment,
    # or the remainder that stays with this run. Disjoint by construction, and
    # exhaustive -- so the slices always sum to the whole window, and an unmatched
    # claim costs nothing beyond its own attribution (its spend simply stays here).
    remainder = {}
    for m in matched:
        m["acc"] = {}
    for ts, model, usage in records:
        target = remainder
        if ts is not None:
            for m in matched:
                if m["start"] is not None and ts >= m["start"] \
                        and (m["end"] is None or ts < m["end"]):
                    target = m["acc"]
                    break
        add_usage(target, model, usage)

    models, cost_computed = price_block(remainder, prices)

    if last_dt is not None:
        base_dt = last_dt
    else:
        candidates = [t for t in (main_first_ts, sub_first_ts) if t is not None]
        base_dt = min(candidates) if candidates else now_dt
    duration_s = int(max(0, (now_dt - base_dt).total_seconds()))

    # Option B (statusline cross-check) measures whole renders, so it cannot be
    # apportioned once part of the window has been carved off. With any claim the
    # field is omitted rather than over-reported against the remainder.
    cost_statusline = None
    if not matched and isinstance(current_snapshot, (int, float)) \
            and isinstance(baseline_snapshot, (int, float)):
        cost_statusline = round(current_snapshot - baseline_snapshot, 4)

    claims_out = []
    for m in matched:
        cm, cc = price_block(m["acc"], prices)
        end_dt = m["end"] or now_dt
        claims_out.append({
            "command": m["command"],
            "ts": m["ts"],
            "models": cm,
            "cost_computed_usd": cc,
            "duration_s": int(max(0, (end_dt - m["start"]).total_seconds()))
            if m["start"] is not None else 0,
        })

    result = {
        "models": models,
        "cost_computed_usd": cost_computed,
        "cost_statusline_usd": cost_statusline,
        "duration_s": duration_s,
        "namespaces": sorted(ns_map) if ns_map else [],
        "notes": notes,
        "command_boundaries": boundaries,
        "claims": claims_out,
        "unmatched_claims": unmatched,
        "new_checkpoint": new_checkpoint,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
