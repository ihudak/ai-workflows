# Specs-repo git — Shared Reference

Single source of truth for the two git entry points the plugin runs against the
**specs repo** (`$SPECS_PATH`). Every command that writes a bookkeeping artifact
there runs them through the `workflows-core:specs-git` skill, which runs `scripts/specs-git.py`; this file is the contract that script follows and is tested against, and the procedure a run follows by hand only where the skill says the script cannot start. The orchestrator owns any
printed output; this reference owns the gates, the bounded write authority, the
branch policy, and the failure discipline — the same shape as
`feedback-emission.md`, `cost-emission.md`, and `followup-emission.md`.

**Purpose.** The per-PRD `dev-workflows/` area exists so feedback, cost,
follow-ups, and the resume pointer reach the **plugin maintainer**. They reach
the maintainer only if they are committed and pushed. The emitters deliberately
never commit — they run mid-run, often from inside someone else's repository,
and must never touch git. This reference supplies the two steps that close the
loop: a **run-start** flush and branch disposition (`specs-preflight`, §3) and a
**terminal** commit (`commit-artifacts`, §4).

**Scope.** ONLY the bounded artifact paths of §2.1, ONLY inside `$SPECS_PATH`. Nothing here ever touches a code repo, a docs repo, or the current working directory, where it is not the specs repository. The code repo a run just changed is finished by `dev-workflows:code-handoff` — a different repository, a different remote, and its own `Code repo:` outcome line. Neither entry point here opens a pull request: `specs-preflight` and `commit-artifacts` are prompt-free bookkeeping steps, and opening a pull request is outward-facing. Deliverable handoff — including `gh pr create` where the host supports it — lives in `${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md` §2.6, behind that reference's consent choice. `git push` here is git-protocol, already sanctioned by `docs-workflows:finish-and-handoff` §3.

## 1. Hard rules

1. **`git -C` always; `cd` never.** Every invocation is
   `git -C "$SPECS_PATH" …`. The working directory is NEVER changed. Most
   callers are running inside a *different* repository when these entry points
   fire; a `cd` would corrupt their git state.
2. **Bounded paths.** Only §2.1 paths are ever staged. `git add -A` is never
   issued at repository scope — always `git add -A -- <literal paths>`.
3. **Bounded branches.** Only branches matching `^(idea|prd|ard|spec|epics|design|ready|brd|frames|kb|conformance)/`
   are the plugin's to switch away from or delete (§2.2). They, the default
   branch and §8's session branch are the only branches it pushes, only to
   `origin`, and only while the push would publish nothing but its own
   session-file commits (§4 step 5) — on the session branch, its own merges of
   the default branch too (§8.4). The session branch, `session/<identity>`, is
   the plugin's for commit and push only: it is never checked out, switched to,
   switched away from or deleted, and it is not in that pattern.
4. **Never destructive.** No `push --force`, no `push -f`, no `branch -D`, no
   `merge`, no `rebase`, no `reset`, and never delete an `index.lock`. §4 step
   4's `restore --staged` is not a `reset`: it rewrites only index entries for
   paths the commit just carried, moves no ref and touches no working-tree file.
   **§4 step 1's here form is the named exception to that `moves no ref`.** For a run typed mid-run that holds no stay (§3.5), it moves HEAD's own branch by `update-ref` from the tip it read onto a commit of the run's own change, made with no checkout, then runs that `restore --staged` over the paths the commit carried whose index entry nobody has staged anew since (§4 step 1), so the index follows HEAD there; it writes no working-tree file, and the held record (rule 8) journals both steps before the ref moves.
   §8's merges are of the default branch into the session branch, never the
   reverse, and move no checkout. **§4 step 6's replay is the named exception
   beside them, and it does move the checkout.** Where `origin` rejects a push
   of the plugin's own session-file commits as non-fast-forward, it takes
   `origin`'s commits in with no `merge`, `rebase` or `reset`: it writes the
   plugin's commits again on top of `origin`'s branch with `merge-tree` and
   `commit-tree`, which move nothing, then moves the branch onto the result
   by `update-ref` inside one locked transaction, and, where the checkout
   stands on that branch, carries its index and files along by
   `read-tree -m -u`. Where the checkout stands is read at the move itself,
   never trusted from before the replay — a branch the checkout left during
   the replay moves by `update-ref` alone — and once more under the
   transaction's lock, so the move refuses, with nothing moved, where
   another session switches the checkout to or from the branch while it
   moves. One instant is left: a switch onto the branch between that last
   look and the ref's write, which no lock this side can take holds off,
   still moves the branch under that checkout, its HEAD on the new tip and
   its index and files on the old. It refuses too where it would
   write over a path the user changed, left untracked or ignores —
   `session-branch.py`, which runs the replay, tests every such path before
   anything moves, since `read-tree` alone writes over an ignored file — and
   the user's staged and unstaged changes keep their status. Only then does
   it push.
   Two discards are named, each of a session file whose exact content it has just found on a branch: §8.3's `lift`, which returns such a file to HEAD once it has found that content on the session branch, and §4 step 1's landing lift, which writes back, once `<default>` holds a landed change, the version that change, or the chain of held changes it ends, started from — only where the working copy is still exactly what landed.
5. **Never fatal.** Every failure is reported and the run continues.
   Where `specs-git.py` stops on a failure it did not foresee after its first write, it prints `Specs preflight: stopped early (<the error>) — what it did is above, and the next run's preflight goes on from where this one stands` at the start and `Specs repo: NOT FINISHED — the terminal step stopped early (<the error>); what it committed or pushed is as it left it, and the next run's preflight flushes the rest` at the end, the end's one outcome line.
   The run never fails because of a git step here.
6. **No `Co-Authored-By` trailer.** These are plugin-generated bookkeeping
   files, not authored content, and each artifact already carries its own
   `author:` field (`feedback-emission.md` §1).
7. **Prompt-free.** Neither entry point asks the user anything. `specs-preflight`
   prints its `Environment:` line (§3) and is otherwise silent unless it acts, a
   guard fires, or §3.1 reports a misconfigured `$SPECS_PATH`; `commit-artifacts`
   emits one outcome line (§6).
   `specs-preflight`'s acts include each report it prints of an attempt that failed (rule 5) — a pull, a push, a deletion, a test that could not run — and of the switch §3.5 then leaves undone for it.
8. **State of its own.** The **push-refusal record** of a branch, which §4
   step 6 writes when `origin` refuses a push to that branch and step 5 reads:
   a file whose path, `<record>` below, is
   `<common>/workflows/push-refused/<branch>` — `<common>` being what
   `git -C "$SPECS_PATH" rev-parse --git-common-dir` prints, joined to
   `$SPECS_PATH` where that is a relative path, and a `/` in the branch name a
   directory level, as git's own refs have it. The record stands where that
   file exists, whatever it holds; it holds the date. It is a file in the
   common git directory, not configuration, because a hardened container
   mounts `.git/config` read-only while the rest of `.git` stays writable, and
   a record that cannot be written has every later run push into the same
   refusal. The older form, the configuration key
   `branch.<branch>.workflowsPushRefused` — which runs before this one wrote,
   and which step 6 still writes where the file cannot be written — is read
   too and counts as the record. And §8.2's one marked block in the
   repository's own `info/attributes` (`git rev-parse --git-path info/attributes`),
   and the per-worktree record `session-branch.py` keeps of the session files
   §8.3's overlay placed (`git rev-parse --git-path session-branch-placed.json`).
   And the run's state record, outside every repository (§7), which `scripts/specs-git.py` writes and removes.
   And the held commits (§4 step 1's landing): each kept under `refs/workflows/held/<commit id>`, and listed by the per-worktree record `git rev-parse --git-path workflows/held.json`, which also journals every landing and here form in flight; a held commit's ref and its entry are removed once it lands, its journal is finished, or it is dropped (§3.2).
   Nothing else is written here; what git itself writes for the commands this
   reference runs is unchanged by it — the upstream a `push -u` sets, the same
   upstream §4 step 6's replay sets with `git branch --set-upstream-to` where
   step 5's push carried `-u`, since its own push, from a commit id, sets
   none, and the
   whole `branch.<branch>` section that `branch -d` removes; §3.5's B2 removes
   the record of a branch it deletes — the configuration-key form only where `.git/config` can be
   written, and its report names one it cannot remove. `workflows.sessionBranch` is the user's
   own key; this reference reads it and never writes it.

## 2. Bounded write authority

### 2.1 Paths

Exactly ten shapes, derived from the emission ladders, from the drafts the family writes for the operator and from the security register — five directory shapes and the five single files §2.1 names below. Nothing outside this
set is ever staged.

```
<specs-root>/{specs|specifications|vis}/**/dev-workflows/**   # tier 1: feedback, cost, resume.md
<specs-root>/documentation/*/dev-workflows/**                 # the documentation run with no PRD (D19): feedback, cost
<specs-root>/dev-workflows-feedback/**                        # feedback-emission.md §2 tier 2 (keyless runs)
<specs-root>/dev-workflows-cost/**                            # cost-emission.md §9 pending files (keyless runs)
<specs-root>/security/*/{runs/**|scans/**|dev-workflows/**|register.json|register.md}  # security-register-format.md §1: the register of one code repository (/security-workflows:scan), its own paths only, and its keyless scans' cost and feedback (cost-emission.md §8, feedback-emission.md §2)
<specs-root>/{specs|specifications|vis}/**/implementation.md  # implementation-format.md §1, appended by /implement
<specs-root>/{specs|specifications|vis}/**/follow-ups.md      # followup-emission.md §2, appended per PRD/Epic folder
<specs-root>/{specs|specifications|vis}/**/_security.md       # security-register-format.md §1: a unit's scan note, appended
<specs-root>/{specs|specifications|vis}/**/pr-draft.md        # the /document (keyed mode) pull-request draft
<specs-root>/{specs|specifications|vis}/**/*-implementation-gaps.md  # the <KEY>-implementation-gaps.md draft (source-truth.md §7.5)
```

**The security register is bookkeeping**: its records are a run's own and must not wait on anyone's review, so `commit-artifacts` (§4) commits them and no pull request hands them off, as `${CLAUDE_PLUGIN_ROOT}/references/security-register-format.md` §1 says. The same directory holds a keyless scan's cost and feedback entries, under `dev-workflows/cost/` and `dev-workflows/feedback/` beside the register, filed per code repository as the `documentation/` shape files a documentation run's (`cost-emission.md` §8, `feedback-emission.md` §2). **The shape names the register's own paths and nothing else under `security/`** — `runs/`, `scans/`, `dev-workflows/`, `register.json` and `register.md` in each `security/<repo-slug>/` — because a specs repository can already hold a team's own `security/<dir>/` documents, a threat model or a policy, and a wider shape would sweep an uncommitted edit there into a prompt-free session commit of any family command, and push it.

**The `documentation/` shape is the `docs-workflows` family's, and it exists because that family's normal run has no PRD and never will.** A documentation run against a repository nobody has written a PRD for would otherwise park every entry as *pending*, awaiting a reconciliation into a PRD directory that is never coming — so those entries accumulate forever and reconcile against nothing. The rung `feedback-emission.md` §2 and `cost-emission.md` §8 insert before pending writes instead to `<specs-root>/documentation/<docs-repo-slug>/dev-workflows/{cost,feedback}/`, where `<docs-repo-slug>` is the one-segment name the next paragraph defines. **Per docs repo, not one flat `documentation/` bucket**, for exactly the reason the PRD-directory rung exists for the pipeline: a person documenting two products must still be able to answer what documenting each one cost. The docs repo is that family's unit of attribution.

**`<docs-repo-slug>` is defined here, once, and it is always exactly one path segment.** It is derived in two steps, and two implementations that follow them produce the same directory for the same repository, byte for byte:

1. **The source string.** Read the resolved docs repository's `origin` remote (`git -C <docs-repo-root> remote get-url origin`) and derive `OWNER_REPO` from it exactly as `${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md` §2.6.1's `owner-repo` derives it — the same `host` and `slug` expressions, and the same rule that only `github.com` drops the host — but **not** its SSH-alias resolution: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" owner-repo --repo <docs-repo-root> --no-alias` prints it as `name` — never `owner_repo`, which is `null` for a slug `gh` cannot take, a check that serves `gh` and is no part of this name — and `name` is `null` where the repository has no `origin` or the derivation comes out empty; where the call exits 2, the source is the basename of the git root, as below. That leaves out the alias resolution, which serves `gh` and `docs-workflows:finish-and-handoff` §4's footer, never a name: the slug is computed from the remote's own text, so a docs repository's folder keeps the name earlier runs gave it. Where the repository has no `origin` remote, **or where that derivation comes out empty** — a nonsense remote such as `https://github.com/` names no owner and no repository — the source is the basename of its git root instead. Where the run's write target is not a git work tree at all, the source is the basename of the target path, resolved to absolute. Three runs' command bodies lead to that last case: `/document` in direct mode pointed at a directory outside any git work tree; `/docs-init` when its operator cancels Phase 0 step 3's offer to create or initialise an absent or empty target — that command's emitter tail still runs, against a path that is not yet a repository; and `/docs-audit` where `resolve-docs-repo` answers with a directory that carries a docs signal and sits in no git work tree, which its own backlog path already provides for.
2. **The flattening — one substitution, per byte, in the C locale:** `printf '%s' "$source" | LC_ALL=C sed 's/[^A-Za-z0-9._-]/-/g'`. Every byte outside `A–Z`, `a–z`, `0–9`, `.`, `_` and `-` becomes one `-`. `/` is such a byte, so this one substitution is also what flattens `OWNER_REPO`'s separators; there is no second step to order it against. It is per **byte**, not per character: `ñ` is two bytes in UTF-8 and becomes `--`, so `Notes (draft) ñ` gives `Notes--draft----` wherever it is computed, where a per-character rule would give `Notes--draft---` and file one repository's record in two directories.

So `git@github.com:acme/docs.git` gives `acme-docs`, and `ssh://git@git.example.com/team/docs.git` gives `git.example.com-team-docs`. **Every such byte is flattened, not only `/`,** because a directory name is the operator's to choose and may carry a space or a non-ASCII letter, and a substitution that admits no exception is what lets two implementations reproduce this directory byte for byte. **It is no longer flattened to keep the path out of the classifier's quoting, and that half of the reason is retired rather than the rule**: `git status --porcelain` does wrap such a path in double quotes (with a non-ASCII byte octal-escaped), and step 2's classifier, reading the path as reported, would have seen `"documentation/…` and never staged it — but step 1 above now reads `-z`, whose records are never quoted, so that is a form this procedure no longer meets. The flattening stands unnarrowed, because **the one-segment property is the whole point, and it is why the flattening is not cosmetic**: step 2's classifier below admits exactly one segment between `documentation/` and `dev-workflows/` (`^documentation/[^/]+/dev-workflows/`), while an unflattened `OWNER_REPO` is two segments on GitHub and three anywhere else. An entry written under one would be classified OTHER — never staged, left dirty, and firing §3.3's G1 on every later preflight of every caller, which is exactly the failure each of the single-file shapes below was once found to cause. Every site that fills the placeholder — `feedback-emission.md` §2, `cost-emission.md` §8, and the `docs-workflows` commands whose runs emit there — cites this definition rather than restating the derivation; a second derivation is how two sites come to disagree about where one repository's record lives. The flattening can in principle map two remotes to one name (`a-b/c` and `a/b-c` both become `a-b-c`); that is accepted, since the alternative is a second derivation or a path the classifier cannot stage.

**The inner `dev-workflows/` in that path names the *family*, not the plugin — do not "correct" it per-plugin.** The shipped persistence ladder writes `<PRD-dir>/dev-workflows/cost/<sid8>.md` regardless of which plugin emitted the entry, and this shape is the same directory one level out. Renaming it to match the emitting plugin would fragment one repository's cost record across one directory per emitting plugin and break every reader of it. **No new branch prefix goes with this shape**: §2.2's prefix authority governs branches the plugin creates *in* `$SPECS_PATH`, and the documentation family's one branch there is `/release-notes`', which hands its draft off under the existing `prd/` prefix — `/document`'s deliverable is the docs repository, where it branches, commits and drafts a pull request it never pushes.

**The five single-file shapes name files, never their folder, and the distinction is the
whole safety property.** All five sit in the feature folder rather than under `dev-workflows/`. The
first two are read by *key* rather than by session — `implementation.md` is read by `/document` and
`/release-notes` (their two-source read), by `/ready` (a unit's derived phase and its repositories), by
`/epics` and `/specify` (repository names) and by `epic-picker.md`'s ● marker — every command
`grep -l 'implementation\.md' plugins/*/commands/*.md` returns but `/implement`, which writes it — and
a record only one machine holds is a record the next run cannot use; `follow-ups.md` is `followup-emission.md` §2's "alongside the artifacts the
follow-ups are about", which its §3 makes explicit is about where a *reader* looking at the folder finds
them. The third, `_security.md`, is the note `/security-workflows:scan` appends to the folder of the unit a run is addressed by, where a reader looking at that folder finds it (`security-register-format.md` §1). The last two are drafts for the operator, written where the operator looks for them — `pr-draft.md` also read by key, as the first two are, by `/dev-workflows:ready` from `<default-ref>` (its Phase 1 step 2c): `/docs-workflows:document` (keyed mode) writes `pr-draft.md` for the pull request it
never opens itself, and it and `/docs-workflows:release-notes` write `<KEY>-implementation-gaps.md`,
the bug-report draft `source-truth.md` §7.5 fixes — its name carries the key, so it is matched as
`*-implementation-gaps.md`. But that same folder holds the phase deliverables (`prd.md`, `ard.md`, `specification.md`,
`design.md`, `idea.md`, `_readiness.md`), which are `${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md`'s
to commit behind its own consent choice. Widening a shape to the folder would sweep them into a
prompt-free bookkeeping commit and take the operator's choice away, so the five files are named
literally and nothing else in that directory is ever staged here. **The `/release-notes` draft,
`release-notes.md`, left this set**: it is content a team reviews before it is published, not a
draft one operator pastes once, so that command hands it off behind the consent choice like any
deliverable (`phase-handoff.md` §4.0), and this commit never stages it.

**Three single files were outside this set until a review found them** — `implementation.md`, the
`/release-notes` draft, which has since left the set again for a pull request of its own, and
`follow-ups.md` — while `/implement` and `/release-notes` each told the operator the terminal step
committed theirs. It did not: step 2 below classified each as
OTHER, step 3 skipped it, and the file then sat permanently dirty — which fired §3.3's G1 dirty-tree
guard on every later run of any of its callers, suppressing the leftover flush and the
branch disposition for the rest of the session. **`follow-ups.md` was the third instance and it was
found the same way, by a live run rather than by reading** — long after the first two were fixed, because
this section's own comment claimed follow-ups were tier 1 under `dev-workflows/**` and its source
citation pointed at a section of `followup-emission.md` that had been renumbered out from under it when
that ladder was cut from four rungs to two. Two stale pointers agreeing with each other read exactly like
a verified fact. **The two drafts were the fourth and fifth instances**, found by classifying a real
specs repo's status against this list after a keyed `/document` run: both came out OTHER beside a
staged cost entry, and nothing else committed them. When an emission ladder changes shape, or a
command starts writing a draft or a record of its own into the feature folder or a new directory, re-derive this list against it rather than
trusting either end. `/epics` is the contrast: the `epic.md` files and `_coverage.md` it
writes are its deliverable, which this reference never stages and `phase-handoff.md` §2 hands off
behind that command's consent choice, as it does every other producer's.

**A screenshot `/document` stages for manual upload is not a shape, and `/document` keeps it out
of `git status` instead.** Its staging directory is, by default, the resolved PRD folder's screenshot subfolder
(`/docs-workflows:document` Phase 1), which lies under `$SPECS_PATH`. No shape stages it, for three
reasons: it is a copy of the operator's own file, kept only until they upload it by hand, so a
commit would make a temporary binary permanent in the specs repo's history through a prompt-free
bookkeeping commit; the default subfolder, `Doc screenshots/`, carries a space, which
`git status --porcelain` once quoted out of step 2's sight — a side effect step 1's `-z` retires,
so the classifier now reads that path raw and places it in OTHER, and what keeps the copy out of
`git status` at all is the local exclude named below, never the quoting; and
a staging directory the operator names at `/document`'s Phase 1 may sit under `$SPECS_PATH` beside
the operator's own files, which a directory shape would sweep in. So `/document` keeps each copy it stages under `$SPECS_PATH` out
of `git status` itself, through that repository's local exclude file (its Phase 6.3), and nothing
here stages or touches it. A staging directory the operator names outside `$SPECS_PATH` is outside
this reference's scope.

Sources: `feedback-emission.md` §2 tiers 1–2 including tier 2's documentation
branch, `cost-emission.md` §8 tier 1, tier 2's documentation and security
branches and its §9 pending, `followup-emission.md` §2 (where it lands, per PRD/Epic folder),
`session-hygiene.md` §1 (resume tier 1), `source-truth.md` §7.5 (the
implementation-gaps draft), `docs-workflows:finish-and-handoff` §5 (the
pull-request draft) and `security-register-format.md` §1 (the security register
and a unit's `_security.md`).

**Staging is by enumeration, not by glob.** Pathspec glob magic (`:(glob)`) is
fragile to express and to review. Steps 1 and 2 are one call, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" --specs "$SPECS_PATH" status`, which prints `{"artifact": [...], "other": [...]}`, each list sorted: the ARTIFACT and OTHER paths below, as step 2 classifies them. Where it exits 2, report the first line of its stderr and stage nothing (§1 rule 5). Inside `specs-preflight` that report is `Specs preflight: could not list the uncommitted paths (<the first line of its stderr>), so nothing is staged`, printed once in a run, and the preflight goes on: §3.3's G1 has no path to find, §3.4's flush stages nothing, and §3.5 switches nothing that run, B2 and B4 staying with the line §3.5 gives. The script performs these two steps, which stay the rule it follows:

1. `git -C "$SPECS_PATH" status --porcelain -z --untracked-files=all`
   `--untracked-files=all` is **required** — the default collapses an untracked
   directory to a single `?? dir/` line, which would hide which files are being
   staged. `-z` is **required** too: without it git wraps any path carrying a
   space, a `"`, a `\` or a non-ASCII byte in double quotes and octal-escapes the
   non-ASCII bytes, and step 2's regexes are anchored at `^`, so the leading `"`
   alone puts such a path in OTHER. It is not a hypothetical shape: a feature
   folder is `<KIND>-<KEY>-<slug>` and `<slug>` is a kebab of a title, so a
   non-English title gives `specifications/PRD-ACME-1-zahlungsauslösung/`, under
   which every bookkeeping file this section owns was classified OTHER, never
   staged, and left permanently dirty — firing §3.3's G1 on every later preflight
   of every caller. Under `-z` each record is terminated by a NUL and the path is
   emitted raw: strip the two status bytes and the space and the remainder is the
   path. A **rename or copy** record carries a second NUL-terminated field, the
   original path, straight after it (`R  <new>\0<old>\0`) — consume it with the
   record it belongs to, never as a record of its own. `-c core.quotepath=false`
   is not a substitute: it suppresses only the octal escaping, and a path with a
   space is still quoted. `${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md`
   §2.3 reads the same form, for the same reason, over a different path set.
2. Classify each reported path: **ARTIFACT** if it matches
   `^(specs|specifications|vis)/.+/dev-workflows/` or
   `^documentation/[^/]+/dev-workflows/` or `^dev-workflows-feedback/`
   or `^dev-workflows-cost/` or `^security/[^/]+/(runs/|scans/|dev-workflows/|register\.(json|md)$)` or
   `^(specs|specifications|vis)/.+/(implementation|follow-ups|pr-draft|[^/]+-implementation-gaps|_security)\.md$`,
   **and** it does not match
   `^(specs|specifications|vis)/(.+/)?(brd|grounding|interview|design|attachments|revisions|bundle-[0-9]{8}|customer-sent-[0-9]{8}|Doc screenshots)/`;
   **OTHER** otherwise.

   **The exclusion is `workflows-core:addressing` §2's register of reserved
   subdirectory names, all but `dev-workflows/`, and it keeps a deliverable's
   files out of this commit.** None of those subdirectories ever holds a
   session file. They hold what a run copied in from outside — a customer's BRD
   files under `brd/source/` and `brd/source-external/`, the pages `/idea`
   vendors under `attachments/`, exported frames under `design/`, a package's
   copies under `bundle-<YYYYMMDD>/` — each under whatever name it arrived
   with, what it archived under `revisions/`, and what it wrote as a
   deliverable under `grounding/` and `interview/`. A customer's
   `implementation.md` or a vendored `release-notes.md` matched a single-file
   shape, and a copied tree holding a `dev-workflows/` directory matched the
   first, so this prompt-free commit took files that are `phase-handoff.md`'s
   to commit behind its consent choice. A feature folder placed beneath a
   directory with one of these names lies outside the layout `addressing` §2
   defines, which reserves them for a feature folder's own subdirectories, and
   its session files are classified OTHER. When the register gains a name, this
   pattern gains it too.
3. Stage the literal ARTIFACT paths only, those `status`'s `artifact` list names:
   `git -C "$SPECS_PATH" add -A -- <path> [<path>…]`.

`-A` is used deliberately: `cost-emission.md` §9 relocates a pending cost file
into a PRD directory and then **deletes** the pending file, and that deletion
must be staged. `-A` states that intent explicitly, and it was strictly
required before git 2.0, where `git add <path>` did not stage a deletion. On
git ≥ 2.0 a plain `git add -- <path>` stages a deletion for a literal path too
— verified empirically — so keep `-A` for explicitness and for older git, but
do not justify it by claiming plain `git add` cannot stage the deletion.

### 2.2 Branches

**The plugin manages only branches it created.** A branch is plugin-owned when
its name matches `^(idea|prd|ard|spec|epics|design|ready|brd|frames|kb|conformance)/`. The session
branch §8 creates is the plugin's too, for commit and push only (§1 rule 3).

Any other **named** branch save the default branch — the user's own work, a
hand-made branch — is left
alone and never switched away from (§3.3 G2). The run's artifacts are still
committed there, because a named branch cannot be lost, but never pushed
(§4 step 5): a push would publish whatever its owner has not pushed yet. In
session-branch mode they go to the session branch instead, and are pushed
(§8).

A **detached HEAD** is not a branch. It is handled separately and far more
strictly (§3.3 G0, §3.7): nothing is committed at all.

## 3. `specs-preflight` — run start

**Run by `scripts/specs-git.py`.** A run reaches this entry point through `Skill(skill: "workflows-core:specs-git", args: "start")` — the loader routes `args: "specs-repo-git specs-preflight"` there — which runs `specs-git.py start` and prints what it returns. What follows in §3 is the rule that script follows and is tested against, and the fallback the skill names where the script cannot start; it is never a procedure to run by hand beside the script. Parts of it — `phase-handoff.md`'s applications above all — are applied by other steps too, and those steps still read this text: `phase-handoff.md`'s three entry points apply §3.1 to §3.6, and `session-hygiene.md`, the emission references and others cite it besides (`` grep -lE 'specs-repo-git(\.md)?`? §' plugins/*/references/*.md `` lists them).

Runs at run start, once the run key set (§3.2) is known — Phase 0 in most commands. A command
that takes an address and reads its key set from resolution resolves it first, since the set is
what resolution returns (the resolved key, and on an Epic-level folder the key its parent's carrier
asserts), and runs this before any placement or refusal reads the resolved folder; a command that
takes none, or whose key set is the keys `workflows-core:addressing` §1's `read-key` reads off its arguments, or the carrier of the folder an `@<path>` argument names asserts (`workflows-core:addressing` §4) — `/dev-workflows:vuln`'s
per-token keys among them, keyless where no token carries one — runs it as soon as `$SPECS_PATH` is known, and resolves afterwards — having first read the carrier of each key typed as a folder's whole name (`workflows-core:addressing` §1) and of each `@<path>` folder. Where resolution comes first,
a run that stops on its address — `invalid`, `ambiguous`, `misrooted` or `absent` — runs none. In
either order, a run that stops before the preflight on a check of its own inputs needing no specs-repo
state — a run flag, the directory it runs from, a path it reads where it sits rather than as an
artifact of the specs tree — runs none either. Prompt-free.
**Its first act is a line, printed on every run that reaches it, whatever its gate finds**: the `Environment:` line `workflows-core:session-hygiene` §7 defines, `Skill(skill: "workflows-core:reference", args: "session-hygiene env-check")` — `$SPECS_PATH`'s real path and `origin`, and `$REPOS_PATH` — which that section's `env-check` compares before the run writes, so a conversation resumed in another container writes nothing into the specs repository there. Past that line it is
silent when the repository is already clean and on the default branch, no other plugin branch holds a session-file commit §3.4 tries to push or is one §3.4 finds merged, nothing it attempts fails, `status` did not fail earlier in the run either (§2.1), and §3.1 finds
`$SPECS_PATH` well placed; it emits a block only when it acts or when a guard fires, and a
notice only where §3.1 reports a misconfigured `$SPECS_PATH`. That notice is one line, plus one more
line naming anything a misrooted run left behind. On a run carrying `specs_git: misrooted`, one whose `status` could not run in this preflight or earlier in the run (§2.1), or one typed while another run of the session is open on HEAD's branch (§3.5), §3.5 adds
one line where it stays on a branch it would otherwise have left. §3.2's held stage prints a line for each held commit it lands, cannot land or finds stuck, and for each here-form journal it finishes with a commit, and reports a push of `<default>` as §3.4's settle loop reports a push of a branch it settles.

Each report the preflight prints of an attempt that failed (§1 rule 5) is one of its acts: a pull, a push, a deletion, a test that could not run, and the switch §3.5 then leaves undone for it.

### 3.1 Gate

All of: `$SPECS_PATH` is set and is an existing directory;
`git -C "$SPECS_PATH" rev-parse --git-dir` succeeds; and the resolved `.git`
directory is **writable**. Test `.git` specifically, not just the worktree —
`commit` and `fetch` both write there, and a read-only specs mount is a normal
state in this container setup.

**A failed gate is not one disposition but three, and conflating them is what made a misconfiguration indistinguishable from a supported state.**

- **`$SPECS_PATH` is unset → silent no-op here**, past the `Environment:` line (§3). Whether that is a supported state is the caller's to say, and it says so *before* this step: a command that resolves or creates its deliverable's folder in the specs tree by key stops in Phase 0 on the unset variable (`workflows-core:escalation-rules` *Required path environment variable unset*), so it never reaches this gate unset — `grep -lE 'Set SPECS_PATH|Required path environment variable unset' plugins/*/commands/*.md` names them, and `/implement`, `/document` in keyed mode and `/release-notes` are among them for a `<KEY>` address only; a command that writes into a folder it resolves from an address but carries no such stop on the address form it was given — `/implement`, `/document` in keyed mode and `/release-notes` on an `@<path>` address (`implementation.md`; `pr-draft.md` and the implementation-gaps draft; the `release-notes.md` draft) — runs on, writing into the folder given, each having stopped on the variable on a `<KEY>` address instead; a command for which the specs repository holds only its bookkeeping — `/document` in direct mode, `/implement` on a direct prompt, `/upgrade`, `/vuln` on a key or no address (on an `@<path>` address it asks for the variable first, as the first class does), `/docs-init`, `/docs-brand`, `/docs-audit`, the four logging commands and `/diagnose-session` — runs on, and its emitters fall to the report-only tier. Those three classes are every caller of this entry point.
- **`.git` resolves but is not writable → silent no-op**, past the `Environment:` line, exactly as before. The artifacts are going to a report-only tier the plugin does not manage, and a read-only specs mount is a normal state in this container setup. Saying nothing more is correct here: there is nothing for the operator to fix.
- **`$SPECS_PATH` is set to a path that is not a directory, or `rev-parse --git-dir` fails there → emit a notice**, one line naming the variable and the path, then continue: `Specs preflight: SPECS_PATH is <value>, which <is not a directory | is not in a git repository> — nothing this run writes there is committed or handed off; set SPECS_PATH to your specs repository's top level, where it is set, and re-run.` This is **never** a supported state: a set-but-not-a-repository `$SPECS_PATH` is a typo, a missing mount, or a path that was right in another container. Under the old blanket silence it looked identical to the read-only case, so a run would write its deliverables, commit nothing, open no pull request, and end on a terminal gate-failed line that named none of it — the operator's first clue being an empty specs tree some time later. **Where the path is a directory and `workflows-core:addressing` §3 `specs-root-check` finds a signal there, the notice goes on, on the same line, with that entry point's own stop text, in whichever of its forms `workflows-core:addressing` §3 picks — the one-line form, or, where only signal (b)'s second half fired and the walk found no value, the two-readings form, whose second reading names making `<value>` a repository's top level — and adds its left-behind line where it has one: never advice that section rules out.** A `specifications/` directory mounted on its own fails `rev-parse` in exactly this way, because the repository's git directory sits above the mount point. A command that resolves no address never reaches that entry point's stop; where this notice fires, it is how such a command learns the cause.

**A passing gate is tested once more, for a `$SPECS_PATH` set inside the specs tree.** On an ordinary checkout, `$SPECS_PATH=<repo>/specifications` meets all three conditions, because git finds the repository above it. A run that resolves no address would then file its bookkeeping inside `specifications/` with nothing said. Examples are `/upgrade`, `/vuln` on tokens carrying none, `/implement` on a direct prompt, `/document` in direct mode, `/docs-init`, `/docs-brand`, `/docs-audit` and the four logging commands. So **where the gate passes, run the tests of `workflows-core:addressing` §3 `specs-root-check`**, exactly as that entry point defines them, its exclusions included. Where a signal holds, emit a notice naming the variable, its value, which signal holds and the value to set, **set `specs_git: misrooted` for the whole run**, then continue. The notice is the stop's own text. It is one line, with the unsupported-layout clause where that applies, plus one more line naming anything a misrooted run left behind and where it belongs. Like the stop, it moves nothing and gives no commands. A run that resolves no address learns all of it here, and only `commit-artifacts` repeats it, verbatim, at the end of the run (§4 step 1, §6). On an ordinary checkout, `$SPECS_PATH=<repo>/specifications` prints the prefix `specifications/`, which that entry point's first test catches whether or not an earlier run left a nested `specifications/` behind. **It stays quiet at a correct root.** A correct root's own carrier-bearing files, such as a `templates/` folder, a `README.md` or a `docs/` page, fail (b)'s prefix test, whether or not `specifications/` exists yet. A `$SPECS_PATH` like `<repo>/specs` holding `specs/specifications/` prints `specs/`, matches no signal, and draws the notice below instead. A specs repository nothing has been written into yet matches nothing. `specs-root-check` records two unsupported layouts, each with its own reason. The specs root that is itself a subdirectory named `specifications` draws this notice on every run. The specs tree inside a larger repository draws the notice below.

**A `$SPECS_PATH` below its repository's top level.** `$SPECS_PATH` names the root of a dedicated specs repository, the directory that holds `specifications/`. **A specs tree inside a larger repository is unsupported**, because this plugin switches branches and commits in the repository `$SPECS_PATH` belongs to. On a correct root, §3.5 settles and switches its branch at run start, `commit-artifacts` (§4) commits on it, and `workflows-core:phase-handoff` §2 cuts a branch there and commits a deliverable. In a repository that also holds code, each of those would move the checkout of everything else that repository holds, so none of them switches or commits under the flag this notice sets. So where the gate passes and `git -C "$SPECS_PATH" rev-parse --show-prefix` prints a non-empty prefix, emit one notice line, **set `specs_git: misrooted` for the whole run**, then continue (§1). The line names the variable, its value and the repository's top level (`git -C "$SPECS_PATH" rev-parse --show-toplevel`): `Specs preflight: SPECS_PATH is <value>, below the top level of its repository (<top>) — a specs tree inside a larger repository is unsupported, because this plugin switches branches and commits in the repository SPECS_PATH belongs to, so this run switches and commits nothing there; set SPECS_PATH to a dedicated specs repository's top level.` This is a misconfigured `$SPECS_PATH` in §1 rule 7's sense. **Skip it where the inside-tree notice above already fired this run.** That notice names the same path and what to set instead, and, where the value it names is below its repository's top level, that the layout is unsupported. **What a run that stops on `specs-root-check` prints depends on its order (§3).** A command that resolves its address first stops there and runs no preflight, so it prints neither notice, only the stop. A command that runs `specs-preflight` first, on the keys `read-key` reads off its arguments (`/idea`, and `/vuln` on a token carrying a key, among them), prints the inside-tree notice here and then stops at its resolution, so the operator sees the notice and then the stop, which name the same cause.

Still **never fatal** (§1): each notice reports and the run continues. **Where the path is a directory and `specs-root-check` finds a signal there, the non-repository notice above sets `specs_git: misrooted` too.**

**`specs_git: misrooted` is the run-wide record that `$SPECS_PATH` is misplaced, or that the run is no longer in the environment it recorded.** It is set by either notice above; by `workflows-core:addressing` §3 `specs-root-check` where it stops the run at resolution; by `session-hygiene.md` §7's `env-check`, where a run no longer stands in the environment its preflight's `Environment:` line printed, its `Environment changed:` notice being the one that set the flag; by `session-hygiene.md` §6's *Stop*, where a run that keeps a session file finds, at any of that section's three points — on a resume, and on every such run before the deliverable write that leads to the handoff and before the tail's first write — its environment no longer the one the file recorded (`$SPECS_PATH`'s real path, its `origin`, `$REPOS_PATH` or the reference loader's install), or, at the last two, that record unreadable or missing; its stop line, `RESUME_ENVIRONMENT_CHANGED:`, is the notice that set the flag; or by `commit-artifacts` itself (§4 step 1), where the record the run's start made stands (§7) and the `SPECS_PATH` half of the run's `Environment:` line no longer matches the one its preflight printed — `session-hygiene.md` §7's environment change, met at the end. Under it, every emitter of the tail falls to its report-only tier, so the tail writes nothing under a path the run has found wrong, or in an environment it did not record. That covers cost (`cost-emission.md` §8), feedback (`feedback-emission.md` §2), follow-ups (`followup-emission.md` §2) and `resume.md` (`session-hygiene.md` §1). Writing there would only add files §2.1's classifier puts in OTHER, or artifact paths that cannot be staged from `$SPECS_PATH` and that the first run after the variable is fixed would commit in the wrong place: a pending cost there never reconciles, and G1 fires on every run after the variable is corrected.

**The preflight itself performs no write under the flag**: no leftover flush, no push retry, no branch switch, creation or deletion, no pull, no commit and no push. Where the gate passed, it still reads, because `workflows-core:phase-handoff`'s `require-on-main` runs on what it reads. §3.2 runs in full, its best-effort fetch included, which refreshes the remote-tracking refs every `<default-ref>` test reads and moves no checkout. §3.5 classifies the branch, and a row that would switch stays and reports instead. §3.3's guards and §3.4's flush do not run, and each section says why. §4's `commit-artifacts` skips, as it does on `specs_git: blocked`. `workflows-core:phase-handoff` §2.1's `handoff-to-main` refuses the handoff, its §4.3 says so above the consent array, and its row C offers no repair. **So none of `specs-preflight`, `commit-artifacts`, `handoff-to-main` and `require-on-main` switches a branch or commits under the flag.** That bound is those four entry points', not the run's. A command that changes code still cuts its own branch and commits on it in the code repository it changed (`dev-workflows:code-handoff`), and a documentation command does the same in its docs repository. Where the specs tree sits inside that same repository, that branch moves the specs checkout too, which is one reason that layout is unsupported.

**What the flag leaves alone is what the command itself writes.** A run a notice let continue still writes its deliverable where the command puts it, and any of §2.1's single files it writes beside it: `implementation.md`, `pr-draft.md` or the implementation-gaps draft. They stay there, written and uncommitted, for the operator to move or commit once `$SPECS_PATH` is right — or, after `session-hygiene` §6's *Stop*, once the recorded environment is restored and the run re-run, as its stop line says. A run stopped at resolution writes nothing under the path at all. What changes is that the condition is now *said*.

### 3.2 Resolution inputs

**Default branch:** `git -C "$SPECS_PATH" symbolic-ref --quiet refs/remotes/origin/HEAD`,
then strip the `refs/remotes/origin/` prefix. It counts only where
`git -C "$SPECS_PATH" rev-parse --verify --quiet origin/<name> >/dev/null` succeeds for the name it
yields: a remote that renamed its default branch, fetched with `--prune`, leaves `origin/HEAD`
naming a branch the remote deleted, and every test below would then name a ref that does not
exist. If unset, or naming a ref that does not exist, fall back to `main`,
then `master`, then the current branch — in which case no branch switching
occurs at all.

**Default ref — which ref *represents* that branch.** The name above is a branch name; every ancestry and presence test needs a ref. Probe `git -C "$SPECS_PATH" remote get-url origin`: exit 0 with a non-empty URL → `<default-ref>` is `origin/<default>`; anything else → `<default-ref>` is the local `refs/heads/<default>`.

**The two cases are not one weakened into the other.** With a remote configured, its tracking ref is the only trustworthy record of what merged — the local branch can be stale or ahead, so testing against it would assert something the shared history does not support. With **no remote at all** there is no remote state to be uncertain about: the local default branch *is* the default branch, and testing against it is the correct application of the check rather than a relaxation of it. The producer side has always worked this way — `phase-handoff.md` §2.1's push-target probe is headed *"run before the choice, and never gated on"*, and a repository with no `origin` is deliberately not a gate failure there — and this makes the consumer side agree. **Every test below, and `phase-handoff.md` §3's, uses `<default-ref>`; none names `origin/<default>` literally.**

**Freshness:** best-effort `git -C "$SPECS_PATH" fetch origin <default>` before
the ancestry test, skipped entirely when there is no remote. On failure (offline, auth), use the existing local
`<default-ref>` and note `offline — ancestry checked against the
last-fetched ref`. Never fatal. In session-branch mode a second fetch follows,
and the mode is resolved here (§8.1).
The note is carried, not printed — `specs-git.py` returns it as `offline` and `offline_clause` — so the preflight stays silent as §1 rule 7 says; `phase-handoff.md` §3.6 says it where its gate reads against that ref.

**Before the guards, held commits land and `<default>` is pushed — the held stage.** Where the gate passed (§3.1), the run carries no `specs_git: misrooted` and HEAD is on a branch, the preflight settles this worktree's held record (§1 rule 8) here, after the fetch above and before §3.3's guards, so that G1 holds none of it back; under the flag, on a detached HEAD, or where the gate failed, it does nothing. First, each `refs/workflows/held/` ref that no worktree's held record lists is removed — every worktree `git worktree list --porcelain -z` names is read, and a ref whose commit is less than an hour old is left, since another worktree may be about to list it. Then each **here-form journal** (§4 step 1's here form) is finished, only where its move is verified and no `index.lock` stands — where one stands, the entry is left for a later call: with HEAD on the journal's branch and that branch at the tip it journalled, or holding that tip, the index is restored as the here form's second step restores it; with HEAD on the journal's branch and that branch still at the tip the here form moved it from, the here form runs again from the entry's change; otherwise the entry is dropped and the files are left as they stand. Each journal finished with its commit on HEAD's branch prints `Specs preflight: finished the commit an earlier run was making on <branch> when it was cut off: <sha7> (<N> files), that run's own session files, committed apart from another run's`, `<branch>` being HEAD's. **With HEAD on `<default>`, or in session-branch mode (§8)**, every other held entry is then dropped with its ref, its files left to §3.4's flush or §8.2's `commit` — whether or not an `index.lock` stands, since a drop touches neither the index nor a working-tree file. **On any other branch, where an `index.lock` stands**, the stage then lands nothing and lifts nothing, and keeps every other held entry as it is — none rebuilt, landed again or lifted — since the git process holding the lock may be committing on the branch HEAD stands on, which a lift would race: an entry held for a cause that will not pass prints its stuck line below; a landing journal whose move is verified, read from the local refs alone (`<default>`, or `origin/<default>` for a commit pushed by refspec), prints nothing, since its commit is on `<default>` already and only its lift waits, as a here-form journal waits; and every other entry, an unverified landing journal included, prints the could-not-commit line below with §6's `locked` reason clause, `<path>` the lock's path, its tail the first alternative. A later run settles them as this paragraph says once the lock is gone. **On any other branch where none stands**, each held file changed since it was held — edited, committed, removed or restored — first leaves its entry, which is rebuilt without it, an entry left with no file being dropped (§3.4's flush commits such a file where it is still dirty); then, oldest first: a **landing journal** is lifted where its move is verified — `<default>` holds the tip it journalled, or, for a commit pushed by refspec, `origin/<default>` holds it once fetched — and is otherwise landed again as a held entry, never lifted unverified, since that lift would write back over a change that is nowhere else; an entry held for a cause that will not pass prints, on every run until it is dropped, `Specs preflight: the session files an earlier run held for <default> cannot be committed there: <reason clause>; they stay in your working tree, and no landing takes them; dropping the hold — as a later run on <default> or in session-branch mode does, or as you can — leaves them ordinary uncommitted files, which a later commit takes: see their change with 'git -C "<SPECS_PATH>" show <sha7>', put it on <default> yourself if you want it there, then run 'python3 "<specs-git.py's path>" --specs "<SPECS_PATH>" land --default-ref <default-ref> --drop-held <sha7>'`; and an entry held for a cause that passes is landed as §4 step 1 lands a change, its files lifted as that step's lift says, printing, `<branch>` being HEAD's, `Specs preflight: committed <sha7> (<N> files) on <default>: the session files an earlier run held for it, now committed without leaving <branch> and taken out of your working tree there` — save where it is held again, which prints `Specs preflight: could not commit the session files an earlier run held for <default> (<reason clause>); they stay in your working tree, <and the next run tries again | and the next run, in session-branch mode, drops this hold and commits them as that mode commits session files>` — the second where its reason clause is `checked-out`'s fifth or sixth alternative (§6), whose next run is in session-branch mode, where this stage drops the hold (above) and §8.2's `commit` takes the files — and keeps held behind it, with the same cause and the same line, every later entry that shares a path with it. In these lines `<reason clause>` is §6's landing reason clause for the entry's cause, `<sha7>` the held commit's first seven characters, and `<specs-git.py's path>` `scripts/specs-git.py`'s own resolved path. `start` checks its time budget before each entry's capped calls, and where the budget would run out it stops here, its `next` resuming at this stage, which keeps as they are, and prints nothing for, the entries this start has already tried and reported held again or stuck — an entry rebuilt since, without a file changed between two of this start's calls (above), counting as the entry it was; each one held again still holding back, with its cause, the later entries that share a path with it, as on the first pass, and a stuck one holding nothing back — so a start spends its budget on each entry at most once. Each path a lift writes back is updated in the run's snapshot (§7) to the version written back, and leaves the snapshot where that version is HEAD's. By hand, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" --specs "$SPECS_PATH" land --default-ref <default-ref> --retry-held`, with `--register-rebuild <path>` where the run has one (§7), runs this stage up to the push below and prints `{landed, finished, failed, stuck, dropped, error}`, from which the lines above are read.

**Then, outside session-branch mode, where HEAD is not on `<default>`, `<default>` is pushed** where it holds commits a push would publish (§4 step 5's `push-scope` measure) and all three of step 5's conditions hold for it, `start`'s budget checked first, printing §3.4's `Specs preflight: pushed <N> session-file commit(s) left on <default>`. A push step 6 reports as failed prints step 6's line for it, as §3.4's settle loop does for a branch the run is not standing on, and a push `origin` rejects as non-fast-forward goes at once to step 6's replay, run as `specs-git.py replay --for start --branch <default>`, which moves `<default>` by `update-ref` alone, since no checkout here stands on it, and whose own `next` resumes at the guards. So a landing whose push failed is retried even while G1 keeps ending the preflight, which §3.4's retry and settle loop, run only past the guards, never reach.

**Run key set:** every key the run is scoped to — the identity each of this run's own branches is
*named for* — taking each key already resolved at the call site. A PRD-scoped run contributes its
PRD key. An **Epic-scoped** run — one whose single address resolved an `EPIC-` folder, on any
command that accepts an Epic address — contributes **both**, because the Epic's key encodes its
ancestry: the Epic is as much this run's key as the PRD is. Whether the run also *reads* the PRD
from the folder above is the command's own business, and not every one does — `/frames` does not (it
indexes what the resolved folder holds and never looks up) — so ancestry alone carries the PRD key,
which is enough, because what the second key is for is §3.5 recognising a branch named for either
(§3.6). Two keys in the set, one address on the command line (D4). When no key is resolved at the
call site the set is empty and the run is **keyless**. Both are correct behaviour — a command runs
its preflight once its key set is known (§3), and never defers it further to obtain a key some later
phase would mint.

**`/create-prd` contributes a key, and the rule does not read the route.** The
positional token is validated by that command's own Phase 0 **step 1**, before the
preflight at step 2b runs, and the folder it resolves is a `PRD-` folder on both
routes — the one the operator named on the `/idea` route, the `PRD-` slice
`/brd-split` carved on the BRD route. Either way the deliverable is written into
that folder and `handoff-to-main` names `prd/<KEY>-<slug>` for it, so the run
contributes that key. There is no per-route classification left to get wrong: no
`/create-prd` run is keyless, and none is treated as though it were.

**Neither route may be classified keyless, and the failure is the same one.** With
an empty key set B3 can never be satisfied, so §3.5's branch reuse fails: a run
interrupted after its branch exists takes **B4** on its own in-progress branch and
switches away, `${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md` §2.2 rule 3
cannot resolve `branch-key` into an empty set, and rule 4 appends `-2` — the
self-duplication §3.5 documents and fixes. The `/idea` route was once described as
"structurally keyless, its key minted by the handoff in a later phase" and the BRD
route as keyless for conservatism; no handoff mints a key now, and both
descriptions produced that same duplicate branch. What genuinely stays keyless is a
run that resolved **no** key at all at its call site — not a route.

**The contributed key is a folder identity, and contributing it widens no tracker
identity.** This set exists to match branch names in §3.5 and nothing else, and a
longer key is matched here exactly as a shorter one is (§3.5,
*A two-segment key resolves exactly as it did before*). The PRD's own `key`
frontmatter is written by `/create-prd`, on both routes, and is set to that same
resolved folder's key — a three-segment slice key included
(`${CLAUDE_PLUGIN_ROOT}/references/prd-format.md`). `/create-prd` copies it and mints
nothing, no handoff writes it, and it fixes no depth.

**This run key set is the preflight's, and only the preflight's.** It exists to
match branches in §3.5 and is resolved at the *start* of the run.
`commit-artifacts` resolves its own key independently — a single key, at the
*end* of the run (§4 step 4) — by which point a command that started keyless may
well have one. A run that is keyless here is not thereby committing under
`NOISSUE`.

### 3.3 Stage 1 — guards

Not run on a run carrying `specs_git: misrooted` (§3.1). Each guard's notice tells the operator what this run's `commit-artifacts` will or will not commit, and under that flag it commits nothing, whatever a guard would find; §3.1's notice has already said why. A detached HEAD is still caught: `commit-artifacts` and `handoff-to-main` refuse on the flag, and `workflows-core:phase-handoff` §3.3 row I tests the state itself. The preflight goes on from §3.2 to §3.5's classification, skipping §3.4 too.

**Any match ends the preflight; the run proceeds.** Every guard emits the §5
notice, never a quiet line.

| # | State | Action |
|---|---|---|
| G0 | **HEAD is detached** | **Hand off, and set `specs_git: blocked` for the whole run** — `commit-artifacts` (§4) must also skip. §5 notice at **blocking** severity. See §3.7. |
| G1 | Any dirty **OTHER** path (§2.1) | **Hand off** — no commit, no branch switch, no push. §5 notice at **advisory** severity, listing the paths. Those files are not the plugin's, and switching branches would carry them. **This does NOT set `specs_git: blocked`**: the terminal `commit-artifacts` still runs, because it stages only artifact paths and is safe beside unrelated dirt. Losing the artifacts to protect files the step never touches would be the worse failure. Where the run stands on a plugin branch it would have left, it takes §4 step 1's landing onto `<default>` instead, without moving the checkout (*G1 on a branch the run would have left*, after this table). |
| G2 | On a **named** branch that is neither the default branch nor a match for `^(idea\|prd\|ard\|spec\|epics\|design\|ready\|brd\|frames\|kb\|conformance)/` | **Leave it; stay on it.** §5 notice at **advisory** severity, naming the branch, so the user knows where this run's artifacts will land — on that branch, or, on a direct `/dev-workflows:implement` run from inside the specs repository, on the code branch the run cuts (§5). The commit is safe — a named branch cannot be lost — so `commit-artifacts` proceeds, and leaves its commit unpushed (§4 step 5). The plugin manages only branches it created (§2.2). In session-branch mode the commit lands on the session branch instead, and is pushed (§8). |

**G1 on a branch the run would have left.** Outside session-branch mode (§8), where G1 fires with HEAD on a plugin branch (§2.2), the preflight asks before it ends there what §3.5 would have asked of the branch, each a read that moves nothing: `branch-merged HEAD` (§3.5), and `branch-key` (§3.5) against the run key set (§3.2) with the commit key the run's start was given beside it. Where the branch reads merged, or no key of either names it, the run's state record (§7) keeps the branch as a stay — its kind `merged` or `unkeyed`, or `mid-run` under a run typed mid-run (§3.5), its `merged` flag the ask's answer, its reason G1 — so `commit-artifacts` takes §4 step 1's landing onto `<default>`, without moving the checkout, and G1's notice takes its landing form (§5). Where the ask cannot answer, §3.5's report says so, once, and the branch reads unmerged. Under a run typed mid-run (§3.5), G1's notice takes its mid-run form (§5) instead, whatever the stay's kind, and whether or not a stay is kept. A run that follows this text by hand keeps in its conversation the stay its last preflight kept, this one or any other §4 step 1 names — each preflight derives its own, so a re-run's (§3.5) starts with none — and its `commit-artifacts` lands as §4 step 1 says; a run whose start the script ran, and whose end it follows by hand, takes the stay from the `stay` field of its last `start` call's JSON, the snapshot from its `start_dirty` field and the open run it was typed under (§3.5) from its `midrun` field.

### 3.4 Stage 2 — flush leftovers

Always runs when stage 1 matched nothing **and the run does not carry `specs_git: misrooted`** (§3.1). Under that flag it does not run at all, so there is no flush and no push retry, and the preflight goes on to §3.5, which switches nothing under the flag. A flush there would `git add` paths that porcelain prints relative to the repository's top level and that do not exist from `$SPECS_PATH`, which fails with exit 128 on every run. Where `$SPECS_PATH` is a correct root holding a stray folder, it would commit and push while the notice says the run wrote nothing.

**Under a run typed mid-run (§3.5) it moves nothing under the open run.** It commits no dirty file on HEAD, since each may be that run's work in progress, makes neither the catch-up nor the merged-branch leave below, and retries no push of HEAD's branch; the settle loop runs as always. Those files are the open run's terminal commit's to take. Outside session-branch mode, this run's end takes §4 step 1's landing or its here form, apart from them, where HEAD stands at its end on the branch it started on — and commits nothing where its start took no snapshot and that run still stands, since nothing then tells the two apart (§3.5); where the run's own handoff has moved HEAD off that branch, the end goes on as for any run whose HEAD moved (§4 step 1).

**On the default branch, catch up first.** Where HEAD is on the default branch (§3.2), `<default-ref>` is `origin/<default>`, and HEAD is strictly behind it — `git -C "$SPECS_PATH" merge-base --is-ancestor HEAD <default-ref>` succeeds and `git -C "$SPECS_PATH" rev-parse HEAD` differs from `git -C "$SPECS_PATH" rev-parse <default-ref>` — run `git -C "$SPECS_PATH" pull --ff-only --no-rebase origin <default>` before either case below. In session-branch mode (§8) the catch-up is wrapped in `lift` and `put-back` (§8.3). `--no-rebase` is required: a `pull.rebase` setting would otherwise make the pull a rebase, which §1 rule 4 forbids and which refuses to run beside a modified artifact. The catch-up is silent where it succeeds; where it fails, print `Specs preflight: could not fast-forward <default> (<git's first error line>); the run goes on from it as it stands`, the parenthesis reading `the pull did not finish within 60 s` where `specs-git.py`'s 60 s cap on the pull ended it, and continue on the branch as it stands. §4 step 2 runs it again before staging, for a run whose preflight ended at a guard or never ran. Before a push, nothing else here brings the default branch up to date while a run stands on it — §3.5's B1 does nothing, and only B2 and B4, which switch to it, pull — so without it a run's commit would land on a stale base, and its push would be rejected as non-fast-forward, left to §4 step 6's replay, which moves the checkout and settles the push only where every condition it tests holds. A default branch holding commits the remote lacks is ahead or diverged, never behind, and no fast-forward applies to it; a diverged one is §4 step 6's case: where its push is rejected, step 6 replays the run's session-file commits onto the remote's branch, or names what to run where it cannot, save where another session switched the checkout during the move.

**On a merged plugin branch, leave it before the flush.** Outside session-branch mode (§8), where HEAD is a plugin branch (§2.2) and dirty ARTIFACT paths exist, ask `branch-merged HEAD` (§3.5) before the first case below. Where it answers merged, run B2's action (§3.5) now, with its reports — switch to the default branch, `pull --ff-only --no-rebase origin <default>` where `<default-ref>` is `origin/<default>`, `branch -d` — and the first case below then commits on the default branch, which §3.5 classifies as B1. The switch carries the dirty session files across: one a run wrote new is untracked, and git carries a modified one wherever the default branch holds the same version of it as HEAD. Where git refuses the switch — a session file the two branches hold differently, `resume.md` the likeliest — print `Specs preflight: could not switch from merged <branch> to <default> (<git's first error line>)`, flush on the branch as below, and, where the flush commits, print `Specs preflight: <branch> is merged, and this flush committed <sha7> on it, which no run pushes; to land it, standing on <default>, run git -C "<SPECS_PATH>" cherry-pick <sha7>`. Without this, the flush commits on the merged branch first, and that commit makes every `branch-merged` test read unmerged (§3.5), so B2 never fires, and the commit stays on a branch whose remote the merge deleted, which §4 step 5 never pushes. The terminal commit keeps off the branch the same way: where the preflight stayed on a merged plugin branch — §3.3 G1 fired, `status` could not run (§2.1), git refused this switch or B2's, or the preflight stopped early before it (§1 rule 5) — and HEAD still stands there at the run's end, `commit-artifacts` takes §4 step 1's landing onto `<default>`, which commits nothing on the branch and lifts out of the working tree the session files it lands, so the branch keeps reading merged and a later run's B2 removes it. Where git refused this switch and the flush below then committed on the branch, the branch reads unmerged until that commit lands on `<default>` by the cherry-pick its line names, and a later run's leave waits for that. In session-branch mode the flush commits nothing on HEAD (§8.2), so there is nothing to leave first, and no such stay is kept.

- **Dirty ARTIFACT paths exist** → commit them **onto the current branch** (they
  belong to the run that wrote them, and such a run stood on this branch: a run that had to stay on a branch it would have left took §4 step 1's landing onto `<default>` instead, and what that landing held this flush leaves out, below) and push where §4 step 5 allows it, per §4
  steps 2–6, which print no §6 line here: where step 4 finds nothing to commit,
  or step 5 pushes nothing, the flush ends silently. A push `origin` rejects
  as non-fast-forward goes to step 6's replay, which prints its line here in
  `Specs preflight:` form whatever it did, a push included (step 6).
  The flush leaves out every file of a held entry (§3.2) whose working copy is still the version the entry holds, and such files alone count as no dirty ARTIFACT path, here and for the merged-branch leave above. A held file changed since it was held is committed here as it stands — its entry rebuilt without it by the held stage, or, where an `index.lock` kept the held stage from rebuilding it, once this commit is made — with the line `Specs preflight: <path> changed after an earlier run held it for <default>, so it is committed here as it stands, and left out of the held commit`.
- **No dirty ARTIFACT path** → where the current branch holds commits a push
  would publish and all three of §4 step 5's conditions hold, **retry the
  push**, a non-fast-forward rejection going to step 6's replay as above;
  where one fails, nothing is retried and nothing is printed. Stage 1
  has already ended the preflight on every branch step 5's first condition
  refuses (§3.3 G2), so the other two decide here, and a specs repository with
  nowhere to push never retries.

  **`push-scope` never reads `@{u}` directly.** A failed `push -u` sets no
  upstream, so `git rev-parse --abbrev-ref '@{u}'` and
  `git rev-list --count '@{u}..HEAD'` both exit 128 with `fatal: no upstream
  configured` — the condition is not false but *unevaluable*, and precisely in
  a state a retry exists for: a branch a failed `push -u` left with no
  upstream — the default branch, or the session branch (§8.4), since a plugin
  branch `origin` does not have is never pushed (§4 step 5) — which strands an
  artifact commit with nothing to retry it.
  Step 5's base reads no upstream at all: it tests
  `refs/remotes/origin/<branch>`, which a failed `push -u` leaves absent, and
  falls through to the remote's refs. Without a test that answers there, a push that
  failed in a previous run leaves a local commit that nothing ever retries — the
  original defect, re-created one layer up.
- **In session-branch mode** (§8) the two cases are one, since the overlay
  keeps session files dirty: commit through §8.2, which finds nothing new
  where the dirty files are the overlay alone, then push the session branch
  where it holds commits a push would publish and step 5's conditions hold
  as §8.4 states them. Where §8.2's `commit` printed `created: true`, it
  created the session branch in this clone, and the preflight says so:
  `Specs preflight: created local session/<identity> at <base short sha>; no session file to commit yet`
  where its `committed` is `null`, and otherwise
  `Specs preflight: created local session/<identity> at <base short sha>, and committed <sha7> on it`,
  `<base short sha>` as §8.2 takes it, and `<sha7>` the first seven
  characters of `committed`. Nothing else is printed, save step 6's
  failure lines — among them §8.4's rejection of the session branch, in
  §6's `Specs preflight:` form, which, where it takes its conflict ending,
  goes on with §6's clause for the paths that `sync.conflicts`, from this
  flush's `commit`, gives the source `origin/session/<identity>`.

**Then, either way, settle every other local plugin branch.** List them with
`git -C "$SPECS_PATH" for-each-ref --format='%(refname:lstrip=2)' refs/heads/`
and keep those §2.2's pattern matches, less the current branch and any branch
the merged-branch leave above already reported this run.
The default branch is never on that list: where HEAD is not on it, §3.2's held stage pushes it, before the guards.
Ask each
`branch-merged` (§3.5) first. **Where it answers merged by its first test,
ancestry, and `branch -d` can see that** — the branch's upstream
(`git -C "$SPECS_PATH" for-each-ref --format='%(upstream)' refs/heads/<branch>`,
which prints the configured name even where that ref has been pruned) is a ref
that exists — `git -C "$SPECS_PATH" rev-parse --verify --quiet <upstream>` prints
an id — and holds the branch's tip
(`git -C "$SPECS_PATH" merge-base --is-ancestor <branch> <upstream> 2>/dev/null` exits 0),
or, where it has none or the `rev-parse` prints nothing, `HEAD` holds it
(`git -C "$SPECS_PATH" merge-base --is-ancestor <branch> HEAD 2>/dev/null` exits 0), git's
own test — **delete it as B2 deletes:**
`git -C "$SPECS_PATH" branch -d <branch>`, then remove its push-refusal record
where one stands (§1 rule 8), and print
`Specs preflight: deleted merged <branch>`. Where `-d` still fails — a worktree
has the branch checked out, say — print `Specs preflight: could not delete merged <branch> (<git's first error line>)` and skip, **never
`-D`**; a config error is not that failure, and B2's line naming the
configuration the branch left behind applies as B2 states it. **Where it
answers merged otherwise** — by a rebase, a squash or its content, or by
ancestry that `-d` cannot see from where the run stands — delete nothing and
print `Specs preflight: <branch> is merged into <default>, which git branch -d cannot see from here — delete it with git -C "<SPECS_PATH>" branch -D <branch>`,
with B2's `rm -f "<record>"` after it where the branch's push-refusal record
stands, at most once per run for that branch, however many times the run's
preflight runs. A merged
branch is never pushed. Without this, a merged plugin branch the run is not
standing on stays for good, and `phase-handoff.md` §2.2 rule 4 names every
later branch for its key with a suffix. Test each branch `branch-merged`
leaves unmerged in this order, stopping at the first that fails: it holds
commits a push would publish (§4 step 5's `push-scope` measure, which on most
branches finds none and ends the test there); and all three of step 5's
conditions hold for it. Where both hold, push it as step 5
does — a push names its branch, so it needs no switch — and print
`Specs preflight: pushed <N> session-file commit(s) left on <branch>`. Where a
test fails, nothing is pushed and nothing is printed. A push step 6 reports as
failed prints step 6's line for it, which names the switch to `<branch>` its
remedy needs, since the run is standing on another branch. A push `origin`
rejects as non-fast-forward goes to step 6's replay, which moves `<branch>`
by `update-ref` alone, since no checkout here stands on it, refuses where
another worktree has it checked out, and prints its line either way.
Each branch the loop meets whose push `origin` rejects as non-fast-forward is replayed only after the loop has settled every other branch, in the order the loop met them, each replay in a Bash call of its own.
Without this, a
commit stranded on a branch the run is not standing on is never retried: B4
below switches away from a plugin branch keyed to no key of the run right after
the flush above committed on it, so a flush whose push failed leaves its commit
there, and every later run starts somewhere else.

Either way, continue to stage 3 — in session-branch mode with the overlay in place, which §8.3 lifts around each move — with a clean tree, save in two cases: where the flush's commit was Locked or failed (§4 step 6), the session files stay dirty, and git may refuse §3.5's switch over them, a failure rule 5 reports (§1); and where `status` could not run (§2.1), the dirty set is unknown, so §3.5 switches nothing.

### 3.5 Stage 3 — branch disposition

First matching row applies.

| # | State | Action |
|---|---|---|
| B1 | On the default branch | Nothing further. |
| B2 | Plugin branch, and `branch-merged HEAD` (below) finds it merged | Switch to default, `git -C "$SPECS_PATH" pull --ff-only --no-rebase origin <default>` where `<default-ref>` is `origin/<default>`, as the catch-up in §3.4 names it (`--no-rebase` for the reason that catch-up gives; with no `origin` there is nothing to pull), `git -C "$SPECS_PATH" branch -d <branch>`, then remove `<branch>`'s push-refusal record where one stands (§1 rule 8), and print §3.4's `Specs preflight: deleted merged <branch>`. If `-d` fails, print §3.4's could-not-delete line and skip — **never `-D`**. **A config error is not that failure**: where git cannot write `.git/config` — a container that mounts it read-only — `-d` deletes the branch and exits 0, then prints `could not write config file` (or `could not lock config file`) and `warning: update of config-file failed`, having tried to rewrite the configuration whether or not it held a `branch.<branch>` section. The branch is gone, so the deletion is reported as done, with nothing about the error. A branch pushed from that container has no such section, since `-u` could not record one (`phase-handoff.md` §2.5); one a `push -u` from a writable checkout recorded stays behind, and a later branch of the same name inherits its upstream. So may the record's older form, `branch.<branch>.workflowsPushRefused`, which a later branch of the same name would read as a refusal — and the inherited upstream is the one step 5 of §4 reads as *the remote deleted the branch*, so either would keep that later branch from being pushed. Where `git -C "$SPECS_PATH" config --get branch.<branch>.merge` or `… --get branch.<branch>.workflowsPushRefused` still prints after the deletion, B2's report adds `Specs preflight: <branch> left configuration this container cannot remove — run git -C "<SPECS_PATH>" config --remove-section branch.<branch> where .git/config is writable`. Where `branch-merged` answered by its second, third or fourth test, a rebase or a squash, git may not see the merge — `-d` deletes a branch merged into its upstream, or into `HEAD` where it has none, and refuses one merged only by a rebase or a squash — so the report then adds the command for the user to run once they are sure: `Specs preflight: <branch> is merged into <default> by a rebase or a squash, which git branch -d cannot see — delete it with git -C "<SPECS_PATH>" branch -D <branch>`, and where `<branch>`'s push-refusal record stands (§1 rule 8), `rm -f "<record>"` after it, since `branch -D` no longer takes the record with it. If `pull --ff-only` fails (the local default branch has diverged), print §3.4's catch-up failure line and continue on default **without** pulling — never merge, rebase, or reset. |
| B3 | Plugin branch, unmerged, `branch-key` (below) resolves the branch to **any** key in the run key set (§3.2) | **Stay on it.** See §3.6. |
| B4 | Plugin branch, unmerged, `branch-key` resolves the branch to **no** key in the set, or the set is empty (keyless run) | Switch to default, `git -C "$SPECS_PATH" pull --ff-only --no-rebase origin <default>` where `<default-ref>` is `origin/<default>`, as B2 pulls, a failed pull printing §3.4's catch-up failure line. **Leave the branch and its pull request alone.** Report it: `Specs preflight: left <branch> for <default>, since no key of this run names it — the branch and its pull request are as they were`, followed, where it still holds commits a push would publish (§4 step 5's `push-scope` measure), by `; <N> commit(s) on it are not on origin, and a later run's preflight pushes them where §4 step 5 lets it` (§3.4). |

**In session-branch mode** (§8), B2's and B4's switch and pull, and the re-run's switch back below, are each wrapped in `lift` and `put-back` (§8.3), and the preflight ends with `put-back`. HEAD on the session branch is not a row's subject: G2 has already kept the run there.

**Where no local `<default>` exists**, B2's and B4's switch — and §3.4's merged-branch leave, which takes B2's action — first creates it at `<default-ref>` with `git -C "$SPECS_PATH" update-ref refs/heads/<default> <the commit <default-ref> names> <the null id>`, which writes no configuration; then sets its upstream with `git -C "$SPECS_PATH" branch --set-upstream-to=origin/<default> <default>`, best-effort, where `.git/config` can be written, leaving it unset with no word where it cannot; and only then switches, with `--no-guess`. A switch left to make the branch itself, by git's `--guess`, writes that upstream as it switches, and where `.git/config` cannot be written — a hardened container mounts it read-only (§1 rule 8) — git moves the index and the working tree onto `<default>`'s tree, leaves HEAD on the branch and exits 1: a staged reversal of the branch's work, which would read as a switch refused with nothing moved (measured on git 2.43, with `.git/config` held locked). So no switch here makes a branch from a remote's copy, and neither `checkout.guess` nor `checkout.defaultRemote` has a say in it; where `<default-ref>` names no commit, nothing is created and the switch is refused. Where git refuses the switch (below; for §3.4's leave, §3.4's own refusal, above), the checkout is unmoved and the local `<default>` stays at `<default-ref>`, holding nothing a push would publish, and §4 step 1's landing builds on it as on any local `<default>` not behind `<default-ref>` ((2)). Outside session-branch mode §4 step 1's landing creates a missing local `<default>` too, at the commit it lands, without moving the checkout (§4 step 1 (3)).

**Where git refuses B2's or B4's switch**, the preflight stops early (§1 rule 5), and before that stop's report the run's state record (§7) keeps the branch as a stay — kind `merged` for B2's, `unkeyed` for B4's, its `merged` flag set for B2's alone, reason `refused` — so `commit-artifacts` takes §4 step 1's landing onto `<default>`, without moving the checkout. Outside session-branch mode only: in the mode the session files never commit on HEAD (§8.2), and no stay is kept.

**Merged — `branch-merged <ref>`.** Whether the work on a branch is on the default branch, asked against `<default-ref>` (§3.2). B2 asks it of `HEAD`, as §3.4's merged-branch leave does before the flush, and as §3.3's G1 and a preflight that stops early (§1 rule 5) do of a plugin branch they end on, and `commit-artifacts` of the one a start that never finished its preflight left HEAD on (§4 step 1's landing); §3.4's settle loop of each branch it lists; `phase-handoff.md` §2.2 rule 3 of the ref it resolves; `session-hygiene.md` §1 of each specs-repository branch an item of the resume pointer it overwrites names; `/dev-workflows:conformance` of each other `conformance/` branch, local or under `origin/`, whose copy of a record never reached the default branch and which changed that record after it forked; `/product-workflows:brd-split` of the handoff branch and of the commit Phase 6's handoff pushed, recorded at Phase 7; and `/product-workflows:update-spec` of each `spec/`, `design/` or `conformance/` branch, local or under `origin/`, that changed the specification since it forked. Ask it with `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" --specs "$SPECS_PATH" branch-merged --ref <ref> --default-ref <default-ref>`, which prints `{"merged": true|false, "test": 1|2|3|4|null}` — `test` the first of the four tests below that held, `null` where none did. Where it exits 2 — a ref that does not resolve among its causes — report the first line of its stderr and read the branch **unmerged**, the answer that never deletes a branch — save `commit-artifacts`' own ask (§4 step 1), which reads it unmerged with no report: unmerged leaves that step as it was before the ask, committing where HEAD stands, which its outcome line names, and a report there would put a line about a test that changed nothing before the run's one outcome line. Inside this preflight — B2, §3.4's merged-branch leave, §3.4's settle loop, and the asks of §3.3's G1 and of an early stop — that report is `Specs preflight: could not tell whether <branch> is merged (<the first line of its stderr>), so it reads unmerged`, printed once for a branch in a run, however many of those asks fail. The script runs these four tests in order; the first that holds answers **merged**, and none holding answers **unmerged**:

1. **A merge or a fast-forward:** `git -C "$SPECS_PATH" merge-base --is-ancestor <ref> <default-ref> 2>/dev/null` exits 0.
2. **A rebase merge:** `git -C "$SPECS_PATH" cherry <default-ref> <ref>` prints at least one line, every line it prints begins `-`, which marks a commit whose change the default branch already holds under another commit, and `git -C "$SPECS_PATH" rev-list --merges <default-ref>..<ref>` prints nothing. `cherry` passes over merge commits, so a branch whose only change of its own sat in a merge commit would otherwise read merged, and B2 would name `branch -D` on it.
3. **A squash merge:** with `<base>` from `git -C "$SPECS_PATH" merge-base <ref> <default-ref>`, the patch id of the branch's whole change, the first field of `git -C "$SPECS_PATH" diff --no-renames <base> <ref> | git -C "$SPECS_PATH" patch-id --stable`, is the first field of a line of `git -C "$SPECS_PATH" log -p --no-renames --no-merges <base>..<default-ref> | git -C "$SPECS_PATH" patch-id --stable`, the default branch's own commits since. An empty change has no patch id and is never found merged this way.
4. **Its content is on the default branch:** the branch's whole change is not empty — `git -C "$SPECS_PATH" diff --quiet <base> <ref>`, `<base>` as in test 3, exits 1 — and merging `<ref>` into `<default-ref>` changes nothing: `git -C "$SPECS_PATH" merge-tree --write-tree <default-ref> <ref>` exits 0 and the first line it prints is the tree id `git -C "$SPECS_PATH" rev-parse "<default-ref>^{tree}"` prints. It writes objects and moves no ref, index or file, the same checkout-free merge §8 requires; a git whose `merge-tree` lacks `--write-tree` exits non-zero, and the test reads unmerged, as before it existed.

**Why the fourth test.** Tests 2 and 3 compare patch ids, and a patch id hashes each hunk's context lines. A squash or rebase merge whose commit landed after the default branch changed a line within three lines of one of the branch's hunks carries different context, so its patch id differs and both tests read unmerged, for good — reproduced on a 30-line file whose branch changed line 10 while the default branch changed line 12 before the squash, where the same squash after a change to line 25 matched. Test 4 asks what those two approximate — whether the work is on the default branch — by content, which context drift cannot defeat; it holds there, and reads unmerged on the same branch before its squash. It still reads unmerged where the default branch has since changed again a line the branch changed, and where the merge needed a conflict settled by hand: either way merging the branch would change the default branch, so it is not shown merged. It also reads merged where the default branch holds the same change from another source — a stacked branch's change landed by the pull request it was stacked under — which is the work being on the default branch, the question this entry point asks.

Ancestry alone was the test, and a pull request merged by squash or by rebase never passes it: the branch read unmerged forever, so B3 kept a resumed run on a branch whose pull request had closed, and the handoff reused it and called `gh pr create` on it. All four tests read the branch at its tip, so a commit of its own made on it after its pull request merged can make it read unmerged again — save where tests 2 to 4 still find that commit's change on the default branch; where it does read unmerged, §4 step 5's deleted-branch state reports that commit's push rather than letting it recreate the branch.

**Under `specs_git: misrooted` (§3.1) the table classifies and moves nothing.** Take the first matching row exactly as above: §3.2's fetch has already refreshed `<default-ref>` for B2's merge test, and `branch-key` below resolves B3 and B4 unchanged. Then act on that row without writing. B1 and B3 stay where they are, as they always do. B2 and B4 stay too, with no `switch`, no `pull --ff-only` and no `branch -d`. Each prints one line in place of its action: `Specs preflight: staying on <branch> — specs_git: misrooted, so no branch is switched (it would have <switched to <default> and deleted it, as it is merged | switched to <default>, as no key of this run names it>)`. A B3 here keeps the checkout on the caller's own branch exactly as it does on a correct `$SPECS_PATH`, so `workflows-core:phase-handoff` §3.3 row B still passes a resumed run whose branch changed the artifact while the default branch has not, and row B′ still stops one where the default branch changed it since the fork. Where HEAD is on no plugin branch, no row applies here, as always.

**Where `status` could not run in this run (§2.1)**, the dirty set is unknown, so G1 (§3.3) could not keep a switch from carrying files that are not the plugin's: the table classifies and moves nothing, as under `specs_git: misrooted`, and B2 and B4 each print `Specs preflight: staying on <branch> — the uncommitted paths could not be listed, so no branch is switched (it would have <switched to <default> and deleted it, as it is merged | switched to <default>, as no key of this run names it>)` in place of their action. Outside session-branch mode each also keeps the branch as a stay (§4 step 1) — kind `merged` for B2's, `unkeyed` for B4's, or `mid-run` for either under a run typed mid-run (§3.5), reason `unlisted` — so `commit-artifacts` takes §4 step 1's landing onto `<default>`, without moving the checkout; that step says what a landing carries where the run's start could list no paths.

**A run typed mid-run.** A command typed while another run of the same session still stands open on the branch HEAD is on — another command's, or its own command's with another run key set (*The same command typed twice*, below): **the open run** — must neither switch that branch away under it nor commit its work in progress — the preflight and the end of such a run do neither, save where its own handoff has moved the checkout off that branch, where its end goes on as for any run whose HEAD moved (§4 step 1), and save what nothing tells from this run's own change: what the open run writes after this run's start to a session file it had no uncommitted change in at that start, and each entry it appends after it to a block-shaped file or `follow-ups.md`, go with this run's change, while an overwritten file, a record or a register already uncommitted at that start is never part of the change, whoever writes it, and stays in the working tree for a later commit on the branch (§4 step 1 (1)). At a run's first `start`, before §3.2's fetch, the script reads this session's records (§7) but the run's own — every other command's, and its own command's where their run key set and this start's differ, both holding a key (*The same command typed twice*, below) — a parked one among them, which the test below passes only while it still protects, since a restart marks it `protects: false`; a re-run reads none, and carries the open run its first start found (*A re-run in the same run switches back first*, below) — save one that finds no record of its own, which reads them as a first start does (below). A record is an open run where all of these hold: a start of `specs-git.py` made it, not a declined handoff alone; that start set no `specs_git` flag, since a misrooted or blocked run commits nothing at its end and so protects nothing; it stands at `done` or at one of `start`'s own stages, and holds no `end_commit`; it is not marked `protects: false`; its repository's top level is this run's; it started within the last 7 days; and HEAD's branch is the branch it recorded, or one `branch-key` resolves to a key of its key set — an open run that handed off onto its own branch. Where one is open, this run is **a run typed mid-run**, and its record names the open run (`midrun`):

- §3.4's flush commits no dirty file on HEAD and moves nothing under the open run (§3.4).
- B2 and B4 stay, each printing in place of its action `Specs preflight: staying on <branch> — <command>'s run in this session is still open on it, so no branch is switched (it would have <switched to <default> and deleted it, as it is merged | switched to <default>, as no key of this run names it>)`, `<command>` the open run's, and, outside session-branch mode, keep the branch as a stay — kind `mid-run`, its `merged` flag B2's answer, reason `mid-run` — so this run's own change (§4 step 1 (1)) takes §4 step 1's landing onto `<default>`, its push as any landing's, the overwritten files uncommitted at its start left where they are — where HEAD still stands on that branch at its end; where the run's own handoff has moved HEAD off it, the step goes on as below, committing on HEAD's branch every session file uncommitted there, the open run's among them, which the handoff's switch carried along (§4 step 1).
- On a branch it would not leave — B1's default branch, B3's, or a branch G2 kept — it keeps no stay, and its end takes §4 step 1's here form, where HEAD still stands there: a commit on HEAD's branch of its change (§4 step 1 (1)), that is not pushed while the open run stands.
- Where its start took no snapshot — `status` could not run (§2.1), or the start was cut off before taking one — its end commits nothing while the open run still stands, by the landing or the here form alike, since nothing tells its files from that run's: §6's *mid-run* row says so, with the `no-snapshot` reason clause (§4 step 1).
- G1, where it fires, takes its mid-run form (§5), as G2 does.

In session-branch mode (§8) it still switches nothing, but its commit, §8.2's, takes every session file the overlay holds, the open run's in-progress files among them, onto the session branch with its own: the mode is unchanged here, and keeps no snapshot apart.

**The open run's protection ends** once its command is typed again in this session with the same run key set, or where either start recorded none — a start that is not that run's own re-run or continuation — which parks its record, or marks it so where it is parked already, protecting nothing from then on, while that second run's own record protects the branch until that run ends (below), though typed again with another key set it leaves it standing, the second run then typed mid-run under it; when HEAD leaves its branch — the one it stands on now, which the open-run test matched, as the branch that run recorded or by a key of it — even where it has returned since; at `/clear`, which gives the session a new id and so a new directory of records (§7); at the open run's own `end`, which removes its record; or 7 days after it started, beyond which no record is read as open. A re-run of the open run that finds its record (`start --rerun`), or a continuation of it (`start --resume`) that goes on with its record or, starting afresh, names it by `--started` or takes it up as its own — a record marked `call_returned: false` (§7), as the harness's stop of that run's start leaves it, with this call's arguments — leaves it standing: a continuation that goes on keeps the record as it is, and the others take it over, keeping the stamps of the run's earlier starts in `started_before` (§7), so a run typed under it, whose record names it by the `started` it held then (`midrun`), still finds it, and the test reads that record as it now stands, its 7 days and HEAD's leave counted from the record's own `started`. A continuation given no `--started` — which the skill makes only to remake a first `start` call that returned no JSON, a plain start, which marks its record `call_returned: false` at its first write (§7) — uses `<command>.json` only where that record is marked so, with this call's arguments: it goes on with it, or, starting afresh, takes it up as its own. Any other record it meets as a plain start does: it parks it where it is an open run, and sets it aside otherwise (§7). Such a record may be another run's: one made with other arguments is another invocation's, and one not marked `call_returned: false` may hold a stamp some run learned from a start call's JSON and names by `--started`, so that run's later calls would land on this run's record were that record gone on with or taken over. The run it belonged to then no longer stands. Every `next` a preflight call returns names its own run's record by `--started` (§7), so a continuation of the open run made from one leaves that run standing however late it is made. HEAD's leave is read from HEAD's reflog, newest first and no further back than the open run's `started`, as a `checkout: moving from <HEAD's branch> to <another branch>` entry among those `git -C "$SPECS_PATH" reflog show --date=unix --format='%gd %gs' HEAD` prints. A move from a branch to itself never counts, and the open run's own handoff onto its branch, a move to HEAD's branch from another, is no leave. Where that reflog cannot be read, the protection holds for as long as HEAD stands on the branch. Until the protection ends, an abandoned run — stopped with Esc and never ended — holds on its branch the preflight and the end of every later run of the session's other commands, and of its own command typed with another key set, each a run typed mid-run: neither of those entry points switches the branch away. So every line that says a run is still open — §5's mid-run *If ignored* lines, §6's *mid-run* and *here* rows, and `phase-handoff.md` §6.1's mid-run stops — names the three ends a user can make for a run they stopped: `/clear`, typing its command again with its key set, which the line names where that run's record holds one (`<keys>`, its keys joined by `and`), or HEAD leaving the branch. Outside session-branch mode, neither commits the abandoned run's files either while HEAD stands at its end on the branch it started on: each such run commits its own change apart from them — by the landing, on `<default>`, where it holds a stay at its end, and by the here form, on the branch itself and unpushed, where it holds none — and nothing at all where its start took no snapshot; where its own handoff has moved HEAD off that branch, its end goes on as for any run whose HEAD moved (§4 step 1), and commits them with its own, which that handoff's switch carried along. That is the cost of keeping both entry points from moving the branch under another run and, outside session-branch mode and save after such a handoff, from committing its work in progress.

**The same command typed twice.** Its `start` moves an open record of its own command aside under a name that carries its `started` stamp (`<command>.<stamp>.json`), marked `parked: true`, rather than setting it aside (§7) — it serves its own run's end — and what follows turns on the run key sets the two starts recorded, compared as sets, their order aside. **Where both hold a key and the two differ** — a second piece of work typed while the first stands — the parked record keeps `protects: true`: the first run stays protected, and the second is a run typed mid-run under it (above), its preflight and its end moving nothing under it. **Where they are the same set, or either start recorded none** (a keyless command), the second is a restart: the parked record is marked `protects: false`, and so is each parked record of this command that the open-run test passes and whose key set is not another — none of them protects its branch from then on, which the second run's own record protects while that run stands — and the run goes on as any other, typed mid-run only where another record passes that test. That second run's end restores the newest parked record, its `protects` as it stands, or drops it where §3.5's open-run test, applied to the parked record, no longer finds that run on HEAD's branch: HEAD stands on neither the branch the parked run recorded nor a branch a key of it names, or HEAD's reflog shows a leave of HEAD's branch since its `started`, as above. A record it restores is marked `call_returned: true` (§7): the start that left it false was overtaken by the one that parked it, so no continuation given no `--started` goes on with it. Each run's end reads and writes its own record, found by any `started` stamp its starts returned (`end --started`, §7), so the two may end in either order. So do its preflight's re-run and continuation (`start --rerun --started` and `start --resume --started`, §7): a re-run of the parked run saves its new record parked, `parked: true` and its `protects` kept, under a name carrying its own new `started` stamp, and removes the parked file it re-ran from, the second run's `<command>.json` untouched — where it is cut off between that save and that removal, the file it re-ran from is left behind, and no end restores it, no open-run test reads it and no `--started` names it, until the new record's next save, its removal, or the save of another run's record in its place removes it; a continuation goes on with the record its stamp names, by any stamp that run's starts returned, so a re-run the harness stopped before it printed its JSON goes on from the stamp of the start before it; and each `next` such a call prints names its record by `--started`, as every `next` a preflight call returns does (§7).

**`end` with no start** — a run that stopped before its preflight, one passed `--no-preflight`, or one whose only record is a declined handoff's — has no snapshot to tell its files from an open run's. Once its gate passes and HEAD is on a branch, before any pull or commit, it reads the session's records as above, every one but the record its `--started` names, this command's own other records included; where one is open on HEAD's branch it writes nothing — no catch-up, no commit, no record saved — and prints §6's *mid-run* row with the `no-preflight` reason clause. Passed `--no-preflight` and no `--started`, where `<command>.json` holds a record a start of the script made — another run's, an open one of its own command among them — it never writes or removes that file, on any of its outcomes: it keeps its own record at a derived name, `<command>.<stamp>.json` under a stamp of its own, as an `end --started` whose stamp names no record does (§7), and never takes that file's `end_commit` for a resume. A run of the same command that stops before its start leaves the first run's protection standing, since its start never ran.

**By hand**, a run reads no records, so its trigger is one it observes: another run of this conversation — another command's, or its own command's with another key set (above) — has printed its preflight's `Environment:` line (§3), and no `Specs repo:` line since. That protection ends where that command, typed again in this conversation with the same key set, or where either takes no key, prints its preflight's `Environment:` line — never where it is typed again and stops before its start, which prints none and leaves it standing (above), nor at the second `Environment:` line its own re-run prints, which nobody typed and which leaves it standing too — or HEAD leaves the branch it stands on, even where it has returned since — a `checkout: moving from <that branch> to <another branch>`, which the run can see in its conversation, or read from HEAD's reflog back to the last `Environment:` line that command printed, as above — the two of its ends a run by hand can see. Such a run takes its snapshot at its start, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" --specs "$SPECS_PATH" snapshot`, keeps the JSON it prints in its conversation, and at its end passes it back on stdin to §4 step 1's `land … --snapshot -`, with `--here` where it holds no stay; the held record journals that here form, and the next preflight finishes it where the run is cut off mid-way (§3.2). Where its `snapshot` call could not run, the run took no snapshot: where that protection still stands at its end, it makes no `land` call and commits nothing, and prints §6's *mid-run* row with the `no-snapshot` reason clause; where it has ended, its `land` call goes without `--snapshot -`.

**Not covered: two sessions on one checkout.** Each session's records are its own, and reading every session's would make other sessions' week-old runs look open.

**One stay line.** Where more than one reason to stay holds, B2 and B4 print one line: the misrooted one, else the unlisted one, else the mid-run one.

**Branch key resolution — `branch-key <branch>`.** The branch's key is resolved
*against the run key set*, by testing the keys the run already holds. It is never
extracted from the branch name as free text. Resolve it with
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" --specs "$SPECS_PATH" branch-key --branch <branch> --key <K>…`,
one `--key` per key in the run key set and none on a keyless run, which prints
`{"plugin_branch": true|false, "prefix": <prefix>|null, "key": <K>|null}`: `plugin_branch` false
is step 1's no-prefix case, and `key` null is step 4's B4. Where it exits 2, report the first
line of its stderr and take B4, which leaves the branch and its pull request alone. The script
follows these steps:

1. Strip the `idea/`, `prd/`, `ard/`, `spec/`, `epics/`, `design/`, `ready/`, `brd/`, `frames/`, `kb/` or `conformance/`
   prefix (a `kb/harvest-<date>` name holds no key, so it resolves to B4). Call the remainder `R`. No prefix matches → not a plugin
   branch, and no row here applies (§3.3 G2 already kept the run on it).
2. A key `K` in the run key set (§3.2) is a **candidate** when `R` is exactly `K`,
   or `R` begins with `K-` or `K_`. **The separator is required.** It is the same
   boundary folder resolution uses (`<KEY>{-|_}<slug>`,
   `${CLAUDE_PLUGIN_ROOT}/references/addressing.md` §3), and a branch name is
   built from the resolved folder's name rather than re-derived
   (`${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md` §2.2), so the two agree by
   construction.
3. **The longest candidate wins**, so a run that holds both a key and a longer key
   extending it resolves the branch to the one the branch was actually named for.
4. No candidate → the branch matches no key in the set (B4). An empty set (a
   keyless run) can produce no candidate, which is the same B4 its own row already
   states.

**Why this is a resolution and not an extraction.** Every candidate is a key the
run *already holds*, so nothing in the branch name can become a key — slug text
included. `spec/PRODUCT-1234-2fa-rollout` on a run keyed `PRODUCT-1234` resolves to
`PRODUCT-1234`, because `2fa-rollout` was never a key and so was never a candidate.
A regex over free text has no such anchor, and both plausible ones fail: the narrow
`[A-Z][A-Z0-9_]*-[0-9]+` reads `EPIC-008` out of `ard/EPIC-008-01-<slug>` and sends
a resumed slice run to B4 to duplicate its own branch, while the obvious widening to
`[A-Z][A-Z0-9_]*(-[0-9]+)+` reads `PRODUCT-1234-2` out of that same
`spec/PRODUCT-1234-2fa-rollout` — a slug beginning with a digit captured as a key
segment. Step 2's required separator forecloses that second failure even for a run
that genuinely holds `PRODUCT-1234-2`: there `PRODUCT-1234-2` is followed by `f`,
not by `-` or `_`, so it is not a candidate, and `PRODUCT-1234` still is.

**A two-segment key resolves exactly as it did before.** For a run keyed
`PRODUCT-1234`, `prd/PRODUCT-1234-<slug>` was extracted as `PRODUCT-1234` and is the
single candidate here; a branch named for some other key matched nothing then and
has no candidate now. The rule never asks how many segments a key carries, which is
why a three-segment slice key needs no special case — `addressing.md` §1's
"shape is not depth" holds here too — and why nothing above has to change when a
key grammar widens again.

**A re-run in the same run switches back first.** Where a command runs this entry point a second
time in one run with a changed key set — `/docs-workflows:document` and
`/docs-workflows:release-notes` do, when the operator enters a slice key at their BRD-container
stop — and the earlier run's B4 switched away from a plugin branch that `branch-key` now resolves
to a key in the new set, switch back to that branch first (`git -C "$SPECS_PATH" switch --no-guess <branch>`,
the name B4 reported; it exists and the plugin created it, and `--no-guess` keeps one deleted since from being made again from `origin`'s copy, with the upstream write that can half-move the checkout (above)), then run stages 1–3 again, whose B3
then stays on it. That is the state a single run holding the new set from the start would have kept,
and a second preflight standing on the default branch cannot reach it by B1–B4 alone. A switch that
fails prints `Specs preflight: could not switch back to <branch> (<git's first error line>); this run goes on from <current>`, and the run continues from the branch it stands on. No
other re-run switches anything outside the table above. Under `specs_git: misrooted` there is nothing
to switch back to: no earlier B4 switched away, so the re-run classifies again and stays.
Where `status` could not run earlier in the run (§2.1), the re-run switches nothing back either, as the table then moves nothing: it prints `Specs preflight: staying on <current> — the uncommitted paths could not be listed, so no branch is switched (it would have switched back to <branch>, as a key of this run names it)` and runs stages 1–3 from the branch it stands on. A re-run is a run typed mid-run (above) only where its first start was one: it carries the open run that start found and tests it again as `end` does (§4 step 1's here form) — the record its command and `started` name, by the open-run test — and, where that run no longer stands, the re-run is not one. It never takes for its open run a run that started after its first start, since the protection is a run's from the commands typed after it — save where the re-run finds no record of its own (one dropped, or a session id changed since), when it reads the open runs as any command typed then does, though, as a re-run, it takes no snapshot (§7): its first start's reading is lost with the record, and a reading taken now can only protect more, the run then committing nothing while such a run stands (§4 step 1 (1)). A run typed mid-run switched nothing at its first start, so it holds no branch to switch back to; a re-run that is not typed mid-run switches back as above.

**No auto-merge, deliberately.** No row above creates a merge commit or merges a
branch into the default branch, and none should be added. The routing here
already resolves every case, and an auto-merge would push an unreviewed PRD or
ARD past the very pull request the command opened for it one phase earlier. B2
handles the only case where a merge would otherwise be needed — a branch already
merged upstream — with cleanup instead. If auto-merge is ever wanted, it slots
into B4 as `merge --ff-only → push → branch -d`, with B3 unchanged.

### 3.6 Why B3 exists — do not "simplify" it away

B3 looks redundant next to B4 and is the obvious candidate for a future simplification into "always return to the default branch." **That simplification is a bug.**

B3 now exists for two reasons.

**First, same-phase resume.** `phase-handoff.md`'s `require-on-main` (its §3) has a state — row B — that *passes* when the artifact is on the default branch but the worktree copy differs because the current branch, one this run itself owns, changed it since it forked (where the default branch changed it since then too, whether or not the branch did, row B′ stops instead): `/design` amends `specification.md` on its own `design/<EPIC>-<eslug>` branch, so a re-run of `/design` legitimately finds that copy has diverged from what merged earlier. B3 is what keeps the repo on that branch in the first place, and that is what makes row B reachable at all. If the preflight instead fell through to B4 and switched to the default branch, `/design`'s in-progress amendments would be left behind on a branch nobody is standing on, and row B — built to pass on exactly this divergence — would never see the case it exists for.

**Second, `/ready`'s explicit checkout.** The user may choose to proceed on the current checkout rather than switch to the default branch. Switching off it mid-run while the readiness report still claims that checkout is the one that was read would make the report false.

**The same shape reaches Epic-scoped runs — which is why §3.2 resolves a key *set*, not a single key.** `/specify <EPIC>` authors `specification.md` on `spec/<EPIC>-<eslug>`, a branch keyed by the **Epic**. The follow-up `/design <EPIC>` run resolves the PRD as its primary key, so a single-key comparison would read branch key ≠ run key, fall through to B4, and switch away from the branch holding the very `specification.md` `/design`'s resume depends on — the same reachability loss described above, one key earlier in the chain. Matching the branch key against **any** key in the set keeps B3 in force for Epic-scoped runs, on every command that takes an Epic address, exactly as it holds for PRD-scoped ones.

The failure this section used to defend against — `/create-ard` continuing silently against the wrong source when the authored PRD file existed only on an unmerged branch — is now caught loudly instead: `phase-handoff.md` §3.3 rows D and E stop that run rather than letting it proceed, so the defense moved there.

B3 keeps the working tree containing the artifact the run is about to read or amend. Where the run amends what that branch wrote, its own branch is cut from the earlier branch rather than from the default — a stacked branch, which states the dependency honestly. Where it neither declares nor read anything that branch changed, `phase-handoff.md` §2.2 (*Where a new branch is cut*) cuts it from the default ref instead: a stack there could only carry another phase's unmerged commits into a pull request that does not depend on them. Either way a gated input that branch changed has already met `require-on-main` — rows D/E where the default branch lacks it, the C rows where it differs — so what stacks is what the run read ungated or declares.

### 3.7 Detached HEAD is blocking, not merely skipped

G0 is the one guard that refuses to commit, and it is a data-loss guard
rather than a courtesy. (`specs_git: misrooted`, §3.1, also stops `commit-artifacts`
and `phase-handoff`'s deliverable commit, but no guard sets it: §3.1 names its setters.)

A commit made on a detached HEAD is reachable from no ref. Nothing points at it,
`git branch` will not list it, and it is eligible for garbage collection. If
`commit-artifacts` committed there, the run would report a short SHA and a
success line while the artifacts were already on their way to being
unrecoverable — the worst possible failure shape, because it looks like success.

So G0 propagates: it sets `specs_git: blocked` for the whole run,
`commit-artifacts` gates on that flag (§4 step 1), and the §5 notice fires at
**blocking** severity at both ends of the run. The artifacts stay in the working
tree, uncommitted and intact, and the notice gives the exact command to attach
them to a branch.

**Of the three guards, this is the only one that disables the terminal commit** — `commit-artifacts` step 1's gate also no-ops silently where §3.1's environment conditions fail on a run carrying neither flag, so *the only condition* full stop, which this sentence used to claim, is wider than the guards it is about. In particular
G1 does not — see the note in its row; on a branch the run would have left, the commit is §4 step 1's landing onto `<default>` instead.

## 4. `commit-artifacts` — terminal step

**Run by `scripts/specs-git.py`.** A run reaches this entry point through `Skill(skill: "workflows-core:specs-git", args: "end")` — the loader routes `args: "specs-repo-git commit-artifacts"` there — which runs `specs-git.py end` and prints what it returns. What follows in §4 is the rule that script follows and is tested against, and the fallback the skill names where the script cannot start; it is never a procedure to run by hand beside the script. Step 6's replay is the script's too: `end` returns it as its `next`, `specs-git.py replay`, which the skill runs in a Bash call of its own; the `session-branch.py replay` call step 6 names is run by hand only in that fallback, and `phase-handoff.md`'s pushes never replay (its §1 rule 4). Parts of it — `phase-handoff.md`'s applications above all — are applied by other steps too, and those steps still read this text: `phase-handoff.md`'s three entry points apply step 4's commit-and-restore form, step 5's push target and `push-scope`, §4.1 and the refusal tail below, and name step 6's replay as the exception their own pushes do not take; the documentation commands run step 4's form against their own repositories; and the references the grep above lists cite it besides.

Runs as the **last action of the run**, after `resume.md` is written (where the
command writes one) and before or as the run's last printed output (§6).

**The one exception — a phase that cedes control.** Where a later phase hands the
session to another skill, or opens an open-ended interactive stretch, this step
runs immediately **before** that hand-off instead, and prints its §6 outcome line
there. `/prompt-brainstorm` (whose Phase 3 hands off to
`superpowers:brainstorming`) and `/prompt-grill-me` (whose Phase 3 is a long
interactive grill) are two of the cases; `/product-workflows:brd-split`'s *Ground now* is the third — its continuation waits on the operator's merge of the pull request this step's commit has to ride in, then runs other commands, so the commit comes before it. "Last" is protective only while the run still
reaches its own end: a commit placed after control has left the command never
executes, and the artifacts it was meant to persist are stranded uncommitted —
the exact loss this reference exists to prevent. The exception is deliberately
narrow. It applies where control genuinely leaves the command, never as a
convenience to commit early, and it never licenses splitting the step across more
than one invocation.

**A run that refuses before it has written anything still runs this tail, and
each member settles for itself what it does there.** A Phase 0 refusal — an
unresolvable address, a folder of the wrong kind, a missing argument, a root
where the command works only on a slice — ordinarily ends the run before it
has a deliverable, a branch or a handoff (the exception is named below), and nothing above said whether feedback,
follow-ups, the cost entry and `resume.md` still fire. They do, and the answer
is each member's own rather than a new condition here:

- **Feedback writes nothing**, save where a command's own stop route runs its
  maintenance phase. `feedback-emission.md`'s `emit-auto` is called by a
  command's maintenance phase, which a refused run reaches only where its
  command's *Ending early* sends a stop through it — as the docs setup
  commands do for their stops past their earliest ones — and `emit-block`
  fires at the halt rather than here and excludes an environment or operator
  halt by its own predicate — which every Phase 0 refusal is.

- **Follow-ups are a no-op.** No signal qualifies, so that phase resolves no
  target, writes nothing and ends silently (`followup-emission.md` §6).

- **The cost entry is written, unless `--skip-costs`, in which case `workflows-core:run-flags` `skip-cost` advances the checkpoint and writes nothing, or unless the run carries `specs_git: misrooted` (§3.1), in which case `cost-emission.md` §8 reports it in the run's output and writes nothing, or unless no transcript holds the run's own invocation, in which case `cost-emission.md` §1 says so in one line and measures nothing** — and on the one stop that is no run at all, and on a refusal a command states takes no tail, both named below, none of this tail runs. `cost-emission.md` §11 settles it already —
  *Cost runs unless the user skipped it* — and it is the member that makes this tail matter on a
  refusal: the run spent the session's tokens whether or not it wrote a file,
  and a keyless one has a home too: that file's §9 pending file, save where its §8 tier 2 files it per docs or code repository, or reports it only. A refusal
  that skipped the tail would break `cost-emission.md` §11 silently, which is why the tail is not
  skipped wholesale.

- **`resume.md` is NOT written.** `session-hygiene.md` §1 defines it as the
  last *completed* position — the phase just finished and the exact next
  command from the run's own `### Next step` — and a Phase 0 refusal completed
  no phase and printed no such block. It is overwritten rather than appended,
  so writing one here would replace a live pointer to a real position with a
  run that did nothing, and what it replaced cannot be recovered.

- **This step runs**, save on those two kinds of stop, for the cost entry above (under `--skip-costs` there is none, and the gates below settle the step exactly as they would for any run with nothing new to stage). Where the refusal was `specs-root-check`'s stop, the run carries `specs_git: misrooted`, and step 1's gate skips the step with the stop repeated. Where the refusal came before
  `$SPECS_PATH` was resolved, with `$SPECS_PATH` unset, step 1's gate no-ops it silently; on a refusal before the preflight with `$SPECS_PATH` misplaced, step 1's placement tests skip it with §3.1's notice; on a detached HEAD with something to stage, step 1 refuses it with G0's notice; on a plugin branch the preflight stayed on and would have left, it takes §4 step 1's landing onto `<default>`; and with no start, where another run of the session is open on HEAD's branch, it commits nothing (§3.5). Where that
  entry is the only new path and a commit is made at all, step 4, or the landing in its place, commits it alone; where nothing is dirty,
  step 3's `nothing to commit` line stands.

**Nothing here is keyed on whether the run wrote under `$SPECS_PATH`**, which
is the obvious rule to reach for and the wrong one: the cost entry is itself
such a write, so that test would drop it on exactly the refusals that spend
most — one that resolves an address, reads a tree and only then refuses. **And
it is scoped to a refusal taken before the run has a deliverable, a branch or
a handoff**, which is what most Phase 0 stops in the family are, never all: a
Phase 0 stop taken after the run cut a branch is outside it — `/document` in
keyed mode is one, its Phase 0 having cut a docs-repository branch and
committed the generated profile on it wherever it profiled that repository
inline, before its later Phase 0 stops. Such a run, like one that stops in a
later phase, has written something, and what its tail does is that command's
to state. **One stop is no run at all, and takes no tail**: `/product-workflows:prd-ground`'s
`PRD_GROUND_TYPED_ONLY`, where the model started the command without `/brd-split`'s
`--from-split` — nobody elected a run, so a cost entry would bill one that never was, and the
spend before it is the conversation's. **And a command may state that a refusal taken before it
has resolved its target takes no tail** where its cost entry is filed per that target and would
otherwise wait in `cost-emission.md` §9's pending file for a reconciliation that never comes
(`cost-emission.md` §8 says why): `/docs-workflows:docs-init`, `/docs-workflows:docs-audit`
and a standalone `/docs-workflows:docs-brand` state it for their stops before a docs repository
is resolved, and `/docs-workflows:document` for a direct-mode stop before its write target is.

1. **Gate.** All of §3.1's environment conditions, **plus** the run must not
   carry `specs_git: blocked` from §3.3 G0 or `specs_git: misrooted`, whichever
   of §3.1's setters set it.
   **The run's environment, at the end.** Where the record the run's start made stands (§7), it holds the `Environment:` line the run's preflight printed: compare the `SPECS_PATH` half of the run's `Environment:` line, as the record holds it, with the same half of the line `session-hygiene.md` §7's Bash call prints now. Where they differ, the run carries `specs_git: misrooted` from here on, with that section's `Environment changed:` notice, built from the two whole lines, as the notice that set it, and the misrooted outcome below follows. Where no such record stands — a run that stopped before its start, one whose session id changed before its end, or one where `CLAUDE_CODE_SESSION_ID` is unset, so that its start wrote none — nothing is compared here, even where a declined handoff's record stands in its place (§7): §3.1's two placement tests — the preflight's, where it ran, or, where the script finds no record the run's start made, this step's, the script treating the run as one that ran no preflight (below) — and `session-hygiene.md` §7's `env-check` before each write of the tail still guard it. The `REPOS_PATH` half is `env-check`'s, which the tail runs: a run `session-hygiene.md` §6 pinned exports its own value per call.
   **Test the two flags first, and a flag's outcome below takes precedence
   over an environment failure**, so each state has one outcome.
   `specs_git: misrooted` is often set where an environment condition fails
   too: §3.1's non-repository notice sets it where `specs-root-check` finds a
   signal, as on a `specifications/` directory bind-mounted on its own, and
   that entry point's stop sets it on a path no `rev-parse` reaches. Such a
   run takes the misrooted outcome, never the silent one. `specs_git: blocked`
   is set only behind a passing gate (§3.3 G0), so it never meets one at the start; at the end that flag's outcome is taken without testing either again, and its row reads the checkout only where §6's own comparison allows. **A run
   that ran no preflight and carries neither flag tests G0's state here**, since
   nothing else did: a refusal taken before the preflight still reaches this
   step (the tail above).
   Such a run first runs §3.1's two placement tests — `specs-root-check`'s signals and the below-top-level test — and, where one fires, takes the `specs_git: misrooted` outcome instead, with the notice §3.1 prints for it, since its preflight would have set the flag.
   Where §3.1's environment conditions hold,
   `git -C "$SPECS_PATH" symbolic-ref -q HEAD` fails, and step 2's enumeration
   would stage at least one ARTIFACT path (§2.1), HEAD is detached with
   something to commit; the run takes the `specs_git: blocked` outcome below,
   printing the notice for the first time rather than again. With nothing to
   stage it goes on, and step 3's `nothing to commit` line stands: the notice
   would warn about artifacts this run never wrote. A commit there would be reachable from no
   ref, whichever way the run arrived (§3.7). Where the gate passes, a run that
   ran no preflight resolves session-branch mode here (§8.1).
   - Carries `specs_git: blocked` → **not silent**: re-emit the §5 blocking
     notice. The repo *is* managed; the plugin is deliberately refusing to
     commit, and the user must know.
   - Carries `specs_git: misrooted` → **not silent**: re-emit the notice
     that set it, or emit it for the first time where this step set the flag — the §3.1 notice, `specs-root-check`'s stop,
     `session-hygiene` §7's `Environment changed:` notice, or
     `session-hygiene` §6's `RESUME_ENVIRONMENT_CHANGED:` stop line — whether
     or not §3.1's environment conditions hold. Nothing is committed, and the
     tail's emitters wrote nothing under `$SPECS_PATH` (§3.1) — save where this step set the flag itself, after they ran, by its environment comparison or its placement tests above: what they wrote then stays where they wrote it, uncommitted. What the command
     itself wrote there — a noticed run's deliverable, or one of §2.1's single
     files such as `implementation.md` — stays written and uncommitted, and
     what was already there sits where this run found it.
   - Carries neither, and fails on path / repo / permission grounds →
     **silent no-op**, matching the emission ladders' silent-skip discipline.
     Nothing committed, nothing reported, run unaffected.

   **A branch the preflight stayed on — the landing.** Where the gate passes on a branch outside session-branch mode (§8), the run may hold a **stay**: the plugin branch (§2.2) the preflight ended on without leaving it, though it would have left it — in the record its start made (§7), or, where the run follows this text by hand, in its conversation (§3.3). A stay records the branch; its kind — `mid-run`, one kept while another run of the session was open there (§3.5), whatever else stayed it; else `merged`, one `branch-merged HEAD` (§3.5) read merged (B2); else `unkeyed`, a branch no key of the run names (§3.5's B4); its `merged` flag, the branch's merged answer whatever the kind; and why it stayed — §3.3 G1 fired, `status` could not run (§2.1), git refused the switch of §3.4's merged-branch leave or of §3.5's B2 or B4, the preflight stopped early before that switch (§1 rule 5), or another run of the session was open on the branch (§3.5). Each preflight derives its own: a re-run's (§3.5) starts with none from the start before it, so the reason is one that preflight met — its early stop asking afresh — and a branch it would no longer leave, or that HEAD has left, holds none.

   **A start that never finished its preflight** — its record (§7) still at one of `start`'s own stages, its last call having stopped early, been cut off, or returned a `next` the run never made, at its budget or for a replay — may hold none for the branch it stopped on, since such a call ended before B2's or B4's switch, and may have ended before G1's test: there `commit-artifacts` asks what G1's test asks (§3.3), where HEAD still stands on the plugin branch that call returned on (its `branch`) — `branch-merged HEAD`, and `branch-key` against the run key set with the commit key `commit-artifacts` is given beside it — and holds a stay with the early stop's reason where the branch reads merged or no key names it; where the merged ask cannot answer, the branch reads unmerged, with no report (§3.5). **A stay whose `merged` flag is not set — `unkeyed`, or a `mid-run` one on an unmerged branch — is tested once more against the commit key `commit-artifacts` is given** (step 4's `<KEY>`): where `branch-key` resolves the branch to that key — a run that resolved its key only after its preflight — the stay is dropped, and the step goes on as below, committing on the branch, which is the run's own; under a run typed mid-run that commit is the here form's (below), its change taken as (1) takes it. Where the run holds none — a run whose session id changed before its end, a `/clear` among the causes, finds no record (§7) — no stay is known, and the step goes on as below, even where its preflight printed G1's landing form.

   **Where the run holds a stay and HEAD still stands on its branch, the landing runs in place of steps 2 to 4.** It commits the run's own session-file change on `<default>` without moving the checkout:

   **(1) The run's own change.** `c1` is HEAD's tree with each path of the run's snapshot at the version the snapshot holds, or removed where it holds none, committed on HEAD; the snapshot is every session file dirty when the run's start took it (§7) — not the run's own: an earlier run's leftover, or an open run's work in progress (§3.5). `c2` is `c1`'s tree with each ARTIFACT path (§2.1) `status` lists now at its working copy, or removed where no file stands, committed on `c1` with step 4's message. **The guard.** In every landing and every here form, whether or not the run was typed mid-run: a path of the snapshot that is an overwritten file, a `runs/` or `scans/` record, or a security register keeps in `c2` the version `c1` holds. Already uncommitted when the run started, it is the branch's, as the snapshot reads every file dirty then (above, the maintainer's S1): whatever was written there since — by this run, by a run open on the branch, or by one typed under this run — is left out of the change — neither landed, lifted nor committed here — and stays in the working tree for a later commit on the branch, and §6's line names each such path whose working copy differs from the snapshot's (*After a landing*, the *here* row, the row a here form's push gives, and the *there* and *nothing* rows that follow a landing or the here form). So the guard depends on no open run: whether one stands at the end, and the order nested runs end in, change nothing it leaves out. It widens what the change leaves out, and nothing else: whether the run stays, takes the here form, or pushes, and which run its `midrun` names, are as above; and steps 2 to 4, which commit on a run's own branch where it holds no stay, are not the change and are unchanged. Its cost: a stayed run's own rewrite of an overwritten file already uncommitted at its start is committed later, by a later commit on that branch — into its pull request, where the branch has one — as the leftover itself is. A block-shaped file and `follow-ups.md` (§8.2 step 3) go with the change as any other path does, each entry added since the snapshot travelling with it. So the change is what changed since the run's start, less those paths: what the open run writes after that start to a session file it had no uncommitted change in then, and each entry it appends then, go with this run's, since nothing tells them apart. Where the two trees are one, nothing of the run's is dirty, and step 3's *nothing to commit* line stands. Where the run's start could not list the uncommitted paths (§2.1), it took no snapshot: `c1` is HEAD, every session file uncommitted on the branch goes with the run's own, and §6's line after a landing says so; the row step 5 gives the here form's commit (below) does not. A start with no snapshot for another cause — one cut off before taking it, or a record an earlier version of this plugin wrote — lands against HEAD the same way, and nothing says so. **Under a run typed mid-run** (§3.5), a start with no snapshot, for any cause, commits nothing while the open run still stands, which `end` tests again as §3.5 tests it: the session files dirty on the branch may be that run's work in progress, and nothing tells them from this run's, so neither the landing nor the here form (below) commits, holds or lifts anything, and the line is §6's *mid-run* row with the `no-snapshot` reason clause. Where that run no longer stands, the change is taken against HEAD as above.

   **(2) The apply**, onto `onto` — local `<default>`, or `<default-ref>`'s commit where local `<default>` is absent or strictly behind it — path by path, for each path `c1` and `c2` differ on, from `onto`'s version. A block-shaped file (§8.2 step 3) becomes `onto`'s version followed by each entry of `c2` that neither `c1` nor `onto` holds (where `onto` lacks the file, `c2`'s header first), and is refused (`edited`) where any entry of `c1` is missing from `c2` — an edit, a removal, or an addition to its last entry — or where `c1` holds the file and `c2` changed its header. `follow-ups.md` becomes `onto`'s version followed by each line of `c2` that neither `c1` nor `onto` holds, in `c2`'s order, and is refused (`dropped`) where a line of `c1` that `onto` lacks is missing from `c2`: so a line `onto` holds, edited in place — a ticked follow-up — lands as a second copy beside it (`followup-emission.md`'s two-copies case), and one `onto` holds that the run dropped stays on `onto`, the lift returning it to the working copy. Either shape is refused (`forms`) where `onto`'s version and `c2`'s are not in one line-ending form. An overwritten file, and any other path, takes `c2`'s version. A deletion applies where `onto` holds `c1`'s version, does nothing where `onto` lacks the path, and is refused (`deleted`) where `onto` holds another. A path `c2` adds or changes under a feature folder that `c1` holds and `onto` holds nothing under is refused (`folder-gone`), since writing it would bring back on `<default>` a folder a teammate removed or renamed, or plant there one only the stayed branch has. A security register the change touches is rebuilt from the result's records by the `register_rebuild` script (§7), and every path of that `security/<slug>/` is refused (`register-rebuild`) where none was handed over or the rebuild fails. So nothing of the branch's own content reaches `<default>` ahead of its pull request. The result is built through a temporary index, with no `merge-tree` and no checkout, and committed on `onto` with step 4's message; like §8.2's `commit` and step 6's replay, it runs no `pre-commit` hook. A refused path is held alone, as one held entry whose cause will not pass, and the rest lands; where only refused paths would have changed `onto`, nothing is committed. Where an `index.lock` stands when the landing starts, nothing is applied or lifted: the run's change, where it has one, is held for the cause `locked`, which passes (*A refused landing is held*, below) — `c1` and `c2` are built through a temporary index, and neither the held ref nor the held record takes the index's lock — so the next run's flush leaves its files out, as it leaves out every held file (§3.4).

   **(3) The move** — never of a local branch another worktree has checked out, since moving a branch under a checkout leaves that checkout's index and files behind it, a revert of the move staged there. Where no worktree has `<default>` checked out, `<default>` is moved from its tip onto the commit — or created there, where it is absent — by `update-ref` inside one locked transaction, which tests, under the ref's lock, that tip again and again that no worktree has the branch checked out; a move refused because the branch or the checkout moved meanwhile is tried once more on the new tip. Where one has, the commit is built on `<default-ref>` instead — `origin`'s `<default>`, never local `<default>`, wherever an `origin` exists — and pushed by refspec, `git -C "$SPECS_PATH" push --porcelain origin <commit>:refs/heads/<default>`, where step 5's first two conditions hold (its third, `push-scope`, has nothing to measure: the push names one commit, built on `<default-ref>`), the local ref left alone for that worktree to pull; where they do not hold, or the push fails, the change is held (below). Where `<default-ref>` names no commit — an `origin` with no `<default>`, whether it never had one or no longer has it — there is no commit to build on that the push could name alone, and local `<default>` may carry commits of the user's own that a push would publish unmeasured, so nothing is built or pushed: the change is held, a cause that will not pass. In that case only where no worktree has `<default>` checked out does the landing build on local `<default>` ((2)), and step 5's push then tests all three of its conditions. With no `origin` at all and another worktree on `<default>`, `<default-ref>` is local `<default>` itself (§3.2): the commit is built there, and the change is held for `no-remote`, a cause that will not pass, since nothing can be pushed. With no `origin` and no such worktree, the commit lands on local `<default>`, moved as above, and step 5 prints its no-remote row.

   **(4) Steps 5 to 7 for that commit on `<default>`**, `<branch>` in them being `<default>` — save where (3) pushed it by refspec, when step 5 has nothing more to push.

   **(5) The lift.** Once `<default>` holds the commit, each path the change landed whose working copy is still exactly what landed is written back to the version the run's change, or the chain of held changes it ends (below), started from — the snapshot's version, HEAD's, or none — so the stayed branch's checkout shows none of what landed, and never less than HEAD. A working copy changed since is left as it stands. The lift is needed: git refuses a later switch to `<default>` over such a working copy even where it is byte for byte the version `<default>` now holds (measured on git 2.43), and the next flush would otherwise commit the same files on the branch again. It is the second of the two discards §1 rule 4 names.

   **Earlier held entries go first.** Before the run's own change, each held entry (§1 rule 8) whose cause passes and that shares a path with that change, or with a later such entry that does, is landed the same way, oldest first, each held file changed since it was held first leaving its entry as at §3.2. They land only locally here, since `commit-artifacts` has no time budget for a capped call, and so does the by-hand `land` call below: an entry that would need the refspec push stays for the next preflight's held stage (§3.2). An entry still held holds back the run's own change, with its cause, where they share a path; held entries chain only on a shared path, so one never holds back a change on other paths. Each held entry landed first prints §3.2's `Specs preflight: committed <sha7> (<N> files) on <default>: …` line for it, before §6's line.

   **A refused landing is held.** Where the change cannot land — an `index.lock` stood when the landing started, another worktree has `<default>` checked out and the refspec push cannot be made or fails, a ref's lock stands, `<default>` moved twice while the run was committing on it, or (2) refused a path — nothing is committed on the stayed branch: the change is kept as a **held commit**, `c2` on `c1`, under `refs/workflows/held/<commit id>` with its entry in the held record (§1 rule 8), and its files stay in the working tree. A cause that passes — a refspec push that failed or that `origin` refused, a lock of the index or of a ref, a branch that moved — prints §6's *held* row. It promises the next run's retry, §3.2's held stage, which every later preflight runs before its guards — save where `origin` refused the push and §4 step 6 recorded it, or a refusal was recorded already (`checked-out`'s fifth or sixth alternative, §6): that record turns session-branch mode on from the next run, whose held stage drops the hold and whose §8.2 `commit` takes the files, and the row's tail says so instead. A cause that will not pass — a path (2) refused, or a refspec push with nowhere to go: no `origin`, a push your configuration sends to another remote, an `origin` with no `<default>`, whether it no longer has one or never had one ((3)) — prints §6's *held, stuck* row, or, where the rest of the change landed, the landing's row with its *held, stuck* append; each names the commands to see the change and to drop the hold (`land --drop-held`). No landing takes such an entry: until its hold is dropped — by that command, or by a later run on `<default>` or in session-branch mode, which drops it (§3.2's held stage, and on `<default>` step 2 too) — §3.2 prints its stuck line for it on every later run, and once dropped its files are ordinary uncommitted files, which a later commit takes.

   **A change already there.** Where the apply refuses nothing and finds `onto` already holding every change the run made, nothing is committed: the lift still runs, and §6's *there* row says so.

   **The landing's journal.** Before `<default>` moves, or the refspec push is made, the held record journals the landing — its change, the commit it built and the tip it moves `<default>` from — and the run's state record saves it as its `end_commit` (§7); the journal entry is removed once the lift is done. A run cut off mid-way is finished by `end --resume`, or, where no resume comes, by the next preflight's held stage (§3.2), only where the move is verified — `<default>` holds the journalled commit, or, for a refspec push, `origin/<default>` does — the files lifted then; otherwise the change is landed again, never lifted unverified, since that lift would write back over a change that is nowhere else. Where `end --resume` finds the move unverified and HEAD no longer on the branch the preflight stayed on — on `<default>`, on another branch, or detached — it drops the journal entry instead: nothing moved, and the files are still in the working tree, so the step goes on as for a run whose HEAD has moved off the branch it stayed on — committing them where §4.1 puts them, or, on a detached HEAD, refusing them as step 1's G0 test does; a landing's journal is never finished by the here form. Where an `index.lock` stands when `end --resume` finds the journal, it does none of these — it neither finishes the journal, nor lands the change again, nor drops the entry — as nothing is applied or lifted under that lock ((2)): the entry is left for the next preflight's held stage, and the line is §6's *Locked* row.

   **A landing that appends to a file the stayed branch also changed makes that branch's pull request conflict on it** — in content, or add/add for a file new on both — since `<default>` and the branch then each hold lines the other lacks. The remedy is the one `phase-handoff.md` §3.3's *Row B′'s remedy* gives for a file the plugin commits beside the documents: merge `<default>` into the branch and keep every line either side holds.

   **By hand**, the landing is one call, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" --specs "$SPECS_PATH" land --branch <branch> --default-ref <default-ref> --command /<name>`, with `--commit-key <KEY>`, `--snapshot -` (the snapshot on stdin, §3.5's *By hand*) and `--register-rebuild <path>` where the run has them, and `--here` for the here form below; (1)'s guard applies to every such call that carries `--snapshot -`. It prints `{status, sha7, files, paths, lifted, default, pushed, reason, detail, path, permanent, stuck, kept, error}`. **Without `--here`**, steps 5 to 7 follow for `<default>`, unless it printed `pushed: true`, the refspec push's, and `status` names §6's row: `landed`, the row step 5 gives the commit; `there`, the *there* row; `nothing`, step 3's; `held`, the *held* row — an `index.lock` at the landing's start among its causes, `reason` `locked` — or the *held, stuck* row where `permanent` is true. **With `--here`** nothing is pushed while the open run stands (§3.5), and `status` names: `landed`, the *here* row — and, once that run no longer stands, steps 5 to 7 for HEAD's branch, whose row it then is; `there` and `nothing`, step 3's *nothing to commit* line; `locked`, the *Locked* row; `kept`, the here form's refusal, the *mid-run* row. Its reason clause (§6's landing reason clause) is worded from three printed fields: `reason` names the clause, `path` is its `<path>`, and `detail` gives the rest — for `checked-out`, the object `{outcome, text, remote, record, date, record_error}`, whose `outcome` selects the alternative — a `refused` one whose `record` is empty selecting the unrecorded form — `text` is `<reason>` or `<the refusal>`, `remote` is `<remote>`, `date` and `record` are `<date>` and `<record>`, and `record_error` is `<error>`; for `register-rebuild`, `none` or `failed`, which selects that clause's alternative. `stuck`, where set, names the paths held alone, for the *held, stuck* append, and `kept`, where not empty, the paths (1)'s guard left out, for the *start-dirty* append (§6). Where the call exits 2 on a line that does not begin `specs-git: not run (usage:`, it moved no ref and held or journalled nothing; where its JSON has `error` set, it stopped after its first ref write (§1 rule 5), and whatever it left in the held record — a held entry, or the journal of a move it began — stays there. Either way, commit nothing more by hand: the run's files stay in the working tree, save any it lifted once their change was on `<default>`; the next preflight's held stage (§3.2) takes up whatever it left there, as it does any held entry or journal; and the run's outcome line is §1 rule 5's `Specs repo: NOT FINISHED` line, `<the error>` the not-run line's reason or the `error` field.

   **The here form** — for a run typed mid-run that holds no stay (§3.5), on a branch it would not leave — commits the run's own change, taken as in (1), on HEAD's branch, in place of steps 2 to 4 and outside session-branch mode only, in two steps. First, the change applied onto HEAD as (2) applies it, `onto` being HEAD's branch, and committed on HEAD; journalled in the held record and in the run's state record (`end_commit`); then, with HEAD still naming the branch and no `index.lock` standing, both tested again immediately before, HEAD's branch moved onto the commit by `update-ref` from the tip the commit was built on, which moves no checkout and writes no file. Second, with both tested once more, `git -C "$SPECS_PATH" restore --staged` over exactly the paths the commit carried whose index entry was the old tip's and still is — one staged since is the user's, and stays — so the index follows HEAD there; then the journal entry is removed. The open run's files stay as they were, uncommitted. A run cut off between the two is finished by `end --resume`, or the next preflight's held stage (§3.2), only where the move is verified and no `index.lock` stands — where one stands, the entry is left for a later call: with HEAD on the branch and the branch at the journalled commit, or holding it, the second step runs; with HEAD on the branch and the branch still at its old tip, the here form runs again; otherwise the entry is dropped, and the files are left uncommitted as they stand. Where that is `end --resume`: with HEAD on the journal's branch, it tests the open run again, as §3.5 tests it, and where that run still stands — the branch having moved on without this run's commit — the line is §6's *mid-run* row with its `unfinished` reason clause; with HEAD on another branch, or where the open run no longer stands, the step goes on from step 1 on HEAD's branch. While the open run stands on the branch the commit is not pushed, since a push `origin` rejected would go to step 6's replay, which moves the checkout under that run: §6's *here* row says the next push of the branch carries it. `end` first tests the open run again, as §3.5 tests it: where it no longer stands — its `end` ran, HEAD left the branch, or its record was replaced — the here form still commits the run's change as (1) takes it, and step 5 then pushes it, its row the one that push gives, with no word of the open run: the run's own change where its start took a snapshot, and, where it took none, every session file uncommitted on the branch, as (1) says, any the ended run left among them. Where (2) refuses any path while the open run stands, the here form commits nothing and holds nothing: §6's *mid-run* row names the cause, and the open run's terminal commit takes the files with its own. It holds nothing because a held entry lands on `<default>`, the wrong place for the files of a branch B3 or G2 kept, which ride that branch. Where (2) refuses a path once the open run no longer stands, nothing is held either, and the step goes on as below, steps 2 to 4 committing on HEAD's branch every session file uncommitted there, as they do for any run that holds no stay. Where an `index.lock` stands, §6's *Locked* row stands; where nothing of the run's is dirty, step 3's *nothing to commit* line; and where the run's start took no snapshot and the open run still stands, §6's *mid-run* row, as (1) says. Where the run's own handoff has moved HEAD off the branch it started on, the here form does not run, as the landing does not where HEAD has moved off the stay's branch: the step goes on as below, steps 2 to 4 committing on HEAD's branch every session file uncommitted there — an open run's work in progress among them, which the handoff's switch carried along — and the commit lands where §4.1 says.

   Where HEAD has moved off the stay's branch — the run's own handoff cut or switched to another — the step goes on as below, and the commit lands where §4.1 says. In session-branch mode the session files never commit on HEAD (§8.2), so no stay is kept there and none of this applies.
2. **Enumerate and stage** per §2.1. OTHER paths are never staged. On the
   default branch, run §3.4's catch-up first.
   The catch-up never runs under a run typed mid-run (§3.5) where the open run, tested again as §3.5 tests it, still stands on the branch HEAD is on: such a run moves nothing under that run.
   A run whose preflight ended at a
   guard (§3.3) or never ran has not had it; where the preflight already caught
   up, it finds nothing to do. Its test reads the ref last fetched, so a merge
   that lands on the remote during the run goes unseen; that run's push is
   rejected as non-fast-forward, and step 6 replays the run's session-file
   commits onto the remote's branch, or names what to run where it cannot,
   save where another session switched the checkout during the move.
   In session-branch mode (§8), §8.2's
   `commit` enumerates instead, and the catch-up is wrapped as §8.3 says.
   **Held files** (§1 rule 8), outside session-branch mode: with HEAD on `<default>`, every held entry but a here-form journal is first dropped with its ref, as §3.2's held stage drops it, and its files are staged with the rest; on any other branch, every file of a held entry whose working copy is still the version the entry holds is left out, as §3.4's flush leaves it out, and a held file changed since it was held is staged as it stands, its entry rebuilt without it once step 4 has committed — an entry left with no file being dropped — and, for each such file the commit carries, §3.4's `Specs preflight: <path> changed after an earlier run held it for <default>, so it is committed here as it stands, and left out of the held commit` line printed before §6's line. Those paths are saved in the run's state record (§7) with the commit before it is made, and kept there for as long as the record holds that commit, so an `end --resume` that finds the commit made — the run cut off after it, during its push, or inside an earlier resume — prints that line for them and rebuilds each entry not yet rebuilt; where a call that printed the line returned its output and the record stayed — its `next` naming step 6's replay, or its stop on an error no signal caused — the record marks the line shown, and a resume after it rebuilds without printing it again; a signal's stop is no outcome, its output set aside by the harness that sent the signal, so the line stays unshown for the `--resume` that follows. An `end` that runs from step 1 on the record instead — a plain `end`, or an `end --resume` past §7's 15 minutes — replaces that commit in the record and does not print the line: it is a new end, whose line speaks of its own commit, and where that end's own commit did not rebuild the entry, the next preflight's held stage settles it (§3.2).
3. **Nothing staged** (the gate passed but no artifact path is dirty) → no
   commit; emit the §6 `nothing to commit` outcome line. This is distinct from
   step 1's silence — here the specs repo *is* managed and simply had nothing
   new.
4. **Commit — by pathspec, never the index.** Message:
   `<KEY> Add dev-workflows session artifacts (<command>)`, or
   `NOISSUE Add dev-workflows session artifacts (<command>)` when the run
   resolved no key. This matches the specs repo's own `<KEY|NOISSUE> <summary>`
   convention. **No `Co-Authored-By` trailer** (§1 rule 6). **`<KEY>` is the
   one key the run addressed**: an Epic run's own key, never the parent PRD
   key §3.2 adds to the run key set only to match branches; a BRD-route
   slice's key; and, where a command addresses several, the first it
   resolved. §3.4's flush, which commits through this step at run start,
   takes the same key, or `NOISSUE` where the run has none yet.

   Commit the paths step 2 staged that git still lists as staged, and
   nothing else. List them with
   `git -C "$SPECS_PATH" diff --cached --name-only -z --no-renames -- ':(literal)<path>' …`
   over the paths step 2 staged: a path step 2 enumerated can be one git no
   longer knows (staged as new by an earlier run whose commit failed, then
   deleted), and one pathspec that matches nothing fails the whole commit.
   Where it lists none, there is nothing to commit: emit step 3's outcome line
   instead. Then read everything the index holds staged, the same command
   with no path, which the restore below needs, and commit:
   `git -C "$SPECS_PATH" commit -q -m "<message>" -- ':(literal)<path>' …`, one
   `':(literal)<path>'` argument per listed path. A plain `git commit` takes
   whatever the index holds, and §3.3 G1 lets this step run beside changes
   that are not the plugin's, a change the user staged included, which that
   commit would carry under this message. `:(literal)` because a porcelain
   path can begin with `:`, which git otherwise reads as pathspec magic; never
   the global `--literal-pathspecs`, which every commit hook would inherit.

   **Then bring the index back in step with the new `HEAD`.** A pathspec
   commit runs the `pre-commit` hook against a temporary index, so a file the
   hook fixes and re-stages, adds, or removes is committed while the real
   index keeps the old entry (measured on git 2.43: `MM`, `D ` beside `??`,
   and `AD`). Once the commit lands, read the paths it carries,
   `git -C "$SPECS_PATH" diff-tree --no-commit-id --name-only -r -z --root --no-renames HEAD`,
   and the paths whose index entry now differs from `HEAD`,
   `git -C "$SPECS_PATH" diff --cached --name-only -z --no-renames`. Over the
   paths on both of those two lists, less every path the read before the
   commit listed that the commit's own pathspecs do not name — a change
   somebody else had staged, left as they staged it — run
   `git -C "$SPECS_PATH" restore --staged -- ':(literal)<path>' …`, and run
   nothing where none is left. Never over the commit's whole list: a path the
   commit deleted is in neither `HEAD` nor the index, and one pathspec that
   matches nothing fails the whole `restore`, which then restores nothing.

   Nothing in this commit-and-restore form is particular to the specs
   repository: `phase-handoff.md` §2.4 and the `docs-workflows` commands that
   commit into a docs repository run it against their own, with their own
   paths and message.

   **In session-branch mode** (§8), §8.2's `commit` replaces this step's
   commit and its index restore, with the same message; its `committed` and
   `files` fill §6's line.
5. **Push — only session-file commits, and only to a branch it may push.**
   **After step 4, this step pushes only where step 4 made its commit** —
   in session-branch mode, where §8.2's `commit` printed a `committed` that
   is not `null` — and the push is a command of its own, run once the
   commit's exit status has been read: never chained after the commit in
   one command line, and never after a construct that swallows its failure
   (`rc=$?`, `|| true`, `;`), the live case `phase-handoff.md` §2.5 records.
   After a landing (step 1), which makes its commit in step 4's place, the branch is `<default>`, which HEAD does not stand on: the push names it, and its three conditions below are tested for `<default>`. A non-fast-forward rejection goes to step 6's replay, which moves a branch no checkout stands on by `update-ref` alone. Where the landing already pushed its commit by refspec (step 1's move), this step has nothing to push; the here form's commit is pushed only once the open run no longer stands (step 1).
   Where step 4 made none — step 3's *nothing to commit*, or a commit git
   refused (step 6) — nothing is pushed. §3.4's flush outside session-branch
   mode runs this step after its own commit, this precondition included;
   §3.4's retry, its pushes of other plugin branches and, in session-branch
   mode, its push of the session branch push what an earlier run left, and
   take this step's three conditions, never this precondition.
   In session-branch mode the branch is the session branch, under §8.4's
   differences. Push only where all three conditions below hold, tested in order. Where one
   fails, no push is attempted and the commit stays local: step 7 emits §6's
   *not pushed* line for the first condition that failed, and step 6 has
   nothing to report.
   - **The branch is the default branch or a plugin branch (§2.2)** — the
     default branch as §3.2 names it, resolved here the same way on a run that
     ran no preflight. Any other named branch is its owner's to push — the one
     §3.3 G2 stayed on, or the code branch a direct `/dev-workflows:implement` run cut where
     `$SPECS_PATH` is the repository it runs from (§4.1) — and a push would
     publish whatever its owner has not pushed yet, a code commit their own
     push choice kept local included.
   - **There is somewhere to push.** The remote is `origin`, the one every
     other step of this reference and of `phase-handoff.md` reads (its §2.1
     says why `origin` specifically), and it must exist:
     `git -C "$SPECS_PATH" remote get-url origin` exits 0. Four more states
     leave nowhere to push, each with its own §6 line:
     - **The user's git configuration pushes this branch elsewhere:**
       `git -C "$SPECS_PATH" config --get branch.<branch>.pushRemote`, or,
       where that prints nothing, `git -C "$SPECS_PATH" config --get remote.pushDefault`,
       prints a remote other than `origin` — a fork's checkout is the usual
       case. A push to `origin` would override that configuration, and a push
       to the other remote would publish to a repository nothing here reads,
       so neither happens. The branch's upstream does not decide the remote:
       it once did, and on a fork whose default branch tracked the parent
       repository's, the push went to the parent while every other step read
       `origin`.
     - **The remote deleted the branch:** the branch was pushed to `origin`
       under its own name, and `origin` no longer has it. Pushed is read from
       its upstream —
       `git -C "$SPECS_PATH" for-each-ref --format='%(upstream)' refs/heads/<branch>`
       prints `refs/remotes/origin/<branch>` — or, where the branch has no
       upstream at all, from the remote-tracking ref a push wrote:
       `git -C "$SPECS_PATH" show-ref --verify -q refs/remotes/origin/<branch>`
       finds it. A push from a repository whose `.git/config` git cannot write
       records no upstream (`phase-handoff.md` §2.5), and a container that
       mounts that file read-only would otherwise never see this state. Gone is
       `git -C "$SPECS_PATH" ls-remote --exit-code --heads origin refs/heads/<branch>`
       exiting 2, which says the remote holds no such branch. A remote that
       renamed its default branch, and a pull request merged with *delete
       branch on merge* — while this run was still finishing included — both
       leave this state, and a push would recreate the branch the remote
       removed. A branch with no upstream whose remote-tracking ref was pruned
       reads as never pushed: the default branch is then pushed, and a plugin
       branch meets the last state below. Any other exit, an unreachable
       remote included, does not count here; the push then reports its own
       failure (step 6).
     - **The remote refused this branch before:** its push-refusal record
       stands (§1 rule 8) — `test -f "<record>"`, or else
       `git -C "$SPECS_PATH" config --get branch.<branch>.workflowsPushRefused`
       prints a date. The date the rows name is the file's content, or the
       key's; where the file is empty, `<date>` is `an earlier run`.
     - **`origin` does not have this plugin branch:** the branch is a plugin
       branch (§2.2) — never the default branch, nor §8's session branch,
       which §8.4 pushes where `origin` lacks it — and the test above reads it
       as never pushed: no upstream on `origin` under its own name, and no
       `refs/remotes/origin/<branch>`. Where either is there, the test above
       has already asked the host, as `phase-handoff.md` §2.2 rule 1 confirms
       a remote-tracking ref, and the branch is on `origin` unless the host
       said it is gone. This step never creates a plugin branch on `origin`:
       only `phase-handoff.md` §2.5 publishes one, with the deliverable its
       pull request is for. A handoff whose commit git refused leaves such a
       branch, and so does one with nothing to commit where git refused its
       switch back off the branch it cut (`phase-handoff.md` §2.3), the run
       staying on that branch; a session-file push would put it on `origin`
       with no pull request beside it. The commits stay on local
       `<branch>` until a later handoff of the branch pushes it, carrying
       every commit on it — one that commits the deliverable, or re-publishes
       the branch (`phase-handoff.md` §2.3) — or until the operator runs
       `git -C "<SPECS_PATH>" push -u origin <branch>`.
   - **`push-scope`: every commit the push would publish is a session-file
     commit.** Test it with
     `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" --specs "$SPECS_PATH" push-scope --branch <branch>`,
     which prints `{"base", "commits", "in_scope", "failed"}`: `in_scope` true is this
     condition holding; otherwise `failed` names the first commit that fails, as `sha`, its
     `reason` (`paths` for a commit touching a path that is not ARTIFACT, which it names as
     `path`, or one touching none; `merge` for a merge or a root commit) — §6's *push-scope*
     line names that commit and path. Where it exits 2, report the first line of its stderr
     and push nothing.
     Inside `specs-preflight` — §3.4's flush, its retry and its settle loop, and B4's count (§3.5), which then names no count — that report is `Specs preflight: could not measure what a push of <branch> would publish (<the first line of its stderr>), so <branch> is not pushed`, printed once for a branch in a run, and the preflight goes on.
     The script measures as follows. First the base the push is measured against:
     `refs/remotes/origin/<branch>`, the ref this push updates, where
     `git -C "$SPECS_PATH" show-ref --verify -q refs/remotes/origin/<branch>`
     finds it; else none, as on the local-only session branch a failed
     `push -u` leaves behind (§8.4), or a default branch whose remote ref was
     pruned — a plugin branch that reads as never pushed stops at the last
     state above.
     The commits the push would
     publish are
     `git -C "$SPECS_PATH" rev-list --reverse refs/heads/<branch> --not <base>`,
     or, with no base,
     `git -C "$SPECS_PATH" rev-list --reverse refs/heads/<branch> --not --remotes=origin`,
     every commit on no ref of that remote this repository has fetched. Never
     measure against the remote as a whole where the branch has a base: a
     default branch fast-forwarded locally onto a pushed `prd/` branch holds
     that branch's commits, which are on the remote but not on this branch
     there, and the push would land them, unreviewed, on the remote's default
     branch. Then, oldest first and stopping at the first that fails, each
     commit must be a non-merge commit
     (`git -C "$SPECS_PATH" rev-list --parents -n 1 <sha>` prints exactly two shas: the commit and its one parent, so a root commit, which prints one, fails too) whose every path,
     `git -C "$SPECS_PATH" diff-tree --no-commit-id --name-only -r -z --root --no-renames <sha>`,
     is an ARTIFACT path (§2.1). The parent count is what refuses a merge,
     since `diff-tree` lists no path for one. This reference makes no merge
     commit outside §8's session branch, which §8.4 measures on its own terms,
     and stages nothing but ARTIFACT paths, so a commit that
     fails the test is somebody else's — the user's own, or a deliverable whose
     push at handoff failed — or one of this reference's own into which a
     `pre-commit` hook put another path (step 4): a file the hook generated, or
     a change somebody else had pending that it swept in. Either way, whether
     that path goes out is not this reference's to decide, and §6's line names
     it.

   Where all three hold, push this branch alone:
   `git -C "$SPECS_PATH" push --porcelain -u origin <branch>`, with `-u` only
   where the branch has no upstream, or one on a remote under another branch's
   name, which a branch cut from the default branch can inherit; a same-name
   upstream on any remote, and any upstream in this repository (`.`), stand as
   they are. Where git cannot write `.git/config`, `-u` records no upstream: git pushes,
   then prints a config error (`phase-handoff.md` §2.5), which is not the push's
   outcome — step 6 reads that from `--porcelain` alone.
   `--porcelain` is what step 6 reads its outcome from. Never a bare `git push`: under `push.default=matching`, or a
   `remote.<name>.push` refspec, it pushes other branches too, whose commits
   this step never measured.
6. **Failure at any step is reported, never fatal.** A push's outcome is read
   from git's own status for the ref in its `--porcelain` output — a line
   beginning `!`, then the refspec, then a bracketed summary — never from the
   server's message text.
   - **`origin` refused the update** (`[remote rejected]`): a rule on the
     server — branch protection, a ruleset, a policy or a hook — takes no push
     of this branch. Every reason git prints after that status, in
     parentheses, counts, save one that begins with the words git or a host
     gives a push a concurrent update or a server fault broke —
     `failed to update ref`, `failed to lock`, `cannot lock ref` (a host's form
     of the first), `unpacker error`, `missing necessary objects` — which is a
     push that failed for another reason (below) and is retried. The hosts word
     their refusals differently (`… hook declined`, `push declined due to
     repository rule violations`, a policy code), so the few transient reasons
     are what is matched, and everything else is a refusal. Write its
     push-refusal record (§1 rule 8),
     `mkdir -p "$(dirname "<record>")" && date +%Y-%m-%d > "<record>"`, and
     where that fails, the older key,
     `git -C "$SPECS_PATH" config branch.<branch>.workflowsPushRefused "$(date +%Y-%m-%d)"`;
     and report. The commit stays local, and step 5 pushes this branch no more
     until the record is removed. Where neither can be written, the refusal is
     unrecorded: §6's row says so, and a later run pushes the branch again. Retrying would be refused the same way on
     every run while the commits pile up on the local branch. Name what to do
     wherever this step runs: at the end of a run, §6's *push refused* line;
     inside §3.4's flush or retry, which print no §6 line, as
     `Specs preflight: <branch> not pushed — origin refused it (<the reason in parentheses>), and this is recorded so no later run pushes it; <the remedy §6's push-refused line gives>` — or, where step 6 could record it neither way, `…, and this could not be recorded (<error>), so a later run pushes it again`.
     A rule that refuses what a commit carries, rather than the branch it goes
     to, refuses the branch that remedy names too; removing the record is then
     how the user lets a later run try again.
   - An auth failure, a remote that cannot be reached, a transient refusal
     above, or any other failure → report; the commit stays local. §3.4 retries the push on the next run whose preflight gets past its guards (§3.3); a push of `<default>` made while HEAD stands on another branch — a landing's (step 1) — §3.2's held stage retries before the guards.
     A push `specs-git.py`'s 60 s cap ended reads `the push did not finish within 60 s` as its reason.
   - **Non-fast-forward rejection** (`[rejected]`): `origin`'s branch has
     commits this one lacks, and a fast-forward cannot reach it. **Never
     force-push.** Where session-branch mode is not on — §8.1's `mode`
     printed `off` or `unsupported`, so the branch is the default branch or
     a plugin branch, never the session branch — the run takes those commits
     in itself, by a **replay** that leaves the checkout alone until one
     locked move (§1 rule 4). Run, in a Bash call of its own with a timeout
     of 420000 ms,
     `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/session-branch.py" --specs "$SPECS_PATH" replay --branch <branch> [--register-rebuild <path>] [--set-upstream]`
     — `--set-upstream` exactly where step 5's push carried `-u`, and
     `--register-rebuild` with the path the caller passed as
     `register_rebuild` (§7), where it passed one. The script fetches
     `origin`'s `<branch>`; refuses where that fetch fails, where this git
     cannot replay without a checkout (its `merge-tree` lacks `--write-tree`
     or `--merge-base`), where a rebase, merge, cherry-pick or revert is in
     progress or a lock stands, where a commit the push would publish is not
     a session-file commit (step 5's `push-scope`, measured again against
     the fetched ref), and where another worktree has `<branch>` checked
     out; replays each commit the push would publish onto `origin`'s with
     `merge-tree` and `commit-tree` — an appended file both sides changed
     settled as §8.2 step 3 settles a block-shaped file or `follow-ups.md`,
     `origin`'s version first and the commit's entries after it, an
     overwritten one taken in the commit's version whole, refused where
     `origin` deleted it, a security
     register both sides changed rebuilt from the merged records with
     `register_rebuild`'s script, and any other path both sides changed
     refused — dropping a commit whose change `origin` already holds; moves
     `<branch>` onto the result as §1 rule 4 says, refusing where the
     checkout switches to or from `<branch>` while it moves; and only then pushes it,
     at most three attempts in all, a second or third only where that push
     is rejected as non-fast-forward again. The 420 s are the script's
     bounded fetches and pushes — three attempts of a fetch and a push, each
     capped at 60 s and killed 2 s after that, as `workflows-core:bounded-run`
     caps a call: 372 s — plus room for the replays and register rebuilds,
     which nothing bounds, under the Bash tool's 600 s ceiling. A branch is
     not left half-moved because of that margin, though: the script holds
     SIGTERM, SIGHUP and SIGINT while it moves a branch, and acts on one only
     once the branch and the checkout agree. Anywhere else it ends a running
     fetch or push at once, passing the signal to git's whole process group,
     and lets any other call run to its end before it stops; a signal it has
     not acted on by the time it prints its JSON changes nothing that JSON
     says.

     It prints one JSON object — `moved`, `pushed`, `attempts`, `replayed`
     and `dropped` (commit ids), `tip`, `porcelain` (the `--porcelain`
     status line for `<branch>` that the last attempt's push printed, or
     `null` where that attempt made no push or its push printed none),
     `moves`,
     `upstream_error` and `refused` (`null`, or `{reason, path}`, with
     `paths` too on `would-overwrite`) — and the first of these that holds
     names the §6 row:
     1. `pushed` is true → *replayed and pushed*.
     2. `moved` is false and `refused` is set → nothing moved: *push
        rejected*, its reason clause naming `refused` (§6).
     3. `replayed` is empty → `origin`'s `<branch>` already held every
        change this branch carries, and nothing was left to push: *already
        there*.
     4. Otherwise `moved` is true and the push did not land: *moved, not
        pushed*, naming why by the first of these that holds — `refused`
        is set: a later attempt refused, its reason clause naming it;
        `porcelain` holds `[rejected]`: `origin` moved on again during each
        of the `attempts` attempts; `porcelain` holds a refusal as the first
        bullet above reads one: write the push-refusal record as that
        bullet does, and take the row's refused form; any other `porcelain`,
        or none: the push failed, as the second bullet reads it.

     Where the script exits 2 with nothing on stdout, nothing moved: *push
     rejected*, its reason clause `session-branch.py could not run (<the
     first line of its stderr>)`. Where it exits 2 having printed its JSON
     first, it stopped after it moved the branch (`moved` is true there):
     read that JSON by the same four cases, so a `pushed` that is true still
     gives *replayed and pushed*; where case 4 applies, its why is
     `session-branch.py stopped (<the first line of its stderr>)`, ahead of
     every other. Where the Bash call ends with no exit status of its own —
     the harness ended it at its 420 s timeout — nothing the script printed
     says what moved: *push rejected*, its reason clause
     `session-branch.py did not finish within 420 s, so <branch> may already stand on the replay (git -C "<SPECS_PATH>" log -1 <branch> shows it); the next run whose preflight gets past its guards retries the push where it stands on <branch> or <branch> is a plugin branch`
     — §3.4, which a preflight reaches only past §3.3's guards, retries the
     branch a run stands on and every other local plugin branch.
     A default branch the run is not standing on is §3.2's held stage's to push, before the guards, so the next run's preflight retries it whether or not it gets past them.

     **In session-branch mode** nothing is replayed: a rejection of the
     session branch is §8.4's, and one of a plugin branch §3.4 retries takes
     *push rejected* naming that branch, its reason clause
     `session-branch mode is on, which replays nothing`, and its remedy
     wrapped in the session branch's `lift` and `put-back` as §6 gives it.
     Wherever the replay does not push, the commits stay on local `<branch>`.

     Report wherever this step runs: at the end of a run, the §6 row;
     inside §3.4's flush or retry, which print no §6 line, that row in its
     `Specs preflight:` form (§6), whatever the replay did, a push
     included. On a branch the run is not standing on, the *push rejected*
     remedy names the switch first, and the switch back after it:
     `run git -C "<SPECS_PATH>" switch <branch>, git -C "<SPECS_PATH>" pull --rebase --no-autostash origin <branch> and git -C "<SPECS_PATH>" push origin <branch>, then switch back to <the branch the run stands on>`.
     The switch is not optional: §3.4's retry pushes branches the run is not
     standing on, and a `pull` run from another branch merges `<branch>`'s
     remote commits into that one instead. The exceptions are the
     `checked-out` reason, whose remedy §6 gives: it runs in the worktree
     that has `<branch>` checked out, and names no switch, which git refuses
     for a branch another worktree has checked out; and `checkout-moved`,
     whose row names no remedy at all (§6).
   - **`index.lock` present** (a concurrent session holds the repo) → report and
     skip; **never delete a lock file**. The artifacts stay in the working tree
     and the next run's preflight flushes them.
   - **The commit fails** — a `pre-commit` or `commit-msg` hook rejects it, a
     signature cannot be made, or a merge is in progress, during which git
     refuses a pathspec commit → report git's error or the hook's output; never
     retry and never `--no-verify`. The artifacts stay staged, and a later
     run's preflight flushes them (§3.4) once git accepts the commit.
7. **Emit the §6 outcome line**, plus the full §5 notice repeated verbatim when
   a guard fired at §3.3. **Where the run printed its report before this step,
   the report is the run's account, and nothing after it restates it.** From
   the report to the end of the run — or, where a later phase cedes control
   (the exception at the head of §4), to that hand-off — the run prints only
   what the command's own steps after the report tell it to print: its
   maintenance, feedback, follow-up and cost lines, any question one of those
   steps asks, a context-hygiene line a step places there, and this outcome
   line with its §5 block and §6's appends, followed by any line the command
   names to follow it. Never a summary, recap or restatement of the report,
   and never one of the report's own lines again, its `Code repo:` or
   `Phase handoff:` line among them: a recap written after the report states
   its facts a second time, from memory, and is the part the user reads last.

### 4.1 Where the commit lands

- **In session-branch mode** (§8) — on the session branch, whatever the
  checkout stands on, and a deliverable branch carries no session file. The
  bullets below hold outside the mode.
- **On a branch the preflight stayed on and would have left, HEAD still standing there at the end** (§4 step 1's landing) — on `<default>`, by the landing, the checkout unmoved. Where the landing is refused, nowhere this run: the files are held in the working tree, and a later run's held stage (§3.2) settles them — with HEAD on `<default>`, or in session-branch mode whatever branch HEAD is on, it drops the hold, the files left to §3.4's flush or §8.2's `commit`; outside that mode and off `<default>`, it reports on every run, until it is dropped, an entry held for a cause that will not pass, landing none of those, and, once no `index.lock` stands, lands one held for a cause that passes, save where it is held again. Under a run typed mid-run whose start took no snapshot, nowhere either while the open run still stands, and nothing is held: that run's terminal commit takes the files (§4 step 1).
- **A run typed mid-run that holds no stay** (§3.5) — on HEAD's branch, by §4 step 1's here form, where HEAD stands at the end on the branch it started on, less the overwritten files uncommitted at its start, which stay uncommitted (§4 step 1 (1)), and unpushed while that run stands; where its start took no snapshot, nowhere while that run stands, and, once it no longer stands, with every session file uncommitted on the branch (§4 step 1); and where the run's own handoff moved HEAD off the branch it started on, as the bullets below say. The bullets below hold everywhere else.
- **A command that opened a specs-repo branch at handoff** (`/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/update-spec`, `/epics`, `/design`, `/implement`, `/ready`, `/frames`, `/prd-ground`, `/prd-proposal`, `/harvest-decisions`, `/promote-decisions`, `/conformance`, `/docs-workflows:release-notes`, and every `/brd-*` command — every command that offers `phase-handoff.md`'s `handoff-to-main`, `/promote-decisions` through `architecture-promotion.md` §11.2) — on that `idea|prd|ard|spec|epics|design|ready|brd|frames|kb|conformance/*` branch, so the push updates the pull request already open. Two commits on one branch: the deliverable, then the artifacts — save where the handoff committed nothing (`phase-handoff.md` §4.1's *Commit failed* or *Nothing to commit*), when the artifacts' commit alone lands on that branch — or, where a handoff with nothing to commit switched back off the branch it cut (`phase-handoff.md` §2.3), on the branch the run returned to, the cut branch removed or left empty; where git refused that switch back, on the cut branch, as after *Commit failed* — and, where `origin` does not have the branch, stays there unpushed until a later handoff of it pushes the branch or the operator does (§4 step 5). Every `/brd-*` command opens on the shared `brd` prefix (`phase-handoff.md` §2.9); `/prd-ground` opens on that same shared `brd` prefix on the BRD route, or on the shared `prd` prefix (with `/create-prd`, `/update-prd`, `/prd-proposal` and `/docs-workflows:release-notes`) on the idea route — it left the `/brd-*` glob the day its own rename shipped, but not the prefix sharing, which is why it is named here rather than folded into "every `/brd-*` command". A later `/brd-*` run — or `/prd-ground`, on the BRD route — that reuses the branch a prior phase of the same BRD opened lands there rather than on the default branch.
- **The same command when the user declined git at handoff** — `phase-handoff.md` §4.3's option 2 (*just write the files*) or option 3 (*Cancel*) — the repo stays on the branch the preflight settled on (the default branch; the one §3.5 B3 or §3.3 G2 kept; or the one it stayed on because §3.3 G1 fired, because `status` could not run (§2.1) so §3.5 switched nothing, or because git refused §3.5's B2 or B4 switch or the preflight stopped before reaching that switch (§1 rule 5, or a start that never finished its preflight, §4 step 1)), and the
  deliverable is uncommitted there. `commit-artifacts` still runs and commits
  **only** the bookkeeping paths — by §4 step 1's landing onto `<default>`, where the preflight stayed on a branch it would have left (this list's second bullet); the uncommitted deliverable is untouched,
  because it is an OTHER path.
  This is deliberate: either decline is about the deliverable — option 2's "I'll handle git" refers to it, and option 3 states nothing more — and the bookkeeping still has to reach the maintainer.
  The outcome line states plainly that the deliverable remains uncommitted, save on §1 rule 5's NOT FINISHED line and the rows §6's declined paragraph excepts: the *Misrooted* row, and the *Blocked (G0)* row of a run whose start set `specs_git: blocked`, where that paragraph says it takes none.
- **Every other command** — on the default branch, unless §3.3 G2 left the run
  on a branch the plugin does not manage, §3.5 B3 kept it on a plugin branch
  keyed to this run, or the preflight stayed on the branch it stood on because §3.3 G1 fired, because `status` could not run (§2.1) so §3.5 switched nothing, or because git refused §3.5's B2 or B4 switch or the preflight stopped before reaching that switch (§1 rule 5, or a start that never finished its preflight, §4 step 1) — save a branch it stayed on and would have left, whose run takes §4 step 1's landing onto `<default>` (this list's second bullet). The commit follows the branch the preflight settled on; it
  never switches: where the preflight stayed on a branch it would have left, the commit is §4 step 1's landing onto `<default>`, without moving the checkout.
- **`/dev-workflows:implement` on a direct run from inside the specs repository** (its Phase 0),
  where the specs repository is the repository the run changes — on the code
  branch the run cut there, which step 5 does not push unless its name carries
  one of §2.2's prefixes; or, where the run stops before it cuts one, on the
  branch HEAD then stands on — the one it started on, or the default branch
  where its Phase 1.4's fresh start switched to it, which step 5 pushes as it
  pushes the default branch on any run.

## 5. Notice contract — the guards must be impossible to overlook

Where `scripts/specs-git.py` runs the two entry points, it renders every block below, and the run prints what it returns.

A guard fires precisely when the plugin has decided **not** to do something the
user is relying on. A single dim line in a long run is how that becomes a silent
loss, so every guard emits a structured block rather than a sentence, at both
the point of detection and again in the run's last printed output.

Every notice carries four parts, in this order:

1. **What was found** — the concrete state, with the branch name, the file
   count, or the path list. Never "an issue was detected".
2. **What the plugin did NOT do** — stated as the consequence for the user's
   data.
3. **The exact commands to resolve it**, ready to paste, with `$SPECS_PATH`
   already substituted.
   In this section's guard blocks — G0's, G1's and G2's, in every form below — this part is the *Fix* line, and it holds commands only, with no comment and no prose, so each of its lines runs as pasted in bash and in zsh, whose interactive shell does not read `#` as a comment unless `interactivecomments` is set: what the reader needs to know about them goes in the block's other parts, and a block with nothing to run, or nothing it can give ready to paste, leaves its *Fix* line empty. A notice elsewhere that takes its four parts from this section — a `require-on-main` stop (`phase-handoff.md` §4.4), or a command's own — is not held to commands only, and may set its commands in a line of prose; the zsh limit is the one this section sets on it, that a command is never followed by `#` prose on its line, so it stands on a line of its own or is quoted whole inside a sentence, and for a `require-on-main` stop `phase-handoff.md` §4.4 sets the rest.
   **A *Fix* line that switches to `<default>` makes the branch first where none exists.** Where `refs/heads/<default>` names no commit and `<default-ref>` names one — a clone made with `--branch` onto another branch, say, or one whose local `<default>` was deleted — each *Fix* line below that opens with `git -C "<SPECS_PATH>" switch <default>` (G2's, in its plain form and in its form on the session branch itself, and G1's on a merged branch the run would have left) has that switch replaced by `git -C "<SPECS_PATH>" branch --no-track <default> <default-ref> && git -C "<SPECS_PATH>" branch --set-upstream-to=<default-ref> <default>; git -C "<SPECS_PATH>" switch --no-guess <default>`, the rest of the line standing as it is. Its first command makes the branch at `<default-ref>` with no configuration write, as §3.5 makes B2's and B4's, for the reason given there: a switch left to make the branch takes git's guess, whose upstream write, where `.git/config` cannot be written, leaves the index and the working tree on `<default>`'s tree with HEAD where it was and exits 1. Its second sets the upstream git's guess would have set, where `.git/config` can be written; the `;` after it lets a failed write stop nothing, and a failed write moves nothing. Where `.git/config` cannot be written, that step prints git's config error and a hint whose suggested `git branch --set-upstream-to=origin/refs/heads/<default>` names no branch — git 2.43's own, which no `-c advice.…` setting silences — and the switch still runs: neither is a failure. Its switch is `--no-guess`, so no path through the line reaches git's guess. The line runs again as it stands after git refuses its switch and the operator moves the files git named: the second run's first command prints `fatal: a branch named '<default>' already exists` and skips the upstream step, which the first run took, and its switch runs; no git message is silenced. G1's `add` and `commit` stay behind the switch's `&&`, so a refused switch commits nothing. Where the branch exists, the line stands as it is. It is judged each time the block is printed — at the run's start, and again where its end repeats the block.
4. **What happens if it is ignored** — one clause.

Severities: **blocking** (G0 — the terminal commit will not run) and **advisory**
(G1, G2 — the commit still runs, but somewhere the user should know about). Both
use the same four-part shape; only the wording of part 2 differs.
G1 where the run's own files are to be committed on `<default>` (§4 step 1's landing) stays advisory: the commit still runs, as that landing at the run's end, aimed at `<default>` rather than at the branch the run stands on; §6's line says what came of it, and nothing is lost whatever that is, as its form below says.

The `Specs repo:` emission (§6) **repeats the notice in full** when a guard
fired. A notice printed only at Phase 0 of a long run is a notice the user has
scrolled past by the time the run ends.

**G0 — blocking:**

```
⚠ SPECS REPO — THIS RUN'S ARTIFACTS WILL NOT BE COMMITTED

Found:    <SPECS_PATH> is on a detached HEAD (<sha7>), not on a branch.
Not done: this run's feedback, cost, follow-ups, and resume pointer will NOT be
          committed and will NOT reach the plugin maintainer. A commit made here
          would be reachable from no branch and eligible for deletion by git's
          garbage collector, so the plugin refuses to make one.
Fix:      git -C "<SPECS_PATH>" switch -c rescue/<YYYY-MM-DD>
If ignored: the artifacts stay in your working tree, uncommitted and intact; the
          next run's preflight picks them up once HEAD is on a branch — the one
          Fix creates, or an existing one you rejoin instead with
          git -C "<SPECS_PATH>" switch <branch>
```

**G1 — advisory:**

```
⚠ SPECS REPO — UNCOMMITTED FILES THAT ARE NOT THE PLUGIN'S

Found:    <SPECS_PATH> has <N> uncommitted change(s) outside the plugin's
          artifact area: <path list>
Not done: the preflight did not switch branches, and did not commit or push
          these files. Those files are yours, and switching branches would
          carry them along. This run's own artifacts WILL still be committed at
          the end of the run — commit-artifacts stages only the §2.1 artifact
          paths.
Fix:      git -C "<SPECS_PATH>" status
          git -C "<SPECS_PATH>" add <path list> && git -C "<SPECS_PATH>" commit
If ignored: nothing is lost — your files stay uncommitted, and this run's
          artifacts are committed alongside them. But the preflight ends here
          on EVERY later run too, so the leftover flush and the branch
          settle (stages 2-3) stay skipped until these paths are committed
          or removed. A deliverable whose handoff was declined — "just
          write the files" — is the usual cause, and it is a supported
          state — this is what it costs.
```

**On a branch the run would have left** — HEAD on a plugin branch (§2.2) the preflight stays on though it would have left it, outside session-branch mode, where §3.3 keeps a stay — this run's own artifacts are to be committed at its end on `<default>`, not on `<branch>`, by §4 step 1's landing, so G1's *Not done* line reads instead `the preflight did not switch branches, and did not commit or push these files. Those files are yours, and switching branches would carry them along. This run's own artifacts WILL be committed at the end of the run on <default>, not on <branch>, <which no key of this run names | which is merged into <default> | where <command>'s run in this session was open when this run started>, and your checkout is not moved.`, the alternative the stay's kind selects — `unkeyed`, `merged` or `mid-run`, in that order. Where the stay's `merged` flag is set, its *Fix* line is `git -C "<SPECS_PATH>" switch <default> && git -C "<SPECS_PATH>" add <path list> && git -C "<SPECS_PATH>" commit` and its *If ignored* line `nothing is lost — your files stay uncommitted, and nothing of this run's is committed with them. But the preflight ends here on EVERY later run too, so the leftover flush and the branch settle (stages 2-3) stay skipped until these paths are committed or removed. Fix commits them on <default>, not on <branch>, and where git refuses its switch it commits nothing, git naming the files in its way; committed on <branch>, they make it read unmerged, and no later run removes it. A deliverable whose handoff was declined — "just write the files" — is the usual cause, and it is a supported state — this is what it costs.`: the plain block's *Fix* line, run on a merged `<branch>`, would commit there, and the switch comes first so that it does not. Otherwise its *Fix* line is the plain block's, and its *If ignored* line `nothing is lost — your files stay uncommitted, and nothing of this run's is committed with them. But the preflight ends here on EVERY later run too, so the leftover flush and the branch settle (stages 2-3) stay skipped until these paths are committed or removed. A deliverable whose handoff was declined — "just write the files" — is the usual cause, and it is a supported state — this is what it costs.` Its *Found* line is the block's own, and `<path list>` on its *Fix* line is the shell-quoted list the plain block's *Fix* line gives. At the run's end, after a landing that did not land the run's whole change — §6's *held*, *held, stuck* or *there* row, step 3's *nothing to commit* line, or a landing that held a path alone while the rest landed, whose row carries the *held, stuck* append (§6) — or after §1 rule 5's `NOT FINISHED` line, which an end that stopped early prints in place of a row, G1's *Not done* line reads instead `the preflight did not switch branches, and did not commit or push these files. Those files are yours, and switching branches would carry them along. This run's own artifacts were to be committed at the end of the run on <default>, not on <branch>, <which no key of this run names | which is merged into <default> | where <command>'s run in this session was open when this run started>, and your checkout is not moved; the Specs repo: line above this notice says what came of them.`, which leaves to the run's `Specs repo:` outcome line what came of the artifacts; and after a landing that landed the run's whole change on `<default>`, no path held alone, it reads `the preflight did not switch branches, and did not commit or push these files. Those files are yours, and switching branches would carry them along. This run's own artifacts were committed at the end of the run on <default>, not on <branch>, <which no key of this run names | which is merged into <default> | where <command>'s run in this session was open when this run started>, and your checkout is not moved; the Specs repo: line above this notice names that commit.`, since the artifacts it said would be committed then were; the landing form's *Fix* and *If ignored* lines stand, true whatever the outcome.

**Under a run typed mid-run** (§3.5) — whatever the stay's kind and flag, and whether or not the run stays — no guard's block names a switch or a commit while the open run stands on the branch, since a switch would move the checkout under that run and a commit would take its work in progress. G1's *Not done* line is the landing form's, its alternative `where <command>'s run in this session was open when this run started`, where the run stays, and the plain block's where it does not; its *Fix* line is empty, as this section's rule gives a block with nothing to run; and its *If ignored* line reads `nothing is lost — these may be <command>'s files in progress, and nothing is to be run here while that run is open: let it finish, or end it, first; if you stopped that run, /clear, typing <command> again[ with <keys>], or HEAD leaving the branch ends it. Nothing of this run's is committed with them. Until these paths are committed or removed, the preflight ends here on EVERY later run too, so the leftover flush and the branch settle (stages 2-3) stay skipped.` G2, in every variant below, takes an empty *Fix* line and the *If ignored* line `nothing is to be run here while <command>'s run in this session is open on <branch>: let it finish, or end it, first — if you stopped that run, /clear, typing <command> again[ with <keys>], or HEAD leaving the branch ends it; this run's Specs repo: line, at its end, says what came of its artifacts.`, which leaves to the run's `Specs repo:` outcome line (§6) what came of them, at the start as at the end. `<command>` is the open run's. Each *If ignored* line names the ends §3.5 gives a run the user stopped — `/clear`, its command typed again with its key set (`<keys>`, the open run's keys joined by `and`, the bracketed part only where its record holds one), and HEAD leaving the branch — as information, never as a command to run while the open run stands.

The run's end repeats the block in the form that matches what the end does. **Where the stay stands** — HEAD still on `<branch>`, and §4 step 1's re-test against the end's commit key has not dropped it — the end takes the landing, and repeats the landing form: with its *Not done* line the landed one (above) where it landed the run's whole change on `<default>`, no path held alone; after any other outcome — held (an `index.lock` at the landing's start among the causes), held stuck, `there`, `nothing`, a landing that held a path alone while the rest landed, or the `NOT FINISHED` line — with its *Not done* line the one for a landing that did not land the run's whole change (above), its *Fix* and *If ignored* lines as they are. **Where no stay stands** — HEAD has moved off `<branch>`, the re-test dropped the stay, or the run kept none — the plain block, since the commit then lands where §4.1 puts it. Its *Not done* line says this run's own artifacts WILL still be committed, and its *If ignored* line that they are committed alongside your files, which is false after a line that committed none of them — step 3's *nothing to commit* line, §6's *Locked*, *Commit failed* and *mid-run* rows, and the session-branch rows that commit nothing (*no identity*, and *the script could not run*) — and need not be true after the `NOT FINISHED` line, which an end that stopped early prints whether or not it had committed them. So after each of those lines — the **not-committed form** — its *Not done* line reads instead `the preflight did not switch branches, and did not commit or push these files. Those files are yours, and switching branches would carry them along. This run's own artifacts were to be committed at the end of the run — commit-artifacts stages only the §2.1 artifact paths; the Specs repo: line above this notice says what came of them.`, and its *If ignored* line `nothing is lost — your files stay uncommitted, and the Specs repo: line above this notice says what came of this run's artifacts. But the preflight ends here on EVERY later run too, so the leftover flush and the branch settle (stages 2-3) stay skipped until these paths are committed or removed. A deliverable whose handoff was declined — "just write the files" — is the usual cause, and it is a supported state — this is what it costs.`, both of which leave to the run's `Specs repo:` outcome line what came of the artifacts; its *Fix* line stands. **Under a run typed mid-run**, the mid-run form, rendered from the plain block the record keeps, its *Not done* line chosen as the same outcomes choose it: the landed one where a stay's landing landed the run's whole change, the not-landed one's after any other outcome of a stay, and, where no stay stands, the plain block's, or the not-committed form's after a line that committed none of the run's files or the `NOT FINISHED` line (§6).

**G2 — advisory:**

```
⚠ SPECS REPO — ON A BRANCH THIS PLUGIN DID NOT CREATE

Found:    <SPECS_PATH> is on branch `<branch>`, which is neither the default
          branch (`<default>`) nor a plugin branch (idea/ prd/ ard/ spec/
          epics/ design/ ready/ brd/ frames/ kb/ conformance/).
Not done: the preflight did not switch away from it — the plugin manages only
          branches it created. This run's artifacts WILL be committed on
          `<branch>`, and not pushed.
Fix:      git -C "<SPECS_PATH>" switch <default>
If ignored: the artifacts land on `<branch>` and reach the maintainer when you
          push or merge that branch; run Fix only if that is the wrong place
          for them.
```

**In session-branch mode** (§8) G2's *Not done* line reads `the preflight did not switch away from it — the plugin manages only branches it created. This run's artifacts WILL be committed on session/<identity>, the session branch this specs repository uses because its default branch takes no push, and not on <branch>.`, its *Fix* line is empty, and its *If ignored* line `nothing changes for the artifacts, and nothing is to be run for them: they reach <default> through session/<identity>'s pull request.` Where `<branch>` is that session branch itself, the *Not done* line reads instead `the preflight did not switch away from it. It is this specs repository's session branch, which the plugin commits to only while nothing stands on it, so this run's artifacts will NOT be committed.`, the *Fix* line `git -C "<SPECS_PATH>" switch <default>`, and the *If ignored* line `the artifacts stay in your working tree, and the first run after you switch back commits them.` Where §8.1 resolves no identity, nothing is committed in the mode until one is set, so G2's *Not done* line reads instead `the preflight did not switch away from it — the plugin manages only branches it created. Session-branch mode is on and no identity names its branch, so this run's artifacts will NOT be committed until one is set.`, its *Fix* line is empty, and its *If ignored* line `the artifacts stay in your working tree, and the first run after you set GIT_USER_INITIALS, or git -C "<SPECS_PATH>" config user.initials, to your initials commits them.` In session-branch mode these variants take precedence over the direct `/dev-workflows:implement` variant below, since a direct run's artifacts then go to the session branch, or, with no identity, are not committed, whatever branch it cuts (§4.1).

**On a direct `/dev-workflows:implement` run from inside the specs repository**
(§4.1) the run changes code here, so it cuts a branch of its own (its
Pre-Phase 3), and the artifacts are committed on that branch, whose name the
preflight does not know yet — or, where the run stops before it cuts one, on
the branch HEAD then stands on: `<branch>`, or `<default>` where the run's
Phase 1.4 answered a fresh start and switched to it before the stop. Its *Not
done* line reads instead `the preflight did not switch away from it — the
plugin manages only branches it created. This run changes code here, so its
artifacts WILL be committed on the branch it cuts for that, or, if it stops
first, on the branch it then stands on — <branch>, or <default> after a fresh
start — and not pushed unless that branch is <default> or its name carries one
of this plugin's prefixes.`; its *Fix* line is empty; and its *If ignored*
line reads `nothing is to be run here: the artifacts stay on that branch until
it is pushed or merged, and reach the maintainer then.` The code commit carries only the session files it takes; the rest
are committed after the run's push choice, by `commit-artifacts`, so pushing
at that choice does not take them (`/dev-workflows:implement` Phase 0 says
the same). In session-branch mode (§8) the code commit takes none: §8.3 lifts
them before its branch and again before its commit, and puts them back after it.

## 6. The outcome line

Where `scripts/specs-git.py` runs the two entry points, it renders every line below — `end` the rows, `start` their `Specs preflight:` forms — and the run prints what it returns.

`commit-artifacts` step 7 emits exactly one of these, prefixed `Specs repo:`.
Where `specs-git.py` stopped early (§1 rule 5), its `Specs repo: NOT FINISHED — …` line is the outcome line, in place of a row, and none of the clauses this section appends to a row follows it.
The caller places it per its own contract (§7) — inside its final report where
the report is the run's last output, or as its own terminal block where the
report was composed earlier, which holds nothing but what §4 step 7 lets
follow the report.

**A file count is singular at one.** In every row below that gives a file count, and in the
`Specs preflight:` and session-branch forms printed after the table, where `<N>` is 1 the line reads
`(1 file)`, never `(1 files)` — the *here* row and §3.2's `Specs preflight: committed <sha7> (<N> files) on <default>: …` line among them.

| Case | Line |
|---|---|
| Committed and pushed, on a plugin branch | `Specs repo: committed <sha7> (<N> files) on <branch> — pushed` |
| Committed and pushed, on the default branch | `Specs repo: committed <sha7> (<N> files) on <default> — pushed straight to <default>, and no pull request was opened: this plugin lands its session files there without review; to land them through a pull request of your own instead, turn on session-branch mode (§8) with git -C "<SPECS_PATH>" config workflows.sessionBranch true — where a container mounts this repository's .git/config read-only, run it on the host` |
| Committed on the session branch and pushed (§8) | `Specs repo: committed <sha7> (<N> files) on session/<identity> — pushed; <F> session file(s) not on <default> yet: merge its pull request, or open one with gh pr create --head session/<identity> --base <default>`, `<F>` the count of paths `git -C "$SPECS_PATH" diff --name-only -z --no-renames <default-ref>...refs/heads/session/<identity>` prints |
| Session-branch mode, no identity (§8.1) | `Specs repo: NOT COMMITTED — session-branch mode is on and no identity names its branch; set GIT_USER_INITIALS (or git config user.initials), and the next run commits these files` |
| Session-branch mode, the script could not run (§8) | `Specs repo: NOT COMMITTED — session-branch.py could not run (<the first line of its stderr>); the files stay in your working tree, and the next run commits them` |
| Committed, not pushed — not a branch this plugin pushes (§4 step 5) | `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: this plugin pushes only the default branch and the branches it creates, so <branch> is yours to push; the artifacts reach the maintainer when you push or merge it` |
| Committed, not pushed — no remote to push to (§4 step 5) | `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: this specs repo has no origin remote` |
| Committed, not pushed — the user's git configuration pushes the branch elsewhere (§4 step 5) | `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: your git configuration pushes <branch> to <remote>, not to origin, which is the remote this plugin reads; push it where it belongs yourself` |
| Committed, not pushed — the remote deleted the branch (§4 step 5) | `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: origin has no <branch> any more, so it was renamed or deleted there, and this step does not recreate it; the commit stays on local <branch>` — and, where `<branch>` is the default branch, `; if origin renamed it, git -C "<SPECS_PATH>" remote set-head origin --auto names the new one` |
| Committed, not pushed — `origin` does not have this plugin branch (§4 step 5) | `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: origin has no <branch>, and this plugin puts a branch of its own there only by handing off its deliverable; the commit stays on local <branch> until a later handoff of <branch> pushes the branch, or you run git -C "<SPECS_PATH>" push -u origin <branch>` |
| Committed, not pushed — origin refused the branch before (§4 step 5) | `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: origin refused pushes to <branch> on <date> (<record>), and every commit since stays on local <branch>; to land the commits on local <branch>, put them on a branch of their own and open a pull request from it — git -C "<SPECS_PATH>" branch --no-track session-files-<YYYY-MM-DD> <branch> && git -C "<SPECS_PATH>" push -u origin session-files-<YYYY-MM-DD> — then, standing on <branch>, git -C "<SPECS_PATH>" reset --keep origin/<branch>; once origin takes pushes to <branch> again, rm "<record>"` |
| Committed, push refused by origin (§4 step 6) | `Specs repo: committed <sha7> (<N> files) on <branch> — push REFUSED by origin (<the reason in parentheses>): a rule there takes no push of <branch>, so this is recorded and no later run pushes it; to land the commits on local <branch>, put them on a branch of their own and open a pull request from it — git -C "<SPECS_PATH>" branch --no-track session-files-<YYYY-MM-DD> <branch> && git -C "<SPECS_PATH>" push -u origin session-files-<YYYY-MM-DD> — then, standing on <branch>, git -C "<SPECS_PATH>" reset --keep origin/<branch>; once origin takes pushes to <branch> again, rm "<record>"` |
| Committed, not pushed — the push would publish other commits (§4 step 5 `push-scope`) | `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: the push would also publish commits that are not this plugin's session-file commits, the oldest <sha7> <subject>, which carries <path>; push <branch> once they are ready to go, and the artifacts go with them` — `which carries <path>` reads `which is a merge commit` where `push-scope`'s `failed.reason` is `merge`, and `which changes no file` where its `path` is `null` — or, where that oldest commit is this run's own, `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: a pre-commit hook added <path>[, and <M-1> more] to this commit, so it carries more than this plugin's session files; check what the hook added before you push <branch>` |
| Committed, origin's branch had moved on — replayed and pushed (§4 step 6) | `Specs repo: committed <sha7> (<N> files) on <branch> — pushed after a replay: origin's <branch> had moved on, so the run replayed its <K> commit(s) onto it[, <D> of them already there and dropped][; <the register clause>]` |
| Committed, origin's branch had moved on — already there (§4 step 6) | `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed, and nothing is left to push: origin's <branch> had moved on and already holds every change <branch> carries, so <branch> now stands on it[; <the register clause>]` |
| Committed, origin's branch had moved on — moved, not pushed (§4 step 6) | `Specs repo: committed <sha7> (<N> files) on <branch> — origin's <branch> had moved on, so the run replayed its <K> commit(s) onto it[, <D> of them already there and dropped][; <the register clause>] and moved <branch> there, but <why>; the commits are on local <branch>, and a later run retries the push` — or, in its refused form, from `but` on: `but push REFUSED by origin (<the reason in parentheses>): ` followed by the *push refused by origin* row from `a rule there` on, as that row reads in this run, its variants below included — the one where step 6 could record the refusal neither way, and, on the default branch, the remedy that says the mode turns on |
| Committed, push rejected as non-fast-forward, nothing moved (§4 step 6) | `Specs repo: committed <sha7> (<N> files) on <branch> — push REJECTED: origin's <branch> has commits this one lacks, and the run could not take them in: <reason clause>; run git -C "<SPECS_PATH>" pull --rebase --no-autostash origin <branch>, then git -C "<SPECS_PATH>" push origin <branch>` |
| Committed, push failed for any other reason | `Specs repo: committed <sha7> (<N> files) on <branch> — push FAILED (<reason>); the commit is local and a later run retries it` |
| Nothing to commit | `Specs repo: no session artifacts to commit` |
| Locked | `Specs repo: skipped — another session holds the repo (index.lock); the next run picks the artifacts up` |
| Commit failed | `Specs repo: NOT COMMITTED — the commit failed (<the first line of git's error or the hook's output>); the artifacts stay staged, and a later run commits them once git accepts the commit (a merge concluded, a hook satisfied)` |
| Blocked (G0) | `Specs repo: NOT COMMITTED — see the notice below`, followed by the §5 G0 block verbatim |
| Misrooted (§3.1: a misplaced `$SPECS_PATH`, `session-hygiene` §7's `env-check`, its §6's *Stop*, or §4 step 1's comparison of the `SPECS_PATH` half of the run's `Environment:` line), whether or not the environment conditions hold | `Specs repo: NOT COMMITTED — SPECS_PATH is misplaced, or the run's environment no longer matches the one it recorded; see the notice below`, followed by the notice that set the flag, verbatim: the §3.1 notice, `specs-root-check`'s stop, `session-hygiene` §7's `Environment changed:` notice, or its §6's `RESUME_ENVIRONMENT_CHANGED:` stop line |
| Held — the preflight stayed on a branch it would have left, HEAD still there, and the landing was refused for a cause that passes (§4 step 1) | the *held* row, given after this table |
| Held, stuck — as *held*, for a cause that will not pass (§4 step 1) | the *held, stuck* row, given after this table |
| Mid-run — a run typed mid-run whose own change could not be committed apart from the open run's, or that has no start, or no snapshot, to tell it apart (§3.5) | the *mid-run* row, given after this table |
| There — the landing found the run's change already on `<default>` (§4 step 1) | the *there* row, given after this table |
| Here — a run typed mid-run that holds no stay, its change committed on HEAD's branch, the overwritten files uncommitted at its start apart, unpushed while that run stands (§4 step 1's here form) | the *here* row, given after this table |
| Gate failed on environment, on a run carrying neither flag | *(no line at all — silent no-op)* |

**The landing's rows** (§4 step 1). In the *held* and *held, stuck* rows, and in the landing's append below, `<which no key of this run names | which is merged into <default> | where <command>'s run in this session was open when this run started>` is the alternative the stay's kind selects — `unkeyed`, `merged` or `mid-run`, in that order — `<command>` being the open run's, and `<branch>` the branch the preflight stayed on; the mid-run alternative speaks of the run's start, so it holds where the open run has ended since. `<sha7>` is the held commit's first seven characters, and `<specs-git.py's path>` `scripts/specs-git.py`'s own resolved path.

- The *held* row reads `Specs repo: NOT COMMITTED — this run's preflight stayed on <branch>, <which no key of this run names | which is merged into <default> | where <command>'s run in this session was open when this run started>, and its files could not be committed on <default> without leaving it: <reason clause>; they stay in your working tree, <held for <default>, and the next run tries again | and the next run, in session-branch mode, drops this hold and commits them as that mode commits session files>` — the first where the cause passes and the next run's held stage (§3.2) tries again; the second where the reason clause is `checked-out`'s fifth or sixth alternative, since its next run is in session-branch mode, where that stage drops the hold and §8.2's `commit` takes the files.
- The *held, stuck* row reads `Specs repo: NOT COMMITTED — this run's preflight stayed on <branch>, <which no key of this run names | which is merged into <default> | where <command>'s run in this session was open when this run started>, and its files cannot be committed on <default> without leaving it: <reason clause>; they stay in your working tree, and no landing takes them; dropping the hold — as a later run on <default> or in session-branch mode does, or as you can — leaves them ordinary uncommitted files, which a later commit takes: see their change with 'git -C "<SPECS_PATH>" show <sha7>', put it on <default> yourself if you want it there, then run 'python3 "<specs-git.py's path>" --specs "<SPECS_PATH>" land --default-ref <default-ref> --drop-held <sha7>'`.
- The *mid-run* row reads `Specs repo: NOT COMMITTED — <command>'s run in this session is still open on <branch>, and this run's own changes could not be committed apart from that run's: <reason clause>; they stay in your working tree, and that run's terminal commit takes them with its own; if you stopped that run, /clear, typing <command> again[ with <keys>], or HEAD leaving the branch ends it, and a later run's commit takes them`, `<command>` the open run's and `<branch>` HEAD's: for a here form whose apply refused a path, the open run still standing at its end; with the `no-preflight` reason clause, for an `end` with no start that found a run open (§3.5); with the `no-snapshot` reason clause, for a run typed mid-run whose start took no snapshot, the open run still standing at its end (§4 step 1); and, with the `unfinished` reason clause, for an `end --resume` whose here-form journal it could not finish, HEAD still on the journal's branch and the open run still standing there (§4 step 1), `<branch>` then that branch.
- The *there* row reads `Specs repo: nothing to commit on <default>, which already holds this run's session-file changes; they were taken out of your working tree on <branch>`.
- The *here* row reads `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed yet: <command>'s run in this session is still open on <branch>, so this run committed what changed since it started and moved nothing under that run; <the next push of <branch> this plugin makes, by that run or a later one, carries it | <branch> is yours to push, as the notice above said>, and that run's files are as they were in your working tree; if you stopped that run, /clear, typing <command> again[ with <keys>], or HEAD leaving the branch ends it`, `<sha7>` and `<N>` the here form's commit's, `<branch>` HEAD's and `<command>` the open run's; its first alternative on the default branch or a plugin branch, the second on a branch this plugin does not push (§3.3 G2, §4 step 5). Where §4 step 1 (1)'s guard left paths out of the change, the *start-dirty* append follows it: `; <path>[, …] stayed out, as they stand in your working tree: uncommitted when this run started, they are left for a later commit on <branch>`, `<path>` each path (1) left out and `<branch>` HEAD's. It promises nothing about whose commit takes them, only that they stay for a later one on `<branch>`. The same append follows the row the here form's push gives once the open run no longer stands, a replay's row included, the *nothing to commit* line that the here form, or a landing, gives where (1) left out every path that changed, and a landing's *there* row.

**After a landing**, the line is the row steps 5 to 7 give its commit on `<default>`, `<branch>` in that row being `<default>`, followed, in this order, by `; this run's preflight stayed on <branch>, <which no key of this run names | which is merged into <default> | where <command>'s run in this session was open when this run started>, so its files were committed on <default> without leaving <branch>, and taken out of your working tree there`, `<branch>` the stayed branch; where the run's start could not list the uncommitted paths (§2.1), `; its preflight could not list the uncommitted paths, so every session file uncommitted on <branch> went with them`; where (1)'s guard left paths out of the change, the *start-dirty* append (the *here* row, above), `<branch>` the stayed branch; where the landing's rebuild of a security register renumbered a record, the register clause (below) for it, after `; `; where a path was held alone while the rest landed, the *held, stuck* append, `; <path>[, …] could not go with them: <reason clause>; they stay in your working tree, and no landing takes them; dropping the hold — as a later run on <default> or in session-branch mode does, or as you can — leaves them ordinary uncommitted files, which a later commit takes: see their change with 'git -C "<SPECS_PATH>" show <sha7>', put it on <default> yourself if you want it there, then run 'python3 "<specs-git.py's path>" --specs "<SPECS_PATH>" land --default-ref <default-ref> --drop-held <sha7>'`; and last the declined append (below). §3.2's `Specs preflight: committed <sha7> (<N> files) on <default>: …` line for each held entry the landing landed first is printed before the row.

**The landing's reason clause** says why a landing, the here form's apply or a held entry's retry was refused, by its `reason`, `<path>` being the refused path. `<onto>` is `<default>`, or, in the here form, HEAD's branch, which `<default>` names too in a clause the here form gives, since that is the branch its apply was refused on:

- `dropped` → `this run's copy of <path> drops a line that <onto> does not hold, which only you can settle`
- `edited` → `this run's copy of <path> changes or removes an entry, or the file's header, that was there when the run started, which only you can settle`
- `forms` → `<path> has other line endings on <default> than in your working tree`
- `deleted` → `this run deleted <path>, which <default> holds in another version`
- `folder-gone` → `<default> does not hold the folder <path> is in`
- `register-rebuild` → `<path> needs its register rebuilt, <and this command hands the run no register.py to rebuild it | and that rebuild failed>`, the first where the call carried no `--register-rebuild`, the second where it did
- `moved` → `<default> moved twice while the run was committing on it`
- `checked-out` → `another worktree, <path>, has <default> checked out, and <the push of the commit by refspec failed (<reason>) | there is no origin to push the commit to | your git configuration pushes <default> to <remote>, not to origin | origin has no <default> | origin refuses pushes to <default> (<the refusal>), so from the next run session-branch mode takes these files | origin refused pushes to <default> on <date> (<record>), so from the next run session-branch mode takes these files | origin refuses pushes to <default> (<the refusal>), but this could not be recorded (<error>, the configuration write's), so a later run pushes <default> again>`, `<path>` being that worktree's, and the alternative the refusal's `detail.outcome` selects: `failed`, a refspec push that failed, and `rejected`, one `origin` rejected as non-fast-forward because its `<default>` moved on between the build and the push — nothing was pushed, and the next run builds on the newer `<default-ref>` — the first, `<reason>` being `detail.text`, the push's own reason (its status line's summary, git's first error line, or `no status line` where it gave none); `no-remote`, `elsewhere`, `<remote>` being `detail.remote`, and `remote-deleted` (§4 step 5's states), the next three, the fourth also for `origin-lacks`, where `<default-ref>` names no commit ((3)), so the clause holds whether `origin` never had `<default>` or no longer has it; `refused`, a push `origin` refused and §4 step 6 recorded, the fifth, `<the refusal>` being `detail.text`, `origin`'s reason, or git's own `[remote rejected]` where it gave none — or, where step 6 could record it neither way (`detail.record` empty), the seventh, its unrecorded form, which mirrors the *push refused* row's: `<error>` is `detail.record_error`, the configuration write's error, and nothing turns session-branch mode on, so a later run's held stage (§3.2) pushes again; `refused-before`, a refusal already recorded, the sixth, worded as the *refused before* row words it, since that record holds the date it was written and never the refusal's text: `<date>` is `detail.date` and `<record>` `detail.record`, the record's path, or the configuration key where that is the record (§6's `<record>`)
- `locked` → the `locked` reason clause below, as it stands — an `index.lock` that stood when the landing started, or a ref's lock
- `no-preflight` → `this run stopped before its preflight, so nothing tells its files from that run's`, on the *mid-run* row alone
- `no-snapshot` → `this run's start took no snapshot of the session files then uncommitted, so nothing tells its files from that run's`, on the *mid-run* row alone
- `unfinished` → `<branch> moved on without the commit this run was making on it when it was cut off, so that commit was dropped unfinished`, on the *mid-run* row alone, `<branch>` the here-form journal's

The apply's six — `dropped`, `edited`, `forms`, `deleted`, `folder-gone` and `register-rebuild` — and `checked-out` with nowhere to push (`no-remote`, `elsewhere`, `remote-deleted`) or nothing to build on (`origin-lacks`, §4 step 1 (3)) are causes that will not pass; `moved`, `locked` and `checked-out`'s other outcomes pass. `no-preflight`, `no-snapshot` and `unfinished` are no landing's causes, and hold nothing: `no-preflight` and `no-snapshot` say why an end committed nothing at all, and `unfinished`'s journal entry is dropped, which no run retries — so, like every refusal of the here form, `unfinished` is marked permanent.

When a guard fired at §3.3 G1 or G2, the outcome line is followed by that
guard's §5 block, repeated verbatim — G1's in the form §5 gives the run's end: where the stay stands, its landing form, whose *Not done* line is the not-landed one unless the end landed the run's whole change on `<default>`, no path held alone; and its plain form wherever no stay stands — HEAD has moved off the branch the preflight stayed on, §4 step 1's re-test dropped the stay, or the run kept none — whose *Not done* and *If ignored* lines are the not-committed form's after a line that committed none of the run's files, and after the `NOT FINISHED` line (§5); under a run typed mid-run, G1's and G2's in their mid-run form (§5). Where the *push-scope* line's hook variant
fired, a path it names may be one that block, or the append below, calls
uncommitted, since the hook swept it into this run's commit: follow them with
`Specs repo: <path>[, …] is now committed in <sha7>, put there by a pre-commit hook, and not pushed`.

**`<record>` in the refused rows is the push-refusal record's path** (§1 rule 8). Where the record is the older configuration key instead — found there, or written there because the file could not be — the row names `branch.<branch>.workflowsPushRefused` in its place and clears it with `git -C "<SPECS_PATH>" config --unset branch.<branch>.workflowsPushRefused`, which needs a writable `.git/config`. **Where step 6 could write neither**, the *push refused* row says so in place of `so this is recorded and no later run pushes it`: `but this could not be recorded (<error>, the configuration write's), so a later run pushes <branch> again`; it names no `rm` or `config --unset`, and on the default branch no session-branch switch, since nothing turns the mode on.

**The rows of a non-fast-forward rejection** (§4 step 6). In the three rows a replay gives where it moved the branch or found nothing left to push — *replayed and pushed*, *already there* and *moved, not pushed* — `<sha7>` is the first seven characters of the replay's `tip`, the commit `<branch>` now stands on: this run's own commit as replayed, or, where that was dropped, the commit `origin`'s branch already held. `<K>` counts the commits in `replayed` and `dropped` together, and the `<D>` clause, the commits in `dropped`, is there only where that is not 0. **The register clause** is there once for each `security/<slug>/` that `moves` names: `the rebuild of security/<slug>/ renumbered <move>[, <move>…], and the next run that records in that register lists the lines that cite an old number`, each `<move>` reading `[SEC#<from>] → [SEC#<to>] (<origin>, <whose number>)` — `the local number` on a move whose `side` is `run`, the number the replayed commits gave it, which the report and follow-up lines of the run that made them cite, and `origin's number` on one whose `side` is `remote`, the number a teammate already saw. No record holds such a move, so the next run that records anything in that register reports it again, with the lines to correct (`security-register-format.md` §2). Where `upstream_error` is set, the *replayed and pushed* row adds `; its upstream could not be set (<upstream_error>)`. `<why>`, in *moved, not pushed*, is the reason step 6 names: `a later attempt could not take origin's newer commits in: <reason clause>` (where the reason is `checkout-moved`, its clause there reads `… so <branch> was not moved again; …`, since an earlier attempt moved it), `origin's <branch> moved on again during each of its <attempts> attempts`, `the push FAILED (<the status line's bracketed summary and its reason, or no status line>)`, or `session-branch.py stopped (<the first line of its stderr>)`.

**The reason clause** says why the replay refused, by `refused.reason`, `<path>` being `refused.path`:

- `conflict` → `both sides changed <path>, or the folder holding it, and the run cannot settle it`
- `register-rebuild` → `both sides changed the security register <path>, which only a rebuild settles, and this command hands the run no register.py to rebuild it` where the call carried no `--register-rebuild`, else `…, which only a rebuild settles, and that rebuild failed`
- `would-overwrite` → `moving the checkout would write over <path>[ and <M> more], which you changed, left untracked or ignore — once that is clear, the next run that commits session files on <branch> settles the push itself`, `<M>` being the paths in `refused.paths` less that one
- `cannot-replay` → `this git cannot replay without a checkout (its merge-tree needs --write-tree and --merge-base, git 2.40 or later)`
- `in-progress` → `a rebase, merge, cherry-pick or revert, or an unresolved conflict, is in progress in the checkout (<path>)`
- `locked` → `<path> is held by another git process, or was left by one that died, and this plugin never deletes a lock`
- `push-scope` → `the push would now also publish <path's first seven characters>, which is not one of this plugin's session-file commits`
- `checked-out` → `another worktree, <path>, has <branch> checked out`
- `fetch-failed` → `fetching origin's <branch> failed`
- `branch-moved` → `<branch> moved while the run was replaying it`
- `cannot-move` → `git could not move the checkout onto the replay (a folder it cannot write, say), and nothing moved`
- `checkout-moved` → `the checkout switched to or from <branch> while the run was moving it — another session's preflight or handoff, say — so <branch> was not moved; the next run that commits session files on <branch> settles the push itself`

Step 6 adds three of its own: `session-branch.py could not run (<the first line of its stderr>)`, `session-branch.py did not finish within 420 s, …` (step 6 gives it whole), and `session-branch mode is on, which replays nothing`. **Where the reason is `checked-out`, the remedy runs in that worktree**, in the row and in its `Specs preflight:` form alike, and names no switch, which git refuses for a branch another worktree has checked out: from `; run git` on, the line reads `; run git -C "<path>" pull --rebase --no-autostash origin <branch>, then git -C "<path>" push origin <branch>`. **Where the reason is `checkout-moved`, the line ends at its reason clause**, in the row and in its `Specs preflight:` form alike, and names no remedy: another session put the checkout where it now stands, and a `pull` run there could merge `<branch>`'s remote commits into another branch. **Where the reason is `session-branch mode is on, which replays nothing`, the remedy is wrapped in the session branch's `lift` and `put-back`**, since the overlay keeps session files modified in the checkout, which the switch and the pull both refuse: from `; run` on, the line reads `; run python3 "<the script's path>" --specs "<SPECS_PATH>" lift --branch session/<identity>, then <the remedy as it reads without this wrapping, from its first git on>, then python3 "<the script's path>" --specs "<SPECS_PATH>" put-back --branch session/<identity> --default-ref origin/<default>`. **The remedy never stashes.** `--no-autostash` is spelled out because a `rebase.autoStash` setting turns a bare `--rebase` into an autostash, which, where putting the user's changes back conflicts, leaves conflict markers in the user's own file and a stash behind, and still exits 0; without it the pull refuses up front while anything in the checkout is uncommitted, and changes nothing.

**Inside §3.4's flush and retry**, which print no §6 line, each of these four rows and the *push FAILED* row prints in its `Specs preflight:` form: `Specs preflight: <branch>` in place of `Specs repo: committed <sha7> (<N> files) on <branch>`, and, on a branch the run is not standing on, the *push rejected* remedy §4 step 6 gives there, which switches first, save for `checked-out`, whose remedy runs in the worktree that has `<branch>` checked out, and `checkout-moved`, which names none (above). The *Locked* and *Commit failed* rows, which a flush can meet, print there with `Specs repo:` replaced by `Specs preflight:`.

**In session-branch mode** (§8) the not-pushed rows name the session branch as `<branch>`, and the *push refused* and *refused before* rows, when they name it, read from `to land the commits` on instead `once origin takes pushes to session/<identity>, rm "<record>"`, `<record>` being `session/<identity>`'s — the session branch is never stood on, so no `reset` is named for it. Where the run carries `session_branch_created: <base short sha>` (§8.2), the line, whichever row it is save the *Misrooted* row, appends `; this run created local session/<identity> at <base short sha>`. Where `sync.conflict` is not empty, append, for the paths `sync.conflicts` gives the source `<default-ref>`, `; merging <default> into session/<identity> left <path>[, …] unsettled — settle them in its pull request`, and for those it gives the source `origin/session/<identity>`, `; origin's copy of session/<identity>, pushed from another clone, was not merged in: on <path>[, …] one clone changed what the other clone's copy still holds unchanged (an entry edited or removed, the header edited, the file deleted) — make the two copies agree, by making the same change on the clone that still holds it (standing on <default> there; a pending cost file the other relocated is relocated there too, never deleted by hand) or by undoing it on the other; the next run on the clone you changed commits it, and once that is pushed, a later run here merges and pushes`; and where `sync.error` is set, `; the merge of <default> into session/<identity> could not run (<sync.error>), and the next run tries again`. Where §8.2's `unsettled` is not empty, the line, whichever row it is, appends, once for each path `unsettled` names, `; <path> and session/<identity>'s version of it each hold a change the other lacks, so it was left out of this commit and is as it was in your working tree — git -C "<SPECS_PATH>" show session/<identity>:<path> shows the branch's version`, and after them, once, `; once a copy left out is the branch's version with your own entries added after it, in the line endings your checkout gives the file, the next run commits it, and an edit or removal of an entry the branch your specs checkout stands on holds can then be made again; until then lift will not discard it, so each move of the specs checkout is skipped`. Where §8.2 printed `stranded` above 0, append `; your local <default> still holds <K> commit(s) origin refused, whose files are on session/<identity> now — to drop them, standing on <default>, run python3 "<the script's path>" --specs "<SPECS_PATH>" lift --branch session/<identity> && git -C "<SPECS_PATH>" reset --keep origin/<default> && python3 "<the script's path>" --specs "<SPECS_PATH>" put-back --branch session/<identity> --default-ref origin/<default>`, `<K>` being `stranded`. The *push-scope* row, where §8.4's test fails with `reason: branch-path`, reads instead `Specs repo: committed <sha7> (<N> files) on session/<identity> — not pushed: its pull request would also change <path>, which is not one of this plugin's session files[, and the branch's newest merge commit is <merge sha7> <subject>]; push session/<identity> once that change is ready to go, and the artifacts go with it`, `<path>` being `failed.path`, and the bracketed clause there only where `failed.sha` names a merge commit. The *push rejected* row, for a push of the session branch, reads `Specs repo: committed <sha7> (<N> files) on session/<identity> — push REJECTED: origin's session/<identity> has commits this clone lacks, pushed from another clone under the same identity; a later run takes them in and pushes` — ending instead `…under the same identity, which a later run takes in only once the two clones' copies agree, as this line says` where `sync.conflicts` gives the source `origin/session/<identity>`. Where `mode` printed `unsupported`, the run's line, whichever row it is save the *Misrooted* and *Blocked (G0)* rows and any line on a detached HEAD, none of which names a branch the files stay on, and the *held*, *held, stuck*, *mid-run* and *there* rows, none of which commits the files this run, appends `; session-branch mode is on for this clone, but this git's merge-tree cannot merge without a checkout (it needs --write-tree and -X), so these files stay on <branch> until git is upgraded`. And where a *push refused* line names the default branch and step 6 recorded it, the run is the one that turns the mode on, so its remedy, from `to land the commits` on, reads instead `from the next run on, session files go to session/<identity>, a branch of your own whose pull request lands them (session-branch mode), and these commits' files go there too` — with `a session branch of your own, once GIT_USER_INITIALS names it` in place of `session/<identity>` where §8.1 resolves no identity.

The *push refused* and *refused before* rows make `session-files-<YYYY-MM-DD>` with `branch --no-track`: a user's `branch.autoSetupMerge=always` would make it track `<branch>`, a write that, where `.git/config` cannot be written, leaves the branch made and exits 1, so the `&&` would stop the push. Under git's default setting `--no-track` changes nothing.

When the deliverable is still uncommitted because the user declined git at handoff (§4.1), on either option, append to the line, whichever row it is save the *Misrooted* row — the *held*, *held, stuck*, *mid-run* and *Blocked (G0)* rows included, where the session files stay uncommitted beside it: `; the deliverable at <path> remains uncommitted, as you asked`, `<path>` being the declined handoff's declared paths that `git status` still lists, written as `phase-handoff.md` §4.1 writes `<artifacts>`. The *Misrooted* row takes none, so that no `git status` runs in a path the run has just found wrong: the deliverable is still uncommitted there, but that line does not say so. Nor does the *Blocked (G0)* row of a run whose start set `specs_git: blocked`, save where the `SPECS_PATH` half of the `Environment:` line printed now is the one the record its start made holds (§4 step 1's comparison, which that flag otherwise skips) and `git status` runs there: `git status` runs only in the repository the start checked, and the row prints as it does without the append wherever it cannot.

## 7. Caller contract

A command that writes anything into `$SPECS_PATH` must do all four of these.
Omitting any one of them is a defect, not a style choice.

1. **Run `specs-preflight` (§3) through the `workflows-core:specs-git` skill's `start`** at run start, once the run key
   set is known, in whichever of §3's cases the command falls; a run that
   stops on its address after resolution runs none, nor does one that stops
   before the preflight on a check of its own inputs needing no specs-repo state (§3). Phase 0 in most
   commands. Carry any returned `specs_git: blocked` or `specs_git: misrooted`
   flag for the whole run, and `specs_git: misrooted` from `workflows-core:addressing`
   §3 `specs-root-check` where its stop ended the run before any preflight, and
   from `workflows-core:session-hygiene` §7's `env-check` or its §6's *Stop* for the rest of the run.
2. **Run `commit-artifacts` (§4) through the skill's `end`** as the last action of the run,
   after `resume.md` (where one is written) and after the cost phase — or, where
   a later phase cedes control to another skill or to an open-ended interactive
   stretch, immediately before that hand-off (§4's exception). **A run that
   stops reaches it too**: a command that can stop states once, in a paragraph
   headed **Ending early.**, what each of its stops leads to — §4's refusal tail,
   a stop before the preflight skipping only the preflight (§3), save where a
   stop's own text names another route — because a `stop` read on its own ends
   the run where it stands, short of this step.
3. **Emit the §6 outcome line exactly once**, wherever `commit-artifacts`
   ran — at the end of the run, or immediately before the hand-off in the
   cede-control case above.
4. **Never restate this reference's rules** — cite the section number. A rule
   copied into a command is a rule that goes stale.

**One optional input, `register_rebuild: <absolute path>`**, to `specs-preflight`
and to `commit-artifacts` alike: the script that rebuilds a security register
(`security-register-format.md` §1), which is `security-workflows`' own
`register.py` — a `workflows-core` reference cannot name another plugin's
root, so the caller hands the path over, and the `workflows-core:specs-git` skill passes it to `specs-git.py start` and `end` as `--register-rebuild <path>`. Either entry point passes it to
§4 step 6's replay, wherever it reaches one (§3.4's flush and retry, or the
terminal push), as `--register-rebuild <path>`, and the replay runs it only
to rebuild a register both sides changed, as
`python3 -I <path> rebuild --specs <a temporary root> --slug <slug>`.
`/security-workflows:scan` passes `${CLAUDE_PLUGIN_ROOT}/scripts/register.py`
at both calls. A caller that passes nothing — every other command — gets the
replay all the same, save that a register both sides changed refuses it
(§6's `register-rebuild` reason clause).

**The run's state record.** What the two entry points share, and what a run once carried only in its conversation, `scripts/specs-git.py` keeps in one file per Claude Code session and command, `~/.claude/dev-workflows/specs-git/<session id>/<command>.json`. The session id is `CLAUDE_CODE_SESSION_ID`, which Claude Code sets in every Bash tool subprocess, equal to a hook's `session_id` and updated on `/clear` (its environment-variables page, https://code.claude.com/docs/en/env-vars) — the `session_id` `cost-emission.md` §1 reads off the transcript's name. The record holds the `start` call's arguments, its key set among them, the flags and the notice that set `specs_git: misrooted`, the guard block §4 step 7 repeats and the paths it lists, `<default>`, `<default-ref>`, `remote` and the offline clause, `session_branch`, `mode` and `session_branch_created`, the branches §3.5's B2 and B4 left, the stay — the branch the preflight stayed on though it would have left it, its kind, its `merged` flag and its reason (§4 step 1's landing — each preflight derives its own, and clears it where it leaves that branch; a `start --resume` goes on with the preflight its earlier call began, the stay that call saved included; `end` asks for one where the start never finished its preflight) — the snapshot of the session files dirty when the start took it, each path's version kept as a blob, which §3.2's held stage updates for each path it lifts and each call narrows, as it returns, to the paths still dirty (§4 step 1), the open run this one was typed under (§3.5), `started`, the time the start began, which its JSON returns and the run passes back as `end --started` and `declined --started` — and as `start --rerun --started` and `start --resume --started`, where its preflight runs again or goes on (§3.5), and every `next` a preflight call returns, a `start` call's or a `replay --for start` call's, carries the record's `started` as `--started`, whether or not that call was given one — so that each reads and writes that record alone, or, where that stamp names no record any longer, a file of the run's own named for it, `<command>.<stamp>.json`, never another run's `<command>.json`, `started_before`, the `started` of each start of the run whose record a re-run, or a continuation that starts afresh and names it by `--started` or takes it up as its own (§3.5), took over, so that the run reaches its own record by any stamp its starts returned, `call_returned`, false from the first write of a plain start or of a continuation given no `--started` — calls whose run learns the record's stamp only from their JSON — until that call returns its JSON, an error's included, and never written false by a named call or a re-run, whose run holds a stamp already, so that a continuation given no `--started` knows a record a start the harness stopped left before its run learned the stamp — marked true again where an end restores it from parked (§3.5) — and `protects`, false on a record a later start of the same command with the same run key set, or where either start recorded none, parked or marked so, and true on one a start with another key set parked (§3.5), the branches §3.4's `-D` advisory has named, the once-a-run reports `start` has printed, the deliverable paths a declined handoff recorded (§6), the run's `Environment:` line, and where an interrupted `start` or `end` stands. `start` opens a fresh one for its command, setting aside whatever stood there — save on a re-run (§3.5) and on its own continuation: one that goes on with its record, names it by `--started`, or takes up as its own a record marked `call_returned: false` with this call's arguments (§3.5) — or, where that is an open run of the same command (§3.5), parking it under a name carrying its `started` stamp, marked `parked: true`, and `protects: false` where the two starts' run key sets are the same or either is empty, for that run's own end; its JSON's `replaced` names a record it set aside or, with `parked: true`, one it parked. It removes every other session's record more than seven days old; the skill's `declined` adds to it, and creates one where the run's start made none, marked as made by no start, so that `end` takes its declined paths from it and compares no `Environment:` line (§4 step 1); `end` reads it, and compares the `SPECS_PATH` half of the run's `Environment:` line, as the record holds it, with the same half of the line `session-hygiene.md` §7's Bash call prints now (§4 step 1). `end`, and `replay --for end` where `end` handed the run a replay, remove it as they return: once they have rendered a row's line, or at step 1's silent no-op. Where an error stops either past its first write, the record stays for `end --resume`, and the `end_commit` it holds, saved before the commit is made, lets that call find a commit a kill cut off. A `start --resume` continues a record only where it stands at one of `start`'s own stages, its arguments are the call's, and it was saved within the last 15 minutes, and one given no `--started` only a record marked `call_returned: false`, meeting any other as a plain start does (§3.5); an `end --resume`, only where it holds an `end_commit` and was saved within the last 15 minutes. **Why it is safe.** It lives outside every repository, so no staging sees it, and `/dev-workflows:implement`'s `run-state.py remove`, which removes files in the code repository's git directory, cannot reach it. One file per session and command keeps two sessions on one specs repository apart, and a different command typed mid-run (§3.5) off the open run's record; the same command typed twice is kept off it by parking, and each of its two runs' ends, re-runs and continuations by `--started`, any stamp the run's starts returned naming its record. The session id survives a compaction, which the conversation's text does not. A nested run is another command, and starts only after its parent's `end` (§4's exception: `/product-workflows:brd-split`'s *Ground now*). A subagent carries its parent's session id, and no agent runs either entry point. A run started `--inline` by another command calls neither. A run whose id changes before its end — a `/clear`, or a resume that hands it a new one — finds no record there, and its `end` runs as a run with no preflight does (§4 step 1), on the flags the run passes, and compares no `Environment:` line, since §4 step 1 compares one only where the record the run's start made stands, and knows no stay, so it commits on the branch HEAD stands on, save where another run of the session is open there (§3.5). It is not kept in the specs repository's git directory because §3.1's gate fails exactly where that directory is missing or unwritable, while a not-a-repository `$SPECS_PATH` with a `specs-root-check` signal still sets the flag whose notice `end` repeats. Where `CLAUDE_CODE_SESSION_ID` is unset, the script runs neither entry point (exit 2, nothing done), and the run follows this reference's prose instead.

## 8. Session-branch mode — a default branch that takes no push

Where the specs repository's default branch takes no direct push — branch protection, a ruleset, a policy or a hook — this reference keeps the run's session files on a per-user **session branch**, and the user lands them through its pull request. Everything above stands; this section says only what changes in the mode. `${CLAUDE_PLUGIN_ROOT}/scripts/session-branch.py` does the git plumbing, every call `--specs "$SPECS_PATH"`, and a change to either is a change to both: the script holds this section's plumbing and §4 step 6's replay, which runs only outside the mode and whose output that step reads — save §8.1's `mode` and §8.4's `push-scope`, which this reference reaches through `${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py`, the second of them that script's own code. Each call this section makes prints one JSON object; exit 2 means it could not run, which is reported with the first line of its stderr while the run goes on (§1 rule 5), inside the preflight as `Specs preflight: session-branch.py could not run (<the first line of its stderr>)`, and inside `commit-artifacts` (§4) — the `lift` and `put-back` around step 2's catch-up, the §8.2 `commit` that `lift` runs on `unpreserved` (§8.3), and step 4's `commit` where that `lift`'s commit had already made this run's commit — as `Specs repo: session-branch.py could not run (<the first line of its stderr>)`, printed before §6's line.

Inside `start` and `end`, `scripts/specs-git.py` makes this section's calls itself. A command that moves the checkout or commits session files by its own text — `/dev-workflows:implement` on a direct run from inside the specs repository — and `phase-handoff.md` around its own moves still make them as this section says.

### 8.1 When the mode is on

At §3.2 — and at §4 step 1 on a run that ran no preflight — run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" --specs "$SPECS_PATH" mode --default <default>` — the same `mode` `session-branch.py` carries, reached through `specs-git.py` like this reference's other primitives — never on a run carrying `specs_git: misrooted`, which commits nothing anyway. It prints `{mode, source, identity, identity_rung, branch}`. `mode` is `on` where `git config --bool workflows.sessionBranch` prints `true`, the user's own opt-in, which this reference reads and never writes; or where the default branch's push-refusal record stands (§1 rule 8), which §4 step 6 writes when `origin` refuses a push to the default branch. Both are local to the clone. `mode` is `unsupported` where one of them is set but this git's `merge-tree` cannot merge without a checkout (it needs `--write-tree` and `-X`): the run goes on as with the mode off, and §6's line says so. `branch` is `session/<identity>`, `<identity>` from `branch-naming.md` §2's first three rungs, never its prompt.

Where the mode is on, carry `session_branch: <branch>` for the whole run, and follow §3.2's fetch with a second, of the session branch alone: `git -C "$SPECS_PATH" fetch origin "+refs/heads/<session branch>:refs/remotes/origin/<session branch>"`, best-effort and silent where it fails, as it does while `origin` has no such branch; one fetch naming both branches would fail whole in that state. §3.1's gate, `specs_git: misrooted`, G0 and G1 gate the mode exactly as they gate everything else. G2 no longer decides where the files land: in the mode they go to the session branch whatever the checkout stands on (§5).

**No identity.** Where `branch` is null the run commits nothing in the mode: its session files stay in the working tree for the next run, the moves §8.3 wraps run unwrapped — git refuses one only where a dirty session file is in its way, and the step reports that as it reports any refused switch or pull — and §6's *no identity* line names `GIT_USER_INITIALS`.

**The session branch is never stood on.** Where a worktree has it checked out, `commit` and `put-back` exit 2 naming it and move nothing, since moving a branch under its own checkout leaves that checkout's index and files behind it; §6's *could not run* line carries the name, and G2's notice (§5) says to switch back.

### 8.2 Committing

In the mode nothing in this reference commits a session file on the checked-out branch. Where §3.4's flush or §4 step 4 would commit, run `… commit --branch <session branch> --default-ref <default-ref> --message "<that step's message>"`, adding `--include-ahead` where HEAD is the default branch. It:

1. creates the session branch where it does not exist, at the commit the checkout's files come from (`git merge-base HEAD <default-ref>`);
2. commits every session file the overlay holds (§8.3) — each path `git status` reports dirty and each where the branch differs from HEAD, by §2.1's classifier, a deleted one as a deletion — onto it through a temporary index. A working copy that is HEAD's version, or the version this worktree was last given, is not committed — save the files `--include-ahead` carries, which HEAD holds: the overlay is simply not in place there (a `lift` not yet put back, a second worktree, a switch back from the session branch, a file removed by hand), or another worktree moved the branch on, and the branch keeps its own. An absent session file is a deletion only under `dev-workflows-cost/` — `cost-emission.md` §9 relocates a pending cost file and deletes it, the one session file a run deletes — and only where HEAD holds it or this worktree held it, which the script records per worktree (path and version, in `session-branch-placed.json` under the git directory); any other absent session file is put back. A working copy the session branch has no version of, a working copy of an overwritten file or of a security register (step 3), and a deletion are committed as they are, with nothing settled. A working copy of a block-shaped file or `follow-ups.md` (step 3) that differs from the branch's version is committed as it is where the branch still holds the version this worktree was last given, by its record or, where it has none (a `lift` clears them), HEAD's: only the working copy changed, so a hand edit goes through. A block-shaped one is committed followed by every entry of the version this worktree was given that neither it nor HEAD's version holds, in the given version's order, entries compared with their line endings taken as `\n`; `follow-ups.md`, where a line of the given version is missing from both it and HEAD's version, lines compared the same way, is united with the given version over HEAD's by `git merge-file --union`. An entry or task line HEAD holds that the working copy dropped is a deliberate removal and stays removed, `implementation-format.md` §1's move of a block among them — save that, where a task only the session branch holds is put back, a task ticked next to it comes back beside its open copy, as git's union keeps such a pair. An entry or task only the session branch holds is put back whatever dropped it — a restore of HEAD's version, a removal by hand, or an edit, whose old version then stays beside the edited one — so no working copy can remove or replace one until the session pull request has merged: a visible duplicate rather than a lost entry. Where the branch holds another version (another worktree's commit or a merge moved it on, or a lift was never put back), the working copy is settled with the branch's version as step 3 settles a file, from the version at `git merge-base HEAD <session branch>`. Every version is read as a checkout writes it, so that their line endings agree, and the result is written back, so an entry only the branch holds survives. Where that cannot be done — for a block-shaped file, an entry of the merge base's version that one of the two versions edited or removed while the other still holds it, the branch's version included (a teammate's removal merged in, say, that the copy still holds), or headers that differ; for either shape, versions whose line endings differ, the one case `follow-ups.md` is refused in (`git merge-file --union` matches lines byte for byte, so it would keep each task in CRLF beside its copy in LF), which, where the branch holds the given version, refuses only where something must be put back — the file is left out of the commit and as it is in the working tree, and listed in `unsettled` (§6), since committing it as it is would drop the branch's entries or bring back one it removed. With `--include-ahead` it also commits the files of the commits on the local default branch that `<default-ref>` lacks, where every one of them is a session-file commit (the ones a refused push left there). It moves neither the checkout, the index nor HEAD;
3. then merges in `<default-ref>`, and `origin`'s copy of the session branch where one exists (another clone pushed it under the same identity), each where the branch lacks it, as `NOISSUE Merge <ref> into <session branch>` — a fast-forward where the branch holds nothing of its own, else `git merge-tree --write-tree -X ours`, after which each block-shaped file and `follow-ups.md` that the merge base (`git merge-base <session branch> <ref>`), the branch and `<ref>` each hold differently is settled from those three versions, whatever `merge-tree` wrote for it, and written into the merge through a temporary index. A **block-shaped** file — `implementation.md`, `_security.md`, and the feedback and cost files, pending ones included, under `dev-workflows/`, `dev-workflows-feedback/` and `dev-workflows-cost/` — is a header followed by entries, each running from its format's dated `## ` heading to the next: it settles as the branch's version followed by each entry of `<ref>`'s that the branch's lacks, in `<ref>`'s order, one empty line before each, and is refused where the two headers differ or an entry of the merge base's version is missing from one side while the other still holds it, an edit or a removal made on one side alone; an entry both sides removed stays removed, one both edited alike is kept once, and one they edited differently stays in both edited versions, a visible duplicate rather than a lost edit. Two cases follow from that: an entry one side removed and the other edited keeps the edit, the removal lost without a word; and a last entry both sides extended, with no heading of their own, stays twice, once with each side's tail. `follow-ups.md`, one task per line, settles by `git merge-file --union`, the branch's lines first. So a teammate's entries and this run's are each kept once and whole — never by git's `union` driver for a block-shaped file, which matches lines, not entries, and fuses two entries that share lines into one. Either shape is also refused where the three versions are not all in one line-ending form, since a line in CRLF never matches its copy in LF. Where a file is refused, or `merge-tree` reports any other path conflicted, that `<ref>` is not merged at all, no merge commit, and the paths are listed in `sync.conflict`; the next run tries again. An overwritten file (`resume.md`, `pr-draft.md`, `*-implementation-gaps.md`, and a security register's `register.json` and `register.md`) keeps this run's version whole, being unset (`-merge`) in one marked block in the repository's own `info/attributes`, which no commit carries; the block gives `follow-ups.md` git's `union` driver and names no block-shaped file, so a merge of one the user makes stops on a conflict rather than fusing two entries;
4. and brings each working copy that still matches the branch's previous version up to the merged one.

It prints `{committed, files, paths, created, stranded, ahead_not_session, unsettled, sync}`. `committed: null` is §4 step 3's *nothing to commit*. `created: true` says step 1 created the session branch in this call, whether or not step 2 then found anything to commit. Where a call prints it, take `<base short sha>` at once: the first seven characters of `git -C "$SPECS_PATH" merge-base HEAD <default-ref>`, the commit step 1 created the branch at. §3.4's flush reports its own call's creation in its `Specs preflight:` line; a creation by any other call — §8.3's, §4 step 4's, or one a command makes itself — is carried as `session_branch_created: <base short sha>` for the rest of the run, and §6's line reports it. A non-empty `unsettled` names the working copies step 2 left out of the commit, which §6's line names. A non-empty `sync.conflict` names files a merge of step 3 could not settle — `sync.conflicts` names each with that merge's source, `<default-ref>` or `origin/<session branch>` — and `sync.error` says the merge could not run at all: either way the commit stands, its push goes ahead, and §6's line says so. The commit is built with `git commit-tree`, signed where `commit.gpgSign` is set, and runs no `pre-commit` or `commit-msg` hook: those judge a change staged in a checkout, and this one is neither; a rule on `origin` still judges its push.

### 8.3 The overlay, around every move of the checkout

In the mode the working tree's session files hold the session branch's version wherever it differs from HEAD, so every command keeps reading and appending them where it always has. Git refuses to fast-forward or switch over such a working copy, even a byte-identical one, so every move of the specs checkout is wrapped:

- **Before it, `… lift --branch <session branch>`.** Where a session file is not yet on the session branch it prints `unpreserved: [...]` and changes nothing: run §8.2's `commit`, with §4 step 4's message, then `lift` again. A second `unpreserved` skips the move, which the step that wanted it reports as it would a refused switch or pull, with `lift found <path>[, …] not yet on session/<identity>` in place of git's first error line; nothing is discarded. Otherwise it returns each dirty session file to HEAD — one of the two discards this reference makes (§1 rule 4), and only of content it has just found on the session branch.
- **After it, `… put-back --branch <session branch> --default-ref <default-ref>`.** It merges as §8.2 step 3 does, then writes each session file where the branch differs from the new HEAD, or removes it where the branch lacks it. A path whose working copy is neither HEAD's nor the branch's is, where it is a block-shaped file or `follow-ups.md`, settled with the branch's version as §8.2 step 2 settles one the branch holds another version of, written back and listed in `merged`; where that settlement is refused, and for any other shape, the copy is left as it is and listed in `skipped`, as is a pending cost file this worktree held and a run deleted, whose deletion §8.2 commits. A copy that is still the version this worktree was last given, where another worktree has since moved the branch on, is brought up to date like HEAD's. Where its merge cannot run, it puts the branch back as it stands and says so in `sync.error`. It runs whether or not the move succeeded, so the overlay returns over the checkout as it stands.

The moves: §3.4's catch-up and §4 step 2's repeat of it; §3.5's B2 (switch, pull — its `branch -d` moves no checkout), B4 (switch, pull) and the re-run's switch back; `phase-handoff.md` §2.2's switch onto a new or reused deliverable branch, and its §3.3 row C repair; and a direct `/dev-workflows:implement` run from inside the specs repository, around its own branch and commit (its Phase 1.4, where its clean-tree check lifts and a fresh start switches, its Pre-Phase 3 and its Phase 4.6). **The preflight ends with `put-back` in the mode** whether or not it moved the checkout, and where a guard (§3.3) ended it, never under `specs_git: misrooted`, so a run interrupted between a `lift` and its `put-back` finds its overlay restored. Neither call prints anything where it succeeds, `skipped` included; an exit 2 is reported as this section's opening says.

### 8.4 Pushing, and the line

§4 step 5 pushes the session branch in place of the checked-out one — `git -C "$SPECS_PATH" push --porcelain -u origin <session branch>` — and §3.4's flush pushes it after its commit (§3.4). Step 5's conditions stand, with three differences for this branch alone:

- **The first condition holds:** the session branch is the plugin's to push (§1 rule 3).
- **A remote that deleted it does not stop the push.** A session pull request merged with *delete branch on merge* deletes it, and every later run's files would otherwise stay local for good; the push recreates it, and its next pull request shows only what has not landed.
- **`push-scope` counts the default branch as published.** Test it with `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" --specs "$SPECS_PATH" push-scope --branch <session branch> --session-default-ref <default-ref>`, whose `failed` carries `reason: branch-path` where the whole-change test below fails, with that path and the branch's newest merge commit (or `null` where it has none); the script measures as follows. The commits the push would publish are `git -C "$SPECS_PATH" rev-list --reverse refs/heads/<session branch> --not <base> <default-ref>`, or, with no base, step 5's `--not --remotes=origin` form, since the merges of §8.2 step 3 bring the default branch's own commits onto this branch and `origin` holds those already. Each must be a session-file commit as step 5 tests it, or a merge with exactly two parents (`rev-list --parents -n 1` prints three shas). Then the branch's whole change, `git -C "$SPECS_PATH" diff --name-only -z --no-renames <default-ref>...refs/heads/<session branch>` — what its pull request shows — must list ARTIFACT paths (§2.1) only; where it lists another, §6's *push-scope* line takes its session-branch form (§6), which names that path, and the branch's newest merge commit where it has one.

Step 6 reads the outcome as for any branch, and records a refusal of the session branch on it. A non-fast-forward rejection there means another clone pushed under the same identity first: a later run fetches that copy (§8.1), merges it in as §8.2 step 3 does and pushes, which §6 says in place of naming a pull — unless that merge is refused, where one clone changed what the other clone's copy still holds unchanged (an entry edited or removed, the header edited, the file deleted); §6's line then names the path, and the merge goes through once both copies agree on it (§8.2 step 3). The outcome line is §6's *session branch* row.
