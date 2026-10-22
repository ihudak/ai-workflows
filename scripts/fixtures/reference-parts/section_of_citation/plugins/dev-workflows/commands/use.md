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

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")` and stop per §4 of `workflows-core:gamma`.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")` and stop per § Key dir not found of `workflows-core:gamma`.

Invoke `Skill(skill: "workflows-core:reference", args: "gamma commit")` and stop per §4 of `Skill(skill: "workflows-core:reference", args: "alpha pickers")`.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")` and stop per §4 of `references/gamma.md`.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")` and apply §4 to every key of `workflows-core:gamma`.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")` and apply § Key dir not found to the keys of `workflows-core:gamma`.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")` and stop per §4 for each folder of `references/gamma.md`.

Invoke `Skill(skill: "workflows-core:reference", args: "gamma commit")` and stop per § Key dir not found of `workflows-core:alpha`.

Invoke `Skill(skill: "workflows-core:reference", args: "gamma commit")` and stop per § Stop rule of `workflows-core:alpha`.

Invoke `Skill(skill: "workflows-core:reference", args: "gamma commit")` and stop per § Missing key of `workflows-core:alpha`.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")` and stop per § Key dir not found of `${CLAUDE_PLUGIN_ROOT}/references/delta.md`.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")` and stop per § Key dir not found of `dev-workflows:delta`.
