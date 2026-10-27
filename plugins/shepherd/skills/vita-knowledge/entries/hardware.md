# Hardware facts (VH)

Device for every VERIFIED entry: PCH-2000, fw 3.65 + Enso, PSVshellPlus, NoPowerLimits, CapUnlocker, YAMT. Discovered October 2026.

### VH-001 -- CPU clocks: 333 at start, 444 for apps, 500 only through a plugin profile
- Status: VERIFIED. Category: CPU.
- Fact: apps start at 333 MHz until they raise the clock; 444 MHz is the app maximum. `scePowerSetArmClockFrequency(500)` returns
  `0x802b0000`. A PSVshellPlus per-title profile gives ~497 MHz (timed) while `scePower` keeps reporting 444.
- Evidence: per-run clock lines (timed loop of 64 dependent adds per pass) across five device sessions; ~8 % faster boot at ~497 MHz in the
  same app (169.9 s -> 156.4 s).
- Use: measure and log the clock yourself; don't force 444 over a higher plugin clock.

### VH-002 -- The 4th core
- Status: VERIFIED. Category: CPU.
- Fact: with CapUnlocker the app can create threads on the 4th core; without it, plan for three.
- Use: background work (GC, compiler, loading) on the 4th core, detected at start.

### VH-003 -- Main-memory budget
- Status: VERIFIED. Category: memory.
- Fact: with `ATTRIBUTE2=12` in param.sfo, ~200 MiB of user memory was free after a 40-60 MiB eboot, besides a newlib heap the app sizes
  itself (~316 MiB of main RAM in that configuration). The eboot's mapped size comes out of free memory 1:1.
- Use: shrink code (trimming, LLVM, dedup) to gain heap; log free memory at checkpoints.

### VH-004 -- CDRAM and PHYCONT at start
- Status: VERIFIED. Category: memory / GPU.
- Fact: ~110 MiB CDRAM and ~26 MiB PHYCONT free at start; vitaGL takes all of both at init (GT-003).

### VH-005 -- RAM latency and no hardware prefetch
- Status: VERIFIED. Category: memory / CPU.
- Fact: a dependent random read costs ~252 ns per 32-byte line (CDRAM ~333 ns); misses don't overlap and there is effectively no hardware
  prefetch.
- Use: contiguous hot data, fewer pointer chases; software prefetch where the next record is known.

### VH-006 -- Memory-card speed
- Status: VERIFIED. Category: storage.
- Fact: ~11.6 MiB/s sequential; ~3.1 ms per random 4 KiB read (128 KiB random ~11.5 ms).
- Use: big blocks in a recorded order; packs instead of many small files.

### VH-007 -- Free VRAM in practice
- Status: VERIFIED. Category: GPU / memory.
- Fact: 31-55 MiB of CDRAM free on menus / a first scene (vitaGL pool counters).
- Use: a place for cold data, shared with any texture-placement plan.

### VH-008 -- Executable memory for a JIT
- Status: VERIFIED. Category: runtime.
- Fact: ForVM blocks + VM domain work at native speed; the opening thread must do the writes; Open isn't nestable; write + Sync ~5.7 us,
  Open / Close ~11 us; 2 MiB + 14 MiB granted (>= 16 MiB), a second large block can be refused; direct BL to helpers out of range.
- Use: one publisher thread, batched windows, register calls / veneers, probe the largest block first.

### VH-009 -- GPU transfer unit
- Status: VERIFIED. Category: GPU / loading.
- Fact: texture swizzle through `sceGxmTransfer` ~100x the CPU, byte-identical.

### VH-010 -- NGS audio engine
- Status: VERIFIED (offload share), OBSERVED (menu cost). Category: audio.
- Fact: NGS takes ~60 % of mixing off the CPU (CPU at 36-40 % of wall time with it); a lean software mixer can be cheaper in quiet menus.
- Use: hybrid, switched at quiet moments, bit-exactness checked.

### VH-011 -- Reading the real model and firmware
- Status: VERIFIED. Category: platform.
- Fact: CDialog model + "imc0 not mounted" misreads a PCH-2000 with a card as PCH-1000; HENkaku spoofs the reported firmware. SceVshBridge
  (`vshSysconIsMCEmuCapable`, `_vshSblGetSystemSwVersion`) gives the real model and firmware.

### VH-012 -- Big memory pages
- Status: FAILED -> see FA-002.
