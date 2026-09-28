#!/usr/bin/env bash
# Guards the plugin's docs/ tree against the drift that splitting prose invites.
#
# Splitting one README into a multi-page tree multiplies the places drift can hide. Every
# check below exists because a specific failure was observed -- in this plugin, or
# in the two restructures this one follows (a sibling plugin repo,
# ai-containers#78).
#
# NINETEEN checks, numbered 1-19 in the order their functions appear below. The number is
# written here and nowhere else in this file, and nothing gates it -- re-derive it with
# `grep -oE '\bfail [0-9]+ ' "$0" | awk '{print $2}' | sort -un` -- the numbers a fail() call
# can actually report -- rather than trusting this sentence, and update it in the commit that
# adds a check. Counting the banner comments instead gives 18: checks 1 and 2 share one.
#
# --selftest mutates a copy of the passing fixture once per check and asserts the
# gate rejects it. Without that, the fixtures are decorative: a gate that cannot
# be shown to fail proves nothing when it passes. ai-containers' equivalent gate
# passed vacuously on its first run, examining nothing, because its file list came
# from `git ls-files` while the new pages were still untracked.
set -uo pipefail

# ---------------------------------------------------------------- edition config
# THE ONLY PART OF THIS FILE THAT DIFFERS BETWEEN EDITIONS. Never copy it across.
# Everything below is byte-identical in ai-workflows, the internal edition
# and ihudak-copilot-plugins, so a fix to the gate ports by plain `cp` of the body.
#
# THE BODY REQUIRES EVERY NAME BELOW TO EXIST. `set -u` is on, so a ported edition whose
# hand-written config block omits one ABORTS rather than skipping a check -- which is the
# property that matters, though not everywhere at the same moment. The three LIST variables
# the dispatch loop expands (PLUGIN_RELS, COST_PLUGIN_RELS, HANDOFF_PLUGIN_RELS) abort at
# that loop; CORE_PLUGIN_REL is read only inside check bodies, so it aborts at the first one
# that reads it -- check_handoff_applicability, which runs for every listed plugin. All four
# arrived with multi-plugin support and are the ones a config block copied from an older
# edition will be missing. EDITION_FORBIDDEN_B64 (check 19, below) is required the same way:
# an edition that forbids nothing defines it EMPTY, never leaves it out.
# Space-separated; the dispatch loop sets PLUGIN_REL from it per iteration, so every
# check function below is unchanged and still reads a single PLUGIN_REL. A one-element
# list behaves exactly as the old scalar did, which is what keeps this body portable to
# editions that ship one plugin.
PLUGIN_RELS="${PLUGIN_RELS:-plugins/dev-workflows plugins/guideline-reviewers plugins/workflows-core plugins/docs-workflows plugins/product-workflows}"   # copilot: dev-workflows
CMD_DIR="commands"                   # copilot: skills
CMD_SUFFIX=".md"                     # copilot: /SKILL.md
CMD_EXCLUDE=""                       # copilot: _shared
REF_DIR="references"                 # copilot: skills/_shared
REF_FLAT_EXTRA="model-routing"       # canonical: references/model-routing/*.md is a
                                     # subtree of reference FILES; copilot: "" (its
                                     # model-routing.md is a flat file in _shared)
DOC_CMD_DIR="commands"               # copilot: skills
CLI="claude"                         # copilot: copilot
CLI_VERBS="marketplace add|marketplace update|install|update"   # copilot: marketplace add|install|update
CLI_REQUIRED="marketplace add|marketplace update|update"   # copilot: marketplace add|update -- the verb
                                     # phrases getting-started.md must carry inline. A subset
                                     # of CLI_VERBS; differs per edition because Copilot
                                     # updates with `plugin update --all`, not a marketplace verb.
HAS_COST=1                           # copilot: 0 -- no cost subsystem exists there

# The command-namespace manifest session-cost.py resolves every cost boundary against,
# repo-relative. Empty means this edition ships none, and check 4's manifest assertion is
# skipped. It is NOT derived from CORE_PLUGIN_REL: the manifest sits beside the script,
# and a corpus that relocates without the script would silently stop being checked.
NS_MAP_REL="${NS_MAP_REL:-plugins/workflows-core/scripts/command-namespaces.json}"
                                     # copilot: "" -- no cost subsystem, so no manifest

# Which plugins ship the subsystems checks 8 and 11 examine. Applicability is declared,
# never inferred: absence-implies-skip would let a genuine regression in a plugin that DOES
# ship them pass silently. Membership is guarded in both directions -- the dispatch loop
# skips an undeclared plugin, and check_cost_applicability / check_handoff_applicability
# assert that a plugin holding the CALL SITES is declared. The trigger is the call sites and
# not the reference file: the corpus extraction separated the two, and a file-presence
# trigger got both directions wrong at once (see those two functions).
COST_PLUGIN_RELS="${COST_PLUGIN_RELS:-plugins/dev-workflows plugins/docs-workflows plugins/workflows-core plugins/product-workflows}"        # copilot: ""
HANDOFF_PLUGIN_RELS="${HANDOFF_PLUGIN_RELS:-plugins/product-workflows}"  # copilot: ""

# The plugin that holds the shared reference corpus. Checks 8, 9, 11 and 16 read a reference
# from HERE and their call sites from $PLUGIN_REL -- the corpus now lives in its own plugin,
# so those are different directories, and a check that resolved both halves against the
# plugin under check would report a MISSING reference for every plugin that merely reads it.
# An edition whose corpus and call sites still live together points this at that one plugin,
# which is byte-for-byte the behaviour this variable replaces.
CORE_PLUGIN_REL="${CORE_PLUGIN_REL:-plugins/workflows-core}"         # copilot: dev-workflows

# The skill a dependent plugin reads that corpus THROUGH, as it is written at a call site.
# It is edition config in its own right and NOT derived from CORE_PLUGIN_REL, deliberately:
# the corpus can be relocated (the selftest does exactly that) without the call sites being
# rewritten, and a derived name would silently stop matching them. Empty means this edition
# has no loader -- its corpus and its call sites ship in one plugin, so ${CLAUDE_PLUGIN_ROOT}
# reaches every reference by path and check 16 has nothing to assert.
LOADER_SKILL="${LOADER_SKILL:-workflows-core:reference}"             # copilot: "" -- one plugin, no loader

# RUNTIME_VARS is a SILENCER: every name in it kills both directions of check 5 (env-var doc
# agreement) for that variable, permanently -- no mutation of the fixture tree can reveal a
# missing entry, so changing this list is a deliberate, reviewed act. Each edition's host and
# hooks inject differently-named runtime variables, so this pair is edition identity, not
# shared body. Each current entry here is justified:
#   CLAUDE_PLUGIN_ROOT ARGUMENTS OSTYPE BASH_SOURCE BASH_REMATCH -- runtime/shell, not user-settable
#   ROOT       -- hook-local shell variable (hooks/changelog-owners-reminder.sh)
#   OWNER_REPO -- template placeholder in $REF_DIR/phase-handoff.md
RUNTIME_VARS="CLAUDE_PLUGIN_ROOT ARGUMENTS OSTYPE BASH_SOURCE BASH_REMATCH ROOT OWNER_REPO"
                                     # copilot: BASH_REMATCH BASH_SOURCE MODEL_ROUTING OSTYPE
                                     # OWNER_REPO PLUGIN_ROOT ROOT -- reads no ARGUMENTS; adds
                                     # MODEL_ROUTING (hook-local, hooks/preload-context.sh:52)
                                     # and PLUGIN_ROOT (host-injected plugin-root path)
# NOTE: this tripwire is self-referential -- it guards a constant in THIS file, and --selftest
# only ever mutates a copy of the fixture tree, never the script. It is therefore verified
# out-of-band (mutate a copy of this script, run it against any tree, see check 5 fail).
# Frozen (sorted) copy -- check_env_vars() asserts RUNTIME_VARS still sorts to exactly this,
# so a silent edit to the list above fails check 5 instead of passing quietly.
RUNTIME_VARS_FROZEN="ARGUMENTS BASH_REMATCH BASH_SOURCE CLAUDE_PLUGIN_ROOT OSTYPE OWNER_REPO ROOT"

# Check 19's per-edition denylist: base64 of ONE extended regex, matched case-insensitively,
# naming what THIS edition must never print anywhere in its tree outside a changelog. It is
# edition config, not body, because the three editions disagree about it by design -- the
# internal edition legitimately names the organisation it is written for, so its value is
# EMPTY and check 19 passes there without looking; this public edition names that
# organisation and its internal repositories nowhere, so its value is set. Encoded for the
# reason check 14 gives for its own list: a denylist in clear text would put the names into
# the tree, making the gate the one violation of the rule it enforces. `-` rather than `:-`
# in the default is deliberate: an explicitly EMPTY value from the environment must win, which
# is how the selftest proves the empty-config edition passes.
EDITION_FORBIDDEN_B64="${EDITION_FORBIDDEN_B64-ZHluYXRyYWNlfG1nZC1zcGVjaWZpY2F0aW9uc3xtZ2QtY2xhdWRlLXBsdWdpbnN8KF58W15bOmFsbnVtOl1fXSltZ2QoW15bOmFsbnVtOl1fXXwkKQ==}"
                                     # internal edition: "" -- it names that organisation
                                     # by design

FAILURES=0

fail() { printf 'FAIL check %s: %s\n' "$1" "$2" >&2; FAILURES=$((FAILURES + 1)); }
note() { printf '  %s\n' "$1" >&2; }

# ---------------------------------------------------------- shared: command enumeration
# A "command" is $CMD_DIR/<name>$CMD_SUFFIX. When $CMD_SUFFIX names a path (it contains a
# slash -- e.g. copilot's "/SKILL.md"), each command is a DIRECTORY holding that file, so
# enumeration walks directories and excludes $CMD_EXCLUDE (a directory that is not a
# command, e.g. copilot's "_shared"). Otherwise $CMD_SUFFIX is a flat filename suffix and
# enumeration globs files directly -- $CMD_EXCLUDE plays no role there, since a bare
# directory never matches the glob.
cmd_names() { # <plugin-dir> -> one command name per line
  local p="$1" b
  case "$CMD_SUFFIX" in
    */*) ls -d "$p/$CMD_DIR"/*/ 2>/dev/null | sed 's|/*$||; s|.*/||' | grep -vxF "${CMD_EXCLUDE:-__none__}" ;;
    *)   ls "$p/$CMD_DIR"/*"$CMD_SUFFIX" 2>/dev/null | while IFS= read -r b; do
           b="$(basename "$b")"; printf '%s\n' "${b%$CMD_SUFFIX}"
         done ;;
  esac
}
cmd_file() { printf '%s/%s/%s%s\n' "$1" "$CMD_DIR" "$2" "$CMD_SUFFIX"; } # <plugin-dir> <name> -> its file path

# ---------------------------------------------------------------- check 1 + 2
# Every relative link resolves, and every #anchor resolves to a real heading in
# whichever file it names. A bare `#anchor` names no file, so a file-existence
# check cannot see it -- that is why check 2 is separate. ai-containers' split
# broke 24 anchors this way.
# GitHub KEEPS non-ASCII letters in an anchor and lowercases them, and disambiguates a
# repeated heading as name, name-1, name-2. Neither is expressible in `tr`/`sed` without a
# UTF-8 locale -- in a C/ASCII locale those letters are deleted outright, so a CORRECT link
# fails check 2. python3 casefolds and classifies Unicode regardless of locale, and it is
# already a hard requirement of this repo's CI (scripts/validate-catalog.py runs in the same
# job), so this adds no dependency. The shell path is kept only for a bare environment with
# no python3, and it announces its own limitation instead of mis-resolving in silence.
strip_fences() { # drop fenced code blocks: an illustrative link inside a ```markdown
                 # block is not a real link, and a `#` line inside one is not a heading.
                 # check 6 has always stripped fences; checks 1 and 2 did not, which made
                 # them fail on correct content AND accept anchors that do not exist.
  awk '/^[ \t]*(```|~~~)/ { infence = !infence; next } !infence' "$1"
}

HAVE_PY=0; command -v python3 >/dev/null 2>&1 && HAVE_PY=1

slug_list() { # <markdown file> -> one GitHub anchor per heading, in document order
  if [ "$HAVE_PY" = 1 ]; then
    strip_fences "$1" | grep -E '^#{1,6} ' | sed -E 's/^#{1,6} //' | python3 -c '
import sys
seen = {}
for line in sys.stdin:
    h = line.rstrip("\n").replace("`", "").lower()
    s = "".join(c for c in h if c.isalnum() or c in " _-").replace(" ", "-")
    n = seen.get(s, 0); seen[s] = n + 1
    print(s if n == 0 else "%s-%d" % (s, n))
'
  else
    strip_fences "$1" | grep -E '^#{1,6} ' | sed -E 's/^#{1,6} //' \
      | tr '[:upper:]' '[:lower:]' \
      | sed -E 's/`//g; s/[^a-z0-9 _-]//g; s/ /-/g' \
      | awk '{ c = seen[$0]++; if (c == 0) print; else print $0 "-" c }'
  fi
}

check_links_and_anchors() {
  local root="$1" f target anchor path abs heading_file
  while IFS= read -r f; do
    while IFS= read -r link; do
      target="${link%%#*}"
      anchor="${link#*#}"
      [ "$anchor" = "$link" ] && anchor=""
      if [ -n "$target" ]; then
        path="$(dirname "$f")/$target"
        abs="$(cd "$(dirname "$path")" 2>/dev/null && pwd)/$(basename "$path")"
        if [ ! -e "$abs" ]; then
          fail 1 "$f -> $target (no such file)"
          continue
        fi
        heading_file="$abs"
      else
        heading_file="$f"
      fi
      if [ -n "$anchor" ] && [ -f "$heading_file" ]; then
        # Collect first, match second. `... | grep -qx` would exit on the first
        # match, SIGPIPE the producer, and `pipefail` would report that as a
        # failure -- turning a VALID anchor into a check-2 error. Same defect
        # ai-containers#78 caught in its own new gate.
        local slugs
        case "$heading_file" in *.md) ;; *) continue ;; esac  # only markdown has headings;
                                                             # a .sh file's `# comment` is not one
        slugs=$(slug_list "$heading_file" 2>/dev/null)
        if ! grep -qx -- "$anchor" <<<"$slugs"; then
          fail 2 "$f -> ${target:-(this file)}#$anchor (no such heading)"
        fi
      fi
    done < <(strip_fences "$f" | grep -oE '\]\([^)#][^)]*\)|\]\(#[^)]*\)' \
             | sed -E 's/^\]\(//; s/\)$//; s/[[:space:]]+"[^"]*"$//; s/^<//; s/>$//' \
             | grep -vE '^(https?|mailto):')
  done < <({ find "$root/$PLUGIN_REL/docs" -name '*.md' 2>/dev/null
             [ -f "$root/$PLUGIN_REL/README.md" ] && printf '%s\n' "$root/$PLUGIN_REL/README.md"
             [ -f "$root/README.md" ] && printf '%s\n' "$root/README.md"
             # The instruction tiers: every why-link from CLAUDE.md or a rules file lands on
             # a docs/maintainers anchor, and a renamed rationale heading must turn this red.
             for extra in "$root/CLAUDE.md" "$root"/.claude/rules/*.md "$root"/docs/maintainers/*.md; do
               [ -f "$extra" ] && printf '%s\n' "$extra"
             done; })
}

# ------------------------------------------------------------------- check 3
# No orphan pages. Reachability is transitive from docs/README.md, so a page
# linked only from another orphan is still an orphan.
check_orphans() {
  local root="$1" docs="$1/$PLUGIN_REL/docs" seen frontier next f target abs
  [ -f "$docs/README.md" ] || { fail 3 "docs/README.md is missing -- nothing to reach from"; return; }
  seen="$(cd "$docs" && pwd)/README.md"
  [ -f "$1/$PLUGIN_REL/README.md" ] && seen="$seen
$(cd "$1/$PLUGIN_REL" && pwd)/README.md"
  frontier="$seen"
  while [ -n "$frontier" ]; do
    next=""
    while IFS= read -r f; do
      [ -f "$f" ] || continue
      while IFS= read -r target; do
        abs="$(cd "$(dirname "$f")" && cd "$(dirname "$target")" 2>/dev/null && pwd)/$(basename "$target")"
        [ -f "$abs" ] || continue
        case "$seen" in *"$abs"*) continue ;; esac
        seen="$seen
$abs"
        next="$next
$abs"
      done < <(grep -oE '\]\([^)#][^):]*\.md[^)]*\)' "$f" | sed -E 's/^\]\(//; s/\)$//; s/#.*$//')
    done < <(printf '%s\n' "$frontier")
    frontier="$next"
  done
  while IFS= read -r f; do
    case "$seen" in *"$f"*) ;; *) fail 3 "orphan page (unreachable from docs/README.md): ${f#$root/}" ;; esac
  done < <(cd "$docs" && find . -name '*.md' -exec sh -c 'cd "$(dirname "$1")" && printf "%s/%s\n" "$(pwd)" "$(basename "$1")"' _ {} \;)
}

# ------------------------------------------------------------------- check 4
# Inventory agrees in BOTH directions, over reference FILES not reference
# markdown -- in the edition this was found in, the reference dir ($REF_DIR) held 98
# files of which 5 were not markdown, and one of those (cost-prices.yaml) is
# user-overridable and therefore user-facing.
# Every inventory is derived from the edition being checked, never from a number
# written into a page.
# Set once the namespace-manifest assertion below has run. It is a RUN-level assertion
# about ONE file describing EVERY plugin, dispatched from a per-plugin loop -- the same
# shape as check 8's reverse direction, and it needs the same latch. It deliberately walks
# every plugin directory in the tree rather than $PLUGIN_RELS: the manifest covers every
# plugin of the marketplace that ships commands, and a plugin with no docs/ tree of its own
# is exactly the one whose entry nothing else would ever look at.
NS_MAP_DONE=0

# The manifest session-cost.py resolves cost boundaries against equals the tree's own
# per-plugin command inventory, in both directions. It is a data file with no reader that
# would notice it going stale: a missing entry costs that plugin's invocations their
# boundary -- a deferred claim then swallows the whole segment, measured at 9000 tokens
# where 5000 was correct -- and a phantom entry mints a boundary for a command nobody can
# run. DERIVED, NEVER HAND-MAINTAINED is the property this enforces, and cmd_names is
# already the edition's own command enumeration, so the two cannot drift apart in silence.
check_namespace_map() {
  local root="$1" out h d rel n
  [ "$NS_MAP_DONE" = 0 ] || return
  NS_MAP_DONE=1
  # Latched FIRST: the note below is run-wide like the assertion it stands in for, and an
  # edition with no manifest used to print it once per listed plugin.
  [ -n "$NS_MAP_REL" ] || { note "check 4 manifest assertion not applicable: this edition ships no command-namespace manifest"; return; }
  # The reader is passed with -c and the derived inventory arrives on the PIPE. It cannot be
  # a `python3 - <<HEREDOC` the way check 16's is: a heredoc redirection wins over the pipe,
  # so the program would be read from the heredoc and the inventory would never arrive --
  # observed here as a manifest whose every namespace was reported as naming no plugin.
  local prog
  prog=$(cat <<'NSEOF'
import json, os, sys

root, rel = sys.argv[1], sys.argv[2]

# The namespace is the plugin's DECLARED name, not its directory, because the namespace is
# what a user TYPES before the colon and that is the name the host registers the plugin
# under -- which a directory is free to differ from. The basename is the fallback for a
# plugin that declares none. Both branches are exercised: plugins/fixture-unlisted declares
# a name its directory does not carry, and plugins/dev-workflows in the fixture ships no
# plugin.json at all.
#
# This does NOT mirror session-cost.py's loader, and an earlier version of this comment
# claimed it did: that loader reads a JSON map and does no directory reading of any kind.
# The <cache>/<marketplace>/<plugin>/<version>/ layout is likewise beside the point here --
# this gate only ever runs against a source tree.
derived = {}
for line in sys.stdin:
    line = line.rstrip("\n")
    if not line:
        continue
    d, name = line.split("\t", 1)
    ns = os.path.basename(d)
    try:
        with open(os.path.join(root, d, ".claude-plugin", "plugin.json"),
                  encoding="utf-8", errors="replace") as fh:
            ns = (json.load(fh) or {}).get("name") or ns
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    derived.setdefault(ns, set()).add(name)

try:
    with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
        manifest = json.load(fh)
except OSError:
    print("%s does not exist -- session-cost.py resolves every cost boundary against it" % rel)
    sys.exit(0)
except ValueError as exc:
    print("%s is not valid JSON (%s)" % (rel, exc))
    sys.exit(0)
if not isinstance(manifest, dict):
    print("%s is not a JSON object mapping a plugin namespace to its command names" % rel)
    sys.exit(0)

for ns in sorted(set(manifest) - set(derived)):
    print("%s names namespace '%s', which is no plugin in this tree that ships commands"
          % (rel, ns))
for ns in sorted(set(derived) - set(manifest)):
    print("plugin namespace '%s' ships %d command(s) and has no entry in %s -- every one "
          "of its invocations mints no cost boundary" % (ns, len(derived[ns]), rel))
for ns in sorted(set(derived) & set(manifest)):
    got = manifest[ns]
    if not isinstance(got, list) or not all(isinstance(x, str) for x in got):
        print("%s entry '%s' is not a list of command names" % (rel, ns))
        continue
    for n in sorted(set(got) - derived[ns]):
        print("%s lists '%s:%s', which is not a command of that plugin" % (rel, ns, n))
    for n in sorted(derived[ns] - set(got)):
        print("%s omits '%s:%s' -- that invocation mints no cost boundary" % (rel, ns, n))
NSEOF
)
  out=$(for d in "$root"/plugins/*/; do
          [ -d "$d" ] || continue
          rel="${d#$root/}"; rel="${rel%/}"
          while IFS= read -r n; do
            [ -n "$n" ] && printf '%s\t%s\n' "$rel" "$n"
          done < <(cmd_names "${d%/}")
        done | python3 -c "$prog" "$root" "$NS_MAP_REL")
  while IFS= read -r h; do
    [ -n "$h" ] || continue
    fail 4 "$h"
  done <<<"$out"
}

check_inventory() {
  local root="$1" p="$1/$PLUGIN_REL" d="$1/$PLUGIN_REL/docs" n

  check_namespace_map "$root"

  # commands <-> docs/$DOC_CMD_DIR/
  while IFS= read -r n; do
    [ -n "$n" ] || continue
    [ -f "$d/$DOC_CMD_DIR/$n.md" ] || fail 4 "command '$n' has no page at docs/$DOC_CMD_DIR/$n.md"
  done < <(cmd_names "$p")
  while IFS= read -r n; do
    [ -f "$(cmd_file "$p" "$n")" ] || fail 4 "docs/$DOC_CMD_DIR/$n.md names no real command"
  done < <(ls "$d/$DOC_CMD_DIR"/*.md 2>/dev/null | sed 's|.*/||; s|\.md$||')

  # agents <-> docs/reference/agents.md
  # The forward direction is ROW-anchored, not merely "the name appears somewhere". It was the
  # latter, and a review proved the gap by replacing an agent's table row with a sentence naming
  # it in prose -- the gate passed, while the inventory table the page exists to be had silently
  # lost a row. The reverse direction below has been row-anchored since it was written; a pair of
  # directions that disagree about what counts as being listed catches phantoms and misses
  # drop-outs, which is the half that actually goes wrong.
  while IFS= read -r n; do
    grep -qE "^\| \`$n\`" "$d/reference/agents.md" 2>/dev/null || fail 4 "agent '$n' has no row in reference/agents.md (a prose mention is not a row)"
  done < <(ls "$p/agents"/*.md 2>/dev/null | sed 's|.*/||; s|\.md$||')
  while IFS= read -r n; do
    [ -f "$p/agents/$n.md" ] || fail 4 "reference/agents.md names '$n', which is not an agent"
  done < <(grep -oE '^\| `[a-z-]+`' "$d/reference/agents.md" 2>/dev/null | tr -d '|` ')

  # reference FILES <-> docs/reference/references.md
  while IFS= read -r n; do
    grep -qE "^[|-] .*\`$n\`" "$d/reference/references.md" 2>/dev/null || fail 4 "reference file '$n' has no row/entry in reference/references.md (a prose mention is not one)"
  done < <({ ls "$p/$REF_DIR"/*.md 2>/dev/null; ls "$p/$REF_DIR"/*.yaml 2>/dev/null; \
             [ -n "$REF_FLAT_EXTRA" ] && ls "$p/$REF_DIR/$REF_FLAT_EXTRA"/*.md 2>/dev/null; } | sed 's|.*/||')
  while IFS= read -r n; do
    [ -f "$p/$REF_DIR/$n" ] || { [ -n "$REF_FLAT_EXTRA" ] && [ -f "$p/$REF_DIR/$REF_FLAT_EXTRA/$n" ]; } \
      || fail 4 "reference/references.md names '$n', which is not a reference file"
  done < <(grep -oE '`[A-Za-z0-9_.-]+\.(md|yaml)`' "$d/reference/references.md" 2>/dev/null | tr -d '`')

  # reference subtree counts -- *.md only: these subtrees also carry vendored
  # non-markdown data/templates that are not user-facing reference pages, so
  # counting everything would fail this check on files docs/ never claims.
  # Derived from the tree, never hardcoded: a hardcoded list cannot see a NEW subtree,
  # which is how a whole directory of reference docs would ship undocumented.
  # model-routing/ is excluded deliberately -- its *.md are inventoried file-by-file above.
  local dir count claimed
  for dir in $(ls -d "$p/$REF_DIR"/*/ 2>/dev/null | sed 's|/*$||; s|.*/||'); do
    [ -n "$REF_FLAT_EXTRA" ] && [ "$dir" = "$REF_FLAT_EXTRA" ] && continue
    count=$(find "$p/$REF_DIR/$dir" -name '*.md' | wc -l | tr -d ' ')
    claimed=$(grep -oE "\`$dir/\` \(([0-9]+)\)" "$d/reference/references.md" 2>/dev/null | grep -oE '[0-9]+' | head -1)
    [ "$claimed" = "$count" ] || fail 4 "reference/references.md says $dir/ has '${claimed:-nothing}', tree has $count"
  done
  # ...and the reverse: a subtree the page claims but the tree no longer has. Without this,
  # `rm -rf $REF_DIR/upgrade/` passes while the page still advertises `upgrade/` (3).
  while IFS= read -r dir; do
    [ -n "$dir" ] || continue
    [ -d "$p/$REF_DIR/$dir" ] || fail 4 "reference/references.md claims subtree $dir/, which does not exist"
  done < <(grep -oE '`[a-z][a-z0-9-]*/` \([0-9]+\)' "$d/reference/references.md" 2>/dev/null | sed 's|`||g; s|/.*||')

  # hooks <-> docs/reference/hooks.md
  while IFS= read -r n; do
    grep -qE "^[|-] .*\`$n\`" "$d/reference/hooks.md" 2>/dev/null || fail 4 "hook '$n' has no row/entry in reference/hooks.md (a prose mention is not one)"
  done < <(ls "$p/hooks"/*.sh 2>/dev/null | sed 's|.*/||; s|\.sh$||')
  while IFS= read -r n; do
    [ -f "$p/hooks/$n.sh" ] || fail 4 "reference/hooks.md names '$n', which is not a hook"
  done < <(grep -oE '^\| `[a-z-]+`' "$d/reference/hooks.md" 2>/dev/null | tr -d '|` ')

  # skills <-> docs/reference/references.md -- the FORWARD direction (every skills/
  # directory must be documented as a skill) is inert where $CMD_DIR IS "skills": there,
  # skills/ holds this edition's COMMANDS (already covered by the command inventory
  # above) plus $CMD_EXCLUDE (a reference directory, not a skill), so demanding each be
  # documented as a skill would be false. The REVERSE direction (a documented skill must
  # be real) stays active in every edition -- it catches a stale/phantom claim in
  # references.md regardless of what skills/ holds, and the command inventory does not
  # cover that direction.
  if [ "$CMD_DIR" = "skills" ]; then
    note "check 4 skills forward-check not applicable: skills/ is this edition's \$CMD_DIR, already covered by the command inventory above"
  else
    while IFS= read -r n; do
      grep -qE "^[|-] .*\`$n\`" "$d/reference/references.md" 2>/dev/null || fail 4 "skill '$n' has no row/entry in reference/references.md (a prose mention is not one)"
    done < <(ls -d "$p/skills"/*/ 2>/dev/null | sed 's|/*$||; s|.*/||')
  fi
  while IFS= read -r n; do
    [ -d "$p/skills/$n" ] || fail 4 "reference/references.md names skill '$n', which is not a skill"
  done < <(grep -oE '^\| `[a-z-]+`' "$d/reference/references.md" 2>/dev/null | tr -d '|` ')
}

# ------------------------------------------------------------------- check 5
# Environment variables agree in both directions. The scan covers the command
# dir ($CMD_DIR), agents/, the reference dir ($REF_DIR), hooks/, and the literal
# skills/ -- narrowing it to the first three would let a variable only a hook
# reads look documented-but-unread. The
# runtime-exclusion list is written in, so an EIGHTH user-settable variable fails
# this check rather than passing silently. That silent pass is exactly how
# GIT_USER_INITIALS and DEV_WORKFLOWS_COST_PRICES came to be missing from the
# section named after them (defect D4).
check_env_vars() {
  local root="$1" p="$1/$PLUGIN_REL" d="$1/$PLUGIN_REL/docs" v
  local now; now=$(printf '%s\n' $RUNTIME_VARS | sort | tr '\n' ' ' | sed 's/ $//')
  [ "$now" = "$RUNTIME_VARS_FROZEN" ] \
    || fail 5 "RUNTIME_VARS changed -- every entry silences check 5 for that variable; justify it in the comment above and update RUNTIME_VARS_FROZEN in the same edit"
  local read_vars documented
  # `skills` stays a literal fifth root: in editions where CMD_DIR is not "skills"
  # there is still a skills/ tree to scan, and in editions where it is, sort -u
  # dedupes. Dropping it is invisible until someone adds a $VAR only under skills/.
  read_vars=$(grep -rhoE '\$\{?[A-Z][A-Z0-9_]{2,}\}?' \
                "$p/$CMD_DIR" "$p/agents" "$p/$REF_DIR" "$p/hooks" "$p/skills" 2>/dev/null \
              | tr -d '${}' | sort -u)
  for v in $read_vars; do
    case " $RUNTIME_VARS " in *" $v "*) continue ;; esac
    grep -qw "$v" "$d/reference/environment.md" 2>/dev/null \
      || fail 5 "\$$v is read by the plugin but absent from reference/environment.md"
    grep -qw "$v" "$d/getting-started.md" 2>/dev/null \
      || fail 5 "\$$v is read by the plugin but absent from getting-started.md"
  done
  documented=$(grep -oE '^#+ `\$?[A-Z][A-Z0-9_]{2,}`|\*\*`\$?[A-Z][A-Z0-9_]{2,}`\*\*' \
                 "$d/reference/environment.md" 2>/dev/null | sed 's/^#* //' | tr -d '*`$')
  for v in $documented; do
    grep -qx -- "$v" <<<"$read_vars" \
      || fail 5 "reference/environment.md documents \$$v, which the plugin never reads"
  done
}

# ------------------------------------------------------------------- check 6
# No table cell over 200 characters. This is the readability invariant the whole
# restructure exists to establish, and the one a future edit will silently
# violate: the README this replaced carried a single cell of 2,066 characters.
check_table_cells() {
  local root="$1" files hits h
  files=$( { find "$root/$PLUGIN_REL/docs" -name '*.md' 2>/dev/null
             [ -f "$root/$PLUGIN_REL/README.md" ] && printf '%s\n' "$root/$PLUGIN_REL/README.md"
             [ -f "$root/README.md" ] && printf '%s\n' "$root/README.md"; } )
  [ -n "$files" ] || return 0
  hits=$(while IFS= read -r f; do
           [ -n "$f" ] || continue
           # LC_ALL=C + subtracting UTF-8 continuation bytes counts CHARACTERS the same way under
           # gawk and mawk. A bare length() counts bytes under mawk (Debian/Ubuntu's default awk),
           # so a 199-character cell carrying a few arrows or em dashes read as over 200.
           # Assumes well-formed UTF-8: a stray continuation byte with no lead byte is subtracted too.
           LC_ALL=C awk -v FILE="${f#$root/}" '
             /^[ \t]*(```|~~~)/ { infence = !infence; next }
             infence   { next }
             /^[[:space:]]*\|/ {
               n = split($0, cells, "|")
               last = ($0 ~ /\|[[:space:]]*$/) ? n - 1 : n   # no trailing pipe => the final field IS a cell
               for (i = 2; i <= last; i++) {
                 c = cells[i]; gsub(/^ +| +$/, "", c)
                 t = c; len = length(c) - gsub(/[\200-\277]/, "", t)
                 if (len > 200)
                   printf "%s:%d cell is %d chars (max 200)\n", FILE, NR, len
               }
             }' "$f"
         done <<<"$files")
  [ -n "$hits" ] || return 0
  while IFS= read -r h; do [ -n "$h" ] && fail 6 "$h"; done <<<"$hits"
}

# ------------------------------------------------------------------- check 7
# getting-started.md carries the install and update commands INLINE rather than
# linking out, because a getting-started page whose first step is a link has
# failed at its one job. That makes it the only page under docs/ carrying edition
# identity, so it is pinned to the repo-root README.
#
# It is a SUBSET pin, not equality: the root README documents the whole
# marketplace, while this page documents ONE plugin and should install only what
# that plugin actually needs. (dev-workflows references `prose-style` 32 times;
# `acli` zero, and `$REF_DIR/followup-emission.md` states outright that it has no
# runtime dependency on `obsidian-llm-wiki`.) So every line HERE must appear verbatim
# in the root README -- which is what catches a drifted marketplace name or command
# form -- but the root README may list more.
check_install_block() {
  local root="$1" a b extra line
  a=$(grep -oE "^$CLI plugin ($CLI_VERBS) .*" "$root/README.md" 2>/dev/null | sort -u)
  b=$(grep -oE "^$CLI plugin ($CLI_VERBS) .*" "$root/$PLUGIN_REL/docs/getting-started.md" 2>/dev/null | sort -u)
  if [ -z "$a" ]; then fail 7 "repo-root README.md has no '$CLI plugin ...' command lines to pin against"; return; fi
  if [ -z "$b" ]; then fail 7 "getting-started.md has no '$CLI plugin ...' command lines -- it must carry them inline"; return; fi

  extra=$(comm -13 <(printf '%s\n' "$a") <(printf '%s\n' "$b"))
  if [ -n "$extra" ]; then
    fail 7 "getting-started.md carries install commands the repo-root README does not"
    while IFS= read -r line; do [ -n "$line" ] && note "only in getting-started: $line"; done <<<"$extra"
  fi

  # The required verbs are the edition identity itself -- a reader who follows this
  # page must be able to perform them from it alone. CLI_REQUIRED is pipe-separated;
  # split on it without leaking the IFS change past this loop.
  local _saved_ifs="$IFS"
  IFS='|'
  for line in $CLI_REQUIRED; do
    IFS="$_saved_ifs"
    [ -n "$line" ] || continue   # guards a doubled '|' in a hand-edited CLI_REQUIRED,
                                  # which would otherwise yield one empty-string split
                                  # field and grep for a malformed pattern
    grep -q "^$CLI plugin $line " <<<"$b" \
      || fail 7 "getting-started.md is missing its '$CLI plugin $line' line"
  done
  IFS="$_saved_ifs"
  grep -q "^$CLI plugin install ${PLUGIN_REL##*/}@" <<<"$b" \
    || fail 7 "getting-started.md does not install ${PLUGIN_REL##*/} itself"
}

# ------------------------------------------------------------------- check 8
# Cost attribution agrees in BOTH directions: every command that hands emit-cost a
# fixed phase/role pair has a row in $REF_DIR/cost-emission.md section 7 carrying
# those same two values, and every section-7 row names a real command. Defect D2 --
# /update-prd emitting `phase: prd-update, role: pm` with no section-7 row -- was found
# by a one-off inline grep and defended by nothing afterwards, which is how it had
# survived since the command shipped. `/document` is the shape that defeats a naive
# grep: it calls emit-cost twice, as `/document (Jira mode)` and `/document (direct
# mode)`, against a single `/document` row.
# The two halves live in different plugins: the section-7 table in $CORE_PLUGIN_REL, the
# call sites in $PLUGIN_REL. That asymmetry is why the reverse direction is run-wide (it
# scans every plugin in COST_PLUGIN_RELS) while the forward direction and the
# extractor-coverage assertion stay per-plugin -- one table, many emitters.
# A command earns a section-7 row two ways: it calls emit-cost itself, or it CEDES
# the session and records a section-13 intent that a later run replays on its
# behalf. Both declare the same triple. A file doing NEITHER must not match --
# otherwise ordinary prose that happens to have the call site's shape satisfies
# the check, which is exactly how the two deferring commands first passed it: they
# contain no `emit-cost` at all, and their intent-record bullet matched the regex
# by coincidence. Rewording that bullet then turned the build red with a message
# blaming the section-7 table.
# Whitespace is normalised before matching: these files are hard-wrapped prose, so
# the phrase routinely straddles a newline and a line-oriented grep misses it.
cost_role_marker() { # <file> -> emit | defer | (empty)
  local flat; flat=$(tr '\n' ' ' < "$1" | tr -s ' ')
  if grep -q 'emit-cost' "$1"; then printf 'emit\n'
  elif printf '%s' "$flat" | grep -q '13.1 intent record'; then printf 'defer\n'
  fi
}
emit_cost_calls() { # <plugin-dir>  ->  lines of  <command>|<phase>|<role>
  local p="$1" f n
  while IFS= read -r n; do
    [ -n "$n" ] || continue
    f=$(cmd_file "$p" "$n")
    [ -f "$f" ] || continue
    [ -n "$(cost_role_marker "$f")" ] || continue
    tr '\n' ' ' < "$f" | tr -s ' ' \
      | grep -oE '`command: /[a-z-]+( \([A-Za-z]+ mode\))?`, `phase: [a-z-]+`, `role: [a-z]+`' \
      | sed -E 's/`command: //; s/ \([A-Za-z]+ mode\)//; s/`, `phase: /|/; s/`, `role: /|/; s/`$//'
  done < <(cmd_names "$p") | sort -u
}

# Set once the run-wide reverse direction below has executed. It is a RUN-level assertion
# about one table, dispatched from a per-plugin loop, so it needs a latch rather than a
# per-plugin repetition. Set only where the loop actually runs, so an early return (no
# table, no call site) leaves it for the next listed plugin instead of swallowing it.
COST_REVERSE_DONE=0

check_cost_attribution() {
  [ "$HAS_COST" = 1 ] || { note "check 8 not applicable: this edition has no cost subsystem"; return; }
  # The TABLE comes from $CORE_PLUGIN_REL and the CALL SITES from $PLUGIN_REL: after the
  # reference corpus is extracted into its own plugin those are different directories, and
  # every plugin that emits reads the one table. While they are the same directory this
  # resolves exactly as it did before.
  local root="$1" p="$1/$PLUGIN_REL" table calls all_calls line cmd phase role want q
  table=$(sed -n '/^## 7\./,/^## 8\./p' "$1/$CORE_PLUGIN_REL/$REF_DIR/cost-emission.md" 2>/dev/null \
          | grep -oE '^\| `/[a-z-]+` \| [^|]+ \| [^|]+ \|' \
          | sed -E 's/^\| `//; s/` \| /|/; s/ \| /|/; s/ *\|$//; s/\*//g; s/ *\| */|/g')
  [ -n "$table" ] || { fail 8 "$CORE_PLUGIN_REL/$REF_DIR/cost-emission.md has no section-7 attribution table"; return; }
  calls=$(emit_cost_calls "$p")
  [ -n "$calls" ] || { fail 8 "no emit-cost call site found in $PLUGIN_REL/$CMD_DIR/ -- the extractor has stopped matching"; return; }

  while IFS='|' read -r cmd phase role; do
    [ -n "$cmd" ] || continue
    want=$(grep -F "$cmd|" <<<"$table" | head -1)
    if [ -z "$want" ]; then
      fail 8 "$cmd emits phase/role '$phase'/'$role' but has no row in cost-emission.md section 7"
    elif [ "$want" != "$cmd|$phase|$role" ]; then
      fail 8 "$cmd emits '$phase'/'$role'; cost-emission.md section 7 says '${want#*|}'"
    fi
  done <<<"$calls"

  # REVERSE direction, and it is RUN-WIDE, not per-plugin. One table attributes the emitting
  # commands of every plugin in COST_PLUGIN_RELS, so a row is unattributed only when NO
  # listed plugin emits it. Matching a row against the call sites of the single plugin under
  # check would fire on every row belonging to a sibling -- the whole table, twice over, the
  # moment the emitting commands are spread across two plugins. Runs once per invocation
  # (the first listed plugin that gets this far), because a duplicated identical FAIL line
  # reads as two defects.
  if [ "$COST_REVERSE_DONE" = 0 ]; then
    COST_REVERSE_DONE=1
    all_calls=$(for q in $COST_PLUGIN_RELS; do emit_cost_calls "$1/$q"; done | sort -u)
    while IFS='|' read -r cmd phase role; do
      [ -n "$cmd" ] || continue
      grep -qF "$cmd|" <<<"$all_calls" \
        || fail 8 "cost-emission.md section 7 attributes $cmd, which neither passes emit-cost a phase/role pair nor records a section-13 intent in any of COST_PLUGIN_RELS ($COST_PLUGIN_RELS)"
    done <<<"$table"
  fi

  # Extractor-coverage assertion. Every command file that calls emit-cost OR records a
  # section-13 intent must yield a triple; otherwise a reworded call site makes this check
  # go QUIET, and the message above would blame the table for what is really an extractor
  # miss. `/document` is the live example -- it calls emit-cost twice under parenthesised
  # names.
  local f n cn
  while IFS= read -r cn; do
    [ -n "$cn" ] || continue
    f=$(cmd_file "$p" "$cn")
    [ -f "$f" ] || continue
    [ -n "$(cost_role_marker "$f")" ] || continue
    n="/$cn"
    grep -qF "$n|" <<<"$calls" \
      || fail 8 "$CMD_DIR/$cn$CMD_SUFFIX calls emit-cost (or records a section-13 intent) but no phase/role triple matched -- the EXTRACTOR has drifted, not the table; fix the regex, never the row"
  done < <(cmd_names "$p")
}

# COST_PLUGIN_RELS is a declared list, not an inferred one -- but a declaration only guards
# the LOUD direction (a plugin wrongly listed runs check 8 against a subsystem it has
# nothing to attribute). The QUIET direction was unguarded: a plugin that emits but is
# missing from the list has check 8 silently skipped for it -- deleting every row from the
# section-7 table left the whole tree green. This asserts the other half.
#
# THE TRIGGER IS THE CALL SITES, NOT THE REFERENCE FILE, and that is a correction. It used
# to fire on a plugin shipping $REF_DIR/cost-emission.md, on the premise that shipping the
# reference implies shipping the emitters. Extracting the corpus falsified that premise in
# both directions at once: the plugin that kept twenty emitting commands stopped shipping
# the reference, so its assertion went SILENT -- drop it from COST_PLUGIN_RELS afterwards
# and nothing catches it -- while the corpus plugin was forced into the list by a file it
# merely holds. What check 8 is about is the emitters, so that is what this asks for.
# `cost_role_marker` is the same predicate check 8 itself uses for "this command owes a
# section-7 row": an emit-cost call, or a section-13 intent a later run replays.
check_cost_applicability() {
  local root="$1" p="$1/$PLUGIN_REL" cn f n=0
  [ "$HAS_COST" = 1 ] || return
  while IFS= read -r cn; do
    [ -n "$cn" ] || continue
    f=$(cmd_file "$p" "$cn"); [ -f "$f" ] || continue
    [ -n "$(cost_role_marker "$f")" ] && n=$((n + 1))
  done < <(cmd_names "$p")
  [ "$n" -gt 0 ] || return
  case " $COST_PLUGIN_RELS " in
    *" $PLUGIN_REL "*) : ;;
    *) fail 8 "$PLUGIN_REL ships $n command(s) that call emit-cost or record a section-13 intent but is not a member of COST_PLUGIN_RELS -- check 8 never runs for it" ;;
  esac
}

# ------------------------------------------------------------------- check 9
# Prose counts. check 4 gates the INVENTORIES in both directions, but not the sentences
# that state their size. A 22nd command with a page and an index link passes check 4 while
# `$PLUGIN_REL/README.md` still says "twenty-one slash commands" -- and a reader
# meets the sentence before the table. Same for the agent, reference-file, hook, skill and
# environment-variable totals.
_word2num() {
  case "$1" in
    one) echo 1 ;; two) echo 2 ;; three) echo 3 ;; four) echo 4 ;; five) echo 5 ;;
    six) echo 6 ;; seven) echo 7 ;; eight) echo 8 ;; nine) echo 9 ;; ten) echo 10 ;;
    eleven) echo 11 ;; twelve) echo 12 ;; thirteen) echo 13 ;; fourteen) echo 14 ;;
    fifteen) echo 15 ;; sixteen) echo 16 ;; seventeen) echo 17 ;; eighteen) echo 18 ;;
    nineteen) echo 19 ;;
    twenty-one) echo 21 ;; twenty-two) echo 22 ;; twenty-three) echo 23 ;; twenty-four) echo 24 ;;
    twenty-five) echo 25 ;; twenty-six) echo 26 ;; twenty-seven) echo 27 ;;
    twenty-eight) echo 28 ;;
    thirty-four) echo 34 ;; ninety-eight) echo 98 ;;
    *) echo "$1" ;;
  esac
}

check_prose_counts() {
  local root="$1" p="$1/$PLUGIN_REL" d="$1/$PLUGIN_REL/docs"
  local raw claimed actual label file pat

  _one() { # <label> <file> <extended-regex whose match STARTS with the numeral> <actual>
    label="$1"; file="$2"; pat="$3"; actual="$4"
    [ -f "$file" ] || return 0
    # -i, and lowercase the captured numeral: a count sentence may open a sentence
    # ("Thirteen commands emit ...") or sit mid-sentence ("twenty-one slash commands").
    #
    # `head -1` TAKES THE FIRST MATCH IN DOCUMENT ORDER, NOT "THE COUNT SENTENCE" --
    # so the count sentence must be the FIRST phrase of its shape in its file, and a
    # prose line above it that happens to read "<number> agents" is silently gated in
    # its place. That is not hypothetical: a section lead reading "The three agents
    # that turn ..." made this compare 3 against a tree of 11, and the wording before
    # it ("The two agents that ...") had been green only by accident, sorting after
    # the introduction's own "ten agents".
    #
    # Failing on a SECOND match was measured and refused, on this repo's usual rule:
    # on a green tree eight gated files already carry more than one matching phrase
    # (every plugin's references.md among them, up to five in one file), so the check
    # would fire on eight correct files and nothing else. Fires-only-on-correct-content
    # is the same result that refused two earlier widenings here.
    #
    # It is therefore an AUTHORING rule, recorded where an author meets it: when you
    # add prose above a count sentence, do not let it name a number and that sentence's
    # noun. Re-run this check after any edit to the top of one of these pages -- a
    # silently wrong comparison passes, which is what makes it worth the paragraph.
    raw=$(grep -ohEi "$pat" "$file" 2>/dev/null | head -1 | awk '{print tolower($1)}')
    if [ -z "$raw" ]; then
      fail 9 "$label: no count sentence found in ${file#$root/} -- the wording drifted, so nothing is being checked"
      return 0
    fi
    claimed=$(_word2num "$raw")
    [ "$claimed" = "$actual" ] \
      || fail 9 "$label: ${file#$root/} says $raw ($claimed), tree has $actual"
  }

  # Left-anchored, on EVERY alternation below without exception: without a boundary, an
  # unenumerated compound like "twenty-five" would let the bare alternative "five" match its own
  # tail and silently compare the wrong numeral instead of failing loudly. The argument does not
  # depend on which count a sentence carries, so neither does the anchor -- an assertion left
  # unanchored is the one an unenumerated compound slips past, and it passes on a coincidentally
  # correct numeral rather than failing. (^|[^[:alnum:]_-]) keeps the match from starting mid-word
  # or mid-compound; a captured boundary character is whitespace in every real sentence, so it
  # disappears when `awk '{print $1}'` splits the extracted match.
  _one "commands"        "$p/README.md"                  '(^|[^[:alnum:]_-])(one|two|three|four|five|six|seven|eight|nine|ten|fifteen|sixteen|seventeen|eighteen|nineteen|twenty-one|twenty-two|twenty-three|twenty-four|twenty-five|twenty-six|twenty-seven|twenty-eight|thirty-four|ninety-eight|[0-9]+) slash commands'    "$(cmd_names "$p" | wc -l | tr -d ' ')"
  # "eleven" is in the agents alternation and in NO sibling below, and that asymmetry was
  # measured before it was taken rather than tidied into uniformity. docs-workflows crossed ten
  # agents and writes that count as a WORD ("eleven agents"), which is the whole reason this
  # word is here: before it, the sentence matched no alternative and check 9 reported the count
  # as ABSENT -- a drifted wording -- instead of comparing 11 against 11. Measured at the same
  # time, per gated plugin, sentence form against tree count: the `commands` sentence is a word
  # only in workflows-core (six), docs-workflows (Six) and guideline-reviewers (two), none of
  # them near ten, while dev-workflows and product-workflows write a numeral; every `files`
  # sentence in every gated plugin is a NUMERAL (15 / 38 / 29 / 23 / 12), matched by [0-9]+, so
  # no word could help it; `hooks` tops out at two, `bundled skills` at two, `user-settable` at
  # five; and the cost-emitting alternation already carries eleven through nineteen. So no
  # sibling has a sentence this word could match today, and adding it to them would be "while I
  # am here" rather than a measurement. Add it to one when a plugin's own count sentence crosses
  # ten IN WORDS, and add the fixture-growing selftest case with it -- an expect_fail case proves
  # only that some word was rejected, never that this one converts.
  _one "agents"          "$d/reference/agents.md"        '(^|[^[:alnum:]_-])(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twenty-one|thirty-four|ninety-eight|[0-9]+) agents'           "$(ls "$p/agents"/*.md 2>/dev/null | wc -l | tr -d ' ')"
  _one "reference files" "$d/reference/references.md"    '(^|[^[:alnum:]_-])(one|two|three|four|five|six|seven|eight|nine|ten|twenty-one|thirty-four|ninety-eight|[0-9]+) files'           "$(find "$p/$REF_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')"
  _one "hooks"           "$d/reference/hooks.md"         '(^|[^[:alnum:]_-])(one|two|three|four|five|six|seven|eight|nine|ten|twenty-one|thirty-four|ninety-eight|[0-9]+) hooks?'                   "$(ls "$p/hooks"/*.sh 2>/dev/null | wc -l | tr -d ' ')"
  # Inert where $CMD_DIR IS "skills" (see check 4's skills forward-check, same reason):
  # ls -d "$p/skills"/*/ would count this edition's commands plus $CMD_EXCLUDE, not
  # bundled skills -- there is no separate "N bundled skills" sentence to state there.
  if [ "$CMD_DIR" = "skills" ]; then
    note "check 9 skills-count assertion not applicable: skills/ is this edition's \$CMD_DIR, already counted by the commands assertion above"
  else
    _one "skills"          "$d/README.md"                  '(^|[^[:alnum:]_-])(one|two|three|four|five|six|seven|eight|nine|ten|twenty-one|thirty-four|ninety-eight|[0-9]+) bundled skills'           "$(ls -d "$p/skills"/*/ 2>/dev/null | wc -l | tr -d ' ')"
  fi

  # The user-settable total is derived the same way check 5 derives its scan, so the two
  # can never disagree about what "user-settable" means.
  local read_vars n_settable v
  read_vars=$(grep -rhoE '\$\{?[A-Z][A-Z0-9_]{2,}\}?' \
                "$p/$CMD_DIR" "$p/agents" "$p/$REF_DIR" "$p/hooks" "$p/skills" 2>/dev/null \
              | tr -d '${}' | sort -u)
  n_settable=0
  for v in $read_vars; do
    case " $RUNTIME_VARS " in *" $v "*) continue ;; esac
    n_settable=$((n_settable + 1))
  done
  _one "environment variables" "$d/reference/environment.md" '(^|[^[:alnum:]_-])(one|two|three|four|five|six|seven|eight|nine|ten|twenty-one|thirty-four|ninety-eight|[0-9]+) user-settable' "$n_settable"

  # The size of the cost-emitting set is prose too, and it is the count that went stale the
  # moment /prompt and /feedback started emitting. Derived from the same extractor check 8 uses,
  # and -- deliberately -- from NOTHING else: the sentence names the emitting commands of the
  # plugin that ships the page, so both halves stay inside $PLUGIN_REL even after
  # $REF_DIR/cost-emission.md has moved to $CORE_PLUGIN_REL. Tying this assertion to the
  # presence of that reference would be applicability inferred from a missing file, and it
  # would go silent for every emitting plugin that is not the corpus.
  #
  # The one thing it IS gated on is the page: session-cost.md is documentation of the
  # subsystem written from the invoking side, and a plugin may emit without shipping its own
  # copy. Absent page => this ONE count is skipped, out loud, and the other six still run.
  if [ "$HAS_COST" != 1 ]; then
    note "check 9 cost-emitting-commands assertion not applicable: this edition has no cost subsystem"
  elif [ ! -f "$d/reference/session-cost.md" ]; then
    note "check 9 cost-emitting-commands assertion not applicable: $PLUGIN_REL ships no docs/reference/session-cost.md"
  else
    local n_emit
    n_emit=$(emit_cost_calls "$p" | cut -d'|' -f1 | sort -u | grep -c . || true)
    _one "cost-emitting commands" "$d/reference/session-cost.md" \
         '(^|[^[:alnum:]_-])(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty-one|twenty-two|twenty-three|twenty-four|twenty-five|twenty-six|twenty-seven|thirty-four|ninety-eight|[0-9]+) commands emit a cost entry' "$n_emit"
  fi
}

# ------------------------------------------------------------------ check 10
# Identity quarantine. No page under $PLUGIN_REL/docs/ may name the marketplace this
# plugin ships from, or the repository that contains it. getting-started.md is the single
# sanctioned exception: it is the one page whose job is to say where the plugin comes
# from, which is why check 7 pins its install block to the repo-root README verbatim.
#
# The binding reason is FORKS. A marketplace name or container-repo URL written into a
# page is wrong in anyone's fork -- the fork ships from a different marketplace, and its
# pages would keep sending readers to the upstream it was forked from. Two per-command
# pages linked a sibling plugin by full container URL and survived several releases;
# nothing in the build could see them, because check 7 pins getting-started.md alone.
#
# The tokens are DERIVED from the repo-root README's own install block -- the same lines
# check 7 already extracts -- and are never written in here. A fork renames its
# marketplace and its container repo in that block, and this check follows without an
# edit. Deriving NOTHING is a failure, not a pass: a token set that came up empty would
# make this check examine nothing and pass every tree.
#
# What it deliberately does NOT cover: any OTHER repository a page might name -- the
# container-image / dev-environment repo the repo-root README recommends, a sibling
# project, a third-party plugin. Nothing in the tree marks which third-party slug is
# "an environment", so a check that guessed would be guessing. It also leaves the
# repo-root README and $PLUGIN_REL/README.md alone: neither is a page under docs/, and
# the root README is where this identity is supposed to be stated.
check_identity_quarantine() {
  local root="$1" d="$1/$PLUGIN_REL/docs" tokens t f hit pat
  # `sed 'p; s|.*/||'` emits the slug AND its bare repo name: a page can name either.
  tokens=$( { grep -oE "^$CLI plugin marketplace add [^[:space:]]+" "$root/README.md" 2>/dev/null \
                | sed -E "s|^$CLI plugin marketplace add ||; s|/+$||" | sed 'p; s|.*/||'
              grep -oE "^$CLI plugin install [^[:space:]]+@[^[:space:]]+" "$root/README.md" 2>/dev/null \
                | sed -E 's/.*@//'
              grep -oE "^$CLI plugin marketplace update [^[:space:]]+" "$root/README.md" 2>/dev/null \
                | sed -E "s|^$CLI plugin marketplace update ||"; } \
            | grep -vE '^[[:space:]]*$' | sort -u)
  if [ -z "$tokens" ]; then
    fail 10 "no marketplace or container-repo token could be derived from the repo-root README's '$CLI plugin ...' lines -- this check would examine nothing"
    return
  fi
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    [ "$f" = "$d/getting-started.md" ] && continue   # the single sanctioned exception
    while IFS= read -r t; do
      [ -n "$t" ] || continue
      # Word-boundary match, NOT substring. A fork is free to pick a short marketplace name --
      # `workflows` is a plausible one -- and an unanchored grep then reports every page that
      # says `dev-workflows`. That was measured: renaming this marketplace to `workflows`
      # produced 38 check-10 failures on unmodified, correct pages. A gate that fires 38 times
      # on correct content in a fork is a gate that fork deletes in its first week, and forks
      # are this check's entire rationale.
      #
      # The boundary class is [A-Za-z0-9_-]: a hyphen HAS to be in it (that is what separates
      # `workflows` from `dev-workflows`), and `@`, `/` and `.` have to be OUT of it -- the
      # marketplace is named as `<plugin>@<marketplace>` and the container repo as
      # `github.com/<owner>/<repo>/tree/...`, so a boundary class containing them would miss
      # the two forms this check exists to catch.
      pat=$(printf '%s' "$t" | sed 's/[][\\.^$*+?(){}|]/\\&/g')
      hit=$(grep -nE "(^|[^A-Za-z0-9_-])$pat([^A-Za-z0-9_-]|$)" "$f" 2>/dev/null | head -1)
      [ -n "$hit" ] && fail 10 "${f#$root/}:${hit%%:*} names '$t' -- no page under $PLUGIN_REL/docs/ may name the marketplace this plugin ships from or the repository that contains it (getting-started.md is the only exception); a fork of this repo inherits the wrong one"
    done <<<"$tokens"
  done < <(find "$d" -name '*.md' 2>/dev/null | sort)
}

# ------------------------------------------------------------------ check 11
# The family globs, read out of ONE line: next-phase-offer.md's scope paragraph, the single
# unwrapped line beginning `**Where this rule applies:`. Both readers below call this, so the
# two can never disagree about which commands the rule binds.
#
# WHY NOT `head -1` OVER THE WHOLE FILE, which is what this was. That was a proxy, and it held
# only while the scope paragraph happened to be the first `<plugin>:<family>*` phrase in the
# file. The repo's instructions (now .claude/rules/gates.md, § Check 11) have always said the
# family comes from the scope paragraph; the proxy agreed with it by accident of line order. The
# file also carries a `## Not pipeline nodes` list -- commands that print NO offer -- and the
# moment a phrase there qualifies for the plugin under check, the proxy hands that plugin a
# family the rule never bound: check_handoff_applicability forces it into HANDOFF_PLUGIN_RELS,
# check_merge_clause then finds no offer of it anywhere, and NEITHER branch is green. Anchoring
# is behaviour-preserving on a file whose scope paragraph does come first, and it is strictly
# stronger in the direction .claude/rules/gates.md asks for: a reworded scope sentence now
# empties the glob and turns the build red, where before any stray phrase elsewhere in the file
# would silently stand in for it.
#
# WHY NOT `head -1` ON THE ANCHORED LINE EITHER, which is what this became next. That held only
# while the scope paragraph named exactly one glob per plugin, and it stopped holding the moment
# one plugin's own line named two: `/prd-ground` left the `/product-workflows:brd-*` family it
# used to belong to -- correctly, per the design's own rule that `brd-` names the BRD route and
# this command now serves two -- but it still prints an offer this gate must cover, so the scope
# paragraph names it under a SECOND glob, `/product-workflows:prd-*`, on the very same line.
# Taking only the first of the two silently drops every offer the second names: `route_n` still
# comes out above zero from the first glob alone, so the vacuity guard stays quiet and the build
# stays green while a whole command's coverage lapses -- exactly the failure mode this check's
# own header comment already named as `head -1`'s risk, one level up. `scope_family` now returns
# every glob on the line, one per line, and both callers accumulate `route_n` / `req_n` across
# all of them -- so a plugin whose scope line names two families is covered by both, and one
# whose line names none still fails loudly.
#
# The two empty-glob dispositions stay exactly as they are -- `fail 11` in check_merge_clause,
# an early `return` in check_handoff_applicability -- and "empty" now means the function
# returned no line at all, never that its first line was empty. The quiet one is safe only
# because the loud one exists.
scope_family() { # <next-phase-offer.md> <qualifier>  -> one family glob per line, or empty
  grep '^\*\*Where this rule applies:' "$1" 2>/dev/null \
    | grep -oE "$2[a-z][a-z0-9-]*\*" | sed "s|^$2||" | sort -u
}

# Merge-clause adoption. An offer that names a downstream command whose Phase 0 gate
# targets an artifact THIS run writes must carry the `<merge-clause>` placeholder, because
# that command stops while this phase's pull request is open. The placeholder and its
# resolution table live in $CORE_PLUGIN_REL/$REF_DIR/next-phase-offer.md, which binds the rule
# to EVERY offer the dependent plugin family prints -- not to the corpus plugin that ships the
# rule, whose own single offer deliberately carries no clause; the family glob below is this
# GATE's scope, not the rule's, and that same file records why it is not widened. This check
# only enforces adoption.
#
# The failure it exists for is PARTIAL adoption, which is worse than none: a reference
# claiming family-wide ownership while seven offers still carried a hardcoded clause, or
# no clause, each naming a command whose gate the offering run itself feeds. That set was
# found once, by enumerating every option by hand. Nothing re-enumerated it afterwards.
#
# Three relations, every one DERIVED, none written in here:
#   family  -- the `<plugin>:<family>*` glob next-phase-offer.md names, which is this gate's
#              scope. Only offers made BY a command of that family are checked. Widening it
#              was measured, not assumed, and re-measured since: with the filter removed the
#              check fires on THREE sites -- a command that runs no handoff at all, and two
#              mid-run refusals -- every one correct content, and catches NONE of the six
#              offers outside the family that carried an unconditional clause or no clause
#              at all. The fourth site the earlier measurement named (a report sentence
#              trailing an array on one line of idea.md) is gone with the branch it sat in,
#              so widening now yields less and still catches nothing -- including the /idea
#              offer that was the sixth defect, which is prose and invisible to any
#              `choices:` scanner. A `choices:` array here is a refusal or a branch point as
#              often as it is an offer, and nothing marks which. Do not widen without new
#              evidence; next-phase-offer.md holds the full record and the numbers.
#   targets -- what each command runs `require-on-main` against, read out of
#              phase-handoff.md's row-F table (column 2's backticked *.md, by basename).
#   writers -- what a command declares it hands off, read out of its own
#              `deliverable_paths` = ... `title:` span (same basename form).
# An offer is REQUIRED to carry the clause when writers(offerer) and targets(offered)
# intersect. It is never required to DROP one: an offer may carry the clause for a reason
# this check cannot see, and a check that forbade that would be asserting more than it knows.
#
# What it deliberately does NOT catch. It reads the option's TEXT for the placeholder, not
# the clause the run resolves it to -- whether the resolution table is applied correctly at
# runtime is not in the file. It cannot see an offer outside a `choices:` array (a prose
# `### Next step` line is not checked). And its writer relation is the paths the command
# DECLARES; a file a run writes but never declares is invisible to it, which under-fires
# rather than over-fires. That last one limits WHICH paths are seen; it is not a licence for a
# whole command to drop out. Any relation coming up empty is a FAILURE -- per family command
# for `writers`, run-wide for the family glob and the target table -- so a reworded handoff
# turns the build red instead of quietly narrowing this check's surface.
#
# WHERE EACH HALF IS READ FROM. Both references -- next-phase-offer.md (the family and the
# placeholder) and phase-handoff.md (the row-F target table) -- come from $CORE_PLUGIN_REL;
# the commands, their offers and their `deliverable_paths` come from $PLUGIN_REL. Once the
# corpus is extracted those are different plugins, and the rule still binds the offers of the
# plugin that prints them. None of the three relations becomes optional as a result: an
# absent reference is still a FAILURE, not a skip, exactly as an emptied one is.
check_merge_clause() {
  local root="$1" p="$1/$PLUGIN_REL" core="$1/$CORE_PLUGIN_REL"
  local ref="$core/$REF_DIR/next-phase-offer.md" ph="$core/$REF_DIR/phase-handoff.md"
  local qual="/${PLUGIN_REL##*/}:" globs glob targets writers offers route_n=0 req_n=0
  local y f x ln has t need needt

  [ -f "$ref" ] || { fail 11 "$CORE_PLUGIN_REL/$REF_DIR/next-phase-offer.md is missing -- it owns the <merge-clause> placeholder, its resolution table, and the command family the rule binds"; return; }
  [ -f "$ph" ]  || { fail 11 "$CORE_PLUGIN_REL/$REF_DIR/phase-handoff.md is missing -- its row-F table is where each command's require-on-main target is declared"; return; }

  globs=$(scope_family "$ref" "$qual")
  [ -n "$globs" ] || { fail 11 "$CORE_PLUGIN_REL/$REF_DIR/next-phase-offer.md no longer names the command family the <merge-clause> rule binds -- the family is read ONLY from the scope-paragraph line, the single line beginning \`**Where this rule applies:\`, and that line carries no \`$qual<family>*\` phrase. A phrase of that shape elsewhere in the file does NOT count and will not silence this; with no family, the check would examine no offer at all"; return; }

  # targets: one `<command>|<artifact-basename>` line per row-F table cell. Column 2 only --
  # column 3 routinely cites reference FILES that are not gate targets.
  targets=$(awk -F'|' '
    /^\| `?\/[a-z]/ {
      c1 = $2; c2 = $3; n = 0
      while (match(c2, /`[^`]*\.md`/)) {
        t = substr(c2, RSTART + 1, RLENGTH - 2); sub(/.*\//, "", t); tg[++n] = t
        c2 = substr(c2, RSTART + RLENGTH)
      }
      if (n == 0) next
      while (match(c1, /\/[a-z][a-z0-9-]*/)) {
        cmd = substr(c1, RSTART + 1, RLENGTH - 1); c1 = substr(c1, RSTART + RLENGTH)
        for (i = 1; i <= n; i++) print cmd "|" tg[i]
      }
    }' "$ph" | sort -u)
  [ -n "$targets" ] || { fail 11 "$CORE_PLUGIN_REL/$REF_DIR/phase-handoff.md's row-F table yielded no require-on-main target -- the EXTRACTOR has drifted, not the table; fix the parser, never the rows"; return; }

  # Outer loop over every glob the scope paragraph names (usually one; two where a command like
  # /prd-ground serves two families at once). route_n and req_n accumulate across all of them,
  # so the vacuity guards below see the family's TOTAL coverage, never just one glob's.
  while IFS= read -r glob; do
    [ -n "$glob" ] || continue
    while IFS= read -r y; do
      [ -n "$y" ] || continue
      case "$y" in $glob) ;; *) continue ;; esac
      f=$(cmd_file "$p" "$y"); [ -f "$f" ] || continue
      route_n=$((route_n + 1))

      # offers: one `<line>|<offered-command>|<0|1 carries the placeholder>` per option.
      offers=$(awk -v Y="$y" -v Q="$qual" '
        index($0, "choices: [") {
          body = substr($0, index($0, "choices: [") + 9)
          while (match(body, /"[^"]*"/)) {
            opt = substr(body, RSTART + 1, RLENGTH - 2); body = substr(body, RSTART + RLENGTH)
            tmp = opt
            while ((i = index(tmp, Q)) > 0) {
              rest = substr(tmp, i + length(Q))
              match(rest, /^[a-z][a-z0-9-]*/)
              x = substr(rest, 1, RLENGTH); tmp = substr(rest, RLENGTH + 1)
              if (x != Y) print FNR "|" x "|" (index(opt, "<merge-clause>") ? "1" : "0")
            }
          }
        }' "$f" | sort -u)
      # A family command that makes no offer has no surface for this check to cover, so it needs
      # no writer set and is not asserted about.
      [ -n "$offers" ] || continue

      # writers: the backticked *.md paths inside this command's `deliverable_paths` = ...
      # `title:` span. The `=` is required: the same word appears in prose that lists nothing.
      writers=$(awk '
        /`deliverable_paths`[[:space:]]*=/ { span = 1; k = 0 }
        span {
          line = $0
          while (match(line, /`[^`]*\.md`/)) {
            t = substr(line, RSTART + 1, RLENGTH - 2); sub(/.*\//, "", t); print t
            line = substr(line, RSTART + RLENGTH)
          }
          if ($0 ~ /`title:/ || ++k > 20) span = 0
        }' "$f" | sort -u)
      # PER-COMMAND coverage assertion, and it has to be per command. Rewording one command's
      # `deliverable_paths` = to `deliverable_paths` lists empties ITS writer set alone: every
      # offer that command makes silently stops being checked while the whole-run assertions
      # below still pass, because the other family commands keep req_n above zero. That is a
      # gate quietly ceasing to cover part of its surface -- the failure this file's check-8
      # extractor-coverage assertion exists to prevent, and the reason no stop-routing check was
      # shipped. A family command that offers something must declare what it writes.
      if [ -z "$writers" ]; then
        fail 11 "$CMD_DIR/$y$CMD_SUFFIX makes a choices: offer but its \`deliverable_paths\` = ... \`title:\` span yields no path -- the EXTRACTOR has drifted or the handoff sentence was reworded, and every offer this command makes has stopped being checked; fix the parser or restore the declaration, never the offers"
        continue
      fi

      while IFS='|' read -r ln x has; do
        [ -n "$ln" ] || continue
        need=0; needt=""
        while IFS= read -r t; do
          [ -n "$t" ] || continue
          grep -qxF -- "$t" <<<"$writers" && { need=1; needt="$t"; break; }
        done < <(grep -F "$x|" <<<"$targets" | sed 's/^[^|]*|//')
        [ "$need" = 1 ] || continue
        req_n=$((req_n + 1))
        [ "$has" = 1 ] || fail 11 "$CMD_DIR/$y$CMD_SUFFIX:$ln offers $qual$x with no <merge-clause>, and this run writes '$needt' -- the artifact $qual$x's require-on-main gate targets, so that command stops while this phase's pull request is open ($CORE_PLUGIN_REL/$REF_DIR/next-phase-offer.md owns the placeholder and its resolution table)"
      done <<<"$offers"
    done < <(cmd_names "$p")
  done <<<"$globs"

  # Coverage assertions. Both states mean the check has gone quiet rather than clean, and a
  # gate that has stopped being able to fail must turn the build red, not green. The family
  # description below lists every glob the scope paragraph named, not just one of them, so the
  # message stays accurate on a plugin whose line names more than one.
  local family_desc; family_desc=$(printf '%s\n' "$globs" | sed "s|^|$qual|" | tr '\n' ' ' | sed 's/ $//')
  [ "$route_n" -gt 0 ] || fail 11 "$CORE_PLUGIN_REL/$REF_DIR/next-phase-offer.md binds the <merge-clause> rule to '$family_desc', which matches no command in $CMD_DIR/ -- the family was renamed or retired and this check now examines nothing"
  [ "$req_n" -gt 0 ] || fail 11 "no offer in the '$family_desc' family names a command whose require-on-main target that offer's own run writes -- either the route stopped handing off to itself or the EXTRACTOR drifted; fix the parser, never the offers"
}

# HANDOFF_PLUGIN_RELS is a declared list, not an inferred one -- same asymmetry as
# COST_PLUGIN_RELS above, and the same correction. A plugin that ships commands of the
# family the <merge-clause> rule binds, but is missing from the list, has check 11 silently
# skipped for it. This asserts the other half.
#
# THE TRIGGER IS THE CALL SITES, NOT THE REFERENCE FILE. It used to fire on a plugin
# shipping $REF_DIR/next-phase-offer.md; extracting the corpus made the corpus plugin ship
# that reference and not one command of the family, so the old form FORCED it into the list,
# whereupon check 11 ran for it, derived an empty family and failed -- with neither branch
# green, because "a relation that comes up empty fails" is the property that must not be
# relaxed. The family is derived exactly as check_merge_clause derives it, from
# $CORE_PLUGIN_REL's copy of the reference and qualified by the plugin under check, so the
# two can never disagree about which commands the rule binds.
#
# NOT the alternative fixes. Making the dispatch guard skip a plugin with no family command,
# or exempting $CORE_PLUGIN_REL there, are both absence-implies-skip at the dispatch site:
# under either, a plugin whose family commands were RENAMED drops out of check 11 entirely
# and the route_n vacuity guard cannot catch it, because the check never runs at all.
# Re-basing the trigger keeps that direction loud.
check_handoff_applicability() {
  local root="$1" p="$1/$PLUGIN_REL" ref="$1/$CORE_PLUGIN_REL/$REF_DIR/next-phase-offer.md"
  local qual="/${PLUGIN_REL##*/}:" globs glob y n=0 family_desc
  # An absent or family-less reference is not degraded to a skip HERE only because it is
  # already loud THERE: check_merge_clause fails on both for every declared plugin, and
  # HANDOFF_PLUGIN_RELS is non-empty in every edition that ships the subsystem.
  [ -f "$ref" ] || return
  globs=$(scope_family "$ref" "$qual")
  [ -n "$globs" ] || return
  # Same accumulation as check_merge_clause: a plugin's scope line may name more than one
  # glob (e.g. /prd-ground's own family alongside the route it left), and `n` has to count
  # matches across every one of them, not just the first.
  while IFS= read -r glob; do
    [ -n "$glob" ] || continue
    while IFS= read -r y; do
      [ -n "$y" ] || continue
      case "$y" in $glob) n=$((n + 1)) ;; esac
    done < <(cmd_names "$p")
  done <<<"$globs"
  [ "$n" -gt 0 ] || return
  family_desc=$(printf '%s\n' "$globs" | sed "s|^|$qual|" | tr '\n' ' ' | sed 's/ $//')
  case " $HANDOFF_PLUGIN_RELS " in
    *" $PLUGIN_REL "*) : ;;
    *) fail 11 "$PLUGIN_REL ships $n command(s) of the '$family_desc' family that $CORE_PLUGIN_REL/$REF_DIR/next-phase-offer.md binds the <merge-clause> rule to, but is not a member of HANDOFF_PLUGIN_RELS -- check 11 never runs for it" ;;
  esac
}

# ------------------------------------------------------------------ selftest
# One passing fixture tree; each check gets a mutation of a fresh copy. Asserting
# the exit code alone would let a mutation that trips a DIFFERENT check register
# as success, so each case also asserts which check fired.
selftest() {
  local here fixture tmp rc=0
  here=$(cd "$(dirname "$0")" && pwd)
  fixture="$here/fixtures/docs/pass"
  # The fixture tree ships two plugins so the dispatch loop is exercised by more than
  # one element. A one-element run cannot distinguish "the loop works" from "the loop
  # runs once and the body ignores it".
  export PLUGIN_RELS="plugins/dev-workflows plugins/fixture-two"
  # The other three plugin-set variables are fixture edition config too, and they became so
  # the moment the repository's corpus moved out of plugins/dev-workflows: the fixture tree
  # keeps its corpus and its call sites in ONE plugin -- a legitimate edition shape, and the
  # one every edition had before the extraction -- so a CORE_PLUGIN_REL inherited from the
  # repository would name a plugin the fixture does not contain, and every green case would
  # go red reporting a missing reference. Cases that need the split shape override
  # CORE_PLUGIN_REL per run (see expect_fail_env / expect_pass_after_env below).
  export CORE_PLUGIN_REL="plugins/dev-workflows"
  # The loader skill is edition config in its own right, NOT derived from CORE_PLUGIN_REL:
  # the relocation helper below moves the corpus without rewriting a single call site, which
  # is the real shape too, and a derived name would stop matching them the moment it moved.
  export LOADER_SKILL="dev-workflows:reference"
  export COST_PLUGIN_RELS="plugins/dev-workflows"
  # The manifest is edition config too, and the fixture ships its own: pointed at the
  # repository's would make every case below assert against real command names, and the
  # green cases are worthless if anything outside the mutation can redden them.
  export NS_MAP_REL="plugins/dev-workflows/scripts/command-namespaces.json"
  export HANDOFF_PLUGIN_RELS="plugins/dev-workflows"
  # Check 18's arming flag is neutralised here so each case controls it, and the two that need
  # it armed set it through expect_fail_env / expect_pass_after_env. Without this line the
  # selftest inherits the caller's value, and the one case that proves the gate STAYS QUIET off
  # a publishing ref fails spuriously -- for the person most likely to run it that way, which is
  # whoever is verifying this gate. Found by doing exactly that.
  export ASSERT_PUBLISHED=""
  [ -d "$fixture" ] || { echo "SELFTEST FAIL: fixture tree missing at $fixture" >&2; exit 2; }

  expect_pass() {
    tmp=$(mktemp -d); cp -R "$fixture/." "$tmp/"
    if "$0" --root "$tmp" >/dev/null 2>&1; then printf 'ok    %s\n' "$1"
    else printf 'FAIL  %s: expected exit 0\n' "$1"; rc=1; fi
    rm -rf "$tmp"
  }
  expect_pass_after() { # <description> <mutation-shell> -- like expect_fail, but the
    # mutation must still leave every check passing. expect_fail alone cannot prove a
    # new number word maps to the right value: an unrecognized word already fails check
    # 9 (no count sentence found), so a mutation that merely stays red proves nothing
    # about which word landed. This proves the word is both matched AND converted correctly.
    tmp=$(mktemp -d); cp -R "$fixture/." "$tmp/"
    ( cd "$tmp" && eval "$2" )
    if "$0" --root "$tmp" >/dev/null 2>&1; then printf 'ok    %s\n' "$1"
    else printf 'FAIL  %s: expected exit 0\n' "$1"; rc=1; fi
    rm -rf "$tmp"
  }
  expect_fail() { # <description> <check-number> <mutation-shell>
    tmp=$(mktemp -d); cp -R "$fixture/." "$tmp/"
    ( cd "$tmp" && eval "$3" )
    local out; out=$("$0" --root "$tmp" 2>&1); local got=$?
    # The colon is load-bearing: fail() prints "FAIL check <n>: <message>", and without it
    # "FAIL check 1" would also match a "FAIL check 10" line, letting a check-10 failure
    # satisfy a check-1 case. Every check number past 9 makes that collision reachable.
    if [ "$got" -eq 1 ] && grep -q "FAIL check $2:" <<<"$out"; then
      printf 'ok    %s (check %s fired)\n' "$1" "$2"
    else
      printf 'FAIL  %s: expected exit 1 with "FAIL check %s", got exit %s\n' "$1" "$2" "$got"; rc=1
    fi
    rm -rf "$tmp"
  }

  # ...and the same two, with EDITION CONFIG overridden for the child run. Checks 8, 9, 11 and 16
  # each read a shared reference from $CORE_PLUGIN_REL and their call sites from $PLUGIN_REL,
  # and there is no way to exercise that split without running the gate against a config in
  # which the two differ. The assignments are eval'd rather than word-split, because
  # COST_PLUGIN_RELS is itself a space-separated list and `env VAR=$3` would tear it apart.
  expect_fail_env() { # <description> <check-number> <env-assignments> <mutation-shell>
    tmp=$(mktemp -d); cp -R "$fixture/." "$tmp/"
    ( cd "$tmp" && eval "$4" )
    local out; out=$(eval "export $3"; "$0" --root "$tmp" 2>&1); local got=$?
    if [ "$got" -eq 1 ] && grep -q "FAIL check $2:" <<<"$out"; then
      printf 'ok    %s (check %s fired)\n' "$1" "$2"
    else
      printf 'FAIL  %s: expected exit 1 with "FAIL check %s", got exit %s\n' "$1" "$2" "$got"; rc=1
    fi
    rm -rf "$tmp"
  }
  expect_pass_after_env() { # <description> <env-assignments> <mutation-shell>
    tmp=$(mktemp -d); cp -R "$fixture/." "$tmp/"
    ( cd "$tmp" && eval "$3" )
    if ( eval "export $2"; "$0" --root "$tmp" ) >/dev/null 2>&1; then printf 'ok    %s\n' "$1"
    else printf 'FAIL  %s: expected exit 0\n' "$1"; rc=1; fi
    rm -rf "$tmp"
  }

  # Moves part of the reference corpus into a SECOND plugin -- the shape checks 8, 9, 11 and 16
  # have to survive: the reference in one plugin, the call sites in another. Every case that
  # calls it runs the gate with CORE_PLUGIN_REL pointed at plugins/fixture-core.
  #
  # fixture-core is deliberately NOT in PLUGIN_RELS. It stands in for a reference corpus, not
  # for a third documented plugin, and giving it a docs/ tree would prove nothing about the
  # cross-plugin READ that this fixture does not already prove about the dispatch loop.
  # docs/reference/references.md is amended in the same breath because check 4 inventories the
  # reference dir in BOTH directions and check 9 counts its files -- a stale inventory would
  # turn the tree red for a reason that has nothing to do with the case being made, and the
  # green cases below are worthless if anything else can redden them. The replacement count is
  # DERIVED from the tree after the move, never arithmetic on the number already written there.
  relocate_refs() { # <reference-basename>... -- run from inside the copied tree
    local f left idx="$PLUGIN_REL/docs/reference/references.md"
    mkdir -p "plugins/fixture-core/$REF_DIR"
    for f in "$@"; do
      mv "$PLUGIN_REL/$REF_DIR/$f" "plugins/fixture-core/$REF_DIR/$f" || return 1
      sed "/^- \`$f\`\$/d" "$idx" > rr.tmp && mv rr.tmp "$idx"
    done
    left=$(find "$PLUGIN_REL/$REF_DIR" -type f | wc -l | tr -d ' ')
    sed -E "s|ships [0-9]+ files|ships $left files|" "$idx" > rr.tmp && mv rr.tmp "$idx"
  }
  # ...and the unit the corpus actually moves in. CORE_PLUGIN_REL is ONE variable serving all
  # three checks, so a case that relocated only the file it is about would leave the other two
  # checks reporting a reference missing from the corpus plugin -- red, for a reason the case
  # was not making. That is the real shape too: the corpus is extracted as a whole.
  relocate_corpus() { relocate_refs cost-emission.md next-phase-offer.md phase-handoff.md; }

  # Rebuilds the namespace manifest from the tree. The two fixture-GROWING cases below add real
  # commands, and check 4 asserts the manifest equals the tree in both directions -- so a case
  # that grew one without the other would go red for a reason it is not making, and the green
  # cases are worthless if anything but their own subject can redden them. DERIVED here for the
  # same reason the gate demands it of the repository: a hand-written list in the mutation would
  # be a second place to keep the command set, and the two would drift.
  ns_map_regen() { # run from inside the copied tree
    [ -n "$NS_MAP_REL" ] || return 0
    local d rel n
    for d in plugins/*/; do
      rel="${d%/}"
      while IFS= read -r n; do
        [ -n "$n" ] && printf '%s\t%s\n' "$rel" "$n"
      done < <(cmd_names "$rel")
    done | python3 -c '
import json, os, sys
out = {}
for line in sys.stdin:
    line = line.rstrip("\n")
    if not line:
        continue
    d, name = line.split("\t", 1)
    ns = os.path.basename(d)
    pj = os.path.join(d, ".claude-plugin", "plugin.json")
    if os.path.isfile(pj):
        try:
            with open(pj, encoding="utf-8", errors="replace") as fh:
                ns = (json.load(fh) or {}).get("name") or ns
        except (OSError, ValueError, TypeError, AttributeError):
            pass
    out.setdefault(ns, []).append(name)
with open(sys.argv[1], "w", encoding="utf-8") as fh:
    json.dump({k: sorted(v) for k, v in out.items()}, fh, indent=2, sort_keys=True)
    fh.write("\n")
' "$NS_MAP_REL"
  }

  expect_pass "the unmutated fixture passes every check"
  expect_fail "a broken relative link is rejected"  1 "sed -i.bak 's|(reference/hooks.md)|(reference/nope.md)|' $PLUGIN_REL/docs/README.md"
  expect_fail "a broken link in the plugin README is rejected" 1 "sed -i.bak 's|(docs/README.md)|(docs/NOPE.md)|' $PLUGIN_REL/README.md"
  expect_fail "a broken anchor is rejected"         2 "sed -i.bak 's|(getting-started.md#install)|(getting-started.md#no-such-heading)|' $PLUGIN_REL/docs/README.md"
  expect_fail "an orphan page is rejected"          3 "printf '# Orphan\n\nUnreachable.\n' > $PLUGIN_REL/docs/orphan.md"
  expect_fail "an undocumented command is rejected" 4 "mkdir -p $(dirname $(cmd_file $PLUGIN_REL delta)) 2>/dev/null; printf -- '---\nname: delta\n---\n' > $(cmd_file $PLUGIN_REL delta)"
  expect_fail "a drifted subtree count is rejected" 4 "sed -i.bak 's|\`handoff/\` (2)|\`handoff/\` (3)|' $PLUGIN_REL/docs/reference/references.md"
  expect_fail "an undocumented skill is rejected"    4 "mkdir -p $PLUGIN_REL/skills/epsilon && printf -- '---\nname: epsilon\n---\n' > $PLUGIN_REL/skills/epsilon/SKILL.md"
  # The command-namespace manifest, in both directions and on both axes. Each of the first
  # four REWRITES the file whole rather than editing a line out of it: deleting a name with
  # sed leaves a dangling comma, and the invalid-JSON message would then stand in for the
  # missing-name one -- same check number, different failure mode, a case proving nothing.
  # The fifth removes the file outright, which is its own failure mode. Each rewrite is
  # otherwise CORRECT, carrying one error and no other, so the manifest assertion is the
  # only check 4 failure any of the five can produce -- and each therefore also re-states
  # what a correct manifest looks like, including `renamed-namespace`, the entry keyed by a
  # DECLARED plugin name that its directory does not carry.
  expect_fail "a command missing from the namespace manifest is rejected" 4 \
    "printf '{\"dev-workflows\": [\"alpha\"], \"fixture-two\": [\"omega\"], \"renamed-namespace\": [\"theta\"]}\n' > $NS_MAP_REL"
  expect_fail "a manifest name that is no command is rejected" 4 \
    "printf '{\"dev-workflows\": [\"alpha\", \"alpha-two\", \"phantom\"], \"fixture-two\": [\"omega\"], \"renamed-namespace\": [\"theta\"]}\n' > $NS_MAP_REL"
  expect_fail "a command-shipping plugin with no manifest entry is rejected" 4 \
    "printf '{\"dev-workflows\": [\"alpha\", \"alpha-two\"], \"fixture-two\": [\"omega\"]}\n' > $NS_MAP_REL"
  expect_fail "a manifest namespace naming no plugin is rejected" 4 \
    "printf '{\"dev-workflows\": [\"alpha\", \"alpha-two\"], \"fixture-two\": [\"omega\"], \"renamed-namespace\": [\"theta\"], \"ghost\": [\"x\"]}\n' > $NS_MAP_REL"
  # The DECLARED-name branch, pinned: plugins/fixture-unlisted ships theta and declares the
  # namespace `renamed-namespace`. Keyed by its directory instead, the manifest is wrong in
  # both directions at once -- a namespace naming no plugin, and a plugin with no entry --
  # which is exactly what a gate reading the directory would accept.
  expect_fail "a manifest keyed by a plugin's DIRECTORY rather than its declared name is rejected" 4 \
    "printf '{\"dev-workflows\": [\"alpha\", \"alpha-two\"], \"fixture-two\": [\"omega\"], \"fixture-unlisted\": [\"theta\"]}\n' > $NS_MAP_REL"
  expect_fail "a missing namespace manifest is rejected" 4 "rm -f $NS_MAP_REL"
  expect_fail "an undocumented env var is rejected" 5 "printf 'Reads \$NEW_SETTABLE_VAR here.\n' >> $(cmd_file $PLUGIN_REL alpha)"
  expect_pass_after "a 190-character cell of multibyte characters is accepted (check 6 counts characters, not bytes)" \
    "printf '\\n| a | %s |\\n|---|---|\\n| b | c |\\n' \"\$(printf '\\342\\206\\222%.0s' \$(seq 190))\" >> $PLUGIN_REL/docs/reference/hooks.md"
  expect_fail "an over-long table cell is rejected" 6 "awk 'BEGIN{s=\"\"; while(length(s)<260) s=s \"x\"; printf \"\\n| a | %s |\\n|---|---|\\n| b | c |\\n\", s}' >> $PLUGIN_REL/docs/reference/hooks.md"
  expect_fail "a drifted install block is rejected" 7 "sed -i.bak 's|$CLI plugin install ${PLUGIN_REL##*/}@fixture-plugins|$CLI plugin install ${PLUGIN_REL##*/}@drifted|' $PLUGIN_REL/docs/getting-started.md"
  expect_fail "a documented nonexistent skill is rejected" 4 "printf '\n| \`ghost-skill\` | Yes | fixture mutation |\n' >> $PLUGIN_REL/docs/reference/references.md"
  expect_fail "a broken link in the ROOT README is rejected" 1 "sed -i.bak 's|($PLUGIN_REL/README.md)|($PLUGIN_REL/NOPE.md)|' README.md"
  expect_fail "a broken bare #anchor is rejected"   2 "printf '\n[self](#no-such-heading-here)\n' >> $PLUGIN_REL/docs/README.md"
  expect_fail "a documented nonexistent agent is rejected"     4 "printf '\n| \`ghost-agent\` | fixture |\n' >> $PLUGIN_REL/docs/reference/agents.md"
  # The agents direction was made ROW-anchored after a review proved a prose mention
  # satisfied it; its three siblings were not. These two cases pin the fix.
  expect_fail "a hook row replaced by a prose mention is rejected" 4 \
    "F=$PLUGIN_REL/docs/reference/hooks.md; h=\$(grep -oE '^\| \`[a-z-]+\`' \$F | head -1 | tr -d '|\` '); sed -i.bak \"/^| \\\`\$h\\\`/d\" \$F; printf 'The \`%s\` hook is described here in prose.\\n' \"\$h\" >> \$F"
  expect_fail "a documented nonexistent hook is rejected"      4 "printf '\n| \`ghost-hook\` | fixture |\n' >> $PLUGIN_REL/docs/reference/hooks.md"
  expect_fail "a documented nonexistent reference file is rejected" 4 "printf '\n- \`ghost-ref.md\`\n' >> $PLUGIN_REL/docs/reference/references.md"
  expect_fail "a claimed-but-absent subtree is rejected"       4 "rm -rf $PLUGIN_REL/$REF_DIR/handoff"
  expect_fail "an undocumented NEW subtree is rejected"        4 "mkdir -p $PLUGIN_REL/$REF_DIR/brandnew && printf '# x\n' > $PLUGIN_REL/$REF_DIR/brandnew/x.md"
  expect_fail "a documented-but-unread env var is rejected"    5 "printf '\n**\`\$PHANTOM_VAR\`** — never read anywhere.\n' >> $PLUGIN_REL/docs/reference/environment.md"
  expect_fail "an over-long cell in the ROOT README is rejected" 6 "awk 'BEGIN{s=\"\"; while(length(s)<260) s=s \"x\"; printf \"\n| a | %s |\n|---|---|\n| b | c |\n\", s}' >> README.md"
  # ${CLI_VERBS##*|} is the LAST verb in the alternation -- every edition has one by
  # construction (canonical "reinstall", copilot "update") -- so this is extracted by
  # check 7 in every edition, regardless of which verbs exist there. The target names
  # a line absent from the root README, so it is extracted AND counts as extra.
  expect_fail "an install line absent from the root README is rejected" 7 "printf '\n$CLI plugin ${CLI_VERBS##*|} ${PLUGIN_REL##*/}@extra-fixture-target\n' >> $PLUGIN_REL/docs/getting-started.md"
  expect_fail "a drifted prose count is rejected"              9 "mkdir -p $(dirname $(cmd_file $PLUGIN_REL gamma)) 2>/dev/null; printf -- '---\nname: gamma\n---\n' > $(cmd_file $PLUGIN_REL gamma) && printf -- '# /gamma\n\nPage.\n' > $PLUGIN_REL/docs/$DOC_CMD_DIR/gamma.md && sed -i.bak 's|($DOC_CMD_DIR/alpha.md)|($DOC_CMD_DIR/alpha.md), [\`/gamma\`]($DOC_CMD_DIR/gamma.md)|' $PLUGIN_REL/docs/README.md"
  # The five cases below read the fixture's COMMAND count, and that count moved 1 -> 2 when
  # check 11's per-command coverage assertion needed a second command in the offer family to be
  # provable against (with one family member, emptying its writer set also empties the run-wide
  # one, so the fixture could not tell the two assertions apart). Every assertion is unchanged;
  # only the numerals and the how-many-to-add loops track the new base: the compound-count case
  # still claims a compound whose tail is a mapped word equal to the real total (twenty-six over
  # 2+4, where it was twenty-five over 1+4), and the two fixture-growing cases still land on
  # exactly seventeen and eighteen commands by adding one fewer each.
  expect_fail "a count sentence reworded away is rejected"     9 "sed -i.bak 's|two slash commands|a handful of slash commands|' $PLUGIN_REL/README.md"
  expect_fail "a compound count whose tail matches a shorter number word is rejected" 9 \
    "mkdir -p $(dirname $(cmd_file $PLUGIN_REL delta)) 2>/dev/null && printf -- '---\nname: delta\n---\n' > $(cmd_file $PLUGIN_REL delta) && printf -- '# /delta\n\nPage.\n' > $PLUGIN_REL/docs/$DOC_CMD_DIR/delta.md && sed -i.bak 's|($DOC_CMD_DIR/alpha.md)|($DOC_CMD_DIR/alpha.md), [\`/delta\`]($DOC_CMD_DIR/delta.md)|' $PLUGIN_REL/docs/README.md && mkdir -p $(dirname $(cmd_file $PLUGIN_REL epsilon)) 2>/dev/null && printf -- '---\nname: epsilon\n---\n' > $(cmd_file $PLUGIN_REL epsilon) && printf -- '# /epsilon\n\nPage.\n' > $PLUGIN_REL/docs/$DOC_CMD_DIR/epsilon.md && sed -i.bak 's|($DOC_CMD_DIR/alpha.md)|($DOC_CMD_DIR/alpha.md), [\`/epsilon\`]($DOC_CMD_DIR/epsilon.md)|' $PLUGIN_REL/docs/README.md && mkdir -p $(dirname $(cmd_file $PLUGIN_REL zeta)) 2>/dev/null && printf -- '---\nname: zeta\n---\n' > $(cmd_file $PLUGIN_REL zeta) && printf -- '# /zeta\n\nPage.\n' > $PLUGIN_REL/docs/$DOC_CMD_DIR/zeta.md && sed -i.bak 's|($DOC_CMD_DIR/alpha.md)|($DOC_CMD_DIR/alpha.md), [\`/zeta\`]($DOC_CMD_DIR/zeta.md)|' $PLUGIN_REL/docs/README.md && mkdir -p $(dirname $(cmd_file $PLUGIN_REL eta)) 2>/dev/null && printf -- '---\nname: eta\n---\n' > $(cmd_file $PLUGIN_REL eta) && printf -- '# /eta\n\nPage.\n' > $PLUGIN_REL/docs/$DOC_CMD_DIR/eta.md && sed -i.bak 's|($DOC_CMD_DIR/alpha.md)|($DOC_CMD_DIR/alpha.md), [\`/eta\`]($DOC_CMD_DIR/eta.md)|' $PLUGIN_REL/docs/README.md && sed -i.bak2 's|two slash commands|twenty-six slash commands|' $PLUGIN_REL/README.md"
  # Discriminates the word-boundary anchor on the reference-files alternation specifically: the
  # fixture ships 8 reference files, so an unanchored "eight" matches the tail of "twenty-eight"
  # and compares 8 against 8 -- a wrong claim passing on a coincidentally-correct numeral.
  # Anchored, nothing matches at a boundary and the count sentence reads as drifted away. Verified
  # red (this case FAILs) with the anchor stashed, green with it applied. The numerals track the
  # fixture: it shipped 6 reference files (and this case read "twenty-six") until check 11's
  # route fixture added next-phase-offer.md and phase-handoff.md. The assertion is unchanged --
  # a compound whose tail is a mapped word equal to the real count -- and "twenty-eight" is
  # unmapped by _word2num for the same reason "twenty-six" was.
  expect_fail "a compound reference-file count whose tail matches a shorter number word is rejected" 9 \
    "sed -i.bak 's|ships 8 files|ships twenty-eight files|' $PLUGIN_REL/docs/reference/references.md"
  # Proves _word2num and the commands alternation actually learned "seventeen" -- not merely
  # that an unrecognized word is rejected (every unmapped word already fails check 9 via "no
  # count sentence found", which would make a same-shaped expect_fail case pass whether or not
  # "seventeen" was ever added). Grows the fixture to 17 real, fully-inventoried commands and
  # re-words the count sentence to match, so the WHOLE gate -- not just check 9 -- must pass.
  # Verified red (this case FAILs: "no count sentence found") with the word2num/alternation
  # additions stashed, green with them applied.
  expect_pass_after "a correctly-worded seventeen-command count is accepted" \
    "for n in cmd01 cmd02 cmd03 cmd04 cmd05 cmd06 cmd07 cmd08 cmd09 cmd10 cmd11 cmd12 cmd13 cmd14 cmd15; do mkdir -p \$(dirname \$(cmd_file $PLUGIN_REL \$n)) 2>/dev/null; printf -- '---\nname: %s\n---\n' \$n > \$(cmd_file $PLUGIN_REL \$n); printf -- '# /%s\n\nPage.\n' \$n > $PLUGIN_REL/docs/$DOC_CMD_DIR/\$n.md; printf -- '\n- [%s](%s/%s.md)\n' \$n $DOC_CMD_DIR \$n >> $PLUGIN_REL/docs/README.md; done && sed -i.bak 's|two slash commands|seventeen slash commands|' $PLUGIN_REL/README.md && for n in cmd01 cmd02 cmd03 cmd04 cmd05 cmd06 cmd07 cmd08 cmd09 cmd10 cmd11 cmd12 cmd13 cmd14 cmd15; do printf -- '\nCommand: \`/%s\`.\n' \$n >> $PLUGIN_REL/README.md; done && { printf -- '\n\`\`\`mermaid\nflowchart TD\n'; for n in cmd01 cmd02 cmd03 cmd04 cmd05 cmd06 cmd07 cmd08 cmd09 cmd10 cmd11 cmd12 cmd13 cmd14 cmd15; do printf -- '    x%s[\"/%s\"]\n' \$n \$n; done; printf -- '\`\`\`\n'; } >> $PLUGIN_REL/docs/workflow.md && ns_map_regen"
  # The same proof for the OTHER gated alternation. The case above exercises the commands
  # alternation only; the cost-emitting-commands alternation in check 9 has its own word list,
  # and until this case existed nothing exercised it -- a word missing from it would have failed
  # only on a real release, which is the failure mode the whole selftest exists to move forward
  # in time. Grows the fixture to eighteen real, fully-inventoried commands, seventeen of which
  # emit a cost entry with a matching section-7 row, and re-words BOTH count sentences. The two
  # numbers deliberately differ: "eighteen" is read out of the commands alternation and
  # "seventeen" out of the cost-emitting one, so a word missing from either is attributable.
  # Verified red (this case FAILs: check 9 "cost-emitting commands: no count sentence found")
  # with the six words stashed out of the cost-emitting alternation alone, green with them
  # applied -- and the seventeen-command case above stays green throughout, which is what shows
  # the two cases cover different alternations.
  expect_pass_after "a correctly-worded seventeen cost-emitting-command count is accepted" \
    "for n in bravo charlie delta echo foxtrot golf hotel india juliet kilo lima mike november oscar papa quebec; do mkdir -p \$(dirname \$(cmd_file $PLUGIN_REL \$n)) 2>/dev/null; printf -- '---\nname: %s\n---\n' \$n > \$(cmd_file $PLUGIN_REL \$n); printf -- '# /%s\n\nPage.\n' \$n > $PLUGIN_REL/docs/$DOC_CMD_DIR/\$n.md; printf -- '\n- [%s](%s/%s.md)\n' \$n $DOC_CMD_DIR \$n >> $PLUGIN_REL/docs/README.md; done && for n in bravo charlie delta echo foxtrot golf hotel india juliet kilo lima mike november oscar papa quebec; do printf -- '\nCall \`emit-cost\` with \`command: /%s\`, \`phase: fixture-phase\`, \`role: pm\`, done.\n' \$n >> \$(cmd_file $PLUGIN_REL \$n); done && { printf -- '# Cost emission (fixture)\n\n## 7. Attribution (phase / role)\n\n| Command | phase | role |\n|---------|-------|------|\n| \`/alpha\` | fixture-phase | pm |\n'; for n in bravo charlie delta echo foxtrot golf hotel india juliet kilo lima mike november oscar papa quebec; do printf -- '| \`/%s\` | fixture-phase | pm |\n' \$n; done; printf -- '\n## 8. Persistence\n\nNot modelled in the fixture.\n'; } > $PLUGIN_REL/$REF_DIR/cost-emission.md && sed -i.bak 's|two slash commands|eighteen slash commands|' $PLUGIN_REL/README.md && sed -i.bak 's|One commands emit a cost entry|Seventeen commands emit a cost entry|' $PLUGIN_REL/docs/reference/session-cost.md && for n in bravo charlie delta echo foxtrot golf hotel india juliet kilo lima mike november oscar papa quebec; do printf -- '\nCommand: \`/%s\`.\n' \$n >> $PLUGIN_REL/README.md; done && { printf -- '\n\`\`\`mermaid\nflowchart TD\n'; for n in bravo charlie delta echo foxtrot golf hotel india juliet kilo lima mike november oscar papa quebec; do printf -- '    x%s[\"/%s\"]\n' \$n \$n; done; printf -- '\`\`\`\n'; } >> $PLUGIN_REL/docs/workflow.md && ns_map_regen"
  # The same proof for the THIRD gated alternation, the agents one, and it is the reason check 9
  # learned "eleven": docs-workflows crossed ten agents and writes that count as a word, so the
  # sentence matched no alternative and the count read as ABSENT rather than as 11. Grows the
  # fixture to eleven real, fully-inventoried agents -- a file each, a table row each, and the
  # count sentence re-worded -- and asserts the gate stays GREEN, which is the only shape that
  # proves a new number word is matched AND converted. An expect_fail case would pass whether or
  # not "eleven" was ever added, since an unmapped word already fails via "no count sentence
  # found". Both halves verified on this branch against a copy of the grown fixture: with
  # "eleven" stashed out of the agents alternation alone the run FAILs "agents: no count sentence
  # found"; with _word2num's eleven mapped to 12 instead it FAILs "says eleven (12), tree has 11";
  # with both correct it passes. The new agents carry no `tools:` line, so check 17 is untouched.
  expect_pass_after "a correctly-worded eleven-agent count is accepted" \
    "for i in 03 04 05 06 07 08 09 10 11; do printf -- '---\nname: ag%s\ndescription: A fixture agent.\n---\n\nA fixture agent body.\n' \$i > $PLUGIN_REL/agents/ag\$i.md; done && awk '{print} /^\| \`eta\` \| fixture \|\$/{for(i=3;i<=11;i++) printf \"| \`ag%02d\` | fixture |\n\", i}' $PLUGIN_REL/docs/reference/agents.md > ag.tmp && mv ag.tmp $PLUGIN_REL/docs/reference/agents.md && sed -i.bak 's|The fixture ships 2 agents.|The fixture ships eleven agents.|' $PLUGIN_REL/docs/reference/agents.md"
  expect_fail "a wrong non-ASCII anchor is rejected"           2 "printf '\n[bad](#uber-config)\n' >> $PLUGIN_REL/docs/$DOC_CMD_DIR/alpha.md"
  expect_fail "a wrong duplicate-heading index is rejected"    2 "printf '\n[bad](#notes-2)\n' >> $PLUGIN_REL/docs/$DOC_CMD_DIR/alpha.md"
  # Check 14 is asserted through the same decoder the check uses, so the fixture carries the
  # name only for the instant the case runs and this file still never spells it out.
  expect_fail "the foreign organisation named in a docs page is rejected" 14 \
    "printf '%s\n' \"\$(b64d \$FOREIGN_IDENTITY_SAMPLE_B64)\" >> $PLUGIN_REL/docs/README.md"
  expect_fail "an unmarked vendor token in CLAUDE.md is rejected" 13 \
    "printf 'A stale claim about a Jira status.\n' >> CLAUDE.md"
  expect_pass_after "a MARKED vendor token in CLAUDE.md is accepted" \
    "printf 'A stale claim about a Jira status. <!-- vendor-token-ok: fixture -->\n' >> CLAUDE.md"
  # Check 13 and checks 1-2 over the CLAUDE.md split's two new surfaces, each as a red/green
  # pair: an implementation that added the files but dropped the marker logic (13) or the
  # anchor resolution (2) passes every red case and fails its green twin.
  expect_fail "an unmarked vendor token in a .claude/rules file is rejected" 13 \
    "mkdir -p .claude/rules && printf -- '---\npaths:\n  - \"plugins/**\"\n---\n\nA stale claim about a Jira status.\n' > .claude/rules/area.md"
  expect_pass_after "a MARKED vendor token in a .claude/rules file is accepted" \
    "mkdir -p .claude/rules && printf -- '---\npaths:\n  - \"plugins/**\"\n---\n\nA stale claim about a Jira status. <!-- vendor-token-ok: fixture -->\n' > .claude/rules/area.md"
  expect_fail "an unmarked vendor token in docs/maintainers is rejected" 13 \
    "mkdir -p docs/maintainers && printf '# Rationale\n\nA stale claim about a Jira status.\n' > docs/maintainers/rationale.md"
  expect_pass_after "a MARKED vendor token in docs/maintainers is accepted" \
    "mkdir -p docs/maintainers && printf '# Rationale\n\nA stale claim about a Jira status. <!-- vendor-token-ok: fixture -->\n' > docs/maintainers/rationale.md"
  expect_fail "a broken link in CLAUDE.md is caught" 1 \
    "printf '\nSee [the rule](docs/maintainers/nowhere.md).\n' >> CLAUDE.md"
  expect_fail "a broken link in a .claude/rules file is caught" 1 \
    "mkdir -p .claude/rules && printf 'See [the rule](../../docs/maintainers/nowhere.md).\n' > .claude/rules/area.md"
  expect_fail "a why-link to a missing rationale anchor is caught" 2 \
    "mkdir -p docs/maintainers && printf '# Rationale\n\n## real-slug\n\nEvidence.\n' > docs/maintainers/rationale.md && printf '\nA rule. ([why](docs/maintainers/rationale.md#no-such-slug))\n' >> CLAUDE.md"
  expect_pass_after "a why-link to a present rationale anchor passes, from CLAUDE.md and from a rules file" \
    "mkdir -p docs/maintainers .claude/rules && printf '# Rationale\n\n## real-slug\n\nEvidence.\n' > docs/maintainers/rationale.md && printf '\nA rule. ([why](docs/maintainers/rationale.md#real-slug))\n' >> CLAUDE.md && printf 'A rule. ([why](../../docs/maintainers/rationale.md#real-slug))\n' > .claude/rules/area.md"
  expect_fail "a broken link inside docs/maintainers is caught" 1 \
    "mkdir -p docs/maintainers && printf '# Rationale\n\nSee [x](nowhere.md).\n' > docs/maintainers/rationale.md"
  expect_fail "the foreign organisation named OUTSIDE the plugin is rejected" 14 \
    "printf '%s\n' \"\$(b64d \$FOREIGN_IDENTITY_SAMPLE_B64)\" >> README.md"
  expect_fail "a command missing from the plugin README is rejected" 15 \
    "sed -i.bak 's|, \`/alpha-two\`||' $PLUGIN_REL/README.md"
  # /alpha is a strict PREFIX of /alpha-two, which is why this case exists: `\b`
  # treats `-` as a word boundary, so `/alpha-two` used to satisfy the requirement
  # for `/alpha` and this mutation passed. The live tree has exactly one such pair
  # (/prompt against /prompt-brainstorm and /prompt-grill-me).
  expect_fail "a command whose name prefixes another is not covered by it" 15 \
    "sed -i.bak 's|\`/alpha\`, ||' $PLUGIN_REL/README.md"
  expect_fail "a command missing from the workflow DIAGRAM is rejected" 15 \
    "sed -i.bak 's|\"/alpha-two\"|\"/removed\"|' $PLUGIN_REL/docs/workflow.md"
  expect_fail "a workflow page with no diagram at all is rejected" 15 \
    "sed -i.bak 's|^\`\`\`mermaid$|text|' $PLUGIN_REL/docs/workflow.md"
  expect_fail "a titled link to a missing file is rejected"    1 "printf '\n[bad](nope.md \"T\")\n' >> $PLUGIN_REL/docs/$DOC_CMD_DIR/alpha.md"
  expect_fail "an angle-bracket link to a missing file is rejected" 1 "printf '\n[bad](<nope.md>)\n' >> $PLUGIN_REL/docs/$DOC_CMD_DIR/alpha.md"
  expect_fail "an over-long INDENTED table cell is rejected"   6 "awk 'BEGIN{s=\"\"; while(length(s)<260) s=s \"q\"; printf \"\n  | a | %s |\n  |---|---|\n\", s}' >> $PLUGIN_REL/docs/reference/agents.md"
  expect_fail "a missing marketplace-add line is rejected"     7 "sed -i.bak '/$CLI plugin marketplace add/d' $PLUGIN_REL/docs/getting-started.md"
  expect_fail "a missing second required-verb line is rejected" 7 "sed -i.bak '/$CLI plugin ${CLI_REQUIRED##*|}/d' $PLUGIN_REL/docs/getting-started.md"
  expect_fail "getting-started not installing the plugin itself is rejected" 7 "sed -i.bak '/$CLI plugin install ${PLUGIN_REL##*/}@/d' $PLUGIN_REL/docs/getting-started.md"
  # Check 10 -- identity quarantine. Both mutations derive the offending token from the
  # fixture's own repo-root README, so the cases port to a fixture with a different
  # marketplace name rather than pinning this one.
  expect_fail "a container-repo URL on a docs page is rejected" 10 \
    "slug=\$(grep -oE '^$CLI plugin marketplace add [^ ]+' README.md | awk '{print \$NF}' | head -1); printf -- '\n[sibling plugin](https://github.com/%s/tree/main/plugins/extra-plugin)\n' \"\$slug\" >> $PLUGIN_REL/docs/reference/hooks.md"
  expect_fail "a marketplace name on a docs page is rejected" 10 \
    "mkt=\$(grep -oE '^$CLI plugin install [^ ]+@[^ ]+' README.md | sed 's/.*@//' | head -1); printf -- '\nInstall the sibling with \`$CLI plugin install extra-plugin@%s\`.\n' \"\$mkt\" >> $PLUGIN_REL/docs/reference/agents.md"
  # ...and the boundary itself, which is the half an expect_fail case cannot prove: a LONGER
  # identifier that merely contains the marketplace name is not naming it, and must stay green.
  # Under the substring match this replaced, this case goes red -- which is what a fork that
  # names its marketplace `workflows` met on every page saying `dev-workflows` (38 failures on
  # unmodified, correct pages, measured). Verified red before / green after by stashing the
  # boundary anchors.
  expect_pass_after "a longer identifier merely containing the marketplace name is accepted" \
    "mkt=\$(grep -oE '^$CLI plugin install [^ ]+@[^ ]+' README.md | sed 's/.*@//' | head -1); printf -- '\nThe mirror repository is called sub-%s-mirror and is not this marketplace.\n' \"\$mkt\" >> $PLUGIN_REL/docs/reference/agents.md"

  # ...and the vacuity guard: with no install block to derive from, check 10 has no token
  # set and must go RED rather than pass every page. (Check 7 fires on this mutation too;
  # the case asserts check 10 specifically.)
  expect_fail "an underivable identity token set is rejected" 10 \
    "sed -i.bak '/^$CLI plugin /d' README.md"

  # Check 11 -- merge-clause adoption. The fixture's route is one command (`alpha`, matched by
  # the `alpha*` family glob next-phase-offer.md declares) offering `/dev-workflows:omega`,
  # whose row-F entry gates `alpha-deliverable.md` -- which alpha's own `deliverable_paths`
  # declares. That is one clause-requiring offer; the live tree has eight.
  expect_fail "an offer that drops <merge-clause> is rejected" 11 \
    "sed -i.bak 's| <merge-clause>||' $(cmd_file $PLUGIN_REL alpha)"
  # The PER-COMMAND coverage guard. Rewording one family command's handoff sentence empties its
  # writer set alone, and every offer that command makes stops being checked while the run-wide
  # assertions stay satisfied by the other family commands -- green, and quietly covering less.
  # This mutation is the one a review demonstrated against the live tree on prd-ground.md.
  expect_fail "a family command whose handoff declares no path is rejected" 11 \
    "sed -i.bak 's|\`deliverable_paths\` = |\`deliverable_paths\` lists |' $(cmd_file $PLUGIN_REL alpha)"
  # The three vacuity guards rewrite through a temp file OUTSIDE the reference dir rather than
  # with `sed -i.bak`: a stray `.bak` there is a file `find $REF_DIR -type f` counts, so the
  # mutation would trip check 9's reference-file count too and blur what the case proves.
  # The three vacuity guards. Each leaves the tree otherwise valid and makes the check examine
  # nothing, which must be RED: a gate that has stopped being able to fail proves nothing green.
  expect_fail "a reworded family-scope sentence is rejected" 11 \
    "sed 's|/${PLUGIN_REL##*/}:alpha\*|the family|' $PLUGIN_REL/$REF_DIR/next-phase-offer.md > np.tmp && mv np.tmp $PLUGIN_REL/$REF_DIR/next-phase-offer.md"
  # ...and the PAIR that discriminates the scope-paragraph anchor from whole-file `head -1`.
  # Neither case proves anything alone. RED: the scope sentence is reworded away AND a stray
  # `$qual<family>*` phrase is added under another heading -- exactly the `## Not pipeline
  # nodes` shape the live reference carries. Under `head -1` the stray stands in for the
  # reworded sentence and the tree comes back green, so this case FAILs; anchored, the glob
  # empties and check 11 fires. GREEN: a stray phrase naming a DIFFERENT family, placed
  # BEFORE the scope paragraph so `head -1` would reach it first. Under `head -1` the glob
  # becomes `zulu*`, which matches no command, and this case goes red; anchored, the scope
  # paragraph still wins and the tree stays green. Verified red before / green after by
  # stashing scope_family.
  expect_fail "a reworded scope sentence is rejected even with a stray family phrase elsewhere" 11 \
    "sed 's|^\*\*Where this rule applies:.*|**Where this rule applies:** every offer this plugin prints.|' $PLUGIN_REL/$REF_DIR/next-phase-offer.md > np.tmp && mv np.tmp $PLUGIN_REL/$REF_DIR/next-phase-offer.md && printf -- '\n## Not pipeline nodes\n\n\`/${PLUGIN_REL##*/}:alpha*\` prints no offer.\n' >> $PLUGIN_REL/$REF_DIR/next-phase-offer.md"
  expect_pass_after "a stray family phrase under another heading does not become the family" \
    "{ printf -- '## Not pipeline nodes\n\n\`/${PLUGIN_REL##*/}:zulu*\` prints no offer.\n\n'; cat $PLUGIN_REL/$REF_DIR/next-phase-offer.md; } > np.tmp && mv np.tmp $PLUGIN_REL/$REF_DIR/next-phase-offer.md"
  expect_fail "a family glob matching no command is rejected" 11 \
    "sed 's|alpha\*|zulu*|' $PLUGIN_REL/$REF_DIR/next-phase-offer.md > np.tmp && mv np.tmp $PLUGIN_REL/$REF_DIR/next-phase-offer.md"
  expect_fail "a row-F table with no gated artifact is rejected" 11 \
    "sed '/alpha-deliverable.md/d; /alpha-two-out.md/d; /elsewhere.md/d' $PLUGIN_REL/$REF_DIR/phase-handoff.md > ph.tmp && mv ph.tmp $PLUGIN_REL/$REF_DIR/phase-handoff.md"
  # ...and the other half of the assertion: the clause is required only where the offering run
  # writes what the offered command gates. `/dev-workflows:sigma` gates `elsewhere.md`, which no
  # fixture command declares, so a clause-free offer of it is CORRECT and must stay green. Without
  # the writer test -- a check that simply demanded the placeholder on every offer -- this case
  # goes red. Verified red before / green after by stashing the writer test.
  expect_pass_after "a clause-free offer of a command this run does not feed is accepted" \
    "printf -- '\nchoices: [\"Hand to the ungated consumer — /${PLUGIN_REL##*/}:sigma <KEY>\", \"Stop here\"]\n' >> $(cmd_file $PLUGIN_REL alpha)"

  # ...and the PAIR that discriminates "returns every glob on the line" from "returns the
  # first glob on the line", now that the line can name more than one. This is the live shape
  # /product-workflows:prd-ground took: it left the `brd-*` family the rename made it stop
  # matching, but next-phase-offer.md's scope line still has to bind it, under a SECOND glob
  # on the same line, because it still prints an offer whose downstream command's
  # require-on-main gate this same run feeds. `nu-ground` here plays that role -- it matches
  # ONLY the second glob (`nu-*`), never the first (`alpha*`), so an implementation that reads
  # both globs but stops at the first would never even put it in route_n, and its missing
  # <merge-clause> would never be checked.
  #
  # RED: the scope line names both `alpha*` and `nu-*`, `nu-ground` offers the gated consumer
  # `/omega` (declaring the same `alpha-deliverable.md` `omega`'s row-F entry targets) with NO
  # <merge-clause>. Under today's fixed scope_family this fires; under the retired
  # first-glob-only form it does not, because `nu-ground` never enters `route_n` at all and the
  # tree comes back green -- verified directly against a scratch copy of the old
  # `head -1`-after-extraction implementation before this pair was added. GREEN: the same
  # fixture with the placeholder present. The pair is required, not optional: an
  # implementation that reads both globs but only ever CHECKS the first passes the green case
  # for the wrong reason (there is nothing there to catch either way), and only the red case
  # discriminates.
  expect_fail "a command matched only by the scope line's SECOND glob with no <merge-clause> is rejected" 11 \
    "sed 's|^\*\*Where this rule applies:.*|& The \`/${PLUGIN_REL##*/}:nu-*\` command carries the same convention under its own glob: it prints an offer naming a downstream command whose require-on-main gate this same run feeds.|' $PLUGIN_REL/$REF_DIR/next-phase-offer.md > np.tmp && mv np.tmp $PLUGIN_REL/$REF_DIR/next-phase-offer.md && printf -- '---\nname: nu-ground\ndescription: A fixture command in a second glob family, disjoint from alpha*.\n---\n\nOn the first choice, execute \`handoff-to-main\` with \`deliverable_paths\` = \`alpha-deliverable.md\`,\nand \`title: nu-ground fixture handoff\`.\n\n\`\`\`\nchoices: [\"Run the gated consumer — /${PLUGIN_REL##*/}:omega <KEY> (Recommended)\", \"Stop here\"]\n\`\`\`\n' > $(cmd_file $PLUGIN_REL nu-ground) && printf -- '# /nu-ground\n\nA fixture command page for the second check-11 family.\n' > $PLUGIN_REL/docs/$DOC_CMD_DIR/nu-ground.md && printf -- '\n- [\`/nu-ground\`]($DOC_CMD_DIR/nu-ground.md)\n' >> $PLUGIN_REL/docs/README.md && sed -i.bak 's|two slash commands|three slash commands|' $PLUGIN_REL/README.md && printf -- '\nCommand: \`/nu-ground\`.\n' >> $PLUGIN_REL/README.md && printf -- '\n\`\`\`mermaid\nflowchart TD\n    n[\"/nu-ground\"]\n\`\`\`\n' >> $PLUGIN_REL/docs/workflow.md && ns_map_regen"
  expect_pass_after "the same second-glob-only command is accepted once its offer carries <merge-clause>" \
    "sed 's|^\*\*Where this rule applies:.*|& The \`/${PLUGIN_REL##*/}:nu-*\` command carries the same convention under its own glob: it prints an offer naming a downstream command whose require-on-main gate this same run feeds.|' $PLUGIN_REL/$REF_DIR/next-phase-offer.md > np.tmp && mv np.tmp $PLUGIN_REL/$REF_DIR/next-phase-offer.md && printf -- '---\nname: nu-ground\ndescription: A fixture command in a second glob family, disjoint from alpha*.\n---\n\nOn the first choice, execute \`handoff-to-main\` with \`deliverable_paths\` = \`alpha-deliverable.md\`,\nand \`title: nu-ground fixture handoff\`.\n\n\`\`\`\nchoices: [\"Run the gated consumer — /${PLUGIN_REL##*/}:omega <KEY> (Recommended) <merge-clause>\", \"Stop here\"]\n\`\`\`\n' > $(cmd_file $PLUGIN_REL nu-ground) && printf -- '# /nu-ground\n\nA fixture command page for the second check-11 family.\n' > $PLUGIN_REL/docs/$DOC_CMD_DIR/nu-ground.md && printf -- '\n- [\`/nu-ground\`]($DOC_CMD_DIR/nu-ground.md)\n' >> $PLUGIN_REL/docs/README.md && sed -i.bak 's|two slash commands|three slash commands|' $PLUGIN_REL/README.md && printf -- '\nCommand: \`/nu-ground\`.\n' >> $PLUGIN_REL/README.md && printf -- '\n\`\`\`mermaid\nflowchart TD\n    n[\"/nu-ground\"]\n\`\`\`\n' >> $PLUGIN_REL/docs/workflow.md && ns_map_regen"

  # ---- check 11 with BOTH its references in another plugin ----
  # The shape after the reference corpus is extracted: next-phase-offer.md (the family and the
  # placeholder) and phase-handoff.md (the row-F target table) in one plugin, the commands that
  # make the offers in another. The GREEN case is the one that discriminates, and it has to be
  # here: every red case below is also red under an implementation that never learned to look
  # in $CORE_PLUGIN_REL, because a reference it cannot find is reported as a MISSING reference
  # -- itself a check-11 failure. Only a correct cross-plugin tree that must come back green
  # separates "resolves the reference elsewhere" from "cannot find it and says so".
  expect_pass_after_env "the tree stays green with the merge-clause references in another plugin" \
    "CORE_PLUGIN_REL=plugins/fixture-core" \
    "relocate_corpus"
  expect_fail_env "an offer that drops <merge-clause> is rejected with the references in another plugin" 11 \
    "CORE_PLUGIN_REL=plugins/fixture-core" \
    "relocate_corpus && sed -i.bak 's| <merge-clause>||' $(cmd_file $PLUGIN_REL alpha)"
  # ...and the vacuity guard, which is the property most easily lost in a cross-plugin rewrite:
  # a relation that comes up empty must still FAIL rather than quietly narrowing the check's
  # surface. Emptying the RELOCATED row-F table proves the target relation is still asserted
  # after it stopped living next to the commands it describes.
  expect_fail_env "a relocated row-F table with no gated artifact is rejected" 11 \
    "CORE_PLUGIN_REL=plugins/fixture-core" \
    "relocate_corpus && sed '/alpha-deliverable.md/d; /alpha-two-out.md/d; /elsewhere.md/d' plugins/fixture-core/$REF_DIR/phase-handoff.md > ph.tmp && mv ph.tmp plugins/fixture-core/$REF_DIR/phase-handoff.md"
  # ...and the vacuity guard for the CORE_PLUGIN_REL config itself, which is a failure mode the
  # variable CREATES: the corpus moves and the config is not repointed at it. No env override
  # here -- that is the point. A missing reference must stay a FAILURE rather than degrade to a
  # skip, or a mis-set corpus path silences this check for the whole run and every offer in the
  # tree stops being examined while the build stays green.
  expect_fail "a corpus CORE_PLUGIN_REL does not point at is rejected" 11 "relocate_corpus"

  # Check 12 -- one case per failure mode, plus the bracket-matching case that is the whole
  # reason this check parses rather than regexes. A naive non-greedy `\[(.*?)\]` stops at the
  # `]` inside the option text and skips the array entirely, so an over-long array hidden
  # behind one would pass. That is not hypothetical: the census that motivated check 12 used
  # the naive form and missed three live arrays, two of them six-option.
  expect_fail "a five-option choices array is rejected" 12 \
    "printf -- '\nchoices: [\"One\", \"Two\", \"Three\", \"Four\", \"Five\"]\n' >> $(cmd_file $PLUGIN_REL alpha)"
  expect_fail "a one-option choices array is rejected" 12 \
    "printf -- '\nchoices: [\"Only one\"]\n' >> $(cmd_file $PLUGIN_REL alpha)"
  expect_fail "an authored Other option is rejected" 12 \
    "printf -- '\nchoices: [\"One\", \"Two\", \"Other… (describe)\"]\n' >> $(cmd_file $PLUGIN_REL alpha)"
  expect_fail "an over-long array whose option text contains brackets is rejected" 12 \
    "printf -- '\nchoices: [\"Use <dir> [+ <sub>]\", \"Two\", \"Three\", \"Four\", \"Five\"]\n' >> $(cmd_file $PLUGIN_REL alpha)"
  # ...and the matching green case: a LEGAL array whose option text contains brackets must not
  # be flagged. Together with the case above this proves the parser reads such arrays rather
  # than skipping them -- a skipping parser passes this one and the one above for the same
  # wrong reason.
  expect_pass_after "a four-option array whose option text contains brackets is accepted" \
    "printf -- '\nchoices: [\"Use <dir> [+ <sub>]\", \"Two\", \"Three\", \"Four\"]\n' >> $(cmd_file $PLUGIN_REL alpha)"

  # Check 13 -- vendor-token quarantine. Four cases, in two discriminating pairs. The first
  # pair proves the check fires on an unmarked vendor name and stays quiet on a marked one --
  # a check with no working marker would fail the green case, and one that matched nothing
  # would pass both. The second pair is the FENCE rule, and it is the pair that matters: a
  # naive implementation that simply skipped fenced blocks passes the marked-fence case and
  # the plain-token case for the same wrong reason, and would let a tracker-shaped field hide
  # in exactly the templates and handoff blocks this plugin is full of. Only the unmarked-fence
  # red case separates "the marker sanctions this block" from "fenced code is not scanned".
  #
  # The token list itself is a constant of THIS file, and --selftest only ever mutates a copy
  # of the fixture tree -- so its vacuity guard, like check 5's RUNTIME_VARS tripwire above,
  # is verified out-of-band (empty VENDOR_TOKENS in a copy of this script, run against any
  # tree, see check 13 fail) rather than by a case here.
  expect_fail "an unmarked vendor token is rejected"          13 \
    "printf -- '\nThe run reads the Jira ticket it was handed.\n' >> $(cmd_file $PLUGIN_REL alpha)"
  expect_pass_after "a marked vendor token is accepted" \
    "printf -- '\nQuoting a repo convention: \`<JIRA-ISSUE-KEY>\` <!-- vendor-token-ok: fixture quote -->\n' >> $(cmd_file $PLUGIN_REL alpha)"
  expect_fail "a vendor token in an UNMARKED fenced block is rejected" 13 \
    "printf -- '\n\`\`\`text\n<name>/<JIRA-ISSUE-KEY>-<slug>\n\`\`\`\n' >> $(cmd_file $PLUGIN_REL alpha)"
  expect_pass_after "a vendor token in a MARKED fenced block is accepted" \
    "printf -- '\n\`\`\`text <!-- vendor-token-ok: fixture quote -->\n<name>/<JIRA-ISSUE-KEY>-<slug>\n\`\`\`\n' >> $(cmd_file $PLUGIN_REL alpha)"
  # The scan covers every TEXT file under the plugin, not just *.md -- a tracker name
  # leaks as readily through a hook script or a config file as through prose. Each red
  # case is PAIRED with a green one in the same file: an implementation that widened the
  # file set but dropped the marker logic outside markdown would pass every red case and
  # fail every green one, so only the pair discriminates.
  expect_fail "an unmarked vendor token in a HOOK SCRIPT is rejected" 13 \
    "printf -- '\n# The hook reads the Jira ticket key from the branch.\n' >> $PLUGIN_REL/hooks/notify-fixture.sh"
  expect_pass_after "a marked vendor token in a hook script is accepted" \
    "printf -- '\n# Matching a foreign branch convention: JIRA-123  # vendor-token-ok: fixture quote\n' >> $PLUGIN_REL/hooks/notify-fixture.sh"
  expect_fail "an unmarked vendor token in a CONFIG file is rejected" 13 \
    "printf -- '\n# jira rates go here\n' >> $PLUGIN_REL/references/cost-prices.yaml"
  expect_pass_after "a marked vendor token in a config file is accepted" \
    "printf -- '\n# quoting a foreign key shape: JIRA-1  # vendor-token-ok: fixture quote\n' >> $PLUGIN_REL/references/cost-prices.yaml"

  # Check 16 -- the loader contract. The UNMUTATED fixture already exercises three of the
  # five relations and is the only place two of them are proven: fixture-two/$CMD_DIR/omega
  # carries the preamble and makes a real loader call (relations 1 and 3, green), and the
  # corpus is reached through BOTH non-loader citation forms -- `gamma.md` by the bare
  # backticked form ALONE and `handoff/one.md`, `handoff/two.md` and
  # `model-routing/classification.md` by the ${CLAUDE_PLUGIN_ROOT} form alone. An
  # implementation that counted only the loader `args:` string, or only two of the three
  # forms, turns the baseline case red rather than needing a case of its own.
  #
  # Every mutation below rewrites through a temp file rather than with `sed -i.bak`, and that
  # is not style: this check walks every file under $CMD_DIR/, agents/ and $REF_DIR/, so a
  # `.bak` sibling still carrying the citation or the call the case just removed keeps the
  # relation satisfied and the case passes for the wrong reason. Two of these cases were
  # written with `-i.bak` first and came back green against a deliberately broken tree.
  expect_fail "an unresolvable loader argument is rejected" 16 \
    "sed 's|args: \"phase-handoff\"|args: \"no-such-reference\"|' plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX > c16.tmp && mv c16.tmp plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX"
  # THE DISCRIMINATOR for the forward direction. A second argument is an entry point WITHIN
  # the reference, not part of its name, and nearly half of the live tree's real invocations
  # carry one -- check 16's own header holds the count, and is the one place it is written. An
  # implementation matching the whole argument string passes both red cases above and
  # below and fails only this one.
  expect_pass_after "the two-argument entry-point form resolves on its first token" \
    "sed 's|args: \"phase-handoff\"|args: \"phase-handoff handoff-to-main\"|' plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX > c16.tmp && mv c16.tmp plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX"
  # ...and the extension guard, which points the OTHER way and was wrong here first. The
  # skill body reads `${CLAUDE_PLUGIN_ROOT}/references/<the first argument>.md`, appending
  # `.md` UNCONDITIONALLY, so an argument naming the corpus's one non-markdown member reads
  # cost-prices.yaml.md and finds nothing. This case used to assert the opposite and pass,
  # which made the gate and the runtime it gates state contradictory contracts -- latent,
  # because no live argument carries an extension, and durable, because a green case pinned
  # it. The pressure to namespace that data file alongside its cost-emission.md neighbour
  # recurs every time someone applies the citation convention uniformly; this is what now
  # meets it. The CITATION path stays extension-tolerant -- `<core>:cost-prices.yaml` in
  # prose names a real corpus member -- and the two resolvers must stay separate.
  expect_fail "a loader argument carrying its own extension is rejected" 16 \
    "printf -- '\nPrices come from \`Skill(skill: \"dev-workflows:reference\", args: \"cost-prices.yaml\")\`.\n' >> plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX"
  # The REVERSE direction. gamma.md is reached by exactly one citation -- the bare backticked
  # form in alpha -- so demoting it to a prose name leaves the reference unreached. This is
  # also what proves the reverse direction is not satisfied by a mere mention: the file name
  # still appears on the line, without the form that resolves it.
  expect_fail "a core reference nothing cites is rejected" 16 \
    "sed 's|\`references/gamma.md\`|the gamma reference|' $(cmd_file $PLUGIN_REL alpha) > c16.tmp && mv c16.tmp $(cmd_file $PLUGIN_REL alpha)"
  # ...and the two citation forms, separately. gamma.md is reached by the BARE backticked form
  # alone and handoff/one.md by the ${CLAUDE_PLUGIN_ROOT} form alone, so each case converts one
  # to the other and must stay green. An implementation that dropped either form turns the
  # unmutated fixture red; these two make WHICH form was dropped attributable.
  expect_pass_after "the plugin-root citation form reaches a reference" \
    "sed 's|\`references/gamma.md\`|\`\${CLAUDE_PLUGIN_ROOT}/references/gamma.md\`|' $(cmd_file $PLUGIN_REL alpha) > c16.tmp && mv c16.tmp $(cmd_file $PLUGIN_REL alpha)"
  expect_pass_after "the bare backticked citation form reaches a reference" \
    "sed 's|\`\${CLAUDE_PLUGIN_ROOT}/references/handoff/one.md\`|\`references/handoff/one.md\`|' $(cmd_file $PLUGIN_REL alpha) > c16.tmp && mv c16.tmp $(cmd_file $PLUGIN_REL alpha)"
  # Relation 3, and its SCOPE, which is the half a red case cannot prove. Measured on the
  # live tree, and counted in check 16's own header, the one place those figures are
  # written: within $CMD_DIR/, agents/ and $REF_DIR/ the match is exact -- every file that
  # cites a core reference carries the preamble -- while dozens of files OUTSIDE them cite
  # one -- docs pages and a shell hook -- and none of them should carry a runtime loader
  # instruction. An implementation reading "every file that cites" fires once for each of
  # them on a correct tree; here it turns the green case red.
  expect_fail "a consuming file that cites core without the preamble is rejected" 16 \
    "sed '/^\*\*Core references\.\*\*/d' plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX > c16.tmp && mv c16.tmp plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX"
  expect_pass_after "a docs page citing core without the preamble is accepted" \
    "printf -- '\nThis page describes what \`dev-workflows:phase-handoff\` does, for a reader.\n' >> plugins/fixture-two/docs/$DOC_CMD_DIR/omega.md"
  # Relation 4 -- the fence, earned rather than designed: a fix round put a loader call
  # inside a report TEMPLATE, a block the command prints to the user, where it would be read
  # as text and never executed. It is invisible to every other relation, because the call is
  # well-formed and its argument resolves. The GREEN case is what discriminates: a checker
  # that simply ignores fenced content passes neither, but one that flags any core mention
  # inside a fence passes the red case and breaks on the bare tokens that correctly sit in
  # report templates today.
  expect_fail "a loader call inside a fenced block is rejected" 16 \
    "printf -- '\n\`\`\`text\nSkill(skill: \"dev-workflows:reference\", args: \"phase-handoff\")\n\`\`\`\n' >> plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX"
  expect_pass_after "a bare core reference NAME inside a fenced block is accepted" \
    "printf -- '\n\`\`\`text\nHandoff: per dev-workflows:phase-handoff, <outcome>\n\`\`\`\n' >> plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX"
  # Relation 5 -- the wrong-plugin path, which is the defect the loader exists to prevent and
  # the one every other relation is silent on: the call is not a loader call, the file is
  # reached by core's own citations anyway, and the citing file carries the preamble. Both
  # path forms get a red case, because they fail for different reasons -- ${CLAUDE_PLUGIN_ROOT}
  # opens nothing in the reading plugin, while the bare form sends a READER to the wrong
  # directory -- and an implementation covering one and not the other passes half the suite.
  expect_fail "a consumer citing a core reference by plugin-root path is rejected" 16 \
    "printf -- '\nLoad \`\${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md\` directly.\n' >> plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX"
  expect_fail "a consumer citing a core reference by bare path is rejected" 16 \
    "printf -- '\nSee \`references/phase-handoff.md\`.\n' >> plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX"
  # ...and the two greens, which are what keep it from being a check on the two path forms
  # themselves. Inside core those SAME forms are correct and are what relation 2 counts, so
  # an implementation that flagged them everywhere turns the whole corpus red.
  expect_pass_after "a core-internal citation by the same path form is accepted" \
    "printf -- '\nSee \`\${CLAUDE_PLUGIN_ROOT}/references/cost-emission.md\`.\n' >> $PLUGIN_REL/$REF_DIR/gamma.md"
  # give_two_refs is what makes the green cases possible at all: dropping a reference file
  # into a plugin with no references/ tree reddens check 4 (no inventory row), check 3 (the
  # new index page is unreachable) and check 9 (no file-count sentence), none of which is the
  # case being made. It gives fixture-two the minimum tree those three demand, with the count
  # DERIVED from what it just wrote.
  give_two_refs() { # <reference-basename>... -- run from inside the copied tree
    local f
    mkdir -p "plugins/fixture-two/$REF_DIR" "plugins/fixture-two/docs/reference"
    for f in "$@"; do printf -- '# %s (fixture copy)\n' "$f" > "plugins/fixture-two/$REF_DIR/$f"; done
    { printf -- '# References\n\n'
      for f in "$@"; do printf -- '- `%s`\n' "$f"; done
      printf -- '\nThe fixture ships %s files.\n' "$(find "plugins/fixture-two/$REF_DIR" -type f | wc -l | tr -d ' ')"
    } > plugins/fixture-two/docs/reference/references.md
    printf -- '\n- [References](reference/references.md)\n' >> plugins/fixture-two/docs/README.md
  }

  # ...and the own-reference carve-out: only a name that belongs to core and NOT to the
  # citing plugin fires. give_two_refs gives fixture-two a cost-emission.md of its own, after
  # which its plugin-root citation of that name is unambiguous and correct. Without the
  # carve-out this case goes red, and so would every future consumer that legitimately ships
  # a reference whose basename core also uses.
  expect_pass_after "a consumer citing a same-named reference IT ships is accepted" \
    "give_two_refs cost-emission.md && printf -- '\nPrices: \`\${CLAUDE_PLUGIN_ROOT}/references/cost-emission.md\`.\n' >> plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX"

  # The vacuity guard. The forward direction reads ONE syntax; a repo-wide rewording of it
  # would leave relations 1 and 4 examining nothing while every message stayed silent. The
  # preamble is the evidence that the syntax is still meant to be in use, so documenting it
  # while calling it nowhere is the state that must be loud.
  expect_fail "a documented loader that is never actually invoked is rejected" 16 \
    "sed '/args: \"phase-handoff\"/d' plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX > c16.tmp && mv c16.tmp plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX"
  # ...and the CORE_PLUGIN_REL vacuity guard, check 16's twin of the ones checks 8 and 11
  # carry: the corpus moved and the config was not repointed at it. No env override here --
  # that is the point. Every loader argument must go on resolving against the CONFIGURED
  # corpus, so a mis-set corpus path is red rather than a silently narrowed check.
  expect_fail "a corpus CORE_PLUGIN_REL does not point at is rejected by check 16" 16 "relocate_corpus"
  # ...and the cross-plugin red, whose green half is the relocation case above: with the
  # corpus in a plugin of its own, an unresolvable argument must still be caught there.
  expect_fail_env "an unresolvable loader argument is rejected with the corpus in another plugin" 16 \
    "CORE_PLUGIN_REL=plugins/fixture-core" \
    "relocate_corpus && sed 's|args: \"phase-handoff\"|args: \"no-such-reference\"|' plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX > c16.tmp && mv c16.tmp plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX"

  # The cost subsystem (check 8, and check 9's cost-emitting-commands sentence) does not
  # exist in every edition -- check_cost_attribution and that half of check_prose_counts
  # both return immediately when HAS_COST=0, so a mutation that only a cost check can see
  # would never trip a failure there and would falsely report this selftest case itself as
  # broken. Everything inside the branch below depends on the cost subsystem being active --
  # every check-8 case (including the emit-cost-call-site field-reorder, which check 8's
  # extractor-coverage assertion alone can see) and every check-9 cost-emitting-count case,
  # cross-plugin ones included. No number is written here: it moved every time a case was
  # added, and every number that had been written -- in this comment and in the skip line
  # below -- disagreed with the block by the time anyone counted it.
  if [ "$HAS_COST" = 1 ]; then
    expect_fail "a drifted emit-cost call site is rejected" 8 "sed -i.bak 's|\`command: /alpha\`, \`phase: fixture-phase\`, \`role: pm\`|\`command: /alpha\`, \`role: pm\`, \`phase: fixture-phase\`|' $(cmd_file $PLUGIN_REL alpha)"
    expect_fail "an unattributed emit-cost call is rejected" 8 "mkdir -p $(dirname $(cmd_file $PLUGIN_REL zeta)) 2>/dev/null; printf -- '---\nname: zeta\n---\n\nCall \`emit-cost\` with \`command: /zeta\`, \`phase: fixture-phase\`, \`role: pm\`, done.\n' > $(cmd_file $PLUGIN_REL zeta) && printf -- '# /zeta\n\nFixture page.\n' > $PLUGIN_REL/docs/$DOC_CMD_DIR/zeta.md && sed -i.bak 's|($DOC_CMD_DIR/alpha.md)|($DOC_CMD_DIR/alpha.md), [\`/zeta\`]($DOC_CMD_DIR/zeta.md)|' $PLUGIN_REL/docs/README.md"
    expect_fail "a section-7 row backed only by look-alike prose is rejected" 8 \
      "sed -i.bak 's|Call \`emit-cost\` with |Recorded as |' $(cmd_file $PLUGIN_REL alpha)"
    expect_fail "a drifted attributed role is rejected"      8 "sed -i.bak 's;| \`/alpha\` | fixture-phase | pm |;| \`/alpha\` | fixture-phase | pe |;' $PLUGIN_REL/$REF_DIR/cost-emission.md"
    expect_fail "a section-7 row for a non-emitting command is rejected" 8 "sed -i.bak 's;| \`/alpha\` | fixture-phase | pm |;| \`/alpha\` | fixture-phase | pm |\n| \`/omega\` | fixture-phase | pm |;' $PLUGIN_REL/$REF_DIR/cost-emission.md"
    expect_fail "a drifted cost-emitting count is rejected"  9 "sed -i.bak 's|One commands emit a cost entry|Five commands emit a cost entry|' $PLUGIN_REL/docs/reference/session-cost.md"

    # ---- checks 8 and 9 with the section-7 table in ANOTHER plugin ----
    # The green cases lead, because they are the ones that discriminate. Every red case here
    # is ALSO red under an implementation that never learned to look in $CORE_PLUGIN_REL: it
    # reports "no section-7 attribution table", which is a check-8 failure of its own. Only a
    # correct cross-plugin tree that must come back GREEN tells the two apart.
    expect_pass_after_env "the tree stays green with the section-7 table in another plugin" \
      "CORE_PLUGIN_REL=plugins/fixture-core" \
      "relocate_corpus"
    # ...and the reverse direction's own green case, which is a different claim. One table
    # attributes the emitters of EVERY plugin in COST_PLUGIN_RELS, so a row belonging to a
    # sibling plugin is correctly attributed and must not fire. A reverse loop that matched
    # each row against only the plugin under check goes red here twice over -- on `/omega`
    # while checking dev-workflows, and on `/alpha` while checking fixture-two.
    expect_pass_after_env "a section-7 table attributing a SECOND plugin's emitter is accepted" \
      "CORE_PLUGIN_REL=plugins/fixture-core COST_PLUGIN_RELS='plugins/dev-workflows plugins/fixture-two'" \
      "relocate_corpus && printf -- '\nCall \`emit-cost\` with \`command: /omega\`, \`phase: fixture-phase\`, \`role: pm\`, done.\n' >> plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX && sed -i.bak 's;| \`/alpha\` | fixture-phase | pm |;| \`/alpha\` | fixture-phase | pm |\n| \`/omega\` | fixture-phase | pm |;' plugins/fixture-core/$REF_DIR/cost-emission.md"
    # The matching reds. The first proves the reverse direction still reads the relocated
    # table; the second proves check 9's cost-emitting count is still ASSERTED once the
    # reference has moved out of the plugin whose page states it -- the count derives from
    # the call sites alone, and gating it on the reference's presence would be applicability
    # inferred from a missing file, silently dropping the assertion for every emitting plugin
    # that is not the corpus. The green case above cannot see that: a check that skips the
    # count passes it too.
    expect_fail_env "a section-7 row for a non-emitting command is rejected with the table in another plugin" 8 \
      "CORE_PLUGIN_REL=plugins/fixture-core" \
      "relocate_corpus && sed -i.bak 's;| \`/alpha\` | fixture-phase | pm |;| \`/alpha\` | fixture-phase | pm |\n| \`/omega\` | fixture-phase | pm |;' plugins/fixture-core/$REF_DIR/cost-emission.md"
    expect_fail_env "a drifted cost-emitting count is rejected with the table in another plugin" 9 \
      "CORE_PLUGIN_REL=plugins/fixture-core" \
      "relocate_corpus && sed -i.bak 's|One commands emit a cost entry|Five commands emit a cost entry|' $PLUGIN_REL/docs/reference/session-cost.md"
    # ...and check 8's half of the CORE_PLUGIN_REL vacuity guard (check 11's twin sits with the
    # merge-clause cases above): the corpus moved and the config was not repointed at it. An
    # absent table must be RED. Degrading it to a skip would silence both directions of check 8
    # for every plugin at once, on nothing louder than a stale config line.
    expect_fail "a corpus CORE_PLUGIN_REL does not point at is rejected by check 8" 8 "relocate_corpus"
  else
    printf 'skip  the cost cases (this edition has no cost subsystem)\n'
  fi

  expect_fail "second plugin's command page is checked too" 4 \
    'rm plugins/fixture-two/docs/commands/omega.md'
  # A plain `[dangling](nowhere.md)` link fires check 1 (missing file), not check 2 --
  # verified empirically while writing this case. A bare #anchor link is what actually
  # exercises the ANCHOR half of check_links_and_anchors (check 2) against the second
  # plugin's docs index, which is the coverage this case's name promises.
  expect_fail "second plugin's docs index is checked too" 2 \
    'printf "\n[dangling](#no-such-heading-here)\n" >> plugins/fixture-two/docs/README.md'

  # check_cost_applicability / check_handoff_applicability guard the QUIET direction: a
  # plugin that ships the CALL SITES but was never added to the declaring list has its check
  # silently skipped -- exactly the state the reviewer proved was invisible by deleting every
  # row from the section-7 table. plugins/fixture-two is a member of neither list, so it is
  # where both directions are exercised; no config edit is needed at runtime.
  #
  # Each direction needs a PAIR. The trigger used to be the reference FILE, and the corpus
  # extraction falsified that premise both ways at once -- the plugin that kept the emitters
  # stopped shipping the reference (assertion goes silent), and the corpus plugin was forced
  # into a list by a file it merely holds (check runs, derives nothing, fails). So the red
  # case alone would be satisfied by the OLD implementation too, wherever the mutation
  # happens to create both; only the green case -- a plugin holding the reference and no call
  # site, which must PASS -- separates a call-site trigger from a file-presence one.
  #

  expect_fail "a plugin with an emit-cost call site undeclared in COST_PLUGIN_RELS is rejected" 8 \
    "printf -- '\nCall \`emit-cost\` with \`command: /omega\`, \`phase: fixture-phase\`, \`role: pm\`, done.\n' >> plugins/fixture-two/$CMD_DIR/omega$CMD_SUFFIX"
  expect_pass_after "a plugin holding cost-emission.md with no emit-cost call site is accepted" \
    "give_two_refs cost-emission.md"
  # The handoff family is qualified by the plugin under check, so the reference has to NAME
  # fixture-two's family before fixture-two can be in it -- which is the real shape: the
  # family belongs to whichever plugin ships those commands, and the reference says so. The
  # phrase is added INSIDE the scope paragraph, because that is the one line scope_family
  # reads; appended anywhere else it would be the stray the anchoring pair above rejects.
  expect_fail "a plugin with a family command undeclared in HANDOFF_PLUGIN_RELS is rejected" 11 \
    "sed 's|^\*\*Where this rule applies:.*|& The \`/fixture-two:omega*\` commands write their offers to the same convention.|' $PLUGIN_REL/$REF_DIR/next-phase-offer.md > np.tmp && mv np.tmp $PLUGIN_REL/$REF_DIR/next-phase-offer.md"
  expect_pass_after "a plugin holding next-phase-offer.md with no family command is accepted" \
    "give_two_refs next-phase-offer.md"

  # Check 17 -- agent dispatch authority (PS15). The baseline fixture already carries the
  # shape both cases below assume: agents/beta.md grants `Task` and carries the exact
  # NEVER-dispatch rule naming `eta`; agents/eta.md talks about "dispatch" in ordinary prose
  # and invokes no subagent, but grants no `Task` in its own tool list (it has no tools: line
  # at all). Each case below mutates exactly one of the two, leaving the other as the
  # untouched Task-carrier that keeps the vacuity guard from firing alongside the real
  # assertion -- the same reason check_cost_attribution's reverse direction needs a run-wide
  # view rather than per-file bookkeeping.
  expect_fail "an agent granted Task with no NEVER-dispatch rule is rejected" 17 \
    "sed -i.bak '/NEVER dispatch any subagent other than/d' $PLUGIN_REL/agents/beta.md"
  expect_fail "an agent carrying the NEVER-dispatch rule without Task is rejected" 17 \
    "printf -- '\n- NEVER dispatch any subagent other than \`beta\`. That one dispatch is your entire \`Task\` authority.\n' >> $PLUGIN_REL/agents/eta.md"
  # THE DISCRIMINATOR. This adds a decoy paragraph to eta.md -- which still carries no
  # tools: line at all -- naming both "dispatch" and a literal quoted \`"Task"\`, the exact
  # substring the tools array uses. An implementation that greps the whole file for either
  # token, rather than scoping `has_task` to the frontmatter tools/allowed-tools line, misreads
  # eta as Task-carrying and then fires the forward-direction failure on a file that grants no
  # such authority -- which is exactly the loose-grep failure mode this check exists to avoid.
  expect_pass_after "prose naming dispatch and a quoted \"Task\" grants no authority" \
    "printf -- '\nA reviewer might dispatch this agent expecting it to \`\"Task\"\` itself out eventually; it never does, and it invokes no subagent either.\n' >> $PLUGIN_REL/agents/eta.md"

  # CHECK 18. The RED case and its GREEN TWIN are the whole point and must be read together:
  # the identical mutation is a failure with ASSERT_PUBLISHED=1 and a PASS without it. A gate
  # that fired on both would be red on every release branch, where an `— Unreleased` section is
  # the correct authoring state; a gate that fired on neither would be inert. Only the pair
  # discriminates, and neither case alone proves the behaviour.
  expect_fail_env "an Unreleased changelog section on a publishing ref is rejected" 18 \
    "ASSERT_PUBLISHED=1" \
    "sed -i.bak 's|^## \[1.1.0\] — 2026-09-22|## [1.1.0] — Unreleased|' $PLUGIN_REL/CHANGELOG.md"
  expect_pass_after "the same Unreleased section is accepted off a publishing ref" \
    "sed -i.bak 's|^## \[1.1.0\] — 2026-09-22|## [1.1.0] — Unreleased|' $PLUGIN_REL/CHANGELOG.md"
  # A dated tree must still PASS with the gate armed -- otherwise the red case above could be
  # passing for any reason at all, including the check firing on every changelog it opens.
  expect_pass_after_env "a fully dated changelog passes with the gate armed" \
    "ASSERT_PUBLISHED=1" \
    "true"
  # The bare Keep-a-Changelog form is deliberately out of scope (see the check's header): this
  # asserts the exclusion rather than leaving it to be re-litigated by the next reader.
  expect_pass_after_env "a bare [Unreleased] heading is out of scope, armed or not" \
    "ASSERT_PUBLISHED=1" \
    "printf -- '\n### [Unreleased] (pre-split history)\n\nA labelled historical section.\n' >> $PLUGIN_REL/CHANGELOG.md"
  # VACUITY GUARD, the same shape as checks 16 and 17 carry: a glob that silently stops matching
  # must turn the build red, not green.
  expect_fail_env "a tree with no changelog at all is rejected when armed" 18 \
    "ASSERT_PUBLISHED=1" \
    "rm -f plugins/*/CHANGELOG.md"

  # CHECK 19. Every case sets EDITION_FORBIDDEN_B64 itself, to a fixture token, so the suite
  # asserts the same thing in every edition -- including the internal one, whose own value is
  # empty and would otherwise leave the red cases nothing to fire on. The token is written
  # through the decoder, as check 14's cases write theirs. The RED case and its GREEN TWIN
  # carry the identical token and differ only in the file it lands in; an implementation that
  # ignored the CHANGELOG.md exemption passes the red case and fails the green one, and one
  # that exempted everything passes the green case and fails the red.
  local ef="EDITION_FORBIDDEN_B64=enotZWRpdGlvbi1mb3JiaWRkZW4tZml4dHVyZS10b2tlbg=="
  expect_fail_env "an edition-forbidden token in a docs page is rejected" 19 "$ef" \
    "printf '%s\n' \"\$(b64d enotZWRpdGlvbi1mb3JiaWRkZW4tZml4dHVyZS10b2tlbg==)\" >> $PLUGIN_REL/docs/README.md"
  expect_pass_after_env "the same token in a CHANGELOG.md is accepted" "$ef" \
    "printf '%s\n' \"\$(b64d enotZWRpdGlvbi1mb3JiaWRkZW4tZml4dHVyZS10b2tlbg==)\" >> $PLUGIN_REL/CHANGELOG.md"
  # The edition that forbids nothing: an EMPTY value passes with the token present, which is the
  # internal edition's configuration and the reason the body must tolerate it under set -u.
  expect_pass_after_env "an empty EDITION_FORBIDDEN_B64 passes with the token present" "EDITION_FORBIDDEN_B64=" \
    "printf '%s\n' \"\$(b64d enotZWRpdGlvbi1mb3JiaWRkZW4tZml4dHVyZS10b2tlbg==)\" >> $PLUGIN_REL/docs/README.md"
  # VACUITY GUARD: a value that decodes to nothing must turn the build red, not green.
  expect_fail_env "an undecodable EDITION_FORBIDDEN_B64 is rejected" 19 "EDITION_FORBIDDEN_B64=@@@" "true"
  # The work-tree scope, as a pair: inside a git work tree an UNTRACKED page is still read (a new
  # page must not pass for want of a `git add`), and a git-IGNORED file is not (a main checkout's
  # ignored .worktrees/ copy must not redden it). Needs git; skipped, and said so, without it.
  if command -v git >/dev/null 2>&1; then
    expect_fail_env "an untracked page naming the token inside a git work tree is rejected" 19 "$ef" \
      "git init -q . && printf '%s\n' \"\$(b64d enotZWRpdGlvbi1mb3JiaWRkZW4tZml4dHVyZS10b2tlbg==)\" >> $PLUGIN_REL/docs/README.md"
    expect_pass_after_env "a git-ignored file naming the token is accepted" "$ef" \
      "git init -q . && printf 'ignored-copy/\n' > .gitignore && mkdir ignored-copy && printf '%s\n' \"\$(b64d enotZWRpdGlvbi1mb3JiaWRkZW4tZml4dHVyZS10b2tlbg==)\" > ignored-copy/page.md"
  else
    printf 'skip  check 19 work-tree scope cases: git not found\n'
  fi

  if [ "$rc" -eq 0 ]; then echo "SELFTEST PASS"; else echo "SELFTEST FAIL"; fi
  exit "$rc"
}

# ------------------------------------------------------------------ check 12
# Every `choices:` array the plugin writes is an AskUserQuestion call, and that
# tool's schema is `minItems: 2, maxItems: 4` with "There should be no 'Other'
# option, that will be provided automatically". A five-option array is not a long
# prompt -- it is a tool call rejected at validation, so the run cannot present it
# at all, while `escalation-rules.md` simultaneously requires the array be shown
# verbatim. That contradiction shipped: a convention stated in nine command files
# ("last choice is always \"Other... (describe)\"") authored 136 duplicate options
# across 30 files and pushed 42 arrays past the cap.
#
# The parser is bracket-matched and quote-aware, NOT a non-greedy regex. A naive
# `choices:\s*\[(.*?)\]` stops at the first `]` -- including one inside an option
# string ("Use <PRD dir> [+ <Epic subdir>]") -- and silently skips that array.
# The census that motivated this check used the naive form and missed three
# arrays, two of them six-option ones. A checker that cannot see the worst
# offenders is worse than none, so this one matches brackets.
#
# CHANGELOG.md is excluded: it quotes retired arrays as history.
#
# What this CANNOT see, stated so nobody mistakes green for safe: an array built
# at runtime from a directory listing -- the Epic picker `/specify`, `/design`
# and `/implement` share -- has no literal options to count. Its cap lives in
# `references/epic-picker.md` (*The cap*) and is held by review, not by this gate.
check_choices_arity() {
  local root="$1" hits
  hits=$(python3 - "$root/$PLUGIN_REL" <<'PYEOF'
import re, sys, io, glob, os
root = sys.argv[1]
START = re.compile(r'choices:\s*\[')
def arrays(text):
    for m in START.finditer(text):
        i = m.end() - 1
        depth = 0; j = i; inq = False; esc = False; opts = []; cur = None
        while j < len(text):
            c = text[j]
            if inq:
                if esc: esc = False; cur.append(c)
                elif c == '\\': esc = True
                elif c == '"': inq = False; opts.append(''.join(cur)); cur = None
                else: cur.append(c)
            else:
                if c == '"': inq = True; cur = []
                elif c == '[': depth += 1
                elif c == ']':
                    depth -= 1
                    if depth == 0:
                        yield (m.start(), opts); break
                elif text[j:j+2] == '\n\n': break
            j += 1
for f in sorted(glob.glob(os.path.join(root, '**', '*.md'), recursive=True)):
    if os.path.basename(f) == 'CHANGELOG.md': continue
    s = io.open(f, encoding='utf-8').read()
    rel = os.path.relpath(f, os.path.dirname(root.rstrip('/')))
    for start, opts in arrays(s):
        if not opts: continue
        n = s[:start].count('\n') + 1
        if len(opts) > 4:
            print("%s:%d has %d options (AskUserQuestion renders at most 4)" % (rel, n, len(opts)))
        if len(opts) < 2:
            print("%s:%d has %d option(s) (AskUserQuestion needs at least 2)" % (rel, n, len(opts)))
        for o in opts:
            if o.strip().lower().startswith('other'):
                print("%s:%d authors its own \"%s\" option (the harness supplies it)" % (rel, n, o[:40]))
PYEOF
)
  [ -n "$hits" ] || return 0
  local h; while IFS= read -r h; do [ -n "$h" ] && fail 12 "$h"; done <<<"$hits"
}

# ------------------------------------------------------------------ check 13
# Vendor-token quarantine. Vendor neutrality is a HARD constraint of this plugin -- one
# markdown tree is the system of record and no tracker is read -- and until this check it
# was held by prose alone. On this codebase that is the losing side of a settled bet: every
# rule enforced by a check has survived, every rule enforced by prose has drifted. It had
# drifted here too. The measurement that motivated this check found THREE live sites where
# the plugin was speaking a vendor's language about its own behaviour: the plugin README
# claiming `/ready` "verify a Jira status" (it is artifact-anchored and reads no tracker),
# and two on `docs/commands/vuln.md` calling `/vuln`'s optional ADDRESS -- a key resolved
# against $SPECS_PATH, as that command's own Step 1 says -- a "Jira ID" and a "Jira ticket".
# All three were fixed in the commit that added this check.
#
# THE TOKEN SET IS NARROW ON EVIDENCE, and the evidence is recorded here so the obvious
# widening is not re-proposed. Over commands/, references/, agents/, docs/ and skills/ the
# tracker-name set below fires on 13 sites: 3 real defects and 10 correct ones. Adding the
# git-FORGE names (bitbucket, github, gitlab) fires on 70 further sites, EVERY ONE of them
# correct content and NONE of them a defect -- they are host classification (`host ==
# bitbucket.org`), CLI capability facts (`gh` exists, Bitbucket ships none), and hard rules
# forbidding REST calls. A forge is a thing this plugin genuinely stands in front of and must
# name to behave correctly; a tracker is a thing it deliberately does not read. That is the
# same shape of result -- fires only on correct content, catches nothing -- on which check
# 11's widening was measured and rejected twice, so it is rejected here for the same reason.
#
# SCOPE is $PLUGIN_REL plus the repo-root instruction tiers: CLAUDE.md, .claude/rules/*.md and
# docs/maintainers/*.md (the 2026-09-23 split moved CLAUDE.md's area rules and evidence into
# the latter two, and moved text must not escape the gate). The repo-root README stays out: it
# documents the whole marketplace, including a sibling plugin whose SUBJECT is a vendor CLI,
# so vendor names there are its subject matter rather than this plugin's vocabulary -- the
# same reason check 10 leaves that file alone. CLAUDE.md was OUT of scope and is now in, on
# evidence: it DESCRIBES this plugin's behaviour, so it drifts in exactly the way the plugin
# does, and it drifted. While the plugin itself reached ZERO unmarked tracker mentions,
# CLAUDE.md still held ten -- among them `/ready` described as "read-only for Jira status"
# (the very defect this check's header records as fixed, corrected in the README and left
# standing here), `doc-planner` described as synthesising a tracker's data when its own agent
# file says PRD content, and `/update-prd` excluded from a gate because "its base is the Jira
# import" when the command resolves a PRD from the specs tree. A file outside the gate that
# describes the thing inside it is how a constraint comes back. CHANGELOG.md is excluded: it
# is history, and history keeps the words it shipped with.
#
# THE MARKER, `vendor-token-ok:`, predates this check by one user and had no enforcer.
# It sanctions the line it sits on; on a fence-OPENING line it sanctions that fenced block,
# which is the only reachable granularity for a verbatim quote (a repository's own
# CONTRIBUTING.md pattern) or an agent-prompt block, neither of which can carry an HTML
# comment on the offending line without corrupting what it quotes. A fenced block is NOT
# skipped by default -- templates and handoff blocks are exactly where a tracker-shaped
# field would hide -- so the marked/unmarked fence pair is a selftest case.
# Sanctioned users -- 16 marked lines across 8 files, in four kinds. Re-derive with
# `grep -rn --exclude=CHANGELOG.md vendor-token-ok: plugins CLAUDE.md .claude/rules
# docs/maintainers` rather than adjusting the number -- scoped to `plugins`, not to one plugin,
# because six of the sixteen moved into workflows-core with the reference corpus:
#   * recognition (8): branch-naming.md's three quotes of a repository's own convention file
#     plus its fenced verbatim pattern; /vuln's no-address placeholder literals (its prose
#     step, its two handoff blocks) and the docs page mirroring them -- foreign text the
#     plugin MATCHES;
#   * illustration (2): prd-format.md naming one third-party tool to stand for "any tracker
#     a user keeps", which is that paragraph's whole argument, and a user's own frontmatter
#     key the preserve-unknown-keys rule exists to protect;
#   * provenance (1): getting-started.md naming the subject of a sibling plugin dev-workflows
#     does not use;
#   * instruction-file rationale (5): the two explanations of WHY the requirement-ID grammar
#     (docs/maintainers/rationale.md's id-grammar evidence) and the pre-lint autolink detector
#     (CLAUDE.md's key-namespace rule) exist -- both are rules about a tracker's key shape and
#     are unexplainable without naming it; CLAUDE.md's hard-constraint statement of
#     this check's rule, which writes the marker itself; docs/maintainers/rationale.md's check-13
#     evidence, which cites the shipped defects this check was created to remove and cannot
#     quote them otherwise; and .claude/rules/gates.md's check-13 description, which writes
#     the marker itself and its census recipe (the recipe matches its own line).
# Each has to write the vendor's name in order to match, illustrate, or attribute it (a
# fence-opening marker, in the block it opens) except two: CLAUDE.md's hard-constraint
# statement of this check's rule and .claude/rules/gates.md's check-13 description name no
# vendor and are counted because the recipe counts them.
#
# SCOPE IS EVERY TEXT FILE UNDER THE PLUGIN, not just *.md, and the widening was
# measured before it was made. A tracker name leaks as readily through plugin.json's
# user-visible `description` -- the text every installing user reads -- or a hook
# script comment as through prose, which is exactly the argument check 14 makes for
# reading every text file. Scoped to *.md, this check could not see either.
#
# MEASURED: 17 non-.md text files under the plugin (plugin.json, hooks.json, four
# hook scripts, three Python scripts, a statusline script, LICENSE, and the yaml/txt
# under references/), and the widened scan fires on NONE of them. That is the
# evidence the widening rests on -- this repo rejects a widening that fires only on
# correct content (check 11's was measured twice and rejected), and accepts this one
# because it fires on nothing while closing a surface the reasoning always covered.
# Binaries cannot reach awk: `grep -rIl ''` enumerates text files only.
#
# The vendored third-party references under references/api-guidelines/ and
# references/fix-vuln/ are IN scope and always were -- they are markdown. They pass
# because the token set is tracker names only, which a REST-API style guide and an
# NVD reference have no reason to contain. A vendored file that did quote one would
# take the same `vendor-token-ok:` marker as any other quoted foreign text; nothing
# about being vendored exempts it.
#
# What this deliberately does NOT catch, stated so nobody mistakes green for safe: it matches
# NAMES, so a tracker-shaped CONCEPT wearing a neutral name -- a `team:` field an Epic no
# longer carries, an import ladder -- is invisible to it. That half is review's.
VENDOR_TOKENS="jira atlassian confluence clickup trello asana youtrack redmine servicenow"

check_vendor_tokens() {
  local root="$1" p="$1/$PLUGIN_REL" files hits h
  [ -n "$VENDOR_TOKENS" ] \
    || { fail 13 "VENDOR_TOKENS is empty -- this check would examine nothing"; return; }
  # EVERY text file under the plugin, not just *.md. `grep -rIl ''` lists text files and
  # skips binaries by -I, so a compiled artifact or an image cannot reach awk. CHANGELOG.md
  # stays excluded, as history.
  files=$(grep -rIl '' "$p" 2>/dev/null | grep -v '/CHANGELOG\.md$' | sort)
  # The repo-root instruction tiers: CLAUDE.md, its path-scoped rules and the rationale they
  # link to. Text moved between them by the 2026-09-23 split stays under this check.
  local extra
  for extra in "$root/CLAUDE.md" "$root"/.claude/rules/*.md "$root"/docs/maintainers/*.md; do
    [ -f "$extra" ] && files=$(printf '%s\n%s\n' "$files" "$extra")
  done
  [ -n "$files" ] \
    || { fail 13 "no markdown under $PLUGIN_REL to scan -- this check would examine nothing"; return; }
  hits=$(while IFS= read -r f; do
           [ -n "$f" ] || continue
           awk -v FILE="${f#$root/}" -v TOKENS="$VENDOR_TOKENS" '
             BEGIN { nt = split(TOKENS, tok, " ") }
             {
               marked  = (index($0, "vendor-token-ok:") > 0)
               isfence = ($0 ~ /^[ \t]*(```|~~~)/)
               # A fence-opening line carrying the marker sanctions the block it opens; the
               # closing fence clears it. Order matters: the state is updated BEFORE the
               # skip tests, so the opening line itself is covered by its own marker.
               if (isfence) {
                 if (infence) { infence = 0; fok = 0 } else { infence = 1; fok = marked }
               }
               if (marked) next
               if (infence && !isfence && fok) next
               low = tolower($0)
               for (i = 1; i <= nt; i++)
                 if (index(low, tok[i])) { printf "%s:%d names \"%s\"\n", FILE, NR, tok[i]; break }
             }' "$f"
         done <<<"$files")
  [ -n "$hits" ] || return 0
  while IFS= read -r h; do
    [ -n "$h" ] && fail 13 "$h -- vendor neutrality is a hard constraint of this plugin; if the name is foreign text being matched, quoted, or attributed rather than this plugin's own vocabulary, mark the line (or its opening fence) \`<!-- vendor-token-ok: <why> -->\`"
  done <<<"$hits"
}

# ------------------------------------------------------------------ check 14
# Foreign-identity quarantine, REPO-WIDE. The organisation this plugin was extracted from
# must never be named anywhere in this repository -- not in the plugin, not in CLAUDE.md,
# not in a script, not in the CHANGELOG. That is a hard constraint of a different kind from
# check 13's: check 13 keeps the plugin from speaking a TRACKER's language about its own
# behaviour, is scoped to $PLUGIN_REL, and has a sanctioning marker because a plugin
# sometimes has to quote foreign text in order to match it. This one has no marker and no
# exception, because there is no legitimate reason to write these names at all.
#
# WHY THE TOKENS ARE ENCODED. A denylist written in clear text would itself put the names
# into the tree, which is the thing being forbidden -- the check would be the only violation
# of the rule it enforces, and `grep -ri` for the names would come back dirty forever after.
# base64 keeps the gate real while leaving the tree clean. It is obfuscation against a
# grep, not against a reader, and it is not pretending otherwise.
#
# SCOPE is the whole repository minus .git, and it reads every text file rather than only
# markdown, because a name leaks as easily through a script comment, a fixture, or a JSON
# description as through prose. The measurement that motivated it: the tree is clean today
# and its git history is clean, so this check has zero live sites -- it exists to keep a
# constraint that currently holds by discipline from quietly stopping to hold. This was
# found by a review that mutated a docs page with the names and watched check 13 pass.
FOREIGN_IDENTITY_B64="KF58W15hLXpBLVowLTldKShzaXplW15hLXpBLVowLTldezAsM31zdHJlYW18YWJ0bykoW15hLXpBLVowLTldfCQp"
FOREIGN_IDENTITY_SAMPLE_B64="QnVpbHQgZm9yIFNpemUgU3RyZWFtIGJ5IEFidG8u"

b64d() { printf '%s' "$1" | base64 -d 2>/dev/null || printf '%s' "$1" | base64 -D 2>/dev/null; }

check_foreign_identity() {
  local root="$1" pat hits
  pat="$(b64d "$FOREIGN_IDENTITY_B64")"
  # A decoder that silently produced nothing would make this check examine nothing while
  # reporting success -- the exact "green by accident" failure the selftest exists to catch.
  [ -n "$pat" ] \
    || { fail 14 "the foreign-identity pattern did not decode -- this check would examine nothing"; return; }
  hits=$(grep -rEinI --exclude-dir=.git -- "$pat" "$root" 2>/dev/null | sed "s|^$root/||" | head -50)
  [ -n "$hits" ] || return 0
  local h; while IFS= read -r h; do
    [ -n "$h" ] && fail 14 "${h%%:*} names the organisation this plugin was extracted from -- that name must appear nowhere in this repository, and there is no sanctioning marker for it"
  done <<<"$hits"
}

# ------------------------------------------------------------------ check 15
# Index membership. Check 4 proves a command HAS a docs page; check 3 proves that page is
# reachable from SOME page. Neither proves the command is findable: a reader looking for it
# arrives through one of three surfaces, and a command can drop out of all three while every
# other check stays green. A review demonstrated exactly that -- it removed /frames from
# the docs index (both places), from the workflow diagram and from the plugin README's role
# table, and the gate passed. The defect that shipped this way was smaller and the same
# shape: /frames reached the workflow page's prose but not its mermaid diagram, under an
# opening sentence promising "every command shown here".
#
# THE THREE SURFACES, and why the diagram is asserted separately from the page: the prose
# below a diagram is where a command lands when someone adds it in a hurry, so asserting
# only "appears in workflow.md" would have passed the very defect this check was written
# for. A node may be written bare (`/idea`) or namespaced (`/docs-workflows:release-notes`),
# so both forms count.
check_index_membership() {
  local root="$1" p="$1/$PLUGIN_REL" n f diagram
  diagram=$(awk '/^```mermaid/{f=1;next} /^```/{f=0} f' "$p/docs/workflow.md" 2>/dev/null)
  [ -n "$diagram" ] \
    || { fail 15 "docs/workflow.md holds no mermaid diagram -- this check would examine nothing"; return; }
  for f in "$p"/commands/*.md; do
    [ -e "$f" ] || continue
    n=$(basename "$f" .md)
    grep -qE "(/|:)$n([^a-zA-Z0-9_-]|\$)" "$p/docs/README.md"   || fail 15 "/$n is not listed in docs/README.md"
    grep -qE "(/|:)$n([^a-zA-Z0-9_-]|\$)" "$p/README.md"        || fail 15 "/$n is not listed in $PLUGIN_REL/README.md"
    printf '%s' "$diagram" | grep -qE "(/|:)$n([^a-zA-Z0-9_-]|\$)" \
      || fail 15 "/$n does not appear in docs/workflow.md's diagram, which says it shows every command (prose below it does not count -- that is where the last one went missing)"
  done
}

# ------------------------------------------------------------------ check 16
# The loader contract. $CORE_PLUGIN_REL holds the shared reference corpus; every other
# plugin reads it through ONE argument-taking skill, because ${CLAUDE_PLUGIN_ROOT} resolves
# to the READING plugin and a dependent plugin therefore cannot open core's files by path.
# One skill instead of one wrapper per reference is a deliberate trade: a typo in an
# argument misfires silently where a named wrapper could not compile. This check is the
# other half of that trade. Without it the loader is a string nothing validates.
#
# FIVE RELATIONS, all derived, none written in here:
#   1. FORWARD  -- every real `args:` string resolves to a file under
#                  $CORE_PLUGIN_REL/$REF_DIR/. The FIRST whitespace token is the reference;
#                  a second token is an entry point WITHIN it (`specs-repo-git
#                  specs-preflight`), and 167 of this tree's 341 real invocations carry one.
#                  An implementation matching the whole argument string reports every one of
#                  them as unresolvable.
#   2. REVERSE  -- every markdown file in the corpus is reached by at least one citation.
#   3. PREAMBLE -- every consuming file that cites a core reference documents the loader
#                  form, so a reader meeting the citation is not left to invent a path.
#   4. FENCE    -- no real loader call sits inside a fenced block.
#   5. WRONG-PLUGIN PATH -- no CONSUMER file cites a core reference by either path form.
#                  ${CLAUDE_PLUGIN_ROOT} resolves to the READING plugin, so that path opens
#                  nothing there, and a bare `$REF_DIR/<name>` sends a reader to a directory
#                  that does not hold the file. This is the defect the loader exists to
#                  prevent -- the class Task 4 swept by hand across 787 sites -- and every
#                  other relation is silent on it: such a citation is not a loader call, its
#                  file is reached by core's own citations anyway, and the citing file
#                  carries the preamble. Only a name that is in core's corpus and NOT in the
#                  citing plugin's own $REF_DIR/ fires, so a plugin shipping its own
#                  `<name>.md` and citing it is never touched; the two trees have zero name
#                  collisions today, which is a fact to re-derive rather than to trust.
#
# THE PLACEHOLDER TRAP, which is the single most likely way to get this wrong. The preamble
# quotes the invocation form literally -- `args: "<name>"` -- as documentation of the
# convention, on 74 files in this tree. A forward direction that resolves every `args:`
# string it finds opens `<name>.md`, fails, and reports 74 defects on entirely correct
# content. A bracketed first token is therefore the PREAMBLE MARKER, not an argument: it is
# what relation 3 looks for, and it is skipped by relations 1 and 4. Anything else that is
# not a plausible reference name is still reported -- skipping "implausible" arguments
# wholesale would let a genuinely malformed one through under the same exemption.
#
# WHY .md IS NOT APPENDED BLINDLY. `cost-prices.yaml` is a data file in the corpus, and the
# pressure to namespace it alongside its `cost-emission.md` neighbour recurs every time
# someone reads the citation convention and applies it uniformly. A token that already
# carries an extension is used as it stands.
#
# RELATION 2 COUNTS THREE CITATION FORMS, NOT TWO, and the third is not optional. A core
# reference is reached by (a) a loader `args:` string from any scanned plugin, (b) a
# `${CLAUDE_PLUGIN_ROOT}/$REF_DIR/<name>` path inside core, or (c) a bare backticked
# `` `$REF_DIR/<name>` `` inside core. Form (c) became unambiguous when the outward-pointing
# bare names were rewritten as `<other-plugin>:<name>`, so inside core that form now means
# core's own file and nothing else. Counting only (a) and (b) reports dependencies.md as
# unreached while grilling-technique.md cites it perfectly well. Requiring a LOADER call
# would be worse still: instruction-file-maintenance.md is cited by impl-maintenance.md
# alone and handoff/code-scanner.md by code-scanner.md alone -- both core-internal, both
# correct, and neither will ever appear in an `args:` string.
#
# SCOPE IS $CMD_DIR/, agents/ and $REF_DIR/, and the bound is measured rather than tasteful.
# THIS HEADER IS THE ONE HOME OF THIS CENSUS. Every figure in it is derived from the scan
# below rather than kept by hand, and .claude/rules/gates.md (§ Check 16) cites this comment
# instead of holding a second copy -- the two copies disagreed for two increments before that.
# Re-derive by instrumenting the scan itself (print real_calls / entry_calls / preamble_files
# after the plugin loop); never adjust a figure by the size of your own change.
#
# Relation 3 over those three directories is an EXACT match on this tree -- 74 files cite a
# core reference, 74 carry the preamble -- while 38 further files cite one from OUTSIDE them
# (human-facing pages under docs/ and one shell hook), and not one of them should carry a
# runtime loader instruction. A relation-3 implemented as "every file that cites" fires 38
# times on a correct tree. The same bound is what keeps relation 2 falsifiable: core's own
# docs/reference/references.md enumerates every reference file by name, so admitting docs/
# as a citation source would make the reverse direction unfalsifiable by construction.
# CHANGELOG.md is excluded for the same reason it is excluded everywhere else -- history
# keeps the words it shipped with, and a retired reference must not stay "reached" by them.
#
# RELATION 5'S SCOPE WAS MEASURED BEFORE IT WAS TAKEN, because this repo has twice rejected a
# widening that fired only on correct content. Over $CMD_DIR/, agents/ and $REF_DIR/ it fires
# on NOTHING: Task 4 swept all 787 sites and the tree is clean, so it starts green and exists
# to keep a constraint that currently holds by discipline from quietly stopping to hold --
# the same profile as check 14, not the profile of the two rejected widenings, which produced
# false positives. Widening it to the whole plugin fires ONCE, on correct content:
# docs/reference/session-cost.md names the companion plugin's `references/cost-prices.yaml`
# while explaining in the same sentence why it is named as a path and not in the loader's
# form. One false positive and zero true ones is the result on which the other widenings were
# refused, so the scope stops where relation 3's does.
#
# WHAT THIS DELIBERATELY DOES NOT GATE, stated so nobody mistakes green for safe:
#   * The BARE-BASENAME class -- an unqualified `<name>.md` with no directory in front of
#     it. NO COUNT IS GIVEN HERE, deliberately: the figure this comment used to carry ("~27
#     hits") was reproducible under no reading of the tree, and the case for the exclusion
#     never rested on it. It rests on a collision that can be checked in one command:
#     `code-scanner.md` and `impl-maintenance.md` each name BOTH a file in the corpus
#     (handoff/) and an agent in the same plugin, so a bare mention of either is undecidable
#     by pattern -- which is precisely why Task 4's `8d20345` had to qualify those two by
#     hand after a basename scan could not see them. The form carries no directory context
#     at all, so it equally names an artifact in the specs tree, a repo file, or a docs
#     page. Resolving an identifier against a known set is this repo's rule; parsing one out
#     of free text is what that rule forbids. Left to review. (Relation 5 above gates the
#     PREFIXED forms, which do carry the context that makes them decidable.)
#   * skills/. No skill in any consuming plugin cites a core reference today, so including
#     it would assert nothing; a skill that starts to is review's to catch.
#   * WHETHER the loaded content is used correctly. This validates that the argument names
#     a real file and that the call is reachable, nothing about what the run then does.
check_loader_contract() {
  local root="$1" out h
  [ -n "$LOADER_SKILL" ] \
    || { note "check 16 not applicable: this edition declares no loader skill (its corpus and its call sites ship in one plugin)"; return; }
  out=$(python3 - "$root" "$CORE_PLUGIN_REL" "$CMD_DIR" "$REF_DIR" "$LOADER_SKILL" "$PLUGIN_RELS" <<'PYEOF'
import io, os, re, sys

root, core_rel, cmd_dir, ref_dir, loader, plugin_list = sys.argv[1:7]
plugins = plugin_list.split()
if core_rel not in plugins:
    plugins = plugins + [core_rel]
scan_dirs = (cmd_dir, 'agents', ref_dir)
core_ref_root = os.path.join(root, core_rel, ref_dir)
out = []

# The corpus: every FILE under the core reference dir, keyed by its path relative to that
# dir, so `handoff/code-scanner.md` and `model-routing/classification.md` are ordinary
# members rather than special cases.
corpus = set()
for dirpath, _dirs, names in os.walk(core_ref_root):
    for n in names:
        corpus.add(os.path.relpath(os.path.join(dirpath, n), core_ref_root).replace(os.sep, '/'))
md_corpus = sorted(r for r in corpus if r.endswith('.md'))

NAME = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]*(/[A-Za-z0-9][A-Za-z0-9_.-]*)*$')

# TWO resolvers, and they must stay two. They were one, extension-tolerant on both paths,
# and that made the gate BLESS a call the runtime cannot serve: skills/reference/SKILL.md
# reads `${CLAUDE_PLUGIN_ROOT}/references/<the first argument>.md`, appending `.md`
# UNCONDITIONALLY, so `args: "cost-prices.yaml"` reads cost-prices.yaml.md and finds
# nothing. A green selftest case pinned the tolerant behaviour, which would have made the
# divergence durable. Latent -- no live argument carries an extension -- which is exactly
# why it would have survived.
def arg_target(tok):
    """A loader `args:` first token -> (corpus path or None, the candidate tried). `.md` is
    appended unconditionally, because that is what the skill body does. An argument carrying
    its own extension is therefore a DEFECT, not a tolerated form: the loader serves
    reference prose, and the corpus's one non-markdown member is read by the script that
    prices with it, never loaded."""
    cand = tok + '.md'
    if '..' in tok or not NAME.match(tok):
        return None, cand
    return (cand if cand in corpus else None), cand

def cite_target(tok):
    """A CITATION token -> its corpus path, or None. Extension-tolerant, and deliberately so:
    a prose citation of the data file (`<core>:cost-prices.yaml`) names a real corpus member
    and must resolve, even though the loader could never serve it. Do not merge this with
    arg_target() again -- the two answer different questions about the same corpus."""
    if '..' in tok or not NAME.match(tok):
        return None
    cand = tok if os.path.splitext(tok)[1] else tok + '.md'
    return cand if cand in corpus else None

CALL = re.compile(r'"' + re.escape(loader) + r'"\s*,\s*args:\s*"([^"]*)"')
core_name = os.path.basename(core_rel)
TOKEN = re.compile(r'(?<![A-Za-z0-9_-])' + re.escape(core_name) + r':([A-Za-z0-9][A-Za-z0-9_./-]*)')
FENCE = re.compile(r'^[ \t]*(```|~~~)')
PATHCITE = re.compile(r'\$\{CLAUDE_PLUGIN_ROOT\}/' + re.escape(ref_dir) + r'/([A-Za-z0-9][A-Za-z0-9_./-]*)')
BARECITE = re.compile(r'`' + re.escape(ref_dir) + r'/([A-Za-z0-9][A-Za-z0-9_./-]*)`')

def files_under(rel):
    for d in scan_dirs:
        base = os.path.join(root, rel, d)
        for dirpath, _dirs, names in os.walk(base):
            for n in sorted(names):
                if n == 'CHANGELOG.md':
                    continue
                yield os.path.join(dirpath, n)

def own_refs(rel):
    """The reference files THIS plugin ships, by corpus-relative name. Relation 5 flags a
    consumer-side path citation only where the name belongs to core and NOT to the citing
    plugin: a plugin that ships its own `<name>.md` is citing its own, unambiguously, and
    the two trees have zero name collisions today (re-derive rather than trust that)."""
    base = os.path.join(root, rel, ref_dir)
    got = set()
    for dirpath, _dirs, names in os.walk(base):
        for n in names:
            got.add(os.path.relpath(os.path.join(dirpath, n), base).replace(os.sep, '/'))
    return got

reached = dict((r, 0) for r in md_corpus)
preamble_files = 0
real_calls = 0

for rel in plugins:
    consumer = (rel != core_rel)
    mine = own_refs(rel) if consumer else set()
    for path in files_under(rel):
        try:
            text = io.open(path, encoding='utf-8').read()
        except Exception:
            continue
        show = os.path.relpath(path, root)
        self_ref = None
        if path.startswith(os.path.join(root, core_rel, ref_dir) + os.sep):
            self_ref = os.path.relpath(path, core_ref_root).replace(os.sep, '/')
        has_preamble = False
        cites_core = False
        infence = False
        for lineno, line in enumerate(text.split('\n'), 1):
            if FENCE.match(line):
                infence = not infence
                continue
            for m in CALL.finditer(line):
                arg = m.group(1)
                parts = arg.split()
                tok = parts[0] if parts else ''
                if tok.startswith('<'):
                    # The documentation placeholder: this line IS the preamble.
                    has_preamble = True
                    continue
                real_calls += 1
                cites_core = True
                target, cand = arg_target(tok)
                if target is None:
                    out.append("%s:%d loads '%s' through %s, which resolves to %s/%s/%s -- "
                               "no such file. The reference is the FIRST whitespace token "
                               "(a second is an entry point WITHIN it) and the loader "
                               "appends '.md' unconditionally, so an argument carrying its "
                               "own extension cannot resolve: a non-markdown corpus member "
                               "is cited as a path and read by whatever consumes it, never "
                               "loaded through the loader"
                               % (show, lineno, arg, loader, core_rel, ref_dir, cand))
                elif target != self_ref:
                    reached[target] = reached.get(target, 0) + 1
                if infence:
                    out.append("%s:%d puts a %s call inside a fenced block -- a run PRINTS a "
                               "fenced block, it never executes it, so this reference is "
                               "never loaded. Name it in the block and make the call in prose"
                               % (show, lineno, loader))
            for m in TOKEN.finditer(line):
                # Trailing sentence punctuation is not part of the name. Stripped HERE and not
                # inside cite_target(), because in a loader `args:` string a trailing dot is a
                # typo to report rather than noise to forgive.
                if cite_target(m.group(1).rstrip('./-')) is not None:
                    cites_core = True
            for pat, form in ((PATHCITE, '${CLAUDE_PLUGIN_ROOT}/%s/<name>' % ref_dir),
                              (BARECITE, '`%s/<name>`' % ref_dir)):
                for m in pat.finditer(line):
                    c = m.group(1)
                    if rel == core_rel:
                        # Inside core these two forms are what relation 2 counts.
                        if c in reached and c != self_ref:
                            reached[c] += 1
                    elif c in corpus and c not in mine:
                        # RELATION 5. Outside core the same two forms are the defect the
                        # loader exists to prevent: ${CLAUDE_PLUGIN_ROOT} resolves to the
                        # READING plugin, so this path opens nothing, and the bare form
                        # sends a reader to a directory that does not hold the file.
                        cites_core = True
                        out.append("%s:%d cites the %s reference '%s' as %s, which resolves "
                                   "to THIS plugin's %s/ and not to the corpus -- that is the "
                                   "defect the loader exists to prevent. Name it '%s:%s' in "
                                   "prose, and load it with Skill(skill: \"%s\", args: \"%s\")"
                                   % (show, lineno, core_rel, c, form, ref_dir,
                                      core_name, c[:-3] if c.endswith('.md') else c,
                                      loader, c[:-3] if c.endswith('.md') else c))
        if has_preamble:
            preamble_files += 1
        if consumer and cites_core and not has_preamble:
            out.append("%s cites a %s reference but carries no loader preamble -- the line "
                       "documenting Skill(skill: \"%s\", args: \"<name>\"), which is what "
                       "tells a run to read it through the loader instead of by a "
                       "${CLAUDE_PLUGIN_ROOT} path that resolves to this plugin"
                       % (show, core_rel, loader))

if not md_corpus:
    out.append("%s/%s/ holds no markdown -- the corpus every loader argument resolves "
               "against is missing or empty, and this check would examine nothing"
               % (core_rel, ref_dir))
else:
    for r in md_corpus:
        if reached[r] == 0:
            out.append("%s/%s/%s is reached by no citation -- no loader args: string names "
                       "it, and no file inside %s's %s/, agents/ or %s/ cites it as "
                       "${CLAUDE_PLUGIN_ROOT}/%s/%s or `%s/%s`. An unreached reference is "
                       "either dead or cited in a form nothing resolves"
                       % (core_rel, ref_dir, r, core_rel, cmd_dir, ref_dir,
                          ref_dir, r, ref_dir, r))

# Vacuity: the forward direction reads one syntax, and a repo-wide rewording of it would
# make relations 1 and 4 examine nothing while every message above stayed silent. The
# preamble count is the evidence that the syntax is still meant to be in use.
if preamble_files > 0 and real_calls == 0:
    out.append("%d file(s) document the %s preamble but no real invocation of it was found "
               "anywhere under %s -- the call syntax was reworded and the forward direction "
               "now examines nothing; fix the extractor, never the call sites"
               % (preamble_files, loader, ' '.join(plugins)))

for line in out:
    print(line)
print("__CHECK16_RAN__")
PYEOF
)
  case "$out" in
    *__CHECK16_RAN__*) : ;;
    *) fail 16 "the loader-contract scan did not complete (python3 absent, or the scan itself errored) -- this check would examine nothing"; return ;;
  esac
  while IFS= read -r h; do
    [ -n "$h" ] || continue
    [ "$h" = "__CHECK16_RAN__" ] && continue
    fail 16 "$h"
  done <<<"$out"
}

# ------------------------------------------------------------------ check 17
# Agent dispatch authority (PS15). A ledger item recorded a live defect: an agent
# self-disclosed dispatching a stray subagent mid-run, outside its own sanctioned set.
# A check that verifies RUNTIME behaviour is impossible from a static script -- and a check
# that merely asserted "the rule exists" would have passed on the very run that misbehaved:
# MEASURED FIRST, only 3 of the agents under PLUGIN_RELS carried `Task` in their tool list at
# all (upgrade-executor, vuln-fixer, docs-style-checker), and all three already carried a
# NEVER-dispatch rule naming their sanctioned subagent, in near-identical wording, when one of
# them still mis-dispatched. So what is checkable is the STRUCTURAL PRECONDITION, not the
# behaviour: every agent whose tool list grants `Task` must also carry the rule. That is 3-for-3
# today -- green on the current tree -- and it fires the moment a fourth agent gains `Task`
# without the rule, which is the realistic way this decays; it cannot catch a dispatch outside
# the sanctioned set from an agent that already carries the rule, because that is behaviour.
#
# THE ANCHOR PHRASE is quoted from the three live carriers rather than invented: "NEVER dispatch
# any subagent other than `<name>`. That one dispatch is your entire `Task` authority." A looser
# match on the word "dispatch" alone would be satisfied by ordinary prose (a reviewer discussing
# who dispatches what) -- this checks for the exact sentence, backticked name varying, which
# nothing but the sanctioned-set rule itself can satisfy.
#
# BOTH DIRECTIONS. The reverse -- a file carrying the rule but NOT `Task` in its tool list -- is
# its own defect: it declares a dispatch authority the harness would refuse, which misleads a
# reader into believing the agent can do what its tool list forbids. Asserted here because it is
# verified green on the tree today (the same 3 files carry both, and no other file carries the
# rule alone).
#
# VACUITY GUARD, same shape as check_merge_clause's: if the scan finds not one agent anywhere
# under PLUGIN_RELS carrying `Task`, that is the frontmatter parsing having silently stopped
# matching, not a tree with nothing to dispatch -- fail loudly rather than pass.
#
# SCOPE is agents/ only, one flat directory (`agents/*.md`, no subdirectories in this tree
# today) under each plugin in PLUGIN_RELS -- commands and skills carry their own
# `allowed-tools:` frontmatter but are outside PS15's finding, which was about a subagent
# dispatching a stray subagent. The tool-list key is read as either `tools:` or
# `allowed-tools:`, whichever the frontmatter uses; every agent in this tree today uses
# `tools:` on one unwrapped line, so a tools array that wraps across lines is this check's
# one blind spot, matching the file's own "state what a check cannot see" convention.
check_dispatch_authority() {
  local root="$1" rel p f frontmatter toolsline has_task has_rule seen=0 rp
  local anchor='NEVER dispatch any subagent other than `[^`]+`\. That one dispatch is your entire `Task` authority\.'
  for rel in $PLUGIN_RELS; do
    p="$root/$rel/agents"
    [ -d "$p" ] || continue
    for f in "$p"/*.md; do
      [ -e "$f" ] || continue
      rp="${f#$root/}"
      frontmatter=$(awk 'NR==1 && $0=="---"{infm=1;next} infm && $0=="---"{exit} infm{print}' "$f")
      toolsline=$(grep -E '^(tools|allowed-tools):' <<<"$frontmatter" | head -1)
      has_task=0
      case "$toolsline" in *'"Task"'*) has_task=1 ;; esac
      has_rule=0
      grep -qE -- "$anchor" "$f" && has_rule=1

      if [ "$has_task" = 1 ]; then
        seen=$((seen + 1))
        [ "$has_rule" = 1 ] \
          || fail 17 "$rp carries \`Task\` in its tool list but no NEVER-dispatch rule naming its sanctioned subagent (the anchor sentence: \"NEVER dispatch any subagent other than \`<name>\`. That one dispatch is your entire \`Task\` authority.\") -- a 4th Task-carrying agent with no sanctioned set stated is exactly how PS15's mis-dispatch happened"
      fi
      if [ "$has_rule" = 1 ] && [ "$has_task" != 1 ]; then
        fail 17 "$rp carries a NEVER-dispatch rule naming a sanctioned subagent but its tool list grants no \`Task\` -- it declares a dispatch authority the harness would refuse, which is stale and will mislead a reader"
      fi
    done
  done
  [ "$seen" -gt 0 ] \
    || fail 17 "no agent under any PLUGIN_RELS agents/ carries \`Task\` in its tool list -- this check would examine nothing, which means the frontmatter scan has drifted rather than the tree having nothing left to dispatch"
}

# --------------------------------------------------------------- check 18
# CHECK 18 gates the one claim a changelog makes about ITSELF: a section headed `— Unreleased`
# says, in each file's own header sentence, that it "has not been published yet". On the default
# branch that is false by construction -- `claude plugin update` fetches from main, so everything
# on main IS what users install. The section is published the moment the push lands.
#
# WHY IT EXISTS: measured recurrence, not taste. Commit 47050554 (2026-09-19) dated every
# `— Unreleased` section then standing, with a commit message saying so; by 2026-09-22 SEVEN more
# stood across four plugins, every one of them live on origin. Twice in a row, with nothing in
# scripts/ able to see it. A published changelog that reads "Unreleased" beside the version a user
# just installed is the whole of the defect -- cosmetic in effect, but it is the file's own claim
# about itself, and it is the kind that no reader ever re-derives.
#
# WHY IT IS NOT ON BY DEFAULT, which is the half that keeps it usable: on a feature branch an
# `— Unreleased` section is the CORRECT authoring state -- that is what the header sentence is for,
# and what it means by "they all ship together in the next release". A gate that fired there would
# be red for the whole life of every release branch, and a gate that blocks correct work is a gate
# someone disables. So it runs only where the claim is actually false: ASSERT_PUBLISHED=1, which
# .github/workflows/validate-catalog.yml sets on a push to the default branch and nowhere else.
# The env var rather than a flag is deliberate -- it composes with the selftest's expect_*_env
# helpers, so the case that proves the gate STAYS QUIET without it can be written at all.
#
# SCOPE is every `plugins/*/CHANGELOG.md`, not PLUGIN_RELS: every plugin in the catalog publishes
# from the same ref, and a docs-gated plugin is not the population here.
#
# WHAT IT DOES NOT MATCH, measured before choosing: the bare Keep-a-Changelog `## [Unreleased]`
# form. This tree carries exactly one, `### [Unreleased] (pre-plugin-split)` in dev-workflows'
# changelog -- a labelled historical section recording work from before the marketplace split,
# which is correct content. Matching it would fire on correct content and on nothing else, which is
# the same result on which this file's earlier widenings were refused. The convention this repo
# actually writes is the version-heading form, and that is what is gated.
check_published_changelog() {
  local root="$1" f rp seen=0 hit line n
  [ "${ASSERT_PUBLISHED:-}" = 1 ] || return 0
  for f in "$root"/plugins/*/CHANGELOG.md; do
    [ -e "$f" ] || continue
    seen=$((seen + 1))
    rp="${f#$root/}"
    # `##`-or-deeper heading, a bracketed version, an em dash or hyphen, then Unreleased.
    # An alternation, never a bracket expression: `[—-]` is a set of BYTES in a C/POSIX locale
    # (a container with LANG unset), where the three-byte em dash can never match it and the
    # check went silently inert on the form this repo actually writes.
    while IFS= read -r line; do
      [ -n "$line" ] || continue
      n="${line%%:*}"
      hit="${line#*:}"
      fail 18 "$rp:$n is headed \`${hit# }\` on a ref that publishes it -- this file's own header says an \`— Unreleased\` section \"has not been published yet\", and everything on the default branch is what \`claude plugin update\` fetches. Date it with the day of the push that publishes it"
    done <<EOF
$(grep -nE '^#{2,}[[:space:]]+\[[^]]+\][[:space:]]*(—|-)[[:space:]]*Unreleased[[:space:]]*$' "$f" || true)
EOF
  done
  [ "$seen" -gt 0 ] \
    || fail 18 "no plugins/*/CHANGELOG.md found at all -- this check would examine nothing, which means the glob has drifted rather than the marketplace having shipped no changelog"
}

# --------------------------------------------------------------- check 19
# CHECK 19 gates the edition's own denylist, EDITION_FORBIDDEN_B64 in the config block: base64
# of one extended regex naming what this edition must never print. It exists because a
# constraint held by discipline alone stopped holding: the public edition's design archive,
# with its neighbouring records, named the organisation it was written inside and that
# organisation's internal repositories, across more than a hundred files before anyone swept
# them out on 2026-09-23. Check 14 could not see it -- check 14 quarantines a DIFFERENT
# organisation, the one the plugin was extracted from, and its list is body, identical in
# every edition. This list cannot be body, because the
# internal edition legitimately names exactly what this one forbids; so the pattern is edition
# config, and an EMPTY value means "this edition forbids nothing" and the check passes without
# opening a file.
#
# SCOPE is every text file under the root minus .git, like check 14's, with two differences.
# First, files named CHANGELOG.md are exempt: a changelog is history and keeps what it shipped
# with, the exemption check-id-grammar.sh and checks 12, 13 and 16 already make by filename.
# Second, where the root is its work tree's top level the file list is
# `git ls-files -co --exclude-standard` --
# tracked AND untracked, so a page not yet added is still examined (the vacuous-pass failure
# this file's header records), but not git-ignored: a main checkout holds ignored second copies
# of the tree (.worktrees/, which can sit on a branch older than the sweep) and ignored
# container state, and a gate that reads them goes red for a reason that is not the tree being
# checked -- the same reason check-id-grammar.sh excludes .worktrees/. Anywhere else (outside a
# work tree, as the selftest's fixture copies are, or below its top level) it walks the directory.
check_edition_forbidden() {
  local root="$1" pat hits top
  [ -n "$EDITION_FORBIDDEN_B64" ] || return 0
  pat="$(b64d "$EDITION_FORBIDDEN_B64")"
  # The same vacuity guard check 14 carries: a value that decodes to nothing would examine
  # nothing while reporting success.
  [ -n "$pat" ] \
    || { fail 19 "EDITION_FORBIDDEN_B64 is set but did not decode -- this check would examine nothing"; return; }
  top="$(git -C "$root" rev-parse --show-toplevel 2>/dev/null || true)"
  if [ -n "$top" ] && [ "$(cd "$top" && pwd -P)" = "$(cd "$root" && pwd -P)" ]; then
    hits=$(cd "$root" && git ls-files -z -co --exclude-standard \
      | tr '\0' '\n' | grep -v -E '(^|/)CHANGELOG\.md$' | tr '\n' '\0' \
      | xargs -0 grep -HEinIs -- "$pat" 2>/dev/null | head -50)
  else
    hits=$(grep -rEinIs --exclude-dir=.git --exclude=CHANGELOG.md -- "$pat" "$root" 2>/dev/null \
      | sed "s|^$root/||" | head -50)
  fi
  [ -n "$hits" ] || return 0
  local h; while IFS= read -r h; do
    [ -n "$h" ] && fail 19 "$(printf '%s' "$h" | cut -d: -f1-2) names something this edition's EDITION_FORBIDDEN_B64 forbids -- it must not appear anywhere in this repository; files named CHANGELOG.md are the only exemption, because history keeps what it shipped with"
  done <<<"$hits"
}

# ---------------------------------------------------------------------- main
# selftest() runs before the dispatch loop below ever assigns PLUGIN_REL per iteration,
# and its fixture mutations reference the bare (singular) $PLUGIN_REL directly -- so it
# needs a value now. The first list element is generic, not edition data: with today's
# one-plugin list it is exactly the old scalar, which is the behaviour this preserves.
PLUGIN_REL="${PLUGIN_RELS%% *}"
[ "${1:-}" = "--selftest" ] && selftest

ROOT="."
if [ "${1:-}" = "--root" ]; then
  [ $# -lt 2 ] && { echo "Usage: $0 [--root <dir>] | --selftest" >&2; exit 2; }
  ROOT="$2"
fi
[ -d "$ROOT" ] || { echo "Usage: $0 [--root <dir>] | --selftest" >&2; exit 2; }
ROOT="$(cd "$ROOT" && pwd)"
[ "$HAVE_PY" = 1 ] || note "python3 not found; falling back to ASCII slugs -- anchors whose heading contains a non-ASCII letter cannot be verified here"

for PLUGIN_REL in $PLUGIN_RELS; do
  if [ ! -d "$ROOT/$PLUGIN_REL/docs" ]; then
    fail 4 "$PLUGIN_REL/docs does not exist"
    continue
  fi
  check_links_and_anchors   "$ROOT"
  check_orphans             "$ROOT"
  check_inventory           "$ROOT"
  check_env_vars            "$ROOT"
  check_table_cells         "$ROOT"
  check_install_block       "$ROOT"
  check_cost_applicability   "$ROOT"
  case " $COST_PLUGIN_RELS "    in *" $PLUGIN_REL "*) check_cost_attribution "$ROOT" ;; esac
  check_prose_counts        "$ROOT"
  check_identity_quarantine "$ROOT"
  check_handoff_applicability "$ROOT"
  case " $HANDOFF_PLUGIN_RELS " in *" $PLUGIN_REL "*) check_merge_clause     "$ROOT" ;; esac
  check_choices_arity       "$ROOT"
  check_vendor_tokens       "$ROOT"
  check_foreign_identity    "$ROOT"
  check_index_membership    "$ROOT"
done

# Check 16 sits OUTSIDE the loop, unlike every check above it. The loader contract is a
# relation between the corpus plugin and all of its consumers at once -- the reverse
# direction asks whether a reference is reached by ANY of them -- so a per-plugin dispatch
# would either report the same unreached reference once per plugin or need a latch to
# suppress the repeats. It derives its own plugin set from $PLUGIN_RELS plus
# $CORE_PLUGIN_REL, which is the same set the loop walks plus the corpus when that is not a
# documented plugin of its own.
check_loader_contract     "$ROOT"

# Check 17 also sits OUTSIDE the loop, for the same reason: its vacuity guard is a claim
# about the ENTIRE PLUGIN_RELS tree ("not one agent anywhere carries Task"), which a
# per-plugin dispatch cannot make without a latch -- the same shape check 16 is here for.
# It loops $PLUGIN_RELS itself rather than reading the loop variable.
check_dispatch_authority  "$ROOT"

# Check 18 sits outside the loop too: its population is every plugin's changelog, not the
# docs-gated subset PLUGIN_RELS names, and it is a no-op unless ASSERT_PUBLISHED=1.
check_published_changelog "$ROOT"

# Check 19 sits outside the loop as well: its population is the whole repository, so a
# per-plugin dispatch would report every hit once per plugin -- the repetition check 14 lives
# with inside the loop.
check_edition_forbidden   "$ROOT"

if [ "$FAILURES" -gt 0 ]; then
  echo "FAIL: $FAILURES problem(s) under $PLUGIN_RELS" >&2
  exit 1
fi
echo "PASS: docs are consistent with the plugin(s) under $PLUGIN_RELS"
