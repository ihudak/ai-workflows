# Next-phase offer (fixture)

A next-step offer that names a downstream command must also name the merge, and it must
name it truthfully — so the clause is carried as the placeholder `<merge-clause>`,
resolved from the handoff outcome the run actually emitted.

| Handoff outcome | `<merge-clause>` resolves to |
|---|---|
| Pull request opened | `(once the pull request above is merged)` |
| Nothing to commit | `(its inputs are already on the default branch — you can run it now)` |

**Where this rule applies: every next-step offer this plugin prints that names a downstream command whose `require-on-main` gate the offering run feeds.** The `<merge-clause>` placeholder is the convention the `/dev-workflows:alpha*` commands write their offers to, and an offer added to that family carries it. Two offers carry it — `/alpha`'s `### Next step` section and `/alpha-two`'s. Offers outside the family are outside the rule.
