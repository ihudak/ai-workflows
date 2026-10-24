# /note

**Rule: Ask, don't guess.** Use `choices` arrays; 2–4 options, and never author an "Other" option.

## Phase 0

**Strip the run flags first.** Execute `strip-run-flags` on `$ARGUMENTS`.

## Phase 1

Resolve the fields, then confirm them with the user in one grouped prompt (2–4 options; the harness
supplies the free-text escape).
