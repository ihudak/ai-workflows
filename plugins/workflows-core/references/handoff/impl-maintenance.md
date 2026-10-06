# impl-maintenance Handoff Format

## Input (impl orchestrator → impl-maintenance)

The caller passes a **compact session handoff**:

```markdown
Session handoff:
- Command run: /implement
- What was done: [1-paragraph summary — classification, component/CVE/task, scope]
- Key events: [BLOCK reviews, test regressions, missing reference docs, workarounds needed, ambiguities that required user clarification, surprising compatibility issues — or "none"]
- Workarounds used: [manual steps the workflow could not automate — or "none"]
- Review verdict: [PASS | PASS WITH RECOMMENDATIONS | BLOCK (+ what the BLOCK was) | N/A]
- Test result: [passed | regressions | not run]
- Project root: [absolute path]
```

`Command run` is the command variant that executed, named as the caller names it
(`/document` additionally naming its mode). The callers are the authority on the
value; it is not drawn from a list held here. It
scopes any "Command workflow improvements" suggestions to the right command.
If `Command run` is missing from the handoff, default to
`/implement` (the canonical code workflow) and note the substitution in the
report's `### Session summary` so the caller notices and updates their
invocation.

Under `--skip-feedback` (`workflows-core:run-flags` §4), the orchestrator sends this same handoff shape, plus a `Plugin root:` field naming its own `${CLAUDE_PLUGIN_ROOT}`, to `workflows-core:defect-reporter` instead of this agent.

## Output (impl-maintenance → impl orchestrator)

Return this exact shape (no preamble, no chatter):

```markdown
## Session Learnings

### Session summary
[1–2 sentences on what was done and the overall outcome]

### Key observations
- [What happened / what was unexpected — one bullet per event]
- ...
- _or_ "No notable events — session followed standard workflow"

### Suggested improvements

#### CLAUDE.md rules
- **Rule**: [proposed rule text, ready to paste]
  **Rationale**: [why this would have helped]
  **Why not a check**: [what makes this a judgement call no script could decide]
  **Scope**: [project-level CLAUDE.md | global ~/.claude/CLAUDE.md]
- **Remove**: [the no-op instruction, quoted]
  **Grounds**: [the key event it failed to prevent, and that it names no action an agent could take or omit]
  **Scope**: [project-level CLAUDE.md | global ~/.claude/CLAUDE.md]
- ...
- _or_ "No new rules suggested"

#### Rules that existed but were not followed
- **Rule**: [the existing instruction, quoted]
  **Where**: [file:line — a project or global CLAUDE.md, a rules file, or a family plugin's command, agent, skill or reference]
  **What happened**: [the key event that broke it]
  **Why missed**: [not loaded | ambiguous | contradicted by <file:line> | read but not applied | undetermined: <the candidates>]
  **Fix**: [the change and the file it touches — a check, a move or scope change, a rewrite, the pair fixed at the source — or "none: no check could catch it"]
- ...
- _or_ "No unfollowed rules found"

#### Hooks and checks
- **Check**: [a hook with its trigger (e.g. UserPromptSubmit, PostToolUse:Bash), a lint rule, a CI job or a gate script]
  **Purpose**: [what it would do]
  **Rationale**: [why this would help]
- ...
- _or_ "No new hooks or checks suggested"

#### Reference docs
- **File**: [path, e.g. ${CLAUDE_PLUGIN_ROOT}/references/session-hygiene.md]
  **Change**: [what to add or update]
  **Rationale**: [what was missing that caused the workaround or ambiguity]
- **Remove**: [the no-op instruction, quoted]
  **File**: [path of the plugin reference that carries it]
  **Grounds**: [the key event it failed to prevent, and that it names no action an agent could take or omit]
- ...
- _or_ "No reference doc gaps found"

#### New agents / skills
- **Agent**: [proposed name and one-line description]
  **Purpose**: [what task it would handle; why it should be reusable]
  **Suggested tools**: [list]
- ...
- _or_ "No new agents suggested"

#### Command workflow improvements
- **Command**: [the command whose workflow would change, named as the handoff named it, e.g. /implement]
  **Section**: [Phase / step reference]
  **Change**: [what to change and why]
- ...
- _or_ "No command improvements suggested"

### Priority
[HIGH — multiple observations point to the same gap | MEDIUM — single clear gap | LOW — minor polish only]
```

This agent is suggest-only — it never writes, edits, or creates a file. The caller (the invoking command) is responsible for acting on any of the suggestions above.
