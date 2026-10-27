# Idea catalog: GPU and rendering (GPU)

The Vita's SGX543MP4+ is a tile-based deferred renderer with hidden-surface removal for opaque pixels; vitaGL sits on GXM. Exact = 0
differing pixels on a pixel A/B against the reference path (plus a device debug compare where a cache is involved).

| ID | Idea | Status | Exact | Source / notes |
|---|---|---|---|---|
| GPU-001 | Keep a post-processing LUT while its settings are unchanged | THEORETICAL | yes | |
| GPU-002 | Static pre-batching + GPU projection + retained VBOs | THEORETICAL | yes | |
| GPU-003 | Vertex data in the smallest format the GPU converts for free (16-bit pos / UV, 8-bit colour) where it round-trips exactly | THEORETICAL | yes | checked per mesh at build time |
| GPU-004 | Skip drawing the world when an opaque full-screen UI or a black transition covers it | THEORETICAL | yes | |
| GPU-005 | Tight sprite meshes; opaque-core + blended-rim split so HSR removes hidden pixels | THEORETICAL | yes | core keeps only texels with alpha exactly 1 at every used mip |
| GPU-006 | No discard / alpha-test where blending gives the same pixels (keeps HSR on) | THEORETICAL | yes | |
| GPU-007 | Lower-precision shader maths only where the output is identical | THEORETICAL | yes | |
| GPU-008 | Honour the game's own mipmap settings | THEORETICAL | yes | fidelity + bandwidth |
| GPU-009 | Draw-prefix cache: reuse the image after the first N bit-identical draws | THEORETICAL | yes | hits mostly in still moments; never 2D-shift a perspective image |
| GPU-010 | Dirty rectangles: redraw only changed draws' old + new bounds | THEORETICAL | yes | |
| GPU-011 | Learning per-tile prefix cache (32x32 tiles resume from their own save point) | THEORETICAL (research) | yes | only if the heat map shows it pays; MSAA multiplies its memory |
| GPU-012 | Frame-change heat map (debug): % of tiles unchanged per scene | THEORETICAL | -- | measures the ceiling of GPU-009..011 |
| GPU-013 | "Green hole" debug fill for reuse proofs | THEORETICAL | -- | Final Fantasy VII field tiles |
| GPU-014 | Tile-based MSAA honouring the game's anti-aliasing setting | THEORETICAL | close | cheap on a tile GPU; A/B the picture and VRAM / parameter-buffer cost |
| GPU-015 | Optional dynamic resolution (world only, UI native, floor 75 %) | THEORETICAL (opt-in) | no | helps GPU-bound scenes only |
| GPU-016 | Fewer full-screen grab copies (tile-friendly rules) | THEORETICAL | yes | ~16 grabs per frame seen in one scene |
| GPU-017 | Read the pixel underneath (framebuffer fetch) instead of Grab for blend modes | THEORETICAL (probe first) | yes, per case | only where nothing was drawn under it since the grab |
| GPU-018 | Static light cache (a runtime lightmap for lights that never change on geometry that never moves) | THEORETICAL | yes | |
| GPU-019 | Sprite sheets packed at build time with safe padding (exact sampling) | THEORETICAL | yes | fewer texture switches |
| GPU-020 | Run the original's own shadow algorithm live on the GPU (same map resolution, cascade fit, filter) | THEORETICAL | yes | pre-baked shadows can't match a moving sun |
| GPU-021 | Cached static-caster shadow depth; draw only moving casters | THEORETICAL | yes | Sega's Vita Smash 4, DOOM (2016) |
| GPU-022 | GPU / CPU balancer: dual-path work on whichever side has room (bit-identical paths only switch per frame) | THEORETICAL | yes | |
| GPU-023 | Shader constants uploaded only when they change; bone palettes in the uniform layout | THEORETICAL | yes | GTA: San Andreas Vita port; no CPU pre-multiplied MVP (rounding) |
| GPU-024 | Permanent uniform slots for still objects | THEORETICAL | yes | Unity's SRP Batcher |
| GPU-025 | World renderer change signature: reuse a draw record when nothing changed | THEORETICAL | yes | Sonic's dynamic pattern load cues |
| GPU-026 | GXM precomputed draws for stable retained draws | THEORETICAL | yes | vitaGL / GXM |
| GPU-027 | Every shader variant created during loading (recorded in play) | THEORETICAL | yes | vitaGL's cache, GTA: SA warm-up lists, Unleashed Recompiled |
| GPU-028 | Every dynamic upload through frame-sliced circular pools in write-combined memory | THEORETICAL | yes | Rinnegatamante's Swordigo port |
| GPU-029 | Pixel-contribution census (offline) to find new exact occlusion rules | THEORETICAL | -- | Ori and the Will of the Wisps |
| GPU-030 | Don't store depth / stencil to memory when nothing reads it | THEORETICAL | yes | tile-GPU "memoryless" practice |
| GPU-031 | Instanced sprite quads (one record per sprite, GPU builds corners) | THEORETICAL | yes, if 0 pixels differ | Godot 4 2D renderer |
| GPU-032 | Order-safe batch merging (look-ahead, no overlap with skipped items) | THEORETICAL | yes | Godot 3.2.2 |
| GPU-033 | Depth copy placed where nothing breaks the tile pass; never a depth prepass on tile GPUs | THEORETICAL | yes | URP 14 docs |
| GPU-034 | Merge render passes that share a target into one GXM scene; last pass straight to the display | THEORETICAL | yes | URP Native RenderPass, Unity 6 Render Graph |
| GPU-035 | No partial renders: count them on the device, size the parameter buffer so heavy scenes never overflow | THEORETICAL | yes | a mid-frame tile flush is very expensive |
| GPU-036 | Textures placed by draw frequency (hot in CDRAM, cold in main RAM) | THEORETICAL | yes | shares a budget with MEM-024 |
| GPU-037 | Drop mip levels never sampled at the device's resolution (proven by a mip-usage test shader) | THEORETICAL | yes | never shrink textures without mips |
| GPU-038 | GPU transfer unit for texture moves / swizzles | VERIFIED | yes | VH-009 |
| GPU-039 | GPU-generated mips | FAILED | no | FA-003 |
| GPU-040 | GPU skinning of skeletal meshes | FAILED (as default) | no | rounds differently: opt-in only |
| GPU-041 | Fallback ladder for heavy scenes: balancer -> (opt-in) dynamic resolution -> 60 fps visual mode per area -> steady locked 30 | THEORETICAL | -- | never stutter or slow motion |
| GPU-042 | Study other platforms' official versions (settings, textures, shaders) for safe cuts | THEORETICAL (research) | depends | only from copies you legally own |
| GPU-043 | Overdraw heat map before optimising layered 2.5D scenes; every layered asset gets GPU-005, worst first | THEORETICAL | -- | layers stay separate quads at their own depths (DROP-018) |
| GPU-044 | Opt-in "Optimized" shadows: each static caster's outline skewed onto the ground by the exact current sun angle in the vertex shader, all into one shadow mask | THEORETICAL (opt-in) | no | ~4 vertices per caster, nothing baked; differences (edge softness, upright receivers) measured and shown before choosing |
| GPU-045 | Opt-in sun-step shadow updates: static casters' map redrawn only when the sun turned past a threshold | THEORETICAL (opt-in) | threshold 0 = yes | shadows trail the sun by at most the step |
| GPU-046 | Opt-in shadows baked along the sun's path per layout, built on spare cores into the learning cache | THEORETICAL (opt-in) | no | snapshot spacing and camera fit differ; moving casters always live |
