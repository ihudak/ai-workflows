# Linked sources (embedded authority)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

How a markdown document's links are found, resolved and walked, stated once. **`/brd-intake` Phase 1
runs the walk** from a customer's BRD, and **`/idea` Phase 1.5 runs it** from an idea source; each
decides afterwards, with the operator, which of the files it reached to take (§7). `brd-reader`,
`idea-reader` and `figure-reader` read what their caller hands them and walk nothing.

Before this file existed `/brd-intake` Phase 2 defined the link forms and `idea-reader` restated them
in full, which is two copies of one rule — and they had already drifted: the command did not
recognise a `[[wikilink]]` at all, and the agent recognised one but never said how a bare name
resolves. Design authority: `docs/superpowers/specs/2026-09-18-brd-figures-and-appendices-design.md`
§14 (removed from the tree 2026-09-23; `git show 62e791e8:docs/superpowers/specs/2026-09-18-brd-figures-and-appendices-design.md` retrieves it).

## 1. The link forms

Four forms, and a markdown document uses all of them:

- a `[[wikilink]]` — bare (`[[notes]]`), aliased (`[[notes|see this]]`), or embedded (`![[shot.png]]`);
- a markdown inline image or link — `![alt](<target>)` and `[text](<target>)`, angle-bracketed
  (`[text](<my file.png>)`) or not, with any title after the target ignored;
- a reference-style definition — `[label]: <target>`, wherever in the document the definition sits;
- an HTML `<img src="<target>">`.

The embedded wikilink is the form a converted BRD most often carries: Obsidian writes a pasted image
as `![[Pasted image ….png]]` and saves the file to the vault's attachment folder, usually outside the
note's own directory.

**The form says only that something is a link; the extension of what it resolves to decides its
kind** (§4). An image embedded as `<img src>` is an image exactly as `![alt](…)` is, and a page
reached only through a reference-style definition is a page exactly as one reached by `[text](…)` is.

## 2. Normalising a target

Drop any `#fragment` and `?query`, then percent-decode. For a wikilink, also drop whatever follows
its `|` — an alias, or an embed's width — and any `#heading` or `^block` suffix. **A target empty
after that is an in-document jump** — `[[#Scope]]`, `[see below](#scope)` — and is neither followed
nor recorded.

The record keeps the target **as written** (§5), what follows a wikilink's `|` aside: normalising is
how a target is resolved, never how it is reported, because every caller that maps a link back to
its copy compares written forms.

## 3. Resolving a target

In this order, stopping at the first that applies:

1. **A target carrying a URI scheme** (`https:`, `http:`, `mailto:`, `data:`, …) is a `url`. It is
   recorded and never followed, fetched or read.
2. **Resolve it against the directory of the file the link sits in**, normalised **as text** — `..`
   segments collapsed, symlinks never resolved. An absolute path resolves as itself. Where it names a
   readable regular file reached through no symbolic link, that is the target: **neither the file nor
   any folder on its path below the deepest folder that path shares with the starting document's
   own directory may be a link**, each tested without following it (`lstat`, never `stat`). A path
   that is a link, or passes through one there, names no file the walk takes — the walk follows no
   link, and `${CLAUDE_PLUGIN_ROOT}/references/idea-format.md`'s programs read none (*The source
   root*) — so a customer's `appendix.md` that is a link to a key file elsewhere is never reached.
   **A wikilink whose name does not already end in
   `.md`, `.markdown` or an image extension of §4's kind table is then tried with `.md` added, in the
   same place**, as Obsidian does — so `[[appendix]]` beside `appendix.md` resolves with no vault at
   all, in a customer's zipped folder as in a vault, and `[[notes.v2]]` is tried as `notes.v2.md`,
   its dot being part of the name rather than an extension.
3. **A wikilink that step 2 did not resolve is looked up in the vault**, and only then. Where the
   name does not already end in one of those extensions, try it with `.md` too, as step 2 does. The
   **vault** is the nearest ancestor of the **starting document** — the one the walk began from, not
   the file this link sits in — that holds a `.obsidian/` directory. A name carrying a `/` resolves
   against the vault root; a bare name is matched by filename anywhere under it — either way
   entering no folder that is a symbolic link and matching no file that is one, as step 2 tests them.
   - **Exactly one match** — that is the target.
   - **More than one** — the target is `ambiguous`. Record every candidate and **choose none**: two
     notes sharing a name are two different files, and a walk that picked one would report a file the
     author may never have meant as though they had linked it.
   - **None** — the target is `unreadable`.

   Where no ancestor holds `.obsidian/`, there is no vault and this step is skipped: the target is
   `unreadable`.
4. **Anything else step 2 did not resolve** is `unreadable` — a path naming no file, naming one
   that cannot be read, or naming a link or reached through one (step 2).

## 4. The walk

**Breadth-first, in document order within each file**: the starting document's links in the order
they appear, then each linked markdown file's links the same way, and so on. The order is
deterministic, so two walks over one tree reach the same files in the same order.

**Transitive through every markdown file reached**, inside the starting document's own directory or
outside it. **A visited set** of resolved absolute paths, the starting document first, makes every
file visited once — a cycle is a silent skip, not an error — so the walk terminates on any tree.

**Every resolved file has a kind**, read off its extension, case-insensitively: **markdown**
(`.md`, `.markdown`), **image** (`workflows-core:grounding-format` §6.2 step 1's set: `.png`, `.jpg`,
`.jpeg`, `.gif`, `.svg`, `.webp`), or **other** — anything else. Only a markdown file is opened, and
only to find its links.

**Read-only, and first.** The walk copies nothing, writes nothing, dispatches nothing and reads no
image or *other* file. It runs before a caller copies or hands anything to an agent, which is what
lets an operator decline for free.

## 5. The walk record

One entry per link found, including a second link to a file already visited (the record is of links;
the visited set is of files):

```yaml
- target:     <the link target exactly as written, what follows a wikilink's | dropped>
  from:       <absolute path of the file the link sits in>
  path:       <resolved absolute path — absent only when the walk itself sets reason>
  kind:       markdown | image | other     # absent only when the walk itself sets reason
  depth:      <1 for the starting document's own links, 2 for theirs, …>
  inside:     true | false                 # resolved path lies within the starting document's own directory; absent only when the walk itself sets reason
  reason:     url | unreadable | ambiguous # set by the walk iff the target resolved to no single file
  candidates: [<absolute path>, …]         # present iff reason: ambiguous
```

**`target` is what sits between the link's own delimiters, as the author typed it; the syntax that
makes it a link is not part of it** — `[[` and `]]`, or `![[` and `]]`, for a wikilink; `(` and `)`
for an inline link or image, and any title after the target; the `]:` of a reference definition,
and its title; the `<` `>` markdown allows around the target of either of those two; and the quotes
of an `<img src="…">`. What is between them is kept exactly, save whatever follows a wikilink's `|`
— an alias, or an embed's width: `![[Pasted image 1.png|300]]` records `Pasted image 1.png`, and
`[fields](<appendix/field list.md>)` records `appendix/field list.md`. Nothing else is normalised
here (§2).

`depth` is the depth at which the file was **first** reached. `inside` compares the resolved `path`
with the starting document's own directory by normalised text, exactly as step 2 of §3 resolves. A
caller may add `reason: excluded` afterwards, beside `taken: false`, on an entry that **did** resolve
(§6, §7) — that entry keeps its `path`, `kind` and `inside`, because `excluded` is not one of the
three reasons above and never means the walk found no file.

## 6. Not-taken reasons

The shared vocabulary for a link whose file is not taken — by the walk, or by the caller after the
operator's answer:

| Reason | Set by | Fires when |
|---|---|---|
| `url` | the walk | the target carries a URI scheme (§3 step 1) |
| `unreadable` | the walk | the target resolved to no readable file (§3 steps 3–4) |
| `ambiguous` | the walk | a wikilink matched more than one file in the vault (§3 step 3); every candidate is recorded |
| `excluded` | the caller | the operator's consent answer left the file out (§7) |

A caller may keep reasons of its own beside these — `/brd-intake`'s link log keeps
`outside the source directory` and `absolute path` for the answer that captures nothing outside the
document's folder — but never redefines one of these four.

## 7. Taking a subset

A caller asks the operator, where it asks at all, which of the reached files to take. **Whatever
subset the answer names, a file is taken only where a chain of taken markdown files reaches it from
the starting document.** A file reached only *through* a file the answer left out is left out too,
with reason `excluded`, even where it would otherwise qualify: its link exists only inside something
nobody is going to read. Callers add `taken: true | false` to each entry; the walk itself takes
nothing.

**This file never decides when to ask.** Each caller states its own trigger and its own choice array,
because the bound it replaces is its own: `/brd-intake`'s was its source document's directory, and
`/idea`'s was a count and a depth.
