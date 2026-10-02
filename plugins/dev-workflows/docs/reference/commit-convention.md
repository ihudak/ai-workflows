# Commit convention

**End your commit subject with the work's key, in square brackets.**

```
feat(orders): add order intake [ACME-77-01]
fix(billing): correct proration on mid-cycle upgrade [ACME-77-02]
```

That is the whole rule. Everything below is why it exists and what it buys you.

## Why it matters

The companion `docs-workflows` plugin's `/docs-workflows:document` and `/docs-workflows:release-notes` ground
their prose in the diff that actually shipped. They find that diff two ways: from
`implementation.md`, which [`/implement`](../commands/implement.md) writes for the work it did, and
from a scan of your repository's commit messages for the key.

The scan is what finds **everything the plugin did not do itself** — the commit you wrote by hand
after the session ran out, the fix a colleague pushed, the follow-up nobody ran a command for. A
commit whose subject names the key — any commit but a merge commit — is one those commands can find. A commit that names nothing is
invisible to them, and the release note or the documentation page comes out thinner than the work
was.

**Put the key on your branch's own commits, not only on the pull request.** The scan reads no merge
commit, so a key that only a merge commit carries — your own `git merge -m`, or the pull-request
title a forge writes into the merge commit it makes — is not found, and the branch's work goes
unread. A squash merge is different: the forge writes the title into the one commit it lands, which
the scan does read.

## Where the key comes from

It is the `key:` in the frontmatter of the folder you are working in — the same key the folder is
named for. `/implement` also puts it in the branch name it creates (`<prefix>/<key>-<slug>`), so if
you are on that branch it is already in front of you. Working on one Epic, it is that Epic's key
rather than its PRD's — the key `/implement` writes for an Epic's work, and one the scan finds both
for that Epic and for its PRD. The scan matches a key only whole — set off from the text around it,
as the brackets do — so a key run into further letters, digits, `-` or `_`, as in `ACME-77-01-fix`,
is not found.

## If you also use a tracker

Add its identifier as a trailer:

```
feat(orders): add order intake [ACME-77-01]

Work-Item: CU-8x9f2a1
```

The plugin never mints, validates, or looks that identifier up — it records it as `workitem_key` in
the folder's frontmatter if you put it there, preserves it across every rewrite, and includes it in
the commit scan. Your own tracker integration can do whatever it likes with the trailer.

## Why the subject and not a trailer

A trailer does not survive `git log --oneline`. The person deciding what their commit should look
like is scrolling the log, and they copy what they see — so a convention that lives only in the
trailer is a convention nobody sees.

## Who writes it

| | |
|---|---|
| [`/vuln`](../commands/vuln.md) | commits for you without asking, writing the subject itself; only the push and the pull request are put to you. It has no `--no-commit` |
| [`/implement`](../commands/implement.md), [`/upgrade`](../commands/upgrade.md) | commit for you without asking, writing the subject themselves; only the push and the pull request are put to you. `--no-commit` opts out, and then **you** write that commit |

So the convention is documented here rather than left implicit in what the plugin emits: whenever
you decline the commit, or pick the work up later, or push a fix nobody ran a command for, you are
the one writing the subject the scan will look for.

## See also

- `workflows-core:implementation-format` — the record `/implement`
  writes, the scan that supplements it, and the different boundary each consumer takes.
- [`/implement`](../commands/implement.md) — where the branch and the handover happen.
