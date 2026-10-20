---
name: model-routing
description: Loads the plugin family's task-complexity classification rules and model fallback chain (workflows-core:model-routing/classification). Invoked at the classification step by every pipeline command across the family, so each loads one copy of the rules from one named entry point rather than citing the file by its own path.
user-invocable: false
allowed-tools: Read
---

# Model routing

The authoritative classification rules and model fallback chain are in:

`${CLAUDE_PLUGIN_ROOT}/references/model-routing/classification.md`

Work from that file's own words, never from memory or a summary. Where its
text is already in this conversation word for word, from a read made in this
run, work from that text and read nothing. Read it otherwise: when it was
never read, when only part of it was read, or when a compaction has replaced
the earlier read with a summary — a summary of a reference is never its text.

Then classify the current task as exactly one of `SIMPLE`, `MODERATE`,
`SIGNIFICANT`, or `HIGH-RISK` using the criteria in that file, and apply the
model fallback chain and `model_routing` handoff block it defines. That file is
the single source of truth — do not paraphrase or summarise its contents here.

Under `--enforce-model` (`run_flags.enforced_model`), apply §10 of that file, which overrides every chain resolution.
