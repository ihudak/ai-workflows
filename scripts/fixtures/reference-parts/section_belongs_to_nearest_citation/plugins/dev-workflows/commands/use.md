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

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")` §1 and normalise per its *Closed-vocabulary pickers*, then invoke `Skill(skill: "workflows-core:reference", args: "gamma commit")` and run its `commit` entry point (§4) inline.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")`. Then invoke `Skill(skill: "workflows-core:reference", args: "gamma commit")` and run its entry point (§4) inline.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")` and stop per `workflows-core:gamma` §4.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")` and stop per `dev-workflows:delta` §4.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")` and read `references/delta.md` §4.

Invoke `Skill(skill: "workflows-core:reference", args: "alpha pickers")`. Then stop as §4 says.

Write it per `Skill(skill: "workflows-core:reference", args: "alpha pickers")` §4.
