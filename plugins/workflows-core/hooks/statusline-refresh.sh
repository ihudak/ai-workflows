#!/usr/bin/env bash
# Fires at every session start. Brings the status line /workflows-core:statusline installed up to
# the script this plugin version ships, so a plugin update reaches it with no re-run.
# Replaces only a copy that still matches the fingerprint the install recorded: a copy edited by
# hand, or one installed before fingerprints existed, is never touched. Prints nothing.
# Always exits 0 — must never block Claude.

src="${CLAUDE_PLUGIN_ROOT:-}/scripts/statusline-command.sh"
dir=~/.claude/dev-workflows
inst="$dir/statusline-command.sh"
rec="$dir/statusline-command.sh.sha256"

sha() {
    if command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" 2>/dev/null | cut -d' ' -f1
    elif command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" 2>/dev/null | cut -d' ' -f1
    fi
}

refresh() {
    [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && [ -s "$src" ] && [ -f "$inst" ] || return 0
    new=$(sha "$src"); [ -n "$new" ] || return 0
    if cmp -s "$src" "$inst"; then
        # Already current: record it, so the next update can replace it.
        [ "$(cat "$rec" 2>/dev/null)" = "$new" ] || printf '%s\n' "$new" > "$rec"
        return 0
    fi
    [ -f "$rec" ] || return 0
    [ "$(sha "$inst")" = "$(cat "$rec" 2>/dev/null)" ] || return 0
    tmp="$inst.tmp.$$"
    cp "$src" "$tmp" && chmod +x "$tmp" && cp -p "$inst" "$inst.prev" && mv -f "$tmp" "$inst" \
        && printf '%s\n' "$new" > "$rec"
    rm -f "$tmp"
}

refresh >/dev/null 2>&1
exit 0
