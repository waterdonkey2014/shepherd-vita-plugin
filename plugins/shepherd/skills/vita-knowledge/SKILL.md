---
name: vita-knowledge
description: The Shepherd PS Vita knowledge base -- numbered entries (VH hardware, GT gotchas, TR tricks, FA failed experiments, EX experimental) each with a status (VERIFIED, OBSERVED, EXPERIMENTAL, FAILED, THEORETICAL), evidence and limits. Use to look up whether a technique has been tried on the Vita, what it measured, what it conflicts with, or before proposing an optimisation that may already have failed.
---

# Shepherd Vita knowledge base (v0.1)

Look up the file for the topic instead of loading everything:

| File | IDs | What's in it |
|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/entries/hardware.md` | VH-### | Measured device facts |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/entries/gotchas.md` | GT-### | Failures that cost device runs, with the fix |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/entries/tricks.md` | TR-### | Optimisations that worked, with numbers |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/entries/failed.md` | FA-### | What did not work, and why -- check before proposing |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/entries/experimental.md` | EX-### | Built and passing off-device, not yet confirmed on a Vita |

## Status labels
- **VERIFIED**: measured on a real Vita, or a reproducible measurement (named).
- **OBSERVED**: seen to work, evidence incomplete.
- **EXPERIMENTAL**: implemented, passes off-device tests (emulator / host), not yet confirmed on a device.
- **FAILED**: tested and rejected (the reason is the valuable part).
- **THEORETICAL**: proposed, not built (the large idea catalog arrives in v0.2).

## Rules for using it
- Prefer VERIFIED entries; say when you rely on EXPERIMENTAL or THEORETICAL ones.
- Check `failed.md` before proposing a technique; don't re-propose a FAILED one under the same conditions without a new reason.
- Hardware facts come from one PCH-2000 on fw 3.65 + Enso with plugins (PSVshellPlus, CapUnlocker). Other models and firmwares are not
  verified -- say so.
- A technique proven elsewhere (PC, other consoles) is not proven on the Vita until measured here.
- New findings: record them in the same format and propose them upstream (see CONTRIBUTING in the repository); they enter as EXPERIMENTAL
  or OBSERVED until reviewed.
