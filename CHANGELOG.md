# Changelog

## 0.4.0 -- the engine, released early
- The Shepherd engine's first public release (separate source tree, MIT): Mono (.NET 8) fork for the Vita, Unity internal calls in C#,
  vitaGL renderer, Unity-exact 2D physics on Box2D, FMOD-compatible audio, Vita host + launcher, Mac-side tools, vlx off-device harness.
  Exported from the private port with gates: no private paths, binaries or game file types, no derived (decompiled) content, no FMOD
  bank key; 24 of 25 C# projects build from the clean export.
- New skill `shepherd-engine`: how the engine works, the order that worked, the hard rules, the first-game seams.

## 0.3.0 -- portable tools
- `tools/vita-imports.py`: imports by library from the linker's ELF (pure Python); `--module-load-libs` (0x8002D003, GT-001),
  `--allow-libs`, `--forbid network|kernel|jit|hooks`, `--allow-func`, `--allow-newlib-net`; `module-load-libs.example.txt`.
- `tools/vita-vpk-check.py`: param.sfo fields and file list; required files, TITLE_ID, ATTRIBUTE2, forbidden types, size, macOS leftovers.
- `tools/vita-runlog.py`: `stats` / `add` / `show` / `compare` over `SM` log lines (or any format via `--spec`); measured clock wins, no
  percentages across clocks, STALE and no-END warnings, no duplicate runs.
- `tools/vita-pull-logs.sh`: read-only log + crash-dump copy from a VitaShell-mounted memory card, with a manifest.
- `tools/c/shepherd_measure.h` + `measure_example.c`: C instrumentation writing the `SM` lines (EXPERIMENTAL until a device run).
- New skill `vita-tools`; the `SM` format in `vita-measure`; "break the checker on purpose" in `vita-check-the-checker`.
- New gotcha GT-014: vitasdk's newlib imports SceNet in every program (found by the import checker on its own example).
- Fixed: the `vita-gotchas` skill's item 13 named the wrong entry.
- `tests/test_tools.py`: 19 tests with negative controls, synthetic fixtures (no binaries in the repo), optional host-C and vitasdk runs;
  12 planted bugs all caught.

## 0.2.0 -- the idea catalog
- `vita-knowledge/catalog/`: 343 labelled ideas in 12 categories -- runtime / JIT (RT), memory (MEM), engine (ENG), fidelity (FID),
  power and clocks (PWR), loading (LOAD), GPU (GPU), UI (UI), animation (ANIM), multicore (CORE), world streaming (WORLD) and dropped
  ideas with reasons (DROP). Each row: status, whether output stays exact, source or prior art.
- New skill `optimization-patterns`: 28 platform-neutral patterns with when-useful / when-harmful / how-to-measure, linked to the Vita
  catalog where applied.
- `vita-knowledge` index covers the catalog; PARKED status added.

## 0.1.0 -- first release (knowledge only)
- Skills: vita-hardware, vita-gotchas, vita-measure, vita-check-the-checker, vita-port-process, vita-knowledge, vita-record-discovery.
- Knowledge base: 12 hardware facts (VH), 13 gotchas (GT), 12 tricks (TR), 8 failed experiments (FA), 6 experimental items (EX).
- Contribution template and review rules. MIT licence.
