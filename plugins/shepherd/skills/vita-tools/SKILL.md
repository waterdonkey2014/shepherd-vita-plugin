---
name: vita-tools
description: Runs the Shepherd plugin's PS Vita tools -- an import checker that catches 0x8002D003 module-load failures and stray network / kernel / JIT imports from the linker's ELF, a VPK / param.sfo checker, a run-history tool that turns device logs into honest numbers and comparisons, a read-only log puller for a VitaShell-mounted memory card, and a one-header C measurement library. Use after a Vita build (before copying it to the card), when pulling or reading device logs, when comparing runs, or when adding measurement to a Vita app.
---

# Shepherd tools

All tools live in `${CLAUDE_PLUGIN_ROOT}/tools/` (full usage in its README.md). Python 3 standard library and POSIX sh; nothing to
install. Run them with `python3` / `sh` so the executable bit doesn't matter.

## After every build, before the card
1. **Imports** -- on the linker's ELF (the input of `vita-elf-create`, not eboot.bin):
   `python3 ${CLAUDE_PLUGIN_ROOT}/tools/vita-imports.py build/app.elf`
   - A module loaded by a launcher with `sceKernelLoadStartModule`: add `--module-load-libs <list>` (start from
     `${CLAUDE_PLUGIN_ROOT}/tools/module-load-libs.example.txt`). Any FAIL = the device would refuse it with 0x8002D003 (GT-001).
   - An app meant to be offline: `--forbid network --allow-newlib-net` (newlib's three SceNet imports are in every program: GT-014).
   - Also useful: `--forbid kernel`, `--forbid jit` (only a JIT should import ForVM), `--forbid hooks`.
2. **Package** -- `python3 ${CLAUDE_PLUGIN_ROOT}/tools/vita-vpk-check.py out/app.vpk --expect-title-id <ID> --expect-attribute2 12`
   plus `--forbid-ext` for any file type that must never ship (game data).
Suggest wiring both into the project's build script so a failure stops the build.

## After a device run
1. Pull the logs (read-only): `sh ${CLAUDE_PLUGIN_ROOT}/tools/vita-pull-logs.sh --data-dir data/<app> --stats`
   (the user puts the Vita in VitaShell's USB mode first; the tool never writes to or ejects the card).
2. Numbers: `python3 ${CLAUDE_PLUGIN_ROOT}/tools/vita-runlog.py stats <log> --built <vpk>` -- read its WARN lines first (no measured
   clock, STALE log, no END line = crash: look in coredumps/).
3. History: `vita-runlog.py add <logs> --history perf-history.tsv --label <version>`, then `compare --history ... --app <app>`.
   Report numbers with their label (MEASURED device / EMULATED / ESTIMATE) and never quote a percentage the tool refused.

## Adding measurement to an app
Use `${CLAUDE_PLUGIN_ROOT}/tools/c/shepherd_measure.h` (C, one header) or write the same `SM` lines from any language -- the format is
in the `vita-measure` skill. Log at least: the clock measured at start and end, free memory at checkpoints, boot milestones, a FRAMES
summary per test window, and an END line.

## Rules
- Never write to the user's memory card or copy builds onto it yourself unless asked; installing a VPK is the user's step.
- A tool that has never failed proves nothing: when you change a tool, run `python3 tests/test_tools.py` in the plugin repository.
- Results from these tools are off-device checks. A clean import check means the module will load as far as imports go -- it doesn't
  prove the app works on the device.
