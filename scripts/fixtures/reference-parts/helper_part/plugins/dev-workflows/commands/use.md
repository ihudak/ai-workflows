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

Word the answer per `workflows-core:alpha`'s *Wording*.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")` and word the answer per its *Wording*.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha wording")` and word the answer.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha stops")` and word the answer per its *Wording*.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha stops")`. Then normalise the answer per *Closed-vocabulary pickers* and word it per *Wording*.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha stops")` and normalise the answer per *Closed-vocabulary pickers*, worded per its *Wording*.
