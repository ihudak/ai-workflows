# Terminology

Rules for naming things: your organization's products and features, third-party names,
trademarks, and the terms your documentation invents.

**Baseline.** The shipped baseline holds **no organization-specific terms** — it cannot,
and inventing them would be wrong. What it ships is the set of *rules* that govern
naming, plus the [Terminology schema](#terminology-schema) for declaring your own terms
so the checker can enforce them. A repo-local or env-var overlay layers on top of this
file and wins on conflict — see `prose-style-checker` step 1 ("Resolve the active rule
set") and the plugin's `docs/reference/overlay.md`.

**Grounded in:** Microsoft Writing Style Guide ("Names of Microsoft products",
"Trademarks", "Terminology"); Google developer documentation style guide ("Product
names", "Word list", "Timeless documentation"); Apple Style Guide (product-name
conventions, capitalization of interface names); The Chicago Manual of Style
(capitalization and possessives of proper names).

---

## Naming rules that hold everywhere

### One name per concept

Pick one term for a concept and use it in every sentence on every page. Synonyms
written for variety are the single most expensive terminology defect: the reader
cannot tell whether two words mean two things.

- ❌ "environment" on one page, "tenant" on the next, "instance" in the API reference
- ✅ one of those three, everywhere

Flagging this requires knowing which term is canonical — which is exactly what the
terminology schema below declares.

### Write the product name as the organization writes it

- Reproduce capitalization, spacing, and internal capitals exactly: `PostgreSQL`,
  `GitHub`, `npm`, `iOS`, `macOS`, `Kubernetes`.
- ❌ Github, Post-greSQL, NPM, IOS, MacOS, kubernetes
- Never abbreviate a product name to initials unless the organization publishes that
  abbreviation as a name in its own right.
- Never pluralize or make possessive a product name that is a mark: use it as an
  adjective instead.
  - ❌ Acme's dashboard — ✅ the Acme dashboard
  - ❌ two Acmes — ✅ two Acme instances

### Do not attach the product name to every noun

- ✅ Open **Dashboards**. — ❌ Open the **Dashboards** app in Acme Platform.
- Use the full product name at first mention on a page; the short form afterwards.

### Feature names are lowercase unless they are marks

A capability described in prose is not a proper noun. Capitalize a feature only when
the organization treats it as a name, and declare that in the terminology schema.

- ✅ Set up single sign-on. — ❌ Set up Single Sign-On.
- ✅ Turn on **Audit logging** (the UI label). — see `ui-interactions.md`.

### UI labels are quotations

Reproduce a UI label exactly as it appears on screen, in bold, including its
capitalization — even where that breaks the sentence-case rule in `formatting.md`.

### Version and release names

- Write a version exactly as the product prints it: `v2`, `2.4`, `2026.1`.
- Avoid time-relative naming: ❌ "the new API", "the latest release", "currently".
  Name the version. Documentation outlives the word "new".
- Define the maturity ladder your organization uses (for example preview → general
  availability) in the terminology schema, and use those labels consistently.

### Deprecated terms

Rename in one direction and keep the mapping. Every deprecated term stays in the
terminology file with its replacement so the checker can catch stragglers, long after
humans have forgotten the old name.

---

## Trademarks

The baseline ships no marks. The rules for handling marks are general.

- Use the symbol (® or ™) on the **first mention per page or document** only, if your
  organization uses symbols at all.
- Never put a symbol in a heading, a title, a URL, or a code sample.
- Never make a marked term possessive or plural with the symbol attached.
  - ❌ Acme®'s platform — ✅ the Acme® platform
  - ❌ two Acme Agents® — ✅ two Acme Agent® instances
- A mark is an adjective. Follow it with a noun: "Acme® software", not "an Acme®".
- Do not translate or localize a mark.

Declare which of your terms carry which symbol in the terminology schema. If your
organization does not use symbols in documentation, declare nothing and the
`Prose.Terminology.TrademarkSymbol` rule never fires.

---

## Third-party names

- Use the owner's official spelling and capitalization; check the owner's own site,
  not a search result.
- Reproduce third-party trademark symbols on first mention only if the owner's
  guidelines require it in your context.
- Do not imply a partnership or endorsement by juxtaposition.
- Do not shorten a third-party name to an in-house nickname in published content.

---

## Terms your documentation invents

If a term appears in your docs but nowhere in the product, it is an invented term. Two
rules:

1. Define it at first use on the page.
2. Add it to the terminology file, or delete it and use the product's word.

---

## Terminology schema

Create a `terminology.md` in your overlay directory (see the plugin's
`docs/reference/overlay.md`). The checker reads these tables structurally, so the column headers matter.
Every section is optional; ship only what you have.

### Canonical terms

The core table. The left column is the term to use; the second lists the forms to flag.

```markdown
## Canonical terms

| ✅ Use | ❌ Do not use | Note |
|---|---|---|
| workspace | tenant, org, account space | One workspace per customer environment |
| extension | plugin, add-on | "Plugins API" keeps its published name |
| issue | ticket, card | |
```

- A term in the ❌ column becomes a `Prose.Terminology.WrongTerm` violation, MAJOR by
  default.
- The `Note` column, when present, is appended to the violation `message`.

### Product and feature names

```markdown
## Product names

| Name | First mention | Short form | Capitalization |
|---|---|---|---|
| Acme Observability Platform | Acme Observability Platform | Acme | exact |
| Acme Agent | Acme Agent | the agent | exact |
```

- `Capitalization: exact` makes any other casing a
  `Prose.Terminology.WrongProductName` violation.
- A `Short form` is permitted after the first mention on a page.

### Trademarks

```markdown
## Trademarks

| Term | Symbol | Scope |
|---|---|---|
| Acme | ® | first mention per page |
| Acme Agent | ® | first mention per page |
| Quickstart | ™ | first mention per page |
```

Omit this section entirely if your documentation does not carry symbols.

### Deprecated terms

```markdown
## Deprecated terms

| Retired term | Replacement | Retired in |
|---|---|---|
| control center | admin console | 2025.3 |
| data node | storage node | 2024.9 |
```

Produces `Prose.Terminology.DeprecatedTerm`, MAJOR by default.

### Severity override

Add a `Severity` column to any table above to override the calibration table in
`prose-style-checker`. Valid values: `MAJOR`, `MINOR`, `NIT`.

### Allowed exceptions

```markdown
## Allowed

| Term | Why |
|---|---|
| tenant | Kept in the multi-tenancy architecture page only. |
```

### Replacing this baseline file

An overlay file layers on top of the baseline by default. To discard this file entirely
and use only yours, put this marker on the first line of your overlay `terminology.md`:

```markdown
<!-- prose-style: replace -->
```

Because this baseline file ships no terms of its own, layering is almost always what
you want — the `replace` marker only matters if you also want to drop the general
naming rules above.
