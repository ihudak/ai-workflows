# /note

**Rule: Ask, don't guess.** Use `choices` arrays; 2–4 options, and never author an "Other" option.

## Phase 0

**Strip the run flags first.** Execute `strip-run-flags` on `$ARGUMENTS`.

**Load the question rules.** Load `escalation-rules core` now, with `Skill(skill: "workflows-core:reference", args: "escalation-rules core")`, before this run asks the user anything: every question it asks follows them — two to four options, presented verbatim with the `(Recommended)` marker where one is recommended, and a selection that carries no text.

## Phase 1

Resolve the fields, then confirm them with the user in one grouped prompt (2–4 options; the harness
supplies the free-text escape).
