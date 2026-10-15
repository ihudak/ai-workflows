#!/usr/bin/env bash
# Fires on every message submission. Matches the two commands this plugin ships
# that inject context: /document bare or prefixed with this plugin's own
# namespace (e.g. /docs-workflows:document), and /release-notes in the
# QUALIFIED form only — see the note above the regexes for why. It routes
# them:
#   • /document                         → specs context iff the argument is an
#                                         address (e.g. /document PRODUCT-1234);
#                                         free-text / @file → silent (direct-edit
#                                         mode owns its own git hygiene and never
#                                         invokes Opus)
#   • /release-notes                    → $SPECS_PATH + $REPOS_PATH default
#                                         + git branch only if cwd is inside
#                                         a git repo (no model-routing, no full
#                                         status/log, no directory listing). It
#                                         accepts an address or a specs directory.
#   • /docs-profile                     → not matched (no context injected)
#
# emit_specs_context surfaces $SPECS_PATH alongside $REPOS_PATH.
#
# Two sibling plugins each ship a hook of this name, matching only their own
# commands: dev-workflows covers /implement, /vuln and /upgrade;
# product-workflows covers /epics. A UserPromptSubmit hook fires whichever
# plugin ships it, so all three run on every prompt. Disjointness holds two
# ways at once: the bare-command alternations share no command name across the
# three plugins, and the plugin-name prefix each regex accepts is a literal,
# distinct string per plugin — required rather than optional for the two
# commands that collide with a Claude Code built-in (/release-notes here,
# /upgrade in dev-workflows) — so no single prompt can match more than one of
# the three.
#
# Exits immediately (near-zero overhead) if the message doesn't match.
# Always exits 0 — must never block Claude.

# Guard: if python3 is not available, skip silently
command -v python3 &>/dev/null || exit 0

# Read prompt from stdin JSON. Claude Code's UserPromptSubmit payload uses the
# key "prompt"; hookify's rule engine also accepts "user_prompt". Try all three
# known names for robustness across versions.
prompt=$(python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('prompt') or d.get('user_prompt') or d.get('message') or '')
except Exception:
    print('')
" 2>/dev/null) || true

# Require at least one non-whitespace, non-flag argument so bare `/document` or
# `/release-notes --help` doesn't inject noise on every misfire. The optional
# first capture group holds this plugin's own namespace prefix when the
# caller used the qualified form; the second holds the command token (e.g.
# "document", "release-notes").
# `release-notes` is matched in the QUALIFIED form only, and that is not an
# oversight. Claude Code ships its own built-in /release-notes, and the built-in
# wins: a bare `/release-notes` never reaches this plugin, so preloading for it
# would inject specs context into a run that is not ours. `/document` has no
# built-in of the same name, so both forms reach us and both are matched. Group 2
# holds the command token in either branch -- keep that true if you edit these.
if [[ "$prompt" =~ ^/(docs-workflows:)?(document)[[:space:]]+[^[:space:]-] ]]; then
    :
elif [[ "$prompt" =~ ^/(docs-workflows:)(release-notes)[[:space:]]+[^[:space:]-] ]]; then
    :
else
    exit 0
fi
cmd="${BASH_REMATCH[2]}"

# --- helpers -------------------------------------------------------------
emit_git_branch_if_repo() {
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo "Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
    fi
}

emit_specs_context() {
    echo "=== Auto-injected project context (specs workflow) ==="
    if [[ -n "${REPOS_PATH:-}" ]]; then
        echo "repos_path: $REPOS_PATH"
    else
        echo "repos_path: /workspace (REPOS_PATH unset — the default, which the command uses without asking wherever it exists)"
    fi
    if [[ -n "${SPECS_PATH:-}" ]]; then
        echo "SPECS_PATH: $SPECS_PATH"
    else
        echo "SPECS_PATH: (not set — the command will ask)"
    fi
    emit_git_branch_if_repo
}

# --- per-command routing -------------------------------------------------
case "$cmd" in
    document)
        # Mode-aware: an address argument → specs context; free-text / @file → silent
        # (direct-edit mode owns its own git hygiene and never invokes Opus).
        if [[ "$prompt" =~ ^/(docs-workflows:)?document[[:space:]]+[A-Z][A-Z0-9]+-[0-9]+ ]]; then
            emit_specs_context
        fi
        ;;
    release-notes)
        # Keyed, specs + repos context.
        emit_specs_context
        ;;
    *)
        # Unreachable given the regex; exit silently if the regex is ever widened.
        exit 0
        ;;
esac

exit 0
