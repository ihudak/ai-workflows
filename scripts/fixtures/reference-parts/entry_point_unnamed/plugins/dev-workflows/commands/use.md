# /use

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

These shared references load by part — `alpha`. A citation of one names a rule:
before applying it, load the part that holds it,
`Skill(skill: "workflows-core:reference", args: "<name> <part>")`, the part its rule
index names, unless that part is already in this conversation word for word; never
guess a part's name — until you hold the index (every part carries it), load it with
`args: "<name> index"`. A citation that names no rule the index holds loads the whole
reference, `args: "<name>"`. Never apply a rule of these references from memory.

## Phase 1

Ask the user to pick a value, and normalise a free-text answer per
`workflows-core:alpha`'s *Closed-vocabulary
pickers*.

## Phase 2

Run `Skill(skill: "workflows-core:reference", args: "steps specs-preflight")`.

Load `Skill(skill: "workflows-core:reference", args: "steps shortlist")`.

Run `Skill(skill: "workflows-core:reference", args: "steps resolve")`.

Run `Skill(skill: "workflows-core:reference", args: "steps run")`.

Run `Skill(skill: "workflows-core:reference", args: "steps fenced-step")`.

Run `Skill(skill: "workflows-core:reference", args: "steps kind")`.
