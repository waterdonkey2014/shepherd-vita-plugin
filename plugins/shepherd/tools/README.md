# Shepherd tools for PS Vita ports

Small, portable tools that catch device failures before a device run and keep device numbers honest. Python 3.8+ (standard library
only) and POSIX sh; the C header needs vitasdk. All are MIT, like the rest of the plugin. Tests: `python3 tests/test_tools.py` from the
repository root (every check has a negative control; the C parts run when `cc` / vitasdk are installed).

| Tool | What it does | Catches |
|---|---|---|
| `vita-imports.py` | Lists an ELF's imported libraries / functions; checks a module-load list, allow-lists and forbidden presets | `0x8002D003` module loads (GT-001), newlib's hidden SceNet (GT-014), stray network / kernel / JIT / hook imports |
| `vita-vpk-check.py` | Reads a VPK's param.sfo and file list; checks required files, TITLE_ID, ATTRIBUTE2, forbidden file types, size | a wrong title id, a missing extended-memory flag (VH-003), game data packed by mistake, macOS `._` files (GT-012) |
| `vita-runlog.py` | Stats from a device log's `SM` lines, and a run-by-run history with honest comparisons | a wrong clock (GT-011), stale logs, crashes with no END line, percentages across different clocks |
| `vita-pull-logs.sh` | Copies an app's logs and recent crash dumps off a VitaShell-mounted memory card, read-only | logs overwritten by the next start, forgotten crash dumps |
| `c/shepherd_measure.h` | One-header C instrumentation that writes the `SM` lines | unmeasured clocks, missing memory checkpoints, suspend gaps (GT-004) |

## vita-imports.py
Reads the linker's ELF (the input of `vita-elf-create`), not `eboot.bin`.
```
python3 vita-imports.py build/app.elf                                  # libraries and counts (--funcs: every function)
python3 vita-imports.py build/engine.elf --module-load-libs loaded.txt # a module loaded by a launcher (GT-001)
python3 vita-imports.py build/app.elf --forbid network --allow-newlib-net --forbid kernel --forbid hooks
```
`module-load-libs.example.txt` is one device's observed list with its caveats -- start from it, then adjust for what your launcher has
loaded. Presets: `network` (SceNet*, SceHttp, SceSsl, SceNp*), `kernel` (*ForDriver / *ForKernel), `jit` (ForVM / VM-domain
functions), `hooks` (taihen, kubridge). `--allow-func NAME` exempts one function. Exit 0 ok, 1 a check failed, 2 unreadable.
Wire it into your build so a bad import fails the build, not the device run.

## vita-vpk-check.py
```
python3 vita-vpk-check.py out/app.vpk --expect-title-id ABCD00001 --expect-attribute2 12 --forbid-ext .assets --forbid-ext .bank
python3 vita-vpk-check.py --sfo out/param.sfo
```

## vita-runlog.py
```
python3 vita-runlog.py stats measure.txt [--frames 600:1800] [--built out/app.vpk]
python3 vita-runlog.py add logs/*.txt --history perf-history.tsv --label v0.3
python3 vita-runlog.py show --history perf-history.tsv --app myport
python3 vita-runlog.py compare --history perf-history.tsv --app myport            # last two runs, or --a LABEL --b LABEL
```
The `SM` line format is in the header of `vita-runlog.py` and in the `vita-measure` skill. Logs in another format: write a small
`--spec` JSON that maps your lines (regex with named groups) to the same events -- the tests show an example.
Rules it enforces: the measured clock wins over the reported one; no percentage across two clocks or for a run whose clock changed
(it points to the closest earlier run at the same clock); a log older than `--built` is STALE; the same log is never added twice.

## vita-pull-logs.sh
On the Vita: VitaShell -> START -> USB. Then:
```
sh vita-pull-logs.sh --data-dir data/myport [--dest DIR] [--wait 10] [--stats]
```
It only reads the card (never writes, deletes or ejects; it refuses a destination on the card), copies text logs with their
sub-folders, crash dumps from the last 3 days, and writes `card-manifest.txt`. A game card mounted through VitaShell is refused.

## c/shepherd_measure.h
```c
#define SHEPHERD_MEASURE_IMPLEMENTATION      /* in one .c file */
#include "shepherd_measure.h"
sm_init("myport", "v0.3", "ux0:data/myport/measure.txt");
sm_log_clock("start"); sm_log_mem("start", -1); sm_log_boot("first_picture");
/* per frame */ sm_frame_begin(); /* ... */ sm_frame_end(render_us, gc_us, 0); sm_suspend_check();
sm_log_frames("menu-idle"); sm_log_clock("end"); sm_end(1, "done");
```
Link with `-lSceRtc_stub -lScePower_stub`. Try it with the example:
```
arm-vita-eabi-gcc -O2 -Wl,-q c/measure_example.c -o measure_example.elf -lSceRtc_stub -lScePower_stub
vita-elf-create measure_example.elf measure_example.velf
vita-make-fself -s measure_example.velf eboot.bin
vita-mksfoex -s TITLE_ID=SMEX00001 -d ATTRIBUTE2=12 "SM example" param.sfo
vita-pack-vpk -s param.sfo -b eboot.bin -a icon0.png=sce_sys/icon0.png sm_example.vpk   # icon0.png: any 128x128 PNG
```
Install the VPK, run it once, pull `ux0:data/sm_example/` with `vita-pull-logs.sh --data-dir data/sm_example --stats`.
Status: the header is built and tested on the host and with vitasdk; its clock-measuring loop is the method verified on a PCH-2000
(VH-001), but the header as a whole is EXPERIMENTAL until someone reports a device run.
