# lib.sh — shared helpers for the LC11 measurements. Sourced by every s*.sh.
# Everything runs in $ROOT/work/<name>/ : origin.git (bare), A (the run), B (the other writer).
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SLUG=acme-api
PRD=specifications/PRD-A-1-x
IMPL=$PRD/implementation.md
FUP=$PRD/follow-ups.md
FB=$PRD/dev-workflows/feedback.md          # the "_session.md-like" appended session file (**/dev-workflows/** union)
RESUME=$PRD/dev-workflows/resume.md         # an overwritten shape (-merge)
REG=security/$SLUG
DELIV=$PRD/prd.md                           # a deliverable (OTHER path)
NOTE=notes/team.md                          # a user's own file (OTHER path)

# Isolate from the user's own git configuration (theirs carries pull.rebase=true, core.autocrlf=input).
cat > "$ROOT/gitconfig" <<'EOF'
[init]
	defaultBranch = main
[advice]
	detachedHead = false
EOF
export GIT_CONFIG_GLOBAL="$ROOT/gitconfig" GIT_CONFIG_NOSYSTEM=1 GIT_EDITOR=true GIT_TERMINAL_PROMPT=0
export LC_ALL=C

# Print a command, run it, print its exit status. Output (stdout+stderr) is shown verbatim.
run() { echo "\$ $*"; "$@" 2>&1; local rc=$?; echo "[exit $rc]"; return $rc; }
say() { echo; echo "### $*"; }

# The verbatim block session-branch.py's ensure_attributes() writes (ATTRIBUTES list, 2026-10-27 main).
install_attrs() {
  local repo=$1 f
  f=$(git -C "$repo" rev-parse --git-path info/attributes)
  case "$f" in /*) ;; *) f="$repo/$f";; esac
  mkdir -p "$(dirname "$f")"
  cat >> "$f" <<'EOF'
# BEGIN workflows-core session-branch: written by session-branch.py, do not edit
**/dev-workflows/** merge=union
dev-workflows-feedback/** merge=union
dev-workflows-cost/** merge=union
**/implementation.md merge=union
**/follow-ups.md merge=union
**/_security.md merge=union
**/*-implementation-gaps.md merge=union
**/dev-workflows/resume.md -merge
**/pr-draft.md -merge
security/*/register.json -merge
security/*/register.md -merge
# END workflows-core session-branch
EOF
}

# A run record: rec <repo> <seq> <at> <hash8> <origin> <title> <status>
rec() {
  local repo=$1 seq=$2 at=$3 h=$4 origin=$5 title=$6 status=$7
  mkdir -p "$repo/$REG/runs"
  printf '{\n  "seq": %d,\n  "at": "%s",\n  "findings": [\n    {"origin": "%s", "title": "%s", "status": "%s"}\n  ]\n}\n' \
    "$seq" "$at" "$origin" "$title" "$status" > "$repo/$REG/runs/$(printf %04d "$seq")-${at//[:-]/}-$h.json"
}
rebuild() { python3 -I "$ROOT/rebuild.py" "$1" "$SLUG"; }

setup_repos() {   # setup_repos <workdir>
  local w=$1
  rm -rf "$w"; mkdir -p "$w"
  git init -q --bare "$w/origin.git"
  git clone -q "$w/origin.git" "$w/seed" 2>/dev/null
  local s=$w/seed
  git -C "$s" config user.name Seed; git -C "$s" config user.email seed@example.com
  mkdir -p "$s/$PRD/dev-workflows" "$s/notes"
  printf '# PRD A-1\n\nGoal: base.\n' > "$s/$DELIV"
  printf '# Implementation record\n\n## 2026-10-01 base run\n- api: abc1234 on feat/a\n' > "$s/$IMPL"
  printf -- '- [ ] base item 1\n- [ ] base item 2\n' > "$s/$FUP"
  printf '# Feedback\n- base entry\n' > "$s/$FB"
  printf 'last: base\nnext: /design PRD-A-1\n' > "$s/$RESUME"
  printf '# Team notes\n\nline 1\nline 2\nline 3\n' > "$s/$NOTE"
  rec "$s" 1 2026-10-01T00:00:00Z aaaaaaaa scan0:p1 "base finding" open
  rebuild "$s" >/dev/null
  git -C "$s" add -A; git -C "$s" commit -q -m "NOISSUE base"; git -C "$s" push -q origin main 2>/dev/null
  for c in A B; do
    git clone -q "$w/origin.git" "$w/$c" 2>/dev/null
    git -C "$w/$c" config user.name "Writer $c"; git -C "$w/$c" config user.email "$c@example.com"
  done
}

# A session-file commit, as commit-artifacts makes one (pathspec commit of ARTIFACT paths only).
# session <repo> <tag> <seq> <hash8>   — appends to implementation.md, feedback.md, follow-ups.md,
# overwrites resume.md, writes a run record, rebuilds the register.
session() {
  local repo=$1 tag=$2 seq=$3 h=$4
  printf '\n## 2026-10-27 %s run\n- api: %s on feat/%s\n' "$tag" "$h" "$tag" >> "$repo/$IMPL"
  printf -- '- %s entry\n' "$tag" >> "$repo/$FB"
  printf -- '- [ ] %s item\n' "$tag" >> "$repo/$FUP"
  printf 'last: %s\nnext: /implement %s\n' "$tag" "$tag" > "$repo/$RESUME"
  rec "$repo" "$seq" "2026-10-27T0$seq:00:00Z" "$h" "scan-$tag:p$seq" "$tag finding" open
  rebuild "$repo" >/dev/null
  git -C "$repo" add -A -- "$IMPL" "$FB" "$FUP" "$RESUME" "$REG"
  git -C "$repo" commit -q -m "PRD-A-1 Add dev-workflows session artifacts (/$tag)" -- "$IMPL" "$FB" "$FUP" "$RESUME" "$REG"
}

# Snapshot everything a user could notice: HEAD, branch, index (with stages), every worktree file's
# hash (untracked included), status, stash list, rebase state.
snap() {
  local repo=$1
  echo "HEAD $(git -C "$repo" rev-parse HEAD) on $(git -C "$repo" symbolic-ref -q HEAD || echo DETACHED)"
  echo "-- index"; git -C "$repo" ls-files -s
  echo "-- worktree"; (cd "$repo" && find . -path ./.git -prune -o -type f -print0 | sort -z | xargs -0 sha256sum)
  echo "-- status"; git -C "$repo" status --porcelain=v1 --untracked-files=all
  echo "-- stash"; git -C "$repo" stash list
  echo "-- rebase dirs"; ls -d "$repo/.git/rebase-merge" "$repo/.git/rebase-apply" 2>/dev/null || echo none
}

# compare two snapshot files, print IDENTICAL or the diff
cmpsnap() { local a b; a=$(cat "$1"); b=$(cat "$2")
  if [ "$a" = "$b" ]; then echo "SNAPSHOT IDENTICAL"; else echo "SNAPSHOT DIFFERS:"; diff -u <(printf '%s\n' "$a") <(printf '%s\n' "$b") | sed -n '3,$p'; fi; }

# LC11's broad form, as decided: rebase the run's own commits onto origin/<default>; on a stop whose
# every conflicted path is a register.json/register.md, rebuild that register, add, continue; on any
# other stop, abort and print today's lines. settle <repo> [rebase options...]
settle() {
  local repo=$1; shift
  run git -C "$repo" rebase "$@" origin/main
  local n=0
  while [ -d "$repo/.git/rebase-merge" ] || [ -d "$repo/.git/rebase-apply" ]; do
    n=$((n+1)); [ $n -gt 20 ] && { echo "LOOP GUARD"; break; }
    local un; un=$(git -C "$repo" diff --name-only --diff-filter=U)
    echo "stop $n — conflicted: $(echo $un)"
    local other; other=$(printf '%s\n' "$un" | grep -vE '^security/[^/]+/register\.(json|md)$' | grep -v '^$')
    if [ -z "$un" ] || [ -n "$other" ]; then
      echo "=> other conflict (or a stop with no conflicted path): abort"
      run git -C "$repo" rebase --abort
      echo "Specs repo: … push REJECTED … run git -C \"$repo\" pull --rebase --autostash origin main, then git -C \"$repo\" push origin main"
      return 1
    fi
    for slug in $(printf '%s\n' "$un" | sed -nE 's#^security/([^/]+)/register\.(json|md)$#\1#p' | sort -u); do
      run python3 -I "$ROOT/rebuild.py" "$repo" "$slug"
      run git -C "$repo" add -- "security/$slug/register.json" "security/$slug/register.md"
    done
    run git -C "$repo" rebase --continue
  done
  return 0
}
