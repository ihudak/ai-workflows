# The evidence contract and the walkthrough spec

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

Single source of truth for what a documentation claim is allowed to rest on and how it is checked: the one interface with its two implementations (§1), the three evidence kinds and what each records (§2), what happens to a claim that could not be verified (§3), the walkthrough file (§4), and how a walkthrough is executed today and by a driver later (§5).

Consumed by `/docs-audit` (its `--refresh` reconciliation, §3), by `/docs-write`, which reads §3's page-level marker before it writes anything and tests each page for it at its commit step — both by `docs-iteration/backlog-run.md` §10's programs, which open this file — reads a unit's walkthrough at §4's home as data, and holds `doc-writer` and `doc-reviewer` to §2's entry shape and §3's markers through its unit brief (`docs-iteration/unit-brief.md`), and by `docs-audit-reviewer` (where some unit carries a non-empty `evidence[]`), and cited by `backlog-format.md` for the entry shape; `docs-auditor` and `ia-planner` do not read it — re-derive the set with `grep -rl evidence-contract plugins/docs-workflows/commands plugins/docs-workflows/agents`, which finds `docs-write.md` by the `DOCS_WRITE_NO_MARKER` line naming this file. And, as they ship, it is consumed by Spec 2's `/docs-capture` and `/docs-verify` and Spec 3's `/docs-drift`.

The page-`type` vocabulary and the audience split this file crosses are `${CLAUDE_PLUGIN_ROOT}/references/docs-audit/coverage-model.md`'s (§3); the `units[].walkthrough` field and the `status` a verification pass moves are `${CLAUDE_PLUGIN_ROOT}/references/docs-audit/backlog-format.md`'s (§1 and §3). Neither is restated here.

Its entry points, so a command can say which part it is executing: **the interface** (§1), **the three kinds** (§2), **the marked-claim rule** (§3), **the walkthrough file** (§4), and **execution** (§5).

---

## 1. One interface, two implementations

Both audiences answer the same four questions, and answer them differently. That is what makes this one contract rather than two: a command asks what template a page takes, where its evidence comes from, what resolves a claim and what signals drift, and gets an answer whichever audience it is writing for.

| | `audience: user` | `audience: engineering` |
|---|---|---|
| Template | Diátaxis quadrant | arc42/C4 section, MADR, runbook, generated API reference |
| Evidence source | Routes, views, i18n strings, plus a walkthrough | Code, config, ARDs and design docs from the specs repo |
| A claim is resolved by | **Observation** — a walkthrough step confirms it | **Code read** — delegated to `workflows-core:source-truth` |
| Drift signal | Behaviour change: routes, labels, flows | Structure change: interfaces, modules, dependencies |

**The two rows that matter most are the third and the fourth, and they are the reason the split exists.** A user-facing claim — a label, a menu path, an order of steps — is a claim about what somebody sees, and reading the code that renders it is not the same act as looking at it. An engineering claim is a claim about structure, which reading the code settles exactly and which no amount of clicking confirms. Resolving one with the other's method is how a page comes to be confidently wrong about the half nobody checked.

---

## 2. The three evidence kinds

A page records its sources in frontmatter, as `evidence:` entries. **Which keys a page carries is `references/docs-profiles/frontmatter-guidelines.md`'s** — it lists `evidence` among the page's fields and says what it is for. **The shape of an entry *inside* that block is this section's**, and that file states none of it: the `kind` vocabulary, the per-kind fields and the entry form below are defined here and nowhere else, so the two do not overlap and a maintainer changing an entry's shape edits this file.

| `kind` | Records | Re-checked by |
|---|---|---|
| `code` | `repo`, `path`, `ref` | Reading that path at that `ref`, and at the current one |
| `walkthrough` | `id` — the walkthrough's own id (§4) | Re-running the walkthrough |
| `artifact` | `path`, and `ref` — the commit it was read at | Reading that path at that `ref`, and at the current one |

```yaml
evidence:
  - { kind: code, repo: example-webapp, path: src/routes/orders/new.tsx, ref: <sha> }
  - { kind: walkthrough, id: W-001 }
  - { kind: artifact, path: specifications/PRD-EXAMPLE-1-orders/release-notes.md, ref: <commit> }
```

**`artifact` covers a claim whose source is neither code nor observation but a committed document** — a `/release-notes` draft under `$SPECS_PATH`, an ARD, a design doc. It is a third kind rather than a variety of `code` because the thing it points at is prose somebody wrote, which changes by being re-worded rather than by being re-implemented.

**It records `ref`, the commit it was read at, and that is the whole of why it is worth recording at all.** A path alone tells drift that a document exists; a path and a `ref` let drift tell a re-worded draft from an unchanged one. Without it there is no difference between "the source still says this" and "the source is still there", and only the first is evidence. **The path is recorded as the repository holding the document records it**, and is not narrowed to one repository: the three sources named above all live under `$SPECS_PATH` today, which is a fact about where this family's committed documents sit rather than a constraint on the kind.

---

## 3. A marked claim never becomes prose fact by default

**Individual sentences are not tracked.** A page's frontmatter records what the page as a whole rests on; nothing maintains a claim-to-sentence map, because one that has to be kept in step with every edit is wrong within two of them.

What *is* tracked is the exception: **a claim that could not be verified is marked inline, reusing the `[NEEDS CLARIFICATION]` vocabulary `/idea` already establishes.** The marker is in the prose, where a reader meets it, and it survives every edit that does not resolve it.

**The hard rule: a marked claim never becomes prose fact by default.** It is either confirmed by a verification pass — which removes the marker because it has resolved the claim — or it **ships visibly marked**, the prose reaching readers with the marker still in it. There is no third disposition, and in particular no disposition in which a marker is removed because the page is being published, or because the claim looks right, or because the marker is untidy.

**Shipping a marked page and marking its unit `published` are two different acts, and only the first is available while a marker stands.** Nothing stops a page being merged and deployed with markers on it — that is what "ships visibly marked" means, and it is better than holding the whole page back over one unresolved sentence. What it cannot do is move its unit to `published`, **by either of the two routes that reach that value**: the ordinary one runs through `verified`, which a page carrying marked claims has not reached, and the other — the `--refresh` reconciliation of a page against a unit still `missing` — **reads the page for markers and lands a marked one on `drafted` instead** (`backlog-format.md` §3). So `backlog-format.md` §5's coverage fraction, which counts `published` units, never counts a page with a marker in it — the page is live, and the grid still says the work is not done. This is what prevents the backlog reporting green on prose nobody checked.

**A backlog run's page carries one more marker, for the page as a whole.** A page a backlog run drafts from the product's code and specifications has had no claim resolved by its audience's method (§1) — a user page none, and an engineering page none beyond the reviewer's spot checks — so besides a marker on each claim its evidence does not ground, its first body line — after `<!-- docs-visibility: internal -->` on an internal page, which comes first after the frontmatter — is this page-level marker, character for character: `[NEEDS CLARIFICATION: this page was drafted from the product's code and specifications and has not been checked against the product itself.]` §6's rules bind it as they bind a claim's marker: it never becomes prose fact by default, and it is removed only in the commit that moves its unit to `verified`, or by a person who walked the page — until `/docs-verify`, which makes that commit, ships, by that person alone. While it stands, the `--refresh` reconciliation lands the page on `drafted`, never on `published` (`backlog-format.md` §3), so a page whose unit's move a merge lost still counts as unverified.

---

## 4. The walkthrough file

A walkthrough is structured from day one so that a browser backend is a **runner rather than a rewrite**: the same file a person reads as a checklist today is the file a driver executes later.

```yaml
walkthrough:
  id: W-001
  unit: U-001
  role: customer
  environment: docker | staging        # which environment it was written against
preconditions:
  - "catalog seeded"
  - "signed in as customer"
steps:
  - n: 1
    action: navigate                   # navigate|click|type|select|wait
    target: "/orders/new"
    expect: { kind: heading, text: "New order" }
  - n: 2
    action: click
    target: { label: "Add item" }
    expect: { kind: visible, label: "Item details" }
captures:
  - { slot: img-order-form, after_step: 2, shows: "the empty order form with the item panel open" }
```

**The action vocabulary is closed: `navigate`, `click`, `type`, `select`, `wait`, and nothing else.** It is closed because it is the half a driver has to implement, and a vocabulary a writer may extend is one no driver can claim to support. A step that needs something outside it is a step the walkthrough cannot express, and that is a finding rather than a licence to invent a sixth verb.

`target` is a string where the action names a location (`navigate`), and an object identifying an element otherwise — `{ label: "Add item" }` in the example. **`expect.kind` is deliberately not closed**, because what a step asserts depends on what the page shows; a driver that meets a kind it does not implement records the step `blocked` with the kind named (§5), which is the honest outcome and not a failure of the walkthrough.

`captures[].slot` names a placeholder the writer leaves in the page, which the verification pass fills with the image it produced. **Where that image then lives is a profile field, not a law** — `images.policy` in `references/docs-profiles/docs-profile-schema.md` — and nothing about the slot changes with it.

**A walkthrough is a file, and it has a home.** It lives at **`<top>/.dev-workflows/walkthroughs/<id>.yml`** — `W-001` at `<top>/.dev-workflows/walkthroughs/W-001.yml` — where `<top>` is the same git work-tree top level of the resolved docs repository that `backlog-format.md` §6 pins for the backlog, tracked and reviewed for the same reasons. A unit records the **id** and never the path (`walkthrough: W-001`), so the path is derived from the id in one place and moving the directory is a one-line change rather than an edit to every unit. Without this, §5 tells a person to work "from the file" and leaves them nothing to open.

**Nothing in this increment composes a walkthrough.** `/docs-audit` mints units with `walkthrough: null` (`backlog-format.md` §1), and composing one is `/docs-capture`'s and `/docs-verify`'s, both Spec 2's — `/docs-write` reads a walkthrough and never writes one. The format is frozen here, ahead of its writers, because it is the expensive thing to change later: a walkthrough written against one shape and a driver built against another is the rewrite D3 exists to avoid.

---

## 5. Execution — a checklist now, a driver later

**v1 execution is a rendered numbered checklist walked by a person, and it is the execution model this family ships** — v2 changes who does the walking and nothing else. The steps are printed in order with their `expect` beside each one, and the person answers each in turn. **No command in this increment renders that checklist**: `/docs-verify`, which renders it and writes the answers back, is Spec 2's, and until it lands the checklist is one a person builds from the file and the answers go back into the file by hand. Per step the person answers one of three:

| Answer | Means | Also records |
|---|---|---|
| `confirmed` | the step did what `expect` says | nothing further |
| `differs` | the step worked, and showed something else | **the actual observed text**, required |
| `blocked` | the step's outcome could not be established | why — a missing precondition, an environment that would not come up, a step taken whose `expect.kind` nothing could evaluate |

**`differs` recording the observed text is what turns a walkthrough into a correction rather than a red X.** "Step 4 failed" sends somebody back to the environment to find out what it says instead; "step 4 shows *Create order*, not *New order*" is the page edit, already written down by the person who was looking at the screen. A `differs` answer with no observed text is an incomplete answer and is re-asked, not recorded.

Results are written back as `result:` on each step, in the same file:

```yaml
  - n: 2
    action: click
    target: { label: "Add item" }
    expect: { kind: visible, label: "Item details" }
    result: { outcome: differs, observed: "Line item details" }
```

**`blocked` is defined by the outcome and not by the attempt, which is what makes it the right home for an unevaluatable `expect`.** A step nobody could take is blocked; so is a step somebody took whose `expect.kind` no reader or driver could evaluate (§4) — in both the walkthrough learned nothing, and calling the second `differs` would assert an observation nobody made. `result.outcome` is one of `confirmed`, `differs`, `blocked`. `result.observed` carries the observed text and is **written on `differs` and on nothing else**. `result.note` carries the reason on `blocked` and is likewise written on nothing else — a note on a `confirmed` step is a comment the next run has no rule for.

**v2 execution is a driver executing the identical file. No format change.** That is the point of every constraint above — the closed action vocabulary, the structured `target` and `expect`, results written back in place. A driver reads the same `steps[]`, writes the same `result:` block, and produces the same three outcomes; what changes is who is looking at the screen, and nothing about the file.

---

## 6. Hard rules

- NEVER let a marked claim become prose fact by default. It is confirmed or it ships marked (§3).
- NEVER remove a `[NEEDS CLARIFICATION]` marker for any reason other than having resolved the claim it marks (§3).
- NEVER resolve a user-audience claim by reading the code that renders it, or an engineering-audience claim by observation (§1).
- NEVER record an `artifact` evidence entry without the commit it was read at (§2).
- NEVER add an action verb outside `navigate|click|type|select|wait` (§4).
- NEVER record a `differs` result without the observed text (§5).
- NEVER track evidence per sentence. The page records its sources; only unverified claims are marked inline (§3).
