#!/bin/sh
# vita-pull-logs.sh -- copy an app's logs from a PS Vita memory card to this computer. READ-ONLY: it never writes, deletes or changes
# anything on the card and never ejects it.
#
# On the Vita: VitaShell -> START -> USB (the memory card appears as a drive). Then:
#   sh vita-pull-logs.sh --data-dir data/myport                 copy ux0:data/myport's logs to ./vita-logs/<date-time>/
#
# Options:
#   --data-dir DIR    the app's folder on the card, relative to its root (e.g. data/myport)     [required]
#   --card PATH       the mounted card (default: found under /Volumes, /media, /run/media)
#   --dest DIR        where to copy (default ./vita-logs/<date-time>)
#   --wait MIN        wait up to MIN minutes for the card to appear (default 0)
#   --dumps-days N    also copy crash dumps (ux0:data/psp2core-*.psp2dmp) changed in the last N days (default 3; 0 = none)
#   --all-files       copy every file of DIR, not only text logs (*.txt *.log *.tsv *.csv *.json *.md)
#   --stats           run vita-runlog.py stats on each copied file that has SM measure lines
# What it copies: the matching files of DIR with their sub-folders (an app that keeps per-app log folders keeps them apart -- the
# next start of the same app overwrites its logs, so copy before re-running), recent crash dumps, and card-manifest.txt (every file
# of DIR with size and time, plus the card's free space). macOS "._" files are skipped (knowledge base GT-012).
# A memory card is a drive with VitaShell/, app/ and data/ at its root and no gc/ (a game card mounted through VitaShell has gc/).
set -u

DATA_DIR= CARD= DEST= WAIT_MIN=0 DUMP_DAYS=3 ALL=0 STATS=0
while [ $# -gt 0 ]; do
	case "$1" in
	--data-dir) DATA_DIR=${2:-}; shift 2 ;;
	--card) CARD=${2:-}; shift 2 ;;
	--dest) DEST=${2:-}; shift 2 ;;
	--wait) WAIT_MIN=${2:-0}; shift 2 ;;
	--dumps-days) DUMP_DAYS=${2:-3}; shift 2 ;;
	--all-files) ALL=1; shift ;;
	--stats) STATS=1; shift ;;
	-h|--help) sed -n '2,22p' "$0"; exit 0 ;;
	*) echo "vita-pull-logs: unknown option $1" >&2; exit 2 ;;
	esac
done
[ -n "$DATA_DIR" ] || { echo "vita-pull-logs: --data-dir is required (e.g. --data-dir data/myport)" >&2; exit 2; }
DATA_DIR=${DATA_DIR#/}
DATA_DIR=${DATA_DIR#ux0:}
DATA_DIR=${DATA_DIR#/}

is_card() { [ -d "$1/VitaShell" ] && [ -d "$1/app" ] && [ -d "$1/data" ] && [ ! -e "$1/gc" ]; }

find_card() {
	for root in /Volumes /media/"${USER:-x}" /run/media/"${USER:-x}" /media; do
		[ -d "$root" ] || continue
		for v in "$root"/*; do
			[ -d "$v" ] || continue
			if is_card "$v" && [ -d "$v/$DATA_DIR" ]; then echo "$v"; return 0; fi
		done
	done
	for root in /Volumes /media/"${USER:-x}" /run/media/"${USER:-x}" /media; do   # a card without the app folder: say so later
		[ -d "$root" ] || continue
		for v in "$root"/*; do
			[ -d "$v" ] && is_card "$v" && { echo "$v"; return 0; }
		done
	done
	return 1
}

if [ -z "$CARD" ]; then
	waited=0
	while ! CARD=$(find_card); do
		if [ "$waited" -ge $((WAIT_MIN * 60)) ]; then
			echo "vita-pull-logs: no Vita memory card found (VitaShell -> START -> USB, then retry; or pass --card PATH)" >&2
			exit 1
		fi
		[ "$waited" -eq 0 ] && echo "waiting up to $WAIT_MIN min for the card ..."
		sleep 5
		waited=$((waited + 5))
	done
fi
is_card "$CARD" || { echo "vita-pull-logs: $CARD does not look like a Vita memory card (needs VitaShell/, app/, data/; no gc/)" >&2; exit 1; }
SRC="$CARD/$DATA_DIR"
if [ ! -d "$SRC" ]; then
	echo "vita-pull-logs: $SRC not found; folders in $CARD/data:" >&2
	ls "$CARD/data" >&2
	exit 1
fi

[ -n "$DEST" ] || DEST="./vita-logs/$(date +%Y%m%d-%H%M%S)"
# the destination must not be on the card -- checked BEFORE anything is created (lexically, and through the nearest existing folder)
CARD_ABS=$(cd "$CARD" && pwd -P)
CARD_LEX=$(cd "$CARD" && pwd -L)
case "$DEST" in /*) DEST_LEX=$DEST ;; *) DEST_LEX=$(pwd -L)/$DEST ;; esac
near=$DEST_LEX
while [ ! -d "$near" ]; do near=$(dirname "$near"); done
NEAR_ABS=$(cd "$near" && pwd -P)
for p in "$DEST_LEX/" "$NEAR_ABS/"; do
	case "$p" in "$CARD_ABS"/*|"$CARD_LEX"/*) echo "vita-pull-logs: --dest is on the card; refusing (read-only tool)" >&2; exit 1 ;; esac
done
mkdir -p "$DEST" || exit 1
DEST_ABS=$(cd "$DEST" && pwd -P)

copied=0
LIST="$DEST_ABS/.pull-list.$$"
if [ "$ALL" = 1 ]; then
	find "$SRC" -type f ! -name '._*' > "$LIST"
else
	find "$SRC" -type f ! -name '._*' \( -name '*.txt' -o -name '*.log' -o -name '*.tsv' -o -name '*.csv' -o -name '*.json' \
		-o -name '*.md' \) > "$LIST"
fi
while IFS= read -r f; do
	rel=${f#"$SRC"/}
	mkdir -p "$DEST_ABS/$(dirname "$rel")" && cp -p "$f" "$DEST_ABS/$rel" && copied=$((copied + 1))
done < "$LIST"
rm -f "$LIST"

dumps=0
if [ "$DUMP_DAYS" -gt 0 ] 2>/dev/null; then
	for f in $(find "$CARD/data" -maxdepth 1 -type f -name 'psp2core-*.psp2dmp' -mtime -"$DUMP_DAYS" 2>/dev/null); do
		mkdir -p "$DEST_ABS/coredumps" && cp -p "$f" "$DEST_ABS/coredumps/" && dumps=$((dumps + 1))
	done
fi

{
	echo "# card-manifest: every file under $DATA_DIR (a listing only), pulled $(date)"
	find "$SRC" -type f -ls
	echo "# free space"
	df -k "$CARD"
} > "$DEST_ABS/card-manifest.txt" 2>/dev/null

echo "copied $copied file(s) from $SRC"
[ "$dumps" -gt 0 ] && echo "copied $dumps crash dump(s) from the last $DUMP_DAYS day(s) into coredumps/ -- the app crashed"
echo "into $DEST_ABS (the card was only read; eject it yourself when done)"

if [ "$STATS" = 1 ] && command -v python3 > /dev/null 2>&1; then
	HERE=$(cd "$(dirname "$0")" && pwd -P)
	find "$DEST_ABS" -type f \( -name '*.txt' -o -name '*.log' \) | while IFS= read -r f; do
		grep -q 'SM [A-Z]' "$f" 2>/dev/null && python3 "$HERE/vita-runlog.py" stats "$f"
	done
fi
exit 0
