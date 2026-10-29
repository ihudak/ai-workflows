# /make

## Phase 0

Resolve the address with `workflows-core:addressing` §3 `resolve-address`.

**Check the branch the run stands on.** Execute `branch-check` (`Skill(skill: "workflows-core:reference", args: "phase-handoff branch-check")`, §6) on the resolved folder, with `prefix: design`; a stop it makes ends the run here.

## Phase 5 — Handoff

    choices: ["Branch + commit + push + open PR to main (Recommended)", "Just write the files — I'll handle git (the next phase will stop until this is on main)", "Cancel"]
