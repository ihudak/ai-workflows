---
name: frames
description: (Re)builds the frame-set index of one resolved folder. For each design/<frame-set>/ subdirectory of a BRD, PRD or Epic folder it lists the images, reads the index already there, describes the frames no row accounts for, and writes the index that references/grounding-format.md §6.1 makes mandatory and §6.2 formats. This is the recovery path for a frame set a human exported and dropped in by hand, which design-grounder otherwise refuses on sight as NO_INDEX. Indexing only — it dispatches no design-grounder, produces no [DG#n], and reaches no verifier. Writes into the resolved folder; on a completed handoff it also opens a pull request for the indexes it wrote (`references/phase-handoff.md` §2); its session artifacts are committed by `commit-artifacts`.
allowed-tools: Read Edit Write Bash Glob Grep Task Skill
---

(Re)build the frame-set indexes of: $ARGUMENTS

`design/` is a reserved subdirectory of **any** folder under `specifications/` — a BRD folder, a PRD
folder, or an Epic folder alike — and each of its immediate subdirectories is one exported frame set
(`${CLAUDE_PLUGIN_ROOT}/references/grounding-format.md` §6.1). That section makes each set's **index
mandatory, and a set without one a refusal**: `design-grounder` returns `NO_INDEX` rather than reading a
set without one, because a filename is not a reliable statement of what a frame shows.

**This command is the recovery path for that.** The obvious workflow — a human exports frames and
drops the folder in — produces a set nothing can read, and until this command the only way out was
hand-authoring an index. `/frames` looks at the frames and writes the index for every set of one
resolved folder.

**`/frames` is not design grounding, and must not be mistaken for it.** Indexing makes frames
*readable*; grounding makes them `[DG#n]` findings. This command dispatches no `design-grounder`,
produces no finding, cites no requirement id or `[CG#n]`, and never reaches `grounding-verifier`,
on either route. The one command that grounds a frame set is `/prd-ground`, now on both routes — the
BRD route's `[BR#n]` inventory and the idea route's PRD-level `[AC#n]`/`[FR#n]`/`[US#n]` inventory.

**The name.** `design/` and *frame set* are §6.1's own vocabulary, so `/frames` names what it acts on.
It is deliberately not `/design-index`: `/design` is the engineering-design workflow, and a name
adjacent to it would invite an operator who wanted an index into the wrong command.

Usage: `/frames <KEY>|@<path> [--skip-costs] [--skip-feedback] [--enforce-model=<model>]`

---

## Phase 0 — Resolve the address + model routing

**Strip the run flags first.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS` before anything else reads a token: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance, cost and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. Every later step parses only what it leaves.

0. **The environment.** `$SPECS_PATH` must resolve: every path this command reads or writes is under
   it. Unset or not a directory → apply the *Required path environment variable unset* rule in
   `${CLAUDE_PLUGIN_ROOT}/references/escalation-rules.md` and stop there. Without this, an address that
   resolves by key reaches the key-resolution stop below and is told "no folder under
   `/specifications/`" — a message naming a failure that is not the failure — and an `@<path>`
   address reaches **no** stop at all, since the path branch resolves without consulting
   `$SPECS_PATH` (`workflows-core:addressing`) and the run then fails at its first write. Neither is
   the diagnosis the operator needs, which is why this gate is taken first. (The argument-shape stops
   in this same step fire either way; they never needed `$SPECS_PATH`, so *the only reachable stop*,
   which this sentence used to say, was wrong in both directions.)

   **`/frames` defines no flags of its own — only the three universal run flags stripped above — and
   takes exactly one address.** A second non-flag token, or a token beginning with `--` that survives
   the strip above (so neither `--skip-costs`, `--skip-feedback` nor `--enforce-model`), is a stop
   rather than a silent discard:
   `FRAMES_EXTRA_ARGUMENT: /frames takes one address and no flags other than the run flags; '<token>' is neither. It indexes the frame sets of one folder per run — re-run once per folder.`
   A discarded second address is a folder the operator believes was indexed and was not.

1. **The address (mandatory).** Parse the first non-flag token and resolve it with `resolve-address`
   (`${CLAUDE_PLUGIN_ROOT}/references/addressing.md` §3) — a key, or `@<path>` to a folder or a file
   inside one. **Pass no `<KIND>`**: `design/` is reserved at every level, so a BRD folder, a PRD
   folder and an Epic folder are all valid targets and narrowing the resolution would refuse two of
   the three. Absent or malformed → stop:
   `FRAMES_NEEDS_ADDRESS: /frames needs the folder whose frame sets it should index — a key (^[A-Z][A-Z0-9_]*(-\d+)+$, e.g. ACME-77) or '@<path>' to the folder. Re-run '/workflows-core:frames <KEY>|@<path>'.`

   Handle the resolution record exactly as it comes back:
   - `status: invalid` → the same stop above, naming the token that failed the grammar.
   - `status: absent` → stop:
     `FRAMES_NO_FOLDER: no folder under $SPECS_PATH/specifications/ asserts key <KEY>. This command indexes an existing folder's frame sets and creates no folder. Re-run with '@<path>' to the folder, or with the key of one that exists.`
     **This command creates no folder**, so `absent` is a stop rather than a create.
   - `status: ambiguous` → §3 rule 5's hard stop, naming **every** match and `@<path>` as the way
     through it. Never choose between them.
   - `status: found` → carry `path`, `kind` and `key`. Report `legacy: true` once as deprecated when
     §5's fallback resolved it.

   **Then, on `status: found`, run the specs-repo preflight below, before anything below reads the
   folder.** Its run key set (`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` §3.2) is the
   resolved `key` and, on an Epic folder, the key its parent's carrier asserts, as §3.2 gives any
   Epic-scoped run — read off carrier frontmatter alone, testing no file's presence; this command
   reads nothing else above the folder. Where the record carries no key, the set is empty and the
   run keyless. The carrier test that follows reads an `@<path>` folder for its
   carrier files, and a stale plugin branch the preflight switches away from would otherwise decide
   what it finds. A run that stops above, on its address, runs no preflight.

   **First, a spec folder with no carrier.** A legacy folder whose artifacts assert no `kind:` or
   `key:` comes back `found` with `kind` empty (§5) — and, on an `@<path>`, with `key` empty too (§3
   step 1). The kind test below would call it "not a BRD, PRD or Epic folder" and send the operator to
   the folder above it, which is wrong for a spec folder written before §4's rule; and this run cannot
   index it without a kind, which the kind test below and Phase 4's cost attribution read — nor, on an
   `@<path>`, without a key, which the index's `key:`, the `frames/` branch and the commit subject all
   take. So test it here, on positive evidence only: the folder is such a spec folder where the record
   is a `<KEY>` run's with `kind` empty — §5's fallback is the only resolution that returns one, since
   §3 step 2 keeps a prefixed candidate only where it asserts the key — or, on an `@<path>` run with
   `kind` empty, where the folder holds at least one of the artifacts §5 names as a carrier — `prd.md`,
   `idea.md`, `epic.md`, `brd-link.md`, `brd/brd-inventory.md`. An `@<path>` to any other directory
   asserting nothing — a frame set not yet indexed, whose `index.md` does not exist yet, is the
   reachable one — is not this case and goes on to the kind test, whose message is the right one for
   it. Stop:
   `FRAMES_NO_CARRIER: <path> is a spec folder carrying no artifact that asserts its kind and key (it holds <the carrier files present>) — a folder written before workflows-core:addressing §4's rule, which /frames cannot index. Give it a carrier as addressing.md §5 says — add key: and its folder kind to one of those files — then re-run '/workflows-core:frames <KEY>'.`
   — and where it holds an `idea.md` and no `prd.md`, add `Or run '/product-workflows:create-prd <KEY>', whose prd.md gives it one.` — **on an `@<path>` run, only where the folder's name carries no kind prefix**: `/create-prd <KEY>` resolves by key, and a prefixed folder asserting no key is dropped by §3 step 2 and never matched by §5's fallback, so that run would resolve `absent` and create a second folder. On a `<KEY>` run the folder came back through §5's fallback and is unprefixed by construction. On a `<KEY>` run `<KEY>` is the key it was addressed by; on an `@<path>` run, which holds no key, write `<KEY>` literally, as the key the operator supplies (§3 step 1). Addressing it by its key instead is not offered as a way on, as §3 step 1 offers it to a caller that needs only the key: §5's fallback resolves such a folder with its key and still with no kind, which this step stops on the same way.
   **Where it holds none of those files** — reachable only on a `<KEY>` run, since the `@<path>` test above requires one; a folder whose PRD still carries its pre-rename name is one such — write `(it holds none of them)` in the parenthesis, and in place of `add key: and its folder kind to one of those files` write `where its PRD still carries a pre-rename name such as <KEY>_<slug>.md, rename it to prd.md and add kind: prd and key: <KEY> to it; otherwise add the carrier file its level takes, with key: and its folder kind`, which is §5's own advice for a folder written before the artifact filenames lost their keys.

   **Then test the kind, because passing no `<KIND>` removed the only guard the path branch had.**
   §3's path branch checks a supplied `<KIND>` against the folder's own and nothing else, so with none
   supplied *any* directory resolves. `kind` must be one of `brd`, `prd`, `epic`; anything else — or a
   folder asserting no `kind:` at all — is a stop:
   `FRAMES_NOT_A_SPEC_FOLDER: <path> is not a BRD, PRD or Epic folder (it asserts <kind, or 'no kind'>). A design/<frame-set>/ directory is one of the sets this command indexes, not the folder that holds them. Re-run against the folder above it — '/workflows-core:frames <KEY>' or '@<path to that folder>'.`
   **The reachable case is the documented one**: `@<path>` to a frame image resolves to its parent — the
   frame-set directory — whose `index.md` asserts `kind: frame-set-index` (§6.2's frontmatter). Without
   this gate the run would look for `design/` *inside* a frame set, report "no design/ subdirectory"
   about a directory visibly holding frames, and reach Phase 4's cost attribution on a kind
   `${CLAUDE_PLUGIN_ROOT}/references/cost-emission.md` declares unreachable precisely because this
   refusal exists.

2. **Resolve model routing.** Invoke the `model-routing` skill (Skill tool,
   `skill: "workflows-core:model-routing"`), then record:
   ```yaml
   model_routing:
     classification: MODERATE          # a bounded read plus a mechanical reconciliation
     reason: <one-line>
     current_model: <the model this orchestrator is running under>
     enforced_model: <run_flags.enforced_model, or omit>   # §10: when set, every dispatched-step *_model below equals it (inline authoring_model / implementation_model keep the session model) and routing: bypassed
     detection_model: <§2.1 Sonnet chain: claude-sonnet-5, fallback claude-sonnet-4-6/4-5>   # frame-describer
     opus_available: <true if a §2 Opus model resolved, else false>
     notes: <any §2/§2.1 fallback or degradation>
   ```
   `frame-describer` runs on `detection_model` — describing a picture is detection work, not
   judgement. **No Opus is required anywhere in this command** and no reviewer gates it: there is no
   artifact of opinion here to review. If no model of the detection chain resolves, degrade to the
   best available and record it in `notes` and the Final report.

**Specs-repo preflight** — run at the end of step 1's resolution, on `status: found`, with the run key
set step 1 fixes, before step 1's carrier and kind tests read the folder. Cite `${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` and execute its
`specs-preflight` entry point (§3) inline: flush any leftover session artifacts from an earlier run,
retry an artifact commit that failed to push, and settle the branch. Prompt-free and silent when the
specs repo is clean and on its default branch. If a guard fires, emit its §5 notice; if it returns
`specs_git: blocked` (§3.3 G0), carry that flag for the whole run — the terminal `commit-artifacts`
step skips on it.

---

## Phase 1 — Enumerate the frame sets

1. **List the immediate subdirectories of `<folder>/design/`.** Each one is a frame set. Do not
   recurse: §6.1 fixes one set per *immediate* subdirectory, and a directory nested deeper is part of
   whatever that set holds, not a set of its own.

2. **No `design/` at all, or a `design/` holding no subdirectory → report and stop, having created
   nothing.** This is a clean outcome, not a failure and not a stop worth a hard-stop token:
   ```
   frame sets: none — <folder> has no design/ subdirectory (nothing created)
   ```
   or `… — <folder>/design/ holds no frame set (nothing created)`.
   **Create no `design/`, create no
   frame-set directory, and write no index.** §6.2 step 6 forbids writing an index where the listing
   is empty, and an empty `design/<frame-set>/` is a directory `design-grounder` would open for
   nothing. Skip Phases 2 and 3 entirely and go to Phase 4 — the run still records its own spend.

2a. **Images sitting directly in `design/` are reported wherever they are found — not only when
   there is no frame set.** A set is a subdirectory of `design/`, so a frame dropped into `design/`
   itself is indexed by nothing. Say so and name the fix:
   `design/: N images sit directly in design/ and are in no frame set; a set is a subdirectory. Move them into design/<set-name>/ and re-run.`
   **This test is deliberately outside item 2.** Nesting it there — its first home — made it
   unreachable in the state that produces it most often: `/idea` creates `design/idea-sources/` for
   any idea-route folder whose source linked a readable image, so `design/` very commonly holds a
   subdirectory *and* loose frames an operator exported later. Item 2 does not fire then, and the
   loose frames went unmentioned while the run reported success on the sets it did find. A guard for
   a near-miss has to fire in the mixed state or it does not fire at all.

3. **List each set's images** — every file carrying one of the frame extensions §6.2 step 1 fixes.
   The set is that section's, not this command's: two writers of one index listing by two vocabularies
   would each drop the other's rows as images that are no longer there. This listing is §6.2 step 1
   and it is the whole truth about what the set holds; `index.md` is not a frame and is never a row.
   A set whose listing is **empty** is reported and skipped — nothing is written into it and nothing
   is removed from it, exactly as §6.2 step 6 requires.

   **Hold every file in the set that is NOT in that extension set, and name each once.** §6.2 step 1
   requires it of every writer — *"a writer that finds one names it once in its own report so it is
   visibly not indexed rather than invisibly missing"* — and this run is the writer. It gets no row
   and is never described; it is reported so an operator who exported a `.fig`, a `.pdf` or a `.sketch`
   into a set learns it will never be grounded, instead of inferring it from a row count. `index.md`
   itself is excluded: it is this format's own file, not an un-indexed frame.

4. **Read the index already there, where there is one — including one under another name.** `index.md` is the name every writer writes
   (§6.2), and this command writes that name. But an index found under **another** name — a manifest, a captions file, a README —
   is **read and adopted**, not merely reported: `grounding-format.md` §6.1 has always let a *reader* accept whatever name a
   frame-set convention used, and this command is the participant that had been declining that permission. Adopt every row whose
   image resolves to a file in this set's own listing, preserving its description **verbatim** — the same rule §6.2 step 2 applies
   to a row in a real `index.md`. Report, and do not adopt, a row naming an image the listing does not hold: the frame it describes
   is not in this set. If the file cannot be parsed into rows at all, report that and adopt nothing from it — **never a partial guess**.

   **The original is left byte-for-byte alone either way.** This command did not fix that file's shape and will not rewrite it; it
   writes `index.md` beside it and the report names both, so the operator can retire the older one deliberately. What changed is
   only that the descriptions in it are no longer thrown away — a set that already carried a hand-written manifest used to come out
   of an indexing run *worse*, with every frame re-emitted as `_no description on record_`.

---

## Phase 2 — Describe and index, one set at a time

**One authority, executed inline and restated nowhere.** Cite
`${CLAUDE_PLUGIN_ROOT}/references/grounding-format.md` §6.2 and run its six reconciliation steps for
each set. That section owns the filename, the frontmatter, the table shape, the `Linked from`
semantics, and every step below that is not about *this* command's cap. **It is the same contract
`/idea` Phase 4.5 follows** — deliberately, because two writers reconciling one directory by two sets
of rules is how a set ends up holding an index neither of them would have written.

For each frame set, in directory order:

1. **Reconcile the listing against the index in memory first.** Every frame in Phase 1's listing falls
   into exactly one of:
   - **has a row whose description is real** → §6.2 step 2 preserves it **verbatim** — the frame, its
     `Linked from`, and its description exactly as they stand. This command never rewrites a
     description it did not produce, and never re-describes a frame that already has a row in
     `index.md` — nor one whose row was **adopted** from an index under another name (step 4), since
     an adopted description is preserved on exactly the same terms as one already in `index.md`.
   - **has a row whose description is the literal `_no description on record_`** → §6.2 step 2's one
     exception. That row holds no description to preserve and this command *can* obtain one, so the
     frame joins the describe set. **This is what makes a capped run recoverable**, and it is why the
     placeholder is a marker rather than an answer.
   - **has a row whose description is `_could not be read: <reason>_`** → **preserved, and not
     retried.** The describer already looked at this file and could not read it, so a re-run
     reproduces the identical failure while spending budget a reachable frame would have used, and the
     set never converges — three oversized exports once rejoined the describe set on every run,
     forever. Clearing it is the operator's move and the report names it: fix the file, delete the
     row, and the next run treats the frame as having no row at all.
   - **has no row at all** → the frame joins the describe set (§6.2 step 3), and the row this
     command appends for it reads `—` in *Linked from*: it holds no link for any frame.

   A row whose image is **not** in the listing is dropped (§6.2 step 5) and reported. Nothing is
   restored and nothing is re-copied: this command reconciles an index with a directory and never
   manages the directory. **It deletes no image, ever.**

2. **Apply the cap — 40 frames described per run, counted across every set the run touches.**
   Consume the budget set by set in directory order, and within a set in listing order.

   **Why a cap of 40, when `/idea` reads every image its operator allows.** `/idea` reads images
   only incidentally, inside a command whose subject is a brief: it asks the operator before reading
   past six, and reads what they allow in `figure-reader` dispatches of at most ten images each, so
   no one context holds more than ten. This command is invoked precisely *to* index and asks nothing
   before it reads, so stopping at six would stop it on the first real export it met; and it
   describes each set in one `frame-describer` dispatch, so a cap is what bounds a context here.
   Forty is the size of a feature's screen flow as humans actually export one, and it is a bound on
   the most context-expensive read this plugin does: forty images in one `frame-describer` context,
   and none of them in this orchestrator's.

   **What happens when it bites.** Every frame past the budget stays in the listing and still gets a
   row — §6.2 step 4's `—` and the literal `_no description on record_` — with `cap` as its reason in
   the report. **The index is still valid and complete**: §6.2 writes the file once, after every row
   is resolved, so a capped run leaves a full index rather than a half-written one, and every frame
   in the set is named in it. The run reports the cap and names the re-run that finishes the job.
   Because step 1 treats that placeholder as a row to be filled rather than preserved, each re-run
   describes up to 40 more and the set converges — 100 frames is three runs, and no run ever leaves
   the set unreadable in between.

3. **Describe the frames in this set's describe set — where there is one.** An **empty** describe set
   dispatches nothing: every frame already carries a real description, or the cap was spent before this
   set. That is the ordinary shape of a re-run over a complete index and of every set after the one the
   cap fell in, and `frame-describer` refuses an empty `frames` list with `INPUT_MISSING` — so
   dispatching would spend an agent to manufacture a failure status, and the report would name a set
   that "stopped" while being complete and correct. Skip to step 4 and write the index from the rows
   already resolved.

   Otherwise dispatch once per set, never per frame:

   → Agent (subagent_type: "workflows-core:frame-describer", model: `<detection_model — §2.1 Sonnet chain>`):
     > "Describe these frames and return the structured result:
     >
     > frame_set_dir: [absolute path of this design/<frame-set>/ directory]
     > frames:        [the basenames in this set's describe set, in listing order]
   "

   Wait for the result. On `status: INPUT_MISSING` or `FRAME_SET_MISSING`, describe nothing for this
   set, give **every** frame in its describe set the `_no description on record_` row with that status
   as the reason, and carry on to the next set — a set this command could not look at is still a set
   whose index must state what it holds. On `OK`, pair `frames[]` with the listing **by basename** and
   take each `description` **verbatim** into that frame's row. Its *Linked from* is `—` — this command
   holds no link for any frame, so a row it appends reads `—` and a placeholder row it fills keeps
   the `—` it had. An entry with `read: false` gets the placeholder row and its `reason` (`missing`,
   `not_an_image`, `unreadable`, `not_a_frame`) is reported. **Which placeholder
   that row carries follows §6.2 step 4's test — whether a re-run would do anything different, and
   nothing else.** `unreadable` and `not_an_image` are facts about the **bytes** — the agent opened the
   file, or tried to — so the row reads `_could not be read: <reason>_` and is not retried.
   Everything else takes `_no description on record_` and the next run tries again: `missing` is a
   disagreement between this run's own listing and what the describer found; the two whole-set
   statuses are facts about the dispatch; and **`not_a_frame` is a fact about the *entry*, not the
   file** — `frame-describer` returns it for a name carrying a path separator where a basename was
   expected, having never opened anything. This command passes basenames, so it should not occur at
   all; if it does, the bug is in the dispatch and a corrected re-run is exactly what should retry
   it.

   **Never write a description this command produced itself.** `grounding-format.md` §6.1's index rule
   exists to forbid exactly the inference a filename invites, and this orchestrator never sees the
   image — which is the point of dispatching an agent rather than reading here.

4. **Write the index** per §6.2 step 6 — once, whole, after every row is resolved. `key` is the
   resolved folder's own key as Phase 0 read it (never parsed from a directory name);
   `frame_set` is this directory's own name; `written_by` is `/frames`, including on a set `/idea`
   wrote first — that field records who last wrote the file and nothing keys off it.

5. **Nothing here is fatal.** A set that could not be described, an index that could not be written
   (permissions, a full disk), a frame that would not open — each is recorded against that set and the
   run moves to the next one. A failure in one set never abandons the sets after it, and never fails
   the run.

Hold, per set: the index path **as a repo-relative path** — that is the form `deliverable_paths`
takes in Phase 3, and `handoff-to-main` §2.3 matches it against `git status --porcelain -z` output, which
is repo-relative; an absolute path there matches nothing and stages nothing. §2.3 step 4 names it in
§4.1's *declaration unaccounted for* clause, so that failure is reported rather than silent — but the
index still does not reach the default branch, which is the reason to hold the repo-relative form. Hold also how
many rows it now holds, how many this run added, how many it
preserved, how many carry each placeholder and why — `_no description on record_` (`cap`, `missing`,
`not_a_frame`, or an agent status) and `_could not be read: <reason>_` (`unreadable`,
`not_an_image`), the second group named frame by frame with its remedy since no re-run clears it —
and every row dropped because its image is gone.
Hold also **each file in the set that is not a frame at all** (Phase 1 step 3), which carries no row
and must still be named, and **any `notes` the describer returned** — a frame illegible at the
resolution supplied, or a set that is plainly several unrelated exports. `frame-describer` documents
`notes` as output and nothing read it, so the observation it exists to surface was discarded; it is
reported, never acted on, exactly as `/prd-ground` consumes `design-grounder`'s. Carry the literal list of index paths written into Phase 3.

**The bookkeeping steps do not stage any of this.**
`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` §2.1 classifies `design/**` as OTHER, so
`commit-artifacts` never touches an index. They are deliverables, and they reach the default branch
only through Phase 3's handoff.

---

## Phase 3 — Handoff

**Only where at least one index was written.** A run that wrote none — no `design/`, no set, every
set empty — has no deliverable, offers no handoff, and says so; offering one would name a pull
request for nothing.

Report what each set now holds, then present
`${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md` §4.3's consent choice verbatim — the **advisory** variant (§4.0), whose second option says no command stops on this and that what reads it reads your working copy. **Nothing gates a frame-set index, but something reads one**: `product-workflows:design-grounder` refuses to run on a frame set holding no index at all, and `product-workflows:grounding-verifier` returns `NO_INDEX`/`STALE_INDEX` on one — both from the working tree, neither off a ref. The **gated** class is wrong outright — §3.4 names no row for a frame-set index, so neither of its two arrays applies, and its **stopping** one would promise a refusal no consumer makes — and the **unread** variant — which this phase presented until §4.0's register was verified against the tree — told the operator to ignore a file `/prd-ground` refuses a frame set without, three lines above a paragraph of this same phase saying the set stays `NO_INDEX` for everybody else. That contradiction is the reason §4.3 asks a producer to name its reader rather than infer the class from the absence of a §3.4 row. On the first
option, execute `handoff-to-main` (§2) with all five of its §2.9 inputs: `prefix: frames`;
`feature_folder` = the folder Phase 0 resolved; `deliverable_paths` = **every `index.md` this run
wrote, one literal path each, repo-relative as Phase 2 held them**; `title: <KEY> Index design frame sets`; and
`body_facts` = each set with its row count, how many rows this run added, how many carry no
description on record and why, and every row dropped.

**The indexes are named literally, one path each — never a directory and never a glob.** §2.3 stages
by enumeration and classifies everything it was not handed as OTHER, so an index left out of this
list is one that never reaches the default branch: the set stays `NO_INDEX` for everybody but the
operator who ran this command, which is the exact state the run set out to repair. Pass the list
Phase 2 held, unchanged.

**Decline and the indexes are written but on no ref.** They are still on disk, and a grounding pass
reads a frame set from the working tree rather than off a ref, so a declined handoff is an unshared
repair rather than a blocked one. Say that, and say one thing more, because it is not free: each
index is an OTHER path under `design/**`, so on the next run of any command sharing this repo
`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` §3.3's **G1** matches — the preflight ends there
at advisory severity listing the paths, and §3.4's leftover flush and §3.5's branch disposition are
suppressed for the rest of that session. G1 does not set `specs_git: blocked`, so nothing is lost or
halted, and the suppression repeats until the paths are committed or the handoff is taken. Beyond
those two facts, neither more nor less — and name no command that could not run against the folder
this run actually resolved.

**No downstream gate reads these files, so no offer here carries a `<merge-clause>`**, and a declined
run takes §4.1's **advisory** `<next-phase-clause>` — the one written for an artifact a command reads
without gating on it. **The two halves of that sentence are different claims and only the first is
about gates**: no `require-on-main` targets a frame-set index, *and* `product-workflows:design-grounder`
refuses to reconcile a frame set that has none. §4.3 requires this clause to agree with the array the
same phase presented minutes earlier, and it did not: the array was moved to advisory when §4.0's
register was corrected, and this clause was left saying nothing reads the file — the exact
self-contradiction §4.3 exists to forbid, inside the command the correction was made for. Nothing runs
`require-on-main` on a frame-set index (`${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md` §3.4's
table names none), and `${CLAUDE_PLUGIN_ROOT}/references/next-phase-offer.md`'s rule attaches the
clause to an offer naming a gate this run's own output feeds. There is none. Recommend nothing
unconditional either: this command sits beside the pipeline rather than inside it, and what to run
next is a question about the folder, not about the index.

### Context hygiene

No `resume.md` is written for `/frames` (`${CLAUDE_PLUGIN_ROOT}/references/session-hygiene.md` §1 skip
list — indexing is not a pipeline phase, so there is nothing to resume; the durable state is the index
on disk and the pull request).

A `/frames` run over a large set carries forty descriptions and nothing else it needs to keep. Going
on to other work in this session? → run **`/compact`**; every index is already on disk. Guidance only —
see `${CLAUDE_PLUGIN_ROOT}/references/session-hygiene.md`.

---

## Phase 4 — Session maintenance, feedback & cost

Terminal phase — runs after Phase 3, NEVER interrupts an earlier phase, and **runs on every path that reached Phase 1**,
including the run that found no `design/` at all.

**Capture-at-block invariant.** If an EARLIER phase **halts on a plugin / skill / command / reference
gap** (a capability the run needed but the plugin lacked), `emit-block` (per
`${CLAUDE_PLUGIN_ROOT}/references/feedback-emission.md`) at that halt **before** escalating. NEVER
`emit-block` for an environment / user halt (an address that resolves to nothing, a cancellation). **A halt on a missing container tool always fires it:** a halt because the container lacks a tool the run needs is a container defect rather than an environment or user halt, so `emit-block` records it with `category: environment-defect` (the same reference's `emit-block` predicate).

**Under `run_flags.skip_feedback`** (`workflows-core:run-flags` §4), dispatch `workflows-core:defect-reporter` instead of `impl-maintenance` in step 1, with the same handoff plus `Plugin root: ${CLAUDE_PLUGIN_ROOT}` (literal — it expands in command bodies to this command's own plugin location), and `model: <§2.2 cheap chain, or run_flags.enforced_model>`; if it returns at least one defect, persist them with `emit-bugs` (`Skill(skill: "workflows-core:reference", args: "feedback-emission emit-bugs")`) in place of `emit-auto`, otherwise load nothing. Surface `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in place of step 2's persisted-path line. Capture-at-block (`emit-block`) is unaffected by the flag.

1. **Invoke `impl-maintenance`** (subagent_type: "workflows-core:impl-maintenance", model: `<detection_model — §2.1 Sonnet chain>`):
   > "Analyse this session and return a Lessons Learned report.
   >
   > Session handoff:
   > - Command run: /frames
   > - What was done: [the folder resolved, how many frame sets, how many frames described, how many indexes written]
   > - Key events: [frames that could not be read, sets skipped, the cap biting, an index found under another name, rows dropped — or 'none']
   > - Workarounds used: [manual steps not automated by the workflow — or 'none']
   > - Review verdict: N/A (no reviewer in /frames)
   > - Test result: N/A (no tests in /frames)
   > - Project root: [the resolved folder]"
2. **Persist plugin feedback (automatic).** Cite
   `${CLAUDE_PLUGIN_ROOT}/references/feedback-emission.md` and call its `emit-auto` entry point (§6)
   with the Lessons Learned report, `command: /frames`, `key` = the resolved folder's key, the run's
   `source`, and `plugin_version` (read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`).
   Surface the persisted path (or "no plugin-facing signal — nothing persisted").
3. **Session cost (ALWAYS runs).** **Under `run_flags.skip_costs`**, do not call `emit-cost` and do not load `cost-emission`: execute `skip-cost` (`Skill(skill: "workflows-core:reference", args: "run-flags skip-cost")`) instead, which advances the checkpoint and drops any deferred record, and surface `Session cost: skipped (--skip-costs)` (or `(WORKFLOWS_SKIP_COSTS)`). The terminal `commit-artifacts` step below runs unchanged either way. Otherwise, cite `${CLAUDE_PLUGIN_ROOT}/references/cost-emission.md` and call
   its `emit-cost` entry point with `command: /frames`, `phase: inferred`, `role: inferred`, `key` =
   the resolved folder's key, the run's `source`, and `plugin_version`. §7's discriminator is the
   resolved folder's own `kind`, which Phase 0 already read: `brd` attributes the run to
   `brd-to-prd`/`pm`, `prd` and `epic` to `prd-creation`/`pm`. A BRD-route slice is a `PRD-` folder
   asserting `brd`, so its frame set is `brd-to-prd`; an Epic folder under it asserts `epic`, and
   is `prd-creation`. The key is always present on any path that reaches here — Phase 0's stops (`FRAMES_NEEDS_ADDRESS`, `FRAMES_EXTRA_ARGUMENT`, `FRAMES_NO_FOLDER`, `FRAMES_NO_CARRIER`, `FRAMES_NOT_A_SPEC_FOLDER`, an ambiguous key, an unset `SPECS_PATH`) all stop Phase 0 before it has a spec folder whose kind and key it can index — `FRAMES_NO_CARRIER` among them, taken on a folder asserting neither — and this phase runs after them, which is why its scope is stated as *every path that reached Phase 1* rather than every path. This
   command refuses to run without a resolved folder — so the entry lands on the keyed tier and never
   on the pending ladder (§9), which **advances the chained checkpoint** (§3); surface the persisted
   path (or the report-only notice).
4. **Commit session artifacts (terminal).** Cite `${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md`
   and execute its `commit-artifacts` entry point (§4) inline — the LAST action of the run. It stages
   ONLY the §2.1 bounded artifact paths inside `$SPECS_PATH`, commits `<KEY> Add dev-workflows session
   artifacts (/frames)` and pushes. It NEVER touches a code/docs repo or the current working
   directory, where it is not the specs repository; NEVER force-pushes; NEVER fails the run; and skips entirely when the run carries
   `specs_git: blocked` (§3.3 G0), re-emitting that notice. Hold its §6 outcome line for the Final
   report.

ADDITIVE — this phase NEVER fails the run, NEVER commits a deliverable (each `index.md` is handed off
separately, before this phase, via `${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md` §2, behind
Phase 3's §4.3 consent choice), and NEVER writes into a code/docs repo or the current working
directory, where it is not the specs repository; no user name is ever written.

---

## Final report

Report: the resolved folder with its `kind` and `key`, and whether §5's legacy fallback resolved it;
**the frame sets found**, or plainly that there were none and that nothing was created — naming no
directory this run did not actually create. Then, per set: the index path and whether it was
written, created, or rewritten; how many rows it now holds; how many rows this run **added**, how
many it **preserved verbatim**, and how many carry each of the two placeholders — `_no description
on record_` with its reason (`cap`, `missing`, `not_a_frame`, or the agent status that stopped the
set), which the next run retries; and `_could not be read: <reason>_` (`unreadable`,
`not_an_image`), which it will not. **Name every frame in that second group individually, with the remedy**, because
this is the one group no re-run clears on its own: fix the file — an oversized export re-exported
smaller, a mislabelled one taken out of the set — then delete that row from `index.md`, after which
the frame has no row and the next run describes it. Reporting it as a count would leave the operator
knowing something is stuck without knowing which file or what to do; every row **dropped** because
its image is no longer in the directory; a set
skipped for holding no image; **each file in the set that is not a frame**, named once so it is
visibly not indexed rather than invisibly missing (§6.2 step 1); and an index found under a name
other than `index.md`, with the fact that `index.md` now sits beside it — and **how many of its rows were adopted, how many were not, and why not** (an image the set's listing does not hold, or a file that could not be parsed into rows at all). An operator retiring the older file needs to know what carried across before deleting it. Report, too, any images
sitting directly in `design/` outside every set (Phase 1 step 2a).

**Report the cap explicitly whenever it bit** — how many frames were described, how many were left,
and that `/workflows-core:frames <the same address>` describes the next 40 and converges. **Convergence
here is over the frames a re-run can reach**: a `_could not be read_` row is excluded from that count
and from the promise, since it is reported separately with its own remedy and no number of re-runs
clears it. State the
count even when it did not bite ("all N frames described; the 40-frame cap did not apply"), because
the absence of a truncation notice is only informative once the run is known to print one.

Also report: the resolved model routing (with any degradation), including `Model routing: bypassed — enforced <id> (flag|env)` in place of the degradation line wherever `run_flags.enforced_model` is set; the `Run flags: …` line, repeated, whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6); the feedback path (or, under `--skip-feedback`, the `Session feedback: …` line); the cost path (or
the report-only notice, or, under `--skip-costs`, the `Session cost: …` line); the `Specs repo:` outcome line from `commit-artifacts`
(`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` §6), with any guard notice repeated in full;
and the `Phase handoff:` outcome line for whichever of the two outcomes Phase 3's offer reached —
`handoff-to-main`'s own line on the first option, and §4.1's *Declined by the user* line on either
other, that one already saying the deliverable is written and not on the default branch
(`${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md` §4.1, exactly one line per handoff
offered; §4.3 has the producer emit it on either declining option). **A run that wrote no index prints
neither**: Phase 3 offers no handoff there, so nothing was declined and §4.1 has no row for it.

**Say what this run did not do.** It reconciled no frame against any requirement, produced no
`[DG#n]`, and dispatched no `design-grounder` — the indexes make these sets *readable*, which is a
precondition of design grounding and not design grounding itself.
