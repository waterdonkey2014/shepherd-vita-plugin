# Idea catalog: menus, UI and text (UI)

Menus in a modern Unity game are expensive on the Vita mostly because of CPU-side mesh and text building. The patterns below keep the
game's own menu code running exactly as written while the engine's work for it gets cheaper. Exact = 0 differing pixels on a pixel A/B.

| ID | Idea | Status | Exact | Source / notes |
|---|---|---|---|---|
| UI-001 | Pre-baked UI / TextMeshPro meshes for fixed screens (credits, settings pages) | THEORETICAL | yes | |
| UI-002 | Canvas batching + layer caching for static screens | THEORETICAL | yes | |
| UI-003 | Animated UI without rebuilds: keep blocks in local space, apply matrix + tint on the GPU | THEORETICAL | yes, if 0 pixels differ | tween timing stays live (real-time) |
| UI-004 | Opaque-panel occlusion: skip world draws fully inside an opaque panel's inner rectangle | THEORETICAL | yes | off (or with a margin) while blur-type post effects run |
| UI-005 | Dialogue text pre-bake (fixed lines' glyph layout baked; names / numbers live) | THEORETICAL | yes | |
| UI-006 | Typewriter reveal from one baked layout | THEORETICAL | yes | per-letter effects in a vertex shader |
| UI-007 | Health / progress bars as width + tint on the GPU (never pre-stepped) | THEORETICAL | yes | a stepped bar would sit a pixel off |
| UI-008 | Icon sheets for every menu, incl. locked silhouettes, resident in VRAM | THEORETICAL | yes | unlocking / scrolling never loads an image |
| UI-009 | Menus one press away: their prepared data resident, textures in free VRAM (data only) | THEORETICAL | yes | a settings menu took ~8-10 s before the menu work |
| UI-010 | Visible-first menu build: engine work for what's on screen first, the rest in spare time | THEORETICAL | yes | the game's own code runs in the original order |
| UI-011 | Recorded command lists for fixed screens, replayed until something changes | THEORETICAL | yes | |
| UI-012 | Whole-pixel UI scroll shift (copy the cached list by the offset, draw the exposed strip) | THEORETICAL | yes | Commander Keen's adaptive tile refresh; never for a perspective world camera |
| UI-013 | Patch only changed colour bytes of a retained block | THEORETICAL | yes | colour cycling |
| UI-014 | Incremental UI re-batching (rebuild only the dirty batch runs) | THEORETICAL | yes | Unity uGUI guidance |
| UI-015 | Frozen world behind a time-scale-0 menu drawn once and reused (or skipped when fully covered) | THEORETICAL | yes | |
| UI-016 | Heavy post effects (depth of field, blur) implemented exactly as Unity's passes, tile-friendly | THEORETICAL | yes | never silently changed |
| UI-017 | Text mesh cache: each exact string's mesh made once (count-up numbers, names) | THEORETICAL | yes | |
| UI-018 | UI particles simulated and meshed off the main thread | THEORETICAL | yes | a looping video would repeat where the original never does -- rejected |
| UI-019 | A platform settings tab cloned from the game's own tab look; descriptions only on added rows | THEORETICAL | -- | added rows never mixed between original rows |
| UI-020 | Closer camera for small screens, done in the projection only (game camera code untouched) | THEORETICAL (opt-in) | no | screen markers follow automatically |
| UI-021 | Hide cutscene letterbox bars (only the bar images; the game still sees a cutscene) | THEORETICAL (opt-in) | no | |
| UI-022 | Accessibility / options parity with the original, checked against the PC version | THEORETICAL | yes | |
| UI-023 | Extra languages only when their glyph atlases fit (CJK measured first) | THEORETICAL | yes | |
| UI-024 | Picture-first menus (replay a recording while the real menu builds) | PARKED | -- | saves little once menus open in ~0.1-0.3 s |
| UI-025 | Hide buttons that can only open things outside the game on a handheld (web links, store ads), as console builds do | VERIFIED | console-original | |
