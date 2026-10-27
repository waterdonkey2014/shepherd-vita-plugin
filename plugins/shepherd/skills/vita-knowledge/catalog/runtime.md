# Idea catalog: runtime (RT) -- interpreter, AOT, LLVM, JIT, calls

Context: a Mono runtime (from .NET 8) ported to the Vita runs a Unity game's compiled C#: an interpreter, static AOT (Mono or LLVM
backend), and an experimental baseline JIT. "Exact" = the game computes the same results. Status: VERIFIED (device), EXPERIMENTAL
(built, off-device only), THEORETICAL (not built), FAILED. Estimates are labelled.

| ID | Idea | Status | Exact | Source / notes |
|---|---|---|---|---|
| RT-001 | Fast TLS: mirror the runtime's TLS keys in fixed `sceKernelGetTLSAddr` slots | EXPERIMENTAL | yes | TLS lookups 7.1 % -> 1.8 % of the idle main thread (emulated) |
| RT-002 | Typed icall stubs: generate typed stubs for the hot engine calls instead of a generic marshalling path | EXPERIMENTAL | yes | 32 hot stubs typed in v1 |
| RT-003 | Zero-hop mirrors: getters the game calls every frame read from a managed mirror of engine state | EXPERIMENTAL | yes | 14 getters = 22 % of engine calls |
| RT-004 | Profile-ordered AOT layout (method order + LLVM function reorder) | EXPERIMENTAL | yes | idle hot code 448 -> 218 pages |
| RT-005 | AOT dedup of generic instances | EXPERIMENTAL | yes | -1.2 to -1.5 MiB per LLVM app; a gsharedvt part (~5.8 MiB) needs a runtime lookup change |
| RT-006 | LLVM safepoint thinning (counted polls) | EXPERIMENTAL | yes | -7 % poll sites, -0.19 MiB |
| RT-007 | 64-bit div/rem with 32-bit operands done as 32-bit division | EXPERIMENTAL | yes | wrapper calls removed at ~1,700 sites |
| RT-008 | Trim the standard library to what the game calls (interpreter fallback for the rest) | VERIFIED (size) | yes | 25 -> 17.8 MiB; LLVM builds 17.3 -> 13.3 MiB (needs the runtime's partial-image fix) |
| RT-009 | PGO + LTO of the runtime and host C | THEORETICAL | yes | profiles from scripted runs |
| RT-010 | IL compaction + compressed IL for methods that are compiled | THEORETICAL | yes | memory |
| RT-011 | Compressed IL for methods that never ran yet, unpacked on first call | THEORETICAL | yes | most game methods never run in a session; a few MiB (estimate) |
| RT-012 | Interpreter transform cache: keep converted interpreter bytecode in a learning cache | THEORETICAL (measured) | yes | ~18k methods converted by the first menu |
| RT-013 | Backport .NET 9's interpreter SSA optimizer, run only when a method tiers up | THEORETICAL | yes | dotnet/runtime PR #96315; changes the IR identity checks rest on -- heavy |
| RT-014 | Self-specialising interpreter opcodes (quickening) with miss counters | THEORETICAL (measured) | yes | CPython PEP 659; measured worth < 1 ms on an idle menu |
| RT-015 | Interpreter entry on the AOT calling convention (no argument translator) | THEORETICAL (measured) | yes | Android ART nterp; ~1,400 crossings per idle frame -- the largest remaining lever there |
| RT-016 | Reflection memo (member lookups, field lists, attributes answered from a per-type table) | THEORETICAL | yes | |
| RT-017 | Closed-world devirtualization in the AOT (one implementation -> direct call, with guards) | THEORETICAL | yes | Stardew console ports (BRUTE), IL2CPP, N64Recomp |
| RT-018 | Drop only PROVABLY redundant null / bounds checks (the first check always stays) | THEORETICAL | yes | IL2CPP's Il2CppSetOption; exceptions must happen where the original's would |
| RT-019 | Loop cloning / predication: one up-front check selects an unchecked copy of a hot loop | THEORETICAL | yes | LLVM loop versioning; only when the body can't change the collection |
| RT-020 | Cheaper locks: biased owner-thread fast path, skip barriers on main-thread-only objects | THEORETICAL | yes | BlitWorks' Bastion Vita port |
| RT-021 | Faster small copies: memcpy / memset to `sceClibMemcpy` or NEON where a per-size benchmark wins | THEORETICAL | yes | vitaGL's copy helpers |
| RT-022 | Drop a static constructor's bytecode and IL after it ran (runs once) | THEORETICAL | yes | Jak & Daxter-style "run-once code" |
| RT-023 | Cache-tuned code layout (Ext-TSP block placement, CDSort function order, A9 32 KiB I-cache) | THEORETICAL | yes | for both LLVM AOT and the GCC-built runtime C |
| RT-024 | Hardware null checks through kubridge exception handlers (implicit checks, fault -> NullReferenceException) | THEORETICAL | yes | needs the kubridge plugin; explicit checks kept for others |
| RT-025 | Baseline JIT: copy-and-patch Thumb-2 stencils, interpreter-shaped frames, one definition for both | EXPERIMENTAL | yes | lockstep 0 mismatches; device speed undecided (see FA-006) |
| RT-026 | JIT: compile only paths actually seen (uncommon traps, per-site exits) | EXPERIMENTAL | yes | -20 % interpreter dispatches vs the first JIT (emulated) |
| RT-027 | JIT: call AOT code directly from traces (register calls / veneers) | EXPERIMENTAL | yes | calls into other INTERPRETED methods stay with the interpreter |
| RT-028 | JIT: trivial getters as intrinsics | EXPERIMENTAL | yes | opt-in until a lockstep run covers a real callee |
| RT-029 | JIT learning cache across starts (hot / not-worth-it entry points saved) | EXPERIMENTAL (device-seen) | yes | 2nd start compiled 2,428 entry points at first hit on the device |
| RT-030 | JIT code publishing in batched windows on one thread | VERIFIED (rules) / EXPERIMENTAL | yes | VH-008 rules; 619-994 windows per route |
| RT-031 | Polymorphic call caches (2-4 types -> checked jump table) | THEORETICAL | yes | |
| RT-032 | Code layout by call graph (callers next to callees) | THEORETICAL | yes | |
| RT-033 | LLVM for the game's own code (not just the engine) | THEORETICAL | yes | engine switch to LLVM gave -20 %; estimate -10-20 % of game-logic time |
| RT-034 | Whole-program LLVM: optimise all assemblies' bitcode together (cross-assembly inlining) | THEORETICAL | yes | estimate 5-10 % |
| RT-035 | Profile-guided branch weights / inlining inside functions | THEORETICAL | yes | estimate 3-8 % |
| RT-036 | Hot code for speed, cold code for size | THEORETICAL | yes | smaller image = more heap |
| RT-037 | Alignment-aware loads: drop a blanket "assume misaligned" flag where alignment is provable (LDRD / LDM) | THEORETICAL | yes | estimate 1-3 % |
| RT-038 | Code overlays: rarely used compiled code in modules loaded per scene and unloaded after | THEORETICAL | yes | PS2 / PSP / DS technique; modules obey GT-001; estimate 5-15 MiB |
| RT-039 | A build-time icall hook table (no runtime scan) | EXPERIMENTAL | yes | |
| RT-040 | Small-vs-fast per method: each hot method built size- and speed-optimised, both timed on the device, the winner kept | THEORETICAL | yes | the Super Mario 64 lesson (Kaze Emanuar): on a cache-starved CPU smaller code often wins; both builds must match in lockstep |
| RT-041 | JIT escape analysis: objects created and dropped inside one method live on the stack | THEORETICAL | yes | types with finalizers excluded; only garbage / GC timing change |
| RT-042 | Conditional / partial escape analysis + allocation sinking with unsink-on-exit (boxes, small arrays, delegates, enumerators) | THEORETICAL (research) | yes | .NET 9-10, Graal, LuaJIT; a bailout rebuilds each sunk object once, in program order; locking / hashing counts as an escape |
| RT-043 | Faster exception path (cached unwind tables, faster catch search) | THEORETICAL | yes | only if the profiler shows the game throws in normal play |
| RT-044 | Exact deopt state at side-effect points: each guard records the IL offset + where every live IL value sits | THEORETICAL | yes | V8 Maglev, Graal, Self; a failed guard rebuilds the exact interpreter frame |
| RT-045 | Speculative AOT code with an exact interpreter continuation (no executable memory needed) | THEORETICAL (research) | yes | LLVM deopt model lowered by hand for ARMv7; first only at stack-empty IL points, never inside inlined bodies |
| RT-046 | Physical promotion of small struct fields (Vector2 / 3 / Quaternion fields in separate VFP registers) | THEORETICAL | yes | .NET 8 / 10; stored fields float32, intermediates exactly as the reference runtime keeps them (FID-002) |
| RT-047 | Loop peeling for loop-invariant code motion + guard hoisting | THEORETICAL | yes | LuaJIT LOOP pass; forward a load only when nothing in the body may alias it; IEEE-exact folding only |
| RT-048 | Inline small library helpers (List indexer / Count, Mathf, vector ops) into JIT'd game code from their IL | THEORETICAL | yes | SPUR (trace JIT for CIL); a never-inline list for icalls and anything that walks the stack |
| RT-049 | IT-block predication for unpredictable integer selects | THEORETICAL | yes | ART's rules; never for floats, never when a side loads, calls or can fault |
| RT-050 | An optimising tier reuses Mono's own register allocators and a flat CFG IR (not sea-of-nodes) | THEORETICAL | -- | V8 leaving Sea of Nodes (Turboshaft), Maglev; compile speed matters on a 444 MHz A9 |
| RT-051 | Guarded inlining of the dominant delegate / interface target from cheap reservoir type profiles | THEORETICAL | yes | .NET 8 Dynamic PGO (delegate GDV, 32-entry reservoir, per-core approximate counters) |
| RT-052 | Profile-guided inlining behind a type check that falls back to the normal call | THEORETICAL | yes | |
| RT-053 | Prefetch (PLD) in the game's own hot loops over reference arrays / lists: element i+k and the object it points to | THEORETICAL | yes | Ainsworth & Jones (ISMM 2020); pays more with MEM-011's depth-first copying; kept per loop only where timing shows a win |
| RT-054 | Prefetch distance from measured timing (~252 ns miss / measured iteration time) | THEORETICAL | yes | APT-GET (EuroSys 2022); miss cost from VH-005 |
| RT-055 | Prefetch distance tried on the device per loop; PLD dropped where every variant is slower | THEORETICAL | yes | RPG2 (ASPLOS 2024) |
| RT-056 | Smaller cold code: the 32-bit ARM machine outliner (+ an ML size inliner if the toolchain allows) on startup / menu methods | THEORETICAL | yes | MLGO; smaller AOT images read faster from the card |
| RT-057 | On-stack replacement: a long loop already in the interpreter switches to compiled code mid-run | THEORETICAL (research) | yes | boot and load loops |
| RT-058 | JIT front-end cache: the analysed form of hot methods kept on the card as data | THEORETICAL | yes | data, not machine code; device compiles skip to code generation |
| RT-059 | Value-profiled memoization: a small exact-input cache only for provably pure methods called with repeating inputs | THEORETICAL (research) | yes | only where the lookup costs less than the work (one RAM miss ~ 100+ arithmetic ops) |
| RT-060 | Self-disabling native method table: native versions of the hottest game methods keyed by assembly MVID + token + IL hash | THEORETICAL | yes | TheFloW's GTA: San Andreas Vita port; each entry proven bit-identical in lockstep; turns itself off when the IL changes |
| RT-061 | IL -> C for a small hot set | THEORETICAL | yes | only if the profile shows a small set covering ~80 % of game self-time |
