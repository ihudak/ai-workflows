# ARD threat model format (shared reference)

Single source of truth for `threat-model.md`, the threat model an ARD may carry: one numbered threat per concrete attack on a component the architecture names, or on an interface between two of them, each with exactly one disposition. Its writer is `/product-workflows:create-ard`, which drafts it at its Phase 4.3 and writes it into the folder at its Phase 6; `scripts/lineage.py` writes its lineage blocks for that command (§2).

**Who reads it.**
- **Two readers by name:** `/product-workflows:create-ard` (a later run on the same folder) and `product-workflows:ard-reviewer` (within the run).
- **One reader as prose, on the BRD route:** `/product-workflows:brd-reconcile`'s stale cross-reference sweep reads it as it reads every markdown file under the parent BRD's folder — as prose. By that sweep's structured-record class, a hit there is `needs-a-human`, never corrected in place. The class is that command's Phase 11's: "a structured record — any file whose content is fields, rows or labelled lines some other rule writes and reads", and "What `updated` is for is the route's own prose, and only that". A threat model's threats are labelled lines that this file writes, and that §6's check and `workflows-core:pre-lint`'s *Threat model* block read.
- **No other command reads it.** `/dev-workflows:design` and `/dev-workflows:conformance` are to read it later, which is why this file is `workflows-core`'s: a reference crosses a plugin boundary only from here.

## 1. What it is and where it lives

- **One per folder.** `threat-model.md` sits beside the folder's ARD files and covers all of them — its `ard.md` and any `ard-<area>.md` — in a PRD folder, an Epic folder or a BRD-route slice.
- **Never named `ard-*.md`.** Three readers take any such file as a per-area ARD: `workflows-core:ard-resolution`, the lineage kind table's `ard` row (`workflows-core:document-lineage` §4), and `product-workflows`' `scripts/architecture-harvest.py`, which would mint team records from it.
- **Never under `$SPECS_PATH/security/`**, which is kept for a team's own documents and the findings register.
- **`kind: threat-model` names no folder kind**, so `workflows-core:addressing` §4 passes the file over as the folder's carrier.
- **Unknown frontmatter keys are kept.** A run that builds on the folder's model keeps every frontmatter key it does not recognise, in place and unmodified, as `product-workflows:ard-format` keeps an ARD's. *Start fresh* (§5) discards the old file whole, its keys included.

## 2. Frontmatter

```yaml
---
kind: threat-model            # what this document is; it names no folder kind (§1)
key: <KEY>                    # this folder's key — must match the folder name
status: draft | reviewed      # the value the run writes in the ARD's own status:
upstreams: …                  # the lineage record — written only by lineage.py (workflows-core:document-lineage §1)
accepted: …                   # written only by lineage.py (workflows-core:document-lineage §6)
---
```

## 3. Sections

In this order, under the title `# <PRD or Epic title> — threat model`:

- **`## Scope`** lists every component id and every contract pair the model considered: a `- **Components:**` line holding the ids, comma-separated, and a `- **Contract rows:**` line holding the pairs (§4), or `none`.
- **`## Not considered`** gives each id or contract pair of the set that the model leaves out, one bullet each with its reason — `- <id or pair> — <why it was left out>` — or reads `_None._` where nothing was left out.
- **`## Threats`** holds one `### [TH#N]: <title>` block per threat (§4).
- **`## Inherited threats`** is written **on an Epic-level model only**. It lists the PRD-level model's live threats, one bullet each: `- [[<PRD-KEY>]] [TH#N] <title> — <its Disposition, as the PRD-level model states it>`. They are bullets, never `### [TH#N]` headings, so the numbering (§5) and the lineage item pattern skip them. Under `## Threats`, an Epic-level model adds only the threats its Epic's `target:` component raises.
- **A BRD-route slice's model inherits none**, and has no `## Inherited threats`: its parent is a BRD container, where `/product-workflows:create-ard` writes nothing, so no model stands above it.

## 4. A threat

```markdown
### [TH#N]: <title>

- **Category:** S | T | R | I | D | E | —
- **Where:** <component id>[, <component id>…][; contract <pair>]
- **Threat:** attacker: <who>; action: <what they do>; asset: <what is at stake>
- **CWE:** [CWE-<n>](https://cwe.mitre.org/data/definitions/<n>.html) | —
- **Disposition:** <exactly one of the three forms below>
- **Superseded by:** [TH#M] — <why>        (a superseded threat only)
- **Withdrawn:** <why>                     (a withdrawn threat only)
```

- **The heading** is `### [TH#N]: <title>`, with the colon, as an ARD's `### [AD#N]:` heading has it.
- **The five fields** — Category, Where, Threat, CWE and Disposition — are list items in that order, and every one is present on every threat. `—` marks an empty Category or CWE. `**Superseded by:**` or `**Withdrawn:**` follows them only on a threat that is no longer live (§5). **A live threat** is one carrying neither.
- **Category** is one STRIDE letter — Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege — or `—`. It is a completeness prompt, never a score.
- **Where** is `<id>[, <id>…][; contract <pair>]`: at least one component id, and the contract row's decision pair where the threat crosses an interface. A contract row is named by its decision pair, never by a row number. Each id is resolved against **the run's resolved component set**, and never against an ARD's own `components:` alone, which only a PRD-level ARD carries:
  - **On a PRD-level run, the BRD route's slice-level run included:** the components `/product-workflows:create-ard`'s Phase 3 confirmed — the list the ARD's `components:` is written from.
  - **On an Epic-level run:** `workflows-core:ard-resolution`'s `components` field, where it is non-empty. Otherwise the `set` that `workflows-core:components`' `multi-component-test` (§3) returns on the PRD folder, where it is non-empty.
  - **Otherwise there is no set**, and no Where can be resolved.

  Contract rows exist only in a PRD-level ARD with two or more `kind: code` components. So an Epic-level threat's Where holds the Epic's `target:` id and, where the threat crosses a boundary, the inherited row's pair: `<target>; contract [[<PRD-KEY>]] ard.md [AD#N]`.
- **A decision pair** names one decision by the ARD file that holds it, because each ARD file numbers its own `[AD#N]` series:
  - its form is `<ARD file> [AD#N]`, `<ARD file>` being the basename of an ARD file in the model's own folder — `ard.md [AD#3]`, or, in an Epic folder split by area, `ard-payments.md [AD#2]`;
  - a decision of the PRD-level ARD an Epic inherits is `[[<PRD-KEY>]] ard.md [AD#4]`, the PRD folder's key in the wikilink form, which `workflows-core:pre-lint`'s auto-link check discards (its *Discard a hit ONLY when …* rule);
  - several pairs are joined by `, `.
- **CWE** is optional. Where a threat names one, it is a link to the CWE's page, `[CWE-<n>](https://cwe.mitre.org/data/definitions/<n>.html)`, `<n>` its number without leading zeros — the form `product-workflows:ard-format`'s *A CWE in Prevents* gives a decision.
- **Disposition** holds exactly one of three forms:
  1. `Mitigated by <pair>[, <pair>…]`, optionally followed by `; the rest deferred to design: <what the design must answer>`. The architecture answers the threat with one or more decisions; the optional remainder is part of this one form.
  2. `Deferred to design: <what the design must answer>`. The detailed design answers it.
  3. `Accepted — <owner>; <reason>; review by <YYYY-MM-DD>`. The residual risk is accepted.
- **The bar.** A decision a `Mitigated by` names is an ordinary `[AD#N]` of the ARD file its pair names. It meets `product-workflows:ard-format`'s bar and carries its fields, as every decision there does, and its Prevents names the threat's CWE, as a link, where the threat names one. This file keeps no copy of that bar. A mitigation that fails the bar is `Deferred to design` instead, and so is a gap whose answer is a product requirement the PRD does not state; `/product-workflows:create-ard` also records such a gap as an open question of the ARD.
- **An acceptance** names its owner, its reason and its review date, the date by which it is looked at again. The PA alone accepts a risk; the Security Engineer's check is the pull request that hands the model off.

## 5. Identity and change

- **`[TH#N]` is numbered per folder from `[TH#1]`**, and the series stays contiguous over live, superseded and withdrawn threats alike. A PRD-level and an Epic-level model each start at `[TH#1]`.
- **A threat is never renumbered or deleted.** A threat changes when its Where or its Threat line comes to mean something else; wording that keeps the meaning is not a change. A changed threat is a new `[TH#M]`, and the old one keeps its heading, id and text and gains `- **Superseded by:** [TH#M] — <why>`, naming a live threat of the same model. A threat made moot, with no replacement, gains `- **Withdrawn:** <why>` instead.
- **A re-disposition is not a change of the threat.** It rewrites the Disposition line of a live threat — a stale mitigation deferred to design, an acceptance renewed with a new review date — and the threat keeps its id.
- **Across folders**, a threat is named by its folder's key in the wikilink form and its id: `[[<KEY>]] [TH#N]`.
- ***Start fresh*.** The model follows the ARD's refine-or-fresh choice at `/product-workflows:create-ard`'s Phase 1:
  - A refine keeps every `[TH#N]`.
  - *Start fresh* keeps them too wherever the specs repository's default branch carries one of the folder's ARD files or its `threat-model.md`, since what stands on the default branch keeps its ids (`product-workflows:ard-format` § Superseding a decision).
  - Only where the default branch carries none of the folder's ARD files and no `threat-model.md` does *Start fresh* discard the model. The run does not read the old file, walks the model fresh and numbers it from `[TH#1]`. At its Phase 6 it writes the new model over the old file, or removes the old file where it writes no model.

## 6. The check

The check is mechanical and asks nothing. It reads the model as the run holds it, and the ARD files as the run holds them at that point: this run's drafts at Phase 4.3, and the files as just written at Phase 6. A `[[<PRD-KEY>]] ard.md` pair is read in the inherited PRD-level ARD the run resolved.

A **live** threat is **stale** where any of these holds:

1. A component id in its Where is not in the run's resolved component set (§4).
2. Its `contract <pair>` names no interface-table row of that ARD file whose `AD` is that id, or that decision is not live.
3. A pair in its `Mitigated by` names no `### [AD#N]` in that ARD file, or names one carrying `**Superseded by:**` or `**Withdrawn:**`.

Nothing else is checked. An acceptance past its review date is not stale: a refine lists it for the PA to renew, re-dispose or keep.

Where a set resolves, `/product-workflows:create-ard` runs the check three times:
- at its Phase 4.3, on the model the folder holds, to choose the question it puts;
- at its Phase 4.3 again, on the draft, before the draft is played back, since a walk can make its own entries stale;
- at its Phase 6, before the model is stamped, since the review's fixes and manual fix notes can still supersede a decision a threat cites.

## 7. What a threat model never holds

- **A generic STRIDE item.** Every threat names the element it attacks (its Where), a concrete attacker action and the asset at stake, or it is not written.
- **A risk score** — DREAD, likelihood × impact or CVSS. Category is a completeness prompt, never a score.
- **An attack tree or a data-flow diagram.**
- **A required CAPEC id.**
- **An `[MT#N]`**, or any other mitigation id. A mitigation the architecture owns is an `[AD#N]`, and one it cannot own is the design's.
- **A Claude Security model, or any register's text.** Neither is consumed, copied or persisted here.

## 8. Its readers

They are the opening's *Who reads it*, in its words:
- **Two readers by name:** `/product-workflows:create-ard` (a later run on the same folder) and `product-workflows:ard-reviewer` (within the run).
- **One reader as prose, on the BRD route:** `/product-workflows:brd-reconcile`'s stale cross-reference sweep, which reads it as prose and, by its structured-record class, takes a hit there as `needs-a-human`, never corrected in place.
- **No other command reads it.** `/dev-workflows:design` and `/dev-workflows:conformance` are to read it later.

The commands and agents that load this reference are what `grep -l 'args: "threat-model-format' plugins/*/commands/*.md plugins/*/agents/*.md` lists — a scope this file is outside. `workflows-core:pre-lint` cites it by path, as the format its *Threat model* block checks. No list of them is kept here.

## Example

A PRD-level model, `specifications/PRD-ACME-90-checkout/threat-model.md`. It sits beside an `ard.md` whose components are `shop:orders`, `shop:payments` and `shop:web`, and whose `## Contracts` holds one interface row, decided by `[AD#3]`, from `shop:orders` to `shop:web`:

```markdown
---
kind: threat-model
key: ACME-90
status: reviewed
upstreams:
  - path: specifications/PRD-ACME-90-checkout/ard.md
    blob: <the git blob id of ard.md as Phase 6 wrote it>
    version: null
---

# Checkout — threat model

## Scope

- **Components:** shop:orders, shop:payments, shop:web
- **Contract rows:** ard.md [AD#3]

## Not considered

_None._

## Threats

### [TH#1]: Order total forged in the browser

- **Category:** T
- **Where:** shop:orders, shop:web; contract ard.md [AD#3]
- **Threat:** attacker: a signed-in customer; action: edits the order total in the request the web client sends to the orders service; asset: the amount charged for the order
- **CWE:** [CWE-602](https://cwe.mitre.org/data/definitions/602.html)
- **Disposition:** Mitigated by ard.md [AD#2]

### [TH#2]: Payment callback replayed

- **Category:** S
- **Where:** shop:payments
- **Threat:** attacker: anyone holding a copy of an earlier payment callback; action: sends it again to mark an unpaid order paid; asset: the order's paid state
- **CWE:** —
- **Disposition:** Deferred to design: how the callback handler rejects a callback it has already processed

### [TH#3]: Another customer's order read by its id

- **Category:** I
- **Where:** shop:orders
- **Threat:** attacker: a signed-in customer; action: requests an order id that is not theirs; asset: other customers' order details
- **CWE:** —
- **Disposition:** Accepted — the checkout team lead; order ids are random UUIDs, and the gateway's rate limit makes guessing one impractical; review by 2027-02-12
```

An Epic-level model under it, in the Epic folder `EPIC-ACME-90-02-web-payments/`, whose `target:` is `shop:web` and whose ARD is split by area into `ard-payments.md` and `ard-cart.md`. This excerpt leaves out its frontmatter, `## Scope`, `## Not considered` and its other inherited bullets:

```markdown
## Threats

### [TH#1]: Payment page framed by another site

- **Category:** T
- **Where:** shop:web
- **Threat:** attacker: a third-party site; action: frames the payment page to trick a customer into confirming a payment; asset: the customer's confirmation of the payment
- **CWE:** —
- **Disposition:** Mitigated by ard-payments.md [AD#2]

## Inherited threats

- [[ACME-90]] [TH#2] Payment callback replayed — Deferred to design: how the callback handler rejects a callback it has already processed
```
