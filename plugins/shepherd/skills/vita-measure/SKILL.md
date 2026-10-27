---
name: vita-measure
description: How to measure a PS Vita port honestly -- what to log in every device run (measured clock, free memory checkpoints, largest free block, boot timeline, per-frame times split into render and logic, GC pauses), how to compare runs kit to kit, and how to avoid misleading numbers (wrong clock, stale logs, wrong window, interpreter vs AOT). Use when adding instrumentation, reading device logs, or reporting fps / boot / memory numbers.
---

# Measuring a Vita port

Numbers decide what goes in. These habits came from runs where the numbers were wrong or missing.

## Log in every run (one line each, greppable prefixes)
- **The clock you actually ran at** -- time a loop of dependent adds at start and end and print it next to what `scePower` reports
  (they differ when a plugin sets the clock: VH-001 / GT-011). Keep one test app at a fixed clock so history stays comparable.
- **Free memory checkpoints** -- `sceKernelGetFreeMemorySize` (user, CDRAM, PHYCONT) at start, after the heap / arena setup, before and
  after graphics init, and at the end; plus the allocator's peak and the **largest free block** (GT-007). For VRAM, read the graphics
  library's own pool counters (GXM doesn't track allocations for you).
- **A boot timeline** -- time to the first picture (e.g. the logo), total time to the first usable menu, and the work left after the logo.
- **Per-frame times** in a table (frame, total ms, render ms, GC pause ms), and an idle window you always measure the same way (same screen,
  same frame range). Report mean AND median; one long hitch can wreck a mean.
- **GC**: worst pause, total pause time, heap at each collection.
- **The device profile**: real model and firmware (VH-011), plugins seen, cores available.
- **A black box**: the last N log lines kept in RAM and written on a fail / stall; every log line flushed as written (a crash must not
  eat the lines before it).

## The SM line format (what the plugin's tools read)
One line per measurement, greppable, `key=value` with no spaces in values (a prefix such as a timestamp is fine):
```
SM BEGIN app=<name> build=<text>
SM CLK when=<start|end|...> reported=<MHz> measured=<MHz> step=<MHz, 0 = not a clock step>
SM MEM tag=<checkpoint> user_kib=<n> cdram_kib=<n> phycont_kib=<n> [largest_kib=<n>]
SM BOOT tag=<milestone> ms=<ms since process start>
SM FRAME n=<frame> ms=<ms> [render_ms=<ms>] [gc_ms=<ms>]          (optional; a card write each)
SM FRAMES window=<label> n=.. mean_ms=.. p50_ms=.. p95_ms=.. p99_ms=.. max_ms=.. fps=..
SM GC pause_ms=<ms>
SM SUSP lost_ms=<ms>
SM END result=<PASS|FAIL> reason="<text>"
```
`${CLAUDE_PLUGIN_ROOT}/tools/c/shepherd_measure.h` writes these from C; `tools/vita-runlog.py` turns them into stats and a history
(`stats`, `add`, `show`, `compare`), and maps other formats with a `--spec` file. See the `vita-tools` skill.

## Comparing runs
- Compare the same app, the same screen, the same window, the same clock. Label every number: MEASURED (device), VLX / EMULATED, DERIVED,
  ESTIMATE.
- Keep a version-by-version history (one row per run) generated from the logs by a script (`vita-runlog.py add`) -- never by hand -- and make the script record
  the measured clock and include every log pull (main and extra runs). A history tool that silently picks the wrong runs is worse than none
  (see `vita-check-the-checker`).
- An idle menu is a poor test for game-logic changes (a JIT moved render time, not logic time, at idle): measure the work you changed.
- When copying logs off the card, copy the per-app log folders, not just loose files at the top level -- the next start of the same app
  overwrites its engine logs.

## Reading a failure
1. Decode the error code first (headers in vitasdk).
2. Find the last lines before the end (black box), and whether the app ended itself (a clean red end) or crashed (a dump).
3. Reproduce it off-device before fixing (`vita-check-the-checker`).
