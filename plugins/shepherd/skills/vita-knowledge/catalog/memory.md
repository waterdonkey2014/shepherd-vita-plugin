# Idea catalog: memory (MEM) -- GC, heaps, layout, RAM stalls

The Vita's RAM latency (~252 ns per miss, no prefetch: VH-005) and a small heap make memory the wall. Exact = only where data lives or
how it is stored changes, never what the game computes.

| ID | Idea | Status | Exact | Source / notes |
|---|---|---|---|---|
| MEM-001 | Concurrent major GC on a spare core (mark + sweep), serial near the heap cap | EXPERIMENTAL | yes | worst major pauses ~3-5x shorter, total -38..-53 % (emulated) |
| MEM-002 | Split nursery (survivors age once before promotion) | EXPERIMENTAL | yes | |
| MEM-003 | Per-scene nursery sizing learned from each scene's allocation history | EXPERIMENTAL | yes | confirm the game has no finalizer / weak-reference behaviour tied to GC timing |
| MEM-004 | A correct per-frame "used size" for the GC (no full walk per query) | EXPERIMENTAL | yes | |
| MEM-005 | Two-ended arena (small objects from one end, large from the other) | EXPERIMENTAL | yes | less fragmentation |
| MEM-006 | One GC before the first frame; collect at real scene loads like Unity | VERIFIED | yes | TR-005 |
| MEM-007 | String interning + a pruned asset catalog | THEORETICAL | yes | |
| MEM-008 | Software prefetch intrinsic (PLD) used in the engine's hot walks | THEORETICAL | yes | the call sites exist; needs a runtime intrinsic |
| MEM-009 | Packed hot records: per-frame engine fields in contiguous arrays by slot | EXPERIMENTAL (partial) | yes | sort keys packed; full SoA not built |
| MEM-010 | Hot fields first inside game objects (auto-layout classes only) | THEORETICAL | yes | reflection still reports declaration order |
| MEM-011 | Neighbours stored together: depth-first copying when the GC moves survivors | THEORETICAL | yes | SGen's nursery already scans depth-first |
| MEM-012 | Hot / cold object separation at promotion | THEORETICAL | yes | HCSGC (PLDI 2020) |
| MEM-013 | Frozen object region for objects that live forever (literals, type objects, empty arrays) | THEORETICAL | yes | .NET 8 non-GC heap |
| MEM-014 | Pinned-object area (long-pinned buffers allocated non-moving) | THEORETICAL | yes | .NET 5 POH; count pinned fragments first |
| MEM-015 | Pretenuring by allocation site | THEORETICAL | yes | LLAMA (ASPLOS 2020) |
| MEM-016 | Promote dense nursery chunks in place instead of copying | THEORETICAL | yes | .NET regions, Generational ZGC, V8 MinorMS |
| MEM-017 | Block-batched major marking (mark by page) | THEORETICAL | yes | Go's Green Tea GC |
| MEM-018 | 4-byte object headers (drop the sync word) | THEORETICAL (census first) | yes | Project Lilliput (JEP 450) |
| MEM-019 | Big memory pages for the heap | FAILED | -- | FA-002: no gain |
| MEM-020 | One purgeable cache arena: rebuildable caches evicted on demand | EXPERIMENTAL | yes | Doom's zone allocator |
| MEM-021 | Per-scene engine arenas freed in one step | THEORETICAL (measured) | yes | Jak & Daxter level heaps; nothing native to free on the measured routes |
| MEM-022 | A modern native allocator for the C heap (mimalloc / rpmalloc) | THEORETICAL | yes | less fragmentation; A/B first |
| MEM-023 | Write-combined memory for CPU-write / GPU-read buffers | THEORETICAL | yes | keep anything the CPU reads back cached |
| MEM-024 | Cold CPU data in free VRAM (pack cache, catalog, audio indexes, IL pool) | THEORETICAL | yes | 31-55 MiB free VRAM measured (VH-007); estimate tens of MiB off main RAM |
| MEM-025 | One shared pool for the C heap and the managed arena (grow from both ends) | THEORETICAL | yes | a fixed C heap peaked well below its reservation; estimate 10-20 MiB |
| MEM-026 | Fragmentation fixes: measure holes, then SGen major-block evacuation | THEORETICAL | yes | GT-007 |
| MEM-027 | Size-class audit of engine types | VERIFIED (one case) | yes | GT-008 |
| MEM-028 | Memory pressure ladder: optional memory given back in a fixed order when free memory falls | THEORETICAL | yes | |
| MEM-029 | Dormant inactive subtrees (memory reserve for objects switched off for long) | THEORETICAL | yes | |
| MEM-030 | Zero-fill off the main core; PLD inside the GC; PHYCONT mapping (probe-gated) | THEORETICAL | yes | |
| MEM-031 | Drop CPU copies of textures after upload; lazy file release | VERIFIED | yes | TR-004 |
| MEM-032 | Share skeletal-animation data, lazy skins | VERIFIED | yes | TR-008 |
