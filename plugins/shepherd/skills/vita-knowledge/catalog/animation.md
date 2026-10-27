# Idea catalog: skeletal animation (ANIM)

Modern 2D games animate dozens of skeletons (Spine, Unity's animator) per frame, and on the Vita that is a CPU cost before it is a GPU
one. Read FA-001 first: baked poses and GPU skinning were NOT exact as defaults. The safe routes are doing the same maths elsewhere
(spare cores, native code), skipping work that provably can't change the result, and sharing results whose inputs are byte-identical.

| ID | Idea | Status | Exact | Source / notes |
|---|---|---|---|---|
| ANIM-001 | Skeleton updates (apply + world transforms) for independent skeletons on spare cores | THEORETICAL | yes | spine-unity's threaded animation, Wulverblade's mesh workers; events recorded and fired on the main thread at that skeleton's own Update slot, in the original order |
| ANIM-002 | Recompute on the main thread any skeleton that game code touched before its spare-core result is used | THEORETICAL | yes | the safety rule for ANIM-001 |
| ANIM-003 | Speculative mesh build (attachments, draw order, packed vertices) on spare cores, committed only if version stamps show nothing touched the skeleton | THEORETICAL | yes | always wait, never skip a frame |
| ANIM-004 | Split spare-core skeleton jobs into >= 8 chunks per core | THEORETICAL | yes | load balance across uneven skeletons |
| ANIM-005 | Skip unchanged poses: every active track in a stretch of constant timelines, no mix in progress, no constraint / bone override changed -> reuse last frame's pose and vertex buffer | THEORETICAL | yes | spine-unity 4.3 static-pose optimizer; animation time still advances and events still fire on the same frame |
| ANIM-006 | Pose sharing: characters whose whole animation state (tracks, times, mix weights) is byte-identical share one bone palette | THEORETICAL | yes, by definition | a pose belongs to skeleton + clip + time, not to a character; outfits / skins are attachments only |
| ANIM-007 | A native skeleton evaluator that is bit-identical to the managed runtime | THEORETICAL | yes | the exact replacement for a pose bake (FA-001) |
| ANIM-008 | Batched bone-to-transform copies (utility bones) in one native loop with the same maths | THEORETICAL | yes | bones of skeletons the game stopped updating stop with them |
| ANIM-009 | Reproduce the original's own animation LOD exactly (distance bands, rates adapted to measured fps, staggered updates) | THEORETICAL | yes | it is the original's behaviour; staggering by instance id needs ids that follow the engine's own pattern |
| ANIM-010 | Honour quality flags the original sets (e.g. lowest-quality skeletons for summoned minions) in the "Original" setting | THEORETICAL | yes | don't silently upgrade or downgrade |
| ANIM-011 | An "Animations: Original / Full" option: Full animates every on-screen skeleton at full rate | THEORETICAL (option) | no (beyond the original) | which one is the default is the project's decision; Shepherd chose Full |
| ANIM-012 | Skip animating and drawing off-screen characters while their logic and physics stay live | THEORETICAL | only if nothing reads the pose | events must still fire; check whether game code reads bone positions |
| ANIM-013 | Characters sharing an atlas drawn together (one draw per atlas) | THEORETICAL | yes with CPU skinning | GPU-skinned batching rounds differently (GPU-040): opt-in only |
| ANIM-014 | Foliage / grass sway in a vertex shader using the game's own sway maths | THEORETICAL | yes, if 0 pixels differ | never per blade on the CPU |
| ANIM-015 | Shared skeleton data and lazy skins for many copies of one character | THEORETICAL | yes | MEM-032; mass spawns of temporary copies |
| ANIM-016 | Pre-baked poses as the default path | FAILED (as default) | no | FA-001 |
