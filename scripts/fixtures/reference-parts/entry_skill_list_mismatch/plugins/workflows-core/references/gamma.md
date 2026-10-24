# Gamma steps

<!-- reference-entry-files
entry check-it holds=1,3
partial check-it 4.0 "never infer"
-->

<!-- entry: check-it -->
Scope: the steps a run takes before it reads a deliverable.

**The principle.** A run reads only what is merged.

## 1. Hard rules

1. Never push to the default branch.
2. `check-it` is fatal by design.
<!-- /entry -->

## 2. `make-it` — the producer entry point

Make the deliverable and hand it off.

<!-- entry: check-it -->
## 3. `check-it` — the entry point

### 3.1 Gate

Run before any expensive work.

### 3.2 The state table

| Row | State |
|---|---|
| A | merged |

```text
## 4. Not a heading — a fenced line
```
<!-- /entry -->

## 4. Reporting

<!-- entry: check-it -->
### 4.0 The downstream classes

*Never infer an artifact's merged-ness from a sibling's gate.* Check each one.
<!-- /entry -->

Each artifact is in one class, and a class is advisory where nothing gates it.

### 4.1 Outcome line

Print one line.
