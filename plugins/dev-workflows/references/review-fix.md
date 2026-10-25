# Review fix — Shared Reference

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

These shared references load by part — `escalation-rules`, `finding-triage`, `next-phase-offer` and `session-hygiene`. A citation of one names a rule: before applying it, load the part that holds it, `Skill(skill: "workflows-core:reference", args: "<name> <part>")`, the part its rule index names, unless that part is already in this conversation word for word; never guess a part's name — until you hold the index (every part carries it), load it with `args: "<name> index"`. A citation that names no rule the index holds loads the whole reference, `args: "<name>"`. Never apply a rule of these references from memory.

Single source of truth for how a fixer applies the findings of a `code-review` report and what it returns: the *Fix method* and the `## Fix Report` shape. Read by `review-fixer`; by `test-writer` on `mode: review`, on test files only; and by `code-writer` on `mode: review`, on its writer unit's non-test files only.

A writer that applies this method to the files it owns applies it only to those files: a finding whose fix lands in a file it does not own is deferred as `DEFERRED — needs human decision` with that as the reason, so the caller re-routes it. In the method below, "Inputs" and the bold terms **Severities to fix**, **User-applied** and **Plan ruling** name what the dispatching caller passes; for each the caller does not pass, its default holds: **Severities to fix** is `BLOCKER` and `MAJOR` (`MINOR` only when the caller names it, never `NIT`); with no **User-applied** line, no NIT is fixed, since a NIT is fixed only where such a line names it; and with no **Plan ruling**, every plan-conflict finding is deferred as step 2 says.

## Fix method

1. Parse all findings from the review output. Group by file.
2. **For each BLOCKER finding:**
   - Check if it is **locally actionable**: a concrete change at a specific
     `path:line` that fixes a code, config, or test problem.
   - Fix it if locally actionable.
   - If the finding requires design change, migration sequencing,
     rollout/rollback/process change, or cross-cutting test strategy across
     multiple subsystems — it cannot be safely auto-fixed. Flag as
     `"DEFERRED — needs human decision"` with a clear reason.
   - If a finding **contradicts the approved plan** (the plan explicitly
     mandated the thing the finding objects to), do NOT auto-fix against the
     plan and do NOT bury it in a generic "other" defer. Flag it
     `DEFERRED — plan-conflict` (the approved plan mandated this; needs a
     human ruling on which governs). A finding a **Plan ruling** names is the exception:
     the ruling is that human ruling.
3. **For each MAJOR finding:** same rule. Fix if locally actionable, defer if
   not.
4. **For each MINOR finding** (only where the caller's **Severities to fix**
   names `MINOR`): same rule as a MAJOR — fix it if locally actionable, defer it
   if not, whatever the length of the fix. The patch gate and the plan-conflict
   deferral bind it as they bind a MAJOR.
5. **Skip all NIT findings entirely**, save one a **User-applied** line names
   (Inputs). Do not mention a skipped one in the fix report.
6. When fixing:
   - Make the minimal change that addresses the finding's suggestion, and add no new logic beyond
     what the suggestion explicitly requires.
   - Modify no file that is not named in a finding's `path:line` location, or in an
     `also at path:line` its observation adds for a fix that spans two files. A fix that needs
     another file is deferred as `DEFERRED — needs human decision`, naming that file.
   - Apply the **patch gate** (`Skill(skill: "workflows-core:reference", args: "finding-triage patch-gate")`): the fix must add no
     public surface, **guard no state the finding did not demonstrate**, and edit no instruction file the
     gate names (`CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, a file under
     `.claude/rules/` or `.github/instructions/`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`) unless the
     finding's own location is in that file — the test is the finding's location, never a diff, which
     not every fixer is handed: a finding located in such a file is one the review raised against
     that file's own text. If the smallest correct fix
     would add such a guard or make such an edit, defer it as `DEFERRED — needs human decision` with
     that as the reason: never add speculative defence, and never edit such a file to make a finding
     go away.
   - Do not refactor surrounding code or fix unrelated issues.
   - If multiple findings touch the same location, apply them in order;
     re-read the file between edits to avoid stale hunks.
7. After all fixes are applied, re-read each changed file end-to-end to confirm
   the edits are syntactically correct and coherent.

## Output

Return this exact shape (no preamble):

```markdown
## Fix Report

### Applied
- [SEVERITY] `path:line` — [observation summary] → [what was changed]
- ...
- _or_ "none"

### Deferred
- [SEVERITY] `path:line` — [observation summary] → [reason: design change / migration / process / cross-cutting test strategy / plan-conflict / other]
- ...
- _or_ "none"

### Files changed
- path/to/file.ext
- ...
- _or_ "none"

### Stop condition flag
[CLEAR — all BLOCKER findings were applied | NEEDS HUMAN — [count] BLOCKER finding(s) and/or any plan-conflict finding deferred; human decision required before re-review]
```
