#!/bin/sh
# Shepherd plugin: the user's choice about sending new Vita findings back to the Shepherd project.
# The choice belongs to one project folder, and a git worktree counts as its own folder: a new project or a new worktree is
# asked once, and a folder that has answered is never asked again, in that session or later. The answer is one word -- on,
# review or off -- in a small file in the plugin's data folder; nothing is written into the user's project. No file = never asked.
#   sharing.sh [note]               print the note for Claude (run by the SessionStart hook); reads only
#   sharing.sh get                  print this folder's choice: on | review | off | unset; reads only
#   sharing.sh set on|review|off    save this folder's choice
# Sends nothing anywhere. `note` and `get` always exit 0 so they can never block a session.
data=${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/shepherd-shepherd-vita}
data=${data%/}
start=${CLAUDE_PROJECT_DIR:-$PWD}
top=$(cd "$start" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null) || top=
[ -n "$top" ] || top=$(cd "$start" 2>/dev/null && pwd -P) || top=
[ -n "$top" ] || top=$start
# file name: the folder's path made safe (its last 150 characters) plus a checksum, so every folder gets its own file
key=$(printf '%s' "$top" | tr -c 'A-Za-z0-9' '-' | tail -c 150)-$(printf '%s' "$top" | cksum | cut -d' ' -f1)
file=$data/choices/$key

choice=
[ -r "$file" ] && choice=$(head -n 1 "$file" 2>/dev/null | tr -d ' \t\r' | tr 'A-Z' 'a-z')
case $choice in on|review|off) ;; *) choice=unset ;; esac

q () { printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"; }
setcmd="CLAUDE_PLUGIN_DATA=$(q "$data") CLAUDE_PROJECT_DIR=$(q "$top") sh $(q "$0") set"

case ${1:-note} in
get) echo "$choice"; exit 0 ;;
set)
  word=$(printf '%s' "${2:-}" | tr 'A-Z' 'a-z')
  case $word in on|review|off) ;; *) echo "usage: sharing.sh set on|review|off" >&2; exit 2 ;; esac
  { mkdir -p "$data/choices" && printf '%s\n%s\n' "$word" "$top" > "$file.tmp.$$" && mv -f "$file.tmp.$$" "$file"; } 2>/dev/null \
    || { rm -f "$file.tmp.$$" 2>/dev/null; echo "could not save the choice in $file" >&2; exit 1; }
  echo "saved: $word for $top"; exit 0 ;;
note) ;;
*) echo "usage: sharing.sh [note | get | set on|review|off]" >&2; exit 2 ;;
esac

case $choice in
unset) echo "Shepherd plugin (PS Vita porting): the user hasn't been asked yet, for this project folder, whether to send new findings back to the Shepherd project. The first time this session uses a Shepherd skill or does Vita porting work, ask them once, in one short question: send new findings back to Shepherd so the engine and its knowledge base improve? Choices: yes, send them / yes, but show me each one first / no thanks. Save the answer at once (on, review or off) and never ask again in this folder, in this session or later. If this session isn't Vita porting work, ignore this note." ;;
on) echo "Shepherd plugin (PS Vita porting): for this project folder the user chose to send new findings back to the Shepherd project. When Vita porting work here learns something new (a device-run result, a fix, a failure, a measurement, a gotcha), write it up with the vita-record-discovery skill, keep it in their project, then send it as a GitHub issue and give them the link in one line." ;;
review) echo "Shepherd plugin (PS Vita porting): for this project folder the user chose to send new findings back to the Shepherd project, but to see each one first. When Vita porting work here learns something new, write it up with the vita-record-discovery skill, keep it in their project, show them the issue text, and send it only when they say yes." ;;
off) echo "Shepherd plugin (PS Vita porting): for this project folder the user chose not to send findings back to the Shepherd project. Still write new findings up in their project with the vita-record-discovery skill, but don't offer to send them or bring sharing up again." ;;
esac
label=$choice; [ "$choice" = unset ] && label="not asked yet"
echo "This folder: $top. Choice: $label. The choice covers this folder only: a different project or a new git worktree is asked once on its own. Save or change it (the user can change it any time just by asking you) with: $setcmd on|review|off -- then confirm in one line. The engine and the plugin work exactly the same whichever they pick. Nothing is ever collected automatically: findings only leave as GitHub issues under the user's own account, never with game files, private paths, credentials or their private code."
exit 0
