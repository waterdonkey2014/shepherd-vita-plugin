---
name: vita-check-the-checker
description: The habit of making off-device tests (emulators, host builds, harnesses, history scripts) catch the failures the real PS Vita shows -- reproduce every device failure off-device before fixing it, add negative controls, and audit the tools that produce your numbers. Use when a device run fails although local tests passed, when building or changing a test harness, or when numbers from a tool look surprising.
---

# Check the checker

A port is tested mostly off-device (an emulator, a host build, scripted routes) because device runs are slow and need a person. That only
works if the off-device tests fail where the device fails. In one kit, three of four device failures were things the emulator simply did
not model:

| Device failure | What the harness did instead | Fix to the harness |
|---|---|---|
| Module refused with `0x8002D003` (GT-001) | Linked everything into one image; import binding not modelled | Refuse a module whose imports aren't on the loaded-libraries list |
| No first picture from the video decoder (GT-002) | A stand-in decoder returned a picture immediately | Delay the stand-in's first picture by N access units |
| Suspend never detected (GT-004) | Process time kept running | Model a suspension: stop process time, keep the RTC running |

## The rule
1. **When the device fails, make the harness fail the same way first** (same error code, same log line). Only then fix the code.
2. **Keep a negative control**: the old, broken build must now FAIL under the improved harness, and the fixed build must pass. If the old
   build passes, the harness still can't see the bug.
3. **Audit the tools that produce numbers.** A stats script once counted stale logs from an older build, missed a whole set of runs, and
   measured the wrong frame window for some apps -- the "results" looked plausible. Check: which files did it read, which window, which
   clock, does it count every run exactly once.
4. **Turn each lesson into a build-time check where possible** (e.g. a module-import allow-list that fails the build), so it can't
   regress silently.
5. **Write down what the harness cannot model** (relocations, real GPU timing, thermal) so nobody reads a pass as proof of those.

## Break the checker on purpose
When a new test suite passes on its first run, make sure it can fail: copy the code, plant one bug per check (a check that always
passes, an off-by-one in a percentile, a skipped filter), run the tests, and expect each planted bug to fail at least one test. The
plugin's own tools were checked this way (12 planted bugs, 12 caught); `tests/test_tools.py` in the plugin repository shows the
fixtures (a synthetic ELF, param.sfo, VPKs, logs, a fake memory card that must be byte-identical afterwards).

