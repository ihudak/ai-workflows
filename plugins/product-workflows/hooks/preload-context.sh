#!/usr/bin/env bash
# Fires on every message submission. Matches the one command this plugin ships
# that injects context, /epics — bare or prefixed with this plugin's own
# namespace (e.g. /product-workflows:epics) — and routes it:
#   • /epics                            → $SPECS_PATH + $REPOS_PATH default
#                                         + git branch only if cwd is inside
#                                         a git repo (no model-routing, no full
#                                         status/log, no directory listing). It
#                                         is keyed and resolves its own
#                                         address or specs-directory argument
#                                         via resolve-address.
#
# emit_specs_context surfaces $SPECS_PATH alongside $REPOS_PATH. The function
# is already byte-identical across dev-workflows and docs-workflows (verified
# by diff); this is the third copy, following established precedent rather
# than a new design decision. Sharing it is not available: a hook runs as
# `bash "${CLAUDE_PLUGIN_ROOT}/hooks/<script>"`, and that variable resolves to
# the reading plugin, so a hook cannot source a sibling plugin's file — a
# dependency grants installation, never file access.
#
# Two sibling plugins each ship a hook of this name, matching only their own
# commands: dev-workflows covers /implement, /vuln and /upgrade;
# docs-workflows covers /document and /release-notes. A UserPromptSubmit hook
# fires whichever plugin ships it, so all three run on every prompt.
# Disjointness holds two ways at once: the bare-command alternations share no
# command name across the three plugins, and the plugin-name prefix each regex
# accepts is a literal, distinct string per plugin — required rather than
# optional for the two commands that collide with a Claude Code built-in
# (/upgrade in dev-workflows, /release-notes in docs-workflows) — so no single
# prompt can match more than one of the three.
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

# Require at least one non-whitespace, non-flag argument so bare `/epics` or
# `/epics --help` doesn't inject noise on every misfire. The optional first
# capture group holds this plugin's own namespace prefix when the caller used
# the qualified form; the second holds the command token ("epics").
if [[ ! "$prompt" =~ ^/(product-workflows:)?(epics)[[:space:]]+[^[:space:]-] ]]; then
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
    echo "repos_path: ${REPOS_PATH:-/workspace} (default — the command will confirm or ask)"
    if [[ -n "${SPECS_PATH:-}" ]]; then
        echo "SPECS_PATH: $SPECS_PATH"
    else
        echo "SPECS_PATH: (not set — the command will ask)"
    fi
    emit_git_branch_if_repo
}

# --- per-command routing -------------------------------------------------
case "$cmd" in
    epics)
        # Keyed, specs + repos context.
        emit_specs_context
        ;;
    *)
        # Unreachable given the regex; exit silently if the regex is ever widened.
        exit 0
        ;;
esac

exit 0
