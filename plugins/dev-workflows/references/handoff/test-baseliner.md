# test-baseliner Handoff Format

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

## Input

```markdown
## Test Baseline Request
repo: /absolute/path/to/repo   # the project root, and the scan root in BOTH modes.
                               # Callers send it under their own label — `Project root:`
                               # throughout this plugin — and it is this field either way.
                               # Required for `mode: verify`; on `mode: capture` a caller
                               # may omit it and the scan falls back to the working
                               # directory, which no shipped caller relies on.
                               # The root sent on the capture call is sent again on every
                               # verify call against that baseline — and where a capture
                               # omitted it, the verify sends that same working directory —
                               # or the two runs have nothing to pair: `### Suites` records
                               # each marker as a path relative to THIS root, so the root is
                               # an operand of what verify PAIRS on — the half nothing
                               # downstream repairs, since verify step 5 rewrites a moved
                               # prefix onto the suite step 2 paired it with, and two roots
                               # move every marker path at once, which is more than step 2's
                               # one-of-each fallback can pair where a framework names more
                               # than one suite. So two roots report a tree that did not
                               # change as every suite moved, and — where a framework names
                               # more than one detected suite — every identifier of it as
                               # missing, with that rewrite and without it alike
                               # (agents/test-baseliner.md capture step 1, measured there).
mode: capture              # capture | verify
command_hint: "./mvnw test -q"   # optional; one or more commands. Detection still runs —
                                 # the hint narrows what is RUN, never what is DETECTED.
                                 # Omitted ⇒ every detected suite runs — and where nothing
                                 # is detected, the test command the repository declares
                                 # for itself (its CI file, else CONTRIBUTING.md/README.md),
                                 # read once at capture as `declared#<n>` suites and replayed
                                 # at verify from the baseline's own rows, so a caller sends
                                 # nothing for it (capture step 1's last rule). A hint sent on the
                                 # capture call is sent again on every verify call against
                                 # that baseline — the same commands IN THE SAME ORDER —
                                 # or the two runs have nothing to pair: a command that
                                 # matches no detected suite is a suite whose `### Suites`
                                 # marker is `command_hint#<n>` for its position in the
                                 # hint, which is what tells two such suites apart and
                                 # what verify pairs them by.
                                 # A hinted command runs in the directory of the detected
                                 # suite it matches, or at the scan root (`repo:`, or the
                                 # working directory where a capture call omits it) where
                                 # it matches none — every other suite runs where capture
                                 # step 2's four sources put it, not at the scan root by
                                 # default, and that holds in BOTH modes
                                 # (agents/test-baseliner.md capture step 2, verify step 3).
baseline: |                # required for mode: verify — the full `## Test Baseline` block
  ## Test Baseline         # from the capture call, verbatim, `### Suites` included
  - **Mode**: capture
  …
```

**Hand verify the whole block, not a re-keyed digest of it.** Its `### Suites` rows are
what verify pairs the current run against; they are what separates a suite the
baseline recorded `OK` and that aborts now (a regression — the change is the only thing
that moved) from one that could not run at either end (`PARTIAL` — a fact about the
environment); and they are what verify step 5 reads the baseline's **own** identifier
prefixes off before it rewrites them onto this run's, since a framework's prefix there is
`[<Framework>] ` or `[<Framework> <that row's marker value>] ` according to how many rows
that framework has in this very section. A caller that passes counts alone leaves verify unable
to tell those apart, and a caller that passes the two test lists without `### Suites`
leaves it unable to rewrite them at all.

**No `model_routing:` block is passed.** The caller pins this agent's tier with `model:` on the dispatch, and nothing in the agent reads a field of that block.

## Output — capture mode

The agent returns a Markdown block, not YAML — this is the exact structure
(see `agents/test-baseliner.md` "Mode: capture" step 5):

```markdown
## Test Baseline
- **Mode**: capture
- **Status**: OK                 <!-- OK | PARTIAL | RUN_FAILED | COMMAND_NOT_FOUND | NO_TESTS -->
- **Framework**: Maven
- **Command**: `./mvnw test -q`
- **Total**: 47 | **Passing**: 47 | **Failing**: 0 | **Skipped**: 0

### Pre-existing failures
none

### Passing tests
[Maven] com.example.FooTest#testCreate
[Maven] com.example.BarTest#testLogin

### Notes
none

### Suites
Maven | pom.xml | `./mvnw test -q` | OK | Total 47, Passing 47, Failing 0, Skipped 0
```

**A repository with more than one suite baselines all of them**, which the block
above expresses without changing shape: **Framework** and **Command** become
comma-separated lists in run order — positionally paired, so a framework repeats
where the run holds more than one suite of it rather than being de-duplicated —
the counts are the sums and the two test lists are the union. **The identifier
prefix on those lists is not one of this paragraph's deltas: every identifier
carries it — in this block and in verify mode's own lists alike, a single-suite
repository's included** —
`[<Framework>] ` where that framework names exactly one row of `### Suites`, and
`[<Framework> <that row's marker value>] ` where it names more than one. That set
is what a hint cannot narrow rather than what ran — every detected suite has a row
whether the hint ran it or not, a candidate either the workspaces or the Cargo division
carved having one per unit it runs rather than one of its own — so narrowing the run moves no prefix; and the marker
of a row a hint adds is a position in that hint and nothing else, which is why the same
commands are sent again in the same order (`agents/test-baseliner.md` capture steps 1
and 3). And
`### Suites` carries one line per suite the run has a row for — framework, the
qualifying marker **as a path relative to the scan root** (that workspace's own
`package.json` for each row of a workspaces division and that member's own
`Cargo.toml` for each row of a Cargo division, never the candidate's; the
lexicographically first of the folded candidates' marker paths where the `Make`
wrapper rule folded more than one of that framework, which is the folded
candidate's own where it folded one — a candidate a division would have carved
included, since that rule is asked first and no row is then carved at all;
`command_hint#<n>` where a hinted command matched no detected suite,
`declared#<n>` for a declared suite), command,
per-suite status, per-suite
counts — including any the `command_hint` left `not run`. Where more than one of that
row's markers qualified in the one directory, which of them the column records
is fixed by capture step 1 rather than by the scan's order, since two calls
recording different markers disagree on the key verify pairs on. The marker of a row a
marker qualified is a path rather than a bare filename, for two reasons. It tells apart two suites of one framework:
qualifying markers of one row whose directories do not contain each other are
siblings, and siblings are separate suites, so more than one row here can read
`Jest/npm` — as do the rows either division carves, each holding its own unit's
manifest, a workspace's `package.json` or a default member's `Cargo.toml`
(`agents/test-baseliner.md` capture step 1). It tells
apart suites and **not** what a `Make` fold put inside one of them — the
candidates it folded, or the units of a divided candidate it took, that rule
being asked before either division so that such a candidate is folded and never
carved — whose row carries the first of the folded candidates' marker paths,
that candidate's own where it folded one, and whose `### Notes` line names the
others and the units of a divided one, since `make test` runs once and its
output does not attribute (the same step). And for every suite whose
run directory is its marker's own, the path says where that row's command ran —
**the project root only where that marker sits at the scan root**, which is the
agent's own qualified form (*"The project root is that directory only for a suite
whose run directory resolves to it"*) and the rule holding in **both** modes
(`agents/test-baseliner.md` capture step 2 and verify step 3, each stating it at
its own number): `pom.xml` for a suite at the scan root,
`frontend/package.json` for one below it. **Three run directories are not a
marker's own** — a suite the `Make` wrapper folded runs at the `Makefile`'s, a
`--workspace` row of a workspaces division and a member row of a Cargo one run at
the candidate's, and a hinted
command matching no suite runs at the scan root, as a declared suite does — and the first two are named in
`### Notes`, the third being what a `command_hint#<n>` or `declared#<n>` marker value already says. A
single-suite repository's block is unchanged in every field, `### Suites` aside
— **the identifier prefix included**, which is why the example at the head of
this section carries `[Maven] ` on each of its two lists and why the prefix is
no longer one of the multi-suite deltas above. What retired that condition is
measured where the rule lives (`agents/test-baseliner.md` capture step 3), and
**a prefix that moves between a capture and its verify no longer makes a
regression of its own**: the condition that remains still reads each call's own
`### Suites` rows, so it moves whenever that set does, and verify step 5 rewrites
every baseline identifier's prefix onto its paired suite's current one before it
compares — three states, each measured there with that rewrite and without it. A
baseline row verify pairs with nothing is not rewritten, and its tests are
**Missing from run** exactly as they always were.

**`### Notes` is present on every capture return, "none" included**, and it
carries what no other field can: a suite whose watch carve-out did not fire and
why, a qualifying marker whose directory another of its own row's contains — a unit
either division carved a row for being named in that row instead — the run directory
of a suite that did not run at its own marker's (a folded `Make` suite's
`Makefile`, the candidate's own for the `--workspace` rows of a workspaces
division and for the member rows of a Cargo one), every candidate a `Make` fold
covering more than one of one framework
holds and every unit of a divided candidate such a fold took, with the fact that
its identifiers are not attributed to them, a `Make` wrapper one level did not
settle, a CTest candidate with no configured tree, the file and step each declared
suite was read from, an identifier one suite printed more than once, a
best-effort suite recorded by its exit status, "no runner found" with the files
read. **Two of those read, from the `Status` and `### Suites` alone, exactly like
a suite that genuinely failed** — a carve-out that did not fire and a best-effort
command that printed no count and exited non-zero, each leaving a `RUN_FAILED`
row with a command beside it — so a caller that reports a failed suite without
reading this section reports the wrong cause. **Six more stand beside a return
whose every row reads `OK`**: the unsettled `Make` wrapper, the fold's
unattributed identifiers, a qualifying marker a non-recursing container kept out
of the candidate set, a duplicated identifier, a suite recorded by its exit
status alone, and a declared suite — which is what
the marked lines below are for, and why they are read on every status rather than
on the ones a caller already stops at. Verify mode has carried the same
section since before capture did, and it is the same section: capture's detection
is what verify step 1 re-runs, so a note owed at one end is owed at both. What
verify adds to it is its own — this call's aborts, step 2's pairing facts, and
each prefix rewrite step 5 made — so a rewrite line there says a suite's prefix
moved between the two calls, never that anything about it failed.

**A line opening with the literal `CAVEAT: ` is a note whose harm the `Status`,
the counts and the test lists cannot show, and a caller surfaces every one of
them on every status — `OK` and `NO_TESTS` included.** Six of the kinds that
carry the mark can stand beside a green return: a `Make` fold's identifiers,
which are not attributed to what printed them — the candidates it folded, or
the units of a divided candidate it took, the wrapper rule being asked before
either division — so a test one of them stopped printing is masked by another's
copy; a
`Make` indirection one level
did not settle, where two suites run and the same tests may be summed twice; and
a qualifying marker a **non-recursing** container left out of the candidate set,
where a real suite is never run and no row says so — a `package.json` with no
`workspaces` field over another, `go test ./...` over a nested `go.mod`, a
Cargo workspace member outside the default set `cargo test` at that root runs,
or one of the six cases the rows for .NET, PHPUnit, sbt, Mix, Dart and CTest
add (capture step 1); an identifier one suite printed more than once, where the
lists record it once and a loss of one copy is masked by the other; a suite
recorded by its exit status alone — a `Make` suite, or a declared or hinted one
naming no runner of the table, whose output yielded no count or no test name —
where one identifier stands for every test; and a declared suite, whose command
the repository chose rather than the table. The other two — a watch
carve-out that did not fire on a suite whose row then reads `RUN_FAILED`, and a
best-effort suite that printed no count and exited non-zero — arrive on an arm the `Status` does
flag, and there the mark is what reaches a caller that reads this section on none
of its arms. Verify marks three more of its own: an abort of a suite whose
baseline row could lose no passing test, step 2's *"more than one of each for a
framework, none of them pairs"* outcome, and a `command_hint` that narrowed the
run over a suite the baseline ran — the last two putting baseline identifiers
into **Missing from run** without that being evidence the change removed them. **The mark is the agent's, so no caller judges which note matters**,
and an unmarked note is a record of where a command ran or which file was
collapsed into which: a caller that surfaced those on every run would teach its
operator to skip the section. A caller that can only return a record rather than
print one — `vuln-fixer`, `upgrade-executor` — copies each marked line into its
own `notes` verbatim, and its orchestrator carries it from there
(`agents/test-baseliner.md` capture step 5 and verify step 7).

**capture status values:**
- `OK` — every detected suite ran and produced counts, Total > 0
- `PARTIAL` — at least one suite produced counts and at least one did not. The
  baseline covers exactly the suites `### Suites` marks `OK` or `NO_TESTS`, and
  names each one it does not cover with the command that failed. It is
  incompleteness, never a verdict on the code: a caller that stops on it stops
  because a JavaScript runner is not installed
- `RUN_FAILED` — **every** suite that was run aborted with no parseable counts,
  so the baseline records nothing for a later verify to compare against
- `NO_TESTS` — every suite ran cleanly and the combined Total = 0
- `COMMAND_NOT_FOUND` — no candidate matched, no `command_hint` supplied one and
  the repository declares no test command capture step 1 could take, so nothing
  ran (**Framework** then reads `not detected`)

**Field mapping for callers that need YAML-shaped fields** (e.g. `vuln-fixer`'s
and `upgrade-executor`'s `baseline:` input — see their own handoff docs):
`passing_count` = the **Passing** number; `passing_tests` = the `### Passing
tests` list — with several suites, that number and that list are already the
totals across them, so neither caller changes. The orchestrator re-keys these
when constructing the next agent's prompt — this agent never emits raw YAML.
**Those two keys are a convenience beside the block, never a replacement for
it:** whatever else a caller sends, the `verify` call gets the whole block.

## Output — verify mode

```markdown
## Test Verify Report
- **Mode**: verify
- **Status**: REGRESSIONS              <!-- OK | PARTIAL | REGRESSIONS | RUN_FAILED | COMMAND_NOT_FOUND -->
- **Framework**: Maven
- **Command**: `./mvnw test -q`
- **Comparison status**: exact         <!-- exact | best-effort | invalid -->
- **Total**: 47 | **Passing**: 46 | **Failing**: 1 | **Skipped**: 0
- **Baseline passing**: 47 | **Regressions**: 1 | **Missing from run**: 0

### Regressions (previously passing, now failing)
[Maven] com.example.FooTest#testCreate

### Missing from run (previously passing, not present in current run)
none

### Newly fixed (previously failing, now passing)
none

### New failures (new tests that are already failing)
none

### Notes
none

### Suites
Maven | pom.xml | `./mvnw test -q` | OK | Total 47, Passing 46, Failing 1, Skipped 0

### Current passing tests
[Maven] com.example.BarTest#testLogin
```

**verify status values (the authoritative field callers branch on):**
- `OK` — the comparison was possible and every previously-green test is still
  green. The aborts it tolerates are the ones that could lose no baseline
  *passing* test: a suite whose baseline row is `NO_TESTS`, one with no row at
  all because the suite is new since the baseline, and one whose baseline row is
  `OK` but which contributed no passing test — each of which `### Notes` names
- `REGRESSIONS` — one or more baseline tests now fail, or are missing from the
  run entirely; see the `### Regressions` / `### Missing from run` lists. A suite
  the baseline recorded `OK` with at least one passing test and that aborts here
  lands here too, because those tests are then unaccounted for — it ran before
  this change and does not now
- `PARTIAL` — no regressions, and at least one detected suite produced no counts
  here **and no counts in the baseline either — its baseline row reads
  `RUN_FAILED` or `not run`**, so it aborted at both ends or the `command_hint`
  left it out at both. The comparison is sound as far as it reaches and says
  nothing about that suite; `### Suites` names it. A suite whose baseline row is
  `NO_TESTS`, or which has no row at all, is **not** this — that abort is `OK`'s
  above, which is where the agent's own "set the first that applies" ladder
  (verify step 6) puts it
- `RUN_FAILED` — nothing was verified. **Three causes, and the first is settled
  before the run rather than by the ladder**: the supplied baseline covers no
  suite at all — its `### Suites` marks none `OK` or `NO_TESTS`, so there is
  nothing to diff against and the call returns without running anything
  (**Comparison status**: `invalid`, verify's pre-step gate); no detected suite
  matches the baseline (`invalid` as well); or no suite produced counts in this
  run at all. The third is tested **after** `REGRESSIONS`, so a run in which every
  suite aborted is a regression where the baseline had run them, and what reaches
  it is a baseline holding no passing test that could go missing. **A caller
  cannot distinguish that first cause from a real comparison by reading `Status`
  alone, which is why it is refused rather than computed**: with an uncovering
  baseline every count is 0, nothing can go missing, and a ladder allowed to run
  would return `OK` wherever this call's own suites produced counts
- `COMMAND_NOT_FOUND` — no candidate matched, no `command_hint` supplied one and
  the baseline holds no declared suite, so nothing ran (**Framework** then reads
  `not detected`) — the same test capture mode applies, a hint being something to run rather than nothing. Never emitted
  once a call reaches the run step

**What a consumer may do with each.** `REGRESSIONS` is the only value that is
evidence about the change, and the only one on which reverting it is warranted.
`PARTIAL`, `RUN_FAILED` and `COMMAND_NOT_FOUND` each say a suite could not be
run — they are facts about the environment, so a consumer records which suite and
proceeds or escalates, and **never reverts work on them**. Reverting on one of
those rolls back a correct change in one language because a runner for another
is not installed.

**`### New failures` is outside that ladder, because it is not a `Status` value
at all.** A test failing now that was in neither baseline list moves no value
above, so `OK` and `PARTIAL` are both returned with that list non-empty. **Every caller reads the list as well as the `Status`**, or it reads a red suite
as a pass. For a caller that writes tests between its capture and its verify —
`/implement`, through `test-writer` — the list holds its own broken test. For
`/upgrade` and `/vuln`, which write none, it holds a test of a suite the
baseline never recorded: on a `PARTIAL` baseline an aborted suite contributed no
identifiers, so every test of it failing here lands in this list rather than in
`### Regressions`. In each of those two workflows the agent — `vuln-fixer`,
`upgrade-executor` — marks the entries `NEW-FAILURE: ` in the `notes` it returns,
and the command reads that prefix — they branched on the
`Status` alone until `dev-workflows` 4.2.0, which is the behaviour this sentence
used to record.

**Note:** `passing_count` / `regressions` / `new_passes` as bare YAML keys
are a caller-side re-keying convenience, not literal fields this agent
emits — see the field mapping above and each consumer's own handoff doc
for the exact keys it expects back from the *orchestrator* (not from this
agent directly).
