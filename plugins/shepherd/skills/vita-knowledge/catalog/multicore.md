# Idea catalog: native core, threads and multicore (CORE)

The Vita has three cores for apps (four with a plugin, VH-002), and a Unity game runs its logic on one. The rule that keeps these exact:
work moves to other cores only when its output is committed in the original order, and game logic itself moves only behind a
device-to-host lockstep check (CORE-012). Floats stay on VFP (FID-004): NEON here is for integer / layout work and copies.

| ID | Idea | Status | Exact | Source / notes |
|---|---|---|---|---|
| CORE-001 | A native C core for render prep (transforms, culling, sort keys, vertex fill) with SoA arenas and PLD | THEORETICAL | yes | NEON only for non-float data movement |
| CORE-002 | Shape-specialised vertex writers (single quad, 9-slice panel, glyph run) with no per-vertex branches | THEORETICAL | yes | Wolfenstein 3D's compiled scalers; byte-checked against the generic loop; small enough for the 32 KiB I-cache |
| CORE-003 | Plain-sprite fast path: white tint, alpha 1, no flip, identity UV -> a stripped loop without the multiplies | THEORETICAL | yes | devilutionX; x 1.0 is exact in IEEE; byte-checked |
| CORE-004 | Radix sort over one packed draw-order key (layer, order, sign-flipped full float depth bits, tie-break) | THEORETICAL (research) | yes | PS1 ordering tables; A/B against the coherence sort (ENG-011); depth is never bucketed |
| CORE-005 | Render-prep job system: fork-join over contiguous renderer ranges, each job writing its own buffer, merged in a fixed order | THEORETICAL | yes | Sega Saturn's twin CPUs, Total War: Three Kingdoms, Dyson Sphere Program; the command stream equals the single-threaded one |
| CORE-006 | Spin-then-block hand-offs measured in microseconds + half-of-remaining work stealing; every barrier's cost logged | THEORETICAL | yes | a frame never spends more on hand-offs than it gains |
| CORE-007 | Scene-reading render prep on the render thread from a snapshot taken at the end of LateUpdate | THEORETICAL | yes | Unity's own multithreaded rendering; only game-code steps (UI rebuild callbacks) stay on the main thread |
| CORE-008 | Particles simulated and meshed on a helper core; everything the original draws is drawn | THEORETICAL | yes | |
| CORE-009 | Saving on a spare core: snapshot what the game writes, write it off the main core, same format and order | THEORETICAL | yes | |
| CORE-010 | The main core emptied of everything that is not game logic (render prep, animation, physics, path scans, audio, loading) | THEORETICAL | yes | the precondition for the rest |
| CORE-011 | Ordered parallel commit: a game system (e.g. per-entity needs, tasks, movement decisions) runs across cores, results applied in the original order | THEORETICAL (research) | yes, gated | applied system by system, each behind its own switch |
| CORE-012 | Device-to-host lockstep hash rig: per-frame state hashes from the device compared with the reference engine | THEORETICAL | -- | gates every native rewrite; doubles as a co-op desync detector |
| CORE-013 | Speculative entity updates on helper cores with a read-set conflict check; the main core reruns any entity whose inputs changed | THEORETICAL (research) | yes | |
| CORE-014 | Hot per-entity data as compact cache-friendly arrays (packed, never compressed); cold data compressed with a decode cache | THEORETICAL | yes | unpacking every frame costs more than it saves; save format never changes |
| CORE-015 | Native rewrites shipped one system at a time, behind its own switch, each after passing the lockstep rig | THEORETICAL | yes | gradual, never one big drop |
| CORE-016 | Two-device ad-hoc lockstep co-op, later online through a relay with rollback | THEORETICAL | -- | needs CORE-012's determinism first |
