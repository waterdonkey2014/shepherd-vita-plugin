# Optimization patterns (OP)

Each pattern: what it is, when it helps, when it hurts, how to measure it, and where it was applied on a Vita (IDs from the
`vita-knowledge` catalog and entries). "Exact" means the output is unchanged; where a pattern can change output, it says so.

## CPU

### OP-001 -- Hoist repeated length / size computations
- Helps: loops that call `strlen`, `Count()` on a lazy sequence, or a size query that walks the data, once per iteration or per token.
- Hurts: never in itself; watch for data that really changes inside the loop.
- Measure: the loop's time against input size -- quadratic growth is the tell.
- Vita: ENG-006 (lookup memos).

### OP-002 -- Replace linear searches with an index
- Helps: "is it already in the list?" checks, Find-by-name / by-type over all objects, repeated lookups in an unsorted array.
- Hurts: tiny collections (a scan of 8 items beats a hash); the index must stay correct when items change; ordering semantics must be kept
  if callers rely on them.
- Measure: lookups per frame x cost per lookup; total time vs item count.
- Vita: ENG-001, ENG-002 (indexes that return results in the original scan order).

### OP-003 -- Cache results that are recomputed with the same inputs
- Helps: pure functions called repeatedly with repeating inputs; parsed data re-parsed every frame.
- Hurts: when the lookup costs more than the work (on a CPU with slow RAM a cache miss can cost 100+ arithmetic operations), when inputs
  rarely repeat, or when the cache hides a state change.
- Measure: hit rate and time saved per hit vs cost per miss; memory used.
- Vita: RT-059, ENG-006, GPU-001.

### OP-004 -- Remove duplicate checks and redundant work
- Helps: validation done at every layer, the same check in a loop body, empty callbacks invoked every frame.
- Hurts: removing a check that is the only guard on some path.
- Measure: count the calls; prove each removed check is redundant (dominated by an identical one).
- Vita: RT-018, ENG-004, ENG-021.

### OP-005 -- Better algorithmic complexity
- Helps: sorts, searches, scans and rebuilds that grow faster than the data (re-sorting an almost-sorted list, full rebuilds after one
  change).
- Hurts: rarely; but a "better" algorithm with a large constant loses on small inputs.
- Measure: time vs input size across realistic sizes.
- Vita: ENG-011 (coherence sort), WORLD-005 (local graph updates), UI-014 (incremental re-batching).

### OP-006 -- Data locality
- Helps: hot loops over objects scattered in memory; CPUs without hardware prefetch or with slow RAM.
- Hurts: when it forces copies to keep two layouts in sync, or when the hot set is already cache-resident.
- Measure: cache-miss counters if available, else time per element vs data size.
- Vita: MEM-009, MEM-010, MEM-011, CORE-014.

### OP-007 -- Software prefetch
- Helps: loops where the next record's address is known well ahead and the CPU does not prefetch by itself.
- Hurts: wrong distance (too early is evicted, too late is useless); bandwidth-bound loops; extra instructions in tiny loops.
- Measure: A/B per loop on the device; try several distances.
- Vita: MEM-008, RT-053..055.

### OP-008 -- Branch reduction where it pays
- Helps: unpredictable branches in hot code; per-element branches that are constant per batch (specialise the loop instead).
- Hurts: predictable branches (already nearly free); predication that executes loads or faulting work.
- Measure: time per element on realistic data, not on uniform test data.
- Vita: RT-049, CORE-002, CORE-003.

### OP-009 -- Smaller code on small instruction caches
- Helps: CPUs with small I-caches (e.g. 32 KiB), large methods, cold code mixed with hot.
- Hurts: hot inner loops that really need unrolling / inlining.
- Measure: build both, time both on the device, keep the winner per method.
- Vita: RT-040, RT-036, RT-056, RT-023.

### OP-010 -- Platform-appropriate parallelism
- Helps: independent work (render prep, animation, decoding, physics substeps) on spare cores.
- Hurts: when hand-off costs exceed the work; when results must be committed in an order the parallel version doesn't keep; shared
  writes.
- Measure: log every barrier's cost; compare the single-thread output byte for byte.
- Vita: CORE-005..007, ANIM-001, EX-006.

## Memory

### OP-011 -- Allocation reduction
- Helps: per-frame garbage that causes collections; short-lived temporaries.
- Hurts: pooling everything adds reset bugs and keeps memory resident.
- Measure: bytes allocated per frame; GC count and pause per minute.
- Vita: RT-041, RT-042, ENG-007.

### OP-012 -- Pools and arenas with clear lifetimes
- Helps: many objects with the same lifetime (per scene, per frame, per load); fixed-size pages for streaming.
- Hurts: objects that outlive their arena; pools sized for the worst case on a small heap.
- Measure: peak memory, fragmentation (largest free block), alloc cost.
- Vita: MEM-021, LOAD-028, MEM-005.

### OP-013 -- Fragmentation control
- Helps: long sessions on a heap with no spare room; allocators with size classes.
- Hurts: compaction pauses if done at the wrong time.
- Measure: largest free block over time, not just total free.
- Vita: GT-007, GT-008, MEM-026.

### OP-014 -- Resource lifetime management
- Helps: releasing what the next moment doesn't need (the place just left), keeping what it will (home textures in spare VRAM).
- Hurts: thrashing when the prediction is wrong; releasing state instead of resources.
- Measure: memory high-water marks per scene; hitches on return.
- Vita: WORLD-013, WORLD-020, MEM-028, MEM-031.

### OP-015 -- Compress cold data, never hot data
- Helps: data read rarely or read from slow storage.
- Hurts: data touched every frame (unpacking costs more than it saves).
- Measure: decode time vs read time saved; frame time with and without.
- Vita: LOAD-005, CORE-014, DROP-019.

## Loading

### OP-016 -- Precomputed metadata and binary formats
- Helps: text formats parsed at every start (JSON, XML, YAML), tables built at boot, reflection-driven deserialisers.
- Hurts: when the build-time format must be kept in sync with code changes; when the binary form is bigger than the compressed text and
  storage is the bottleneck.
- Measure: parse time at start vs read time of the prepared form.
- Vita: LOAD-001, LOAD-002, LOAD-026, LOAD-038.

### OP-017 -- Read in the order things are used
- Helps: slow storage with seek or request overhead; many small files.
- Hurts: when the order changes between runs (record it and rebuild).
- Measure: read throughput and request count during a load.
- Vita: LOAD-009, LOAD-013, LOAD-024.

### OP-018 -- Reduce initialisation work
- Helps: work done at start that the first screen doesn't need; static initialisers that compute constants.
- Hurts: moving work to a moment where it causes a visible hitch instead.
- Measure: a boot timeline (time to first picture, to first usable screen, work left after).
- Vita: LOAD-023, LOAD-030, LOAD-047.

### OP-019 -- Prepare during idle windows
- Helps: videos, fades, conversations, loading screens and menus where the CPU waits for the player.
- Hurts: preparing things that are then not used (memory pressure); running game logic early (changes behaviour).
- Measure: hit statistics of predictions; load time at the predicted moment.
- Vita: LOAD-014, WORLD-007..012.

## Rendering

### OP-020 -- Draw-call reduction and batching
- Helps: many small draws with the same state; per-draw CPU overhead dominates.
- Hurts: merging that changes draw order or blending results.
- Measure: draws per frame and CPU submit time; pixel A/B for order.
- Vita: GPU-002, GPU-031, GPU-032.

### OP-021 -- Retained geometry for what doesn't change
- Helps: static scenery, UI that changes rarely.
- Hurts: data that changes every frame (rebuild cost every frame plus the retained copy).
- Measure: rebuilds per frame, CPU time in mesh building.
- Vita: WORLD-001, UI-001, UI-011.

### OP-022 -- Texture and vertex format optimisation
- Helps: bandwidth-bound GPUs; memory-tight devices.
- Hurts: lossy formats where the fidelity rule forbids them; formats that don't round-trip exactly.
- Measure: VRAM use, GPU time, pixel A/B.
- Vita: GPU-003, GPU-019, GPU-037.

### OP-023 -- Visibility and culling
- Helps: work spent on things fully hidden (behind opaque UI, off screen, under a black fade).
- Hurts: culling that is not conservative (visible pops).
- Measure: draws and pixels skipped; a "green hole" debug fill to prove nothing visible was skipped.
- Vita: GPU-004, UI-004, GPU-013.

### OP-024 -- Shader simplification
- Helps: fragment-bound scenes.
- Hurts: any change in output where the fidelity rule applies; lower precision that changes pixels.
- Measure: GPU time per pass; pixel A/B.
- Vita: GPU-006, GPU-007.

## Build-time

### OP-025 -- Do expensive work at build time
- Helps: asset conversion, swizzling, compression, shader compilation, lookup tables, string hashing -- anything deterministic done on
  the device at every start.
- Hurts: when the result depends on device state or user data; when the prepared form is larger than what it replaces on slow storage.
- Measure: device time removed vs storage added.
- Vita: LOAD-010, LOAD-032, ENG-012, TR-001.

### OP-026 -- Offline compilation where supported
- Helps: platforms without runtime code generation, or where it is slow or restricted.
- Hurts: generic code the compiler couldn't foresee (needs an interpreter fallback); larger binaries read from slow storage.
- Measure: fallback counts at run time; binary size; load time.
- Vita: TR-001, TR-002, LOAD-022.

## Runtime

### OP-027 -- Hardware-aware scheduling
- Helps: devices with asymmetric cores or a borrowed core; work that can run on whichever core is idle.
- Hurts: migrating work that touches main-thread-only state.
- Measure: per-core utilisation; frame time split by core.
- Vita: LOAD-042, CORE-010, PWR-007.

### OP-028 -- Learning caches across runs
- Helps: work whose results repeat across sessions (shader compiles, hot method lists, read orders).
- Hurts: stale entries (key them on everything that affects the result); unbounded growth.
- Measure: hit rate, time saved, cache size; verify entries on first reuse.
- Vita: LOAD-011, LOAD-043, RT-029.
