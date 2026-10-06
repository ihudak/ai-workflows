#!/usr/bin/env python3
"""Validate every plugin manifest and marketplace catalog in this repository.

Guards the defects that have actually shipped from this repo, most of them more
than once:

  1. An over-long plugin ``description``. GitHub Copilot CLI rejects a
     marketplace whose ``plugins[i].description`` exceeds 1024 characters, and
     it rejects the WHOLE catalog -- every plugin in the marketplace then fails
     to install or update, not just the offending one. Claude Code enforces no
     such limit, so the Claude editions can drift far past it with no local
     symptom and then break the Copilot edition at port time. Trimmed by hand
     three times in the Copilot edition before this check existed; each trim
     reset the length without stopping the growth that caused it.

  2. Version drift between a plugin's own ``plugin.json`` and the marketplace
     catalog entry that advertises it. They are independent files kept in sync
     by hand; a release that bumps one and forgets the other ships a catalog
     pointing at the wrong version. Has shipped four times.

  3. A plugin manifest with no catalog entry at all. Every check above is
     forward-only: it starts from a ``marketplace.json`` entry and asks
     whether the ``plugin.json`` it names exists. Nothing asked the reverse --
     whether every ``plugin.json`` under the repository is named by some
     catalog. A plugin built this way (a valid manifest, no row in any
     ``marketplace.json``) passed every gate and shipped to nobody, because
     Claude Code and Copilot CLI both install only what a catalog advertises.

  4. Two plugin manifests declaring the same ``name``. Not a shipped incident
     but a disproved claim: a plan for this repository's own five-plugin split
     asserted this was already structurally enforced, and a review built a
     fixture -- two directories both declaring ``"name": "dupname"`` -- and
     watched it validate clean. ``manifests[name] = (...)`` was a plain dict
     assignment, so the second directory silently overwrote the first's entry;
     ``advertised`` is a ``set[str]``, so a catalog entry naming either
     directory read as satisfied either way. A ``plugin.json`` copy-pasted
     from another plugin and never given its own ``name`` would collide
     invisibly, and nothing would catch it.

  5. An over-long command, agent or skill ``description`` (frontmatter). Claude
     Code gives every installed plugin's descriptions one listing, sized as a
     share of the context window, and shortens all of them once it overflows;
     ten of this family's command descriptions had passed 1,024 characters,
     one 4,310, narrating procedure their bodies already carry. Fails above
     1,024 (the Agent Skills ceiling), warns above 600
     (docs/maintainers/rationale.md, "entry-descriptions").

  6. A command left in that listing for nothing, or flagged out of it while
     something calls it. A command whose frontmatter sets
     ``disable-model-invocation: true`` is absent from the listing and refused by
     the Skill tool, though it still runs when typed; the 600-character budget
     still left the family's entries at 20,997 characters against the 8,000 a
     200K window gives the listing. Every command carries the flag unless a file
     runs it through the Skill tool as ``skill: "<plugin>:<name>"`` or its plugin
     ships a skill of its name, and nothing flagged is run that way
     (docs/maintainers/rationale.md, "typed-only-commands").

Note on what is deliberately NOT checked: the ``description`` in a catalog
entry and in the matching ``plugin.json`` are not required to be identical.
They are independently authored in practice -- Copilot's ``prose-style``
blurbs, for instance, share no wording at all -- so an equality check would
fail on correct content. The half-fix it might have caught (Copilot's
marketplace trimmed to 964 while its plugin.json stayed at 2091) is already
caught by applying the length check to both files.

It also enforces the repo-root instruction budget: ``CLAUDE.md`` fails above 40,000
characters and warns above 36,000, and each ``.claude/rules/*.md`` warns above 20,000.
And it checks that every ``.claude/rules/*.md`` declares a non-empty ``paths:`` frontmatter
list whose every glob matches at least one file outside ``.claude/rules/`` itself, so a rule
that would load into every session, a glob left dead by a rename, or a glob that matches only
its own rules file fails the build instead of surviving unnoticed.

Usage:
    python3 scripts/validate-catalog.py [REPO_ROOT ...]
    python3 scripts/validate-catalog.py --selftest

With no arguments, validates the repository containing this script. Exits 0
when everything passes, 1 on any error. Warnings alone do not fail the run.

``--selftest`` builds a minimal catalog in a temporary directory, mutates it once
per failure mode, and asserts both the exit status and WHICH error was reported.
Its two siblings under ``scripts/`` have had one for releases; this one did not,
so nothing proved it could still fail -- and a checker that cannot be shown to
fail proves nothing when it passes. Asserting the message rather than the exit
code alone is deliberate: every mutation here trips a non-zero exit, so exit
status alone would let a mutation that broke a DIFFERENT rule register as
success, which is exactly how the sibling gate's selftest went green over a real
regression.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# GitHub Copilot CLI's hard schema limit. Applied to every edition, not just
# the Copilot one: canonical is the source the Copilot blurb is ported from, so
# letting canonical grow past the limit is what reloads the gun.
DESCRIPTION_MAX = 1024

# Growth in this field is a ratchet -- each release has historically appended a
# sentence and removed nothing (259 chars at inception, 2788 by 2.52.0). Warn
# with enough headroom that trimming happens as routine maintenance instead of
# as an outage.
DESCRIPTION_WARN = 900

# A command's, agent's or skill's own frontmatter `description`. 1024 is the Agent Skills
# ceiling; Claude Code also gives the whole skill listing a slice of the context window
# (1% by default) and shortens every plugin's descriptions once the listing outgrows it, so
# a description that narrates its procedure costs every other plugin's too. 600 leaves room
# for what it does, when to use it and what it is not for.
ENTRY_DESC_MAX = 1024
ENTRY_DESC_WARN = 600

# A command the user types carries `disable-model-invocation: true`, which keeps it out of
# that listing altogether (the Skill tool then refuses it; a typed command still runs). Only a
# command another file runs through the Skill tool -- written `skill: "<plugin>:<name>"` --
# stays model-invocable (docs/maintainers/rationale.md, "typed-only-commands").
TYPED_ONLY_KEY = "disable-model-invocation"
SKILL_CALL = re.compile(r'skill:\s*"([a-z0-9-]+):([a-z0-9-]+)"')

# The repo-root CLAUDE.md loads into every session and every non-fork subagent here. It
# reached 189,969 characters by accretion before the 2026-09-23 split moved area rules to
# .claude/rules/ (loaded by path) and evidence to docs/maintainers/rationale.md (never
# loaded). Characters, not bytes or lines: the budget is context, and the file is unwrapped
# paragraphs, so a line count means nothing.
CLAUDE_MD_MAX = 40_000
CLAUDE_MD_WARN = 36_000
RULES_FILE_WARN = 20_000

SKIP_DIRS = {".git", "node_modules", ".superpowers", ".idea"}

# scripts/fixtures/ ships a synthetic plugin.json (fixture-two) that exists solely as
# check-docs.sh --selftest scaffolding: it names no real, installable plugin and is
# deliberately absent from every marketplace.json. Without an exclusion the reverse
# "every manifest is advertised" assertion below fires on it, reporting a defect that
# does not exist.
#
# This is a PATH prefix, not a SKIP_DIRS entry, and the distinction is load-bearing.
# SKIP_DIRS matches a bare directory NAME at any depth, which is safe for `.git` and
# `node_modules` -- names nothing legitimate is ever called -- but "fixtures" is a
# common word. As a SKIP_DIRS entry it silently hid any manifest nested under a
# directory named `fixtures` anywhere in the tree, including a real plugin's own test
# corpus, from BOTH directions of the advertisement check. Anchored here instead, it
# excludes exactly the one directory it was written for.
# A git worktree at `.worktrees/<name>/` (or `worktrees/<name>/`) is a SECOND FULL COPY
# of the tree, so every plugin name in it appears twice and the uniqueness assertion
# below reports one ERROR per plugin -- measured at 10 errors and 3 warnings on a tree
# with one worktree present. The copy is git-ignored (`/.worktrees/` in .gitignore) and
# is never what this gate is asked about. It matters beyond the annoyance: the
# merged-result gate run is the last check before a branch lands, it runs from the main
# checkout while the worktree is still on disk, and it fails there for a reason that has
# nothing to do with the merge -- at the precise moment someone is deciding whether the
# merge was sound. Both names are excluded because both are what the worktree tooling
# creates; only `.worktrees` is in this repo's .gitignore today.
#
# Root-anchored for exactly the reason the `fixtures` exclusion above is: `worktrees` is
# an ordinary word, and a bare name-match at any depth would hide a real manifest nested
# under any directory that happened to be called that. The selftest pins the anchoring
# with a pair -- a copy under the root's own `.worktrees/` passes, an identical one under
# a `worktrees` directory further down is still rejected.
SKIP_PREFIXES = (("scripts", "fixtures"), (".worktrees",), ("worktrees",))


def find_files(root: Path, name: str) -> list[Path]:
    """Locate every file with this name, at any depth.

    Deliberately unbounded: Copilot keeps its catalog at
    ``.github/plugin/marketplace.json`` (depth 3) while Claude editions use
    ``.claude-plugin/marketplace.json`` (depth 2). A depth-limited search
    reported "Copilot has no catalog" once and shipped a stale one as a result.
    """
    return sorted(
        p
        for p in root.rglob(name)
        if not any(part in SKIP_DIRS for part in p.parts)
        and not any(
            p.relative_to(root).parts[: len(prefix)] == prefix
            for prefix in SKIP_PREFIXES
        )
    )


def load(path: Path) -> dict | None:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"  ERROR {path}: cannot parse -- {exc}")
        return None


def check_description(label: str, description: str) -> tuple[int, int]:
    """Return (errors, warnings) for one description field."""
    size = len(description)
    if size > DESCRIPTION_MAX:
        print(
            f"  ERROR {label}: description is {size} chars, "
            f"limit is {DESCRIPTION_MAX} "
            f"(Copilot rejects the entire catalog, breaking every plugin in it)"
        )
        return 1, 0
    if size > DESCRIPTION_WARN:
        print(
            f"  WARN  {label}: description is {size} chars, "
            f"nearing the {DESCRIPTION_MAX} limit -- trim it now, "
            f"and move release detail to CHANGELOG.md"
        )
        return 0, 1
    return 0, 0


def check_instruction_sizes(root: Path) -> tuple[int, int]:
    """Return (errors, warnings) for the repo-root instruction tiers' size budget."""
    errors = warnings = 0
    claude = root / "CLAUDE.md"
    if claude.is_file():
        size = len(claude.read_text(encoding="utf-8"))
        if size > CLAUDE_MD_MAX:
            print(
                f"  ERROR CLAUDE.md is {size} characters, limit is {CLAUDE_MD_MAX} -- "
                f"move a rule that binds one area to .claude/rules/<area>.md, and "
                f"evidence to docs/maintainers/rationale.md"
            )
            errors += 1
        elif size > CLAUDE_MD_WARN:
            print(
                f"  WARN  CLAUDE.md is {size} characters, nearing the {CLAUDE_MD_MAX} "
                f"limit -- move evidence to docs/maintainers/rationale.md now"
            )
            warnings += 1
    for rules_file in sorted((root / ".claude" / "rules").glob("*.md")):
        size = len(rules_file.read_text(encoding="utf-8"))
        if size > RULES_FILE_WARN:
            rel = rules_file.relative_to(root)
            print(
                f"  WARN  {rel} is {size} characters, past {RULES_FILE_WARN} -- split it "
                f"by command group with narrower paths: globs, or move evidence to "
                f"docs/maintainers/rationale.md"
            )
            warnings += 1
    return errors, warnings


def check_rules_paths(root: Path) -> tuple[int, int]:
    """Return (errors, warnings): every .claude/rules/*.md must declare a non-empty `paths:`
    list, and every glob in it must match at least one file under root, outside
    .claude/rules/ itself.

    Parser limits, stated so a reader does not mistake them for Claude Code's: `paths:` must
    be a top-level (unindented) key of the frontmatter, other top-level keys may sit before
    or after it, and its value must be a block list of `- ` items -- an inline `[a, b]` list
    or a bare string is not read. Globs go through pathlib, which has no brace expansion, so
    a `{a,b}` glob matches nothing and is reported dead; Claude Code's support for braces is
    unverified, so write each alternative as its own entry. A match under .claude/rules/ is
    not counted, so a glob whose every match is a rules file is reported -- including one
    written on purpose to load a rule while rules files are edited; none exists today."""
    errors = warnings = 0
    rules_dir = root / ".claude" / "rules"
    if not rules_dir.is_dir():
        return errors, warnings
    rules_parts = (".claude", "rules")

    no_paths = (
        "no paths: -- without one, Claude Code loads this file into every session, "
        "which defeats the split"
    )

    for rules_file in sorted(rules_dir.glob("*.md")):
        rel = rules_file.relative_to(root)
        lines = rules_file.read_text(encoding="utf-8").splitlines()

        if not lines or lines[0].rstrip() != "---":
            print(f"  ERROR {rel}: {no_paths} (no frontmatter)")
            errors += 1
            continue

        try:
            close = 1 + lines[1:].index("---")
        except ValueError:
            print(f"  ERROR {rel}: {no_paths} (frontmatter '---' is never closed)")
            errors += 1
            continue

        frontmatter = lines[1:close]
        key_at = [i for i, line in enumerate(frontmatter) if line.rstrip() == "paths:"]
        if not key_at:
            print(f"  ERROR {rel}: {no_paths} (frontmatter has no top-level 'paths:' key "
                  f"with a block list under it)")
            errors += 1
            continue

        globs: list[str] = []
        malformed = False
        for line in frontmatter[key_at[0] + 1:]:
            stripped = line.strip()
            if not stripped:
                continue
            if not line[:1].isspace() and not stripped.startswith("-"):
                break  # the next top-level key ends the paths: list
            if not stripped.startswith("-"):
                print(f"  ERROR {rel}: unexpected line in the paths: list -- {line!r}")
                errors += 1
                malformed = True
                break
            item = stripped[1:].strip()
            if len(item) >= 2 and item[0] == item[-1] and item[0] in "\"'":
                item = item[1:-1]
            if not item:
                print(f"  ERROR {rel}: an empty entry in the paths: list")
                errors += 1
                malformed = True
                break
            globs.append(item)
        if malformed:
            continue

        if not globs:
            print(f"  ERROR {rel}: {no_paths} (the paths: list is empty)")
            errors += 1
            continue

        for glob in globs:
            # Mirror find_files' SKIP_DIRS/SKIP_PREFIXES exclusion, anchored at root: a
            # glob whose only matches sit under .git, a worktree copy, node_modules or
            # .superpowers is dead for this gate's purposes even though Path.glob finds
            # bytes there.
            # Files only: `<dir>/**` yields <dir> itself, so an empty directory would
            # otherwise keep a glob that no file read can ever trigger looking live. And
            # before Python 3.13 a trailing `**` yields directories only, never files, so
            # the files-only filter alone would call every `<dir>/**` glob dead on CI's
            # 3.11. Globbing `<pattern>/*` as well (a `**` then `*` matches every file at
            # any depth below, on every version) makes the answer version-independent.
            candidates = set(root.glob(glob))
            if glob == "**" or glob.endswith("/**"):
                candidates.update(root.glob(glob + "/*"))
            matches = [
                p for p in candidates
                if p.is_file()
                and not any(part in SKIP_DIRS for part in p.parts)
                and not any(
                    p.relative_to(root).parts[: len(prefix)] == prefix
                    for prefix in SKIP_PREFIXES
                )
            ]
            # A match under .claude/rules/ does not count either. A rules file is a real
            # file, so a glob naming its own path -- or two rules naming only each other --
            # passed as live, yet such a rule loads only when a rules file is itself opened,
            # never during the work it governs.
            outside = [p for p in matches if p.relative_to(root).parts[:2] != rules_parts]
            if not matches:
                print(f"  ERROR {rel}: paths: glob {glob!r} matches no file under {root}")
                errors += 1
            elif not outside:
                inside = ", ".join(sorted(str(p.relative_to(root)) for p in matches))
                print(
                    f"  ERROR {rel}: paths: glob {glob!r} matches only files under "
                    f".claude/rules/ ({inside}) -- a rule loads when Claude reads a file its "
                    f"paths: match, and a rules file is read only when it is itself opened, "
                    f"never during the work the rule governs; point the glob at the files the "
                    f"rule is about"
                )
                errors += 1

    return errors, warnings


def frontmatter_description(text: str) -> str | None:
    """The `description` a file's YAML frontmatter holds, as YAML reads it, or None.

    Enough YAML for the shapes this repository writes: a plain or quoted scalar on the
    key's line, a plain scalar continued on indented lines, and a `>`/`|` block scalar
    (folded lines joined by a space, literal ones by a newline). Nothing else is parsed.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None
    body = lines[1:end]
    for i, line in enumerate(body):
        if not line.startswith("description:"):
            continue
        head = line[len("description:"):].strip()
        more = []
        for nxt in body[i + 1:]:
            if nxt and not nxt[0].isspace():
                break
            more.append(nxt.strip())
        while more and not more[-1]:
            more.pop()
        if head[:1] in (">", "|"):
            return ("\n" if head[0] == "|" else " ").join(more)
        value = " ".join([head] + [m for m in more if m])
        if len(value) >= 2 and value[0] == value[-1] == '"':
            try:  # YAML's double-quoted escapes include JSON's
                return json.loads(value)
            except json.JSONDecodeError:
                return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        if len(value) >= 2 and value[0] == value[-1] == "'":
            return value[1:-1].replace("''", "'")
        return value
    return None


def check_entry_descriptions(root: Path) -> tuple[int, int]:
    """Fail a command's, agent's or skill's description above ENTRY_DESC_MAX, warn above ENTRY_DESC_WARN."""
    errors = warnings = 0
    plugins = root / "plugins"
    found = sorted(plugins.glob("*/commands/*.md")) + sorted(plugins.glob("*/agents/*.md")) \
        + sorted(plugins.glob("*/skills/*/SKILL.md"))
    for path in found:
        description = frontmatter_description(path.read_text(encoding="utf-8"))
        if description is None:
            continue
        rel = path.relative_to(root)
        size = len(description)
        if size > ENTRY_DESC_MAX:
            print(f"  ERROR {rel}: description is {size} chars, limit is {ENTRY_DESC_MAX} -- say what it "
                  f"does, when to use it and what it is not for, and move the procedure into the body "
                  f"or its docs page")
            errors += 1
        elif size > ENTRY_DESC_WARN:
            print(f"  WARN  {rel}: description is {size} chars, past {ENTRY_DESC_WARN} -- say what it "
                  f"does, when to use it and what it is not for, and move the procedure into the body "
                  f"or its docs page")
            warnings += 1
    return errors, warnings


def frontmatter_flag(text: str, key: str) -> bool:
    """True when the file's YAML frontmatter sets this top-level key the way Claude Code reads a
    flag: the YAML value, quotes and a trailing comment dropped, is "1", "true", "yes" or "on" in
    any case (read from the 2.1.288 binary)."""
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        return False
    for line in lines[1:]:
        if line.strip() == "---":
            return False
        if not line.startswith(key + ":"):
            continue
        value = line[len(key) + 1:].strip()
        if value[:1] in ("'", '"'):
            close = value.find(value[0], 1)
            value = value[1:close] if close > 0 else value[1:]
        else:
            value = re.split(r"\s#", value, maxsplit=1)[0]
        return value.strip().lower() in ("1", "true", "yes", "on")
    return False


def unfenced(text: str) -> str:
    """The text with every fenced block blanked: a fence is printed, never executed."""
    out, fence = [], None
    for line in text.split("\n"):
        mark = line.lstrip()[:3]
        if fence is None and mark in ("```", "~~~"):
            fence = mark
        elif fence is not None and mark == fence:
            fence = None
        elif fence is None:
            out.append(line)
    return "\n".join(out)


def check_typed_only(root: Path) -> tuple[int, int]:
    """Every command is flagged typed-only unless another file runs it through the Skill tool.

    The two directions: an unflagged command nothing calls costs the listing for nothing, and a
    flagged command or skill something calls is refused by the Skill tool when it is called.
    A command whose plugin ships a skill of the same name is exempt from both: the listing holds
    one entry for the name either way, and the Skill tool runs the skill once the command is
    flagged (both measured). A plugin is named by its manifest, as Claude Code names it.
    """
    errors = 0
    plugins = root / "plugins"
    names = {}
    for manifest in plugins.glob("*/.claude-plugin/plugin.json"):
        data = load(manifest) or {}
        names[manifest.parent.parent.name] = data.get("name") or manifest.parent.parent.name
    called: dict[tuple[str, str], Path] = {}
    for pattern in ("*/commands/*.md", "*/agents/*.md", "*/skills/**/*.md", "*/references/**/*.md"):
        for path in sorted(plugins.glob(pattern)):
            for m in SKILL_CALL.finditer(unfenced(path.read_text(encoding="utf-8"))):
                called.setdefault((m.group(1), m.group(2)), path)
    entries = [(p.parent.parent.name, p.stem, p, True) for p in sorted(plugins.glob("*/commands/*.md"))] \
        + [(p.parent.parent.parent.name, p.parent.name, p, False)
           for p in sorted(plugins.glob("*/skills/*/SKILL.md"))]
    for folder, name, path, is_command in entries:
        rel = path.relative_to(root)
        plugin = names.get(folder, folder)
        flagged = frontmatter_flag(path.read_text(encoding="utf-8"), TYPED_ONLY_KEY)
        caller = called.get((plugin, name))
        twin = is_command and (plugins / folder / "skills" / name / "SKILL.md").is_file()
        if twin:
            continue
        if flagged and caller is not None:
            print(f"  ERROR {rel}: flagged `{TYPED_ONLY_KEY}`, but {caller.relative_to(root)} runs "
                  f"{plugin}:{name} through the Skill tool, which refuses a flagged entry -- drop the flag")
            errors += 1
        elif is_command and not flagged and caller is None:
            print(f"  ERROR {rel}: no `{TYPED_ONLY_KEY}: true` -- a command the user types stays out of "
                  f"the model's skill listing; only one another file runs through the Skill tool "
                  f"(`skill: \"{plugin}:{name}\"`) is left in it")
            errors += 1
    return errors, 0


def validate_repo(root: Path) -> tuple[int, int]:
    print(f"\n=== {root}")
    errors = 0
    warnings = 0

    # Index every plugin manifest by the directory that holds the plugin, so a
    # catalog entry can be matched against the manifest it advertises.
    manifests: dict[str, tuple[Path, dict]] = {}
    for manifest_path in find_files(root, "plugin.json"):
        data = load(manifest_path)
        if data is None:
            errors += 1
            continue
        name = data.get("name")
        if not name:
            print(f"  ERROR {manifest_path}: no 'name' field")
            errors += 1
            continue
        if name in manifests:
            other_rel = manifests[name][0].relative_to(root)
            print(
                f"  ERROR {manifest_path.relative_to(root)}: plugin name "
                f"{name!r} is already declared by {other_rel} -- plugin "
                f"names must be unique across the repository"
            )
            errors += 1
            continue
        manifests[name] = (manifest_path, data)
        rel = manifest_path.relative_to(root)
        e, w = check_description(str(rel), data.get("description", ""))
        errors += e
        warnings += w

    catalogs = find_files(root, "marketplace.json")
    if not catalogs:
        print("  ERROR no marketplace.json found in this repository")
        errors += 1

    # Every catalog entry's name, across every marketplace.json in the repository --
    # a plugin advertised by ANY catalog counts. Populated below as entries are
    # walked, then checked against `manifests` once every catalog has been read.
    advertised: set[str] = set()

    for catalog_path in catalogs:
        data = load(catalog_path)
        if data is None:
            errors += 1
            continue
        rel = catalog_path.relative_to(root)
        entries = data.get("plugins", [])
        if not entries:
            print(f"  ERROR {rel}: catalog lists no plugins")
            errors += 1
            continue

        for index, entry in enumerate(entries):
            name = entry.get("name", f"<unnamed #{index}>")
            label = f"{rel} plugins[{index}] ({name})"
            advertised.add(name)

            e, w = check_description(label, entry.get("description", ""))
            errors += e
            warnings += w

            if name not in manifests:
                print(
                    f"  ERROR {label}: catalog advertises a plugin with no "
                    f"plugin.json anywhere in this repository"
                )
                errors += 1
                continue

            manifest_path, manifest = manifests[name]
            manifest_rel = manifest_path.relative_to(root)

            catalog_version = entry.get("version")
            manifest_version = manifest.get("version")
            if catalog_version != manifest_version:
                print(
                    f"  ERROR {label}: catalog says version "
                    f"{catalog_version!r} but {manifest_rel} says "
                    f"{manifest_version!r}"
                )
                errors += 1

    # The reverse of the loop above: every manifest found on disk must be named by
    # some catalog, not just every catalog entry must have a manifest. No
    # suppression mechanism -- a plugin that is deliberately unadvertised is a
    # decision to make when that plugin exists, not a standing escape hatch.
    for name, (manifest_path, manifest_data) in manifests.items():
        if name not in advertised:
            manifest_rel = manifest_path.relative_to(root)
            print(
                f"  ERROR {manifest_rel}: plugin {manifest_data.get('name')!r} "
                f"has a plugin.json but is not listed in any marketplace.json "
                f"in this repository"
            )
            errors += 1

    e, w = check_entry_descriptions(root)
    errors += e
    warnings += w

    e, w = check_typed_only(root)
    errors += e
    warnings += w

    e, w = check_instruction_sizes(root)
    errors += e
    warnings += w

    e, w = check_rules_paths(root)
    errors += e
    warnings += w

    if errors == 0 and warnings == 0:
        print("  OK")
    return errors, warnings


def _selftest() -> int:
    """Build a passing catalog, mutate it once per rule, assert what was reported."""
    import tempfile

    def build(root: Path, *, version: str = "1.0.0", catalog_version: str | None = None,
              description: str = "A fixture plugin.", ghost_manifest: bool = False,
              second_plugin_name: str | None = None,
              duplicate_at: str | None = None,
              claude_md: str | None = None, rules: dict[str, str] | None = None,
              empty_dirs: tuple[str, ...] = (), entries: dict[str, str] | None = None) -> None:
        plugin = root / "plugins" / "fixture" / ".claude-plugin"
        plugin.mkdir(parents=True)
        (plugin / "plugin.json").write_text(json.dumps(
            {"name": "fixture", "version": version, "description": description}), encoding="utf-8")
        catalog_entries = [{"name": "fixture", "source": "./plugins/fixture",
                            "version": catalog_version or version,
                            "description": description}]
        if second_plugin_name is not None:
            # A second plugin.json under a DIFFERENT directory, advertised by its own
            # catalog entry so this exercises only the duplicate-NAME assertion, not
            # the separate "unadvertised manifest" one. When its declared `name`
            # collides with the first plugin's ("fixture"), this is the red fixture
            # check 4 (the uniqueness assertion) exists to catch; when it names
            # something else, it is the paired green case proving the multi-manifest
            # code path still passes on correct content.
            second = root / "plugins" / "fixture-second" / ".claude-plugin"
            second.mkdir(parents=True)
            (second / "plugin.json").write_text(json.dumps(
                {"name": second_plugin_name, "version": "1.0.0",
                 "description": "A second fixture plugin."}), encoding="utf-8")
            catalog_entries.append(
                {"name": second_plugin_name, "source": "./plugins/fixture-second",
                 "version": "1.0.0", "description": "A second fixture plugin."})
        market = root / ".claude-plugin"
        market.mkdir(parents=True)
        (market / "marketplace.json").write_text(json.dumps({
            "name": "fixture-plugins",
            "plugins": catalog_entries,
        }), encoding="utf-8")
        if ghost_manifest:
            # A valid manifest with no catalog entry anywhere -- the state check 3
            # (the reverse-advertisement assertion) exists to catch.
            ghost = root / "plugins" / "ghost" / ".claude-plugin"
            ghost.mkdir(parents=True)
            (ghost / "plugin.json").write_text(json.dumps(
                {"name": "ghost", "version": "1.0.0", "description": "An unadvertised fixture plugin."}),
                encoding="utf-8")
        if duplicate_at is not None:
            # A verbatim second copy of the fixture plugin, planted at a caller-chosen
            # path. This is exactly what a git worktree looks like to a walk of the
            # tree: every declared name, one more time, under one extra directory.
            copy = root.joinpath(*duplicate_at.split("/")) / "plugins" / "fixture" / ".claude-plugin"
            copy.mkdir(parents=True)
            (copy / "plugin.json").write_text(json.dumps(
                {"name": "fixture", "version": version, "description": description}),
                encoding="utf-8")
        if claude_md is not None:
            (root / "CLAUDE.md").write_text(claude_md, encoding="utf-8")
        for rel in empty_dirs:
            root.joinpath(*rel.split("/")).mkdir(parents=True, exist_ok=True)
        for rel, text in (entries or {}).items():
            # A command, agent or skill file inside the fixture plugin, by its path there.
            path = root / "plugins" / "fixture" / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        for rel, text in (rules or {}).items():
            path = root / ".claude" / "rules" / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    rc = 0
    TYPED = "disable-model-invocation: true\n"

    def case(desc: str, want_ok: bool, needle: str, **kw) -> None:
        nonlocal rc
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build(root, **kw)
            import io as _io
            import contextlib
            buf = _io.StringIO()
            with contextlib.redirect_stdout(buf):
                errors, _ = validate_repo(root)
            out = buf.getvalue()
            ok = (errors == 0)
            if ok != want_ok:
                print(f"FAIL  {desc}: expected {'no errors' if want_ok else 'an error'}, "
                      f"got {errors}")
                rc = 1
            elif needle and needle not in out:
                print(f"FAIL  {desc}: the right outcome, but the report never said "
                      f"{needle!r} -- a different rule may have fired")
                rc = 1
            else:
                print(f"ok    {desc}")

    case("a consistent catalog passes", True, "OK")
    case("version drift between catalog and manifest is rejected", False,
         "but plugins/fixture/.claude-plugin/plugin.json says", catalog_version="9.9.9")
    case("an over-long description is rejected", False, "ERROR",
         description="x" * (DESCRIPTION_MAX + 1))
    case("a description past the warning threshold is reported", True, "WARN",
         description="x" * (DESCRIPTION_WARN + 1))
    case("a command description within budget passes", True, "OK",
         entries={"commands/c.md": "---\ndescription: " + "x" * ENTRY_DESC_WARN + "\n" + TYPED + "---\n"})
    case("an over-long command description is rejected", False, "plugins/fixture/commands/c.md",
         entries={"commands/c.md": "---\ndescription: " + "x" * (ENTRY_DESC_MAX + 1) + "\n" + TYPED
                                   + "---\n"})
    case("an agent description past the entry warning threshold is reported", True,
         "plugins/fixture/agents/a.md", entries={"agents/a.md": "---\nname: a\ndescription: \""
                                                 + "x" * (ENTRY_DESC_WARN + 1) + "\"\n---\n"})
    # A folded block scalar is measured as YAML reads it -- its lines joined -- not as its
    # first line: many of this repository's descriptions are written that way.
    case("a folded skill description is measured whole", True, "plugins/fixture/skills/s/SKILL.md",
         entries={"skills/s/SKILL.md": "---\nname: s\ndescription: >\n  " + "x" * 300 + "\n  "
                                       + "y" * 301 + "\nallowed-tools: Read\n---\n"})
    # A double-quoted description is measured unescaped: `\"` is one character, as YAML reads it.
    case("an escaped quote in a quoted description counts once", True, "OK",
         entries={"commands/q.md": "---\ndescription: \"" + "x" * (ENTRY_DESC_WARN - 3)
                                   + "\\\"y\\\"\"\n" + TYPED + "---\n"})

    # Typed-only commands. A command the user types carries `disable-model-invocation: true`,
    # which keeps it out of the model's skill listing; the Skill tool refuses a flagged command,
    # so one another file runs that way (`skill: "<plugin>:<name>"`) must stay unflagged.
    case("a command without disable-model-invocation is rejected", False,
         "plugins/fixture/commands/c.md: no `disable-model-invocation: true`",
         entries={"commands/c.md": "---\ndescription: d\n---\n"})
    case("a flagged command passes", True, "OK",
         entries={"commands/c.md": "---\ndescription: d\n" + TYPED + "---\n"})
    case("an unflagged command another command runs through the Skill tool passes", True, "OK",
         entries={"commands/p.md": "---\ndescription: d\n---\n",
                  "commands/c.md": "---\ndescription: d\n" + TYPED + "---\nRun it (Skill tool, "
                                   "`skill: \"fixture:p\"`).\n"})
    case("a flagged command another command runs through the Skill tool is rejected", False,
         "plugins/fixture/commands/c.md runs fixture:p through the Skill tool",
         entries={"commands/p.md": "---\ndescription: d\n" + TYPED + "---\n",
                  "commands/c.md": "---\ndescription: d\n" + TYPED + "---\nRun it (Skill tool, "
                                   "`skill: \"fixture:p\"`).\n"})
    # Claude Code reads the flag as YAML, then as any of "1", "true", "yes", "on" in any case:
    # a quoted value and a trailing comment flag the command as surely as a bare `true`.
    case("a quoted and a commented flag both count", True, "OK",
         entries={"commands/a.md": "---\ndescription: d\ndisable-model-invocation: \"true\"\n---\n",
                  "commands/b.md": "---\ndescription: d\ndisable-model-invocation: true # typed\n---\n"})
    case("a callee flagged `yes` is still flagged, and its caller is rejected", False,
         "plugins/fixture/commands/c.md runs fixture:p through the Skill tool",
         entries={"commands/p.md": "---\ndescription: d\ndisable-model-invocation: yes\n---\n",
                  "commands/c.md": "---\ndescription: d\n" + TYPED + "---\nRun it (Skill tool, "
                                   "`skill: \"fixture:p\"`).\n"})
    # A fenced block is printed, never executed (check 16's rule for loader calls), so a call
    # shown inside one keeps nothing in the listing.
    case("a call inside a fenced block is not a call", False,
         "plugins/fixture/commands/p.md: no `disable-model-invocation: true`",
         entries={"commands/p.md": "---\ndescription: d\n---\n",
                  "commands/c.md": "---\ndescription: d\n" + TYPED + "---\n```\nskill: \"fixture:p\"\n```\n"})
    # Where a command and a skill share a name, the listing holds one entry either way -- the
    # command's while it is unflagged (measured) -- so flagging it would only swap the entry.
    case("an unflagged command whose plugin ships a same-named skill passes", True, "OK",
         entries={"commands/w.md": "---\ndescription: d\n---\n",
                  "skills/w/SKILL.md": "---\nname: w\ndescription: d\n---\n"})
    # Claude Code namespaces a plugin by its manifest `name`, not its directory.
    case("a call resolves by the plugin's manifest name", True, "OK", second_plugin_name="other",
         entries={"../fixture-second/commands/p.md": "---\ndescription: d\n---\n",
                  "commands/c.md": "---\ndescription: d\n" + TYPED + "---\nRun it (Skill tool, "
                                   "`skill: \"other:p\"`).\n"})
    # A command and a skill may share a name; the Skill tool then runs the skill (measured), so
    # a flagged command whose skill twin is called is correct, and a flagged skill is not.
    case("a flagged command whose same-named skill another file runs passes", True, "OK",
         entries={"commands/w.md": "---\ndescription: d\n" + TYPED + "---\n",
                  "skills/w/SKILL.md": "---\nname: w\ndescription: d\n---\n",
                  "commands/c.md": "---\ndescription: d\n" + TYPED + "---\nRun it (Skill tool, "
                                   "`skill: \"fixture:w\"`).\n"})
    case("a flagged skill another file runs through the Skill tool is rejected", False,
         "plugins/fixture/commands/c.md runs fixture:s through the Skill tool",
         entries={"skills/s/SKILL.md": "---\nname: s\ndescription: d\n" + TYPED + "---\n",
                  "commands/c.md": "---\ndescription: d\n" + TYPED + "---\nRun it (Skill tool, "
                                   "`skill: \"fixture:s\"`).\n"})
    case("a plugin.json with no catalog entry anywhere is rejected", False,
         "is not listed in any marketplace.json", ghost_manifest=True)
    case("two plugin.json files declaring the same name are rejected", False,
         "is already declared by", second_plugin_name="fixture")
    case("two plugin.json files with distinct names both pass", True, "OK",
         second_plugin_name="fixture-second")
    # SKIP_PREFIXES' worktree exclusion, as a PAIR. Only the pair discriminates: an
    # unanchored exclusion -- a bare `worktrees` name-match at any depth, the shape the
    # SKIP_PREFIXES comment exists to keep out -- passes the green case and fails the red
    # one, while an implementation that simply stopped asserting uniqueness passes green
    # and fails red too.
    case("a worktree copy at the repo root is not walked", True, "OK",
         duplicate_at=".worktrees/wt")
    case("a duplicate under a `worktrees` directory below the root is still rejected",
         False, "is already declared by", duplicate_at="nested/worktrees/wt")

    # The instruction-file budget. Characters, not bytes: every `→` and `—` is three bytes,
    # so a byte count would fail a file that is under the budget -- the multi-byte case
    # below passes only if the gate counts characters.
    #
    # "Passes" means "does not error" (want_ok=True checks errors == 0), not "prints a bare
    # OK": CLAUDE_MD_WARN (36,000) sits below CLAUDE_MD_MAX (40,000), so any size in that
    # 4,000-character band -- including CLAUDE_MD_MAX itself -- is legitimately inside the
    # WARN zone as well as under the error cap. A size exactly at CLAUDE_MD_MAX cannot print
    # a bare "OK": it is definitionally > CLAUDE_MD_WARN. The needle below asserts the WARN
    # text that size actually produces, which is what proves the ERROR branch's `>` (not
    # `>=`) held rather than merely testing an assertion that no combination of these two
    # constants could satisfy.
    case("CLAUDE.md at the limit passes", True,
         f"WARN  CLAUDE.md is {CLAUDE_MD_MAX} characters", claude_md="x" * CLAUDE_MD_MAX)
    case("CLAUDE.md one character over the limit is rejected", False,
         f"CLAUDE.md is {CLAUDE_MD_MAX + 1} characters", claude_md="x" * (CLAUDE_MD_MAX + 1))
    case("CLAUDE.md of multi-byte characters under the limit passes", True,
         f"WARN  CLAUDE.md is {CLAUDE_MD_MAX - 1} characters", claude_md="→" * (CLAUDE_MD_MAX - 1))
    case("CLAUDE.md past the warning threshold is reported", True, "WARN  CLAUDE.md",
         claude_md="x" * (CLAUDE_MD_WARN + 1))
    case("a rules file past its threshold is reported", True, "WARN  .claude/rules/area.md",
         rules={"area.md": '---\npaths:\n  - "plugins/**"\n---\n\n' + "x" * (RULES_FILE_WARN + 1)})
    case("a repository with no CLAUDE.md passes", True, "OK")

    # check_rules_paths: paths: frontmatter and live globs. "plugins/fixture/.claude-plugin/
    # plugin.json" is the one file every fixture build() call creates, so every glob below
    # is checked against a real, always-present path three directories deep.
    case("a rules file whose glob matches a file in the fixture passes", True, "OK",
         rules={"good.md": '---\npaths:\n  - "plugins/fixture/**/*.json"\n---\n\nA rule.\n'})
    case("a rules file whose glob matches nothing is rejected", False,
         "plugins/does-not-exist/**",
         rules={"bad.md": '---\npaths:\n  - "plugins/does-not-exist/**"\n---\n\nA rule.\n'})
    case("a rules file with no frontmatter is rejected", False, "no paths:",
         rules={"noheader.md": "A rule with no frontmatter at all.\n"})
    # The three ERROR branches inside a present paths: key. Each needle is the branch's own
    # message text, so a case passes only when that branch -- not the no-frontmatter one,
    # which shares the "no paths:" prefix -- fired.
    case("a rules file whose paths: list is empty is rejected", False,
         "(the paths: list is empty)",
         rules={"empty.md": "---\npaths:\n---\n\nA rule.\n"})
    case("a paths: list item that is not a '- ' line is rejected", False,
         "unexpected line in the paths: list",
         rules={"malformed.md": '---\npaths:\n  "plugins/fixture/**/*.json"\n---\n\nA rule.\n'})
    case("a paths: list item that is empty is rejected", False,
         "an empty entry in the paths: list",
         rules={"blank.md": '---\npaths:\n  - ""\n---\n\nA rule.\n'})
    # The pair. Both globs target the same real file -- plugins/fixture/.claude-plugin/
    # plugin.json, two directories below plugins/fixture/ -- so only the `*`-vs-`**`
    # difference explains the opposite outcomes; nothing else about the fixture changed.
    case("a paths: glob using ** matches only a nested file, and passes", True, "OK",
         rules={"nested.md": '---\npaths:\n  - "plugins/fixture/**/*.json"\n---\n\nA rule.\n'})
    case("a paths: glob using a single * does not cross a directory boundary, "
         "and is rejected", False, "plugins/fixture/*.json",
         rules={"nested.md": '---\npaths:\n  - "plugins/fixture/*.json"\n---\n\nA rule.\n'})

    # A `**` glob over a directory that holds no file. Path.glob("<dir>/**") yields the
    # directory itself, so a gate that counted any path would call this glob live; Claude
    # Code loads a rules file on a *file* read, so a glob matching only directories is dead.
    case("a paths: glob matching only an empty directory is rejected", False,
         "plugins/fixture/empty/**", empty_dirs=("plugins/fixture/empty",),
         rules={"hollow.md": '---\npaths:\n  - "plugins/fixture/empty/**"\n---\n\nA rule.\n'})
    # The version-independence pair. Before Python 3.13 Path.glob("<dir>/**") yields
    # directories only, from 3.13 files as well; the gate must give one answer on both.
    # A `dir/**` over a directory holding only a nested file is live; over an empty one,
    # dead (the empty-directory case above).
    case("a paths: glob `dir/**` over a directory holding only a nested file passes", True,
         "OK", rules={"deep.md": '---\npaths:\n  - "plugins/fixture/**"\n---\n\nA rule.\n'})

    # Other top-level frontmatter keys around paths: -- a description: ahead of it and
    # another key after its list. The list ends at the next top-level key.
    case("a paths: key after another frontmatter key is found, and passes", True, "OK",
         rules={"keyed.md": '---\ndescription: an area\npaths:\n  - "plugins/fixture/**/*.json"\n'
                            'other: x\n---\n\nA rule.\n'})

    # A match under .claude/rules/ does not count. A rules file is a real file, so Path.glob
    # finds it, and a rule whose only glob names its own path counted as live -- it loads
    # only when it is itself opened, never for the work it describes. Two rules whose globs
    # name only each other are the same defect one step removed, and excluding the file
    # itself alone would pass them; the whole folder is excluded for that reason.
    case("a rules file whose only glob is its own path is rejected", False,
         "matches only files under .claude/rules/",
         rules={"selfref.md": '---\npaths:\n  - ".claude/rules/selfref.md"\n---\n\nA rule.\n'})
    case("two rules files whose globs match only each other are rejected", False,
         "a.md: paths: glob '.claude/rules/b.md' matches only files under .claude/rules/",
         rules={"a.md": '---\npaths:\n  - ".claude/rules/b.md"\n---\n\nA rule.\n',
                "b.md": '---\npaths:\n  - ".claude/rules/a.md"\n---\n\nA rule.\n'})
    # The pair. One glob, `**/*.md`, which matches the rules file itself either way; the only
    # difference is whether a real file outside the folder (CLAUDE.md) also matches. A gate
    # that rejected any glob touching the folder fails the green case; a gate that still
    # counted the rules file fails the red one.
    case("a glob matching a rules file and a file outside the folder passes", True,
         "OK", claude_md="A file outside the rules folder.\n",
         rules={"broad.md": '---\npaths:\n  - "**/*.md"\n---\n\nA rule.\n'})
    case("the same glob, with nothing outside the folder to match, is rejected", False,
         "paths: glob '**/*.md' matches only files under .claude/rules/",
         rules={"broad.md": '---\npaths:\n  - "**/*.md"\n---\n\nA rule.\n'})
    # The rules loop mirrors find_files' SKIP_PREFIXES: a glob whose only match sits inside a
    # worktree copy at the root is dead, though Path.glob finds the bytes there.
    case("a paths: glob matching only a root worktree copy is rejected", False,
         "paths: glob '.worktrees/**/*.json' matches no file",
         duplicate_at=".worktrees/wt",
         rules={"wt.md": '---\npaths:\n  - ".worktrees/**/*.json"\n---\n\nA rule.\n'})

    print("SELFTEST PASS" if rc == 0 else "SELFTEST FAIL")
    return rc


def main(argv: list[str]) -> int:
    if len(argv) > 1 and argv[1] == "--selftest":
        return _selftest()

    roots = (
        [Path(a).resolve() for a in argv[1:]]
        if len(argv) > 1
        else [Path(__file__).resolve().parent.parent]
    )

    total_errors = 0
    total_warnings = 0
    for root in roots:
        if not root.is_dir():
            print(f"ERROR {root}: not a directory")
            total_errors += 1
            continue
        errors, warnings = validate_repo(root)
        total_errors += errors
        total_warnings += warnings

    print(
        f"\n{total_errors} error(s), {total_warnings} warning(s) "
        f"across {len(roots)} repo(s)."
    )
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
