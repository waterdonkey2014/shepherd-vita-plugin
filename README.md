# Shepherd for PS Vita -- a Claude plugin

PS Vita game-porting knowledge for Claude, from the **Shepherd** project (a from-scratch Unity stand-in engine that runs a modern Unity
game's own compiled C# on a Mono runtime ported to the Vita). Weeks of device runs, condensed so your Claude doesn't have to relearn them.

**Version 0.2 -- knowledge + the idea catalog.** The Shepherd engine itself follows as an early open-source release, so people porting other games can fill its gaps and send findings back.

## What's inside
| Skill | Use it for |
|---|---|
| `vita-hardware` | Measured clocks, memory budgets, latency, card speed, JIT memory rules, GPU transfer unit, NGS, real model / firmware |
| `vita-gotchas` | The checklist of failures that each cost a device run (0x8002D003 module loads, decoder delay, vitaGL memory, suspend clock, ...) |
| `vita-measure` | What to log in every device run and how to compare runs honestly |
| `vita-check-the-checker` | Making off-device tests catch what the device catches |
| `vita-port-process` | The kit process: fidelity first, parallel tracks, review, integration, device runs |
| `vita-knowledge` | The numbered knowledge base (VERIFIED / OBSERVED / EXPERIMENTAL / FAILED entries with evidence) and the idea catalog: ~340 techniques in 12 categories, each labelled with its status and whether it keeps output exact |
| `optimization-patterns` | Platform-neutral patterns (loading, memory, CPU, rendering, build-time, runtime): when each helps, when it hurts, how to measure it |
| `vita-record-discovery` | Writing up your own finding (success or failure) in the knowledge-base format, ready to contribute |

Claude loads a skill only when a task needs it, so the plugin stays light.

## Install
In Claude Code:
```
/plugin marketplace add <owner>/<repo>
/plugin install shepherd@shepherd-vita
```
(`<owner>/<repo>` = this repository once it is published.)

## Updates
New versions are published here as the port and the community learn more. Update with:
```
claude plugin update shepherd@shepherd-vita
```
or turn on auto-update for the `shepherd-vita` marketplace in the `/plugin` menu.

## Status labels
VERIFIED (measured on a Vita) · OBSERVED · EXPERIMENTAL (passes off-device tests, not yet on a device) · FAILED (kept on purpose) ·
THEORETICAL (planned, not built -- most of the catalog) · PARKED. Hardware facts so far come from one PCH-2000 (fw 3.65 + Enso, plugins) -- runs on
other models and firmwares are the most welcome contribution.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Failed experiments are as welcome as successes.

## Roadmap
- v0.1: knowledge skills
- v0.2: the idea catalog + general optimisation patterns (this release)
- v0.3: portable tools (module-import check, run-history script, log helpers, later the off-device Vita harness)
- Engine: an early public release of Shepherd (MIT), not waiting for polish -- gaps get filled by people porting their own games

## Licence
MIT -- see [LICENSE](LICENSE).
