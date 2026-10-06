---
name: prose-style-refresh
description: >
  Refreshes your organization's prose style overlay from the source you configured —
  a set of style-guide URLs, a git repository, or a local directory. Distils the
  source into the plugin's eight reference-file structure and writes the result into
  your overlay directory. Never modifies the shipped vendor-neutral baseline, and
  carries no hardcoded style-guide URL.
allowed-tools: Read Write Edit WebFetch Bash Glob Grep Skill
disable-model-invocation: true
---

# Refresh the prose style overlay

Regenerates the overlay rules from **your** configured style-guide source. The plugin
ships no vendor's style guide and this command fetches from no fixed site: the source
is whatever your `source.yml` declares, or whatever you pass on the command line.

## Arguments

| Argument | Example | Behaviour |
|---|---|---|
| *(none)* | `/prose-style-refresh` | Uses the configured `source.yml` |
| `--source <url>` | `--source https://style.example.com/docs` | One-off web source; may be repeated |
| `--from <path>` | `--from ~/company-style-guide/` | One-off local directory or file source |
| `--rules <path>` | `--rules ~/style/rules` | Write to this overlay directory instead of the discovered one |
| `--dry-run` | `--dry-run` | Report what would change; write nothing |

## Procedure

### 0. Resolve the baseline directory

Invoke the `prose-style-rules` skill (Skill tool, `skill: "prose-style:prose-style-rules"`), which states where the shipped baseline lives, and take from it the absolute path of the shipped baseline directory — the one holding `terminology.md`, `word-list.md`, and the other six reference files. The path is taken from the skill rather than restated here because the skill states it together with the rule that nothing writes into it, and this command — the one that writes overlays — is the one that has to honour that rule.

Everything below calls that resolved path **`<baseline>`**. It is a read-only input to
this command: the structure to map onto, and the one path that must never be written to.

### 1. Resolve the overlay directory (the write target)

Take the FIRST that resolves:

1. `--rules <path>`, when given.
2. `<repo-root>/.prose-style/rules/` — `<repo-root>` from
   `git rev-parse --show-toplevel`, falling back to the working directory.
3. `$PROSE_STYLE_PATH`.

If none exists yet, tell the user which path you would create — default
`<repo-root>/.prose-style/rules/` — and ask for confirmation before creating it. Do not
create a directory tree unasked.

**The shipped baseline at `<baseline>` is never a write target.**
It is the vendor-neutral fallback, it is reinstalled with the plugin, and anything
written there is lost on the next update. Refuse a `--rules` path that resolves inside
`<baseline>` or its parent plugin directory, and say why.

### 2. Resolve the source

Take the FIRST that resolves:

1. `--source` / `--from` arguments, when given.
2. `<overlay directory>/source.yml`.

If neither resolves, do not guess a URL. Ask the user:

> "This plugin has no built-in style-guide source. Where should the rules come from —
> a set of URLs, a git repository, or a local directory?"

Then offer to write their answer to `<overlay directory>/source.yml` so the next
refresh needs no arguments.

#### `source.yml` schema

```yaml
# Where your style guide lives. Exactly one `kind` per source entry.
sources:
  - kind: web                    # fetch pages over HTTP
    pages:
      terminology:      ["https://style.example.com/terms", "https://style.example.com/trademarks"]
      word-list:        ["https://style.example.com/word-list"]
      voice-and-tone:   ["https://style.example.com/voice"]
      grammar:          ["https://style.example.com/grammar"]
      formatting:       ["https://style.example.com/numbers", "https://style.example.com/punctuation"]
      ui-interactions:  ["https://style.example.com/ui"]
      accessibility:    ["https://style.example.com/inclusive-language"]
      top-10-tips:      ["https://style.example.com/tips"]

  - kind: git                    # clone or pull a repo of style docs
    repo: git@github.example.com:org/style-guide.git
    ref: main
    path: docs/style             # subdirectory within the repo

  - kind: local                  # read a directory or a single file already on disk
    path: ~/company-style-guide/

# Optional. Defaults to all eight when omitted.
targets: [terminology, word-list, voice-and-tone, grammar, formatting,
          ui-interactions, accessibility, top-10-tips]

# Optional. `layer` (default) keeps the baseline underneath each generated file;
# `replace` writes the `<!-- prose-style: replace -->` marker into every generated file
# so it supersedes the baseline outright.
mode: layer
```

Multiple `sources` entries are read in order and merged; a later entry wins on conflict.

### 3. Fetch

- **web** — fetch each URL. If a page is paginated or truncated, fetch with a larger
  `max_length` and continue with `start_index`. A URL that fails is reported and
  skipped; it never aborts the run.
- **git** — clone into a temporary directory, or `git -C <clone> pull --ff-only` if it
  is already there, then read from `path`. Never write into the source repository.
- **local** — read the directory or file directly. Read-only; never modify the source.

If every source fails, report the failure and leave the existing overlay unchanged.
Exit without writing.

### 4. Distil into the reference structure

For each target file:

- Read the **existing overlay file** if there is one, to see the current structure and
  what has already been captured.
- Read the corresponding **baseline** file under `<baseline>` to see
  the section headings and table shapes the checker expects.
- Map the fetched content onto that structure: same file name, same heading levels, same
  `✅` / `❌` table shape. `terminology.md` and `word-list.md` have documented entry
  schemas at the end of their baseline files — follow them exactly, because the checker
  reads those tables structurally.
- **Distil, never transcribe.** Turn prose guidance into concrete, checkable rules with
  examples. A rule a checker cannot test against a line of text does not belong in the
  output.
- **Write only what the source actually says.** Never carry a rule over from the
  baseline into the overlay, and never invent one to fill a section. An empty section is
  correct when the source is silent — the baseline still covers it underneath.
- When `mode: replace`, put `<!-- prose-style: replace -->` on the first line of each
  generated file.
- Preserve any `## Allowed` section already present in the overlay file unless the
  source contradicts it; those are deliberate local exceptions.

### 5. Write

Write the generated files into the overlay directory. Under `--dry-run`, write nothing
and print the diff instead.

Files that would be identical are left untouched, so timestamps and version control
stay meaningful.

### 6. Report

Summarise per file:

- Rules added
- Rules changed
- Rules removed
- Terminology entries added or removed
- Sources that failed and were skipped

If nothing changed, say the overlay is already up to date.

Close with the resolved paths, so the next run is unambiguous:

```
Source:  <resolved source description>
Overlay: <absolute path to the overlay directory>
Baseline: <baseline>  (unchanged — always)
```

## Hard rules

- **No hardcoded style-guide source.** This command knows no vendor's URL. If the user
  has configured nothing and passed nothing, it asks — it never guesses.
- **Never write into `<baseline>` or anywhere else under the installed plugin.** The
  baseline is the fallback; a refresh
  writes only the overlay.
- **Never write into the source.** A git source is cloned read-only; a local source is
  read, never edited.
- **Never invent a rule.** Every generated line traces to the fetched source. A silent
  source produces an empty section, not a guess.
- **Keep the eight file names and their structure.** `prose-style-checker` and
  `prose-style-rules` both read them by name.
- **A failed source is reported, not fatal.** Partial refreshes are fine; a total
  failure leaves the overlay exactly as it was.
- **Credentials are the user's.** Use whatever git or network auth is already
  configured; never prompt for, store, or echo a secret.
