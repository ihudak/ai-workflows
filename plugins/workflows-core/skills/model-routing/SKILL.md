---
name: model-routing
description: Loads the plugin family's task-complexity classification rules and model fallback chain (workflows-core:model-routing/classification). Invoked at the classification step by every pipeline command across the family, so each loads one copy of the rules from one named entry point rather than citing the file by its own path.
user-invocable: false
allowed-tools: Read
---

# Model routing

The authoritative classification rules and model fallback chain are in:

`${CLAUDE_PLUGIN_ROOT}/references/model-routing/classification.md`

Work from that file's own words, never from memory or a summary. The text
this request needs is the whole file, and a read of some of its lines — a
section, a range, a search — covers no request. Where the text this request
needs is already in this conversation word for word, from a read made in this
run, work from that text and read nothing, within one bound: classifying
executes that file, so reuse an earlier read to classify only where that read
was made in the current phase — a `## Phase` of your command, a `Step` of a
command numbered by steps, or, for an agent, its whole dispatch, since an
agent's run is one unit — and read it again otherwise; to look up a rule of
it, any read in this run serves. Read it whenever those words are not in
front of you now, whatever removed them — it was never read, only a different
part of it was read, or an earlier read has since been replaced by a summary
or cleared; a summary of a reference is never its text. Where you cannot
tell, read it. Reading the whole file means reading every line of it: where
one read cannot hold it, read it in consecutive ranges up to its last line.

Whether the text was read now or is already in this conversation, classify
the current task as exactly one of `SIMPLE`, `MODERATE`, `SIGNIFICANT`, or
`HIGH-RISK` using the criteria in that file, and apply the model fallback chain
and `model_routing` handoff block it defines. That file is the single source of
truth — do not paraphrase or summarise its contents here.

Under `--enforce-model` (`run_flags.enforced_model`), apply §10 of that file, which overrides every chain resolution.
