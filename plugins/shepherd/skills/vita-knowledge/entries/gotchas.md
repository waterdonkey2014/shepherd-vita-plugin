# Gotchas (GT)

Each cost at least one device run. Status VERIFIED = the failure was seen on a device and the fix confirmed (or, where noted, confirmed
off-device with the failure reproduced first).

### GT-001 -- A loaded module may import only libraries already loaded
- Status: VERIFIED (failure on device; fix confirmed on device). Category: loading / linking.
- Problem: `sceKernelLoadStartModule` returned `0x8002D003` (MODULEMGR_NO_LIB): the engine module imported SceShaccCg (libshacccg, loaded
  later by the shader-compiler wrapper) and SceNet (libnet, never loaded). Eboots tolerate late libraries; modules don't.
- Fix: define the late functions as signature-agnostic trampolines that resolve with `taiGetModuleExportFunc` on first call; keep a
  loaded-at-module-load allow-list and fail the build on any other import.

### GT-002 -- Hardware AVC decoder output delay
- Status: VERIFIED (failure on device), fix EXPERIMENTAL (EX-003). Category: video.
- Problem: the first access unit returned no picture ("the decoder gave no picture"); the player gave up and showed black.
- Fix: keep feeding while pictures are pending, drain with `sceAvcdecDecodeStop`, time frames by output; encode with no B-frames
  (max_dec_frame_buffering 1).

### GT-003 -- vitaGL takes all CDRAM and PHYCONT at init
- Status: VERIFIED (failure on device), fix EXPERIMENTAL (EX-004). Category: memory / video.
- Problem: `sceVideodecInitLibrary` after `vglInit` failed `0x80024302` (NO_FREE_PHYSICAL_PAGE).
- Fix: initialise the decoder library (~6 MiB PHYCONT) before `vglInit`, free it after the clip; measure what vitaGL loses (~10.7 MiB less
  free VRAM estimated).

### GT-004 -- Process time stops while suspended
- Status: VERIFIED (failure on device), fix EXPERIMENTAL (EX-005). Category: platform.
- Problem: a watchdog looking for gaps in `sceKernelGetProcessTimeWide` never saw PS-button / standby suspensions.
- Fix: compare `sceRtcGetCurrentTick` with process time; re-raise clocks after standby. A game clock on process time resumes without a jump.

### GT-005 -- Shader cache entries must keep their exact size
- Status: VERIFIED. Category: GPU / loading.
- Problem: storing GXP programs padded to 4 bytes made the size check reject every cached program (7-8 s of recompiles per start).
- Fix: store and check the exact size (cache then cut shader setup from 7.4 s to 0.5 s).

### GT-006 -- libshacccg.suprx is never shipped
- Status: VERIFIED. Category: GPU / distribution.
- Fix: users extract it with ShaRKF00D; check for it (ur0:data/ and ur0:data/external/) with a plain message before vitaGL starts.

### GT-007 -- Fragmentation before exhaustion
- Status: VERIFIED. Category: memory.
- Problem: some boots ended out-of-memory with MiB free: no hole for a 4 MiB atlas decode.
- Fix: log the largest free block; collect before big allocations at known points; avoid long-lived small allocations between big ones.

### GT-008 -- SGen size classes
- Status: VERIFIED (measured off-device: +3 MiB on a scene; fixed). Category: memory / runtime.
- Problem: an 8-byte field took an engine object from 200 to 208 bytes = the next size class (256 B).
- Fix: check object sizes after adding fields; reorder / pack.

### GT-009 -- Rooted paths
- Status: VERIFIED (review finding, reproduced with a strict-path harness). Category: IO.
- Problem: sceIo refuses `/ux0:...`. Fix: pass `ux0:...`.

### GT-010 -- The .NET SDK commit stamp
- Status: VERIFIED. Category: build.
- Problem: AssemblyInformationalVersion gets `+<git sha>`, so every commit changes every DLL's MVID (and AOT images bound to it, and any
  shared DLL on the card).
- Fix: build a release from one commit; reproduce with `SourceRevisionId=<sha>`.

### GT-011 -- Clock reporting with plugins
- Status: VERIFIED. Category: CPU.
- Problem: the app forced 444 at launch over a plugin's higher clock; `scePower` reported 444 while the CPU ran ~497.
- Fix: keep a higher launch clock; measure and show the measured clock.

### GT-012 -- Copying files to the card by hand
- Status: VERIFIED. Category: workflow.
- Problem: Finder "Replace" on a folder wipes the card folder; macOS leaves `._` AppleDouble files on exFAT.
- Fix: copy files, not folders; skip `._` files in scans.

### GT-013 -- A "green" end that needs a menu response
- Status: VERIFIED. Category: testing.
- Problem: test starts whose only press was the title screen counted 0 menu responses and ended red although nothing failed.
- Fix: count the title press, or put one menu move in every scripted step.
