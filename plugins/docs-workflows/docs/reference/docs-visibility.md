# Documentation visibility

A documentation portal usually has to publish two things at once: pages anyone may read, and pages only the team that builds the product should. This page describes how this plugin's scaffolding commands separate the two, why the two obvious ways of *checking* that separation both fail, and what CI asserts instead.

It documents the plugin's own visibility reference, listed on [References](references.md), which is the file the commands actually execute. If the two ever disagree, that file is right.

## One source tree, two builds

There is exactly one directory of Markdown. Internal pages live under `docs/internal/`; everything else is public. The split happens at **build time**, not in the source:

| Build | Config | Contains | Output |
|---|---|---|---|
| public | `mkdocs.yml` | every page except those under `docs/internal/`, dropped by `exclude_docs` | `site/` |
| internal | `mkdocs.internal.yml` | every page, via `INHERIT: mkdocs.yml` plus the internal nav | `site-internal/` |

The two configs share **one content source** and differ only in what they publish from it. The documentation directory, the Markdown extension set, the theme and the navigation-generation rule are identical. Four things differ, and only these four: which paths each excludes, the site name, the output directory, and the navigation block each generates. That is deliberate and it is checked — two configs that differ in their content source are two sites, and the shared snippets, shared search index and working cross-links that one source tree buys are gone.

The output directory matters more than it looks. It defaults to `site` for both configs, and the internal one inherits from the public one, so an internal build that does not set `site_dir: site-internal` **writes over the public build's output** — after which the marker gate below inspects the internal pages, every one of which carries the marker by design, and fails on a perfectly correct repository.

Neither exclusion set is empty. The public build drops `docs/internal/` **and** `docs/_snippets/`; the internal build drops `docs/_snippets/` too. The fragment directory is excluded from both because a fragment is an include, not a page: any `.md` file inside the documentation directory is rendered as a standalone page unless something excludes it, so leaving the fragments in would give every one of them its own orphan page in both builds — and would publish an internal fragment as a public page, which is a more direct leak than the one the second gate below exists for. Excluding them costs nothing, because the snippets extension reads fragments off the filesystem rather than out of the build, so an excluded fragment is still includable.

The two outputs go to two deploy targets on **two hostnames**, rather than to one host with a protected `/internal/` path. Path-prefix protection fails open — a rule that stops matching looks, from outside, exactly like no rule — while a separate host fails closed, because there is nothing at the public address to protect.

**The plugin does not implement authentication.** It produces two build artefacts and says unambiguously which is which. Protecting the internal host is the project's own infrastructure choice: basic auth at a reverse proxy, an SSO proxy, a private host, a VPN.

## Two traps

Both of these look like they should work. Neither does, and each one is why one of the gates below exists.

### The dev server is not the build

What the local preview (`mkdocs serve`) shows is not what the build ships, and how the two differ depends on the MkDocs version and on which exclusion key a config uses. The public build drops internal pages with `exclude_docs`: on MkDocs 1.6, which the scaffold's configs are written for, the preview drops them too and their URLs return 404, while up to MkDocs 1.5 it still rendered them at their ordinary URLs. A page named by `draft_docs` goes the other way — it renders in the preview while it is drafted, and never ships. And no version's preview can show the snippet leak described next, because the leaked text renders inside a public page like any other text on it.

So: visibility is never confirmed by looking at the dev server. Not by browsing it, not by searching it, not by checking that a URL returns 404 in it. It is confirmed against built output only, which is the artefact that is actually deployed — whatever a preview happens to show, **what you see locally is not what ships**.

### Snippets cross the boundary invisibly

Pages can include reusable fragments from `docs/_snippets/` with `pymdownx.snippets`. An internal fragment included into a public page **leaks its content while every file sits in exactly the right directory**.

No path is wrong, so no path-based rule can see it. Nor does excluding the fragment help, and the reason is the same one that makes excluding it safe: `exclude_docs` governs what the build renders as a page, while the snippets extension reads fragments off the filesystem. The fragment never ships as a page — its **content** ships, inside a page that does. A link checker sees nothing either, because there is no link: there is only text that used to be in one document and is now in another.

## The two gates

Both run in CI, and both assert on **built output**. That follows directly from the traps: the preview is not evidence, and source layout is not evidence, so the only thing left that can be evidence is the artefact that ships.

| Gate | What it does | What it catches |
|---|---|---|
| Public build with `strict: true` | `mkdocs.yml` sets `strict: true` and `validation.nav.omitted_files`/`absolute_links` to `warn`, so a public page linking into `internal/` fails the build | the whole cross-link class, at no extra cost |
| Marker grep over `site/` | fails if the visibility marker appears anywhere in the built public output | snippet-level leakage, which paths and links both miss |

The first gate is not a separate CI step — it *is* the public build step. A workflow that dropped `--strict`, or a config that dropped `strict: true`, would retire the gate while the step still appeared to run.

The second gate is the same technique as verifying a history rewrite by grepping the resulting blobs: assert on the artefact, not on the intent.

### The marker

Every file under `docs/internal/`, and every snippet meant for internal pages, carries this as its first line after the frontmatter:

```markdown
<!-- docs-visibility: internal -->
```

An HTML comment survives into rendered output, which is exactly the property the gate needs: the marker travels with the content, through a snippet include, into whatever page inlined it, and lands in the HTML where a grep finds it. A frontmatter key would not — the renderer consumes it and it never reaches the artefact — and a naming convention would not either, because the leak carries content across the boundary while leaving every name correct.

Two halves of one convention, and both have to hold:

- a snippet meant for internal pages carries the marker even though it does not live under `internal/`, because nothing else marks it and it is the exact file the leak travels in;
- a page in the built public tree never carries the marker, not even quoting it while explaining the convention — the gate greps for the literal string, so such a page would fail the build that ships it. That is why this explanation lives here, in the plugin's own documentation, rather than in the portal being scaffolded.

## A third gate, sometimes

Neither gate above can see inside an object store, so a portal that hosts its images externally needs one more. Which of these is written depends on `images.policy` in the docs profile:

| `images.policy` | Extra CI step |
|---|---|
| `in-repo` | an image **size budget**, checking each file against `images.max_bytes` |
| `object-store`, `cdn` | an **image-prefix gate**: every image URL in the built public output must start with `images.public_prefix` |

Under `in-repo` there are no image URLs to check — an image is a file in the tree, referenced by a relative path — and the same `exclude_docs` that separates the pages separates the files, since it drops any file and not only Markdown. That does mean an image only internal pages may see belongs under `docs/internal/` rather than in the shared assets directory: MkDocs copies the content tree into the build, it does not trace which page referenced what. Under the other two policies a bucket has no notion of the two builds at all: a public page referencing an internal screenshot leaks the image while both gates above pass, because the leak is in the object store and not in the HTML. Under `object-store`, internal media sits under `images.internal_prefix`, which is what the gate separates it from.

Neither step is written unconditionally. A size budget under `cdn` checks a directory holding no images, and a prefix gate under `in-repo` checks URLs that do not exist; both would be green forever, which is worse than absent, because a gate that cannot fail teaches a reviewer the gate set is complete when it is not.

The size budget does pass when the image directory does not exist yet, and that is not the same thing. Git tracks no empty directory, so a freshly scaffolded repository that has committed no image — every scaffold whose branding applied no logo — has no image directory on the CI runner at all, and a bare scan over it would fail its very first run as though an image were over budget. The step checks for the directory first; the moment an image is committed the directory exists and the budget applies. It cannot hide an oversized image, because an oversized image is a file, and a file means the directory is there.

The fields themselves are defined in the docs-profile schema, listed on [References](references.md), which is the authority on what each policy means.
