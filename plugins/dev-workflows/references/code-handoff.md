# Code-repo handoff — Shared Reference

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

Single source of truth for the step that turns finished work in a **code repository** into a commit on its own branch, pushes that branch, and opens a pull request where the host allows one: the `finish-code-branch` entry point (§2). Consumed by `/implement`, `/vuln`, and `/upgrade` — the three commands that create a branch in a code repo and write into it.

**The principle.** Work that exists only in a working tree is one `git checkout` away from gone, and a command that created the branch it was written on owns getting it committed before the run ends. Committing is local and reversible, so it is not the user's to approve. Pushing and opening a pull request leave the machine, so they are.

**Why this file exists.** `/implement` and `/upgrade` each created a branch, wrote into it, ran their gates, and then ended — leaving every change uncommitted, with nothing but the user's own memory standing between a finished implementation and a stray `git checkout`. `/vuln` did commit and open a pull request, but named no mechanics for either: no capability probe, no fallback for a host without `gh`, no defined base branch. All three are now this file's callers.

**Relationship to the other git references.** Four references, and what separates them is which repository each may write into:

| Reference | Repository | Scope |
|---|---|---|
| `workflows-core:specs-repo-git` | `$SPECS_PATH` | bookkeeping — session artifacts, cost, feedback |
| `workflows-core:phase-handoff` | `$SPECS_PATH` | phase deliverables — idea, PRD, ARD, specification, design, readiness, BRD artifacts |
| **this file** | the **code** repo (under `$REPOS_PATH`, or the working clone) | the code the run just wrote |
| `docs-workflows:finish-and-handoff` | a **docs** repo (the one `/docs-workflows:document` resolved) | a keyed documentation run's edits — squashed, pushed only on opt-in, its pull request drafted rather than opened |

This file never writes into `$SPECS_PATH` or a docs repo, and none of the others ever writes into a code repo; the two that share `$SPECS_PATH` are separated by *which paths* they stage, not by repository (`workflows-core:specs-repo-git` §2.1's bounded bookkeeping set versus the caller's own declared deliverable paths). A single run of this file's callers may execute the first three against different targets, and the outcome lines — `Specs repo:`, `Phase handoff:`, `Code repo:` — are what keep them attributable in its output.

---

## 1. Hard rules

1. **`git -C "<repo>"` always; `cd` never.** The caller may be standing somewhere else entirely — `/implement` on a multi-source run reasons about several repos at once, and a `cd` would corrupt whichever one it left.
2. **Never the default branch.** The commit lands on the run's own branch or it does not land. This entry point never commits to `main` / `master` / `develop`, and never pushes to one.
3. **Never destructive.** No `push --force`, no `push -f`, no `branch -D`, no `merge`, no `rebase`, no `reset`, no `checkout --`, no `commit --amend`, and never delete an `index.lock`. It also never *drops* a stash: a stash the caller pushed at branch time is the user's, and §2.2 carve-out 2 says so.
4. **Never fatal.** Every failure is reported and the run's remaining phases still execute — including the caller's terminal `commit-artifacts` step, which commits a different repository.
5. **The commit is prompt-free; the push and the pull request are not.** This is the same rule as `workflows-core:phase-handoff` §1 rule 7, drawn one step later: there, nothing at all happens without consent because the deliverable is already safe on disk. Here the work is *not* safe until it is committed, and a prompt that can be answered "no" is exactly the failure mode this file was written to remove. So the commit runs unconditionally and §2.4's choice governs only what leaves the machine.

**The one opt-out, and it is typed rather than clicked.** `/implement` and `/upgrade` take `--no-commit`, which skips this entry point entirely and leaves the work in the tree. That does not contradict rule 5: the rule is about a prompt a tired operator clicks past at the end of a long run, not about someone who deliberately asked. A caller running under it says once, in its report, what the choice costs — the work is recoverable only on this machine, and `/document` and `/release-notes` will not find it later (`workflows-core:implementation-format` §4) — and does not argue it twice. `/vuln` has no such flag.

**Where this reference deliberately differs from its siblings.** Both `workflows-core:specs-repo-git` (§1 rule 2) and `workflows-core:phase-handoff` (§1 rule 2) forbid `git add -A` at repository scope: there, the repository holds artifacts belonging to many runs and to the user, so only enumerated paths may be staged. **This entry point stages at repository scope on purpose** (§2.2), because in a code repo the run branched off a verified-clean tree and the whole diff *is* the deliverable — staging an enumerated subset would commit part of an implementation and silently drop the rest, which is the failure this file exists to prevent. The bound is moved rather than dropped: it is the **clean-tree precondition plus §2.2's `pre_existing_dirty` carve-out** that keeps somebody else's work out of the commit, and where that precondition does not hold, §2.2 falls back to staging by enumeration exactly as the siblings do. A reader who "corrects" §2.2 to match the siblings breaks this contract; a reader who carries §2.2's repository-scope staging back into either sibling breaks theirs.

---

## 2. `finish-code-branch` — the entry point

Called once per branch the run finished work on, at the point where **every** in-repo write is done — including the caller's post-implementation maintenance agents, which edit `README.md`, `CHANGELOG.md`, `CLAUDE.md`, and in-repo memory files. A call placed before those agents run leaves their edits outside the commit, which is the one ordering mistake this step can make.

### 2.1 Gate

Resolve the base branch (§2.8) **first** — the gate's last check needs its value. Then require all of:

1. `repo` is set and is an existing directory, and `git -C "<repo>" rev-parse --git-dir` succeeds.
2. `git -C "<repo>" symbolic-ref --quiet --short HEAD` succeeds (HEAD is on a branch, not detached). **`--short` is required**: without it the command prints `refs/heads/<name>`, which can never compare equal to the short name §2.8 resolves, so checks 3 and 4 would both silently pass on every run.
3. That name is **not** the resolved base branch.
4. That name **equals the caller's `branch` input**. `git commit` writes to HEAD while `git push -u origin <branch>` pushes the ref *named* `<branch>`; if the two differ both succeed and the run reports a push that never happened. Mismatch is a gate failure naming both values, never a silent correction.

**Writability is not pre-probed.** Attempt the commit and let a real `Read-only file system` error be the trigger (`workflows-core:read-only-repos` §1's own secondary trigger). That file's `test -w` probe is written for a *scanner*, where it says in as many words that a false positive is benign because the agent just reads at a ref instead. Here the same probe would decide whether finished work is committed at all, and a false positive strands it — and note that a genuinely read-only mount would have failed the caller's Write/Edit tools hours earlier, so nearly every firing of a pre-probe here is a false positive.

A failed gate is reported through §3.1's `NOT committed` line and the run continues. Detached HEAD is worth naming rather than merely reporting: it is the same blocking state `workflows-core:specs-repo-git` §3.3 G0 names, for the same reason — a commit made there is reachable from no ref. Report it; never create a branch to escape it, because the branch this run was supposed to be on is not the one this step gets to choose.

**No `origin` remote is not a gate failure.** §2.8's ladder is unresolvable without one, so checks 3 and 4 fall back to comparing HEAD against the caller's `branch` input alone, the commit proceeds, and §2.5 reports that there was nothing to push. A local-only clone is a legitimate setup and must never cost the user their commit.

### 2.2 What gets staged

**After a §2.12 unit-level commit that did not land, this step stages nothing** — its changes stay uncommitted — and the call goes straight on to §2.4 where the branch carries a commit this run's unit-level calls made, and otherwise ends on §3.1's *Commit rejected* row (§2.12).

**The precondition.** The caller is responsible for establishing, before its first file edit, that the tree held nothing it did not put there — `/implement` at Pre-Phase 3 step 1 and `/upgrade` at Phase 2 prep step 1 do it with an explicit dirty-tree prompt, and `/vuln` does it by capturing the porcelain set at the top of Step 3 and passing it as `pre_existing_dirty` (it never prompts, so on `/vuln` a non-empty set always takes carve-out 1 below rather than the `add -A` path). Where the tree was established clean, everything uncommitted in the repo now **is** this run's work — the same reasoning `docs-workflows:finish-and-handoff` §2 applies to the docs repo — and staging is `git -C "<repo>" add -A`.

Enumerate before staging regardless: `git -C "<repo>" status --porcelain -z --untracked-files=all`. `--untracked-files=all` is required because the default collapses an untracked directory to a single `?? dir/` line, which would hide individual files from carve-out 1's set subtraction below. **`-z` is required for the reason `workflows-core:phase-handoff` §2.3 gives** — without it git wraps any path carrying a space, a `"`, a `\` or a non-ASCII byte in double quotes and octal-escapes the non-ASCII bytes, so carve-out 1 would stage that path in its quoted form and `git add` would match no file; under `-z` each record is NUL-terminated and the path is raw. **The caller's `pre_existing_dirty` capture reads the same form**, and that is not optional either: carve-out 1 subtracts one set from the other, so a quoted recorded path beside a raw current one fails to subtract and sweeps somebody else's uncommitted work into this run's commit — the one thing that carve-out exists to prevent. All three callers capture it with `-z` (`/implement` Pre-Phase 3 step 1, `/upgrade` Phase 2 prep step 1, `/vuln` Step 3).

Three carve-outs:

1. **`pre_existing_dirty` is non-empty.** The precondition does not hold, and `add -A` would sweep somebody else's uncommitted work into this run's commit. Stage by enumeration instead: the current porcelain set **minus** the recorded paths. **A path that was already dirty and that this run also edited is staged**, because the run's edit is inside that file and cannot be separated from what was there before; list those paths in the §3.1 line rather than deciding them silently.

   This is a **rule, not a prompt.** An earlier draft asked the user to choose between enumeration, whole-tree staging, and skipping the commit; that reintroduced exactly the "prompt that can be answered no" §1 rule 5 exists to remove, offered a skip option that contradicts the unconditional commit, and fired once per unit in a loop. The subtraction is the safe answer in every case, so it is taken without asking, and the §3.1 line reports how many pre-existing paths were left alone.

2. **A stash the caller pushed.** Never restored here and never dropped. It stays where it is and §3.1's line names it, because a stash nobody mentions is a stash nobody remembers.

3. **Temp files are already out of reach.** Every caller writes its diffs, claims files, and scan summaries to `mktemp -t …` outside any repo tree specifically so `add -A` cannot pick them up. This step does not re-verify that; a caller that writes a temp file inside the tree breaks this step's staging, which is why the rule sits in the callers.

**A `git add` git refuses** (a held `index.lock`, a full disk) is a unit that did not land too: what §2.3 and §2.12 say of a rejected commit holds for it, save that its changes are in the working tree, perhaps partly staged, rather than staged.

**Nothing staged.** Do **not** emit a line here — §3.1 allows exactly one per call, and this path continues. If the branch carries commits this run made earlier (the §2.12 split form), proceed to §2.4 and report the run's outcome from the pushing rows. If it carries none, the call ends and §3.1's `no changes to commit` row is the line. An `/upgrade` component already at its target version, or a re-run that changed nothing, both land here legitimately.

### 2.3 Commit

**Subject.** Every commit this entry point makes ends with `[<key>]` where the run resolved a key, and carries a `Work-Item: <workitem_key>` trailer where that key's folder has one — `workflows-core:implementation-format` §3, this plugin's own documented convention, binding on all three callers. **This is where the plugin writes that convention rather than merely teaching it.**

Everything the convention leaves open comes from the repository, never from habit: read `git -C "<repo>" log --oneline -20` and match what it shows. A conventional-commits log gets `feat:` / `fix:` / `chore:` matching the type the run's own branch prefix already expresses (`workflows-core:branch-naming` §2.4 lists each command's fallback prefix, but a repo with its own documented convention may have supplied a different one — read what the run resolved, not the fallback table); a log with no discernible convention gets a plain imperative subject. A caller with a full template of its own overrides this paragraph — `/vuln`'s "Git Workflow → Commit message" is the one that exists today — and passes it as `commit_template`.

**A run with no key writes no suffix.** `/implement` in direct mode and `/vuln` on a bare `CVE-ID` both resolve no folder; the subject is the bare imperative and the trailer is absent. Never invent a key to satisfy the convention — the scan in `workflows-core:implementation-format` §4 searches for tokens the run already holds, and a minted one matches nothing.

**Body.** What changed and why — one line per notable item — plus the review verdict where the caller has one, and the test result where the caller ran tests. **Trailers.** `Co-Authored-By: Claude <noreply@anthropic.com>`, plus `Work-Item:` where the folder supplies one; a caller's own template may add more. This diverges from `workflows-core:specs-repo-git` §1 rule 6, which forbids the trailer, and follows `workflows-core:phase-handoff` §1 rule 6 instead, for the same reason: a bookkeeping file is plugin-generated, and code is authored.

**Write the whole message to a file and commit with `-F`:**

    git -C "<repo>" commit -F <msg-path>

`<msg-path>` is a `command mktemp -t` path **outside any repo tree** (§5). This is `workflows-core:phase-handoff` §2.7's rule applied to the commit message, and it is not stylistic: `-m "…"` inside a double-quoted shell string command-substitutes `$(…)` and backticks before git ever sees the text, and `/vuln`'s template interpolates an NVD CVE description — free text, routinely containing shell metacharacters and version expressions — straight into it. `/upgrade` interpolates component names and `/implement` a free-text summary, with the same exposure. `-F` also preserves the multi-line body and trailer that `-m` would mangle.

**Remove `<msg-path>` once the commit has been made** — `command rm -f -- "<msg-path>"`, `command` because the Bash tool's shell carries the user's aliases and an `rm -i` of theirs would ask, be answered no from that shell's empty standard input, and leave the file. Nothing else removes it: it sits under the system's temporary directory, where no later step of the run and no later run looks. A rejected commit keeps its file until the run has recorded the failure, then removes it too: the commit is not retried here, so nothing re-reads the path.

Never `--amend` (§1 rule 3): an amend rewrites a commit that may already be pushed, and this step is reachable more than once per run.

**A rejected commit is a reported failure, never a silent one.** A `pre-commit` / `commit-msg` hook can reject the commit; the changes then stay staged. So does a commit git itself fails to write (a signing failure, an unset author identity), and everything this paragraph and §2.12 say of a rejected commit holds for it, with git's error in place of the hook's output. Do not retry, do not bypass with `--no-verify`, and do not proceed to the next unit as though the commit landed — a later unit's `add -A` would fold this unit's diff into that unit's commit under the wrong message. Record the failure and the hook's output or git's error; in the §2.12 split form the caller reports it in its own per-unit results table, and the terminal call's §3.1 line names the unit that failed to commit where an earlier unit committed, and is otherwise the *Commit rejected* row (§2.12).

### 2.4 The consent choice

Asked **after** the first successful commit, and presented verbatim — order, wording, and the `(Recommended)` marker are not the caller's to change:

    choices: ["Push the branch and open a pull request (Recommended)", "Push the branch only — no pull request", "Neither — the commit stays on this machine"]

There is deliberately no `Cancel`: the commit has already happened, so there is nothing left to cancel, and the third option *is* the decline.

**Asked once per run, then reused** — record it as `code_handoff_choice`. `/vuln` finishes one branch per CVE and `/upgrade` commits once per component; re-asking would turn a single decision into one per unit of work, which is how a prompt becomes something a user clicks through without reading.

**Two triggers re-ask, and only these two.** First, **the `clean_finish` this call carries differing from the one the recorded answer was given under — in either direction.** `true` → `false` because the user authorised pushing reviewed work, not blocked work; `false` → `true` because declining on a blocked first unit and thereby silently withholding nine clean ones is just as wrong, and a rule written over one direction ships exactly that. **A re-ask replaces the record**: the new answer becomes `code_handoff_choice` and is stamped with the flag *it* was given under, which is what every later unit then compares against. Without that the first answer stands for the whole run and every later unit differing from it asks again, which is one per unit — the cost this section's caching exists to avoid, reintroduced by the widening rather than avoided by it. **The comparison is against the flag the *answer* was given under, never against the previous unit's**, which buys a **clustered** batch its saving and nothing more: `false, false, true, true, true` asks twice over five units. A strictly alternating batch does ask once per unit, and that is not a cost being smuggled past — there every unit genuinely is a new question, and the alternatives are pushing blocked work under an answer given for clean work or withholding clean work under an answer given for blocked. Second, a change of `repo`. Re-asking names the trigger so the user knows why they are being asked twice.

### 2.5 Push

`git -C "<repo>" push -u origin <branch>`. Never force.

- **No `origin` remote** → nothing to push; the call ends and §3.1's `no origin remote` row is the line (§2.1 already established this is not a failure).
- **Non-fast-forward rejection** → reported, never resolved by rebasing, resetting, or forcing. The branch is the run's own, so this means somebody else pushed to it; that is a human's call. Server-side rejections (protected-branch pattern, `pre-receive` hook, size or LFS limits) report the same way, through §3.1's `push FAILED (<reason>)` row.
- **A failed push never undoes the commit and never starts a retry loop.** The commit is the durable half and it survives every push failure — which is the whole reason §1 rule 5 puts it first.

### 2.6 Open the pull request

**First, probe for an existing pull request** — a re-run against a branch that already has one is ordinary, not exceptional:

    gh pr list -R "<owner_repo>" --head <branch> --state open --json number,url

One already open ⇒ the push in §2.5 has already updated it. Report it through §3.1's *pushed to existing PR* row — not the rows for a pull request this run opened, which would assert something that did not happen (§2.10) and would leave that row reachable by nothing — and do **not** call `gh pr create`, which would fail on the duplicate and send the run down §3.2 telling the user to open a pull request that exists. This is `workflows-core:phase-handoff` §3.5's primitive, applied here.

A `gh pr create` that exits 0 but prints nothing parseable as a number or URL is **not** treated as a failure — the pull request very likely exists, and falling back to §3.2 would tell the user to open a second one. Report it with the dedicated §3.1 row instead.

Otherwise derive the repository and create it. Run the cheap `gh auth status` pre-check first, purely so a missing login reports as a login problem rather than a raw `gh` error, then supply every argument that would otherwise make `gh` prompt — the plugin must never block on an interactive editor:

    url=$(git -C "<repo>" remote get-url origin)
    host=$(printf '%s' "$url" | sed -E 's#^[a-zA-Z][a-zA-Z0-9+.-]*://##; s#^[^/@]+@##; s#[:/].*$##')
    slug=$(printf '%s' "$url" | sed -E 's#^[a-zA-Z][a-zA-Z0-9+.-]*://##; s#^[^/@]+@##; s#^[^/:]+(:[0-9]+)?[/:]##; s#/+$##; s#\.git$##')
    case "$host" in github.com) owner_repo="$slug" ;; *) owner_repo="$host/$slug" ;; esac

    gh pr create -R "$owner_repo" --base <base> --head <branch> \
                 --title "<title>" --body-file "<body-path>" [--draft]

**The host is kept, not stripped.** `gh -R` accepts `[HOST/]OWNER/REPO`, and `gh auth status` succeeds whenever the user is authenticated to *any* host — so a bare `OWNER/REPO` derived from a GitHub Enterprise remote resolves against **github.com**, silently targeting an unrelated public repository if one happens to sit at that path. Only `github.com` may drop the host. Validate the slug against `^[^/]+/[^/]+$` before calling `gh`; anything else (a Bitbucket `scm/proj/repo`, a nested GitLab group) is not a `gh` target — skip to §3.2.

The `sed` expressions strip, in order: a scheme (`ssh://`, `https://`), a `user@`, and a host with an optional `:port` terminated by `/` **or** `:` (the scp-like `git@host:Org/repo` form uses a colon), then a trailing slash and the `.git` suffix. Verified against `git@host:Org/repo.git`, `https://host/Org/repo(.git)`, `https://user@host/Org/repo.git`, `ssh://git@host/Org/repo.git`, `ssh://git@host:7999/proj/repo.git`, `git@ghe.corp:Team/repo.git`, and a nested `group/sub/repo`. A two-expression form matching only `git@host:` or `https://host/` passes an `ssh://…` URL through **unchanged** — do not simplify it back.

**Capability probe, not host classification.** Try the call; on any failure fall back to §3.2. Push authority and pull-request authority are independent — push runs over SSH with a per-repo key, `gh` runs over the API with a token, and the same account can have write access to one repository and read access to another. No hostname test can detect that mismatch, which is why `docs-workflows:finish-and-handoff` §4's host classification is right for choosing *instructions* and insufficient here.

`gh` wraps the API rather than calling it over HTTPS, which is what the zero-direct-API rule permits.

### 2.7 The title and the body file

Title: the commit subject of §2.3 — on a §2.12 terminal call, which makes no commit of its own, the caller's `title`, written the way §2.3 writes a subject.

Body: **written to a file** — `<body-path>`, a `command mktemp -t` path outside any repo tree — never passed inline, which would break on newlines and quoting. The same file is what §3.2 names when `gh` is unavailable, so the user pastes the identical body — banner included — into the web UI.

**What the body holds.** Four sections, in this order, rendered from `body_facts`, with no preamble: on a `clean_finish: false` run §2.9's banner is the body's **first line**, and otherwise its first heading is — save where a template resolves (below), which keeps its own opening first, under the banner where there is one.

1. `## Summary` — what changed, one line per notable item, and the files changed.
2. `## Evidence` — a **Before** and an **After**, each taken only from what the run observed: the caller's baseline against its verification, and on a bug fix the failing reproduction against the passing test. Where the run has no before or no after — tests the operator skipped, a verification that could not run — the section says which, and why. "Tests pass" alone is a claim, not a before and an after.
3. `## Merge danger` — the **door**, with one line of why, and the **blast radius**, with one line of what breaking would look like:
   - **Door: one-way** where the change includes a step that reverting its commit does not undo — a migration that drops or rewrites data, removing a public contract that consumers outside the repository use, writing persisted data in a new format, or anything that ships outward (sends, publishes, deletes); **two-way** otherwise. **Where the run cannot tell, one-way**, with the reason: the door is the run grading its own change, and the uncertain case is the one a reader should slow down on.
   - **Blast radius** — a short phrase naming what breaks if the change is wrong: an API's consumers, a data store, a screen, the build.
4. `## Review` — the run's classification; the reviewer verdict and triage summary where the caller has them, or, where no review ran, that none did and why; and every review finding the caller did not apply, with its severity.

**The repository's own template wins.** Resolve it against a fixed set of paths, never by searching for one: list the committed tree's candidates with `git -C "<repo>" ls-tree -r -z --full-tree --name-only HEAD | tr '\0' '\n' | grep -i -E '^(\.github/|docs/)?pull_request_template(\.md|/[^/]+\.md)$|^\.gitlab/merge_request_templates/default\.md$'` — `-z` because, without it, git quotes a name holding a non-ASCII byte and the anchor never matches it, and `--full-tree` so the listing is the whole tree wherever `<repo>` points; no output is no template — and stop at the first rung below that a listed path matches, comparing without regard to case —

1. `.github/pull_request_template.md`, then `pull_request_template.md` at the root, then `docs/pull_request_template.md`;
2. the first of `.github/PULL_REQUEST_TEMPLATE/`, `PULL_REQUEST_TEMPLATE/` and `docs/PULL_REQUEST_TEMPLATE/` that holds a `.md` file directly: where it holds exactly one, that file; where it holds several, none — a directory of templates names no default, so the body is written as above and its last line says the repository offers several templates, naming the directory;
3. `.gitlab/merge_request_templates/Default.md`.

Where a template resolves, read it with `git -C "<repo>" show HEAD:<path>`, `<path>` spelled exactly as the listing printed it (git looks a path up case-sensitively) — the committed file, never a working-tree copy that may hold somebody else's edit — and the body **is that template, filled**: its headings kept in their order, and each section answered from `body_facts`; a section the run has nothing for says so and why, and never keeps the template's placeholder text; a checkbox ticked only where the run can show what it claims, and never deleted; each of the four sections above placed in the template section that asks for it, and every one no template section asks for appended after the template, in the order above. A template with no headings is one section, answered in place. An HTML comment (`<!-- … -->`) in a template is its note to whoever fills it: follow it, then remove it with the placeholder text. The banner stays the first line. **The template wins because the body replaces it otherwise**: `gh pr create --body-file` replaces what the web UI would have prefilled, and §3.2 has the user paste the body in its place, so a body in this section's own shape would delete the template on either path.

**Remove `<body-path>` once `gh pr create` has read it** — `command rm -f -- "<body-path>"`, as §2.3 removes the message file and for the same reason. **This file is this reference's one exception to that rule**, and §3.2 is why: where the fallback text names it, the user opens the pull request by hand afterwards, from that path, so the run leaves it and the report names it. It is kept on that path alone; where the run opened the pull request, or never reached §2.6 at all, nothing names the file again and it goes.

### 2.8 Resolving the base branch

In order, stopping at the first that succeeds — never assume `main`:

1. `git -C "<repo>" symbolic-ref --quiet --short refs/remotes/origin/HEAD` → strip the leading `origin/`; what remains is the name. `--quiet` is required, or a clone whose `origin/HEAD` is unset leaks `fatal: ref refs/remotes/origin/HEAD is not a symbolic ref` into the run's output. **The rung succeeds only where `git -C "<repo>" rev-parse --verify --quiet origin/<name> >/dev/null` also succeeds for that name**; otherwise go on to rung 2. A remote that renames its default branch — `master` to `main` — and a clone that then fetches with `--prune` leave `origin/HEAD` naming the branch the remote deleted: the command still prints `origin/master` and exits 0, and taking it would hand `gh pr create` a `--base` the remote no longer has, where rung 2 finds `main`.
2. For `main`, then `master`, then `develop`: `git -C "<repo>" rev-parse --verify --quiet origin/<name> >/dev/null` — and on success take **`<name>`**, never the command's output.

**The `main`/`master`/`develop` probes are existence tests, not name sources.** `rev-parse` prints a 40-character SHA, so a caller that uses its stdout gets a SHA: `git switch <sha>` detaches HEAD — the state §2.1 treats as blocking — and `gh pr create --base <sha>` is rejected outright. Redirect the output and use the literal name you probed.

An exhausted ladder (or no `origin`) means no pull request can be opened: report it through §3.1 and skip §2.6.

### 2.9 A run that did not end clean

`clean_finish: false` when the caller reports any of:

- an Opus review that stayed blocked — a `BLOCKER` survived its re-review's triage, or the user kept its verdict at a settle prompt (or, in `/vuln` and `/upgrade`, cancelled there), or, in `/implement`, a surviving `BLOCKER` whose fix lies in another code repository;
- test regressions the user chose to keep rather than fix or revert;
- a unit of work the caller marked `BLOCKED` (a `/vuln` CVE, an `/upgrade` component) **that reached the repository** — a unit that stopped before writing anything (an unreadable input) changed nothing and must not flip the flag for the rest of the batch. **A failed baseline was the other member of that set and no longer is**: `/vuln`'s `BASELINE_FAILED` stopped a CVE before its branch existed, and `dev-workflows` 4.2.0 retired it — a capture that cannot run is now the operator's question, and whichever way they answer, no unit stops there;
- a **New failure** the verification reported — a test failing now that was in neither baseline list, which no `test-baseliner` `Status` carries, so the unit reaches the caller green (`/vuln` `SUCCESS`, `/upgrade` `OK`) with a red suite behind it. The caller finds it by the `NEW-FAILURE: ` prefix its agent marks in `notes`, never by reading the `Status`. **It is the mildest entry here** — the baseline never recorded those tests, so nothing says this change caused them — and it still belongs, because what this flag asks is whether the diff is safe to merge unexamined and a failing suite answers no. **It is reachable on an ordinary `PARTIAL` baseline**, which is why it is not folded into the bullet below: there the suites the baseline covered are green and this one's failures come from a suite it did not cover;
- a verification the caller **attempted and could not complete**, and proceeded on anyway — `/implement`'s accepted unverified run, `/vuln`'s and `/upgrade`'s `TESTS_NOT_RUN`. Kept regressions at least name what failed; here nothing is known about the tests in either direction, which is the stronger case for the banner, not a weaker one. Two states that also leave the tests unknown are **not** this, and both are excluded deliberately rather than by omission: a comparison that was merely *incomplete* — a `test-baseliner` `PARTIAL`, where every suite the baseline covered is green, **the qualifier being load-bearing since the bullet above fires on a `PARTIAL` whose uncovered suite runs red here** — and a verification the operator **declined before the first edit** — `/implement`'s `test_decision: skip` where the operator answered *"Skip tests for this run"* at Pre-Phase 3.5, while a baseline could still have been taken (`/vuln`'s `SKIPPED_BY_USER` is the same decision one step earlier — it never invokes the fixer, so nothing of that CVE is on the tree and Step 3.9's tree test skips this entry point outright). A typed decision taken up front is the `--no-commit` precedent of §1's opt-out paragraph — honoured without penalty — where this bullet is about a gate the run ran into. Neither flips the flag.

  **That second exclusion is the operator's answer, never the bare token.** `test_decision: skip` has a *second* provenance: `/implement` records it **itself** after two `command_hint` attempts that also failed to capture (Pre-Phase 3.5's *"Ask at most twice in a run; after that record `test_decision: skip`"*). Nothing was typed and nothing was declined there — the operator asked twice for a working command and the run gave up — so that state matches this bullet's own predicate word for word and **does** flip the flag. A caller must therefore pass which provenance it holds and never the token alone; `/implement` does, in its Phase 4.6 `clean_finish` list. The distinction is worth stating because the token is what a reader reaches for: the exclusion above was written as "a typed decision", and the run can type nothing and record the same value.

- a §2.12 unit-level commit that did not land — the pull request carries fewer units than the run was asked for, and that unit's changes sit uncommitted in the local repository, staged or in the working tree.

**The commit runs exactly as it would on a clean finish, and the push is still *offered* under §2.4's choice.** Unreviewed work that exists is recoverable; work that was never committed is not, and a failed gate is the case where losing it hurts most. *Offered* rather than guaranteed, because this flag is §2.4's own first re-ask trigger: where it differs from the flag the recorded answer was given under, that choice is put again and can be answered *"Neither"*. What the flag itself changes is only the pull request:

- opened with `--draft`, so it cannot be merged by reflex;
- the body file's **first line** is `> ⚠ DO NOT MERGE — <blocking facts>.`, listing **every** blocking fact when a batch has more than one, semicolon-separated. One slot, all the facts.
- where §2.6 fell back, §3.2 carries the same banner as its own first line **and** appends `--draft` to the copy-paste `gh` command it offers, and its web-UI wording says to open the pull request as a draft. A fallback that quietly produces a mergeable pull request for blocked work defeats this whole section.

### 2.10 Failure discipline

Never fatal (§1 rule 4). Every failure is reported, and no report may imply a step succeeded that did not. "Committed", "pushed", and "pull request opened" are three separate claims, and a run that committed but could not push says both of the first two.

### 2.11 Caller-supplied inputs

| Input | Meaning |
|---|---|
| `repo` | absolute path of the code repository's top level — where the caller holds a path inside it, `git -C <path> rev-parse --show-toplevel` of that path: §2.2's porcelain paths are relative to the top level, and `git add` run from a subdirectory reads them against the wrong root |
| `branch` | the branch the caller created or adopted — §2.1 check 4 verifies HEAD is actually on it |
| `pre_existing_dirty` | porcelain paths dirty before the run's first edit, or `null` |
| `stash_ref` | the stash the caller pushed at branch time, or `null` |
| `key` | the key of the unit the run implements (`workflows-core:implementation-format` §3) — the resolved folder's (`workflows-core:addressing` §4), save where `/implement` chose an Epic under a PRD address and passes that Epic's — or `null` |
| `workitem_key` | that unit's folder's `workitem_key`, or `null` |
| `title` | the commit subject and pull-request title — on a §2.12 terminal call, which commits nothing, the pull-request title alone (§2.7) |
| `body_facts` | what §2.7 renders into the body file's four sections: what changed and the files changed; the before and the after the run observed; the facts its door and blast-radius calls rest on; and the review — the classification, the verdict and triage, and every finding not applied |
| `clean_finish` | `true` / `false` per §2.9 |
| `commit_template` | the caller's own message template, or `null` |

### 2.12 Splitting the call across a loop

A caller whose units **share a single branch** — `/upgrade`'s per-component loop — may run **§2.1–§2.3** at the end of each unit and the **full entry point once** at the end of the run. The unit-level call commits and stops; the terminal call finds nothing left to stage, takes §2.2's `nothing staged` path, and continues into §2.4 and §2.5–§2.6 because the branch carries commits to push.

**§2.1 is inside the split, not outside it.** An earlier draft sanctioned "§2.2–§2.3 alone", which ran every per-unit commit with no gate: a caller whose branch creation had failed would commit its whole batch onto the default branch, one commit per unit, and only discover it at the terminal call — which would then report `NOT committed` over work that was very much committed, in the wrong place. Run the gate every time; it is four cheap reads.

The split is what makes per-unit committing worth having: a batch that dies on component three still has one and two committed, each with its own message, on a branch that bisects. Both halves are required — a caller that runs the unit-level half and never reaches the terminal call has committed the work and left it on the machine, which is only half the fix.

**Where each unit gets its own branch there is no split.** `/vuln` is that case: a unit-level call that only committed would leave that CVE's branch unpushed forever, since the terminal call can push only the branch it is standing on. Each CVE runs the **full** entry point, and §2.4's once-per-run caching keeps that from asking N times.

**A unit-level commit that does not land ends the split**, whether a hook rejected it or git failed to stage or write it (§2.2, §2.3). Its changes stay behind uncommitted, and §2.3 forbids carrying on as though it landed, so the caller works no later unit — a later unit's §2.2 would fold the rejected changes into that unit's commit — and goes to its terminal call, which then stages and commits nothing: it runs §2.1, then, where the branch carries a commit this run's unit-level calls made, §2.4 onward for those commits, its §3.1 line carrying the *A unit commit rejected* append; the caller sets `clean_finish: false` (§2.9). Where the branch carries no such commit, its line is the *Commit rejected* row.

**A unit-level call emits no §3.1 line** (§3.1 allows one per *full* call), but it is not silent: it returns its outcome — commit sha, `nothing staged`, or a commit failure with its reason — to the caller, which records it in its own per-unit results table. §2.10's "every failure is reported" is satisfied there, not by a `Code repo:` line.

---

## 3. Reporting

### 3.1 Outcome line

Exactly one per **full** call, prefixed `Code repo:`. A caller that finishes several branches in one run (a `/vuln` CVE loop) emits one line per branch. A §2.12 unit-level call emits none.

`<what>` below is `<sha7> on <branch>` for a call that committed, and `<n> commit(s) on <branch>` for a terminal call whose own staging was empty, or skipped after a unit that did not land (§2.12), but whose branch carries commits from unit-level calls; `<who>` is `a <hook> hook`, or `git` where git itself failed to stage or write it (§2.2, §2.3); `<where>` is `staged`, or `in the working tree` where §2.2's `git add` failed; and `<unit>` is the unit's name on a §2.12 split, `the commit` otherwise.

| Case | Line |
|---|---|
| Pushed, PR opened | `Code repo: <what> — pushed, PR #<num> open (<url>).` |
| Pushed, draft PR | `Code repo: <what> — pushed, DRAFT PR #<num> open (<url>) — <blocking facts>.` |
| Pushed, PR already existed | `Code repo: <what> — pushed to existing PR #<num> (<url>).` |
| Pushed, no PR requested | `Code repo: <what> — pushed. No pull request opened (not requested).` |
| Pushed, PR not opened | `Code repo: <what> — pushed, PR NOT opened (<reason>). Open it manually.` |
| Pushed, PR opened but unparseable | `Code repo: <what> — pushed, pull request opened but `gh` returned no usable number or URL; check the branch on the host.` |
| Pushed, PR not opened, run blocked | `Code repo: <what> — pushed, PR NOT opened (<reason>) — <blocking facts>. Open it manually as a DRAFT.` |
| Push failed | `Code repo: <what> — push FAILED (<reason>). The work IS committed locally.` |
| Push declined | `Code repo: <what> — not pushed at your request.` |
| No origin remote | `Code repo: <what> — no origin remote, nothing to push.` |
| Nothing to commit, nothing to push | `Code repo: no changes to commit on <branch>.` |
| Commit rejected | `Code repo: NOT committed — <unit> rejected by <who> (<reason>). The changes are <where>.` |
| Gate failed | `Code repo: NOT committed — <reason>. Your changes are still in the working tree.` |
| Skipped under `--no-commit` | `Code repo: not committed — --no-commit. Your changes are in the working tree on <branch>.` |
| A unit commit rejected (§2.12) | append `; <unit> NOT committed — rejected by <who> (<reason>); its changes are <where>.` |
| Pre-existing dirty paths skipped | append `; <n> pre-existing dirty path(s) were left uncommitted.` |
| A stash is outstanding | append `; a stash from this run's branch step is still on the stack (<stash_ref>).` |

The `push FAILED` line states the surviving commit explicitly. A user reading "FAILED" needs to know in the same sentence that their work is not gone.

### 3.2 The no-`gh` fallback text

On a `clean_finish: false` run the banner is the **first** line, above everything else, and it is also the first line of `<body-path>` (§2.7) so it survives the paste:

    > ⚠ DO NOT MERGE — <blocking facts>.

    The branch is pushed but no pull request was opened (<reason>).
    Open one from <branch> into <base> in the web UI — as a DRAFT if the banner above is present.
    Title: <title>
    The body is at <body-path> — paste it in place of any description the web UI prefills.

For a GitHub remote where `gh` is merely absent, append the command the user may run once it is installed — carrying `--draft` whenever the banner is present, or the fallback silently produces the mergeable pull request §2.9 exists to prevent:

    gh pr create -R <OWNER_REPO> --base <base> --head <branch> \
      --title "<title>" --body-file <body-path> [--draft]

---

## 4. Caller contract

Four obligations. Omitting any one is a defect, not a style choice.

1. **Call it after the last in-repo write, not before.** Post-implementation maintenance edits files inside the repo; a call placed ahead of them commits a partial run.
2. **Record `pre_existing_dirty` and `stash_ref` at branch time.** A caller that does not cannot honour §2.2's first two carve-outs, and will either sweep up somebody else's work or forget a stash.
3. **Emit §3.1's line exactly once per *full* call**, in the run's own report. A §2.12 unit-level call emits none — it returns its outcome to the caller instead (§2.12), which records it in that command's own results table.
4. **Never restate this reference's rules** — cite the section number. A rule copied into a command is a rule that goes stale.

## 5. What this entry point never does

- Never touches `$SPECS_PATH` — that repository belongs to `workflows-core:specs-repo-git` (bookkeeping) and `workflows-core:phase-handoff` (deliverables) — and never touches a docs repo, which belongs to `docs-workflows:finish-and-handoff`. `$DOCS_PATH` is a read-only grounding base and is nobody's to commit.
- Never merges a pull request, and never approves one.
- Never calls a REST API over HTTPS. `git push` is git-protocol; `gh` wraps the API (§2.6).
- Never writes a file into the repository it is committing. Everything it needs — the pull-request body included — is written outside the tree.
