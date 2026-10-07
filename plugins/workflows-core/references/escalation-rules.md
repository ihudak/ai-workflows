# Escalation rules (shared)

Canonical `choices:` arrays for escalation decision points. Command bodies are authoritative; where
`/document` and `/epics` differ for the same scenario, both variants are listed.

## §0 — Array shape: two to four options, and the free-text option is the harness's

**Every `choices:` array in this plugin and in every plugin that depends on it carries between two
and four options, and never authors an "Other" option of its own.** `AskUserQuestion` renders
`minItems: 2, maxItems: 4` and supplies the free-text escape itself — its own schema says *"There
should be no 'Other' option, that will be provided automatically."* A five-option array is not a
long prompt; it is a tool call the harness rejects at validation, so the run cannot present it at
all.

This replaces the rule that stood here, which said the opposite: that every array ends in
`"Other… (describe)"` and that adding one where a phase omitted it was a permitted adjustment. That
rule authored 136 duplicate options across 30 files and pushed 42 arrays past the cap, and it did it
while the file next to it insisted the arrays be presented verbatim — a rule the harness made
unfollowable.

**Two consequences, both of which the rest of this file now depends on:**

1. **The free-text option is unconditional.** No array can decline it. A picker that used to protect
   a closed vocabulary by *omitting* the option cannot do that any more, and must handle the answer
   instead — see the next section.
2. **A fifth option must go somewhere else, not away.** Where an offer has more routes than four,
   `${CLAUDE_PLUGIN_ROOT}/references/next-phase-offer.md`'s overflow rule applies: the prose carries
   every route, the array carries the likeliest, and the run says the list is longer than the prompt.

## Choice lists are presented verbatim

**A choice list written into a command phase is presented to the user verbatim. Its options, their
order, their wording, and the `(Recommended)` marker are not the orchestrator's to change. An
orchestrator that believes a different option is correct for this run says so in prose alongside the
list — it never edits the list.**

This rule binds every command in the family — this plugin's own and those of every plugin that depends on it — not only the ones documented below. It exists because a
`/document` run presented Phase 6.5's `["Run smoke-check (Recommended)", "Skip — use the manual table
only", "Cancel"]` with the recommendation moved onto Skip, and the render gate was never exercised.

There is no permitted adjustment. Under §0 an array's options are exactly what its phase wrote, and
the free-text option is the harness's — neither is the orchestrator's to add to or take from.

## Closed-vocabulary pickers must normalise the free-text answer

A picker whose options are drawn from a **closed vocabulary another authority fixes** has no room for
a fifth *value*: one nothing downstream can read is a state no consumer handles. These pickers used
to protect that by omitting the free-text option. **Under §0 they cannot** — the harness supplies it
whatever the array says — so the protection moves from the array's shape to the run's handling of the
answer:

**A free-text answer on one of the nine arrays below is normalised into that array's own vocabulary,
or the question is re-asked. It is never written through as a new value.** `/document`'s image
disposition is the shipped worked example: its free text *"resolves to one of the three dispositions
above … There is no fourth disposition and no 'skip on my own judgement' path here."*

**The nine:**

| Array | Its closed vocabulary | Owner |
|---|---|---|
| the candidate-confirmation picker, with its two-option form for an answer matching no question the package put | `confirm` / `correct` / `reject` / `ask-the-customer`; on that form, `record-for-a-human` / `reject`, or a re-point onto a question the package put, which re-asks the candidate on the four-option form — never a freeze | `/product-workflows:brd-reconcile`, *Confirm every candidate* |
| the missing-reason picker | ask the customer, or freeze `status: open` | `/product-workflows:brd-reconcile`, *Confirm every candidate* |
| the propagation-sweep picker | `inherited-unchanged` / `reverted` / `reopened` / `withdrawn`; presented without `reopened` on an `[AS#n]` item or on any decision not `decided`, without `reverted` on an item whose prior position the record does not preserve or whose restored evidence the will-change rule fires on unresolved, and not presented at all on an item whose record is `superseded` or `withdrawn` | `/product-workflows:brd-reconcile`, *The propagation sweep* |
| the will-change resolution picker | the exactly three resolutions of `product-workflows:decision-register-format` §6 | `/product-workflows:brd-interview` |
| the `[SR#n]` disposition picker | `fixed` / `accepted-risk` / `escalated-to-customer` / `rejected-with-reason`; presented without `fixed` where the finding's named artifact is one this command may not change | `/product-workflows:brd-package` |
| the degradation-tier picker | `Full` / `Partial` / `Documents only` — the three rows of `product-workflows:bundle-packaging` §3 | `/product-workflows:brd-package` |
| the customer-content ruling picker | ship the package, or hold it — the two outcomes `product-workflows:bundle-packaging` §6.3's *The operator's ruling* fixes | `/product-workflows:brd-package`, once per pass that reports a hit |
| the `engagement_model` picker | `time-and-material` / `fixed-price` | `/product-workflows:prd-proposal` Phase 2, over the two shapes `product-workflows:proposal-format` §4 sections 16–18 fixes; `/product-workflows:brd-proposal` re-asks the same question over the same committed profile |
| the conflicting-answer picker | freeze this candidate / keep the earlier one / ask the customer — the one not frozen set aside as a conflicting answer, never a second freeze | `/product-workflows:brd-reconcile`, *Confirm every candidate* |

**The eighth is the one whose value is re-read as configuration by later runs of the same commands**,
which is why it is here rather than left to the command: the answer is written to a committed
`proposal-profile.yml` and loaded again on every later run of **both** proposal commands, to choose
which of `product-workflows:proposal-format` §4's two section shapes to render — so a third value
written through would be re-read indefinitely by two commands with no shape to render for it. It is
never consumed once and closed.

**Outliving its own run is not what distinguishes it, and six other rows falsify that weaker
property** — it was claimed here once and was wrong. Row 5's `[SR#n]` disposition is read by a later
run of a **different** command, as the defect-remediation sweep's third source
(`product-workflows:proposal-format` §7). Rows 1, 2, 4 and 9 write into `decisions.md`, whose frozen
`[VD#n]`s and `[CD#n]`s are read on later runs by `/create-prd`, `/create-ard` and `/specify`, each
filtering them by altitude. Row 3's disposition is written onto a dependent BRD's register row and
read there the same way. Every one of those is a **record** of what was decided, read back as evidence
about one finding or one requirement; only the eighth is a **setting** that shapes what a later run
renders. Rows 6 and 7 are the two genuinely spent inside their run — row 6's tier is recorded as a
fact about that dated bundle, never reloaded to shape a later one, and row 7's ruling binds the
passes of the run that took it and reaches the run's final report as an outcome line, nothing later
reading it back. So check the property in every row before claiming one, rather than checking that
the row is in the table.

The eighth also has a **second route to the same field** — the proposal-profile confirmation
picker's *Correct a field* option, in both commands — and that route is normalised the same way.

**The first three, and the ninth, are load-bearing beyond tidiness, and the reason is worth carrying.** They are the
pickers through which a customer's authority enters the decision register, and D14 exists because
**normalising prose into a register row is inference, and promoting inference to customer authority
silently is the one way that workflow could fabricate a mandate the customer never gave.** A free-text
entry on a picker about what the customer decided is a box into which something that is neither their
decision nor a refusal of it can be typed and then frozen as theirs — the exact route D14 closes,
re-opened by an adjustment made in good faith against this file. A rule contradicted by its own
authority is not a rule, so the carve-out is written here, by name, rather than left to each command
to assert against a reference that overrules it.

**No operator is trapped, and the reason is no longer `Cancel`.** Three of the nine carried a
trailing `Cancel` until the four-option cap was enforced, and it was dropped from each — a fifth slot
the harness would not render. The escape that replaces it is the free-text option, which is always
present and, on these nine, is normalised rather than frozen. Where aborting has a consequence the
operator must see before choosing, the command states it in the prose introducing the walk rather
than in an option: `/brd-package`'s and `/brd-reconcile`'s walks both do.

**This list is closed, and it is not a licence to prune elsewhere.** It marks where a free-text answer
needs *normalising*, not where an array may be shortened; §0's cap binds every array equally.

## The `(Recommended)` marker is unconditional

**A `(Recommended)` marker applies whenever its list is shown.** A marker that carries its own
condition — `(Recommended for <case>)`, `(Recommended if <case>)` — is malformed: it hands the user
the gate the command was supposed to evaluate, and it cannot be honoured verbatim by an orchestrator
that must not edit the list. Write it one of two ways instead:

- the condition **gates the prompt** (the list is only shown in that case) → the marker is a plain
  `(Recommended)`; or
- the condition **lives in the option's own description** → the list carries no marker at all.

A **reason** annotation is not a condition and is fine: `(Recommended — <why>)` states why the option
is recommended, unconditionally, and is honoured verbatim like any other marker (`/document`
Phase 5 and `/epics` Phase 1 both use it).

**A marker the command resolves through a placeholder is not a violation of this rule, and it is not
an edit to the list.** Where which option is recommended varies per showing, the array may carry a
placeholder the command substitutes — `/brd-split`'s Phase 4 walk writes `<recommended>` on each of
its dispositions and resolves it, per row, to `(Recommended — <why>)` on one and to the empty string
on the rest. That is substitution, exactly as `<BRD-KEY>` and `<merge-clause>` are substituted in
the same strings (`references/next-phase-offer.md`), and it is the mechanism this section's first
bullet asks for: the **command** evaluates the condition and prints a bare, reasoned marker, rather
than printing the condition for the user to evaluate. What stays forbidden is the orchestrator
deciding a marker belongs somewhere the command did not put a placeholder.

When no option is safe to recommend across the runs that reach a prompt, omit the marker and say so
in prose beside the list (as `/document` Phase 5.6 does for its per-occurrence image review).

This rule binds every command in the family — this plugin's own and those of every plugin that depends on it — not only the ones documented below.

## When a choice list fires

**A choice list blocks whenever it is shown.** Presenting one and continuing without an answer is never
correct — the list *is* the wait.

**A list is shown only when its firing condition holds.** A list with no written condition is shown
every time its phase runs. That is the default, and it is the right default for most phases.

**A list written for a question whose answer is already determined is a defect**, not a formality — it
spends a user turn on a prompt with one plausible answer. Where the answer is determined on some runs
and open on others, write the firing condition and keep the list for the runs where it is open.

**The inline-confirmation form.** When the answer is determined, state the resolution in one line that
names what was resolved and how to correct it, then proceed without waiting:

```
Reading this as a <type> — say so if it's actually a <other-type>.
```

An inline confirmation is **not** a choice list: it carries no `choices:` array, it never waits, and the
run continues on the stated resolution. It is the correct form wherever a phase would otherwise ask a
question with one plausible answer.

This rule governs only *whether* a list is presented. Option wording, option order, and the
`(Recommended)` marker are governed by the two rules above and are untouched by it.

This rule binds every command in the family — this plugin's own and those of every plugin that depends on it — not only the ones documented below.

## key dir not found

`choices: ["Re-enter key", "Cancel"]`

Used when the address resolved to no folder — `resolve-address` returned `status: absent`, or a
folder that resolved earlier in the run is gone when a later phase reads it.
**A folder that is there is never this case, whatever it holds**: re-entering a key that resolved
cannot help. A command that stops on what such a folder holds — a BRD container, a folder placed at
no level, a PRD folder carrying no key, a PRD folder with no `prd.md` — raises a named stop of its
own instead, as `/document`'s and `/release-notes`' `*_BRD_NOT_SLICED`, `*_FOLDER_NOT_PLACED`,
`*_PRD_NO_KEY` and `*_NO_PRD` do. (The
folder read is an inline step each command performs, not an agent returning a status — this rule
described a dispatch that no longer exists.)

## Required path environment variable unset

`choices: ["Set <VAR> (enter the path)", "Cancel"]`

Used when a command stops in Phase 0 because a path environment variable it requires is unset, or
resolves to nothing that exists. `<VAR>` is that variable's own name, written out — the list names
the variable the run is missing, never a generic placeholder.

`/brd-intake` (Phase 0 step 5), `/prd-ground` (Phase 0 step 3 for `SPECS_PATH` and Phase 0 step 7
for `REPOS_PATH`), `/brd-split` (Phase 0 step 2), `/brd-interview` (Phase 0 step 3), `/brd-package`
(Phase 0 step 3), `/brd-reconcile` (Phase 0 step 3), `/frames` (Phase 0 step 0), `/prd-proposal`
(Phase 0 step 1), `/brd-proposal` (Phase 0 step 1), `/idea` (Phase 0 step 1), `/implement` (Phase 0
*Address resolution*, on a `<KEY>` address only), `/document` (*Mode detection*, keyed mode on a
`<KEY>` address only) and `/release-notes` (Phase 0 step 1, on a `<KEY>` address only) cite this
rule by name — for every one of them but `/prd-ground`, `SPECS_PATH` is the only path variable it
requires, since none of the others requires a repository root (`/idea --ground-code`, `/document`
and `/release-notes`' opt-in diff grounding read `${REPOS_PATH:-/workspace}` with its default and
never stop on it unset; a `$DOCS_PATH` that does not resolve only skips documentation grounding, or, in
`/document`, one rung of its docs-repository ladder, and stops nothing). **State the set by its
property, not by counting from the end of the list, nor by naming a subset**: the clause read "for
the last four" until the list grew, at which point it silently described a different set, and a
named subset that replaced it then left `/brd-split` and `/brd-intake` out of it. Derive the set
rather than trusting this list:
`grep -rl 'Required path environment variable unset' plugins/*/commands/*.md`, run from the
repository root. It is a stop, not a degradation: there is no "continue without it" option, because
the path is where the run's inputs and outputs live. Other commands reproduce the same two-option
list inline without naming the rule; a citer that names the rule uses the list written here.

## Repo unresolved (zero matches) — /document

`choices: ["Skip and continue without its refs", "I'll clone it — wait", "Cancel", "Specify a different absolute path for this repo"]`

Used in `/document` Phase 4 when a repo slug has zero matches in the
slug→clone map. The first option names **refs**, not PRs: that command builds
its `refs[]` from `implementation.md` and the `git log --grep` scan beside it,
and reads no pull request (`/document` Phase 4 step 1).

## Repo unresolved (zero matches) — /epics

`choices: ["Skip and continue without this repo's scan", "I'll clone it — wait", "Cancel", "Specify a different absolute path for this repo"]`

Used in `/epics` Phase 4 when a repo slug has zero matches in the
slug→clone map.

## Repo unresolved (zero matches) — /prd-ground

`choices: ["Skip and continue without this repo", "I'll clone it — wait", "Cancel", "Specify a different absolute path for this repo"]`

Used in `/prd-ground` Phase 1 step 3 when a repo the operator named has zero matches in the
slug→clone map. Same options, same order as the `/epics` variant above; the first one drops
"'s scan" because this command grounds a claim against a repository rather than scanning one for
capabilities, and skipping it leaves that repository's claims ungrounded rather than unscanned.

## No repos derivable — /epics

`choices: ["List repos to scan manually", "Proceed without code scan", "Cancel"]`

Used in `/idea` Phase 2.6 when the proposed theme → repo mapping is empty (no
theme matches any mounted repo), and in `/epics` Phase 4 when the final
resolved repo list is empty (every repo was skipped or missing — "Use case B
with no repos derivable"). The `— /epics` suffix on this heading is historical
— `/epics` was its first citer — not a scope restriction; the rule now serves
both commands listed above, and any future citer with the same empty-repo-set
shape uses it too.

In `/prd-ground` Phase 1 step 4 the *Proceed without code scan* entry is omitted:
`choices: ["List repos to check manually", "Cancel"]`

and *scan* reads *check*, for the reason the `— /prd-ground` heading above gives. The dropped
option is not a shortening: grounding has nothing to check a claim against without at least one
mounted repository, which is why that command already refuses to start with none
(`/product-workflows:prd-ground` Phase 0 step 7) — an option offering to proceed anyway would name an
outcome the command cannot deliver.

## Repo missing (after resolution)

`choices: ["Skip this repo", "I'll clone it — wait", "Specify a different absolute path for this repo", "Cancel"]`

Used when a diff-summarizer or code-scanner batch returns `REPO_MISSING` at
Phase 5 after Phase 4 already checked, in `/idea` Phase 2.6, which has no
earlier check, and in `/implement` Phase 1.7. `REPO_MISSING` means `repo_path`
is not a directory **or** the clone's `origin` slug does not match
`repo_url_slug`; *Specify a different absolute path for this repo* is the
option that resolves the second case, which the previous list had no answer
for at all. Present this choice per affected repo. No `(Recommended)` marker —
which option is right depends entirely on why the repo is absent.

## Stashing the user's changes

**Six stash choices run this procedure**: the Stash choice of § *Dirty working tree* below, and the
"Stash … and continue" choices of the documentation commands that branch a repository they write
into (`/document` Phase 6.2's two, `/docs-profile` Phase 5, `/docs-init` Phase 2.5 and `/docs-brand`
Phase 7). `/implement`, `/upgrade` and `/vuln` keep their own: each records a `stash_ref` that
`dev-workflows:code-handoff` reads.

1. **Stash under a name no other run shares**, reading the stash ref on both sides of it:
   `git -C "<repo>" rev-parse -q --verify refs/stash` (empty where there is none), then
   `git -C "<repo>" stash push -u -m "<command> <KEY>: <why> <UTC timestamp>"`, untracked files
   included, since `status --porcelain` counts them, then the same `rev-parse` again. `<KEY>` is the
   run's key, or its command name alone where it has none. Never a bare `git stash`. **Where the
   ref did not change, nothing was stashed** — git prints `No local changes to save` and exits 0 on
   a clean tree — so record nothing, say so, and go on as the choice says. **Where the push exits
   non-zero** (`You do not have the initial commit yet` on a repository with no commit), report
   git's message and present the choice that led here again.
2. **Record it at once**: its commit, the ref's new value, and where HEAD stood when the run
   reached the choice — `git -C "<repo>" branch --show-current`, or, where that prints nothing (a
   detached HEAD), `git -C "<repo>" rev-parse HEAD`. A caller that has already moved HEAD records
   where it stood before the move, and passes that.
3. **Never apply or pop it.** The run then moves HEAD — a switch, a pull, a new branch — and the
   changes belong where they were made.
4. **Name it wherever the run ends** — its final report, or the stop message of a run that ends
   early, a later repository's *Cancel* included; a run inside another (`/docs-profile --inline`
   inside `/document`) hands the record back, and the outer run names it — by its message, with the
   commands that restore it: `git -C "<repo>" switch <branch>` (`switch --detach <commit>` where HEAD was detached), then
   `git -C "<repo>" stash apply <stash commit>`, and once the result is checked,
   `git -C "<repo>" stash drop <ref>`, `<ref>` being the `stash@{<n>}` that
   `git -C "<repo>" stash list --format='%gd %H'` pairs with that commit. **By commit, never by
   index**: the stash stack is shared by every worktree and session, and each later stash shifts
   every index under it.

## Dirty working tree

`choices: ["Stash changes and retry this repo", "Use the checkout as it stands — no fetch, switch or pull", "Skip this repo", "Cancel"]`

Used in `/document` Phase 5 when a diff-summarizer returns `DIRTY_TREE`. `/create-ard`, `/design`,
`/release-notes` and `/implement` (Phase 1.7) cite this rule by name without reproducing the list,
so per the "Choice lists are presented verbatim" convention above they use the list written under
this heading; `/epics` (Phase 5) and `/specify` (Phase 4) reproduce the same list inline. **`/docs-audit`
reproduces a list without the second choice**, and says why: its coverage denominator is a claim
about the product as it ships. A new citer that reproduces a list inline states which one it uses.

**The uncommitted changes are the user's, in a repository the run only reads, so no choice commits,
pushes or discards them.** Each choice does exactly this, and **the answer holds for the rest of the
run**: a later dispatch to the same repository — a second scan round — is made the way the answer
left it, and asks nothing.

- **Stash changes and retry this repo** — stash per § *Stashing the user's changes* above, then
  re-dispatch the agent for this repo unchanged.
- **Use the checkout as it stands — no fetch, switch or pull** — re-dispatch the agent for this repo
  with its refresh off: `code-scanner` with `refresh.pull` and `refresh.switch_to_default_branch`
  false, `diff-summarizer` with `refresh.fetch` and `refresh.pull` false. Neither then changes the
  repository. **`code-scanner` reads the working tree as it is**, so a line it cites may be one no
  commit holds: the run's final report says so per repository —
  `<repo>: read as it stands at <prep.branch_at_scan> @ <git -C "<repo>" rev-parse --short HEAD>, with uncommitted changes`
  — and an ARD, specification, design or Epic the run writes says the same where it names the code
  it was grounded on (an ARD's `## Grounding findings`). **`diff-summarizer` diffs the refs the
  clone already holds**, which may be behind `origin`; the final report says
  `<repo>: read without a fetch`.
- **Skip this repo** — the run goes on without it, and its report names the repository skipped.
- **Cancel** — the run ends, naming any stash it took.

## Branch prefix undetected

`choices: ["Use `<fallback>` (default for this command)", "Use my initials — I'll enter them"]`

Used by every branch-creating command (`/implement`, `/document` (keyed mode only — a direct-mode run creates no branch), `/docs-profile`, `/docs-init`, `/docs-brand` standalone, `/upgrade`, `/vuln`) when the `branch-naming.md` §2 identity ladder — `$GIT_USER_INITIALS`, `git config user.initials`, then inference from existing branches — yields nothing. `<fallback>` is that command's own default (`feat/`, `docs/`, `fix/`, `chore/`).

**Identity variant.** When the value is filling an **identity** placeholder in a convention documented by the repo itself (`<your-name-or-initials>`, `<user>`, …), the fallback choice is omitted — a generic prefix is not a name, and the documented convention requires a real identity:

`"This repo's documented convention starts the branch with your name or initials, and I couldn't infer one. What should I use?"`
`choices: ["Enter my initials", "Cancel"]`

Either way, prompt for the value with: `"Enter your initials (lowercase; 2–8 characters from [a-z0-9-], starting with a letter or digit, e.g. `iv-gu` or `ivgu`):"` — then suggest, without persisting, `GIT_USER_INITIALS` or `git config --global user.initials`.

## Refresh blocked

`choices: ["Continue with current local state", "Skip this repo", "Cancel"]`

Used in `/document` Phase 5 when a diff-summarizer returns `REFRESH_BLOCKED`. `/create-ard`, `/design`,
`/docs-audit`, `/release-notes` and `/implement` (Phase 1.7) cite this rule by name without
reproducing the list, so per the "Choice lists are presented verbatim" convention above they use the
list written under this heading; `/epics` (Phase 5) and `/specify` (Phase 4) reproduce the same list
inline. A new citer that reproduces a list inline states which one it uses.

## Read-only mount — ref stale or diverged

`choices: ["Scan released code at `<ref>` (Recommended — cites shipped behavior)", "Cancel — refresh on the host (`git -C <path> fetch`) or re-mount read-write, then re-run"]`

Used when `code-scanner` or `diff-summarizer` returns `prep.read_only: true` **and** either `prep.ref_committed_at` is more than 14 days old or `prep.head_divergence.ahead > 0`, per `${CLAUDE_PLUGIN_ROOT}/references/read-only-repos.md` §5. Present per affected repo. Neither agent accepts a scan-target parameter — a user who genuinely needs the unmerged working tree says so through the harness's free-text option (§0), because scanning an unmerged tree is what caused this feature's original defect: released behavior cited from unreleased code.

A read-only mount is not a failure and does not use the `Refresh blocked` list: the scan proceeds at `prep.scanned_ref`. This prompt exists only because the container cannot fetch, so refreshing the clone is an action only the user can take on the host.

The condition gates the prompt, so the `(Recommended — <why>)` reason annotation is well-formed under the rules at the top of this file.

## A recorded verdict names the version it was taken against

**The review cap assumes a fix cycle only removes defects, and three live runs proved otherwise.** On
each, the fix applied after a BLOCK **introduced** something the re-review then found — and by then
the one-fix-cycle-plus-one-re-review budget was spent, so the run's choice was to ship a known defect
or to fix it and leave the final text unreviewed. Both branches end the same way: the verdict on
record was reached against a version of the artifact that is no longer the one on disk, and nothing
says so. A reader meets a `PASS` beside a file the `PASS` never saw.

**Every command that records a review verdict states what that verdict was taken against**, and where
**any** edit followed it — a `MAJOR` fix applied inline, an escalation's manual fix notes, a deferred
finding written into the artifact, a style pass, a resumed verify step — the final report says so
plainly and names the edits. One line: *"`<verdict>` was reached before <the edits>, which followed
it; the current text has not been reviewed."*

**Which commands those are is derived, not listed, and a phrase grep is not the derivation.** The set
was first taken from the commands carrying the literal *"one fix cycle + one re-review"* cap, which
missed `/vuln` and `/upgrade` — both run one fixer pass and one re-review, both edit afterwards
through a resumed verify step, and `/upgrade`'s own results table carries a `Review` column. The test
is behavioural: **a command records a review verdict, and anything it does afterwards can change what
that verdict was about.**

**Once the cap is spent, this is deliberately a reporting rule and not another cycle.** Raising the
cap trades one unreviewed version for a later one and has no fixed point, since each new review can
find something the previous fix introduced. What actually costs the reader is not the unreviewed
edit — a run has to stop somewhere — but believing the verdict covers it. Saying which version it
covers costs nothing, cannot itself introduce a defect, and leaves the decision about the residue
where it belongs. **Where no edit followed the verdict, say that too**, so a clean run reads as
checked rather than as unreported. A run whose verdict was not `BLOCK` has not spent the cap, and
the next section offers it the re-review the cap still holds.

## Edits after a verdict that is not BLOCK — the unspent re-review

**A verdict that is not `BLOCK` spends neither half of the cap**, so the no-fixed-point argument
above does not reach it. A run that edits the reviewed artifact in answer to such a verdict's
findings — `MAJOR` findings the user chose to apply, or the fixer pass a command dispatches over
them — still holds the cap's one re-review, and handing off without offering it ships edited text
unreviewed for no reason the cap gives. A live `/create-prd` run is the case: `PASS WITH
RECOMMENDATIONS` with four `MAJOR` findings, two of them acceptance criteria contradicting each
other; the user applied every finding, criteria were merged and renumbered, and the text went to
its pull request with only the version line above to say the verdict predated it.

**So, before the step that follows the review gate, offer it once** — the handoff in most adopters,
step 7.5 in `/implement`, whose tests still run on either answer:

`choices: ["Re-review the edited <artifact> once (Recommended)", "Go on without it — the report says the verdict predates the edits"]`

`<artifact>` names what was reviewed — `prd.md`, `ard.md`, `specification.md`, `design.md`,
`proposal.md`, the Epic drafts, the pages written, the code change. The offer is made where all
three hold: the verdict was not `BLOCK`, the run has not re-reviewed this artifact, and an edit
answering the verdict's findings followed it. An edit of any other kind — a style
pass, a resumed verify step — stays under the reporting rule above and makes no offer.

- **Taken**, it is the cap's one re-review. Dispatch it as the command dispatches its re-review after
  a `BLOCK` — with the fixer's report as `claims_file` where the command passes one there — and
  triage it where the command triages its re-review (`finding-triage.md` § On re-review). A `BLOCK`,
  or, where the command triages, a review that **stayed blocked**, is handled as the command handles
  one after its fix cycle — its own `Review verdict BLOCK (unresolved after one fix cycle)` rule
  below, or `/implement`'s stayed-blocked stop; any other verdict, or **Proceed** at a settle prompt,
  goes on to the step that follows the review gate, as after the command's own re-review, and none
  starts a fix cycle or offers to apply its findings. The version line then names the re-review's verdict, and
  an edit after it falls back to the reporting rule above, the cap now spent.
- **Declined**, the run goes on exactly as before, and the version line says the verdict predates
  the edits.

**It never raises the cap.** A run that went through a `BLOCK` spent its re-review there, and nothing
here offers another. **Which commands it reaches is a behavioural test, as above: a command whose cap
allows a re-review, whose verdict that is not `BLOCK` leads to the handoff without one, and which can
edit the reviewed artifact on the way.** `/create-prd`, `/update-prd` and `/create-ard` offer to apply
a `MAJOR` finding; `/epics` and `/document` dispatch `doc-fixer` over them, and `/implement`
`review-fixer`; `/specify`, `/design`, `/prd-proposal` and `/brd-proposal` defer them, and edit only
where the user asks. `/vuln` and `/upgrade` re-run their review after the `PASS WITH RECOMMENDATIONS`
fixer pass, spending the re-review there, so the offer never arises; `/docs-init`, `/docs-brand` and
`/docs-audit` cap at no re-review, so there is none to offer.

## Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline

`choices: ["Provide manual fix notes (you'll be prompted)", "Defer to a follow-up issue (record in the final report)", "Override and accept the finding", "Cancel the whole run"]`

Used by the commands that fix their own reviewer's findings inline, with no delegated writer, and define no "Defer" of their own — `/create-prd`, `/update-prd`, `/create-ard`, `/design`, `/prd-proposal` and `/brd-proposal` — when the one re-review returns `BLOCK`, whether it followed a `BLOCK`'s fix cycle or was the unspent re-review offered after a verdict that was not (above); for `/prd-proposal` and `/brd-proposal`, which triage their re-review, when the review stayed blocked (`finding-triage.md` § On re-review).
Escalate per unresolved BLOCKER individually. "Manual fix notes" → take free-text from the user and apply it inline in one bounded pass, with no further re-review. "Defer" → record the finding as deferred in the run's final report. "Override" → record it there with the user's rationale. "Cancel" aborts the run.

## Review verdict BLOCK (unresolved after one fix cycle) — /document

`choices: ["Provide manual fix notes (you'll be prompted)", "Defer to a follow-up issue (record in Phase 9 report)", "Override and accept the finding", "Cancel the whole run"]`

Used in `/document` Phase 7 at either of two points: when `doc-fixer` returns `Stop condition flag: NEEDS HUMAN` — it deferred a BLOCKER as needing a human decision, so no re-review runs — or when the review stayed blocked (`finding-triage.md` § On re-review).
Escalate per unresolved BLOCKER individually.

## Review verdict BLOCK (unresolved after one fix cycle) — /epics

`choices: ["Provide manual fix notes (you'll be prompted)", "Defer to a follow-up issue (record in Phase 9 report)", "Override and accept the finding", "Cancel the whole run"]`

Used in `/epics` Phase 7 at either of two points: when `doc-fixer` returns `Stop condition flag: NEEDS HUMAN` — it deferred a BLOCKER as needing a human decision, so no re-review runs — or when the review stayed blocked (`finding-triage.md` § On re-review).
Escalate per unresolved BLOCKER individually. "Defer" means the finding goes
into an Epic-refinement note in the draft itself (appended as a
`## Refinement notes` section) in addition to the Phase 9 report.
`/specify` cites this entry on purpose and defines its own "Defer" to mirror it —
a `## Refinement notes` section in `specification.md`.
