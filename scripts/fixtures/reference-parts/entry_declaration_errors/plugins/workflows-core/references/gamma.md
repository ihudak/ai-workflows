# Gamma steps

<!-- reference-entry-files
entry check-it holds=1
entry check-it holds=2
entry Check_It holds=1
entry make-it holds=one
partial check-it 1 never infer
partial ghost 1 "never infer"
entries check-it holds=1
-->

<!-- entry: check-it -->
## 1. `check-it` — the entry point

Never infer an artifact's merged-ness from a sibling's gate.
<!-- /entry -->

## 2. `make-it` — the producer entry point

Make the deliverable and hand it off.
