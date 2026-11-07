---
paths:
  - "scripts/**"
  - ".github/**"
---

# Gates — `check-docs.sh`'s checks 22 to 29

Loaded with `.claude/rules/gates.md`, whose `paths:` it shares and whose opening rule binds every gate. Split out of `.claude/rules/gates.md` to keep that file under 20,000 characters; the rest of `scripts/check-docs.sh`, its one body across three editions included, is there; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

### Check 22

**Check 22 holds a vendored copy to its original**: each `<original>:<copy>` pair `VENDORED_COPIES` names must be byte-identical, an absent copy is skipped, and an empty list — this edition's — makes it a no-op. The internal Claude edition lists the two scripts one of its plugins ships as copies of another's.

### Check 23

**Check 23 holds a path question to its rule**: every paragraph of a command under `PLUGIN_RELS` offering *Set <NAME>_PATH (you'll be prompted …)* — a run of non-blank lines, a fenced `choices:` block inside it included — names the rule `PATH_UNSET_RULE` names, *Required path environment variable unset* here, whitespace collapsed; none at all fails as vacuous. The unit is the paragraph, not the file, because `/design`, `/create-ard` and `/specify` cited the rule for `REPOS_PATH` while carrying a typed `SPECS_PATH` locally, which a file-level test passes. Measured at batch B20: on the tree before its fixes it fired on exactly the seven sites the batch fixed, and on none after. **What it cannot see:** whether a cited paragraph's own prose then contradicts the rule, nor a path asked for in prose with no such option. A numbered list with no blank line between its steps is one paragraph to it, so the rule named in one step passes a sibling step's option — a false pass; and prose separated from its fenced `choices:` block by a blank line fails though it cites the rule — a conservative false fail, fixed by closing the gap.

### Check 24

**Check 24 holds a keyed preload hook to the key grammar, by running it**: each `<hook>:<command>` pair `KEYED_HOOKS` names is piped a JSON payload for the command followed by each of `A-1`, `ACME_X-90`, `ACME-1-2-3` and two whole folder names — each also behind `--skip-costs` and behind `--enforce-model opus`, a run flag's one-token and two-token forms — and must print `KEYED_HOOK_MARKER`, the specs-context line; on a free-text argument, behind either or neither, it must not. Behavioural rather than a regex compare, because a hook may test more loosely than `workflows-core:addressing` §1 (the command validates the address) and never more narrowly — batch B28 found both hooks rejecting `A-1`, `ACME_X-90` and a typed folder name, and D41 every preload hook injecting nothing behind a leading run flag, which the command strips there. An absent hook is skipped with a note, an empty list switches it off, and without `python3`, which the hooks read the prompt with, it does not run. **What it cannot see:** a hook or command `KEYED_HOOKS` does not name — `product-workflows`' `/epics` hook, which tests no key, and the other commands of the two hooks it names, `/vuln`, `/dev-workflows:upgrade` and `/docs-workflows:release-notes`, whose leading-flag skip it never runs, among them — a key shape outside its fixed tokens, and a leading flag other than its two leads, a command's own flag taking a value of its own among them.

### Check 25

**Check 25 keeps maintainer vocabulary off a user's page.** Its pages are each `*.md` under a `PLUGIN_RELS` plugin's `docs/`, each such plugin's `README.md`, and the repository-root `README.md`. A line fails on any of three things:
- **a `§`**, anywhere a reader sees it: a fenced block and a mermaid label included;
- **a design-decision id**, `D` and one to three digits standing as a word (`D3.js` is not one), in prose and in an ordinary fenced block. In a mermaid block only the labels a diagram shows are read, never a node id;
- **`<plugin>:<name>`, where the name or its longest leading path is a markdown file under that plugin's `references/`.** This is resolved against every plugin in the tree, by directory and by declared name, never parsed by shape. So an agent, a skill (`workflows-core:model-routing`, a reference subtree but no file) and a command pass.

**What is not read:** an HTML comment in prose, where a recipe re-deriving a number on the page is kept, and a mermaid `%%` comment line. A comment that opens a line runs to the next `-->`; one inside a line hides text only where it closes before the paragraph ends, and is literal text otherwise. A `<!--` inside a code span or a fenced block opens nothing. A fence closes only on a run of its own character at least as long as the one that opened it.

**The marker.** A prose line carrying `<!-- docs-vocab-ok: <why> -->`, closed on that line, passes, and on a fence-opening line the marker sanctions the block it opens, as check 13's does. It is for the user's own content or output a run prints verbatim. A marker with an empty reason, one not written as that HTML comment, and one a reader sees, in a code span or on a line inside a fenced block, fails on its own line and sanctions nothing. A hidden comment that only mentions the marker's name is a note.

**Population.** It has no config name and no switch: its population is derived from `PLUGIN_RELS`, and every edition ships pages a user reads. A plugin with no page to read fails as vacuous. It runs outside the loop, because the root README is no plugin's. A page that is not valid UTF-8 fails, since a `§` a Latin-1 editor writes is a byte the scan would otherwise miss, and so does a scan that does not run to its end. Without `python3` the vacuity guard still runs, and the check prints a note and passes, as checks 12 and 24 do.

**Why.** A `§` cites a section of a reference written for the agents, a reference id names a file the reader never opens, and a decision id numbers a row of a design spec that is not shipped. None resolves for the reader.

**Measured at batch B30.** On the tree before its fixes (`9d9292b4`) it found 488 findings on 372 lines of 71 pages: 248 `§`, 225 reference ids and 15 decision ids. It finds none after the fixes, and no line carries the marker.

**What it cannot see:**
- the path form `references/<name>.md`, which also names files a user acts on;
- change history;
- a maintainer recipe outside a comment;
- an internal field name such as `specs_git`;
- a code span that runs across lines;
- a fenced block indented four or more spaces inside a list item, which it reads as prose;
- a decision id in a mermaid label written in none of the bracketed or quoted forms, such as edge text in `A -- text --> B`, a state label after `:`, an unbracketed subgraph title, or a sequence message;
- a citation of a reference that is not markdown, such as `cost-prices.yaml`;
- the other id families a design spec numbers, such as `C2`, `E1` or `L2`, whose shapes are also ordinary keys and words.

Review holds those. It also fires on a `D1` that is no decision id, such as a product's own name, which takes the marker.

### Checks 26 to 29: one reading of a page

Checks 26 to 29 read a page the same way, so the four agree on what a link is.
- **Read:** prose outside fenced blocks. A fence closes only on a run of its own character at least as long as the one that opened it, so a ```` block may quote a ``` one.
- **Not read:** an HTML comment, read as check 25 reads one, and a code span's contents as a link.
- **A link** is an inline link (a title in `""`, `''` or `()` allowed), a reference definition, or an `<a href>` or `<img src>`. A target with a scheme, or only an anchor, is no relative link.
- **Without `python3`** none of the four runs, and each says so; their vacuity guards run all the same.

### Check 26

**Check 26 holds a command page to a link back to its plugin's workflow page**: each `*.md` under a `PLUGIN_RELS` plugin's `docs/$DOC_CMD_DIR/` must link that plugin's `docs/workflow.md`, an anchor allowed. Check 15 holds every command to that page's diagram, save one the page's introduction says it leaves out, so the link reaches a picture with the command in it. A page may link more, as the BRD-route pages also link their route page. No command page under any plugin fails as vacuous. Measured at batch B31: 24 command pages linked no `workflow.md`, all six of `dev-workflows`' among them. **What it cannot see:** whether the link sits where a reader looks for it.

### Check 27

**Check 27 keeps a relative link inside its plugin.** An installed plugin sits alone in the plugin cache, `cache/<marketplace>/<plugin>/<version>/`, with no repository root above it and no sibling beside it. So a link that climbs out of `plugins/<name>/` works on GitHub and in a checkout, and breaks in the installed copy — even one that comes back down into a directory of the plugin's own name, since the cache's directory above it holds versions. A target fails the moment a `..` takes it above the plugin's directory, and a root-relative one (`/x`) fails outright. Its pages are check 1's: each `*.md` under a plugin's `docs/`, and its `README.md`. No page under any plugin fails as vacuous.

Measured at batch B31: 18 links, the plugin READMEs' and getting-started pages' links to the root README and four links into a sibling's pages. The fix: a README links its own getting-started page; a getting-started page, which check 10 lets name the repository, uses its URL; a sibling's page is named in words. Widening to every `*.md` under the plugin found one more, an example in `product-workflows`' `idea-format` reference of a user's absolute image path, which is correct content, so commands, agents and references stay out.

**What it cannot see:** a link inside the plugin that is wrong, which is check 1's; a link in a command, agent or reference; and whether a getting-started page's repository URL still names this repository in a fork.

### Check 28

**Check 28 holds a page that names one of its plugin's commands to linking that command's page.** GitHub draws a mermaid diagram without click-through, so the prose is the only way from a command's name to its page.
- **A mention** is `/<name>`, or `/<plugin>:<name>` for this plugin by directory or declared name, for a name the commands directory lists. It must stand as a word, never inside a path (`docs/commands/design.md`, `<KEY>/design.md`). `CMD_FORM=trigger` also reads `<name>:`. It is read from the prose above, code spans kept.
- **A link** resolves to `docs/$DOC_CMD_DIR/<name>.md`. One link anywhere on the page satisfies the check.
- **Population, the user's ruling at B31:** each `docs/*.md` (the index, workflow, roles, getting-started and route pages, and `workflows-core`'s family map) and each command page, its own command excepted. Reference pages are not held: they had 199 such mentions on 34 pages, left as they stand. The plugin README is not held either: check 15 holds it to naming every command, and every README links each one it names. Another plugin's command is not held, since check 27 forbids the link it would need.
- **Vacuity:** no page under any plugin fails, as does a scan that does not run to its end.

Measured at batch B31: 135 mentions on 33 pages, each fixed by linking the first one. A code span naming a chain (`` `/idea → /create-prd` ``) is never the one linked.

**What it cannot see, and where it fires on correct content:** a link to the wrong command; a command named in words; a reference page and the plugin README; a mention in an indented code block, which it reads as prose; and a bare name a Claude Code built-in shares (`/statusline`, `/feedback`, `/upgrade`), which it takes for the plugin's own command — link the plugin's page in the same sentence, as `workflows-core`'s getting-started page does.

### Check 29

**Check 29 holds a plugin's README to listing its pages.** A reader who opens a plugin on GitHub meets its README first, and the README's Documentation table is the list of pages the plugin ships, so a page the table leaves out is one that reader never learns exists.
- **The section** is an ATX heading reading `Documentation`, at any level, down to the next heading of its level or above: a `###` under it is inside it, and `## Documentation workflow` is not it. Its links are the navigation scan's, resolved from the README.
- **Held:** a README with the section links every `*.md` under its plugin's `docs/` but the command pages, which check 15 holds the README to naming. A README without the section links `docs/README.md`, as `prose-style`'s does, and check 3 holds the index to reaching every page.
- **Population:** each `PLUGIN_RELS` plugin's `README.md`. **Vacuity:** no README under any plugin fails, as does a scan that does not run to its end.

Measured at batch B32: nine pages left out of four tables — `workflows-core`'s Grounding sources, `dev-workflows`' Commit convention, four of `docs-workflows`' reference pages and three of `product-workflows'` — and none after.

**What it cannot see:** a setext heading, so a README that underlines `Documentation` is held to the index link alone; whether a row's description is true; and a page outside `docs/`.
