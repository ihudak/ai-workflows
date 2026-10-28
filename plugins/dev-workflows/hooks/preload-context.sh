#!/usr/bin/env bash
# Fires on every message submission. Matches /implement and /vuln bare or
# prefixed with this plugin's own namespace (e.g. /dev-workflows:implement),
# and /upgrade in the QUALIFIED form only — see the note above the regexes for
# why — and routes per spec §3:
#   • /implement, /vuln, /upgrade       → full (model-routing + git status +
#                                         recent commits + small-repo directory
#                                         listing); /implement also preloads
#                                         specs context when its argument is a
#                                         address (keyed — /implement resolves
#                                         its own argument via resolve-address)
#
# /epics moved to the companion product-workflows plugin along with the command
# itself. Its preload row — specs + repos context, no model-routing, no full
# status/log, no directory listing — now ships from product-workflows's own
# preload-context.sh, carried across intact rather than re-derived.
#
# emit_specs_context surfaces $SPECS_PATH; /implement reads no $REPOS_PATH, so it is not shown.
#
# Two sibling plugins each ship a hook of this name, matching only their own
# commands: docs-workflows covers /document and /release-notes;
# product-workflows covers /epics. A UserPromptSubmit hook fires whichever
# plugin ships it, so all three run on every prompt. Disjointness holds two
# ways at once: the bare-command alternations share no command name across the
# three plugins, and the plugin-name prefix each regex accepts is a literal,
# distinct string per plugin — required rather than optional for the two
# commands that collide with a Claude Code built-in (/upgrade here,
# /release-notes in docs-workflows) — so no single prompt can match more than
# one of the three.
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

# Require at least one non-whitespace, non-flag argument so bare `/implement`
# or `/implement --help` doesn't inject noise on every misfire. The optional
# first capture group holds this plugin's own namespace prefix when the
# caller used the qualified form; the second holds the command token (e.g.
# "implement", "upgrade") — see spec §3 "Hook scope" for the normative regex.
# `upgrade` is matched in the QUALIFIED form only, and that is not an oversight.
# Claude Code ships its own built-in /upgrade, and the built-in wins: a bare
# `/upgrade` never reaches this plugin, so preloading for it would inject a repo
# scan into a run that is not ours. `/implement` and `/vuln` have no built-in of
# the same name, so both forms reach us and both are matched. Group 2 holds the
# command token in either branch -- keep that true if you edit these.
if [[ "$prompt" =~ ^/(dev-workflows:)?(implement|vuln)[[:space:]]+[^[:space:]-] ]]; then
    :
elif [[ "$prompt" =~ ^/(dev-workflows:)(upgrade)[[:space:]]+[^[:space:]-] ]]; then
    :
else
    exit 0
fi
cmd="${BASH_REMATCH[2]}"

# --- helpers -------------------------------------------------------------
emit_model_routing() {
    echo "Model routing: classify task as SIMPLE / MODERATE / SIGNIFICANT / HIGH-RISK before planning."
    echo "  SIGNIFICANT / HIGH-RISK -> plan with risk-planner (Opus), code-review (Opus)"
    echo "  BEFORE running tests; /implement also sends MODERATE work to code-review,"
    echo "  with no risk-planner. Invoke each by subagent_type — Agent(subagent_type:"
    echo "  dev-workflows:risk-planner) and Agent(subagent_type: dev-workflows:code-review)"
    echo "  — each frontmatter-pinned to Opus, so add no model: override unless"
    echo "  --enforce-model is set."
    echo "  Full rules: invoke the workflows-core:model-routing skill, which loads"
    echo "  workflows-core:model-routing/classification from the companion plugin."
}

emit_git_full() {
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo "Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
        echo "Status:"
        git status --short 2>/dev/null | head -20
        echo "Recent commits:"
        git log --oneline -5 2>/dev/null
    else
        echo "(not a git repository)"
    fi
}

emit_git_branch_if_repo() {
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo "Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
    fi
}

emit_dir_listing_if_small() {
    local entry_count
    entry_count=$(ls -1 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$entry_count" -le 30 ]]; then
        echo "Directory:"
        ls -1 2>/dev/null | head -20
    fi
}

emit_specs_context() {
    echo "=== Auto-injected project context (specs workflow) ==="
    if [[ -n "${SPECS_PATH:-}" ]]; then
        echo "SPECS_PATH: $SPECS_PATH"
    else
        echo "SPECS_PATH: (not set — a command that needs it asks for it)"
    fi
    emit_git_branch_if_repo
}

# --- per-command routing (spec §3 table) ---------------------------------
case "$cmd" in
    implement|vuln|upgrade)
        # Full — code / security / upgrade benefit from full git context + model-routing.
        echo "=== Auto-injected project context ==="
        emit_model_routing
        emit_git_full
        emit_dir_listing_if_small
        # /implement <address> is keyed — it resolves its own argument via
        # resolve-address; also preload specs context here.
        if [[ "$cmd" == "implement" && "$prompt" =~ ^/(dev-workflows:)?implement[[:space:]]+[A-Z][A-Z0-9]+-[0-9]+ ]]; then
            emit_specs_context
        fi
        ;;
    *)
        # Unreachable given the regex; exit silently if the regex is ever widened.
        exit 0
        ;;
esac

exit 0
