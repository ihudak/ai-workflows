# SEC-G1 Architecture Feedback Loop — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** the security findings registers feed the architecture: a `known-weakness` challenge in `/create-ard`, `/specify`, `/design` and `/update-spec`; a follow-up for the PA when accepted risks of one class recur; and a cross-register recurrence signal in `/promote-decisions`.

**Architecture:**
- One new standard-library script, `plugins/workflows-core/scripts/weakness-classes.py`, is the only reader of registers outside `register.py`. It has two verbs, `classes` and `across`, and prints validated structured fields only.
- One new internal skill, `workflows-core:weakness-classes`, runs it for five commands. It writes the JSON to a temporary file and prints the file's path.
- Agents (`architecture-grounder`, `promotion-scout`) receive that JSON file and never open a register. The rule lives in a new §7 of `workflows-core:security-register-format`.

**Tech Stack:** Python 3 standard library, runnable on 3.9 (the scan's floor); markdown prose that agents execute; the repository gates.

**Spec:** `docs/superpowers/specs/2026-11-13-sec-g1-architecture-feedback-design.md`, revision 2.1, approved 2026-11-13. Read it whole first. § numbers below are the spec's unless a reference is named.

**Execution (already chosen):** subagent-driven. Each task gets an Opus implementer and an Opus task review; Fable reviews the whole branch at the end.

**Base:** worktree `/home/ihudak/dev/ai-tools/ai-workflows-wt/sec-g1`, branch `feat/sec-g1-arch-feedback`. `origin/main` (`3016ead8`, after IMP-G5) is merged in at `55ccb0f1`. Every line number below was read on `55ccb0f1` and is a finding aid only: **locate every site by the quoted phrase.**

## Global Constraints

### What is not ours

- **GIT-G1.** The only GIT-G1 file SEC-G1 touches is `.github/workflows/validate-catalog.yml`, and only by **one** new step: `weakness-classes.py --selftest`, placed right after "Self-test the security register" and written in its style (maintainer ruling, 2026-11-13). The PR names that step for the GIT-G1 owner. Never edit:
  - `plugins/workflows-core/references/specs-repo-git.md`;
  - `plugins/workflows-core/references/phase-handoff.md` and its generated files;
  - `plugins/workflows-core/scripts/specs-git.py`;
  - `.claude/rules/workflows-core-git.md`.

  In every command, leave GIT-G1's sections alone: **Ending early**, the specs preflight, `branch-check`, `require-on-main`, the specs handover (`handoff-to-main` and its `Phase handoff:` line) and the terminal `commit-artifacts`.
- **`register.py` does not change**, and neither does `promotion-signals.py` (design §9 and §7).
- **IMP-G3 runs at the same time.** It does not touch any SEC-G1 code file, but it edits these files too:
  - `plugins/workflows-core/docs/reference/references.md`: IMP-G3 edits its `run-flags.md` entry; SEC-G1 edits the `## Skills` section and the `security-register-format.md`, `architecture-grounding.md` and `architecture-promotion.md` entries.
  - `.claude/rules/workflows-core.md`: IMP-G3 edits the `run-flags.md` paragraph; SEC-G1 edits the *Plugin facts* paragraph.
  - `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md`: IMP-G3 edits row F; SEC-G1 edits row E and D2.
  - `docs/superpowers/reviews/2026-10-26-feature-gaps-review.md`: each marks its own row and heading.
  - `plugins/dev-workflows/docs/reference/environment.md`: IMP-G3 edits its opening sentence; SEC-G1 edits its `--no-arch` sentence (S36).
  - `plugins/workflows-core/docs/reference/environment.md`: IMP-G3 edits its run-flags text; SEC-G1 edits its `--no-arch` resolution sentence (S36).
  - The release files: both bump `workflows-core` and `dev-workflows` (`plugin.json`, `.claude-plugin/marketplace.json`, `CHANGELOG.md`), and each adds a bullet to `.claude/rules/plugin-updates-coupling.md`, which may move bullets to a history file and change `plugin-updates.md` and `CLAUDE.md`.

  SEC-G1 does not edit `implement.md`, `run-state.py`, `model-routing/classification` or `run-flags`. Where IMP-G3 lands first, `git merge origin/main` into this branch (never rebase), keep both sides in every overlap file, and re-derive versions and sizes (Task 8).

### Repository rules

- **Prose is executed.** Every sentence an agent reads must be true when it runs.
- **Shared references** are cited `workflows-core:<name>` outside `workflows-core`, never by path. The new skill is called `Skill(skill: "workflows-core:weakness-classes", args: "…")`, unfenced and inline: that execution phrase is what §6's recipe and `validate-catalog`'s skill-call check read. Its SKILL.md carries no `disable-model-invocation`.
- **Docs entries.** A new skill without its row in `workflows-core/docs/reference/references.md` and the right count in `docs/README.md` fails `check-docs` (checks 4 and 9).
- **User pages** (`plugins/*/docs/**`, plugin READMEs) carry no `§`, no `D<n>`, and no `<plugin>:<reference-name>` (check 25). Say it in words, or use the path form. Each table cell is at most 200 characters (check 6).
- **Sizes, cutting nothing.**
  - `.claude/rules/*.md`: under 20,000 characters. Measure with `python3 -c "import sys;print(len(open(sys.argv[1],encoding='utf-8').read()))" <file>`, never `wc -c`.
  - `CLAUDE.md`: under 36,000 characters.
  - An agent's or skill's frontmatter `description`: at most 600 characters.
- **ID grammar:** `[SEC#n]`, `[AD#N]`. Never a dash form of either.
- **Vendor neutrality:** no tracker names.
- **Every executed regex uses `[0-9]`, never `\d`**, in the script and in prose. In Python, every whole-value pattern is anchored `^…\Z` and compiled with `re.ASCII`.
- **Commits:**
  - Run `git branch --show-current` immediately before each one. Expected: `feat/sec-g1-arch-feedback`.
  - End each message with:
    ```
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01EcAVqApJxfCBcAbv5iWuu7
    ```

### `weakness-classes.py` — the contract (Tasks 1–2 build it; Tasks 3–7 consume it)

**CLI.** Flags repeat (`action="append"`), and repeated values are deduplicated.
```
weakness-classes.py classes --specs <root> --repo <slug> [--repo …] [--component <id> …] [--origin <origin> …] [--prd-key <KEY>] [--today <YYYY-MM-DD>]
weakness-classes.py across  --specs <root> --ref <ref> [--today <YYYY-MM-DD>]
weakness-classes.py --selftest
```
- `--today` defaults to today's UTC date.
- The script reads no environment variable.
- It runs nothing named in a register and opens no path taken from one.

**Exits.**
- `0`: it ran. Exactly one JSON object goes to stdout (`json.dumps(…, indent=2)`).
- `2`: it could not run. One stderr line, `weakness-classes: not run (<why>)`, and nothing on stdout. Each cause has its own fixed `<why>`, which names the flag and never echoes a register or record value:
  - a usage error, or a flag value that fails its check (argparse's error is overridden to print this one line);
  - `--specs` is not a directory;
  - a `--component` whose slug is not among the `--repo` values;
  - for `across`: `--specs` is not a git work tree, or `--ref` does not resolve to a commit;
  - **any other exception:** `main` catches it and prints exactly `weakness-classes: not run (internal error)`, never the exception's text or a traceback (review I2).
- `--selftest`: `0` when every case passes, `1` otherwise.

No register state, team record or finding ever causes exit 2 by itself.

**Validators** (design §8; at least as strict as `register.py`'s):

| Value | Check | On failure |
|---|---|---|
| slug (`--repo`; a directory name in `across`) | `^[A-Za-z0-9._-]+\Z`, not `.` or `..` | exit 2; in `across`, the directory is not a register |
| `--prd-key` | `^[A-Z][A-Z0-9_]*(-[0-9]+)+\Z` | exit 2 |
| `--component` | `<slug>` or `<slug>:<path>`; the slug must be among `--repo`; `<path>` passes the path check, with no leading `./` and no trailing `/` | an unnamed slug is exit 2; a failing `<path>` is ignored for `in_component` (R6) |
| `--today` | a real `YYYY-MM-DD` | exit 2 |
| `--origin` | compared exactly with the `origin` values the register holds | an unknown one is ignored |
| `cwe` | `^CWE-[0-9]{1,6}\Z`. The **class key is `CWE-<int(digits)>`**, so `CWE-089` is `CWE-89`. Digits equal to 0 fail | the finding is counted in `unclassified` and joins no class |
| `path` | `^[A-Za-z0-9._@+][A-Za-z0-9._/@+-]*\Z`, no `..` segment, ≤ 512 characters | printed as `null` |
| `id` | `int`, not `bool`, ≥ 1 | the finding is dropped |
| `line` | `int`, not `bool`, ≥ 0 | dropped |
| `severity` | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` | dropped |
| `status` | `new`, `open`, `fix`, `fixing`, `fixed`, `reopened`, `false-positive`, `accepted-risk` | dropped |
| `review_by` | a real date on an `accepted-risk`; `null` or absent otherwise | dropped |
| `confirmed` | `bool` or `null` | dropped |
| a `history` entry the rule reads | `status` in the enum; `at` matches `^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\Z` and parses; `run` is `int`, not `bool`, ≥ 1 | dropped |
| a team record's id | the `.md` file's stem, `^[A-Z][A-Z0-9_]*(-[0-9]+)+(-[a-z0-9]+)*-AD[0-9]+\Z` | the record is skipped and counted in `kb_skipped` |
| the record's `status` | a scalar | skipped |
| the record's `source` | the path check | skipped |
| the record's `promotion` | absent, or one of `proposed`, `accepted`, `rejected`, `declined`, `covered` | skipped |
| the record's `promoted_to` | absent, or `promotion-signals.py`'s `PROMOTED_TO_RE` shape, `^[A-Za-z0-9][A-Za-z0-9._-]{0,99}\Z` | skipped |
| the record's `components` | a flow list `json.loads` reads as a list of strings | skipped |
| the record's `**Prevents:**` paragraph | present | skipped |

- A dropped finding is counted in `dropped`.
- Every field outside the printed set is never printed: `title`, `reason`, `evidence`, `by`, `owner`, `links`, `scope`, `units`, `origin`, `plugin_id`, `other_cwes`, `first_seen`, `last_seen`.
- A register or team-record value that fails its check is never echoed, not even in an error.

**What it reads.**
- `classes` reads the working tree:
  - `<specs>/security/<slug>/register.json`, and nothing else under `security/`. A slug resolves only by an exact match against `os.listdir(<specs>/security)`, never by opening the path directly, so a case-insensitive file system never maps `api` to `API/`;
  - the frontmatter and `**Prevents:**` paragraph of `<specs>/architecture/decisions/*.md`.
- `across` reads the same two kinds of file **at `<ref>`**, through `git ls-tree` and `git show` (or `git cat-file`), with `GIT_TERMINAL_PROMPT=0` and `GIT_OPTIONAL_LOCKS=0`. It never checks anything out.
- **A team record** is parsed as design §3.3 says:
  - the frontmatter lies between the first two `---` lines;
  - scalars lose one pair of quotes;
  - `components` is a flow list read with `json.loads`;
  - Prevents is the body paragraph that opens `**Prevents:**`, up to the next blank line, its lines joined by single spaces.
- **A register's `state`:**
  - `absent`: no such file;
  - `unreadable`: an `OSError`, or bytes that are not UTF-8 JSON;
  - `unknown-format`: a JSON object whose `format` is not `1`;
  - `malformed`: not an object, `findings` not a list, or a `last_at` that is neither `null` nor a valid `at`;
  - `ok`: otherwise.

  A state other than `ok` gives `last_at: null` and zero counts.

**The rule** (design §3.4, written into `security-register-format` §7):
- **Live:** `new`, `open`, `fix`, `fixing`, `reopened`, `accepted-risk`.
- **Recent fixed:** `fixed`, where the `at` of the last `history` entry is at most 180 days before `--today`. 180 days counts; 181 does not; a later date counts.
- **Judged real** (`across`): `fix`, `fixing`, `reopened`, `accepted-risk`, and recent fixed.
- **Never counted:** `false-positive`.
- **The accepting run** of an `accepted-risk` finding is the `(run, at)` of the earliest entry in the unbroken trailing run of `accepted-risk` entries in its `history`.
- **Recurs** (`classes`): `accepting_runs` — the distinct accepting-run pairs among the class's `accepted-risk` findings — is ≥ 2.
- **Prevents.** A record prevents a class where:
  - its `status` is `accepted`; and
  - its Prevents paragraph names the class as a whole token, `CWE-0*<int>`: not preceded by `[A-Za-z0-9_-]`, and not followed by `[A-Za-z0-9_]`. So `[CWE-89](…)` and `CWE-089` match class `CWE-89`, while `CWE-890` and `XCWE-89` do not (review I4).

  In `classes`, one of the record's `components` must also have the register's slug: the id itself, or its part before the first `:`.

  A promoted record (`promotion` `accepted` or `covered`) still prevents.
- **`in_component`:** some `--component` holds a live finding of the class. A bare `<slug>` holds every finding of its register. `<slug>:<path>` holds a finding whose path equals `<path>` or starts with `<path>/`.
- **Ranking of `classes`:**
  1. recurring with an empty `prevented_by`, first;
  2. `in_component` true, first;
  3. the highest live severity;
  4. the larger `live`;
  5. the slug, ascending;
  6. the CWE number, ascending, compared as numbers.
- **Ordering of `across`:** more registers first, then the larger `real`, then the CWE number.
- **Lists:**
  - `registers` is sorted by slug, and `absent` entries are included;
  - `prevented_by` is sorted by id;
  - a class's `findings` holds at most 5 entries: live findings first, by severity then id, then recent fixed by id.

**Output.**
- `classes`: `{format: 1, today, kb_skipped, registers: [{repo, state, last_at, findings, dropped, unclassified}], classes: [...]}`. Only classes with ≥ 1 live finding are listed. Each class holds:
  - `repo`, `cwe`, `cwe_url`;
  - `live`, `accepted`, `accepting_runs`, `awaiting_review` (live `accepted-risk` with `confirmed: false`), `review_due` (`accepted-risk` whose `review_by` is before `--today`) and `fixed_recent`;
  - `top_severity`, `in_component`, `recurs`;
  - `decided` and `decided_ids`, keys present only when `--origin` was given. `decided_ids` lists the `id` of each finding of the class whose origin was passed, as validated ints, ascending. Phase 5 maps its rows by these `[SEC#n]`, never by CWE (review I4);
  - `prevented_by: [{id, source, promotion, promoted_to}]`;
  - `findings: [{id, status, severity, path, line, review_by, confirmed}]`;
  - `pa_line` and `pa_next_step`.

  Here `cwe_url` is `https://cwe.mitre.org/data/definitions/<int>.html`, and the register's `findings` is the length of its `findings` list.
- `across`: the same envelope, plus `ref`, the full commit sha `--ref` resolved to (never the string as given). Its classes are those with ≥ 1 judged-real finding in each of ≥ 2 registers. Each holds:
  - `cwe`, `cwe_url`, `real`, `accepted`, `fixed_recent`;
  - `registers: [{repo, real, accepted, fixed_recent, last_at}]`;
  - `prevented_by: [{id, promotion, promoted_to}]`, from live records naming the CWE, whatever their components.
- **The PA fields** (`classes` only):
  - Both are null unless the class is `decided`, `recurs` and has an empty `prevented_by`.
  - With `--prd-key`, `pa_line` is set and `pa_next_step` is null.
  - Without it, `pa_line` is null and `pa_next_step` is set.

**Exact copy.** `<n>` values come from the class. The bracketed `, <awaiting> awaiting security review` clause appears only where `awaiting_review` ≥ 1.
- `pa_line` (design §5.3, verbatim). `<PRD-KEY>` is `--prd-key`:
  ```text
  - [ ] Run `/product-workflows:create-ard <PRD-KEY>` to record an [AD#N] whose Prevents names [<cwe>](<cwe_url>) — <accepted> accepted risks of <cwe> in the <repo> register (security/<repo>/register.md), accepted in <accepting_runs> runs[, <awaiting> awaiting security review], and no team decision for <repo> prevents it — raised by /security-workflows:scan
  ```
- `pa_next_step` (ruling R8). Here `<PRD-KEY>` stays literal, for the user to fill:
  ```text
  Record an [AD#N] whose Prevents names [<cwe>](<cwe_url>), with `/product-workflows:create-ard <PRD-KEY>` for the PRD whose work changes the <repo> repository — <accepted> accepted risks of <cwe> in the <repo> register (security/<repo>/register.md), accepted in <accepting_runs> runs[, <awaiting> awaiting security review], and no team decision for <repo> prevents it.
  ```

### The skill (Task 3)

`plugins/workflows-core/skills/weakness-classes/SKILL.md`:
- **Frontmatter:** `name: weakness-classes`, a `description` of at most 600 characters, `user-invocable: false`, `allowed-tools: Bash`.
- **Argument:** the verb and its flags, as the caller wrote them, each value single-quoted. The skill adds `--specs`.
- **The argument rule (review I1).** An origin is scanner-written text (`register.py` checks only that its plugin ID holds a `:`). So the skill never puts on the command line a value holding any character outside `[A-Za-z0-9._:/@+=-]`.
  - A `--component` value that fails is **dropped**, and its `--repo` is kept, so an odd component path costs only `in_component`, as R6 has it (re-check N2).
  - Where any other flag's value fails, the skill runs nothing, prints `weakness-classes: not run (an argument holds a character the skill does not pass)`, and prints no path.
- **The call:** one Bash call:
  ```
  out=$(TMPDIR="<scratchpad>" command mktemp -t dw-weakness-classes-XXXXXX.json) && python3 "${CLAUDE_PLUGIN_ROOT}/scripts/weakness-classes.py" <verb> --specs "${SPECS_PATH-}" <flags> > "$out"
  ```
  - Drop the `TMPDIR` assignment where the session names no scratchpad that exists (`workflows-core:run-flags` §7, stated in the skill itself). Write `TMPDIR` without a `$`, so `check-docs` check 5 does not read it as a variable the plugin reads.
  - Where the run took `$SPECS_PATH` from an answer rather than the environment, open the call with `export SPECS_PATH='<the value>';`, as `specs-git` does.
- **On exit 0:** print the file's absolute path as the skill's last line. The file is never edited and, like the promotion signals file, never removed.
- **On any non-zero exit:** remove the file. Print the script's stderr line only where it starts `weakness-classes: not run (`; otherwise print `weakness-classes: not run (the script exited <code>)`. Never print any other stderr text. That one line is "the skill's error" in every caller's report line. Print no path.
- **The caller:**
  - hands the path to its agent, or reads the JSON's fields itself;
  - never opens a register;
  - is always a command, never an agent.

### Part 1's resolve fields, lines and dispatch (Task 4 writes them; Task 5 consumes them)

**`resolve-architecture-grounding`.**
- It returns, beside its existing fields, `security_registers` (`ON`, `OFF` or `none`), `security_root`, `security_count` and `security_reason`.
- `none` means `$SPECS_PATH` is unset or empty, or `$SPECS_PATH/security` is neither a directory nor a symbolic link. Then no line prints and nothing is called.
- A symbolic link at `$SPECS_PATH/security` is `OFF` with the reason `<specs>/security is a symbolic link` (Task 4 review M3): the script follows no link, so it would read every register through one as `unreadable`.
- `security_count` is the number of `register.json` files directly under `$SPECS_PATH/security/*/`, counted with `find … 2>/dev/null | wc -l` so that no name under `security/` reaches the run.
- Step 1 (`--no-arch`) returns `OFF` with the reason `disabled with --no-arch` wherever the resolution would not return `none`.

**Configure lines** (design §4.1), shown beside the team line:
```
security registers: ON <specs>/security (<n> registers; read for the repositories the work touches)
security registers: OFF (disabled with --no-arch)
security registers: OFF (no findings register under <specs>/security — it holds only cost or feedback entries, or other files)
security registers: OFF (<specs>/security is a symbolic link)
security registers: OFF (<specs>/security is not readable)
```

**The consumer's call.**
- **When:** only where `security_registers: ON` and the component set is not empty, whether or not a root is ON. Make it once the scan's last batch has returned — in `/create-ard`, after Phase 3 step 4's scan; in `/specify` and `/design`, where Phase 4's paragraph waits for it — the point where `stack_facts` is built (review M2):
  `Skill(skill: "workflows-core:weakness-classes", args: "classes --repo '<slug>' … --component '<id>' …")`
- **Arguments:** an id's slug is the id up to its first `:`, or the whole id where it has none (`workflows-core:components` §1). Keep each component id the grounder gets that passes all three tests, and leave out every other one (`architecture-grounding.md` § Dispatch, *The argument*; Task 4 review M1):
  1. every character lies in the skill's class `[A-Za-z0-9._:/@+=-]`;
  2. it does not open with `-`;
  3. its slug is not empty, holds only letters, digits, `.`, `_` and `-`, and is neither `.` nor `..` (the script's slug check, which would otherwise refuse the whole call).

  Then one `--repo` for each distinct slug of the ids kept, and after the last of them one `--component` for each id kept, bare slugs included: every `--repo` before any `--component`, and no other flag. Where no id is kept, make no call.
- **Dispatch condition:** `arch_grounding: ON`, or `team_grounding: ON`, or a non-empty `classes`.
- **New dispatch input:** `weakness_classes: <absolute path of the JSON> | null`, set only where `classes` is non-empty.
- **When the skill fails:** grounding runs exactly as without the call, and the final report carries `security registers: not read — <the skill's error>`. `<the skill's error>` is the skill's `weakness-classes: not run (…)` line; for a path whose file cannot be used, `the JSON file the skill named could not be read`; for any other output, the Skill tool's own failure among it, `the skill printed neither a path nor a not-run line`, never that output (Task 4 review M5).
- **`root_errors`** (Task 4 review M6). `architecture-grounder`'s output gains one optional key, `root_errors: ["<arch_root | team_root> <its path>: <what failed>", …]`, on an `OK` or `EMPTY` digest only, naming each set root it could not read, and omitted where every set root was read; `error:` stays `ERROR`-only. Where the digest carries it, each command's final report carries one line for all its entries, copied verbatim from `architecture-grounding.md`: `architecture grounding: root not read — <entry>[; <entry>…]`, each `<entry>` as the digest gives it, in its order. It matters most where the run holds a class and no set root could be read: the digest is then `OK` with `known-weakness` challenges alone, where it was `ERROR` before.
- **When it ran:** the final report's `architecture grounding:` line gains `; registers read: <each slug in state ok, comma-separated>`, then `; skipped: <slug> (<state>), …` for `unreadable`, `unknown-format` and `malformed` registers. `absent` is silent.

**`known-weakness`** (design §4.3–4.4).
- **Shape:** `kind`, `subject: <cwe> in <repo>`, `evidence`, `governing`, `weakness`.
  - `evidence` is `security/<repo>/register.md — ` followed by `[SEC#<id>] <status> <severity> <path>:<line>` per evidence entry, joined by `; `. Where the path is null, `location in register.md` stands in place of `<path>:<line>`.
  - `weakness` is `{repo, cwe, cwe_url, live, accepted, awaiting_review, review_due, fixed_recent, recurs, register: security/<repo>/register.md}`.
- **Cap and order:** at most **3**, inside the existing cap of 8, taken in the script's order. Challenges are ordered `contradicts-*`, then `known-weakness`, then `radar-retire`, `radar-hold`, `radar-absent`.
- **`governing`:**
  - It is null where `prevented_by` is empty. Otherwise it is picked in tiers (Task 4's ruling, as `architecture-grounder.md` step 5a states): a record from the run's own ARD first, then one the agent can quote, then a promoted one; `prevented_by`'s text order breaks only ties. Consumers test only whether it is null.
  - Normally it is quoted from `team_root/decisions/<id>.md`, as any team reference is.
  - Where its `source` is in `own_sources`, or `team_root` is null, it gives `{id, source}` only.
  - Where its `promotion` is `accepted` or `covered`, it is `{ id: <promoted_to>, title: null, root: organisation, path: null, url: null, rule: null }`, with no `prd` and no `source`.

### Exact copy the commands use

- **`/create-ard`**, for a recurring class with a null `governing`:
  ```text
  choices: ["Record an [AD#N] that prevents <cwe> (Recommended)", "Not in this ARD"]
  ```
- **A specification's open question** (design §4.5). The link target is relative from the specification to `security/<repo>/register.md`:
  ```text
  - [ ] Known weakness: [<cwe>](<cwe_url>) in <repo> ([register](<link>)) — <how this work could add to it> — settled by a Security / privacy acceptance criterion that prevents it
  ```
  - Where the class recurs and `governing` is null, append `, or by an ARD decision whose Prevents names that CWE, made with /product-workflows:create-ard <PRD-KEY>`.
  - The CWE appears only as the link. A bare `CWE-<n>` in an artifact is a pre-lint finding.
- **A design line** (design §4.5, verbatim):
  ```text
  - Known weakness: [<cwe>](<cwe_url>) in <repo> ([register](<link>)) — <how this design avoids adding to it, or why it accepts it>
  ```
- **Part 3** (design §6.3). User-facing text says "registers", never "teams" (design E10):
  ```text
  prevents <cwe>, which recurs in <n> registers (<slug>, …)
  <cwe> — recurs in <n> registers: <slug> (last run <date>), <slug> (<date>), …; <accepted> accepted risks, <fixed_recent> fixed — no team decision prevents it, and no ADR or standard covers it — record one with /product-workflows:create-ard
  Weakness classes recurring across registers: <n> covered by an ADR or standard; <m> prevented by a team decision not on this shortlist.
  ```
  - The first line is a candidate's reason.
  - The second is a *Reported only* line.
  - The third is the count line (ruling R11), printed where either count is ≥ 1. A class both covered and prevented counts once, as covered (review M4).

### Gates

Run them as one chain, from the worktree root, and read the printed value:
```bash
set -o pipefail; python3 scripts/validate-catalog.py && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --baseline && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && python3 scripts/reference-parts.py check-branch-check && ./scripts/check-docs.sh --root . && python3 plugins/workflows-core/scripts/weakness-classes.py --selftest && python3 plugins/security-workflows/scripts/register.py --selftest; echo "EXIT=$?"
```
- Before Task 1 creates the script, drop its `--selftest` from the chain.
- `promotion-signals.py --selftest` joins only where a task touches that script. None does.
- Expected: `EXIT=0`, and no `WARN` line from `validate-catalog`.
- Where `node` exists, a task that edits a mermaid block also runs `npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund && node scripts/mermaid/check-mermaid.mjs --root .`.

### The claim sweep (design §10)

- **Method:** claim-sweep refinements 1–8. The scope is `plugins/` (every `CHANGELOG.md` included), `README.md`, `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/`. Match by phrase; read the whole paragraph around each hit.
- **Counting:** count wrap-insensitively, immediately before and after each edit:
  ```bash
  sweep() { python3 -c '
  import os,re,sys
  def walk(r):
      if os.path.isfile(r): yield r
      for d,_,n in os.walk(r):
          for f in n:
              if f.endswith((".md",".py",".json",".yml",".sh")): yield os.path.join(d,f)
  for ph in sys.argv[1:]:
      k=re.sub(r"\s+"," ",ph); hits={}
      for r in ("plugins","README.md","CLAUDE.md",".claude/rules","docs/maintainers"):
          for p in walk(r):
              c=re.sub(r"\s+"," ",open(p,encoding="utf-8",errors="replace").read()).count(k)
              if c: hits[p]=c
      print(sum(hits.values()),ph,hits)
  ' "$@"; }
  ```
  Map each hit to its line with `grep -n` when recording it.
- **Recording:** each owning task records, in its report, each row's before count, its after count, and each hit's disposition.

The "before" column was measured on `55ccb0f1`.

| # | Phrase (`sweep` argument) | Before | Owner | Intended after |
|---|---|---|---|---|
| S1 | `Not in it: E, the architecture feedback loop` | 1 | 8 | 1: history, true of its release (design §10 item 1) |
| S2 | `is the register's only writer and implements this file` | 1 | 1 | 0; it narrows to "§1 to §5", and §7 names `weakness-classes.py` |
| S3 | `never read back as a run's state` | 1 | 3 | 0 |
| S4 | `reads the derived files back as its state` | 2 | 3 | 0: the format's §1, and the security register page `:26`, a copy the design missed |
| S5 | `reads them back as its state` | 2 | 3 | 1: `register.py:16` stays. `register.py` is unchanged, and its sentence stays true, since the reader decides no register change. `docs/workflow.md:70` is rewritten |
| S6 | `The one read of a derived file as state` | 1 | 3 | 0; the new phrase `as the register's state` goes from 0 to 5 |
| S7 | `builds every follow-up line` | 1 | 6 | 0 |
| S8 | `builds them at Phase 7.2` | 1 | 6 | 1, plus the PA line's sentence in the same bullet |
| S9 | `every reader of the register reads it the same way` | 1 | 3 | 0 |
| S10 | `its readers are what` | 1 | 3 | 1, extended with the skill's callers' recipe |
| S11 | ``the rules `register.py` applies`` | 2 | 3 | 2, each extended with §7's weakness classes |
| S12 | `The script implements it` | 1 | 3 | 0 |
| S13 | `implements it (byte-identical in every edition` | 1 | 3 | 1, plus a sentence naming the second implementer |
| S14 | `three bundled skills` / `Three skills ship` | 2 / 1 | 3 | 0 / 0; `four bundled skills` goes to 2 |
| S15 | `every miss turns grounding OFF` | 1 | 4 | 1: re-read, and the opening gains the registers |
| S16 | `The team line is shown with the organisation line, always` | 1 | 4 | 1, plus the security line's own sentence |
| S17 | ``Run only when `arch_grounding: ON` or `team_grounding: ON` `` | 1 | 4 | 0 |
| S18 | `A promoted team record is not read` | 1 | 4 | 1, plus its exception |
| S19 | ``Never blocks; every miss is `OFF` with a reason`` | 1 | 4 | 1, plus the failed-call line |
| S20 | `At least one of the two roots is set` / ``No root readable → `status: ERROR` `` | 1 / 1 | 4 | 0 / 0 |
| S21 | `At most 8 challenges` / `the sources were read and nothing bears on the work` | 1 / 1 | 4 | 1 / 0: the cap is re-worded around it; the EMPTY sentence becomes `the sources it could read were read`, since an `EMPTY` digest can carry `root_errors` (Task 4 re-check) |
| S22 | ``Where it resolved `arch_grounding: ON` or `team_grounding: ON` `` | 3 | 5 | 0 |
| S23 | `` `architecture grounding:` and `team decisions:` lines `` | 9 | 5 | 2, the two CHANGELOGs. The seven sites in `create-ard.md` (2), `specify.md` (2), `design.md` (2) and `docs/commands/specify.md` (1) name the security line too |
| S24 | `` `docs grounding:`, `architecture grounding:` and `team decisions:` `` | 1 | 5 | 0: `update-spec.md:68`, a site the design missed |
| S25 | `Phase 1's OFF lines dispatch nothing` | 1 | 5 | 1: re-read only (design §10 item 8); record why it stays true |
| S26 | `Where grounding was OFF, nothing in this section is required.` (with the period) | 2 | 5 | 0 (ruling R16) |
| S27 | `where 7.2 built any` | 1 | 6 | 0 |
| S28 | ``Each line is written exactly as `commit` printed it`` | 1 | 6 | 1, plus the PA line's clause |
| S29 | `A line without the token is matched as before` | 2 | 6 | 2, each followed by the PA line's identity; the dev follow-ups page `:54` is a copy the design missed |
| S30 | `no candidate and no superseding entry` / ``neither root is readable, or `signals` is not the JSON described`` | 1 / 1 | 7 | 0 / 0 |
| S31 | ``No record with `candidate: true` and no artifact with friction`` | 1 | 7 | 0 |
| S32 | `` `architecture-grounder` never writes, fetches, pulls or switches the architecture repository `` | 1 | 4 | 1, plus "never opens a file under the specs repository's `security/`" |
| S33 | `Where it resolved OFF, dispatch nothing` | 8 | 5 | 5. The three that close the architecture dispatch paragraphs (`create-ard.md` Phase 3 step 6, `specify.md` and `design.md` Phase 4) are reworded: they contradict the widened trigger, where both roots are OFF and classes exist. The five docs-grounding twins stay, and are recorded by file and line as the five left (`create-ard.md`'s step 5, `create-prd.md`, `idea.md`, `specify.md`'s docs paragraph, `update-prd.md`) (review I3a) |
| S34 | `builds them from structured fields only` / `follow-ups written to <target>` | 1 / 3 | 6 | 0 / 2. In `scan.md`'s Invariants, "`register.py commit` builds them" becomes false for the PA line and sentence, so it is reworded. 7.6's output names two targets now, so its `N follow-ups written to <target>` is reworded; `/conformance`'s and `/ready`'s stay (review I3b) |
| S35 | `turns both off` / `turns off both architecture roots` / `Disable both per run with` | 2 / 1 / 1 | 4, 5 | 0 / 0 / 0. These are `architecture-grounding.md` `:39` (Task 4), `product-workflows/docs/workflow.md:190` (Task 5), core `grounding.md:37` (Task 4) and the repository-root `README.md:102` (Task 5). Each names the security registers as the flag's third source (review I3c) |
| S36 | `turns off architecture grounding for the run` / `` `--no-arch` turns it off for a run `` / `forces architecture grounding off` | 1 / 2 / 1 | 4, 5 | 0 / 0 / 0. These are `design.md:26` (Task 5), the `dev-workflows` and `product-workflows` `environment.md` pages (Task 5) and the `workflows-core` `environment.md` page (Task 4). Then every remaining `--no-arch` hit (38 before) is dispositioned. The usage, synopsis and flag-strip lines stay; any other description of what the flag turns off names the registers. Core `grounding.md`'s *At a glance* table gains a *Security registers* row, with `--no-arch` as its off switch (Task 4) |

Design §10 items 13–16, which have no phrase row:
- Item 13 is S14.
- Item 14: the `CLAUDE.md` paragraphs, in Task 3.
- Item 15: the CI step, in Task 1.
- Item 16: the roadmap D2 line, in Task 8.

### Rulings where the design is silent

- **R1:** `[0-9]` in place of `\d`. This is identical under `re.ASCII`, and it is the repository's executed-regex rule.
- **R2:** the CWE class key is canonical: `CWE-089` is `CWE-89`, and `CWE-0` is unclassified. A link to `…/089.html` would be broken, and two keys for one weakness would split its count.
- **R3:** checks on the printed team-record fields that §8's table omits: `source`, `promotion`, `promoted_to` (in `promotion-signals.py`'s stricter `PROMOTED_TO_RE` shape, by the review's ruling), and the id taken as the file stem. Design §8 says a field that fails its check is never echoed, and these fields are printed.
- **R4:** an `accepted-risk` finding with no readable accepting entry, or a `fixed` one with no readable last entry, is dropped. The rule cannot be applied to it, and `register.py` always writes those entries.
- **R5:** exit 2 covers every case where the script could not run: usage errors, `--specs` not a directory, and `across` with no repository or no such ref. Design §3.1 knows only exit 0 and 2.
- **R6:** every component id is passed as `--component`, bare slugs included. A component of an unnamed slug is exit 2, since a caller that mis-derives a slug is a defect, not a silent miss. A component whose `<path>` fails the path check is ignored for `in_component` (the review's ruling). This makes `in_component` mean "inside the work's components".
- **R7:** `across` prints `ref` as the sha it resolved to, which is deterministic, and orders its classes by register count, then `real`, then CWE.
- **R8:** `pa_next_step`'s copy, which design §3.2 names but does not fix.
- **R9:** the commands derive `--repo` from the component ids (exact, by `components` §1), and make no call for an empty set.
- **R10:** the grounder picks `governing` in tiers (own ARD, then quotable, then promoted; text order breaks ties) — amended after Task 4, since `prevented_by` sorts ids as text (`AD10` before `AD2`). With `team_root` null it gives the id and source only. An unreadable `weakness_classes` file is `ERROR` only where no root is readable; otherwise the grounder raises no `known-weakness`.
- **R11:** the Part 3 count line also counts uncovered classes whose preventing record is not a shortlist row, so no class is silently absent.
- **R12:** *Not in this ARD* writes nothing into the ARD, and the final report names the class.
- **R13:** `.claude/rules/product-workflows.md` stands at 19,989 characters, so its `## Invariants` section moves byte for byte to a new `.claude/rules/product-workflows-prd-flow.md` (Task 5). `dev-workflows.md` stands at 19,945 characters, so it takes a 28-character edit and no split, unless the measure at Task 5, or Task 8's after the merge, says otherwise. **The `/design` map line's asymmetry is deliberate** (review M6): it gains only the widened `when` clause and no `[weakness-classes …]` bracket, while the product lines gain both. The skill call is a step inside the grounder's dispatch, which the map draws as one bracket, and `dev-workflows.md` has no room for more.
- **R14:** `.claude/rules/security-workflows.md`'s `paths:` gains the script, as `docs-grounding.md`'s does. The register invariants bind it, and `CLAUDE.md`'s table row follows.
- **R15:** sites the design's §10 missed: S4's register page, S23, S24, S26, S29's page, S33–S36 (the review's I3), `references.md`'s three entries, and the `agents.md` rows.
- **R16:** two bullets sit outside the premise "grounding ON": `ard-format`'s CWE bullet binds every decision whose Prevents names a CWE, and `design-format`'s premise widens to "or `architecture-grounder` returned a `known-weakness` challenge".
- **R17:** two pieces of the scan's wording are fixed here: its report line `- Weakness classes: …`, and Phase 5's row note `prevented by <id>[, <id>…]`.
- **R18 (review I5, as amended by the controller):** the PA line's folder and `--prd-key` are the folder and key `/create-ard` would read a PRD from. That is tested by the artifact `/create-ard` consumes, **never by the folder's asserted `kind` or its prefix**. `CLAUDE.md`, *Hard constraints*: "Any kind gate must test the artifact it actually cares about, never the folder's asserted kind — a BRD-route slice is `PRD-`-prefixed yet asserts `kind: brd`." `.claude/rules/brd-route.md` (the bullet "A slice folder is `PRD-`-prefixed and asserts `kind: brd`") explains why: "An asserted-kind gate would refuse every slice and accept nothing". It also gives the artifact test this follows: `/epics`'s accept gate "tests **`prd.md`'s own `kind: prd`** one file down".
  - **The artifact, by `/create-ard`'s own name and test.** Its Phase 0 gate (the phrase "**Gate the PRD — on every route, with no branch.**") runs `require-on-main` "against the PRD file in that folder … that file is `prd.md`, a constant". Its Phase 2 (the phrase "Read the PRD from the folder `resolve-address <PRD>` returned") reads "its `prd.md`, whose frontmatter is `kind: prd`". So a folder qualifies where it holds a top-level `prd.md` whose frontmatter `kind:` is `prd`.
  - **The candidate folders** come from what Phase 0 step 4 already holds, never from a folder name read by pattern:
    - an Epic-scoped run (two keys in the run key set): the resolved folder's parent folder and the parent's key, where the parent qualifies;
    - a single-key run: the resolved folder and its key, where it qualifies.
  - **Otherwise** — a path run, a candidate without such a `prd.md` (a BRD container, or a slice with no PRD authored yet) — pass no `--prd-key`, and the sentence goes to the report.

## Review Focus

1. **A CWE written with leading zeros** (`CWE-089`) is the same class as `CWE-89`, and its URL ends `/89.html`. A record whose Prevents names `CWE-089` prevents class `CWE-89`. Lowercase `cwe-89` and `CWE-0` are unclassified. Test: Task 1, `case_cwe_canonical`.
2. **A risk re-accepted at its review date in a later run** (Phase 5's review-due re-date, or a `sec` confirmation) is still one acceptance. accept → fix → accept is a new one. Test: Task 1, `case_redated_risk_is_one_acceptance`.
3. **A Prevents paragraph wrapped over lines** prevents the class. One naming the CWE only inside a link's URL (`[SQL injection](https://cwe.mitre.org/data/definitions/89.html)`) does not. Test: Task 1, `case_prevents_wrapped_and_url_only`.
4. **Directories under `security/` that are no register** are silent. Such a directory is a team's document folder, a name with a space, or one holding only `dev-workflows/` cost entries. A `--repo api` beside a `security/API/` is `absent`. Tests: Task 1, `case_non_register_dirs`; Task 2, `case_across_non_register_dirs`. Task 4's configure step counts only `register.json` holders.
5. **The 180-day boundary:** day 180 counts and day 181 does not. A `fixed` finding whose last entry has a malformed `at` is dropped, not counted. Test: Task 1, `case_fixed_window_boundary`.

---

### Task 1: `weakness-classes.py classes`, `security-register-format` §7, the CI step

**Files:**
- Create `plugins/workflows-core/scripts/weakness-classes.py`: the docstring, the validators, the readers, `classes`, `main`, and `selftest` with its `case_*` functions.
- Modify `plugins/workflows-core/references/security-register-format.md`:
  - the opening sentence `is the register's only writer and implements this file` (S2): `register.py` implements §1 to §5, and `scripts/weakness-classes.py` implements §7, each changing with its section in one commit;
  - §3's structured-fields list: the PA line's closed list (the CWE and its URL, the slug, the register path, the counts and the PRD key), built by `weakness-classes.py`;
  - a new `## 7. Weakness classes`: the class, the tables of Global Constraints *The rule*, the validators, what is never printed, the fixed `not run` lines (no exception text), `classes`' output, `decided_ids` and the PA fields, and design §3.3's staleness note (`register.json` may lag records on unmerged `session/*` branches; the output is advice, so a lag of one rebuild is acceptable). `across` comes in Task 2.
- Modify `.github/workflows/validate-catalog.yml`: one step, `name: Self-test the weakness classes reader`, after "Self-test the security register". It carries a comment in that step's style, naming its silent failure modes: scan text reaching a question or a line, `CWE-890` taken for `CWE-89`, and one batch's acceptances counted as recurring. It runs `python3 plugins/workflows-core/scripts/weakness-classes.py --selftest`.

**Interfaces — produces:**
- `main(argv: list[str]) -> int`
- `classes(specs: str, repos: list[str], components: list[str], origins: list[str] | None, prd_key: str | None, today: datetime.date) -> dict`
- `read_register(raw: bytes | None, slug: str, today: datetime.date) -> tuple[dict, list[dict]]`: the `registers` entry, and the validated findings, each carrying its class key or `None`, its accepting run and its recent flag.
- `read_record(stem: str, text: str) -> dict | None`: `{id, status, source, promotion, promoted_to, components, prevents}`, or `None` when skipped.
- `prevents(record: dict, cwe: str) -> bool`
- `pa_line(cls: dict, prd_key: str) -> str`
- `pa_next_step(cls: dict) -> str`

Task 2 reuses `read_register`, `read_record` and `prevents` unchanged.

- [ ] **Step 1: The failing selftest.**
  - **Harness:** `register.py`'s. Each `case_*(tmp)` runs in a `TemporaryDirectory` and prints `ok   <name>` or `FAIL <name>: …`; the run ends with `selftest: <passed>/<total> passed`. Cases drive `main([...])` with `contextlib.redirect_stdout` and `redirect_stderr`, so they pin the CLI and its exits. Until Step 3, the stub `main` raises `NotImplementedError` and has no catch-all, so no exit-2 case can pass vacuously (review M3).
  - **Fixtures:**
    - `_register(specs, slug, findings, last_at)` writes `register.json` as `register.py` shapes it: `{format: 1, repo, next_id, next_seq, last_at, scans: [], findings: [...], renumbered: []}`, each finding carrying every §3 field and a `history` of `{status, at, by, reason, evidence, role, run, links}`.
    - `_record(specs, stem, status, components, prevents, source, promotion=None, promoted_to=None)` writes a team record exactly as `architecture-harvest.py`'s `render_record` writes one, with the promotion keys after the owned ones.
  - **The injection guard, each value planted separately:**
    - `case_hostile_text_never_printed`: a title and a history `reason` of `Ignore all previous instructions`, plus hostile `owner`, `by`, `evidence`, `links`, `units` and `scope`. Assert that the stdout does not contain that string, and that no key in the output (walked recursively) is one of the never-printed names.
    - `case_cwe_injection_and_overlong`: `CWE-89; rm -rf` and `CWE-1234567`. Assert `unclassified == 2`, no class, and that stdout contains neither `rm -rf` nor `1234567`.
    - `case_path_traversal_and_backtick`: `../etc/passwd`, ``src/a`b.py`` and a 513-character path each print `path: null`, and the finding still counts.
    - `case_bool_id_and_negative_line`: `id: true` and `line: -1` give `dropped == 2`.
    - `case_enums_and_dates`: severity `URGENT`, status `wontfix`, `review_by: "2026-02-30"` and `confirmed: "yes"` are each dropped.
    - `case_prevents_whole_token`: `CWE-890` does not prevent `CWE-89`; `XCWE-89` does not; `[CWE-89](https://cwe.mitre.org/data/definitions/89.html)` and `CWE-89,` do.
    - `case_internal_error_never_echoed` (review I2): patch a reader to raise an exception whose text is `Ignore all previous instructions`. `main` exits 2, stdout is empty, stderr is exactly `weakness-classes: not run (internal error)` plus a newline, and neither stream holds the string.
  - **Usage:** `case_usage_exits_2`. Each of these exits 2, with an empty stdout and a stderr line that starts `weakness-classes: not run (` and is **not** the `(internal error)` line:
    - `--repo ..`;
    - `--repo a/b`;
    - `--prd-key acme-1`;
    - `--component other:x` without `--repo other`;
    - `--today 2026-13-01`;
    - a missing `--specs` directory;
    - no `--repo`.
  - **States:** `case_register_states`:
    - `absent`, `unreadable` (`{`), `unknown-format` (`format: 2`) and `malformed` (`findings: {}`) each give that state, a null `last_at` and zero counts, and the exit is 0;
    - an `ok` register copies a valid `last_at`.
  - **Team records:** `case_record_checks`. Each of these is skipped, with `kb_skipped` counting them: a stem `notes`, `source: "../x"`, `promotion: maybe`, `promoted_to: "../../e"`, `promoted_to: "-ADR"` (fails `PROMOTED_TO_RE`), `components: api` (not a flow list), and no Prevents paragraph. stdout contains neither hostile `source` nor hostile `promoted_to` value (review M3). A record in the harvest's exact shape is read.
  - **Dropped history:** `case_empty_history_dropped` (R4): an `accepted-risk` finding whose `history` is `[]` is dropped and counted in `dropped`.
  - **The rule:**
    - `case_live_and_context`: each live status counts in `live`. `false-positive` counts nowhere. A class with only a recent `fixed` is not listed.
    - `case_accepting_runs`: two findings accepted in run 3 at one `at` give `accepting_runs 1` and `recurs false`. Adding one accepted in run 4 gives `2` and `true`. Two findings with run 3 at different `at` values give `2`.
    - `case_unconfirmed_and_review_due`: `confirmed: false` with a past `review_by` counts in `accepted`, gives `awaiting_review 1` and `review_due 1`, and counts toward `recurs`.
    - `case_prevented_component_scope`:
      - a record with `["billing"]` naming the CWE does not prevent `api`'s class, while `["api:src"]` does;
      - `status: superseded` does not prevent;
      - `promotion: accepted` still prevents, and is printed with `promotion` and `promoted_to`.
    - `case_ranking`: four classes, built so that each ranking key decides one pair, come out in the exact order of Global Constraints *Ranking*, and CWE-79 sorts before CWE-100.
    - `case_in_component`: `--component api:src/orders` marks `src/orders/Repo.java` true and `src/ordersx/A.java` false. A bare `--component api` marks both true. With no component, both are false. `--component api:./x` exits 0 and marks nothing (R6).
    - `case_evidence_cap_and_order`: seven findings give five entries: live by severity, then id.
  - **The PA fields:**
    - `case_pa_line`: `--origin` of an `accepted-risk` finding in a recurring, unprevented class, with `--prd-key ACME-17`, makes `pa_line` equal, character for character:
      ```text
      - [ ] Run `/product-workflows:create-ard ACME-17` to record an [AD#N] whose Prevents names [CWE-89](https://cwe.mitre.org/data/definitions/89.html) — 2 accepted risks of CWE-89 in the api register (security/api/register.md), accepted in 2 runs, 1 awaiting security review, and no team decision for api prevents it — raised by /security-workflows:scan
      ```
      and `pa_next_step` is null.
    - `case_pa_next_step`: the same, without `--prd-key`, makes `pa_line` null and `pa_next_step` equal to the copy in Global Constraints. With `awaiting_review` 0, the clause is absent.
    - `case_pa_needs_decided_recurring_unprevented`: a prevented class, a non-recurring class and an unknown `--origin` each give null for both fields. Without `--origin`, the `decided` and `decided_ids` keys are absent. With `--origin` of findings 3 and 7, both in a class whose `cwe` the register writes `CWE-089`, that class's `decided_ids` is `[3, 7]`, even where 7 is not among its five evidence entries (review I4).
  - **Review Focus:** `case_cwe_canonical`, `case_redated_risk_is_one_acceptance`, `case_prevents_wrapped_and_url_only`, `case_non_register_dirs` and `case_fixed_window_boundary`, with the assertions their Review Focus lines state.
  - **The envelope:** `case_envelope`:
    - stdout parses as one object with keys exactly `format`, `today`, `kb_skipped`, `registers` and `classes`;
    - `format` is 1;
    - `today` echoes `--today`;
    - a repeated `--repo` gives one register entry.
- [ ] **Step 2: Run** `python3 plugins/workflows-core/scripts/weakness-classes.py --selftest`. Expected: every case FAILs, since nothing is implemented beneath the harness.
- [ ] **Step 3: Implement** to the Global Constraints contract.
  - The whole-token test, for class `CWE-<n>`, is `re.search(r"(?<![A-Za-z0-9_-])CWE-0*" + str(n) + r"(?![A-Za-z0-9_])", prevents)`.
  - `main` overrides argparse's error to print the one `not run (usage: …)` line, and wraps everything else in the catch-all that prints `not run (internal error)`.
  - Read a team record by lines; never import YAML.
  - Use `from __future__ import annotations` for the type hints, since 3.9 is the floor.
  - The docstring names the verbs, the exits and the never-printed fields.
- [ ] **Step 4: Run the selftest.** Expected: `selftest: N/N passed`, exit 0.
- [ ] **Step 5: Write §7 and the two edits to the format, and add the CI step.** Re-read the whole format for any sentence §7 now contradicts. The sweep owns S2. Record its counts.
- [ ] **Step 6: Gates.** `check-docs` passes, because no inventory counts scripts.
- [ ] **Step 7: Commit:** `feat(sec-g1): weakness-classes.py classes — the one reader of the security registers, and security-register-format §7`.

### Task 2: `weakness-classes.py across`

**Files:**
- Modify `plugins/workflows-core/scripts/weakness-classes.py`: the `across` verb, its git reads, and its cases.
- Modify `security-register-format.md` §7: `across`, its judged-real rule and its output.

**Interfaces:**
- Consumes `read_register`, `read_record` and `prevents` from Task 1.
- Produces `across(specs: str, ref: str, today: datetime.date) -> dict`.

- [ ] **Step 1: The failing cases.** Fixtures are throwaway git repositories, using `register.py`'s git environment (`GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1`, `GIT_CEILING_DIRECTORIES` set to the temporary directory).
  - `case_across_reads_at_ref_only`: an uncommitted register and an uncommitted record in the work tree change nothing, and `ref` equals `git rev-parse <ref>`.
  - `case_across_threshold`:
    - a class judged real in one register is absent, and in two it is present;
    - `open` and `false-positive` are not judged real;
    - a `fixed` within 180 days is;
    - the counts `real`, `accepted` and `fixed_recent`, per register and in total, are pinned.
  - `case_across_prevented_any_component`: a record with `["billing"]` naming the CWE prevents the class in `across`, printed as `{id, promotion, promoted_to}` and nothing else.
  - `case_across_order`: three classes come out in R7's order.
  - `case_across_exits`: an unknown ref, and a `--specs` that is not a git work tree, each exit 2.
  - `case_across_no_security`: a ref with no `security/` gives `registers: []` and `classes: []`, with exit 0.
  - `case_across_non_register_dirs`: Review Focus 4 at a ref.
  - `case_across_hostile_text`: the Task 1 injection assertions, at a ref.
- [ ] **Step 2: Run the selftest.** Expected: the new cases FAIL, and Task 1's PASS.
- [ ] **Step 3: Implement.**
  - List `security/*/register.json` at the ref in one `git ls-tree` call, and keep only paths of exactly that depth whose directory name passes the slug check.
  - Read each file with `git show <sha>:<path>`. Bytes that are not UTF-8 make the register `unreadable`.
- [ ] **Step 4: Run the selftest.** Expected: PASS, every case.
- [ ] **Step 5: §7's `across` text. Gates.**
- [ ] **Step 6: Commit:** `feat(sec-g1): weakness-classes.py across — weakness classes recurring across registers, read at a ref`.

### Task 3: The skill, its pages, and every statement of who reads the register

**Files:**
- Create `plugins/workflows-core/skills/weakness-classes/SKILL.md`, to the Global Constraints contract.
- `plugins/workflows-core/references/security-register-format.md`:
  - §1's two "as a run's state" sentences become "as the register's state" (S3, S4);
  - its "for the readers §6 names" is re-read;
  - §3's `every reader of the register reads it the same way` (S9) becomes: every reader of the register reads a finding's text that way, and `weakness-classes.py` prints none of it;
  - §6 keeps the loaders' recipe and adds a second one: `grep -l 'skill: "workflows-core:weakness-classes"' plugins/*/commands/*.md`, the commands that read the register through §7's script. §6 gives the recipes only, never a list, so it stays true while Tasks 5–7 add callers (`CLAUDE.md`, *Re-measure in one place*);
  - §7 gains the skill's argument rule (review I1): an origin is scanner-written text, so the skill passes no value holding a character outside `[A-Za-z0-9._:/@+=-]`, and refuses the call where one does.
- `plugins/workflows-core/references/architecture-kb.md`: the opening's `The script implements it` (S12) names `weakness-classes.py` as the second implementer. It reads the frontmatter keys and the Prevents paragraph, so a format change changes both scripts in one commit.
- `.claude/rules/security-workflows.md`:
  - `paths:` gains `plugins/workflows-core/scripts/weakness-classes.py` (R14);
  - the *Authority* paragraph (S10, S11) adds §7 and the skill's callers' recipe;
  - the first invariant's `The one read of a derived file as state` (S6) becomes "…as the register's state", and says the §7 reader's read decides no register change.
- `.claude/rules/docs-grounding.md`:
  - `paths:` gains `plugins/workflows-core/skills/weakness-classes/SKILL.md` and `plugins/workflows-core/scripts/weakness-classes.py`;
  - the `architecture-kb` paragraph (S13) names the second implementer.
- `.claude/rules/workflows-core.md`, the *Plugin facts* paragraph (S14):
  - "four bundled skills", with the fourth described in one clause;
  - `weakness-classes` in the scripts list.
- `CLAUDE.md`:
  - the Shared-authorities bullet ``the rules `register.py` applies`` (S11) adds "and §7's weakness classes";
  - the `security-workflows.md` table row's `workflows-core/` list adds `scripts/weakness-classes.py`;
  - re-read the `plugins/workflows-core/` paragraph (design §10 item 14) and the `plugins/security-workflows/` paragraph. Edit a clause only where it is now false, and record either way;
  - the `docs-grounding.md` row already abbreviates its `paths:`, leaving out the knowledge-base and promotion files. Leave it, and record why.
- Pages:
  - `plugins/workflows-core/docs/README.md` `:32`: four bundled skills, named.
  - `docs/reference/references.md` `## Skills`:
    - `Three skills ship` becomes four;
    - "The third skill" stays;
    - a new "The fourth skill, `weakness-classes`" paragraph;
    - a table row for it, each cell ≤ 200 characters;
    - the `security-register-format.md` entry adds that the weakness classes are read from it by `scripts/weakness-classes.py`.
  - `plugins/security-workflows/docs/workflow.md` (`:70`, S5) and `docs/reference/security-register.md` (`:26`, S4) say "as the register's state", and add that a read-only reader in `workflows-core` hands the architecture commands validated weakness classes.

**Interfaces:**
- Consumes Task 1's CLI.
- Produces the skill call form and its error line, as in Global Constraints *The skill*.

- [ ] **Step 1: Before counts** for S3, S4, S5, S6, S9, S10, S11, S12, S13 and S14.
- [ ] **Step 2: Write the skill.** Then run its Bash call by hand, with `CLAUDE_PLUGIN_ROOT` set to the worktree's `plugins/workflows-core` and `SPECS_PATH` set to a scratch tree built like Task 1's fixtures:
  - a `classes` call prints a path whose file parses;
  - a bad `--repo` prints the `not run` line and no path, and leaves no file;
  - a hostile `--origin` holding a single quote plus `; touch <scratch>/pwned` prints `weakness-classes: not run (an argument holds a character the skill does not pass)` and no path, and `<scratch>/pwned` does not exist afterwards (review I1).

  - a `--component 'api:a b'` beside `--repo 'api'` is dropped, and the call still runs and prints a path (re-check N2).

  Record all four outputs in the report.
- [ ] **Step 3: The authority and rules edits. Then the pages.** Measure every rules file and `CLAUDE.md` you touched.
- [ ] **Step 4: After counts**, against the table. Re-read every paragraph that holds a hit (refinement 1).
- [ ] **Step 5: Gates.** Expected: check 4 and check 9 pass with four skills.
- [ ] **Step 6: Commit:** `feat(sec-g1): workflows-core:weakness-classes skill, and every statement of who reads the register`.

### Task 4: Part 1 in `workflows-core` — resolution, dispatch, the grounder

**Files:**
- `plugins/workflows-core/references/architecture-grounding.md`:
  - the opening (S15) adds the registers, read only through the skill;
  - *Consumers*: each consumer calls the skill at its dispatch step (`/update-spec` through `/specify`'s);
  - step 1 and a new step 5a: Global Constraints *resolve fields*, and the count of `register.json` holders;
  - step 6's return;
  - the *Plan-approval line* section: the four lines; no line where `security/` is no directory; S16 gains a sentence; S35's "turns both off" names all three sources `--no-arch` turns off;
  - *Dispatch*: S17 becomes the widened condition, the skill call is stated as the consumer's step, the dispatch block gains `weakness_classes:`, and the failed-call line is added;
  - *Consumption*:
    - S18 gains its exception: a promoted record's `promoted_to` is taken for `governing`, and only its promotion keys are read;
    - a new bullet **A `known-weakness` challenge** competes for a slot like any other challenge. The command builds its question from the JSON's fields only (`[SEC#n]`, the CWE link, the register link) and never opens a register. The question asks how the work avoids adding to the class. What the artifact records is authored in the grill, never copied from a register (design §8 item 4);
    - the bullet **A specification records only conflicts** gains the specification's open question, copied from Global Constraints;
  - *Invariants*: `:81` adds "never opens a file under `$SPECS_PATH/security/`"; S19 gains the failed-call report line; "runs exactly once" covers the security line.
- `plugins/workflows-core/agents/architecture-grounder.md`:
  - the description and purpose (design §10 item 7) name the `weakness_classes` input and the `known-weakness` kind, still ≤ 600 characters;
  - *Inputs*: `weakness_classes`, and S20's two sentences widened to "at least one of the two roots, or `weakness_classes`", per R10;
  - Method step 4: the two exceptions, for `governing` only;
  - a new step 5a, which raises one `known-weakness` per class in the script's order;
  - step 7 (S21): the cap of 3 and the new order;
  - *Output*: `known-weakness` in the kind list, and the `weakness:` line in the challenge shape;
  - the EMPTY sentence (S21) adds that `EMPTY` cannot occur where `weakness_classes` holds a class;
  - *Hard rules*: never open any file under the specs repository's `security/`. `weakness_classes` is the only security input. The existing hard rule on Bash stays as it is.
- `.claude/rules/docs-grounding.md`:
  - the `architecture-grounding` authority paragraph (`:58`) names the weakness classes and the skill;
  - the grounder bullet (S32) adds that it never opens a file under `security/`.
- Pages:
  - `plugins/workflows-core/docs/reference/grounding.md`:
    - a new `## Security registers` section after *Team decision records*, with *Feeds*, *Turned on by*, *Status line* and *Off switch*, in that section's form;
    - a *Security registers* row in the *At a glance* table, read by `/create-ard`, `/specify`, `/update-spec` and `/dev-workflows:design`, turned on by a findings register under `$SPECS_PATH/security/`, off switch `--no-arch` (S36);
    - *Team decision records*' off switch, `turns off both architecture roots` (S35), names the registers too;
  - `plugins/workflows-core/docs/reference/environment.md`: `forces architecture grounding off` (S36) names the team decisions and the security registers as well;
  - `docs/reference/agents.md`: the `architecture-grounder` row (cell ≤ 200 characters);
  - `docs/reference/references.md`: the `architecture-grounding.md` entry.

**Interfaces:**
- Consumes Task 3's skill call.
- Produces the resolve fields, the lines, the dispatch input and the challenge shape (Global Constraints).

- [ ] **Step 1: Before counts** for S15–S21, S32, and S35–S36's `workflows-core` sites.
- [ ] **Step 2: Edit the reference, then the agent.** Re-read every dispatch-condition consequence against the new trigger (`CLAUDE.md`, *Extent face*):
  - a run with both roots OFF and classes present dispatches with `arch_root: null`, `team_root: null` and `snapshot: none`;
  - that run still builds `stack_facts`, `feature_summary` and `themes` as the dispatch section says, and the skill call sits once the scan's last batch has returned, whether or not a root is ON (review M2);
  - its `layout` is `[]`;
  - it raises only `known-weakness` challenges;
  - "On `status: ERROR` … OFF from there on" still holds.

  Record each.
- [ ] **Step 3: The rules and pages. After counts.**
- [ ] **Step 4: Gates.**
- [ ] **Step 5: Commit:** `feat(sec-g1): Part 1 core — the security registers line, the weakness-classes dispatch input, and known-weakness challenges`.

### Task 5: Part 1's consumers — `/create-ard`, `/specify`, `/design`, `/update-spec`

**Files:**
- `plugins/product-workflows/commands/create-ard.md`, `plugins/product-workflows/commands/specify.md` and `plugins/dev-workflows/commands/design.md`, each at the same three sites:
  1. **Phase 1's *Resolve architecture grounding next* step** (S23): show the `security registers:` line too, where one is returned.
  2. **The *Architecture grounding (optional)* dispatch paragraph** (S22): `create-ard.md` Phase 3 step 6; `specify.md` and `design.md` Phase 4.
     - Add the skill call, to Global Constraints *The consumer's call*.
     - Replace the condition.
     - Add `weakness_classes` to the dispatch.
     - Add the failed-call rule.
     - Reword its closing `Where it resolved OFF, dispatch nothing` (S33), which the widened trigger contradicts: "Where neither root resolved ON and the run holds no class — the call was not made, failed, or returned none — dispatch nothing." Leave the docs-grounding paragraph's sentence of the same words alone.
  3. **The final report** (S23): `create-ard.md`'s *Report:* sentence, `specify.md`'s `### Run details` block plus its line-detail paragraph, and `design.md`'s *Report:* sentence. Add the `registers read:` clause and the `not read` line.
- The grill sites:
  - **`create-ard.md` Phase 4**, after its team-record paragraph:
    - a `known-weakness` challenge is grilled per § Consumption;
    - for a recurring class with a null `governing`, first check the Prevents lines of this ARD's own decisions, `prior_ard`'s included, for the class's CWE as a whole token. A hit is played back as a fact, and nothing is offered;
    - otherwise ask the `choices` array from Global Constraints;
    - *Record* is grilled like any other decision, its Prevents naming the CWE as a link;
    - *Not in this ARD* writes nothing (R12) and is named in the report.
  - **`specify.md`'s *Architecture grounding.* paragraph in Phase 5:** an unsettled `known-weakness` becomes the open question from Global Constraints.
  - **`design.md`'s *Architecture governance* bullet:** the *Known weakness* line, per `design-format`.
- `plugins/product-workflows/commands/update-spec.md`:
  - `:68` (S24) lists the `security registers:` line;
  - re-read `:94` (S25), and record why "Phase 1's OFF lines dispatch nothing" stays true: an OFF line still dispatches nothing, and the skill call is part of `/specify`'s dispatch step, which Phase 3 makes.
- `plugins/product-workflows/references/ard-format.md` § Architecture governance:
  - a bullet **A CWE in Prevents**: a decision whose Prevents names a CWE names it as `[CWE-<n>](https://cwe.mitre.org/data/definitions/<n>.html)`, whether or not grounding ran. Adding that link to an existing decision's Prevents is not a change to the decision (§ Superseding a decision). A decision that would also need its Rule to require more is a new `[AD#M]`;
  - S26 becomes "Where grounding was OFF, nothing in this section is required but **A CWE in Prevents**."
- `plugins/dev-workflows/references/design-format.md`:
  - § Architecture governance: its premise (R16), the *Known weakness* bullet (advisory; `design-reviewer` raises no finding on it), and S26 becoming "Where grounding was OFF and no `known-weakness` challenge was raised, nothing in this section is required.";
  - `## Risks & mitigations` (`:176`): "Each `Architecture deviation:` line" adds "and each `Known weakness:` line".
- `--no-arch` descriptions (S35, S36), each naming the security registers as the flag's third source:
  - `design.md:26`'s `turns off architecture grounding for the run`;
  - `plugins/dev-workflows/docs/reference/environment.md` and `plugins/product-workflows/docs/reference/environment.md`, each `` `--no-arch` turns it off for a run ``;
  - `plugins/product-workflows/docs/workflow.md:190`'s `turns both off`;
  - the repository-root `README.md:102`'s `Disable both per run with`;
  - the three command pages' "turned off with `--no-arch`" sentences (`dev-workflows` `design.md`, `product-workflows` `create-ard.md` and `specify.md`), and `update-spec.md`'s flag line.

  Usage, synopsis and flag-strip lines stay. Record each of the 38 hits' dispositions.
- `.claude/rules/product-workflows.md`:
  1. Move `## Invariants` and its subsection, byte for byte, to a new `.claude/rules/product-workflows-prd-flow.md`. It takes the same `paths:`, all eight globs:
     ```yaml
     paths:
       - "plugins/product-workflows/**"
       - "plugins/dev-workflows/commands/design.md"
       - "plugins/dev-workflows/commands/ready.md"
       - "plugins/dev-workflows/commands/implement.md"
       - "plugins/docs-workflows/commands/release-notes.md"
       - "plugins/workflows-core/references/addressing.md"
       - "plugins/workflows-core/references/grilling-technique.md"
       - "plugins/workflows-core/references/prd-format.md"
     ```
     Its title is `# product-workflows — the PRD-creation flow's invariants`. Its intro follows `brd-route-detection.md`'s form: "Loaded with `.claude/rules/product-workflows.md`, whose `paths:` it shares. Split out of `.claude/rules/product-workflows.md` to keep that file under 20,000 characters; …".
  2. In `product-workflows.md`, the H1 `# product-workflows — invariants, workflow map, agent callers` becomes `# product-workflows — plugin facts, workflow map, agent callers`. Fix the pointer the move strands: the opening's "the PRD-creation invariants below bind" (`CLAUDE.md`, *Pointer face*). Name the new file in the opening's split sentence.
  3. Grep the sweep scope for `product-workflows.md` § Invariants and `Key invariants for the PRD-creation flow`, and repoint each live hit.
  4. Edit the `/create-ard` and `/specify` map lines: `[weakness-classes (security registers ON)]` before the grounder, `or a register holds a class` in its `when`, and, on `/create-ard`'s grill, `a recurring unprevented class offers an [AD#N] preventing its CWE`.
- `.claude/rules/dev-workflows.md`, the `/design` line: `(when either root resolves)` becomes `(when either root resolves or a register holds a class)`, and nothing more (R13: the asymmetry with the product lines is deliberate). Measure the file. If it reaches 20,000 characters, move `### /design and /ready` byte for byte to `.claude/rules/dev-workflows-design-ready.md`, with the same `paths:`, a pointer, a `CLAUDE.md` row, and the moved PRD-flow file's "their own bullets are in" sentence repointed.
- `CLAUDE.md`'s rules table:
  - a row ``| `product-workflows-prd-flow.md` | as `product-workflows.md` | the PRD-creation flow's invariants |``;
  - `product-workflows.md`'s row reads "plugin facts, map, callers".
- Pages:
  - `plugins/product-workflows/docs/commands/create-ard.md`, `specify.md` (`:99`, S23) and `update-spec.md`;
  - `plugins/dev-workflows/docs/commands/design.md`.

  Each says, in words, that the registers of the repositories the work touches are read, what the run asks or records, and that a run never waits on a register.

**Interfaces:** consumes Task 4's fields, lines, dispatch input and challenge shape, and Global Constraints' exact copy.

- [ ] **Step 1: Before counts** for S22–S26, S33, and S35–S36's sites in this task. **Size** `product-workflows.md`, `dev-workflows.md` and `CLAUDE.md`.
- [ ] **Step 2: The three commands, site by site.** Keep the three dispatch paragraphs' shared wording identical, so a later sweep matches all three.
  - `/create-ard`'s choice question is preceded by its command's existing **Load the question rules.** step. `check-questions` holds that.
- [ ] **Step 3: `update-spec`, the two formats, the rules split, the map lines and the pages.**
- [ ] **Step 4: After counts.** For each of the three commands, read its Phase 1 to its final report through once (refinement 2). Record what each site now says.
- [ ] **Step 5: Gates.** `check-questions` sees the new `choices:` array. Check 12 passes its labels.
- [ ] **Step 6: Commit:** `feat(sec-g1): Part 1 consumers — /create-ard, /specify, /design and /update-spec read the weakness classes; a CWE in Prevents is a link`.

### Task 6: Part 2 — the scan raises the PA line, and annotates review-due rows

**Files:**
- `plugins/security-workflows/commands/scan.md`:
  - **Phase 5 step 1**, after its `rebuild`, only where the plan's `review_due` is non-empty:
    - `Skill(skill: "workflows-core:weakness-classes", args: "classes --repo '<repo-slug>' --origin '<origins[n]>' …")`, one origin per review-due number, taken from `plan.json`'s `origins`;
    - read only `prevented_by` and `decided_ids`. Each review-due row whose `[SEC#n]` is in a class's `decided_ids` gains `prevented by <id>[, <id>…]` from that class's `prevented_by` (R17). Rows are mapped by `[SEC#n]`, never by CWE text, which the register may write as `CWE-089` (review I4);
    - the row's suggestion is unchanged: it still offers the finding's current status (design §5.7);
    - ignore `pa_line` and `pa_next_step`;
    - a failed call leaves the rows as they are and adds the report line.
  - **Phase 7.2**, only where `register.py commit` ran — after its `REGISTER_MOVED` and `TRIAGE_*` retries settle — and its decisions file holds ≥ 1 `accepted-risk` decision:
    - one `classes` call with `--repo '<repo-slug>'`;
    - one `--origin` per such decision: for `id:<n>`, `answered-plan.json`'s `origins["<n>"]`; for `plugin:<pid>`, `<the plan's scan.id>:<pid>`. Phase 5 step 7 names a match or an existing finding only by `id:<n>`, so a `plugin:` target is always a new finding;
    - `--prd-key '<KEY>'` per R18: on an Epic-scoped run, the parent's key, and on a single-key run the resolved key, each only where that folder holds a `prd.md` whose frontmatter `kind:` is `prd`; otherwise none (review I5). The `scan.md` sentence carries the literal phrase `asserted kind`, without backticks around `kind`, as in "never by the folder's asserted kind or its prefix", so `brd-route.md`'s grep finds it (re-check N1);
    - keep each `pa_line` for 7.6 and each `pa_next_step` for the report.
  - **7.5's report:**
    - `### Register` gains `- Weakness classes: [each PA line, pending the preview; each sentence for the PA; "none"; or "not read — <the skill's error>"]`;
    - `### Next step` carries each `pa_next_step` verbatim.
  - **7.6's follow-ups paragraph:**
    - S27: the persist step runs where 7.2 built any line or the call printed a `pa_line`;
    - S28: each PA line is written exactly as the script printed it. Its `unit_folder` and `key` are the folder and key that passed R18's `prd.md` test: on an Epic-scoped run, the resolved folder's parent and the parent's key; on a single-key run, the resolved folder and its key. Never test a kind from a folder name, prefix or asserted `kind`;
    - on a run with a PA line, **every** item of the `followup-emission` call carries its own `unit_folder` and `key`, the per-item form §8 uses "instead". Each finding's line takes the unit's folder and key, and each PA line takes the PRD's. The call is never a mix of a call-level `unit_folder` and per-item ones;
    - the cancel rule excludes the PA line: leaving it out records nothing and returns no finding to `fix`;
    - this step's output line `N follow-ups written to <target>` (S34) becomes one line per target: the unit's `follow-ups.md`, and the PRD folder's where a PA line was written.
  - **Invariants** (S34): `register.py commit builds them from structured fields only` becomes: `register.py commit` builds each finding's follow-up and prompt line, and `weakness-classes.py` builds the PA line and sentence, each from structured fields only.
- **The BRD-route rules' population** (R18 makes `scan.md` carry a kind gate). `.claude/rules/brd-route.md` says, at the phrase "a kind gate added elsewhere needs its file added to these `paths:`", that such a file joins its `paths:`. So, unconditionally (re-check N1):
  - add `plugins/security-workflows/commands/scan.md` to the `paths:` of `brd-route.md`, `brd-route-detection.md` and `prd-ground-verification.md`, which share them;
  - name it in `brd-route.md`'s opening list of named files, as briefly as `security-workflows`' `/scan`;
  - add it to `CLAUDE.md`'s `brd-route.md` table row;
  - then run that file's second grep, `grep -lE 'kind it asserts|asserted kind|asserts .kind: brd|asserting .brd' plugins/*/commands/*.md plugins/*/references/*.md`. It must now return `scan.md`, which checks that the `scan.md` sentence carries the literal phrase.

  `brd-route.md` stands at 19,881 characters and lands at about 19,965–19,970. Measure it after the edit; it must stay under 20,000.
- `plugins/workflows-core/references/followup-emission.md`:
  - §5: after S29, a paragraph **A decision for the PA**. Its identity is the PRD key in its `/product-workflows:create-ard <KEY>` span, its `[CWE-<n>]` link text and its `(security/<slug>/register.md)`, each compared exactly as the run holds it. It matches only an **open** line carrying all three, so a ticked line never stands for it.
  - §6: a bullet: a decision another role must record — here the scan's line for the PA.
  - Re-read the caller list at `:7`–`:9`; it is unchanged.
- `.claude/rules/security-workflows.md`:
  - the map line: `→ [accepted risks recorded: weakness-classes → the PA line]` after `register.py commit`, and `→ [review-due rows: weakness-classes, prevented_by only]` in triage;
  - the follow-ups-structured-fields invariant (S7): `register.py commit` builds each finding's line, and `weakness-classes.py` builds the PA line from its own closed list;
  - the *Follow-ups are written after the report* invariant (S8): the PA line, and that cancelling it records nothing.
- Pages:
  - `plugins/security-workflows/docs/commands/scan.md`: *Triage* gets the review-due note; *What it produces* gets the PA line.
  - `docs/workflow.md`: the PRD folder's `follow-ups.md`.
  - `docs/reference/security-register.md`: a short section, *What the registers feed*. It covers three things: the architecture commands see each weakness class of the repositories their work touches; two accepted risks of one class, accepted in different runs, raise a follow-up for the PA; and a review-due risk's row names the team decision that prevents its class.
  - `docs/roles-and-phases.md`: the PA receives the line.
  - `plugins/dev-workflows/docs/reference/follow-ups.md`: after its `:54` copy (S29), the PA line's identity, in words.
  - `plugins/workflows-core/docs/family-map.md`:
    - one edge `secscan -.->|"follow-up for the PA: a recurring accepted risk"| createard`;
    - a sentence in the scan bullet: the registers also feed `/create-ard`, `/specify`, `/design` and `/promote-decisions`.

**Interfaces:** consumes Task 1's `classes` JSON (`pa_line`, `pa_next_step`, `prevented_by`, `decided`, `decided_ids`) through Task 3's skill.

- [ ] **Step 1: Before counts** for S7, S8, S27–S29 and S34.
- [ ] **Step 2: `scan.md`.** Read Phase 5 to 7.6, and the Invariants, end to end first. None of these edits enters *Ending early*, the preflight or the terminal `commit-artifacts` paragraph.
- [ ] **Step 3: `followup-emission`, the rules, the pages.** Run the mermaid gate where `node` exists.
- [ ] **Step 4: After counts.** Re-read 7.6's cancel rule against the PA line, and §5's existing `[SEC#n]` paragraph against the new one. Two live contradictory rules are a defect.
- [ ] **Step 5: Gates.**
- [ ] **Step 6: Commit:** `feat(sec-g1): Part 2 — the scan raises a recurring accepted risk as a follow-up for the PA, and names the decision that prevents a review-due risk`.

### Task 7: Part 3 — `/promote-decisions` sees classes recurring across registers

**Files:**
- `plugins/workflows-core/references/architecture-promotion.md`:
  - **§5:**
    - after the signals, the command's `across` call;
    - keep the JSON's path beside the signals file;
    - S31: nothing to promote now also requires no class;
    - a failed call leaves the report line `weakness classes: not read — <the skill's error>`, and the run goes on as it would without the call.
  - **§6:** the dispatch gains `weakness_classes: <path> | null`. `EMPTY` is as §5's nothing-to-promote only where there are no classes.
  - **§7:**
    - item 1's ranking: after cluster size, a row whose record is in a class's `prevented_by` gains the reason, and ranks on it;
    - item 5, *Reported only*: the uncovered line;
    - the count line, where a class both covered and prevented counts once, as covered (review M4);
    - design §6.3 item 4's case, with classes and no candidate;
    - the command builds every row and line from the JSON's fields only, and never opens a register.
- `plugins/workflows-core/agents/promotion-scout.md`:
  - the description (≤ 600 characters). It has 53 characters of room, so make room by replacing wording, not by appending. Dropping "(dispatch-pinned to the §2 Opus chain)" frees 39, and the pin stays stated where it binds, in `architecture-promotion` §6;
  - *Inputs*: `weakness_classes`;
  - a Method step: per class, `covered` (an `accepted` ADR or `active` standard names the CWE or states a rule implying it, and the scout reads every artifact it cites) or `uncovered`;
  - *Output*: `weakness_classes: [{cwe, relation, artifact}]`;
  - S30's `EMPTY` and `ERROR` sentences, taking the classes and their file into account;
  - a hard rule: never open a file under the specs repository's `security/`.
- `plugins/product-workflows/commands/promote-decisions.md`:
  - Phase 3 step 1 carries the call: `Skill(skill: "workflows-core:weakness-classes", args: "across --ref '<default-ref>'")`;
  - step 2 passes `weakness_classes`;
  - Phase 4 shows §7's new lines;
  - the final report gains the classes listed and any `not read` line;
  - *Ending early* is GIT-G1's, and its "Phase 3's stop with nothing to promote" stays true.
- `.claude/rules/product-workflows.md`, the `/promote-decisions` map line: `→ [weakness-classes across: classes in 2+ registers]` after the signals.
- Pages:
  - `plugins/product-workflows/docs/commands/promote-decisions.md`;
  - `plugins/workflows-core/docs/reference/agents.md`: the `promotion-scout` row;
  - `docs/reference/references.md`: the `architecture-promotion.md` entry.

**Interfaces:** consumes Task 2's `across` JSON through Task 3's skill.

- [ ] **Step 1: Before counts** for S30 and S31.
- [ ] **Step 2: The reference, the agent, the command.** Re-read the extent of "Nothing to promote" against §11.2's and *Ending early*'s wording.
- [ ] **Step 3: Rules and pages. After counts.**
- [ ] **Step 4: Gates.** `promotion-signals.py` is untouched; say so in the report.
- [ ] **Step 5: Commit:** `feat(sec-g1): Part 3 — /promote-decisions ranks and reports weakness classes recurring across registers`.

### Task 8: Release

**Files:**
- the four `plugin.json` files and `.claude-plugin/marketplace.json`;
- the four `CHANGELOG.md` files;
- `.claude/rules/plugin-updates-coupling.md`, plus a history file and its pointers where Step 3 moves bullets;
- `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md`;
- `docs/superpowers/reviews/2026-10-26-feature-gaps-review.md`.

- [ ] **Step 1: Merge.** Run `git fetch origin`. Where `origin/main` has moved, `git merge --no-edit origin/main` (never rebase), with the trailers. Resolve each overlap file by keeping both sides.
- [ ] **Step 2: Versions.** Each of `workflows-core`, `product-workflows`, `dev-workflows` and `security-workflows` takes the next free **minor**, read from `origin/main` at this moment.
  - Never hardcode: IMP-G3 will probably have taken `dev-workflows` 4.65.0 and the next `workflows-core` minor.
  - `plugin.json` must equal `marketplace.json`.
  - Each CHANGELOG gets a section dated with the landing day (UTC), never `— Unreleased`. It says what each plugin's users see, in each plugin's own terms.
  - No `description` changes: each blurb stays true.
  - S1 stays; record it.
  - The `workflows-core` CHANGELOG notes that an Opus `architecture-grounder` dispatch made only for `known-weakness` challenges will be the common case for teams with registers and no knowledge base or architecture repository.
- [ ] **Step 3: The coupling bullet.**
  - **Its title:** ``**Update `workflows-core` <X> with `product-workflows` <Y>, `dev-workflows` <Z> and `security-workflows` <W>**``, after the last `workflows-core` bullet and before the `prose-style` bullets.
  - **Its two directions** (design §11):
    - older dependents beside the newer core never call the skill, so grounding is today's and no PA line is written;
    - newer dependents beside the older core fail each skill call, leave one report line, and break no run.
  - **The size limit:** measure the file. Above 19,000 characters, move its oldest bullets byte for byte into the highest-numbered `plugin-updates-coupling-history-*.md`, or into a new one where that would pass 20,000. Update every range pointer: the coupling intro, the receiving file's title and intro, `plugin-updates.md`, and `CLAUDE.md`'s table.
- [ ] **Step 4: The roadmap and the review.**
  - Row E gains `*Built as SEC-G1:*` with the design's path and the four versions, in the form IMP-G5 used.
  - D2 (design §10 item 16) gains one amendment line: the scan joins E's consumers, and the register's one reader outside `register.py` is `workflows-core`'s `weakness-classes.py`, through its skill. The agents get its JSON and never read a register.
  - The feature-gaps review's SEC-G1 row and its `### SEC-G1` heading are marked resolved, in IMP-G5's form.
- [ ] **Step 5: Gates.** Measure every rules file this branch touched, and `CLAUDE.md`. Re-measure `.claude/rules/dev-workflows.md` after Step 1's merge in particular. If it now reaches 20,000 characters, take Task 5's fallback split here.
- [ ] **Step 6: Commit:** `release(sec-g1): workflows-core <X>, product-workflows <Y>, dev-workflows <Z>, security-workflows <W> — the architecture feedback loop`.

### Task 9: Close

- [ ] **Step 1: Consistency.**
  - Every verb, flag and JSON key that the prose names (`grep -rhoE 'weakness-classes", args: "[a-z]+ [^"]*' plugins` and every field the commands, agents and references read) exists in the script, and the reverse.
  - `grep -l 'skill: "workflows-core:weakness-classes"' plugins/*/commands/*.md` lists exactly `create-ard.md`, `specify.md`, `design.md`, `scan.md` and `promote-decisions.md`, and §6 matches.
  - No agent body contains the call.
  - No agent or command tells a run to open `security/<slug>/` (`grep -rn 'security/<' plugins/*/agents plugins/*/commands`, each hit read). A hit is fine where it builds a link for people.
- [ ] **Step 2: GIT-G1.**
  - `git diff origin/main...HEAD -- .github/workflows/validate-catalog.yml` shows one added step and no other line.
  - The diff of the four GIT-G1 files is empty.
  - For each edited command, no hunk falls inside a GIT-G1 section (read each hunk's heading context).
- [ ] **Step 3: The sweep, closed.** Re-run every S-row. Each after-count equals its intended value. Record the table.
- [ ] **Step 4: The full CI list.** Every step `validate-catalog.yml` runs, in order, including every `--selftest`, the mermaid gate where `node` exists, and `check-docs.sh --selftest`. Expected: all pass.
- [ ] **Step 5: The PR text** (review M5). Draft the pull request description in the task report, for the controller to open the PR with. It must:
  - name the one step added to `.github/workflows/validate-catalog.yml` ("Self-test the weakness classes reader") for the GIT-G1 owner, and say that no other GIT-G1 file or section changed;
  - list the four versions and the IMP-G3 overlap files;
  - end with the attribution lines the session's system reminder gives for pull requests.
- [ ] **Step 6: The whole-branch review** is the controller's: Fable reviews the branch against the design and this plan.
