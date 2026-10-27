# Failed or rejected (FA)

Failures are kept on purpose: they stop the next port from repeating them. Check here before proposing a technique.

### FA-001 -- Pre-baked animation poses as an exact replacement
- Status: FAILED (as a default). Category: animation.
- Why: baked poses differed from the live evaluation in about 40 % of tested clips (up to tens of pixels): merged / wrong skins at bake
  time, interpolation across stepped keys, flip timing. GPU skinning also rounds differently.
- Instead: a native evaluator that is bit-identical, exact skipping of unchanged poses, and sharing poses only when inputs are byte-identical.

### FA-002 -- Big memory pages
- Status: FAILED (no measurable gain). Category: memory.

### FA-003 -- GPU-generated mipmaps
- Status: FAILED (not exact). Category: GPU.
- Why: the GPU's downscale differs by +-1 in some channels from the stored mips. Keep stored mips.

### FA-004 -- Asking scePower for 500 MHz from an app
- Status: FAILED. Category: CPU.
- Why: refused (`0x802b0000`). Only a plugin profile (PSVshellPlus) reaches ~500, and plugins expose no user API an app can call.

### FA-005 -- Detecting the model from CDialog + imc0
- Status: FAILED. Category: platform. See VH-011.

### FA-006 -- Judging a JIT on the idle menu
- Status: OBSERVED (method lesson). Category: testing / runtime.
- Why: JIT on vs off changed total idle frame time (48.1 -> 45.0 ms) but game-logic time didn't move (23.5 vs 23.8 ms); the difference was
  in render -- run variance, not the JIT. Measure the code the change affects.

### FA-007 -- Trusting a harness that doesn't model the platform
- Status: FAILED (process). Category: testing.
- Why: builds passed an emulator that didn't model module import binding, decoder output delay or the suspended process clock; the device
  failed all three. See the `vita-check-the-checker` skill.

### FA-008 -- Forcing 444 MHz at launch
- Status: FAILED. Category: CPU. Overrode a plugin's higher clock (GT-011).
