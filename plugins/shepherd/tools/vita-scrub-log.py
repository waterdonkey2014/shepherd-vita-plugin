#!/usr/bin/env python3
"""Make a copy of a log (or any text file) that's safe to attach to a public issue.

usage: vita-scrub-log.py IN [OUT]      (OUT defaults to IN with .scrubbed before the extension; never overwrites IN)
       vita-scrub-log.py --check FILE   (exit 1 if FILE still holds anything this tool would remove)

Replaces, keeping the numbers people need (timings, sizes, clocks, error codes):
- home folders and their user names: /Users/<name>, /home/<name>, C:\\Users\\<name>, /Volumes/<drive name> -> <home> / <volume>
- e-mail addresses -> <email>
- IPv4 addresses (except 0.0.0.0, 127.x and the documentation ranges) -> <ip>
- MAC addresses -> <mac>
- 32-hex-digit console / account IDs (PSID, OpenPSID, IDPS-like) -> <id32>
- 17-digit Steam IDs (7656119...) -> <steamid>
- PSN / account names after "account", "user", "psn", "login", "online id" labels -> <name>
Standard library only, Python 3.8+. Read-only towards the input.
"""
import os, re, sys

RULES = [
    (re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\s]+"), r"<home>"),
    (re.compile(r"/Users/[^/\s]+"), r"<home>"),
    (re.compile(r"/home/[^/\s]+"), r"<home>"),
    (re.compile(r"/Volumes/[^/\n]+?(?=/|\s|$)"), r"<volume>"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), r"<email>"),
    (re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b"), r"<mac>"),
    (re.compile(r"\b7656119\d{10}\b"), r"<steamid>"),
    (re.compile(r"\b[0-9A-Fa-f]{32}\b"), r"<id32>"),
    (re.compile(r"(?i)\b(account|user(?:name)?|psn|login|online[ _-]?id)(\s*[:=]\s*)\S+"), r"\1\2<name>"),
]
IPV4 = re.compile(r"\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b")


def _ip(m):
    a, b, c, d = (int(x) for x in m.groups())
    if max(a, b, c, d) > 255:
        return m.group(0)                      # not an address (a version number, a timestamp)
    if (a, b, c, d) == (0, 0, 0, 0) or a == 127:
        return m.group(0)
    if (a, b, c) in ((192, 0, 2), (198, 51, 100), (203, 0, 113)):
        return m.group(0)                      # documentation ranges are already safe
    return "<ip>"


def scrub(text):
    for rx, rep in RULES:
        text = rx.sub(rep, text)
    return IPV4.sub(_ip, text)


def main(argv):
    if len(argv) >= 2 and argv[0] == "--check":
        with open(argv[1], encoding="utf-8", errors="replace") as f:
            t = f.read()
        if scrub(t) != t:
            print("scrub-log: FILE STILL HOLDS PRIVATE DATA: " + argv[1])
            return 1
        print("scrub-log: clean: " + argv[1])
        return 0
    if not argv or len(argv) > 2:
        print(__doc__)
        return 2
    src = argv[0]
    dst = argv[1] if len(argv) == 2 else "{0}.scrubbed{1}".format(*os.path.splitext(src))
    if os.path.abspath(dst) == os.path.abspath(src):
        print("scrub-log: refusing to overwrite the input")
        return 2
    with open(src, encoding="utf-8", errors="replace") as f:
        t = f.read()
    out = scrub(t)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(out)
    print("scrub-log: wrote {0} ({1} changes)".format(dst, sum(1 for a, b in zip(t.splitlines(), out.splitlines()) if a != b)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
