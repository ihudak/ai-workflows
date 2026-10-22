# /ask

## Phase 0

```markdown
**Load the question rules.** Load `escalation-rules core` now, with `Skill(skill: "workflows-core:reference", args: "escalation-rules core")`, before this run asks the user anything: every question it asks follows them — two to four options, presented verbatim with the `(Recommended)` marker where one is recommended, and a selection that carries no text.
```

## Phase 1

Ask the user which way to go, `choices: ["Go on (Recommended)", "Stop"]`.
