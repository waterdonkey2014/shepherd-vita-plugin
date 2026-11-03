# Contributing a Vita discovery

Open an issue with the template that fits -- **Vita discovery** (a finding, success or failure), **Device measurement** (numbers from a
real Vita) or **Game port report** (how a game runs) -- or a pull request editing an entries file. Before attaching any log, run it through
`plugins/shepherd/tools/vita-scrub-log.py` (it strips home paths, console / Steam IDs, addresses and account names, and keeps the
numbers). For a discovery, include:

1. **The problem** you hit (error codes, symptoms).
2. **The technique** or fix you tried.
3. **How it's implemented** (enough for someone else to repeat it).
4. **Hardware and software**: Vita model (PCH-1000 / PCH-2000 / PS TV), firmware, CFW / plugins, SDK and library versions.
5. **Results**: what changed, with measurements where you have them (and how you measured: see the `vita-measure` skill).
6. **Limits**: where it doesn't apply, what it conflicts with, what it costs (memory, battery, exactness).
7. **Evidence**: logs, numbers, a repro.

Failed experiments are valuable -- submit them too.

## Review
- New entries start as **EXPERIMENTAL** (off-device evidence) or **OBSERVED** (seen working, evidence incomplete).
- **VERIFIED** needs a device measurement (or a named reproducible measurement) that a reviewer can follow.
- AI-generated claims are not accepted as verified without evidence.
- Every entry carries a **Source** line: maintainers (which kit) or community (the issue, the reporter's device), and whether the
  maintainers have reproduced it. Community findings keep their status label (OBSERVED / EXPERIMENTAL / VERIFIED with the reporter's
  device evidence) and say "reproduced by maintainers: not yet" until we have; they are never silently mixed with our own.
- Entries get the next free ID in their file (VH / GT / TR / FA / EX). Never renumber an existing entry.
- Don't include game files, copyrighted assets, private paths or credentials.

## Tools
Changes to `plugins/shepherd/tools/` need `python3 tests/test_tools.py` to pass, and a new check needs a test that fails without it
(a negative control). Tools stay standard-library Python 3.8+ / POSIX sh, read-only towards the user's memory card, and MIT.

