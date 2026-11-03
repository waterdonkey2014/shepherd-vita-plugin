#!/bin/sh
# Shepherd plugin, SessionStart hook: tells Claude whether the user wants new Vita findings sent back to the Shepherd project.
# The choice is one word in the plugin's data folder: on | review | off (no file = never asked). This script only prints text
# for Claude; it writes nothing, sends nothing anywhere, and always exits 0 so it can never block a session.
dir=${CLAUDE_PLUGIN_DATA:-$HOME/.claude/plugins/data/shepherd-shepherd-vita}
file=${dir%/}/sharing
choice=
[ -r "$file" ] && choice=$(tr -d ' \t\r\n' 2>/dev/null < "$file" | tr 'A-Z' 'a-z')
case $choice in on|review|off) ;; *) choice=unset ;; esac

case $choice in
unset) echo "Shepherd plugin (PS Vita porting): the user hasn't been asked yet whether to send new findings back to the Shepherd project. The first time this session uses a Shepherd skill or does Vita porting work, ask them once, in one short question: send new findings back to Shepherd so the engine and its knowledge base improve? Choices: yes, send them / yes, but show me each one first / no thanks. Save the answer as on, review or off and don't ask again. If this session isn't Vita porting work, ignore this note." ;;
on) echo "Shepherd plugin (PS Vita porting): the user chose to send new findings back to the Shepherd project. When Vita porting work here learns something new (a device-run result, a fix, a failure, a measurement, a gotcha), write it up with the vita-record-discovery skill, keep it in their project, then send it as a GitHub issue and give them the link in one line." ;;
review) echo "Shepherd plugin (PS Vita porting): the user chose to send new findings back to the Shepherd project, but to see each one first. When Vita porting work here learns something new, write it up with the vita-record-discovery skill, keep it in their project, show them the issue text, and send it only when they say yes." ;;
off) echo "Shepherd plugin (PS Vita porting): the user chose not to send findings back to the Shepherd project. Still write new findings up in their project with the vita-record-discovery skill, but don't offer to send them or bring sharing up again." ;;
esac
label=$choice; [ "$choice" = unset ] && label="not asked yet"
echo "Their choice: $label, kept in $file. They can change it any time just by asking you: write on, review or off to that file (create the folder if needed) and confirm in one line. The engine and the plugin work exactly the same whichever they pick. Nothing is ever collected automatically: findings only leave as GitHub issues under the user's own account, never with game files, private paths, credentials or their private code."
exit 0
