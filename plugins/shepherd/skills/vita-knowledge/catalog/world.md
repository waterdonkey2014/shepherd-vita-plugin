# Idea catalog: scenes, streaming, prediction and pathing (WORLD)

How to make a big or procedurally generated world feel instant from a ~10 MiB/s card and a small heap without changing what the game
decides. **The rule above every row: never call the game's random functions early, and never guess a choice the player or the dice make.**
Prepare every candidate (within a memory budget), let the game pick, drop the rest. The game's own load calls still run at the same
moment and simply finish sooner, as on a fast PC.

| ID | Idea | Status | Exact | Source / notes |
|---|---|---|---|---|
| WORLD-001 | Retained static scenery: buildings, decorations and ground built once into GPU geometry merged per area chunk, rebuilt only for the chunk that changed | THEORETICAL | yes | animated parts stay live; chunk size tuned on the device (smaller = better culling, more draws) |
| WORLD-002 | Rarely-changing clutter and growth stages live in the retained chunks; each touched chunk rebuilt ONCE per frame even when many pieces are placed | THEORETICAL | yes | |
| WORLD-003 | Generation-time baking: right after the game's generator places a procedural room, its static scenery is built as retained geometry on spare cores | THEORETICAL | yes | the generator stays live and random; freed when the floor is left |
| WORLD-004 | Pathfinding scan memo: a deterministic graph scan stored with an exact fingerprint of every input it reads; reused on a match | THEORETICAL | yes | area switches that rescan the whole graph in one frame |
| WORLD-005 | Exact local pathfinding graph update when one obstacle moves (validated equal to a full scan) | THEORETICAL | yes | |
| WORLD-006 | Memoised recurring paths, dropped when the layout changes | THEORETICAL | yes | |
| WORLD-007 | Tiered preparation by likelihood under a memory budget: tier 0 tiny manifests for every candidate, tier 1 shared data for the top one or two, tier 2 first room + its code compiled for the one being approached | THEORETICAL | yes | ranking from quest state, habits (preload hit statistics) and where the player is heading |
| WORLD-008 | Branching maps: prepare every reachable next node (shared parts first, the highlighted one first once the map is open), never the random pick | THEORETICAL | yes | hidden "?" nodes are real nodes: prepared invisibly, nothing spoiled |
| WORLD-009 | Binary choices on screen (dialogue answers): prepare both branches while the conversation plays, drop the unused one after the answer | THEORETICAL | yes | small: a reply line, a clip, or a fight's enemies |
| WORLD-010 | Content chosen by save counters (the next conversation of an NPC) prepared before entering | THEORETICAL | yes | only where the decomp shows it isn't random |
| WORLD-011 | Mid-fight async loads (enemy waves loaded when a round starts) prepared one room ahead, every candidate of a random pick | THEORETICAL | yes | the load log should show no mid-fight loads |
| WORLD-012 | Forced-path chains (boss floors): prepare room by room, compile the boss's code during conversations (the longest idle windows) | THEORETICAL | yes | retries often skip intros: preparation must finish during the floor |
| WORLD-013 | Free the resources of the place being left while keeping its game state; on a cancel, read them back with the frame waiting | THEORETICAL | yes | never a missing texture; an accepted rare hitch instead of a slower load every time |
| WORLD-014 | Prepare the result of a placement at placement time (a construction site's finished building); hover prepares the ghost | THEORETICAL | yes | data only, dropped if the player picks something else |
| WORLD-015 | Mass spawns of temporary copies (ceremonies): prepared when the prompt shows, fast creation, shared skeleton data, one shared pose | THEORETICAL | yes | the memory spike covered by MEM-028's ladder |
| WORLD-016 | An illustrated map composed once and cached as one image keyed by the discovered set; markers and reveals live on top | THEORETICAL | yes | rebuilt only on a new discovery |
| WORLD-017 | Pre-sized engine pools + a GC in a covered frame right before a load | THEORETICAL | yes | no growth stalls or collections mid-load |
| WORLD-018 | Time-sliced background preparation with a per-frame budget | THEORETICAL | yes | no hitches |
| WORLD-019 | Off-screen-only streaming: nothing visible ever pops in | THEORETICAL | yes | |
| WORLD-020 | VRAM residency across transitions: the home area's textures stay in video memory during a trip while space allows | THEORETICAL | yes | coming home is instant |
| WORLD-021 | Projectile hit checks on a native physics fast path; projectiles of one type drawn together in the original order | THEORETICAL | yes | |
| WORLD-022 | Re-activation of pooled objects kept cheap (engine records kept warm) | THEORETICAL | yes | ENG-007 / ENG-019 |
| WORLD-023 | Particle warm-up state baked only where its random seed is fixed; otherwise live | THEORETICAL | yes | |
| WORLD-024 | Physics extras: sleeping kinematic bodies skipped exactly, a child-aware broadphase, pathfinding grids and composite colliders built at pack time | THEORETICAL | yes | EX-006 for the threaded step |
| WORLD-025 | Code for rarely used systems in overlays loaded with their scene | THEORETICAL | yes | RT-038 |
| WORLD-026 | A cached image of a still background while the camera holds still (static NPC rooms, conversations) | THEORETICAL | yes | GPU-009; switches itself off while the camera moves; rarely helps where the sun or wind changes every frame |
