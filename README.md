# Shepherd for PS Vita -- a Claude plugin

PS Vita game-porting knowledge for Claude, from the **Shepherd** project (a from-scratch Unity stand-in engine that runs a modern Unity
game's own compiled C# on a Mono runtime ported to the Vita). Weeks of device runs, condensed so your Claude doesn't have to relearn them.

**Version 0.4 -- knowledge, the idea catalog, portable tools, and the engine.** The Shepherd engine (MIT) is released early alongside it, so people porting other games can fill its gaps and send findings back.

## What's inside
| Skill | Use it for |
|---|---|
| `vita-hardware` | Measured clocks, memory budgets, latency, card speed, JIT memory rules, GPU transfer unit, NGS, real model / firmware |
| `vita-gotchas` | The checklist of failures that each cost a device run (0x8002D003 module loads, decoder delay, vitaGL memory, suspend clock, ...) |
| `vita-measure` | What to log in every device run and how to compare runs honestly |
| `vita-check-the-checker` | Making off-device tests catch what the device catches |
| `vita-port-process` | The kit process: fidelity first, parallel tracks, review, integration, device runs |
| `vita-knowledge` | The numbered knowledge base (VERIFIED / OBSERVED / EXPERIMENTAL / FAILED entries with evidence) and the idea catalog: ~340 techniques in 12 categories, each labelled with its status and whether it keeps output exact |
| `vita-tools` | Running the tools below: after a build (imports, package), after a device run (pull logs, numbers, history), adding measurement |
| `shepherd-engine` | Porting a Unity game with the Shepherd engine: how it works, the order that worked, the hard rules, the first-game seams to fix |
| `optimization-patterns` | Platform-neutral patterns (loading, memory, CPU, rendering, build-time, runtime): when each helps, when it hurts, how to measure it |
| `vita-record-discovery` | Writing up your own finding (success or failure) in the knowledge-base format, and sending it back to Shepherd if you chose that |

Claude loads a skill only when a task needs it, so the plugin stays light.

## Tools (`plugins/shepherd/tools/`)
| Tool | Catches |
|---|---|
| `vita-imports.py` | Module loads the Vita would refuse with 0x8002D003, newlib's hidden SceNet imports, stray network / kernel / JIT / hook imports -- from the linker's ELF, before a device run |
| `vita-vpk-check.py` | Wrong TITLE_ID, missing extended-memory flag, files that must not ship, macOS `._` leftovers |
| `vita-runlog.py` | Device-log stats and a run history that refuses dishonest comparisons (different clocks, stale logs, crashed runs) |
| `vita-pull-logs.sh` | Read-only copy of an app's logs and crash dumps from a VitaShell-mounted memory card |
| `c/shepherd_measure.h` | One-header C instrumentation: measured clock, memory checkpoints, boot milestones, frame summaries, suspend gaps |

Python 3 standard library and POSIX sh -- nothing to install. Tests: `python3 tests/test_tools.py`.

## Install
In Claude Code:
```
/plugin marketplace add <owner>/<repo>
/plugin install shepherd@shepherd-vita
```
(`<owner>/<repo>` = this repository once it is published.)

Progress of the first port, every kit done and planned: the Shepherd engine repository's `docs/ledger/` page
(`https://<owner>.github.io/shepherd/ledger/` once it is public).

## Updates
New versions are published here as the port and the community learn more. Update with:
```
claude plugin update shepherd@shepherd-vita
```
or turn on auto-update for the `shepherd-vita` marketplace in the `/plugin` menu.

## Sending findings back (your choice)
The first time Claude uses the plugin in a project, it asks you once whether new findings from your port -- fixes, failures,
measurements, gotchas -- should go back to the Shepherd project, so the engine and this knowledge base keep improving for everyone.
Choices: *yes, send them*, *yes, but show me each one first*, or *no thanks*. Change your mind any time by telling Claude ("stop
sending findings", "show me each one first"). Whatever you pick, the engine and the plugin work exactly the same: they're free and
open source either way.

- The answer belongs to that project folder. A git worktree counts as its own folder, so branching off into a new worktree (and a new
  chat there) asks once more; a folder that has answered, yes or no, is never asked again.
- Findings are written up in your project's notes whichever you choose. Sending one means a GitHub issue posted under your account
  (public), with logs run through `vita-scrub-log.py` and never game files, private paths, credentials or your private code.
- Nothing is collected automatically; the plugin has no telemetry.
- Each folder's answer is one word (`on`, `review` or `off`) in a small file under the plugin's data folder
  (`~/.claude/plugins/data/shepherd-shepherd-vita/choices/`); nothing is written into your project. A session-start hook runs
  `scripts/sharing.sh note`, which reads the answer and tells Claude; it only prints text.

## Status labels
VERIFIED (measured on a Vita) · OBSERVED · EXPERIMENTAL (passes off-device tests, not yet on a device) · FAILED (kept on purpose) ·
THEORETICAL (planned, not built -- most of the catalog) · PARKED. Hardware facts so far come from one PCH-2000 (fw 3.65 + Enso, plugins) -- runs on
other models and firmwares are the most welcome contribution.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Failed experiments are as welcome as successes.

## Roadmap
- v0.1: knowledge skills
- v0.2: the idea catalog + general optimisation patterns
- v0.3: portable tools
- v0.4: the Shepherd engine's early public release (MIT) + the `shepherd-engine` skill (this release); the off-device harness (vlx) ships inside the engine

## Licence
MIT -- see [LICENSE](LICENSE).
