---
name: shepherd-engine
description: Porting a Unity game to the PS Vita with the Shepherd engine -- the open-source (MIT) stand-in for the Unity runtime that runs a game's own compiled C# on a Mono (.NET 8) fork with vitaGL, Unity-exact 2D physics on Box2D and an FMOD-compatible audio engine. Covers how the engine is put together, the order that worked (Mac engine first, missing icalls as the work list, then the Vita), the hard rules (no game files, decompiled ports stay local, fidelity first) and the known first-game seams to fix. Use when someone wants to port a Unity game to the Vita, works in a Shepherd checkout, or asks how Shepherd works.
---

# Porting a Unity game with Shepherd

Shepherd is released early (v0.4.0, MIT): it runs its first game (Cult of the Lamb) to the Main Menu and into New Game on a PS Vita,
and it expects contributors to fill gaps for their own games. Source: the Shepherd engine repository (README, BUILD.md,
docs/ARCHITECTURE.md, docs/PORTING-ANOTHER-GAME.md, CONTRIBUTING.md). Read those files in the checkout before acting; this skill is the
short version.

## How it works (one paragraph)
The game's own assemblies and Unity's managed assemblies come from the user's install. `tools/Rewriter` turns every Unity
`InternalCall` into a managed call to `Shepherd.Hooks.Icalls.Call(id, args)` and writes `icalls.json`; `engine/Shepherd.Engine`
implements those calls in C# (lifecycle, scenes from the game's serialized files, rendering through GL / vitaGL, physics, audio, input,
video, saves). On the Vita, a .NET 8 Mono fork runs it: engine + BCL AOT-compiled into the eboot (LLVM Thumb-2), game code interpreted,
AOT-compiled locally, or JIT-compiled where allowed. A tiny launcher eboot loads the engine as a module (watch `0x8002D003`: the
`vita-tools` skill's import checker). `vita/vlx` runs the Vita build's own objects on a Mac under QEMU.

## The order that worked
1. **Mac engine first** (`play.sh`): minutes per try instead of a device run. Work through `runtime/logs/missing-icalls.txt` (each
   missing Unity internal call, with its signature) and the engine log.
2. **Fidelity before speed**: compare with the real game; anything that changes play or the picture is an opt-in switch, off by default
   (`SHEPHERD_STRICT_ORIGINAL=1` turns every non-original behaviour off).
3. **Then the Vita**: headless boot -> GL -> input -> menus -> gameplay; vlx before every device run; measure on the device with the
   `vita-measure` habits.
4. **Memory** decides most things: see `vita-hardware` (VH-003, VH-005) and the catalog's MEM / LOAD rows.

## Hard rules (also in CONTRIBUTING.md)
- Never commit or share game files or anything built from them (rewritten DLLs, packs, bakes, keys, saves); the build reads the user's
  own install and writes under the git-ignored `runtime/`.
- Ports of a game's or third party's decompiled code or shaders stay in the git-ignored `engine/**/Derived/`;
  `python3 vita/shepherd/derived_leaks.py --require` must pass before a commit or pull request.
- No private data in commits (absolute paths, user names, LAN addresses, tokens).
- Label every number (MEASURED device / EMULATED / DERIVED / ESTIMATE).

## Known first-game seams (good first fixes)
Product / company name and window title, the boot splash clip rules, physics check scenes, starting time settings, default data paths
(`COTL_DATA` -> `SHEPHERD_GAME_DATA`), first-game TITLE_IDs, test routes and menu labels; `tools/VitaBudget` does not build. The full
table with file names is in `docs/PORTING-ANOTHER-GAME.md`.

## What a new game will likely need
Icalls the first game never used (3D physics simulation, terrain, other render pipelines), GLSL ES 1.00 replacements for its shaders
(kept local when they are ports), and middleware stand-ins (e.g. Wwise) following the FMOD surface's pattern. Record what you learn,
including failures, with the `vita-record-discovery` skill.
