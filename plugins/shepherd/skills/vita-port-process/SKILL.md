---
name: vita-port-process
description: A test-first process for porting a game to the PS Vita with Claude -- fidelity first, every change switchable back, work planned in numbered "kits" built as parallel tracks, reviewed and integrated, then run on the device by a person with exact steps, with logs and lessons recorded. Use when planning a Vita port, organising multi-agent build work, writing device test instructions, or deciding whether a change may ship by default.
---

# The kit process (how the Shepherd port is run)

## Principles
- **Fidelity first.** The port must look and play exactly like the original. A change that alters output ships only behind an opt-in.
  Every change has a switch back to the previous behaviour (an env-file line), so a regression is one line away from undone.
- **Identity checks.** Every build is compared frame by frame (render-command hashes per frame, an audio stream hash) against the previous
  version on scripted routes (idle menu, New Game, sub-menus, settings toggles). Differences must be explained or they block.
- **Measure, then believe** (`vita-measure`). Estimates are labelled as estimates.
- **The device is the judge; the harness must agree with it** (`vita-check-the-checker`).

## A kit
1. **Plan**: a numbered kit with a theme (e.g. runtime + memory). A shared brief lists the rules, inputs, identity references and pending
   decisions; each track owns named rows and named files so tracks don't collide.
2. **Build tracks in parallel** (separate branches / worktrees), MUST rows first, STRETCH only if they fit. Not-done rows are reported
   honestly.
3. **Review** each track (read-only, concrete defects with file / line / failure scenario), then **verify** each finding adversarially
   before fixing; fix with switch-safe changes and re-run the gates.
4. **Integrate**: merge tracks one at a time, build after each, re-check identity and memory (eboot size -> free memory), review the
   merged diff through several lenses (merges, fidelity, device safety, memory), fix, then build the kit from one clean clone.
5. **Device run by a person**: a plain-words README with exact steps (what to press, how long, what to send back), one menu move per start
   if the app ends green only after a menu response, optional extras clearly marked, env files named per step. Copy-by-hand instructions
   list files, never folders.
6. **Read the logs**, update the version history, and record: what worked, what failed and why (hiccups included), newly proven facts
   (into the playbook / this plugin), and the next kit's rows.

## Budget and pacing
- Big parallel builds are expensive; small fixes are done directly. Pause cleanly when a budget ends: commit WIP with a note of where it
  stopped, and resume from the branches.
- One device-proven lesson saves more than ten untested ideas: prefer kits that end in a device run.
