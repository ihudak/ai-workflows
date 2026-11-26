# Open-bracket negative control — this file MUST fail the gate

Every violation below is a dash form after an opening bracket that no closing bracket
follows: the bracketed branch of the gate needs the closing bracket, and the bare branch
refuses an opening bracket before the id, so this form passed both. It fails ONLY on the
open-bracket branch, so deleting that branch makes this file PASS — and a negative control
that passes is a broken gate, which `--selftest` catches. One line per prefix, and two that
end on the id, so the selftest pins each prefix and each alternation's end-of-line case.

- [US-3 here, an opening bracket and no closing one.
- [AC-3, then a comma.
- [SM-3; then a semicolon.
- [SMC-3) then a parenthesis.
- [UC-3 here.
- [FR-n here, a placeholder.
- [AD-X here, an uppercase placeholder.
- [SEC-3 here.
- [TH-3 here.
- [DT-3 here.
- [SM-C3 here, the legacy counter-metric.
- A line ending on one: [US-4
- And on the legacy one: [SM-C4
