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

Normalise per `workflows-core:alpha`'s *Closed-vocabulary pickers*.

Stop per `workflows-core:alpha`'s **Key dir not found**.

Normalise per `workflows-core:alpha`'s `Closed-vocabulary pickers`.

Stop per `workflows-core:alpha` ("Key dir not found").

Present the list per `workflows-core:alpha` (“Choice lists are presented verbatim”).

Stop per `workflows-core:alpha` §2.

Stop per `workflows-core:alpha` § Key dir not found, and name the key.

Normalise per `workflows-core:alpha` § Picker rules.

Normalise per `workflows-core:alpha`, e.g. *Closed-vocabulary pickers*.

Apply *Closed-vocabulary pickers*. Then see `workflows-core:alpha`.

Apply *Closed-vocabulary pickers* first. `workflows-core:alpha` says why.

Stop per *Key dir not found.* `workflows-core:alpha` says why.
