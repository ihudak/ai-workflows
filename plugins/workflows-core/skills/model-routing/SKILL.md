---
name: model-routing
description: Loads the plugin family's task-complexity classification rules and model fallback chain (workflows-core:model-routing/classification). Invoked at the classification step by every pipeline command across the family, so each loads one copy of the rules from one named entry point rather than citing the file by its own path.
user-invocable: false
allowed-tools: Read
---

# Model routing

Read the authoritative classification rules and model fallback chain:

`${CLAUDE_PLUGIN_ROOT}/references/model-routing/classification.md`

Then classify the current task as exactly one of `SIMPLE`, `MODERATE`,
`SIGNIFICANT`, or `HIGH-RISK` using the criteria in that file, and apply the
model fallback chain and `model_routing` handoff block it defines. That file is
the single source of truth — do not paraphrase or cache its contents here.

Under `--enforce-model` (`run_flags.enforced_model`), apply §10 of that file, which overrides every chain resolution.
