# Workflow

`workflows-core` runs no pipeline of its own. It is the shared foundation the `dev-workflows` plugin family draws on — the reference corpus, the `model-routing` skill, and eight agents — plus seven commands that sit beside a pipeline rather than inside one.

```mermaid
flowchart TD
    subgraph CORPUS["What every sibling plugin reads"]
        refs["references/ — addressing, git + phase handoff, escalation, triage, emission"]:::core
        loader["skills/reference — the loader a sibling reads the corpus through"]:::core
        skill["skills/model-routing"]:::core
        agents["agents/ — architecture-grounder · code-scanner · defect-reporter · doc-fixer · docs-grounder · frame-describer · impl-maintenance · session-analyst"]:::core
    end
    subgraph CROSS["Cross-cutting commands"]
        setup["/workflows-core:statusline — install the status line"]:::core
        repair["/frames — (re)build a design/ frame-set index"]:::core
        improve["/feedback · /prompt · /prompt-brainstorm · /prompt-grill-me"]:::core
        diagnose["/diagnose-session — why a run went wrong, with evidence"]:::core
    end
    pipeline["a sibling plugin's pipeline command"]:::other

    refs --> loader
    loader --> pipeline
    skill --> pipeline
    agents --> pipeline
    pipeline -->|a bad result you corrected| improve
    pipeline -.->|its transcripts| diagnose
    diagnose -.->|a summary you choose to log| improve
    setup -.->|cost cross-check| pipeline
    repair -.->|"a readable frame-set index — design grounding in /product-workflows:prd-ground needs one"| pipeline

    classDef core fill:#ede9fe,stroke:#6d28d9,color:#4c1d95
    classDef other fill:#f3f4f6,stroke:#6b7280,color:#1f2937
```

The three dashed and solid edges into `a sibling plugin's pipeline command` are the whole point of this plugin: a command in `dev-workflows`, `product-workflows`, or `docs-workflows` reads a reference here, loads the routing skill here, and dispatches an agent here, so the same rules bind every plugin in the family rather than being copied into each.

**`skills/reference` is why the corpus edge goes through a node instead of straight across**, and it is the mechanism the whole split turns on. `${CLAUDE_PLUGIN_ROOT}` resolves to the *reading* plugin, so a sibling cannot open a file in `references/` by path — its own plugin root names itself. It calls `Skill(skill: "workflows-core:reference", args: "<name>")` instead, and the skill resolves the path on the caller's behalf. `skills/model-routing` is the same trick applied to one specific reference, kept separate because the classification rules are loaded at one fixed point in every pipeline command and a named skill says so where an argument string does not. Both are listed in [References and skills](reference/references.md#skills).

## Cross-cutting commands

These run outside any role pipeline, at any time:

- **Plugin improvement.** `/feedback` logs a note about the plugin itself; `/prompt`, `/prompt-brainstorm`, and `/prompt-grill-me` turn a correction you just made into logged feedback plus a fix — applied directly, redesigned with `superpowers:brainstorming`, or grilled inline.
- **Session diagnosis.** [`/diagnose-session`](commands/diagnose-session.md) reads a session's transcripts — this one, or a past one — and reports what happened in a run that went wrong, a `path:line` behind every finding. It says whether the family was involved and where, proposes no fix, and leaves you a ready-to-run `/feedback` line when it was.
- **Setup.** `/statusline` installs the family's multi-line status line. It collides with a Claude Code built-in of the same name, so type the qualified `/workflows-core:statusline`.
- **Specs-tree repair.** [`/frames`](commands/frames.md) (re)builds the frame-set index of any folder holding exported design frames — a BRD, PRD, or Epic folder alike — so a set somebody dropped in by hand becomes readable. It advances no phase and grounds nothing.

None of the seven advances a pipeline phase. What six of them share with the pipeline is the cost ledger: five are charged to the phase of the command they are correcting or the folder they are acting on, `/diagnose-session` to `plugin-feedback`, while `/statusline` emits no cost entry at all — see [Roles and phases](roles-and-phases.md).

For every command of the four plugins on one diagram — by role, coloured by plugin, with the deliverable each hands the next — see the [Family map](family-map.md).

See the [documentation index](README.md) for everything else.
