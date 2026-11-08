# Scan refresh (shared reference)

Single source of truth for **when** a command's `code-scanner` dispatches refresh a clone, and when they read the session's own repository at its default ref by ref instead: the refresh question and its forms, the late join, a fixed policy, the `refresh:` lines each repository's brief carries, what a read by ref that fails does, and the line a read by ref gets in the run's report. **How** a read by ref is done is not decided here: `workflows-core:read-only-repos` §4 (*A writable clone read by ref*) is the authority on that, `code-scanner` step 2 runs it, and `workflows-core:read-only-repos` §7 says what a caller records after one. This file's consumers are not listed in it, so that no copy of the list goes stale: re-derive them with `grep -l 'scan-refresh' plugins/*/commands/*.md`.

**Why it exists.** `code-scanner` switches a checkout to its default branch under either fetch policy — a dirty one too under *fetch only*, which runs no dirty check — and the session's own repository is the checkout the user is working in. Where that repository stands on a feature branch with a clean tree, a refresh that switches every clone it scans moves the user's checkout without a word.

## 1. The inputs, and the session's repository

A caller supplies three inputs:

- **`session_repo`** — the repository the session runs in, where the working directory is inside one (`git rev-parse --show-toplevel`) that is not `$SPECS_PATH`'s: its top level, and its slug, taken from its `origin` — what `git -C <top level> remote get-url origin` prints, a trailing `/` and then a trailing `.git` stripped, its last path segment, what follows its last `/` or `:`. It is `none` where the working directory is in no repository, is in `$SPECS_PATH`'s, or is in one with no `origin`. A repository the scan resolves is the session's where its resolved path is that top level.
- **`asks`** — `true`, or `false` for a caller with a fixed policy, which it names (§4).
- **`scan_list`** — `known`, with the names the run has taken, where the list of repositories to scan is settled before the question and only a later step's answer can add to it; or `unknown`, where the list is settled after the question — derived by a later step, or open to a repository gate that can add repositories after it. Where `asks` is `false`, nothing is asked and `scan_list` is not read.

## 2. The branch test

Run on `session_repo`'s top level, wherever this reference asks whether that repository **stands on a branch other than its default**:

- **Its branch** is the one `git -C <top level> branch --show-current` prints. Where it prints nothing, HEAD is detached, which counts as another branch, `<branch>` reading `its detached HEAD at <short commit>` (`git -C <top level> rev-parse --short HEAD`).
- **Its default branch** is what follows `origin/` in what `git -C <top level> rev-parse --abbrev-ref origin/HEAD` prints, where that exits 0 — `<default>` below. Where it exits non-zero — `origin/HEAD` unset, when it prints `origin/HEAD` itself — the run cannot tell, which counts as another branch too, and the four-option question takes its unknown-default form.

So a detached HEAD whose default branch the run can tell takes the **known**-default form, its `<branch>` naming the detached commit; an `origin/HEAD` that does not resolve takes the **unknown**-default form, whatever HEAD is.

## 3. The questions

### Entry point: `refresh-question`

Run once, at the step the caller names, with the three inputs (§1). It returns the answer — the run's refresh policy — and §5 maps that policy onto each repository's `refresh:` lines at dispatch: `switch_to_default_branch`, `pull`, and `read_default_by_ref` where it is true. Where `asks` is `false`, nothing is asked: §4 is the policy.

**The three-option question** — asked where `session_repo` is `none`, where the branch test (§2) finds that repository on its default branch, or where `scan_list` is `known` and the session's slug is not among the names taken:

```
choices: ["fetch + pull default branch (Recommended)", "fetch only", "no refresh"]
```

The `fetch + pull default branch` default matches `code-scanner`'s default (`refresh.switch_to_default_branch: true, refresh.pull: true`) — capability scans target present-day code and want the default-branch tip. This is deliberately different from `/docs-workflows:document` (keyed mode), which keeps `pull: false` because historical merged commits must not move.

**The four-option question** — asked instead where the session's own repository stands on a branch other than its default (§2) **and may be scanned**, in one of two forms, by whether the run knows that repository's default branch (§2), `<session-slug>` in each being `session_repo`'s slug and `<branch>` its branch as §2 reads it:

- **Its default branch known** — `<default>` below — the question's own text naming that repository, the branch it is on and its default branch, and saying that the first option reads the default branch's tip by ref, as one fetch from `origin` finds it, without moving the checkout or reading its working tree; that *fetch + pull default branch* switches a scanned repository to its default branch; and that *fetch only*, which this form does not offer, may still be typed, applying to every repository scanned, the session's included, as below:
  ```
  choices: ["fetch + pull default branch, but read <session-slug> at origin/<default> by ref — your checkout stays on <branch> (Recommended)", "fetch + pull default branch, but scan <session-slug> on <branch> as it stands", "fetch + pull default branch, <session-slug> included", "no refresh"]
  ```
- **Its default branch unknown** — the question's own text naming that repository and the branch it is on, saying that its default branch is unknown, so there is no ref to read it at, and saying that *fetch + pull default branch* and *fetch only* switch a scanned repository to its default branch:
  ```
  choices: ["fetch + pull default branch, but scan <session-slug> on <branch> as it stands (Recommended)", "fetch + pull default branch, <session-slug> included", "fetch only, <session-slug> included", "no refresh"]
  ```

Since `code-scanner` switches a checkout to its default branch under either fetch policy, and the session's repository is the checkout the user is working in, neither *but* answer moves it, and each gives every other repository *fetch + pull default branch*'s settings in the scan's brief. **The *read … by ref* answer reads the merged code**: the session repository's brief carries `refresh.read_default_by_ref: true`, on which `code-scanner` fetches `origin` once and reads `origin/<default>`'s tip by ref, never the checkout's branch or its working tree — a live `/product-workflows:epics` run that took *scan … as it stands*, the answer recommended then, grounded its Epic in the feature branch's unmerged endpoint and test. **The *scan … as it stands* answer reads the branch, its unmerged work included**: that brief carries *no refresh*'s settings. The other answers, a typed *fetch only* among them, apply to every repository scanned, the session's included.

**May be scanned** is known where `scan_list` is `known` — the session's slug is among the names taken, or it is not, and where it is not the three-option question is asked instead, the `late-join` entry point putting the four-option question before the scan should the session's repository join the list later. Where `scan_list` is `unknown`, whether that repository may be scanned is unknown, and there the four-option question is asked, either *but* answer acting as *fetch + pull default branch* where the session's repository turns out not to be scanned.

### Entry point: `late-join`

Run by a caller whose `scan_list` was `known`, once its repository list settles — a step after the question, a path given at a missing-repository answer or a name a later picker takes, can add the session's own repository after the refresh policy was answered without it. Where a resolved path is that repository's top level, the refresh policy was answered on the three-option question with *fetch + pull default branch* or *fetch only*, and the branch test (§2) — run now where the question did not run it — finds that repository on a branch other than its default, a detached HEAD and a default the run cannot tell included, ask the four-option question before the scan, in the form §2's default-branch test picks, its array and its text as *The four-option question* writes and words that form, naming the earlier answer too and saying that this answer replaces it for every repository the scan covers — as it does: a user who answered *fetch only* and takes the recommended option gets *fetch + pull default branch* on every other repository. Otherwise nothing is asked. Without it, the scan would switch the checkout the user works in to its default branch on an answer given before that checkout was on the list.

A caller whose `scan_list` was `unknown` never runs it: its question already covered the session's repository.

## 4. A fixed policy

A caller that asks no refresh question and switches every clone it scans — `asks: false`, its fixed policy one that sets `switch_to_default_branch: true` — reads the session's own repository by ref wherever the branch test (§2) finds it on a branch other than its default, a detached HEAD and a default the run cannot tell included: that repository's brief carries `read_default_by_ref: true`, and every other repository the fixed policy. The test is applied at each dispatch, so it covers the session's repository whenever that repository joins the list. Nothing is asked: the read by ref reads the default branch the fixed policy wants, without moving the checkout. Where the run cannot tell the default branch, `code-scanner` resolves the ref itself, with a capped `git remote set-head origin --auto` and `workflows-core:read-only-repos` §3's chain, and returns `REFRESH_BLOCKED` only where that chain is exhausted (§6).

## 5. The brief's refresh lines

Each repository's `code-scanner` brief carries, per the run's refresh policy — the refresh question's answer, the late join's where `late-join` asked, or §4's fixed policy:

```
refresh:
  switch_to_default_branch: [true if the refresh policy is any form of 'fetch + pull default branch' (default) or of 'fetch only', a typed one included; false if 'no refresh', and false for the session's own repository where the policy reads it by ref or scans it on its branch as it stands]
  pull: [true if any form of 'fetch + pull default branch', save for the session's own repository where the policy reads it by ref or scans it as it stands; false otherwise]
  read_default_by_ref: [true for the session's own repository where the policy reads it at its default branch by ref — the *read … by ref* answer to the four-option question, at the refresh question or at the late join, or §4's fixed policy; omit the line otherwise]
```

Under §4 the fixed policy stands where this mapping names the question's answers. A repository the caller dispatches with settings of its own whatever the policy — a repository it never switches, pulls or stashes — keeps them; this mapping does not reach it.

After a read by ref the checkout still holds the branch's unmerged work, so a caller that reads that repository's files itself reads them at `prep.scanned_ref`, never in its working tree — `workflows-core:read-only-repos` §7's caller contract.

## 6. A read by ref that fails

- **Its fetch failed** — `prep.read_only: false`, `prep.refreshed: false`, and `prep.refresh_note` naming the failed fetch — not a failure: the scan read `prep.scanned_ref` as the clone last fetched it, which may be behind `origin`, and never fell back to the working tree. Nothing is asked; the run's report line for that repository (§7) says that the scan read a stale default ref, and names the failure `refresh_note` gives. Never fail silently.
- **`REFRESH_BLOCKED`** — on a read by ref, the session's repository, its brief carrying `read_default_by_ref`, `code-scanner` returns it only where `workflows-core:read-only-repos` §3's chain cannot resolve the default ref. Escalate as the caller escalates any `REFRESH_BLOCKED`; its *Continue with current local state* re-dispatches that repository with the *scan … as it stands* answer's settings, reading its branch and its unmerged work, and the question's own text says so. That re-dispatch is no read by ref: what the caller records after it is what it records after any scan of a working tree (`workflows-core:read-only-repos` §7). **A caller with a fixed policy (§4) may leave *Continue with current local state* out** of the list it asks after a read by ref, where its own reason for the policy rules out a scan of the branch — it reproduces the list inline without that option, stating which list it uses, as `workflows-core:escalation-rules`' *Refresh blocked* lets an inline citer do, and the question's own text says why.

## 7. The report line

The run's report line for each repository whose brief read it by ref carries, after its status, `read by ref at <prep.scanned_ref>; checkout left on <branch>` — or, where its fetch failed (§6), `read by ref at <prep.scanned_ref> as last fetched — a stale default ref: the fetch failed (<the failure prep.refresh_note names>); checkout left on <branch>` — `<branch>` being the one `prep.refresh_note` names the checkout left on. Every other repository's line carries neither. Each caller's report template carries this wording in a slot of its own, so that the run fills a line rather than remembering a rule; a change to it here changes every slot, which `grep -rn 'read by ref at <prep.scanned_ref>' plugins/*/commands` lists.
