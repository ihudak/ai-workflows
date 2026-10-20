# /use

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

These shared references load by part — `alpha`. A citation of one names a rule:
before applying it, load the part that holds it,
`Skill(skill: "workflows-core:reference", args: "<name> <part>")`, the part its
rule index names (`args: "<name> index"` loads the index; every part carries
it), unless that part is already in this conversation. A citation that names no
rule the index holds loads the whole reference, `args: "<name>"`. Never apply a
rule of these references from memory.

## Phase 1

Load the pickers: `Skill(skill: "workflows-core:reference", args: "alpha pickers")`.

Load the index: `Skill(skill: "workflows-core:reference", args: "alpha index")`.

Load a part that does not exist: `Skill(skill: "workflows-core:reference", args: "alpha nosuch")`.

Load the private part: `Skill(skill: "workflows-core:reference", args: "alpha maintainer")`.
