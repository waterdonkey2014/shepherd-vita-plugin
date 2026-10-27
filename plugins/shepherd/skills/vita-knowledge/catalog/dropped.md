# Idea catalog: dropped or rejected (DROP)

Ideas considered and dropped, with the reason. Most are classic console tricks that change how the game plays or looks -- they are
rejected under a fidelity-first rule, not because they don't run faster. A project with a different rule may choose differently, but
should know what it trades. Tested failures with measurements are in `entries/failed.md` (FA).

| ID | Idea | Why dropped |
|---|---|---|
| DROP-001 | GPU overclock | 222 MHz is already the maximum |
| DROP-002 | Mono `-O` optimisation flags on the LLVM-era runtime | no gain on the device's code |
| DROP-003 | Resizing vitaGL's RAM pools at run time | no idle pool to give back |
| DROP-004 | Caching lifecycle attributes | it runs game code |
| DROP-005 | 30 Hz physics | changes play |
| DROP-006 | Kinematic-first physics / freezing physics of far objects | changes play |
| DROP-007 | Visible particle budgets | changes the picture |
| DROP-008 | Unlocked 21-29 fps | uneven pacing; lock to a steady rate instead |
| DROP-009 | Character flipbooks instead of skeletal animation | changes the picture; see FA-001 for why even baked skeletal poses failed |
| DROP-010 | Entity caps (limits on characters a player can have) | changes play |
| DROP-011 | Fixed-point maths instead of the game's floats | changes results |
| DROP-012 | Updating enemies / AI every other frame | changes play |
| DROP-013 | Frame skipping under load | changes timing; never stutter or slow motion either (GPU-041) |
| DROP-014 | Lower render resolution by default | changes the picture; an opt-in mode only (GPU-015) |
| DROP-015 | Lower audio sample rates | changes the sound |
| DROP-016 | A pre-rendered video of a scene whose content varies (who attends, outfits, levels) | different every time in the original |
| DROP-017 | A looping video in place of live UI particles | repeats where the original never does |
| DROP-018 | Flattening layered 2.5D sprite stacks into one image | breaks the parallax shift between layers as the camera moves |
| DROP-019 | Compressing hot per-frame data | unpacking every frame costs more than it saves; compress only cold data |
| DROP-020 | Pre-rolling or replaying random outcomes (boss attack patterns, drops) | the game's random stream decides them live |
| DROP-021 | Shifting a perspective image in 2D to reuse it | not exact under perspective (UI-012 / GPU-009 limits) |
| DROP-022 | Pre-multiplying the MVP on the CPU | rounds differently from the GPU path (GPU-023) |
