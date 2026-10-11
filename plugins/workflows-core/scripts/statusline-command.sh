#!/usr/bin/env bash
# Claude Code status line — multi-line, truecolor RGB gradient
# Line 1: session-name  version  agent  cwd  project_dir  added_dirs
# Line 2: repo/dir  git-branch  context-bar  emoji%  tokens  cost  velocity  model
# Line 3: effort  thinking  duration  context sizes
# Line 4: 5h rate-limit bar  weekly rate-limit bar

input=$(cat)

# ── helpers ─────────────────────────────────────────────────────────────────
rgb()   { printf '\033[38;2;%s;%s;%sm' "$1" "$2" "$3"; }
bold()  { printf '\033[1m'; }
reset() { printf '\033[0m'; }
dim()   { printf '\033[2m'; }
PIPE="$(dim)$(rgb 80 80 80)|$(reset)"

# ── JSON fields ──────────────────────────────────────────────────────────────
cwd=$(echo "$input"            | jq -r '.workspace.current_dir // .cwd // ""')
project_dir=$(echo "$input"    | jq -r '.workspace.project_dir // ""')
added_dirs=$(echo "$input"     | jq -r '(.workspace.added_dirs // []) | join(" 📂 ")')
git_branch=$(echo "$input"     | jq -r '.workspace.git_worktree // ""')
model=$(echo "$input"          | jq -r '.model.display_name // ""')
used_pct=$(echo "$input"       | jq -r '.context_window.used_percentage // ""')
remaining_pct=$(echo "$input"  | jq -r '.context_window.remaining_percentage // ""')
total_in_tok=$(echo "$input"   | jq -r '.context_window.total_input_tokens // ""')
total_out_tok=$(echo "$input"  | jq -r '.context_window.total_output_tokens // ""')
ctx_win_size=$(echo "$input"   | jq -r '.context_window.context_window_size // ""')
session_id=$(echo "$input"     | jq -r '.session_id // ""')
session_name=$(echo "$input"   | jq -r 'if (.session_name | type) == "string" and (.session_name | length) > 0 then .session_name else "" end')
version=$(echo "$input"        | jq -r '.version // ""')
transcript=$(echo "$input"     | jq -r '.transcript_path // ""')
effort=$(echo "$input"         | jq -r '.effort.level // ""')
thinking=$(echo "$input"       | jq -r '.thinking.enabled // ""')
agent_name=$(echo "$input"     | jq -r '.agent.name // ""')

five_pct=$(echo "$input"       | jq -r '.rate_limits.five_hour.used_percentage  // ""')
five_reset=$(echo "$input"     | jq -r '.rate_limits.five_hour.resets_at        // ""')
week_pct=$(echo "$input"       | jq -r '.rate_limits.seven_day.used_percentage  // ""')
week_reset=$(echo "$input"     | jq -r '.rate_limits.seven_day.resets_at        // ""')

# ── repo name ────────────────────────────────────────────────────────────────
repo_name=""
if [ -n "$project_dir" ] && [ "$project_dir" != "null" ]; then
  repo_name=$(basename "$project_dir")
elif [ -n "$cwd" ] && [ "$cwd" != "null" ]; then
  repo_name=$(basename "$cwd")
fi

# ── git branch (live, skipping optional locks) ───────────────────────────────
branch=""
if [ -n "$cwd" ] && [ "$cwd" != "null" ]; then
  branch=$(GIT_OPTIONAL_LOCKS=0 git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null)
  if [ -z "$branch" ]; then
    branch=$(GIT_OPTIONAL_LOCKS=0 git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
  fi
fi
[ -z "$branch" ] && branch="$git_branch"

# ── git diff stats (code velocity) ───────────────────────────────────────────
git_added=0
git_removed=0
if [ -n "$cwd" ] && [ "$cwd" != "null" ]; then
  diff_stat=$(GIT_OPTIONAL_LOCKS=0 git -C "$cwd" diff --shortstat HEAD 2>/dev/null)
  if [ -n "$diff_stat" ]; then
    ins=$(echo "$diff_stat" | grep -oE '[0-9]+ insertion' | grep -oE '[0-9]+')
    del=$(echo "$diff_stat" | grep -oE '[0-9]+ deletion'  | grep -oE '[0-9]+')
    [ -n "$ins" ] && git_added=$ins
    [ -n "$del" ] && git_removed=$del
  fi
fi

# ── session cost + lines stats from transcript ───────────────────────────────
session_cost=""
lines_added=""
lines_removed=""
session_start_ts=""

# 1. Try reading cost directly from the JSON input (several candidate field names)
cost_direct=$(echo "$input" | jq -r '
  .cost.total_cost_usd //
  .cost.session_cost_usd //
  .session.cost_usd //
  .costUSD //
  empty' 2>/dev/null)
if [ -n "$cost_direct" ] && [ "$cost_direct" != "null" ]; then
  session_cost=$(printf "%.4f" "$cost_direct")
fi

# ── plugin-family cost snapshot (Option B enabler) ────────────────────────────
# Persist the authoritative session cost (.cost.total_cost_usd) so the
# family's terminal cost phase can cross-check its transcript-computed
# estimate. Overwrites a single-object snapshot each render (bounded size).
# Fully silent — never alters the rendered status line, never fails the render.
if [ -n "$cost_direct" ] && [ "$cost_direct" != "null" ] \
   && [ -n "$session_id" ] && [ "$session_id" != "null" ]; then
  _dw_snap_dir="$HOME/.claude/dev-workflows/cost-snapshots"
  if mkdir -p "$_dw_snap_dir" 2>/dev/null; then
    printf '{"ts":"%s","cost_usd":%s}\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$session_cost" \
      > "$_dw_snap_dir/${session_id}.json" 2>/dev/null
  fi
fi

# Helper: sum costUSD from a JSONL file using jq (handles spacing variants)
_sum_cost_jq() {
  local f="$1"
  jq -r 'select(.costUSD != null) | .costUSD' "$f" 2>/dev/null \
    | awk '{s+=$1} END{if(s>0) printf "%.4f", s}'
}

# Helper: sum costUSD via grep fallback (no jq line-by-line needed)
_sum_cost_grep() {
  local f="$1"
  grep -oE '"costUSD"\s*:\s*[0-9]+(\.[0-9]+)?' "$f" 2>/dev/null \
    | grep -oE '[0-9]+(\.[0-9]+)?' \
    | awk '{s+=$1} END{if(s>0) printf "%.4f", s}'
}

if [ -n "$transcript" ] && [ "$transcript" != "null" ] && [ -f "$transcript" ]; then
  # cumulative cost from JSONL: only needed when direct JSON field was absent
  if [ -z "$session_cost" ]; then
    cost_raw=$(_sum_cost_jq "$transcript")
    if [ -z "$cost_raw" ]; then
      cost_raw=$(_sum_cost_grep "$transcript")
    fi
    [ -n "$cost_raw" ] && session_cost="$cost_raw"
  fi

  # lines added/removed from transcript linesAdded / linesRemoved fields
  la=$(jq -r 'select(.linesAdded != null) | .linesAdded' "$transcript" 2>/dev/null | tail -1)
  lr=$(jq -r 'select(.linesRemoved != null) | .linesRemoved' "$transcript" 2>/dev/null | tail -1)
  if [ -z "$la" ]; then
    la=$(grep -o '"linesAdded":[0-9]*' "$transcript" 2>/dev/null | tail -1 | grep -oE '[0-9]+')
  fi
  if [ -z "$lr" ]; then
    lr=$(grep -o '"linesRemoved":[0-9]*' "$transcript" 2>/dev/null | tail -1 | grep -oE '[0-9]+')
  fi
  [ -n "$la" ] && lines_added="$la"
  [ -n "$lr" ] && lines_removed="$lr"

  # session start: first timestamp in transcript, the value of `"timestamp":"…"`
  # (cut takes the fourth `"`-field; a pattern over the quoted pair would match
  # the `":"` between key and value first). GNU date parses it with `-d`; BSD date
  # (macOS) has no `-d`, so parse the seconds part with `-j -f`, in UTC, which the
  # trailing Z says it is
  first_ts=$(grep -oE '"timestamp":"[0-9T:Z.+-]+"' "$transcript" 2>/dev/null | head -1 | cut -d'"' -f4)
  if [ -n "$first_ts" ]; then
    session_start_ts=$(date -d "$first_ts" "+%s" 2>/dev/null) \
      || session_start_ts=$(TZ=UTC date -j -f '%Y-%m-%dT%H:%M:%S' "${first_ts%%[.Z]*}" "+%s" 2>/dev/null)
  fi
fi

# ── fallback: look for session stats JSON if all above gave no cost ───────────
if [ -z "$session_cost" ] && [ -n "$session_id" ] && [ "$session_id" != "null" ]; then
  stats_file=""
  if [ -n "$transcript" ] && [ "$transcript" != "null" ]; then
    transcript_dir=$(dirname "$transcript")
    candidate="${transcript%.jsonl}.json"
    [ -f "$candidate" ] && stats_file="$candidate"
  fi
  if [ -n "$stats_file" ]; then
    cost_raw=$(jq -r '.costUSD // .cost_usd // .totalCostUSD // empty' "$stats_file" 2>/dev/null)
    [ -n "$cost_raw" ] && [ "$cost_raw" != "null" ] && session_cost=$(printf "%.4f" "$cost_raw")
  fi
fi

# ── session duration ─────────────────────────────────────────────────────────
session_duration=""
if [ -n "$session_start_ts" ] && [ "$session_start_ts" != "null" ]; then
  now_ts=$(date +%s)
  elapsed=$(( now_ts - session_start_ts ))
  if [ "$elapsed" -gt 0 ]; then
    dur_h=$(( elapsed / 3600 ))
    dur_m=$(( (elapsed % 3600) / 60 ))
    dur_s=$(( elapsed % 60 ))
    if [ "$dur_h" -gt 0 ]; then
      session_duration="${dur_h}h${dur_m}m"
    else
      session_duration="${dur_m}m${dur_s}s"
    fi
  fi
fi

# ── gradient context bar (20 blocks, 24-bit RGB) ─────────────────────────────
# green(0,200,80) → yellow(220,200,0) → red(220,40,20)  empty=dark-gray(60,60,60)
context_bar=""
if [ -n "$used_pct" ] && [ "$used_pct" != "null" ]; then
  filled=$(echo "$used_pct" | awk '{v=int($1/5+0.5); if(v<0)v=0; if(v>20)v=20; print v}')
  for i in $(seq 1 20); do
    if [ "$i" -le "$filled" ]; then
      pos=$(echo "$i $filled" | awk '{p=($1-1)/19; if(p<0)p=0; if(p>1)p=1; print p}')
      r=$(echo "$pos" | awk '{
        if($1<=0.5){ r=int(0   + (220-0)   *($1*2)); }
        else       { r=int(220 + (220-220)  *(($1-0.5)*2)); }
        if(r<0)r=0; if(r>255)r=255; print r}')
      g=$(echo "$pos" | awk '{
        if($1<=0.5){ g=int(200 + (200-200) *($1*2)); }
        else       { g=int(200 + (40-200)  *(($1-0.5)*2)); }
        if(g<0)g=0; if(g>255)g=255; print g}')
      b=$(echo "$pos" | awk '{
        if($1<=0.5){ b=int(80  + (0-80)   *($1*2)); }
        else       { b=int(0   + (20-0)   *(($1-0.5)*2)); }
        if(b<0)b=0; if(b>255)b=255; print b}')
      context_bar="${context_bar}$(rgb $r $g $b)█$(reset)"
    else
      context_bar="${context_bar}$(dim)$(rgb 80 80 80)░$(reset)"
    fi
  done
fi

# ── dynamic emoji + colored percentage ───────────────────────────────────────
ctx_emoji=""
ctx_pct_colored=""
if [ -n "$used_pct" ] && [ "$used_pct" != "null" ]; then
  pct_int=$(printf '%.0f' "$used_pct")
  if   [ "$pct_int" -lt 20 ]; then
    ctx_emoji="🟢"
    ctx_pct_colored="$(rgb 0 200 80)${pct_int}%$(reset)"
  elif [ "$pct_int" -lt 70 ]; then
    ctx_emoji="⚡"
    ctx_pct_colored="$(rgb 220 200 0)${pct_int}%$(reset)"
  elif [ "$pct_int" -lt 90 ]; then
    ctx_emoji="🔥"
    ctx_pct_colored="$(rgb 220 120 0)${pct_int}%$(reset)"
  else
    ctx_emoji="🚨"
    ctx_pct_colored="$(rgb 220 40 20)${pct_int}%$(reset)"
  fi
fi

# ── token formatter (k/M suffix) ─────────────────────────────────────────────
fmt_tok() {
  echo "$1" | awk '{
    if ($1 >= 1000000) printf "%.1fM", $1/1000000
    else if ($1 >= 1000) printf "%.1fk", $1/1000
    else printf "%d", $1
  }'
}

# ── rate-limit helpers ────────────────────────────────────────────────────────
rate_bar_segment() {
  local label="$1"
  local pct="$2"
  local reset_epoch="$3"
  local bar="" filled pct_int r g b reset_in

  pct_int=$(printf '%.0f' "$pct")
  filled=$(echo "$pct_int" | awk '{v=int($1/10+0.5); if(v<0)v=0; if(v>10)v=10; print v}')

  for i in $(seq 1 10); do
    if [ "$i" -le "$filled" ]; then
      pos=$(echo "$i" | awk '{p=($1-1)/9; if(p<0)p=0; if(p>1)p=1; print p}')
      r=$(echo "$pos" | awk '{
        if($1<=0.5){ r=int(0+(220-0)*($1*2)); }
        else       { r=220; }
        if(r<0)r=0; if(r>255)r=255; print r}')
      g=$(echo "$pos" | awk '{
        if($1<=0.5){ g=200; }
        else       { g=int(200+(40-200)*(($1-0.5)*2)); }
        if(g<0)g=0; if(g>255)g=255; print g}')
      b=$(echo "$pos" | awk '{
        if($1<=0.5){ b=int(80+(0-80)*($1*2)); }
        else       { b=int(0+(20-0)*(($1-0.5)*2)); }
        if(b<0)b=0; if(b>255)b=255; print b}')
      bar="${bar}$(rgb $r $g $b)█$(reset)"
    else
      bar="${bar}$(dim)$(rgb 80 80 80)░$(reset)"
    fi
  done

  local pct_color
  if   [ "$pct_int" -lt 20 ]; then pct_color="$(rgb 0 200 80)"
  elif [ "$pct_int" -lt 70 ]; then pct_color="$(rgb 220 200 0)"
  elif [ "$pct_int" -lt 90 ]; then pct_color="$(rgb 220 120 0)"
  else                              pct_color="$(rgb 220 40 20)"
  fi

  reset_in=""
  if [ -n "$reset_epoch" ] && [ "$reset_epoch" != "null" ]; then
    now=$(date +%s)
    diff=$(( reset_epoch - now ))
    if [ "$diff" -gt 0 ]; then
      h=$(( diff / 3600 ))
      m=$(( (diff % 3600) / 60 ))
      reset_in=" $(dim)$(rgb 140 140 140)resets ${h}h${m}m$(reset)"
    fi
  fi

  printf '%s' "$(dim)$(rgb 140 140 140)${label}$(reset) ${bar} ${pct_color}${pct_int}%$(reset)${reset_in}"
}

# ══ LINE 1 — session identity + paths ════════════════════════════════════════
line1=""

# session name / ID — tag emoji + bold yellow
_session_label=""
if [ -n "$session_name" ] && [ "$session_name" != "null" ]; then
  _session_label="$session_name"
elif [ -n "$session_id" ] && [ "$session_id" != "null" ]; then
  if [ "${#session_id}" -le 12 ]; then
    _session_label="$session_id"
  else
    _session_label="${session_id:0:8}"
  fi
fi
if [ -n "$_session_label" ]; then
  line1="${line1}🏷️  $(bold)$(rgb 220 180 0)${_session_label}$(reset)"
fi

# version — dim gray
if [ -n "$version" ] && [ "$version" != "null" ]; then
  [ -n "$line1" ] && line1="${line1} ${PIPE} "
  line1="${line1}$(dim)$(rgb 140 140 140)v${version}$(reset)"
fi

# agent name — robot + orange
if [ -n "$agent_name" ] && [ "$agent_name" != "null" ]; then
  [ -n "$line1" ] && line1="${line1} ${PIPE} "
  line1="${line1}🦾 $(rgb 220 140 0)${agent_name}$(reset)"
fi

# tilde for home-dir substitution (no backslash)
tilde="~"

# cwd — folder emoji + sky blue
if [ -n "$cwd" ] && [ "$cwd" != "null" ]; then
  [ -n "$line1" ] && line1="${line1} ${PIPE} "
  cwd_display="${cwd/#$HOME/$tilde}"
  line1="${line1}📁 $(rgb 80 180 255)${cwd_display}$(reset)"
fi

# project dir (only if different from cwd)
if [ -n "$project_dir" ] && [ "$project_dir" != "null" ] && [ "$project_dir" != "$cwd" ]; then
  [ -n "$line1" ] && line1="${line1} ${PIPE} "
  project_dir_display="${project_dir/#$HOME/$tilde}"
  line1="${line1}🗂️  $(dim)$(rgb 100 160 220)${project_dir_display}$(reset)"
fi

# added dirs
if [ -n "$added_dirs" ] && [ "$added_dirs" != "null" ] && [ "$added_dirs" != "" ]; then
  [ -n "$line1" ] && line1="${line1} ${PIPE} "
  added_dirs_display="${added_dirs//$HOME/$tilde}"
  line1="${line1}📂 $(dim)$(rgb 100 160 220)${added_dirs_display}$(reset)"
fi

# ══ LINE 2 — repo  branch  context  cost  velocity  model ════════════════════
line2=""

# repo name — bold yellow
if [ -n "$repo_name" ]; then
  line2="${line2}$(bold)$(rgb 220 180 0)${repo_name}$(reset)"
fi

# git branch — leaf + bold cyan
if [ -n "$branch" ]; then
  [ -n "$line2" ] && line2="${line2} ${PIPE} "
  line2="${line2}🌿 $(bold)$(rgb 0 200 220)(${branch})$(reset)"
fi

# context bar
if [ -n "$context_bar" ]; then
  [ -n "$line2" ] && line2="${line2} ${PIPE} "
  line2="${line2}${context_bar}"
fi

# dynamic emoji + colored pct
if [ -n "$ctx_emoji" ]; then
  line2="${line2} ${ctx_emoji} ${ctx_pct_colored}"
fi

# session cost — money bag + yellow
if [ -n "$session_cost" ]; then
  [ -n "$line2" ] && line2="${line2} ${PIPE} "
  line2="${line2}💰 $(rgb 220 200 0)\$${session_cost}$(reset)"
fi

# code velocity (git diff)
if [ "$git_added" -gt 0 ] || [ "$git_removed" -gt 0 ]; then
  [ -n "$line2" ] && line2="${line2} ${PIPE} "
  line2="${line2}$(rgb 0 200 80)+${git_added}$(reset) $(rgb 220 40 20)-${git_removed}$(reset)"
fi

# lines added/removed from transcript
if [ -n "$lines_added" ] || [ -n "$lines_removed" ]; then
  [ -n "$line2" ] && line2="${line2} ${PIPE} "
  la_disp="${lines_added:-0}"
  lr_disp="${lines_removed:-0}"
  line2="${line2}✏️  $(rgb 0 200 80)+${la_disp}$(reset) $(rgb 220 40 20)-${lr_disp}$(reset) $(dim)$(rgb 140 140 140)lines$(reset)"
fi

# model — robot + magenta
if [ -n "$model" ] && [ "$model" != "null" ]; then
  [ -n "$line2" ] && line2="${line2} ${PIPE} "
  line2="${line2}🤖 $(rgb 200 60 220)${model}$(reset)"
fi

# ══ LINE 3 — effort  thinking  duration  token counts ════════════════════════
line3=""

# effort level — colored badge
if [ -n "$effort" ] && [ "$effort" != "null" ]; then
  case "$effort" in
    low)    effort_color="$(rgb 0 200 80)"  ; effort_emoji="🔋" ;;
    medium) effort_color="$(rgb 220 200 0)" ; effort_emoji="⚡" ;;
    high)   effort_color="$(rgb 220 120 0)" ; effort_emoji="🔥" ;;
    xhigh)  effort_color="$(rgb 220 40 20)" ; effort_emoji="🚀" ;;
    max)    effort_color="$(rgb 255 0 80)"  ; effort_emoji="💥" ;;
    *)      effort_color="$(rgb 160 160 160)"; effort_emoji="🔩" ;;
  esac
  line3="${line3}${effort_emoji} $(dim)$(rgb 140 140 140)effort:$(reset)${effort_color}${effort}$(reset)"
fi

# thinking enabled
if [ -n "$thinking" ] && [ "$thinking" != "null" ]; then
  [ -n "$line3" ] && line3="${line3} ${PIPE} "
  if [ "$thinking" = "true" ]; then
    line3="${line3}🧠 $(rgb 160 80 220)thinking:on$(reset)"
  else
    line3="${line3}💭 $(dim)$(rgb 120 120 120)thinking:off$(reset)"
  fi
fi

# session duration — clock + teal
if [ -n "$session_duration" ]; then
  [ -n "$line3" ] && line3="${line3} ${PIPE} "
  line3="${line3}⏱️  $(rgb 0 180 160)${session_duration}$(reset)"
fi

# token counts — in / out / window-size
tok_seg=""
if [ -n "$total_in_tok" ] && [ "$total_in_tok" != "null" ] && [ "$total_in_tok" != "0" ]; then
  in_fmt=$(fmt_tok "$total_in_tok")
  tok_seg="${tok_seg}$(dim)$(rgb 140 140 140)in:$(reset)$(rgb 100 180 255)${in_fmt}$(reset)"
fi
if [ -n "$total_out_tok" ] && [ "$total_out_tok" != "null" ] && [ "$total_out_tok" != "0" ]; then
  out_fmt=$(fmt_tok "$total_out_tok")
  [ -n "$tok_seg" ] && tok_seg="${tok_seg} "
  tok_seg="${tok_seg}$(dim)$(rgb 140 140 140)out:$(reset)$(rgb 180 140 255)${out_fmt}$(reset)"
fi
if [ -n "$ctx_win_size" ] && [ "$ctx_win_size" != "null" ] && [ "$ctx_win_size" != "0" ]; then
  win_fmt=$(fmt_tok "$ctx_win_size")
  [ -n "$tok_seg" ] && tok_seg="${tok_seg} "
  tok_seg="${tok_seg}$(dim)$(rgb 140 140 140)win:$(reset)$(dim)$(rgb 160 160 160)${win_fmt}$(reset)"
fi
if [ -n "$tok_seg" ]; then
  [ -n "$line3" ] && line3="${line3} ${PIPE} "
  line3="${line3}🪙 ${tok_seg}"
fi

# ══ LINE 4 — rate limits ═════════════════════════════════════════════════════
line4=""

if [ -n "$five_pct" ] && [ "$five_pct" != "null" ]; then
  seg=$(rate_bar_segment "5h" "$five_pct" "$five_reset")
  line4="${line4}${seg}"
fi

if [ -n "$week_pct" ] && [ "$week_pct" != "null" ]; then
  [ -n "$line4" ] && line4="${line4} ${PIPE} "
  seg=$(rate_bar_segment "7d" "$week_pct" "$week_reset")
  line4="${line4}${seg}"
fi

# ══ output ════════════════════════════════════════════════════════════════════
output=""
[ -n "$line1" ] && output="${line1}"
if [ -n "$line2" ]; then
  [ -n "$output" ] && output="${output}\n${line2}" || output="${line2}"
fi
if [ -n "$line3" ]; then
  [ -n "$output" ] && output="${output}\n${line3}" || output="${line3}"
fi
if [ -n "$line4" ]; then
  [ -n "$output" ] && output="${output}\n${line4}" || output="${line4}"
fi
printf '%b' "${output}"
