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

### GT-014 -- vitasdk's newlib imports SceNet in every program
- Status: VERIFIED (reproducible: the link map of any vitasdk newlib program; on device, eboots carrying these imports ran and a module
  carrying them was refused). Category: loading / linking.
- Problem: newlib's `libc.a` makes read / write / close work on sockets -- `syscalls.o` imports `sceNetRecv` / `sceNetSend`, `io.o`
  imports `sceNetSocketClose` -- so a program with no networking at all still imports SceNet. An eboot runs fine with it. A module loaded
  with `sceKernelLoadStartModule` is refused with `0x8002D003` unless libnet is already loaded (GT-001), and a "no network imports"
  policy flags it.
- Fix: in a module, bind those three at first use (trampolines, as in GT-001) or supply replacements; for a network-free eboot policy,
  exempt exactly those three (`vita-imports.py --allow-newlib-net`).
- Found: running the plugin's import check on its own example program (v0.3), traced with `-Wl,-Map,--cref`.

### GT-015 -- Fast local loads expose races that slow internet hid
- Status: VERIFIED (the failure reproduced on a host in Ruffle with timestamped beacons; the fix confirmed on a device: the game loads and
  plays). Category: loading / timing. Runtime: Flash.
- Source: maintainers (Flash side project, 2026-11); reproduced by maintainers: yes.
- Problem: a 2008 preloader's frame script dispatches "intro reached" and then calls `stop()`; when loading has already finished, the
  listener answers with `gotoAndPlay("out")` inside the dispatch. Flash Player queues that goto together with its play, so "out" plays.
  Ruffle before ruffle-rs/ruffle#24684 applied the play at once and the trailing `stop()` cancelled it: the loading bar froze. Over 2008
  internet the loads always finished after that frame; from a memory card they finish in under a second, before it.
- Fix / use: swap the two calls (`stop(); dispatchEvent(...)`: same bytes, same length), or use a Ruffle that has #24684 (Sept 2026).
- Evidence: Flash Player 32 and Ruffle on the same files, with HTTP pings injected into the preloader's methods: both loads done at
  0.91 s, the frame script at 1.88 s; Ruffle stopped after it, Flash Player went on.
- Limits: suspect any loader or intro that assumes the network is slower than its own animation.

### GT-016 -- AOT covers only what ran while it was emitting
- Status: OBSERVED (host). Category: runtime / AOT. Runtime: Flash on RuffleVita (applies to any record-then-compile AOT).
- Source: maintainers; reproduced by maintainers: yes (host).
- Problem: RuffleVita's AOT translator compiles a method when it first runs during the emit session, and the device uses it only if the
  shipped bytes fingerprint the same. An emit over one level left the other levels' own code interpreted -- those levels were locked,
  because unlocks came from a web service that no longer exists -- and an emit from a traced or patched test build left the changed
  methods interpreted in the build that shipped.
- Fix / use: emit from the exact files you ship, and play every level and mode during the emit (a test-only unlock patch is fine: the
  methods it changes simply stay out of the shipped table). Then count the fingerprints in the eboot (GT-017).
- Evidence: one level 667 game methods compiled; all four levels 863; screenshots identical compiled vs interpreted on all four.

### GT-017 -- An eboot's strings and constants are hidden until inflated
- Status: VERIFIED (reproducible: the check below on three builds). Category: tooling.
- Source: maintainers; reproduced by maintainers: yes.
- Problem: searching a VPK's `eboot.bin` for compiled-method fingerprints, version strings or settings labels finds nothing, because the
  SELF's segments are zlib-compressed.
- Fix / use: find each zlib stream (`78` followed by `01` / `5E` / `9C` / `DA`, keeping only streams that inflate to something
  sizeable), inflate, then search. A build check that counts every fingerprint of the compiled table (1411 of 1411 here) catches a
  stale or partial build before it reaches a Vita.
- Limits: a check that finds no streams must fail loudly, or "0 found" looks like a result. `vita-vpk-check.py` doesn't do this yet.

### GT-018 -- The Mac's Finder replaces a same-name folder; VitaShell's paste merges
- Status: CONFIRMED (VitaShell source, a libarchive unpack on a host, and a device paste: a 333 MiB, 162-file build pasted over a
  card folder of the same name; the card's saves and staged files stayed, and every run afterwards passed). Category: delivery / tooling.
  Runtime: any.
- Source: maintainers (2026-11); reproduced by maintainers: yes (host).
- Problem: with the card mounted over USB, dragging a folder onto the card's folder of the same name makes the Finder offer
  **Replace**. That deletes everything in the card's folder that the new one lacks: saves, game files staged once, caches. Copying the
  files one by one is safe but slow, and it is easy to get wrong on a phone.
- Fix / use: ship each test build as ONE zip whose top folder mirrors the card's (`<app>/...`). Copy that one file to the card, open it
  in VitaShell (X: it browses like a folder), TRIANGLE -> Copy on the top folder, go to the parent folder (e.g. `ux0:data/`), TRIANGLE ->
  Paste. VitaShell reads archives with libarchive. Pasting from one creates folders that are missing and tolerates ones that exist
  (`sceIoMkdir`, EEXIST ignored), and opens each file with `SCE_O_WRONLY | SCE_O_CREAT | SCE_O_TRUNC`: same-name files are replaced,
  everything else stays, there is no prompt, and a file that fails is removed.
- Pack it carefully:
  - Store the members uncompressed, so the Vita unpacks at copy speed.
  - Keep each file's own modification time, never a fixed date: apps that cache "already verified" by size + mtime would otherwise skip
    a check.
  - Refuse any file that would land where an app reads it as a live switch (an env or args file at the top of the app's folder).
  - Unpack the finished zip on the Mac with `bsdtar` (also libarchive) and compare every file.
- Limits:
  - A merge never deletes. A build that must remove a stale file has to say so in its steps.
  - The card needs room for the zip plus the new files until the zip is deleted.
  - Read from VitaShell's current source; an old VitaShell may differ.

### GT-019 -- The Vita refuses to install a VPK whose sce_sys PNGs are not 8-bit palette images
- Status: OBSERVED (device: the two VPKs with such images failed to install, the three with 8-bit palette icons installed; the same two
  VPKs with only their images re-encoded are not installed yet, so the fix is not yet confirmed). Category: packaging / tooling.
  Runtime: any.
- Source: maintainers (2026-11); reproduced by maintainers: yes (device).
- Problem: VitaShell's install of a VPK fails when `sce_sys/icon0.png` or a LiveArea image (`sce_sys/livearea/contents/bg.png`,
  `startup.png`) is not an 8-bit palette PNG. Two ways to get there without noticing:
  - Pillow's `convert("P", colors=16).save(..., optimize=True)` writes 1-, 2- or 4-bit indices when the palette is short. The file is a
    palette PNG, and the tool's comment says "8-bit palette", but the installer refuses it.
  - An icon saved as RGB or RGBA, which is what most image editors do by default.
  Three icons in the same build that were 8-bit palette installed fine; a VPK with no icon at all also installs (default bubble).
- Fix / use: write sce_sys images as 8-bit palette PNGs. With Pillow, pad the palette to 256 entries before saving
  (`p.putpalette(pal + [0] * (768 - len(pal)))`), which makes it write 8-bit indices. Check the result in the build: read the IHDR
  (bytes 16-25) and require bit depth 8 and colour type 3, both in the source tree and in the finished VPK.
- Limits: the images must also keep their expected sizes (icon0 128x128, bg 840x500, startup 280x158). Not tested here: whether the
  installer also limits the palette size or rejects other PNG chunks.
