# Epsilon steps

<!-- reference-entry-files
entry check-it holds=1,1,3,3.1
partial check-it 3.2 "never infer"
partial check-it 1 "never infer"
entry make-it holds=2.1
partial make-it 2 "hand it off"
partial make-it 2.2 "hand it off"
-->

<!-- entry: check-it -->
## 1. `check-it` — the entry point

Never infer an artifact's merged-ness from a sibling's gate.
<!-- /entry -->

## 2. `make-it` — the producer entry point

### 2.1 Gate

Make the deliverable.

### 2.2 Hand-off

Hand it off.
