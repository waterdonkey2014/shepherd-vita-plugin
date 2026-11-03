# Idea catalog: boot and loading (LOAD)

The memory card reads ~10-12 MiB/s (VH-006) while spare cores decode far faster -- so the right compression makes loading FASTER, and
anything stored must be faster to read than to rebuild. Exact = identical bytes / objects; only where and when work happens changes.

| ID | Idea | Status | Exact | Source / notes |
|---|---|---|---|---|
| LOAD-001 | Field programs for Instantiate and scene loads (no generic deserializer on the hot path) | THEORETICAL | yes | the biggest boot / load item |
| LOAD-002 | Asset object snapshots: big immutable data assets stored ready-to-fill | THEORETICAL | yes | localisation and data tables |
| LOAD-003 | Pre-compiled animator controllers (state machines in runtime form) | THEORETICAL | yes | |
| LOAD-004 | Asset diet: drop vertex attributes a 2D game never reads; 16-bit indices; per-clip audio review | THEORETICAL | yes | |
| LOAD-005 | Per-asset codec choice: a stronger lossless codec where spare cores out-decode the card, LZ4 elsewhere | THEORETICAL | yes | decode rate > card rate x ratio |
| LOAD-006 | Decode-ahead worker + LZ4 records | EXPERIMENTAL (partial) | yes | |
| LOAD-007 | Dependency-parallel bundle loads | THEORETICAL | yes | |
| LOAD-008 | DMA bulk copies (`sceDmac`) for loads and uploads | THEORETICAL (device-measured ~2x memcpy) | yes | |
| LOAD-009 | Pack layout in recorded visit order; block-aligned chunks; unbroken (unfragmented) files | THEORETICAL | yes | |
| LOAD-010 | Pre-swizzled textures (or swizzled at load by the GPU transfer unit) | EXPERIMENTAL | yes | VH-009 |
| LOAD-011 | Learning caches on the card: hashed, verified on first reuse, size-capped, user-clearable; results only, never game state | EXPERIMENTAL (shader + JIT caches) | yes | the cap is a user setting |
| LOAD-012 | Per-scene hot lists / read-order maps / memory high-water marks learned from the last visit | EXPERIMENTAL (read maps) | yes | |
| LOAD-013 | Pack-time preload manifests: each predicted moment's chunks laid out contiguously -> one straight read | THEORETICAL | yes | |
| LOAD-014 | Idle-window scheduler: videos, quotes, loading and fade windows filled with engine-side prep | THEORETICAL | yes | data only, never game code early |
| LOAD-015 | Warm-return cache (compressed records of the room just left) | THEORETICAL | yes | |
| LOAD-016 | Audio opened ahead at known transitions | THEORETICAL | yes | |
| LOAD-017 | Loading priority: give load work up to ~50 ms per frame while a loading screen shows | THEORETICAL | yes | what Unity's High background-loading priority does |
| LOAD-018 | Make the engine's "unload unused assets" scan cheap with the exact same result | THEORETICAL | yes | |
| LOAD-019 | Verify-files option (pack integrity hashes) | THEORETICAL | -- | a failing card shows a message, not a crash |
| LOAD-020 | Pack-time deduplication of byte-identical assets | THEORETICAL | yes | |
| LOAD-021 | Generate instead of read where exact and cheaper (sprite quads from rect + pivot; uncompressed mips only if bit-identical) | THEORETICAL | yes | the .kkrieger lesson, reversed for a RAM-poor device |
| LOAD-022 | AOT that learns from play: record generic instantiations that fell back to the interpreter; compile them next build | THEORETICAL | yes | also the safety net without a JIT |
| LOAD-023 | A boot that always shows something: early logo -> the game's own loading screen -> a recorded title until the live one is ready | EXPERIMENTAL (launcher) | yes | the swap must be invisible; one press remembered, not a queue |
| LOAD-024 | Game code in one bundle in boot order (one open, one read) | THEORETICAL | yes | ~109 assemblies / ~43 MB read at boot in the measured game |
| LOAD-025 | IL bodies on demand: read metadata + only the IL the interpreter needs | THEORETICAL | yes | |
| LOAD-026 | Load-in-place index and catalog (offsets, no table building at boot) | THEORETICAL | yes | classic console trick; ~2 s of boot work in the measured game |
| LOAD-027 | Sony's FIOS2 RAM-cache filter under the pack reader (A/B) | THEORETICAL | yes | TheFloW's GTA: San Andreas Vita port |
| LOAD-028 | Fixed page pool for streaming (equal-size pages, no heap fragmentation) | THEORETICAL | yes | Crash Bandicoot's 64 KB pages |
| LOAD-029 | Exact decoders pinned (integer-exact builds checked against the PC's decoded output) | THEORETICAL | yes | Ocarina of Time's fixed-point decoders |
| LOAD-030 | Pre-computed startup values: provably pure static constructors run at build time | THEORETICAL | yes | NativeAOT static preinitialization |
| LOAD-031 | Trained compression dictionaries for many small similar files | THEORETICAL | yes | zstd |
| LOAD-032 | A pre-built shader cache shipped in the kit (if the compiler output is identical everywhere) | THEORETICAL | yes | Steam-style pre-caching; fallback = compile |
| LOAD-033 | Saved runtime class state (layouts, vtables, resolved tokens) mapped at boot | THEORETICAL | yes | Java Leyden JEP 483 / 515 |
| LOAD-034 | Background-rebuilt boot cache (pointer-free stream rebuilt while the card reads) | THEORETICAL | yes | JDK JEP 516 |
| LOAD-035 | Whole-process boot snapshot -- only if reading beats rebuilding | THEORETICAL (research) | yes | CRaC, Node.js startup snapshots, Wizer; reseed what a cold boot seeds |
| LOAD-036 | Tiled compression for parallel decode (64 KiB tiles) | THEORETICAL | yes | DirectStorage's GDeflate |
| LOAD-037 | Boot spill check after every rebuild (boot bytes must stay in the boot region) | THEORETICAL | -- | Android startup profiles |
| LOAD-038 | Flattened per-scene load lists (references pre-resolved; same creation / Awake order) | THEORETICAL | yes | Unreal 5 Zen Loader |
| LOAD-039 | Texture block split before compression (endpoints vs indices), rejoined at load | THEORETICAL | yes | Oodle BC7Prep |
| LOAD-040 | Format-aware compression for structured data | THEORETICAL (research) | yes | Meta OpenZL; must decode faster than the card |
| LOAD-041 | Decompress in place (zstd / LZ4 margins), newer zstd for ARMv7 | THEORETICAL | yes | |
| LOAD-042 | Preparation on the 4th core; cores 1-2 lend idle slices; core 0 only hands off | THEORETICAL | yes | one priority queue for card reads |
| LOAD-043 | Cache keys carry every accuracy setting; per-assumption fixups for compiled code | THEORETICAL | yes | RPCS3 / V8 / ReadyToRun practice |
| LOAD-044 | Write discipline: our writes batched into idle windows; the game's saves never delayed | THEORETICAL | yes | card writes can stall reads for 10s-100s of ms |
| LOAD-045 | I/O priority lanes (a read the player waits on beats background preloads) | THEORETICAL | yes | |
| LOAD-046 | Boot data on the PCH-2000's built-in storage | PARKED | yes | only if a device A/B shows a gain; hard write limits on soldered flash |
| LOAD-047 | Tiny launcher eboot + engine module behind an early logo | VERIFIED (start) | yes | TR-010, GT-001 |
| LOAD-048 | Shader cache on the card | VERIFIED | yes | TR-003 |
| LOAD-049 | Test loaders both from local storage and from a delayed source: loads that finish faster than authored expose races | THEORETICAL | yes | GT-015 |
