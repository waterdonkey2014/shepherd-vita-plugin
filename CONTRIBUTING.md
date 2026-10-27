# Contributing a Vita discovery

Open an issue with the "Vita discovery" template (or a pull request editing an entries file). Include:

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
- Entries get the next free ID in their file (VH / GT / TR / FA / EX). Never renumber an existing entry.
- Don't include game files, copyrighted assets, private paths or credentials.

## Tools
Changes to `plugins/shepherd/tools/` need `python3 tests/test_tools.py` to pass, and a new check needs a test that fails without it
(a negative control). Tools stay standard-library Python 3.8+ / POSIX sh, read-only towards the user's memory card, and MIT.

