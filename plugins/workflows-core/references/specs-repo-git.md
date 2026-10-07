# Specs-repo git — Shared Reference

Single source of truth for the two git entry points the plugin runs against the
**specs repo** (`$SPECS_PATH`). Every command that writes a bookkeeping artifact
there cites this file and executes its steps inline. The orchestrator owns any
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
3. **Bounded branches.** Only branches matching `^(idea|prd|ard|spec|design|ready|brd|frames|kb)/`
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
   §8's merges are of the default branch into the session branch, never the
   reverse, and move no checkout. §8.3's `lift` is the one discard: it returns
   to HEAD a session file whose exact content it has just found on the session
   branch.
5. **Never fatal.** Every failure is reported and the run continues. The run
   never fails because of a git step here.
6. **No `Co-Authored-By` trailer.** These are plugin-generated bookkeeping
   files, not authored content, and each artifact already carries its own
   `author:` field (`feedback-emission.md` §1).
7. **Prompt-free.** Neither entry point asks the user anything. `specs-preflight`
   is silent unless it acts, a guard fires, or §3.1 reports a misconfigured
   `$SPECS_PATH`; `commit-artifacts` emits one outcome line (§6).
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
   Nothing else is written here; what git itself writes for the commands this
   reference runs is unchanged by it — the upstream a `push -u` sets, and the
   whole `branch.<branch>` section that `branch -d` removes; §3.5's B2 removes
   the record of a branch it deletes. `workflows.sessionBranch` is the user's
   own key; this reference reads it and never writes it.

## 2. Bounded write authority

### 2.1 Paths

Exactly nine shapes, derived from the emission ladders and from the drafts the family writes for the operator — four directory shapes and the five single files §2.1 names below. Nothing outside this
set is ever staged.

```
<specs-root>/{specs|specifications|vis}/**/dev-workflows/**   # tier 1: feedback, cost, resume.md
<specs-root>/documentation/*/dev-workflows/**                 # the documentation run with no PRD (D19): feedback, cost
<specs-root>/dev-workflows-feedback/**                        # feedback-emission.md §2 tier 2 (keyless runs)
<specs-root>/dev-workflows-cost/**                            # cost-emission.md §9 pending files (keyless runs)
<specs-root>/{specs|specifications|vis}/**/implementation.md  # implementation-format.md §1, appended by /implement
<specs-root>/{specs|specifications|vis}/**/release-notes.md   # the /release-notes draft
<specs-root>/{specs|specifications|vis}/**/follow-ups.md      # followup-emission.md §2, appended per PRD/Epic folder
<specs-root>/{specs|specifications|vis}/**/pr-draft.md        # the /document (keyed mode) pull-request draft
<specs-root>/{specs|specifications|vis}/**/*-implementation-gaps.md  # the <KEY>-implementation-gaps.md draft (source-truth.md §7.5)
```

**The `documentation/` shape is the `docs-workflows` family's, and it exists because that family's normal run has no PRD and never will.** A documentation run against a repository nobody has written a PRD for would otherwise park every entry as *pending*, awaiting a reconciliation into a PRD directory that is never coming — so those entries accumulate forever and reconcile against nothing. The rung `feedback-emission.md` §2 and `cost-emission.md` §8 insert before pending writes instead to `<specs-root>/documentation/<docs-repo-slug>/dev-workflows/{cost,feedback}/`, where `<docs-repo-slug>` is the one-segment name the next paragraph defines. **Per docs repo, not one flat `documentation/` bucket**, for exactly the reason the PRD-directory rung exists for the pipeline: a person documenting two products must still be able to answer what documenting each one cost. The docs repo is that family's unit of attribution.

**`<docs-repo-slug>` is defined here, once, and it is always exactly one path segment.** It is derived in two steps, and two implementations that follow them produce the same directory for the same repository, byte for byte:

1. **The source string.** Read the resolved docs repository's `origin` remote (`git -C <docs-repo-root> remote get-url origin`) and derive `OWNER_REPO` from it exactly as `${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md` §2.6 derives it — the same `host` and `slug` expressions, and the same rule that only `github.com` drops the host — but **not** its SSH-alias resolution, which serves `gh` and `docs-workflows:finish-and-handoff` §4's footer, never a name: the slug is computed from the remote's own text, so a docs repository's folder keeps the name earlier runs gave it. Where the repository has no `origin` remote, **or where that derivation comes out empty** — a nonsense remote such as `https://github.com/` names no owner and no repository — the source is the basename of its git root instead. Where the run's write target is not a git work tree at all, the source is the basename of the target path, resolved to absolute. Three runs' command bodies lead to that last case: `/document` in direct mode pointed at a directory outside any git work tree; `/docs-init` when its operator cancels Phase 0 step 3's offer to create or initialise an absent or empty target — that command's emitter tail still runs, against a path that is not yet a repository; and `/docs-audit` where `resolve-docs-repo` answers with a directory that carries a docs signal and sits in no git work tree, which its own backlog path already provides for.
2. **The flattening — one substitution, per byte, in the C locale:** `printf '%s' "$source" | LC_ALL=C sed 's/[^A-Za-z0-9._-]/-/g'`. Every byte outside `A–Z`, `a–z`, `0–9`, `.`, `_` and `-` becomes one `-`. `/` is such a byte, so this one substitution is also what flattens `OWNER_REPO`'s separators; there is no second step to order it against. It is per **byte**, not per character: `ñ` is two bytes in UTF-8 and becomes `--`, so `Notes (draft) ñ` gives `Notes--draft----` wherever it is computed, where a per-character rule would give `Notes--draft---` and file one repository's record in two directories.

So `git@github.com:acme/docs.git` gives `acme-docs`, and `ssh://git@git.example.com/team/docs.git` gives `git.example.com-team-docs`. **Every such byte is flattened, not only `/`,** because a directory name is the operator's to choose and may carry a space or a non-ASCII letter, and a substitution that admits no exception is what lets two implementations reproduce this directory byte for byte. **It is no longer flattened to keep the path out of the classifier's quoting, and that half of the reason is retired rather than the rule**: `git status --porcelain` does wrap such a path in double quotes (with a non-ASCII byte octal-escaped), and step 2's classifier, reading the path as reported, would have seen `"documentation/…` and never staged it — but step 1 above now reads `-z`, whose records are never quoted, so that is a form this procedure no longer meets. The flattening stands unnarrowed, because **the one-segment property is the whole point, and it is why the flattening is not cosmetic**: step 2's classifier below admits exactly one segment between `documentation/` and `dev-workflows/` (`^documentation/[^/]+/dev-workflows/`), while an unflattened `OWNER_REPO` is two segments on GitHub and three anywhere else. An entry written under one would be classified OTHER — never staged, left dirty, and firing §3.3's G1 on every later preflight of every caller, which is exactly the failure each of the single-file shapes below was once found to cause. Every site that fills the placeholder — `feedback-emission.md` §2, `cost-emission.md` §8, and the `docs-workflows` commands whose runs emit there — cites this definition rather than restating the derivation; a second derivation is how two sites come to disagree about where one repository's record lives. The flattening can in principle map two remotes to one name (`a-b/c` and `a/b-c` both become `a-b-c`); that is accepted, since the alternative is a second derivation or a path the classifier cannot stage.

**The inner `dev-workflows/` in that path names the *family*, not the plugin — do not "correct" it per-plugin.** The shipped persistence ladder writes `<PRD-dir>/dev-workflows/cost/<sid8>.md` regardless of which plugin emitted the entry, and this shape is the same directory one level out. Renaming it to match the emitting plugin would fragment one repository's cost record across four directories and break every reader of it. **No new branch prefix goes with this shape**: §2.2's prefix authority governs branches the plugin creates *in* `$SPECS_PATH`, and the documentation family creates none there — its deliverable is the docs repository, where it branches, commits and drafts a pull request it never pushes.

**The five single-file shapes name files, never their folder, and the distinction is the
whole safety property.** All five sit in the feature folder rather than under `dev-workflows/`. The
first three are read by *key* rather than by session — `implementation.md` is read by `/document` and
`/release-notes` (their two-source read), by `/ready` (a unit's derived phase and its repositories), by
`/epics` and `/specify` (repository names) and by `epic-picker.md`'s ● marker — every command
`grep -l 'implementation\.md' plugins/*/commands/*.md` returns but `/implement`, which writes it — and
a record only one machine holds is a record the next run cannot use; `follow-ups.md` is `followup-emission.md` §2's "alongside the artifacts the
follow-ups are about", which §3 makes explicit is about where a *reader* looking at the folder finds
them. The last two are drafts for the operator, as `release-notes.md` is, written where the operator
looks for them: `/docs-workflows:document` (keyed mode) writes `pr-draft.md` for the pull request it
never opens itself, and it and `/docs-workflows:release-notes` write `<KEY>-implementation-gaps.md`,
the bug-report draft `source-truth.md` §7.5 fixes — its name carries the key, so it is matched as
`*-implementation-gaps.md`. But that same folder holds the phase deliverables (`prd.md`, `ard.md`, `specification.md`,
`design.md`, `idea.md`, `_readiness.md`), which are `${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md`'s
to commit behind its own consent choice. Widening a shape to the folder would sweep them into a
prompt-free bookkeeping commit and take the operator's choice away, so the five files are named
literally and nothing else in that directory is ever staged here.

**The first three were outside this set until a review found them**, while `/implement` and `/release-notes`
each told the operator the terminal step committed them. It did not: step 2 below classified each as
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
command starts writing a draft into the feature folder, re-derive this list against it rather than
trusting either end. `/epics` is the deliberate contrast and stays as it is: it
writes `epic.md` files this reference never stages, and says so in place.

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
branch, `cost-emission.md` §8 tier 1, tier 2's documentation branch and
§9 pending, `followup-emission.md` §2 (where it lands, per PRD/Epic folder),
`session-hygiene.md` §1 (resume tier 1), `source-truth.md` §7.5 (the
implementation-gaps draft) and `docs-workflows:finish-and-handoff` §5 (the
pull-request draft).

**Staging is by enumeration, not by glob.** Pathspec glob magic (`:(glob)`) is
fragile to express and to review. The procedure is:

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
   or `^dev-workflows-cost/` or
   `^(specs|specifications|vis)/.+/(implementation|release-notes|follow-ups|pr-draft|[^/]+-implementation-gaps)\.md$`,
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
3. Stage the literal ARTIFACT paths only:
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
its name matches `^(idea|prd|ard|spec|design|ready|brd|frames|kb)/`. The session
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

Runs at run start, once the run key set (§3.2) is known — Phase 0 in most commands. A command
that takes an address and reads its key set from resolution resolves it first, since the set is
what resolution returns (the resolved key, and on an Epic-level folder the key its parent's carrier
asserts), and runs this before any placement or refusal reads the resolved folder; a command that
takes none, or whose key set is its validated argument keys as typed — `/dev-workflows:vuln`'s
per-token keys among them, keyless where no token carries one — runs it as soon as `$SPECS_PATH`
is known, and resolves afterwards. Where resolution comes first,
a run that stops on its address — `invalid`, `ambiguous`, `misrooted` or `absent` — runs none. In
either order, a run that stops before the preflight on a check of its own inputs needing no specs-repo
state — a run flag, the directory it runs from, a path it reads where it sits rather than as an
artifact of the specs tree — runs none either. Prompt-free.
Silent when the repository is already clean and on the default branch, no other plugin branch holds a session-file commit §3.4 tries to push, and §3.1 finds
`$SPECS_PATH` well placed; it emits a block only when it acts or when a guard fires, and a
notice only where §3.1 reports a misconfigured `$SPECS_PATH`. That notice is one line, plus one more
line naming anything a misrooted run left behind. On a run carrying `specs_git: misrooted`, §3.5 adds
one line where it stays on a branch it would otherwise have left.

### 3.1 Gate

All of: `$SPECS_PATH` is set and is an existing directory;
`git -C "$SPECS_PATH" rev-parse --git-dir` succeeds; and the resolved `.git`
directory is **writable**. Test `.git` specifically, not just the worktree —
`commit` and `fetch` both write there, and a read-only specs mount is a normal
state in this container setup.

**A failed gate is not one disposition but three, and conflating them is what made a misconfiguration indistinguishable from a supported state.**

- **`$SPECS_PATH` is unset → silent no-op here.** Whether that is a supported state is the caller's to say, and it says so *before* this step: a command that resolves or creates its deliverable's folder in the specs tree by key stops in Phase 0 on the unset variable (`workflows-core:escalation-rules` *Required path environment variable unset*, or the same two-option list inline), so it never reaches this gate unset — `grep -lE 'Set SPECS_PATH|Required path environment variable unset' plugins/*/commands/*.md` names them, and `/implement`, `/document` in keyed mode and `/release-notes` are among them for a `<KEY>` address only; a command that writes into a folder it resolves from an address but carries no such stop on the address form it was given — `/epics` on either address form, and `/implement`, `/document` in keyed mode and `/release-notes` on an `@<path>` address (`implementation.md`; `pr-draft.md` and the implementation-gaps draft; the `release-notes.md` draft) — stops not-found on a `<KEY>` address, there being no tree to search, and on an `@<path>` address runs on, writing into the folder given (`/implement`, `/document` and `/release-notes` never reach the not-found stop unset, having stopped on the variable first); a command for which the specs repository holds only its bookkeeping — `/document` in direct mode, `/implement` on a direct prompt, `/upgrade`, `/vuln`, `/docs-init`, `/docs-brand`, `/docs-audit`, the four logging commands and `/diagnose-session` — runs on, and its emitters fall to the report-only tier. Those three classes are every caller of this entry point.
- **`.git` resolves but is not writable → silent no-op**, exactly as before. The artifacts are going to a report-only tier the plugin does not manage, and a read-only specs mount is a normal state in this container setup. Saying nothing is correct here: there is nothing for the operator to fix.
- **`$SPECS_PATH` is set to a path that is not a directory, or `rev-parse --git-dir` fails there → emit a notice**, one line naming the variable and the path, then continue. This is **never** a supported state: a set-but-not-a-repository `$SPECS_PATH` is a typo, a missing mount, or a path that was right in another container. Under the old blanket silence it looked identical to the read-only case, so a run would write its deliverables, commit nothing, open no pull request, and end on a terminal gate-failed line that named none of it — the operator's first clue being an empty specs tree some time later. **Where the path is a directory and `workflows-core:addressing` §3 `specs-root-check` finds a signal there, the same line also says which one, and names the value to set and the clause that entry point's stop adds. Where that stop has a second line, naming what a misrooted run left behind, the notice adds that line too.** A `specifications/` directory mounted on its own fails `rev-parse` in exactly this way, because the repository's git directory sits above the mount point. A command that resolves no address never reaches that entry point's stop; where this notice fires, it is how such a command learns the cause.

**A passing gate is tested once more, for a `$SPECS_PATH` set inside the specs tree.** On an ordinary checkout, `$SPECS_PATH=<repo>/specifications` meets all three conditions, because git finds the repository above it. A run that resolves no address would then file its bookkeeping inside `specifications/` with nothing said. Examples are `/upgrade`, `/vuln` on tokens carrying none, `/implement` on a direct prompt, `/document` in direct mode, `/docs-init`, `/docs-brand`, `/docs-audit` and the four logging commands. So **where the gate passes, run the tests of `workflows-core:addressing` §3 `specs-root-check`**, exactly as that entry point defines them, its exclusions included. Where a signal holds, emit a notice naming the variable, its value, which signal holds and the value to set, **set `specs_git: misrooted` for the whole run**, then continue. The notice is the stop's own text. It is one line, with the unsupported-layout clause where that applies, plus one more line naming anything a misrooted run left behind and where it belongs. Like the stop, it moves nothing and gives no commands. A run that resolves no address learns all of it here, and only `commit-artifacts` repeats it, verbatim, at the end of the run (§4 step 1, §6). On an ordinary checkout, `$SPECS_PATH=<repo>/specifications` prints the prefix `specifications/`, which that entry point's first test catches whether or not an earlier run left a nested `specifications/` behind. **It stays quiet at a correct root.** A correct root's own carrier-bearing files, such as a `templates/` folder, a `README.md` or a `docs/` page, fail (b)'s prefix test, whether or not `specifications/` exists yet. A `$SPECS_PATH` like `<repo>/specs` holding `specs/specifications/` prints `specs/`, matches no signal, and draws the notice below instead. A specs repository nothing has been written into yet matches nothing. `specs-root-check` records two unsupported layouts, each with its own reason. The specs root that is itself a subdirectory named `specifications` draws this notice on every run. The specs tree inside a larger repository draws the notice below.

**A `$SPECS_PATH` below its repository's top level.** `$SPECS_PATH` names the root of a dedicated specs repository, the directory that holds `specifications/`. **A specs tree inside a larger repository is unsupported**, because this plugin switches branches and commits in the repository `$SPECS_PATH` belongs to. On a correct root, §3.5 settles and switches its branch at run start, `commit-artifacts` (§4) commits on it, and `workflows-core:phase-handoff` §2 cuts a branch there and commits a deliverable. In a repository that also holds code, each of those would move the checkout of everything else that repository holds, so none of them switches or commits under the flag this notice sets. So where the gate passes and `git -C "$SPECS_PATH" rev-parse --show-prefix` prints a non-empty prefix, emit one notice line, **set `specs_git: misrooted` for the whole run**, then continue (§1). The line names the variable, its value and the repository's top level (`git -C "$SPECS_PATH" rev-parse --show-toplevel`), and says that a specs tree inside a larger repository is unsupported because the plugin switches branches and commits there. This is a misconfigured `$SPECS_PATH` in §1 rule 7's sense. **Skip it where the inside-tree notice above already fired this run.** That notice names the same path and what to set instead, and, where the value it names is below its repository's top level, that the layout is unsupported. **What a run that stops on `specs-root-check` prints depends on its order (§3).** A command that resolves its address first stops there and runs no preflight, so it prints neither notice, only the stop. A command that runs `specs-preflight` first, on its argument keys as typed (`/idea`, and `/vuln` on a token carrying a key, among them), prints the inside-tree notice here and then stops at its resolution, so the operator sees the notice and then the stop, which name the same cause.

Still **never fatal** (§1): each notice reports and the run continues. **Where the path is a directory and `specs-root-check` finds a signal there, the non-repository notice above sets `specs_git: misrooted` too.**

**`specs_git: misrooted` is the run-wide record that `$SPECS_PATH` is misplaced.** It is set by either notice above, or by `workflows-core:addressing` §3 `specs-root-check` where it stops the run at resolution. Under it, every emitter of the tail falls to its report-only tier, so the tail writes nothing under a path the run has found wrong. That covers cost (`cost-emission.md` §8), feedback (`feedback-emission.md` §2), follow-ups (`followup-emission.md` §2) and `resume.md` (`session-hygiene.md` §1). Writing there would only add files §2.1's classifier puts in OTHER, or artifact paths that cannot be staged from `$SPECS_PATH` and that the first run after the variable is fixed would commit in the wrong place: a pending cost there never reconciles, and G1 fires on every run after the variable is corrected.

**The preflight itself performs no write under the flag**: no leftover flush, no push retry, no branch switch, creation or deletion, no pull, no commit and no push. Where the gate passed, it still reads, because `workflows-core:phase-handoff`'s `require-on-main` runs on what it reads. §3.2 runs in full, its best-effort fetch included, which refreshes the remote-tracking refs every `<default-ref>` test reads and moves no checkout. §3.5 classifies the branch, and a row that would switch stays and reports instead. §3.3's guards and §3.4's flush do not run, and each section says why. §4's `commit-artifacts` skips, as it does on `specs_git: blocked`. `workflows-core:phase-handoff` §2.1's `handoff-to-main` refuses the handoff, its §4.3 says so above the consent array, and its row C offers no repair. **So none of `specs-preflight`, `commit-artifacts`, `handoff-to-main` and `require-on-main` switches a branch or commits under the flag.** That bound is those four entry points', not the run's. A command that changes code still cuts its own branch and commits on it in the code repository it changed (`dev-workflows:code-handoff`), and a documentation command does the same in its docs repository. Where the specs tree sits inside that same repository, that branch moves the specs checkout too, which is one reason that layout is unsupported.

**What the flag leaves alone is what the command itself writes.** A run a notice let continue still writes its deliverable where the command puts it, and any of §2.1's single files it writes beside it: `implementation.md`, the `release-notes.md` draft, `pr-draft.md` or the implementation-gaps draft. They stay there, written and uncommitted, for the operator to move or commit once `$SPECS_PATH` is right. A run stopped at resolution writes nothing under the path at all. What changes is that the condition is now *said*.

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
| G1 | Any dirty **OTHER** path (§2.1) | **Hand off** — no commit, no branch switch, no push. §5 notice at **advisory** severity, listing the paths. Those files are not the plugin's, and switching branches would carry them. **This does NOT set `specs_git: blocked`**: the terminal `commit-artifacts` still runs, because it stages only artifact paths and is safe beside unrelated dirt. Losing the artifacts to protect files the step never touches would be the worse failure. |
| G2 | On a **named** branch that is neither the default branch nor a match for `^(idea\|prd\|ard\|spec\|design\|ready\|brd\|frames\|kb)/` | **Leave it; stay on it.** §5 notice at **advisory** severity, naming the branch, so the user knows where this run's artifacts will land — on that branch, or, on a direct `/dev-workflows:implement` run from inside the specs repository, on the code branch the run cuts (§5). The commit is safe — a named branch cannot be lost — so `commit-artifacts` proceeds, and leaves its commit unpushed (§4 step 5). The plugin manages only branches it created (§2.2). In session-branch mode the commit lands on the session branch instead, and is pushed (§8). |

### 3.4 Stage 2 — flush leftovers

Always runs when stage 1 matched nothing **and the run does not carry `specs_git: misrooted`** (§3.1). Under that flag it does not run at all, so there is no flush and no push retry, and the preflight goes on to §3.5, which switches nothing under the flag. A flush there would `git add` paths that porcelain prints relative to the repository's top level and that do not exist from `$SPECS_PATH`, which fails with exit 128 on every run. Where `$SPECS_PATH` is a correct root holding a stray folder, it would commit and push while the notice says the run wrote nothing.

**On the default branch, catch up first.** Where HEAD is on the default branch (§3.2), `<default-ref>` is `origin/<default>`, and HEAD is strictly behind it — `git -C "$SPECS_PATH" merge-base --is-ancestor HEAD <default-ref>` succeeds and `git -C "$SPECS_PATH" rev-parse HEAD` differs from `git -C "$SPECS_PATH" rev-parse <default-ref>` — run `git -C "$SPECS_PATH" pull --ff-only --no-rebase origin <default>` before either case below. In session-branch mode (§8) the catch-up is wrapped in `lift` and `put-back` (§8.3). `--no-rebase` is required: a `pull.rebase` setting would otherwise make the pull a rebase, which §1 rule 4 forbids and which refuses to run beside a modified artifact. The catch-up is silent where it succeeds; where it fails, report git's first error line and continue on the branch as it stands. §4 step 2 runs it again before staging, for a run whose preflight ended at a guard or never ran. Nothing else here brings the default branch up to date while a run stands on it — §3.5's B1 does nothing, and only B2 and B4, which switch to it, pull — so without it a run's commit would land on a stale base, and its push and every later retry would be rejected as non-fast-forward. A default branch holding commits the remote lacks is ahead or diverged, never behind, and no fast-forward applies to it; a diverged one is §4 step 6's case.

- **Dirty ARTIFACT paths exist** → commit them **onto the current branch** (they
  belong to the run that wrote them) and push where §4 step 5 allows it, per §4
  steps 2–6, which print no §6 line here: where step 4 finds nothing to commit,
  or step 5 pushes nothing, the flush ends silently.
- **No dirty ARTIFACT path** → where the current branch holds commits a push
  would publish and all three of §4 step 5's conditions hold, **retry the
  push**; where one fails, nothing is retried and nothing is printed. Stage 1
  has already ended the preflight on every branch step 5's first condition
  refuses (§3.3 G2), so the other two decide here, and a specs repository with
  nowhere to push never retries.

  **`push-scope` never reads `@{u}` directly.** A failed `push -u` sets no
  upstream, so `git rev-parse --abbrev-ref '@{u}'` and
  `git rev-list --count '@{u}..HEAD'` both exit 128 with `fatal: no upstream
  configured` — the condition is not false but *unevaluable*, and precisely in
  the state the retry exists for: the local-only branch a failed `push -u` leaves
  behind, which strands an artifact commit with nothing to retry it.
  Step 5's base reads no upstream at all: it tests
  `refs/remotes/origin/<branch>`, which a failed `push -u` leaves absent, and
  falls through to the remote's refs. Without a test that answers there, a push that
  failed in a previous run leaves a local commit that nothing ever retries — the
  original defect, re-created one layer up.
- **In session-branch mode** (§8) the two cases are one, since the overlay
  keeps session files dirty: commit through §8.2, which finds nothing new
  where the dirty files are the overlay alone, then push the session branch
  where it holds commits a push would publish and step 5's conditions hold
  as §8.4 states them. Nothing is printed but step 6's failure lines.

**Then, either way, retry every other local plugin branch.** List them with
`git -C "$SPECS_PATH" for-each-ref --format='%(refname:lstrip=2)' refs/heads/`
and keep those §2.2's pattern matches, less the current branch. Test each in
this order, stopping at the first that fails: it holds commits a push would
publish (§4 step 5's `push-scope` measure, which on most branches finds none
and ends the test there); `branch-merged` (§3.5) does not find it merged; and
all three of step 5's conditions hold for it. Where all hold, push it as step 5
does — a push names its branch, so it needs no switch — and print
`Specs preflight: pushed <N> session-file commit(s) left on <branch>`. Where a
test fails, nothing is pushed and nothing is printed. A push step 6 reports as
failed prints step 6's line for it, which names the switch to `<branch>` its
remedy needs, since the run is standing on another branch. Without this, a
commit stranded on a branch the run is not standing on is never retried: B4
below switches away from a plugin branch keyed to no key of the run right after
the flush above committed on it, so a flush whose push failed leaves its commit
there, and every later run starts somewhere else.

Either way, continue to stage 3 with a clean tree — in session-branch mode,
with the overlay in place, which §8.3 lifts around each move.

### 3.5 Stage 3 — branch disposition

First matching row applies.

| # | State | Action |
|---|---|---|
| B1 | On the default branch | Nothing further. |
| B2 | Plugin branch, and `branch-merged HEAD` (below) finds it merged | Switch to default, `git -C "$SPECS_PATH" pull --ff-only`, `git -C "$SPECS_PATH" branch -d <branch>`, then remove `<branch>`'s push-refusal record where one stands (§1 rule 8). If `-d` fails, report git's own message and skip — **never `-D`**. Where `branch-merged` answered by its second or third test, a rebase or a squash, git may not see the merge — `-d` deletes a branch merged into its upstream, or into `HEAD` where it has none, and refuses one merged only by a rebase or a squash — so the report then adds the command for the user to run once they are sure: `Specs preflight: <branch> is merged into <default> by a rebase or a squash, which git branch -d cannot see — delete it with git -C "<SPECS_PATH>" branch -D <branch>`, and where `<branch>`'s push-refusal record stands (§1 rule 8), `rm -f "<record>"` after it, since `branch -D` no longer takes the record with it. If `pull --ff-only` fails (the local default branch has diverged), report and continue on default **without** pulling — never merge, rebase, or reset. |
| B3 | Plugin branch, unmerged, `branch-key` (below) resolves the branch to **any** key in the run key set (§3.2) | **Stay on it.** See §3.6. |
| B4 | Plugin branch, unmerged, `branch-key` resolves the branch to **no** key in the set, or the set is empty (keyless run) | Switch to default, `git -C "$SPECS_PATH" pull --ff-only`. **Leave the branch and its pull request alone.** Report the branch name, and, where it still holds commits a push would publish (§4 step 5's `push-scope` measure), how many: a later run's preflight retries them wherever §4 step 5 lets it push them (§3.4). |

**In session-branch mode** (§8), B2's and B4's switch and pull, and the re-run's switch back below, are each wrapped in `lift` and `put-back` (§8.3), and the preflight ends with `put-back`. HEAD on the session branch is not a row's subject: G2 has already kept the run there.

**Merged — `branch-merged <ref>`.** Whether the work on a branch is on the default branch, asked against `<default-ref>` (§3.2). B2 asks it of `HEAD`, `phase-handoff.md` §2.2 rule 3 of the ref it resolves, and §3.4's retry of each branch it lists. The first test that holds answers **merged**; none holding answers **unmerged**:

1. **A merge or a fast-forward:** `git -C "$SPECS_PATH" merge-base --is-ancestor <ref> <default-ref> 2>/dev/null` exits 0.
2. **A rebase merge:** `git -C "$SPECS_PATH" cherry <default-ref> <ref>` prints at least one line, every line it prints begins `-`, which marks a commit whose change the default branch already holds under another commit, and `git -C "$SPECS_PATH" rev-list --merges <default-ref>..<ref>` prints nothing. `cherry` passes over merge commits, so a branch whose only change of its own sat in a merge commit would otherwise read merged, and B2 would name `branch -D` on it.
3. **A squash merge:** with `<base>` from `git -C "$SPECS_PATH" merge-base <ref> <default-ref>`, the patch id of the branch's whole change, the first field of `git -C "$SPECS_PATH" diff --no-renames <base> <ref> | git -C "$SPECS_PATH" patch-id --stable`, is the first field of a line of `git -C "$SPECS_PATH" log -p --no-renames --no-merges <base>..<default-ref> | git -C "$SPECS_PATH" patch-id --stable`, the default branch's own commits since. An empty change has no patch id and is never found merged this way.

Ancestry alone was the test, and a pull request merged by squash or by rebase never passes it: the branch read unmerged forever, so B3 kept a resumed run on a branch whose pull request had closed, and the handoff reused it and called `gh pr create` on it. All three tests read the branch at its tip, so a commit made on it after its pull request merged makes it read unmerged again; §4 step 5's deleted-branch state then reports that commit's push rather than letting it recreate the branch.

**Under `specs_git: misrooted` (§3.1) the table classifies and moves nothing.** Take the first matching row exactly as above: §3.2's fetch has already refreshed `<default-ref>` for B2's merge test, and `branch-key` below resolves B3 and B4 unchanged. Then act on that row without writing. B1 and B3 stay where they are, as they always do. B2 and B4 stay too, with no `switch`, no `pull --ff-only` and no `branch -d`. Each prints one line in place of its action: `Specs preflight: staying on <branch> — specs_git: misrooted, so no branch is switched (it would have <switched to <default> and deleted it, as it is merged | switched to <default>, as no key of this run names it>)`. A B3 here keeps the checkout on the caller's own branch exactly as it does on a correct `$SPECS_PATH`, so `workflows-core:phase-handoff` §3.3 row B still passes a resumed run. Where HEAD is on no plugin branch, no row applies here, as always.

**Branch key resolution — `branch-key <branch>`.** The branch's key is resolved
*against the run key set*, by testing the keys the run already holds. It is never
extracted from the branch name as free text.

1. Strip the `idea/`, `prd/`, `ard/`, `spec/`, `design/`, `ready/`, `brd/`, `frames/` or `kb/`
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
to a key in the new set, switch back to that branch first (`git -C "$SPECS_PATH" switch <branch>`,
the name B4 reported; it exists and the plugin created it), then run stages 1–3 again, whose B3
then stays on it. That is the state a single run holding the new set from the start would have kept,
and a second preflight standing on the default branch cannot reach it by B1–B4 alone. A switch that
fails is reported with the branch name, and the run continues from the branch it stands on. No
other re-run switches anything outside the table above. Under `specs_git: misrooted` there is nothing
to switch back to: no earlier B4 switched away, so the re-run classifies again and stays.

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

**First, same-phase resume.** `phase-handoff.md`'s `require-on-main` (§3) has a state — row B — that *passes* when the artifact is on the default branch but the worktree copy differs because the current branch is one this run itself owns: `/design` amends `specification.md` on its own `design/<EPIC>-<eslug>` branch, so a re-run of `/design` legitimately finds that copy has diverged from what merged earlier. B3 is what keeps the repo on that branch in the first place, and that is what makes row B reachable at all. If the preflight instead fell through to B4 and switched to the default branch, `/design`'s in-progress amendments would be left behind on a branch nobody is standing on, and row B — built to pass on exactly this divergence — would never see the case it exists for.

**Second, `/ready`'s explicit checkout.** The user may choose to proceed on the current checkout rather than switch to the default branch. Switching off it mid-run while the readiness report still claims that checkout is the one that was read would make the report false.

**The same shape reaches Epic-scoped runs — which is why §3.2 resolves a key *set*, not a single key.** `/specify <EPIC>` authors `specification.md` on `spec/<EPIC>-<eslug>`, a branch keyed by the **Epic**. The follow-up `/design <EPIC>` run resolves the PRD as its primary key, so a single-key comparison would read branch key ≠ run key, fall through to B4, and switch away from the branch holding the very `specification.md` `/design`'s resume depends on — the same reachability loss described above, one key earlier in the chain. Matching the branch key against **any** key in the set keeps B3 in force for Epic-scoped runs, on every command that takes an Epic address, exactly as it holds for PRD-scoped ones.

The failure this section used to defend against — `/create-ard` continuing silently against the wrong source when the authored PRD file existed only on an unmerged branch — is now caught loudly instead: `phase-handoff.md` §3.3 rows D and E stop that run rather than letting it proceed, so the defense moved there.

B3 keeps the working tree containing the artifact the run is about to read or amend. The cost is that the follow-up command's own branch is cut from the earlier branch rather than from the default — a stacked branch. That is correct: an ARD genuinely depends on its PRD and a design on its spec, and stacking is the honest representation.

### 3.7 Detached HEAD is blocking, not merely skipped

G0 is the one guard that refuses to commit, and it is a data-loss guard
rather than a courtesy. (`specs_git: misrooted`, §3.1, also stops `commit-artifacts`
and `phase-handoff`'s deliverable commit, but it is set by the gate's notices, not by a guard.)

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
G1 does not — see the note in its row.

## 4. `commit-artifacts` — terminal step

Runs as the **last action of the run**, after `resume.md` is written (where the
command writes one) and before or as the run's last printed output (§6).

**The one exception — a phase that cedes control.** Where a later phase hands the
session to another skill, or opens an open-ended interactive stretch, this step
runs immediately **before** that hand-off instead, and prints its §6 outcome line
there. `/prompt-brainstorm` (whose Phase 3 hands off to
`superpowers:brainstorming`) and `/prompt-grill-me` (whose Phase 3 is a long
interactive grill) are the cases. "Last" is protective only while the run still
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

- **Feedback writes nothing.** `feedback-emission.md`'s `emit-auto` is called
  by a command's maintenance phase, which a refused run never reaches, and
  `emit-block` fires at the halt rather than here and excludes an environment
  or operator halt by its own predicate — which every Phase 0 refusal is.

- **Follow-ups are a no-op.** No signal qualifies, so that phase resolves no
  target, writes nothing and ends silently (`followup-emission.md` §6).

- **The cost entry is written, unless `--skip-costs`, in which case `workflows-core:run-flags` `skip-cost` advances the checkpoint and writes nothing, or unless the run carries `specs_git: misrooted` (§3.1), in which case `cost-emission.md` §8 reports it in the run's output and writes nothing.** `cost-emission.md` §11 settles it already —
  *Cost runs unless the user skipped it* — and it is the member that makes this tail matter on a
  refusal: the run spent the session's tokens whether or not it wrote a file,
  and a keyless one has a home under that file's §9 pending ladder. A refusal
  that skipped the tail would break §11 silently, which is why the tail is not
  skipped wholesale.

- **`resume.md` is NOT written.** `session-hygiene.md` §1 defines it as the
  last *completed* position — the phase just finished and the exact next
  command from the run's own `### Next step` — and a Phase 0 refusal completed
  no phase and printed no such block. It is overwritten rather than appended,
  so writing one here would replace a live pointer to a real position with a
  run that did nothing, and what it replaced cannot be recovered.

- **This step runs**, for the cost entry above (under `--skip-costs` there is none, and the gates below settle the step exactly as they would for any run with nothing new to stage). Where the refusal was `specs-root-check`'s stop, the run carries `specs_git: misrooted`, and step 1's gate skips the step with the stop repeated. Where the refusal came before
  `$SPECS_PATH` was resolved, step 1's gate no-ops it silently; on a detached HEAD with something to stage, step 1 refuses it with G0's notice; where that
  entry is the only new path, step 4 commits it alone; where nothing is dirty,
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
to state.

1. **Gate.** All of §3.1's environment conditions, **plus** the run must not
   carry `specs_git: blocked` from §3.3 G0 or `specs_git: misrooted` from §3.1.
   **Test the two flags first, and a flag's outcome below takes precedence
   over an environment failure**, so each state has one outcome.
   `specs_git: misrooted` is often set where an environment condition fails
   too: §3.1's non-repository notice sets it where `specs-root-check` finds a
   signal, as on a `specifications/` directory bind-mounted on its own, and
   that entry point's stop sets it on a path no `rev-parse` reaches. Such a
   run takes the misrooted outcome, never the silent one. `specs_git: blocked`
   is set only behind a passing gate (§3.3 G0), so it never meets one. **A run
   that ran no preflight and carries neither flag tests G0's state here**, since
   nothing else did: a refusal taken before the preflight still reaches this
   step (the tail above). Where §3.1's environment conditions hold,
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
   - Carries `specs_git: misrooted` → **not silent**: re-emit the §3.1 notice,
     or `specs-root-check`'s stop, that set it, whether or not §3.1's
     environment conditions hold. Nothing is committed, and the tail's
     emitters wrote nothing under `$SPECS_PATH` (§3.1). What the command
     itself wrote there — a noticed run's deliverable, or one of §2.1's single
     files such as `implementation.md` — stays written and uncommitted, and
     what was already there sits where this run found it wrong.
   - Carries neither, and fails on path / repo / permission grounds →
     **silent no-op**, matching the emission ladders' silent-skip discipline.
     Nothing committed, nothing reported, run unaffected.
2. **Enumerate and stage** per §2.1. OTHER paths are never staged. On the
   default branch, run §3.4's catch-up first. A run whose preflight ended at a
   guard (§3.3) or never ran has not had it; where the preflight already caught
   up, it finds nothing to do. Its test reads the ref last fetched, so a merge
   that lands on the remote during the run goes unseen; that run's push is
   rejected, and step 6 says what to run. In session-branch mode (§8), §8.2's
   `commit` enumerates instead, and the catch-up is wrapped as §8.3 says.
3. **Nothing staged** (the gate passed but no artifact path is dirty) → no
   commit; emit the §6 `nothing to commit` outcome line. This is distinct from
   step 1's silence — here the specs repo *is* managed and simply had nothing
   new.
4. **Commit — by pathspec, never the index.** Message:
   `<KEY> Add dev-workflows session artifacts (<command>)`, or
   `NOISSUE Add dev-workflows session artifacts (<command>)` when the run
   resolved no key. This matches the specs repo's own `<KEY|NOISSUE> <summary>`
   convention. **No `Co-Authored-By` trailer** (§1 rule 6).

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
     `git -C "$SPECS_PATH" remote get-url origin` exits 0. Three more states
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
     - **The remote deleted the branch:** the branch's upstream is `origin`'s
       branch of the same name —
       `git -C "$SPECS_PATH" for-each-ref --format='%(upstream)' refs/heads/<branch>`
       prints `refs/remotes/origin/<branch>` — and
       `git -C "$SPECS_PATH" ls-remote --exit-code --heads origin refs/heads/<branch>`
       exits 2, which says the remote holds no such branch. A remote that
       renamed its default branch, and a pull request merged with *delete
       branch on merge*, both leave this state, and a push would recreate the
       branch the remote removed. Any other exit, an unreachable remote
       included, does not count here; the push then reports its own failure
       (step 6).
     - **The remote refused this branch before:** its push-refusal record
       stands (§1 rule 8) — `test -f "<record>"`, or else
       `git -C "$SPECS_PATH" config --get branch.<branch>.workflowsPushRefused`
       prints a date. The date the rows name is the file's content, or the
       key's; where the file is empty, `<date>` is `an earlier run`.
   - **`push-scope`: every commit the push would publish is a session-file
     commit.** First the base the push is measured against:
     `refs/remotes/origin/<branch>`, the ref this push updates, where
     `git -C "$SPECS_PATH" show-ref --verify -q refs/remotes/origin/<branch>`
     finds it; else none, as on the local-only branch a failed `push -u` leaves
     behind, or one whose remote ref was pruned. The commits the push would
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
     (`git -C "$SPECS_PATH" rev-list --parents -n 1 <sha>` prints at most two
     shas: the commit and its one parent) whose every path,
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
   they are.
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
     unrecorded: §6's row says so, and the next run pushes the branch again. Retrying would be refused the same way on
     every run while the commits pile up on the local branch. Name what to do
     wherever this step runs: at the end of a run, §6's *push refused* line;
     inside §3.4's flush or retry, which print no §6 line, as
     `Specs preflight: <branch> not pushed — origin refused it (<the reason in parentheses>), and this is recorded so no later run pushes it; <the remedy §6's push-refused line gives>` — or, where step 6 could record it neither way, `…, and this could not be recorded (<error>), so the next run pushes it again`.
     A rule that refuses what a commit carries, rather than the branch it goes
     to, refuses the branch that remedy names too; removing the record is then
     how the user lets a later run try again.
   - An auth failure, a remote that cannot be reached, a transient refusal
     above, or any other failure → report; the commit stays local. §3.4 retries the push on the next run.
   - **Non-fast-forward rejection** (`[rejected]`) → report; **never force-push**, never
     auto-rebase mid-run. The commit stays local, and no later run's retry
     succeeds until the user takes in the remote's commits: the branch has
     diverged, a fast-forward cannot reach it, and this reference never
     rebases. Name the commands that do it wherever this step runs: at the
     end of a run, in §6's *push rejected* line; inside §3.4's flush or retry,
     which print no §6 line, as
     `Specs preflight: <branch> not pushed — origin's <branch> has commits it lacks; run git -C "<SPECS_PATH>" switch <branch>, git -C "<SPECS_PATH>" pull --rebase --autostash origin <branch> and git -C "<SPECS_PATH>" push origin <branch>, then switch back to <the branch the run stands on>`.
     The switch is not optional: §3.4's retry pushes branches the run is not
     standing on, and a `pull` run from another branch merges `<branch>`'s
     remote commits into that one instead.
   - **`index.lock` present** (a concurrent session holds the repo) → report and
     skip; **never delete a lock file**. The artifacts stay in the working tree
     and the next run's preflight flushes them.
   - **The commit fails** — a `pre-commit` or `commit-msg` hook rejects it, a
     signature cannot be made, or a merge is in progress, during which git
     refuses a pathspec commit → report git's error or the hook's output; never
     retry and never `--no-verify`. The artifacts stay staged, and a later
     run's preflight flushes them (§3.4) once git accepts the commit.
7. **Emit the §6 outcome line**, plus the full §5 notice repeated verbatim when
   a guard fired at §3.3.

### 4.1 Where the commit lands

- **In session-branch mode** (§8) — on the session branch, whatever the
  checkout stands on, and a deliverable branch carries no session file. The
  bullets below hold outside the mode.
- **A command that opened a specs-repo branch at handoff** (`/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/design`, `/implement`, `/ready`, `/frames`, `/prd-ground`, `/prd-proposal`, `/harvest-decisions`, `/promote-decisions`, and every `/brd-*` command — nineteen total, matching `phase-handoff.md`'s producer count) — on that `idea|prd|ard|spec|design|ready|brd|frames|kb/*` branch, so the push updates the pull request already open. Two commits on one branch: the deliverable, then the artifacts — save where the deliverable's commit failed (`phase-handoff.md` §4.1's *Commit failed*), when the artifacts' commit alone lands on that branch and its push opens no pull request. Every `/brd-*` command opens on the shared `brd` prefix (`phase-handoff.md` §2.9); `/prd-ground` opens on that same shared `brd` prefix on the BRD route, or on the shared `prd` prefix (with `/create-prd`, `/update-prd` and `/prd-proposal`) on the idea route — it left the `/brd-*` glob the day its own rename shipped, but not the prefix sharing, which is why it is named here rather than folded into "every `/brd-*` command". A later `/brd-*` run — or `/prd-ground`, on the BRD route — that reuses the branch a prior phase of the same BRD opened lands there rather than on the default branch.
- **The same command when the user declined git at handoff** ("just write the
  files — I'll handle git") — the repo is still on the default branch and the
  deliverable is uncommitted there. `commit-artifacts` still runs and commits
  **only** the bookkeeping paths; the uncommitted deliverable is untouched,
  because it is an OTHER path. This is deliberate: "I'll handle git" refers to
  the deliverable, and the bookkeeping still has to reach the maintainer. The
  outcome line states plainly that the deliverable remains uncommitted.
- **Every other command** — on the default branch, unless §3.3 G2 left the run
  on a branch the plugin does not manage, or §3.5 B3 kept it on a plugin branch
  keyed to this run. The commit follows the branch the preflight settled on; it
  never switches.
- **`/dev-workflows:implement` on a direct run from inside the specs repository** (its Phase 0),
  where the specs repository is the repository the run changes — on the code
  branch the run cut there, which step 5 does not push unless its name carries
  one of §2.2's prefixes.

## 5. Notice contract — the guards must be impossible to overlook

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
4. **What happens if it is ignored** — one clause.

Severities: **blocking** (G0 — the terminal commit will not run) and **advisory**
(G1, G2 — the commit still runs, but somewhere the user should know about). Both
use the same four-part shape; only the wording of part 2 differs.

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
          # or, to rejoin an existing branch:
          git -C "<SPECS_PATH>" switch <branch>
If ignored: the artifacts stay in your working tree, uncommitted and intact; the
          next run's preflight picks them up once HEAD is on a branch.
```

**G1 — advisory:**

```
⚠ SPECS REPO — UNCOMMITTED FILES THAT ARE NOT THE PLUGIN'S

Found:    <SPECS_PATH> has <N> uncommitted change(s) outside the plugin's
          artifact area: <path list>
Not done: the preflight did not commit, switch branches, or push. Those files
          are yours, and switching branches would carry them along. This run's
          own artifacts WILL still be committed at the end of the run —
          commit-artifacts stages only the §2.1 artifact paths.
Fix:      git -C "<SPECS_PATH>" status
          git -C "<SPECS_PATH>" add <path list> && git -C "<SPECS_PATH>" commit
If ignored: nothing is lost — your files stay uncommitted, and this run's
          artifacts are committed alongside them. But the preflight ends here
          on EVERY later run too, so the leftover flush and the branch
          settle (stages 2-3) stay skipped until these paths are committed
          or removed. An Epic draft left in place by /epics is the usual
          cause, and it is a supported state — this is what it costs.
```

**G2 — advisory:**

```
⚠ SPECS REPO — ON A BRANCH THIS PLUGIN DID NOT CREATE

Found:    <SPECS_PATH> is on branch `<branch>`, which is neither the default
          branch (`<default>`) nor a plugin branch (idea/ prd/ ard/ spec/
          design/ ready/ brd/ frames/ kb/).
Not done: the preflight did not switch away from it — the plugin manages only
          branches it created. This run's artifacts WILL be committed on
          `<branch>`, and not pushed.
Fix:      # only if that is the wrong place for them:
          git -C "<SPECS_PATH>" switch <default>
If ignored: the artifacts land on `<branch>` and reach the maintainer when you
          push or merge that branch.
```

**In session-branch mode** (§8) G2's *Not done* line reads `the preflight did not switch away from it — the plugin manages only branches it created. This run's artifacts WILL be committed on session/<identity>, the session branch this specs repository uses because its default branch takes no push, and not on <branch>.`, its *Fix* line `# nothing to do for the artifacts`, and its *If ignored* line `nothing changes for the artifacts: they reach <default> through session/<identity>'s pull request.` Where `<branch>` is that session branch itself, the *Not done* line reads instead `the preflight did not switch away from it. It is this specs repository's session branch, which the plugin commits to only while nothing stands on it, so this run's artifacts will NOT be committed.`, the *Fix* line `git -C "<SPECS_PATH>" switch <default>`, and the *If ignored* line `the artifacts stay in your working tree, and the first run after you switch back commits them.`

**On a direct `/dev-workflows:implement` run from inside the specs repository**
(§4.1) the run changes code here, so it cuts a branch of its own (its
Pre-Phase 3), and the artifacts are committed on that branch, whose name the
preflight does not know yet — or on `<branch>`, where the run stops before it
cuts one. Its *Not done* line reads instead `the preflight did not switch away
from it — the plugin manages only branches it created. This run changes code
here, so its artifacts WILL be committed on the branch it cuts for that, or on
<branch> if it stops first, and not pushed unless that branch's name carries one
of this plugin's prefixes.`; its *Fix* line reads `# nothing to do here: they
reach the maintainer when that branch is pushed or merged`; and its *If
ignored* line reads `the artifacts stay on that branch until it is pushed or
merged.` The code commit carries only the session files it takes; the rest
are committed after the run's push choice, by `commit-artifacts`, so pushing
at that choice does not take them (`/dev-workflows:implement` Phase 0 says
the same). In session-branch mode (§8) the code commit takes none: §8.3 lifts
them before its branch and again before its commit, and puts them back after it.

## 6. The outcome line

`commit-artifacts` step 7 emits exactly one of these, prefixed `Specs repo:`.
The caller places it per its own contract (§7) — inside its final report where
the report is the run's last output, or as its own terminal block where the
report was composed earlier.

| Case | Line |
|---|---|
| Committed and pushed | `Specs repo: committed <sha7> (<N> files) on <branch> — pushed` |
| Committed on the session branch and pushed (§8) | `Specs repo: committed <sha7> (<N> files) on session/<identity> — pushed; <F> session file(s) not on <default> yet: merge its pull request, or open one with gh pr create --head session/<identity> --base <default>`, `<F>` the count of paths `git -C "$SPECS_PATH" diff --name-only -z --no-renames <default-ref>...refs/heads/session/<identity>` prints |
| Session-branch mode, no identity (§8.1) | `Specs repo: NOT COMMITTED — session-branch mode is on and no identity names its branch; set GIT_USER_INITIALS (or git config user.initials), and the next run commits these files` |
| Session-branch mode, the script could not run (§8) | `Specs repo: NOT COMMITTED — session-branch.py could not run (<the first line of its stderr>); the files stay in your working tree, and the next run commits them` |
| Committed, not pushed — not a branch this plugin pushes (§4 step 5) | `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: this plugin pushes only the default branch and the branches it creates, so <branch> is yours to push; the artifacts reach the maintainer when you push or merge it` |
| Committed, not pushed — no remote to push to (§4 step 5) | `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: this specs repo has no origin remote` |
| Committed, not pushed — the user's git configuration pushes the branch elsewhere (§4 step 5) | `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: your git configuration pushes <branch> to <remote>, not to origin, which is the remote this plugin reads; push it where it belongs yourself` |
| Committed, not pushed — the remote deleted the branch (§4 step 5) | `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: origin has no <branch> any more, so it was renamed or deleted there, and this step does not recreate it; the commit stays on local <branch>` — and, where `<branch>` is the default branch, `; if origin renamed it, git -C "<SPECS_PATH>" remote set-head origin --auto names the new one` |
| Committed, not pushed — origin refused the branch before (§4 step 5) | `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: origin refused pushes to <branch> on <date> (<record>), and every commit since stays on local <branch>; to land the commits on local <branch>, put them on a branch of their own and open a pull request from it — git -C "<SPECS_PATH>" branch session-files-<YYYY-MM-DD> <branch> && git -C "<SPECS_PATH>" push -u origin session-files-<YYYY-MM-DD> — then, standing on <branch>, git -C "<SPECS_PATH>" reset --keep origin/<branch>; once origin takes pushes to <branch> again, rm "<record>"` |
| Committed, push refused by origin (§4 step 6) | `Specs repo: committed <sha7> (<N> files) on <branch> — push REFUSED by origin (<the reason in parentheses>): a rule there takes no push of <branch>, so this is recorded and no later run pushes it; to land the commits on local <branch>, put them on a branch of their own and open a pull request from it — git -C "<SPECS_PATH>" branch session-files-<YYYY-MM-DD> <branch> && git -C "<SPECS_PATH>" push -u origin session-files-<YYYY-MM-DD> — then, standing on <branch>, git -C "<SPECS_PATH>" reset --keep origin/<branch>; once origin takes pushes to <branch> again, rm "<record>"` |
| Committed, not pushed — the push would publish other commits (§4 step 5 `push-scope`) | `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: the push would also publish commits that are not this plugin's session-file commits, the oldest <sha7> <subject>, which carries <path>; push <branch> once they are ready to go, and the artifacts go with them` — or, where that oldest commit is this run's own, `Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: a pre-commit hook added <path>[, and <M-1> more] to this commit, so it carries more than this plugin's session files; check what the hook added before you push <branch>` |
| Committed, push rejected as non-fast-forward (§4 step 6) | `Specs repo: committed <sha7> (<N> files) on <branch> — push REJECTED: origin's <branch> has commits this one lacks, and no run takes them in for you; run git -C "<SPECS_PATH>" pull --rebase --autostash origin <branch>, then git -C "<SPECS_PATH>" push origin <branch>` |
| Committed, push failed for any other reason | `Specs repo: committed <sha7> (<N> files) on <branch> — push FAILED (<reason>); the commit is local and the next run retries it` |
| Nothing to commit | `Specs repo: no session artifacts to commit` |
| Locked | `Specs repo: skipped — another session holds the repo (index.lock); the next run picks the artifacts up` |
| Commit failed | `Specs repo: NOT COMMITTED — the commit failed (<the first line of git's error or the hook's output>); the artifacts stay staged, and a later run commits them once git accepts the commit (a merge concluded, a hook satisfied)` |
| Blocked (G0) | `Specs repo: NOT COMMITTED — see the notice below`, followed by the §5 G0 block verbatim |
| Misrooted (§3.1), whether or not the environment conditions hold | `Specs repo: NOT COMMITTED — SPECS_PATH is misplaced; see the notice below`, followed by the §3.1 notice, or `specs-root-check`'s stop, verbatim |
| Gate failed on environment, on a run carrying neither flag | *(no line at all — silent no-op)* |

When a guard fired at §3.3 G1 or G2, the outcome line is followed by that
guard's §5 block, repeated verbatim. Where the *push-scope* line's hook variant
fired, a path it names may be one that block, or the append below, calls
uncommitted, since the hook swept it into this run's commit: follow them with
`Specs repo: <path>[, …] is now committed in <sha7>, put there by a pre-commit hook, and not pushed`.

**`<record>` in the refused rows is the push-refusal record's path** (§1 rule 8). Where the record is the older configuration key instead — found there, or written there because the file could not be — the row names `branch.<branch>.workflowsPushRefused` in its place and clears it with `git -C "<SPECS_PATH>" config --unset branch.<branch>.workflowsPushRefused`, which needs a writable `.git/config`. **Where step 6 could write neither**, the *push refused* row says so in place of `so this is recorded and no later run pushes it`: `, and this could not be recorded (<error>), so the next run pushes <branch> again`; it names no `rm` or `config --unset`, and on the default branch no session-branch switch, since nothing turns the mode on.

**In session-branch mode** (§8) the not-pushed rows name the session branch as `<branch>`, and the *push refused* and *refused before* rows, when they name it, read from `to land the commits` on instead `once origin takes pushes to session/<identity>, rm "<record>"`, `<record>` being `session/<identity>`'s — the session branch is never stood on, so no `reset` is named for it. Where `sync.conflict` is not empty, append `; merging <default> into session/<identity> left <path>[, …] unsettled — settle them in its pull request`, and where `sync.error` is set, `; the merge of <default> into session/<identity> could not run (<sync.error>), and the next run tries again`. Where §8.2 printed `stranded` above 0, append `; your local <default> still holds <K> commit(s) origin refused, whose files are on session/<identity> now — to drop them, standing on <default>, run python3 "<the script's path>" --specs "<SPECS_PATH>" lift --branch session/<identity> && git -C "<SPECS_PATH>" reset --keep origin/<default> && python3 "<the script's path>" --specs "<SPECS_PATH>" put-back --branch session/<identity> --default-ref origin/<default>`, `<K>` being `stranded`. The *push rejected* row reads `Specs repo: committed <sha7> (<N> files) on session/<identity> — push REJECTED: origin's session/<identity> has commits this clone lacks, pushed from another clone under the same identity; the next run takes them in and pushes`. Where `mode` printed `unsupported`, the run's line, whichever it is, appends `; session-branch mode is on for this clone, but this git's merge-tree cannot merge without a checkout (it needs --write-tree and -X), so these files stay on <branch> until git is upgraded`. And where a *push refused* line names the default branch, the run is the one that turns the mode on, so its remedy, from `to land the commits` on, reads instead `from the next run on, session files go to session/<identity>, a branch of your own whose pull request lands them (session-branch mode), and these commits' files go there too` — with `a session branch of your own, once GIT_USER_INITIALS names it` in place of `session/<identity>` where §8.1 resolves no identity.

When the deliverable is still uncommitted because the user declined git at
handoff (§4.1), append to the line:
`; the deliverable at <path> remains uncommitted, as you asked`.

## 7. Caller contract

A command that writes anything into `$SPECS_PATH` must do all four of these.
Omitting any one of them is a defect, not a style choice.

1. **Cite and execute `specs-preflight` (§3)** at run start, once the run key
   set is known, in whichever of §3's cases the command falls; a run that
   stops on its address after resolution runs none, nor does one that stops
   before the preflight on a check of its own inputs needing no specs-repo state (§3). Phase 0 in most
   commands. Carry any returned `specs_git: blocked` or `specs_git: misrooted`
   flag for the whole run, and `specs_git: misrooted` from `workflows-core:addressing`
   §3 `specs-root-check` where its stop ended the run before any preflight.
2. **Cite and execute `commit-artifacts` (§4)** as the last action of the run,
   after `resume.md` (where one is written) and after the cost phase — or, where
   a later phase cedes control to another skill or to an open-ended interactive
   stretch, immediately before that hand-off (§4's exception).
3. **Emit the §6 outcome line exactly once**, wherever `commit-artifacts`
   ran — at the end of the run, or immediately before the hand-off in the
   cede-control case above.
4. **Never restate this reference's rules** — cite the section number. A rule
   copied into a command is a rule that goes stale.

## 8. Session-branch mode — a default branch that takes no push

Where the specs repository's default branch takes no direct push — branch protection, a ruleset, a policy or a hook — this reference keeps the run's session files on a per-user **session branch**, and the user lands them through its pull request. Everything above stands; this section says only what changes in the mode. `${CLAUDE_PLUGIN_ROOT}/scripts/session-branch.py` does the git plumbing, every call `--specs "$SPECS_PATH"`, and a change to either is a change to both. Each call prints one JSON object; exit 2 means it could not run, which is reported with the first line of its stderr while the run goes on (§1 rule 5).

### 8.1 When the mode is on

At §3.2 — and at §4 step 1 on a run that ran no preflight — run `… mode --default <default>`, never on a run carrying `specs_git: misrooted`, which commits nothing anyway. It prints `{mode, source, identity, identity_rung, branch}`. `mode` is `on` where `git config --bool workflows.sessionBranch` prints `true`, the user's own opt-in, which this reference reads and never writes; or where the default branch's push-refusal record stands (§1 rule 8), which §4 step 6 writes when `origin` refuses a push to the default branch. Both are local to the clone. `mode` is `unsupported` where one of them is set but this git's `merge-tree` cannot merge without a checkout (it needs `--write-tree` and `-X`): the run goes on as with the mode off, and §6's line says so. `branch` is `session/<identity>`, `<identity>` from `branch-naming.md` §2's first three rungs, never its prompt.

Where the mode is on, carry `session_branch: <branch>` for the whole run, and follow §3.2's fetch with a second, of the session branch alone: `git -C "$SPECS_PATH" fetch origin "+refs/heads/<session branch>:refs/remotes/origin/<session branch>"`, best-effort and silent where it fails, as it does while `origin` has no such branch; one fetch naming both branches would fail whole in that state. §3.1's gate, `specs_git: misrooted`, G0 and G1 gate the mode exactly as they gate everything else. G2 no longer decides where the files land: in the mode they go to the session branch whatever the checkout stands on (§5).

**No identity.** Where `branch` is null the run commits nothing in the mode: its session files stay in the working tree for the next run, the moves §8.3 wraps run unwrapped — git refuses one only where a dirty session file is in its way, and the step reports that as it reports any refused switch or pull — and §6's *no identity* line names `GIT_USER_INITIALS`.

**The session branch is never stood on.** Where a worktree has it checked out, `commit` and `put-back` exit 2 naming it and move nothing, since moving a branch under its own checkout leaves that checkout's index and files behind it; §6's *could not run* line carries the name, and G2's notice (§5) says to switch back.

### 8.2 Committing

In the mode nothing in this reference commits a session file on the checked-out branch. Where §3.4's flush or §4 step 4 would commit, run `… commit --branch <session branch> --default-ref <default-ref> --message "<that step's message>"`, adding `--include-ahead` where HEAD is the default branch. It:

1. creates the session branch where it does not exist, at the commit the checkout's files come from (`git merge-base HEAD <default-ref>`);
2. commits every session file the overlay holds (§8.3) — each path `git status` reports dirty and each where the branch differs from HEAD, by §2.1's classifier, a deleted one as a deletion — onto it through a temporary index. A working copy that is HEAD's version, or the version this worktree was last given, is not committed — save the files `--include-ahead` carries, which HEAD holds: the overlay is simply not in place there (a `lift` not yet put back, a second worktree, a switch back from the session branch, a file removed by hand), or another worktree moved the branch on, and the branch keeps its own. An absent session file is a deletion only under `dev-workflows-cost/` — `cost-emission.md` §9 relocates a pending cost file and deletes it, the one session file a run deletes — and only where HEAD holds it or this worktree held it, which the script records per worktree (path and version, in `session-branch-placed.json` under the git directory); any other absent session file is put back; a working copy of an appended shape (the `union` ones of step 3) that differs from the branch's version is first merged with it, `git merge-file --union` from the version at `git merge-base HEAD <session branch>`, and written back, so an entry only the branch holds survives a hand edit or a lift nobody put back; and with `--include-ahead` also the files of the commits on the local default branch that `<default-ref>` lacks, where every one of them is a session-file commit (the ones a refused push left there); it moves neither the checkout, the index nor HEAD;
3. then merges in `<default-ref>`, and `origin`'s copy of the session branch where one exists (another clone pushed it under the same identity), each where the branch lacks it, as `NOISSUE Merge <ref> into <session branch>` — a fast-forward where the branch holds nothing of its own, else `git merge-tree --write-tree -X ours` with git's `union` driver for the appended shapes, kept as one marked block in the repository's own `info/attributes`, which no commit carries — so a teammate's entries and this run's both survive, and an overwritten file (`resume.md`, `pr-draft.md`, unset there) keeps this run's version whole;
4. and brings each working copy that still matches the branch's previous version up to the merged one.

It prints `{committed, files, paths, created, stranded, ahead_not_session, sync}`. `committed: null` is §4 step 3's *nothing to commit*. A non-empty `sync.conflict` names files the merge could not settle, and `sync.error` says the merge could not run at all: either way the commit stands, its push goes ahead, and §6's line says so. The commit is built with `git commit-tree`, signed where `commit.gpgSign` is set, and runs no `pre-commit` or `commit-msg` hook: those judge a change staged in a checkout, and this one is neither; a rule on `origin` still judges its push.

### 8.3 The overlay, around every move of the checkout

In the mode the working tree's session files hold the session branch's version wherever it differs from HEAD, so every command keeps reading and appending them where it always has. Git refuses to fast-forward or switch over such a working copy, even a byte-identical one, so every move of the specs checkout is wrapped:

- **Before it, `… lift --branch <session branch>`.** Where a session file is not yet on the session branch it prints `unpreserved: [...]` and changes nothing: run §8.2's `commit`, with §4 step 4's message, then `lift` again. A second `unpreserved` skips the move, which the step that wanted it reports as it would a refused switch or pull; nothing is discarded. Otherwise it returns each dirty session file to HEAD — the one discard this reference makes (§1 rule 4), and only of content it has just found on the session branch.
- **After it, `… put-back --branch <session branch> --default-ref <default-ref>`.** It merges as §8.2 step 3 does, then writes each session file where the branch differs from the new HEAD, or removes it where the branch lacks it. A path whose working copy is neither HEAD's nor the branch's is merged with the branch's version as §8.2 step 2 merges it where its shape is appended, and listed in `merged`; any other is left as it is and listed in `skipped`, as is a pending cost file this worktree held and a run deleted, whose deletion §8.2 commits. A copy that is still the version this worktree was last given, where another worktree has since moved the branch on, is brought up to date like HEAD's. Where its merge cannot run, it puts the branch back as it stands and says so in `sync.error`. It runs whether or not the move succeeded, so the overlay returns over the checkout as it stands.

The moves: §3.4's catch-up and §4 step 2's repeat of it; §3.5's B2 (switch, pull, `branch -d`), B4 (switch, pull) and the re-run's switch back; `phase-handoff.md` §2.2's switch onto a new or reused deliverable branch, and its §3.3 row C repair; and a direct `/dev-workflows:implement` run from inside the specs repository, around its own branch and commit (its Pre-Phase 3 and Phase 4.6). **The preflight ends with `put-back` in the mode** whether or not it moved the checkout, and where a guard (§3.3) ended it, never under `specs_git: misrooted`, so a run interrupted between a `lift` and its `put-back` finds its overlay restored. Neither call prints anything where it succeeds, `skipped` included; an exit 2 is reported as this section's opening says.

### 8.4 Pushing, and the line

§4 step 5 pushes the session branch in place of the checked-out one — `git -C "$SPECS_PATH" push --porcelain -u origin <session branch>` — and §3.4's flush pushes it after its commit (§3.4). Step 5's conditions stand, with three differences for this branch alone:

- **The first condition holds:** the session branch is the plugin's to push (§1 rule 3).
- **A remote that deleted it does not stop the push.** A session pull request merged with *delete branch on merge* deletes it, and every later run's files would otherwise stay local for good; the push recreates it, and its next pull request shows only what has not landed.
- **`push-scope` counts the default branch as published.** The commits the push would publish are `git -C "$SPECS_PATH" rev-list --reverse refs/heads/<session branch> --not <base> <default-ref>`, or, with no base, step 5's `--not --remotes=origin` form, since the merges of §8.2 step 3 bring the default branch's own commits onto this branch and `origin` holds those already. Each must be a session-file commit as step 5 tests it, or a merge with exactly two parents (`rev-list --parents -n 1` prints three shas). Then the branch's whole change, `git -C "$SPECS_PATH" diff --name-only -z --no-renames <default-ref>...refs/heads/<session branch>` — what its pull request shows — must list ARTIFACT paths (§2.1) only; where it lists another, §6's *push-scope* line names the branch's newest merge commit and that path.

Step 6 reads the outcome as for any branch, and records a refusal of the session branch on it. A non-fast-forward rejection there means another clone pushed under the same identity first: the next run fetches that copy (§8.1), merges it in and pushes, which §6 says in place of naming a pull. The outcome line is §6's *session branch* row.
