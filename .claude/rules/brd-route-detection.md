---
paths:
  - "plugins/product-workflows/commands/create-prd.md"
  - "plugins/product-workflows/commands/create-ard.md"
  - "plugins/product-workflows/commands/specify.md"
  - "plugins/product-workflows/docs/commands/create-prd.md"
  - "plugins/product-workflows/docs/commands/create-ard.md"
  - "plugins/product-workflows/docs/commands/specify.md"
---

# BRD route — route detection

Loaded when `/create-prd`'s, `/create-ard`'s or `/specify`'s command file or docs page is read — the three commands the invariant below binds. Split out of `.claude/rules/brd-route.md` to keep that file under 20,000 characters; the route's map lines and its other invariants are there; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## Invariants

- **The BRD route is detected, never declared.** `/create-prd`, `/create-ard` and `/specify` each take one positional address; where it resolves to a folder carrying `brd-link.md`, the run is on the BRD route and says so before doing anything. There is no flag: one that could disagree with the folder it names is one more disagreement to have. The seeds are altitude-partitioned and non-interchangeable — `prd-seed.md` is `/create-prd`'s, `ard-seed.md` `/create-ard`'s, `spec-seed.md` `/specify`'s — and `prd-format.md`'s no-implementation-detail rule is **not** relaxed on that route: sub-product-altitude content is what the ARD and specification seeds exist to carry. `/create-prd` may fill what a seed leaves open and may **never** reopen a `[VD#n]` or `[CD#n]`; a customer signed those. `--from-prd` survives as a flag and is not symmetric with what was removed: it names a *different* PRD to seed from, which no folder can decide on the operator's behalf.
