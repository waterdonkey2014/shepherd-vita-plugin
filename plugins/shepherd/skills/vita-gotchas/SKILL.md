---
name: vita-gotchas
description: Checklist of PS Vita porting gotchas that each cost a real device run -- module loads refusing late libraries (0x8002D003), the hardware video decoder's output delay, vitaGL taking all CDRAM/PHYCONT (0x80024302), process time stopping during suspend, shader cache size, fragmentation, SGen size classes, rooted paths, the .NET SDK commit stamp, clock reporting, card copying, newlib's hidden SceNet imports. Use before a first device run, when a device run fails with an error code, or when designing loaders, video, suspend handling or memory layouts.
---

# Vita gotchas -- read before your first device run

Each item below cost at least one device run. IDs refer to `${CLAUDE_PLUGIN_ROOT}/skills/vita-knowledge/entries/gotchas.md`.
**First rule: decode the error code.** Most failures name their class in the code (`psp2/kernel/error.h`, the library headers).

1. **GT-001 Module loads may import only libraries already loaded.** An eboot may import a library that is loaded later (its stubs are
   bound when it arrives); a module loaded with `sceKernelLoadStartModule` is refused with `0x8002D003` (MODULEMGR_NO_LIB). Libraries
   that arrive late (e.g. SceShaccCg = libshacccg, SceNet = libnet) need first-use trampolines (`taiGetModuleExportFunc`). Keep an
   allow-list of libraries loaded at module-load time and fail the build on anything else.
2. **GT-002 The hardware AVC decoder has output delay.** The first access unit(s) return NO picture. Keep feeding while pictures are
   pending, drain at the end (`sceAvcdecDecodeStop`), time frames by output. Encode clips with no B-frames / a small reorder buffer.
3. **GT-003 vitaGL takes every free CDRAM and PHYCONT page at init.** Anything else that needs physical memory (the video decoder library
   needs ~6 MiB PHYCONT) must reserve it BEFORE `vglInit`, or it fails with `0x80024302` (NO_FREE_PHYSICAL_PAGE).
4. **GT-004 Process time stops while the app is suspended** (PS button, standby). A watchdog that looks for gaps in
   `sceKernelGetProcessTimeWide` never sees a suspension -- compare the RTC with process time. Bonus: a game clock on process time
   already resumes without a jump.
5. **GT-005 Stored GXP shaders must keep their exact size.** Padding a cached program changed its size and the cache refused every program
   (7-8 s of recompiles per start).
6. **GT-006 libshacccg.suprx is never shipped.** Users extract it with ShaRKF00D. Check for it with a plain message before touching vitaGL.
7. **GT-007 Fragmentation fails before total memory does.** An allocation can fail with MiB free overall because no single hole fits (a
   4 MiB atlas decode). Log the largest free block, not just free bytes.
8. **GT-008 SGen size classes.** An object 8 bytes past a size class takes the next class (200 -> 208 bytes = a 256-byte slot; +3 MiB
   over a scene's transforms). Check object sizes after adding fields.
9. **GT-009 sceIo refuses rooted paths** like `/ux0:data/...` (common when a managed runtime adds a leading slash). Pass `ux0:...`.
10. **GT-010 The .NET SDK stamps the git commit into every DLL** (AssemblyInformationalVersion), so every commit changes every MVID and any
    AOT image bound to it. Build a whole release from one commit, or pass `SourceRevisionId=<sha>` to reproduce one.
11. **GT-011 Apps start at 333 MHz** and a plugin-set clock is not reported by `scePower`. Don't force 444 at launch over a higher plugin
    clock; measure the clock yourself.
12. **GT-012 Copying to the card by hand:** Finder's "Replace" on a folder deletes the card folder's contents -- copy files, not folders.
    macOS also leaves `._` AppleDouble files on exFAT cards: harmless, skip them in scans.
13. **GT-013 A "green" end can need a menu response.** Scripted test starts whose only press was the title screen counted 0 menu
    responses and ended red with nothing wrong: count the title press, or make every scripted step move the menu once.
14. **GT-014 vitasdk's newlib imports SceNet in every program** (`sceNetRecv` / `sceNetSend` / `sceNetSocketClose`, for socket-aware
    read / write / close). Fine in an eboot; a module carrying them is refused with `0x8002D003` (GT-001). Check with
    `python3 ${CLAUDE_PLUGIN_ROOT}/tools/vita-imports.py build/app.elf --module-load-libs <list>` before a device run.

Also: test harnesses lie by omission -- an emulator / host harness that doesn't model import binding, decoder delay or suspend clocks
passes builds the device refuses (FA-007; see `vita-check-the-checker`).
