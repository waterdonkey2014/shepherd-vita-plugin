#!/bin/sh
# Release scrub check: refuse a release that carries private paths, personal data or game files.
# usage: tools/scrub-check.sh   (run from the repository root; exit 1 on any hit)
cd "$(dirname "$0")/.." || exit 2
fail=0
hit () { echo "SCRUB: $1"; fail=1; }
# private paths and machine names
grep -rIn --exclude-dir=.git -E '/Volumes/|/Users/' . --exclude=scrub-check.sh && hit "private path"
# your own private words (drive, folder and machine names), one regex per line in an untracked .scrub-extra file; exact public
# strings that contain one (e.g. this repository's own links under your account name) go in an untracked .scrub-allow file, one
# extended regex per line: they are removed from a hit line before the line is checked again
if [ -f .scrub-extra ]; then
  t=$(mktemp "${TMPDIR:-/tmp}/scrub.XXXXXX") || exit 2
  grep -rIn --exclude-dir=.git -E -f .scrub-extra . --exclude=scrub-check.sh --exclude=.scrub-extra --exclude=.scrub-allow > "$t"
  if [ -f .scrub-allow ]; then
    while IFS= read -r re; do
      [ -n "$re" ] || continue
      sed -E "s#$re##g" "$t" > "$t.x" && mv "$t.x" "$t"
    done < .scrub-allow
  fi
  grep -E -f .scrub-extra "$t" && hit "private word"
  rm -f "$t" "$t.x"
fi
# personal data
grep -rIn --exclude-dir=.git -E '@icloud\.com|@gmail\.com' . && hit "e-mail address"
# game files / binaries that must never ship
find . -path ./.git -prune -o -type f \( -name '*.dll' -o -name '*.vpk' -o -name '*.suprx' -o -name '*.self' -o -name '*.pack' -o -name '*.shv' -o -name '*.bank' -o -name '*.assets' \) -print | grep . && hit "binary / game file"
[ "$fail" = 0 ] && echo "scrub check: clean"
exit $fail
