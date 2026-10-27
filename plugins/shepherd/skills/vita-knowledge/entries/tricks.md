# Tricks that worked (TR)

Context: a modern Unity game's own compiled C# running on a Mono runtime ported to the Vita, under a from-scratch Unity stand-in engine,
rendered with vitaGL. Numbers are device-measured unless labelled.

### TR-001 -- Precompile the engine ahead of time (AOT)
- Status: VERIFIED. Category: runtime / CPU.
- Result: the idle menu went from 159 ms per frame (interpreted, on screen) to 65 ms (AOT, headless measurement) in one step.
- Note: game code can stay interpreted (no compiler needed on the player's side) or be AOT-compiled too.

### TR-002 -- Use the LLVM backend for AOT
- Status: VERIFIED. Category: runtime / CPU / memory.
- Result: menus ~20 % faster (64.5 -> 51.4 ms) and ~10 MiB more free memory (smaller code).
- Settings: `-mcpu=cortex-a9`, hard float, VFP not NEON for floats (exactness), DWARF exceptions.

### TR-003 -- Keep the shader cache on the card
- Status: VERIFIED. Category: GPU / loading.
- Result: shader setup 7.4 s -> 0.5 s per start (after GT-005 was fixed).

### TR-004 -- Packs, big ordered reads, lazy release
- Status: VERIFIED. Category: loading / memory.
- Result: game data rearranged into packs read in big blocks in a recorded order; files released after N idle frames; CPU copies of
  textures dropped after GPU upload.

### TR-005 -- One GC before the first frame, collections at real scene loads
- Status: VERIFIED. Category: memory.
- Result: boots started from a clean heap with ~12 MiB more room; out-of-memory ends at the menu disappeared.

### TR-006 -- Size thread stacks from a stack watch; an IL pool
- Status: VERIFIED. Category: memory.
- Result: stacks sized from measured high-water marks; assembly images read into a dedicated pool so they don't fragment the C heap.

### TR-007 -- Exact engine shortcuts
- Status: VERIFIED (identical output on scripted routes; device runs green). Category: CPU.
- Examples: tag lookups from an index instead of a scene walk, stable insertion sorts instead of LINQ re-sorts, skipping Update methods whose
  body is only `ret`. Same answers, same order -- checked frame by frame.

### TR-008 -- Share skeletal-animation data; load skins lazily
- Status: VERIFIED. Category: memory.
- Result: Spine skeletons share their common data and only load the skins shown; several MiB off the heap.

### TR-009 -- Trim the standard library to what the game calls
- Status: VERIFIED (size, reproducible build measurement); device effect pending. Category: memory.
- Result: CoreLib in the image 25 -> 17.8 MiB (interpreted fallback for the rest); 17.3 -> 13.3 MiB on the LLVM builds; +5 to +9 MiB of
  free memory.

### TR-010 -- A tiny launcher eboot that loads the engine as a module
- Status: VERIFIED (start + module load on device), picture fix EXPERIMENTAL (EX-003). Category: boot.
- Result: the launcher starts its splash ~40 ms after the tap (the full app showed nothing for ~105 s); the 21 MB engine module loads in
  ~4 s behind it. Requires GT-001's import rule.

### TR-011 -- Small, player-visible wins
- Status: VERIFIED. Category: controls / safety.
- Examples: rear-touch corners as the missing L2 / R2 / L3 / R3; a late input latch (one input state per frame read at the first query);
  save backups (5 per file) with read-back verification and a restore option; showing the measured clock.

### TR-012 -- Thread-local storage fast path
- Status: EXPERIMENTAL (emulated profile). Category: runtime.
- Result: runtime TLS lookups 7.1 % -> 1.8 % of the idle main thread by mirroring the runtime's keys in fixed TLS slots.
