"""specs_git_lines.py — every notice and outcome line specs-git.py prints, as its references write it.

Each template in T is the exact text of one line or clause of workflows-core:specs-repo-git, of
workflows-core:addressing §3 or of workflows-core:session-hygiene §7, its <…> placeholders and […] segments as the
source writes them, copied as a literal and never built from pieces of another template. pins() finds each one in
its source, so a reference's wording and the script's cannot drift apart; fill() renders one with the run's values,
and left_behind() renders addressing §3's left-behind line, whose repeated clause no single template holds. Python
standard library only; loaded by specs-git.py only for the subcommands that need it.

A template that is a piece of another line says, in the comment above it, how a renderer puts it in.
"""

import posixpath
import re

# specs-repo-git §5's notice blocks, compared line for line with its three fenced blocks.
G0 = """⚠ SPECS REPO — THIS RUN'S ARTIFACTS WILL NOT BE COMMITTED

Found:    <SPECS_PATH> is on a detached HEAD (<sha7>), not on a branch.
Not done: this run's feedback, cost, follow-ups, and resume pointer will NOT be
          committed and will NOT reach the plugin maintainer. A commit made here
          would be reachable from no branch and eligible for deletion by git's
          garbage collector, so the plugin refuses to make one.
Fix:      git -C "<SPECS_PATH>" switch -c rescue/<YYYY-MM-DD>
If ignored: the artifacts stay in your working tree, uncommitted and intact; the
          next run's preflight picks them up once HEAD is on a branch — the one
          Fix creates, or an existing one you rejoin instead with
          git -C "<SPECS_PATH>" switch <branch>"""

G1 = """⚠ SPECS REPO — UNCOMMITTED FILES THAT ARE NOT THE PLUGIN'S

Found:    <SPECS_PATH> has <N> uncommitted change(s) outside the plugin's
          artifact area: <path list>
Not done: the preflight did not switch branches, and did not commit or push
          these files. Those files are yours, and switching branches would
          carry them along. This run's own artifacts WILL still be committed at
          the end of the run — commit-artifacts stages only the §2.1 artifact
          paths.
Fix:      git -C "<SPECS_PATH>" status
          git -C "<SPECS_PATH>" add <path list> && git -C "<SPECS_PATH>" commit
If ignored: nothing is lost — your files stay uncommitted, and this run's
          artifacts are committed alongside them. But the preflight ends here
          on EVERY later run too, so the leftover flush and the branch
          settle (stages 2-3) stay skipped until these paths are committed
          or removed. A deliverable whose handoff was declined — "just
          write the files" — is the usual cause, and it is a supported
          state — this is what it costs."""

G2 = """⚠ SPECS REPO — ON A BRANCH THIS PLUGIN DID NOT CREATE

Found:    <SPECS_PATH> is on branch `<branch>`, which is neither the default
          branch (`<default>`) nor a plugin branch (idea/ prd/ ard/ spec/
          epics/ design/ ready/ brd/ frames/ kb/ conformance/).
Not done: the preflight did not switch away from it — the plugin manages only
          branches it created. This run's artifacts WILL be committed on
          `<branch>`, and not pushed.
Fix:      git -C "<SPECS_PATH>" switch <default>
If ignored: the artifacts land on `<branch>` and reach the maintainer when you
          push or merge that branch; run Fix only if that is the wrong place
          for them."""

T = {
    "g0": G0,
    "g1": G1,
    "g2": G2,
    # §5's G1 on a branch the run would have left (§4 step 1's landing), and under a run typed mid-run: each replaces
    # the text after its label ("Not done: ", "Fix:      ", "If ignored: ") in G1, rendered on its one line, unwrapped;
    # <path list> on the Fix line is the plain block's second, shell-quoted one. The landing form's Not done by the
    # stay's kind (STAY_KINDS, specs-git.py); g1.merged.fix and g1.merged.if_ignored where the stay's merged flag is
    # set, else the plain Fix and g1.landing.if_ignored. Under a run typed mid-run, whatever the kind: the landing
    # form's Not done, its third alternative, where the run stayed, else the plain one; an empty Fix;
    # g1.midrun.if_ignored.
    "g1.landing.not_done": "the preflight did not switch branches, and did not commit or push these files. Those files are yours, and switching branches would carry them along. This run's own artifacts WILL be committed at the end of the run on <default>, not on <branch>, <which no key of this run names | which is merged into <default> | where <command>'s run in this session was open when this run started>, and your checkout is not moved.",
    "g1.landing.if_ignored": "nothing is lost — your files stay uncommitted, and nothing of this run's is committed with them. But the preflight ends here on EVERY later run too, so the leftover flush and the branch settle (stages 2-3) stay skipped until these paths are committed or removed. A deliverable whose handoff was declined — \"just write the files\" — is the usual cause, and it is a supported state — this is what it costs.",
    # At the run's end, after a landing that did not land the run's whole change (held -- an index.lock at the
    # landing's start among the causes --, held-stuck, there, nothing, landed with a path held alone: stuck set, or
    # end.stopped): the landing form's Not done in its place, by the same kind; its Fix and If ignored stand
    # (specs-repo-git §5). The Specs repo: line it names is the run's outcome line, which §6 prints above the
    # repeated block.
    "g1.landing.not_done.unlanded": "the preflight did not switch branches, and did not commit or push these files. Those files are yours, and switching branches would carry them along. This run's own artifacts were to be committed at the end of the run on <default>, not on <branch>, <which no key of this run names | which is merged into <default> | where <command>'s run in this session was open when this run started>, and your checkout is not moved; the Specs repo: line above this notice says what came of them.",
    # At the run's end, after a landing that landed the run's whole change, no path held alone: the landing form's Not
    # done in its place, by the same kind; its Fix and If ignored stand (specs-repo-git §5).
    "g1.landing.not_done.landed": "the preflight did not switch branches, and did not commit or push these files. Those files are yours, and switching branches would carry them along. This run's own artifacts were committed at the end of the run on <default>, not on <branch>, <which no key of this run names | which is merged into <default> | where <command>'s run in this session was open when this run started>, and your checkout is not moved; the Specs repo: line above this notice names that commit.",
    # The not-committed form (specs-repo-git §5): at the run's end where no stay stands, after a line that committed
    # none of the run's files (nothing, locked, commit-failed, midrun-kept, no-identity, session-not-run) or the
    # end.stopped line -- the plain block's Not done and If ignored in their place, the mid-run form's Not done where no
    # stay stands; Fix stands.
    "g1.not_done.uncommitted": "the preflight did not switch branches, and did not commit or push these files. Those files are yours, and switching branches would carry them along. This run's own artifacts were to be committed at the end of the run — commit-artifacts stages only the §2.1 artifact paths; the Specs repo: line above this notice says what came of them.",
    "g1.if_ignored.uncommitted": "nothing is lost — your files stay uncommitted, and the Specs repo: line above this notice says what came of this run's artifacts. But the preflight ends here on EVERY later run too, so the leftover flush and the branch settle (stages 2-3) stay skipped until these paths are committed or removed. A deliverable whose handoff was declined — \"just write the files\" — is the usual cause, and it is a supported state — this is what it costs.",
    "g1.midrun.if_ignored": "nothing is lost — these may be <command>'s files in progress, and nothing is to be run here while that run is open: let it finish, or end it, first; if you stopped that run, /clear, typing <command> again[ with <keys>], or HEAD leaving the branch ends it. Nothing of this run's is committed with them. Until these paths are committed or removed, the preflight ends here on EVERY later run too, so the leftover flush and the branch settle (stages 2-3) stay skipped.",
    "g1.merged.fix": "git -C \"<SPECS_PATH>\" switch <default> && git -C \"<SPECS_PATH>\" add <path list> && git -C \"<SPECS_PATH>\" commit",
    # §5 part 3: where refs/heads/<default> names no commit and <default-ref> names one, a Fix line that opens with the
    # switch to <default> -- G2's plain and session-branch-itself forms, g1.merged.fix -- has that switch replaced by
    # this, the rest of the line as it stands; judged each time the block is printed.
    "fix.make-default": "git -C \"<SPECS_PATH>\" branch --no-track <default> <default-ref> && git -C \"<SPECS_PATH>\" branch --set-upstream-to=<default-ref> <default>; git -C \"<SPECS_PATH>\" switch --no-guess <default>",
    "g1.merged.if_ignored": "nothing is lost — your files stay uncommitted, and nothing of this run's is committed with them. But the preflight ends here on EVERY later run too, so the leftover flush and the branch settle (stages 2-3) stay skipped until these paths are committed or removed. Fix commits them on <default>, not on <branch>, and where git refuses its switch it commits nothing, git naming the files in its way; committed on <branch>, they make it read unmerged, and no later run removes it. A deliverable whose handoff was declined — \"just write the files\" — is the usual cause, and it is a supported state — this is what it costs.",
    # §5's G2 variants: each replaces the text after its label ("Not done: ", "Fix:      ", "If ignored: ") in G2,
    # rendered on its one line, unwrapped; an empty Fix leaves the label alone (§5: nothing to run, or nothing it can
    # give ready to paste).
    "g2.session.not_done": "the preflight did not switch away from it — the plugin manages only branches it created. This run's artifacts WILL be committed on session/<identity>, the session branch this specs repository uses because its default branch takes no push, and not on <branch>.",
    "g2.session.fix": "",
    "g2.session.if_ignored": "nothing changes for the artifacts, and nothing is to be run for them: they reach <default> through session/<identity>'s pull request.",
    "g2.self.not_done": "the preflight did not switch away from it. It is this specs repository's session branch, which the plugin commits to only while nothing stands on it, so this run's artifacts will NOT be committed.",
    "g2.self.fix": "git -C \"<SPECS_PATH>\" switch <default>",
    "g2.self.if_ignored": "the artifacts stay in your working tree, and the first run after you switch back commits them.",
    # §5: in session-branch mode where §8.1 resolves no identity, nothing is committed in the mode until one is set.
    "g2.no-identity.not_done": "the preflight did not switch away from it — the plugin manages only branches it created. Session-branch mode is on and no identity names its branch, so this run's artifacts will NOT be committed until one is set.",
    "g2.no-identity.fix": "",
    "g2.no-identity.if_ignored": "the artifacts stay in your working tree, and the first run after you set GIT_USER_INITIALS, or git -C \"<SPECS_PATH>\" config user.initials, to your initials commits them.",
    "g2.implement.not_done": "the preflight did not switch away from it — the plugin manages only branches it created. This run changes code here, so its artifacts WILL be committed on the branch it cuts for that, or, if it stops first, on the branch it then stands on — <branch>, or <default> after a fresh start — and not pushed unless that branch is <default> or its name carries one of this plugin's prefixes.",
    "g2.implement.fix": "",
    "g2.implement.if_ignored": "nothing is to be run here: the artifacts stay on that branch until it is pushed or merged, and reach the maintainer then.",
    # The clause naming a stopped run's ends, in g1.midrun.if_ignored, g2.midrun.if_ignored, row.midrun-kept and
    # row.here, takes <keys> as the open run's key set, its keys joined by " and ", where its record holds one, and None
    # where it holds none (open_run_keys, specs-git.py).
    # §5, under a run typed mid-run: replaces every G2 variant's If ignored, its Fix left empty. It names the run's
    # Specs repo: outcome line, which §6 prints at the end above the repeated block, never "the line above", which in
    # the block is its empty Fix line, and at the start is no outcome line at all.
    "g2.midrun.if_ignored": "nothing is to be run here while <command>'s run in this session is open on <branch>: let it finish, or end it, first — if you stopped that run, /clear, typing <command> again[ with <keys>], or HEAD leaving the branch ends it; this run's Specs repo: line, at its end, says what came of its artifacts.",

    # §6's rows, in its order (ROWS below); "silent" prints nothing and has none.
    "row.pushed-plugin": "Specs repo: committed <sha7> (<N> files) on <branch> — pushed",
    "row.pushed-default": "Specs repo: committed <sha7> (<N> files) on <default> — pushed straight to <default>, and no pull request was opened: this plugin lands its session files there without review; to land them through a pull request of your own instead, turn on session-branch mode (§8) with git -C \"<SPECS_PATH>\" config workflows.sessionBranch true — where a container mounts this repository's .git/config read-only, run it on the host",
    "row.pushed-session": "Specs repo: committed <sha7> (<N> files) on session/<identity> — pushed; <F> session file(s) not on <default> yet: merge its pull request, or open one with gh pr create --head session/<identity> --base <default>",
    "row.no-identity": "Specs repo: NOT COMMITTED — session-branch mode is on and no identity names its branch; set GIT_USER_INITIALS (or git config user.initials), and the next run commits these files",
    "row.session-not-run": "Specs repo: NOT COMMITTED — session-branch.py could not run (<the first line of its stderr>); the files stay in your working tree, and the next run commits them",
    "row.not-ours": "Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: this plugin pushes only the default branch and the branches it creates, so <branch> is yours to push; the artifacts reach the maintainer when you push or merge it",
    "row.no-remote": "Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: this specs repo has no origin remote",
    "row.elsewhere": "Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: your git configuration pushes <branch> to <remote>, not to origin, which is the remote this plugin reads; push it where it belongs yourself",
    "row.remote-deleted": "Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: origin has no <branch> any more, so it was renamed or deleted there, and this step does not recreate it; the commit stays on local <branch>",
    # Appended to row.remote-deleted where <branch> is the default branch.
    "row.remote-deleted.default-tail": "; if origin renamed it, git -C \"<SPECS_PATH>\" remote set-head origin --auto names the new one",
    "row.origin-lacks": "Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: origin has no <branch>, and this plugin puts a branch of its own there only by handing off its deliverable; the commit stays on local <branch> until a later handoff of <branch> pushes the branch, or you run git -C \"<SPECS_PATH>\" push -u origin <branch>",
    "row.refused-before": "Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: origin refused pushes to <branch> on <date> (<record>), and every commit since stays on local <branch>; to land the commits on local <branch>, put them on a branch of their own and open a pull request from it — git -C \"<SPECS_PATH>\" branch --no-track session-files-<YYYY-MM-DD> <branch> && git -C \"<SPECS_PATH>\" push -u origin session-files-<YYYY-MM-DD> — then, standing on <branch>, git -C \"<SPECS_PATH>\" reset --keep origin/<branch>; once origin takes pushes to <branch> again, rm \"<record>\"",
    "row.push-refused": "Specs repo: committed <sha7> (<N> files) on <branch> — push REFUSED by origin (<the reason in parentheses>): a rule there takes no push of <branch>, so this is recorded and no later run pushes it; to land the commits on local <branch>, put them on a branch of their own and open a pull request from it — git -C \"<SPECS_PATH>\" branch --no-track session-files-<YYYY-MM-DD> <branch> && git -C \"<SPECS_PATH>\" push -u origin session-files-<YYYY-MM-DD> — then, standing on <branch>, git -C \"<SPECS_PATH>\" reset --keep origin/<branch>; once origin takes pushes to <branch> again, rm \"<record>\"",
    # <sha7> names two commits here: pass a list, the run's commit first.
    "row.scope": "Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: the push would also publish commits that are not this plugin's session-file commits, the oldest <sha7> <subject>, which carries <path>; push <branch> once they are ready to go, and the artifacts go with them",
    # Each replaces "which carries <path>" in row.scope.
    "row.scope.merge": "which is a merge commit",
    "row.scope.no-file": "which changes no file",
    # The push-scope row for the session branch where §8.4's test fails with reason branch-path; its bracketed clause
    # only where failed.sha names a merge commit.
    "row.scope.branch-path": "Specs repo: committed <sha7> (<N> files) on session/<identity> — not pushed: its pull request would also change <path>, which is not one of this plugin's session files[, and the branch's newest merge commit is <merge sha7> <subject>]; push session/<identity> once that change is ready to go, and the artifacts go with it",
    "row.scope.hook": "Specs repo: committed <sha7> (<N> files) on <branch> — not pushed: a pre-commit hook added <path>[, and <M-1> more] to this commit, so it carries more than this plugin's session files; check what the hook added before you push <branch>",
    "row.replayed": "Specs repo: committed <sha7> (<N> files) on <branch> — pushed after a replay: origin's <branch> had moved on, so the run replayed its <K> commit(s) onto it[, <D> of them already there and dropped][; <the register clause>]",
    "row.already-there": "Specs repo: committed <sha7> (<N> files) on <branch> — not pushed, and nothing is left to push: origin's <branch> had moved on and already holds every change <branch> carries, so <branch> now stands on it[; <the register clause>]",
    "row.moved": "Specs repo: committed <sha7> (<N> files) on <branch> — origin's <branch> had moved on, so the run replayed its <K> commit(s) onto it[, <D> of them already there and dropped][; <the register clause>] and moved <branch> there, but <why>; the commits are on local <branch>, and a later run retries the push",
    # The refused form of row.moved: replaces it from "but" on, followed by row.push-refused from "a rule there" on.
    "row.moved.refused": "but push REFUSED by origin (<the reason in parentheses>): ",
    "row.rejected": "Specs repo: committed <sha7> (<N> files) on <branch> — push REJECTED: origin's <branch> has commits this one lacks, and the run could not take them in: <reason clause>; run git -C \"<SPECS_PATH>\" pull --rebase --no-autostash origin <branch>, then git -C \"<SPECS_PATH>\" push origin <branch>",
    "row.failed": "Specs repo: committed <sha7> (<N> files) on <branch> — push FAILED (<reason>); the commit is local and a later run retries it",
    "row.nothing": "Specs repo: no session artifacts to commit",
    "row.locked": "Specs repo: skipped — another session holds the repo (index.lock); the next run picks the artifacts up",
    "row.commit-failed": "Specs repo: NOT COMMITTED — the commit failed (<the first line of git's error or the hook's output>); the artifacts stay staged, and a later run commits them once git accepts the commit (a merge concluded, a hook satisfied)",
    # Followed by the G0 block.
    "row.blocked": "Specs repo: NOT COMMITTED — see the notice below",
    # Followed by the notice that set the flag.
    "row.misrooted": "Specs repo: NOT COMMITTED — SPECS_PATH is misplaced, or the run's environment no longer matches the one it recorded; see the notice below",
    # §4 step 1's landing refused: held for a cause that passes, or for one that will not; the <which no key ...>
    # alternation by the stay's kind (STAY_KINDS, specs-git.py). row.held's tail, like pre.held.failed's, is its second
    # alternative where session-branch mode takes the files from the next run (specs-git.py's mode_takes).
    "row.held": "Specs repo: NOT COMMITTED — this run's preflight stayed on <branch>, <which no key of this run names | which is merged into <default> | where <command>'s run in this session was open when this run started>, and its files could not be committed on <default> without leaving it: <reason clause>; they stay in your working tree, <held for <default>, and the next run tries again | and the next run, in session-branch mode, drops this hold and commits them as that mode commits session files>",
    "row.held-stuck": "Specs repo: NOT COMMITTED — this run's preflight stayed on <branch>, <which no key of this run names | which is merged into <default> | where <command>'s run in this session was open when this run started>, and its files cannot be committed on <default> without leaving it: <reason clause>; they stay in your working tree, and no landing takes them; dropping the hold — as a later run on <default> or in session-branch mode does, or as you can — leaves them ordinary uncommitted files, which a later commit takes: see their change with 'git -C \"<SPECS_PATH>\" show <sha7>', put it on <default> yourself if you want it there, then run 'python3 \"<specs-git.py's path>\" --specs \"<SPECS_PATH>\" land --default-ref <default-ref> --drop-held <sha7>'",
    # §6's mid-run row (§3.5): a here form whose apply refused, or an end with no start that found a run open.
    "row.midrun-kept": "Specs repo: NOT COMMITTED — <command>'s run in this session is still open on <branch>, and this run's own changes could not be committed apart from that run's: <reason clause>; they stay in your working tree, and that run's terminal commit takes them with its own; if you stopped that run, /clear, typing <command> again[ with <keys>], or HEAD leaving the branch ends it, and a later run's commit takes them",
    "row.there": "Specs repo: nothing to commit on <default>, which already holds this run's session-file changes; they were taken out of your working tree on <branch>",
    # §4 step 1's here form: its first alternative on the default branch or a plugin branch, the second on a branch
    # this plugin does not push.
    "row.here": "Specs repo: committed <sha7> (<N> files) on <branch> — not pushed yet: <command>'s run in this session is still open on <branch>, so this run committed what changed since it started and moved nothing under that run; <the next push of <branch> this plugin makes, by that run or a later one, carries it | <branch> is yours to push, as the notice above said>, and that run's files are as they were in your working tree; if you stopped that run, /clear, typing <command> again[ with <keys>], or HEAD leaving the branch ends it",
    # §6's push-rejected row for the session branch (§8.4); the conflict ending replaces "; a later run takes them
    # in and pushes".
    "row.session-rejected": "Specs repo: committed <sha7> (<N> files) on session/<identity> — push REJECTED: origin's session/<identity> has commits this clone lacks, pushed from another clone under the same identity; a later run takes them in and pushes",
    "row.session-rejected.conflict-ending": ", which a later run takes in only once the two clones' copies agree, as this line says",

    # §6's appends and the pieces its paragraphs substitute.
    "app.hook-line": "Specs repo: <path>[, …] is now committed in <sha7>, put there by a pre-commit hook, and not pushed",
    # The older configuration-key record: app.record-key replaces <record>, app.record-unset replaces rm "<record>".
    "app.record-key": "branch.<branch>.workflowsPushRefused",
    "app.record-unset": "git -C \"<SPECS_PATH>\" config --unset branch.<branch>.workflowsPushRefused",
    # Replaces "so this is recorded and no later run pushes it" in row.push-refused; the remedy is then dropped.
    "app.unrecorded": "but this could not be recorded (<error>, the configuration write's), so a later run pushes <branch> again",
    # Once per security/<slug>/ the replay's moves name; each <move> is app.register-move.
    "app.register-clause": "the rebuild of security/<slug>/ renumbered <move>[, <move>…], and the next run that records in that register lists the lines that cite an old number",
    "app.register-move": "[SEC#<from>] → [SEC#<to>] (<origin>, <whose number>)",
    # <whose number> in app.register-move, by the move's side.
    "app.register-move.run": "the local number",
    "app.register-move.remote": "origin's number",
    "app.upstream-error": "; its upstream could not be set (<upstream_error>)",
    # row.moved's <why>, by the first that holds.
    "app.why.later-refused": "a later attempt could not take origin's newer commits in: <reason clause>",
    "app.why.moved-on": "origin's <branch> moved on again during each of its <attempts> attempts",
    "app.why.failed": "the push FAILED (<the status line's bracketed summary and its reason, or no status line>)",
    # The parenthesis of app.why.failed where the last attempt's push printed no status line.
    "app.why.failed.none": "no status line",
    "app.why.stopped": "session-branch.py stopped (<the first line of its stderr>)",
    # Where a later attempt refused with checkout-moved, an earlier one having moved the branch: replaces
    # "so <branch> was not moved;" in reason.checkout-moved inside app.why.later-refused.
    "app.why.checkout-moved": "so <branch> was not moved again;",
    # Session-branch mode (§8), in §6's order.
    "app.session.created": "; this run created local session/<identity> at <base short sha>",
    "app.session.conflict-default": "; merging <default> into session/<identity> left <path>[, …] unsettled — settle them in its pull request",
    "app.session.conflict-origin": "; origin's copy of session/<identity>, pushed from another clone, was not merged in: on <path>[, …] one clone changed what the other clone's copy still holds unchanged (an entry edited or removed, the header edited, the file deleted) — make the two copies agree, by making the same change on the clone that still holds it (standing on <default> there; a pending cost file the other relocated is relocated there too, never deleted by hand) or by undoing it on the other; the next run on the clone you changed commits it, and once that is pushed, a later run here merges and pushes",
    "app.session.sync-error": "; the merge of <default> into session/<identity> could not run (<sync.error>), and the next run tries again",
    # Once for each path unsettled names, then app.session.unsettled.close once after them.
    "app.session.unsettled": "; <path> and session/<identity>'s version of it each hold a change the other lacks, so it was left out of this commit and is as it was in your working tree — git -C \"<SPECS_PATH>\" show session/<identity>:<path> shows the branch's version",
    "app.session.unsettled.close": "; once a copy left out is the branch's version with your own entries added after it, in the line endings your checkout gives the file, the next run commits it, and an edit or removal of an entry the branch your specs checkout stands on holds can then be made again; until then lift will not discard it, so each move of the specs checkout is skipped",
    "app.session.stranded": "; your local <default> still holds <K> commit(s) origin refused, whose files are on session/<identity> now — to drop them, standing on <default>, run python3 \"<the script's path>\" --specs \"<SPECS_PATH>\" lift --branch session/<identity> && git -C \"<SPECS_PATH>\" reset --keep origin/<default> && python3 \"<the script's path>\" --specs \"<SPECS_PATH>\" put-back --branch session/<identity> --default-ref origin/<default>",
    "app.session.unsupported": "; session-branch mode is on for this clone, but this git's merge-tree cannot merge without a checkout (it needs --write-tree and -X), so these files stay on <branch> until git is upgraded",
    # Replaces the push-refused and refused-before remedies from "to land the commits" on, for the session branch.
    "app.session.refused-remedy": "once origin takes pushes to session/<identity>, rm \"<record>\"",
    # Replaces the push-refused remedy from "to land the commits" on where it names the default branch and was
    # recorded; app.mode-on.no-identity replaces "session/<identity>" in it where no identity resolves.
    "app.mode-on": "from the next run on, session files go to session/<identity>, a branch of your own whose pull request lands them (session-branch mode), and these commits' files go there too",
    "app.mode-on.no-identity": "a session branch of your own, once GIT_USER_INITIALS names it",
    # D2: on either decline; <path> is artifacts() of the declared paths git status still lists.
    "app.declined": "; the deliverable at <path> remains uncommitted, as you asked",
    # §6, after a landing: in this order after the row its commit on <default> takes -- app.landed, app.landed.unlisted
    # where the run's start could not list the uncommitted paths, app.start-dirty-kept where the guard left paths out,
    # the register clause, app.held.stuck where a path was held alone -- then app.declined.
    "app.landed": "; this run's preflight stayed on <branch>, <which no key of this run names | which is merged into <default> | where <command>'s run in this session was open when this run started>, so its files were committed on <default> without leaving <branch>, and taken out of your working tree there",
    "app.landed.unlisted": "; its preflight could not list the uncommitted paths, so every session file uncommitted on <branch> went with them",
    # §4 step 1 (1)'s guard (P1): after the here row, after app.landed (and app.landed.unlisted, which never meets it),
    # after the pushed or replayed row of a here form, or after the there and nothing rows of the landing or the here
    # form, the snapshot paths of a class that is not appended that the guard left out of the run's change; <branch>
    # the stayed branch, or HEAD's in the here form.
    "app.start-dirty-kept": "; <path>[, …] stayed out, as they stand in your working tree: uncommitted when this run started, they are left for a later commit on <branch>",
    "app.held.stuck": "; <path>[, …] could not go with them: <reason clause>; they stay in your working tree, and no landing takes them; dropping the hold — as a later run on <default> or in session-branch mode does, or as you can — leaves them ordinary uncommitted files, which a later commit takes: see their change with 'git -C \"<SPECS_PATH>\" show <sha7>', put it on <default> yourself if you want it there, then run 'python3 \"<specs-git.py's path>\" --specs \"<SPECS_PATH>\" land --default-ref <default-ref> --drop-held <sha7>'",

    # §6's reason clauses, by refused.reason, and §4 step 6's own three.
    "reason.conflict": "both sides changed <path>, or the folder holding it, and the run cannot settle it",
    "reason.register-rebuild": "both sides changed the security register <path>, which only a rebuild settles, and this command hands the run no register.py to rebuild it",
    # Where the call carried --register-rebuild: replaces reason.register-rebuild from ", which only" on.
    "reason.register-rebuild.failed": ", which only a rebuild settles, and that rebuild failed",
    "reason.would-overwrite": "moving the checkout would write over <path>[ and <M> more], which you changed, left untracked or ignore — once that is clear, the next run that commits session files on <branch> settles the push itself",
    "reason.cannot-replay": "this git cannot replay without a checkout (its merge-tree needs --write-tree and --merge-base, git 2.40 or later)",
    "reason.in-progress": "a rebase, merge, cherry-pick or revert, or an unresolved conflict, is in progress in the checkout (<path>)",
    "reason.locked": "<path> is held by another git process, or was left by one that died, and this plugin never deletes a lock",
    "reason.push-scope": "the push would now also publish <path's first seven characters>, which is not one of this plugin's session-file commits",
    "reason.checked-out": "another worktree, <path>, has <branch> checked out",
    "reason.fetch-failed": "fetching origin's <branch> failed",
    "reason.branch-moved": "<branch> moved while the run was replaying it",
    "reason.cannot-move": "git could not move the checkout onto the replay (a folder it cannot write, say), and nothing moved",
    "reason.checkout-moved": "the checkout switched to or from <branch> while the run was moving it — another session's preflight or handoff, say — so <branch> was not moved; the next run that commits session files on <branch> settles the push itself",
    "reason.not-run": "session-branch.py could not run (<the first line of its stderr>)",
    "reason.timed-out": "session-branch.py did not finish within 420 s, so <branch> may already stand on the replay (git -C \"<SPECS_PATH>\" log -1 <branch> shows it); the next run whose preflight gets past its guards retries the push where it stands on <branch> or <branch> is a plugin branch",
    "reason.session-mode": "session-branch mode is on, which replays nothing",

    # §6's landing reason clauses, by the landing's refused reason (LAND_REASONS, specs-git.py; locked reuses
    # reason.locked). <onto> is <default>, or HEAD's branch in the here form, which <default> names there too.
    "reason.land.dropped": "this run's copy of <path> drops a line that <onto> does not hold, which only you can settle",
    "reason.land.edited": "this run's copy of <path> changes or removes an entry, or the file's header, that was there when the run started, which only you can settle",
    "reason.land.forms": "<path> has other line endings on <default> than in your working tree",
    "reason.land.deleted": "this run deleted <path>, which <default> holds in another version",
    "reason.land.folder-gone": "<default> does not hold the folder <path> is in",
    # The first where the call carried no --register-rebuild, the second where it did.
    "reason.land.register": "<path> needs its register rebuilt, <and this command hands the run no register.py to rebuild it | and that rebuild failed>",
    "reason.land.moved": "<default> moved twice while the run was committing on it",
    # The alternative by the printed detail (specs-git.py's checked_out_values): a refspec push that failed or was
    # rejected; no-remote; elsewhere; remote-deleted or origin-lacks; a push origin refused, recorded; refused-before,
    # worded as row.refused-before words it; a push origin refused that could be recorded neither way, as
    # app.unrecorded.
    "reason.land.checked-out": "another worktree, <path>, has <default> checked out, and <the push of the commit by refspec failed (<reason>) | there is no origin to push the commit to | your git configuration pushes <default> to <remote>, not to origin | origin has no <default> | origin refuses pushes to <default> (<the refusal>), so from the next run session-branch mode takes these files | origin refused pushes to <default> on <date> (<record>), so from the next run session-branch mode takes these files | origin refuses pushes to <default> (<the refusal>), but this could not be recorded (<error>, the configuration write's), so a later run pushes <default> again>",
    "reason.land.no-preflight": "this run stopped before its preflight, so nothing tells its files from that run's",
    # A run typed mid-run whose start took no snapshot (status could not run, or the start was cut off before taking
    # one), the open run still standing at its end: it commits nothing, by the landing or the here form (specs-repo-git
    # §4 step 1 (1)); on the mid-run row alone.
    "reason.land.no-snapshot": "this run's start took no snapshot of the session files then uncommitted, so nothing tells its files from that run's",
    # An end --resume whose here-form journal could not be finished while the open run still stands; <branch> the
    # journal's, which is HEAD's.
    "reason.land.unfinished": "<branch> moved on without the commit this run was making on it when it was cut off, so that commit was dropped unfinished",

    # The push-rejected remedies, each replacing remedy.rejected in row.rejected (and its Specs preflight: form):
    # not-standing on a branch the run is not standing on, checked-out for that reason, session-wrap around
    # whichever applies in session-branch mode. checkout-moved names none: the line ends at its reason clause.
    "remedy.rejected": "run git -C \"<SPECS_PATH>\" pull --rebase --no-autostash origin <branch>, then git -C \"<SPECS_PATH>\" push origin <branch>",
    "remedy.not-standing": "run git -C \"<SPECS_PATH>\" switch <branch>, git -C \"<SPECS_PATH>\" pull --rebase --no-autostash origin <branch> and git -C \"<SPECS_PATH>\" push origin <branch>, then switch back to <the branch the run stands on>",
    "remedy.checked-out": "run git -C \"<path>\" pull --rebase --no-autostash origin <branch>, then git -C \"<path>\" push origin <branch>",
    "remedy.session-wrap": "run python3 \"<the script's path>\" --specs \"<SPECS_PATH>\" lift --branch session/<identity>, then <the remedy as it reads without this wrapping, from its first git on>, then python3 \"<the script's path>\" --specs \"<SPECS_PATH>\" put-back --branch session/<identity> --default-ref origin/<default>",

    # The preflight's own lines (§1 rule 5, §3.1, §3.4, §3.5, §4 step 6, §8).
    "pre.nonrepo": "Specs preflight: SPECS_PATH is <value>, which <is not a directory | is not in a git repository> — nothing this run writes there is committed or handed off; set SPECS_PATH to your specs repository's top level, where it is set, and re-run.",
    "pre.below-top": "Specs preflight: SPECS_PATH is <value>, below the top level of its repository (<top>) — a specs tree inside a larger repository is unsupported, because this plugin switches branches and commits in the repository SPECS_PATH belongs to, so this run switches and commits nothing there; set SPECS_PATH to a dedicated specs repository's top level.",
    # <git's first error line> reads text.pull-capped where the cap ended the pull.
    "pre.pull-failed": "Specs preflight: could not fast-forward <default> (<git's first error line>); the run goes on from it as it stands",
    "pre.leave-failed": "Specs preflight: could not switch from merged <branch> to <default> (<git's first error line>)",
    # In these three, <the first line of its stderr> is the line the entry point's CLI prints on stderr:
    # specs-git: not run (<why>).
    "pre.merged-unknown": "Specs preflight: could not tell whether <branch> is merged (<the first line of its stderr>), so it reads unmerged",
    "pre.status-failed": "Specs preflight: could not list the uncommitted paths (<the first line of its stderr>), so nothing is staged",
    "pre.scope-failed": "Specs preflight: could not measure what a push of <branch> would publish (<the first line of its stderr>), so <branch> is not pushed",
    "pre.merged-flush": "Specs preflight: <branch> is merged, and this flush committed <sha7> on it, which no run pushes; to land it, standing on <default>, run git -C \"<SPECS_PATH>\" cherry-pick <sha7>",
    "pre.refused": "Specs preflight: <branch> not pushed — origin refused it (<the reason in parentheses>), and this is recorded so no later run pushes it; <the remedy §6's push-refused line gives>",
    # Replaces pre.refused from ", and this is recorded" on.
    "pre.refused.unrecorded": ", and this could not be recorded (<error>), so a later run pushes it again",
    "pre.created.empty": "Specs preflight: created local session/<identity> at <base short sha>; no session file to commit yet",
    "pre.created.committed": "Specs preflight: created local session/<identity> at <base short sha>, and committed <sha7> on it",
    "pre.deleted": "Specs preflight: deleted merged <branch>",
    "pre.delete-failed": "Specs preflight: could not delete merged <branch> (<git's first error line>)",
    "pre.advisory-D": "Specs preflight: <branch> is merged into <default>, which git branch -d cannot see from here — delete it with git -C \"<SPECS_PATH>\" branch -D <branch>",
    # Follows pre.advisory-D or pre.b2-squash where the branch's push-refusal record stands.
    "pre.advisory-D.rm": "rm -f \"<record>\"",
    "pre.pushed-left": "Specs preflight: pushed <N> session-file commit(s) left on <branch>",
    "pre.b2-config": "Specs preflight: <branch> left configuration this container cannot remove — run git -C \"<SPECS_PATH>\" config --remove-section branch.<branch> where .git/config is writable",
    "pre.b2-squash": "Specs preflight: <branch> is merged into <default> by a rebase or a squash, which git branch -d cannot see — delete it with git -C \"<SPECS_PATH>\" branch -D <branch>",
    "pre.b4": "Specs preflight: left <branch> for <default>, since no key of this run names it — the branch and its pull request are as they were",
    # Appended to pre.b4 where the branch holds commits a push would publish.
    "pre.b4.count": "; <N> commit(s) on it are not on origin, and a later run's preflight pushes them where §4 step 5 lets it",
    "pre.stay": "Specs preflight: staying on <branch> — specs_git: misrooted, so no branch is switched (it would have <switched to <default> and deleted it, as it is merged | switched to <default>, as no key of this run names it>)",
    # pre.stay's form for a run whose status could not run (specs-repo-git §3.5).
    "pre.stay.unlisted": "Specs preflight: staying on <branch> — the uncommitted paths could not be listed, so no branch is switched (it would have <switched to <default> and deleted it, as it is merged | switched to <default>, as no key of this run names it>)",
    # pre.stay's form under a run typed mid-run (specs-repo-git §3.5), <command> the open run's.
    "pre.stay.midrun": "Specs preflight: staying on <branch> — <command>'s run in this session is still open on it, so no branch is switched (it would have <switched to <default> and deleted it, as it is merged | switched to <default>, as no key of this run names it>)",
    # §3.2's held stage, each held entry by what came of it; <branch> HEAD's.
    "pre.held.landed": "Specs preflight: committed <sha7> (<N> files) on <default>: the session files an earlier run held for it, now committed without leaving <branch> and taken out of your working tree there",
    "pre.held.failed": "Specs preflight: could not commit the session files an earlier run held for <default> (<reason clause>); they stay in your working tree, <and the next run tries again | and the next run, in session-branch mode, drops this hold and commits them as that mode commits session files>",
    "pre.held.stuck": "Specs preflight: the session files an earlier run held for <default> cannot be committed there: <reason clause>; they stay in your working tree, and no landing takes them; dropping the hold — as a later run on <default> or in session-branch mode does, or as you can — leaves them ordinary uncommitted files, which a later commit takes: see their change with 'git -C \"<SPECS_PATH>\" show <sha7>', put it on <default> yourself if you want it there, then run 'python3 \"<specs-git.py's path>\" --specs \"<SPECS_PATH>\" land --default-ref <default-ref> --drop-held <sha7>'",
    # §3.2's held stage, for each here-form journal it finishes with its commit on HEAD's branch, <branch> HEAD's.
    "pre.here.finished": "Specs preflight: finished the commit an earlier run was making on <branch> when it was cut off: <sha7> (<N> files), that run's own session files, committed apart from another run's",
    # §3.4's flush, of a held file changed since it was held.
    "pre.held.changed": "Specs preflight: <path> changed after an earlier run held it for <default>, so it is committed here as it stands, and left out of the held commit",
    "pre.rerun-failed": "Specs preflight: could not switch back to <branch> (<git's first error line>); this run goes on from <current>",
    # The re-run's switch back left undone where status could not run earlier in the run (specs-repo-git §3.5).
    "pre.rerun-stay": "Specs preflight: staying on <current> — the uncommitted paths could not be listed, so no branch is switched (it would have switched back to <branch>, as a key of this run names it)",
    "pre.session-not-run": "Specs preflight: session-branch.py could not run (<the first line of its stderr>)",
    "pre.stopped": "Specs preflight: stopped early (<the error>) — what it did is above, and the next run's preflight goes on from where this one stands",
    # §8: commit-artifacts' report of a lift or put-back around step 2, or a step 4 commit after a lift's commit made the
    # run's, that could not run; printed before the outcome line.
    "end.session-not-run": "Specs repo: session-branch.py could not run (<the first line of its stderr>)",
    "end.stopped": "Specs repo: NOT FINISHED — the terminal step stopped early (<the error>); what it committed or pushed is as it left it, and the next run's preflight flushes the rest",
    # The reason a push or pull the 60 s cap ended gives in place of git's.
    "text.push-capped": "the push did not finish within 60 s",
    "text.pull-capped": "the pull did not finish within 60 s",
    # §8.3: in place of git's first error line where a second unpreserved skipped a wrapped move.
    "text.lift-unpreserved": "lift found <path>[, …] not yet on session/<identity>",
    # §3.2's offline note: carried as start's offline_clause, never printed by the script.
    "text.offline": "offline — ancestry checked against the last-fetched ref",

    # addressing §3 specs-root-check's stop, each form the text inside its label.
    "root.one-line": "SPECS_PATH_INSIDE_TREE: SPECS_PATH is <value>, which <is itself a specifications/ directory | is inside the specifications/ directory | is itself a specs folder, asserting key <key> | holds the specs folder <subdirectory> directly> — every folder lives under $SPECS_PATH/specifications/, so this run would look for and create folders in the wrong place; it wrote nothing under that path, and its cost and feedback are reported here instead. Set SPECS_PATH to <the value the walk found | the directory that holds specifications/> where it is set, and re-run.[ <the value the walk found> is not the top level of its repository (<that repository's top level>), and a specs tree inside a larger repository is unsupported: this plugin switches branches and commits in that repository.]",
    "root.stray": "SPECS_PATH_INSIDE_TREE: SPECS_PATH is <value>, <the top level of its repository | which holds <value>/specifications/>, and holds the specs folder(s) <subdirectory>[, <subdirectory>…] outside <value>/specifications/, where every folder lives. SPECS_PATH names the right directory; move <subdirectory>[, <subdirectory>…] into <value>/specifications/ yourself, commit the move, then re-run — the plugin moves nothing. This run wrote nothing under <value>, and its cost and feedback are reported here instead.[ <value> is not the top level of its repository (<that repository's top level>), and a specs tree inside a larger repository is unsupported: this plugin switches branches and commits in that repository.]",
    "root.two-readings": "SPECS_PATH_INSIDE_TREE: SPECS_PATH is <value>, which holds the specs folder <subdirectory> directly, and nothing on disk says whether <value> is a specs tree under another name or a specs root. If it is a specs tree under another name, its folders belong in a directory named specifications/, and SPECS_PATH names that directory's parent: <move them into <the parent of <value>>/specifications/ yourself, commit the move, and set SPECS_PATH to <the parent of <value>> | set SPECS_PATH to the parent of the specifications/ directory <value> is a mount of, and mount that parent whole rather than the tree alone>, where it is set. If it is a specs root, move <subdirectory> and every other specs folder beside it into <value>/specifications/ yourself and commit the move<, and make <value> the top level of a git repository, which it is not | ; <value> is not the top level of its repository (<that repository's top level>), and a specs tree inside a larger repository is unsupported: this plugin switches branches and commits in that repository>. Then re-run — the plugin moves nothing. This run wrote nothing under that path, and its cost and feedback are reported here instead.",
    # The left-behind line, whole: never filled whole (its clauses repeat); left_behind() renders it from the
    # opening this text holds before root.left-behind.nested, then its pieces.
    "root.left-behind": "<in the two-readings form only: If <value> is a specs tree under another name, m|M>isrooted runs left: <value>/specifications/ (<folder>, …), which belongs in <the value the walk found>/specifications/ | the specs repository's specifications/, and which the first run after SPECS_PATH is fixed searches for keys and commits bookkeeping from, in the wrong place, unless it is moved first; <value>/<bookkeeping directory>/, which belongs at <the value the walk found>/<bookkeeping directory>/ | the same path at the specs repository's top level[, which the first run after SPECS_PATH is fixed commits there in the wrong place unless it is moved first]; …. Move them yourself, commit the move, then re-run — the plugin moves nothing.",
    "root.left-behind.nested": "<value>/specifications/ (<folder>, …), which belongs in <the value the walk found>/specifications/ | the specs repository's specifications/, and which the first run after SPECS_PATH is fixed searches for keys and commits bookkeeping from, in the wrong place, unless it is moved first",
    "root.left-behind.dir": "<value>/<bookkeeping directory>/, which belongs at <the value the walk found>/<bookkeeping directory>/ | the same path at the specs repository's top level[, which the first run after SPECS_PATH is fixed commits there in the wrong place unless it is moved first]",
    "root.left-behind.close": ". Move them yourself, commit the move, then re-run — the plugin moves nothing.",

    # session-hygiene §7's notice, which end's environment comparison prints (D4).
    "env.changed": "Environment changed: started in <the values the line recorded>, now <the values printed now> — nothing more is committed, handed off or recorded here, and what this run already wrote stays where it is. Re-run in the container the run started in.",
}

# The rows of specs-repo-git §6's table that commit-artifacts may end on, in its order.
ROWS = (
    "pushed-plugin", "pushed-default", "pushed-session", "no-identity", "session-not-run", "not-ours", "no-remote",
    "elsewhere", "remote-deleted", "origin-lacks", "refused-before", "push-refused", "scope", "replayed",
    "already-there", "moved", "rejected", "failed", "nothing", "locked", "commit-failed", "blocked", "misrooted",
    "held", "held-stuck", "midrun-kept", "there", "here", "silent",
)

BLOCKS = ("g0", "g1", "g2")
SOURCE_NAMES = {"srg": "specs-repo-git.md", "addressing": "addressing.md", "hygiene": "session-hygiene.md"}


def source_of(tid):
    """Which reference holds template <tid>: addressing §3 for root.*, session-hygiene §7 for env.*, else SRG."""
    if tid.startswith("root."):
        return "addressing"
    if tid.startswith("env."):
        return "hygiene"
    return "srg"


def count_files(n):
    """specs-repo-git §6's file count, singular at one."""
    n = int(n)
    return "(1 file)" if n == 1 else "(%d files)" % n


def artifacts(paths):
    """phase-handoff §4.1's <artifacts>: the paths comma-separated where three or fewer, else '<n> files under
    <dir>', <dir> the nearest directory holding every path, repo-relative ('.' where that is the top level)."""
    paths = list(paths)
    if len(paths) <= 3:
        return ", ".join(paths)
    common = posixpath.commonpath([posixpath.dirname(p) for p in paths])
    return "%d files under %s" % (len(paths), common or ".")


_COMMITTED = re.compile(r"Specs repo: committed \S+ \((?:1 file|\d+ files)\) on (\S+)")


def preflight_form(row_line):
    """specs-repo-git §6, Inside §3.4's flush and retry: a rendered row as the preflight prints it."""
    m = _COMMITTED.match(row_line)
    if m:
        return "Specs preflight: " + m.group(1) + row_line[m.end():]
    if row_line.startswith("Specs repo: "):
        return "Specs preflight: " + row_line[len("Specs repo: "):]
    raise ValueError("preflight_form: not a Specs repo: line: %r" % row_line[:80])


def _close(s, i, opening, closing):
    """The index of the bracket that closes the one at s[i], nested pairs counted."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == opening:
            depth += 1
        elif s[j] == closing:
            depth -= 1
            if depth == 0:
                return j
    raise ValueError("fill: an unbalanced %s at %r" % (opening, s[i:i + 60]))


def _alternatives(inner):
    """The alternatives of a placeholder's inside, split at each ' | ' at its own level."""
    parts, depth, start, k = [], 0, 0, 0
    while k < len(inner):
        ch = inner[k]
        if ch in "<[":
            depth += 1
        elif ch in ">]":
            depth -= 1
        elif depth == 0 and inner.startswith(" | ", k):
            parts.append(inner[start:k])
            k += 3
            start = k
            continue
        k += 1
    parts.append(inner[start:])
    return parts


def _placeholders(text):
    """The placeholders of <text> outside any optional segment nested in it, each a whole balanced <…>."""
    found, i = [], 0
    while i < len(text):
        if text[i] == "<":
            j = _close(text, i, "<", ">")
            found.append(text[i:j + 1])
            i = j + 1
        elif text[i] == "[" and not text.startswith("[SEC#", i):
            i = _close(text, i, "[", "]") + 1
        else:
            i += 1
    return found


def _spans(text):
    """Every key fill() takes in <text>, in order: each placeholder at its own level, optional segments included,
    and, inside an alternation, the placeholders of each alternative, which fill() renders in turn."""
    found, i = [], 0
    while i < len(text):
        if text[i] == "<":
            j = _close(text, i, "<", ">")
            span = text[i:j + 1]
            found.append(span)
            alternatives = _alternatives(span[1:-1])
            if len(alternatives) > 1:
                for alternative in alternatives:
                    found.extend(_spans(alternative))
            i = j + 1
        else:
            i += 1
    return found


def placeholder(tid, start):
    """The placeholder of T[tid] that is <start>, or the one placeholder it begins — any key fill() takes for that
    template, an alternation's whole text and the placeholders inside its alternatives included. ValueError where
    none, or more than one, matches."""
    spans = _spans(T[tid])
    if start in spans:
        return start
    found = sorted({s for s in spans if s.startswith(start)})
    if len(found) != 1:
        raise ValueError("placeholder: %s has %d placeholders beginning %r" % (tid, len(found), start))
    return found[0]


def _value(span, values, used, joined, root):
    value = values.get(span)
    if value is None:
        raise ValueError("fill: no value for %s" % span)
    alternatives = _alternatives(span[1:-1])
    if len(alternatives) > 1:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("fill: %s is an alternation, whose value is the int of an alternative, not %r" % (span, value))
        if not 0 <= value < len(alternatives):
            raise ValueError("fill: %s has no alternative %d" % (span, value))
        named = "<%s>" % alternatives[value]
        if named in root:  # an alternative that names a placeholder of the same template is that placeholder
            return _value(named, values, used, False, root)
        return _render(alternatives[value], values, used, root)
    if isinstance(value, (list, tuple)):
        if joined:
            return ", ".join(str(v) for v in value)
        k = used.get(span, 0)
        if k >= len(value):
            raise ValueError("fill: no value for occurrence %d of %s" % (k + 1, span))
        used[span] = k + 1
        return str(value[k])
    return str(value)


def _render(t, values, used, root):
    out, i = [], 0
    while i < len(t):
        ch = t[i]
        if ch == "<":
            j = _close(t, i, "<", ">")
            span = t[i:j + 1]
            i = j + 1
            joined = False
            for marker in ("[, …]", "[, %s…]" % span, ", …"):
                if t.startswith(marker, i):
                    i += len(marker)
                    joined = True
                    break
            out.append(_value(span, values, used, joined, root))
        elif ch == "[" and not t.startswith("[SEC#", i):
            j = _close(t, i, "[", "]")
            inner = t[i + 1:j]
            i = j + 1
            if all(values.get(p) is not None for p in _placeholders(inner)):
                out.append(_render(inner, values, used, root))
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def fill(template_or_id, values):
    """Render a template (or the template T names by that id) with <values>, keyed by placeholder as the template
    writes it ("<branch>"). In order: (<N> files) by count_files; a list marker — "[, …]", "<P>[, <P>…]", or ", …"
    straight after <P> — dropped, <P> taking its whole list joined by ", "; an optional segment, any balanced […]
    not opening "[SEC#", kept without its brackets where every placeholder in it has a value that is not None and
    dropped whole otherwise; then every placeholder replaced by its value — a list value, with no list marker after
    it, one item per occurrence in order; an alternation (one holding " | " at its own level) by the alternative an
    int picks, itself filled from the same values — an alternative that names a placeholder of the same template
    (root.one-line's "the value the walk found") taking that placeholder's value. A placeholder left with no value,
    and an alternation given anything but an int naming one of its alternatives, raises ValueError naming it, so no
    placeholder reaches a user. A template holding a repeated clause ("; …") is never filled whole: left_behind()
    renders addressing §3's."""
    t = T.get(template_or_id, template_or_id)
    if "; …" in t:
        raise ValueError("fill: %s repeats a clause; render its pieces" % (template_or_id if template_or_id in T else "the template"))
    if "(<N> files)" in t:
        if values.get("<N>") is None:
            raise ValueError("fill: no value for <N>")
        t = t.replace("(<N> files)", count_files(values["<N>"]))
    return _render(t, values, {}, t)


# addressing §3's left-behind line names where each item belongs by an alternation its source leaves unbracketed:
# from the words after "which belongs in" or "which belongs at" to the next ", " or "[".
_BELONGS = re.compile(r"(which belongs (?:in|at) )(.+?) \| (.+?)(?=, |\[|$)")


def left_behind(values, folders, dirs, two_readings):
    """addressing §3's left-behind line: the opening (in the two-readings form, under its first reading), the
    nested specifications/ clause where <folders> is not None (the folders it holds), one bookkeeping-directory
    clause per entry of <dirs> (each a path under <value>, no trailing slash), joined by "; ", and the closing
    sentence, which the source writes after its "; …". <values> holds <value>
    and <the value the walk found> (None where the walk found none, which names where each item belongs instead).
    The clause that a directory is committed in the wrong place is kept for one under documentation/ alone: addressing
    §3 says specs-repo-git §2.1's classifier never stages dev-workflows-feedback/ or dev-workflows-cost/ where a
    misrooted run left them. An empty <folders> is no nested clause, as None is. None where nothing is left."""
    folders = list(folders) if folders else None
    if folders is None and not dirs:
        return None
    whole = T["root.left-behind"]
    opening = whole[:whole.index(T["root.left-behind.nested"])]
    cond = opening[:_close(opening, 0, "<", ">") + 1]
    first, _, other = cond[1:-1].split(": ", 1)[1].rpartition("|")
    vals = dict(values)
    vals[cond] = fill(first, vals) if two_readings else other
    walk = vals.get("<the value the walk found>") is not None

    def belongs(piece):
        return _BELONGS.sub(lambda m: m.group(1) + (m.group(2) if walk else m.group(3)), piece, count=1)

    clauses = []
    if folders is not None:
        clauses.append(fill(belongs(T["root.left-behind.nested"]), dict(vals, **{"<folder>": folders})))
    for d in dirs or []:
        piece = belongs(T["root.left-behind.dir"])
        if not d.startswith("documentation/"):
            piece = piece[:piece.index("[")] + piece[_close(piece, piece.index("["), "[", "]") + 1:]
        clauses.append(fill(piece, dict(vals, **{"<bookkeeping directory>": d})))
    return fill(opening, vals) + "; ".join(clauses) + T["root.left-behind.close"]


def _collapse(text):
    return " ".join(text.split())


def section5_blocks(srg):
    """The fenced blocks of specs-repo-git §5, in order, each as its lines joined by newlines."""
    start = srg.index("\n## 5. ")
    end = srg.index("\n## 6. ", start)
    blocks, cur = [], None
    for line in srg[start:end].split("\n"):
        if line.startswith("```"):
            if cur is None:
                cur = []
            else:
                blocks.append("\n".join(cur))
                cur = None
        elif cur is not None:
            cur.append(line)
    return blocks


def pins(srg, addressing, hygiene):
    """One failure per template its source does not hold: each compared whitespace-collapsed on both sides, save
    §5's three blocks, compared line for line with specs-repo-git §5's fenced blocks."""
    failures = []
    try:
        blocks = section5_blocks(srg)
    except ValueError:
        blocks = []
    for k, tid in enumerate(BLOCKS):
        if k >= len(blocks) or blocks[k] != T[tid]:
            failures.append("%s: not specs-repo-git.md §5's fenced block %d, line for line" % (tid, k + 1))
    sources = {"srg": _collapse(srg), "addressing": _collapse(addressing), "hygiene": _collapse(hygiene)}
    for tid, text in T.items():
        if tid in BLOCKS:
            continue
        src = source_of(tid)
        if _collapse(text) not in sources[src]:
            failures.append("%s: not found in %s" % (tid, SOURCE_NAMES[src]))
    return failures
