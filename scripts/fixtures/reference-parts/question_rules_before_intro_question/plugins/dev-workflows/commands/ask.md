# /ask

**Strip the run flags first.** Execute `strip-run-flags` on `$ARGUMENTS`.

**The model gate runs next.** Where the session is below Opus, ask
`choices: ["Stop — relaunch on Opus (Recommended)", "Go on anyway"]`.

## Phase 0

**Load the question rules.** Load `escalation-rules core` now, with `Skill(skill: "workflows-core:reference", args: "escalation-rules core")`, before this run asks the user anything: every question it asks follows them — two to four options, presented verbatim with the `(Recommended)` marker where one is recommended, and a selection that carries no text.

Ask the user which way to go, `choices: ["Go on (Recommended)", "Stop"]`.
