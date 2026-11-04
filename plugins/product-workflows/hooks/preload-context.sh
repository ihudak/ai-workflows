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
# is byte-identical to docs-workflows' copy; dev-workflows' copy differs only by
# omitting the REPOS_PATH lines, since /implement reads no $REPOS_PATH. This is
# the third copy, following established precedent rather than a new design
# decision. Sharing it is not available: a hook runs as
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

# Match the command token. The optional first capture group holds this
# plugin's own namespace prefix when the caller used the qualified form; the
# second holds the command token ("epics").
if [[ ! "$prompt" =~ ^/(product-workflows:)?(epics)([[:space:]]+|$) ]]; then
    exit 0
fi
cmd="${BASH_REMATCH[2]}"

# Skip the leading flags, then require an argument, so a bare `/epics` or
# `/epics --help` doesn't inject noise on every misfire. A command strips its
# run flags wherever they stand (workflows-core:run-flags §3), and its own
# flags may come first too, so the argument is the first token after the
# leading run of tokens opening with `-`. A bare `--enforce-model` takes the
# token after it as its value (the pair form, run-flags §1), so that token is
# skipped with it. A command's own flag that takes a separate value
# (`/epics --docs <path>`) leaves its value as the argument, which is still an
# argument.
# The same block stands in dev-workflows' and docs-workflows' hooks.
args="${prompt:${#BASH_REMATCH[0]}}"
while :; do
    args="${args#"${args%%[![:space:]]*}"}"
    if [[ "$args" =~ ^--enforce-model[[:space:]]+[^[:space:]]+ || "$args" =~ ^-[^[:space:]]* ]]; then
        args="${args:${#BASH_REMATCH[0]}}"
    else
        break
    fi
done
[[ -n "$args" ]] || exit 0

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
        echo "SPECS_PATH: (not set — a command that needs it asks for it)"
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
