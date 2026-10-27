#!/bin/sh
# Release scrub check: refuse a release that carries private paths, personal data or game files.
# usage: tools/scrub-check.sh   (run from the repository root; exit 1 on any hit)
cd "$(dirname "$0")/.." || exit 2
fail=0
hit () { echo "SCRUB: $1"; fail=1; }
# private paths and machine names
grep -rIn --exclude-dir=.git -E '/Volumes/|/Users/' . --exclude=scrub-check.sh && hit "private path"
# your own private words (drive, folder and machine names), one regex per line in an untracked .scrub-extra file
[ -f .scrub-extra ] && grep -rIn --exclude-dir=.git -E -f .scrub-extra . --exclude=scrub-check.sh --exclude=.scrub-extra && hit "private word"
# personal data
grep -rIn --exclude-dir=.git -E '@icloud\.com|@gmail\.com' . && hit "e-mail address"
# game files / binaries that must never ship
find . -path ./.git -prune -o -type f \( -name '*.dll' -o -name '*.vpk' -o -name '*.suprx' -o -name '*.self' -o -name '*.pack' -o -name '*.shv' -o -name '*.bank' -o -name '*.assets' \) -print | grep . && hit "binary / game file"
[ "$fail" = 0 ] && echo "scrub check: clean"
exit $fail
