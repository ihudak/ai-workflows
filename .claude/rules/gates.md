---
paths:
  - "scripts/**"
  - ".github/**"
---

# Gates — what each check enforces and cannot see

Loaded when a file under `scripts/` or `.github/` is read. Repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

**A gate widening or a scope change is measured before it is taken, and one that would fire only on correct content is refused.** Each refused widening below records that result; do not re-propose one without new evidence.

## ID-grammar gate (`scripts/check-id-grammar.sh`)

It runs on every push via `.github/workflows/validate-catalog.yml` — preceded there by `--selftest`, which asserts, per fixture, the exit code **and every ID form the gate must have named** — one grep per alternation of `PATTERN`. The exit code alone is not enough: each negative fixture carries several violating lines, so any surviving alternation holds the exit at 1. `scripts/validate-catalog.py` carries a `--selftest` of its own for the same reason, wired into the same workflow ahead of the run it guards. ([why](../../docs/maintainers/rationale.md#id-grammar))

Of the `id-grammar-ok` markers, one accepts the legacy form as a tolerant reader — `workflows-core:ard-resolution`; the others are the reviewers that check identifier integrity and must quote the form they reject. Re-derive the census with `grep -rn 'id-grammar-ok' plugins/ --include=*.md | grep -v CHANGELOG` — scoped to `plugins/`, not to one plugin, since the split put `workflows-core:ard-resolution`'s marker outside `dev-workflows` rather than adjusting it. The spec/design numbered-ID namespace is deliberately outside this grammar and unchanged; `scripts/spec-id-baseline.txt` is its census tripwire.

## `scripts/check-docs.sh`

`scripts/check-docs.sh` iterates every plugin in its `PLUGIN_RELS` list, so every tree in it is gated identically. It runs on every push via `.github/workflows/validate-catalog.yml`, preceded there by `--selftest`, which copies a fixture tree per case and asserts both the exit code and *which* check fired — one case per check and failure mode, plus the fixture-growing cases that assert the gate still **passes**, which is the only way to prove a number word newly taught to check 9 converts correctly rather than merely being rejected. **No case count is stated in `CLAUDE.md` or the rules files, deliberately**: `--selftest` prints one `ok` line per case, so the number is a `grep -c` away and needs no copy. ([why](../../docs/maintainers/rationale.md#docs-tree))

### Check 1

Links resolve — under each gated plugin, and in `CLAUDE.md`, `.claude/rules/*.md` and `docs/maintainers/*.md`. The link parser does not skip inline code spans, so never write a closing bracket followed directly by an opening parenthesis inside backticks in those files.

### Check 2

Anchors resolve, including a why-link's `#<slug>` into `docs/maintainers/rationale.md`.

### Check 3

No page is unreachable from `docs/README.md`.

### Check 4

The command / agent / reference-file / hook / skill inventories match the shipped tree in both directions.

### Check 5

Every plugin-read environment variable is documented and every documented one is actually read.

### Check 6

No table cell exceeds 200 characters.

### Check 7

`getting-started.md`'s install commands match the repo-root README verbatim.

### Check 8

Every command handing `emit-cost` a fixed `phase`/`role` pair has a matching `workflows-core:cost-emission` §7 row, with no §7 row naming a command that emits no fixed pair.

### Check 9

Every prose count matches the tree — six inventories (commands, agents, reference files, hooks, skills, environment variables) plus the size of the cost-emitting set.

### Check 10

No page under `docs/` names the marketplace this plugin ships from or the repository that contains it, with the token set derived from the repo-root README's own install block so a fork re-derives its own. The rule it enforces is in `CLAUDE.md` § Hard constraints. The check covers the marketplace and the containing repository and nothing else — a dev-environment or container-image repository a page might name is outside it, because nothing in the tree marks which third-party slug that is. Check 10 matches its tokens on word boundaries, not as substrings. ([why](../../docs/maintainers/rationale.md#check-10))

### Check 11

Every `choices:` option in the `/brd-*` and `/prd-*` families — the families check 11 derives from **every** such glob in `workflows-core:next-phase-offer`'s scope paragraph, not only the first, which binds the `<merge-clause>` rule itself to every offer the plugin prints, not only to those two families — carries the placeholder wherever the offering run writes the artifact the offered command's `require-on-main` gate targets, with the families, the gate targets (`workflows-core:phase-handoff`'s row-F table) and the written paths (each command's own `deliverable_paths`) all derived, and every one of those relations coming up empty failing rather than passing — `writers` per family command, so a reworded handoff sentence turns the build red instead of silently dropping that command's offers out of the check.

**What check 11 excludes:** it gates the *presence* of the placeholder, never which row of the resolution table a run resolves it to (naming a branch on a declined handoff, where nothing was committed, satisfies it); it sees `choices:` options only, never a prose `### Next step` offer; and its writer relation is what a command *declares*, so an undeclared path is invisible. `workflows-core:next-phase-offer` states these three where someone reworking the offer convention will meet them.

**Check 11 is not widened past the `/brd-*` and `/prd-*` families to cover the rest of `product-workflows`, and that is evidence, not inertia** — `workflows-core:next-phase-offer` records it, so it is not re-proposed without new evidence. **The widening census itself lives in exactly one place, `workflows-core:next-phase-offer`'s own scope-paragraph section, and is not restated in `CLAUDE.md` or the rules files**: re-measure in one place, cite it everywhere else. ([why](../../docs/maintainers/rationale.md#check-11))

### Check 12

**Check 12 gates the arity rule in `CLAUDE.md` § Hard constraints.** Its parser is **bracket-matched and quote-aware, not a non-greedy regex**, and that is the whole point: `choices:\s*\[(.*?)\]` stops at a `]` inside an option string and silently skips that array. ([why](../../docs/maintainers/rationale.md#check-12))

**What check 12 cannot see, stated because green is not safe here:** an array built at runtime from a directory listing has no literal options to count. The Epic picker `/specify`, `/design` and `/implement` share is exactly that, and it overflows at four Epics where the run appends its own option and at five where it does not — `/specify` appends always, `/design` never, `/implement` only where the PRD folder holds a flat `specification.md`; its cap lives in `workflows-core:epic-picker` *The cap* and is held by review alone.

### No stop-routing check

**Stop routing has no check, deliberately.** The obvious next one — for every `BRD_*` stop naming exactly one command, assert that command's Phase 0 does not itself refuse the described state — was designed and rejected on evidence, and should not be re-proposed without new evidence. Nothing in a stop's text says what state the named command refuses; every proxy tried was either wrong on the live tree or inert on the history it was built for. The two checks that did ship gate the halves that are written down: an artifact's writer, and a gate's target. ([why](../../docs/maintainers/rationale.md#stop-routing-no-check))

### Check 13

**Check 13 gates vendor neutrality**, the rule in `CLAUDE.md` § Hard constraints. It scans every text file under any plugin in `PLUGIN_RELS` — `dev-workflows`, `docs-workflows`, `product-workflows`, `workflows-core` and `guideline-reviewers` today — plus `CLAUDE.md`, `.claude/rules/*.md` and `docs/maintainers/*.md`, which are scanned alongside each of them (binaries never reach it). The sanctioned markers are audited by kind in the check's own comment — **16 marked lines across 8 files** as this is written — and re-derived with `grep -rn --exclude=CHANGELOG.md 'vendor-token-ok:' plugins CLAUDE.md .claude/rules docs/maintainers`, never adjusted as a number. **Widen the scope, not the count, when the corpus moves.** It excludes the changelog by *filename*, never by a filter on line content.

**The token set is tracker names only, and is not widened to the git-forge names**; do not re-propose the widening without new evidence. **The scope stops at the plugin and the repo-root instruction tiers**: the repo-root README documents a sibling plugin whose *subject* is a vendor CLI, the same reason check 10 leaves that file alone. **Its scope is every text file, not just markdown.** Two **paired** selftest cases per surface, red and green in the same file, because an implementation that widened the file set but dropped the marker logic outside markdown passes every red case and fails every green one. ([why](../../docs/maintainers/rationale.md#check-13))

**What check 13 cannot see:** it matches names, so a tracker-shaped *concept* under a neutral name — a `team:` field on an Epic, an import ladder — is invisible to it; that half is review's. Its fence rule is proven by a **pair** of selftest cases, marked and unmarked: an implementation that simply skipped fenced code would pass the marked one for the wrong reason, and templates and handoff blocks are exactly where a tracker-shaped field would hide.

### Check 14

**Check 14 is a different constraint wearing a similar shape, and the two must not be conflated** — it enforces the organisation-identity half of the identity quarantine, the rule in `CLAUDE.md` § Hard constraints, and it honours no marker. It scans the **whole repository** rather than the plugin, because a name leaks through a script comment or a JSON description as easily as through prose. Its token list is stored base64-encoded, never in clear text. ([why](../../docs/maintainers/rationale.md#check-14))

### Check 15

**Check 15 gates index membership** — every command must appear in `docs/README.md`, in the plugin README, and inside `docs/workflow.md`'s **mermaid diagram**, asserted separately from the page. Check 4 proves a command has a page and check 3 proves that page is reachable from *some* page; neither proves it is findable. ([why](../../docs/maintainers/rationale.md#check-15))

### Check 16

**Check 16 gates the loader contract.** Five relations, all derived: every real `args:` string resolves to a file in the corpus (on its **first whitespace token**, because a second token is an entry point *within* the reference — how many of this tree's real invocations carry one is `scripts/check-docs.sh`'s check-16 header's census, the one place it lives); every markdown file in the corpus is reached by at least one citation, counting **three forms** — a loader `args:` string, a `${CLAUDE_PLUGIN_ROOT}/references/<name>` path inside core, and a bare backticked `` `references/<name>` `` inside core, each of which is load-bearing for a different file; every consuming file that cites a core reference carries the loader preamble; no loader call sits inside a fenced block, which a run prints rather than executes; and no file outside core cites a core reference by path in either of the two forms that resolve to the reading plugin — the defect the loader exists to prevent, gated only over `commands/`, `agents/` and `references/`; it is not widened to the whole plugin. ([why](../../docs/maintainers/rationale.md#check-16))

**The bracketed documentation placeholder is not an argument** — the preamble quotes `args: "<name>"` on scores of files, so a forward direction that resolves every `args:` string it meets reports one defect per file on correct content, and it is the placeholder that relation 3 looks for. **Scope is `commands/`, `agents/` and `references/`, measured rather than chosen**, and the check-16 figures live in `scripts/check-docs.sh`'s check-16 header and nowhere else, deliberately.

**What check 16 cannot see:** the bare-basename class — an unqualified `<name>.md` inside core — which is undecidable by pattern, because `design.md`, `idea.md`, `epics.md` and `ready.md` are artifact filenames in the specs tree as well as command basenames; that is `CLAUDE.md`'s own *Resolve an identifier against a known set; never parse one out of free text* rule met in the wild, and it is left to review.

### Check 17

**Check 17 gates agent dispatch authority (PS15)**. What the check gates is the **structural precondition**, not the behaviour: every agent granted `Task` must also carry the rule, matched on the exact anchor sentence ("NEVER dispatch any subagent other than `<name>`. That one dispatch is your entire `Task` authority.") not on the bare word "dispatch", which ordinary prose would satisfy. It fires the moment another agent gains `Task` without the rule, which is the realistic way this decays; it cannot catch a dispatch outside the sanctioned set from an agent that already states the rule, because that is behaviour, not structure, and no static check reaches behaviour. ([why](../../docs/maintainers/rationale.md#check-17))

**The reverse direction is asserted too**, the same call checks 8 and 11 already made for their own declared-vs-observed pairs: an agent carrying the rule but not `Task` declares a dispatch authority the harness would refuse, which is stale and misleading. **Its vacuity guard is check 11's shape**: no agent under `PLUGIN_RELS` carrying `Task` means the frontmatter scan stopped matching, not a tree with nothing left to dispatch, so it fails.

### Check 18

**Check 18 gates the one claim a changelog makes about itself**, enforcing `CLAUDE.md` § Hard constraints' dating rule for `— Unreleased` sections, and it is the only check in `check-docs.sh` that is off by default: `ASSERT_PUBLISHED=1` — which `.github/workflows/validate-catalog.yml` sets on a push to the default branch and nowhere else — is what arms it. **Off a publishing ref the same section is correct authoring state**, which is why the gate is conditional rather than universal and why its selftest carries a red case and a green twin over the *identical* mutation. ([why](../../docs/maintainers/rationale.md#check-18))

**What it deliberately does not match**: the bare Keep-a-Changelog `## [Unreleased]` form, whose one instance is a labelled pre-split historical section — matching it would fire on correct content and nothing else; it is not widened to that form. Its scope is every `plugins/*/CHANGELOG.md` rather than `PLUGIN_RELS`, because every plugin in the catalog publishes from the same ref.

### Check 19

**Check 19 gates the edition's own denylist**, and it is the one check whose subject is edition config rather than body: `EDITION_FORBIDDEN_B64`, in the script's config block, is base64 of one extended regex naming what this edition must never print — in this edition, the organisation the internal edition is written inside and that organisation's internal repositories. It cannot be body, as check 14's list is, because the script body is byte-identical across three editions and the internal one legitimately names exactly what this one forbids; so that edition sets the variable **empty**, and an empty value passes without opening a file. Every edition must still *define* it, empty where nothing is forbidden, because `set -u` aborts on a missing name. It is encoded, never in clear text, for check 14's reason ([why](../../docs/maintainers/rationale.md#check-14)), and it reads every text file under the root outside `.git` **except files named `CHANGELOG.md`**, the only exemption, because history keeps what it shipped with. At the work tree's top level it reads `git ls-files -co --exclude-standard` — an untracked page is read, an ignored `.worktrees/` copy is not — and elsewhere walks the directory. ([why](../../docs/maintainers/rationale.md#check-19))

### Check 20

**Check 20 gates the untrusted-content guard**: every agent in `GUARD_PLUGIN_RELS` — the docs-gated plugins plus `prose-style` — carries `workflows-core`'s `references/untrusted-content.md` block byte for byte, every `Task`-granted agent its pass-on sentence with its sanctioned child, every dispatching command its relay sentence as its own paragraph, word for word, each also in reverse; a listed plugin that does not exist, or a plugin that ships agents without being listed, fails too. ([why](../../docs/maintainers/rationale.md#check-20))

### Check 21

**Check 21 gates install-time code**: every install command in `ITC_PLUGIN_REL`'s three install references, two agents and two commands — each code span and each command of a chained line on its own, prose included — carries `--ignore-scripts` (yarn berry `--mode=skip-build`) if it is npm, pnpm or yarn, and `--only-binary=:all:` (a pipenv lock too), never `:all:` for no-binary, if it is pip or pipenv; none at all fails as vacuous.

## `scripts/validate-catalog.py`

Besides the catalog, it gates the instruction tiers. **Sizes**, as Python `len` of the decoded file: `CLAUDE.md` fails above 40,000 characters and warns above 36,000; a `.claude/rules/*.md` file warns above 20,000 and is then split with narrower `paths:` globs, or its evidence moved to the rationale. **Paths**: every rules file must carry frontmatter with a top-level `paths:` block list (without one it loads every session), and every glob must match at least one *file* outside `.git`, worktrees, fixtures, `node_modules`, `.superpowers` and `.claude/rules/`. Globs are matched by pathlib, which has no brace expansion, so a `{a,b}` glob is reported dead: write each alternative as its own entry.

## Mermaid gate (`scripts/mermaid/check-mermaid.mjs`)

The gate finds diagrams with a real CommonMark lexer (`marked`) and parses each with mermaid's own parser, both pinned by exact version and a committed lockfile, over tracked files only — which is what GitHub renders, and which leaves out every worktree copy under the ignored `.worktrees/` — and excluding its own fixture tree, `scripts/fixtures/mermaid/`, whose green cases are skipped as well as the red ones broken on purpose. Do not replace the lexer with a regex: the selftest runs it over a fixture for each of the four constructs a hand-rolled fence scanner got wrong, so an extractor that misses them again fails it. It never runs the old scanner. ([why](../../docs/maintainers/rationale.md#mermaid-gate))

A failure names the **source-file line**, found by content — the context mermaid prints around a failure, located in the diagram — never by replaying mermaid's own rewrites of the text. Where that context matches no single place, the gate names the fence line and says why; it never guesses. An unclosed fence is not rejected for being unclosed — CommonMark runs it to the end of its container and GitHub draws what it holds — so only its content is judged.

It runs on every push after its `--selftest`, every fixture case of which asserts the block count as well as the exit code, and each red case what the gate reported. Two cases are red/green pairs — `edge-label`, one diagram broken and then fixed, and `closed-by-list-item`, one layout holding a broken diagram and then a valid one; the other green cases each pin a construct the lexer must find or leave alone, and the other red cases, the `red-line-*` location cases among them, have no green twin.

**What it cannot see:** it parses and does not render, so a diagram that parses and then fails at layout passes — a render needs a browser CI does not carry — and a mermaid fence inside a raw HTML block is outside it, as it is outside any CommonMark lexer. Run it locally with `npm ci --prefix scripts/mermaid --ignore-scripts` then `node scripts/mermaid/check-mermaid.mjs --root .`.
