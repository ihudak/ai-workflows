# Rationale — the evidence behind the repository's rules

Never auto-loaded. Each section holds the measured cases, refused widenings and history behind one rule in `CLAUDE.md` or `.claude/rules/`, each linking back here by a `why` reference to its matching `#<slug>` heading. Read a section before proposing to change its rule. Figures marked *(as of d5f3034b)* were true on that commit and have not been re-derived.

## description-budget

The limit is GitHub Copilot CLI's, and it rejects the **whole catalog** — one over-long blurb makes every plugin in the marketplace fail to install or update.

Claude Code enforces no limit, which is exactly why over-long blurbs kept shipping: the Claude editions grew unchecked and the Copilot edition inherited the overflow at port time. The blurb reached 2788 chars by appending one sentence per release, and was trimmed by hand three times in the Copilot edition before the check existed.

## id-grammar

A dash-separated ID has the shape of a Jira issue key, so pasting a PRD, ARD, or Epic draft into Jira auto-links it to an unrelated real ticket in any project sharing the prefix, and a wiki-style importer rewrites it into a triple-bracketed wikilink on export. <!-- vendor-token-ok: names the tracker whose autolinking is the hazard the requirement-ID grammar exists to avoid; the rule is unexplainable without it -->

The exit code alone was not enough and this was proven rather than assumed: each negative fixture carries several violating lines, so any surviving alternation holds the exit at 1, and a review deleted both `SM-C` alternations, watched `--selftest` print PASS, and then watched the degraded gate accept a live bracketed legacy counter-metric ID in a shipped reference file. `scripts/validate-catalog.py` now carries a `--selftest` of its own for the same reason.

The `id-grammar-ok` census was five such lines across five files *(as of d5f3034b)* (one accepts the legacy form as a tolerant reader — `workflows-core:ard-resolution`; the other four are the reviewers that check identifier integrity and must quote the form they reject). **The count fell from ten when the tracker-reading agent that held five of them was deleted.**

## docs-tree

Deriving every claim on a page from the thing that runs it is how the restructure found six defects the README had been asserting for releases.

No case count is stated for `check-docs.sh --selftest` because it changes every time a check gains a failure mode, and the two readings of it (cases that mutate a copy, and cases in total) differ by the unmutated-fixture pass — so a count is a claim that goes stale in the same commit that improves the gate. The `CLAUDE.md` sentence that stated it asserted 37 while the tree had 39, and was then corrected to a number the correcting commit's own diff had already moved.

### Why three shipped plugins sit outside the docs gate

`PLUGIN_RELS` names five of the catalog's eight plugins. `obsidian-llm-wiki`, `prose-style` and `acli` are outside it, and the 2026-09-29 audit responded to that by scoping the `CLAUDE.md` docs rule down to `PLUGIN_RELS` rather than widening the list — which made the instruction accurate and left the gap undecided. Deciding it: **those three ship no `plugins/<name>/docs/` tree at all**, so adding them to `PLUGIN_RELS` does not gate them, it turns the build red on the first run — check 1 has no `docs/README.md` to resolve links against and check 9 has no prose to count. Bringing them in is therefore authoring three documentation trees, which is a feature, not a one-line list edit, and it is not obviously worth it: `acli` and `prose-style` are thin single-purpose plugins whose README is genuinely the whole story, and `obsidian-llm-wiki` carries its own `CLAUDE.md` and its conventions live in `skills/_shared/`, read by the skills themselves rather than by a human browsing a docs tree.

So the list is **deliberately** five, and the rule is deliberately scoped to it. What would change that: a plugin in this group growing past what a README can carry — the trigger the `dev-workflows` restructure itself hit — at which point it gets a `docs/` tree and joins `PLUGIN_RELS` in the same change, because a tree that exists and is ungated is the one state this arrangement does not tolerate.

## number-gating

`check-docs.sh` check 9 gates seven sentences **per gated plugin**, and every one of them lives under that plugin's own tree — none is in `CLAUDE.md` or `.claude/rules/`. Some of their inventory numbers (each plugin's slash commands, subagents, skills and hooks) have a counterpart sentence in a file check 9 does gate, so a tree change turns the build red somewhere and prompts the edit in `CLAUDE.md` or the rules file; every other number in them — the documentation-page totals, `check-docs.sh`'s own check count, both marker tallies, and the caller and consumer counts — has no counterpart anywhere and is held by hand alone.

A count taken off the prose it was meant to check agrees with that prose by construction and tells nobody anything, and it is at its most convincing exactly when the finding beside it is right. **The case is `CLAUDE.md`'s own**: a branch reported a released changelog entry as claiming *eleven* states where it says *ten* and lists ten, having read a 660-character window centred on another word, met it mid-way at *"n-state gate"*, and completed it from memory — from `CLAUDE.md`, which does say eleven, about today's table. The rendering was read for the thing, the gap filled from a belief about the current tree, and nothing beside it was wrong.

## check-10

Check 10 enforces the identity quarantine; before that check existed two per-command pages linked a sibling plugin by full container URL and survived releases, found only by hand. The binding reason is **forks**: a hardcoded container URL is wrong in anyone's fork.

Check 10 matches its tokens on word boundaries, not as substrings: an unanchored match produced 38 failures on correct pages when the marketplace was renamed to a word another identifier contains, and a gate a fork must disable is a gate a fork does not have.

`getting-started.md` is the single sanctioned exception to the identity quarantine, which is why it carries the install commands inline instead of linking out.

## check-11

What check 11 excludes is stated because a reader who assumes otherwise reintroduces a shipped defect.

The widening census lives only in `workflows-core:next-phase-offer`'s scope-paragraph section. The `CLAUDE.md` sentence stating the rule used to carry its own copy of the site count, naming `/document`, `/implement`, `/specify` and `/idea`, and the reference file carried a second copy naming three of those four — both true when written, both stale within two increments as commands moved plugins, and disagreeing with each other in the meantime. The rule that would have prevented that is the one the rule now follows: re-measure in one place, cite it everywhere else.

## check-12

Check 12's parser is **bracket-matched and quote-aware, not a non-greedy regex**, and that is the whole point: `choices:\s*\[(.*?)\]` stops at a `]` inside an option string and silently skips that array, which is how the census that motivated the check missed three live arrays, two of them six-option.

Check 12's selftest pairs each failure mode with a **green** case whose option text also contains brackets — a skipping parser passes the red case and the green one for the same wrong reason, so only the pair discriminates.

## stop-routing-no-check

Matching the stop-ID condition suffix (`BRD_SPLIT_EMPTY_INVENTORY` → `PRD_GROUND_EMPTY_INVENTORY`) fires 7 times on content that is correct, because a stop legitimately names a command to warn against it (“do not run …, which stops on the same emptiness” — though both instances of exactly that wording, in `/brd-split`'s full-mode stop and `/brd-interview`'s, proved false on 2026-09-23, `/prd-ground` refusing each folder before it reads any inventory, which is the point about stop texts made again) or names it against a *different* key (`<PARENT-KEY>`); silencing those needs three hand-tuned filters, after which it fires on nothing and would have caught none of the eleven route defects that motivated it. “Names the emitting command itself” fires 11 times, all correct (`re-run '/product-workflows:brd-split <KEY>'` on a bad key). “Names no exit at all” fires 14 times, all correct (a dirty tree, a prompt leak, a schema boundary — the remedy is not a command). What the eleven actually shared is a claim about another command's *behaviour* in a state, which no file states.

## check-13

Check 13 excludes the changelog by *filename*, which is not cosmetic — the older `| grep -v '/CHANGELOG.md:'` form filtered on line content and so silently dropped from its own audit any line quoting the filter. Vendor neutrality was a hard constraint held by prose alone until it was not. The marker convention already existed with exactly one user and no enforcer.

**The narrow token set is evidence, not taste, and is recorded so the widening is not re-proposed:** the tracker names fire on 13 sites, of which 3 were real defects (the plugin README claiming `/ready` verifies a Jira status when it is artifact-anchored and reads no tracker; `docs/commands/vuln.md` twice calling `/vuln`'s optional address — a key resolved against `$SPECS_PATH` — a Jira ID) and 10 correct content, now marked. <!-- vendor-token-ok: quotes the two shipped defects check 13 was created to remove, which cannot be cited without naming the token they carried -->

Adding the git-forge names fires on **70 further sites, every one correct and none a defect** — host classification, CLI capability facts, and rules forbidding REST calls: a forge is something the plugin stands in front of and must name to behave correctly, a tracker is something it deliberately does not read. That is the same fires-only-on-correct-content result on which check 11's widening was measured and rejected twice.

**Its scope is every text file, not just markdown, and the widening was measured before it was made.** A tracker name leaks as readily through `plugin.json`'s user-visible `description` or a hook-script comment as through prose — the argument its sibling check 14 already makes for reading everything — and scoped to `*.md` it could see neither. Measured first, as this repo requires of any widening: 17 non-markdown text files under the plugin, and the widened scan fires on **none** of them, which is why this widening was taken where check 11's (which fired only on correct content) was twice rejected.

Six of the fourteen marked lines sat in `workflows-core` *(as of d5f3034b)*, so the census recipe reads `plugins` rather than one plugin. The older `| grep -v '/CHANGELOG.md:'` filter silently dropped the `CLAUDE.md` sentence describing it from its own audit, because the sentence quoted the filter.

## check-14

Check 14's token list is stored base64-encoded for one reason worth stating plainly: a denylist written in clear text would itself put the names into the tree, making the gate the only violation of the rule it enforces and every future `grep` come back dirty. It has zero live sites — the tree and its history are both clean — so it exists to keep a constraint that currently holds by discipline from quietly stopping to hold. It was added after a review mutated a docs page with those names and watched check 13 pass, which is also the correction to the belief that check 13 covered them: it never did.

## check-15

**Check 15 gates index membership** — every command must appear in `docs/README.md`, in the plugin README, and inside `docs/workflow.md`'s **mermaid diagram**, asserted separately from the page because prose below a diagram is where a command lands when someone adds it in a hurry. Check 4 proves a command has a page and check 3 proves that page is reachable from *some* page; neither proves it is findable, and a review demonstrated the gap by deleting a command from all four listing surfaces and watching the build stay green. The defect that actually shipped this way was the same shape and smaller: `/frames` reached the workflow page's prose but not its diagram, under an opening sentence promising "every command shown here".

## check-16

The loader contract is the trade the split made explicit: the shared reference corpus lives in `workflows-core`, `${CLAUDE_PLUGIN_ROOT}` resolves to the *reading* plugin, and a dependent plugin therefore reaches every reference through one argument-taking skill rather than through 28 named wrappers — one skill whose argument nothing validates unless something does.

Each of the three citation forms is load-bearing for a different file: the **bare** form is the only thing reaching `dependencies.md`, while the **plugin-root** form is the only reason `instruction-file-maintenance.md`, `handoff/code-scanner.md` and `handoff/impl-maintenance.md` are not reported as dead, since each is read by one of core's own agents by path.

No file outside core cites a core reference by path in either of the two forms that resolve to the reading plugin — the defect the loader exists to prevent, gated only over `commands/`, `agents/` and `references/` because widening it to the whole plugin fires once, on correct content, which is the result on which two earlier widenings were refused. **Scope is `commands/`, `agents/` and `references/`, measured rather than chosen**: within them the preamble relation is an **exact** match — every file that cites, carries — while a comparable number of files outside them cite a core reference and correctly carry none, so an unscoped implementation fires on every one of those on a clean tree. **All four of those figures live in `scripts/check-docs.sh`'s check-16 header and nowhere else, deliberately**: the `CLAUDE.md` sentence describing check 16 carried a second copy of them, both copies went stale, and the rule stated with check 11 — re-measure in one place, cite it everywhere else — is the one that would have prevented it — and admitting `docs/` as a *citation source* would make the reverse direction unfalsifiable, since core's own `docs/reference/references.md` enumerates every reference file by name.

Admitting `docs/` as a *citation source* would make check 16's reverse direction unfalsifiable, since core's own `docs/reference/references.md` enumerates every reference file by name.

## check-17

A ledger item (PS15) recorded a live defect: an agent self-disclosed dispatching a stray subagent mid-run, outside its own sanctioned set. Verifying *runtime* behaviour is impossible from a static script, and a check that merely asserted "the rule exists" would have passed on the very run that misbehaved: **measured first**, only 3 of the agents under `PLUGIN_RELS` carried `Task` in their tool list at all (`upgrade-executor`, `vuln-fixer`, `docs-style-checker`), and all three already carried a NEVER-dispatch rule naming their sanctioned subagent, in near-identical wording, when one of them still mis-dispatched. That is 3-for-3 today *(as of d5f3034b)* — green on the current tree — and it fires the moment a fourth agent gains `Task` without the rule, which is the realistic way this decays. **The reverse direction is asserted too**, the same call checks 8 and 11 already made for their own declared-vs-observed pairs: an agent carrying the rule but not `Task` declares a dispatch authority the harness would refuse, which is stale and misleading — verified green on the same three-file tree before it shipped.

## check-18

Each changelog's header says a section headed `— Unreleased` *"has not been published yet"*; on the default branch that is false by construction, because `claude plugin update` fetches from there and whatever is on main is what users install. The gate fires only on the push to the default branch that publishes the section, which is why the rule itself stands in `CLAUDE.md` § Hard constraints rather than only beside the gate. A gate that fired on both the red case and its green twin would be red for the life of every release branch, and a gate that blocks correct work is a gate someone disables. **The recurrence is what bought it**: commit 47050554 dated every such section on 2026-09-19 and said so in its message, and by 2026-09-22 seven more stood across four plugins, all live on origin. Matching the bare `## [Unreleased]` form would fire on correct content and nothing else, the same result on which earlier widenings of `check-docs.sh` were refused.

## check-19

The organisation's name and its internal repositories were named by the design archive and its neighbouring records across more than a hundred files until they were swept out on 2026-09-23. The denylist is encoded because a clear-text denylist would be the one violation of its own rule.

Its selftest sets a fixture token of its own, so the suite asserts the same thing in every edition, and carries the red case (a docs page) with its green twin (the same token in a `CHANGELOG.md`), the empty-config pass, the undecodable-value vacuity guard, and the untracked/ignored pair.

## check-20

Every agent reads material its author does not control, and until 2026-10-05 only `architecture-grounder`'s prompt said such material is data. The rule now sits in each agent's own body rather than in a reference the agent is pointed to, because an agent's body is its system prompt: it is in force before the agent reads anything, while a pointer depends on a Read the agent may skip. Every copy is byte-identical to `workflows-core`'s `references/untrusted-content.md` because a rule edited in some agents and not in others is how such a rule decays; the check turns a partial edit into a red build. The rule says content supplies values, never tasks, because agents legitimately act on what a repository declares — `test-baseliner` runs its test command, `upgrade-executor` and `vuln-fixer` its build, `docs-style-checker` the linter it configures — and every writer follows the conventions it documents; a rule making every file inert would break them. Notices are relayed and advisory: an agent's reply ends in the orchestrating run, so a notice no command printed would reach no one, and a notice that stopped a run would let any planted comment stop one. `GUARD_PLUGIN_RELS` reaches `prose-style`, which ships agents and dispatching commands but no `docs/` tree and so sits outside `PLUGIN_RELS`.

## mermaid-gate

The rule exists because GitHub draws each ```` ```mermaid ```` block as a diagram and shows *"Unable to render rich display"* where it does not parse.

Until `scripts/mermaid/check-mermaid.mjs` existed nothing in this repository parsed mermaid (`check-docs.sh` check 15 extracts diagrams, but only to test which commands appear in one). `plugins/product-workflows/docs/workflow.md` shipped from product-workflows 3.0.0 onward with five unquoted edge labels carrying `[BR#n]`, `[CG#n]/[DG#n]` and `[AC#n]/[FR#n]`, which mermaid reads as the start of a node shape; a person found it by opening the page.

**Its first version used a hand-rolled fence scanner, and a release review found three kinds of diagram GitHub draws that it never saw** — inside a blockquote, on a list-marker line, and after a line opening with a backtick code span — plus a four-space-indented block it wrongly rejected.

A failure is located by content because mermaid numbers its errors from text it has already rewritten, and a replay of those rewrites is never complete: the gate's second version tried one and pointed confidently at the wrong line after a decision node. The parser was calibrated against a real headless render of the repository's tree, where the two agreed block for block.

The four constructs the hand-rolled fence scanner got wrong, each a selftest fixture: `red-blockquote`, `red-list-marker`, `red-after-code-span` and `green-indented-code`.

## choices-arity

The plugin nonetheless shipped a convention saying the opposite of the harness schema (2–4 options, no authored Other), stated across the command files (*"last choice is always `"Other… (describe)"`"*), which authored duplicate options in bulk and pushed dozens of arrays past the cap — the measured figures are in `scripts/check-docs.sh`'s check-12 header, cited rather than restated in `CLAUDE.md` because two copies of one census is how they came to disagree while `workflows-core:escalation-rules` simultaneously required every array be presented verbatim — a rule the harness made unfollowable. **Two consequences outlive the cleanup** (both stated in `CLAUDE.md`). Six closed-vocabulary pickers used to protect themselves by omitting the free-text option.

The harness's schema is the authority on the arity, not the plugin's taste. A five-option array is not a long prompt — it is a tool call rejected at validation, so the run cannot present it at all. Of the four customer-authority pickers, three used to omit the free-text option and `/brd-reconcile`'s conflicting-answer picker never could; normalising a free-text answer there, never writing it through, is where D14's protection now lives. The next-phase-offer overflow rule's full menu in prose is already that file's "universal minimum". The epic-picker's directory-listing case is the one no static check can see, because a PRD with four Epics overflows an array that has no literal options to count.

Verbatim presentation binds every command of the family, not only `/document` and `/epics`. The two rules are one rule — verbatim presentation and the arity rule: an array the harness cannot render is an array no orchestrator can present verbatim, which is what the retired "last choice is always `Other… (describe)`" convention produced.

## code-handoff-citation

The code-oriented commands' not-clean-finish invariant cites `code-handoff`'s *A run that did not end clean* by heading rather than by number: it read §2.8 from 3.10.0, where that was right, until 3.12.0 inserted `### 2.7 The title and the body file` above that section and shifted every later section by one — and a stale §-citation is invisible to a §-existence sweep, because it resolves, to the wrong section.

## implement-phase-3-5

The `/implement` invariant that Phase 3.5 **names what it did not cover rather than assuming it** is the honest form of the "full test suite is verified" that invariant used to claim in `CLAUDE.md`, a claim three reachable completions denied — the three the invariant now lists.

## test-writing-requirement

Changing the tree to meet an unqualified first clause of the test-writing requirement was the alternative and was rejected: it would have to remove **both** escapes a user can choose — *"Accept the remaining failures and proceed"* and Pre-Phase 3.5's *"Skip tests for this run"* — and a gate-failed run that cannot finish is a run that leaves the implementation uncommitted, which `dev-workflows:code-handoff` §1 rule 5 exists to prevent. The completions nobody chooses are not options to remove at all: a suite that will not start is the environment's answer, not the operator's.

The silent fourth member of kind 2 — a runner that narrows its own run past the test `test-writer` just wrote — was measured on Mocha 12.0.2, which does not default `--forbid-only` from `CI` (`dev-workflows:test-baseliner` capture step 1 draws that distinction per runner, and names the runners that abort instead): with an `it.only` already committed in the repository, `CI=true npm test` printed `1 passing` and exited 0 both before the run wrote a failing spec beside it and after.

## brd-recut-readers

The sibling re-cut rule names no recipe for its readers because the recipe that stood in its `CLAUDE.md` bullet was wrong. That recipe — `grep -l unallocated plugins/product-workflows/commands/brd-*.md` — returns six files and is wrong in both directions: `/brd-proposal` is in it and reads neither §3.2 nor the re-cut (its one `§3.2` is `workflows-core:phase-handoff`'s), and `/brd-intake` is in it citing §3.2 only to say it offers no re-cut, while `/create-prd`, `/create-ard`, `/specify` and `/prd-ground` each cite `coverage-ledger-format` §3.2 by name for a disposition the re-cut leaves behind and are all outside the glob.

## addressing-fallback-totals

The "twelve files, eleven commands" totals the `workflows-core:addressing` §7 bullet in `CLAUDE.md` used to tell readers to re-derive went false twice — cutting the tracker moved them without moving the number, and by 2026-09-23 the commands citing §7 did so for other reasons — `/brd-split` for its *Adoption is additive* rule, `/release-notes` to say why it has a row — and none to reach the fallback, while `/implement`, `/vuln` and `/brd-proposal` resolved through §3 with no row — so §7 now keeps none.

A regression in the shared fallback reaches `/epics`, `/design` and `/ready`, which have nothing to do with BRDs.

## prose-style-roles

**The `CLAUDE.md` sentence stating `docs-workflows`' style-gate dependency used to call the dispatch a fallback gated on the rungs failing**, which left the ordinary case — a repo whose Vale run succeeds, where the checker runs anyway as the complementary semantic pass — unstated.

## docs-grounding-flags

`/idea` was the only implementation of `--no-docs` / `--docs <path>` until the other eight consumers were given a flag-stripping rung, four of which had none at all and would have read the flag as a positional token.

## release-notes-worthiness

`/release-notes` once read the PRD's own `relevant_for_release_notes` and stopped on an explicit `false` or `no`. Every PRD is relevant for release notes, so the field asked a question with one answer and the only value that changed anything was one nobody should write.

## recipe-returns-wrong-answer

**Match the execution phrase, not the bare name.** The recipe that stood in `CLAUDE.md`'s `specs-repo-git` paragraph was `grep -l commit-artifacts plugins/*/commands/*.md`, and it returns thirty: `/docs-serve`'s only two occurrences of that string are its rule never to run it, so the bare-name grep counts a negative mention as a caller. A recipe that returns a wrong answer is worse than a stale count, because the next reader trusts what it returns.

The `prose-formatting` consumer sentence in `CLAUDE.md` named nine consumers and missed `/prd-proposal` and `/brd-proposal`, which is why it now carries the recipe instead. The `finding-triage` consumer list omitted the two proposal commands until its grep was run against it.

## plugin-root-expansion

`${CLAUDE_PLUGIN_ROOT}`'s expansion in slash-command bodies was verified in a live run by typing the slash command and comparing the received body against the file on disk: all 33 literal tokens in `docs-workflows`'s `document.md` arrived as absolute paths. So the substitution is not general expansion: of the variables that run tested, only this one expanded (`$ARGUMENTS` is the harness's separate argument substitution, which 43 command files use *(as of dd4eed5c)*; no variable beyond those named here was tested, so nothing here claims it is the only one that expands): `${DOCS_PATH:-/workspace/docs}` and `${REPOS_PATH:-/workspace}` arrived **literal** in the same body. **`CLAUDE.md` previously claimed the opposite**, and that claim was the stated reason the `model-routing` skill exists; the claim is retired, the skill is not.

## one-key-namespace

The rule that stood in `CLAUDE.md` forbade widening a *tracker-side* check to accept three segments, on the grounds that no tracker mints a three-segment key; with no tracker read by any command, every check is folder-side and the defect family it guarded against cannot occur. **What survives is the reason, not the rule** — the autolink detector's narrowness, which the rule in `CLAUDE.md` now states.

## resolve-against-a-known-set

All five sites of 3.3.0's longest-running defect family are this: four re-stated a key grammar locally instead of citing the one `workflows-core:addressing` §1 fixes, so the copies drifted apart and a valid slice key hard-stopped a command its own recommended redirect sent it to; the fifth extracted a key out of a branch name.

Candidates come from the set, so nothing in a branch name can *become* a key and slug text can never be captured — where the obvious widened regex `[A-Z][A-Z0-9_]*(-[0-9]+)+` reads `PRODUCT-1234-2` out of `spec/PRODUCT-1234-2fa-rollout`.

A key re-derived by pattern is a key nothing in the tree ever asserted.

The worked example: `workflows-core:specs-repo-git` §3.5's `branch-key` strips the plugin prefix, then tests the remainder against the keys the run already holds — a key counting as a candidate only where the remainder is exactly it or continues with `-` or `_`, longest candidate winning.

## claim-expiry-sweep

Eleven such sentences were retired in 3.3.0, sitting in ten files — four commands, three references and three documentation pages — and the count grew from six to eleven only because successive agents walked the tree instead of trusting the list they were handed.

The eight subsections below hold the evidence for the refinements the sibling re-cut paid for, and the rounds after it — each one bought by a review finding what the sweep had already walked past, which is why the refinement list carries no count of its own.

Nothing gates such sentences: they are ordinary prose, invisible to every script in `scripts/`. A sentence that named the absence as its reason for an offer needs a new reason because the state a run leaves is usually still a real constraint on what it can honestly offer next.

### refinement-1

One sweep landed in the right paragraph, read the sentence its own term matched, found it true and moved on — leaving two sentences beside it that the same change had falsified, in a command body an agent executes in order.

### refinement-2

The two most expensive misses on that branch contained none of the swept phrases at all; one was found only by reading Phase 0 in sequence, and a later task's end-to-end read turned up five more the same way.

### refinement-3

The exclusivity probe was missing through six task reviews, and two Important findings survived to the whole-branch review because of it.

The five phrases were shown to be a starting set, not the vocabulary, on the 2026-09-22 whole-tree pass: four of six independent slices reported the same gap, and two of that pass's confirmed defects were reachable only past it. One slice's supplementary probe over the same files returned **44 further matches**; another's returned 29, one of which was the second site of a defect whose first site the five had found, so fixing on the five alone would have left a copy standing.

Three wider rounds followed (2026-09-22/23), the second finding more than the first; what they ran and found, and what round 3's reviews deferred, is in `docs/superpowers/verification/2026-09-23-exclusivity-probe-wider-vocabulary.md`.

The exclusivity probe matters because that is where a falsified claim hides when it names none of the vocabulary the change introduced.

### refinement-4

The family's shared authorities live in `workflows-core`, so a per-plugin recipe cannot see them: `workflows-core:next-phase-offer` — the file `.claude/rules/gates.md` § Check 11 names as the authority for the offer convention and for check 11's family derivation — carried a claim the re-cut falsified in both directions, and `workflows-core:phase-handoff` §3.4 kept an unqualified no-op claim the branch had corrected at four sites inside its own plugin. Both reached the final review untouched because the design's own sweep recipe was written as a grep over one plugin's commands and was structurally blind to everything else. The two root files were bought the same way, one round later: a review found that round's worst claim — the repo-root `README.md` selling a `gh auth` step for a diff-reading capability neither command has — in a file every recipe written in `CLAUDE.md` scoped past, while `CLAUDE.md` had been swept only because each ruling named it by hand.

Keeping `CHANGELOG.md` in the sweep was measured before deciding, as this repo requires of any scope change: **25 of the 67 defects review passes A22–A28 and B22–B28 recorded are sited in a changelog** — the highest-yield single surface in the tree, ahead of `docs/` at 15 and `references/` at 13 — so keeping them in fires on defective content at a higher rate than any other file class, which is the opposite of the fires-only-on-correct-content result on which check 11's widening was refused twice. Nor is the file unread by the build — check 14 reads every text file in the repository, changelogs included, and a mutation of one fires it, so "no gate opens a changelog" is false as well as beside the point. `scratchpad/r47/sweep.py`, the instrument refinement 7 names, carries no such exclusion; two of this branch's citation resolvers did copy the gates' filename filter — one wrong phase citation was sitting in a changelog while they ran, in a file neither could open.

Widening the scope is only half of it: four more of that citation's family were written into the same changelog later, and an existence check would have passed all five however wide its scope, because every one named `Phase 12` of a command that had a Phase 12. They were caught by reading the phase they cited — the axis, not the scope. **Reading the phase proves containment, not uniqueness**, and the difference is worth carrying: slicing the phase a citation names and finding the cited thing inside it falsifies a citation that is simply wrong, which is what a `Phase 12`-exists check cannot do — but it does not prove the cited thing is only there, so a phrase living in two phases passes under either citation. And where one command file carries two modes over the same phase numbers, the reader has to pick the mode before slicing: `/document`'s `# Mode A` and `# Mode B` each carry a `## Phase 3`, one reading the PRD folder and one implementing a direct edit. Picking the wrong mode reports a miss rather than a false pass, which is the safe direction — but that is a property of this failure mode, not of the check.

The scope clause binds a human or agent sweep and moves no gate's scope: `check-docs.sh` check 10 still leaves the root README alone, for its own unrelated reason. `check-id-grammar.sh` and `check-docs.sh` checks 12, 13, 16 and 19 do exclude `CHANGELOG.md` by filename, each for the one stated reason that **history keeps the retired form it shipped with** — which exempts a *quotation* and nothing else: a count, a line citation, a phase name or a claim about today's tree goes stale in an entry exactly as it does in a command, and that is most of what an entry is.

### refinement-5

The round that corrected the repo-matching claim in a `getting-started.md` page and a reference layout block swept both root files thoroughly on the *other* axis it was fixing — its commit message says so — and left the repo-root `README.md`'s two copies of the corrected claim standing, so the scope was honoured and the trigger was not, because nothing had landed. The instinct to sweep the phrasing just rewritten, taken alone, is what left a sixth copy standing.

### refinement-6

A sweep for *"no agent reads `$REPOS_PATH`"* cannot reach *"`code-scanner` resolves repositories under it"*, and one for *"there is no `pull_requests[]`"* cannot reach *"resolves the pull requests named there"*, which is how two corrections each shipped beside an uncorrected twin — one on the sibling page the corrected page links to, one in the corrected page itself.

### refinement-7

**The two measurements behind the addition-count rule disagree about whether one delimiter is enough, which is why it states a property and not a character count.** On the edit that added a wrapper alternation to the `test-notify` gate, one delimiter on each side suffices: the body `mvn test|gradlew test|…|make test` still returns 1 with `mvnw test|` inserted ahead of it, and returns 1 again on a fixture appending `|cargo test` instead — the second case being why the opening `(` is not enough on its own, since an insertion lands at either edge. On the edit that inserted five rows into `test-baseliner`'s parse table it does not, because there the delimiter bounds every row rather than the edit: the `Gradle` row alone returns 1 before and 1 after, that row with one character on each side returns 1 and 1 as well, and only the `Gradle` row *plus the `pytest` row that had followed it* falls 1 → 0.

Measured over `commands/` and `references/`, a 17-character phrase survives the wrap break about six times in seven, but an 80-character one only about one time in three — so at sentence length a line-based grep misses an occurrence more often than it finds one, and the short count it reports is plausible rather than obviously wrong, which is what makes it dangerous on exactly the files refinement 7 exists for. The reviews on this branch ran the three-step method as `scratchpad/r47/sweep.py`, a session-local script this repo does not ship and which collapses the file but not the pattern.

Reading the paragraph is not enough either, and this was bought twice in one round and once more by the round that wrote the refinement: the round that corrected `between the three` to `between the four` in `workflows-core:phase-handoff` §4.3 had read that paragraph and left the identical string standing further down the same section, in the paragraph saying the array is not reworded for a missing remote — next to a second falsified count on that same line — while scoping *"the one reader a proposal has"* on six surfaces and leaving it on two more, one of them the §1 of the very reference whose §0 it had just made the census, and the other an instruction telling the run to **print** the retired sentence; then the round that wrote refinement 7 certified it with a count of that same string taken on the parent tree, publishing **3** in a commit whose own new prose quoted it — as this rationale section still does. One wrap-insensitive count per edited string, taken after the edit rather than before it, catches every one of those; no other refinement on the list does, because each of the others tells you where to look and this one tells you when you are done.

A replacement changes text *inside* the span you counted, so the after-count falls however the query was framed, while an addition changes text only at that span's boundary and leaves the string standing inside the new form *by design*. A line-based `grep -c` over hard-wrapped files returns a number smaller than the truth with nothing to say it did. The three-step method is the rule, not any script: write your own and keep the method.

### refinement-8

**Two instances of the miss itself, one caught and one missed, which is what makes the pair evidence.** Correcting a probe's `git log` from *"the token"* to the run's whole token set falsified two changelog copies carrying the singular, and a sweep built on the **subject** found both in the same round. Narrowing a fallback's listing — so that a commit accounted for by the block recording it gets no line of its own — falsified six copies, and a sweep anchored on **one known site's wording** — the query string `that date rule dropped`, which exactly one of the five carried, the others varying enough that the round fixing them needed four different per-site strings — reached five and missed the sixth, a `docs/` page stating the same claim with a different noun. **And once prospectively, which is the one kind of evidence those two cannot supply**, both being reconstructions of misses already made: refinement 8 sent a reader to the distant copies of a claim the branch had just narrowed, and one was there — `dev-workflows`' released 2.52.0 entry still saying in the present tense what `phase-handoff` §4.1 *defines*, falsified by the count change one round earlier and sitting in a changelog nobody had reopened. **Recorded once and not added to**: a refinement that logged every later find would become a changelog of itself, and the point is made by one.

The `docs/` copies need remembering, not a wider scope: refinement 4's scope already covers those pages. The second instance above is what anchoring a sweep on a noun costs.

Refinement 8 says which strings to count; refinement 7 says when you are done counting them. **Copies vary in wording site by site, including among the ones you already hold**, which is the whole reason the query is built on the subject; and one noun across every copy is worth a little precision because a second noun is a copy the next sweep cannot see.

## sentence-context

**The risk peaks where a reader would least expect it**: of the four instances one batch's records carry, **three were introduced by fixes to earlier findings**, so the move is likeliest exactly when someone is already being careful about a rule they have just been shown to have got wrong.

**Four surfaces, one move.** A **trigger**'s extent is the worked example below. A **rationale**'s is the second. A **report condition**'s is the third: a Final Report asked for `workflows-core:phase-handoff` §4.1's outcome line *on every run*, where a producer that never offers a handoff — `/frames` having written no index, `/idea` on `status: draft`, `/implement`'s Phase 4.5 no-op, the live cases §4.1 itself lists — has no line to print and would have had to assert a decline nobody was asked about; the widened condition reached all three of §4.1's outcome states, not the two the report line was written for. And the fourth is the same move at **sentence** scale: a gloss widened to say what else an option drops asserted *save one*, a count the run cannot make where the set may be none, one or many.

**The trigger surface in full, because it is the clearest.** The array is the cheap half of such a change; the expensive half is every sentence around it that says what an option *does*, each written when only the old trigger could reach that question and free to assume whatever that trigger guaranteed. **Measured**, as an Important regression on its branch: `/brd-intake`'s same-or-new question gained a second trigger — a matched pair whose two anchors name one element without their text being the same — with no condition on the file's recorded state, while *Same requirement*'s stated effect kept the existing row whole, its anchor and its existing `text` with it. That effect was written for the unmatched-row case, where the file is recorded **unchanged** and the existing text is still what the document says; on a file Phase 2 recorded **replaced** it would have kept text the revised document no longer carries. The array was right and its options were right — the paragraph stating the effect was not, and it is the one a change that reads only the array never opens. It now turns on the file's recorded state: on a replaced file the option keeps the id, takes the returned `text` and reports the change old → new.

**The rationale surface** — `pass9a-1-report.md` counts two of that batch's last three findings as this: a **rationale** clause added for a new rule, landing beside an older sentence written when the rule was narrower, where the instruction stays correct and the reason beside it goes false. In `/brd-intake` a carve-out gained a clause saying a revised document can make the agent start returning a row it had not returned, two clauses from a standing claim that the agent is handed the same inputs on every later run; sweeping that claim found a twin one paragraph away resting a prediction on the same premise. **A third site kept the claim unqualified and was right to**, being the re-dispatch *within one run*, where nothing the agent is handed can change. On qualifying by the class: the first repair (`d2cdba1a`) named a source the customer had not revised, and it survived exactly one review round before a corrected transcription — a change to what the agent is handed with no revision behind it — falsified it; the second (`9a5599a9`) closed the class instead.

**The pointer face — one documented instance of each kind.** A `source:` ladder written from `product-workflows:brd-format` §1.1's vantage, where *this log* is the link log, was pasted into `brd/brd-figures.md`'s own layout block, where *this* re-points at the figures file — which is no log, and the opening line the instruction means is the link log's — so a writer meeting the instruction inside the block it is writing looks in the wrong file. And a clause across an em-dash read *"no later command of the route opens anything"*, where the object was the file named before the dash: read literally it is an absolute claim about every later command. **It arrived in a sentence written to repair an earlier finding** — `62c4a552`, the round-13 lead-in that gave `/brd-intake`'s one run-ending recommendation its reason where the choice is made — and the round after removed it (`19ea31f3`): the *risk peaks* claim above, counted there over the extent face alone, holds on this one too. Two instances, one check, so the pointer face stays a clause of the rule rather than a rule of its own.

**Nothing in the rule quotes `brd-intake.md` for what it says today, deliberately**: the first draft of the rule quoted it four times, and one of those quotations was falsified within a round by the batch that owns the file — the rule, in miniature, at its own expense. The instances **describe** instead, which is what that audit settled on and what keeps them checkable; the one quotation that stands is of a clause two named commits add and then remove, which `git show` settles and no later edit of that file can move.

Why the faces differ: on the extent face the sentence you wrote stays put while its neighbours go false, and it is the one you have already checked; on the pointer face the sentence you wrote is the one that goes wrong while its neighbours stay untouched, so the extent check is inert, nothing having widened and no case split existing to enumerate. The old precondition's out-of-reach paragraphs are where an assumption sits unstated precisely because nothing could once falsify it. The third-check threshold exists because three checks with their evidence will not read as one line; a face that needs a check of its own is a rule of its own.

Refinement 8 of the claim-expiry sweep fires on the same change as the extent face and covers the *other* axis — the **copies** of that claim elsewhere — so a reader who does one and not the other is half covered: the extent face is about the adjacent assumption, refinement 8 about the distant copy.

## verification-record-last

Three of the 2026-08-07 round's records went stale because the record was written first; one was falsified by its own sub-project's next commit 17 minutes later. Two of that round's wrong values propagated by copying an `expect N` from another plan.

## measure-the-population

It was learned expensively. A resolver for the pre-rename artifact filenames was triaged, measured across ten commands, specified, approved and costed at four plugins before anyone asked the one question that decided it — *how many trees hold a pre-rename artifact?* None: every finding in it was reachable only on a specs repo written before the filenames lost their keys and never renamed since, and the loop it had found between `/update-prd` and `/create-prd` needed a legacy file to exist before either command could misbehave. What shipped instead was one paragraph, because the reason the defect looked live was a promise in `workflows-core:addressing` §5 that over-reached — *"the fallback means they need never do it"* — **from which the entire resolver was derivable, and had been derived.**

Trace reachability per finding because a defect class assumed to be uniform routinely is not. The counter-case is stated so the rule is not over-applied.

## drift-risk

A refactor deleted `prd-source-resolution.md` rather than rewriting it, on the judgement that what remained was *"'resolve the folder, read `prd.md`' — two obvious lines, inlined into its two callers. Duplicating those is not the drift risk that duplicating a key grammar was."* What remained was **three** lines. The third identified the pre-rename PRD by a frontmatter field, and the commit immediately before had kept exactly that line on purpose and recorded why. Both callers lost it in the same change — one silently, one rewritten into a test for a field that had arrived in the same commit as the rename and so could never match — and the duplication then drifted into three disagreeing copies and five commands carrying none, one pair of which formed a remedy loop in which neither command could run.

## plugin-update-cli

`CLAUDE.md` named a `claude plugin reinstall` for a long time, in four places, and it does not exist: the CLI answers `error: unknown command 'reinstall'` and offers `install` and `uninstall`.

That `marketplace update` leaves installed plugins alone was measured, not assumed: after a successful `marketplace update`, `claude plugins list` still reported `docs-workflows` at `1.0.0` while the catalogue advertised `1.1.0`. **`CLAUDE.md` previously claimed the opposite** — that refreshing the marketplace "does the same thing for every plugin installed from it, in one step" — and that claim is retired. The `/plugins` interface was verified live, where it took `docs-workflows` from 1.0.0 to 1.1.0 after a CLI `marketplace update` had left it at 1.0.0.

`prose-style` 0.4.0 is the release whose checker applies the specs repository's house-style rules to `/release-notes`' draft. The `/plugins` interface is a human step, which is why `CLAUDE.md`'s update section leads with the per-plugin `update` command.

An edit that "did not land" is very often a session that has not restarted since the update.

## verify-branch-before-commit

That is not hypothetical: one session branched away from `main` between two commits of another session's run, and the second commit — a fix for a release-gating defect — landed on the unrelated feature branch, where a `git push origin main` would have left it behind.

## docs-workflows-not-a-dependency

`dev-workflows` offers `/document` and `/release-notes` as next steps and `product-workflows` offers `/release-notes`, and both cite their references in prose, but load nothing from them, so a run completes whether or not `docs-workflows` is installed.

## gate-chain-exit

A trailing `echo "EXIT=$?"` prints the **chain's** status correctly — `$?` expands before the `echo` runs, and a `;` and a newline are the same separator, so neither form changes what is printed. What it does change is the *invocation's own* exit status, which becomes 0 either way: a reader who trusts the wrapper's status instead of the printed value reads a red build as green, which one round did five times before catching it. Appending nothing and letting the chain's own status stand works too.

## model-routing-fan-out

§8.5's opt-in seeded second round has its adopters named in §8.5's own *Opt-in* paragraph, not copied into `CLAUDE.md`.

## defect-reporter-tier

**`defect-reporter` runs on the §2.1 Sonnet chain, not on Haiku (2026-10-02).** It shipped in `workflows-core` 1.8.0 on a cheap chain headed by `claude-haiku-4-5`, on the reasoning that a bugs-only pass is a cheap pass. The work is not cheap: it applies `feedback-emission` §4.1's defect predicate and its exclusions, which is judgement, and tries to confirm the wrong line in a plugin's source before it reports one. Under `--skip-feedback` it is the run's only post-session feedback capture (`emit-block` still fires on a halt), so a miss loses a defect outright, and a false report becomes a persisted entry somebody has to triage. The saving was small: one dispatch per run, at Haiku 4.5's $1 / $5 per million input / output tokens against Sonnet 5.5's $2 / $10 in `cost-prices.yaml`. `impl-maintenance`, the agent it replaces, already ran on §2.1.

**Refused, with the reason:**

- *Keeping Haiku as the chain's first row, with Sonnet behind it as the fallback.* In a family-only harness the first row of a listed family wins, so Haiku would still run on every dispatch.
- *Retiring the `haiku` alias with the chain.* An enforced model is the user's own choice, so `run-flags` §2 keeps the Haiku rows that choice resolves against.

## worktree-not-checkout

A duplicate commit on another session's branch is theirs to resolve and, where the content is identical, merges cleanly.

## verifier-blind-batched

**Blind by construction (#73).** Until 2026-10-01 `/prd-ground` Phase 7 handed `grounding-verifier` the whole finding — `evidence` and `cites` included — and relied on the agent's own rule not to read them before re-deriving. In one live run of eight dispatches, four reported unprompted that they could not comply: the evidence was already in their context. The anchoring risk is toward `agree` on exactly the failure that run found most often, an original citing something real but adjacent to the premise. A self-imposed discipline cannot remove text from a context window, so the answer is no longer sent: the derive dispatch carries the premise and the source, and the agent refuses one that carries more. A `[DG#n]`'s `class`, and a class-1 claim's `none — frame-only: <field>`, still reach the blind step: they are the question being re-derived, not its answer. **Blinding also removed the second look**, so a disputed `contradict` gets one back. An unblind verifier could weigh its own reading against the original's; a comparison that has seen the original must never revise the blind result, or the blindness is undone. In the final live smoke run an original `NOT-PROVABLE` ("orders are persisted to a database table", where persistence could live in another system) came back from the blind step `REWRITTEN`. The comparison's own notes said the blind verdict overreached, and the finding was rewritten anyway. So compare now flags a blind result whose own evidence does not establish its own verdict, never one merely because the original differs, and Phase 7 asks a second blind derivation. Agreement upholds the `contradict`; disagreement settles the finding `unprovable`. That restores the second look without anchoring it to the original.

**Batched, not weakened (#74).** One Opus dispatch per finding made a 138-claim, two-repository run cost 278 verifier dispatches in about 70 sequential batches, 200 of them `NOT-PROVABLE` and 117 from a frontend answering backend claims. Batching by repository or frame set, at most 25 to a batch and two dispatches each, makes that run about 24 dispatches, and each derive batch explores its repository once instead of once per finding.

**Refused, with the reason:**

- *A cheaper tier, or a sample, for `NOT-PROVABLE` findings.* A wrong `NOT-PROVABLE` where the code actually contradicts the premise sends a question to `/brd-interview`'s operator without the fact that settles it. Every finding keeps its own Opus re-derivation.
- *One repository-scope finding ("this repository holds no persistence layer") standing in for the findings under it.* The findings under it would never be individually re-derived. Inside one derive batch the agent may cite a fact it established for one finding for another, after checking it bears on that premise — each finding's evidence still stands alone.
- *Carrying an outcome forward from an earlier run at the same pin.* It needs a stamp saying which verifier contract the outcome was reached under, something must bump that stamp whenever the agent, `grounding-format` or the model changes, and no gate would check it; a missed bump carries a stale outcome forward silently. Batching shrinks a re-run's cost by the same factor as a first run's, and on unchanged code a re-verification is the only way the first verifier's error surfaces.
- *Two dispatches per finding instead of per batch.* It fixes #73 by doubling #74's dispatch count.
- *One dispatch with the originals sealed in a file the agent opens after deriving.* Blind by instruction again.
- *The comparison done inline by Phase 7.* Running controls and judging agreement would move to the session's model, which need not be Opus, and every result would land in the orchestrator's context.
- *Continuing the same agent with the withheld fields.* Agent continuation is not available in every harness these commands run in.
- *Checkpoint and resume across a Phase 7 stop.* With batching a lost pass is about 24 dispatches; an incomplete result is retried once in each verification pass and in each second opinion instead.

## specs-push-scope

**`commit-artifacts` pushes only its own commits, and only to a branch it may push (2026-10-05).** Until then step 5 pushed whatever branch the specs repository stood on, with `push -u origin` where it had no upstream. Three runs published something nobody had agreed to. On a branch the plugin did not create (§3.3 G2), the push carried the owner's own unpushed commits, while G2's notice said the artifacts would reach the maintainer "when that branch is merged or pushed", as if the plugin would not push it. On a direct `/implement` run from inside the specs repository, it pushed the code branch, code commit included, whatever the user had answered at the push choice. On the default branch, a user's own unpushed local commits went out with the session files. §3.4's retry had refused that last case all along: it retried only where every commit ahead of the branch's own remote ref touched §2.1 artifact paths. Step 5 now applies that rule as `push-scope`, and §3.4 cites it.

**The base is the branch's own remote ref, never the remote as a whole.** The first draft of `push-scope` counted the commits on no ref of the remote at all. A review showed that this passes a default branch that has been fast-forwarded locally onto a pushed `prd/` branch: that branch's commits are on the remote, so they did not count, and the push landed them on the remote's default branch — effectively merging an unreviewed pull request. The remote-wide form survives only where the branch has no remote ref: the local-only branch a failed `push -u` leaves behind, or one whose remote ref was pruned. **The push names its branch**, `push -u <remote> <branch>`, because a bare `git push` under `push.default=matching` pushes every matching branch, and only this one was measured; an upstream under another branch's name, which a branch cut from the default branch can inherit, counts as none, so a plugin branch is never pushed onto the default branch. Upstream presence is read with `for-each-ref`, which prints nothing where there is none, because `@{u}` exits 128 in exactly that state.

**A default branch the run stands on is caught up at run start (2026-10-05).** §3.5's B1 did nothing, and only B2 and B4, which switch to the default branch, pulled. A checkout left on the default branch while a pull request merged on the remote, or while a teammate pushed session files, then committed on a stale base: the push was rejected as non-fast-forward, and so was every later run's retry. §3.4 now fast-forwards a default branch that is strictly behind before it flushes, and §4 step 2 again before staging, so a run whose preflight stopped at a guard also commits on the remote's tip. The pull carries `--no-rebase`: a `pull.rebase` setting, common in user configs, would otherwise make it a rebase that refuses to run beside a modified artifact. A branch that has already diverged is not rebased; the rejected-push line names `pull --rebase --autostash` and the push for the user to run.

**Refused, with the reason:**

- *Pushing a branch the plugin did not create where `push-scope` passes.* That still adds a commit to somebody else's remote branch, and to any pull request open from it. §2.2 manages only the branches the plugin created, so pushing someone else's branch is theirs to do.
- *Exempting a deliverable commit whose own push failed at handoff.* Telling it from a user's commit means parsing commit messages, a pattern over free text rather than a lookup in a known set. §6's *push-scope* line names the commit and tells the user to push the branch, `next-phase-offer`'s *Push failed* clause says the same, and §3.4's retry already refused it.
- *Passing this reference's own commits whatever a `pre-commit` hook put into them.* A hook that regenerates and stages a file puts it into the pathspec commit (step 4), so on such a repository the plugin never pushes its session files: the §6 line names the file each run, and the user pushes. Two passes were tried in review and both leaked. A pass by sha also pushed whatever a hook that stages broadly (`git add -A`) swept in: the user's pending G1 path, draft or deliverable. A pass by path (a path step 2 did not list was clean, so the hook generated it) missed the original path of a staged rename, whose deletion a `git add -u` hook commits, and it let a generated index carry the names of folders the user had not committed. Each fix exposed the next, and a stranded push that is reported is the cheaper failure.
- *Rebasing the plugin's session-file commits onto a diverged default branch.* `push-scope` proves they are the plugin's own, but two writers appending to the same `implementation.md` conflict, and a rebase stopped on a conflict in a shared checkout is worse than a line naming the two commands.

## specs-push-target

**Where the session-file push goes, and what it never touches (2026-10-06).** The push-scope round filed twelve edge cases, fixed two and closed ten as outside the population it measured. At the user's request a later round reopened the ten: nine are fixed, and a protected default branch had an interim fix until the next round designed it ([session-branch](#session-branch)). These six are `workflows-core:specs-repo-git`'s:

- **`origin`, and only `origin`.** Step 5 pushed to the branch's upstream remote, else `origin`, while §3.2, §3.5 and `phase-handoff.md` read `origin` alone. On a fork whose default branch tracked the parent repository, the session files went to the parent. Now the push goes to `origin`, and where `branch.<branch>.pushRemote` or `remote.pushDefault` sends the branch elsewhere it does not push at all.
- **The session-file push never goes to a branch the remote deleted.** A branch whose same-name upstream on `origin` is gone (`ls-remote` exits 2) is not pushed, since a push recreated a renamed default branch or a merged, deleted pull-request branch. `phase-handoff.md`'s own deliverable push is outside this rule: it pushes a branch its §2.2 rule 3 reused, which a deliverable may need.
- **A refusal is final until the user says otherwise.** `[remote rejected]` in the push's `--porcelain` status records `branch.<branch>.workflowsPushRefused`, a configuration key of the reference's own, and no later run pushes that branch — whatever reason follows it, save a reason beginning with the few words git or a host gives a push a concurrent update or a server fault broke (`failed to update ref`, `unpacker error` and the like), which is retried. Before, each run retried, was refused, and left another commit on the local branch. On the default branch the record also turns session-branch mode on ([session-branch](#session-branch)).
- **Merged means merged by any of the three ways a pull request lands.** `branch-merged` adds a rebase test (`git cherry`, every line `-`) and a squash test (the branch's whole change found by patch id among the default branch's commits) to ancestry. B2 and `phase-handoff.md` §2.2 rule 3 share it.
- **A copied file is never a session file.** §2.1's shapes matched any path under the specs tree, so a customer's `implementation.md` under `brd/source/`, or a page `/idea` vendored under `attachments/` as `release-notes.md`, went into the prompt-free bookkeeping commit. The classifier now excludes `workflows-core:addressing` §2's reserved subdirectory names, all but `dev-workflows/`.
- **A commit stranded on another plugin branch is retried.** §3.4 retried only the branch the run stood on, and B4 switches away right after the flush commits.

**Measured, and the reason a protected default branch was not fixed here:** git refuses to fast-forward over a working copy of a file the incoming commits add or change, even when the copy is byte-identical, untracked or tracked (git 2.43). Most session files are appended across sessions — the feedback file per PRD, `follow-ups.md`, `implementation.md`, `resume.md` — so any design that commits them somewhere other than the checked-out default branch, while their copies stay in its tree, stalls the default branch's catch-up as soon as that commit is merged. One that commits them on the local default branch and pushes them elsewhere diverges it from the remote the first time a teammate merges. The next round designed it, as an overlay in the main checkout rather than the second checkout first proposed here ([session-branch](#session-branch)); a refused push of the default branch is still recorded, and the record now turns that mode on.

**Refused, with the reason:**

- *Pushing where git itself would push (`@{push}`).* On a fork that is the user's fork, which nothing in this reference reads, so the next run's catch-up and merge tests would not see what was pushed.
- *Anchoring the §2.1 shapes to key-shaped folder names.* `workflows-core:addressing` §4 reads a folder's kind and key off its carrier, never its name, and an `@<path>` address can name a folder of any name, so a session file in an ordinary folder such as `specifications/my-feature/` would have been left dirty forever, firing G1 on every run. The reserved-name exclusion that was taken has the same cost only for a feature folder placed beneath a directory with a reserved name, a layout `addressing` §2 does not define.
- *Recording only a hook's refusal (`… hook declined`).* That is git's own wording for a refusing hook, but GitHub's rulesets refuse with `push declined due to repository rule violations` and Azure Repos' policies with a code of their own, so an allow-list retried them on every run, the defect being fixed. A deny-list of the few transient reasons errs the other way, on a host's own transient wording, and the line says how to remove the record.
- *Deleting a branch merged by squash or rebase.* `git branch -d` cannot see such a merge and `-D` is forbidden (§1 rule 4), so B2 names the command and the user runs it.

## session-branch

**Session files on a specs repository whose default branch takes no push (2026-10-06).** Before it, every run committed its session files on the local default branch and pushed them; on a protected one the push was refused, the interim recorded the refusal and stopped retrying, and the commits piled up on a local branch that diverged from `origin` the first time a teammate merged anything, after which the catch-up stopped working. Runs that open a deliverable branch were never the problem; every run that stands on the default branch when it commits was.

**Measured (git 2.43):** `pull --ff-only` and `switch` refuse to overwrite a working copy of a file the incoming commits add or change, byte-identical or not, so a session file left in the tree blocks the catch-up the moment the commit carrying it is merged. `git merge-tree --write-tree -X ours`, with `merge=union` for the appended shapes in the repository's own `info/attributes`, merges a teammate's appended entry and the user's own without a checkout and keeps the session side of an overwritten file. A commit can be built on a branch nobody stands on through a temporary index, `commit-tree` and `update-ref` with the old value. `commit-tree` reads no `commit.gpgSign`.

**The user's decisions:** the files reach the default branch through a pull request from a per-user `session/<identity>` branch; an *overlay* in the main checkout, so no emitter or reader changes; the mode turns on automatically at the first refused push and by an opt-in key (`workflows.sessionBranch`) for a team that knows in advance; the user opens the pull request from a printed `gh pr create` line, the steps staying prompt-free; and the plumbing lives in one self-tested script, `workflows-core/scripts/session-branch.py`, whose selftest pins its classifier and identity exclusions to `specs-repo-git` §2.1 and `branch-naming` §4.

**Amended during planning:** `commit` builds on the tip the working copies came from and merges the default branch second, since writing working copies over a merged tip deleted the entries the merge brought; a new session branch starts at `merge-base HEAD <default-ref>`; `sync` defers while a dirty session file is not on the branch; the preflight ends with `put-back`; a branch that holds nothing of its own is fast-forwarded; and the overlay's paths include those where the branch differs from HEAD, without which a deleted overlay-only file was never committed as a deletion and came back.

**Amended during execution, each found by a test or a walk-through and fixed test-first:**

- *`sync` also merges `origin`'s copy of the session branch*, which a second fetch refreshes. The same identity on a second clone or machine otherwise built a branch that could never fast-forward onto the one it had pushed.
- *A remote that deleted the session branch does not stop its push.* Delete-on-merge is common, and §4 step 5's deleted-branch rule would have kept every later run's files local for good.
- *`push-scope` counts the default branch as published* and checks the branch's whole change (`<default-ref>...<session>`) for ARTIFACT paths only. Measured: listing against the session branch's own remote ref alone listed every teammate commit the merge brought in, and the first merge after the default branch moved blocked every later push. The line counts session files not yet landed, not commits, which a squash merge leaves counted.
- *The stranded commits are dropped with `lift` then `reset --keep`.* Measured: `reset --keep` alone aborts over the overlay, and a mixed `reset` leaves a teammate's newer deliverable stale in the tree.
- *A working copy of an appended shape that lost the branch's entries is union-merged* (`merge-file --union`, base `merge-base HEAD <tip>`), never written over them — a manual `lift` then a ticked follow-up did that. HEAD as the base read a stranded commit's entry as deleted on the branch; the selftest caught it.
- *`commit` and `put-back` refuse while a worktree has the session branch checked out*, and sign where the user signs.
- *A commit never takes a missing overlay for the run's own deletions.* Review round 1 found every direct `/implement` run inside the specs repository, the stranded-commit remedy and a switch back from the session branch deleting session files from it: after a `lift`, an overlay-only file is absent and a tracked one is HEAD's, which a commit read as the run's intent. A working copy that is HEAD's version, or the version this worktree was last given, is now never committed, and an absent session file is a deletion only under `dev-workflows-cost/`, the one session file a run deletes, and only where HEAD holds it or this worktree held it; any other is put back, a tracked one removed by hand included. The script records path and version per worktree. Round 2 found the record taking a stranded commit's clean file as held, a lift a lock stopped partway leaving removed files held, and a second worktree's stale copies undoing the first's relocation; round 3 found a lift stopped partway leaving present files unrecorded, so a later relocation was undone. Each path now leaves the record just before `lift` touches it, and `put-back` records a copy already in place.
- *Overwritten shapes are `-merge`.* `!merge` leaves the attribute unspecified, so `resume.md` got a line-by-line text merge that can splice two overwrites together; unset keeps the session side whole.
- *`require-on-main`'s row C′ does not count session files in the mode*, or every consumer would stop on the overlay; `/implement`'s direct run lifts again before its code commit; moves run unwrapped where no identity names the branch; a guard-ended preflight still puts back.

**Refused, with the reason:**

- *A second checkout of the session branch.* Every reader of `implementation.md`, `follow-ups.md` and the release-notes draft would learn a second root, and the operator's drafts would sit in a hidden directory.
- *Per-session files.* It changes the format every reader depends on.
- *Opening the pull request, or asking once.* These steps are prompt-free and never open one.
- *Moving the user's default branch to drop the stranded commits.* A `reset` the plugin never runs (§1 rule 4); the line names it.
- *A session branch on every repository ("always PR").* Considered twice and declined: the machinery is the same size either way, and what it adds is a standing pull request per person on every team, `implementation.md` reaching a teammate's `/document` only after that merges, and the overlay on every repository rather than the ones that need it. A team that wants the pull-request flow sets `workflows.sessionBranch`.

## entry-descriptions

**Command, agent and skill descriptions (2026-10-06).** Every installed plugin's command and skill descriptions share one listing in each session's context, and Claude Code bounds it. **Measured in the 2.1.288 binary:** the listing gets a fraction of the context window (`skillListingBudgetFraction`, default 1%), each description is cut at `skillListingMaxDescChars` (default 1,536), and "when the listing exceeds this, descriptions are shortened to fit" — every plugin's, not only the long ones. A survey agent saw ten of this family's commands listed with no description at all and another cut mid-sentence. Before this check the family's descriptions totalled 32,355 characters over 50 commands, 22,805 over 51 agents and 6,444 over 16 skills; ten command descriptions passed 1,024 (`/brd-split`'s reached 4,310), most of them narrating the procedure the body already carries.

**The rule:** a description says what the command, agent or skill does, when to use it and what it is not for, in about 500 characters (BMAD's Toolsmith canon, `6a0a068e`: a description that explains the procedure lets the model skip the body and improvise). **The thresholds are the user's** (2026-10-06): `scripts/validate-catalog.py` fails a description above 1,024 — the Agent Skills ceiling — and warns above 600. The 28 over 600 were rewritten in the same change, bringing the totals to 18,910, 21,063 and 5,875, measured on the change itself.

**Taken later the same day:** `disable-model-invocation` on every command only ever typed. It was first set aside here as a per-command audit for a gain only to prose requests; the 600 budget then left the listing over its budget, so the gain is the listing itself ([typed-only-commands](#typed-only-commands)).

## typed-only-commands

**Typed-only commands (2026-10-06).** The 600-character budget cut the waste and left the listing over its budget. **Measured in the 2.1.288 binary:** the skill listing gets the context window's token count × 4 × `skillListingBudgetFraction` (default 0.01) characters — 8,000 at a 200,000-token window, a subagent's included, and 40,000 at 1M — overridden by the `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable or the `skillListingBudgetFraction` setting, and each entry is `- <name>: ` followed by its description and its `when_to_use`. This family's descriptions came to 20,997 characters (22,801 with their names), every other installed plugin's on top. Splitting a plugin changes nothing: the budget is per session, over everything installed.

**The listing holds only what the model may invoke.** An entry whose frontmatter sets `disable-model-invocation` — read as Claude Code reads it: the YAML value, as `1`, `true`, `yes` or `on` in any case — is left out of it, and the Skill tool refuses it unless the user typed `/<name>` in that turn's message ("cannot be used with Skill tool due to disable-model-invocation. Ask the user to run /<name> themselves"), while the typed slash command still runs. Measured on a probe plugin, Claude Code 2.1.288 with Claude Haiku 4.5: the flagged command ran when typed, was absent from the listing the model quoted, and was refused through the Skill tool; its unflagged sibling was listed. **Where a command and a skill share a name** the listing holds one entry: the command's, and the Skill tool runs the command, while the command is unflagged; the skill's, and the Skill tool runs the skill, once it is flagged. Flagging such a command only swaps its entry for the skill's — for `obsidian-llm-wiki`, whose ten commands each wrap a same-named skill, that would have grown its share from 2,400 characters to 4,184 — so those commands stay unflagged.

**The rule:** every command is typed-only unless a command, agent, skill or reference file runs it through the Skill tool, written `skill: "<plugin>:<name>"` outside a fenced block (a fence is printed, never executed) — on 2026-10-06, `/document` running `/docs-profile` and `/docs-init` running `/docs-brand` — or its plugin ships a skill of the same name. `scripts/validate-catalog.py` fails a command that is none of these, and a flagged command or skill some file calls; it reads a call only in that form, which is why `/docs-init`'s Phase 5 now writes it so, and it names a plugin by its manifest, as Claude Code does. A command that used to hand the run on to a flagged one now stops and names it for the user to type — `/create-prd`'s pickers for `/update-prd` — and `session-cost.py` cuts no window at a Skill call the tool refused. The family's descriptions fell from 20,997 characters to 4,975 (22,801 to 5,555 with their names), measured on the change. **The cost:** a request in prose ("implement EPIC-1") no longer starts a family command; the user types it, and each getting-started page says so.

**Where everything else still overflows it**, the user raises the budget: `skillListingBudgetFraction` in `~/.claude/settings.json`, or `SLASH_COMMAND_TOOL_CHAR_BUDGET`. Every getting-started page and the repository README say what to set and how to check it: `claude --debug` writes `Skill listing over budget: <N> skills, <X> chars > <Y> budget` to `~/.claude/debug/latest` (measured). An estimate from plugin files alone is not enough — on the maintainer's machine it gave about 34,000 characters where that log, with `0.025` set and the pre-change versions installed, read 130 skills and 48,396 characters, Claude Code's bundled skills and the user's synced and personal skills making up the difference — so the pages give the check, not a number to trust. The budget is not reserved: a session pays only for what is listed.

**Not taken:** descriptions short enough to fit as they were — about 150 characters each, which strips the "when to use" and "not for" clauses the 600 budget keeps, and still overflows beside any other plugin. The Agent tool's list of agent descriptions (21,063 characters) is a separate list with no such budget, and is not the overflow.
