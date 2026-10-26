# /api-guideline-reviewer

Reviews OpenAPI specification files against the bundled REST API and IAM permission-naming guidelines, distilled from public sources (Google AIP, the Zalando and Microsoft REST API guidelines, OpenAPI 3.1, and the relevant RFCs). The review runs in two halves: a **deterministic Spectral lint** against a bundled ruleset, then the LLM passes, scoped to what a linter cannot express.

## Who runs it

`/api-guideline-reviewer` is **standalone**: it consumes no workflow artifact and produces none, needs no `$SPECS_PATH` and opens no branch, and runs no LLM-model classification step — the command file carries no classification phase, no `model_routing` block, and no Opus/Sonnet chain reference. [Workflow overview](../workflow.md) shows it alongside [`/guideline-reviewer`](guideline-reviewer.md), its sibling reviewer for app code and UI rather than API specs.

## Synopsis

```
/api-guideline-reviewer <spec-file(s)> [--rules <path>]
```

`$ARGUMENTS` names one or more OpenAPI spec files. Leave it empty and the command asks which file(s) to review before dispatching anything.

## What it needs

- One or more OpenAPI spec file paths.
- Optionally, a Spectral CLI — see [Deterministic lint](#deterministic-lint) below. Without one the review still runs.
- Nothing else — no `$SPECS_PATH`, no branch, no specs-repo preflight. The command reads the named files and the vendored guideline references, and writes nothing.

## Deterministic lint

Before any LLM pass, the subagent lints the spec files with [Spectral](https://github.com/stoplightio/spectral) — once per directory it lints from, found for each spec as **Resolution** below says — against the ruleset bundled at `references/api-guidelines/spectral/ruleset.yaml`. That ruleset extends `spectral:oas` (recommended) and adds forty rules of its own, covering the seven areas the guidelines state mechanically: version-field shape, required document elements, naming conventions, IAM scope grammar, HTTP status codes, schema composition, and header hygiene — including the single org-wide tenant-header spelling and the org-wide security-scheme name, which are pinned as literals rather than described in prose.

**Resolution.** The subagent probes `spectral` on `PATH` first, then `npx --no-install @stoplight/spectral-cli`. The first that answers is used. If a `.spectral.yaml`, `.spectral.yml`, or `.spectral.json` sits at or above the spec — the nearest one, up to its repository's top level, or, for a spec in no repository, one in the spec's own directory, where the search stops — that ruleset is used instead of the bundled one: an organization is expected to *extend* the bundled ruleset in its own file rather than edit the bundled file in place. Both the probes and the lint run from the nearest directory above the spec that carries a ruleset or a `package.json` declaring the CLI — where the ruleset, or the CLI, is — else the repository's top level, or, for a spec in no repository, the spec's own directory, whichever directory the session stands in, since `npx --no-install` looks for the CLI in the project it runs in; and because the lint runs there, the ruleset is passed to Spectral by its absolute path. Specs that share that directory are linted together, in one run, and the findings from every directory are merged, each keyed by its spec file: a monorepo package that keeps its own ruleset or CLI is linted from there, and specs reviewed together from two such packages are each linted from their own package.

**Degradation.** No Spectral CLI is not a failure. Where none answers from a directory, that directory's lint is skipped, no prompt is raised, nothing is installed, the run does not fail, and the review of its specs proceeds exactly as it did before the ruleset existed — every check the linter would have made on them reverts to the LLM passes. The same applies when Spectral resolves but errors: an unparseable ruleset, or a run that exceeds roughly two minutes. The verdict records the outcome as `lint_source: none` with a one-clause reason. A non-zero exit code is *not* a failure signal here — Spectral exits non-zero whenever it reports findings, so the subagent judges success by whether it got parseable JSON.

**Merge, not duplication.** Spectral's findings are authoritative for the rules it covers, and the LLM passes do not restate them. Each finding in the verdict is attributed — `spectral:<rule-id>` for a machine-checked one, `review` for a reasoned one.

### Before your first real run

**Five bundled rules carry a placeholder, and two of them fail at `error` on any real specification that declares a tenant header or a security scheme.** The ruleset pins the organization-wide spellings the guidelines call "the organization's single declared" value — and ships them with the placeholders the bundled template uses, so that template lints clean, not with your organization's values:

| Rule | Severity | Placeholder | What you replace it with |
|---|---|---|---|
| `api-tenant-header-canonical-spelling` | `error` | `Example-Tenant` | your tenant header's spelling |
| `api-security-scheme-name-consistent` | `error` | `oauth2` | your security scheme's id |
| `api-custom-header-org-prefix` | `warn` | `Example-` | your custom request-header prefix |
| `api-response-header-org-prefix` | `warn` | `Example-` | the same prefix, on response headers |
| `api-operation-id-verb-first` | `warn` | an open verb list | the verbs your operation ids start with |

Left as shipped, a specification that sends `Acme-Tenant` and names its scheme `bearerAuth` gets both as **Mistakes** — MUST violations — on its first run. Override the five once, in a `.spectral.yaml` at the root of the API repository that `extends` the bundled ruleset. The ruleset's own header comment, at the top of `references/api-guidelines/spectral/ruleset.yaml`, shows the override for the tenant header, both header prefixes and the verb list; the scheme id, which it does not show, is the `values` list of `api-security-scheme-name-consistent`. The review then uses your file, as **Resolution** above says.

**What stays with the LLM passes**, whether or not Spectral ran:

| Check | Why a linter cannot make it |
|---|---|
| Version **agreement** | Spectral checks each version field's shape alone; that `info.version`, `servers[].url` and `x-gateway-url` name the *same* major is a cross-field comparison it cannot express. |
| `allOf` property redefinition | Needs the `$ref` resolved and two property sets intersected. |
| Error-envelope conformance | Needs the organization's envelope schema identity. |
| Semantic naming quality | Noun vs verb, singular vs plural, American English, "overly generic" — all judgements. |
| Conditional requirements | Whether `x-gateway-url` or the `deprecated` field is required at all depends on facts outside the document. |
| Resource modelling, documentation adequacy | Decomposition, method choice, whether a description actually informs. |
| IAM scope **correctness** | Spectral checks a scope's grammar; whether its service, resource and action match the URL and HTTP method is a reading of the API. |

## What it produces

The `api-guideline-reviewer` subagent's verdict, printed as-is: a summary carrying the `lint_source` line — one per directory Spectral runs from, each naming its directory, where the specs span more than one — then Mistakes (MUST violations), Potential Improvements (SHOULD violations), and what the spec does well — each finding pointing at the offending element and naming whether it came from the linter or the review. A Spectral finding at severity `error` lands under Mistakes; `warn`, `info` and `hint` land under Potential Improvements, which is how the ruleset's own RFC 2119 severity mapping reaches the verdict.

The agent's frontmatter grants `Read`, `Glob`, `Grep`, and `Bash` — `Bash` so it can find the spec's repository with `git` and invoke the Spectral CLI there. Nothing it finds is auto-fixed by this command.

## Rule overlay

The bundled rules are a **vendor-neutral baseline** distilled from public standards. Rules specific to your organization — an internal scope grammar, a required header spelling, an error-envelope contract — have no public equivalent and deliberately do not ship in a public plugin. Supply them as an **overlay**, resolved in this order, first hit winning (two overlays are never merged):

| Order | Source |
|---|---|
| 1 | `--rules <path>` |
| 2 | `<repo-root>/.dev-workflows/api-guidelines/` |
| 3 | `$API_GUIDELINES_PATH` |
| 4 | the bundled baseline alone |

An overlay is a **flat** directory of `.md` files, matched to the baseline by file name alone — which matters here, because `references/api-guidelines/` is itself two levels deep and holds two files named `Introduction.md`; an overlay file of that name matches both. An overlay file whose name matches a bundled one layers over it and wins on conflict; a file matching none is an additional rule source; an `## Allowed` section suppresses matching baseline rules; and a file whose first line is `<!-- api-guidelines: replace -->` supersedes its baseline counterpart outright. A candidate that is absent or unreadable falls through **silently** — a missing overlay is the normal case, not a problem — but one that is a readable directory holding no `.md` file of its own falls through with a `rules_overlay_skipped:` line naming it, since the usual way to produce one is to mirror the bundled subtree's nesting, and an overlay set up that way would otherwise be lost without a word. The report's `rules_source:` line records what actually resolved (`baseline`, or `overlay:<path>`).

This is the same mechanism the sibling `prose-style` plugin uses for its own rules, deliberately — one convention, not two.

## Gates

There is no review gate here in the pipeline sense — **this command is the review.** No triage, no fixer, no BLOCK/re-review cycle; the subagent's verdict is the final output. The Spectral lint is a pre-pass, not a gate: it never stops the review, and its absence never does either.

## Example

```
/guideline-reviewers:api-guideline-reviewer specs/openapi.yaml
```

Lints `specs/openapi.yaml` with the bundled ruleset where a Spectral CLI is available, then dispatches `api-guideline-reviewer` for the passes the linter cannot make, and prints the merged verdict.

## See also

- [`/guideline-reviewer`](guideline-reviewer.md) — the sibling standalone reviewer for app code and UI instead of OpenAPI specs.
- [Workflow overview](../workflow.md) — where the two standalone reviewers sit relative to each other.
- [Environment](../reference/environment.md) — `$API_GUIDELINES_PATH`, the one variable this command reads.
