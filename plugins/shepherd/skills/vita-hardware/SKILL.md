---
name: vita-hardware
description: Measured PS Vita hardware facts for porting work -- CPU clocks and the 500 MHz reality, the 4th core, memory budgets (user RAM, CDRAM, PHYCONT), RAM latency, memory-card speed, JIT/ForVM rules, the GPU transfer unit, NGS audio, and how to read the real model and firmware. Use when planning memory or performance budgets, choosing where work runs, or interpreting device numbers.
---

# PS Vita hardware, measured

Measured on a PCH-2000 (fw 3.65 + Enso, PSVshellPlus, CapUnlocker) while porting a modern Unity game. Each fact carries an ID from
the knowledge base (`vita-knowledge` skill); status VERIFIED means measured on the device. Other models (PCH-1000, PS TV) and other
firmwares are not verified yet -- say so when it matters.

## CPU
- **Clocks (VH-001)**: apps start at 333 MHz until they raise it; 444 MHz is the standard app maximum. `scePowerSetArmClockFrequency(500)`
  is refused to apps (`0x802b0000`). A PSVshellPlus per-title profile gives a real ~497 MHz while `scePower` still REPORTS 444 -- so
  always measure the clock yourself (time a loop of dependent adds) and log the measured value. ~8 % faster boot measured at 500.
- **4th core (VH-002)**: usable when CapUnlocker is installed; detect it and put background work there; fall back to three cores.
- Cortex-A9: in-order-ish, no effective hardware prefetch -- see memory latency below.

## Memory
- **Budget (VH-003)**: with `ATTRIBUTE2=12` in param.sfo (the extended homebrew budget) an app had ~200 MiB of free user memory after a
  40-60 MiB eboot, plus the newlib heap you size yourself (~316 MiB of main RAM in all in our configuration). The eboot's size comes
  straight out of free memory -- smaller code = more heap.
- **CDRAM / PHYCONT (VH-004)**: ~110 MiB CDRAM and ~26 MiB physically contiguous memory free at start. vitaGL takes ALL of both at init
  (see `vita-gotchas` GT-003).
- **Latency (VH-005)**: a dependent random read costs ~252 ns per 32-byte line (CDRAM ~333 ns). With no hardware prefetch, waiting on RAM
  dominates many frames: data layout and fewer pointer chases beat micro-optimising instructions.
- **Free VRAM (VH-007)**: 31-55 MiB of CDRAM was still free on menus / a first scene -- usable for cold data.

## Storage
- **Memory card (VH-006)**: ~11.6 MiB/s sequential, ~3.1 ms per random 4 KiB read. Read big blocks in a recorded order; avoid many small
  files and seeks.

## JIT / executable memory (VH-008)
- `sceKernelAllocMemBlockForVM` + VM-domain Open / write / Sync / Close works at native speed.
- The thread that Opens the domain must do the writes; Open is not nestable.
- Write + Sync ~5.7 us; Open / Close ~11 us -- batch publishing.
- One 2-4 MiB block plus at least 14 MiB more were granted (>= 16 MiB in all); a second large block can be refused -- probe the largest
  first.
- Direct `BL` from the block to runtime helpers is out of range: use MOVW/MOVT + BLX register calls or veneers.

## Other units
- **GPU transfer unit (VH-009)**: `sceGxmTransfer` swizzles textures ~100x faster than the CPU, byte-identical. GPU-generated mips are NOT
  exact (FA-003).
- **NGS (VH-010)**: the audio engine can take ~60 % of mixing off the CPU; a lean software mixer can still be cheaper in quiet scenes.
  Use hybrids and check bit-exactness.
- **Model / firmware (VH-011)**: `sceKernelGetModelForCDialog` + "imc0 not mounted" misreads a PCH-2000 with a memory card as a PCH-1000,
  and HENkaku spoofs the reported firmware (3.65 shown as 3.73). Read the real values through SceVshBridge
  (`vshSysconIsMCEmuCapable`, `_vshSblGetSystemSwVersion`).

Full entries with evidence: `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/entries/hardware.md`.
