---
name: vita-knowledge
description: The Shepherd PS Vita knowledge base -- numbered entries (VH hardware, GT gotchas, TR tricks, FA failed experiments, EX experimental) with evidence, plus an idea catalog of ~340 labelled techniques by category (runtime / JIT, memory, engine, fidelity, power, loading, GPU, UI, animation, multicore, world streaming, dropped). Each has a status (VERIFIED, OBSERVED, EXPERIMENTAL, FAILED, THEORETICAL) and whether it keeps output exact. Use to look up whether a technique has been tried or planned on the Vita, what it measured, what it conflicts with, or before proposing an optimisation that may already have failed or been dropped.
---

# Shepherd Vita knowledge base (v0.2)

Look up the file for the topic instead of loading everything:

| File | IDs | What's in it |
|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/entries/hardware.md` | VH-### | Measured device facts |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/entries/gotchas.md` | GT-### | Failures that cost device runs, with the fix |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/entries/tricks.md` | TR-### | Optimisations that worked, with numbers |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/entries/failed.md` | FA-### | What did not work, and why -- check before proposing |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/entries/experimental.md` | EX-### | Built and passing off-device, not yet confirmed on a Vita |

### Idea catalog (one table row per idea: ID, idea, status, exact?, source / notes)
Most rows are THEORETICAL -- planned for the Shepherd port, not built. Rows that were built point to their entry above.

| File | IDs | Category |
|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/catalog/runtime.md` | RT-### | Mono runtime, AOT / LLVM, interpreter, JIT tiers, prefetch, code layout |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/catalog/memory.md` | MEM-### | GC, heap layout, arenas, VRAM as storage, pressure ladder |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/catalog/engine.md` | ENG-### | Exact engine shortcuts: lookups, timers, sorting, visibility, object creation |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/catalog/fidelity.md` | FID-### | Keeping results identical: random numbers, float rules, identity and lockstep checks |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/catalog/power.md` | PWR-### | Clocks, modes, suspend, cores, device detection, player-side hardware |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/catalog/loading.md` | LOAD-### | Boot and loading: packs, codecs, caches, preparation, I/O priority |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/catalog/gpu.md` | GPU-### | Rendering on the SGX543MP4+ / GXM / vitaGL: tile rules, caches, shadows |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/catalog/ui.md` | UI-### | Menus, UI meshes, text, settings rows |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/catalog/animation.md` | ANIM-### | Skeletal animation (Spine): spare cores, pose skipping / sharing, LOD |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/catalog/multicore.md` | CORE-### | Native render-prep core, job systems, ordered commit, lockstep rig |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/catalog/world.md` | WORLD-### | Scenes, streaming, prediction without guessing, pathfinding memos |
| `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/catalog/dropped.md` | DROP-### | Ideas dropped and why (mostly tricks that change play or picture) |

Platform-neutral patterns (when a technique helps, when it hurts, how to measure) are in the `optimization-patterns` skill.

## Status labels
- **VERIFIED**: measured on a real Vita, or a reproducible measurement (named).
- **OBSERVED**: seen to work, evidence incomplete.
- **EXPERIMENTAL**: implemented, passes off-device tests (emulator / host), not yet confirmed on a device.
- **FAILED**: tested and rejected (the reason is the valuable part).
- **THEORETICAL**: proposed, not built (most of the catalog). Treat as a lead to measure, never as a result.
- **PARKED**: considered, deferred until something changes (the row says what).

## Rules for using it
- Prefer VERIFIED entries; say when you rely on EXPERIMENTAL or THEORETICAL ones.
- Check `failed.md` and `catalog/dropped.md` before proposing a technique; don't re-propose a FAILED one under the same conditions without a new reason.
- Hardware facts come from one PCH-2000 on fw 3.65 + Enso with plugins (PSVshellPlus, CapUnlocker). Other models and firmwares are not
  verified -- say so.
- A technique proven elsewhere (PC, other consoles) is not proven on the Vita until measured here.
- New findings: record them in the same format and propose them upstream (see CONTRIBUTING in the repository); they enter as EXPERIMENTAL
  or OBSERVED until reviewed.
- "Exact" in the catalog means the output (pixels, game state, sound) is unchanged; "no" rows are opt-in settings under a
  fidelity-first rule. Many rows were written for one Unity game -- check that the game you port does the same thing before relying on it.
