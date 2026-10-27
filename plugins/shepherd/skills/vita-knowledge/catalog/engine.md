# Idea catalog: engine layer (ENG) -- a Unity stand-in's own work

Shepherd replaces Unity's engine under the game's unmodified code. These ideas make the engine answer the game's calls faster with the
same answers in the same order (exact), checked frame by frame.

| ID | Idea | Status | Exact | Source / notes |
|---|---|---|---|---|
| ENG-001 | Tag index: FindWithTag / FindGameObjectsWithTag from a per-tag set in walk order | VERIFIED (green device runs) | yes | a profiler found tag walks at ~31 % of a scene frame |
| ENG-002 | Find indexes by type / name (FindObjectsOfType, GameObject.Find) in scan order | EXPERIMENTAL | yes | |
| ENG-003 | Stable insertion sorts in kept buffers instead of LINQ re-sorts | VERIFIED | yes | |
| ENG-004 | Skip Update / LateUpdate / FixedUpdate whose IL is only `ret` | VERIFIED | yes | read at the type's first use |
| ENG-005 | Frame-number stamps instead of cleared per-frame flags | EXPERIMENTAL | yes | Quake's visframe |
| ENG-006 | Lookup memos: GetComponent, Resources.Load, Shader.PropertyToID, StringToHash, CompareTag per call site | EXPERIMENTAL | yes | BlitWorks' Bastion port; cleared on AddComponent / Destroy / scene change |
| ENG-007 | Record recycling: a destroyed object's engine records reused by the next one | EXPERIMENTAL | yes | the game's Awake / OnDestroy still run |
| ENG-008 | Coroutine timer wheel (WaitForSeconds sleepers in a heap; Unity's resume order) | EXPERIMENTAL | yes | |
| ENG-009 | Invoke / InvokeRepeating in the same timer wheel, in Unity's order | EXPERIMENTAL | yes | RimWorld's rare / long ticks |
| ENG-010 | Engine housekeeping on a 16-slot phase cycle (never game logic) | EXPERIMENTAL | yes | SimCity's phase cycle, RollerCoaster Tycoon's tick128 |
| ENG-011 | Temporal-coherence draw sorting (repair last frame's order; ties exactly Unity's) | EXPERIMENTAL | yes | |
| ENG-012 | Pack-time string IDs (tags, layers, animator parameters, translation keys pre-hashed) | THEORETICAL | yes | |
| ENG-013 | Shortest-slice hashing for fixed engine tables | THEORETICAL | yes | .NET 8 FrozenDictionary key analysis |
| ENG-014 | Swiss-style hash tables for the engine's own maps (never the game's Dictionary) | THEORETICAL | yes | the game's iteration order is game-visible |
| ENG-015 | Late input latch: one input state per frame, read at the first input query | VERIFIED | yes | |
| ENG-016 | Exact visibility signals (isVisible, OnBecameVisible / Invisible) | EXPERIMENTAL (opt-in) | depends | the game reacts to visibility: needs an editor check before default |
| ENG-017 | Lazy menu watch (selection read only at a press) | EXPERIMENTAL | yes | conflicts with a late input latch -- keep per-frame there |
| ENG-018 | Fast object creation (E3 field programs) for Instantiate and scene loads | THEORETICAL | yes | the biggest boot / load item in the plan |
| ENG-019 | Warm switch-back: keep an area's engine records ready while it is switched off (SetActive false) | THEORETICAL | yes | the game's own OnEnable still runs |
| ENG-020 | Event-driven structure / needs updates via timer wheels with ordered commit | THEORETICAL | yes | |
| ENG-021 | No-op message elision / spin elision | THEORETICAL | yes | |
| ENG-022 | Engine-side asset-group prediction: prepare the next scene's data when the context makes it likely (data only) | THEORETICAL | yes | the game's own load call still runs in order |
