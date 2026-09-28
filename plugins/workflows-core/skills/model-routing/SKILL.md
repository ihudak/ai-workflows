---
name: model-routing
description: Load the plugin family's task-complexity classification rules and model fallback chain. Invoked at the classification step by the 26 pipeline commands (`/implement`, `/document`, `/epics`, `/release-notes`, `/vuln`, `/upgrade`, `/docs-profile`, `/docs-init`, `/docs-brand`, `/docs-audit`, `/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/design`, `/ready`, `/frames`, the effort-proposal pair `/prd-proposal` and `/brd-proposal`, and the BRD-to-PRD route's `/brd-intake`, `/brd-split`, `/prd-ground`, `/brd-interview`, `/brd-package` and `/brd-reconcile`), so every pipeline command across the family loads one copy of the rules from one named entry point, rather than each citing the file by its own path.
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
