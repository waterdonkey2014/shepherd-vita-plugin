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
