# Idea catalog: fidelity (FID) -- matching the original exactly

Tools and rules for making the port compute what the original computes (same random numbers, same float results, same order).

| ID | Idea | Status | Exact | Source / notes |
|---|---|---|---|---|
| FID-001 | Unity-exact random numbers (UnityEngine.Random reimplemented to Unity's sequences) | EXPERIMENTAL | yes | differences vs a Unity oracle 6,862 -> 198 (1-16 ulp) |
| FID-002 | PC-like float precision for managed code (double intermediates) behind a switch | EXPERIMENTAL | yes | Mono forces float32 on ARM; an IL rewrite tool did it; x64 suite 121/122 |
| FID-003 | Copy x64's float-to-int edge cases (NaN, infinities, out-of-range) in every tier | EXPERIMENTAL (partial) | yes | XenonRecomp's approach; probe the PC version for the reference |
| FID-004 | VFP-only float maths, FZ / DN off, never NEON for floats; a build scan that fails on NEON float ops | EXPERIMENTAL (scan built) | yes | NEON flushes denormals |
| FID-005 | One shared libm for every tier + no build-host constant folding | THEORETICAL | yes | needs golden values from the PC reference |
| FID-006 | NaN bit patterns: keep operand order; exact-NaN mode only if the game reads raw bits | THEORETICAL (census) | yes | the measured game reads raw bits at ~290 sites |
| FID-007 | Exact fast maths: faster sin / cos / atan2 / pow / sqrt proven bit-for-bit over the used input ranges | THEORETICAL | yes | |
| FID-008 | Fix stand-in API differences found by tests against a Unity oracle, one switch each | EXPERIMENTAL | yes | JsonUtility, number formatting, curve evaluation, defaults ... |
| FID-009 | Sprite tie order exactly like Unity's | THEORETICAL | yes | needs an editor check |
| FID-010 | Identity checks: per-frame render-command hashes + an audio stream hash on scripted routes | VERIFIED (method) | -- | the backbone of every default change |
| FID-011 | Lockstep check: a new execution tier compared against the interpreter op by op | VERIFIED (method) | -- | JIT: 0 mismatches over tens of millions of runs |
| FID-012 | A Unity editor oracle for physics and API behaviour | VERIFIED (method) | -- | settles hypotheses the decompiled code can't |
| FID-013 | Official platform visuals (another console's official assets / effects) count as "original" only by the project lead's decision | rule | -- | anything the original never drew is opt-in |
| FID-014 | Timing minigames judge a press at the frame it lands in, so a low frame rate changes their feel | OBSERVED (read from game code) | -- | a true 60 matters most here; a 60 fps visual mode alone doesn't move where a press is judged |
| FID-015 | Camera shakes that roll a random direction once per frame depend on the frame rate even on PC | OBSERVED (read from game code) | -- | keep live; don't "fix" it |
| FID-016 | Whole-game screenshot A/B at fixed frames in a deterministic timedemo (virtual clock, seeded random): compiled vs interpreted, and new build vs previous | VERIFIED (host procedure) | yes | every Flash speed patch (EX-009, EX-010) and three AOT table rebuilds passed it byte-identically; pair it with instructions per frame |
| FID-017 | AI redraws of art the game layers or swaps (lighting states, hover crops of one picture laid over another): keep one master, derive the others with the originals' own gain map, and take the second redraw only where the originals differ | OBSERVED (host, in game) | yes (seams) | Flash menus: crops of a separately redrawn picture showed as hard-edged boxes; blended by the original-difference weight they vanished. Same sides in every state, or the edges change when the lights do |
