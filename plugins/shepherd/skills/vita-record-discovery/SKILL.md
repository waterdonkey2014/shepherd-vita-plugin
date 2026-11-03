---
name: vita-record-discovery
description: Write up a PS Vita porting finding -- a technique that worked, a failure, a hardware measurement or a gotcha -- in the Shepherd knowledge-base format (ID, status, category, problem, fix, evidence, limits), keep it in the user's project, and send it back to the Shepherd project if the user chose that (asked once, the first time the plugin is used; they can change it any time by asking). Use after an experiment succeeds or fails on a Vita, after a device run teaches something new, or when the user wants to share a finding or change their sharing choice.
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
- Source: <maintainers (Shepherd kit N) | community (issue #, reporter's device)>; reproduced by maintainers: <yes | not yet>.
- Problem / fact: <what happened, with error codes>.
- Fix / use: <the technique, enough to repeat it>.
- Evidence: <numbers and how they were measured; log lines>.
- Limits: <where it doesn't apply, conflicts, costs (memory, battery, exactness)>.
```
Leave the ID as a placeholder (e.g. `GT-new`) -- maintainers assign the next free number.

## 3. Keep it locally
Save it in the user's own project notes (e.g. `docs/vita-discoveries.md`) so their future sessions see it. Don't edit the installed plugin's
files (updates replace them).

## 4. Send it back to Shepherd, if the user chose that
The user's choice is one word in `${CLAUDE_PLUGIN_DATA}/sharing`; the plugin's session-start note states it too. If that path came
through unexpanded (it still starts with a dollar sign), the folder is `~/.claude/plugins/data/shepherd-shepherd-vita/`.
- **No file: they've never been asked.** Ask once, now, in one short question (a multiple-choice question if your tools have one):
  "Send new findings back to the Shepherd project so the engine and its knowledge base improve?" -- *Yes, send them* / *Yes, but show
  me each one first* / *No thanks*. Say that findings go out as public GitHub issues under their account, and that the engine and the
  plugin work the same either way. Save `on`, `review` or `off` (create the folder if needed) and don't ask again.
- **on** -- send it (step 5), then give them the issue link in one line.
- **review** -- show them the issue text; send it only when they say yes.
- **off** -- keep it in their notes and don't bring sharing up.

They can change their mind any time just by asking ("stop sending findings", "send them again", "show me each one first"): write the
new word and confirm in one line. Nothing is ever collected automatically; the plugin has no telemetry.

## 5. How to send it
- Pick the template that fits -- **Vita discovery** (a finding, success or failure), **Device measurement** (numbers from a real Vita)
  or **Game port report** -- and fill its fields from the entry. One issue per finding; if it adds evidence to an existing entry, name
  that entry's ID.
- Never include game files, copyrighted assets, private paths, credentials, or the user's private code or unreleased project details.
  Run any log you attach through `tools/vita-scrub-log.py` (it strips home paths, IDs, addresses and account names and keeps the
  numbers); `--check` confirms a file is clean. If a finding can't be shared without something private, keep it local and say why.
- With the GitHub CLI signed in: `gh issue create --repo <owner>/<repo> --title "[discovery] <title>" --body-file <draft>`. Without it,
  give them the text and the repository's new-issue page so they can post it themselves. If posting fails, the draft stays in their
  notes; say so.
