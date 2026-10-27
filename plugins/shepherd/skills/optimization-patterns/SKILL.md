---
name: optimization-patterns
description: General software optimization patterns (not Vita-specific) for loading, memory, CPU, rendering, build-time and runtime work -- each with when it helps, when it hurts, and how to measure it -- plus the rule that a pattern proven elsewhere must be re-measured on the target. Use when profiling a slow load or frame on any constrained device, when choosing between optimisations, or when a hot path looks like a known anti-pattern (repeated strlen, linear duplicate checks, per-frame re-parsing).
---

# General optimization patterns

This library is platform-neutral on purpose. Vita-specific facts and the Vita idea catalog live in the `vita-knowledge` skill; the
patterns here point to them where they've been applied on a Vita.

The full list with when-useful / when-harmful / how-to-measure for each pattern is in
`${CLAUDE_PLUGIN_ROOT}/skills/optimization-patterns/patterns.md`. Read the category you need instead of the whole file.

## Rules
1. **Profile first.** Name the bottleneck with a measurement before choosing a pattern. A pattern applied to code that isn't hot is only
   risk.
2. **Proven elsewhere is not proven here.** A technique that worked on a PC, another console or in a paper is a candidate on the target
   until it is measured there (A/B on the device, same scene, same frame range).
3. **Correctness before speed.** If the project has a fidelity rule (same output as the original), a pattern is only allowed where the
   output is provably identical; anything else is an opt-in setting.
4. **Measure what the change affects.** A whole-frame number can hide or invent a win (see FA-006 in `vita-knowledge`).
5. **Write down failures.** A pattern that didn't help on the target goes into the knowledge base as FAILED with the reason.

## The classic example
In 2021 a developer known as t0st profiled GTA Online's ~6 minute load and found two problems in parsing one ~10 MB JSON file of store
items: `sscanf` called `strlen` on the whole remaining buffer for every token (quadratic), and every item was checked for duplicates by a
linear scan of all items already stored (quadratic again). Fixing those two cut the load by about 70 %. Patterns OP-001, OP-002 and
OP-004 below are that story generalised.
