---
paths:
  - "**"
---

# Plugin updates

Loaded when any file is read (`paths: "**"`), as near to always-on as a rules file comes: it was always-on in `CLAUDE.md`. Moved out of `CLAUDE.md` to keep it under its 36,000-character warning; evidence is in `docs/maintainers/rationale.md`.

## Updating installed plugins after editing

After pushing an edit, update the affected plugin on each machine so Claude Code picks up the new content:

```bash
claude plugin update dev-workflows@shipwright
claude plugin update product-workflows@shipwright
claude plugin update docs-workflows@shipwright
claude plugin update workflows-core@shipwright
claude plugin update security-workflows@shipwright
```

- **`claude plugin update` requires a restart to apply** — the CLI says so itself.
- **There is no `claude plugin reinstall`.** The verb is `update`. Verify a command against `claude plugin --help` before writing it into `CLAUDE.md` or `.claude/rules/` — agents run what those files say, and a command that does not exist fails in a way that looks like a broken plugin. ([why](../../docs/maintainers/rationale.md#plugin-update-cli))
- **Update `workflows-core` 1.39.0 and `docs-workflows` 1.15.0 together**: the first stops the session commit staging `release-notes.md`, and the second hands that draft off by pull request instead, so a newer `workflows-core` beside an older `docs-workflows` leaves every draft uncommitted with no offer, and the reverse lets the session commit, or the next run's leftover flush, commit a declined draft as a session file — on the checkout's branch, or on the session branch in session-branch mode.
- **Update `workflows-core` 1.40.0 with `dev-workflows` 4.25.0, `product-workflows` 3.34.0 and `docs-workflows` 1.16.0**: the three rely on its `escalation-rules` — the *Required path environment variable unset* rule saying what its *Set* option asks next, and, for `/prd-proposal` and `/brd-proposal`, §0's *A selection carries no text* — which an older `workflows-core` does not carry, so a run beside one loads a reference missing what it was told to follow.
- **Update `workflows-core` 1.40.1 with `dev-workflows` 4.26.0**: 1.40.1's `followup-emission` relies on 4.26.0's `/implement` skipping a follow-up whose line a PRD record carries as `withdraws:`, which an older `/implement` would build.
- **Update `workflows-core` 1.41.0 with `dev-workflows` 4.27.0**: 1.41.0's `require-on-main` adds the stopping row B′ (a run's own branch holding a copy the default branch has changed since), and `/ready`, which maps every stopping row to exactly one finding, maps it from 4.27.0 on — an older `/ready` beside 1.41.0 meets a stopping row its mapping gives no reason for. Take `product-workflows` 3.34.2 with them: its `*_REGISTER_NOT_ON_MAIN` stops have a B′ form, and an older one prints a B′ stop with a consequence that is false for it.
- **Update `workflows-core` 1.42.0 and `dev-workflows` 4.28.0 with `security-workflows` 0.1.0** — installed the first time with `claude plugin install security-workflows@shipwright`: the new plugin loads `security-register-format` and `implementation-format` §5's `unit-branch`, which an older `workflows-core` does not carry; commits its register on bookkeeping paths an older `specs-repo-git` and `session-branch.py` do not stage; files its cost under a `/scan` row of `cost-emission` §7 that an older `workflows-core` lacks, counting Claude Security's agents, which an older `session-cost.py` does not read; and hands its fixes to an `/implement` that continues on the Epic's branch, which an older `dev-workflows` does not. 4.28.0's `/implement` and `/conformance` load `unit-branch` too, so neither runs beside an older `workflows-core`; and an older `/conformance` stops with `CONFORMANCE_NOT_MERGED` on the Epic run before the merge that 1.42.0's `next-phase-offer` offers.
- **Update `prose-style` with `docs-workflows` past 1.1.3** (`claude plugin update prose-style@shipwright`): beside a `prose-style` older than 0.4.0, `/release-notes` records its style check `DEGRADED`.
- **Update the plugin that holds the file you edited — not the one whose workflow you were thinking about.** An update re-fetches exactly one plugin: the shared references, shared agents and family-meta commands are `workflows-core`'s, the product-definition commands and their agents and references `product-workflows`'s, the documentation commands `docs-workflows`'s, the security scan and its `register.py` `security-workflows`'s. Otherwise the run picks up the old content and the change looks like it did not land.
- **`claude plugin marketplace update <marketplace>` does NOT update installed plugins.** It refreshes the *catalogue* — what the marketplace advertises — which is what makes a newly added plugin installable. An already-installed plugin stays at the version it was installed at. Use `claude plugin update` per plugin, or the `/plugins` interface (next bullet). ([why](../../docs/maintainers/rationale.md#plugin-update-cli))
- **The `/plugins` interface inside Claude Code upgrades what is already installed**, and **AutoUpdate** is settable per plugin there, after which nothing above is needed. This is a human step: an agent cannot drive that interface, so it uses the per-plugin `update` command.
- **A renamed plugin blocks marketplace update entirely** — not just its own, but every plugin from that marketplace. The remedy is to remove the marketplace and its plugins and reinstall from scratch (`claude plugin marketplace remove`, then `add`, then install each plugin), and the cost lands on every user, so weigh it before renaming one.
- `claude plugin validate <path>` validates a plugin or marketplace manifest, or the skills, agents and commands in a directory — a local pre-flight cheaper than a failed install. `claude plugin tag [path]` creates a `{name}--v{version}` git tag for a plugin release, **validating that `plugin.json` and any enclosing marketplace entry agree**, as `scripts/validate-catalog.py` also asserts — the last place to catch a disagreement.
