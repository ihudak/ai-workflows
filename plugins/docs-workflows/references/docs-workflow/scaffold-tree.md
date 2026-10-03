# The scaffold — tree, stubs, nav, and configs

Single source of truth for **what `/docs-init` creates**. It is an executable template, not a description of one: a command reads it to know which directories and files to write, what goes in each, and what the two build configs and the linter config contain.

Consumed by `/docs-init` (Phase 3 writes §1–§6, Phase 4 writes §7), by `/docs-brand`, which reads §5 and §6 to know which config carries the theme and which inherits it, §3.13 for the file a rebrand reconciles and §7 for its commit-time ignore test, by `/docs-serve`, which takes the two builds' site names from §5 and §6 and its state file's ignore line from §7, and by `docs-scaffold-reviewer`, whose checklist asserts relationships between the files this file specifies; two references, `visibility.md` and `docs-audit/backlog-format.md`, cite single sections of it. `grep -rl scaffold-tree plugins/docs-workflows/commands plugins/docs-workflows/agents plugins/docs-workflows/references` lists every reader, and this file besides. §4 is written for one more reader that does not ship yet: `/docs-write`, a later command, is to regenerate the same `nav:` on every page it writes, and will take the rule from §4 rather than restate it.

Its entry points, so a command can say which part it is executing: **the tree** (§1), **the stubs** (§3), **nav generation** (§4), **the mkdocs configs** (§5 and §6), and **the vale config** (§7, which also carries `requirements-docs.txt`, `.gitignore` with its create-or-merge rule, and the Vale exit criterion both the scaffold's own verification and its CI apply).

The navigation is **product-shaped** (design D15). Diátaxis lives in each page's `type:` frontmatter, whose vocabulary is that of the page type `/docs-audit`'s coverage grid takes as its second axis from the backlog's units, so the tree looks like a documentation portal a reader recognises while the quadrant discipline stays fully intact.

---

## 1. The tree

```
mkdocs.yml                  # public build; strict: true; exclude_docs drops internal/ and _snippets/
mkdocs.internal.yml         # INHERIT: mkdocs.yml + internal nav; site_dir: site-internal
.gitignore                  # build outputs, synced Vale packages, /docs-serve's state file -- see §7
.vale.ini
requirements-docs.txt       # the CI build's Python dependencies -- see §7
styles/                     # .vale.ini's StylesPath; `vale sync` populates it
  config/vocabularies/Project/accept.txt   # product terms Vale must not flag -- see §7
docs/
  index.md                             # portal home
  discover/                            # "Discover <product>"
    index.md                           #   What is <product>          type: explanation
    how-it-works.md                    #   the mental model
    use-cases.md
    roles.md                           #   who does what             ← the role surface
    glossary.md                        #   terms, roles, integrations, primary workflows
    pricing.md                         #   optional: --with-pricing
    accessibility.md                   #   optional: --with-compliance
    security.md                        #   optional: --with-compliance
  get-started/
    index.md                           #   quickstart                 type: tutorial
    requirements.md
    install.md
  guides/                              # task-oriented                type: how-to
  reference/                           #                              type: reference
    api/
    configuration.md
    cli.md
    data-model.md
    limits.md                          #   limits and quotas
    errors.md                          #   error codes
  integrations/                        # optional
  administration/                      # users and roles, security, SSO, billing
  troubleshooting/
    index.md
    faq.md
    known-issues.md
  whats-new/
    index.md                           #   release-notes hub
    v<MAJOR>/
      index.md                         #   the major release
      maintenance.md                   #   per-build fixes in that major
    deprecations.md                    #   end-of-life and end-of-support
  support.md
  internal/                            # engineering docs; excluded from the public build
    architecture/
    decisions/
    runbooks/
  _snippets/                           # pymdownx.snippets base_path; excluded from BOTH builds
  assets/                              # logo, favicon, images
  stylesheets/extra.css
.dev-workflows/
  docs-profile.yml
.github/workflows/docs.yml             # build both, lint, and the two visibility gates
```

Four flags or conditions vary this tree. `integrations/` is written when the run has integrations to document — the source-repo set resolved in Phase 2 is what answers that, not a flag. `pricing.md` is written under `--with-pricing`. `accessibility.md` and `security.md` are written under `--with-compliance`. `--public-only` omits `mkdocs.internal.yml` and the whole `docs/internal/` tree, and drops the internal build step and gate 2 from `docs.yml` (`/docs-init` Phase 3's *The flags that vary the tree*). Everything else is unconditional: a portal missing one of the §2 sections is missing it, not customised.

**"What's new" is fed, not written from scratch.** Its entries come from the `/release-notes` drafts already sitting in `$SPECS_PATH`, which that command writes for its user to paste wherever release notes are published — and pasting them here is how the pages are filled today. **Half of that is automated now, and it is the half that finds the work rather than the half that does it.** `/docs-audit` enumerates a `release` surface per release version from those same drafts (`references/docs-audit/coverage-model.md` §2), so a version whose page nobody has pasted yet shows up as a `missing` unit in the backlog instead of being noticed by somebody remembering. Rendering the page is still by hand; `/docs-write`, in a later spec, is to take that over. `references/release-note-types.md` supplies the section split inside each page — breaking changes, feature updates, fixes — because that reference already owns the destination map and the per-destination prose shape. Nothing is re-derived here.

---

## 2. Why each section

The sections a reader would predict need no defence. These nine do, and each is standard rather than decoration — every one of them is a page a real portal has and a new portal forgets.

| Section | Why every portal has it |
|---|---|
| **Glossary** | The highest-leverage page in a new portal: it is what lets every other page stop re-explaining terms. Every product noun it defines belongs in the Vale vocabulary too (§7), so those nouns stop being reported as misspellings. |
| **Roles** | A reader's first question is which of these instructions are for them. It is also this family's coverage dimension, so the page and the coverage grid `/docs-audit` builds enumerate the same roles. |
| **Troubleshooting / FAQ / Known issues** | The highest-traffic pages on most portals, and the main support-deflection surface. Absent, the traffic arrives as tickets instead. |
| **Limits and quotas** | Routinely the single most-visited reference page, and the one most often missing. An evaluator looks for it before they look at features. |
| **Error codes** | The only page a reader arrives at by pasting a string out of a log. Nothing else in the portal serves that entry path. |
| **Administration** | Role-gated tasks that do not belong in user guides, and the first thing an evaluator opens to judge whether the product is operable. |
| **Deprecations / end-of-life** | Pairs with What's new. `references/release-note-types.md` already requires an end-of-life date on every deprecation note, so the destination has to exist. |
| **Support** | How to reach a human. Every other page implicitly promises this escape hatch; the portal has to keep the promise. |
| **Accessibility and security statements** | Increasingly a procurement requirement. Scaffolded as stubs under `discover/` when `--with-compliance` is passed. |

---

## 3. Stubs

**Each directory gets one stub that states what belongs there and what does not**, carrying the section's default `type:` in its frontmatter. The stub is that directory's own `index.md`. §1's tree names an `index.md` only where the spec had something to say about its content; every other directory in the tree gets one from this section, and the three in §3.13 get none at all.

This is not filler. The commonest failure of a documentation tree is contributors putting explanation into how-to guides — a guide that starts with four paragraphs of background, a reference page that becomes a tutorial, a concept page that grows numbered steps. The stub is where that is prevented, at the moment someone opens the directory to add a page. A convention stated only in a style guide nobody opens is not a convention; a convention stated in the file you are about to edit is.

Every **directory** stub carries six frontmatter fields — `title`, `description`, `type`, `audience`, `visibility`, `order` — being the six that record where the page sits, who it is for, and which build it belongs to (the build itself is decided by path — `visibility.md` §1 — and each stub's `visibility` matches its path). The full page contract is larger (`references/docs-profiles/frontmatter-guidelines.md` and the `docs-frontmatter` skill own it), and the writer fills the rest when the page stops being a stub. **A leaf-page stub carries a lighter shape**, defined with its reason in §3.12.

**Every file under `internal/` carries the visibility marker** as its first line after the frontmatter — see `visibility.md` §5. The stubs below show it. A stub written without it is the exact file the gate cannot see.

### 3.1 Portal home

`docs/index.md`

```markdown
---
title: <product> documentation
description: Everything published about <product>, by what you are trying to do.
type: explanation
audience: user
visibility: public
order: 1
---

Start here. This page routes to the rest of the portal: what <product> is, how to get it running, how to do a specific task, and where the exact values live.

**What belongs here:** signposting—one short paragraph per section, naming who each is for. Nothing else.

**What does not:** product explanation (that is `discover/`), installation steps (`get-started/`), or anything a reader would need to scroll to reach. A home page that has to be read is a home page nobody reads.
```

### 3.2 `discover/`

`docs/discover/index.md`

```markdown
---
title: What is <product>
description: What <product> does, who it is for, and the model behind it.
type: explanation
audience: user
visibility: public
order: 1
---

The concept layer. Pages here answer *what is this and why is it shaped like this* for someone who has not decided to use the product yet.

**What belongs here:** the product's purpose, its mental model, the vocabulary the rest of the portal uses, the roles it recognises, and the shapes of problem it solves.

**What does not:** instructions. The moment a page here acquires a numbered list of steps, it belongs in `get-started/` or `guides/`. Explanation earns its place by being readable in any order; steps do not.
```

### 3.3 `get-started/`

`docs/get-started/index.md`

```markdown
---
title: Get started
description: Install <product> and reach a first working result.
type: tutorial
audience: user
visibility: public
order: 1
---

The one guaranteed path from nothing to a working result. A reader following this page in order arrives somewhere real, without deciding anything.

**What belongs here:** prerequisites, installation, and a single end-to-end first run with a stated outcome.

**What does not:** alternatives, options, and platform variants. A tutorial that branches has stopped being a tutorial; branches belong in `guides/`, values belong in `reference/`. If a step needs a caveat, the caveat links out rather than opening a fork in the path.
```

### 3.4 `guides/`

`docs/guides/index.md`

```markdown
---
title: Guides
description: Task-oriented instructions for the things people do with <product>.
type: how-to
audience: user
visibility: public
order: 1
---

One page per task, each named for the task in the reader's words—*Import a customer list*, not *The import subsystem*.

**What belongs here:** a stated goal, the prerequisites for it, the steps, and how to tell it worked.

**What does not:** background. A guide's reader has already decided to do the thing; explaining why it exists costs them the top of the page. Link to `discover/` for the why, and to `reference/` for the exact values, and keep the steps unbroken.
```

### 3.5 `reference/`

`docs/reference/index.md`

```markdown
---
title: Reference
description: Exact values—configuration, CLI, data model, limits, errors.
type: reference
audience: user
visibility: public
order: 1
---

The lookup layer. A reader arrives here knowing what they want and needing its exact name, type, default, or value.

**What belongs here:** complete, structured, scannable statements of fact—tables, parameter lists, enumerations, error codes. Consistency of shape matters more than prose quality.

**What does not:** narrative and advice. A reference page that explains when to use an option has become an explanation with a table in it, and the table is now harder to scan. Put the recommendation in a guide and link it.
```

### 3.6 `reference/api/`

`docs/reference/api/index.md`

```markdown
---
title: API reference
description: Endpoints, request and response shapes, authentication, and errors.
type: reference
audience: user
visibility: public
order: 10
---

The HTTP (or equivalent) surface, one page per resource or generated from a schema.

**What belongs here:** endpoints with their methods, parameters, request and response bodies, status codes, and auth requirements—every one of them derived from the shipped source or spec, never from memory.

**What does not:** integration tutorials and client walkthroughs. Those are `guides/`. This directory is also the one most likely to be generated; a hand-written page that duplicates a generated one is a page that will disagree with the API within a release.
```

### 3.7 `integrations/`

`docs/integrations/index.md`

```markdown
---
title: Integrations
description: How <product> connects to the other systems it works with.
type: how-to
audience: user
visibility: public
order: 1
---

One page per integrated system, each covering what the connection does, what it needs, and how to set it up.

**What belongs here:** the third-party prerequisites, the credentials and permissions required, the setup steps, and what breaks when the connection is wrong.

**What does not:** documentation of the third-party product itself. Link to their docs and keep this page about the seam. A page that re-explains another vendor's console is a page that goes stale on their release schedule, not yours.
```

### 3.8 `administration/`

`docs/administration/index.md`

```markdown
---
title: Administration
description: Managing users, roles, security, and billing for <product>.
type: how-to
audience: user
visibility: public
order: 1
---

Tasks that require elevated permissions: user and role management, authentication and SSO, security settings, quotas, and billing.

**What belongs here:** anything a reader without an admin role cannot do, kept separate precisely so ordinary guides do not send readers into a wall.

**What does not:** engineering operations. A runbook for the team that operates the service is `internal/runbooks/`; this section is for the customer's own administrator. The test is whose console the reader is in.
```

### 3.9 `troubleshooting/`

`docs/troubleshooting/index.md`

```markdown
---
title: Troubleshooting
description: Symptoms, causes, and fixes—plus the FAQ and known issues.
type: how-to
audience: user
visibility: public
order: 1
---

Organised by **symptom**, in the words a reader would use before they know the cause: what they saw, what it means, what to do.

**What belongs here:** symptom-first entries, the FAQ, and the current known-issues list with its status and workaround.

**What does not:** error-code tables—those are `reference/errors.md`, because a reader pasting a code wants a lookup, not a narrative. Nor does anything organised by subsystem: a reader who knew which subsystem failed would not be here.
```

### 3.10 `whats-new/`

`docs/whats-new/index.md`

```markdown
---
title: What's new
description: Releases, what changed in each, and what is being retired.
type: reference
audience: user
visibility: public
order: 1
---

The release hub: one entry per major version, newest first, plus the deprecations page.

**What belongs here:** links to the per-major pages and the deprecation schedule. Nothing that has to be edited when a release ships—the per-major pages carry that.

**What does not:** release prose written from scratch. Each entry comes from the release-notes draft the pipeline already produced for that change; writing it again by hand creates a second source of truth that disagrees with the first by the following release.
```

`docs/whats-new/v<MAJOR>/index.md`

```markdown
---
title: v<MAJOR>
description: What changed in <product> v<MAJOR>.
type: reference
audience: user
visibility: public
order: 1
---

One major version. Sections follow `references/release-note-types.md`: breaking changes, feature updates, fixes.

**What belongs here:** the changes shipped in this major, in that section order, each one taken from its release-notes draft.

**What does not:** migration tutorials. A breaking change names its remediation in a sentence and links a guide; the guide lives in `guides/`, where it can be found by someone who is not reading release notes.
```

### 3.11 `internal/`

`docs/internal/index.md`

```markdown
---
title: Internal documentation
description: Engineering documentation for the team that builds and runs <product>.
type: explanation
audience: engineering
visibility: internal
order: 1
---
<!-- docs-visibility: internal -->

Everything in this tree is excluded from the public build. It is for the people who build and operate the product.

**What belongs here:** architecture, decision records, and runbooks—plus anything that names internal hostnames, internal tooling, or unreleased work.

**What does not:** anything a customer should be able to read. A page that is merely technical is not internal; API reference is engineering-shaped and public. The test is whether publishing it would be wrong, not whether it is advanced. Every file here carries the visibility marker on its first line after the frontmatter.
```

`docs/internal/architecture/index.md`

```markdown
---
title: Architecture
description: How <product> is built—components, boundaries, and data flow.
type: explanation
audience: engineering
visibility: internal
order: 1
---
<!-- docs-visibility: internal -->

The system as it is today: components, the boundaries between them, what crosses each boundary, and where state lives.

**What belongs here:** structure and rationale that a new engineer needs before reading code, with a diagram wherever a diagram is what is actually being described.

**What does not:** decisions and their alternatives—those are `internal/decisions/`, where they can be dated and superseded. An architecture page that carries its own history stops describing the present.
```

`docs/internal/decisions/index.md`

```markdown
---
title: Decision records
description: Decisions taken about <product>, with their context and consequences.
type: explanation
audience: engineering
visibility: internal
order: 1
---
<!-- docs-visibility: internal -->

One page per decision, dated, stating the context, the decision, the alternatives considered, and the consequences.

**What belongs here:** decisions that constrain later work, including the ones that were reversed—a superseded record is marked superseded and kept, never deleted.

**What does not:** the current state of the system. That is `internal/architecture/`. A decision record is a record of a moment; editing it to match today destroys the only thing it was for.
```

`docs/internal/runbooks/index.md`

```markdown
---
title: Runbooks
description: What to do when something breaks or has to be operated.
type: how-to
audience: engineering
visibility: internal
order: 1
---
<!-- docs-visibility: internal -->

Operational procedures, written to be followed at three in the morning by someone who did not write them.

**What belongs here:** the trigger, the checks, the steps, the rollback, and who to escalate to—each step executable without judgement calls the reader cannot make under pressure.

**What does not:** explanation of why the system works this way. Link it. A runbook whose first screen is background is a runbook nobody reaches the steps of.
```

### 3.12 The named leaf pages

The tree names individual pages inside four sections. Each is created as a stub too, but in a **lighter shape than a directory stub**: `title:`, `description:`, `type:`, `order:`, and a one-line "what belongs here". The `type:` and `order:` are below; `title:` and `description:` come from the page's own subject. `audience:` and `visibility:` are not in that list because every leaf named here sits in a public, user-facing section and takes its section stub's values — a leaf that differs from its section states both explicitly. The directory stub's `type:` is the section default, and a leaf listed here that differs from its section is a deliberate exception, not an oversight.

> **The "what does not belong" half is deliberately not required of a leaf, and that is a narrowing of §3's rule.** §3 requires it of every stub; this section exempts the 19 leaves. The reason is what the half is *for*: it marks a **boundary**, so a contributor adding to `guides/` is told, in the file they opened, that explanation does not go there. A directory is a boundary. `limits.md` and `errors.md` are content pages inside one, and their boundary is already stated by the stub one level up. Writing 19 more of them would restate `reference/`'s rule five times and dilute it. **What was cut is the requirement on leaves only**; a directory stub still carries the full shape, and §8's hard rule now says so explicitly rather than reading as though it bound both.

| Page | `type:` | `order:` | What belongs on it |
|---|---|---|---|
| `discover/how-it-works.md` | explanation | 20 | The mental model: the pieces, how they relate, what the product does on your behalf. |
| `discover/use-cases.md` | explanation | 30 | The shapes of problem the product is for, each with who has it. |
| `discover/roles.md` | explanation | 40 | Every role the product recognises and what each can do. |
| `discover/glossary.md` | reference | 50 | Every term, role, integration and workflow name the portal uses, defined once. |
| `discover/pricing.md` | reference | 60 | Plans, what each includes, and what is metered. `--with-pricing` only. |
| `discover/accessibility.md` | explanation | 70 | The accessibility conformance statement. `--with-compliance` only. |
| `discover/security.md` | explanation | 80 | The security posture statement. `--with-compliance` only. |
| `get-started/requirements.md` | reference | 20 | Supported platforms, versions, and the resources a working install needs. |
| `get-started/install.md` | how-to | 30 | Installation, per supported platform, ending in a verification step. |
| `reference/configuration.md` | reference | 20 | Every setting: name, type, default, effect, and where it is set. |
| `reference/cli.md` | reference | 30 | Every command, its flags, its arguments, and its exit codes. |
| `reference/data-model.md` | reference | 40 | The entities, their fields, and the relationships between them. |
| `reference/limits.md` | reference | 50 | Limits and quotas, with the value, the scope, and whether it can be raised. |
| `reference/errors.md` | reference | 60 | Every error code, what causes it, and what to do about it. |
| `troubleshooting/faq.md` | how-to | 20 | Questions in the reader's words, each with a short answer that links out. |
| `troubleshooting/known-issues.md` | reference | 30 | Current defects with status and workaround; entries are removed when fixed. |
| `whats-new/v<MAJOR>/maintenance.md` | reference | 20 | Per-build fixes within that major, newest first. |
| `whats-new/deprecations.md` | reference | 90 | Every deprecation with its end-of-life date, and its end-of-support date when set. |
| `support.md` | how-to | 90 | How to reach a human, what to include, and what response to expect. |

### 3.13 The three directories that get no stub

None of the three holds pages, and the reason differs by directory. `_snippets/` holds **fragments** — includes that are inlined into a page that has its own frontmatter — and it is excluded from both builds (§5, §6) precisely so that no fragment is mistaken for a page; a stub there would be a page-shaped file in a directory whose whole contract is that it holds none. `assets/` and `stylesheets/` hold no Markdown at all, so there is nothing for a stub to be.

So their convention is stated here rather than in a file that ships:

- **`_snippets/`** — reusable Markdown fragments included with `pymdownx.snippets`, and excluded from both builds (§5) while staying includable, because the extension reads them off the filesystem rather than out of the build. A fragment intended for internal pages carries the visibility marker (`visibility.md` §5); this is the file the snippet leak travels in, and nothing else marks it. No fragment carries frontmatter — it is inlined into a page that has its own.
- **`assets/`** — the logo, the favicon, and images, under `images.root` when the profile's `images.policy` is `in-repo`. One path per slot: a replacement overwrites, and never lands beside the old file under a new name. An image only internal pages may see does **not** go here — it goes under `internal/`, because `exclude_docs` drops files rather than only Markdown, and everything in `assets/` is copied into both builds whether a public page references it or not (`visibility.md` §4).
- **`stylesheets/`** — `extra.css` and nothing else unless the brand needs it. `/docs-brand` writes here; hand edits are what a rebrand then has to reconcile.

---

## 4. `nav:` generation

**`nav:` is generated, never hand-maintained.**

MkDocs takes navigation order from `mkdocs.yml`, not from frontmatter, so a page's `order:` field would otherwise be decorative — present, plausible, and read by nothing. Generating the block is what makes the field real.

The rule: **sort each section's pages on frontmatter `order`, then on `title`.** Ties break on title so the result is stable rather than filesystem-ordered, and a page with no `order:` sorts after every page that has one.

Regenerated on every write that goes through the family: today that is `/docs-init` when it scaffolds, and `/docs-write`, a later command, is to regenerate it whenever it adds or renames a page. One source of truth, no extra plugin, and no state that can drift: the block is derived from the tree each time rather than edited.

Both configs' `nav:` blocks are generated. The internal one is the public nav plus the `internal/` sections, in the same order by the same rule.

A hand-edit to a generated `nav:` survives until the next write and then vanishes, which is worse than being rejected. The block therefore carries the comment shown in §5 and §6, so the next person to open the file is told before they edit rather than after.

---

## 5. `mkdocs.yml`

The public build.

```yaml
site_name: <product>
strict: true
theme:
  name: material
  features: [navigation.sections, navigation.top, search.suggest, content.code.copy]
markdown_extensions:
  - admonition
  - attr_list
  - md_in_html
  - toc: { permalink: true }
  - pymdownx.snippets: { base_path: [docs/_snippets] }
  - pymdownx.superfences
  - pymdownx.tabbed: { alternate_style: true }
exclude_docs: |
  internal/
  _snippets/
validation:
  nav:
    omitted_files: warn
    absolute_links: warn
extra_css:
  - stylesheets/extra.css
nav:
  # generated — see §4; do not hand-edit
```

`strict: true` plus the `validation.nav.*` settings are gate 1 (`visibility.md` §4): a public page linking into `internal/` becomes a build failure rather than a broken link a reader finds. Dropping either one retires that gate while the CI step still appears to run.

**No `logo:` or `favicon:` key, deliberately.** The scaffold writes no image, so a key naming `assets/logo.svg` would reference a file nothing wrote — a broken image on every page of both builds, which `--strict` does not catch because Material does not check that a theme asset exists. `/docs-brand` adds both keys in the same run that copies the files into `docs/assets/`, and only when it applies a logo; under `--no-brand`, or where `/docs-init`'s branding phase applied nothing, Material's own default mark stands and the config stays valid without them.

**`_snippets/` is excluded while `pymdownx.snippets` keeps `base_path: [docs/_snippets]`, and that pairing is deliberate rather than contradictory.** `exclude_docs` removes a file from the **build**; the snippets extension reads its fragments from the **filesystem**. So an excluded fragment is still includable — which is MkDocs' own guidance for include files — and this is the only configuration in which the directory works as intended. Without the exclusion every fragment under `docs/_snippets/` is a `.md` file inside `docs_dir` and MkDocs therefore **renders each one as a standalone page in both builds**: every fragment becomes an orphan that `validation.nav.omitted_files` reports, and an *internal* fragment becomes a **public page** — a more direct leak than the transclusion case gate 2 exists for. State the pairing wherever it is set, because a reader who does not know it reads the exclusion as a mistake and removes it.

---

## 6. `mkdocs.internal.yml`

The internal build.

```yaml
INHERIT: mkdocs.yml
site_name: <product> (internal)
site_dir: site-internal
exclude_docs: |
  _snippets/
nav:
  # generated — the public nav plus the internal/ sections; see §4
```

### The invariant, stated as a content rule

**The two builds share one content source and differ only in what they publish from it.** Concretely, and this is the form the reviewer's second checklist item is checked against:

| Must be identical | May differ |
|---|---|
| `docs_dir` (inherited — the internal config never sets it) | `exclude_docs` — `internal/` + `_snippets/` public, `_snippets/` internal |
| `markdown_extensions`, including `pymdownx.snippets`' `base_path` | `site_name` — the internal site says so in its title |
| the `theme` block, `extra_css`, and `validation` | `site_dir` — `site/` and `site-internal/` |
| the §4 nav-generation **rule** | the generated `nav:` that rule produces |

`_snippets/` is excluded from **both** for the reason §5 gives: a fragment is an include, not a page, and leaving it in either build renders every fragment as a standalone page. So the internal exclusion is not empty, and an internal config carrying `exclude_docs: ""` is the defect, not the baseline.

**`site_dir: site-internal` is not optional.** `site_dir` defaults to `site` and `INHERIT` merges a parent that does not set it either, so an internal config omitting it writes **over the public build's output**. The two are then indistinguishable on disk, and gate 2's marker grep over `site/` inspects the internal output — where every `internal/` page carries the marker by design — and fails every correct scaffold in the one way that reads as a real leak (`visibility.md` §4). `references/docs-profiles/docs-profile-schema.md`'s `builds[]` records `out: site-internal` for this build; the config and the profile have to agree.

**Everything in the left column is the actual rule.** A second `nav:` **source**, a different `markdown_extensions` list, or a divergent `theme` block in the internal config is a **defect, not a customisation** — two configs that differ in their content source are two sites, and the shared snippets, shared search index and working cross-links that the one-tree model buys are gone. The generated `nav:` differs, of course; that is §4 running over a larger file set, not a second source of truth.

> **This rule was narrowed, deliberately.** It read *"the two configs differ only in which paths they exclude"*, and before that *"`exclude_docs: \"\"` is the whole of the difference"*. Both were falsified by the file's own config: §6 has always set `site_name`, and `site_dir` is now a third divergence. A reviewer implementing the old wording would have flagged a correct scaffold, and — worse — a scaffold author obeying it literally would have deleted the `site_dir` line that makes the two builds separable at all. What was cut is **key-level identity**; what survives, and is the whole point, is **one content source**. Nothing in the left column was relaxed.

---

## 7. `.gitignore`, `requirements-docs.txt`, `.vale.ini`, and the vocabulary

### `.gitignore`

Created or merged into first, before `vale sync` downloads anything and before either build writes an output, so none of what the scaffold's own tooling produces ever shows up as an untracked file. The block below is what the scaffold needs the file to carry:

```
# Build outputs: both builds write here, and CI rebuilds them from source.
/site/
/site-internal/
# Vale packages that `vale sync` downloads into StylesPath. Only the project vocabulary under styles/config/ is committed.
/styles/*
!/styles/config/
# /docs-serve's pid/port record. The profile beside it is committed, so never ignore the directory.
/.dev-workflows/docs-serve.state.json
```

**Create or merge — never replace.** Where the resolved root has no `.gitignore`, write the block above as the whole file. Where it has one, **append only the lines of the block it does not already contain verbatim, at the end of the file and in the block's order — never removing, reordering or rewriting a line that is already there**, and starting on a new line: where the file does not end in a newline, terminate its last line first — a line terminator, not a change to that line's text, though git's diff will show the line as changed — or the first appended line fuses with it and rewrites it. The reason is the directory `/docs-init` accepts. Phase 0 takes any git work tree that carries no docs signal, and a common one is a repository created on a hosting service with a language template's `.gitignore` already committed — every line of which is the project's own decision: its virtualenv, its caches, its secrets file. Replacing the file would un-ignore all of them silently, in a diff that reads as a docs scaffold, and the next `git add` by anyone would commit what the project had deliberately kept out. An exact line already present is therefore skipped rather than duplicated, and an equivalent line spelled differently (`/site` against `/site/`) is appended beside it — two patterns matching the same build directory cost nothing.

**A pre-existing line can still ignore a path the run writes, and it is reported, not rewritten.** The block's own lines never do — that is what its two narrow rules below are for — but a project line can: `styles/` — beneath which no line appended after it can re-include a file — or a template's `*.svg` or `*.css`. **The commit-time ignore test** is how a run finds out, and it runs **at commit time, immediately before staging**, over every path the run wrote — `/docs-init` Phase 8, where that includes whatever its `/docs-brand --inline` phase wrote, and a standalone `/docs-brand` run's Phase 10. It cannot run earlier: the branding phase writes a logo and favicon under `docs/assets/` whose names nothing before it knows. Test each written path with `git -C <root> check-ignore -v <path>`; a line it prints whose pattern starts with `!` re-includes the path, and is no match. For each path that matches:

- **Leave it unstaged** — never force-added past the project's own rule. The line that matched is the project's, and it stays as it is.
- **Remove every reference a committed config makes to it**, before staging, so that no committed config ever names a file the commit leaves out: a `theme.logo` or `theme.favicon` key, an `extra_css` entry, or — for a page — its `nav:` entry, by regenerating the block by §4's rule over the pages being committed. A logo the project's `.gitignore` keeps out would otherwise be a broken image on every page of the committed site.
- **Name it in the pull-request draft and in the run's report**: the path, the ignoring line with its line number, and every reference removed. Those removals come after the run's own verification and review looked at the tree, so the report says the committed configs differ from the verified ones by exactly those references.

**Two of these rules are narrower than they could be, and each is narrow on purpose.** `/styles/*` with `!/styles/config/` rather than `/styles/`, because git cannot re-include a file whose parent directory is ignored: ignoring `styles/` wholesale would drop `accept.txt` — the one file under it the scaffold commits — from the repository. And the `/docs-serve` state file by name rather than `.dev-workflows/`, because that directory also holds `docs-profile.yml`, which is committed and which the family's other commands read; ignoring the directory would silently drop the profile from the next commit that touched it.

### `requirements-docs.txt`

The CI workflow's first job is to reproduce the build, so the scaffold writes the dependency file that step installs:

```
mkdocs-material
```

**One pin is all a `--strict` build needs.** `mkdocs-material` pulls `mkdocs` and the `pymdownx` extensions §5 enables, so every extension in that config resolves from this single requirement. A project adds to this file as it adds plugins; the scaffold does not guess at any.

The file is not optional and is not a convenience: `visibility.md` §6's workflow runs `pip install -r requirements-docs.txt`, and a workflow whose first substantive step installs a file the scaffold never wrote fails on the repository's very first CI run.

### `.vale.ini` and the vocabulary

Vale is the deterministic pre-lint the family's existing style gate already knows how to run — `docs-style-checker` runs a repo's `.vale.ini` as its primary rung — so writing this file lights up an existing gate with no new wiring.

```ini
StylesPath = styles
MinAlertLevel = suggestion
Packages = Google, write-good
Vocab = Project

[*.md]
BasedOnStyles = Vale, Google, write-good
```

`Packages` load in order, with later entries overriding earlier ones, so a project package added later can override Google's rules without editing them.

After writing the file, run **`vale sync`** to download the packages named by `Packages` into `styles/` — from the repository's top level, in the form `references/toolchain-preflight.md` §2, source 2, gives for a configuration that sets `StylesPath`, as this one does: `(builtin cd "<root>" >/dev/null && unset VALE_CONFIG_PATH && command vale --no-global sync)`. A `.vale.ini` naming a package that was never synced fails at the first lint, which the scaffold's own verification phase surfaces immediately rather than leaving for the first contributor.

**`vale sync` runs in CI as well as locally, and that is not a duplicate.** Sync writes the downloaded packages into `StylesPath` (`styles/`), and those are third-party bundles a repository does not commit — what the scaffold commits under `styles/` is the vocabulary below and nothing else. So a fresh CI checkout has a `.vale.ini` naming packages that are not on disk, and `visibility.md` §6's Vale step therefore runs `vale sync` before `vale docs/`. A workflow that lints without syncing fails on a clean runner while passing on the author's machine, which is the least useful shape a CI failure can take.

### The exit criterion — stated here, once

**`vale docs/` passes when it exits 0.** Vale exits non-zero when any **error**-level alert fires, and on a configuration or runtime error — a package never synced, a style that does not resolve, a vocabulary directory that does not exist. Warning- and suggestion-level alerts are reported and never change the exit code. That is Vale's own default, and it is the criterion **both** places that gate on this scaffold's lint apply: `/docs-init` Phase 7 step 3, and the Vale step of `visibility.md` §6's CI workflow. **Both read the repository's configuration alone**, and so does the `vale sync` before each — `/docs-init` Phase 4's in the same form as Phase 7's lint, so the packages it installs are the ones this file names, in its `styles/`. Vale merges a user's global configuration — `~/.config/vale/.vale.ini` on Linux, wherever `vale ls-dirs` names it elsewhere — under the repository's, and a global one can turn off a rule the repository enables only through `BasedOnStyles` (Vale 3.21: a global `Vale.Repetition = NO` makes a scaffold whose repetition fails CI exit 0), while a `VALE_CONFIG_PATH` makes Vale read the file it names in place of the repository's. So Phase 7 runs Vale in the form `references/toolchain-preflight.md` §2, source 2, gives for a configuration that sets `StylesPath`, as this one does — `(builtin cd "<root>" >/dev/null && unset VALE_CONFIG_PATH && command vale --no-global docs/)` — and the CI step runs `vale docs/` bare on a runner that carries neither: a GitHub-hosted one, the kind the workflow declares, has no Vale on its image until the workflow installs the binary, and the scaffold's workflow sets no `VALE_CONFIG_PATH`. Same criterion, same configuration, same exit code — so a scaffold that passes the one cannot fail the other on its first run over the same files, which is the gap this paragraph exists to close. Three things can still make the two differ, and none is a second criterion: a scaffold path a project `.gitignore` line keeps out of the commit (the `.gitignore` rule above reports it by name, and an uncommitted `accept.txt` fails CI's lint); a Vale release or synced package that is newer on the runner than on the machine that ran the scaffold's own check; and a runner of the project's own that does carry a global Vale configuration or set `VALE_CONFIG_PATH`, which the bare CI step reads and Phase 7 does not. **Neither place passes a flag that moves the line**: `--no-exit`, which makes Vale exit 0 whatever it finds; `--filter` or `--glob`, which narrow the rules or files checked and so can leave an error-level alert unraised (`--filter='.Level in ["warning", "suggestion"]'` turns a failing file into a passing one); or `--config`, which swaps the configuration. `--no-global`, which Phase 7 passes, moves no line and swaps nothing in: it drops the machine's global configuration, and with it Vale's default StylesPath — which, for a configuration that sets `StylesPath = styles`, where `vale sync` installs, holds nothing on a clean runner — so it leaves the repository's configuration and its styles, the ones CI reads. **`MinAlertLevel` does not move it**, whether set as the `.vale.ini` key or as the `--minAlertLevel` flag: it sets the lowest severity Vale *reports*, and since `error` is the highest severity there is, no setting of it can filter out an error-level alert or change the exit code. Vale's own documentation says both halves — only error-level alerts produce a non-zero exit, and `MinAlertLevel` is the minimum level reported — and Vale 3.21 confirms it: a file carrying only warnings and suggestions exits 0, and a file carrying one error-level alert exits 1, under every `MinAlertLevel` from `suggestion` to `error`. So `.vale.ini`'s `MinAlertLevel = suggestion` reports every alert and fails on exactly what `error` would; a reviewer reading it as a stricter gate has misread it. Every other file that mentions this criterion cites this paragraph rather than restating it.

**The scaffold passes its own gate, and that is a property of this file rather than luck.** Run over §3's stubs with the configuration above and the seed below, Vale raises no error-level alert — checked against Vale 3.21 with the `Google` and `write-good` packages when this was written. Two things buy it. The seed below covers every word the stubs use that the dictionary does not know. And the stubs write an em dash **without** surrounding spaces, because `Google.EmDash` is an error-level rule — which is why they read differently from the prose in this file. **A stub edited later has to keep the property**: a spaced em dash, or a word the dictionary lacks, fails the step and fails CI. Reword the stub, or add a genuine term to the seed list here in the same change — never a word to `accept.txt` at run time to make a failing step pass.

### The vocabulary is seeded, not left empty

`styles/config/vocabularies/Project/accept.txt` holds the product's own terms — one per line, regex-escaped — so Vale stops reporting them as misspellings.

**Seeding it is not a nicety.** Without it every product noun is a spelling error on day one — and `Vale.Spelling` is an error-level rule, so under the criterion above that is a failing gate rather than noise — the first lint returns dozens of findings that are all wrong, and the team turns Vale off in week two. A linter that cried wolf once is a linter nobody re-enables.

**There are two seeds, and only one of them has a command.**

- **The scaffold seed — written by `/docs-init`, always.** It exists so the scaffold passes its own gate, and it is **not** a domain vocabulary. It is the comment, the product name, and the words §3's stubs introduce that the dictionary does not know — the last derived by running Vale over the stubs, not guessed:

  ```
  # Product terms Vale should not flag as misspellings.
  # Add terms by hand — one per line, regex-escaped.
  <product>
  [Ff]rontmatter
  [Hh]ostnames?
  [Rr]unbooks?
  [Ww]alkthroughs?
  ```

  `<product>` is the product name `/docs-init` confirmed at its Phase 2, regex-escaped — a scaffold-time substitution like every other `<product>` in this file, and the entry that matters most, because every stub names the product and a name the dictionary lacks fails the gate on every page. The four patterns after it are the stubs' own technical vocabulary; each admits its capitalised form because a vocabulary entry also fixes a term's case — `Vale.Terms`, an error-level rule, reports `Runbooks` against a lowercase-only `runbooks?` — and a stub title starts with a capital.
- **The domain seed — nobody's, and added by hand.** **No command of this family extracts a product's domain nouns, and nothing adds to this file after `/docs-init` writes the seed above**, `/docs-audit` included: that command enumerates documentation *surfaces* and writes a backlog, and it never opens `.vale.ini`, a `StylesPath` or a vocabulary. So the comment above is the whole instruction, and the scaffold seed's boundedness has nothing to do with waiting for one: **the scaffold has to pass the lint gate it installs on its own first run**, before anyone has written a page or audited anything, and the seed is exactly the words that run needs. A term added beyond it silences the linter over prose that does not exist yet, which is why `docs-scaffold-reviewer` dimension 4 reports one.

The file is created on every `/docs-init` run. An absent `accept.txt` beside a `Vocab = Project` line is a configuration defect, and Vale's exit code does not reliably report it: where the `Project/` directory is gone too — as it always is on a fresh checkout, since git tracks no empty directory — Vale stops with a runtime error and exits 2, but an empty `Project/` directory left behind passes with exit 0 (both checked against Vale 3.21). So the file's presence is checked directly, by `docs-scaffold-reviewer` dimension 4, rather than left to the lint step.

---

## 8. Hard rules

- NEVER hand-edit a generated `nav:`. Change `order:` or `title:` and regenerate (§4).
- NEVER let the two configs differ in their content source — `docs_dir`, `markdown_extensions`, `theme`, `extra_css`, `validation`, or the nav-generation rule. `exclude_docs`, `site_name`, `site_dir` and the generated `nav:` are the four that may differ, and §6's table is the list (§6).
- NEVER omit `site_dir: site-internal` from the internal config — without it both builds write to `site/` and gate 2 greps the wrong tree (§6).
- NEVER remove `_snippets/` from either config's `exclude_docs`, and never remove `base_path: [docs/_snippets]` to "match" it — the pairing is what makes fragments includable without rendering them (§5).
- NEVER write a directory without its stub, and never write a **directory** stub without its "what does not belong" half (§3). A leaf-page stub carries the lighter shape §3.12 defines and is exempt from that half, by the narrowing recorded there.
- NEVER write a file under `internal/` without the visibility marker on its first line after the frontmatter (`visibility.md` §5).
- NEVER put a page stub in `_snippets/`, `assets/` or `stylesheets/` (§3.13).
- NEVER create `.vale.ini` without also creating `accept.txt` carrying the scaffold seed, and never write the CI workflow without `requirements-docs.txt` beside it — a workflow installing a file the scaffold never wrote fails on the first run (§7).
- NEVER apply a different Vale exit criterion locally than in CI, and NEVER add a flag that moves it (`--no-exit`, `--filter`, `--glob`, `--config`) — §7 states it once, and both apply it (§7). `MinAlertLevel` changes what is reported, never what fails, and `--no-global`, with `VALE_CONFIG_PATH` cleared — the form `references/toolchain-preflight.md` §2, source 2, gives for a configuration that sets `StylesPath`, as this one does — is how the local check reads the repository's configuration alone, as CI does (§7).
- NEVER write a stub that raises an error-level Vale alert — no spaced em dash, no word the dictionary lacks unless it is in the scaffold seed — since the scaffold has to pass its own gate (§7).
- NEVER ignore `styles/` or `.dev-workflows/` wholesale in `.gitignore` — the first holds the committed vocabulary, the second the committed profile (§7).
- NEVER replace an existing `.gitignore`, and NEVER remove, reorder or rewrite a line already in one — append only the lines of §7's block it lacks (§7).
- NEVER stage a written path the project's own `.gitignore` ignores, never force-add one, and never commit a config that names one — run §7's commit-time ignore test immediately before staging, over every path the run wrote, and report each match (§7).
- NEVER write a `logo:` or `favicon:` key the scaffold has no file for — `/docs-brand` adds both when it applies a logo (§5).
