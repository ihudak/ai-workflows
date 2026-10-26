# /prose-style-refresh

Regenerates your organization's overlay from the style-guide source you configure — a set of web pages, a git repository, or a local directory — distilled into the same eight files the baseline has. It never writes into the shipped baseline, and it knows no style guide of its own.

## Who runs it

You do, by typing it, whenever your style guide changes; it is typed-only. The two review commands and the plugins that run the checker then read the overlay it wrote. [Workflow](../workflow.md) shows where the overlay sits.

## Synopsis

```
/prose-style-refresh [--source <url>]... [--from <path>] [--rules <path>] [--dry-run]
```

| Argument | What it does |
|---|---|
| *(none)* | Reads the sources your overlay's `source.yml` declares |
| `--source <url>` | A web page to read this time, in place of `source.yml`; may be repeated |
| `--from <path>` | A local directory or file to read this time, in place of `source.yml` |
| `--rules <path>` | The overlay directory to write, in place of the discovered one |
| `--dry-run` | Print what would change, and write nothing |

## What it needs

- **A source.** With no `--source` or `--from` and no `source.yml`, it asks where your rules come from — it never guesses a URL — and offers to save your answer as `source.yml`, so the next refresh needs no arguments.
- **An overlay directory to write**, the first that resolves of `--rules <path>`, `<repo-root>/.prose-style/rules/` and `$PROSE_STYLE_PATH`. Where none exists yet, it names the directory it would create — by default `.prose-style/rules/` at the repository's top level — and asks before creating it.

## The `source.yml` file

It lives in the overlay directory, beside the rules, and the checker ignores it — only `.md` files there are rules.

```yaml
sources:
  - kind: web                    # pages read over HTTP, listed per baseline file
    pages:
      terminology: ["https://style.example.com/terms"]
      word-list:   ["https://style.example.com/word-list"]
  - kind: git                    # a repository of style documents
    repo: git@github.example.com:org/style-guide.git
    ref: main
    path: docs/style
  - kind: local                  # a directory or file already on disk
    path: ~/company-style-guide/
targets: [terminology, word-list]  # optional; all eight when omitted
mode: layer                        # optional; `replace` marks every file to replace its baseline file
```

Several sources are read in order and merged, a later one winning on a conflict. The page keys are the eight baseline file names, listed in [References](../reference/references.md).

## What it produces

The overlay files, written into the overlay directory — a file that would come out identical is left untouched — and a report, per file, of the rules and terms added, changed and removed and of any source that failed and was skipped, closing with the resolved source, overlay and baseline paths. **The shipped baseline is never a write target**: a `--rules` path inside the installed plugin is refused, since anything written there is lost on the next update.

## See also

- [The overlay](../reference/overlay.md) — how the files this command writes layer over the baseline.
- [Environment](../reference/environment.md) — `$PROSE_STYLE_PATH`, one of the places it writes.
