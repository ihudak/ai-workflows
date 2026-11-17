# Visibility — two builds from one source tree

Single source of truth for how public and internal documentation are separated, why the obvious ways of checking that separation do not work, and what CI asserts instead.

Consumed by `/docs-init`, which writes the two build configs and the workflow in §6, by `docs-scaffold-reviewer`, whose checklist asserts the relationship §4 describes, by `/document`'s render check, which reads §1 to decide which affected pages the public build excludes (`references/docs-profiles/render-verification.md` §2), by `docs-audit-reviewer`, which reads §1 for the internal tree a unit's `page_path` must agree with, and by `/docs-write`, which reads §1 for the internal tree an internal unit's page must lie under, and holds every page it writes there to §5's marker as its first line after the frontmatter, testing for it before the unit commits, since without it the gate cannot see the page; five references cite it too — `docs-profiles/render-verification.md`, whose §2 is where that render check reads §1, and `scaffold-tree.md`, `docs-profiles/frontmatter-guidelines.md`, `docs-audit/backlog-format.md` and `docs-iteration/unit-brief.md`, which cite single sections of it. `grep -rl 'visibility\.md' plugins/docs-workflows/commands plugins/docs-workflows/agents plugins/docs-workflows/references` lists every reader.

Its entry points, so a command can say which part it is executing: **the model** (§1), **the traps** (§2 and §3), **the gates** (§4), and **the CI workflow** (§6).

---

## 1. The model

One source tree, shared snippets, working cross-links. Two builds over that one tree:

| Build | Config | What it contains | Output |
|---|---|---|---|
| **public** | `mkdocs.yml` | every page except those under `internal/`, dropped by `exclude_docs` (gitignore-style patterns, MkDocs 1.6+) | `site/` |
| **internal** | `mkdocs.internal.yml` | every page, via `INHERIT: mkdocs.yml` plus the internal nav | `site-internal/` |

**The two builds share one content source and differ only in what they publish from it.** `docs_dir`, the `markdown_extensions` set, the `theme` block and the nav-generation rule are identical; `exclude_docs`, `site_name`, `site_dir` and the generated `nav:` are the four things that differ, and `scaffold-tree.md` §6 is the list. Neither exclusion set is empty: the public build drops `internal/` and `_snippets/`, the internal build drops `_snippets/` alone. The fragment directory is excluded from **both** because a fragment is an include and not a page: left in a build, every file under `docs/_snippets/` renders as a standalone page — an orphan in the nav, and, for an internal fragment in the public build, a leak more direct than the one gate 2 exists for. Excluding it costs nothing, because `pymdownx.snippets` reads its fragments off the filesystem rather than out of the build (`scaffold-tree.md` §5).

**`site_dir` is load-bearing here, not cosmetic.** It defaults to `site`, and `INHERIT` merges a parent that does not set it either — so an internal config omitting `site_dir: site-internal` writes over the public output. The two builds are then indistinguishable on disk, and gate 2's grep over `site/` inspects the internal build, where every `internal/` page carries the marker by design: the gate fails on a correct scaffold, in the one way that reads as a genuine leak.

Two outputs, two deploy targets, **two hostnames**.

**Separate hostnames rather than a protected path prefix.** Path-prefix protection is easy to misconfigure and fails open: a rule that was meant to guard `/internal/*` and does not match is indistinguishable, from outside, from no rule at all. A separate host fails closed, because there is nothing at the public host to protect.

**The family does not implement authentication.** Protection at the internal host is the project's own choice — basic auth at a reverse proxy, an SSO proxy, a private host, a VPN. What the family produces is two artefacts and an unambiguous statement of which is which; what happens to the internal one is infrastructure.

One content root is what makes this worth doing at all. A second site would give the internal pages their own search index, their own snippet base path, and broken links in both directions. `visibility` is a build-time decision precisely so that an internal page can link a public one and be right.

---

## 2. Trap 1 — the dev server is not the build

What `mkdocs serve` shows is not what `mkdocs build` ships, and how the two differ depends on the MkDocs version and on which exclusion key a config uses:

- **`exclude_docs`** — the key §1's public build uses. On MkDocs 1.6, the version §1's configs are written for, `mkdocs serve` drops an excluded page as the build does, and its URL answers 404. Up to MkDocs 1.5 the dev server still rendered it, at its ordinary URL.
- **`draft_docs`** (MkDocs 1.6+) — a page it names renders under `mkdocs serve` and is left out of `mkdocs build`: readable in the preview while it is drafted, and never shipped.

And **no version's dev server can show §3's leak.** An internal snippet included into a public page renders inside that page wherever the page renders, so the preview shows an ordinary public page with nothing to mark what crossed.

**Rule: visibility is never confirmed by looking at the dev server.** Not by browsing it, not by searching it, not by checking that a URL 404s in it. It is confirmed against **built output** only — `site/`, produced by `mkdocs build`, which is the artefact that is actually deployed. The reason holds on every version: whatever a dev server happens to show, **what you see locally is not what ships.**

A run that reports "the internal page is not in the public site" on the strength of a dev-server observation has reported nothing.

---

## 3. Trap 2 — snippets cross the boundary invisibly

`pymdownx.snippets` lets a page include a file from `docs/_snippets/`. An **internal snippet included into a public page leaks its content** even though every file sits in exactly the correct directory.

A path-based rule cannot catch this, because **no path is wrong**. The internal snippet is under the snippet root, the public page is outside `internal/`, and the include is a legal include.

**Excluding the snippet does not help, and understanding why is the whole trap.** `exclude_docs` governs what the build renders as a page; `pymdownx.snippets` reads its fragments off the **filesystem**. So `_snippets/` is excluded from both builds and every fragment is still includable — which is what makes that exclusion safe (§1) — and it is exactly why the exclusion cannot be the defence here. The fragment never ships as a page; its **content** ships, inside a page that does.

Nor does a link check catch it. There is no link. There is only text that used to be in one document and is now in another.

This is the whole reason the second gate exists, and the reason it asserts on **rendered HTML** rather than on sources.

---

## 4. The two gates

Both gates run in CI, and **both assert on built output**. That is the discipline the traps buy: the dev server is not evidence (§2), and source layout is not evidence (§3), so the only thing left that can be evidence is the artefact that ships.

**Gate 1 — public build with `strict: true`.** `mkdocs.yml` sets `strict: true` and

```yaml
validation:
  nav:
    omitted_files: warn
    absolute_links: warn
```

so a public page linking into `internal/` becomes a **build failure** rather than a broken link discovered by a reader. It is free — the build has to run anyway — and it catches the link class completely.

**Gate 2 — marker grep over the public build output.** Every file under `docs/internal/` and every snippet intended for internal pages carries the §5 marker. The gate fails if that marker appears anywhere under the public `site/` tree. This is what catches the snippet-level leakage §3 describes, which paths and links both miss.

Gate 2 is the same technique as verifying a history rewrite by grepping the resulting blobs: **assert on the artefact, not on the intent.**

**Every tool the workflow invokes, the workflow installs.** A CI file is not a note to a human who already has the toolchain; it runs on a bare runner. So §6 installs the Python build dependencies from `requirements-docs.txt` (which the scaffold writes — `scaffold-tree.md` §7), installs the Vale **binary** explicitly rather than assuming it, and runs `vale sync` before linting because the style packages `.vale.ini` names are downloaded rather than committed. A step that invokes a tool no earlier step provided is a gate that fails on the repository's first run and teaches the team to distrust the workflow before it has ever caught anything.

### The third gate, and when it exists

`images.policy` in the profile (`references/docs-profiles/docs-profile-schema.md` fixes the field and its per-policy rules; they are not restated here) decides whether a third gate is written at all, because the two above have no reach into an object store.

- **`in-repo`** — no third gate, because there are no image **URLs** to check: an image is a file in the tree, referenced by a relative path, and the build resolves it. What separates the two builds here is the same `exclude_docs` that separates the pages — it drops files, not only Markdown — so **an image that only internal pages may see belongs under `docs/internal/`, not under `images.root`.** A file under `images.root` is copied into *both* builds whether or not any page references it: MkDocs copies the content tree, it does not trace references. What is written instead of a gate is the **size-budget step**, checking each file under `images.root` against `images.max_bytes`, because committed binaries are permanent and an unbudgeted default is how a docs repository becomes one nobody wants to clone. **Both halves of that step come from the profile** — the path from `images.root` exactly as the threshold comes from `images.max_bytes` — and §6's template shows the two defaults (`docs/assets` and `+300k`, the latter rendering 307200 bytes) rather than fixed values. A step that hardcoded `docs/assets` against a repository whose `images.root` is anything else would scan an empty directory and pass forever, which is the failure this section condemns two paragraphs below.
- **`object-store` and `cdn`** — the third gate is written, and the size-budget step is not. **A bucket has no notion of the two builds.** A public page referencing an internal screenshot leaks the image while gates 1 and 2 both pass, because the leak is in the object store and not in the HTML. So the gate asserts that **every image URL in the built public output starts with `images.public_prefix`**; under `object-store`, internal media lives under `images.internal_prefix`, which is what the gate is separating it from. A gate cannot assert against a prefix the profile does not record, which is why those two fields are part of the schema rather than left to convention.

**Neither step is written unconditionally.** A size-budget step under `cdn` checks a directory that holds no images; an image-prefix gate under `in-repo` checks URLs that do not exist. Both are green forever, which is worse than absent: a gate that cannot fail teaches a reviewer that the gate set is complete when it is not.

The script the template names — `scripts/check-image-prefix.sh` — is part of the **scaffolded repository**, not of this plugin. What it must assert is the sentence above: every image URL in the public build output resolves to `images.public_prefix`, with the offending page and URL named on failure, and a non-zero exit.

---

## 5. The marker convention

Every file under `docs/internal/`, and every snippet intended for internal pages, carries this as its **first line after the frontmatter**:

```markdown
<!-- docs-visibility: internal -->
```

An HTML comment survives into rendered output, which is exactly the property gate 2 needs: the marker travels with the content, through a snippet include, into whatever page inlined it, and lands in the HTML where a grep over `site/` finds it. A frontmatter key would not — it is consumed by the renderer and never reaches the artefact — and neither would a naming convention, because §3's leak carries content across a boundary while leaving every name correct.

Two consequences worth stating, because both halves of the convention have to agree or the gate is decoration:

- **A snippet under `docs/_snippets/` that is meant for internal pages carries the marker too.** It is not under `internal/`, so nothing else marks it, and it is the exact file §3's trap travels in.
- **A public page never carries the marker**, not even quoting it in prose about visibility. Gate 2 greps for the literal string, so a page explaining the convention would fail the build that ships it. Documentation of the marker belongs outside the built tree — in this reference, and in the plugin's own `docs/`.

---

## 6. The CI workflow

`/docs-init` writes this to `.github/workflows/docs.yml`. Both builds run, the visibility gate runs against the public output, every tool a step invokes is installed by an earlier step (§4), and the image steps are written per `images.policy`. The two steps marked `WRITTEN ONLY WHEN` are **conditional and are omitted, not disabled, when the policy does not call for them**; the other comments mark scaffold-time substitutions, which are resolved rather than left in place.

```yaml
name: docs
on:
  pull_request:
  push:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements-docs.txt
      # Vale is a single static binary, not a pip package, so it is installed explicitly.
      # <VALE_VERSION> and the asset name are scaffold-time substitutions, resolved against
      # the project's current release — pinned, never floating, and never copied from here.
      - name: Install Vale
        run: |
          curl -sSfL "https://github.com/vale-cli/vale/releases/download/v<VALE_VERSION>/vale_<VALE_VERSION>_Linux_64-bit.tar.gz" \
            | sudo tar -xz -C /usr/local/bin vale
      - name: Build public site
        run: mkdocs build --strict -f mkdocs.yml
      - name: Build internal site
        run: mkdocs build --strict -f mkdocs.internal.yml
      - name: Gate 2 — no internal marker in the public build
        run: |
          if grep -rl 'docs-visibility: internal' site/; then
            echo "::error::internal content reached the public build"
            exit 1
          fi
      # WRITTEN ONLY WHEN images.policy is object-store or cdn — omit under in-repo
      - name: Gate 3 — every public image URL resolves to the public prefix
        run: scripts/check-image-prefix.sh
      # WRITTEN ONLY WHEN images.policy is in-repo — omit under object-store and cdn.
      # BOTH the path and the threshold are scaffold-time substitutions from the profile,
      # at every place the step names them: the path is images.root (docs/assets below is
      # its default), and the threshold is images.max_bytes, rendered as a find size suffix
      # (+300k renders the 307200 default) and in the error message's wording.
      - name: Image size budget
        run: |
          if [ ! -d docs/assets ]; then
            echo "docs/assets does not exist yet: no committed image to budget"
            exit 0
          fi
          find docs/assets -type f -size +300k -print -exec false {} + \
            || { echo "::error::image over the 300 KB budget"; exit 1; }
      # `vale sync` downloads the packages .vale.ini names; they are not committed.
      # `vale docs/` is run bare: its exit code IS the gate (scaffold-tree.md §7).
      - name: Vale
        run: |
          vale sync
          vale docs/
```

Gate 1 is not a step of its own: it **is** the `Build public site` step, because `strict: true` in `mkdocs.yml` is what makes a cross-boundary link fail the build. A workflow that ran the build without `--strict`, or a config that dropped `strict: true`, would silently retire gate 1 while the step still appeared to run — which is why `docs-scaffold-reviewer` checks the config and the workflow against each other rather than either alone.

The internal build runs on every PR too. It is not deployed from here, but a config that has drifted into a second source of truth fails loudly at build time rather than at the next release.

**The size-budget step passes when `images.root` does not exist, and that is not a gate that cannot fail.** Git tracks no empty directory, so a scaffold that has committed no image yet — every `--no-brand` run, and every run whose branding applied no logo — has no `docs/assets/` on the runner at all, and a bare `find` over it exits non-zero and reports exactly as an over-budget image would. The guard makes the step's first run pass for the right reason; the moment an image is committed the directory exists and the budget applies to it. It cannot mask an over-budget image, because an over-budget image is a file, and a file means the directory exists.

**The Vale step's exit code is the gate, unmodified.** It passes by the criterion `scaffold-tree.md` §7 states once — the one `/docs-init`'s own Phase 7 applies, over the same configuration: Phase 7 clears what a machine adds to it (`--no-global`, and no `VALE_CONFIG_PATH`), and the runner this workflow declares adds nothing — so a scaffold that passed locally does not fail here on its first run over the same files (§7 names what can still make them differ). Nothing that moves or discards that exit code belongs on this step: not a Vale flag that moves the line (`scaffold-tree.md` §7 names them — `--no-exit`, `--filter`, `--glob`, `--config`), and not a shell or workflow construct that swallows a failure (`|| true`, `continue-on-error: true`). `--minAlertLevel` is not one of them — it changes which alerts are reported, and no value of it hides an error-level alert (`scaffold-tree.md` §7) — but the step still runs `vale docs/` bare, because the same criterion over the same configuration in both places is what makes CI report what Phase 7 reported.

---

## 7. Hard rules

- NEVER confirm visibility from the dev server. Built output only (§2).
- NEVER treat correct file placement as evidence that content did not cross the boundary (§3).
- NEVER write an internal file, or an internal-only snippet, without the §5 marker.
- NEVER quote the literal marker string on a page inside the built public tree.
- NEVER write a conditional image step the resolved `images.policy` does not call for (§4).
- NEVER let the two build configs differ in their content source — `docs_dir`, `markdown_extensions`, `theme`, `validation`, or the nav-generation rule. `exclude_docs`, `site_name`, `site_dir` and the generated `nav:` are the four that may differ (`scaffold-tree.md` §6).
- NEVER ship an internal config without `site_dir: site-internal` — both builds then write to `site/` and gate 2 greps the internal output.
- NEVER write a workflow step that invokes a tool no earlier step installed (§4).
- NEVER hardcode the size-budget step's path or threshold; both come from the profile (§4).
