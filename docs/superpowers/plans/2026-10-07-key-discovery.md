# Pull-request discovery by key Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/document` and `/release-notes` run the whole-key commit scan through one tested script, and — where a scanned clone is on GitHub and `gh` is installed and logged in — read merged GitHub pull requests naming a key through the commits they landed.

**Architecture:** `plugins/docs-workflows/scripts/key-discovery.py` (shared byte for byte with the family's other editions) runs the scan, the probe and the optional `gh` search, and prints JSON. A new reference, `plugins/docs-workflows/references/key-discovery.md`, says how both commands run it and use its result; `workflows-core:implementation-format` §4 gains the pull-request layer. `diff-summarizer` is unchanged: a pull request reaches it only as commits.

**Tech Stack:** Python 3 standard library, git, `gh` (optional), markdown command and reference files, `check-docs.sh` (checks 13 and 19 included), `check-id-grammar.sh`, `validate-catalog.py`, the mermaid checker.

**Spec:** `docs/superpowers/specs/2026-10-07-key-discovery-design.md` (this repository).

## Global Constraints

- Work only in this repository's scratchpad clone (`$SCRATCH/clones/aiw`), branch `iv-gu/key-discovery`.
- Never `rm -rf` or `rm -r`; `rm -f` on one file, or Python's `shutil.rmtree`, only.
- Script every prose edit (Python, each replacement asserted to match exactly once); `git diff --summary | grep mode` prints nothing but the new script's `100755`.
- `key-discovery.py` is byte-identical to the family's other editions' copy; no tracker name and no organisation name anywhere in the tree (checks 13 and 19).
- `diff-summarizer`'s input stays `refs[]` alone; the note boundary and the read set stay as `workflows-core:implementation-format` §4 and `references/release-note-types.md` §1 define them.
- CHANGELOG headings read `— Unreleased` on the branch and are dated at merge; take the next free versions after fetching `main`.
- Minors are bugs: every review finding that is a defect is fixed before the push.
- Commit trailer, on every commit:
  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_018c5oyZambF9QfvUmRnwA4d
  ```

## Review Focus

1. **A pull-request commit and the note boundary**: a commit only a pull request found must be dropped by a later `/release-notes` run exactly when a scan commit with its pull request's tokens would be — a reasonable person expects no release note to describe it twice. (Task 4 pins the tokens rule in the command; Task 2 in the reference.)
2. **The probe and a found pull request**: a merge commit a found pull request accounts for must not also be printed as "inspect by hand". (The script's self-test pins it; Task 3 pins that the command prints the script's `probe` rather than running its own.)
3. **`gh` absent, logged out or rate-limited, or the script exiting 2**: the run continues on the record (and the scan, where it ran), and the report says why. (Tasks 2–4.)
4. **An open pull request naming a key**: listed, never read — documenting unmerged work as shipped is the failure a person would notice first. (Task 2's reference; Tasks 3–4's reports.)
5. **The scanned set when `implementation.md` names repositories**: the search covers only those clones' owners, and a pull request in a repository outside the set is listed with `clone: null`. (Task 2.)

---

### Task 1: The shared script and its CI step

**Files:**
- Create: `plugins/docs-workflows/scripts/key-discovery.py` (mode 755)
- Modify: `.github/workflows/validate-catalog.yml` (a step after "Self-test the proposal record")

- [ ] **Step 1: The failing check.** `python3 plugins/docs-workflows/scripts/key-discovery.py --selftest` → `No such file or directory`.
- [ ] **Step 2: Copy it.** Copy the shared script byte for byte from the family edition that merged it first — its merged `main`, in that edition's scratchpad clone under `$SCRATCH/clones/` — then `chmod 755`. `cmp <that copy> plugins/docs-workflows/scripts/key-discovery.py` prints nothing.
- [ ] **Step 3: Verify.** `python3 plugins/docs-workflows/scripts/key-discovery.py --selftest | tail -1` → `selftest: 24/24 passed`; `./scripts/check-docs.sh --root . | tail -2` green — checks 13 and 19 read the script.
- [ ] **Step 4: CI step**, after "Self-test the proposal record":

```yaml
      - name: Self-test the key discovery
        # /document and /release-notes run the whole-key commit scan, its probe and the optional
        # GitHub pull-request search with it. A boundary that matches a longer key, or a search
        # that keeps GitHub's loose hits, hands another key's work to the writer as this one's.
        # Fixtures and a fake gh and ssh are built at run time.
        run: python3 plugins/docs-workflows/scripts/key-discovery.py --selftest
```

- [ ] **Step 5: Commit** — `feat(key-discovery): the whole-key commit scan, its probe and an optional gh pull-request search as one self-tested script`.

---

### Task 2: `references/key-discovery.md`

**Files:**
- Create: `plugins/docs-workflows/references/key-discovery.md`
- Modify: `plugins/docs-workflows/docs/reference/references.md` (an entry, and any count the page states)

- [ ] **Step 1: The failing check.** `test -e plugins/docs-workflows/references/key-discovery.md; echo $?` → `1`.
- [ ] **Step 2: Create the reference** with exactly this content:

````markdown
# Key discovery

How `/document` (keyed mode) and `/release-notes` (with diff grounding on) run the commit scan `workflows-core:implementation-format` §4 defines, and the optional pull-request layer beside it, through one script: `${CLAUDE_PLUGIN_ROOT}/scripts/key-discovery.py`. That §4 stays the authority on what the scan means; this file says how it runs and what the two commands do with what it returns.

## 1. Run it

In Phase 3's diff-source step, once the slug→clone map is built and the tokens are known — §4's tokens for this run's scope, each read off a folder the run resolved or listed — in one shell block:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/key-discovery.py" scan --scope head --probe \
  --key <token> --key <token> … --repo <clone> --repo <clone> …
```

Each token is its own `--key`. Each repository the scan covers — those `implementation.md` names, resolved through the map, or, when it names none, every clone in the map, one per slug by Phase 4's preference (a basename ending `-repo`, then `_repo` or `_fast`, then the alphabetically last) — is its own `--repo`.

Exit 0 prints one JSON document (§2). Exit 2 means it could not run: report its stderr line as the scan's result for every repository, and continue on the record alone.

The script fetches nothing and writes nothing: it reads each clone as it stands.

## 2. What it returns

- `repos[]` — per clone: `path`, the `ref` scanned (`HEAD`), `scanned` (its non-merge commits), `matched`, `github` (`<owner>/<repo>`, or null where the clone is not on github.com), `error`, and `probe` — §4's unanchored probe, by SHA, date and subject, on a clone where `matched` is 0.
- `commits[]` — each non-merge commit on `HEAD` whose message names a token whole (`via: message`), and each commit a found pull request landed whose own message names none (`via: pull-request`): `repo` (the clone), `sha`, `date`, `subject`, `keys` (the tokens), and `prs` — the URLs of the found pull requests that landed it.
- `github` — `status` (`ok`, `partial`, `rate-limited`, `not-installed`, `not-authenticated` or `no-github-clones`), `detail`, the `owners` searched, `queries`, `dropped_loose`, and `prs[]`: `url`, `owner`, `repo`, `number`, `title`, `state` (`MERGED`, `OPEN` or `CLOSED`), `keys`, `clone` (null where no scanned clone holds the repository), `head_ref`, `base_ref`, `head_oid`, `merge_commit`, `cross_repository`, `landed_as` (`merge`, `squash`, `rebase` or null), `landed` and `reason`.

## 3. The scan's result

- `commits[]` with `via: message` are exactly the scan §4 describes.
- `repos[].scanned` and `matched` are the scan's reach.
- `repos[].probe` is §4's report-only probe, less any commit a found pull request accounts for — its merge commit, or a commit it landed — which the run reads or lists under §4 below instead.

## 4. Pull requests — optional

Where a scanned clone's `origin` is on github.com — an SSH host alias resolved as `workflows-core:phase-handoff` §2.6 resolves it — and `gh` is installed and logged in, the script also searches the GitHub pull requests of every owner the scanned clones belong to for the tokens, and keeps one only where its title or body names a token whole: GitHub's own search matches loosely, and `dropped_loose` counts the hits it dropped. Where `gh` is absent or logged out, `github.status` says so and nothing else changes.

- **A merged pull request whose merge commit the clone holds** contributes its `landed` commits — the branch's own commits for a merge commit, the one commit for a squash, the rebased run for a rebase. One the scan already found is that same commit, tagged with the pull request in `prs`. One whose own message names no token comes back `via: pull-request` and joins the scan's commits as a commit only the scan found — reported as unrecorded work like any other, and handed to `diff-summarizer` as `{branch_from: <sha>, branch_to: <sha>^}`. Its tokens, wherever a rule reads a commit's tokens — `/release-notes`' note boundary among them — are the tokens its pull request named (`keys`).
- **Every other found pull request is listed, never read**: an open one, a closed unmerged one, a merged one whose merge commit the clone does not hold (`reason`), and one in a repository no scanned clone holds (`clone: null`) — each by URL and why.

## 5. What the report says

- One `GitHub PR search:` line: `ok — <owners>, <queries> queries, <n> kept, <dropped_loose> loose matches dropped`, or the `status` and its `detail`.
- The merged pull requests read through their landed commits, each by URL with its commits' SHAs.
- The pull requests found but not read, each by URL and why.
- Where the script exited 2, its stderr line.
````

- [ ] **Step 3: Run check-docs to see the inventory fail.** `./scripts/check-docs.sh --root . | tail -5` → FAIL naming `key-discovery.md`.
- [ ] **Step 4: Document it** in `docs/reference/references.md`, in its place:
  `` - `key-discovery.md` — how `/document` (keyed mode) and `/release-notes` run the whole-key commit scan, its probe and the optional GitHub pull-request search through `scripts/key-discovery.py`, and how a merged pull request's landed commits join the scan's result while every other pull request found is listed, never read. ``
  and every count check-docs names.
- [ ] **Step 5: Verify.** `./scripts/check-docs.sh --root . | tail -2` green; `grep -c "never read" plugins/docs-workflows/references/key-discovery.md` ≥ 2; `grep -c "the tokens its pull request named" plugins/docs-workflows/references/key-discovery.md` → `1`.
- [ ] **Step 6: Commit** — `docs(key-discovery): how /document and /release-notes run the scan and use the pull requests it finds`.

---

### Task 3: `/document` runs the scan through the script

**Files:**
- Modify: `plugins/docs-workflows/commands/document.md`

- [ ] **Step 1: The failing check.** `grep -c "key-discovery" plugins/docs-workflows/commands/document.md` → `0`.
- [ ] **Step 2: Edit** (one Python script, each replacement asserted once):
  1. In Phase 3 step 2: `with the \`git log\` command \`workflows-core:implementation-format\` §4 gives: one\n   \`--grep\` per token, each matching only as a whole key.` → `through \`${CLAUDE_PLUGIN_ROOT}/scripts/key-discovery.py\`, run as\n   \`${CLAUDE_PLUGIN_ROOT}/references/key-discovery.md\` §1 says — the \`git log\` \`workflows-core:implementation-format\`\n   §4 gives, one \`--grep\` per token, each matching only as a whole key.`
  2. After the paragraph starting `**Merge and dedupe by SHA.**` insert:
     `**Merged pull requests add commits** (\`${CLAUDE_PLUGIN_ROOT}/references/key-discovery.md\` §4) — only where a scanned clone is on GitHub and \`gh\` is installed and logged in. A merged pull request naming a token contributes the commits it landed: one the scan already found is that commit, tagged with the pull request; one whose own message names no token joins the scan's commits as a commit only the scan found, reported as unrecorded work like any other and tagged with its pull request. Every other pull request found is listed in the report, never read.`
  3. `Say **how many commits it scanned** — the non-merge commits it walked,\n\`git -C <repo> rev-list --no-merges --count HEAD\` — **and how many matched**.` → `Say **how many commits it scanned** — the non-merge commits it walked, the script's \`scanned\`\n(\`git -C <repo> rev-list --no-merges --count HEAD\`) — **and how many matched** (\`matched\`).`
  4. `run §4's report-only unanchored probe**` → `run §4's report-only unanchored probe** (the script's \`probe\` for it, less the commits a found pull request accounts for)`
  5. `repeated inside an element. No URL, no host classification, no \`gh\` requirement.` → `repeated inside an element. No URL and no host classification reach it, and nothing here requires \`gh\`: a pull request reaches \`diff-summarizer\` only as the commits it landed (\`${CLAUDE_PLUGIN_ROOT}/references/key-discovery.md\` §4).`
  6. Phase 4 step 1: `— nothing in this plugin reads a tracker or a pull-request API, so the record of what was implemented is \`implementation.md\` and the \`git log --grep\` scan beside it.` → `— the record of what was implemented is \`implementation.md\` and the commit scan beside it, which a merged GitHub pull request's landed commits join (\`${CLAUDE_PLUGIN_ROOT}/references/key-discovery.md\` §4); an open or unmerged one is listed, never read.`
  7. Final report: after the `### Branch-name probe` section's last bullet (`- Nothing here was read: …`) insert:
     ```markdown

     ### Pull requests
     [`${CLAUDE_PLUGIN_ROOT}/references/key-discovery.md` §5.]
     - GitHub PR search: [ok — <owners>, <queries> queries, <n> kept, <dropped> loose matches dropped | <status> — <detail>]
     - Read through their landed commits: [each merged pull request by URL, with its commits' SHAs | none]
     - Found but not read: [each by URL and why — open, closed, merge commit not in the clone, or a repository no scanned clone holds | none]
     ```
  8. Invariant: `The one forge command this command names is the \`gh pr create\` Phase 8.5 offers the **user** for the run's own pull request, and \`gh\` wraps the API rather than calling it directly` → `The forge commands this command names are key discovery's optional, read-only \`gh search prs\` and \`gh pr view\` (\`${CLAUDE_PLUGIN_ROOT}/references/key-discovery.md\`) and the \`gh pr create\` Phase 8.5 offers the **user** for the run's own pull request, and \`gh\` wraps the API rather than calling it directly`
- [ ] **Step 3: Verify.** `grep -c "key-discovery" plugins/docs-workflows/commands/document.md` ≥ 6; `./scripts/check-docs.sh --root . | tail -2` green.
- [ ] **Step 4: Commit** — `feat(document): the commit scan runs through key-discovery.py, and a merged GitHub pull request naming a key adds the commits it landed`.

---

### Task 4: `/release-notes` runs the scan through the script

**Files:**
- Modify: `plugins/docs-workflows/commands/release-notes.md`

- [ ] **Step 1: The failing check.** `grep -c "key-discovery" plugins/docs-workflows/commands/release-notes.md` → `0`.
- [ ] **Step 2: Edit** (one Python script, each replacement asserted once):
  1. Task 3's edit 1, the same text (Phase 3 step 2).
  2. After the paragraph starting `**Merge and dedupe by SHA.**` insert Task 3's edit 2 text, followed by: ` Their tokens, for the note boundary above and for the read set, are the tokens their pull request named.`
  3. Task 3's edits 3, 4 and 5, the same text.
  4. `Nothing here asks which pull-request statuses to include: Phase 3 builds its refs from \`implementation.md\` and a \`git log --grep\` scan, neither of which carries one, and \`refs[]\` is the only element list \`diff-summarizer\` takes.` → `Nothing here asks which pull-request statuses to include: Phase 3 builds its refs from \`implementation.md\` and the commit scan, and a pull request reaches them only as the commits a merged one landed (\`${CLAUDE_PLUGIN_ROOT}/references/key-discovery.md\` §4); \`refs[]\` is the only element list \`diff-summarizer\` takes.`
  5. Report: after the `   - Branch-name probe: …` line insert `   - Pull requests: <GitHub PR search: ok — <owners>, <queries> queries, <n> kept | <status> — <detail>>; read through their landed commits: <each by URL | none>; found but not read: <each by URL and why | none> — on a run with diff grounding on (\`key-discovery.md\` §5)`
  6. Invariant: `- ZERO external API calls — this run has no forge URL to resolve in the first place: Phase 3 builds \`refs[]\` from \`implementation.md\` and the commit scan, and \`diff-summarizer\` takes a ref's diff with pure local \`git\`.` → `- No external API call but one — key discovery's optional, read-only \`gh search prs\` and \`gh pr view\`, where a scanned clone is on GitHub and \`gh\` is installed and logged in (\`${CLAUDE_PLUGIN_ROOT}/references/key-discovery.md\`); \`gh\` wraps the API. This run has no forge URL to resolve: Phase 3 builds \`refs[]\` from \`implementation.md\` and the commit scan, which a merged pull request's landed commits join, and \`diff-summarizer\` takes a ref's diff with pure local \`git\`.`
- [ ] **Step 3: Verify.** `grep -c "key-discovery" plugins/docs-workflows/commands/release-notes.md` ≥ 6; `grep -c "the tokens their pull request named" plugins/docs-workflows/commands/release-notes.md` → `1`; `./scripts/check-docs.sh --root . | tail -2` green.
- [ ] **Step 4: Commit** — `feat(release-notes): the commit scan runs through key-discovery.py; a merged GitHub pull request's landed commits join it under its tokens`.

---

### Task 5: `implementation-format` §4, the rules and the docs pages

**Files:**
- Modify: `plugins/workflows-core/references/implementation-format.md` (§4, after the paragraph starting `**This is a search for tokens the run already holds, never an extraction.**`)
- Modify: `.claude/rules/docs-workflows.md` (the "Zero direct API calls" bullet), `.claude/rules/release-notes.md` (its "Zero direct API calls" bullet)
- Modify: `plugins/docs-workflows/docs/commands/document.md`, `plugins/docs-workflows/docs/commands/release-notes.md`

- [ ] **Step 1: The failing check.** `grep -c "pull-request layer" plugins/workflows-core/references/implementation-format.md` → `0`.
- [ ] **Step 2: §4** — insert after the paragraph starting `**This is a search for tokens the run already holds, never an extraction.**`:
  `**The pull-request layer, optional.** Where a scanned clone's \`origin\` is on github.com and \`gh\` is installed and logged in, the scan's consumers also search the GitHub pull requests of the scanned clones' owners for the same tokens, keep one only where its title or body names a token whole — by the boundary above — and take a merged one's landed commits into the scan's result: the branch's own commits for a merge commit, the one commit for a squash, the rebased run for a rebase, each read off the clone. A landed commit whose own message names no token joins the scan's commits as one only the scan found, its tokens those its pull request named; an open, unmerged or out-of-clone pull request is reported, never read. Like the scan, it searches for tokens the run already holds; a pull request's number, branches and merge commit come from \`gh\`'s JSON, never from parsed text. \`docs-workflows\` runs the scan, its probe and this layer through one script (its \`references/key-discovery.md\`).`
- [ ] **Step 3: Rules.** `.claude/rules/docs-workflows.md`: `The one \`gh\` command either names is the \`gh pr create\` \`/document\` Phase 8.5 offers the **user**` → `The \`gh\` commands either names are key discovery's optional, read-only \`gh search prs\` and \`gh pr view\` (\`references/key-discovery.md\` — a merged pull request reaches \`diff-summarizer\` only as the commits it landed) and the \`gh pr create\` \`/document\` Phase 8.5 offers the **user**`. `.claude/rules/release-notes.md`: after `all resolution runs against clones under \`$REPOS_PATH\`` append `; key discovery's optional, read-only \`gh search prs\` and \`gh pr view\` (\`plugins/docs-workflows/references/key-discovery.md\`) are the one forge read, and \`gh\` wraps the API`.
- [ ] **Step 4: Docs pages.** `docs/commands/release-notes.md`: `No phase collects a PR link: a ref carries no URL, no host classification and no \`gh\` requirement.` → `No phase collects a PR link: a ref carries no URL and no host classification, and nothing requires \`gh\` — where it is installed and logged in and a scanned clone is on GitHub, a merged pull request naming a key adds the commits it landed, and every other one found is listed, never read ([key discovery](../reference/references.md)).` `docs/commands/document.md`: beside its description of the commit scan, the same sentence from "where it is installed".
- [ ] **Step 5: Verify.** `./scripts/check-docs.sh --root . | tail -2`, `./scripts/check-id-grammar.sh --root . | tail -1`, `python3 scripts/validate-catalog.py | tail -1`, `node scripts/mermaid/check-mermaid.mjs --root . | tail -1` green; `grep -rn "no \`gh\` requirement" plugins .claude | grep -v CHANGELOG` prints nothing.
- [ ] **Step 6: Commit** — `docs: implementation-format §4's optional pull-request layer; rules and command pages name the gh reads`.

---

### Task 6: Release

**Files:**
- Modify: `plugins/docs-workflows/CHANGELOG.md`, `plugins/workflows-core/CHANGELOG.md`, both `plugin.json` files, `.claude-plugin/marketplace.json`

- [ ] **Step 1: Versions.** `git fetch -q origin`; the next minor above `origin/main`'s docs-workflows and workflows-core versions.
- [ ] **Step 2: CHANGELOGs** — `## <version> — Unreleased` in each: docs-workflows (Added: `key-discovery.py`, `references/key-discovery.md`, the optional GitHub pull-request layer; Changed: the scan, reach and probe run through the script; the "no `gh` requirement" statements), workflows-core (Added: §4's pull-request layer).
- [ ] **Step 3: Bump** both `plugin.json` files and their `marketplace.json` entries.
- [ ] **Step 4: Full gates.** `python3 scripts/validate-catalog.py --selftest && python3 scripts/validate-catalog.py && ./scripts/check-id-grammar.sh --selftest && ./scripts/check-id-grammar.sh --root . && ./scripts/check-docs.sh --selftest && ./scripts/check-docs.sh --root . && node scripts/mermaid/check-mermaid.mjs --root . && python3 plugins/docs-workflows/scripts/key-discovery.py --selftest` — every gate green, `24/24`.
- [ ] **Step 5: Commit** — `release: docs-workflows <v> + workflows-core <v> — pull-request discovery by key`.
- [ ] **Step 6: Whole-branch review** — one Opus reviewer with the spec, this plan and the Review Focus; fix every finding that is a defect, Minor included; re-run Step 4.
- [ ] **Step 7: Merge and push** — fetch, re-take versions if `main` moved, date both headings, merge `--no-ff`, run check-docs with `ASSERT_PUBLISHED=1`, push, CI green, delete the branch locally and on origin.
