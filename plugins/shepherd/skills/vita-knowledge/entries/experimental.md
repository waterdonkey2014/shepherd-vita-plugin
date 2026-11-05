# Experimental (EX) -- built and passing off-device, waiting for a device run

### EX-001 -- Concurrent garbage collection on another core
- Status: EXPERIMENTAL (emulated). Category: memory / CPU.
- Result: SGen's major collections run concurrently on a spare core: worst major pauses ~3-5x shorter, total major-pause time -38 to -53 %.
  Kept serial near the heap cap (refusals rise there). One app variant's worst pause rose -- check per app.

### EX-002 -- A baseline JIT for interpreted game code
- Status: EXPERIMENTAL (identity proven off-device; speed undecided on device). Category: runtime.
- Design: copy-and-patch Thumb-2 stencils with interpreter-shaped frames, compiling only hot loops, a learning cache across starts, batched
  code publishing on one thread, uncommon traps for unseen paths. Lockstep against the interpreter: 0 mismatches over tens of millions of
  trace runs. Off-device: ~20 % fewer interpreter dispatches than the first version.

### EX-003 -- Video playback that tolerates decoder output delay
- Status: EXPERIMENTAL. Category: video. The fix for GT-002 (feed while pending, drain, time by output; clips without B-frames).

### EX-004 -- Reserving decoder memory before the GL library
- Status: EXPERIMENTAL. Category: memory / video. The fix for GT-003 (~6 MiB PHYCONT reserved before `vglInit`).

### EX-005 -- Suspend detection by RTC
- Status: EXPERIMENTAL. Category: platform. The fix for GT-004; a modelled 30 s standby logged its suspension and re-raised the clocks.

### EX-006 -- Physics work spread over worker threads, exactly
- Status: EXPERIMENTAL (exact off-device; off by default). Category: physics / CPU.
- Result: Box2D's parallel-safe phases forked to workers and applied back in serial order; identical results. Off by default until a device
  A/B shows the forks pay on the A9 (the physics step was under 1 % of the main thread in the measured scenes).

### EX-007 -- Real-time step for frame-locked Flash games
- Status: EXPERIMENTAL (host: RuffleVita desktop build; installed on a Vita, its timing not yet measured there). Category: runtime /
  timing. Runtime: Flash (ActionScript 3) on RuffleVita.
- Source: maintainers (Flash side project, 2026-11); reproduced by maintainers: yes (host).
- Problem: many Flash games step their logic by a constant every frame (`onUpdate(33)`, whatever time really passed) and play their
  animations on timelines, one timeline frame per rendered frame. Below the authored frame rate the whole game runs in slow motion: 12 fps
  of a 34 fps game is 35 % speed.
- Fix / use: replace the constant with the time the update method already read from `getTimer()`, scaled to the authored step
  (`elapsed * 1122 / 1000` for a 33 step at 34 fps) and capped (100 here) so collisions can't tunnel. A short bytecode patch.
- Evidence: stage forced to 15 fps, level start to first tutorial, wall clock: original at 34 fps 13.0 s, original at 15 fps 29.5 s,
  patched at 15 fps 13.3 s.
- Limits: only what moves through that step keeps its speed. Timeline animations, and code that moves things a fixed amount per
  `enterFrame` outside the step, still slow down -- read every `enterFrame` listener before trusting it.

### EX-008 -- Smooth 60: frames at 60, timelines at their authored rate
- Status: EXPERIMENTAL (host; first device run 2026-11-04: menus at 60 fps, gameplay below 60 -- owner's report, no log yet).
  Category: runtime / frame pacing. Runtime: Flash on RuffleVita (a patch to Ruffle's frame loop).
- Source: maintainers; reproduced by maintainers: yes (host).
- Fix / use: the player runs its frames (`enterFrame` scripts, drawing) at 60 per second while MovieClip timelines step from an
  accumulator at the movie's own rate. On a frame between two timeline steps the Enter phase skips the playhead pass and only broadcasts
  `enterFrame`; the construct, frame-script and exit phases run as usual (nothing new to do, so they cost little). A per-game opt-in,
  set or cleared at every game start because the switch is global in the core.
- Evidence (host; a 34 fps game already using EX-007): level start to first tutorial 12.98 s at 60 vs 13.00 s at 34; one second captured
  frame by frame: 60 of 60 frames differ from the one before; the run cycle keeps its authored pace. With the setting off, screenshots
  and instruction counts are byte-identical to before.
- Limits: needs logic that follows the clock (EX-007), or the game runs 1.76x fast. Work per frame is unchanged, so 60 fps costs
  ~1.76x the CPU per second. Anything moved a fixed amount per `enterFrame` outside the step speeds up. Compare GPU-041.
- Device gotcha (fixed): the timeline accumulator must take the real time given to the player's tick, not 1/60 s per frame drawn.
  The first version did the latter; on the Vita, gameplay drew fewer than 60 frames and could not catch up, so animations slowed (a
  run cycle at ~half speed at 30 fps) while clock-driven movement kept its speed. Fixed: steps follow tick time, at most one per
  frame, excess dropped. Host check with every game frame slowed to ~22 ms: 30 fps, 30 timeline steps/s (the old code: ~17), game
  timing unchanged.
- With V-Sync on, a frame that misses 16.7 ms waits for the next refresh: anything over it runs at 30 fps, where this mode gains
  nothing over the authored rate. It only pays when the whole frame (game code + drawing) fits in 16.7 ms.

### EX-009 -- Skip to the next object that needs work, natively
- Status: EXPERIMENTAL (host; exact). Category: CPU / engine loop. Runtime: Flash on RuffleVita's AOT.
- Source: maintainers; reproduced by maintainers: yes (host).
- Problem: the game's render loop tested every object of the level for visibility every frame (~2,360 objects in 15 layers), though only
  a handful change state per frame. With compiled code on, that loop was 63 % of all game-code time (sampling profiler).
- Fix / use: an object needs work only when its on-screen test and its active state ("has a picture") disagree. The now-unused
  visibility method gets a new signature and body -- `scan(i, list, view values)` returns the next index that needs work -- written in
  ActionScript, so it is exact on its own, and the loop calls it at its head. The loop body is unchanged and re-checks whatever it gets.
  The runtime swaps that one method for a native, matched by name plus parameter count so it can never apply to the unpatched game:
  plain slot reads with slot ids cached per class, the same f64 test in the same operand order. Anything unexpected (an entry that
  isn't an object, a field that isn't a slot, a value that isn't a number) stops the scan there and the game's own code takes over.
- Evidence (host, deterministic timedemo): 5.10 -> 3.45 M instructions per frame (-32 %); byte-identical screenshots on all four levels,
  native vs interpreted and new build vs previous build.
- Limits: every object is still touched every frame, only cheaply. Skipping objects altogether needs proof that they never move
  (ENG-023).

### EX-010 -- Bytecode inlining and hoisting before AOT
- Status: EXPERIMENTAL (host; exact). Category: CPU. Runtime: Flash (AVM2 bytecode).
- Source: maintainers; reproduced by maintainers: yes (host).
- Fix / use: a 4x4 matrix-times-vector that read its elements through 16 `getElem(r, c)` calls reads the array directly; a per-object
  loop reads four display-object getters once before the loop instead of four times per object; a one-caller test is inlined. A small
  AVM2 re-assembler with branch fix-up makes length-changing edits safe -- it round-trips all 3,293 method bodies of the game
  byte-identically before any edit is trusted.
- Evidence: interpreted, 15.69 -> 8.94 M instructions per frame (-43 %), screenshots identical.
- Limits: prove a hoisted value can't change inside the loop (read every writer); inline only methods with one caller and no overrides.

### EX-011 -- Size restored art by how big the game really draws it, with smaller copies for the small moments
- Status: EXPERIMENTAL (host; device run pending). Category: GPU / art pipeline. Runtime: Flash on RuffleVita (any engine that draws
  bitmaps under arbitrary transforms).
- Source: maintainers; reproduced by maintainers: yes (host).
- Problem: upscaled or AI-restored pictures were all resized to one factor, the stage-to-screen scale, which is pixel-exact only when the
  game draws a picture at its natural size. Flash games scale pictures freely: one game's title cards drop onto the screen from 2.7x their
  resting size, and a smoke picture is drawn at 20-80 %. A bigger copy alone fixes the big moment but turns grainy at rest, because the
  renderer minifies with plain bilinear sampling and no mipmaps.
- Fix / use: (1) a texel census in the renderer (a test switch): for every draw of a bitmap -- direct bitmap draws, CPU-batched bitmap
  fills and GPU bitmap fills -- the singular values of the texel-to-screen map, keeping the most and least per texture size. Scripted runs
  over menus and every level give each picture's real on-screen range. Sanity check: untouched pictures read exactly the stage scale.
  (2) A picture drawn bigger than natural is kept at twice its natural size; one drawn much smaller stays natural. Both are listed in a
  sidecar file next to the movie, by texture size. (3) The renderer gives listed textures half-size copies (2x2 box average of the
  premultiplied pixels, built once at upload) as plain textures, not GL mipmaps, so nothing depends on the driver's mipmap support for
  non-power-of-two sizes. UVs are normalised, so a copy draws in place of the full texture. Each draw picks the copy nearest one texel
  per screen pixel (GL's nearest-level rule, from the smaller singular value). Twice natural makes the first copy exactly the natural-
  size picture, so the resting look matches the old build and only the big moments gain.
- Evidence (host): in one game, 1,321 pictures were drawn and 163 of them bigger than natural at some point. Title cards mid-drop are
  visibly sharper; at rest they match the previous build within filter rounding; every other frame checked is byte-identical (81 sampled
  frames of a level, the title before the drop). Memory: about +7 MiB for five pictures.
- Limits: the census is per texture size, so pictures sharing a size share a row (the larger wins). Coverage is only as good as the
  scripted runs. Copies are chosen per draw without blending between levels, so a picture shrinking smoothly can step at a level change.
  Device check pending: the copies' memory and their upload time at first draw.
