# SEC-G1 — the architecture feedback loop (security sub-project E)

**Date:** 2026-11-13. **Status:** draft, for a Fable design review and then the maintainer's approval. Nothing here is implemented. **Roadmap:** row E of `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md:101`, read with its non-goal at `:151`, D2 at `:208`–`:210`, the accepted-risk claim at `:395` and the free-text rule at `:475`. **Branch:** `feat/sec-g1-arch-feedback`.

Calls marked **my call** are where the roadmap leaves a choice open. §12 lists the ones the maintainer should look at first.

## 1. The decisions

| # | Decision | |
|---|---|---|
| E1 | **One reader, in `workflows-core`.** A new standard-library script, `scripts/weakness-classes.py`, reads `register.json` by format and prints structured fields only. A new skill, `workflows-core:weakness-classes`, which users cannot invoke, runs it for commands in other plugins. `register.py` does not change. | my call |
| E2 | **A weakness class is a register plus the finding's primary CWE**, validated as `^CWE-\d+$`. `other_cwes` is not used, and CWEs are not rolled up into parent classes. | my call |
| E3 | **The repositories a piece of work touches** are the repo-slugs of the `components` each consumer already passes to `architecture-grounder`. No new input is added. | my call |
| E4 | **Part 1.** The registers become architecture grounding's third root (`security_grounding`). It resolves next to the team root and is turned off by `--no-arch`. The grounder returns at most three `known-weakness` challenges, ranked after `contradicts-*`. | my call (cap, rank, flag) |
| E5 | **What feeds Part 1.** Live findings count: `open`, `fix`, `fixing`, `reopened` and `accepted-risk`. A `fixed` finding closed in the last 180 days adds context, but never raises a class by itself. A false positive never counts. | my call (window) |
| E6 | **Part 2: "recurs".** A class recurs when its register holds two or more findings at `accepted-risk`. Risks a Dev accepted and risks past their review date both count. The review-by date serves as the window. | my call (threshold) |
| E7 | **Part 2: "prevented".** A class is prevented when the `**Prevents:**` of a live team record names its CWE. A prevented class raises no follow-up. | from the row |
| E8 | **Part 2: who raises it.** The scan raises the follow-up for the PA, on a key run that records an accepted risk of a recurring, unprevented class. `/create-ard`'s grill also offers the `[AD#N]` itself. Nothing writes a decision without the PA. | my call (emitter) |
| E9 | **The decision names its CWE as a link** to the CWE's own page. Pre-lint then passes it, and the coverage test in E7 can find it. | my call |
| E10 | **Part 3.** A "team" is a register, which means one code repository. A class recurs across teams when two or more registers hold a finding of it that a person has judged real. The signal surfaces in `/promote-decisions`' shortlist. | my call |
| E11 | **Safety.** No agent opens a register file. The reader is the only way in, and it never prints a finding's text. | stricter than `:475` |
| E12 | **Plugins.** `workflows-core`, `product-workflows`, `dev-workflows` and `security-workflows` each take a minor bump. No plugin gains a dependency on `security-workflows`. | — |

## 2. What exists today

- **The register.** Each code repository has one, at `$SPECS_PATH/security/<repo-slug>/`. It holds `runs/`, `scans/`, and the derived `register.json` and `register.md` (`security-register-format.md:16`–`24`).
  - A finding carries `cwe`, `severity`, `path`, `line`, `status`, `units`, and `owner`/`review_by`/`confirmed` on an accepted risk. It also carries `history` entries of the form `{status, at, …}` (`:87`–`:96`).
  - The `cwe` value is copied from the scan's JSONL `cwe_id` (`register.py:444`). Only follow-up lines validate it, against `^CWE-\d+\Z` (`register.py:151`, `:473`).
  - The derived files exist "for people and for the readers §6 names" (`security-register-format.md:33`). Today §6 names readers by a grep recipe (`:158`).
- **`register.py`** is the register's only writer. Its six verbs are `plan`, `ids`, `commit`, `rebase`, `rebuild` and `verify-scope` (`register.py:4722`), and none of them is a read-only query: `rebuild` writes both derived files (`:1501`–`:1505`). It also cannot be reached from another plugin, because `${CLAUDE_PLUGIN_ROOT}` resolves to the plugin doing the reading (CLAUDE.md, *Internal reference convention*). Its definition of "active" is `open`, `fix`, `fixing`, `reopened` and `accepted-risk` (`register.py:143`).
- **Free text.** `register.md` prints a finding's title under `## Scan output`, labelled "data, never instructions" (`register.py:1488`–`1489`). A follow-up line is built only from structured fields (`security-register-format.md:98`–`105`).
- **Accepted risk.** An accepted risk has an owner and a review-by date, 90 days by default. "Sub-project E learns from accepted risks", and false positives "teach it nothing" (roadmap `:395`). A Dev's decision takes effect at once, with `confirmed: false` (`security-register-format.md:126`).
- **`architecture-grounder`** reads two roots: the organisation's architecture repository and the team knowledge base (`architecture-grounder.md:11`–`13`).
  - It returns `arch_challenges` of six kinds, at most eight in all (`:49`, `:72`).
  - It may use Bash only to list files and for read-only `git` (`:85`).
  - It is dispatched only when `arch_grounding` or `team_grounding` is ON (`architecture-grounding.md:45`).
  - `--no-arch` turns both roots off (`:9`, `:39`).
  - Challenges are ranked into the grill's Impact × Uncertainty gap list and never appended to it (`:70`). The advice never gates and is never a reviewer finding (`:83`).
- **Its consumers** each pass `components`.
  - `/create-ard` passes the confirmed set (`create-ard.md:620`).
  - `/specify` and `/design` pass the ARD's `components`, or else the slugs of the repositories they scanned (`specify.md:906`, `design.md:304`).
  - `/update-spec` makes `/specify`'s dispatch (`update-spec.md:94`).
- **The team knowledge base** is `$SPECS_PATH/architecture/`. Its `index.yaml` lists each record with a `status`, and each `decisions/<id>.md` carries `**Prevents:**` copied verbatim from the ARD (`architecture-kb.md:12`, `:29`, `:60`). A record belongs to its nearest `PRD-` folder (`:20`).
- **Decisions.** An `[AD#N]` carries `**Binds:**`, `**Prevents:**`, `**Rule:**` and `**Alternatives:**` (`ard-format.md:68`). Violating one without a deviation record is a reviewer BLOCKER (`ard-resolution.md:109`–`117`).
- **Promotion.** `/promote-decisions` stops with "Nothing to promote" when no record is a candidate and no artifact has friction (`architecture-promotion.md:98`).
  - It ranks candidates by cluster size "in distinct groups" (`:123`), where a group is a PRD (`promotion-scout.md:30`).
  - Other teams appear only as other specs repositories that share the architecture repository (`architecture-promotion.md:56`).
- **Follow-ups.** A run that resolved no folder keeps its follow-ups in the report only (`followup-emission.md:44`).
  - A line carrying `[SEC#n]` is matched as a security finding's line (`:86`).
  - ``repository `<name>` `` is reserved for the other-repository identity (`:93`).
  - `register.py` treats any task line that names ``repository `<slug>` `` and carries `[SEC#n]` as that finding's own line (`register.py:882`–`885`).
- **Pre-lint.** Pre-lint's autolink grep runs over PRDs, ARDs and Epics (`pre-lint.md:44`, `:48`). A hit inside a markdown link is discarded (`:56`). A standards token such as `CWE-89` is reported as a MINOR (`:63`).

## 3. The data path

### 3.1 One reader in `workflows-core` (E1)

**Decision.** Add `plugins/workflows-core/scripts/weakness-classes.py`. It uses the standard library only, has a `--selftest` that CI runs next to `register.py`'s (`.github/workflows/validate-catalog.yml:242`), and has two verbs:

- `classes --specs <root> --repo <slug>… [--component <id>…] [--today <date>]` reads the named registers, for Parts 1 and 2.
- `across --specs <root> [--ref <ref>] [--today <date>]` reads every register in the tree, for Part 3. With `--ref` it reads `git show <ref>:security/<slug>/register.json`.

It prints one JSON object and exits 0 whenever it could run. Exit 2 means a usage error.

- **`workflows-core` agents run the script by path.** That is `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/weakness-classes.py"`; `code-scanner.md:62` is the precedent for an agent running its own plugin's script.
- **Commands in other plugins run it through a skill**, `plugins/workflows-core/skills/weakness-classes/SKILL.md`, with `user-invocable: false`. The skill runs the script and passes its JSON through. This follows the `specs-git` precedent, a `workflows-core` skill that runs `workflows-core`'s script for every plugin's commands (`skills/specs-git/SKILL.md:1`–`14`).

**Why.**

- `register.py` cannot be reached across the plugin boundary, and it has no read verb.
- An agent reading `register.json` directly would also read the titles (E11).
- The recurrence rule needs exactly one implementation, because three consumers apply it.
- Copying the script byte for byte, as the copied-scripts rule allows (`.claude/rules/workflows-core-bounded-run.md:17`), would give three copies of a domain rule rather than of a utility. That is the alternative in §12 Q5.

**Where the rule lives.** It goes in a new §7 of `workflows-core:security-register-format`, *Weakness classes*. §6 becomes "the readers are the callers of `weakness-classes.py`", and §1's "register.py implements this file" is narrowed to §1–§5 (§10).

### 3.2 Which registers (E3)

- **Part 1 and the scan's Part 2.** For each `components` id, the slug is the part before the first `:`. A slug never contains `:` or `/`, because it is the last segment of the URL after `/` or `:` (`components.md:11`–`14`), so the split is exact. Each slug is then resolved against the known set: the directory names under `$SPECS_PATH/security/` that hold a `register.json`. A slug that is not in that set has no register, and that is the normal case.
- **Part 3.** Every `security/<dir>/register.json` on the ref, where `<dir>` matches `register.py`'s slug pattern.
- **Why `components` (my call).** It is the one set every consumer already passes and the grounder already holds. The Epic's `target:` and `implementation.md` blocks name a narrower or later set. Reading them would add an input to fix a gap nobody has measured (CLAUDE.md, *Measure the population*).

### 3.3 What it reads, and what happens when a register is missing or bad

- **It reads `register.json` only.** It never reads `runs/` or `scans/`, because replaying them is `register.py`'s logic, and it never reads `register.md`.
- **Part 1 reads the working tree**, with the team root's "differs from `<default-ref>`" clause carried over (`architecture-grounding.md:19`). **Part 3 reads `--ref`**, as every promotion input does (`architecture-kb.md:85`).
- **Each register reports one `state`.** None of them stops a run:

| `state` | When | Effect |
|---|---|---|
| `ok` | It parses, `format` is `1`, and `findings` is a list | Read. An empty list gives no classes |
| `absent` | No `register.json` for the slug | Silent |
| `unreadable` | An I/O or JSON error | Skipped; the report names it |
| `unknown-format` | `format` is not `1` | Skipped; the report names it |
| `malformed` | The top-level shape is wrong | Skipped; the report names it |

  Within an `ok` register, a finding whose required field fails its check (§8) is dropped and counted in `dropped`.
- **Staleness is accepted.** The file is derived, and may lag records that sit on unmerged `session/*` branches (`security-register-format.md:33`, `:61`). The output is advice, so a lag of one rebuild is acceptable. The plan line says when the tree differs.

### 3.4 The class, and the rule (E2, E5, E6)

- **Key: `(repo-slug, cwe)`.** `cwe` is the primary one, and must match `^CWE-\d+$`. A finding that fails the pattern is counted under `unclassified` and never forms a class.
- **Why only the primary CWE.** §5 rule 1 matches on "same CWE" (`security-register-format.md:130`). Using `other_cwes` as well would count one finding into several classes.
- **What counts toward each part:**

| Use | Statuses that count |
|---|---|
| Part 1, live | `open`, `fix`, `fixing`, `reopened`, `accepted-risk` (`register.py:143`), plus a transient `new` |
| Part 1, context | `fixed`, where the `at` of its last `history` entry is within 180 days of `--today` |
| Part 2, recurs | `accepted-risk` in at least 2 findings of one register |
| Part 3, judged real | `fix`, `fixing`, `reopened`, `accepted-risk`, and `fixed` within 180 days |
| Never | `false-positive` (roadmap `:395`). Part 3 also excludes undecided `open` |

- **`prevented_by`.** Lists the ids of team records that meet both of these:
  - their `index.yaml` status is `accepted`;
  - the `**Prevents:**` paragraph of `decisions/<id>.md` holds the class's CWE as a whole token, so that `CWE-89` is not matched by `CWE-890`.

  This matches a token the reader already holds, the same way the commit scan does (`.claude/rules/workflows-core.md:36`). It never extracts an identifier from the text. A promoted record still counts, because the organisation artifact it names covers the class too.
- **Ranking.** Classes are sorted by:
  1. recurring and not prevented;
  2. the highest live severity;
  3. the live count;
  4. whether a finding lies under a `--component` path;
  5. the slug;
  6. the CWE number.

## 4. Part 1 — the `known-weakness` challenge

### 4.1 Resolution (E4)

`resolve-architecture-grounding` gains a step 5a, **the register root**, inside the one resolution the run already makes (`architecture-grounding.md:85`):

- `security_root` is `$SPECS_PATH/security`.
- `security_grounding` is ON when at least one `*/register.json` exists under it.
- `--no-arch` turns it OFF with the other two roots.

The plan-approval line is shown with the team line:

```
security registers: ON <specs>/security (<n> registers[; differs from <default-ref>])
security registers: OFF (<reason>)
```

**No line at all where `$SPECS_PATH/security/` does not exist (my call).** A tree that has never run a scan then prints exactly what it prints today. The team line, by contrast, is always shown (`:39`), because every family install has a knowledge base. Registers come from an optional plugin.

### 4.2 Dispatch and the agent

- **The dispatch condition widens.** "`arch_grounding: ON` or `team_grounding: ON`" becomes "… or `security_grounding: ON`" in `architecture-grounding.md:45`, `create-ard.md:620`, `specify.md:906` and `design.md:304`. `/update-spec` follows `/specify` (`update-spec.md:94`).
- **The agent gains the input** `security_root: <specs>/security | null`. The extent of "at least one root is set" (`architecture-grounder.md:13`, `:20`) widens to three roots.
- **New method step 5a.** Run `weakness-classes.py classes` with the slugs and ids from `components`. Raise one `known-weakness` per class that holds a live finding, taking the script's order.
- **Hard rule `:85` widens by exactly that one script.**

### 4.3 Shape

```yaml
arch_challenges:
  - kind: known-weakness
    subject: CWE-89 in api
    evidence: "security/api/register.md — [SEC#3] accepted-risk HIGH src/orders/Repo.java:88; [SEC#7] fixing MEDIUM src/search/Query.java:41"
    governing: { id: ACME-17-AD3, title: …, root: team, path: architecture/decisions/ACME-17-AD3.md, url: null, rule: "<quoted>", prd: ACME-17, source: … }   # null where no live record prevents the class
    weakness: { repo: api, cwe: CWE-89, live: 2, accepted: 1, awaiting_review: 1, review_due: 0, fixed_recent: 1, recurs: false, register: security/api/register.md }
security_registers: [{ repo: api, state: ok }, { repo: billing, state: malformed }]
```

- **Evidence lists at most five findings.** Each is its `[SEC#n]`, status, severity and `path:line`. Where the path fails its check, the entry reads "location in register.md".
- **`governing`** names the first id in `prevented_by`, with its Rule quoted, as the grounder quotes any record. It does so even when the record's `source:` is in `own_sources`: the caller then learns that its own ARD already prevents the class.

### 4.4 Rank and cap

- At most **three** `known-weakness` challenges, inside the existing cap of eight.
- The order becomes `contradicts-*`, then `known-weakness`, then the radar kinds (my call). A recorded, triaged weakness in the code the work touches is measured evidence. A radar ring is policy about a technology.

### 4.5 How each command presents it

The challenge competes for a question slot like any other; it never adds one (`architecture-grounding.md:70`). The question cites the `[SEC#n]`, the CWE and the register link, and never a finding's text. It asks how the work avoids adding to the class.

- **`/create-ard` (the PA).**
  - Where `recurs` is true and `governing` is null, the question offers the decision itself: `choices: ["Record an [AD#N] that prevents CWE-89 (Recommended)", "Not in this ARD"]`. A yes is grilled into Binds, Prevents, Rule and Alternatives like any decision, and `ard-reviewer` gates it.
  - The ARD records nothing for the challenge itself.
  - The grill also checks the ARD's own unharvested `[AD#N]` Prevents lines, which the run holds (`architecture-grounding.md:72`).
- **`/specify`, and `/update-spec` for the items it revises.** Where the grill cannot settle the challenge, it writes a `- [ ]` open question. The question names the class and links the register relative to the specification. It says what settles it: a Security / privacy acceptance criterion in the specification, or, where the class recurs and nothing prevents it, an ARD decision whose Prevents names the CWE, through `/product-workflows:create-ard <PRD-KEY>`. This follows the shape at `architecture-grounding.md:75`.
- **`/design` (the Dev).** `design-format` § Architecture governance gains a line under `## Risks & mitigations` (`design-format.md:176`) (my call):

  ```
  - Known weakness: CWE-89 in api ([register](<link>)) — <how this design avoids adding to it, or why it accepts it>
  ```

  The line is advisory. `design-reviewer` never gates on it.
- **The final report** extends its `architecture grounding:` line with `registers read: api; skipped: billing (malformed)`.

### 4.6 When there is no register

- With no `security/` directory, or no register for any touched slug, `security_grounding` is OFF, or `classes` returns nothing. The dispatch and the digest are then exactly today's.
- A script failure, or `status: ERROR` from the grounder, turns architecture grounding OFF in the way that already applies (`architecture-grounding.md:65`).
- No command stops, asks or becomes unavailable because of a register.

## 5. Part 2 — recurring accepted risks become a decision

### 5.1 Recurs (E6)

A class recurs when its register holds **two or more** findings whose current status is `accepted-risk`.

- **No separate window.** An accepted risk returns to triage at its review-by date (roadmap `:395`). A risk that is then fixed, or ruled a false positive, stops counting at once. The review-by date already bounds the count.
- **A review-due risk still counts.** It remains accepted until someone decides again, and the line says it is due.
- **A Dev's accepted risk counts** (`confirmed: false`). It "takes effect at once" (`security-register-format.md:126`), and the PA decides whatever is proposed. If the Security Engineer overrules it, it drops out at the next read.

### 5.2 Prevented (E7)

A class is prevented when `prevented_by` is not empty (§3.4). Only harvested records are visible to this test. Between the PA recording the `[AD#N]` and `/harvest-decisions` running, the test still reports the class unprevented. That costs at most a duplicate follow-up line, and §5's dedupe catches it within a folder.

### 5.3 Who raises it (E8)

**Decision: the scan raises it.** An accepted-risk decision is made only in the scan's triage, so the scan is where the event happens. The scan is already a `followup-emission` caller (`followup-emission.md:7`–`9`).

**When.** After 7.2's `commit`, the scan calls the skill: `classes --repo <repo-slug>`. Where both of these hold, it adds one item to 7.6's follow-ups:

- the run's decisions include an `accepted-risk`, new or confirmed, for a finding of class C;
- after the rebuild, C recurs with an empty `prevented_by`.

That read informs a follow-up and changes nothing in the register, so it is not a read of the register's state (§10, item 3).

**The line:**

```
- [ ] Run `/product-workflows:create-ard ACME-17` to record an [AD#N] whose Prevents names CWE-89 — 2 accepted risks of CWE-89 in the api register (security/api/register.md), and no team decision prevents it — raised by /security-workflows:scan
```

- **It carries no `[SEC#n]` and no ``repository `<name>` ``.** Otherwise `register.py` would count the line as a finding's own follow-up (`register.py:882`–`885`), and `followup-emission` would match it as a security line (`:86`).
- **It dedupes on the CWE and the register path.**
- **The key is the nearest `PRD-` folder at or above the unit folder**, by the rule at `architecture-kb.md:20`.
- **Where it lands.**
  - On a key run, it lands in the unit's folder (§2 of `followup-emission`).
  - On a path run it is report-only, in `### Next step`, because there is no folder. The `/create-ard` grill and Part 3 still reach that class later.

**`/create-ard` raises it directly** when the PA is there (§4.5). No command writes an `[AD#N]` itself: the PA answers the grill, and `ard-reviewer` gates the result.

### 5.4 The decision's form (E9)

`**Prevents:**` names the CWE as a link: `[CWE-89](https://cwe.mitre.org/data/definitions/89.html)`, where the number is the validated digits.

- A bare `CWE-89` in an ARD is a pre-lint MINOR on every run (`pre-lint.md:63`). A token inside a link is discarded (`:56`).
- The coverage test finds the token in the link text.
- `ard-format` § Architecture governance gains one sentence saying this. The pre-lint grep is not touched (CLAUDE.md, *One key namespace*).

### 5.5 Downstream

From here on, nothing new is involved:

1. The ARD merges through `handoff-to-main`.
2. `/harvest-decisions` turns the decision into a team record, with Prevents carried verbatim (`architecture-kb.md:60`).
3. `prevented_by` now names that record, so Part 2 goes quiet for the class and Part 1 shows it as `governing`.
4. `/promote-decisions` offers the record (§6).
5. `ard-resolution` makes breaking the decision a reviewer BLOCKER (`ard-resolution.md:117`).

### 5.6 Review-by interaction

1. **A decision changes no risk.** No status, owner or review-by date moves when an `[AD#N]` lands. `ard-resolution` binds the artifacts that consume the ARD, not code a person has already accepted.
2. **The review date is when the decision reaches existing code** (my call). Scan Phase 5's row for a review-due accepted risk (`scan.md:305`) names the live team record whose Prevents covers its class. The data comes from one `classes` call made before the triage. Re-accepting then means choosing visibly against a team decision. The suggestion stays as it is today: the current status, shown for a new decision.

## 6. Part 3 — recurrence across teams

### 6.1 What a team is (E10)

**A team is a register: one code repository.**

- One `/promote-decisions` run sees one specs repository. Other teams are other specs repositories, which no run can read (`architecture-promotion.md:56`).
- Inside one specs repository, the register is the only unit of ownership the tree records (`security-register-format.md:3`).
- PRD groups (`promotion-scout.md:30`) lose every finding raised by a path run, because those carry no `units` (`register.py:521`).
- Aggregating across specs repositories is a non-goal (§9). Coverage is still checked organisation-wide, because another team's promoted ADR or standard sits in the architecture repository the scout reads.

### 6.2 Signal and threshold

A class recurs across teams when **two or more registers** each hold at least one judged-real finding of it (§3.4). Undecided findings and false positives do not count.

### 6.3 Where it surfaces

1. **§5 signals.** `/promote-decisions` also runs `weakness-classes across --ref <default-ref>` through the skill, and writes the JSON next to the signals file. "Nothing to promote" now also requires that no class recurs across teams (`architecture-promotion.md:98`).
2. **§6 comparison.** `promotion-scout` gains the input `weakness_classes`, the path of that JSON.
   - For each class it returns `relation: covered | uncovered`, together with the `accepted` ADR or `active` standard that prevents it. "Prevents" means the artifact names the CWE or states a rule that implies it; the scout reads every artifact it cites.
   - `EMPTY` (`promotion-scout.md:58`) also requires no classes.
3. **§7 shortlist.**
   - **A promotion row whose record is in a class's `prevented_by`** gains the reason `prevents CWE-89, which recurs in 3 registers (api, billing, web)`. It ranks on that reason right after cluster size (`:123`) (my call).
   - **An uncovered class that no record prevents** is listed, unnumbered, under *Reported only* (`:132`): `CWE-89 — recurs in 3 registers (api, billing, web): 4 accepted risks, 2 fixed — no team decision prevents it, and no ADR or standard covers it — record one with /product-workflows:create-ard`.
   - **Covered classes** get one count line.
   - **No ADR is drafted from a class alone.** A decision starts in an ARD (§5).

## 7. Plugin boundaries

| Plugin | Changes |
|---|---|
| `workflows-core` | Adds `scripts/weakness-classes.py` (with `--selftest` in CI) and `skills/weakness-classes/`. Changes `security-register-format` §1, §6 and the new §7; `architecture-grounding` (step 5a, plan line, dispatch condition, consumption); `architecture-grounder` (input, step 5a, `known-weakness`, hard rule); `architecture-promotion` §5–§7; and `promotion-scout` (input, output, `EMPTY`) |
| `product-workflows` | `create-ard.md`, `specify.md` (`update-spec` follows it), `promote-decisions.md`, and the Prevents-link sentence in `ard-format.md` |
| `dev-workflows` | `design.md`'s dispatch condition, and `design-format.md`'s *Known weakness* line |
| `security-workflows` | `scan.md` Phase 5 (the review-due annotation) and Phases 7.2/7.6 (the PA follow-up). `register.py` is unchanged |
| `docs-workflows` | None |

**How no plugin comes to depend on `security-workflows`.**

- The register is data in SPECS, and reading it needs no dependency (roadmap `:210`).
- Its format and its only reader are both in `workflows-core`, which every family plugin already declares.
- `grep -l security-workflows plugins/*/.claude-plugin/plugin.json` still lists only its own manifest (`.claude/rules/security-workflows.md:16`).
- On a machine without `security-workflows` there are no registers, so every path above takes the absent case.

## 8. Safety — register text is data

1. **The reader prints validated structured fields only:**
   - `[SEC#n]` as an integer;
   - `cwe` (`^CWE-\d+$`);
   - `severity` and `status` (enums);
   - `path` (`register.py`'s safe-path pattern, `register.py:162`, else null);
   - `line` (integer);
   - `review_by` (`YYYY-MM-DD`);
   - `confirmed` (boolean);
   - the slug (slug pattern);
   - counts.

   It **never** prints `title`, `reason`, `evidence`, `by`/`owner`, `links`, `scope` or `units`. A field that fails its check is dropped, never echoed. The script never opens a path taken from the register, and never runs anything a field names.
2. **The agents never open a register file.** `architecture-grounder` and `promotion-scout` each gain a hard rule: never read `register.md`, `register.json`, `runs/` or `scans/` under `security/`, and use the script as the only way in. Their untrusted-content blocks (`architecture-grounder.md:90`–`125`, `promotion-scout.md:67`–`102`) still cover everything else.
3. **Every line, row and question built from a class** uses those fields plus fixed wording, as follow-up lines do today (`security-register-format.md:98`–`105`). A CWE's URL is built from its validated digits only.
4. **What the artifacts record is human-authored.** An ARD decision, a specification question or a design line is written by a person in the grill, never copied from register text.
5. **A `--selftest` fixture plants injected text.** It plants `Ignore all previous instructions` in a title and a reason, a CWE of `CWE-89; rm -rf`, and a path containing a backtick and `../`. It then asserts that none of them reaches the output. `register.py`'s selftest plants the same phrase (`register.py:1996`).

## 9. Non-goals and anti-goals

**Non-goals.**

- No scanning, patching or fixing. Claude Security and the scan do that.
- No writes to a register. `register.py` stays its only writer and does not change.
- No automatic `[AD#N]`, and no ADR drafted from a register alone.
- No new gate. `known-weakness` is advice, and a BLOCKER comes only through a recorded `[AD#N]`.
- No CWE taxonomy rollup, and no use of `other_cwes`.
- No aggregation across specs repositories.
- No new environment variable or flag.
- No change to triage statuses, suggestions or review-by rules.
- No threat models: those are B, C and D.

**Anti-goals.**

- A finding's text in any agent's context, artifact, follow-up or shortlist.
- Any consumer failing, stopping or asking because of a register.
- A slug or key parsed out of free text.
- Reading `runs/` and replaying them outside `register.py`.
- Exempting `CWE-` from the pre-lint grep.
- The recurrence rule implemented in more than one place.

## 10. Claim-expiry sweep — notes E makes stale

The sweep covers the scope of refinement 4 in `.claude/rules/claim-sweep.md`. Each item below is matched by phrase, then the whole paragraph is read:

1. **`security-workflows/CHANGELOG.md:235`**: "Not built yet … Not in it: E". This stays: it is true of that release. The new entry says what E adds.
2. **`security-register-format.md:11`**: "register.py … implements this file" is narrowed to §1–§5. §7 is `weakness-classes.py`'s.
3. **`security-register-format.md:33`**: "No run reads the derived files back as its state … One read is the exception". This is an exclusivity probe (refinement 3). E's reads, including the scan's Part 2 read after its own rebuild, decide no register change. The sentence must say "as the register's state", so the reads are visibly outside it. `.claude/rules/security-workflows.md:34` ("The one read of a derived file as state") needs the same change.
4. **`security-register-format.md:158`** (§6) and **`.claude/rules/security-workflows.md:22`**: the readers recipe greps for `args: "security-register-format`, which misses readers that go through the script. Rewrite it as "the callers of `weakness-classes.py`", with a grep recipe that matches the execution phrase.
5. **`architecture-grounding.md`** `:3` ("a second, team root"), `:39` ("the two roots … turns both off"), `:45` (the dispatch condition), `:81` (the invariant on what it never writes), and its Consumers line.
6. **`architecture-grounder.md`** `:3` (the description), `:13` and `:20` (two roots), `:72` (the kinds enum), and `:85` (Bash).
7. **The three dispatch sentences**: `create-ard.md:620`, `specify.md:906` and `design.md:304`. `update-spec.md:94` must be re-read, not edited.
8. **`.claude/rules/docs-grounding.md:58`, `:64`** (what the grounder reads) and its `paths:`, which gain the skill and the script.
9. **`.claude/rules/workflows-core.md:18`** ("three bundled skills") and **`plugins/workflows-core/docs/README.md:32`** ("the three bundled skills").
10. **`promotion-scout.md:3`, `:58`** and **`architecture-promotion.md:98`**, which hold the early exit.
11. **The roadmap spec** `:151` and `:208` ("E's consumers (`architecture-grounder` and `promotion-scout`)") are outside the sweep's scope. The scan joins the consumers through Part 2, so D2's sentence can take an amendment line, as the roadmap's earlier amendments did.

A sweep for the subject, "who reads the register", covers items 3, 4 and 11 (refinement 6).

## 11. Docs, versions, coupling

**Pages.**

- **`workflows-core`:** `docs/reference/grounding.md`, `agents.md`, `references.md#skills` (a new skill fails `check-docs.sh` without its entry), `README.md:32`, and `family-map.md`'s security lane.
- **`product-workflows`:** `docs/commands/create-ard.md`, `specify.md`, `update-spec.md` and `promote-decisions.md`.
- **`dev-workflows`:** `docs/commands/design.md`.
- **`security-workflows`:** `docs/commands/scan.md`, `workflow.md`, `reference/security-register.md` (who reads the register) and `roles-and-phases.md` (the PA receives the follow-up).

**Rules files.** The rules files named in §10, and the workflow-map lines in `.claude/rules/product-workflows.md:42`, `:44` and `:45`, `security-workflows.md:27` and `dev-workflows.md` (`/design`).

**Versions.** Each plugin takes its next minor at merge: `workflows-core` from 1.85.0, `product-workflows` from 3.79.4, `dev-workflows` from 4.63.0 and `security-workflows` from 0.11.3. Each has a dated `CHANGELOG.md` entry.

**Coupling.** One bullet in `.claude/rules/plugin-updates-coupling.md` naming all four, in both directions:

- **An older dependent beside the newer `workflows-core`.** The old commands never resolve `security_grounding` and never pass `security_root`, so the grounder behaves as it does today, and no PA line is written.
- **A newer dependent beside the older `workflows-core`.** `security_grounding` is never returned, so it is never ON. The skill does not exist, and a failed reader call is skipped with one report line by design (§4.6), so no run breaks. The signals are lost until both sides are updated.

## 12. Open questions for the maintainer

1. **Threshold: is it 2 for both Part 2 (accepted risks in one register) and Part 3 (registers)?** *Recommend 2.* Every accepted risk is a deliberate decision with an owner, so two of one class are already a pattern. The PA or the architect filters what is proposed.
2. **Is a "team" a register (one code repository) or a PRD group?** *Recommend the register* (§6.1). A group loses every finding from a path run. A team as a specs repository cannot be reached from one run.
3. **Should the scan raise the PA follow-up, or should only `/create-ard`'s grill?** *Recommend the scan, on key runs* (§5.3). The row says "a follow-up for the PA", and the scan is where the accepted risk is decided. The grill alone would wait until the PA happens to refine an ARD for a PRD that touches the repository.
4. **Should a Dev's accepted risk, still awaiting security review, count toward recurrence?** *Recommend yes* (§5.1). It is in effect now. An overrule removes it at the next read, and the PA decides the outcome anyway.
5. **One script reached through a skill, or byte-identical copies in three plugins?** *Recommend the skill* (§3.1): one implementation of a domain rule, as `specs-git` already does. Copies are allowed under the copied-scripts rule, but that rule was written for small utilities.
