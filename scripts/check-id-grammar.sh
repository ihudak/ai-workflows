#!/usr/bin/env bash
# Fails when a tracked plugin doc teaches the dash-form requirement-ID grammar.
# Spec: docs/superpowers/specs/2026-08-18-jira-safe-requirement-ids-design.md, removed from
# the tree 2026-09-23 -- `git show 62e791e8:<that path>` retrieves it.
set -uo pipefail

# --baseline [<root>] holds the spec/design numbered-ID census to scripts/spec-id-baseline.txt.
# Those IDs sit deliberately outside the [PREFIX#N] grammar this gate enforces, and the baseline
# is their tripwire: a change in a count means text using them moved, or a global replace
# reached their namespace. The file's own "Verify" recipe was run by nothing, so two drifts were
# found weeks late by hand; this mode runs that recipe -- the pattern and scan roots below must
# stay the ones its header's Regenerate and Verify recipes name; the mode fails where those
# recipes do not, and on any difference in the counts. A recipe is matched by its own context,
# `grep -rhoE '<pattern>'` and `--exclude='CHANGELOG.md' <roots>`, never by the bare string, which
# the header's prose also carries; each must appear twice, once per recipe. `sort` runs in the C
# locale and both sides are compared as `<count> <id>`, so neither the order nor `uniq -c`'s count
# width (GNU and BSD pad it differently) can depend on the machine.
SPEC_ID_PATTERN='\[U0[0-9]+\]|\[AC0[0-9]+\]|\[TC0[0-9]+\]|\[Uxx\]|\[ACxx\]|\[TCxx\]'
SPEC_ID_ROOTS='plugins/ CLAUDE.md .claude/rules/ docs/maintainers/'

# --selftest runs the gate against its own fixtures and asserts, per fixture, the
# exit code AND every form the gate must have named. Without it the fixtures are
# decorative: CI only ever ran `--root .`, so nothing proved the gate could still
# FAIL. A check that cannot be shown to fail proves nothing when it passes.
#
# THE EXIT CODE ALONE IS NOT ENOUGH, and this was proven, not assumed. Each negative
# fixture carries several violating lines, so ANY surviving alternation of PATTERN
# holds the exit code at 1: a review deleted both `SM-C` alternations and watched
# `--selftest` print SELFTEST PASS, then watched the degraded gate accept a live
# `[SM-C1]` in a shipped reference file. The sibling gate's selftest had asserted
# WHICH check fired since the day it was written, for exactly this reason. So every
# negative case here also asserts the forms in the gate's own output, one grep per
# form, which is what makes an alternation impossible to delete quietly.
if [ "${1:-}" = "--selftest" ]; then
  here=$(cd "$(dirname "$0")" && pwd)
  rc=0
  mode=--root # the mode each expect runs the gate in; the --baseline cases below switch it
  expect() { # <description> <expected-exit> <root> [<form-that-must-be-reported>...]
    local desc="$1" want="$2" root="$3"; shift 3
    local out got form missing=""
    out=$("$0" "$mode" "$root" 2>&1); got=$?
    for form in "$@"; do
      grep -qF -- "$form" <<<"$out" || missing="$missing $form"
    done
    if [ "$got" -eq "$want" ] && [ -z "$missing" ]; then
      printf 'ok    %s (exit %s%s)\n' "$desc" "$got" "$([ $# -gt 0 ] && printf ', %s forms named' "$#")"
    elif [ "$got" -ne "$want" ]; then
      printf 'FAIL  %s: expected exit %s, got %s\n' "$desc" "$want" "$got"; rc=1
    else
      printf 'FAIL  %s: exit %s was right, but the gate never named:%s -- an alternation of PATTERN has stopped matching\n' "$desc" "$got" "$missing"; rc=1
    fi
  }
  # The form lists are the whole point: each one pins one alternation of PATTERN.
  # Bracketed and bare are separate branches of the regex and are asserted separately.
  expect "numeric dash forms are rejected"      1 "$here/fixtures/prd-bad.md" \
         "[US-1]" "[AC-1]" "[AC-2]" "[SM-1]" "[SEC-1]" "bare SEC-2"
  expect "placeholder dash forms are rejected"  1 "$here/fixtures/prd-bad-placeholders.md" \
         "[US-n]" "[AC-x]" "[AC-X]" "[SM-Cx]" "bare SM-Cx"
  expect "hash forms and real keys are accepted" 0 "$here/fixtures/prd-good.md"
  expect "a nonexistent root is an error"       2 "$here/fixtures/no-such-file.md"
  # EXCLUDED_SUBTREES, tested as a PAIR on DIRECTORY roots -- the only shape that
  # reaches that variable at all, since a file root takes the other branch of the scan
  # entirely and the four cases above are all files. Only the pair discriminates: an
  # unanchored exclusion (a bare `worktrees` name-match at any depth, which is what
  # --exclude-dir would give) passes the green case and fails the red one, and an
  # implementation that excluded too much passes green and fails red the same way.
  wtroot=$(mktemp -d)
  trap 'rm -rf "$wtroot"' EXIT
  mkdir -p "$wtroot/green/.worktrees/copy/scripts/fixtures" "$wtroot/red/nested/worktrees/copy"
  printf '# a worktree copy of this gate own negative fixtures\n\n[AC-1] and [SM-1]\n' \
    > "$wtroot/green/.worktrees/copy/scripts/fixtures/prd-bad.md"
  printf '# compliant\n\n[AC#1] and [SM#1]\n' > "$wtroot/green/kept.md"
  printf '# not a root-level worktree\n\n[AC-1] and [SM-1]\n' \
    > "$wtroot/red/nested/worktrees/copy/prd-bad.md"
  # docs/: only docs/superpowers/ (design and verification records quoting the old form) is
  # history. docs/maintainers/ holds live rationale moved out of CLAUDE.md and is gated. A
  # PAIR: the green root proves docs/superpowers stays excluded, the red one proves
  # docs/maintainers is not -- a wholesale `docs` exclusion passes green and fails red.
  mkdir -p "$wtroot/green/docs/superpowers/verification" "$wtroot/maint/docs/maintainers"
  printf '# a record quoting the retired form\n\n[AC-1]\n' \
    > "$wtroot/green/docs/superpowers/verification/record.md"
  printf '# live rationale\n\n[FR-1]\n' > "$wtroot/maint/docs/maintainers/rationale.md"
  expect "a worktree copy at the scan root is not walked"  0 "$wtroot/green"
  expect "a \`worktrees\` directory below the scan root is still walked" 1 "$wtroot/red" \
         "[AC-1]" "[SM-1]"
  expect "docs/maintainers is scanned although docs/superpowers is not" 1 "$wtroot/maint" "[FR-1]"
  # The mermaid gate's installed parser: `npm ci` puts third-party package docs under
  # scripts/mermaid/node_modules/, which is git-ignored and nothing this repository wrote.
  mkdir -p "$wtroot/green-nm/scripts/mermaid/node_modules/pkg"
  printf '# a third-party package readme\n\n[AC-1] and [SM-1]\n' \
    > "$wtroot/green-nm/scripts/mermaid/node_modules/pkg/README.md"
  printf '# compliant\n\n[AC#1] and [SM#1]\n' > "$wtroot/green-nm/kept.md"
  expect "the mermaid gate's installed packages are not walked" 0 "$wtroot/green-nm"
  # --baseline: the green tree's census equals its baseline only if every scan root is read
  # (plugins/, CLAUDE.md, .claude/rules/, docs/maintainers/) and nothing else is -- a CHANGELOG.md,
  # a non-markdown file and docs/superpowers/ each carry IDs that would move a count. Its counts
  # are padded unlike `uniq -c`'s, which must not matter. The red tree adds one ID and drops
  # another file's, and must name both drifted lines. A header with one recipe naming another
  # pattern fails, however the counts compare, and so does one whose prose names the roots while
  # one recipe names others: prose is never counted as a recipe.
  mode=--baseline
  b="$wtroot/base-green"
  mkdir -p "$b/scripts" "$b/plugins/p" "$b/.claude/rules" "$b/docs/maintainers" "$b/docs/superpowers"
  recipe() { # <pattern> <roots>: one recipe's two header lines, as the real header writes them
    printf "#   grep -rhoE '%s' \\\n#     --include='*.md' --exclude='CHANGELOG.md' %s 2>/dev/null\n" "$1" "$2"
  }
  hdr=$(recipe "$SPEC_ID_PATTERN" "$SPEC_ID_ROOTS"; recipe "$SPEC_ID_PATTERN" "$SPEC_ID_ROOTS")
  printf '%s\n2 [AC01]\n  1 [ACxx]\n   2 [Uxx]\n' "$hdr" > "$b/scripts/spec-id-baseline.txt"
  printf '# a rule\n\n[ACxx]\n' > "$b/.claude/rules/r.md"
  printf '# a plugin page\n\n[AC01] and [Uxx]\n' > "$b/plugins/p/a.md"
  printf '# root\n\n[AC01]\n' > "$b/CLAUDE.md"
  printf '# rationale\n\n[Uxx]\n' > "$b/docs/maintainers/rationale.md"
  printf '# history\n\n[U01] [U01]\n' > "$b/plugins/p/CHANGELOG.md"
  printf '[TC01]\n' > "$b/plugins/p/notes.txt"
  printf '# a record\n\n[TC01]\n' > "$b/docs/superpowers/record.md"
  cp -R "$b" "$wtroot/base-red"
  printf '# new\n\n[U01]\n' > "$wtroot/base-red/plugins/p/b.md"
  rm "$wtroot/base-red/CLAUDE.md"
  mkdir -p "$wtroot/base-empty/scripts"
  printf '%s\n' "$hdr" > "$wtroot/base-empty/scripts/spec-id-baseline.txt"
  cp -R "$b" "$wtroot/base-recipe"
  { recipe '\[U0[0-9]+\]|\[Uxx\]' "$SPEC_ID_ROOTS"; recipe "$SPEC_ID_PATTERN" "$SPEC_ID_ROOTS"
    grep -v '^#' "$b/scripts/spec-id-baseline.txt"; } > "$wtroot/base-recipe/scripts/spec-id-baseline.txt"
  cp -R "$b" "$wtroot/base-prose"
  { printf '# Scan root: %s   (all commands below are run from the repository root)\n' "$SPEC_ID_ROOTS"
    recipe "$SPEC_ID_PATTERN" "$SPEC_ID_ROOTS"; recipe "$SPEC_ID_PATTERN" 'plugins/ CLAUDE.md docs/maintainers/'
    grep -v '^#' "$b/scripts/spec-id-baseline.txt"; } > "$wtroot/base-prose/scripts/spec-id-baseline.txt"
  expect "the census equals its baseline"            0 "$b"
  expect "a census that drifted from its baseline fails" 1 "$wtroot/base-red" "[U01]" "[AC01]"
  expect "a baseline with no census line fails"      1 "$wtroot/base-empty" "no census line"
  expect "a missing baseline is an error"            2 "$wtroot/green"
  expect "a header naming another pattern fails"     1 "$wtroot/base-recipe" "no longer name"
  expect "prose naming the roots is no recipe"       1 "$wtroot/base-prose" "no longer name"
  mode=--root
  if [ "$rc" -eq 0 ]; then
    echo "SELFTEST PASS"
  else
    echo "SELFTEST FAIL"
  fi
  exit "$rc"
fi

if [ "${1:-}" = "--baseline" ]; then
  broot="${2:-.}"
  bfile="$broot/scripts/spec-id-baseline.txt"
  if [ ! -r "$bfile" ]; then
    echo "ERROR: '$bfile' does not exist or is not readable" >&2
    exit 2
  fi
  # The recipes in the header and the copy above must agree, or the two drift apart unseen.
  for needle in "grep -rhoE '$SPEC_ID_PATTERN'" "--exclude='CHANGELOG.md' $SPEC_ID_ROOTS"; do
    if [ "$(grep '^#' "$bfile" | grep -cF -- "$needle")" -lt 2 ]; then
      echo "FAIL: $bfile's Regenerate and Verify recipes no longer name this mode's $needle --"
      echo "      change scripts/check-id-grammar.sh's SPEC_ID_PATTERN or SPEC_ID_ROOTS with them"
      exit 1
    fi
  done
  want=$(grep -v '^#' "$bfile" | awk '{print $1, $2}' || true)
  if [ -z "$want" ]; then
    echo "FAIL: $bfile holds no census line -- a census of nothing trips on nothing"
    exit 1
  fi
  # shellcheck disable=SC2086 # SPEC_ID_ROOTS is a word list on purpose
  got=$( cd "$broot" && grep -rhoE "$SPEC_ID_PATTERN" --include='*.md' --exclude='CHANGELOG.md' \
           $SPEC_ID_ROOTS 2>/dev/null | LC_ALL=C sort | uniq -c | awk '{print $1, $2}' )
  if delta=$(diff <(printf '%s\n' "$want") <(printf '%s\n' "$got")); then
    echo "PASS: the spec-ID census under $broot equals scripts/spec-id-baseline.txt"
    exit 0
  fi
  echo "FAIL: the spec-ID census drifted from scripts/spec-id-baseline.txt (< baseline, > tree):"
  printf '%s\n' "$delta"
  echo
  echo "Find which files moved each count before touching the baseline. A global replace that"
  echo "reached these IDs is the defect this catches; a new or removed use of one is regenerated"
  echo "with the file's Regenerate recipe and a dated header paragraph naming each delta's source."
  exit 1
fi

ROOT="."
if [ "${1:-}" = "--root" ]; then
  if [ $# -lt 2 ]; then
    echo "Usage: $0 [--root <dir>] | --selftest" >&2
    exit 2
  fi
  ROOT="$2"
fi

if [ ! -e "$ROOT" ] || [ ! -r "$ROOT" ]; then
  echo "ERROR: --root '$ROOT' does not exist or is not readable" >&2
  exit 2
fi

# Requirement-ID prefixes the plugin mints. NOT a general Jira-key check:
# a real key like PRODUCT-123 is legitimate and must never be flagged.
# SEC is the security register's finding ID, [SEC#n] (security-workflows); it
# joined both prefix alternations when nothing in the tree wrote a dash form of it.
#
# The number class is [NnXx0-9] everywhere, and identical on all four
# alternations. It covers literal numbers plus every placeholder letter these
# docs actually use -- N, n, x and X. Narrowing it has already cost us once:
# the class was [N0-9] when the conversion ran, so `[SM-Cx]` in prd-reviewer.md
# passed the gate green and had to be found and fixed by hand (2c56b57).
# A bracketed `[US-n]` slipped through the same way while the bare `US-n` was
# caught, because the two branches disagreed about lowercase n.
#
# SM-C<N> (e.g. SM-C1) is the legacy counter-metric form; SMC#<N> is its
# hash-form target and is already covered by the shared prefix alternation
# below -- SM-C needs its own alternative because it doesn't fit the
# \[(PREFIX)-[N0-9]+\] shape (the dash sits before the C, not after it).
NUM='[NnXx0-9]'
PATTERN="\[(US|AC|SM|SMC|UC|FR|AD|SEC)-${NUM}+\]|\[SM-C${NUM}+\]|(^|[^[:alnum:]_[])(US|AC|SM|SMC|UC|FR|AD|SEC)-${NUM}+([^[:alnum:]_]|\$)|(^|[^[:alnum:]_[])SM-C${NUM}+([^[:alnum:]_]|\$)"

# Subtrees that legitimately carry the legacy form, anchored to the SCAN ROOT
# rather than matched by bare directory name. `--exclude-dir=docs` would skip
# any directory called `docs` at any depth -- including a future
# plugins/<name>/docs/ -- which is a silent hole in a gate whose whole job is
# to have no silent holes. `.git` stays a name-match: it is never in scope at
# any depth.
#   docs/superpowers/ -- this repo's design and verification records, which quote the old form.
#                       docs/maintainers/ is NOT excluded: it is live rationale moved out of
#                       CLAUDE.md, and nothing about moving a rule exempts it from the grammar.
#   .remember/       -- session history, untracked
#   .superpowers/    -- SDD workspace, untracked
#   .worktrees/      -- git worktrees: a SECOND FULL COPY of the tree, git-ignored,
#     worktrees/        never what this gate was asked about. Walking into one reaches
#                       the copy's own scripts/fixtures/, whose deliberate dash-form
#                       negative controls are then reported as live violations -- the
#                       gate goes red on the main checkout for a reason that has nothing
#                       to do with the tree being checked, and it does so during the
#                       merged-result run, the last check before a branch lands. Both
#                       names are excluded because both are what the worktree tooling
#                       creates; only `.worktrees` is in this repo's .gitignore today.
#   scripts/fixtures -- this gate's own negative-control fixtures
#   scripts/mermaid/node_modules -- the mermaid gate's installed parser (`npm ci`),
#                       git-ignored: third-party package docs, nothing this
#                       repository wrote or ships
EXCLUDED_SUBTREES='^\./(docs/superpowers|\.remember|\.superpowers|\.worktrees|worktrees|scripts/fixtures|scripts/mermaid/node_modules)/'

# CHANGELOG.md is history and keeps the dash form (spec Global Constraints).
# A line carrying the marker `id-grammar-ok:` is documenting the legacy form on
# purpose. Sanctioned users -- 5 marked lines across 5 files, in three kinds.
# It was 10 across 6 until the tracker-reading agent holding five reader-tolerance
# lines was deleted; re-derive with grep rather than adjusting the number:
#   * reader tolerance (1): ard-resolution's
#     parse of `## Architecture decisions` -- this ACCEPTS the legacy form;
#   * authoring BLOCKER rules (3): prd-reviewer, ard-reviewer, epic-reviewer --
#     these FORBID it in a file their own command just wrote;
#   * readiness-reviewer's MINOR rule (1) -- it REPORTS the legacy form in an
#     artifact the run did not author, without gating the verdict.
# Each has to quote the legacy form in order to accept, forbid, or report it.
# The per-file breakdown is audited so the marker cannot become a general
# escape hatch.
if [ -d "$ROOT" ]; then
  raw=$( cd "$ROOT" && grep -rnE "$PATTERN" \
          --include='*.md' \
          --exclude='CHANGELOG.md' \
          --exclude-dir='.git' \
          . 2>/dev/null || true )
  raw=$( printf '%s\n' "$raw" | grep -vE "$EXCLUDED_SUBTREES" || true )
else
  raw=$( grep -nE "$PATTERN" "$ROOT" 2>/dev/null || true )
fi

hits=$( printf '%s\n' "$raw" | grep -v 'id-grammar-ok:' | sed '/^$/d' || true )

if [ -n "$hits" ]; then
  echo "FAIL: dash-form requirement IDs found (expected [PREFIX#N]):"
  echo "$hits"
  echo
  echo "Count: $(echo "$hits" | wc -l)"
  exit 1
fi

echo "PASS: no dash-form requirement IDs under $ROOT"
exit 0
