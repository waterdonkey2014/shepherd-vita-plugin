---
name: vita-record-discovery
description: Write up a PS Vita porting finding -- a technique that worked, a failure, a hardware measurement or a gotcha -- in the Shepherd knowledge-base format (ID, status, category, problem, fix, evidence, limits), keep it in the user's project, and prepare it as a contribution. Use after an experiment succeeds or fails on a Vita, after a device run teaches something new, or when the user wants to share a finding.
---

# Recording a Vita discovery

When an experiment ends -- success or failure -- capture it while the evidence is fresh. Keep it short and factual; never invent numbers.

## 1. Classify it
- **VH** hardware fact · **GT** gotcha (a failure and its fix) · **TR** technique that worked · **FA** failed or rejected · **EX** built and
  passing off-device, not yet on a Vita.
- Status: **VERIFIED** only with a device measurement (or a named reproducible measurement); **OBSERVED** if seen working without full
  evidence; **EXPERIMENTAL** if only off-device; **FAILED** with the reason; **THEORETICAL** if not built.
- Check the existing entries first (`vita-knowledge` skill): if it matches one, add evidence to that entry instead of a new one; if it
  contradicts one, say so explicitly.

## 2. Write the entry (same format as the knowledge base)
```
### <ID-placeholder> -- <one-line title>
- Status: <label> (<device model, firmware, CFW / plugins; or "emulated / host">). Category: <area>.
- Problem / fact: <what happened, with error codes>.
- Fix / use: <the technique, enough to repeat it>.
- Evidence: <numbers and how they were measured; log lines>.
- Limits: <where it doesn't apply, conflicts, costs (memory, battery, exactness)>.
```
Leave the ID as a placeholder (e.g. `GT-new`) -- maintainers assign the next free number.

## 3. Keep it locally
Save it in the user's own project notes (e.g. `docs/vita-discoveries.md`) so their future sessions see it. Don't edit the installed plugin's
files (updates replace them).

## 4. Offer to contribute it
Draft an issue for the Shepherd repository using its "Vita discovery" template (problem, technique, implementation, hardware and software,
results, limits, evidence, outcome). Show the draft to the user; only they decide whether and where to post it. Never include game files,
copyrighted assets, private paths, credentials or the user's private code.
