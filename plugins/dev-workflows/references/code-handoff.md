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
3. **Never destructive.** No `push --force`, no `push -f`, no `branch -D`, no `merge`, no `rebase`, no `reset`, no `checkout --`, no `commit --amend`, and never delete an `index.lock`. The index-only `restore --staged` and `rm --cached` that §2.2 and §2.3 run are not a `reset`: they rewrite only index entries the run itself made or this call just committed, move no ref and touch no working-tree file. This entry point also never *drops* a stash: a stash the caller pushed at branch time is the user's, and §2.2 carve-out 2 says so.
4. **Never fatal.** Every failure is reported and the run's remaining phases still execute — including the caller's terminal `commit-artifacts` step, which commits a different repository.
5. **The commit is prompt-free; the push and the pull request are not.** This is the same rule as `workflows-core:phase-handoff` §1 rule 7, drawn one step later: there, nothing at all happens without consent because the deliverable is already safe on disk. Here the work is *not* safe until it is committed, and a prompt that can be answered "no" is exactly the failure mode this file was written to remove. So the commit runs unconditionally and §2.4's choice governs only what leaves the machine. **One prompt can come before it**: §2.2's secret scan, on a possible secret it cannot dismiss. That is the one thing a commit makes worse rather than safer — a secret committed is in the history, and taking it out again needs the rewrite rule 3 forbids — and the prompt fires only on a hit, so it does not become a question a user clicks through.

**The one opt-out, and it is typed rather than clicked.** `/implement` and `/upgrade` take `--no-commit`, which skips this entry point entirely and leaves the work in the tree. That does not contradict rule 5: the rule is about a prompt a tired operator clicks past at the end of a long run, not about someone who deliberately asked. A caller running under it says once, in its report, what the choice costs — the work is recoverable only on this machine, and `/document` and `/release-notes` will not find it later (`workflows-core:implementation-format` §4) — and does not argue it twice. `/vuln` has no such flag.

**Where this reference deliberately differs from its siblings.** Both `workflows-core:specs-repo-git` (§1 rule 2) and `workflows-core:phase-handoff` (§1 rule 2) forbid `git add -A` at repository scope: there, the repository holds artifacts belonging to many runs and to the user, so only enumerated paths may be staged. **This entry point stages at repository scope on purpose** (§2.2), because in a code repo the run branched off a verified-clean tree and the whole diff *is* the deliverable — staging an enumerated subset would commit part of an implementation and silently drop the rest, which is the failure this file exists to prevent. The bound is moved rather than dropped: it is the **clean-tree precondition plus §2.2's `pre_existing_dirty` carve-out** that keeps somebody else's work out of the commit — save a file whose content changed during the run, which §2.2 commits whole and names — and where that precondition does not hold, §2.2 falls back to enumeration, as the siblings do, but commits the enumerated paths as pathspecs instead of staging them: an index commit would carry whatever else the index holds, and the dirty tree that sent the run there may include somebody else's staged change (§2.2 carve-out 1). A reader who "corrects" §2.2 to match the siblings breaks this contract; a reader who carries §2.2's repository-scope staging back into either sibling breaks theirs.

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

Enumerate before staging regardless: `git -C "<repo>" status --porcelain -z --untracked-files=all`. `--untracked-files=all` is required because the default collapses an untracked directory to a single `?? dir/` line, which would hide individual files from carve-out 1's set subtraction below. **`-z` is required for the reason `workflows-core:phase-handoff` §2.3 gives** — without it git wraps any path carrying a space, a `"`, a `\` or a non-ASCII byte in double quotes and octal-escapes the non-ASCII bytes, so carve-out 1 would commit that path in its quoted form and match no file; under `-z` each record is NUL-terminated and the path is raw. **The caller's `pre_existing_dirty` capture reads the same form**, and that is not optional either: carve-out 1 subtracts one set from the other, so a quoted recorded path beside a raw current one fails to subtract and sweeps somebody else's uncommitted work in a file the run never changed into this run's commit — the one thing that carve-out exists to prevent. All three callers capture it with `-z` (`/implement` Pre-Phase 3 step 1, `/upgrade` Phase 2 prep step 1, `/vuln` Step 3).

**Each recorded path carries a fingerprint**, which is how carve-out 1 tells a path whose content changed during the run from one left as it was: for a symlink (`test -L "<repo>/<path>"`), the hash of its link text, `readlink -n -- "<repo>/<path>" | git -C "<repo>" hash-object --stdin`, since `hash-object` given the path reads the file the link points at; for a regular file, `git -C "<repo>" hash-object --no-filters -- <path>`; and `-` for anything else, a deleted path or a directory such as a nested repository included. One path per call, because a `hash-object` call naming several fails whole on the first it cannot read. Carve-out 1 takes each fingerprint again the same way at commit time, and a recorded path that carries no fingerprint counts as unchanged. **A changed fingerprint shows that the content changed, not who changed it**: an edit somebody else makes in the tree during the run reads the same as one the run made. A change of mode alone, or of a submodule's checked-out commit, is not seen at all, so such a path counts as unchanged.

**The run set** is what changed during this run: the current porcelain set, less every recorded path whose fingerprint is unchanged, and less each **no-change record** — a ` D` or `AD` record for a path `HEAD` does not hold (`git -C "<repo>" cat-file -e HEAD:<path>` fails), which is an intent-to-add entry for a file since removed, or a new file staged and then deleted. It also leaves out every recorded path whose captured record had `D` in its first column — a deletion staged in the index — whatever its fingerprint: a pathspec commit takes the path's work-tree state, so committing it would undo that deletion rather than carry it, and §3.1's *A staged deletion kept* append names it where its content changed during the run. On a run that recorded nothing it is the whole porcelain set less the no-change records. Take each record whole: a rename or copy record (`R` or `C` in either column) carries two NUL-terminated paths, the new one then the original, and both are paths of the set. Subtract path by path, never record by record, so a rename record pairing somebody else's new file with a path the run deleted keeps the run's deletion in the set — save where both halves of a rename record were recorded, a rename the user had made: those two go together, subtracted where neither fingerprint changed, and kept, the rename committed whole, where either did. A copy record (`C`) is subtracted path by path like any other, since its source is no part of the copy. Carve-out 1 commits this set; `/implement` reads it for Phase 3A step 5's trigger count, Phase 4's diff capture and the Phase 5 report's file list, and `/vuln` for its tree check between CVEs and its hand-off test.

**A recorded path that a commit of this run has carried is retired**: the caller drops it from `pre_existing_dirty` for every later call of the run (a later §2.12 unit, `/vuln`'s next CVE), since its content is committed state from then on and any later change to it is the run's own.

Three carve-outs:

1. **`pre_existing_dirty` is non-empty.** The precondition does not hold, and `add -A` would sweep somebody else's uncommitted work into this run's commit. Commit the run set by enumeration instead, as pathspecs (§2.3's `-- <paths>` form), never staged into the index first: an index commit would also carry whatever else the index holds, somebody else's staged change included, and a per-path `git add` of a path already removed from the index (a `git rm`, or a `git mv`'s original) exits 128. Drop each no-change record that is not a recorded path — the run's own — from the index, `git -C "<repo>" rm --cached -q -- ':(literal)<path>'`, so a staged copy the run left behind does not outlive it; a recorded one is the user's, and stays as they left it. A new file in the set is made known to git first, `git -C "<repo>" add -N -- ':(literal)<path>'`. `rm --cached`, `add -N`, §2.3's commit and its `restore --staged` name each path with `:(literal)`, since a porcelain path can begin with `:`, which git otherwise reads as pathspec magic; never the global `--literal-pathspecs`, which every commit hook would inherit, its own globs then matching nothing. `cat-file`, `hash-object` and `readlink` take the path bare: none of them reads a pathspec. **A recorded path in the run set is committed whole**, with the other half of its rename where it has one: its content changed during the run, a change inside that file cannot be separated from what was there before, so its earlier changes go with it, and §3.1's *Pre-existing dirty paths committed* append names it rather than deciding it silently. A path the run changed back to what it held has an unchanged fingerprint and is left out: the run's net change there is none.

   This is a **rule, not a prompt.** An earlier draft asked the user to choose between enumeration, whole-tree staging, and skipping the commit; that reintroduced exactly the "prompt that can be answered no" §1 rule 5 exists to remove, offered a skip option that contradicts the unconditional commit, and fired once per unit in a loop. Leaving out what did not change and committing whole what did is the safe answer in every case — the first keeps somebody else's work out of the commit, the second keeps the run's in — so it is taken without asking, and the §3.1 line reports both.

2. **A stash the caller pushed.** Never restored here and never dropped. It stays where it is and §3.1's line names it, because a stash nobody mentions is a stash nobody remembers.

3. **Temp files are already out of reach.** Every caller writes its diffs, claims files, and scan summaries to `mktemp -t …` outside any repo tree specifically so `add -A` cannot pick them up. This step does not re-verify that; a caller that writes a temp file inside the tree breaks this step's staging, which is why the rule sits in the callers.

**A `git add` git refuses** (a held `index.lock`, a full disk) is a unit that did not land too: what §2.3 and §2.12 say of a rejected commit holds for it, save that its changes are in the working tree, perhaps partly staged, rather than staged, as after an `add -A`.

**Nothing to commit** — on the `add -A` path, the index holds nothing to commit after it (`git -C "<repo>" diff --cached --quiet` exits 0), a change the run staged itself with `git mv` or `git rm` included; under carve-out 1, the run set is empty. Never run §2.3 with an empty `--` list: `git commit --` with no path commits whatever the index holds, somebody else's staged change included, or fails with `no changes added to commit`. Do **not** emit a line here — §3.1 allows exactly one per call, and this path continues. If the branch carries commits this run made earlier (the §2.12 split form), proceed to §2.4 and report the run's outcome from the pushing rows. If it carries none, the call ends and §3.1's `no changes to commit` row is the line. An `/upgrade` component already at its target version, or a re-run that changed nothing, both land here legitimately.

**The secret scan — last, just before §2.3.** Once the call has something to commit, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/secret-scan.py" --repo "<repo>"` on the `add -A` path, which reads the staged diff, or, under carve-out 1, the same with `-- <path> …` appended, one argument per enumerated path, after the `add -N` above, which reads those paths against `HEAD`. It reads only the lines the commit adds and the names of the files it adds or changes, so a secret already in the history is not reported again. Each possible secret prints as path, line, rule and a masked preview — a token's first four characters, its public format prefix, and its length; a password's or a URL's credentials' length alone; never the value — after it has dismissed and counted placeholders, environment-variable references and lines carrying a `gitleaks:allow` or `pragma: allowlist secret` marker. It looks for private-key blocks, cloud and SaaS token formats, three-part JWTs, credentials inside a URL, a credential-named key assigned a literal, and an added `.env`, keystore or credentials file.

- **Exit 0** — no hit: go on to §2.3.
- **Exit 1** — show its output verbatim, then ask:

      choices: ["Stop — leave it uncommitted so I can remove it (Recommended)", "Not a secret — commit it"]

  *Stop* is a commit that did not land — §3.1's `<who>` is `the secret scan, at your request`, and its `<reason>` the hits' paths and lines — so §2.3's rejected-commit rules, §2.12's for a split and the caller's own for a loop all hold for it as for a hook's rejection. On the `add -A` path, first unstage everything this call staged — `git -C "<repo>" restore --staged -- :/` (`git -C "<repo>" rm --cached -r -q -- :/` on a branch with no commit yet), safe because the precondition made everything in the index this run's own — so the staged copy that still holds the secret is not what a plain `git commit` takes once the user has edited the file, and no half of a rename is left staged without the other; the work stays in the working tree. *Not a secret* goes on to §2.3, and §3.1's line carries the *Possible secrets committed* append. Ask on every call that finds a hit — each unit's hits are new ones — never caching the answer as §2.4 caches its choice.
- **Exit 2, or no `python3`** — the scan did not run. §2.3 goes ahead (§1 rule 4), and §3.1's line carries the *Secret scan not run* append.

A hit's value is never written anywhere — not into the commit message, the pull-request body, the run's report or a specs-repository artifact. The masked preview is the most any of them carries.

### 2.3 Commit

**Subject.** Every commit this entry point makes ends with `[<key>]` where the run resolved a key, and carries a `Work-Item: <workitem_key>` trailer where that key's folder has one — `workflows-core:implementation-format` §3, this plugin's own documented convention, binding on all three callers. **This is where the plugin writes that convention rather than merely teaching it.**

Everything the convention leaves open comes from the repository, never from habit: read `git -C "<repo>" log --oneline -20` and match what it shows. A conventional-commits log gets `feat:` / `fix:` / `chore:` matching the type the run's own branch prefix already expresses (`workflows-core:branch-naming` §2.4 lists each command's fallback prefix, but a repo with its own documented convention may have supplied a different one — read what the run resolved, not the fallback table); a log with no discernible convention gets a plain imperative subject. A caller with a full template of its own overrides this paragraph — `/vuln`'s "Git Workflow → Commit message" is the one that exists today — and passes it as `commit_template`.

**A run with no key writes no suffix.** `/implement` in direct mode and `/vuln` on a bare `CVE-ID` both resolve no folder; the subject is the bare imperative and the trailer is absent. Never invent a key to satisfy the convention — the scan in `workflows-core:implementation-format` §4 searches for tokens the run already holds, and a minted one matches nothing.

**Body.** What changed and why — one line per notable item — plus the review verdict where the caller has one, and the test result where the caller ran tests. **Trailers.** `Co-Authored-By: Claude <noreply@anthropic.com>`, plus `Work-Item:` where the folder supplies one; a caller's own template may add more. This diverges from `workflows-core:specs-repo-git` §1 rule 6, which forbids the trailer, and follows `workflows-core:phase-handoff` §1 rule 6 instead, for the same reason: a bookkeeping file is plugin-generated, and code is authored.

**Write the whole message to a file and commit with `-F`:**

    git -C "<repo>" commit -F <msg-path>

Under §2.2's carve-out 1, run it as one commit, `git -C "<repo>" commit -F <msg-path> -- ':(literal)<path>' …`, with one `':(literal)<path>'` argument per enumerated path: git then commits those paths' work-tree state, read literally, and nothing else the index holds. Where git ends it with `nothing to commit` (exit 1), every path's work-tree state is already what `HEAD` holds: that is §2.2's *Nothing to commit*, never a commit git failed to write. **Then bring the index back in step with the new `HEAD`.** A pathspec commit runs the `pre-commit` hook against a temporary index, so a file the hook fixes and re-stages, adds, or removes is committed while the real index keeps the old entry: a reverting copy, a staged deletion of the file it added, or the file it removed (measured on git 2.43: `MM`, `D ` beside `??`, and `AD`). Just before the commit, read what the index already holds staged, `git -C "<repo>" diff --cached --name-only -z --no-renames`. Once the commit lands, read the paths it carries, `git -C "<repo>" diff-tree --no-commit-id --name-only -r -z --root --no-renames HEAD`, and the paths whose index entry now differs from `HEAD`, the same `diff --cached` again. Over the paths on both of those two lists, less every path the first read listed that the commit's own pathspecs do not name — a change somebody else had staged, left as they staged it — run `git -C "<repo>" restore --staged -- ':(literal)<path>' …`, and run nothing where none is left. Never over the commit's whole list: a path the commit deleted is in neither `HEAD` nor the index, and one pathspec that matches nothing fails the whole `restore`, which then restores nothing.

`<msg-path>` is a `command mktemp -t dw-commit-msg-XXXXXX` path **outside any repo tree** (§5). This is `workflows-core:phase-handoff` §2.7's rule applied to the commit message, and it is not stylistic: `-m "…"` inside a double-quoted shell string command-substitutes `$(…)` and backticks before git ever sees the text, and `/vuln`'s template interpolates an NVD CVE description — free text, routinely containing shell metacharacters and version expressions — straight into it. `/upgrade` interpolates component names and `/implement` a free-text summary, with the same exposure. `-F` also preserves the multi-line body and trailer that `-m` would mangle.

**Remove `<msg-path>` once the commit has been made** — `command rm -f -- "<msg-path>"`, `command` because the Bash tool's shell carries the user's aliases and an `rm -i` of theirs would ask, be answered no from that shell's empty standard input, and leave the file. Nothing else removes it: it sits under the system's temporary directory, where no later step of the run and no later run looks. A rejected commit keeps its file until the run has recorded the failure, then removes it too: the commit is not retried here, so nothing re-reads the path.

Never `--amend` (§1 rule 3): an amend rewrites a commit that may already be pushed, and this step is reachable more than once per run.

**A rejected commit is a reported failure, never a silent one.** A `pre-commit` / `commit-msg` hook can reject the commit; the changes then stay staged — or, under §2.2's carve-out 1, which stages nothing, in the working tree. A commit git itself fails to write (a signing failure, an unset author identity) leaves them the same way, and everything this paragraph and §2.12 say of a rejected commit holds for it, with git's error in place of the hook's output. Do not retry, do not bypass with `--no-verify`, and do not proceed to the next unit as though the commit landed — a later unit's §2.2 would fold this unit's diff into that unit's commit under the wrong message. Record the failure and the hook's output or git's error; in the §2.12 split form the caller reports it in its own per-unit results table, and the terminal call's §3.1 line names the unit that failed to commit where an earlier unit committed, and is otherwise the *Commit rejected* row (§2.12).

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
                 --title '<title>' --body-file "<body-path>" [--draft]

**`<title>` is free text, so it goes in single quotes**, each `'` it holds written `'\''`: inside double quotes its backticks and `$(…)` would be command-substituted before `gh` saw it. §3.2's command quotes it the same way.

**The host is kept, not stripped.** `gh -R` accepts `[HOST/]OWNER/REPO`, and `gh auth status` succeeds whenever the user is authenticated to *any* host — so a bare `OWNER/REPO` derived from a GitHub Enterprise remote resolves against **github.com**, silently targeting an unrelated public repository if one happens to sit at that path. Only `github.com` may drop the host. Validate the slug against `^[^/]+/[^/]+$` before calling `gh`; anything else (a Bitbucket `scm/proj/repo`, a nested GitLab group) is not a `gh` target — skip to §3.2.

The `sed` expressions strip, in order: a scheme (`ssh://`, `https://`), a `user@`, and a host with an optional `:port` terminated by `/` **or** `:` (the scp-like `git@host:Org/repo` form uses a colon), then a trailing slash and the `.git` suffix. Verified against `git@host:Org/repo.git`, `https://host/Org/repo(.git)`, `https://user@host/Org/repo.git`, `ssh://git@host/Org/repo.git`, `ssh://git@host:7999/proj/repo.git`, `git@ghe.corp:Team/repo.git`, and a nested `group/sub/repo`. A two-expression form matching only `git@host:` or `https://host/` passes an `ssh://…` URL through **unchanged** — do not simplify it back.

**Capability probe, not host classification.** Try the call; on any failure fall back to §3.2. Push authority and pull-request authority are independent — push runs over SSH with a per-repo key, `gh` runs over the API with a token, and the same account can have write access to one repository and read access to another. No hostname test can detect that mismatch, which is why `docs-workflows:finish-and-handoff` §4's host classification is right for choosing *instructions* and insufficient here.

`gh` wraps the API rather than calling it over HTTPS, which is what the zero-direct-API rule permits.

### 2.7 The title and the body file

Title: the commit subject of §2.3 — on a §2.12 terminal call, which makes no commit of its own, the caller's `title`, written the way §2.3 writes a subject.

Body: **written to a file** — `<body-path>`, a `command mktemp -t dw-pr-body-XXXXXX` path outside any repo tree — never passed inline, which would break on newlines and quoting. The same file is what §3.2 names when `gh` is unavailable, so the user pastes the identical body — banner included — into the web UI.

**What the body holds.** Four sections, in this order, rendered from `body_facts`, with no preamble: on a `clean_finish: false` run §2.9's banner is the body's **first line**, and otherwise its first heading is — save where a template resolves (below), which keeps its own opening first, under the banner where there is one.

1. `## Summary` — what changed, one line per notable item, and the files changed: the paths the run's commits on this branch carry, read from git (`git -C "<repo>" show --no-show-signature --name-status -z --format= <sha>` per commit this run made), never an agent's own list. Where the branch also carries commits this run did not make — any that `origin/<base>..HEAD` lists besides its own, unpushed commits on a local `<base>` included — the Summary names them (`git -C "<repo>" log --no-show-signature --format='%h %s' origin/<base>..HEAD`, less this run's) as part of the pull request this run neither made nor reviewed, and Merge danger weighs them.
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
| `pre_existing_dirty` | porcelain paths dirty before the run's first edit, each with its §2.2 fingerprint, or `null` |
| `stash_ref` | the stash the caller pushed at branch time, or `null` |
| `key` | the key of the unit the run implements (`workflows-core:implementation-format` §3) — the resolved folder's (`workflows-core:addressing` §4), save where `/implement` chose an Epic under a PRD address and passes that Epic's — or `null` |
| `workitem_key` | that unit's folder's `workitem_key`, or `null` |
| `title` | the commit subject and pull-request title — on a §2.12 terminal call, which commits nothing, the pull-request title alone (§2.7) |
| `body_facts` | what §2.7 renders into the body file's four sections: what changed (the files changed being §2.7 item 1's, read from git); the before and the after the run observed; the facts its door and blast-radius calls rest on; and the review — the classification, the verdict and triage, and every finding not applied |
| `clean_finish` | `true` / `false` per §2.9 |
| `commit_template` | the caller's own message template, or `null` |

### 2.12 Splitting the call across a loop

A caller whose units **share a single branch** — `/upgrade`'s per-component loop — may run **§2.1–§2.3** at the end of each unit and the **full entry point once** at the end of the run. The unit-level call commits and stops; the terminal call finds nothing left to commit, takes §2.2's *nothing to commit* path, and continues into §2.4 and §2.5–§2.6 because the branch carries commits to push.

**§2.1 is inside the split, not outside it.** An earlier draft sanctioned "§2.2–§2.3 alone", which ran every per-unit commit with no gate: a caller whose branch creation had failed would commit its whole batch onto the default branch, one commit per unit, and only discover it at the terminal call — which would then report `NOT committed` over work that was very much committed, in the wrong place. Run the gate every time; it is four cheap reads.

The split is what makes per-unit committing worth having: a batch that dies on component three still has one and two committed, each with its own message, on a branch that bisects. Both halves are required — a caller that runs the unit-level half and never reaches the terminal call has committed the work and left it on the machine, which is only half the fix.

**Where each unit gets its own branch there is no split.** `/vuln` is that case: a unit-level call that only committed would leave that CVE's branch unpushed forever, since the terminal call can push only the branch it is standing on. Each CVE runs the **full** entry point, and §2.4's once-per-run caching keeps that from asking N times.

**A unit-level commit that does not land ends the split**, whether a hook rejected it, git failed to stage or write it, or you stopped it at the secret scan (§2.2, §2.3). Its changes stay behind uncommitted, and §2.3 forbids carrying on as though it landed, so the caller works no later unit — a later unit's §2.2 would fold the rejected changes into that unit's commit — and goes to its terminal call, which then stages and commits nothing: it runs §2.1, then, where the branch carries a commit this run's unit-level calls made, §2.4 onward for those commits, its §3.1 line carrying the *A unit commit rejected* append; the caller sets `clean_finish: false` (§2.9). Where the branch carries no such commit, its line is the *Commit rejected* row.

**A unit-level call emits no §3.1 line** (§3.1 allows one per *full* call), but it is not silent: it returns its outcome — commit sha, `nothing to commit`, or a commit failure with its reason, and, where §2.2's scan did not run, a hit was committed as not secret, or carve-out 1 committed a path that was dirty before the run or kept a staged deletion out, that too, with those paths — to the caller, which records it in its own per-unit results table. The terminal call's §3.1 line carries the *Possible secrets committed*, *Secret scan not run*, *Pre-existing dirty paths committed* and *A staged deletion kept* appends for every unit that returned one, since the terminal call stages nothing and runs no scan of its own. §2.10's "every failure is reported" is satisfied there, not by a `Code repo:` line.

---

## 3. Reporting

### 3.1 Outcome line

Exactly one per **full** call, prefixed `Code repo:`. A caller that finishes several branches in one run (a `/vuln` CVE loop) emits one line per branch. A §2.12 unit-level call emits none.

`<what>` below is `<sha7> on <branch>` for a call that committed, and `<n> commit(s) on <branch>` for a terminal call whose own commit set was empty, or skipped after a unit that did not land (§2.12), but whose branch carries commits from unit-level calls; `<who>` is `a <hook> hook`, `git` where git itself failed to stage or write it (§2.2, §2.3), or `the secret scan, at your request` where §2.2's scan stopped it; `<where>` is `staged` after an `add -A` whose commit a hook or git rejected, and `in the working tree` where §2.2's `git add` failed, the secret scan stopped the commit, or a carve-out-1 commit did not land; and `<unit>` is the unit's name on a §2.12 split, `the commit` otherwise.

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
| Pre-existing dirty paths committed (§2.2) | append `; <n> path(s) dirty before this run whose content changed during it were committed whole, their earlier changes included, each with the other half of its rename where it has one (<path>, …).` |
| A staged deletion kept (§2.2) | append `; <path>, … changed during this run but stay uncommitted, since committing them would undo a deletion you had staged.` |
| A stash is outstanding | append `; a stash from this run's branch step is still on the stack (<stash_ref>).` |
| Possible secrets committed (§2.2) | append `; <n> possible secret(s) the scan flagged were committed as not secret, at your request (<unit>, …).` |
| Secret scan not run (§2.2) | append `; the secret scan did not run (<unit>: <reason>; …).` |

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
      --title '<title>' --body-file <body-path> [--draft]

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
- Never writes a possible secret's value into a commit message, a pull-request body, a report or an artifact — §2.2's masked preview is the most any of them carries. Committing a hit the user ruled not secret is the user's call (§2.2), not this rule's breach.
